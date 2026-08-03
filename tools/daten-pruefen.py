#!/usr/bin/env python3
"""Prueft die Rohdaten unter docs/data/ gegen docs/data/schema.json.

    python3 tools/daten-pruefen.py            # Bericht, Exit 1 bei Abweichungen
    python3 tools/daten-pruefen.py --ci       # zusaetzlich ::error::/::warning::-Zeilen
    python3 tools/daten-pruefen.py --stdlib   # eingebauten Pruefer erzwingen (ohne jsonschema)

Warum es dieses Skript gibt (Issue #9): die Datensaetze unter docs/data/ machen
die Zahlen der Seite belegbar, aber nichts pruefte sie. Zwei Vorfaelle zeigten
die Luecke: ein Datensatz trug `per_source: []`, obwohl der Beitrag Einzelwerte
nannte; ein anderer trug eine aus einem fremden Beitrag kopierte Beschreibung.

Was geprueft wird:

  1. Schema (docs/data/schema.json) — Pflichtfelder und Wertformate. Das Schema
     ist aus dem Bestand abgeleitet und bildet die drei vorgefundenen Formate
     ab (kanonisch, historisch-en, historisch-de); der Bestand ist konform.
  2. per_source leer, obwohl results Einzelzaehlungen nennt (Vorfall 1) —
     Fehler.
  3. Wortgleiche `question` in zwei Datensaetzen (Vorfall 2, Kopierbefund) —
     Fehler, AUSNAHME: ausgewiesene Gegenmessung, wenn einer der beiden per
     `counterpart` (Top-Level oder in method) auf den anderen verweist.
  4. Kanonischer Datensatz ohne Kontrolllauf-Angabe (method enthaelt weder
     control/verification/counterpart noch ein Top-Level-counterpart) —
     Warnung, kein Fehler.

Pipeline-Entscheidung: der Schritt laeuft in .github/workflows/pruefen-und-
ausliefern.yml BLOCKIEREND (kein `|| true`). Das ist vertretbar, weil das
Schema den Bestand so abbildet, wie er ist — legitime historische Formate sind
konform, und die einzige wortgleiche question ist eine per counterpart
ausgewiesene Gegenmessung. Was kuenftig durchfaellt, ist also ein echter
Befund und soll die Auslieferung anhalten, bevor eine unbelegte Zahl
oeffentlich wird.

Abhaengigkeiten: laeuft mit `jsonschema`, wenn installiert; sonst mit dem
eingebauten Stdlib-Pruefer (deckt genau die Schema-Merkmale ab, die
schema.json verwendet: type, required, properties, pattern, minLength, allOf,
anyOf, if/then). In der Pipeline ist jsonschema nicht installiert — dort
laeuft der Stdlib-Pruefer, lokal getestet ueber --stdlib.
"""
import argparse
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent.parent
SCHEMA_WEG = HIER / "docs" / "data" / "schema.json"
DATEN_WEG = HIER / "docs" / "data"

# Schluessel in results, deren Zahlenwert > 0 Einzelwerte nahelegt — dazu
# gehoert dann eine befuellte per_source-Liste (Vorfall: leere Liste bei
# genannten Einzelwerten).
ZAEHL_MUSTER = re.compile(r"record|source|complete|handled|returned|blocked|urls", re.I)

# Wo ein Kontrolllauf erkennbar ist: Schluessel in method oder Top-Level.
KONTROLL_SCHLUESSEL = ("control", "verification", "counterpart")


# ---------------------------------------------------------------- Stdlib-Pruefer

def _std_fehler(schema, daten, pfad):
    """Mini-Validator fuer genau die Merkmale, die schema.json verwendet.
    Gibt eine Liste deutscher Fehlertexte zurueck."""
    fehler = []
    typ = schema.get("type")
    if typ:
        typen = typ if isinstance(typ, list) else [typ]
        zuordnung = {"object": dict, "array": list, "string": str,
                     "number": (int, float), "integer": int, "boolean": bool}
        if not any(isinstance(daten, zuordnung[t]) and
                   not (t in ("number", "integer") and isinstance(daten, bool))
                   for t in typen):
            fehler.append(f"{pfad}: Typ {type(daten).__name__}, erwartet {'/'.join(typen)}")
            return fehler
    if isinstance(daten, dict):
        for schluessel in schema.get("required", []):
            if schluessel not in daten:
                fehler.append(f"{pfad}: Pflichtfeld '{schluessel}' fehlt")
        for schluessel, unterschema in schema.get("properties", {}).items():
            if schluessel in daten:
                fehler.extend(_std_fehler(unterschema, daten[schluessel],
                                          f"{pfad}.{schluessel}"))
    if isinstance(daten, str):
        if "pattern" in schema and not re.search(schema["pattern"], daten):
            fehler.append(f"{pfad}: '{daten[:60]}' passt nicht auf Muster "
                          f"{schema['pattern']}")
        if "minLength" in schema and len(daten) < schema["minLength"]:
            fehler.append(f"{pfad}: zu kurz (mindestens {schema['minLength']} Zeichen)")
    for teil in schema.get("allOf", []):
        fehler.extend(_std_fehler(teil, daten, pfad))
    if "anyOf" in schema:
        # Reine Pflichtfeld-Alternativen bekommen eine lesbare Sammelmeldung.
        if all(set(a) == {"required"} for a in schema["anyOf"]):
            felder = [a["required"][0] for a in schema["anyOf"]]
            if not any(f in daten for f in felder if isinstance(daten, dict)):
                fehler.append(f"{pfad}: mindestens eines der Felder "
                              f"{'/'.join(felder)} erforderlich")
        elif not any(not _std_fehler(a, daten, pfad) for a in schema["anyOf"]):
            fehler.append(f"{pfad}: erfuellt keine der {len(schema['anyOf'])} Alternativen")
    if "if" in schema:
        wenn = schema["if"]
        if not _std_fehler(wenn, daten, pfad):  # Bedingung trifft zu
            dann = schema.get("then", {})
            for text in _std_fehler(dann, daten, pfad):
                fehler.append(f"{text} (Bedingung: 'if' erfuellt)")
    return fehler


# ---------------------------------------------------------------- jsonschema-Weg

def _js_fehler(schema, daten, name):
    from jsonschema import Draft202012Validator
    aus = []
    for e in Draft202012Validator(schema).iter_errors(daten):
        feld = ".".join(str(p) for p in e.absolute_path) or name
        if e.validator == "required":
            fehlend = re.search(r"'([^']+)'", e.message)
            aus.append(f"{feld}: Pflichtfeld '{fehlend.group(1)}' fehlt")
        elif e.validator == "pattern":
            aus.append(f"{feld}: Wert passt nicht auf Muster {e.validator_value}")
        elif e.validator == "minLength":
            aus.append(f"{feld}: zu kurz (mindestens {e.validator_value} Zeichen)")
        elif e.validator == "type":
            aus.append(f"{feld}: falscher Typ, erwartet {e.validator_value}")
        elif e.validator == "anyOf" and all(
                set(a) == {"required"} for a in e.validator_value):
            # Reine Pflichtfeld-Alternativen lesbar zusammenfassen, statt die
            # englische Sammelmeldung von jsonschema durchzureichen.
            felder = "/".join(a["required"][0] for a in e.validator_value)
            aus.append(f"{feld}: mindestens eines der Felder {felder} erforderlich")
        else:
            aus.append(f"{feld}: {e.message}")
    return aus


def schema_pruefen(schema, daten, name, stdlib):
    if stdlib:
        return _std_fehler(schema, daten, name)
    try:
        return _js_fehler(schema, daten, name)
    except ImportError:
        return _std_fehler(schema, daten, name)


# ---------------------------------------------------------------- Zusatz-Checks

def format_profil(daten):
    """Welches der drei Bestandsformate der Datensatz traegt — zur Einordnung
    im Bericht, nicht als Bewertung."""
    if "measurement" in daten:
        return "kanonisch"
    if "title" in daten:
        return "historisch-en"
    return "historisch-de"


def kontrolllauf_vorhanden(daten):
    if any(k in daten for k in KONTROLL_SCHLUESSEL):
        return True
    methode = daten.get("method")
    return isinstance(methode, dict) and any(k in methode for k in KONTROLL_SCHLUESSEL)


def per_source_pruefen(name, daten):
    """Vorfall 1: leere per_source-Liste, obwohl results Einzelwerte nennt."""
    quellen = daten.get("per_source")
    if not isinstance(quellen, list) or quellen:
        return []
    ergebnis = daten.get("results")
    if not isinstance(ergebnis, dict):
        return []
    zaehlungen = {k: v for k, v in ergebnis.items()
                  if isinstance(v, (int, float)) and not isinstance(v, bool)
                  and v > 0 and ZAEHL_MUSTER.search(k)}
    if zaehlungen:
        return [f"{name}: 'per_source' ist leer, aber 'results' nennt "
                f"Einzelwerte ({', '.join(f'{k}={v}' for k, v in zaehlungen.items())})"]
    return []


def counterpart_ziel(daten):
    """Dateiname, auf den ein Datensatz als Gegenmessung verweist — oder None."""
    stellen = [daten.get("counterpart")]
    methode = daten.get("method")
    if isinstance(methode, dict):
        stellen.append(methode.get("counterpart"))
    for s in stellen:
        if isinstance(s, str) and s:
            return Path(s).name
    return None


def fragen_pruefen(datensaetze):
    """Vorfall 2: wortgleiche question in zwei Datensaetzen. Fehler — es sei
    denn, einer verweist per counterpart auf den anderen (Gegenmessung, z.B.
    die VPN-Wiederholung von reading-list-to-bibliography)."""
    fehler, hinweise = [], []
    nach_frage = {}
    for name, daten in datensaetze.items():
        frage = daten.get("question")
        if isinstance(frage, str) and frage.strip():
            nach_frage.setdefault(frage.strip(), []).append(name)
    for frage, namen in nach_frage.items():
        if len(namen) < 2:
            continue
        # Eine Datei ist gedeckt, wenn sie selbst per counterpart auf eine
        # andere Datei der Gruppe verweist ODER von einer anderen so genannt
        # wird. Jede ungedeckte Datei ist ein eigener Kopierbefund — sonst
        # wuerde eine einzige Gegenmessung beliebig viele Kopien decken.
        ziele = {n: counterpart_ziel(datensaetze[n]) for n in namen}
        verweist_auf = {z for z in ziele.values() if z}
        ungedeckt = [n for n in namen
                     if not (ziele[n] in namen or n in verweist_auf)]
        gedeckt = [n for n in namen if n not in ungedeckt]
        if len(gedeckt) >= 2:
            hinweise.append(f"{', '.join(gedeckt)}: wortgleiche 'question', aber per "
                            f"'counterpart' als Gegenmessung ausgewiesen — zulässig")
        for n in ungedeckt:
            fehler.append(f"{n}: 'question' wortgleich mit anderen Datensaetzen "
                          f"({', '.join(x for x in namen if x != n)}), ohne "
                          f"counterpart-Verweis — Kopierbefund: „{frage[:80]}…“")
    return fehler, hinweise


# ---------------------------------------------------------------- Ablauf

def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--ci", action="store_true",
                   help="zusaetzlich GitHub-Actions-Zeilen ausgeben")
    p.add_argument("--stdlib", action="store_true",
                   help="eingebauten Pruefer erzwingen (ohne jsonschema)")
    p.add_argument("--schema", type=Path, default=SCHEMA_WEG)
    p.add_argument("--daten", type=Path, default=DATEN_WEG,
                   help="Verzeichnis mit den Datensaetzen")
    a = p.parse_args()

    def anzeige(weg):
        # Pfade ausserhalb des Repos (z.B. --daten ins Temp-Verzeichnis)
        # werden absolut angezeigt statt zu stuerzen.
        try:
            return str(weg.relative_to(HIER))
        except ValueError:
            return str(weg)

    schema = json.loads(a.schema.read_text(encoding="utf-8"))
    dateien = sorted(f for f in a.daten.glob("*.json") if f.name != "schema.json")
    if not dateien:
        print(f"Keine Datensaetze in {anzeige(a.daten)} gefunden.")
        return 1

    backend = "stdlib" if a.stdlib else "jsonschema (Fallback: stdlib)"
    print(f"Datenpruefung: {len(dateien)} Datensaetze in {anzeige(a.daten)}")
    print(f"Schema: {anzeige(a.schema)}, Pruefer: {backend}\n")

    fehler_gesamt, warnungen_gesamt = [], []
    datensaetze = {}
    for datei in dateien:
        name = datei.name
        try:
            daten = json.loads(datei.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fehler_gesamt.append(f"{name}: kein gueltiges JSON ({e})")
            continue
        datensaetze[name] = daten

        fehler = schema_pruefen(schema, daten, name, a.stdlib)
        fehler.extend(per_source_pruefen(name, daten))
        warnungen = []
        if format_profil(daten) == "kanonisch" and not kontrolllauf_vorhanden(daten):
            warnungen.append(f"{name}: kanonischer Datensatz ohne Kontrolllauf-Angabe "
                             f"(method.control/verification/counterpart)")

        profil = format_profil(daten)
        if fehler or warnungen:
            print(f"  {name}  [{profil}]")
            for f in fehler:
                print(f"    FEHLER  {f}")
                if a.ci:
                    print(f"::error file=docs/data/{name}::{f}")
            for w in warnungen:
                print(f"    WARNUNG {w}")
                if a.ci:
                    print(f"::warning file=docs/data/{name}::{w}")
        else:
            print(f"  {name}  [{profil}]  ok")
        fehler_gesamt.extend(fehler)
        warnungen_gesamt.extend(warnungen)

    # Dateiuebergreifend: Kopierbefund bei wortgleicher Frage.
    f_fehler, f_hinweise = fragen_pruefen(datensaetze)
    for h in f_hinweise:
        print(f"\n  HINWEIS {h}")
    for f in f_fehler:
        print(f"\n  FEHLER  {f}")
        if a.ci:
            print(f"::error::{f}")
    fehler_gesamt.extend(f_fehler)

    print(f"\n{len(fehler_gesamt)} Fehler, {len(warnungen_gesamt)} Warnungen "
          f"in {len(datensaetze)} Datensaetzen.")
    return 1 if fehler_gesamt else 0


if __name__ == "__main__":
    sys.exit(main())
