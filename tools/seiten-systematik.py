#!/usr/bin/env python3
"""Findet Seiten, die veröffentlicht sind, aber nirgends stehen.

Der Anlass (16.08.2026): Auf der Startseite standen unter der Überschrift
„Notizen" vier Beiträge — zwei davon Anleitungen, einer eine Messung. Wer sie
dort sah und später unter /notes/ suchte, fand sie nicht. Und /how-to/, wo die
beiden Anleitungen liegen, antwortete mit 404: drei Artikel ohne
Verzeichnisseite, erreichbar nur über die Startseite.

Drei Prüfungen:

1. **Verzeichnis vorhanden.** Jede Rubrik mit Artikeln braucht eine
   Übersichtsseite. Ohne sie ist ein Artikel nur so lange auffindbar, wie er
   auf der Startseite steht.
2. **Verzeichnis vollständig.** Jeder Artikel muss im Verzeichnis seiner
   eigenen Rubrik verlinkt sein.
3. **Überschrift hält, was sie sagt.** Ein Startseiten-Abschnitt „Notizen"
   verlinkt Notizen. Mischt er Rubriken, ist entweder die Überschrift falsch
   oder die Auswahl.

    python3 tools/seiten-systematik.py
"""
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DOCS = WURZEL / "docs"

# Rubrik -> Überschrift, unter der die Startseite sie führt.
RUBRIKEN = {
    "notes": ("Notizen", "Notes"),
    "measurements": ("Messungen", "Measurements"),
    "how-to": ("Anleitung", "How to"),
    "tools": ("Werkzeuge", "Tools"),
}


def deutscher_block(html: str) -> str:
    m = re.search(r'<div[^>]*data-lang="de"[^>]*>([\s\S]*?)(?=<div[^>]*data-lang=|\Z)',
                  html)
    return m.group(1) if m else html


def artikel() -> dict:
    """{rubrik: [pfad]} — alle veroeffentlichten Artikelseiten."""
    raus = {}
    for p in sorted(DOCS.rglob("index.html")):
        teile = str(p.relative_to(DOCS).parent).replace("\\", "/").split("/")
        if len(teile) == 2 and teile[0] in RUBRIKEN:
            raus.setdefault(teile[0], []).append("/" + "/".join(teile) + "/")
    return raus


def verlinkt(index: Path) -> set:
    h = index.read_text(encoding="utf-8", errors="replace")
    return set(re.findall(r'href="([^"#?]+)"', deutscher_block(h)))


def _endet_auf(links: set, pfad: str) -> bool:
    name = pfad.rstrip("/").split("/")[-1]
    return any(pfad in l or l.rstrip("/").split("/")[-1] == name for l in links)


def abschnitte_der_startseite() -> list:
    """[(ueberschrift, [verlinkte pfade])] aus dem deutschen Block."""
    h = (DOCS / "index.html").read_text(encoding="utf-8", errors="replace")
    de = deutscher_block(h)
    stellen = [(m.start(), re.sub(r"<[^>]+>", "", m.group(1)).strip())
               for m in re.finditer(r"<h2[^>]*>([\s\S]*?)</h2>", de)]
    raus = []
    for i, (pos, titel) in enumerate(stellen):
        ende = stellen[i + 1][0] if i + 1 < len(stellen) else len(de)
        raus.append((titel, re.findall(r'href="([^"#?]+)"', de[pos:ende])))
    return raus


def main():
    fehler = []
    hinweise = []
    a = artikel()

    print("1. Verzeichnis je Rubrik")
    for rubrik, seiten in sorted(a.items()):
        index = DOCS / rubrik / "index.html"
        if not index.exists():
            fehler.append(f"/{rubrik}/ hat kein Verzeichnis — "
                          f"{len(seiten)} Artikel nur ueber die Startseite erreichbar")
            print(f"  FEHLT  /{rubrik}/   ({len(seiten)} Artikel)")
            for s in seiten:
                print(f"           {s}")
        else:
            print(f"  ok     /{rubrik}/")

    print("\n2. Vollstaendigkeit der Verzeichnisse")
    for rubrik, seiten in sorted(a.items()):
        index = DOCS / rubrik / "index.html"
        if not index.exists():
            continue
        l = verlinkt(index)
        fehlend = [s for s in seiten if not _endet_auf(l, s)]
        if fehlend:
            for s in fehlend:
                fehler.append(f"{s} fehlt im Verzeichnis /{rubrik}/")
            print(f"  FEHL   /{rubrik}/   {len(fehlend)} von {len(seiten)} nicht verlinkt")
        else:
            print(f"  ok     /{rubrik}/   {len(seiten)} von {len(seiten)}")

    print("\n3. Halten die Startseiten-Ueberschriften, was sie sagen?")
    zu_rubrik = {}
    for rubrik, (de_titel, en_titel) in RUBRIKEN.items():
        zu_rubrik[de_titel.lower()] = rubrik
        zu_rubrik[en_titel.lower()] = rubrik
    for titel, links in abschnitte_der_startseite():
        rubrik = zu_rubrik.get(titel.strip().lower())
        if not rubrik:
            continue
        artikel_links = [l for l in links
                         if re.match(r"^(?:\.\./)?[a-z-]+/[a-z0-9-]+/$", l)]
        fremd = [l for l in artikel_links if not l.lstrip("./").startswith(rubrik + "/")]
        if fremd:
            hinweise.append(
                f'Abschnitt "{titel}" verlinkt {len(fremd)} von '
                f"{len(artikel_links)} Beitraegen aus anderen Rubriken: "
                + ", ".join(fremd))
            print(f'  MISCHT "{titel}": {len(fremd)} von {len(artikel_links)} fremd')
            for l in fremd:
                print(f"           {l}")
        else:
            print(f'  ok     "{titel}"')

    print("\n" + "=" * 66)
    for f in fehler:
        print("  FEHLER   " + f)
    for h in hinweise:
        print("  HINWEIS  " + h)
    if not fehler and not hinweise:
        print("  Jede Seite steht dort, wo man sie sucht.")
    print("=" * 66)
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
