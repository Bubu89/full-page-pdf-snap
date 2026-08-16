#!/usr/bin/env python3
"""Gesamtabnahme von provinglab.dev — ein Lauf, eine Note, ein Verlauf.

Das Problem, das diese Datei loest: Im Ordner liegen fuenfzehn Pruefwerkzeuge.
Jedes fuer sich ist gut, zusammen laufen sie nie. Wer wissen will, ob die Seite
diese Woche besser dasteht als letzte, muesste fuenfzehn Aufrufe machen und die
Ergebnisse im Kopf behalten.

Hier laufen sie in einem Durchgang, das Ergebnis wird als Zeitreihe abgelegt,
und der Vergleich zum letzten Lauf steht in der Ausgabe. Damit ist "besser
geworden" eine Zahl und keine Empfindung.

Zwei Gruppen:
  OHNE ZUGANG   laufen immer — von aussen pruefbar, jeder kann sie nachstellen
  MIT ZUGANG    brauchen ein Cloudflare-Token; ohne Token uebersprungen,
                NICHT als bestanden gewertet

  python3 tools/abnahme.py               # voller Lauf
  python3 tools/abnahme.py --schnell     # nur die Pruefungen ohne Netzlast
  python3 tools/abnahme.py --verlauf     # Zeitreihe der letzten Laeufe
  python3 tools/abnahme.py --offen       # nur was zu tun ist
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
WERKZEUGE = WURZEL / "tools"
# NICHT nach docs/data/: dort liegen die veroeffentlichten Datensaetze, die
# gegen schema.json geprueft werden. Der Verlauf ist eine Liste und liess
# daten-pruefen.py mit AttributeError abbrechen — die Abnahme haette sich
# selbst durchgefallen. Ausserdem ist er interner Arbeitsstand, kein Messwert
# zur Veroeffentlichung. (14.08.2026)
VERLAUF = WURZEL / "tools" / ".abnahme-verlauf.json"
SEITE = "https://provinglab.dev"
VERLAUF_MAX = 200

# (Kennung, Beschriftung, Aufruf, braucht_token, Gewicht)
#
# Gewicht sagt, was ein Fehlschlag kostet. Ein toter Link ist aergerlich, ein
# nicht erreichbarer MCP-Server macht die Seite fuer Agenten wertlos — das darf
# nicht gleich zaehlen.
PRUEFUNGEN = [
    ("erreichbar",  "Seite erreichbar",          None,                      False, 3),
    ("mcp",         "MCP-Server antwortet",      None,                      False, 3),
    ("mcp_karte",   "MCP-Serverkarte gueltig",   None,                      False, 2),
    ("robots",      "robots.txt + llms.txt",     None,                      False, 1),
    ("sitemap",     "Sitemap vollstaendig",      None,                      False, 2),
    ("kopfzeilen",  "Sicherheits-Kopfzeilen",    None,                      False, 1),
    ("daten",       "Datensaetze gegen Schema",  "daten-pruefen.py",        False, 2),
    ("links",       "Links erreichbar",          "links-pruefen.py",        False, 2),
    ("seo",         "Auffindbarkeit",            "seo-pruefen.py",          False, 1),
    ("sprachen",    "Sprachfassungen vollstaendig", "sprachen-pruefen.py",  False, 1),
    ("registry",    "MCP-Registry aktuell",      "registry-stand.py",       False, 1),
    ("fristen",     "Fristen nicht faellig",     "fristen-pruefen.py",      False, 2),
    ("agenten",     "Werkzeuge fuer Agenten",    "agenten-abnahme.py",      False, 2),
    # Faengt den Unfall ab, der die Neun-Sprachen-Umstellung bedroht: einen
    # veralteten Builder als Textquelle nehmen und damit Inhalt loeschen.
    ("drift",       "Builder passen zu den Seiten", "builder-drift.py",     False, 3),
    # Faengt Seiten ab, die veroeffentlicht sind, aber in keinem Verzeichnis
    # stehen — /how-to/ hatte drei davon und antwortete selbst mit 404.
    ("systematik",  "Jede Seite in ihrem Verzeichnis", "seiten-systematik.py", False, 2),
    # Rechnet die Zugriffsauswertung richtig? Laeuft OHNE Token gegen eine
    # nachgestellte Anbieter-Antwort — sonst bliebe die Logik ungeprueft,
    # solange kein Zugang da ist, und der erste echte Lauf waere zugleich
    # der erste Test.
    ("auswertung",  "Zugriffsauswertung rechnet", "test-crawler-bericht.py", False, 2),
    ("crawler",     "Zugriffe erhoben",          "crawler-bericht.py",      True,  1),
    ("cloudflare",  "Cloudflare-Einstellungen",  "cloudflare-audit.py",     True,  1),
]


# --------------------------------------------------------- Pruefungen von aussen

def _hole(pfad, methode="GET", koerper=None, timeout=25):
    req = urllib.request.Request(
        SEITE + pfad, method=methode,
        data=json.dumps(koerper).encode() if koerper else None,
        headers={"Content-Type": "application/json"} if koerper else {})
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(), dict(r.headers), (time.monotonic() - t0) * 1000
    except urllib.error.HTTPError as e:
        return e.code, e.read(), dict(e.headers), (time.monotonic() - t0) * 1000
    except Exception as e:
        return 0, str(e).encode(), {}, (time.monotonic() - t0) * 1000


def pruef_erreichbar():
    code, koerper, kopf, ms = _hole("/")
    if code != 200:
        return False, f"HTTP {code}"
    hinweise = []
    if kopf.get("cf-cache-status") not in ("HIT", "REVALIDATED"):
        hinweise.append(f"Cache {kopf.get('cf-cache-status', '?')}")
    return True, f"{len(koerper)} Bytes, {ms:.0f} ms{', ' + ', '.join(hinweise) if hinweise else ''}"


def pruef_mcp():
    """Nicht nur erreichbar: der Server muss auch Werkzeuge anbieten.

    Ein `initialize`, das antwortet, waehrend `tools/list` leer bleibt, sieht
    im Betrieb gesund aus und ist fuer einen Agenten trotzdem nutzlos.
    """
    code, koerper, _, ms = _hole("/mcp", "POST", {
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                   "clientInfo": {"name": "abnahme", "version": "1"}}})
    if code != 200:
        return False, f"initialize -> HTTP {code}"
    try:
        d = json.loads(koerper)
        version = d["result"]["serverInfo"]["version"]
    except Exception as e:
        return False, f"Antwort unlesbar: {e}"
    code2, koerper2, _, _ = _hole("/mcp", "POST", {
        "jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    try:
        werkzeuge = json.loads(koerper2)["result"]["tools"]
    except Exception:
        return False, f"v{version}, aber tools/list liefert nichts"
    if not werkzeuge:
        return False, f"v{version}, aber kein Werkzeug angeboten"
    return True, f"v{version}, {len(werkzeuge)} Werkzeuge, {ms:.0f} ms"


def pruef_mcp_karte():
    """Die Serverkarte muss auf den Endpunkt zeigen, der wirklich antwortet."""
    code, koerper, _, _ = _hole("/.well-known/mcp.json")
    if code != 200:
        return False, f"HTTP {code}"
    try:
        d = json.loads(koerper)
    except Exception as e:
        return False, f"kein gueltiges JSON: {e}"
    fehlt = [f for f in ("serverInfo", "transport", "tools") if f not in d]
    if fehlt:
        return False, "fehlende Felder: " + ", ".join(fehlt)
    ziel = (d.get("transport") or {}).get("endpoint", "")
    if not ziel.startswith(SEITE):
        return False, f"Endpunkt zeigt woandershin: {ziel}"
    return True, f"{len(d.get('tools', []))} Werkzeuge beschrieben, Endpunkt stimmt"


def pruef_robots():
    fehlt, hinweise = [], []
    for pfad in ("/robots.txt", "/llms.txt"):
        code, koerper, _, _ = _hole(pfad)
        if code != 200:
            fehlt.append(pfad)
        elif pfad == "/robots.txt":
            text = koerper.decode("utf-8", "replace")
            if "Content-Signal" not in text:
                hinweise.append("kein Content-Signal")
            if "Sitemap:" not in text:
                hinweise.append("kein Sitemap-Verweis")
    if fehlt:
        return False, "fehlt: " + ", ".join(fehlt)
    return (not hinweise), ("in Ordnung" if not hinweise else ", ".join(hinweise))


def pruef_sitemap():
    """Eine Sitemap mit toten Adressen schadet mehr als keine — Suchmaschinen
    werten wiederholte 404 als Qualitaetsmangel der ganzen Domain."""
    code, koerper, _, _ = _hole("/sitemap.xml")
    if code != 200:
        return False, f"HTTP {code}"
    adressen = re.findall(r"<loc>([^<]+)</loc>", koerper.decode("utf-8", "replace"))
    if not adressen:
        return False, "keine Eintraege"
    tot = []
    for u in adressen[:40]:
        pfad = u.replace(SEITE, "") or "/"
        c, _, _, _ = _hole(pfad, timeout=15)
        if c >= 400 or c == 0:
            tot.append(f"{pfad} ({c})")
    if tot:
        return False, f"{len(adressen)} Adressen, tot: " + ", ".join(tot[:4])
    return True, f"{len(adressen)} Adressen, davon {min(40, len(adressen))} geprueft, alle erreichbar"


def pruef_kopfzeilen():
    _, _, kopf, _ = _hole("/")
    k = {a.lower(): b for a, b in kopf.items()}
    fehlt = [n for n in ("strict-transport-security", "x-content-type-options",
                         "referrer-policy", "content-security-policy")
             if n not in k]
    if fehlt:
        return False, "fehlt: " + ", ".join(fehlt)
    return True, "alle vier gesetzt"


EIGEN = {"erreichbar": pruef_erreichbar, "mcp": pruef_mcp,
         "mcp_karte": pruef_mcp_karte, "robots": pruef_robots,
         "sitemap": pruef_sitemap, "kopfzeilen": pruef_kopfzeilen}


# ------------------------------------------------------------ Werkzeuge aufrufen

def werkzeug_laufen(datei, timeout=240):
    pfad = WERKZEUGE / datei
    if not pfad.exists():
        return None, f"{datei} fehlt"
    try:
        p = subprocess.run([sys.executable, str(pfad)], capture_output=True,
                           text=True, timeout=timeout, cwd=str(WURZEL))
    except subprocess.TimeoutExpired:
        return False, f"Zeitueberschreitung nach {timeout}s"
    ausgabe = (p.stdout + p.stderr).strip().splitlines()
    letzte = next((z.strip() for z in reversed(ausgabe) if z.strip()), "")
    return p.returncode == 0, letzte[:110]


ZONE = "0d7110c80d576750944785d0ae759209"          # provinglab.dev
TOKEN_KURZ = ("c8b0a042", "0fd9f886", "84c722a0", "d0ba695f")


def token_da():
    """Ist ein Token da, das die Zone-Analytik LESEN darf?

    Zwei Irrwege lagen hier schon:
      1. Am Vorhandensein einer Vault-Session festmachen — meldete "vorhanden",
         waehrend das Token widerrufen war.
      2. Gegen /user/tokens/verify pruefen — meldete "fehlt", obwohl ein
         gueltiges Token vorlag: ohne User-Scope antwortet verify mit 401,
         auch wenn Zone und Account erreichbar sind. So galten am 15.08.2026
         drei brauchbare Token als tot, darunter das einzige mit
         Analytics-Recht.
    Gefragt wird deshalb genau das, was die beiden Pruefungen brauchen.
    """
    kandidaten = []
    aus_umgebung = os.environ.get("CF_API_TOKEN", "").strip()
    if aus_umgebung:
        kandidaten.append(aus_umgebung)
    sitzung = Path("/dev/shm/bw-session")
    if sitzung.exists():
        s = sitzung.read_text().strip()
        for kennung in TOKEN_KURZ:
            try:
                r = subprocess.run(["bw", "get", "password", kennung,
                                    "--session", s],
                                   capture_output=True, text=True, timeout=60)
                if r.returncode == 0 and r.stdout.strip():
                    kandidaten.append(r.stdout.strip())
            except Exception:
                pass
    seit = (datetime.now(timezone.utc) - timedelta(hours=1)
            ).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = {"query": "query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                  "httpRequestsAdaptiveGroups(limit:1,filter:{datetime_geq:$s})"
                  "{count}}}}",
         "variables": {"z": ZONE, "s": seit}}
    for tok in kandidaten:
        req = urllib.request.Request(
            "https://api.cloudflare.com/client/v4/graphql",
            json.dumps(q).encode(),
            {"authorization": "Bearer " + tok,
             "content-type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=25) as r:
                if not json.load(r).get("errors"):
                    os.environ["CF_API_TOKEN"] = tok     # Werkzeuge erben ihn
                    return True
        except Exception:
            continue
    return False


# ----------------------------------------------------------------------- Verlauf

def verlauf_laden():
    try:
        return json.loads(VERLAUF.read_text(encoding="utf-8"))
    except Exception:
        return []


def verlauf_sichern(eintrag):
    d = verlauf_laden()
    d.append(eintrag)
    d = d[-VERLAUF_MAX:]
    VERLAUF.parent.mkdir(parents=True, exist_ok=True)
    tmp = VERLAUF.with_suffix(".tmp")
    tmp.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, VERLAUF)


def note(ergebnisse):
    """Erreichte durch moegliche Gewichtspunkte. Uebersprungenes zaehlt weder
    im Zaehler noch im Nenner — sonst sagt die Note etwas ueber die
    Token-Lage statt ueber die Seite."""
    erreicht = moeglich = 0
    for k, e in ergebnisse.items():
        if e["stand"] == "uebersprungen":
            continue
        gew = e["gewicht"]
        moeglich += gew
        if e["stand"] == "ok":
            erreicht += gew
    return (round(100.0 * erreicht / moeglich, 1) if moeglich else 0.0,
            erreicht, moeglich)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schnell", action="store_true",
                    help="nur die Pruefungen ohne Werkzeugaufrufe")
    ap.add_argument("--verlauf", action="store_true", help="Zeitreihe anzeigen")
    ap.add_argument("--offen", action="store_true", help="nur Offenes")
    a = ap.parse_args()

    if a.verlauf:
        d = verlauf_laden()
        if not d:
            print("Noch kein Lauf abgelegt.")
            return 0
        print(f"{'Zeitpunkt':<18}{'Note':>7}{'ok':>5}{'fehl':>6}{'ueber':>7}   Veraenderung")
        vorher = None
        for e in d[-25:]:
            pfeil = ""
            if vorher is not None:
                diff = e["note"] - vorher
                pfeil = f"{diff:+.1f}" if abs(diff) >= 0.05 else "gleich"
            print(f"{e['zeit'][:16]:<18}{e['note']:>6.1f}%{e['ok']:>5}"
                  f"{e['fehl']:>6}{e['uebersprungen']:>7}   {pfeil}")
            vorher = e["note"]
        return 0

    hat_token = token_da()
    print(f"Abnahme provinglab.dev — {datetime.now(timezone.utc):%d.%m.%Y %H:%M} UTC")
    print(f"Cloudflare-Zugang: {'vorhanden' if hat_token else 'FEHLT — 2 Pruefungen uebersprungen'}\n")

    ergebnisse = {}
    for kennung, titel, datei, braucht_token, gewicht in PRUEFUNGEN:
        if braucht_token and not hat_token:
            ergebnisse[kennung] = {"titel": titel, "stand": "uebersprungen",
                                   "detail": "kein Cloudflare-Token", "gewicht": gewicht}
            print(f"  ---  {titel:<32} kein Cloudflare-Token")
            continue
        if datei and a.schnell:
            ergebnisse[kennung] = {"titel": titel, "stand": "uebersprungen",
                                   "detail": "--schnell", "gewicht": gewicht}
            continue
        if kennung in EIGEN:
            try:
                ok, detail = EIGEN[kennung]()
            except Exception as e:
                ok, detail = False, f"Ausnahme: {e}"
        else:
            ok, detail = werkzeug_laufen(datei)
            if ok is None:
                ergebnisse[kennung] = {"titel": titel, "stand": "uebersprungen",
                                       "detail": detail, "gewicht": gewicht}
                print(f"  ---  {titel:<32} {detail}")
                continue
        ergebnisse[kennung] = {"titel": titel, "stand": "ok" if ok else "fehl",
                               "detail": detail, "gewicht": gewicht}
        print(f"  {'OK ' if ok else 'FEHL'} {titel:<32} {detail}")

    prozent, erreicht, moeglich = note(ergebnisse)
    anzahl = {s: sum(1 for e in ergebnisse.values() if e["stand"] == s)
              for s in ("ok", "fehl", "uebersprungen")}

    eintrag = {"zeit": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
               "note": prozent, "punkte": erreicht, "moeglich": moeglich,
               "ok": anzahl["ok"], "fehl": anzahl["fehl"],
               "uebersprungen": anzahl["uebersprungen"],
               "einzeln": {k: {"stand": v["stand"], "detail": v["detail"]}
                           for k, v in ergebnisse.items()}}

    alt = verlauf_laden()
    print("\n" + "=" * 66)
    zeile = (f"Note {prozent:.1f} %  ({erreicht}/{moeglich} Gewichtspunkte)  "
             f"ok {anzahl['ok']} · fehl {anzahl['fehl']} · "
             f"uebersprungen {anzahl['uebersprungen']}")
    print(zeile)
    if alt:
        diff = prozent - alt[-1]["note"]
        wohin = "besser" if diff > 0 else ("schlechter" if diff < 0 else "gleich")
        print(f"Gegenueber {alt[-1]['zeit'][:10]}: {diff:+.1f} Punkte ({wohin})")
        # Was sich einzeln geaendert hat — das ist die eigentliche Auskunft.
        frueher = alt[-1].get("einzeln", {})
        for k, v in ergebnisse.items():
            vorher = (frueher.get(k) or {}).get("stand")
            if vorher and vorher != v["stand"]:
                print(f"   {v['titel']}: {vorher} -> {v['stand']}")
    print("=" * 66)

    offen = [(k, v) for k, v in ergebnisse.items() if v["stand"] == "fehl"]
    if offen:
        print("\nZu tun, nach Gewicht:")
        for k, v in sorted(offen, key=lambda i: -i[1]["gewicht"]):
            print(f"  [{v['gewicht']}] {v['titel']}: {v['detail']}")
    uebersprungen = [v for v in ergebnisse.values() if v["stand"] == "uebersprungen"]
    if uebersprungen:
        print(f"\nNicht geprueft ({len(uebersprungen)}): "
              + ", ".join(v["titel"] for v in uebersprungen))
        print("  Diese zaehlen weder positiv noch negativ in die Note.")

    if not a.offen:
        verlauf_sichern(eintrag)
        print(f"\nLauf abgelegt in {VERLAUF.relative_to(WURZEL)} "
              f"({len(verlauf_laden())} Laeufe).")
    return 1 if offen else 0


if __name__ == "__main__":
    sys.exit(main())
