#!/usr/bin/env python3
"""Portiert die Firefox-MV2-Quellen nach Chrome MV3.

Reproduzierbar: laeuft gegen die unveraenderten Firefox-Quellen und schreibt
den Chrome-Zweig neu. Bei einer neuen Firefox-Version einfach erneut ausfuehren
und die Patch-Liste pruefen - jede Ersetzung meldet, ob sie gegriffen hat.

    python3 port.py            # portiert
    python3 port.py --check    # nur pruefen, nichts schreiben
"""
import re
import shutil
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent.parent          # Firefox-Quellen (Repo-Wurzel)
DST = Path(__file__).resolve().parent                 # chrome-mv3/
CHECK = "--check" in sys.argv

# (Beschreibung, Suchmuster, Ersatz, erwartete Trefferzahl)
PATCHES = [
    # Platzhalter - die tatsaechliche importScripts-Zeile wird aus
    # background.html abgeleitet, siehe build_import_line().
    ("Skripte per importScripts laden (MV3 hat keine background.html)",
     '"use strict";\n', "@@IMPORTS@@", 1),

    ("blobToImage -> createImageBitmap (kein DOM im Service Worker)",
     re.compile(r"async function blobToImage\(blob\) \{.*?\n\}\n", re.S),
     "", 1),

    ("canvasToJpegBytes -> OffscreenCanvas.convertToBlob",
     re.compile(r"function canvasToJpegBytes\(canvas, quality\) \{.*?\n\}\n", re.S),
     "", 1),

    ("document.createElement(canvas) -> OffscreenCanvas",
     'document.createElement("canvas")',
     "createCanvas()", 3),

    # createImageBitmap liefert ein ImageBitmap. Das kennt nur width/height -
    # naturalWidth/naturalHeight gibt es ausschliesslich bei HTMLImageElement.
    # Ohne diesen Patch ist pxW undefined und OffscreenCanvas wirft
    # "Value is not of type 'unsigned long'".
    ("img.naturalWidth -> img.width (ImageBitmap kennt kein naturalWidth)",
     ".naturalWidth", ".width", 2),
    ("img.naturalHeight -> img.height",
     ".naturalHeight", ".height", 2),

    ("PDF-Blob -> data:-URL statt Blob-URL",
     "const url = URL.createObjectURL(pdfBlob);",
     "const url = await blobToDataUrl(pdfBlob);", 1),

    ("revokeObjectURL entfaellt bei data:-URLs",
     re.compile(r"setTimeout\(\(\) => URL\.revokeObjectURL\(url\), 60_000\);"),
     "revokeDownloadUrl(url);", 1),

    # scripting.executeScript braucht keinen Patch mehr: seit dem MV3-Port
    # ruft die Firefox-Quelle dieselbe API mit derselben Signatur auf.

    # --- Meldungstexte: nennen Firefox, laufen aber in Chrome ---------------
    ("Meldung 'Interne Firefox-Seite' -> browserneutral",
     '"Interne Firefox-Seite — bitte zu einer normalen Webseite wechseln (https://...)."',
     '"Interne Browser-Seite (chrome://, Web Store, Einstellungen) — '
     'bitte zu einer normalen Webseite wechseln (https://...)."', 1),

    ("Meldung 'Firefox schuetzt diese Seite' -> browserneutral",
     '"Firefox schuetzt diese Seite. Bitte zu einer normalen Webseite wechseln (z.B. wikipedia.org)."',
     '"Chrome schuetzt diese Seite. Bitte zu einer normalen Webseite wechseln (z.B. wikipedia.org)."', 1),

    ("Injektions-Fehlertext -> Chrome-Beispiele",
     '"Diese Seite erlaubt keine Erweiterungs-Skripte (about:/addons.mozilla.org/PDF-Viewer etc.)"',
     '"Diese Seite erlaubt keine Erweiterungs-Skripte (chrome://, Chrome Web Store, PDF-Viewer)"', 1),

    ("Gesperrte Hosts: Mozilla -> Chrome Web Store",
     '''const BLOCKED_HOSTS = [
  "addons.mozilla.org",
  "accounts.firefox.com",
  "support.mozilla.org",
  "install.mozilla.org"
];''',
     '''const BLOCKED_HOSTS = [
  "chromewebstore.google.com",
  "chrome.google.com"
];''', 1),

    ("Kommentar zur Host-Sperre -> Chrome",
     "// Firefox blockiert Content-Script-Injektion auf diesen Seiten aus Sicherheitsgruenden.",
     "// Chrome blockiert Content-Script-Injektion auf diesen Seiten aus Sicherheitsgruenden.", 1),
]

# Dateien, die unveraendert uebernommen werden
COPY_AS_IS = ["content.js", "pdf-writer.js", "popup.html", "popup.js",
              "options.html", "options.js", "i18n.js", "i18n-data.js"]

MANIFEST = """{
  "manifest_version": 3,
  "name": "__MSG_extName__",
  "default_locale": "en",
  "short_name": "PDFSnap",
  "version": "2.15.0",
  "description": "__MSG_extDescription__",
  "author": "Bubu89",
  "minimum_chrome_version": "116",
  "icons": {
    "16": "icons/icon-16.png",
    "48": "icons/icon-48.png",
    "128": "icons/icon-128.png"
  },
  "permissions": [
    "activeTab",
    "downloads",
    "downloads.open",
    "storage",
    "contextMenus",
    "notifications",
    "scripting"
  ],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_icon": {
      "16": "icons/icon-16.png",
      "48": "icons/icon-48.png"
    },
    "default_title": "Full Page PDF Snap \\u2014 save the whole page as PDF",
    "default_popup": "popup.html"
  },
  "options_ui": {
    "page": "options.html",
    "open_in_tab": true
  },
  "commands": {
    "capture-full-page": {
      "suggested_key": { "default": "Alt+Shift+Y" },
      "description": "Save the whole page as PDF"
    },
    "capture-full-page-alt": {
      "suggested_key": { "default": "Ctrl+Shift+Y" },
      "description": "Save the whole page as PDF (second shortcut)"
    }
  }
}
"""


def build_import_line():
    """Leitet die importScripts-Zeile aus background.html ab.

    MV2 laedt Bibliotheken ueber <script>-Tags in der Hintergrundseite. MV3 hat
    keine solche Seite - fehlt hier eine Datei, ist sie zur Laufzeit schlicht
    nicht definiert (genau so fehlte pdf-writer.js und PageShotPdf war undefined).
    Deshalb wird die Liste ausgelesen statt gepflegt.
    """
    html = (SRC / "background.html").read_text(encoding="utf-8")
    srcs = [s for s in re.findall(r'<script src="([^"]+)"', html) if s != "background.js"]
    files = ["compat.js"] + srcs          # compat.js zuerst: setzt den Namensraum
    joined = ", ".join(f'"{f}"' for f in files)
    return ('"use strict";\n\n'
            "// Chrome MV3 kennt keine background.html - alle dort geladenen\n"
            "// Skripte muessen hier importiert werden, sonst fehlen sie zur Laufzeit.\n"
            f"importScripts({joined});\n"), files


def patch_background():
    text = (SRC / "background.js").read_text(encoding="utf-8")
    import_line, imported = build_import_line()
    report = [f"  [INFO] importScripts: {', '.join(imported)}"]
    for desc, pattern, repl, expected in PATCHES:
        if repl == "@@IMPORTS@@":
            repl = import_line
        if isinstance(pattern, re.Pattern):
            text, n = pattern.subn(repl, text)
        else:
            n = text.count(pattern)
            text = text.replace(pattern, repl)
        ok = "OK  " if n == expected else "FEHL"
        report.append(f"  [{ok}] {desc}  ({n}/{expected})")
    return text, report


def add_compat_script(html_text):
    """compat.js als ERSTES Skript laden.

    i18n.js greift beim Start auf `browser` zu - in Chrome existiert der
    Namensraum erst, nachdem compat.js gelaufen ist. Vor dem eigenen Skript
    einzufuegen reichte nicht: i18n.js stand davor und haette bei bereits
    geladenem Dokument sofort ins Leere gegriffen.
    """
    return re.sub(r'(<script src="i18n-data\.js")',
                  r'<script src="compat.js"></script>\n  \1',
                  html_text, count=1)


# Hinweistexte, die auf Firefox oder Android verweisen - in Chrome sachlich
# falsch. Chrome fuer Android kennt keine Erweiterungen.
HTML_TEXT_PATCHES = [
    ('"Ordner zeigen" nutzt Firefox-Downloads-API (Desktop). Auf Android wird '
     'das PDF direkt in der Standard-App geoeffnet — die Ordner-Anzeige ist dort '
     'nicht verfuegbar.',
     'Standard ist "Ordner zeigen": nach dem Speichern oeffnet sich der '
     'Download-Ordner mit vorausgewaehlter Datei. "PDF automatisch oeffnen" '
     'startet stattdessen den PDF-Betrachter, "Beides" macht nacheinander beides.'),
    ('Setzt Browser-Zoom vor dem Capture per <code>tabs.setZoom</code>. '
     'Auf Android ohne Wirkung (API fehlt).',
     'Setzt Browser-Zoom vor dem Capture per <code>tabs.setZoom</code>.'),
]


def patch_html_texts(html_text):
    """Gibt (Text, Trefferliste) zurueck - Treffer werden im Report gemeldet."""
    hits = []
    for old, new in HTML_TEXT_PATCHES:
        n = html_text.count(old)
        hits.append(n)
        html_text = html_text.replace(old, new)
    return html_text, hits


def main():
    print(f"Quelle: {SRC}\nZiel  : {DST}\n")
    text, report = patch_background()
    print("background.js:")
    print("\n".join(report))
    failed = [line for line in report if "FEHL" in line]

    if CHECK:
        print("\n--check: nichts geschrieben.")
        return 1 if failed else 0
    if failed:
        print("\nABBRUCH: mindestens ein Patch hat nicht gegriffen. "
              "Die Firefox-Quelle hat sich geaendert - Patch-Liste anpassen.")
        return 1

    (DST / "background.js").write_text(text, encoding="utf-8")
    (DST / "manifest.json").write_text(MANIFEST, encoding="utf-8")

    for name in COPY_AS_IS:
        content = (SRC / name).read_text(encoding="utf-8")
        if name.endswith(".html"):
            content = add_compat_script(content)
            content, hits = patch_html_texts(content)
            if name == "options.html":
                print(f"  Hinweistexte in options.html angepasst: {hits} "
                      f"(Firefox-/Android-Erwaehnungen)")
        (DST / name).write_text(content, encoding="utf-8")

    # Nur die im Manifest referenzierten Groessen - jede zusaetzliche Datei im
    # Paket erzeugt beim Review nur Rueckfragen. Chrome kann kein SVG.
    # Sprachdateien mituebernehmen
    loc_dst = DST / "_locales"
    if loc_dst.exists():
        shutil.rmtree(loc_dst)
    shutil.copytree(SRC / "_locales", loc_dst)

    icons_dir = DST / "icons"
    if icons_dir.exists():
        shutil.rmtree(icons_dir)
    icons_dir.mkdir()
    for size in ("16", "32", "48", "128"):
        shutil.copy(SRC / "icons" / f"icon-{size}.png", icons_dir / f"icon-{size}.png")

    print("\nGeschrieben: manifest.json, background.js, "
          f"{len(COPY_AS_IS)} uebernommene Dateien, Icons (PNG - Chrome kann kein SVG).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
