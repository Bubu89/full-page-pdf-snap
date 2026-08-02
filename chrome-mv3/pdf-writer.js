// Minimaler PDF/1.4 Image-Writer.
// Eingabe: Array von Seiten. Jede Seite ist eines von:
//   (legacy) { jpegBytes:Uint8Array, widthPx, heightPx }       — ein Bild fuellt die Seite
//   (tiled)  { widthPx, heightPx, tiles:[{ jpegBytes, xPx, yPx, wPx, hPx }, ...] }
// Ausgabe: Uint8Array (komplettes PDF).
// Strategie: JPEGs direkt als XObject mit /Filter /DCTDecode einbetten (kein Re-Encode).
// Tile-Modus: mehrere JPEGs auf einer PDF-Seite — wirkt wie eine fortlaufende Seite,
// aber jedes JPEG ist klein genug, damit der Encoder Chroma-Subsampling effizient nutzt.

(function (root) {
  "use strict";

  function strToBytes(s) {
    const out = new Uint8Array(s.length);
    for (let i = 0; i < s.length; i++) out[i] = s.charCodeAt(i) & 0xff;
    return out;
  }

  function concatBytes(parts) {
    let total = 0;
    for (const p of parts) total += p.length;
    const out = new Uint8Array(total);
    let off = 0;
    for (const p of parts) { out.set(p, off); off += p.length; }
    return out;
  }

  // --- Nachweiszeile und Metadaten -----------------------------------------
  //
  // Eine Bildschirmaufnahme ist KEIN qualifiziertes elektronisches Dokument im
  // Sinne der eIDAS-Verordnung. Sie traegt keine Signatur und keinen
  // vertrauenswuerdigen Zeitstempel, und niemand ausser dem Erzeuger bezeugt
  // sie. Was sie leisten kann, ist Selbstdokumentation: festhalten, welche
  // Adresse wann abgerufen wurde und dass die Datei seither unveraendert ist.
  //
  // Genau das — und nichts darueber hinaus — sagt die Fussnote. Der Wortlaut
  // ist bewusst zurueckhaltend: Der Zeitstempel stammt von der Geraeteuhr, die
  // Pruefsumme deckt die Bilddaten dieser Datei ab, nicht den Inhalt der
  // Website. Wer mehr braucht, braucht einen qualifizierten Zeitstempeldienst.
  //
  // Die Zeile steht auf Englisch, auch wenn die Oberflaeche uebersetzt ist:
  // Standard-PDF-Schriften koennen nur WinAnsi darstellen, und eine Fussnote,
  // die auf Japanisch oder Russisch zu Kaestchen zerfaellt, dokumentiert
  // nichts. Englisch ist im Zweifel lesbar.
  const HINWEIS =
    "Self-made screen capture. Not a qualified electronic document (eIDAS). " +
    "Time from device clock. Checksum covers this file's image data only, " +
    "not the authenticity of the page.";

  function pdfString(s) {
    // Klammern und Backslash sind in PDF-Literalstrings Steuerzeichen.
    return String(s).replace(/[\\()]/g, "\\$&").replace(/[\r\n]/g, " ");
  }

  // --- Quellenangabe --------------------------------------------------------
  //
  // Formatiert wird nach APA 7, weil es im deutschsprachigen Studium die
  // haeufigste Vorgabe ist. Wer eine andere Zitierweise braucht, nimmt den
  // RIS-Satz und laesst das Literaturprogramm formatieren — deshalb liegt er
  // dem PDF bei. Umgeschrieben wird nichts: liegt ein Feld nicht vor, fehlt
  // es in der Ausgabe, statt geraten zu werden.

  /** "Nachname, V." — nur wenn die Form erkennbar ist, sonst unveraendert. */
  function autorKurz(name) {
    var s = String(name || "").trim();
    if (!s) return "";
    if (s.indexOf(",") > 0) {
      var t = s.split(",");
      var nach = t[0].trim();
      var vor = t.slice(1).join(" ").trim();
      if (!vor) return nach;
      var ini = vor.split(/[\s.]+/).filter(Boolean)
                   .map(function (w) { return w.charAt(0).toUpperCase() + "."; }).join(" ");
      return nach + ", " + ini;
    }
    // Ohne Komma steht ueblicherweise "Vorname(n) Nachname". Namenszusaetze
    // wie "van der" oder "de la" gehoeren zum Nachnamen und lassen sich nicht
    // sicher abtrennen — solche Namen bleiben unveraendert stehen. Ein falsch
    // zerlegter Name ist schlimmer als ein nicht gekuerzter.
    var w = s.split(/\s+/).filter(Boolean);
    if (w.length < 2) return s;
    if (w.some(function (x) {
      return /^(van|von|de|der|den|del|della|di|da|dos|du|la|le|al|bin|ibn|ter|zu|zum)$/i.test(x);
    })) return s;
    var nachname = w[w.length - 1];
    var ini = w.slice(0, -1).map(function (x) {
      return x.charAt(0).toUpperCase() + ".";
    }).join(" ");
    return nachname + ", " + ini;
  }

  function autorenListe(autoren) {
    var a = (autoren || []).map(autorKurz).filter(Boolean);
    if (!a.length) return "";
    if (a.length === 1) return a[0];
    if (a.length > 20) return a.slice(0, 19).join(", ") + ", … " + a[a.length - 1];
    return a.slice(0, -1).join(", ") + " & " + a[a.length - 1];
  }

  /** Eine Zeile im Literaturverzeichnis-Format. */
  function zitation(q) {
    if (!q || !q.titel) return "";
    // Sieht die Seite nach Fehlermeldung oder Zugangsschranke aus, waere eine
    // formatierte Quellenangabe eine Behauptung ueber etwas, das gar nicht
    // erfasst wurde. Dann steht dort der Hinweis statt der Zitation.
    if (q.warnung) return "Keine belastbare Quellenangabe: " + q.warnung;
    var t = [];
    var au = autorenListe(q.autoren);
    if (au) t.push(au + " ");
    t.push("(" + (q.jahr || "o. J.") + "). ");
    t.push(q.titel.replace(/\s+/g, " ").trim());
    if (!/[.?!]$/.test(q.titel.trim())) t.push(".");
    var seiten = q.seiteVon
      ? q.seiteVon + (q.seiteBis && q.seiteBis !== q.seiteVon ? "–" + q.seiteBis : "")
      : "";
    if (q.sammelwerk) {
      // Beitrag in einem Sammel- oder Tagungsband: "In <Werk> (S. x–y). Verlag."
      t.push(" In " + q.sammelwerk);
      if (seiten) t.push(" (S. " + seiten + ")");
      t.push(".");
      if (q.verlag) t.push(" " + q.verlag + ".");
    } else if (q.journal) {
      t.push(" " + q.journal);
      if (q.band) t.push(", " + q.band + (q.heft ? "(" + q.heft + ")" : ""));
      if (seiten) t.push(", " + seiten);
      t.push(".");
    } else if (q.art === "Hochschulschrift") {
      t.push(" [Hochschulschrift]." + (q.verlag ? " " + q.verlag + "." : ""));
    } else if (q.art === "Video") {
      t.push(" [Video]." + (q.verlag ? " " + q.verlag + "." : ""));
    } else if (q.verlag) {
      t.push(" " + q.verlag + ".");
    }
    if (q.doi) t.push(" https://doi.org/" + q.doi.replace(/^https?:\/\/(dx\.)?doi\.org\//i, ""));
    else if (q.urlZitat || q.url) {
      t.push(" " + (q.urlZitat || q.url));
      // Ohne DOI haengt der Nachweis an der Adresse — und die kann sich
      // aendern. Dann gehoert der Abrufzeitpunkt in die Angabe.
      if (q.abrufdatum) t.push(" (abgerufen am " + q.abrufdatum + ")");
    }
    return t.join("");
  }

  /** RIS-Satz — das Austauschformat, das Citavi, Zotero und EndNote lesen. */
  function risSatz(q) {
    var typ = q.art === "Zeitschriftenaufsatz" ? "JOUR"
            : q.art === "Buchkapitel" ? "CHAP"
            : q.art === "Buch" ? "BOOK"
            : q.art === "Konferenzbeitrag" ? "CPAPER"
            : q.art === "Hochschulschrift" ? "THES"
            : q.art === "Bericht" ? "RPRT"
            : q.art === "Datensatz" ? "DATA"
            : q.art === "Video" ? "VIDEO"
            : q.art === "Preprint" ? "UNPB" : "ELEC";
    var z = ["TY  - " + typ];
    var setze = function (k, v) { if (v) z.push(k + "  - " + String(v).replace(/[\r\n]+/g, " ")); };
    (q.autoren || []).forEach(function (a) { setze("AU", a); });
    setze("TI", q.titel);
    setze("PY", q.jahr);
    // RIS erwartet in DA das Format JJJJ/MM/TT. Verlagsangaben wie
    // "Jun 23, 2023" wuerden Importprogramme stolpern lassen — dann bleibt
    // es beim Jahr in PY, das jeder Importer versteht.
    var iso = String(q.datum || "").match(/^(\d{4})[-/](\d{2})[-/](\d{2})/);
    if (iso) setze("DA", iso[1] + "/" + iso[2] + "/" + iso[3]);
    // Bei Beitraegen in Sammelbaenden gehoert der Werktitel in T2, nicht in
    // JO — Literaturprogramme setzen JO nur bei Periodika.
    if (q.sammelwerk) setze("T2", q.sammelwerk);
    else setze("JO", q.journal);
    setze("VL", q.band);
    setze("IS", q.heft);
    setze("SP", q.seiteVon);
    setze("EP", q.seiteBis);
    setze("DO", q.doi);
    setze("SN", q.isbn || q.issn);
    setze("PB", q.verlag);
    setze("LA", q.sprache);
    setze("UR", q.urlZitat || q.url);
    // Y2 ist im RIS-Standard das Abrufdatum. Die Uhrzeit gehoert dazu:
    // Seiten aendern sich im Lauf eines Tages, und ein Beleg ohne Uhrzeit
    // laesst sich einer Fassung nicht zuordnen.
    setze("Y2", q.abrufzeit || q.abrufdatum);
    if (q.fassung && q.fassung !== q.url) setze("L2", q.fassung);
    (q.dateien || []).forEach(function (d) {
      if (d.art === "pdf") setze("L1", d.url);
    });
    setze("C1", q.lizenz);
    if (q.geaendert) setze("C2", "zuletzt geaendert: " + q.geaendert);
    setze("N1", (q.warnung ? "ACHTUNG: " + q.warnung + " " : "") +
                "Angaben aus: " + (q.herkunft || "der Seite") +
                ". Bildschirmaufnahme, kein Verlagsdokument." +
                (q.zeitzone ? " Zeitzone des Geraets: " + q.zeitzone + "." : ""));
    z.push("ER  - ");
    return z.join("\r\n") + "\r\n";
  }

  // --- Textebene ------------------------------------------------------------
  //
  // Der Text stammt aus dem Dokument, nicht aus einer Erkennung des Bildes.
  // Das ist der ganze Punkt: Gemessen an einer echten Seite liegt der
  // Wort-Recall bei 100 % gegen 92,6 % bei OCR, weil nichts geraten wird.
  //
  // Er wird unsichtbar gesetzt (Textrendermodus 3) und deckt sich mit dem, was
  // das Bild zeigt. Ein PDF, dessen unsichtbarer Text etwas anderes sagt als
  // das sichtbare Bild, waere irrefuehrend — deshalb stammen Bild und Text aus
  // demselben Seitenzustand, und die Metadaten halten fest, dass es eine
  // DOM-Uebernahme ist und keine Erkennung. Beide haben andere Fehlermodi:
  // OCR verliest sich, eine DOM-Uebernahme kann Text mitnehmen, den eine
  // Ueberdeckung im Bild verbirgt.

  // Zeichenbreiten von Helvetica in 1/1000 em, aus der PDF-Spezifikation.
  // Sie stecken in jedem Betrachter, deshalb muss nichts eingebettet werden.
  var HELV = {32:278,33:278,34:355,35:556,36:556,37:889,38:667,39:191,40:333,41:333,
  42:389,43:584,44:278,45:333,46:278,47:278,48:556,49:556,50:556,51:556,52:556,53:556,
  54:556,55:556,56:556,57:556,58:278,59:278,60:584,61:584,62:584,63:556,64:1015,65:667,
  66:667,67:722,68:722,69:667,70:611,71:778,72:722,73:278,74:500,75:667,76:556,77:833,
  78:722,79:778,80:667,81:778,82:722,83:667,84:611,85:722,86:667,87:944,88:667,89:667,
  90:611,91:278,92:278,93:278,94:469,95:556,96:333,97:556,98:556,99:500,100:556,101:556,
  102:278,103:556,104:556,105:222,106:222,107:500,108:222,109:833,110:556,111:556,
  112:556,113:556,114:333,115:500,116:278,117:556,118:500,119:722,120:500,121:500,
  122:500,123:334,124:260,125:334,126:584};

  // WinAnsiEncoding ist CP1252, nicht Latin-1: Gedankenstrich, typografische
  // Anfuehrungszeichen und Auslassungspunkte sind darstellbar. An einer echten
  // Seite gemessen passen damit 100 % der Zeichen.
  var CP1252 = {0x20ac:0x80,0x201a:0x82,0x0192:0x83,0x201e:0x84,0x2026:0x85,0x2020:0x86,
  0x2021:0x87,0x02c6:0x88,0x2030:0x89,0x0160:0x8a,0x2039:0x8b,0x0152:0x8c,0x017d:0x8e,
  0x2018:0x91,0x2019:0x92,0x201c:0x93,0x201d:0x94,0x2022:0x95,0x2013:0x96,0x2014:0x97,
  0x02dc:0x98,0x2122:0x99,0x0161:0x9a,0x203a:0x9b,0x0153:0x9c,0x017e:0x9e,0x0178:0x9f};

  function nachWinAnsi(s) {
    var out = "";
    for (var i = 0; i < s.length; i++) {
      var c = s.codePointAt(i);
      if (c > 0xffff) { i++; continue; }          // ausserhalb der BMP: kein Platz
      if (c < 0x100) out += s[i];
      else if (CP1252[c] !== undefined) out += String.fromCharCode(CP1252[c]);
      // alles andere faellt weg — lieber eine Luecke als ein falsches Zeichen
    }
    return out;
  }

  function breiteEm(s) {
    var b = 0;
    for (var i = 0; i < s.length; i++) {
      var c = s.charCodeAt(i);
      b += (HELV[c] !== undefined ? HELV[c] : 556) / 1000;
    }
    return b;
  }

  /**
   * Erzeugt die PDF-Anweisungen fuer die unsichtbare Textebene einer Seite.
   * anfangYpx ist die Position dieser Seite im Gesamtbild — bei einer
   * einzelnen Seite null, im mehrseitigen Modus der Beginn des Ausschnitts.
   * Woerter ausserhalb des Ausschnitts gehoeren auf eine andere Seite.
   */
  function textebene(woerter, skala, seitenHoehePx, versatzYpt, pxToPt, anfangYpx) {
    var s = "";
    var anfang = anfangYpx || 0;
    for (var i = 0; i < woerter.length; i++) {
      var wo = woerter[i];
      var txt = nachWinAnsi(String(wo.t || ""));
      if (!txt) continue;

      var groessePt = wo.s * skala * pxToPt;
      if (groessePt < 0.5 || groessePt > 400) continue;

      // Grundlinie: Der Kasten umfasst die Zeilenhoehe, der Text sitzt darin
      // mittig. Helvetica hat 0.718 em Oberlaenge — so weit unter der Oberkante
      // des Textes liegt die Grundlinie.
      var ueberschuss = Math.max(0, (wo.h - wo.s)) * skala;
      var grundlinieYpx = (wo.y * skala) + ueberschuss / 2 + (wo.s * skala * 0.718) - anfang;
      if (grundlinieYpx < 0 || grundlinieYpx > seitenHoehePx) continue;

      var natuerlich = breiteEm(txt) * groessePt;
      var ziel = wo.w * skala * pxToPt;
      var tz = natuerlich > 0 ? (ziel / natuerlich) * 100 : 100;
      if (!isFinite(tz)) tz = 100;
      tz = Math.max(5, Math.min(600, tz));

      s += "BT 3 Tr /F1 " + groessePt.toFixed(2) + " Tf " + tz.toFixed(1) + " Tz " +
           (wo.x * skala * pxToPt).toFixed(2) + " " +
           ((seitenHoehePx - grundlinieYpx) * pxToPt + versatzYpt).toFixed(2) +
           " Td (" + pdfString(txt) + ") Tj ET\n";
    }
    return s;
  }

  function pdfTextString(s) {
    // Nicht-ASCII in Dokumentinformationen: UTF-16BE mit Byte-Order-Mark.
    // eslint-disable-next-line no-control-regex
    if (/^[\x20-\x7e]*$/.test(s)) return "(" + pdfString(s) + ")";
    let hex = "FEFF";
    for (const ch of String(s)) {
      const c = ch.codePointAt(0);
      if (c > 0xffff) {
        const v = c - 0x10000;
        hex += (0xd800 + (v >> 10)).toString(16).padStart(4, "0");
        hex += (0xdc00 + (v & 0x3ff)).toString(16).padStart(4, "0");
      } else {
        hex += c.toString(16).padStart(4, "0");
      }
    }
    return "<" + hex.toUpperCase() + ">";
  }

  function pdfDate(d) {
    // PDF-Datum nach ISO 32000: D:YYYYMMDDHHmmSSOHH'mm — mit Zeitzonenversatz,
    // damit "wann" ohne Kenntnis des Geraets nachvollziehbar bleibt.
    const p = (n) => String(Math.abs(n)).padStart(2, "0");
    const off = -d.getTimezoneOffset();
    const sign = off === 0 ? "Z" : (off > 0 ? "+" : "-");
    return "D:" + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) +
      p(d.getHours()) + p(d.getMinutes()) + p(d.getSeconds()) +
      (off === 0 ? "Z" : sign + p(off / 60) + "'" + p(off % 60) + "'");
  }

  function localIso(d) {
    const p = (n) => String(Math.abs(n)).padStart(2, "0");
    const off = -d.getTimezoneOffset();
    const tz = off === 0 ? "Z"
      : (off > 0 ? "+" : "-") + p(off / 60) + ":" + p(off % 60);
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
      " " + p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds()) + " " + tz;
  }

  /** Kuerzt eine URL mittig, damit Anfang und Ende lesbar bleiben. */
  function kuerzen(s, max) {
    s = String(s || "");
    if (s.length <= max) return s;
    const kopf = Math.ceil((max - 3) * 0.6);
    return s.slice(0, kopf) + "..." + s.slice(-(max - 3 - kopf));
  }

  function buildPdf(pages, opts) {
    opts = opts || {};
    const dpi = opts.dpi || 144;            // 144 dpi = 2x Standard, gut fuer OCR
    const pxToPt = 72 / dpi;                 // 1 pt = 1/72 inch
    const beleg = opts.provenance || null;   // { url, capturedAt:Date, sha256 }
    const woerter = opts.textLayer || null;  // [{t,x,y,w,h,s}] in CSS-Pixeln
    const quelle = opts.source || null;      // Zitationsdaten aus der Seite

    const objects = [];                      // index 0 = unused
    objects.push(null);

    const addObject = (bodyBytes) => {
      objects.push(bodyBytes);
      return objects.length - 1;
    };

    const catalogId = addObject(null);
    const pagesId = addObject(null);

    // Die Nachweiszeile bekommt eigenen Platz unter dem Bild, statt darueber zu
    // liegen: Sie darf nichts verdecken, sonst waere sie eine Veraenderung der
    // Aufnahme statt einer Angabe darueber. Die Metadaten schreibt der Writer
    // immer, die sichtbare Zeile nur auf Wunsch — sie aendert das Bild, die
    // Metadaten nicht.
    const zeigeFuss = !!(beleg && beleg.footer);
    // Liegt eine Quellenangabe vor, bekommt sie eine eigene Zeile darueber:
    // sie ist das, was in ein Literaturverzeichnis wandert, und darf nicht
    // mit der Pruefsumme in einer Zeile zusammengedraengt werden.
    const zitZeile = zeigeFuss && quelle && quelle.titel ? zitation(quelle) : "";
    const fussPt = zeigeFuss ? (zitZeile ? 42 : 30) : 0;
    const brauchtFont = zeigeFuss || !!(woerter && woerter.length);
    let fontId = 0;
    if (brauchtFont) {
      fontId = addObject(strToBytes(
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>"
      ));
    }

    const pageRefs = [];
    for (const pg of pages) {
      const wPt = (pg.widthPx * pxToPt).toFixed(2);
      const hPt = (pg.heightPx * pxToPt + fussPt).toFixed(2);

      // Normalisiere: legacy einzelnes Bild -> Tile-Liste mit einem Eintrag.
      const tiles = pg.tiles && pg.tiles.length
        ? pg.tiles
        : [{ jpegBytes: pg.jpegBytes, xPx: 0, yPx: 0, wPx: pg.widthPx, hPx: pg.heightPx }];

      const xobjs = [];
      for (let i = 0; i < tiles.length; i++) {
        const t = tiles[i];
        const imgHeader =
          "<< /Type /XObject /Subtype /Image " +
          "/Width " + t.wPx + " /Height " + t.hPx + " " +
          "/ColorSpace /DeviceRGB /BitsPerComponent 8 " +
          "/Filter /DCTDecode " +
          "/Length " + t.jpegBytes.length + " >>\nstream\n";
        const imgFooter = "\nendstream";
        const imgBytes = concatBytes([
          strToBytes(imgHeader),
          t.jpegBytes,
          strToBytes(imgFooter)
        ]);
        const imgId = addObject(imgBytes);
        xobjs.push({ name: "Im" + i, id: imgId, t });
      }

      // PDF y-Achse zeigt nach OBEN ab unten-links; Pixel-Koordinaten beziehen
      // sich auf die Canvas-Top-Left-Ecke. Umrechnung:
      //   pdfX = xPx * pxToPt
      //   pdfY = (heightPx - yPx - hPx) * pxToPt
      let contentStr = "";
      for (const x of xobjs) {
        const wptT = (x.t.wPx * pxToPt).toFixed(2);
        const hptT = (x.t.hPx * pxToPt).toFixed(2);
        const xptT = (x.t.xPx * pxToPt).toFixed(2);
        const yptT = ((pg.heightPx - x.t.yPx - x.t.hPx) * pxToPt + fussPt).toFixed(2);
        contentStr += "q\n" + wptT + " 0 0 " + hptT + " " + xptT + " " + yptT + " cm\n/" + x.name + " Do\nQ\n";
      }

      // Textebene. Die Wortkoordinaten beziehen sich auf das ganze Dokument;
      // im mehrseitigen Modus sagt pg.yPx, wo dieser Ausschnitt beginnt, und
      // jedes Wort landet auf der Seite, auf der es abgebildet ist. Fehlt die
      // Angabe, gaebe es keine verlaessliche Zuordnung — dann lieber keine
      // Textebene als eine falsche.
      const zuordenbar = pages.length === 1 || typeof pg.yPx === "number";
      if (woerter && woerter.length && zuordenbar) {
        const skala = pg.widthPx / (opts.textLayerPageWidth || pg.widthPx);
        // In q/Q geklammert: Textrendermodus und Laufweite gehoeren zum
        // Grafikzustand, nicht zum Textobjekt — sie ueberleben ET. Ohne die
        // Klammer erbt die Fusszeile das "3 Tr" des letzten Wortes und wird
        // unsichtbar. Der Fehler zeigt sich nur, wenn Textebene und Fuss
        // zusammen aktiv sind.
        contentStr += "q\n" +
          textebene(woerter, skala, pg.heightPx, fussPt, pxToPt, pg.yPx || 0) + "Q\n";
      }

      if (zeigeFuss) {
        const breite = pg.widthPx * pxToPt;
        // Wieviele Zeichen bei 7 pt Helvetica in die Breite passen — grob 0.5 em
        // je Zeichen, mit Rand. Lieber zu kurz kuerzen als ueber den Rand laufen.
        const platz = Math.max(40, Math.floor((breite - 20) / 3.4));
        const zeile1 =
          kuerzen(beleg.url, Math.max(24, platz - 62)) +
          "  |  captured " + localIso(beleg.capturedAt) +
          (beleg.sha256 ? "  |  SHA-256 " + beleg.sha256.slice(0, 16) + "..." : "");
        contentStr +=
          "q\n0.85 0.85 0.85 rg\n0 0 " + breite.toFixed(2) + " " + fussPt + " re\nf\nQ\n";
        if (zitZeile) {
          // Die Standardschrift eines PDF kann nur WinAnsi. Bei kyrillischen,
          // griechischen oder ostasiatischen Quellen bleibt von der Zitation
          // nur Interpunktion uebrig — gemessen an einer russischen Arbeit:
          // ", . . & , . . (2007)." Eine solche Zeile ist schlechter als
          // keine, weil sie wie eine Angabe aussieht. Dann wird gesagt, wo
          // die vollstaendige steht, statt sie zu verstuemmeln.
          const sichtbar = nachWinAnsi(zitZeile);
          const buchstaben = (zitZeile.match(/[^\s\p{P}\d]/gu) || []).length;
          const erhalten = (sichtbar.match(/[^\s\p{P}\d]/gu) || []).length;
          const text = (buchstaben > 0 && erhalten / buchstaben < 0.6)
            ? "Citation omitted: it uses characters a standard PDF font cannot show. " +
              "The full record is attached to this file as quelle.ris."
            : kuerzen(sichtbar, platz + 6);
          contentStr +=
            "BT /F1 7.5 Tf 0 0 0 rg 10 " + (fussPt - 12) + " Td (" +
            pdfString(text) + ") Tj ET\n";
        }
        contentStr +=
          "BT /F1 7 Tf 0.15 0.15 0.15 rg 10 18 Td (" + pdfString(zeile1) + ") Tj ET\n" +
          "BT /F1 5.5 Tf 0.35 0.35 0.35 rg 10 7 Td (" + pdfString(kuerzen(HINWEIS, platz + 40)) + ") Tj ET\n";
      }

      const contentBytes = strToBytes(
        "<< /Length " + contentStr.length + " >>\nstream\n" + contentStr + "endstream"
      );
      const contentId = addObject(contentBytes);

      const xobjEntries = xobjs.map(x => "/" + x.name + " " + x.id + " 0 R").join(" ");
      const pageDict =
        "<< /Type /Page /Parent " + pagesId + " 0 R " +
        "/MediaBox [0 0 " + wPt + " " + hPt + "] " +
        "/Resources << /XObject << " + xobjEntries + " >>" +
        (brauchtFont ? " /Font << /F1 " + fontId + " 0 R >>" : "") + " >> " +
        "/Contents " + contentId + " 0 R >>";
      const pageId = addObject(strToBytes(pageDict));
      pageRefs.push(pageId);
    }

    objects[pagesId] = strToBytes(
      "<< /Type /Pages /Count " + pageRefs.length +
      " /Kids [" + pageRefs.map(id => id + " 0 R").join(" ") + "] >>"
    );
    // Der RIS-Satz wird als Anhang in die Datei gelegt. Damit traegt das PDF
    // seine Herkunft selbst — wer es in einem Jahr wiederfindet, braucht
    // weder die Aufnahme-Sitzung noch die Ursprungsseite, um es korrekt zu
    // zitieren. Herausholen laesst er sich mit "pdfdetach -saveall" oder
    // ueber die Anlagen-Ansicht des Betrachters.
    let namesEintrag = "";
    if (quelle && quelle.titel) {
      const ris = strToBytes(risSatz(quelle));
      const risId = addObject(concatBytes([
        strToBytes("<< /Type /EmbeddedFile /Subtype /text#2Fplain /Length " +
                   ris.length + " >>\nstream\n"),
        ris,
        strToBytes("\nendstream"),
      ]));
      const specId = addObject(strToBytes(
        "<< /Type /Filespec /F (quelle.ris) /UF " + pdfTextString("quelle.ris") +
        " /Desc " + pdfTextString("Zitationsdatensatz (RIS) fuer Citavi, Zotero, EndNote") +
        " /EF << /F " + risId + " 0 R >> >>"
      ));
      const namesId = addObject(strToBytes(
        "<< /Names [(quelle.ris) " + specId + " 0 R] >>"
      ));
      namesEintrag = " /Names << /EmbeddedFiles " + namesId + " 0 R >>";
    }

    objects[catalogId] = strToBytes(
      "<< /Type /Catalog /Pages " + pagesId + " 0 R" + namesEintrag + " >>"
    );

    // Dokumentinformationen: dieselben Angaben wie in der Fussnote, aber
    // maschinenlesbar. Wer die Datei archiviert, findet Adresse und Zeitpunkt
    // damit auch dann noch, wenn die letzte Seite abgeschnitten wurde.
    let infoId = 0;
    if (beleg || opts.title) {
      const felder = ["/Producer " + pdfTextString("Full Page PDF Snap" + (opts.version ? " " + opts.version : ""))];
      // Der Titel aus den Verlagsangaben ist genauer als der Fenstertitel:
      // dieser traegt oft den Namen der Website und Zusaetze mit.
      const titel = (quelle && quelle.titel) || opts.title;
      if (titel) felder.push("/Title " + pdfTextString(titel));
      if (quelle && quelle.autoren && quelle.autoren.length) {
        felder.push("/Author " + pdfTextString(quelle.autoren.join("; ")));
      }
      if (beleg) {
        felder.push("/Subject " + pdfTextString(
          quelle && quelle.titel ? zitation(quelle) : "Screen capture of " + beleg.url));
        felder.push("/CreationDate (" + pdfDate(beleg.capturedAt) + ")");
        felder.push("/ModDate (" + pdfDate(beleg.capturedAt) + ")");
        if (beleg.sha256) {
          felder.push("/Keywords " + pdfTextString(
            "source-url=" + beleg.url +
            "; captured=" + localIso(beleg.capturedAt) +
            "; image-sha256=" + beleg.sha256 +
            "; note=self-made screen capture, not a qualified electronic document (eIDAS)" +
            (woerter && woerter.length
              ? "; text-layer=extracted from the page's own DOM, not OCR"
              : "") +
            (quelle && quelle.doi ? "; doi=" + quelle.doi : "") +
            (quelle && quelle.titel ? "; citation-source=" + quelle.herkunft : "")
          ));
        }
      }
      infoId = addObject(strToBytes("<< " + felder.join(" ") + " >>"));
    }

    const chunks = [];
    chunks.push(strToBytes("%PDF-1.4\n%\xFF\xFF\xFF\xFF\n"));
    const offsets = [0];
    let runningOffset = chunks[0].length;

    for (let i = 1; i < objects.length; i++) {
      offsets.push(runningOffset);
      const head = strToBytes(i + " 0 obj\n");
      const tail = strToBytes("\nendobj\n");
      chunks.push(head, objects[i], tail);
      runningOffset += head.length + objects[i].length + tail.length;
    }

    const xrefOffset = runningOffset;
    let xref = "xref\n0 " + objects.length + "\n";
    xref += "0000000000 65535 f \n";
    for (let i = 1; i < objects.length; i++) {
      xref += String(offsets[i]).padStart(10, "0") + " 00000 n \n";
    }
    chunks.push(strToBytes(xref));

    const trailer =
      "trailer\n<< /Size " + objects.length +
      " /Root " + catalogId + " 0 R" +
      (infoId ? " /Info " + infoId + " 0 R" : "") + " >>\n" +
      "startxref\n" + xrefOffset + "\n%%EOF\n";
    chunks.push(strToBytes(trailer));

    return concatBytes(chunks);
  }

  root.PageShotPdf = { buildPdf };
})(typeof window !== "undefined" ? window : globalThis);
