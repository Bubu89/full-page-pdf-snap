/* Oberflaechen-Texte, mit eigener Sprachwahl.
 *
 * browser.i18n folgt starr der Browsersprache - eine Umschaltung in den
 * Einstellungen ist damit nicht moeglich. Darum liest diese Schicht die
 * gewaehlte Sprache aus storage.local und laedt die passende messages.json
 * direkt aus dem Paket. Bei "auto" bleibt es bei browser.i18n, also der
 * Browsersprache.
 *
 * Die Store-Metadaten (Name, Beschreibung) laufen weiterhin ueber _locales -
 * die legt der Store anhand der Browsersprache fest, darauf hat eine
 * Erweiterung keinen Einfluss.
 */
(function () {
  const FALLBACK = "en";
  let table = null;              // gefuellt, wenn eine Sprache erzwungen wurde

  function loadTable(lang) {
    if (!lang || lang === "auto") return null;
    const all = (typeof PAGESHOT_MESSAGES !== "undefined") ? PAGESHOT_MESSAGES : {};
    return all[lang] || all[lang.split("_")[0]] || all[FALLBACK] || null;
  }

  function t(key) {
    if (table && table[key]) return table[key];
    try { return browser.i18n.getMessage(key) || ""; } catch (_) { return ""; }
  }

  function apply() {
    for (const el of document.querySelectorAll("[data-i18n]")) {
      const msg = t(el.dataset.i18n);
      if (msg) el.textContent = msg;
    }
    for (const el of document.querySelectorAll("[data-i18n-title]")) {
      const msg = t(el.dataset.i18nTitle);
      if (msg) el.title = msg;
    }
    const titleKey = document.documentElement.dataset.i18nTitle;
    if (titleKey) {
      const msg = t(titleKey);
      if (msg) document.title = msg;
    }
  }

  async function init() {
    table = null;                 // bei erneutem Aufruf nicht die alte Wahl behalten
    let lang = "auto";
    try {
      const s = await browser.storage.local.get({ uiLanguage: "auto" });
      lang = s.uiLanguage || "auto";
    } catch (_) { /* Standard bleibt auto */ }
    table = loadTable(lang);
    document.documentElement.lang = lang !== "auto" ? lang.split("_")[0]
      : ((browser.i18n.getUILanguage && browser.i18n.getUILanguage()) || FALLBACK).slice(0, 2);
    apply();
  }

  // Nach aussen sichtbar, damit background.js dieselbe Wahl nutzen kann
  window.PageShotI18n = { t, apply, init, load: loadTable };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
