#!/usr/bin/env python3
"""Erzeugt i18n-data.js aus den Sprachdateien.

_locales/ ist ein Sonderordner: der Browser nutzt ihn fuer die Store-Metadaten,
liefert ihn aber nicht ueber fetch() aus, solange er nicht in
web_accessible_resources steht. Statt daran zu drehen, werden die Texte in eine
gewoehnliche Skriptdatei geschrieben - kein Netzwerkweg, kein Sonderfall, und
in Firefox wie Chrome identisch.
"""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = {}
for d in sorted((HERE / "_locales").iterdir()):
    f = d / "messages.json"
    if not f.exists():
        continue
    data = json.loads(f.read_text(encoding="utf-8"))
    out[d.name] = {k: v["message"] for k, v in data.items()}

body = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
(HERE / "i18n-data.js").write_text(
    "/* Automatisch aus _locales erzeugt - nicht von Hand aendern.\n"
    "   Erzeugen mit: python3 build-i18n-data.py */\n"
    f"const PAGESHOT_MESSAGES = {body};\n", encoding="utf-8")

size = (HERE / "i18n-data.js").stat().st_size
print(f"  i18n-data.js: {len(out)} Sprachen, "
      f"{len(next(iter(out.values())))} Texte, {size / 1024:.0f} KB")
