#!/usr/bin/env python3
"""build-feed.py — erzeugt docs/feed.xml aus den veroeffentlichten Beitraegen.

Ohne Feed erreicht die Seite eine ganze Gruppe von Lesern gar nicht: wer Feedly,
NetNewsWire, Miniflux oder Thunderbird benutzt, abonniert und kommt wieder —
statt einmal vorbeizuschauen und die Seite nie wiederzusehen. Aggregatoren wie
Lobsters und Planet-Seiten nehmen ebenfalls nur Feeds entgegen.

Quelle sind die Beitraege selbst, nicht eine gepflegte Liste: Titel aus <title>,
Zusammenfassung aus der meta-description, Datum aus dem JSON-LD, das ohnehin auf
jeder Seite steht. Damit kann der Feed nicht veralten, solange die Seite stimmt.

    python3 build-feed.py           # schreiben
    python3 build-feed.py --check   # nur pruefen, Exitcode 1 bei Abweichung

Gehoert nach jeder neuen Seite aufgerufen — und vor ping-suchmaschinen.py.
"""
import argparse
import glob
import html
import json
import re
import sys
from pathlib import Path

BASIS = "https://provinglab.dev"
DOCS = Path(__file__).resolve().parent / "docs"
TITEL = "Proving Lab"
UNTERTITEL = "Measurements on browser tools, OCR pipelines and AI-assisted development"


def feld(muster, text, default=""):
    m = re.search(muster, text, re.S)
    return m.group(1).strip() if m else default


def beitraege():
    """Sammelt alle Seiten, die sich selbst als Artikel oder Datensatz ausweisen."""
    out = []
    for datei in sorted(glob.glob(str(DOCS / "**" / "index.html"), recursive=True)):
        s = Path(datei).read_text(encoding="utf-8")
        if '"TechArticle"' not in s and '"Dataset"' not in s:
            continue
        pfad = str(Path(datei).relative_to(DOCS).parent).replace("\\", "/")
        if pfad == ".":
            continue  # Startseite ist kein Beitrag
        titel = feld(r"<title>(.*?)</title>", s)
        # Der Seitentitel traegt oft einen Namenszusatz — im Feed stoert der.
        titel = re.sub(r"\s*[—|]\s*Proving Lab\s*$", "", titel)
        out.append({
            "url": f"{BASIS}/{pfad}/",
            "titel": titel,
            "text": feld(r'<meta name="description" content="(.*?)"', s),
            "pub": feld(r'"datePublished"\s*:\s*"([\d-]+)"', s),
            "mod": feld(r'"dateModified"\s*:\s*"([\d-]+)"', s) or feld(r'"datePublished"\s*:\s*"([\d-]+)"', s),
        })
    # neueste zuerst; bei gleichem Datum stabil nach Titel
    out.sort(key=lambda b: (b["mod"], b["titel"]), reverse=True)
    return out


def bauen(liste):
    aktuell = max((b["mod"] for b in liste), default="1970-01-01")
    teile = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom" xml:lang="en">',
        f"  <title>{html.escape(TITEL)}</title>",
        f"  <subtitle>{html.escape(UNTERTITEL)}</subtitle>",
        f"  <id>{BASIS}/</id>",
        f'  <link rel="alternate" type="text/html" href="{BASIS}/"/>',
        f'  <link rel="self" type="application/atom+xml" href="{BASIS}/feed.xml"/>',
        f"  <updated>{aktuell}T00:00:00Z</updated>",
        f"  <author><name>{html.escape(TITEL)}</name><uri>{BASIS}/</uri></author>",
        f"  <icon>{BASIS}/icon-128.png</icon>",
        f"  <rights>Content licensed for reading and quoting with attribution.</rights>",
    ]
    for b in liste:
        teile += [
            "  <entry>",
            f"    <title>{html.escape(b['titel'])}</title>",
            f"    <id>{b['url']}</id>",
            f'    <link rel="alternate" type="text/html" href="{b["url"]}"/>',
            f"    <published>{b['pub']}T00:00:00Z</published>",
            f"    <updated>{b['mod']}T00:00:00Z</updated>",
            f'    <summary type="text">{html.escape(b["text"])}</summary>',
            "  </entry>",
        ]
    teile.append("</feed>")
    return "\n".join(teile) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true", help="nur pruefen, nichts schreiben")
    a = p.parse_args()

    liste = beitraege()
    if not liste:
        sys.exit("Keine Beitraege gefunden — stimmt der Pfad zu docs/?")
    neu = bauen(liste)
    ziel = DOCS / "feed.xml"
    alt = ziel.read_text(encoding="utf-8") if ziel.exists() else ""

    for b in liste:
        print(f"  {b['mod']}  {b['titel'][:66]}")
    print(f"  {len(liste)} Beitraege")

    if alt == neu:
        print("  feed.xml ist aktuell.")
        return 0
    if a.check:
        print("  feed.xml weicht ab.")
        return 1
    ziel.write_text(neu, encoding="utf-8")
    print(f"  feed.xml geschrieben ({len(neu)} Zeichen)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
