#!/usr/bin/env python3
"""Warnt, bevor eine Frist ablaeuft, an der etwas haengt.

    python3 tools/fristen-pruefen.py            # alle Fristen, Warnung ab 90 Tagen
    python3 tools/fristen-pruefen.py --tage 30  # engere Schwelle
    python3 tools/fristen-pruefen.py --ci       # Ausgabe fuer GitHub Actions

Vier Fristen wurden am 3. August 2026 gesetzt oder vorgefunden, und an keiner
haengt eine Erinnerung:

  security.txt   Pflichtfeld nach RFC 9116. Laeuft es ab, gilt die Datei als
                 ungueltig — Sicherheitsforscher behandeln sie dann, als gaebe
                 es sie nicht.
  Zwei Tokens    Laufen 2027 aus. Danach schlaegt die Auslieferung fehl.
  Die Domain     **Auto-Renew ist ausgeschaltet.** Wird sie nicht von Hand
                 verlaengert, faellt die ganze Publikation aus — der teuerste
                 Fall, und der einzige, der sich nicht nachholen laesst, wenn
                 jemand anders sie in der Zwischenzeit registriert.

Die Fristen werden **gelesen, nicht gepflegt**: aus der Datei, aus der
Cloudflare-Schnittstelle und aus RDAP. Eine Liste, die jemand aktuell halten
muesste, waere genau der Fehler, den dieses Skript verhindern soll.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
KONTO = "5b4b2a56eeb5ec2010547b575d3db3f1"
HEUTE = datetime.date.today()


def tage_bis(datum):
    return (datum - HEUTE).days


def aus_security_txt():
    p = HIER / "docs" / ".well-known" / "security.txt"
    if not p.exists():
        return [("security.txt", None, "Datei fehlt — RFC 9116 erwartet sie")]
    m = re.search(r"^Expires:\s*(\d{4}-\d{2}-\d{2})", p.read_text(encoding="utf-8"), re.M)
    if not m:
        return [("security.txt", None, "kein Expires-Feld — die Datei gilt als ungueltig")]
    return [("security.txt", datetime.date.fromisoformat(m.group(1)),
             "Nach Ablauf behandeln Sicherheitsforscher die Datei als nicht vorhanden")]


def aus_cloudflare():
    """Tokens ueber die Schnittstelle. Ohne Leserecht wird uebersprungen, nicht
    geraten — eine erfundene Frist waere schlimmer als keine."""
    try:
        sitzung = open("/dev/shm/bw-session").read().strip()
    except OSError:
        return [("Cloudflare-Tokens", None, "Vaultwarden nicht offen — uebersprungen")]
    r = subprocess.run(["bw", "get", "item", "84c722a0-1341-4dbb-b543-7ea2de751840",
                        "--session", sitzung], capture_output=True, text=True)
    if r.returncode:
        return [("Cloudflare-Tokens", None, "Token nicht lesbar — uebersprungen")]
    tok = (json.loads(r.stdout).get("login") or {}).get("password", "").strip()
    req = urllib.request.Request(
        f"https://api.cloudflare.com/client/v4/accounts/{KONTO}/tokens",
        headers={"authorization": "Bearer " + tok})
    try:
        with urllib.request.urlopen(req, timeout=25) as a:
            d = json.load(a)
    except Exception as e:
        return [("Cloudflare-Tokens", None, f"nicht abrufbar ({type(e).__name__})")]
    if not d.get("success"):
        return [("Cloudflare-Tokens", None, "Schnittstelle verweigert")]
    aus = []
    for t in d["result"]:
        if t.get("status") != "active":
            continue
        if not t.get("expires_on"):
            aus.append((f"Token {t['name']}", None,
                        "KEIN Ablaufdatum — ein Token ohne Frist ist ein Token, "
                        "an das niemand mehr denkt"))
            continue
        aus.append((f"Token {t['name']}",
                    datetime.date.fromisoformat(t["expires_on"][:10]),
                    "Danach schlaegt die Auslieferung fehl"))
    return aus


def aus_rdap():
    """Ablauf der Domain ueber RDAP.

    Der Bootstrap-Dienst rdap.org loest die zustaendige Registry selbst auf.
    Direkt geratene Registry-Adressen antworten mit 404 — geprueft am
    03.08.2026 fuer `registry.google` und `rdap.iana.org`. Ein geratener
    Endpunkt, der 404 liefert, sieht aus wie „keine Frist gefunden" und ist
    damit gefaehrlicher als gar keine Pruefung.
    """
    try:
        req = urllib.request.Request(
            "https://rdap.org/domain/provinglab.dev",
            headers={"user-agent": "provinglab-fristen/1.0",
                     "accept": "application/rdap+json"})
        with urllib.request.urlopen(req, timeout=25) as a:
            d = json.load(a)
        for e in d.get("events", []):
            if e.get("eventAction") == "expiration":
                return [("Domain provinglab.dev",
                         datetime.date.fromisoformat(e["eventDate"][:10]),
                         "AUTO-RENEW IST AUS — ohne manuelle Verlaengerung faellt "
                         "die ganze Publikation aus, und die Adresse ist danach frei")]
    except Exception as e:
        return [("Domain provinglab.dev", None,
                 f"RDAP nicht abrufbar ({type(e).__name__}) — laut Vault 2027-08-01")]
    return [("Domain provinglab.dev", None, "kein expiration-Ereignis in der RDAP-Antwort")]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tage", type=int, default=90)
    p.add_argument("--ci", action="store_true")
    a = p.parse_args()

    alle = aus_security_txt() + aus_cloudflare() + aus_rdap()
    warnungen = 0
    print(f"Fristen, Schwelle {a.tage} Tage, Stand {HEUTE}\n")
    for name, datum, hinweis in sorted(alle, key=lambda x: (x[1] is None, x[1] or HEUTE)):
        if datum is None:
            print(f"  ?     {name:44} {hinweis}")
            if "KEIN Ablaufdatum" in hinweis:
                warnungen += 1
                if a.ci:
                    print(f"::warning::{name}: {hinweis}")
            continue
        t = tage_bis(datum)
        zeichen = "!" if t <= a.tage else ("x" if t < 0 else " ")
        print(f"  {zeichen}  {datum}  {name:44} {t:>5} Tage")
        if t <= a.tage:
            warnungen += 1
            print(f"        → {hinweis}")
            if a.ci:
                print(f"::warning::{name} laeuft in {t} Tagen ab ({datum}). {hinweis}")

    print(f"\n{warnungen} Frist(en) unter der Schwelle oder ohne Ablauf.")
    # Absichtlich immer 0: eine bald ablaufende Frist ist kein Grund, eine
    # Auslieferung anzuhalten. Sie ist ein Grund, es zu wissen.
    return 0


if __name__ == "__main__":
    sys.exit(main())
