"use strict";

const $ = id => document.getElementById(id);

$("go").addEventListener("click", async () => {
  const status = $("status");
  status.className = "status";
  status.textContent = "Erfasse Seite ...";
  $("go").disabled = true;

  try {
    const res = await browser.runtime.sendMessage({ cmd: "capture" });
    if (res && res.ok) {
      status.className = "status ok";
      status.textContent = `Gespeichert (${res.result.pages} Seiten)`;
      setTimeout(() => window.close(), 800);
    } else {
      status.className = "status err";
      status.textContent = (res && res.error) || "Unbekannter Fehler";
    }
  } catch (e) {
    status.className = "status err";
    status.textContent = e.message || String(e);
  } finally {
    $("go").disabled = false;
  }
});

$("opts").addEventListener("click", () => {
  browser.runtime.openOptionsPage();
  window.close();
});

/* Zeigt die tatsaechlich aktive Tastenkombination.
 *
 * Sie fest ins HTML zu schreiben war falsch: der Nutzer kann sie in den
 * Browser-Einstellungen aendern, und bei einem Konflikt mit einem
 * browsereigenen Kuerzel vergibt der Browser gar keine - dann stand dort eine
 * Kombination, die nichts ausloest.
 */
(async () => {
  const el = document.getElementById("shortcut");
  if (!el) return;
  try {
    const cmds = await browser.commands.getAll();
    // Chrome fuehrt ein zweites Kuerzel; hier steht das erste vergebene.
    const keys = cmds
      .filter(x => x.name.startsWith("capture-full-page") && x.shortcut)
      .map(x => x.shortcut);
    if (keys.length) {
      el.textContent = keys[0];
      if (keys.length > 1) el.title = keys.join("  /  ");
    } else {
      el.textContent = "—";
      el.title = "No shortcut assigned (conflict with a browser shortcut). "
               + "Assign one in the browser's extension shortcut settings.";
    }
  } catch (_) {
    // Kein Rateversuch: eine genannte, aber nicht vergebene Kombination ist
    // schlimmer als gar keine Angabe.
    el.textContent = "—";
  }
})();
