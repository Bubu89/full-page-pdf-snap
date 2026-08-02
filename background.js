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
    if (pg.tiles && pg.tiles.length) for (const t of pg.tiles) teile.push(t.jpegBytes);
    else if (pg.jpegBytes) teile.push(pg.jpegBytes);
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
  settlingMs: 400,
  filenameTemplate: "{site}_{date}_{time}_{n}",
  titleMaxLen: 40,
  singlePagePdf: true,
  pageHeightPx: 2400,
  pageFormat: "free",     // "a4" bricht auf Druckseiten um
  breakAtLines: true,      // Schnitt in die naechste Luecke ziehen
  sourceMetadata: true,    // Quellenangaben aus der Seite lesen (kein Netz)
  fetchOriginal: false,    // Verlags-PDF holen — einziger Netzzugriff, daher aus
  tilePx: 4000,
  hideSticky: true,
  // Sichtbare Herkunftszeile unter der Aufnahme. Standard aus, weil sie das
  // Bild veraendert; die Metadaten im PDF stehen ohnehin immer drin.
  provenanceFooter: false,
  // Unsichtbare Textebene aus dem Dokument. Standard an: sie macht das PDF
  // durchsuchbar, ohne das Bild zu veraendern.
  textLayer: true,
  uiLanguage: "auto",
  appLayout: "context",
  afterCapture: "show",
  // 1.0 = genau die Ansicht, die der Nutzer am Bildschirm sieht. Hoehere Werte
  // zoomen die Seite vor der Aufnahme: schaerfer, aber es passt weniger ins
  // Fenster - Menues und Seitenleisten werden dann frueher abgeschnitten.
  captureScale: 1.0
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

async function getSettings() {
  const defs = await getDefaults();
  const stored = await browser.storage.local.get(defs);
  const merged = { ...defs, ...stored };
  // Android-Safety: 'show'/'both' funktionieren dort nicht (downloads.show fehlt).
  // Falls Settings von Desktop-Sync hierher landen, mappen wir auf 'open'.
  const p = await getPlatform();
  if (p.isAndroid && (merged.afterCapture === "show" || merged.afterCapture === "both")) {
    merged.afterCapture = "open";
  }
  return merged;
}

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

function sanitizeFilename(s, maxLen) {
  return String(s)
    .replace(/[\\/:*?"<>|]/g, "_")
    .replace(/\s+/g, " ")
    .trim()
    .slice(0, maxLen || 40) || "page";
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
      throw new Error("Diese Seite erlaubt keine Erweiterungs-Skripte (about:/addons.mozilla.org/PDF-Viewer etc.)");
    }
    await sleep(120);
  }
  const r = await browser.tabs.sendMessage(tabId, { cmd: "ping" });
  if (!r || !r.ok) throw new Error("Content-Script antwortet nicht.");
}

async function captureFullPage(tab) {
  const settings = await getSettings();
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

async function captureFullPageInner(tab, settings) {
  // Textebene: wird im selben Seitenzustand gesammelt wie die Bilder.
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

      const fresh = await browser.tabs.sendMessage(tab.id, { cmd: "currentTotalH" }).catch(() => null);
      if (fresh && fresh.totalH && fresh.totalH > totalH) {
        log("Lazy-load grew page:", totalH, "->", fresh.totalH);
        totalH = fresh.totalH;
        maxScroll = Math.max(0, totalH - layout.viewportH);
      }

      if (actualY >= maxScroll - 2) break;
      y += stepCss;
      if (y > maxScroll) y = maxScroll;
      if (++safety > 400) throw new Error("Zu viele Scroll-Schritte");
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
        }
      } catch (e) {
        log("Quellenangaben nicht verfuegbar:", e && e.message);
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
        }
      } catch (e) {
        log("Textebene nicht verfuegbar:", e && e.message);
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
  const unvollstaendig = coverage.filter(c => !c.ok);
  if (unvollstaendig.length) {
    log("WARNUNG: unvollstaendige Abdeckung —", unvollstaendig.map(c => c.meldung).join(" | "));
    notifyHint("Teile der Seite konnten nicht vollstaendig erfasst werden: "
               + unvollstaendig.map(c => c.meldung).join(" · "));
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
  const pxW = keepFrame ? segments[0].pxW : clipW;
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

  const big = document.createElement("canvas");
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
    // A4 hoch mit 15 mm Rand: 180 x 267 mm nutzbar. Die aufgenommene Breite
    // fuellt diese 180 mm, daraus folgt die Hoehe.
    const hoehe = seitenHoehe || Math.round(pxW * 267 / 180);
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

  const pages = [];
  if (settings.singlePagePdf) {
    const tilePx = Math.max(800, Math.min(8000, effectiveTilePx));
    if (bigH <= tilePx) {
      const jpegBytes = await canvasToJpegBytes(big, settings.jpegQuality);
      pages.push({ jpegBytes, widthPx: pxW, heightPx: bigH });
      log("Single-page PDF: 1 page, 1 tile,", jpegBytes.length, "bytes JPEG");
    } else {
      const tasks = [];
      for (let y = 0; y < bigH; y += tilePx) {
        const h = Math.min(tilePx, bigH - y);
        const slice = document.createElement("canvas");
        slice.width = pxW;
        slice.height = h;
        slice.getContext("2d").drawImage(big, 0, y, pxW, h, 0, 0, pxW, h);
        tasks.push(
          canvasToJpegBytes(slice, settings.jpegQuality).then(b => ({
            jpegBytes: b, xPx: 0, yPx: y, wPx: pxW, hPx: h
          }))
        );
      }
      const tiles = await Promise.all(tasks);
      const totalBytes = tiles.reduce((s, t) => s + t.jpegBytes.length, 0);
      pages.push({ widthPx: pxW, heightPx: bigH, tiles });
      log("Single-page PDF: 1 page,", tiles.length, "tiles, tilePx=", tilePx, "total=", totalBytes, "bytes JPEG");
    }
  } else {
    const sliceH = Math.max(400, Math.min(8000, settings.pageHeightPx || 2400));
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
      tasks.push(canvasToJpegBytes(slice, settings.jpegQuality).then(b => ({
        jpegBytes: b, widthPx: pxW, heightPx: h, yPx: y
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
  });

  const baseTitle = sanitizeFilename(tab.title || "page", settings.titleMaxLen);
  const site = siteFromUrl(tab.url);
  const stamp = nowStamp();
  const n = await nextCounter();

  const filename = (settings.filenameTemplate || "{site}_{date}_{time}_{n}")
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
    let usedFilename = relPath;
    let saveMethod = "download-subfolder";

    const withTimeout = (promise, ms, tag) => Promise.race([
      promise,
      new Promise((_, rej) => setTimeout(() => rej(new Error("TIMEOUT_" + tag + "_" + ms + "ms")), ms))
    ]);

    // Attempt 1 — mit Subfolder
    try {
      id = await withTimeout(browser.downloads.download({
        url,
        filename: relPath,
        saveAs: p.isAndroid ? false : !!settings.saveAs,
        conflictAction: "uniquify"
      }), p.isAndroid ? 5000 : 30000, "A1");
      log("Save A1 OK:", id, relPath);
    } catch (e1) {
      log("Save A1 failed:", e1.message);
      id = null;
    }

    // Attempt 2 — Android-Fallback ohne Subfolder
    if (id === null && p.isAndroid && subfolder) {
      log("Save A2: retrying without subfolder ...");
      try {
        id = await withTimeout(browser.downloads.download({
          url,
          filename: filename,
          saveAs: false,
          conflictAction: "uniquify"
        }), 5000, "A2");
        usedFilename = filename;
        saveMethod = "download-root";
        log("Save A2 OK:", id, filename);
      } catch (e2) {
        log("Save A2 failed:", e2.message);
        id = null;
      }
    }

    // Attempt 3 — Auf Android: PDF direkt im Browser oeffnen.
    // Der User speichert dann selbst wenn er will (via Firefox-Download-Icon).
    // Kein SAF-Dialog mehr, weil er auf manchen Geraeten nicht triggert.
    if (id === null && p.isAndroid) {
      log("Save A3: opening PDF in new tab (Android default fallback) ...");
      try {
        try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) {}
        const newTab = await browser.tabs.create({ url, active: true });
        saveMethod = "tab-open";
        _lastDownloadId = null;
        _lastFilename = filename;
        _lastFallbackTabId = newTab && newTab.id;
        notifyInfo("PDF im Browser bereit — dort steht die Download-Option zur Verfuegung.");
        return { ok: true, downloadId: null, filename: usedFilename, pages: pages.length, segments: segments.length, method: saveMethod };
      } catch (e3) {
        log("Save A3 (tab open) failed:", e3.message);
        try { await browser.notifications.clear("pdfsnap-progress"); } catch (_) {}
        notifyError("Speichern fehlgeschlagen.");
        throw e3;
      }
    }
    log("Download started", id, usedFilename, "method=" + saveMethod, "pages=", pages.length);

    const platform = await getPlatform();

    // Auf Android liefert onChanged 'complete' u.U. nie — wir warten kurz und ziehen dann durch.
    const waitMs = platform.isAndroid ? 8000 : 30000;
    let downloadComplete = true;
    try { await waitForDownloadComplete(id, waitMs); }
    catch (e) { log("download wait:", e.message); downloadComplete = false; }

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
      const fallbackHint = usedFilename === filename && subfolder
        ? " (Root Download-Ordner)"
        : "";
      notifyInfo(`Fertig — ${pages.length} Seite${pages.length === 1 ? "" : "n"} gespeichert${fallbackHint}. Tippen zum Anzeigen.`);
    }

    // Originaldatei des Verlags dazulegen, wenn die Seite eine angibt.
    //
    // Das ist der einzige Vorgang der Erweiterung, der eine Verbindung
    // aufbaut, und deshalb standardmaessig aus. Geholt wird ausschliesslich
    // die Adresse, die die Seite selbst als Volltext nennt — derselbe Abruf,
    // den ein Klick auf "PDF" ausloest, mit demselben Zugang. Was hinter
    // einer Schranke liegt, bleibt dort: der Server antwortet dann mit einer
    // Fehlerseite, und die wird nicht als Volltext ausgegeben.
    if (settings.fetchOriginal === true && quelle && quelle.dateien && quelle.dateien.length) {
      const stamm = relPath.replace(/\.pdf$/i, "");
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

function isCapturable(url) {
  if (!url) return { ok: false, reason: "Kein Tab geladen." };
  if (!/^https?:|^file:/.test(url)) {
    return { ok: false, reason: "Interne Firefox-Seite — bitte zu einer normalen Webseite wechseln (https://...)." };
  }
  try {
    const host = new URL(url).hostname;
    if (BLOCKED_HOSTS.some(h => host === h || host.endsWith("." + h))) {
      return { ok: false, reason: "Firefox schuetzt diese Seite. Bitte zu einer normalen Webseite wechseln (z.B. wikipedia.org)." };
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
    notifyInfo("PDF im Browser bereit — dort steht die Download-Option zur Verfuegung.");
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
    notifyInfo(`PDF gespeichert: ${filename}. Tippen zum Anzeigen.`);
  }
  return { ok: true, downloadId: id, filename: relPath, pages: null, segments: null, method: "pdf-direct" };
}

function makeUserHintError(msg) {
  const e = new Error(msg);
  e.userHint = true;
  return e;
}

async function runOnActiveTab() {
  if (_captureInFlight) {
    log("Ignoring tap — capture already in flight.");
    return { ok: false, error: "Bereits laufend" };
  }
  const [tab] = await browser.tabs.query({ active: true, currentWindow: true });
  if (!tab) throw makeUserHintError("Kein aktiver Tab.");
  const check = isCapturable(tab.url);
  if (!check.ok) {
    throw makeUserHintError(check.reason);
  }
  // Bereits geoeffnete PDF -> direkter Download-Zweig statt Screenshot-Pipeline.
  const useDirectPdf = check.mode === "pdf-direct";
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
      : await captureFullPage(tab);
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
      notifyError(e && e.message ? e.message : String(e));
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
    catch (e) { console.error(TAG, e); notifyError(e.message); }
  });
}

browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg && msg.cmd === "capture") {
    runOnActiveTab()
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
      downloadId: _lastDownloadId
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
  catch (e) { console.error(TAG, e); notifyError(e.message); }
});

(async () => {
  const p = await getPlatform();
  if (p.isAndroid) {
    try {
      await browser.action.setPopup({ popup: "" });
      log("Android detected — popup disabled, direct-capture mode active.");
    } catch (e) { log("setPopup failed:", e); }
  }
})();

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
          message: "Aufnahme laeuft noch — bitte warten. Bei Fehler wird eine Meldung angezeigt."
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
    // Regelfall: die Ergebnisseite zeigen. Sie enthaelt die Vorschau und
    // darueber die beiden Schaltflaechen - Herunterladen und Weiterleiten.
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

function notifyError(text) {
  try {
    browser.notifications?.create({
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: "Full Page PDF Snap — Fehler",
      message: text
    });
  } catch (_) { /* permission ggf. fehlt */ }
}

function notifyHint(text) {
  try {
    browser.notifications?.create({
      type: "basic",
      iconUrl: browser.runtime.getURL("icons/icon-48.png"),
      title: "Full Page PDF Snap — Hinweis",
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

  browser.menus.create({ id: MENU_IDS.capture, title: "Ganze Seite als PDF speichern", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep1, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.saveAs, type: "checkbox", checked: !!s.saveAs, title: "Speicher-Dialog jedes Mal anzeigen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.afterShow, type: "checkbox", checked: s.afterCapture === "show" || s.afterCapture === "both", title: "Nach Save: Ordner zeigen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.afterOpen, type: "checkbox", checked: s.afterCapture === "open" || s.afterCapture === "both", title: "Nach Save: PDF oeffnen", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.hideSticky, type: "checkbox", checked: !!s.hideSticky, title: "Sticky/Sidebar verstecken", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep2, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.scaleParent, title: "Capture-Qualitaet", contexts: ctx });
  const scale = Number(s.captureScale || 1.0);
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale1, type: "radio", checked: scale === 1.0, title: "1.0x — wie am Bildschirm", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale125, type: "radio", checked: scale === 1.25, title: "1.25x — Balance", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale15, type: "radio", checked: scale === 1.5, title: "1.5x — scharf", contexts: ctx });
  browser.menus.create({ parentId: MENU_IDS.scaleParent, id: MENU_IDS.scale2, type: "radio", checked: scale === 2.0, title: "2.0x — maximal", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.sep4, type: "separator", contexts: ctx });
  browser.menus.create({ id: MENU_IDS.options, title: "Alle Einstellungen…", contexts: ctx });
}

async function applyMenuClick(id, checked) {
  const s = await browser.storage.local.get(DEFAULTS);
  const patch = {};
  switch (id) {
    case MENU_IDS.capture:
      runOnActiveTab().catch(e => { console.error(TAG, e); notifyError(e.message); });
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
});

log("Background ready.");
