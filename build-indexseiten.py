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
        # Absatz-Eintrag ohne Ueberschrift ("Zusammen.", "Offenlegung.") —
        # label fett voran, optional ein zweiter Absatz mit Abstand.
        if e.get("para"):
            teile.append(f'  <p><strong>{e["label"]}</strong> {e["text"]}</p>')
            if e.get("extra"):
                teile.append(f'  <p style="margin-top:10px">{e["extra"]}</p>')
            teile.append("</div>")
            aus.append("\n".join(teile))
            continue
        if e.get("date"):
            teile.append(f'  <p class="date">{e["date"]}</p>')
        teile.append(f'  <h2><a href="{e["href"]}">{e["title"]}</a></h2>')
        teile.append(f'  <p>{e["text"]}</p>')
        if e.get("figures"):
            spannen = "".join(f"<span>{f}</span>" for f in e["figures"])
            teile.append(f'  <div class="figures">{spannen}</div>')
        if e.get("links"):
            zeilen = []
            for v in e["links"]:
                kl = f' class="{v["class"]}"' if v.get("class") else ""
                zeilen.append(f'    <a{kl} href="{v["href"]}">{v["text"]}</a>')
            teile.append('  <div class="holen">\n' + "\n".join(zeilen) + "\n  </div>")
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


# Anleitungen gehoeren auch in die Notizenliste.
#
# Warum: Wer den neuesten Beitrag sucht, sieht auf /notes/ nach — die Startseite
# fuehrt dort selbst Anleitungen unter der Ueberschrift "Notizen". Stand die
# Anleitung vom 15. August nur unter /how-to/, war der neueste Eintrag auf
# /notes/ der 7. August, und der Beitrag praktisch unauffindbar. Dreimal
# nachgefragt worden, dreimal von mir erklaert statt behoben. (16.08.2026)
#
# Zusammengefuehrt wird HIER, nicht in texte_indexseiten.py: so wandert jeder
# neue Beitrag automatisch mit, ohne dass ihn jemand an zwei Stellen pflegt.
MISCHEN = {"notes": ["how-to"]}

_MONATE = {m: i for i, m in enumerate(
    ["januar", "februar", "maerz", "märz", "april", "mai", "juni", "juli",
     "august", "september", "oktober", "november", "dezember"], 1)}
_MONATE.update({m: i for i, m in enumerate(
    ["january", "february", "march", "april", "may", "june", "july", "august",
     "september", "october", "november", "december"], 1)})


def _sortschluessel(datum: str):
    """Aus '15 August 2026' bzw. '15. August 2026' ein vergleichbares Tupel.

    Sortiert wird ueber die ENGLISCHE Liste; die anderen Sprachen uebernehmen
    deren Reihenfolge ueber den href. Neun Datumsformate zu parsen waere neun
    Gelegenheiten, eine Reihenfolge falsch zu bekommen.
    """
    import re as _re
    m = _re.match(r"(\d{1,2})\.?\s+([A-Za-zäöüÄÖÜ]+)\s+(\d{4})", datum.strip())
    if not m:
        return (0, 0, 0)
    tag, monat, jahr = int(m.group(1)), _MONATE.get(m.group(2).lower(), 0), int(m.group(3))
    return (jahr, monat, tag)


def zusammenfuehren(seite):
    """Fremde Rubriken in die Liste dieser Seite mischen, nach Datum."""
    quellen = MISCHEN.get(seite)
    if not quellen:
        return
    basis = T.BASIS
    # Reihenfolge einmal an der Basissprache bestimmen.
    reihenfolge = []
    for eintrag in T.TEXTE[seite][basis]["items"]:
        reihenfolge.append((_sortschluessel(eintrag["date"]), eintrag["href"]))
    for rubrik in quellen:
        if rubrik not in T.TEXTE:
            continue
        for eintrag in T.TEXTE[rubrik][basis]["items"]:
            reihenfolge.append((_sortschluessel(eintrag["date"]),
                                f"../{rubrik}/" + eintrag["href"]))
    reihenfolge.sort(key=lambda x: x[0], reverse=True)
    folge = [h for _, h in reihenfolge]

    for spr in T.SPRACHEN:
        if spr not in T.TEXTE[seite]:
            continue
        nach_href = {e["href"]: e for e in T.TEXTE[seite][spr]["items"]}
        for rubrik in quellen:
            if spr not in T.TEXTE.get(rubrik, {}):
                continue
            for e in T.TEXTE[rubrik][spr]["items"]:
                kopie = dict(e)
                kopie["href"] = f"../{rubrik}/" + e["href"]
                nach_href[kopie["href"]] = kopie
        T.TEXTE[seite][spr]["items"] = [nach_href[h] for h in folge if h in nach_href]


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
            zusammenfuehren(seite)
            bauen(seite)


if __name__ == "__main__":
    main()
