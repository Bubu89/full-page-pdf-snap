/* Prueft, dass beim Druck keine weissen Streifen bleiben.
 *
 * Gemeldet am 18.08.2026 mit zwei Dateien: im Querformat 89 pt weiss unten, im
 * Hochformat 12 pt seitlich. Die Ursache war eine Rechnung an zwei Stellen:
 *
 *   - Das Verhaeltnis der Blattstuecke kam aus der NUTZFLAECHE bei 15 mm Rand
 *     (210-30 x 297-30), gedruckt wurde aber randlos. Das Stueck passte damit
 *     nicht aufs Blatt, wurde beim Einpassen verkleinert, und der Rest blieb
 *     leer.
 *   - Im A4-Zweig der Seitenaufteilung stand dasselbe: pxW * 267/180 statt
 *     pxW * 297/210. Verhaeltnis 1:1,483 statt 1:1,414.
 *
 * Beides rechnet jetzt mit dem vollen Blatt. Ein Rand entsteht nur noch, wenn
 * er ausdruecklich eingestellt wurde — dann aber als echter Rand und nicht als
 * Rechenfehler.
 *
 * Aufruf: node --test tests/druckrand.test.mjs
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

const ctx = { console, Math, JSON, Date, Uint8Array, Array, String, Number, Object,
              isFinite, parseInt, parseFloat };
ctx.globalThis = ctx; ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(readFileSync(join(WURZEL, "pdf-writer.js"), "utf8"), ctx);
const JPEG = new Uint8Array([0xFF,0xD8,0xFF,0xE0,0,16,74,70,73,70,0,1,1,0,0,1,0,1,0,0,0xFF,0xD9]);

/** Ein Ausschnitt im Verhaeltnis der Nutzflaeche — so schneidet umbruchstellen. */
function lage(pxW, blatt, randPt) {
  const nutzB = blatt.breite - 2 * randPt, nutzH = blatt.hoehe - 2 * randPt;
  const hPx = Math.round(pxW * (nutzH / nutzB));
  const bytes = ctx.PageShotPdf.buildPdf([{ bytes: JPEG, widthPx: pxW, heightPx: hPx, yPx: 0 }],
    { dpi: 144, title: "T", version: "t", blattPt: blatt, randPt });
  const t = Buffer.from(bytes).toString("latin1");
  const m = [...t.matchAll(/q\n(-?[\d.]+) 0 0 (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) cm/g)][0];
  const [bw, bh, x, y] = [m[1], m[2], m[3], m[4]].map(Number);
  return { oben: blatt.hoehe - bh - y, unten: y, links: x, rechts: blatt.breite - bw - x };
}

test("Kein weisser Streifen beim Druck", () => {
  const A4H = { breite: 595, hoehe: 842 }, A4Q = { breite: 842, hoehe: 595 };
  const LET = { breite: 612, hoehe: 792 };

  for (const [name, blatt] of [["A4 hoch", A4H], ["A4 quer", A4Q], ["Letter", LET]]) {
    const r = lage(832, blatt, 0);
    p(Math.abs(r.oben) < 1.5 && Math.abs(r.unten) < 1.5,
      `${name} randlos: oben/unten ${r.oben.toFixed(0)}/${r.unten.toFixed(0)} pt`);
    p(Math.abs(r.links) < 1.5 && Math.abs(r.rechts) < 1.5,
      `${name} randlos: links/rechts ${r.links.toFixed(0)}/${r.rechts.toFixed(0)} pt`);
  }

  /* Ein eingestellter Rand kommt als echter Rand heraus — gleich auf allen
   * Seiten. 5 mm sind 14,17 pt. */
  const mm5 = 5 * 72 / 25.4;
  const r = lage(832, A4H, mm5);
  for (const [seite, wert] of Object.entries(r)) {
    p(Math.abs(wert - mm5) < 1.5, `5 mm Rand: ${seite} ${wert.toFixed(1)} pt (erwartet 14,2)`);
  }

  /* Gegenprobe: Die alte Rechnung (Nutzflaeche 180/267 auf randlosem Blatt)
   * haette hier einen Streifen erzeugt. */
  const altesVerhaeltnis = 267 / 180;      // 1,483
  const blattVerhaeltnis = 297 / 210;      // 1,414
  p(Math.abs(altesVerhaeltnis - blattVerhaeltnis) > 0.05,
    `Gegenprobe: die alte Rechnung weicht messbar ab (1:${altesVerhaeltnis.toFixed(3)} statt 1:${blattVerhaeltnis.toFixed(3)})`);

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Druckrand: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
