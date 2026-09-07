#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sind die „Menschen" wirklich Menschen? (17.08.2026)

Ein User-Agent ist kein Ausweis. Die Gegenprobe fragt nach Merkmalen, die
sich schlechter faelschen lassen:

  1. **Wieviele verschiedene IPs?** 196 Abrufe von drei Adressen sind kein
     Publikum, sondern ein Werkzeug.
  2. **Welche Pfade?** Ein Mensch liest Seiten. Wer `/wp-admin/install.php`
     abklopft, sucht Luecken.
  3. **Welche Statuscodes?** Viele 404 heissen: da probiert jemand Pfade
     durch.
  4. **rDNS der haeufigsten IPs** — Rechenzentrum oder Zugangsanbieter?
"""
import collections
import datetime
import importlib.util
import re
import socket
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cb", HIER / "crawler-bericht.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

STUNDEN = 23.5
BROWSER = re.compile(r"mozilla/5\.0.*(chrome/|safari/|firefox/|edg/|opr/)", re.I)
BOTWORT = re.compile(
    r"bot|crawl|spider|scan|probe|monitor|liveness|health|check|registry|"
    r"curl|wget|python|httpx|node|go-http|java/|okhttp|scrapy|headless", re.I)

ABFRAGE_IP_PFAD = (
    "query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
    "httpRequestsAdaptiveGroups(limit:10000,filter:{datetime_geq:$s}){"
    "count dimensions{userAgent clientIP clientRequestPath "
    "edgeResponseStatus}}}}}")


def main():
    tok = cb.token()
    if not tok:
        print("Kein Token.")
        return 2
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=STUNDEN))
    v = {"z": cb.ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")}
    zeilen = cb.frag(tok, ABFRAGE_IP_PFAD, v)["httpRequestsAdaptiveGroups"]

    ips = collections.Counter()
    pfade = collections.Counter()
    codes = collections.Counter()
    gesamt = 0
    ip_pfade = collections.defaultdict(collections.Counter)
    for x in zeilen:
        ua = x["dimensions"].get("userAgent") or ""
        if not BROWSER.search(ua) or BOTWORT.search(ua):
            continue
        pfad = (x["dimensions"].get("clientRequestPath") or "")
        if pfad.lower().startswith("/mcp"):
            continue
        n = x["count"]
        ip = x["dimensions"].get("clientIP", "?")
        gesamt += n
        ips[ip] += n
        pfade[pfad] += n
        codes[str(x["dimensions"].get("edgeResponseStatus", "?"))] += n
        ip_pfade[ip][pfad] += n

    print(f"Browser-Kennung auf der Webseite: {gesamt} Anfragen "
          f"von {len(ips)} verschiedenen IPs\n")
    if not gesamt:
        return 0

    print("Verteilung — wieviele IPs machen wieviel aus?")
    lauf = 0
    for i, (ip, n) in enumerate(ips.most_common(10), 1):
        lauf += n
        try:
            name = socket.gethostbyaddr(ip)[0]
        except Exception:
            name = "kein rDNS"
        print(f"  {i:2d}. {ip:24} {n:5d} ({n / gesamt * 100:5.1f} %)  "
              f"kumuliert {lauf / gesamt * 100:5.1f} %   {name[:44]}")
    top3 = sum(n for _, n in ips.most_common(3))
    print(f"\n  Die drei haeufigsten IPs stellen {top3 / gesamt * 100:.1f} % "
          f"aller „menschlichen\" Anfragen.")

    print("\nStatuscodes:")
    for c, n in codes.most_common(8):
        print(f"  {c:5} {n:5d} ({n / gesamt * 100:5.1f} %)")

    print("\nHaeufigste Pfade:")
    for p, n in pfade.most_common(12):
        print(f"  {n:5d}  {p[:70]}")

    verdaechtig = sum(n for p, n in pfade.items() if any(
        m in p.lower() for m in ("wp-", "admin", ".env", ".git", "phpmyadmin",
                                 "xmlrpc", "config", "backup", ".php")))
    print(f"\n  Pfade mit Angriffsmuster: {verdaechtig} "
          f"({verdaechtig / gesamt * 100:.1f} %)")

    seiten = sum(n for p, n in pfade.items()
                 if p in ("/", "/index.html") or p.endswith(".html")
                 or p.count("/") <= 2 and "." not in p.split("/")[-1])
    print(f"  Abrufe echter Seiten:     {seiten} "
          f"({seiten / gesamt * 100:.1f} %)")
    return 0


def rechenzentrum_anteil():
    """Wieviel der Browser-Kennung kommt aus Rechenzentren?

    Ein Browser-User-Agent aus einer Cloud ist kein Mensch am Bildschirm,
    sondern ein Werkzeug, das sich als Browser ausgibt. Erkennung ueber
    rDNS-Merkmale der grossen Anbieter; ohne rDNS bleibt es unklar.
    """
    tok = cb.token()
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=STUNDEN))
    v = {"z": cb.ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")}
    zeilen = cb.frag(tok, ABFRAGE_IP_PFAD, v)["httpRequestsAdaptiveGroups"]
    RZ = ("googleusercontent", "amazonaws", "compute.internal", "azure",
          "your-server.de", "hetzner", "ovh", "digitalocean", "linode",
          "vultr", "contabo", "aliyun", "tencent", "oraclecloud",
          "scaleway", "hostwinds", "leaseweb", "datacenter", "cloud")
    ZUGANG = ("dip0.t-ipconnect", "t-ipconnect", "a1.net", "chello",
              "kabel", "dsl", "pool", "dyn", "cable", "liwest", "upcbusiness",
              "magenta", "vodafone", "telekom", "res.spectrum", "comcast")
    zaehl = {"Rechenzentrum": 0, "Zugangsanbieter": 0, "ohne rDNS": 0,
             "sonstiges": 0}
    gesehen = {}
    for x in zeilen:
        ua = x["dimensions"].get("userAgent") or ""
        if not BROWSER.search(ua) or BOTWORT.search(ua):
            continue
        pfad = (x["dimensions"].get("clientRequestPath") or "")
        if pfad.lower().startswith("/mcp"):
            continue
        ip = x["dimensions"].get("clientIP", "?")
        if ip not in gesehen:
            try:
                gesehen[ip] = socket.gethostbyaddr(ip)[0].lower()
            except Exception:
                gesehen[ip] = ""
        name = gesehen[ip]
        if not name:
            art = "ohne rDNS"
        elif any(m in name for m in RZ):
            art = "Rechenzentrum"
        elif any(m in name for m in ZUGANG):
            art = "Zugangsanbieter"
        else:
            art = "sonstiges"
        zaehl[art] += x["count"]
    ges = sum(zaehl.values()) or 1
    print("\nHerkunft der Browser-Kennung (rDNS):")
    for art, n in sorted(zaehl.items(), key=lambda i: -i[1]):
        print(f"  {art:18} {n:5d} ({n / ges * 100:5.1f} %)")
    print(f"\n  Belastbar Mensch (Zugangsanbieter): "
          f"{zaehl['Zugangsanbieter']} von {ges}")
    print(f"  Sicher KEIN Mensch (Rechenzentrum): {zaehl['Rechenzentrum']}")


if __name__ == "__main__":
    code = main()
    rechenzentrum_anteil()
    raise SystemExit(code)
