#!/usr/bin/env python3
"""Meldet geaenderte Adressen an die Suchmaschinen, die IndexNow sprechen.

    python3 tools/indexnow.py                 # was sich seit dem letzten Lauf geaendert hat
    python3 tools/indexnow.py --alle          # die ganze Sitemap
    python3 tools/indexnow.py --pruefen       # zeigen, nichts senden

Warum ueberhaupt
----------------
Die Domain wurde am **1. August 2026** registriert. Am 3. August lieferte keine
Suchmaschine einen Treffer — auch nicht fuer den Namen selbst. Das ist kein
Fehler und keine technische Luecke, sondern das Alter: eine zwei Tage alte
Domain hat keine Autoritaet, und Rankings folgen ihr mit Monaten Abstand.

Was sich beschleunigen laesst, ist nicht das Ranking, sondern die **Aufnahme**.
IndexNow kehrt den Ablauf um: statt zu warten, bis ein Crawler wiederkommt,
wird ihm gesagt, dass sich etwas geaendert hat. Bing, Yandex, Seznam und Naver
werten das aus; **Google nicht** — dort bleibt es bei Sitemap und Search
Console.

Bei Yandex lohnt es hier besonders: der Bot war am 3. August mit 122 Abrufen in
24 Stunden der aktivste benannte Crawler auf der Zone, vor Googlebot mit 64.

Der Schluessel
--------------
IndexNow arbeitet ohne Konto. Der Nachweis ist eine Datei mit dem Schluessel
als Inhalt, die unter demselben Host liegt — wer die Datei ablegen kann,
kontrolliert die Domain. Der Schluessel ist deshalb **nicht geheim**; er steht
oeffentlich auf der Seite und gehoert nicht in den Vault.
"""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
DOCS = HIER / "docs"
HOST = "provinglab.dev"
BASIS = f"https://{HOST}"
STAND = HIER / ".indexnow-stand.json"     # nicht ausgeliefert, siehe .gitignore
KENNUNG = f"provinglab-indexnow/1.0 (+{BASIS}/)"

# Ein Endpunkt genuegt: die teilnehmenden Maschinen reichen die Meldung
# untereinander weiter. Zwei zu bedienen verdoppelt nur die Fehlerquellen.
ENDPUNKT = "https://api.indexnow.org/indexnow"


def schluessel():
    """Aus der abgelegten Datei lesen, nicht neu erzeugen.

    Ein bei jedem Lauf neu erfundener Schluessel wuerde bei jeder Meldung
    abgelehnt, weil die passende Datei noch nicht ausgeliefert ist — und der
    Fehler saehe aus wie ein Problem mit IndexNow.
    """
    treffer = sorted(DOCS.glob("*.txt"))
    for p in treffer:
        name = p.stem
        if re.fullmatch(r"[0-9a-f]{32,64}", name) and p.read_text().strip() == name:
            return name
    raise SystemExit(
        "Keine Schluesseldatei in docs/ gefunden. Einmalig anlegen:\n"
        "  python3 -c \"import secrets,pathlib;k=secrets.token_hex(16);\"\n"
        "  (siehe README dieses Skripts)")


def adressen():
    s = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    return re.findall(r"<loc>([^<]+)</loc>", s)


def geaendert(alle):
    """Nur melden, was neu oder veraendert ist.

    IndexNow bittet ausdruecklich darum, nicht bei jedem Lauf alles zu senden.
    Verglichen wird gegen den letzten Stand; beim ersten Lauf ist das alles.
    """
    stand = json.loads(STAND.read_text()) if STAND.exists() else {}
    s = (DOCS / "sitemap.xml").read_text(encoding="utf-8")
    jetzt = dict(re.findall(r"<loc>([^<]+)</loc>\s*<lastmod>([^<]+)</lastmod>", s))
    neu = [u for u in alle if stand.get(u) != jetzt.get(u)]
    return neu, jetzt


def senden(liste, key, trocken):
    if not liste:
        print("  nichts zu melden — seit dem letzten Lauf unveraendert")
        return True
    print(f"  {len(liste)} Adressen")
    for u in liste[:5]:
        print(f"    {u}")
    if len(liste) > 5:
        print(f"    … und {len(liste)-5} weitere")
    if trocken:
        print("  (Probelauf — nichts gesendet)")
        return True
    koerper = json.dumps({"host": HOST, "key": key,
                          "keyLocation": f"{BASIS}/{key}.txt",
                          "urlList": liste}).encode()
    req = urllib.request.Request(ENDPUNKT, koerper,
                                 {"content-type": "application/json; charset=utf-8",
                                  "user-agent": KENNUNG})
    try:
        with urllib.request.urlopen(req, timeout=30) as a:
            # 200 = angenommen, 202 = angenommen, Schluessel wird noch geprueft.
            print(f"  ✓ HTTP {a.status} — angenommen")
            return True
    except urllib.error.HTTPError as e:
        hinweis = {400: "Anfrage fehlerhaft", 403: "Schluessel nicht bestaetigt — "
                        "liegt die Datei unter keyLocation und ist sie erreichbar?",
                   422: "Adressen gehoeren nicht zum Host oder Schluessel passt nicht",
                   429: "zu viele Meldungen"}.get(e.code, "")
        print(f"  ✗ HTTP {e.code} {hinweis}")
        return False
    except Exception as e:
        print(f"  ✗ {type(e).__name__}: {e}")
        return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--alle", action="store_true", help="ganze Sitemap melden")
    p.add_argument("--pruefen", action="store_true")
    a = p.parse_args()

    key = schluessel()
    print(f"Schluessel: {key[:8]}… ({BASIS}/{key}.txt)")

    # Gegenprobe vor dem Senden: liegt die Datei wirklich? Ohne sie wird jede
    # Meldung mit 403 abgelehnt, und das saehe nach einem Fehler im Protokoll
    # aus statt nach einer fehlenden Datei.
    try:
        req = urllib.request.Request(f"{BASIS}/{key}.txt",
                                     headers={"user-agent": KENNUNG})
        with urllib.request.urlopen(req, timeout=20) as r:
            inhalt = r.read().decode().strip()
        if inhalt != key:
            print(f"  ! Datei erreichbar, Inhalt passt nicht ({inhalt[:16]}…)")
            return 1
        print("  ✓ Schluesseldatei erreichbar und korrekt")
    except Exception as e:
        print(f"  ! Schluesseldatei nicht abrufbar ({type(e).__name__}) — "
              "erst ausliefern, dann melden")
        return 1

    alle = adressen()
    liste, jetzt = (alle, None) if a.alle else geaendert(alle)
    ok = senden(liste, key, a.pruefen)
    if ok and not a.pruefen and jetzt is not None:
        STAND.write_text(json.dumps(jetzt, indent=1), encoding="utf-8")
    print("\n  Erreicht Bing, Yandex, Seznam und Naver. Google wertet IndexNow "
          "nicht aus —\n  dort bleibt es bei Sitemap und Search Console.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
