/* Prueft, dass jede gespeicherte Einstellung auch gelesen wird.
 *
 * Anlass (18.08.2026): Querformat umgestellt, Datei kam als A4 hoch heraus,
 * und im Popup stand weiter "Querformat". Ein Bedienelement, das speichert und
 * nichts bewirkt — von aussen nicht von einem kaputten Ausgabeweg zu
 * unterscheiden, und deshalb dreimal als "geht immer noch nicht" gemeldet.
 *
 * Die Ursache steckt in einer Eigenheit der Speicher-Schnittstelle:
 *
 *     browser.storage.local.get(defs)
 *
 * liest AUSSCHLIESSLICH die Schluessel, die in `defs` vorkommen. Ein Wert, den
 * das Popup speichert, der aber in den Voreinstellungen fehlt, wird nie
 * zurueckgegeben — kein Fehler, keine Warnung, er ist schlicht nicht da.
 *
 * Sechs Schluessel waren betroffen: druckPapier, druckQuer, artikelPapier,
 * artikelQuerWahl, artikelSchriftgroesse, artikelAlsText.
 *
 * Geprueft wird deshalb beides gegeneinander: Was das Popup schreibt, muss in
 * den Voreinstellungen stehen — und was die Aufnahme liest, ebenfalls.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const pruefe = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

/** Die Schluessel aus DEFAULTS_DESKTOP. */
function voreinstellungen(bg) {
  const von = bg.indexOf("const DEFAULTS_DESKTOP = {");
  const bis = bg.indexOf("const DEFAULTS_ANDROID_OVERRIDES", von);
  const block = bg.slice(von, bis);
  return new Set([...block.matchAll(/^\s*([a-zA-Z][\w]*)\s*:/gm)].map(m => m[1]));
}

test("Jede gespeicherte Einstellung steht in den Voreinstellungen", () => {
  const popup = readFileSync(join(WURZEL, "popup.js"), "utf8");
  const optionen = readFileSync(join(WURZEL, "options.js"), "utf8");

  for (const [name, datei] of [["firefox", "background.js"],
                               ["chrome", join("chrome-mv3", "background.js")]]) {
    const bg = readFileSync(join(WURZEL, datei), "utf8");
    const defs = voreinstellungen(bg);

    /* Gegenprobe zuerst: Findet die Suche ueberhaupt etwas?
     * Ohne sie waere eine leere Menge nicht von "alles in Ordnung" zu
     * unterscheiden — derselbe Fehler, der einen frueheren Pruefer in dieser
     * Reihe gruen werden liess, obwohl er nichts gemessen hat. */
    pruefe(defs.size > 15, `${name}: die Voreinstellungen sind lesbar (${defs.size} Schluessel)`);
    pruefe(defs.has("jpegQuality"), `${name}: Gegenprobe — jpegQuality wird gefunden`);
    pruefe(!defs.has("gibtEsNichtXyz"), `${name}: Gegenprobe — Erfundenes wird nicht gefunden`);

    /* Was das Popup in seiner Feldtabelle speichert. */
    const ausPopup = [...popup.matchAll(/schluessel:\s*"([A-Za-z0-9_]+)"/g)].map(m => m[1]);
    pruefe(ausPopup.length >= 6, `${name}: Popup-Feldtabelle gefunden (${ausPopup.length} Felder)`);
    for (const k of new Set(ausPopup)) {
      pruefe(defs.has(k),
        `${name}: "${k}" wird vom Popup gespeichert und steht in den Voreinstellungen`);
    }

    /* Und was die Einstellungsseite speichert. */
    const ausOptionen = [...optionen.matchAll(/schluessel:\s*"([A-Za-z0-9_]+)"/g)].map(m => m[1]);
    for (const k of new Set(ausOptionen)) {
      if (k === "counter") continue;   // Zaehlerstand, kein Einstellwert
      pruefe(defs.has(k),
        `${name}: "${k}" wird von den Einstellungen gespeichert und steht in den Voreinstellungen`);
    }

    /* Und umgekehrt: Was die Aufnahme aus settings liest, muss lesbar sein. */
    const gelesen = new Set([...bg.matchAll(/settings\.([a-zA-Z][\w]*)/g)].map(m => m[1]));
    // Werte, die zur Laufzeit gesetzt werden statt gespeichert zu sein.
    /* Werte, die zur Laufzeit gesetzt werden statt gespeichert zu sein.
     * Sie entstehen aus einer gespeicherten Einstellung — randPt etwa aus
     * druckRandMm — und haben deshalb keinen eigenen Platz im Speicher. */
    const ZURLAUFZEIT = new Set(["region", "blattPt", "pageVerhaeltnis", "randPt"]);
    for (const k of gelesen) {
      if (ZURLAUFZEIT.has(k)) continue;
      pruefe(defs.has(k),
        `${name}: settings.${k} wird gelesen und steht in den Voreinstellungen`);
    }
  }

  /* Die Gegenrichtung — sie fehlte, und genau dort schlug es zu.
   *
   * Bisher wurde nur geprueft: Was die Einstellungsseite speichert, muss der
   * Hintergrunddienst kennen. Die Seite hat aber eine EIGENE Vorgabeliste,
   * und auch die entscheidet, was storage.local.get() zurueckgibt. In 2.36.0
   * fehlten dort "zitatDatei" und "risDatei": Beide Haken standen leer, und
   * beim Speichern schrieb die Seite das leere Haekchen als "aus" zurueck.
   * Wer die Einstellungen nur geoeffnet hatte, verlor die Beilagen.
   *
   * Jedes Feld der Seite muss also auch in IHRER Vorgabeliste stehen. */
  {
    const optionen = readFileSync(join(WURZEL, "options.js"), "utf8");
    const von = optionen.indexOf("const DEFAULTS = {");
    const bis = optionen.indexOf("\n};", von);
    const block = optionen.slice(von, bis);
    const eigene = new Set([...block.matchAll(/^\s*([a-zA-Z][\w]*)\s*:/gm)].map(m => m[1]));

    pruefe(eigene.size > 15, `Einstellungsseite: eigene Vorgaben lesbar (${eigene.size})`);
    pruefe(eigene.has("jpegQuality"), "Einstellungsseite: Gegenprobe — jpegQuality gefunden");
    pruefe(!eigene.has("gibtEsNichtXyz"), "Einstellungsseite: Gegenprobe — Erfundenes nicht gefunden");

    const felder = [...optionen.matchAll(/\{\s*id:\s*"[^"]+",\s*art:\s*"[^"]+",\s*schluessel:\s*"([A-Za-z0-9_]+)"/g)]
      .map(m => m[1]);
    pruefe(felder.length >= 15, `Einstellungsseite: Feldtabelle gefunden (${felder.length})`);
    for (const k of new Set(felder)) {
      pruefe(eigene.has(k),
        `Einstellungsseite: "${k}" wird angezeigt und steht in ihrer eigenen Vorgabeliste`);
    }
  }

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Einstellungen: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
