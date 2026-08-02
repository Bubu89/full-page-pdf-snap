#!/usr/bin/env python3
"""Erzeugt den Beitrag über den MCP-Server dieser Seite.

Kopf und Fuß stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und gemeinsame Meta-Angaben nicht auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "notes" / "mcp-server-what-it-solves"

URL = "https://provinglab.dev/notes/mcp-server-what-it-solves/"
TITEL = "This site runs an MCP server. Measured: it is smaller than the file it competes with"
BESCHREIBUNG = (
    "An MCP endpoint at /mcp exposes the measurement datasets and published methods to "
    "AI clients. Everything it can return adds up to roughly 1,300 tokens — less than "
    "the llms.txt file that already sits on the same domain. What that leaves it good "
    "for, and what it does not solve."
)


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    for feld in ("canonical",):
        k = re.sub(rf'(<link rel="{feld}" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
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


INHALT = """<div class="wrap">

<header>
  <h1>This site runs an MCP server. Measured: it is smaller than the file it competes with</h1>
  <p class="standfirst">
    Since 2 August 2026 there is an endpoint at <code>/mcp</code> that hands the
    measurement datasets and the published methods to an AI client on request.
    Before recommending that anyone else build one, here is what it actually
    returns — and the number that decides whether it was worth it.
  </p>
  <p class="meta">2 August 2026 · Protocol MCP 2025-06-18 · transport streamable HTTP ·
    <a href="/.well-known/mcp/server-card.json">server card</a></p>
</header>

<h2>What it can do</h2>
<p>
  Three tools, no authentication, no state:
</p>
<table>
  <thead><tr><th>Tool</th><th>Input</th><th>Returns</th></tr></thead>
  <tbody>
    <tr><td><code>list_measurements</code></td><td>none</td>
        <td>every measurement with its dataset URL and the page documenting the method</td></tr>
    <tr><td><code>get_measurement_data</code></td><td><code>dataset</code></td>
        <td>one dataset as JSON — measured values, control run, conditions</td></tr>
    <tr><td><code>get_method</code></td><td><code>name</code> (optional)</td>
        <td>a reproducible method, or the list of them</td></tr>
  </tbody>
</table>

<h2>The number that matters</h2>
<p>
  Everything the server can return, added together, is about
  <strong>1,300 tokens</strong>. The <a href="/llms.txt">llms.txt</a> file on the
  same domain — a plain text summary any model can read in one request — is about
  <strong>1,988 tokens</strong>.
</p>
<p>
  So a model that simply reads one text file ends up with <em>more</em> context than
  one that calls all three tools. The protocol solves a size problem this site does
  not have. That is worth saying plainly, because the opposite is usually implied:
  an MCP server sounds like capability, and here it mostly is not.
</p>

<h2>Where it earns its place anyway</h2>
<p>
  One thing it does that a text file cannot: <strong>it makes a number
  checkable at the moment of use.</strong> Asked how much text survives OCR on a
  screenshot, a model can either recall something approximate or call
  <code>get_measurement_data</code> and read 92.6&nbsp;% out of the dataset, along
  with the control run that makes the figure meaningful. The second answer can be
  verified; the first cannot.
</p>
<p>
  Two smaller advantages follow from the same property. The data is structured —
  JSON rather than prose, so it can go straight into a calculation. And it is
  current: llms.txt is maintained by hand and drifts, the endpoint reads the same
  files the site serves.
</p>

<h2>What it does not solve</h2>
<ul>
  <li><strong>Reach.</strong> No one finds a site because it has an MCP endpoint.
    The server has served a few dozen calls, essentially all of them our own tests.</li>
  <li><strong>Discovery.</strong> A client has to be told the address. The
    <a href="/.well-known/mcp/server-card.json">server card</a> helps only clients
    that already look there.</li>
  <li><strong>Anything at scale.</strong> Five datasets and three methods fit in
    any context window. At fifty the calculus reverses — that is when the endpoint
    starts to pay for itself.</li>
</ul>

<h2>How to connect it</h2>
<p>
  The endpoint speaks JSON-RPC 2.0 over HTTP POST. Authentication is offered but
  <strong>not required</strong>; anonymous requests get identical answers.
</p>
<pre><code>curl -X POST https://provinglab.dev/mcp \\
  -H 'content-type: application/json' \\
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'</code></pre>
<p>
  In a client that supports remote MCP servers, add
  <code>https://provinglab.dev/mcp</code> as a streamable-HTTP connector. A
  <code>GET</code> on the endpoint answers 405: the server is stateless and opens no
  server-initiated stream, which the specification permits.
</p>

<h2>Questions</h2>
<h3>Why build it if the numbers say it barely helps?</h3>
<p>
  Because the cost was one file and the failure mode is bounded: if the worker
  breaks, it falls back to serving the site unchanged. And because the claim
  "measurements you can verify" should survive contact with an agent that wants to
  verify them. What would not have been defensible is publishing the endpoint and
  implying it does more than it does.
</p>
<h3>Is anything protected behind it?</h3>
<p>
  No. Every resource on this domain is public. An OAuth flow exists because some
  clients refuse to connect without one — it grants no access beyond anonymous, and
  <a href="/auth.md">auth.md</a> says so in its first paragraph.
</p>

"""


def main():
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Token counts are estimates at four characters per token, measured on the\n'
        '      responses of 2 August 2026. The endpoint is operated by the author of this\n'
        '      site; the figures it returns come from the measurements published here.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + INHALT + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
