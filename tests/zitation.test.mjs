/**
 * Testfaelle fuer die Zitationserfassung.
 *
 * Jeder Fall stammt aus einem Fehler, der im Betrieb aufgetreten ist, oder
 * aus einer Quellenart, die anders behandelt werden muss als die uebrigen.
 * Ein neuer Fehler gehoert hier als Fall hinein, bevor er behoben wird —
 * sonst kommt er wieder.
 *
 *   node tests/zitation.test.mjs
 */
import { readFileSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const HIER = dirname(fileURLToPath(import.meta.url));
const src = readFileSync(join(HIER, "..", "worker", "mcp.js"), "utf8");
// Den ganzen Block von der ersten Hilfsfunktion bis zum Ende von bibtexAus
// uebernehmen — im Wortlaut. Ein Nachbau wuerde etwas anderes pruefen als das,
// was ausgeliefert wird. AGENT wird nur beim Netzabruf gebraucht, den diese
// Testfaelle nicht ausloesen.
const von = src.indexOf("function entzeichnen(");
const bisEnde = src.indexOf("\n}\n", src.indexOf("function bibtexAus(")) + 3;
const F = new Function('const AGENT = "test";\n' + src.slice(von, bisEnde) +
                       "\n return { quelleAusHtml, risAus, bibtexAus, plattformAbfrage, oaiDcAusXml, kennungAusAdresse, cellarAusXml };")();

const seite = (kopf, koerper = "x".repeat(9000)) =>
  `<html><head>${kopf}</head><body>${koerper}</body></html>`;

const FAELLE = [
  {
    name: "Zeitschriftenaufsatz mit vollstaendigen Verlagsangaben",
    html: seite(`<title>Efficacy of Psychological Interventions</title>
      <meta name="citation_title" content="Efficacy of Psychological Interventions">
      <meta name="citation_author" content="Fruehauf, Sarah">
      <meta name="citation_author" content="Gerger, Heike">
      <meta name="citation_journal_title" content="Archives of Sexual Behavior">
      <meta name="citation_volume" content="42"><meta name="citation_issue" content="6">
      <meta name="citation_firstpage" content="915"><meta name="citation_lastpage" content="933">
      <meta name="citation_doi" content="10.1007/s10508-012-0062-0">
      <meta name="citation_issn" content="1573-2800">
      <meta name="citation_publication_date" content="2013">`),
    url: "https://link.springer.com/article/10.1007/s10508-012-0062-0",
    pruefe: (q) => [
      [q.art === "Zeitschriftenaufsatz", `art=${q.art}`],
      [q.authors.length === 2, `Verfasser=${q.authors.length}`],
      [q.year === "2013", `Jahr=${q.year}`],
      [q.doi === "10.1007/s10508-012-0062-0", `doi=${q.doi}`],
      [!q.warning, `Warnung=${q.warning}`],
      [q.complete === true, "nicht als vollstaendig gewertet"],
    ],
  },
  {
    name: "Buchkapitel: ISBN mit Seitenangabe schlaegt Zeitschriftenfeld",
    html: seite(`<title>Arbeitsmarkt</title>
      <meta name="citation_title" content="Arbeitsmarkt">
      <meta name="citation_author" content="Keller, Berndt">
      <meta name="citation_journal_title" content="Handwoerterbuch der Stadt- und Raumentwicklung">
      <meta name="citation_isbn" content="978-3-88838-559-9">
      <meta name="citation_firstpage" content="83">
      <meta name="citation_date" content="2018">`),
    url: "https://www.ssoar.info/ssoar/handle/document/72281",
    pruefe: (q) => [
      [q.art === "Buchkapitel", `art=${q.art} (ISBN+Seite muss Kapitel ergeben)`],
      [!!q.container, "Sammelwerk nicht gesetzt"],
    ],
  },
  {
    name: "Hochschulschrift ueber dissertation_institution",
    html: seite(`<title>Eine Dissertation</title>
      <meta name="citation_title" content="Eine Dissertation">
      <meta name="citation_author" content="Muster, Anna">
      <meta name="citation_dissertation_institution" content="Universitaet Wien">
      <meta name="citation_date" content="2021">`),
    url: "https://utheses.univie.ac.at/detail/12345",
    pruefe: (q) => [
      [q.art === "Hochschulschrift", `art=${q.art}`],
      [q.publisher === "Universitaet Wien", `verlag=${q.publisher}`],
    ],
  },
  {
    name: "Behoerdenquelle: Koerperschaft ist Urheber",
    html: seite(`<title>Bevoelkerungsstand</title>
      <meta property="og:site_name" content="Statistik Austria">`),
    url: "https://www.statistik.at/statistiken/bevoelkerungsstand",
    pruefe: (q) => [
      [q.authors.length === 1 && q.authors[0] === "Statistik Austria", `Verfasser=${JSON.stringify(q.authors)}`],
      [q.corporateAuthor === true, "nicht als Koerperschaft gekennzeichnet"],
      // Die Seite nennt kein Jahr, also ist der Satz unvollstaendig — und seit
      // dem 03.08.2026 sagt der Endpunkt auch, woran es liegt, statt es zu
      // verschweigen. Frueher stand hier `!q.warning`; das prueft den Stand,
      // in dem `complete: false` ohne Begruendung zurueckkam und ein
      // aufrufendes Programm den Satz am gefuellten Titel fuer einen Treffer
      // hielt. Erwartet wird jetzt genau das Gegenteil: eine Warnung, die das
      // fehlende Feld benennt.
      [q.complete === false, `complete=${q.complete}`],
      [/year is missing/.test(q.warning || ""), `Warnung=${q.warning}`],
    ],
  },
  {
    name: "Sperrseite wird nicht zur Quellenangabe (Fehler 3, 5)",
    html: seite(`<title>Making sure you're not a bot!</title>`, "kurz"),
    url: "https://www.ssoar.info/x",
    pruefe: (q) => [[!!q.warning, "keine Warnung bei Bot-Wand"]],
  },
  {
    name: "Fachtitel mit 'Error' ist keine Fehlerseite (Fehler 6)",
    html: seite(`<title>Error Analysis in Second Language Acquisition</title>
      <meta name="citation_author" content="Corder, S. P.">
      <meta name="citation_journal_title" content="IRAL">
      <meta name="citation_date" content="1967">`),
    url: "https://example.org/a",
    pruefe: (q) => [[!q.warning, `faelschlich als Fehlerseite: ${q.warning}`]],
  },
  {
    name: "Leere Verfasser aus ';;;;;' (Fehler 9)",
    html: seite(`<title>Distribution of Epiphytic Lichens</title>
      <meta name="citation_author" content=";;;;;">
      <meta name="citation_journal_title" content="The Korean Journal of Ecology">
      <meta name="citation_date" content="2004">`),
    url: "https://doi.org/10.5141/x",
    pruefe: (q, r, b) => [
      [q.authors.length === 0, `leere Verfasser durchgelassen: ${JSON.stringify(q.authors)}`],
      [!/ and  and /.test(b), "BibTeX-Autorenliste kaputt"],
      [!/AU  - \s*$/m.test(r), "leeres AU-Feld im RIS"],
    ],
  },
  {
    name: "Reine Datensatznummer ist kein Titel (Fehler 10)",
    html: seite(`<title>1643858</title>`, "kurz"),
    url: "https://example.org/rec/1643858",
    pruefe: (q) => [[!!q.warning, "Zahlentitel als Quelle akzeptiert"]],
  },
  {
    name: "Seitenname-Anhaengsel abschneiden, aber nicht den Titel (Fehler 8)",
    html: seite(`<title>| bioRxiv</title><meta property="og:site_name" content="bioRxiv">`, "kurz"),
    url: "https://www.biorxiv.org/content/x",
    pruefe: (q) => [[!!q.warning, "nur der Seitenname wurde als Titel akzeptiert"]],
  },
  {
    name: "DOI aus der Adresse ohne Wegstueck (Fehler 2)",
    html: seite(`<title>Ein Aufsatz</title><meta name="citation_author" content="A, B">
      <meta name="citation_date" content="2021">`),
    url: "https://www.frontiersin.org/articles/10.3389/fpsyg.2021.618509/full",
    pruefe: (q) => [
      [q.doi === "10.3389/fpsyg.2021.618509", `doi=${q.doi} (darf kein /full tragen)`],
    ],
  },
  {
    name: "Nicht-lateinische Angaben bleiben unversehrt",
    html: seite(`<title>ЭНЕРГЕТИЧЕСКИЕ ПОКАЗАТЕЛИ</title>
      <meta name="citation_title" content="ЭНЕРГЕТИЧЕСКИЕ ПОКАЗАТЕЛИ">
      <meta name="citation_author" content="Лавренченко, Г. К.">
      <meta name="citation_journal_title" content="Технические газы">
      <meta name="citation_date" content="2007">`),
    url: "https://journals.uran.ua/x",
    pruefe: (q, r) => [
      [q.title.startsWith("ЭНЕРГ"), `Titel verstuemmelt: ${q.title}`],
      [/Лавренченко/.test(r), "kyrillischer Name fehlt im RIS"],
    ],
  },
  {
    name: "Namenszusatz bleibt unangetastet",
    html: seite(`<title>Ein Werk</title>
      <meta name="citation_author" content="Ludwig van Beethoven">
      <meta name="citation_journal_title" content="J"><meta name="citation_date" content="1810">`),
    url: "https://example.org/b",
    pruefe: (q) => [[q.authors[0] === "Ludwig van Beethoven", `Name zerlegt: ${q.authors[0]}`]],
  },
  {
    name: "RIS und BibTeX sind wohlgeformt",
    html: seite(`<title>Ein Aufsatz</title><meta name="citation_title" content="Ein Aufsatz">
      <meta name="citation_author" content="Muster, Max">
      <meta name="citation_journal_title" content="Zeitschrift"><meta name="citation_date" content="2020">
      <meta name="citation_doi" content="10.1000/x">`),
    url: "https://example.org/c",
    pruefe: (q, r, b) => [
      [r.startsWith("TY  - JOUR"), "RIS ohne Typ"],
      [/\r\nER  - \r\n$/.test(r), "RIS ohne Endmarker"],
      [r.split("\r\n").every((z) => !z || /^[A-Z][A-Z0-9]  - /.test(z)), "RIS-Zeile fehlgeformt"],
      [/^@article\{muster2020,/.test(b), `BibTeX-Schluessel: ${b.split("\n")[0]}`],
      [!/\{\s*\}/.test(b), "leeres BibTeX-Feld"],
    ],
  },
  {
    name: "Rechtsquelle: EU-Verordnung mit Datum im Titel",
    html: seite(`<title>Verordnung (EU) 2025/327</title>
      <meta name="WT.z_docTitle" content="Verordnung (EU) 2025/327 des Europaeischen Parlaments und des Rates vom 11. Februar 2025 ueber den europaeischen Raum fuer Gesundheitsdaten">`),
    url: "https://eur-lex.europa.eu/legal-content/DE/TXT/?uri=CELEX%3A32025R0327",
    pruefe: (q) => [
      [q.art === "Rechtsquelle", `art=${q.art}`],
      [q.year === "2025", `Jahr=${q.year} (steht im Titel, nicht in einem Datumsfeld)`],
      [q.publisher === "Europaeische Union", `Traeger=${q.publisher}`],
      [!q.warning, `Warnung=${q.warning}`],
    ],
  },
  {
    name: "Rechtsquelle: oesterreichisches Bundesrecht ohne jede Angabe",
    html: seite(`<title>RIS - Gesundheitstelematikgesetz 2012 - Bundesrecht konsolidiert</title>`),
    url: "https://www.ris.bka.gv.at/GeltendeFassung.wxe?Abfrage=Bundesnormen&Gesetzesnummer=20008120",
    pruefe: (q) => [
      [q.art === "Rechtsquelle", `art=${q.art}`],
      [q.publisher === "Republik Oesterreich", `Traeger=${q.publisher}`],
    ],
  },
  {
    name: "Kein Rechtsakt, nur ein Aufsatz ueber Recht",
    html: seite(`<title>Die Wirkung von Verordnungen auf den Datenschutz</title>
      <meta name="citation_title" content="Die Wirkung von Verordnungen auf den Datenschutz">
      <meta name="citation_author" content="Muster, Max">
      <meta name="citation_journal_title" content="Juristische Blaetter">
      <meta name="citation_date" content="2024">`),
    url: "https://link.springer.com/article/10.1007/x",
    pruefe: (q) => [
      [q.art === "Zeitschriftenaufsatz", `art=${q.art} — ein Aufsatz UEBER Recht ist keine Rechtsquelle`],
    ],
  },
  {
    name: "Twitter-Handle ist kein Verfasser (Fehler 13)",
    html: seite(`<title>Is it ok for A Network-Theoretic Framework</title>
      <meta name="twitter:site" content="@ResearchGate">
      <meta name="twitter:creator" content="@ResearchGate">
      <meta property="og:site_name" content="ResearchGate">`),
    url: "https://www.researchgate.net/post/Is_it_ok_for_A_Network",
    pruefe: (q, r) => [
      [!q.authors.some((a) => /^@/.test(a)), `Handle als Verfasser: ${JSON.stringify(q.authors)}`],
      [!/AU  - @/.test(r), "Handle im RIS-Verfasserfeld"],
      [q.publisher !== "@ResearchGate", `Herausgeber mit @: ${q.publisher}`],
    ],
  },
  {
    name: "PubMed-Namensform: Nachname vorn (Fehler 14)",
    html: seite(`<title>Measuring cancer evolution from the genome</title>
      <meta name="citation_title" content="Measuring cancer evolution from the genome">
      <meta name="citation_author" content="Graham TA">
      <meta name="citation_author" content="Sottoriva A">
      <meta name="citation_journal_title" content="The Journal of pathology">
      <meta name="citation_date" content="2017">
      <meta name="citation_doi" content="10.1002/path.4821">`),
    url: "https://pubmed.ncbi.nlm.nih.gov/27741350/",
    pruefe: (q) => [
      [q.authors[0] === "Graham TA", `roh veraendert: ${q.authors[0]}`],
      [q.art === "Zeitschriftenaufsatz", `art=${q.art}`],
    ],
  },
  // Die drei folgenden Faelle decken die Ableitung der Seitenart ab. Gegen die
  // echten Seiten lokal geprueft (curl mit Browser-Kennung, 03.08.2026):
  // derstandard.at deklariert og:type, zenodo.org nur schema.org in
  // URL-Schreibweise, wko.at/eservices keines von beiden. Live gegen den
  // Endpunkt pruefbar erst nach dem Ausliefern des Workers.
  {
    name: "Seitenart aus og:type (Issue #4)",
    html: seite(`<title>Ein Zeitungsartikel</title>
      <meta property="og:type" content="article">
      <meta property="og:site_name" content="Beispielzeitung">
      <meta property="og:title" content="Ein Zeitungsartikel">`),
    url: "https://www.derstandard.at/story/3000000200000/",
    pruefe: (q) => [
      [q.pageType === "article", `pageType=${q.pageType}`],
      // Der Fall, fuer den das Feld gebaut wurde: Artikel ohne Datums-
      // deklaration. Die Warnung benennt das fehlende Feld, pageType die Art
      // der Seite — erst beides zusammen macht den Satz einordbar.
      [q.complete === false, `complete=${q.complete}`],
      [/year is missing/.test(q.warning || ""), `Warnung=${q.warning}`],
    ],
  },
  {
    name: "Seitenart aus schema.org, URL-Schreibweise gekuerzt (Issue #4)",
    html: seite(`<title>Ein Werkzeug</title>
      <script type="application/ld+json">{"@context":"https://schema.org","@type":"https://schema.org/SoftwareSourceCode","name":"Ein Werkzeug"}</script>`),
    url: "https://zenodo.org/records/3832945",
    pruefe: (q) => [
      // SoftwareSourceCode faellt durch den Werktyp-Filter von jsonLdLesen;
      // fuer die Seitenart muss die Deklaration trotzdem zaehlen.
      [q.pageType === "SoftwareSourceCode", `pageType=${q.pageType}`],
    ],
  },
  {
    name: "Keine Seitenart deklariert: Feld bleibt weg (Issue #4)",
    html: seite(`<title>Eine Seite ohne jede Typangabe</title>`),
    url: "https://www.wko.at/eservices",
    pruefe: (q) => [
      // Geraten wird nichts: ohne og:type und ohne schema.org-Typ darf das
      // Feld nicht erscheinen, sonst unterscheidet es sich nicht vom Belegten.
      [!("pageType" in q), `pageType unerwartet vorhanden: ${q.pageType}`],
    ],
  },
];

// --- Maschinenschnittstelle der Plattform (OAI-PMH/SRU) ---------------------
// Die Faelle oben pruefen die HTML-Strecke; hier der letzte Rettungsweg davor,
// die Schnittstelle der Plattform selbst. Die Fixtures sind woertliche Auszuege
// der Live-Antworten vom 03.08.2026 (Abruf mit der Kennung des Endpunkts):
//   - DNB-SRU fuer IDN 1279437049: vollstaendiger oai_dc-Satz.
//   - OPUS opus4.kobv.de/opus4-zib: docId 1 liefert einen Satz, docId 8138 den
//     OAI-Fehler idDoesNotExist — beides hier als Verhalten verankert.
//   - PsychArchives /handle/20.500.12034/2487: GetRecord mit dem Identifier
//     oai:psycharchives.org:20.500.12034/2487 liefert den Satz.
// peDOCS faellt raus: pedocs.de/oai und www.pedocs.de/oai antworteten am
// 03.08.2026 beide mit HTTP 404, es gibt keine verifizierbare Schnittstelle.

const DNB_SRU = `<?xml version="1.0" encoding="UTF-8"?>
<searchRetrieveResponse xmlns="http://www.loc.gov/zing/srw/"><version>1.1</version><numberOfRecords>1</numberOfRecords><records><record><recordData><dc xmlns="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
  <dc:title>Deleuze - seine philosophischen Welten für Einsteiger 3. Band / Michael Pflaum</dc:title>
  <dc:creator>Pflaum, Michael [Verfasser]</dc:creator>
  <dc:publisher>Norderstedt : BoD – Books on Demand</dc:publisher>
  <dc:date>2023</dc:date>
  <dc:language>ger</dc:language>
  <dc:identifier xsi:type="tel:ISBN">978-3-7347-2612-5 Paperback : EUR 25.99 (DE)</dc:identifier>
  <dc:identifier xsi:type="dnb:IDN">1279437049</dc:identifier>
</dc></recordData></record></records></searchRetrieveResponse>`;

const OPUS_OAI = `<?xml version="1.0" encoding="utf-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <responseDate>2026-08-03T15:28:26Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="oai:kobv.de-opus4-zib:1">https://opus4.kobv.de/opus4-zib/oai</request>
  <GetRecord><record><header><identifier>oai:kobv.de-opus4-zib:1</identifier></header>
    <metadata><oai_dc:dc xmlns:oai_dc="http://www.openarchives.org/OAI/2.0/oai_dc/" xmlns:dc="http://purl.org/dc/elements/1.1/">
      <dc:title xml:lang="en">Efficient Numerical Simulation and Identification of Large Chemical Reaction Systems.</dc:title>
      <dc:creator>Deuflhard, Peter</dc:creator>
      <dc:creator>Nowak, Ulrich</dc:creator>
      <dc:date>1986-05-29</dc:date>
      <dc:type>doc-type:preprint</dc:type>
      <dc:language>eng</dc:language>
    </oai_dc:dc></metadata>
  </record></GetRecord>
</OAI-PMH>`;

const OAI_FEHLER = `<?xml version="1.0" encoding="utf-8"?>
<OAI-PMH xmlns="http://www.openarchives.org/OAI/2.0/">
  <responseDate>2026-08-03T15:27:33Z</responseDate>
  <request verb="GetRecord" metadataPrefix="oai_dc" identifier="oai:kobv.de-opus4-zib:8138">https://opus4.kobv.de/opus4-zib/oai</request>
  <error code="idDoesNotExist">The value of the identifier argument is unknown or illegal in this repository.</error>
</OAI-PMH>`;

const SCHNITTSTELLE = [
  {
    name: "DNB-SRU: Mapping mit Rollen-Klammer und ISBN",
    reg: () => F.oaiDcAusXml(DNB_SRU),
    pruefe: (r) => [
      [!!r, "kein Datensatz erkannt"],
      [r && /Deleuze/.test(r.title), `Titel=${r && r.title}`],
      // Die DNB haengt "[Verfasser]" an — das ist eine Rolle, kein Name.
      [r && r.authors[0] === "Pflaum, Michael", `Autor=${r && r.authors[0]}`],
      [r && r.year === "2023", `Jahr=${r && r.year}`],
      [r && r.isbn === "978-3-7347-2612-5", `ISBN=${r && r.isbn} (Preis-Anhaengsel darf nicht mit)`],
      [r && r.art === "Buch", `art=${r && r.art} (ISBN-13 muss Buch ergeben)`],
      [r && r.language === "de", `Sprache=${r && r.language} (ger -> de)`],
    ],
  },
  {
    name: "OPUS-OAI: Mapping mit Namespace-Praefix oai_dc:",
    reg: () => F.oaiDcAusXml(OPUS_OAI),
    pruefe: (r) => [
      [!!r, "kein Datensatz erkannt"],
      [r && r.title.startsWith("Efficient Numerical Simulation"), `Titel=${r && r.title}`],
      [r && r.authors.length === 2 && r.authors[0] === "Deuflhard, Peter", `Autoren=${r && JSON.stringify(r.authors)}`],
      [r && r.year === "1986", `Jahr=${r && r.year}`],
      [r && r.art === "Preprint", `art=${r && r.art}`],
    ],
  },
  {
    name: "OAI-Fehler idDoesNotExist ist kein Datensatz",
    reg: () => F.oaiDcAusXml(OAI_FEHLER),
    pruefe: (r) => [[r === null, `Fehler als Satz gewertet: ${r && r.title}`]],
  },
  {
    name: "Leerer SRU-Treffer ist kein Datensatz",
    reg: () => F.oaiDcAusXml(`<searchRetrieveResponse><numberOfRecords>0</numberOfRecords></searchRetrieveResponse>`),
    pruefe: (r) => [[r === null, "leerer Treffer als Satz gewertet"]],
  },
  {
    name: "Adressmuster der Plattformen werden erkannt",
    reg: () => true,
    pruefe: () => {
      const dnb = F.plattformAbfrage("https://d-nb.info/1279437049");
      const opus = F.plattformAbfrage("https://opus4.kobv.de/opus4-zib/frontdoor/index/index/docId/8138");
      const psych = F.plattformAbfrage("https://psycharchives.org/handle/20.500.12034/2487");
      const fremd = F.plattformAbfrage("https://example.org/1279437049");
      return [
        [dnb && dnb.abruf.includes("services.dnb.de/sru/dnb") && dnb.abruf.includes("idn%3D1279437049"),
          `DNB: ${dnb && dnb.abruf}`],
        [opus && opus.abruf === "https://opus4.kobv.de/opus4-zib/oai?verb=GetRecord&identifier=oai%3Akobv.de-opus4-zib%3A8138&metadataPrefix=oai_dc",
          `OPUS: ${opus && opus.abruf}`],
        [psych && psych.abruf.includes("oai%3Apsycharchives.org%3A20.500.12034%2F2487"),
          `PsychArchives: ${psych && psych.abruf}`],
        [fremd === null, "fremde Adresse faelschlich erkannt"],
      ];
    },
  },
];
// --- Kennung aus der Adresse (Issues #16/#17) ------------------------------
// SSRN, OECD und EUR-Lex tragen ihre Kennung in anderer Form in der Adresse
// als das DOI-Muster 10.xxxx/. Die Uebersetzungen sind am 04.08.2026 live
// verifiziert:
//   - 10.2139/ssrn.3529682 gegen api.crossref.org (Brady/Bass 2019)
//   - 10.1787/a1689dc5-en gegen api.crossref.org (OECD Digital Economy
//     Outlook 2024 Vol. 1)
//   - CELEX 32016R0679 gegen publications.europa.eu/resource/celex — die
//     Fixture unten ist die WORTLICHE, vollstaendige Antwort auf
//     resource/celex/32016R0679.ENG mit Accept: application/rdf+xml.
// Befund dabei: der Abruf OHNE Sprachsuffix liefert ein 61-MB-
// Verknuepfungsobjekt ohne ein einziges Titelfeld; Titel steht nur in der
// sprachlichen Fassung (.ENG/.DEU, knapp 4 KB). Ein Datumsfeld traegt auch
// sie nicht — das Jahr steht im amtlichen Titel.

const CELLAR_ENG = `<rdf:RDF
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:j.0="http://publications.europa.eu/ontology/cdm#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:j.1="http://www.w3.org/2004/02/skos/core#"
    xmlns:j.2="http://publications.europa.eu/ontology/cdm/cmr#" >
  <rdf:Description rdf:about="http://publications.europa.eu/resource/celex/32016R0679.ENG">
    <rdf:type rdf:resource="http://publications.europa.eu/ontology/cdm#expression"/>
    <j.0:expression_title_short rdf:datatype="http://www.w3.org/2001/XMLSchema#string">gdpr, personal data, personal data protection</j.0:expression_title_short>
    <j.0:title_short rdf:datatype="http://www.w3.org/2001/XMLSchema#string">gdpr, personal data, personal data protection</j.0:title_short>
  </rdf:Description>
  <rdf:Description rdf:about="http://publications.europa.eu/resource/cellar/3e485e15-11bd-11e6-ba9a-01aa75ed71a1.0006">
    <owl:sameAs rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.RNG"/>
    <owl:sameAs rdf:resource="http://publications.europa.eu/resource/uriserv/OJ.L_.2016.119.01.0001.01.ENG"/>
    <owl:sameAs rdf:resource="http://publications.europa.eu/resource/celex/32016R0679.ENG"/>
    <owl:sameAs rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG"/>
    <j.2:lang rdf:datatype="http://www.w3.org/2001/XMLSchema#language">en</j.2:lang>
    <j.2:lang rdf:datatype="http://www.w3.org/2001/XMLSchema#language">eng</j.2:lang>
    <j.2:lastModificationDate rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2025-02-05T16:25:55.607+01:00</j.2:lastModificationDate>
  </rdf:Description>
  <rdf:Description rdf:about="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG">
    <j.0:expression_manifested_by_manifestation rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG.fmx4"/>
    <j.0:uses rdf:resource="http://publications.europa.eu/resource/authority/language/ENG"/>
    <j.0:expression_manifested_by_manifestation rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG.xhtml"/>
    <j.0:expression_belongs_to_work rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001"/>
    <j.0:belongs_to rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001"/>
    <j.0:expression_uses_language rdf:resource="http://publications.europa.eu/resource/authority/language/ENG"/>
    <rdf:type rdf:resource="http://publications.europa.eu/ontology/cdm#expression"/>
    <j.0:title>Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation) (Text with EEA relevance)</j.0:title>
    <j.0:expression_title>Regulation (EU) 2016/679 of the European Parliament and of the Council of 27 April 2016 on the protection of natural persons with regard to the processing of personal data and on the free movement of such data, and repealing Directive 95/46/EC (General Data Protection Regulation) (Text with EEA relevance)</j.0:expression_title>
    <j.0:expression_manifested_by_manifestation rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG.pdfa1a"/>
  </rdf:Description>
  <rdf:Description rdf:about="http://publications.europa.eu/resource/authority/language/ENG">
    <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>
    <rdf:type rdf:resource="http://publications.europa.eu/ontology/cdm#language"/>
    <j.1:inScheme rdf:resource="http://publications.europa.eu/resource/authority/language"/>
    <j.0:language_used_by_expression rdf:resource="http://publications.europa.eu/resource/oj/JOL_2016_119_R_0001.ENG"/>
  </rdf:Description>
</rdf:RDF>`;

const KENNUNG = [
  {
    name: "SSRN: abstract_id wird zu 10.2139/ssrn.<id> (Issue #16)",
    reg: () => F.kennungAusAdresse("https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3529682"),
    pruefe: (k) => [
      [k && k.doi === "10.2139/ssrn.3529682", `doi=${k && k.doi}`],
    ],
  },
  {
    name: "OECD: _<slug>-<sprache>.html wird zu 10.1787/<slug> (Issue #16)",
    reg: () => F.kennungAusAdresse("https://www.oecd.org/en/publications/oecd-digital-economy-outlook-2024-volume-1_a1689dc5-en.html"),
    pruefe: (k) => [
      [k && k.doi === "10.1787/a1689dc5-en", `doi=${k && k.doi}`],
    ],
  },
  {
    name: "EUR-Lex: CELEX aus dem uri-Parameter (Issue #17)",
    reg: () => F.kennungAusAdresse("https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679"),
    pruefe: (k) => [
      [k && k.celex === "32016R0679", `celex=${k && k.celex}`],
      [k && k.sprache === "EN", `sprache=${k && k.sprache} (steht im Pfad)`],
    ],
  },
  {
    name: "SSRN ohne abstract_id: kein Rateversuch",
    reg: () => F.kennungAusAdresse("https://papers.ssrn.com/sol3/papers.cfm"),
    pruefe: (k) => [[k === null, `unerwartet uebersetzt: ${k && JSON.stringify(k)}`]],
  },
  {
    name: "oecd.org ohne Slug-Form: kein Rateversuch",
    reg: () => F.kennungAusAdresse("https://www.oecd.org/en/about.html"),
    pruefe: (k) => [[k === null, `unerwartet uebersetzt: ${k && JSON.stringify(k)}`]],
  },
  {
    name: "Fremder Host mit aehnlicher Form bleibt unuebersetzt",
    reg: () => true,
    pruefe: () => [
      [F.kennungAusAdresse("https://example.org/x_a1689dc5-en.html") === null, "oecd-aehnlicher Pfad auf fremdem Host"],
      [F.kennungAusAdresse("https://notssrn.com/sol3/papers.cfm?abstract_id=3529682") === null, "ssrn-aehnlicher Host"],
      [F.kennungAusAdresse("https://eur-lex.europa.eu.example.com/legal-content/EN/TXT/?uri=CELEX%3A32016R0679") === null, "eur-lex im Hostnamen versteckt"],
    ],
  },
  {
    name: "Cellar-RDF: Titel, Jahr und Traeger aus der echten Antwort",
    reg: () => F.cellarAusXml(CELLAR_ENG),
    pruefe: (r) => [
      [!!r, "kein Datensatz erkannt"],
      [r && /^Regulation \(EU\) 2016\/679/.test(r.title), `Titel=${r && (r.title || "").slice(0, 60)}`],
      [r && /General Data Protection Regulation/.test(r.title), "Titel abgeschnitten"],
      [r && r.year === "2016", `Jahr=${r && r.year} (steht im Titel, die Fassung traegt kein Datumsfeld)`],
      [r && r.art === "Rechtsquelle", `art=${r && r.art}`],
      [r && r.publisher === "Europaeische Union", `Traeger=${r && r.publisher}`],
      [r && r.language === "en", `Sprache=${r && r.language}`],
      // title_short ("gdpr, personal data, ...") darf nicht als Titel
      // durchgehen — es ist ein Schlagwortfeld, kein Werktitel.
      [r && !/^gdpr,/.test(r.title), `Kurztitel als Titel: ${r && r.title}`],
    ],
  },
  {
    name: "Cellar-RDF kaputt oder ohne Titel: kein Datensatz",
    reg: () => true,
    pruefe: () => [
      [F.cellarAusXml("") === null, "leere Antwort als Satz gewertet"],
      [F.cellarAusXml("<rdf:RDF><rdf:Description><j.0:title_short>nur ein Schlagwort</j.0:title_short></rdf:Description></rdf:RDF>") === null,
        "title_short allein ist kein Datensatz"],
      [F.cellarAusXml("gar kein XML") === null, "Muell als Satz gewertet"],
    ],
  },
];


let gruen = 0, rot = 0;
for (const f of FAELLE) {
  const q = F.quelleAusHtml(f.html, f.url);
  const r = F.risAus(q), b = F.bibtexAus(q);
  const ergebnisse = f.pruefe(q, r, b);
  const fehler = ergebnisse.filter(([ok]) => !ok);
  if (fehler.length === 0) { gruen++; console.log(`  ok    ${f.name}`); }
  else {
    rot++;
    console.log(`  FEHL  ${f.name}`);
    for (const [, wie] of fehler) console.log(`          ${wie}`);
  }
}
for (const f of SCHNITTSTELLE.concat(KENNUNG)) {
  const reg = f.reg();
  const fehler = f.pruefe(reg).filter(([ok]) => !ok);
  if (fehler.length === 0) { gruen++; console.log(`  ok    ${f.name}`); }
  else {
    rot++;
    console.log(`  FEHL  ${f.name}`);
    for (const [, wie] of fehler) console.log(`          ${wie}`);
  }
}
console.log(`\n  ${gruen} von ${FAELLE.length + SCHNITTSTELLE.length + KENNUNG.length} bestanden${rot ? `, ${rot} fehlgeschlagen` : ""}`);
process.exit(rot ? 1 : 0);
