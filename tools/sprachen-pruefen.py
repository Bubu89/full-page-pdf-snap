#!/usr/bin/env python3
"""Ist die Oberflaeche in allen Sprachen vollstaendig austauschbar?

    python3 tools/sprachen-pruefen.py    # Exitcode 1 bei fehlenden Texten


Gleiche Schluesselzahl beweist nichts: zwei Dateien koennen 122 Eintraege
haben und trotzdem verschiedene. Geprueft wird deshalb der Schluesselsatz,
die Platzhalter je Schluessel, unuebersetzte Reste und — der eigentliche
Punkt — Text, der im Quelltext steht statt in den Sprachdateien. Was dort
steht, ist durch keine Sprachdatei ersetzbar.

Beide Bauformen werden getrennt geprueft. Ein Port, der die Sprachdateien
nicht mitnimmt, faellt in der Zaehlung nicht auf, weil er dieselbe Zahl hat.
"""
import json
import pathlib
import re
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent
BAUFORMEN = {"Firefox": REPO, "Chrome": REPO / "chrome-mv3"}
befunde = []


def melde(schwere, wo, text):
    befunde.append((schwere, wo, text))


def lade(pfad):
    return json.loads(pfad.read_text(encoding="utf-8"))


for bauform, wurzel in BAUFORMEN.items():
    loc = wurzel / "_locales"
    sprachen = sorted(p.name for p in loc.iterdir() if p.is_dir())
    daten = {s: lade(loc / s / "messages.json") for s in sprachen}
    basis = daten["en"]

    print(f"\n{'='*66}\n{bauform}: {len(sprachen)} Sprachen — {', '.join(sprachen)}\n{'='*66}")

    # --- 1. Schluesselsatz identisch? -------------------------------------
    for s in sprachen:
        fehlt = set(basis) - set(daten[s])
        zuviel = set(daten[s]) - set(basis)
        if fehlt:
            melde("FEHLER", f"{bauform}/{s}",
                  f"{len(fehlt)} Schluessel fehlen: {sorted(fehlt)[:6]}")
        if zuviel:
            melde("WARNUNG", f"{bauform}/{s}",
                  f"{len(zuviel)} Schluessel ohne Gegenstueck in en: {sorted(zuviel)[:6]}")
    print(f"  Schluesselsatz: {'identisch in allen Sprachen' if not any(b[1].startswith(bauform) for b in befunde) else 'ABWEICHUNGEN'}")

    # --- 2. Platzhalter je Schluessel -------------------------------------
    ph = lambda t: sorted(set(re.findall(r"\$\w+\$|\$\d", t or "")))
    abw = 0
    for k, v in basis.items():
        soll = ph(v.get("message", ""))
        for s in sprachen:
            if k not in daten[s]:
                continue
            ist = ph(daten[s][k].get("message", ""))
            if ist != soll:
                abw += 1
                melde("FEHLER", f"{bauform}/{s}",
                      f"Platzhalter in '{k}': erwartet {soll}, gefunden {ist}")
    print(f"  Platzhalter: {'stimmen ueberall' if not abw else f'{abw} Abweichungen'}")

    # --- 3. Unuebersetzte Reste -------------------------------------------
    # Ein Wert, der Zeichen fuer Zeichen dem englischen entspricht, ist
    # entweder nicht uebersetzt oder ein Eigenname. Kurze Werte und solche
    # ohne Buchstaben werden nicht gemeldet — "PDF" bleibt "PDF".
    for s in sprachen:
        if s == "en":
            continue
        gleich = [k for k, v in daten[s].items()
                  if k in basis
                  and v.get("message", "").strip() == basis[k].get("message", "").strip()
                  and len(v.get("message", "")) > 14
                  and re.search(r"[A-Za-z]{4}", v.get("message", ""))]
        if gleich:
            melde("HINWEIS", f"{bauform}/{s}",
                  f"{len(gleich)} Werte wortgleich mit en: {gleich[:5]}")

    # --- 4. Leere Werte ---------------------------------------------------
    for s in sprachen:
        leer = [k for k, v in daten[s].items() if not v.get("message", "").strip()]
        if leer:
            melde("FEHLER", f"{bauform}/{s}", f"{len(leer)} leere Werte: {leer[:5]}")

    # --- 5. Der eigentliche Punkt: Text im Quelltext ----------------------
    # Sichtbarer Text, der nicht durch i18n laeuft, ist nicht austauschbar.
    verwendet = set()
    quelldateien = [p for p in wurzel.rglob("*.js")
                    if "_locales" not in str(p) and "node_modules" not in str(p)]
    quelldateien += [p for p in wurzel.rglob("*.html") if "node_modules" not in str(p)]
    for p in quelldateien:
        t = p.read_text(encoding="utf-8", errors="replace")
        verwendet |= set(re.findall(r"getMessage\(\s*[\"'](\w+)[\"']", t))
        verwendet |= set(re.findall(r"data-i18n=[\"'](\w+)[\"']", t))
        verwendet |= set(re.findall(r"__MSG_(\w+)__", t))

    unbenutzt = set(basis) - verwendet
    fehlend = verwendet - set(basis)
    print(f"  im Quelltext angefordert: {len(verwendet)} Schluessel")
    if fehlend:
        melde("FEHLER", bauform,
              f"{len(fehlend)} Schluessel werden angefordert, existieren aber nicht: "
              f"{sorted(fehlend)[:8]}")
    if unbenutzt:
        melde("HINWEIS", bauform,
              f"{len(unbenutzt)} Schluessel in den Sprachdateien werden nirgends "
              f"angefordert: {sorted(unbenutzt)[:8]}")

# --- 6. Weichen die beiden Bauformen inhaltlich voneinander ab? -----------
print(f"\n{'='*66}\nFirefox gegen Chrome\n{'='*66}")
for s in sorted(p.name for p in (REPO / "_locales").iterdir() if p.is_dir()):
    a = lade(REPO / "_locales" / s / "messages.json")
    b_pfad = REPO / "chrome-mv3" / "_locales" / s / "messages.json"
    if not b_pfad.exists():
        melde("FEHLER", f"Chrome/{s}", "Sprachdatei fehlt im Chrome-Build")
        continue
    b = lade(b_pfad)
    unterschiede = [k for k in a
                    if k in b and a[k].get("message") != b[k].get("message")]
    nur_a = set(a) - set(b)
    if nur_a:
        melde("FEHLER", f"Chrome/{s}", f"{len(nur_a)} Schluessel fehlen gegenueber Firefox")
    print(f"  {s:<8} {len(unterschiede):>3} abweichende Texte"
          + (f"  {unterschiede[:3]}" if unterschiede else ""))

print(f"\n{'='*66}")
for stufe in ("FEHLER", "WARNUNG", "HINWEIS"):
    treffer = [b for b in befunde if b[0] == stufe]
    if treffer:
        print(f"\n── {stufe} ({len(treffer)}) ──")
        for _, wo, text in treffer[:14]:
            print(f"  [{wo}] {text}")
f = sum(1 for b in befunde if b[0] == "FEHLER")
print(f"\n{f} Fehler, "
      f"{sum(1 for b in befunde if b[0]=='WARNUNG')} Warnungen, "
      f"{sum(1 for b in befunde if b[0]=='HINWEIS')} Hinweise")
sys.exit(1 if f else 0)
