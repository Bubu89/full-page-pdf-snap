/* Ergebnisseite nach einer Aufnahme.
 *
 * Zeigt das fertige PDF in der Vorschau und stellt zwei Schaltflaechen bereit:
 * Herunterladen und Weiterleiten. Vor allem fuer Android gedacht - dort ist das
 * Weiterreichen an eine andere App (Mail, Messenger, Cloud) der uebliche
 * naechste Schritt, und der eingebaute PDF-Betrachter bietet dafuer nichts an.
 *
 * Der Hintergrund liefert nur die Adresse des PDF - in Firefox eine blob:-URL,
 * in Chrome MV3 eine data:-URL (im Service Worker gibt es keine Blob-URLs).
 * Diese Seite holt sie per fetch() und baut sich daraus ihren eigenen Blob.
 * Damit ist der weitere Ablauf auf beiden Zweigen identisch, und das PDF muss
 * nicht als Rohdaten durch die Nachrichtenschicht - Chrome serialisiert die
 * naemlich als JSON, wo ein Uint8Array zu einem Objekt mit Ziffernschluesseln
 * zerfaellt.
 */
"use strict";

const $ = (id) => document.getElementById(id);
const t = (key) => {
  try { return window.PageShotI18n ? window.PageShotI18n.t(key) : ""; }
  catch (_) { return ""; }
};

let datei = null;          // File-Objekt fuer navigator.share
let blobUrl = null;        // eigene Objekt-URL fuer die Vorschau
let stand = null;          // Antwort des Hintergrunds

function setzeHinweis(text, istFehler) {
  const el = $("hinweis");
  el.textContent = text || "";
  el.classList.toggle("fehler", !!istFehler);
}

function groesse(bytes) {
  if (!bytes && bytes !== 0) return "";
  const mb = bytes / (1024 * 1024);
  if (mb >= 1) return mb.toFixed(1).replace(".", ",") + " MB";
  return Math.max(1, Math.round(bytes / 1024)) + " kB";
}

/* Kann dieser Browser eine Datei an andere Apps weiterreichen?
 *
 * Firefox kann es nicht: navigator.share gibt es dort zwar seit Version 79,
 * der files-Parameter ist aber bis heute nicht implementiert (MDN-Kompatibi-
 * litaetsdaten, Stand August 2026). canShare() meldet das ehrlich zurueck -
 * darum wird gefragt statt geraten, und der Rueckfallweg greift automatisch,
 * sobald Firefox es nachruestet. */
function kannDateiTeilen(f) {
  try { return !!(navigator.canShare && f && navigator.canShare({ files: [f] })); }
  catch (_) { return false; }
}

async function laden() {
  let antwort = null;
  try {
    antwort = await browser.runtime.sendMessage({ type: "pdfsnap:last" });
  } catch (e) {
    console.warn("[PDFSnap/result] Hintergrund nicht erreichbar:", e);
  }

  if (!antwort || !antwort.ok) {
    $("name").textContent = t("resultGone") || "No capture available.";
    $("download").disabled = true;
    $("share").disabled = true;
    document.body.classList.add("kein-embed");
    return;
  }
  stand = antwort;

  $("name").textContent = antwort.filename || "capture.pdf";

  // Das PDF selbst holen. Schlaegt das fehl, ist der Hintergrund zwischen-
  // zeitlich entladen worden - die Datei auf dem Geraet bleibt davon unberuehrt,
  // erreichbar ist sie dann nur noch ueber das System.
  let blob = null;
  if (antwort.url) {
    try {
      const antw = await fetch(antwort.url);
      blob = await antw.blob();
    } catch (e) {
      console.warn("[PDFSnap/result] PDF nicht mehr im Speicher:", e);
    }
  }

  const teile = [];
  if (antwort.pages) {
    const wort = antwort.pages === 1 ? (t("resultPage") || "page")
                                     : (t("resultPages") || "pages");
    teile.push(antwort.pages + " " + wort);
  }
  if (blob) teile.push(groesse(blob.size));

  const meta = $("meta");
  meta.textContent = teile.join(" · ");
  const zustand = document.createElement("span");
  if (antwort.saved) {
    zustand.className = "ok";
    zustand.textContent = " · " + (t("resultSaved") || "Saved");
    if (antwort.path) zustand.title = antwort.path;
  } else {
    zustand.className = "warn";
    zustand.textContent = " · " + (t("resultNotSaved") || "Not saved yet");
  }
  meta.appendChild(zustand);

  if (blob && blob.size) {
    blobUrl = URL.createObjectURL(blob);
    datei = new File([blob], antwort.filename || "capture.pdf", { type: "application/pdf" });
  }
  // Die Vorschau haengt am Bild, nicht am PDF: bei einer bereits geoeffneten
  // PDF-Seite entsteht kein Bild, die Datei ist aber vorhanden.
  if (antwort.preview) zeigeVorschau(antwort.preview);
  else document.body.classList.add("kein-embed");

  // Firefox kann Dateien nicht an Apps uebergeben. Statt eine Schaltflaeche
  // anzubieten, die dann nichts tut, steht der Weg vorher da.
  /* Wenn der Download scheiterte, gehoert der Grund hierher - sichtbar, nicht
   * nur ins Protokoll. Ohne ihn blieb ueber mehrere Fassungen unklar, warum
   * das PDF nicht in der Ablage landete, und es wurde am Symptom geraten. */
  if (antwort.downloadFehler) {
    setzeHinweis((t("resultDownloadError") || "Download failed.") +
                 " " + antwort.downloadFehler, true);
  } else if (!kannDateiTeilen(datei)) {
    setzeHinweis(t("resultShareHint") ||
      "This browser cannot hand files to other apps directly. The PDF opens in the app chooser — share it from there.");
  }
}

/* Zeigt die verkleinerte Gesamtansicht der Aufnahme.
 *
 * Ein Bild und kein eingebetteter PDF-Betrachter: ob der in einem Rahmen
 * anspringt, entscheidet das Geraet, und wenn nicht, bleibt eine leere Flaeche
 * stehen, ohne dass irgendetwas fehlschlaegt. Genau das trat beim Messen auf.
 * Das Bild meldet Erfolg und Misserfolg dagegen zuverlaessig. */
function zeigeVorschau(url) {
  const bild = $("bild");
  bild.addEventListener("error", () => document.body.classList.add("kein-embed"));
  bild.addEventListener("click", oeffneImBetrachter);
  bild.src = url;
}

/* Herunterladen ueber einen Anker mit download-Attribut.
 *
 * Auf Android ist das der einzige Weg, der den Dateinamen traegt: Weder eine
 * data:- noch eine blob:-URL fuehrt einen mit sich, und die Download-Schnitt-
 * stelle ist dort haeufig nicht verfuegbar. Ohne diesen Weg legt der Browser
 * die Datei als "document.pdf" ab, beim naechsten Mal "document(1).pdf". */
/* Woher die Bytes zum Herunterladen kommen.
 *
 * Bevorzugt der eigene Blob dieser Seite. Fehlt er, tut es die Adresse aus dem
 * Hintergrund unmittelbar: In Chrome MV3 ist das eine data:-URL, in Firefox
 * eine blob:-URL derselben Herkunft - ein Anker kann beide laden, ohne dass
 * die Seite die Daten noch einmal durch fetch() ziehen muss.
 *
 * Das ist der Punkt, an dem es am 07.08.2026 auf dem Telefon hakte: Bei einer
 * 6-MB-Aufnahme wird die data:-URL ueber acht Megabyte gross. Ging fetch()
 * dabei aus, blieben blobUrl und datei leer - und beide Schaltflaechen fielen
 * auf "pdfsnap:open" zurueck, das nur einen Reiter oeffnet. Fuer den Nutzer
 * sah es so aus, als taete "Herunterladen" etwas voellig anderes. */
function downloadQuelle() {
  return blobUrl || (stand && stand.url) || null;
}

function ankerDownload(url, name) {
  const a = document.createElement("a");
  a.href = url;
  a.download = String(name || "capture.pdf").split("/").pop();
  a.style.display = "none";
  document.body.appendChild(a);
  a.click();
  a.remove();
}

async function oeffneImBetrachter() {
  /* Auf Android nicht die blob:-URL im Reiter oeffnen. Sie traegt so wenig
   * einen Dateinamen wie eine data:-URL, und wer das PDF von dort ueber den
   * Browser sichert, findet es als "document.pdf" wieder - beim naechsten Mal
   * "document(1).pdf". Am 07.08.2026 entstand so "document(11).pdf", obwohl
   * 2.31.18 schon lief: Der Aufnahmeweg war repariert, dieser hier nicht.
   * Stattdessen der benannte Weg. Android bietet die geladene Datei in der
   * Leiste zum Oeffnen an - angesehen wird sie also weiterhin, nur eben unter
   * ihrem Namen. */
  const quelle = downloadQuelle();
  if (quelle && stand && stand.isAndroid) {
    ankerDownload(quelle, (stand && stand.filename) || "capture.pdf");
    setzeHinweis(t("resultDownloadDone") || "Saved to your downloads folder.");
    return;
  }
  if (blobUrl) {
    try { await browser.tabs.create({ url: blobUrl, active: true }); return; }
    catch (_) { /* weiter zum System-Weg */ }
  }
  try { await browser.runtime.sendMessage({ type: "pdfsnap:open" }); }
  catch (_) { setzeHinweis(t("resultShareError") || "Could not open the file.", true); }
}

/* Herunterladen: schreibt die Datei (noch einmal) in den Download-Ordner.
 * conflictAction "uniquify" verhindert, dass eine vorhandene Datei ueber-
 * schrieben wird - der Nutzer bekommt dann name(1).pdf. */
async function herunterladen() {
  const knopf = $("download");
  knopf.disabled = true;
  try {
    const quelle = downloadQuelle();
    if (!quelle) {
      /* Kein Reiter mehr an dieser Stelle. Bis 2.31.19 wurde hier
       * "pdfsnap:open" geschickt, was das PDF in einem neuen Reiter oeffnete -
       * die Schaltflaeche heisst aber "Herunterladen", und der Nutzer musste
       * dort von Hand noch einmal speichern. Wenn die Daten wirklich weg sind,
       * gehoert das gesagt statt kaschiert. */
      setzeHinweis(t("resultGone") || "No capture available.", true);
      return;
    }
    const name = (stand && stand.filename) || "capture.pdf";
    /* Auf Android gar nicht erst ueber die Download-Schnittstelle gehen. Sie
     * ist dort haeufig nicht verfuegbar, und wenn sie es ist, scheitert sie
     * mitunter still - dann greift auch kein catch, und die Datei landet ohne
     * Namen. Der Anker traegt ihn zuverlaessig. */
    if (stand && stand.isAndroid) {
      ankerDownload(quelle, name);
      setzeHinweis(t("resultDownloadDone") || "Saved to your downloads folder.");
      return;
    }
    try {
      await browser.downloads.download({
        url: quelle,
        filename: name,
        conflictAction: "uniquify",
        saveAs: false
      });
    } catch (eDownload) {
      /* Auf Android ist der Download-Zweig oft nicht verfuegbar. Dann bleibt
       * der Anker mit download-Attribut - und nur er traegt den Dateinamen.
       * Wird das PDF stattdessen als nackte data:-URL im Reiter geoeffnet,
       * kennt der Browser keinen Namen und legt es als "document.pdf" ab;
       * beim zweiten Mal "document(1).pdf" und so fort. Genau das war am
       * 07.08.2026 an einer Aufnahme aus pCloud zu sehen: "document(10).pdf"
       * statt des Seitentitels, waehrend dieselbe Fassung am Rechner richtig
       * benannte. */
      ankerDownload(quelle, name);
    }
    setzeHinweis(t("resultDownloadDone") || "Saved to your downloads folder.");
  } catch (e) {
    console.warn("[PDFSnap/result] Download:", e);
    setzeHinweis((t("resultDownloadError") || "Download failed.") + " " + (e.message || ""), true);
  } finally {
    knopf.disabled = false;
  }
}

/* Weiterleiten: erst der direkte Weg ueber das System-Teilen-Menue, sonst
 * die Datei im System oeffnen - von dort aus teilt jede PDF-App weiter. */
async function weiterleiten() {
  const knopf = $("share");
  knopf.disabled = true;
  try {
    if (kannDateiTeilen(datei)) {
      try {
        await navigator.share({
          files: [datei],
          title: (stand && stand.filename) || "PDF"
        });
        setzeHinweis(t("resultShareDone") || "Forwarded.");
      } catch (e) {
        // Abbruch durch den Nutzer ist kein Fehler und bekommt keine Meldung.
        if (e && e.name === "AbortError") setzeHinweis("");
        else throw e;
      }
      return;
    }
    /* Kann dieser Browser keine Datei an andere Apps uebergeben, fuehrt der
     * bisherige Weg ins Leere: "pdfsnap:open" oeffnete nur einen Reiter mit
     * dem PDF, und darin gibt es keine App-Auswahl. Am 07.08.2026 auf dem
     * Telefon genau so beobachtet - die Schaltflaeche fuehrte nicht dorthin,
     * wo man auswaehlt, ueber welche App weitergeleitet wird.
     *
     * Der Weg, der ans Ziel fuehrt, ist die Datei selbst: heruntergeladen
     * liegt sie in der Ablage, und von dort bietet jedes Android-System das
     * Teilen-Menue an. Also laden und genau das sagen. */
    const quelle = downloadQuelle();
    if (quelle) {
      ankerDownload(quelle, (stand && stand.filename) || "capture.pdf");
      setzeHinweis(t("resultShareViaDownload") ||
        "This browser cannot hand files to other apps directly. The PDF has been saved — open it from your downloads and share it from there.");
    } else {
      setzeHinweis(t("resultShareError") || "Could not forward the file.", true);
    }
  } catch (e) {
    console.warn("[PDFSnap/result] Teilen:", e);
    setzeHinweis((t("resultShareError") || "Could not forward the file.") + " " + (e.message || ""), true);
  } finally {
    knopf.disabled = false;
  }
}

$("download").addEventListener("click", herunterladen);
$("share").addEventListener("click", weiterleiten);
$("extern").addEventListener("click", oeffneImBetrachter);

// Die Objekt-URL lebt so lange wie die Seite. Beim Schliessen freigeben,
// damit das PDF nicht im Speicher haengenbleibt.
window.addEventListener("pagehide", () => {
  if (blobUrl) { try { URL.revokeObjectURL(blobUrl); } catch (_) { /* ignore */ } }
});

laden();
