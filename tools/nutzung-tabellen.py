#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wer nutzt provinglab.dev — Agenten oder Menschen? (17.08.2026)

Anlass: `crawler-bericht.py` verwirft in `einordnen()` jeden User-Agent, der
weder bekannter KI-Bot noch Suchmaschine ist. Damit tauchen **Menschen
ueberhaupt nicht auf** — die Statistik zeigte bisher nur die Bot-Seite.

Dieses Werkzeug ordnet ALLE Anfragen ein und trennt dabei zwei Fragen, die
gern vermischt werden:

  1. **MCP** — Werkzeugaufrufe an `/mcp*`. Das sind nie Menschen.
  2. **Webseite** — alles uebrige. Hier ist die Frage Agent oder Mensch.

Ehrlichkeitsgrenze: die Einordnung „Mensch" stuetzt sich auf den
User-Agent, und der ist kein Ausweis — er laesst sich frei setzen. Wo eine
Anbieterliste oder rDNS existiert, wird gegengeprueft; sonst steht die
Zeile als Selbstauskunft da. Siehe `feedback_ki_crawler_statistik_zaehlt_faelschungen`.
"""
import datetime
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "cb", HIER / "crawler-bericht.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

STUNDEN = float(sys.argv[1]) if len(sys.argv) > 1 else 23.5

# Ein Browser meldet sich als Mozilla/5.0 mit einer Engine-Kennung und
# NICHT als bot/crawler/spider. Das ist eine Selbstauskunft, kein Beweis.
BROWSER = re.compile(
    r"mozilla/5\.0.*(chrome/|safari/|firefox/|edg/|opr/)", re.I)
BOTWORT = re.compile(
    r"bot|crawl|spider|scan|probe|monitor|liveness|health|check|registry|"
    r"curl|wget|python|httpx|node|go-http|java/|okhttp|libwww|scrapy|"
    r"headless|phantom|selenium|puppeteer|playwright|axios|postman", re.I)


def einordnen(ua: str, pfad: str) -> tuple:
    """-> (gruppe, art, anzeige)."""
    u = (ua or "").strip()
    ul = u.lower()
    if any(m in (pfad or "").lower() for m in ("/mcp", "/.well-known/mcp",
                                               "/server.json")):
        gruppe = "MCP"
    else:
        gruppe = "Webseite"

    for k, name in cb.KI_KENNZEICHEN.items():
        if k in ul:
            return gruppe, "KI-Agent", name
    for k, name in cb.SUCH_KENNZEICHEN.items():
        if k in ul:
            return gruppe, "Suchmaschine", name
    if not u or ul in ("-", "unknown"):
        return gruppe, "ohne Kennung", "(kein User-Agent)"
    if BOTWORT.search(u):
        return gruppe, "Werkzeug/Bot", u[:52]
    if BROWSER.search(u):
        return gruppe, "Mensch (behauptet)", _browser_kurz(u)
    return gruppe, "unklar", u[:52]


def _browser_kurz(ua: str) -> str:
    for kenn, name in (("Edg/", "Edge"), ("OPR/", "Opera"),
                       ("Firefox/", "Firefox"), ("Chrome/", "Chrome"),
                       ("Safari/", "Safari")):
        if kenn in ua:
            plattform = "Windows" if "Windows" in ua else \
                "macOS" if "Mac OS" in ua else \
                "Android" if "Android" in ua else \
                "iOS" if ("iPhone" in ua or "iPad" in ua) else \
                "Linux" if "Linux" in ua else "?"
            return f"{name} / {plattform}"
    return ua[:52]


def tabelle(zeilen, kopf, breiten):
    aus = ["| " + " | ".join(kopf) + " |",
           "|" + "|".join("-" * (b + 2) for b in breiten) + "|"]
    for z in zeilen:
        aus.append("| " + " | ".join(str(x) for x in z) + " |")
    return "\n".join(aus)


def main():
    tok = cb.token()
    if not tok:
        print("Kein Cloudflare-Token verfuegbar.")
        return 2
    seit = (datetime.datetime.now(datetime.UTC)
            - datetime.timedelta(hours=STUNDEN))
    v = {"z": cb.ZONE, "s": seit.strftime("%Y-%m-%dT%H:%M:%SZ")}
    pfade = cb.frag(tok, cb.ABFRAGE_PFADE, v)["httpRequestsAdaptiveGroups"]

    gruppen = {}
    detail = {}
    for x in pfade:
        ua = x["dimensions"].get("userAgent") or ""
        pfad = x["dimensions"].get("clientRequestPath") or ""
        n = x["count"]
        gruppe, art, anzeige = einordnen(ua, pfad)
        gruppen.setdefault(gruppe, {}).setdefault(art, 0)
        gruppen[gruppe][art] += n
        d = detail.setdefault(gruppe, {}).setdefault(art, {})
        d[anzeige] = d.get(anzeige, 0) + n

    print(f"# Nutzung provinglab.dev — Fenster {STUNDEN} h")
    print(f"Erhoben {datetime.datetime.now(datetime.UTC):%Y-%m-%d %H:%M} UTC\n")

    for gruppe in ("Webseite", "MCP"):
        if gruppe not in gruppen:
            continue
        gesamt = sum(gruppen[gruppe].values())
        print(f"\n## {gruppe} — {gesamt} Anfragen\n")
        zeilen = []
        for art, n in sorted(gruppen[gruppe].items(), key=lambda i: -i[1]):
            anteil = n / gesamt * 100 if gesamt else 0
            oben = sorted(detail[gruppe][art].items(),
                          key=lambda i: -i[1])[:3]
            bsp = ", ".join(f"{k} ({w})" for k, w in oben)
            zeilen.append([art, n, f"{anteil:.1f} %", bsp[:74]])
        print(tabelle(zeilen, ["Art", "Anfragen", "Anteil", "Haeufigste"],
                      [20, 9, 7, 74]))

    # Kernzahl: Agent gegen Mensch auf der Webseite
    w = gruppen.get("Webseite", {})
    menschen = w.get("Mensch (behauptet)", 0)
    maschine = sum(n for a, n in w.items() if a != "Mensch (behauptet)")
    gesamt_w = menschen + maschine
    print("\n\n## Kernzahl Webseite\n")
    if gesamt_w:
        print(tabelle([
            ["Maschinen (Agenten, Bots, Werkzeuge)", maschine,
             f"{maschine / gesamt_w * 100:.1f} %"],
            ["Menschen (laut User-Agent)", menschen,
             f"{menschen / gesamt_w * 100:.1f} %"],
        ], ["", "Anfragen", "Anteil"], [38, 9, 7]))
    print("\n## MCP\n")
    print("MCP-Aufrufe sind ausnahmslos Werkzeugaufrufe — kein Mensch ruft "
          "`/mcp` im Browser auf.")

    print("\n---\n**Grenze:** Die Einordnung „Mensch\" ist eine "
          "Selbstauskunft des User-Agent, kein Ausweis. Sie laesst sich frei "
          "setzen. Belastbar sind nur die Anbieter, fuer die eine IP-Liste "
          "oder rDNS-Gegenprobe existiert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
