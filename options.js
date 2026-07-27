"use strict";

const DEFAULTS = {
  subfolder: "Full Page PDF Snap",
  saveAs: false,
  jpegQuality: 0.92,
  settlingMs: 400,
  filenameTemplate: "{site}_{date}_{time}_{n}",
  titleMaxLen: 40,
  counter: 0,
  singlePagePdf: true,
  pageHeightPx: 2400,
  tilePx: 4000,
  hideSticky: true,
  appLayout: "context",
  afterCapture: "show",
  captureScale: 1.5
};

const $ = id => document.getElementById(id);

async function load() {
  // Plattform-Erkennung + adaptive Info-Anzeige.
  let isAndroid = false;
  try {
    const info = await browser.runtime.getPlatformInfo();
    isAndroid = info && info.os === "android";
    const diag = $("diagPlatform");
    if (diag) diag.textContent = (info && info.os) ? info.os + (info.arch ? " / " + info.arch : "") : "unbekannt";
  } catch (_) {
    const diag = $("diagPlatform");
    if (diag) diag.textContent = "PlatformInfo nicht verfuegbar";
  }
  try {
    const m = browser.runtime.getManifest ? browser.runtime.getManifest() : null;
    const v = $("diagVersion");
    if (v && m) v.textContent = m.version;
  } catch (_) { /* ignore */ }

  // Device-Metriken direkt aus window/navigator lesen (options.html laeuft im Chrome-Ctx).
  try {
    const dpr = window.devicePixelRatio || 1;
    const memGb = navigator.deviceMemory || null;
    const cores = navigator.hardwareConcurrency || null;
    const sw = window.screen ? Math.round(window.screen.width * dpr) : null;
    const sh = window.screen ? Math.round(window.screen.height * dpr) : null;
    if ($("diagScreen")) $("diagScreen").textContent = (sw && sh) ? `${sw} x ${sh} px` : "unbekannt";
    if ($("diagDpr")) $("diagDpr").textContent = dpr.toFixed(2);
    if ($("diagRam")) $("diagRam").textContent = memGb ? String(memGb) : "unbekannt";
    if ($("diagCpu")) $("diagCpu").textContent = cores ? String(cores) : "unbekannt";
    // Effektive tilePx nach gleicher Formel wie background.js
    if (isAndroid) {
      const m = memGb || 4;
      let base = Math.round(2500 * (2 / Math.max(1, dpr)));
      if (m < 3) base = Math.round(base * 0.7);
      else if (m >= 6) base = Math.round(base * 1.4);
      const eff = Math.max(800, Math.min(4000, base));
      if ($("diagTile")) $("diagTile").textContent = String(eff) + " (adaptive)";
    } else {
      const s = await browser.storage.local.get(DEFAULTS);
      if ($("diagTile")) $("diagTile").textContent = String(s.tilePx || 4000) + " (User-Setting, Desktop nutzt keine Adaptive)";
    }
  } catch (_) { /* ignore */ }

  // Trigger-Info: nur den passenden Kasten zeigen.
  const boxDesktop = $("triggerBoxDesktop");
  const boxAndroid = $("triggerBoxAndroid");
  if (isAndroid) {
    if (boxAndroid) boxAndroid.style.display = "";
    if (boxDesktop) boxDesktop.style.display = "none";
  } else {
    if (boxAndroid) boxAndroid.style.display = "none";
    if (boxDesktop) boxDesktop.style.display = "";
  }

  if (isAndroid) {
    const sel = $("afterCapture");
    Array.from(sel.querySelectorAll("option")).forEach(opt => {
      if (opt.value === "show" || opt.value === "both") opt.remove();
    });
    const hint = sel.parentNode.querySelector(".hint");
    if (hint) hint.textContent = "Auf Android wird das PDF nach dem Speichern direkt in der Standard-PDF-App geoeffnet — die Ordner-Anzeige ist dort nicht verfuegbar.";
    const scaleHint = $("captureScale").parentNode.querySelector(".hint");
    if (scaleHint) scaleHint.textContent = "Auf Android ohne Wirkung — Firefox for Android bietet keine tabs.setZoom API.";
  }

  const s = await browser.storage.local.get(DEFAULTS);
  $("subfolder").value = s.subfolder ?? "";
  $("saveAs").checked = !!s.saveAs;
  $("jpegQuality").value = String(s.jpegQuality);
  $("qVal").textContent = Number(s.jpegQuality).toFixed(2);
  $("settlingMs").value = String(s.settlingMs);
  $("filenameTemplate").value = s.filenameTemplate || "{site}_{date}_{time}_{n}";
  $("titleMaxLen").value = String(s.titleMaxLen || 40);
  $("counterVal").textContent = String(s.counter || 0).padStart(4, "0");
  $("singlePagePdf").value = s.singlePagePdf ? "true" : "false";
  $("pageHeightPx").value = String(s.pageHeightPx || 2400);
  $("tilePx").value = String(s.tilePx || 4000);
  $("hideSticky").checked = s.hideSticky !== false;
  $("appLayout").value = s.appLayout || "context";
  $("afterCapture").value = s.afterCapture || "show";
  $("captureScale").value = String(s.captureScale || 1.5);
}

$("resetCounter").addEventListener("click", async () => {
  await browser.storage.local.set({ counter: 0 });
  $("counterVal").textContent = "0000";
  const s = $("status");
  s.textContent = "Counter zurueckgesetzt.";
  setTimeout(() => { s.textContent = ""; }, 1800);
});

$("jpegQuality").addEventListener("input", e => {
  $("qVal").textContent = Number(e.target.value).toFixed(2);
});

$("save").addEventListener("click", async () => {
  const data = {
    subfolder: $("subfolder").value.trim(),
    saveAs: $("saveAs").checked,
    jpegQuality: parseFloat($("jpegQuality").value),
    settlingMs: Math.max(50, Math.min(5000, parseInt($("settlingMs").value, 10) || 400)),
    filenameTemplate: $("filenameTemplate").value.trim() || "{site}_{date}_{time}_{n}",
    titleMaxLen: Math.max(10, Math.min(120, parseInt($("titleMaxLen").value, 10) || 40)),
    singlePagePdf: $("singlePagePdf").value === "true",
    pageHeightPx: Math.max(400, Math.min(8000, parseInt($("pageHeightPx").value, 10) || 2400)),
    tilePx: Math.max(800, Math.min(8000, parseInt($("tilePx").value, 10) || 4000)),
    hideSticky: $("hideSticky").checked,
    appLayout: $("appLayout").value,
    afterCapture: $("afterCapture").value,
    captureScale: parseFloat($("captureScale").value) || 1.5
  };
  await browser.storage.local.set(data);
  const s = $("status");
  s.textContent = "Gespeichert.";
  setTimeout(() => { s.textContent = ""; }, 1800);
});

load();
