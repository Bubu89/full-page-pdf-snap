/* Prueft isSideNavigation: Welche fixed/sticky-Elemente sind Navigation
   (bleiben im ersten Segment stehen) und welche sind Stoerer (fliegen raus)?
   Geometrie aus echten Seiten. */
const winW = 1384, winH = 805;
function isSideNavigation(r) {
  const tall = r.height >= winH * 0.5;
  const narrow = r.width <= winW * 0.4;
  const edge = Math.max(12, winW * 0.05);
  const atEdge = r.left <= edge || r.right >= winW - edge;
  return tall && narrow && atEdge;
}
const R = [];
const check = (name, rect, want) => {
  const got = isSideNavigation({ ...rect, right: rect.left + rect.width });
  R.push(`${got === want ? "OK  " : "FEHL"}  ${want ? "behalten  " : "ausblenden"}  ${name}`);
  return got === want;
};

// Aus kimi.com/code/docs gemessen
check("VitePress Sidebar links (272x805 @0)",      {left:0,    width:272,  height:805}, true);
check("VitePress Inhaltsverz. rechts (224x805)",   {left:1113, width:224,  height:805}, true);
check("VitePress Sticky-Kopfzeile (1369x64)",      {left:0,    width:1369, height:64},  false);
check("VitePress Curtain (257x64)",                {left:0,    width:257,  height:64},  false);
check("VitePress Aside-Curtain (224x32)",          {left:1113, width:224,  height:32},  false);

// Typische Stoerer anderer Seiten
check("Cookie-Banner unten (1384x180)",            {left:0,    width:1384, height:180}, false);
check("Chat-Blase rechts unten (64x64)",           {left:1300, width:64,   height:64},  false);
check("Newsletter-Overlay mittig (600x400)",       {left:392,  width:600,  height:400}, false);
check("Schwebender Zurueck-Button (48x48)",        {left:20,   width:48,   height:48},  false);
// Grenzfaelle
check("Schmale Navi mit Aussenabstand (200x700)",  {left:40,   width:200,  height:700}, true);
check("Halbhohe Spalte am Rand (200x300)",         {left:0,    width:200,  height:300}, false);
check("Breite Spalte am Rand (700x805)",           {left:0,    width:700,  height:805}, false);


/* --- Zweiter Teil: wer wird tatsaechlich ausgeblendet? -----------------
 *
 * Die Geometrie-Erkennung allein genuegt nicht. visibility:hidden vererbt
 * sich: Wird ein VORFAHRE der Navigationsspalte ausgeblendet, verschwindet
 * die Spalte mit - obwohl sie ausdruecklich behalten werden sollte.
 *
 * Gefunden am 07.08.2026 am Cloudflare-Dashboard: Im PDF blieb der Platz
 * der Navigation leer, oben ragte noch das halbe Logo herein. Der Fehler
 * war nicht die Erkennung - die Spalte stand korrekt in "keep" - sondern
 * dass ihr Elterncontainer als grossflaechiges Overlay eingestuft und
 * ausgeblendet wurde.
 */
const SCHUTZ_VORFAHREN = process.env.OHNE_SCHUTZ !== '1';
function auswahl(baum, includeSideNav) {
  // baum: [{name, rect, fixiert, overlay, kinder:[...]}]
  const alle = [];
  (function sammle(liste, eltern) {
    for (const k of liste) {
      k.eltern = eltern; alle.push(k);
      sammle(k.kinder || [], k);
    }
  })(baum, null);
  const enthaelt = (a, b) => { for (let e = b; e; e = e.eltern) if (e === a) return true; return false; };

  const keep = [], candidates = [];
  for (const el of alle) {
    if (!el.fixiert && !el.overlay) continue;
    const r = { ...el.rect, right: el.rect.left + el.rect.width };
    if (!includeSideNav && isSideNavigation(r)) keep.push(el);
    else candidates.push(el);
  }
  const versteckt = [];
  for (const el of candidates) {
    // Wie im Code: k.contains(el) - was INNERHALB einer behaltenen Spalte
    // liegt, bleibt stehen.
    if (keep.some(k => enthaelt(k, el))) continue;
    // Der Zusatz vom 07.08.2026: umgekehrt ebenso. Ein Element, das eine
    // behaltene Spalte UMSCHLIESST, darf nicht ausgeblendet werden -
    // visibility:hidden vererbt sich und nimmt die Spalte mit.
    if (SCHUTZ_VORFAHREN && keep.some(k => enthaelt(el, k))) continue;
    versteckt.push(el);
  }
  // sichtbar = nicht selbst versteckt und kein Vorfahre versteckt
  const sichtbar = n => !versteckt.some(v => enthaelt(v, n));
  return { versteckt, sichtbar };
}

// Cloudflare-Dashboard: Navigationsspalte in einem grossflaechigen,
// hoch gestapelten Container.
const navi   = { name: "nav",   rect: {left:0, width:245, height:1000}, fixiert: true,  kinder: [] };
const huelle = { name: "shell", rect: {left:0, width:1600, height:1000}, overlay: true, kinder: [navi] };
const banner = { name: "cookie", rect: {left:0, width:1600, height:180}, fixiert: true, kinder: [] };
const a = auswahl([huelle, banner], false);
R.push((a.sichtbar(navi) ? "OK  " : "FEHL") + "  behalten    Navigationsspalte im ausgeblendeten Elterncontainer");
R.push((!a.sichtbar(banner) ? "OK  " : "FEHL") + "  ausblenden  Cookie-Banner daneben");

// Und im zweiten Durchgang muss die Spalte weg sein, sonst wandert sie mit.
const b = auswahl([huelle, banner], true);
R.push((!b.sichtbar(navi) ? "OK  " : "FEHL") + "  ausblenden  Navigationsspalte ab dem zweiten Segment");


/* --- Wann zaehlt ein Bereich als eigenstaendig scrollend? --------------
 *
 * Am 07.08.2026 wurde "hidden" ohne weitere Bedingung zugelassen, damit
 * Navigationsspalten mit verborgener Bildlaufleiste erfasst werden. Das war
 * zu weit gefasst: "hidden" ist das haeufigste Overflow-Verhalten ueberhaupt.
 * Karten, Umbruchcontainer und Abschnitte wurden dadurch zu eigenstaendigen
 * Bereichen erklaert und einzeln durchgescrollt - vom Cloudflare-Dashboard kam
 * danach nur noch ein Bildschirm ins PDF statt der ganzen Seite.
 *
 * Jetzt gilt: erklaert scrollbar genuegt fuer sich; "hidden" nur, wenn das
 * Element auch nach Lage und Form eine Navigationsspalte ist.
 */
function zaehltAlsBereich(overflowY, rect) {
  if (/auto|scroll|overlay/.test(overflowY)) return true;
  if (overflowY === "hidden") return isSideNavigation({ ...rect, right: rect.left + rect.width });
  return false;
}
const B = (name, overflowY, rect, want) =>
  R.push(`${zaehltAlsBereich(overflowY, rect) === want ? "OK  " : "FEHL"}  ${want ? "Bereich   " : "kein Bereich"}  ${name}`);

B("Navigationsspalte, erklaert scrollbar", "auto",   {left:0,   width:245, height:805}, true);
B("Navigationsspalte, Leiste verborgen",   "hidden", {left:0,   width:245, height:805}, true);
B("Inhaltskarte mit hidden",               "hidden", {left:320, width:900, height:400}, false);
B("Umbruchcontainer mit hidden",           "hidden", {left:320, width:900, height:805}, false);
B("schmaler Kasten mittig, hidden",        "hidden", {left:600, width:200, height:700}, false);
B("Inhaltsbereich, erklaert scrollbar",    "scroll", {left:320, width:900, height:805}, true);
B("visible zaehlt nie",                    "visible",{left:0,   width:245, height:805}, false);

console.log(R.join("\n"));
console.log("\nERGEBNIS: " + (R.some(l => l.startsWith("FEHL")) ? "FEHLER" : "ALLE BESTANDEN"));
process.exit(R.some(l => l.startsWith("FEHL")) ? 1 : 0);
