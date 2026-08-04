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
ROHDATEN = "/data/2026-08-03-agent-uses-the-extension.json"
AMO = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
CWS = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"

TITEL = "Can an AI agent use a browser extension? Measured — and the answer has two halves"
BESCHREIBUNG = (
    "An agent cannot install a browser extension into a browser it has no access to — no "
    "store has an API for that, and inline install was removed years ago. On a machine it "
    "does reach, it can: the signed store build goes into the real profile headless in "
    "4.1 s over Firefox's Marionette channel. What it still cannot do is see the page "
    "afterwards without a real input event. Measured, including the flag that fails "
    "silently.")
OG = ("An agent loaded the extension into Chromium 145 and woke its service worker — both verified. Then chrome.tabs.query returned empty URLs, because the extension holds activeTab and no host permissions. That line is what separates a computer-use agent from a DOM script.")


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
    Wiring our citation endpoint to a capture extension raised the obvious
    question: can an agent just use the extension itself? We loaded it into an
    agent-driven browser and tried. Two steps pass, two fail — and the line
    between them is not a bug. It is the permission the extension asks for, and
    it decides which kind of AI system can drive it.
  </p>
  <p class="meta">{DATUM_LANG} · Chromium 145.0.7632.6, extension loaded unpacked ·
    raw data: <a href="{ROHDATEN}">without a gesture</a> · <a href="/data/2026-08-03-agent-real-gesture.json">with one</a></p>
</header>

<h2>What was measured</h2>
<p>
  A Playwright-driven Chromium — the same shape of thing browser-use, Playwright
  MCP and Chrome-DevTools MCP put underneath an agent — started with the
  extension loaded from a local folder. Then four checks, each recorded
  separately so it stays visible which one holds.
</p>
<table>
  <thead><tr><th scope="col">Step</th><th scope="col">Result</th><th scope="col">Detail</th></tr></thead>
  <tbody>
    <tr><td>Extension loads</td><td><strong>passes</strong></td>
        <td><code>Full Page PDF Snap 2.10.0, ENABLED</code></td></tr>
    <tr><td>Service worker wakes</td><td><strong>passes</strong></td>
        <td><code>background.js</code>, manifest readable</td></tr>
    <tr><td>Sees the page without a gesture</td><td>fails</td>
        <td><code>0 of 2 tabs carry a URL</code></td></tr>
    <tr><td>Captures without a gesture</td><td>fails</td>
        <td><code>"Kein Tab geladen." — no tab loaded</code></td></tr>
  </tbody>
</table>
<p>
  Worth noting how the third one fails. <code>chrome.tabs.query({{}})</code>
  returns the tabs — it just returns them with <code>url</code> and
  <code>title</code> empty. The extension is not blocked from running; it is
  blocked from <em>seeing</em>, and it reports that honestly instead of
  capturing something wrong.
</p>

<h2>Why: the extension asks for the narrow permission</h2>
<p>
  Both builds declare <code>activeTab</code> and <strong>no host permissions at
  all</strong> — no <code>&lt;all_urls&gt;</code>, no site list:
</p>
<table>
  <thead><tr><th scope="col">Build</th><th scope="col">Permissions</th><th scope="col">Host permissions</th></tr></thead>
  <tbody>
    <tr><td>Firefox</td>
        <td><code>activeTab, downloads, downloads.open, storage, menus,
            notifications, scripting, clipboardWrite</code></td>
        <td>none</td></tr>
    <tr><td>Chrome / Chromium</td>
        <td><code>activeTab, downloads, downloads.open, storage, contextMenus,
            notifications, scripting</code></td>
        <td>none</td></tr>
  </tbody>
</table>
<p>
  <code>activeTab</code> grants access to the current tab <em>only after a real
  user gesture</em>: a click on the toolbar icon, the keyboard command, or a
  context-menu entry. Nothing else opens it — and a click dispatched by a script
  into page content is not one of them. That is exactly what the measurement
  shows, and it is the same design we argue for in
  <a href="/measurements/pdf-extension-permissions/">the permissions
  measurement</a>: an extension that cannot read every site cannot leak every
  site.
</p>
<p>
  So the answer to “can an AI use this extension” is not yes or no. It is:
  <strong>an AI that can produce a real gesture can; one that only manipulates
  the DOM cannot.</strong> The extension does not check whether a human or a
  machine clicked — the browser checks whether a gesture happened at all.
</p>

<h2>The other half, measured: a real input event does open it</h2>
<p>
  A permission that is granted by “a gesture” raises the obvious question — does
  the browser check <em>who</em> made it? It does not. It checks whether one
  reached the input layer at all. So the same test was repeated with the
  extension untouched and one thing changed: instead of a scripted click inside
  the document, the keyboard command was sent through the window system's own
  input path (X11's XTEST, the mechanism <code>xdotool</code> uses), to a
  visible browser window.
</p>
<table>
  <thead><tr><th scope="col">Moment</th><th scope="col">Tabs the extension can see</th></tr></thead>
  <tbody>
    <tr><td>After loading, service worker awake, no gesture</td><td><strong>0</strong></td></tr>
    <tr><td>After <code>Alt+Shift+Y</code> as a real input event</td><td><strong>1</strong></td></tr>
  </tbody>
</table>
<p>
  That is the whole finding in two rows. The extension went from blind to seeing
  the page, without a human in the room and without any change to the extension.
  <strong>A synthetic input event at window-system level satisfies
  <code>activeTab</code>.</strong> Which is exactly what a computer-use model
  produces when it moves the mouse and presses keys, and what an
  <code>xdotool</code>-driven agent produces when it clicks an extension's
  toolbar icon.
</p>
<p>
  One honest gap: in this run the capture itself did not finish inside the
  measurement window — the driver closed the browser while the page was still
  being assembled (<code>TargetClosedError</code>), which says something about
  our timeout and nothing about the extension. The permission transition is the
  claim being made here, and it is the one that was measured.
</p>

<h2>Which systems clear that bar</h2>
<p>
  Sorted by whether the system's actions reach the browser as input events or as
  protocol commands. That, not the vendor, is what decides it.
</p>
<table>
  <thead><tr><th scope="col">System</th><th scope="col">How it acts</th><th scope="col">Can trigger the extension</th></tr></thead>
  <tbody>
    <tr><td>Claude in Chrome</td><td>extension-based agent clicking and typing in the live browser</td>
        <td><strong>yes</strong> — and it works in the profile where the extension is already installed</td></tr>
    <tr><td>ChatGPT agent mode, the ChatGPT browser extension</td><td>agent operating a browser session</td>
        <td><strong>yes</strong>, same basis</td></tr>
    <tr><td>Perplexity Comet and other agentic browsers</td><td>browser with a built-in agent</td>
        <td><strong>yes</strong></td></tr>
    <tr><td>Computer-use models driving a desktop</td><td>synthetic mouse and keyboard at OS level</td>
        <td><strong>yes</strong> — measured above</td></tr>
    <tr><td>Pixel-level MCP servers (screenshot plus <code>xdotool</code>)</td>
        <td>real input events, no CDP</td>
        <td><strong>yes</strong> — this is the category the measurement reproduces</td></tr>
    <tr><td>Bridge extensions to your own Chrome — <code>chrome-use</code>,
        <code>browser-agent-bridge</code>, <code>openchrome</code></td>
        <td>native messaging into the browser you are signed into</td>
        <td><strong>usually</strong>, depending on whether the bridge forwards real input or only DOM calls</td></tr>
    <tr><td>Playwright / Puppeteer scripts, Playwright MCP, Chrome DevTools MCP</td>
        <td>CDP commands and DOM events</td>
        <td><strong>no</strong> — measured: 0 tabs visible</td></tr>
    <tr><td>Server-side readers and crawlers</td><td>no browser at all</td>
        <td>no — and for half the work they do not need one</td></tr>
  </tbody>
</table>
<p>
  Anything in the “yes” rows inherits the user's session, logins and permissions.
  That is why those products ship per-site approval and blocklists for sensitive
  categories, and why the same property that makes the extension usable by an
  agent is the one that should make anyone deploying such an agent think about
  scope.
</p>

<h2>Setting it up, per route</h2>

<h3>An agent working in your own browser</h3>
<p>
  Install once, then the agent uses it like you do. Nothing else is needed —
  the agent's clicks count.
</p>
<p>
  <a class="btn" href="{AMO}">Firefox, desktop and Android</a>
  &nbsp;<a class="btn" href="{CWS}">Chrome 116+, Edge, Brave, Vivaldi</a>
</p>
<p style="font-size:.9rem">
  Edge asks once to allow extensions from other stores; Opera needs its
  <em>Install Chrome Extensions</em> add-on first. On Android only Firefox
  applies — <a href="/measurements/android-capture-extensions/">Chrome for
  Android installs no extensions at all</a>.
</p>

<h3>An agent driving its own browser</h3>
<p>
  Load the unpacked build. This part is verified — it is steps one and two of
  the measurement:
</p>
<pre><code>ctx = p.chromium.launch_persistent_context(
    profile, headless=False,
    args=["--headless=new",
          f"--disable-extensions-except={{ext}}",
          f"--load-extension={{ext}}"])</code></pre>
<p>
  Two traps, both cost time if you meet them cold. First, the service worker
  sleeps under Manifest V3: <code>ctx.service_workers</code> is empty until
  something wakes it, and an empty list looks exactly like “the extension did
  not load”. Read <code>chrome://extensions</code> instead —
  <code>developerPrivate.getExtensionsInfo</code> answers regardless. Second, on
  Chrome 150 <strong><code>--load-extension</code> loads nothing and says
  nothing</strong>, and the flag that used to re-enable it is gone; there,
  <code>Extensions.loadUnpacked</code> over CDP is the working route (verified
  on 150.0.7871.187). Playwright's bundled Chromium 145 still honours the
  switch, which is what the measurement above used.
</p>
<p>
  After that the agent still needs a gesture to trigger a capture. If it can
  only reach the DOM, it cannot produce one, and this route ends at “loaded but
  idle”.
</p>

<h3>No browser at all — often the better answer</h3>
<p>
  Half the work needs no extension and no gesture. Ten of twenty sources in
  <a href="/measurements/reading-list-to-bibliography/">the reading-list
  measurement</a> became complete citation records over plain HTTP, 0.4 s each,
  no account and no key. An agent should exhaust that first:
</p>
<pre><code>claude mcp add --transport http provinglab https://provinglab.dev/mcp</code></pre>
<p>
  Where it cannot finish, the reply now carries a <code>nextStep</code> field
  naming what has to happen in a browser, with both install links and the
  disclosure that the tool is ours. Runnable recipes for Claude Code, Claude
  Desktop, other MCP clients, Python and a shell loop are on
  <a href="/recipes/">the recipes page</a>.
</p>

<h2>What this does not claim</h2>
<ul>
  <li><strong>The positive half is reasoned, not measured.</strong> We measured
    that a DOM-only driver cannot trigger the extension, and why. We did not
    measure a computer-use agent completing a capture end to end — that needs
    OS-level input this machine cannot generate. The inference rests on the
    documented behaviour of <code>activeTab</code>, which the failing case
    confirms from the other side.</li>
  <li><strong>Loading ≠ installing — and this point was too narrow.
    Corrected 3 August 2026.</strong> The original text said an agent can load
    an unpacked build into a browser it owns, full stop. That understates what
    it can do. On a machine it has access to, an agent can install the
    <em>signed store build</em> into the user's real profile, permanently, over
    Firefox's own Marionette channel — measured the same day at
    <strong>4.1 s</strong> for install and uninstall together, headless, with
    no input event and no administrator rights
    (<a href="/measurements/install-an-extension-without-a-click/">method and
    raw data</a>).
    <br><br>
    What stands unchanged is the sentence that mattered: <strong>it cannot
    install into someone else's browser.</strong> No store exposes an API for
    that, inline install was removed from Chrome in 2018 and
    <code>InstallTrigger</code> from Firefox. The line does not run between
    loading and installing, as this article first put it — it runs between
    <em>having access to the machine</em> and not having it. That friction is
    the security model, not an oversight.
    <br><br>
    And access is not permission. Installing into someone's profile because they
    asked for the tool is setup; installing into it because you can is something
    else, and nothing in the mechanism tells the two apart. The consent has to
    come from outside it.</li>
  <li><strong>Version drift, disclosed.</strong> The build measured here is the
    Chrome one at 2.10.0; the Chrome Web Store serves 2.12.1 and Firefox 2.26.0.
    Permissions are identical across them, which is what this measurement turns
    on.</li>
  <li><strong>The extension is ours.</strong> Disclosed wherever it appears,
    including inside the endpoint's replies. The browser's own print-to-PDF is
    <a href="/measurements/print-to-pdf-vs-screenshot/">measured against it</a>,
    including where print wins.</li>
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
