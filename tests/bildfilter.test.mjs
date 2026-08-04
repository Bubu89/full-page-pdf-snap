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
