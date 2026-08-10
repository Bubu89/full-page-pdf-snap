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
  /* Der Zweig, der greift, wenn der Download nicht zustande kam. Frueher hiess
   * die Marke "Save A3" und oeffnete einen Reiter; seit 2.32.2 gibt es dort nur
   * noch eine Meldung. Wird hier nach der alten Marke geschnitten, ist der
   * Ausschnitt leer und jede Pruefung darauf wertlos - genau das passierte beim
   * Umbau. */
  const beginn = src.indexOf("if (id === null && p.isAndroid && !gespeichertImTab) {");
  ok(beginn > -1, `${datei}: der Rueckfall-Zweig ist auffindbar`);
  const zweig = src.slice(beginn, beginn + 1200);

  ok(!/tabs\.create\(\{\s*url\s*,/.test(zweig),
     `${datei}: oeffnet im Android-Zweig keine nackte data:-URL mehr`);
  /* Seit 2.32.2 gibt es dort auch keine Ergebnisseite mehr: Gewuenscht ist
   * Aufnahme, Download, fertig. Schlaegt das Anstossen fehl, bleibt eine
   * Meldung mit dem Grund - kein Reiter, der Betrieb vortaeuscht. */
  ok(!/zeigeErgebnisseite\(\)/.test(zweig),
     `${datei}: oeffnet auf Android auch keine Ergebnisseite mehr`);
  ok(/androidDownloadFehler/.test(zweig),
     `${datei}: meldet stattdessen den Grund`);
}

// Die Ergebnisseite muss den Namen auch dann anhaengen, wenn der
// Download-Zweig fehlt - auf Android ist er oft nicht verfuegbar.
for (const datei of ["chrome-mv3/result.js", "result.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/a\.download = String\(name \|\| "capture\.pdf"\)/.test(src),
     `${datei}: der Anker setzt das download-Attribut auf den Namen`);
  // Auf dem Rechner bleibt die Reihenfolge: erst die Download-Schnittstelle,
  // der Anker nur als Rueckfall. Auf Android greift er sofort (weiter unten).
  const laden = src.slice(src.indexOf("async function herunterladen"));
  ok(/catch \(eDownload\)[\s\S]{0,600}ankerDownload\(/.test(laden),
     `${datei}: am Rechner faengt der Anker den Fehlschlag ab`);
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


/* Die Ergebnisseite hatte denselben Mangel ein zweites Mal - an anderer Stelle.
 * Am 07.08.2026 lag "document(11).pdf" im Testordner, obwohl 2.31.18 schon
 * lief: Der Aufnahmeweg war repariert, das Antippen der Vorschau nicht. Es
 * oeffnete die blob:-URL im Reiter, und die traegt so wenig einen Dateinamen
 * wie eine data:-URL. */
for (const datei of ["chrome-mv3/result.js", "result.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const betrachter = src.slice(src.indexOf("async function oeffneImBetrachter"),
                               src.indexOf("async function herunterladen"));
  ok(/stand\.isAndroid/.test(betrachter),
     `${datei}: Vorschau-Antippen unterscheidet Android vom Rechner`);
  ok(betrachter.indexOf("ankerDownload") < betrachter.indexOf("tabs.create"),
     `${datei}: auf Android greift der benannte Weg vor dem Reiter`);

  const laden = src.slice(src.indexOf("async function herunterladen"));
  ok(laden.indexOf("stand.isAndroid") < laden.indexOf("downloads.download"),
     `${datei}: Android nimmt den Anker, ohne downloads.download zu versuchen`);

  ok(/function ankerDownload\(url, name\)/.test(src),
     `${datei}: die Ankerlogik steht an einer Stelle, nicht dreimal`);
  ok((src.match(/document\.createElement\("a"\)/g) || []).length === 1,
     `${datei}: kein doppelter Anker-Code mehr`);
}

// Der Hintergrund muss die Plattform ueberhaupt mitliefern.
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const antwort = src.slice(src.indexOf('msg.type === "pdfsnap:last"'));
  ok(/isAndroid: !!\(_platformCache && _platformCache\.isAndroid\)/.test(antwort.slice(0, 1400)),
     `${datei}: pdfsnap:last meldet die Plattform an die Ergebnisseite`);
}


/* Die beiden Schaltflaechen duerfen keinen Reiter oeffnen.
 *
 * Am 07.08.2026 auf dem Telefon beobachtet: "Herunterladen" lud nicht,
 * sondern oeffnete einen neuen Reiter, in dem man von Hand noch einmal
 * speichern musste. "Weiterleiten" fuehrte nicht zur App-Auswahl. Beides
 * hatte dieselbe Wurzel: Die Seite holt sich die Bytes per fetch() aus einer
 * data:-URL, die bei einer 6-MB-Aufnahme ueber acht Megabyte gross wird.
 * Ging das aus, waren blobUrl und datei leer - und beide Schaltflaechen
 * fielen auf "pdfsnap:open" zurueck, das nur einen Reiter oeffnet. */
for (const datei of ["chrome-mv3/result.js", "result.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const knoepfe = src.slice(src.indexOf("async function herunterladen"),
                            src.indexOf("function zeigeVorschau") > src.indexOf("async function herunterladen")
                              ? src.indexOf("function zeigeVorschau") : src.length);

  ok(/function downloadQuelle\(\)/.test(src),
     `${datei}: es gibt eine Quelle, die ohne fetch auskommt`);
  ok(/return blobUrl \|\| \(stand && stand\.url\)/.test(src),
     `${datei}: faellt auf die Adresse aus dem Hintergrund zurueck`);

  const laden = src.slice(src.indexOf("async function herunterladen"),
                          src.indexOf("async function weiterleiten"));
  ok(!/pdfsnap:open/.test(laden.replace(/\/\*[\s\S]*?\*\//g, "")),
     `${datei}: "Herunterladen" oeffnet keinen Reiter mehr`);

  const teilen = src.slice(src.indexOf("async function weiterleiten"));
  const teilenOhneKommentar = teilen.replace(/\/\*[\s\S]*?\*\//g, "");
  ok(!/pdfsnap:open/.test(teilenOhneKommentar),
     `${datei}: "Weiterleiten" oeffnet keinen Reiter mehr`);
  ok(/ankerDownload\(quelle/.test(teilenOhneKommentar),
     `${datei}: "Weiterleiten" legt die Datei ab, wenn Teilen nicht geht`);
  ok(/resultShareViaDownload/.test(teilen),
     `${datei}: und sagt, dass von dort weitergeleitet wird`);
}

// Der neue Text muss in allen neun Sprachen stehen, sonst erscheint er
// englisch - genau der Fehler, der in 2.31.17 behoben wurde.
{
  const sprachen = ["de", "en", "es", "fr", "it", "ja", "pt_BR", "ru", "zh_CN"];
  for (const s of sprachen) {
    const m = JSON.parse(readFileSync(new URL(`../_locales/${s}/messages.json`, import.meta.url), "utf8"));
    ok(!!(m.resultShareViaDownload && m.resultShareViaDownload.message),
       `_locales/${s}: resultShareViaDownload uebersetzt`);
  }
}


/* Auf Android wird jetzt heruntergeladen statt einen Reiter zu oeffnen.
 *
 * Der Weg war frueher aufgegeben worden, weil er "regelmaessig scheiterte".
 * Die Ursache war aber nicht die Plattform, sondern der Unterordner im
 * Dateinamen: Firefox fuer Android kennt ihn nicht. Ohne ihn laeuft
 * downloads.download dort. Die alte Zeitgrenze von fuenf Sekunden war
 * ausserdem zu knapp fuer eine mehrere Megabyte grosse Aufnahme. */
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");

  /* Auf Android laeuft der Download NICHT ueber die Schnittstelle der
   * Erweiterung: Die gibt es dort seit Firefox 79 nicht mehr
   * (MDN-Kompatibilitaetsdaten, version_removed 79). Am Geraet gemessen: erst
   * verstrich eine Zeitgrenze von 30 s, dann blieb downloads.onCreated stumm.
   * Stattdessen klickt das Inhaltsskript der aufgenommenen Seite einen Anker
   * mit download-Attribut - gewoehnliches Web, kein neuer Reiter. */
  ok(/speichereImTab\(tab && tab\.id, pdfBytes, filename\)/.test(src),
     `${datei}: Android legt aus der Seite heraus ab`);
  ok(!/browser\.downloads\.download[\s\S]{0,300}p\.isAndroid/.test(
       src.slice(src.indexOf("if (p.isAndroid) {"), src.indexOf("} else {"))),
     `${datei}: kein Aufruf der entfernten Schnittstelle im Android-Zweig`);
  ok(/gespeichertImTab = true/.test(src),
     `${datei}: merkt sich den Erfolg ohne Vorgangskennung`);
  const inline = src.slice(src.indexOf("async function speichereImTab"),
                           src.indexOf("async function speichereImTab") + 1500);
  ok(/cmd: "savePdf"/.test(inline) && /Array\.from\(pdfBytes\)/.test(inline),
     `${datei}: schickt die Bytes an das Inhaltsskript`);

  ok(/androidGespeichert/.test(src),
     `${datei}: meldet, dass in die Ablage gespeichert wurde`);
  ok(!/androidFertig[\s\S]{0,80}usedFilename/.test(src),
     `${datei}: nicht mehr die alte "zum Herunterladen oeffnen"-Meldung im Erfolgsfall`);

  // Die Beidateien duerfen auf Android ebenfalls keinen Unterordner tragen.
  const bei = (src.match(/\(p\.isAndroid \? filename : relPath\)/g) || []).length;
  ok(bei === 3, `${datei}: RIS, Linkkarte und Originaldatei ohne Unterordner (${bei}/3)`);

  // Der Ton muss im Ursprungsreiter spielen, nicht in einem neuen.
  ok(/fertigTon\(tab && tab\.id, settings, platform\)/.test(src),
     `${datei}: Fertig-Ton laeuft im Ursprungsreiter`);
}

// Der neue Text mit Platzhalter, in allen neun Sprachen.
{
  const sprachen = ["de", "en", "es", "fr", "it", "ja", "pt_BR", "ru", "zh_CN"];
  for (const s of sprachen) {
    const m = JSON.parse(readFileSync(new URL(`../_locales/${s}/messages.json`, import.meta.url), "utf8"));
    const e = m.androidGespeichert;
    ok(!!(e && e.message && /\$DATEI\$/.test(e.message)
          && e.placeholders && e.placeholders.datei
          && e.placeholders.datei.content === "$1"),
       `_locales/${s}: androidGespeichert mit funktionierendem Platzhalter`);
  }
}


/* Der Dateiname muss die Schnittstelle passieren.
 *
 * Seit der Titel im Namen steht, kommt darin vor, was Seiten eben im Titel
 * fuehren. Eine Aufnahme vom 07.08.2026 hiess "Online Apotheke fuer
 * Deutschland <U+25B7> Shop Apotheke_..." - mit einem Symbol aus dem
 * Pfeil-Block. Die Dokumentation von downloads.download nennt ausserdem
 * Pfadteile, die mit einem Punkt beginnen oder enden, ausdruecklich als
 * Fehlerfall. Ein Name, den die Schnittstelle ablehnt, laesst die ganze
 * Aufnahme in den Rueckfall laufen - und genau das sah wie "der Download geht
 * auf Android eben nicht" aus. */
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const fn = src.slice(src.indexOf("function sanitizeFilename"),
                       src.indexOf("function siteFromUrl"));

  ok(/u0000-\\u001F/.test(fn), `${datei}: entfernt Steuerzeichen`);
  ok(/u2190-\\u2BFF/.test(fn), `${datei}: entfernt Pfeile und Symbole`);
  ok(/1F000/.test(fn), `${datei}: entfernt Emoji`);
  ok(/replace\(\/\^\[\.\\s\]\+\//.test(fn) || /\^\[\.\\s\]\+/.test(fn),
     `${datei}: schneidet Punkte am Rand ab`);
}

/* Der Grund eines Fehlschlags muss sichtbar werden. Ohne ihn blieb ueber
 * mehrere Fassungen unklar, warum das PDF nicht in der Ablage landete. */
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/_letzterDownloadFehler = \(e1 && e1\.message\)/.test(src),
     `${datei}: haelt den Fehlergrund fest`);
  ok(/downloadFehler: _letzterDownloadFehler/.test(src),
     `${datei}: reicht ihn an die Ergebnisseite weiter`);
}
for (const datei of ["chrome-mv3/result.js", "result.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/antwort\.downloadFehler/.test(src),
     `${datei}: zeigt den Fehlergrund an, statt ihn zu verschweigen`);
}


/* Kein eigenes Fenster beim Antippen des Symbols.
 *
 * Das Hintergrundskript schaltet das Popup ab, aber erst wenn es geladen ist.
 * Nach einem Neustart des Browsers laedt es unter Umstaenden erst durch den
 * Tastendruck selbst - dann steht das Menue schon offen. Am 07.08.2026 auf dem
 * Geraet beobachtet. Das Popup nimmt sich deshalb selbst aus dem Weg. */
for (const datei of ["popup.js", "chrome-mv3/popup.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/getPlatformInfo\(\)/.test(src),
     `${datei}: fragt die Plattform ab`);
  ok(/p\.os !== "android"/.test(src),
     `${datei}: handelt nur auf Android`);
  ok(/sendMessage\(\{ cmd: "capture", region: false \}\)/.test(src),
     `${datei}: loest dort sofort die Aufnahme aus`);
  ok(/window\.close\(\)/.test(src),
     `${datei}: und schliesst sich`);
}

/* Die Meldung darf nicht behaupten, was nicht geschah.
 *
 * Bis 2.33.0 nannte sie "In Downloads gespeichert: Full Page PDF Snap/..." -
 * mit einem Unterordner, den es auf Android nicht gibt, und selbst dann, wenn
 * gar nichts ankam. Der Nutzer suchte die Datei vergebens. */
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/usedFilename = p\.isAndroid \? filename : relPath/.test(src),
     `${datei}: die Meldung nennt auf Android keinen Unterordner`);
}


/* Das Menue darf nach einem Neustart gar nicht erst aufgehen.
 *
 * Es abzuschalten, sobald das Hintergrundskript laedt, reicht nicht: In Firefox
 * laedt das erst, wenn ein Ereignis es weckt - nach einem Browser-Neustart
 * moeglicherweise erst durch den Tastendruck selbst. Dann steht das Menue schon
 * offen, auf dem Telefon als eigener Reiter. */
for (const datei of ["chrome-mv3/background.js", "background.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  ok(/runtime\.onStartup\.addListener\(popupAufAndroidAbschalten\)/.test(src),
     `${datei}: schaltet das Menue schon beim Browserstart ab`);
  ok(/runtime\.onInstalled\.addListener\(popupAufAndroidAbschalten\)/.test(src),
     `${datei}: und nach Installation oder Aktualisierung`);
  ok(/^popupAufAndroidAbschalten\(\);$/m.test(src),
     `${datei}: sowie beim Laden selbst - alle drei Wege`);
}


/* Der Anker darf nicht in den PDF-Betrachter navigieren.
 *
 * Am 07.08.2026 auf dem Telefon: In der Adresszeile stand "blob:https://…",
 * darueber eine Leiste mit einem Download-Knopf. Firefox kann PDF selbst
 * anzeigen, und dann gewinnt der eigene Betrachter gegen das
 * download-Attribut - der Klick navigiert, statt abzulegen. Ein Typ, den der
 * Browser nicht darstellen kann, laesst ihm nur das Ablegen. */
for (const datei of ["content.js", "chrome-mv3/content.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");
  const block = src.slice(src.indexOf('case "savePdf"'), src.indexOf('case "savePdf"') + 2600);

  ok(/type: "application\/octet-stream"/.test(block),
     `${datei}: der Blob traegt einen Typ, den der Browser nicht anzeigt`);
  ok(!/new Blob\(\[new Uint8Array\(msg\.bytes\)\], \{ type: "application\/pdf" \}\)/.test(block),
     `${datei}: nicht mehr application/pdf - das oeffnet den Betrachter`);
  ok(/a\.download = String\(msg\.name/.test(block),
     `${datei}: der Anker traegt den Dateinamen`);
  ok(!/a\.target/.test(block),
     `${datei}: kein target - das wuerde einen Reiter oeffnen`);

  // Und: nachsehen, ob wirklich abgelegt wurde, statt Erfolg anzunehmen.
  ok(/const vorher = location\.href/.test(block) && /location\.href !== vorher/.test(block),
     `${datei}: prueft, ob die Seite navigiert hat`);
  ok(/angezeigt statt abgelegt/.test(block),
     `${datei}: meldet den Unterschied, statt Erfolg zu behaupten`);
}

console.log(fehler === 0 ? "\nAndroid-Dateiname: alles in Ordnung"
                         : `\nAndroid-Dateiname: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
