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
BESCHREIBUNG = (
    "Given a mixed reading list, an MCP endpoint turned 8 of 12 sources into complete "
    "citations with RIS records in 13 seconds. The other four are blocked to any "
    "server-side reader — and saying so precisely is worth more than guessing."
)


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{TITEL}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": TITEL, "description": BESCHREIBUNG,
        "datePublished": "2026-08-03", "dateModified": "2026-08-03",
        "inLanguage": "en", "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)


def inhalt(d):
    r = d["results"]
    zurueck = "\n".join(
        f'    <tr><td><code>{x["host"]}</code></td><td>{x["reason"]}</td></tr>'
        for x in r["handed_back"])
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    A reading list goes in, citable records come out — for two thirds of it. The
    remaining third is refused by the publishers to any server that asks. What
    makes the endpoint useful is not the two thirds; it is that it names the
    third precisely enough to act on.
  </p>
  <p class="meta">3 August 2026 · {d["method"]["sources"]} sources, one pass ·
    <a href="/data/2026-08-03-citation-triage.json">raw data</a></p>
</header>

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
  <thead><tr><th>Source</th><th>Reason</th></tr></thead>
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
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
