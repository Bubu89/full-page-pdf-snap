"use strict";

const $ = id => document.getElementById(id);

const t = (schluessel, ersatz) =>
  (window.PageShotI18n && window.PageShotI18n.t && window.PageShotI18n.t(schluessel)) || ersatz;

async function aufnehmen(knopf, bereich) {
  const status = $("status");
  status.className = "status";
  status.textContent = t("popupWorking", "Capturing …");
  $("go").disabled = true;
  $("region").disabled = true;

  try {
    const res = await browser.runtime.sendMessage({ cmd: "capture", region: !!bereich });
    if (res && res.ok && res.result && res.result.cancelled) {
      // Abbruch ist kein Fehler und keine Erfolgsmeldung.
      status.className = "status";
      status.textContent = t("popupRegionCancelled", "Selection cancelled");
    } else if (res && res.ok) {
      status.className = "status ok";
      const n = (res.result && res.result.pages) || 1;
      status.textContent = t("popupSaved", "Saved") + ` (${n})`;
      setTimeout(() => window.close(), 800);
    } else {
      status.className = "status err";
      status.textContent = (res && res.error) || t("popupUnknownError", "Unknown error");
    }
  } catch (e) {
    status.className = "status err";
    status.textContent = e.message || String(e);
  } finally {
    $("go").disabled = false;
    $("region").disabled = false;
  }
}

$("go").addEventListener("click", () => aufnehmen($("go"), false));
// Die Auswahl geschieht in der Seite; das Fenster muss dafuer aus dem Weg.
$("region").addEventListener("click", () => {
  browser.runtime.sendMessage({ cmd: "capture", region: true });
  window.close();
});

/* Schalter fuer stoerende Einblendungen.
 *
 * Er sitzt im Hauptfenster, weil er die Aufnahme sichtbar veraendert — anders
 * als die uebrigen Einstellungen, die einmal gesetzt und vergessen werden. Der
 * Wert kommt aus demselben Speicher wie die Einstellungsseite und das
 * Kontextmenue; wer ihn an einer Stelle umlegt, sieht ihn ueberall umgelegt.
 */
/* Ein Schalter, ein Speicherschluessel, eine Rueckmeldung — fuer beide gleich.
   Zwei fast gleiche Bloecke nebeneinander waeren zwei Orte, an denen dasselbe
   schiefgehen kann. */
async function schalter(id, schluessel, anText, ausText, vorgabeAn = true) {
  const box = $(id);
  if (!box) return;
  try {
    const s = await browser.storage.local.get(schluessel);
    box.checked = vorgabeAn ? s[schluessel] !== false : s[schluessel] === true;
  } catch (_) { /* Vorgabe bleibt: eingeschaltet */ }
  box.addEventListener("change", async () => {
    const st = $("status");
    try {
      await browser.storage.local.set({ [schluessel]: box.checked });
      st.className = "status ok";
      st.textContent = box.checked ? t(anText[0], anText[1]) : t(ausText[0], ausText[1]);
      setTimeout(() => { if (st.textContent) { st.className = "status"; st.textContent = ""; } }, 1600);
    } catch (e) {
      st.className = "status err";
      st.textContent = e.message || String(e);
      box.checked = !box.checked;   // Anzeige nicht luegen lassen
    }
  });
}

schalter("hideSticky", "hideSticky",
         ["popupHideOn", "Banners will be hidden"],
         ["popupHideOff", "Banners will be captured as they are"]);
// copyPath ist der einzige Schalter, der ausgeschaltet als Vorgabe gilt: er
// ueberschreibt die Zwischenablage, und das soll niemanden ueberraschen.
schalter("copyPath", "copyPath",
         ["popupCopyOn", "Path will be copied after saving"],
         ["popupCopyOff", "Path will not be copied"], false);
schalter("sourceMetadata", "sourceMetadata",
         ["popupCiteOn", "Citation details will be added"],
         ["popupCiteOff", "No citation details"]);

(async () => {
  const box = null;
  if (!box) return;
  try {
    const s = await browser.storage.local.get("hideSticky");
    box.checked = s.hideSticky !== false;
  } catch (_) { /* Vorgabe bleibt: eingeschaltet */ }
  box.addEventListener("change", async () => {
    try {
      await browser.storage.local.set({ hideSticky: box.checked });
      const st = $("status");
      st.className = "status ok";
      st.textContent = box.checked
        ? t("popupHideOn", "Banners will be hidden")
        : t("popupHideOff", "Banners will be captured as they are");
      setTimeout(() => { if (st.textContent) { st.className = "status"; st.textContent = ""; } }, 1600);
    } catch (e) {
      const st = $("status");
      st.className = "status err";
      st.textContent = e.message || String(e);
      box.checked = !box.checked;   // Anzeige nicht luegen lassen
    }
  });
})();

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
