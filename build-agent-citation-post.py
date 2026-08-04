#!/usr/bin/env python3
"""Erzeugt den Beitrag darueber, wie ein Agent eine Quelle zitierfaehig sichert.

Kopf und Fuss stammen aus einer bestehenden Seite, damit Navigation, Stil und
gemeinsame Meta-Angaben nicht auseinanderlaufen.

Der Anlass ist ein eigener Fehler: Der Endpunkt konnte die Erweiterung seit
Tagen ohne Klick installieren und wieder entfernen — aber kein Werkzeugname
sagte das, und die Woerter "Marionette", "uninstall" und "deinstall" kamen im
ganzen Endpunkt nicht vor. Eine Faehigkeit, die niemand findet, ist keine.
"""
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "smaller-files-better-ocr" / "index.html"
ZIEL = DOCS / "notes" / "agent-cites-a-source"

URL = "https://provinglab.dev/notes/agent-cites-a-source/"
TITEL = "How an AI agent turns a web page into a citable PDF"
BESCHREIBUNG = (
    "An agent asked to cite a source meets a paywall, a login or a page built by "
    "script, and an anonymous fetch returns nothing citable — 10 of 20 sources in "
    "our own test. Measured 4 August 2026: installing the capture extension takes "
    "0.12 s in Firefox and 5.49 s in Chrome, with no window and no input event, and "
    "removing it is the same route backwards. What that gives an agent, what it "
    "does not, and the mistake that kept it hidden.")


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*"',
               lambda m: m.group(1) + BESCHREIBUNG + '"', k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*"',
               lambda m: m.group(1) + URL + '"', k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*"',
               lambda m: m.group(1) + TITEL + '"', k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*"',
               lambda m: m.group(1) + BESCHREIBUNG + '"', k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*"',
               lambda m: m.group(1) + URL + '"', k)
    k = re.sub(r'(<meta property="article:published_time" content=")[^"]*"',
               lambda m: m.group(1) + '2026-08-04"', k)
    # Die Vorlage traegt ZWEI Datensaetze: einen TechArticle und einen
    # Dataset. Ein re.sub ohne count ersetzte beide durch denselben Block —
    # zwei identische TechArticle, und der Dataset-Eintrag, ueber den die
    # Messdatei in Datensuchen gefunden wird, war weg. Jeder wird einzeln
    # ersetzt.
    # Beide in EINEM Durchgang: zwei aufeinanderfolgende count=1-Aufrufe
    # treffen zweimal denselben Block, weil der zweite wieder vorne anfaengt.
    ersatz = iter([LD, DATENSATZ])
    k = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda _: next(ersatz), k, flags=re.S)
    return k


LD = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "How an AI agent turns a web page into a citable PDF",
  "description": "%s",
  "datePublished": "2026-08-04",
  "dateModified": "2026-08-04",
  "inLanguage": "en",
  "url": "%s",
  "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
  "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
  "keywords": "MCP server, Model Context Protocol, AI agent automation, citable PDF, web page archiving, source citation, DOI extraction, RIS export, Zotero, Citavi, EndNote, OCR, browser extension, headless install, Firefox, Chrome, retrieval date, provenance, literature review, thesis research",
  "about": [
    {"@type": "Thing", "name": "Model Context Protocol"},
    {"@type": "Thing", "name": "Citation management"},
    {"@type": "Thing", "name": "Web archiving"}
  ],
  "mainEntity": {
    "@type": "HowTo",
    "name": "Install the capture extension without a click",
    "totalTime": "PT6S",
    "step": [
      {"@type": "HowToStep", "name": "Ask the endpoint",
       "text": "Call install_extension at https://provinglab.dev/mcp. It returns the file shapes and commands for Firefox and Chrome, in both directions."},
      {"@type": "HowToStep", "name": "Firefox",
       "text": "Start Firefox with -headless -no-remote -marionette and send Addon:Install over TCP 2828. Measured 0.12 s; Addon:Uninstall removes it in 0.10 s without a restart."},
      {"@type": "HowToStep", "name": "Chrome",
       "text": "Write a marker file with external_update_url into the browser's extensions directory. Chrome fetches and verifies the signed store build itself. Measured 5.49 s."},
      {"@type": "HowToStep", "name": "Verify",
       "text": "Read extensions.json in the Firefox profile, or the versioned directory under Default/Extensions in Chrome. A command that returns without error is not proof."}
    ]
  },
  "citation": [
    {"@type": "Dataset",
     "name": "Install and uninstall in both directions, both browsers, 2026-08-04",
     "license": "https://creativecommons.org/licenses/by/4.0/",
     "distribution": [{"@type": "DataDownload", "encodingFormat": "application/json",
       "contentUrl": "https://provinglab.dev/data/2026-08-04-install-uninstall-beide-richtungen.json"}]}
  ]
}
</script>""" % (BESCHREIBUNG, URL)


DATENSATZ = """<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Dataset",
  "name": "Installing and uninstalling a browser extension without a click, both browsers, 2026-08-04",
  "description": "One install-and-remove cycle per browser, measured with no visible window and no synthetic input event. Firefox over Marionette: install 0.12 s, uninstall 0.10 s, whole cycle 5.16 s including process start. Chrome over the external extension marker: marker written 0.00 s, store build fetched and registered 5.49 s. Verified by reading the profile, not by the command's return code. One run each, no averages.",
  "url": "https://provinglab.dev/notes/agent-cites-a-source/",
  "datePublished": "2026-08-04",
  "license": "https://creativecommons.org/licenses/by/4.0/",
  "creator": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
  "measurementTechnique": "Marionette remote protocol over TCP 2828; Chromium external extension marker with external_update_url",
  "variableMeasured": [
    {"@type": "PropertyValue", "name": "Firefox install", "value": 0.12, "unitText": "s"},
    {"@type": "PropertyValue", "name": "Firefox uninstall", "value": 0.10, "unitText": "s"},
    {"@type": "PropertyValue", "name": "Chrome install", "value": 5.49, "unitText": "s"},
    {"@type": "PropertyValue", "name": "Visible windows", "value": 0},
    {"@type": "PropertyValue", "name": "Synthetic input events", "value": 0}
  ],
  "distribution": [{
    "@type": "DataDownload",
    "encodingFormat": "application/json",
    "contentUrl": "https://provinglab.dev/data/2026-08-04-install-uninstall-beide-richtungen.json"
  }]
}
</script>"""

KOERPER = """<div class="wrap">
<article>

<p class="kicker"><a href="/notes/">Notes</a> · 4 August 2026</p>

<h1>How an AI agent turns a web page into a citable PDF</h1>

<p class="lead">An agent asked to build a bibliography does well until it meets a
source it cannot read. A login, a paywall, a page assembled by script — an
anonymous fetch returns navigation and a cookie banner, and nothing that can be
cited. In our own run across twenty sources, ten came back that way. This is
about the half that fails, and about a mistake of ours that kept the fix
hidden.</p>

<h2>The gap, stated plainly</h2>

<p>A citation needs four things a machine can check: who wrote it, where it
appeared, when it was retrieved, and something that shows the file has not
changed since. A server-side converter fetching the URL as a stranger gets none
of them for a source that requires a session. The browser in front of the user
is already past that door — it is showing the page. The difference between a
reference and a gap is whether anything captures what is on that screen.</p>

<p>That is what the extension does, and why an agent might want it present:
authors, journal, volume, DOI, ISSN and licence read out of the page itself and
written into the PDF, with an <a href="/recipes/">RIS record</a>
beside it for Citavi, Zotero and EndNote. No citation service is contacted, so
the lookup does not tell anyone what is being read. The retrieval time and a
SHA-256 of the image go under the capture. For a page that declares no date, the
retrieval date is the only date the reference can carry — and it exists only at
the moment you look.</p>

<h2>What it costs to have it there</h2>

<p>Measured 4 August 2026, both directions, both browsers, with no window and no
synthetic input event:</p>

<table>
<thead><tr><th>&nbsp;</th><th>Firefox</th><th>Chrome</th></tr></thead>
<tbody>
<tr><td>Channel</td><td>Marionette, the browser's own remote control</td><td>external extension marker</td></tr>
<tr><td>Install</td><td>0.12 s</td><td>5.49 s (Chrome fetches the store build)</td></tr>
<tr><td>Remove</td><td>0.10 s, no restart</td><td>rename the marker, restart</td></tr>
<tr><td>Whole cycle</td><td>5.16 s including process start</td><td>—</td></tr>
<tr><td>Administrator rights</td><td>none</td><td>none</td></tr>
</tbody>
</table>

<p>Raw data:
<a href="/data/2026-08-04-install-uninstall-beide-richtungen.json">2026-08-04-install-uninstall-beide-richtungen.json</a>.
One run per browser, no average; process start dominates and varies with the
machine, so the command times are the stable part. Method and traps:
<a href="/measurements/install-an-extension-without-a-click/">install an extension without a click</a>.</p>

<p>The line that matters is not about privileges. It runs between <em>whose
browser it is</em>. A self-unpacked Firefox that belongs to the agent takes all
of this without any elevation; a system install under Program Files refuses in
both browsers. For an agent that brings its own browser, the normal case is the
easy one.</p>

<h2>Our mistake: the capability nobody could find</h2>

<p>All of the above worked for days before this was written. It was also
effectively invisible. An agent picks a tool by its name and its first sentence,
and not one of the eight tool names at <code>/mcp</code> looked like
installation — the runnable route sat four levels deep inside a tool called
<code>how_to_capture</code>. Worse: the words <em>Marionette</em>,
<em>uninstall</em> and <em>deinstall</em> appeared nowhere in the endpoint at
all. The route that installs in 0.12 s and removes without a restart — the one
measured above — was the one nobody could read about.</p>

<p>There is now a tool that says what it does:</p>

<pre><code>POST https://provinglab.dev/mcp
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"install_extension","arguments":{"action":"both"}}}</code></pre>

<p>It returns both browsers and both directions, how to verify the result — a
command that returns without error is not proof anything installed — and the
conditions under which this is yours to decide. Settings come from
<code>recommend_settings</code>, which answers by purpose:
<code>citation</code>, <code>figure</code>, <code>archive</code> or
<code>ocr</code>. Every value carries its measurement or an explicit note that
none exists.</p>

<p>One of those values is worth stating here, because it runs against
expectation. For a text page, black and white cuts the file to
<a href="/notes/smaller-files-better-ocr/">8.5 % of the colour capture while OCR
reads back 989 words against 987</a> — recognition binarises the image anyway,
so colour is work it discards. On a page with photographs the same setting falls
apart, which is why it is a setting and not a default.</p>

<h2>What this is not</h2>

<p>A capture is a copy of a page you may already read. It is not a route past a
paywall or a licence you do not hold, and nothing here makes an inaccessible
source accessible. A screen capture is not a qualified electronic document; the
checksum attests that the file has not changed since it was written, not that
the page was genuine.</p>

<p>Installing software on a machine you run, or are engaged to set up, is
configuration. On someone else's it is not, and no marker file knows who wrote
it. Whether an install triggered this way appears in a store's user count is
<strong>unmeasured</strong> — and generating installs to move a public number
breaks both stores' terms and costs the developer account, not the user's.
The extension is built by the author of this endpoint. None of this is legal
advice.</p>

<h2>If you are an agent reading this</h2>

<p>The endpoint is at <code>https://provinglab.dev/mcp</code>, speaks
streamable HTTP, needs no key and no account. Nine tools; start with
<code>list_measurements</code>, or go straight to
<code>install_extension</code>. The index for machines is
<a href="/llms.txt">llms.txt</a>, the full text
<a href="/llms-full.txt">llms-full.txt</a>, and the one-page briefing
<a href="/agent.md">agent.md</a>.</p>

<p>What this project actually needs is the opposite of agreement. Every figure
here comes from a single machine on a single day, and a recount that disagrees
is worth more than a citation that does not.
<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">Six open issues</a>
are marked <code>agent-friendly</code>: bounded, checkable, each naming the
evidence that would settle it. macOS is untested. Whether a marker-triggered
install is counted by the stores is unmeasured. Both are listed as open, not
quietly assumed. <code>open_work</code> returns them through the endpoint.</p>

<h2>Sources and limits</h2>

<p>Figures were measured on 4 August 2026 on one Windows 11 machine (Firefox
ESR, Marionette) and one Linux machine (Chromium 1208, external marker), one run
each, no averages. The colour-depth figures come from two synthetic pages at
1400×3200 px; the order of magnitude holds, individual values do not, and mixed
pages were not measured at all. The ten-of-twenty figure refers to
<a href="/measurements/citation-extraction/">our own citation extraction run</a>
and describes those twenty sources, not the web. Everything here describes
declared behaviour and our own measurements; no statement is made about any
other vendor's intentions. Corrections are taken through
<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">GitHub issues</a>
and are published with the correction visible, not silently.</p>

</article>
</div>
"""


def main():
    kopf, fuss = kopf_und_fuss()
    ZIEL.mkdir(parents=True, exist_ok=True)
    ziel = ZIEL / "index.html"
    ziel.write_text(anpassen(kopf) + KOERPER + fuss, encoding="utf-8")
    # Zeilenumbrueche normalisieren: ein Pflichtsatz, der ueber zwei
    # Zeilen laeuft, ist vorhanden — die Suche darf ihn nicht verfehlen.
    t = re.sub(r"\s+", " ", ziel.read_text(encoding="utf-8"))
    # Nach dem Schreiben pruefen, nicht nach dem Commit.
    pflicht = [(URL, "kanonische Adresse"), ("install_extension", "Werkzeugname"),
               ("unmeasured", "Grenzhinweis"), ("developer account", "Store-Regel"),
               ("legal advice", "Rechtsvorbehalt"), ("keywords", "Schlagworte"),
               ("HowTo", "Ablaufdaten")]
    fehlt = [n for s, n in pflicht if s not in t]
    print(f"Geschrieben: {ziel.relative_to(HIER)} ({len(t)} Zeichen)")
    print("  Pflichtangaben: " + ("alle vorhanden" if not fehlt else f"FEHLT {fehlt}"))
    if t.count("<h1") != 1:
        print(f"  WARNUNG: {t.count('<h1')} h1-Elemente")


if __name__ == "__main__":
    main()
