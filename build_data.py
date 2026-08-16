#!/usr/bin/env python3
"""Baut docs/data/index.html aus texte_data.py — neun Sprachen.

Gleiches Muster wie build-indexseiten.py: alle Sprachen in derselben Datei als
data-lang-Bloecke, sichtbar ist genau eine (docs/site-lang.js). Kopf und Fuss
kommen aus der bestehenden Seite, damit Navigation, Stil und die Metadaten von
build-meta-nachschlag.py (keywords, Open Graph, JSON-LD) unangetastet bleiben.
Eintraege und Textaenderungen gehoeren in texte_data.py — die gebaute Seite
nicht von Hand editieren. Der Lauf ist idempotent: ein zweiter Lauf aendert
nichts.

    python3 build_data.py
"""
from pathlib import Path

import texte_data as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "data" / "index.html"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)


def eintraege(liste):
    aus = []
    for e in liste:
        teile = ['<div class="item">']
        teile.append(f'  <h2><a href="{e["href"]}">{e["title"]}</a></h2>')
        teile.append(f'  <p>{e["text"]}</p>')
        if e.get("figures"):
            spannen = "".join(f"<span>{f}</span>" for f in e["figures"])
            teile.append(f'  <div class="figures">{spannen}</div>')
        teile.append("</div>")
        aus.append("\n".join(teile))
    return "\n\n".join(aus)


def block(l):
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <h1>{d["h1"]}</h1>
  <p class="lead">{d["lead"]}</p>
</header>

{eintraege(d["items"])}

<footer>{d["foot"]}</footer>
</div>'''


def main():
    s = ZIEL.read_text(encoding="utf-8")

    # Kopf bis einschliesslich <div class="wrap">, Fuss ab dem wrap-Ende.
    kopf = s[: s.index('<div class="wrap">') + len('<div class="wrap">')]
    fuss = s[s.rindex("</div>\n</body>") :]

    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE]
    if fehlt:
        print(f"WARNUNG: ohne Fassung fuer {', '.join(fehlt)} — Seite unvollstaendig")
    bloecke = "\n\n".join(block(l) for l in T.SPRACHEN if l in T.TEXTE)
    ZIEL.write_text(kopf + "\n" + bloecke + "\n" + fuss, encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)} ({len(T.TEXTE)} Fassungen)")


if __name__ == "__main__":
    main()
