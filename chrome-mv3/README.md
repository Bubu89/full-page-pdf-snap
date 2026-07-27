# Chrome MV3 — abgezweigte Portierung

Chrome nimmt seit 2025 nur noch **Manifest V3** an. Firefox unterstützt **MV2** dauerhaft weiter. Deshalb liegt der Chrome-Stand hier getrennt: Die Firefox-Version im Repo-Wurzelverzeichnis bleibt unverändert MV2.

## Was anders ist als bei Firefox

Ein MV3-**Service-Worker hat kein DOM** — kein `document`, kein `new Image()`, kein `URL.createObjectURL`. Genau darauf stützte sich das PDF-Stitching. Statt den gesamten Code umzuschreiben, kapselt [`compat.js`](compat.js) die Unterschiede:

| Firefox MV2 | Chrome MV3 |
|---|---|
| `document.createElement("canvas")` | `new OffscreenCanvas()` |
| `new Image()` + `URL.createObjectURL` | `createImageBitmap(blob)` |
| `canvas.toBlob()` | `canvas.convertToBlob()` |
| Blob-URL für den Download | `data:`-URL (base64, in 32-KB-Blöcken kodiert) |
| `browser.*` | `chrome.*` |
| `browser.menus` | `chrome.contextMenus` |
| `browserAction` | `action` |
| `tabs.executeScript` | `scripting.executeScript` |

Zwei weitere Unterschiede, die keinen Code brauchen: Chrome akzeptiert **kein SVG** als Icon, daher werden die PNGs verwendet — und **Chrome für Android kennt keine Erweiterungen**, der Android-Zweig läuft hier also nie an.

## Erneut portieren

Der Port ist ein Skript, kein Hand-Fork. Nach jeder Änderung an der Firefox-Version:

```bash
cd chrome-mv3
python3 port.py --check    # prüft, ohne zu schreiben
python3 port.py            # portiert
```

Jede Ersetzung meldet ihre Trefferzahl. Weicht eine ab, bricht das Skript ab, statt einen halb portierten Stand zu schreiben — dann hat sich die Firefox-Quelle geändert und die Patch-Liste in `port.py` muss nachgezogen werden.

## Lokal testen

1. `chrome://extensions` öffnen
2. **Entwicklermodus** einschalten
3. **Entpackte Erweiterung laden** → diesen Ordner wählen
4. Auf einer langen Seite testen (Wikipedia-Artikel, Nachrichtenportal, X-Feed)
5. Bei Fehlern: auf der Karte der Erweiterung auf **Service Worker** klicken — dort landen die Logs

**Der entscheidende Test** ist eine sehr lange Seite: Das Stitching auf `OffscreenCanvas` muss dasselbe Ergebnis liefern wie unter Firefox, ohne Versatz zwischen den Segmenten. Am besten dieselbe Seite in beiden Browsern aufnehmen und die PDFs nebeneinanderlegen.

## Einreichen

```bash
cd chrome-mv3
python3 pack.py
```

Erzeugt `full-page-pdf-snap-chrome-<version>.zip` (~39 KB, 13 Dateien) eine Ebene höher. Werkzeuge, diese README und `store-assets/` bleiben draußen — jede überflüssige Datei im Paket erzeugt beim Review nur Rückfragen.

Store-Assets liegen in [`store-assets/`](store-assets/): Screenshots in 1280×800 (EN und DE) und die Promo-Kachel in 440×280. Die Listing-Texte inklusive aller Berechtigungs-Begründungen stehen in `Chrome_Store_Listing.docx`.

## Nicht vergessen

- **Datenschutz-URL** ist Pflicht: https://bubu89.github.io/full-page-pdf-snap/privacy.html
- Im Privacy-Tab bleibt **jede** Datenkategorie unangehakt — die Erweiterung erhebt nichts
- Für **jede** Berechtigung eine eigene Begründung eintragen; fehlende oder pauschale Begründungen sind der häufigste Ablehnungsgrund

## Auslieferung — ein Befehl

```bash
python3 release.py            # Tests, Version hochstufen, beide Pakete
python3 release.py --patch    # Patch- statt Minor-Sprung
python3 release.py --check    # nur prüfen, nichts schreiben
python3 release.py --keep     # Version lassen, nur neu bauen
```

Läuft der Reihe nach: Tests → Syntaxprüfung → Version gegen den Store → Chrome
portieren und packen → Firefox packen → Gegenprobe an den fertigen Paketen
(Version, Dateizahl, Sprachdateien). Bricht beim ersten Fehlschlag ab, statt ein
halb gebautes Paket zu hinterlassen.

Die Versionsnummer kommt aus `bump-version.py`, das die veröffentlichten
Versionen bei AMO abfragt. Lokales Hochzählen reicht nicht: Zwischen Bauen und
Hochladen liegt Zeit, und eine bereits veröffentlichte Nummer lehnt der Store
erst beim Upload ab.
