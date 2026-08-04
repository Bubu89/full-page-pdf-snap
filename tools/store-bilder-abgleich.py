#!/usr/bin/env python3
"""Haelt die Bilder auf der Produktseite mit denen im Store gleich.

    python3 tools/store-bilder-abgleich.py            # pruefen
    python3 tools/store-bilder-abgleich.py --holen    # abweichende uebernehmen
    python3 tools/store-bilder-abgleich.py --vorschau # kleine Fassungen bauen

Warum das ein Werkzeug braucht
------------------------------
Die Bilder auf `/tools/full-page-pdf-snap/` und die im Firefox-Store stammen
aus derselben Quelle (`make-store-screenshots.py`), laufen aber auseinander,
sobald eines von beiden erneuert wird. Am 4. August 2026 zeigte der Store
**fuenf** Bilder und die Seite **drei** — die beiden neueren fehlten, ohne dass
es jemandem aufgefallen waere.

Das ist keine Schoenheitsfrage: Wer auf der Seite sieht, was die Erweiterung
kann, und im Store etwas anderes, hat zweimal denselben Eindruck bekommen und
einmal den falschen.

Warum die Vorschau eigene Dateien braucht
-----------------------------------------
Die Seite lud die Bilder in voller Aufloesung — 890 kB fuer drei Vorschauen,
mit `loading="eager"`. Angezeigt werden sie mit wenigen hundert Pixeln Breite,
das volle Bild braucht nur, wer klickt. Die Vorschau ist deshalb eine eigene,
kleine WebP-Fassung; das grosse Bild laedt die Lightbox nach.
"""
import argparse
import hashlib
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
BILDER = HIER / "docs" / "screenshots"
AMO_API = ("https://addons.mozilla.org/api/v5/addons/addon/"
           "full_page_pdf_snap_webpagesave/")
KENNUNG = "provinglab-bilder/1.0 (+https://provinglab.dev/)"
VORSCHAU_BREITE = 480          # doppelt so breit wie die Anzeige, fuer scharfe Kanten


def store_bilder():
    req = urllib.request.Request(AMO_API, headers={"user-agent": KENNUNG})
    with urllib.request.urlopen(req, timeout=30) as a:
        d = json.load(a)
    aus = []
    for i, p in enumerate(d.get("previews", []), 1):
        req = urllib.request.Request(p["image_url"], headers={"user-agent": KENNUNG})
        with urllib.request.urlopen(req, timeout=60) as a:
            roh = a.read()
        aus.append({"nr": i, "groesse": p.get("image_size"), "bytes": roh,
                    "sha": hashlib.sha256(roh).hexdigest()[:12],
                    "titel": (p.get("caption") or {}).get("en-US") if isinstance(
                        p.get("caption"), dict) else p.get("caption")})
    return aus


def lokale_bilder():
    return sorted(BILDER.glob("0*_en.png"))


def vergleich():
    """Bild fuer Bild, nach Reihenfolge — die Store-Reihenfolge ist die, die
    ein Besucher sieht, und sie ist die einzige Zuordnung, die es gibt."""
    store = store_bilder()
    lokal = lokale_bilder()
    print(f"  Store: {len(store)} Bilder   Seite: {len(lokal)} Bilder\n")
    abweichung = False
    for i in range(max(len(store), len(lokal))):
        s = store[i] if i < len(store) else None
        l = lokal[i] if i < len(lokal) else None
        if s and not l:
            print(f"  !  {i+1}. im Store, aber nicht auf der Seite "
                  f"({s['groesse']}, sha {s['sha']})")
            abweichung = True
        elif l and not s:
            print(f"  !  {i+1}. auf der Seite, aber nicht im Store ({l.name})")
            abweichung = True
        else:
            eigen = hashlib.sha256(l.read_bytes()).hexdigest()[:12]
            gleich = eigen == s["sha"]
            print(f"  {'=' if gleich else '~'}  {i+1}. {l.name:<24} "
                  f"Seite {eigen}  Store {s['sha']}"
                  + ("" if gleich else "   ABWEICHUNG"))
            # Ungleiche Pruefsummen sind der Normalfall: AMO rechnet die Bilder
            # beim Hochladen um. Gemeldet wird es trotzdem, denn ob eine
            # Abweichung Umrechnung oder ein anderer Inhalt ist, entscheidet
            # niemand automatisch.
            if not gleich:
                abweichung = True
    return abweichung, store


def holen(store):
    """Fehlende Bilder aus dem Store uebernehmen.

    Nur fehlende: Ein vorhandenes zu ueberschreiben hiesse, die vom Store
    umgerechnete Fassung gegen das Original zu tauschen — schlechter, nicht
    besser.
    """
    lokal = lokale_bilder()
    for i, s in enumerate(store):
        if i < len(lokal):
            continue
        ziel = BILDER / f"{i+1:02d}_store_en.png"
        ziel.write_bytes(s["bytes"])
        print(f"  + {ziel.name} ({len(s['bytes'])//1024} kB) aus dem Store")


def vorschau():
    """Kleine WebP-Fassungen fuer die Seite. Das grosse Bild bleibt liegen —
    die Lightbox holt es, wenn jemand klickt."""
    try:
        from PIL import Image
    except ImportError:
        sys.exit("Pillow fehlt: pip install pillow")
    for p in lokale_bilder():
        im = Image.open(p)
        h = round(im.height * VORSCHAU_BREITE / im.width)
        klein = im.resize((VORSCHAU_BREITE, h), Image.LANCZOS)
        ziel = p.with_name(p.stem + "_klein.webp")
        klein.save(ziel, format="WEBP", quality=82, method=6)
        print(f"  {ziel.name:<30} {ziel.stat().st_size/1024:>6.0f} kB "
              f"(statt {p.stat().st_size/1024:.0f} kB)")


def main():
    a = argparse.ArgumentParser()
    a.add_argument("--holen", action="store_true", help="fehlende aus dem Store uebernehmen")
    a.add_argument("--vorschau", action="store_true", help="kleine Fassungen bauen")
    ns = a.parse_args()

    abweichung, store = vergleich()
    if ns.holen:
        print()
        holen(store)
    if ns.vorschau:
        print()
        vorschau()
    if abweichung and not (ns.holen or ns.vorschau):
        print("\n  Abweichungen gefunden. `--holen` uebernimmt fehlende Bilder,\n"
              "  `--vorschau` baut die kleinen Fassungen fuer die Seite.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
