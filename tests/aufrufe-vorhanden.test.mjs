/* Prueft, dass beide Fassungen dieselben Funktionen haben.
 *
 * Anlass (18.08.2026): Beim Einbau des Artikelwegs wurden drei Hilfsfunktionen
 * nur in die Chrome-Fassung geschrieben — dateinamenBauen, belegeAblegen,
 * beilageAblegen. Die Firefox-Fassung rief sie trotzdem auf. Beim ersten Klick
 * auf "Artikel" waere dort ein ReferenceError geflogen, und zwar erst zur
 * Laufzeit: JavaScript laesst unbekannte Namen bis zum Aufruf durchgehen.
 * Weder `node --check` noch der Ladeketten-Test finden das — die Datei ist
 * syntaktisch einwandfrei und laedt fehlerfrei.
 *
 * Zur Form dieser Pruefung: Der erste Entwurf wollte ALLE Aufrufe gegen ALLE
 * Definitionen halten und dafuer Kommentare und Zeichenketten wegschneiden.
 * Das ging zweimal schief. Erst las er deutsche Prosa als Quelltext ("…, nicht
 * (wie frueher)…" wurde zum Aufruf von `nicht(`) und meldete zwanzig
 * Fehlalarme. Dann zerstoerte der Kommentar-Entferner den Code selbst: Die
 * Regel fuer Zeilenkommentare verschluckte das "//" in "https://" mitsamt dem
 * Rest der Zeile, danach hingen die Anfuehrungszeichen, und `dateinamenBauen`
 * galt in BEIDEN Fassungen als nicht vorhanden. Der Test wurde dadurch gruen —
 * er verglich zwei gleich falsche Messungen.
 *
 * Deshalb jetzt eng und ohne Vorverarbeitung: Eine Funktionsdefinition steht
 * am Zeilenanfang. Danach wird gesucht, sonst nach nichts.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HIER = dirname(fileURLToPath(import.meta.url));
const WURZEL = join(HIER, "..");

let fehler = 0;
const pruefe = (b, t) => {
  if (b) console.log("#   ok   " + t);
  else { console.log("# FEHL " + t); fehler++; }
};

/** Steht in dieser Datei eine Definition dieser Funktion, am Zeilenanfang? */
function definiert(quelle, name) {
  return new RegExp(`^\\s*(async\\s+)?function\\s+${name}\\s*\\(`, "m").test(quelle);
}

/** Wird der Name aufgerufen — ausserhalb von Kommentarzeilen? */
function ruftAuf(quelle, name) {
  const muster = new RegExp(`(^|[^.\\w$])${name}\\s*\\(`);
  return quelle.split("\n").some(zeile => {
    const t = zeile.trim();
    if (t.startsWith("*") || t.startsWith("//") || t.startsWith("/*")) return false;
    return muster.test(zeile);
  });
}

test("Beide Fassungen tragen dieselben Funktionen", () => {
  const ff = readFileSync(join(WURZEL, "background.js"), "utf8");
  const ch = readFileSync(join(WURZEL, "chrome-mv3", "background.js"), "utf8");

  /* Erst die Gegenprobe: Findet die Suche ueberhaupt etwas?
   *
   * Ohne sie waere ein Messfehler nicht von einem Gleichstand zu
   * unterscheiden — genau daran ist der vorige Entwurf gescheitert. */
  pruefe(definiert(ff, "captureFullPage") && definiert(ch, "captureFullPage"),
         "Gegenprobe: captureFullPage wird in beiden Fassungen gefunden");
  pruefe(!definiert(ff, "gibtEsNichtXyz"),
         "Gegenprobe: ein erfundener Name wird NICHT gefunden");

  const gemeinsam = [
    "dateinamenBauen", "beilageAblegen", "belegeAblegen", "artikelAlsDatei",
    "captureFullPage", "captureFullPageInner", "runOnActiveTab", "getSettings",
    "sanitizeFilename", "siteFromUrl", "nowStamp", "nextCounter",
    "ensureContentInjected", "fertigTon", "waitForDownloadComplete",
  ];
  for (const name of gemeinsam) {
    const a = definiert(ff, name), b = definiert(ch, name);
    pruefe(a === b, `${name}: firefox=${a} chrome=${b}`);
  }

  /* Der Vektorweg ist Chromium-eigen und darf NUR dort stehen.
   * In Firefox gibt es kein DevTools-Protokoll; der Aufruf ist deshalb mit
   * typeof abgesichert, und genau das wird hier festgehalten. */
  pruefe(!definiert(ff, "vektorAufnahme") && definiert(ch, "vektorAufnahme"),
         "vektorAufnahme: nur in der Chrome-Fassung");
  pruefe(!ruftAuf(ff, "vektorAufnahme") || /typeof vektorAufnahme === "function"/.test(ff),
         "firefox ruft vektorAufnahme nur nach typeof-Pruefung auf");

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Fassungen: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
