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
// genuegt also. Zwei APIs heissen anders und werden umgehaengt.
if (typeof globalThis.browser === "undefined") {
  globalThis.browser = chrome;
}
if (!globalThis.browser.menus && chrome.contextMenus) {
  globalThis.browser.menus = chrome.contextMenus;
}
if (!globalThis.browser.browserAction && chrome.action) {
  globalThis.browser.browserAction = chrome.action;
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

// --- 4. Content-Script-Injection -------------------------------------------

/** MV2: tabs.executeScript(tabId, {file}). MV3: scripting.executeScript
 *  mit target/files. */
async function injectContentScript(tabId, file) {
  await chrome.scripting.executeScript({
    target: { tabId },
    files: [file],
  });
}
