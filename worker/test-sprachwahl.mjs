/* Prueft die Sprachwahl fuer Agenten, bevor sie live geht.
 *
 * Der Worker laesst sich nicht beobachten, ohne ihn zu deployen. Ein Deploy
 * als erster Test waere die falsche Reihenfolge: die Route faengt die ganze
 * Zone ab. Hier laufen die beiden reinen Funktionen gegen die echten
 * ausgelieferten Seiten aus docs/.
 *
 *   node worker/test-sprachwahl.mjs
 */
import { readFileSync, existsSync } from "node:fs";

const quelle = readFileSync(new URL("./mcp.js", import.meta.url), "utf8");

// Die drei Funktionen samt ihrer Konstante herausloesen.
const teile = [];
for (const name of ["const AGENT_SPRACHEN", "function sprachWunsch",
                    "function passendeSprache", "function aufEineSprache"]) {
  const von = quelle.indexOf(name);
  if (von < 0) throw new Error(`nicht gefunden: ${name}`);
  const rest = quelle.slice(von);
  const bis = rest.search(/\n(?=(const |function |\/\* |\/\*\*))/);
  teile.push(rest.slice(0, bis > 0 ? bis : rest.length));
}
const m = await import("data:text/javascript," + encodeURIComponent(
  teile.join("\n") +
  "\nexport { sprachWunsch, passendeSprache, aufEineSprache };"));

let fehler = 0;
function pruefe(name, ist, soll) {
  const ok = JSON.stringify(ist) === JSON.stringify(soll);
  console.log(`  ${ok ? "OK  " : "FEHL"}  ${name}`);
  if (!ok) {
    console.log(`          erwartet: ${JSON.stringify(soll)}`);
    console.log(`          bekommen: ${JSON.stringify(ist)}`);
    fehler++;
  }
}

function anfrage(url, kopf = {}) {
  return { url, headers: { get: (k) => kopf[k.toLowerCase()] ?? null } };
}

console.log("=== A. Sprachwunsch lesen ===");
pruefe("?lang=de schlaegt alles", m.sprachWunsch(
  anfrage("https://x/y?lang=de", { "accept-language": "fr" })), "de");
pruefe("Accept-Language einfach", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "fr" })), "fr");
// Ohne q-Auswertung gewinnt die erste genannte Sprache — das ist falsch.
pruefe("q-Werte entscheiden", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "en;q=0.3, de;q=0.9" })), "de");
pruefe("Regionalform faellt zurueck", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "de-AT" })), "de");
pruefe("pt-PT -> pt-BR", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "pt-PT" })), "pt-BR");
pruefe("zh-TW -> zh-CN", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "zh-TW" })), "zh-CN");
pruefe("unbekannt -> keine Wahl", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "kl-GL" })), null);
pruefe("nichts angegeben", m.sprachWunsch(anfrage("https://x/y")), null);
pruefe("* wird ignoriert", m.sprachWunsch(
  anfrage("https://x/y", { "accept-language": "*" })), null);

console.log("\n=== B. Filtern echter Seiten ===");
const seiten = [
  ["../docs/notes/smaller-files-better-ocr/index.html", "smaller-files"],
  ["../docs/mitmachen/index.html", "mitmachen"],
  ["../docs/how-to/for-students/index.html", "for-students (h1 traegt data-lang)"],
];
for (const [rel, name] of seiten) {
  const pfad = new URL(rel, import.meta.url);
  if (!existsSync(pfad)) { console.log(`  ---   ${name} fehlt`); continue; }
  const html = readFileSync(pfad, "utf8");
  const alle = new Set([...html.matchAll(/data-lang="([^"]+)"/g)].map((x) => x[1]));
  const de = m.aufEineSprache(html, "de");
  const uebrig = new Set([...de.html.matchAll(/data-lang="([^"]+)"/g)].map((x) => x[1]));
  pruefe(`${name}: nur noch de uebrig`, [...uebrig], ["de"]);
  pruefe(`${name}: Sprache gemeldet`, de.sprache, "de");
  const kleiner = de.html.length < html.length * 0.6;
  console.log(`        ${alle.size} Sprachen, ${html.length} -> ${de.html.length} Zeichen`
              + `  ${kleiner ? "" : "  (kaum kleiner — verdaechtig)"}`);
  if (!kleiner) fehler++;
}

console.log("\n=== C. Grenzfaelle ===");
{
  const ohne = "<html><body><p>nur eine Sprache</p></body></html>";
  const r = m.aufEineSprache(ohne, "de");
  pruefe("Seite ohne Bloecke bleibt unveraendert", r.html, ohne);
  pruefe("und meldet keine Sprache", r.sprache, null);
}
{
  const html = readFileSync(new URL("../docs/mitmachen/index.html", import.meta.url), "utf8");
  // Nicht vorhandene Sprache: der Standardblock muss uebrig bleiben, nicht nichts.
  const r = m.aufEineSprache(html, "kl");
  const uebrig = new Set([...r.html.matchAll(/data-lang="([^"]+)"/g)].map((x) => x[1]));
  pruefe("unbekannte Sprache -> Standardblock", [...uebrig], ["en"]);
  const leer = m.aufEineSprache(html, null);
  pruefe("ohne Wunsch -> Standardblock", leer.sprache, "en");
}

console.log("\n" + "=".repeat(58));
if (fehler) { console.log(`${fehler} FEHLER`); process.exit(1); }
console.log("Sprachwahl arbeitet richtig.");
