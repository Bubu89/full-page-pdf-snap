/* Laedt den Hintergrunddienst so, wie der Browser ihn laedt.
 *
 * Anlass (17.08.2026): Mit cdp-vektor.js und zitate.js kamen zwei Dateien in
 * die importScripts-Zeile. Faellt eine davon aus — Tippfehler im Namen, ein
 * Syntaxfehler, ein Verweis auf etwas, das es noch nicht gibt —, dann startet
 * der Hintergrunddienst gar nicht, und die Erweiterung tut nichts mehr. Nicht
 * "die neue Funktion fehlt", sondern: nichts. Kein anderer Test in diesem
 * Ordner haette das bemerkt, weil alle einzelne Funktionen herausschneiden
 * und fuer sich pruefen.
 *
 * Geprueft wird deshalb das, was der Browser tut: alle Dateien der Reihe nach
 * in einen Bereich laden, in dem die Browser-Schnittstellen nur nachgeahmt
 * sind, und sehen, ob am Ende die erwarteten Bausteine dastehen.
 *
 * Was hier NICHT geprueft wird: ob die Aufnahme funktioniert. Dafuer braucht
 * es einen Browser. Geprueft wird, dass sie ueberhaupt starten kann.
 */
import { test } from "node:test";
import { readFileSync, existsSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const HIER = dirname(fileURLToPath(import.meta.url));
const WURZEL = join(HIER, "..");

let fehler = 0;
const pruefe = (bedingung, text) => {
  if (bedingung) console.log("#   ok   " + text);
  else { console.log("# FEHL " + text); fehler++; }
};

/* Eine Attrappe der Browser-Schnittstelle.
 *
 * Sie muss nichts koennen — nur alles hinnehmen, was beim Laden aufgerufen
 * wird. Der Hintergrunddienst haengt beim Start Zuhoerer ein; wirft dabei
 * etwas, faellt der ganze Dienst aus. Genau das soll auffallen. */
function attrappe() {
  const zuhoerer = { addListener() {}, removeListener() {}, hasListener: () => false };
  const nichts = () => Promise.resolve();
  const browser = {
    runtime: {
      onMessage: zuhoerer, onInstalled: zuhoerer, onStartup: zuhoerer,
      getManifest: () => ({ version: "0.0.0-test" }),
      getPlatformInfo: () => Promise.resolve({ os: "linux", arch: "x86-64" }),
      getURL: p => "chrome-extension://test/" + p,
      lastError: null,
    },
    tabs: { query: () => Promise.resolve([]), sendMessage: nichts, getZoom: () => Promise.resolve(1),
            setZoom: nichts, create: nichts, onUpdated: zuhoerer, onRemoved: zuhoerer },
    downloads: { download: nichts, search: () => Promise.resolve([]), open: nichts,
                 show: nichts, onChanged: zuhoerer },
    storage: { local: { get: d => Promise.resolve(d || {}), set: nichts },
               managed: { get: () => Promise.reject(new Error("keine Vorgabe")) },
               onChanged: zuhoerer },
    action: { setBadgeText: nichts, setBadgeBackgroundColor: nichts, setTitle: nichts,
              setPopup: nichts, onClicked: zuhoerer },
    notifications: { create: nichts, clear: nichts, onClicked: zuhoerer, onButtonClicked: zuhoerer },
    commands: { onCommand: zuhoerer, getAll: () => Promise.resolve([]) },
    contextMenus: { create: () => {}, removeAll: nichts, onClicked: zuhoerer },
    menus: { create: () => {}, removeAll: nichts, onClicked: zuhoerer },
    scripting: { executeScript: () => Promise.resolve([]) },
    permissions: { contains: () => Promise.resolve(false), request: () => Promise.resolve(false),
                   remove: () => Promise.resolve(true) },
    debugger: { attach: nichts, detach: nichts, sendCommand: nichts,
                getTargets: () => Promise.resolve([]), onEvent: zuhoerer, onDetach: zuhoerer },
    i18n: { getMessage: () => "", getUILanguage: () => "de" },
  };

  const geladen = [];
  const bereich = {
    browser, chrome: browser, console,
    setTimeout, clearTimeout, setInterval, clearInterval,
    Math, JSON, Date, Promise, Error, TypeError, RangeError,
    Uint8Array, Uint32Array, Uint8ClampedArray, Int32Array, Float64Array, ArrayBuffer, DataView,
    Array, Object, String, Number, Boolean, Map, Set, WeakMap, RegExp, Symbol, Proxy, Reflect,
    parseInt, parseFloat, isNaN, isFinite, encodeURIComponent, decodeURIComponent,
    atob: s => Buffer.from(s, "base64").toString("binary"),
    btoa: s => Buffer.from(s, "binary").toString("base64"),
    TextEncoder, TextDecoder, URL, Blob: class {}, FileReader: class {},
    crypto: { subtle: { digest: () => Promise.resolve(new ArrayBuffer(32)) },
              getRandomValues: a => a },
    fetch: () => Promise.reject(new Error("kein Netz im Test")),
    OffscreenCanvas: class { getContext() { return null; } },
    createImageBitmap: () => Promise.reject(new Error("kein Bild im Test")),
    importScripts(...dateien) { geladen.push(...dateien); },
    self: null, location: { href: "chrome-extension://test/" },
  };
  bereich.globalThis = bereich;
  bereich.self = bereich;
  return { bereich, geladen };
}

function ladeKette(paketPfad, importZeileAus) {
  const { bereich, geladen } = attrappe();
  vm.createContext(bereich);

  // Die importScripts-Zeile aus der echten Datei lesen, nicht abschreiben.
  const quelle = readFileSync(join(paketPfad, importZeileAus), "utf8");
  const treffer = quelle.match(/importScripts\(([^)]*)\)/);
  const dateien = treffer
    ? treffer[1].split(",").map(s => s.trim().replace(/^["']|["']$/g, "")).filter(Boolean)
    : [];

  for (const datei of [...dateien, importZeileAus]) {
    const pfad = join(paketPfad, datei);
    if (!existsSync(pfad)) {
      pruefe(false, `${datei}: Datei fehlt im Paket`);
      continue;
    }
    try {
      vm.runInContext(readFileSync(pfad, "utf8"), bereich, { filename: datei });
      pruefe(true, `${datei}: geladen`);
    } catch (e) {
      pruefe(false, `${datei}: wirft beim Laden — ${e.message}`);
    }
  }
  return { bereich, dateien, geladen };
}

test("Ladekette des Hintergrunddienstes", () => {
  console.log("# --- Chrome (MV3, importScripts) ---");
  const chrome = ladeKette(join(WURZEL, "chrome-mv3"), "background.js");

  pruefe(chrome.dateien.includes("cdp-vektor.js"),
         "background.js laedt cdp-vektor.js");
  pruefe(chrome.dateien.includes("zitate.js"),
         "background.js laedt zitate.js");

  for (const baustein of ["PageShotPdf", "PageShotZitate", "PageShotVektor"]) {
    pruefe(typeof chrome.bereich[baustein] === "object" && chrome.bereich[baustein] !== null,
           `${baustein} steht nach dem Laden bereit`);
  }
  for (const fn of ["vektorMoeglich", "vektorErlaubt", "vektorAufnehmen"]) {
    pruefe(typeof chrome.bereich.PageShotVektor?.[fn] === "function",
           `PageShotVektor.${fn} ist aufrufbar`);
  }
  pruefe(typeof chrome.bereich.PageShotZitate?.belegDatei === "function",
         "PageShotZitate.belegDatei ist aufrufbar");

  /* Ohne DevTools-Protokoll darf der Vektorweg nicht behaupten, er koenne
   * etwas. In der Attrappe ist browser.debugger vorhanden — also muss
   * vektorMoeglich() true sagen und vektorErlaubt() (contains: false) false. */
  pruefe(chrome.bereich.PageShotVektor.vektorMoeglich() === true,
         "vektorMoeglich erkennt das vorhandene DevTools-Protokoll");

  console.log("# --- Firefox (background.html) ---");
  const html = readFileSync(join(WURZEL, "background.html"), "utf8");
  const skripte = [...html.matchAll(/<script src="([^"]+)"/g)].map(m => m[1]);
  const { bereich: ff } = attrappe();
  vm.createContext(ff);
  for (const datei of skripte) {
    const pfad = join(WURZEL, datei);
    if (!existsSync(pfad)) { pruefe(false, `${datei}: Datei fehlt`); continue; }
    try {
      vm.runInContext(readFileSync(pfad, "utf8"), ff, { filename: datei });
      pruefe(true, `${datei}: geladen`);
    } catch (e) {
      pruefe(false, `${datei}: wirft beim Laden — ${e.message}`);
    }
  }
  pruefe(typeof ff.PageShotZitate?.belegDatei === "function",
         "Firefox: PageShotZitate steht bereit");

  /* Jede in background.html geladene Datei muss auch ins Paket.
   * zeitanker.js fehlte dort unbemerkt, weil die Paketpruefung ausgerechnet
   * background.html ausnahm — die Funktion war standardmaessig aus und fiel
   * deshalb nie auf. */
  const pack = readFileSync(join(WURZEL, "pack-firefox.py"), "utf8");
  const include = pack.match(/INCLUDE = \[([\s\S]*?)\]/)[1];
  for (const datei of skripte) {
    pruefe(include.includes(`"${datei}"`),
           `pack-firefox.py nimmt ${datei} ins Paket`);
  }

  console.log(fehler === 0 ? "# alle Prüfungen bestanden"
                           : `# Ladekette: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Prüfungen fehlgeschlagen`);
});
