/* Ersetzt Texte mit data-i18n durch die Uebersetzung der Browsersprache.
 * Faellt automatisch auf Englisch zurueck (default_locale im Manifest). */
(function () {
  const t = (k) => {
    try { return browser.i18n.getMessage(k); } catch (_) { return ""; }
  };
  document.addEventListener("DOMContentLoaded", () => {
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
    document.documentElement.lang = (browser.i18n.getUILanguage
      ? browser.i18n.getUILanguage() : "en").slice(0, 2);
  });
})();
