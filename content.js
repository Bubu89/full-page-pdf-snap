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

    let best = null, bestDelta = 0;
    const all = document.querySelectorAll("*");
    for (const el of all) {
      if (!el || el.clientHeight < winH * 0.5) continue;
      const delta = el.scrollHeight - el.clientHeight;
      if (delta <= 4 || delta <= bestDelta) continue;
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (!/auto|scroll|overlay/.test(cs.overflowY)) continue;
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

  function measureLayout() {
    scrollState = findScrollableRoot();
    const layout = {
      totalH: getTotalHeight(scrollState),
      viewportH: getViewportHeight(scrollState),
      viewportW: getViewportWidth(scrollState),
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

  function hideStickyAndFixed() {
    const els = document.querySelectorAll("*");
    let n = 0;
    for (const el of els) {
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (cs.position === "fixed" || cs.position === "sticky") {
        saved.stickyChanges.push({ el, prevVisibility: el.style.visibility });
        el.style.setProperty("visibility", "hidden", "important");
        n++;
      }
    }
    log("Hidden sticky/fixed:", n);
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
            hideStickyAndFixed();
            sendResponse({ ok: true });
            break;
          case "scrollTo": {
            const res = await scrollToYActive(msg.y || 0);
            sendResponse({ ok: true, ...res });
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
