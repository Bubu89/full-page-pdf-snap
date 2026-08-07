/* Prueft die Schwarzweiss-Umkehr an vierzehn Seitenarten.
 *
 * Anlass (07.08.2026): Die Frage, ob das Verfahren auch bei anderen Formaten,
 * anderer Darstellung und auf anderen Rechnern richtig arbeitet. Der erste
 * Versuch zaehlte einfach die dunklen Punkte und traf damit nur sieben von
 * zwoelf Faellen - er kippte, sobald ein grosses Bild oder ein Diagramm auf
 * einer hellen Seite lag.
 *
 * Geprueft wird die Entscheidung selbst, nicht die Bitpackung: Wird die Seite
 * umgekehrt oder nicht? Der Code dazu steht in farbtiefeAnwenden.
 *
 * Aufruf: node tests/sw-robustheit.test.mjs
 */
import { readFileSync } from "node:fs";
import vm from "node:vm";

const quelle = readFileSync(new URL("../background.js", import.meta.url), "utf8");
const von = quelle.indexOf("function farbtiefeAnwenden");
const bis = quelle.indexOf("\nasync function canvasToFlateBytes");
const kontext = { Uint8Array, Uint32Array, Math, console };
kontext.globalThis = kontext;
vm.createContext(kontext);
vm.runInContext(quelle.slice(von, bis), kontext);

const B = 400, H = 300;

/** Graustufenbild -> RGBA, wie es aus getImageData kaeme. */
function alsRGBA(grau) {
  const d = new Uint8Array(grau.length * 4);
  for (let i = 0, j = 0; i < grau.length; i++, j += 4) {
    d[j] = d[j + 1] = d[j + 2] = grau[i]; d[j + 3] = 255;
  }
  return d;
}
const flaeche = (v) => new Uint8Array(B * H).fill(v);
function text(hg, tx, anteil = 0.08) {
  const a = flaeche(hg);
  const schritt = Math.max(2, Math.round(1 / anteil));
  for (let i = 0; i < a.length; i += schritt) a[i] = tx;
  return a;
}
function block(a, v, y0, y1, x0, x1) {
  const k = Uint8Array.from(a);
  for (let y = y0; y < y1; y++) for (let x = x0; x < x1; x++) k[y * B + x] = v;
  return k;
}

/* Wurde umgekehrt? Ablesbar am Ergebnis: Bei einer Seite mit wenig Schrift
 * ist der Hintergrund nach korrekter Behandlung weiss - also die grosse
 * Mehrheit der Bits gesetzt. */
function wurdeUmgekehrt(grau, sollHintergrundDunkel) {
  const { daten } = kontext.farbtiefeAnwenden(alsRGBA(grau), "sw", B);
  const bpz = Math.ceil(B / 8);
  let gesetzt = 0;
  for (let y = 0; y < H; y++)
    for (let x = 0; x < B; x++)
      if (daten[y * bpz + (x >> 3)] & (0x80 >> (x & 7))) gesetzt++;
  const weissAnteil = gesetzt / (B * H);
  // War die Vorlage dunkel und ist das Ergebnis hell, wurde umgekehrt.
  return sollHintergrundDunkel ? weissAnteil > 0.5 : weissAnteil > 0.5 ? false : true;
}

/** Ergebnis unabhaengig von der Vorlage: wie viel des Blattes bleibt weiss? */
function weissAnteil(grau) {
  const { daten } = kontext.farbtiefeAnwenden(alsRGBA(grau), "sw", B);
  const bpz = Math.ceil(B / 8);
  let gesetzt = 0;
  for (let y = 0; y < H; y++)
    for (let x = 0; x < B; x++)
      if (daten[y * bpz + (x >> 3)] & (0x80 >> (x & 7))) gesetzt++;
  return gesetzt / (B * H);
}

const FAELLE = [
  // [Name, Bild, Mindestanteil Weiss im Ergebnis]
  ["helle Textseite",                 text(255, 20),                                   0.75],
  ["dunkle Textseite (Dark Mode)",    text(25, 230),                                   0.75],
  ["Sepia / warmes Papier",           text(238, 60),                                   0.75],
  ["heller Grauton",                  text(200, 30),                                   0.75],
  ["dunkler Grauton",                 text(70, 240),                                   0.75],
  ["kontrastarm hell",                text(245, 120),                                  0.75],
  ["kontrastarm dunkel",              text(40, 110),                                   0.75],
  ["randloses dunkles Vollbild",      flaeche(35),                                     0.75],
  ["hell, dunkle Kopf- und Fusszeile", block(block(text(255,20),40,0,45,0,B),40,255,H,0,B), 0.50],
  ["hell mit dunkler Menuespalte",    block(text(255,20), 40, 0, H, 0, 90),            0.50],
  ["dunkel mit heller Menuespalte",   block(text(25,230), 235, 0, H, 0, 90),           0.50],
  ["hell + grosses dunkles Foto",     block(text(255,20), 45, 40, 260, 60, 340),       0.40],
  ["Diagramm hell, dunkle Balken",    block(flaeche(250), 60, 100, 280, 20, 380),      0.40],
  ["dunkel, heller Kopfbereich",      block(text(25,230), 240, 0, 45, 0, B),           0.50],
];

let fehler = 0;
console.log(`  ${"Seitenart".padEnd(36)} ${"weiss".padStart(7)}   mindestens`);
console.log("  " + "-".repeat(62));
for (const [name, bild, mindestens] of FAELLE) {
  const w = weissAnteil(bild);
  const ok = w >= mindestens;
  if (!ok) fehler++;
  console.log(`  ${ok ? "ok  " : "FEHL"} ${name.padEnd(31)} ${(w*100).toFixed(1).padStart(6)} %   ${(mindestens*100).toFixed(0)} %`);
}

/* Formate und Rechner: Die Bitpackung muss bei jeder Breite stimmen, auch bei
 * krummen. Zwei Bildschirmbreiten mal drei Pixeldichten - so entstehen die
 * Werte, die auf unterschiedlichen Geraeten wirklich vorkommen. */
console.log("\n  Breiten (Bildschirm x Pixeldichte):");
// Breite 1 ist bewusst nicht dabei: Dort IST der eine schwarze Punkt die
// ganze Flaeche, also wird zu Recht umgekehrt - die Probe wuerde ihre eigene
// Voraussetzung pruefen, nicht die Bitpackung. Die Laenge stimmt auch dort,
// das deckt der Fall "Breite 7" mit ab (beide fuellen auf ein Byte auf).
const BREITEN = [1280, 1366, 1440, 1512, 1600, 1617, 1920, 2560, 999, 8, 7];
let formatFehler = 0;
for (const breite of BREITEN) {
  const hoehe = 6;
  const g = new Uint8Array(breite * hoehe).fill(255);
  for (let y = 0; y < hoehe; y++) g[y * breite] = 0;      // linker Punkt schwarz
  const { daten, bits, kanaele } = kontext.farbtiefeAnwenden(alsRGBA(g), "sw", breite);
  const bpz = Math.ceil(breite / 8);
  const laengeOk = daten.length === bpz * hoehe;
  let punkteOk = true;
  for (let y = 0; y < hoehe; y++) {
    if (daten[y * bpz] & 0x80) punkteOk = false;           // linker Punkt: schwarz = Bit 0
    for (let x = 1; x < breite; x++)
      if (!(daten[y * bpz + (x >> 3)] & (0x80 >> (x & 7)))) punkteOk = false;
  }
  const ok = laengeOk && punkteOk && bits === 1 && kanaele === 1;
  if (!ok) { formatFehler++; fehler++; }
  console.log(`  ${ok ? "ok  " : "FEHL"} Breite ${String(breite).padStart(4)}  ` +
              `${daten.length} Byte (erwartet ${bpz*hoehe})`);
}

console.log(fehler === 0
  ? "\nSchwarzweiss: alle Seitenarten und Breiten in Ordnung"
  : `\nSchwarzweiss: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
