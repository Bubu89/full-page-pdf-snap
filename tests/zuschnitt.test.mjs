// Prueft den Zuschnitt im Wortlaut des ausgelieferten Codes: ein Gesamtbild
// bekannter Groesse, ein Ausschnitt, und die Frage, ob Breite, Hoehe und
// Textebene danach zusammenpassen.
import { readFileSync } from "node:fs";
const bg = readFileSync(new URL("../background.js", import.meta.url), "utf8");
// Der zweite Treffer ist der Zuschnitt; der erste ist der Schleifenabbruch.
// Der Zuschnitt-Block, eindeutig an seiner ersten Zeile erkannt — nicht an
// einem Meldungstext, der sich mit jeder Aenderung verschiebt.
const von = bg.indexOf("  if (settings.region) {\n    const r = settings.region;");
const bis = bg.indexOf("\n  }", bg.indexOf("textSeiteBreite = breiteCss;")) + 4;
const block = bg.slice(von, bis);

// Minimaler Ersatz fuer die Zeichenflaeche: merkt sich nur die Masse und den
// Ausschnitt, mit dem gezeichnet wurde.
function machFlaeche(w, h) {
  return { width: w, height: h, _gezeichnet: null,
           getContext: () => ({ drawImage: (q, sx, sy, sw, sh) => {
             machFlaeche._letzte = { sx, sy, sw, sh, quelleW: q.width, quelleH: q.height };
           } }) };
}
const document = { createElement: () => machFlaeche(0, 0) };
const log = () => {};

function lauf(bildW, bildH, dprY, region, woerter, seiteBreite) {
  let big = machFlaeche(bildW, bildH);
  let pxW = bildW, bigH = bildH;
  let textWoerter = woerter, textSeiteBreite = seiteBreite;
  const settings = { region };
  eval(block);
  return { pxW, bigH, bigW: big.width, bigH2: big.height,
           woerter: textWoerter, breite: textSeiteBreite,
           gelesen: machFlaeche._letzte };
}

// Fall aus dem Fehlerbericht: breite Seite, kleiner Ausschnitt, Faktor 2
const woerter = [];
for (let i = 0; i < 40; i++) woerter.push({ t: "w" + i, x: 40 + i * 12, y: 100 + i * 30, w: 10, h: 14, s: 12 });
const r = lauf(2000, 12000, 2, { x: 100, y: 200, w: 500, h: 300, dpr: 2 }, woerter, 1000);

const pruef = [
  ["pxW folgt dem Ausschnitt", r.pxW === 1000, `pxW=${r.pxW} (erwartet 1000)`],
  ["bigH folgt dem Ausschnitt", r.bigH === 600, `bigH=${r.bigH} (erwartet 600)`],
  ["Flaeche hat dieselbe Breite", r.bigW === r.pxW, `${r.bigW} vs ${r.pxW}`],
  ["Flaeche hat dieselbe Hoehe", r.bigH2 === r.bigH, `${r.bigH2} vs ${r.bigH}`],
  ["aus der richtigen Stelle gelesen", r.gelesen.sx === 200 && r.gelesen.sy === 400,
   `sx=${r.gelesen.sx} sy=${r.gelesen.sy} (erwartet 200/400)`],
  ["Textebene erhalten", Array.isArray(r.woerter) && r.woerter.length > 0,
   `${r.woerter ? r.woerter.length : 0} Woerter`],
  ["Wortkoordinaten versetzt", r.woerter && r.woerter.every(w => w.x >= -20 && w.y >= -20),
   "keine Wortmarke weit im Negativen"],
  ["Seitenbreite auf CSS umgerechnet", r.breite === 500, `${r.breite} (erwartet 500 — die Auswahl war 500 CSS-Pixel breit)`],
];
let fehl = 0;
for (const [name, ok, wie] of pruef) { if (!ok) fehl++; console.log(`  ${ok ? "ok  " : "FEHL"} ${name.padEnd(34)} ${wie}`); }

// Der gemeldete Fehler: weit gescrollt, dann einen Bereich gewaehlt. Die
// Auswahl liefert Dokumentkoordinaten (Fensterposition plus Scrollstand); der
// Zuschnitt muss genau dort greifen und nicht am Seitenanfang.
const gescrollt = lauf(2000, 24000, 2,
  { x: 100, y: 5200, w: 500, h: 300, scrollY: 5000, dpr: 2 }, woerter, 1000);
const pruef2 = [
  ["Zuschnitt an der gescrollten Stelle", gescrollt.gelesen.sy === 10400,
   `sy=${gescrollt.gelesen.sy} (erwartet 10400 = 5200 CSS x 2)`],
  ["nicht am Seitenanfang", gescrollt.gelesen.sy !== 0, `sy=${gescrollt.gelesen.sy}`],
  ["Breite stimmt", gescrollt.pxW === 1000, `pxW=${gescrollt.pxW}`],
];
for (const [name, ok, wie] of pruef2) { if (!ok) fehl++; console.log(`  ${ok ? "ok  " : "FEHL"} ${name.padEnd(34)} ${wie}`); }

console.log(fehl ? `\n  ${fehl} fehlgeschlagen` : "\n  alle 11 Prüfungen bestanden");
process.exit(fehl ? 1 : 0);
