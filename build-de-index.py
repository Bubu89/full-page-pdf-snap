#!/usr/bin/env python3
"""Erzeugt docs/deutsch/index.html — die Übersicht der deutschen Fassungen.

Warum es diese Seite gibt: Acht Seiten tragen einen vollständigen deutschen
Teil, die übrigen nicht. Ein Menüpunkt, der mal erscheint und mal
nicht, ist für Leser schlechter als keiner — er wirkt wie ein Fehler. Mit
dieser Seite steht „Deutsch" überall im Menü und führt immer irgendwohin:
auf Seiten mit eigenem deutschen Teil direkt dorthin, sonst hierher.

Der Inhalt wird aus den Seiten selbst gelesen, nicht gepflegt. Wer eine
deutsche Fassung ergänzt, muss nichts nachtragen.
"""
import glob
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "index.html"


def deutsche_seiten():
    """Alle Seiten mit einem eigenen deutschen Abschnitt, mit Titel und Umfang."""
    out = []
    for datei in sorted(glob.glob(str(DOCS / "**" / "*.html"), recursive=True)):
        s = Path(datei).read_text(encoding="utf-8")
        # Bis zum 10.08.2026 wurde die Seite am Anker id="b-de" erkannt. Den gab
        # es nur, solange jede Seite ihr eigenes Schaltflaechenpaar trug. Seit
        # die Sprachwahl fuer neun Sprachen im Menue steht, ist das Merkmal der
        # Sprachblock selbst — der Anker waere ein Merkmal der Bedienung, nicht
        # des Inhalts.
        if 'data-lang="de"' not in s:
            continue
        pfad = str(Path(datei).relative_to(DOCS).parent).replace("\\", "/")
        url = "/" if pfad == "." else f"/{pfad}/"
        titel = (re.search(r"<title>(.*?)</title>", s, re.S) or [None, ""])[1]
        titel = re.sub(r"\s*[—|]\s*Proving Lab\s*$", "", titel).strip()
        # Umfang: alles ab dem Anker bis zum Fuss. Der erste Versuch mass
        # nur bis zum ersten schliessenden Tag und war um Faktor drei zu klein.
        # Keine Zeichenzahl — siehe unten. Sortiert wird nach Titel.
        # Erste deutsche Zeile als Vorschau
        vor = ""
        m = re.search(r'<p[^>]*\blang="de"[^>]*>(.*?)</p>', s, re.S)
        if m:
            vor = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            vor = re.sub(r"\s+", " ", vor)[:190]
        out.append({"url": url, "titel": titel, "vorschau": vor})
    out.sort(key=lambda x: x["titel"])
    return out


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf, anzahl):
    URL = "https://provinglab.dev/deutsch/"
    TITEL = "Deutschsprachige Fassungen"
    # Die Zahl muss mitgerechnet werden: Sie stand fest im Text, und nach der
    # neunten Fassung haette die Seite von acht Beitraegen gesprochen, waehrend
    # darunter neun gelistet waren.
    BESCHR = (f"{anzahl} Beiträge auf provinglab.dev tragen eine vollständige deutsche "
              "Fassung: zum Werkzeug, zu verschwindenden Quellen, zu Zitationsdaten "
              "und Literaturverzeichnissen, zu Nachweisen im Studium, zur "
              "Offenlegung und zum Haftungsausschluss.")
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHR + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{TITEL}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHR + m.group(2), k)
    # Diese eine Seite ist durchgehend deutsch — anders als die übrigen.
    k = re.sub(r'(<html[^>]*\blang=")[^"]*(")', r"\g<1>de\g<2>", k)
    k = re.sub(r'<link rel="alternate" hreflang="[^"]*"[^>]*>\s*', "", k)
    k = k.replace("</head>",
                  f'<link rel="alternate" hreflang="de" href="{URL}">\n'
                  f'<link rel="alternate" hreflang="en" href="https://provinglab.dev/">\n'
                  f'<link rel="alternate" hreflang="x-default" href="https://provinglab.dev/">\n</head>')
    return k


def inhalt(seiten):
    zeilen = []
    for s in seiten:
        zeilen.append(f'''<div class="item">
  <h2><a href="{s['url']}">{s['titel']}</a></h2>
  <p>{s['vorschau']}</p>
</div>''')
    return f'''<div class="wrap">

<header>
  <h1>Deutschsprachige Fassungen</h1>
  <p class="standfirst">
    Diese Seite ist auf Englisch geschrieben. {len(seiten)} Beiträge tragen
    zusätzlich eine vollständige deutsche Fassung auf derselben Seite.
    Es sind keine Übersetzungen, sondern
    eigenständige Fassungen desselben Arguments, geschrieben für Leser in
    Österreich und Deutschland.
  </p>
  <p class="meta">Der Link „Deutsch" im Menü führt auf diesen Seiten direkt zum
    deutschen Teil, überall sonst hierher. ·
    <a href="/" hreflang="en" lang="en">English site</a></p>
</header>

{chr(10).join(zeilen)}

<div class="item">
  <h2><a href="/anleitung/webseite-als-pdf-speichern/">Webseite als PDF speichern — die Anleitung</a></h2>
  <p>
    Für Menschen geschrieben, jede Zahl mit ihrer Messung verlinkt: warum eine
    Erweiterung statt des Druckdialogs, wo der Druckexport trotzdem gewinnt,
    was auf Android geht und warum in eine Quellenangabe das Abrufdatum gehört.
  </p>
  <p style="font-size:.9rem">
    Diese Seite verlinkte bis zum 3. August 2026 nur die englische Fassung —
    die deutsche existierte, war aber von nirgendwo erreichbar und damit für
    Suchmaschinen praktisch nicht vorhanden. Gefunden hat es
    <code>tools/seo-pruefen.py</code> als einzigen echten Befund unter zwanzig
    Meldungen, von denen sich sechzehn als Fehler des Prüfers herausstellten.
  </p>
</div>

<div class="item">
  <h2>Warum nicht die ganze Seite?</h2>
  <p>
    Weil eine halb gepflegte Übersetzung schlechter ist als eine ehrliche
    Teilfassung. Die Messungen enthalten Zahlen, Methoden und Korrekturen, die
    sich ändern; zwei Sprachfassungen davon auseinanderlaufen zu lassen wäre
    genau die Art Fehler, über die hier sonst geschrieben wird. Übersetzt wird
    daher, was auch auf Deutsch vollständig gepflegt werden kann.
  </p>
</div>

'''


def main():
    seiten = deutsche_seiten()
    if not seiten:
        raise SystemExit("Keine Seite mit einem deutschen Abschnitt gefunden.")
    kopf, fuss = kopf_und_fuss()
    ziel = DOCS / "deutsch"
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "index.html").write_text(anpassen(kopf, len(seiten)) + inhalt(seiten) + fuss, encoding="utf-8")
    print(f"  deutsch/index.html geschrieben — {len(seiten)} Fassungen")
    for s in seiten:
        print(f"    {s['url']}")


if __name__ == "__main__":
    main()
