#!/usr/bin/env python3
"""Misst, wie zuverlaessig zitierte Weblinks noch abrufbar und archiviert sind.

Grundgesamtheit: die externen Links aus den Literatur- und Weblink-Abschnitten
deutschsprachiger Wikipedia-Artikel eines festgelegten Themenfelds. Das ist eine
oeffentliche, jederzeit nachziehbare Quelle - anders als eine selbst
zusammengestellte Linkliste, die niemand nachpruefen kann.

Gemessen wird je URL:
  1. Antwortet der Server heute? (HEAD, bei Bedarf GET)
  2. Liegt im Internet Archive ein Schnappschuss? Wie alt ist der juengste?

Die zweite Frage ist die eigentliche: Ein toter Link, den jemand archiviert hat,
ist wiederherstellbar. Ein toter Link ohne Archiv ist weg.

    python3 messung-quellen-archiv.py --stichprobe 150
    python3 messung-quellen-archiv.py --stichprobe 40 --schnell

Schreibt docs/data/<datum>-quellen-archiv.json
"""
import argparse
import datetime
import json
import random
import sys
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import requests

REPO = Path(__file__).resolve().parent
ZIEL = REPO / "docs" / "data"

WIKI_API = "https://de.wikipedia.org/w/api.php"
# Themenfeld: Wirtschafts- und Sozialwissenschaften — der Bereich, in dem
# Studierende ueberwiegend Webquellen zitieren (Behoerden, Verbaende, Presse).
KATEGORIEN = [
    "Kategorie:Betriebswirtschaftslehre",
    "Kategorie:Volkswirtschaftslehre",
    "Kategorie:Arbeitsmarktpolitik",
    "Kategorie:Sozialpolitik",
    "Kategorie:Bildungspolitik",
]
KOPF = {"User-Agent": "provinglab.dev research script (contact via provinglab.dev/about)"}

# Diese Ziele sind keine Belegquellen, sondern Infrastruktur - sie wuerden die
# Messung schoenfaerben, weil sie praktisch nie verschwinden.
AUSSCHLUSS = (
    "doi.org", "dx.doi.org", "worldcat.org", "d-nb.info", "portal.dnb.de",
    "web.archive.org", "archive.org", "wikidata.org", "wikimedia.org",
    "wikipedia.org", "isbnsearch.org", "jstor.org/stable",
)


def artikel_sammeln(anzahl_je_kategorie=60):
    """Artikelnamen aus den festgelegten Kategorien holen."""
    namen = []
    for kat in KATEGORIEN:
        p = {"action": "query", "list": "categorymembers", "cmtitle": kat,
             "cmlimit": anzahl_je_kategorie, "cmnamespace": 0, "format": "json"}
        try:
            r = requests.get(WIKI_API, params=p, headers=KOPF, timeout=30)
            r.raise_for_status()
            namen += [m["title"] for m in r.json()["query"]["categorymembers"]]
        except Exception as e:
            print(f"  Kategorie {kat}: {e}", file=sys.stderr)
        time.sleep(0.3)
    return sorted(set(namen))


def links_sammeln(artikel):
    """Externe Links der Artikel einsammeln, Infrastruktur ausgenommen."""
    treffer = []
    for i in range(0, len(artikel), 20):          # API nimmt 20 Titel je Aufruf
        block = artikel[i:i + 20]
        p = {"action": "query", "titles": "|".join(block), "prop": "extlinks",
             "ellimit": 500, "format": "json"}
        try:
            r = requests.get(WIKI_API, params=p, headers=KOPF, timeout=30)
            r.raise_for_status()
            for seite in r.json().get("query", {}).get("pages", {}).values():
                for el in seite.get("extlinks", []):
                    url = el.get("*") or ""
                    if not url.startswith("http"):
                        continue
                    wirt = urllib.parse.urlparse(url).netloc.lower()
                    if any(a in url for a in AUSSCHLUSS):
                        continue
                    treffer.append({"url": url, "host": wirt, "artikel": seite.get("title")})
        except Exception as e:
            print(f"  Linkblock {i}: {e}", file=sys.stderr)
        time.sleep(0.3)
    return treffer


def lebt(url, timeout=20):
    """Antwortet der Server? HEAD zuerst, weil viele Server GET drosseln.

    Gibt neben dem Status ein Urteil zurueck. Der erste Durchlauf zaehlte jede
    Nichtantwort als toten Link und kam so auf 38,7 % - darunter neun Seiten,
    die lediglich Bot-Abwehr betreiben (403) und im Browser einwandfrei laden.
    Nur 404 und 410 sagen "gibt es nicht mehr"; alles andere ist ungeklaert und
    wird auch so ausgewiesen.
    """
    status, fehler = None, None
    for versuch in range(2):
        try:
            r = requests.head(url, headers=KOPF, timeout=timeout, allow_redirects=True)
            if r.status_code in (403, 405, 501):    # HEAD nicht erlaubt -> GET
                r = requests.get(url, headers=KOPF, timeout=timeout, stream=True)
            status, fehler = r.status_code, None
            break
        except requests.exceptions.SSLError as e:
            fehler = "TLS: " + type(e).__name__
        except requests.exceptions.Timeout:
            fehler = "Zeitueberschreitung"
        except requests.exceptions.ConnectionError as e:
            fehler = "Verbindung: " + type(e).__name__
        except Exception as e:
            fehler = type(e).__name__
        if versuch == 0:
            time.sleep(2)                           # einmal nachfassen

    if status and 200 <= status < 400:
        urteil = "erreichbar"
    elif status in (404, 410):
        urteil = "verschwunden"                     # der Server sagt es selbst
    elif status:
        urteil = "ungeklaert"                       # 403, 400, 5xx - Abwehr o. Stoerung
    elif fehler and "Verbindung" in fehler:
        urteil = "ungeklaert"                       # Host weg ODER nur gestoert
    else:
        urteil = "ungeklaert"
    return status, fehler, urteil


def archiviert(url, timeout=30):
    """Juengster Schnappschuss im Internet Archive.

    Rueckgabe (stempel, geklaert). geklaert=False heisst: der Dienst hat nicht
    geantwortet - daraus darf kein "nicht archiviert" werden. Genau dieser
    Kurzschluss liess im ersten Durchlauf 57 % der Quellen als unarchiviert
    erscheinen, darunter dejure.org und bgbl.de, die beide seit Jahren im
    Archiv liegen. Ursache war die Drosselung bei paralleler Abfrage.
    """
    for versuch in range(3):
        try:
            r = requests.get("https://archive.org/wayback/available",
                             params={"url": url}, headers=KOPF, timeout=timeout)
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(4 * (versuch + 1))
                continue
            r.raise_for_status()
            schnapp = (r.json().get("archived_snapshots") or {}).get("closest")
            if schnapp and schnapp.get("available"):
                return schnapp.get("timestamp"), True     # Form: JJJJMMTTHHMMSS
            # Gegenprobe ueber den CDX-Index: die availability-Schnittstelle
            # meldet gelegentlich nichts, obwohl Aufnahmen vorliegen.
            c = requests.get("https://web.archive.org/cdx/search/cdx",
                             params={"url": url, "output": "json", "limit": -1,
                                     "fl": "timestamp", "filter": "statuscode:200"},
                             headers=KOPF, timeout=timeout)
            if c.status_code == 200 and c.text.strip():
                zeilen = c.json()
                if len(zeilen) > 1:
                    return zeilen[-1][0], True
            return None, True                             # geklaert: kein Schnappschuss
        except Exception:
            time.sleep(3 * (versuch + 1))
    return None, False                                    # Dienst hat nicht geantwortet


def pruefe(eintrag):
    status, fehler, urteil = lebt(eintrag["url"])
    time.sleep(0.6)                                       # hoeflich zum Archiv
    stempel, geklaert = archiviert(eintrag["url"])
    alter_tage = None
    if stempel and len(stempel) >= 8:
        try:
            d = datetime.datetime.strptime(stempel[:8], "%Y%m%d").date()
            alter_tage = (datetime.date.today() - d).days
        except ValueError:
            pass
    return {**eintrag, "status": status, "fehler": fehler, "urteil": urteil,
            "archiv_stempel": stempel, "archiv_alter_tage": alter_tage,
            "archiv_geklaert": geklaert,
            "erreichbar": urteil == "erreichbar",
            "archiviert": bool(stempel)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stichprobe", type=int, default=150)
    ap.add_argument("--schnell", action="store_true", help="weniger Artikel einsammeln")
    ap.add_argument("--saat", type=int, default=20260802, help="fuer Wiederholbarkeit")
    a = ap.parse_args()

    print("Artikel einsammeln ...")
    artikel = artikel_sammeln(20 if a.schnell else 60)
    print(f"  {len(artikel)} Artikel")

    print("Externe Links einsammeln ...")
    alle = links_sammeln(artikel)
    print(f"  {len(alle)} Links (Infrastruktur bereits ausgenommen)")

    # Je Host hoechstens ein Link: sonst bestimmt eine einzige, oft verlinkte
    # Behoerdenseite das Ergebnis.
    je_host, gesehen = [], set()
    random.seed(a.saat)
    random.shuffle(alle)
    for e in alle:
        if e["host"] in gesehen:
            continue
        gesehen.add(e["host"])
        je_host.append(e)
    print(f"  {len(je_host)} verschiedene Hosts")

    probe = je_host[:a.stichprobe]
    print(f"Pruefe {len(probe)} URLs (live + Archiv) ...")
    with ThreadPoolExecutor(max_workers=6) as ex:   # hoeflich zu beiden Diensten
        ergebnisse = list(ex.map(pruefe, probe))

    n = len(ergebnisse)
    tot = [e for e in ergebnisse if not e["erreichbar"]]
    ohne_archiv = [e for e in ergebnisse if not e["archiviert"]]
    tot_ohne_archiv = [e for e in ergebnisse if not e["erreichbar"] and not e["archiviert"]]
    alter = [e["archiv_alter_tage"] for e in ergebnisse if e["archiv_alter_tage"] is not None]
    alter.sort()

    zus = {
        "geprueft": n,
        "nicht_erreichbar": len(tot),
        "nicht_erreichbar_prozent": round(100 * len(tot) / n, 1) if n else None,
        "ohne_archiv": len(ohne_archiv),
        "ohne_archiv_prozent": round(100 * len(ohne_archiv) / n, 1) if n else None,
        "tot_und_ohne_archiv": len(tot_ohne_archiv),
        "tot_und_ohne_archiv_prozent": round(100 * len(tot_ohne_archiv) / n, 1) if n else None,
        "archivalter_median_tage": alter[len(alter) // 2] if alter else None,
        "archivalter_aeltestes_viertel_tage": alter[int(len(alter) * .75)] if alter else None,
    }

    ZIEL.mkdir(parents=True, exist_ok=True)
    heute = datetime.date.today().isoformat()
    datei = ZIEL / f"{heute}-quellen-archiv.json"
    datei.write_text(json.dumps({
        "gemessen_am": heute,
        "methode": {
            "grundgesamtheit": "externe Links deutschsprachiger Wikipedia-Artikel "
                               "aus fuenf Kategorien der Wirtschafts- und Sozialwissenschaften",
            "kategorien": KATEGORIEN,
            "ausgeschlossen": list(AUSSCHLUSS),
            "je_host": "hoechstens ein Link je Host",
            "stichprobe": n,
            "saat": a.saat,
            "erreichbarkeit": "HEAD, bei 403/405/501 GET; erreichbar = Status 200-399",
            "archiv": "archive.org/wayback/available, juengster Schnappschuss",
            "grenzen": "Keine Zufallsstichprobe aus allen studentischen Quellen. "
                       "Wikipedia-Belege sind gepflegter als der Durchschnitt - "
                       "die Werte sind daher eher zu guenstig als zu streng.",
        },
        "zusammenfassung": zus,
        "lizenz": "CC BY 4.0",
        "eintraege": ergebnisse,
    }, ensure_ascii=False, indent=2), encoding="utf-8")

    print()
    for k, v in zus.items():
        print(f"  {k:38} {v}")
    print(f"\nGeschrieben: {datei}")


if __name__ == "__main__":
    sys.exit(main())
