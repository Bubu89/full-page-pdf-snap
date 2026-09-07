// Zuschnitt des Client-Namens (M6, 17.08.2026)
//
// `clientInfo.name` ist fremdbestimmte Eingabe und wandert in einen
// KV-Schluessel der Form `c:<name>:<tag>`. Ein Doppelpunkt darin wuerde die
// Struktur zerlegen, ein langer Name den Namensraum zumuellen. Dieser Test
// haelt beides fest.
//
// Aufruf: node tools/klientname-test.js

const fs = require("fs");
const src = fs.readFileSync(__dirname + "/../worker/mcp.js", "utf8");
const treffer = src.match(/function klientName[\s\S]*?\n\}/);
if (!treffer) {
  console.error("klientName nicht gefunden — wurde sie umbenannt?");
  process.exit(2);
}
eval(treffer[0]);

const faelle = [
  ["claude-ai", "claude-ai", "gewoehnlicher Name bleibt"],
  ["Claude Desktop", "Claude-Desktop", "Leerzeichen wird Strich"],
  ["", "ohne-Namen", "leer"],
  [null, "ohne-Namen", "fehlt"],
  [undefined, "ohne-Namen", "nicht gesetzt"],
  ["a:b:c", "a-b-c", "Doppelpunkt kann den Schluessel nicht zerlegen"],
  ["x".repeat(200), "x".repeat(40), "Laenge gedeckelt"],
  ["---", "ohne-Namen", "nur Striche zaehlt als leer"],
  ["../../etc/passwd", "..-..-etc-passwd", "Pfadtrenner entschaerft"],
  ["  cursor  ", "cursor", "Rand abgeschnitten"],
  ["mcp\nclient", "mcp-client", "Zeilenumbruch"],
  ["Ünïcödé", "n-c-d", "Nicht-ASCII wird ersetzt, Randstriche fallen weg"],
];

let fehler = 0;
for (const [ein, soll, warum] of faelle) {
  const ist = klientName(ein);
  const ok = ist === soll;
  if (!ok) fehler++;
  console.log(
    (ok ? "ok    " : "FAIL  ")
    + String(JSON.stringify(ein)).slice(0, 26).padEnd(28)
    + "-> " + JSON.stringify(ist).padEnd(22)
    + (ok ? warum : `erwartet ${JSON.stringify(soll)}`));
}

// Gegenprobe: laesst sich aus dem erzeugten Schluessel der Tag wieder
// sauber loesen? Genau daran scheitert eine naive split(":")[1]-Zerlegung.
const proben = ["claude-ai", "Claude Desktop", "a:b:c", ""];
for (const p of proben) {
  const schluessel = `c:${klientName(p)}:2026-08-17`;
  const teile = schluessel.split(":");
  const tag = teile[teile.length - 1];
  const name = teile.slice(1, -1).join(":");
  const ok = tag === "2026-08-17" && name === klientName(p);
  if (!ok) fehler++;
  console.log((ok ? "ok    " : "FAIL  ")
    + `Schluessel ${schluessel}`.slice(0, 50).padEnd(52)
    + `Tag=${tag} Name=${name}`);
}

console.log(`\nklientName: ${fehler} Fehler`);
process.exit(fehler ? 1 : 0);
