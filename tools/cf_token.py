#!/usr/bin/env python3
"""Welches Cloudflare-Token kann, was gebraucht wird? — eine Stelle für alle.

Der Anlass: Dieselbe Fehlannahme steckte in vier Werkzeugen. Alle prüften die
Gültigkeit eines Tokens über `/user/tokens/verify` — und dieser Endpunkt
antwortet mit 401 für jedes Token OHNE User-Scope, auch wenn es für Zone und
Konto einwandfrei gültig ist. Am 15./16.08.2026 galten dadurch drei brauchbare
Tokens als widerrufen, darunter das einzige mit Analytics- und Purge-Recht.

Die Regel, die daraus folgt und die dieses Modul durchsetzt:

    Ein Zugang wird gegen DIE RESSOURCE geprüft, die gebraucht wird —
    nie gegen einen allgemeinen Gültigkeits-Endpunkt.

Und: Welches Token welches Recht trägt, steht in keinem Feld. Der Name
"Email-Routing Token" verrät nicht, dass es Analytics liest und den Cache
leeren darf. Also werden alle Kandidaten durchprobiert.

    from cf_token import fuer_analytics, fuer_purge, fuer_workers
    tok = fuer_purge()          # -> Token oder None
"""
import json
import os
import subprocess
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ZONE = "0d7110c80d576750944785d0ae759209"      # provinglab.dev
KONTO = "5b4b2a56eeb5ec2010547b575d3db3f1"     # Blockinhalt@gmail.com

# Reihenfolge nach gemessener Trefferquote, nicht nach Namen.
KANDIDATEN = ("c8b0a042", "0fd9f886", "84c722a0", "d0ba695f", "09c49fa4")
API = "https://api.cloudflare.com/client/v4"


def _tokens():
    """Alle in Frage kommenden Tokens, Umgebungsvariable zuerst."""
    aus = []
    umgebung = os.environ.get("CF_API_TOKEN", "").strip()
    if umgebung:
        aus.append((umgebung, "CF_API_TOKEN"))
    sitzung = Path("/dev/shm/bw-session")
    if not sitzung.exists():
        return aus
    s = sitzung.read_text().strip()
    for kennung in KANDIDATEN:
        try:
            r = subprocess.run(["bw", "get", "item", kennung, "--session", s],
                               capture_output=True, text=True, timeout=60)
            if r.returncode:
                continue
            e = json.loads(r.stdout)
            t = (e.get("login") or {}).get("password", "").strip()
            if t:
                aus.append((t, e.get("name", kennung)[:44]))
        except Exception:
            continue
    return aus


def _versuch(tok, pfad, koerper=None, methode=None):
    daten = json.dumps(koerper).encode() if koerper is not None else None
    r = urllib.request.Request(
        API + pfad, daten,
        {"authorization": "Bearer " + tok, "content-type": "application/json"},
        method=methode)
    try:
        with urllib.request.urlopen(r, timeout=30) as a:
            d = json.load(a)
        return bool(d.get("success", True)) and not d.get("errors")
    except Exception:
        return False


def _graphql(tok):
    seit = (datetime.now(timezone.utc) - timedelta(hours=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = {"query": "query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                  "httpRequestsAdaptiveGroups(limit:1,filter:{datetime_geq:$s})"
                  "{count}}}}",
         "variables": {"z": ZONE, "s": seit}}
    r = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql", json.dumps(q).encode(),
        {"authorization": "Bearer " + tok, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=30) as a:
            return not json.load(a).get("errors")
    except Exception:
        return False


def _waehle(pruefung, was):
    versucht = []
    for tok, name in _tokens():
        versucht.append(name)
        if pruefung(tok):
            return tok, name
    return None, ("keines der hinterlegten Tokens darf " + was
                  + " (geprueft: " + ", ".join(versucht or ["keines lesbar"]) + ")")


def fuer_analytics():
    """Token, das die Zone-Analytik lesen darf."""
    return _waehle(_graphql, "die Zone-Analytik lesen")


def fuer_purge():
    """Token, das den Edge-Cache leeren darf.

    Geprüft wird mit einer echten Purge-Anfrage auf EINE unkritische Adresse.
    Ein Trockenlauf gibt es hier nicht — und robots.txt neu zu holen kostet
    nichts.
    """
    def p(tok):
        return _versuch(tok, f"/zones/{ZONE}/purge_cache",
                        {"files": ["https://provinglab.dev/robots.txt"]})
    return _waehle(p, "den Cache leeren")


def fuer_workers():
    """Token, das die Worker-Skripte des Kontos sehen darf."""
    def p(tok):
        return _versuch(tok, f"/accounts/{KONTO}/workers/scripts")
    return _waehle(p, "die Worker lesen")


if __name__ == "__main__":
    for name, f in (("Analytics", fuer_analytics), ("Cache leeren", fuer_purge),
                    ("Worker", fuer_workers)):
        tok, quelle = f()
        print(f"  {name:<14} {'geht  via ' + quelle if tok else 'FEHLT — ' + quelle}")
