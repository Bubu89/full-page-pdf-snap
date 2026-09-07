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

  /* 1b. Steht in der fremden Datei wirklich eine Uebersetzung?
   *
   * Die Pruefung oben sieht nur nach, ob ein Schluessel VORHANDEN ist. Ein
   * englischer Satz in der spanischen Datei ist danach einwandfrei — und
   * genau so blieben fuenf Texte ueber Jahre in sieben Sprachen englisch,
   * darunter "Capturing …" und "Saved", die bei JEDER Aufnahme im Popup
   * stehen. Aufgefallen ist es erst, als jemand gezielt danach fragte.
   *
   * Gleichlautend heisst nicht immer unuebersetzt: "page" ist im
   * Franzoesischen dasselbe Wort, und Eigennamen wie Zotero oder APA werden
   * nirgends uebersetzt. Solche Faelle stehen namentlich in der Ausnahme —
   * eine Liste, die man beim Eintragen begruenden muss, statt einer Schwelle,
   * die stillschweigend alles durchlaesst. */
  const DARF_GLEICH_SEIN = new Set([
    "optImmerRisKurz",   // "(Zotero, Citavi)" — Programmnamen
    "optImmerStile",     // "(APA, MLA, Chicago, …)" — Namen von Zitierweisen
    "menuScale20",       // "2.0x — maximum" — im Franzoesischen gleich
    "resultPage",        // "page" — im Franzoesischen gleich
    "resultPages",       // "pages" — im Franzoesischen gleich
    "popupArtikel",      // "Article" — im Franzoesischen gleich
    "popupAusrichtung",  // "Orientation" — im Franzoesischen gleich
    "popupHoch",         // "Portrait" — im Franzoesischen gleich
  ]);

  for (const l of sprachen) {
    if (l === "en") continue;
    const m = lies(l);
    /* Ohne Laengenschwelle.
     *
     * Der erste Entwurf pruefte erst ab acht Zeichen, weil kurze Texte oft
     * Abkuerzungen sind. Der Gegentest zeigte, was das kostet: "Saved"
     * rutschte durch — ausgerechnet einer der beiden Texte, die bei jeder
     * Aufnahme im Popup stehen und die den Anlass fuer diese Pruefung gaben.
     * Ueber den gesamten Bestand gemessen erzeugt auch die Schwelle 1 keinen
     * einzigen Fehlalarm. Kommt spaeter ein kurzer Text dazu, der zu Recht in
     * mehreren Sprachen gleich lautet, gehoert er benannt in die Liste oben —
     * nicht stillschweigend unter eine Schwelle. */
    const gleich = keysEn.filter(k =>
      !DARF_GLEICH_SEIN.has(k) &&
      k in m &&
      m[k].message === en[k].message);
    pruefe(gleich.length === 0,
           `${paket.name}/${l}: ${gleich.length} Texte unuebersetzt (${gleich.slice(0, 3)})`);
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

  /* 2b. Kein sichtbarer Text ohne Uebersetzung — auch nicht in Attributen.
   *
   * Gemeldet am 18.08.2026 mit einem Bildschirmfoto: Die Oberflaeche stand auf
   * Deutsch, der Hinweis am Zitationsschalter erschien englisch. Ursache waren
   * drei title-Attribute im Popup, die beim Verschlanken direkt als Text
   * hineingeschrieben wurden, ohne data-i18n-title daneben.
   *
   * Die Pruefungen 1 und 2 konnten das nicht sehen: Sie vergleichen die
   * Sprachdateien untereinander und pruefen, ob jeder BENUTZTE Schluessel
   * existiert. Ein Text, der gar keinen Schluessel hat, kommt darin nicht vor.
   *
   * Geprueft wird deshalb umgekehrt: Jedes title-Attribut mit mehr als ein
   * paar Zeichen braucht ein data-i18n-title daneben. */
  for (const [name, text] of dateien) {
    if (!/\.html$/.test(name)) continue;
    const ohne = [];
    for (const m of text.matchAll(/<[^>]*\stitle="([^"]{12,})"[^>]*>/g)) {
      if (!/data-i18n-title=/.test(m[0])) ohne.push(m[1].slice(0, 40));
    }
    pruefe(ohne.length === 0,
           `${paket.name}/${name}: ${ohne.length} title-Attribute ohne Uebersetzung` +
           (ohne.length ? ` ("${ohne[0]}…")` : ""));
  }

  /* 3. Keine fest eingebauten Oberflaechentexte im Hintergrunddienst.
   *
   * Genau der Fehler vom 07.08.2026 — und am 18.08.2026 noch einmal, an einer
   * Stelle, die diese Pruefung nicht ansah: Die Meldungen fuer geschuetzte
   * Seiten und fehlende Reiter standen als "reason:" im Code, fest auf
   * Deutsch, obwohl es sie unter noTab, internalPage, protectedPage und
   * noScripts in allen neun Sprachen gab. Die Schluessel lagen unbenutzt
   * herum. Ein japanischer Nutzer bekam "Chrome schuetzt diese Seite".
   *
   * Deshalb sieht die Pruefung jetzt auch auf "reason:" und auf die
   * Hinweis-Ausnahme. Ein Rueckfall nach getMessage(...) || oder hinter
   * txt(...) ist erlaubt und gewollt: Er greift nur, wenn die Uebersetzung
   * fehlschlaegt, und eine deutsche Meldung ist besser als eine leere. */
  const bg = readFileSync(join(paket.basis, "background.js"), "utf8");
  const SPRACHVERDACHT = /[äöüßÄÖÜ]|\b(oeffnen|Aufnahme|Speicher|Ganze|Einstellungen|Qualitaet|verstecken|zeigen|bitte|Bitte|warten|Fehler|Hinweis|schuetzt|geladen|wechseln|erlaubt)\b/;

  for (const m of bg.matchAll(/(?<!\|\|\s*)\b(title|message|reason)\s*:\s*"([^"]{4,})"/g)) {
    const wert = m[2];
    // Steht der Text hinter txt("schluessel", …), ist er der Rueckfall.
    const davor = bg.slice(Math.max(0, m.index - 90), m.index + 30);
    const istRueckfall = /txt\s*\(\s*["'][A-Za-z0-9_]+["']\s*,/.test(davor);
    const istProduktname = /^Full Page PDF Snap$/.test(wert);
    pruefe(istProduktname || istRueckfall || !SPRACHVERDACHT.test(wert),
      `${paket.name}/background.js: fester Oberflaechentext ${m[1]}: "${wert.slice(0, 52)}" - gehoert in _locales`);
  }

  // Dasselbe fuer die Hinweis-Ausnahme, die dem Nutzer unmittelbar angezeigt wird.
  for (const m of bg.matchAll(/makeUserHintError\(\s*"([^"]{4,})"/g)) {
    pruefe(!SPRACHVERDACHT.test(m[1]),
      `${paket.name}/background.js: fester Hinweistext "${m[1].slice(0, 52)}" - gehoert in _locales`);
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
