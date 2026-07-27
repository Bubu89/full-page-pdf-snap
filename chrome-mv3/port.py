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
    ("Compat-Layer im Service Worker laden",
     '"use strict";\n',
     '"use strict";\n\n// Chrome MV3: Namensraum, DOM-Ersatz und data:-URL-Helfer.\n'
     'importScripts("compat.js");\n', 1),

    ("blobToImage -> createImageBitmap (kein DOM im Service Worker)",
     re.compile(r"async function blobToImage\(blob\) \{.*?\n\}\n", re.S),
     "", 1),

    ("canvasToJpegBytes -> OffscreenCanvas.convertToBlob",
     re.compile(r"function canvasToJpegBytes\(canvas, quality\) \{.*?\n\}\n", re.S),
     "", 1),

    ("document.createElement(canvas) -> OffscreenCanvas",
     'document.createElement("canvas")',
     "createCanvas()", 3),

    ("PDF-Blob -> data:-URL statt Blob-URL",
     "const url = URL.createObjectURL(pdfBlob);",
     "const url = await blobToDataUrl(pdfBlob);", 1),

    ("revokeObjectURL entfaellt bei data:-URLs",
     re.compile(r"setTimeout\(\(\) => URL\.revokeObjectURL\(url\), 60_000\);"),
     "revokeDownloadUrl(url);", 1),

    ("tabs.executeScript -> scripting.executeScript",
     'await browser.tabs.executeScript(tabId, { file: "content.js" });',
     'await injectContentScript(tabId, "content.js");', 1),
]

# Dateien, die unveraendert uebernommen werden
COPY_AS_IS = ["content.js", "pdf-writer.js", "popup.html", "popup.js",
              "options.html", "options.js"]

MANIFEST = """{
  "manifest_version": 3,
  "name": "Full Page PDF Snap",
  "short_name": "PDFSnap",
  "version": "2.2.0",
  "description": "Save any webpage as a single high-resolution PDF. Runs entirely on your device \\u2014 no upload, no account, no data collection.",
  "author": "Bubu89",
  "minimum_chrome_version": "116",
  "icons": {
    "16": "icons/icon-16.png",
    "48": "icons/icon-48.png",
    "128": "icons/icon-128.png"
  },
  "permissions": [
    "activeTab",
    "tabs",
    "downloads",
    "downloads.open",
    "storage",
    "contextMenus",
    "notifications",
    "scripting"
  ],
  "host_permissions": ["<all_urls>"],
  "background": {
    "service_worker": "background.js"
  },
  "action": {
    "default_icon": {
      "16": "icons/icon-16.png",
      "48": "icons/icon-48.png"
    },
    "default_title": "Full Page PDF Snap \\u2014 save the whole page as PDF (Ctrl+Shift+Y)",
    "default_popup": "popup.html"
  },
  "options_ui": {
    "page": "options.html",
    "open_in_tab": true
  },
  "commands": {
    "capture-full-page": {
      "suggested_key": { "default": "Ctrl+Shift+Y" },
      "description": "Save the whole page as PDF"
    }
  }
}
"""


def patch_background():
    text = (SRC / "background.js").read_text(encoding="utf-8")
    report = []
    for desc, pattern, repl, expected in PATCHES:
        if isinstance(pattern, re.Pattern):
            text, n = pattern.subn(repl, text)
        else:
            n = text.count(pattern)
            text = text.replace(pattern, repl)
        ok = "OK  " if n == expected else "FEHL"
        report.append(f"  [{ok}] {desc}  ({n}/{expected})")
    return text, report


def add_compat_script(html_text):
    """compat.js vor dem eigenen Skript laden, damit `browser` existiert."""
    return re.sub(r'(<script src="(?:popup|options)\.js")',
                  r'<script src="compat.js"></script>\n  \1',
                  html_text, count=1)


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
        (DST / name).write_text(content, encoding="utf-8")

    # Nur die im Manifest referenzierten Groessen - jede zusaetzliche Datei im
    # Paket erzeugt beim Review nur Rueckfragen. Chrome kann kein SVG.
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
