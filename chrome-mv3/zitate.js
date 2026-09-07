"use strict";

/* Fertige Eintraege fuers Literaturverzeichnis.
 *
 * Die Erweiterung liest ohnehin schon alle Angaben aus der Seite, die eine
 * Zitation braucht — Verfasser, Titel, Jahr, Zeitschrift, Band, Seiten, DOI,
 * Abrufzeitpunkt. Bisher lagen sie nur als RIS-Datensatz daneben. Der ist
 * fuer Zotero und Citavi richtig, aber nutzlos fuer den, der einfach eine
 * Zeile in seine Arbeit kopieren will.
 *
 * Diese Datei formt aus denselben Angaben die gaengigen Stile — in Deutsch
 * und Englisch, weil sich die Stile darin unterscheiden: "u. a." gegen
 * "et al.", "Hrsg." gegen "ed.", "abgerufen am" gegen "Retrieved".
 *
 * Zwei Grundsaetze, beide aus den Faellen, die diese Erweiterung schon
 * getroffen hat:
 *
 *  1. Nichts erfinden. Fehlt das Jahr, steht "o. J." da und nicht das Jahr
 *     des Abrufs. Ein erfundenes Jahr im Literaturverzeichnis ist teurer als
 *     eine Luecke, die auffaellt.
 *
 *  2. Die Zerlegung eines Namens offenlegen. Ob "Klaus Mueller" als Mueller,
 *     K. gehoert oder ob "Mueller" der Vorname ist, kann diese Datei nicht
 *     wissen — sie folgt der ueblichen Annahme und legt die Rohform daneben,
 *     damit der Fehler sichtbar bleibt statt sich fortzupflanzen.
 */

const PageShotZitate = (function () {

  /* Zu "undZeichen": Das kaufmaennische Und ist in APA ein SYMBOL, keine
   * Vokabel — es bleibt in jeder Sprache "&". Uebersetzt wird nur "undWort",
   * das in MLA, Chicago und Harvard ausgeschrieben steht. Der erste Entwurf
   * uebersetzte beides und machte aus "Mueller, K., & Schmidt, A." im
   * Japanischen "Mueller, K., ・ Schmidt, A." — ein Zeichen, das dort nichts
   * verbindet. */
  const WORT = {
    de: {
      ohneJahr: "o. J.", ohneVerfasser: "o. V.", ohneTitel: "ohne Titel",
      undZeichen: "&", undWort: "und", uaKurz: "u. a.",
      abgerufen: "abgerufen am", in: "In", hrsg: "Hrsg.",
      band: "Bd.", heft: "H.", seite: "S.", auflage: "Aufl.",
      online: "Online", verfuegbar: "verfügbar unter",
      vonWort: "von", datumsform: "punkt",
    },
    en: {
      ohneJahr: "n.d.", ohneVerfasser: "Anon.", ohneTitel: "untitled",
      undZeichen: "&", undWort: "and", uaKurz: "et al.",
      abgerufen: "Retrieved", in: "In", hrsg: "ed.",
      band: "vol.", heft: "no.", seite: "pp.", auflage: "ed.",
      online: "Online", verfuegbar: "available at",
      vonWort: "from", datumsform: "iso",
    },
    /* Die uebrigen Oberflaechensprachen.
     *
     * Die Stile selbst — APA, MLA, Chicago — sind englischsprachige Normen und
     * werden nicht uebersetzt. Uebersetzt gehoeren die Woerter, die eine
     * Zitation VERBINDET: "abgerufen am", "In:", "Bd.", "S.". Wer eine Arbeit
     * auf Spanisch schreibt, kann keinen Eintrag mit "Retrieved" gebrauchen. */
    es: {
      ohneJahr: "s. f.", ohneVerfasser: "Anón.", ohneTitel: "sin título",
      undZeichen: "&", undWort: "y", uaKurz: "et al.",
      abgerufen: "consultado el", in: "En", hrsg: "ed.",
      band: "vol.", heft: "n.º", seite: "pp.", auflage: "ed.",
      online: "En línea", verfuegbar: "disponible en",
      vonWort: "de", datumsform: "punkt",
    },
    fr: {
      ohneJahr: "s. d.", ohneVerfasser: "Anon.", ohneTitel: "sans titre",
      undZeichen: "&", undWort: "et", uaKurz: "et al.",
      abgerufen: "consulté le", in: "Dans", hrsg: "dir.",
      band: "vol.", heft: "n°", seite: "p.", auflage: "éd.",
      online: "En ligne", verfuegbar: "disponible à",
      vonWort: "à", datumsform: "punkt",
    },
    it: {
      ohneJahr: "s. d.", ohneVerfasser: "Anon.", ohneTitel: "senza titolo",
      undZeichen: "&", undWort: "e", uaKurz: "et al.",
      abgerufen: "consultato il", in: "In", hrsg: "a cura di",
      band: "vol.", heft: "n.", seite: "pp.", auflage: "ed.",
      online: "Online", verfuegbar: "disponibile all'indirizzo",
      vonWort: "da", datumsform: "punkt",
    },
    pt_BR: {
      ohneJahr: "s. d.", ohneVerfasser: "Anôn.", ohneTitel: "sem título",
      undZeichen: "&", undWort: "e", uaKurz: "et al.",
      abgerufen: "acessado em", in: "Em", hrsg: "org.",
      band: "vol.", heft: "n.º", seite: "pp.", auflage: "ed.",
      online: "On-line", verfuegbar: "disponível em",
      vonWort: "de", datumsform: "punkt",
    },
    ru: {
      ohneJahr: "б. г.", ohneVerfasser: "Аноним", ohneTitel: "без названия",
      undZeichen: "&", undWort: "и", uaKurz: "и др.",
      abgerufen: "дата обращения", in: "В", hrsg: "ред.",
      band: "т.", heft: "№", seite: "с.", auflage: "изд.",
      online: "Электронный ресурс", verfuegbar: "доступно по адресу",
      vonWort: "по адресу", datumsform: "punkt",
    },
    zh_CN: {
      ohneJahr: "无日期", ohneVerfasser: "佚名", ohneTitel: "无标题",
      undZeichen: "&", undWort: "和", uaKurz: "等",
      abgerufen: "访问日期", in: "见", hrsg: "编",
      band: "卷", heft: "期", seite: "页", auflage: "版",
      online: "在线", verfuegbar: "获取自",
      vonWort: "来自", datumsform: "iso",
    },
    ja: {
      ohneJahr: "発行年不明", ohneVerfasser: "著者不明", ohneTitel: "無題",
      undZeichen: "&", undWort: "と", uaKurz: "ほか",
      abgerufen: "参照日", in: "所収", hrsg: "編",
      band: "巻", heft: "号", seite: "頁", auflage: "版",
      online: "オンライン", verfuegbar: "入手先",
      vonWort: "取得元", datumsform: "iso",
    },
  };

  /* Auf eine Sprache zurueckfallen, die es gibt.
   *
   * Die Oberflaeche kennt neun Sprachen, die Zitierwoerter ebenfalls — aber
   * eine Einstellung wie "auto" oder ein Kuerzel mit Land ("de-AT") darf nicht
   * ins Leere greifen. Fehlt eine Sprache, ist Englisch die richtige Antwort:
   * die Stilnamen sind ohnehin englisch. */
  function wort(sprache) {
    if (WORT[sprache]) return WORT[sprache];
    const kurz = String(sprache || "").split(/[-_]/)[0];
    return WORT[kurz] || WORT.en;
  }

  function txt(v) { return v == null ? "" : String(v).trim(); }

  /* Einen Namen in Nachname und Vornamen zerlegen.
   *
   * Mit Komma ist die Sache klar — so schreiben es die meisten Verlage in
   * citation_author. Ohne Komma gilt die uebliche Annahme: das letzte Wort
   * ist der Nachname. Sie geht bei "van der Berg" und bei ostasiatischen
   * Namen fehl; deshalb steht die Rohform in der Datei mit dabei. */
  function namenTeilen(roh) {
    const n = txt(roh);
    if (!n) return null;
    if (n.indexOf(",") > -1) {
      const [nach, ...rest] = n.split(",");
      return { nach: txt(nach), vor: txt(rest.join(",")), roh: n };
    }
    const teile = n.split(/\s+/);
    if (teile.length === 1) return { nach: teile[0], vor: "", roh: n };
    return { nach: teile[teile.length - 1], vor: teile.slice(0, -1).join(" "), roh: n };
  }

  function initialen(vor) {
    const v = txt(vor);
    if (!v) return "";
    return v.split(/[\s.]+/).filter(Boolean)
            .map(t => t.charAt(0).toUpperCase() + ".").join(" ");
  }

  function personen(q) {
    return (q.autoren || []).map(namenTeilen).filter(Boolean);
  }

  /* --- Verfasserangaben je Stil ------------------------------------------ */

  function autorenApa(p, w) {
    if (!p.length) return "";
    const eins = x => x.nach + (x.vor ? ", " + initialen(x.vor) : "");
    if (p.length === 1) return eins(p[0]);
    if (p.length <= 20) {
      return p.slice(0, -1).map(eins).join(", ") + ", " + w.undZeichen + " " + eins(p[p.length - 1]);
    }
    // APA 7: ab 21 Verfassern die ersten 19, Auslassung, der letzte.
    return p.slice(0, 19).map(eins).join(", ") + ", ... " + eins(p[p.length - 1]);
  }

  function autorenMla(p, w) {
    if (!p.length) return "";
    const voll = x => x.nach + (x.vor ? ", " + x.vor : "");
    if (p.length === 1) return voll(p[0]);
    if (p.length === 2) {
      return voll(p[0]) + ", " + w.undWort + " " + (p[1].vor ? p[1].vor + " " : "") + p[1].nach;
    }
    return voll(p[0]) + ", " + w.uaKurz;
  }

  function autorenHarvard(p, w) {
    if (!p.length) return "";
    const eins = x => x.nach + (x.vor ? ", " + initialen(x.vor) : "");
    if (p.length === 1) return eins(p[0]);
    if (p.length <= 3) {
      return p.slice(0, -1).map(eins).join(", ") + " " + w.undWort + " " + eins(p[p.length - 1]);
    }
    return eins(p[0]) + " " + w.uaKurz;
  }

  function autorenChicago(p, w) {
    if (!p.length) return "";
    const voll = x => x.nach + (x.vor ? ", " + x.vor : "");
    const gerade = x => (x.vor ? x.vor + " " : "") + x.nach;
    if (p.length === 1) return voll(p[0]);
    if (p.length <= 3) {
      return voll(p[0]) + ", " + p.slice(1, -1).map(gerade).concat([]).join(", ")
           + (p.length > 2 ? ", " : " ") + w.undWort + " " + gerade(p[p.length - 1]);
    }
    return voll(p[0]) + ", " + w.uaKurz;
  }

  function autorenDin(p, w) {
    // DIN 1505-2 setzt den Nachnamen in Grossbuchstaben.
    if (!p.length) return "";
    const eins = x => x.nach.toUpperCase() + (x.vor ? ", " + x.vor : "");
    if (p.length <= 3) return p.map(eins).join("; ");
    return eins(p[0]) + " " + w.uaKurz;
  }

  /* --- Bausteine ---------------------------------------------------------- */

  function jahrVon(q, w) {
    const j = txt(q.jahr);
    if (j) return j;
    const d = txt(q.datum).match(/(\d{4})/);
    return d ? d[1] : w.ohneJahr;
  }

  function abrufVon(q, sprache, w) {
    const roh = txt(q.abrufzeit) || txt(q.abrufdatum);
    if (!roh) return "";
    // Auf Datum kuerzen, wenn eine volle Zeitangabe dasteht: das
    // Literaturverzeichnis nennt den Tag, die Uhrzeit steht im RIS-Satz.
    const d = roh.match(/^(\d{4})-(\d{2})-(\d{2})/);
    if (!d) return roh;
    /* Welche Schreibweise gilt, sagt die Sprachtabelle — nicht ein Vergleich
     * auf "de". Der traf "de-AT" nicht und gab oesterreichischen Nutzern das
     * ISO-Datum, waehrend deutsche das gewohnte bekamen. */
    const form = (w && w.datumsform) || "iso";
    return form === "punkt" ? `${d[3]}.${d[2]}.${d[1]}` : `${d[1]}-${d[2]}-${d[3]}`;
  }

  function seitenVon(q) {
    const von = txt(q.seiteVon), bis = txt(q.seiteBis);
    if (von && bis) return von + "–" + bis;
    return von || bis || "";
  }

  function adresseVon(q) { return txt(q.urlZitat) || txt(q.url); }

  /* Der bestaendige Verweis hat Vorrang.
   *
   * Ein DOI zeigt auf dieselbe Arbeit, auch wenn der Verlag seine Adressen
   * umstellt — eine gewoehnliche Adresse tut das nicht. Wo ein Stil nur einen
   * Verweis vorsieht, gehoert deshalb der DOI dorthin. */
  function verweisVon(q) { return doiVon(q) || adresseVon(q); }

  function doiVon(q) {
    const d = txt(q.doi);
    if (!d) return "";
    return /^https?:/i.test(d) ? d : "https://doi.org/" + d.replace(/^doi:\s*/i, "");
  }

  function punkt(s) {
    const t = txt(s);
    if (!t) return "";
    return /[.!?]$/.test(t) ? t : t + ".";
  }

  /* Achtung beim Trennzeichen: der leere String ist falsy.
   *
   * Mit "trenn || ' '" wurde aus einer gewollt fugenlosen Verbindung eine mit
   * Leerzeichen — APA schrieb dadurch "66 (3)" statt "66(3)". Der Vergleich
   * muss auf "nicht angegeben" pruefen, nicht auf "unwahr". */
  function zusammen(teile, trenn) {
    return teile.map(txt).filter(Boolean).join(trenn == null ? " " : trenn);
  }

  /* Einen Punkt anhaengen, aber keinen zweiten.
   *
   * "o. J." endet bereits auf einen Punkt. Ohne diese Pruefung stand in jedem
   * Eintrag ohne Jahresangabe "o. J.." — ein Fehler, der in einer abgegebenen
   * Arbeit auffaellt. */
  function satzende(s) {
    const t = txt(s);
    if (!t) return "";
    return /\.$/.test(t) ? t : t + ".";
  }

  /* Umlaute und Zeichen mit Strich fuer den BibTeX-Schluessel uebertragen.
   *
   * Ohne das wurde aus "Mueller" der Schluessel "mller": die Umlaute fielen
   * ersatzlos weg, weil der Filter nur Buchstaben von A bis Z durchliess. */
  function entzeichnen(s) {
    return txt(s)
      .replace(/ä/g, "ae").replace(/ö/g, "oe").replace(/ü/g, "ue")
      .replace(/Ä/g, "Ae").replace(/Ö/g, "Oe").replace(/Ü/g, "Ue")
      .replace(/ß/g, "ss")
      .normalize("NFD").replace(/[̀-ͯ]/g, "");
  }

  /* --- Die Stile ---------------------------------------------------------- */

  function apa(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenApa(p, w) || txt(q.verlag) || w.ohneVerfasser;
    const jahr = jahrVon(q, w);
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk);
    const doi = doiVon(q), url = adresseVon(q), abruf = abrufVon(q, sprache, w);

    let mitte;
    if (werk) {
      const bandheft = zusammen([txt(q.band), txt(q.heft) ? "(" + txt(q.heft) + ")" : ""], "");
      mitte = zusammen([punkt(titel), zusammen([werk + (bandheft ? ", " + bandheft : ""),
               seitenVon(q)], ", ")], " ");
    } else {
      mitte = zusammen([punkt(titel), txt(q.verlag)], " ");
    }
    /* Die Praeposition kommt aus der Sprachtabelle.
     *
     * Sie stand als "von" fuer Deutsch und "from" fuer ALLES andere im Code —
     * spanische, franzoesische und japanische Eintraege lasen sich dadurch
     * "consultado el 2026-08-18, from https://…". Halb uebersetzt ist in einem
     * Literaturverzeichnis schlechter als gar nicht: Es sieht aus wie ein
     * Fehler des Verfassers. */
    const schluss = doi || (url
      ? (abruf ? `${w.abgerufen} ${abruf}, ${w.vonWort} ${url}` : url)
      : "");
    return zusammen([punkt(verf), `(${jahr}).`.replace("..", "."), punkt(mitte), schluss], " ");
  }

  function mla(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenMla(p, w);
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk) || txt(q.verlag);
    const jahr = jahrVon(q, w);
    const bandheft = zusammen([txt(q.band) ? "vol. " + txt(q.band) : "",
                               txt(q.heft) ? "no. " + txt(q.heft) : ""], ", ");
    const seiten = seitenVon(q) ? "pp. " + seitenVon(q) : "";
    const url = adresseVon(q), abruf = abrufVon(q, sprache, w);
    return zusammen([
      verf ? punkt(verf) : "",
      `"${titel}."`,
      // MLA trennt Werk und Bandangabe mit Komma, nicht mit Punkt.
      werk ? werk + "," : "",
      satzende(zusammen([bandheft, jahr, seiten], ", ")),
      verweisVon(q),
      abruf ? (sprache === "de" ? `${w.abgerufen} ${abruf}.` : `Accessed ${abruf}.`) : "",
    ], " ");
  }

  function chicago(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenChicago(p, w);
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk);
    const jahr = jahrVon(q, w);
    const url = adresseVon(q), abruf = abrufVon(q, sprache, w);
    const bandheft = zusammen([txt(q.band), txt(q.heft) ? "no. " + txt(q.heft) : ""], ", ");
    return zusammen([
      // Ohne Verfasser tritt der Herausgeber der Seite an dessen Stelle —
      // sonst begaenne der Eintrag mit der Jahresangabe.
      verf ? punkt(verf) : punkt(txt(q.verlag)),
      satzende(jahr),
      `"${titel}."`,
      werk ? zusammen([werk, bandheft], " ") + (seitenVon(q) ? ": " + seitenVon(q) : "") + "." : "",
      txt(q.verlag) && !werk && verf ? punkt(txt(q.verlag)) : "",
      verweisVon(q),
      abruf ? (sprache === "de" ? `(${w.abgerufen} ${abruf}).` : `(accessed ${abruf}).`) : "",
    ], " ");
  }

  function harvard(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenHarvard(p, w) || txt(q.verlag) || w.ohneVerfasser;
    const jahr = jahrVon(q, w);
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk);
    const url = adresseVon(q), abruf = abrufVon(q, sprache, w);
    const bandheft = zusammen([txt(q.band), txt(q.heft) ? "(" + txt(q.heft) + ")" : ""], "");
    const zielHarvard = verweisVon(q);
    return zusammen([
      punkt(verf), `(${jahr})`, punkt(titel),
      werk ? zusammen([werk, bandheft], ", ") + (seitenVon(q) ? ", " + w.seite + " " + seitenVon(q) : "") + "." : "",
      txt(q.verlag) && !werk ? punkt(txt(q.verlag)) : "",
      zielHarvard ? (sprache === "de" ? `${w.verfuegbar}: ${zielHarvard}` : `Available at: ${zielHarvard}`) : "",
      abruf ? (sprache === "de" ? `(${w.abgerufen} ${abruf}).` : `(Accessed: ${abruf}).`) : "",
    ], " ");
  }

  function din(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenDin(p, w) || txt(q.verlag).toUpperCase() || w.ohneVerfasser;
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk);
    const jahr = jahrVon(q, w);
    const url = adresseVon(q), abruf = abrufVon(q, sprache, w);
    const teile = [punkt(verf), titel + "."];
    if (werk) {
      teile.push(`${w.in}: ${werk}.`);
      const bh = zusammen([txt(q.band) ? w.band + " " + txt(q.band) : "",
                           txt(q.heft) ? w.heft + " " + txt(q.heft) : ""], ", ");
      if (bh) teile.push(bh + ",");
      teile.push(satzende(jahr + (seitenVon(q) ? ", " + w.seite + " " + seitenVon(q) : "")));
    } else {
      if (txt(q.verlag)) teile.push(txt(q.verlag) + ",");
      teile.push(satzende(jahr));
    }
    const zielDin = verweisVon(q);
    if (zielDin) teile.push(`URL: ${zielDin}`);
    if (abruf) teile.push(`– ${w.abgerufen} ${abruf}.`);
    return zusammen(teile, " ");
  }

  function iso690(q, sprache) {
    const w = wort(sprache), p = personen(q);
    const verf = autorenDin(p, w) || txt(q.verlag).toUpperCase();
    const titel = txt(q.titel) || w.ohneTitel;
    const werk = txt(q.journal) || txt(q.sammelwerk);
    const jahr = jahrVon(q, w);
    const url = adresseVon(q), abruf = abrufVon(q, sprache, w);
    return zusammen([
      verf ? punkt(verf) : "",
      titel + ".",
      `[${w.online}].`,
      werk ? `${w.in}: ${werk}.` : "",
      satzende(jahr + (seitenVon(q) ? ", " + w.seite + " " + seitenVon(q) : "")),
      txt(q.issn) ? "ISSN " + txt(q.issn) + "." : (txt(q.isbn) ? "ISBN " + txt(q.isbn) + "." : ""),
      abruf ? `[${sprache === "de" ? "Zugriff" : "viewed"} ${abruf}].` : "",
      url ? (sprache === "de" ? `Verfügbar unter: ${url}` : `Available from: ${url}`) : "",
    ], " ");
  }

  /* --- BibTeX ------------------------------------------------------------- */

  function bibtexSchluessel(q) {
    const p = personen(q);
    const nach = p.length ? p[0].nach : (txt(q.verlag) || "web");
    const jahr = txt(q.jahr) || (txt(q.datum).match(/(\d{4})/) || [, "oJ"])[1];
    const wort = (txt(q.titel).split(/\s+/)[0] || "quelle");
    return entzeichnen(nach + jahr + wort).replace(/[^A-Za-z0-9]/g, "").toLowerCase();
  }

  function bibtex(q) {
    const typ = q.art === "Zeitschriftenaufsatz" ? "article"
              : q.art === "Buchkapitel" ? "incollection"
              : q.art === "Buch" ? "book"
              : q.art === "Konferenzbeitrag" ? "inproceedings"
              : q.art === "Hochschulschrift" ? "phdthesis"
              : q.art === "Bericht" ? "techreport" : "misc";
    const f = [];
    const setze = (k, v) => { const t = txt(v); if (t) f.push("  " + k + " = {" + t.replace(/[{}]/g, "") + "}"); };
    const p = personen(q);
    if (p.length) setze("author", p.map(x => x.vor ? x.nach + ", " + x.vor : x.nach).join(" and "));
    setze("title", q.titel);
    setze("year", txt(q.jahr) || (txt(q.datum).match(/(\d{4})/) || [])[1]);
    if (q.journal) setze("journal", q.journal);
    if (q.sammelwerk) setze("booktitle", q.sammelwerk);
    setze("volume", q.band);
    setze("number", q.heft);
    if (seitenVon(q)) setze("pages", seitenVon(q).replace("–", "--"));
    setze("publisher", q.verlag);
    setze("doi", txt(q.doi).replace(/^https?:\/\/doi\.org\//i, ""));
    setze("isbn", q.isbn);
    setze("issn", q.issn);
    setze("url", adresseVon(q));
    setze("urldate", txt(q.abrufdatum) || txt(q.abrufzeit));
    setze("note", "Bildschirmaufnahme, kein Verlagsdokument");
    return "@" + typ + "{" + bibtexSchluessel(q) + ",\n" + f.join(",\n") + "\n}\n";
  }

  /* --- Die Datei ---------------------------------------------------------- */

  const STILE = [
    ["APA 7", apa], ["MLA 9", mla], ["Chicago", chicago],
    ["Harvard", harvard], ["DIN 1505-2", din], ["ISO 690", iso690],
  ];

  /* Baut den Text der Beleg-Datei.
   *
   * Bewusst eine reine Textdatei: sie laesst sich in jedem Programm oeffnen,
   * und wer eine Zeile braucht, markiert sie und kopiert. Ein PDF oder eine
   * Tabelle waere schoener anzusehen und umstaendlicher zu benutzen. */
  /* Ueberschriften und Hinweise der Belegdatei, je Sprache.
   *
   * Die Datei ist kein Beiwerk: Sie ist das, was der Nutzer nach der Aufnahme
   * tatsaechlich in die Hand nimmt. Sie in der Sprache der Oberflaeche zu
   * schreiben ist deshalb kein Zierrat — wer die Erweiterung auf Japanisch
   * gestellt hat, soll nicht deutsche Abschnittstitel lesen muessen. */
  const BLATT = {
    de: { kopf: "QUELLENANGABEN", titel: "Titel", adresse: "Adresse", abruf: "Abgerufen am",
          beleg: "Beleg-PDF", pruef: "Prüfsumme SHA-256", art: "Art", herkunft: "Angaben aus",
          eigene: "IN IHRER SPRACHE", englisch: "AUF ENGLISCH", bibtex: "BIBTEX",
          verfasser: "VERFASSER, WIE DIE SEITE SIE NENNT",
          verfasserHinweis: ["Die Zerlegung in Vor- und Nachname folgt der üblichen Annahme",
            "(letztes Wort = Nachname). Bei Namenszusätzen und ostasiatischen Namen",
            "kann sie falsch sein — hier die Rohform:"],
          kiKopf: "FÜR KI-WERKZEUGE",
          ki: ["Dieselben Angaben stecken im PDF selbst, in den Dokumenteigenschaften",
               "(Autor, Titel, Stichwörter, DOI, Zeitschrift) und als XMP-Datensatz.",
               "Ein Sprachmodell oder ein Literaturprogramm liest sie direkt aus der",
               "Datei, ohne diese Textdatei zu benötigen. Der RIS-Satz liegt zusätzlich",
               "als Anlage im PDF."],
          warnUnvoll: ["ACHTUNG: Die Seite gibt nicht alle Pflichtangaben her. Die Einträge",
                       "unten sind entsprechend unvollständig — bitte vor der Abgabe prüfen."],
          risKopf: "RIS-DATENSATZ (für Zotero, Citavi, EndNote)",
          risHinweis: ["Diesen Block in eine leere Datei mit der Endung .ris kopieren,",
                       "dann per Doppelklick importieren. Er steckt auch als Anlage im PDF."],
          fuss: ["Erzeugt von Full Page PDF Snap. Die Angaben stammen aus der Seite selbst,",
                 "nicht aus einer Literaturdatenbank. Der Beleg ist eine Bildschirmaufnahme,",
                 "kein Verlagsdokument."] },
    en: { kopf: "CITATION DETAILS", titel: "Title", adresse: "URL", abruf: "Retrieved",
          beleg: "Evidence PDF", pruef: "Checksum SHA-256", art: "Type", herkunft: "Details from",
          eigene: "IN YOUR LANGUAGE", englisch: "IN ENGLISH", bibtex: "BIBTEX",
          verfasser: "AUTHORS AS THE PAGE NAMES THEM",
          verfasserHinweis: ["Splitting into first and last name follows the usual assumption",
            "(last word = surname). With name particles and East Asian names it can be",
            "wrong — the raw form is listed here:"],
          kiKopf: "FOR AI TOOLS",
          ki: ["The same details are inside the PDF itself, in the document properties",
               "(author, title, keywords, DOI, journal) and as an XMP record. A language",
               "model or reference manager reads them straight from the file, without",
               "needing this text file. The RIS record is attached to the PDF as well."],
          warnUnvoll: ["NOTE: The page does not supply every required detail. The entries",
                       "below are incomplete accordingly — please check before submitting."],
          risKopf: "RIS RECORD (for Zotero, Citavi, EndNote)",
          risHinweis: ["Copy this block into an empty file with the extension .ris,",
                       "then import it by double-click. It is also attached to the PDF."],
          fuss: ["Produced by Full Page PDF Snap. The details come from the page itself,",
                 "not from a bibliographic database. The evidence is a screen capture,",
                 "not a publisher's document."] },
    es: { kopf: "DATOS DE CITA", titel: "Título", adresse: "URL", abruf: "Consultado el",
          beleg: "PDF de evidencia", pruef: "Suma SHA-256", art: "Tipo", herkunft: "Datos de",
          eigene: "EN SU IDIOMA", englisch: "EN INGLÉS", bibtex: "BIBTEX",
          verfasser: "AUTORES SEGÚN LOS NOMBRA LA PÁGINA",
          verfasserHinweis: ["La división en nombre y apellido sigue la suposición habitual",
            "(última palabra = apellido). Con partículas y nombres de Asia oriental puede",
            "ser incorrecta; aquí está la forma original:"],
          kiKopf: "PARA HERRAMIENTAS DE IA",
          ki: ["Los mismos datos están dentro del propio PDF, en las propiedades del",
               "documento (autor, título, palabras clave, DOI, revista) y como registro",
               "XMP. Un modelo de lenguaje o un gestor bibliográfico los lee directamente",
               "del archivo, sin necesitar este texto. El registro RIS también va adjunto."],
          warnUnvoll: ["ATENCIÓN: La página no aporta todos los datos obligatorios. Las",
                       "entradas siguientes están incompletas; revíselas antes de entregar."],
          risKopf: "REGISTRO RIS (para Zotero, Citavi, EndNote)",
          risHinweis: ["Copie este bloque en un archivo vacío con la extensión .ris y",
                       "ábralo con doble clic. También va adjunto al PDF."],
          fuss: ["Generado por Full Page PDF Snap. Los datos proceden de la propia página,",
                 "no de una base de datos bibliográfica. La evidencia es una captura de",
                 "pantalla, no un documento editorial."] },
    fr: { kopf: "RÉFÉRENCES", titel: "Titre", adresse: "URL", abruf: "Consulté le",
          beleg: "PDF de preuve", pruef: "Somme SHA-256", art: "Type", herkunft: "Données de",
          eigene: "DANS VOTRE LANGUE", englisch: "EN ANGLAIS", bibtex: "BIBTEX",
          verfasser: "AUTEURS TELS QUE LA PAGE LES NOMME",
          verfasserHinweis: ["La séparation prénom / nom suit l’hypothèse habituelle",
            "(dernier mot = nom). Avec les particules et les noms est-asiatiques, elle",
            "peut être fausse — voici la forme brute :"],
          kiKopf: "POUR LES OUTILS D’IA",
          ki: ["Les mêmes données figurent dans le PDF lui-même, dans les propriétés du",
               "document (auteur, titre, mots-clés, DOI, revue) et sous forme XMP. Un",
               "modèle de langage ou un gestionnaire bibliographique les lit directement",
               "dans le fichier, sans ce texte. L’enregistrement RIS y est aussi joint."],
          warnUnvoll: ["ATTENTION : la page ne fournit pas toutes les indications requises.",
                       "Les entrées ci-dessous sont incomplètes — vérifiez avant de rendre."],
          risKopf: "ENREGISTREMENT RIS (pour Zotero, Citavi, EndNote)",
          risHinweis: ["Copiez ce bloc dans un fichier vide portant l’extension .ris,",
                       "puis importez-le par double-clic. Il est aussi joint au PDF."],
          fuss: ["Produit par Full Page PDF Snap. Les données proviennent de la page",
                 "elle-même, non d’une base bibliographique. La preuve est une capture",
                 "d’écran, pas un document d’éditeur."] },
    it: { kopf: "DATI DI CITAZIONE", titel: "Titolo", adresse: "URL", abruf: "Consultato il",
          beleg: "PDF di prova", pruef: "Checksum SHA-256", art: "Tipo", herkunft: "Dati da",
          eigene: "NELLA SUA LINGUA", englisch: "IN INGLESE", bibtex: "BIBTEX",
          verfasser: "AUTORI COME LI INDICA LA PAGINA",
          verfasserHinweis: ["La divisione in nome e cognome segue l’ipotesi consueta",
            "(ultima parola = cognome). Con particelle e nomi dell’Asia orientale può",
            "essere errata — ecco la forma grezza:"],
          kiKopf: "PER STRUMENTI DI IA",
          ki: ["Gli stessi dati si trovano nel PDF stesso, nelle proprietà del documento",
               "(autore, titolo, parole chiave, DOI, rivista) e come record XMP. Un",
               "modello linguistico o un gestore bibliografico li legge direttamente dal",
               "file, senza questo testo. Il record RIS è allegato al PDF."],
          warnUnvoll: ["ATTENZIONE: la pagina non fornisce tutti i dati obbligatori. Le voci",
                       "seguenti sono incomplete — verificarle prima della consegna."],
          risKopf: "RECORD RIS (per Zotero, Citavi, EndNote)",
          risHinweis: ["Copiare questo blocco in un file vuoto con estensione .ris,",
                       "poi importarlo con doppio clic. È allegato anche al PDF."],
          fuss: ["Prodotto da Full Page PDF Snap. I dati provengono dalla pagina stessa,",
                 "non da una banca dati bibliografica. La prova è una schermata,",
                 "non un documento editoriale."] },
    pt: { kopf: "DADOS DE CITAÇÃO", titel: "Título", adresse: "URL", abruf: "Acessado em",
          beleg: "PDF de evidência", pruef: "Soma SHA-256", art: "Tipo", herkunft: "Dados de",
          eigene: "NO SEU IDIOMA", englisch: "EM INGLÊS", bibtex: "BIBTEX",
          verfasser: "AUTORES CONFORME A PÁGINA OS NOMEIA",
          verfasserHinweis: ["A divisão em nome e sobrenome segue a suposição habitual",
            "(última palavra = sobrenome). Com partículas e nomes do Leste Asiático pode",
            "estar errada — eis a forma original:"],
          kiKopf: "PARA FERRAMENTAS DE IA",
          ki: ["Os mesmos dados estão dentro do próprio PDF, nas propriedades do documento",
               "(autor, título, palavras-chave, DOI, periódico) e como registro XMP. Um",
               "modelo de linguagem ou gerenciador bibliográfico os lê diretamente do",
               "arquivo, sem este texto. O registro RIS também está anexado ao PDF."],
          warnUnvoll: ["ATENÇÃO: A página não fornece todos os dados obrigatórios. As",
                       "entradas abaixo estão incompletas — verifique antes de entregar."],
          risKopf: "REGISTRO RIS (para Zotero, Citavi, EndNote)",
          risHinweis: ["Copie este bloco para um arquivo vazio com a extensão .ris e",
                       "importe-o com duplo clique. Ele também está anexado ao PDF."],
          fuss: ["Produzido por Full Page PDF Snap. Os dados vêm da própria página,",
                 "não de uma base bibliográfica. A evidência é uma captura de tela,",
                 "não um documento editorial."] },
    ru: { kopf: "БИБЛИОГРАФИЧЕСКИЕ ДАННЫЕ", titel: "Заглавие", adresse: "Адрес",
          abruf: "Дата обращения", beleg: "PDF-подтверждение", pruef: "Контрольная сумма SHA-256",
          art: "Тип", herkunft: "Данные из",
          eigene: "НА ВАШЕМ ЯЗЫКЕ", englisch: "НА АНГЛИЙСКОМ", bibtex: "BIBTEX",
          verfasser: "АВТОРЫ, КАК ИХ НАЗЫВАЕТ СТРАНИЦА",
          verfasserHinweis: ["Разделение на имя и фамилию следует обычному допущению",
            "(последнее слово — фамилия). Для приставок и восточноазиатских имён оно",
            "может быть неверным — вот исходный вид:"],
          kiKopf: "ДЛЯ ИИ-ИНСТРУМЕНТОВ",
          ki: ["Те же данные находятся в самом PDF — в свойствах документа (автор,",
               "заглавие, ключевые слова, DOI, журнал) и в виде записи XMP. Языковая",
               "модель или менеджер литературы читает их прямо из файла, без этого",
               "текста. Запись RIS также вложена в PDF."],
          warnUnvoll: ["ВНИМАНИЕ: страница даёт не все обязательные сведения. Записи ниже",
                       "соответственно неполны — проверьте их перед сдачей."],
          risKopf: "ЗАПИСЬ RIS (для Zotero, Citavi, EndNote)",
          risHinweis: ["Скопируйте этот блок в пустой файл с расширением .ris и откройте",
                       "его двойным щелчком. Он также вложен в PDF."],
          fuss: ["Создано Full Page PDF Snap. Сведения взяты с самой страницы, а не из",
                 "библиографической базы. Подтверждение — снимок экрана, а не документ",
                 "издательства."] },
    ja: { kopf: "引用情報", titel: "タイトル", adresse: "URL", abruf: "取得日時",
          beleg: "証拠 PDF", pruef: "チェックサム SHA-256", art: "種別", herkunft: "情報源",
          eigene: "お使いの言語", englisch: "英語", bibtex: "BIBTEX",
          verfasser: "ページに記載された著者名",
          verfasserHinweis: ["姓名の分割は一般的な想定（最後の語を姓とみなす）によります。",
            "冠称のある名前や東アジアの名前では誤ることがあります。原形は次のとおりです:"],
          kiKopf: "AI ツール向け",
          ki: ["同じ情報は PDF 自体の文書プロパティ（著者・タイトル・キーワード・DOI・",
               "雑誌名）と XMP レコードにも入っています。言語モデルや文献管理ソフトは",
               "このテキストを使わずにファイルから直接読み取れます。RIS レコードも PDF に",
               "添付されています。"],
          warnUnvoll: ["注意: このページからは必須項目のすべてを取得できませんでした。",
                       "以下の記載は不完全です。提出前にご確認ください。"],
          risKopf: "RIS レコード（Zotero・Citavi・EndNote 用）",
          risHinweis: ["このブロックを拡張子 .ris の空ファイルにコピーし、ダブルクリックで",
                       "取り込んでください。PDF にも添付されています。"],
          fuss: ["Full Page PDF Snap により作成。情報はページ自体から取得したもので、",
                 "文献データベースによるものではありません。証拠は画面の取り込みであり、",
                 "出版社の文書ではありません。"] },
    zh: { kopf: "引用信息", titel: "标题", adresse: "网址", abruf: "访问时间",
          beleg: "证据 PDF", pruef: "校验和 SHA-256", art: "类型", herkunft: "信息来源",
          eigene: "您的语言", englisch: "英文", bibtex: "BIBTEX",
          verfasser: "页面所标注的作者",
          verfasserHinweis: ["姓名拆分依据通常的假设（最后一个词为姓）。对于带有前缀的姓名",
            "和东亚姓名可能有误，以下为原始形式:"],
          kiKopf: "供 AI 工具使用",
          ki: ["相同信息也写在 PDF 本身的文档属性中（作者、标题、关键词、DOI、期刊），",
               "并以 XMP 记录保存。语言模型或文献管理软件可直接从文件读取，无需本文本。",
               "RIS 记录同样作为附件存于 PDF 中。"],
          warnUnvoll: ["注意: 该页面未提供全部必需信息。下列条目相应不完整，提交前请核对。"],
          risKopf: "RIS 记录（用于 Zotero、Citavi、EndNote）",
          risHinweis: ["将此段复制到扩展名为 .ris 的空文件中，双击即可导入。",
                       "该记录也已附在 PDF 中。"],
          fuss: ["由 Full Page PDF Snap 生成。信息取自页面本身，而非文献数据库。",
                 "证据为屏幕截图，并非出版社文档。"] },
  };

  function blatt(sprache) {
    if (BLATT[sprache]) return BLATT[sprache];
    const kurz = String(sprache || "").split(/[-_]/)[0];
    return BLATT[kurz] || BLATT.en;
  }

  /* Baut den Text der Beleg-Datei.
   *
   * Bewusst eine reine Textdatei: Sie laesst sich in jedem Programm oeffnen,
   * und wer eine Zeile braucht, markiert sie und kopiert. Ein PDF oder eine
   * Tabelle waere schoener anzusehen und umstaendlicher zu benutzen.
   *
   * Ausgegeben wird in der Sprache der Oberflaeche und zusaetzlich auf
   * Englisch. Zwei Fassungen, weil Hochschulen im deutschsprachigen Raum
   * regelmaessig englische Zitierweisen verlangen — und weil die Stilnamen
   * selbst (APA, MLA, Chicago) ohnehin englisch sind. */
  function belegDatei(q, zusatz, sprache) {
    const z = zusatz || {};
    const sp = sprache || "de";
    const b = blatt(sp);
    const zeilen = [];
    const trenner = "-".repeat(72);

    zeilen.push(b.kopf);
    zeilen.push(trenner);
    zeilen.push(b.titel.padEnd(18) + ": " + (txt(q.titel) || "-"));
    zeilen.push(b.adresse.padEnd(18) + ": " + (adresseVon(q) || "-"));
    zeilen.push(b.abruf.padEnd(18) + ": " + (txt(q.abrufzeit) || txt(q.abrufdatum) || "-"));
    if (z.pdfDatei) zeilen.push(b.beleg.padEnd(18) + ": " + z.pdfDatei);
    if (z.pruefsumme) zeilen.push(b.pruef.padEnd(18) + ": " + z.pruefsumme);
    zeilen.push(b.art.padEnd(18) + ": " + (txt(q.art) || "-"));
    zeilen.push(b.herkunft.padEnd(18) + ": " + (txt(q.herkunft) || "-"));

    if (q.vollstaendig === false) { zeilen.push(""); b.warnUnvoll.forEach(l => zeilen.push(l)); }
    if (txt(q.warnung)) { zeilen.push(""); zeilen.push("ACHTUNG: " + txt(q.warnung)); }

    /* Der Hinweis auf die Dokumenteigenschaften steht WEIT OBEN.
     * Wer diese Datei einem Sprachmodell vorlegt, soll gleich erfahren, dass
     * es die Angaben auch maschinenlesbar im PDF gibt — sonst wird die
     * Textdatei geparst, obwohl daneben ein sauberer Datensatz liegt. */
    zeilen.push("");
    zeilen.push(trenner);
    zeilen.push(b.kiKopf);
    zeilen.push(trenner);
    b.ki.forEach(l => zeilen.push(l));

    // Erst die Sprache der Oberflaeche, dann Englisch. Ist die Oberflaeche
    // englisch, entfaellt die Wiederholung.
    const fassungen = (sp === "en" || sp.startsWith("en"))
      ? [["en", b.englisch]]
      : [[sp, b.eigene], ["en", b.englisch]];   // in der Sprache des Nutzers beschriftet

    for (const [lang, ueberschrift] of fassungen) {
      zeilen.push("");
      zeilen.push(trenner);
      zeilen.push(ueberschrift);
      zeilen.push(trenner);
      for (const [name, bauen] of STILE) {
        let eintrag;
        try { eintrag = bauen(q, lang); }
        catch (e) { eintrag = "(" + (e && e.message) + ")"; }
        zeilen.push("");
        zeilen.push(name + ":");
        zeilen.push(eintrag);
      }
    }

    zeilen.push("");
    zeilen.push(trenner);
    zeilen.push(b.bibtex);
    zeilen.push(trenner);
    zeilen.push(bibtex(q));

    /* Der RIS-Satz gehoert in dieselbe Datei.
     *
     * Er lag bis 2.35.10 als eigene .ris daneben — und kam bei vielen Nutzern
     * gar nicht an: Chrome laesst eine Erweiterung nur EINEN Download ohne
     * Rueckfrage ablegen; weitere werden stillschweigend verworfen, solange
     * der Nutzer "mehrere Dateien" nicht ausdruecklich erlaubt hat. Das PDF
     * kam durch, die Beilagen nicht.
     *
     * Eine Datei statt drei loest das unabhaengig von der Einstellung des
     * Browsers. Wer den Satz in Zotero oder Citavi braucht, kopiert den Block
     * unten in eine leere .ris-Datei — oder holt ihn aus dem PDF, wo er als
     * Anlage steckt. */
    if (z.ris) {
      zeilen.push(trenner);
      zeilen.push(b.risKopf);
      zeilen.push(trenner);
      b.risHinweis.forEach(l => zeilen.push(l));
      zeilen.push("");
      zeilen.push(String(z.ris).replace(/\r\n/g, "\n").trim());
      zeilen.push("");
    }

    const roh = (q.autoren || []).filter(Boolean);
    if (roh.length) {
      zeilen.push(trenner);
      zeilen.push(b.verfasser);
      zeilen.push(trenner);
      b.verfasserHinweis.forEach(l => zeilen.push(l));
      zeilen.push("");
      roh.forEach(a => zeilen.push("  " + a));
      zeilen.push("");
    }

    zeilen.push(trenner);
    b.fuss.forEach(l => zeilen.push(l));
    if (z.version) zeilen.push("Version " + z.version);

    return zeilen.join("\r\n") + "\r\n";
  }

  return {
    belegDatei, bibtex,
    apa, mla, chicago, harvard, din, iso690,
    namenTeilen, STILE,
  };
})();

if (typeof globalThis !== "undefined") globalThis.PageShotZitate = PageShotZitate;
