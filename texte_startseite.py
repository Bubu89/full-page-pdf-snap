#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Startseite in neun Sprachen — getrennt vom Bauen der Seite.

Muster wie texte_artikel_studierende.py: ENGLISCH ist die Ausgangsfassung,
alle Sprachen landen als data-lang-Bloecke in derselben docs/index.html.
Rendering ueber build-startseite.py, Kopf und Navigation kommen aus der
bestehenden Seite.

WICHTIG — neuer Arbeitsweg: Wer einen Beitrag auf der Startseite eintraegt
(Notes/Messungen/Tools) oder Texte aendert, tut das HIER und baut mit
build-startseite.py neu. docs/index.html nicht mehr von Hand editieren —
der naechste Lauf des Bauers ueberschreibt es. Ein neuer Eintrag braucht
alle neun Sprachen, sonst fehlt er in acht Fassungen still.

Datumsangaben in den Eintraegen sind lokalisiert ("15 August 2026" vs.
"15. August 2026"); Zahlenformate folgen der Sprache (Komma/Punkt).
"""

URL = "https://provinglab.dev/"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "h1": "Keep the web page you will need later.",
    "tagline1": (
        'Save a whole page as one PDF that carries where it came from and when — and turn a\n'
        '      list of links into a reference list. <strong>19.3 % of sources in real bibliographies\n'
        '      are already gone</strong>, and 8.7 % have no archived copy anywhere.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Start here</a> ·\n'
        '      <a href="/for-agents/">for AI agents</a>'
    ),
    "tagline2": (
        'Measurements, not opinions: everything here has a <strong>method, raw data and a\n'
        '      control run</strong>. Where a number cannot be reproduced, it does not get written\n'
        '      down. Where something went wrong, that is written down first.'
    ),
    "dmark": "The tool built here",
    "dtext": (
        "Save a whole webpage as one continuous PDF — the entire scrolling page on a single "
        "sheet. Nothing cropped at the edge, and no page break cutting through a table or a "
        "sentence. Everything happens in your browser: no upload, no account, no data "
        "collection. MIT licensed, free of charge, Firefox and Chrome."
    ),
    "dzahlen": [
        "<b>One sheet</b>, not 26 pages",
        "<b>Works behind a login</b>",
        "<b>Stays on your device</b>",
    ],
    "dbeleg": (
        'Every claim here is measured and dated:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">one sheet against 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92.6&nbsp;% of the text readable by OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">zero network requests</a>.'
    ),
    "ddownload": "Download for Firefox",
    "dversion": "Version 2.33.4 — signed by Mozilla. Installs in one step, desktop and Android.",
    "dohne": "Without any store",
    "dchrome": "Chrome and Edge",
    "dwas": "What it does",
    "notes_h2": "Notes",
    "notes_sub": "Build reports from real work — including the parts that went wrong.",
    "notes": [
        {
            "date": "15 August 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "For researchers and students: the add-on in Firefox and Chrome",
            "text": (
                "The practical companion to the students piece: every install route — Firefox on\n"
                "          desktop and Android, the Chrome Web Store, and both store-free paths — then the\n"
                "          capture–cite–archive workflow and the four settings that matter for papers. In\n"
                "          nine languages."
            ),
            "figures": [
                "<b>2</b> browsers, 4 install routes",
                "<b>18</b> XMP fields in the PDF",
                "<b>2</b> ways the RIS record travels",
            ],
        },
        {
            "date": "10 August 2026",
            "href": "how-to/for-students/",
            "title": "For students: a source that cites itself, survives, and can be read by a machine",
            "text": (
                "Three things go wrong with a web source in a term paper: it disappears, its\n"
                "          citation has to be typed by hand, and the file you kept is a picture no tool\n"
                "          can search. What a capture does about each — including the six sources in\n"
                "          twenty it hands straight back to you. In nine languages."
            ),
            "figures": [
                "<b>61 %</b> coverage, same as Citoid",
                "<b>100 %</b> accurate against its 79 %",
                "<b>6 of 20</b> handed back",
            ],
        },
        {
            "date": "3 August 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "What an AI agent can and cannot do with a browser extension",
            "text": (
                "Installing one into someone's browser is a user gesture by design — no store\n"
                "          exposes an API for it. What an agent can do instead, the command-line flag that\n"
                "          loads nothing and says nothing, and where the work divides between the two."
            ),
            "figures": [
                "<b>3</b> things an agent can do",
                "<b>1</b> flag that fails silently",
                "<b>0</b> ways to install for someone",
            ],
        },
        {
            "date": "3 August 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "The sources a machine cannot cite for you — and how to cite them anyway",
            "text": (
                "When a citation tool hands a source back, the cause is one of three: a bot defence,\n"
                "          a refusal aimed at the network, or a page that declares nothing about itself. Each\n"
                "          needs different work, and only one is solved by opening the page in a browser."
            ),
            "figures": [
                "<b>3</b> causes",
                "<b>1</b> solved by a browser",
                "<b>2</b> requests to tell them apart",
            ],
        },
        {
            "date": "2 August 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "This site runs an MCP server. Measured: it is smaller than the file it competes with",
            "text": (
                "An endpoint at <code>/mcp</code> hands the datasets, the methods and a citation\n"
                "          reader to AI clients over JSON-RPC — no key, no account. What that is actually\n"
                "          good for, and where a plain text file on the same domain already does the job."
            ),
            "figures": [
                "<b>4</b> tools",
                "<b>1,300</b> tokens total",
                "<b>1,988</b> in llms.txt",
            ],
        },
        {
            "date": "1 August 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Six things went wrong building software with an AI assistant in one day",
            "text": (
                "A wrong assumption about browser engines, a false claim caught before publication,\n"
                "          22 local paths one commit from a public repository, and three more. Sorted by what\n"
                "          actually caught them — two were caught by luck, one by nothing at all."
            ),
            "figures": [
                "<b>3 of 6</b> caught by checking an external source",
                "<b>1</b> still untested in production",
            ],
        },
    ],
    "meas_h2": "Measurements",
    "meas_sub": "Each with the commands to repeat it and the raw data behind it.",
    "meas": [
        {
            "date": "3 August 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Installing a browser extension without a click, and removing it again",
            "text": (
                "Four routes, both directions. One installs and uninstalls a signed store build in\n"
                "          4.1 seconds with no window and no admin rights — and the two commands themselves\n"
                "          take 0.24 s, so the cost is starting the browser, not the work. The click route\n"
                "          took 179 seconds, reported success at every step, and installed nothing: a click\n"
                "          into empty space is a valid click. The fast route does not count in the store's\n"
                "          user statistics, and that is the point rather than the flaw."
            ),
            "figures": [],
        },
        {
            "date": "3 August 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Twenty links, ten citations: what a machine finishes and what it hands back",
            "text": (
                "A reading list into a bibliography, end to end. The split does not run between paid\n"
                "          and free — it runs between pages built to be cited and pages built to be read.\n"
                "          Journal publishers yield records either way; statistics portals, chambers of\n"
                "          commerce and newspapers yield none, and not because they defend themselves."
            ),
            "figures": [
                "<b>10/20</b> complete records",
                "<b>1</b> bot defence",
                "<b>5</b> pages with nothing to declare",
            ],
        },
        {
            "date": "3 August 2026",
            "href": "measurements/citation-triage/",
            "title": "An agent can cite eight of twelve sources — the useful part is knowing which four it cannot",
            "text": (
                "A mixed reading list through the citation endpoint: complete records with RIS for\n"
                "          two thirds, and the rest named precisely enough to fetch by hand instead of\n"
                "          invented."
            ),
            "figures": [
                "<b>8/12</b> done by the agent",
                "<b>1.09 s</b> per source",
                "<b>4</b> named, not guessed",
            ],
        },
        {
            "date": "2 August 2026",
            "href": "measurements/citation-extraction/",
            "title": "Measured against Citoid on random samples: same coverage, nothing invented",
            "text": (
                "The Wikimedia service built on the Zotero translators is the yardstick. Across\n"
                "          18 works drawn at random: equal coverage, and not one refusal reported as a\n"
                "          success."
            ),
            "figures": [
                "<b>13/13</b> fields complete",
                "<b>0</b> false block reports",
                "<b>0.35 s</b> median",
            ],
        },
        {
            "date": "1 August 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Print to PDF or capture the screen? The same page measured both ways",
            "text": (
                "Firefox already saves pages as PDF for free. So when is a capture worth it? The same\n"
                "          article through both routes — and the answer is narrower, and more useful, than either\n"
                "          side usually admits."
            ),
            "figures": [
                "<b>1 : 26</b> pages",
                "<b>9</b> breaks cut a sentence",
                "capture leads on text: <b>91.5 %</b>",
            ],
        },
        {
            "date": "1 August 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Webpage to PDF for OCR: how much text actually survives?",
            "text": (
                "A full-page screenshot PDF run through Tesseract and compared against the source\n"
                "          article. Includes the resolution threshold where recognition collapses."
            ),
            "figures": [
                "<b>92.6 %</b> vocabulary recovered",
                "<b>8/8</b> critical values",
                "<b>72 dpi</b> collapse point",
            ],
        },
        {
            "date": "1 August 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "Does your PDF extension upload the page?",
            "text": (
                "What current PDF extensions declare in their manifests, how to verify it in\n"
                "          30 seconds — and the consequence nobody mentions: server-side converters cannot\n"
                "          reach pages behind a login."
            ),
            "figures": [
                "<b>8</b> extensions surveyed",
                "raw data published",
            ],
        },
        {
            "date": "1 August 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "An extension is only as dangerous as its permissions allow",
            "text": (
                "One year after Mozilla warned about phished developer accounts: why the useful\n"
                "          question is not who you trust, but what a compromised extension could reach."
            ),
            "figures": [
                "worst-case permission table",
                "assessment checklist",
            ],
        },
    ],
    "prinzip_h2": "How things are measured here",
    "prinzipien": [
        ("A control run, always",
         "Before any result counts, the method has to fail where it should. A comparison that\n"
         "          does not distinguish the reference case measures nothing."),
        ("Raw data published",
         "Numbers come with the file they were computed from, timestamped. That makes them\n"
         "          checkable — and it means nobody has to take a claim on trust."),
        ("Losses named first",
         "Where our own tool is worse — file size, processing time, missing features — it is\n"
         "          stated before the advantages. A comparison that only flatters is worthless."),
        ("Dated, not timeless",
         "Every figure carries the date it was retrieved. Software changes; a measurement\n"
         "          without a date quietly turns into a false claim."),
    ],
    "tools_h2": "Tools",
    "tools_sub": (
        "Software built here, documented like anything else on this site — including what it\n"
        "      cannot do. It appears in some of the measurements above; that is disclosed on each of them."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Firefox extension that saves a whole web page as one continuous PDF. Runs on the\n"
                "          device, asks for <code>activeTab</code> rather than all-sites access, works on\n"
                "          Firefox for Android. MIT licensed. Optionally writes the citation the page\n"
                "          declares — authors, DOI, licence, time of retrieval — into the PDF, with an RIS\n"
                "          record beside it."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Citation endpoint at <code>/mcp</code>",
            "text": (
                "Hand it a URL, get back what that page says about itself as a structured record\n"
                "          with RIS and BibTeX — or a named refusal where the page turns out to be a paywall,\n"
                "          an error or a bot check rather than a work. No account and no key. Speaks MCP for\n"
                "          AI clients and plain HTTP for everything else."
            ),
            "figures": [
                "<b>7 of 10</b> scholarly sources complete",
                "<b>0.45 s</b> median",
                "<b>3 Aug 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Recipes: a reading list into a reference list",
            "text": (
                "Complete, runnable instructions for putting the citation endpoint into the tools\n"
                "          people actually work in: a shell loop that turns <code>reading-list.txt</code> into\n"
                "          one importable <code>.ris</code> for Zotero or Citavi, one line to connect Claude\n"
                "          Code, the remote-server entry for Claude Desktop and other MCP clients, and the\n"
                "          Python minimum. Every one was run before it was written down."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Check any figure yourself",
    "nach_sub": (
        "Everything here has a method, raw data and a control run — so it can be checked,\n"
        "      not so it has to be believed."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "The most useful contribution is a counter-measurement that comes out differently",
            "text": (
                "Four places where the published figures are most likely to wobble are named\n"
                "          explicitly — starting with the ten of twenty sources whose four refusals are\n"
                "          blocks against a data-centre address. From a home network the rate should be\n"
                "          higher, and that is unmeasured."
            ),
            "figures": [
                "<b>4</b> named weak spots",
                "<b>9</b> datasets, CC BY 4.0",
                "open tasks on <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "For AI agents: rules, construction, limits",
            "text": (
                "The project is set up so an agent can work on it without asking anyone first.\n"
                "          Open tasks are served machine-readably by the <code>open_work</code> tool on\n"
                "          <a href=\"for-agents/\">/mcp</a> — with labels, an excerpt, and the five rules\n"
                "          that are different here from usual."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Disclosure",
    "disc_p1": (
        "This site is run by the developer of <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, which appears in several of the measurements above. That is stated in\n"
        "        each article where it is relevant, and the tool sits openly under\n"
        "        <code>/tools/</code> rather than hidden behind neutral framing."
    ),
    "disc_p2": (
        "Figures about other products come exclusively from publicly declared data — manifests\n"
        "        and listing descriptions — with the retrieval date given. No product was decompiled,\n"
        "        and no claim is made about any provider's intentions.\n"
        "        Corrections are welcome via\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">GitHub issues</a> and\n"
        "        get applied."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">About</a> · <a href="privacy.html">Privacy</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Source</a> · '
        '<a href="disclaimer/">Disclaimer</a>'
    ),
    "foot_2": "Content licensed for reuse with attribution. Software MIT licensed.",
}

# ---------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "h1": "Behalten Sie die Webseite, die Sie später brauchen.",
    "tagline1": (
        'Speichern Sie eine ganze Seite als ein PDF, das Herkunft und Abrufzeitpunkt trägt —\n'
        '      und verwandeln Sie eine Linkliste in ein Literaturverzeichnis. <strong>19,3 % der Quellen\n'
        '      in echten Literaturverzeichnissen sind bereits verschwunden</strong>, und 8,7 % haben\n'
        '      nirgends eine archivierte Kopie.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Hier beginnen</a> ·\n'
        '      <a href="/for-agents/">für KI-Agenten</a>'
    ),
    "tagline2": (
        'Messungen, keine Meinungen: Alles hier hat eine <strong>Methode, Rohdaten und einen\n'
        '      Kontrolllauf</strong>. Was sich nicht nachrechnen lässt, wird nicht aufgeschrieben.\n'
        '      Was schiefging, wird zuerst aufgeschrieben.'
    ),
    "dmark": "Das hier gebaute Werkzeug",
    "dtext": (
        "Speichert eine ganze Webseite als ein fortlaufendes PDF — die komplette scrollende "
        "Seite auf einem einzigen Blatt. Nichts am Rand abgeschnitten, kein Seitenumbruch "
        "mitten durch Tabelle oder Satz. Alles passiert in Ihrem Browser: kein Upload, kein "
        "Konto, keine Datenerhebung. MIT-lizenziert, kostenlos, Firefox und Chrome."
    ),
    "dzahlen": [
        "<b>Ein Blatt</b>, nicht 26 Seiten",
        "<b>Funktioniert hinter einem Login</b>",
        "<b>Bleibt auf Ihrem Gerät</b>",
    ],
    "dbeleg": (
        'Jede Aussage hier ist gemessen und datiert:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">ein Blatt gegen 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92,6&nbsp;% des Textes per OCR lesbar</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">null Netzwerkanfragen</a>.'
    ),
    "ddownload": "Für Firefox herunterladen",
    "dversion": "Version 2.33.4 — von Mozilla signiert. Installiert in einem Schritt, Desktop und Android.",
    "dohne": "Ganz ohne Store",
    "dchrome": "Chrome und Edge",
    "dwas": "Was sie kann",
    "notes_h2": "Notizen",
    "notes_sub": "Bauberichte aus echter Arbeit — einschließlich der Teile, die schiefgingen.",
    "notes": [
        {
            "date": "15. August 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "Für Wissenschaftler:innen und Studierende: die Erweiterung in Firefox und Chrome",
            "text": (
                "Das praktische Gegenstück zum Studierenden-Beitrag: alle Installationswege —\n"
                "          Firefox auf Desktop und Android, der Chrome Web Store und beide store-freien\n"
                "          Pfade —, dann der Ablauf aufnehmen–zitieren–archivieren und die vier\n"
                "          Einstellungen, die für Arbeiten zählen. In neun Sprachen."
            ),
            "figures": [
                "<b>2</b> Browser, 4 Installationswege",
                "<b>18</b> XMP-Felder im PDF",
                "<b>2</b> Wege für den RIS-Datensatz",
            ],
        },
        {
            "date": "10. August 2026",
            "href": "how-to/for-students/",
            "title": "Für Studierende: eine Quelle, die sich selbst zitiert, überlebt und maschinenlesbar ist",
            "text": (
                "Drei Dinge gehen mit einer Webquelle in einer Seminararbeit schief: Sie verschwindet,\n"
                "          ihre Zitation muss von Hand abgetippt werden, und die aufgehobene Datei ist ein\n"
                "          Bild, das kein Werkzeug durchsucht. Was eine Aufnahme gegen jedes der drei tut —\n"
                "          einschließlich der sechs von zwanzig Quellen, die sie an Sie zurückgibt. In neun\n"
                "          Sprachen."
            ),
            "figures": [
                "<b>61 %</b> Abdeckung, gleichauf mit Citoid",
                "<b>100 %</b> richtig gegenüber deren 79 %",
                "<b>6 von 20</b> zurückgegeben",
            ],
        },
        {
            "date": "3. August 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "Was ein KI-Agent mit einer Browser-Erweiterung kann — und was nicht",
            "text": (
                "Eine Installation in fremdem Browser ist bewusst eine Nutzer-Geste — kein Store\n"
                "          bietet eine API dafür. Was ein Agent stattdessen kann, der Kommandozeilen-Schalter,\n"
                "          der nichts lädt und nichts sagt, und wo die Arbeit zwischen beiden aufgeteilt ist."
            ),
            "figures": [
                "<b>3</b> Dinge, die ein Agent kann",
                "<b>1</b> Schalter, der still versagt",
                "<b>0</b> Wege, für jemanden zu installieren",
            ],
        },
        {
            "date": "3. August 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "Die Quellen, die eine Maschine nicht für Sie zitieren kann — und wie man sie trotzdem zitiert",
            "text": (
                "Wenn ein Zitationswerkzeug eine Quelle zurückgibt, ist die Ursache eine von dreien:\n"
                "          eine Bot-Abwehr, eine Weigerung gegen das Netzwerk oder eine Seite, die nichts\n"
                "          über sich erklärt. Jede braucht andere Arbeit, und nur eine löst das Öffnen im Browser."
            ),
            "figures": [
                "<b>3</b> Ursachen",
                "<b>1</b> durch einen Browser gelöst",
                "<b>2</b> Anfragen zur Unterscheidung",
            ],
        },
        {
            "date": "2. August 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Diese Seite betreibt einen MCP-Server. Gemessen: Er ist kleiner als die Datei, mit der er konkurriert",
            "text": (
                "Ein Endpunkt unter <code>/mcp</code> reicht die Datensätze, die Methoden und einen\n"
                "          Zitationsleser über JSON-RPC an KI-Clients — kein Schlüssel, kein Konto. Wozu das\n"
                "          wirklich taugt, und wo eine schlichte Textdatei auf derselben Domain die Aufgabe\n"
                "          schon erledigt."
            ),
            "figures": [
                "<b>4</b> Werkzeuge",
                "<b>1.300</b> Token insgesamt",
                "<b>1.988</b> in llms.txt",
            ],
        },
        {
            "date": "1. August 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Sechs Dinge, die beim Bauen von Software mit einem KI-Assistenten an einem Tag schiefgingen",
            "text": (
                "Eine falsche Annahme über Browser-Engines, eine vor Veröffentlichung erwischte\n"
                "          Falschbehauptung, 22 lokale Pfade einen Commit vor einem öffentlichen Repository —\n"
                "          und drei weitere. Sortiert danach, was sie tatsächlich erwischt hat: zwei wurden\n"
                "          durch Glück gefunden, eine durch gar nichts."
            ),
            "figures": [
                "<b>3 von 6</b> durch Prüfen einer externen Quelle erwischt",
                "<b>1</b> noch immer ungetestet im Produktivbetrieb",
            ],
        },
    ],
    "meas_h2": "Messungen",
    "meas_sub": "Jede mit den Befehlen zu ihrer Wiederholung und den Rohdaten dahinter.",
    "meas": [
        {
            "date": "3. August 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Eine Browser-Erweiterung ohne Klick installieren — und wieder entfernen",
            "text": (
                "Vier Wege, beide Richtungen. Einer installiert und deinstalliert eine signierte\n"
                "          Store-Version in 4,1 Sekunden ohne Fenster und ohne Admin-Rechte — und die zwei\n"
                "          Befehle selbst brauchen 0,24 s; die Kosten sind der Browser-Start, nicht die Arbeit.\n"
                "          Der Klick-Weg brauchte 179 Sekunden, meldete bei jedem Schritt Erfolg und\n"
                "          installierte nichts: Ein Klick ins Leere ist ein gültiger Klick. Der schnelle Weg\n"
                "          zählt nicht in den Nutzerstatistiken des Stores — und das ist der Punkt, nicht der Fehler."
            ),
            "figures": [],
        },
        {
            "date": "3. August 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Zwanzig Links, zehn Zitationen: was eine Maschine fertig macht und was sie zurückgibt",
            "text": (
                "Eine Leseliste in ein Literaturverzeichnis, von Anfang bis Ende. Die Trennlinie läuft\n"
                "          nicht zwischen kostenpflichtig und frei — sie läuft zwischen Seiten, die zum\n"
                "          Zitieren gebaut sind, und Seiten, die zum Lesen gebaut sind. Fachverlage liefern\n"
                "          Datensätze in beiden Fällen; Statistikportale, Kammern und Zeitungen liefern keine,\n"
                "          und nicht, weil sie sich verteidigen."
            ),
            "figures": [
                "<b>10/20</b> vollständige Datensätze",
                "<b>1</b> Bot-Abwehr",
                "<b>5</b> Seiten ohne etwas zu erklären",
            ],
        },
        {
            "date": "3. August 2026",
            "href": "measurements/citation-triage/",
            "title": "Ein Agent kann acht von zwölf Quellen zitieren — der nützliche Teil ist zu wissen, welche vier er nicht kann",
            "text": (
                "Eine gemischte Leseliste durch den Zitations-Endpunkt: vollständige Datensätze mit\n"
                "          RIS für zwei Drittel, und der Rest präzise genug benannt, um ihn von Hand zu holen\n"
                "          statt zu erfinden."
            ),
            "figures": [
                "<b>8/12</b> vom Agenten erledigt",
                "<b>1,09 s</b> pro Quelle",
                "<b>4</b> benannt, nicht geraten",
            ],
        },
        {
            "date": "2. August 2026",
            "href": "measurements/citation-extraction/",
            "title": "Gegen Citoid an Zufallsstichproben gemessen: gleiche Abdeckung, nichts erfunden",
            "text": (
                "Der Wikimedia-Dienst auf Basis der Zotero-Translatoren ist der Maßstab. Über 18\n"
                "          zufällig gezogene Werke: gleiche Abdeckung, und keine einzige Weigerung als\n"
                "          Erfolg gemeldet."
            ),
            "figures": [
                "<b>13/13</b> Felder vollständig",
                "<b>0</b> falsche Sperr-Meldungen",
                "<b>0,35 s</b> Median",
            ],
        },
        {
            "date": "1. August 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Als PDF drucken oder den Bildschirm aufnehmen? Dieselbe Seite, beide Wege gemessen",
            "text": (
                "Firefox speichert Seiten bereits kostenlos als PDF. Wann lohnt also eine Aufnahme?\n"
                "          Derselbe Artikel durch beide Wege — und die Antwort ist enger und nützlicher,\n"
                "          als beide Seiten üblicherweise zugeben."
            ),
            "figures": [
                "<b>1 : 26</b> Seiten",
                "<b>9</b> Umbrüche durchtrennen einen Satz",
                "Aufnahme führt beim Text: <b>91,5 %</b>",
            ],
        },
        {
            "date": "1. August 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Webseite als PDF für OCR: Wie viel Text überlebt tatsächlich?",
            "text": (
                "Ein Ganzseiten-Screenshot-PDF durch Tesseract, verglichen mit dem Ursprungsartikel.\n"
                "          Einschließlich der Auflösungsschwelle, an der die Erkennung einbricht."
            ),
            "figures": [
                "<b>92,6 %</b> Wortschatz zurückgewonnen",
                "<b>8/8</b> kritische Werte",
                "<b>72 dpi</b> Einbruchstelle",
            ],
        },
        {
            "date": "1. August 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "Lädt Ihre PDF-Erweiterung die Seite hoch?",
            "text": (
                "Was aktuelle PDF-Erweiterungen in ihren Manifesten deklarieren, wie man es in\n"
                "          30 Sekunden überprüft — und die Folge, die niemand erwähnt: Server-seitige\n"
                "          Konverter erreichen keine Seiten hinter einem Login."
            ),
            "figures": [
                "<b>8</b> Erweiterungen untersucht",
                "Rohdaten veröffentlicht",
            ],
        },
        {
            "date": "1. August 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "Eine Erweiterung ist nur so gefährlich, wie ihre Berechtigungen es erlauben",
            "text": (
                "Ein Jahr nach Mozillas Warnung vor erbeuteten Entwicklerkonten: Warum die nützliche\n"
                "          Frage nicht ist, wem Sie vertrauen, sondern was eine kompromittierte Erweiterung\n"
                "          erreichen könnte."
            ),
            "figures": [
                "Worst-Case-Berechtigungstabelle",
                "Bewertungs-Checkliste",
            ],
        },
    ],
    "prinzip_h2": "Wie hier gemessen wird",
    "prinzipien": [
        ("Ein Kontrolllauf, immer",
         "Bevor ein Ergebnis zählt, muss die Methode dort scheitern, wo sie scheitern soll. Ein\n"
         "          Vergleich, der den Referenzfall nicht unterscheidet, misst nichts."),
        ("Rohdaten veröffentlicht",
         "Zahlen kommen mit der Datei, aus der sie berechnet wurden, mit Zeitstempel. Das macht\n"
         "          sie prüfbar — und es heißt, niemand muss eine Behauptung auf Vertrauen hinnehmen."),
        ("Verluste zuerst genannt",
         "Wo das eigene Werkzeug schlechter ist — Dateigröße, Laufzeit, fehlende Funktionen —,\n"
         "          steht es vor den Vorteilen. Ein Vergleich, der nur schmeichelt, ist wertlos."),
        ("Datiert, nicht zeitlos",
         "Jede Zahl trägt das Datum ihrer Erhebung. Software ändert sich; eine Messung ohne\n"
         "          Datum wird still zur Falschbehauptung."),
    ],
    "tools_h2": "Werkzeuge",
    "tools_sub": (
        "Hier gebaute Software, dokumentiert wie alles auf dieser Seite — einschließlich dessen,\n"
        "      was sie nicht kann. Sie kommt in einigen der Messungen oben vor; das ist bei jeder offengelegt."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Firefox-Erweiterung, die eine ganze Webseite als ein fortlaufendes PDF speichert.\n"
                "          Läuft auf dem Gerät, fragt <code>activeTab</code> statt Zugriff auf alle Seiten an,\n"
                "          funktioniert auf Firefox für Android. MIT-lizenziert. Schreibt optional die Zitation,\n"
                "          die die Seite erklärt — Verfasser:innen, DOI, Lizenz, Abrufzeitpunkt — ins PDF,\n"
                "          mit einem RIS-Datensatz daneben."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Zitations-Endpunkt unter <code>/mcp</code>",
            "text": (
                "Geben Sie eine URL, bekommen Sie zurück, was diese Seite über sich selbst erklärt —\n"
                "          als strukturierten Datensatz mit RIS und BibTeX, oder eine benannte Weigerung,\n"
                "          wenn sich die Seite als Paywall, Fehler oder Bot-Prüfung entpuppt statt als Werk.\n"
                "          Kein Konto und kein Schlüssel. Spricht MCP für KI-Clients und schlichtes HTTP für\n"
                "          alles andere."
            ),
            "figures": [
                "<b>7 von 10</b> wissenschaftliche Quellen vollständig",
                "<b>0,45 s</b> Median",
                "<b>3. Aug 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Rezepte: eine Leseliste in ein Literaturverzeichnis",
            "text": (
                "Vollständige, lauffähige Anleitungen, um den Zitations-Endpunkt in die Werkzeuge zu\n"
                "          bringen, in denen tatsächlich gearbeitet wird: eine Shell-Schleife, die\n"
                "          <code>reading-list.txt</code> in eine importierbare <code>.ris</code> für Zotero oder\n"
                "          Citavi verwandelt, eine Zeile für Claude Code, der Remote-Server-Eintrag für Claude\n"
                "          Desktop und andere MCP-Clients und das Python-Minimum. Jedes wurde ausgeführt,\n"
                "          bevor es aufgeschrieben wurde."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Rechnen Sie eine Zahl nach",
    "nach_sub": (
        "Jede Angabe hier hat Methode, Rohdaten und einen Kontrolllauf — damit sie nachgerechnet\n"
        "      werden kann, nicht damit sie geglaubt wird."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "Der nützlichste Beitrag ist eine Gegenmessung, die etwas anderes ergibt",
            "text": (
                "Vier Stellen, an denen die veröffentlichten Zahlen am wahrscheinlichsten wackeln, sind\n"
                "          ausdrücklich benannt — angefangen bei den zehn von zwanzig Quellen, deren vier\n"
                "          Ablehnungen Sperren gegen eine Rechenzentrums-Adresse sind. Aus einem Heimnetz müsste\n"
                "          die Quote höher liegen, und gemessen ist das nicht."
            ),
            "figures": [
                "<b>4</b> benannte Schwachstellen",
                "<b>9</b> Datensätze, CC BY 4.0",
                "offene Aufgaben auf <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Für KI-Agenten: Regeln, Bauweise, Grenzen",
            "text": (
                "Das Projekt ist so eingerichtet, dass ein Agent daran arbeiten kann, ohne vorher\n"
                "          jemanden zu fragen. Offene Aufgaben liefert das Werkzeug <code>open_work</code> auf\n"
                "          <a href=\"for-agents/\">/mcp</a> maschinenlesbar aus — mit Labels, Auszug und den fünf\n"
                "          Regeln, die hier anders sind als üblich."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Offenlegung",
    "disc_p1": (
        "Diese Seite wird vom Entwickler von <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a> betrieben, das in mehreren der Messungen oben vorkommt. Das steht in jedem\n"
        "        Beitrag, in dem es relevant ist, und das Werkzeug steht offen unter\n"
        "        <code>/tools/</code>, statt hinter neutraler Rahmung versteckt."
    ),
    "disc_p2": (
        "Zahlen über fremde Produkte stammen ausschließlich aus öffentlich deklarierten Daten —\n"
        "        Manifesten und Store-Beschreibungen — mit angegebenem Abrufdatum. Kein Produkt wurde\n"
        "        dekompiliert, und keine Aussage wird über die Absichten eines Anbieters gemacht.\n"
        "        Korrekturen sind willkommen über\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">GitHub Issues</a> und\n"
        "        werden übernommen."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">Über</a> · <a href="privacy.html">Datenschutz</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Quelltext</a> · '
        '<a href="disclaimer/">Haftungsausschluss</a>'
    ),
    "foot_2": "Inhalte lizenziert zur Weiterverwendung mit Namensnennung. Software MIT-lizenziert.",
}

# --------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "h1": "Guarda la página web que necesitarás más tarde.",
    "tagline1": (
        'Guarda una página entera como un solo PDF que lleva su origen y su fecha — y convierte\n'
        '      una lista de enlaces en una bibliografía. <strong>El 19,3 % de las fuentes en\n'
        '      bibliografías reales ya ha desaparecido</strong>, y el 8,7 % no tiene copia archivada\n'
        '      en ningún sitio.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Empieza aquí</a> ·\n'
        '      <a href="/for-agents/">para agentes de IA</a>'
    ),
    "tagline2": (
        'Mediciones, no opiniones: todo aquí tiene <strong>método, datos brutos y una ejecución\n'
        '      de control</strong>. Lo que no se puede recalcular no se escribe. Lo que salió mal\n'
        '      se escribe primero.'
    ),
    "dmark": "La herramienta construida aquí",
    "dtext": (
        "Guarda una página web entera como un PDF continuo — toda la página desplazable en una "
        "sola hoja. Nada recortado en los bordes y ningún salto de página atravesando una tabla "
        "o una frase. Todo ocurre en tu navegador: sin subidas, sin cuenta, sin recolección de "
        "datos. Licencia MIT, gratuita, Firefox y Chrome."
    ),
    "dzahlen": [
        "<b>Una hoja</b>, no 26 páginas",
        "<b>Funciona tras un inicio de sesión</b>",
        "<b>Se queda en tu dispositivo</b>",
    ],
    "dbeleg": (
        'Cada afirmación aquí está medida y fechada:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">una hoja contra 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">el 92,6&nbsp;% del texto legible por OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">cero peticiones de red</a>.'
    ),
    "ddownload": "Descargar para Firefox",
    "dversion": "Versión 2.33.4 — firmada por Mozilla. Se instala en un paso, escritorio y Android.",
    "dohne": "Sin ninguna tienda",
    "dchrome": "Chrome y Edge",
    "dwas": "Qué hace",
    "notes_h2": "Notas",
    "notes_sub": "Crónicas de trabajo real — incluidas las partes que salieron mal.",
    "notes": [
        {
            "date": "15 de agosto de 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "Para investigadores y estudiantes: la extensión en Firefox y Chrome",
            "text": (
                "El complemento práctico del artículo para estudiantes: todas las vías de\n"
                "          instalación — Firefox en escritorio y Android, la Chrome Web Store y ambos\n"
                "          caminos sin tienda —, luego el flujo capturar–citar–archivar y los cuatro\n"
                "          ajustes que importan para los trabajos. En nueve idiomas."
            ),
            "figures": [
                "<b>2</b> navegadores, 4 vías de instalación",
                "<b>18</b> campos XMP en el PDF",
                "<b>2</b> caminos para el registro RIS",
            ],
        },
        {
            "date": "10 de agosto de 2026",
            "href": "how-to/for-students/",
            "title": "Para estudiantes: una fuente que se cita sola, sobrevive y es legible por máquina",
            "text": (
                "Tres cosas fallan con una fuente web en un trabajo académico: desaparece, su cita\n"
                "          hay que teclearla a mano, y el archivo guardado es una imagen que ninguna\n"
                "          herramienta busca. Qué hace una captura contra cada una — incluidas las seis\n"
                "          fuentes de veinte que te devuelve. En nueve idiomas."
            ),
            "figures": [
                "<b>61 %</b> de cobertura, igual que Citoid",
                "<b>100 %</b> correcto frente a su 79 %",
                "<b>6 de 20</b> devueltas",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "Qué puede y qué no puede hacer un agente de IA con una extensión de navegador",
            "text": (
                "Instalar una en el navegador de alguien es un gesto de usuario por diseño — ninguna\n"
                "          tienda expone una API para ello. Qué puede hacer un agente en su lugar, el flag\n"
                "          de línea de comandos que no carga nada y no dice nada, y dónde se divide el\n"
                "          trabajo entre ambos."
            ),
            "figures": [
                "<b>3</b> cosas que un agente puede hacer",
                "<b>1</b> flag que falla en silencio",
                "<b>0</b> formas de instalar para otro",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "Las fuentes que una máquina no puede citar por ti — y cómo citarlas igualmente",
            "text": (
                "Cuando una herramienta de citación devuelve una fuente, la causa es una de tres:\n"
                "          una defensa contra bots, una negativa dirigida a la red o una página que no\n"
                "          declara nada de sí misma. Cada una necesita un trabajo distinto, y solo una se\n"
                "          resuelve abriendo la página en un navegador."
            ),
            "figures": [
                "<b>3</b> causas",
                "<b>1</b> resuelta con un navegador",
                "<b>2</b> peticiones para distinguirlas",
            ],
        },
        {
            "date": "2 de agosto de 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Este sitio opera un servidor MCP. Medido: es más pequeño que el archivo con el que compite",
            "text": (
                "Un endpoint en <code>/mcp</code> entrega los conjuntos de datos, los métodos y un\n"
                "          lector de citas a clientes de IA por JSON-RPC — sin clave, sin cuenta. Para qué\n"
                "          sirve realmente, y dónde un simple archivo de texto en el mismo dominio ya\n"
                "          hace el trabajo."
            ),
            "figures": [
                "<b>4</b> herramientas",
                "<b>1.300</b> tokens en total",
                "<b>1.988</b> en llms.txt",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Seis cosas salieron mal construyendo software con un asistente de IA en un día",
            "text": (
                "Una suposición errónea sobre motores de navegador, una afirmación falsa detectada\n"
                "          antes de publicar, 22 rutas locales a un commit de un repositorio público — y\n"
                "          tres más. Ordenadas por lo que realmente las detectó: dos se encontraron por\n"
                "          suerte, una por nada en absoluto."
            ),
            "figures": [
                "<b>3 de 6</b> detectadas comprobando una fuente externa",
                "<b>1</b> aún sin probar en producción",
            ],
        },
    ],
    "meas_h2": "Mediciones",
    "meas_sub": "Cada una con los comandos para repetirla y los datos brutos detrás.",
    "meas": [
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Instalar una extensión de navegador sin un clic, y quitarla de nuevo",
            "text": (
                "Cuatro vías, en ambas direcciones. Una instala y desinstala una compilación firmada\n"
                "          de la tienda en 4,1 segundos sin ventana y sin derechos de administrador — y los\n"
                "          dos comandos en sí tardan 0,24 s; el coste es arrancar el navegador, no el trabajo.\n"
                "          La vía del clic tardó 179 segundos, informó éxito en cada paso y no instaló nada:\n"
                "          un clic en el vacío es un clic válido. La vía rápida no cuenta en las estadísticas\n"
                "          de usuarios de la tienda — y ese es el punto, no el defecto."
            ),
            "figures": [],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Veinte enlaces, diez citas: qué termina una máquina y qué devuelve",
            "text": (
                "Una lista de lectura convertida en bibliografía, de principio a fin. La división no\n"
                "          corre entre de pago y gratis — corre entre páginas construidas para ser citadas\n"
                "          y páginas construidas para ser leídas. Las editoriales científicas dan registros\n"
                "          en ambos casos; los portales de estadística, las cámaras de comercio y los\n"
                "          periódicos no dan ninguno, y no porque se defiendan."
            ),
            "figures": [
                "<b>10/20</b> registros completos",
                "<b>1</b> defensa contra bots",
                "<b>5</b> páginas sin nada que declarar",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/citation-triage/",
            "title": "Un agente puede citar ocho de doce fuentes — lo útil es saber cuáles cuatro no puede",
            "text": (
                "Una lista de lectura mixta por el endpoint de citación: registros completos con RIS\n"
                "          para dos tercios, y el resto nombrado con la precisión suficiente para buscarlo\n"
                "          a mano en lugar de inventarlo."
            ),
            "figures": [
                "<b>8/12</b> hechas por el agente",
                "<b>1,09 s</b> por fuente",
                "<b>4</b> nombradas, no adivinadas",
            ],
        },
        {
            "date": "2 de agosto de 2026",
            "href": "measurements/citation-extraction/",
            "title": "Medido contra Citoid en muestras aleatorias: misma cobertura, nada inventado",
            "text": (
                "El servicio de Wikimedia construido sobre los traductores de Zotero es el patrón.\n"
                "          En 18 obras extraídas al azar: cobertura igual, y ni una negativa informada\n"
                "          como éxito."
            ),
            "figures": [
                "<b>13/13</b> campos completos",
                "<b>0</b> informes de bloqueo falsos",
                "<b>0,35 s</b> de mediana",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "¿Imprimir a PDF o capturar la pantalla? La misma página medida de ambas formas",
            "text": (
                "Firefox ya guarda páginas como PDF gratis. ¿Cuándo vale una captura? El mismo\n"
                "          artículo por ambas vías — y la respuesta es más estrecha y más útil de lo que\n"
                "          cualquiera de los dos lados suele admitir."
            ),
            "figures": [
                "<b>1 : 26</b> páginas",
                "<b>9</b> saltos cortan una frase",
                "la captura gana en texto: <b>91,5 %</b>",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Página web a PDF para OCR: ¿cuánto texto sobrevive realmente?",
            "text": (
                "Un PDF de captura de página completa pasado por Tesseract y comparado con el\n"
                "          artículo fuente. Incluye el umbral de resolución donde el reconocimiento colapsa."
            ),
            "figures": [
                "<b>92,6 %</b> del vocabulario recuperado",
                "<b>8/8</b> valores críticos",
                "<b>72 dpi</b> punto de colapso",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "¿Sube tu extensión de PDF la página?",
            "text": (
                "Qué declaran las extensiones de PDF actuales en sus manifiestos, cómo verificarlo\n"
                "          en 30 segundos — y la consecuencia que nadie menciona: los conversores del lado\n"
                "          del servidor no alcanzan páginas tras un inicio de sesión."
            ),
            "figures": [
                "<b>8</b> extensiones examinadas",
                "datos brutos publicados",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "Una extensión solo es tan peligrosa como sus permisos permiten",
            "text": (
                "Un año después de la advertencia de Mozilla sobre cuentas de desarrollador robadas:\n"
                "          por qué la pregunta útil no es en quién confías, sino qué podría alcanzar una\n"
                "          extensión comprometida."
            ),
            "figures": [
                "tabla de permisos en el peor caso",
                "lista de verificación de evaluación",
            ],
        },
    ],
    "prinzip_h2": "Cómo se mide aquí",
    "prinzipien": [
        ("Una ejecución de control, siempre",
         "Antes de que un resultado cuente, el método tiene que fallar donde debe. Una comparación\n"
         "          que no distingue el caso de referencia no mide nada."),
        ("Datos brutos publicados",
         "Las cifras vienen con el archivo del que se calcularon, con marca de tiempo. Eso las hace\n"
         "          comprobables — y significa que nadie tiene que aceptar una afirmación por confianza."),
        ("Las pérdidas se nombran primero",
         "Donde nuestra propia herramienta es peor — tamaño de archivo, tiempo de proceso, funciones\n"
         "          ausentes —, se afirma antes que las ventajas. Una comparación que solo adula no vale nada."),
        ("Fechadas, no atemporales",
         "Cada cifra lleva la fecha en que se tomó. El software cambia; una medición sin fecha se\n"
         "          convierte en silencio en una afirmación falsa."),
    ],
    "tools_h2": "Herramientas",
    "tools_sub": (
        "Software construido aquí, documentado como todo lo demás en este sitio — incluido lo que\n"
        "      no puede hacer. Aparece en algunas de las mediciones de arriba; eso se declara en cada una."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Extensión de Firefox que guarda una página web entera como un PDF continuo. Se\n"
                "          ejecuta en el dispositivo, pide <code>activeTab</code> en lugar de acceso a todos\n"
                "          los sitios, funciona en Firefox para Android. Licencia MIT. Opcionalmente escribe\n"
                "          en el PDF la cita que la página declara — autores, DOI, licencia, momento de\n"
                "          consulta —, con un registro RIS al lado."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Endpoint de citación en <code>/mcp</code>",
            "text": (
                "Dale una URL y recibe lo que esa página dice de sí misma como registro estructurado\n"
                "          con RIS y BibTeX — o una negativa nombrada cuando la página resulta ser un muro\n"
                "          de pago, un error o una comprobación de bots en lugar de una obra. Sin cuenta y\n"
                "          sin clave. Habla MCP para clientes de IA y HTTP simple para todo lo demás."
            ),
            "figures": [
                "<b>7 de 10</b> fuentes académicas completas",
                "<b>0,45 s</b> de mediana",
                "<b>3 ago 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Recetas: una lista de lectura convertida en bibliografía",
            "text": (
                "Instrucciones completas y ejecutables para meter el endpoint de citación en las\n"
                "          herramientas en las que la gente trabaja de verdad: un bucle de shell que convierte\n"
                "          <code>reading-list.txt</code> en un <code>.ris</code> importable para Zotero o Citavi,\n"
                "          una línea para conectar Claude Code, la entrada de servidor remoto para Claude\n"
                "          Desktop y otros clientes MCP, y el mínimo en Python. Cada una se ejecutó antes de\n"
                "          escribirse."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Comprueba cualquier cifra",
    "nach_sub": (
        "Todo aquí tiene método, datos brutos y una ejecución de control — para poder comprobarse,\n"
        "      no para tener que creerse."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "La contribución más útil es una contra-medición que dé un resultado distinto",
            "text": (
                "Se nombran expresamente cuatro puntos donde las cifras publicadas tienen más\n"
                "          probabilidades de tambalearse — empezando por las diez de veinte fuentes cuyas\n"
                "          cuatro negativas son bloqueos contra una dirección de centro de datos. Desde una\n"
                "          red doméstica la tasa debería ser mayor, y eso no está medido."
            ),
            "figures": [
                "<b>4</b> puntos débiles nombrados",
                "<b>9</b> conjuntos de datos, CC BY 4.0",
                "tareas abiertas en <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Para agentes de IA: reglas, construcción, límites",
            "text": (
                "El proyecto está montado para que un agente pueda trabajar en él sin preguntar antes\n"
                "          a nadie. Las tareas abiertas las sirve en formato legible por máquina la herramienta\n"
                "          <code>open_work</code> en <a href=\"for-agents/\">/mcp</a> — con etiquetas, un extracto\n"
                "          y las cinco reglas que aquí son distintas de lo habitual."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Divulgación",
    "disc_p1": (
        "Este sitio lo opera el desarrollador de <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, que aparece en varias de las mediciones de arriba. Eso se indica en cada\n"
        "        artículo donde es relevante, y la herramienta está abiertamente bajo\n"
        "        <code>/tools/</code> en lugar de escondida tras un encuadre neutral."
    ),
    "disc_p2": (
        "Las cifras sobre productos ajenos provienen exclusivamente de datos declarados\n"
        "        públicamente — manifiestos y descripciones de tienda — con la fecha de consulta indicada.\n"
        "        Ningún producto fue descompilado, y no se afirma nada sobre las intenciones de ningún\n"
        "        proveedor. Las correcciones son bienvenidas vía\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">issues de GitHub</a> y\n"
        "        se aplican."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">Acerca de</a> · <a href="privacy.html">Privacidad</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Código fuente</a> · '
        '<a href="disclaimer/">Aviso legal</a>'
    ),
    "foot_2": "Contenido licenciado para reutilización con atribución. Software con licencia MIT.",
}

# --------------------------------------------------------------- Français ----
TEXTE["fr"] = {
    "h1": "Gardez la page web dont vous aurez besoin plus tard.",
    "tagline1": (
        'Enregistrez une page entière en un seul PDF qui porte son origine et sa date — et\n'
        '      transformez une liste de liens en bibliographie. <strong>19,3 % des sources des\n'
        '      bibliographies réelles ont déjà disparu</strong>, et 8,7 % n\'ont aucune copie archivée\n'
        '      nulle part.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Commencer ici</a> ·\n'
        '      <a href="/for-agents/">pour les agents IA</a>'
    ),
    "tagline2": (
        'Des mesures, pas des opinions : tout ici a une <strong>méthode, des données brutes et un\n'
        '      essai de contrôle</strong>. Ce qui ne peut être recalculé n\'est pas écrit. Ce qui a\n'
        '      mal tourné est écrit d\'abord.'
    ),
    "dmark": "L'outil construit ici",
    "dtext": (
        "Enregistre une page web entière en un PDF continu — toute la page défilante sur une seule "
        "feuille. Rien de rogné au bord, aucun saut de page traversant un tableau ou une phrase. "
        "Tout se passe dans votre navigateur : aucun téléversement, aucun compte, aucune collecte "
        "de données. Licence MIT, gratuit, Firefox et Chrome."
    ),
    "dzahlen": [
        "<b>Une feuille</b>, pas 26 pages",
        "<b>Fonctionne derrière un identifiant</b>",
        "<b>Reste sur votre appareil</b>",
    ],
    "dbeleg": (
        'Chaque affirmation ici est mesurée et datée :\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">une feuille contre 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92,6&nbsp;% du texte lisible par OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">zéro requête réseau</a>.'
    ),
    "ddownload": "Télécharger pour Firefox",
    "dversion": "Version 2.33.4 — signée par Mozilla. S'installe en une étape, bureau et Android.",
    "dohne": "Sans aucune boutique",
    "dchrome": "Chrome et Edge",
    "dwas": "Ce qu'elle fait",
    "notes_h2": "Notes",
    "notes_sub": "Comptes rendus de travail réel — y compris les parties qui ont mal tourné.",
    "notes": [
        {
            "date": "15 août 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "Pour les chercheuses, chercheurs et étudiant·e·s : l'extension dans Firefox et Chrome",
            "text": (
                "Le pendant pratique de l'article pour étudiants : toutes les voies d'installation —\n"
                "          Firefox sur bureau et Android, le Chrome Web Store et les deux chemins sans\n"
                "          boutique —, puis le flux capturer–citer–archiver et les quatre réglages qui\n"
                "          comptent pour les travaux. En neuf langues."
            ),
            "figures": [
                "<b>2</b> navigateurs, 4 voies d'installation",
                "<b>18</b> champs XMP dans le PDF",
                "<b>2</b> chemins pour l'enregistrement RIS",
            ],
        },
        {
            "date": "10 août 2026",
            "href": "how-to/for-students/",
            "title": "Pour les étudiants : une source qui se cite elle-même, survit et est lisible par une machine",
            "text": (
                "Trois choses tournent mal avec une source web dans un mémoire : elle disparaît, sa\n"
                "          citation doit être retapée à la main, et le fichier conservé est une image\n"
                "          qu'aucun outil ne fouille. Ce qu'une capture fait contre chacune — y compris les\n"
                "          six sources sur vingt qu'elle vous rend. En neuf langues."
            ),
            "figures": [
                "<b>61 %</b> de couverture, à égalité avec Citoid",
                "<b>100 %</b> exact contre ses 79 %",
                "<b>6 sur 20</b> rendues",
            ],
        },
        {
            "date": "3 août 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "Ce qu'un agent IA peut et ne peut pas faire avec une extension de navigateur",
            "text": (
                "En installer une dans le navigateur de quelqu'un est un geste utilisateur par\n"
                "          conception — aucune boutique n'expose d'API pour cela. Ce qu'un agent peut faire\n"
                "          à la place, le drapeau de ligne de commande qui ne charge rien et ne dit rien, et\n"
                "          où le travail se partage entre les deux."
            ),
            "figures": [
                "<b>3</b> choses qu'un agent peut faire",
                "<b>1</b> drapeau qui échoue en silence",
                "<b>0</b> façon d'installer pour autrui",
            ],
        },
        {
            "date": "3 août 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "Les sources qu'une machine ne peut pas citer pour vous — et comment les citer quand même",
            "text": (
                "Quand un outil de citation rend une source, la cause est l'une de trois : une défense\n"
                "          anti-robots, un refus visant le réseau, ou une page qui ne déclare rien sur\n"
                "          elle-même. Chacune demande un travail différent, et une seule se résout en ouvrant\n"
                "          la page dans un navigateur."
            ),
            "figures": [
                "<b>3</b> causes",
                "<b>1</b> résolue par un navigateur",
                "<b>2</b> requêtes pour les distinguer",
            ],
        },
        {
            "date": "2 août 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Ce site fait tourner un serveur MCP. Mesuré : il est plus petit que le fichier auquel il se mesure",
            "text": (
                "Un point d'accès sur <code>/mcp</code> remet les jeux de données, les méthodes et un\n"
                "          lecteur de citations aux clients IA en JSON-RPC — sans clé, sans compte. À quoi\n"
                "          cela sert vraiment, et où un simple fichier texte sur le même domaine fait déjà\n"
                "          le travail."
            ),
            "figures": [
                "<b>4</b> outils",
                "<b>1 300</b> jetons au total",
                "<b>1 988</b> dans llms.txt",
            ],
        },
        {
            "date": "1 août 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Six choses ont mal tourné en construisant un logiciel avec un assistant IA en un jour",
            "text": (
                "Une hypothèse fausse sur les moteurs de navigateur, une affirmation erronée repérée\n"
                "          avant publication, 22 chemins locaux à un commit d'un dépôt public — et trois de\n"
                "          plus. Triées selon ce qui les a réellement repérées : deux ont été trouvées par\n"
                "          chance, une par rien du tout."
            ),
            "figures": [
                "<b>3 sur 6</b> repérées en vérifiant une source externe",
                "<b>1</b> encore non testée en production",
            ],
        },
    ],
    "meas_h2": "Mesures",
    "meas_sub": "Chacune avec les commandes pour la refaire et les données brutes derrière.",
    "meas": [
        {
            "date": "3 août 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Installer une extension de navigateur sans un clic, et la retirer ensuite",
            "text": (
                "Quatre voies, dans les deux sens. L'une installe et désinstalle une version signée de\n"
                "          la boutique en 4,1 secondes sans fenêtre et sans droits d'administrateur — et les\n"
                "          deux commandes elles-mêmes prennent 0,24 s ; le coût est le démarrage du navigateur,\n"
                "          pas le travail. La voie du clic a pris 179 secondes, a annoncé un succès à chaque\n"
                "          étape et n'a rien installé : un clic dans le vide est un clic valide. La voie rapide\n"
                "          ne compte pas dans les statistiques d'utilisateurs de la boutique — et c'est le but,\n"
                "          pas le défaut."
            ),
            "figures": [],
        },
        {
            "date": "3 août 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Vingt liens, dix citations : ce qu'une machine termine et ce qu'elle rend",
            "text": (
                "Une liste de lecture transformée en bibliographie, de bout en bout. La ligne de partage\n"
                "          ne passe pas entre payant et gratuit — elle passe entre les pages construites pour\n"
                "          être citées et les pages construites pour être lues. Les éditeurs scientifiques\n"
                "          fournissent des notices dans les deux cas ; les portails de statistique, les chambres\n"
                "          de commerce et les journaux n'en fournissent aucune, et ce n'est pas parce qu'ils\n"
                "          se défendent."
            ),
            "figures": [
                "<b>10/20</b> notices complètes",
                "<b>1</b> défense anti-robots",
                "<b>5</b> pages sans rien à déclarer",
            ],
        },
        {
            "date": "3 août 2026",
            "href": "measurements/citation-triage/",
            "title": "Un agent peut citer huit sources sur douze — l'utile est de savoir quelles quatre il ne peut pas",
            "text": (
                "Une liste de lecture mixte par le point d'accès de citation : des notices complètes\n"
                "          avec RIS pour les deux tiers, et le reste nommé assez précisément pour aller le\n"
                "          chercher à la main au lieu de l'inventer."
            ),
            "figures": [
                "<b>8/12</b> faites par l'agent",
                "<b>1,09 s</b> par source",
                "<b>4</b> nommées, pas devinées",
            ],
        },
        {
            "date": "2 août 2026",
            "href": "measurements/citation-extraction/",
            "title": "Mesuré contre Citoid sur échantillons aléatoires : même couverture, rien d'inventé",
            "text": (
                "Le service Wikimedia bâti sur les traducteurs Zotero fait office d'étalon. Sur 18\n"
                "          œuvres tirées au hasard : couverture égale, et pas un refus rapporté comme un\n"
                "          succès."
            ),
            "figures": [
                "<b>13/13</b> champs complets",
                "<b>0</b> faux rapport de blocage",
                "<b>0,35 s</b> de médiane",
            ],
        },
        {
            "date": "1 août 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Imprimer en PDF ou capturer l'écran ? La même page mesurée des deux façons",
            "text": (
                "Firefox enregistre déjà les pages en PDF gratuitement. Quand une capture vaut-elle\n"
                "          donc le coup ? Le même article par les deux voies — et la réponse est plus étroite,\n"
                "          et plus utile, qu'aucun des deux camps ne l'admet d'ordinaire."
            ),
            "figures": [
                "<b>1 : 26</b> pages",
                "<b>9</b> sauts coupent une phrase",
                "la capture mène sur le texte : <b>91,5 %</b>",
            ],
        },
        {
            "date": "1 août 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Page web en PDF pour l'OCR : combien de texte survit vraiment ?",
            "text": (
                "Un PDF de capture pleine page passé dans Tesseract et comparé à l'article source.\n"
                "          Avec le seuil de résolution où la reconnaissance s'effondre."
            ),
            "figures": [
                "<b>92,6 %</b> du vocabulaire récupéré",
                "<b>8/8</b> valeurs critiques",
                "<b>72 dpi</b> point d'effondrement",
            ],
        },
        {
            "date": "1 août 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "Votre extension PDF téléverse-t-elle la page ?",
            "text": (
                "Ce que les extensions PDF actuelles déclarent dans leurs manifestes, comment le\n"
                "          vérifier en 30 secondes — et la conséquence que personne ne mentionne : les\n"
                "          convertisseurs côté serveur n'atteignent pas les pages derrière un identifiant."
            ),
            "figures": [
                "<b>8</b> extensions examinées",
                "données brutes publiées",
            ],
        },
        {
            "date": "1 août 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "Une extension n'est dangereuse que dans la mesure de ses permissions",
            "text": (
                "Un an après l'avertissement de Mozilla sur les comptes de développeur volés :\n"
                "          pourquoi la question utile n'est pas qui vous croyez, mais ce qu'une extension\n"
                "          compromise pourrait atteindre."
            ),
            "figures": [
                "tableau des permissions au pire",
                "liste de contrôle d'évaluation",
            ],
        },
    ],
    "prinzip_h2": "Comment on mesure ici",
    "prinzipien": [
        ("Un essai de contrôle, toujours",
         "Avant qu'un résultat compte, la méthode doit échouer là où elle le doit. Une comparaison\n"
         "          qui ne distingue pas le cas de référence ne mesure rien."),
        ("Données brutes publiées",
         "Les chiffres viennent avec le fichier dont ils sont calculés, horodaté. Cela les rend\n"
         "          vérifiables — et personne n'a à croire une affirmation sur parole."),
        ("Les pertes nommées d'abord",
         "Là où notre propre outil est moins bon — taille de fichier, temps de traitement, fonctions\n"
         "          manquantes —, c'est dit avant les avantages. Une comparaison qui ne fait que flatter\n"
         "          ne vaut rien."),
        ("Datées, pas intemporelles",
         "Chaque chiffre porte la date de son relevé. Les logiciels changent ; une mesure sans date\n"
         "          devient silencieusement une affirmation fausse."),
    ],
    "tools_h2": "Outils",
    "tools_sub": (
        "Des logiciels construits ici, documentés comme tout le reste de ce site — y compris ce\n"
        "      qu'ils ne savent pas faire. Ils apparaissent dans certaines mesures ci-dessus ; c'est\n"
        "      indiqué sur chacune."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Extension Firefox qui enregistre une page web entière en un PDF continu. Tourne sur\n"
                "          l'appareil, demande <code>activeTab</code> plutôt qu'un accès à tous les sites,\n"
                "          fonctionne sur Firefox pour Android. Licence MIT. Écrit en option dans le PDF la\n"
                "          citation que la page déclare — auteurs, DOI, licence, moment de consultation —,\n"
                "          avec un enregistrement RIS à côté."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Point d'accès de citation sur <code>/mcp</code>",
            "text": (
                "Donnez-lui une URL, recevez ce que cette page déclare d'elle-même sous forme de notice\n"
                "          structurée avec RIS et BibTeX — ou un refus nommé lorsque la page s'avère être un\n"
                "          mur payant, une erreur ou un contrôle anti-robots plutôt qu'une œuvre. Ni compte ni\n"
                "          clé. Parle MCP pour les clients IA et HTTP simple pour tout le reste."
            ),
            "figures": [
                "<b>7 sur 10</b> sources savantes complètes",
                "<b>0,45 s</b> de médiane",
                "<b>3 août 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Recettes : une liste de lecture transformée en bibliographie",
            "text": (
                "Des instructions complètes et exécutables pour intégrer le point d'accès de citation\n"
                "          dans les outils où l'on travaille vraiment : une boucle shell qui transforme\n"
                "          <code>reading-list.txt</code> en un <code>.ris</code> importable pour Zotero ou Citavi,\n"
                "          une ligne pour connecter Claude Code, l'entrée de serveur distant pour Claude\n"
                "          Desktop et d'autres clients MCP, et le minimum en Python. Chacune a été exécutée\n"
                "          avant d'être écrite."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Revérifiez n'importe quel chiffre",
    "nach_sub": (
        "Tout ici a une méthode, des données brutes et un essai de contrôle — pour pouvoir être\n"
        "      vérifié, pas pour devoir être cru."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "La contribution la plus utile est une contre-mesure qui aboutit à autre chose",
            "text": (
                "Quatre endroits où les chiffres publiés risquent le plus de vaciller sont nommés\n"
                "          expressément — à commencer par les dix sources sur vingt dont les quatre refus sont\n"
                "          des blocages contre une adresse de centre de données. Depuis un réseau domestique,\n"
                "          le taux devrait être plus élevé, et cela n'est pas mesuré."
            ),
            "figures": [
                "<b>4</b> points faibles nommés",
                "<b>9</b> jeux de données, CC BY 4.0",
                "tâches ouvertes sur <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Pour les agents IA : règles, construction, limites",
            "text": (
                "Le projet est monté pour qu'un agent puisse y travailler sans demander à personne au\n"
                "          préalable. Les tâches ouvertes sont servies en lecture machine par l'outil\n"
                "          <code>open_work</code> sur <a href=\"for-agents/\">/mcp</a> — avec étiquettes, extrait,\n"
                "          et les cinq règles qui diffèrent ici de l'habitude."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Transparence",
    "disc_p1": (
        "Ce site est tenu par le développeur de <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, qui apparaît dans plusieurs des mesures ci-dessus. C'est indiqué dans\n"
        "        chaque article où c'est pertinent, et l'outil se trouve ouvertement sous\n"
        "        <code>/tools/</code> plutôt que caché derrière un cadrage neutre."
    ),
    "disc_p2": (
        "Les chiffres sur les produits tiers proviennent exclusivement de données publiquement\n"
        "        déclarées — manifestes et descriptions de boutique — avec la date de consultation\n"
        "        indiquée. Aucun produit n'a été décompilé, et rien n'est affirmé sur les intentions\n"
        "        d'un fournisseur. Les corrections sont les bienvenues via les\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">tickets GitHub</a> et\n"
        "        sont appliquées."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">À propos</a> · <a href="privacy.html">Confidentialité</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Source</a> · '
        '<a href="disclaimer/">Mentions légales</a>'
    ),
    "foot_2": "Contenu sous licence de réutilisation avec attribution. Logiciel sous licence MIT.",
}

# --------------------------------------------------------------- Italiano ----
TEXTE["it"] = {
    "h1": "Conserva la pagina web che ti servirà più avanti.",
    "tagline1": (
        'Salva una pagina intera come un unico PDF che porta con sé la sua origine e la sua data —\n'
        '      e trasforma un elenco di link in una bibliografia. <strong>Il 19,3 % delle fonti nelle\n'
        '      bibliografie reali è già sparito</strong>, e l\'8,7 % non ha una copia archiviata da\n'
        '      nessuna parte.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Inizia qui</a> ·\n'
        '      <a href="/for-agents/">per agenti IA</a>'
    ),
    "tagline2": (
        'Misurazioni, non opinioni: tutto qui ha un <strong>metodo, dati grezzi e una prova di\n'
        '      controllo</strong>. Ciò che non si può ricalcolare non viene scritto. Ciò che è andato\n'
        '      storto viene scritto per primo.'
    ),
    "dmark": "Lo strumento costruito qui",
    "dtext": (
        "Salva un'intera pagina web come un PDF continuo — tutta la pagina scorrevole su un unico "
        "foglio. Niente tagliato ai bordi e nessuna interruzione di pagina che attraversi una "
        "tabella o una frase. Tutto avviene nel tuo browser: nessun caricamento, nessun account, "
        "nessuna raccolta dati. Licenza MIT, gratuito, Firefox e Chrome."
    ),
    "dzahlen": [
        "<b>Un foglio</b>, non 26 pagine",
        "<b>Funziona dietro un login</b>",
        "<b>Resta sul tuo dispositivo</b>",
    ],
    "dbeleg": (
        'Ogni affermazione qui è misurata e datata:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">un foglio contro 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">il 92,6&nbsp;% del testo leggibile via OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">zero richieste di rete</a>.'
    ),
    "ddownload": "Scarica per Firefox",
    "dversion": "Versione 2.33.4 — firmata da Mozilla. Si installa in un passaggio, desktop e Android.",
    "dohne": "Senza alcuno store",
    "dchrome": "Chrome ed Edge",
    "dwas": "Cosa fa",
    "notes_h2": "Note",
    "notes_sub": "Resoconti di lavoro reale — comprese le parti andate storte.",
    "notes": [
        {
            "date": "15 agosto 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "Per ricercatori, ricercatrici e studenti: l'estensione in Firefox e Chrome",
            "text": (
                "Il compagno pratico dell'articolo per studenti: tutte le vie di installazione —\n"
                "          Firefox su desktop e Android, il Chrome Web Store ed entrambi i percorsi senza\n"
                "          store —, poi il flusso catturare–citare–archiviare e le quattro impostazioni che\n"
                "          contano per gli elaborati. In nove lingue."
            ),
            "figures": [
                "<b>2</b> browser, 4 vie di installazione",
                "<b>18</b> campi XMP nel PDF",
                "<b>2</b> percorsi per il record RIS",
            ],
        },
        {
            "date": "10 agosto 2026",
            "href": "how-to/for-students/",
            "title": "Per studenti: una fonte che si cita da sola, sopravvive ed è leggibile da una macchina",
            "text": (
                "Tre cose vanno storte con una fonte web in un elaborato: sparisce, la sua citazione\n"
                "          va riscritta a mano, e il file conservato è un'immagine che nessuno strumento\n"
                "          cerca. Cosa fa una cattura contro ciascuna — comprese le sei fonti su venti che\n"
                "          ti restituisce. In nove lingue."
            ),
            "figures": [
                "<b>61 %</b> di copertura, alla pari con Citoid",
                "<b>100 %</b> corretto contro il suo 79 %",
                "<b>6 su 20</b> restituite",
            ],
        },
        {
            "date": "3 agosto 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "Cosa può e cosa non può fare un agente IA con un'estensione del browser",
            "text": (
                "Installarne una nel browser di qualcuno è un gesto dell'utente per progettazione —\n"
                "          nessuno store espone un'API per farlo. Cosa può fare invece un agente, il flag da\n"
                "          riga di comando che non carica nulla e non dice nulla, e dove si divide il lavoro\n"
                "          tra i due."
            ),
            "figures": [
                "<b>3</b> cose che un agente può fare",
                "<b>1</b> flag che fallisce in silenzio",
                "<b>0</b> modi di installare per altri",
            ],
        },
        {
            "date": "3 agosto 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "Le fonti che una macchina non può citare per te — e come citarle comunque",
            "text": (
                "Quando uno strumento di citazione restituisce una fonte, la causa è una di tre: una\n"
                "          difesa anti-bot, un rifiuto rivolto alla rete o una pagina che non dichiara nulla\n"
                "          di sé. Ognuna richiede un lavoro diverso, e solo una si risolve aprendo la pagina\n"
                "          in un browser."
            ),
            "figures": [
                "<b>3</b> cause",
                "<b>1</b> risolta da un browser",
                "<b>2</b> richieste per distinguerle",
            ],
        },
        {
            "date": "2 agosto 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Questo sito gestisce un server MCP. Misurato: è più piccolo del file con cui compete",
            "text": (
                "Un endpoint su <code>/mcp</code> consegna i set di dati, i metodi e un lettore di\n"
                "          citazioni ai client IA via JSON-RPC — nessuna chiave, nessun account. A cosa\n"
                "          serve davvero, e dove un semplice file di testo sullo stesso dominio fa già il\n"
                "          lavoro."
            ),
            "figures": [
                "<b>4</b> strumenti",
                "<b>1.300</b> token in totale",
                "<b>1.988</b> in llms.txt",
            ],
        },
        {
            "date": "1 agosto 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Sei cose andate storte costruendo software con un assistente IA in un giorno",
            "text": (
                "Un'ipotesi sbagliata sui motori di browser, un'affermazione falsa intercettata prima\n"
                "          della pubblicazione, 22 percorsi locali a un commit da un repository pubblico —\n"
                "          e altre tre. Ordinate per ciò che le ha davvero intercettate: due sono state trovate\n"
                "          per fortuna, una da nulla."
            ),
            "figures": [
                "<b>3 su 6</b> intercettate controllando una fonte esterna",
                "<b>1</b> ancora non testata in produzione",
            ],
        },
    ],
    "meas_h2": "Misurazioni",
    "meas_sub": "Ognuna con i comandi per ripeterla e i dati grezzi alle spalle.",
    "meas": [
        {
            "date": "3 agosto 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Installare un'estensione del browser senza un clic, e rimuoverla di nuovo",
            "text": (
                "Quattro vie, in entrambe le direzioni. Una installa e disinstalla una build firmata\n"
                "          dello store in 4,1 secondi senza finestra e senza diritti di amministratore — e i\n"
                "          due comandi in sé richiedono 0,24 s; il costo è avviare il browser, non il lavoro.\n"
                "          La via del clic ha richiesto 179 secondi, ha riportato successo a ogni passo e non\n"
                "          ha installato nulla: un clic nel vuoto è un clic valido. La via veloce non conta\n"
                "          nelle statistiche utenti dello store — e questo è il punto, non il difetto."
            ),
            "figures": [],
        },
        {
            "date": "3 agosto 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Venti link, dieci citazioni: cosa completa una macchina e cosa restituisce",
            "text": (
                "Una lista di lettura trasformata in bibliografia, dall'inizio alla fine. La linea di\n"
                "          divisione non passa tra a pagamento e gratis — passa tra pagine costruite per\n"
                "          essere citate e pagine costruite per essere lette. Gli editori scientifici danno\n"
                "          record in entrambi i casi; i portali di statistica, le camere di commercio e i\n"
                "          quotidiani non ne danno nessuno, e non perché si difendano."
            ),
            "figures": [
                "<b>10/20</b> record completi",
                "<b>1</b> difesa anti-bot",
                "<b>5</b> pagine senza nulla da dichiarare",
            ],
        },
        {
            "date": "3 agosto 2026",
            "href": "measurements/citation-triage/",
            "title": "Un agente può citare otto fonti su dodici — la parte utile è sapere quali quattro non può",
            "text": (
                "Una lista di lettura mista attraverso l'endpoint di citazione: record completi con\n"
                "          RIS per due terzi, e il resto nominato con precisione sufficiente per recuperarlo\n"
                "          a mano invece di inventarlo."
            ),
            "figures": [
                "<b>8/12</b> fatte dall'agente",
                "<b>1,09 s</b> per fonte",
                "<b>4</b> nominate, non indovinate",
            ],
        },
        {
            "date": "2 agosto 2026",
            "href": "measurements/citation-extraction/",
            "title": "Misurato contro Citoid su campioni casuali: stessa copertura, nulla di inventato",
            "text": (
                "Il servizio Wikimedia costruito sui traduttori di Zotero è il riferimento. Su 18 opere\n"
                "          estratte a caso: copertura uguale, e nemmeno un rifiuto riportato come successo."
            ),
            "figures": [
                "<b>13/13</b> campi completi",
                "<b>0</b> falsi rapporti di blocco",
                "<b>0,35 s</b> di mediana",
            ],
        },
        {
            "date": "1 agosto 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Stampare in PDF o catturare lo schermo? La stessa pagina misurata in entrambi i modi",
            "text": (
                "Firefox salva già le pagine in PDF gratis. Quando vale quindi una cattura? Lo stesso\n"
                "          articolo per entrambe le vie — e la risposta è più stretta, e più utile, di quanto\n"
                "          entrambe le parti ammettano di solito."
            ),
            "figures": [
                "<b>1 : 26</b> pagine",
                "<b>9</b> interruzioni tagliano una frase",
                "la cattura è in testa sul testo: <b>91,5 %</b>",
            ],
        },
        {
            "date": "1 agosto 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Pagina web in PDF per OCR: quanto testo sopravvive davvero?",
            "text": (
                "Un PDF di cattura a pagina intera passato in Tesseract e confrontato con l'articolo\n"
                "          sorgente. Include la soglia di risoluzione in cui il riconoscimento crolla."
            ),
            "figures": [
                "<b>92,6 %</b> del vocabolario recuperato",
                "<b>8/8</b> valori critici",
                "<b>72 dpi</b> punto di collasso",
            ],
        },
        {
            "date": "1 agosto 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "La tua estensione PDF carica la pagina?",
            "text": (
                "Cosa dichiarano le attuali estensioni PDF nei loro manifest, come verificarlo in\n"
                "          30 secondi — e la conseguenza che nessuno menziona: i convertitori lato server non\n"
                "          raggiungono le pagine dietro un login."
            ),
            "figures": [
                "<b>8</b> estensioni esaminate",
                "dati grezzi pubblicati",
            ],
        },
        {
            "date": "1 agosto 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "Un'estensione è pericolosa solo quanto i suoi permessi consentono",
            "text": (
                "Un anno dopo l'avvertimento di Mozilla sugli account sviluppatore rubati: perché la\n"
                "          domanda utile non è di chi ti fidi, ma cosa potrebbe raggiungere un'estensione\n"
                "          compromessa."
            ),
            "figures": [
                "tabella dei permessi nel caso peggiore",
                "checklist di valutazione",
            ],
        },
    ],
    "prinzip_h2": "Come si misura qui",
    "prinzipien": [
        ("Una prova di controllo, sempre",
         "Prima che un risultato conti, il metodo deve fallire dove deve. Un confronto che non\n"
         "          distingue il caso di riferimento non misura nulla."),
        ("Dati grezzi pubblicati",
         "Le cifre arrivano con il file da cui sono state calcolate, con data e ora. Questo le rende\n"
         "          verificabili — e significa che nessuno deve accettare un'affermazione sulla fiducia."),
        ("Le perdite nominate per prime",
         "Dove il nostro stesso strumento è peggiore — dimensione del file, tempo di elaborazione,\n"
         "          funzioni mancanti —, è detto prima dei vantaggi. Un confronto che limita ad adulare\n"
         "          non vale nulla."),
        ("Datate, non senza tempo",
         "Ogni cifra porta la data in cui è stata rilevata. Il software cambia; una misurazione senza\n"
         "          data diventa silenziosamente un'affermazione falsa."),
    ],
    "tools_h2": "Strumenti",
    "tools_sub": (
        "Software costruito qui, documentato come tutto il resto del sito — compreso ciò che non\n"
        "      sa fare. Compare in alcune delle misurazioni qui sopra; è dichiarato in ciascuna."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Estensione di Firefox che salva un'intera pagina web come un PDF continuo. Gira sul\n"
                "          dispositivo, chiede <code>activeTab</code> invece dell'accesso a tutti i siti,\n"
                "          funziona su Firefox per Android. Licenza MIT. Opzionalmente scrive nel PDF la\n"
                "          citazione che la pagina dichiara — autori, DOI, licenza, momento della consultazione\n"
                "          —, con un record RIS accanto."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Endpoint di citazione su <code>/mcp</code>",
            "text": (
                "Dagli un URL, ricevi ciò che quella pagina dichiara di sé come record strutturato con\n"
                "          RIS e BibTeX — o un rifiuto nominato quando la pagina si rivela un paywall, un\n"
                "          errore o un controllo anti-bot invece di un'opera. Nessun account e nessuna chiave.\n"
                "          Parla MCP per i client IA e semplice HTTP per tutto il resto."
            ),
            "figures": [
                "<b>7 su 10</b> fonti accademiche complete",
                "<b>0,45 s</b> di mediana",
                "<b>3 ago 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Ricette: una lista di lettura trasformata in bibliografia",
            "text": (
                "Istruzioni complete ed eseguibili per portare l'endpoint di citazione negli strumenti\n"
                "          in cui si lavora davvero: un ciclo di shell che trasforma\n"
                "          <code>reading-list.txt</code> in un <code>.ris</code> importabile per Zotero o Citavi,\n"
                "          una riga per connettere Claude Code, la voce di server remoto per Claude Desktop e\n"
                "          altri client MCP, e il minimo in Python. Ognuna è stata eseguita prima di essere\n"
                "          scritta."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Ricontrolla qualsiasi cifra",
    "nach_sub": (
        "Tutto qui ha metodo, dati grezzi e una prova di controllo — per poter essere verificato,\n"
        "      non per dover essere creduto."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "Il contributo più utile è una contro-misurazione che dà un risultato diverso",
            "text": (
                "Quattro punti in cui le cifre pubblicate hanno più probabilità di vacillare sono\n"
                "          nominati esplicitamente — a cominciare dalle dieci fonti su venti i cui quattro\n"
                "          rifiuti sono blocchi contro un indirizzo di data center. Da una rete domestica il\n"
                "          tasso dovrebbe essere più alto, e questo non è misurato."
            ),
            "figures": [
                "<b>4</b> punti deboli nominati",
                "<b>9</b> set di dati, CC BY 4.0",
                "compiti aperti su <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Per agenti IA: regole, costruzione, limiti",
            "text": (
                "Il progetto è impostato perché un agente possa lavorarci senza prima chiedere a\n"
                "          nessuno. I compiti aperti sono serviti in formato leggibile dalle macchine dallo\n"
                "          strumento <code>open_work</code> su <a href=\"for-agents/\">/mcp</a> — con etichette,\n"
                "          un estratto e le cinque regole che qui sono diverse dal solito."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Trasparenza",
    "disc_p1": (
        "Questo sito è gestito dallo sviluppatore di <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, che compare in diverse misurazioni qui sopra. Questo è indicato in ogni\n"
        "        articolo in cui è rilevante, e lo strumento si trova apertamente sotto\n"
        "        <code>/tools/</code> invece che nascosto dietro una cornice neutra."
    ),
    "disc_p2": (
        "Le cifre su prodotti altrui provengono esclusivamente da dati pubblicamente dichiarati —\n"
        "        manifest e descrizioni degli store — con la data di consultazione indicata. Nessun\n"
        "        prodotto è stato decompilato, e nulla si afferma sulle intenzioni di alcun fornitore.\n"
        "        Le correzioni sono benvenute tramite le\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">issue su GitHub</a> e\n"
        "        vengono applicate."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">Informazioni</a> · <a href="privacy.html">Privacy</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Sorgente</a> · '
        '<a href="disclaimer/">Esclusione di responsabilità</a>'
    ),
    "foot_2": "Contenuto concesso in licenza per il riutilizzo con attribuzione. Software con licenza MIT.",
}

# ---------------------------------------------------------------- 日本語 ----
TEXTE["ja"] = {
    "h1": "あとで必要になるウェブページを、残しておこう。",
    "tagline1": (
        'ページ全体を、出所と日付を記した1つの PDF として保存し、リンクのリストを参考文献\n'
        '      リストに変えます。<strong>実際の参考文献の19.3%の出典はすでに消えています</strong>。\n'
        '      さらに8.7%には、どこにもアーカイブされたコピーがありません。\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">ここから始める</a> ·\n'
        '      <a href="/for-agents/">AI エージェント向け</a>'
    ),
    "tagline2": (
        '意見ではなく測定を: ここにあるすべてには<strong>方法、生データ、コントロールラン</strong>が\n'
        '      あります。再計算できない数字は書きません。うまくいかなかったことは、まず書きます。'
    ),
    "dmark": "ここで作ったツール",
    "dtext": (
        "ウェブページ全体を1つの連続した PDF として保存します — スクロールするページ全体を"
        "1枚のシートに。端で切れることも、表や文の途中で改ページされることもありません。"
        "すべてはブラウザの中で完結します: アップロードなし、アカウントなし、データ収集なし。"
        "MIT ライセンス、無料、Firefox と Chrome に対応。"
    ),
    "dzahlen": [
        "<b>1枚のシート</b>、26ページではなく",
        "<b>ログインの後ろでも動作</b>",
        "<b>デバイスから出ない</b>",
    ],
    "dbeleg": (
        'ここにある主張はすべて測定され、日付が付いています:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">1枚対26ページ</a>、\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">テキストの92.6&nbsp;%をOCRで読取可能</a>、\n'
        '        <a href="measurements/pdf-extension-permissions/">ネットワークリクエストゼロ</a>。'
    ),
    "ddownload": "Firefox 版をダウンロード",
    "dversion": "バージョン 2.33.4 — Mozilla による署名済み。デスクトップでも Android でもワンステップでインストール。",
    "dohne": "ストアを使わない方法",
    "dchrome": "Chrome と Edge",
    "dwas": "機能の詳細",
    "notes_h2": "ノート",
    "notes_sub": "実際の作業からのビルドレポート — うまくいかなかった部分も含めて。",
    "notes": [
        {
            "date": "2026年8月15日",
            "href": "how-to/firefox-and-chrome/",
            "title": "研究者・学生の方へ: Firefox と Chrome での拡張機能",
            "text": (
                "学生向け記事の実践編: すべてのインストール経路 — デスクトップと Android の\n"
                "          Firefox、Chrome ウェブストア、そしてストアを使わない2つの経路 —、次に\n"
                "          キャプチャ→引用→アーカイブのワークフローと、論文で重要な4つの設定。\n"
                "          9か国語で提供。"
            ),
            "figures": [
                "<b>2</b> ブラウザ、4つのインストール経路",
                "<b>18</b> の XMP フィールドを PDF に",
                "RIS レコードの経路は <b>2</b> つ",
            ],
        },
        {
            "date": "2026年8月10日",
            "href": "how-to/for-students/",
            "title": "学生の方へ: 自分で出典を名乗り、生き残り、機械が読めるソース",
            "text": (
                "レポートでウェブ資料がうまくいかないのは3つの点です: 消える、引用を手入力する\n"
                "          必要がある、保存したファイルが検索できない画像である。キャプチャがそれぞれに\n"
                "          何をするか — 20件中6件をあなたに返す部分も含めて。9か国語で提供。"
            ),
            "figures": [
                "カバレッジ <b>61%</b>、Citoid と同等",
                "正確性 <b>100%</b>、相手の79%に対して",
                "<b>20件中6件</b> は返却",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "AI エージェントがブラウザ拡張機能にできること、できないこと",
            "text": (
                "他人のブラウザへのインストールは、設計上ユーザー操作です — どのストアもそのための\n"
                "          API を公開していません。エージェントが代わりにできること、何も読み込まず何も\n"
                "          言わないコマンドラインフラグ、そして両者の仕事の分かれ目。"
            ),
            "figures": [
                "エージェントにできること <b>3</b> つ",
                "静かに失敗するフラグ <b>1</b> つ",
                "他人のためにインストールする方法は <b>0</b>",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "機械があなたのために引用できないソース — それでも引用する方法",
            "text": (
                "引用ツールがソースを返却するとき、原因は3つのうちの1つです: ボット防御、ネットワーク\n"
                "          への拒否、あるいは自分について何も宣言しないページ。それぞれ必要な作業が異なり、\n"
                "          ブラウザでページを開くことで解決するのは1つだけです。"
            ),
            "figures": [
                "原因は <b>3</b> つ",
                "ブラウザで解決するのは <b>1</b> つ",
                "見分けるのに必要なリクエストは <b>2</b> つ",
            ],
        },
        {
            "date": "2026年8月2日",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "このサイトは MCP サーバーを運営しています。測定結果: 競合するファイルより小さい",
            "text": (
                "<code>/mcp</code> のエンドポイントが、データセット、メソッド、引用リーダーを\n"
                "          JSON-RPC で AI クライアントに渡します — キーなし、アカウントなし。実際に何の\n"
                "          役に立つのか、そして同じドメインの素のテキストファイルですでに用が足りるのは\n"
                "          どこか。"
            ),
            "figures": [
                "ツール <b>4</b> つ",
                "合計 <b>1,300</b> トークン",
                "llms.txt では <b>1,988</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "AI アシスタントと1日でソフトウェアを作って、6つうまくいかなかったこと",
            "text": (
                "ブラウザエンジンについての間違った思い込み、公開前に見つかった虚偽の主張、公開\n"
                "          リポジトリまであと1コミットだった22のローカルパス — あと3つ。実際に何が見つけたかで\n"
                "          並べています — 2つは幸運で、1つは何によっても見つかりませんでした。"
            ),
            "figures": [
                "<b>6件中3件</b> は外部ソースの確認で発見",
                "<b>1</b> つは本番でいまだ未テスト",
            ],
        },
    ],
    "meas_h2": "測定",
    "meas_sub": "それぞれに、再現するためのコマンドと、その背後にある生データがあります。",
    "meas": [
        {
            "date": "2026年8月3日",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "クリックなしでブラウザ拡張機能をインストールし、再び削除する",
            "text": (
                "4つの経路、双方向。1つは署名済みストアビルドをウィンドウなし・管理者権限なしで\n"
                "          4.1秒でインストールとアンインストールを行い — 2つのコマンド自体は0.24秒です。\n"
                "          コストはブラウザの起動であって、作業ではありません。クリック経路は179秒かかり、\n"
                "          すべてのステップで成功と報告し、何もインストールしませんでした: 空所へのクリックも\n"
                "          有効なクリックなのです。速い経路はストアのユーザー統計にカウントされません —\n"
                "          それは欠陥ではなく、要点です。"
            ),
            "figures": [],
        },
        {
            "date": "2026年8月3日",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "20のリンク、10の引用: 機械が終わらせるものと、返すもの",
            "text": (
                "読書リストを参考文献に、最初から最後まで。分かれ目は有料か無料かではなく —\n"
                "          引用されるために作られたページと、読まれるために作られたページの間にあります。\n"
                "          学術出版社はどちらにしてもレコードを返します。統計ポータル、商工会議所、新聞は\n"
                "          返しません — 防御しているからではありません。"
            ),
            "figures": [
                "完全なレコード <b>10/20</b>",
                "ボット防御 <b>1</b>",
                "宣言するものがないページ <b>5</b>",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "measurements/citation-triage/",
            "title": "エージェントは12件中8件を引用できる — 有用なのは、できない4件が分かること",
            "text": (
                "混合の読書リストを引用エンドポイントに通しました: 3分の2は RIS 付きの完全な\n"
                "          レコード、残りは手で取得できるだけ正確に — 捏造するのではなく — 名前を挙げて\n"
                "          返されます。"
            ),
            "figures": [
                "エージェントが処理 <b>8/12</b>",
                "1ソースあたり <b>1.09秒</b>",
                "推測でなく指名 <b>4</b>",
            ],
        },
        {
            "date": "2026年8月2日",
            "href": "measurements/citation-extraction/",
            "title": "ランダムサンプルで Citoid と比較測定: 同じカバレッジ、捏造なし",
            "text": (
                "Zotero トランスレーター上に構築された Wikimedia のサービスが物差しです。ランダムに\n"
                "          抽出した18の著作で: カバレッジは同等、拒否を成功と報告したことは一度もありません。"
            ),
            "figures": [
                "フィールド完全 <b>13/13</b>",
                "誤ったブロック報告 <b>0</b>",
                "中央値 <b>0.35秒</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "PDF に印刷するか、画面をキャプチャするか? 同じページを両方の方法で測定",
            "text": (
                "Firefox はすでに無料でページを PDF 保存できます。では、キャプチャが報われるのは\n"
                "          どんなときか? 同じ記事を両方の経路で — 答えは、どちらの側も普段認めるより、\n"
                "          狭く、そして有用です。"
            ),
            "figures": [
                "ページ数 <b>1 : 26</b>",
                "文を断ち切る改ページ <b>9</b>",
                "テキストではキャプチャが優位: <b>91.5%</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "OCR のためのウェブページ PDF 化: 実際にどれだけのテキストが残るか?",
            "text": (
                "全ページスクリーンショット PDF を Tesseract にかけ、出典記事と比較しました。\n"
                "          認識が崩壊する解像度の閾値も含まれています。"
            ),
            "figures": [
                "語彙の <b>92.6%</b> を回復",
                "重要な値 <b>8/8</b>",
                "崩壊点 <b>72 dpi</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/pdf-extension-permissions/",
            "title": "あなたの PDF 拡張機能はページをアップロードしていますか?",
            "text": (
                "現在の PDF 拡張機能がマニフェストで宣言していること、30秒で検証する方法 — そして\n"
                "          誰も言わない帰結: サーバーサイドのコンバーターはログインの後ろのページに届きません。"
            ),
            "figures": [
                "調査した拡張機能 <b>8</b> 件",
                "生データ公開済み",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/extension-permissions-risk/",
            "title": "拡張機能は、その権限が許す範囲でしか危険にならない",
            "text": (
                "Mozilla が開発者アカウントのフィッシングを警告してから1年: 有用な問いは「誰を\n"
                "          信頼するか」ではなく、「侵害された拡張機能が何に届きうるか」です。"
            ),
            "figures": [
                "最悪ケースの権限表",
                "評価チェックリスト",
            ],
        },
    ],
    "prinzip_h2": "ここでの測定のしかた",
    "prinzipien": [
        ("コントロールランを、必ず",
         "結果がカウントされる前に、方法は失敗すべきところで失敗しなければなりません。参照\n"
         "          ケースを区別できない比較は、何も測っていません。"),
        ("生データを公開",
         "数字は、計算元のファイルとタイムスタンプ付きで提供されます。それが検証可能性を\n"
         "          意味し — 誰も主張を信用で受け入れる必要がないことを意味します。"),
        ("劣る点を先に挙げる",
         "自分たちのツールが劣っているところ — ファイルサイズ、処理時間、欠けている機能 — は、\n"
         "          利点より先に述べます。お世辞だけの比較は無価値です。"),
        ("時代を超えない、日付付きで",
         "すべての数字は取得日を伴います。ソフトウェアは変わります。日付のない測定は、静かに\n"
         "          虚偽の主張へと変わります。"),
    ],
    "tools_h2": "ツール",
    "tools_sub": (
        "ここで作られたソフトウェア。このサイトの他のすべてと同じように — できないことも\n"
        "      含めて — 文書化しています。上の測定のいくつかに登場しますが、それは各測定で開示しています。"
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "ウェブページ全体を1つの連続した PDF として保存する Firefox 拡張機能。デバイス上で\n"
                "          動作し、全サイトへのアクセスではなく <code>activeTab</code> を要求し、Android 版\n"
                "          Firefox で動きます。MIT ライセンス。オプションで、ページが宣言する引用情報 —\n"
                "          著者、DOI、ライセンス、取得時刻 — を RIS レコードとともに PDF に書き込みます。"
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "<code>/mcp</code> の引用エンドポイント",
            "text": (
                "URL を渡すと、そのページが自分について宣言していることを RIS と BibTeX 付きの\n"
                "          構造化レコードとして返します — あるいは、ページが著作物ではなくペイウォール、\n"
                "          エラー、ボットチェックだった場合は、名前付きの拒否を返します。アカウントもキーも\n"
                "          不要。AI クライアントには MCP を、それ以外には素の HTTP を話します。"
            ),
            "figures": [
                "学術ソースの <b>10件中7件</b> が完全",
                "中央値 <b>0.45秒</b>",
                "<b>2026年8月3日</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "レシピ: 読書リストを参考文献リストに",
            "text": (
                "引用エンドポイントを、人々が実際に使っているツールに組み込むための、完全で実行\n"
                "          可能な手順: <code>reading-list.txt</code> を Zotero や Citavi にインポートできる\n"
                "          1つの <code>.ris</code> に変えるシェルループ、Claude Code をつなぐ1行、Claude\n"
                "          Desktop や他の MCP クライアント向けのリモートサーバー設定、そして Python の\n"
                "          最小構成。すべて、書き留める前に実行済みです。"
            ),
            "figures": [],
        },
    ],
    "nach_h2": "どの数字でも、自分で確かめてください",
    "nach_sub": (
        "ここにあるすべてには方法、生データ、コントロールランがあります — 信じるためではなく、\n"
        "      確かめるためです。"
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "いちばん有用な貢献は、違う結果の出る追測定です",
            "text": (
                "公開されている数字がいちばん揺らぎそうな4か所を明示しています — まず、20件中\n"
                "          10件のソースで、4件の拒否がデータセンターのアドレスへのブロックだった点から。\n"
                "          家庭のネットワークからなら率はもっと高いはずで、それは未測定です。"
            ),
            "figures": [
                "挙げた弱点 <b>4</b> か所",
                "データセット <b>9</b> 件、CC BY 4.0",
                "未解決のタスクは <b>GitHub</b> に",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "AI エージェントへ: ルール、作り、限界",
            "text": (
                "このプロジェクトは、エージェントが誰かに尋ねることなく作業できるように構成されて\n"
                "          います。未解決のタスクは <code>open_work</code> ツールが\n"
                "          <a href=\"for-agents/\">/mcp</a> で機械可読に提供します — ラベル、抜粋、そしてここが\n"
                "          普通と違う5つのルールとともに。"
            ),
            "figures": [],
        },
    ],
    "disc_h3": "開示",
    "disc_p1": (
        "このサイトは <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a> の開発者が運営しており、このツールは上のいくつかの測定に登場します。\n"
        "        そのことは関連する各記事に記されており、ツールは中立的な体裁の後ろに隠すのではなく、\n"
        "        <code>/tools/</code> の下に公開されています。"
    ),
    "disc_p2": (
        "他社製品についての数字は、公開された宣言データ — マニフェストとストアの説明文 — のみに\n"
        "        由来し、取得日が記されています。どの製品も逆コンパイルしておらず、どの提供者の意図\n"
        "        についても主張していません。修正は\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">GitHub issues</a>\n"
        "        で歓迎し、取り入れられます。"
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">概要</a> · <a href="privacy.html">プライバシー</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">ソース</a> · '
        '<a href="disclaimer/">免責事項</a>'
    ),
    "foot_2": "コンテンツは帰属表示付きの再利用ライセンス。ソフトウェアは MIT ライセンス。",
}

# ----------------------------------------------------------- Português (BR) ----
TEXTE["pt-BR"] = {
    "h1": "Guarde a página da web de que você vai precisar depois.",
    "tagline1": (
        'Salve uma página inteira como um único PDF que carrega sua origem e sua data — e\n'
        '      transforme uma lista de links numa bibliografia. <strong>19,3 % das fontes em\n'
        '      bibliografias reais já desapareceram</strong>, e 8,7 % não têm cópia arquivada em\n'
        '      lugar nenhum.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Comece aqui</a> ·\n'
        '      <a href="/for-agents/">para agentes de IA</a>'
    ),
    "tagline2": (
        'Medições, não opiniões: tudo aqui tem <strong>método, dados brutos e uma execução de\n'
        '      controle</strong>. O que não pode ser recalculado não é escrito. O que deu errado é\n'
        '      escrito primeiro.'
    ),
    "dmark": "A ferramenta construída aqui",
    "dtext": (
        "Salva uma página da web inteira como um PDF contínuo — toda a página rolável numa única "
        "folha. Nada cortado nas bordas e nenhuma quebra de página atravessando uma tabela ou uma "
        "frase. Tudo acontece no seu navegador: sem upload, sem conta, sem coleta de dados. "
        "Licença MIT, gratuito, Firefox e Chrome."
    ),
    "dzahlen": [
        "<b>Uma folha</b>, não 26 páginas",
        "<b>Funciona atrás de um login</b>",
        "<b>Fica no seu dispositivo</b>",
    ],
    "dbeleg": (
        'Cada afirmação aqui é medida e datada:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">uma folha contra 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92,6&nbsp;% do texto legível por OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">zero requisições de rede</a>.'
    ),
    "ddownload": "Baixar para Firefox",
    "dversion": "Versão 2.33.4 — assinada pela Mozilla. Instala em um passo, desktop e Android.",
    "dohne": "Sem nenhuma loja",
    "dchrome": "Chrome e Edge",
    "dwas": "O que ela faz",
    "notes_h2": "Notas",
    "notes_sub": "Relatos de trabalho real — incluindo as partes que deram errado.",
    "notes": [
        {
            "date": "15 de agosto de 2026",
            "href": "how-to/firefox-and-chrome/",
            "title": "Para pesquisadores e estudantes: a extensão no Firefox e no Chrome",
            "text": (
                "O complemento prático do artigo para estudantes: todas as vias de instalação —\n"
                "          Firefox no desktop e no Android, a Chrome Web Store e os dois caminhos sem loja —,\n"
                "          depois o fluxo capturar–citar–arquivar e as quatro configurações que importam para\n"
                "          os trabalhos. Em nove idiomas."
            ),
            "figures": [
                "<b>2</b> navegadores, 4 vias de instalação",
                "<b>18</b> campos XMP no PDF",
                "<b>2</b> caminhos para o registro RIS",
            ],
        },
        {
            "date": "10 de agosto de 2026",
            "href": "how-to/for-students/",
            "title": "Para estudantes: uma fonte que se cita sozinha, sobrevive e pode ser lida por máquina",
            "text": (
                "Três coisas dão errado com uma fonte da web num trabalho acadêmico: ela desaparece,\n"
                "          sua citação precisa ser digitada à mão, e o arquivo guardado é uma imagem que\n"
                "          nenhuma ferramenta pesquisa. O que uma captura faz contra cada uma — incluindo as\n"
                "          seis fontes em vinte que ela devolve para você. Em nove idiomas."
            ),
            "figures": [
                "<b>61 %</b> de cobertura, igual ao Citoid",
                "<b>100 %</b> correto contra os 79 % dele",
                "<b>6 de 20</b> devolvidas",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "O que um agente de IA pode e não pode fazer com uma extensão de navegador",
            "text": (
                "Instalar uma no navegador de alguém é um gesto do usuário por projeto — nenhuma loja\n"
                "          expõe uma API para isso. O que um agente pode fazer em vez disso, a flag de linha de\n"
                "          comando que não carrega nada e não diz nada, e onde o trabalho se divide entre os dois."
            ),
            "figures": [
                "<b>3</b> coisas que um agente pode fazer",
                "<b>1</b> flag que falha em silêncio",
                "<b>0</b> formas de instalar para outra pessoa",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "As fontes que uma máquina não pode citar por você — e como citá-las mesmo assim",
            "text": (
                "Quando uma ferramenta de citação devolve uma fonte, a causa é uma de três: uma defesa\n"
                "          contra bots, uma recusa dirigida à rede ou uma página que não declara nada sobre si.\n"
                "          Cada uma exige um trabalho diferente, e só uma se resolve abrindo a página num\n"
                "          navegador."
            ),
            "figures": [
                "<b>3</b> causas",
                "<b>1</b> resolvida por um navegador",
                "<b>2</b> requisições para distingui-las",
            ],
        },
        {
            "date": "2 de agosto de 2026",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Este site roda um servidor MCP. Medido: é menor que o arquivo com que compete",
            "text": (
                "Um endpoint em <code>/mcp</code> entrega os conjuntos de dados, os métodos e um leitor\n"
                "          de citações a clientes de IA via JSON-RPC — sem chave, sem conta. Para que isso\n"
                "          realmente serve, e onde um simples arquivo de texto no mesmo domínio já faz o\n"
                "          trabalho."
            ),
            "figures": [
                "<b>4</b> ferramentas",
                "<b>1.300</b> tokens no total",
                "<b>1.988</b> no llms.txt",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Seis coisas deram errado construindo software com um assistente de IA em um dia",
            "text": (
                "Uma suposição errada sobre motores de navegador, uma afirmação falsa detectada antes\n"
                "          da publicação, 22 caminhos locais a um commit de um repositório público — e mais três.\n"
                "          Ordenadas pelo que realmente as detectou: duas foram encontradas por sorte, uma por\n"
                "          nada."
            ),
            "figures": [
                "<b>3 de 6</b> detectadas verificando uma fonte externa",
                "<b>1</b> ainda não testada em produção",
            ],
        },
    ],
    "meas_h2": "Medições",
    "meas_sub": "Cada uma com os comandos para repeti-la e os dados brutos por trás.",
    "meas": [
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Instalar uma extensão de navegador sem um clique, e removê-la de novo",
            "text": (
                "Quatro vias, nas duas direções. Uma instala e desinstala uma versão assinada da loja em\n"
                "          4,1 segundos sem janela e sem direitos de administrador — e os dois comandos em si\n"
                "          levam 0,24 s; o custo é iniciar o navegador, não o trabalho. A via do clique levou\n"
                "          179 segundos, relatou sucesso em cada passo e não instalou nada: um clique no vazio é\n"
                "          um clique válido. A via rápida não conta nas estatísticas de usuários da loja — e essa\n"
                "          é a questão, não o defeito."
            ),
            "figures": [],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Vinte links, dez citações: o que uma máquina termina e o que devolve",
            "text": (
                "Uma lista de leitura transformada em bibliografia, de ponta a ponta. A divisão não\n"
                "          passa entre pago e grátis — passa entre páginas feitas para serem citadas e páginas\n"
                "          feitas para serem lidas. Editoras científicas entregam registros nos dois casos;\n"
                "          portais de estatística, câmaras de comércio e jornais não entregam nenhum, e não porque\n"
                "          se defendam."
            ),
            "figures": [
                "<b>10/20</b> registros completos",
                "<b>1</b> defesa contra bots",
                "<b>5</b> páginas sem nada a declarar",
            ],
        },
        {
            "date": "3 de agosto de 2026",
            "href": "measurements/citation-triage/",
            "title": "Um agente consegue citar oito de doze fontes — a parte útil é saber quais quatro não consegue",
            "text": (
                "Uma lista de leitura mista pelo endpoint de citação: registros completos com RIS para\n"
                "          dois terços, e o resto nomeado com precisão suficiente para buscar à mão em vez de\n"
                "          inventar."
            ),
            "figures": [
                "<b>8/12</b> feitas pelo agente",
                "<b>1,09 s</b> por fonte",
                "<b>4</b> nomeadas, não adivinhadas",
            ],
        },
        {
            "date": "2 de agosto de 2026",
            "href": "measurements/citation-extraction/",
            "title": "Medido contra o Citoid em amostras aleatórias: mesma cobertura, nada inventado",
            "text": (
                "O serviço da Wikimedia construído sobre os tradutores do Zotero é o parâmetro. Em 18\n"
                "          obras sorteadas ao acaso: cobertura igual, e nenhuma recusa relatada como sucesso."
            ),
            "figures": [
                "<b>13/13</b> campos completos",
                "<b>0</b> falsos relatórios de bloqueio",
                "<b>0,35 s</b> de mediana",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Imprimir em PDF ou capturar a tela? A mesma página medida dos dois jeitos",
            "text": (
                "O Firefox já salva páginas em PDF de graça. Quando vale uma captura? O mesmo artigo\n"
                "          pelas duas vias — e a resposta é mais estreita, e mais útil, do que qualquer um dos\n"
                "          lados costuma admitir."
            ),
            "figures": [
                "<b>1 : 26</b> páginas",
                "<b>9</b> quebras cortam uma frase",
                "captura vence no texto: <b>91,5 %</b>",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Página da web em PDF para OCR: quanto texto realmente sobrevive?",
            "text": (
                "Um PDF de captura de página inteira passado pelo Tesseract e comparado com o artigo de\n"
                "          origem. Inclui o limiar de resolução em que o reconhecimento colapsa."
            ),
            "figures": [
                "<b>92,6 %</b> do vocabulário recuperado",
                "<b>8/8</b> valores críticos",
                "<b>72 dpi</b> ponto de colapso",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/pdf-extension-permissions/",
            "title": "Sua extensão de PDF envia a página?",
            "text": (
                "O que as extensões de PDF atuais declaram em seus manifestos, como verificar em\n"
                "          30 segundos — e a consequência que ninguém menciona: conversores no lado do servidor\n"
                "          não alcançam páginas atrás de um login."
            ),
            "figures": [
                "<b>8</b> extensões examinadas",
                "dados brutos publicados",
            ],
        },
        {
            "date": "1 de agosto de 2026",
            "href": "measurements/extension-permissions-risk/",
            "title": "Uma extensão só é tão perigosa quanto suas permissões permitem",
            "text": (
                "Um ano depois do alerta da Mozilla sobre contas de desenvolvedor roubadas: por que a\n"
                "          pergunta útil não é em quem você confia, mas o que uma extensão comprometida poderia\n"
                "          alcançar."
            ),
            "figures": [
                "tabela de permissões no pior caso",
                "checklist de avaliação",
            ],
        },
    ],
    "prinzip_h2": "Como se mede aqui",
    "prinzipien": [
        ("Uma execução de controle, sempre",
         "Antes que um resultado conte, o método tem de falhar onde deve. Uma comparação que não\n"
         "          distingue o caso de referência não mede nada."),
        ("Dados brutos publicados",
         "Os números vêm com o arquivo de onde foram calculados, com carimbo de data. Isso os torna\n"
         "          verificáveis — e significa que ninguém precisa aceitar uma afirmação pela confiança."),
        ("As perdas nomeadas primeiro",
         "Onde a nossa própria ferramenta é pior — tamanho de arquivo, tempo de processamento,\n"
         "          funções ausentes —, isso é dito antes das vantagens. Uma comparação que só elogia\n"
         "          não vale nada."),
        ("Datadas, não atemporais",
         "Cada número carrega a data em que foi levantado. Software muda; uma medição sem data se\n"
         "          torna em silêncio uma afirmação falsa."),
    ],
    "tools_h2": "Ferramentas",
    "tools_sub": (
        "Software construído aqui, documentado como tudo o mais neste site — incluindo o que não\n"
        "      consegue fazer. Aparece em algumas das medições acima; isso é declarado em cada uma."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Extensão do Firefox que salva uma página da web inteira como um PDF contínuo. Roda no\n"
                "          dispositivo, pede <code>activeTab</code> em vez de acesso a todos os sites, funciona\n"
                "          no Firefox para Android. Licença MIT. Opcionalmente grava no PDF a citação que a\n"
                "          página declara — autores, DOI, licença, momento da consulta —, com um registro RIS\n"
                "          ao lado."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Endpoint de citação em <code>/mcp</code>",
            "text": (
                "Dê uma URL, receba o que essa página declara sobre si como registro estruturado com\n"
                "          RIS e BibTeX — ou uma recusa nomeada quando a página se revela um paywall, um erro\n"
                "          ou uma verificação de bots em vez de uma obra. Sem conta e sem chave. Fala MCP para\n"
                "          clientes de IA e HTTP simples para todo o resto."
            ),
            "figures": [
                "<b>7 de 10</b> fontes acadêmicas completas",
                "<b>0,45 s</b> de mediana",
                "<b>3 ago 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Receitas: uma lista de leitura transformada em bibliografia",
            "text": (
                "Instruções completas e executáveis para colocar o endpoint de citação nas ferramentas\n"
                "          em que as pessoas realmente trabalham: um laço de shell que transforma\n"
                "          <code>reading-list.txt</code> num <code>.ris</code> importável para Zotero ou Citavi,\n"
                "          uma linha para conectar o Claude Code, a entrada de servidor remoto para o Claude\n"
                "          Desktop e outros clientes MCP, e o mínimo em Python. Cada uma foi executada antes de\n"
                "          ser escrita."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Confira qualquer número",
    "nach_sub": (
        "Tudo aqui tem método, dados brutos e uma execução de controle — para poder ser conferido,\n"
        "      não para precisar ser acreditado."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "A contribuição mais útil é uma contramedição que dá um resultado diferente",
            "text": (
                "Quatro pontos onde os números publicados têm mais chance de balançar são nomeados\n"
                "          explicitamente — começando pelas dez de vinte fontes cujas quatro recusas são\n"
                "          bloqueios contra um endereço de data center. De uma rede doméstica a taxa deveria\n"
                "          ser maior, e isso não está medido."
            ),
            "figures": [
                "<b>4</b> pontos fracos nomeados",
                "<b>9</b> conjuntos de dados, CC BY 4.0",
                "tarefas abertas no <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Para agentes de IA: regras, construção, limites",
            "text": (
                "O projeto é montado para que um agente possa trabalhar nele sem antes perguntar a\n"
                "          ninguém. As tarefas abertas são servidas em formato legível por máquina pela ferramenta\n"
                "          <code>open_work</code> em <a href=\"for-agents/\">/mcp</a> — com rótulos, um trecho e as\n"
                "          cinco regras que aqui são diferentes do habitual."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Transparência",
    "disc_p1": (
        "Este site é operado pelo desenvolvedor do <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, que aparece em várias das medições acima. Isso é indicado em cada artigo em\n"
        "        que é relevante, e a ferramenta está abertamente em <code>/tools/</code> em vez de\n"
        "        escondida atrás de um enquadramento neutro."
    ),
    "disc_p2": (
        "Os números sobre produtos de terceiros vêm exclusivamente de dados publicamente declarados —\n"
        "        manifestos e descrições de loja — com a data de consulta informada. Nenhum produto foi\n"
        "        descompilado, e nada se afirma sobre as intenções de qualquer fornecedor. Correções são\n"
        "        bem-vindas via\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">issues no GitHub</a> e\n"
        "        são aplicadas."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">Sobre</a> · <a href="privacy.html">Privacidade</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Código-fonte</a> · '
        '<a href="disclaimer/">Aviso legal</a>'
    ),
    "foot_2": "Conteúdo licenciado para reutilização com atribuição. Software sob licença MIT.",
}

# ---------------------------------------------------------------- Русский ----
TEXTE["ru"] = {
    "h1": "Сохраните веб-страницу, которая понадобится вам позже.",
    "tagline1": (
        'Сохраните страницу целиком одним PDF, который несёт её источник и дату — и превратите\n'
        '      список ссылок в библиографию. <strong>19,3 % источников в реальных библиографиях уже\n'
        '      исчезли</strong>, а у 8,7 % нет ни одной архивной копии.\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">Начните здесь</a> ·\n'
        '      <a href="/for-agents/">для ИИ-агентов</a>'
    ),
    "tagline2": (
        'Измерения, а не мнения: у всего здесь есть <strong>метод, сырые данные и контрольный\n'
        '      прогон</strong>. Что нельзя пересчитать, то не записывается. Что пошло не так,\n'
        '      записывается первым.'
    ),
    "dmark": "Инструмент, построенный здесь",
    "dtext": (
        "Сохраняет веб-страницу целиком одним непрерывным PDF — вся прокручиваемая страница на "
        "одном листе. Ничего не обрезано по краям, и ни один разрыв страницы не проходит через "
        "таблицу или предложение. Всё происходит в вашем браузере: без выгрузки, без учётной "
        "записи, без сбора данных. Лицензия MIT, бесплатно, Firefox и Chrome."
    ),
    "dzahlen": [
        "<b>Один лист</b>, а не 26 страниц",
        "<b>Работает за логином</b>",
        "<b>Остаётся на вашем устройстве</b>",
    ],
    "dbeleg": (
        'Каждое утверждение здесь измерено и датировано:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">один лист против 26</a>,\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92,6&nbsp;% текста читается OCR</a>,\n'
        '        <a href="measurements/pdf-extension-permissions/">ноль сетевых запросов</a>.'
    ),
    "ddownload": "Скачать для Firefox",
    "dversion": "Версия 2.33.4 — подписана Mozilla. Устанавливается в один шаг, компьютер и Android.",
    "dohne": "Совсем без магазина",
    "dchrome": "Chrome и Edge",
    "dwas": "Что она умеет",
    "notes_h2": "Заметки",
    "notes_sub": "Отчёты из реальной работы — включая части, которые пошли не так.",
    "notes": [
        {
            "date": "15 августа 2026 г.",
            "href": "how-to/firefox-and-chrome/",
            "title": "Исследователям и студентам: расширение в Firefox и Chrome",
            "text": (
                "Практическая пара к статье для студентов: все способы установки — Firefox на\n"
                "          компьютере и Android, Chrome Web Store и оба пути без магазина —, затем цикл\n"
                "          «захват–цитирование–архив» и четыре настройки, важные для научных работ.\n"
                "          На девяти языках."
            ),
            "figures": [
                "<b>2</b> браузера, 4 способа установки",
                "<b>18</b> полей XMP в PDF",
                "<b>2</b> пути для RIS-записи",
            ],
        },
        {
            "date": "10 августа 2026 г.",
            "href": "how-to/for-students/",
            "title": "Студентам: источник, который сам себя цитирует, выживает и читается машиной",
            "text": (
                "Три вещи идут не так с веб-источником в курсовой: он исчезает, его цитату приходится\n"
                "          перепечатывать вручную, а сохранённый файл — картинка, которую ни один инструмент\n"
                "          не ищет. Что захват делает против каждой — включая шесть источников из двадцати,\n"
                "          которые он возвращает вам. На девяти языках."
            ),
            "figures": [
                "<b>61 %</b> покрытия, как у Citoid",
                "<b>100 %</b> точности против его 79 %",
                "<b>6 из 20</b> возвращены",
            ],
        },
        {
            "date": "3 августа 2026 г.",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "Что ИИ-агент может и чего не может с расширением браузера",
            "text": (
                "Установка в чужой браузер — это по замыслу жест пользователя: ни один магазин не\n"
                "          предоставляет для этого API. Что агент может вместо этого, флаг командной строки,\n"
                "          который ничего не загружает и ничего не говорит, и где между ними двоими делится\n"
                "          работа."
            ),
            "figures": [
                "<b>3</b> вещи, которые агент может",
                "<b>1</b> флаг, который молча не срабатывает",
                "<b>0</b> способов установить за кого-то",
            ],
        },
        {
            "date": "3 августа 2026 г.",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "Источники, которые машина не может процитировать за вас — и как процитировать их всё же",
            "text": (
                "Когда инструмент цитирования возвращает источник, причина — одна из трёх: защита от\n"
                "          ботов, отказ, направленный на сеть, или страница, которая ничего о себе не заявляет.\n"
                "          Каждая требует своей работы, и лишь одна решается открытием страницы в браузере."
            ),
            "figures": [
                "<b>3</b> причины",
                "<b>1</b> решается браузером",
                "<b>2</b> запроса, чтобы их различить",
            ],
        },
        {
            "date": "2 августа 2026 г.",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Этот сайт держит MCP-сервер. Измерено: он меньше файла, с которым соревнуется",
            "text": (
                "Конечная точка на <code>/mcp</code> передаёт наборы данных, методы и читалку цитат\n"
                "          ИИ-клиентам по JSON-RPC — без ключа, без учётной записи. Для чего это на самом деле\n"
                "          годится, и где обычный текстовый файл на том же домене уже справляется."
            ),
            "figures": [
                "<b>4</b> инструмента",
                "<b>1 300</b> токенов всего",
                "<b>1 988</b> в llms.txt",
            ],
        },
        {
            "date": "1 августа 2026 г.",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "Шесть вещей, пошедших не так при создании ПО с ИИ-ассистентом за один день",
            "text": (
                "Неверное предположение о браузерных движках, ложное утверждение, пойманное до\n"
                "          публикации, 22 локальных пути в одном коммите от публичного репозитория — и ещё три.\n"
                "          Отсортированы по тому, что их реально поймало: два нашлись по везению, один — ничем."
            ),
            "figures": [
                "<b>3 из 6</b> пойманы проверкой внешнего источника",
                "<b>1</b> до сих пор не проверен в продакшене",
            ],
        },
    ],
    "meas_h2": "Измерения",
    "meas_sub": "Каждое — с командами для его повторения и с сырыми данными за ним.",
    "meas": [
        {
            "date": "3 августа 2026 г.",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "Установка расширения браузера без единого щелчка — и удаление обратно",
            "text": (
                "Четыре пути, в обе стороны. Один устанавливает и удаляет подписанную магазинную сборку\n"
                "          за 4,1 секунды без окна и без прав администратора — а сами две команды занимают\n"
                "          0,24 с; цена — запуск браузера, а не работа. Путь со щелчком занял 179 секунд,\n"
                "          сообщил об успехе на каждом шаге и не установил ничего: щелчок в пустоту —\n"
                "          действительный щелчок. Быстрый путь не считается в статистике пользователей магазина —\n"
                "          и это суть, а не недостаток."
            ),
            "figures": [],
        },
        {
            "date": "3 августа 2026 г.",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "Двадцать ссылок, десять цитат: что машина доводит до конца, а что возвращает",
            "text": (
                "Список чтения в библиографию, от начала до конца. Граница проходит не между платным и\n"
                "          бесплатным — она проходит между страницами, построенными, чтобы их цитировали, и\n"
                "          страницами, построенными, чтобы их читали. Научные издательства дают записи в обоих\n"
                "          случаях; статистические порталы, торговые палаты и газеты не дают никаких — и не\n"
                "          потому, что защищаются."
            ),
            "figures": [
                "<b>10/20</b> полных записей",
                "<b>1</b> защита от ботов",
                "<b>5</b> страниц без единого заявления",
            ],
        },
        {
            "date": "3 августа 2026 г.",
            "href": "measurements/citation-triage/",
            "title": "Агент может процитировать восемь из двенадцати источников — полезно знать, какие четыре он не может",
            "text": (
                "Смешанный список чтения через конечную точку цитирования: полные записи с RIS для\n"
                "          двух третей, а остальные названы достаточно точно, чтобы забрать их вручную вместо\n"
                "          выдумывания."
            ),
            "figures": [
                "<b>8/12</b> сделано агентом",
                "<b>1,09 с</b> на источник",
                "<b>4</b> названы, а не угаданы",
            ],
        },
        {
            "date": "2 августа 2026 г.",
            "href": "measurements/citation-extraction/",
            "title": "Измерено против Citoid на случайных выборках: то же покрытие, ничего выдуманного",
            "text": (
                "Эталон — сервис Wikimedia, построенный на трансляторах Zotero. На 18 случайно\n"
                "          извлечённых произведениях: одинаковое покрытие, и ни одного отказа, доложенного\n"
                "          как успех."
            ),
            "figures": [
                "<b>13/13</b> полей заполнены",
                "<b>0</b> ложных сообщений о блокировке",
                "<b>0,35 с</b> медиана",
            ],
        },
        {
            "date": "1 августа 2026 г.",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "Печатать в PDF или захватывать экран? Одна и та же страница, измеренная двумя способами",
            "text": (
                "Firefox уже сохраняет страницы в PDF бесплатно. Так когда окупается захват? Одна и та\n"
                "          же статья обоими путями — и ответ уже и полезнее, чем обычно признаёт любая из сторон."
            ),
            "figures": [
                "<b>1 : 26</b> страниц",
                "<b>9</b> разрывов режут предложение",
                "захват ведёт по тексту: <b>91,5 %</b>",
            ],
        },
        {
            "date": "1 августа 2026 г.",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "Веб-страница в PDF для OCR: сколько текста реально выживает?",
            "text": (
                "PDF полностраничного скриншота прогнан через Tesseract и сравнён с исходной статьёй.\n"
                "          Включая порог разрешения, на котором распознавание рушится."
            ),
            "figures": [
                "<b>92,6 %</b> словаря восстановлено",
                "<b>8/8</b> критических значений",
                "<b>72 dpi</b> точка обвала",
            ],
        },
        {
            "date": "1 августа 2026 г.",
            "href": "measurements/pdf-extension-permissions/",
            "title": "Выгружает ли ваше PDF-расширение страницу?",
            "text": (
                "Что декларируют актуальные PDF-расширения в своих манифестах, как проверить это за\n"
                "          30 секунд — и следствие, о котором никто не говорит: серверные конвертеры не достают\n"
                "          страницы за логином."
            ),
            "figures": [
                "<b>8</b> расширений исследовано",
                "сырые данные опубликованы",
            ],
        },
        {
            "date": "1 августа 2026 г.",
            "href": "measurements/extension-permissions-risk/",
            "title": "Расширение опасно ровно настолько, насколько позволяют его разрешения",
            "text": (
                "Год спустя после предупреждения Mozilla об украденных учётках разработчиков: почему\n"
                "          полезный вопрос не «кому вы доверяете», а «до чего дотянется скомпрометированное\n"
                "          расширение»."
            ),
            "figures": [
                "таблица разрешений наихудшего случая",
                "контрольный список оценки",
            ],
        },
    ],
    "prinzip_h2": "Как здесь измеряют",
    "prinzipien": [
        ("Контрольный прогон — всегда",
         "Прежде чем результат засчитывается, метод должен отказать там, где должен. Сравнение,\n"
         "          не различающее эталонный случай, не измеряет ничего."),
        ("Сырые данные опубликованы",
         "Цифры приходят с файлом, из которого они вычислены, и с меткой времени. Это делает их\n"
         "          проверяемыми — и значит, никому не нужно принимать утверждение на веру."),
        ("Потери названы первыми",
         "Где наш собственный инструмент хуже — размер файла, время обработки, недостающие функции —,\n"
         "          сказано до преимуществ. Сравнение, которое только льстит, ничего не стоит."),
        ("Датировано, а не вне времени",
         "Каждая цифра несёт дату своего снятия. Программы меняются; измерение без даты тихо\n"
         "          превращается в ложное утверждение."),
    ],
    "tools_h2": "Инструменты",
    "tools_sub": (
        "Программы, построенные здесь, задокументированы как всё на этом сайте — включая то, чего\n"
        "      они не умеют. Они встречаются в некоторых измерениях выше; это раскрыто в каждом из них."
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "Расширение Firefox, сохраняющее веб-страницу целиком одним непрерывным PDF. Работает\n"
                "          на устройстве, запрашивает <code>activeTab</code> вместо доступа ко всем сайтам,\n"
                "          работает на Firefox для Android. Лицензия MIT. Опционально записывает в PDF цитату,\n"
                "          которую заявляет страница — авторы, DOI, лицензия, время обращения —, с RIS-записью\n"
                "          рядом."
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "Конечная точка цитирования на <code>/mcp</code>",
            "text": (
                "Дайте ей URL — получите то, что эта страница заявляет о себе, в виде структурированной\n"
                "          записи с RIS и BibTeX, или именованный отказ, если страница оказывается пейволом,\n"
                "          ошибкой или проверкой на бота, а не произведением. Ни учётной записи, ни ключа.\n"
                "          Говорит на MCP для ИИ-клиентов и на простом HTTP для всего остального."
            ),
            "figures": [
                "<b>7 из 10</b> научных источников полные",
                "<b>0,45 с</b> медиана",
                "<b>3 авг 2026</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "Рецепты: список чтения в библиографию",
            "text": (
                "Полные, исполняемые инструкции, как встроить конечную точку цитирования в инструменты,\n"
                "          в которых люди реально работают: цикл shell, превращающий <code>reading-list.txt</code>\n"
                "          в импортируемый <code>.ris</code> для Zotero или Citavi, одна строка для подключения\n"
                "          Claude Code, запись удалённого сервера для Claude Desktop и других MCP-клиентов и\n"
                "          минимум на Python. Каждая была выполнена до того, как записана."
            ),
            "figures": [],
        },
    ],
    "nach_h2": "Перепроверьте любую цифру",
    "nach_sub": (
        "У всего здесь есть метод, сырые данные и контрольный прогон — чтобы это можно было\n"
        "      перепроверить, а не чтобы этому приходилось верить."
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "Самый полезный вклад — контр-измерение с другим результатом",
            "text": (
                "Явно названы четыре места, где опубликованные цифры наиболее вероятно шатаются —\n"
                "          начиная с десяти из двадцати источников, чьи четыре отказа были блокировками адреса\n"
                "          дата-центра. Из домашней сети показатель должен быть выше, и это не измерено."
            ),
            "figures": [
                "<b>4</b> названных слабых места",
                "<b>9</b> наборов данных, CC BY 4.0",
                "открытые задачи на <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "Для ИИ-агентов: правила, устройство, границы",
            "text": (
                "Проект устроен так, что агент может работать над ним, ни у кого предварительно не\n"
                "          спрашивая. Открытые задачи машиночитаемо выдаёт инструмент <code>open_work</code> на\n"
                "          <a href=\"for-agents/\">/mcp</a> — с метками, выдержкой и пятью правилами, которые здесь\n"
                "          отличаются от обычных."
            ),
            "figures": [],
        },
    ],
    "disc_h3": "Раскрытие",
    "disc_p1": (
        "Этот сайт ведёт разработчик <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a>, который встречается в нескольких измерениях выше. Это указано в каждой\n"
        "        статье, где это уместно, и инструмент открыто лежит под <code>/tools/</code>, а не\n"
        "        спрятан за нейтральной рамкой."
    ),
    "disc_p2": (
        "Цифры о чужих продуктах происходят исключительно из публично заявленных данных — манифестов\n"
        "        и описаний в магазинах — с указанной датой обращения. Ни один продукт не был\n"
        "        декомпилирован, и ничего не утверждается о намерениях какого-либо поставщика.\n"
        "        Исправления приветствуются через\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">issues на GitHub</a> и\n"
        "        применяются."
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">О сайте</a> · <a href="privacy.html">Конфиденциальность</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">Исходный код</a> · '
        '<a href="disclaimer/">Отказ от ответственности</a>'
    ),
    "foot_2": "Содержимое лицензировано для переиспользования с указанием авторства. Программы — под лицензией MIT.",
}

# ---------------------------------------------------------------- 中文(简体) ----
TEXTE["zh-CN"] = {
    "h1": "留住你以后会用到的网页。",
    "tagline1": (
        '把整个页面保存为一份带来源和日期的 PDF——并把一串链接变成参考文献列表。\n'
        '      <strong>真实参考文献中 19.3% 的来源已经消失</strong>,8.7% 的来源在任何地方都没有存档副本。\n'
        '      <a href="/how-to/save-a-webpage-as-pdf/">从这里开始</a> ·\n'
        '      <a href="/for-agents/">面向 AI 代理</a>'
    ),
    "tagline2": (
        '要测量,不要观点:这里的一切都有<strong>方法、原始数据和对照运行</strong>。无法复算的数字\n'
        '      不写下来;出了差错的事情最先写下来。'
    ),
    "dmark": "这里打造的工具",
    "dtext": (
        "把整个网页保存为一份连续的 PDF——整个可滚动的页面在一张纸上。边缘无裁切,也没有"
        "穿过表格或句子的分页符。一切都在你的浏览器中发生:无上传、无账户、无数据收集。"
        "MIT 许可,免费,支持 Firefox 和 Chrome。"
    ),
    "dzahlen": [
        "<b>一张纸</b>,而不是 26 页",
        "<b>在登录之后也能用</b>",
        "<b>留在你的设备上</b>",
    ],
    "dbeleg": (
        '这里的每一项主张都经过测量并注明日期:\n'
        '        <a href="measurements/print-to-pdf-vs-screenshot/">一张纸对 26 页</a>、\n'
        '        <a href="measurements/webpage-to-pdf-for-ocr/">92.6% 的文本可被 OCR 读取</a>、\n'
        '        <a href="measurements/pdf-extension-permissions/">零网络请求</a>。'
    ),
    "ddownload": "下载 Firefox 版",
    "dversion": "版本 2.33.4——由 Mozilla 签名。桌面端和 Android 均可一步安装。",
    "dohne": "完全不经过商店",
    "dchrome": "Chrome 和 Edge",
    "dwas": "功能介绍",
    "notes_h2": "笔记",
    "notes_sub": "来自真实工作的构建记录——包括出错的部分。",
    "notes": [
        {
            "date": "2026年8月15日",
            "href": "how-to/firefox-and-chrome/",
            "title": "致研究人员和学生:Firefox 与 Chrome 中的扩展",
            "text": (
                "学生篇的实践姊妹篇:所有安装途径——桌面端与 Android 的 Firefox、Chrome 应用商店,\n"
                "          以及两条不经商店的路径——然后是“捕获—引用—归档”工作流,以及对论文至关重要\n"
                "          的四项设置。以九种语言提供。"
            ),
            "figures": [
                "<b>2</b> 款浏览器,4 条安装途径",
                "PDF 中的 <b>18</b> 个 XMP 字段",
                "RIS 记录的 <b>2</b> 条路径",
            ],
        },
        {
            "date": "2026年8月10日",
            "href": "how-to/for-students/",
            "title": "致学生:一个能自引出处、能够存活、可被机器读取的来源",
            "text": (
                "网络来源在课程论文中会出三种问题:它会消失;它的引用要手工录入;你保存的文件是\n"
                "          任何工具都无法搜索的图片。一次捕获对这三者各能做什么——包括 20 个来源中它\n"
                "          交还给你的 6 个。以九种语言提供。"
            ),
            "figures": [
                "覆盖率 <b>61%</b>,与 Citoid 持平",
                "准确率 <b>100%</b>,对其 79%",
                "<b>20 个中 6 个</b>被交还",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "notes/what-an-agent-can-do-with-an-extension/",
            "title": "AI 代理用浏览器扩展能做什么、不能做什么",
            "text": (
                "向他人浏览器安装扩展,按设计是用户操作——没有任何商店为此提供 API。代理可以改做\n"
                "          什么、那个什么都不加载也什么都不说的命令行参数,以及两者之间的工作如何划分。"
            ),
            "figures": [
                "代理能做的 <b>3</b> 件事",
                "<b>1</b> 个静默失败的参数",
                "替他人安装的方式 <b>0</b> 种",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "notes/sources-a-machine-cannot-cite/",
            "title": "机器无法替你引用的来源——以及如何照样引用它们",
            "text": (
                "当引用工具把一个来源退回时,原因是三者之一:反机器人防御、针对网络的拒绝,或是\n"
                "          一个对自身毫无声明的页面。三者需要的处理各不相同,而其中只有一种靠用浏览器\n"
                "          打开页面解决。"
            ),
            "figures": [
                "原因 <b>3</b> 种",
                "<b>1</b> 种靠浏览器解决",
                "区分它们需要 <b>2</b> 次请求",
            ],
        },
        {
            "date": "2026年8月2日",
            "href": "notes/mcp-server-what-it-solves/",
            "title": "本站运行一个 MCP 服务器。实测:它比与之竞争的文件还小",
            "text": (
                "<code>/mcp</code> 端点通过 JSON-RPC 向 AI 客户端提供数据集、方法和引用读取器——\n"
                "          无需密钥、无需账户。它究竟有什么用,以及在哪些地方同域名下的一个纯文本文件\n"
                "          就已经够用。"
            ),
            "figures": [
                "工具 <b>4</b> 个",
                "合计 <b>1,300</b> token",
                "llms.txt 中为 <b>1,988</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "notes/building-with-ai-what-went-wrong/",
            "title": "一天之内与 AI 助手开发软件出错的六件事",
            "text": (
                "一个关于浏览器引擎的错误假设、一个在发布前被拦下的虚假陈述、距离公开仓库仅一次\n"
                "          提交的 22 个本地路径——还有三件。按究竟是什么抓住了它们来排序:两个靠运气被\n"
                "          发现,一个什么都没发现它。"
            ),
            "figures": [
                "<b>6 件中 3 件</b>靠核对来源被发现",
                "<b>1</b> 个至今未在生产中验证",
            ],
        },
    ],
    "meas_h2": "测量",
    "meas_sub": "每一项都附有复现它的命令和其背后的原始数据。",
    "meas": [
        {
            "date": "2026年8月3日",
            "href": "measurements/install-an-extension-without-a-click/",
            "title": "无需点击即可安装浏览器扩展,并将其移除",
            "text": (
                "四条路径,双向。其中一条在 4.1 秒内安装并卸载了商店签名版本,无窗口、无管理员权限\n"
                "          ——而两条命令本身只需 0.24 秒,成本在启动浏览器,而非工作。点击路径用了 179 秒,\n"
                "          每一步都报告成功,却什么都没装上:点击空白处也是有效点击。快速路径不计入商店的\n"
                "          用户统计——这正是关键,而非缺陷。"
            ),
            "figures": [],
        },
        {
            "date": "2026年8月3日",
            "href": "measurements/reading-list-to-bibliography/",
            "title": "二十个链接,十条引用:机器完成了什么,交还了什么",
            "text": (
                "把一份阅读清单从头到尾变成参考文献。分界线不在付费与免费之间——而在为被引用而\n"
                "          建的页面和为被阅读而建的页面之间。学术出版社两种情况下都会给出记录;统计门户、\n"
                "          商会和报纸一条也不给,而且并不是因为它们在防御。"
            ),
            "figures": [
                "完整记录 <b>10/20</b>",
                "反机器人防御 <b>1</b>",
                "无任何可声明内容的页面 <b>5</b>",
            ],
        },
        {
            "date": "2026年8月3日",
            "href": "measurements/citation-triage/",
            "title": "代理能引用 12 个来源中的 8 个——有用的部分是知道哪 4 个不行",
            "text": (
                "把一份混合阅读清单送入引用端点:三分之二得到带 RIS 的完整记录,其余的被足够精确地\n"
                "          命名,可以手动获取,而不是靠编造。"
            ),
            "figures": [
                "代理完成 <b>8/12</b>",
                "每个来源 <b>1.09 秒</b>",
                "<b>4</b> 个被指名而非猜测",
            ],
        },
        {
            "date": "2026年8月2日",
            "href": "measurements/citation-extraction/",
            "title": "在随机样本上与 Citoid 对比测量:相同覆盖率,零编造",
            "text": (
                "基于 Zotero 翻译器构建的维基媒体服务是标尺。随机抽取 18 部著作:覆盖率相同,\n"
                "          且没有一次拒答被报为成功。"
            ),
            "figures": [
                "字段完整 <b>13/13</b>",
                "错误的拦截报告 <b>0</b>",
                "中位数 <b>0.35 秒</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/print-to-pdf-vs-screenshot/",
            "title": "打印为 PDF 还是截屏?同一页面两种方式实测",
            "text": (
                "Firefox 已经可以免费把页面存为 PDF。那么什么时候值得捕获?同一篇文章走两条路径\n"
                "          ——答案比任何一方通常承认的都更窄,也更有用。"
            ),
            "figures": [
                "页数 <b>1 : 26</b>",
                "<b>9</b> 处分页截断句子",
                "文本方面捕获领先:<b>91.5%</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/webpage-to-pdf-for-ocr/",
            "title": "网页转 PDF 用于 OCR:究竟有多少文本存活?",
            "text": (
                "把整页截图 PDF 送入 Tesseract,与源文章对比。还包括识别崩溃的分辨率阈值。"
            ),
            "figures": [
                "词汇恢复 <b>92.6%</b>",
                "关键值 <b>8/8</b>",
                "崩溃点 <b>72 dpi</b>",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/pdf-extension-permissions/",
            "title": "你的 PDF 扩展会上传页面吗?",
            "text": (
                "当前 PDF 扩展在清单中声明了什么、如何在 30 秒内验证——以及没人提及的后果:\n"
                "          服务器端转换器够不到登录之后的页面。"
            ),
            "figures": [
                "调查了 <b>8</b> 款扩展",
                "原始数据已公开",
            ],
        },
        {
            "date": "2026年8月1日",
            "href": "measurements/extension-permissions-risk/",
            "title": "扩展的危险程度只取决于其权限允许的范围",
            "text": (
                "在 Mozilla 就开发者账户被钓鱼发出警告一年后:为什么有用的问题不是你信任谁,\n"
                "          而是被攻陷的扩展能够触及什么。"
            ),
            "figures": [
                "最坏情况权限表",
                "评估清单",
            ],
        },
    ],
    "prinzip_h2": "这里如何测量",
    "prinzipien": [
        ("对照运行,每次都有",
         "在结果作数之前,方法必须在应当失败的地方失败。不能区分参照案例的比较,什么也测不到。"),
        ("原始数据公开",
         "数字都附带计算它们的文件和时间戳。这使它们可以被检验——也意味着没有人需要凭信任\n"
         "          接受一个说法。"),
        ("先讲不足",
         "我们自己的工具在哪些方面更差——文件大小、处理时间、缺失的功能——都先讲,再讲优点。\n"
         "          只会讨好的比较一文不值。"),
        ("注明日期,而非脱离时间",
         "每个数字都带有采集日期。软件在变;没有日期的测量会悄悄变成虚假陈述。"),
    ],
    "tools_h2": "工具",
    "tools_sub": (
        "这里构建的软件,与本站其他内容一样记录在案——包括它做不到的事。它出现在上面的一些\n"
        "      测量中;这一点在每一篇里都有披露。"
    ),
    "tools": [
        {
            "href": "tools/full-page-pdf-snap/",
            "title": "Full Page PDF Snap",
            "text": (
                "把整个网页保存为一份连续 PDF 的 Firefox 扩展。在设备上运行,只请求\n"
                "          <code>activeTab</code> 而非全站访问,支持 Android 版 Firefox。MIT 许可。\n"
                "          可选地把页面声明的引用信息——作者、DOI、许可、获取时间——连同一条 RIS 记录\n"
                "          写入 PDF。"
            ),
            "figures": [],
        },
        {
            "href": "notes/mcp-server-what-it-solves/",
            "title": "<code>/mcp</code> 引用端点",
            "text": (
                "给它一个 URL,得到该页面关于自身的结构化记录(含 RIS 和 BibTeX)——或者,当页面\n"
                "          其实是付费墙、错误或机器人检查而非一部著作时,得到一个具名的拒绝。无需账户,\n"
                "          无需密钥。对 AI 客户端说 MCP,对其他一切说普通 HTTP。"
            ),
            "figures": [
                "学术来源 <b>10 个里 7 个</b>完整",
                "中位数 <b>0.45 秒</b>",
                "<b>2026年8月3日</b>",
            ],
        },
        {
            "href": "recipes/",
            "title": "食谱:把阅读清单变成参考文献",
            "text": (
                "把引用端点接入人们实际使用的工具的完整可运行说明:一个把 <code>reading-list.txt</code>\n"
                "          变成可导入 Zotero 或 Citavi 的 <code>.ris</code> 的 shell 循环,连接 Claude Code\n"
                "          的一行命令,Claude Desktop 及其他 MCP 客户端的远程服务器配置,以及 Python 最小\n"
                "          示例。每一条都在写下之前实际运行过。"
            ),
            "figures": [],
        },
    ],
    "nach_h2": "任何数字,都请自己验算",
    "nach_sub": (
        "这里的一切都有方法、原始数据和对照运行——是为了可以被验算,而不是必须被相信。"
    ),
    "nach": [
        {
            "href": "mitmachen/",
            "title": "最有用的贡献,是得出不同结果的复核测量",
            "text": (
                "我们明确指出了公开数字最可能站不住脚的四个地方——首先是 20 个来源中的 10 个,\n"
                "          其 4 次拒绝是针对数据中心地址的封锁。从家庭网络测,比率应该更高,而这尚未测量。"
            ),
            "figures": [
                "指出的薄弱环节 <b>4</b> 处",
                "数据集 <b>9</b> 个,CC BY 4.0",
                "开放任务见 <b>GitHub</b>",
            ],
        },
        {
            "href": "AGENTS.md",
            "title": "面向 AI 代理:规则、构建方式、边界",
            "text": (
                "这个项目被配置成代理无需先询问任何人即可上手工作。开放任务由 <code>open_work</code>\n"
                "          工具在 <a href=\"for-agents/\">/mcp</a> 上以机器可读方式提供——附标签、摘要,以及这里\n"
                "          与常规不同的五条规则。"
            ),
            "figures": [],
        },
    ],
    "disc_h3": "披露",
    "disc_p1": (
        "本站由 <a href=\"tools/full-page-pdf-snap/\">Full Page\n"
        "        PDF Snap</a> 的开发者运营,该工具出现在上面的多项测量中。这一点在每一篇相关文章里\n"
        "        都有说明,而且该工具公开放在 <code>/tools/</code> 下,而不是藏在中立的表述背后。"
    ),
    "disc_p2": (
        "关于其他产品的数字完全来自公开声明的数据——清单文件和商店描述——并注明获取日期。\n"
        "        没有反编译任何产品,也不对任何提供商的意图作任何主张。欢迎通过\n"
        "        <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">GitHub issues</a>\n"
        "        提出更正,并会被采纳。"
    ),
    "foot_1": (
        'Proving Lab · <a href="about/">关于</a> · <a href="privacy.html">隐私</a> · '
        '<a href="https://github.com/Bubu89/full-page-pdf-snap">源代码</a> · '
        '<a href="disclaimer/">免责声明</a>'
    ),
    "foot_2": "内容以署名方式许可再利用。软件采用 MIT 许可。",
}
