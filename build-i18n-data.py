#!/usr/bin/env python3
"""Erzeugt i18n-data.js aus den Sprachdateien - fuer beide Auslieferungen.

_locales/ ist ein Sonderordner: der Browser nutzt ihn fuer die Store-Metadaten,
liefert ihn aber nicht ueber fetch() aus, solange er nicht in
web_accessible_resources steht. Statt daran zu drehen, werden die Texte in eine
gewoehnliche Skriptdatei geschrieben - kein Netzwerkweg, kein Sonderfall, und
in Firefox wie Chrome identisch.

Bis zum 7. August 2026 schrieb dieses Skript nur die Fassung im
Wurzelverzeichnis (Firefox). chrome-mv3/i18n-data.js blieb stehen, wo es
stand. Da die Datei die eigene Sprachwahl traegt, hiesse das: ein neuer oder
geaenderter Text erscheint in Firefox, in Chrome bleibt der alte - ohne
Fehlermeldung, denn eine veraltete Uebersetzung ist syntaktisch einwandfrei.
Aufgefallen ist es erst, als tests/i18n.test.mjs beide Fassungen verglich.
Deshalb laeuft es jetzt ueber alle Pakete, die ein _locales haben.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

# Jede Auslieferung mit eigenem _locales bekommt ihre eigene Tabelle. Die
# Liste steht nicht fest verdrahtet, sondern wird gefunden - kommt ein
# drittes Paket dazu, ist hier nichts zu aendern.
PAKETE = [p for p in (HERE, *sorted(d for d in HERE.iterdir() if d.is_dir()))
          if (p / "_locales").is_dir() and (p / "manifest.json").exists()]

if not PAKETE:
    sys.exit("Kein Paket mit _locales und manifest.json gefunden.")

for paket in PAKETE:
    out = {}
    for d in sorted((paket / "_locales").iterdir()):
        f = d / "messages.json"
        if not f.exists():
            continue
        data = json.loads(f.read_text(encoding="utf-8"))
        out[d.name] = {k: v["message"] for k, v in data.items()}

    body = json.dumps(out, ensure_ascii=False, separators=(",", ":"))
    ziel = paket / "i18n-data.js"
    ziel.write_text(
        "/* Automatisch aus _locales erzeugt - nicht von Hand aendern.\n"
        "   Erzeugen mit: python3 build-i18n-data.py */\n"
        f"const PAGESHOT_MESSAGES = {body};\n", encoding="utf-8")

    name = paket.name if paket != HERE else "(Wurzel/Firefox)"
    print(f"  {name:16} {len(out)} Sprachen, "
          f"{len(next(iter(out.values())))} Texte, {ziel.stat().st_size / 1024:.0f} KB")
