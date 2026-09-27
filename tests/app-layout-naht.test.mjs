// Naht bei App-Layouts (innerer Scroll-Container mit klebender Kopfzeile).
//
// Anlass 27.09.2026, Gmail-Lesebereich in Firefox (2.42.0): Leerband an der
// Naht, doppelte Textzeilen, leerer Schwanz. Drei Ursachen, hier je eine
// Pruefung im Wortlaut des ausgelieferten Codes:
//   1. Massstab aus der Fensterbreite, nicht aus der Containerbreite.
//   2. Schrittweite aus dem sichtbaren Ausschnitt (clip.h), nicht aus der
//      Containerhoehe - sonst fehlt je Naht die Hoehe der Kopfzeile.
//   3. Klebende Kopfzeile im Container vermessen; Zuschnitt beginnt darunter.
//   4. Nebenbereiche (Seitenleiste) zuletzt zeichnen, sonst uebermalt.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";

const bg = readFileSync(new URL("../background.js", import.meta.url), "utf8");
const cs = readFileSync(new URL("../content.js", import.meta.url), "utf8");
const bgChrome = readFileSync(new URL("../chrome-mv3/background.js", import.meta.url), "utf8");
const csChrome = readFileSync(new URL("../chrome-mv3/content.js", import.meta.url), "utf8");

function massstab(layout, pxW, pxH) {
  const von = bg.indexOf("const breiteCssFuerMassstab");
  const bis = bg.indexOf(";", bg.indexOf("const dprY", von)) + 1;
  const segments = [{ pxW, pxH }];
  let dprY;
  eval(bg.slice(von, bis).replace("const dprY", "dprY"));
  return dprY;
}

test("Massstab kommt aus der Fensterbreite (Gmail-Fall 27.09.2026)", () => {
  // Gmail: Fenster 1666, Container 1354, Aufnahme 1832x1261 bei dpr 1,0909
  const d = massstab({ winW: 1666, viewportW: 1354, winH: 1147, viewportH: 1019 }, 1832, 1261);
  assert.ok(Math.abs(d - 1832 / 1666) < 1e-9, "1832/1666 erwartet, bekam " + d);
  assert.ok(Math.abs(d - 1.353) > 0.2, "die Containerbreite (1832/1354 = 1,353) darf nicht mehr gelten");
});

test("Fenster-Scroll: beide Breiten gleich, Massstab unveraendert", () => {
  const d = massstab({ winW: 1489, viewportW: 1489, winH: 900, viewportH: 900 }, 1489, 900);
  assert.equal(d, 1);
});

test("Schrittweite folgt dem Ausschnitt, nicht der Containerhoehe", () => {
  const von = bg.indexOf("const sichtbarCss");
  const bis = bg.indexOf(";", bg.indexOf("const stepCss", von)) + 1;
  const block = bg.slice(von, bis);
  const rechne = (layout) => { let stepCss; eval(block.replace("const stepCss", "stepCss")); return stepCss; };
  // Testseite 27.09.2026: Container 907 hoch, Kopfzeile 224 -> Ausschnitt 683
  assert.equal(rechne({ isWindow: false, viewportH: 907, clip: { h: 683 } }), 643);
  // Fenster-Scroll: wie bisher
  assert.equal(rechne({ isWindow: true, viewportH: 1019, clip: null }), 979);
});

test("Content-Skript vermisst die klebende Kopfzeile und meldet sie im Zuschnitt", () => {
  assert.ok(cs.includes("function stickyKopfImContainer("), "Vermessung fehlt");
  assert.ok(/return \{ x, y, w, h, kopf \};/.test(cs), "Zuschnitt traegt kein Feld kopf");
  assert.ok(cs.includes('cs.position !== "sticky" && cs.position !== "fixed"'), "nur sticky/fixed zaehlen");
});

test("Nebenbereiche werden nach Fuellung und Segmenten gezeichnet", () => {
  const kontext = bg.indexOf("const frameH = segments[0].pxH;");
  const fuellung = bg.indexOf("bigCtx.fillRect(srcX, frameH, clipW, bigH - frameH);", kontext);
  const schleife = bg.indexOf("for (let i = 1; i < segments.length; i++)", kontext);
  const seite = bg.indexOf("drawSideAreas();", kontext);
  assert.ok(kontext > 0 && fuellung > 0 && schleife > 0 && seite > 0, "Bloecke nicht gefunden");
  assert.ok(seite > fuellung && seite > schleife, "drawSideAreas() muss nach Fuellung und Segmentschleife stehen");
});

test("Chrome-Fassung traegt dieselben Aenderungen", () => {
  for (const s of ["breiteCssFuerMassstab", "sichtbarCss"]) assert.ok(bgChrome.includes(s), s + " fehlt in chrome-mv3/background.js");
  assert.ok(csChrome.includes("function stickyKopfImContainer("), "chrome-mv3/content.js ohne Kopfzeilen-Vermessung");
});
