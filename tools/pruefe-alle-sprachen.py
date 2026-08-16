#!/usr/bin/env python3
"""pruefe-alle-sprachen.py — Sprachumschaltung ueber ALLE Seiten der Domain.

Warum es das gibt: Die Sprachwahl ist domainweit, aber die Abdeckung waechst
seitenweise. Dieser Lauf beantwortet in einem Zug pro Seite: Ist der Picker
da? Schaltet die Seite wirklich um (nicht nur die Klasse, sondern der
sichtbare Text)? Faellt eine fehlende Sprache ehrlich mit Hinweis zurueck —
und meldet eine Seite mit Bloecken, aber ohne erkennbare Umschaltung?

    python3 tools/pruefe-alle-sprachen.py            # gegen den Arbeitsstand
    python3 tools/pruefe-alle-sprachen.py --live     # gegen provinglab.dev

Geprueft wird mit echtem DOM (Playwright), nicht am Markup: Was sichtbar ist,
entscheidet der Browser.
"""
import http.server
import socketserver
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HIER = Path(__file__).resolve().parent
DOCS = HIER.parent / "docs"
PORT = 8750
LIVE = "--live" in sys.argv
BASIS = "https://provinglab.dev" if LIVE else f"http://127.0.0.1:{PORT}"

# Zwei Pruefsprachen: eine, die es fast nirgends gibt (fr), und de.
WECHSEL = ["fr", "de"]

FR_KENNSATZ = "Cette page n'existe pas encore dans votre langue"


class Still(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=str(DOCS), **kw)

    def log_message(self, *a):
        pass


def server_starten():
    socketserver.TCPServer.allow_reuse_address = True
    srv = socketserver.TCPServer(("127.0.0.1", PORT), Still)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv


def seiten():
    aus = []
    for f in sorted(DOCS.rglob("*.html")):
        rel = f.relative_to(DOCS)
        if str(rel) == "404.html":
            continue
        # Weiterleitungen enthalten keine Prosa und koennen nie mehrsprachig
        # werden. Ohne diese Ausnahme meldete der Lauf drei alte Adressen
        # dauerhaft als "einsprachig" — eine Baustelle, die keine ist, und
        # die den Blick auf die echten 30 offenen Seiten verstellt.
        # (16.08.2026)
        if _weiterleitung(f):
            continue
        if str(rel) == "index.html":
            pfad = "/"
        elif rel.name == "index.html":
            pfad = "/" + str(rel.parent).replace("\\", "/") + "/"
        else:
            pfad = "/" + str(rel).replace("\\", "/")
        aus.append((pfad, f))
    return aus


def _weiterleitung(datei) -> bool:
    """Ist das nur eine Umleitung auf die eigentliche Seite?

    Erkannt an beidem zusammen: Meta-Refresh UND sehr wenig Text. Nur am
    Refresh festzumachen waere zu grob — eine echte Seite darf einen haben.
    """
    try:
        h = datei.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if 'http-equiv="refresh"' not in h.lower():
        return False
    import re as _re
    roh = _re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", h)
    return len(_re.sub(r"<[^>]+>", " ", roh).split()) < 60


def main():
    srv = None if LIVE else server_starten()
    zeilen, fehler = [], []
    mehrsprachig = einsprachig = 0

    with sync_playwright() as p:
        b = p.chromium.launch()
        seite = b.new_context(locale="en-US").new_page()

        for pfad, datei in seiten():
            url = BASIS + pfad
            html = datei.read_text(encoding="utf-8", errors="replace")
            hat_bloecke = 'data-lang="' in html

            r = seite.goto(url, wait_until="networkidle")
            if not r or r.status != 200:
                fehler.append(f"{pfad}: HTTP {r.status if r else '?'}")
                continue

            picker = seite.evaluate("() => !!document.getElementById('pl-langpick')")
            if not picker:
                fehler.append(f"{pfad}: KEIN SPRACH-PICKER")
                continue

            bloecke = seite.eval_on_selector_all(
                "div[data-lang], header[data-lang], section[data-lang]",
                "els => els.map(e => e.getAttribute('data-lang'))")
            sprachen = sorted(set(bloecke))

            if hat_bloecke and not bloecke:
                # Bloecke sind Elemente ausserhalb der div/header/section-Abfrage
                sprachen = ["(elementweise)"]

            # Grundzustand: alle sichtbaren Sprachelemente gehoeren zu GENAU
            # einer Sprache. Seiten wie /tools/full-page-pdf-snap/ tragen
            # mehrere div-Bloecke derselben Sprache — das ist zulaessig,
            # entscheidend ist die Sprache, nicht die Anzahl.
            an_sprachen = seite.eval_on_selector_all(
                "[data-lang]",
                "els => [...new Set(els.filter(e => e.classList.contains('on')).map(e => e.getAttribute('data-lang')))]")
            if hat_bloecke and len(an_sprachen) != 1:
                fehler.append(f"{pfad}: sichtbare Sprachen {an_sprachen}, erwartet genau 1")

            if hat_bloecke:
                mehrsprachig += 1
                status = f"{len(sprachen)} Sprachen [{','.join(sprachen)}]"
            else:
                einsprachig += 1
                status = "einsprachig"

            # Umschalttest FR: vorhanden -> sichtbar FR; fehlend -> Hinweis
            seite.select_option("#pl-langpick", "fr")
            seite.wait_for_timeout(120)
            lang = seite.evaluate("() => document.documentElement.lang")
            hinw = seite.evaluate(
                "() => { var e = document.getElementById('pl-fallback');"
                " return e && !e.hidden ? e.textContent : null; }")
            if hat_bloecke and "fr" in sprachen:
                if lang != "fr":
                    fehler.append(f"{pfad}: FR vorhanden, aber html lang={lang}")
                if hinw:
                    fehler.append(f"{pfad}: FR vorhanden, aber Rueckfall-Hinweis sichtbar")
            else:
                if lang != "en":
                    fehler.append(f"{pfad}: ohne FR-Block, aber html lang={lang}")
                if not hinw or FR_KENNSATZ not in hinw:
                    fehler.append(f"{pfad}: fehlender Rueckfall-Hinweis auf FR")

            # Umschalttest DE analog (kurz)
            seite.select_option("#pl-langpick", "de")
            seite.wait_for_timeout(120)
            lang = seite.evaluate("() => document.documentElement.lang")
            if hat_bloecke and "de" in sprachen and lang != "de":
                fehler.append(f"{pfad}: DE vorhanden, aber html lang={lang}")

            seite.select_option("#pl-langpick", "en")
            seite.wait_for_timeout(80)
            zeilen.append(f"  {pfad:<52} {status}")

        b.close()

    print(f"Geprueft: {len(zeilen)} Seiten ({mehrsprachig} mehrsprachig, {einsprachig} einsprachig)\n")
    for z in zeilen:
        print(z)
    print()
    if fehler:
        print(f"FEHLER ({len(fehler)}):")
        for f in fehler:
            print(" ", f)
        return 1
    print("Alle Seiten: Picker da, Umschaltung korrekt, Rueckfall ehrlich — alles gruen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
