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
