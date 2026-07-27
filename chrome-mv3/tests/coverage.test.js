/* Prueft verifyCoverage aus background.js: erkennt es fehlenden Anfang,
   fehlendes Ende und Luecken in der Mitte - je Scroll-Ebene? */
function verifyCoverage(label, positions, viewH, maxScroll) {
  if (!positions.length) return { ok: false, meldung: `${label}: keine Aufnahme` };
  const ys = positions.slice().sort((a, b) => a - b);
  const startOk = ys[0] <= 2;
  const endOk = ys[ys.length - 1] >= maxScroll - 2;
  const gaps = [];
  let reach = 0;
  for (const y of ys) {
    if (y > reach + 2) gaps.push([Math.round(reach), Math.round(y)]);
    reach = Math.max(reach, y + viewH);
  }
  if (reach < maxScroll + viewH - 2) gaps.push([Math.round(reach), Math.round(maxScroll + viewH)]);
  return { ok: startOk && endOk && gaps.length === 0, startOk, endOk, gaps };
}
const R = [];
const t = (name, pos, viewH, max, want) => {
  const r = verifyCoverage(name, pos, viewH, max);
  R.push(`${r.ok === want ? "OK  " : "FEHL"}  ${r.ok ? "vollstaendig  " : "unvollstaendig"}  ${name}`);
};
t("lueckenlos bis zum Ende",      [0, 700, 1400, 1659], 741, 1659, true);
t("Anfang fehlt",                 [700, 1400, 1659],    741, 1659, false);
t("Ende fehlt",                   [0, 700, 1400],       741, 1659, false);
t("Luecke in der Mitte",          [0, 1400, 1659],      741, 1659, false);
t("nur ein Fenster, kein Scroll", [0],                  741, 0,    true);
t("keine Aufnahme",               [],                   741, 1659, false);
t("Nebenbereich vollstaendig",    [0, 711, 1422, 1699], 741, 1699, true);
t("Nebenbereich bricht ab",       [0, 711],             741, 1699, false);
console.log(R.join("\n"));
console.log("\nERGEBNIS: " + (R.some(l => l.startsWith("FEHL")) ? "FEHLER" : "ALLE BESTANDEN"));
