/* Prueft den Schalter "Hintergrund immer weiss halten".
 *
 * Anlass (07.08.2026): Bis dahin kehrte nur Schwarzweiss dunkle Oberflaechen
 * um, Graustufen gab die Seite unveraendert wieder. Wer eine Seite im
 * Dunkelmodus in Graustufen aufnahm und druckte, bekam ein fast vollstaendig
 * eingefaerbtes Blatt.
 *
 * Jetzt entscheidet ein Schalter, und er gilt fuer beide Modi. Farbaufnahmen
 * bleiben immer unberuehrt - dort waere eine Umkehr eine Verfaelschung.
 *
 * Aufruf: node tests/heller-hintergrund.test.mjs
 */
import { readFileSync } from "node:fs";
import vm from "node:vm";
const q = readFileSync("background.js", "utf8");
const c = { Uint8Array, Uint32Array, Math, console }; c.globalThis = c;
vm.createContext(c);
vm.runInContext(q.slice(q.indexOf("function farbtiefeAnwenden"), q.indexOf("\nasync function canvasToFlateBytes")), c);

const B = 200, H = 100;
const rgba = g => { const d = new Uint8Array(g.length*4); for (let i=0,j=0;i<g.length;i++,j+=4){d[j]=d[j+1]=d[j+2]=g[i];d[j+3]=255;} return d; };
const seite = (hg, tx) => { const a = new Uint8Array(B*H).fill(hg); for (let i=0;i<a.length;i+=13) a[i]=tx; return a; };

let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

// Graustufen: mittlerer Grauwert sagt, ob hell oder dunkel
const mittel = (a) => a.reduce((s,x)=>s+x,0)/a.length;
for (const [name, bild, vorgabe, sollHell] of [
  ["Graustufen, dunkle Seite, Schalter AN",  seite(25,230), true,  true],
  ["Graustufen, dunkle Seite, Schalter AUS", seite(25,230), false, false],
  ["Graustufen, helle Seite, Schalter AN",   seite(250,20), false, true],
]) {
  const { daten, bits, kanaele } = c.farbtiefeAnwenden(rgba(bild), "graustufen", B, vorgabe);
  const m = mittel(daten);
  ok(bits === 8 && kanaele === 1, `${name}: bleibt 8 bit Graustufen`);
  ok((m > 128) === sollHell, `${name}: mittlerer Wert ${m.toFixed(0)} (${sollHell ? "hell erwartet" : "dunkel erwartet"})`);
}

// Schwarzweiss: Anteil weisser Bits
const weiss = (daten, b, h) => { const bpz = Math.ceil(b/8); let n=0;
  for (let y=0;y<h;y++) for (let x=0;x<b;x++) if (daten[y*bpz+(x>>3)]&(0x80>>(x&7))) n++;
  return n/(b*h); };
for (const [name, bild, vorgabe, sollHell] of [
  ["Schwarzweiss, dunkle Seite, Schalter AN",  seite(25,230), true,  true],
  ["Schwarzweiss, dunkle Seite, Schalter AUS", seite(25,230), false, false],
]) {
  const { daten } = c.farbtiefeAnwenden(rgba(bild), "sw", B, vorgabe);
  const w = weiss(daten, B, H);
  ok((w > 0.5) === sollHell, `${name}: ${(w*100).toFixed(0)} % weiss (${sollHell ? "hell erwartet" : "dunkel erwartet"})`);
}

// Farbe bleibt unberuehrt
{
  const bild = seite(25, 230);
  const { kanaele, bits } = c.farbtiefeAnwenden(rgba(bild), "farbe", B, true);
  ok(kanaele === 3 && bits === 8, "Farbe bleibt RGB und wird nie umgekehrt");
}
process.exit(fehler ? 1 : 0);
