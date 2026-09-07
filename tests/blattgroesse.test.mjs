/* Prueft, dass "Aufnahme fuer Druck" echte Blattmasse erzeugt.
 *
 * Anlass (18.08.2026), mit dem Druckdialog als Beleg: Dort stand
 * "Dokument: 220,1 x 1008,9 mm" neben "Papier 297 x 210 mm" — eine Bahn von
 * einem Meter, die der Drucker auf ein Blatt zwingen sollte, und "Seite 1
 * von 1". Die Ursache war zweigeteilt und beide Teile mussten fallen:
 *
 *   1. Der Modus kam gar nicht an (siehe tests/modus-kette.test.mjs).
 *   2. Auch danach folgte die Seitengroesse dem BILD statt dem Papier: so
 *      breit wie die Aufnahme, so hoch wie der Ausschnitt.
 *
 * Jetzt gilt bei vorgegebenem Blatt das Blatt. Das Bild wird hineingerechnet:
 * auf die Nutzflaeche gebracht, mittig, mit Rand. Dann stimmt das Papier, und
 * der Drucker muss nichts mehr anpassen.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const pruefe = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

const ctx = { console, Math, JSON, Date, Uint8Array, Array, String, Number, Object,
              isFinite, parseInt, parseFloat };
ctx.globalThis = ctx; ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(readFileSync(join(WURZEL, "pdf-writer.js"), "utf8"), ctx);
const P = ctx.PageShotPdf;

const JPEG = new Uint8Array([0xFF,0xD8,0xFF,0xE0,0,16,74,70,73,70,0,1,1,0,0,1,0,1,0,0,0xFF,0xD9]);
const SEITEN = [0,1,2].map(i => ({ bytes: JPEG, widthPx: 832, heightPx: 1234, yPx: i * 1234 }));

function masse(opts) {
  const bytes = P.buildPdf(SEITEN, Object.assign({ dpi: 144, title: "T", version: "t" }, opts));
  const txt = Buffer.from(bytes).toString("latin1");
  const kaesten = [...new Set([...txt.matchAll(/\/MediaBox \[([^\]]*)\]/g)].map(m => m[1]))];
  const [b, h] = kaesten[0].split(/\s+/).slice(2).map(Number);
  return { breite: b, hoehe: h, kaesten: kaesten.length,
           seiten: (txt.match(/\/Type \/Page[^s]/g) || []).length };
}

test("Blattgroesse beim Druck", () => {
  const mm = pt => pt / 72 * 25.4;

  // Ohne Vorgabe bleibt alles wie bisher: die Seite folgt dem Bild.
  const frei = masse({});
  pruefe(Math.abs(frei.breite - 416) < 1,
         `ohne Vorgabe folgt die Seite dem Bild (${frei.breite.toFixed(0)} pt)`);

  const faelle = [
    ["A4 hoch",     { breite: 595, hoehe: 842 }, 210, 297],
    ["A4 quer",     { breite: 842, hoehe: 595 }, 297, 210],
    ["Letter hoch", { breite: 612, hoehe: 792 }, 216, 279],
    ["Letter quer", { breite: 792, hoehe: 612 }, 279, 216],
  ];
  for (const [name, blattPt, sollB, sollH] of faelle) {
    const m = masse({ blattPt });
    pruefe(Math.abs(mm(m.breite) - sollB) < 1 && Math.abs(mm(m.hoehe) - sollH) < 1,
           `${name}: ${mm(m.breite).toFixed(0)} x ${mm(m.hoehe).toFixed(0)} mm`);
    pruefe(m.kaesten === 1, `${name}: alle Blaetter gleich gross`);
    pruefe(m.seiten === 3, `${name}: die Aufteilung bleibt bei 3 Seiten`);
  }

  /* Quer muss breiter als hoch sein — der Fall aus der Meldung.
   * Vorher war die Ausrichtung ohne jede Wirkung auf die Datei. */
  const hoch = masse({ blattPt: { breite: 595, hoehe: 842 } });
  const quer = masse({ blattPt: { breite: 842, hoehe: 595 } });
  pruefe(quer.breite > quer.hoehe, "quer: Blatt ist breiter als hoch");
  pruefe(hoch.hoehe > hoch.breite, "hoch: Blatt ist hoeher als breit");
  pruefe(quer.breite !== hoch.breite, "Die Ausrichtung veraendert die Datei ueberhaupt");

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Blattgroesse: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
