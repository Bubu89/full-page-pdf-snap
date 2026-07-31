/* Kompatibilitaets-Schicht Firefox MV2 -> Chrome MV3.
 *
 * Zweck: background.js, content.js, popup.js und options.js bleiben nahezu
 * unveraendert. Alles, was in einem MV3-Service-Worker fehlt oder anders
 * heisst, wird hier gekapselt.
 *
 * Drei Problemklassen:
 *   1. Namensraum   - Chrome kennt nur `chrome`, kein `browser`
 *   2. Kein DOM     - ein Service Worker hat weder `document` noch `Image`
 *   3. Keine Blob-URLs - `URL.createObjectURL` existiert im SW nicht
 */

// --- 1. Namensraum ----------------------------------------------------------
// Chrome liefert seit MV3 Promises fuer die hier genutzten APIs, ein Alias
// genuegt also. Nur menus heisst anders und wird umgehaengt - action und
// scripting sprechen beide Browser seit dem MV3-Port gleich an.
if (typeof globalThis.browser === "undefined") {
  globalThis.browser = chrome;
}
if (!globalThis.browser.menus && chrome.contextMenus) {
  globalThis.browser.menus = chrome.contextMenus;
}

// --- 1b. Drossel fuer captureVisibleTab -------------------------------------
// Chrome begrenzt tabs.captureVisibleTab auf MAX_CAPTURE_VISIBLE_TAB_CALLS_PER_SECOND
// (zwei Aufrufe pro Sekunde). Firefox kennt diese Grenze nicht, deshalb ruft der
// gemeinsame Code schneller auf und laeuft ins Kontingent. Die Drossel haelt einen
// Mindestabstand ein und wiederholt, falls die Grenze trotzdem greift - etwa weil
// eine andere Erweiterung parallel aufnimmt.
const CAPTURE_MIN_GAP_MS = 550;   // etwas ueber 500 ms, gegen Taktungenauigkeit
const CAPTURE_MAX_RETRIES = 4;

if (chrome.tabs && typeof chrome.tabs.captureVisibleTab === "function") {
  const original = chrome.tabs.captureVisibleTab.bind(chrome.tabs);
  let lastCall = 0;

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  chrome.tabs.captureVisibleTab = async function throttledCapture(...args) {
    for (let attempt = 0; ; attempt++) {
      const wait = CAPTURE_MIN_GAP_MS - (Date.now() - lastCall);
      if (wait > 0) await sleep(wait);
      lastCall = Date.now();
      try {
        return await original(...args);
      } catch (err) {
        const isQuota = /quota|MAX_CAPTURE/i.test(err && err.message || "");
        if (!isQuota || attempt >= CAPTURE_MAX_RETRIES) throw err;
        // Bei Quota-Treffer laenger warten und erneut versuchen
        await sleep(CAPTURE_MIN_GAP_MS * (attempt + 1));
      }
    }
  };
}

// --- 2. Grafik ohne DOM -----------------------------------------------------

/** Ersetzt document.createElement("canvas"). width/height bleiben schreibbar,
 *  deshalb funktionieren die bestehenden Zuweisungen unveraendert weiter. */
function createCanvas() {
  return new OffscreenCanvas(1, 1);
}

/** Ersetzt new Image() + URL.createObjectURL. Ein ImageBitmap ist fuer
 *  ctx.drawImage() vollwertiger Ersatz. */
async function blobToImage(blob) {
  return await createImageBitmap(blob);
}

/** Ersetzt canvas.toBlob(). OffscreenCanvas kennt nur convertToBlob(). */
async function canvasToJpegBytes(canvas, quality) {
  const blob = await canvas.convertToBlob({ type: "image/jpeg", quality });
  return new Uint8Array(await blob.arrayBuffer());
}

// --- 3. Download ohne Blob-URL ---------------------------------------------

/** downloads.download() braucht eine URL. Im Service Worker gibt es kein
 *  URL.createObjectURL, also wird der Blob zu einer data:-URL kodiert.
 *  In 32-KB-Bloecken, weil String.fromCharCode bei grossen Arrays den
 *  Aufruf-Stack sprengt. */
async function blobToDataUrl(blob) {
  const bytes = new Uint8Array(await blob.arrayBuffer());
  const CHUNK = 0x8000;
  let binary = "";
  for (let i = 0; i < bytes.length; i += CHUNK) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + CHUNK));
  }
  return `data:${blob.type || "application/octet-stream"};base64,${btoa(binary)}`;
}

/** data:-URLs muessen nicht freigegeben werden - No-op, damit bestehende
 *  Aufrufe nicht ins Leere greifen. */
function revokeDownloadUrl(_url) { /* nichts zu tun */ }

// Content-Script-Injection braucht keine Kapselung mehr: beide Browser
// sprechen seit dem MV3-Port dieselbe scripting.executeScript-API.
