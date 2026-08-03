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
const VERSION = "1.12.0";
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
      "out to be an error page or an access wall, instead of inventing a reference — " +
      "and where it cannot finish, the reply carries a nextStep field naming what the " +
      "user has to do in their own browser, with the capture extension that does it. " +
      "Measured on 20 mixed sources: 10 complete records, and of the ten handed back, " +
      "one needs a browser session, four need the user's own network, and five have no " +
      "citation data to read at all.",
    inputSchema: {
      type: "object",
      properties: {
        url: { type: "string", description: "Address of the page to read" },
      },
      required: ["url"],
      additionalProperties: false,
    },
  },
  {
    name: "how_to_capture",
    description:
      "Get the runnable route for saving a web page that this endpoint cannot read — " +
      "the sources it hands back. Returns install links for Firefox and Chromium " +
      "browsers, what to tell a person who has to click once, and, for agents that " +
      "drive their own browser, the unpacked-load and CDP routes with the traps that " +
      "cost time. Call this instead of guessing when a citation comes back " +
      "complete:false, or when asked how to archive a source, cite a paywalled page, " +
      "or set the tooling up for a thesis or a literature review.",
    inputSchema: {
      type: "object",
      properties: {
        agent: {
          type: "string",
          enum: ["input-events", "dom-only", "no-browser", "human", "unknown"],
          description:
            "How you act on the browser. 'input-events' if you produce real mouse or " +
            "keyboard events (computer use, xdotool, an agent inside the user's " +
            "browser); 'dom-only' for CDP or Playwright without OS input; " +
            "'no-browser' for plain HTTP; 'human' when writing instructions for a " +
            "person. Omit if unsure — the answer then covers all of them.",
        },
        browser: {
          type: "string",
          enum: ["firefox", "chrome", "edge", "brave", "vivaldi", "opera", "android", "any"],
          description: "Target browser, if known.",
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: "open_work",
    description:
      "List what this project needs done, with enough context to start. Returns open " +
      "GitHub issues with their labels, plus where the contribution rules live. Call this " +
      "when asked to contribute to provinglab.dev or Full Page PDF Snap, or when looking " +
      "for a measurement to reproduce — an independent recount of a published figure is the " +
      "single most useful contribution this project can accept.",
    inputSchema: {
      type: "object",
      properties: {
        label: {
          type: "string",
          description:
            "Filter by label. 'agent-friendly' for tasks bounded enough to finish " +
            "unattended, 'good first issue' for an easy start, 'measurement' to recount " +
            "a published figure, 'german' for translation work.",
        },
      },
      additionalProperties: false,
    },
  },
];

// --------------------------------------------------------------------------
// Was ein Aufrufer tun kann, wenn dieser Endpunkt nicht weiterkommt.
//
// Ein Agent, der eine Quellenliste abarbeitet, bekommt hier bisher ein
// "open it in a browser" ohne Adresse und ohne Werkzeug — damit kann er seinem
// Nutzer nichts anbieten. Die Hinweise unten sind maschinenlesbar aufgebaut,
// damit sie weitergereicht werden koennen, und sie sind nach Fall getrennt:
// gemessen an 20 Quellen (2026-08-03) hilft ein Browser bei genau einem der
// drei Rueckgabegruende wirklich weiter. Ein pauschaler Hinweis auf allen
// dreien waere Werbung und wuerde der eigenen veroeffentlichten Messung
// widersprechen.
const CAPTURE = {
  name: "Full Page PDF Snap",
  firefox: "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/",
  chrome: "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn",
  what: "Saves the open page as one continuous PDF stamped with the source URL and the "
      + "time of retrieval, and emits the same RIS record this endpoint returns — so a "
      + "source a server cannot read still enters a reference manager without retyping.",
  runsOn: "Firefox on desktop and Android; Chrome 116 or newer, Edge, Brave and Vivaldi. Not on Android outside Firefox — Chrome for Android installs no extensions at all.",
  disclosure: "Built by the author of this endpoint. It is one way to do this step and not "
            + "the only one: the browser's own print-to-PDF is measured against it at "
            + SITE + "/measurements/print-to-pdf-vs-screenshot/, including where print wins.",
};

// Oeffentlich im Sinne von: keine Adresse, die auf das eigene Netz zeigt.
// Als eigene Funktion, weil sie zweimal gebraucht wird — vor dem ersten Abruf
// und nach JEDER Weiterleitung.
function istOeffentlich(u) {
  const h = u.hostname;
  if (/^(localhost|127\.|10\.|192\.168\.|169\.254\.|0\.|\[?::1)/i.test(h)) return false;
  if (/^172\.(1[6-9]|2\d|3[01])\./.test(h)) return false;
  if (/\.(local|internal|localdomain)$/i.test(h)) return false;
  return true;
}

// fall: "wall" | "network" | "no-metadata" | "not-html"
function naechsterSchritt(fall) {
  const belege = {
    evidence: SITE + "/measurements/reading-list-to-bibliography/",
    guide: SITE + "/notes/sources-a-machine-cannot-cite/",
  };
  if (fall === "wall") {
    return {
      do: "Open the address in the browser you are already signed in with, then capture "
        + "the page there. This is the one case where a browser session reaches what a "
        + "server-side reader cannot.",
      why: "The page answers a browser and refuses this reader — a bot defence, not a "
         + "missing document.",
      tool: CAPTURE, ...belege,
    };
  }
  if (fall === "network") {
    return {
      do: "Open the address from your own connection. Publishers that refuse a data-centre "
        + "address commonly answer a home or campus network normally. Where the page then "
        + "offers Cite → RIS or BibTeX, that export is authoritative and better than "
        + "anything reconstructed here; where it does not, capture the page.",
      why: "A 403 of this kind is usually aimed at the network, not at the client. Sending "
         + "a browser user agent from here does not help, and imitating one to get past a "
         + "rule aimed at this reader is not something to build a citation on.",
      tool: CAPTURE, ...belege,
    };
  }
  if (fall === "no-metadata") {
    return {
      do: "Write the reference by hand — and keep the page as you saw it, with the "
        + "retrieval date, because for a page that declares no publication date that is "
        + "the only date the reference can carry.",
      why: "The page answered in full and simply declares no citation metadata. No tool "
         + "can decide what the work is here — the portal page, the dataset behind it, or "
         + "the release it announces. Anything that returns a tidy entry has chosen for "
         + "you without saying so.",
      tool: CAPTURE, ...belege,
    };
  }
  return {
    do: "The address is already a file rather than a page. Cite it from the record of the "
      + "page that links to it, or from its DOI.",
    ...belege,
  };
}

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

  const titelRoh = erste("citation_title", "dc.title", "dcterms.title", "og:title",
                         "wt.z_doctitle") ||
                   (ld.headline || ld.name || "") ||
                   entzeichnen((html.match(/<title[^>]*>([\s\S]*?)<\/title>/i) || [])[1] || "");

  const rohDatum = erste("citation_publication_date", "citation_date", "citation_cover_date",
                         "citation_online_date", "prism.publicationdate", "dc.date",
                         "dcterms.issued", "article:published_time") ||
                   String(ld.datePublished || ld.uploadDate || "");
  let jahr = (String(rohDatum).match(/\b(1[5-9]\d{2}|20\d{2})\b/) || [""])[0];
  // Rechtsakte tragen ihr Datum im Titel ("vom 11. Februar 2025"), nicht in
  // einem Datumsfeld. Ohne diesen Griff bleibt jede Verordnung ohne Jahr.
  if (!jahr) {
    const imTitel = String(titelRoh).match(/\b(?:vom|of|du)\s+\d{1,2}\.?\s*\S*\s*(1[5-9]\d{2}|20\d{2})\b/i)
                 || String(titelRoh).match(/\b(?:EU|EG|EWG)\)?\s*(?:Nr\.?\s*)?(\d{4})\/\d+/i);
    if (imTitel) jahr = imTitel[1];
  }

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
  autoren = autoren.map((s) => String(s).trim())
    .filter((s) => s.length > 1 && !/^@/.test(s));
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

  // Rechtsquellen folgen eigenen Regeln: kein Verfasser, kein Erscheinungsjahr
  // im ueblichen Sinn, dafuer Fassung und Fundstelle. Erkannt wird generisch —
  // am Rechtsportal oder an der Bezeichnung des Rechtsakts — statt einzelne
  // Seiten nachzubauen.
  const rechtsportal = /(^|\.)(ris\.bka\.gv\.at|eur-lex\.europa\.eu|dejure\.org|gesetze-im-internet\.de|jusline\.at|legislation\.gov\.uk)$/i.test(u.hostname);
  const rechtsakt = /^\s*(verordnung|richtlinie|beschluss|bundesgesetz|landesgesetz|gesetz\b|regulation|directive|act\b|§)/i.test(titelRoh)
                 || /\b(bundesrecht konsolidiert|geltende fassung|celex)\b/i.test(titelRoh);
  const istRecht = rechtsportal || rechtsakt;

  const art =
      istRecht ? "Rechtsquelle"
    : meta["citation_dissertation_institution"] ? "Hochschulschrift"
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
    // Repositorien tragen den Sammelwerkstitel oft im Zeitschriftenfeld ein.
    // Ohne den Rueckgriff verlaere die Zitation genau die Angabe, die einen
    // Beitrag erst auffindbar macht: "In <Werk> (S. x-y)".
    container: (art === "Buchkapitel" || art === "Konferenzbeitrag")
      ? (buchTitel || tagung || zeitschrift) : "",
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
  // Behoerden- und EU-Adressen nennen ihren Traeger nicht immer in den
  // Angaben. Die Domain sagt ihn eindeutig — das ist kein Raten, sondern die
  // Zuordnung, die auch ein Leser vornimmt.
  if (!q.authors.length && !q.publisher) {
    const traeger =
      /\.gv\.at$/i.test(u.hostname) ? "Republik Oesterreich"
      : /\.europa\.eu$/i.test(u.hostname) ? "Europaeische Union"
      : /\.bund\.de$|\.gesetze-im-internet\.de$/i.test(u.hostname) ? "Bundesrepublik Deutschland"
      : "";
    if (traeger) { q.publisher = traeger; q.corporateAuthor = true; }
  }
  if (!q.authors.length && !q.doi) {
    const koerper =
      (typeof ld.publisher === "object" && ld.publisher && ld.publisher.name) ||
      (typeof ld.publisher === "string" ? ld.publisher : "") ||
      // twitter:site taugt als Herausgeber, nicht als Verfasser — und das @
      // gehört nicht in eine Quellenangabe.
      erste("og:site_name", "dc.publisher", "publisher", "twitter:site");
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
  // Bisher blieb die Warnung leer, wenn keine Wand erkannt wurde und die Seite
  // trotzdem nicht reicht. Gemessen am 03.08.2026 traf das fuenf von zwanzig
  // Quellen, zwei davon mit gefuelltem Titel UND Verfasser — die Form, in der
  // ein aufrufendes Programm den Satz faelschlich als Treffer ablegt. Ein
  // Grund ist brauchbarer als ein Schweigen.
  if (!q.complete && !q.warning) {
    const fehlt = [
      !q.title && "a title",
      !(q.authors.length || q.publisher) && "an author or publisher",
      !q.year && "a year",
    ].filter(Boolean);
    q.warning = "The page answered in full but declares no complete citation: "
              + fehlt.join(" and ") + " is missing. Read this flag rather than the "
              + "title field — the details below are what the page says about itself, "
              + "not a reference.";
  }
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
    if (!istOeffentlich(ziel)) throw new Error("only public addresses can be read");

    // Weiterleitungen selbst verfolgen. Mit redirect:"follow" wird nur die
    // ZUERST genannte Adresse geprueft — eine oeffentliche Adresse, die auf
    // 127.0.0.1 weiterleitet, umgeht die Pruefung vollstaendig. Die Plattform
    // faengt das derzeit ab, aber darauf soll die Sicherheit nicht beruhen.
    let r = await holeMitPruefung(ziel);
    async function holeMitPruefung(start) {
      let adresse = start;
      for (let sprung = 0; sprung < 5; sprung++) {
        const antwort = await fetchRoh(adresse);
        if (![301, 302, 303, 307, 308].includes(antwort.status)) return antwort;
        const ort = antwort.headers.get("location");
        if (!ort) return antwort;
        let naechste;
        try { naechste = new URL(ort, adresse); } catch { return antwort; }
        if (!/^https?:$/.test(naechste.protocol) || !istOeffentlich(naechste)) {
          throw new Error("redirect target is not a public address");
        }
        adresse = naechste;
      }
      throw new Error("too many redirects");
    }
    function fetchRoh(adresse) {
      return fetch(adresse.href, {
      redirect: "manual",
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
    }
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
        nextStep: r.status === 403 || r.status === 503
          ? naechsterSchritt("network") : undefined,
      }, null, 2));
    }
    const typ = r.headers.get("content-type") || "";
    if (!/html|xml/i.test(typ)) {
      return textResult(JSON.stringify({
        url: r.url, contentType: typ,
        warning: "The address does not return an HTML page, so it declares no citation metadata.",
        nextStep: naechsterSchritt("not-html"),
      }, null, 2));
    }
    // Gedeckelt, damit eine einzelne riesige Seite den Aufruf nicht sprengt;
    // die Angaben stehen im Kopf, lange vor dieser Grenze.
    const html = (await r.text()).slice(0, 1500000);
    // Eine leere oder winzige Antwort ist keine Seite. EUR-Lex antwortet
    // serverseitigen Lesern mit HTTP 202 und null Bytes — ohne diese Pruefung
    // meldete das Werkzeug "nur der Seitenname steht da" und schob den Grund
    // damit der Seite zu, statt die Sperre zu benennen.
    if (html.trim().length < 500) {
      return textResult(JSON.stringify({
        url: r.url, httpStatus: r.status, bytes: html.length,
        warning: "The server returned an empty or near-empty response. That is a block, "
               + "not a page: nothing was declared and nothing could be read.",
        hint: "Open the page in a browser and capture it there.",
        nextStep: naechsterSchritt("wall"),
      }, null, 2));
    }
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
      // Nur wo der Satz nicht traegt. Bei einem vollstaendigen Datensatz gibt es
      // nichts vorzuschlagen, und ein Hinweis waere dort blosse Werbung.
      nextStep: q.complete ? undefined : naechsterSchritt("no-metadata"),
    }, null, 2));
  }

  if (name === "open_work") {
    // Die Aufgaben stehen dort, wo sie auch ein Mensch findet. Eine zweite,
    // handgepflegte Liste im Worker waere binnen einer Woche veraltet.
    const label = (args && args.label) || "";
    const u = "https://api.github.com/repos/Bubu89/full-page-pdf-snap/issues"
            + "?state=open&per_page=30" + (label ? "&labels=" + encodeURIComponent(label) : "");
    let aufgaben = [];
    try {
      const r = await fetch(u, {
        headers: { accept: "application/vnd.github+json", "user-agent": AGENT },
        cf: { cacheTtl: 300 },
      });
      if (r.ok) {
        aufgaben = (await r.json())
          .filter((i) => !i.pull_request)
          .map((i) => ({
            number: i.number,
            title: i.title,
            labels: (i.labels || []).map((l) => l.name),
            url: i.html_url,
            // Der Anfang des Rumpfs reicht, um zu entscheiden, ob die Aufgabe
            // passt. Wer sie annimmt, liest ohnehin das Ganze.
            excerpt: (i.body || "").slice(0, 400),
          }));
      }
    } catch (_) { /* kein Grund, den Aufruf scheitern zu lassen */ }

    return textResult(JSON.stringify({
      project: "provinglab.dev and the Full Page PDF Snap extension",
      repository: "https://github.com/Bubu89/full-page-pdf-snap",
      license: "MIT for the software, CC BY 4.0 for the measurements and data",
      read_first: {
        agents: SITE + "/AGENTS.md",
        why_it_matters: (
          "The site's whole claim is that every figure has a method, raw data and a "
          + "control run. A contribution that introduces a number without evidence does "
          + "more harm than no contribution — it is the one thing that cannot be fixed "
          + "later, because a figure once quoted travels on its own."),
      },
      open_tasks: aufgaben,
      tasks_url: "https://github.com/Bubu89/full-page-pdf-snap/issues",
      before_you_start: [
        "python3 rechtscheck.py — must report 0 errors; if it is already red, that is the finding",
        "node --test tests/*.mjs — must report 18/18",
        "python3 tools/links-pruefen.py — internal targets and store versions",
      ],
      house_rules: [
        "Every factual claim needs a source and a retrieval date, or it becomes an opinion, or it goes.",
        "Never state a third party's intent. '403 Forbidden' is an observation; 'they block deliberately' is not provable.",
        "A comparison the local tool only wins reads as advertising — name at least one category where the alternative is better.",
        "No result is a bug, not a zero. A measurement returning 0 of 20 is suspect before the world is.",
        "German for comments and internal docs, English for the published site.",
      ],
      most_valuable: (
        "Recounting a published figure and getting a different number. The raw data is "
        + "under /data/ precisely so that this is possible, and the limits section of each "
        + "measurement says where it is likely to differ."),
      done_when: [
        "rechtscheck.py reports 0 errors",
        "tests are green",
        "a new figure has its raw data under docs/data/",
        "CHANGELOG.md states what, why, how and with what result",
        "no local paths anywhere in the tracked tree — this repository is public",
      ],
    }, null, 2));
  }

  if (name === "how_to_capture") {
    const art = (args && args.agent) || "unknown";
    const brw = (args && args.browser) || "any";

    // Wege nach Browser. Die Bedingungen sind geprueft, nicht angenommen:
    // Edge fragt einmal nach Freigabe, Opera braucht eine eigene Bruecke, und
    // auf Android installiert Chrome ueberhaupt keine Erweiterungen.
    const install = {
      firefox: { url: CAPTURE.firefox, note: "One click. Works on desktop and on Android." },
      chrome:  { url: CAPTURE.chrome,  note: "One click. Needs Chrome 116 or newer." },
      edge:    { url: CAPTURE.chrome,  note: "Edge asks once to allow extensions from other stores, then installs normally." },
      brave:   { url: CAPTURE.chrome,  note: "Installs from the Chrome Web Store as it is." },
      vivaldi: { url: CAPTURE.chrome,  note: "Installs from the Chrome Web Store as it is." },
      opera:   { url: CAPTURE.chrome,  note: "Needs Opera's own 'Install Chrome Extensions' add-on first." },
      android: { url: CAPTURE.firefox, note: "Firefox only. Chrome for Android installs no extensions at all — measured: https://provinglab.dev/measurements/android-capture-extensions/" },
    };

    // Was fuer wen gilt. Die Trennlinie ist gemessen, nicht behauptet:
    // https://provinglab.dev/notes/what-an-agent-can-do-with-an-extension/
    const wege = {
      "input-events": {
        verdict: "You can drive the extension yourself.",
        why: "activeTab is granted by any event that reaches the browser's input layer. "
           + "Measured: tabs visible to the extension went from 0 to 1 after a synthetic "
           + "Alt+Shift+Y sent through X11 XTEST. The browser does not ask who produced it.",
        steps: [
          "Make sure the extension is installed in the profile you are driving (see install).",
          "Open the source in a tab and bring that window to the front.",
          "Send the command as a real input event: Alt+Shift+Y, or click the toolbar icon.",
          "The PDF lands in the browser's download folder, stamped with the source URL and "
            + "the time of retrieval, with an RIS record beside it.",
        ],
        caveat: "A click dispatched into page content is NOT such an event and will not work.",
      },
      "dom-only": {
        verdict: "You cannot trigger it — but you can still load it, and you may not need it.",
        why: "CDP and DOM events do not satisfy activeTab. Measured: the extension loads and "
           + "its service worker runs, then chrome.tabs.query returns every tab with an empty "
           + "url and title. It is running and blind, by design.",
        steps: [
          "Use extract_citation for the whole list first — half the work needs no browser.",
          "For what comes back, hand the user the addresses and the install link; their click "
            + "is the missing step, and it takes one.",
          "If you must stay in-process, add a layer that produces real input events "
            + "(see interoperability) or drive a browser the user is signed into.",
        ],
        caveat: "Do not imitate a browser user agent to get past a rule aimed at you. It does "
              + "not work on the measured cases and it is not something to build a citation on.",
      },
      "no-browser": {
        verdict: "Start here — and you may be finished here.",
        why: "10 of 20 mixed sources became complete citation records over plain HTTP in 8.1 s, "
           + "no account and no key: https://provinglab.dev/measurements/reading-list-to-bibliography/",
        steps: [
          "claude mcp add --transport http provinglab https://provinglab.dev/mcp",
          "Call extract_citation per URL and read the `complete` flag, never the title alone.",
          "Concatenate the `ris` fields into one file; import into Zotero or Citavi.",
          "Where complete is false, the reply carries nextStep with what a person must do.",
        ],
        caveat: "A record can carry a title and an author and still be complete:false.",
      },
      "human": {
        verdict: "One click, once.",
        why: "Installing is a user gesture by design — no store exposes an API for it, in "
           + "either browser. That friction is the security model, not an obstacle.",
        steps: [
          "Install from the store link for your browser (see install).",
          "Open the page you want to keep — logged in, behind the paywall you have access to.",
          "Press Alt+Shift+Y, or click the icon in the toolbar.",
          "Keep the PDF with your work: it carries the source URL and the retrieval date, "
            + "which is the date a web reference has to cite when the page declares none.",
        ],
        caveat: "It captures what you may already read. It is not a route past a licence.",
      },
    };

    const antwort = {
      tool: CAPTURE,
      install: brw === "any" ? install : { [brw]: install[brw] || install.chrome },
      route: art === "unknown" ? wege : { [art]: wege[art] },
      // Fuer Agenten, die ihren eigenen Browser fahren und die Erweiterung dort
      // laden wollen. Beide Fallen haben uns Zeit gekostet.
      loadIntoYourOwnBrowser: {
        chromium: 'launch_persistent_context(profile, headless=False, args=['
                + '"--headless=new", f"--disable-extensions-except={dir}", '
                + 'f"--load-extension={dir}"])',
        chrome150: "On Chrome 150 --load-extension loads nothing and reports nothing, and the "
                 + "flag that re-enabled it is gone. Use CDP instead: start with "
                 + "--remote-debugging-port and --enable-unsafe-extension-debugging, then send "
                 + "Extensions.loadUnpacked {path}. Verified on 150.0.7871.187.",
        serviceWorkerTrap: "Under Manifest V3 the service worker sleeps. An empty "
                 + "ctx.service_workers looks exactly like 'the extension did not load'. Read "
                 + "chrome://extensions via developerPrivate.getExtensionsInfo instead, or open "
                 + "the extension's popup.html once to wake it.",
        source: "https://github.com/Bubu89/full-page-pdf-snap",
      },
      // Fremde Projekte, die die fehlende Ebene liefern. Keine Empfehlung und
      // keine Pruefung ihrer Sicherheit — nur der Hinweis, wonach zu suchen ist.
      interoperability: {
        note: "Not endorsements and not audited here. Listed because they supply the input-event "
            + "layer that a DOM-only driver lacks. Check any of them yourself before use.",
        projects: [
          { name: "chrome-use", url: "https://github.com/leeguooooo/chrome-use",
            what: "points an agent at the Chrome you are already signed into, via extension and native messaging" },
          { name: "browser-agent-bridge", url: "https://github.com/TNJ2026/browser-agent-bridge",
            what: "exposes browser control to local agents through an extension and a Python native-messaging host" },
          { name: "openchrome", url: "https://github.com/shaun0927/openchrome",
            what: "MCP server controlling a real Chrome from any agent" },
          { name: "chrome-devtools-mcp", url: "https://github.com/ChromeDevTools/chrome-devtools-mcp",
            what: "official DevTools MCP — inspects and drives a live Chrome, DOM-level" },
          { name: "xdotool", url: "https://github.com/jordansissel/xdotool",
            what: "the X11 input-event tool; this is the layer that satisfies activeTab" },
        ],
      },
      evidence: {
        canAnAgentUseIt: SITE + "/notes/what-an-agent-can-do-with-an-extension/",
        whatComesBack: SITE + "/measurements/reading-list-to-bibliography/",
        whichSourcesNeedAPerson: SITE + "/notes/sources-a-machine-cannot-cite/",
        recipes: SITE + "/recipes/",
        permissions: SITE + "/measurements/pdf-extension-permissions/",
      },
      legal: "Capturing pages you are entitled to read is a copy for your own use. It is not a "
           + "way past a paywall or a licence you do not hold, and nothing here is legal advice.",
    };
    return textResult(JSON.stringify(antwort, null, 2));
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
