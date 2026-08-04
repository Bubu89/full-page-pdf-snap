#!/usr/bin/env python3
"""build-headless-install-post.py — Beitrag zur Messung „Installation ohne Klick".

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und die gemeinsamen Meta-Angaben nicht auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "android-capture-extensions" / "index.html"
ZIEL = DOCS / "measurements" / "install-an-extension-without-a-click"
DATEI = DOCS / "data" / "2026-08-03-install-without-a-click.json"

SLUG = "install-an-extension-without-a-click"
URL = f"https://provinglab.dev/measurements/{SLUG}/"
TITEL = "Installing a browser extension without a click, and removing it again"
BESCHREIBUNG = (
    "Four routes measured on 3 August 2026. Firefox's own Marionette channel "
    "installs and uninstalls a signed store extension headless in 9.4 seconds "
    "with zero input events and no visible window. The click route took 179.4 "
    "seconds and installed nothing while reporting success at every step."
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
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": TITEL,
        "description": BESCHREIBUNG,
        "datePublished": "2026-08-03",
        "dateModified": "2026-08-03",
        "inLanguage": "en",
        "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab",
                   "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab",
                      "url": "https://provinglab.dev/"},
        "about": {
            "@type": "Dataset",
            "name": "Extension install and uninstall routes without user interaction, 2026-08-03",
            "description": (
                "Four routes — Marionette, CDP, enterprise policy and the "
                "store user interface — measured for whether they can install "
                "and remove a browser extension without a click, without a "
                "visible window and without administrator rights."
            ),
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "distribution": [{
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": f"https://provinglab.dev/data/{DATEI.name}",
            }],
        },
    }
    neu = ('<script type="application/ld+json">\n'
           + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>")
    return re.sub(r'<script type="application/ld\+json">.*?</script>',
                  lambda _: neu, k, count=1, flags=re.S)


def ja_nein(w):
    return {True: "yes", False: "no"}.get(w, str(w))


def wege_tabelle(d):
    namen = {"marionette": "Marionette (Firefox)", "cdp": "CDP (Chrome)",
             "richtlinie": "Enterprise policy", "oberflaeche": "Store UI + real input"}
    zeilen = []
    for w in d["wege"]:
        zeit = w.get("sekunden_rundlauf")
        zeilen.append(
            f'      <tr><th scope="row">{namen[w["weg"]]}</th>'
            f'<td>{ja_nein(w["installieren"])}</td>'
            f'<td>{ja_nein(w["deinstallieren"])}</td>'
            f'<td>{w["eingabe_ereignisse"]}</td>'
            f'<td>{"yes" if w["administratorrechte"] else "no"}</td>'
            f'<td>{ja_nein(w["zaehlt_im_store"])}</td>'
            f'<td class="num">{f"{zeit} s" if zeit else "—"}</td></tr>')
    return "\n".join(zeilen)


def schritte_tabelle(w):
    return "\n".join(
        f'      <tr><th scope="row">{s["schritt"]}</th>'
        f'<td class="num">{s["sekunden"]}</td>'
        f'<td>{"succeeded" if s["ok"] else "failed"}</td>'
        f'<td>{s.get("beleg", "—")}</td></tr>' for s in w["schritte"])


def inhalt(d):
    m = next(w for w in d["wege"] if w["weg"] == "marionette")
    u = next(w for w in d["wege"] if w["weg"] == "oberflaeche")
    c = next(w for w in d["wege"] if w["weg"] == "cdp")
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    An agent that can install an extension can also be asked to remove it. Both
    directions were measured across four routes on one machine, with an ordinary
    user account. One of them does both in 9.4 seconds without a window ever
    appearing — and it is the one route that does <em>not</em> count
    in the store's user statistics. That trade-off is the whole result.
  </p>
  <p class="meta">Measured {d["gemessen_am"]} · Firefox ESR and Chrome stable on Windows 11 ·
    <a href="/data/{DATEI.name}">raw data</a></p>
</header>

<h2>The four routes</h2>
<table>
  <caption>What each route can do, measured 3 August 2026</caption>
  <thead>
    <tr><th scope="col">Route</th><th scope="col">Install</th><th scope="col">Uninstall</th>
        <th scope="col">Input events</th><th scope="col">Admin rights</th>
        <th scope="col">Counts in store</th><th scope="col">Round trip</th></tr>
  </thead>
  <tbody>
{wege_tabelle(d)}
  </tbody>
</table>

<h2>Marionette: the channel Firefox already ships</h2>
<p>
  Firefox carries a remote control channel of its own — the one geckodriver
  speaks. Started with <code>-headless -marionette</code>, it answers
  <code>Addon:Install</code> and <code>Addon:Uninstall</code> over a TCP socket.
  No driver, no third-party package: a length-prefixed JSON protocol and about
  two dozen lines of client code.
</p>
<table>
  <caption>Round trip: uninstall, then install, verified against the profile</caption>
  <thead>
    <tr><th scope="col">Step</th><th scope="col">Seconds</th>
        <th scope="col">Outcome</th><th scope="col">Evidence</th></tr>
  </thead>
  <tbody>
{schritte_tabelle(m)}
  </tbody>
</table>
<p>
  The evidence column matters more than the outcome column. Every step is
  verified against <code>extensions.json</code> — the file Firefox itself
  maintains — not against the command's own reply. A command can report success
  and leave nothing behind, and on the route below, that is exactly what happened.
</p>

<h2>Why the click route is not a route</h2>
<p>
  Driving the store page with real input events is the only measured way to be
  counted as a store user, and on this machine it produced nothing. The run took
  {u["sekunden_rundlauf"]} seconds. Every click reported success, because a click
  into empty space is a valid click as far as Windows is concerned. The extension
  was not installed.
</p>
<p>
  The cause is fixed coordinates. A different resolution, a different font size or
  a changed store layout moves every target, and nothing in the script can tell
  the difference between hitting a button and hitting the space beside it. For a
  person that is an annoyance. For an agent it is worse than useless: <strong>a
  route that reports success on failure poisons everything downstream of it.</strong>
</p>
<p>
  It also needs the foreground. Real input events go to the focused window, so
  whoever sends them takes over the user's mouse and keyboard for the duration.
</p>

<h2>Chrome: half the answer</h2>
<p>
  Chrome has no Marionette. Over CDP with
  <code>--headless=new --enable-unsafe-extension-debugging</code>,
  <code>Extensions.loadUnpacked</code> loads an unpacked folder and returns its
  id, and <code>Extensions.uninstall</code> removes it. But
  <code>Extensions.install</code> does not exist —
  <code>-32601 'Extensions.install' wasn't found</code>. There is no CDP command
  that installs a store build.
</p>
<p>
  So for Chrome the honest answer is split: an agent can put an <em>unpacked</em>
  extension into a browser it controls, headless, and take it out again. Getting
  the <em>store</em> build in requires the user interface or an enterprise policy.
  Worth noting that the <code>Extensions</code> domain is not listed by
  <code>Schema.getDomains</code> at all, yet answers — so absence from the schema
  is not evidence that a command is missing. Only the error is.
</p>

<h2>The policy route — corrected 4 August 2026</h2>
<p style="border-left:3px solid #c93;padding-left:1rem">
  <strong>The first version of this page said the policy route was closed in
  both directions. That was too absolute.</strong> It holds for a
  <em>system</em> installation, and the measurement below still stands. It does
  not hold generally: unpack Firefox yourself — into
  <code>~/tools/firefox-release</code>, say — and
  <code>distribution/policies.json</code> is writable with no extra rights at
  all, with the policy fully in effect.
</p>
<p>
  For an agent that is not an edge case, it is the normal case: it brings its
  own browser rather than borrowing the user's. And unlike Marionette, which
  installs a local file, the policy fetches from the store — the entry carries
  an <code>install_url</code> pointing at the signed XPI on
  addons.mozilla.org:
</p>
<pre><code>{{"policies": {{"ExtensionSettings": {{
  "&lt;extension id&gt;": {{
    "installation_mode": "normal_installed",
    "install_url": "https://addons.mozilla.org/firefox/downloads/file/…xpi"
  }}}}}}}}</code></pre>
<p>
  Whether an installation triggered this way appears in the store's user count
  is <strong>not measured</strong>. It fetches from the store, which is the
  mechanism a counted install uses — but that is an inference, not a
  measurement, and this page does not present it as one.
</p>
<p>
  The correction came from a second measurement run in the same repository
  while this page was already published. That is what the raw data is for.
</p>

<h3>The original finding, unchanged: a system installation needs rights</h3>
<p>
  Enterprise policy is the usual answer to “install silently”, and it is also the
  route that could remove an extension the same way — <code>ExtensionSettings</code>
  with <code>installation_mode: blocked</code> uninstalls and blocks in one step.
  On this machine it does neither:
</p>
<ul>
  <li><code>C:\\Program Files\\Mozilla FirefoxESR\\distribution</code> — not writable,
      <code>UnauthorizedAccessException</code></li>
  <li><code>HKCU\\Software\\Policies\\Google\\Chrome</code> — ACL-protected,
      <code>UnauthorizedAccessException</code></li>
</ul>
<p>
  Without administrator rights the policy route is closed in <em>both</em>
  directions. This corrects an earlier version of our own agent skill, which said
  the Chrome entries could go under <code>HKCU</code> without elevation. They
  cannot.
</p>

<h2>The trade-off, stated plainly</h2>
<p>
  Marionette installs the file. It does not visit a store page, so it does not
  appear in the store's user count. The XPI is the signed store build — the same
  bytes, checksummed in the raw data — but the visit that would be counted never
  happens.
</p>
<p>
  That is the correct outcome, not a limitation to design around. A user number is
  supposed to mean “someone chose to install this”. Anyone who wants to be counted
  has to go through the interface, as a person would. Both stores terminate the
  <em>developer</em> account for inflating installs, so the incentive here points
  in exactly one direction.
</p>

<h2>A side finding about WSL</h2>
<p>
  Firefox binds Marionette to <code>127.0.0.1</code> of the Windows host, and from
  WSL2 that port is unreachable — neither over <code>127.0.0.1</code> nor over the
  host address, both refused. The client has to run on the same side as the
  browser. This is not specific to Marionette; it applies to any browser control
  channel bound to loopback.
</p>

<h2>Reproducing this</h2>
<p>
  One command, and it writes its own raw data:
</p>
<pre><code>python3 tools/erweiterung-fernsteuern.py rundlauf --protokoll lauf.json</code></pre>
<p>
  Firefox must not have the target profile open — the tool checks whether the lock
  file is actually <em>held</em>, not merely present, and stops rather than killing
  someone's browser. Source:
  <a href="https://github.com/Bubu89/full-page-pdf-snap">github.com/Bubu89/full-page-pdf-snap</a>.
</p>

<h2>Questions</h2>
<h3>Is doing this allowed?</h3>
<p>
  Installing an extension into a browser on a machine you administer, or that the
  user asked you to set up, is ordinary configuration. What is not allowed under
  either store's terms is manufacturing installs to move a public number. Nothing
  here does that — this route is invisible to the counter, which is precisely why
  it is safe to publish.
</p>
<h3>Will this keep working?</h3>
<p>
  Unknown. Marionette exists because Firefox's own test tooling needs it, and
  <code>--enable-unsafe-extension-debugging</code> is named the way it is for a
  reason. Both are subject to change. The measurement says what was true on
  3 August 2026 on one machine; if it stops being true, the reproduction command
  above will say so.
</p>
<h3>Can this uninstall an extension a user installed themselves?</h3>
<p>
  Yes — <code>Addon:Uninstall</code> does not care how the add-on arrived. That
  cuts both ways, and it is the reason this page states the profile check so
  prominently: a tool that removes extensions should be certain which profile it
  is pointed at. On this machine six profiles sit side by side.
</p>

"""


def main():
    d = json.loads(DATEI.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    kopf = anpassen(kopf, d)
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Method: single run per route on one Windows 11 machine with an ordinary user\n'
        '      account, 3 August 2026. Firefox ESR and Chrome stable. Install and uninstall verified\n'
        '      against the profile\'s own <code>extensions.json</code>, not against command replies.\n'
        '      Times include starting and quitting the browser and are a single measurement, not a\n'
        '      mean. Circumventing a protection measure is not something any of these routes\n'
        '      does: each uses a control channel the browser documents and ships, and none\n'
        '      touches a restriction a publisher or a store put in place. The author\n'
        '      develops the extension used in the test.\n'
        '      Nothing here is legal advice.\n      <br><br>\n'
        '      Corrections are welcome and are made in public:\n'
        '      <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">open an issue</a>.\n'
        '      The tool and its raw data are published so that a wrong figure here can be shown\n'
        '      to be wrong — run the reproduction command above and post what you get.\n'
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
