#!/usr/bin/env python3
"""Warnt, wenn ein Builder nicht mehr zu seiner Seite passt.

Der Anlass (16.08.2026): Zehn `build-*-post.py` erzeugen nicht mehr das, was
unter `docs/` liegt. Die Seiten wurden nach dem ersten Bau von Hand
weitergeschrieben, die Builder blieben stehen. `build-mcp-post.py` htte die
Seite von 1281 auf 673 Wrter gekrzt  47 % Inhalt weg, darunter ein
kompletter Abschnitt vom 3. August.

Gefhrlich wird das bei der Neun-Sprachen-Umstellung: Wer den Builder als
Textquelle nimmt, bersetzt einen veralteten Stand  und multipliziert den
Rckschritt mit neun.

Merksatz: **Magebend ist das HTML, nicht der Builder.** Ein Builder, der von
seiner Seite abweicht, ist Gerst, keine Quelle.

    python3 tools/builder-drift.py            # alle Paare prfen
    python3 tools/builder-drift.py --wortzahl # nur Seiten mit Textverlust
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DOCS = WURZEL / "docs"

# Ab wie vielen verlorenen Wrtern ist es keine Formatierungsabweichung mehr,
# sondern Inhalt? 20 Wrter sind ein Absatz.
WORTSCHWELLE = 20


def ziel_von(builder: Path):
    """Welche Datei schreibt dieser Builder? Aus `ZIEL = DOCS / ...` gelesen."""
    try:
        q = builder.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    m = re.search(r"^ZIEL\s*=\s*DOCS\s*/\s*(.+)$", q, re.M)
    if not m:
        return None
    teile = re.findall(r'"([^"]+)"', m.group(1))
    if not teile:
        return None
    p = DOCS.joinpath(*teile)
    return p if p.suffix else p / "index.html"


def nur_text(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>|<style[\s\S]*?</style>", " ", html)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html)).strip()


def pruefe(builder: Path):
    """-> (stand, meldung). Die Seite wird IMMER unveraendert zurueckgelassen."""
    ziel = ziel_von(builder)
    if not ziel or not ziel.exists():
        return "kein Ziel", ""
    vorher = ziel.read_bytes()
    try:
        r = subprocess.run([sys.executable, str(builder)], capture_output=True,
                           text=True, timeout=180, cwd=str(WURZEL))
        nachher = ziel.read_bytes()
    except subprocess.TimeoutExpired:
        return "Zeitueberschreitung", ""
    finally:
        # Unbedingt zurueckschreiben, auch bei Abbruch: eine Pruefung darf die
        # Publikation nicht veraendern.
        ziel.write_bytes(vorher)
    if r.returncode != 0:
        letzte = (r.stderr or r.stdout).strip().splitlines()
        return "Builder bricht ab", (letzte[-1][:70] if letzte else "")
    if vorher == nachher:
        return "gleich", ""
    a = nur_text(vorher.decode("utf-8", "replace")).split()
    b = nur_text(nachher.decode("utf-8", "replace")).split()
    verlust = len(a) - len(b)
    if verlust >= WORTSCHWELLE:
        return "INHALTSVERLUST", (f"{len(a)} -> {len(b)} Woerter, "
                                  f"{verlust} weniger ({100*verlust//max(1,len(a))} %)")
    if verlust <= -WORTSCHWELLE:
        return "Builder neuer", f"{len(a)} -> {len(b)} Woerter, {-verlust} mehr"
    return "abweichend", f"{abs(len(vorher)-len(nachher))} Bytes, Text ~gleich"


def main():
    nur_verlust = "--wortzahl" in sys.argv
    builder = sorted(WURZEL.glob("build-*.py"))
    zeilen, schlimm = [], 0
    for b in builder:
        stand, det = pruefe(b)
        if stand == "kein Ziel":
            continue
        if nur_verlust and stand != "INHALTSVERLUST":
            continue
        zeilen.append((stand, b.name, det))
        if stand == "INHALTSVERLUST":
            schlimm += 1

    rang = {"INHALTSVERLUST": 0, "Builder bricht ab": 1, "Builder neuer": 2,
            "abweichend": 3, "Zeitueberschreitung": 4, "gleich": 5}
    for stand, name, det in sorted(zeilen, key=lambda z: rang.get(z[0], 9)):
        marke = "!!" if stand == "INHALTSVERLUST" else ("  " if stand == "gleich" else " ·")
        print(f" {marke} {name:<34}{stand:<20}{det}")

    print()
    if schlimm:
        print(f"{schlimm} Builder wuerde(n) Inhalt loeschen.")
        print("Nicht neu bauen. Fuer eine Uebersetzung ist das HTML die Quelle,")
        print("nicht der Builder — der Text ist dort weitergeschrieben worden.")
        return 1
    print("Kein Builder loescht Inhalt.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
