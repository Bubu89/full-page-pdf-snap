#!/usr/bin/env python3
"""Schnuert das Einreich-Paket und legt es im festen upload-Ordner ab.

Der Ablageort bleibt bei jeder Version derselbe, damit Testen und Hochladen
immer aus demselben Pfad laufen. Erkennbar aktuell ist er am Aenderungsdatum
des Ordners und an VERSION.txt.

    upload/
      full-page-pdf-snap-chrome-<version>.zip   -> im Dashboard hochladen
      extension/                                -> chrome://extensions laden
      VERSION.txt                               -> Version, Datum, Pruefsumme
"""
import hashlib
import json
import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
UPLOAD = Path("/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Chrome/upload")

EXCLUDE_FILES = {"port.py", "pack.py", "README.md"}
EXCLUDE_DIRS = {"store-assets", "tests", "__pycache__"}

version = json.loads((HERE / "manifest.json").read_text())["version"]

files = []
for p in sorted(HERE.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(HERE)
    if rel.parts[0] in EXCLUDE_DIRS or rel.name in EXCLUDE_FILES or rel.suffix == ".zip":
        continue
    files.append((p, rel))

# --- Ziel leeren, damit keine Datei einer Vorversion liegen bleibt ----------
# Frueher wurde der ganze Ordner geloescht. Das scheitert, sobald eine Datei
# darin geoeffnet ist (Word sperrt .docx), und riss dabei Zusatzdateien mit.
UPLOAD.mkdir(parents=True, exist_ok=True)
for old_zip in UPLOAD.glob("*.zip"):
    old_zip.unlink()
if (UPLOAD / "extension").exists():
    shutil.rmtree(UPLOAD / "extension")

zip_path = UPLOAD / f"full-page-pdf-snap-chrome-{version}.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p, rel in files:
        z.write(p, rel.as_posix())

# --- Entpackte Fassung: exakt der Zip-Inhalt, nicht der Quellordner ---------
ext_dir = UPLOAD / "extension"
with zipfile.ZipFile(zip_path) as z:
    z.extractall(ext_dir)

digest = hashlib.sha256(zip_path.read_bytes()).hexdigest()
stamp = datetime.now()

(UPLOAD / "VERSION.txt").write_text(
    f"Full Page PDF Snap - Chrome MV3\n"
    f"{'=' * 33}\n\n"
    f"Version   : {version}\n"
    f"Erstellt  : {stamp:%d.%m.%Y %H:%M:%S}\n"
    f"Dateien   : {len(files)}\n"
    f"Groesse   : {zip_path.stat().st_size / 1024:.0f} KB\n"
    f"SHA-256   : {digest}\n\n"
    f"Hochladen : {zip_path.name}\n"
    f"Testen    : Ordner extension\\ ueber chrome://extensions laden\n",
    encoding="utf-8")

# Store-Assets mitliefern, damit im Upload-Ordner alles beisammen liegt
assets_src = HERE / "store-assets"
if assets_src.exists():
    assets_dst = UPLOAD / "store-assets"
    assets_dst.mkdir(exist_ok=True)
    for a in sorted(assets_src.glob("*.png")):
        shutil.copy(a, assets_dst / a.name)

# Aenderungsdatum des Ordners auf jetzt setzen - macht im Explorer sofort
# sichtbar, wie aktuell der Stand ist.
now = stamp.timestamp()
os.utime(UPLOAD, (now, now))

print(f"upload/  aktualisiert  ({stamp:%d.%m.%Y %H:%M:%S})")
print(f"  {zip_path.name}  ({zip_path.stat().st_size / 1024:.0f} KB, {len(files)} Dateien)")
print(f"  extension/  entpackt zum lokalen Testen")
print(f"  SHA-256: {digest[:16]}...")
