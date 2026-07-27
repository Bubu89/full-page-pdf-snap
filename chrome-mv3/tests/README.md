# Tests

Drei Seiten, die ohne geladene Erweiterung in Chrome laufen. Sie decken genau die Stellen ab, an denen der MV2→MV3-Port zur Laufzeit gescheitert ist — statische Prüfung hatte jeden dieser Fehler durchgelassen.

| Datei | Prüft |
|---|---|
| `selftest.html` | `createImageBitmap` → `OffscreenCanvas` → `convertToBlob` → `data:`-URL |
| `layouttest.html` | Container-Erkennung und Zuschnitt über sechs Layout-Typen |
| `stitchtest.html` | Zusammenfügen mit Zuschnitt, pixelweise geprüft |

## Vorbereitung für `layouttest.html`

Die Seite prüft den **unveränderten** Code aus `content.js`. Er wird dafür herausgelöst — so kann der Test nicht an einer veralteten Kopie vorbeilaufen:

```bash
cd chrome-mv3/tests
python3 - <<'PY'
import re
from pathlib import Path
src = Path("../../content.js").read_text(encoding="utf-8")
fns = ["findScrollableRoot", "computeClipRect", "getTotalHeight",
       "getViewportHeight", "getViewportWidth", "getScrollTop"]
out = [re.search(r"\n  function " + n + r"\(.*?\n  \}\n", src, re.S)
         .group(0).replace("\n  ", "\n").strip() for n in fns]
Path("_logic.js").write_text("function log(){}\nlet scrollState = null;\n\n"
                             + "\n\n".join(out), encoding="utf-8")
PY
```

## Ausführen

Am einfachsten direkt im Browser öffnen — das Ergebnis steht auf der Seite.

Automatisiert über CDP:

```bash
chrome.exe --headless=new --disable-gpu --remote-debugging-port=9223 \
  --user-data-dir=<temporaeres Profil> --window-size=1400,900 <datei>
# dann verbinden und auf document.title === "fertig" warten
```

`--dump-dom` funktioniert **nicht**: Es greift, bevor der asynchrone Testcode fertig ist, und liefert nur den leeren Ausgangszustand.

## Bekannte Grenzen, die die Tests sichtbar machen

Fall C und D in `layouttest.html` dokumentieren bewusste Abwägungen, keine Fehler:

- **Verschachtelte Container:** Es gewinnt der mit dem größten Scroll-Überhang. Inhalt des äußeren Containers landet dann nicht im PDF.
- **Zwei Container nebeneinander:** Der längere gewinnt, der andere wird abgeschnitten.

Beides ist für Mail- und Dokument-Apps richtig, weil dort der Hauptinhalt der längste Container ist. Bei geteilten Ansichten (Vorschau neben Liste) ist es eine Einschränkung.

## `end-detection.test.js`

Reiner Logik-Test, läuft ohne Browser:

```bash
node chrome-mv3/tests/end-detection.test.js
```

Stellt beide Scroll-Schleifen nach — Haupt- und Nebenbereich — gegen einen
Container, der `scrollTop` auf `[0, max]` klemmt, genau wie der Browser. Geprüft
wird für jeden von neun Fällen dreierlei:

- **Ende erreicht** — die letzte Aufnahme sitzt exakt auf `max`
- **keine Wiederholung** — keine Position wird zweimal aufgenommen
- **keine Lücke** — die Fenster decken den Bereich zusammenhängend ab

Abgedeckt: glatte und ungerade Resthöhen, Seiten knapp über Fensterhöhe, exakt
eine Fensterhöhe, 50.000 px lange Seiten, sowie Nebenbereiche von 0 px Überhang
bis zum schmalen 5.000-px-Menü.
