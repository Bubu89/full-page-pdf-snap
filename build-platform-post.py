#!/usr/bin/env python3
"""Erzeugt den Beitrag ueber Zitationsdaten je Plattform und die Anwendungsfaelle.

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und gemeinsame Meta-Angaben nicht auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "measurements" / "citation-by-platform"
DATEN = DOCS / "data" / "2026-08-03-citation-by-platform.json"

URL = "https://provinglab.dev/measurements/citation-by-platform/"
TITEL = "Where citation data actually lives: 18 scholarly platforms measured"
TITEL_DE = "Wo Zitationsdaten tatsächlich stehen: 18 wissenschaftliche Plattformen gemessen"
BESCHREIBUNG = (
    "Which platforms declare citation data a reader can use? Eleven of eighteen returned "
    "a record, ten of them complete. The most complete record of all came from the DOI "
    "resolver — not from the article page."
)

# Deutsche Fassung auf derselben Adresse, Umschaltung per #b-de — das Muster
# dafuer ist measurements/web-citations-that-vanish. Sprachbloecke tragen
# data-lang, build-de-index.py findet die Seite am Anker id="b-de".
SPRACHE_CSS = """
  /* --- Sprachumschaltung --- */
  [data-lang]{display:none}
  [data-lang].on{display:block}
  li[data-lang].on{display:list-item}
  span[data-lang].on,a[data-lang].on{display:inline}
  .lang{display:flex;gap:6px;margin:0 0 26px}
  .lang button{font:inherit;font-size:.86rem;font-weight:600;padding:7px 18px;cursor:pointer;
    background:var(--card);color:var(--dim);border:1px solid var(--line);border-radius:8px}
  .lang button[aria-pressed="true"]{background:var(--acc);color:#fff;border-color:var(--acc)}
"""

SPRACHE_SKRIPT = """<script>
function setLang(l){
  document.querySelectorAll('[data-lang]').forEach(function(e){
    e.classList.toggle('on', e.dataset.lang === l);
  });
  document.getElementById('b-en').setAttribute('aria-pressed', l === 'en');
  document.getElementById('b-de').setAttribute('aria-pressed', l === 'de');
  document.documentElement.lang = l;
  try { localStorage.setItem('pl-lang', l); } catch (e) {}
}
(function(){
  var gespeichert = null;
  try { gespeichert = localStorage.getItem('pl-lang'); } catch (e) {}
  var l = gespeichert || ((navigator.language || 'en').slice(0,2) === 'de' ? 'de' : 'en');
  if (l === 'de') setLang('de');
})();
</script>"""


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + " Mit deutscher Fassung." + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{TITEL}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    # hreflang in beide Richtungen: deutsch und englisch teilen sich eine
    # Adresse, also zeigen alle drei Angaben auf dieselbe.
    k = k.replace(
        f'<link rel="canonical" href="{URL}">',
        f'<link rel="canonical" href="{URL}">\n'
        f'<link rel="alternate" hreflang="en" href="{URL}">\n'
        f'<link rel="alternate" hreflang="de" href="{URL}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{URL}">')
    k = k.replace("</style>", SPRACHE_CSS + "</style>")
    k = k.replace(
        '<a class="n" href="../../deutsch/" hreflang="de" lang="de" '
        'title="Deutschsprachige Fassungen">Deutsch</a>',
        '<a class="n" href="#b-de" hreflang="de" lang="de" '
        'title="Zur deutschen Fassung auf dieser Seite">Deutsch</a>')
    ld = {"@context": "https://schema.org", "@type": "TechArticle",
          "headline": TITEL, "description": BESCHREIBUNG,
          "datePublished": "2026-08-03", "dateModified": "2026-08-03",
          "inLanguage": ["en", "de"], "url": URL,
          "about": ["citation metadata", "scholarly platforms", "DOI",
                    "Zitationsdaten", "Quellennachweis", "Literaturverzeichnis"],
          "keywords": ("citation data, DOI resolver, scholarly platforms, "
                       "Zitationsdaten, Literaturverzeichnis erstellen, "
                       "Internetquellen zitieren, Abrufdatum, RIS, BibTeX"),
          "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
          "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"}}
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)


def tabelle(d):
    ja = lambda x: "✓" if x else "—"
    zeilen = []
    for p in d["results"]["per_platform"]:
        if p["returned"]:
            zeilen.append(
                f'    <tr><td>{p["platform"]}</td><td class="num">{p["authors"]}</td>'
                f'<td class="num">{p["year"] or "—"}</td><td class="num">{ja(p["doi"])}</td>'
                f'<td class="num">{ja(p["pages"])}</td><td class="num">{ja(p["issn"])}</td>'
                f'<td class="num">{p["seconds"]}</td></tr>')
        else:
            grund = (p["reason"] or "no result")[:38]
            zeilen.append(
                f'    <tr><td>{p["platform"]}</td><td colspan="5" style="color:#64748b">{grund}</td>'
                f'<td class="num">{p["seconds"]}</td></tr>')
    return "\n".join(zeilen)


def inhalt(d):
    r = d["results"]
    return f"""<div class="wrap">

<header>
  <h1 data-lang="en" class="on" lang="en">{TITEL}</h1>
  <h1 data-lang="de" lang="de">{TITEL_DE}</h1>
  <p class="standfirst on" data-lang="en" lang="en">
    A reference is only as good as the data behind it. Eighteen platforms a
    researcher would plausibly use were asked what they declare about their own
    articles. Eleven answered; the most complete answer did not come from an
    article page at all.
  </p>
  <p class="standfirst" data-lang="de" lang="de">
    Ein Quellennachweis ist nur so gut wie die Daten dahinter. Achtzehn
    Plattformen, die Forschende realistischerweise nutzen, wurden gefragt, was
    sie über ihre eigenen Artikel ausweisen. Elf antworteten — und die
    vollständigste Antwort kam gar nicht von einer Artikelseite.
  </p>
  <p class="meta"><span data-lang="en" class="on" lang="en">3 August 2026 · {len(r["per_platform"])} platforms, one pass ·
    <a href="/data/2026-08-03-citation-by-platform.json">raw data</a></span><span data-lang="de" lang="de">3. August 2026 · {len(r["per_platform"])} Plattformen, ein Durchlauf ·
    <a href="/data/2026-08-03-citation-by-platform.json">Rohdaten</a></span></p>
</header>

<div class="lang">
  <button id="b-en" aria-pressed="true" onclick="setLang('en')">English</button>
  <button id="b-de" aria-pressed="false" onclick="setLang('de')">Deutsch</button>
</div>

<div data-lang="en" class="on" lang="en">

<div class="kf-row">
  <div class="kf b"><div class="n">{r["returned_data"]}/{len(r["per_platform"])}</div><div class="l">returned a record</div></div>
  <div class="kf"><div class="n">{r["complete_authors_and_year"]}</div><div class="l">with authors and year</div></div>
  <div class="kf"><div class="n">{r["title_matched_crossref"]}</div><div class="l">titles confirmed by Crossref</div></div>
</div>

<h2>What each platform declares</h2>
<table>
  <thead><tr><th scope="col">Platform</th><th scope="col">Authors</th><th scope="col">Year</th><th scope="col">DOI</th><th scope="col">Pages</th><th scope="col">ISSN</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle(d)}
  </tbody>
</table>

<h2>The finding worth acting on</h2>
<p>
  <strong>Resolving the DOI beat visiting the article page.</strong> The same work
  that Wiley's own page serves without page numbers came back complete through
  <code>doi.org</code> — authors, year, journal, volume, pages and ISSN — in
  0.4&nbsp;seconds, from a publisher whose article pages refuse server-side
  readers outright.
</p>
<p>
  So the practical rule for anyone assembling a bibliography: <strong>if you have
  the DOI, use <code>https://doi.org/…</code></strong>, not the link your search
  engine gave you. It is faster, more complete, and it works where the publisher's
  own page does not.
</p>

<h2>What this is good for</h2>

<h3>Keeping a source that will not survive the term</h3>
<p>
  Web pages cited in student work vanish — we have
  <a href="/measurements/web-citations-that-vanish/">measured how often</a>. A
  capture keeps the page as it looked, with the retrieval time down to the second
  and its time zone, a checksum of the image data, and the citation record beside
  it. When the marker asks what the page said in August, the answer is a file
  rather than a memory.
</p>

<h3>Turning a reading list into records</h3>
<p>
  Given a list of addresses, the endpoint returns RIS entries that import into
  Citavi, Zotero or EndNote without retyping — and
  <a href="/measurements/citation-triage/">names the ones it cannot reach</a>, so
  those can be opened in a browser instead of being silently dropped.
</p>

<h3>Sources behind a login</h3>
<p>
  A university licence, a library proxy, a paywalled journal: no server-side
  reader can follow you there, and three of the publishers measured here refuse
  them outright. A <a href="/tools/full-page-pdf-snap/">capture extension</a> runs
  in your own session with your own access, which is why the two approaches
  belong together rather than competing.
</p>

<h3>Feeding a long page to a language model</h3>
<p>
  One continuous sheet with real, selectable text — taken from the document rather
  than recognised from pixels — and page breaks that fall between lines instead of
  through them. What the model reads is what the page said.
</p>

<h2>What it is not good for</h2>
<ul>
  <li><strong>Replacing a publisher's own export.</strong> Where an article page
    offers RIS or BibTeX, that file is authoritative and this is not.</li>
  <li><strong>Proving what a page contained.</strong> A screen capture is not a
    qualified electronic document under eIDAS. It records what a browser displayed
    at a stated time, nothing more — the checksum covers the file, not the
    truthfulness of the page.</li>
  <li><strong>Filling gaps.</strong> Where a platform declares no page numbers —
    PubMed's abstract pages, for instance — the field stays empty rather than
    being fetched from somewhere else and presented as if the page had said it.</li>
</ul>

<h2>Limits of this measurement</h2>
<ul>
  <li>Eighteen platforms is a survey of the common ones, not a census.</li>
  <li>Europe PMC timed out after 55&nbsp;seconds. That is counted as no result
    here, not as a fault of the platform.</li>
  <li>Three refusals (MDPI, ScienceDirect, DOAJ) are publisher policy against
    server-side readers, measured on one afternoon and liable to change.</li>
</ul>

</div>

<div data-lang="de" lang="de">

<div class="kf-row">
  <div class="kf b"><div class="n">{r["returned_data"]}/{len(r["per_platform"])}</div><div class="l">gaben einen Nachweis zurück</div></div>
  <div class="kf"><div class="n">{r["complete_authors_and_year"]}</div><div class="l">mit Autoren und Jahr</div></div>
  <div class="kf"><div class="n">{r["title_matched_crossref"]}</div><div class="l">Titel von Crossref bestätigt</div></div>
</div>

<h2>Was jede Plattform ausweist</h2>
<table>
  <thead><tr><th scope="col">Plattform</th><th scope="col">Autoren</th><th scope="col">Jahr</th><th scope="col">DOI</th><th scope="col">Seiten</th><th scope="col">ISSN</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle(d)}
  </tbody>
</table>

<h2>Der Befund, den man umsetzen sollte</h2>
<p>
  <strong>Den DOI aufzulösen schlug den Besuch der Artikelseite.</strong>
  Derselbe Beitrag, den die eigene Seite von Wiley ohne Seitenzahlen ausliefert,
  kam über <code>doi.org</code> vollständig zurück — Autoren, Jahr, Zeitschrift,
  Band, Seiten und ISSN — in 0,4&nbsp;Sekunden, von einem Verlag, dessen
  Artikelseiten serverseitige Leser kategorisch abweisen.
</p>
<p>
  Die praktische Regel für alle, die ein Literaturverzeichnis zusammenstellen:
  <strong>Wer den DOI hat, nutzt <code>https://doi.org/…</code></strong>, nicht
  den Link aus der Suchmaschine. Das ist schneller, vollständiger und
  funktioniert dort, wo die eigene Seite des Verlags versagt.
</p>

<h2>Wofür das gut ist</h2>

<h3>Eine Quelle sichern, die das Semester nicht überlebt</h3>
<p>
  Webseiten, die in studentischen Arbeiten zitiert werden, verschwinden — wie
  oft, haben wir <a href="/measurements/web-citations-that-vanish/">gemessen</a>.
  Eine Aufnahme bewahrt die Seite, wie sie aussah: mit Abrufzeitpunkt auf die
  Sekunde samt Zeitzone, einer Prüfsumme der Bilddaten und dem Zitationsnachweis
  daneben. Fragt die prüfende Person, was im August auf der Seite stand, ist die
  Antwort eine Datei statt einer Erinnerung.
</p>

<h3>Eine Leseliste in Nachweise verwandeln</h3>
<p>
  Mit einer Liste von Adressen liefert der Endpunkt RIS-Einträge, die sich ohne
  Abtippen in Citavi, Zotero oder EndNote importieren lassen — und er
  <a href="/measurements/citation-triage/">nennt die Adressen, die er nicht
  erreicht</a>, sodass diese im Browser geöffnet werden können, statt still
  unterzugehen.
</p>

<h3>Quellen hinter einem Login</h3>
<p>
  Eine Hochschullizenz, ein Bibliotheks-Proxy, eine Fachzeitschrift hinter der
  Bezahlschranke: Kein serverseitiger Leser kann Ihnen dorthin folgen, und drei
  der hier gemessenen Verlage weisen sie kategorisch ab. Eine
  <a href="/tools/full-page-pdf-snap/">Aufnahme-Erweiterung</a> läuft in Ihrer
  eigenen Sitzung mit Ihrem eigenen Zugang — darum gehören beide Wege zusammen,
  statt miteinander zu konkurrieren.
</p>

<h3>Eine lange Seite an ein Sprachmodell geben</h3>
<p>
  Ein durchgehendes Blatt mit echtem, markierbarem Text — aus dem Dokument
  entnommen statt aus Pixeln erkannt — und Seitenumbrüche, die zwischen den
  Zeilen fallen statt durch sie hindurch. Was das Modell liest, ist das, was
  die Seite sagte.
</p>

<h2>Wofür es nicht gut ist</h2>
<ul>
  <li><strong>Den Export des Verlags ersetzen.</strong> Wo eine Artikelseite
    RIS oder BibTeX anbietet, ist diese Datei maßgeblich und dies hier nicht.</li>
  <li><strong>Beweisen, was eine Seite enthielt.</strong> Eine
    Bildschirmaufnahme ist kein qualifiziertes elektronisches Dokument im Sinn
    der eIDAS-Verordnung. Sie hält fest, was ein Browser zu einem genannten
    Zeitpunkt anzeigte, nicht mehr — die Prüfsumme deckt die Datei, nicht die
    Wahrhaftigkeit der Seite.</li>
  <li><strong>Lücken füllen.</strong> Wo eine Plattform keine Seitenzahlen
    ausweist — etwa die Abstract-Seiten von PubMed —, bleibt das Feld leer,
    statt von anderswo geholt und so dargestellt zu werden, als hätte die Seite
    es gesagt.</li>
</ul>

<h2>Grenzen dieser Messung</h2>
<ul>
  <li>Achtzehn Plattformen sind eine Aufnahme der gängigen, keine
    Vollerhebung.</li>
  <li>Europe PMC lief nach 55&nbsp;Sekunden in eine Zeitüberschreitung. Das
    zählt hier als kein Ergebnis, nicht als Fehler der Plattform.</li>
  <li>Drei Verweigerungen (MDPI, ScienceDirect, DOAJ) sind
    Verlagsentscheidungen gegen serverseitige Leser, gemessen an einem
    Nachmittag und veränderlich.</li>
</ul>

</div>

"""


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Measured on 3 August 2026 in one pass from a Cloudflare Workers edge.\n'
        '      Every returned title was checked against Crossref. Raw data:\n'
        '      <a href="/data/2026-08-03-citation-by-platform.json">JSON</a>, CC BY 4.0.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    fuss = fuss.replace("</body>", SPRACHE_SKRIPT + "\n</body>")
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
