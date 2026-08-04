#!/usr/bin/env python3
"""Erzeugt die Agenten-Karte aus dem Worker — statt sie von Hand zu pflegen.

    python3 build-server-card.py
    python3 build-server-card.py --check     # Exitcode 1, wenn nicht aktuell

Am 4. August 2026 stand in der Karte Fassung 1.15.0 mit vier Werkzeugen,
waehrend der Endpunkt 1.21.0 mit neun auslieferte. Darunter `install_extension`
— ausgerechnet das, mit dem ein Agent die Erweiterung ohne Klick einrichtet.
Wer die Karte liest statt `tools/list` zu rufen, sah diese Faehigkeit nicht.

Eine Datei, die dasselbe behauptet wie eine andere und von Hand gepflegt wird,
laeuft irgendwann auseinander. Die einzige Abhilfe ist, sie nicht zu pflegen,
sondern abzuleiten.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
WORKER = HIER / "worker" / "mcp.js"
ZIEL = HIER / "docs" / ".well-known" / "mcp" / "server-card.json"


def js_string(text, start):
    """Einen JS-Ausdruck aus aneinandergehaengten Zeichenketten zusammensetzen.

    Die Beschreibungen im Worker stehen als "..." + "..." ueber mehrere
    Zeilen. Ein Muster, das nur das erste Stueck nimmt, liefert einen
    abgeschnittenen Satz — und der wandert dann in die Karte.
    """
    teile, i, n = [], start, len(text)
    while i < n:
        while i < n and text[i] in ' \t\r\n+':
            i += 1
        if i >= n or text[i] != '"':
            break
        i += 1
        stueck = []
        while i < n and text[i] != '"':
            if text[i] == "\\":
                stueck.append(text[i:i + 2])
                i += 2
                continue
            stueck.append(text[i])
            i += 1
        i += 1
        teile.append("".join(stueck))
    roh = "".join(teile)
    # Nur die tatsaechlichen Escape-Sequenzen aufloesen. `unicode_escape`
    # ueber die ganze Zeichenkette zerstoert UTF-8, weil es sie als Latin-1
    # liest — aus einem Gedankenstrich wird dann Buchstabensalat.
    einfach = {"n": chr(10), "t": chr(9), "r": chr(13),
               chr(34): chr(34), chr(92): chr(92), "/": "/"}

    def ersetze(m):
        z = m.group(1)
        if z.startswith("u") and len(z) == 5:
            return chr(int(z[1:], 16))
        return einfach.get(z, z)

    return re.sub(r"\\(u[0-9a-fA-F]{4}|.)", ersetze, roh)


def werkzeuge():
    t = WORKER.read_text(encoding="utf-8")
    # Nur der Definitionsblock, nicht jede Erwaehnung eines Namens im Code.
    anfang = t.index("const TOOLS") if "const TOOLS" in t else 0
    block = t[anfang:t.index("];", anfang) + 2] if "];" in t[anfang:] else t
    gefunden = []
    for m in re.finditer(r'name:\s*"(\w+)",\s*\n\s*description:', block):
        name = m.group(1)
        beschr = js_string(block, block.index("description:", m.start()) + len("description:"))
        gefunden.append({"name": name, "description": beschr.strip()})
    return gefunden


def version():
    m = re.search(r'const VERSION = "([^"]+)"', WORKER.read_text(encoding="utf-8"))
    return m.group(1) if m else None


def karte():
    wz = werkzeuge()
    # Gegenproben: ein Parser, der still zu wenig findet, ist schlimmer als
    # eine veraltete Datei — er sieht richtig aus.
    if len(wz) < 8:
        raise SystemExit(f"Nur {len(wz)} Werkzeuge erkannt — der Parser greift nicht.")
    namen = {w["name"] for w in wz}
    if "install_extension" not in namen:
        raise SystemExit("install_extension nicht erkannt — Abbruch statt stiller Luecke.")
    kurz = [w for w in wz if len(w["description"]) < 40]
    if kurz:
        raise SystemExit(f"Abgeschnittene Beschreibungen: {[w['name'] for w in kurz]}")

    return {
        "$schema": "https://modelcontextprotocol.io/schema/2025-06-18/server-card.json",
        "serverInfo": {
            "name": "provinglab",
            "version": version(),
            "title": "Proving Lab",
            "description":
                "Measurement datasets and reproducible methods on browser tools, OCR "
                "pipelines and AI-assisted development. Every dataset has a documented "
                "method and a control run.",
        },
        "protocolVersion": "2025-06-18",
        "transport": {"type": "streamable-http",
                      "endpoint": "https://provinglab.dev/mcp"},
        "capabilities": {"tools": {"listChanged": False}},
        "tools": wz,
        "authentication": {"type": "none"},
        "registry": {
            "name": "dev.provinglab/browser-citation-capture",
            "url": "https://registry.modelcontextprotocol.io",
        },
        "documentation": "https://provinglab.dev/auth.md",
        "license": "https://creativecommons.org/licenses/by/4.0/",
        "_hinweis":
            "Erzeugt aus worker/mcp.js durch build-server-card.py — nicht von Hand "
            "aendern. Bis zum 4. August 2026 war diese Datei handgepflegt und nannte "
            "vier von neun Werkzeugen bei einer drei Fassungen alten Versionsnummer.",
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    neu = json.dumps(karte(), indent=2, ensure_ascii=False) + "\n"
    alt = ZIEL.read_text(encoding="utf-8") if ZIEL.exists() else ""
    k = karte()
    if a.check:
        if neu != alt:
            print(f"  server-card.json veraltet — {len(k['tools'])} Werkzeuge, "
                  f"Fassung {k['serverInfo']['version']}")
            sys.exit(1)
        print(f"  server-card.json aktuell ({len(k['tools'])} Werkzeuge, "
              f"{k['serverInfo']['version']})")
        return
    ZIEL.write_text(neu, encoding="utf-8")
    print(f"  server-card.json: {len(k['tools'])} Werkzeuge, "
          f"Fassung {k['serverInfo']['version']}")
    for w in k["tools"]:
        print(f"    {w['name']:<22} {w['description'][:58]}…")


if __name__ == "__main__":
    main()
