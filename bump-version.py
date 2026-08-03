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
import re
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


# --- Chrome ---------------------------------------------------------------
#
# Chrome laeuft auf einer eigenen Reihe: bei Firefox stand 2.19.0, im
# Chrome-Paket 2.2.0. Das ist kein Versehen, sondern die Folge davon, dass
# beide Stores unterschiedlich oft angenommen haben. Wer beide Nummern
# gleichzieht, bekommt beim naechsten Upload eine Ablehnung wegen einer
# Version, die dort schon existiert.
#
# Der Chrome Web Store hat keine offene Abfrage fuer die veroeffentlichte
# Version. Massgeblich ist deshalb das zuletzt gebaute Paket im Upload-Ordner,
# hilfsweise das Manifest — beides laesst sich pruefen, im Gegensatz zu einer
# Annahme.
CHROME_MANIFEST = HERE / "chrome-mv3" / "manifest.json"
CHROME_UPLOAD = Path("/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Chrome/upload")

# Der Chrome Web Store bietet keine offene Abfrage der veroeffentlichten
# Version. Sie steht deshalb hier und wird bei jeder Annahme im Store
# nachgezogen — eine Zahl, die von Hand gepflegt wird, aber benannt ist,
# statt einer, die aus einer Datei geraten wird.
CHROME_STAND = "2.2.0"


def chrome_stand():
    """Hoechste Nummer, die fuer Chrome bereits gebaut wurde."""
    # Bewusst NICHT aus chrome-mv3/manifest.json: der Portierungslauf schreibt
    # dort die Firefox-Nummer hinein. Wer den Chrome-Stand von dort nimmt,
    # zaehlt die falsche Reihe hoch — am 03.08.2026 wurde so aus 2.2.0 eine
    # 2.20.0. Massgeblich sind die gebauten Pakete und CHROME_STAND.
    kandidaten = [CHROME_STAND]
    try:
        for f in CHROME_UPLOAD.glob("*chrome-*.zip"):
            m = re.search(r"(\d+\.\d+\.\d+)", f.name)
            if m:
                kandidaten.append(m.group(1))
    except Exception:
        pass
    return max(kandidaten, key=parse) if kandidaten else "0.0.0"


def chrome_setzen(neu):
    d = json.loads(CHROME_MANIFEST.read_text(encoding="utf-8"))
    alt = d.get("version")
    if alt == neu:
        return alt
    s = CHROME_MANIFEST.read_text(encoding="utf-8")
    CHROME_MANIFEST.write_text(s.replace(f'"{alt}"', f'"{neu}"', 1), encoding="utf-8")
    # Der Portierungslauf ueberschreibt das Manifest aus der Firefox-Quelle;
    # dort steht die Chrome-Nummer, damit sie den Lauf ueberlebt.
    pp = HERE / "chrome-mv3" / "port.py"
    if pp.exists():
        t = pp.read_text(encoding="utf-8")
        if alt and alt in t:
            pp.write_text(t.replace(alt, neu), encoding="utf-8")
    return neu


def main():
    local = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["version"]
    remote = published_versions()
    # Auch ein lokal gebautes Paket macht die Nummer unbrauchbar: es kann
    # laengst eingereicht sein, und die Wache im Paketbau lehnt sie ohnehin ab.
    # Nur AMO zu fragen liess bump-version "bleibt" melden, waehrend pack
    # unmittelbar danach abbrach — zwei Werkzeuge, zwei Wahrheiten.
    gebaut = False
    try:
        FF_UPLOAD = Path("/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Firefox/upload")
        gebaut = any(local in f.name for f in FF_UPLOAD.glob("*firefox-*.zip"))
    except Exception:
        pass
    published = (local in remote) or gebaut

    print(f"  lokal        : {local}")
    print(f"  bei AMO      : {', '.join(remote[:5]) if remote else '(unbekannt)'}")
    print(f"  Status       : {'VEROEFFENTLICHT' if local in remote else ('lokal gebaut' if gebaut else 'noch nicht veroeffentlicht')}")

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

    # Chrome laeuft auf einer eigenen Reihe und wird getrennt hochgezaehlt.
    # Sie an die Firefox-Nummer anzugleichen wuerde dort Nummern ueberspringen
    # oder — schlimmer — eine bereits eingereichte doppelt vergeben.
    c_alt = chrome_stand()
    a, b, _ = parse(c_alt)
    c_neu = f"{a}.{b + 1}.0" if "--patch" not in sys.argv else f"{a}.{b}.{parse(c_alt)[2] + 1}"
    if "--set-chrome" in sys.argv:
        c_neu = sys.argv[sys.argv.index("--set-chrome") + 1]
    chrome_setzen(c_neu)
    print(f"  Chrome       : {c_alt} -> {c_neu}  (eigene Reihe)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
