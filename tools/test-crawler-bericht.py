#!/usr/bin/env python3
"""Prueft die Auswertung von crawler-bericht.py ohne Cloudflare-Zugang.

Warum das noetig ist: Ohne gueltiges Token laesst sich der Bericht nicht
starten, und "der Code ist fertig" ist keine Aussage darueber, ob er richtig
rechnet. Hier wird die Antwort des Anbieters nachgestellt — mit Faellen, deren
Ergebnis feststeht — und die Auswertung dagegen laufen gelassen.

Damit ist geprueft: Einordnung, Herkunftsabgleich, Scan-Abzug, MCP-Zaehlung.
NICHT geprueft: die Abfrage selbst. Ob Cloudflare auf genau diese GraphQL-Frage
diese Felder liefert, zeigt erst der erste echte Lauf.

  python3 tools/test-crawler-bericht.py
"""
import importlib.util
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("cb", HIER / "crawler-bericht.py")
cb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cb)

fehler = []


def pruefe(name, ist, soll):
    ok = ist == soll
    print(f"  {'OK  ' if ok else 'FEHL'}  {name}")
    if not ok:
        print(f"          erwartet: {soll!r}")
        print(f"          bekommen: {ist!r}")
        fehler.append(name)


# --- Nachgestellte Antwort ---------------------------------------------------
# Echte IPs: eine aus der veroeffentlichten OpenAI-Liste, eine von Google mit
# gueltigem Rueckwaerts-DNS, eine beliebige fremde.
NETZE = cb.netze_laden()
OPENAI_IP = str(NETZE["OpenAI"][0].network_address + 1) if NETZE.get("OpenAI") else None
FREMD = "203.0.113.7"          # TEST-NET-3, gehoert niemandem

SUMMEN = [
    {"count": 40, "sum": {"edgeResponseBytes": 400000},
     "dimensions": {"userAgent": "Mozilla/5.0 (compatible; GPTBot/1.2)"}},
    {"count": 12, "sum": {"edgeResponseBytes": 90000},
     "dimensions": {"userAgent": "Mozilla/5.0 (compatible; ClaudeBot/1.0)"}},
    {"count": 5, "sum": {"edgeResponseBytes": 20000},
     "dimensions": {"userAgent": "Mozilla/5.0 (compatible; Googlebot/2.1)"}},
    {"count": 99, "sum": {"edgeResponseBytes": 800000},
     "dimensions": {"userAgent": "Mozilla/5.0 (Windows NT 10.0) Firefox/128.0"}},
]
PFADE = [
    {"count": 30, "dimensions": {"userAgent": "GPTBot/1.2",
                                 "clientRequestPath": "/measurements/"}},
    {"count": 10, "dimensions": {"userAgent": "GPTBot/1.2",
                                 "clientRequestPath": "/.env"}},
    {"count": 7, "dimensions": {"userAgent": "claude-code/2.1",
                                "clientRequestPath": "/mcp"}},
    {"count": 3, "dimensions": {"userAgent": "unbekannt",
                                "clientRequestPath": "/.well-known/mcp.json"}},
    {"count": 99, "dimensions": {"userAgent": "Firefox/128.0",
                                 "clientRequestPath": "/"}},
]
HERKUNFT = [
    # GPTBot aus echtem OpenAI-Netz -> bestaetigt
    {"count": 25, "dimensions": {"userAgent": "GPTBot/1.2", "clientIP": OPENAI_IP}},
    # GPTBot aus fremder Adresse -> Faelschung
    {"count": 15, "dimensions": {"userAgent": "GPTBot/1.2", "clientIP": FREMD}},
    # ClaudeBot ohne bestaetigte Herkunft
    {"count": 12, "dimensions": {"userAgent": "ClaudeBot/1.0", "clientIP": FREMD}},
]


def frag_attrappe(tok, abfrage, variablen):
    if "clientIP" in abfrage:
        return {"httpRequestsAdaptiveGroups": HERKUNFT}
    if "clientRequestPath" in abfrage:
        return {"httpRequestsAdaptiveGroups": PFADE}
    return {"httpRequestsAdaptiveGroups": SUMMEN}


print("=== A. Herkunftspruefung ===")
if OPENAI_IP:
    pruefe("Adresse aus OpenAI-Liste erkannt",
           cb.herkunft_pruefen(OPENAI_IP, NETZE), "OpenAI")
else:
    print("  ---   OpenAI-Liste nicht erreichbar, Fall uebersprungen")
pruefe("fremde Adresse nicht zugeordnet", cb.herkunft_pruefen(FREMD, NETZE), None)
pruefe("Adresse ohne Rueckwaerts-Eintrag", cb.herkunft_pruefen("8.8.8.8", NETZE), None)

print("\n=== B. MCP-Zaehlung ===")
mcp = cb.mcp_zaehlen(PFADE)
pruefe("Summe nur der MCP-Pfade", mcp["gesamt"], 10)
pruefe("Seitenabruf zaehlt nicht mit", "/" in mcp["je_pfad"], False)
pruefe("Aufrufer erfasst", mcp["je_aufrufer"].get("claude-code/2.1"), 7)

print("\n=== C. Gesamtauswertung ===")
echt = cb.frag
cb.frag = frag_attrappe
try:
    d = cb.erheben("attrappe", stunden=24)
finally:
    cb.frag = echt

hg = d["herkunft_geprueft"]
pruefe("GPTBot: bestaetigte Anfragen", hg.get("gptbot", {}).get("bestaetigt"), 25)
pruefe("GPTBot: unbestaetigte Anfragen", hg.get("gptbot", {}).get("unbestaetigt"), 15)
pruefe("ClaudeBot durchweg unbestaetigt",
       hg.get("claudebot", {}).get("bestaetigt"), 0)
pruefe("MCP-Aufrufe im Ergebnis", d["mcp_aufrufe"]["gesamt"], 10)

# Der Scan auf /.env muss von den Lesezahlen abgezogen sein — sonst blaeht ein
# Angreifer mit KI-Kennzeichen die Statistik auf.
gptbot = next((v for k, v in d.get("ki_systeme", {}).items() if "GPTBot" in k), None)
pruefe("GPTBot-Eintrag vorhanden", gptbot is not None, True)
if gptbot:
    pruefe("Zugangsdaten-Scan abgezogen (40 - 10)", gptbot["anfragen"], 30)

pruefe("Erhebungsdatum gesetzt", bool(d.get("gemessen_am")), True)

print("\n" + "=" * 58)
if fehler:
    print(f"{len(fehler)} FEHLER: " + ", ".join(fehler))
    sys.exit(1)
print("Auswertung rechnet richtig. Es fehlt nur der Zugang.")
