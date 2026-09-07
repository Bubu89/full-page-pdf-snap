/* Der freie Rest unter dem Bild bekommt die Farbe der Seite.
 *
 * Anlass (18.08.2026): Eine Aufnahme im Querformat, randlos, von einer Seite
 * mit dunklem Hintergrund. Links, rechts und oben sass das Bild exakt an der
 * Blattkante — gemessen 0,0 pt. Unten blieben je nach Seite 15 bis 40 pt
 * frei, weil der Schnitt in die naechste Zeilenluecke gezogen wird, damit
 * keine Textzeile zerschnitten wird.
 *
 * Dieser Rest ist unvermeidlich; er ist derselbe Rest, der in jedem
 * Textsatzprogramm am Seitenende bleibt. Sichtbar wurde er, weil dort das
 * blanke Blatt durchschien: ein weisser Balken quer ueber die untere Kante
 * einer dunklen Seite.
 *
 * Geprueft wird deshalb NICHT, dass kein Rest bleibt — das waere nur mit
 * zerschnittenen Zeilen oder verzerrtem Bild zu haben —, sondern dass der
 * Rest nicht mehr weiss ist.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

import vm from "node:vm";
const ctx = { console, Math, JSON, Date, Uint8Array, Array, Object, String, Number, TextEncoder };
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(readFileSync(join(WURZEL, "pdf-writer.js"), "utf8"), ctx);
const P = ctx.PageShotPdf;

// Ein Ein-Punkt-JPEG genuegt: geprueft wird die Flaeche, nicht das Bild.
const JPEG = new Uint8Array([0xFF, 0xD8, 0xFF, 0xD9]);
const BLATT = { breite: 842, hoehe: 595 };

function bauen(hintergrund) {
  const seite = { jpegBytes: JPEG, widthPx: 200, heightPx: 100, filter: "DCTDecode" };
  if (hintergrund) seite.hintergrund = hintergrund;
  const bytes = P.buildPdf([seite], { dpi: 144, blattPt: BLATT, randPt: 0 });
  return Buffer.from(bytes).toString("latin1");
}

test("Der freie Rest traegt die Seitenfarbe", () => {
  const mit = bauen([24, 26, 31]);
  const treffer = mit.match(/([\d.]+) ([\d.]+) ([\d.]+) rg\s*\n0 0 ([\d.]+) ([\d.]+) re\s*\nf/);
  p(!!treffer, "eine Fuellflaeche wird gezeichnet");
  if (treffer) {
    const [r, g, b] = treffer.slice(1, 4).map(Number);
    p(Math.abs(r * 255 - 24) < 1.5, `Rot trifft (${(r * 255).toFixed(0)} statt 24)`);
    p(Math.abs(g * 255 - 26) < 1.5, `Gruen trifft (${(g * 255).toFixed(0)} statt 26)`);
    p(Math.abs(b * 255 - 31) < 1.5, `Blau trifft (${(b * 255).toFixed(0)} statt 31)`);
    p(Number(treffer[4]) === BLATT.breite && Number(treffer[5]) === BLATT.hoehe,
      `die Flaeche deckt das ganze Blatt (${treffer[4]}x${treffer[5]})`);
    p(mit.indexOf(" re\nf") < mit.indexOf(" cm\n/Im"),
      "die Fuellung steht VOR dem Bild, nicht darueber");
  }

  /* Gegenprobe: Ohne Farbangabe bleibt alles wie bisher. Ein geratener Ton
   * waere schlimmer als der weisse Rest. */
  const ohne = bauen(null);
  p(!/ rg\s*\n0 0 [\d.]+ [\d.]+ re/.test(ohne),
    "Gegenprobe: ohne Farbangabe wird nichts gefuellt");

  /* Und die Quelle der Farbe: Schwarzweiss ergibt immer Weiss, sonst stuende
   * ein dunkler Balken auf einem Blatt, das gerade hell gerechnet wurde. */
  for (const [name, datei] of [["firefox", "background.js"],
                               ["chrome", join("chrome-mv3", "background.js")]]) {
    const bg = readFileSync(join(WURZEL, datei), "utf8");
    p(/function seitenHintergrund\(/.test(bg), `${name}: die Farbe wird ermittelt`);
    p(/if \(modus === "sw"\) return \[255, 255, 255\]/.test(bg),
      `${name}: Schwarzweiss ergibt Weiss`);
    const stellen = (bg.match(/hintergrund: seitenHintergrund\(/g) || []).length;
    const erzeugt = (bg.match(/canvasToBildBytes\(slice,/g) || []).length;
    p(stellen === erzeugt && stellen > 0,
      `${name}: alle ${erzeugt} Seitenerzeugungen geben die Farbe mit (${stellen})`);
  }

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Hintergrund: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
