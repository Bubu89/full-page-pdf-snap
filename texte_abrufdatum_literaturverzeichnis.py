#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/how-to/abrufdatum-literaturverzeichnis/ — die Zitations-Messungen auf Deutsch, in neun Sprachen.

Anlass: AGENTS.md, "Wo Beitraege am meisten helfen", Punkt 1. Wer eine
Seminar- oder Abschlussarbeit schreibt, sucht nach "Abrufdatum",
"Literaturverzeichnis erstellen" und "Internetquellen zitieren" — Begriffe,
zu denen die englischen Messungen nichts beitragen, solange sie nur englisch
dastehen. Deshalb ist DEUTSCH hier die Ausgangsfassung (BASIS = "de", wie
texte_deutsch_seite.py); die uebrigen acht Sprachen sind daraus uebersetzt.

Die Seite fuehrt KEINE neue Zahl ein. Jede Zahl stammt aus einem vorhandenen
Datensatz unter docs/data/ und steht so schon auf der verlinkten Messseite:

    2026-08-02-quellen-archiv.json                       19,3 % / 8,7 % / 2,0 % / 603 Tage
    2026-08-03-reading-list-to-bibliography.json          10 von 20, 0,4 s
    2026-08-04-reading-list-to-bibliography-nach-ableitung.json   14 von 20, 0,58 s
    2026-08-03-de-plattformen.json                        4 von 11, 0,75 s
    2026-08-03-de-plattformen-nach-fallback.json          5 von 11, 0,69 s
    2026-08-02-citation-extraction.json  (comparison)     18 Werke, 61/61 %, 100/79 %, 0/3, 0,68/1,92 s, 14 gegen 11

Die Angaben zur Belegdatei (.zitate.txt, sechs Zitierweisen, RIS-Datumsform)
stammen aus /notes/a-download-that-never-arrives/ und zitate.js ("o. J.").

Unverrueckbar in jeder Sprache: Zahlen, Masseinheiten, Dateiformate, Werkzeug-
und Eigennamen, alle Adressen. Die Zahlen stehen deshalb in _ZAHLEN und werden
je Sprache nur im Dezimaltrennzeichen angepasst — eine uebersetzte Zahl waere
eine andere Messung.

Rendern:  python3 tools/seite-neunsprachig.py texte_abrufdatum_literaturverzeichnis.py
"""

URL = "https://provinglab.dev/how-to/abrufdatum-literaturverzeichnis/"
ZIEL = "how-to/abrufdatum-literaturverzeichnis/index.html"
SPRACHEN = ['en', 'de', 'es', 'fr', 'it', 'ja', 'pt-BR', 'ru', 'zh-CN']
BASIS = "de"
DATUM = "2026-10-23"

# Dezimalkomma, wo die Sprache es verlangt. Nur die Schreibweise aendert sich.
_KOMMA = {"de", "es", "fr", "it", "pt-BR", "ru"}


def _z(wert, l):
    return wert.replace(".", ",") if l in _KOMMA else wert


_D = "/data/"
_Q = {
    "vanish": "/measurements/web-citations-that-vanish/",
    "liste": "/measurements/reading-list-to-bibliography/",
    "de": "/measurements/de-plattformen/",
    "citoid": "/measurements/citation-extraction/",
    "beleg": "/notes/a-download-that-never-arrives/",
    "tool": "/tools/full-page-pdf-snap/",
    "zitate_js": "https://github.com/Bubu89/full-page-pdf-snap/blob/main/zitate.js",
    "issues": "https://github.com/Bubu89/full-page-pdf-snap/issues",
    "spn": "https://web.archive.org/save",
}
_ROH = {
    "vanish": _D + "2026-08-02-quellen-archiv.json",
    "liste1": _D + "2026-08-03-reading-list-to-bibliography.json",
    "liste2": _D + "2026-08-04-reading-list-to-bibliography-nach-ableitung.json",
    "de1": _D + "2026-08-03-de-plattformen.json",
    "de2": _D + "2026-08-03-de-plattformen-nach-fallback.json",
    "citoid": _D + "2026-08-02-citation-extraction.json",
}


def _seite(l, t):
    """Baut den Rumpf aus den Saetzen einer Sprache. Zahlen kommen von hier."""
    z = lambda w: _z(w, l)
    return f"""<header>
  <h1>{t['h1']}</h1>
  <p class="standfirst">
    {t['standfirst']}
  </p>
  <p class="meta-line">{t['meta']}</p>
</header>

<div class="box"><p>
  {t['hinweis']}
</p></div>

<h2>{t['h_wozu']}</h2>
<p>
  {t['wozu_1']}
</p>
<table>
  <thead><tr><th scope="col">{t['th_befund']}</th><th scope="col">{t['th_anteil']}</th></tr></thead>
  <tbody>
    <tr><td>{t['v_weg']}</td><td>{z('19.3')}&nbsp;% (29/150)</td></tr>
    <tr><td>{t['v_ohne']}</td><td>{z('8.7')}&nbsp;% (13)</td></tr>
    <tr><td>{t['v_beides']}</td><td><strong>{z('2.0')}&nbsp;%</strong> (3)</td></tr>
    <tr><td>{t['v_alter']}</td><td>603 {t['tage']}</td></tr>
  </tbody>
</table>
<p>
  {t['wozu_2']}
  <a href="{_Q['vanish']}">{t['messung']}</a> ·
  <a href="{_ROH['vanish']}">{t['rohdaten']}</a>
</p>

<h2>{t['h_form']}</h2>
<p>
  {t['form_1']}
</p>
<pre><code>Y2  - 2026/08/18/11:00</code></pre>
<p>
  {t['form_2']}
  <a href="{_Q['beleg']}">{t['messung']}</a> ·
  <a href="{_Q['zitate_js']}">zitate.js</a>
</p>

<h2>{t['h_liste']}</h2>
<p>
  {t['liste_1']}
</p>
<table>
  <thead><tr><th scope="col">{t['th_lauf']}</th><th scope="col">{t['th_datum']}</th><th scope="col">{t['th_voll']}</th><th scope="col">{t['th_je']}</th></tr></thead>
  <tbody>
    <tr><td>{t['l_liste1']}</td><td>{t['d_03']}</td><td>10/20</td><td>{z('0.4')}&nbsp;s</td></tr>
    <tr><td>{t['l_liste2']}</td><td>{t['d_04']}</td><td><strong>14/20</strong></td><td>{z('0.58')}&nbsp;s</td></tr>
    <tr><td>{t['l_de1']}</td><td>{t['d_03']}</td><td>4/11</td><td>{z('0.75')}&nbsp;s</td></tr>
    <tr><td>{t['l_de2']}</td><td>{t['d_03']}</td><td><strong>5/11</strong></td><td>{z('0.69')}&nbsp;s</td></tr>
  </tbody>
</table>
<p>
  {t['liste_2']}
</p>
<p>
  {t['liste_3']}
  <a href="{_Q['liste']}">{t['messung']}</a> (<a href="{_ROH['liste1']}">{t['rohdaten']}</a>, <a href="{_ROH['liste2']}">{t['rohdaten']}</a>) ·
  <a href="{_Q['de']}">{t['messung']}</a> (<a href="{_ROH['de1']}">{t['rohdaten']}</a>, <a href="{_ROH['de2']}">{t['rohdaten']}</a>)
</p>

<h2>{t['h_vergleich']}</h2>
<p>
  {t['vergleich_1']}
</p>
<table>
  <thead><tr><th scope="col">{t['th_18']}</th><th scope="col">{t['th_wir']}</th><th scope="col">Citoid</th></tr></thead>
  <tbody>
    <tr><td>{t['c_abdeckung']}</td><td>61&nbsp;%</td><td>61&nbsp;%</td></tr>
    <tr><td>{t['c_richtig']}</td><td><strong>100&nbsp;%</strong></td><td>79&nbsp;%</td></tr>
    <tr><td>{t['c_falsch']}</td><td>0</td><td>3</td></tr>
    <tr><td>{t['c_median']}</td><td>{z('0.68')}&nbsp;s</td><td>{z('1.92')}&nbsp;s</td></tr>
  </tbody>
</table>
<p>
  {t['vergleich_2']}
  <a href="{_Q['citoid']}">{t['messung']}</a> ·
  <a href="{_ROH['citoid']}">{t['rohdaten']}</a>
</p>

<h2>{t['h_selbst']}</h2>
<ul>
  <li>{t['s_1']}</li>
  <li>{t['s_2']}</li>
  <li>{t['s_3']}</li>
  <li>{t['s_4']}</li>
</ul>

<h2>{t['h_grenzen']}</h2>
<p>
  {t['grenzen']}
</p>

<footer>
      {t['fuss']}
      <br><br>
      <a href="../../">← Proving Lab</a> · <a href="../../disclaimer/">{t['disclaimer']}</a> · <a href="{_Q['issues']}">GitHub Issues</a>
    </footer>
"""


_T = {}

# ---------------------------------------------------------------- Deutsch ----
_T["de"] = {
    "h1": "Abrufdatum und Literaturverzeichnis: Internetquellen zitieren, gemessen statt behauptet",
    "standfirst": (
        "Wozu das Abrufdatum im Literaturverzeichnis steht, wie viel ein Werkzeug beim "
        "Erstellen des Literaturverzeichnisses abnimmt und an welcher Stelle es die Arbeit an "
        "Sie zurückgibt — zusammengefasst aus den Zitations-Messungen dieser Seite. Jede Zahl "
        "trägt ihr Datum und verweist auf ihre Rohdaten."),
    "meta": "Stand 23. Oktober 2026 · deutsche Zusammenfassung · Messungen vom 2. bis 18. August 2026",
    "hinweis": (
        "Ein privater, nicht kommerzieller Bericht — keine Rechtsberatung und keine Auskunft "
        "einer Hochschule. Welche Zitierweise gilt und wie das Abrufdatum zu schreiben ist, legt "
        "Ihr Institut fest; dessen Vorgabe geht allem hier vor. Offenlegung: Der Autor entwickelt "
        f'<a href="{_Q["tool"]}">Full Page PDF Snap</a>, das unten als eines von mehreren Mitteln vorkommt.'),
    "h_wozu": "1. Wozu das Abrufdatum dient",
    "wozu_1": (
        "Eine Internetquelle ist kein Buch: Sie kann nach dem Zitieren geändert, verschoben oder "
        "gelöscht werden. Das Abrufdatum sagt, <em>das stand an diesem Tag dort</em>. Wie oft das "
        "zählt, zeigt eine Stichprobe vom 2. August 2026: 150 Quellen aus den Literaturangaben "
        "deutschsprachiger Wikipedia-Artikel zu Wirtschafts- und Sozialpolitik, höchstens eine je Server."),
    "th_befund": "Befund", "th_anteil": "Anteil",
    "v_weg": "Der Server meldet die Seite als gelöscht (HTTP 404 oder 410)",
    "v_ohne": "Keine Kopie im Internet Archive",
    "v_beides": "Gelöscht und nie archiviert — unwiederbringlich",
    "v_alter": "Alter der jüngsten Archivkopie, Median",
    "tage": "Tage",
    "wozu_2": (
        "Wikipedia-Belege werden gepflegt; die Werte sind deshalb eher zu günstig als zu streng. "
        "Und wo eine Archivkopie existiert, ist sie im Median 603 Tage alt — oft nicht die Fassung, "
        "die Sie gelesen haben. Ein Datum allein macht eine Aussage nicht nachprüfbar, dafür braucht "
        "es eine Kopie. Die Folgerung: die Quelle in dem Moment sichern, in dem Sie sie zitieren, "
        "nicht am Ende der Arbeit."),
    "messung": "Messung", "rohdaten": "Rohdaten",
    "h_form": "2. Wie das Abrufdatum im Eintrag steht",
    "form_1": (
        "Die Form legt die Zitierweise fest — APA, Harvard, DIN 1505-2 und ISO 690 unterscheiden "
        "sich darin, und deutschsprachige Einträge verbinden mit „abgerufen am“. Full Page PDF Snap "
        "legt neben jedes PDF eine Datei mit der Endung <code>.zitate.txt</code>: je eine fertige "
        "Zeile in APA 7, MLA 9, Chicago, Harvard, DIN 1505-2 und ISO 690, dazu BibTeX und einen "
        "RIS-Satz für Citavi, Zotero und EndNote. Im RIS-Satz steht das Abrufdatum in der Form, die "
        "Citavi und EndNote einlesen, mit Uhrzeit — Seiten ändern sich im Lauf eines Tages:"),
    "form_2": (
        "Fehlt auf der Seite das Erscheinungsjahr, steht „o. J.“ im Eintrag und nicht das Jahr des "
        "Abrufs. Ein erfundenes Jahr ist teurer als eine Lücke, die auffällt."),
    "h_liste": "3. Literaturverzeichnis erstellen: was eine Maschine abnimmt",
    "liste_1": (
        "Zwei Messungen haben dieselbe Frage gestellt: Wie viele Quellen werden ohne Abtippen zu "
        "einem vollständigen Nachweis — gelesen aus dem, was die Seite selbst über sich ausweist? "
        "Gemessen am Zitations-Endpunkt dieser Seite (<code>extract_citation</code>), die Auswahl "
        "jeweils vor dem Lauf festgelegt."),
    "th_lauf": "Lauf", "th_datum": "Datum", "th_voll": "vollständig", "th_je": "je Quelle",
    "l_liste1": "Leseliste einer Seminararbeit, 20 Quellen",
    "l_liste2": "dieselben 20, Kennungen abgeleitet (DOI, CELEX)",
    "l_de1": "11 deutschsprachige Plattformen",
    "l_de2": "dieselben 11, mit den Schnittstellen der Plattformen",
    "d_03": "3. Aug. 2026", "d_04": "4. Aug. 2026",
    "liste_2": (
        "Lesbar waren die Verlagsplattformen Springer Link und Nomos eLibrary, die Repositorien "
        "PsychArchives und peDOCS und — über ihre SRU-Schnittstelle — die Deutsche "
        "Nationalbibliothek. Zurückgegeben wurden eine lizenzierte Datenbank hinter einer Anmeldung "
        "(beck-online), eine Seite mit einer Aktennummer statt eines Titels (openJur), zwei "
        "Statistikportale ohne Jahresangabe (Statistik Austria, Destatis), ein Repositorium, das den "
        "Endpunkt abweist (OPUS 4), und SSOAR als Kontrollfall mit Zugangsschranke."),
    "liste_3": (
        "Wo eine Angabe fehlt, kommt der Nachweis als unvollständig markiert zurück, statt dass das "
        "Jahr geraten wird."),
    "h_vergleich": "4. Der Vergleich — und wo die Alternative vorn liegt",
    "vergleich_1": (
        "Am 2. August 2026 liefen 18 zufällig aus OpenAlex gezogene Werke durch diesen Endpunkt und "
        "durch Citoid, den Dienst der Wikimedia auf Grundlage der Zotero-Übersetzer."),
    "th_18": "18 Werke, zufällig gezogen", "th_wir": "dieser Endpunkt",
    "c_abdeckung": "Abdeckung", "c_richtig": "Richtigkeit des Gelieferten",
    "c_falsch": "falsche Nachweise", "c_median": "Median je Quelle",
    "vergleich_2": (
        "Citoid liefert häufiger überhaupt einen Datensatz (14 gegen 11) und erreicht MDPI, PeerJ "
        "und die OECD, die diesen Endpunkt abweisen. Dafür kamen dort drei falsche Angaben zurück, "
        "darunter „Redirect URL“ als Titel eines Werks. Für ein Literaturverzeichnis ist ein falscher "
        "Eintrag teurer als eine Lücke: Die Lücke sehen Sie beim Schreiben, den falschen Eintrag "
        "findet, wer die Arbeit bewertet."),
    "h_selbst": "5. Was bei Ihnen bleibt",
    "s_1": (
        "<strong>Das Kennzeichen „vollständig“ lesen, nicht den Titel.</strong> Ein Statistikportal "
        "lieferte „Forschung, Innovation, Digitalisierung“ mit STATISTIK AUSTRIA als Verfasser — es "
        "sah fertig aus und war als unvollständig markiert."),
    "s_2": (
        "<strong>Seiten hinter einer Anmeldung, zu der Sie Zugang haben,</strong> im eigenen Browser "
        "öffnen und dort sichern. Ein Server von außen kann sie nicht lesen, eine Erweiterung in Ihrer "
        "Sitzung schon."),
    "s_3": (
        "<strong>Zeitungsartikel, Statistikseiten und graue Literatur</strong> selbst angeben: Diese "
        "Seiten antworteten vollständig und wiesen trotzdem nicht aus, was ein Nachweis braucht — mal fehlte der Verfasser, mal das Jahr."),
    "s_4": (
        "<strong>Die Kopie zum Abrufdatum aufheben</strong> — als PDF, oder bei öffentlichen Seiten "
        f'über <a href="{_Q["spn"]}">Save Page Now</a> des Internet Archive, das einen datierten, für '
        "alle Lesenden prüfbaren Link erzeugt."),
    "h_grenzen": "Grenzen",
    "grenzen": (
        "Jede Zahl stammt aus einem einzelnen Durchlauf an einem genannten Tag im August 2026; Seiten "
        "und Plattformen ändern sich, ein Lauf heute kann anders ausfallen. Die Plattform-Messung lief "
        "über einen kommerziellen VPN-Ausgang, nicht über einen privaten Anschluss. Neue Zahlen führt "
        "diese Seite nicht ein — sie fasst die verlinkten Messungen auf Deutsch zusammen."),
    "fuss": (
        "Veröffentlicht am 23. Oktober 2026. Jede Zahl verweist auf ihre Rohdaten unter "
        '<a href="/data/">/data/</a>, CC BY 4.0. Korrekturen über die GitHub-Issues.'),
    "disclaimer": "Haftungsausschluss",
}

# ---------------------------------------------------------------- English ----
_T["en"] = {
    "h1": "Retrieval date and bibliography: citing web sources, measured rather than asserted",
    "standfirst": (
        "Why a reference list carries a retrieval date, how much a tool takes off your hands when "
        "you build the bibliography, and where it hands the work back — summarised from this site's "
        "citation measurements. Every figure carries its date and links to its raw data."),
    "meta": "As of 23 October 2026 · German-first summary · measurements from 2 to 18 August 2026",
    "hinweis": (
        "A private, non-commercial account — not legal advice and not guidance from a university. "
        "Which citation style applies and how the retrieval date is written is set by your "
        "department; its rules come before anything here. Disclosure: the author develops "
        f'<a href="{_Q["tool"]}">Full Page PDF Snap</a>, which appears below as one of several options.'),
    "h_wozu": "1. What the retrieval date is for",
    "wozu_1": (
        "A web source is not a book: it can be edited, moved or deleted after you cite it. The "
        "retrieval date says <em>this is what stood there on that day</em>. How often that matters "
        "shows in a sample from 2 August 2026: 150 sources from the references of German-language "
        "Wikipedia articles on economic and social policy, at most one per server."),
    "th_befund": "Finding", "th_anteil": "Share",
    "v_weg": "The server reports the page as deleted (HTTP 404 or 410)",
    "v_ohne": "No copy in the Internet Archive",
    "v_beides": "Deleted and never archived — unrecoverable",
    "v_alter": "Age of the newest archived copy, median",
    "tage": "days",
    "wozu_2": (
        "Wikipedia references are maintained, so these values err on the kind side. And where an "
        "archived copy exists, it is a median of 603 days old — often not the version you read. A "
        "date alone does not make a claim checkable; that takes a copy. The consequence: secure the "
        "source at the moment you cite it, not at the end of the work."),
    "messung": "measurement", "rohdaten": "raw data",
    "h_form": "2. How the retrieval date appears in the entry",
    "form_1": (
        "The citation style sets the form — APA, Harvard, DIN 1505-2 and ISO 690 differ in it, and "
        "German entries join it with „abgerufen am“. Full Page PDF Snap puts a file ending in "
        "<code>.zitate.txt</code> beside every PDF: one finished line each in APA 7, MLA 9, Chicago, "
        "Harvard, DIN 1505-2 and ISO 690, plus BibTeX and an RIS record for Citavi, Zotero and "
        "EndNote. In the RIS record the retrieval date is written in the form Citavi and EndNote "
        "import, with the time — pages change in the course of a day:"),
    "form_2": (
        "If the page gives no year of publication, the entry says „o. J.“ (n.d.), not the year of "
        "retrieval. An invented year costs more than a gap that shows."),
    "h_liste": "3. Building the bibliography: what a machine takes off your hands",
    "liste_1": (
        "Two measurements asked the same question: how many sources become a complete record without "
        "typing — read from what the page declares about itself? Measured on this site's citation "
        "endpoint (<code>extract_citation</code>), each selection fixed before the run."),
    "th_lauf": "Run", "th_datum": "Date", "th_voll": "complete", "th_je": "per source",
    "l_liste1": "Reading list of a term paper, 20 sources",
    "l_liste2": "the same 20, identifiers derived (DOI, CELEX)",
    "l_de1": "11 German-language platforms",
    "l_de2": "the same 11, using the platforms' own interfaces",
    "d_03": "3 Aug 2026", "d_04": "4 Aug 2026",
    "liste_2": (
        "Readable were the publisher platforms Springer Link and Nomos eLibrary, the repositories "
        "PsychArchives and peDOCS and — through its SRU interface — the German National Library. "
        "Handed back were a licensed database behind a login (beck-online), a page with a case number "
        "instead of a title (openJur), two statistics portals without a year (Statistik Austria, "
        "Destatis), a repository that refuses the endpoint (OPUS 4), and SSOAR as the control case "
        "behind an access wall."),
    "liste_3": "Where a detail is missing, the record comes back marked incomplete instead of the year being guessed.",
    "h_vergleich": "4. The comparison — and where the alternative is ahead",
    "vergleich_1": (
        "On 2 August 2026, 18 works drawn at random from OpenAlex went through this endpoint and "
        "through Citoid, the Wikimedia service built on the Zotero translators."),
    "th_18": "18 works, drawn at random", "th_wir": "this endpoint",
    "c_abdeckung": "Coverage", "c_richtig": "Accuracy of what came back",
    "c_falsch": "Wrong records", "c_median": "Median per source",
    "vergleich_2": (
        "Citoid returns a record of some kind more often (14 against 11) and reaches MDPI, PeerJ and "
        "the OECD, which refuse this endpoint. In exchange three wrong records came back from it, "
        "among them „Redirect URL“ as the title of a work. In a bibliography a wrong entry costs more "
        "than a gap: you see the gap while writing; the wrong entry is found by whoever marks the work."),
    "h_selbst": "5. What stays with you",
    "s_1": (
        "<strong>Read the completeness flag, not the title.</strong> A statistics portal returned "
        "„Forschung, Innovation, Digitalisierung“ with STATISTIK AUSTRIA as author — it looked "
        "finished and was marked incomplete."),
    "s_2": (
        "<strong>Pages behind a login you have access to:</strong> open them in your own browser and "
        "save them there. A server outside cannot read them; an extension in your session can."),
    "s_3": (
        "<strong>Newspaper articles, statistics pages and grey literature:</strong> describe them "
        "yourself. These pages answered in full and still did not declare what a reference needs — sometimes the author was missing, sometimes the year."),
    "s_4": (
        "<strong>Keep the copy that goes with the retrieval date</strong> — as a PDF, or for public "
        f'pages via <a href="{_Q["spn"]}">Save Page Now</a> at the Internet Archive, which creates a '
        "dated link any reader can check."),
    "h_grenzen": "Limits",
    "grenzen": (
        "Every figure comes from a single run on a stated day in August 2026; pages and platforms "
        "change, and a run today may come out differently. The platform measurement ran from a "
        "commercial VPN exit, not a residential line. This page introduces no new figures — it "
        "summarises the linked measurements."),
    "fuss": (
        "Published 23 October 2026. Every figure links to its raw data under "
        '<a href="/data/">/data/</a>, CC BY 4.0. Corrections via GitHub issues.'),
    "disclaimer": "Disclaimer",
}

# ---------------------------------------------------------------- Español ----
_T["es"] = {
    "h1": "Fecha de consulta y bibliografía: citar fuentes web, medido en lugar de afirmado",
    "standfirst": (
        "Para qué sirve la fecha de consulta en la bibliografía, cuánto trabajo le quita una "
        "herramienta al elaborarla y en qué punto se lo devuelve — resumido a partir de las "
        "mediciones de citas de este sitio. Cada cifra lleva su fecha y enlaza con sus datos brutos."),
    "meta": "A 23 de octubre de 2026 · resumen en alemán y ocho idiomas · mediciones del 2 al 18 de agosto de 2026",
    "hinweis": (
        "Un informe privado y no comercial: no es asesoramiento jurídico ni una indicación de una "
        "universidad. Qué estilo de cita se aplica y cómo se escribe la fecha de consulta lo decide su "
        "departamento; sus normas prevalecen sobre todo lo que aquí se dice. Divulgación: el autor "
        f'desarrolla <a href="{_Q["tool"]}">Full Page PDF Snap</a>, que aparece abajo como una de varias opciones.'),
    "h_wozu": "1. Para qué sirve la fecha de consulta",
    "wozu_1": (
        "Una fuente web no es un libro: puede modificarse, moverse o borrarse después de citarla. La "
        "fecha de consulta dice <em>esto es lo que había ese día</em>. Cuánto importa lo muestra una "
        "muestra del 2 de agosto de 2026: 150 fuentes de las referencias de artículos de la Wikipedia "
        "en alemán sobre política económica y social, como máximo una por servidor."),
    "th_befund": "Resultado", "th_anteil": "Proporción",
    "v_weg": "El servidor indica que la página se ha borrado (HTTP 404 o 410)",
    "v_ohne": "Ninguna copia en el Internet Archive",
    "v_beides": "Borrada y nunca archivada — irrecuperable",
    "v_alter": "Antigüedad de la copia archivada más reciente, mediana",
    "tage": "días",
    "wozu_2": (
        "Las referencias de Wikipedia se mantienen, así que estos valores pecan de favorables. Y donde "
        "existe una copia archivada, tiene una mediana de 603 días — a menudo no es la versión que usted "
        "leyó. Una fecha por sí sola no hace comprobable una afirmación; para eso hace falta una copia. "
        "La consecuencia: asegurar la fuente en el momento de citarla, no al final del trabajo."),
    "messung": "medición", "rohdaten": "datos brutos",
    "h_form": "2. Cómo aparece la fecha de consulta en la entrada",
    "form_1": (
        "La forma la fija el estilo de cita: APA, Harvard, DIN 1505-2 e ISO 690 difieren en ello, y "
        "las entradas en alemán la unen con „abgerufen am“. Full Page PDF Snap coloca junto a cada PDF "
        "un archivo terminado en <code>.zitate.txt</code>: una línea lista en APA 7, MLA 9, Chicago, "
        "Harvard, DIN 1505-2 e ISO 690, además de BibTeX y un registro RIS para Citavi, Zotero y "
        "EndNote. En el registro RIS la fecha de consulta figura en la forma que importan Citavi y "
        "EndNote, con la hora — las páginas cambian a lo largo de un día:"),
    "form_2": (
        "Si la página no indica año de publicación, la entrada dice „o. J.“ (s. f.) y no el año de la "
        "consulta. Un año inventado cuesta más que un hueco que se ve."),
    "h_liste": "3. Elaborar la bibliografía: lo que una máquina le quita de encima",
    "liste_1": (
        "Dos mediciones hicieron la misma pregunta: ¿cuántas fuentes se convierten en una referencia "
        "completa sin teclear, leída de lo que la página declara sobre sí misma? Medido en el endpoint "
        "de citas de este sitio (<code>extract_citation</code>), con la selección fijada antes de cada pasada."),
    "th_lauf": "Pasada", "th_datum": "Fecha", "th_voll": "completas", "th_je": "por fuente",
    "l_liste1": "Lista de lectura de un trabajo de curso, 20 fuentes",
    "l_liste2": "las mismas 20, identificadores derivados (DOI, CELEX)",
    "l_de1": "11 plataformas en alemán",
    "l_de2": "las mismas 11, con las interfaces propias de las plataformas",
    "d_03": "3 ago. 2026", "d_04": "4 ago. 2026",
    "liste_2": (
        "Fueron legibles las plataformas editoriales Springer Link y Nomos eLibrary, los repositorios "
        "PsychArchives y peDOCS y — mediante su interfaz SRU — la Biblioteca Nacional Alemana. Se "
        "devolvieron una base de datos con licencia tras un inicio de sesión (beck-online), una página "
        "con un número de expediente en lugar de título (openJur), dos portales estadísticos sin año "
        "(Statistik Austria, Destatis), un repositorio que rechaza el endpoint (OPUS 4) y SSOAR como "
        "caso de control tras una barrera de acceso."),
    "liste_3": "Donde falta un dato, la referencia vuelve marcada como incompleta en lugar de adivinar el año.",
    "h_vergleich": "4. La comparación — y dónde va por delante la alternativa",
    "vergleich_1": (
        "El 2 de agosto de 2026, 18 obras extraídas al azar de OpenAlex pasaron por este endpoint y por "
        "Citoid, el servicio de Wikimedia basado en los traductores de Zotero."),
    "th_18": "18 obras, extraídas al azar", "th_wir": "este endpoint",
    "c_abdeckung": "Cobertura", "c_richtig": "Exactitud de lo devuelto",
    "c_falsch": "Referencias erróneas", "c_median": "Mediana por fuente",
    "vergleich_2": (
        "Citoid devuelve algún registro con más frecuencia (14 frente a 11) y llega a MDPI, PeerJ y la "
        "OCDE, que rechazan este endpoint. A cambio, devolvió tres datos erróneos, entre ellos „Redirect "
        "URL“ como título de una obra. En una bibliografía una entrada errónea cuesta más que un hueco: "
        "el hueco se ve al escribir; la entrada errónea la descubre quien evalúa el trabajo."),
    "h_selbst": "5. Lo que queda en sus manos",
    "s_1": (
        "<strong>Leer el indicador de completitud, no el título.</strong> Un portal estadístico devolvió "
        "„Forschung, Innovation, Digitalisierung“ con STATISTIK AUSTRIA como autor: parecía terminado y "
        "estaba marcado como incompleto."),
    "s_2": (
        "<strong>Páginas tras un inicio de sesión al que usted tiene acceso:</strong> ábralas en su propio "
        "navegador y guárdelas allí. Un servidor externo no puede leerlas; una extensión en su sesión sí."),
    "s_3": (
        "<strong>Artículos de prensa, páginas estadísticas y literatura gris:</strong> descríbalos usted. "
        "Estas páginas respondieron por completo y aun así no declaraban lo que necesita una referencia: a veces faltaba el autor, a veces el año."),
    "s_4": (
        "<strong>Conservar la copia que corresponde a la fecha de consulta</strong>: como PDF o, en páginas "
        f'públicas, mediante <a href="{_Q["spn"]}">Save Page Now</a> del Internet Archive, que crea un '
        "enlace fechado que cualquier lector puede comprobar."),
    "h_grenzen": "Límites",
    "grenzen": (
        "Cada cifra procede de una sola pasada en un día indicado de agosto de 2026; las páginas y las "
        "plataformas cambian, y una pasada hoy puede dar otro resultado. La medición de plataformas se "
        "hizo desde una salida VPN comercial, no desde una conexión doméstica. Esta página no introduce "
        "cifras nuevas: resume las mediciones enlazadas."),
    "fuss": (
        "Publicado el 23 de octubre de 2026. Cada cifra enlaza con sus datos brutos en "
        '<a href="/data/">/data/</a>, CC BY 4.0. Correcciones a través de GitHub issues.'),
    "disclaimer": "Aviso legal",
}

# ---------------------------------------------------------------- Français ---
_T["fr"] = {
    "h1": "Date de consultation et bibliographie : citer des sources web, mesuré plutôt qu’affirmé",
    "standfirst": (
        "À quoi sert la date de consultation dans la bibliographie, quelle part du travail un outil "
        "prend en charge pour la constituer et à quel moment il vous le rend — d’après les mesures de "
        "citation de ce site. Chaque chiffre porte sa date et renvoie à ses données brutes."),
    "meta": "État au 23 octobre 2026 · résumé d’abord en allemand · mesures du 2 au 18 août 2026",
    "hinweis": (
        "Un compte rendu privé et non commercial — ni un conseil juridique ni une consigne "
        "universitaire. Le style de citation applicable et la manière d’écrire la date de consultation "
        "relèvent de votre établissement ; ses règles priment sur tout ce qui est écrit ici. Divulgation : "
        f'l’auteur développe <a href="{_Q["tool"]}">Full Page PDF Snap</a>, cité plus bas parmi plusieurs moyens.'),
    "h_wozu": "1. À quoi sert la date de consultation",
    "wozu_1": (
        "Une source web n’est pas un livre : elle peut être modifiée, déplacée ou supprimée après "
        "avoir été citée. La date de consultation dit <em>voici ce qui figurait là ce jour-là</em>. Un "
        "échantillon du 2 août 2026 montre à quel point cela compte : 150 sources tirées des références "
        "d’articles de la Wikipédia germanophone sur la politique économique et sociale, au plus une par serveur."),
    "th_befund": "Constat", "th_anteil": "Part",
    "v_weg": "Le serveur signale la page comme supprimée (HTTP 404 ou 410)",
    "v_ohne": "Aucune copie dans l’Internet Archive",
    "v_beides": "Supprimée et jamais archivée — irrécupérable",
    "v_alter": "Âge de la copie archivée la plus récente, médiane",
    "tage": "jours",
    "wozu_2": (
        "Les références de Wikipédia sont entretenues ; ces valeurs sont donc plutôt favorables. Et là "
        "où une copie archivée existe, elle a en médiane 603 jours — souvent pas la version que vous "
        "avez lue. Une date seule ne rend pas une affirmation vérifiable ; il faut une copie. La "
        "conséquence : sauvegarder la source au moment où vous la citez, pas à la fin du travail."),
    "messung": "mesure", "rohdaten": "données brutes",
    "h_form": "2. Comment la date de consultation figure dans la référence",
    "form_1": (
        "Le style de citation en fixe la forme — APA, Harvard, DIN 1505-2 et ISO 690 diffèrent sur ce "
        "point, et les références en allemand la relient par „abgerufen am“. Full Page PDF Snap dépose "
        "à côté de chaque PDF un fichier se terminant par <code>.zitate.txt</code> : une ligne prête "
        "dans chacun des styles APA 7, MLA 9, Chicago, Harvard, DIN 1505-2 et ISO 690, plus BibTeX et "
        "un enregistrement RIS pour Citavi, Zotero et EndNote. Dans l’enregistrement RIS, la date de "
        "consultation est écrite sous la forme qu’importent Citavi et EndNote, avec l’heure — les pages "
        "changent au cours d’une journée :"),
    "form_2": (
        "Si la page n’indique pas d’année de publication, la référence porte „o. J.“ (s. d.) et non "
        "l’année de consultation. Une année inventée coûte plus cher qu’une lacune visible."),
    "h_liste": "3. Constituer la bibliographie : ce qu’une machine prend en charge",
    "liste_1": (
        "Deux mesures ont posé la même question : combien de sources deviennent une référence complète "
        "sans rien saisir, lue à partir de ce que la page déclare sur elle-même ? Mesuré sur le point "
        "d’accès de citation de ce site (<code>extract_citation</code>), la sélection étant fixée avant chaque passage."),
    "th_lauf": "Passage", "th_datum": "Date", "th_voll": "complètes", "th_je": "par source",
    "l_liste1": "Liste de lecture d’un mémoire, 20 sources",
    "l_liste2": "les mêmes 20, identifiants dérivés (DOI, CELEX)",
    "l_de1": "11 plateformes germanophones",
    "l_de2": "les mêmes 11, via les interfaces propres des plateformes",
    "d_03": "3 août 2026", "d_04": "4 août 2026",
    "liste_2": (
        "Étaient lisibles les plateformes d’éditeurs Springer Link et Nomos eLibrary, les dépôts "
        "PsychArchives et peDOCS et — via son interface SRU — la Bibliothèque nationale allemande. Ont "
        "été rendus : une base de données sous licence derrière une connexion (beck-online), une page "
        "portant un numéro de dossier au lieu d’un titre (openJur), deux portails statistiques sans "
        "année (Statistik Austria, Destatis), un dépôt qui refuse le point d’accès (OPUS 4) et SSOAR "
        "comme cas de contrôle derrière une barrière d’accès."),
    "liste_3": "Là où une donnée manque, la référence revient marquée incomplète au lieu que l’année soit devinée.",
    "h_vergleich": "4. La comparaison — et où l’alternative fait mieux",
    "vergleich_1": (
        "Le 2 août 2026, 18 œuvres tirées au hasard dans OpenAlex sont passées par ce point d’accès et "
        "par Citoid, le service de Wikimedia fondé sur les traducteurs de Zotero."),
    "th_18": "18 œuvres, tirées au hasard", "th_wir": "ce point d’accès",
    "c_abdeckung": "Couverture", "c_richtig": "Exactitude de ce qui revient",
    "c_falsch": "Références erronées", "c_median": "Médiane par source",
    "vergleich_2": (
        "Citoid renvoie plus souvent un enregistrement quelconque (14 contre 11) et atteint MDPI, PeerJ "
        "et l’OCDE, qui refusent ce point d’accès. En contrepartie, il a renvoyé trois données erronées, "
        "dont „Redirect URL“ comme titre d’une œuvre. Dans une bibliographie, une référence fausse coûte "
        "plus cher qu’une lacune : la lacune se voit en écrivant, la référence fausse est découverte par "
        "celui qui évalue le travail."),
    "h_selbst": "5. Ce qui vous reste à faire",
    "s_1": (
        "<strong>Lire l’indicateur de complétude, pas le titre.</strong> Un portail statistique a "
        "renvoyé „Forschung, Innovation, Digitalisierung“ avec STATISTIK AUSTRIA comme auteur — "
        "l’ensemble paraissait terminé et était marqué incomplet."),
    "s_2": (
        "<strong>Pages derrière une connexion à laquelle vous avez accès :</strong> ouvrez-les dans "
        "votre propre navigateur et sauvegardez-les là. Un serveur extérieur ne peut pas les lire ; une "
        "extension dans votre session, si."),
    "s_3": (
        "<strong>Articles de presse, pages statistiques et littérature grise :</strong> décrivez-les "
        "vous-même. Ces pages répondaient intégralement et ne déclaraient pourtant pas ce dont une référence a besoin — tantôt l’auteur manquait, tantôt l’année."),
    "s_4": (
        "<strong>Conserver la copie qui correspond à la date de consultation</strong> — en PDF ou, pour "
        f'les pages publiques, via <a href="{_Q["spn"]}">Save Page Now</a> de l’Internet Archive, qui '
        "crée un lien daté vérifiable par tout lecteur."),
    "h_grenzen": "Limites",
    "grenzen": (
        "Chaque chiffre provient d’un seul passage à un jour indiqué d’août 2026 ; pages et plateformes "
        "changent, et un passage aujourd’hui peut donner un autre résultat. La mesure des plateformes a "
        "été faite depuis une sortie VPN commerciale, pas depuis une ligne résidentielle. Cette page "
        "n’introduit aucun chiffre nouveau — elle résume les mesures liées."),
    "fuss": (
        "Publié le 23 octobre 2026. Chaque chiffre renvoie à ses données brutes sous "
        '<a href="/data/">/data/</a>, CC BY 4.0. Corrections via les GitHub issues.'),
    "disclaimer": "Avertissement",
}

# ---------------------------------------------------------------- Italiano ---
_T["it"] = {
    "h1": "Data di consultazione e bibliografia: citare fonti web, misurato invece che affermato",
    "standfirst": (
        "A che cosa serve la data di consultazione in bibliografia, quanto lavoro uno strumento toglie "
        "nel compilarla e in quale punto lo restituisce a voi — riassunto dalle misurazioni sulle "
        "citazioni di questo sito. Ogni cifra porta la sua data e rimanda ai dati grezzi."),
    "meta": "Aggiornato al 23 ottobre 2026 · sintesi nata in tedesco · misurazioni dal 2 al 18 agosto 2026",
    "hinweis": (
        "Un resoconto privato e non commerciale — non è consulenza legale né un’indicazione di "
        "un’università. Quale stile di citazione valga e come si scriva la data di consultazione lo "
        "stabilisce il vostro dipartimento; le sue regole prevalgono su quanto scritto qui. Trasparenza: "
        f'l’autore sviluppa <a href="{_Q["tool"]}">Full Page PDF Snap</a>, che compare sotto come uno di più strumenti.'),
    "h_wozu": "1. A che cosa serve la data di consultazione",
    "wozu_1": (
        "Una fonte web non è un libro: può essere modificata, spostata o cancellata dopo la citazione. "
        "La data di consultazione dice <em>questo c’era quel giorno</em>. Quanto conti lo mostra un "
        "campione del 2 agosto 2026: 150 fonti dalle note di voci della Wikipedia in lingua tedesca su "
        "politica economica e sociale, al massimo una per server."),
    "th_befund": "Risultato", "th_anteil": "Quota",
    "v_weg": "Il server segnala la pagina come cancellata (HTTP 404 o 410)",
    "v_ohne": "Nessuna copia nell’Internet Archive",
    "v_beides": "Cancellata e mai archiviata — irrecuperabile",
    "v_alter": "Età della copia archiviata più recente, mediana",
    "tage": "giorni",
    "wozu_2": (
        "Le note di Wikipedia vengono curate, quindi questi valori sono semmai ottimistici. E dove esiste "
        "una copia archiviata, ha in mediana 603 giorni — spesso non è la versione che avete letto. Una "
        "data da sola non rende verificabile un’affermazione; serve una copia. La conseguenza: mettere al "
        "sicuro la fonte nel momento in cui la citate, non alla fine del lavoro."),
    "messung": "misurazione", "rohdaten": "dati grezzi",
    "h_form": "2. Come compare la data di consultazione nella voce",
    "form_1": (
        "La forma la stabilisce lo stile di citazione — APA, Harvard, DIN 1505-2 e ISO 690 differiscono "
        "in questo, e le voci in tedesco la introducono con „abgerufen am“. Full Page PDF Snap affianca a "
        "ogni PDF un file che termina in <code>.zitate.txt</code>: una riga pronta in APA 7, MLA 9, "
        "Chicago, Harvard, DIN 1505-2 e ISO 690, più BibTeX e un record RIS per Citavi, Zotero ed "
        "EndNote. Nel record RIS la data di consultazione è scritta nella forma che Citavi ed EndNote "
        "importano, con l’ora — le pagine cambiano nel corso di una giornata:"),
    "form_2": (
        "Se la pagina non indica l’anno di pubblicazione, la voce riporta „o. J.“ (s. d.) e non l’anno "
        "della consultazione. Un anno inventato costa più di una lacuna che si vede."),
    "h_liste": "3. Compilare la bibliografia: che cosa toglie di mano una macchina",
    "liste_1": (
        "Due misurazioni hanno posto la stessa domanda: quante fonti diventano un riferimento completo "
        "senza digitare nulla, letto da ciò che la pagina dichiara di sé? Misurato sull’endpoint di "
        "citazione di questo sito (<code>extract_citation</code>), con la selezione fissata prima di ogni passaggio."),
    "th_lauf": "Passaggio", "th_datum": "Data", "th_voll": "complete", "th_je": "per fonte",
    "l_liste1": "Lista di lettura di una tesina, 20 fonti",
    "l_liste2": "le stesse 20, identificatori ricavati (DOI, CELEX)",
    "l_de1": "11 piattaforme in lingua tedesca",
    "l_de2": "le stesse 11, con le interfacce proprie delle piattaforme",
    "d_03": "3 ago 2026", "d_04": "4 ago 2026",
    "liste_2": (
        "Leggibili erano le piattaforme editoriali Springer Link e Nomos eLibrary, i repository "
        "PsychArchives e peDOCS e — tramite la sua interfaccia SRU — la Biblioteca nazionale tedesca. "
        "Restituiti sono stati una banca dati in licenza dietro un accesso (beck-online), una pagina con "
        "un numero di fascicolo al posto del titolo (openJur), due portali statistici senza anno "
        "(Statistik Austria, Destatis), un repository che respinge l’endpoint (OPUS 4) e SSOAR come caso "
        "di controllo dietro una barriera d’accesso."),
    "liste_3": "Dove manca un dato, il riferimento torna segnato come incompleto invece di indovinare l’anno.",
    "h_vergleich": "4. Il confronto — e dove l’alternativa è avanti",
    "vergleich_1": (
        "Il 2 agosto 2026, 18 opere estratte a caso da OpenAlex sono passate per questo endpoint e per "
        "Citoid, il servizio di Wikimedia basato sui traduttori di Zotero."),
    "th_18": "18 opere, estratte a caso", "th_wir": "questo endpoint",
    "c_abdeckung": "Copertura", "c_richtig": "Esattezza di ciò che torna",
    "c_falsch": "Riferimenti errati", "c_median": "Mediana per fonte",
    "vergleich_2": (
        "Citoid restituisce più spesso un record di qualche tipo (14 contro 11) e raggiunge MDPI, PeerJ e "
        "l’OCSE, che respingono questo endpoint. In cambio ha restituito tre dati errati, tra cui "
        "„Redirect URL“ come titolo di un’opera. In una bibliografia una voce sbagliata costa più di una "
        "lacuna: la lacuna la vedete mentre scrivete, la voce sbagliata la scopre chi valuta il lavoro."),
    "h_selbst": "5. Che cosa resta a voi",
    "s_1": (
        "<strong>Leggere l’indicatore di completezza, non il titolo.</strong> Un portale statistico ha "
        "restituito „Forschung, Innovation, Digitalisierung“ con STATISTIK AUSTRIA come autore — sembrava "
        "finito ed era segnato come incompleto."),
    "s_2": (
        "<strong>Pagine dietro un accesso di cui disponete:</strong> apritele nel vostro browser e "
        "salvatele lì. Un server esterno non può leggerle; un’estensione nella vostra sessione sì."),
    "s_3": (
        "<strong>Articoli di giornale, pagine statistiche e letteratura grigia:</strong> descriveteli voi. "
        "Queste pagine rispondevano per intero e tuttavia non dichiaravano ciò che serve a un riferimento — a volte mancava l’autore, a volte l’anno."),
    "s_4": (
        "<strong>Conservare la copia che corrisponde alla data di consultazione</strong> — come PDF o, per "
        f'le pagine pubbliche, con <a href="{_Q["spn"]}">Save Page Now</a> dell’Internet Archive, che crea '
        "un link datato verificabile da qualunque lettore."),
    "h_grenzen": "Limiti",
    "grenzen": (
        "Ogni cifra proviene da un singolo passaggio in un giorno indicato di agosto 2026; pagine e "
        "piattaforme cambiano, e un passaggio oggi può dare un altro esito. La misurazione delle "
        "piattaforme è stata eseguita da un’uscita VPN commerciale, non da una linea domestica. Questa "
        "pagina non introduce cifre nuove — riassume le misurazioni collegate."),
    "fuss": (
        "Pubblicato il 23 ottobre 2026. Ogni cifra rimanda ai dati grezzi in "
        '<a href="/data/">/data/</a>, CC BY 4.0. Correzioni tramite le GitHub issues.'),
    "disclaimer": "Esclusione di responsabilità",
}

# ---------------------------------------------------------------- 日本語 -----
_T["ja"] = {
    "h1": "参照日と参考文献リスト：ウェブ資料の引用を、主張ではなく測定で",
    "standfirst": (
        "参考文献リストに参照日（ドイツ語で Abrufdatum）を書く理由、文献リスト作りでツールがどこまで"
        "肩代わりし、どこで作業をあなたに返すのか ― 本サイトの引用に関する測定をまとめました。"
        "すべての数値に日付があり、元データにリンクしています。"),
    "meta": "2026年10月23日時点 · ドイツ語版を基にした要約 · 測定は2026年8月2日〜18日",
    "hinweis": (
        "個人による非営利の報告であり、法的助言でも大学の指示でもありません。どの引用スタイルを使い、"
        "参照日をどう書くかは所属機関が定めます。その規定がここに書かれたすべてに優先します。"
        f'開示：著者は <a href="{_Q["tool"]}">Full Page PDF Snap</a> を開発しており、下で複数の手段の一つとして登場します。'),
    "h_wozu": "1. 参照日は何のためにあるか",
    "wozu_1": (
        "ウェブ資料は本ではありません。引用した後に書き換えられ、移動され、削除されることがあります。"
        "参照日は<em>その日そこにはこう書かれていた</em>という表明です。それがどれほど重要かを、"
        "2026年8月2日の標本が示します。経済・社会政策に関するドイツ語版ウィキペディア記事の出典から"
        "150件、1サーバーにつき最大1件を抽出しました。"),
    "th_befund": "結果", "th_anteil": "割合",
    "v_weg": "サーバーがページを削除済みと応答（HTTP 404 または 410）",
    "v_ohne": "Internet Archive にコピーが一つもない",
    "v_beides": "削除済みで一度も保存されていない ― 回復不能",
    "v_alter": "最新の保存コピーの経過日数（中央値）",
    "tage": "日",
    "wozu_2": (
        "ウィキペディアの出典は手入れされているため、これらの値はむしろ甘めです。保存コピーがある場合でも"
        "中央値で603日前のもので、あなたが読んだ版ではないことが多いのです。日付だけでは主張を検証できず、"
        "そのためにはコピーが必要です。結論：資料は論文の最後ではなく、引用したその時に保存すること。"),
    "messung": "測定", "rohdaten": "元データ",
    "h_form": "2. 参照日は文献項目にどう書かれるか",
    "form_1": (
        "書式は引用スタイルが決めます。APA、Harvard、DIN 1505-2、ISO 690 で異なり、ドイツ語の項目では"
        "„abgerufen am“でつなぎます。Full Page PDF Snap はすべての PDF の隣に <code>.zitate.txt</code> "
        "で終わるファイルを置きます。APA 7、MLA 9、Chicago、Harvard、DIN 1505-2、ISO 690 の完成した行が"
        "各1行、さらに BibTeX と、Citavi・Zotero・EndNote 用の RIS レコードが入っています。RIS レコードでは"
        "参照日が Citavi と EndNote が読み込める形式で、時刻付きで書かれます ― ページは一日のうちにも変わるからです："),
    "form_2": (
        "ページに出版年がなければ、項目には参照した年ではなく„o. J.“（年不明）と書かれます。"
        "作り上げた年は、目に見える空欄よりも高くつきます。"),
    "h_liste": "3. 参考文献リストを作る：機械が肩代わりできること",
    "liste_1": (
        "二つの測定が同じ問いを立てました。ページ自身が宣言している情報から、打ち込みなしで完全な文献記録に"
        "なる資料はいくつあるか。本サイトの引用エンドポイント（<code>extract_citation</code>）で測定し、"
        "対象はいずれも実行前に固定しました。"),
    "th_lauf": "実行", "th_datum": "日付", "th_voll": "完全", "th_je": "1件あたり",
    "l_liste1": "期末レポートの文献リスト、20件",
    "l_liste2": "同じ20件、識別子を導出（DOI、CELEX）",
    "l_de1": "ドイツ語圏のプラットフォーム11件",
    "l_de2": "同じ11件、各プラットフォーム自身のインターフェースを利用",
    "d_03": "2026年8月3日", "d_04": "2026年8月4日",
    "liste_2": (
        "読み取れたのは出版社プラットフォームの Springer Link と Nomos eLibrary、リポジトリの PsychArchives と "
        "peDOCS、そして SRU インターフェース経由のドイツ国立図書館です。返却されたのは、ログインの向こうにある"
        "契約データベース（beck-online）、タイトルの代わりに事件番号しかないページ（openJur）、年の記載がない"
        "統計ポータル二つ（Statistik Austria、Destatis）、エンドポイントを拒否するリポジトリ（OPUS 4）、"
        "そしてアクセス制限の向こうにある対照例の SSOAR です。"),
    "liste_3": "情報が欠けている場合、年を推測するのではなく、記録は「不完全」と印を付けて返されます。",
    "h_vergleich": "4. 比較 ― そして代替手段が勝る点",
    "vergleich_1": (
        "2026年8月2日、OpenAlex から無作為に抽出した18件の著作を、このエンドポイントと、Zotero の"
        "トランスレーターを基にした Wikimedia のサービス Citoid に通しました。"),
    "th_18": "無作為抽出の18件", "th_wir": "このエンドポイント",
    "c_abdeckung": "カバー率", "c_richtig": "返された内容の正確さ",
    "c_falsch": "誤った記録", "c_median": "1件あたりの中央値",
    "vergleich_2": (
        "Citoid は何らかの記録を返す頻度が高く（14対11）、このエンドポイントを拒否する MDPI、PeerJ、OECD "
        "にも届きます。その代わり誤ったデータが3件返り、その中には著作のタイトルとしての„Redirect URL“も"
        "ありました。参考文献リストでは、誤った項目は空欄より高くつきます。空欄は書いている間に見えますが、"
        "誤った項目は論文を評価する人が見つけるのです。"),
    "h_selbst": "5. あなたの手に残ること",
    "s_1": (
        "<strong>タイトルではなく「完全」フラグを読むこと。</strong>ある統計ポータルは STATISTIK AUSTRIA を"
        "著者として„Forschung, Innovation, Digitalisierung“を返しました。完成して見えましたが、不完全と"
        "印が付いていました。"),
    "s_2": (
        "<strong>あなたがアクセス権を持つログインの向こうのページ：</strong>自分のブラウザーで開き、そこで"
        "保存してください。外部のサーバーには読めませんが、あなたのセッション内の拡張機能なら読めます。"),
    "s_3": (
        "<strong>新聞記事、統計ページ、灰色文献：</strong>自分で記述してください。これらのページは完全に"
        "応答しながら、文献記録に必要な情報を宣言していませんでした。著者が欠けることもあれば、年が欠けることもありました。"),
    "s_4": (
        "<strong>参照日に対応するコピーを保管すること</strong> ― PDF として、あるいは公開ページなら "
        f'Internet Archive の <a href="{_Q["spn"]}">Save Page Now</a> で。誰でも確認できる日付入りの'
        "リンクが作られます。"),
    "h_grenzen": "限界",
    "grenzen": (
        "どの数値も、2026年8月の特定の日の1回の実行によるものです。ページやプラットフォームは変わるため、"
        "今日実行すれば結果が異なることがあります。プラットフォームの測定は家庭用回線ではなく商用 VPN の出口から"
        "行いました。このページは新しい数値を加えず、リンク先の測定をまとめたものです。"),
    "fuss": (
        "2026年10月23日公開。すべての数値は <a href=\"/data/\">/data/</a> の元データ（CC BY 4.0）に"
        "リンクしています。訂正は GitHub issues へ。"),
    "disclaimer": "免責事項",
}

# ---------------------------------------------------------------- Português --
_T["pt-BR"] = {
    "h1": "Data de acesso e bibliografia: citar fontes da web, medido em vez de afirmado",
    "standfirst": (
        "Para que serve a data de acesso na bibliografia, quanto trabalho uma ferramenta tira das suas "
        "mãos ao montá-la e em que ponto o devolve — resumido das medições de citação deste site. Cada "
        "número traz a sua data e leva aos dados brutos."),
    "meta": "Situação em 23 de outubro de 2026 · resumo nascido em alemão · medições de 2 a 18 de agosto de 2026",
    "hinweis": (
        "Um relato privado e não comercial — não é assessoria jurídica nem orientação de uma "
        "universidade. Qual estilo de citação vale e como se escreve a data de acesso é definido pelo seu "
        "departamento; as regras dele prevalecem sobre tudo o que está aqui. Divulgação: o autor desenvolve "
        f'<a href="{_Q["tool"]}">Full Page PDF Snap</a>, que aparece abaixo como uma de várias opções.'),
    "h_wozu": "1. Para que serve a data de acesso",
    "wozu_1": (
        "Uma fonte da web não é um livro: pode ser alterada, movida ou apagada depois de citada. A data "
        "de acesso diz <em>isto é o que estava lá naquele dia</em>. Uma amostra de 2 de agosto de 2026 "
        "mostra o quanto isso pesa: 150 fontes das referências de artigos da Wikipédia em alemão sobre "
        "política econômica e social, no máximo uma por servidor."),
    "th_befund": "Resultado", "th_anteil": "Parcela",
    "v_weg": "O servidor informa a página como apagada (HTTP 404 ou 410)",
    "v_ohne": "Nenhuma cópia no Internet Archive",
    "v_beides": "Apagada e nunca arquivada — irrecuperável",
    "v_alter": "Idade da cópia arquivada mais recente, mediana",
    "tage": "dias",
    "wozu_2": (
        "As referências da Wikipédia são cuidadas; por isso estes valores tendem a ser favoráveis. E onde "
        "existe uma cópia arquivada, ela tem em mediana 603 dias — muitas vezes não é a versão que você "
        "leu. Uma data sozinha não torna uma afirmação verificável; para isso é preciso uma cópia. A "
        "consequência: guardar a fonte no momento em que você a cita, não no fim do trabalho."),
    "messung": "medição", "rohdaten": "dados brutos",
    "h_form": "2. Como a data de acesso aparece na referência",
    "form_1": (
        "A forma é definida pelo estilo de citação — APA, Harvard, DIN 1505-2 e ISO 690 diferem nisso, e "
        "as referências em alemão a introduzem com „abgerufen am“. O Full Page PDF Snap coloca ao lado de "
        "cada PDF um arquivo terminado em <code>.zitate.txt</code>: uma linha pronta em APA 7, MLA 9, "
        "Chicago, Harvard, DIN 1505-2 e ISO 690, além de BibTeX e um registro RIS para Citavi, Zotero e "
        "EndNote. No registro RIS a data de acesso é escrita na forma que Citavi e EndNote importam, com a "
        "hora — as páginas mudam ao longo de um dia:"),
    "form_2": (
        "Se a página não informa o ano de publicação, a referência traz „o. J.“ (s.d.) e não o ano do "
        "acesso. Um ano inventado custa mais do que uma lacuna que se vê."),
    "h_liste": "3. Montar a bibliografia: o que uma máquina tira das suas mãos",
    "liste_1": (
        "Duas medições fizeram a mesma pergunta: quantas fontes viram uma referência completa sem "
        "digitação, lida a partir do que a própria página declara sobre si? Medido no endpoint de citação "
        "deste site (<code>extract_citation</code>), com a seleção fixada antes de cada rodada."),
    "th_lauf": "Rodada", "th_datum": "Data", "th_voll": "completas", "th_je": "por fonte",
    "l_liste1": "Lista de leitura de um trabalho acadêmico, 20 fontes",
    "l_liste2": "as mesmas 20, identificadores derivados (DOI, CELEX)",
    "l_de1": "11 plataformas em alemão",
    "l_de2": "as mesmas 11, com as interfaces próprias das plataformas",
    "d_03": "3 ago. 2026", "d_04": "4 ago. 2026",
    "liste_2": (
        "Foram legíveis as plataformas editoriais Springer Link e Nomos eLibrary, os repositórios "
        "PsychArchives e peDOCS e — pela sua interface SRU — a Biblioteca Nacional Alemã. Foram devolvidos "
        "uma base de dados licenciada atrás de um login (beck-online), uma página com um número de processo "
        "em vez de título (openJur), dois portais estatísticos sem ano (Statistik Austria, Destatis), um "
        "repositório que recusa o endpoint (OPUS 4) e o SSOAR como caso de controle atrás de uma barreira de acesso."),
    "liste_3": "Onde falta um dado, a referência volta marcada como incompleta em vez de o ano ser adivinhado.",
    "h_vergleich": "4. A comparação — e onde a alternativa sai na frente",
    "vergleich_1": (
        "Em 2 de agosto de 2026, 18 obras sorteadas no OpenAlex passaram por este endpoint e pelo Citoid, "
        "o serviço da Wikimedia baseado nos tradutores do Zotero."),
    "th_18": "18 obras, sorteadas", "th_wir": "este endpoint",
    "c_abdeckung": "Cobertura", "c_richtig": "Exatidão do que voltou",
    "c_falsch": "Referências erradas", "c_median": "Mediana por fonte",
    "vergleich_2": (
        "O Citoid devolve algum registro com mais frequência (14 contra 11) e alcança MDPI, PeerJ e a OCDE, "
        "que recusam este endpoint. Em troca, devolveu três dados errados, entre eles „Redirect URL“ como "
        "título de uma obra. Numa bibliografia, uma entrada errada custa mais do que uma lacuna: a lacuna "
        "você vê ao escrever; a entrada errada é descoberta por quem avalia o trabalho."),
    "h_selbst": "5. O que fica com você",
    "s_1": (
        "<strong>Ler o indicador de completude, não o título.</strong> Um portal estatístico devolveu "
        "„Forschung, Innovation, Digitalisierung“ com STATISTIK AUSTRIA como autor — parecia pronto e "
        "estava marcado como incompleto."),
    "s_2": (
        "<strong>Páginas atrás de um login ao qual você tem acesso:</strong> abra-as no seu próprio "
        "navegador e salve-as ali. Um servidor externo não consegue lê-las; uma extensão na sua sessão consegue."),
    "s_3": (
        "<strong>Artigos de jornal, páginas estatísticas e literatura cinzenta:</strong> descreva-os você "
        "mesmo. Essas páginas responderam por completo e ainda assim não declaravam o que uma referência precisa — às vezes faltava o autor, às vezes o ano."),
    "s_4": (
        "<strong>Guardar a cópia que corresponde à data de acesso</strong> — como PDF ou, em páginas "
        f'públicas, pelo <a href="{_Q["spn"]}">Save Page Now</a> do Internet Archive, que cria um link '
        "datado que qualquer leitor pode verificar."),
    "h_grenzen": "Limites",
    "grenzen": (
        "Cada número vem de uma única rodada num dia indicado de agosto de 2026; páginas e plataformas "
        "mudam, e uma rodada hoje pode dar outro resultado. A medição das plataformas foi feita a partir de "
        "uma saída de VPN comercial, não de uma conexão residencial. Esta página não introduz números novos "
        "— resume as medições vinculadas."),
    "fuss": (
        "Publicado em 23 de outubro de 2026. Cada número leva aos dados brutos em "
        '<a href="/data/">/data/</a>, CC BY 4.0. Correções pelas GitHub issues.'),
    "disclaimer": "Aviso legal",
}

# ---------------------------------------------------------------- Русский ----
_T["ru"] = {
    "h1": "Дата обращения и список литературы: как цитировать веб-источники — измерено, а не заявлено",
    "standfirst": (
        "Зачем в списке литературы стоит дата обращения, какую часть работы над списком берёт на себя "
        "инструмент и в какой момент он возвращает её вам — по материалам измерений цитирования на этом "
        "сайте. У каждой цифры есть дата и ссылка на исходные данные."),
    "meta": "По состоянию на 23 октября 2026 г. · сводка, написанная сначала по-немецки · измерения со 2 по 18 августа 2026 г.",
    "hinweis": (
        "Частный некоммерческий отчёт — не юридическая консультация и не указание университета. Какой "
        "стиль цитирования применять и как писать дату обращения, определяет ваша кафедра; её правила "
        "важнее всего, что здесь написано. Раскрытие: автор разрабатывает "
        f'<a href="{_Q["tool"]}">Full Page PDF Snap</a>, который ниже упоминается как одно из нескольких средств.'),
    "h_wozu": "1. Зачем нужна дата обращения",
    "wozu_1": (
        "Веб-источник — не книга: после цитирования его могут изменить, перенести или удалить. Дата "
        "обращения говорит: <em>вот что было там в тот день</em>. Насколько это важно, показывает выборка "
        "от 2 августа 2026 г.: 150 источников из ссылок статей немецкоязычной Википедии об экономической "
        "и социальной политике, не более одного на сервер."),
    "th_befund": "Результат", "th_anteil": "Доля",
    "v_weg": "Сервер сообщает, что страница удалена (HTTP 404 или 410)",
    "v_ohne": "Нет ни одной копии в Internet Archive",
    "v_beides": "Удалена и ни разу не архивирована — невосстановима",
    "v_alter": "Возраст самой свежей архивной копии, медиана",
    "tage": "дн.",
    "wozu_2": (
        "Ссылки в Википедии поддерживаются, поэтому эти значения скорее занижены. А там, где архивная "
        "копия есть, её медианный возраст — 603 дня, и часто это не та версия, которую вы читали. Одна "
        "лишь дата не делает утверждение проверяемым; для этого нужна копия. Вывод: сохранять источник в "
        "момент цитирования, а не в конце работы."),
    "messung": "измерение", "rohdaten": "исходные данные",
    "h_form": "2. Как дата обращения выглядит в записи",
    "form_1": (
        "Форму задаёт стиль цитирования — APA, Harvard, DIN 1505-2 и ISO 690 здесь различаются, а "
        "немецкие записи вводят её словами „abgerufen am“. Full Page PDF Snap кладёт рядом с каждым PDF "
        "файл с окончанием <code>.zitate.txt</code>: по одной готовой строке в APA 7, MLA 9, Chicago, "
        "Harvard, DIN 1505-2 и ISO 690, а также BibTeX и запись RIS для Citavi, Zotero и EndNote. В записи "
        "RIS дата обращения стоит в том виде, который импортируют Citavi и EndNote, со временем — страницы "
        "меняются в течение дня:"),
    "form_2": (
        "Если на странице нет года издания, в записи стоит „o. J.“ (б. г.), а не год обращения. "
        "Выдуманный год обходится дороже, чем заметный пробел."),
    "h_liste": "3. Составление списка литературы: что берёт на себя машина",
    "liste_1": (
        "Два измерения задавали один и тот же вопрос: сколько источников превращаются в полную "
        "библиографическую запись без ручного ввода — по тому, что страница сама о себе сообщает? "
        "Измерено на эндпоинте цитирования этого сайта (<code>extract_citation</code>), выборка каждый раз "
        "зафиксирована до прогона."),
    "th_lauf": "Прогон", "th_datum": "Дата", "th_voll": "полных", "th_je": "на источник",
    "l_liste1": "Список литературы курсовой работы, 20 источников",
    "l_liste2": "те же 20, идентификаторы выведены (DOI, CELEX)",
    "l_de1": "11 немецкоязычных платформ",
    "l_de2": "те же 11, через собственные интерфейсы платформ",
    "d_03": "3 авг. 2026", "d_04": "4 авг. 2026",
    "liste_2": (
        "Прочитаны были издательские платформы Springer Link и Nomos eLibrary, репозитории PsychArchives и "
        "peDOCS и — через интерфейс SRU — Немецкая национальная библиотека. Возвращены: лицензионная база "
        "данных за входом в систему (beck-online), страница с номером дела вместо заглавия (openJur), два "
        "статистических портала без года (Statistik Austria, Destatis), репозиторий, отказывающий "
        "эндпоинту (OPUS 4), и SSOAR как контрольный случай за барьером доступа."),
    "liste_3": "Если сведений не хватает, запись возвращается с пометкой «неполная», а год не угадывается.",
    "h_vergleich": "4. Сравнение — и где альтернатива впереди",
    "vergleich_1": (
        "2 августа 2026 г. 18 работ, случайно выбранных из OpenAlex, прошли через этот эндпоинт и через "
        "Citoid — сервис Wikimedia на основе трансляторов Zotero."),
    "th_18": "18 работ, случайная выборка", "th_wir": "этот эндпоинт",
    "c_abdeckung": "Охват", "c_richtig": "Точность возвращённого",
    "c_falsch": "Ошибочные записи", "c_median": "Медиана на источник",
    "vergleich_2": (
        "Citoid чаще возвращает хоть какую-то запись (14 против 11) и достаёт до MDPI, PeerJ и ОЭСР, "
        "которые отказывают этому эндпоинту. Зато от него пришли три ошибочных значения, среди них "
        "„Redirect URL“ в качестве заглавия работы. В списке литературы ошибочная запись дороже пробела: "
        "пробел вы видите, пока пишете, а ошибочную запись находит тот, кто оценивает работу."),
    "h_selbst": "5. Что остаётся за вами",
    "s_1": (
        "<strong>Смотреть на флаг полноты, а не на заглавие.</strong> Статистический портал вернул "
        "„Forschung, Innovation, Digitalisierung“ с автором STATISTIK AUSTRIA — выглядело готовым и было "
        "помечено как неполное."),
    "s_2": (
        "<strong>Страницы за входом, к которому у вас есть доступ:</strong> откройте их в своём браузере и "
        "сохраните там. Внешний сервер их прочитать не может, расширение в вашем сеансе — может."),
    "s_3": (
        "<strong>Газетные статьи, страницы статистики и «серую» литературу</strong> описывайте сами: эти "
        "страницы отвечали полностью и всё же не сообщали того, что нужно для записи: где-то не было автора, где-то года."),
    "s_4": (
        "<strong>Хранить копию, соответствующую дате обращения</strong> — в виде PDF или, для открытых "
        f'страниц, через <a href="{_Q["spn"]}">Save Page Now</a> в Internet Archive, который создаёт '
        "датированную ссылку, доступную для проверки любому читателю."),
    "h_grenzen": "Ограничения",
    "grenzen": (
        "Каждая цифра получена в одном прогоне в указанный день августа 2026 г.; страницы и платформы "
        "меняются, и прогон сегодня может дать другой результат. Измерение платформ выполнялось с выхода "
        "коммерческого VPN, а не с домашней линии. Новых цифр эта страница не вводит — она сводит "
        "указанные измерения."),
    "fuss": (
        "Опубликовано 23 октября 2026 г. Каждая цифра ведёт к исходным данным в "
        '<a href="/data/">/data/</a>, CC BY 4.0. Исправления — через GitHub issues.'),
    "disclaimer": "Отказ от ответственности",
}

# ---------------------------------------------------------------- 简体中文 ---
_T["zh-CN"] = {
    "h1": "访问日期与参考文献：引用网络来源，靠测量而非断言",
    "standfirst": (
        "为什么参考文献里要写访问日期（德语 Abrufdatum）、编制参考文献时工具能替你分担多少、又在哪里把工作"
        "交还给你 —— 本页汇总了本站有关引用的测量。每个数字都带有日期，并链接到原始数据。"),
    "meta": "截至 2026 年 10 月 23 日 · 以德语版为底本的摘要 · 测量时间为 2026 年 8 月 2 日至 18 日",
    "hinweis": (
        "这是个人的非商业报告，不是法律建议，也不是大学的指引。采用哪种引用格式、访问日期怎样书写，由你所在的"
        "院系决定；其规定优先于本页的一切内容。披露：作者开发了 "
        f'<a href="{_Q["tool"]}">Full Page PDF Snap</a>，下文把它作为几种手段之一提及。'),
    "h_wozu": "1. 访问日期有什么用",
    "wozu_1": (
        "网络来源不是书：被引用之后，它可能被修改、移动或删除。访问日期表明<em>那一天那里写的是这些</em>。"
        "它有多重要，2026 年 8 月 2 日的一份样本可以说明：从德语维基百科经济与社会政策条目的参考资料中抽取 "
        "150 个来源，每个服务器最多一个。"),
    "th_befund": "结果", "th_anteil": "比例",
    "v_weg": "服务器表示页面已删除（HTTP 404 或 410）",
    "v_ohne": "Internet Archive 中没有任何副本",
    "v_beides": "已删除且从未存档 —— 无法恢复",
    "v_alter": "最新存档副本的时间间隔（中位数）",
    "tage": "天",
    "wozu_2": (
        "维基百科的参考资料有人维护，因此这些数值偏于乐观。即使存在存档副本，其中位数也是 603 天前的 —— "
        "往往不是你读到的那个版本。仅有日期并不能让论断可核查，为此需要一份副本。结论：在引用的那一刻就保存来源，"
        "而不是等到论文结尾。"),
    "messung": "测量", "rohdaten": "原始数据",
    "h_form": "2. 访问日期在条目中如何呈现",
    "form_1": (
        "格式由引用规范决定 —— APA、Harvard、DIN 1505-2 和 ISO 690 各不相同，德语条目用„abgerufen am“连接。"
        "Full Page PDF Snap 会在每个 PDF 旁边放一个以 <code>.zitate.txt</code> 结尾的文件：APA 7、MLA 9、"
        "Chicago、Harvard、DIN 1505-2 和 ISO 690 各一行现成条目，另附 BibTeX 以及供 Citavi、Zotero 和 "
        "EndNote 使用的 RIS 记录。在 RIS 记录中，访问日期按 Citavi 和 EndNote 能导入的格式书写，并带有时间 —— "
        "页面在一天之内也会变化："),
    "form_2": (
        "如果页面没有给出出版年份，条目中写的是„o. J.“（无年份），而不是访问的年份。编造的年份比一眼可见的空缺代价更高。"),
    "h_liste": "3. 编制参考文献：机器能替你做什么",
    "liste_1": (
        "两项测量提出了同一个问题：仅凭页面对自身的声明，有多少来源无需手动输入就能成为完整的文献记录？"
        "测量使用本站的引用端点（<code>extract_citation</code>），每次的样本都在运行前确定。"),
    "th_lauf": "运行", "th_datum": "日期", "th_voll": "完整", "th_je": "每个来源",
    "l_liste1": "一篇课程论文的阅读清单，20 个来源",
    "l_liste2": "同样的 20 个，推导出标识符（DOI、CELEX）",
    "l_de1": "11 个德语平台",
    "l_de2": "同样的 11 个，使用各平台自己的接口",
    "d_03": "2026 年 8 月 3 日", "d_04": "2026 年 8 月 4 日",
    "liste_2": (
        "能够读取的是出版平台 Springer Link 和 Nomos eLibrary、仓储 PsychArchives 和 peDOCS，以及通过 SRU "
        "接口读取的德国国家图书馆。被退回的有：需要登录的授权数据库（beck-online）、只有案号而没有标题的页面"
        "（openJur）、两个没有年份的统计门户（Statistik Austria、Destatis）、拒绝该端点的仓储（OPUS 4），"
        "以及位于访问屏障之后、作为对照的 SSOAR。"),
    "liste_3": "缺少信息时，记录会被标为“不完整”返回，而不是去猜年份。",
    "h_vergleich": "4. 对比 —— 以及替代方案领先之处",
    "vergleich_1": (
        "2026 年 8 月 2 日，从 OpenAlex 随机抽取的 18 部作品分别经过了本端点和 Citoid —— 后者是 Wikimedia "
        "基于 Zotero 翻译器构建的服务。"),
    "th_18": "随机抽取的 18 部作品", "th_wir": "本端点",
    "c_abdeckung": "覆盖率", "c_richtig": "返回内容的准确率",
    "c_falsch": "错误记录", "c_median": "每个来源的中位数",
    "vergleich_2": (
        "Citoid 更常返回某种记录（14 比 11），并能访问拒绝本端点的 MDPI、PeerJ 和经合组织（OECD）。代价是它返回了"
        "三条错误数据，其中包括把„Redirect URL“当作作品标题。在参考文献里，错误条目比空缺代价更高：空缺你在写作时"
        "就能看到，错误条目则由评阅论文的人发现。"),
    "h_selbst": "5. 仍需你自己完成的事",
    "s_1": (
        "<strong>看“完整”标记，而不是看标题。</strong>一个统计门户以 STATISTIK AUSTRIA 为作者返回了"
        "„Forschung, Innovation, Digitalisierung“ —— 看上去已经完成，实际被标为不完整。"),
    "s_2": (
        "<strong>你有权访问的登录后页面：</strong>在你自己的浏览器中打开并在那里保存。外部服务器读不到它们，"
        "而你会话中的扩展可以。"),
    "s_3": (
        "<strong>报纸文章、统计页面和灰色文献：</strong>自己填写著录信息。这些页面完整地作出了响应，却没有声明一条记录所需的信息："
        "有的缺作者，有的缺年份。"),
    "s_4": (
        "<strong>保存与访问日期对应的副本</strong> —— 保存为 PDF；如果是公开页面，也可以用 Internet Archive 的 "
        f'<a href="{_Q["spn"]}">Save Page Now</a>，它会生成任何读者都能核查的带日期链接。'),
    "h_grenzen": "局限",
    "grenzen": (
        "每个数字都来自 2026 年 8 月某个指定日期的一次运行；页面和平台会变化，今天再运行结果可能不同。平台测量是从"
        "商用 VPN 出口进行的，而不是家庭宽带。本页没有引入新的数字 —— 它汇总的是所链接的测量。"),
    "fuss": (
        "发布于 2026 年 10 月 23 日。每个数字都链接到 <a href=\"/data/\">/data/</a> 下的原始数据，"
        "CC BY 4.0。更正请提交 GitHub issues。"),
    "disclaimer": "免责声明",
}

# Jede Sprache traegt den FERTIGEN Rumpf. Leere Eintraege verhindern den Bau.
INHALT = {l: _seite(l, _T[l]) for l in SPRACHEN}

# Fuer das Verzeichnis /how-to/ (texte_indexseiten.py) und den Seitenkopf.
TITEL = {l: _T[l]["h1"] for l in SPRACHEN}
VORSPANN = {l: _T[l]["standfirst"] for l in SPRACHEN}
