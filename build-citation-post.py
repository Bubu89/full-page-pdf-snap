#!/usr/bin/env python3
"""Erzeugt den Beitrag zur Messung der serverseitigen Zitationserfassung.

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und gemeinsame Meta-Angaben nicht auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "measurements" / "citation-extraction"
DATEN = DOCS / "data" / "2026-08-02-citation-extraction.json"

URL = "https://provinglab.dev/measurements/citation-extraction/"
TITEL = "Measured against Citoid: same citations, three times faster, none invented"
BESCHREIBUNG = (
    "A citation reader is only as good as the one it replaces. Against Citoid, the Wikimedia service built on the Zotero translators, across 26 sources in twelve fields: 8 complete citations each, 0.34 s against 1.63 s, and two references Citoid built out of bot walls."
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
        "datePublished": "2026-08-02", "dateModified": "2026-08-02",
        "inLanguage": "en", "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)
    return k


def tabelle(d):
    """Je Fachgebiet eine Zeile: was kam zurueck, was nicht."""
    nach_fach = {}
    for p in d["per_source"]:
        nach_fach.setdefault(p["field"], []).append(p)
    zeilen = []
    for fach, eintraege in nach_fach.items():
        rec = [e for e in eintraege if e["outcome"] == "record"]
        namen = ", ".join(e["source"] for e in rec) or "—"
        blockiert = ", ".join(f"{e['source']} ({e['block_reason']})"
                              for e in eintraege if e["outcome"] == "blocked") or "—"
        zeilen.append(f"    <tr><td>{fach}</td><td>{len(rec)}/{len(eintraege)}</td>"
                      f"<td>{namen}</td><td>{blockiert}</td></tr>")
    return "\n".join(zeilen)


def inhalt(d):
    r0 = d["results"]; s = r0["seconds"]; c = d["comparison"]
    r = {"records_complete_ours": c["complete_citations"]["ours"],
         "records_complete_citoid": c["complete_citations"]["citoid"],
         "any_ours": c["any_record"]["ours"], "any_citoid": c["any_record"]["citoid"],
         "med_ours": c["median_seconds"]["ours"], "med_citoid": c["median_seconds"]["citoid"],
         "slow_ours": c["slowest_seconds"]["ours"], "slow_citoid": c["slowest_seconds"]["citoid"],
         "records_returned": r0["records_returned"], "blocks_reported": r0["blocks_reported"],
         "type_classification_correct": r0["type_classification_correct"],
         "false_block_reports": r0["false_block_reports"]}
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    An endpoint that turns a URL into a citation sounds like a solved problem.
    It is not: half the sources a student would actually cite refuse to answer a
    server at all. Here is which half, how fast the other half answers, and the
    number that decides whether the answers can be trusted.
  </p>
  <p class="meta">2 August 2026 · {len(d['per_source'])} sources, twelve fields, two runs each ·
    <a href="/data/2026-08-02-citation-extraction.json">raw data</a></p>
</header>

<h2>What was measured</h2>
<p>
  The <code>extract_citation</code> tool on this site's
  <a href="/notes/mcp-server-what-it-solves/">MCP endpoint</a> is given nothing but an
  address. It fetches the page, reads whatever citation metadata the page declares
  about itself — Highwire <code>citation_*</code> tags, Dublin Core, PRISM,
  schema.org, OpenGraph — and returns a structured record with RIS and BibTeX.
  No citation service is queried, so nothing learns what is being read.
</p>

<h2>The comparison that decides it</h2>
<p>
  A hit rate on its own says nothing. <a href="https://www.mediawiki.org/wiki/Citoid">Citoid</a>
  — the Wikimedia service that turns a URL into a citation, built on the Zotero
  translators — was given the same {len(d['per_source'])} addresses in the same order.
</p>
<table>
  <thead><tr><th></th><th>This endpoint</th><th>Citoid</th></tr></thead>
  <tbody>
    <tr><td>Complete citations</td><td class="num win">{r['records_complete_ours']}</td><td class="num">{r['records_complete_citoid']}</td></tr>
    <tr><td>Any record returned</td><td class="num">{r['any_ours']}</td><td class="num win">{r['any_citoid']}</td></tr>
    <tr><td><strong>References built from a block page</strong></td><td class="num win">0</td><td class="num">2</td></tr>
    <tr><td>Median seconds</td><td class="num win">{r['med_ours']}</td><td class="num">{r['med_citoid']}</td></tr>
    <tr><td>Slowest single call</td><td class="num win">{r['slow_ours']}</td><td class="num">{r['slow_citoid']}</td></tr>
  </tbody>
</table>
<p>
  <strong>The same eight complete citations, in a third of the time.</strong> Citoid
  returns a record more often — twenty against thirteen — but that is where the
  second row matters: two of those extra records are references to a bot wall.
  For EconStor and SSOAR, Citoid returned <em>Making sure you&#8217;re not a bot!</em>
  as the title of the work. Formatted, complete-looking, and worthless.
</p>
<p>
  That is the whole argument for refusing to answer. A reference that looks right
  and is not costs more than a gap does: the gap is visible while you write, the
  wrong entry is discovered by whoever marks the work.
</p>
<p>
  It runs both ways. Citoid reaches three publishers that block us — MDPI, PeerJ
  and the OECD — and those are real losses, not rounding. We reach two it misses,
  Zenodo and Wikipedia. On coverage the two are close; on what they do when
  coverage fails, they are not.
</p>

<h2>By field</h2>
<table>
  <thead><tr><th>Field</th><th>Returned</th><th>Sources that answered</th><th>Sources that refused</th></tr></thead>
  <tbody>
{tabelle(d)}
  </tbody>
</table>

<h2>The number that matters more than the hit rate</h2>
<p>
  <strong>Zero false alarms.</strong> Every one of the {r['blocks_reported']} refusals was
  re-fetched from an unrelated network with a browser user-agent. All thirteen were
  real: same 403, same 404, same bot wall. And in the other direction, all
  {r['records_returned']} records that were returned carried every required field —
  authors, year, container, identifier — and were classified into the right kind of
  source, from journal article through preprint to legal text.
</p>
<p>
  This matters more than coverage because of what the failure mode would be. A
  reader that invents a reference from an error page produces a bibliography entry
  that looks correct and is not. Half an answer is usable; a confident wrong answer
  is not.
</p>

<h2>Speed</h2>
<table>
  <thead><tr><th></th><th>Seconds</th></tr></thead>
  <tbody>
    <tr><td>Endpoint alone, no page fetched</td><td class="num">{s['baseline_no_fetch']}</td></tr>
    <tr><td>Median, all calls</td><td class="num">{s['median_all']}</td></tr>
    <tr><td>Median, successful lookup</td><td class="num">{s['median_successful']}</td></tr>
    <tr><td>Median, refusal</td><td class="num">{s['median_blocked']}</td></tr>
    <tr><td>95th percentile</td><td class="num">{s['p95']}</td></tr>
    <tr><td>Slowest single call</td><td class="num">{s['slowest']}</td></tr>
  </tbody>
</table>
<p>
  Roughly six tenths of a second is the fetch; the rest is the endpoint. A refusal
  costs a third of a success, because a blocked page is small. The slowest call —
  {s['slowest']} s, an Austrian consolidated statute — is a page of several hundred
  kilobytes, and the time is spent transferring it, not parsing it. Two runs of the
  same address differed by up to 176 %: <strong>this measures the target site, not
  the endpoint.</strong>
</p>

<h2>Two things that went wrong while measuring</h2>
<p>
  The first run returned <code>HTTP 403</code> for all 26 sources, each in 0.13 s —
  far too fast for a real fetch, which is how it was caught. The cause was the
  measuring script, not the pipeline: Python's <code>urllib</code> sends
  <code>Python-urllib/3.x</code>, and Cloudflare's bot protection rejects exactly
  that signature. <code>requests</code>, <code>node-fetch</code>, Go's client, a
  browser and an MCP client all pass. Worth knowing for anyone connecting to this
  endpoint from a script.
</p>
<p>
  The second was subtler. Fetched pages were cached at the edge for five minutes.
  A bot wall answers with <code>HTTP 200</code>, so it cached like any page — and a
  freshly deployed detection for bot walls then ran against the stored response and
  could not take effect at all. Caching for this tool is now off. A citation is
  worth an extra fetch.
</p>

<h2>What this says about the two ways to save a source</h2>
<p>
  One source in this set makes the point cleanly. SSOAR, a German social-science
  repository, serves the real page to a desktop browser and a bot wall to Cloudflare
  worker addresses. The endpoint cannot read it. A
  <a href="/tools/full-page-pdf-snap/">browser extension</a> running in the reader's
  own session can, because it is not a third party — it is the reader.
</p>
<p>
  So the two are not competitors. The endpoint is fast, needs no installation and
  works for open sources; it fails at exactly the publishers whose material sits
  behind a login a student already has. The extension covers those and cannot be
  called from a script. Anyone building a citation workflow needs both, and should
  know which one is answering.
</p>

<h2>Questions</h2>
<h3>Why not resolve the DOI through Crossref when the page refuses?</h3>
<p>
  It would raise coverage. It would also tell Crossref which paper is being read,
  every time. For the sources measured here it would have added nothing to the
  thirteen that worked — they already declare the full record — and the thirteen
  that failed mostly failed before a DOI was ever found. The trade was not worth it.
</p>
<h3>Is 50 % good?</h3>
<p>
  It is the honest number for a server-side reader in August 2026, and it will get
  worse rather than better as publishers tighten bot defences. Which is the
  argument for reading a page where the reader already is, rather than asking a
  server to do it from somewhere else.
</p>

"""


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Measured on 2 August 2026 from a Cloudflare Workers edge in Frankfurt,\n'
        '      two runs per address, system load 0.25 at the start. Every reported refusal\n'
        '      was re-checked from an unrelated network. Raw data:\n'
        '      <a href="/data/2026-08-02-citation-extraction.json">JSON</a>, CC BY 4.0.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
