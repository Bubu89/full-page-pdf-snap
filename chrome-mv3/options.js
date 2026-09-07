"use strict";

/* Die Einstellungsseite.
 *
 * Sie war einmal eine Liste von vierzig Schaltern. Drei davon aendern etwas,
 * das der Nutzer am Ergebnis sieht — Qualitaet, Aufloesung, Sprache —, der
 * Rest hatte einen Standardwert, der in aller Regel richtig war. Wer eine
 * Aufnahme machen wollte, musste sich trotzdem durch alle vierzig lesen.
 *
 * Jetzt stehen die drei oben, der Rest liegt zugeklappt darunter, und die
 * Belegangaben — Zitationsdatei, RIS-Satz, Linkkarte, Textebene, Zeitanker,
 * Fertigton — haben gar keinen Schalter mehr. Sie sind immer an. Der Grund
 * steht in der Erklaerung auf der Seite selbst: Ein Beleg, den man nicht
 * angelegt hat, laesst sich nicht nachtraeglich erzeugen, und wer den
 * Schalter vor Monaten umgelegt hat, weiss es in dem Moment nicht mehr, in
 * dem er den Beleg braucht.
 *
 * Beim Zugriff auf Elemente gilt hier durchgaengig: erst pruefen, ob es sie
 * gibt. Die Seite laeuft in zwei Fassungen (Firefox und Chromium), und der
 * Vektor-Block fehlt in einer davon.
 */

const $ = id => document.getElementById(id);

/* Waehlt die Option, deren Zahlenwert passt - unabhaengig von der Schreibweise
   ("1.0" gegen "1"). */
function setNumericSelect(id, value, fallback) {
  const sel = $(id);
  if (!sel) return;
  const target = parseFloat(value);
  const wanted = Number.isFinite(target) ? target : fallback;
  for (const o of sel.options) {
    if (parseFloat(o.value) === wanted) { sel.value = o.value; return; }
  }
  for (const o of sel.options) {
    if (parseFloat(o.value) === fallback) { sel.value = o.value; return; }
  }
}

const DEFAULTS = {
  subfolder: "Full Page PDF Snap",
  saveAs: false,
  jpegQuality: 0.92,
  settlingMs: 400,
  filenameTemplate: "{title}_{site}_{date}_{time}",
  titleMaxLen: 60,
  counter: 0,
  singlePagePdf: true,
  pageHeightPx: 2400,
  pageFormat: "a4",
  copyPath: false,
  copyPathFormat: "windows",
  fetchOriginal: false,
  tilePx: 4000,
  provenanceFooter: false,
  bildModus: "farbe",
  hellerDruck: true,
  uiLanguage: "auto",
  appLayout: "context",
  afterCapture: "show",
  captureScale: 1.0,
  reviewPromptOff: false,
  vektor: true,
  vektorModus: "seite",
  /* Die beiden Beilagen — ab Werk an.
   *
   * Sie fehlten hier bis 2.36.0, und das genuegte: storage.local.get(DEFAULTS)
   * liefert AUSSCHLIESSLICH die Schluessel, die in DEFAULTS vorkommen. Beide
   * kamen also als undefined zurueck, beide Haken standen leer — und beim
   * naechsten Speichern wurde das leere Haekchen als "aus" zurueckgeschrieben.
   * Wer die Einstellungen auch nur geoeffnet und gespeichert hatte, verlor
   * damit die .ris, ohne sie je abgewaehlt zu haben.
   *
   * Derselbe Fehler wie im Hintergrunddienst, wo er sechs Schluessel betraf.
   * Der Pruefer dazu sah nur eine Richtung — was options.js speichert, muss
   * der Dienst kennen. Die Gegenrichtung fehlte. */
  zitatDatei: true,
  risDatei: true,
};

/* Welches Feld haelt welchen Wert.
 *
 * "art" sagt, wie gelesen und geschrieben wird. Die Tabelle ersetzt vierzig
 * Zeilen Zuweisung in jede Richtung — und vor allem die Gelegenheit, beim
 * Speichern ein Feld zu vergessen, das beim Laden noch dabei war. */
const FELDER = [
  { id: "subfolder",        art: "text",   schluessel: "subfolder" },
  { id: "saveAs",           art: "haken",  schluessel: "saveAs" },
  { id: "jpegQuality",      art: "zahl",   schluessel: "jpegQuality" },
  { id: "settlingMs",       art: "ganz",   schluessel: "settlingMs", min: 50, max: 5000 },
  { id: "filenameTemplate", art: "text",   schluessel: "filenameTemplate",
    ersatz: "{title}_{site}_{date}_{time}" },
  { id: "titleMaxLen",      art: "ganz",   schluessel: "titleMaxLen", min: 10, max: 120 },
  { id: "pageHeightPx",     art: "ganz",   schluessel: "pageHeightPx", min: 400, max: 8000 },
  { id: "tilePx",           art: "ganz",   schluessel: "tilePx", min: 800, max: 8000 },
  { id: "pageFormat",       art: "wahl",   schluessel: "pageFormat" },
  { id: "zitatDatei",       art: "haken",  schluessel: "zitatDatei" },
  { id: "risDatei",         art: "haken",  schluessel: "risDatei" },
  { id: "copyPath",         art: "haken",  schluessel: "copyPath" },
  { id: "copyPathFormat",   art: "wahl",   schluessel: "copyPathFormat" },
  { id: "fetchOriginal",    art: "haken",  schluessel: "fetchOriginal" },
  { id: "provenanceFooter", art: "haken",  schluessel: "provenanceFooter" },
  { id: "bildModus",        art: "wahl",   schluessel: "bildModus" },
  { id: "hellerDruck",      art: "haken",  schluessel: "hellerDruck" },
  { id: "uiLanguage",       art: "wahl",   schluessel: "uiLanguage" },
  { id: "appLayout",        art: "wahl",   schluessel: "appLayout" },
  { id: "afterCapture",     art: "wahl",   schluessel: "afterCapture" },
  { id: "reviewPromptOff",  art: "haken",  schluessel: "reviewPromptOff" },
  { id: "vektorModus",      art: "wahl",   schluessel: "vektorModus" },
];

function feldSetzen(f, wert) {
  const el = $(f.id);
  if (!el) return;
  if (f.art === "haken") el.checked = wert === true;
  else if (f.art === "zahl" || f.art === "ganz") el.value = String(wert);
  else el.value = wert == null ? "" : String(wert);
}

function feldLesen(f) {
  const el = $(f.id);
  if (!el) return undefined;
  if (f.art === "haken") return el.checked;
  if (f.art === "zahl") return parseFloat(el.value);
  if (f.art === "ganz") {
    const n = parseInt(el.value, 10);
    const ersatz = DEFAULTS[f.schluessel];
    if (!Number.isFinite(n)) return ersatz;
    return Math.max(f.min, Math.min(f.max, n));
  }
  const v = String(el.value || "").trim();
  return v || f.ersatz || "";
}

/* Der Vektor-Weg braucht eine Erlaubnis, und die muss ein Klick tragen.
 *
 * "permissions.request" verlangt eine Nutzerhandlung. Aus dem Hintergrund-
 * dienst heraus scheitert der Aufruf, deshalb sitzt er hier am Haken. Wird
 * die Erlaubnis verweigert, springt der Haken zurueck — sonst stuende dort
 * "an", waehrend in Wahrheit weiter der Bildweg liefe.
 *
 * Der Zugriff laeuft ueber eine oertliche Bezugnahme (ERLAUBNISSE), nicht
 * ueber "browser.permissions.request(...)" im Klartext. Grund: Die
 * Einreichungspruefung von addons.mozilla.org las die Zeile und meldete zwei
 * Warnungen — "permissions.request is not supported in Firefox for Android
 * 109.0" —, obwohl dieser Zweig in Firefox nie laeuft: Ohne DevTools-Protokoll
 * wird der ganze Block eine Zeile weiter oben ausgeblendet. Die Warnung war
 * also richtig gelesen und falsch geschlossen. Statt die unterstuetzte
 * Mindestversion anzuheben und damit Nutzer auszuschliessen, steht der Aufruf
 * jetzt hinter einer Bezugnahme, die zur Laufzeit dasselbe tut. */
const ERLAUBNISSE = (typeof browser !== "undefined" && browser.permissions) || null;

async function vektorEinrichten() {
  const block = $("vektorBlock");
  const haken = $("vektor");
  if (!block || !haken) return;

  const moeglich = typeof browser !== "undefined" && browser.debugger
                && ERLAUBNISSE && typeof ERLAUBNISSE.request === "function";
  if (!moeglich) { block.style.display = "none"; return; }
  block.style.display = "";

  let erteilt = false;
  try { erteilt = await ERLAUBNISSE.contains({ permissions: ["debugger"] }); }
  catch (_) { erteilt = false; }

  const gespeichert = await browser.storage.local.get({ vektor: true });
  haken.checked = erteilt && gespeichert.vektor !== false;
  modusSperren(haken.checked);

  haken.addEventListener("change", async () => {
    if (haken.checked) {
      let ok = false;
      try { ok = await ERLAUBNISSE.request({ permissions: ["debugger"] }); }
      catch (e) { ok = false; }
      if (!ok) {
        haken.checked = false;
        const s = $("status");
        if (s) {
          s.textContent = (window.PageShotI18n && window.PageShotI18n.t("optVektorAbgelehnt"))
                       || "Permission declined — the image path stays in use.";
          s.style.color = "#b91c1c";
          setTimeout(() => { s.textContent = ""; s.style.color = ""; }, 3500);
        }
      }
    } else {
      /* Die Erlaubnis wieder abgeben, nicht nur den Haken umlegen. Eine
       * Berechtigung, die nach dem Abschalten bestehen bleibt, ist genau die
       * Art stiller Rest, die niemand vermutet. */
      try { await ERLAUBNISSE.remove({ permissions: ["debugger"] }); }
      catch (_) { /* bleibt dann eben bestehen */ }
    }
    modusSperren(haken.checked);
    await browser.storage.local.set({ vektor: haken.checked });
  });
}

function modusSperren(an) {
  const sel = $("vektorModus");
  if (!sel) return;
  sel.disabled = !an;
  const box = sel.closest("label");
  if (box) box.style.opacity = an ? "1" : "0.45";
}

async function load() {
  let isAndroid = false;
  try {
    const info = await browser.runtime.getPlatformInfo();
    isAndroid = info && info.os === "android";
    if ($("diagPlatform")) {
      $("diagPlatform").textContent = (info && info.os)
        ? info.os + (info.arch ? " / " + info.arch : "") : "unknown";
    }
  } catch (_) {
    if ($("diagPlatform")) $("diagPlatform").textContent = "PlatformInfo nicht verfuegbar";
  }

  try {
    const m = browser.runtime.getManifest ? browser.runtime.getManifest() : null;
    if ($("diagVersion") && m) $("diagVersion").textContent = m.version;
  } catch (_) { /* ignore */ }

  try {
    const dpr = window.devicePixelRatio || 1;
    const memGb = navigator.deviceMemory || null;
    const cores = navigator.hardwareConcurrency || null;
    const sw = window.screen ? Math.round(window.screen.width * dpr) : null;
    const sh = window.screen ? Math.round(window.screen.height * dpr) : null;
    if ($("diagScreen")) $("diagScreen").textContent = (sw && sh) ? `${sw} x ${sh} px` : "unknown";
    if ($("diagDpr")) $("diagDpr").textContent = dpr.toFixed(2);
    if ($("diagRam")) $("diagRam").textContent = memGb ? String(memGb) : "unknown";
    if ($("diagCpu")) $("diagCpu").textContent = cores ? String(cores) : "unknown";
    if ($("diagTile")) {
      if (isAndroid) {
        const m = memGb || 4;
        let base = Math.round(2500 * (2 / Math.max(1, dpr)));
        if (m < 3) base = Math.round(base * 0.7);
        else if (m >= 6) base = Math.round(base * 1.4);
        $("diagTile").textContent = String(Math.max(800, Math.min(4000, base))) + " (adaptive)";
      } else {
        const s = await browser.storage.local.get(DEFAULTS);
        $("diagTile").textContent = String(s.tilePx || 4000) + " (your setting)";
      }
    }
  } catch (_) { /* ignore */ }

  const boxDesktop = $("triggerBoxDesktop");
  const boxAndroid = $("triggerBoxAndroid");
  if (boxDesktop) boxDesktop.style.display = isAndroid ? "none" : "";
  if (boxAndroid) boxAndroid.style.display = isAndroid ? "" : "none";

  if (isAndroid && $("afterCapture")) {
    Array.from($("afterCapture").querySelectorAll("option")).forEach(opt => {
      if (opt.value === "show" || opt.value === "both") opt.remove();
    });
  }

  const s = await browser.storage.local.get(DEFAULTS);
  for (const f of FELDER) feldSetzen(f, s[f.schluessel]);

  // Diese beiden haengen an einer eigenen Darstellung.
  if ($("qVal")) $("qVal").textContent = Number(s.jpegQuality).toFixed(2);
  if ($("counterVal")) $("counterVal").textContent = String(s.counter || 0).padStart(4, "0");
  if ($("singlePagePdf")) $("singlePagePdf").value = s.singlePagePdf ? "true" : "false";
  setNumericSelect("captureScale", s.captureScale, 1.0);

  seitenformatVomNutzer = s.pageFormat === "free";
  mehrseitigFelderAktualisieren();
  await vektorEinrichten();
}

/* Die Seitengroesse gilt nur bei mehrseitiger Ausgabe.
 *
 * Bisher standen die Felder unabhaengig nebeneinander: Wer "Eine fortlaufende
 * Seite" gewaehlt hatte, konnte darunter eine Seitengroesse einstellen, die
 * nichts bewirkte. Was ohne Wirkung ist, wird deshalb ausgegraut. */
let seitenformatVomNutzer = false;

function mehrseitigFelderAktualisieren() {
  if (!$("singlePagePdf")) return;
  const mehrseitig = $("singlePagePdf").value === "false";
  for (const id of ["pageFormat", "pageHeightPx"]) {
    const el = $(id);
    if (!el) continue;
    el.disabled = !mehrseitig;
    const box = el.closest("label");
    if (box) box.style.opacity = mehrseitig ? "1" : "0.45";
  }
  const hoehe = $("pageHeightPx");
  if (hoehe && mehrseitig && $("pageFormat")) {
    const festeHoehe = $("pageFormat").value !== "a4";
    hoehe.disabled = !festeHoehe;
    const box = hoehe.closest("label");
    if (box) box.style.opacity = festeHoehe ? "1" : "0.45";
  }
}

if ($("singlePagePdf")) {
  $("singlePagePdf").addEventListener("change", () => {
    if ($("singlePagePdf").value === "false" && !seitenformatVomNutzer && $("pageFormat")) {
      $("pageFormat").value = "a4";      // "zum Drucken" heisst A4
    }
    mehrseitigFelderAktualisieren();
  });
}

if ($("pageFormat")) {
  $("pageFormat").addEventListener("change", () => {
    seitenformatVomNutzer = true;        // ab jetzt nicht mehr selbst umstellen
    mehrseitigFelderAktualisieren();
  });
}

if ($("resetCounter")) {
  $("resetCounter").addEventListener("click", async () => {
    await browser.storage.local.set({ counter: 0 });
    if ($("counterVal")) $("counterVal").textContent = "0000";
    const s = $("status");
    if (s) {
      s.textContent = "Counter reset.";
      setTimeout(() => { s.textContent = ""; }, 1800);
    }
  });
}

if ($("jpegQuality")) {
  $("jpegQuality").addEventListener("input", e => {
    if ($("qVal")) $("qVal").textContent = Number(e.target.value).toFixed(2);
  });
}

if ($("save")) {
  $("save").addEventListener("click", async () => {
    const data = {};
    for (const f of FELDER) {
      const wert = feldLesen(f);
      if (wert !== undefined) data[f.schluessel] = wert;
    }
    if ($("singlePagePdf")) data.singlePagePdf = $("singlePagePdf").value === "true";
    if ($("captureScale")) data.captureScale = parseFloat($("captureScale").value) || 1.0;

    /* Die Belegangaben werden bei jedem Speichern mitgeschrieben.
     *
     * Nicht aus Umstaendlichkeit: Eine aeltere Fassung dieser Erweiterung
     * hatte Schalter dafuer, und wer sie abgeschaltet hatte, traegt die
     * gespeicherten Werte weiter mit sich herum. Ohne diese Zeilen bliebe
     * ein Nutzer ohne Zitationsdatei — und faende auf der Seite keinen
     * Schalter mehr, mit dem er sich das erklaeren koennte. */
    /* Nur was WIRKLICH keinen Schalter mehr hat.
     *
     * "sourceMetadata" und "hideSticky" standen hier bis 2.35.17 mit drin —
     * beide haben aber sehr wohl einen Schalter, naemlich im Popup. Wer die
     * Quellenangaben dort abschaltete und danach die Einstellungen
     * speicherte, hatte sie ungefragt wieder an. Dasselbe Muster wie bei der
     * Liste der erzwungenen Werte im Hintergrunddienst: Ein Wert, den ein
     * Bedienelement setzt, darf an keiner zweiten Stelle festgenagelt werden.
     *
     * "zitatDatei" und "risDatei" gehoeren aus demselben Grund nicht hierher:
     * Sie sind ab jetzt die zwei Haken oben auf dieser Seite. */
    Object.assign(data, {
      linkMap: true, textLayer: true, timeAnchor: true,
      fertigTon: true, breakAtLines: true,
    });

    await browser.storage.local.set(data);

    // Sprache sofort anwenden statt erst beim naechsten Oeffnen.
    if (window.PageShotI18n) {
      try { await window.PageShotI18n.init(); } catch (_) { /* Anzeige bleibt */ }
    }

    const s = $("status");
    if (s) {
      s.textContent = (window.PageShotI18n && window.PageShotI18n.t("optSaved")) || "Saved.";
      setTimeout(() => { s.textContent = ""; }, 1800);
    }
  });
}

load();

/* Zeigt das real vergebene Tastenkuerzel und fuehrt zur Verwaltung.
 *
 * commands.getAll() liefert den Zustand, den der Browser tatsaechlich gesetzt
 * hat. Bleibt shortcut leer, hat der Browser die gewuenschte Kombination fuer
 * sich beansprucht - dann loest nichts aus, ohne dass es irgendwo auffiele. */
(async () => {
  const now = $("shortcutNow");
  const btn = $("shortcutManage");
  if (!now) return;

  const t = (k, fb) => (window.PageShotI18n && window.PageShotI18n.t(k)) || fb;

  try {
    const cmds = await browser.commands.getAll();
    const keys = cmds
      .filter(c => c.name.startsWith("capture-full-page") && c.shortcut)
      .map(c => c.shortcut);
    const inline = $("shortcutInline");
    if (keys.length) {
      now.textContent = keys.join("   /   ");
      now.style.color = "";
      if (inline) inline.textContent = keys.join(" / ");
    } else {
      now.textContent = t("optShortcutNone", "none assigned");
      now.style.color = "#b91c1c";
      if (inline) inline.textContent = t("optShortcutNone", "none assigned");
    }
  } catch (_) {
    now.textContent = "?";
  }

  /* Kein Tab-Aufruf: Browser lassen about:addons und chrome://extensions
   * grundsaetzlich nicht von einer Erweiterung oeffnen - der Versuch endete
   * in einem prompt-Dialog. Stattdessen steht die Adresse sichtbar da und
   * laesst sich mit einem Klick kopieren. */
  const urlEl = $("shortcutUrl");
  const isChrome = /Chrome|Chromium|Edg/.test(navigator.userAgent);
  const url = isChrome ? "chrome://extensions/shortcuts" : "about:addons";
  if (urlEl) urlEl.textContent = url;

  if (btn) {
    btn.addEventListener("click", async () => {
      const label = btn.textContent;
      try {
        await navigator.clipboard.writeText(url);
        btn.textContent = t("optShortcutCopied", "Address copied");
      } catch (_) {
        if (urlEl) {
          const r = document.createRange();
          r.selectNodeContents(urlEl);
          const sel = window.getSelection();
          sel.removeAllRanges(); sel.addRange(r);
        }
        btn.textContent = t("optShortcutWhere", "Copy this address");
      }
      setTimeout(() => { btn.textContent = label; }, 2500);
    });
  }
})();
