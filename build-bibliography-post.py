#!/usr/bin/env python3
"""Erzeugt die beiden Seiten zur Messung 'reading list to bibliography'.

    python3 build-bibliography-post.py

Zwei Seiten aus einem Datensatz, weil zwei verschiedene Fragen daran haengen:

  /measurements/reading-list-to-bibliography/
      Was ein Werkzeug an einer Quellenliste erledigt und was nicht — und
      warum. Der Befund, der die Muehe wert war: die Haelfte der Rueckgaben
      sind keine Abwehr, sondern Seiten ohne Zitationsangaben.

  /notes/sources-a-machine-cannot-cite/
      Was ein Mensch mit den zurueckgegebenen tut. Drei Faelle, drei Wege.
      Hier steht der Nutzen der Erweiterung — an der Stelle, an der die
      Automatik ehrlich aufhoert, nicht als Behauptung vorneweg.

Kopf und Fuss stammen aus bestehenden Seiten, damit Navigation und Stil nicht
auseinanderlaufen.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
DATEN = DOCS / "data" / "2026-08-03-reading-list-to-bibliography.json"

VORLAGE_M = DOCS / "measurements" / "citation-triage" / "index.html"
VORLAGE_N = DOCS / "notes" / "mcp-server-what-it-solves" / "index.html"

DATUM = "2026-08-03"
DATUM_LANG = "3 August 2026"
ROHDATEN = "/data/2026-08-03-reading-list-to-bibliography.json"


# ---------------------------------------------------------------- Geruest

def kopf_und_fuss(vorlage):
    """Kopf bis einschliesslich der Oeffnung des Layout-Containers.

    Der Fuss der Vorlage schliesst dieses <div> wieder. Wird die Oeffnung beim
    Schneiden weggelassen, hat die fertige Seite ein </div> zu viel und keinen
    Breitenrahmen — sichtbar erst im Browser, nicht im Quelltext.
    """
    s = vorlage.read_text(encoding="utf-8")
    auf = '<div class="wrap">'
    schnitt = s.index(auf) + len(auf)
    return s[:schnitt], s[s.index("<footer"):]


def anpassen(kopf, url, titel, beschreibung, og_beschreibung, tiefe, art):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{titel} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + beschreibung + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{titel}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + og_beschreibung + m.group(2), k)
    k = re.sub(r'(<link rel="icon" href=")[^"]*(")', rf"\g<1>{tiefe}icon-128.png\g<2>", k)
    # Die Vorlage traegt eine deutsche Fassung im selben Dokument und verweist
    # mit #b-de darauf. Seiten ohne diesen Abschnitt haetten damit einen toten
    # Anker in der Navigation — auf die Sammelseite umbiegen.
    k = k.replace('href="#b-de"', f'href="{tiefe}deutsch/"')
    ld = {
        "@context": "https://schema.org", "@type": art,
        "headline": titel, "description": beschreibung,
        "datePublished": DATUM, "dateModified": DATUM,
        "inLanguage": "en", "url": url,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)
    return k


KORREKTUR = ('Corrections are welcome and are made in public: '
             '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">open an issue</a>. '
             'If a figure here is wrong, the data and the script are published so it can be '
             'shown to be wrong.')


def fuss_setzen(fuss, satz, tiefe, offenlegung=""):
    return re.sub(
        r"<footer>.*?</footer>",
        lambda _: (f'<footer>\n      {satz}\n      Raw data: '
                   f'<a href="{ROHDATEN}">JSON</a>, CC BY 4.0.\n      <br><br>\n'
                   f'      {KORREKTUR}{offenlegung}\n      <br><br>\n'
                   f'      <a href="{tiefe}">← Proving Lab</a> · '
                   f'<a href="{tiefe}disclaimer/">Disclaimer</a>\n    </footer>'),
        fuss, count=1, flags=re.S)


# ---------------------------------------------------------------- Auswertung

def gruppen(d):
    """Teilt die Rueckgaben nach dem, was sie verursacht hat."""
    rest = [e for e in d["per_source"] if not e["complete"]]
    wand, tot, stumm = [], [], []
    for e in rest:
        leser = e.get("as_reader", {}).get("status")
        browser = e.get("as_browser", {}).get("status")
        if browser == 200 and leser != 200:
            wand.append(e)
        elif browser != 200:
            tot.append(e)
        else:
            stumm.append(e)
    return wand, tot, stumm


def zeilen(eintraege, grund):
    return "\n".join(
        f'    <tr><th scope="row"><code>{e["host"]}</code></th><td>{e["kind"]}</td>'
        f'<td>{grund(e)}</td></tr>' for e in eintraege)


# ---------------------------------------------------------------- Messseite

def messseite(d):
    r = d["results"]
    wand, tot, stumm = gruppen(d)
    art = r["by_kind"]

    def nach_art(schluessel):
        a = art.get(schluessel, {"complete": 0, "total": 0})
        return f'{a["complete"]}/{a["total"]}'

    tab_art = "\n".join(
        f'    <tr><td>{k}</td><td>{v["complete"]} of {v["total"]}</td></tr>'
        for k, v in sorted(art.items(), key=lambda x: -x[1]["complete"] / x[1]["total"]))

    t_wand = zeilen(wand, lambda e: "answers a browser, refuses the reader")
    t_tot = zeilen(tot, lambda e: f'refuses both — HTTP {e["as_browser"]["status"]} '
                                  f'from a data centre address')
    t_stumm = zeilen(stumm, lambda e: "answers in full, declares no citation data")

    return f"""
<header>
  <h1>Twenty links, ten citations: what a machine finishes and what it hands back</h1>
  <p class="standfirst">
    A reading list of twenty sources through a citation endpoint. Ten came back
    as complete records with RIS and BibTeX, in eight seconds. The interesting
    half is the other ten — because only one of them was stopped by a bot
    defence. Five answered every request in full and simply had no citation data
    to declare.
  </p>
  <p class="meta">{DATUM_LANG} · {r['sources']} sources, one pass ·
    <a href="{ROHDATEN}">raw data</a></p>
</header>

<h2>The question</h2>
<p>
  A bibliography is the part of a piece of work where a machine looks most
  useful and is hardest to check. Hand an assistant twenty addresses, ask for a
  reference list, and something plausible comes back for all twenty. The
  question worth measuring is not how many entries appear. It is how many are
  <em>records</em> — read from what the page declares about itself — and whether
  the rest are named as gaps or quietly filled in.
</p>
<p>
  Each source was sent once to <code>extract_citation</code> on this site's
  <a href="/notes/mcp-server-what-it-solves/">MCP endpoint</a>, which reads the
  citation metadata a page publishes about itself and returns a structured
  record. Nothing was retried, nothing was chosen for whether it works. Every
  address was checked in a browser before the run, so that a typo of ours could
  not be counted as a failure of theirs.
</p>

<div class="kf-row">
  <div class="kf b"><div class="n">{r['complete_records']}/{r['sources']}</div><div class="l">complete records</div></div>
  <div class="kf"><div class="n">{r['handed_back_behind_a_wall']}</div><div class="l">stopped by a bot defence</div></div>
  <div class="kf"><div class="n">{r['handed_back_thin_page']}</div><div class="l">no citation data on the page</div></div>
  <div class="kf"><div class="n">{r['seconds_per_source']} s</div><div class="l">per source</div></div>
</div>

<h2>Where the split runs</h2>
<p>
  Not between disciplines, and not between paid and free. It runs between pages
  built to be cited and pages built to be read.
</p>
<table>
  <thead><tr><th scope="col">Kind of source</th><th scope="col">Complete records</th></tr></thead>
  <tbody>
{tab_art}
  </tbody>
</table>
<p>
  Journal publishers are the easiest case, whether the article is paywalled or
  open: {nach_art('publisher')} and {nach_art('open access')}. A journal page
  carries <code>citation_author</code>, <code>citation_title</code> and a DOI in
  its head, because it wants to be indexed. An encyclopaedia entry and a bare
  DOI resolve just as cleanly.
</p>
<p>
  Official statistics, chambers of commerce and newspapers are the hard case:
  none of the four produced a record. Not because they defend themselves — they
  answered every request in full — but because a statistics portal page is a
  topic overview, not a work, and declares no author, no date and no title of
  the kind a reference list needs.
</p>

<h2>The ten that came back, sorted by cause</h2>
<p>
  The distinction matters because each cause needs a different response from
  whoever is writing. Lumping them together as “blocked” is what makes a
  citation tool feel unreliable when it is being accurate.
</p>

<h3>One was stopped by a bot defence</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Kind</th><th scope="col">What happened</th></tr></thead>
  <tbody>
{t_wand}
  </tbody>
</table>
<p>
  This is the only case in twenty where a browser sees something a server-side
  reader is not allowed to see. It is also the only case where opening the page
  yourself changes the outcome — see
  <a href="/notes/sources-a-machine-cannot-cite/">what to do with the ten</a>.
</p>

<h3>Four refuse everyone from this address</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Kind</th><th scope="col">What happened</th></tr></thead>
  <tbody>
{t_tot}
  </tbody>
</table>
<p>
  These answered 403 to a browser user agent as readily as to a reader. The
  common factor is not the client but the network: requests from a data centre
  are refused whatever they claim to be. From a home connection the same pages
  open normally. That is worth stating plainly, because it is the one result
  here that would look different measured from a different place.
</p>

<h3>Five answered in full and had nothing to declare</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Kind</th><th scope="col">What happened</th></tr></thead>
  <tbody>
{t_stumm}
  </tbody>
</table>
<p>
  Fifty to ninety kilobytes of perfectly readable HTML, no defence of any kind,
  and no <code>citation_*</code> metadata, no author, no publication date. A
  reference for these has to be written by a person who decides what the work
  <em>is</em> — a page of a statistics portal, an article in a newspaper, a
  software release on a repository. No amount of retrying changes that, and any
  tool that returns a tidy entry here has invented the missing half.
</p>

<h2>A record can carry a title and still not be one</h2>
<p>
  Two of the five silent cases are the trap this measurement was worth doing
  for. The Zenodo record returns
  <code>"kjswedberg/kjswedberg.github.io: First Release"</code> with an author
  attached; the statistics portal returns
  <code>"Forschung, Innovation, Digitalisierung"</code> with
  <code>STATISTIK AUSTRIA</code> as author. Both look like results. Both come
  back with <code>complete: false</code>.
</p>
<p>
  Anything reading the title field and skipping the flag will file both as
  sources. The lesson is not about this endpoint — it applies to every citation
  service: <strong>read the completeness flag, not the title.</strong> On this
  endpoint that check is one field:
</p>
<pre><code>if not record["complete"]:
    hand_back(url, record.get("warning") or "no citation data on the page")</code></pre>
<p>
  A gap we should close on our side: in these five cases the
  <code>warning</code> field is empty. <code>complete: false</code> is correct
  and sufficient to act on, but a reason would be more useful than a silence,
  and it is <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">noted
  as such</a>.
</p>

<h2>Counter-measurement: a second network, and what it did not change</h2>
<p>
  The section below said a home connection should produce a higher completion
  rate. That claim has now been tested once — from a commercial VPN exit rather
  than a home line — and it mostly did not hold.
</p>
<table>
  <thead><tr><th scope="col"></th><th scope="col">Data centre</th><th scope="col">VPN exit</th></tr></thead>
  <tbody>
    <tr><td>Complete records</td><td>10</td><td><strong>11</strong></td></tr>
    <tr><td>Stopped by a bot defence</td><td>1</td><td>1</td></tr>
    <tr><td>Refusing every client from this address</td><td><strong>4</strong></td><td><strong>4</strong></td></tr>
    <tr><td>Answered in full, declared nothing</td><td>5</td><td>4</td></tr>
    <tr><td>Seconds per source</td><td>0.4</td><td>0.7</td></tr>
  </tbody>
</table>
<p>
  <strong>The four network-level refusals did not move.</strong> ScienceDirect,
  SSRN, the OECD and EUR-Lex answered the second address exactly as they
  answered the first. The likely reason is that a commercial VPN exit is itself
  a data-centre range — so this run swapped one data centre for another rather
  than testing the claim. <em>Whether a residential connection changes the
  outcome is still open</em>, and this measurement does not close it.
</p>
<p>
  The one source that changed is Zenodo, and not because of the network: it
  returned <code>authors, doi, title</code> on the first run and
  <code>authors, doi, publisher, title, year</code> on the second. The record
  gained a year, which is the field that decides completeness. Either the
  deposit was edited between the runs or Zenodo serves its metadata unevenly —
  from outside, both look the same.
</p>
<p>
  Raw data: <a href="/data/2026-08-03-reading-list-to-bibliography-vpn-ausgang.json">second
  run</a>. Anyone with a residential line is invited to settle the open half —
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues/3">issue 3</a>.
</p>

<h2>What this does not settle</h2>
<ul>
  <li><strong>Twenty sources is a shape, not a study.</strong> For coverage
    against an established service on randomly drawn samples, the
    <a href="/measurements/citation-extraction/">Citoid comparison</a> is the
    measurement to cite. This one shows how the work divides.</li>
  <li><strong>The address you measure from changes the result — less than
    expected.</strong> A second run from a different address left all four
    network-level refusals in place. A residential line might still differ, but
    that is now an open question rather than an assumption — and is welcome to
    say so; the <a href="{ROHDATEN}">data</a> and the
    <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/messung-literaturverzeichnis.py">script</a>
    are both published.</li>
  <li><strong>The split moves.</strong> Publishers tighten defences, and pages
    are rebuilt. A figure here is one afternoon, not a constant.</li>
  <li><strong>A publisher's own export beats all of this.</strong> Where a page
    offers RIS or BibTeX for download, that file is authoritative and this is
    not.</li>
</ul>

<h2>Running it yourself</h2>
<p>
  One URL per line in, one importable <code>.ris</code> out, with the refusals
  named on stderr instead of half-imported. The
  <a href="/recipes/">recipes page</a> has the same thing for Claude Code,
  Claude Desktop, Python and the browser.
</p>
<pre><code>while read -r u; do
  curl -sX POST https://provinglab.dev/mcp \\
    -H 'content-type: application/json' \\
    -d "{{\\"jsonrpc\\":\\"2.0\\",\\"id\\":1,\\"method\\":\\"tools/call\\",
         \\"params\\":{{\\"name\\":\\"extract_citation\\",\\"arguments\\":{{\\"url\\":\\"$u\\"}}}}}}" \\
  | python3 -c 'import json,sys
d = json.loads(json.load(sys.stdin)["result"]["content"][0]["text"])
sys.stdout.write(d["ris"]) if d.get("complete") else \\
  sys.stderr.write("hand back: " + d["url"] + "\\n")'
done &lt; reading-list.txt &gt; literature.ris</code></pre>
<p>
  Then <em>Zotero → File → Import</em>, or <em>Citavi → Import → RIS</em>. No
  key, no account. One caveat worth knowing: this site sits behind a filter that
  refuses the user agent Python's <code>urllib</code> sends by default. Set any
  user agent of your own and it answers normally.
</p>
"""


# ---------------------------------------------------------------- Notizseite

def notizseite(d):
    r = d["results"]
    wand, tot, stumm = gruppen(d)
    return f"""
<header>
  <h1>The sources a machine cannot cite for you — and how to cite them anyway</h1>
  <p class="standfirst">
    Of twenty sources in a reading list, ten came back as finished citations and
    ten were handed back. Handing them back is the right behaviour. This is what
    to do with them, which differs by cause — and only one of the three cases is
    solved by opening the page in a browser.
  </p>
  <p class="meta">{DATUM_LANG} · from the
    <a href="/measurements/reading-list-to-bibliography/">twenty-source
    measurement</a></p>
</header>

<p>
  Anyone assembling a reference list from web sources meets the same wall
  eventually: the automated part stops, and it is not obvious whether the tool
  failed, the page is defended, or there was never anything there to collect.
  The three look identical from the outside — an empty result — and they need
  completely different work. Guessing wrong wastes an afternoon on a page that
  will never yield a record, or gives up on one that opens on the first click.
</p>
<p>
  So the useful question is not <em>how do I get a citation</em>. It is
  <em>which of the three is this?</em>
</p>

<h2>Case 1 — the page answers a browser but not a reader</h2>
<p>
  <strong>{len(wand)} of the twenty.</strong> A server-side reader gets 403; a
  browser gets the page. This is a bot defence, and it is the only case where
  opening the source yourself changes what is available.
</p>
<p>
  What to do: open it in the browser you already have. Your session, your
  network, your institutional access. Then take the source with you before it
  changes — a
  <a href="/tools/full-page-pdf-snap/">full-page capture</a> writes the page as
  one PDF with the URL and the retrieval date on it, which is what a reference
  to a web source has to carry anyway. The metadata for the entry is then in
  the header of your own file rather than in a service's index.
</p>
<p>
  Why bother capturing at all, rather than noting the link: because
  <a href="/measurements/web-citations-that-vanish/">we measured what happens to
  web sources after they are cited</a>. A URL in a reference list is a promise
  about a page you no longer control.
</p>

<h2>Case 2 — the page refuses everyone from this address</h2>
<p>
  <strong>{len(tot)} of the twenty.</strong> 403 to a browser user agent as
  readily as to a reader. Here the client is not the problem: requests coming
  from a data centre are refused whatever they claim to be. Publishers do this
  to deter bulk downloading, and it catches every automated tool equally.
</p>
<p>
  What to do: nothing clever. Open the page from your own connection, where
  these same publishers answer normally, and use their own export — most journal
  pages offer <em>Cite</em> → RIS or BibTeX, and that file is better than
  anything a reader can reconstruct. If you need the article itself rather than
  the entry, that is a library question, not a tooling question.
</p>
<p>
  The one thing not to do is retry from the same place with a different user
  agent. It does not work, and a tool that pretends to be a browser to get past
  a rule that is aimed at it is a tool you cannot cite in good conscience.
</p>

<h2>Case 3 — the page answers in full and has nothing to declare</h2>
<p>
  <strong>{len(stumm)} of the twenty — the largest group, and the one people
  expect least.</strong> Fifty to ninety kilobytes of readable HTML, no defence
  of any kind, and no author, no date, no title of a work. A statistics portal
  page, a chamber-of-commerce service page, a news article, a software release.
</p>
<p>
  What to do: write the entry yourself, because the decision the machine cannot
  make is <em>what the work is</em>. Is the source the statistics portal page,
  the dataset behind it, or the release the portal announces? A citation tool
  that answers here has picked one for you without saying so.
</p>
<p>
  Two things make that manual entry defensible. First, the retrieval date, which
  for a page with no publication date is the only date the reference can carry.
  Second, the state of the page as you saw it — a
  <a href="/tools/full-page-pdf-snap/">capture</a> stamped with the URL and the
  date, kept with the work. For grey literature and official web pages this is
  not belt and braces; a corporate page or an agency portal is rebuilt on no
  schedule and with no notice.
</p>

<h2>Telling the three apart in one step</h2>
<p>
  Two requests answer it. If the second succeeds where the first fails, it is
  case 1. If both fail, case 2. If both succeed and the record still comes back
  <code>complete: false</code>, case 3.
</p>
<pre><code>curl -sI -A 'my-reader/1.0' "$URL" | head -1     # as a reader
curl -sI -A "$BROWSER_UA"    "$URL" | head -1     # as a browser</code></pre>
<p>
  In an AI workflow the same three cases fall out of the record itself: a
  <code>warning</code> naming a wall is case 1 or 2, and
  <code>complete: false</code> with no warning is case 3. Which is why the flag
  matters more than the title — the
  <a href="/measurements/reading-list-to-bibliography/">measurement</a> has two
  records that carry a title, an author, and no completeness.
</p>

<h2>What this is not</h2>
<ul>
  <li><strong>Not a way past a paywall.</strong> Every case above assumes you
    have access — your own, or your institution's. Capturing a page you may
    read is a copy for your own use; it is not a route to one you may not.</li>
  <li><strong>Not a replacement for a publisher's export.</strong> Where a
    <em>Cite</em> button exists, use it.</li>
  <li><strong>Not stable.</strong> {len(tot)} of these refusals are refusals of
    a data centre address and would not reproduce from a home connection. The
    <a href="{ROHDATEN}">data</a> says which.</li>
</ul>
"""


# ---------------------------------------------------------------- Schreiben

def schreiben(ziel, vorlage, inhalt, url, titel, besch, og, tiefe, art, fusssatz,
              offenlegung=""):
    kopf, fuss = kopf_und_fuss(vorlage)
    ziel.mkdir(parents=True, exist_ok=True)
    seite = (anpassen(kopf, url, titel, besch, og, tiefe, art)
             + inhalt + fuss_setzen(fuss, fusssatz, tiefe, offenlegung))
    (ziel / "index.html").write_text(seite, encoding="utf-8")
    print(f"  geschrieben: {(ziel / 'index.html').relative_to(DOCS)}")


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))

    schreiben(
        DOCS / "measurements" / "reading-list-to-bibliography", VORLAGE_M,
        messseite(d),
        "https://provinglab.dev/measurements/reading-list-to-bibliography/",
        "Twenty links, ten citations: what a machine finishes and what it hands back",
        ("Turning a reading list into a bibliography, measured: 10 of 20 sources became "
         "complete records with RIS and BibTeX in 8 seconds. Only one of the other ten was "
         "stopped by a bot defence — five pages answered in full and declared no citation data."),
        ("A reading list of 20 mixed sources through a citation endpoint. Journal publishers "
         "yield records whether paywalled or open; statistics portals, chambers of commerce and "
         "newspapers yield none — not because they defend themselves, but because they declare "
         "nothing to cite. With the trap: a record can carry a title and still be incomplete."),
        "../../", "TechArticle",
        f"Measured on {DATUM_LANG}, one pass, from a Cloudflare Workers edge. Every "
        "handed-back source was fetched twice, once as a reader and once as a browser, "
        "to separate a page's wall from a reader's limit.")

    schreiben(
        DOCS / "notes" / "sources-a-machine-cannot-cite", VORLAGE_N,
        notizseite(d),
        "https://provinglab.dev/notes/sources-a-machine-cannot-cite/",
        "The sources a machine cannot cite for you — and how to cite them anyway",
        ("Ten of twenty sources came back uncited. Three different causes, three different "
         "responses — and only one is solved by opening the page in a browser. How to tell "
         "them apart, and how to cite a web source that declares nothing about itself."),
        ("When a citation tool hands a source back, the cause is one of three: a bot defence, "
         "a refusal aimed at the network, or a page with no citation data at all. Each needs "
         "different work. Two requests tell them apart."),
        "../../", "Article",
        f"Follows the twenty-source measurement of {DATUM_LANG}.",
        offenlegung=(' <br><br>\n      Disclosure: the author develops Full Page PDF Snap, '
                     'the capture extension linked above. It is one way to do the step it is '
                     'named for and not the only one — the browser\'s own print-to-PDF is '
                     'compared against it in a '
                     '<a href="/measurements/print-to-pdf-vs-screenshot/">published '
                     'measurement</a>, including the cases where print wins.'))


if __name__ == "__main__":
    main()
