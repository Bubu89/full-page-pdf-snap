"use strict";

const $ = id => document.getElementById(id);

const t = (schluessel, ersatz) =>
  (window.PageShotI18n && window.PageShotI18n.t && window.PageShotI18n.t(schluessel)) || ersatz;

const KNOEPFE = ["go", "a4", "artikel", "region"];

/* Ein Weg fuer alle Ausgabearten.
 *
 * "modus" sagt, was herauskommen soll: die fortlaufende Seite (leer), auf A4
 * zerlegt, oder nur der Lesetext als Datei. Der Unterschied gehoert in den
 * Hintergrund, nicht in drei fast gleiche Fassungen dieser Funktion —
 * sonst sind es drei Orte, an denen dieselbe Fehlerbehandlung schiefgeht. */
async function aufnehmen(modus, bereich) {
  const status = $("status");
  status.className = "status";
  status.textContent = t("popupWorking", "Capturing …");
  for (const id of KNOEPFE) { if ($(id)) $(id).disabled = true; }

  try {
    const res = await browser.runtime.sendMessage(
      { cmd: "capture", region: !!bereich, modus: modus || null });
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
    for (const id of KNOEPFE) { if ($(id)) $(id).disabled = false; }
  }
}

$("go").addEventListener("click", () => aufnehmen(null, false));
if ($("a4")) $("a4").addEventListener("click", () => aufnehmen("a4", false));
if ($("artikel")) $("artikel").addEventListener("click", () => aufnehmen("artikel", false));
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



/* Die Zahnraeder.
 *
 * Jede Ausgabeart hat ihr eigenes Fach; es klappt unter dem Knopf auf, zu dem
 * es gehoert. Immer nur eines ist offen — zwei offene Faecher machen aus dem
 * Fenster wieder die Liste, die es einmal war.
 *
 * Die Werte werden beim Umstellen sofort gespeichert, nicht erst beim
 * Aufnehmen. Wer das Fach zuklappt und den Knopf drueckt, soll bekommen, was
 * er eingestellt hat, und nicht das, was vor dem Zuklappen galt.
 */
const FACH_FELDER = [
  { id: "druckPapier",    schluessel: "druckPapier",   art: "wahl" },
  { id: "druckQuer",      schluessel: "druckQuer",     art: "wahl" },
  { id: "druckRand",      schluessel: "druckRandMm",   art: "zahl", rueckfall: 0 },
  { id: "artikelPapier",  schluessel: "artikelPapier", art: "wahl" },
  { id: "artikelQuer",    schluessel: "artikelQuerWahl", art: "wahl" },
  { id: "artikelSchrift", schluessel: "artikelSchriftgroesse", art: "zahl", rueckfall: 18 },
  { id: "artikelText",    schluessel: "artikelAlsText", art: "haken" },
];

(async () => {
  const vorgabe = {
    druckPapier: "a4", druckQuer: "hoch", druckRandMm: 0,
    artikelPapier: "a4", artikelQuerWahl: "hoch",
    artikelSchriftgroesse: 18, artikelAlsText: false,
  };
  let stand = vorgabe;
  try { stand = await browser.storage.local.get(vorgabe); } catch (_) { /* Vorgabe bleibt */ }

  for (const f of FACH_FELDER) {
    const el = $(f.id);
    if (!el) continue;
    const wert = stand[f.schluessel];
    if (f.art === "haken") {
      el.checked = wert === true;
    } else {
      el.value = String(wert);
      /* Ein Auswahlfeld nimmt nur an, was es als Option gibt.
       *
       * Steht gespeichert ein Wert, den die Liste nicht kennt, faellt
       * `value` still auf "" — das Feld erscheint LEER, und der alte Wert
       * bleibt trotzdem in Kraft. Gemeldet am 18.08.2026: "ohne Rand"
       * gewaehlt, Feld leer, gedruckt wurde mit 51 pt Rand ringsum. Das
       * waren 18 mm, ein Wert, den die Liste seit dem Zusammenstreichen auf
       * 0/5/10 gar nicht mehr anbietet.
       *
       * Deshalb wird hier nicht nur die Anzeige zurechtgerueckt, sondern
       * auch der gespeicherte Wert: Ein Feld, das etwas anderes anzeigt als
       * gilt, ist schlimmer als ein falscher Wert. */
      if (el.tagName === "SELECT" && el.selectedIndex < 0) {
        const ersatz = f.rueckfall != null ? String(f.rueckfall)
                     : (el.options[0] ? el.options[0].value : "");
        el.value = ersatz;
        const bereinigt = f.art === "zahl" ? (parseInt(ersatz, 10) || 0) : ersatz;
        try { browser.storage.local.set({ [f.schluessel]: bereinigt }); }
        catch (_) { /* dann eben beim naechsten Mal */ }
      }
    }
    el.addEventListener("change", async () => {
      const neu = f.art === "haken" ? el.checked
                /* Der Rueckfall gehoert zum FELD, nicht zur Art.
                 * Hier stand fuer jedes Zahlenfeld die 18 — sinnvoll fuer
                 * eine Schriftgroesse, sinnlos fuer einen Rand. Bei leerem
                 * Feld wurden daraus 18 mm Rand, also 51 pt. */
                : f.art === "zahl" ? (parseInt(el.value, 10) || (f.rueckfall != null ? f.rueckfall : 0))
                : el.value;
      try { await browser.storage.local.set({ [f.schluessel]: neu }); }
      catch (e) { /* Der naechste Klick nimmt dann die alte Einstellung */ }
    });
  }
})();

for (const rad of document.querySelectorAll(".rad")) {
  rad.addEventListener("click", () => {
    const fach = $(rad.dataset.fach);
    if (!fach) return;
    const offen = fach.classList.contains("auf");
    // Erst alle zu, dann das gewaehlte auf — so bleibt hoechstens eines offen.
    for (const f of document.querySelectorAll(".fach")) f.classList.remove("auf");
    for (const r of document.querySelectorAll(".rad")) r.setAttribute("aria-expanded", "false");
    if (!offen) {
      fach.classList.add("auf");
      rad.setAttribute("aria-expanded", "true");
    }
  });
}

/* Was dieser Browser nicht vollwertig kann, steht auch nicht im Menue.
 *
 * Der Artikel-Weg setzt die Seite als Lesedokument und braucht dafuer
 * Chromiums Druckschnittstelle. In Firefox liesse sich zwar eine Leseansicht
 * aufnehmen, aber als BILD statt als Text — dieselbe Schaltflaeche haette
 * dort also eine andere Bedeutung. Eine Funktion, die je nach Browser etwas
 * anderes liefert, ist schlechter als eine, die es nur dort gibt, wo sie
 * haelt was sie verspricht.
 *
 * Ausgeblendet wird anhand dessen, was der Browser KANN, nicht anhand seines
 * Namens: Kennungen lassen sich faelschen und aendern sich, eine fehlende
 * Schnittstelle nicht. */
(function artikelNurWoErTraegt() {
  const kann = typeof browser !== "undefined" && !!browser.debugger;
  if (kann) return;
  for (const id of ["zeileArtikel", "fachArtikel"]) {
    const el = $(id);
    if (el) el.remove();
  }
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

/* Auf Android gar nicht erst dieses Menue zeigen.
 *
 * Das Hintergrundskript schaltet das Popup zwar ab (action.setPopup mit leerem
 * Wert), aber erst wenn es geladen ist. Nach einem Neustart des Browsers laedt
 * es unter Umstaenden erst durch den Tastendruck selbst - da steht das Menue
 * schon offen. Am 07.08.2026 auf dem Geraet so beobachtet.
 *
 * Deshalb hier noch einmal, aus der Seite heraus: Ist es ein Telefon, sofort
 * aufnehmen und schliessen. Wer es einmal sieht, sieht es nie wieder - der
 * naechste Tastendruck laeuft dann ueber onClicked. */
(async () => {
  try {
    const p = await browser.runtime.getPlatformInfo();
    if (!p || p.os !== "android") return;
    document.body.classList.add("android-sofort");
    // Nicht auf die Antwort warten - die Aufnahme dauert, das Fenster soll weg.
    browser.runtime.sendMessage({ cmd: "capture", region: false })
      .catch((e) => console.warn("[PDFSnap/popup] Aufnahme:", e));
    setTimeout(() => { try { window.close(); } catch (_) { /* egal */ } }, 150);
  } catch (e) {
    console.warn("[PDFSnap/popup] Plattform unbekannt:", e);
  }
})();
