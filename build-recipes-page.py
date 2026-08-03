#!/usr/bin/env python3
"""Baut /recipes/ — die Rezepte, mit denen der Endpunkt benutzt wird.

Warum eine eigene Seite und kein Abschnitt in der Notiz: die Notiz begruendet,
ob der Server sich lohnt. Wer ihn benutzen will, sucht nicht nach einer
Begruendung, sondern nach einer Zeile zum Einfuegen.

Jedes Rezept hier wurde am 03.08.2026 ausgefuehrt, bevor es aufgeschrieben
wurde. Ein ungetestetes Rezept ist eine Behauptung.

    python3 build-recipes-page.py
"""
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "mcp-server-what-it-solves" / "index.html"

TITEL = "Recipes: turn a web source into a citation"
BESCHREIBUNG = ("Copy-paste recipes for the citation endpoint: Claude Code, Claude Desktop, "
                "the terminal, WSL and Python. Each one was run before it was written down.")

RUMPF = """
<p class="crumb"><a href="../">Proving Lab</a> · Recipes</p>

<header>
  <h1>Recipes: turn a web source into a citation</h1>
  <p class="standfirst">
    Short, complete instructions for the citation endpoint at
    <code>/mcp</code> — in a terminal, in WSL, in Python, and in AI tools that
    speak MCP. Every one of them was run on 3 August 2026 before it was written
    down; an untested recipe is a claim.
  </p>
  <p class="meta-line">No account and no key · fair use, please ·
    <a href="/notes/mcp-server-what-it-solves/">what the endpoint is and what it refuses</a></p>
</header>

<div class="box">
  <h3>What you get back</h3>
  <p>
    For a page that is a work: authors, title, journal, year, volume, pages,
    DOI, ISSN and licence — plus a ready-to-import <strong>RIS record</strong>
    and a <strong>BibTeX entry</strong>. For a page that is a paywall, an error
    or a bot check: <code>complete: false</code> and a warning naming the wall.
    <strong>Test <code>complete</code> before you file the result</strong> — a
    refused record still carries a title, and it will read like a work.
  </p>
</div>

<h2 id="reading-list">A reading list becomes a .ris file</h2>
<p>
  The recipe most people actually want. One URL per line in
  <code>reading-list.txt</code>, one importable file out. Sources that cannot be
  read are named on stderr and left out of the file rather than half-imported.
</p>
<pre><code>while read -r u; do
  curl -sX POST https://provinglab.dev/mcp \\
    -H 'content-type: application/json' \\
    -d "{\\"jsonrpc\\":\\"2.0\\",\\"id\\":1,\\"method\\":\\"tools/call\\",
         \\"params\\":{\\"name\\":\\"extract_citation\\",\\"arguments\\":{\\"url\\":\\"$u\\"}}}" \\
  | python3 -c 'import json,sys
d = json.loads(json.load(sys.stdin)["result"]["content"][0]["text"])
sys.stdout.write(d["ris"]) if d.get("complete") else \\
  sys.stderr.write("skipped: " + d.get("warning","") + "\\n")'
done &lt; reading-list.txt &gt; literature.ris</code></pre>
<p>
  Then <strong>Zotero → File → Import</strong>, or <strong>Citavi →
  Import → RIS</strong>. Measured on three scholarly URLs: three records,
  under two seconds, imported without editing.
</p>

<h2 id="claude-code">Claude Code, in one line</h2>
<pre><code>claude mcp add --transport http provinglab https://provinglab.dev/mcp</code></pre>
<p>
  <code>claude mcp list</code> then reports <code>✔ Connected</code>. After that
  you can simply say: <em>"cite these four links for my bibliography"</em> — the
  tool is called for each one, and the ones behind a wall are reported as such
  instead of invented.
</p>

<h2 id="claude-desktop">Claude Desktop and other MCP clients</h2>
<p>
  Add <code>https://provinglab.dev/mcp</code> as a <strong>remote MCP
  server</strong> (transport: streamable HTTP). Authentication is offered but not
  required; anonymous requests get identical answers. In clients that only accept
  local servers, the usual bridge works:
</p>
<pre><code>{
  "mcpServers": {
    "provinglab": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://provinglab.dev/mcp"]
    }
  }
}</code></pre>

<h2 id="python">Python — mind the user agent</h2>
<p>
  The standard library identifies itself as <code>Python-urllib</code>, and the
  CDN in front of this site answers that with <strong>HTTP 403</strong> before the
  worker ever sees the request. Any user agent of your own is enough. This is not
  a rule against automation — it is a filter that does not know the difference.
</p>
<pre><code>import json, urllib.request

def cite(url):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "extract_citation", "arguments": {"url": url}}}).encode()
    req = urllib.request.Request("https://provinglab.dev/mcp", body, {
        "content-type": "application/json",
        "user-agent": "my-bibliography-script/1.0",   # <- without this: 403
    })
    answer = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return json.loads(answer["result"]["content"][0]["text"])

record = cite("https://doi.org/10.1038/s41586-020-2649-2")
if record.get("complete"):
    print(record["ris"])
else:
    print("not usable:", record["warning"])</code></pre>

<h2 id="wsl">WSL: from the browser into the terminal</h2>
<p>
  The two halves of the work sit on different sides of the filesystem boundary.
  A source behind a university login can only be captured in the browser, and
  the file then has to be found from a shell.
</p>
<p>
  In <a href="/tools/full-page-pdf-snap/">Full Page PDF Snap</a>, switch on
  <em>Copy file path after saving</em> and set the format to <strong>WSL</strong>
  under Settings. After a capture the path is on the clipboard in the shape a
  Linux shell understands:
</p>
<pre><code>/mnt/c/Users/&lt;you&gt;/Downloads/Full Page PDF Snap/pubmed_2026-08-03_0911_0001.pdf</code></pre>
<p>
  Paste it straight after a command, or into a chat with an AI tool that can read
  files. The RIS record for the same capture sits next to the PDF with the same
  name and a <code>.ris</code> extension.
</p>

<h2 id="which-route">Which of the two routes for which source</h2>
<div class="tblwrap"><table>
  <thead><tr><th scope="col"></th><th scope="col">The endpoint</th><th scope="col">The extension</th></tr></thead>
  <tbody>
    <tr><td>Runs</td><td>on a server, anonymous</td><td>in your browser, logged in</td></tr>
    <tr><td>Gives you</td><td>the reference</td><td>the reference <em>and</em> the document</td></tr>
    <tr><td>Behind a login</td><td class="lose">no</td><td class="win">yes</td></tr>
    <tr><td>Cost per source</td><td class="win">none, scriptable</td><td>one click</td></tr>
    <tr><td>Output</td><td>RIS + BibTeX</td><td>PDF with the fields inside, plus RIS</td></tr>
  </tbody>
</table></div>
<p>
  So the division is not a compromise: <strong>the endpoint for volume, the
  extension for the ones it refuses</strong>. Both emit the same RIS format, so
  everything lands in one Zotero or Citavi library regardless of the route. The
  refusal list from the first pass tells you which sources need the second.
</p>

<h2 id="machine">For an agent rather than a person</h2>
<p>
  These recipes are also published as a machine-readable skill, alongside the
  measurement methods:
</p>
<ul>
  <li><a href="/.well-known/agent-skills/index.json">agent-skills/index.json</a>
      — the skills with their checksums</li>
  <li><a href="/.well-known/agent-skills/cite-a-web-source.md">cite-a-web-source.md</a>
      — this page as a procedure</li>
  <li><a href="/llms.txt">llms.txt</a> — everything published here, as plain text</li>
  <li><a href="/.well-known/mcp/server-card.json">server card</a> — the tools and the transport</li>
</ul>

<div class="box">
  <h3>What none of this proves</h3>
  <p>
    A citation record says what a page declares about itself. It is not a check
    that the work exists, that the DOI resolves to it, or that the page is
    honest — for the eight of eighteen platforms where the data is thin, that
    matters. A screen capture, likewise, is a picture of a screen and
    <a href="/disclaimer/">not a qualified electronic document</a>. Where the
    content decides something, read the source.
  </p>
</div>

<footer><a href="../">← Proving Lab</a> · <a href="/tools/">Tools</a> ·
  <a href="/notes/mcp-server-what-it-solves/">About the endpoint</a> ·
  <a href="/disclaimer/">Disclaimer</a></footer>
"""

LD = """{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "Turn a web source into a citation with RIS and BibTeX",
  "description": "%s",
  "url": "https://provinglab.dev/recipes/",
  "datePublished": "2026-08-03",
  "inLanguage": "en",
  "totalTime": "PT2M",
  "supply": [{"@type": "HowToSupply", "name": "A list of source URLs"}],
  "tool": [
    {"@type": "HowToTool", "name": "curl or Python"},
    {"@type": "HowToTool", "name": "An MCP client such as Claude Code or Claude Desktop"},
    {"@type": "HowToTool", "name": "Zotero, Citavi, EndNote or Mendeley for the import"}
  ],
  "step": [
    {"@type": "HowToStep", "name": "Collect the URLs",
     "text": "Put one source URL per line into a text file.",
     "url": "https://provinglab.dev/recipes/#reading-list"},
    {"@type": "HowToStep", "name": "Call the endpoint for each",
     "text": "POST a JSON-RPC tools/call for extract_citation to https://provinglab.dev/mcp. No account or key is needed.",
     "url": "https://provinglab.dev/recipes/#reading-list"},
    {"@type": "HowToStep", "name": "Keep the complete records",
     "text": "Write the ris field of every record whose complete flag is true into one file; report the others, which name the paywall or bot check that stopped them.",
     "url": "https://provinglab.dev/recipes/#reading-list"},
    {"@type": "HowToStep", "name": "Import",
     "text": "Import the resulting .ris file into Zotero, Citavi, EndNote or Mendeley.",
     "url": "https://provinglab.dev/recipes/#reading-list"},
    {"@type": "HowToStep", "name": "Capture what the endpoint refused",
     "text": "Sources behind a login are captured in the browser with Full Page PDF Snap, which writes the same fields into the PDF and saves the same RIS format beside it.",
     "url": "https://provinglab.dev/recipes/#which-route"}
  ]
}""" % BESCHREIBUNG


def main():
    vor = VORLAGE.read_text(encoding="utf-8")
    stil = re.search(r"<style>.*?</style>", vor, re.S).group(0)
    nav = re.search(r'<nav class="topnav">.*?</nav>', vor, re.S).group(0)
    # Die Vorlage liegt zwei Ebenen tief, /recipes/ nur eine.
    nav = nav.replace("../../", "../").replace('aria-current="page"', "")

    seite = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{TITEL} — Proving Lab</title>
<meta name="description" content="{BESCHREIBUNG}">
<link rel="canonical" href="https://provinglab.dev/recipes/">
<link rel="alternate" type="application/atom+xml" title="Proving Lab" href="/feed.xml">
<link rel="describedby" href="/.well-known/agent-skills/index.json" type="application/json">
<link rel="api-catalog" href="/.well-known/api-catalog" type="application/linkset+json">
<link rel="service-doc" href="/llms.txt" type="text/plain">
<link rel="alternate" hreflang="en" href="https://provinglab.dev/recipes/">
<link rel="icon" href="../icon-128.png">
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large">
<meta property="og:type" content="article">
<meta property="og:title" content="{TITEL}">
<meta property="og:description" content="{BESCHREIBUNG}">
<meta property="og:url" content="https://provinglab.dev/recipes/">
<meta property="og:image" content="https://provinglab.dev/screenshots/05_cite_en.png">
<meta property="article:published_time" content="2026-08-03">
<meta name="twitter:card" content="summary_large_image">

<script type="application/ld+json">
{LD}
</script>

{stil}
<script src="/agent-tools.js" defer></script>
</head>
<body>
{nav}

<div class="wrap">
{RUMPF}
</div>
</body>
</html>
"""
    ziel = DOCS / "recipes"
    ziel.mkdir(exist_ok=True)
    (ziel / "index.html").write_text(seite, encoding="utf-8")
    print(f"docs/recipes/index.html  {len(seite)} Zeichen")


if __name__ == "__main__":
    main()
