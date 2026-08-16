#!/usr/bin/env python3
"""pruefe-sprachwahl.py — bedient die Sprachwahl in echtem Chrome.

Warum es das gibt: Dass neun Sprachbloecke im HTML stehen, sagt nichts darueber,
ob genau einer sichtbar ist, ob die Wahl den Seitenwechsel ueberlebt und ob eine
einsprachige Seite das auch zugibt. Das entscheidet erst der Browser.

Geprueft wird gegen einen lokalen Server, nicht gegen file:// — localStorage
haette dort den Ursprung "null", und die Persistenz waere nicht dieselbe.

    python3 pruefe-sprachwahl.py          # gegen den Arbeitsstand
    python3 pruefe-sprachwahl.py --live   # gegen provinglab.dev

Der Live-Lauf ist die eigentliche Abnahme: lokal fehlt der Cache davor, und eine
Seite, die am Ursprung richtig liegt, kann beim Leser trotzdem alt ankommen.
"""
import http.server
import socketserver
import subprocess
import sys
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
PORT = 8731

LIVE = "--live" in sys.argv
BASIS = "https://provinglab.dev" if LIVE else f"http://127.0.0.1:{PORT}"

ARTIKEL = f"{BASIS}/how-to/for-students/"
EINSPRACHIG = f"{BASIS}/recipes/"

SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]

# Ein Wort, das nur in dieser Sprachfassung vorkommt — der Beleg, dass wirklich
# umgeschaltet wurde und nicht bloss eine Klasse gesetzt ist.
PROBE = {
    "en": "The source that cites itself",
    "de": "Die Quelle, die sich selbst zitiert",
    "es": "La fuente que se cita sola",
    "fr": "La source qui se cite elle-même",
    "it": "La fonte che si cita da sola",
    "ja": "自分で出典を名乗るソース",
    "pt-BR": "A fonte que se cita sozinha",
    "ru": "Источник, который сам себя цитирует",
    "zh-CN": "自带出处的来源",
}

# Menueprobe: der "Measurements"-Eintrag in der Leiste, je Sprache. Die Leiste
# ist die Bedienstelle der Sprachwahl — bliebe sie englisch, waere die Wahl
# nur halb umgesetzt. Werte muessen zu NAV in docs/site-lang.js passen.
NAV_PROBE = {
    "en": "Measurements", "de": "Messungen", "es": "Mediciones",
    "fr": "Mesures", "it": "Misure", "ja": "測定",
    "pt-BR": "Medições", "ru": "Измерения", "zh-CN": "测量",
}


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


def sichtbarer_text(seite):
    """Was ein Leser tatsaechlich sieht — nicht, was im HTML steht."""
    return seite.evaluate("() => document.querySelector('.wrap').innerText")


def main():
    srv = None if LIVE else server_starten()
    fehler = []
    print(f"Prueft: {ARTIKEL}")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(locale="en-US")
        seite = ctx.new_page()

        # 1. Grundzustand: Englisch, genau eine Fassung sichtbar.
        seite.goto(ARTIKEL, wait_until="networkidle")
        sichtbar = seite.eval_on_selector_all(
            "div[data-lang]", "els => els.filter(e => e.classList.contains('on')).length")
        if sichtbar != 1:
            fehler.append(f"Grundzustand: {sichtbar} Textbloecke sichtbar, erwartet 1")
        text = sichtbarer_text(seite)
        if PROBE["en"] not in text:
            fehler.append("Grundzustand: englischer Text nicht sichtbar")

        # 2. Jede Sprache durchschalten und am sichtbaren Text pruefen.
        for l in SPRACHEN:
            seite.select_option("#pl-langpick", l)
            seite.wait_for_timeout(120)
            text = sichtbarer_text(seite)
            if PROBE[l] not in text:
                fehler.append(f"{l}: Kennsatz nicht im sichtbaren Text")
            # Gegenprobe: keine zweite Sprache steht gleichzeitig da.
            fremd = [x for x in SPRACHEN if x != l and PROBE[x] in text]
            if fremd:
                fehler.append(f"{l}: zusaetzlich sichtbar {fremd}")
            if seite.evaluate("() => document.documentElement.lang") != l:
                fehler.append(f"{l}: <html lang> nicht gesetzt")
            # Das Menue muss mitschalten — es ist die Bedienstelle der Wahl.
            nav = seite.eval_on_selector(
                '.topnav a.n[href$="measurements/"]', "e => e.textContent")
            if nav != NAV_PROBE[l]:
                fehler.append(f"{l}: Menue zeigt '{nav}', erwartet '{NAV_PROBE[l]}'")

        # 3. Persistenz: Wahl ueberlebt den Seitenwechsel.
        seite.select_option("#pl-langpick", "ja")
        seite.wait_for_timeout(120)
        seite.goto(EINSPRACHIG, wait_until="networkidle")
        gewaehlt = seite.evaluate("() => localStorage.getItem('pl-lang')")
        if gewaehlt != "ja":
            fehler.append(f"Persistenz: gespeichert '{gewaehlt}', erwartet 'ja'")

        # 4. Einsprachige Seite sagt, dass sie zurueckfaellt — statt stumm Englisch.
        hinweis = seite.evaluate(
            "() => { var e = document.getElementById('pl-fallback');"
            " return e && !e.hidden ? e.textContent : null; }")
        if not hinweis:
            fehler.append("Einsprachige Seite: kein Rueckfall-Hinweis")
        elif "英語" not in hinweis:
            fehler.append(f"Einsprachige Seite: Hinweis nicht auf Japanisch ({hinweis[:40]})")

        # 5. Zurueck zum Artikel: die Wahl gilt weiterhin.
        seite.goto(ARTIKEL, wait_until="networkidle")
        if PROBE["ja"] not in sichtbarer_text(seite):
            fehler.append("Rueckkehr: japanische Fassung nicht wiederhergestellt")

        # 6. Die Sprachwahl darf die Menueleiste nicht zweizeilig machen.
        #    Der erste Entwurf schrieb die vollen Sprachnamen ins zugeklappte
        #    Feld — 114 px, und die Leiste brach auf *jeder* Fensterbreite um,
        #    weil sie eine feste Hoechstbreite hat. Im HTML war davon nichts zu
        #    sehen; gefunden hat es erst ein Blick auf die Seite.
        for breite in (1180, 1440, 1920):
            mess = ctx.new_page()
            mess.set_viewport_size({"width": breite, "height": 400})
            mess.goto(ARTIKEL, wait_until="networkidle")
            mess.wait_for_timeout(150)
            hoehe = mess.eval_on_selector(".topnav .inner", "e => e.getBoundingClientRect().height")
            if hoehe > 70:
                fehler.append(f"Menueleiste bei {breite} px zweizeilig ({hoehe:.0f} px hoch)")
            mess.close()

        # 6b. Uebersetzte Menueeintraege sind laenger als das Englische —
        #     de/es/ru/fr brachen bei 1180 px auf zwei Zeilen um (15.08.2026).
        #     site-lang.js verkleinert dann Abstand und Schrift der Leiste.
        for l in ("de", "es", "ru"):
            mess = ctx.new_page()
            mess.set_viewport_size({"width": 1180, "height": 400})
            mess.goto(ARTIKEL, wait_until="networkidle")
            mess.select_option("#pl-langpick", l)
            mess.wait_for_timeout(150)
            hoehe = mess.eval_on_selector(".topnav .inner", "e => e.getBoundingClientRect().height")
            if hoehe > 70:
                fehler.append(f"Menueleiste ({l}) bei 1180 px zweizeilig ({hoehe:.0f} px hoch)")
            mess.close()

        # 7. Ohne gespeicherte Wahl entscheidet die Browsersprache.
        ctx2 = browser.new_context(locale="de-AT")
        s2 = ctx2.new_page()
        s2.goto(ARTIKEL, wait_until="networkidle")
        if PROBE["de"] not in sichtbarer_text(s2):
            fehler.append("Browsersprache de-AT ergibt nicht die deutsche Fassung")

        browser.close()

    if srv:
        srv.shutdown()

    if fehler:
        print("FEHLER:")
        for f in fehler:
            print("  -", f)
        sys.exit(1)
    print(f"Sprachwahl geprueft: {len(SPRACHEN)} Sprachen, Persistenz, Rueckfall — alles gruen.")


if __name__ == "__main__":
    main()
