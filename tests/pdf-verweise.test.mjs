/* Prueft, dass Verweise im PDF anklickbar sind.
 *
 * Anlass (18.08.2026, vom Nutzer gemeldet): "die links werden auch im normalen
 * pdf nicht mitübernommen und sind nicht anklickbar". Das stimmte. Der
 * PDF-Schreiber kannte /Annots ueberhaupt nicht — das fertige PDF war ein Bild
 * der Seite, und was darin wie ein Verweis aussah, war einer GEWESEN. Die Lage
 * jedes Verweises lag dabei die ganze Zeit vor: die Linkkarte sammelt sie und
 * legte sie als Datei daneben.
 *
 * Geprueft wird deshalb dreierlei, und jedes davon konnte still danebengehen:
 *   1. Stehen die Anmerkungen ueberhaupt im PDF und ist die Seite auf sie
 *      verwiesen (/Annots)?
 *   2. Sitzen sie an der richtigen Stelle? Das PDF zaehlt seine Y-Achse nach
 *      OBEN, die Seite nach unten, und das Bild ist gegenueber dem Dokument
 *      skaliert. Ein Vorzeichenfehler faellt beim Ansehen nicht auf, beim
 *      Klicken schon.
 *   3. Bleiben "javascript:"-Ziele draussen? Ausfuehrbarer Code in einer Datei,
 *      die als Beleg weitergereicht wird, hat dort nichts zu suchen.
 *
 * Aufruf: node --test tests/pdf-verweise.test.mjs
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const HIER = dirname(fileURLToPath(import.meta.url));
const WURZEL = join(HIER, "..");

test("Anklickbare Verweise im PDF", () => {
  const ctx = { console, Math, JSON, Date, Uint8Array, Array, String, Number, Object, isFinite, parseInt, parseFloat };
  ctx.globalThis = ctx; ctx.window = ctx;
  vm.createContext(ctx);
  vm.runInContext(readFileSync(join(WURZEL, "pdf-writer.js"), "utf8"), ctx);
  const P = ctx.PageShotPdf;

  // Ein Blatt, 1000x2000 Bildpunkte, Dokumentbreite 500 CSS-px -> Skala 2
  const jpeg = new Uint8Array([0xFF,0xD8,0xFF,0xE0,0,16,74,70,73,70,0,1,1,0,0,1,0,1,0,0,0xFF,0xD9]);
  const pages = [{ bytes: jpeg, widthPx: 1000, heightPx: 2000 }];

  const links = [
    { href: "https://example.org/eins", x: 10,  y: 20,  w: 100, h: 15 },
    { href: "https://example.org/zwei", x: 50,  y: 900, w: 80,  h: 12 },
    { href: "javascript:alert(1)",      x: 10,  y: 40,  w: 100, h: 15 },  // muss raus
    { href: "#abschnitt",               x: 10,  y: 60,  w: 100, h: 15 },  // muss raus
    { href: "mailto:a@b.de",            x: 10,  y: 80,  w: 60,  h: 12 },
  ];

  const bytes = P.buildPdf(pages, {
    dpi: 144, title: "Test", version: "test",
    links, linksPageWidth: 500,
  });
  const pdf = Buffer.from(bytes);
  const txt = pdf.toString("latin1");

  const annots = (txt.match(/\/Subtype \/Link/g) || []).length;
  const uris = [...txt.matchAll(/\/URI \(([^)]*)\)/g)].map(m => m[1]);
  const rects = [...txt.matchAll(/\/Rect \[([^\]]*)\]/g)].map(m => m[1]);

  console.log("Anmerkungen :", annots);
  console.log("Ziele       :", uris);
  console.log("Rechtecke   :", rects);
  console.log("/Annots     :", /\/Annots \[/.test(txt) ? "in der Seite eingetragen" : "FEHLT");

  let fehler = 0;
  const p = (b, t) => { console.log((b ? "  ok   " : "  FEHL ") + t); if (!b) fehler++; };
  p(annots === 3, `drei Verweise uebernommen (${annots})`);
  p(!uris.some(u => /javascript/i.test(u)), "javascript: aussortiert");
  p(!txt.includes("#abschnitt"), "Sprungmarke aussortiert");
  p(uris.includes("https://example.org/eins"), "erster Verweis vorhanden");
  p(uris.includes("mailto:a@b.de"), "mailto vorhanden");

  // Lage pruefen: Link 1 sitzt bei y=20..35 CSS -> *2 = 40..70 Bildpunkte von oben.
  // Seitenhoehe 2000 px -> von unten 1930..1960 px -> *0.5 pt/px = 965..980 pt.
  const r1 = rects[0].split(/\s+/).map(Number);
  p(Math.abs(r1[0] - 10)   < 0.5, `x links  ${r1[0]} (erwartet 10)`);
  p(Math.abs(r1[2] - 110)  < 0.5, `x rechts ${r1[2]} (erwartet 110)`);
  p(Math.abs(r1[1] - 965)  < 0.5, `y unten  ${r1[1]} (erwartet 965)`);
  p(Math.abs(r1[3] - 980)  < 0.5, `y oben   ${r1[3]} (erwartet 980)`);
  p(r1[3] > r1[1], "Oberkante ist der groessere Y-Wert");

  console.log(fehler ? `# Verweise: ${fehler} Fehler` : "# alle Pruefungen bestanden");
    if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);

});
