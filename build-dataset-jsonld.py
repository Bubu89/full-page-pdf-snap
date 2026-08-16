#!/usr/bin/env python3
"""Repariert Dataset-JSON-LD-Bloecke, die fremde Datensaetze beschreiben.

Befund 15.08.2026: Elf Seiten trugen im strukturierten Dataset-Block den
Verweis auf einen Datensatz, mit dem die Seite nichts zu tun hat — kopiert
aus der Vorlage einer anderen Seite. `who-actually-reads-this` beschrieb
die Android-Erweiterungs-Erhebung, `citation-by-platform` die
Druck-gegen-Aufnahme-Messung. Fuer Suchmaschinen und Dataset-Indexer sagte
jede dieser Seiten damals das Falsche.

Die Zuordnung steht unten explizit in REPARATUR — nicht erraten: je Seite der
Datensatz, auf den ihr Text selbst unter /data/ verweist. Name und
Beschreibung kommen aus der JSON-Datei des Datensatzes (question/methode),
die Schlagworte aus dem keywords-meta der Seite, das build-meta-nachschlag.py
schon gesetzt hat.

Sonderfaelle:

  - nineteen-issues verweist auf keinen Datensatz — der falsche Block wird
    entfernt, nicht ersetzt.
  - for-students verweist auf vier Datensaetze, keiner ist "der" Datensatz
    der Seite — bleibt, wie es ist, wird nur gemeldet.
  - firefox-and-chrome ist eine Begleitseite ohne eigene Messung; ihr
    Dataset-Verweis auf die Grundmessung ist Absicht und bleibt.

    python3 build-dataset-jsonld.py           # schreiben
    python3 build-dataset-jsonld.py --check   # nur berichten, Exitcode 1 bei Rest
"""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
CHECK = "--check" in sys.argv

REPARATUR = {
    "measurements/citation-by-platform/index.html":
        "2026-08-03-citation-by-platform.json",
    "measurements/citation-triage/index.html":
        "2026-08-03-citation-triage.json",
    "measurements/de-plattformen/index.html":
        "2026-08-03-de-plattformen.json",
    "measurements/install-an-extension-without-a-click/index.html":
        "2026-08-03-install-without-a-click.json",
    "measurements/reading-list-to-bibliography/index.html":
        "2026-08-03-reading-list-to-bibliography.json",
    "measurements/web-citations-that-vanish/index.html":
        "2026-08-02-quellen-archiv.json",
    "notes/agent-cites-a-source/index.html":
        "2026-08-04-install-uninstall-beide-richtungen.json",
    "notes/nineteen-issues/index.html": None,
    "notes/smaller-files-better-ocr/index.html":
        "2026-08-04-kompression-aufnahme.json",
    "notes/what-an-agent-may-install/index.html":
        "2026-08-04-beide-browser-headless.json",
    "notes/who-actually-reads-this/index.html":
        "ki-crawler-aktuell.json",
}

LIZENZ = "https://creativecommons.org/licenses/by/4.0/"


def dataset_block(datei, seite_s):
    d = json.loads((DOCS / "data" / datei).read_text(encoding="utf-8"))
    url = "https://provinglab.dev/data/" + datei
    name = d.get("measurement", "").replace("-", " ")
    beschreibung = d.get("question", "")
    datum = d.get("date", "")
    if not name:
        # ki-crawler-aktuell.json fuehrt deutsche Schluessel — der einzige
        # Datensatz dieser Bauart, darum hier benannt statt abgeleitet.
        name = "AI crawler traffic on provinglab.dev, rolling snapshot"
        methode = d.get("methode", {})
        beschreibung = methode.get("quelle", "")
        datum = d.get("gemessen_am", "")
    kw = re.search(r'<meta name="keywords" content="([^"]*)"', seite_s)
    block = {
        "@context": "https://schema.org",
        "@type": "Dataset",
        "name": name[:1].upper() + name[1:],
        "description": beschreibung,
        "url": url,
        "identifier": url,
        "datePublished": datum,
        "license": LIZENZ,
        "isAccessibleForFree": True,
        "inLanguage": "en",
    }
    if kw:
        block["keywords"] = kw.group(1)
    return block


def reparieren(pfad):
    datei = DOCS / pfad
    s = datei.read_text(encoding="utf-8")
    ziel = REPARATUR[pfad]
    muster = re.compile(
        r'<script type="application/ld\+json">\s*\{[^{]*?"@type":\s*"Dataset".*?</script>\s*',
        re.S)
    if not muster.search(s):
        # web-citations/agent-cites tragen den Block ohne url-Feld — das
        # Muster oben trifft sie trotzdem; hier nur Sicherheit.
        return s, "kein Dataset-Block gefunden"
    if ziel is None:
        neu = muster.sub("", s)
        return neu, "fremden Dataset-Block entfernt"
    block = dataset_block(ziel, s)
    ein = ('<script type="application/ld+json">\n'
           + json.dumps(block, ensure_ascii=False, indent=2)
           + "\n</script>\n")
    neu = muster.sub(ein, s, count=1)
    return neu, f"Dataset -> {ziel}"


def aktuell(pfad, s):
    """Ist der Block schon der richtige? An der url im Block erkennbar."""
    ziel = REPARATUR[pfad]
    m = re.search(r'"@type":\s*"Dataset"', s)
    if ziel is None:
        return m is None
    if not m:
        return False
    return ('"url": "https://provinglab.dev/data/%s"' % ziel) in s


def main():
    offen = 0
    for pfad in REPARATUR:
        s = (DOCS / pfad).read_text(encoding="utf-8")
        if aktuell(pfad, s):
            continue
        if CHECK:
            offen += 1
            print(f"offen: {pfad}")
            continue
        neu, was = reparieren(pfad)
        (DOCS / pfad).write_text(neu, encoding="utf-8")
        print(f"  {pfad}: {was}")
    if CHECK:
        print(f"\n{offen} von {len(REPARATUR)} Seiten noch offen.")
        sys.exit(1 if offen else 0)
    print("\nfertig.")


if __name__ == "__main__":
    main()
