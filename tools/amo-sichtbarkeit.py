#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wo steht das Add-on in der AMO-Suche? (17.08.2026)

Vorher-Messung für M1 (Kategorien und Tags am Anwendungsfall ausrichten).
Ohne diese Zahlen liesse sich hinterher nicht sagen, ob die Aenderung
etwas gebracht hat — und „fuehlt sich besser an" ist keine Messung.

Gesucht wird nach den Begriffen, die die Zielgruppe tatsaechlich eingibt.
Ausgegeben wird die Position, die Trefferzahl und der staerkste Wettbewerber.
"""
import json
import sys
import urllib.parse
import urllib.request

SLUG = "full_page_pdf_snap_webpagesave"
BEGRIFFE = [
    "zotero", "citation", "cite webpage", "research", "reference manager",
    "save page as pdf", "full page pdf", "web page pdf", "archive webpage",
    "citavi", "ris", "screenshot pdf", "source capture", "scholar",
]


def suche(q, seiten=3, pro=25):
    treffer = []
    gesamt = None
    for s in range(1, seiten + 1):
        u = ("https://addons.mozilla.org/api/v5/addons/search/?"
             + urllib.parse.urlencode({
                 "q": q, "app": "firefox", "type": "extension",
                 "page_size": pro, "page": s}))
        try:
            with urllib.request.urlopen(u, timeout=25) as r:
                d = json.loads(r.read())
        except Exception:
            break
        gesamt = d.get("count") if gesamt is None else gesamt
        res = d.get("results", [])
        treffer.extend(res)
        if len(res) < pro:
            break
    return treffer, gesamt


def name_von(r):
    n = r.get("name")
    if isinstance(n, dict):
        return n.get("en-US") or next(iter(n.values()), "")
    return n or ""


print(f"{'Suchbegriff':22} {'Position':>9} {'Treffer':>8}  Staerkster Wettbewerber")
print("-" * 84)
gefunden, nicht = 0, []
for q in BEGRIFFE:
    res, gesamt = suche(q)
    pos = None
    for i, r in enumerate(res, 1):
        if r.get("slug") == SLUG:
            pos = i
            break
    erster = res[0] if res else None
    wett = (f"{name_von(erster)[:34]} ({erster.get('average_daily_users', 0)})"
            if erster else "—")
    if pos:
        gefunden += 1
        p = f"{pos}"
    else:
        nicht.append(q)
        p = f">{len(res)}"
    print(f"{q:22} {p:>9} {str(gesamt or 0):>8}  {wett}")

print("-" * 84)
print(f"Gefunden bei {gefunden} von {len(BEGRIFFE)} Begriffen.")
if nicht:
    print("Nicht in den ersten Treffern bei: " + ", ".join(nicht))
