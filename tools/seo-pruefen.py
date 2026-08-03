#!/usr/bin/env python3
"""Was ein SEO-Plugin fuer WordPress taete — hier als Pruefung im Repository.

    python3 tools/seo-pruefen.py            # alles pruefen
    python3 tools/seo-pruefen.py --ci       # Ausgabe fuer GitHub Actions
    python3 tools/seo-pruefen.py --live     # zusaetzlich die Kopfzeilen der Live-Seite

Warum kein Plugin
-----------------
Diese Seite ist statisches HTML auf GitHub Pages hinter Cloudflare. Yoast,
Rank Math, All in One SEO und Wordfence setzen alle WordPress voraus und sind
hier nicht installierbar. Was sie leisten, laesst sich aber nachbilden — und
zwar besser, weil eine Pruefung im Repository die Auslieferung anhalten kann,
waehrend ein Plugin nur eine Ampel im Redaktionsfenster zeigt.

Was diese Datei aus jenen Plugins uebernimmt:

  Titel- und Beschreibungslaengen      Yoast, Rank Math
  eine H1 je Seite                     Yoast
  Canonical vorhanden und richtig      alle
  strukturierte Daten vorhanden        Rank Math, Schema Pro
  verwaiste Seiten (keine Verweise)    Link Whisper
  Bilder ohne Alternativtext           Yoast
  Sicherheits-Kopfzeilen               Wordfence, Sucuri

Was bewusst **nicht** uebernommen wird
--------------------------------------
**Keine Analytik im Browser.** Die Datenschutzerklaerung sagt woertlich, die
Seite setze keine Cookies und binde keine Analytik-Bibliothek ein. Google
Analytics oder ein aequivalentes Skript einzubauen wuerde diese Zusage brechen,
in der EU eine Einwilligung erfordern und der Seite ein Banner aufzwingen —
fuer Zahlen, die serverseitig ohnehin vorliegen (`tools/crawler-bericht.py`).

**Keine Keyword-Dichte.** Das war schon 2010 kein Rankingfaktor und ist heute
ein Anreiz, schlechter zu schreiben.

**Kein Lesbarkeitsindex.** Flesch-Werte auf einem Text ueber HTTP-Statuscodes
messen das Vokabular des Themas, nicht die Qualitaet des Satzbaus.
"""
import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DOCS = HIER / "docs"
BASIS = "https://provinglab.dev"

# Google schneidet Titel bei etwa 600 Pixeln ab, was rund 60 Zeichen entspricht.
# 65 als Grenze, weil schmale Zeichen mehr zulassen und ein starrer Wert sonst
# jede zweite Seite meldet.
TITEL_MAX, TITEL_MIN = 65, 20
BESCHREIBUNG_MAX, BESCHREIBUNG_MIN = 165, 70

KOPFZEILEN_PFLICHT = {
    "strict-transport-security": "erzwingt HTTPS auch beim ersten Aufruf nach dem Merken",
    "content-security-policy": "begrenzt, was eine eingeschleuste Zeile ueberhaupt tun kann",
    "x-content-type-options": "verhindert, dass der Browser den Typ selbst raet",
    "referrer-policy": "haelt die Herkunftsadresse aus fremden Logs heraus",
    "permissions-policy": "schaltet Kamera, Mikrofon und Ortung ab",
}


def umgezogen():
    """Adressen, die der Worker mit 301 beantwortet.

    Ihre HTML-Dateien liegen noch im Baum, werden aber nie ausgeliefert. Sie
    als Seiten zu pruefen erzeugt drei sichere Fehlalarme — keine H1, keine
    Beschreibung, verwaist — und genau die haben beim ersten Lauf die echten
    Befunde zugedeckt.
    """
    w = (HIER / "worker" / "mcp.js").read_text(encoding="utf-8")
    block = re.search(r"const UMGEZOGEN = \{(.*?)\};", w, re.S)
    if not block:
        return set()
    return {f'{p.strip("/")}/index.html'
            for p in re.findall(r'"(/[^"]+)":', block.group(1))}


def seiten():
    aus = umgezogen()
    return [p for p in sorted(DOCS.rglob("index.html")) if rel(p) not in aus]


def rel(p):
    return str(p.relative_to(DOCS))


def pruefe_seite(p, befunde):
    s = p.read_text(encoding="utf-8", errors="replace")
    r = rel(p)

    m = re.search(r"<title>(.*?)</title>", s, re.S)
    if not m:
        befunde.append(("FEHLER", r, "kein-titel", "Seite ohne <title>"))
    else:
        t = m.group(1).strip()
        # Der Suffix „ — Proving Lab" zaehlt mit, weil er auch angezeigt wird.
        if len(t) > TITEL_MAX:
            befunde.append(("HINWEIS", r, "titel-lang",
                            f"{len(t)} Zeichen — wird in Ergebnissen nach etwa "
                            f"{TITEL_MAX} abgeschnitten: {t[:60]}…"))
        elif len(t) < TITEL_MIN:
            befunde.append(("WARNUNG", r, "titel-kurz", f"{len(t)} Zeichen: {t}"))

    m = re.search(r'<meta name="description" content="([^"]*)"', s)
    if not m:
        befunde.append(("WARNUNG", r, "keine-beschreibung",
                        "ohne description schreibt die Suchmaschine selbst eine"))
    else:
        b = m.group(1).strip()
        if len(b) > BESCHREIBUNG_MAX:
            befunde.append(("HINWEIS", r, "beschreibung-lang", f"{len(b)} Zeichen"))
        elif len(b) < BESCHREIBUNG_MIN:
            befunde.append(("WARNUNG", r, "beschreibung-kurz", f"{len(b)} Zeichen"))

    # Zweisprachige Seiten tragen zwei H1, von denen immer nur eine sichtbar
    # ist — erkennbar am `data-lang`. Das als Doppelung zu melden traf sieben
    # Seiten und war jedes Mal falsch.
    h1 = re.findall(r"<h1[^>]*>", s)
    echte = [h for h in h1 if "data-lang" not in h]
    if len(h1) == 0:
        befunde.append(("WARNUNG", r, "keine-h1", "Seite ohne <h1>"))
    elif len(echte) > 1:
        befunde.append(("WARNUNG", r, "mehrere-h1",
                        f"{len(echte)} ohne Sprachkennzeichnung"))

    if not re.search(r'<link rel="canonical"', s):
        befunde.append(("FEHLER", r, "kein-canonical",
                        "ohne canonical konkurrieren Varianten derselben Seite"))

    if not re.search(r'type="application/ld\+json"', s):
        befunde.append(("HINWEIS", r, "keine-strukturdaten",
                        "kein JSON-LD — die Seite erscheint ohne Zusatzangaben"))

    for bild in re.findall(r"<img\s[^>]*>", s):
        if 'alt="' not in bild:
            befunde.append(("WARNUNG", r, "bild-ohne-alt", bild[:70]))


def verwaiste(befunde):
    """Seiten, auf die von nirgendwo verwiesen wird.

    Eine Seite ohne eingehenden Verweis wird von Crawlern nur ueber die Sitemap
    gefunden und gilt ihnen als unwichtig — das ist der Befund, den Link
    Whisper unter „orphaned content" meldet.
    """
    eingehend = defaultdict(int)
    alle = {rel(p) for p in seiten()}
    for p in seiten():
        s = p.read_text(encoding="utf-8", errors="replace")
        von = Path(rel(p)).parent
        for ziel in re.findall(r'href="([^"#?]+)"', s):
            if ziel.startswith(("http", "mailto:", "//")):
                continue
            pfad = (von / ziel).resolve().relative_to(Path("/").resolve()) \
                if ziel.startswith("/") else None
            aufgeloest = ziel.lstrip("/") if ziel.startswith("/") else str(
                (von / ziel))
            aufgeloest = re.sub(r"/+", "/", aufgeloest).strip("/")
            kandidat = f"{aufgeloest}/index.html" if not aufgeloest.endswith(
                ".html") else aufgeloest
            kandidat = kandidat.lstrip("/")
            if kandidat in alle and kandidat != rel(p):
                eingehend[kandidat] += 1
    for seite in sorted(alle):
        if seite == "index.html":
            continue
        if eingehend.get(seite, 0) == 0:
            befunde.append(("WARNUNG", seite, "verwaist",
                            "keine interne Verlinkung — nur ueber die Sitemap auffindbar"))


def kopfzeilen(befunde):
    try:
        req = urllib.request.Request(BASIS + "/", headers={"user-agent": "provinglab-seo/1.0"})
        with urllib.request.urlopen(req, timeout=25) as a:
            vorhanden = {k.lower() for k in a.headers.keys()}
    except Exception as e:
        befunde.append(("HINWEIS", "(live)", "kopfzeilen-unpruefbar",
                        f"{type(e).__name__} — uebersprungen"))
        return
    for k, warum in KOPFZEILEN_PFLICHT.items():
        if k not in vorhanden:
            befunde.append(("WARNUNG", "(live)", "kopfzeile-fehlt", f"{k} — {warum}"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--ci", action="store_true")
    p.add_argument("--live", action="store_true", help="Kopfzeilen der Live-Seite pruefen")
    a = p.parse_args()

    befunde = []
    for s in seiten():
        pruefe_seite(s, befunde)
    verwaiste(befunde)
    if a.live:
        kopfzeilen(befunde)

    rang = {"FEHLER": 0, "WARNUNG": 1, "HINWEIS": 2}
    for stufe, wo, kennung, text in sorted(befunde, key=lambda x: (rang[x[0]], x[1])):
        print(f"  [{kennung}] {wo}\n      {text}")
        if a.ci and stufe == "FEHLER":
            print(f"::error::{wo}: {kennung} — {text}")
        elif a.ci and stufe == "WARNUNG":
            print(f"::warning::{wo}: {kennung} — {text}")

    z = {s: sum(1 for b in befunde if b[0] == s) for s in rang}
    print(f"\n{z['FEHLER']} Fehler, {z['WARNUNG']} Warnungen, {z['HINWEIS']} Hinweise "
          f"in {len(seiten())} Seiten.")
    return 1 if z["FEHLER"] else 0


if __name__ == "__main__":
    sys.exit(main())
