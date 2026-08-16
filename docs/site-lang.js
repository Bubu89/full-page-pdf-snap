/* site-lang.js — eine Sprachwahl fuer die ganze Seite.
 *
 * Die Wahl steht im Menue, gilt domainweit (localStorage 'pl-lang') und
 * ueberlebt den Seitenwechsel. Uebersetzte Abschnitte tragen data-lang="xx";
 * sichtbar ist genau einer. Das Menue selbst schaltet mit (NAV unten) — die
 * Leiste ist die Bedienstelle der Wahl und darf nicht englisch stehen bleiben.
 *
 * Nicht jede Seite gibt es in jeder Sprache. Statt eine leere Seite zu zeigen,
 * faellt sie auf Englisch zurueck und sagt das in der gewaehlten Sprache — eine
 * stumme Rueckfall-Anzeige liest sich wie ein Defekt.
 *
 * Erzeugt aus _locales: dieselben neun Sprachen, die die Erweiterung spricht.
 */
(function () {
  "use strict";

  // kurz: was im zugeklappten Feld steht. Der volle Name erscheint beim
  // Aufklappen. Grund: die Menueleiste hat eine feste Hoechstbreite und war mit
  // den vollen Namen (114 px) auf jeder Fensterbreite zweizeilig — gemessen,
  // nicht vermutet.
  var LANGS = [
    { code: "en",    name: "English",   kurz: "EN" },
    { code: "de",    name: "Deutsch",   kurz: "DE" },
    { code: "es",    name: "Español",   kurz: "ES" },
    { code: "fr",    name: "Français",  kurz: "FR" },
    { code: "it",    name: "Italiano",  kurz: "IT" },
    { code: "ja",    name: "日本語",     kurz: "JA" },
    { code: "pt-BR", name: "Português", kurz: "PT" },
    { code: "ru",    name: "Русский",   kurz: "RU" },
    { code: "zh-CN", name: "简体中文",   kurz: "ZH" }
  ];

  // Rueckfall-Hinweis in der jeweils gewaehlten Sprache. Kurz halten: er steht
  // ueber dem Artikel und soll ihn nicht verdraengen.
  // Rueckfall-Hinweis in der jeweils gewaehlten Sprache. Kurz halten: er steht
  // ueber dem Artikel und soll ihn nicht verdraengen.
  //
  // {s} wird durch die Eigenbezeichnung der Sprache ersetzt, die TATSAECHLICH
  // angezeigt wird. Vorher stand hier fest "Englisch" — auf den einsprachig
  // deutschen Seiten (/mitmachen/, /anleitung/…, /deutsch/) meldete das Skript
  // damit "affichage en anglais", waehrend deutscher Text zu sehen war.
  // (16.08.2026, vom Nutzer gemeldet)
  var FALLBACK = {
    "en": "This page is not available in your language yet — showing {s}.",
    "de": "Diese Seite gibt es noch nicht in Ihrer Sprache — angezeigt wird {s}.",
    "es": "Esta página aún no está en su idioma — se muestra en {s}.",
    "fr": "Cette page n'existe pas encore dans votre langue — affichage en {s}.",
    "it": "Questa pagina non è ancora disponibile nella tua lingua — mostrata in {s}.",
    "ja": "このページはまだお使いの言語では提供されていません。{s}で表示します。",
    "pt-BR": "Esta página ainda não está no seu idioma — exibindo em {s}.",
    "ru": "Эта страница пока недоступна на вашем языке — показан {s}.",
    "zh-CN": "本页面暂无您所选语言的版本，将显示{s}。"
  };

  // Wie die angezeigte Sprache im Hinweis benannt wird.
  //
  // Rueckfall ist in der Praxis immer "en" oder "de" — nur diese beiden sind
  // Basis einer Seite. Fuer sie steht die im Satz gebeugte Form da; die
  // Eigenbezeichnung ("affichage en English") las sich falsch. Alles andere
  // faellt auf die Eigenbezeichnung aus LANGS zurueck: eindeutig, wenn auch
  // ungelenk — und es tritt nicht auf, solange keine dritte Basissprache
  // hinzukommt.
  var IM_SATZ = {
    "en": { "en": "English", "de": "Englisch", "es": "inglés", "fr": "anglais",
            "it": "inglese", "ja": "英語", "pt-BR": "inglês",
            "ru": "английский", "zh-CN": "英文" },
    "de": { "en": "German", "de": "Deutsch", "es": "alemán", "fr": "allemand",
            "it": "tedesco", "ja": "ドイツ語", "pt-BR": "alemão",
            "ru": "немецкий", "zh-CN": "德文" }
  };

  function sprachName(code, anzeige) {
    var g = IM_SATZ[code];
    if (g && g[anzeige]) return g[anzeige];
    for (var i = 0; i < LANGS.length; i++) {
      if (LANGS[i].code === code) return LANGS[i].name;
    }
    return code;
  }

  // Die Sprache, in der die Seite AUSGELIEFERT wurde. Einmal beim Laden
  // festhalten, bevor setLang() das Attribut ueberschreibt.
  var SEITENSPRACHE = (document.documentElement.getAttribute("lang") || "en");
  var LABEL = {
    "en": "Language", "de": "Sprache", "es": "Idioma", "fr": "Langue",
    "it": "Lingua", "ja": "言語", "pt-BR": "Idioma", "ru": "Язык", "zh-CN": "语言"
  };

  /* Menuebeschriftungen. Bisher schalteten nur die data-lang-Bloecke im
     Artikel um — die Menueleiste blieb auf jeder Sprache englisch, und genau
     die Leiste ist es, ueber die sich die Sprache einstellen laesst. Der
     Schluessel wird aus dem href erkannt, nicht aus dem Text: der Text ist
     je nach Seite schon mal "Mitmachen" statt "Contribute". "Mitmachen"
     bleibt auf Englisch stehen — so steht es heute auf allen Seiten, und eine
     Umbenennung ist eine inhaltliche Entscheidung, keine Uebersetzung.
     NBSP wo er heute steht ("How to"), damit die Leiste nicht umbricht. */
  var NAV = {
    "notes":        { "en": "Notes",        "de": "Notizen",       "es": "Notas",        "fr": "Notes",          "it": "Note",         "ja": "ノート",           "pt-BR": "Notas",        "ru": "Заметки",      "zh-CN": "笔记" },
    "measurements": { "en": "Measurements", "de": "Messungen",     "es": "Mediciones",   "fr": "Mesures",        "it": "Misure",       "ja": "測定",             "pt-BR": "Medições",     "ru": "Измерения",    "zh-CN": "测量" },
    "how-to":       { "en": "How to",  "de": "Anleitung",     "es": "Guías",       "fr": "Guides",         "it": "Guide",        "ja": "使い方",           "pt-BR": "Guias",        "ru": "Инструкции",  "zh-CN": "指南" },
    "recipes":      { "en": "Recipes",      "de": "Rezepte",       "es": "Recetas",      "fr": "Recettes",       "it": "Ricette",      "ja": "レシピ",           "pt-BR": "Receitas",     "ru": "Рецепты",      "zh-CN": "配方" },
    "for-agents":   { "en": "For agents", "de": "Für Agenten", "es": "Para agentes", "fr": "Pour les agents", "it": "Per gli agenti", "ja": "エージェント向け", "pt-BR": "Para agentes", "ru": "Для агентов", "zh-CN": "面向代理" },
    "mitmachen":    { "en": "Mitmachen",    "de": "Mitmachen",     "es": "Participar",   "fr": "Participer",     "it": "Partecipa",    "ja": "参加する",         "pt-BR": "Participar",   "ru": "Участвовать",  "zh-CN": "参与" },
    "tools":        { "en": "Tools",        "de": "Werkzeuge",     "es": "Herramientas", "fr": "Outils",         "it": "Strumenti",    "ja": "ツール",           "pt-BR": "Ferramentas",  "ru": "Инструменты",  "zh-CN": "工具" },
    "about":        { "en": "About",        "de": "Über",          "es": "Acerca de",    "fr": "À propos",       "it": "Informazioni", "ja": "概要",             "pt-BR": "Sobre",        "ru": "О сайте",      "zh-CN": "关于" },
    "download":     { "en": "Download",     "de": "Download",      "es": "Descargar",    "fr": "Télécharger",    "it": "Scarica",      "ja": "ダウンロード",     "pt-BR": "Baixar",       "ru": "Скачать",      "zh-CN": "下载" }
  };

  /* href auf einen NAV-Schluessel abbilden. Die Pfade sind relativ und tief
     verschachtelt ("../../notes/"), deshalb nur auf den Zielnamen pruefen. */
  function navSchluessel(a) {
    if (a.className === "dl") return "download";
    var m = (a.getAttribute("href") || "").match(/\/(notes|measurements|recipes|tools|about|for-agents|mitmachen)\/$/);
    if (m) return m[1];
    if (/\/how-to\//.test(a.getAttribute("href") || "")) return "how-to";
    return null;
  }

  /* Menue in der *gewaehlten* Sprache beschriften — nicht in der angezeigten.
     Faellt eine Seite auf Englisch zurueck, bleibt die Leiste die Stelle, an
     der der Leser seine eigene Sprache wiederfindet. */
  function navUebersetzen(wahl) {
    var labels = {};
    for (var k in NAV) labels[k] = NAV[k][wahl] || NAV[k].en;
    document.querySelectorAll(".topnav a.n, .topnav a.dl").forEach(function (a) {
      var k = navSchluessel(a);
      if (k && labels[k]) a.textContent = labels[k];
    });
    var sel = document.getElementById("pl-langpick");
    if (sel) sel.setAttribute("aria-label", LABEL[wahl] || LABEL.en);
    navEinpassen();
  }

  /* Uebersetzungen sind laenger als das Englische ("Messungen", "Herramientas")
     und die Leiste hat eine feste Hoechstbreite — bei 1180 px brachen de, es,
     ru und fr auf zwei Zeilen um, gemessen am 15.08.2026. Statt Sprachlisten
     zu pflegen: einmal messen, bei Umbruch Abstand und Schrift der Leiste
     verkleinern. Zurueck auf Englisch nimmt die Regel sich wieder raus. */
  var navStil = null;
  function navEinpassen() {
    var leiste = document.querySelector(".topnav .inner");
    if (!leiste) return;
    if (!navStil) {
      navStil = document.createElement("style");
      navStil.id = "pl-navfit";
      document.head.appendChild(navStil);
    }
    navStil.textContent = "";
    if (leiste.getBoundingClientRect().height > 70) {
      navStil.textContent =
        "@media (min-width:641px){.topnav .inner{gap:10px}.topnav a.n{font-size:.84rem}}";
      if (leiste.getBoundingClientRect().height > 70) {
        navStil.textContent =
          "@media (min-width:641px){.topnav .inner{gap:8px}.topnav a.n{font-size:.8rem}}";
      }
      // Russisch bei 980 px: kyrillische Woerter sind lang und brechen nicht
      // um — es braucht eine dritte, engere Stufe (gemessen 15.08.2026).
      if (leiste.getBoundingClientRect().height > 70) {
        navStil.textContent =
          "@media (min-width:641px){.topnav .inner{gap:6px}.topnav a.n{font-size:.78rem}}";
      }
    }
  }

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
      // Einfuegestelle, absteigend nach Genauigkeit. Der letzte Zweig kehrte
      // frueher einfach zurueck: fehlte .wrap, erschien GAR KEIN Hinweis, und
      // zwar lautlos. Auf privacy.html bekam ein franzoesischer Leser dadurch
      // englischen Text ohne jede Erklaerung. Ein Hinweis, der sich selbst
      // verschluckt, ist schlechter als ein haesslich platzierter.
      // (16.08.2026)
      var wrap = document.querySelector(".wrap");
      var header = wrap && wrap.querySelector("header");
      var ziel = null, vor = null;
      if (header && header.parentNode) { ziel = header.parentNode; vor = header.nextSibling; }
      else if (wrap) { ziel = wrap; vor = wrap.firstChild; }
      else {
        var haupt = document.querySelector("main") || document.body;
        var h1 = haupt && haupt.querySelector("h1");
        if (h1 && h1.parentNode) { ziel = h1.parentNode; vor = h1.nextSibling; }
        else if (haupt) { ziel = haupt; vor = haupt.firstChild; }
      }
      if (!ziel) return;
      ziel.insertBefore(el, vor);
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
    // Eine Seite ohne Sprachbloecke ist NICHT automatisch englisch — sie ist in
    // der Sprache, in der sie ausgeliefert wurde. Die alte Annahme setzte
    // lang="en" auf deutschen Text und meldete "zeigt Englisch", waehrend
    // Deutsch zu sehen war. Sie ist trotzdem ein Rueckfall und muss es sagen.
    var zeigen;
    if (!hatBloecke) {
      zeigen = SEITENSPRACHE;
    } else if (da[wahl]) {
      zeigen = wahl;
    } else {
      zeigen = da["en"] ? "en" : Object.keys(da)[0];
    }

    if (hatBloecke) {
      document.querySelectorAll("[data-lang]").forEach(function (e) {
        e.classList.toggle("on", e.getAttribute("data-lang") === zeigen);
      });
    }

    document.documentElement.lang = zeigen;
    if (!stumm) merken(wahl);
    navUebersetzen(wahl);

    if (zeigen !== wahl) {
      hinweisZeigen((FALLBACK[wahl] || FALLBACK.en)
                    .replace("{s}", sprachName(zeigen, wahl)));
    }
    else hinweisVerbergen();

    var sel = document.getElementById("pl-langpick");
    if (sel && sel.value !== wahl) {
      sel.value = wahl;
      if (sel.beschriften) sel.beschriften(false);
    }

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
    // Feste Breite ist noetig, nicht Geschmack: ein <select> mit width:auto
    // bemisst sich nach seiner *breitesten* Option, nicht nach der angezeigten.
    // Der Kurzcode allein haette also nichts gespart. Die aufgeklappte Liste
    // darf breiter werden — das entscheidet der Browser.
    sel.style.cssText =
      "font:inherit;color:inherit;background:transparent;border:1px solid rgba(128,128,128,.45);" +
      "border-radius:4px;padding:.15rem .2rem;margin-left:.15rem;cursor:pointer;" +
      "width:4.2rem;max-width:4.2rem;";

    var da = vorhanden();
    LANGS.forEach(function (l) {
      var o = document.createElement("option");
      o.value = l.code;
      // Sprachen, die es auf dieser Seite gibt, zuerst erkennbar machen.
      o.dataset.voll = (da[l.code] ? "• " : "") + l.name;
      o.dataset.kurz = l.kurz;
      o.textContent = o.dataset.voll;
      o.style.color = "#111";
      if (l.code === aktuell) o.selected = true;
      sel.appendChild(o);
    });

    // Zugeklappt genuegt der Code, aufgeklappt braucht es den Namen. Ein
    // <select> zeigt immer den Text der gewaehlten Option — also wird der Text
    // umgeschaltet, statt ein eigenes Bedienelement nachzubauen.
    function beschriften(voll) {
      for (var i = 0; i < sel.options.length; i++) {
        var o = sel.options[i];
        o.textContent = (voll || !o.selected) ? o.dataset.voll : o.dataset.kurz;
      }
    }
    // setLang kann die Auswahl auch ohne Zutun des Lesers aendern (Rueckfall,
    // gespeicherte Wahl). Dann muss die Beschriftung mitziehen.
    sel.beschriften = beschriften;
    sel.addEventListener("mousedown", function () { beschriften(true); });
    sel.addEventListener("focus", function () { beschriften(true); });
    sel.addEventListener("blur", function () { beschriften(false); });
    sel.addEventListener("change", function () {
      setLang(sel.value);
      beschriften(false);
    });
    beschriften(false);

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
