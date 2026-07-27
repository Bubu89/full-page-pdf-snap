"use strict";

(function () {
  const TAG = "[PageShot/content]";
  const log = (...a) => console.log(TAG, ...a);

  if (window.__pageShotInjected) {
    log("Already injected — listener active.");
    return;
  }
  window.__pageShotInjected = true;
  log("Injected v1.1.0.");

  const saved = {
    html: { overflow: "", scrollBehavior: "" },
    body: { overflow: "" },
    rootScrollTop: 0,
    windowScrollY: 0,
    windowScrollX: 0,
    stickyChanges: []
  };

  let scrollState = null;

  function findScrollableRoot() {
    const html = document.documentElement;
    const body = document.body;
    const winH = window.innerHeight;
    const se = document.scrollingElement;

    const candidates = [];
    if (se) candidates.push(se);
    if (html && !candidates.includes(html)) candidates.push(html);
    if (body && !candidates.includes(body)) candidates.push(body);

    for (const c of candidates) {
      if (c.scrollHeight > c.clientHeight + 4) {
        log("Scrollable root = window-level (", c.tagName || "scrollingElement", ") scrollH=", c.scrollHeight, " clientH=", c.clientHeight);
        return { root: c, isWindow: true };
      }
    }

    /* Auswahl unter mehreren Scroll-Containern.
     *
     * Der breiteste Bereich ist der Hauptinhalt - eine schmale Navigations-
     * spalte kann laenger scrollen als der Lesebereich, ist aber nie das,
     * was der Nutzer als PDF haben will.
     *
     * Breite allein reicht jedoch nicht: bei verschachtelten Containern ist
     * der aeussere fast genauso breit wie der innere, obwohl der Inhalt im
     * inneren steckt. Darum entscheidet bei aehnlicher Breite (10 % Toleranz)
     * der groessere Scroll-Ueberhang.
     */
    const WIDTH_TOLERANCE = 0.9;

    function isBetter(el, delta, cur, curDelta) {
      if (!cur) return true;
      const w = el.clientWidth, cw = cur.clientWidth;
      if (w > cw / WIDTH_TOLERANCE) return true;    // deutlich breiter gewinnt
      if (w < cw * WIDTH_TOLERANCE) return false;   // deutlich schmaler verliert
      return delta > curDelta;                      // aehnlich breit: mehr Inhalt
    }

    let best = null, bestDelta = 0;
    const all = document.querySelectorAll("*");
    for (const el of all) {
      if (!el || el.clientHeight < winH * 0.5) continue;
      const delta = el.scrollHeight - el.clientHeight;
      if (delta <= 4) continue;
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (!/auto|scroll|overlay/.test(cs.overflowY)) continue;
      if (!isBetter(el, delta, best, bestDelta)) continue;
      best = el; bestDelta = delta;
    }
    if (best) {
      log("Scrollable root = inner container", best.tagName, best.id || "", "delta=", bestDelta);
      return { root: best, isWindow: false };
    }

    log("WARNING: No scrollable container detected. Falling back to window-level.");
    return { root: se || html, isWindow: true };
  }

  function setScrollTop(state, y) {
    const { root, isWindow } = state;
    if (isWindow) {
      try { window.scrollTo({ top: y, left: 0, behavior: "instant" }); }
      catch (_) { try { window.scrollTo(0, y); } catch (_) { /* ignore */ } }
      try { document.documentElement.scrollTop = y; } catch (_) { /* ignore */ }
      try { if (document.body) document.body.scrollTop = y; } catch (_) { /* ignore */ }
      try { if (root && root !== document.documentElement && root !== document.body) root.scrollTop = y; } catch (_) { /* ignore */ }
    } else {
      try { root.scrollTop = y; } catch (_) { /* ignore */ }
      try { root.scrollTo({ top: y, left: 0, behavior: "instant" }); } catch (_) { /* ignore */ }
    }
  }

  function getScrollTop(state) {
    const { root, isWindow } = state;
    if (isWindow) {
      return Math.max(
        window.scrollY || 0,
        document.documentElement.scrollTop || 0,
        document.body ? document.body.scrollTop || 0 : 0
      );
    }
    return root.scrollTop || 0;
  }

  function getTotalHeight(state) {
    const { root, isWindow } = state;
    if (isWindow) {
      return Math.max(
        document.documentElement.scrollHeight,
        document.body ? document.body.scrollHeight : 0,
        document.documentElement.offsetHeight,
        document.body ? document.body.offsetHeight : 0
      );
    }
    return root.scrollHeight;
  }

  function getViewportHeight(state) {
    return state.isWindow ? window.innerHeight : state.root.clientHeight;
  }

  function getViewportWidth(state) {
    return state.isWindow ? window.innerWidth : state.root.clientWidth;
  }

  /* Ausschnitt des Scroll-Containers im Fenster, in CSS-Pixeln.
   *
   * Bei App-Layouts (Gmail, Outlook, Notion) scrollt nicht die Seite, sondern
   * ein inneres Element. Der Screenshot zeigt aber immer das ganze Fenster -
   * also auch Kopfzeile und Seitenleiste, die beim Scrollen stehen bleiben.
   * Ohne Zuschnitt taucht dieser Rahmen in JEDEM Segment erneut auf und
   * zerschneidet den Verlauf.
   *
   * Rueckgabe null bei normalen Seiten: dort ist der ganze Viewport gewollt.
   */
  function computeClipRect(state) {
    if (state.isWindow) return null;
    let r;
    try { r = state.root.getBoundingClientRect(); } catch (_) { return null; }

    const x = Math.max(0, Math.round(r.left));
    const y = Math.max(0, Math.round(r.top));
    const w = Math.round(Math.min(r.width, window.innerWidth - x));
    const h = Math.round(Math.min(r.height, window.innerHeight - y));

    // Unbrauchbar schmale oder hohe Ausschnitte lieber verwerfen als ein
    // kaputtes PDF erzeugen - dann bleibt es beim vollen Viewport.
    if (w < 50 || h < 50) {
      log("Clip verworfen (zu klein):", w, "x", h);
      return null;
    }
    log("Clip auf Scroll-Container:", x, y, w, h);
    return { x, y, w, h };
  }

  /* Hintergrundfarbe fuer die Flaeche, auf der im Kontext-Modus unterhalb des
   * ersten Segments kein Menue mehr gezeichnet wird. Ohne sie entstuende dort
   * ein weisser Block, der bei dunklen Oberflaechen wie ein Fehler wirkt.
   */
  function pageBackgroundColor(state) {
    const opaque = (c) =>
      c && !/^rgba\(0,\s*0,\s*0,\s*0\)$/.test(c) && c !== "transparent";
    const candidates = [state.root, document.body, document.documentElement];
    for (const el of candidates) {
      if (!el) continue;
      try {
        const c = getComputedStyle(el).backgroundColor;
        if (opaque(c)) return c;
      } catch (_) { /* weiter */ }
    }
    return "#ffffff";
  }

  /* Weitere Scroll-Bereiche neben dem Hauptbereich.
   *
   * Bei App-Layouts ist die Seitenleiste oft selbst scrollbar - bei Gmail die
   * Label-Liste. Wird nur der Hauptbereich verfolgt, endet die Seitenleiste im
   * PDF am Ende des ersten Segments, obwohl sie noch Inhalt haette.
   *
   * Erfasst werden nur Bereiche, die neben dem Hauptbereich liegen (nicht
   * darin) und selbst nennenswert scrollen.
   */
  const tagOf = (el) =>
    el.tagName.toLowerCase()
    + (el.id ? "#" + el.id : "")
    + (el.className && typeof el.className === "string"
        ? "." + el.className.trim().split(/\s+/).slice(0, 2).join(".") : "");

  const sideScrollerEls = [];

  function collectSideScrollers(state) {
    sideScrollerEls.length = 0;

    const main = state.root;
    const out = [];

    /* Bei Fenster-Scroll gibt es keinen inneren Hauptbereich, aber sehr wohl
     * scrollbare Navigationsspalten - Dokumentations-Seiten legen ihre
     * Navigation als festes, eigenstaendig scrollendes Element an. Ohne
     * diesen Zweig landet nur der sichtbare Ausschnitt im PDF.
     */
    if (state.isWindow) {
      for (const el of document.querySelectorAll("*")) {
        const delta = el.scrollHeight - el.clientHeight;
        if (delta <= 4) continue;
        let cs;
        try { cs = getComputedStyle(el); } catch (_) { continue; }
        if (cs.position !== "fixed" && cs.position !== "sticky") continue;
        if (!/auto|scroll|overlay/.test(cs.overflowY)) continue;
        let r;
        try { r = el.getBoundingClientRect(); } catch (_) { continue; }
        if (!isSideNavigation(r)) continue;
        if (out.some(o => o.el.contains(el))) continue;
        out.push({
          el,
          x: Math.max(0, Math.round(r.left)), y: Math.max(0, Math.round(r.top)),
          w: Math.round(Math.min(r.width, window.innerWidth - Math.max(0, r.left))),
          h: Math.round(Math.min(r.height, window.innerHeight - Math.max(0, r.top))),
          max: delta
        });
      }
      out.sort((a, b) => b.max - a.max);
      const capped = out.slice(0, 2);
      capped.forEach(o => sideScrollerEls.push(o.el));
      log("Scrollbare Navigationsspalten:",
          capped.map(o => `${tagOf(o.el)} ${o.w}x${o.h} max=${o.max}`).join(" | ") || "keine");
      return capped.map(({ el, ...rest }) => rest);
    }

    const mainRect = main.getBoundingClientRect();

    const rejected = [];   // fuer die Diagnose im Log
    for (const el of document.querySelectorAll("*")) {
      if (el === main || main.contains(el) || el.contains(main)) continue;
      const delta = el.scrollHeight - el.clientHeight;
      // Gleiche Schwelle wie beim Hauptbereich - ein Menue, das nur wenig
      // ueberlaeuft, ist trotzdem unvollstaendig, wenn man es weglaesst.
      if (delta <= 4) continue;
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (!/auto|scroll|overlay/.test(cs.overflowY)) {
        rejected.push(`${tagOf(el)} overflowY=${cs.overflowY} delta=${delta}`);
        continue;
      }

      let r;
      try { r = el.getBoundingClientRect(); } catch (_) { continue; }
      if (r.width < 30 || r.height < 60) {
        rejected.push(`${tagOf(el)} zu klein ${Math.round(r.width)}x${Math.round(r.height)}`);
        continue;
      }
      if (r.bottom <= 0 || r.top >= window.innerHeight) {
        rejected.push(`${tagOf(el)} ausserhalb des Fensters`);
        continue;
      }
      // Ueberlappung mit dem Hauptbereich: nur verwerfen, wenn sie erheblich
      // ist. Bei knappen Randfaellen (Rahmen, Schatten) sonst faelschlich raus.
      const overlap = Math.min(r.right, mainRect.right) - Math.max(r.left, mainRect.left);
      if (overlap > Math.min(r.width, mainRect.width) * 0.25) {
        rejected.push(`${tagOf(el)} ueberlappt Hauptbereich um ${Math.round(overlap)}px`);
        continue;
      }
      // verschachtelte Kandidaten: nur den aeussersten behalten
      if (out.some(o => o.el.contains(el))) continue;

      out.push({
        el,
        x: Math.max(0, Math.round(r.left)),
        y: Math.max(0, Math.round(r.top)),
        w: Math.round(Math.min(r.width, window.innerWidth - Math.max(0, r.left))),
        h: Math.round(Math.min(r.height, window.innerHeight - Math.max(0, r.top))),
        max: delta
      });
    }

    out.sort((a, b) => b.max - a.max);
    const capped = out.slice(0, 2);          // mehr als zwei sind unrealistisch
    capped.forEach(o => sideScrollerEls.push(o.el));
    if (capped.length) {
      log("Weitere Scroll-Bereiche:",
          capped.map(o => `${tagOf(o.el)} ${o.w}x${o.h} bei ${o.x},${o.y} max=${o.max}`).join(" | "));
    } else {
      log("Keine weiteren Scroll-Bereiche gefunden.");
      if (rejected.length) log("  Verworfene Kandidaten:", rejected.slice(0, 8).join(" | "));
    }
    return capped.map(({ el, ...rest }) => rest);
  }

  function measureLayout() {
    scrollState = findScrollableRoot();
    const layout = {
      totalH: getTotalHeight(scrollState),
      viewportH: getViewportHeight(scrollState),
      viewportW: getViewportWidth(scrollState),
      // Fenstermasse getrennt vom Container: der Screenshot bildet immer das
      // Fenster ab, daraus ergibt sich der Skalierungsfaktor.
      winH: window.innerHeight,
      winW: window.innerWidth,
      clip: computeClipRect(scrollState),
      bgColor: pageBackgroundColor(scrollState),
      sideScrollers: collectSideScrollers(scrollState),
      dpr: window.devicePixelRatio || 1,
      isWindow: scrollState.isWindow,
      rootTag: scrollState.root.tagName || "?",
      currentScrollTop: getScrollTop(scrollState),
      // Adaptive: Device-Metriken fuer effektive tilePx-Berechnung im Background
      deviceMemoryGb: navigator.deviceMemory || null,
      cpuCores: navigator.hardwareConcurrency || null,
      screenPxH: window.screen ? window.screen.height * (window.devicePixelRatio || 1) : null,
      screenPxW: window.screen ? window.screen.width * (window.devicePixelRatio || 1) : null
    };
    log("Layout:", layout);
    return layout;
  }

  function freezePage() {
    if (!scrollState) scrollState = findScrollableRoot();
    saved.windowScrollX = window.scrollX;
    saved.windowScrollY = window.scrollY;
    saved.rootScrollTop = getScrollTop(scrollState);

    const html = document.documentElement;
    saved.html.overflow = html.style.overflow;
    saved.html.scrollBehavior = html.style.scrollBehavior;
    saved.body.overflow = document.body ? document.body.style.overflow : "";

    html.style.setProperty("scroll-behavior", "auto", "important");
    if (document.body) document.body.style.setProperty("scroll-behavior", "auto", "important");
    if (!scrollState.isWindow) {
      try { scrollState.root.style.setProperty("scroll-behavior", "auto", "important"); } catch (_) { /* ignore */ }
    }

    setScrollTop(scrollState, 0);
    log("Freeze: saved scrollY=", saved.windowScrollY, " reset to 0. Verify actual=", getScrollTop(scrollState));
  }

  function restorePage() {
    const html = document.documentElement;
    html.style.overflow = saved.html.overflow;
    html.style.scrollBehavior = saved.html.scrollBehavior;
    if (document.body) document.body.style.overflow = saved.body.overflow;
    for (const entry of saved.stickyChanges) {
      try { entry.el.style.visibility = entry.prevVisibility; }
      catch (_) { /* element gone */ }
    }
    saved.stickyChanges.length = 0;
    if (scrollState) setScrollTop(scrollState, saved.rootScrollTop);
    window.scrollTo(saved.windowScrollX, saved.windowScrollY);
    log("Restored.");
  }

  /* Seitliche Navigation von stoerenden Overlays unterscheiden.
   *
   * "Sticky ausblenden" soll Cookie-Banner, Chat-Blasen und mitwandernde
   * Kopfleisten entfernen - die tauchen sonst in jedem Abschnitt erneut auf.
   *
   * Dokumentations-Seiten (VitePress, Docusaurus, MkDocs) legen ihre
   * Navigation aber ebenfalls als position:fixed an. Die pauschal
   * auszublenden loescht Inhalt statt Stoerung: im PDF bleibt links eine
   * leere Spalte.
   *
   * Merkmal einer Navigationsspalte: hoch, schmal und an einem Fensterrand.
   * Banner sind breit und flach, Chat-Blasen klein - beide fallen durch.
   */
  function isSideNavigation(r) {
    const winW = window.innerWidth, winH = window.innerHeight;
    const tall = r.height >= winH * 0.5;
    const narrow = r.width <= winW * 0.4;
    // Toleranz relativ zur Fensterbreite: Layouts mit Aussenabstand haben
    // ihre Navigationsspalte nicht buendig am Rand.
    const edge = Math.max(12, winW * 0.05);
    const atEdge = r.left <= edge || r.right >= winW - edge;
    return tall && narrow && atEdge;
  }

  /* includeSideNav=false: Navigationsspalten bleiben stehen (erstes Segment).
   * includeSideNav=true:  auch sie verschwinden (alle weiteren Segmente).
   *
   * Bei fixem Layout mit Fenster-Scroll wandert die Navigation sonst durch
   * jedes Segment und zerschneidet den Verlauf - genau wie Kopfzeile und
   * Seitenleiste bei App-Layouts. Einmal oben zeigen loest beides.
   */
  function hideStickyAndFixed(includeSideNav) {
    const els = document.querySelectorAll("*");
    const keep = [];
    const candidates = [];

    for (const el of els) {
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (cs.position !== "fixed" && cs.position !== "sticky") continue;
      let r;
      try { r = el.getBoundingClientRect(); } catch (_) { continue; }
      if (!includeSideNav && isSideNavigation(r)) {
        keep.push(el);
        log("Sticky behalten (Navigationsspalte):",
            el.tagName.toLowerCase(), Math.round(r.width) + "x" + Math.round(r.height));
      } else {
        candidates.push(el);
      }
    }

    let n = 0;
    for (const el of candidates) {
      // Was innerhalb einer behaltenen Navigation liegt, bleibt ebenfalls -
      // sonst verschwinden einzelne Bedienelemente aus der Spalte.
      if (keep.some(k => k.contains(el))) continue;
      saved.stickyChanges.push({ el, prevVisibility: el.style.visibility });
      el.style.setProperty("visibility", "hidden", "important");
      n++;
    }
    log("Sticky/fixed ausgeblendet:", n, "| behalten:", keep.length);
  }

  function scrollToYActive(targetY) {
    if (!scrollState) scrollState = findScrollableRoot();
    const start = Date.now();
    const startY = getScrollTop(scrollState);
    const tolerance = 4;
    const maxMs = 2500;

    setScrollTop(scrollState, targetY);

    return new Promise((resolve) => {
      let resolved = false;
      let onScroll = null;

      const detach = () => {
        if (onScroll) {
          try {
            (scrollState.isWindow ? window : scrollState.root)
              .removeEventListener("scroll", onScroll);
          } catch (_) { /* ignore */ }
          onScroll = null;
        }
      };

      const done = (method, extra) => {
        if (resolved) return;
        resolved = true;
        detach();
        const actualY = getScrollTop(scrollState);
        const info = { actualY, method, elapsed: Date.now() - start, startY, targetY, ...(extra || {}) };
        log("scrollTo done:", info);
        resolve(info);
      };

      onScroll = () => {
        const cur = getScrollTop(scrollState);
        if (Math.abs(cur - targetY) <= tolerance) done("scrollEvent");
      };
      try {
        (scrollState.isWindow ? window : scrollState.root)
          .addEventListener("scroll", onScroll, { passive: true });
      } catch (_) { /* ignore */ }

      let pokeCount = 0;
      const tick = () => {
        if (resolved) return;
        const cur = getScrollTop(scrollState);
        if (Math.abs(cur - targetY) <= tolerance) return done("rAFPoll");
        if (Date.now() - start > maxMs) {
          return done("TIMEOUT", { stuck: true, pokeCount });
        }
        if (++pokeCount <= 8) setScrollTop(scrollState, targetY);
        requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    });
  }

  async function probeScroll() {
    if (!scrollState) scrollState = findScrollableRoot();
    const before = getScrollTop(scrollState);
    const target = before + 200;
    setScrollTop(scrollState, target);
    await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
    const after = getScrollTop(scrollState);
    setScrollTop(scrollState, before);
    const moved = Math.abs(after - before) > 4;
    log("Probe scroll: before=", before, "target=", target, "after=", after, "moved=", moved);
    return { before, target, after, moved };
  }

  browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    (async () => {
      try {
        switch (msg.cmd) {
          case "ping":
            sendResponse({ ok: true, injected: true, version: "1.1.0" });
            break;
          case "getLayout":
            sendResponse(measureLayout());
            break;
          case "probe":
            sendResponse(await probeScroll());
            break;
          case "freeze":
            freezePage();
            sendResponse({ ok: true, scrollTop: getScrollTop(scrollState) });
            break;
          case "hideSticky":
            hideStickyAndFixed(!!msg.includeSideNav);
            sendResponse({ ok: true });
            break;
          case "scrollTo": {
            const res = await scrollToYActive(msg.y || 0);
            sendResponse({ ok: true, ...res });
            break;
          }
          case "scrollSide": {
            // Nebenbereich (z.B. Seitenleiste) unabhaengig vom Hauptbereich
            // scrollen, damit auch dessen Inhalt vollstaendig erfasst wird.
            const sideEl = sideScrollerEls[msg.index];
            if (!sideEl) { sendResponse({ ok: false, actualY: 0 }); break; }
            try { sideEl.scrollTop = msg.y; } catch (_) { /* ignore */ }
            sendResponse({ ok: true, actualY: sideEl.scrollTop || 0 });
            break;
          }
          case "currentTotalH":
            sendResponse({ totalH: scrollState ? getTotalHeight(scrollState) : 0 });
            break;
          case "restore":
            restorePage();
            sendResponse({ ok: true });
            break;
          default:
            sendResponse({ ok: false, error: "unknown cmd: " + msg.cmd });
        }
      } catch (e) {
        log("ERROR in handler:", e);
        sendResponse({ ok: false, error: String(e) });
      }
    })();
    return true;
  });
})();
