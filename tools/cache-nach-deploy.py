#!/usr/bin/env python3
"""Haelt die Seite am Edge vorraetig und leert den Cache nach einer Auslieferung.

    python3 tools/cache-nach-deploy.py            # Cache leeren (nach git push)
    python3 tools/cache-nach-deploy.py --regel    # zusaetzlich die Edge-TTL-Regel setzen
    python3 tools/cache-nach-deploy.py --pruefen  # nur zeigen, nichts aendern

Warum das noetig ist, gemessen am 03.08.2026 ueber 24 Stunden: **262 Antworten
mit HTTP 504** auf Adressen, die es gibt — `/tools/` 51 mal, die Startseite 36
mal. Dazu 404 auf Seiten, die live sind. Beides faellt in die Zeitfenster, in
denen GitHub Pages neu baut und das Origin kurz nicht antwortet.

`serve_stale` und `always_online` sind eingeschaltet, konnten aber nichts
ausliefern: GitHub Pages sendet `max-age=600`, und die Cache-Regel folgte dem
Origin. Zehn Minuten nach dem letzten Abruf lag am Edge nichts mehr vor.

Die Loesung ist ein Paar, das nur zusammen funktioniert:

  1. Edge-TTL deutlich hoeher als das Origin-TTL, damit ueberhaupt eine Kopie
     vorliegt, wenn das Origin ausfaellt.
  2. Gezieltes Leeren nach jeder Auslieferung, damit die hohe Haltedauer keine
     veralteten Seiten bedeutet.

Ohne Schritt 2 waere Schritt 1 ein Fehler. Deshalb stehen sie in einer Datei.
"""
import argparse
import json
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

ZONE = "0d7110c80d576750944785d0ae759209"
ITEM = "0fd9f886-bdb1-40a2-b364-24961e4d2253"     # Cloudflare API Token — provinglab.dev
API = "https://api.cloudflare.com/client/v4"
BASIS = "https://provinglab.dev"

# Vier Stunden. Lange genug, um jeden Neubau von GitHub Pages zu ueberbruecken,
# kurz genug, dass ein vergessener Purge sich von selbst aufloest.
EDGE_TTL = 14400

# Fehlerantworten werden NICHT gehalten. Die erste Fassung der Regel setzte die
# Haltedauer ueber alle Statuscodes, und das hat sich am 3. August 2026 gerecht:
# in 24 Stunden 850 Antworten mit 404, davon der groesste Teil mit
# `cacheStatus=hit` — auf Seiten, die es gibt. Der Edge hatte waehrend eines
# Neubaus von GitHub Pages ein 404 eingefangen und lieferte es danach vier
# Stunden lang weiter aus. Eine Regel gegen Ausfaelle, die den Ausfall
# konserviert, ist schlimmer als keine.
#
# Dazu 460 Antworten mit 504, alle mit `cacheStatus=miss`: keine Kopie am Edge,
# also Gang zum Origin, und das baute gerade. Beides zeigt in dieselbe Richtung
# — gehalten werden darf nur, was tatsaechlich eine Seite ist.
# -1 heisst „no-store", 0 hiesse nur „revalidieren" — und revalidieren laesst
# den Eintrag am Edge stehen. Mit 0 gemessen: der zweite Abruf derselben
# fehlenden Adresse kam als `cf-cache-status: HIT` zurueck. Erst -1 verhindert
# das Speichern wirklich.
FEHLER_TTL = [
    {"status_code_range": {"from": 400, "to": 499}, "value": -1},
    {"status_code_range": {"from": 500, "to": 599}, "value": -1},
]


def token():
    """Das Token, das den Cache WIRKLICH leeren darf.

    Vorher stand hier ein fester Vault-Eintrag. Der darf es nicht, und der
    Purge scheiterte mit "Authentication error" — sichtbar erst, wenn man
    hinsieht. Welches Token welches Recht traegt, steht in keinem Feld; also
    werden alle durchprobiert, geprueft mit einer echten Purge-Anfrage.
    (16.08.2026, siehe tools/cf_token.py)
    """
    import cf_token
    tok, quelle = cf_token.fuer_purge()
    if not tok:
        sys.exit(quelle)
    print(f"  Zugang: {quelle}")
    return tok


def ruf(pfad, methode="GET", koerper=None, tok=None):
    d = json.dumps(koerper).encode() if koerper is not None else None
    r = urllib.request.Request(API + pfad, d,
                               {"authorization": "Bearer " + tok,
                                "content-type": "application/json"}, method=methode)
    try:
        with urllib.request.urlopen(r, timeout=30) as a:
            return json.load(a)
    except urllib.error.HTTPError as e:
        return json.load(e)


def regel_setzen(tok, trocken):
    """Setzt die HTML-Regel auf eine feste Haltedauer statt auf das Origin-TTL."""
    pfad = f"/zones/{ZONE}/rulesets/phases/http_request_cache_settings/entrypoint"
    d = ruf(pfad, tok=tok)
    if not d.get("success"):
        print("  Regelsatz nicht lesbar:", [e.get("message") for e in d.get("errors", [])])
        return False
    regeln = d["result"].get("rules") or []
    geaendert = False
    for r in regeln:
        if "HTML am Edge" not in (r.get("description") or ""):
            continue
        ap = r.setdefault("action_parameters", {})
        ist = ap.get("edge_ttl", {})
        if (ist.get("mode") == "override_origin" and ist.get("default") == EDGE_TTL
                and ist.get("status_code_ttl") == FEHLER_TTL):
            print(f"  = Edge-TTL bereits {EDGE_TTL}s, Fehlerseiten ausgenommen")
            return True
        print(f"  ~ Edge-TTL {json.dumps(ist)} → override_origin {EDGE_TTL}s "
              "(4xx/5xx ausgenommen)")
        ap["edge_ttl"] = {"mode": "override_origin", "default": EDGE_TTL,
                          "status_code_ttl": FEHLER_TTL}
        ap["serve_stale"] = {"disable_stale_while_updating": False}
        geaendert = True
    if not geaendert:
        print("  ! Regel 'HTML am Edge …' nicht gefunden")
        return False
    if trocken:
        print("  (Probelauf — nichts geschrieben)")
        return True
    # Nur die Felder senden, die der Regelsatz-Endpunkt annimmt.
    schlank = [{k: v for k, v in r.items()
                if k in ("action", "action_parameters", "expression", "description", "enabled")}
               for r in regeln]
    a = ruf(pfad, "PUT", {"rules": schlank}, tok)
    if a.get("success"):
        print("  ✓ Regel gesetzt")
        return True
    print("  ✗", [e.get("message") for e in a.get("errors", [])])
    return False


def leeren(tok, trocken):
    """Alles leeren. Bei einer Seite dieser Groesse ist das billiger als eine
    Liste zu pflegen, die irgendwann eine neue Adresse vergisst."""
    if trocken:
        print("  (Probelauf — nicht geleert)")
        return True
    a = ruf(f"/zones/{ZONE}/purge_cache", "POST", {"purge_everything": True}, tok)
    if a.get("success"):
        print("  ✓ Cache geleert")
        return True
    print("  ✗", [e.get("message") for e in a.get("errors", [])])
    return False


def zustand():
    """Gegenprobe: liefert der Edge aus, und wie alt ist die Kopie?"""
    print("\n  Gegenprobe")
    for p in ("/", "/tools/", "/for-agents/", "/measurements/"):
        r = urllib.request.Request(BASIS + p, headers={"user-agent": "provinglab-cache-check/1.0"})
        try:
            with urllib.request.urlopen(r, timeout=20) as a:
                print(f"    {a.status}  {p:<20} cache={a.headers.get('cf-cache-status')}"
                      f"  age={a.headers.get('age', '-')}")
        except Exception as e:
            print(f"    --  {p:<20} {type(e).__name__}")


def auf_pages_warten(minuten=5):
    """Wartet, bis GitHub Pages den aktuellen Commit ausliefert.

    Ohne das ist der Purge schlimmer als keiner: er holt die **alte** Fassung
    frisch an den Edge und zementiert sie fuer die volle Haltedauer. Genau so
    passiert am 3. August 2026 — die Pipeline war gruen, der Purge lief, und
    die Seite zeigte vier Stunden lang den Stand davor.

    Geprueft wird gegen den Commit, nicht gegen eine Zeitspanne: nur der sagt,
    ob der Ursprung wirklich den neuen Stand hat.
    """
    kopf = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                          text=True, cwd=Path(__file__).resolve().parent.parent)
    if kopf.returncode:
        print("  ?  Commit nicht lesbar — warte nicht, purge sofort")
        return
    sha = kopf.stdout.strip()
    ende = time.time() + minuten * 60
    while time.time() < ende:
        try:
            r = subprocess.run(["gh", "api",
                                "repos/Bubu89/full-page-pdf-snap/pages/builds/latest",
                                "-q", ".commit + \" \" + .status"],
                               capture_output=True, text=True, timeout=30)
            live, _, status = r.stdout.strip().partition(" ")
            if live == sha and status == "built":
                print(f"  OK Pages liefert {sha[:8]} aus")
                return
            print(f"  .. Pages steht auf {live[:8]} ({status}), erwartet {sha[:8]}")
        except Exception as e:
            print(f"  ?  Pages-Stand nicht abfragbar ({type(e).__name__}) — purge trotzdem")
            return
        time.sleep(15)
    print(f"  !  Pages hat {sha[:8]} nach {minuten} min nicht ausgeliefert — "
          "purge trotzdem, aber danach nachsehen")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--regel", action="store_true", help="Edge-TTL-Regel setzen")
    p.add_argument("--pruefen", action="store_true", help="nichts aendern")
    p.add_argument("--sofort", action="store_true",
                   help="nicht auf den Pages-Deploy warten")
    a = p.parse_args()

    if not (a.pruefen or a.sofort):
        print("Warte auf GitHub Pages")
        auf_pages_warten()

    tok = token()
    if a.regel:
        print("Edge-Haltedauer")
        regel_setzen(tok, a.pruefen)
    print("Cache leeren")
    leeren(tok, a.pruefen)
    zustand()
    print("\n  Gehoert nach jedem `git push`, sonst haelt der Edge bis zu "
          f"{EDGE_TTL // 3600} Stunden die alte Fassung.")
    print("  Danach `python3 tools/indexnow.py` — meldet die Aenderung an\n  Bing, Yandex, Seznam und Naver, statt auf den naechsten Crawl zu warten.")


if __name__ == "__main__":
    main()
