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
import datetime
import json
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


def token():
    try:
        sitzung = open("/dev/shm/bw-session").read().strip()
    except OSError:
        sys.exit("Vaultwarden nicht offen — vault-popup-unlock ausfuehren.")
    r = subprocess.run(["bw", "get", "item", ITEM, "--session", sitzung],
                       capture_output=True, text=True)
    if r.returncode:
        sys.exit("Token nicht lesbar.")
    return (json.loads(r.stdout).get("login") or {}).get("password", "").strip()


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


def erheben(tok, stunden=23.9):
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=stunden))
    v = {"z": ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")}
    summen = frag(tok, ABFRAGE_SUMMEN, v)["httpRequestsAdaptiveGroups"]
    pfade = frag(tok, ABFRAGE_PFADE, v)["httpRequestsAdaptiveGroups"]

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
    a = p.parse_args()
    d = erheben(token())
    zeigen(d)
    if not a.zeigen:
        ZIEL.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        print(f"\n  geschrieben: {ZIEL.relative_to(HIER)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
