#!/usr/bin/env python3
"""Macht eine bestehende Seite neunsprachig — ein Renderer fuer alle Seiten.

Bisher trug jede uebersetzte Seite ihren eigenen Builder: rund 200 Zeilen, in
denen dasselbe stand (Kopf abtrennen, hreflang setzen, Bloecke bauen, Fuss
wieder anhaengen) und nur die Textfragmente wechselten. Bei dreissig offenen
Seiten waeren das sechstausend Zeilen Wiederholung.

Hier steht das Verfahren einmal. Je Seite bleibt nur noch ein Textmodul:

    URL      = "https://provinglab.dev/notes/beispiel/"
    ZIEL     = "notes/beispiel/index.html"      # relativ zu docs/
    SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
    BASIS    = "en"
    INHALT   = {"en": "<header>…</header><h2>…", "de": "…", …}

INHALT traegt je Sprache den FERTIGEN Rumpf der Seite — genau das, was zwischen
`<div class="wrap">` und dem schliessenden `</div>` steht. Warum ganze
HTML-Bloecke statt einzelner Fragmente: Die Seiten sind baulich verschieden
(Tabellen, Listen, Kaesten), ein gemeinsames Fragmentschema gaebe es nicht ohne
Zwang. Und wer uebersetzt, sieht den Satz in seiner Umgebung.

WICHTIG: Ausgangstext ist die AUSGELIEFERTE Seite, nie ein alter Builder —
vierzehn von vierzehn `build-*.py` weichen von ihrer Seite ab, vier loeschen
Text. Siehe tools/builder-drift.py.

    python3 tools/seite-neunsprachig.py texte_beispiel.py
    python3 tools/seite-neunsprachig.py texte_beispiel.py --pruefen   # nichts schreiben
"""
import importlib.util
import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DOCS = WURZEL / "docs"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)


def modul_laden(pfad: Path):
    spec = importlib.util.spec_from_file_location(pfad.stem, pfad)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    for feld in ("URL", "ZIEL", "SPRACHEN", "BASIS", "INHALT"):
        if not hasattr(m, feld):
            raise SystemExit(f"{pfad.name}: Feld {feld} fehlt")
    return m


def kopf_anpassen(kopf: str, T) -> str:
    """hreflang und inLanguage auf neun Sprachen setzen.

    Die alten hreflang-Zeilen werden entfernt, nicht ergaenzt: sonst sammeln
    sich bei jedem Lauf Dubletten an, und Suchmaschinen sehen widerspruechliche
    Angaben.
    """
    k = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", kopf)
    verweise = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{T.URL}">' for l in T.SPRACHEN
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{T.URL}">'
    k = re.sub(r'(<link rel="canonical" href="[^"]*">)',
               lambda m: m.group(1) + "\n" + verweise, k, count=1)
    k = re.sub(r'"inLanguage":\s*(?:"[^"]*"|\[[^\]]*\])',
               lambda _: '"inLanguage": ' + json.dumps(T.SPRACHEN), k, count=1)
    return k


def bauen(T, schreiben=True):
    ziel = DOCS / T.ZIEL
    if not ziel.exists():
        raise SystemExit(f"Seite fehlt: {ziel}")
    s = ziel.read_text(encoding="utf-8")

    marke = '<div class="wrap">'
    if marke not in s:
        raise SystemExit(f"{T.ZIEL}: kein <div class=\"wrap\"> gefunden")
    kopf = s[: s.index(marke) + len(marke)]
    # Von HINTEN suchen: der Rumpf enthaelt selbst schliessende divs.
    if "</div>\n</body>" not in s:
        raise SystemExit(f"{T.ZIEL}: Fussmarke </div></body> nicht gefunden")
    ende = s[s.rindex("</div>\n</body>"):]

    kopf = kopf_anpassen(kopf, T)
    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.INHALT or not T.INHALT[l].strip()]
    if fehlt:
        # Kein stiller Teilbau: eine Seite mit Picker, hinter dem nichts steht,
        # ist schlimmer als eine ehrlich einsprachige.
        raise SystemExit(f"{T.ZIEL}: ohne Fassung fuer {', '.join(fehlt)} — "
                         "nicht gebaut")

    bloecke = []
    for l in T.SPRACHEN:
        an = ' class="on"' if l == T.BASIS else ""
        bloecke.append(f'<div data-lang="{l}"{an} lang="{l}">\n'
                       + T.INHALT[l].strip() + "\n</div>")
    neu = kopf + "\n" + "\n\n".join(bloecke) + "\n" + ende

    def worte(h):
        h = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", h)
        return len(re.sub(r"<[^>]+>", " ", h).split())

    if schreiben:
        ziel.write_text(neu, encoding="utf-8")
    return {"ziel": str(T.ZIEL), "sprachen": len(T.SPRACHEN),
            "worte_vorher": worte(s), "worte_nachher": worte(neu),
            "geschrieben": schreiben}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__)
        return 1
    pfad = Path(args[0])
    if not pfad.exists():
        pfad = WURZEL / args[0]
    T = modul_laden(pfad)
    d = bauen(T, schreiben="--pruefen" not in sys.argv)
    print(f"{d['ziel']}: {d['sprachen']} Sprachen, "
          f"{d['worte_vorher']} -> {d['worte_nachher']} Woerter"
          + ("" if d["geschrieben"] else "   (nur geprueft, nichts geschrieben)"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
