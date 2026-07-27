# Full Page PDF Snap

Save any webpage as a single high-resolution PDF. Auto-scrolls and captures the whole page — no cropping, no print dialog, no upload.

[![Get it on Firefox Add-ons](https://img.shields.io/badge/Firefox-Add--ons-orange)](https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**[→ Install from addons.mozilla.org](https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/)**

![Capture the entire page](screenshots/01_capture_en.png)

---

## What it does

Full Page PDF Snap scrolls the page from top to bottom, captures every viewport, and stitches all segments into one seamless PDF — entirely on your device.

- **Full-page capture** — the complete scrollable page, not just the visible part
- **Auto-scroll** — handles lazy-loading pages (LinkedIn, X/Twitter, news portals)
- **Single-page PDF** by default, with no visible seams between segments — ideal for OCR and AI tools
- **Multi-page output** optionally, for printing
- **Resolution scaling** from 1.0x to 2.0x
- **Filename templates** with site, date, time, counter and page title
- **Hide sticky elements** — cookie banners, chat widgets and top bars before capture
- **Firefox for Android** — tap the extension icon and the capture starts immediately

## Privacy

The extension has **no technical capability to collect data**. All processing — scrolling, screenshots, PDF generation, saving — happens locally in the Firefox process.

- No server of the author is ever contacted
- No analytics library, no telemetry, no error reporting
- The author never learns which pages you capture

The full source is in this repository under the MIT license, so you can verify all of the above.

## How to use it

**Desktop**

- Click the toolbar icon → **Capture now**
- Press `Alt+Shift+P`
- Right-click the toolbar icon → **Save entire page as PDF** (also offers quick switches for scaling, folder and sticky handling)

**Android**

Open the menu, tap the extension — the capture starts immediately without an intermediate popup. The finished PDF opens in your device's default PDF app.

![Settings](screenshots/02_settings_en.png)

## Default settings

| Setting | Desktop | Android |
|---|---|---|
| JPEG quality | 0.92 | 0.92 |
| Scroll delay | 400 ms | 400 ms |
| PDF format | Single page | Single page |
| Tile height | 4000 px | 2000 px |
| Hide sticky elements | On | On |
| After capture | Show folder | Open PDF |
| Capture scaling | 1.5x | 1.0x |

![Output options](screenshots/03_output_en.png)

## Support

Found a bug or missing a feature? **[Open an issue](../../issues)** — please include your Firefox version, operating system, and the page where it happened.

## Building from source

```bash
web-ext lint
web-ext build --overwrite-dest
```

Requires [web-ext](https://extensionworkshop.com/documentation/develop/getting-started-with-web-ext/). Signed builds are distributed through addons.mozilla.org.

## License

MIT — see [LICENSE](LICENSE).

---

# Deutsch

Speichert eine komplette Webseite als hochauflösendes PDF. Auto-Scroll erfasst die ganze Seite — kein Zuschneiden, kein Druckdialog, kein Upload.

## Funktionen

- **Vollseiten-Erfassung** — die komplette scrollbare Seite, nicht nur der sichtbare Teil
- **Auto-Scroll** — erfasst auch Lazy-Load-Seiten (LinkedIn, X/Twitter, Nachrichtenportale)
- **Single-Page-PDF** als Standard, ohne sichtbare Schnittkanten zwischen den Streifen
- **Mehrseitige Ausgabe** optional, zum Drucken
- **Auflösung skalierbar** von 1.0x bis 2.0x
- **Dateinamen-Vorlage** mit Seite, Datum, Uhrzeit, Zähler und Seitentitel
- **Sticky-Elemente ausblenden** — Cookie-Banner, Chat-Widgets und Top-Leisten vor der Aufnahme
- **Firefox für Android** — Antippen des Symbols startet die Aufnahme sofort

## Datenschutz

Die Erweiterung enthält **technisch keine Funktion zur Datenerhebung**. Die gesamte Verarbeitung findet lokal im Firefox-Prozess statt: kein Server des Autors wird kontaktiert, keine Analytics, keine Telemetrie. Der Autor erfährt zu keinem Zeitpunkt, welche Seiten erfasst werden. Der Quellcode liegt vollständig in diesem Repository (MIT-Lizenz) und ist überprüfbar.

## Auslösen

- **Desktop:** Toolbar-Icon → **Jetzt aufnehmen**, Tastenkürzel `Alt+Shift+P`, oder Rechtsklick auf das Toolbar-Icon
- **Android:** Menü → Erweiterung antippen, die Aufnahme startet sofort

## Support

Fehler gefunden oder Funktion vermisst? **[Issue eröffnen](../../issues)** — bitte Firefox-Version, Betriebssystem und die betroffene Seite angeben.
