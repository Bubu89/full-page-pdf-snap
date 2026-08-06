# Kompression und Metaebenen — gemessen 6. August 2026

Zwei echte Seitenaufnahmen, 1617×2400, headless Chromium.
Rohbilder und Prototyp im Scratchpad der Sitzung, nicht im Repo.

## Kompression: was die Alternativen bringen

| Verfahren | PDF-Filter | Textseite | Bildseite |
|---|---|---|---|
| JPEG 0.92 | DCTDecode | 792 kB | 528 kB | **heute** |
| JPEG 0.85 | DCTDecode | 618 kB | 412 kB | −22 % |
| JPEG 0.75 | DCTDecode | 490 kB | 325 kB | −38 % |
| JPEG 2000 ~12:1 | JPXDecode | 947 kB | 947 kB | **größer** |
| Flate, 1 bit | FlateDecode | 57 kB | 35 kB | **heute (S/W)** |
| CCITT Gruppe 4 | CCITTFaxDecode | 56 kB | 32 kB | −2 % / −7 % |
| LZW, 1 bit | LZWDecode | 70 kB | 41 kB | schlechter |

**Folgerung:** Am Schwarzweiß-Weg ist nichts zu holen — CCITT G4 spart 2 bis 7 %
und kostet einen Kodierer. JPEG 2000 ist größer und wird von Readern schlechter
unterstützt. Der einzige Hebel ist die JPEG-Stufe.

**JBIG2 ungemessen** — `jbig2enc` ist nicht installiert. Es wäre der einzige
Kandidat mit deutlichem Vorsprung bei Schwarzweiß. Anzumerken ist, dass die
verlustbehaftete Betriebsart historisch Ziffern vertauscht hat; für ein Werkzeug,
das Belege erzeugt, käme nur die verlustfreie in Frage.

## Was weniger JPEG-Qualität an Lesbarkeit kostet

| Qualität | Größe | PSNR gesamt | PSNR an Textkanten |
|---|---|---|---|
| 0.92 | 792 kB | 44,9 dB | 48,3 dB |
| 0.85 | 618 kB | 40,6 dB | 44,4 dB |
| 0.80 | 545 kB | 38,5 dB | 42,4 dB |
| 0.75 | 490 kB | 37,0 dB | 40,9 dB |

Zwei Ausschnitte bei 0.92 und 0.75, 2× vergrößert, nebeneinander angesehen:
**kein sichtbarer Unterschied.**

**Grenze der Aussage:** Ein Textbild auf weißem Grund ist der für JPEG günstige
Fall. Fotos mit weichen Verläufen und farbige Flächen wurden nicht einzeln
beurteilt, und ein Blick auf zwei Ausschnitte ist keine systematische Prüfung.

## Metaebenen: als Prototyp gebaut, nicht behauptet

Ein PDF mit vier Ebenen erzeugt und mit **fremden** Werkzeugen gegengelesen
(`pdfinfo` aus poppler, `pypdf`):

| Ebene | PDF-Struktur | Prüfung |
|---|---|---|
| klickbare Verweise | `/Annots` → `/Link` → `/A /URI` | pypdf liest 3 von 3, URI korrekt |
| Linkkarte als Anhang | `/Names /EmbeddedFiles`, `/Filespec` | pypdf liest 1528 Verweise zurück |
| Herkunft maschinenlesbar | `/Metadata` → XMP (RDF/XML) | `dc:source` gelesen |
| Anhänge sichtbar machen | `/PageMode /UseAttachments` | im Katalog gesetzt |

**Kosten:** Die Linkkarte mit 1528 Verweisen ist roh 208 kB, Flate-komprimiert
**13 kB — zwei Prozent des Bildes.** XMP 0,5 kB.

Das ist derselbe Mechanismus, mit dem eine elektronische Rechnung ihre
strukturierten Daten in die Sicht-PDF legt (PDF/A-3). Ein Dokument, zwei Leser:
Der Mensch sieht die Seite, die Maschine liest den Anhang.

**Ungeprüft:** Acrobat, die eingebauten Anzeigen von Firefox und Chrome, sowie
Anzeigeprogramme auf Android. Geprüft wurden nur poppler und pypdf. Ob die
`.links.json` als getrennte Datei erhalten bleibt oder im Anhang aufgeht, ist
eine offene Entscheidung — getrennt ist sie leichter zu greifen, eingebettet
geht sie beim Weitergeben nicht verloren.
