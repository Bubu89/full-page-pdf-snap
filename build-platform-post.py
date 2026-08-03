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
BESCHREIBUNG = (
    "Which platforms declare citation data a reader can use? Eleven of eighteen returned "
    "a record, ten of them complete. The most complete record of all came from the DOI "
    "resolver — not from the article page."
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
    ld = {"@context": "https://schema.org", "@type": "TechArticle",
          "headline": TITEL, "description": BESCHREIBUNG,
          "datePublished": "2026-08-03", "dateModified": "2026-08-03",
          "inLanguage": "en", "url": URL,
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
  <h1>{TITEL}</h1>
  <p class="standfirst">
    A reference is only as good as the data behind it. Eighteen platforms a
    researcher would plausibly use were asked what they declare about their own
    articles. Eleven answered; the most complete answer did not come from an
    article page at all.
  </p>
  <p class="meta">3 August 2026 · {len(r["per_platform"])} platforms, one pass ·
    <a href="/data/2026-08-03-citation-by-platform.json">raw data</a></p>
</header>

<div class="kf-row">
  <div class="kf b"><div class="n">{r["returned_data"]}/{len(r["per_platform"])}</div><div class="l">returned a record</div></div>
  <div class="kf"><div class="n">{r["complete_authors_and_year"]}</div><div class="l">with authors and year</div></div>
  <div class="kf"><div class="n">{r["title_matched_crossref"]}</div><div class="l">titles confirmed by Crossref</div></div>
</div>

<h2>What each platform declares</h2>
<table>
  <thead><tr><th>Platform</th><th>Authors</th><th>Year</th><th>DOI</th><th>Pages</th><th>ISSN</th><th>s</th></tr></thead>
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
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
