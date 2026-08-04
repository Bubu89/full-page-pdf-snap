#!/usr/bin/env python3
"""Prueft jeden Link der Publikation — intern wie extern — und die Store-Staende.

    python3 tools/links-pruefen.py             # gegen die lokalen Dateien
    python3 tools/links-pruefen.py --live      # gegen provinglab.dev

Warum ein eigenes Skript: `rechtscheck.py` prueft interne Ziele, aber keine
externen. Ein toter Store-Link faellt darum erst auf, wenn jemand ihn anklickt —
und bei einem Werkzeug, das ueber genau diese Links verteilt wird, ist das die
teuerste Stelle zum Schweigen.

Geprueft wird zusaetzlich, was kein Statuscode verraet: ob die Fassung im
Chrome Web Store und die auf addons.mozilla.org zusammenpassen. Ein Store, der
zwoelf Versionen zurueckliegt, ist erreichbar und trotzdem falsch.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DOCS = HIER / "docs"
BASIS = "https://provinglab.dev"

BROWSER = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"),
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "accept-language": "en,de;q=0.8",
}

AMO_SLUG = "full_page_pdf_snap_webpagesave"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"


def hole(url, methode="GET"):
    # Adressen mit Nicht-ASCII (kyrillische Slugs auf addons.mozilla.org)
    # bringen urllib zum Absturz, bevor eine Anfrage entsteht. Prozentkodieren,
    # sonst meldet der Pruefer einen eigenen Fehler als toten Link.
    sicher = urllib.parse.quote(url, safe=":/?#[]@!$&'()*+,;=~-._%")
    r = urllib.request.Request(sicher, headers=BROWSER, method=methode)
    try:
        with urllib.request.urlopen(r, timeout=30) as a:
            return a.status, a.read(600_000).decode("utf-8", "replace"), a.url
    except urllib.error.HTTPError as e:
        return e.code, "", url
    except Exception as e:
        return type(e).__name__, "", url


def links_sammeln():
    """Jeder href aus jeder ausgelieferten Seite, mit Fundstelle."""
    gefunden = {}
    for datei in sorted(DOCS.rglob("*.html")):
        s = datei.read_text(encoding="utf-8")
        rel = datei.relative_to(DOCS).as_posix()
        for m in re.finditer(r'href="([^"#][^"]*)"', s):
            gefunden.setdefault(m.group(1), set()).add(rel)
    # Auch die Textkanaele, die Agenten lesen
    for name in ("llms.txt",):
        p = DOCS / name
        if p.exists():
            for m in re.finditer(r"\((https?://[^)\s]+)\)", p.read_text(encoding="utf-8")):
                gefunden.setdefault(m.group(1), set()).add(name)
    return gefunden


def intern_pruefen(ziel, fundstelle):
    """Existiert das Ziel — aufgeloest relativ zu der Seite, die darauf verweist?

    Ohne die Fundstelle liest sich `citation-triage/` in
    `measurements/index.html` als Wurzelpfad, und der Pruefer meldet ein Dutzend
    intakter Verweise als tot. Ein Pruefwerkzeug, das an unveraenderten Seiten
    Alarm schlaegt, misst nur sich selbst.
    """
    pfad = ziel.split("#")[0].split("?")[0]
    if not pfad:
        return True
    if pfad.startswith(BASIS):
        pfad = "/" + pfad[len(BASIS):].lstrip("/")
    if pfad.startswith("/"):
        basis = DOCS
        rest = pfad.lstrip("/")
    else:
        basis = (DOCS / fundstelle).parent
        rest = pfad
    p = (basis / rest).resolve()
    try:
        p.relative_to(DOCS.resolve())
    except ValueError:
        return False                      # zeigt aus der Publikation hinaus
    return p.exists() or (p / "index.html").exists()


def stores_pruefen():
    """Erreichbarkeit UND Gleichstand der beiden Auslieferungen."""
    print("\nStore-Staende")
    stand = {}
    s, koerper, _ = hole(f"https://addons.mozilla.org/api/v5/addons/addon/{AMO_SLUG}/")
    if s == 200:
        d = json.loads(koerper)
        stand["firefox"] = d["current_version"]["version"]
        print(f"  addons.mozilla.org   {s}  Version {stand['firefox']}  "
              f"Nutzer {d.get('average_daily_users')}  Status {d.get('status')}")
    else:
        print(f"  addons.mozilla.org   {s}  ABRUF FEHLGESCHLAGEN")

    s, koerper, ende = hole(f"https://chromewebstore.google.com/detail/{CWS_ID}")
    if s == 200:
        # Aus dem Umfeld lesen, nicht als ersten Treffer: das alte Muster nahm
        # am 4. August 2026 ein Stueck SVG-Pfad (`4.38.38`) fuer die Fassung
        # und meldete 2.12.1, waehrend der Store 2.17.0 auslieferte. Dieselbe
        # Reihenfolge wie in build-versionen.py — zwei Werkzeuge, die dieselbe
        # Seite lesen, duerfen nicht zwei Zahlen melden.
        m = (re.search(r'\\?"version\\?":\s*\\?"(\d+\.\d+\.\d+)', koerper)
             or re.search(r">Version</div><div[^>]*>([\d.]+)<", koerper))
        stand["chrome"] = m.group(1) if m else "?"
        nutzer = re.search(r">([\d,]+) users<", koerper)
        print(f"  chromewebstore       {s}  Version {stand['chrome']}  "
              f"Nutzer {nutzer.group(1) if nutzer else '?'}")
    else:
        print(f"  chromewebstore       {s}  ABRUF FEHLGESCHLAGEN")

    lokal = json.loads((HIER / "manifest.json").read_text(encoding="utf-8"))["version"]
    ch_lokal = json.loads((HIER / "chrome-mv3" / "manifest.json").read_text(encoding="utf-8"))
    print(f"  lokal Firefox        {lokal}")
    print(f"  lokal Chrome         {ch_lokal['version']}  "
          f"(mindestens Chrome {ch_lokal.get('minimum_chrome_version', '?')})")

    warnungen = []
    if stand.get("firefox") and stand.get("chrome") and stand["firefox"] != stand["chrome"]:
        warnungen.append(f"Firefox liefert {stand['firefox']}, Chrome {stand['chrome']} — "
                         "wer die Seite nach Chrome schickt, bekommt eine aeltere Fassung.")
    if stand.get("firefox") and lokal != stand["firefox"]:
        warnungen.append(f"lokal {lokal}, im Firefox-Store {stand['firefox']} — "
                         "gebaut, aber nicht eingereicht.")
    return warnungen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--live", action="store_true",
                   help="interne Ziele gegen provinglab.dev statt gegen docs/ pruefen")
    a = p.parse_args()

    alle = links_sammeln()
    extern = {u: q for u, q in alle.items() if u.startswith("http")}
    intern = {u: q for u, q in alle.items() if not u.startswith(("http", "mailto:"))}
    print(f"{len(alle)} verschiedene Adressen: {len(extern)} extern, {len(intern)} intern")

    fehler = []

    print("\nExterne Adressen")
    for url in sorted(extern):
        s, _, ende = hole(url, "HEAD" if "addons.mozilla" not in url else "GET")
        if s in (405, 403) and url.startswith("http"):        # HEAD nicht erlaubt
            s, _, ende = hole(url)
        ok = s == 200
        umleitung = "" if ende == url else f"  -> {ende[:70]}"
        print(f"  {str(s):>5}  {url[:78]}{umleitung}")
        if not ok:
            fehler.append((url, s, sorted(extern[url])))

    print("\nInterne Ziele")
    tot = 0
    for url in sorted(intern):
        # Jede Fundstelle einzeln: derselbe relative Pfad meint je Seite anderes.
        for quelle in sorted(intern[url]):
            if not intern_pruefen(url, quelle):
                tot += 1
                print(f"  TOT   {url}   in {quelle}")
                fehler.append((url, "fehlt", [quelle]))
    if not tot:
        print(f"  alle {len(intern)} erreichbar")

    warnungen = stores_pruefen()

    print()
    for w in warnungen:
        print(f"WARNUNG: {w}")
    if fehler:
        print(f"\n{len(fehler)} Adressen antworten nicht mit 200.")
        sys.exit(1)
    print("\nKeine toten Adressen." + ("" if not warnungen else
          f" {len(warnungen)} Warnung(en) zu den Store-Staenden."))


if __name__ == "__main__":
    main()
