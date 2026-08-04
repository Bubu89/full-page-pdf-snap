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
DATUM_DE = "3. August 2026"
ROHDATEN = "/data/2026-08-03-reading-list-to-bibliography.json"

TITEL_M_DE = ("Zwanzig Links, zehn Nachweise: was eine Maschine erledigt "
              "und was sie zurückgibt")

# Deutsche Fassung auf derselben Adresse, Umschaltung per #b-de — das Muster
# dafuer ist measurements/web-citations-that-vanish. Sprachbloecke tragen
# data-lang, build-de-index.py findet die Seite am Anker id="b-de".
SPRACHE_CSS = """
  /* --- Sprachumschaltung --- */
  [data-lang]{display:none}
  [data-lang].on{display:block}
  li[data-lang].on{display:list-item}
  span[data-lang].on,a[data-lang].on{display:inline}
  .lang{display:flex;gap:6px;margin:0 0 26px}
  .lang button{font:inherit;font-size:.86rem;font-weight:600;padding:7px 18px;cursor:pointer;
    background:var(--card);color:var(--dim);border:1px solid var(--line);border-radius:8px}
  .lang button[aria-pressed="true"]{background:var(--acc);color:#fff;border-color:var(--acc)}
"""

SPRACHE_SKRIPT = """<script>
function setLang(l){
  document.querySelectorAll('[data-lang]').forEach(function(e){
    e.classList.toggle('on', e.dataset.lang === l);
  });
  document.getElementById('b-en').setAttribute('aria-pressed', l === 'en');
  document.getElementById('b-de').setAttribute('aria-pressed', l === 'de');
  document.documentElement.lang = l;
  try { localStorage.setItem('pl-lang', l); } catch (e) {}
}
(function(){
  var gespeichert = null;
  try { gespeichert = localStorage.getItem('pl-lang'); } catch (e) {}
  var l = gespeichert || ((navigator.language || 'en').slice(0,2) === 'de' ? 'de' : 'en');
  if (l === 'de') setLang('de');
})();
</script>"""


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


def anpassen(kopf, url, titel, beschreibung, og_beschreibung, tiefe, art,
             deutsch=False):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{titel} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + beschreibung
               + (" Mit deutscher Fassung." if deutsch else "") + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{url}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{titel}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + og_beschreibung + m.group(2), k)
    k = re.sub(r'(<link rel="icon" href=")[^"]*(")', rf"\g<1>{tiefe}icon-128.png\g<2>", k)
    if deutsch:
        # hreflang in beide Richtungen: deutsch und englisch teilen sich eine
        # Adresse, also zeigen alle drei Angaben auf dieselbe. Steht in der
        # Vorlage schon, ist der Ersatz oben ausreichend gewesen.
        if 'hreflang="de"' not in k:
            k = k.replace(
                f'<link rel="canonical" href="{url}">',
                f'<link rel="canonical" href="{url}">\n'
                f'<link rel="alternate" hreflang="en" href="{url}">\n'
                f'<link rel="alternate" hreflang="de" href="{url}">\n'
                f'<link rel="alternate" hreflang="x-default" href="{url}">')
        if '--- Sprachumschaltung ---' not in k:
            k = k.replace("</style>", SPRACHE_CSS + "</style>")
    else:
        # Die Vorlage traegt eine deutsche Fassung im selben Dokument und
        # verweist mit #b-de darauf. Seiten ohne diesen Abschnitt haetten
        # damit einen toten Anker in der Navigation — auf die Sammelseite
        # umbiegen.
        k = k.replace('href="#b-de"', f'href="{tiefe}deutsch/"')
    ld = {
        "@context": "https://schema.org", "@type": art,
        "headline": titel, "description": beschreibung,
        "datePublished": DATUM, "dateModified": DATUM,
        "inLanguage": ["en", "de"] if deutsch else "en", "url": url,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "isAccessibleForFree": True,
        "license": "https://creativecommons.org/licenses/by/4.0/",
    }
    if deutsch:
        ld["about"] = ["citation", "bibliography", "reading list",
                       "Literaturverzeichnis", "Quellennachweis", "Zitieren"]
        ld["keywords"] = ("reading list, citation endpoint, MCP, "
                          "Literaturverzeichnis erstellen, Internetquellen "
                          "zitieren, Abrufdatum, RIS, BibTeX, Citavi, Zotero")
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
    # Folgemessungen desselben Laufs: zweites Netz (VPN) und verbesserter
    # Endpunkt (Kennungs-Ableitung). Die Vergleichstabelle unten liest ihre
    # Zahlen aus den Datensaetzen, statt sie zu wiederholen.
    vpn = json.loads((DOCS / "data" / "2026-08-03-reading-list-to-bibliography-vpn-ausgang.json")
                     .read_text(encoding="utf-8"))["results"]
    abl = json.loads((DOCS / "data" / "2026-08-04-reading-list-to-bibliography-nach-ableitung.json")
                     .read_text(encoding="utf-8"))["results"]
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

    # Dieselben Zeilen fuer die deutsche Fassung: Kategorien und Begruendungen
    # uebersetzt, die Zahlen kommen aus demselben Datensatz.
    arten_de = {"publisher": "Verlag", "open access": "Open Access",
                "repository": "Repositorium", "preprint": "Preprint",
                "official": "amtliche Stelle", "grey lit": "graue Literatur",
                "reference": "Nachschlagewerk", "bare doi": "nackter DOI",
                "news": "Presse"}
    tab_art_de = "\n".join(
        f'    <tr><td>{arten_de.get(k, k)}</td><td>{v["complete"]} von {v["total"]}</td></tr>'
        for k, v in sorted(art.items(), key=lambda x: -x[1]["complete"] / x[1]["total"]))
    t_wand_de = zeilen(wand, lambda e: "beantwortet einen Browser, verweigert dem Leser")
    t_tot_de = zeilen(tot, lambda e: f'verweigert beiden — HTTP {e["as_browser"]["status"]} '
                                     f'von einer Rechenzentrums-Adresse')
    t_stumm_de = zeilen(stumm, lambda e: "antwortet vollständig, weist keine Zitationsdaten aus")

    return f"""
<header>
  <h1 data-lang="en" class="on" lang="en">Twenty links, ten citations: what a machine finishes and what it hands back</h1>
  <h1 data-lang="de" lang="de">{TITEL_M_DE}</h1>
  <p class="standfirst on" data-lang="en" lang="en">
    A reading list of twenty sources through a citation endpoint. Ten came back
    as complete records with RIS and BibTeX, in eight seconds. The interesting
    half is the other ten — because only one of them was stopped by a bot
    defence. Five answered every request in full and simply had no citation data
    to declare.
  </p>
  <p class="standfirst" data-lang="de" lang="de">
    Eine Leseliste aus zwanzig Quellen durch einen Zitations-Endpunkt. Zehn
    kamen als vollständige Nachweise mit RIS und BibTeX zurück, in acht
    Sekunden. Die interessante Hälfte sind die anderen zehn — denn nur eine
    davon wurde von einer Bot-Abwehr gestoppt. Fünf beantworteten jede Anfrage
    vollständig und hatten schlicht keine Zitationsdaten auszuweisen.
  </p>
  <p class="meta"><span data-lang="en" class="on" lang="en">{DATUM_LANG} · {r['sources']} sources, one pass ·
    <a href="{ROHDATEN}">raw data</a></span><span data-lang="de" lang="de">{DATUM_DE} · {r['sources']} Quellen, ein Durchlauf ·
    <a href="{ROHDATEN}">Rohdaten</a></span></p>
</header>

<div class="lang">
  <button id="b-en" aria-pressed="true" onclick="setLang('en')">English</button>
  <button id="b-de" aria-pressed="false" onclick="setLang('de')">Deutsch</button>
</div>

<div data-lang="en" class="on" lang="en">

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

<h2>Follow-up measurement: the endpoint changed, the pages did not</h2>
<p>
  Both runs above measured the same endpoint from two networks. A third run on
  4 August 2026 measured the same twenty addresses against an improved
  endpoint, and the split moved again:
</p>
<table>
  <thead><tr><th scope="col"></th><th scope="col">3 Aug, data centre</th><th scope="col">3 Aug, VPN exit</th><th scope="col">4 Aug, after identifier derivation</th></tr></thead>
  <tbody>
    <tr><td>Complete records</td><td>{r['complete_records']}</td><td>{vpn['complete_records']}</td><td><strong>{abl['complete_records']}</strong></td></tr>
    <tr><td>Seconds per source</td><td>{r['seconds_per_source']}</td><td>{vpn['seconds_per_source']}</td><td>{abl['seconds_per_source']}</td></tr>
  </tbody>
</table>
<p>
  <strong>The gain came from the endpoint, not from the pages.</strong> An SSRN
  address carries its abstract ID and an OECD address its publication slug —
  both resolve to a DOI, and the registration agency (Crossref) returns the
  authoritative fields. A EUR-Lex address carries its CELEX number, which the
  Publications Office of the EU resolves in Cellar. And the endpoint now reads
  Zenodo's deposit metadata in full. Newly complete: Zenodo, SSRN, EUR-Lex and
  the OECD.
</p>
<p>
  The limit is equally clear. ScienceDirect and MDPI remain walls without a
  derivable identifier; SSOAR's bot defence covers its API as well; and the
  three remaining pages — statistik.at, wko.at, derstandard.at — still declare
  nothing. There the extension's browser path remains the honest way: open the
  page yourself and cite what you saw.
</p>
<p>
  Raw data: <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">third
  run</a>, retrieved 4 August 2026.
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

</div>

<div data-lang="de" lang="de">

<h2>Die Frage</h2>
<p>
  Ein Literaturverzeichnis ist die Stelle einer Arbeit, an der eine Maschine
  am nützlichsten wirkt und am schwersten zu kontrollieren ist. Gibt man einem
  Assistenten zwanzig Adressen und bittet um ein Literaturverzeichnis, kommt
  zu allen zwanzig etwas Plausibles zurück. Die Messfrage ist nicht, wie viele
  Einträge erscheinen. Sie lautet: Wie viele davon sind <em>Nachweise</em> —
  gelesen aus dem, was die Seite über sich selbst ausweist —, und wird der
  Rest als Lücke benannt oder still aufgefüllt?
</p>
<p>
  Jede Quelle ging genau einmal an <code>extract_citation</code> am
  <a href="/notes/mcp-server-what-it-solves/">MCP-Endpunkt</a> dieser Seite,
  der die Zitationsmetadaten liest, die eine Seite über sich selbst
  veröffentlicht, und einen strukturierten Nachweis zurückgibt. Nichts wurde
  wiederholt, nichts danach ausgewählt, ob es funktioniert. Jede Adresse wurde
  vor dem Lauf in einem Browser geprüft, damit ein eigener Tippfehler nicht
  als Versagen der Gegenseite gezählt wird.
</p>

<div class="kf-row">
  <div class="kf b"><div class="n">{r['complete_records']}/{r['sources']}</div><div class="l">vollständige Nachweise</div></div>
  <div class="kf"><div class="n">{r['handed_back_behind_a_wall']}</div><div class="l">von einer Bot-Abwehr gestoppt</div></div>
  <div class="kf"><div class="n">{r['handed_back_thin_page']}</div><div class="l">keine Zitationsdaten auf der Seite</div></div>
  <div class="kf"><div class="n">{r['seconds_per_source']} s</div><div class="l">pro Quelle</div></div>
</div>

<h2>Wo die Trennlinie verläuft</h2>
<p>
  Nicht zwischen Fachgebieten, und nicht zwischen kostenpflichtig und frei.
  Sie verläuft zwischen Seiten, die gebaut sind, um zitiert zu werden, und
  Seiten, die gebaut sind, um gelesen zu werden.
</p>
<table>
  <thead><tr><th scope="col">Art der Quelle</th><th scope="col">Vollständige Nachweise</th></tr></thead>
  <tbody>
{tab_art_de}
  </tbody>
</table>
<p>
  Verlage von Fachzeitschriften sind der einfachste Fall, gleich ob der
  Artikel hinter einer Bezahlschranke liegt oder offen steht:
  {nach_art('publisher')} und {nach_art('open access')}. Eine
  Zeitschriftenseite trägt <code>citation_author</code>,
  <code>citation_title</code> und einen DOI im Kopf, weil sie indexiert werden
  will. Ein Enzyklopädie-Eintrag und ein nackter DOI lösen genauso sauber auf.
</p>
<p>
  Amtliche Statistik, Wirtschaftskammern und Zeitungen sind der harte Fall:
  Keine der vier brachte einen Nachweis hervor. Nicht weil sie sich wehren —
  sie beantworteten jede Anfrage vollständig —, sondern weil eine
  Statistikportal-Seite ein Themenüberblick ist und kein Werk: Sie weist
  weder Autor noch Datum noch einen Titel aus, wie ihn ein
  Literaturverzeichnis braucht.
</p>

<h2>Die zehn, die zurückkamen, nach Ursache sortiert</h2>
<p>
  Die Unterscheidung zählt, weil jede Ursache eine andere Reaktion der
  schreibenden Person verlangt. Alles unter „blockiert" zusammenzufassen ist
  genau das, was ein Zitationswerkzeug unzuverlässig wirken lässt, während es
  in Wahrheit genau ist.
</p>

<h3>Eine wurde von einer Bot-Abwehr gestoppt</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Art</th><th scope="col">Was geschah</th></tr></thead>
  <tbody>
{t_wand_de}
  </tbody>
</table>
<p>
  Das ist der einzige Fall unter zwanzig, in dem ein Browser etwas sieht, das
  ein serverseitiger Leser nicht sehen darf. Es ist auch der einzige Fall, in
  dem das eigene Öffnen der Seite das Ergebnis ändert — siehe
  <a href="/notes/sources-a-machine-cannot-cite/">was mit den zehn zu tun
  ist</a>.
</p>

<h3>Vier verweigern jeder Anfrage von dieser Adresse</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Art</th><th scope="col">Was geschah</th></tr></thead>
  <tbody>
{t_tot_de}
  </tbody>
</table>
<p>
  Diese antworteten einem Browser-User-Agent genauso bereitwillig mit 403 wie
  einem Leser. Der gemeinsame Faktor ist nicht der Client, sondern das Netz:
  Anfragen aus einem Rechenzentrum werden abgewiesen, was immer sie vorgeben
  zu sein. Von einem Hausanschluss aus öffnen dieselben Seiten normal. Das ist
  es wert, klar benannt zu werden, denn es ist das eine Ergebnis hier, das von
  einem anderen Ort aus gemessen anders aussehen würde.
</p>

<h3>Fünf antworteten vollständig und hatten nichts auszuweisen</h3>
<table>
  <thead><tr><th scope="col">Host</th><th scope="col">Art</th><th scope="col">Was geschah</th></tr></thead>
  <tbody>
{t_stumm_de}
  </tbody>
</table>
<p>
  Fünfzig bis neunzig Kilobyte einwandfrei lesbares HTML, keinerlei Abwehr,
  und keine <code>citation_*</code>-Metadaten, kein Autor, kein
  Veröffentlichungsdatum. Einen Nachweis dafür muss ein Mensch schreiben, der
  entscheidet, was das Werk <em>ist</em> — eine Seite eines Statistikportals,
  ein Zeitungsartikel, ein Software-Release in einem Repositorium. Kein noch
  so häufiges Wiederholen ändert das, und jedes Werkzeug, das hier einen
  sauberen Eintrag zurückgibt, hat die fehlende Hälfte erfunden.
</p>

<h2>Ein Nachweis kann einen Titel tragen und trotzdem keiner sein</h2>
<p>
  Zwei der fünf stillen Fälle sind die Falle, für die sich diese Messung
  gelohnt hat. Der Zenodo-Nachweis meldet
  <code>"kjswedberg/kjswedberg.github.io: First Release"</code> mit einem
  Autor; das Statistikportal meldet
  <code>"Forschung, Innovation, Digitalisierung"</code> mit
  <code>STATISTIK AUSTRIA</code> als Autor. Beide sehen wie Ergebnisse aus.
  Beide kommen mit <code>complete: false</code> zurück.
</p>
<p>
  Wer das Titelfeld liest und das Flag überspringt, legt beide als Quellen ab.
  Die Lehre betrifft nicht nur diesen Endpunkt — sie gilt für jeden
  Zitationsdienst: <strong>Lesen Sie das Vollständigkeits-Flag, nicht den
  Titel.</strong> An diesem Endpunkt ist diese Prüfung ein einziges Feld:
</p>
<pre><code>if not record["complete"]:
    hand_back(url, record.get("warning") or "no citation data on the page")</code></pre>
<p>
  Eine Lücke, die wir auf eigener Seite schließen sollten: In diesen fünf
  Fällen ist das <code>warning</code>-Feld leer. <code>complete: false</code>
  ist korrekt und reicht zum Handeln, aber ein Grund wäre nützlicher als
  Schweigen — und das ist
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">als solches
  vermerkt</a>.
</p>

<h2>Gegenmessung: ein zweites Netz, und was es nicht änderte</h2>
<p>
  Der Abschnitt weiter unten sagte voraus, ein Hausanschluss sollte eine
  höhere Abschlussquote liefern. Diese Behauptung wurde inzwischen einmal
  geprüft — von einem kommerziellen VPN-Ausgang statt von einem
  Hausanschluss —, und sie hielt größtenteils nicht stand.
</p>
<table>
  <thead><tr><th scope="col"></th><th scope="col">Rechenzentrum</th><th scope="col">VPN-Ausgang</th></tr></thead>
  <tbody>
    <tr><td>Vollständige Nachweise</td><td>10</td><td><strong>11</strong></td></tr>
    <tr><td>Von einer Bot-Abwehr gestoppt</td><td>1</td><td>1</td></tr>
    <tr><td>Verweigern jedem Client von dieser Adresse</td><td><strong>4</strong></td><td><strong>4</strong></td></tr>
    <tr><td>Antworteten vollständig, wiesen nichts aus</td><td>5</td><td>4</td></tr>
    <tr><td>Sekunden pro Quelle</td><td>0.4</td><td>0.7</td></tr>
  </tbody>
</table>
<p>
  <strong>Die vier Verweigerungen auf Netzebene bewegten sich nicht.</strong>
  ScienceDirect, SSRN, die OECD und EUR-Lex beantworteten die zweite Adresse
  exakt wie die erste. Der wahrscheinliche Grund: Ein kommerzieller
  VPN-Ausgang ist selbst ein Rechenzentrums-Bereich — dieser Lauf tauschte
  also ein Rechenzentrum gegen ein anderes, statt die Behauptung zu prüfen.
  <em>Ob ein privater Anschluss das Ergebnis ändert, bleibt offen</em>; diese
  Messung schließt die Frage nicht.
</p>
<p>
  Die eine Quelle, die sich änderte, ist Zenodo, und nicht wegen des Netzes:
  Sie gab im ersten Lauf <code>authors, doi, title</code> zurück, im zweiten
  <code>authors, doi, publisher, title, year</code>. Der Nachweis gewann ein
  Jahr — und das ist das Feld, das über Vollständigkeit entscheidet. Entweder
  wurde der Datensatz zwischen den Läufen bearbeitet, oder Zenodo liefert
  seine Metadaten uneinheitlich aus; von außen sehen beide gleich aus.
</p>
<p>
  Rohdaten: <a href="/data/2026-08-03-reading-list-to-bibliography-vpn-ausgang.json">zweiter
  Lauf</a>. Wer über einen privaten Anschluss verfügt, ist eingeladen, die
  offene Hälfte zu klären —
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues/3">Issue 3</a>.
</p>

<h2>Folgemessung: Der Endpunkt änderte sich, die Seiten nicht</h2>
<p>
  Beide Läufe oben maßen denselben Endpunkt aus zwei Netzen. Ein dritter Lauf
  am 4. August 2026 maß dieselben zwanzig Adressen gegen einen verbesserten
  Endpunkt — und die Aufteilung wanderte erneut:
</p>
<table>
  <thead><tr><th scope="col"></th><th scope="col">3.8., Rechenzentrum</th><th scope="col">3.8., VPN-Ausgang</th><th scope="col">4.8., nach Kennungs-Ableitung</th></tr></thead>
  <tbody>
    <tr><td>Vollständige Nachweise</td><td>{r['complete_records']}</td><td>{vpn['complete_records']}</td><td><strong>{abl['complete_records']}</strong></td></tr>
    <tr><td>Sekunden pro Quelle</td><td>{r['seconds_per_source']}</td><td>{vpn['seconds_per_source']}</td><td>{abl['seconds_per_source']}</td></tr>
  </tbody>
</table>
<p>
  <strong>Der Zugewinn kam vom Endpunkt, nicht von den Seiten.</strong> Eine
  SSRN-Adresse trägt ihre Abstract-ID, eine OECD-Adresse ihren
  Publikations-Slug — beide lösen zu einem DOI auf, und die
  Registrierungsstelle (Crossref) liefert die autoritativen Angaben. Eine
  EUR-Lex-Adresse trägt ihre CELEX-Nummer, die das Amt für Veröffentlichungen
  der EU in Cellar auflöst. Und der Endpunkt liest die Deposit-Metadaten von
  Zenodo inzwischen vollständig. Neu vollständig: Zenodo, SSRN, EUR-Lex und
  die OECD.
</p>
<p>
  Die Grenze ist ebenso klar. ScienceDirect und MDPI bleiben Wände ohne
  ableitbare Kennung; SSOARs Bot-Abwehr deckt auch die API ab; und die drei
  übrigen Seiten — statistik.at, wko.at, derstandard.at — deklarieren weiterhin
  nichts. Dort bleibt der Browser-Weg der Erweiterung der ehrliche Weg: die
  Seite selbst öffnen und das zitieren, was man gesehen hat.
</p>
<p>
  Rohdaten: <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">dritter
  Lauf</a>, abgerufen am 4. August 2026.
</p>

<h2>Was hier nicht geklärt ist</h2>
<ul>
  <li><strong>Zwanzig Quellen sind eine Form, keine Studie.</strong> Für die
    Abdeckung gegenüber einem etablierten Dienst an zufällig gezogenen
    Stichproben ist der
    <a href="/measurements/citation-extraction/">Citoid-Vergleich</a> die zu
    zitierende Messung. Diese hier zeigt, wie sich die Arbeit aufteilt.</li>
  <li><strong>Die Adresse, von der aus gemessen wird, verändert das Ergebnis
    — weniger als erwartet.</strong> Ein zweiter Lauf von einer anderen
    Adresse ließ alle vier Verweigerungen auf Netzebene bestehen. Ein privater
    Anschluss könnte immer noch etwas ändern, aber das ist nun eine offene
    Frage statt einer Annahme — wer es prüft, möge es gern sagen; die
    <a href="{ROHDATEN}">Daten</a> und das
    <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/messung-literaturverzeichnis.py">Skript</a>
    sind beide veröffentlicht.</li>
  <li><strong>Die Aufteilung wandert.</strong> Verlage ziehen ihre Abwehr
    enger, und Seiten werden neu gebaut. Eine Zahl hier ist ein Nachmittag,
    keine Konstante.</li>
  <li><strong>Der eigene Export eines Verlags schlägt all das.</strong> Wo
    eine Seite RIS oder BibTeX zum Herunterladen anbietet, ist diese Datei
    maßgeblich und dies hier nicht.</li>
</ul>

<h2>Selbst ausführen</h2>
<p>
  Eine URL pro Zeile hinein, eine importierbare <code>.ris</code> heraus — mit
  den Verweigerungen auf stderr benannt statt halb importiert. Die
  <a href="/recipes/">Rezepte-Seite</a> bietet dasselbe für Claude Code,
  Claude Desktop, Python und den Browser.
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
  Dann <em>Zotero → Datei → Importieren</em> oder <em>Citavi → Import →
  RIS</em>. Kein Schlüssel, kein Konto. Ein Hinweis lohnt sich noch: Diese
  Seite sitzt hinter einem Filter, der den User-Agent ablehnt, den Pythons
  <code>urllib</code> standardmäßig sendet. Setzen Sie einen beliebigen
  eigenen User-Agent, und sie antwortet normal.
</p>

</div>
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
              offenlegung="", deutsch=False):
    kopf, fuss = kopf_und_fuss(vorlage)
    ziel.mkdir(parents=True, exist_ok=True)
    seite = (anpassen(kopf, url, titel, besch, og, tiefe, art, deutsch)
             + inhalt + fuss_setzen(fuss, fusssatz, tiefe, offenlegung))
    # Das Umschalt-Skript gehoert nur auf Seiten mit deutschem Abschnitt. Es
    # kann aus einer zweisprachigen Vorlage mitkommen oder fehlen — beides
    # ausgleichen, sonst setzt es auf einer rein englischen Seite bei
    # deutschen Besuchern die Dokumentsprache auf de.
    if deutsch and "function setLang" not in seite:
        seite = seite.replace("</body>", SPRACHE_SKRIPT + "\n</body>")
    if not deutsch and "function setLang" in seite:
        seite = seite.replace(SPRACHE_SKRIPT + "\n</body>", "</body>")
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
        "to separate a page's wall from a reader's limit.",
        deutsch=True)

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
