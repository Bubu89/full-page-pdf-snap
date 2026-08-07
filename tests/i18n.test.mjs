/* Prueft die Mehrsprachigkeit an den Stellen, an denen sie schon gebrochen ist.
 *
 * Anlass (07.08.2026): In der ausgelieferten 2.31.0 standen elf
 * Kontextmenue-Eintraege und drei Meldungstitel fest auf Deutsch im Code —
 * fuer jeden davon gab es einen uebersetzten Schluessel in allen neun
 * Sprachen, er wurde nur nicht benutzt. Jeder Nutzer weltweit sah ein
 * deutsches Menue. Aufgefallen ist es keinem Test, weil kein Test die
 * Oberflaechentexte je angesehen hat.
 *
 * Aufruf: node tests/i18n.test.mjs
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const pruefe = (bedingung, text) => {
  if (!bedingung) { console.error("  FEHLER  " + text); fehler++; }
};

// Die beiden Auslieferungen: Firefox (Wurzel) und Chrome (chrome-mv3)
const PAKETE = [
  { name: "firefox", basis: WURZEL },
  { name: "chrome",  basis: join(WURZEL, "chrome-mv3") },
];

for (const paket of PAKETE) {
  const locales = join(paket.basis, "_locales");
  if (!existsSync(locales)) { console.error(`  FEHLER  ${paket.name}: kein _locales`); fehler++; continue; }
  const sprachen = readdirSync(locales).filter(d => existsSync(join(locales, d, "messages.json")));
  const lies = l => JSON.parse(readFileSync(join(locales, l, "messages.json"), "utf8"));
  const en = lies("en");
  const keysEn = Object.keys(en).sort();

  console.log(`\n[${paket.name}]  ${sprachen.length} Sprachen, ${keysEn.length} Schluessel`);

  // 1. Jede Sprache traegt genau die Schluessel von en
  for (const l of sprachen) {
    const m = lies(l);
    const fehlend = keysEn.filter(k => !(k in m));
    const zusatz = Object.keys(m).filter(k => !(k in en));
    pruefe(fehlend.length === 0, `${paket.name}/${l}: ${fehlend.length} Schluessel fehlen (${fehlend.slice(0,3)})`);
    pruefe(zusatz.length === 0, `${paket.name}/${l}: ${zusatz.length} unbekannte Schluessel (${zusatz.slice(0,3)})`);
    for (const k of keysEn) {
      if (!(k in m)) continue;
      // Platzhalter muessen ueberall gleich sein, sonst bricht die Ersetzung
      const p = s => (String(s).match(/\$\w+\$|\$\d/g) || []).sort().join(",");
      pruefe(p(en[k].message) === p(m[k].message),
             `${paket.name}/${l}/${k}: Platzhalter weichen ab ("${p(en[k].message)}" vs "${p(m[k].message)}")`);
    }
  }

  // 2. Jeder im Code benutzte Schluessel existiert
  const dateien = readdirSync(paket.basis)
    .filter(f => /\.(js|html)$/.test(f))
    .map(f => [f, readFileSync(join(paket.basis, f), "utf8")]);
  for (const [name, text] of dateien) {
    for (const m of text.matchAll(/getMessage\(\s*["']([A-Za-z0-9_]+)["']/g))
      pruefe(m[1] in en, `${paket.name}/${name}: getMessage("${m[1]}") ohne Eintrag`);
    for (const m of text.matchAll(/data-i18n(?:-title)?="([A-Za-z0-9_]+)"/g))
      pruefe(m[1] in en, `${paket.name}/${name}: data-i18n="${m[1]}" ohne Eintrag`);
  }

  // 3. Keine fest eingebauten Oberflaechentexte im Hintergrunddienst.
  //    Genau der Fehler vom 07.08.2026. Ein Fallback nach getMessage(...) ||
  //    ist erlaubt und gewollt - geprueft wird nur der nackte Zuweisungsfall.
  const bg = readFileSync(join(paket.basis, "background.js"), "utf8");
  for (const m of bg.matchAll(/(?<!\|\|\s*)\b(title|message)\s*:\s*"([^"]{4,})"/g)) {
    const wert = m[2];
    const istProduktname = /^Full Page PDF Snap$/.test(wert);
    const sprachverdaechtig = /[äöüßÄÖÜ]|\b(oeffnen|Aufnahme|Speicher|Ganze|Einstellungen|Qualitaet|verstecken|zeigen|bitte|warten|Fehler|Hinweis)\b/.test(wert);
    pruefe(istProduktname || !sprachverdaechtig,
      `${paket.name}/background.js: fester Oberflaechentext ${m[1]}: "${wert.slice(0, 52)}" - gehoert in _locales`);
  }

  // 4. Die erzeugte Tabelle stimmt mit _locales ueberein. Sie traegt die
  //    eigene Sprachwahl; laeuft sie auseinander, zeigt die Erweiterung
  //    stillschweigend den Stand von vorgestern.
  const datei = join(paket.basis, "i18n-data.js");
  if (existsSync(datei)) {
    const roh = readFileSync(datei, "utf8");
    const treffer = roh.match(/=\s*(\{[\s\S]*\});?\s*$/);
    pruefe(!!treffer, `${paket.name}/i18n-data.js: Tabelle nicht lesbar`);
    if (treffer) {
      const tabelle = JSON.parse(treffer[1]);
      for (const l of sprachen) {
        const quelle = lies(l);
        pruefe(l in tabelle, `${paket.name}/i18n-data.js: Sprache ${l} fehlt - build-i18n-data.py erneut laufen lassen`);
        if (!(l in tabelle)) continue;
        const abweichend = Object.keys(quelle).filter(k => tabelle[l][k] !== quelle[k].message);
        pruefe(abweichend.length === 0,
          `${paket.name}/i18n-data.js/${l}: ${abweichend.length} Texte veraltet (${abweichend.slice(0,3)}) - build-i18n-data.py erneut laufen lassen`);
      }
    }
  }
}

// 5. Beide Auslieferungen zeigen dieselben Texte
const lade = (p, l) => JSON.parse(readFileSync(join(p, "_locales", l, "messages.json"), "utf8"));
for (const l of readdirSync(join(WURZEL, "_locales"))) {
  if (!existsSync(join(WURZEL, "chrome-mv3", "_locales", l, "messages.json"))) continue;
  const a = lade(WURZEL, l), b = lade(join(WURZEL, "chrome-mv3"), l);
  const anders = Object.keys(a).filter(k => k in b && a[k].message !== b[k].message);
  pruefe(anders.length === 0, `firefox/chrome ${l}: ${anders.length} Texte weichen ab (${anders.slice(0,3)})`);
}

console.log(fehler === 0 ? "\ni18n: alles in Ordnung" : `\ni18n: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
