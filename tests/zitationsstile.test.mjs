/* Prueft die fertigen Eintraege fuers Literaturverzeichnis.
 *
 * Jede Pruefung hier steht fuer einen Fehler, der beim Bauen tatsaechlich
 * dastand — nicht fuer einen, den man sich ausdenken kann:
 *
 *   "66 (3)" statt "66(3)"   — zusammen(teile, "") nahm den leeren String als
 *                              "nicht angegeben" und setzte ein Leerzeichen.
 *   "o. J.."                 — an eine Angabe, die auf einen Punkt endet,
 *                              wurde ein zweiter gehaengt.
 *   "mller2024digitale"      — der BibTeX-Schluessel warf Umlaute ersatzlos weg.
 *   "Zeitschrift. vol. 66"   — MLA trennt Werk und Band mit Komma, nicht Punkt.
 *
 * Ein Fehler im Literaturverzeichnis faellt erst bei der Abgabe auf. Deshalb
 * werden sie hier festgehalten, statt sich auf den Augenschein zu verlassen.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HIER = dirname(fileURLToPath(import.meta.url));
const WURZEL = join(HIER, "..");

// Die Datei laedt sich selbst in globalThis — kein Modulsystem, weil sie im
// Hintergrunddienst per importScripts gelesen wird.
new Function(readFileSync(join(WURZEL, "zitate.js"), "utf8"))();
const Z = globalThis.PageShotZitate;

let fehler = 0;
const pruefe = (bedingung, text) => {
  if (bedingung) { console.log("#   ok   " + text); }
  else { console.log("# FEHL " + text); fehler++; }
};

const AUFSATZ = {
  art: "Zeitschriftenaufsatz",
  autoren: ["Müller, Klaus", "Anna Schmidt", "Lee, Ji-Woo"],
  titel: "Digitale Belegführung in der Steuerprüfung",
  jahr: "2024", datum: "2024-06-23",
  journal: "Zeitschrift für Wirtschaftsinformatik",
  band: "66", heft: "3", seiteVon: "211", seiteBis: "229",
  doi: "10.1007/s11576-024-01234-5", issn: "1861-8936",
  verlag: "Springer", url: "https://example.org/artikel/123",
  abrufzeit: "2026-08-17T14:25:20+02:00", abrufdatum: "2026-08-17",
  herkunft: "citation_*-Tags", vollstaendig: true,
};

const OHNE_ANGABEN = {
  art: "Webseite", autoren: [], titel: "Eine Seite ohne Angaben",
  jahr: "", datum: "", verlag: "Beispiel AG",
  url: "https://example.org/seite",
  abrufzeit: "2026-08-17T14:25:20+02:00", abrufdatum: "2026-08-17",
  vollstaendig: false,
};

test("Zitationsstile", () => {
  // --- Band und Heft ohne Fuge -------------------------------------------
  const apa = Z.apa(AUFSATZ, "de");
  pruefe(apa.includes("66(3)"), `APA setzt Band(Heft) ohne Leerzeichen — "${apa.match(/66[^,]*/)?.[0]}"`);
  pruefe(!apa.includes("66 (3)"), "APA: kein Leerzeichen zwischen Band und Heft");

  // --- Kein doppelter Punkt bei fehlender Jahresangabe --------------------
  for (const sprache of ["de", "en"]) {
    for (const [name, bauen] of Z.STILE) {
      const eintrag = bauen(OHNE_ANGABEN, sprache);
      pruefe(!/\.\./.test(eintrag), `${name}/${sprache}: kein doppelter Punkt`);
    }
  }

  // --- BibTeX-Schluessel behaelt den Namen --------------------------------
  const bib = Z.bibtex(AUFSATZ);
  pruefe(/@article\{mueller2024/.test(bib),
         `BibTeX-Schluessel überträgt den Umlaut — "${bib.match(/@article\{([^,]*)/)?.[1]}"`);
  pruefe(bib.includes("pages = {211--229}"), "BibTeX: Seitenbereich mit doppeltem Strich");
  pruefe(bib.includes("Müller, Klaus and Schmidt, Anna and Lee, Ji-Woo"),
         "BibTeX: Verfasser mit and verbunden, Nachname zuerst");

  // --- MLA trennt Werk und Band mit Komma ---------------------------------
  const mla = Z.mla(AUFSATZ, "en");
  pruefe(mla.includes("Wirtschaftsinformatik, vol. 66"),
         "MLA: Komma zwischen Werk und Bandangabe");

  // --- Der bestaendige Verweis hat Vorrang --------------------------------
  for (const [name, bauen] of [["APA", Z.apa], ["Harvard", Z.harvard], ["DIN", Z.din]]) {
    const eintrag = bauen(AUFSATZ, "de");
    pruefe(eintrag.includes("doi.org/10.1007"), `${name}: nennt den DOI, nicht nur die Adresse`);
  }

  // --- Verfasserregeln ----------------------------------------------------
  pruefe(Z.apa(AUFSATZ, "de").startsWith("Müller, K., Schmidt, A., & Lee, J."),
         "APA: Initialen, letzter mit &");
  pruefe(Z.mla(AUFSATZ, "de").startsWith("Müller, Klaus, u. a."),
         "MLA/de: ab drei Verfassern u. a.");
  pruefe(Z.mla(AUFSATZ, "en").startsWith("Müller, Klaus, et al."),
         "MLA/en: ab drei Verfassern et al.");
  pruefe(Z.din(AUFSATZ, "de").startsWith("MÜLLER, Klaus; SCHMIDT"),
         "DIN: Nachname in Großbuchstaben, Semikolon als Trenner");

  // --- Nichts erfinden ----------------------------------------------------
  const ohneJahr = Z.apa(OHNE_ANGABEN, "de");
  pruefe(ohneJahr.includes("o. J."), "Fehlendes Jahr wird als o. J. ausgewiesen");
  pruefe(!ohneJahr.includes("2026)"), "Das Abrufjahr wird NICHT als Erscheinungsjahr ausgegeben");

  // --- Die Namenszerlegung ------------------------------------------------
  pruefe(Z.namenTeilen("Müller, Klaus").nach === "Müller", "Mit Komma: Nachname vorn");
  pruefe(Z.namenTeilen("Anna Schmidt").nach === "Schmidt", "Ohne Komma: letztes Wort ist Nachname");
  pruefe(Z.namenTeilen("Cher").nach === "Cher", "Einzelner Name bleibt stehen");

  // --- Die Datei ----------------------------------------------------------
  const datei = Z.belegDatei(AUFSATZ, { pdfDatei: "x.pdf", pruefsumme: "abc", version: "2.35.3" }, "de");
  for (const stil of ["APA 7", "MLA 9", "Chicago", "Harvard", "DIN 1505-2", "ISO 690"]) {
    pruefe(datei.includes(stil + ":"), `Belegdatei führt ${stil}`);
  }
  pruefe(datei.includes("IN IHRER SPRACHE") && datei.includes("AUF ENGLISCH"),
         "Belegdatei führt die eigene Sprache und Englisch");
  pruefe(datei.includes("BIBTEX"), "Belegdatei führt BibTeX");
  pruefe(datei.includes("VERFASSER, WIE DIE SEITE SIE NENNT"),
         "Belegdatei legt die Rohform der Namen offen");

  /* Der Hinweis auf die Dokumenteigenschaften.
   *
   * Wer diese Datei einem Sprachmodell vorlegt, soll erfahren, dass dieselben
   * Angaben maschinenlesbar im PDF stehen — sonst wird Fliesstext geparst,
   * obwohl ein sauberer Datensatz danebenliegt. */
  pruefe(datei.includes("FÜR KI-WERKZEUGE"), "Belegdatei nennt den Abschnitt für KI-Werkzeuge");
  pruefe(/Dokumenteigenschaften/.test(datei) && /XMP/.test(datei),
         "Belegdatei verweist auf Dokumenteigenschaften und XMP im PDF");
  pruefe(datei.indexOf("FÜR KI-WERKZEUGE") < datei.indexOf("APA 7:"),
         "Der KI-Hinweis steht VOR den Einträgen, nicht am Ende");

  /* Die Sprache der Oberflaeche bestimmt die Ausgabe. */
  const jp = Z.belegDatei(AUFSATZ, {}, "ja");
  pruefe(jp.includes("参照日"), "Japanisch: Abrufwort übersetzt");

  /* Die Beschriftung der Belegdatei — nicht nur die Zitierweisen.
   *
   * Bis 2.35.17 kannte die Beschriftungstabelle nur Deutsch und Englisch;
   * alle uebrigen sieben Sprachen fielen still auf Englisch zurueck. Ein
   * frueherer Pruefer hielt genau das als Erwartung fest und machte den
   * Mangel damit unsichtbar: Er gruente, WEIL die Uebersetzung fehlte.
   *
   * Geprueft wird deshalb je Sprache ein Wort, das es nur dort gibt, und
   * zusaetzlich, dass die englische Fassung des Kopfes NICHT erscheint. */
  for (const [sp, eigen] of [
    ["ja", "AI ツール向け"], ["es", "PARA HERRAMIENTAS DE IA"],
    ["fr", "POUR LES OUTILS D’IA"], ["it", "PER STRUMENTI DI IA"],
    ["pt_BR", "PARA FERRAMENTAS DE IA"], ["ru", "ДЛЯ ИИ-ИНСТРУМЕНТОВ"],
    ["zh_CN", "供 AI 工具使用"], ["de", "FÜR KI-WERKZEUGE"],
  ]) {
    const d = Z.belegDatei(AUFSATZ, {}, sp);
    pruefe(d.includes(eigen), `${sp}: Blattkopf in der eigenen Sprache`);
    pruefe(!d.includes("FOR AI TOOLS"), `${sp}: kein Rückfall auf Englisch`);
  }
  /* Gegenprobe: Englisch MUSS den englischen Kopf tragen. Ohne sie wuerde
   * eine Tabelle, die gar nichts findet, alle Pruefungen oben bestehen. */
  pruefe(Z.belegDatei(AUFSATZ, {}, "en").includes("FOR AI TOOLS"),
         "Gegenprobe: Englisch trägt den englischen Kopf");
  const es = Z.belegDatei(AUFSATZ, {}, "es");
  pruefe(es.includes("consultado el"), "Spanisch: Abrufwort übersetzt");
  pruefe(!/,\s+from\s+http/.test(es), "Spanisch: keine englische Präposition mehr");
  const at = Z.belegDatei(AUFSATZ, {}, "de-AT");
  pruefe(at.includes("17.08.2026") || at.includes("abgerufen am"),
         "de-AT fällt auf Deutsch zurück, nicht auf Englisch");
  const nur_en = Z.belegDatei(AUFSATZ, {}, "en");
  pruefe(!nur_en.includes("IN YOUR LANGUAGE"),
         "Bei englischer Oberfläche steht die Fassung nicht doppelt da");

  /* Das kaufmaennische Und ist ein Symbol, keine Vokabel. */
  for (const sp of ["ja", "zh_CN", "ru", "es", "fr"]) {
    pruefe(Z.apa(AUFSATZ, sp).includes("& Lee"), `APA/${sp}: & bleibt & (kein übersetztes Zeichen)`);
  }

  const lueckenhaft = Z.belegDatei(OHNE_ANGABEN, {});
  pruefe(lueckenhaft.includes("ACHTUNG"),
         "Unvollständige Angaben werden in der Datei benannt, nicht verschwiegen");

  console.log(fehler === 0
    ? `# alle Prüfungen bestanden`
    : `# Zitationsstile: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Prüfungen fehlgeschlagen`);
});
