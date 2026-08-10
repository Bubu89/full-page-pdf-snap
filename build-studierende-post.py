#!/usr/bin/env python3
"""Baut den Beitrag fuer Studierende in neun Sprachen zu einer Seite.

Alle Sprachen stehen in derselben Datei, jede in einem Block mit data-lang.
Sichtbar ist genau eine; die Wahl trifft docs/site-lang.js und gilt domainweit.

Warum eine Datei statt neun: die Adresse bleibt dieselbe, ein geteilter Link
oeffnet beim Empfaenger in *dessen* Sprache, und Suchmaschinen finden alle
Fassungen ohne hreflang-Geflecht. Der Preis ist Seitengroesse — bei diesem
Umfang rund 60 kB, was gegenueber einem Bild nichts ist.

Kopf und Fuss stammen aus einer bestehenden Seite, damit Navigation und Stil
nicht auseinanderlaufen.

    python3 build-studierende-post.py
"""
import json
import re
from pathlib import Path

import texte_artikel_studierende as T

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "citation-triage" / "index.html"
ZIEL = DOCS / "how-to" / T.SLUG

# Die Ausgangsfassung. Ihr Titel steht in den Metadaten, weil ein Dokument
# genau einen <title> hat.
BASIS = "en"


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[: s.index('<div class="wrap">')], s[s.index("<footer") :]


def kopf_anpassen(kopf):
    b = T.TEXTE[BASIS]
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{b['title']} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + b["description"] + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{T.URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{T.URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{b['title']}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + b["description"] + m.group(2), k)

    # Die Vorlage traegt einen hreflang-Verweis auf sich selbst. Hier liegen alle
    # Sprachen unter einer Adresse — also je Sprache ein Verweis auf diese, plus
    # x-default. Das ist die Form, die Google fuer sprachumschaltende Seiten nennt.
    # Erst alle geerbten Verweise entfernen, dann den vollstaendigen Satz einmal
    # setzen. Ein Aufraeum-Regex mit Lookahead frisst hier die eigenen Zeilen:
    # jede Zeile, auf die eine weitere folgt, faellt weg — uebrig bleibt die letzte.
    k = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", k)
    verweise = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{T.URL}">' for l in T.SPRACHEN
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{T.URL}">'
    k = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + "\n" + verweise, k, count=1)

    ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": b["title"], "description": b["description"],
        "datePublished": T.DATUM, "dateModified": T.DATUM,
        "inLanguage": T.SPRACHEN, "url": T.URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)

    # Die Vorlage ist eine Messung, dieser Beitrag eine Anleitung.
    k = k.replace('href="../../measurements/" aria-current="page"', 'href="../../measurements/"')
    k = k.replace('href="../../how-to/save-a-webpage-as-pdf/"',
                  'href="../../how-to/save-a-webpage-as-pdf/" aria-current="page"')
    return k


def kopfzeile():
    """Titel, Vorspann und Zeile mit Datum — je Sprache ein Block."""
    teile = ["<header>"]
    for l in T.SPRACHEN:
        d = T.TEXTE[l]
        an = " on" if l == BASIS else ""
        teile.append(f'  <h1 data-lang="{l}"{" class=\"on\"" if l == BASIS else ""} lang="{l}">{d["h1"]}</h1>')
        teile.append(f'  <p class="standfirst{an}" data-lang="{l}" lang="{l}">{d["standfirst"]}</p>')
    teile.append('  <p class="meta">')
    for l in T.SPRACHEN:
        an = " on" if l == BASIS else ""
        teile.append(f'    <span data-lang="{l}" class="{an.strip()}" lang="{l}">{T.TEXTE[l]["meta"]}</span>')
    teile.append("  </p>")
    teile.append("</header>\n")
    return "\n".join(teile)


def koerper():
    teile = []
    for l in T.SPRACHEN:
        an = ' class="on"' if l == BASIS else ""
        teile.append(f'<div data-lang="{l}"{an} lang="{l}">\n{T.TEXTE[l]["body"]}\n</div>\n')
    return "\n".join(teile)


FUSS = """<footer>
      Published 10 August 2026. Every figure carries the date it was taken and links
      to its raw data under <a href="/data/">/data/</a>, CC BY 4.0.
      <br><br>
      <a href="../../">← Proving Lab</a> · <a href="../../disclaimer/">Disclaimer</a>
    </footer>"""


def main():
    kopf, fuss = kopf_und_fuss()
    kopf = kopf_anpassen(kopf)
    fuss = re.sub(r"<footer>.*?</footer>", lambda _: FUSS, fuss, count=1, flags=re.S)

    seite = kopf + '<div class="wrap">\n\n' + kopfzeile() + koerper() + "\n" + fuss

    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(seite, encoding="utf-8")
    print(f"geschrieben: {(ZIEL / 'index.html').relative_to(HIER)} "
          f"({len(seite):,} Zeichen, {len(T.SPRACHEN)} Sprachen)")


if __name__ == "__main__":
    main()
