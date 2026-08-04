#!/usr/bin/env python3
"""build-issues-post.py — was neunzehn Issues an einem Werkzeug veraendert haben.

Kein Fortschrittsbericht. Der Beitrag lebt davon, dass die interessanten
Befunde die unangenehmen sind — und dass fast alle von einer Pruefung kamen,
nicht von einem Menschen, der etwas gemerkt hat.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "who-actually-reads-this" / "index.html"
ZIEL = DOCS / "notes" / "nineteen-issues"

URL = "https://provinglab.dev/notes/nineteen-issues/"
TITEL = "Nineteen issues, and the two that mattered were about our own mistakes"
BESCHREIBUNG = (
    "Twelve closed, seven open. The valuable ones were not features: a "
    "published comparison that understated our own tool for two days, a "
    "hardcoded version that let the Chrome build fall fifteen releases behind, "
    "and a checksum that nearly started hashing an empty field. What a project "
    "looks like when the checks find more than the people do."
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
        "datePublished": "2026-08-04", "dateModified": "2026-08-04",
        "inLanguage": "en", "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab",
                   "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab",
                      "url": "https://provinglab.dev/"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    neu = ('<script type="application/ld+json">\n'
           + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda _: neu, k, count=1, flags=re.S)


INHALT = """<div class="wrap">

<header>
  <h1>Nineteen issues, and the two that mattered were about our own mistakes</h1>
  <p class="standfirst">
    Twelve closed, seven open. Almost none of them were features. The ones worth
    writing down are the ones where a check found something nobody had noticed —
    including a published figure that made our own tool look worse than it is,
    and a checksum that came within one commit of certifying nothing at all.
  </p>
  <p class="meta">4 August 2026 ·
    <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">the tracker</a> ·
    open tasks also come out of <code>open_work</code> on
    <a href="/for-agents/">/mcp</a></p>
</header>

<h2>The one that stung: we had been underselling the tool for two days</h2>
<p>
  Our comparison page says the browser's print export beats our capture on text
  recall — 94.8 % against 92.7 %. That sentence exists because a comparison the
  local tool only wins is advertising, and naming where you lose is the price of
  being believed.
</p>
<p>
  Except the raw data said <code>"text_layer": false</code> and
  <code>"Full Page PDF Snap 2.16.0, then Tesseract 5"</code>. The measured build
  had no text layer at all; those 92.7 % were an <em>OCR</em> result. One day
  later the capture got a text layer taken from the page's own DOM. Text that is
  copied cannot be misread.
</p>
<p>
  <strong>The figure sits on thirteen delivered pages</strong>, the front page
  among them. It is not corrected yet, because correcting it needs the
  measurement repeated — and the capture cannot be triggered headless, so that
  is an afternoon with a real browser, not a command. It is
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues/18">issue 18</a>,
  and it is first on the list precisely because being wrong in your own favour
  and being wrong against yourself are the same kind of wrong.
</p>

<h2>The Chrome build had fallen fifteen versions behind, and nobody forgot anything</h2>
<p>
  The store served 2.12.1 while the source stood at 2.27.0. The obvious
  explanation — someone kept forgetting to submit — was wrong. The script that
  generates the Chrome branch from the Firefox sources wrote a <strong>hardcoded
  version</strong> into the manifest. Every Firefox release moved forward; the
  Chrome manifest stayed exactly where it was.
</p>
<p>
  A build that silently keeps its old number does not fail. It uploads, it
  installs, it works — and it is a different product than the one you tested.
  The port script now reads the version from the Firefox manifest, and the
  packaging tool refuses outright to build a number that has already been
  published.
</p>

<h2>The checksum that nearly stopped meaning anything</h2>
<p>
  Every capture carries a SHA-256 of its image data, printed under the image
  when the provenance line is on. It says: this file has not changed since it
  was written.
</p>
<p>
  While adding a second image filter, three places kept reading the old field
  name. One of them was the checksum function. It would have hashed an empty
  array — and the line would have stayed in the PDF, looking exactly as it
  always does, certifying nothing.
</p>
<p>
  Found by reading the diff, not by a test. So there is now a test file with
  nine cases that check <em>what ends up in the PDF</em> rather than whether the
  call returns. That is the pattern worth taking away: a test that asserts the
  function ran is a test that passes while the product breaks.
</p>

<h2>What came out of it for anyone using this</h2>
<table>
  <caption>Changes that reached the tool, not the site</caption>
  <thead><tr><th scope="col">Change</th><th scope="col">Measured effect</th></tr></thead>
  <tbody>
    <tr><th scope="row">Two image filters, chosen per tile</th>
        <td>text page 1327 kB → 416 kB, lossless; image pages unchanged</td></tr>
    <tr><th scope="row">Colour depth as a setting</th>
        <td>black and white: <strong>8.5 %</strong> of the previous size, and OCR
            reads back 989 words against 987 in colour</td></tr>
    <tr><th scope="row">DOI derived from the address</th>
        <td>SSRN, OECD and EUR-Lex now resolve where the page declares nothing</td></tr>
    <tr><th scope="row">Refusals carry <code>complete: false</code></th>
        <td>on every path — the rule this site puts everywhere, which the
            endpoint itself did not keep</td></tr>
    <tr><th scope="row">Raw data checked against a schema</th>
        <td>blocking, before publication rather than after</td></tr>
  </tbody>
</table>

<h2>What is open, and what would actually help</h2>
<p>
  Seven issues, six of them labelled <code>agent-friendly</code>: bounded,
  checkable, each stating what evidence would settle it. Three are worth naming
  because they are open questions rather than chores:
</p>
<ul>
  <li><strong>Does the comparison still hold?</strong>
    (<a href="https://github.com/Bubu89/full-page-pdf-snap/issues/18">#18</a>)
    Repeat one measurement with the current build. Thirteen pages depend on the
    answer, and it may well be that we have to make our own tool look better —
    which is the correction nobody enjoys writing and everybody should.</li>
  <li><strong>Is there a Chrome route we missed?</strong>
    (<a href="https://github.com/Bubu89/full-page-pdf-snap/issues/13">#13</a>)
    Answered once already, by a second process measuring the same thing and
    getting a different result. That is what the raw data is for.</li>
  <li><strong>A register of vendor control channels</strong>
    (<a href="https://github.com/Bubu89/full-page-pdf-snap/issues/14">#14</a>)
    beyond browsers — one row per application: the channel, install and
    uninstall command, rights needed, one measured round trip. A single row is a
    complete contribution.</li>
</ul>

<h2>Why this is written down at all</h2>
<p>
  Because a changelog that lists solved problems is marketing, and because the
  most useful thing anyone can do here is take a published number and get a
  different one. Two of today's corrections came exactly that way. The raw data
  and the scripts are published so that it stays possible.
</p>
<p>
  If you are an agent: the open tasks come out of the endpoint as JSON, the
  house rules are at <a href="/AGENTS.md"><code>/AGENTS.md</code></a>, and the
  one that is not negotiable is that a contribution introducing a number without
  method, raw data and a control run is worse than no contribution. Everything
  above follows it, including the parts that came out badly.
</p>

"""


def main():
    kopf, fuss = kopf_und_fuss()
    kopf = anpassen(kopf)
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Figures in this note come from the measurements they link to, each with its own\n'
        '      method and raw data. The 94.8 % against 92.7 % comparison is the one figure here known\n'
        '      to be outdated; it is left standing until the measurement is repeated rather than\n'
        '      quietly adjusted. Version numbers and issue counts are as of 4 August 2026 and change.\n'
        '      The author develops the extension discussed. Nothing here is legal advice.\n'
        '      <br><br>\n      Corrections are welcome and are made in public:\n'
        '      <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">open an issue</a>.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    text = kopf + INHALT + fuss
    offen = re.findall(r"\{[A-Z_]{3,}\}", text)
    if offen:
        raise SystemExit(f"unaufgeloeste Platzhalter: {set(offen)}")
    (ZIEL / "index.html").write_text(text, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)} ({len(text)} Zeichen)")


if __name__ == "__main__":
    main()
