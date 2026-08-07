/* Prueft, dass der PDF-Writer beide Bildfilter schreibt und die alte
 * Aufrufform weiter funktioniert.
 *
 * Anlass: Am 4. August 2026 bekam die Aufnahme einen zweiten Filter — Kacheln
 * werden seitdem als DCTDecode ODER FlateDecode eingebettet, je nachdem, was
 * kleiner ist. Beim Umbau brach an drei Stellen die Feldbenennung, darunter
 * die SHA-256-Pruefsumme, die danach ueber ein leeres Feld gelaufen waere.
 * Der Beleg im PDF haette weiter dagestanden und nichts mehr belegt.
 *
 * Deshalb prueft dieser Test nicht, ob der Aufruf durchlaeuft, sondern was im
 * PDF steht.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import vm from "node:vm";

// pdf-writer.js ist kein Modul — im Kontext auswerten und die Funktion greifen.
const quelle = readFileSync(new URL("../pdf-writer.js", import.meta.url), "utf8");
const kontext = { console, TextEncoder, TextDecoder, Uint8Array, Date, Math, JSON };
kontext.globalThis = kontext;
vm.createContext(kontext);
vm.runInContext(quelle, kontext);
// Die Datei haengt sich als PageShotPdf an den globalen Namensraum — der
// erste Entwurf dieses Tests suchte per Heuristik die "erste Funktion" und
// erwischte Uint8Array.
const schreibePdf = (pages, opts = {}) => kontext.PageShotPdf.buildPdf(pages, opts);

const bytes = (n, f = 0x41) => new Uint8Array(n).fill(f);
const alsText = (u8) => Buffer.from(u8).toString("latin1");

test("eine Kachel mit FlateDecode landet als FlateDecode im PDF", () => {
  const pdf = schreibePdf([{
      widthPx: 100, heightPx: 50,
      tiles: [{ bytes: bytes(64), filter: "FlateDecode",
                xPx: 0, yPx: 0, wPx: 100, hPx: 50 }],
    }]);
  const t = alsText(pdf);
  assert.match(t, /\/Filter \/FlateDecode/, "FlateDecode fehlt im Bildobjekt");
  assert.doesNotMatch(t, /\/Filter \/DCTDecode/, "DCTDecode steht faelschlich drin");
  assert.match(t, /\/Length 64\b/, "Laenge stimmt nicht mit den Daten ueberein");
});

test("eine Kachel ohne Filterangabe bleibt DCTDecode", () => {
  // Die alte Aufrufform. Sie muss weiter funktionieren, sonst brechen
  // bestehende Verwendungen still.
  const pdf = schreibePdf([{ jpegBytes: bytes(32), widthPx: 10, heightPx: 10 }]);
  assert.match(alsText(pdf), /\/Filter \/DCTDecode/,
    "ohne Filterangabe muss DCTDecode herauskommen");
});

test("gemischte Kacheln bekommen jede ihren eigenen Filter", () => {
  const pdf = schreibePdf([{
      widthPx: 100, heightPx: 100,
      tiles: [
        { bytes: bytes(16), filter: "FlateDecode", xPx: 0, yPx: 0, wPx: 100, hPx: 50 },
        { bytes: bytes(24), filter: "DCTDecode",  xPx: 0, yPx: 50, wPx: 100, hPx: 50 },
      ],
    }]);
  const t = alsText(pdf);
  assert.equal((t.match(/\/Filter \/FlateDecode/g) || []).length, 1);
  assert.equal((t.match(/\/Filter \/DCTDecode/g) || []).length, 1);
});

test("das Ergebnis ist ein PDF mit Ende-Kennung", () => {
  const pdf = schreibePdf([{ bytes: bytes(8), filter: "FlateDecode", widthPx: 10, heightPx: 10 }]);
  const t = alsText(pdf);
  assert.match(t, /^%PDF-/, "kein PDF-Kopf");
  assert.match(t, /%%EOF\s*$/, "keine Ende-Kennung");
});

test("Graustufen und Schwarzweiss schreiben DeviceGray mit passender Bittiefe", () => {
  const pdf = schreibePdf([{
    widthPx: 100, heightPx: 100,
    tiles: [
      { bytes: bytes(10), filter: "FlateDecode", kanaele: 1, bits: 8,
        xPx: 0, yPx: 0, wPx: 100, hPx: 50 },
      { bytes: bytes(10), filter: "FlateDecode", kanaele: 1, bits: 1,
        xPx: 0, yPx: 50, wPx: 100, hPx: 50 },
    ],
  }]);
  const t = alsText(pdf);
  assert.equal((t.match(/\/ColorSpace \/DeviceGray/g) || []).length, 2,
    "beide Kacheln muessen DeviceGray tragen");
  assert.match(t, /\/BitsPerComponent 1\b/, "1-bit-Kachel fehlt");
  assert.match(t, /\/BitsPerComponent 8\b/, "8-bit-Kachel fehlt");
});

test("ohne Farbraumangabe bleibt es bei DeviceRGB und 8 bit", () => {
  const pdf = schreibePdf([{ jpegBytes: bytes(16), widthPx: 10, heightPx: 10 }]);
  const t = alsText(pdf);
  assert.match(t, /\/ColorSpace \/DeviceRGB \/BitsPerComponent 8/);
});

/* --------------------------------------------------------------------------
 * Zeilenausrichtung bei Schwarzweiss
 *
 * PDF verlangt, dass jede Bildzeile an einer Byte-Grenze beginnt
 * (ISO 32000-1, 7.4.4). Die erste Fassung von farbtiefeAnwenden packte alle
 * Punkte fortlaufend durch. Bei 1440 Punkten Breite fiel das nicht auf, weil
 * 1440 durch 8 teilbar ist; bei 1617 rutschte jede Zeile um sieben Bit und
 * das Bild zerfiel in Diagonalen.
 *
 * Geprueft wird deshalb beides: die glatte Breite, die auch vorher ging, und
 * die krumme, die es aufdeckte.
 * ----------------------------------------------------------------------- */

const hintergrund = readFileSync(new URL("../background.js", import.meta.url), "utf8");
const anfang = hintergrund.indexOf("function farbtiefeAnwenden");
const ende = hintergrund.indexOf("\nasync function canvasToFlateBytes");
const kontext2 = { Uint8Array, Math, console };
kontext2.globalThis = kontext2;
vm.createContext(kontext2);
vm.runInContext(hintergrund.slice(anfang, ende), kontext2);

/** Ein Bild bauen, dessen erste Spalte schwarz ist und der Rest weiss. */
function testbild(breite, hoehe) {
  const d = new Uint8Array(breite * hoehe * 4).fill(255);
  for (let y = 0; y < hoehe; y++) {
    const i = (y * breite) * 4;
    d[i] = d[i + 1] = d[i + 2] = 0;      // Punkt ganz links: schwarz
  }
  return d;
}

for (const breite of [1440, 1617, 999, 8, 7]) {
  test(`Schwarzweiss: Zeilen byte-ausgerichtet bei Breite ${breite}`, () => {
    const hoehe = 5;
    const { daten, bits, kanaele } = kontext2.farbtiefeAnwenden(
      testbild(breite, hoehe), "sw", breite);

    assert.equal(bits, 1);
    assert.equal(kanaele, 1);

    const bytesJeZeile = Math.ceil(breite / 8);
    assert.equal(daten.length, bytesJeZeile * hoehe,
      "Puffergroesse muss Zeilen auf volle Bytes auffuellen");

    // Der schwarze Punkt jeder Zeile muss am Zeilenanfang stehen — genau das
    // verrutscht ohne Auffuellung.
    for (let y = 0; y < hoehe; y++) {
      const erstesByte = daten[y * bytesJeZeile];
      assert.equal(erstesByte & 0x80, 0x80,
        `Zeile ${y}: linker Punkt muss gesetzt sein, Byte war 0x${erstesByte.toString(16)}`);
      // und der Rest der Zeile leer
      for (let b = 1; b < bytesJeZeile; b++) {
        assert.equal(daten[y * bytesJeZeile + b], 0,
          `Zeile ${y}, Byte ${b}: darf nichts enthalten`);
      }
      assert.equal(erstesByte, 0x80, `Zeile ${y}: nur der linke Punkt`);
    }
  });
}

test("Graustufen bleibt 8 bit und unveraendert lang", () => {
  const breite = 1617, hoehe = 4;
  const { daten, bits, kanaele } = kontext2.farbtiefeAnwenden(
    testbild(breite, hoehe), "graustufen", breite);
  assert.equal(bits, 8);
  assert.equal(kanaele, 1);
  assert.equal(daten.length, breite * hoehe, "Graustufen kennt keine Auffuellung");
});

/* --- Farbtiefe muss den Weg bis in den PDF-Kopf ueberstehen --------------
 *
 * Gefunden am 07.08.2026: Im mehrseitigen Druckmodus mit Schwarzweiss kam ein
 * PDF heraus, das oben ein paar Zeilen Rauschen zeigte und darunter nichts.
 * Der Kopf sagte /DeviceRGB /BitsPerComponent 8, im Strom lagen 1-Bit-Daten -
 * ein Achtel der angekuendigten Menge.
 *
 * Die Umrechnung war nie schuld. Verloren gingen die Angaben erst im Writer:
 * Wege, die eine Seite als EIN Bild ablegen (mehrseitiger Druck, kurze Seiten
 * ohne Kachelung), bekamen eine Ersatzkachel gebaut - und die uebernahm
 * kanaele/bits nicht. Der gekachelte Weg trug sie immer schon, deshalb fiel
 * es an langen Seiten nie auf.
 */
{
  // Der Normalisierungsschritt aus pdf-writer.js, wie er sein muss
  const normalisiere = (pg) => pg.tiles && pg.tiles.length
    ? pg.tiles
    : [{ bytes: pg.bytes, filter: pg.filter,
         kanaele: pg.kanaele, bits: pg.bits,
         xPx: 0, yPx: 0, wPx: pg.widthPx, hPx: pg.heightPx }];

  const kopf = (t) => {
    const kanaele = t.kanaele || 3, bits = t.bits || 8;
    return { farbraum: kanaele === 1 ? "/DeviceGray" : "/DeviceRGB", bits };
  };

  const faelle = [
    ["Schwarzweiss, eine Seite als ein Bild", { kanaele: 1, bits: 1 }, "/DeviceGray", 1],
    ["Graustufen, eine Seite als ein Bild",   { kanaele: 1, bits: 8 }, "/DeviceGray", 8],
    ["Farbe, eine Seite als ein Bild",        { kanaele: 3, bits: 8 }, "/DeviceRGB",  8],
  ];
  for (const [name, tiefe, wantFarbraum, wantBits] of faelle) {
    const seite = { bytes: new Uint8Array(10), filter: "FlateDecode",
                    widthPx: 1617, heightPx: 2400, ...tiefe };
    const k = kopf(normalisiere(seite)[0]);
    const ok = k.farbraum === wantFarbraum && k.bits === wantBits;
    console.log(`${ok ? "ok  " : "FEHL"} ${name}: ${k.farbraum} ${k.bits} bit`);
    if (!ok) process.exitCode = 1;
  }

  // Gekachelt: die Angaben stehen je Kachel und muessen unangetastet bleiben
  const gekachelt = { widthPx: 1617, heightPx: 9000,
                      tiles: [{ bytes: new Uint8Array(4), filter: "FlateDecode",
                                kanaele: 1, bits: 1, xPx: 0, yPx: 0, wPx: 1617, hPx: 2400 }] };
  const kg = kopf(normalisiere(gekachelt)[0]);
  const okg = kg.farbraum === "/DeviceGray" && kg.bits === 1;
  console.log(`${okg ? "ok  " : "FEHL"} Schwarzweiss, gekachelt: ${kg.farbraum} ${kg.bits} bit`);
  if (!okg) process.exitCode = 1;

  // Gegenprobe: ohne Uebernahme faellt genau der Schwarzweiss-Fall durch
  const ohne = (pg) => [{ bytes: pg.bytes, filter: pg.filter,
                          xPx: 0, yPx: 0, wPx: pg.widthPx, hPx: pg.heightPx }];
  const kaputt = kopf(ohne({ bytes: new Uint8Array(10), filter: "FlateDecode",
                             widthPx: 1617, heightPx: 2400, kanaele: 1, bits: 1 }));
  const zeigtFehler = kaputt.farbraum === "/DeviceRGB" && kaputt.bits === 8;
  console.log(`${zeigtFehler ? "ok  " : "FEHL"} Gegenprobe: ohne Uebernahme entsteht ${kaputt.farbraum} ${kaputt.bits} bit`);
  if (!zeigtFehler) process.exitCode = 1;
}

/* --- Dunkle Oberflaechen werden vor der Schwelle umgekehrt ---------------
 *
 * Frage aus der Praxis (07.08.2026): Warum ist die Schrift in Schwarzweiss so
 * grob? Zwei Ursachen, und nur eine liess sich beheben.
 *
 * Die eine ist prinzipbedingt: Bei einem Bit je Punkt gibt es kein
 * Antialiasing, die weichen Kanten der Bildschirmschrift fallen weg. Dagegen
 * hilft nur eine hoehere Aufnahmeskalierung oder Graustufen.
 *
 * Die andere war ein echter Mangel: Eine Seite im Dunkelmodus wurde zur
 * schwarzen Flaeche mit weisser Schrift, weil der Hintergrund unter der
 * Schwelle liegt und der Text darueber. Gemessen an einer Textprobe
 * (Hintergrund 30, Schrift 235): 93,9 % der Punkte schwarz.
 */
{
  // Das Kriterium aus dem Code: gezaehlt wird das ERGEBNIS, nicht die Vorlage.
  const schwarzAnteil = (grau) => {
    let n = 0; for (const g of grau) if (g < 128) n++;
    return n / grau.length;
  };
  const umkehrNoetig = (grau) => schwarzAnteil(grau) > 0.5;
  const schwelle = (grau, umkehren) => {
    let n = 0;
    for (const g of grau) { const w = umkehren ? 255 - g : g; if (w < 128) n++; }
    return n / grau.length;
  };
  const mittelwert = (a) => a.reduce((s, x) => s + x, 0) / a.length;

  // Textprobe: 6 % Schrift auf Flaeche - einmal hell, einmal dunkel
  const machProbe = (hg, schrift) => {
    const a = new Uint8Array(1000).fill(hg);
    for (let i = 0; i < 60; i++) a[i * 16] = schrift;
    return a;
  };

  const hell = machProbe(255, 20);
  const dunkel = machProbe(30, 235);

  const mH = mittelwert([...hell]), mD = mittelwert([...dunkel]);
  console.log(`ok   mittlere Helligkeit hell=${mH.toFixed(0)} dunkel=${mD.toFixed(0)}`);

  // Helle Vorlage: keine Umkehr, wenig Schwarz - und die Umkehr aendert nichts
  const a1 = schwelle(hell, umkehrNoetig(hell));
  const okHell = !umkehrNoetig(hell) && a1 < 0.2;
  console.log(`${okHell ? "ok  " : "FEHL"} helle Vorlage bleibt unangetastet: ${(a1*100).toFixed(1)} % schwarz`);
  if (!okHell) process.exitCode = 1;

  // Dunkle Vorlage OHNE Umkehr: fast alles schwarz - der Zustand vorher
  const a2 = schwelle(dunkel, false);
  const zeigtFehler = a2 > 0.8;
  console.log(`${zeigtFehler ? "ok  " : "FEHL"} Gegenprobe ohne Umkehr: ${(a2*100).toFixed(1)} % schwarz`);
  if (!zeigtFehler) process.exitCode = 1;

  // Dunkle Vorlage MIT Umkehr: so wenig Schwarz wie bei der hellen
  const a3 = schwelle(dunkel, umkehrNoetig(dunkel));
  const okDunkel = umkehrNoetig(dunkel) && a3 < 0.2;
  console.log(`${okDunkel ? "ok  " : "FEHL"} dunkle Vorlage umgekehrt: ${(a3*100).toFixed(1)} % schwarz`);
  if (!okDunkel) process.exitCode = 1;

  // Beide Wege muessen zum selben Ergebnis fuehren - das ist der Sinn
  const gleich = Math.abs(a1 - a3) < 0.02;
  console.log(`${gleich ? "ok  " : "FEHL"} hell und dunkel ergeben denselben Schwarzanteil (${(a1*100).toFixed(1)} vs ${(a3*100).toFixed(1)} %)`);
  if (!gleich) process.exitCode = 1;

  // Der Fall, an dem die mittlere Helligkeit scheitert: heller Kopfbereich,
  // dunkler Inhalt. Im Mittel ueber 128 - und trotzdem waere die Seite zu
  // zwei Dritteln schwarz. Genau dafuer zaehlt das Ergebnis, nicht die Vorlage.
  {
    // 45 % sehr hell (Rand, Kopfzeile), 55 % mittelgrau (Inhaltsflaeche).
    // Mittlere Helligkeit 0.45*255 + 0.55*100 = 170 - klar ueber 128, das alte
    // Kriterium haette die Seite so gelassen. Der Schwarzanteil liegt aber bei
    // 55 %: mehr als die Haelfte des Blattes waere Toner.
    const gemischt = new Uint8Array(2000);
    gemischt.fill(255, 0, 900);
    gemischt.fill(100, 900, 2000);
    const m = mittelwert([...gemischt]);
    const vorher = m < 128;                       // altes Kriterium
    const jetzt = umkehrNoetig(gemischt);         // neues Kriterium
    const nachher = schwelle(gemischt, jetzt);
    console.log(`ok   gemischte Seite: mittlere Helligkeit ${m.toFixed(0)} (altes Kriterium haette ${vorher ? "umgekehrt" : "NICHT umgekehrt"})`);
    const gut = jetzt && nachher < 0.5;
    console.log(`${gut ? "ok  " : "FEHL"} gemischte Seite wird umgekehrt: ${(nachher*100).toFixed(1)} % schwarz`);
    if (!gut) process.exitCode = 1;
    console.log(`${!vorher ? "ok  " : "FEHL"} Gegenprobe: mittlere Helligkeit haette hier versagt`);
    if (vorher) process.exitCode = 1;
  }
}
