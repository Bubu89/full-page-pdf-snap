#!/usr/bin/env python3
"""Erzeugt den Beitrag ueber die Messung deutschsprachiger Wissenschaftsplattformen.

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und gemeinsame Meta-Angaben nicht auseinanderlaufen. Muster und
Sprachschalter wie build-platform-post.py.

Die Seite stellt die Fehlschlaege an den Anfang: Fuer die Zielgruppe ist der
siebenmalige Grund der Zurueckgabe die verwertbare Auskunft, nicht die
viermalige Vollstaendigkeit. Drei Gruende werden unterschieden — Sperre,
fehlende Deklaration, Unerreichbarkeit — weil jeder eine andere Antwort
verlangt.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "measurements" / "de-plattformen"
DATEN = DOCS / "data" / "2026-08-03-de-plattformen.json"

URL = "https://provinglab.dev/measurements/de-plattformen/"
TITEL = "German-language scholarly platforms measured: four read, seven handed back"
TITEL_DE = "Deutschsprachige Wissenschaftsplattformen gemessen: vier gelesen, sieben zurückgegeben"
BESCHREIBUNG = (
    "Eleven platforms a student at a German-speaking university actually cites — "
    "repositories, the National Library, German publishers, case law, official "
    "statistics. Four return a complete record; for the other seven this page "
    "names the reason: wall, missing declaration, or unreachable."
)

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


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    return s[:s.index('<div class="wrap">')], s[s.index("<footer"):]


def anpassen(kopf):
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + " Deutsche Fassung auf derselben Seite." + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{TITEL}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    # hreflang in beide Richtungen: deutsch und englisch teilen sich eine
    # Adresse, also zeigen alle drei Angaben auf dieselbe.
    k = k.replace(
        f'<link rel="canonical" href="{URL}">',
        f'<link rel="canonical" href="{URL}">\n'
        f'<link rel="alternate" hreflang="en" href="{URL}">\n'
        f'<link rel="alternate" hreflang="de" href="{URL}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{URL}">')
    k = k.replace("</style>", SPRACHE_CSS + "</style>")
    k = k.replace(
        '<a class="n" href="../../deutsch/" hreflang="de" lang="de" '
        'title="Deutschsprachige Fassungen">Deutsch</a>',
        '<a class="n" href="#b-de" hreflang="de" lang="de" '
        'title="Zur deutschen Fassung auf dieser Seite">Deutsch</a>')
    ld = {"@context": "https://schema.org", "@type": "TechArticle",
          "headline": TITEL, "description": BESCHREIBUNG,
          "datePublished": "2026-08-03", "dateModified": "2026-08-03",
          "inLanguage": ["en", "de"], "url": URL,
          "about": ["citation metadata", "German scholarly platforms",
                    "Zitationsdaten", "Repositorien", "Literaturverzeichnis"],
          "keywords": ("Zitationsdaten, Literaturverzeichnis erstellen, "
                       "Internetquellen zitieren, Abrufdatum, SSOAR, OPUS, "
                       "Deutsche Nationalbibliothek, citation data, repositories"),
          "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
          "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"}}
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    return re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)


# Die Begruendung einer Zurueckgabe wird aus den Rohdaten abgeleitet, nicht
# formuliert: Statuspaar und Warnung des Endpunkts tragen den Befund schon.
def befund(e):
    """(Schluessel, en, de) — Sperre, Interstitial, duenne oder unvollstaendige Seite."""
    r, b = e.get("as_reader", {}), e.get("as_browser", {})
    w = (e.get("warning") or "").lower()
    if b.get("status") == 200 and r.get("status") != 200:
        return ("wall",
                f"A wall: a browser is answered with 200, the reader is refused "
                f"({r.get('status')}). The address exists — not for a machine.",
                f"Eine Sperre: Der Browser bekommt 200, der Leser wird abgewiesen "
                f"({r.get('status')}). Die Adresse existiert — nicht für eine Maschine.")
    if "access wall" in w:
        return ("wall-page",
                "Both are answered with 200, but what the reader receives is an "
                "access wall, not the record.",
                "Beide bekommen 200, aber was der Leser erhält, ist eine "
                "Zugangsschranke, nicht der Datensatz.")
    if "interstitial" in w or "block page" in w:
        return ("interstitial",
                "Both receive the same stub of a page — a login screen of a "
                "licensed database, with no citation metadata in it.",
                "Beide erhalten denselben Seitenstummel — den Anmeldeschirm "
                "einer lizenzierten Datenbank, ohne Zitationsdaten.")
    if "only title" in w:
        return ("thin-title",
                "No wall: the page answers in full, but declares only a record "
                "number as its title. Nothing identifies the work.",
                "Keine Sperre: Die Seite antwortet vollständig, weist aber nur "
                "eine Aktennummer als Titel aus. Nichts benennt das Werk.")
    if "no complete citation" in w:
        return ("incomplete",
                "The page answers in full, but declares no year — an incomplete "
                "citation, flagged instead of guessed.",
                "Die Seite antwortet vollständig, weist aber kein Jahr aus — "
                "eine unvollständige Angabe, markiert statt erraten.")
    return ("other", e.get("warning") or "no result", e.get("warning") or "kein Ergebnis")


def tabelle_fehler(fehler, lang):
    zeilen = []
    for e in fehler:
        schl, en, de = befund(e)
        r = e.get("as_reader", {}).get("status", "—")
        b = e.get("as_browser", {}).get("status", "—")
        grund = en if lang == "en" else de
        zeilen.append(
            f'    <tr><td>{e["platform"]}</td><td class="num">{r}</td>'
            f'<td class="num">{b}</td><td>{grund}</td>'
            f'<td class="num">{e["seconds"]}</td></tr>')
    return "\n".join(zeilen)


def tabelle_ok(ganz, lang):
    zeilen = []
    for e in ganz:
        f = e["fields"]
        autoren = "✓" if "authors" in f else "—"
        jahr = "✓" if "year" in f else "—"
        doi = "✓" if "doi" in f else "—"
        art_en = {"repository": "repository", "publisher": "publisher"}.get(e["kind"], e["kind"])
        art_de = {"repository": "Repositorium", "publisher": "Verlag"}.get(e["kind"], e["kind"])
        zeilen.append(
            f'    <tr><td>{e["platform"]}</td><td>{art_en if lang == "en" else art_de}</td>'
            f'<td class="num">{autoren}</td><td class="num">{jahr}</td>'
            f'<td class="num">{doi}</td><td class="num">{"✓" if e["has_ris"] else "—"}</td>'
            f'<td class="num">{e["seconds"]}</td></tr>')
    return "\n".join(zeilen)


def inhalt(d):
    r = d["results"]
    fehler = [e for e in d["per_source"] if not e["complete"]]
    ganz = [e for e in d["per_source"] if e["complete"]]
    n = r["sources"]
    return f"""<div class="wrap">

<header>
  <h1 data-lang="en" class="on" lang="en">{TITEL}</h1>
  <h1 data-lang="de" lang="de">{TITEL_DE}</h1>
  <p class="standfirst on" data-lang="en" lang="en">
    A term paper at a German-speaking university cites SSOAR, the National
    Library, Nomos and Destatis — not PubMed. Eleven such platforms went
    through the citation endpoint on 3 August 2026. Four returned a complete
    record. The more useful half of this page is the seven that did not, and
    the reason for each.
  </p>
  <p class="standfirst" data-lang="de" lang="de">
    Eine Arbeit an einer deutschsprachigen Hochschule zitiert SSOAR, die
    Nationalbibliothek, Nomos und Destatis — nicht PubMed. Elf solcher
    Plattformen gingen am 3. August 2026 durch den Zitations-Endpunkt. Vier
    lieferten einen vollständigen Nachweis. Die verwertbarere Hälfte dieser
    Seite sind die sieben, die es nicht taten — und der jeweilige Grund.
  </p>
  <p class="meta"><span data-lang="en" class="on" lang="en">3 August 2026 · {n} platforms, one pass ·
    <a href="/data/2026-08-03-de-plattformen.json">raw data</a></span><span data-lang="de" lang="de">3. August 2026 · {n} Plattformen, ein Durchlauf ·
    <a href="/data/2026-08-03-de-plattformen.json">Rohdaten</a></span></p>
</header>

<div class="lang">
  <button id="b-en" aria-pressed="true" onclick="setLang('en')">English</button>
  <button id="b-de" aria-pressed="false" onclick="setLang('de')">Deutsch</button>
</div>

<div data-lang="en" class="on" lang="en">

<div class="kf-row">
  <div class="kf b"><div class="n">{r["complete_records"]}/{n}</div><div class="l">complete records</div></div>
  <div class="kf"><div class="n">{r["handed_back_behind_a_wall"]}</div><div class="l">behind a measured wall</div></div>
  <div class="kf"><div class="n">{r["handed_back_page_unreachable"]}</div><div class="l">unreachable for a browser</div></div>
  <div class="kf"><div class="n">{r["seconds_per_source"]}&nbsp;s</div><div class="l">per source</div></div>
</div>

<h2>Where it fails — and why</h2>
<p>
  The failures come first, because they are the usable answer. Each handed-back
  address was fetched twice, once with the reader's own user agent, once with a
  browser's. A wall counts only where the browser is answered and the reader is
  not; everything else is a page that answers but declares too little. None of
  the eleven was unreachable for a browser.
</p>
<table>
  <thead><tr><th scope="col">Platform</th><th scope="col">Reader</th><th scope="col">Browser</th><th scope="col">Finding</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle_fehler(fehler, "en")}
  </tbody>
</table>
<p>
  SSOAR is the control: its refusal of server-side readers was already measured
  in the <a href="/measurements/reading-list-to-bibliography/">reading-list
  run</a>. This time both fetches were answered with 200 — but the reader's
  copy is an access wall, not the record. A run in which SSOAR yields a clean
  citation would be the suspicious result, not this one.
</p>

<h2>What it reads</h2>
<table>
  <thead><tr><th scope="col">Platform</th><th scope="col">Kind</th><th scope="col">Authors</th><th scope="col">Year</th><th scope="col">DOI</th><th scope="col">RIS</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle_ok(ganz, "en")}
  </tbody>
</table>
<p>
  Both German-language publisher platforms and both disciplinary repositories
  of the Leibniz institutes (ZPID, DIPF) declare enough for a complete record,
  including a RIS entry that imports into Citavi, Zotero or EndNote.
</p>

<h2>Method</h2>
<ul>
  <li>The eleven addresses were fixed on 3 August 2026 before the run, and each
    answered 200 to a browser in a pre-check the same day — two first guesses
    (a catalogue number, a DOI) returned 404 and were replaced with verified
    records before measuring, so no typo masquerades as a platform's fault.</li>
  <li>Every address went to the endpoint
    (<code>https://provinglab.dev/mcp</code>, tool <code>extract_citation</code>),
    which fetches from Cloudflare's edge.</li>
  <li>The measuring client ran from a commercial VPN exit on the local network
    (AS209854 Cyberzone S.A., Frankfurt DE) — not a plain residential line.
    Some platforms answer such ranges differently than a home connection.</li>
  <li>Raw data, per source and with both status codes:
    <a href="/data/2026-08-03-de-plattformen.json">JSON</a>, CC BY 4.0.</li>
</ul>

<h2>What this means for a bibliography in German</h2>
<p>
  Publisher platforms and the Leibniz repositories can go through the endpoint.
  The National Library's catalogue, OPUS front doors and licensed databases
  cannot — there the page has to be opened in a browser and kept from inside
  the session, which is what the
  <a href="/tools/full-page-pdf-snap/">capture extension</a> is for. Statistics
  portals answer in full but declare too little for a citation; the endpoint
  says so instead of inventing the missing year. The two routes are
  complements, not competitors.
</p>

<h2>Limits of this measurement</h2>
<ul>
  <li>Eleven platforms with one example record each, one pass on one day — a
    survey of what a German-language bibliography touches, not a census.</li>
  <li>“Wall” here means: two fetches on one afternoon, one answered, one not.
    It is an observation, not a statement about any operator's motives.</li>
  <li>Whether a page declares enough metadata can differ between records on the
    same platform; the example records were chosen before the run, not after.</li>
</ul>

</div>

<div data-lang="de" lang="de">

<div class="kf-row">
  <div class="kf b"><div class="n">{r["complete_records"]}/{n}</div><div class="l">vollständige Nachweise</div></div>
  <div class="kf"><div class="n">{r["handed_back_behind_a_wall"]}</div><div class="l">hinter gemessener Sperre</div></div>
  <div class="kf"><div class="n">{r["handed_back_page_unreachable"]}</div><div class="l">für Browser unerreichbar</div></div>
  <div class="kf"><div class="n">{str(r["seconds_per_source"]).replace(".", ",")}&nbsp;s</div><div class="l">pro Quelle</div></div>
</div>

<h2>Wo es scheitert — und warum</h2>
<p>
  Die Fehlschläge stehen zuerst, weil sie die verwertbare Auskunft sind. Jede
  zurückgegebene Adresse wurde zweimal abgerufen — einmal mit der Kennung des
  Lesers, einmal mit der eines Browsers. Eine Sperre zählt nur, wo der Browser
  durchkommt und der Leser nicht; alles andere ist eine Seite, die antwortet,
  aber zu wenig ausweist. Keine der elf Adressen war für einen Browser
  unerreichbar.
</p>
<table>
  <thead><tr><th scope="col">Plattform</th><th scope="col">Leser</th><th scope="col">Browser</th><th scope="col">Befund</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle_fehler(fehler, "de")}
  </tbody>
</table>
<p>
  SSOAR ist der Kontrolllauf: Die Abweisung serverseitiger Leser war bereits im
  <a href="/measurements/reading-list-to-bibliography/">Quellenlisten-Lauf</a>
  gemessen. Diesmal wurden beide Abrufe mit 200 beantwortet — aber was der
  Leser erhält, ist eine Zugangsschranke, nicht der Datensatz. Ein Lauf, in dem
  SSOAR einen sauberen Nachweis liefert, wäre das verdächtige Ergebnis, nicht
  dieses.
</p>

<h2>Was gelesen wird</h2>
<table>
  <thead><tr><th scope="col">Plattform</th><th scope="col">Art</th><th scope="col">Autoren</th><th scope="col">Jahr</th><th scope="col">DOI</th><th scope="col">RIS</th><th scope="col">s</th></tr></thead>
  <tbody>
{tabelle_ok(ganz, "de")}
  </tbody>
</table>
<p>
  Beide deutschsprachigen Verlagsplattformen und beide fachlichen Repositorien
  der Leibniz-Institute (ZPID, DIPF) weisen genug für einen vollständigen
  Nachweis aus — inklusive RIS-Eintrag, der sich ohne Abtippen in Citavi,
  Zotero oder EndNote importieren lässt.
</p>

<h2>Methode</h2>
<ul>
  <li>Die elf Adressen wurden am 3. August 2026 vor dem Lauf festgelegt, und
    jede antwortete einem Browser am selben Tag mit 200 — zwei zuerst gewählte
    Adressen (eine Katalognummer, ein DOI) lieferten in dieser Vorab-Prüfung
    404 und wurden vor der Messung durch geprüfte Datensätze ersetzt, damit
    kein Tippfehler als Fehler einer Plattform erscheint.</li>
  <li>Jede Adresse ging an den Endpunkt
    (<code>https://provinglab.dev/mcp</code>, Werkzeug
    <code>extract_citation</code>), der von Cloudflares Randnetz abruft.</li>
  <li>Der messende Client lief über den kommerziellen VPN-Ausgang des lokalen
    Netzes (AS209854 Cyberzone S.A., Frankfurt am Main) — keine gewöhnliche
    Haushaltsleitung. Manche Plattformen antworten solchen Adressbereichen
    anders als einem Heimanschluss.</li>
  <li>Rohdaten, pro Quelle und mit beiden Statuscodes:
    <a href="/data/2026-08-03-de-plattformen.json">JSON</a>, CC BY 4.0.</li>
</ul>

<h2>Was das für ein deutsches Literaturverzeichnis bedeutet</h2>
<p>
  Verlagsplattformen und die Leibniz-Repositorien können über den Endpunkt
  laufen. Der Katalog der Nationalbibliothek, OPUS-Einstiegsseiten und
  lizenzierte Datenbanken können es nicht — dort muss die Seite im Browser
  geöffnet und aus der eigenen Sitzung heraus gesichert werden, wofür die
  <a href="/tools/full-page-pdf-snap/">Aufnahme-Erweiterung</a> gebaut ist.
  Statistikportale antworten vollständig, weisen aber zu wenig für einen
  Nachweis aus; der Endpunkt sagt das, statt das fehlende Jahr zu erfinden.
  Die beiden Wege ergänzen sich, sie konkurrieren nicht.
</p>

<h2>Grenzen dieser Messung</h2>
<ul>
  <li>Elf Plattformen mit je einem Beispieldatensatz, ein Durchlauf an einem
    Tag — eine Aufnahme dessen, was ein deutsches Literaturverzeichnis berührt,
    keine Vollerhebung.</li>
  <li>„Sperre" heißt hier: zwei Abrufe an einem Nachmittag, einer beantwortet,
    einer nicht. Das ist eine Beobachtung, keine Aussage über die Absichten
    eines Betreibers.</li>
  <li>Ob eine Seite genug Metadaten ausweist, kann zwischen Datensätzen
    derselben Plattform variieren; die Beispiele wurden vor dem Lauf gewählt,
    nicht danach.</li>
</ul>

</div>

"""


def main():
    d = json.loads(DATEN.read_text(encoding="utf-8"))
    kopf, fuss = kopf_und_fuss()
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Measured on 3 August 2026 in one pass against https://provinglab.dev/mcp.\n'
        '      Every handed-back source was fetched twice — as reader and as browser. Raw data:\n'
        '      <a href="/data/2026-08-03-de-plattformen.json">JSON</a>, CC BY 4.0.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a> · '
        '<a href="../../disclaimer/">Disclaimer</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    fuss = fuss.replace("</body>", SPRACHE_SKRIPT + "\n</body>")
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(anpassen(kopf) + inhalt(d) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)}")


if __name__ == "__main__":
    main()
