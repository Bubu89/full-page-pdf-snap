/* Jede Aufrufstelle muss die Schalter mitgeben.
 *
 * Anlass (18.08.2026): Die Chrome-Fassung ruft belegeAblegen an DREI Stellen
 * auf — Hauptweg, Vektorweg, Markdown-Weg —, die Firefox-Fassung an zwei.
 * Beim Einbau der beiden Beilagen-Schalter bekam nur der Hauptweg sie mit.
 *
 * Der Fehler waere von aussen nicht als Fehler erschienen, sondern als
 * Eigensinn: In `belegeAblegen` steht `z.risDatei !== false`. Fehlt der Wert,
 * ist er `undefined`, und `undefined !== false` ist wahr — die Datei wird
 * abgelegt. Wer sie in den Einstellungen abwaehlt, bekommt sie ueber diese
 * beiden Wege trotzdem. Ein Haken, der sich setzen laesst und nichts bewirkt.
 *
 * Geprueft wird deshalb: Jeder Aufruf von belegeAblegen fuehrt beide Schalter
 * mit, in beiden Fassungen.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

/** Der Argumentblock eines Aufrufs — von der Klammer bis zum passenden Ende. */
function aufrufBlock(text, ab) {
  let tiefe = 0;
  for (let i = ab; i < text.length; i++) {
    if (text[i] === "(") tiefe++;
    else if (text[i] === ")") { tiefe--; if (tiefe === 0) return text.slice(ab, i + 1); }
  }
  return "";
}

test("Jeder Aufruf der Beilagen-Ablage führt beide Schalter mit", () => {
  for (const [name, datei] of [["firefox", "background.js"],
                               ["chrome", join("chrome-mv3", "background.js")]]) {
    const bg = readFileSync(join(WURZEL, datei), "utf8");

    /* Gesucht wird "await belegeAblegen(" — der AUFRUF.
     *
     * Ein erster Versuch suchte nur den Namen und zaehlte damit auch die
     * Stelle mit, an der ein Kommentar erklaert, warum es die Funktion gibt.
     * Der Pruefer meldete daraufhin einen Fehler in einem Fliesstext. Dieselbe
     * Falle wie bei der .links.json weiter oben: Wer auf die Zeichenkette
     * prueft statt auf die Sache, verbietet am Ende die Erklaerung. */
    const stellen = [];
    let i = 0;
    while ((i = bg.indexOf("await belegeAblegen(", i)) !== -1) {
      stellen.push(i + 6);
      i += 20;
    }

    /* Gegenprobe: Findet die Suche ueberhaupt Aufrufe? Ohne sie waere eine
     * leere Liste von "alles in Ordnung" nicht zu unterscheiden. */
    p(stellen.length >= 2, `${name}: Aufrufstellen gefunden (${stellen.length})`);

    for (const [nr, ab] of stellen.entries()) {
      const block = aufrufBlock(bg, bg.indexOf("(", ab));
      const zeile = bg.slice(0, ab).split("\n").length;
      p(/risDatei:\s*settings\./.test(block),
        `${name}: Aufruf ${nr + 1} (Zeile ${zeile}) gibt risDatei mit`);
      p(/zitatDatei:\s*settings\./.test(block),
        `${name}: Aufruf ${nr + 1} (Zeile ${zeile}) gibt zitatDatei mit`);
    }

    /* Und die Bedingung, auf die sich das alles stuetzt: Beide Schalter
     * haengen am Zitationsschalter des Menues. */
    const treffer = bg.match(/risDatei:\s*settings\.sourceMetadata !== false && settings\.risDatei !== false/g) || [];
    p(treffer.length === stellen.length,
      `${name}: alle ${stellen.length} Aufrufe koppeln an sourceMetadata (${treffer.length})`);
  }

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Beilagen-Schalter: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
