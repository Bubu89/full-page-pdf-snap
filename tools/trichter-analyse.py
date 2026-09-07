#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wer liest die Agenten-Beschreibungen — echte Agenten oder Monitore?
(17.08.2026)

Die Adoptionszahlen zeigen 150 Abrufe der Server-Karte gegen 16
Werkzeugaufrufe. Daraus liesse sich „viele schauen, wenige handeln"
folgern — aber nur, wenn die 150 von handlungsfaehigen Agenten kommen.
Kommen sie von denselben Registry-Crawlern, die auch `/mcp` anpingen,
gibt es diese Zielgruppe gar nicht, und jede Massnahme zur
„Umwandlung" ginge ins Leere.

Deshalb: Beschreibungspfade nach Aufrufer aufschluesseln, nicht nur
zaehlen.
"""
import collections
import datetime
import importlib.util
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cb", HIER / "crawler-bericht.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

STUNDEN = float(sys.argv[1]) if len(sys.argv) > 1 else 23.5

BESCHREIBUNG = (
    "/.well-known/mcp", "/.well-known/agent", "/agent.md", "/llms.txt",
    "/llms-full.txt", "/.well-known/agent-skills", "/server.json",
)
MONITORWORT = re.compile(
    r"monitor|liveness|health|probe|registry|scoring|witness|beat|scan|"
    r"sentinel|uptime|check|crawler", re.I)

ABFRAGE = ("query($z:String!,$s:Time!){viewer{zones(filter:{zoneTag:$z}){"
           "httpRequestsAdaptiveGroups(limit:10000,filter:{datetime_geq:$s}){"
           "count dimensions{userAgent clientRequestPath}}}}}")


def main():
    tok = cb.token()
    if not tok:
        print("Kein Token.")
        return 2
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=STUNDEN))
    zeilen = cb.frag(tok, ABFRAGE, {
        "z": cb.ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")})[
            "httpRequestsAdaptiveGroups"]

    je_aufrufer = collections.Counter()
    je_pfad = collections.Counter()
    monitor, sonstige = 0, 0
    sonstige_ua = collections.Counter()
    for x in zeilen:
        pfad = (x["dimensions"].get("clientRequestPath") or "")
        if not any(pfad.lower().startswith(b) for b in BESCHREIBUNG):
            continue
        ua = (x["dimensions"].get("userAgent") or "(ohne)")
        n = x["count"]
        je_aufrufer[ua[:58]] += n
        je_pfad[pfad] += n
        if MONITORWORT.search(ua):
            monitor += n
        else:
            sonstige += n
            sonstige_ua[ua[:58]] += n

    gesamt = monitor + sonstige
    print(f"Abrufe der Agenten-Beschreibungen: {gesamt} "
          f"(Fenster {STUNDEN} h)\n")
    if not gesamt:
        return 0
    print(f"  Monitore/Registries : {monitor:5d} "
          f"({monitor / gesamt * 100:5.1f} %)")
    print(f"  alles uebrige       : {sonstige:5d} "
          f"({sonstige / gesamt * 100:5.1f} %)\n")

    print("Haeufigste Aufrufer insgesamt:")
    for ua, n in je_aufrufer.most_common(12):
        kennz = "MON" if MONITORWORT.search(ua) else "   "
        print(f"  {kennz} {n:5d}  {ua}")

    print("\nNicht als Monitor erkennbar — die moegliche Zielgruppe:")
    for ua, n in sonstige_ua.most_common(12):
        print(f"      {n:5d}  {ua}")

    print("\nMeistgelesene Beschreibungen:")
    for p, n in je_pfad.most_common(10):
        print(f"      {n:5d}  {p}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
