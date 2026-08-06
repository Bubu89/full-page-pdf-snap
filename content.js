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
      try {
        // Zwei Arten von Eingriff, dieselbe Liste: ausgeblendete Elemente
        // tragen prevVisibility, gelöste Bildlauf-Sperren prevOverflow.
        if (entry.prevOverflow !== undefined) {
          entry.el.style.overflow = entry.prevOverflow;
          entry.el.style.overflowY = entry.prevOverflowY;
          entry.el.style.position = entry.prevPosition;
        } else {
          entry.el.style.visibility = entry.prevVisibility;
        }
      } catch (_) { /* element gone */ }
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
  /* Overlays, die kein "position: fixed" tragen.
   *
   * Zustimmungsdialoge, Anmeldeaufforderungen und Werbeeinblendungen liegen oft
   * als modaler Dialog oder als absolut positionierter Kasten mit hohem
   * Stapelwert über der Seite. Die bisherige Regel griff nur bei fixed und
   * sticky — gemessen an acht Seiten blieben dadurch zwei von sechs Overlays
   * stehen, eines davon über dem gesamten Sichtfenster.
   *
   * Entschieden wird nach Bauart, nicht nach Namenslisten: was sich selbst als
   * Dialog ausweist, oder was hoch gestapelt ist, positioniert ist und einen
   * erheblichen Teil des Fensters deckt. Eine Namensliste müsste gepflegt
   * werden und wäre an dem Tag falsch, an dem eine Seite ihre Klassen umbenennt.
   */
  function isBlockingOverlay(el, cs, r) {
    try {
      if (el.matches("dialog[open],[role=dialog],[aria-modal=true]")) return true;
    } catch (_) { /* ungueltiger Selektor kommt vor */ }
    if (!/fixed|sticky|absolute/.test(cs.position)) return false;
    const z = parseInt(cs.zIndex, 10);
    if (!Number.isFinite(z) || z < 100) return false;
    const anteil = (r.width * r.height) / (window.innerWidth * window.innerHeight);
    if (anteil < 0.12 || r.width < 120 || r.height < 60) return false;

    // Was den Text der Seite trägt, ist der Inhalt — auch wenn es hoch
    // gestapelt und absolut positioniert ist. Ohne diese Bremse blendete die
    // Regel bei zeit.de den Hauptcontainer aus und die Seitenhöhe fiel von
    // 48.437 auf 900 Pixel: aus einer Störungsbereinigung wurde Datenverlust.
    const gesamt = (document.body.innerText || "").length;
    const eigener = (el.innerText || "").length;
    if (gesamt > 400 && eigener / gesamt > 0.25) return false;

    // Ebenso: was höher ist als das Fenster, wird gescrollt und ist damit
    // Inhalt, kein Overlay. Zustimmungsdialoge passen auf einen Bildschirm.
    return r.height <= window.innerHeight * 1.5;
  }

  /* Sperre des Bildlaufs aufheben.
   *
   * Zustimmungsdialoge setzen dem Dokument häufig "overflow: hidden", damit
   * dahinter nicht weitergelesen wird. Für eine Aufnahme der ganzen Seite ist
   * das kein Schönheitsfehler, sondern der Grund, warum sie nach dem ersten
   * Bildschirm abbricht: gemessen an acht Seiten war bei vier der Bildlauf
   * gesperrt, darunter eine ohne jedes erkennbare Overlay.
   */
  function releaseScrollLock() {
    for (const el of [document.documentElement, document.body]) {
      if (!el) continue;
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      if (!/hidden|clip/.test(cs.overflow + " " + cs.overflowY)) continue;
      saved.stickyChanges.push({ el, prevOverflow: el.style.overflow,
                                 prevOverflowY: el.style.overflowY,
                                 prevPosition: el.style.position });
      el.style.setProperty("overflow", "visible", "important");
      el.style.setProperty("overflow-y", "visible", "important");
      // Manche Seiten fixieren zusätzlich die Position des Körpers.
      if (cs.position === "fixed") el.style.setProperty("position", "static", "important");
      log("Bildlauf-Sperre aufgehoben an", el.tagName.toLowerCase());
    }
  }

  function hideStickyAndFixed(includeSideNav) {
    releaseScrollLock();
    const els = document.querySelectorAll("*");
    const keep = [];
    const candidates = [];

    for (const el of els) {
      let cs;
      try { cs = getComputedStyle(el); } catch (_) { continue; }
      let r;
      try { r = el.getBoundingClientRect(); } catch (_) { continue; }
      const fixiert = cs.position === "fixed" || cs.position === "sticky";
      if (!fixiert && !isBlockingOverlay(el, cs, r)) continue;
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


  /* Sammelt jedes sichtbare Wort mit seiner Lage auf der Seite.
   *
   * Grundlage fuer die Textebene im PDF: Der Text stammt aus dem Dokument
   * selbst, nicht aus einer Erkennung des Bildes. Gemessen an einer echten
   * Seite liegt der Wort-Recall damit bei 100 % gegen 92,6 % bei OCR — es
   * wird nichts erkannt, sondern abgelesen.
   *
   * Ein Range je Wort, weil ein umbrechender Textknoten nur Zeilenkaesten
   * kennt: Wo genau ein Wort in der Zeile sitzt, weiss nur der Range.
   * Kosten an der Messseite: 14 ms fuer 1068 Woerter.
   */

  /* Sammelt die Verweise der Seite mit ihrer Lage und ihrer Rolle.
   *
   * Ein Agent mit Auftrag braucht nicht alle Adressen, sondern die richtige.
   * Eine Liste von 1.528 Verweisen beantwortet "finde das Impressum" so wenig
   * wie gar keine. Gemessen am 6. August 2026: Auf einer Enzyklopaedie-Seite
   * gehoeren 741 von 1.528 Verweisen zum Seitengeruest — fast die Haelfte
   * laesst sich vorab ausschliessen, wenn man weiss, welche das sind.
   *
   * Die Rolle kommt aus vier Quellen, in dieser Reihenfolge: was das Dokument
   * selbst auszeichnet (nav, footer, main, role=), wie der Verweis heisst
   * (weiter, zurueck), wo er liegt, und ob er nur springt. Was sich nicht
   * zuordnen laesst, bekommt null — geraten wird nicht.
   *
   * Der letzte Punkt ist der Grund, warum das hier steht und nicht in einem
   * Crawler: Ein Behoerdenportal in der Probe trug KEINE einzige Landmarke.
   * Dort bleibt nur die Lage, und die kennt nur, wer die Seite gerendert hat.
   */
  function collectLinks() {
    const BLAETTERN = /^(next|prev|previous|weiter|zurück|zurueck|nächste|vorige|»|«|›|‹|\d{1,3})$/i;

    function rolleVon(a, kasten, seiteH) {
      const rel = (a.getAttribute("rel") || "").toLowerCase();
      if (rel === "next" || rel === "prev") return "blaettern";
      for (let el = a; el && el !== document.body; el = el.parentElement) {
        const tag = el.tagName;
        const ro = (el.getAttribute("role") || "").toLowerCase();
        if (tag === "NAV" || ro === "navigation") return "navigation";
        if (tag === "FOOTER" || ro === "contentinfo") return "fusszeile";
        if (tag === "HEADER" || ro === "banner") return "kopfzeile";
        if (tag === "ASIDE" || ro === "complementary") return "randspalte";
        if (tag === "MAIN" || ro === "main" || tag === "ARTICLE") return "inhalt";
      }
      const txt = (a.textContent || "").trim();
      if (BLAETTERN.test(txt)) return "blaettern";
      if ((a.getAttribute("href") || "").startsWith("#")) return "sprungmarke";
      // Nur wenn das Dokument nichts hergibt: die Lage. Als solche benannt,
      // damit ein Aufrufer den schwaecheren Beleg erkennt.
      if (kasten.y < 200) return "kopfbereich?";
      if (kasten.y > seiteH - 400) return "fussbereich?";
      return null;
    }

    const seiteH = document.documentElement.scrollHeight;
    const eigenerHost = location.host;
    const links = [];
    for (const a of document.querySelectorAll("a[href]")) {
      const st = getComputedStyle(a);
      if (st.visibility === "hidden" || st.display === "none" || +st.opacity === 0)
        continue;
      const k = a.getBoundingClientRect();
      if (k.width < 2 || k.height < 2) continue;
      const ziel = a.href;
      if (!/^https?:/i.test(ziel)) continue;
      let host = "";
      try { host = new URL(ziel).host; } catch (_) { continue; }
      links.push({
        rolle: rolleVon(a, k, seiteH),
        text: (a.textContent || "").trim().replace(/\s+/g, " ").slice(0, 120),
        href: ziel,
        x: Math.round(k.x + scrollX), y: Math.round(k.y + scrollY),
        w: Math.round(k.width), h: Math.round(k.height),
        intern: host === eigenerHost,
        beschriftung: a.getAttribute("aria-label") || a.getAttribute("title") || "",
      });
      if (links.length > 4000) break;   // Reissleine wie bei der Textebene
    }
    // Die gemeldete Dokumenthoehe enthaelt nicht zwingend alle Elemente:
    // gemessen am 6. August 2026 nennt eine Enzyklopaedie-Seite 24.784 px,
    // waehrend ihr tiefster Verweis bei 27.694 liegt — 384 Verweise einer
    // aufgeklappten Navigationsbox ragen darueber hinaus. Wer die Karte
    // gegen das Bild legt, braucht die Hoehe, die alle Koordinaten umfasst.
    let tiefster = seiteH;
    for (const l of links) tiefster = Math.max(tiefster, l.y + l.h);
    return {
      ok: true,
      seite: {
        w: document.documentElement.scrollWidth,
        h: tiefster,
        dokumentHoehe: seiteH,
        ueberhang: tiefster - seiteH,
      },
      links,
    };
  }

  function collectText() {
    const raus = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEXTAREA", "SVG", "CANVAS"]);
    const geher = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(n) {
        if (!n.nodeValue || !n.nodeValue.trim()) return NodeFilter.FILTER_REJECT;
        const el = n.parentElement;
        if (!el || raus.has(el.tagName)) return NodeFilter.FILTER_REJECT;
        const st = getComputedStyle(el);
        if (st.visibility === "hidden" || st.display === "none" || +st.opacity === 0)
          return NodeFilter.FILTER_REJECT;
        return NodeFilter.FILTER_ACCEPT;
      },
    });

    const woerter = [];
    const bereich = document.createRange();
    let n;
    while ((n = geher.nextNode())) {
      const st = getComputedStyle(n.parentElement);
      const groesse = parseFloat(st.fontSize) || 12;
      const re = /\S+/g;
      let m;
      while ((m = re.exec(n.nodeValue)) !== null) {
        try {
          bereich.setStart(n, m.index);
          bereich.setEnd(n, m.index + m[0].length);
        } catch (_) { continue; }
        const kaesten = bereich.getClientRects();
        if (!kaesten.length) continue;
        // Ein sehr langes Wort kann selbst umbrechen; dann den breitesten
        // Kasten nehmen, sonst rutscht es an den Zeilenanfang.
        let b = kaesten[0];
        for (const r of kaesten) if (r.width > b.width) b = r;
        if (b.width < 0.5 || b.height < 0.5) continue;
        woerter.push({
          t: m[0],
          x: b.x + scrollX, y: b.y + scrollY,
          w: b.width, h: b.height, s: groesse,
        });
        if (woerter.length > 60000) break;   // Reissleine bei absurd langen Seiten
      }
      if (woerter.length > 60000) break;
    }
    // Unteilbare Bloecke fuer den Seitenumbruch: eine Abbildung oder Tabelle
    // mitten durchzuschneiden ist derselbe Fehler wie eine zerschnittene
    // Textzeile, aber Textknoten erfassen sie nicht. Sehr kleine Elemente
    // (Symbole, Zaehlpixel) bleiben draussen — sie stehen ohnehin innerhalb
    // einer Zeile und wuerden nur Luecken verstellen.
    const bloecke = [];
    document.querySelectorAll("img,table,figure,pre,svg,video,iframe").forEach(el => {
      const st = getComputedStyle(el);
      if (st.display === "none" || st.visibility === "hidden") return;
      const b = el.getBoundingClientRect();
      if (b.width < 24 || b.height < 24) return;
      bloecke.push({ a: b.y + scrollY, b: b.y + b.height + scrollY });
    });

    return {
      ok: true,
      woerter,
      bloecke,
      seite: {
        w: document.documentElement.scrollWidth,
        h: document.documentElement.scrollHeight,
      },
    };
  }

  // =====================================================================
  // Quellenangaben
  //
  // Gelesen wird ausschliesslich die Seite, die ohnehin im Browser steht —
  // kein zusaetzlicher Abruf, kein Dienst wird befragt. Das ist keine
  // Sparmassnahme: ein Aufruf bei einem Zitationsdienst wuerde diesem
  // verraten, welche Arbeit gerade gelesen wird, und das Versprechen der
  // Erweiterung brechen, keine Netzverbindung aufzubauen.
  //
  // Gemessen an sechs Wissenschaftsseiten (arXiv, Springer, PMC, PLOS,
  // MDPI, Wikipedia): fuenf liefern die vollstaendige Zitation ueber
  // citation_*-Angaben im Seitenkopf. Ein Abruf haette nichts ergaenzt.
  // =====================================================================

  function sammleQuelle() {
    const meta = {};
    document.querySelectorAll("meta[name],meta[property]").forEach(e => {
      const n = (e.getAttribute("name") || e.getAttribute("property") || "").toLowerCase();
      const v = (e.getAttribute("content") || "").trim();
      if (!n || !v) return;
      (meta[n] = meta[n] || []).push(v);
    });
    const erste = (...k) => { for (const x of k) if (meta[x] && meta[x][0]) return meta[x][0]; return ""; };
    const alle = (...k) => { for (const x of k) if (meta[x] && meta[x].length) return meta[x].slice(); return []; };

    // schema.org: nur als Rueckfallebene. Verlagsseiten sind dort oft
    // ungenauer als in den citation_-Angaben.
    let ld = {};
    document.querySelectorAll('script[type="application/ld+json"]').forEach(s => {
      try {
        const j = JSON.parse(s.textContent);
        for (const o of (Array.isArray(j) ? j : [j])) {
          const t = String(o["@type"] || "");
          // Auch Videos, Datensaetze und Berichte zaehlen — sie werden
          // zitiert wie alles andere, tragen aber keine citation_-Felder.
          // WebPage und Organization bleiben draussen: sie beschreiben die
          // Website, nicht das Werk.
          if (/Article|Book|Thesis|Chapter|Posting|VideoObject|Dataset|Report|Course|Map|SoftwareSource/i.test(t) &&
              !ld["@type"]) ld = o;
        }
      } catch (_) { /* fehlerhaftes JSON-LD ist haeufig und kein Grund aufzugeben */ }
    });
    const ldAutor = () => {
      const a = ld.author;
      if (!a) return [];
      return (Array.isArray(a) ? a : [a])
        .map(x => (typeof x === "string" ? x : (x && x.name) || "")).filter(Boolean);
    };

    // Ein Jahr steht in ganz unterschiedlichen Formaten; die vier Ziffern
    // sind der einzige Teil, der sich zuverlaessig herausloesen laesst.
    const rohDatum = erste("citation_publication_date", "citation_date", "citation_cover_date",
                           "citation_online_date", "prism.publicationdate", "dc.date",
                           "dcterms.issued", "article:published_time", "datepublished") ||
                     (ld.datePublished || "");
    const jahr = (String(rohDatum).match(/\b(1[5-9]\d{2}|20\d{2})\b/) || [""])[0];

    // DOI: aus den Angaben, sonst aus der Adresse. Nicht aus dem Fliesstext —
    // dort steht oft die DOI einer zitierten Arbeit, nicht die dieser Seite.
    let doi = erste("citation_doi", "prism.doi", "dc.identifier.doi", "doi").replace(/^doi:\s*/i, "");
    if (!doi) {
      // Aus der Adresse geraten wird nur der DOI-Kern. Verlagsseiten haengen
      // Wegstuecke an ("/full", "/abstract", "/pdf"), die nicht zur DOI
      // gehoeren — mit ihnen loest sie nicht auf, und eine falsche DOI im
      // Literaturverzeichnis ist schaedlicher als gar keine.
      const m = location.href.match(/\b10\.\d{4,9}\/[-._;()A-Za-z0-9]+/);
      if (m) doi = m[0].replace(/[.,;)]+$/, "");
    }

    let autoren = alle("citation_author", "dc.creator", "dcterms.creator", "author",
                       "citation_authors", "article:author");
    // twitter:creator/site bewusst NICHT: das ist ein Kanalname, kein Verfasser.
    // ResearchGate lieferte darüber "@ResearchGate" als Autor einer Diskussion —
    // im Literaturverzeichnis eine Falschangabe, gemeldet am 03.08.2026.
    if (autoren.length === 1 && /;/.test(autoren[0])) autoren = autoren[0].split(";");
    // Leere Namen aussortieren: eine Zeitschrift lieferte content=";;;;;",
    // was sechs leere Verfasser ergab, die als vollständige Angabe galten.
    autoren = autoren.map(s => String(s).trim())
      // Ein führendes @ macht aus dem Wert einen Kontonamen. Als Verfasser
      // taugt er nicht, und ihn stillschweigend zu entstellen wäre schlechter,
      // als ihn wegzulassen.
      .filter(s => s.length > 1 && !/^@/.test(s));
    if (!autoren.length) autoren = ldAutor();

    // Der uebergeordnete Titel — Zeitschrift, Sammelband oder Tagungsband.
    // Getrennt gehalten, weil davon die Art der Quelle abhaengt: dieselbe
    // Seitenangabe bedeutet bei einer ISBN ein Kapitel und bei einer ISSN
    // einen Aufsatz.
    const buchTitel = erste("citation_inbook_title", "citation_book_title",
                            "citation_series_title");
    const tagung = erste("citation_conference_title", "citation_conference");
    const journal = erste("citation_journal_title", "prism.publicationname", "dc.source") ||
                    buchTitel || tagung;
    const q = {
      titel: erste("citation_title", "dc.title", "dcterms.title", "og:title") ||
             (ld.headline || "") || document.title || "",
      autoren: autoren,
      jahr: jahr,
      datum: String(rohDatum || ""),
      journal: journal,
      band: erste("citation_volume", "prism.volume"),
      heft: erste("citation_issue", "prism.number"),
      seiteVon: erste("citation_firstpage", "prism.startingpage"),
      seiteBis: erste("citation_lastpage", "prism.endingpage"),
      doi: doi,
      issn: erste("citation_issn", "prism.issn", "citation_eissn"),
      isbn: erste("citation_isbn"),
      verlag: erste("citation_publisher", "dc.publisher", "citation_dissertation_institution",
                    "citation_technical_report_institution"),
      webseite: erste("og:site_name") || location.hostname.replace(/^www\./, ""),
      sprache: erste("citation_language", "dc.language") ||
               (document.documentElement.lang || "").split("-")[0],
      url: location.href.split("#")[0],
      abrufdatum: new Date().toISOString().slice(0, 10),
      pdfUrl: erste("citation_pdf_url"),
    };

    // --- Angaben, die den Nachweis tragen ------------------------------
    // Ein Beleg muss sagen, was wann unter welcher Adresse stand. Datum
    // allein genuegt dafuer nicht: Seiten aendern sich im Lauf eines Tages.
    const jetzt = new Date();
    const vz = -jetzt.getTimezoneOffset();
    const zwei = n => String(Math.floor(Math.abs(n))).padStart(2, "0");
    q.abrufzeit = jetzt.getFullYear() + "-" + zwei(jetzt.getMonth() + 1) + "-" + zwei(jetzt.getDate()) +
      " " + zwei(jetzt.getHours()) + ":" + zwei(jetzt.getMinutes()) + ":" + zwei(jetzt.getSeconds()) +
      " " + (vz < 0 ? "-" : "+") + zwei(vz / 60) + ":" + zwei(vz % 60);
    q.zeitzone = (Intl.DateTimeFormat().resolvedOptions() || {}).timeZone || "";

    // Die kanonische Adresse ist die zitierfaehige. Die Adresszeile traegt
    // oft Sitzungs- und Kampagnenparameter, die niemanden weiterfuehren und
    // in einem Literaturverzeichnis nichts verloren haben.
    const kanon = document.querySelector('link[rel="canonical"]');
    q.urlKanonisch = (kanon && kanon.href) || erste("og:url") || "";
    if (q.urlKanonisch && q.urlKanonisch !== q.url) q.urlZitat = q.urlKanonisch;
    else q.urlZitat = q.url.replace(/([?&])(utm_[^&]*|fbclid=[^&]*)(&|$)/g, "$1").replace(/[?&]$/, "");

    // Eine Fassungsadresse zeigt genau den Stand, der gesehen wurde. Wo eine
    // Seite sie anbietet, ist sie dem wandernden Link vorzuziehen.
    const permalink = document.querySelector('link[rel="bookmark"], #t-permalink a, link[rel="alternate"][type="text/html"][hreflang]');
    q.fassung = (permalink && permalink.href) || "";
    if (!q.fassung) {
      const old = location.href.match(/[?&]oldid=\d+/);
      if (old) q.fassung = q.url;
    }

    // document.lastModified liefert bei dynamisch erzeugten Seiten den
    // Zeitpunkt des Seitenaufbaus — also praktisch "jetzt". Als Angabe
    // "zuletzt geaendert" waere das eine Falschaussage. Deshalb zaehlt es
    // nur, wenn es erkennbar aelter ist als der Abruf.
    q.geaendert = erste("article:modified_time", "dcterms.modified", "citation_online_date",
                        "last-modified", "og:updated_time") ||
                  (ld.dateModified || "");
    if (!q.geaendert && document.lastModified) {
      const lm = new Date(document.lastModified);
      if (!isNaN(lm) && (jetzt - lm) > 3600e3) q.geaendert = lm.toISOString();
    }
    // Lizenz: entscheidet, ob und wie weiterverwendet werden darf.
    const lizLink = document.querySelector('a[rel~="license"], link[rel~="license"]');
    q.lizenz = erste("dc.rights", "dcterms.license", "citation_license", "og:license") ||
               (typeof ld.license === "string" ? ld.license : (ld.license && ld.license.url) || "") ||
               (lizLink && (lizLink.href || lizLink.textContent.trim())) || "";

    // Volltext-Adressen des Verlags, sofern angegeben. Nur die Angabe —
    // ob etwas geholt wird, entscheidet die Einstellung, nicht diese Stelle.
    q.dateien = [];
    const anhaengen = (art, adresse) => {
      if (!adresse) return;
      try { adresse = new URL(adresse, location.href).href; } catch (_) { return; }
      if (!/^https?:/i.test(adresse)) return;
      if (q.dateien.some(d => d.url === adresse)) return;
      q.dateien.push({ art: art, url: adresse });
    };
    anhaengen("pdf", erste("citation_pdf_url"));
    anhaengen("xml", erste("citation_xml_url", "citation_fulltext_xml_url"));
    anhaengen("html", erste("citation_fulltext_html_url", "citation_abstract_html_url"));
    if (!q.dateien.length && /\.pdf($|\?)/i.test(location.href)) anhaengen("pdf", location.href);
    q.seitenTitel = document.title || "";

    // Woher die Angaben stammen, gehoert dazu: eine Zitation aus dem
    // Seitentitel ist etwas anderes als eine aus Verlagsangaben, und wer
    // sie uebernimmt, sollte den Unterschied sehen.
    const highwire = Object.keys(meta).some(k => k.indexOf("citation_") === 0);
    q.herkunft = highwire ? "Verlagsangaben der Seite (citation_*)"
               : Object.keys(meta).some(k => k.indexOf("dc.") === 0) ? "Dublin-Core-Angaben der Seite"
               : ld["@type"] ? "schema.org-Angaben der Seite"
               : "Seitentitel und Adresse";
    // Ohne Titel ist nichts zu zitieren; ohne Verfasser oder Jahr ist die
    // Angabe unvollstaendig, aber als Internetquelle noch brauchbar.
    // Fehlerseiten und Zugangsschranken sehen fuer den Auslesevorgang aus wie
    // gewoehnliche Seiten — sie haben einen Titel und eine Adresse. Aus
    // "Just a moment..." oder "404 Not found" darf aber keine Quellenangabe
    // werden. Erkannt wird das am Titel und an der Duennheit der Seite; wo es
    // zutrifft, wird die Angabe als unbrauchbar gekennzeichnet.
    // Titel bereinigen und beurteilen, BEVOR die Warnung gesetzt wird.
    // Zuvor standen diese Deklarationen darunter: die Warnungspruefung griff
    // auf sie zu, bevor sie existierten, und brach mit einem ReferenceError ab.
    // Der Listener fing ihn ab — dadurch lieferte collectSource in der
    // Erweiterung ueberhaupt nichts, ohne dass es auffiel.
    const seitenName = erste("og:site_name");
    // Der Name der Website steht vor der Endung, nicht am Anfang: bei
    // "de.wikipedia.org" ist der erste Teil die Sprache.
    const teile = location.hostname.split(".");
    const kern = teile.length > 1 ? teile[teile.length - 2] : teile[0];
    q.titel = q.titel.replace(/^[\s|–—-]+|[\s|–—-]+$/g, "").trim();
    // Bleibt nach der Bereinigung nur der Name der Website stehen, ist das
    // kein Werktitel — bioRxiv liefert "| bioRxiv".
    const nurSeitenname = q.titel.toLowerCase() === (seitenName || "").trim().toLowerCase() ||
                          q.titel.toLowerCase() === (kern || "").toLowerCase();
    // Ein Titel aus lauter Ziffern ist eine Datensatznummer, kein Werktitel.
    const nurNummer = /^[\d\s.,;:\/-]{1,24}$/.test(q.titel.trim());
    // Titel, der eine Kennung statt eines Werktitels trägt: korrekt
    // wiedergegeben, aber als Literaturhinweis schwer benutzbar. Benannt,
    // nicht korrigiert — eine Korrektur wäre geraten.
    if (!nurNummer && /\b(10\.\d{4,9}\/|[A-Za-z]+ID:|accession)/i.test(q.titel)) {
      q.titelHinweis = "Der Titel enthält eine Kennung statt einer Bezeichnung — vor dem Zitieren am Werk prüfen.";
    }
    q.warnung = "";
    // Zwei Gruppen: eindeutige Schranken-Formulierungen dürfen überall im
    // Titel stehen ("Making sure you're not a bot!" kam am 02.08.2026 durch
    // ein Muster durch, das nur den Anfang prüfte), generische Wörter nur am
    // Anfang — "Error Analysis in Second Language Acquisition" ist ein
    // Fachtitel und keine Fehlerseite.
    const eindeutig = /(just a moment|attention required|access denied|checking your browser|are you (a )?(robot|human)|not a bot|verify you are (human|not)|security check required|please enable javascript)/i;
    const generisch = /^\W*(40[0-9]|41[0-9]|50[0-9]|not found|page not found|forbidden|unauthorized|zugriff verweigert|seite nicht gefunden|bitte bestätigen)\b/i;
    // "Error" allein sagt nichts: "Error Analysis in Second Language
    // Acquisition" ist ein Fachtitel. Erst was darauf folgt entscheidet.
    const fehlerwort = /^\W*error\s*(\d{3}|page|occurred|has occurred|[:.–—-]|$)/i;
    if (nurSeitenname || nurNummer) {
      q.warnung = "Als Titel steht nur der Name der Website oder eine bloße Datensatznummer da, kein Werktitel.";
    } else if (eindeutig.test(q.titel) || generisch.test(q.titel.trim()) || fehlerwort.test(q.titel.trim())) {
      q.warnung = "Die Seite sieht nach Fehlermeldung oder Zugangsschranke aus, nicht nach Inhalt.";
    } else if (!autoren.length && !q.journal && !q.verlag &&
               (document.body.innerText || "").trim().length < 600) {
      q.warnung = "Sehr wenig Text und keine Verlagsangaben — moeglicherweise eine Zwischenseite.";
    }

    // Die Vollstaendigkeit wird erst nach der Art bestimmt — dort werden bei
    // manchen Quellenarten Verfasser und Jahr noch ergaenzt.
    // Die Art bestimmt, wie zitiert wird. Entschieden wird nach dem
    // eindeutigsten vorliegenden Merkmal, nicht nach dem erstbesten:
    // eine ISBN weist einen Sammelband aus, auch wenn die Seite daneben
    // ein Feld fuer Zeitschriftentitel gefuellt hat — Repositorien tun das
    // regelmaessig. Eine ISSN gibt es nur bei Periodika.
    const ldTyp = String(ld["@type"] || "");
    q.art =
        meta["citation_dissertation_institution"] ? "Hochschulschrift"
      : tagung ? "Konferenzbeitrag"
      : (q.isbn && (q.seiteVon || buchTitel)) ? "Buchkapitel"
      : q.isbn ? "Buch"
      : (q.issn || erste("citation_journal_title", "prism.publicationname"))
          ? "Zeitschriftenaufsatz"
      : (meta["citation_arxiv_id"] || /arxiv\.org|biorxiv|medrxiv|ssrn|psyarxiv|preprints\.org|osf\.io/i.test(q.url))
          ? "Preprint"
      : /VideoObject/i.test(ldTyp) ? "Video"
      : /(^|[^a-z])Dataset/i.test(ldTyp) ? "Datensatz"
      : /Report/i.test(ldTyp) ? "Bericht"
      : "Internetquelle";
    if (q.art === "Buchkapitel" || q.art === "Konferenzbeitrag") {
      q.sammelwerk = buchTitel || tagung || q.journal;
    }
    if (q.art === "Preprint" && !q.verlag) {
      q.verlag = meta["citation_arxiv_id"] ? "arXiv" : q.webseite;
    }
    if (q.art === "Hochschulschrift" && !q.verlag) {
      q.verlag = erste("citation_dissertation_institution");
    }
    // Video: Urheber ist der Kanal, Datum das Hochladedatum. Beides steht
    // nicht in den citation_-Feldern, die es hier nicht gibt.
    if (q.art === "Video") {
      if (!q.autoren.length) {
        const kanal = document.querySelector('link[itemprop="name"], span[itemprop="author"] link[itemprop="name"]');
        const name = (kanal && kanal.getAttribute("content")) ||
                     (ld.author && (ld.author.name || ld.author)) || "";
        if (name) q.autoren = [String(name)];
      }
      if (!q.jahr) {
        const hoch = String(ld.uploadDate || erste("uploaddate") || "");
        const j = hoch.match(/\b(19|20)\d{2}\b/);
        if (j) { q.jahr = j[0]; q.datum = hoch; }
      }
      if (!q.verlag) q.verlag = q.webseite;
    }

    // Körperschaft als Urheber. Bei Behörden-, Statistik- und Rechtsquellen
    // gibt es keine Person, und das ist kein Mangel: nach APA ist dort die
    // herausgebende Einrichtung der Urheber. Ohne diese Regel blieben
    // amtliche Quellen unvollständig, obwohl die Angabe vorliegt.
    if (!q.autoren.length && !q.doi) {
      const koerper =
        (ld.publisher && (ld.publisher.name || (typeof ld.publisher === "string" ? ld.publisher : ""))) ||
        erste("og:site_name", "dc.publisher", "publisher");
      if (koerper && String(koerper).trim().length > 1) {
        q.autoren = [String(koerper).trim()];
        q.koerperschaft = true;
      }
    }

    q.vollstaendig = !q.warnung &&
      !!(q.titel && (q.autoren.length || q.verlag) && q.jahr);
    // Seitentitel tragen oft den Namen der Website als Anhaengsel
    // ("Sexualtherapie – Wikipedia"). Abgeschnitten wird nur, wenn der
    // Rest woertlich dem angegebenen Seitennamen entspricht — sonst waere
    // es geraten, und ein verstuemmelter Titel ist schlimmer als ein langer.
    const m = q.titel.match(/^(.*?)\s*[|–—-]\s*([^|–—-]+)$/);
    // Mindestlänge, sonst bleibt nichts übrig: bioRxiv liefert "| bioRxiv"
    // als Titel, und ohne die Prüfung entstünde ein leerer Titel mit
    // angehängtem Seitennamen — schlechter als der Rohwert.
    if (m && m[1].trim().length >= 3) {
      const schwanz = m[2].trim().toLowerCase();
      if (schwanz === (seitenName || "").trim().toLowerCase() ||
          schwanz === (kern || "").toLowerCase()) {
        q.titel = m[1].trim();
      }
    }
    return { ok: true, quelle: q };
  }

  /* Bereich mit der Maus aufziehen.
   *
   * Die Auswahl liegt in einem eigenen Overlay ueber der Seite, nicht in ihr:
   * so kann kein Klick versehentlich einen Link der Seite ausloesen, und der
   * Zustand der Seite bleibt unberuehrt. Zurueckgegeben werden Fensterkoordinaten
   * in CSS-Pixeln — der Aufrufer rechnet sie in Geraetepixel um, weil nur er die
   * Skalierung der Aufnahme kennt.
   *
   * Abbruch ist ausdruecklich vorgesehen: Esc, rechte Maustaste, oder ein Zug,
   * der zu klein zum Ablesen waere. Ein Werkzeug, das den Nutzer in eine
   * angefangene Auswahl einsperrt, ist schlimmer als eines ohne Auswahl.
   */
  function selectRegion(hinweisText) {
    return new Promise((fertig) => {
      const zIndex = 2147483647;
      const huelle = document.createElement("div");
      huelle.style.cssText =
        "position:fixed;inset:0;z-index:" + zIndex + ";cursor:crosshair;" +
        "background:rgba(17,24,39,.34);";
      const kasten = document.createElement("div");
      kasten.style.cssText =
        "position:fixed;border:2px solid #2563eb;background:rgba(37,99,235,.14);" +
        "box-shadow:0 0 0 9999px rgba(17,24,39,.34);pointer-events:none;display:none;";
      const masse = document.createElement("div");
      masse.style.cssText =
        "position:fixed;padding:3px 7px;border-radius:4px;background:#111827;color:#fff;" +
        "font:12px/1.3 system-ui,sans-serif;pointer-events:none;display:none;white-space:nowrap;";
      const hinweis = document.createElement("div");
      hinweis.textContent = hinweisText || "Drag to select an area · Esc cancels";
      hinweis.style.cssText =
        "position:fixed;left:50%;top:18px;transform:translateX(-50%);padding:7px 14px;" +
        "border-radius:6px;background:#111827;color:#fff;font:13px/1.3 system-ui,sans-serif;" +
        "pointer-events:none;box-shadow:0 2px 10px rgba(0,0,0,.3);";
      huelle.append(kasten, masse, hinweis);
      document.documentElement.appendChild(huelle);

      let startX = 0, startY = 0, zieht = false;
      const rechteck = (e) => {
        const x = Math.min(startX, e.clientX), y = Math.min(startY, e.clientY);
        const w = Math.abs(e.clientX - startX), h = Math.abs(e.clientY - startY);
        return { x, y, w, h };
      };
      const zeichnen = (r) => {
        kasten.style.display = "block";
        kasten.style.left = r.x + "px"; kasten.style.top = r.y + "px";
        kasten.style.width = r.w + "px"; kasten.style.height = r.h + "px";
        masse.style.display = "block";
        masse.textContent = Math.round(r.w) + " × " + Math.round(r.h);
        // Das Massband bleibt im Fenster, auch wenn am oberen Rand gezogen wird.
        masse.style.left = Math.min(r.x, window.innerWidth - 90) + "px";
        masse.style.top = (r.y > 30 ? r.y - 26 : r.y + r.h + 8) + "px";
      };
      const aufraeumen = () => {
        window.removeEventListener("keydown", beiTaste, true);
        try { huelle.remove(); } catch (_) { /* schon fort */ }
      };
      const beenden = (ergebnis) => { aufraeumen(); fertig(ergebnis); };
      const beiTaste = (e) => {
        if (e.key === "Escape") { e.preventDefault(); e.stopPropagation(); beenden(null); }
      };

      huelle.addEventListener("mousedown", (e) => {
        if (e.button !== 0) { beenden(null); return; }   // rechte Taste bricht ab
        e.preventDefault();
        zieht = true; startX = e.clientX; startY = e.clientY;
        hinweis.style.display = "none";
      });
      huelle.addEventListener("mousemove", (e) => { if (zieht) zeichnen(rechteck(e)); });
      huelle.addEventListener("mouseup", (e) => {
        if (!zieht) return;
        const r = rechteck(e);
        // Ein Zug unter 12 Pixeln war ein Klick, keine Auswahl.
        // Fensterkoordinaten allein genuegen nicht: Die Aufnahme beginnt am
        // Seitenanfang, die Auswahl geschah aber an der Stelle, an der der
        // Nutzer gerade stand. Ohne den Scrollstand landet der Ausschnitt um
        // genau diese Strecke zu weit oben — bei einer weit gescrollten Seite
        // zeigt das PDF dann etwas voellig anderes als das Gewaehlte.
        const versatzY = window.scrollY || document.documentElement.scrollTop || 0;
        const versatzX = window.scrollX || document.documentElement.scrollLeft || 0;
        beenden(r.w < 12 || r.h < 12 ? null : {
          x: Math.max(0, r.x) + versatzX, y: Math.max(0, r.y) + versatzY,
          w: Math.min(r.w, window.innerWidth - r.x),
          h: Math.min(r.h, window.innerHeight - r.y),
          scrollX: versatzX, scrollY: versatzY,
          dpr: window.devicePixelRatio || 1,
        });
      });
      huelle.addEventListener("contextmenu", (e) => { e.preventDefault(); beenden(null); });
      window.addEventListener("keydown", beiTaste, true);
    });
  }

  browser.runtime.onMessage.addListener((msg, sender, sendResponse) => {
    (async () => {
      try {
        switch (msg.cmd) {
          case "ping":
            sendResponse({ ok: true, injected: true, version: "1.1.0" });
            break;
          case "selectRegion":
            sendResponse(await selectRegion(msg.hint));
            break;
          case "collectSource":
            sendResponse(sammleQuelle());
            break;
          case "collectText":
            sendResponse(collectText());
            break;
          case "collectLinks":
            sendResponse(collectLinks());
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
