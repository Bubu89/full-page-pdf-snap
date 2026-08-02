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
    // Aufnahme statt einer Angabe darueber.
    const fussPt = beleg ? 30 : 0;
    let fontId = 0;
    if (beleg) {
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

      if (beleg) {
        const breite = pg.widthPx * pxToPt;
        // Wieviele Zeichen bei 7 pt Helvetica in die Breite passen — grob 0.5 em
        // je Zeichen, mit Rand. Lieber zu kurz kuerzen als ueber den Rand laufen.
        const platz = Math.max(40, Math.floor((breite - 20) / 3.4));
        const zeile1 =
          kuerzen(beleg.url, Math.max(24, platz - 62)) +
          "  |  captured " + localIso(beleg.capturedAt) +
          (beleg.sha256 ? "  |  SHA-256 " + beleg.sha256.slice(0, 16) + "..." : "");
        contentStr +=
          "q\n0.85 0.85 0.85 rg\n0 0 " + breite.toFixed(2) + " " + fussPt + " re\nf\nQ\n" +
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
        (beleg ? " /Font << /F1 " + fontId + " 0 R >>" : "") + " >> " +
        "/Contents " + contentId + " 0 R >>";
      const pageId = addObject(strToBytes(pageDict));
      pageRefs.push(pageId);
    }

    objects[pagesId] = strToBytes(
      "<< /Type /Pages /Count " + pageRefs.length +
      " /Kids [" + pageRefs.map(id => id + " 0 R").join(" ") + "] >>"
    );
    objects[catalogId] = strToBytes(
      "<< /Type /Catalog /Pages " + pagesId + " 0 R >>"
    );

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
      " /Root " + catalogId + " 0 R >>\n" +
      "startxref\n" + xrefOffset + "\n%%EOF\n";
    chunks.push(strToBytes(trailer));

    return concatBytes(chunks);
  }

  root.PageShotPdf = { buildPdf };
})(typeof window !== "undefined" ? window : globalThis);
