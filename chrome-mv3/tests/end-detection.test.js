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

console.log("\n" + R.join("\n"));
console.log("\nERGEBNIS: " + (R.some(l => l.startsWith("FEHL")) ? "FEHLER" : "ALLE BESTANDEN"));
