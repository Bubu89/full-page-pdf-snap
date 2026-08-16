#!/usr/bin/env python3
"""Baut docs/disclaimer/index.html aus texte_disclaimer.py — neun Sprachen.

Gleiches Muster wie build-for-agents.py: Kopf und Fuss aus der bestehenden
Seite, alle Sprachen als data-lang-Bloecke in einer Datei. h1, standfirst
und meta stehen MIT im Sprachblock (nicht elementweise wie zuvor), damit
pro Sprache genau ein Block sichtbar ist. Das MIT-Zitat ist Lizenztext und
bleibt ueberall englisch.

Idempotent: ein zweiter Lauf erzeugt keine Aenderung.

    python3 build_disclaimer.py
"""
import json
import re
from pathlib import Path

import texte_disclaimer as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "disclaimer" / "index.html"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)


def absaetze(items):
    aus = []
    for art, text in items:
        if art == "z":
            aus.append(f'  <p class="zitat">\n    {T.ZITAT}\n  </p>')
        else:
            aus.append(f"  <p>\n    {text}\n  </p>")
    return "\n".join(aus)


def block(l):
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    punkte = "\n\n".join(
        f'<div class="punkt">\n  <h3>{h3}</h3>\n{absaetze(items)}\n</div>'
        for h3, items in d["punkte"]
    )
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <h1>{d["h1"]}</h1>
  <p class="standfirst">
    {d["standfirst"]}
  </p>
  <p class="meta-line">{d["meta"]}</p>
</header>

<div class="wichtig">
  <p><strong>{d["kurz_stark"]}</strong> {d["kurz"]}</p>
</div>

{punkte}
</div>'''


def kopf_anpassen(kopf):
    k = kopf
    # hreflang-Satz auf diese Adresse, wie bei den anderen neunsprachigen Seiten.
    k = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", k)
    verweise = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{T.URL}">' for l in T.SPRACHEN
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{T.URL}">'
    k = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + "\n" + verweise, k, count=1)
    # Die Seite war zweisprachig beschrieben; jetzt sind es neun Fassungen.
    k = k.replace("zweisprachig", "neunsprachig")
    # ld+json: Sprachliste und Aenderungsdatum nachfuehren, Rest unveraendert.
    m = re.search(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', k, flags=re.S)
    if m:
        ld = json.loads(m.group(1))
        ld["inLanguage"] = T.SPRACHEN
        ld["dateModified"] = "2026-08-16"
        neu = ('<script type="application/ld+json">\n'
               + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>")
        k = k[: m.start()] + neu + k[m.end():]
    return k


def main():
    s = ZIEL.read_text(encoding="utf-8")
    kopf = s[: s.index('<div class="wrap">') + len('<div class="wrap">')]
    ende = s[s.index("<footer style"):]
    kopf = kopf_anpassen(kopf)
    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE]
    if fehlt:
        print(f"WARNUNG: ohne Fassung fuer {', '.join(fehlt)} — Seite unvollstaendig")
    bloecke = "\n\n".join(block(l) for l in T.SPRACHEN if l in T.TEXTE)
    ZIEL.write_text(kopf + "\n" + bloecke + "\n\n" + ende, encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)} ({len(T.TEXTE)} Fassungen)")


if __name__ == "__main__":
    main()
