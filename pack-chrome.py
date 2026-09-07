#!/usr/bin/env python3
"""Baut das hochladbare Paket fuer den Chrome Web Store.

Gegenstueck zu pack-firefox.py. Das Chrome-Paket wurde bis 2.35.16 von Hand
zusammengestellt — mit dem Ergebnis, dass Aenderungen an gemeinsamen Dateien
(pdf-writer.js, zitate.js, den Sprachdateien) einmal in der Firefox-Fassung
ankamen und in der Chrome-Fassung nicht. Genau dieser Fehler hat schon einmal
eine Datei jahrelang aus dem Firefox-Paket ferngehalten.

Aufgenommen wird deshalb nach einer festen Liste, und jede Datei darin muss
vorhanden sein — fehlt eine, bricht der Lauf ab, statt ein unvollstaendiges
Paket abzuliefern.
"""
import hashlib
import json
import zipfile
from datetime import datetime
from pathlib import Path

WURZEL = Path(__file__).resolve().parent
QUELLE = WURZEL / "chrome-mv3"
UPLOAD = Path("/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Chrome/upload")

# Was ins Paket gehoert. Reihenfolge egal, Vollstaendigkeit nicht.
DATEIEN = [
    "manifest.json",
    "background.js", "cdp-vektor.js", "compat.js", "content.js",
    "i18n.js", "i18n-data.js", "pdf-writer.js", "zitate.js", "zeitanker.js",
    "options.html", "options.js",
    "popup.html", "popup.js",
    "result.html", "result.js",
    "icons/icon-16.png", "icons/icon-32.png", "icons/icon-48.png", "icons/icon-128.png",
]
SPRACHEN = ["de", "en", "es", "fr", "it", "ja", "pt_BR", "ru", "zh_CN"]


def pruefe_gemeinsame_dateien():
    """Die Dateien, die sich Firefox und Chrome teilen, muessen gleich sein.

    Sie liegen doppelt im Baum — einmal in der Wurzel, einmal unter
    chrome-mv3/. Laufen sie auseinander, faellt das sonst erst auf, wenn ein
    Nutzer eine Fassung meldet, die die andere laengst behoben hat.

    Nicht in der Liste stehen die Dateien, die sich UNTERSCHEIDEN SOLLEN:

      popup.html    laedt in der Chrome-Fassung zusaetzlich compat.js
      background.js ist in beiden Fassungen ein eigenes Programm
                    (Hintergrundseite gegen Service Worker)
      manifest.json Fassung 2 gegen Fassung 3
    """
    geteilt = ["pdf-writer.js", "zitate.js", "zeitanker.js", "i18n.js",
               "i18n-data.js", "options.html", "options.js",
               "popup.js", "content.js"]
    abweichend = []
    for name in geteilt:
        a, b = WURZEL / name, QUELLE / name
        if not a.exists() or not b.exists():
            continue
        if a.read_bytes() != b.read_bytes():
            abweichend.append(name)
    return abweichend


def main():
    manifest = json.loads((QUELLE / "manifest.json").read_text(encoding="utf8"))
    version = manifest["version"]

    fehlend = [d for d in DATEIEN if not (QUELLE / d).exists()]
    fehlend += [f"_locales/{s}/messages.json" for s in SPRACHEN
                if not (QUELLE / "_locales" / s / "messages.json").exists()]
    if fehlend:
        raise SystemExit("FEHLT im Chrome-Baum:\n  " + "\n  ".join(fehlend))

    abweichend = pruefe_gemeinsame_dateien()
    if abweichend:
        print("  ACHTUNG — gemeinsame Dateien weichen ab:")
        for n in abweichend:
            print(f"    {n}")
        print("    (Firefox-Fassung und Chrome-Fassung sind nicht gleich)")

    UPLOAD.mkdir(parents=True, exist_ok=True)
    for alt in UPLOAD.glob("full-page-pdf-snap-chrome-*.zip"):
        if alt.name != f"full-page-pdf-snap-chrome-{version}.zip":
            alt.unlink()

    ziel = UPLOAD / f"full-page-pdf-snap-chrome-{version}.zip"
    alle = DATEIEN + [f"_locales/{s}/messages.json" for s in SPRACHEN]
    with zipfile.ZipFile(ziel, "w", zipfile.ZIP_DEFLATED) as z:
        for name in alle:
            z.write(QUELLE / name, name)

    roh = ziel.read_bytes()
    stamp = datetime.now()
    (UPLOAD / "VERSION.txt").write_text(
        f"Full Page PDF Snap — Chrome\n"
        f"Version   : {version}\n"
        f"Gebaut    : {stamp:%d.%m.%Y %H:%M:%S}\n"
        f"Dateien   : {len(alle)}\n"
        f"SHA-256   : {hashlib.sha256(roh).hexdigest()}\n",
        encoding="utf8")

    print(f"upload/  aktualisiert  ({stamp:%d.%m.%Y %H:%M:%S})")
    print(f"  {ziel.name}  ({len(roh) // 1024} KB, {len(alle)} Dateien)")
    print(f"  SHA-256: {hashlib.sha256(roh).hexdigest()[:16]}...")


if __name__ == "__main__":
    main()
