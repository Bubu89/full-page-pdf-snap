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
    # Die Vorlage traegt eine deutsche Fassung im selben Dokument und verweist
    # mit #b-de darauf. Seiten ohne diesen Abschnitt haetten damit einen toten
    # Anker in der Navigation — auf die Sammelseite umbiegen.
    k = k.replace('href="#b-de"', f'href="{tiefe}deutsch/"')
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
  <thead><tr><th scope="col"></th><th scope="col">Browser print</th><th scope="col">Full-page capture</th></tr></thead>
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

FAQ_DE = [
    ("Wie speichere ich eine ganze Webseite als PDF ohne Seitenumbrueche?",
     "Mit einer Aufnahme-Erweiterung statt ueber den Druckdialog. Der Druckexport des "
     "Browsers teilt in Seiten auf: derselbe Artikel kam als 26 Seiten heraus, und 9 "
     "Umbrueche schnitten mitten durch einen Satz. Eine Vollseiten-Aufnahme schreibt ein "
     "durchgehendes Blatt. Beide Wege sind gemessen unter "
     "https://provinglab.dev/measurements/print-to-pdf-vs-screenshot/ — einschliesslich der "
     "Faelle, in denen der Druckexport besser ist, weil er markierbaren Text behaelt."),
    ("Kann ich eine Seite hinter einem Login speichern?",
     "Ja, wenn Sie sie im eigenen Browser geoeffnet haben. Die Erweiterung nimmt auf, was "
     "Ihre Sitzung ohnehin zeigt — ein lizenzierter Zeitschriftenartikel oder ein Kursraum "
     "wird so gesichert, wie Sie ihn sehen. Kein serverseitiger Dienst kann das, weil er "
     "Ihre Sitzung nicht hat. Es ist kein Weg zu Inhalten, zu denen Sie keinen Zugang haben."),
    ("Was ist das Abrufdatum und warum steht es in jeder Quellenangabe?",
     "Das Abrufdatum ist der Zeitpunkt, zu dem Sie eine Webquelle gesehen haben. Es steht in "
     "der Angabe, weil eine Webseite sich aendern oder verschwinden kann — und weil es bei "
     "einer Seite ohne Veroeffentlichungsdatum das einzige Datum ist, das die Quellenangabe "
     "tragen kann. Von 150 Quellen aus echten Literaturverzeichnissen waren 19,3 % nicht mehr "
     "erreichbar, 8,7 % nirgends archiviert."),
    ("Wie speichere ich eine Webseite am Handy als PDF?",
     "Unter Android nur mit Firefox: Chrome fuer Android installiert ueberhaupt keine "
     "Erweiterungen. Von 248 geprueften Seiten-Speicher-Erweiterungen geben 60 "
     "Android-Unterstuetzung an."),
    ("Kann ich aus einer Linkliste automatisch ein Literaturverzeichnis erzeugen?",
     "Teilweise — und es lohnt zu wissen, welcher Teil. Von 20 gemischten Quellen wurden 10 "
     "in 8,1 Sekunden zu vollstaendigen Datensaetzen mit RIS und BibTeX, ueber einfaches "
     "HTTP, ohne Konto. Die anderen 10 brauchen einen Menschen: eine wegen einer Bot-Abwehr, "
     "vier wegen einer Sperre gegen das anfragende Netz, und fuenf, weil die Seite ueberhaupt "
     "keine Zitationsangaben deklariert."),
]

ANLEITUNG_DE = f"""
<header>
  <h1>Webseite als PDF speichern — ein Blatt, mit Quelle und Abrufdatum darauf</h1>
  <p class="standfirst">
    Kurz: eine Aufnahme-Erweiterung statt des Druckdialogs. Der Druckexport
    teilt in Seiten auf — derselbe Artikel kam als <strong>26 Seiten heraus, 9
    Umbrueche schnitten mitten durch einen Satz</strong>. Eine Aufnahme schreibt
    ein durchgehendes Blatt und kann Herkunft und Abrufzeit hineinschreiben.
  </p>
  <p class="meta">{DATUM_LANG} · jede Zahl verweist auf die Messung dahinter ·
    <a href="/how-to/save-a-webpage-as-pdf/" hreflang="en">English version</a></p>
</header>

<p>
  <a class="btn" href="{AMO}">Firefox, Rechner und Android</a>
  &nbsp;<a class="btn" href="{CWS}">Chrome 116+, Edge, Brave, Vivaldi</a>
</p>
<p style="font-size:.9rem">
  Kostenlos, MIT-Lizenz, laeuft auf dem Geraet. Edge fragt einmal, ob
  Erweiterungen aus anderen Stores zugelassen werden; Opera braucht zuerst seine
  Erweiterung <em>Install Chrome Extensions</em>. Dann: Seite oeffnen,
  <code>Alt+Umschalt+Y</code> druecken oder auf das Symbol klicken.
</p>

<h2>Drucken oder aufnehmen? Der ehrliche Vergleich</h2>
<table>
  <thead><tr><th scope="col"></th><th scope="col">Druckexport</th><th scope="col">Vollseiten-Aufnahme</th></tr></thead>
  <tbody>
    <tr><td>Derselbe Artikel ergibt</td><td>26 Seiten</td><td><strong>1 Blatt</strong></td></tr>
    <tr><td>Umbrueche mitten im Satz</td><td>9</td><td>0</td></tr>
    <tr><td>Markierbarer, durchsuchbarer Text</td><td><strong>94,8 %</strong></td><td>per Texterkennung: 92,6 %</td></tr>
    <tr><td>Kostet etwas</td><td>nein, eingebaut</td><td>nein</td></tr>
  </tbody>
</table>
<p>
  <strong>Beim Text gewinnt der Druckexport.</strong> Wer nur eine lesbare,
  durchsuchbare Kopie braucht und sich an der Seitenaufteilung nicht stoert,
  kommt mit der Funktion aus, die im Browser schon steckt — das steht hier,
  statt es zu verschweigen. Eine Aufnahme lohnt, wenn das Layout zaehlt, wenn
  ein Umbruch durch eine Tabelle fiele, oder wenn die Quellenangaben mit der
  Datei mitreisen sollen.
  <a href="/measurements/print-to-pdf-vs-screenshot/">Methode und Rohdaten</a>
</p>

<h2>Hinter einem Login oder einer Schranke, zu der Sie Zugang haben</h2>
<p>
  Eine Aufnahme-Erweiterung liest, was Ihre eigene Sitzung ohnehin zeigt: ein
  lizenzierter Zeitschriftenartikel, ein Kursraum, eine Bestellbestaetigung —
  gesichert, wie Sie es sehen. Kein serverseitiger Dienst kann das. Gemessen an
  20 gemischten Quellen wurde ein serverseitiger Leser von 5 davon rundweg
  abgewiesen. Eine Seite zu sichern, die Sie lesen duerfen, ist eine Kopie zum
  eigenen Gebrauch (§ 42 UrhG) — kein Weg zu Inhalten ohne Zugang.
</p>

<h2>Am Handy</h2>
<p>
  Nur Firefox. <strong>Chrome fuer Android installiert ueberhaupt keine
  Erweiterungen</strong>, die Frage stellt sich also nur dort. Von 248 geprueften
  Erweiterungen geben 60 Android-Unterstuetzung an — getestet hatte sie vorher
  keine.
  <a href="/measurements/android-capture-extensions/">Die Android-Messung</a>
</p>

<h2>Warum das Abrufdatum in die Datei gehoert</h2>
<p>
  Eine Adresse im Literaturverzeichnis ist ein Versprechen ueber eine Seite, die
  Ihnen nicht gehoert. Geprueft an 150 Quellen aus echten Verzeichnissen:
  <strong>19,3 % waren verschwunden</strong>, 8,7 % nirgends archiviert, und wo
  eine Sicherung bestand, war sie im Mittel 603 Tage alt. Bei einer Seite ohne
  Veroeffentlichungsdatum ist die Abrufzeit das einzige Datum, das die Angabe
  tragen kann — und es existiert nur in dem Moment, in dem Sie hinsehen.
  <a href="/measurements/web-citations-that-vanish/">Was mit einer Quelle
  geschieht, nachdem man sie zitiert hat</a>
</p>
<p>
  Eine Aufnahme schreibt das hinein: Verfasser, Titel, DOI, Lizenz und die
  genaue Zeit — im PDF und in einem RIS-Satz daneben, den Zotero, Citavi,
  EndNote und Mendeley einlesen.
</p>

<h2>Eine ganze Quellenliste auf einmal</h2>
<p>
  Fuer ein Literaturverzeichnis statt einer einzelnen Seite braucht der groessere
  Teil gar keinen Browser. Von 20 gemischten Quellen wurden
  <strong>10 in 8,1 Sekunden zu vollstaendigen Datensaetzen</strong> mit RIS und
  BibTeX — ohne Konto, ohne Schluessel. Die anderen zehn kommen mit Begruendung
  zurueck, damit Sie wissen, welche Adressen Sie selbst oeffnen muessen.
  <a href="/recipes/">Die Rezepte</a> ·
  <a href="/measurements/reading-list-to-bibliography/">die Messung</a>
</p>

<h2>Was es nicht leistet</h2>
<ul>
  <li>Es erreicht keine Inhalte, zu denen Sie keinen Zugang haben.</li>
  <li>Eine Bildschirmaufnahme ist kein qualifiziertes elektronisches Dokument.
    Sie haelt fest, wie eine Seite zu einem Zeitpunkt aussah — das ist etwas
    anderes, als es zu beweisen.</li>
  <li>Wo ein Verlag einen eigenen <em>Zitieren → RIS</em>-Export anbietet, ist
    diese Datei massgeblich und besser als alles Rekonstruierte.</li>
  <li>Die Hinweise zum Urheberrecht auf dieser Seite sind eine Einordnung, keine
    Rechtsberatung. Im Zweifel und bei einer Auseinandersetzung fragen Sie eine
    Anwaeltin oder einen Anwalt, nicht diese Seite.</li>
</ul>
"""

MITMACHEN = f"""
<header>
  <h1>Rechnen Sie eine Zahl nach. Am liebsten die, die falsch ist.</h1>
  <p class="standfirst">
    Jede Angabe hier hat eine Methode, Rohdaten und einen Kontrolllauf — damit
    sie nachgerechnet werden kann, nicht damit sie geglaubt wird. Der
    nützlichste Beitrag zu diesem Projekt ist deshalb keine neue Messung,
    sondern eine <strong>Gegenmessung, die etwas anderes ergibt</strong>.
  </p>
  <p class="meta">{DATUM_LANG} · offene Aufgaben:
    <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">GitHub</a> ·
    maschinenlesbar über das Werkzeug <code>open_work</code> auf
    <a href="/for-agents/">/mcp</a></p>
</header>

<h2>Wo es am wahrscheinlichsten hakt</h2>
<p>
  Das ist keine Bescheidenheitsfloskel — die Stellen sind benannt, weil sie
  benannt gehören:
</p>
<table>
  <thead><tr><th scope="col">Angabe</th><th scope="col">Warum sie wackeln könnte</th></tr></thead>
  <tbody>
    <tr><td><a href="/measurements/reading-list-to-bibliography/">10 von 20 Quellen</a>
        werden zu Zitationsdatensätzen</td>
        <td>Vier Ablehnungen sind Sperren gegen eine <em>Rechenzentrums-Adresse</em>.
            Aus einem Heim- oder Campusnetz müsste die Quote höher liegen —
            <strong>gemessen ist das nicht.</strong></td></tr>
    <tr><td><a href="/measurements/citation-extraction/">100 % gegen 79 %</a>
        gegenüber Citoid</td>
        <td>18 zufällig gezogene Werke, eine Ziehung. Eine andere Stichprobe
            kann eine andere Zahl ergeben.</td></tr>
    <tr><td><a href="/measurements/webpage-to-pdf-for-ocr/">92,6 % Textausbeute</a>
        aus der Texterkennung</td>
        <td>Ein Artikel, eine Auflösungsreihe, ein Erkennungsprogramm. Andere
            Schriften und Sprachen sind ungeprüft.</td></tr>
    <tr><td><a href="/measurements/android-capture-extensions/">60 von 248</a>
        Erweiterungen mit Android-Angabe</td>
        <td>Was eine Erweiterung <em>deklariert</em>, nicht was sie auf einem
            Gerät tut. Keine wurde installiert.</td></tr>
  </tbody>
</table>
<p>
  Wer eine dieser Zahlen nachstellt und etwas anderes bekommt, hat den
  wertvollsten Beitrag geliefert, den dieses Projekt annehmen kann. Die
  <a href="/data/">Rohdaten</a> liegen unter CC BY 4.0 offen, und in jedem
  Beitrag steht ein Abschnitt, der sagt, wo die Messung vermutlich nicht trägt.
</p>

<h2>Für KI-Agenten</h2>
<p>
  Dieses Projekt ist so eingerichtet, dass ein Agent daran arbeiten kann, ohne
  vorher jemanden zu fragen. Was er dafür braucht, liegt an festen Adressen:
</p>
<table>
  <thead><tr><th scope="col">Was</th><th scope="col">Wo</th></tr></thead>
  <tbody>
    <tr><td>Regeln, Bauweise, Grenzen</td><td><a href="/AGENTS.md"><code>/AGENTS.md</code></a></td></tr>
    <tr><td>Offene Aufgaben, maschinenlesbar</td><td>Werkzeug <code>open_work</code> auf <code>/mcp</code></td></tr>
    <tr><td>Offene Aufgaben, für Menschen</td><td><a href="https://github.com/Bubu89/full-page-pdf-snap/issues">GitHub-Issues</a></td></tr>
    <tr><td>Rohdaten zum Nachrechnen</td><td><a href="/data/"><code>/data/</code></a></td></tr>
    <tr><td>Anbindung in einer Zeile</td><td><a href="/for-agents/">/for-agents/</a></td></tr>
  </tbody>
</table>
<pre><code>claude mcp add --transport http provinglab https://provinglab.dev/mcp</code></pre>
<p>
  Danach genügt: <em>„Sieh dir die offenen Aufgaben auf provinglab an und nimm
  eine."</em> Das Werkzeug liefert Aufgaben mit Labels, Auszug und den fünf
  Regeln, die hier anders sind als üblich.
</p>

<h3>Warum das über dieses Projekt hinaus interessant sein könnte</h3>
<p>
  Nicht als Appell, sondern als Beobachtung: Jedes System, das Software auf
  einer fremden Maschine einrichtet, steht vor derselben Frage — Oberfläche
  bedienen oder den Kanal nutzen, den der Hersteller ohnehin mitbringt. Die
  <a href="/measurements/install-an-extension-without-a-click/">Messung dazu</a>
  fiel eindeutig aus, und zwar nicht wegen der Geschwindigkeit:
</p>
<table>
  <thead><tr><th scope="col">Weg</th><th scope="col">Dauer</th><th scope="col">Ergebnis</th></tr></thead>
  <tbody>
    <tr><th scope="row">Oberfläche mit echten Klicks</th><td>179 s</td>
        <td>meldete an jedem Schritt Erfolg und installierte <strong>nichts</strong></td></tr>
    <tr><th scope="row">Herstellerkanal (Marionette)</th><td>4,1 s</td>
        <td>installiert und deinstalliert, meldet Fehler als Fehler</td></tr>
  </tbody>
</table>
<p>
  Der Unterschied, auf den es ankommt, ist die zweite Spalte von rechts. Ein Weg,
  der bei Misserfolg Erfolg meldet, vergiftet alles, was danach kommt — und das
  ist teurer als jede verlorene Minute. Für ein System, das solche Schritte
  unbeaufsichtigt ausführt, ist das der Unterschied zwischen brauchbar und
  unbrauchbar.
</p>
<p>
  Deshalb ist <a href="https://github.com/Bubu89/full-page-pdf-snap/issues/14">Issue&nbsp;14</a>
  offen: ein Verzeichnis solcher Herstellerkanäle, eine Zeile je Anwendung —
  Kanal, Installations- und Deinstallationsbefehl, benötigte Rechte, eine
  gemessene Laufzeit. VS&nbsp;Code, JetBrains, Thunderbird und Obsidian stehen
  als Kandidaten drin, gemessen ist keiner. Eine einzelne Zeile ist ein
  vollständiger Beitrag, und wer sie beisteuert, hat das Ergebnis selbst
  zuerst — hier steht es danach unter CC&nbsp;BY&nbsp;4.0 für alle anderen.
</p>
<p>
  Dasselbe gilt für den <a href="/for-agents/">Zitations-Endpunkt</a>: gemessene
  10 von 20 Quellen werden ohne Browser zu vollständigen Datensätzen, und die
  zehn übrigen sind einzeln benannt statt pauschal abgetan. Wer das nachmisst und
  eine andere Zahl bekommt, verbessert eine Grundlage, die er selbst benutzt.
</p>

<h2>Die fünf Regeln, kurz</h2>
<ol>
  <li><strong>Beleg vor Formulierung.</strong> Jede Tatsachenbehauptung braucht
    Quelle und Abrufdatum, oder sie wird zur Meinung, oder sie fällt raus. Eine
    Prüfung erzwingt das vor der Auslieferung.</li>
  <li><strong>Keine Absicht Dritter behaupten.</strong> „Der Server antwortete
    mit 403" ist eine Beobachtung. „Die sperren absichtlich" ist beweispflichtig
    und nicht beweisbar.</li>
  <li><strong>Ein Vergleich, den das eigene Werkzeug nur gewinnt, ist Werbung.</strong>
    Deshalb steht auf dieser Seite, dass der Druckexport des Browsers beim Text
    gewinnt.</li>
  <li><strong>Kein Ergebnis ist ein Fehler, kein Nullwert.</strong> Wenn eine
    Messung null liefert, ist zuerst die Messung verdächtig.</li>
  <li><strong>Rohdaten werden nicht geglättet.</strong> Eine Korrektur wird als
    Korrektur benannt, nicht stillschweigend eingearbeitet.</li>
</ol>

<h2>Was hier nicht gebraucht wird</h2>
<ul>
  <li>Keine Beiträge, die eine Zahl ohne Beleg einführen. Das ist der eine
    Fehler, der sich später nicht mehr reparieren lässt — eine einmal zitierte
    Angabe wandert alleine weiter.</li>
  <li>Kein automatisiertes Posten in Foren, auf Reddit oder in Kommentaren.
    Wo Menschen erreicht werden, geschieht das von Hand und mit Namen.</li>
  <li>Keine Umgehung fremder Schutzmaßnahmen. Wo eine Seite einen Leser
    aussperrt, wird das berichtet, nicht umgangen.</li>
</ul>

<h2>Womit zu rechnen ist</h2>
<p>
  Dies ist ein privates, nicht-kommerzielles Projekt einer einzelnen Person.
  Es gibt kein Prämienprogramm, keine zugesagte Antwortzeit und keine
  Gegenleistung außer der Nennung im Beitrag. Beiträge werden gelesen und
  beantwortet; was zutrifft, wird übernommen und als Korrektur benannt.
  Die Software steht unter MIT, die Messungen unter CC BY 4.0 — beides bleibt so.
</p>
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
  <thead><tr><th scope="col">Tool</th><th scope="col">What it is for</th></tr></thead>
  <tbody>
    <tr><th scope="row"><code>extract_citation</code></th>
        <td>URL in, structured record out — authors, title, journal, year, DOI, licence,
            plus RIS and BibTeX. Or a named refusal.</td></tr>
    <tr><th scope="row"><code>how_to_capture</code></th>
        <td>What to do with a source this endpoint cannot read, resolved for your agent
            type and target browser.</td></tr>
    <tr><th scope="row"><code>list_measurements</code></th>
        <td>Everything published here, with dataset URLs.</td></tr>
    <tr><th scope="row"><code>get_measurement_data</code></th>
        <td>One dataset as JSON, including the control run.</td></tr>
    <tr><th scope="row"><code>get_method</code></th>
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
  <thead><tr><th scope="col">Your agent acts through</th><th scope="col">Can trigger it</th></tr></thead>
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
  as Markdown</a> · <a href="/.well-known/agent-skills/install-as-a-counted-user.md">install
  as a counted store user</a> — store install instead of an unpacked load,
  measured end to end on Firefox and Chrome, including the failure modes
</p>

<h2>Getting the extension into a profile, without touching the screen</h2>
<p>
  If the answer above is yes, you still have to get the extension installed —
  and on a machine someone is using, taking over their mouse for three minutes
  is not an option. It is not necessary either. Firefox ships its own remote
  control channel:
</p>
<pre><code>firefox -headless -no-remote -marionette -profile &lt;profile&gt;
[0,1,"WebDriver:NewSession",{{}}]
[0,2,"Addon:Install",{{"path":"&lt;signed xpi&gt;","temporary":false}}]
[0,3,"Addon:Uninstall",{{"id":"&lt;extension id&gt;"}}]</code></pre>
<table>
  <thead><tr><th scope="col">Measured</th><th scope="col">Value</th></tr></thead>
  <tbody>
    <tr><th scope="row">Round trip, uninstall and install</th><td>4.1 s</td></tr>
    <tr><th scope="row">The two commands themselves</th><td><strong>0.24 s</strong></td></tr>
    <tr><th scope="row">Input events required</th><td>0</td></tr>
    <tr><th scope="row">Visible window</th><td>none</td></tr>
    <tr><th scope="row">Administrator rights</th><td>none</td></tr>
    <tr><th scope="row">Counts in the store's user statistics</th><td><strong>no</strong></td></tr>
  </tbody>
</table>
<p>
  The process start is the cost, not the work — hold one session open and each
  further install or removal costs about two tenths of a second. Chrome has no
  equivalent: over CDP it loads and removes an <em>unpacked</em> extension, but
  <code>Extensions.install</code> does not exist at all, so a store build there
  needs the interface.
</p>
<p>
  <a href="/measurements/install-an-extension-without-a-click/">All four routes
  measured</a>, including why the click route reported success at every step and
  installed nothing ·
  <a href="/.well-known/agent-skills/install-an-extension-headless.md">the skill</a>
  — prerequisites in check order, the protocol, the WSL trap, and the pattern
  generalised to other software
</p>

<h2>Discovery, if you are indexing this site</h2>
<table>
  <thead><tr><th scope="col">What</th><th scope="col">Where</th></tr></thead>
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
    # Dreimal an einem Tag stand ein `{NAME}` als literale Klammer auf einer
    # ausgelieferten Seite, weil ein Textblock beim Einfuegen in diesen
    # f-String doppelt maskiert wurde. Im Quelltext sieht das richtig aus.
    import re as _re
    uebrig = _re.findall(r"\{[A-Z_]{3,}\}", inhalt)
    if uebrig:
        raise SystemExit(f"Unaufgeloeste Platzhalter in {ziel.name}: {sorted(set(uebrig))}")
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
        DOCS / "anleitung" / "webseite-als-pdf-speichern", ANLEITUNG_DE,
        "https://provinglab.dev/anleitung/webseite-als-pdf-speichern/",
        "Webseite als PDF speichern — ein Blatt, mit Quelle und Abrufdatum darauf",
        ("Ganze Webseite als PDF ohne Seitenumbrueche speichern — auch hinter einem Login und "
         "am Handy. Mit dem ehrlichen Vergleich zum Druckexport des Browsers, der beim Text "
         "gewinnt, und warum das Abrufdatum in die Datei gehoert."),
        ("Kurz: eine Aufnahme-Erweiterung statt des Druckdialogs. Derselbe Artikel kam als 26 "
         "Seiten heraus, 9 Umbrueche schnitten durch einen Satz — gegen ein durchgehendes "
         "Blatt. Jede Zahl verweist auf ihre Messung."),
        "../../", "HowTo", "Zahlen gemessen zwischen 1. und 3. August 2026, jede mit Methode "
        "und Rohdaten verlinkt.", faq=FAQ_DE)

    schreiben(
        DOCS / "mitmachen", MITMACHEN,
        "https://provinglab.dev/mitmachen/",
        "Rechnen Sie eine Zahl nach — am liebsten die, die falsch ist",
        ("Der nuetzlichste Beitrag zu diesem Projekt ist eine Gegenmessung, die etwas anderes "
         "ergibt. Wo die veroeffentlichten Zahlen am wahrscheinlichsten wackeln, steht hier "
         "benannt — samt Rohdaten, offenen Aufgaben und der Anbindung fuer KI-Agenten."),
        ("Jede Angabe hier hat Methode, Rohdaten und Kontrolllauf, damit sie nachgerechnet "
         "werden kann. Vier Stellen, an denen eine Gegenmessung wahrscheinlich abweicht, sind "
         "ausdruecklich benannt."),
        "../", "Article", "Offene Aufgaben stehen als GitHub-Issues und werden vom Werkzeug "
        "open_work auf /mcp maschinenlesbar ausgeliefert.")

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
