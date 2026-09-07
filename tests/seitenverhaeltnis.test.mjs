/* Prueft, dass Papierformat und Ausrichtung im Bildweg wirklich wirken.
 *
 * Gemeldet am 18.08.2026: "auch formatänderung querformat ect ändert die pdf
 * ausgabe nicht". Zutreffend, und in zwei Stufen:
 *
 *   1. Der Vektorweg las die Einstellung ueberhaupt nicht und lieferte weiter
 *      eine Endlosbahn. (Behoben ueber echte Blattmasse in cdp-vektor.js.)
 *   2. Im Bildweg wirkte sie, aber falsch: Dort wurden die Papiermasse in
 *      Pixel eingesetzt (794 px fuer A4 quer). Bei einer Aufnahmebreite von
 *      832 px ergibt das ein Verhaeltnis von 1:0,95 — fast quadratisch, wo
 *      1:0,71 hingehoert.
 *
 * Der Grund fuer (2) steckt in der Sache: Im Bildweg steht die Breite fest,
 * sie ist die Breite der Aufnahme. "Quer" kann deshalb nicht breiter machen,
 * nur flacher — die Hoehe muss aus dem VERHAELTNIS folgen, nicht aus einem
 * absoluten Mass.
 */
import { test } from "node:test";

let fehler = 0;
const pruefe = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

/** Dieselbe Rechnung wie in background.js: Nutzflaeche bei 15 mm Rand. */
function verhaeltnis(papier, ausrichtung) {
  const letter = papier === "letter";
  const kurz = (letter ? 216 : 210) - 30;
  const lang = (letter ? 279 : 297) - 30;
  return ausrichtung === "quer" ? (kurz / lang) : (lang / kurz);
}

test("Papierformat und Ausrichtung", () => {
  const pxW = 832;   // die Aufnahmebreite aus der Meldung

  const faelle = [
    ["a4", "hoch", 1.41, 1.55],
    ["a4", "quer", 0.60, 0.75],
    ["letter", "hoch", 1.28, 1.40],
    ["letter", "quer", 0.68, 0.82],
  ];
  for (const [papier, richtung, min, max] of faelle) {
    const v = verhaeltnis(papier, richtung);
    pruefe(v >= min && v <= max,
      `${papier} ${richtung}: Verhaeltnis 1:${v.toFixed(2)} liegt zwischen ${min} und ${max}`);
  }

  /* Quer MUSS flacher sein als hoch — das ist der Kern der Meldung.
   * Vorher war quer (0,95) fast so hoch wie hoch (1,48). */
  for (const papier of ["a4", "letter"]) {
    const hoch = verhaeltnis(papier, "hoch");
    const quer = verhaeltnis(papier, "quer");
    pruefe(quer < hoch * 0.6,
      `${papier}: quer (${quer.toFixed(2)}) ist deutlich flacher als hoch (${hoch.toFixed(2)})`);
    pruefe(Math.abs(quer - 1 / hoch) < 0.01,
      `${papier}: quer ist der Kehrwert von hoch`);
  }

  /* Und in Seitenzahlen: Ein flacheres Blatt ergibt MEHR Seiten. */
  const bigH = 3813;
  const seitenHoch = Math.ceil(bigH / (pxW * verhaeltnis("a4", "hoch")));
  const seitenQuer = Math.ceil(bigH / (pxW * verhaeltnis("a4", "quer")));
  pruefe(seitenQuer > seitenHoch,
    `A4: quer ergibt mehr Seiten als hoch (${seitenQuer} gegen ${seitenHoch})`);

  /* Gegenprobe: Die alte, falsche Rechnung wuerde durchfallen. */
  const altQuer = 794 / pxW;
  pruefe(!(altQuer < verhaeltnis("a4", "hoch") * 0.6),
    `Gegenprobe: die alte Rechnung (1:${altQuer.toFixed(2)}) waere hier durchgefallen`);

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Seitenverhaeltnis: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
