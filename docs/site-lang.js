/* site-lang.js — eine Sprachwahl fuer die ganze Seite.
 *
 * Die Wahl steht im Menue, gilt domainweit (localStorage 'pl-lang') und
 * ueberlebt den Seitenwechsel. Uebersetzte Abschnitte tragen data-lang="xx";
 * sichtbar ist genau einer.
 *
 * Nicht jede Seite gibt es in jeder Sprache. Statt eine leere Seite zu zeigen,
 * faellt sie auf Englisch zurueck und sagt das in der gewaehlten Sprache — eine
 * stumme Rueckfall-Anzeige liest sich wie ein Defekt.
 *
 * Erzeugt aus _locales: dieselben neun Sprachen, die die Erweiterung spricht.
 */
(function () {
  "use strict";

  var LANGS = [
    { code: "en",    name: "English" },
    { code: "de",    name: "Deutsch" },
    { code: "es",    name: "Español" },
    { code: "fr",    name: "Français" },
    { code: "it",    name: "Italiano" },
    { code: "ja",    name: "日本語" },
    { code: "pt-BR", name: "Português" },
    { code: "ru",    name: "Русский" },
    { code: "zh-CN", name: "简体中文" }
  ];

  // Rueckfall-Hinweis in der jeweils gewaehlten Sprache. Kurz halten: er steht
  // ueber dem Artikel und soll ihn nicht verdraengen.
  var FALLBACK = {
    "en": "This page is not available in your language yet — showing English.",
    "de": "Diese Seite gibt es noch nicht in Ihrer Sprache — angezeigt wird Englisch.",
    "es": "Esta página aún no está en su idioma — se muestra en inglés.",
    "fr": "Cette page n'existe pas encore dans votre langue — affichage en anglais.",
    "it": "Questa pagina non è ancora disponibile nella tua lingua — mostrata in inglese.",
    "ja": "このページはまだお使いの言語では提供されていません。英語で表示します。",
    "pt-BR": "Esta página ainda não está no seu idioma — exibindo em inglês.",
    "ru": "Эта страница пока недоступна на вашем языке — показан английский.",
    "zh-CN": "本页面暂无您所选语言的版本，将显示英文。"
  };

  var LABEL = {
    "en": "Language", "de": "Sprache", "es": "Idioma", "fr": "Langue",
    "it": "Lingua", "ja": "言語", "pt-BR": "Idioma", "ru": "Язык", "zh-CN": "语言"
  };

  function gespeichert() {
    try { return localStorage.getItem("pl-lang"); } catch (e) { return null; }
  }

  function merken(l) {
    try { localStorage.setItem("pl-lang", l); } catch (e) {}
  }

  /* Welche Sprachen traegt diese Seite tatsaechlich? */
  function vorhanden() {
    var set = {};
    document.querySelectorAll("[data-lang]").forEach(function (e) {
      set[e.getAttribute("data-lang")] = true;
    });
    return set;
  }

  /* Browsersprache auf eine unterstuetzte abbilden: "de-AT" -> "de",
     "pt-PT" -> "pt-BR" (naeher als Englisch), "zh-TW" -> "zh-CN". */
  function ausBrowser() {
    var roh = (navigator.language || "en");
    var kurz = roh.slice(0, 2).toLowerCase();
    for (var i = 0; i < LANGS.length; i++) {
      if (LANGS[i].code.toLowerCase() === roh.toLowerCase()) return LANGS[i].code;
    }
    if (kurz === "pt") return "pt-BR";
    if (kurz === "zh") return "zh-CN";
    for (var j = 0; j < LANGS.length; j++) {
      if (LANGS[j].code === kurz) return kurz;
    }
    return "en";
  }

  function hinweisZeigen(text) {
    var el = document.getElementById("pl-fallback");
    if (!el) {
      el = document.createElement("p");
      el.id = "pl-fallback";
      el.setAttribute("role", "status");
      el.style.cssText =
        "margin:0 0 1.2rem;padding:.55rem .8rem;border-left:3px solid #b9b9b9;" +
        "background:rgba(128,128,128,.10);font-size:.92rem;line-height:1.45;";
      var wrap = document.querySelector(".wrap");
      var header = wrap && wrap.querySelector("header");
      if (header && header.parentNode) header.parentNode.insertBefore(el, header.nextSibling);
      else if (wrap) wrap.insertBefore(el, wrap.firstChild);
      else return;
    }
    el.textContent = text;
    el.hidden = false;
  }

  function hinweisVerbergen() {
    var el = document.getElementById("pl-fallback");
    if (el) el.hidden = true;
  }

  /* Kern: gewuenschte Sprache setzen. Gespeichert wird die *Wahl*, angezeigt
     die *verfuegbare* — sonst verliert der Leser seine Wahl beim Seitenwechsel
     auf eine uebersetzte Seite. */
  function setLang(wahl, stumm) {
    var da = vorhanden();
    var hatBloecke = Object.keys(da).length > 0;
    // Eine Seite ohne Sprachbloecke ist einsprachig englisch. Sie ist damit
    // genauso ein Rueckfall wie eine, der die gewaehlte Sprache fehlt — und
    // muss es genauso sagen.
    var zeigen = (hatBloecke && da[wahl]) ? wahl : "en";

    if (hatBloecke) {
      document.querySelectorAll("[data-lang]").forEach(function (e) {
        e.classList.toggle("on", e.getAttribute("data-lang") === zeigen);
      });
    }

    document.documentElement.lang = zeigen;
    if (!stumm) merken(wahl);

    if (zeigen !== wahl) hinweisZeigen(FALLBACK[wahl] || FALLBACK.en);
    else hinweisVerbergen();

    var sel = document.getElementById("pl-langpick");
    if (sel && sel.value !== wahl) sel.value = wahl;

    // Alte Seiten tragen noch zwei Schaltflaechen. Solange sie da sind,
    // sollen sie den Zustand richtig anzeigen.
    ["en", "de"].forEach(function (c) {
      var b = document.getElementById("b-" + c);
      if (b) b.setAttribute("aria-pressed", String(zeigen === c));
    });
  }

  function menueBauen(aktuell) {
    var nav = document.querySelector(".topnav .inner");
    if (!nav || document.getElementById("pl-langpick")) return;

    var sel = document.createElement("select");
    sel.id = "pl-langpick";
    sel.className = "n";
    sel.setAttribute("aria-label", LABEL[aktuell] || LABEL.en);
    sel.style.cssText =
      "font:inherit;color:inherit;background:transparent;border:1px solid rgba(128,128,128,.45);" +
      "border-radius:4px;padding:.15rem .35rem;margin-left:.15rem;cursor:pointer;";

    var da = vorhanden();
    LANGS.forEach(function (l) {
      var o = document.createElement("option");
      o.value = l.code;
      // Sprachen, die es auf dieser Seite gibt, zuerst erkennbar machen.
      o.textContent = (da[l.code] ? "• " : "") + l.name;
      o.style.color = "#111";
      if (l.code === aktuell) o.selected = true;
      sel.appendChild(o);
    });

    sel.addEventListener("change", function () { setLang(sel.value); });

    // Der alte Menuepunkt "Deutsch" zeigte auf einen Anker in der Seite. Die
    // Sprachwahl ersetzt ihn — zwei Bedienstellen fuer dieselbe Sache sind eine
    // zu viel.
    var alt = nav.querySelector('a[hreflang="de"]');
    if (alt) alt.parentNode.removeChild(alt);

    var dl = nav.querySelector("a.dl");
    if (dl) nav.insertBefore(sel, dl); else nav.appendChild(sel);
  }

  function start() {
    var wahl = gespeichert() || ausBrowser();
    menueBauen(wahl);
    setLang(wahl, true);
    // Die alten Inline-Schaltflaechen rufen setLang() global auf.
    window.setLang = setLang;
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
