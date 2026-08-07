/* Stellt die beiden Scroll-Schleifen aus background.js nach und prueft:
   - wird das Ende erkannt?
   - hoert die Aufnahme dann auf (keine Wiederholung)?
   - entstehen Luecken?
   Ein Container klemmt scrollTop auf [0, max] - genau wie der Browser. */
const R = [];
const ok = (c, m) => { R.push(`${c ? "OK  " : "FEHL"}  ${m}`); return c; };

function container(max) {
  let top = 0;
  return { set: (y) => { top = Math.max(0, Math.min(max, y)); return top; }, max };
}

// --- Hauptbereich: Schleife aus captureFullPageInner ---------------------
function mainLoop(totalH, viewportH) {
  const maxScroll = Math.max(0, totalH - viewportH);
  const stepCss = Math.max(100, viewportH - 40);
  const c = container(maxScroll);
  const shots = [];
  let y = 0, lastActualY = -1, stuck = 0, safety = 0;
  while (true) {
    const actualY = c.set(Math.min(y, maxScroll));
    if (Math.abs(actualY - lastActualY) <= 2 && shots.length > 0) {
      if (++stuck >= 3) break;
    } else stuck = 0;
    lastActualY = actualY;
    shots.push(actualY);
    if (actualY >= maxScroll - 2) break;
    y += stepCss;
    if (y > maxScroll) y = maxScroll;
    if (++safety > 400) throw new Error("safety");
  }
  return { shots, maxScroll, viewportH };
}

// --- Nebenbereich: Schleife fuer sideScrollers ---------------------------
function sideLoop(max, h) {
  const c = container(max);
  const step = Math.max(80, h - 30);
  const shots = [];
  let sy = 0, lastY = 0, guard = 0;
  while (true) {
    const actual = c.set(sy);
    if (shots.length && actual <= lastY + 2) break;
    shots.push(actual);
    lastY = actual;
    if (actual >= max - 2) break;
    sy = actual + step;
    if (++guard > 30) break;
  }
  return shots;
}

function coverage(shots, view, total) {
  // Deckt die Vereinigung der Fenster [y, y+view) den Bereich [0,total) ab?
  const holes = [];
  let reach = 0;
  for (const y of shots.slice().sort((a, b) => a - b)) {
    if (y > reach) holes.push([reach, y]);
    reach = Math.max(reach, y + view);
  }
  if (reach < total) holes.push([reach, total]);
  return holes;
}

console.log("HAUPTBEREICH");
for (const [total, view, label] of [
  [2400, 741, "glatt teilbar-nah"],
  [2401, 741, "ungerade Resthoehe"],
  [800, 741, "kaum laenger als ein Fenster"],
  [741, 741, "exakt ein Fenster"],
  [50000, 741, "sehr lange Seite"],
]) {
  const { shots, maxScroll } = mainLoop(total, view);
  const last = shots[shots.length - 1];
  const holes = coverage(shots, view, total);
  const dup = shots.length !== new Set(shots).size;
  ok(last === maxScroll, `${label}: Ende erreicht (${last}/${maxScroll}, ${shots.length} Segmente)`);
  ok(!dup, `${label}: keine Position doppelt aufgenommen`);
  ok(holes.length === 0, `${label}: keine Luecke${holes.length ? " " + JSON.stringify(holes) : ""}`);
}

console.log("\nNEBENBEREICH");
for (const [max, h, label] of [
  [1699, 741, "Gmail-artige Labelliste"],
  [100, 741, "knapp ueber der Schwelle"],
  [5000, 300, "schmales, langes Menue"],
  [0, 741, "kein Ueberhang"],
]) {
  const shots = sideLoop(max, h);
  const last = shots[shots.length - 1];
  const holes = coverage(shots, h, max + h);
  ok(last === max, `${label}: Ende erreicht (${last}/${max}, ${shots.length} Aufnahmen)`);
  ok(shots.length === new Set(shots).size, `${label}: keine Wiederholung derselben Position`);
  ok(holes.length === 0, `${label}: lueckenlos abgedeckt`);
}


/* --- Seitenfuss als Endmarke bei endlosem Nachschub -------------------
 *
 * Frage aus der Praxis (07.08.2026): Seiten mit endlosem Scroll tragen
 * meist trotzdem einen Seitenfuss. Kann man daran nicht erkennen, wo die
 * Seite eigentlich endet, statt nach einer festen Zahl von Nachladungen
 * abzubrechen? Ja - und der Fuss ist das bessere Kriterium, weil ein
 * Zaehler je nach Netzgeschwindigkeit woanders schneidet.
 */
function findePageEnd(elemente, winW) {
  const treffer = [];
  for (const e of elemente) {
    if (e.position === "fixed" || e.position === "sticky") continue;
    if (e.display === "none" || e.visibility === "hidden") continue;
    if (e.height < 20) continue;
    if (e.width < winW * 0.5) continue;
    treffer.push(e.bottomDoc);
  }
  return treffer.length ? Math.max(...treffer) : null;
}

const W = 1384;
const pe = (name, els, want) => ok(findePageEnd(els, W) === want,
  `Seitenfuss ${name}: ${findePageEnd(els, W)} (erwartet ${want})`);

pe("gewoehnlicher Fuss unter dem Inhalt",
   [{ width: 1384, height: 220, bottomDoc: 48200, position: "static" }], 48200);
pe("mitlaufende Leiste zaehlt nicht",
   [{ width: 1384, height: 60, bottomDoc: 900, position: "fixed" }], null);
pe("Fuss in einer schmalen Spalte zaehlt nicht",
   [{ width: 260, height: 400, bottomDoc: 5000, position: "static" }], null);
pe("ausgeblendeter Fuss zaehlt nicht",
   [{ width: 1384, height: 220, bottomDoc: 48200, position: "static", display: "none" }], null);
pe("verschachtelt - der aeussere gewinnt",
   [{ width: 1384, height: 90,  bottomDoc: 47800, position: "static" },
    { width: 1384, height: 220, bottomDoc: 48200, position: "static" }], 48200);
pe("kein Fuss vorhanden -> Deckel greift", [], null);

// Zusammenspiel: mit Fuss endet die Aufnahme dort, ohne bei der Starthoehe.
// Beides muss endlich sein - dass es das nicht war, war der eigentliche Fehler.
function endlosLauf(startH, viewportH, fussEnde) {
  const grenze = fussEnde !== null ? fussEnde : startH;
  const maxScroll = Math.max(0, grenze - viewportH);
  const step = Math.max(100, viewportH - 40);
  let y = 0, schritte = 0;
  while (y < maxScroll && ++schritte < 500) y = Math.min(y + step, maxScroll);
  return { schritte, endeBei: y + viewportH };
}
const mitFuss = endlosLauf(20000, 800, 48200);
ok(mitFuss.schritte < 500 && Math.abs(mitFuss.endeBei - 48200) < 900,
   `mit Seitenfuss: endet bei ${mitFuss.endeBei} nach ${mitFuss.schritte} Schritten`);
const ohneFuss = endlosLauf(20000, 800, null);
ok(ohneFuss.schritte < 500 && Math.abs(ohneFuss.endeBei - 20000) < 900,
   `ohne Seitenfuss: endet bei ${ohneFuss.endeBei} nach ${ohneFuss.schritte} Schritten`);

console.log("\n" + R.join("\n"));
console.log("\nERGEBNIS: " + (R.some(l => l.startsWith("FEHL")) ? "FEHLER" : "ALLE BESTANDEN"));
