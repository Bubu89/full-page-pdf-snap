#!/usr/bin/env python3
"""Erntet Titel und Kurzbeschreibung je Sprache aus den fertigen Seiten.

Warum ernten statt schreiben: Auf einer neunsprachigen Seite steht die
Überschrift bereits in neun Sprachen, und der Vorspann darunter ist genau das,
was eine Suchmaschine als Beschreibung zeigen würde. Sie noch einmal von Hand
zu verfassen hiesse, neun Übersetzungen zu erzeugen, die von den vorhandenen
abweichen können — und irgendwann abweichen werden.

Was hier NICHT behauptet wird: dass damit die Suchmaschinen-Auffindbarkeit je
Sprache erledigt sei. Ein Dokument hat genau einen <title>. Solange alle neun
Sprachen unter DERSELBEN Adresse liegen, kann es keine sprachspezifischen
Metaangaben geben — und die hreflang-Angaben, die neunmal auf dieselbe Adresse
zeigen, sind für Suchmaschinen wertlos. Diese Karte ist die Vorarbeit: Sie
liefert die Texte, die eine Auslieferung unter eigenen Adressen braucht.

    python3 tools/sprachmeta.py            # Karte schreiben
    python3 tools/sprachmeta.py --zeigen   # nur anzeigen
"""
import json
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DOCS = WURZEL / "docs"
ZIEL = DOCS / "data" / "sprachen-meta.json"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]

# Beschreibungen über ~160 Zeichen schneidet Google ab. Am Wortende kürzen,
# nicht mitten im Wort — ein abgehackter Teaser sieht nach Fehler aus.
BESCHREIBUNG_MAX = 160


def _text(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def _kuerzen(s: str, n: int = BESCHREIBUNG_MAX) -> str:
    if len(s) <= n:
        return s
    return s[:n].rsplit(" ", 1)[0].rstrip(" ,;:–—") + " …"


def bloecke(html: str) -> dict:
    """{sprache: block_html} — nur die obersten data-lang-Bloecke."""
    raus = {}
    for m in re.finditer(r'<div[^>]*data-lang="([^"]+)"[^>]*>', html):
        spr = m.group(1)
        start = m.end()
        naechster = html.find('<div data-lang="', start)
        ende = naechster if naechster > 0 else html.rfind("</div>\n</body>")
        raus[spr] = html[start:ende]
    return raus


def titel_ausserhalb(html: str, spr: str) -> str:
    """Manche Seiten haengen data-lang an die <h1> selbst statt an den Block.

    /how-to/for-students/ und /how-to/firefox-and-chrome/ tragen neun
    <h1 data-lang="…"> als Geschwister VOR den Bloecken. Wer nur in den
    Bloecken sucht, findet dort keinen Titel und ueberspringt die Seite
    stillschweigend — beide fehlten in der ersten Fassung dieser Karte.
    """
    m = re.search(r'<h1[^>]*data-lang="' + re.escape(spr) + r'"[^>]*>(.*?)</h1>',
                  html, re.S)
    return _text(m.group(1)) if m else ""


def aus_block(block: str, html: str = "", spr: str = "") -> dict:
    """Titel aus <h1>, Beschreibung aus dem Vorspann darunter."""
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", block, re.S)
    titel = _text(h1.group(1)) if h1 else ""
    if not titel and html and spr:
        titel = titel_ausserhalb(html, spr)
    besch = ""
    vor = re.search(r'<p[^>]*class="[^"]*standfirst[^"]*"[^>]*>(.*?)</p>', block, re.S)
    if vor:
        besch = _text(vor.group(1))
    else:
        # Kein Vorspann: erster echter Absatz. Brotkrumen und Metazeilen sind
        # keine Beschreibung.
        for p in re.finditer(r"<p([^>]*)>(.*?)</p>", block, re.S):
            if re.search(r'class="[^"]*\b(crumb|meta|meta-line)\b', p.group(1)):
                continue
            t = _text(p.group(2))
            if len(t) >= 40:
                besch = t
                break
    return {"title": titel, "description": _kuerzen(besch)}


def sammeln() -> dict:
    karte = {}
    for datei in sorted(DOCS.rglob("*.html")):
        html = datei.read_text(encoding="utf-8", errors="replace")
        b = bloecke(html)
        if len(b) < 2:
            continue                      # ein- oder zweisprachig: nichts zu ernten
        rel = datei.relative_to(DOCS)
        pfad = "/" if str(rel) == "index.html" else (
            "/" + str(rel.parent).replace("\\", "/") + "/" if rel.name == "index.html"
            else "/" + str(rel).replace("\\", "/"))
        eintrag = {}
        for spr, block in b.items():
            d = aus_block(block, html, spr)
            if d["title"]:
                eintrag[spr] = d
        if eintrag:
            karte[pfad] = eintrag
    return karte


def main():
    karte = sammeln()
    luecken = []
    for pfad, e in karte.items():
        fehlt = [s for s in SPRACHEN if s not in e]
        ohne = [s for s, d in e.items() if not d["description"]]
        if fehlt:
            luecken.append(f"{pfad}: ohne Titel in {', '.join(fehlt)}")
        if ohne:
            luecken.append(f"{pfad}: ohne Beschreibung in {', '.join(sorted(ohne))}")

    print(f"Seiten mit Sprachbloecken: {len(karte)}")
    for pfad in sorted(karte):
        e = karte[pfad]
        print(f"  {pfad:<46} {len(e)} Sprachen")
    if luecken:
        print("\nLuecken:")
        for l in luecken:
            print("  ", l)

    if "--zeigen" in sys.argv:
        beispiel = next(iter(sorted(karte)), None)
        if beispiel:
            print(f"\nBeispiel {beispiel}:")
            for s in SPRACHEN:
                d = karte[beispiel].get(s)
                if d:
                    print(f"  {s:<6} {d['title'][:72]}")
        return 0

    ZIEL.parent.mkdir(parents=True, exist_ok=True)
    ZIEL.write_text(json.dumps(karte, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    print(f"\ngeschrieben: {ZIEL.relative_to(WURZEL)} "
          f"({sum(len(v) for v in karte.values())} Eintraege)")
    return 1 if luecken else 0


if __name__ == "__main__":
    sys.exit(main())
