#!/usr/bin/env python3
"""Baut die Index-Seiten (measurements/, notes/, tools/) aus texte_indexseiten.py.

Gleiches Muster wie build-startseite.py: alle Sprachen in derselben Datei als
data-lang-Bloecke, sichtbar ist genau eine (docs/site-lang.js). Kopf und Fuss
kommen aus der bestehenden Seite. Wer einen Eintrag aendert, aendert ihn in
texte_indexseiten.py — die gebauten Seiten nicht von Hand.

    python3 build-indexseiten.py
"""
from pathlib import Path

import texte_indexseiten as T

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"

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
        if e.get("date"):
            teile.append(f'  <p class="date">{e["date"]}</p>')
        teile.append(f'  <h2><a href="{e["href"]}">{e["title"]}</a></h2>')
        teile.append(f'  <p>{e["text"]}</p>')
        if e.get("figures"):
            spannen = "".join(f"<span>{f}</span>" for f in e["figures"])
            teile.append(f'  <div class="figures">{spannen}</div>')
        teile.append("</div>")
        aus.append("\n".join(teile))
    return "\n".join(aus)


def block(seite, l):
    d = T.TEXTE[seite][l]
    an = ' class="on"' if l == T.BASIS else ""
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <h1>{d["h1"]}</h1>
  <p class="lead">{d["lead"]}</p>
</header>
{eintraege(d["items"])}

<footer>{d["foot"]}</footer>
</div>'''


def bauen(seite):
    ziel = DOCS / seite / "index.html"
    s = ziel.read_text(encoding="utf-8")

    # Kopf bis einschliesslich <div class="wrap">, Fuss ab dem wrap-Ende.
    kopf = s[: s.index('<div class="wrap">') + len('<div class="wrap">')]
    fuss = s[s.rindex("</div>\n</body>") :]

    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE.get(seite, {})]
    if fehlt:
        print(f"  {seite}: WARNUNG ohne {', '.join(fehlt)} — unvollstaendig")
    bloecke = "\n\n".join(block(seite, l) for l in T.SPRACHEN if l in T.TEXTE.get(seite, {}))
    ziel.write_text(kopf + "\n" + bloecke + "\n" + fuss, encoding="utf-8")
    n = len(T.TEXTE.get(seite, {}))
    print(f"  {seite}/index.html geschrieben ({n} Fassungen)")


def main():
    for seite in T.SEITEN:
        if T.TEXTE.get(seite):
            bauen(seite)


if __name__ == "__main__":
    main()
