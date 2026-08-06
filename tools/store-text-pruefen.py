#!/usr/bin/env python3
"""Prueft Store-Texte gegen die Regeln, an denen schon eine Einreichung scheiterte.

    python3 tools/store-text-pruefen.py DATEI…            # Chrome-Regeln (streng)
    python3 tools/store-text-pruefen.py --amo DATEI…      # AMO-Regeln (nur Laengen)

Am 02.08.2026 lehnte Google die Chrome-Einreichung ab: "Mimicking ranking,
performance, current status or promotional information: free badge in media."
Betroffen waren zwei Bilder und der Beschreibungstext, der 'Completely free' als
Versalien-Schlagzeile trug.

Der Unterschied zwischen den Stores ist echt und keine Vorsicht: derselbe Text
laeuft bei Mozilla seit Monaten. Deshalb zwei Regelsaetze statt einem strengen.
"""
import argparse
import re
import sys
from pathlib import Path

# Als Werbeaussage untersagt. Sachlich verneint ("no ads") bleibt erlaubt —
# das beschreibt eine Eigenschaft, keinen Store-Status.
WORTE = ["free", "premium", "recommended", "best", "#1", "number one", "top-rated"]

# Diese Verwendungen sind gepruefte Ausnahmen und loesen keinen Treffer aus.
ERLAUBT = [
    r"free software",          # Lizenzaussage
    r"free of charge",         # sachliche Angabe im Fliesstext
    r"MIT licen[sc]e",
    r"no free",                # "no free tier"
    r"freie Software",
    r"kostenlos",              # deutsche Fassung sagt es sachlich
]

GRENZEN = {"chrome": {"summary": 132, "name": 45}, "amo": {"summary": 250, "name": 50}}

# Am 05.08.2026 lehnte Google ein zweites Mal ab: "Spam and Placement in the
# Store — Having excessive keywords in the item's description", genannt wurden
# PubMed, arXiv, SpringerLink, Wiley, ScienceDirect, JMIR, doi.org. Es war eine
# einzige Zeile mit sieben Anbieternamen hintereinander.
#
# Die Regel greift deshalb an der Bauart, nicht an einer Verbotsliste: eine
# Aufzaehlung fremder Produkt- oder Anbieternamen ab einer bestimmten Zahl ist
# das Muster, das als Keyword-Stuffing gelesen wird — unabhaengig davon, welche
# Namen gerade darin stehen. Wer stattdessen die Faehigkeit beschreibt
# ("liest die Zitationsangaben, die Verlage einbetten"), sagt ohnehin das
# Genauere und faellt nicht darunter.
FREMDNAMEN = [
    "PubMed", "arXiv", "SpringerLink", "Springer", "Wiley", "ScienceDirect",
    "Elsevier", "JMIR", "doi.org", "JSTOR", "ResearchGate", "Scopus", "PLOS",
    "Zotero", "Citavi", "EndNote", "Mendeley", "Papers", "Paperpile",
    "LinkedIn", "Twitter", "Facebook", "Instagram", "Reddit", "Notion",
    "Gmail", "Outlook", "Confluence", "SharePoint", "VitePress", "Docusaurus",
]
NAMEN_JE_ZEILE = 3      # ab drei Namen in einer Zeile liegt eine Aufzaehlung vor


def namen_haeufung(text):
    """Zeilen, in denen sich fremde Produktnamen zu einer Aufzaehlung reihen."""
    treffer = []
    for i, z in enumerate(text.splitlines(), 1):
        gefunden = []
        for n in FREMDNAMEN:
            if re.search(r"(?<![\w.])" + re.escape(n) + r"(?![\w])", z, re.I):
                gefunden.append(n)
        # "Springer" ist in "SpringerLink" enthalten - nicht doppelt zaehlen
        if "SpringerLink" in gefunden and "Springer" in gefunden:
            gefunden.remove("Springer")
        if len(gefunden) >= NAMEN_JE_ZEILE:
            treffer.append((i, gefunden, z.strip()))
    return treffer


def zeilen_mit_versalien(text):
    """Ueberschriften in Grossbuchstaben — bei Chrome als Werbebanner gelesen."""
    treffer = []
    for i, z in enumerate(text.splitlines(), 1):
        z = z.strip()
        if len(z) < 6 or len(z) > 80:
            continue
        buchstaben = [c for c in z if c.isalpha()]
        if buchstaben and all(c.isupper() for c in buchstaben):
            treffer.append((i, z))
    return treffer


def sonderzeichen_rahmen(text):
    return [(i, z.strip()) for i, z in enumerate(text.splitlines(), 1)
            if re.fullmatch(r"[+*=~#_-]{4,}", z.strip())]


def pruefe(pfad, amo):
    text = Path(pfad).read_text(encoding="utf-8")
    name = Path(pfad).name
    fehler = []

    grenze = GRENZEN["amo" if amo else "chrome"]
    if "SUMMARY" in name.upper() and len(text.strip()) > grenze["summary"]:
        fehler.append(f"Summary {len(text.strip())} Zeichen, Grenze {grenze['summary']}")
    if "NAME" in name.upper() and len(text.strip()) > grenze["name"]:
        fehler.append(f"Name {len(text.strip())} Zeichen, Grenze {grenze['name']}")

    if not amo:
        for i, z in zeilen_mit_versalien(text):
            fehler.append(f"Zeile {i}: Versalien-Schlagzeile — {z[:56]}")
        for i, z in sonderzeichen_rahmen(text):
            fehler.append(f"Zeile {i}: Rahmen aus Sonderzeichen — {z[:30]}")
        for i, namen, z in namen_haeufung(text):
            fehler.append(f"Zeile {i}: {len(namen)} fremde Produktnamen in einer Zeile "
                          f"({', '.join(namen)}) — als 'excessive keywords' abgelehnt am "
                          f"05.08.2026. Faehigkeit beschreiben statt Anbieter aufzaehlen.")
        klein = text.lower()
        for w in WORTE:
            for m in re.finditer(r"\b" + re.escape(w) + r"\b", klein):
                umfeld = klein[max(0, m.start() - 30):m.end() + 30]
                if any(re.search(a, umfeld, re.I) for a in ERLAUBT):
                    continue
                zeile = text[:m.start()].count("\n") + 1
                fehler.append(f"Zeile {zeile}: Werbewort '{w}' — …{umfeld.strip()}…")

    return fehler


def main():
    p = argparse.ArgumentParser()
    p.add_argument("dateien", nargs="+")
    p.add_argument("--amo", action="store_true", help="AMO-Regeln statt Chrome-Regeln")
    a = p.parse_args()

    gesamt = 0
    for f in a.dateien:
        fehler = pruefe(f, a.amo)
        marke = "OK" if not fehler else f"{len(fehler)} Befund(e)"
        print(f"{Path(f).name:34} {marke}")
        for x in fehler[:12]:
            print("   ", x)
        gesamt += len(fehler)
    print(f"\n{'AMO' if a.amo else 'Chrome'}-Regeln: {gesamt} Befund(e)")
    sys.exit(1 if gesamt else 0)


if __name__ == "__main__":
    main()
