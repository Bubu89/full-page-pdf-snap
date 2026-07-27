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

  function buildPdf(pages, opts) {
    opts = opts || {};
    const dpi = opts.dpi || 144;            // 144 dpi = 2x Standard, gut fuer OCR
    const pxToPt = 72 / dpi;                 // 1 pt = 1/72 inch

    const objects = [];                      // index 0 = unused
    objects.push(null);

    const addObject = (bodyBytes) => {
      objects.push(bodyBytes);
      return objects.length - 1;
    };

    const catalogId = addObject(null);
    const pagesId = addObject(null);

    const pageRefs = [];
    for (const pg of pages) {
      const wPt = (pg.widthPx * pxToPt).toFixed(2);
      const hPt = (pg.heightPx * pxToPt).toFixed(2);

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
        const yptT = ((pg.heightPx - x.t.yPx - x.t.hPx) * pxToPt).toFixed(2);
        contentStr += "q\n" + wptT + " 0 0 " + hptT + " " + xptT + " " + yptT + " cm\n/" + x.name + " Do\nQ\n";
      }
      const contentBytes = strToBytes(
        "<< /Length " + contentStr.length + " >>\nstream\n" + contentStr + "endstream"
      );
      const contentId = addObject(contentBytes);

      const xobjEntries = xobjs.map(x => "/" + x.name + " " + x.id + " 0 R").join(" ");
      const pageDict =
        "<< /Type /Page /Parent " + pagesId + " 0 R " +
        "/MediaBox [0 0 " + wPt + " " + hPt + "] " +
        "/Resources << /XObject << " + xobjEntries + " >> >> " +
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
