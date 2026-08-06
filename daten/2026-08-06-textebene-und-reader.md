# Textebene und Reader-Prüfung — 6. August 2026

## Runde 2: die unsichtbare Textebene, gebaut

Ein vollständiges PDF erzeugt: Bild, unsichtbarer Text (`3 Tr`), 143 klickbare
Verweise, Linkkarte als Anhang, XMP. Aus einer echten Seitenaufnahme.

| Bestandteil | Größe |
|---|---|
| Bild (JPEG 0.85) | 618 kB |
| **Textebene, Flate** | **5 kB** |
| Linkkarte, Flate | 3 kB |
| XMP | 0,4 kB |
| **gesamt** | **654 kB** — Struktur unter 1,4 % |

Die Textebene fiel deutlich kleiner aus als in der Vorabmessung (39 kB), weil
hier nur der sichtbare Ausschnitt bis 2400 px erfasst wurde statt der ganzen
Seite. Für eine vollständige Aufnahme gilt die höhere Zahl.

**Urteil fremder Werkzeuge:** `pdftotext` gibt **7.373 Zeichen** zurück, findet
„Portable Document Format" zweimal, und `pdftotext -bbox` liefert **1.117
Wörter mit Rechtecken** bei plausibler mittlerer Wortbreite (37 pt auf 1.617 pt
Seitenbreite).

Das ist der Unterschied zwischen einer Bildschirmaufnahme und einem Dokument:
Ein Agent kann darin suchen, zitieren und Stellen adressieren — **ohne OCR und
damit ohne Erkennungsfehler**, weil der Text aus dem Dokument selbst stammt.

**Grenze:** Die Zeichenbreite wird über `Tz` an die gemessene Kastenbreite
angeglichen, mit einer Näherung für Helvetica. Für Suche und Extraktion reicht
das; ob eine Textauswahl mit der Maus exakt auf den Buchstaben sitzt, ist nicht
geprüft. Proportionalschriften und Ligaturen wurden nicht einzeln behandelt.

## Runde 3: Reader

| Werkzeug | Prüfung | Ergebnis |
|---|---|---|
| `pdftotext` | Textebene | 7.373 Zeichen |
| `pdfdetach -list` | Anhang | `linkkarte.json` gelistet |
| `pdfinfo -meta` | XMP | `dc:source` gelesen |
| `pypdf` | Verweise, Anhang, XMP | alle drei |
| Chrome (PDFium) | lädt ohne Fehler | bestanden |

**Ungeprüft geblieben:** Firefox `pdf.js` und Acrobat — beide brauchen eine
Anzeige, die hier nicht zur Verfügung stand. Für Android ebenfalls ungeprüft.
Das sind die drei, die vor einem Einbau noch fehlen; PDFium deckt Chrome und
Edge ab, poppler die meisten Linux-Anzeigen.
