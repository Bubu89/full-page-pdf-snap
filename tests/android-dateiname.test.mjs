/* Prueft, dass die Aufnahme auf Android einen Dateinamen behaelt.
 *
 * Anlass (07.08.2026): Im pCloud-Testordner lag "document(10).pdf" statt des
 * sprechenden Namens. Am Rechner stimmte er. Ursache war nicht die
 * Namensbildung - die lief korrekt -, sondern der Weg danach: Auf Android
 * wurde das fertige PDF als nackte data:-URL in einem Reiter geoeffnet.
 * Eine data:-URL traegt keinen Dateinamen, also vergibt der Browser beim
 * Speichern seinen eigenen: "document.pdf", dann "document(1).pdf" und so
 * fort. Der berechnete Name wurde nur intern gemerkt und nie weitergereicht.
 *
 * Aufruf: node tests/android-dateiname.test.mjs
 */
import { readFileSync } from "node:fs";

let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const zweig = src.slice(src.indexOf("Save A3"), src.indexOf("Save A3") + 1800);

  ok(!/tabs\.create\(\{\s*url\s*,/.test(zweig),
     `${datei}: oeffnet im Android-Zweig keine nackte data:-URL mehr`);
  ok(/zeigeErgebnisseite\(\)/.test(zweig),
     `${datei}: nutzt stattdessen die Ergebnisseite, die den Namen kennt`);
}

// Die Ergebnisseite muss den Namen auch dann anhaengen, wenn der
// Download-Zweig fehlt - auf Android ist er oft nicht verfuegbar.
for (const datei of ["chrome-mv3/result.js", "result.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/a\.download\s*=\s*name/.test(src),
     `${datei}: Rueckfall ueber einen Anker mit download-Attribut`);
  ok(src.indexOf("downloads.download") < src.indexOf("a.download = name"),
     `${datei}: erst der Download-Zweig, dann der Anker`);
}

// Gegenprobe: Ohne den Fix haette der alte Code den Test bestanden? Nein -
// diese Zeile stellt sicher, dass das Muster ueberhaupt greifen kann.
{
  const alt = `const newTab = await browser.tabs.create({ url, active: true });`;
  ok(/tabs\.create\(\{\s*url\s*,/.test(alt),
     "Gegenprobe: das Muster erkennt die alte Fassung tatsaechlich");
}


/* Der Name soll auch sagen, worum es geht - nicht nur woher und wann.
 * Bis 2.31.18 lautete die Voreinstellung "{site}_{date}_{time}_{n}": Website,
 * Datum, Uhrzeit, laufende Nummer. Wer die Datei ein Jahr spaeter wiederfand,
 * sah daran nicht das Thema. */
for (const datei of ["chrome-mv3/background.js", "background.js",
                     "options.js", "chrome-mv3/options.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(!/\{site\}_\{date\}_\{time\}_\{n\}/.test(src.replace(/const ALT = "[^"]*"/g, "")),
     `${datei}: alte Vorlage nur noch in der Migration`);
  ok(/\{title\}_\{site\}_\{date\}_\{time\}/.test(src),
     `${datei}: Voreinstellung nennt den Titel zuerst`);
}

// Bestehende Installationen ziehen mit - aber nur die unangetasteten.
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/filenameTemplate === ALT/.test(src),
     `${datei}: stellt nur um, wenn die Vorlage nie angepasst wurde`);
  ok(/titleMaxLen === 40/.test(src),
     `${datei}: hebt die Titellaenge nur beim unveraenderten Wert an`);
}

// Der Titel kommt aus den Verlagsangaben, nicht aus dem Fenstertitel.
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/\(quelle && quelle\.titel\) \|\| tab\.title/.test(src),
     `${datei}: {title} bevorzugt den Verlagstitel vor dem Fenstertitel`);
}

/* Gegenprobe an einem echten Fall: Der Fenstertitel der PubMed-Seite traegt
 * " - PubMed" mit. Bei 40 Zeichen frisst dieser Zusatz das Ende des Titels. */
{
  const kurz = (s, m) => String(s).replace(/[\\/:*?"<>|]/g, "_").trim().slice(0, m);
  const fenster = "Advances in screening and detection of gastric cancer - PubMed";
  const verlag  = "Advances in screening and detection of gastric cancer";
  ok(kurz(verlag, 60) === verlag, "Verlagstitel passt bei 60 Zeichen vollstaendig");
  ok(kurz(fenster, 40) === "Advances in screening and detection of g",
     "Gegenprobe: der Fenstertitel wird bei 40 Zeichen mitten im Wort gekappt");
  ok(!kurz(verlag, 40).endsWith("cancer"),
     "Gegenprobe: bei 40 Zeichen waere der Titel abgeschnitten worden");
}

console.log(fehler === 0 ? "\nAndroid-Dateiname: alles in Ordnung"
                         : `\nAndroid-Dateiname: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
