#!/usr/bin/env python3
"""Legt eine neue Seite so an, dass sie von Anfang an vollständig ist.

Das Problem, das diese Datei löst: Eine Seite ist nicht fertig, wenn ihr Text
steht. Sie muss in neun Sprachen vorliegen, im Verzeichnis ihrer Rubrik
verlinkt sein, in der Sitemap stehen, im Agenten-Index auftauchen und die
Sprachumschaltung korrekt bedienen. Wird eines davon vergessen, fällt es
niemandem auf — die Seite ist ja da. So entstanden /how-to/ ohne
Verzeichnisseite (drei Artikel, nur über die Startseite erreichbar) und
Beiträge, die unter der Überschrift „Notizen" standen, ohne Notizen zu sein.

    python3 tools/neue-seite.py anlegen notes mein-thema "Titel des Beitrags"
    python3 tools/neue-seite.py fertigstellen texte_mein_thema.py

`anlegen` erzeugt Gerüst und Textmodul aus einer bestehenden Seite derselben
Rubrik — Kopf, Navigation und Fuß werden übernommen, nicht neu erfunden.
`fertigstellen` fährt danach die ganze Kette und sagt, was noch fehlt.

Die Kette, in dieser Reihenfolge — jeder Schritt setzt den vorigen voraus:

    1. seite-neunsprachig     Sprachblöcke in die Seite
    2. build-sitemap          Adresse aufnehmen
    3. build-llms-index       Agenten-Index nachziehen
    4. sprachmeta             Titel/Beschreibung je Sprache ernten
    5. seiten-systematik      steht sie im Verzeichnis ihrer Rubrik?
    6. pruefe-alle-sprachen   schaltet sie im echten Browser um?
    7. links-pruefen          zeigt sie irgendwohin ins Leere?
"""
import re
import subprocess
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
DOCS = WURZEL / "docs"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]

# Vorlage je Rubrik: eine bestehende, neunsprachige Seite. Kopf und Fuss von
# dort zu nehmen ist der einzige Weg, der nicht auseinanderlaeuft.
VORLAGEN = {
    "notes": "notes/smaller-files-better-ocr/index.html",
    "measurements": "measurements/android-capture-extensions/index.html",
    "how-to": "how-to/for-students/index.html",
    "tools": "tools/index.html",
}

KETTE = [
    ("Sprachblöcke bauen", ["tools/seite-neunsprachig.py", "{modul}"]),
    ("Sitemap", ["build-sitemap.py"]),
    ("Agenten-Index", ["build-llms-index.py"]),
    ("Meta je Sprache", ["tools/sprachmeta.py"]),
    ("Systematik", ["tools/seiten-systematik.py"]),
    ("Sprachumschaltung", ["tools/pruefe-alle-sprachen.py"]),
    ("Verlinkung", ["tools/links-pruefen.py"]),
]


def lauf(argv, timeout=400):
    p = subprocess.run([sys.executable] + argv, capture_output=True, text=True,
                       timeout=timeout, cwd=str(WURZEL))
    zeilen = (p.stdout + p.stderr).strip().splitlines()
    letzte = next((z.strip() for z in reversed(zeilen) if z.strip()), "")
    return p.returncode == 0, letzte[:100]


def anlegen(rubrik, slug, titel):
    if rubrik not in VORLAGEN:
        raise SystemExit(f"Unbekannte Rubrik: {rubrik} — "
                         f"bekannt: {', '.join(VORLAGEN)}")
    ziel = DOCS / rubrik / slug / "index.html"
    if ziel.exists():
        raise SystemExit(f"Gibt es schon: {ziel.relative_to(WURZEL)}")
    vorlage = DOCS / VORLAGEN[rubrik]
    if not vorlage.exists():
        raise SystemExit(f"Vorlage fehlt: {vorlage}")

    v = vorlage.read_text(encoding="utf-8")
    marke = '<div class="wrap">'
    kopf = v[: v.index(marke) + len(marke)]
    fuss = v[v.rindex("</div>\n</body>"):]

    url = f"https://provinglab.dev/{rubrik}/{slug}/"
    kopf = re.sub(r"<title>.*?</title>", f"<title>{titel} — Proving Lab</title>",
                  kopf, count=1, flags=re.S)
    kopf = re.sub(r'(<link rel="canonical" href=")[^"]*(">)',
                  lambda m: m.group(1) + url + m.group(2), kopf, count=1)
    # Alte hreflang-Zeilen der Vorlage entfernen — der Renderer setzt eigene.
    kopf = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", kopf)

    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_text(kopf + "\n<header>\n  <h1>" + titel + "</h1>\n</header>\n"
                    + fuss, encoding="utf-8")

    modul = WURZEL / ("texte_" + slug.replace("-", "_") + ".py")
    if not modul.exists():
        # Mit ",\n" verbinden erzeugt ein doppeltes Komma: jede Zeile traegt
        # ihres schon. Das erzeugte Modul war dadurch nicht ladbar — und der
        # Fehler faellt erst beim Bauen auf, nicht beim Anlegen.
        bloecke = "\n".join(
            f'    "{s}": _RUMPF if "{s}" == BASIS else "",' for s in SPRACHEN)
        modul.write_text(f'''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""{titel} — in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, nie ein alter build-*.py:
vierzehn von vierzehn weichen von ihrer Seite ab, vier loeschen Text.
Pruefen mit: python3 tools/builder-drift.py

Unverrueckbar in jeder Sprache: Zahlen, Masseinheiten, Versionsnummern,
Dateiformate, Werkzeug- und Funktionsnamen, Eigennamen, alle Adressen.
Eine uebersetzte Zahl waere eine andere Messung.

Rendern:  python3 tools/seite-neunsprachig.py {modul.name}
"""

URL = "{url}"
ZIEL = "{rubrik}/{slug}/index.html"
SPRACHEN = {SPRACHEN!r}
BASIS = "en"

# Der fertige Rumpf: alles zwischen <div class="wrap"> und dem schliessenden
# </div>. Zuerst hier auf Englisch schreiben, dann uebersetzen.
_RUMPF = """<header>
  <h1>{titel}</h1>
  <p class="standfirst">
    Ein Satz, der sagt, was gemessen wurde und was dabei herauskam.
  </p>
</header>

<h2>Ueberschrift</h2>
<p>
  Text.
</p>
"""

# Jede Sprache traegt den FERTIGEN Rumpf. Leere Eintraege verhindern den Bau —
# eine Seite mit Umschalter, hinter dem nichts steht, ist schlechter als eine
# ehrlich einsprachige.
INHALT = {{
{bloecke}
}}
''', encoding="utf-8")

    print(f"angelegt: {ziel.relative_to(WURZEL)}")
    print(f"          {modul.relative_to(WURZEL)}")
    print(f"\nJetzt den englischen Rumpf in {modul.name} schreiben, uebersetzen,")
    print(f"dann:  python3 tools/neue-seite.py fertigstellen {modul.name}")
    print(f"\nNICHT vergessen: die Seite muss im Verzeichnis /{rubrik}/ verlinkt")
    print("werden — Schritt 5 der Kette meldet es, falls sie fehlt.")
    return 0


def fertigstellen(modul):
    print("Kette laeuft. Jeder Schritt setzt den vorigen voraus.\n")
    offen = 0
    for name, argv in KETTE:
        arg = [a.replace("{modul}", modul) for a in argv]
        datei = WURZEL / arg[0]
        if not datei.exists():
            print(f"  ---  {name:<22} {arg[0]} fehlt")
            continue
        try:
            ok, letzte = lauf(arg)
        except subprocess.TimeoutExpired:
            ok, letzte = False, "Zeitueberschreitung"
        print(f"  {'OK ' if ok else 'FEHL'} {name:<22} {letzte}")
        if not ok:
            offen += 1
            # Nach einem gescheiterten Bau haben die spaeteren Schritte keine
            # Grundlage mehr — dann lieber hier halten als Folgefehler melden.
            if name == "Sprachblöcke bauen":
                print("\n  Bau gescheitert — Kette angehalten.")
                return 1
    print()
    print("Fertig." if not offen else f"{offen} Schritt(e) offen.")
    return 1 if offen else 0


def main():
    a = sys.argv[1:]
    if len(a) >= 4 and a[0] == "anlegen":
        return anlegen(a[1], a[2], " ".join(a[3:]))
    if len(a) == 2 and a[0] == "fertigstellen":
        return fertigstellen(a[1])
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
