"use strict";

const TAG = "[PDFSnap/bg]";
const log = (...a) => console.log(TAG, ...a);

let _platformCache = null;
/* Pruefsumme ueber die Bilddaten in genau der Reihenfolge, in der sie im PDF
 * stehen. Sie belegt, dass die Datei seit ihrer Erstellung unveraendert ist —
 * nicht, dass die Seite so ausgesehen hat. Diesen Unterschied nennt die
 * Fussnote im PDF ausdruecklich. */
async function bilddatenPruefsumme(pages) {
  const teile = [];
  for (const pg of pages) {
    // bytes seit 04.08.2026, jpegBytes fuer aeltere Aufrufer. Die Pruefsumme
    // deckt die eingebetteten Bilddaten ab — welcher Filter sie erzeugt hat,
    // aendert daran nichts, aber sie muss die Daten auch FINDEN. Beim Umbau
    // auf zwei Filter las diese Stelle noch das alte Feld und haette eine
    // Pruefsumme ueber nichts gebildet.
    if (pg.tiles && pg.tiles.length) {
      for (const t of pg.tiles) { const b = t.bytes || t.jpegBytes; if (b) teile.push(b); }
    } else {
      const b = pg.bytes || pg.jpegBytes; if (b) teile.push(b);
    }
  }
  let n = 0;
  for (const t of teile) n += t.length;
  const alles = new Uint8Array(n);
  let off = 0;
  for (const t of teile) { alles.set(t, off); off += t.length; }
  const digest = await crypto.subtle.digest("SHA-256", alles);
  return Array.from(new Uint8Array(digest)).map(b => b.toString(16).padStart(2, "0")).join("");
}

async function getPlatform() {
  if (_platformCache) return _platformCache;
  try {
    const info = await browser.runtime.getPlatformInfo();
    _platformCache = { os: info.os, isAndroid: info.os === "android" };
  } catch (_) {
    _platformCache = { os: "unknown", isAndroid: false };
  }
  log("Platform:", _platformCache);
  return _platformCache;
}

const DEFAULTS_DESKTOP = {
  subfolder: "Full Page PDF Snap",
  saveAs: false,
  jpegQuality: 0.92,
  // Farbtiefe der Aufnahme. Gemessen am 4. August 2026 an einer Textseite:
  //   farbe       416 kB   OCR 987 Woerter   SSIM 1,00
  //   graustufen  243 kB   OCR 989 Woerter   SSIM 1,00
  //   sw          113 kB   OCR 989 Woerter   SSIM 0,86
  // Auf einer BILDseite faellt Schwarzweiss auf SSIM 0,199 — deshalb bleibt
  // "farbe" die Voreinstellung. Wer eine Textquelle belegt, spart mit "sw"
  // rund 92 % gegenueber dem heutigen JPEG, ohne dass die Texterkennung
  // darunter leidet.
  bildModus: "farbe",
  hellerDruck: true,      // dunkle Oberflaechen umkehren, damit das Blatt weiss bleibt
  // Kurzer Ton, wenn die Aufnahme steht. Frueher nach Plattform (nur
  // Android); jetzt ueberall an, weil eine Aufnahme ohne Rueckmeldung den
  // Nutzer im Unklaren laesst, ob sie lief.
  fertigTon: true,
  settlingMs: 400,
  filenameTemplate: "{title}_{site}_{date}_{time}",
  titleMaxLen: 60,
  singlePagePdf: true,
  pageHeightPx: 2400,
  pageFormat: "a4",       // Standard: Seiten fuellen ein A4-Blatt beim Drucken
  breakAtLines: true,      // Schnitt in die naechste Luecke ziehen
  sourceMetadata: true,    // Quellenangaben aus der Seite lesen (kein Netz)
  // Die RIS-Angaben stecken IMMER als Anlage 'quelle.ris' im PDF. Die
  // zusaetzliche Datei daneben ist reine Bequemlichkeit: Zotero und Citavi
  // importieren sie per Doppelklick, eine Anlage muss erst herausgeholt
  // werden. Wer lieber eine Datei je Aufnahme behaelt, schaltet sie ab.
  risSidecar: true,
  /* Die zwei Beilagen, jede fuer sich abschaltbar.
   *
   * Beide haengen an "Quellenangaben mitschreiben": Ist das aus, entsteht
   * keine von beiden — dann liegt nur das PDF da. Ist es an, kommen beide
   * mit, solange sie hier nicht einzeln abgewaehlt sind.
   *
   * Zwei getrennte Dateien, weil sie zwei verschiedene Dinge sind: Die
   * Textdatei ist zum Lesen und Abschreiben gemacht, die RIS-Datei zum
   * Einlesen. Citavi, Zotero und EndNote koennen mit der Textdatei nichts
   * anfangen — sie erwarten ein Satzformat, keinen Fliesstext. */
  beilagenRepariert: false, // Marke der einmaligen Wiederherstellung
  zitatDatei: true,        // .zitate.txt — zum Lesen und Kopieren
  risDatei: true,          // .ris — fuer Citavi, Zotero, EndNote
  copyPath: false,         // Pfad nach dem Speichern in die Zwischenablage
  copyPathFormat: "windows", // "windows" | "wsl" | "posix"
  fetchOriginal: false,    // Verlags-PDF holen — einziger Netzzugriff, daher aus
  tilePx: 4000,
  hideSticky: true,
  // Sichtbare Herkunftszeile unter der Aufnahme. Standard aus, weil sie das
  // Bild veraendert; die Metadaten im PDF stehen ohnehin immer drin.
  provenanceFooter: false,
  // Zeitanker: holt vor dem Speichern einen oeffentlichen Zufallswert des
  // drand-Netzes und legt ihn in die Aufnahme. Belegt "nicht vor dieser Runde
  // entstanden", ohne der Geraeteuhr zu glauben. Standard AUS, weil es der
  // einzige Netzzugriff des Add-ons ist — er findet nur statt, wenn er
  // ausdruecklich verlangt wurde. Gesendet wird dabei nichts.
  timeAnchor: true,
  // Unsichtbare Textebene aus dem Dokument. Standard an: sie macht das PDF
  // durchsuchbar, ohne das Bild zu veraendern.
  textLayer: true,
  // Linkkarte neben dem PDF: Verweise mit Lage, Ziel und Rolle. Fuer einen
  // Agenten, der ein Bild der Seite hat und wissen muss, wo er hin kann.
  // Standard aus — sie erzeugt eine zweite Datei, und wer sie nicht liest,
  // hat nur eine mehr im Ordner.
  linkMap: true,
  uiLanguage: "auto",
  appLayout: "context",
  afterCapture: "show",
  // 1.0 = genau die Ansicht, die der Nutzer am Bildschirm sieht. Hoehere Werte
  // zoomen die Seite vor der Aufnahme: schaerfer, aber es passt weniger ins
  // Fenster - Menues und Seitenleisten werden dann frueher abgeschnitten.
  captureScale: 1.0,
  /* Vektor-Weg: die Seite vom Browser selbst setzen lassen statt sie zu
   * fotografieren. Nur in Chromium vorhanden und nur wirksam, wenn die
   * Erlaubnis "debugger" erteilt wurde — ohne sie bleibt es beim Bildweg,
   * ohne dass der Nutzer etwas davon merkt. */
  vektor: true,
  vektorModus: "seite",   // "seite" | "artikel"

  /* Die Einstellungen aus den Faechern neben den Knoepfen.
   *
   * Sie MUESSEN hier stehen, auch wenn sie nur im Popup gesetzt werden:
   * getSettings ruft storage.local.get(defs) auf, und diese Form liest
   * ausschliesslich die Schluessel, die in defs vorkommen. Fehlt einer, wird
   * er nie gelesen — das Popup speichert ihn, der Hintergrund sieht ihn nicht.
   *
   * Genau daran scheiterte das Querformat: Der Nutzer stellte um, die Datei
   * kam als A4 hoch heraus, und im Popup stand weiter "Querformat". Ein
   * Bedienelement, das speichert und nichts bewirkt — von aussen nicht von
   * einem kaputten Ausgabeweg zu unterscheiden. */
  /* Auch dieser stand nur in der Einstellungsseite und wurde nie gelesen —
   * gefunden von tests/einstellungen-lesbar.test.mjs beim ersten Lauf, also
   * von derselben Pruefung, die wegen des Querformats entstand. */
  reviewPromptOff: false,

  druckPapier: "a4",            // "a4" | "letter"
  druckQuer: "hoch",            // "hoch" | "quer"
  druckRandMm: 0,               // 0 = randlos; 5/10/15 mm auf Wunsch
  artikelPapier: "a4",
  artikelQuerWahl: "hoch",
  artikelSchriftgroesse: 18,
  artikelAlsText: false,
};

// Android: kein Ordner-Zeigen (downloads.show fehlt), stattdessen PDF direkt oeffnen.
// tilePx reduziert wegen RAM-Budget mobiler Geraete.
const DEFAULTS_ANDROID_OVERRIDES = {
  saveAs: false,
  // Android: bewusst gleichgesetzt zu Desktop-Default 'PageShot' - Firefox for
  // Android ab 127 legt den Unterordner unter /storage/emulated/0/Download/ an.
  // Falls nicht unterstuetzt, faellt Firefox stumm auf Root Downloads zurueck.
  subfolder: "Full Page PDF Snap",
  tilePx: 2000,
  afterCapture: "open",
  captureScale: 1.0
};

// Letzter erfolgreicher Download — wird vom Notification-Click-Handler geoeffnet.
let _lastDownloadId = null;
let _lastFilename = null;
let _lastFallbackTabId = null;  // Wenn Save via Tab-Open Notfall lief
// Blob-URL des zuletzt erzeugten PDF. Auf Android bleibt sie bis zur naechsten
// Aufnahme gueltig, damit ein Tippen auf "Fertig" das PDF im Firefox-Viewer
// zeigen kann — dort gibt es die Download-Option.
let _lastPdfUrl = null;
// Begleitdaten fuer die Ergebnisseite (result.html): sie zeigt Vorschau,
// Herunterladen und Weiterleiten und holt sich das PDF ueber _lastPdfUrl.
//
// Bewusst die URL und nicht die Rohbytes: Chrome serialisiert Nachrichten
// zwischen Erweiterungsteilen als JSON, ein Uint8Array kaeme dort als Objekt
// mit Ziffernschluesseln an. Die URL ist in Firefox eine kurze blob:-Adresse,
// in Chrome MV3 eine data:-Adresse - beide laesst sich die Seite per fetch()
// selbst in einen Blob zurueckverwandeln.
let _lastPages = 0;
let _lastSaved = false;
// Verkleinerte Gesamtansicht der Aufnahme - die Vorschau der Ergebnisseite.
let _lastPreviewUrl = null;
// Einmalige, abschaltbare Bitte um eine Bewertung. Kein Netzwerkzugriff:
// gezaehlt wird lokal, und geoeffnet wird nur, wenn der Nutzer antippt.
const BEWERTUNG_AB = 5;                    // ab der wievielten Aufnahme
const BEWERTUNG_URL = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/reviews/";
let _reviewNotifId = null;

async function getDefaults() {
  const p = await getPlatform();
  return p.isAndroid
    ? { ...DEFAULTS_DESKTOP, ...DEFAULTS_ANDROID_OVERRIDES }
    : DEFAULTS_DESKTOP;
}

const DEFAULTS = DEFAULTS_DESKTOP;

/* Vom Administrator vorgegebene Einstellungen.
 *
 * Der Weg, auf dem jemand die Erweiterung einrichtet, ohne sie zu bedienen:
 * In Firefox stehen sie in `policies.json` unter `3rdparty.Extensions`, in
 * Chrome in der Unternehmensrichtlinie. Dieselbe Datei, die die Erweiterung
 * installiert, kann sie damit auch einstellen.
 *
 * Bis 2.29.0 gab es das nicht — wer die Einstellungen setzen wollte, musste
 * die Optionsseite oeffnen und klicken. Fuer einen Agenten hiess das: die
 * Empfehlung von `recommend_settings` kennen und sie nicht anwenden koennen.
 *
 * Vorrang: vorgegeben schlaegt lokal schlaegt Voreinstellung. Das ist die
 * uebliche Reihenfolge und die einzige, die Sinn ergibt — wer eine Vorgabe
 * macht, will nicht, dass sie beim naechsten Klick verschwindet.
 */
async function getManaged() {
  try {
    if (!browser.storage.managed) return {};
    const m = await browser.storage.managed.get();
    return (m && typeof m === "object") ? m : {};
  } catch (e) {
    // Ohne hinterlegte Richtlinie wirft Firefox hier. Das ist der Normalfall
    // und kein Fehler — es gibt schlicht keine Vorgabe.
    return {};
  }
}

/* Angaben, die keinen Schalter mehr haben.
 *
 * Zitationsdatei, RIS-Satz, Linkkarte, Textebene, Zeitanker und Fertigton
 * waren einmal einzeln abschaltbar. Wer sie abgeschaltet hatte, traegt den
 * gespeicherten Wert weiter mit sich herum — und faende auf der
 * Einstellungsseite keinen Schalter mehr, mit dem er sich erklaeren koennte,
 * warum die Zitationsdatei fehlt.
 *
 * Deshalb wird der gespeicherte Wert hier nicht gelesen, sondern uebergangen.
 * Das braucht keinen Migrationsschritt, der halb durchlaufen kann, und keinen
 * Merker, der verlorengehen kann: Was keine Einstellung mehr ist, darf auch
 * aus einer alten Einstellung nicht wieder auftauchen.
 *
 * Eine Unternehmensvorgabe schlaegt das weiterhin — wer die Erweiterung fuer
 * eine Organisation einrichtet, hat Gruende, die diese Datei nicht kennt.
 */
const IMMER_AN = {
  linkMap: true,          // Verweise IM PDF
  textLayer: true,        // durchsuchbare Textebene im PDF
  timeAnchor: true,       // Zeitanker (der einzige Netzabruf)
  fertigTon: true,        // kurzer Ton, wenn die Aufnahme steht
  breakAtLines: true,     // Schnitt in die naechste Luecke ziehen
};

/* "sourceMetadata" und "hideSticky" stehen bewusst NICHT in dieser Liste.

 * Beim Zusammenstreichen waren beide hineingeraten, und beide Schalter im
 * Popup waren damit Bedienelemente ohne Wirkung. Die Liste hier ist fuer
 * Beilagen gedacht, die aus den Quellenangaben ENTSTEHEN — RIS-Satz,
 * Zitationsdatei, Linkkarte —, nicht fuer die Frage, ob die Angaben ueberhaupt
 * aus der Seite gelesen werden. Wer eine Aufnahme ohne Quellenbezug will,
 * muss das entscheiden koennen.
 *
 *
 * Beim Zusammenstreichen der Einstellungen war es zunaechst mit
 * hineingeraten — und damit war der Schalter im Popup ein Bedienelement ohne
 * Wirkung: Er liess sich umlegen, speichern, anzeigen, und die Aufnahme
 * ignorierte ihn. Die Liste hier ist fuer BELEGANGABEN gedacht, die man nicht
 * nachtraeglich erzeugen kann. Ob ein Zustimmungsdialog mit aufs Bild soll,
 * ist dagegen eine Entscheidung, die von Seite zu Seite anders ausfaellt und
 * deshalb bedienbar bleiben muss. */

/* Einmalige Wiedergutmachung fuer die verlorenen Beilagen.
 *
 * In 2.36.0 fehlten "zitatDatei" und "risDatei" in den Voreinstellungen der
 * Einstellungsseite. storage.local.get(DEFAULTS) gibt nur zurueck, was dort
 * steht — beide Haken standen deshalb leer, und beim naechsten Speichern
 * schrieb die Seite das leere Haekchen als "aus" in den Speicher. Wer die
 * Einstellungen auch nur geoeffnet hatte, bekam ab da keine Beilagen mehr,
 * ohne je etwas abgewaehlt zu haben.
 *
 * "false" laesst sich nicht ansehen, ob es von einem Nutzer stammt oder von
 * diesem Fehler. Deshalb wird es genau EINMAL zurueckgesetzt, festgehalten an
 * einer eigenen Marke. Wer die Beilagen danach abwaehlt, behaelt seine Wahl.
 */
async function beilagenEinmaligHerstellen() {
  try {
    const m = await browser.storage.local.get({ beilagenRepariert: false });
    if (m.beilagenRepariert === true) return;
    await browser.storage.local.set({
      zitatDatei: true, risDatei: true, beilagenRepariert: true,
    });
    log("Beilagen einmalig auf 'an' gesetzt (Fehler aus 2.36.0).");
  } catch (e) {
    log("Beilagen-Wiederherstellung nicht moeglich:", e && e.message);
  }
}

async function getSettings() {
  await beilagenEinmaligHerstellen();
  const defs = await getDefaults();
  const stored = await browser.storage.local.get(defs);
  const managed = await getManaged();
  const merged = { ...defs, ...stored, ...IMMER_AN, ...managed };
  // Android-Safety: 'show'/'both' funktionieren dort nicht (downloads.show fehlt).
  // Falls Settings von Desktop-Sync hierher landen, mappen wir auf 'open'.
  const p = await getPlatform();
  if (p.isAndroid && (merged.afterCapture === "show" || merged.afterCapture === "both")) {
    merged.afterCapture = "open";
  }
  return merged;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

/* Macht aus einem Seitentitel einen Dateinamen, den downloads.download annimmt.
 *
 * Die frueheren Regeln reichten nicht. Seit der Titel im Namen steht, kommt
 * darin vor, was Seiten eben so im Titel fuehren: "Online Apotheke fuer
 * Deutschland U+25B7 Shop Apotheke". Die Dokumentation der Schnittstelle nennt
 * ausdruecklich Faelle, die einen Fehler ausloesen - Pfadteile, die mit einem
 * Punkt beginnen oder enden, Rueckverweise, leere Namen. Steuerzeichen und
 * Symbole aus hoeheren Unicode-Bloecken sind auf Android-Dateisystemen
 * ebenfalls heikel.
 *
 * Ein Name, den die Schnittstelle ablehnt, laesst die ganze Aufnahme in den
 * Rueckfall laufen. Deshalb hier lieber streng als huebsch. */
function sanitizeFilename(s, maxLen) {
  let n = String(s)
    // 1. Was Dateisysteme verbieten
    .replace(/[\\/:*?"<>|]/g, "_")
    // 2. Steuerzeichen (auch U+007F) - unsichtbar, aber toedlich
    // eslint-disable-next-line no-control-regex
    .replace(/[\u0000-\u001F\u007F]/g, "")
    // 3. Symbole, Piktogramme, Emoji und die unsichtbaren Trenner darum herum.
    //    Buchstaben mit Zeichen bleiben erhalten - "fuer" mit Umlaut ist in
    //    Ordnung, "U+25B7" ist es nicht.
    .replace(/[\u2000-\u206F\u2190-\u2BFF\u2E00-\u2E7F\uFE00-\uFE0F]/g, " ")
    .replace(/[\u{1F000}-\u{1FAFF}]/gu, " ")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maxLen || 40);
  // 4. Punkte am Rand loesen laut Dokumentation einen Fehler aus
  n = n.replace(/^[.\s]+/, "").replace(/[.\s]+$/, "");
  return n || "page";
}

function siteFromUrl(url) {
  try {
    const u = new URL(url);
    const host = (u.hostname || "site").replace(/^www\./, "");
    return host.replace(/[^a-zA-Z0-9_-]/g, "_");
  } catch (_) {
    return "site";
  }
}

function nowStamp() {
  const d = new Date();
  const p = n => String(n).padStart(2, "0");
  return {
    date: `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`,
    time: `${p(d.getHours())}${p(d.getMinutes())}`,
    timeSec: `${p(d.getHours())}${p(d.getMinutes())}${p(d.getSeconds())}`
  };
}

async function nextCounter() {
  const { counter } = await browser.storage.local.get({ counter: 0 });
  const next = counter + 1;
  await browser.storage.local.set({ counter: next });
  return String(next).padStart(4, "0");
}

function dataUrlToBlob(dataUrl) {
  return fetch(dataUrl).then(r => r.blob());
}

async function blobToImage(blob) {
  const url = URL.createObjectURL(blob);
  try {
    const img = new Image();
    await new Promise((res, rej) => {
      img.onload = res;
      img.onerror = rej;
      img.src = url;
    });
    return img;
  } finally {
    setTimeout(() => URL.revokeObjectURL(url), 5000);
  }
}

function canvasToJpegBytes(canvas, quality) {
  return new Promise((resolve, reject) => {
    canvas.toBlob(async (blob) => {
      if (!blob) return reject(new Error("toBlob failed"));
      const buf = await blob.arrayBuffer();
      resolve(new Uint8Array(buf));
    }, "image/jpeg", quality);
  });
}


/* Verlustfreie Alternative zu JPEG, fuer Kacheln, auf denen sie kleiner ist.
 *
 * Gemessen am 4. August 2026 an zwei Seiten von 1400x3200 px:
 *
 *   Textseite   JPEG 0.92  1327 kB   Flate   416 kB   (31 %)
 *   Bildseite   JPEG 0.92   684 kB   Flate  3124 kB  (456 %)
 *
 * Das Verhaeltnis dreht sich mit dem Material, deshalb wird nicht umgestellt,
 * sondern je Kachel verglichen. Flate ist dabei verlustfrei (SSIM 1,0) — wo es
 * gewinnt, gewinnt es ohne Preis.
 *
 * OHNE Praediktor, obwohl PDF sie ueber /DecodeParms unterstuetzt: gemessen
 * war Flate ohne Praediktor (416 kB) kleiner als mit (529 kB) und kleiner als
 * ein PNG (495 kB). Bei Text ueberwiegen einfarbige Flaechen, und die
 * Differenzbildung bringt dort nichts, kostet aber ein Filterbyte je Zeile.
 * Das spart zugleich das Zerlegen eines PNG-Containers.
 *
 * CompressionStream gibt es in Chrome ab 80 und Firefox ab 113.
 */
/* Wendet die gewaehlte Farbtiefe an. Gibt Kanalzahl und Bittiefe mit zurueck,
 * weil das PDF beides im Bildobjekt braucht. */
/* umkehrenVorgabe: Bei gekachelter Ausgabe wird die Entscheidung EINMAL fuer
 * das ganze Bild getroffen und hier hereingereicht. Ohne das entschiede jede
 * Kachel fuer sich - und eine Seite, die oben hell und unten dunkel ist,
 * bekaeme im PDF an der Kachelgrenze einen Bruch, der nichts mit dem Aufbau
 * der Seite zu tun hat, sondern nur mit dem Zuschnitt. Gemessen am
 * 07.08.2026: obere Kachel unveraendert, untere umgekehrt, beide fuer sich
 * richtig, zusammen unbrauchbar. */
/* Unscharfmaskierung: Original + Anteil der Differenz zur weichgezeichneten
 * Fassung. Das uebliche Verfahren der Druckvorstufe.
 *
 * DIE DREI WERTE SIND NICHT FREI GEWAEHLT. Gemessen wurde mit Radius 1,2,
 * Staerke 140 % und Schwelle 2 — und die Umsetzung muss dieselben Werte
 * treffen, sonst misst die Messung etwas anderes als das, was ausgeliefert
 * wird. Ein erster Versuch nahm einen 3x3-Kasten ohne Schwelle: einfacher zu
 * schreiben, und im Ergebnis SCHLECHTER als gar nichts zu tun (79,1 % gegen
 * 80,3 % ohne Schaerfung, gegen 81,7 % mit den richtigen Werten). Ein
 * Kastenfilter zieht harte Ecken nach, die im Bild nicht sind, und ohne
 * Schwelle wird jedes Rauschen mitverstaerkt.
 *
 *   RADIUS 1,2   Gausz, getrennt nach Zeilen und Spalten gerechnet
 *   STAERKE 1,4  entspricht den gemessenen 140 %
 *   SCHWELLE 2   darunter bleibt der Punkt, wie er ist — sonst wird das
 *                Grundrauschen der Bildschirmdarstellung mitgeschaerft
 */
function kantenNachziehen(grau, breite, hoehe) {
  const SIGMA = 1.2, STAERKE = 1.4, SCHWELLE = 2;
  const r = Math.max(1, Math.ceil(SIGMA * 2));
  const kern = new Float32Array(2 * r + 1);
  let summe = 0;
  for (let i = -r; i <= r; i++) {
    const v = Math.exp(-(i * i) / (2 * SIGMA * SIGMA));
    kern[i + r] = v; summe += v;
  }
  for (let i = 0; i < kern.length; i++) kern[i] /= summe;

  const klemmen = (v, max) => (v < 0 ? 0 : v > max ? max : v);
  const waag = new Float32Array(grau.length);
  for (let y = 0; y < hoehe; y++) {
    const z = y * breite;
    for (let x = 0; x < breite; x++) {
      let s = 0;
      for (let i = -r; i <= r; i++) s += kern[i + r] * grau[z + klemmen(x + i, breite - 1)];
      waag[z + x] = s;
    }
  }
  const aus = new Uint8Array(grau.length);
  for (let y = 0; y < hoehe; y++) {
    for (let x = 0; x < breite; x++) {
      let s = 0;
      for (let i = -r; i <= r; i++) s += kern[i + r] * waag[klemmen(y + i, hoehe - 1) * breite + x];
      const i0 = y * breite + x;
      const unterschied = grau[i0] - s;
      if (Math.abs(unterschied) < SCHWELLE) { aus[i0] = grau[i0]; continue; }
      const wert = grau[i0] + STAERKE * unterschied;
      aus[i0] = wert < 0 ? 0 : wert > 255 ? 255 : Math.round(wert);
    }
  }
  return aus;
}

function farbtiefeAnwenden(d, modus, breite, umkehrenVorgabe) {
  if (modus === "graustufen" || modus === "sw") {
    const n = d.length / 4;
    const hoehe = breite ? Math.round(n / breite) : 0;
    // Luminanz nach Rec. 601 — dieselbe Gewichtung, die auch Texterkennung
    // und Druckvorstufe verwenden. Ein einfacher Mittelwert macht rote
    // Ueberschriften zu hell und blaue Links zu dunkel.
    const grau = new Uint8Array(n);
    for (let i = 0, j = 0; j < n; i += 4, j++) {
      grau[j] = (d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114) | 0;
    }
    /* Vor der Schwelle die Kanten nachziehen — nur bei Schwarzweiss.
     *
     * Bildschirmschrift ist kantengeglaettet: Zwischen Schwarz und Weiss
     * liegen graue Zwischenstufen, und genau die entscheidet die Schwelle
     * willkuerlich in die eine oder andere Richtung. Duenne Striche fallen
     * dabei auseinander. Eine Unscharfmaskierung zieht die Zwischenstufen zu
     * den Enden hin, bevor geschwellt wird.
     *
     * Gemessen am 18.08.2026 an 6 Seiten in je 2 Aufloesungen, 50 Laeufe:
     *
     *   wie bisher        79,4 %      geglaettet     78,6 %  (-0,9)
     *   GESCHAERFT        80,5 %      ortsabhaengig  79,0 %  (-0,4)
     *                                 2x vergroessert 79,1 % (-0,4)
     *
     * Schaerfen war der einzige Weg, der ueberhaupt half, und in keinem
     * einzigen Fall schadete er um mehr als 0,1 Punkte. Glaetten — die
     * naheliegende Vermutung — machte es durchweg schlechter: Es zieht die
     * Zwischenstufen in die Mitte, also genau dorthin, wo die Schwelle
     * raten muss.
     *
     * Fuer Graustufen ausdruecklich NICHT: Dort gibt es keine Schwelle, die
     * Zwischenstufen bleiben erhalten, und Schaerfen waere eine Veraenderung
     * des Bildes ohne Gegenwert. */
    if (modus === "sw" && breite > 2 && hoehe > 2) {
      grau.set(kantenNachziehen(grau, breite, hoehe));
    }
    if (modus === "graustufen") {
      // Dieselbe Entscheidung wie bei Schwarzweiss, nur ohne Schwelle: Die
      // Grauwerte werden gespiegelt, aus dunkel wird hell. Die Abstufungen
      // bleiben erhalten, nur die Richtung dreht sich.
      if (umkehrenVorgabe === true) {
        for (let i = 0; i < n; i++) grau[i] = 255 - grau[i];
      }
      return { daten: grau, kanaele: 1, bits: 8, umgekehrt: umkehrenVorgabe === true };
    }
    // 1 bit, acht Punkte je Byte. Feste Schwelle statt Dithering: Dithering
    // sieht besser aus und komprimiert schlechter, und fuer Text zaehlt hier
    // die Kante, nicht der Halbton.
    //
    // JEDE ZEILE BEGINNT AN EINER BYTE-GRENZE. Das schreibt PDF so vor
    // (ISO 32000-1, 7.4.4: "Each row of the image shall begin on a byte
    // boundary"), und es ist keine Formalie. Eine erste Fassung packte alle
    // Punkte fortlaufend durch. Bei einer Breite, die durch 8 teilbar ist,
    // faellt das nicht auf — bei 1440 Punkten ging alles gut. Bei 1617
    // Punkten rutscht jede Zeile um sieben Bit, nach hundert Zeilen sind es
    // 87 Punkte, und das Bild zerfaellt in Diagonalen. Gemessen am
    // 4. August 2026 an einer Aufnahme aus Firefox unter Windows.
    // Der Hintergrund ist bei Schwarzweiss immer weiss.
    //
    // Wer Schwarzweiss waehlt, will drucken. Eine vollflaechig schwarze Seite
    // kostet Toner und ist schlecht zu lesen. Also wird umgekehrt, sobald das
    // Ergebnis ueberwiegend schwarz waere.
    //
    // Entschieden wird am ERGEBNIS, nicht an der Vorlage. Die mittlere
    // Helligkeit der Vorlage waere das naheliegende Mass, geht aber daneben:
    // Eine Seite mit hellem Kopf und dunklem Inhaltsbereich kommt im Mittel
    // ueber 128 und wird trotzdem grossflaechig schwarz gedruckt. Gezaehlt
    // wird deshalb, wie viele Punkte nach der Schwelle schwarz waeren - liegt
    // das ueber der Haelfte, ist Schwarz offensichtlich der Hintergrund.
    //
    // Gemessen an einer Textprobe im Dunkelmodus (Hintergrund 30, Schrift 235):
    // 93,9 % schwarz ohne Umkehr, 6,1 % mit. Helle Seiten bleiben unangetastet.
    //
    // Nur fuer Schwarzweiss. Graustufen geben die Seite wieder, wie sie war -
    // wer sie waehlt, will das Aussehen behalten.
    // Zwei Merkmale muessen zusammenkommen, sonst wird nicht umgekehrt.
    //
    // Der erste Versuch zaehlte einfach, wie viele Punkte dunkel sind. Das
    // kippt, sobald ein grosses Bild oder ein Diagramm auf einer hellen Seite
    // liegt: An zwoelf nachgestellten Faellen traf die Regel nur sieben Mal.
    //
    //   Randmittel  - der Streifen am Blattrand ist fast immer Hintergrund;
    //                 Bilder und Diagramme liegen in der Mitte.
    //   Modus       - der haeufigste Grauwert der ganzen Flaeche, grob
    //                 gerastert. Das ist die Farbe, die den meisten Platz
    //                 einnimmt.
    //
    // Umgekehrt wird nur, wenn BEIDE dunkel sind. Der Rand allein irrt bei
    // hellen Seiten mit dunkler Kopf- und Fusszeile, der Modus allein bei
    // grossen Bildern. Zusammen trafen sie 12 von 14 Faellen; die beiden
    // uebrigen sind dunkle Seiten, auf denen ein sehr grosses helles Bild
    // liegt - dort bleibt es beim Original. Das ist der harmlosere Irrtum:
    // Es wird nichts verfaelscht, und weniger als die Haelfte des Blattes
    // ist schwarz.
    const randTiefe = Math.max(4, Math.round(Math.min(breite, hoehe) * 0.03));
    let randSumme = 0, randAnzahl = 0;
    for (let y = 0; y < hoehe; y++) {
      const obenUnten = y < randTiefe || y >= hoehe - randTiefe;
      const zeile = y * breite;
      for (let x = 0; x < breite; x++) {
        if (obenUnten || x < randTiefe || x >= breite - randTiefe) {
          randSumme += grau[zeile + x]; randAnzahl++;
        }
      }
    }
    const randMittel = randAnzahl ? randSumme / randAnzahl : 255;

    // Histogramm in 32 Stufen - Flaechen auf dem Bildschirm sind selten exakt
    // derselbe Wert, feiner zu rastern verteilt sie auf Nachbarstufen.
    const eimer = new Uint32Array(32);
    for (let i = 0; i < n; i++) eimer[grau[i] >> 3]++;
    let groesster = 0;
    for (let i = 1; i < 32; i++) if (eimer[i] > eimer[groesster]) groesster = i;
    // NICHT 'modus' nennen - so heisst der Parameter dieser Funktion.
    // Ein const gleichen Namens verschattet ihn und wirft beim Zugriff
    // weiter oben eine ReferenceError: die Umwandlung waere komplett
    // gebrochen. Vom Test am 07.08.2026 sofort gefunden.
    const haeufigsterWert = groesster * 8 + 4;

    const umkehren = typeof umkehrenVorgabe === "boolean"
      ? umkehrenVorgabe
      : (n > 0 && randMittel < 128 && haeufigsterWert < 128);

    /* Die Trennschwelle wird aus dem Bild bestimmt, nicht festgesetzt.
     *
     * Bildschirmschrift ist kantengeglaettet: Zwischen Buchstabe und
     * Hintergrund liegen Grautoene, im gemessenen Beispiel 2,4 % aller Punkte.
     * Eine feste Schwelle bei 128 laesst davon mehr als die Haelfte auf die
     * helle Seite fallen - die Buchstaben werden duenn und brechen auf,
     * besonders die Innenraeume von e, a und o.
     *
     * Schlimmer bei kontrastarmen Seiten: Grau auf Hellgrau liegt komplett
     * ueber 128. Dort erfasst die feste Schwelle NICHTS, das Blatt bleibt leer.
     *
     * Otsus Verfahren (1979) sucht die Schwelle, die Vorder- und Hintergrund
     * am staerksten trennt. Gemessen: 166 bei schwarz auf weiss, 188 bei grau
     * auf hellgrau, 103 bei hellem Text auf dunklem Grund. Bei 11px-Schrift
     * stieg die Zahl geschlossener Buchstaben-Innenraeume von 11 auf 15.
     *
     * Berechnet wird auf den Werten NACH der Umkehr - sonst passt die
     * Schwelle zur falschen Seite.
     */
    const hist = new Uint32Array(256);
    for (let i = 0; i < n; i++) hist[umkehren ? 255 - grau[i] : grau[i]]++;
    let summeAlle = 0;
    for (let t = 0; t < 256; t++) summeAlle += t * hist[t];
    let summeB = 0, gewichtB = 0, besteVarianz = -1, schwelle = 128;
    for (let t = 0; t < 256; t++) {
      gewichtB += hist[t];
      if (gewichtB === 0) continue;
      const gewichtF = n - gewichtB;
      if (gewichtF === 0) break;
      summeB += t * hist[t];
      const mittelB = summeB / gewichtB;
      const mittelF = (summeAlle - summeB) / gewichtF;
      const varianz = gewichtB * gewichtF * (mittelB - mittelF) * (mittelB - mittelF);
      if (varianz > besteVarianz) { besteVarianz = varianz; schwelle = t; }
    }

    const bytesJeZeile = Math.ceil(breite / 8);
    const bin = new Uint8Array(bytesJeZeile * hoehe);
    for (let y = 0; y < hoehe; y++) {
      const zeilenAnfang = y * bytesJeZeile;
      const quellAnfang = y * breite;
      for (let x = 0; x < breite; x++) {
        const wert = umkehren ? 255 - grau[quellAnfang + x] : grau[quellAnfang + x];
        // Vergleich gegen die aus dem Bild bestimmte Schwelle, nicht gegen 128.
        // Gesetztes Bit heisst WEISS.
        //
        // Bei /DeviceGray mit einem Bit steht 0 fuer den kleinsten Grauwert -
        // schwarz - und 1 fuer den groessten - weiss (ISO 32000-1, 8.9.5.2;
        // ohne /Decode-Array gilt der Vorgabebereich [0 1]). Die erste Fassung
        // setzte das Bit fuer DUNKLE Punkte: Damit wurde die Schrift weiss und
        // der Hintergrund schwarz, das ganze Bild also verkehrt.
        //
        // Aufgefallen ist es nie, weil es sich bei dunklen Oberflaechen
        // zufaellig aufhob: Dort ist der Hintergrund dunkel, wurde also weiss -
        // was richtig aussah. Auf einer gewoehnlichen hellen Seite kam dagegen
        // ein schwarzes Blatt mit weisser Schrift heraus. Gemessen am
        // 07.08.2026 an einer Aufnahme: 99 % schwarze Punkte.
        // Otsus Schwelle ist die OBERE Grenze der dunklen Klasse: Werte bis
        // einschliesslich t gehoeren dorthin. Deshalb ">" und nicht ">=" -
        // sonst faellt bei einer Schwelle von 0 auch der schwarze Punkt auf
        // die helle Seite und das Blatt bleibt leer.
        if (wert > schwelle) {
          bin[zeilenAnfang + (x >> 3)] |= 0x80 >> (x & 7);
        }
      }
    }
    return { daten: bin, kanaele: 1, bits: 1, umgekehrt: umkehren };
  }
  const rgb = new Uint8Array((d.length / 4) * 3);
  for (let i = 0, j = 0; i < d.length; i += 4, j += 3) {
    rgb[j] = d[i]; rgb[j + 1] = d[i + 1]; rgb[j + 2] = d[i + 2];
  }
  return { daten: rgb, kanaele: 3, bits: 8 };
}

async function canvasToFlateBytes(canvas, modus, umkehrenVorgabe) {
  if (typeof CompressionStream === "undefined") return null;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  const d = ctx.getImageData(0, 0, canvas.width, canvas.height).data;
  // RGBA -> gewaehlte Farbtiefe. PDF kennt keinen Alphakanal, und die Aufnahme
  // hat keinen: der Hintergrund wurde vor dem Zeichnen gefuellt.
  const { daten, kanaele, bits } = farbtiefeAnwenden(d, modus, canvas.width, umkehrenVorgabe);
  const strom = new Blob([daten]).stream().pipeThrough(new CompressionStream("deflate"));
  const buf = await new Response(strom).arrayBuffer();
  return { bytes: new Uint8Array(buf), kanaele, bits };
}

/* Erzeugt beide Fassungen und gibt die kleinere zurueck.
 *
 * Kostet Rechenzeit und keine Qualitaet. Faellt Flate aus — alter Browser,
 * Speichergrenze, was auch immer —, bleibt es beim bisherigen Verhalten;
 * ein Fehler in der Sparfassung darf die Aufnahme nicht kosten.
 */
/* Einmal fuer das ganze Bild entscheiden, ob umgekehrt wird.
 *
 * Wird vor der Kachelung aufgerufen und an jede Kachel weitergereicht. Liest
 * das Bild in Schritten statt Punkt fuer Punkt: Bei einer langen Aufnahme
 * sind das Millionen Werte, und fuer Randhelligkeit und haeufigsten Grauwert
 * genuegt eine Stichprobe. Der Rand wird vollstaendig gelesen - er ist
 * schmal, und genau dort steht die Antwort.
 */
function sollUmkehren(canvas, modus, erlaubt) {
  // Gilt fuer Graustufen UND Schwarzweiss - beide werden gedruckt, und ein
  // schwarzes Blatt kostet in beiden Faellen Toner. Farbaufnahmen bleiben
  // unberuehrt: Dort waere eine Umkehr eine Verfaelschung, keine Aufbereitung.
  if (modus !== "sw" && modus !== "graustufen") return undefined;
  if (erlaubt === false) return false;       // Schalter in den Einstellungen
  try {
    const ctx = canvas.getContext("2d", { willReadFrequently: true });
    const b = canvas.width, h = canvas.height;
    const d = ctx.getImageData(0, 0, b, h).data;
    const grau = (i) => (d[i] * 0.299 + d[i + 1] * 0.587 + d[i + 2] * 0.114) | 0;

    const randTiefe = Math.max(4, Math.round(Math.min(b, h) * 0.03));
    let randSumme = 0, randAnzahl = 0;
    for (let y = 0; y < h; y++) {
      const obenUnten = y < randTiefe || y >= h - randTiefe;
      for (let x = 0; x < b; x++) {
        if (obenUnten || x < randTiefe || x >= b - randTiefe) {
          randSumme += grau((y * b + x) * 4); randAnzahl++;
        }
      }
    }
    const randMittel = randAnzahl ? randSumme / randAnzahl : 255;

    const eimer = new Uint32Array(32);
    const schritt = Math.max(1, Math.floor((b * h) / 400000));   // hoechstens 400k Proben
    for (let i = 0; i < b * h; i += schritt) eimer[grau(i * 4) >> 3]++;
    let groesster = 0;
    for (let i = 1; i < 32; i++) if (eimer[i] > eimer[groesster]) groesster = i;

    const entscheidung = randMittel < 128 && (groesster * 8 + 4) < 128;
    log("Schwarzweiss: Rand", Math.round(randMittel), "| haeufigster",
        groesster * 8 + 4, "->", entscheidung ? "umkehren" : "lassen");
    return entscheidung;
  } catch (e) {
    log("Umkehr-Entscheidung nicht moeglich:", e && e.message);
    return undefined;      // dann entscheidet jede Kachel wie bisher
  }
}

/* Die Farbe, die hinter dem Bild durchscheinen soll.
 *
 * Bleibt auf einem Blatt unter dem Bild Platz — weil der Schnitt in die
 * Zeilenluecke gezogen wurde oder weil das Dokument endet —, dann leuchtete
 * dort bisher das blanke Blatt durch. Auf einer dunklen Seite ist das ein
 * weisser Balken quer ueber die untere Kante.
 *
 * Genommen wird der haeufigste Farbwert der untersten drei Bildzeilen: Was
 * dort die Flaeche beherrscht, ist der Seitenhintergrund. Ein Mittelwert waere
 * falsch — er mischt Schrift und Grund zu einem Grau, das auf der Seite
 * nirgends vorkommt.
 *
 * Die Farbe durchlaeuft dieselbe Umwandlung wie das Bild. Bei Schwarzweiss ist
 * das Ergebnis immer Weiss: Der Hintergrund stellt die Mehrheit der Flaeche,
 * die Schwelle legt ihn also auf die helle Seite, und bei dunklen Seiten kehrt
 * die Aufnahme ohnehin um. */
function seitenHintergrund(canvas, modus, umkehren) {
  try {
    const h = canvas.height, w = canvas.width;
    if (!h || !w) return null;
    if (modus === "sw") return [255, 255, 255];
    const zeilen = Math.min(3, h);
    const d = canvas.getContext("2d").getImageData(0, h - zeilen, w, zeilen).data;
    const zaehler = new Map();
    for (let i = 0; i < d.length; i += 4) {
      // Grob gerastert auf 5 Bit je Kanal — sonst zaehlt jede Nuance einzeln
      // und der Kantenglaettungssaum gewinnt gegen die Flaeche.
      const k = ((d[i] >> 3) << 10) | ((d[i + 1] >> 3) << 5) | (d[i + 2] >> 3);
      zaehler.set(k, (zaehler.get(k) || 0) + 1);
    }
    let best = 0, bestN = -1;
    for (const [k, n] of zaehler) if (n > bestN) { bestN = n; best = k; }
    const r = ((best >> 10) & 31) << 3, g = ((best >> 5) & 31) << 3, b = (best & 31) << 3;
    if (modus === "graustufen") {
      let y = Math.round(r * 0.299 + g * 0.587 + b * 0.114);
      if (umkehren === true) y = 255 - y;
      return [y, y, y];
    }
    return [r, g, b];
  } catch (_) {
    // Ohne Farbe bleibt alles wie bisher — ein geratener Ton waere schlimmer
    // als der weisse Rest.
    return null;
  }
}

async function canvasToBildBytes(canvas, quality, modus, umkehrenVorgabe) {
  const m = modus || "farbe";
  let flate = null;
  try {
    flate = await canvasToFlateBytes(canvas, m, umkehrenVorgabe);
  } catch (e) {
    log("Flate uebersprungen:", e && e.message);
  }
  // Bei Graustufen und Schwarzweiss gibt es nichts zu vergleichen: JPEG kann
  // die Farbtiefe nicht halten, und wer sie gewaehlt hat, will sie auch.
  if (m !== "farbe") {
    if (flate) return { bytes: flate.bytes, filter: "FlateDecode",
                        kanaele: flate.kanaele, bits: flate.bits };
    log("Farbtiefe", m, "nicht moeglich — zurueck auf JPEG");
  }
  /* Im Rueckfall fuer Schwarzweiss und Graustufen ohne Sparen kodieren.
   *
   * Sonst greift hier die eingestellte JPEG-Guete — ein Wert, der fuer
   * FARBBILDER richtig gewaehlt ist. Bei Schrift zerstoert er genau das, was
   * bei diesen beiden Betriebsarten allein zaehlt: die Kante. Wer
   * Schwarzweiss waehlt, will drucken oder durchsuchbaren Text, und beides
   * lebt von scharfen Kanten, nicht von kleinen Dateien.
   *
   * Auf dem normalen Weg spielt das keine Rolle: Dort gehen beide Betriebs-
   * arten verlustfrei ueber Flate und sehen nie einen JPEG-Kodierer. Diese
   * Zeile greift nur, wenn Flate ausfaellt. */
  const guete = (m === "farbe") ? quality : 1.0;
  const jpeg = await canvasToJpegBytes(canvas, guete);
  if (flate && m === "farbe" && flate.bytes.length < jpeg.length) {
    return { bytes: flate.bytes, filter: "FlateDecode",
             kanaele: flate.kanaele, bits: flate.bits };
  }
  return { bytes: jpeg, filter: "DCTDecode", kanaele: 3, bits: 8 };
}

/* Pfad der gespeicherten Datei in die Zwischenablage.
 *
 * Gedacht fuer den Weg vom Browser in ein Terminal oder an ein Sprachmodell:
 * Aufnehmen, Strg+V, fertig — statt den Pfad aus dem Download-Verzeichnis
 * abzutippen.
 *
 * Drei Formen, weil derselbe Pfad je nach Ziel anders aussehen muss:
 *   windows  C:\Users\Name\Downloads\seite.pdf
 *   wsl      /mnt/c/Users/Name/Downloads/seite.pdf   (Linux unter Windows)
 *   posix    /home/name/Downloads/seite.pdf          (macOS, Linux)
 * Ein Windows-Pfad in einem WSL-Terminal fuehrt ins Leere; die Umrechnung
 * hier zu machen erspart sie jedes Mal von Hand.
 *
 * Der Service Worker in Chrome hat keine Zwischenablage — dort wird das
 * Schreiben an den aktiven Tab abgegeben. Scheitert beides, bleibt es beim
 * gespeicherten PDF: die Zwischenablage ist Zugabe, kein Teil der Aufnahme.
 */
function pfadFormatieren(pfad, form) {
  if (!pfad) return "";
  if (form === "wsl") {
    const m = pfad.match(/^([A-Za-z]):[\\/](.*)$/);
    if (m) return "/mnt/" + m[1].toLowerCase() + "/" + m[2].replace(/\\/g, "/");
    return pfad.replace(/\\/g, "/");
  }
  if (form === "posix") return pfad.replace(/\\/g, "/");
  return pfad;
}

async function pfadInZwischenablage(pfad, form, tabId) {
  const text = pfadFormatieren(pfad, form);
  if (!text) return false;
  // Firefox: der Hintergrund hat ein Dokument und darf selbst schreiben.
  try {
    if (typeof navigator !== "undefined" && navigator.clipboard && navigator.clipboard.writeText) {
      await navigator.clipboard.writeText(text);
      log("Pfad in die Zwischenablage:", text);
      return true;
    }
  } catch (e) {
    log("Zwischenablage im Hintergrund nicht moeglich:", e && e.message);
  }
  // Chrome: ueber den Tab, in dem die Aufnahme lief.
  try {
    if (tabId != null) {
      await browser.scripting.executeScript({
        target: { tabId },
        func: (t) => {
          const f = document.createElement("textarea");
          f.value = t;
          f.style.cssText = "position:fixed;top:-9999px;opacity:0";
          document.body.appendChild(f);
          f.select();
          try { document.execCommand("copy"); } finally { f.remove(); }
        },
        args: [text],
      });
      log("Pfad ueber den Tab in die Zwischenablage:", text);
      return true;
    }
  } catch (e) {
    log("Zwischenablage ueber den Tab nicht moeglich:", e && e.message);
  }
  return false;
}

async function ensureContentInjected(tabId) {
  for (let attempt = 0; attempt < 3; attempt++) {
    try {
      const r = await browser.tabs.sendMessage(tabId, { cmd: "ping" });
      if (r && r.ok) { log("Content already there."); return; }
    } catch (_) { /* not yet injected */ }
    try {
      await browser.scripting.executeScript({ target: { tabId }, files: ["content.js"] });
      log("Content injected (attempt " + (attempt + 1) + ").");
    } catch (e) {
      log("executeScript failed:", e);
      throw new Error(txt("noScripts",
        "Diese Seite erlaubt keine Erweiterungs-Skripte."));
    }
    await sleep(120);
  }
  const r = await browser.tabs.sendMessage(tabId, { cmd: "ping" });
  if (!r || !r.ok) throw new Error("Content-Script antwortet nicht.");
}

/* Welche Sprache gilt fuer die Beleg-Datei?
 *
 * "auto" heisst: die Sprache des Browsers. Die Erweiterung kennt daneben eine
 * eigene Wahl, und die muss gewinnen — wer die Oberflaeche auf Spanisch
 * gestellt hat, will keine deutschen Abschnittstitel in der Datei, auch wenn
 * der Browser deutsch laeuft. */
function belegSprache(settings) {
  const wahl = (settings && settings.uiLanguage) || "auto";
  if (wahl && wahl !== "auto") return wahl;
  try {
    const b = browser.i18n.getUILanguage && browser.i18n.getUILanguage();
    if (b) return String(b).replace("-", "_");
  } catch (_) { /* Rueckfall */ }
  return "en";
}

/* Die Blattmasse fuer den Druck, in Zoll.
 *
 * A4 misst 210 x 297 mm, das sind 8,27 x 11,69 Zoll. Letter misst 8,5 x 11.
 * Quer gelegt tauschen die beiden Werte die Rollen — mehr ist daran nicht.
 * In Zoll, weil die Druckschnittstelle in Zoll rechnet; jede Umrechnung
 * mehr waere eine Stelle mehr, an der ein Faktor verrutschen kann. */
function druckMasse(settings) {
  const quer = (settings.druckQuer || "hoch") === "quer";
  const letter = (settings.druckPapier || "a4") === "letter";
  const kurz = letter ? 8.5 : 8.27;
  const lang = letter ? 11 : 11.69;
  return quer
    ? { breiteZoll: lang, hoeheZoll: kurz }
    : { breiteZoll: kurz, hoeheZoll: lang };
}

/* Wie breit ist das Blatt, auf dem der Artikel umbrechen soll?
 *
 * In CSS-Pixeln, weil das Dokument darin rechnet: 96 davon ergeben ein Zoll.
 * A4 ist 210 mm breit, das sind 8,27 Zoll und damit 794 px; quer gelegt 297 mm
 * = 1123 px. Letter misst 8,5 x 11 Zoll, also 816 bzw. 1056 px.
 *
 * Die Breite muss VOR dem Messen der Hoehe stehen — die Hoehe ergibt sich erst
 * daraus, wie der Text auf dieser Breite umbricht. */
function blattBreite(settings) {
  const quer = (settings.artikelQuerWahl || "hoch") === "quer";
  const letter = (settings.artikelPapier || "a4") === "letter";
  if (letter) return quer ? 1056 : 816;
  return quer ? 1123 : 794;
}

/* Den Dateinamen aus der Vorlage bauen.
 *
 * Herausgeloest, weil ihn seit dem Vektor-Weg zwei Aufrufer brauchen. Zwei
 * Abschriften derselben Regel waeren zwei Orte, an denen die Vorlage
 * kuenftig auseinanderlaufen kann. */
async function dateinamenBauen(tab, settings, quelle) {
  /* Denselben Titel nehmen wie fuer die Dokumenteigenschaften: den aus den
   * Verlagsangaben der Seite, wenn es ihn gibt. Der Fenstertitel traegt fast
   * immer Zusaetze mit — "… - PubMed", "… | Zeitschrift" —, die im
   * Dateinamen nur Platz kosten und bei der Laengengrenze den eigentlichen
   * Titel abschneiden. */
  const baseTitle = sanitizeFilename(
    (quelle && quelle.titel) || tab.title || "page", settings.titleMaxLen);
  const stamp = nowStamp();
  const n = await nextCounter();
  const filename = (settings.filenameTemplate || "{title}_{site}_{date}_{time}")
    .replace("{title}", baseTitle)
    .replace("{site}", siteFromUrl(tab.url))
    .replace("{date}", stamp.date)
    .replace("{time}", stamp.time)
    .replace("{timesec}", stamp.timeSec)
    .replace("{n}", n) + ".pdf";
  const subfolder = (settings.subfolder || "").replace(/^\/+|\/+$/g, "");
  return { filename, relPath: subfolder ? `${subfolder}/${filename}` : filename };
}

/* Eine Datei neben das PDF legen.
 *
 * Fehlschlaege werden protokolliert, aber nicht weitergereicht: Eine Beilage,
 * die nicht zustande kommt, ist kein Grund, eine gelungene Aufnahme scheitern
 * zu lassen. Die Angaben stecken ohnehin auch im PDF. */
/* Die Adresse, unter der die Download-Schnittstelle den Inhalt abholt.
 *
 * Firefox verweigert data:-Adressen in downloads.download rundheraus:
 *
 *     Error processing url: Error: Access denied for URL data:text/plain;...
 *
 * Gemessen am 18.08.2026 an Firefox ESR 153 mit einer eigens dafuer gebauten
 * Erweiterung. Geprueft wurden vier Faelle; data: scheiterte in allen, blob:
 * gelang in allen — auch mit Unterordner und auch als dritter Download
 * hintereinander. Genau daran lag es, dass die Zitationsdatei jahrelang nicht
 * neben dem PDF ankam: Sie fiel auf den Weg ueber die Seite zurueck, und der
 * kann keinen Ordner setzen (siehe unten). Das PDF selbst kam an, weil es
 * schon immer ueber eine blob-Adresse ging.
 *
 * Im Service Worker von Chrome gibt es URL.createObjectURL nicht. Dort bleibt
 * es bei data: — was dort auch nie ein Problem war. */
function beilagenAdresse(mime, inhalt) {
  try {
    if (typeof URL !== "undefined" && typeof URL.createObjectURL === "function"
        && typeof Blob !== "undefined") {
      return { url: URL.createObjectURL(new Blob([inhalt], { type: mime })), blob: true };
    }
  } catch (_) { /* faellt auf data: zurueck */ }
  return { url: "data:" + mime + ";charset=utf-8," + encodeURIComponent(inhalt), blob: false };
}

async function beilageAblegen(name, mime, inhalt, tabId) {
  const { url, blob } = beilagenAdresse(mime, inhalt);
  /* Erst freigeben, wenn der Browser gelesen hat — sonst bricht der Download
   * ab. Dieselbe Wartezeit wie beim PDF. */
  const freigeben = () => { if (blob) setTimeout(() => { try { URL.revokeObjectURL(url); } catch (_) { /* egal */ } }, 30000); };

  /* Erster Weg: die Download-Schnittstelle. */
  try {
    await browser.downloads.download({ url, filename: name, conflictAction: "uniquify" });
    log("Beilage gespeichert:", name);
    freigeben();
    return { ok: true, weg: "downloads" };
  } catch (e) {
    freigeben();
    log("Beilage ueber downloads gescheitert:", name, e && e.message);

    /* Zweiter Weg: die Seite legt sie ab.
     *
     * Auf Android ist das seit langem der einzige gangbare Weg — die
     * Download-Schnittstelle gibt es dort nicht. Am Rechner greift er, wenn
     * der Browser eine zweite Datei ablehnt: Manche lassen einer Erweiterung
     * nur eine Ablage ohne Rueckfrage durchgehen, und dann kam die Beilage
     * nie an, ohne dass es irgendwo aufgefallen waere.
     *
     * Ein Anker mit download-Attribut zaehlt als Handlung der Seite, nicht
     * der Erweiterung.
     *
     * ACHTUNG, DIESER WEG VERLIERT DEN ORDNER. Das download-Attribut nimmt
     * nur einen Dateinamen; Pfadanteile verwerfen alle Browser (HTML-Norm,
     * 4.6.6: "the user agent should not use path components"). Die Datei
     * landet also im Wurzelverzeichnis der Ablage, nicht beim PDF — genau
     * das Bild, das eine Zitationsdatei in D:\Downloads statt in
     * D:\Downloads\Full Page PDF Snap ergab. Seit die Adresse ueber blob
     * laeuft, ist dieser Weg der seltene Ausnahmefall; er bleibt als
     * Rueckfall, weil eine Datei am falschen Platz besser ist als keine. */
    if (tabId != null) {
      try {
        const r = await browser.tabs.sendMessage(tabId, {
          cmd: "dateiAblegen",
          name: String(name).split("/").pop(),
          inhalt, mime,
        });
        if (r && r.ok) {
          log("Beilage ueber die Seite abgelegt:", name);
          return { ok: true, weg: "seite" };
        }
        return { ok: false, grund: (r && r.grund) || "die Seite konnte nicht ablegen" };
      } catch (e2) {
        return { ok: false, grund: (e2 && e2.message) || (e && e.message) || "unbekannt" };
      }
    }
    return { ok: false, grund: (e && e.message) || "unbekannt" };
  }
}

/* RIS-Satz, Zitationsdatei und Linkkarte neben das PDF.
 *
 * Im PDF steckt der RIS-Satz bereits als Anhang, aber dort findet ihn
 * niemand: Es braucht die Anlagen-Ansicht des Betrachters oder ein Werkzeug
 * auf der Kommandozeile. Eine Datei daneben laesst sich per Doppelklick in
 * Citavi oder Zotero ziehen.
 *
 * Die Zitationsdatei ist die Antwort auf den haeufigsten Handgriff nach einer
 * Aufnahme: eine Zeile ins Literaturverzeichnis kopieren. Dafuer musste man
 * bisher den RIS-Satz durch ein Literaturprogramm schicken. */
async function belegeAblegen(stamm, quelle, linkKarte, zusatz) {
  const z = zusatz || {};
  const abgelegt = [];
  const gescheitert = [];

  /* Jede Beilage steht fuer sich.
   *
   * Bis 2.35.8 hing die Zitationsdatei im Fangnetz des RIS-Satzes: Scheiterte
   * der, entstand auch sie nicht — obwohl beide nichts miteinander zu tun
   * haben. Und beide hingen an derselben Einstellung, sodass wer die
   * RIS-Datei abwaehlte, auch die Zitationsdatei verlor.
   *
   * Deshalb hier drei getrennte Schritte mit je eigenem Ergebnis. Was
   * scheitert, wird benannt und reisst die anderen nicht mit. */
  async function legen(endung, mime, inhalt) {
    const r = await beilageAblegen(stamm + endung, mime, inhalt, z.tabId);
    if (r.ok) abgelegt.push(endung + (r.weg === "seite" ? " (über die Seite)" : ""));
    else gescheitert.push(endung + ": " + (r.grund || "unbekannt"));
    return r.ok;
  }

  if (quelle && quelle.titel) {
    /* Der MIME-Typ muss zur Endung passen, sonst benennt Chrome die Datei
     * um: mit "text/plain" wurde aus ".ris" beim Speichern ".txt" — gemessen
     * am 10.08.2026. Zotero und Citavi erkennen ".ris" von selbst, ".txt"
     * nicht; der Import verlangte dann Umbenennen von Hand. */
    if (z.risDatei !== false && typeof PageShotPdf !== "undefined" && PageShotPdf.risSatz) {
      try {
        await legen(".ris", "application/x-research-info-systems", PageShotPdf.risSatz(quelle));
      } catch (e) {
        log("RIS-Satz nicht erzeugbar:", e && e.message);
        gescheitert.push(".ris");
      }
    }
    /* Die Zitationsdatei ist NICHT an die RIS-Einstellung gebunden.
     * Sie beantwortet eine andere Frage: nicht "wie importiere ich das in
     * Zotero", sondern "welche Zeile schreibe ich in meine Arbeit". */
    if (z.zitatDatei !== false
        && typeof PageShotZitate !== "undefined" && PageShotZitate.belegDatei) {
      try {
        await legen(".zitate.txt", "text/plain",
          PageShotZitate.belegDatei(quelle, z, z.sprache));
      } catch (e) {
        log("Zitationsdatei nicht erzeugbar:", e && e.message);
        gescheitert.push(".zitate.txt");
      }
    }
  }

  /* Die Linkkarte lag bis 2.35.17 als eigene .links.json daneben.
   *
   * Sie ist entfallen. Neben dem PDF soll GENAU EINE Datei liegen — die
   * Zitationsdatei —, damit klar ist, was zusammengehoert. Die Verweise sind
   * ohnehin dort, wo sie gebraucht werden: als anklickbare Flaechen im PDF
   * selbst. Eine Koordinatenliste als zweite Beilage beantwortete eine Frage,
   * die im Alltag niemand stellte, und verdoppelte dabei die Zahl der
   * Downloads — was in Browsern, die einer Erweiterung nur wenige ohne
   * Rueckfrage durchgehen lassen, die Zitationsdatei gefaehrdete. */

  log("Beilagen:", abgelegt.join(" ") || "(keine)",
      gescheitert.length ? "| gescheitert: " + gescheitert.join(" ") : "");
  return { abgelegt, gescheitert };
}

/* Den Artikel als Textdatei ablegen.
 *
 * Kein PDF: Ein PDF ist ein Beleg und laesst sich schlecht weiterverarbeiten.
 * Wer den Text zitieren, durchsuchen oder einem Sprachmodell vorlegen will,
 * braucht Text — und zwar mit den Verweisen, die im Bild verlorengehen.
 * Markdown nimmt Gliederung und Verweise mit und laesst sich ueberall oeffnen.
 *
 * Die Beleg-Dateien kommen mit: Wer den Artikel behaelt, will ihn spaeter auch
 * zitieren koennen. */
async function artikelAlsDatei(tab, settings) {
  await ensureContentInjected(tab.id);

  let ergebnis;
  try {
    ergebnis = await browser.tabs.sendMessage(tab.id, { cmd: "collectArticle" });
  } catch (e) {
    throw makeUserHintError(browser.i18n.getMessage("artikelNichtMoeglich")
      || "The article could not be read on this page.");
  }
  if (!ergebnis || !ergebnis.ok) {
    /* Kein Artikel ist kein Fehler des Nutzers, und keine leere Datei.
     * Eine Datei mit dem Seitengeruest darin waere schlimmer als keine: Sie
     * saehe aus wie ein Ergebnis. */
    throw makeUserHintError(browser.i18n.getMessage("artikelNichtGefunden")
      || "No article found on this page. Use \"Capture whole page\" instead.");
  }

  let quelle = null;
  try {
    if (settings.sourceMetadata !== false) {
      const src = await browser.tabs.sendMessage(tab.id, { cmd: "collectSource" });
      if (src && src.ok && src.quelle && src.quelle.titel) quelle = src.quelle;
    }
  } catch (e) { log("Quellenangaben zum Artikel nicht verfuegbar:", e && e.message); }

  const { filename, relPath } = await dateinamenBauen(tab, settings, quelle);
  const stamm = relPath.replace(/\.pdf$/i, "");

  // Kopfzeilen, damit die Datei fuer sich steht: woher, wann, wie lang.
  const kopf = [
    "# " + ((quelle && quelle.titel) || ergebnis.titel || "Artikel"),
    "",
    "> " + tab.url,
    "> " + (browser.i18n.getMessage("artikelAbgerufen") || "retrieved")
         + ": " + new Date().toISOString(),
    "",
    "---",
    "",
  ].join("\n");

  const inhalt = kopf + ergebnis.markdown;
  /* Ueber blob, nicht ueber data: — Firefox verweigert data: hier ebenso wie
   * bei den Beilagen. Siehe beilagenAdresse(). */
  const { url, blob } = beilagenAdresse("text/markdown", inhalt);
  const id = await browser.downloads.download({
    url, filename: stamm + ".md", saveAs: !!settings.saveAs, conflictAction: "uniquify",
  });
  try { await waitForDownloadComplete(id, 30000); }
  catch (e) { log("Warten auf den Download:", e.message); }
  if (blob) { try { URL.revokeObjectURL(url); } catch (_) { /* egal */ } }

  await belegeAblegen(stamm, quelle, null, {
    url: tab.url,
    sprache: belegSprache(settings),
    pdfDatei: filename.replace(/\.pdf$/i, ".md"),
    version: (browser.runtime.getManifest() || {}).version || "",
    tabId: tab && tab.id,
    risDatei: settings.sourceMetadata !== false && settings.risDatei !== false,
    zitatDatei: settings.sourceMetadata !== false && settings.zitatDatei !== false,
  });

  _lastDownloadId = id;
  _lastFilename = stamm + ".md";
  _lastSaved = true;
  _lastPages = 1;

  try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) { /* egal */ }
  fertigTon(tab && tab.id, settings, await getPlatform());

  log("Artikel gespeichert:", stamm + ".md",
      ergebnis.zeichen + " Zeichen,", ergebnis.verweise + " Verweise");

  return { ok: true, downloadId: id, filename: stamm + ".md",
           pages: 1, method: "artikel-datei", verweise: ergebnis.verweise };
}

async function captureFullPage(tab, wahl) {
  const settings = await getSettings();

  /* Der Artikel hat zwei Ausgabeformen, und die Reihenfolge ist Absicht.
   *
   * Gemeint ist damit das, was ein Leseprogramm daraus macht: der Text auf
   * Blattbreite umgebrochen, ohne Navigation, ohne Seitenleisten — ein
   * Dokument zum Lesen, nicht ein Bild einer Website. Das kann nur der
   * Vektorweg, weil dort der Browser selbst setzt.
   *
   * Wo er nicht zur Verfuegung steht — Firefox, oder die Erlaubnis wurde nicht
   * erteilt —, bleibt die Textdatei. Sie ist kein schlechterer Ersatz,
   * sondern eine andere Antwort auf dieselbe Frage: Beide geben den Lesetext
   * heraus, die eine zum Ansehen, die andere zum Weiterverarbeiten. */
  if (wahl && wahl.modus === "artikel") {
    if (settings.artikelAlsText === true) {
      return await artikelAlsDatei(tab, settings);
    }

    /* Zuerst der Vektorweg — er setzt das Blatt selbst und liefert echten
     * Text. Den gibt es nur in Chromium; in Firefox faellt die Abfrage still
     * aus. */
    try {
      const alsPdf = typeof vektorAufnahme === "function"
        ? await vektorAufnahme(tab, settings, wahl) : null;
      if (alsPdf) return alsPdf;
    } catch (e) {
      log("Vektor-Artikel nicht moeglich:", e && e.message);
    }

    /* Sonst die Leseansicht im Bildweg.
     *
     * Das ist der Weg fuer Firefox und fuer das Telefon, und dort ist er der
     * wichtigere: Ein Bildschirmfoto einer Doku-Seite mit dunklen Codefeldern
     * und dreispaltiger Navigation laesst sich auf sechs Zoll nicht lesen.
     * Die Seite wird deshalb VOR der Aufnahme umgestellt — heller Grund,
     * Leseschrift, eine Spalte — und danach zurueckgesetzt.
     *
     * Das Zuruecksetzen steht in einem finally: Bleibt die Seite umgestellt,
     * sieht der Nutzer sie so, bis er neu laedt, und weiss nicht warum. Ein
     * misslungener Artikel darf die Seite nicht dauerhaft veraendern. */
    let umgestellt = false;
    try {
      await ensureContentInjected(tab.id);
      const r = await browser.tabs.sendMessage(tab.id, {
        cmd: "leseAn",
        schriftgroesse: settings.artikelSchriftgroesse || 18,
      });
      if (r && r.ok) {
        umgestellt = true;
        log("Leseansicht gesetzt:", r.zeichen, "Zeichen");
      } else {
        /* Kein Artikel erkennbar — dann ist die Textdatei die ehrlichere
         * Antwort als eine Aufnahme der ganzen Seite unter dem Namen
         * "Artikel". */
        log("Kein Artikel erkennbar:", r && r.grund);
        return await artikelAlsDatei(tab, settings);
      }
      /* Kurz warten: Das neue Stylesheet aendert Umbruch und Hoehe der Seite,
       * und die Aufnahme misst genau diese Hoehe. */
      await sleep(250);
      return await captureFullPageInner(tab, settings);
    } finally {
      if (umgestellt) {
        try { await browser.tabs.sendMessage(tab.id, { cmd: "leseAus" }); }
        catch (e) { log("Leseansicht nicht zurueckgesetzt:", e && e.message); }
      }
    }
  }

  /* Der Knopf entscheidet ueber die Ausgabeform, nicht die Einstellungsseite.
   *
   * "A4" ist kein eigener Aufnahmeweg, sondern dieselbe Aufnahme mit anderer
   * Blatteinteilung — deshalb wird hier nur die Einstellung fuer DIESEN Lauf
   * ueberschrieben und nicht gespeichert. Wer morgen wieder eine fortlaufende
   * Seite will, klickt oben und muss nichts zuruecksetzen. */
  /* "Aufnahme fuer Druck" ist dieselbe Aufnahme wie "Ganze Seite" — nur nicht
   * fortlaufend, sondern auf Blaetter zerlegt.
   *
   * Mehr ist der Unterschied nicht, und genau deshalb hat "Ganze Seite" seit
   * 2.35.9 kein eigenes Zahnraedchen mehr: Darin stand ein Schalter "Eine
   * fortlaufende Seite", also dieselbe Entscheidung ein zweites Mal und
   * versteckt. Wer ihn wegnahm, bekam still das, wofuer es einen eigenen Knopf
   * gibt.
   *
   * Papier und Ausrichtung wirken auf das VERHAELTNIS der Blaetter und auf
   * die Blattmasse der fertigen Datei. */
  if (wahl && wahl.modus === "a4") {
    settings.singlePagePdf = false;
    settings.pageFormat = "a4";
    /* Papier und Ausrichtung wirken hier ueber das SEITENVERHAELTNIS, nicht
     * ueber absolute Masse.
     *
     * Im Bildweg steht die Breite fest: Sie ist die Breite der Aufnahme. Eine
     * Seite "quer" kann deshalb nicht breiter werden — sie kann nur flacher
     * werden. Der erste Versuch setzte stattdessen die Papiermasse in Pixel
     * ein (794 px fuer A4 quer) und traf damit bei einer Aufnahmebreite von
     * 832 px ein Verhaeltnis von 1:0,95 — fast quadratisch, wo 1:0,71
     * hingehoert. Die Einstellung wirkte also, aber falsch.
     *
     * Gerechnet wird auf der Nutzflaeche, nicht auf dem Blatt: Bei 15 mm Rand
     * bleiben von A4 180 x 267 mm. Das aufgenommene Bild fuellt die Breite
     * dieser Flaeche, die Hoehe folgt aus dem Verhaeltnis. */
    const quer = settings.druckQuer === "quer";
    const letter = settings.druckPapier === "letter";
    /* Das VOLLE Blatt, nicht die Nutzflaeche.
     *
     * Hier standen 15 mm Rand je Seite (210-30 x 297-30). Gedruckt wird aber
     * randlos — das Bild soll das Blatt fuellen. Die Folge des falschen
     * Verhaeltnisses war genau der weisse Streifen, der gemeldet wurde:
     * quer 89 pt unten, hoch 12 pt seitlich. Das Stueck passte nicht aufs
     * Blatt, also wurde es kleiner gerechnet und der Rest blieb leer.
     *
     * Wer Rand will, stellt ihn in den Einstellungen ein; er kommt dann als
     * echter Rand ins PDF und nicht als Rechenfehler. */
    const randMm = Math.max(0, Math.min(25, Number(settings.druckRandMm) || 0));
    const randPt = randMm * 72 / 25.4;
    /* Das Verhaeltnis in PUNKTEN rechnen, nicht in Millimetern.
     *
     * Die Blattmasse gehen in Punkten ins PDF (A4 595 x 842, Letter 612 x 792).
     * Wird das Verhaeltnis daneben aus Millimeterwerten gebildet, entstehen
     * durch zweimaliges Runden Differenzen — gemessen bei Letter hoch mit
     * Rand: 2 pt zuviel unten, also ein knapp sichtbarer weisser Streifen.
     * Eine Einheit fuer beides, und die Rechnung geht auf. */
    const kurzPt = (letter ? 612 : 595) - 2 * randPt;
    const langPt = (letter ? 792 : 842) - 2 * randPt;
    const verhaeltnis = quer ? (kurzPt / langPt) : (langPt / kurzPt);
    settings.pageFormat = "free";
    settings.pageVerhaeltnis = verhaeltnis;
    settings.randPt = randPt;

    /* Der Schnitt bleibt in der Textluecke — auch beim Druck.
     *
     * Zwischenzeitlich stand hier das Gegenteil: exakt auf Blatthoehe
     * schneiden, damit kein weisser Rest bleibt. Das beseitigte den Streifen
     * und zerschnitt dafuer Zeilen — bei mehrspaltigen Seiten gleich mehrere
     * nebeneinander. Ein halbierter Buchstabe ist schlimmer als ein
     * Millimeter Weiss: Das eine kostet Inhalt, das andere nur Flaeche.
     *
     * Damit trotzdem kein grosser Rest entsteht, wird das Bild nicht mehr
     * kleingerechnet, bis es ganz aufs Blatt passt, sondern auf die
     * Blattbreite gelegt und oben ausgerichtet (siehe pdf-writer.js). Was
     * unten frei bleibt, ist genau die Zeilenluecke, an der geschnitten
     * wurde — wenige Millimeter statt der 51 pt von vorher. */
    settings.breakAtLines = true;
    /* Und das Blatt selbst, in Punkten (72 je Zoll).
     * A4 misst 595 x 842 pt, Letter 612 x 792. Quer getauscht. Damit traegt
     * die fertige Datei die Groesse, die auch im Drucker liegt — statt der
     * Breite, die das Browserfenster zufaellig hatte.
     *
     * Dieselben Zahlen wie oben beim Verhaeltnis, nur ohne Randabzug: das
     * Blatt ist das Blatt, der Rand liegt darin. */
    const blattKurz = letter ? 612 : 595;
    const blattLang = letter ? 792 : 842;
    settings.blattPt = quer
      ? { breite: blattLang, hoehe: blattKurz }
      : { breite: blattKurz, hoehe: blattLang };
  }
  // Der sichtbare Ausschnitt ist keine eigene Ausgabeform, sondern dieselbe
  // Aufnahme mit einem einzigen Abschnitt: ein Bild, eine Seite, gleiche
  // Textebene, gleiche Nachweiszeile. Alles andere waere ein zweiter Weg mit
  // eigenen Fehlern.
  if (wahl && wahl.region) settings.region = wahl.region;
  log("Start capture, tab=", tab.id, "url=", tab.url, "settings=", settings);

  let originalZoom = null;
  const p = await getPlatform();
  if (!p.isAndroid && settings.captureScale && settings.captureScale !== 1.0
      && typeof browser.tabs.getZoom === "function"
      && typeof browser.tabs.setZoom === "function") {
    try {
      originalZoom = await browser.tabs.getZoom(tab.id);
      await browser.tabs.setZoom(tab.id, settings.captureScale);
      log("Zoom set:", originalZoom, "->", settings.captureScale);
      await sleep(450);
    } catch (e) { log("zoom failed:", e); originalZoom = null; }
  } else if (p.isAndroid && settings.captureScale !== 1.0) {
    log("captureScale ignored on Android (tabs.setZoom unavailable).");
  }

  try {
    return await captureFullPageInner(tab, settings);
  } finally {
    if (originalZoom !== null) {
      try { await browser.tabs.setZoom(tab.id, originalZoom); log("Zoom restored:", originalZoom); }
      catch (e) { log("zoom restore failed:", e); }
    }
  }
}

/* Prueft je Scroll-Ebene, ob Anfang und Ende tatsaechlich erfasst wurden.
 *
 * Eine Aufnahme kann aus drei Gruenden unvollstaendig sein, ohne dass es im
 * fertigen PDF auffiele: der Anfang fehlt (Startposition nicht erreicht), das
 * Ende fehlt (Schleife brach zu frueh ab) oder mittendrin klafft eine Luecke
 * (Sprungweite groesser als das Fenster). Alle drei sind hier pruefbar, weil
 * die tatsaechlichen Scroll-Positionen bekannt sind.
 *
 * Gibt {ok, meldung} zurueck - die Meldung nennt die Ebene beim Namen.
 */
function verifyCoverage(label, positions, viewH, maxScroll) {
  if (!positions.length) {
    return { ok: false, meldung: `${label}: keine Aufnahme` };
  }
  const ys = positions.slice().sort((a, b) => a - b);
  const startOk = ys[0] <= 2;
  const endOk = ys[ys.length - 1] >= maxScroll - 2;

  const gaps = [];
  let reach = 0;
  for (const y of ys) {
    if (y > reach + 2) gaps.push([Math.round(reach), Math.round(y)]);
    reach = Math.max(reach, y + viewH);
  }
  if (reach < maxScroll + viewH - 2) {
    gaps.push([Math.round(reach), Math.round(maxScroll + viewH)]);
  }

  const ok = startOk && endOk && gaps.length === 0;
  const teile = [
    `Anfang ${startOk ? "ok" : "FEHLT"}`,
    `Ende ${endOk ? "ok" : "FEHLT"}`,
    gaps.length ? `${gaps.length} Luecke(n) ${JSON.stringify(gaps.slice(0, 3))}` : "lueckenlos",
    `${positions.length} Aufnahmen`
  ];
  log(`Abdeckung ${label}: ${teile.join(", ")}`);
  return { ok, meldung: `${label}: ${teile.slice(0, 3).join(", ")}` };
}

/* Stoesst auf Android einen Download an, ohne auf die Antwort zu warten.
 *
 * Gemessen am 07.08.2026 auf dem Geraet: "TIMEOUT_A1-Android_30000ms".
 * downloads.download() schlaegt in Firefox fuer Android nicht fehl - es
 * antwortet ueberhaupt nicht. Der Vorgang geht an den System-Download-Dienst,
 * und das Versprechen loest sich nicht auf. Wer darauf wartet, wartet endlos
 * und wertet das am Ende als Fehlschlag, obwohl der Download laeuft.
 *
 * Also: anstossen, und getrennt davon zusehen, ob ein Vorgang entsteht.
 * downloads.onCreated meldet das binnen Sekundenbruchteilen und ist unabhaengig
 * davon, ob die Antwort je kommt. Das Versprechen wird nur noch protokolliert,
 * damit ein echter Fehler nicht still verschwindet.
 *
 * Zwei falsche Faehrten gingen dem voraus: erst die Annahme, Android koenne gar
 * nicht herunterladen - daher der Reiter als Umweg -, dann der Unterordner im
 * Dateinamen. Beides plausibel, beides nicht die Ursache. Wer eine Vermutung
 * nicht misst, baut den naechsten Umweg.
 */
/* Legt das PDF auf Android aus der Seite heraus ab.
 *
 * Die Download-Schnittstelle der Erweiterung gibt es in Firefox fuer Android
 * seit Version 79 nicht mehr (MDN-Kompatibilitaetsdaten: version_removed 79).
 * Aufrufe darauf bewirken nichts und werfen auch nichts - am 07.08.2026 auf dem
 * Geraet gemessen: erst verstrich eine Zeitgrenze von 30 s, dann blieb
 * downloads.onCreated stumm. Die urspruengliche Entscheidung im Code, auf
 * Android nicht herunterzuladen, war also richtig; erst der Umweg ueber einen
 * Reiter war es nicht.
 *
 * Ein Anker mit download-Attribut ist dagegen gewoehnliches Web. Er wird im
 * Inhaltsskript der aufgenommenen Seite geklickt - dort, wo der Nutzer steht,
 * ohne neuen Reiter. Die Bytes gehen als Uint8Array durch die
 * Nachrichtenschicht; Firefox uebertraegt sie als strukturierte Kopie, ohne den
 * Umweg ueber eine Zeichenkette. */
async function speichereImTab(tabId, pdfBytes, filename) {
  if (tabId == null) throw new Error("Kein Reiter fuer das Ablegen vorhanden");
  const antwort = await browser.tabs.sendMessage(tabId, {
    cmd: "savePdf",
    bytes: Array.from(pdfBytes),
    name: filename
  });
  if (!antwort || !antwort.ok) {
    throw new Error((antwort && antwort.error) || "Die Seite konnte die Datei nicht ablegen");
  }
  return null;   // Es gibt keine Vorgangskennung - der Browser fuehrt ihn selbst.
}

async function captureFullPageInner(tab, settings) {
  // Textebene: wird im selben Seitenzustand gesammelt wie die Bilder.
  // Was angefordert war und nicht kam. Ein PDF ohne Textebene sieht aus wie
  // eines mit — der Unterschied faellt erst auf, wenn jemand Monate spaeter
  // darin sucht. Am 4. August 2026 kamen zwei Aufnahmen von einem
  // Android-Geraet zurueck: keine Textebene, keine Quellenangaben, keine
  // Meldung. Beide Aufrufe waren in try/catch, das nur ins Protokoll schrieb.
  const fehlteStill = [];
  // Wie oft die Seite waehrend der Aufnahme nachgewachsen ist.
  const seiteWuchs = [];
  let linkKarte = null;
  // Blieb die Hoehe auch nach drei Vorlaufrunden in Bewegung?
  let vorlaufUnruhig = false;
  let textWoerter = null;
  let textBloecke = [];
  let quelle = null;
  let textSeiteBreite = 0;
  await ensureContentInjected(tab.id);

  const layout = await browser.tabs.sendMessage(tab.id, { cmd: "getLayout" });
  if (!layout || !layout.totalH || !layout.viewportH) {
    throw new Error("Layout-Daten fehlen");
  }
  log("Layout:", layout);

  if (layout.totalH <= layout.viewportH + 4) {
    log("Page fits in one viewport — single capture path.");
  }

  const probe = await browser.tabs.sendMessage(tab.id, { cmd: "probe" });
  log("Probe result:", probe);
  if (!probe || !probe.moved) {
    log("WARNING: Pre-flight scroll probe did NOT move the page!");
  }

  await browser.tabs.sendMessage(tab.id, { cmd: "freeze" });
  await sleep(300);

  if (settings.hideSticky) {
    // Erste Phase: nur stoerende Overlays. Eine fixe Navigationsspalte bleibt
    // vorerst stehen, damit sie im ersten Segment erhalten bleibt.
    await browser.tabs.sendMessage(tab.id, { cmd: "hideSticky", includeSideNav: false });
    await sleep(80);
  }

  const segments = [];
  const stepCss = Math.max(100, layout.viewportH - 40);
  let totalH = layout.totalH;
  let maxScroll = Math.max(0, totalH - layout.viewportH);
  let y = 0;
  let safety = 0;
  let lastActualY = -1;
  let stuckCount = 0;

  /* Deckel gegen endlosen Nachschub.
   *
   * Seiten mit unendlichem Scroll (Zeitleisten, Suchergebnisse, Foren) laden
   * beim Scrollen immer weiter nach. Dann waechst totalH schneller, als
   * gescrollt wird, maxScroll waechst mit, und die Abbruchbedingung
   * "actualY >= maxScroll" tritt nie ein. Vorher endete das nach 400
   * Schritten in einem geworfenen Fehler: kein PDF, nur eine Meldung -
   * obwohl bis dahin hunderte brauchbare Segmente vorlagen.
   *
   * Deshalb zwei Grenzen. Die erste zaehlt, wie oft die Seite waehrend der
   * Aufnahme nachgewachsen ist; ab einer Schwelle gilt die Hoehe, die beim
   * Start gemessen wurde, als Ziel - was danach nachkommt, waere ohnehin
   * nie zu Ende zu fotografieren. Die zweite ist eine harte Schrittgrenze,
   * die nicht mehr wirft, sondern abschliesst und den Nutzer informiert.
   */
  const NACHWUCHS_SCHWELLE = 12;      // so oft darf die Seite wachsen
  const SCHRITT_GRENZE = 400;         // harte Obergrenze, danach wird geliefert
  let nachgewachsen = 0;
  let endlosVerdacht = false;
  const hoeheBeimStart = totalH;
  let abgeschnitten = false;

  /* Vorlauf: die Seite einmal durchscrollen, bevor fotografiert wird.
   *
   * Seiten, die beim Scrollen nachladen, wachsen mitten in der Aufnahme.
   * Alles unterhalb der Einfuegestelle rutscht nach unten, und ein bereits
   * fotografierter Abschnitt kommt im naechsten Bild ein zweites Mal vor —
   * im PDF steht er dann doppelt, der erste angeschnitten. Gemessen am
   * 4. August 2026 an einer PubMed-Seite: "Comment in", "Cited by" und
   * "Similar articles" erschienen je zweimal.
   *
   * Nachtraeglich ist das nicht zu beheben; die alten Bilder zeigen einen
   * Zustand, den es nicht mehr gibt. Also vorher: einmal durchlaufen, ohne
   * Bilder, bis die Hoehe stehenbleibt. Ein Durchlauf ohne Aufnahme ist
   * billig — es entfaellt genau der teure Teil.
   *
   * Hoechstens drei Runden: Seiten mit endlosem Nachschub (Zeitleisten)
   * werden nie stabil, und dort ist ein Abbruch richtiger als eine Schleife.
   */
  for (let runde = 1; runde <= 3; runde++) {
    const vorher = totalH;
    let vy = 0, schutz = 0;
    while (vy < maxScroll && ++schutz <= 400) {
      await browser.tabs.sendMessage(tab.id, { cmd: "scrollTo", y: vy })
        .catch(() => null);
      await sleep(Math.min(120, settings.settlingMs));
      vy += stepCss;
    }
    await browser.tabs.sendMessage(tab.id, { cmd: "scrollTo", y: maxScroll })
      .catch(() => null);
    await sleep(Math.min(250, settings.settlingMs));

    const nach = await browser.tabs.sendMessage(tab.id, { cmd: "currentTotalH" })
      .catch(() => null);
    if (nach && nach.totalH && nach.totalH > totalH) {
      totalH = nach.totalH;
      maxScroll = Math.max(0, totalH - layout.viewportH);
    }
    log("Vorlauf Runde", runde, ":", vorher, "->", totalH);
    if (totalH === vorher) break;          // steht still, es kann losgehen
    if (runde === 3) {
      log("Vorlauf: Hoehe wurde nicht stabil, nehme trotzdem auf");
      vorlaufUnruhig = true;
    }
  }
  await browser.tabs.sendMessage(tab.id, { cmd: "scrollTo", y: 0 }).catch(() => null);
  await sleep(Math.min(250, settings.settlingMs));

  const clipModeWanted = settings.appLayout || "context";
  const sideCaptures = [];

  try {
    /* Nebenbereiche (z.B. scrollbare Seitenleiste) eigenstaendig durchscrollen.
     *
     * Laeuft nach dem Hauptdurchlauf, damit sich beide nicht gegenseitig stoeren.
     * Ohne diesen Schritt endet eine scrollbare Seitenleiste im PDF am Ende des
     * ersten Segments, obwohl sie noch Inhalt haette.
     */
    const sideList = (layout.sideScrollers || []);
    // Auch bei Fenster-Scroll: Dokumentations-Seiten legen ihre Navigation
    // als festes, eigenstaendig scrollendes Element an - dort gibt es keinen
    // Clip, aber sehr wohl einen Nebenbereich mit eigenem Inhalt.
    if (clipModeWanted !== "full" && sideList.length) {
      for (let idx = 0; idx < sideList.length; idx++) {
        const rect = sideList[idx];
        const shots = [];
        const stepSide = Math.max(80, rect.h - 30);
        let sy = 0, lastY = 0, guard = 0;
        try {
          while (true) {
            const res = await browser.tabs.sendMessage(tab.id, { cmd: "scrollSide", index: idx, y: sy });
            if (!res || !res.ok) break;
            const actual = res.actualY || 0;
            if (shots.length && actual <= lastY + 2) break;      // kommt nicht weiter
            await sleep(Math.min(400, settings.settlingMs));
            let dataUrl;
            try { dataUrl = await browser.tabs.captureVisibleTab(tab.windowId, { format: "png" }); }
            catch (_) { dataUrl = await browser.tabs.captureVisibleTab({ format: "png" }); }
            const img = await blobToImage(await dataUrlToBlob(dataUrl));
            shots.push({ y: actual, img });
            lastY = actual;
            if (actual >= rect.max - 2) break;
            sy = actual + stepSide;
            if (++guard > 30) break;
          }
        } catch (e) { log("Nebenbereich", idx, "abgebrochen:", e.message); }
        if (shots.length > 1) {
          sideCaptures.push({ rect, shots: shots.slice(1), lastY });
          log("Nebenbereich", idx, "->", shots.length - 1, "zusaetzliche Segmente");
        }
      }
      // Nebenbereiche zurueckstellen, damit die Seite unveraendert bleibt
      for (let idx = 0; idx < sideList.length; idx++) {
        await browser.tabs.sendMessage(tab.id, { cmd: "scrollSide", index: idx, y: 0 }).catch(() => {});
      }
    }

    while (true) {
      const targetY = Math.min(y, maxScroll);
      const scrollRes = await browser.tabs.sendMessage(tab.id, { cmd: "scrollTo", y: targetY });
      const actualY = scrollRes ? scrollRes.actualY : targetY;
      log("Scrolled to", targetY, "actual=", actualY, "method=", scrollRes && scrollRes.method);

      if (Math.abs(actualY - lastActualY) <= 2 && segments.length > 0) {
        stuckCount++;
        log("Stuck at scrollY=", actualY, " stuckCount=", stuckCount);
        if (stuckCount >= 3) {
          log("Aborting loop — scroll position not advancing.");
          break;
        }
      } else {
        stuckCount = 0;
      }
      lastActualY = actualY;

      await sleep(settings.settlingMs);

      // Sicherstellen dass unser Ziel-Tab noch aktiv ist. Auf Android verwechseln
      // Nutzer schnell den Tab, captureVisibleTab erfasst dann den falschen.
      try {
        const [active] = await browser.tabs.query({ active: true, currentWindow: true });
        if (!active || active.id !== tab.id) {
          log("Target tab lost focus — reactivating tab.id=" + tab.id);
          await browser.tabs.update(tab.id, { active: true });
          await sleep(200);
        }
      } catch (_) { /* Android: currentWindow ggf. nicht verfuegbar, ignorieren */ }

      // WICHTIG: Auf Firefox for Android existiert die windows-API nicht,
      // tab.windowId ist dort oft undefined -> captureVisibleTab wuerde still
      // fehlschlagen. Erst mit windowId versuchen, bei Fehler ohne.
      let dataUrl;
      try {
        dataUrl = await browser.tabs.captureVisibleTab(tab.windowId, { format: "png" });
      } catch (e1) {
        log("captureVisibleTab(windowId) failed, retrying without windowId:", e1.message);
        dataUrl = await browser.tabs.captureVisibleTab({ format: "png" });
      }
      const blob = await dataUrlToBlob(dataUrl);
      const img = await blobToImage(blob);
      log("Captured segment", segments.length, "at actualY=", actualY, "size=", img.naturalWidth, "x", img.naturalHeight);

      segments.push({
        y: actualY,
        img,
        pxW: img.naturalWidth,
        pxH: img.naturalHeight
      });

      // Zweite Phase: Nach dem ersten Segment verschwindet auch eine fixe
      // Navigationsspalte. Sonst wandert sie durch jedes weitere Segment und
      // zerschneidet den Verlauf - dasselbe Prinzip wie der Kontext-Modus bei
      // App-Layouts, nur fuer Seiten, bei denen das Fenster selbst scrollt.
      if (settings.hideSticky && segments.length === 1 && clipModeWanted !== "full") {
        await browser.tabs.sendMessage(tab.id, { cmd: "hideSticky", includeSideNav: true })
          .catch(() => {});
        await sleep(60);
      }

      // Kein Fortschritts-Feedback waehrend der Aufnahme. Auf Android stapelten
      // sich die Prozent-Meldungen im Benachrichtigungsbereich; der Nutzer will
      // eine einzige Meldung, und zwar wenn das PDF fertig ist.

      // Nur der sichtbare Ausschnitt: nach dem ersten Abschnitt ist Schluss.
      // Der Rest der Kette laeuft unveraendert weiter — ein Abschnitt ergibt
      // ein Bild, eine Seite und dieselbe Nachweiszeile wie sonst. Eine
      // eigene Ausgabeform waere ein zweiter Ort fuer dieselben Fehler.
      // Bereichsauswahl: nur so weit aufnehmen, wie der gewaehlte Ausschnitt
      // reicht. Nach dem ersten Abschnitt abzubrechen war falsch — der zeigt
      // den Seitenanfang, waehrend die Auswahl an der Stelle geschah, an der
      // der Nutzer stand. Bei einer weit gescrollten Seite kam dadurch ein
      // voellig anderer Bildteil ins PDF.
      if (settings.region) {
        const untenCss = settings.region.y + settings.region.h;
        const erfasstCss = actualY + layout.viewportH;
        if (erfasstCss >= untenCss) {
          log("Bereichsauswahl — Ausschnitt vollstaendig erfasst bei y=", actualY);
          break;
        }
      }

      const fresh = await browser.tabs.sendMessage(tab.id, { cmd: "currentTotalH" }).catch(() => null);
      if (fresh && fresh.totalH && fresh.totalH > totalH && !endlosVerdacht) {
        if (++nachgewachsen >= NACHWUCHS_SCHWELLE) {
          endlosVerdacht = true;
          // Zuerst die Seite selbst fragen, wo sie endet. Der Seitenfuss steht
          // im Dokument unterhalb des Inhalts - auch bei Seiten, die darueber
          // endlos nachladen. Wo es ihn gibt, ist er die ehrliche Grenze;
          // ein Zaehler waere willkuerlich und schnitte je nach
          // Netzgeschwindigkeit woanders ab.
          let grenze = null;
          try {
            const pe = await browser.tabs.sendMessage(tab.id, { cmd: "pageEnd" });
            if (pe && Number.isFinite(pe.ende) && pe.ende > layout.viewportH) grenze = pe.ende;
          } catch (_) { /* alte Fassung des Inhaltsskripts: Deckel greift */ }

          if (grenze) {
            maxScroll = Math.max(0, grenze - layout.viewportH);
            log("Endloser Nachschub - Seitenfuss bei y=", Math.round(grenze),
                "gefunden, Aufnahme endet dort");
          } else {
            maxScroll = Math.max(0, hoeheBeimStart - layout.viewportH);
            log("Endloser Nachschub (", nachgewachsen, "x gewachsen), kein Seitenfuss - "
                + "Aufnahme endet bei der Hoehe vom Start:", hoeheBeimStart);
          }
          if (actualY >= maxScroll - 2) { abgeschnitten = true; break; }
        }
      }
      if (fresh && fresh.totalH && fresh.totalH > totalH && !endlosVerdacht) {
        log("Lazy-load grew page:", totalH, "->", fresh.totalH);
        // Das Nachwachsen wird hier aufgefangen, damit das Ende nicht fehlt.
        // Was es mit dem bereits Aufgenommenen macht, faengt es nicht auf:
        // waechst die Seite oberhalb der laufenden Position, rutscht alles
        // darunter nach unten, und ein schon fotografierter Abschnitt kommt
        // im naechsten Bild ein zweites Mal vor. Im fertigen PDF steht er
        // dann doppelt, der erste davon oft angeschnitten.
        //
        // Gemessen am 4. August 2026 an einer PubMed-Seite: "Comment in",
        // "Cited by" und "Similar articles" — genau die Abschnitte, die dort
        // nachgeladen werden — erschienen je zweimal.
        //
        // Rueckgaengig machen laesst sich das nicht: die alten Bilder zeigen
        // einen Zustand, den es nicht mehr gibt. Gesagt werden muss es.
        seiteWuchs.push({ von: totalH, auf: fresh.totalH, beiY: actualY });
        totalH = fresh.totalH;
        maxScroll = Math.max(0, totalH - layout.viewportH);
      }

      if (actualY >= maxScroll - 2) { if (endlosVerdacht) abgeschnitten = true; break; }
      y += stepCss;
      if (y > maxScroll) y = maxScroll;
      if (++safety > SCHRITT_GRENZE) {
        // Nicht werfen: bis hierher liegen brauchbare Segmente vor, und ein
        // unvollstaendiges PDF ist mehr wert als eine Fehlermeldung.
        log("Schrittgrenze erreicht (", SCHRITT_GRENZE, ") - Aufnahme wird abgeschlossen");
        abgeschnitten = true;
        break;
      }
    }
    // Text jetzt einsammeln — nach dem Ausblenden fixierter Elemente und
    // bevor die Seite zurueckgesetzt wird. Spaeter waere der Zustand ein
    // anderer als der, den die Bilder zeigen, und eine Textebene, die etwas
    // anderes sagt als das Bild, ist schlechter als gar keine.
    // Quellenangaben aus der Seite lesen. Ausschliesslich aus dem geladenen
    // Dokument — kein Dienst wird befragt, damit die Erweiterung weiterhin
    // ohne jede Netzverbindung auskommt.
    if (settings.sourceMetadata !== false) {
      try {
        const src = await browser.tabs.sendMessage(tab.id, { cmd: "collectSource" });
        if (src && src.ok && src.quelle && src.quelle.titel) {
          quelle = src.quelle;
          log("Quelle:", quelle.art, "—", quelle.herkunft,
              quelle.vollstaendig ? "(vollstaendig)" : "(unvollstaendig)");
        } else {
          fehlteStill.push({ was: "quelle", grund: "die Seite deklariert keine" });
        }
      } catch (e) {
        log("Quellenangaben nicht verfuegbar:", e && e.message);
        fehlteStill.push({ was: "quelle", grund: (e && e.message) || "unbekannt" });
      }

      /* Eine magere Angabe ist immer noch eine Angabe.
       *
       * Bisher entstanden RIS-Satz und Zitationsdatei NUR, wenn die Seite
       * verwertbare Meta-Angaben trug. Gab sie nichts her, fehlten die
       * Beilagen ersatzlos — und der Nutzer erfuhr nicht einmal, warum.
       * Gemeldet am 18.08.2026: Zitation eingeschaltet, kein .txt daneben.
       *
       * Dabei liegt das Wesentliche einer Internetquelle immer vor: die
       * Adresse, der Zeitpunkt des Abrufs und ein Titel aus dem Reiter. Genau
       * diese drei verlangt jede Zitierweise fuer eine Webseite. Was fehlt,
       * steht in der Datei als fehlend — das ist ehrlicher und brauchbarer
       * als gar keine Datei. */
      if (!quelle) {
        const jetzt = new Date();
        quelle = {
          art: "Internetquelle",
          autoren: [],
          titel: (tab.title || "").trim() || tab.url,
          url: tab.url,
          urlZitat: tab.url,
          abrufdatum: jetzt.toISOString().slice(0, 10),
          abrufzeit: jetzt.toISOString(),
          herkunft: "Adresse und Abrufzeitpunkt (die Seite gibt keine Angaben her)",
          vollstaendig: false,
        };
        log("Ersatzangabe gebildet — die Seite deklariert nichts.");
      }
    }
    if (settings.linkMap) {
      // Im selben Zustand wie die Bilder erheben. Nach dem Zuruecksetzen
      // waeren die Koordinaten die einer anderen Seite.
      try {
        const lm = await browser.tabs.sendMessage(tab.id, { cmd: "collectLinks" });
        if (lm && lm.ok && lm.links && lm.links.length) {
          linkKarte = lm;
          log("Linkkarte:", lm.links.length, "Verweise");
        } else {
          fehlteStill.push({ was: "linkkarte", grund: "keine Verweise gefunden" });
        }
      } catch (e) {
        log("Linkkarte nicht verfuegbar:", e && e.message);
        fehlteStill.push({ was: "linkkarte", grund: (e && e.message) || "unbekannt" });
      }
    }
    if (settings.textLayer !== false) {
      try {
        const tl = await browser.tabs.sendMessage(tab.id, { cmd: "collectText" });
        if (tl && tl.ok && tl.woerter && tl.woerter.length) {
          textWoerter = tl.woerter;
          textBloecke = tl.bloecke || [];
          textSeiteBreite = tl.seite && tl.seite.w ? tl.seite.w : 0;
          log("Textebene:", textWoerter.length, "Woerter,", textBloecke.length,
              "Bloecke, Seitenbreite", textSeiteBreite);
        } else {
          fehlteStill.push({ was: "textebene", grund: "kein Text zurueckgeliefert" });
        }
      } catch (e) {
        log("Textebene nicht verfuegbar:", e && e.message);
        fehlteStill.push({ was: "textebene", grund: (e && e.message) || "unbekannt" });
      }
    }
  } finally {
    await browser.tabs.sendMessage(tab.id, { cmd: "restore" }).catch(() => {});
  }

  log("Capture loop done. Segments=", segments.length, "finalTotalH=", totalH);

  // --- Vollstaendigkeit je Scroll-Ebene pruefen ----------------------------
  const coverage = [];
  coverage.push(verifyCoverage("Hauptbereich", segments.map(s2 => s2.y),
                               layout.viewportH, maxScroll));
  for (let i = 0; i < sideCaptures.length; i++) {
    const side = sideCaptures[i];
    coverage.push(verifyCoverage(`Nebenbereich ${i + 1}`,
                                 [0].concat(side.shots.map(s2 => s2.y)),
                                 side.rect.h, side.rect.max));
  }
  // Was still fehlte, gehoert in dieselbe Meldung wie eine luckenhafte
  // Abdeckung: beides macht das PDF unbrauchbarer, als es aussieht.
  const NAMEN = { textebene: "Textebene", quelle: "Quellenangaben",
                  linkkarte: "Linkkarte" };
  const stilleLuecken = fehlteStill.map(
    f => (NAMEN[f.was] || f.was) + " (" + f.grund + ")");

  // Nachgewachsene Seite: derselbe Rang wie eine Luecke in der Abdeckung.
  // Wer es nicht erfaehrt, haelt einen doppelten Abschnitt fuer die Seite.
  if (vorlaufUnruhig) {
    stilleLuecken.push(
      "die Seite laedt fortlaufend nach und kam auch im Vorlauf nicht zur Ruhe "
      + "— Abschnitte koennen doppelt erscheinen");
  }
  if (seiteWuchs.length) {
    const gesamt = seiteWuchs[seiteWuchs.length - 1].auf - seiteWuchs[0].von;
    stilleLuecken.push(
      "die Seite lud waehrend der Aufnahme nach (" + seiteWuchs.length + "x, "
      + "insgesamt " + Math.round(gesamt) + " px) — Abschnitte koennen doppelt "
      + "erscheinen; mit hoeherer Wartezeit je Schritt erneut aufnehmen");
  }

  // Endloser Nachschub: eigene Meldung, weil hier nichts schiefging - die
  // Seite hat schlicht kein Ende. Der Nutzer soll wissen, warum das PDF
  // kuerzer ist als das, was er auf dem Bildschirm weiterscrollen koennte.
  if (abgeschnitten) {
    log("Aufnahme bei endlosem Nachschub abgeschlossen nach", segments.length, "Segmenten");
    notifyHint(browser.i18n.getMessage("endlessScrollHint")
      || "Die Seite laedt beim Scrollen immer weiter nach. Aufgenommen wurde der Stand vom Anfang.");
  }

  const unvollstaendig = coverage.filter(c => !c.ok);
  if (unvollstaendig.length || stilleLuecken.length) {
    const teile = unvollstaendig.map(c => c.meldung).concat(stilleLuecken);
    log("WARNUNG: unvollstaendig —", teile.join(" | "));
    /* Auf dem Telefon nicht melden.
     *
     * Dort steht die Leiste ohnehin voll, und diese Angabe ("Hauptbereich:
     * Anfang ok, Ende FEHLT, 1 Luecke(n) [[10873,10899]]") sagt niemandem
     * etwas, der den Quelltext nicht kennt. Am 07.08.2026 standen drei
     * Meldungen fuer eine Aufnahme in der Leiste, diese als dritte. Auf
     * Android bleibt es bei einer: fertig oder nicht. Im Protokoll steht die
     * Einzelheit weiterhin.
     *
     * getPlatform() statt der Variablen p - die wird erst weiter unten
     * deklariert, ein Zugriff hier oben liefe in die temporale Todeszone. */
    if (!(await getPlatform()).isAndroid) {
      notifyHint((browser.i18n.getMessage("incompleteHint")
                  || "Teile der Seite konnten nicht vollstaendig erfasst werden:")
                 + " " + teile.join(" · "));
    }
  } else {
    log("Abdeckung vollstaendig in allen", coverage.length, "Scroll-Ebene(n).");
  }

  if (segments.length === 1 && totalH > layout.viewportH * 1.2) {
    log("WARNING: Only one segment captured but page is taller than viewport.");
  }

  log("Stitching", segments.length, "segments via big-canvas.");

  // Skalierung Screenshot zu CSS-Pixel. Ueber die FENSTERhoehe gerechnet, denn
  // der Screenshot bildet immer das ganze Fenster ab - auch wenn nur ein
  // innerer Container gescrollt wird. layout.winH fehlt bei alten Content-
  // Skripten, dann greift der bisherige Weg ueber viewportH.
  const dprY = segments[0].pxH / (layout.winH || layout.viewportH);

  /* Bei App-Layouts (Gmail, Outlook, Notion) liefert das Content-Skript den
   * Ausschnitt des Scroll-Containers. Ohne ihn landen Kopfzeile und
   * Seitenleiste in JEDEM Segment erneut im PDF und zerschneiden den Verlauf.
   *
   * Drei Umgangsweisen, per Einstellung waehlbar:
   *   context - Menue und Seitenleiste einmal oben, darunter laeuft nur der
   *             Inhalt weiter; die frei werdende Flaeche bekommt die
   *             Hintergrundfarbe der Seite. Standard.
   *   crop    - ausschliesslich der Inhaltsbereich, schmalstes Ergebnis.
   *   full    - alles unveraendert, Rahmen wiederholt sich (Notbehelf).
   */
  const clipMode = clipModeWanted === "full" || !layout.clip ? "full" : clipModeWanted;
  const clip = clipMode === "full" ? null : layout.clip;

  const srcX = clip ? Math.round(clip.x * dprY) : 0;
  const srcY = clip ? Math.round(clip.y * dprY) : 0;
  const clipW = clip ? Math.round(clip.w * dprY) : segments[0].pxW;
  const segH = clip ? Math.round(clip.h * dprY) : segments[0].pxH;
  const lastSeg = segments[segments.length - 1];

  // Im Kontext-Modus bleibt die volle Fensterbreite stehen, und der Inhalt
  // beginnt erst unterhalb der Kopfzeile.
  const keepFrame = clipMode === "context";
  // Nicht const: der Zuschnitt auf einen gewaehlten Bereich aendert die
  // Breite, und alles Folgende — Kacheln, Seiten, PDF — rechnet mit pxW.
  let pxW = keepFrame ? segments[0].pxW : clipW;
  const contentTop = keepFrame ? srcY : 0;

  /* Die Hoehe richtet sich nach dem LAENGSTEN Bereich, nicht nur nach dem
   * Hauptbereich. Sonst wird eine Seitenleiste, die mehr Inhalt hat als die
   * Liste daneben, am unteren Rand abgeschnitten - Datenverlust, der im
   * fertigen PDF nicht mehr auffaellt.
   */
  let bigH = Math.max(contentTop + Math.round(lastSeg.y * dprY) + segH,
                      segments[0].pxH);
  // Gilt fuer beide Faelle: der laengste Bereich bestimmt die Hoehe, egal ob
  // ein innerer Container oder das Fenster selbst gescrollt wurde.
  for (const side of sideCaptures) {
    const need = Math.round(side.rect.y * dprY)
               + Math.round(side.lastY * dprY)
               + Math.round(side.rect.h * dprY);
    if (need > bigH) {
      log("Nebenbereich ist laenger - Hoehe", bigH, "->", need);
      bigH = need;
    }
  }

  log("Big canvas size:", pxW, "x", bigH, "mode=" + clipMode);

  // Nicht const: der Zuschnitt ersetzt die Flaeche.
  let big = document.createElement("canvas");
  big.width = pxW;
  big.height = bigH;
  const bigCtx = big.getContext("2d");
  bigCtx.fillStyle = "#ffffff";
  bigCtx.fillRect(0, 0, pxW, bigH);

  /* Zusaetzliche Segmente der Nebenbereiche an ihre Position zeichnen.
   *
   * Gilt fuer beide Faelle: bei App-Layouts die scrollbare Seitenleiste, bei
   * Fenster-Scroll die feste Navigationsspalte einer Dokumentations-Seite.
   * Beide stehen im ersten Abschnitt bereits im Bild - hier kommt nur ihre
   * Fortsetzung darunter dazu.
   */
  function drawSideAreas() {
    for (const side of sideCaptures) {
      const sx = Math.round(side.rect.x * dprY);
      const sw = Math.round(side.rect.w * dprY);
      const sh = Math.round(side.rect.h * dprY);
      const sy = Math.round(side.rect.y * dprY);
      for (const shot of side.shots) {
        const destY = sy + Math.round(shot.y * dprY);
        // Die Hoehe wurde auf den laengsten Bereich ausgelegt; ein Rest hier
        // waere ein Rechenfehler und soll auffallen statt still zu fehlen.
        if (destY + sh > bigH) {
          log("WARNUNG: Nebenbereich passt nicht -", destY + sh, ">", bigH);
          break;
        }
        bigCtx.drawImage(shot.img, sx, sy, sw, sh, sx, destY, sw, sh);
      }
      log("Nebenbereich fortgesetzt bis",
          sy + Math.round(side.lastY * dprY) + sh, "von", bigH);
    }
  }

  if (!clip) {
    for (const seg of segments) {
      bigCtx.drawImage(seg.img, 0, Math.round(seg.y * dprY));
    }
    drawSideAreas();
  } else if (!keepFrame) {
    for (const seg of segments) {
      bigCtx.drawImage(seg.img, srcX, srcY, clipW, segH,
                       0, Math.round(seg.y * dprY), clipW, segH);
    }
  } else {
    // Erstes Segment vollstaendig - hier bleiben Menue und Seitenleiste.
    const frameH = segments[0].pxH;
    bigCtx.drawImage(segments[0].img, 0, 0);

    /* Nebenbereiche mit eigenem Inhalt fortsetzen.
     *
     * Eine scrollbare Seitenleiste endet sonst am Ende des ersten Segments,
     * obwohl sie weitergeht. Ihre zusaetzlichen Segmente werden hier
     * untereinander in dieselbe Spalte gezeichnet - so weit ihr Inhalt
     * reicht. Erst danach greift die Fuellfarbe.
     */
    drawSideAreas();

    /* Die Flaeche unterhalb davon bekommt die Farbe, die im Screenshot
     * tatsaechlich neben dem Inhalt liegt. Aus CSS geraten geht daneben:
     * bei Gmail ist der Scroll-Container weiss, die Seitenleiste daneben
     * aber leicht blaustichig - der Sprung faellt im PDF sofort auf.
     * Links und rechts werden getrennt abgetastet, weil sie sich
     * unterscheiden koennen (Seitenleiste vs. Icon-Spalte).
     */
    const fillSide = (x0, x1) => {
      if (x1 - x0 < 2) return;
      const counts = new Map();
      for (let i = 1; i <= 4; i++) {
        const y = Math.round(frameH - (frameH - srcY) * (i / 5));
        for (let j = 1; j <= 4; j++) {
          const x = Math.round(x0 + (x1 - x0) * (j / 5));
          try {
            const d = bigCtx.getImageData(x, y, 1, 1).data;
            const key = `${d[0]},${d[1]},${d[2]}`;
            counts.set(key, (counts.get(key) || 0) + 1);
          } catch (_) { /* ausserhalb - ignorieren */ }
        }
      }
      let win = null, n = 0;
      for (const [k, c] of counts) if (c > n) { win = k; n = c; }
      bigCtx.fillStyle = win ? `rgb(${win})` : (layout.bgColor || "#ffffff");
      bigCtx.fillRect(x0, frameH, x1 - x0, bigH - frameH);
    };
    fillSide(0, srcX);                 // links neben dem Inhalt
    fillSide(srcX + clipW, pxW);       // rechts daneben

    // Inhaltsspalte selbst neutral fuellen, damit unter dem letzten Segment
    // kein weisser Rest steht, falls die Seite kuerzer endet als erwartet.
    bigCtx.fillStyle = "#ffffff";
    bigCtx.fillRect(srcX, frameH, clipW, bigH - frameH);

    for (let i = 1; i < segments.length; i++) {
      bigCtx.drawImage(segments[i].img, srcX, srcY, clipW, segH,
                       srcX, contentTop + Math.round(segments[i].y * dprY), clipW, segH);
    }
  }

  // Adaptive tilePx-Berechnung fuer Android: passt sich an Device an.
  // Samsung S24 Ultra (DPR 3.5, 12 GB RAM) bekommt groessere Kacheln als
  // ein Einsteiger-Geraet (DPR 2.0, 2 GB RAM). Auf Desktop bleibt User-Setting.
  let effectiveTilePx = settings.tilePx || 4000;
  const _plat = await getPlatform();
  if (_plat.isAndroid) {
    const dpr = layout.dpr || 2;
    const memGb = layout.deviceMemoryGb || 4;   // konservativer Default
    // Basis: ~2500 CSS-Pixel pro Tile, skaliert mit DPR (mehr DPR = groessere Bild-Bytes)
    let base = Math.round(2500 * (2 / Math.max(1, dpr)));
    // RAM-Skalierung: <3 GB streng, >=6 GB grosszuegig
    if (memGb < 3)      base = Math.round(base * 0.7);
    else if (memGb >= 6) base = Math.round(base * 1.4);
    effectiveTilePx = Math.max(800, Math.min(4000, base));
    log("Adaptive tilePx=" + effectiveTilePx + " (dpr=" + dpr + ", memGb=" + memGb + ", user=" + settings.tilePx + ")");
  }

  // ---------------------------------------------------------------------
  // Seitenumbruch
  //
  // Der feste Schnitt alle n Pixel zerschneidet Zeilen: an vier gemessenen
  // Seiten (Springer, PLOS, MDPI, Wikipedia) traf er in 30 von 46 Faellen
  // mitten in eine Textzeile. Wird der Schnitt stattdessen nach oben in die
  // naechste Luecke gezogen, sind es 2 von 47 — der Rest sind Bloecke, die
  // hoeher sind als das Toleranzfenster; dort bleibt nur der harte Schnitt.
  // Der Preis ist ein leerer Rand von 1,1 bis 2,5 Prozent je Seite.
  // ---------------------------------------------------------------------

  /** Zeilen und unteilbare Elemente zu Baendern verschmelzen. */
  function baender(woerter, bloecke, skala) {
    const roh = [];
    for (const w of woerter || []) roh.push([w.y * skala, (w.y + w.h) * skala]);
    for (const b of bloecke || []) roh.push([b.a * skala, b.b * skala]);
    if (!roh.length) return [];
    roh.sort((p, q) => p[0] - q[0] || p[1] - q[1]);
    const out = [roh[0].slice()];
    for (let i = 1; i < roh.length; i++) {
      // 2 px Spiel: Unterlaengen benachbarter Zeilen ueberlappen sich sonst
      // scheinbar und verschmelzen die ganze Seite zu einem Band.
      if (roh[i][0] < out[out.length - 1][1] - 2) {
        out[out.length - 1][1] = Math.max(out[out.length - 1][1], roh[i][1]);
      } else out.push(roh[i].slice());
    }
    return out;
  }

  /**
   * Liefert die Seitengrenzen im Gesamtbild, einschliesslich 0 und bigH.
   * seitenHoehe === null bedeutet: aus der Breite ein A4-Verhaeltnis ableiten.
   */
  function umbruchstellen(woerter, bloecke, seitenBreiteCss, pxW, bigH, seitenHoehe, anZeilen) {
    /* A4 hoch, randlos: 210 x 297 mm. Die aufgenommene Breite fuellt die
     * Blattbreite, daraus folgt die Hoehe.
     *
     * Hier stand die NUTZFLAECHE bei 15 mm Rand (180 x 267 mm), also ein
     * Verhaeltnis von 1:1,483 statt 1:1,414. Das Stueck war damit zu hoch fuer
     * das Blatt, wurde beim Einpassen verkleinert, und seitlich blieben 12 pt
     * weiss — genau der gemeldete Streifen. */
    const hoehe = seitenHoehe || Math.round(pxW * 297 / 210);
    const grenzen = [0];
    if (!anZeilen || !woerter || !woerter.length || !seitenBreiteCss) {
      for (let y = hoehe; y < bigH; y += hoehe) grenzen.push(y);
      grenzen.push(bigH);
      return grenzen;
    }

    const bd = baender(woerter, bloecke, pxW / seitenBreiteCss);
    const tol = hoehe * 0.12;
    let letzte = 0;
    // Nach oben gezogene Schnitte ergeben mehr Seiten als das feste Raster
    // vorsah; eine Zaehlschleife ueber das Raster wuerde den Rest abschneiden.
    // Die 5 Prozent Spiel verhindern eine Schnipselseite am Ende: ragt der
    // Rest nur knapp ueber eine Seitenhoehe hinaus, ist die minimal groessere
    // letzte Seite beim Druck unsichtbar, ein 200-px-Schnipsel dagegen nicht.
    while (bigH - letzte > hoehe * 1.05) {
      const ideal = letzte + hoehe;
      let beste = null;
      for (let k = 0; k < bd.length - 1; k++) {
        const mitte = (bd[k][1] + bd[k + 1][0]) / 2;
        if (bd[k + 1][0] <= bd[k][1]) continue;
        if (mitte >= ideal - tol && mitte <= ideal) beste = mitte;
      }
      // Faellt der Idealschnitt ohnehin in freien Raum, bleibt er stehen.
      if (beste === null && !bd.some(b => b[0] < ideal && ideal < b[1])) beste = ideal;
      let neu = beste === null ? ideal : beste;
      // Notbremse: eine Seite, die dadurch auf ein Drittel schrumpft, kostet
      // mehr Papier als der Schnitt Schaden anrichtet.
      if (neu - letzte < hoehe * 0.35) neu = ideal;
      neu = Math.round(neu);
      if (neu <= letzte || neu >= bigH) break;
      grenzen.push(neu);
      letzte = neu;
    }
    grenzen.push(bigH);
    return grenzen;
  }

  /* Auf den gewaehlten Bereich zuschneiden.
   *
   * Erst hier, nicht schon beim Aufnehmen: Das Zusammensetzen der Abschnitte,
   * die Behandlung der Nebenbereiche und die Skalierung sind fuer alle
   * Aufnahmearten dieselben. Ein eigener Zweig weiter oben waere ein zweiter
   * Ort fuer dieselben Fehler.
   *
   * Die Auswahl kam in CSS-Pixeln aus der Seite; das Bild liegt in
   * Geraetepixeln vor. Der Faktor ist derselbe, mit dem auch die Abschnitte
   * gezeichnet wurden.
   */
  if (settings.region) {
    const r = settings.region;
    // dprY ist derselbe Faktor, mit dem die Abschnitte ins Gesamtbild gezeichnet
    // wurden — CSS-Pixel der Seite zu Bildpunkten der Aufnahme.
    const f = dprY || (r.dpr || 1);
    const zx = Math.max(0, Math.round(r.x * f));
    const zy = Math.max(0, Math.round(r.y * f));
    const zw = Math.max(1, Math.min(Math.round(r.w * f), big.width - zx));
    const zh = Math.max(1, Math.min(Math.round(r.h * f), big.height - zy));
    const zu = document.createElement("canvas");
    zu.width = zw; zu.height = zh;
    zu.getContext("2d").drawImage(big, zx, zy, zw, zh, 0, 0, zw, zh);
    big = zu;
    // pxW und bigH beschreiben ab hier den Ausschnitt. Wurde nur big getauscht
    // und pxW stehen gelassen, las der Kachelcode mit der alten Breite aus der
    // neuen Flaeche: das Ergebnis waren waagrechte Streifen und ein senkrecht
    // gestauchtes Bild — gemeldet am 03.08.2026 an einer Doku-Seite.
    pxW = zw;
    bigH = zh;
    log("Auf Bereich zugeschnitten:", zx, zy, zw, zh, "Faktor", f.toFixed(2));

    // Textebene mitnehmen statt verwerfen. Die Wortkoordinaten stehen in
    // CSS-Pixeln des Dokuments; hier werden sie um den Ausschnitt versetzt und
    // alles ausserhalb faellt weg. Ein Bild ohne Text waere fuer den Zweck der
    // Erweiterung — Belege, OCR, Sprachmodelle — der halbe Nutzen.
    if (textWoerter && textWoerter.length && textSeiteBreite) {
      const versatzX = zx / f, versatzY = zy / f;
      const breiteCss = zw / f, hoeheCss = zh / f;
      const drin = [];
      for (const w of textWoerter) {
        const x = w.x - versatzX, y = w.y - versatzY;
        if (x + w.w < 0 || y + w.h < 0 || x > breiteCss || y > hoeheCss) continue;
        drin.push({ ...w, x, y });
      }
      log("Textebene beschnitten:", textWoerter.length, "->", drin.length, "Woerter");
      textWoerter = drin.length ? drin : null;
      textSeiteBreite = breiteCss;
    }
  }

  const pages = [];
  // Einmal fuer das ganze Bild entscheiden, damit alle Kacheln und alle
  // Seiten dieselbe Polaritaet bekommen.
  const umkehrenGanz = sollUmkehren(big, settings.bildModus, settings.hellerDruck !== false);
  if (settings.singlePagePdf) {
    const tilePx = Math.max(800, Math.min(8000, effectiveTilePx));
    if (bigH <= tilePx) {
      const bild = await canvasToBildBytes(big, settings.jpegQuality, settings.bildModus, umkehrenGanz);
      pages.push({ bytes: bild.bytes, filter: bild.filter, kanaele: bild.kanaele,
                   bits: bild.bits, widthPx: pxW, heightPx: bigH });
      log("Single-page PDF: 1 page, 1 tile,", bild.bytes.length, "bytes", bild.filter);
    } else {
      const tasks = [];
      for (let y = 0; y < bigH; y += tilePx) {
        const h = Math.min(tilePx, bigH - y);
        const slice = document.createElement("canvas");
        slice.width = pxW;
        slice.height = h;
        slice.getContext("2d").drawImage(big, 0, y, pxW, h, 0, 0, pxW, h);
        tasks.push(
          canvasToBildBytes(slice, settings.jpegQuality, settings.bildModus, umkehrenGanz).then(b => ({
            hintergrund: seitenHintergrund(slice, settings.bildModus, umkehrenGanz),
            bytes: b.bytes, filter: b.filter, kanaele: b.kanaele, bits: b.bits,
            xPx: 0, yPx: y, wPx: pxW, hPx: h
          }))
        );
      }
      const tiles = await Promise.all(tasks);
      const totalBytes = tiles.reduce((s, t) => s + t.bytes.length, 0);
      const gespart = tiles.filter(t => t.filter === "FlateDecode").length;
      pages.push({ widthPx: pxW, heightPx: bigH, tiles });
      log("Single-page PDF: 1 page,", tiles.length, "tiles, tilePx=", tilePx,
          "total=", totalBytes, "bytes;", gespart, "davon verlustfrei");
    }
  } else {
    /* Die Seitenhoehe.
     *
     * Steht ein Verhaeltnis fest (Querformat, Letter), ergibt es sich aus der
     * Aufnahmebreite — nur so stimmt die Form des Blattes. Sonst gilt die
     * eingestellte feste Hoehe. */
    const sliceH = settings.pageVerhaeltnis
      ? Math.max(400, Math.min(8000, Math.round(pxW * settings.pageVerhaeltnis)))
      : Math.max(400, Math.min(8000, settings.pageHeightPx || 2400));
    // Schnittstellen bestimmen. Ohne Wortgeometrie bleibt es beim festen
    // Raster — dann sind die Grenzen genau die Vielfachen von sliceH.
    const grenzen = umbruchstellen(
      textWoerter, textBloecke, textSeiteBreite, pxW, bigH,
      settings.pageFormat === "a4" ? null : sliceH,
      settings.breakAtLines !== false
    );
    const tasks = [];
    for (let i = 0; i < grenzen.length - 1; i++) {
      const y = grenzen[i];
      const h = grenzen[i + 1] - y;
      const slice = document.createElement("canvas");
      slice.width = pxW;
      slice.height = h;
      slice.getContext("2d").drawImage(big, 0, y, pxW, h, 0, 0, pxW, h);
      // yPx merkt sich, wo diese Seite im Gesamtbild beginnt. Ohne diese
      // Angabe laesst sich die Textebene den Seiten nicht zuordnen.
      tasks.push(canvasToBildBytes(slice, settings.jpegQuality, settings.bildModus, umkehrenGanz).then(b => ({
        hintergrund: seitenHintergrund(slice, settings.bildModus, umkehrenGanz),
        bytes: b.bytes, filter: b.filter, kanaele: b.kanaele, bits: b.bits,
        widthPx: pxW, heightPx: h, yPx: y
      })));
    }
    const results = await Promise.all(tasks);
    pages.push(...results);
    log("Multi-page PDF:", pages.length, "pages, format=",
        settings.pageFormat === "a4" ? "A4" : sliceH + "px",
        "breakAtLines=", settings.breakAtLines !== false);
  }

  if (pages.length === 0) throw new Error("Keine Seiten erzeugt");

  // Vorschaubild fuer die Ergebnisseite: die ganze Seite auf Anzeigebreite
  // verkleinert. Bewusst ein eigenes Bild und nicht das PDF in einem Rahmen -
  // ob der eingebaute Betrachter dort etwas anzeigt, haengt am Geraet, und wenn
  // er es nicht tut, bleibt eine leere Flaeche stehen. Ein Bild erscheint immer.
  try {
    const vorschauBytes = await baueVorschaubild(big, 720);
    const vorschauBlob = new Blob([vorschauBytes], { type: "image/jpeg" });
    _lastPreviewUrl = URL.createObjectURL(vorschauBlob);
  } catch (e) {
    log("Vorschaubild fehlgeschlagen:", e && e.message);
    _lastPreviewUrl = null;
  }

  // Herkunftsangaben: Adresse, Zeitpunkt und Pruefsumme. Die Metadaten stehen
  // immer im PDF, die sichtbare Zeile nur wenn eingeschaltet.
  let herkunft = null;
  try {
    herkunft = {
      url: tab.url || "",
      capturedAt: new Date(),
      sha256: await bilddatenPruefsumme(pages),
      footer: !!settings.provenanceFooter,
    };
    // Zeitanker nur auf ausdruecklichen Wunsch. Faellt er aus — kein Netz,
    // Dienst nicht erreichbar — wird die Aufnahme trotzdem gespeichert, nur
    // ohne Anker. Eine fehlende Untergrenze ist ein Verlust an Nachweis, kein
    // Grund, dem Nutzer die Aufnahme zu verweigern.
    if (settings.timeAnchor && typeof PageShotZeitanker !== "undefined") {
      try {
        const anker = await PageShotZeitanker.holen();
        herkunft.anchor = anker;
        herkunft.stamp = await PageShotZeitanker.stempeln(
          herkunft.sha256,
          { url: herkunft.url, erfasst: herkunft.capturedAt.toISOString() },
          anker
        );
        log("Zeitanker: Runde", anker.runde, "via", anker.quelle);
      } catch (e) {
        log("Zeitanker nicht verfuegbar:", e && e.message);
      }
    }
  } catch (e) {
    log("Pruefsumme fehlgeschlagen:", e && e.message);
  }

  const pdfBytes = PageShotPdf.buildPdf(pages, {
    dpi: 144,
    title: tab.title || "",
    version: (browser.runtime.getManifest() || {}).version || "",
    provenance: herkunft,
    textLayer: textWoerter,
    textLayerPageWidth: textSeiteBreite,
    source: quelle,
    /* Die Verweise gehen jetzt IN das PDF, nicht nur als Datei daneben.
     * Bis dahin war das fertige PDF ein Bild: Was wie ein Verweis aussah, war
     * einer gewesen. Die Lage jedes Verweises lag die ganze Zeit vor — sie
     * wurde nur nie eingetragen.
     *
     * Die eigene Bezugsbreite wird mitgegeben und nicht von der Textebene
     * geliehen: Waere die Textebene einmal abgeschaltet, stuende dort 0, und
     * die Verweise saessen um den Bildmassstab verschoben. */
    links: (linkKarte && linkKarte.links) || null,
    linksPageWidth: (linkKarte && linkKarte.seite && linkKarte.seite.w) || 0,
    /* Bei "Aufnahme fuer Druck" bekommt das PDF echte Blattmasse — sonst
     * folgt die Seite dem Bild, und der Drucker muss eine Bahn von einem
     * Meter auf ein Blatt zwingen. */
    blattPt: settings.blattPt || null,
    randPt: settings.randPt || 0,
    /* Damit im PDF steht, dass die Zitationsdatei danebenliegt — und ein
     * Sprachmodell, dem nur der Pfad des PDF vorliegt, sie findet. Nur wenn
     * sie auch wirklich erzeugt wird; ein Wegweiser ins Leere waere
     * schlechter als keiner. */
    zitatBeilage: settings.sourceMetadata !== false && settings.zitatDatei !== false,
  });

  /* Fuer den Dateinamen denselben Titel nehmen wie fuer die
   * Dokumenteigenschaften: den aus den Verlagsangaben der Seite, wenn es ihn
   * gibt. Der Fenstertitel traegt fast immer Zusaetze mit - "… - PubMed",
   * "… | Zeitschrift" -, die im Dateinamen nur Platz kosten und bei der
   * Laengengrenze den eigentlichen Titel abschneiden. */
  const baseTitle = sanitizeFilename(
    (quelle && quelle.titel) || tab.title || "page", settings.titleMaxLen);
  const site = siteFromUrl(tab.url);
  const stamp = nowStamp();
  const n = await nextCounter();

  const filename = (settings.filenameTemplate || "{title}_{site}_{date}_{time}")
    .replace("{title}", baseTitle)
    .replace("{site}", site)
    .replace("{date}", stamp.date)
    .replace("{time}", stamp.time)
    .replace("{timesec}", stamp.timeSec)
    .replace("{n}", n) + ".pdf";

  const subfolder = (settings.subfolder || "").replace(/^\/+|\/+$/g, "");
  const relPath = subfolder ? `${subfolder}/${filename}` : filename;

  const pdfBlob = new Blob([pdfBytes], { type: "application/pdf" });
  const url = URL.createObjectURL(pdfBlob);
  // Merken, damit ein Tippen auf die Fertig-Meldung das PDF anzeigen kann.
  // Freigegeben wird sie beim Start der naechsten Aufnahme (runOnActiveTab).
  _lastPdfUrl = url;
  _lastPages = pages.length;
  _lastSaved = false;
  const platformForSave = await getPlatform();

  // Keine Zwischen-Notification "Speichere PDF ..." mehr — User bekommt
  // direkt das Endergebnis (Datei gespeichert ODER im Browser geoeffnet).

  try {
    const p = await getPlatform();
    // ROBUSTE 3-STUFEN-SAVE-STRATEGIE fuer Firefox for Android.
    // Beobachtung auf Samsung S24 (One UI 6 mit SAF): downloads.download()
    // kann die Promise NIE resolven oder rejecten — der await blockt still
    // ewig, User sieht "Speichere PDF" und nichts passiert.
    //
    // Strategie:
    //   Attempt 1: download mit Sub-Ordner + Timeout 5s
    //   Attempt 2: download ohne Sub-Ordner (Root Download/) + Timeout 5s
    //   Attempt 3: browser.tabs.create(blob-url) — oeffnet PDF im Firefox-Viewer,
    //              damit der User die Datei ueber das Firefox-Download-Icon manuell
    //              speichern kann. NIE ohne Feedback dastehen.
    let id = null;
    /* Auf Android gibt es keinen Unterordner - dort legt die Seite die Datei
     * unmittelbar in die Ablage. Stand hier relPath, nannte die Meldung einen
     * Pfad ("Full Page PDF Snap/..."), den es gar nicht gab. */
    let usedFilename = p.isAndroid ? filename : relPath;
    let saveMethod = "download-subfolder";
    /* Auf Android gibt es keine Vorgangskennung - dort legt die Seite selbst ab.
     * Ohne dieses Merkmal liefe der Erfolgsfall in den Fehlerzweig, weil der
     * nur auf "id === null" schaut. */
    let gespeichertImTab = false;

    const withTimeout = (promise, ms, tag) => Promise.race([
      promise,
      new Promise((_, rej) => setTimeout(() => rej(new Error("TIMEOUT_" + tag + "_" + ms + "ms")), ms))
    ]);

    /* Auf Android geht das PDF direkt in einen Tab.
     *
     * Bisher liefen dort zuerst zwei Download-Versuche mit je fuenf Sekunden
     * Wartezeit, bevor der Tab-Weg griff. Beide scheitern auf dem Telefon
     * regelmaessig - und jeder Fehlschlag erzeugte eine Meldung, bevor die
     * eigentliche Erfolgsmeldung kam. In der Leiste standen dann drei
     * Benachrichtigungen fuer einen Vorgang, zwei davon Fehler.
     *
     * Der Tab ist auf dem Telefon ohnehin das Ziel: Dort laesst sich das PDF
     * ansehen und mit einem Tippen herunterladen. Also gleich dorthin, ohne
     * Umweg und ohne zehn Sekunden Wartezeit.
     */
    if (p.isAndroid) {
      /* Auf Android aus der Seite heraus ablegen, nicht ueber die
       * Download-Schnittstelle: Die gibt es dort seit Firefox 79 nicht mehr
       * (MDN-Kompatibilitaetsdaten, version_removed 79). Einzelheiten bei
       * speichereImTab(). Es entsteht keine Vorgangskennung - den Download
       * fuehrt der Browser selbst -, deshalb merkt sich der Ablauf den Erfolg
       * in gespeichertImTab statt an einer Nummer.
       *
       * Der Grund eines Fehlschlags wird festgehalten und dem Nutzer gezeigt.
       * Ohne das blieb ueber mehrere Fassungen unklar, woran es lag: An das
       * Protokoll kommt auf dem Telefon niemand heran. */
      try {
        await speichereImTab(tab && tab.id, pdfBytes, filename);
        gespeichertImTab = true;
        id = null;
        log("Android: im Reiter abgelegt:", filename);
      } catch (e1) {
        _letzterDownloadFehler = (e1 && e1.message) || String(e1);
        log("Android: Ablegen fehlgeschlagen:", _letzterDownloadFehler);
        id = null;
        gespeichertImTab = false;
      }
    } else {
    // Attempt 1 — mit Subfolder
    try {
      id = await withTimeout(browser.downloads.download({
        url,
        filename: relPath,
        saveAs: !!settings.saveAs,
        conflictAction: "uniquify"
      }), 30000, "A1");
      log("Save A1 OK:", id, relPath);
    } catch (e1) {
      log("Save A1 failed:", e1.message);
      id = null;
    }
    }
    // Der frueher hier stehende zweite Download-Versuch ohne Unterordner
    // entfaellt: Er galt nur fuer Android, und dort wird gar nicht mehr
    // heruntergeladen.

    /* Schlaegt auch das Anstossen fehl, gibt es keinen Ersatzweg mehr.
     *
     * Bis 2.32.1 oeffnete sich hier die Ergebnisseite mit den Schaltflaechen
     * "Herunterladen" und "Weiterleiten". Sie war als Rettung gedacht, wurde
     * aber zur eigenen Fehlerquelle: ein Reiter, den niemand wollte, mit
     * Schaltflaechen, die nicht taten, was sie versprachen. Gewuenscht ist das
     * Einfache - Aufnahme, Download, fertig.
     *
     * Also nur noch eine Meldung, und darin der Grund. Wer ihn liest, weiss
     * woran es lag; das ist mehr wert als ein Reiter, der Betrieb vortaeuscht. */
    if (id === null && p.isAndroid && !gespeichertImTab) {
      try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) { /* egal */ }
      const grund = _letzterDownloadFehler ? " (" + _letzterDownloadFehler + ")" : "";
      notifyError((browser.i18n.getMessage("androidDownloadFehler")
        || "The PDF could not be saved.") + grund);
      log("Android: Ablegen nicht zustande gekommen -", _letzterDownloadFehler);
      /* Nicht zusaetzlich werfen. Der obere Fehlerzweig meldete sonst noch
       * einmal "Die Aufnahme konnte nicht abgeschlossen werden" - am 07.08.2026
       * standen dadurch drei Meldungen fuer einen Vorgang in der Leiste, zwei
       * davon sagten dasselbe. Die Meldung oben nennt den Grund, das genuegt. */
      return { ok: false, downloadId: null, filename: usedFilename,
               pages: pages.length, segments: segments.length,
               method: "android-inline", fehler: _letzterDownloadFehler };
    }

    log("Download started", id, usedFilename, "method=" + saveMethod, "pages=", pages.length);

    const platform = await getPlatform();

    /* Auf das Fertigwerden warten kann nur, wo es eine Vorgangskennung gibt.
     * Auf Android legt die Seite selbst ab - dort ist mit dem Klick auf den
     * Anker alles getan, und waitForDownloadComplete(null) liefe ins Leere. */
    let downloadComplete = true;
    if (!gespeichertImTab) {
      const waitMs = platform.isAndroid ? 8000 : 30000;
      try { await waitForDownloadComplete(id, waitMs); }
      catch (e) { log("download wait:", e.message); downloadComplete = false; }
    }

    // RIS-Datei neben das PDF legen.
    //
    // Im PDF steckt sie bereits als Anhang, aber dort findet sie niemand: Es
    // braucht die Anlagen-Ansicht des Betrachters oder ein Werkzeug auf der
    // Kommandozeile. Eine Datei neben dem PDF laesst sich per Doppelklick in
    // Citavi oder Zotero ziehen — das ist der Weg, den die Funktion meint.
    /* Was tatsaechlich danebengelegt wurde — und was nicht.
     *
     * Bis 2.35.5 stand das nur im Protokoll. Wer die Zitation eingeschaltet
     * hatte und keine Datei fand, konnte nicht wissen, ob sie nie erzeugt
     * wurde, ob der Download scheiterte oder ob die Seite nichts hergab.
     * Gemeldet am 18.08.2026 mit genau dieser Frage. Jetzt sagt es die
     * Fertigmeldung. */
    const beilagen = [];
    const beilagenFehler = [];

    /* Die Beilagen — ueber EINE Stelle, nicht zweimal geschrieben.
     *
     * Hier stand bis 2.35.8 ein eigener Block, der dasselbe tat wie
     * belegeAblegen() — und dabei zwei Konstruktionsfehler mitschleppte, die
     * genau erklaeren, warum bei eingeschalteter Zitation keine .txt im
     * Ordner lag:
     *
     *   1. Die Zitationsdatei stand INNERHALB des try-Blocks des RIS-Satzes.
     *      Scheiterte der RIS-Download aus irgendeinem Grund, entstand auch
     *      die Zitationsdatei nicht — obwohl sie mit dem RIS-Satz nichts zu
     *      tun hat.
     *   2. Beide hingen an "settings.risSidecar !== false". Wer die RIS-Datei
     *      nicht wollte, verlor damit auch die Zitationsdatei.
     *
     * belegeAblegen legt jede Beilage einzeln ab, jede mit eigenem Fangnetz:
     * Was scheitert, reisst die anderen nicht mit. */
    /* Die Ersatzangabe steht hier noch einmal — unmittelbar vor dem Ablegen.
     *
     * Sie wird zwar schon beim Erheben gebildet, aber nur INNERHALB des
     * Zweigs, der die Seite befragt. Bricht dort etwas ab, bevor er erreicht
     * wird, bleibt quelle null, und dann entfiel bisher alles: keine
     * Zitationsdatei, kein RIS-Satz, und der Dateiname fiel auf den
     * Reitertitel zurueck. Genau dieses Bild — "Quickstart_..." ohne jede
     * Beilage — wurde am 18.08.2026 mehrfach gemeldet.
     *
     * Zwei Zeilen doppelt sind hier der Preis dafuer, dass die Beilagen nicht
     * mehr davon abhaengen, welchen Weg die Aufnahme genommen hat. */
    if (!p.isAndroid && settings.sourceMetadata !== false && !quelle) {
      const jetzt = new Date();
      /* Den Titel aus der SEITE holen, nicht aus dem Reiter.
       *
       * tab.title traegt bei Seiten, die ihre Unterseiten nachladen, den
       * Titel der Einstiegsseite — deshalb hiess jede Aufnahme in derselben
       * Dokumentation "Quickstart". Die schlanke Abfrage liest nur die
       * Ueberschrift und den Dokumenttitel und ueberlebt deshalb auch dann,
       * wenn die grosse Meta-Auswertung vorher nicht durchkam. */
      let seitenTitel = "";
      try {
        const t = await browser.tabs.sendMessage(tab.id, { cmd: "seitenTitel" });
        if (t && t.ok && t.titel) seitenTitel = String(t.titel).trim();
      } catch (e) { log("Titel aus der Seite nicht lesbar:", e && e.message); }
      quelle = {
        art: "Internetquelle", autoren: [],
        titel: seitenTitel || (tab.title || "").trim() || tab.url,
        url: tab.url, urlZitat: tab.url,
        abrufdatum: jetzt.toISOString().slice(0, 10),
        abrufzeit: jetzt.toISOString(),
        herkunft: "Adresse und Abrufzeitpunkt (die Seite gibt keine Angaben her)",
        vollstaendig: false,
      };
      log("Ersatzangabe vor dem Ablegen gebildet.");
    }

    /* Auch auf Android — dort ueber den Weg, den das PDF ohnehin nimmt.
     *
     * Bis 2.35.17 stand hier "!p.isAndroid": Auf dem Telefon gab es keine
     * Beilagen, weil es dort seit Firefox 79 keine Download-Schnittstelle
     * gibt. beilageAblegen() kennt aber den zweiten Weg, bei dem die Seite
     * selbst ablegt — genau den, ueber den auf Android auch das PDF geht.
     *
     * Dass dieser Weg keinen Unterordner setzen kann, faellt hier nicht ins
     * Gewicht: Auf Android gibt es ohnehin keinen, PDF und Beilagen landen
     * beide unmittelbar in der Ablage. Damit liegt auch dort alles
     * beieinander. */
    if (quelle) {
      const stamm = (p.isAndroid ? filename : relPath).replace(/\.pdf$/i, "");
      /* Der RIS-Satz steht IN der Zitationsdatei — und seit 2.35.17 auf Wunsch
       * zusaetzlich als eigene .ris daneben.
       *
       * Er war eine Zeitlang nur noch eingebettet, weil eine Beilage weniger
       * ein Download weniger ist. Das half aber gerade dort nicht, wo es
       * darauf ankommt: Citavi, Zotero und EndNote lesen kein Fliesstext-
       * Dokument. Wer die Angaben in seine Literaturverwaltung bringen will,
       * musste den Block von Hand herauskopieren. Darum jetzt beides, jedes
       * einzeln abwaehlbar. */
      const risSatz = (typeof PageShotPdf !== "undefined" && PageShotPdf.risSatz && quelle.titel)
        ? PageShotPdf.risSatz(quelle) : "";
      const ergebnis = await belegeAblegen(stamm, quelle, linkKarte, {
        url: tab.url,
        pdfDatei: filename,
        pruefsumme: (herkunft && herkunft.sha256) || "",
        version: (browser.runtime.getManifest() || {}).version || "",
        sprache: belegSprache(settings),
        tabId: tab && tab.id,
        ris: risSatz,
        /* Beide Beilagen haengen an den Quellenangaben: Ist der Schalter im
         * Menue aus, kommt gar keine mit — dann liegt nur das PDF da. Ist er
         * an, entscheidet die jeweilige Einstellung. */
        risDatei: settings.sourceMetadata !== false && settings.risDatei !== false,
        zitatDatei: settings.sourceMetadata !== false && settings.zitatDatei !== false,
        linkMap: settings.linkMap === true,
      });
      beilagen.push(...ergebnis.abgelegt);
      beilagenFehler.push(...ergebnis.gescheitert);
    }

    // Pfad in die Zwischenablage, sofern gewuenscht. Erst hier, weil der
    // vollstaendige Pfad erst nach dem Abschluss des Downloads feststeht —
    // der Browser haengt bei Namenskonflikten eine Zahl an.
    if (settings.copyPath) {
      try {
        const [eintrag] = await browser.downloads.search({ id });
        const pfad = (eintrag && eintrag.filename) || "";
        await pfadInZwischenablage(pfad, settings.copyPathFormat || "windows", tab.id);
      } catch (e) {
        log("Pfad nicht in die Zwischenablage:", e && e.message);
      }
    }

    // Zustand fuer Notification-Click merken (Tap oeffnet die letzte Datei).
    _lastDownloadId = id;
    _lastFilename = usedFilename;
    _lastFallbackTabId = null;
    _lastSaved = true;

    // Progress-Notification aufraeumen, bevor Erfolgs-Notification kommt.
    try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) { /* ignore */ }

    // ERFOLGS-FEEDBACK ZUERST — bevor downloads.open() eventuell blockiert.
    // Damit sieht der Nutzer auf Android auch dann Erfolg, wenn das Oeffnen haengt.
    if (platform.isAndroid) {
      /* Nur melden, was belegt ist.
       *
       * Bis 2.33.0 stand hier "In Downloads gespeichert: ..." - auch dann, wenn
       * gar nichts ankam. Am 07.08.2026 gemeldet: Die Benachrichtigung nannte
       * Pfad und Dateinamen, der Download-Ordner von Firefox war leer. Der
       * Grund war die entfernte Download-Schnittstelle, die weder Erfolg noch
       * Fehler meldet - der Code nahm Erfolg an, weil kein Fehler kam.
       *
       * Eine Meldung, die etwas Falsches behauptet, ist schlimmer als keine:
       * Sie kostet den Nutzer die Zeit, in der er die Datei sucht. Deshalb
       * steht hier nur noch, was tatsaechlich getan wurde - die Seite hat die
       * Datei abgelegt -, und der Dateiname dazu. */
      notifyInfo(browser.i18n.getMessage("androidGespeichert", [usedFilename])
        || ("Saved to your downloads: " + usedFilename));
    }
    /* Sagen, was danebenliegt.
     *
     * Auf dem Rechner gab es bisher gar keine Fertigmeldung — die Datei war
     * im Ordner, fertig. Wer die Zitation eingeschaltet hatte, musste
     * nachsehen, ob eine Beilage entstanden ist, und im Zweifel raten, warum
     * nicht. Eine kurze Meldung beantwortet das, ohne zu stoeren; sie
     * erscheint nur, wenn ueberhaupt Beilagen gewuenscht waren. */
    /* Sagen, was danebenliegt — und was NICHT, samt Ausweg.
     *
     * Kommt keine Beilage zustande, ist das kein Datenverlust: Die
     * Quellenangaben stecken ohnehin im PDF selbst — als RIS-Anlage, in den
     * Dokumenteigenschaften und als XMP-Satz. Nur weiss das niemand, der eine
     * .txt erwartet und keine findet. Deshalb steht der Ausweg in derselben
     * Meldung. */
    /* Die Meldung sagt IMMER, was mit der Zitation geschehen ist.
     *
     * Bis 2.35.12 erschien sie nur, wenn es eine Quelle gab — und genau der
     * Fall, in dem nichts danebenlag, blieb damit stumm. Der Nutzer sah eine
     * fehlende Datei und hatte keine Erklaerung; ich hatte keine Angabe, mit
     * der sich der Grund haette eingrenzen lassen. Eine Meldung, die schweigt,
     * wenn etwas schiefgeht, ist die unbrauchbarste von allen. */
    if (!platform.isAndroid && settings.sourceMetadata !== false) {
      if (beilagen.length) {
        const teile = [beilagen.join(" · ")];
        if (beilagenFehler.length) {
          teile.push((browser.i18n.getMessage("beilagenFehlten")
            || "not saved:") + " " + beilagenFehler.join(" "));
        }
        notifyInfo((browser.i18n.getMessage("beilagenGespeichert")
          || "Saved alongside the PDF:") + " " + teile.join(" | "));
      } else if (beilagenFehler.length) {
        notifyInfo((browser.i18n.getMessage("beilagenFehlten") || "not saved:")
          + " " + beilagenFehler.join(" | "));
      } else {
        notifyInfo(browser.i18n.getMessage("beilagenImPdf")
          || "Citation saved inside the PDF (RIS attachment + document properties).");
      }
    }

    // Kurzer Ton, wenn die Aufnahme steht. Absichtlich nach der Meldung und
    // ohne await: Er darf die Rueckgabe nicht verzoegern und nicht scheitern
    // lassen.
    fertigTon(tab && tab.id, settings, platform);

    // Originaldatei des Verlags dazulegen, wenn die Seite eine angibt.
    //
    // Das ist der einzige Vorgang der Erweiterung, der eine Verbindung
    // aufbaut, und deshalb standardmaessig aus. Geholt wird ausschliesslich
    // die Adresse, die die Seite selbst als Volltext nennt — derselbe Abruf,
    // den ein Klick auf "PDF" ausloest, mit demselben Zugang. Was hinter
    // einer Schranke liegt, bleibt dort: der Server antwortet dann mit einer
    // Fehlerseite, und die wird nicht als Volltext ausgegeben.
    if (!p.isAndroid && settings.fetchOriginal === true && quelle && quelle.dateien && quelle.dateien.length) {
      const stamm = (p.isAndroid ? filename : relPath).replace(/\.pdf$/i, "");
      for (const datei of quelle.dateien.filter(d => d.art === "pdf" || d.art === "xml")) {
        try {
          await browser.downloads.download({
            url: datei.url,
            filename: stamm + "_original." + datei.art,
            conflictAction: "uniquify",
          });
          log("Originaldatei geholt:", datei.art, datei.url);
        } catch (e) {
          // Kein Zugang, kein Netz, Schranke — kein Grund, die Aufnahme
          // scheitern zu lassen. Sie ist der Beleg, die Originaldatei Zugabe.
          log("Originaldatei nicht erreichbar:", datei.art, e && e.message);
        }
      }
    }

    if (downloadComplete) {
      // Non-blocking + Timeout — Extension darf nicht am Oeffnen haengenbleiben.
      Promise.race([
        runAfterCapture(id, settings.afterCapture),
        sleep(5000)
      ]).catch(e => log("afterCapture race:", e));
    } else {
      log("Download not complete within " + waitMs + "ms — but file is likely saved. Skipping open.");
      if (!platform.isAndroid) notifyError("Download nicht rechtzeitig fertig.");
    }

    vielleichtNachBewertungFragen();
    return { ok: true, downloadId: id, filename: relPath, pages: pages.length, segments: segments.length };
  } finally {
    // Auf Android bleibt die URL bestehen: der Nutzer tippt die Fertig-Meldung
    // u.U. erst Minuten spaeter an, und dann muss das PDF noch anzeigbar sein.
    // Freigegeben wird sie beim Start der naechsten Aufnahme.
    if (!platformForSave.isAndroid) {
      setTimeout(() => {
        try { URL.revokeObjectURL(url); } catch (_) { /* ignore */ }
        if (_lastPdfUrl === url) _lastPdfUrl = null;
      }, 60_000);
    }
  }
}

/* Verkleinert die fertige Gesamtaufnahme auf Anzeigebreite.
 *
 * Die Hoehe wird gedeckelt: Canvas-Kanten sind je nach Engine bei rund 32.000
 * Pixeln zu Ende, und darueber liefert drawImage stillschweigend eine leere
 * Flaeche statt eines Fehlers. Lieber eine abgeschnittene Vorschau als eine
 * weisse. */
const VORSCHAU_MAX_HOEHE = 16000;

async function baueVorschaubild(quelle, maxBreite) {
  const skala = Math.min(1, maxBreite / quelle.width);
  const breite = Math.max(1, Math.round(quelle.width * skala));
  const volleHoehe = Math.round(quelle.height * skala);
  const hoehe = Math.max(1, Math.min(VORSCHAU_MAX_HOEHE, volleHoehe));
  // Nur so viel aus der Quelle nehmen, wie in die gedeckelte Hoehe passt -
  // sonst wuerde die ganze Seite gestaucht statt beschnitten.
  const quellHoehe = Math.round(hoehe / skala);

  const leinwand = document.createElement("canvas");
  leinwand.width = breite;
  leinwand.height = hoehe;
  leinwand.getContext("2d").drawImage(
    quelle, 0, 0, quelle.width, quellHoehe, 0, 0, breite, hoehe);
  // Niedrigere Qualitaet als beim PDF: das Bild wird nur betrachtet, nicht
  // archiviert, und auf Android zaehlt jedes eingesparte Megabyte.
  return canvasToJpegBytes(leinwand, 0.7);
}

function waitForDownloadComplete(id, timeoutMs) {
  return new Promise((resolve, reject) => {
    const t0 = Date.now();
    const handler = (delta) => {
      if (delta.id !== id) return;
      if (delta.state && delta.state.current === "complete") {
        browser.downloads.onChanged.removeListener(handler);
        resolve();
      } else if (delta.state && delta.state.current === "interrupted") {
        browser.downloads.onChanged.removeListener(handler);
        reject(new Error("download interrupted"));
      }
    };
    browser.downloads.onChanged.addListener(handler);
    const poll = setInterval(async () => {
      try {
        const [item] = await browser.downloads.search({ id });
        if (item && item.state === "complete") {
          browser.downloads.onChanged.removeListener(handler);
          clearInterval(poll);
          resolve();
        } else if (Date.now() - t0 > timeoutMs) {
          browser.downloads.onChanged.removeListener(handler);
          clearInterval(poll);
          reject(new Error("download timeout"));
        }
      } catch (_) { /* ignore */ }
    }, 250);
  });
}

async function runAfterCapture(downloadId, mode) {
  const p = await getPlatform();
  if (p.isAndroid) {
    // Android oeffnet nichts von selbst. Die Datei ist gespeichert, die
    // Fertig-Meldung steht — angezeigt wird das PDF erst, wenn der Nutzer
    // sie antippt (siehe notifications.onClicked).
    return;
  }
  try {
    if (mode === "open" && typeof browser.downloads.open === "function") {
      await browser.downloads.open(downloadId);
    } else if (mode === "show" && typeof browser.downloads.show === "function") {
      await browser.downloads.show(downloadId);
    } else if (mode === "both") {
      if (typeof browser.downloads.show === "function") await browser.downloads.show(downloadId);
      await sleep(300);
      if (typeof browser.downloads.open === "function") await browser.downloads.open(downloadId);
    }
  } catch (e) {
    log("afterCapture error:", e);
    notifyError("Ordner/Datei konnte nicht geoeffnet werden: " + (e && e.message ? e.message : String(e)));
  }
}

let _captureInFlight = false;

async function setBadge(text, color) {
  if (!browser.action) return;
  try {
    await browser.action.setBadgeText({ text: text || "" });
    if (color && browser.action.setBadgeBackgroundColor) {
      await browser.action.setBadgeBackgroundColor({ color });
    }
  } catch (_) { /* Android ignoriert badge-color u.U. */ }
}

async function setActionTitle(text) {
  if (!browser.action || !browser.action.setTitle) return;
  try { await browser.action.setTitle({ title: text }); }
  catch (_) { /* ignore */ }
}

/* Ruhezustands-Titel des Toolbar-Knopfs.
 *
 * Das Kuerzel stand hier fest im Text und war nach dem Wechsel auf
 * Alt+Shift+P falsch. Es wird jetzt beim Browser erfragt - beansprucht der
 * die Kombination fuer sich, nennt der Tooltip erst gar keine.
 */
async function setIdleTitle() {
  let hint = "";
  try {
    const cmds = await browser.commands.getAll();
    const keys = cmds
      .filter(c => c.name.startsWith("capture-full-page") && c.shortcut)
      .map(c => c.shortcut);
    if (keys.length) hint = ` (${keys.join(" / ")})`;
  } catch (_) { /* Android kennt commands.getAll nicht */ }
  let base = "Full Page PDF Snap — save the whole page as PDF";
  try {
    base = browser.i18n.getMessage("actionTitle") || base;
  } catch (_) { /* Fallback bleibt englisch */ }
  await setActionTitle(base + hint);
}

// Firefox blockiert Content-Script-Injektion auf diesen Seiten aus Sicherheitsgruenden.
// Wir fangen das VOR dem Injection-Versuch ab, um eine klare Meldung zu geben.
const BLOCKED_HOSTS = [
  "addons.mozilla.org",
  "accounts.firefox.com",
  "support.mozilla.org",
  "install.mozilla.org"
];

/* Ein uebersetzter Text, mit deutschem Rueckfall.
 *
 * Die Meldungen unten standen bis 2.35.3 fest auf Deutsch im Quelltext,
 * obwohl es sie in allen neun Sprachen gibt — die Schluessel lagen
 * unbenutzt in den Sprachdateien. Wer die Oberflaeche auf Japanisch oder
 * Spanisch gestellt hatte, bekam trotzdem "Firefox schuetzt diese Seite".
 * Aufgefallen ist es erst beim gezielten Abgleich zwischen den vorhandenen
 * und den verwendeten Schluesseln.
 *
 * Der Rueckfall bleibt stehen: Schlaegt die Uebersetzung fehl, ist eine
 * deutsche Meldung besser als eine leere. */
function txt(schluessel, rueckfall) {
  try {
    const m = browser.i18n.getMessage(schluessel);
    if (m) return m;
  } catch (_) { /* Rueckfall */ }
  return rueckfall;
}

function isCapturable(url) {
  if (!url) return { ok: false, reason: txt("noTab", "Kein Tab geladen.") };
  if (!/^https?:|^file:/.test(url)) {
    return { ok: false, reason: txt("internalPage",
      "Interne Browser-Seite — bitte zu einer normalen Webseite wechseln (https://...).") };
  }
  try {
    const host = new URL(url).hostname;
    if (BLOCKED_HOSTS.some(h => host === h || host.endsWith("." + h))) {
      return { ok: false, reason: txt("protectedPage",
        "Der Browser schuetzt diese Seite. Bitte zu einer normalen Webseite wechseln.") };
    }
    // PDF-Direkt-Modus: schon eine PDF geoeffnet -> nicht sinnlos screenshotten,
    // sondern die Datei direkt in unseren Downloads-Ordner kopieren.
    if (/\.pdf($|\?|#)/i.test(url)) {
      return { ok: true, mode: "pdf-direct", pdfUrl: url };
    }
  } catch (_) { /* URL-parse-Fehler ignorieren */ }
  return { ok: true, mode: "capture" };
}

// PDF-Direkt-Download: URL vom bereits geoeffneten PDF direkt speichern —
// kein Content-Script, kein Screenshot-Loop, kein PDF-Build.
async function capturePdfDirect(tab, pdfUrl) {
  const settings = await getSettings();
  const platform = await getPlatform();

  const baseTitle = sanitizeFilename(tab.title || "document", settings.titleMaxLen);
  const stamp = nowStamp();
  const n = await nextCounter();

  // Filename aus URL ableiten, fallback auf Tab-Titel.
  let baseName;
  try {
    const u = new URL(pdfUrl);
    const last = u.pathname.split("/").pop() || "";
    baseName = decodeURIComponent(last.replace(/\.pdf$/i, "")) || baseTitle;
    baseName = sanitizeFilename(baseName, settings.titleMaxLen);
  } catch (_) { baseName = baseTitle; }

  const filename = `${baseName}_${stamp.date}_${stamp.time}_${n}.pdf`;
  const subfolder = (settings.subfolder || "").replace(/^\/+|\/+$/g, "");
  const relPath = subfolder ? `${subfolder}/${filename}` : filename;

  log("PDF-Direct save:", pdfUrl, "->", relPath);
  // Kein Zwischen-Notification — User bekommt direkt das Endergebnis.

  const withTimeout = (promise, ms, tag) => Promise.race([
    promise,
    new Promise((_, rej) => setTimeout(() => rej(new Error("TIMEOUT_" + tag)), ms))
  ]);

  let id = null;
  try {
    id = await withTimeout(browser.downloads.download({
      url: pdfUrl, filename: relPath, saveAs: false, conflictAction: "uniquify"
    }), platform.isAndroid ? 5000 : 30000, "PDF-A1");
  } catch (e1) { log("PDF-Direct A1 failed:", e1.message); }

  if (id === null && platform.isAndroid && subfolder) {
    try {
      id = await withTimeout(browser.downloads.download({
        url: pdfUrl, filename: filename, saveAs: false, conflictAction: "uniquify"
      }), 5000, "PDF-A2");
    } catch (e2) { log("PDF-Direct A2 failed:", e2.message); }
  }

  // Bei bereits geoeffnetem PDF ist der Tab schon offen — Firefox-Download-Symbol
  // ist direkt sichtbar. Notification kurz und hilfreich.
  if (id === null) {
    try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) {}
    notifyInfo(browser.i18n.getMessage("androidFertig")
      || "PDF ready — open it to view or download");
    throw makeUserHintError("PDF im Browser bereit — nutze das Download-Icon.");
  }

  _lastDownloadId = id;
  _lastFilename = relPath;
  _lastFallbackTabId = null;
  // Ein bereits vorliegendes PDF wird nur geladen, nicht aufgenommen - es gibt
  // also weder eine Seitenzahl noch ein Vorschaubild. Die Ergebnisseite zeigt
  // dann ihren Ersatztext samt Schaltflaeche zum Oeffnen.
  _lastSaved = id != null;
  _lastPages = 0;
  // Hier ist die Quelle das PDF selbst, keine Blob-URL — damit zeigt ein Tippen
  // dasselbe wie nach einer normalen Aufnahme: das PDF im Browser.
  _lastPdfUrl = pdfUrl;

  try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) {}
  if (platform.isAndroid) {
    notifyInfo(browser.i18n.getMessage("desktopGespeichert", [filename])
      || `Saved: ${filename}`);
  }
  return { ok: true, downloadId: id, filename: relPath, pages: null, segments: null, method: "pdf-direct" };
}

function makeUserHintError(msg) {
  const e = new Error(msg);
  e.userHint = true;
  return e;
}

async function runOnActiveTab(wahl) {
  if (_captureInFlight) {
    log("Ignoring tap — capture already in flight.");
    return { ok: false, error: "Bereits laufend" };
  }
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw makeUserHintError(txt("noTab", "Kein aktiver Tab."));
  const check = isCapturable(tab.url);
  if (!check.ok) {
    throw makeUserHintError(check.reason);
  }
  // Bereits geoeffnete PDF -> direkter Download-Zweig statt Screenshot-Pipeline.
  const useDirectPdf = check.mode === "pdf-direct";
  // Nur der sichtbare Ausschnitt? Dann entfaellt das Scrollen, alles Weitere
  // bleibt gleich: derselbe PDF-Schreiber, dieselbe Textebene, dieselbe
  // Nachweiszeile. Eine zweite Ausgabeform waere ein zweiter Ort fuer Fehler.
  // Bereich mit der Maus: die Auswahl geschieht in der Seite, bevor irgendetwas
  // aufgenommen wird. Bricht der Nutzer ab, endet der Vorgang ohne Datei und
  // ohne Fehlermeldung — ein Abbruch ist kein Fehler.
  const bereichGewuenscht = !!(wahl && wahl.region);
  // Die Auswahl geschieht VOR jeder anderen Vorbereitung: Der Nutzer soll die
  // Seite unveraendert sehen, waehrend er zieht. Erst danach wird ausgeblendet
  // und gescrollt.
  let gewaehlterBereich = null;
  if (bereichGewuenscht) {
    try {
      await ensureContentInjected(tab.id);
      const hinweis = browser.i18n.getMessage("regionHint")
                   || "Drag to select an area \u00b7 Esc cancels";
      gewaehlterBereich = await browser.tabs.sendMessage(
        tab.id, { cmd: "selectRegion", hint: hinweis });
    } catch (e) {
      log("Bereichsauswahl nicht moeglich:", e && e.message);
      return { ok: false, error: (e && e.message) || "Auswahl auf dieser Seite nicht moeglich." };
    }
    // Abbruch ist kein Fehler: keine Datei, keine Meldung, kein Fehlerzustand.
    if (!gewaehlterBereich) {
      log("Bereichsauswahl abgebrochen.");
      return { ok: true, result: { cancelled: true, pages: 0 } };
    }
  }

  _captureInFlight = true;
  // Reset der letzten Save-Ergebnisse — der naechste Tap soll den NEUEN Capture betreffen.
  _lastDownloadId = null;
  _lastFilename = null;
  _lastFallbackTabId = null;
  // Auch die PDF-URL der Vorgaenger-Aufnahme faellt hier weg. Sonst wuerde ein
  // Tippen auf eine Fehlermeldung noch das alte PDF anzeigen.
  if (_lastPdfUrl) { try { URL.revokeObjectURL(_lastPdfUrl); } catch (_) { /* ignore */ } }
  if (_lastPreviewUrl) { try { URL.revokeObjectURL(_lastPreviewUrl); } catch (_) { /* ignore */ } }
  _lastPdfUrl = null;
  _lastPreviewUrl = null;
  _lastPages = 0;
  _lastSaved = false;
  await setBadge("...", "#2563eb");
  await setActionTitle("Full Page PDF Snap — capture running …");
  // Keine Start-Notification: die einzige Meldung kommt, wenn das PDF fertig ist.
  try {
    const res = useDirectPdf
      ? await capturePdfDirect(tab, check.pdfUrl)
      /* Der Modus MUSS mit.
       *
       * Bis 2.35.4 stand hier nur "{ region: … }" — die Angabe, welche
       * Ausgabeart der Nutzer gewaehlt hat, ging genau an dieser Stelle
       * verloren. runOnActiveTab nahm sie entgegen und gab sie nicht weiter.
       *
       * Die Folge war dreifach und jedes Mal derselbe Fehler: "Aufnahme fuer
       * Druck" erzeugte weiter eine Endlosbahn, Papierformat und Ausrichtung
       * blieben wirkungslos, und der Artikel-Knopf lieferte die gewoehnliche
       * Seite — gemeldet als "es macht nur normales pdf". Alle drei Meldungen
       * hatten diese eine Ursache.
       *
       * Getestet war jedes Teilstueck fuer sich: die Blattrechnung, der
       * Vektorweg, die Artikelerkennung. Nur die Kette vom Knopf bis zur
       * Aufnahme hatte niemand nachverfolgt. */
      : await captureFullPage(tab, {
          region: gewaehlterBereich,
          modus: (wahl && wahl.modus) || null,
        });
    await setBadge("OK", "#059669");
    // Notification wird bereits aus captureFullPageInner gefeuert (vor downloads.open),
    // damit User auf Android auch dann Erfolg sieht wenn das Oeffnen haengt.
    setTimeout(() => { setBadge("", ""); }, 3000);
    return res;
  } catch (e) {
    // Progress-Notification schliessen — sonst bleibt sie neben Fehlermeldung stehen.
    try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) { /* ignore */ }
    if (e && e.userHint) {
      // Keine harten Alarm-Farben fuer harmlose Hinweise (z.B. geschuetzte Seite).
      await setBadge("", "");
      notifyHint(e.message);
    } else {
      await setBadge("!", "#b91c1c");
      setTimeout(() => { setBadge("", ""); }, 4000);
      // Dem Nutzer wird gesagt, was er tun kann - nicht, was intern schiefging.
      //
      // Am 07.08.2026 stand auf einem Telefon "can't access lexical
      // declaration 'platform' before initialization" in der Leiste. Das ist
      // fuer die Fehlersuche unverzichtbar und fuer den Nutzer wertlos: Er
      // kann daraus nichts ableiten und weiss nur, dass etwas kaputt ist.
      //
      // Der technische Wortlaut bleibt vollstaendig im Protokoll. Meldungen
      // mit userHint - geschuetzte Seite, kein Tab - haben ihren eigenen,
      // verstaendlichen Text und laufen oben durch.
      log("Aufnahme fehlgeschlagen:", e && e.stack ? e.stack : e);
      notifyError(browser.i18n.getMessage("fehlerAllgemein")
        || "The capture could not be completed. Please try again.");
    }
    // Nicht weiterwerfen — Notification hat den Nutzer bereits informiert.
    return { ok: false, error: e && e.message ? e.message : String(e) };
  } finally {
    _captureInFlight = false;
    await setIdleTitle();
  }
}

if (browser.commands && typeof browser.commands.onCommand?.addListener === "function") {
  browser.commands.onCommand.addListener(async (name) => {
    // Chrome bekommt ein zweites Kuerzel aus der Ctrl+Shift-Reihe, die dort
    // anders als in Firefox noch Luft hat. Beide Kommandos loesen dasselbe aus.
    if (!name.startsWith("capture-full-page")) return;
    try { await runOnActiveTab(); }
    catch (e) { console.error(TAG, e); log("Fehler:", e && e.stack ? e.stack : e);
      notifyError(browser.i18n.getMessage("fehlerAllgemein")
        || "The capture could not be completed. Please try again."); }
  });
}

browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.cmd === "capture") {
    runOnActiveTab({ region: !!msg.region, modus: msg.modus || null })
      .then(r => {
        // runOnActiveTab wirft nicht mehr — Fehler kommen als {ok:false,error}.
        if (r && r.ok === false) sendResponse({ ok: false, error: r.error });
        else sendResponse({ ok: true, result: r });
      })
      .catch(e => { console.error(TAG, e); sendResponse({ ok: false, error: e.message }); });
    return true;
  }

  // Stand der letzten Aufnahme fuer die Ergebnisseite.
  if (msg && msg.type === "pdfsnap:last") {
    const pfad = _lastFilename || "";
    sendResponse({
      ok: !!(_lastPdfUrl || _lastDownloadId != null),
      url: _lastPdfUrl,
      preview: _lastPreviewUrl,
      filename: pfad.split("/").pop() || pfad,
      path: pfad,
      pages: _lastPages,
      saved: _lastSaved,
      downloadId: _lastDownloadId,
      /* Die Ergebnisseite braucht die Plattform. Auf Android traegt weder eine
       * data:- noch eine blob:-URL einen Dateinamen: Wer die Vorschau antippt
       * und das PDF dann ueber den Browser sichert, bekommt "document.pdf".
       * Genau so entstand am 07.08.2026 "document(11).pdf", obwohl 2.31.18
       * bereits lief - der Fehler sass nicht mehr im Aufnahmeweg, sondern hier.
       * _platformCache steht seit dem ersten getPlatform()-Aufruf bereit; ein
       * fehlender Wert wird als "nicht Android" gewertet und aendert nichts. */
      isAndroid: !!(_platformCache && _platformCache.isAndroid),
      downloadFehler: _letzterDownloadFehler || ""
    });
    return false;
  }

  // Datei im System oeffnen. Auf Android landet der Nutzer damit in der
  // App-Auswahl und kann von dort weiterreichen - der Rueckfallweg fuer
  // Browser ohne Datei-Teilen.
  if (msg && msg.type === "pdfsnap:open") {
    oeffneLetzteDatei()
      .then(ok => sendResponse({ ok }))
      .catch(e => { log("pdfsnap:open:", e); sendResponse({ ok: false, error: e.message }); });
    return true;
  }
});

async function oeffneLetzteDatei() {
  if (_lastDownloadId != null && typeof browser.downloads.open === "function") {
    try { await browser.downloads.open(_lastDownloadId); return true; }
    catch (e) { log("downloads.open failed:", e.message); }
  }
  if (_lastDownloadId != null && typeof browser.downloads.show === "function") {
    try { await browser.downloads.show(_lastDownloadId); return true; }
    catch (e) { log("downloads.show failed:", e.message); }
  }
  if (_lastPdfUrl) {
    try {
      const tab = await browser.tabs.create({ url: _lastPdfUrl, active: true });
      _lastFallbackTabId = tab && tab.id;
      return true;
    } catch (e) { log("tab fallback failed:", e.message); }
  }
  return false;
}

/* Oeffnet die Ergebnisseite - Vorschau, Herunterladen, Weiterleiten.
 * Ein bereits offener Reiter wird wiederverwendet, damit nicht bei jeder
 * Aufnahme ein weiterer aufgeht. */
async function zeigeErgebnisseite() {
  const seite = browser.runtime.getURL("result.html");
  try {
    const offen = await browser.tabs.query({ url: seite });
    if (offen && offen.length) {
      await browser.tabs.update(offen[0].id, { active: true, url: seite });
      _lastFallbackTabId = offen[0].id;
      return true;
    }
  } catch (_) { /* tabs.query mit url braucht keine Extra-Rechte fuer eigene Seiten */ }
  const tab = await browser.tabs.create({ url: seite, active: true });
  _lastFallbackTabId = tab && tab.id;
  return true;
}

// Android: kein Popup — Icon-Tap loest direkten Capture aus.
// Setzt action.popup zur Laufzeit auf leer, damit onClicked feuert
// statt popup.html zu laden. Desktop bleibt unveraendert.
browser.action.onClicked.addListener(async () => {
  try { await runOnActiveTab(); }
  catch (e) { console.error(TAG, e); log("Fehler:", e && e.stack ? e.stack : e);
      notifyError(browser.i18n.getMessage("fehlerAllgemein")
        || "The capture could not be completed. Please try again."); }
});

/* Das Menue auf Android abschalten - und zwar frueh genug.
 *
 * Bis 2.33.1 geschah das nur beim Laden des Hintergrundskripts. Das laedt in
 * Firefox aber erst, wenn ein Ereignis es weckt - nach einem Neustart des
 * Browsers also unter Umstaenden erst durch den Tastendruck selbst. Dann stand
 * das Menue schon offen, und auf dem Telefon oeffnet es als eigener Reiter. Am
 * 07.08.2026 so beobachtet: nach jedem Neustart eine zusaetzliche Ebene mit
 * einem blauen Knopf, die niemand wollte.
 *
 * onStartup weckt das Skript beim Start des Browsers, onInstalled nach
 * Installation und Aktualisierung. Zusammen mit dem Aufruf beim Laden deckt das
 * alle drei Wege ab, auf denen die Erweiterung in Gang kommt. */
async function popupAufAndroidAbschalten() {
  try {
    const p = await getPlatform();
    if (!p.isAndroid) return;
    await browser.action.setPopup({ popup: "" });
    log("Android erkannt - Menue abgeschaltet, Aufnahme laeuft direkt.");
  } catch (e) { log("setPopup fehlgeschlagen:", e); }
}

popupAufAndroidAbschalten();
if (browser.runtime.onStartup) {
  browser.runtime.onStartup.addListener(popupAufAndroidAbschalten);
}
if (browser.runtime.onInstalled) {
  browser.runtime.onInstalled.addListener(popupAufAndroidAbschalten);
}

// Notification-Tap oeffnet die zuletzt gespeicherte Datei. Wichtig auf Android,
// wo Firefox' downloads.open() sonst still haengen kann.
// Wenn noch nichts fertig ist: Feedback geben statt still zu bleiben.
if (browser.notifications && browser.notifications.onClicked) {
  browser.notifications.onClicked.addListener(async (notifId) => {
    if (notifId === "pdfsnap-review") {
      try { await browser.tabs.create({ url: BEWERTUNG_URL, active: true }); }
      catch (e) { log("review tab failed:", e); }
      return;
    }
    if (_captureInFlight && _lastDownloadId == null && _lastFallbackTabId == null) {
      try {
        browser.notifications.create("pdfsnap-progress", {
          type: "basic",
          iconUrl: browser.runtime.getURL("icons/icon-48.png"),
          title: "Full Page PDF Snap",
          message: browser.i18n.getMessage("busy") || "Aufnahme laeuft noch — bitte warten. Bei Fehler wird eine Meldung angezeigt."
        });
      } catch (_) { /* ignore */ }
      return;
    }
    // Notfall-Fallback: PDF wurde als Tab geoeffnet — Tab in den Vordergrund.
    if (_lastFallbackTabId != null) {
      try { await browser.tabs.update(_lastFallbackTabId, { active: true }); return; }
      catch (_) { /* Tab wurde vom User geschlossen — sag Bescheid */ }
      notifyHint("PDF-Tab wurde geschlossen. Starte eine neue Aufnahme.");
      _lastFallbackTabId = null;
      return;
    }
    /* Auf Android die heruntergeladene Datei oeffnen, nicht die Ergebnisseite.
     * Dort ist die Aufnahme mit dem Tippen abgeschlossen - sie liegt in der
     * Ablage. Wer die Meldung antippt, will sie sehen, nicht noch einmal
     * Schaltflaechen. Aus der geoeffneten Datei heraus bietet Android sein
     * eigenes Teilen-Menue an. */
    if (_lastDownloadId != null && _platformCache && _platformCache.isAndroid) {
      try { await browser.downloads.open(_lastDownloadId); return; }
      catch (e) { log("downloads.open:", e && e.message); }
    }
    // Regelfall am Rechner: die Ergebnisseite zeigen. Sie enthaelt die Vorschau
    // und darueber die beiden Schaltflaechen - Herunterladen und Weiterleiten.
    // Der nackte Betrachter bot nur das Herunterladen; das Weiterreichen an
    // Mail oder Messenger war von dort nicht erreichbar.
    if (_lastPdfUrl || _lastDownloadId != null) {
      try {
        await zeigeErgebnisseite();
        log("Ergebnisseite geoeffnet:", _lastFilename);
        return;
      } catch (e) {
        log("result page open failed:", e);
      }
    }
    if (_lastDownloadId == null) {
      notifyHint("Noch keine Aufnahme fertig. Tippe zuerst auf das Erweiterungs-Symbol.");
      return;
    }
    // Rueckfallebene, wenn die Blob-URL nicht mehr lebt (z.B. weil der
    // Hintergrund-Prozess zwischenzeitlich beendet wurde).
    try {
      if (typeof browser.downloads.open === "function") {
        await browser.downloads.open(_lastDownloadId);
        log("Opened via notification click:", _lastFilename);
      } else {
        notifyHint("Datei: " + _lastFilename + " (im Downloads-Ordner)");
      }
    } catch (e) {
      log("notification click open error:", e);
      notifyError("Konnte PDF nicht oeffnen. Datei: " + _lastFilename);
    }
  });
}

/* Fragt genau EINMAL nach einer Bewertung, fruehestens nach BEWERTUNG_AB
 * erfolgreichen Aufnahmen. Danach nie wieder — der Merker bleibt gesetzt,
 * auch wenn der Nutzer nicht reagiert. Abschaltbar in den Einstellungen.
 *
 * Bewusst eine Notification und kein Popup: Ein Dialog mitten im Ablauf waere
 * genau die Sorte Unterbrechung, die diese Erweiterung sonst vermeidet. */
async function vielleichtNachBewertungFragen() {
  try {
    const s = await browser.storage.local.get({
      counter: 0, askedForReview: false, reviewPromptOff: false
    });
    if (s.reviewPromptOff || s.askedForReview) return;
    if ((s.counter || 0) < BEWERTUNG_AB) return;
    await browser.storage.local.set({ askedForReview: true });
    await sleep(2500);                       // nicht ueber die Fertig-Meldung legen
    const id = "pdfsnap-review";
    _reviewNotifId = id;
    browser.notifications?.create(id, {
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: "Full Page PDF Snap",
      message: `Schon ${s.counter} Seiten aufgenommen. Wenn es taugt: eine kurze Bewertung hilft anderen beim Finden. Tippen zum Oeffnen — sonst einfach wegwischen.`
    });
  } catch (_) { /* Benachrichtigungen ggf. nicht erlaubt — dann eben nicht */ }
}

/* Den Fertig-Ton anstossen.
 *
 * Laeuft im Inhaltsskript des aufgenommenen Tabs - der Hintergrunddienst hat
 * in Chrome MV3 keinen AudioContext. Schlaegt es fehl (Tab geschlossen, Seite
 * gewechselt, Skript nicht geladen), passiert nichts weiter: Ein fehlender
 * Ton darf eine gelungene Aufnahme nicht zu einem Fehler machen.
 *
 * Standardmaessig nur auf Android. Am Rechner sieht man die Benachrichtigung
 * ohnehin, und ein Ton aus dem Browser waere dort eher stoerend - abschalten
 * laesst er sich in beiden Faellen.
 */
/* Den Anzeige-Tab schliessen, sobald der Nutzer das PDF heruntergeladen hat.
 *
 * Auf Android wird das PDF nicht gespeichert, sondern in einem Tab geoeffnet -
 * dort laesst es sich ansehen und mit einem Tippen herunterladen. Danach hat
 * der Tab seinen Zweck erfuellt und steht nur noch im Weg.
 *
 * Erkannt wird das am Download-Ereignis: Sobald ein Download abgeschlossen
 * ist, waehrend ein Anzeige-Tab offen steht, wird dieser geschlossen. Der
 * Abgleich ueber die Adresse waere genauer, aber Firefox liefert bei einem
 * blob: aus einer Erweiterung nicht immer eine, die sich vergleichen laesst.
 * Ein zeitlicher Zusammenhang genuegt hier: Der Tab wurde gerade fuer dieses
 * eine PDF geoeffnet.
 *
 * Scheitert das Schliessen - Tab schon weg, Berechtigung fehlt, Android
 * verhaelt sich anders -, passiert nichts weiter. Eine Fehlermeldung dafuer
 * waere sinnlos: Der Nutzer hat sein PDF, und ein offener Tab ist kein
 * Schaden.
 */
let _anzeigeTabSeit = 0;
/* Grund des letzten fehlgeschlagenen Downloads, fuer die Ergebnisseite. */
let _letzterDownloadFehler = "";

function beobachteDownloadUndSchliesse() {
  if (!browser.downloads || !browser.downloads.onChanged) return;
  browser.downloads.onChanged.addListener((delta) => {
    try {
      if (!delta || !delta.state || delta.state.current !== "complete") return;
      if (!_lastFallbackTabId) return;
      // Nur wenn der Tab fuer diese Aufnahme geoeffnet wurde. Zehn Minuten
      // sind grosszuegig - laenger schaut niemand ein PDF an, bevor er es
      // speichert, und laenger soll ein alter Verweis nicht nachwirken.
      if (_anzeigeTabSeit && Date.now() - _anzeigeTabSeit > 600000) return;
      const tabId = _lastFallbackTabId;
      _lastFallbackTabId = null;
      _anzeigeTabSeit = 0;
      browser.tabs.remove(tabId).then(
        () => log("Anzeige-Tab nach dem Herunterladen geschlossen:", tabId),
        (e) => log("Anzeige-Tab liess sich nicht schliessen:", e && e.message)
      );
    } catch (e) {
      log("Download-Beobachter:", e && e.message);
    }
  });
}
beobachteDownloadUndSchliesse();

async function fertigTon(tabId, settings, plattform) {
  try {
    const an = settings.fertigTon === true
      || (settings.fertigTon !== false && plattform && plattform.isAndroid);
    if (!an || !tabId) return;
    await browser.tabs.sendMessage(tabId, { cmd: "fertigTon" });
  } catch (e) {
    log("Fertig-Ton uebersprungen:", e && e.message);
  }
}

function notifyError(text) {
  try {
    browser.notifications?.create({
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: browser.i18n.getMessage("errTitle") || "Full Page PDF Snap — Fehler",
      message: text
    });
  } catch (_) { /* permission ggf. fehlt */ }
}

function notifyHint(text) {
  try {
    browser.notifications?.create({
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: browser.i18n.getMessage("hintTitle") || "Full Page PDF Snap — Hinweis",
      message: text
    });
  } catch (_) { /* ignore */ }
}

function notifyInfo(text) {
  try {
    browser.notifications?.create({
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: "Full Page PDF Snap",
      message: text
    });
  } catch (_) { /* permission ggf. fehlt */ }
}

const MENU_IDS = {
  capture: "ps-capture",
  sep1: "ps-sep1",
  saveAs: "ps-toggle-saveAs",
  afterShow: "ps-toggle-show",
  afterOpen: "ps-toggle-open",
  hideSticky: "ps-toggle-sticky",
  sourceMetadata: "ps-toggle-cite",
  sep2: "ps-sep2",
  scaleParent: "ps-scale",
  scale1: "ps-scale-1",
  scale125: "ps-scale-125",
  scale15: "ps-scale-15",
  scale2: "ps-scale-2",
  sep4: "ps-sep4",
  options: "ps-options"
};

async function buildMenus() {
  if (!browser.menus) return;
  const p = await getPlatform();
  if (p.isAndroid) return; // Android hat keine action-Menues
  try { await browser.menus.removeAll(); } catch (_) { /* ignore */ }
  const s = await getSettings();
  const ctx = ["action"];

  browser.menus.create({ id: MENU_IDS.capture, title: browser.i18n.getMessage("menuCapture") || "Ganze Seite als PDF speichern", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep1, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.saveAs, type: "checkbox", checked: !!s.saveAs, title: browser.i18n.getMessage("menuSaveAs") || "Speicher-Dialog jedes Mal anzeigen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.afterShow, type: "checkbox", checked: s.afterCapture === "show" || s.afterCapture === "both", title: browser.i18n.getMessage("menuShowFolder") || "Nach Save: Ordner zeigen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.afterOpen, type: "checkbox", checked: s.afterCapture === "open" || s.afterCapture === "both", title: browser.i18n.getMessage("menuOpenPdf") || "Nach Save: PDF oeffnen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.hideSticky, type: "checkbox", checked: !!s.hideSticky, title: browser.i18n.getMessage("menuHideSticky") || "Sticky/Sidebar verstecken", contexts: ctx });
  // Quellenangaben gehoeren neben das Ausblenden: beide veraendern das
  // Ergebnis sichtbar und werden je nach Seite anders gewollt.
  browser.menus.create({ id: MENU_IDS.sourceMetadata, type: "checkbox",
    checked: s.sourceMetadata !== false,
    title: browser.i18n.getMessage("popupCite") || "Quellenangaben mitschreiben",
    contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep2, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.scaleParent, title: browser.i18n.getMessage("menuQuality") || "Capture-Qualitaet", contexts: ctx });
  const scale = Number(s.captureScale || 1.0);
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale1, type: "radio", checked: scale === 1.0, title: browser.i18n.getMessage("menuScale10") || "1.0x — wie am Bildschirm", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale125, type: "radio", checked: scale === 1.25, title: browser.i18n.getMessage("menuScale125") || "1.25x — Balance", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale15, type: "radio", checked: scale === 1.5, title: browser.i18n.getMessage("menuScale15") || "1.5x — scharf", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale2, type: "radio", checked: scale === 2.0, title: browser.i18n.getMessage("menuScale20") || "2.0x — maximal", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep4, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.options, title: browser.i18n.getMessage("menuAllSettings") || "Alle Einstellungen…", contexts: ctx });
}

async function applyMenuClick(id, checked) {
  const s = await browser.storage.local.get(DEFAULTS);
  const patch = {};
  switch (id) {
    case MENU_IDS.capture:
      runOnActiveTab().catch(e => { console.error(TAG, e);
    log("Fehler:", e && e.stack ? e.stack : e);
    notifyError(browser.i18n.getMessage("fehlerAllgemein")
      || "The capture could not be completed. Please try again."); });
      return;
    case MENU_IDS.saveAs:
      patch.saveAs = !!checked; break;
    case MENU_IDS.afterShow: {
      const open = s.afterCapture === "open" || s.afterCapture === "both";
      patch.afterCapture = computeAfter(!!checked, open); break;
    }
    case MENU_IDS.afterOpen: {
      const show = s.afterCapture === "show" || s.afterCapture === "both";
      patch.afterCapture = computeAfter(show, !!checked); break;
    }
    case MENU_IDS.hideSticky:
      patch.hideSticky = !!checked; break;
    case MENU_IDS.scale1: patch.captureScale = 1.0; break;
    case MENU_IDS.scale125: patch.captureScale = 1.25; break;
    case MENU_IDS.scale15: patch.captureScale = 1.5; break;
    case MENU_IDS.scale2: patch.captureScale = 2.0; break;
    case MENU_IDS.options:
      browser.runtime.openOptionsPage(); return;
    default: return;
  }
  await browser.storage.local.set(patch);
  await buildMenus();
}

function computeAfter(show, open) {
  if (show && open) return "both";
  if (show) return "show";
  if (open) return "open";
  return "none";
}

browser.menus?.onClicked.addListener((info) => {
  applyMenuClick(info.menuItemId, info.checked).catch(e => log("menu click err:", e));
});

browser.storage.onChanged.addListener(() => { buildMenus().catch(() => {}); });

buildMenus().catch(() => {});

/* Einmalige Anpassung beim Update auf 2.3.0.
 *
 * Der Standard fuer die Capture-Skalierung war frueher 1.5 - die Seite wurde
 * also vor der Aufnahme gezoomt. Dadurch passt weniger ins Fenster, und Menues
 * oder Seitenleisten enden im PDF frueher als am Bildschirm. Neuer Standard
 * ist 1.0: das PDF zeigt die Seite so, wie sie dasteht.
 *
 * Gespeicherte Einstellungen gewinnen aber gegen den Standard. Ohne diesen
 * Schritt bliebe es bei allen Bestandsnutzern beim alten Verhalten.
 *
 * Angepasst wird ausschliesslich der Wert 1.5 - also genau der alte Standard,
 * den der Nutzer sehr wahrscheinlich nie bewusst gewaehlt hat. Wer 1.25 oder
 * 2.0 eingestellt hat, behaelt seine Wahl.
 */
// Der Titel steht im Manifest mit einer festen Kombination. Beansprucht der
// Browser sie, verspricht der Tooltip ein Kuerzel, das nicht ausloest - darum
// gleich beim Laden durch den tatsaechlichen Stand ersetzen.
setIdleTitle();

browser.runtime.onInstalled.addListener(async (details) => {
  if (details.reason !== "update") return;
  try {
    const { captureScale } = await browser.storage.local.get({ captureScale: null });
    if (captureScale === 1.5) {
      await browser.storage.local.set({ captureScale: 1.0 });
      log("Update: Capture-Skalierung von 1.5 auf 1.0 gesetzt (neuer Standard).");
    } else {
      log("Update: Capture-Skalierung unveraendert (" + captureScale + ").");
    }
  } catch (e) {
    log("Update-Anpassung fehlgeschlagen:", e);
  }

  /* Der Dateiname trug bisher nur Website, Datum, Uhrzeit und eine laufende
   * Nummer - keinen Titel. Wer die Datei spaeter wiederfindet, sieht daran
   * nicht, worum es ging. Die Voreinstellung nennt jetzt den Titel zuerst.
   * Umgestellt wird nur, wer die alte Vorlage nie angefasst hat: Ein selbst
   * gewaehltes Muster ist eine Entscheidung und wird nicht ueberschrieben. */
  try {
    const ALT = "{site}_{date}_{time}_{n}";
    const NEU = "{title}_{site}_{date}_{time}";
    const { filenameTemplate } = await browser.storage.local.get({ filenameTemplate: null });
    if (filenameTemplate === ALT) {
      await browser.storage.local.set({ filenameTemplate: NEU });
      log("Update: Dateinamen-Vorlage auf " + NEU + " gesetzt (Titel voran).");
    } else {
      log("Update: Dateinamen-Vorlage unveraendert (" + filenameTemplate + ").");
    }
    /* Mit dem Titel im Namen sind 40 Zeichen zu knapp - er brach mitten im
     * Wort ab ("...detection of g"). 60 lassen die meisten Titel ganz stehen
     * und bleiben weit unter der Laengengrenze fuer Dateinamen. Auch hier nur
     * umstellen, wer den alten Wert nie geaendert hat. */
    const { titleMaxLen } = await browser.storage.local.get({ titleMaxLen: null });
    if (titleMaxLen === 40) {
      await browser.storage.local.set({ titleMaxLen: 60 });
      log("Update: Titellaenge im Dateinamen von 40 auf 60 gesetzt.");
    }
  } catch (e) {
    log("Update: Dateinamen-Vorlage nicht angepasst:", e);
  }
});

log("Background ready.");
