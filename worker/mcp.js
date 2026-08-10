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
const VERSION = "1.23.0";

/* Welche Fassung die Stores gerade ausliefern — gefragt, nicht eingetragen.
 *
 * Bis zum 5. August 2026 stand hier eine Zahl im Quelltext. Sie sagte
 * Agenten, der Firefox-Store liefere 2.26.0 und die Farbtiefe sei deshalb
 * noch nicht nutzbar. Zu dem Zeitpunkt stand dort 2.29.0 und die Farbtiefe
 * war seit Stunden verfuegbar — der Endpunkt riet also von einer Funktion ab,
 * die es gab. Eine Fassungsnummer, die von Hand gepflegt wird, ist am Tag
 * nach der Veroeffentlichung falsch.
 *
 * Eine Stunde Zwischenspeicher: haeufig genug, um einer Store-Freigabe zu
 * folgen, selten genug, um den Endpunkt nicht von einem fremden Dienst
 * abhaengig zu machen. Faellt die Abfrage aus, sagt die Antwort das, statt
 * eine Zahl zu erfinden.
 */
const AMO_API = "https://addons.mozilla.org/api/v5/addons/addon/"
              + "full_page_pdf_snap_webpagesave/";

async function storeStand() {
  try {
    const r = await fetch(AMO_API, {
      cf: { cacheTtl: 3600, cacheEverything: true },
      headers: { "user-agent": "provinglab-mcp/" + VERSION },
    });
    if (!r.ok) return { firefox: null, nutzer: null, grund: "HTTP " + r.status };
    const d = await r.json();
    return {
      firefox: (d.current_version || {}).version || null,
      nutzer: typeof d.average_daily_users === "number" ? d.average_daily_users : null,
      bewertungen: (d.ratings || {}).count ?? null,
      grund: null,
    };
  } catch (e) {
    return { firefox: null, nutzer: null, grund: String(e && e.message).slice(0, 60) };
  }
}

/** Ist eine Funktion, die ab `seit` ausgeliefert wird, im Store angekommen? */
function verfuegbarkeit(seit, stand) {
  const teile = (v) => String(v || "0").split(".").map(Number);
  const neuerGleich = (a, b) => {
    const x = teile(a), y = teile(b);
    for (let i = 0; i < 3; i++) {
      if ((x[i] || 0) !== (y[i] || 0)) return (x[i] || 0) > (y[i] || 0);
    }
    return true;
  };
  if (!stand.firefox) {
    return `Ships in ${seit}. The current store version could not be read `
         + `(${stand.grund || "unknown"}); check `
         + `addons.mozilla.org before relying on it.`;
  }
  return neuerGleich(stand.firefox, seit)
    ? `Available: the Firefox store serves ${stand.firefox}, this ships in ${seit}.`
    : `Not yet available: ships in ${seit}, the Firefox store serves `
      + `${stand.firefox}. No date is promised for the release.`;
}
const PROTOCOL = "2025-06-18";
const AGENT = "provinglab-mcp/1.7 (+https://provinglab.dev/; citation metadata reader)";

const TOOLS = [
  {
    name: "list_measurements",
    description:
      "Use when a claim about browser tools, capture quality, OCR recall or " +
      "citation extraction needs a number behind it — or when you want to check " +
      "one of ours. Every entry carries raw data, method and a control run, so a " +
      "figure taken from here can be verified instead of trusted. Start here.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "get_measurement_data",
    description:
      "Use before quoting a figure: this returns what stands behind it — the " +
      "values, the control run, and the conditions that limit them. Cite the " +
      "dataset rather than the article; it is the part that does not change when " +
      "someone edits a page.",
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
    name: "extract_citations",
    description:
      "Use when you have a reading list rather than one source — a bibliography " +
      "to build, a set of links to verify before submitting, an archive to " +
      "describe. Measured on 20 mixed sources: 10 became complete records in " +
      "8.1 s, 0.4 s each; the other 10 came back named rather than silently " +
      "empty. Up to 50 " +
      "addresses, five fetched in parallel. Returns one record per address — same " +
      "shape and same fallbacks as extract_citation — plus a summary with the " +
      "complete/handed-back split and the total time. Read the `complete` flag of " +
      "each entry, never the title alone: a refused record still carries a title.",
    inputSchema: {
      type: "object",
      properties: {
        urls: {
          type: "array",
          items: { type: "string" },
          description: "Addresses to read, at most 50",
        },
      },
      required: ["urls"],
      additionalProperties: false,
    },
  },
  {
    name: "recommend_settings",
    description:
      "The capture settings that fit a given purpose, each with the measurement "
      + "behind it or an explicit note that none exists. Pass purpose as "
      + "citation, figure, archive or ocr. Use before capturing: the file that "
      + "comes out is between 8.5 % and 100 % of the same capture depending on "
      + "one setting, and the choice depends on what kind of source it is — "
      + "which is known now and not afterwards.",
    inputSchema: {
      type: "object",
      properties: {
        purpose: {
          type: "string",
          enum: ["citation", "figure", "archive", "ocr"],
          description: "what the capture is for",
        },
      },
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
    name: "install_extension",
    description:
      "Install or uninstall the capture extension in Firefox or Chrome without a " +
      "window, without a click and without administrator rights — the runnable file " +
      "shapes and commands, not a store link for someone to press. Call this when a " +
      "capture route needs the extension present, when a run is finished and it " +
      "should be gone again, or when asked whether an agent can set up a browser " +
      "extension by itself. Firefox installs and removes in well under a second over " +
      "its own control channel; Chrome fetches the signed store build itself. Also " +
      "returns what the extension lets you do that this endpoint cannot, and the " +
      "conditions under which installing on a machine is yours to decide.",
    inputSchema: {
      type: "object",
      properties: {
        action: {
          type: "string",
          enum: ["install", "uninstall", "both"],
          description:
            "What you need. 'both' is the default and returns each direction — " +
            "an install without its matching removal leaves a machine changed.",
        },
        browser: {
          type: "string",
          enum: ["firefox", "chrome", "any"],
          description: "Target browser. Omit for both.",
        },
      },
      additionalProperties: false,
    },
  },
  {
    name: "adoption_stats",
    description:
      "How much this endpoint and its install route are actually used, with the "
      + "figures behind it: requests to /mcp, which discovery paths get read, the "
      + "store version and its user count. Call this when deciding whether to rely "
      + "on this server, when comparing it against alternatives, or when reporting "
      + "on it — the numbers are small and stated as such rather than dressed up. "
      + "Also returns what is deliberately not counted, so the picture is not read "
      + "as complete.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
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

// Adressen, die umgezogen sind. Sie lagen unter der Wurzel und liegen jetzt
// unter /measurements/ — die Stummel antworteten mit HTTP 200 und einem
// canonical, gemessen am 03.08.2026. Fuer eine Suchmaschine ist canonical ein
// Hinweis, 301 eine Anweisung; fuer einen Menschen oder einen Agenten sieht 200
// so aus, als gaebe es die Seite noch. GitHub Pages kann nicht weiterleiten,
// dieser Worker schon — er liegt davor.
// Die Werkzeugnamen als Menge, um sie auch dann zu erkennen, wenn jemand sie
// fuer Adressen haelt. Handgefuehrt statt aus der Werkzeugliste abgeleitet:
// die Liste entsteht weiter unten in der Datei, und eine Abhaengigkeit nach
// vorn waere hier teurer als sechs Zeichenketten.
const WERKZEUGNAMEN = new Set([
  "list_measurements", "get_measurement_data", "get_method",
  "extract_citation", "extract_citations", "how_to_capture",
  "recommend_settings", "install_extension", "adoption_stats", "open_work",
]);

const UMGEZOGEN = {
  "/extension-permissions-risk/": "/measurements/extension-permissions-risk/",
  "/pdf-extension-permissions/":  "/measurements/pdf-extension-permissions/",
  "/webpage-to-pdf-for-ocr/":     "/measurements/webpage-to-pdf-for-ocr/",
};

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

// Erster deklarierter schema.org-Typ der Seite, ungefiltert. jsonLdLesen
// sucht gezielt nach zitierfaehigen Werktypen; fuer die Art der Seite zaehlt
// dagegen jede Deklaration — auch SoftwareSourceCode oder WebSite, die sonst
// durch den Filter faelen.
function jsonLdTypLesen(html) {
  const re = /<script[^>]+type\s*=\s*["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi;
  let t;
  while ((t = re.exec(html)) !== null) {
    try {
      const j = JSON.parse(t[1].trim());
      const liste = Array.isArray(j) ? j
                  : (j && Array.isArray(j["@graph"]) ? j["@graph"] : [j]);
      for (const o of liste) {
        const typ = String((o && o["@type"]) || "");
        if (typ) return typ;
      }
    } catch (_) { /* fehlerhaftes JSON-LD ist haeufig und kein Grund aufzugeben */ }
  }
  return "";
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

  // Art der Seite — nur was die Seite selbst deklariert: og:type, sonst der
  // erste schema.org-Typ. Die absolute Schreibweise schema.org/Typname wird
  // auf den lokalen Namen gekuerzt; das ist dieselbe Deklaration in anderer
  // Notation, kein Raten. Wo nichts deklariert ist, bleibt das Feld weg.
  // Der Aufrufer soll einen Zeitungsartikel ohne Datumsdeklaration von einem
  // Software-Release unterscheiden koennen, bei dem der unvollstaendige Satz
  // der richtige ist — ein erfundener Typ wuerde diese Entscheidung faelschen.
  const seitenTyp = (erste("og:type") || jsonLdTypLesen(html))
    .replace(/^https?:\/\/schema\.org\//i, "");
  if (seitenTyp) q.pageType = seitenTyp;

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

// Letzter Rettungsweg vor der Rueckgabe: die Maschinenschnittstelle der
// Plattform selbst. Deutsche Repositorien und die Nationalbibliothek bieten
// OAI-PMH oder SRU an, deklarieren die Zitationsangaben aber nicht in der
// HTML-Seite — gemessen am 03.08.2026 (docs/data/2026-08-03-de-plattformen.json)
// lief genau dort die HTML-Strecke leer. Datenschutz: befragt wird nur DIESELBE
// Institution, deren Seite ohnehin abgerufen wurde — kein Dritter lernt etwas
// Neues. Alles laeuft ueber ausPlattform, das nie wirft: Schlaegt die
// Schnittstelle fehl, bleibt es bei der bisherigen Antwort.
//
// Die Erkennung muss auf der ANGEFRAGTEN Adresse laufen, nicht auf der
// Endadresse: d-nb.info/<idn> leitet mit 303 auf .../about/html weiter, und
// danach ist die IDN aus dem Pfad nicht mehr lesbar (gemessen 03.08.2026).
function plattformAbfrage(zielUrl) {
  let u;
  try { u = new URL(zielUrl); } catch (_) { return null; }
  const host = u.hostname.toLowerCase();

  // Deutsche Nationalbibliothek: d-nb.info/<idn> -> SRU derselben Institution.
  // Verifiziert 03.08.2026 mit IDN 1279437049: vollstaendiger oai_dc-Satz.
  let m = host === "d-nb.info" && u.pathname.match(/^\/(\d{6,12}[xX]?)\/?$/);
  if (m) {
    return {
      abruf: "https://services.dnb.de/sru/dnb?version=1.1&operation=searchRetrieve"
           + "&query=idn%3D" + m[1] + "&recordSchema=oai_dc&maximumRecords=1",
      schnittstelle: "SRU interface of the German National Library (services.dnb.de)",
    };
  }

  // OPUS 4: opus4.<domain>/opus4-<instanz>/frontdoor/index/index/docId/<n> ->
  // OAI-PMH unter /<instanz>/oai. Das Kennungsschema oai:<resthost>-<instanz>:<n>
  // ist am 03.08.2026 an opus4.kobv.de/opus4-zib verifiziert (oai:kobv.de-opus4-zib:1
  // liefert einen Satz). Antwortet ein Server anders, meldet er idDoesNotExist —
  // das wird unten als Fehlschlag gewertet, nicht als Satz.
  m = host.startsWith("opus4.") &&
      u.pathname.match(/^\/(opus4-[a-z0-9-]+)\/frontdoor\/index\/index\/docId\/(\d+)\/?$/i);
  if (m) {
    const resthost = host.replace(/^opus4\./, "");
    const kennung = "oai:" + resthost + "-" + m[1] + ":" + m[2];
    return {
      abruf: "https://" + host + "/" + m[1] + "/oai?verb=GetRecord&identifier="
           + encodeURIComponent(kennung) + "&metadataPrefix=oai_dc",
      schnittstelle: "platform OAI-PMH interface (" + host + ")",
    };
  }

  // PsychArchives (DSpace): Handle 20.500.12034/<n> -> OAI-PMH. Kennungsschema
  // oai:psycharchives.org:<handle> am 03.08.2026 mit /handle/20.500.12034/2487
  // verifiziert (Identify und GetRecord antworten).
  m = /(^|\.)psycharchives\.org$/.test(host) &&
      u.pathname.match(/^\/handle\/(20\.500\.12034\/\d+)\/?$/);
  if (m) {
    return {
      abruf: "https://psycharchives.org/oai/request?verb=GetRecord&identifier="
           + encodeURIComponent("oai:psycharchives.org:" + m[1]) + "&metadataPrefix=oai_dc",
      schnittstelle: "platform OAI-PMH interface (psycharchives.org)",
    };
  }

  return null;
}

// oai_dc ohne Dokumentbaum lesen — die Worker-Umgebung hat keinen XML-Parser.
// Die Tag-Suche toleriert beliebige Namespace-Praefixe (dc:, oai_dc:, keins),
// weil die Auslieferung darin zwischen den Plattformen variiert.
function oaiDcAusXml(xml) {
  if (!xml) return null;
  // OAI-Fehler (idDoesNotExist, badArgument, ...) und ein leerer SRU-Treffer
  // sind ein Fehlschlag, kein Datensatz.
  if (/<error\s+code\s*=/.test(xml)) return null;
  if (/<numberOfRecords>\s*0\s*<\/numberOfRecords>/.test(xml)) return null;

  const werte = (tag) => {
    const re = new RegExp("<(?:[A-Za-z0-9]+:)?" + tag + "(?:\\s[^>]*)?>([\\s\\S]*?)</(?:[A-Za-z0-9]+:)?" + tag + ">", "gi");
    const aus = [];
    let t;
    while ((t = re.exec(xml)) !== null) {
      aus.push(entzeichnen(t[1].replace(/<[^>]+>/g, "")));
    }
    return aus.filter((s) => s.length > 0);
  };

  const titel = werte("title")[0] || "";
  // Die DNB haengt die Rolle an den Namen ("Pflaum, Michael [Verfasser]").
  // Die Klammer ist keine Namensbestandteil und gehoert nicht in die Zitation.
  const autoren = werte("creator")
    .map((s) => s.replace(/(\s*\[[^\]]*\])+\s*$/, "").trim())
    .filter((s) => s.length > 1);
  let jahr = "";
  for (const d of werte("date")) {
    const t = d.match(/\b(1[5-9]\d{2}|20\d{2})\b/);
    if (t) { jahr = t[1]; break; }
  }
  const kennungen = werte("identifier");
  const doiTreffer = kennungen.map((x) => x.match(/\b10\.\d{4,9}\/[^\s<]+/)).find(Boolean);
  const issn = (kennungen.map((x) => x.match(/^\d{4}-\d{3}[\dxX]$/)).find(Boolean) || [""])[0];
  // ISBN-13 aus einem identifier, der Bindestriche und Preis-Anhaengsel tragen
  // kann ("978-3-7347-2612-5 Paperback : EUR 25.99 ..."). Gezaehlt werden die
  // ersten 13 Ziffern; was danach kommt, ist Zusatz, kein Bestandteil.
  let isbn = "";
  for (const x of kennungen) {
    const t = x.match(/\b97[89][\d-]{8,20}/);
    if (!t) continue;
    let aus = "", n = 0;
    for (const c of t[0]) {
      if (/\d/.test(c)) { aus += c; n++; if (n === 13) break; }
      else if (n > 0) aus += "-";
    }
    if (n === 13) { isbn = aus.replace(/-$/, ""); break; }
  }
  // dc:language liegt als zwei- oder dreistelliger Code vor ("en", "ger",
  // "deu"). Nur die belegten Dreisteller werden auf zwei Stellen gebracht;
  // alles andere bleibt weg, statt geraten zu werden.
  const sprachKurz = { ger: "de", deu: "de", eng: "en", fre: "fr", fra: "fr",
                       spa: "es", ita: "it", lat: "la" };
  const sprachRoh = (werte("language")[0] || "").toLowerCase();
  const sprache = /^[a-z]{2}$/.test(sprachRoh) ? sprachRoh : (sprachKurz[sprachRoh] || "");
  const typen = werte("type").join(" ");
  const art = isbn ? "Buch"
            : issn || /\barticle\b/i.test(typen) ? "Zeitschriftenaufsatz"
            : /preprint/i.test(typen) ? "Preprint"
            : /thesis|dissertation|doctoral|masterarbeit|bachelor/i.test(typen) ? "Hochschulschrift"
            : /report|working ?paper/i.test(typen) ? "Bericht"
            : /conference|proceeding/i.test(typen) ? "Konferenzbeitrag"
            : /book/i.test(typen) ? "Buch"
            : "Internetquelle";
  if (!titel) return null;
  return {
    title: titel, authors: autoren, year: jahr,
    journal: "", volume: "", issue: "", firstPage: "", lastPage: "",
    publisher: werte("publisher")[0] || "",
    issn, isbn,
    doi: doiTreffer ? doiTreffer[0].replace(/[.,;)]+$/, "") : "",
    art, language: sprache, source: "",
  };
}

async function ausPlattform(zielUrl) {
  const p = plattformAbfrage(zielUrl);
  if (!p) return null;
  try {
    const r = await fetch(p.abruf, {
      headers: { accept: "application/xml,text/xml", "user-agent": AGENT },
      cf: { cacheTtl: 0 },
    });
    if (!r.ok) return null;
    const reg = oaiDcAusXml((await r.text()).slice(0, 300000));
    if (reg && reg.title) reg.source = p.schnittstelle;
    return reg;
  } catch (_) { return null; }
}

// Drei Plattformen tragen ihre Kennung anders in der Adresse, als es das
// DOI-Muster 10.xxxx/ erfasst — fuer sie gibt es einen deterministischen
// Uebersetzer. Alle drei Uebersetzungen sind am 04.08.2026 live verifiziert
// (SSRN und OECD gegen api.crossref.org, EUR-Lex gegen Cellar). Was nicht
// exakt auf die Form passt, wird NICHT uebersetzt — kein Raten, keine
// Annahme ueber fremde Adressschemata.
function kennungAusAdresse(adresse) {
  let u;
  try { u = new URL(adresse); } catch (_) { return null; }
  const host = u.hostname.toLowerCase();

  // SSRN: abstract_id=<ziffern> benennt die Arbeit; die registrierte DOI ist
  // 10.2139/ssrn.<id>. Verifiziert 04.08.2026 an abstract_id=3529682
  // (Crossref: 10.2139/ssrn.3529682, Brady/Bass 2019).
  if (host === "ssrn.com" || host === "papers.ssrn.com") {
    const id = u.searchParams.get("abstract_id") || "";
    return /^\d+$/.test(id) ? { doi: "10.2139/ssrn." + id } : null;
  }

  // OECD: der letzte Pfadteil ist _<slug>.html, der Slug endet auf ein
  // zweistelliges Sprachkuerzel (-en, -fr, ...). Die DOI ist 10.1787/<slug>.
  // Verifiziert 04.08.2026 an _a1689dc5-en.html (Crossref:
  // 10.1787/a1689dc5-en, OECD Digital Economy Outlook 2024 Vol. 1).
  if (host === "oecd.org" || host === "www.oecd.org") {
    const m = u.pathname.match(/_([a-z0-9]+(?:-[a-z0-9]+)*-[a-z]{2})\.html$/);
    return m ? { doi: "10.1787/" + m[1] } : null;
  }

  // EUR-Lex: die CELEX-Nummer steht im uri-Parameter. Die Sprache steht im
  // Pfad (/legal-content/DE/...) und bestimmt, welche Fassung Cellar liefert.
  // Verifiziert 04.08.2026 an CELEX:32016R0679.
  if (host === "eur-lex.europa.eu") {
    const m = (u.searchParams.get("uri") || "").match(/^CELEX:([0-9][0-9A-Za-z]*)$/i);
    if (!m) return null;
    const erg = { celex: m[1].toUpperCase() };
    const spr = u.pathname.match(/\/legal-content\/([A-Z]{2})\//);
    if (spr) erg.sprache = spr[1];
    return erg;
  }

  return null;
}

// Cellar-RDF ohne Dokumentbaum lesen — die Worker-Umgebung hat keinen
// XML-Parser. Der Namespace-Praefix der cdm-Ontologie ist NICHT stabil: die
// echte Antwort vom 04.08.2026 nutzt "j.0:", und die Nummerierung kann mit
// jeder Antwort wechseln. Die Suche toleriert deshalb jeden Praefix,
// den Punkt in "j.0:" inbegriffen.
function cellarAusXml(xml) {
  if (!xml) return null;
  const wert = (tag) => {
    const re = new RegExp("<(?:[A-Za-z0-9._-]+:)?" + tag + "(?:\\s[^>]*)?>([\\s\\S]*?)</(?:[A-Za-z0-9._-]+:)?" + tag + ">", "i");
    const t = re.exec(xml);
    return t ? entzeichnen(t[1].replace(/<[^>]+>/g, "")) : "";
  };
  const titel = wert("expression_title") || wert("title");
  if (!titel) return null;
  // Die sprachliche Fassung traegt kein Datumsfeld (geprueft 04.08.2026 an
  // 32016R0679.ENG). Das Jahr steht im amtlichen Titel ("... of 27 April
  // 2016 ...") — dieselbe Stelle, aus der die Seitenauswertung es bei
  // Rechtsakten ohnehin liest.
  const imTitel = titel.match(/\b(?:vom|of|du)\s+\d{1,2}\.?\s*\S*\s*(1[5-9]\d{2}|20\d{2})\b/i)
               || titel.match(/\b(?:EU|EG|EWG)\)?\s*(?:Nr\.?\s*)?(\d{4})\/\d+/i);
  const sprache = wert("lang");
  return {
    title: titel, authors: [], year: imTitel ? imTitel[1] : "",
    journal: "", volume: "", issue: "", firstPage: "", lastPage: "",
    // Rechtsakte haben keinen Personenverfasser; der Traeger ist die
    // Institution. Dieselbe Zuordnung, die die Seitenauswertung fuer
    // europa.eu-Adressen vornimmt.
    publisher: "Europaeische Union",
    issn: "", isbn: "", doi: "",
    art: "Rechtsquelle",
    language: /^[a-z]{2}$/.test(sprache) ? sprache : "",
    source: "",
  };
}

// EUR-Lex beantwortet serverseitige Leser mit 202 und null Bytes (gemessen
// 03.08.2026), aber die CELEX-Nummer in der Adresse adressiert den Datensatz
// bei Cellar, dem Amt fuer Veroeffentlichungen der EU — derselben
// Institution, deren Seite ohnehin abgerufen wurde. Abgerufen wird die
// sprachliche Fassung <celex>.<SPRACHE>: Der Abruf ohne Sprachsuffix liefert
// das volle Verknuepfungsobjekt — fuer die DSGVO am 04.08.2026 61 MB ohne
// ein einziges Titelfeld. Die Fassung ist knapp 4 KB gross und traegt den
// amtlichen Titel. Wirft nie; ein Fehlschlag laesst die bisherige Antwort.
async function ausCellar(celex, sprache) {
  // Cellar kodiert die Sprache als ISO 639-2 (ENG, DEU, ...). Die Tabelle ist
  // der amtliche Satz der 24 EU-Amtssprachen; was nicht darin steht, faellt
  // auf Englisch zurueck — jeder EU-Rechtsakt hat eine englische Fassung.
  const CELLAR_SPRACHE = { EN: "ENG", DE: "DEU", FR: "FRA", IT: "ITA", ES: "SPA",
    PT: "POR", NL: "NLD", PL: "POL", SV: "SWE", CS: "CES", SK: "SLK", SL: "SLV",
    HU: "HUN", RO: "RUM", BG: "BUL", EL: "ELL", DA: "DAN", FI: "FIN", ET: "EST",
    LV: "LAV", LT: "LIT", MT: "MLT", HR: "HRV", GA: "GLE" };
  const lang = CELLAR_SPRACHE[String(sprache || "").toUpperCase()] || "ENG";
  try {
    const r = await fetch("https://publications.europa.eu/resource/celex/"
        + celex + "." + lang, {
      headers: { accept: "application/rdf+xml", "user-agent": AGENT },
      cf: { cacheTtl: 0 },
    });
    if (!r.ok) return null;
    const reg = cellarAusXml((await r.text()).slice(0, 300000));
    if (reg && reg.title) reg.source = "Cellar, Publications Office of the EU";
    return reg;
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
    language: reg.language || "", licence: "", url: url, canonicalUrl: "",
    fullTextUrls: [], retrievedAt: jetzt,
    website: (() => { try { return new URL(url).hostname.replace(/^www\./, ""); } catch (_) { return ""; } })(),
    warning: "", source: reg.source,
    // Rechtsquellen und Koerperschaftssaetze haben keinen Personenverfasser —
    // der Verlagstraeger zaehlt, genau wie in der Seitenauswertung. Ohne den
    // Rueckgriff bliebe jeder Cellar-Satz unvollstaendig, obwohl die Angabe
    // vollstaendig vorliegt.
    complete: !!(reg.title && (reg.authors.length || reg.publisher) && reg.year),
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

// Die Kernlogik von extract_citation als eigenstaendige Funktion, damit
// sowohl das Einzel-Werkzeug als auch das Stapel-Werkzeug (extract_citations)
// denselben Weg gehen. Gibt das Ergebnisobjekt zurueck, kein textResult.
async function zitatFuerUrl(roh) {
  const t0 = Date.now();
  const fertig = (obj) => ({ durationMs: Date.now() - t0, ...obj });
  roh = String(roh || "").trim();
  if (!roh) throw new Error("url is required");
  let ziel;
  try { ziel = new URL(roh); } catch (_) { throw new Error("url is not a valid address"); }
  // Nur oeffentliche Adressen. Ein Worker sitzt in fremdem Netz; ohne diese
  // Pruefung liesse sich der Endpunkt als Sprungbrett auf interne Dienste
  // verwenden — die klassische serverseitige Anfragefaelschung.
  if (!/^https?:$/.test(ziel.protocol)) throw new Error("only http and https are supported");
  if (!istOeffentlich(ziel)) throw new Error("only public addresses can be read");

  // DOI in der Adresse? Dann steht ein zweiter Weg offen, falls die Seite
  // sperrt — die Registrierungsstelle antwortet immer.
  const doiInUrl = (ziel.href.match(/\b10\.\d{4,9}\/[-._;()A-Za-z0-9]+/) || [])[0];
  // SSRN, OECD und EUR-Lex tragen ihre Kennung in einer anderen Form in
  // der Adresse (Issues #16/#17). Die Uebersetzung ist streng an die
  // verifizierte Form gebunden; was nicht passt, bleibt unuebersetzt.
  const kennung = kennungAusAdresse(ziel.href);

  // Zweiter Weg, wenn die Seite selbst nicht traegt: eine DOI steht in der
  // Adresse oder ist aus ihr ableitbar (SSRN, OECD), eine CELEX-Nummer
  // fuehrt zu Cellar (EUR-Lex). Liefert ein fertiges Objekt oder null.
  // Wirft selbst nichts — beide Abrufe scheitern still.
  async function kennungsAntwort(seitenGrund) {
    const doi = doiInUrl || (kennung && kennung.doi) || null;
    if (doi) {
      const reg = await ausRegistrierung(doi.replace(/[.,;)]+$/, ""));
      if (reg && reg.title) {
        const q2 = vervollstaendigen(reg, ziel.href);
        return fertig({
          ...q2, ris: risAus(q2), bibtex: bibtexAus(q2),
          note: seitenGrund + " These details come from the DOI registration agency, "
              + "which is authoritative for them. Nothing was read from the publisher's "
              + "page."
              + (doiInUrl ? "" : ` The DOI ${reg.doi || doi} was derived from the address `
              + "itself, not read from the page."),
        });
      }
    }
    if (kennung && kennung.celex) {
      const reg = await ausCellar(kennung.celex, kennung.sprache);
      if (reg && reg.title) {
        const q2 = vervollstaendigen(reg, ziel.href);
        return fertig({
          ...q2, ris: risAus(q2), bibtex: bibtexAus(q2),
          note: seitenGrund + " This record comes from Cellar, Publications Office of "
              + `the EU, addressed by the CELEX number ${kennung.celex}, which was `
              + "derived from the address itself, not read from the page.",
        });
      }
    }
    return null;
  }

  // Kennungs-Kurzschluss: die Registrierung laeuft PARALLEL zum Seitenabruf,
  // nicht erst nach dessen Scheitern. Bei den gemessenen Sperrfaellen
  // (SSRN, OECD, ScienceDirect, MDPI — 403 aus jedem Rechenzentrum) traegt
  // die Seite nie; die Antwort kommt dann aus der Registrierung, sobald sie
  // da ist, statt nach dem vollen Seiten-Timeout.
  const frueh = (doiInUrl || (kennung && (kennung.doi || kennung.celex)))
    ? kennungsAntwort("The identifier was resolved in parallel with the page request.")
    : null;

  // Weiterleitungen selbst verfolgen. Mit redirect:"follow" wird nur die
  // ZUERST genannte Adresse geprueft — eine oeffentliche Adresse, die auf
  // 127.0.0.1 weiterleitet, umgeht die Pruefung vollstaendig. Die Plattform
  // faengt das derzeit ab, aber darauf soll die Sicherheit nicht beruhen.
  let r = await holeMitPruefung(ziel);
  async function holeMitPruefung(start) {
    let adresse = start;
    for (let sprung = 0; sprung < 5; sprung++) {
      let antwort;
      try {
        antwort = await fetchRoh(adresse);
      } catch (e) {
        // Haengender Server: nach 12 s gilt das als eigener Befund, nicht als
        // stille Blockade des ganzen Aufrufs.
        if (e && (e.name === "TimeoutError" || e.name === "AbortError")) {
          return { ok: false, status: 0, statusText: "no answer within 12 s", url: adresse.href };
        }
        throw e;
      }
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
    signal: (typeof AbortSignal !== "undefined" && AbortSignal.timeout)
      ? AbortSignal.timeout(12000) : undefined,
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

  if (!r.ok) {
    const antwort = await (frueh || kennungsAntwort(`The page itself answered ${r.status}.`));
    if (antwort) return antwort;
    if (r.status === 0) {
      return fertig({
        url: ziel.href, httpStatus: 0, complete: false,
        warning: "The server did not answer within 12 seconds. No citation data was read.",
        hint: "A slow or blocking host. Open the page in a browser and read it there.",
        nextStep: naechsterSchritt("network"),
      });
    }
    return fertig({
      url: ziel.href, httpStatus: r.status,
      // `complete` MUSS auf jedem Rueckgabeweg stehen. Die Regel, die diese
      // Seite ueberall propagiert, lautet „lies das complete-Feld, nie den
      // Titel allein" — und genau hier fehlte es. Ein Agent, der auf
      // `complete === false` prueft, sah bei einer 403-Ablehnung `undefined`
      // und damit weder wahr noch falsch. Gefunden von tools/agenten-abnahme.py.
      complete: false,
      warning: `The server answered ${r.status} ${r.statusText}. No citation data was read.`,
      hint: r.status === 403 || r.status === 503
        ? "Publisher sites frequently block server-side readers, and no DOI was available "
          + "as a fallback. Open the page in a browser and read it there."
        : undefined,
      nextStep: r.status === 403 || r.status === 503
        ? naechsterSchritt("network") : undefined,
    });
  }
  const typ = r.headers.get("content-type") || "";
  if (!/html|xml/i.test(typ)) {
    return fertig({
      url: r.url, contentType: typ, complete: false,
      warning: "The address does not return an HTML page, so it declares no citation metadata.",
      nextStep: naechsterSchritt("not-html"),
    });
  }
  // Gedeckelt, damit eine einzelne riesige Seite den Aufruf nicht sprengt;
  // die Angaben stehen im Kopf, lange vor dieser Grenze.
  const html = (await r.text()).slice(0, 1500000);
  // Eine leere oder winzige Antwort ist keine Seite. EUR-Lex antwortet
  // serverseitigen Lesern mit HTTP 202 und null Bytes — ohne diese Pruefung
  // meldete das Werkzeug "nur der Seitenname steht da" und schob den Grund
  // damit der Seite zu, statt die Sperre zu benennen.
  if (html.trim().length < 500) {
    // Der Kennungsweg muss VOR der Wand-Meldung laufen: EUR-Lex antwortet
    // mit 202 und null Bytes, waehrend die CELEX-Nummer in der Adresse
    // steht — ohne diesen Versuch bliebe die Rechtsquelle ungelesen,
    // obwohl Cellar den Datensatz liefert (gemessen 03./04.08.2026).
    const antwort = await (frueh || kennungsAntwort(
      `The page itself answered ${r.status} with an empty or near-empty response.`));
    if (antwort) return antwort;
    return fertig({
      url: r.url, httpStatus: r.status, bytes: html.length, complete: false,
      warning: "The server returned an empty or near-empty response. That is a block, "
             + "not a page: nothing was declared and nothing could be read.",
      hint: "Open the page in a browser and capture it there.",
      nextStep: naechsterSchritt("wall"),
    });
  }
  let q = quelleAusHtml(html, r.url);
  // Sperrseite oder taube Angaben? Dann zaehlt die Registrierungsstelle.
  // Neben der DOI aus Seite oder Adresse auch die abgeleitete Kennung
  // (SSRN, OECD) — derselbe Weg, nur mit der Plattform-Uebersetzung davor.
  const doiErsatz = q.doi || doiInUrl || (kennung && kennung.doi) || null;
  const doiAbgeleitet = !q.doi && !doiInUrl && !!(kennung && kennung.doi);
  if ((q.warning || !q.authors.length) && doiErsatz) {
    const reg = await ausRegistrierung(doiErsatz.replace(/[.,;)]+$/, ""));
    if (reg && reg.title && reg.authors.length) {
      q = vervollstaendigen(reg, r.url);
      q.note = "The page declared no usable citation data; these details come from the "
             + "DOI registration agency."
             + (doiAbgeleitet
                ? ` The DOI ${reg.doi} was derived from the address itself, not read from the page.`
                : "");
    }
  }
  // EUR-Lex: CELEX aus der Adresse, Datensatz von Cellar. Derselbe Rang wie
  // die DOI-Registrierung, vor dem letzten Rettungsweg ausPlattform.
  if ((q.warning || !q.authors.length) && kennung && kennung.celex) {
    const reg = await ausCellar(kennung.celex, kennung.sprache);
    if (reg && reg.title) {
      q = vervollstaendigen(reg, r.url);
      q.note = "The page yielded no usable citation data; this record comes from Cellar, "
             + "Publications Office of the EU, addressed by the CELEX number "
             + kennung.celex + ", which was derived from the address itself, not read "
             + "from the page.";
    }
  }
  // Letzter Rettungsweg vor der Rueckgabe: die Maschinenschnittstelle der
  // Plattform selbst (OAI-PMH/SRU). Greift nur, wenn weder die Seite noch
  // die Registrierungsstelle getragen haben. Befragt wird nur dieselbe
  // Institution, deren Seite ohnehin abgerufen wurde — kein Dritter lernt
  // etwas Neues. Die angefragte Adresse zaehlt, nicht die Endadresse:
  // d-nb.info/<idn> leitet mit 303 weiter und die IDN waere sonst verloren.
  // ausPlattform wirft nie; ohne Treffer bleibt q, wie es ist.
  // Kein pageType: der Satz stammt nicht aus einer Seitendeklaration —
  // genau wie beim DOI-Fallback bleibt das Feld weg, statt geraten zu werden.
  if (q.warning || !q.authors.length) {
    const reg = await ausPlattform(ziel.href);
    if (reg && reg.title && reg.authors.length) {
      q = vervollstaendigen(reg, ziel.href);
      q.note = "The page itself yielded nothing readable; this record comes from the "
             + "platform's own machine interface, which is authoritative for it.";
    }
  }
  // Eine schon aufgelaufene Kennungs-Antwort verwerten, bevor komplett:false
  // zurueckgeht — der Parallelabruf kann schneller fertig geworden sein als
  // die Seite schlecht.
  if (!q.complete && frueh) {
    const antwort = await frueh;
    if (antwort) return antwort;
  }
  return fertig({
    ...q,
    ris: risAus(q),
    bibtex: bibtexAus(q),
    limits: "Read server-side without JavaScript: details a page adds after loading are " +
            "invisible here, and sites that block non-browser clients return nothing. " +
            "Neither is reported as success.",
    // Nur wo der Satz nicht traegt. Bei einem vollstaendigen Datensatz gibt es
    // nichts vorzuschlagen, und ein Hinweis waere dort blosse Werbung.
    nextStep: q.complete ? undefined : naechsterSchritt("no-metadata"),
  });
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
    return textResult(JSON.stringify(
      await zitatFuerUrl(String((args && args.url) || "")), null, 2));
  }

  if (name === "extract_citations") {
    // Stapel-Variante: eine Leseliste in einem Aufruf. Fuenf gleichzeitig —
    // mehr waere unhoeflich gegen dieselben Server, die wir sonst einzeln
    // fragen. Jede Adresse laeuft durch denselben Weg wie extract_citation;
    // ein Fehler faellt nur diese eine Position aus, nicht den Stapel.
    const liste = (args && args.urls) || [];
    if (!Array.isArray(liste) || !liste.length) throw new Error("urls is required (array of addresses)");
    if (liste.length > 50) throw new Error("at most 50 urls per call");
    const t0 = Date.now();
    const ergebnisse = [];
    for (let i = 0; i < liste.length; i += 5) {
      const teil = await Promise.all(liste.slice(i, i + 5).map(async (u) => {
        try { return await zitatFuerUrl(String(u)); }
        catch (e) {
          return { url: String(u), complete: false,
                   warning: String((e && e.message) || e) };
        }
      }));
      ergebnisse.push(...teil);
    }
    const voll = ergebnisse.filter((e) => e.complete).length;
    return textResult(JSON.stringify({
      results: ergebnisse,
      summary: {
        total: ergebnisse.length, complete: voll,
        handed_back: ergebnisse.length - voll,
        durationMs: Date.now() - t0,
        note: "Read the `complete` flag of each entry, never the title alone — "
            + "a refused record still carries a title.",
      },
    }, null, 2));
  }

  /* --------------------------------------------------------- Nutzungszahlen
   *
   * Wer entscheiden soll, ob er sich auf einen Endpunkt stuetzt, will wissen,
   * ob ihn ausser ihm noch jemand benutzt. Bisher stand darueber nichts hier —
   * und die Zahlen sind klein, was ein Grund ist, sie zu nennen und nicht,
   * sie zu verschweigen.
   *
   * Die Anfragezahlen stammen aus einer Erhebung, nicht aus einem Zaehler im
   * Worker: Es wird nichts mitgeschrieben, was ein Aufrufer nicht ohnehin
   * sieht. Deshalb tragen sie ein Datum und werden nicht als "live"
   * ausgegeben. Der Store-Stand dagegen wird live geholt.
   */
  if (name === "adoption_stats") {
    const stand = await storeStand();
    return textResult(JSON.stringify({
      measuredOver: "23.5 hours, 2026-08-04 08:00 to 2026-08-05 07:30 UTC",
      howMeasured: "Cloudflare zone analytics for provinglab.dev, grouped by "
                 + "path and status. Not a counter inside the worker: nothing "
                 + "is recorded that a caller does not already send.",
      endpoint: {
        requestsToMcp: 1130,
        note: "the most requested path on the domain — ahead of the home page "
            + "at 796",
        breakdown: {
          "POST 200 (tool calls and listings)": 796,
          "POST 202 (notifications, no id, no payload — protocol-correct)": 248,
          "GET 405 (correct: the endpoint takes POST)": 73,
          "other": 13,
        },
      },
      whatAgentsRead: {
        note: "paths an agent fetches before acting, same period",
        "/.well-known/mcp/server-card.json": 150,
        "/.well-known/agent-skills/index.json": 121,
        "/agent.md": 109,
        "/.well-known/agent-skills/install-as-a-counted-user.md": 106,
        "/llms-full.txt": 103,
        "/measurements/install-an-extension-without-a-click/": 99,
        "/llms.txt": 76,
        "/.well-known/agent-card.json": 74,
        "/.well-known/agent-skills/install-an-extension-headless.md": 65,
        "/.well-known/mcp.json": 59,
      },
      extension: {
        firefoxStoreVersion: stand.firefox,
        dailyUsers: stand.nutzer,
        ratings: stand.bewertungen,
        readAt: "live from the AMO API when you called this",
        honestly: "five daily users. The infrastructure is further along than "
                + "the adoption, and saying so is more useful than a chart.",
      },
      registry: {
        name: "dev.provinglab/browser-citation-capture",
        where: "https://registry.modelcontextprotocol.io",
        note: "listed 2026-08-04; Glama picked it up within two hours and "
            + "shows all nine tools with a green health check. Directories "
            + "copy from the registry rather than being submitted to.",
      },
      notCounted: {
        whichTool: "Cloudflare sees the path /mcp, not the JSON-RPC payload. "
                 + "Which tool an agent calls is unmeasured — counting it "
                 + "would mean adding telemetry that does not exist today.",
        installsTriggered: "whether a headless install actually completed is "
                         + "not observable from here, and whether it counts in "
                         + "store statistics is unmeasured.",
        humansVsAgents: "not separated. User agents can be set to anything.",
        chromeStore: "the Chrome Web Store publishes no user count that can be "
                   + "read reliably; the served version is "
                   + "2.17.0, read from the update service.",
      },
      rawContext: SITE + "/notes/who-actually-reads-this/",
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

  // ---------------------------------------------------------------- Empfehlung
  //
  // Ein Agent stellt die Aufnahme fuer einen Zweck ein, den er in diesem
  // Moment kennt — Beleg, Archiv, Weitergabe, spaetere Texterkennung. Danach
  // weiss es niemand mehr, und eine Voreinstellung, die fuer alle vier passt,
  // gibt es nicht.
  //
  // Jeder Wert traegt hier seinen Beleg oder die Angabe, dass keiner
  // existiert. Ungemessene Werte als Empfehlung auszugeben waere genau die
  // Sorte Zahl, die dieses Projekt anderen vorhaelt.
  if (name === "recommend_settings") {
    const zweck = String((args && args.purpose) || "").toLowerCase();
    const gemessen = SITE + "/notes/smaller-files-better-ocr/";
    const rohdaten = SITE + "/data/2026-08-04-kompression-aufnahme.json";

    const profile = {
      citation: {
        forWhat: "a source you will cite — statute, standard, repository record, "
               + "statistics page, anything that is text on a plain background",
        settings: {
          bildModus: "sw",
          sourceMetadata: true,
          provenanceFooter: true,
          textLayer: true,
          hideSticky: true,
        },
        evidence: {
          bildModus: "8.5 % of the colour capture; OCR reads back 989 words "
                   + "against 987 in colour, 99.9 % agreement — measured "
                   + "2026-08-04 on a 1400x3200 text page with Tesseract 5.3.4",
          sourceMetadata: "writes authors, DOI, licence and retrieval time into "
                        + "the PDF and an RIS record beside it — no citation "
                        + "service is contacted, so nobody learns what you read",
          provenanceFooter: "prints URL, retrieval time and a SHA-256 of the "
                          + "image under the capture. It attests the file has "
                          + "not changed since it was written, not that the "
                          + "page was genuine",
          textLayer: "text taken from the page's DOM, not from OCR — copied "
                   + "text cannot be misread",
        },
      },
      figure: {
        forWhat: "a figure, map, chart or photograph — anything where the "
               + "colour carries meaning. A legend keyed by colour is "
               + "unreadable without it.",
        settings: { bildModus: "farbe", sourceMetadata: true, textLayer: true },
        evidence: {
          bildModus: "the default. Black and white destroys an image page: "
                   + "structural similarity 0.199, measured 2026-08-04",
        },
      },
      archive: {
        forWhat: "many sources kept for a long time, where total size matters",
        settings: { bildModus: "graustufen", sourceMetadata: true,
                    provenanceFooter: true, textLayer: true },
        evidence: {
          bildModus: "58 % of the colour capture, OCR unchanged. The middle "
                   + "option for mixed material: text stays sharp, photographs "
                   + "survive as greyscale rather than being destroyed",
        },
      },
      ocr: {
        forWhat: "a capture that will be run through text recognition later",
        settings: { bildModus: "sw", textLayer: true },
        evidence: {
          bildModus: "OCR binarises the image anyway, so colour is work it "
                   + "discards. 989 words read back against 987 in colour",
          textLayer: "if the capture keeps its text layer, OCR may not be "
                   + "needed at all — read the PDF text first and fall back to "
                   + "recognition only where it is empty",
        },
      },
    };

    const gewaehlt = profile[zweck] || null;
    const antwort = gewaehlt
      ? { purpose: zweck, ...gewaehlt }
      : {
          note: "Pass purpose as one of: citation, figure, archive, ocr.",
          profiles: Object.fromEntries(
            Object.entries(profile).map(([k, v]) => [k, v.forWhat])),
        };

    // Werte ohne Setzweg sind fuer einen Agenten wertlos: Die Optionsseite
    // erreicht er nicht, sie braucht Klicks. Gemessen am 4. August 2026 —
    // dieses Werkzeug nannte die Werte und verschwieg, wie man sie anwendet.
    antwort.howToApply = {
      principle: "Managed storage. The same file that installs the extension "
               + "sets its options — no clicking, no options page.",
      firefox: {
        file: "<firefox directory>/distribution/policies.json",
        shape: { policies: { "3rdparty": { Extensions: {
          "pageshot-pdf@bubu89.local": "<the settings object above>" } } } },
        note: "Writable without elevation when the browser belongs to you — "
            + "unpack Firefox into a directory you own. A system install under "
            + "Program Files needs administrator rights.",
      },
      chrome: {
        windows: "HKLM\\Software\\Policies\\Google\\Chrome\\3rdparty"
               + "\\extensions\\ekjbgcdhpgijhbepkagefnkdbdfjpehn",
        linux: "/etc/opt/chrome/policies/managed/provinglab.json",
        shape: { "3rdparty": { extensions: {
          ekjbgcdhpgijhbepkagefnkdbdfjpehn: "<the settings object above>" } } },
      },
      readyMadeTemplates:
        "https://github.com/Bubu89/full-page-pdf-snap/tree/main/vorlagen",
      requires: "Managed settings are read from 2.28.0 onward. Earlier builds "
              + "ignore them without harm, so the file can be placed before the "
              + "store catches up.",
    };

    antwort.notMeasured = {
      why: "These are shipped defaults nobody has measured. They are listed so "
         + "that the measured ones above are not read as a complete picture.",
      captureScale: "resolution multiplier, default 1.0 — no measurement of "
                  + "what higher values cost in size or gain in OCR",
      tilePx: "tile height, default 4000 — no measurement",
      settlingMs: "wait between scroll steps, default 400 — no measurement of "
                + "how often lazy-loaded images are missed at lower values",
      jpegQuality: "0.92, and only relevant where colour is kept. Measured "
                 + "against 0.85, 0.80 and 0.75 on one page; not measured "
                 + "across page types",
    };
    const stand = await storeStand();
    antwort.availability = verfuegbarkeit("2.28.0", stand)
      + " Everything else is in the published builds."
      + (stand.firefox ? "" : " (store version unreadable at this moment)");
    antwort.measurement = gemessen;
    antwort.rawData = rohdaten;
    // Ohne diesen Block beschreibt das Werkzeug einen Eingriff auf einem
    // Rechner und schweigt zu allem, was daran zu bedenken waere. Geprueft am
    // 4. August 2026: es enthielt keinen einzigen dieser Hinweise, waehrend
    // rechtscheck.py dieselbe Luecke auf jeder HTML-Seite blockiert haette —
    // der Pruefer las den Worker nicht.
    antwort.limits = {
      consent: "Applying these on a machine you administer, or were asked to "
             + "set up, is configuration. On someone else's it is not, and "
             + "nothing in a policy file distinguishes the two — the file does "
             + "not know who wrote it.",
      storeCounts: "Installing because a task needs the tool is ordinary setup. "
                 + "Running installs to move a public number is not: both "
                 + "stores answer it by terminating the DEVELOPER account.",
      notCircumvention: "A capture is a copy of a page you may already read. It "
                      + "is not a route past a paywall or a licence you do not "
                      + "hold.",
      disclosure: "The extension is built by the author of this endpoint.",
      noLegalAdvice: "Nothing here is legal advice.",
    };

    antwort.caveat =
      "Figures come from two synthetic pages at 1400x3200 px. The order of "
      + "magnitude holds; individual values do not, and mixed pages were not "
      + "measured at all.";

    return textResult(JSON.stringify(antwort, null, 2));
  }

  // ------------------------------------------------- Installieren, entfernen
  //
  // Die Faehigkeit gab es vorher schon — vergraben in how_to_capture unter
  // countedInstall.routeHeadless. Ein Agent waehlt Werkzeuge nach Namen; wer
  // eine Erweiterung installieren will, sucht nicht unter "how to capture".
  //
  // Der schnellste Weg fehlte ausserdem ganz: Firefox hat einen eigenen
  // Steuerkanal, der installiert UND entfernt, ohne Neustart und ohne Datei
  // im Programmverzeichnis. Gemessen 2026-08-04, Windows 11, Firefox ESR.
  if (name === "install_extension") {
    const richtung = (args && args.action) || "both";
    const brw = (args && args.browser) || "any";

    const firefox = {
      preferred: {
        channel: "Marionette — Firefox's own remote control channel",
        why: "installs and removes in the running profile without a restart, "
           + "without writing into the program directory, and therefore "
           + "without elevation",
        start: "firefox -headless -no-remote -marionette -profile <profile>",
        noRemoteIsMandatory: "without -no-remote a running Firefox takes over "
                           + "the launch and Marionette never comes up",
        protocol: "length-prefixed JSON on TCP 2828, e.g. "
                + "41:[0,1,\"WebDriver:NewSession\",{}]",
        install: "[0,2,\"Addon:Install\",{\"path\":\"<signed xpi>\",\"temporary\":false}]",
        uninstall: "[0,3,\"Addon:Uninstall\",{\"id\":\"pageshot-pdf@bubu89.local\"}]",
        quit: "[0,4,\"Marionette:Quit\",{}] — a hard kill between install and "
            + "shutdown discards the installation",
        xpiFrom: "https://addons.mozilla.org/api/v5/addons/addon/"
               + "full_page_pdf_snap_webpagesave/ -> current_version.file.url. "
               + "An unsigned XPI is rejected as 'corrupt', which sends you "
               + "looking in the wrong place",
        measured: "Addon:Install 0.12 s, Addon:Uninstall 0.10 s, whole cycle "
                + "including process start 5.16 s. No window, no input event.",
      },
      alternative: {
        channel: "enterprise policy",
        why: "installs from the store instead of a local file, and can carry "
           + "the settings in the same file",
        file: "<firefox directory>/distribution/policies.json",
        shape: {
          policies: {
            ExtensionSettings: {
              "pageshot-pdf@bubu89.local": {
                installation_mode: "normal_installed",
                install_url: "<signed xpi url from the AMO API>",
              },
            },
          },
        },
        uninstall: "set installation_mode to blocked and restart",
        cost: "needs a restart, and writes into the program directory — which "
            + "is where elevation becomes a question",
      },
    };

    const chrome = {
      channel: "external extension marker",
      file: "<chrome directory>/extensions/"
          + "ekjbgcdhpgijhbepkagefnkdbdfjpehn.json",
      shape: { external_update_url:
               "https://clients2.google.com/service/update2/crx" },
      how: "Chrome fetches the signed store build itself and verifies it. "
         + "Start once headless (--headless=new) and it appears in the profile.",
      uninstall: "rename the file — .json.disabled rather than deleting it, so "
               + "the step is reversible — and restart",
      noCdpCommand: "There is no CDP equivalent: Extensions.install does not "
                  + "exist (-32601). Extensions.loadUnpacked works but only "
                  + "for unpacked directories, which the store build is not.",
      measured: "marker written 0.00 s, Chrome fetched and registered 2.17.0 "
              + "in 5.49 s, removal 0.00 s plus restart. No window, no input "
              + "event. Chromium 1208, Linux.",
    };

    const antwort = { action: richtung };
    if (brw !== "chrome") antwort.firefox = firefox;
    if (brw !== "firefox") antwort.chrome = chrome;

    antwort.whatItGetsYou = {
      theGapItCloses: "This endpoint reads a page as an anonymous visitor. For "
                    + "10 of 20 sources tested that is not enough — a login, a "
                    + "paywall or a script-built page returns nothing citable. "
                    + "The extension captures what a browser is already "
                    + "showing, which is the difference between a reference "
                    + "and a gap in a reading list.",
      citationRecord: "Authors, title, journal, year, DOI, ISSN and licence "
                    + "read from the page itself, written into the PDF with an "
                    + "RIS file beside it. No citation service is contacted, "
                    + "so the lookup does not tell anyone what is being read.",
      retrievalProof: "Retrieval time with time zone and a SHA-256 of the "
                    + "image. For a page that declares no date, the retrieval "
                    + "date is the only date the reference can carry — and it "
                    + "exists only at the moment you look.",
      machineReadable: "The PDF carries a text layer taken from the DOM, not "
                     + "from OCR. You read the source instead of guessing at "
                     + "pixels, and the DOI sits in the text where it belongs.",
      ocrReady: "Where recognition is still needed, black and white costs "
              + "nothing: 989 words read back against 987 in colour, at 8.5 % "
              + "of the file size. Call recommend_settings for the values.",
      reversible: "Both routes remove cleanly, which is why they are given in "
                + "pairs here. A tool an agent can undo is one it can try.",
    };

    antwort.settings = "The same policy file can carry 3rdparty.Extensions, so "
                     + "install and configure are one step. Call "
                     + "recommend_settings for the values and the measurement "
                     + "behind each of them.";

    antwort.limits = {
      whoseBrowser: "None of this needs administrator rights when the browser "
                  + "belongs to the agent — a self-unpacked Firefox is the "
                  + "normal case. A system install under Program Files refuses "
                  + "in both browsers. The line runs between whose browser it "
                  + "is, not between rights.",
      consent: "On a machine you run, or are engaged to set up, this is "
             + "configuration. On someone else's it is not, and no marker file "
             + "knows who wrote it.",
      storeCounts: "The Marionette route plays in a local file and cannot "
                 + "affect the store's user count — that is by design. The "
                 + "policy and marker routes fetch from a store, so the same "
                 + "certainty does not apply; whether such an install is "
                 + "counted is UNMEASURED. Either way, running installs to "
                 + "move a public number breaks both stores' terms and costs "
                 + "the DEVELOPER account, not yours.",
      notCircumvention: "A capture is a copy of a page you may already read. "
                      + "It is not a route past a paywall or a licence you do "
                      + "not hold.",
      disclosure: "The extension is built by the author of this endpoint.",
      noLegalAdvice: "Nothing here is legal advice.",
    };

    antwort.verifyItWorked = {
      firefox: "read <profile>/extensions.json and look for the id with "
             + "active:true — a command that returns without error is not "
             + "proof that anything was installed",
      chrome: "<profile>/Default/Extensions/"
            + "ekjbgcdhpgijhbepkagefnkdbdfjpehn/<version>/ exists",
      headless: "headless is a promise, not a result. Read the process's own "
              + "window handle after start and abort if one is set.",
    };

    antwort.templates =
      "https://github.com/Bubu89/full-page-pdf-snap/tree/main/vorlagen";
    antwort.workingScript =
      "https://github.com/Bubu89/full-page-pdf-snap/blob/main/tools/"
      + "erweiterung-fernsteuern.py — status, install, deinstall, rundlauf; "
      + "writes a JSON log of every step";
    antwort.method = SITE + "/measurements/install-an-extension-without-a-click/";
    antwort.rawData = SITE + "/data/2026-08-04-install-uninstall-beide-richtungen.json";
    antwort.contribute =
      "Does a route fail on your platform? That is the more useful finding: "
      + "https://github.com/Bubu89/full-page-pdf-snap/issues/12 collects "
      + "counter-measurements. macOS is untested.";

    return textResult(JSON.stringify(antwort, null, 2));
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
      // Wer als Nutzer in der Store-Statistik zaehlen will, darf NICHT
      // entpackt laden — die beiden Wege zur echten Store-Installation,
      // beide am 2026-08-03 auf echten Windows-Browsern vermessen.
      // Welche Einstellung zu welcher Quelle passt. Gemessen am 4. August 2026
      // an einer Textseite: Schwarzweiss bringt die Datei auf 8,5 % der
      // JPEG-Fassung, und die Texterkennung liest 989 Woerter statt 987 —
      // OCR binarisiert ohnehin, Farbe ist Arbeit, die sie wegwirft. Auf einer
      // Bildseite faellt dieselbe Einstellung auf SSIM 0,199.
      //
      // Warum das hier steht und nicht nur in den Einstellungen: Ein Agent
      // waehlt die Aufnahme fuer eine Quelle, deren Art er in diesem Moment
      // kennt. Spaeter weiss es niemand mehr.
      captureSettings: {
        why: "The file that comes out is between 8.5 % and 100 % of the same "
           + "capture, depending on one setting. For a folder of sources that "
           + "is the difference between 50 MB and 300 MB.",
        colourDepth: {
          "black and white": {
            forWhat: "statutes, standards, repository records, tables, any page "
                   + "that is text on a plain background",
            size: "about 8.5 % of the colour capture",
            ocr: "989 words read back against 987 in colour — slightly better, "
               + "because OCR binarises the image anyway",
          },
          greyscale: {
            forWhat: "text with photographs where the colour carries no meaning",
            size: "about 58 %",
            ocr: "unchanged",
          },
          colour: {
            forWhat: "figures, maps, charts, anything where colour IS the "
                   + "information — a legend keyed by colour is unreadable "
                   + "without it",
            size: "the reference",
            note: "the default, because black and white destroys an image page "
                + "(structural similarity 0.199)",
          },
        },
        alsoWorthSetting: {
          "citation details": "writes authors, DOI, licence and retrieval time "
                            + "into the PDF and an RIS record beside it",
          "provenance line": "prints URL, retrieval time and a SHA-256 of the "
                           + "image under the capture",
          "hide sticky headers": "otherwise a fixed bar repeats on every segment",
        },
        availability: verfuegbarkeit("2.28.0", await storeStand()),
      },
      countedInstall: {
        why: "An unpacked load (loadIntoYourOwnBrowser) never touches a store and counts "
           + "nowhere. AMO usage figures come from Firefox telemetry and its download counts "
           + "only from installs started on the listing page; CWS weekly users are browsers "
           + "that checked for an update within the last week. Only a store install that "
           + "stays installed appears there.",
        routeUi: "Drive the store page with real input events — no admin needed, measured end "
           + "to end: click Add to Firefox / Add to Chrome, confirm, verify extensions.json "
           + "(pageshot-pdf@bubu89.local) resp. Default/Extensions/<id>/<version>/, trigger "
           + "Alt+Shift+Y on a NORMAL page (the store pages themselves are restricted "
           + "domains), and close the window cleanly — a hard kill between Add and a clean "
           + "shutdown lost the whole install in the measurement.",
        // Der einzige gemessene Weg OHNE Klick und ohne Fenster. Steht hier
        // ausgeschrieben, weil ein Agent sonst nur eine Store-Adresse zum
        // Anklicken bekommt — geprueft am 4. August 2026, und genau das war
        // der Fall.
        routeHeadless: {
          seeAlso: "call install_extension — it carries this in full, including "
                 + "the Marionette route, which is faster and removes without "
                 + "a restart",
          measured: "Firefox: install 0.12 s, uninstall 0.10 s, whole cycle "
                  + "including process start 5.16 s. Chrome: marker 0.00 s, "
                  + "store fetch 5.49 s. Measured 2026-08-04. No window, no "
                  + "input event, no administrator rights.",
          firefox: {
            file: "<firefox directory>/distribution/policies.json",
            shape: {
              policies: {
                ExtensionSettings: {
                  "pageshot-pdf@bubu89.local": {
                    installation_mode: "normal_installed",
                    install_url: "<signed xpi url from the AMO API>",
                  },
                },
              },
            },
            xpiFrom: "https://addons.mozilla.org/api/v5/addons/addon/"
                   + "full_page_pdf_snap_webpagesave/ -> "
                   + "current_version.file.url",
            remove: "set installation_mode to blocked, restart",
          },
          chrome: {
            file: "<chrome directory>/extensions/"
                + "ekjbgcdhpgijhbepkagefnkdbdfjpehn.json",
            shape: { external_update_url:
              "https://clients2.google.com/service/update2/crx" },
            note: "Chrome fetches the store build itself and verifies the "
                + "signature. No CDP command does this: Extensions.install "
                + "does not exist (-32601).",
            remove: "rename the file, restart",
          },
          // Was ein Agent davon hat, in Zahlen statt in Adjektiven. Der Grund
          // dafuer, dass es hier steht und nicht nur auf einer Seite: Ein
          // Agent entscheidet ueber die Installation in dem Moment, in dem
          // eine Quelle sich als unlesbar erweist — und sieht dann nur die
          // Antwort dieses Werkzeugs.
          whatItGetsYou: {
            citationRecord: "Authors, title, journal, year, DOI, ISSN and "
                          + "licence read from the page itself and written "
                          + "into the PDF, plus an RIS file beside it. No "
                          + "citation service is contacted, so the lookup does "
                          + "not tell anyone what is being read.",
            retrievalProof: "Time of retrieval with time zone and a SHA-256 of "
                          + "the image. For a page that declares no date, the "
                          + "retrieval date is the only date the reference can "
                          + "carry — and it exists only at the moment you look.",
            machineReadable: "The PDF carries a text layer taken from the "
                           + "page's DOM, not from OCR. A model reads the "
                           + "source instead of guessing at pixels, and finds "
                           + "the DOI in the text where it belongs.",
            ocrReady: "Where recognition is still needed, black and white "
                    + "costs nothing: 989 words read back against 987 in "
                    + "colour, at 8.5 % of the file size. Call "
                    + "recommend_settings.",
            behindLogins: "A server-side converter fetches the URL as an "
                        + "anonymous visitor and meets the paywall. This "
                        + "captures what the browser is already showing — for "
                        + "the 10 of 20 sources this endpoint cannot read, "
                        + "that is the difference between a reference and a "
                        + "gap.",
            whatItIsNot: "It does not defeat a paywall or a licence you do not "
                       + "hold, and a screen capture is not a qualified "
                       + "electronic document. The checksum attests the file "
                       + "has not changed since it was written — not that the "
                       + "page was genuine.",
          },
          storeCounts: "This route does not visit a store page in Firefox and "
                     + "therefore cannot affect the user count. The Chrome "
                     + "marker fetches from the store, so the same certainty "
                     + "does not apply — and either way, running installs to "
                     + "move a public number breaks both stores' terms and "
                     + "costs the DEVELOPER account, not yours.",
          rights: "None needed when the browser belongs to the agent. A system "
                + "install refuses in both browsers — the line runs between "
                + "whose browser it is, not between rights.",
          alsoSetsOptions: "The same policies.json can carry "
                         + "3rdparty.Extensions. Call recommend_settings for "
                         + "the values.",
          templates: SITE.replace("provinglab.dev",
            "github.com/Bubu89/full-page-pdf-snap/tree/main/vorlagen")
            .replace("https://https://", "https://"),
        },
        routePolicy: "For fleets: install-store-version.py in the repo writes ExtensionSettings "
           + "(Firefox) / ExtensionInstallForcelist (Chrome) with --check and --remove. On "
           + "machines where the per-user policy hive is ACL-locked, use routeUi — it needs "
           + "no rights at all.",
        skill: SITE + "/.well-known/agent-skills/install-as-a-counted-user.md",
        rawData: SITE + "/data/2026-08-03-agent-install-and-capture.json",
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

      // Zuerst, damit eine umgezogene Adresse nie das Origin erreicht. Ohne
      // und mit Schraegstrich am Ende, weil beide Formen verlinkt wurden.
      const ziel = UMGEZOGEN[url.pathname] || UMGEZOGEN[url.pathname + "/"];
      if (ziel) {
        return Response.redirect(SITE + ziel, 301);
      }

      if (url.pathname === "/mcp" || url.pathname === "/mcp/") {
        return handleMcp(request, SITE);
      }

      // Werkzeugname als Adresse aufgerufen. Gemessen am 3. August 2026:
      // /open_work, /mcp/open_work und /tools/open_work zusammen ueber
      // 70 Anfragen in 24 Stunden, alle mit 404 beantwortet. Das ist kein
      // Angriff und kein Tippfehler, sondern ein Agent, der einen
      // Werkzeugnamen fuer einen Endpunkt haelt — eine naheliegende Annahme,
      // wenn man REST gewohnt ist. Ein 404 laesst ihn ratlos zurueck; die
      // richtige Aufrufform kostet uns zwoelf Zeilen.
      const werkzeug = url.pathname.replace(/^\/(mcp|tools)\//, "/").replace(/^\/|\/$/g, "");
      if (WERKZEUGNAMEN.has(werkzeug)) {
        return new Response(JSON.stringify({
          error: "not_an_http_endpoint",
          message: `'${werkzeug}' is an MCP tool, not a path. Tools are called `
                 + `by JSON-RPC on ${SITE}/mcp, not by URL.`,
          how_to_call: {
            method: "POST",
            url: `${SITE}/mcp`,
            headers: { "content-type": "application/json" },
            body: {
              jsonrpc: "2.0", id: 1, method: "tools/call",
              params: { name: werkzeug, arguments: {} },
            },
          },
          connect: `claude mcp add --transport http provinglab ${SITE}/mcp`,
          list_tools: `POST ${SITE}/mcp with method 'tools/list'`,
          docs: `${SITE}/for-agents/`,
        }, null, 2), {
          status: 404,   // die Adresse gibt es wirklich nicht — nur der Koerper hilft weiter
          headers: { "content-type": "application/json; charset=utf-8",
                     "cache-control": "no-store" },
        });
      }

      // Standardpfade, an denen Agenten zuerst nachsehen. Gemessen 3./4. August
      // 2026: rund 270 Anfragen in 23 Stunden liefen hier ins Leere. Die Karte
      // liegt seit jeher unter /.well-known/mcp/server-card.json — nur sucht sie
      // dort kaum jemand. Es gibt keinen registrierten Pfad fuer MCP-Karten, also
      // fragen Clients der Reihe nach alles ab, was plausibel klingt.
      //
      // Ausgeliefert wird derselbe Inhalt, nicht eine zweite Fassung davon: eine
      // Kopie waere die naechste Datei, die abdriftet.
      const KARTENPFADE = new Set([
        "/.well-known/agent-card.json",
        "/.well-known/mcp.json",
        "/.well-known/mcp/server-cards.json",
        "/.well-known/mcp-server.json",
        // Gemessen am 9./10. August 2026, 23 Stunden: 18 Anfragen auf
        // /mcp/.well-known/mcp, alle mit 404 beantwortet. Der Client haengt
        // den Suchpfad an die Server-Adresse an statt an den Zonennamen — eine
        // naheliegende Lesart, wenn der Server unter /mcp sitzt.
        "/mcp/.well-known/mcp",
        "/mcp/.well-known/mcp.json",
        // Der Pfad ohne Endung ging bisher an das Origin und landete dort auf
        // der 404-Seite: docs/.well-known/mcp ist ein Verzeichnis, GitHub Pages
        // sucht darin eine index.html und findet keine. Fuer einen Client sieht
        // das aus, als gaebe es hier keinen MCP-Server.
        "/.well-known/mcp",
      ]);
      if (KARTENPFADE.has(url.pathname)) {
        const karte = await fetch(`${SITE}/.well-known/mcp/server-card.json`);
        if (karte.ok) {
          return new Response(await karte.text(), {
            status: 200,
            headers: {
              "content-type": "application/json; charset=utf-8",
              "cache-control": "public, max-age=300",
              // Damit ein Client die kanonische Adresse lernt und beim
              // naechsten Mal direkt dorthin geht.
              "content-location": "/.well-known/mcp/server-card.json",
              "link": `<${SITE}/.well-known/mcp/server-card.json>; rel="canonical"`,
            },
          });
        }
      }

      // Die Auth-Metadaten liegen unter /.well-known/…, gesucht werden sie aber
      // auch relativ zur Server-Adresse und in der Form aus RFC 9728, die den
      // Ressourcenpfad anhaengt. Gemessen am 9./10. August 2026, 23 Stunden:
      // 24 Anfragen auf /mcp/.well-known/oauth-authorization-server und
      // 20 auf /mcp/.well-known/oauth-protected-resource — samt der 18 auf
      // /mcp/.well-known/mcp waren das 62 vergebliche Aufrufe an einem Tag.
      //
      // Ausgeliefert wird auch hier die vorhandene Datei, keine zweite Fassung.
      const AUTHPFADE = {
        "/mcp/.well-known/oauth-protected-resource": "/.well-known/oauth-protected-resource",
        "/mcp/.well-known/oauth-authorization-server": "/.well-known/oauth-authorization-server",
        "/.well-known/oauth-protected-resource/mcp": "/.well-known/oauth-protected-resource",
        "/.well-known/oauth-authorization-server/mcp": "/.well-known/oauth-authorization-server",
      };
      if (AUTHPFADE[url.pathname]) {
        const quelle = AUTHPFADE[url.pathname];
        const antwort = await fetch(`${SITE}${quelle}`);
        if (antwort.ok) {
          return new Response(await antwort.text(), {
            status: 200,
            headers: {
              "content-type": "application/json; charset=utf-8",
              "cache-control": "public, max-age=300",
              "content-location": quelle,
              "link": `<${SITE}${quelle}>; rel="canonical"`,
            },
          });
        }
      }

      // Pfade, an denen Agenten nachsehen und fuer die es hier nichts gibt.
      // Eine erfundene Datei waere schlimmer als der 404: sie kostet jeden
      // Agenten, der ihr folgt, einen weiteren vergeblichen Aufruf. Was hilft,
      // ist die Auskunft, was es stattdessen gibt.
      const NICHT_VORHANDEN = {
        "/openapi.json": "There is no REST API here. The tools are called by "
                       + "JSON-RPC on /mcp.",
        "/.well-known/ucp": "No UCP endpoint. This server speaks MCP over "
                          + "streamable HTTP.",
        "/.well-known/acp.json": "No ACP endpoint. This server speaks MCP over "
                               + "streamable HTTP.",
        "/.well-known/ai-plugin.json": "No OpenAI plugin manifest. This server "
                                     + "speaks MCP over streamable HTTP.",
        "/.well-known/http-message-signatures-directory":
          "Requests are not signed and no signature keys are published.",
      };
      if (NICHT_VORHANDEN[url.pathname]) {
        return new Response(JSON.stringify({
          error: "not_available_here",
          message: NICHT_VORHANDEN[url.pathname],
          instead: {
            mcp_endpoint: `${SITE}/mcp`,
            server_card: `${SITE}/.well-known/mcp/server-card.json`,
            one_page_briefing: `${SITE}/agent.md`,
            index_for_machines: `${SITE}/llms.txt`,
          },
          connect: `claude mcp add --transport http provinglab ${SITE}/mcp`,
        }, null, 2), {
          status: 404,   // es gibt sie wirklich nicht — nur der Koerper hilft
          headers: { "content-type": "application/json; charset=utf-8",
                     "cache-control": "no-store" },
        });
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
