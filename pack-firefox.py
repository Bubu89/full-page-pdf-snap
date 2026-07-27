#!/usr/bin/env python3
"""Schnuert das Einreich-Paket fuer addons.mozilla.org.

Nimmt nur die Laufzeit-Dateien auf. Der Chrome-Zweig, die Projektseite, die
Tests und die Doku bleiben draussen - im XPI haetten sie nichts verloren und
erzeugen beim Review nur Rueckfragen.

Ablage wie beim Chrome-Paket in einem festen Ordner, damit Testen und
Hochladen immer aus demselben Pfad laufen.
"""
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPLOAD = Path("/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Firefox/upload")

# Nur diese Dateien gehoeren ins Paket
INCLUDE = ["manifest.json", "background.html", "background.js", "content.js",
           "popup.html", "popup.js", "options.html", "options.js", "pdf-writer.js"]
ICONS = ["icon-16.png", "icon-32.png", "icon-48.png", "icon-64.png",
         "icon-128.png", "icon.svg"]

manifest = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))
version = manifest["version"]

missing = [n for n in INCLUDE if not (HERE / n).exists()]
if missing:
    raise SystemExit(f"Fehlende Dateien: {missing}")

UPLOAD.mkdir(parents=True, exist_ok=True)
for old in UPLOAD.glob("*.zip"):
    old.unlink()

zip_path = UPLOAD / f"full-page-pdf-snap-firefox-{version}.zip"
count = 0
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for n in INCLUDE:
        z.write(HERE / n, n)
        count += 1
    for i in ICONS:
        src = HERE / "icons" / i
        if src.exists():
            z.write(src, f"icons/{i}")
            count += 1

digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
stamp = datetime.now()

(UPLOAD / "VERSION.txt").write_text(
    f"Full Page PDF Snap - Firefox (MV2)\n"
    f"{'=' * 34}\n\n"
    f"Version   : {version}\n"
    f"Erstellt  : {stamp:%d.%m.%Y %H:%M:%S}\n"
    f"Dateien   : {count}\n"
    f"Groesse   : {zip_path.stat().st_size / 1024:.0f} KB\n"
    f"SHA-256   : {digest}\n\n"
    f"Hochladen : {zip_path.name}\n"
    f"            addons.mozilla.org -> My Add-ons -> Full Page PDF Snap\n"
    f"            -> Upload New Version\n",
    encoding="utf-8")

now = stamp.timestamp()
os.utime(UPLOAD, (now, now))

print(f"upload/  aktualisiert  ({stamp:%d.%m.%Y %H:%M:%S})")
print(f"  {zip_path.name}  ({zip_path.stat().st_size / 1024:.0f} KB, {count} Dateien)")
print(f"  SHA-256: {digest[:16]}...")
