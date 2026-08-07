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
//
// Die Werte entstehen aus Fensterbreite mal Pixeldichte - das ist die Breite,
// mit der captureVisibleTab liefert. Rechner und Telefone liegen dabei weit
// auseinander, und auf Android sind krumme Werte die Regel statt die
// Ausnahme: 412 x 2,625 ergibt 1081,5, und was der Browser daraus macht,
// ist nicht durch acht teilbar.
const BREITEN = [
  // Rechner
  1280, 1366, 1440, 1512, 1600, 1617, 1920, 2560,
  // Telefone: CSS-Breite x Pixeldichte
  720,   // 360 x 2      aeltere Geraete
  1080,  // 360 x 3      verbreitetster Fall
  1081,  // 412 x 2,625  Pixel-Reihe, abgerundet
  1082,  // dieselbe Rechnung, aufgerundet
  1179,  // 393 x 3      iPhone-Klasse im Querformat-Browser
  828,   // 414 x 2
  1344,  // 448 x 3      Falt-Telefon aufgeklappt
  // Randwerte
  999, 8, 7,
];
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

/* --- Dark Reader ---------------------------------------------------------
 *
 * Das Add-on faerbt Seiten nachtraeglich um. Fuer die Aufnahme ist das keine
 * Sonderbehandlung wert - captureVisibleTab liefert, was auf dem Bildschirm
 * steht -, aber es erzeugt Farbkombinationen, die von Hand gebaute Dunkelmodi
 * so nicht haben:
 *
 *   - Der Hintergrund ist nicht schwarz, sondern ein dunkles Grau mit
 *     Farbstich (#181a1b, Grauwert um 26).
 *   - Die Schrift ist nicht weiss, sondern ein warmes Hellgrau (#e8e6e3).
 *   - Bilder und Videos laesst es je nach Einstellung unangetastet oder
 *     dimmt sie nur. Auf einer sonst dunklen Seite steht dann ein helles
 *     Rechteck - genau die Lage, in der die Umkehr schwer zu entscheiden ist.
 *
 * Geprueft wird deshalb mit den echten Standardfarben des Add-ons.
 */
console.log("\n  Dark Reader (Standardfarben #181a1b / #e8e6e3):");
const DR_HG = 26, DR_TX = 230;
const DR = [
  ["reine Textseite",                    text(DR_HG, DR_TX),                             0.75],
  ["mit Kopfzeile in Markenfarbe",       block(text(DR_HG, DR_TX), 70, 0, 45, 0, B),     0.50],
  ["mit ungedimmtem Bild (klein)",       block(text(DR_HG, DR_TX), 235, 60, 160, 120, 280), 0.50],
  // Ein gedimmtes Bild auf halber Flaeche wird dunkel dargestellt - es WAR
  // dunkel (Wert 90 von 255). Es hell zu machen waere eine Erfindung. Der
  // Hintergrund bleibt weiss, und das war die Anforderung.
  ["mit gedimmtem Bild",                 block(text(DR_HG, DR_TX), 90, 40, 260, 60, 340), 0.40],
  ["Code-Block etwas heller",            block(text(DR_HG, DR_TX), 45, 100, 200, 30, 370), 0.60],
  ["Tabelle mit hellen Zeilen",          block(block(text(DR_HG,DR_TX),200,80,110,20,380), 200, 150, 180, 20, 380), 0.50],
];
for (const [name, bild, mindestens] of DR) {
  const w = weissAnteil(bild);
  const ok = w >= mindestens;
  if (!ok) fehler++;
  console.log(`  ${ok ? "ok  " : "FEHL"} ${name.padEnd(31)} ${(w*100).toFixed(1).padStart(6)} %   ${(mindestens*100).toFixed(0)} %`);
}

/* Der Fall, der die Umkehr am ehesten kippt: ein ungedimmtes Bild, das mehr
 * Platz einnimmt als der Text. Hier bleibt es beim Original - dokumentiert,
 * nicht behauptet, dass es gut waere. Weniger als die Haelfte des Blattes ist
 * dann schwarz, verfaelscht wird nichts. */
{
  const grenzfall = block(text(DR_HG, DR_TX), 235, 20, 280, 30, 370);
  const w = weissAnteil(grenzfall);
  const schwarz = 1 - w;
  const ok = schwarz < 0.5;
  if (!ok) fehler++;
  console.log(`  ${ok ? "ok  " : "FEHL"} ${"Grenzfall: Bild groesser als Text".padEnd(31)} ${(schwarz*100).toFixed(1).padStart(6)} % schwarz   unter 50 %`);
}

/* --- Alle Kacheln entscheiden gleich ------------------------------------
 *
 * Bei langen Aufnahmen wird das Bild in Kacheln zerlegt, und jede lief bisher
 * einzeln durch die Umwandlung. Eine Seite mit hellem oberem und dunklem
 * unterem Teil bekam dadurch an der Kachelgrenze einen Bruch: obere Kachel
 * unveraendert, untere umgekehrt. Beide fuer sich richtig, zusammen
 * unbrauchbar - und die Grenze lag dort, wo der Zuschnitt zufaellig hinfiel.
 *
 * Jetzt wird einmal fuer das ganze Bild entschieden und die Vorgabe an jede
 * Kachel gereicht. Geprueft wird genau das: dieselbe Vorgabe, dasselbe
 * Verhalten - unabhaengig davon, wie die einzelne Kachel aussieht.
 */
console.log("\n  Gemeinsame Entscheidung fuer alle Kacheln:");
{
  const HOCH = 400, KACHEL = 200;
  const ganz = new Uint8Array(B * HOCH);
  for (let y = 0; y < HOCH; y++)
    for (let x = 0; x < B; x++) {
      const obenHell = y < HOCH / 2;
      const i = y * B + x;
      ganz[i] = obenHell ? 250 : 25;
      if (i % 13 === 0) ganz[i] = obenHell ? 20 : 235;
    }

  const kachelWeiss = (vorgabe) => {
    const anteile = [];
    for (let k = 0; k < HOCH / KACHEL; k++) {
      const teil = ganz.slice(k * KACHEL * B, (k + 1) * KACHEL * B);
      const { daten } = kontext.farbtiefeAnwenden(alsRGBA(teil), "sw", B, vorgabe);
      const bpz = Math.ceil(B / 8);
      let gesetzt = 0;
      for (let y = 0; y < KACHEL; y++)
        for (let x = 0; x < B; x++)
          if (daten[y * bpz + (x >> 3)] & (0x80 >> (x & 7))) gesetzt++;
      anteile.push(gesetzt / (B * KACHEL));
    }
    return anteile;
  };

  const ohne = kachelWeiss(undefined);            // wie bisher: jede fuer sich
  const mit  = kachelWeiss(false);                // gemeinsame Vorgabe

  const unterschiedOhne = Math.abs(ohne[0] - ohne[1]);
  const unterschiedMit  = Math.abs(mit[0]  - mit[1]);

  const zeigtProblem = unterschiedOhne < 0.05;    // beide ~gleich hell = beide "optimiert"
  const okMit = unterschiedMit > 0.5;             // mit Vorgabe bleibt der Unterschied sichtbar

  console.log(`  ${zeigtProblem ? "ok  " : "FEHL"} Gegenprobe ohne Vorgabe: Kacheln ${(ohne[0]*100).toFixed(0)} % / ${(ohne[1]*100).toFixed(0)} % weiss - der Bruch faellt nicht auf`);
  console.log(`  ${okMit ? "ok  " : "FEHL"} mit gemeinsamer Vorgabe:  Kacheln ${(mit[0]*100).toFixed(0)} % / ${(mit[1]*100).toFixed(0)} % weiss - die Seite bleibt, wie sie war`);
  if (!zeigtProblem || !okMit) fehler++;

  // Und die Vorgabe muss in beide Richtungen durchschlagen
  const erzwungen = kachelWeiss(true);
  const beideUmgekehrt = erzwungen.every((w, i) => Math.abs(w - (1 - mit[i])) < 0.02);
  console.log(`  ${beideUmgekehrt ? "ok  " : "FEHL"} Vorgabe 'umkehren' wirkt auf jede Kachel gleich`);
  if (!beideUmgekehrt) fehler++;
}

/* --- Die Schwelle kommt aus dem Bild -------------------------------------
 *
 * Rueckfrage aus der Praxis (07.08.2026): Warum brechen die Buchstaben auf,
 * besonders das e? Weil Bildschirmschrift kantengeglaettet ist - zwischen
 * Buchstabe und Hintergrund liegen Grautoene, gemessen 2,4 % aller Punkte.
 * Eine feste Schwelle bei 128 laesst mehr als die Haelfte davon auf die helle
 * Seite fallen.
 *
 * Der schwerere Fall ist ein anderer: Bei kontrastarmen Seiten - grau auf
 * hellgrau - liegt ALLES ueber 128. Die feste Schwelle erfasst dort nichts,
 * das Blatt bleibt leer.
 */
console.log("\n  Selbstbestimmte Schwelle (Otsu):");
{
  const probe = (vordergrund, hintergrund) => {
    const a = new Uint8Array(B * H).fill(hintergrund);
    // Schrift mit weichen Kanten: je Strich ein Kern und zwei Randwerte
    for (let i = 0; i < B * H; i += 17) {
      a[i] = vordergrund;
      if (i + 1 < a.length) a[i + 1] = Math.round((vordergrund + hintergrund) / 2);
      if (i > 0) a[i - 1] = Math.round((vordergrund * 0.25 + hintergrund * 0.75));
    }
    return a;
  };

  const FAELLE = [
    ["schwarz auf weiss",        20, 255],
    ["dunkelgrau auf weiss",     60, 255],
    ["grau auf hellgrau",       110, 235],
    ["weiss auf dunkel",        235,  25],
    ["hellgrau auf dunkelgrau", 200,  60],
  ];
  for (const [name, vg, hg] of FAELLE) {
    const bild = probe(vg, hg);
    const { daten } = kontext.farbtiefeAnwenden(alsRGBA(bild), "sw", B);
    const bpz = Math.ceil(B / 8);
    let schwarz = 0;
    for (let y = 0; y < H; y++)
      for (let x = 0; x < B; x++)
        if (!(daten[y * bpz + (x >> 3)] & (0x80 >> (x & 7)))) schwarz++;
    const anteil = schwarz / (B * H);
    // Die Schrift belegt rund 6 % - erfasst werden sollte etwas in dieser
    // Groessenordnung, keinesfalls null und keinesfalls das halbe Blatt.
    const ok = anteil > 0.02 && anteil < 0.35;
    if (!ok) fehler++;
    console.log(`  ${ok ? "ok  " : "FEHL"} ${name.padEnd(26)} ${(anteil*100).toFixed(1).padStart(5)} % schwarz`);
  }

  // Gegenprobe: Mit fester Schwelle 128 verschwindet der kontrastarme Fall.
  {
    const bild = probe(110, 235);
    let unter128 = 0;
    for (const v of bild) if (v < 128) unter128++;
    // Die feste Schwelle erfasst hier nur den Kern, nicht die weichen Kanten.
    // Otsu nimmt beide - deshalb bleiben die Buchstaben geschlossen.
    let unterOtsu = 0;
    const h2 = new Uint32Array(256); for (const v of bild) h2[v]++;
    let sAlle = 0; for (let t = 0; t < 256; t++) sAlle += t * h2[t];
    let sB = 0, gB = 0, bv = -1, otsu = 128;
    for (let t = 0; t < 256; t++) {
      gB += h2[t]; if (!gB) continue;
      const gF = bild.length - gB; if (!gF) break;
      sB += t * h2[t];
      const v = gB * gF * (sB/gB - (sAlle-sB)/gF) ** 2;
      if (v > bv) { bv = v; otsu = t; }
    }
    for (const v of bild) if (v <= otsu) unterOtsu++;
    const zeigt = unterOtsu > unter128;
    console.log(`  ${zeigt ? "ok  " : "FEHL"} Gegenprobe: feste Schwelle erfasst ${unter128} Punkte, Otsu (${otsu}) erfasst ${unterOtsu}`);
    if (!zeigt) fehler++;
  }
}

console.log(fehler === 0
  ? "\nSchwarzweiss: alle Seitenarten und Breiten in Ordnung"
  : `\nSchwarzweiss: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);

