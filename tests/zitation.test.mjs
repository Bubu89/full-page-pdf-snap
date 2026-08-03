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
                       "\n return { quelleAusHtml, risAus, bibtexAus };")();

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
console.log(`\n  ${gruen} von ${FAELLE.length} bestanden${rot ? `, ${rot} fehlgeschlagen` : ""}`);
process.exit(rot ? 1 : 0);
