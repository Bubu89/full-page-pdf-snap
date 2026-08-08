#!/usr/bin/env python3
"""Erzeugt docs/sitemap.xml aus dem, was tatsaechlich unter docs/ liegt.

    python3 build-sitemap.py            # schreiben
    python3 build-sitemap.py --check    # nur pruefen, Exitcode 1 bei Abweichung

Warum erzeugt statt gepflegt: die Liste wurde von Hand gefuehrt, und am
3. August 2026 fehlten darin drei veroeffentlichte Messungen und zwei
Datensaetze. Eine Seite, die nicht in der Sitemap steht, ist fuer die Indizes,
aus denen Antwortsysteme schoepfen, nicht vorhanden — und niemand merkt es,
weil die Seite selbst einwandfrei aussieht.

lastmod kommt aus dem letzten Commit, der die Datei angefasst hat, nicht aus
der Dateizeit: ein Neubau aller Seiten wuerde sonst jede Seite als frisch
ausweisen und den Wert wertlos machen.
"""
import argparse
import subprocess
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
BASIS = "https://provinglab.dev"
ZIEL = DOCS / "sitemap.xml"

# Nicht in den Index: die Weiterleitungsstummel an der Wurzel und Verzeichnisse
# ohne eigene Seite. Als GANZE Pfade, nicht als Namensteile — die Stummel heissen
# genau wie die Messungen, auf die sie zeigen, und ein Vergleich auf Pfadteile
# haette die drei echten Messungen unter measurements/ mit entfernt.
AUS = {"extension-permissions-risk/", "pdf-extension-permissions/",
       "webpage-to-pdf-for-ocr/", "screenshots/", ".well-known/", "_visual-check/"}

# Seiten, die keine index.html sind und trotzdem in den Index gehoeren.
EINZELN = ["privacy.html"]

# Rang und erwartete Aenderungshaeufigkeit nach Art der Seite.
RANG = [
    ("",                 "1.0", "weekly"),    # Startseite
    ("tools/full-page-pdf-snap/", "0.9", "monthly"),
    ("recipes/",         "0.9", "monthly"),
    ("measurements/",    "0.8", "weekly"),
    ("notes/",           "0.8", "weekly"),
    ("tools/",           "0.8", "monthly"),
    ("data/",            "0.7", "weekly"),
    ("deutsch/",         "0.7", "monthly"),
    ("about/",           "0.4", "yearly"),
    ("disclaimer/",      "0.3", "yearly"),
]


def geaendert(pfad):
    """Datum des letzten Commits, der die Datei beruehrt hat."""
    r = subprocess.run(["git", "log", "-1", "--format=%cs", "--", str(pfad)],
                       cwd=HIER, capture_output=True, text=True)
    return r.stdout.strip() or "2026-08-03"


def einstufen(rel):
    if rel == "":
        return "1.0", "weekly"
    for prefix, prio, freq in RANG:
        if prefix and rel == prefix:
            return prio, freq
    # Ein Beitrag unterhalb einer Rubrik: wichtiger als die Rubrikseite selbst
    # war er nie, aendert sich aber praktisch nie mehr.
    if rel.startswith(("measurements/", "notes/")):
        return "0.7", "yearly"
    if rel.startswith("data/"):
        return "0.5", "yearly"
    return "0.5", "monthly"


def sammeln():
    eintraege = []
    for datei in sorted(DOCS.rglob("index.html")):
        rel = datei.parent.relative_to(DOCS).as_posix()
        rel = "" if rel == "." else rel + "/"
        if rel in AUS:
            continue
        prio, freq = einstufen(rel)
        eintraege.append((f"{BASIS}/{rel}", geaendert(datei), freq, prio))
    for name in EINZELN:
        datei = DOCS / name
        if datei.exists():
            eintraege.append((f"{BASIS}/{name}", geaendert(datei), "yearly", "0.3"))
    # Die JSON-Messdateien unter data/ stehen bewusst NICHT in der Sitemap.
    #
    # Eine Sitemap nennt Seiten, die in den Suchergebnissen erscheinen sollen.
    # Diese Dateien werden mit Content-Type application/json ausgeliefert und
    # koennen dort nie erscheinen. Google folgt der Sitemap trotzdem, crawlt sie
    # und meldet sie anschliessend als "Gefunden – zurzeit nicht indexiert" —
    # am 08.08.2026 betraf das 16 von 20 nicht indexierten Adressen, bei
    # 25 JSON-Dateien in der Sitemap.
    #
    # Auffindbar bleiben sie ueber /.well-known/api-catalog und ueber die
    # Verweise aus den Messberichten, die sie belegen. Das sind die Wege, auf
    # denen ein Agent sie ohnehin findet.
    # Startseite zuerst, dann nach Rang, dann alphabetisch — stabile Reihenfolge,
    # damit ein Diff nur echte Aenderungen zeigt.
    eintraege.sort(key=lambda e: (-float(e[3]), e[0]))
    return eintraege


def bauen(eintraege):
    zeilen = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, freq, prio in eintraege:
        zeilen += ["  <url>", f"    <loc>{loc}</loc>",
                   f"    <lastmod>{mod}</lastmod>",
                   f"    <changefreq>{freq}</changefreq>",
                   f"    <priority>{prio}</priority>", "  </url>"]
    zeilen.append("</urlset>")
    return "\n".join(zeilen) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()

    eintraege = sammeln()
    neu = bauen(eintraege)
    alt = ZIEL.read_text(encoding="utf-8") if ZIEL.exists() is not None else ""

    fehlten = [loc for loc, *_ in eintraege if loc not in alt]
    if fehlten:
        print(f"{len(fehlten)} Adressen fehlten in der bisherigen Sitemap:")
        for loc in fehlten:
            print("  +", loc)
    else:
        print("keine Adresse fehlte")

    if a.check:
        # Nur fehlende Adressen sind ein Grund anzuhalten. Ein Byte-Vergleich
        # scheitert in einer Pipeline immer: `lastmod` kommt aus `git log`, und
        # ein flacher Checkout kennt die Historie nicht — die Datei ist dann
        # anders, aber nicht falsch.
        sys.exit(1 if fehlten else 0)
    ZIEL.write_text(neu, encoding="utf-8")
    print(f"\n{len(eintraege)} Adressen geschrieben nach {ZIEL.relative_to(HIER)}")


if __name__ == "__main__":
    main()
