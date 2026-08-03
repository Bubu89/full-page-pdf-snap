#!/usr/bin/env python3
"""Erzeugt den Beitrag ueber die Arbeitsteilung zwischen Agent und Mensch.

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und gemeinsame Meta-Angaben nicht auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "measurements" / "citation-triage"
DATEN = DOCS / "data" / "2026-08-03-citation-triage.json"

URL = "https://provinglab.dev/measurements/citation-triage/"
TITEL = "An agent can cite eight of twelve sources. The useful part is knowing which four it cannot"
TITEL_DE = ("Ein Agent kann acht von zwölf Quellen zitieren. Wertvoll ist, "
            "dass er die vier benennt, die er nicht kann")
BESCHREIBUNG = (
    "Given a mixed reading list, an MCP endpoint turned 8 of 12 sources into complete "
    "citations with RIS records in 13 seconds. The other four are blocked to any "
    "server-side reader — and saying so precisely is worth more than guessing."
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
    ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": TITEL, "description": BESCHREIBUNG,
        "datePublished": "2026-08-03", "dateModified": "2026-08-03",
        "inLanguage": ["en", "de"], "url": URL,
        "about": ["citation", "MCP endpoint", "bibliography",
                  "Literaturverzeichnis", "Quellennachweis", "Zitieren"],
        "keywords": ("citation endpoint, MCP, extract_citation, reading list, "
                     "Literaturverzeichnis erstellen, Internetquellen zitieren, "
                     "Abrufdatum, RIS, BibTeX, Citavi, Zotero"),
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)


def inhalt(d):
    r = d["results"]
    zurueck = "\n".join(
        f'    <tr><th scope="row"><code>{x["host"]}</code></th><td>{x["reason"]}</td></tr>'
        for x in r["handed_back"])
    # Die Gruende stehen als Rohdaten-Text im JSON; fuer die deutsche Tabelle
    # werden sie uebersetzt, die Zahl der Faelle bleibt dieselbe.
    gruende_de = {
        "http-403": "http-403",
        "bot wall served to server-side readers":
            "Bot-Abwehr-Seite an serverseitige Leser ausgeliefert",
        "near-empty response to server-side readers":
            "nahezu leere Antwort an serverseitige Leser",
    }
    zurueck_de = "\n".join(
        f'    <tr><th scope="row"><code>{x["host"]}</code></th>'
        f'<td>{gruende_de.get(x["reason"], x["reason"])}</td></tr>'
        for x in r["handed_back"])
    return f"""<div class="wrap">

<header>
  <h1 data-lang="en" class="on" lang="en">{TITEL}</h1>
  <h1 data-lang="de" lang="de">{TITEL_DE}</h1>
  <p class="standfirst on" data-lang="en" lang="en">
    A reading list goes in, citable records come out — for two thirds of it. The
    remaining third is refused by the publishers to any server that asks. What
    makes the endpoint useful is not the two thirds; it is that it names the
    third precisely enough to act on.
  </p>
  <p class="standfirst" data-lang="de" lang="de">
    Eine Leseliste geht hinein, zitierfähige Nachweise kommen heraus — für zwei
    Drittel davon. Das restliche Drittel verweigern die Verlage jedem Server,
    der nachfragt. Was den Endpunkt nützlich macht, sind nicht die zwei Drittel,
    sondern dass er das letzte Drittel so genau benennt, dass man damit
    weiterarbeiten kann.
  </p>
  <p class="meta"><span data-lang="en" class="on" lang="en">3 August 2026 · {d["method"]["sources"]} sources, one pass ·
    <a href="/data/2026-08-03-citation-triage.json">raw data</a></span><span data-lang="de" lang="de">3. August 2026 · {d["method"]["sources"]} Quellen, ein Durchlauf ·
    <a href="/data/2026-08-03-citation-triage.json">Rohdaten</a></span></p>
</header>

<div class="lang">
  <button id="b-en" aria-pressed="true" onclick="setLang('en')">English</button>
  <button id="b-de" aria-pressed="false" onclick="setLang('de')">Deutsch</button>
</div>

<div data-lang="en" class="on" lang="en">

<h2>The task</h2>
<p>
  An agent is handed a list of addresses and asked to prepare them for a
  bibliography. For each one it calls <code>extract_citation</code> on this
  site's <a href="/notes/mcp-server-what-it-solves/">MCP endpoint</a>, which
  reads whatever citation data the page declares about itself and returns a
  structured record with RIS and BibTeX.
</p>

<div class="kf-row">
  <div class="kf b"><div class="n">{r["handled_by_the_agent"]}/{d["method"]["sources"]}</div><div class="l">done by the agent</div></div>
  <div class="kf"><div class="n">{r["handed_back_to_the_human"]}</div><div class="l">handed back</div></div>
  <div class="kf"><div class="n">{r["seconds_per_source"]} s</div><div class="l">per source</div></div>
</div>

<h2>What came back for the eight</h2>
<p>
  Complete records — authors, year, container, identifier — each with an RIS
  entry that imports into Citavi, Zotero or EndNote without retyping. A journal
  article from Springer with five authors, a PLOS article, a PubMed Central
  paper, an arXiv preprint, a Wikipedia entry, a Zenodo record, and a bare DOI
  that resolved through the registration agency because the publisher's page
  refused.
</p>
<p>
  Two of the eight carry no author, because the page declares none. That is the
  page's gap, not the reader's — and it is reported as an empty field rather than
  filled in with a guess. A bibliography entry that looks complete and is wrong
  costs more than one with a visible hole.
</p>

<h2>What was handed back, and why</h2>
<table>
  <thead><tr><th scope="col">Source</th><th scope="col">Reason</th></tr></thead>
  <tbody>
{zurueck}
  </tbody>
</table>
<p>
  Every one of these was re-fetched from an unrelated network to check the block
  is real rather than a fault at this end. All four are genuine.
</p>

<h2>Why the refusal is the valuable half</h2>
<p>
  A citation tool that returns something for every URL sounds better and is
  worse. Fed a bot wall, it produces a reference whose title reads
  <em>Making sure you're not a bot!</em> — formatted, complete-looking, and
  worthless. We have <a href="/measurements/citation-extraction/">measured that
  happening</a> to an established service on two of eighteen random sources.
</p>
<p>
  A refusal, by contrast, is actionable. The agent can tell its user exactly
  four addresses to open in a browser, where a
  <a href="/tools/full-page-pdf-snap/">capture extension</a> reaches what no
  server can: the page is loaded in the reader's own session, with the reader's
  own access. The division of labour is not a workaround — it follows from who
  is allowed to see what.
</p>

<h2>What this does not settle</h2>
<ul>
  <li><strong>The split moves.</strong> EUR-Lex began returning a near-empty
    response to server-side readers between two runs on the same day. Any figure
    here is a reading from one afternoon, not a constant.</li>
  <li><strong>Twelve sources is a demonstration, not a study.</strong> The
    <a href="/measurements/citation-extraction/">random-sample measurement</a>
    is the one to cite for coverage; this one shows the shape of the workflow.</li>
  <li><strong>Nothing here beats a publisher's own export.</strong> Where a page
    offers a RIS or BibTeX download, that file is authoritative and this is not.</li>
</ul>

<h2>Trying it</h2>
<pre><code>curl -X POST https://provinglab.dev/mcp \\
  -H 'content-type: application/json' \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{
       "name":"extract_citation",
       "arguments":{{"url":"https://arxiv.org/abs/1706.03762"}}}}}}'</code></pre>
<p>
  No key and no account. Please use it in proportion — it is one small endpoint, and a reading list is a handful of calls, not a crawl. A record comes back with a
  <code>source</code> field saying where the details were read, and a
  <code>warning</code> field that is empty when there is nothing to warn about.
</p>

</div>

<div data-lang="de" lang="de">

<h2>Die Aufgabe</h2>
<p>
  Ein Agent bekommt eine Liste von Adressen und soll sie für ein
  Literaturverzeichnis vorbereiten. Für jede ruft er
  <code>extract_citation</code> am
  <a href="/notes/mcp-server-what-it-solves/">MCP-Endpunkt</a> dieser Seite auf.
  Der Endpunkt liest die Zitationsdaten, die eine Seite über sich selbst
  ausweist, und gibt einen strukturierten Nachweis mit RIS und BibTeX zurück.
</p>

<div class="kf-row">
  <div class="kf b"><div class="n">{r["handled_by_the_agent"]}/{d["method"]["sources"]}</div><div class="l">vom Agenten erledigt</div></div>
  <div class="kf"><div class="n">{r["handed_back_to_the_human"]}</div><div class="l">zurückgegeben</div></div>
  <div class="kf"><div class="n">{r["seconds_per_source"]} s</div><div class="l">pro Quelle</div></div>
</div>

<h2>Was für die acht zurückkam</h2>
<p>
  Vollständige Nachweise — Autoren, Jahr, Publikationsorgan, Identifikator —,
  jeder mit einem RIS-Eintrag, der sich ohne Abtippen in Citavi, Zotero oder
  EndNote importieren lässt. Ein Zeitschriftenartikel von Springer mit fünf
  Autoren, ein PLOS-Artikel, ein Beitrag aus PubMed Central, ein
  arXiv-Preprint, ein Wikipedia-Eintrag, ein Zenodo-Datensatz und ein nackter
  DOI, der über die Registrierungsagentur aufgelöst wurde, weil die Seite des
  Verlags die Antwort verweigerte.
</p>
<p>
  Zwei der acht tragen keinen Autor, weil die Seite keinen ausweist. Das ist
  die Lücke der Seite, nicht die des Werkzeugs — und sie wird als leeres Feld
  gemeldet statt mit einer Vermutung gefüllt. Ein Eintrag im
  Literaturverzeichnis, der vollständig aussieht und falsch ist, kostet mehr
  als einer mit sichtbarer Lücke.
</p>

<h2>Was zurückgegeben wurde — und warum</h2>
<table>
  <thead><tr><th scope="col">Quelle</th><th scope="col">Grund</th></tr></thead>
  <tbody>
{zurueck_de}
  </tbody>
</table>
<p>
  Jede dieser Adressen wurde zur Kontrolle von einem unabhängigen Netz aus
  erneut abgerufen, damit eine Störung auf eigener Seite nicht für eine Sperre
  gehalten wird. Alle vier Sperren sind echt.
</p>

<h2>Warum die Verweigerung die wertvolle Hälfte ist</h2>
<p>
  Ein Zitationswerkzeug, das zu jeder Adresse etwas zurückgibt, klingt besser
  und ist schlechter. Mit einer Bot-Abwehr gefüttert, erzeugt es einen Beleg,
  dessen Titel <em>Making sure you're not a bot!</em> lautet — formatiert,
  vollständig wirkend und wertlos. <a href="/measurements/citation-extraction/">Gemessen
  haben wir das</a> an einem etablierten Dienst, bei zwei von achtzehn zufällig
  gezogenen Quellen.
</p>
<p>
  Eine Verweigerung dagegen lässt sich umsetzen. Der Agent kann genau die vier
  Adressen nennen, die im Browser zu öffnen sind — dort erreicht eine
  <a href="/tools/full-page-pdf-snap/">Aufnahme-Erweiterung</a>, was kein
  Server erreicht: Die Seite lädt in der eigenen Sitzung, mit dem eigenen
  Zugang. Diese Arbeitsteilung ist kein Notbehelf, sie folgt daraus, wer was
  sehen darf.
</p>

<h2>Was hier nicht geklärt ist</h2>
<ul>
  <li><strong>Die Aufteilung verändert sich.</strong> EUR-Lex begann zwischen
    zwei Durchläufen am selben Tag, serverseitigen Lesern eine nahezu leere
    Antwort zu schicken. Jede Zahl hier ist ein Messwert eines Nachmittags,
    keine Konstante.</li>
  <li><strong>Zwölf Quellen sind eine Demonstration, keine Studie.</strong>
    Zitierfähig für die Abdeckung ist die
    <a href="/measurements/citation-extraction/">Messung an der
    Zufallsstichprobe</a>; diese hier zeigt die Form des Arbeitsablaufs.</li>
  <li><strong>Nichts davon schlägt den Export des Verlags selbst.</strong> Wo
    eine Seite RIS oder BibTeX zum Herunterladen anbietet, ist diese Datei
    maßgeblich und dies hier nicht.</li>
</ul>

<h2>Selbst ausprobieren</h2>
<pre><code>curl -X POST https://provinglab.dev/mcp \\
  -H 'content-type: application/json' \\
  -d '{{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{{
       "name":"extract_citation",
       "arguments":{{"url":"https://arxiv.org/abs/1706.03762"}}}}}}'</code></pre>
<p>
  Kein Schlüssel, kein Konto. Bitte im Verhältnis nutzen — es ist ein kleiner
  Endpunkt, und eine Leseliste ist eine Handvoll Aufrufe, kein Crawl. Der
  Nachweis kommt mit einem <code>source</code>-Feld zurück, das angibt, wo die
  Einzelheiten gelesen wurden, und einem <code>warning</code>-Feld, das leer
  ist, wenn es nichts zu warnen gibt.
</p>

</div>

"""


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Measured on 3 August 2026 in a single pass from a Cloudflare Workers edge.\n'
        '      Every refusal was re-checked from an unrelated network. Raw data:\n'
        '      <a href="/data/2026-08-03-citation-triage.json">JSON</a>, CC BY 4.0.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    fuss = fuss.replace("</body>", SPRACHE_SKRIPT + "\n</body>")
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
