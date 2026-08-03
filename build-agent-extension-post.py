#!/usr/bin/env python3
"""Erzeugt /notes/what-an-agent-can-do-with-an-extension/.

Die Frage, die beim Verdrahten des Endpunkts mit der Erweiterung aufkam und
deren Antwort unbequem genug ist, um sie aufzuschreiben: Ein Agent kann eine
Browser-Erweiterung nicht installieren. Er kann sie benennen, begruenden und
verlinken — und in einem Browser, den er selbst startet, eine entpackte
Fassung laden. Beides ist nicht dasselbe, und die Verwechslung fuehrt zu
Anleitungen, die im Leeren enden.

Kopf und Fuss stammen aus einer bestehenden Notiz.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "mcp-server-what-it-solves" / "index.html"
ZIEL = DOCS / "notes" / "what-an-agent-can-do-with-an-extension"

URL = "https://provinglab.dev/notes/what-an-agent-can-do-with-an-extension/"
DATUM, DATUM_LANG = "2026-08-03", "3 August 2026"
AMO = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
CWS = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"

TITEL = "What an AI agent can and cannot do with a browser extension"
BESCHREIBUNG = (
    "An agent cannot install a browser extension into your browser — no store has an API "
    "for it, and inline install was removed years ago. What it can do: name the step, link "
    "the install, and load an unpacked build into a browser it drives itself. Measured, "
    "including the flag that fails silently.")
OG = ("Agents are increasingly told to 'use an extension'. They cannot install one into "
      "someone else's browser: store installation is a user gesture by design. What works "
      "instead, what fails silently, and how the work actually divides.")


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    auf = '<div class="wrap">'
    return s[:s.index(auf) + len(auf)], s[s.index("<footer"):]


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
               lambda m: m.group(1) + OG + m.group(2), k)
    ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": TITEL, "description": BESCHREIBUNG,
        "datePublished": DATUM, "dateModified": DATUM, "inLanguage": "en", "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)


INHALT = f"""
<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    Our citation endpoint now tells agents, in the cases it cannot finish, to
    have the user capture the page in a browser — and links the extension that
    does it. That raised a fair question: could the agent not just install it
    itself? No. And the reason is worth writing down, because the assumption
    produces instructions that end in mid-air.
  </p>
  <p class="meta">{DATUM_LANG} · checked against Chrome 150 and Firefox 141</p>
</header>

<h2>The short answer</h2>
<p>
  Installing an extension into a person's browser is a <em>user gesture</em> by
  design. Neither store exposes an API for it, and the mechanisms that once came
  close were removed on purpose:
</p>
<table>
  <thead><tr><th>Route</th><th>Status</th></tr></thead>
  <tbody>
    <tr><td>Chrome inline install (<code>chrome.webstore.install</code>)</td>
        <td>removed in 2018; pages can no longer trigger an install</td></tr>
    <tr><td>Firefox <code>InstallTrigger</code></td>
        <td>removed with Manifest V3 support; no page-initiated install</td></tr>
    <tr><td>Store API for installing on a user's behalf</td>
        <td>does not exist, in either store</td></tr>
    <tr><td>Enterprise policy (<code>ExtensionInstallForcelist</code>)</td>
        <td>exists, but it is an administrator deploying to managed machines —
            not an assistant acting in a conversation</td></tr>
  </tbody>
</table>
<p>
  This is not an oversight to be worked around. An extension can read and
  rewrite pages; the deliberate friction of a person clicking <em>Add</em> after
  seeing the requested permissions is the security model. An agent that could
  install extensions silently would be the exact hole the model exists to close.
</p>

<h2>What an agent can do — and it is not nothing</h2>
<p>
  Three things, in descending order of how often they apply.
</p>

<h3>1. Name the step, the reason and the address</h3>
<p>
  The common case. The agent hits a source it cannot read, and instead of an
  apology it hands over something actionable: which addresses need a person, why
  each one does, and where to get the tool. That is what
  <code>extract_citation</code> on <a href="/notes/mcp-server-what-it-solves/">this
  site's endpoint</a> now returns in its <code>nextStep</code> field — the
  instruction, the evidence behind it, both install links, and the disclosure
  that the tool comes from the same author.
</p>
<pre><code>"nextStep": {{
  "do": "Open the address in the browser you are already signed in with…",
  "why": "The page answers a browser and refuses this reader — a bot defence.",
  "tool": {{
    "name": "Full Page PDF Snap",
    "firefox": "{AMO}",
    "chrome": "{CWS}",
    "runsOn": "Firefox on desktop and Android; Chrome 116 or newer, Edge, Brave and Vivaldi.",
    "disclosure": "Built by the author of this endpoint…"
  }},
  "evidence": "https://provinglab.dev/measurements/reading-list-to-bibliography/"
}}</code></pre>
<p>
  Note what it does <em>not</em> say. It is attached only where the endpoint
  actually stopped, and it distinguishes the three reasons a source comes back —
  because <a href="/measurements/reading-list-to-bibliography/">measured across
  twenty sources</a>, a browser only helps with one of them. Four of the ten
  refusals were aimed at the network rather than the client, and no extension
  changes those; five were pages that declare no citation data at all, where the
  reference has to be written by a person regardless of tooling. A hint pasted
  onto all three would be advertising, and an agent that notices it is
  advertising is right to ignore it.
</p>

<h3>2. Load an unpacked build into a browser it drives itself</h3>
<p>
  Different situation, often confused with the first: the agent is running its
  own automated browser. There it <em>can</em> load an extension — into its own
  session, from a local folder, never from a store and never into anyone else's
  profile.
</p>
<p>
  With a caveat we hit in testing and that costs an afternoon if you do not know
  it: <strong>the command-line switch fails silently.</strong> On Chrome 150,
  <code>--load-extension</code> loads nothing and reports nothing, and the flag
  that used to re-enable it is gone too. The run then looks like a broken
  manifest — no service worker, no errors — and the search for the fault starts
  in the wrong place. What works is the debugging protocol:
</p>
<pre><code>chrome --remote-debugging-port=9223 --user-data-dir=&lt;temp&gt; \\
       --enable-unsafe-extension-debugging --no-first-run about:blank</code></pre>
<pre><code>b = p.chromium.connect_over_cdp("http://127.0.0.1:9223")
s = b.new_browser_cdp_session()
s.send("Extensions.loadUnpacked", {{"path": "/path/to/extension"}})</code></pre>
<p>
  Verified on Chrome 150.0.7871.187. Useful for testing an extension, or for an
  agent that captures pages inside a browser it owns. Not a route into a user's
  browser, and not a way to install from a store.
</p>

<h3>3. Use the endpoint instead, where that is enough</h3>
<p>
  Half of the work needs no browser at all. Ten of twenty sources produced
  complete records with RIS and BibTeX over plain HTTP, no account, no key,
  0.4 s each. An agent should exhaust that route first and only escalate to a
  person for what is left — which is the whole point of naming the leftovers
  precisely. The <a href="/recipes/">recipes</a> are runnable for Claude Code,
  Claude Desktop, other MCP clients, Python and a plain shell loop.
</p>

<h2>So where does that leave the division of labour</h2>
<table>
  <thead><tr><th>Step</th><th>Who</th></tr></thead>
  <tbody>
    <tr><td>Read what a page declares about itself, in bulk</td><td>the agent, over HTTP</td></tr>
    <tr><td>Decide which sources need a person, and why</td><td>the agent</td></tr>
    <tr><td>Install a browser extension</td><td>the person, once</td></tr>
    <tr><td>Open a source behind a login or a bot wall</td><td>the person, in their session</td></tr>
    <tr><td>Keep the page and its retrieval date</td><td>the extension, on that click</td></tr>
    <tr><td>Merge the results into one reference list</td><td>the agent</td></tr>
  </tbody>
</table>
<p>
  The honest version of “AI does your bibliography” is this table, not a promise
  that the machine handles all of it. What changed here is only the fourth
  column of the third row: the person now gets told exactly what to install and
  why, at the moment it matters, instead of an agent shrugging.
</p>

<h2>What this does not claim</h2>
<ul>
  <li><strong>No measurement of uptake.</strong> Whether naming a tool at the
    point of failure actually leads anyone to install it is not something we can
    show yet. Both stores stood at four users on {DATUM_LANG}; that figure is
    published here so a later claim can be checked against it.</li>
  <li><strong>Platform behaviour changes.</strong> The removed install APIs are
    unlikely to return, but the CDP method is an unstable debugging interface
    and may well break.</li>
  <li><strong>The extension is ours.</strong> Disclosed everywhere it appears,
    including inside the endpoint's replies. The browser's own print-to-PDF is
    <a href="/measurements/print-to-pdf-vs-screenshot/">measured against it</a>,
    including the cases where print is the better choice.</li>
</ul>
"""


def main():
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        lambda _: (
            f'<footer>\n      Checked on {DATUM_LANG} against Chrome 150.0.7871.187 and '
            'Firefox 141. Store figures from the addons.mozilla.org API and the Chrome Web '
            'Store listing on the same day.\n      <br><br>\n      Corrections are welcome and '
            'are made in public: <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">'
            'open an issue</a>.\n      <br><br>\n      Disclosure: the author develops Full Page '
            'PDF Snap, the extension named above.\n      <br><br>\n'
            '      <a href="../../">← Proving Lab</a> · '
            '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>'),
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + INHALT + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
