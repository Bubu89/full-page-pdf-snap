#!/usr/bin/env python3
"""Schnuert das Einreich-Paket fuer den Chrome Web Store.

Nimmt nur die Laufzeit-Dateien auf - Werkzeuge, Doku und Store-Assets bleiben
draussen, weil sie im Paket nur Angriffsflaeche und Review-Fragen erzeugen.
"""
import json
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXCLUDE_FILES = {"port.py", "pack.py", "README.md"}
EXCLUDE_DIRS = {"store-assets", "__pycache__"}

version = json.loads((HERE / "manifest.json").read_text())["version"]
target = HERE.parent / f"full-page-pdf-snap-chrome-{version}.zip"

files = []
for p in sorted(HERE.rglob("*")):
    if not p.is_file():
        continue
    rel = p.relative_to(HERE)
    if rel.parts[0] in EXCLUDE_DIRS or rel.name in EXCLUDE_FILES:
        continue
    if rel.suffix == ".zip":
        continue
    files.append((p, rel))

with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as z:
    for p, rel in files:
        z.write(p, rel.as_posix())

print(f"{target.name}  ({target.stat().st_size / 1024:.0f} KB, {len(files)} Dateien)")
for _, rel in files:
    print("   ", rel.as_posix())
