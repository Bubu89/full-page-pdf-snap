/**
 * provinglab.dev — MCP-Server und Markdown-Aushandlung als Cloudflare Worker.
 *
 * Zwei Aufgaben, ein Worker, weil beide denselben Ursprung brauchen:
 *
 *   POST /mcp                     MCP ueber Streamable HTTP (JSON-RPC 2.0),
 *                                 zustandslos — keine Durable Objects, damit
 *                                 der freie Tarif reicht (100.000 Anfragen/Tag).
 *   Accept: text/markdown         liefert jede HTML-Seite als Markdown aus.
 *                                 Cloudflares eigenes "Markdown for Agents"
 *                                 verlangt Pro; das hier kostet nichts.
 *
 * Sicherheitsnetz: Jeder unerwartete Fehler faellt auf fetch(request) zurueck,
 * also auf die unveraenderte Antwort von GitHub Pages. Ein Defekt in diesem
 * Worker darf die Seite nicht ausknipsen.
 */

// Die Daten liegen immer auf der Publikation — nicht auf der Domain, unter der
// dieser Worker gerade laeuft. Auf einer workers.dev-Adresse zeigte url.origin
// sonst auf den Worker selbst und jede Datenabfrage endete im 404.
const SITE = "https://provinglab.dev";
const VERSION = "1.7.0";
const PROTOCOL = "2025-06-18";
const AGENT = "provinglab-mcp/1.7 (+https://provinglab.dev/; citation metadata reader)";

const TOOLS = [
  {
    name: "list_measurements",
    description:
      "List the measurements published on provinglab.dev with their dataset " +
      "URLs and the pages documenting how each was measured. Start here.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "get_measurement_data",
    description:
      "Fetch one measurement dataset as JSON: measured values, the control run " +
      "and the conditions under which they were obtained.",
    inputSchema: {
      type: "object",
      properties: {
        dataset: { type: "string", description: "Dataset URL or bare filename" },
      },
      required: ["dataset"],
      additionalProperties: false,
    },
  },
  {
    name: "get_method",
    description:
      "Fetch a reproducible method: reading a browser extension's permissions, " +
      "measuring OCR recall with a control run, or choosing between " +
      "print-to-PDF and screen capture. Omit the argument to list them.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string" } },
      additionalProperties: false,
    },
  },
  {
    name: "extract_citation",
    description:
      "Read the citation details a web page declares about itself and return them as " +
      "a structured record plus ready-to-import RIS and BibTeX. Covers journal " +
      "articles, book chapters, conference papers, preprints, theses, reports, " +
      "datasets, videos and plain web pages. Use when a source has to be cited, " +
      "archived, or added to a reference manager. Says so plainly when a page turns " +
      "out to be an error page or an access wall, instead of inventing a reference.",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Address of the page to read" },
      },
      required: ["url"],
      additionalProperties: false,
    },
  },
];

// Der Endpunkt liefert ausschliesslich oeffentliche Daten und kennt keine
// Sitzung — ein weit gefasstes CORS gibt hier nichts preis, oeffnet aber
// browserbasierten Clients ueberhaupt erst den Zugang.
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type, mcp-protocol-version",
  "access-control-max-age": "86400",
};

const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...CORS, ...extra },
  });

const rpcOk = (id, result) => json({ jsonrpc: "2.0", id, result });
const rpcErr = (id, code, message) => json({ jsonrpc: "2.0", id, error: { code, message } });
const textResult = (s) => ({ content: [{ type: "text", text: s }] });

// ---------------------------------------------------------------------------
// Zitationsangaben aus einer fremden Seite
//
// Dieselben Regeln wie in der Erweiterung, aber ohne Dokumentbaum: hier steht
// nur der ausgelieferte Quelltext zur Verfuegung. Was eine Seite per
// JavaScript nachtraegt, ist damit unsichtbar — das ist eine Grenze und wird
// als solche gemeldet, nicht ueberspielt.
//
// Geraten wird nichts. Liegt ein Feld nicht vor, fehlt es in der Ausgabe.
// ---------------------------------------------------------------------------

function entzeichnen(s) {
  return String(s || "")
    .replace(/&#(\d+);/g, (_, n) => String.fromCharCode(+n))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCharCode(parseInt(n, 16)))
    .replace(/&quot;/g, '"').replace(/&apos;/g, "'").replace(/&nbsp;/g, " ")
    .replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&")
    .replace(/\s+/g, " ").trim();
}

/** Alle meta-Angaben als { name: [werte] }. */
function metaLesen(html) {
  const m = {};
  const kopf = html.slice(0, 400000);   // Angaben stehen im Kopf; der Rest waere Ballast
  const re = /<meta\b([^>]*)>/gi;
  let t;
  while ((t = re.exec(kopf)) !== null) {
    const attr = t[1];
    const n = (attr.match(/\b(?:name|property)\s*=\s*["']([^"']+)["']/i) || [])[1];
    const v = (attr.match(/\bcontent\s*=\s*["']([^"']*)["']/i) || [])[1];
    if (!n || !v) continue;
    const k = n.toLowerCase();
    (m[k] = m[k] || []).push(entzeichnen(v));
  }
  return m;
}

function jsonLdLesen(html) {
  const re = /<script[^>]+type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let t;
  while ((t = re.exec(html)) !== null) {
    try {
      const j = JSON.parse(t[1].trim());
      for (const o of (Array.isArray(j) ? j : [j])) {
        const typ = String((o && o["@type"]) || "");
        if (/Article|Book|Thesis|Chapter|Posting|VideoObject|Dataset|Report|Map/i.test(typ)) return o;
      }
    } catch (_) { /* fehlerhaftes JSON-LD ist haeufig und kein Grund aufzugeben */ }
  }
  return {};
}

function quelleAusHtml(html, endgueltigeUrl) {
  const meta = metaLesen(html);
  const ld = jsonLdLesen(html);
  const erste = (...k) => { for (const x of k) if (meta[x] && meta[x][0]) return meta[x][0]; return ""; };
  const alle = (...k) => { for (const x of k) if (meta[x] && meta[x].length) return meta[x].slice(); return []; };
  const u = new URL(endgueltigeUrl);

  const titelRoh = erste("citation_title", "dc.title", "dcterms.title", "og:title") ||
                   (ld.headline || ld.name || "") ||
                   entzeichnen((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || "");

  const rohDatum = erste("citation_publication_date", "citation_date", "citation_cover_date",
                         "citation_online_date", "prism.publicationdate", "dc.date",
                         "dcterms.issued", "article:published_time") ||
                   String(ld.datePublished || ld.uploadDate || "");
  const jahr = (String(rohDatum).match(/\b(1[5-9]\d{2}|20\d{2})\b/) || [""])[0];

  let doi = erste("citation_doi", "prism.doi", "dc.identifier.doi", "doi").replace(/^doi:\s*/i, "");
  if (!doi) {
    const t = endgueltigeUrl.match(/\b10\.\d{4,9}\/[-._;()A-Za-z0-9]+/);
    if (t) doi = t[0].replace(/[.,;)]+$/, "");
  }

  let autoren = alle("citation_author", "dc.creator", "dcterms.creator", "author",
                     "citation_authors", "article:author");
  if (autoren.length === 1 && /;/.test(autoren[0])) autoren = autoren[0].split(";");
  // Leere Namen aussortieren. Eine koreanische Zeitschrift lieferte
  // content=";;;;;" — daraus wurden sechs leere Verfasser, die als
  // vollstaendige Angabe durchgingen und in BibTeX zu "{ and  and }" wurden.
  autoren = autoren.map((s) => String(s).trim()).filter((s) => s.length > 1);
  if (!autoren.length && ld.author) {
    autoren = (Array.isArray(ld.author) ? ld.author : [ld.author])
      .map((x) => String(typeof x === "string" ? x : (x && x.name) || "").trim())
      .filter((s) => s.length > 1);
  }

  const buchTitel = erste("citation_inbook_title", "citation_book_title", "citation_series_title");
  const tagung = erste("citation_conference_title", "citation_conference");
  const issn = erste("citation_issn", "prism.issn", "citation_eissn");
  const isbn = erste("citation_isbn");
  const zeitschrift = erste("citation_journal_title", "prism.publicationname", "dc.source");
  const seiteVon = erste("citation_firstpage", "prism.startingpage");
  const ldTyp = String(ld["@type"] || "");

  const art =
      meta["citation_dissertation_institution"] ? "Hochschulschrift"
    : tagung ? "Konferenzbeitrag"
    : (isbn && (seiteVon || buchTitel)) ? "Buchkapitel"
    : isbn ? "Buch"
    : (issn || zeitschrift) ? "Zeitschriftenaufsatz"
    : (meta["citation_arxiv_id"] || /arxiv\.org|biorxiv|medrxiv|ssrn|psyarxiv|preprints\.org|osf\.io/i.test(endgueltigeUrl))
        ? "Preprint"
    : /VideoObject/i.test(ldTyp) ? "Video"
    : /(^|[^a-z])Dataset/i.test(ldTyp) ? "Datensatz"
    : /Report/i.test(ldTyp) ? "Bericht"
    : "Internetquelle";

  const kanon = entzeichnen(
    (html.match(/<link[^>]+rel\s*=\s*["']canonical["'][^>]*>/i) || [""])[0]
      .match(/href\s*=\s*["']([^"']+)["']/i)?.[1] || "");

  const q = {
    art,
    title: titelRoh,
    authors: autoren,
    year: jahr,
    date: String(rohDatum || ""),
    journal: zeitschrift || buchTitel || tagung,
    container: (art === "Buchkapitel" || art === "Konferenzbeitrag") ? (buchTitel || tagung) : "",
    volume: erste("citation_volume", "prism.volume"),
    issue: erste("citation_issue", "prism.number"),
    firstPage: seiteVon,
    lastPage: erste("citation_lastpage", "prism.endingpage"),
    doi,
    issn,
    isbn,
    publisher: erste("citation_publisher", "dc.publisher", "citation_dissertation_institution",
                     "citation_technical_report_institution") ||
               (art === "Preprint" && meta["citation_arxiv_id"] ? "arXiv" : ""),
    language: erste("citation_language", "dc.language") ||
              (html.match(/<html[^>]+lang\s*=\s*["']([^"'-]+)/i) || [])[1] || "",
    licence: erste("dc.rights", "dcterms.license", "citation_license") ||
             (typeof ld.license === "string" ? ld.license : (ld.license && ld.license.url) || ""),
    url: endgueltigeUrl,
    canonicalUrl: kanon || erste("og:url") || "",
    fullTextUrls: [],
    retrievedAt: new Date().toISOString(),
    website: erste("og:site_name") || u.hostname.replace(/^www\./, ""),
  };
  for (const [k, art2] of [["citation_pdf_url", "pdf"], ["citation_xml_url", "xml"],
                           ["citation_fulltext_html_url", "html"]]) {
    const v = erste(k);
    if (v) { try { q.fullTextUrls.push({ type: art2, url: new URL(v, endgueltigeUrl).href }); } catch (_) {} }
  }

  // Seitenname als Anhaengsel im Titel abschneiden — aber nur im Abgleich mit
  // dem angegebenen Seitennamen oder dem Namen der Domain, nie geraten.
  const teile = u.hostname.split(".");
  const kern = teile.length > 1 ? teile[teile.length - 2] : teile[0];
  const tm = q.title.match(/^(.*?)\s*[|–—-]\s*([^|–—-]+)$/);
  if (tm && tm[1].trim().length >= 3) {
    // Mindestlaenge, weil sonst nichts uebrig bleibt: bioRxiv liefert
    // "| bioRxiv" als Titel, und ohne die Pruefung wurde daraus ein leerer
    // Titel mit angehaengtem Seitennamen — schlechter als der Rohwert.
    const schwanz = tm[2].trim().toLowerCase();
    if (schwanz === (erste("og:site_name") || "").trim().toLowerCase() ||
        schwanz === kern.toLowerCase()) q.title = tm[1].trim();
  }
  // Bleibt nur der Seitenname stehen, ist der Titel unbrauchbar.
  q.title = q.title.replace(/^[\s|–—-]+|[\s|–—-]+$/g, "").trim();
  // Bleibt nach der Bereinigung nur der Name der Website stehen, ist das kein
  // Werktitel. bioRxiv liefert "| bioRxiv" — daraus eine Quellenangabe zu
  // bauen hiesse, den Namen des Servers als Titel der Arbeit auszugeben.
  const nurSeitenname = q.title.toLowerCase() === (erste("og:site_name") || "").trim().toLowerCase() ||
                        q.title.toLowerCase() === kern.toLowerCase();
  // Ein Titel aus lauter Ziffern ist eine Datensatznummer, kein Werktitel.
  // Ein Datenarchiv lieferte "1643858" als Titel einer Gesteinsprobe — als
  // Quellenangabe waere das nicht wiederauffindbar.
  const nurNummer = /^[\d\s.,;:\/-]{1,24}$/.test(q.title.trim());
  // Traegt der Titel eine Kennung statt eines Werktitels, ist die Angabe zwar
  // korrekt wiedergegeben, aber als Literaturhinweis schwer benutzbar. Ein
  // Bakterienarchiv lieferte "Archive BacDiveID:10.13145/bacdive113535...".
  // Nicht korrigiert — das waere geraten — sondern benannt.
  if (!nurNummer && /\b(10\.\d{4,9}\/|[A-Za-z]+ID:|accession|record\s*(no|number))/i.test(q.title)) {
    q.titleNote = "The title the page declares contains an identifier rather than a "
                + "descriptive title. Check it against the work itself before citing.";
  }

  // Koerperschaft als Urheber. Bei Behoerden-, Statistik- und Rechtsquellen
  // gibt es keine Person, und das ist kein Mangel: nach APA ist dort die
  // herausgebende Einrichtung der Urheber. Ohne diese Regel blieb die Haelfte
  // der amtlichen Quellen unvollstaendig, obwohl die Angabe vorliegt.
  if (!q.authors.length && !q.doi) {
    const koerper =
      (typeof ld.publisher === "object" && ld.publisher && ld.publisher.name) ||
      (typeof ld.publisher === "string" ? ld.publisher : "") ||
      erste("og:site_name", "dc.publisher", "publisher", "author", "twitter:site");
    if (koerper && koerper.trim().length > 1) {
      q.authors = [koerper.trim().replace(/^@/, "")];
      q.corporateAuthor = true;
    }
  }

  // Zugangsschranken formulieren sich sehr unterschiedlich; ein Muster, das
  // nur am Zeilenanfang sucht, uebersieht die meisten. Am 02.08.2026 kam
  // SSOAR mit "Making sure you're not a bot!" durch und erzeugte einen leeren
  // BibTeX-Satz mit dem Schluessel "anon".
  // Zwei Gruppen, und das ist der Punkt: eindeutige Schranken-Formulierungen
  // duerfen ueberall im Titel stehen, generische Woerter nur am Anfang.
  // "Error Analysis in Second Language Acquisition" ist ein Fachtitel, keine
  // Fehlerseite — ein Muster mit \berror\b haette ihn verworfen.
  const eindeutig = /(just a moment|attention required|access denied|checking your browser|are you (a )?(robot|human)|not a bot|verify you are (human|not)|security check required|please enable javascript)/i;
  const generisch = /^\W*(40[0-9]|41[0-9]|50[0-9]|not found|page not found|forbidden|unauthorized|zugriff verweigert|seite nicht gefunden|bitte bestätigen)\b/i;
  // "Error" allein sagt nichts: "Error Analysis in Second Language
  // Acquisition" ist ein Fachtitel. Erst was darauf folgt entscheidet.
  const fehlerwort = /^\W*error\s*(\d{3}|page|occurred|has occurred|[:.–—-]|$)/i;
  q.warning = (nurSeitenname || nurNummer)
    ? "The only title the page declares is the name of the site or a bare record number, not the title of a work. Nothing here identifies a source."
    : (eindeutig.test(q.title) || generisch.test(q.title.trim()) || fehlerwort.test(q.title.trim()))
    ? "The page looks like an error message or an access wall, not content. The details below are not usable as a reference."
    // Eine Schranke, die sich anders nennt, verraet sich an der Duennheit:
    // kaum Auszeichnung und keine einzige Verlagsangabe.
    : (html.length < 6000 && !q.authors.length && !q.doi && !q.journal)
      ? "The page carries almost no content and declares no citation metadata. It is more likely an interstitial or a block page than the source itself."
      : "";
  q.source = Object.keys(meta).some((k) => k.startsWith("citation_"))
    ? "publisher metadata in the page (citation_*)"
    : Object.keys(meta).some((k) => k.startsWith("dc."))
      ? "Dublin Core metadata in the page"
      : ldTyp ? "schema.org metadata in the page" : "page title and address";
  q.complete = !q.warning && !!(q.title && (q.authors.length || q.publisher) && q.year);
  return q;
}

// DOI-Registrierungsstelle. Wo eine DOI vorliegt, ist sie die bessere Quelle
// als die Verlagsseite: sie ist autoritativ, offen und wird nicht gesperrt.
// Gemessen am 02.08.2026: von neun Zufallsquellen wies der Verlag fuenf
// serverseitige Abrufe mit HTTP 403 ab — unabhaengig davon, wie sich der
// Leser nannte. Der Umweg ueber die Registrierungsstelle liefert genau dort.
//
// Das gilt nur fuer diesen Endpunkt. Die Erweiterung im Browser des Nutzers
// fragt weiterhin niemanden: sie liest die Seite, die ohnehin offen ist, und
// ein Abruf bei Crossref wuerde verraten, was gerade gelesen wird.
async function ausRegistrierung(doi) {
  const kopf = { accept: "application/json", "user-agent": AGENT };
  try {
    const r = await fetch("https://api.crossref.org/works/" + encodeURIComponent(doi),
                          { headers: kopf, cf: { cacheTtl: 0 } });
    if (r.ok) {
      const m = (await r.json()).message || {};
      const autoren = (m.author || [])
        .map((a) => [a.family, a.given].filter(Boolean).join(", "))
        .filter((x) => x.length > 1);
      const jahr = (((m.issued || {})["date-parts"] || [[]])[0] || [])[0];
      return {
        title: (m.title || [])[0] || "",
        authors: autoren,
        year: jahr ? String(jahr) : "",
        journal: (m["container-title"] || [])[0] || "",
        volume: m.volume || "", issue: m.issue || "",
        firstPage: (m.page || "").split("-")[0] || "",
        lastPage: (m.page || "").split("-")[1] || "",
        publisher: m.publisher || "",
        issn: (m.ISSN || [])[0] || "", isbn: (m.ISBN || [])[0] || "",
        doi: m.DOI || doi,
        art: /journal-article/.test(m.type || "") ? "Zeitschriftenaufsatz"
           : /book-chapter/.test(m.type || "") ? "Buchkapitel"
           : /proceedings/.test(m.type || "") ? "Konferenzbeitrag"
           : /^book/.test(m.type || "") ? "Buch"
           : /posted-content/.test(m.type || "") ? "Preprint" : "Internetquelle",
        source: "DOI registration agency (Crossref)",
      };
    }
  } catch (_) { /* weiter zu DataCite */ }
  try {
    const r = await fetch("https://api.datacite.org/dois/" + encodeURIComponent(doi),
                          { headers: kopf, cf: { cacheTtl: 0 } });
    if (!r.ok) return null;
    const a = ((await r.json()).data || {}).attributes || {};
    return {
      title: ((a.titles || [])[0] || {}).title || "",
      authors: (a.creators || []).map((c) => c.name || "").filter((x) => x.length > 1),
      year: a.publicationYear ? String(a.publicationYear) : "",
      journal: ((a.container || {}).title) || "",
      publisher: a.publisher || "", doi: a.doi || doi,
      volume: "", issue: "", firstPage: "", lastPage: "", issn: "", isbn: "",
      art: "Datensatz", source: "DOI registration agency (DataCite)",
    };
  } catch (_) { return null; }
}

/** Bringt einen Registrierungssatz auf dieselbe Form wie die Seitenauswertung. */
function vervollstaendigen(reg, url) {
  const jetzt = new Date().toISOString();
  return {
    art: reg.art, title: reg.title, authors: reg.authors, year: reg.year,
    date: reg.year, journal: reg.journal, container: reg.art === "Buchkapitel" ? reg.journal : "",
    volume: reg.volume, issue: reg.issue, firstPage: reg.firstPage, lastPage: reg.lastPage,
    doi: reg.doi, issn: reg.issn, isbn: reg.isbn, publisher: reg.publisher,
    language: "", licence: "", url: url, canonicalUrl: "",
    fullTextUrls: [], retrievedAt: jetzt,
    website: (() => { try { return new URL(url).hostname.replace(/^www\./, ""); } catch (_) { return ""; } })(),
    warning: "", source: reg.source,
    complete: !!(reg.title && reg.authors.length && reg.year),
  };
}

function risAus(q) {
  const typ = { Zeitschriftenaufsatz: "JOUR", Buchkapitel: "CHAP", Buch: "BOOK",
                Konferenzbeitrag: "CPAPER", Hochschulschrift: "THES", Bericht: "RPRT",
                Datensatz: "DATA", Video: "VIDEO", Preprint: "UNPB" }[q.art] || "ELEC";
  const z = ["TY  - " + typ];
  const s = (k, v) => { if (v) z.push(k + "  - " + String(v).replace(/[\r\n]+/g, " ")); };
  q.authors.forEach((a) => s("AU", a));
  s("TI", q.title);
  s("PY", q.year);
  const iso = String(q.date || "").match(/^(\d{4})[-/](\d{2})[-/](\d{2})/);
  if (iso) s("DA", `${iso[1]}/${iso[2]}/${iso[3]}`);
  if (q.container) s("T2", q.container); else s("JO", q.journal);
  s("VL", q.volume); s("IS", q.issue); s("SP", q.firstPage); s("EP", q.lastPage);
  s("DO", q.doi); s("SN", q.isbn || q.issn); s("PB", q.publisher); s("LA", q.language);
  s("UR", q.canonicalUrl || q.url);
  s("Y2", q.retrievedAt);
  (q.fullTextUrls || []).forEach((d) => { if (d.type === "pdf") s("L1", d.url); });
  s("C1", q.licence);
  s("N1", (q.warning ? "WARNING: " + q.warning + " " : "") +
          "Fields taken from " + q.source + ", read server-side without JavaScript.");
  z.push("ER  - ");
  return z.join("\r\n") + "\r\n";
}

function bibtexAus(q) {
  const typ = { Zeitschriftenaufsatz: "article", Buchkapitel: "incollection", Buch: "book",
                Konferenzbeitrag: "inproceedings", Hochschulschrift: "phdthesis",
                Bericht: "techreport", Datensatz: "misc", Video: "misc",
                Preprint: "misc" }[q.art] || "misc";
  const ersterNachname = (q.authors[0] || "anon").split(",")[0].split(/\s+/).pop()
    .replace(/[^A-Za-z]/g, "").toLowerCase() || "anon";
  const schluessel = ersterNachname + (q.year || "");
  const esc = (v) => String(v).replace(/[{}]/g, "");
  const f = [];
  const add = (k, v) => { if (v) f.push(`  ${k} = {${esc(v)}}`); };
  add("author", q.authors.join(" and "));
  add("title", q.title);
  add("year", q.year);
  if (q.container) add("booktitle", q.container); else add("journal", q.journal);
  add("volume", q.volume); add("number", q.issue);
  if (q.firstPage) add("pages", q.firstPage + (q.lastPage && q.lastPage !== q.firstPage ? "--" + q.lastPage : ""));
  add("doi", q.doi); add("issn", q.issn); add("isbn", q.isbn);
  add("publisher", q.publisher); add("language", q.language);
  add("url", q.canonicalUrl || q.url);
  add("urldate", q.retrievedAt.slice(0, 10));
  add("note", q.warning || "");
  return `@${typ}{${schluessel},\n${f.join(",\n")}\n}\n`;
}

async function fetchJson(origin, path) {
  const url = origin + path;
  const r = await fetch(url, {
    headers: { accept: "application/json", "user-agent": "provinglab-mcp/1.0" },
    // Der Subrequest darf nicht am Edge-Cache haengen bleiben: die Discovery-
    // Dateien aendern sich haeufiger als der Rest und muessen aktuell sein.
    cf: { cacheTtl: 60, cacheEverything: false },
  });
  if (!r.ok) throw new Error(`GET ${url} -> ${r.status} ${r.statusText}`);
  return r.json();
}

async function runTool(origin, name, args) {
  if (name === "list_measurements") {
    const cat = await fetchJson(origin, "/.well-known/api-catalog");
    const rows = cat.linkset
      .filter((e) => e.anchor.includes("/data/"))
      .map((e) => {
        const via = e.via && e.via[0] ? e.via[0].href : "";
        return `- dataset: ${e.anchor}${via ? `\n  method: ${via}` : ""}`;
      });
    return textResult(
      `Measurements with raw data (${rows.length}):\n${rows.join("\n")}\n\n` +
        `Narrative index of everything published here: ${origin}/llms.txt`
    );
  }

  if (name === "get_measurement_data") {
    const d = String((args && args.dataset) || "");
    if (!d) throw new Error("dataset is required");
    // Nur der Dateiname zaehlt. Ein Praefixvergleich auf "/data/" reicht nicht:
    // "/data/../beliebig" beginnt damit und wird vom Server trotzdem
    // normalisiert — gemessen am 02.08.2026, es lieferte eine fremde Datei aus.
    // Deshalb wird der Name geprueft, nicht der Pfad zusammengesetzt.
    const roh = d.startsWith("http") ? new URL(d).pathname : d;
    const name2 = roh.split("/").pop() || "";
    if (!/^[A-Za-z0-9._-]+\.json$/.test(name2) || name2.includes("..")) {
      throw new Error("dataset must be a plain .json filename from /data/");
    }
    return textResult(JSON.stringify(await fetchJson(origin, "/data/" + name2), null, 2));
  }

  if (name === "extract_citation") {
    const roh = String((args && args.url) || "").trim();
    if (!roh) throw new Error("url is required");
    let ziel;
    try { ziel = new URL(roh); } catch (_) { throw new Error("url is not a valid address"); }
    // Nur oeffentliche Adressen. Ein Worker sitzt in fremdem Netz; ohne diese
    // Pruefung liesse sich der Endpunkt als Sprungbrett auf interne Dienste
    // verwenden — die klassische serverseitige Anfragefaelschung.
    if (!/^https?:$/.test(ziel.protocol)) throw new Error("only http and https are supported");
    if (/^(localhost|127\.|10\.|192\.168\.|169\.254\.|0\.|\[?::1)/i.test(ziel.hostname) ||
        /^172\.(1[6-9]|2\d|3[01])\./.test(ziel.hostname) ||
        /\.(local|internal|localdomain)$/i.test(ziel.hostname)) {
      throw new Error("only public addresses can be read");
    }

    const r = await fetch(ziel.href, {
      redirect: "follow",
      headers: {
        // Offen benennen, wer anfragt. Wer den Zugriff nicht wuenscht, kann
        // ihn so unterscheiden und aussperren.
        "user-agent": "provinglab-mcp/1.5 (+https://provinglab.dev/; citation metadata reader)",
        accept: "text/html,application/xhtml+xml",
        "accept-language": "en,de;q=0.8",
      },
      // Nicht zwischenspeichern. Eine Zugangsschranke antwortet mit HTTP 200
      // und landete damit fuer fuenf Minuten im Edge-Cache — die Pruefung auf
      // Schrankenseiten lief danach gegen die gespeicherte Antwort und konnte
      // gar nicht greifen. Bei einem Werkzeug, das selten aufgerufen wird und
      // dessen Ergebnis zitiert wird, ist Aktualitaet mehr wert als Ersparnis.
      cf: { cacheTtl: 0, cacheEverything: false },
    });
    // DOI in der Adresse? Dann steht ein zweiter Weg offen, falls die Seite
    // sperrt — die Registrierungsstelle antwortet immer.
    const doiInUrl = (ziel.href.match(/\b10\.\d{4,9}\/[-._;()A-Za-z0-9]+/) || [])[0];

    if (!r.ok) {
      if (doiInUrl) {
        const reg = await ausRegistrierung(doiInUrl.replace(/[.,;)]+$/, ""));
        if (reg && reg.title) {
          const q2 = vervollstaendigen(reg, ziel.href);
          return textResult(JSON.stringify({
            ...q2, ris: risAus(q2), bibtex: bibtexAus(q2),
            note: `The page itself answered ${r.status}; these details come from the DOI `
                + `registration agency, which is authoritative for them. Nothing was read `
                + `from the publisher's page.`,
          }, null, 2));
        }
      }
      return textResult(JSON.stringify({
        url: ziel.href, httpStatus: r.status,
        warning: `The server answered ${r.status} ${r.statusText}. No citation data was read.`,
        hint: r.status === 403 || r.status === 503
          ? "Publisher sites frequently block server-side readers, and no DOI was available "
            + "as a fallback. Open the page in a browser and read it there."
          : undefined,
      }, null, 2));
    }
    const typ = r.headers.get("content-type") || "";
    if (!/html|xml/i.test(typ)) {
      return textResult(JSON.stringify({
        url: r.url, contentType: typ,
        warning: "The address does not return an HTML page, so it declares no citation metadata.",
      }, null, 2));
    }
    // Gedeckelt, damit eine einzelne riesige Seite den Aufruf nicht sprengt;
    // die Angaben stehen im Kopf, lange vor dieser Grenze.
    const html = (await r.text()).slice(0, 1500000);
    let q = quelleAusHtml(html, r.url);
    // Sperrseite oder taube Angaben? Dann zaehlt die Registrierungsstelle.
    if ((q.warning || !q.authors.length) && (q.doi || doiInUrl)) {
      const reg = await ausRegistrierung((q.doi || doiInUrl).replace(/[.,;)]+$/, ""));
      if (reg && reg.title && reg.authors.length) {
        q = vervollstaendigen(reg, r.url);
        q.note = "The page declared no usable citation data; these details come from the "
               + "DOI registration agency.";
      }
    }
    return textResult(JSON.stringify({
      ...q,
      ris: risAus(q),
      bibtex: bibtexAus(q),
      limits: "Read server-side without JavaScript: details a page adds after loading are " +
              "invisible here, and sites that block non-browser clients return nothing. " +
              "Neither is reported as success.",
    }, null, 2));
  }

  if (name === "get_method") {
    const idx = await fetchJson(origin, "/.well-known/agent-skills/index.json");
    const want = args && args.name;
    if (!want) {
      return textResult(idx.skills.map((s) => `- ${s.name}: ${s.description}`).join("\n"));
    }
    const hit = idx.skills.find((s) => s.name === want);
    if (!hit) {
      return textResult(
        `No method named ${want}. Available: ${idx.skills.map((s) => s.name).join(", ")}`
      );
    }
    const r = await fetch(hit.url);
    return textResult(await r.text());
  }

  throw new Error(`unknown tool: ${name}`);
}

async function handleMcp(request, origin) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }
  if (request.method === "GET") {
    // Kein SSE: der Server ist zustandslos, es gibt nichts zu streamen.
    return json(
      { error: "This MCP endpoint is stateless. Send JSON-RPC over POST." },
      405,
      { allow: "POST" }
    );
  }
  if (request.method !== "POST") return json({ error: "method not allowed" }, 405);

  let msg;
  try {
    msg = await request.json();
  } catch {
    return rpcErr(null, -32700, "Parse error");
  }

  const batch = Array.isArray(msg) ? msg : [msg];
  const out = [];
  for (const m of batch) {
    const id = m && m.id !== undefined ? m.id : null;
    try {
      switch (m.method) {
        case "initialize":
          out.push({
            jsonrpc: "2.0",
            id,
            result: {
              protocolVersion: PROTOCOL,
              capabilities: { tools: { listChanged: false } },
              serverInfo: { name: "provinglab", version: VERSION },
              instructions:
                "Measurements on browser tools, OCR pipelines and AI-assisted " +
                "development. Every dataset here has a documented method and a " +
                "control run. Start with list_measurements.",
            },
          });
          break;
        case "notifications/initialized":
          break; // Benachrichtigung, keine Antwort
        case "ping":
          out.push({ jsonrpc: "2.0", id, result: {} });
          break;
        case "tools/list":
          out.push({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
          break;
        case "tools/call": {
          const p = m.params || {};
          const res = await runTool(origin, p.name, p.arguments || {});
          out.push({ jsonrpc: "2.0", id, result: res });
          break;
        }
        default:
          if (id !== null) out.push({ jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${m.method}` } });
      }
    } catch (e) {
      if (id !== null) {
        out.push({
          jsonrpc: "2.0",
          id,
          result: { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true },
        });
      }
    }
  }
  if (!out.length) return new Response(null, { status: 202 });
  return json(Array.isArray(msg) ? out : out[0]);
}

/** Kompakter HTML→Markdown-Wandler. Bewusst klein: die Seiten hier sind
 *  handgeschriebenes, flaches HTML ohne Frameworks. */
function toMarkdown(html) {
  const titel = (html.match(/<title>([\s\S]*?)<\/title>/i) || [, ""])[1].trim();
  let s = html;
  s = s.replace(/<script[\s\S]*?<\/script>/gi, "");
  s = s.replace(/<style[\s\S]*?<\/style>/gi, "");
  s = s.replace(/<head[\s\S]*?<\/head>/gi, "");
  s = s.replace(/<nav[\s\S]*?<\/nav>/gi, "");
  s = s.replace(/<footer[\s\S]*?<\/footer>/gi, "");
  s = s.replace(/<!--[\s\S]*?-->/g, "");

  s = s.replace(/<h([1-6])[^>]*>([\s\S]*?)<\/h\1>/gi, (_, n, t) => `\n\n${"#".repeat(+n)} ${t.trim()}\n\n`);
  s = s.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (_, t) => `- ${t.trim()}\n`);
  s = s.replace(/<(pre|code)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `\n\`\`\`\n${t.trim()}\n\`\`\`\n`);
  s = s.replace(/<a [^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, (_, h, t) => `[${t.trim()}](${h})`);
  s = s.replace(/<(strong|b)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `**${t.trim()}**`);
  s = s.replace(/<(em|i)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `*${t.trim()}*`);
  s = s.replace(/<(p|div|section|article|tr)[^>]*>/gi, "\n");
  s = s.replace(/<br\s*\/?>/gi, "\n");
  s = s.replace(/<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi, (_, t) => `| ${t.trim()} `);
  s = s.replace(/<[^>]+>/g, "");

  s = s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<")
       .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
       .replace(/&mdash;/g, "—").replace(/&ndash;/g, "–");
  s = s.replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
  return `---\ntitle: ${titel}\n---\n\n${s}\n`;
}

function wantsMarkdown(request) {
  const a = (request.headers.get("accept") || "").toLowerCase();
  if (!a.includes("text/markdown") && a !== "text/*") return false;
  // Browser senden text/html mit hoeherer Gewichtung — die bekommen HTML.
  const md = /text\/markdown(?:;q=([\d.]+))?/.exec(a);
  const ht = /text\/html(?:;q=([\d.]+))?/.exec(a);
  const q = (m) => (m ? (m[1] === undefined ? 1 : parseFloat(m[1])) : 0);
  return q(md) >= q(ht);
}


/* --- OAuth: echt, aber nicht erforderlich ---------------------------------
 *
 * Nichts auf dieser Seite ist geschuetzt, und daran aendert sich nichts. Der
 * Grund fuer diesen Teil ist ein anderer: Manche MCP-Clients erwarten einen
 * Autorisierungsserver und verbinden sich sonst gar nicht erst. Fuer die
 * bietet der Endpunkt einen vollstaendigen Weg an — dynamische Registrierung
 * nach RFC 7591, Token nach Client Credentials, und der MCP-Endpunkt nimmt das
 * Token entgegen.
 *
 * Was hier NICHT passiert: so zu tun, als wuerde damit etwas geschuetzt. Der
 * MCP-Endpunkt antwortet mit und ohne Token identisch, jede Registrierung wird
 * angenommen, und auth.md sagt das ausdruecklich. Ein Token, das nichts
 * freischaltet, darf nicht so aussehen, als taete es das.
 *
 * Die Signatur verhindert nur, dass ein erfundenes Token als gueltig gilt —
 * sie schuetzt keinen Zugang. Der Schluessel steht deshalb offen im Code;
 * ihn geheim zu halten waere Theater.
 */
const OAUTH_KEY = "provinglab-public-endpoint-no-secret-needed";
const TOKEN_TTL = 3600;

async function hmac(daten) {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(OAUTH_KEY),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(daten));
  return btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function tokenErzeugen(clientId) {
  const nutz = btoa(JSON.stringify({
    sub: clientId, iss: "https://provinglab.dev", aud: "https://provinglab.dev",
    iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + TOKEN_TTL,
  })).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return nutz + "." + (await hmac(nutz));
}

function autorisierungsserver() {
  return {
    issuer: "https://provinglab.dev",
    authorization_endpoint: "https://provinglab.dev/oauth/authorize",
    token_endpoint: "https://provinglab.dev/oauth/token",
    registration_endpoint: "https://provinglab.dev/oauth/register",
    jwks_uri: "https://provinglab.dev/oauth/jwks",
    scopes_supported: ["read"],
    response_types_supported: ["code"],
    grant_types_supported: ["client_credentials", "authorization_code"],
    token_endpoint_auth_methods_supported: ["none", "client_secret_post"],
    code_challenge_methods_supported: ["S256"],
    service_documentation: "https://provinglab.dev/auth.md",
    // Aufbau nach der auth.md-Spezifikation (github.com/workos/auth.md).
    // Die Feldnamen lauten dort identity_types_supported und
    // credential_types_supported je Typ — nicht umgekehrt, wie die Prosa
    // des Pruefberichts nahelegt. Drei Runden Raten haetten sich mit einem
    // Blick in die Spezifikation erledigt.
    agent_auth: {
      skill: "https://provinglab.dev/auth.md",
      register_uri: "https://provinglab.dev/oauth/register",
      claim_uri: "https://provinglab.dev/oauth/claim",
      revocation_uri: "https://provinglab.dev/oauth/revoke",
      identity_endpoint: "https://provinglab.dev/oauth/register",
      claim_endpoint: "https://provinglab.dev/oauth/claim",
      events_endpoint: null,
      identity_types_supported: ["anonymous", "service_auth"],
      anonymous: {
        credential_types_supported: ["none"],
        register_uri: "https://provinglab.dev/oauth/register",
        claim_uri: "https://provinglab.dev/oauth/claim",
        description: "Send no credentials. The normal case, and it grants full access.",
      },
      service_auth: {
        credential_types_supported: ["client_secret_post", "none"],
        claim_uri: "https://provinglab.dev/oauth/claim",
        register_uri: "https://provinglab.dev/oauth/register",
        token_uri: "https://provinglab.dev/oauth/token",
        grant_types_supported: ["client_credentials"],
        description: "For clients that require an OAuth flow. Grants nothing beyond anonymous.",
      },
      events_supported: [],
      // Der wichtigste Eintrag: Es ist nicht noetig.
      authentication_required: false,
      note: "All resources are public. Credentials are accepted for clients that require an OAuth flow, and grant no additional access.",
    },
  };
}

async function handleOAuth(pfad, request) {
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

  if (pfad === "/oauth/register") {
    // RFC 7591: jede Registrierung wird angenommen, weil es nichts zu pruefen
    // gibt. Der Client bekommt eine echte, stabile Kennung.
    let wunsch = {};
    try { wunsch = await request.json(); } catch { /* leerer Rumpf ist zulaessig */ }
    const id = "pl_" + (await hmac(JSON.stringify(wunsch.client_name || "anonymous"))).slice(0, 24);
    return json({
      client_id: id,
      client_id_issued_at: Math.floor(Date.now() / 1000),
      client_name: wunsch.client_name || "anonymous",
      grant_types: ["client_credentials"],
      token_endpoint_auth_method: "none",
      scope: "read",
    }, 201);
  }

  if (pfad === "/oauth/token") {
    let clientId = "anonymous";
    try {
      const ct = request.headers.get("content-type") || "";
      if (ct.includes("json")) {
        const b = await request.json();
        clientId = b.client_id || clientId;
      } else {
        const f = new URLSearchParams(await request.text());
        clientId = f.get("client_id") || clientId;
      }
    } catch { /* ohne Angabe: anonym */ }
    return json({
      access_token: await tokenErzeugen(clientId),
      token_type: "Bearer",
      expires_in: TOKEN_TTL,
      scope: "read",
    });
  }

  if (pfad === "/oauth/claim") {
    // Eine anonyme Identitaet an ein Konto zu binden, setzt Konten voraus.
    // Es gibt keine — und der Endpunkt sagt das, statt zu schweigen.
    return json({
      claimable: false,
      reason: "no_accounts",
      description:
        "There are no accounts to bind an identity to. Every resource on " +
        "provinglab.dev is public, so an anonymous identity already has full " +
        "access and nothing is gained by claiming it.",
      documentation: "https://provinglab.dev/auth.md",
    }, 200);
  }

  if (pfad === "/oauth/revoke") {
    // RFC 7009 verlangt 200 auch fuer unbekannte Token. Hier gilt das immer:
    // Ein Token schaltet nichts frei, es zurueckzuziehen aendert nichts.
    return json({
      revoked: true,
      note: "Tokens grant no access, so revocation has no effect on what a client can reach.",
    }, 200);
  }

  if (pfad === "/oauth/jwks") {
    // Symmetrisch signiert — es gibt keinen oeffentlichen Schluessel zu zeigen.
    return json({ keys: [] });
  }

  if (pfad === "/oauth/authorize") {
    return json({
      error: "not_required",
      error_description:
        "All resources on provinglab.dev are public. Use the token endpoint with " +
        "grant_type=client_credentials if your client needs a token, or send no " +
        "credentials at all.",
    }, 400);
  }

  return json({ error: "not_found" }, 404);
}

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);

      if (url.pathname === "/mcp" || url.pathname === "/mcp/") {
        return handleMcp(request, SITE);
      }

      if (url.pathname.startsWith("/oauth/")) {
        return handleOAuth(url.pathname, request);
      }

      if (url.pathname === "/.well-known/oauth-authorization-server") {
        return json(autorisierungsserver());
      }

      const upstream = await fetch(request);
      const ct = upstream.headers.get("content-type") || "";
      if (!wantsMarkdown(request) || !ct.includes("text/html") || !upstream.ok) {
        return upstream;
      }

      const md = toMarkdown(await upstream.text());
      const h = new Headers(upstream.headers);
      h.set("content-type", "text/markdown; charset=utf-8");
      h.set("x-markdown-tokens", String(Math.ceil(md.length / 4)));
      h.append("vary", "accept");
      h.delete("content-length");
      return new Response(md, { status: upstream.status, headers: h });
    } catch (e) {
      // Niemals die Seite wegen eines Fehlers hier ausknipsen.
      return fetch(request);
    }
  },
};
