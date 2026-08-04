#!/usr/bin/env python3
"""Vergleicht server.json mit dem, was die offizielle MCP-Registry fuehrt.

    python3 tools/registry-stand.py            # Bericht, Exitcode 0
    python3 tools/registry-stand.py --gleich   # Exitcode 0 wenn gleich, sonst 1

Gedacht fuer die Pipeline: veroeffentlichen soll nur, wer etwas zu
veroeffentlichen hat. Und nach dem Veroeffentlichen wird nachgesehen — ein
Befehl, der ohne Fehler zurueckkehrt, ist kein Nachweis, dass ein Eintrag
tatsaechlich steht.
"""
import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

REGISTRY = "https://registry.modelcontextprotocol.io/v0/servers"
LOKAL = Path(__file__).resolve().parent.parent / "server.json"


def fern(name):
    """Fassung und Zustand des Eintrags, oder (None, None) wenn es keinen gibt."""
    frage = name.split("/")[-1]
    try:
        with urllib.request.urlopen(f"{REGISTRY}?search={frage}&limit=30",
                                    timeout=30) as a:
            d = json.load(a)
    except (urllib.error.URLError, TimeoutError) as e:
        print(f"  Registry nicht erreichbar: {e}")
        return None, None
    for e in d.get("servers") or []:
        if e["server"]["name"] == name:
            zustand = (e.get("_meta", {})
                        .get("io.modelcontextprotocol.registry/official", {})
                        .get("status"))
            return e["server"]["version"], zustand
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gleich", action="store_true",
                    help="Exitcode 1, wenn die Registry nicht den lokalen Stand fuehrt")
    a = ap.parse_args()

    d = json.loads(LOKAL.read_text(encoding="utf-8"))
    name, hier = d["name"], d["version"]
    dort, zustand = fern(name)

    print(f"  {name}")
    print(f"    lokal:    {hier}")
    print(f"    Registry: {dort or 'kein Eintrag'}"
          + (f" ({zustand})" if zustand else ""))

    if a.gleich:
        sys.exit(0 if (dort == hier and zustand == "active") else 1)


if __name__ == "__main__":
    main()
