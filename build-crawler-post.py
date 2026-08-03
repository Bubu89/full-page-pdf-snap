#!/usr/bin/env python3
"""build-crawler-post.py — die Seite, die offenlegt, wer hier tatsaechlich liest.

Die Zahlen kommen aus `tools/crawler-bericht.py`. Diese Datei formt sie.
Beide getrennt, damit ein Neubau der Seite keine neue Erhebung ausloest — sonst
stuende bei jedem Bau ein anderer Stand drin, und die Seite waere nicht mehr
reproduzierbar.
"""
import datetime
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "android-capture-extensions" / "index.html"
ZIEL = DOCS / "notes" / "who-actually-reads-this"
DATEN = DOCS / "data" / "ki-crawler-aktuell.json"
TAGE_FRISCH = 7

URL = "https://provinglab.dev/notes/who-actually-reads-this/"
TITEL = "Who actually reads this site: 24 hours of crawler logs, published"
BESCHREIBUNG = (
    "AI systems made more requests to this site than search engines did — "
    "299 against 282 in 24 hours, on a domain two days old. ClaudeBot and "
    "GPTBot lead. Twenty requests carrying AI user agents were not reading at "
    "all but scanning for /keys.json and /.git/HEAD, and are counted "
    "separately. Self-reported figures with the query published."
)


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf, d):
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
        "datePublished": d["stand"][:10], "dateModified": d["stand"][:10],
        "inLanguage": "en", "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab",
                   "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab",
                      "url": "https://provinglab.dev/"},
        "about": {
            "@type": "Dataset",
            "name": f"AI crawler and search engine requests to provinglab.dev, {d['stand'][:10]}",
            "description": ("Requests grouped by user agent over a 24-hour window, "
                            "separating reading traffic from credential scans that "
                            "carry AI user agents."),
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "distribution": [{"@type": "DataDownload",
                              "encodingFormat": "application/json",
                              "contentUrl": f"https://provinglab.dev/data/{DATEN.name}"}],
        },
    }
    neu = ('<script type="application/ld+json">\n'
           + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda _: neu, k, count=1, flags=re.S)


def zeilen(gruppe, gesamt):
    aus = []
    for name, v in gruppe.items():
        anteil = 100 * v["anfragen"] / gesamt if gesamt else 0
        aus.append(f'      <tr><th scope="row">{name}</th>'
                   f'<td class="num">{v["anfragen"]}</td>'
                   f'<td class="num">{v["bytes"]/1024:.0f} kB</td>'
                   f'<td class="num">{anteil:.0f} %</td></tr>')
    return "\n".join(aus)


def scan_zeilen(d):
    return "\n".join(
        f'      <tr><th scope="row">{name}</th>'
        f'<td class="num">{v["anfragen"]}</td>'
        f'<td><code>{"</code>, <code>".join(v["gesuchte_pfade"][:3])}</code></td></tr>'
        for name, v in d["scans_mit_ki_kennzeichen"].items())


def inhalt(d):
    s = d["summe"]
    alter = (datetime.datetime.now(datetime.UTC)
             - datetime.datetime.strptime(d["stand"], "%Y-%m-%dT%H:%M:%SZ")
             .replace(tzinfo=datetime.UTC)).days
    veraltet = ""
    if alter > TAGE_FRISCH:
        veraltet = (f'\n<p class="standfirst" style="border-left:3px solid #c93;padding-left:1rem">'
                    f'<strong>These figures are {alter} days old.</strong> They were current when '
                    f'written and have not been refreshed since. Treat them as a snapshot of '
                    f'{d["stand"][:10]}, not as the present state.</p>\n')
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    Plenty is claimed about AI crawlers and very little is shown. Anyone running
    a site can see in their own logs which systems actually arrive, what they
    take and how often — and almost nobody publishes it. Here is one day of it,
    with the query that produced it.
  </p>
  <p class="meta">Collected {d["stand"][:10]} · {d["fenster_stunden"]} h window ·
    <a href="/data/{DATEN.name}">raw data</a></p>
</header>
{veraltet}
<h2>The headline</h2>
<p>
  <strong>AI systems made more requests than search engines did</strong> —
  {s["ki_anfragen"]} against {s["such_anfragen"]}. The search engines pulled
  more data ({s["such_bytes"]/1024/1024:.1f} MB against
  {s["ki_bytes"]/1024/1024:.1f} MB), because Googlebot fetches images and
  stylesheets that a language model has no use for.
</p>
<p>
  This domain was registered on 1 August 2026. It is two days old, ranks for
  nothing, and has no inbound links worth counting — and seven distinct AI
  systems have already read it.
</p>

<h2>AI systems</h2>
<table>
  <caption>Requests by AI user agent, {d["fenster_stunden"]} hours to {d["stand"][:16].replace("T", " ")} UTC</caption>
  <thead><tr><th scope="col">System</th><th scope="col">Requests</th>
    <th scope="col">Data</th><th scope="col">Share</th></tr></thead>
  <tbody>
{zeilen(d["ki_systeme"], s["ki_anfragen"])}
  </tbody>
</table>

<h2>Search engines, for comparison</h2>
<table>
  <caption>Same window, conventional crawlers</caption>
  <thead><tr><th scope="col">Crawler</th><th scope="col">Requests</th>
    <th scope="col">Data</th><th scope="col">Share</th></tr></thead>
  <tbody>
{zeilen(d["suchmaschinen"], s["such_anfragen"])}
  </tbody>
</table>
<p>
  YandexBot at {d["suchmaschinen"].get("YandexBot", {}).get("anfragen", 0)} requests is
  within reach of Googlebot, which is not the ratio most sites see. Bingbot at
  {d["suchmaschinen"].get("Bingbot", {}).get("anfragen", 0)} is the surprise in the other
  direction.
</p>

<h2>Twenty requests were not reading</h2>
<p>
  Separated out rather than counted: requests carrying an AI user agent that went
  straight for files nobody links to.
</p>
<table>
  <caption>Credential scans arriving under AI or crawler user agents</caption>
  <thead><tr><th scope="col">User agent claimed</th><th scope="col">Requests</th>
    <th scope="col">Paths sought</th></tr></thead>
  <tbody>
{scan_zeilen(d)}
  </tbody>
</table>
<p>
  <strong>A user agent is not an identity.</strong> It is a string the client
  chooses. Whether these came from the named operators or from someone borrowing
  their name cannot be determined from this side, and this page does not claim
  to know. What can be said: they were not reading, all of them got 404, and
  nothing they sought exists here.
</p>

<h2>What the AI systems actually fetched</h2>
<p>
  The most-requested paths across all of them are the machine-readable ones —
  <code>/sitemap.xml</code>, <code>/llms.txt</code>, <code>/mcp</code> — before
  the articles. That is the whole argument for maintaining those files: they are
  not decoration, they are what gets read first.
</p>

<h2>What this is not</h2>
<p>
  <strong>These numbers cannot be checked from outside.</strong> They come from
  our own provider's analytics, retrieved with a token only the operator holds.
  Nobody can recompute them. What is published instead is the method: the query
  runs in
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/tools/crawler-bericht.py"><code>tools/crawler-bericht.py</code></a>,
  in plain text, and anyone with a Cloudflare zone can run the same one against
  their own.
</p>
<p>
  So this is a self-report with a disclosed method, not a measurement someone
  could repeat. Everywhere else on this site that distinction is the point, and
  it would be dishonest to blur it here because the numbers happen to be
  flattering.
</p>
<p>
  Two further limits. One day is one day — a crawler that visits weekly is
  invisible in it. And requests are counted at the edge, so a system reading a
  cached copy through an intermediary never appears at all.
</p>

"""


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    kopf = anpassen(kopf, d)
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Method: Cloudflare GraphQL Analytics, <code>httpRequestsAdaptiveGroups</code>,\n'
        '      grouped by user agent over a 24-hour window, collected ' + d["stand"][:10] + '. Requests\n'
        '      for paths that only a scanner seeks are separated out and not counted as reading. The\n'
        '      query is published; the underlying log is not accessible to anyone but the operator,\n'
        '      so these figures are a self-report and are labelled as one. A user agent can be set\n'
        '      freely and is not proof of origin. Nothing here is legal advice.\n      <br><br>\n'
        '      Corrections are welcome and are made in public:\n'
        '      <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">open an issue</a>.\n'
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
