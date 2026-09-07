#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sagen alle Beschreibungen dasselbe zuerst? (17.08.2026)

Ein MCP-Server beschreibt sich an drei Stellen, und sie werden getrennt
gepflegt:

  1. `server.json`        — was die Registry ausliefert, und damit das,
                            was jedes Verzeichnis kopiert
  2. server-card.json     — was ein Agent vor dem Verbinden liest
  3. `instructions`       — was er nach dem Verbinden liest

Am 17.08.2026 sagten (1) „Cite or capture a web page" und (2)/(3)
„Measurement datasets and reproducible methods". Ein Agent, den die
Registry mit der Aufgabe angelockt hatte, las nach dem Verbinden etwas
anderes — und schloss daraus, er sei falsch. Ein Trichterbruch genau an
der Uebergabestelle, und der teuerste, weil der Agent schon da ist.

Dieser Test haelt fest, dass alle drei mit derselben Aufgabe beginnen.
Er prueft KEINE Wortgleichheit — die Texte duerfen unterschiedlich lang
und unterschiedlich ausfuehrlich sein. Er prueft den ersten Satz.
"""
import json
import pathlib
import re
import sys

WURZEL = pathlib.Path(__file__).resolve().parent.parent
# Der gemeinsame Nenner. Aendert er sich, aendert er sich an ALLEN drei
# Stellen — und dieser Wert hier mit.
AUFGABE = "cite or capture a web page"

fehler = 0


def pruefe(name, ok, hinweis=""):
    global fehler
    if not ok:
        fehler += 1
    print(("ok    " if ok else "FAIL  ") + name
          + (("  — " + hinweis) if hinweis and not ok else ""))


def erster_satz(t):
    return re.split(r"(?<=[.;:])\s", t.strip(), 1)[0]


quellen = {}

# 1. Registry
try:
    quellen["server.json"] = json.loads(
        (WURZEL / "server.json").read_text(encoding="utf-8"))["description"]
except Exception as e:
    pruefe("server.json lesbar", False, str(e))

# 2. Server-Karte
try:
    quellen["server-card.json"] = json.loads(
        (WURZEL / "docs/.well-known/mcp/server-card.json")
        .read_text(encoding="utf-8"))["serverInfo"]["description"]
except Exception as e:
    pruefe("server-card.json lesbar", False, str(e))

# 3. instructions aus dem Worker
try:
    src = (WURZEL / "worker/mcp.js").read_text(encoding="utf-8")
    m = re.search(r'instructions:\s*\n(?:\s*//.*\n)*\s*"([^"]+)"', src)
    quellen["instructions"] = m.group(1) if m else None
    pruefe("instructions im Worker gefunden", bool(m))
except Exception as e:
    pruefe("worker/mcp.js lesbar", False, str(e))

print()
for name, txt in quellen.items():
    if not txt:
        continue
    beginnt = txt.lower().startswith(AUFGABE)
    pruefe(f"{name:18} beginnt mit der Aufgabe", beginnt,
           f"beginnt mit {erster_satz(txt)[:60]!r}")

print()
for name, txt in quellen.items():
    if txt:
        print(f"  {name:18} {erster_satz(txt)[:78]}")

# Gegenprobe: die alte, laborzentrierte Formulierung darf nirgends mehr
# den Anfang machen. Sie im Text zu haben ist in Ordnung — sie beschreibt
# ja etwas Richtiges, nur nicht die Aufgabe.
print()
for name, txt in quellen.items():
    if not txt:
        continue
    schlecht = erster_satz(txt).lower().startswith(
        ("measurement", "measurements"))
    pruefe(f"{name:18} beginnt NICHT mit 'Measurement'", not schlecht)

print(f"\nBeschreibungs-Gleichlauf: {fehler} Fehler")
sys.exit(1 if fehler else 0)
