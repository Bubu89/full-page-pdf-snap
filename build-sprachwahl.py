#!/usr/bin/env python3
"""Zieht die Sprachwahl in jede Seite ein — eine Bedienstelle, im Menue.

Vorher gab es zwei Wege: einen Menuepunkt "Deutsch", der auf einen Anker in
derselben Seite sprang, und auf zehn Seiten ein Schaltflaechenpaar mit einem
eingebetteten setLang(). Beide konnten nur Englisch und Deutsch, und jede Seite
trug ihre eigene Kopie der Logik — neun Sprachen haetten neun Kopien bedeutet.

Jetzt liegt die Logik in docs/site-lang.js, und hier wird sie eingebunden:

  1. <script src="/site-lang.js" defer> in jede Seite
  2. das eingebettete setLang() entfernen (es kann nur zwei Sprachen und
     ueberschreibt sonst die neue Funktion)
  3. das Schaltflaechenpaar entfernen
  4. das CSS fuer [data-lang] sicherstellen, wo Sprachbloecke vorkommen

Mehrfach ausfuehrbar: was schon erledigt ist, bleibt unangetastet.

    python3 build-sprachwahl.py           # schreiben
    python3 build-sprachwahl.py --check   # nur berichten, Exitcode 1 bei Rest
"""
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
CHECK = "--check" in sys.argv

EINBINDUNG = '<script src="/site-lang.js" defer></script>'
CSS = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)


def einbinden(s):
    """Nach agent-tools.js einhaengen, sonst vor </head>."""
    if EINBINDUNG in s:
        return s, False
    anker = '<script src="/agent-tools.js" defer></script>'
    if anker in s:
        return s.replace(anker, anker + "\n" + EINBINDUNG, 1), True
    if "</head>" in s:
        return s.replace("</head>", EINBINDUNG + "\n</head>", 1), True
    return s, False


def altes_script_raus(s):
    """Das eingebettete setLang() samt seinem Sofortaufruf entfernen."""
    muster = re.compile(r"<script>\s*function setLang\(l\)\{.*?</script>\s*", re.S)
    neu, n = muster.subn("", s)
    return neu, n > 0


def alte_buttons_raus(s):
    muster = re.compile(r'<div class="lang">\s*<button id="b-en".*?</div>\s*', re.S)
    neu, n = muster.subn("", s)
    return neu, n > 0


def toter_menuepunkt_raus(s):
    """Der Menuepunkt "Deutsch" sprang auf den Anker #b-de — also auf die
    Schaltflaeche, die es nicht mehr gibt. Mit abgeschaltetem JavaScript bliebe
    ein Link, der nirgends hinfuehrt. Die Sprachwahl setzt site-lang.js an seine
    Stelle."""
    muster = re.compile(r'\s*<a class="n" href="#b-de"[^>]*>.*?</a>', re.S)
    neu, n = muster.subn("", s)
    return neu, n > 0


def css_sichern(s):
    """Nur wo Sprachbloecke vorkommen und die Regel fehlt."""
    if "data-lang" not in s or "[data-lang].on" in s:
        return s, False
    m = re.search(r"<style>", s)
    if not m:
        return s, False
    i = m.end()
    return s[:i] + "\n" + CSS + s[i:], True


def main():
    seiten = sorted(DOCS.rglob("*.html"))
    offen = 0
    geaendert = 0
    for datei in seiten:
        s0 = s = datei.read_text(encoding="utf-8")
        # Reihenfolge zaehlt: erst CSS pruefen (solange data-lang noch dasteht),
        # dann die alten Bedienteile entfernen.
        s, c4 = css_sichern(s)
        s, c1 = einbinden(s)
        s, c2 = altes_script_raus(s)
        s, c3 = alte_buttons_raus(s)
        s, c5 = toter_menuepunkt_raus(s)
        if s != s0:
            if CHECK:
                offen += 1
                print(f"offen: {datei.relative_to(DOCS)}")
            else:
                datei.write_text(s, encoding="utf-8")
                geaendert += 1
                teile = [t for t, c in
                         (("script", c1), ("altes setLang", c2), ("buttons", c3),
                          ("css", c4), ("toter Menuepunkt", c5)) if c]
                print(f"  {datei.relative_to(DOCS)}: {', '.join(teile)}")

    if CHECK:
        print(f"\n{offen} von {len(seiten)} Seiten noch offen.")
        sys.exit(1 if offen else 0)
    print(f"\n{geaendert} von {len(seiten)} Seiten geaendert.")


if __name__ == "__main__":
    main()
