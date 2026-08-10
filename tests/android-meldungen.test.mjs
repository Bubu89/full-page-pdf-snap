/* Prueft, was auf Android in der Benachrichtigungsleiste landet.
 *
 * Anlass (07.08.2026): Auf dem Telefon standen drei Benachrichtigungen fuer
 * einen Vorgang - zwei Fehler und eine Erfolgsmeldung:
 *
 *   Fehler: can't access lexical declaration 'platform' before initialization
 *   Fehler: Speichern fehlgeschlagen.
 *   PDF im Browser bereit — dort steht die Download-Option zur Verfuegung.
 *
 * Der erste war ein echter Programmfehler. Der zweite gar keiner: Auf Android
 * ist der Download-Weg nicht der vorgesehene, das Scheitern war eingeplant.
 * Der dritte stand fest auf Deutsch, unabhaengig von der eingestellten
 * Sprache.
 *
 * Aufruf: node tests/android-meldungen.test.mjs
 */
import { readFileSync } from "node:fs";

let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

for (const datei of ["background.js", "chrome-mv3/background.js"]) {
  const s = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const kurz = datei.includes("chrome") ? "chrome " : "firefox";

  // 1. Keine rohen Fehlertexte mehr an den Nutzer
  const roh = (s.match(/notifyError\(\s*e(\s*&&\s*e\.message[^)]*)?\.?m?e?s?s?a?g?e?\s*\)/g) || [])
    .filter(x => !x.includes("getMessage"));
  ok(roh.length === 0, `${kurz}: keine rohen Fehlertexte in der Leiste (${roh.length})`);

  // 2. Die Erfolgsmeldung laeuft ueber die Uebersetzung
  ok(s.includes('getMessage("androidFertig")'),
     `${kurz}: Rueckfall-Meldung uebersetzt (androidFertig)`);
  ok(s.includes('getMessage("androidGespeichert"'),
     `${kurz}: Erfolgsmeldung nennt die abgelegte Datei (androidGespeichert)`);
  ok(!s.includes('notifyInfo("PDF im Browser bereit'),
     `${kurz}: alte deutsche Erfolgsmeldung entfernt`);

  // 3. "Speichern fehlgeschlagen" nur noch am Rechner
  const i = s.indexOf('notifyError("Speichern fehlgeschlagen.")');
  ok(i === -1 || s.slice(Math.max(0, i - 120), i).includes("!platformForSave.isAndroid"),
     `${kurz}: "Speichern fehlgeschlagen" nur ausserhalb von Android`);

  /* 4. Auf Android wird wieder heruntergeladen - ohne Unterordner.
   *
   * Bis 2.31.20 stand hier das Gegenteil: "kein Download-Versuch auf Android".
   * Diese Annahme war falsch. Firefox fuer Android beherrscht
   * downloads.download; was scheiterte, war der Unterordner im Dateinamen, den
   * die Android-Fassung nicht kennt. Der Reiter, der stattdessen aufging, war
   * fuer den Nutzer der eigentliche Aerger. */
  ok(s.includes("speichereImTab("),
     `${kurz}: Android legt aus der Seite heraus ab statt einen Reiter zu oeffnen`);
  ok(!s.includes("Android: PDF direkt im Tab oeffnen"),
     `${kurz}: die alte Begruendung steht nicht mehr im Code`);

  // 5. Der Anzeige-Tab schliesst sich nach dem Herunterladen, still
  ok(s.includes("beobachteDownloadUndSchliesse"),
     `${kurz}: Anzeige-Tab wird nach dem Download geschlossen`);
  const j = s.indexOf("browser.tabs.remove(tabId)");
  ok(j > -1 && !s.slice(j, j + 300).includes("notifyError"),
     `${kurz}: Scheitern beim Schliessen erzeugt keine Meldung`);

  // 6. Der Fertig-Ton darf die Aufnahme nicht gefaehrden
  const k = s.indexOf("async function fertigTon(");
  ok(k > -1 && s.slice(k, k + 500).includes("catch"),
     `${kurz}: Fertig-Ton in try/catch`);
}

console.log(fehler === 0 ? "\nAndroid-Meldungen: in Ordnung" : `\nAndroid-Meldungen: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
