#!/usr/bin/env python3
"""Erzeugt die beiden Einstiegsseiten, die der Seite bisher gefehlt haben.

    python3 build-einstiegsseiten.py

Befund vom 3. August 2026: Die Publikation ist indexiert, rankt aber fuer
nichts — nicht einmal fuer den eigenen Namen. Der Grund ist nicht technisch
(robots.txt, Content-Signals, Sitemap und IndexNow sind in Ordnung), sondern
strukturell: **alle Titel sind Befund-Titel.** „Twenty links, ten citations"
ist zitierfaehig, aber niemand tippt es ein.

Deshalb zwei Seiten, die die Frage tragen statt des Ergebnisses:

  /how-to/save-a-webpage-as-pdf/
      Was ein Mensch sucht. Antwort in den ersten zwei Saetzen, Messungen als
      Beleg dahinter — nicht umgekehrt.

  /for-agents/
      Was ein KI-System oder dessen Betreiber sucht. Buendelt Endpunkt,
      Faehigkeiten, Entscheidungsregel und lauffaehige Beispiele an einer
      Stelle, statt sie ueber fuenf Beitraege zu verteilen.

Beide verweisen auf dieselben Messungen. Der Beleg wandert nicht, nur der
Einstieg.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "notes" / "mcp-server-what-it-solves" / "index.html"
DATUM, DATUM_LANG = "2026-08-03", "3 August 2026"
AMO = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
CWS = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    auf = '<div class="wrap">'
    return s[:s.index(auf) + len(auf)], s[s.index("<footer"):]


def anpassen(kopf, url, titel, besch, og, tiefe, art, faq=None):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{titel} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + besch + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{titel}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + og + m.group(2), k)
    k = re.sub(r'(<link rel="icon" href=")[^"]*(")', rf"\g<1>{tiefe}icon-128.png\g<2>", k)
    # Die Vorlage liegt zwei Ebenen tief; ihre Navigation zeigt mit ../../ nach
    # oben. Eine Seite direkt unter der Wurzel braucht ../ — sonst zeigt jeder
    # Navigationspunkt ins Leere, und zwar auf jeder erzeugten Seite gleich.
    if tiefe != "../../":
        k = k.replace('href="../../', f'href="{tiefe}').replace('src="../../', f'src="{tiefe}')
    ld = {
        "@context": "https://schema.org", "@type": art,
        "headline": titel, "description": besch,
        "datePublished": DATUM, "dateModified": DATUM, "inLanguage": "en", "url": url,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    bloecke = ['<script type="application/ld+json">\n'
               + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"]
    if faq:
        # Frage-Antwort-Auszeichnung: Antwortsysteme lesen sie direkt aus, und
        # sie zwingt dazu, jede Frage in einem Absatz zu beantworten.
        fld = {"@context": "https://schema.org", "@type": "FAQPage",
               "mainEntity": [{"@type": "Question", "name": f,
                               "acceptedAnswer": {"@type": "Answer", "text": a}}
                              for f, a in faq]}
        bloecke.append('<script type="application/ld+json">\n'
                       + json.dumps(fld, indent=2, ensure_ascii=False) + "\n</script>")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda _: "\n".join(bloecke), k, count=1, flags=re.S)


def fuss_setzen(fuss, satz, tiefe):
    return re.sub(
        r"<footer>.*?</footer>",
        lambda _: (f'<footer>\n      {satz}\n      <br><br>\n'
                   '      Corrections are welcome and are made in public: '
                   '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">open an issue</a>.\n'
                   '      <br><br>\n      Disclosure: the author develops Full Page PDF Snap, '
                   'the extension named on this page. The browser\'s own print-to-PDF is '
                   '<a href="/measurements/print-to-pdf-vs-screenshot/">measured against it</a>, '
                   'including where print wins.\n      <br><br>\n'
                   f'      <a href="{tiefe}">← Proving Lab</a> · '
                   f'<a href="{tiefe}disclaimer/">Disclaimer</a>\n    </footer>'),
        fuss, count=1, flags=re.S)


# ------------------------------------------------------------------ Anleitung

FAQ = [
    ("How do I save a whole web page as one PDF without page breaks?",
     "Use a capture extension rather than the print dialog. The browser's print export "
     "paginates: the same article came out as 26 pages, and 9 page breaks cut through a "
     "sentence. A full-page capture writes one continuous sheet. Both routes are measured "
     "at https://provinglab.dev/measurements/print-to-pdf-vs-screenshot/ — including the "
     "cases where print is the better choice, because it keeps selectable text."),
    ("Can I save a page that is behind a login or a paywall I have access to?",
     "Yes, if you open it in your own browser. An extension captures what your session "
     "already shows, so a licensed article or a course page is saved as you see it. No "
     "server-side service can do this, because it does not have your session. It is not a "
     "way to reach content you do not have access to."),
    ("How do I save a web page as PDF on a phone?",
     "On Android, only Firefox can do it: Chrome for Android installs no extensions at all. "
     "Of 248 page-saving extensions checked against the add-ons API, 60 declare Android "
     "support. Measured at "
     "https://provinglab.dev/measurements/android-capture-extensions/"),
    ("Why does a saved page need the retrieval date?",
     "Because a web source can change or vanish, and for a page that declares no publication "
     "date the retrieval date is the only date a reference can carry. Of 150 sources taken "
     "from real bibliographies, 19.3 % were gone and 8.7 % had no archived copy anywhere; "
     "where a snapshot existed it was a median of 603 days old."),
    ("Can I turn a list of links into a bibliography automatically?",
     "Partly, and it is worth knowing which part. Of 20 mixed sources, 10 became complete "
     "records with RIS and BibTeX over plain HTTP in 8.1 seconds. The other 10 need a "
     "person — one because of a bot defence, four because the publisher refuses that "
     "network, and five because the page declares no citation data at all."),
]

ANLEITUNG = f"""
<header>
  <h1>How to save a web page as a PDF — one sheet, with its source on it</h1>
  <p class="standfirst">
    The short answer: use a capture extension, not the print dialog. Print
    paginates — the same article came out as <strong>26 pages with 9 breaks
    cutting through a sentence</strong>. A capture writes one continuous sheet
    and can stamp the page with where it came from and when.
  </p>
  <p class="meta">{DATUM_LANG} · every figure on this page links to the
    measurement it comes from</p>
</header>

<p>
  <a class="btn" href="{AMO}">Firefox, desktop and Android</a>
  &nbsp;<a class="btn" href="{CWS}">Chrome 116+, Edge, Brave, Vivaldi</a>
</p>
<p style="font-size:.9rem">
  Free, MIT licensed, runs on the device. Edge asks once to allow extensions
  from other stores; Opera needs its <em>Install Chrome Extensions</em> add-on
  first. Then: open the page, press <code>Alt+Shift+Y</code> or click the icon.
</p>

<h2>Print to PDF or capture? The honest comparison</h2>
<table>
  <thead><tr><th></th><th>Browser print</th><th>Full-page capture</th></tr></thead>
  <tbody>
    <tr><td>Same article comes out as</td><td>26 pages</td><td><strong>1 sheet</strong></td></tr>
    <tr><td>Page breaks cutting a sentence</td><td>9</td><td>0</td></tr>
    <tr><td>Text you can select and search</td><td><strong>94.8 % recall</strong></td><td>from OCR: 92.6 %</td></tr>
    <tr><td>Costs anything</td><td>no, built in</td><td>no</td></tr>
  </tbody>
</table>
<p>
  <strong>Print wins on text.</strong> If all you need is a readable, searchable
  copy and the pagination does not bother you, the function already in your
  browser is enough — and this page says so rather than pretending otherwise.
  A capture is worth it when the layout matters, when a break would fall through
  a table, or when the source details have to travel with the file.
  <a href="/measurements/print-to-pdf-vs-screenshot/">Method and raw data</a>
</p>

<h2>Behind a login or a paywall you have access to</h2>
<p>
  A capture extension reads what your own session already shows. A licensed
  journal article, a course page, an order confirmation — saved as you see it.
  No server-side converter can do this, because it does not have your session:
  measured across 20 mixed sources, a server-side reader was refused by 5 of
  them outright. Capturing a page you may read is a copy for your own use; it is
  not a route to content you do not have access to.
</p>

<h2>On a phone</h2>
<p>
  Only Firefox. <strong>Chrome for Android installs no extensions at all</strong>,
  so the question only arises there. Of 248 page-saving extensions checked
  against the add-ons API, 60 declare Android support and none had been tested on
  a device before we did.
  <a href="/measurements/android-capture-extensions/">The Android measurement</a>
</p>

<h2>Why the file should carry its source</h2>
<p>
  A URL in a bibliography is a promise about a page you do not control. Checked
  against 150 sources taken from real reference lists: <strong>19.3 % were
  gone</strong>, 8.7 % had no archived copy anywhere, and where a snapshot
  existed it was a median of 603 days old. For a page that declares no
  publication date, the time of retrieval is the only date a reference can carry
  — and it exists only at the moment you look.
  <a href="/measurements/web-citations-that-vanish/">What happens to a source
  after you cite it</a>
</p>
<p>
  A capture can write that in: authors, title, DOI, licence and the exact time,
  inside the PDF and in an RIS record beside it — a format that imports into
  Zotero, Citavi, EndNote or Mendeley.
</p>

<h2>A whole reading list at once</h2>
<p>
  For a bibliography rather than a single page, most of the work needs no
  browser. Of 20 mixed sources, <strong>10 became complete records with RIS and
  BibTeX in 8.1 seconds</strong> over plain HTTP — no account, no key. The other
  ten are handed back with the reason, so you know which addresses need you.
  <a href="/recipes/">The recipes</a> ·
  <a href="/measurements/reading-list-to-bibliography/">the measurement</a>
</p>

<h2>What this does not do</h2>
<ul>
  <li>It does not reach content you have no access to.</li>
  <li>A screen capture is not a qualified electronic document. It records what a
    page looked like at a time, which is a different thing from proving it.</li>
  <li>Where a publisher offers its own <em>Cite → RIS</em> export, that file is
    authoritative and better than anything reconstructed from the page.</li>
</ul>
"""

# ------------------------------------------------------------------ Agenten

AGENTEN = f"""
<header>
  <h1>For AI agents: citations without a browser, and the step that needs one</h1>
  <p class="standfirst">
    An endpoint that turns a URL into a citation record, a skill index that
    describes when to use it, and one measured rule for the cases it cannot
    finish. No account, no key. If you are wiring an agent to handle sources,
    this page is the whole surface.
  </p>
  <p class="meta">{DATUM_LANG} · everything below was run before it was written
    down</p>
</header>

<h2>Connect in one line</h2>
<pre><code>claude mcp add --transport http provinglab https://provinglab.dev/mcp</code></pre>
<p>
  Claude Desktop and other MCP clients: add
  <code>https://provinglab.dev/mcp</code> as a remote server, transport
  <em>streamable HTTP</em>. Clients that only accept local servers can bridge
  with <code>npx -y mcp-remote https://provinglab.dev/mcp</code>. Authentication
  is offered but not required; anonymous requests get identical answers.
</p>
<p style="font-size:.9rem">
  One caveat that costs an afternoon: the CDN refuses the user agent Python's
  <code>urllib</code> sends by default. Set any user agent of your own and it
  answers normally.
</p>

<h2>Five tools</h2>
<table>
  <thead><tr><th>Tool</th><th>What it is for</th></tr></thead>
  <tbody>
    <tr><td><code>extract_citation</code></td>
        <td>URL in, structured record out — authors, title, journal, year, DOI, licence,
            plus RIS and BibTeX. Or a named refusal.</td></tr>
    <tr><td><code>how_to_capture</code></td>
        <td>What to do with a source this endpoint cannot read, resolved for your agent
            type and target browser.</td></tr>
    <tr><td><code>list_measurements</code></td>
        <td>Everything published here, with dataset URLs.</td></tr>
    <tr><td><code>get_measurement_data</code></td>
        <td>One dataset as JSON, including the control run.</td></tr>
    <tr><td><code>get_method</code></td>
        <td>A reproducible method, to repeat a measurement rather than cite it.</td></tr>
  </tbody>
</table>

<h2>The one rule worth hard-coding</h2>
<p>
  <strong>Read <code>complete</code>, never the title alone.</strong> A refused
  record still carries a title, and two of twenty measured sources returned a
  title <em>and</em> an author while <code>complete</code> was false — a Zenodo
  software release and a statistics portal page. Anything that files those as
  sources has invented the missing half.
</p>
<pre><code>if not record["complete"]:
    hand_back(url, record.get("warning"), record.get("nextStep"))</code></pre>
<p>
  Where the endpoint cannot finish, the reply carries <code>nextStep</code>: what
  has to happen, why, both install links for the capture extension, and the
  disclosure that the tool is ours.
</p>

<h2>What a reading list actually yields</h2>
<div class="kf-row">
  <div class="kf b"><div class="n">10/20</div><div class="l">complete records</div></div>
  <div class="kf"><div class="n">0.4 s</div><div class="l">per source</div></div>
  <div class="kf"><div class="n">1</div><div class="l">stopped by a bot defence</div></div>
  <div class="kf"><div class="n">5</div><div class="l">declare no citation data</div></div>
</div>
<p>
  The split does not run between paid and free. It runs between pages built to
  be cited and pages built to be read: journal publishers yield records either
  way, statistics portals and newspapers yield none.
  <a href="/measurements/reading-list-to-bibliography/">Method and raw data</a>
</p>

<h2>Can your agent drive the browser extension?</h2>
<p>
  Depends on one property, and it is measured. The extension declares
  <code>activeTab</code> and no host permissions, so it sees a tab only after an
  event reaches the browser's input layer. Tabs visible to it went from
  <strong>0 to 1</strong> after a synthetic <code>Alt+Shift+Y</code> sent through
  X11 XTEST. The browser does not ask who produced the gesture.
</p>
<table>
  <thead><tr><th>Your agent acts through</th><th>Can trigger it</th></tr></thead>
  <tbody>
    <tr><td>Real input events — computer use, <code>xdotool</code>, an agent inside the
        user's browser</td><td><strong>yes</strong></td></tr>
    <tr><td>CDP and DOM only — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP</td>
        <td><strong>no</strong></td></tr>
    <tr><td>No browser</td><td>not needed for half the work</td></tr>
  </tbody>
</table>
<p>
  <a href="/notes/what-an-agent-can-do-with-an-extension/">The measurement, both
  halves</a> · <a href="/.well-known/agent-skills/capture-a-source.md">the skill
  as Markdown</a>
</p>

<h2>Discovery, if you are indexing this site</h2>
<table>
  <thead><tr><th>What</th><th>Where</th></tr></thead>
  <tbody>
    <tr><td>Site summary for language models</td><td><a href="/llms.txt"><code>/llms.txt</code></a></td></tr>
    <tr><td>Skills with checksums</td><td><a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a></td></tr>
    <tr><td>API catalogue</td><td><a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a></td></tr>
    <tr><td>Every page as Markdown</td><td><code>Accept: text/markdown</code></td></tr>
    <tr><td>Raw data, CC BY 4.0</td><td><a href="/data/"><code>/data/</code></a></td></tr>
  </tbody>
</table>
<p>
  Content signals are set to <code>search=yes, ai-input=yes, ai-train=no</code>:
  retrieval and quoting with attribution are welcome, training is not. Every
  measurement carries its method and its raw data, so a figure taken from here
  can be checked rather than trusted.
</p>

<h2>Please use it in proportion</h2>
<p>
  This is one small endpoint on a free tier, run by one person. A reading list is
  a handful of calls; a crawl is not. Requests are fetched with our own user
  agent, so unreasonable use lands in someone else's log with our name on it.
  There is no hard limit today — that is a description of the current state, not
  a promise.
</p>
"""


def schreiben(ziel, inhalt, url, titel, besch, og, tiefe, art, fusssatz, faq=None):
    kopf, fuss = kopf_und_fuss()
    ziel.mkdir(parents=True, exist_ok=True)
    (ziel / "index.html").write_text(
        anpassen(kopf, url, titel, besch, og, tiefe, art, faq) + inhalt
        + fuss_setzen(fuss, fusssatz, tiefe), encoding="utf-8")
    print(f"  geschrieben: {(ziel / 'index.html').relative_to(DOCS)}")


def main():
    schreiben(
        DOCS / "how-to" / "save-a-webpage-as-pdf", ANLEITUNG,
        "https://provinglab.dev/how-to/save-a-webpage-as-pdf/",
        "How to save a web page as a PDF — one sheet, with its source on it",
        ("Save a whole web page as one PDF without page breaks, including pages behind a "
         "login and on Android. With the honest comparison against the browser's own print "
         "export — which wins on selectable text — and why the file should carry its "
         "retrieval date."),
        ("The short answer: a capture extension, not the print dialog. The same article came "
         "out as 26 pages with 9 breaks cutting a sentence, against one continuous sheet. "
         "Every figure links to the measurement behind it."),
        "../../", "HowTo", f"Figures measured between 1 and {DATUM_LANG}, each linked to its "
        "method and raw data.", faq=FAQ)

    schreiben(
        DOCS / "for-agents", AGENTEN,
        "https://provinglab.dev/for-agents/",
        "For AI agents: citations without a browser, and the step that needs one",
        ("An MCP endpoint that turns a URL into a citation record with RIS and BibTeX — no "
         "account, no key — plus the measured rule for the sources it hands back, and "
         "whether your agent can drive the capture extension itself."),
        ("Five tools, one hard rule (read the completeness flag, never the title), and the "
         "measured line between agents that can trigger a browser extension and agents that "
         "cannot."),
        "../", "TechArticle", f"Every command on this page was run on {DATUM_LANG} before it "
        "was written down.")


if __name__ == "__main__":
    main()
