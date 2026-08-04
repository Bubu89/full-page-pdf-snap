#!/usr/bin/env python3
"""build-kompression-teaser.py — kurzer Hinweis auf den Farbtiefe-Modus.

Bewusst knapp und bewusst im Konjunktiv, wo es um den Store geht: Die Fassung
ist gebaut und geladen, aber nicht eingereicht. Eine Zusage ueber ein Datum
waere eine Aussage ueber die Zukunft, und die haelt hier niemand.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "who-actually-reads-this" / "index.html"
ZIEL = DOCS / "notes" / "smaller-files-better-ocr"
DATEI = DOCS / "data" / "2026-08-04-kompression-aufnahme.json"

URL = "https://provinglab.dev/notes/smaller-files-better-ocr/"
TITEL = "A capture at 8.5 % of the size, and OCR reads it slightly better"
BESCHREIBUNG = (
    "Measured 4 August 2026: on a text page, black and white cuts the file to "
    "8.5 % of the current JPEG while Tesseract reads back 989 words against "
    "987 in colour. Built into 2.28.0 as a setting, not a default — on a page "
    "with photographs the same setting falls apart."
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
        "about": {"@type": "Dataset",
                  "name": "Colour depth against file size and OCR recall, 2026-08-04",
                  "license": "https://creativecommons.org/licenses/by/4.0/",
                  "distribution": [{"@type": "DataDownload",
                                    "encodingFormat": "application/json",
                                    "contentUrl": f"https://provinglab.dev/data/{DATEI.name}"}]},
    }
    neu = ('<script type="application/ld+json">\n'
           + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda _: neu, k, count=1, flags=re.S)


def inhalt(d):
    t = d["farbtiefe_2026-08-04"]["textseite"]
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    Our own measurement had the capture at 6.7 MB against 1.1 MB for the
    browser's print export — noted on the comparison page and left there
    without comment. Looking into it turned up something better than a
    compression setting: for a page of text, dropping the colour costs nothing
    that matters and saves almost everything.
  </p>
  <p class="meta">Measured {d["gemessen_am"]} ·
    <a href="/data/{DATEI.name}">raw data</a></p>
</header>

<h2>One page of text, three colour depths</h2>
<table>
  <caption>1400 × 3200 px, lossless compression, OCR with Tesseract 5.3.4</caption>
  <thead><tr><th scope="col">Mode</th><th scope="col">File</th>
    <th scope="col">Share</th><th scope="col">Words read back</th></tr></thead>
  <tbody>
    <tr><th scope="row">Full colour</th><td class="num">{t["rgb_24bit"]["flate_kb"]} kB</td>
        <td class="num">{t["rgb_24bit"]["anteil"]}</td><td class="num">{t["rgb_24bit"]["ocr_woerter"]}</td></tr>
    <tr><th scope="row">Greyscale</th><td class="num">{t["graustufen_8bit"]["flate_kb"]} kB</td>
        <td class="num">{t["graustufen_8bit"]["anteil"]}</td><td class="num">{t["graustufen_8bit"]["ocr_woerter"]}</td></tr>
    <tr><th scope="row">Black and white</th><td class="num"><strong>{t["schwarzweiss_1bit"]["flate_kb"]} kB</strong></td>
        <td class="num"><strong>{t["schwarzweiss_1bit"]["anteil"]}</strong></td><td class="num">{t["schwarzweiss_1bit"]["ocr_woerter"]}</td></tr>
  </tbody>
</table>
<p>
  Against the 1327 kB the current build produces as JPEG, the last row is
  <strong>8.5 %</strong>. And the text recognition does not suffer — it reads
  back <em>two words more</em> than from the colour version, at 99.9 %
  agreement. That is not a coincidence: OCR binarises the image anyway. Handing
  it colour means handing it work it immediately throws away.
</p>

<h2>Why it will not be the default</h2>
<p>
  The same setting on a page of photographs produces a structural similarity of
  <strong>0.199</strong> — the image is gone. No single value is right for both,
  which is why this belongs in the hands of whoever knows what they are
  capturing. A statute, a repository record, a page of tables: black and white.
  A figure, a map, a photograph: colour.
</p>

<h2>What is built, and what is not</h2>
<p>
  The setting exists in <strong>2.28.0</strong>, in both branches, and both
  browsers load that build. Alongside it the capture stopped always embedding
  JPEG: each tile is now compared and the smaller of lossless
  <code>FlateDecode</code> and <code>DCTDecode</code> is used.
</p>
<p>
  <strong>It is not in either store yet.</strong> What is measured is the
  encoding and the recognition; what is not measured is a full capture in a
  real browser, because that needs a genuine input event the test setup cannot
  produce. No date is promised here — the stores currently serve 2.26.0 and
  2.17.0, and this site does not make claims about when that changes.
</p>

<h2>What was checked and rejected</h2>
<p>
  MRC, the standard behind small scanned PDFs, reaches a factor of eight to ten.
  It relies on JBIG2, which replaces similar glyphs with one shared pattern and
  has documented digit substitution. For a tool whose output is meant to serve
  as evidence, a file in which a year could quietly change is worth nothing —
  the saving does not enter into it. WebP and AVIF are not part of PDF at all.
</p>
<p>
  The source details are untouched by any of this. Text layer, metadata and
  image are separate objects in the file; the RIS record and the checksum sit
  beside it. Changing how the image is stored does not change what the capture
  says about where it came from.
</p>

"""


def main():
    d = json.loads(DATEI.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    kopf = anpassen(kopf)
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Method: two synthetic pages at 1400 × 3200 px, one text-heavy and one\n'
        '      image-heavy, each encoded at three colour depths and compressed losslessly. OCR with\n'
        '      Tesseract 5.3.4, German model, output compared to the colour run by sequence\n'
        '      similarity. The structural comparison used here works on luminance and therefore does\n'
        '      not see colour loss — greyscale scores 1.000 despite having none. Synthetic pages, so\n'
        '      the order of magnitude holds and the individual figures do not. Nothing here is legal\n'
        '      advice.\n      <br><br>\n'
        '      Corrections are welcome and are made in public:\n'
        '      <a href="https://github.com/Bubu89/full-page-pdf-snap/issues/19">issue 19</a>.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    text = kopf + inhalt(d) + fuss
    offen = re.findall(r"\{[A-Z_]{3,}\}", text)
    if offen:
        raise SystemExit(f"unaufgeloeste Platzhalter: {set(offen)}")
    (ZIEL / "index.html").write_text(text, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)} ({len(text)} Zeichen)")


if __name__ == "__main__":
    main()
