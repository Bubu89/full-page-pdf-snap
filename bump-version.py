#!/usr/bin/env python3
"""Setzt die naechste freie Versionsnummer - gegen den Store geprueft.

Blindes Hochzaehlen reicht nicht: Es ist schon passiert, dass eine Version
lokal gebaut wurde, die im Store bereits veroeffentlicht war. AMO lehnt so
etwas beim Upload ab, und das faellt erst dort auf.

Darum wird die veroeffentlichte Version bei AMO abgefragt und die naechste
freie Nummer daraus abgeleitet.

    python3 bump-version.py            # naechste Minor-Version (2.3.0 -> 2.4.0)
    python3 bump-version.py --patch    # naechste Patch-Version (2.3.0 -> 2.3.1)
    python3 bump-version.py --check    # nur pruefen, nichts aendern
    python3 bump-version.py --set 3.0.0
"""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLUG = "full_page_pdf_snap_webpagesave"
AMO = f"https://addons.mozilla.org/api/v5/addons/addon/{SLUG}/"


def parse(v):
    parts = (v.split(".") + ["0", "0"])[:3]
    return tuple(int(p) for p in parts)


def fmt(t):
    return ".".join(str(x) for x in t)


def published_versions():
    """Alle bei AMO bekannten Versionen. Leere Liste, wenn nicht erreichbar -
    dann wird nur lokal hochgezaehlt und das deutlich gemeldet."""
    try:
        with urllib.request.urlopen(AMO + "versions/?lang=en-US", timeout=10) as r:
            data = json.loads(r.read())
        return [v["version"] for v in data.get("results", [])]
    except Exception as e:
        print(f"  WARNUNG: AMO nicht erreichbar ({str(e)[:50]}) - nur lokal gezaehlt")
        return []


def main():
    local = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["version"]
    remote = published_versions()
    published = local in remote

    print(f"  lokal        : {local}")
    print(f"  bei AMO      : {', '.join(remote[:5]) if remote else '(unbekannt)'}")
    print(f"  Status       : {'VEROEFFENTLICHT' if published else 'noch nicht veroeffentlicht'}")

    # Zielnummer bestimmen
    if "--set" in sys.argv:
        target = sys.argv[sys.argv.index("--set") + 1]
    elif not published:
        # Noch nicht draussen - es gibt nichts hochzuzaehlen. Sonst springt die
        # Nummer bei jedem Zwischenlauf, ohne dass je etwas hochgeladen wurde.
        print(f"  Ergebnis     : {local} bleibt.")
        return 0
    else:
        # Vom hoechsten bekannten Stand aus weiter - lokal ODER veroeffentlicht.
        maj, mi, pa = max([parse(local)] + [parse(v) for v in remote])
        target = fmt((maj, mi, pa + 1)) if "--patch" in sys.argv else fmt((maj, mi + 1, 0))

    if target in remote:
        print(f"  ABBRUCH      : {target} ist bereits veroeffentlicht.")
        return 1

    print(f"  Ergebnis     : {local} -> {target}")
    if "--check" in sys.argv:
        print("  --check: nichts geschrieben.")
        return 0

    f = HERE / "manifest.json"
    m = json.loads(f.read_text(encoding="utf-8"))
    m["version"] = target
    f.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    f = HERE / "chrome-mv3" / "port.py"
    t = f.read_text(encoding="utf-8")
    f.write_text(t.replace(f'"version": "{local}",', f'"version": "{target}",'), encoding="utf-8")

    print("  geschrieben in manifest.json und chrome-mv3/port.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
