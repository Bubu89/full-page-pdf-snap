#!/usr/bin/env python3
"""Holt, welche KI-Systeme diese Seite tatsaechlich lesen, und legt es offen.

    python3 tools/crawler-bericht.py            # Zahlen holen und schreiben
    python3 tools/crawler-bericht.py --zeigen   # nur anzeigen

Warum das veroeffentlicht wird
------------------------------
Ueber KI-Crawler wird viel behauptet und wenig gezeigt. Wer eine Seite
betreibt, sieht in seinen eigenen Zahlen, welche Systeme wirklich vorbeikommen,
was sie holen und wie oft — und fast niemand macht diese Zahlen oeffentlich.
Hier passt es zum Rest der Seite: eine Angabe, die nachvollziehbar erhoben und
mit Datum versehen ist.

Was daran pruefbar ist, und was nicht
-------------------------------------
**Nicht pruefbar von aussen.** Das sind Zahlen aus der Analytik eines
Anbieters, abgerufen mit einem Token, das nur der Betreiber hat. Wer sie
nachrechnen will, kann es nicht — er kann nur die Methode lesen und dieselbe
Abfrage auf seiner eigenen Zone laufen lassen.

Deshalb steht die Abfrage im Klartext in dieser Datei, das Erhebungsfenster im
Ergebnis, und die Einschraenkung auf der Seite. Eine Zahl, die man nicht
nachrechnen kann, wird hier als solche gekennzeichnet — nicht weggelassen, aber
auch nicht als Messung ausgegeben.

**Ein User-Agent ist kein Ausweis.** `ClaudeBot` im Kopf einer Anfrage heisst
nicht, dass Anthropic sie gestellt hat. Am 3. August kamen fuenf Abrufe von
`/keys.json` mit einem ChatGPT-Kennzeichen und fuenf von `/terraform.tfvars`
mit einem Perplexity-Kennzeichen — das sind Scans nach Zugangsdaten, kein
Lesen. Solche Anfragen werden getrennt ausgewiesen und nicht mitgezaehlt.

Veralten
--------
Der Bericht traegt sein Erhebungsdatum. Aelter als `TAGE_FRISCH`, gilt er als
veraltet und die Seite sagt das selbst — eine Zahl ohne Datum wird
stillschweigend falsch, und das ist schlimmer als keine Zahl.
"""
import argparse
import collections
import datetime
import ipaddress
import json
import os
import socket
import subprocess
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
ZIEL = HIER / "docs" / "data" / "ki-crawler-aktuell.json"
ZONE = "0d7110c80d576750944785d0ae759209"
ITEM = "0fd9f886-bdb1-40a2-b364-24961e4d2253"
TAGE_FRISCH = 7

# Kennzeichen, die sich als KI-System ausgeben. Bewusst als Liste und nicht als
# Mustersuche auf „bot": sonst zaehlen Uptime-Pruefer und Linkchecker mit.
KI_KENNZEICHEN = {
    "claudebot": "ClaudeBot (Anthropic)",
    "claude-web": "Claude-Web (Anthropic)",
    "gptbot": "GPTBot (OpenAI)",
    "chatgpt-user": "ChatGPT-User (OpenAI, im Auftrag eines Menschen)",
    "oai-searchbot": "OAI-SearchBot (OpenAI)",
    "perplexitybot": "PerplexityBot",
    "perplexity-user": "Perplexity-User",
    "google-extended": "Google-Extended",
    "applebot-extended": "Applebot-Extended",
    "bytespider": "Bytespider (ByteDance)",
    "amazonbot": "Amazonbot",
    "ccbot": "CCBot (Common Crawl)",
    "meta-externalagent": "Meta-ExternalAgent",
    "cohere-ai": "cohere-ai",
    "diffbot": "Diffbot",
    "youbot": "YouBot",
}
# Klassische Suchmaschinen, zum Vergleich mitgezaehlt — die Frage „lesen KI-
# Systeme mehr als Suchmaschinen" ist ohne Bezugsgroesse nicht zu beantworten.
SUCH_KENNZEICHEN = {
    "googlebot": "Googlebot",
    "bingbot": "Bingbot",
    "yandexbot": "YandexBot",
    "duckduckbot": "DuckDuckBot",
    "applebot": "Applebot",
    "seznambot": "SeznamBot",
}
# Pfade, die niemand verlinkt hat und die nur ein Scanner sucht.
SCAN_MUSTER = (".env", ".git", "keys.json", ".tfvars", "wp-login", "wp-includes",
               "wp-admin", ".sql", "config.json", "credentials", ".aws", ".ssh")


# Mehrere Vault-Eintraege tragen Cloudflare-Token fuer diese Zone, mit
# unterschiedlichem Zuschnitt. Welcher davon Analytics lesen darf, steht in
# keinem Feld — es muss ausprobiert werden.
TOKEN_KURZ = ("c8b0a042", "0fd9f886", "84c722a0", "d0ba695f")


def _analytics_lesbar(tok):
    """Darf dieses Token die Zone-Analytik lesen?

    NICHT ueber /user/tokens/verify pruefen. Ein Token ohne User-Scope
    scheitert dort mit 401, obwohl es fuer Zone und Account gueltig ist — am
    15.08.2026 galten dadurch drei brauchbare Token faelschlich als widerrufen,
    darunter das einzige mit Analytics-Recht. Gefragt wird deshalb genau das,
    was gebraucht wird.
    """
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
    q = {"query": "query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                  "httpRequestsAdaptiveGroups(limit:1,filter:{datetime_geq:$s})"
                  "{count}}}}",
         "variables": {"z": ZONE, "s": seit}}
    r = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql", json.dumps(q).encode(),
        {"authorization": "Bearer " + tok, "content-type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=25) as a:
            return not (json.load(a).get("errors"))
    except Exception:
        return False


def token():
    aus_umgebung = os.environ.get("CF_API_TOKEN", "").strip()
    if aus_umgebung:
        return aus_umgebung
    try:
        sitzung = open("/dev/shm/bw-session").read().strip()
    except OSError:
        sys.exit("Vaultwarden nicht offen — vault-popup-unlock ausfuehren.")
    versucht = []
    for kennung in TOKEN_KURZ:
        r = subprocess.run(["bw", "get", "item", kennung, "--session", sitzung],
                           capture_output=True, text=True)
        if r.returncode:
            continue
        try:
            eintrag = json.loads(r.stdout)
        except Exception:
            continue
        tok = (eintrag.get("login") or {}).get("password", "").strip()
        if not tok:
            continue
        versucht.append(eintrag.get("name", kennung))
        if _analytics_lesbar(tok):
            return tok
    sys.exit(
        "Kein hinterlegtes Token darf die Zone-Analytik lesen.\n"
        "Geprueft: " + ", ".join(versucht or ["keines lesbar"]) + "\n\n"
        "Neues Token erzeugen im Konto Blockinhalt@gmail.com:\n"
        "  dash.cloudflare.com -> My Profile -> API Tokens -> Create Token\n"
        "  Berechtigung: Zone -> Analytics -> Read\n"
        "  Zone:         provinglab.dev\n\n"
        "Oder fuer einen einzelnen Lauf: export CF_API_TOKEN=<token>")


def frag(tok, abfrage, variablen):
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql",
        json.dumps({"query": abfrage, "variables": variablen}).encode(),
        {"authorization": "Bearer " + tok, "content-type": "application/json"})
    d = json.load(urllib.request.urlopen(req, timeout=40))
    if d.get("errors"):
        sys.exit("API: " + str([e.get("message") for e in d["errors"]])[:200])
    return d["data"]["viewer"]["zones"][0]


# ZWEI Abfragen, nicht eine. Der erste Entwurf gruppierte nach userAgent,
# Pfad und Status zugleich — das erzeugt tausende Gruppen, und bei `limit:200`
# fallen die selteneren Kennzeichen hinten heraus. Das Ergebnis meldete
# ClaudeBot mit 62 Anfragen und GPTBot mit **keiner**, waehrend das Dashboard
# zeitgleich 39 zeigte. Eine Rangliste, die stillschweigend abschneidet, sieht
# aus wie eine vollstaendige.
ABFRAGE_SUMMEN = ("query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                  "httpRequestsAdaptiveGroups(limit:500,filter:{datetime_geq:$s},"
                  "orderBy:[count_DESC]){count sum{edgeResponseBytes} "
                  "dimensions{userAgent}}}}}")
ABFRAGE_PFADE = ("query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                 "httpRequestsAdaptiveGroups(limit:500,filter:{datetime_geq:$s},"
                 "orderBy:[count_DESC]){count "
                 "dimensions{userAgent clientRequestPath}}}}}")
# Kennzeichen GEGEN Herkunft. Ohne diese Abfrage bleibt der Bericht bei dem
# stehen, was der Kopf der Anfrage behauptet — und genau das nennt die
# Einleitung dieser Datei selbst „kein Ausweis".
#
# Die Feldnamen sind von der API bestaetigt (15.08.2026): Cloudflare prueft das
# Schema VOR den Rechten. Ein erfundenes Feld liefert `unknown field "..."`,
# diese Abfrage liefert nur den Rechtefehler — also ist sie schemagueltig.
# Gegenprobe mit einem Token ohne Analytics-Recht gefahren, damit die Aussage
# nicht auf einem geglueckten Lauf beruht, sondern auf dem Unterschied.
ABFRAGE_HERKUNFT = ("query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
                    "httpRequestsAdaptiveGroups(limit:2000,filter:{datetime_geq:$s},"
                    "orderBy:[count_DESC]){count "
                    "dimensions{userAgent clientIP}}}}}")

# Pfade des MCP-Servers. Sie werden getrennt gezaehlt: ein Werkzeugaufruf ist
# kein Seitenabruf, und die Frage "wie oft nutzt jemand den Server" ist eine
# andere als "wie oft liest jemand die Seite".
MCP_PFADE = ("/mcp", "/.well-known/mcp.json", "/server.json")


# ---------------------------------------------------------------- Herkunft
#
# Zwei Wege, eine Anfrage dem genannten Anbieter zuzuordnen:
#
#   1. Veroeffentlichte Adressbereiche. OpenAI und Perplexity legen ihre
#      Crawler-Netze als JSON offen. Faellt die Herkunft hinein, ist die
#      Zuordnung gesichert.
#   2. Rueckwaerts-DNS MIT Vorwaerts-Gegenprobe, fuer Anbieter ohne Liste
#      (Anthropic, Google). Die IP muss auf einen Namen des Anbieters zeigen
#      UND dieser Name wieder auf dieselbe IP. Ohne die zweite Haelfte beweist
#      ein PTR-Eintrag nichts — den setzt, wer die Adresse kontrolliert.
#
# Was keinem der beiden Wege standhaelt, erscheint als "unbestaetigt". Es wird
# nicht weggelassen: eine Faelschung ist ein Befund, kein Messfehler.

IP_LISTEN = {
    "OpenAI": ("https://openai.com/gptbot.json",
               "https://openai.com/searchbot.json",
               "https://openai.com/chatgpt-user.json"),
    "Perplexity": ("https://www.perplexity.com/perplexitybot.json",
                   "https://www.perplexity.com/perplexity-user.json"),
}
RDNS_ENDUNGEN = {
    "anthropic.com": "Anthropic", "claudebot.com": "Anthropic",
    "googlebot.com": "Google", "google.com": "Google",
    "search.msn.com": "Microsoft", "applebot.apple.com": "Apple",
    "crawl.yahoo.net": "Yahoo",
}
# Welcher Anbieter steckt hinter einem Kennzeichen? Fuer den Abgleich
# Behauptung gegen Herkunft.
KENNZEICHEN_ANBIETER = {
    "claudebot": "Anthropic", "claude-web": "Anthropic",
    "gptbot": "OpenAI", "chatgpt-user": "OpenAI", "oai-searchbot": "OpenAI",
    "perplexitybot": "Perplexity", "perplexity-user": "Perplexity",
    "google-extended": "Google", "applebot-extended": "Apple",
    "googlebot": "Google", "bingbot": "Microsoft",
}


def netze_laden():
    netze = collections.defaultdict(list)
    for anbieter, urls in IP_LISTEN.items():
        for url in urls:
            try:
                with urllib.request.urlopen(url, timeout=20) as r:
                    d = json.load(r)
            except Exception:
                continue
            for e in d.get("prefixes", []):
                for s in ("ipv4Prefix", "ipv6Prefix"):
                    if e.get(s):
                        try:
                            netze[anbieter].append(ipaddress.ip_network(e[s]))
                        except ValueError:
                            pass
    return netze


_RDNS = {}


def _rdns(ip):
    if ip in _RDNS:
        return _RDNS[ip]
    ergebnis = None
    try:
        name = socket.gethostbyaddr(ip)[0].lower().rstrip(".")
        treffer = next((a for d, a in RDNS_ENDUNGEN.items()
                        if name == d or name.endswith("." + d)), None)
        if treffer and ip in {i[4][0] for i in socket.getaddrinfo(name, None)}:
            ergebnis = treffer
    except Exception:
        pass
    _RDNS[ip] = ergebnis
    return ergebnis


def herkunft_pruefen(ip, netze):
    """-> Anbietername oder None."""
    try:
        adr = ipaddress.ip_address(ip)
    except ValueError:
        return None
    for anbieter, liste in netze.items():
        if any(adr in n for n in liste):
            return anbieter
    return _rdns(ip)


def belege_sammeln(tok, seit_str, netze):
    """Je Kennzeichen: wie viele Anfragen kamen aus bestaetigter Herkunft?

    Rueckgabe: {kennzeichen_name: {"bestaetigt": n, "unbestaetigt": n,
                                   "fremde_herkunft": {anbieter: n}}}
    """
    try:
        zeilen = frag(tok, ABFRAGE_HERKUNFT,
                      {"z": ZONE, "s": seit_str})["httpRequestsAdaptiveGroups"]
    except Exception:
        return {}
    raus = {}
    for x in zeilen:
        ua = (x["dimensions"].get("userAgent") or "").lower()
        kenn = next((k for k in KENNZEICHEN_ANBIETER if k in ua), None)
        if not kenn:
            continue
        erwartet = KENNZEICHEN_ANBIETER[kenn]
        tatsaechlich = herkunft_pruefen(x["dimensions"].get("clientIP", ""), netze)
        e = raus.setdefault(kenn, {"erwartet": erwartet, "bestaetigt": 0,
                                   "unbestaetigt": 0, "fremde_herkunft": {}})
        if tatsaechlich == erwartet:
            e["bestaetigt"] += x["count"]
        else:
            e["unbestaetigt"] += x["count"]
            if tatsaechlich:
                e["fremde_herkunft"][tatsaechlich] = \
                    e["fremde_herkunft"].get(tatsaechlich, 0) + x["count"]
    return raus


def mcp_zaehlen(pfade_zeilen):
    """Werkzeugaufrufe am MCP-Server, getrennt nach Pfad und Aufrufer."""
    gesamt, je_pfad, je_ua = 0, {}, {}
    for x in pfade_zeilen:
        pfad = (x["dimensions"].get("clientRequestPath") or "").lower()
        if not any(pfad == m or pfad.startswith(m + "/") for m in MCP_PFADE):
            continue
        n = x["count"]
        gesamt += n
        je_pfad[pfad] = je_pfad.get(pfad, 0) + n
        ua = (x["dimensions"].get("userAgent") or "unbekannt")[:60]
        je_ua[ua] = je_ua.get(ua, 0) + n
    return {"gesamt": gesamt,
            "je_pfad": dict(sorted(je_pfad.items(), key=lambda i: -i[1])),
            "je_aufrufer": dict(sorted(je_ua.items(), key=lambda i: -i[1])[:10])}


def erheben(tok, stunden=23.5):
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=stunden))
    v = {"z": ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")}
    summen = frag(tok, ABFRAGE_SUMMEN, v)["httpRequestsAdaptiveGroups"]
    pfade = frag(tok, ABFRAGE_PFADE, v)["httpRequestsAdaptiveGroups"]
    netze = netze_laden()
    belege = belege_sammeln(tok, v["s"], netze)
    mcp = mcp_zaehlen(pfade)

    def einordnen(ua):
        u = ua.lower()
        for k, name in KI_KENNZEICHEN.items():
            if k in u:
                return "ki", name
        for k, name in SUCH_KENNZEICHEN.items():
            if k in u:
                return "suche", name
        return None, None

    ki, suche, scans = {}, {}, {}
    # Erst die Summen je Kennzeichen — vollstaendig, weil nur eine Dimension.
    for x in summen:
        art, name = einordnen(x["dimensions"]["userAgent"])
        if not art:
            continue
        eimer = ki if art == "ki" else suche
        e = eimer.setdefault(name, {"anfragen": 0, "bytes": 0, "pfade": {}})
        e["anfragen"] += x["count"]
        e["bytes"] += x["sum"]["edgeResponseBytes"]
    # Dann die Pfade. Scans werden hier erkannt und von der Summe abgezogen,
    # damit ein Scanner mit KI-Kennzeichen die Lesezahlen nicht aufblaeht.
    for x in pfade:
        art, name = einordnen(x["dimensions"]["userAgent"])
        if not art:
            continue
        pfad = x["dimensions"]["clientRequestPath"]
        if any(m in pfad.lower() for m in SCAN_MUSTER):
            e = scans.setdefault(name, {"anfragen": 0, "pfade": set()})
            e["anfragen"] += x["count"]
            e["pfade"].add(pfad)
            eimer = ki if art == "ki" else suche
            if name in eimer:
                eimer[name]["anfragen"] -= x["count"]
            continue
        eimer = ki if art == "ki" else suche
        if name in eimer:
            eimer[name]["pfade"][pfad] = eimer[name]["pfade"].get(pfad, 0) + x["count"]

    def aufraeumen(d):
        return {k: {"anfragen": v["anfragen"], "bytes": v["bytes"],
                    "top_pfade": dict(sorted(v["pfade"].items(),
                                             key=lambda i: -i[1])[:5])}
                for k, v in sorted(d.items(), key=lambda i: -i[1]["anfragen"])}

    return {
        # Der Schema-Pruefer verlangt ein Erhebungsdatum unter einem der
        # bekannten Namen — zu Recht: ein Datensatz ohne Datum wird
        # stillschweigend falsch.
        "gemessen_am": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d"),
        "stand": datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "fenster_stunden": round(stunden, 1),
        # Kennzeichen gegen Herkunft. Das Feld unterscheidet, was belegt ist,
        # von dem, was nur behauptet wurde — der Rest des Berichts kann das
        # nicht, weil er nur den Kopf der Anfrage kennt.
        "herkunft_geprueft": belege,
        # Werkzeugaufrufe am MCP-Server. Getrennt von den Leseabrufen, weil ein
        # Aufruf von /mcp keine gelesene Seite ist.
        "mcp_aufrufe": mcp,
        "lizenz": "CC BY 4.0 — https://creativecommons.org/licenses/by/4.0/",
        "methode": {
            "quelle": ("Cloudflare GraphQL Analytics, httpRequestsAdaptiveGroups, "
                       "Zone provinglab.dev. Beide Abfragen stehen im Klartext in "
                       "tools/crawler-bericht.py."),
            "control": ("Zwei getrennte Abfragen statt einer. Der erste Entwurf "
                        "gruppierte nach Kennzeichen, Pfad und Status zugleich und "
                        "schnitt bei limit:200 ab — er meldete ClaudeBot mit 62 und "
                        "GPTBot mit null, waehrend das Dashboard zeitgleich 39 zeigte. "
                        "Die Gegenprobe gegen die Oberflaeche des Anbieters deckte das auf."),
            "verification": ("Summen je Kennzeichen aus einer Abfrage mit nur einer "
                             "Dimension, Pfade aus einer zweiten. Scan-Anfragen werden "
                             "von den Lesezahlen abgezogen, nicht nur getrennt gezeigt."),
        },
        "nicht_pruefbar": (
            "Diese Zahlen stammen aus der Analytik des eigenen Anbieters und "
            "lassen sich von aussen nicht nachrechnen. Sie sind eine "
            "Selbstauskunft mit offengelegter Methode, keine Messung, die "
            "jemand wiederholen koennte. Ein User-Agent ist ausserdem kein "
            "Ausweis: er laesst sich frei setzen."),
        "ki_systeme": aufraeumen(ki),
        "suchmaschinen": aufraeumen(suche),
        "scans_mit_ki_kennzeichen": {
            k: {"anfragen": v["anfragen"], "gesuchte_pfade": sorted(v["pfade"])}
            for k, v in sorted(scans.items(), key=lambda i: -i[1]["anfragen"])},
        "summe": {
            "ki_anfragen": sum(v["anfragen"] for v in ki.values()),
            "ki_bytes": sum(v["bytes"] for v in ki.values()),
            "such_anfragen": sum(v["anfragen"] for v in suche.values()),
            "such_bytes": sum(v["bytes"] for v in suche.values()),
            "scan_anfragen": sum(v["anfragen"] for v in scans.values()),
        },
    }


def zeigen(d):
    s = d["summe"]
    print(f"  Stand {d['stand']}, Fenster {d['fenster_stunden']} h\n")
    print(f"  KI-Systeme      {s['ki_anfragen']:>5} Anfragen  "
          f"{s['ki_bytes']/1024:>9.0f} kB")
    for name, v in list(d["ki_systeme"].items())[:8]:
        print(f"    {name:<46} {v['anfragen']:>4}  {v['bytes']/1024:>8.0f} kB")
    print(f"\n  Suchmaschinen   {s['such_anfragen']:>5} Anfragen  "
          f"{s['such_bytes']/1024:>9.0f} kB")
    for name, v in list(d["suchmaschinen"].items())[:6]:
        print(f"    {name:<46} {v['anfragen']:>4}  {v['bytes']/1024:>8.0f} kB")
    if d["scans_mit_ki_kennzeichen"]:
        print(f"\n  Scans unter KI-Kennzeichen  {s['scan_anfragen']:>4} "
              "(nicht mitgezaehlt)")
        for name, v in d["scans_mit_ki_kennzeichen"].items():
            print(f"    {name:<46} {v['anfragen']:>4}  "
                  f"{', '.join(v['gesuchte_pfade'][:3])}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--zeigen", action="store_true", help="nichts schreiben")
    # erheben() konnte das Fenster schon immer, nur liess es sich von aussen
    # nicht setzen. Im Free-Plan reicht die Rueckschau ohnehin nur rund 24 h —
    # groessere Werte liefern dort weniger, nicht mehr.
    p.add_argument("--stunden", type=float, default=23.5,
                   help="Erhebungsfenster in Stunden (Standard 23.5). Cloudflare lehnt ab 24 h mit 'wider than 1d' ab.")
    a = p.parse_args()
    d = erheben(token(), stunden=a.stunden)
    zeigen(d)
    if not a.zeigen:
        ZIEL.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"\n  geschrieben: {ZIEL.relative_to(HIER)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
