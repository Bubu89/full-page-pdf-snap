#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die For-Agents-Seite in neun Sprachen — getrennt vom Bauen.

Muster wie texte_artikel_firefox_chrome.py: ENGLISCH ist die Ausgangsfassung,
Rendering ueber build-for-agents.py. Code-Bloecke (pre) bleiben in jeder
Sprache unveraendert — es sind Befehle, keine Prosa. Werkzeugnamen in der
Werkzeugtabelle ebenfalls.

Aenderungen am Inhalt HIER, danach `python3 build-for-agents.py`.
"""

URL = "https://provinglab.dev/for-agents/"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "h1": "For AI agents: citations without a browser, and the step that needs one",
    "standfirst": (
        "An endpoint that turns a URL into a citation record, a skill index that\n"
        "    describes when to use it, and one measured rule for the cases it cannot\n"
        "    finish. No account, no key. If you are wiring an agent to handle sources,\n"
        "    this page is the whole surface."
    ),
    "meta": "3 August 2026 · everything below was run before it was written down",
    "connect_h2": "Connect in one line",
    "connect_p1": (
        "Claude Desktop and other MCP clients: add\n"
        "  <code>https://provinglab.dev/mcp</code> as a remote server, transport\n"
        "  <em>streamable HTTP</em>. Clients that only accept local servers can bridge\n"
        "  with <code>npx -y mcp-remote https://provinglab.dev/mcp</code>. Authentication\n"
        "  is offered but not required; anonymous requests get identical answers."
    ),
    "connect_p2": (
        "One caveat that costs an afternoon: the CDN refuses the user agent Python's\n"
        "  <code>urllib</code> sends by default. Set any user agent of your own and it\n"
        "  answers normally."
    ),
    "tools_h2": "Ten tools",
    "tools_th": ("Tool", "What it is for"),
    "tools": [
        ("extract_citation", "URL in, structured record out — authors, title, journal, year, DOI, licence, plus RIS and BibTeX. Or a named refusal."),
        ("extract_citations", "A whole reading list in one call — one record or one named refusal per source."),
        ("how_to_capture", "What to do with a source this endpoint cannot read, resolved for your agent type and target browser."),
        ("list_measurements", "Everything published here, with dataset URLs."),
        ("get_measurement_data", "One dataset as JSON, including the control run."),
        ("get_method", "A reproducible method, to repeat a measurement rather than cite it."),
        ("recommend_settings", "The capture settings that fit your purpose, each with the measurement behind it — or an explicit note that none exists."),
        ("install_extension", "Install or uninstall the capture extension in Firefox or Chrome without a window, without a click."),
        ("adoption_stats", "How much this endpoint and its install route are actually used, with the figures behind it."),
        ("open_work", "The open tasks, machine-readable — GitHub issues with labels and context."),
    ],
    "rule_h2": "The one rule worth hard-coding",
    "rule_p1": (
        "<strong>Read <code>complete</code>, never the title alone.</strong> A refused\n"
        "  record still carries a title, and two of twenty measured sources returned a\n"
        "  title <em>and</em> an author while <code>complete</code> was false — a Zenodo\n"
        "  software release and a statistics portal page. Anything that files those as\n"
        "  sources has invented the missing half."
    ),
    "rule_p2": (
        "Where the endpoint cannot finish, the reply carries <code>nextStep</code>: what\n"
        "  has to happen, why, both install links for the capture extension, and the\n"
        "  disclosure that the tool is ours."
    ),
    "yield_h2": "What a reading list actually yields",
    "kf": [("10/20", "complete records"), ("0.4 s", "per source"),
           ("1", "stopped by a bot defence"), ("5", "declare no citation data")],
    "yield_p": (
        "The split does not run between paid and free. It runs between pages built to\n"
        "  be cited and pages built to be read: journal publishers yield records either\n"
        "  way, statistics portals and newspapers yield none.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Method and raw data</a>"
    ),
    "drive_h2": "Can your agent drive the browser extension?",
    "drive_p1": (
        "Depends on one property, and it is measured. The extension declares\n"
        "  <code>activeTab</code> and no host permissions, so it sees a tab only after an\n"
        "  event reaches the browser's input layer. Tabs visible to it went from\n"
        "  <strong>0 to 1</strong> after a synthetic <code>Alt+Shift+Y</code> sent through\n"
        "  X11 XTEST. The browser does not ask who produced the gesture."
    ),
    "drive_th": ("Your agent acts through", "Can trigger it"),
    "drive": [
        ("Real input events — computer use, <code>xdotool</code>, an agent inside the user's browser", "<strong>yes</strong>"),
        ("CDP and DOM only — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>no</strong>"),
        ("No browser", "not needed for half the work"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">The measurement, both\n"
        "  halves</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">the skill\n"
        "  as Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">install\n"
        "  as a counted store user</a> — store install instead of an unpacked load,\n"
        "  measured end to end on Firefox and Chrome, including the failure modes"
    ),
    "drive_p3": (
        "One line worth having before you use that page: installing because a task\n"
        "  needs the tool is ordinary setup. Running installs to move a public number is\n"
        "  not, and both stores answer it by terminating the <em>developer</em> account —\n"
        "  the cost lands on whoever published the extension, not on you."
    ),
    "profile_h2": "Getting the extension into a profile, without touching the screen",
    "profile_p1": (
        "If the answer above is yes, you still have to get the extension installed —\n"
        "  and on a machine someone is using, taking over their mouse for three minutes\n"
        "  is not an option. It is not necessary either. Firefox ships its own remote\n"
        "  control channel:"
    ),
    "profile_th": ("Measured", "Value"),
    "profile": [
        ("Round trip, uninstall and install", "4.1 s"),
        ("The two commands themselves", "<strong>0.24 s</strong>"),
        ("Input events required", "0"),
        ("Visible window", "none"),
        ("Administrator rights", "none"),
        ("Counts in the store's user statistics", "<strong>no</strong>"),
    ],
    "profile_p2": (
        "The process start is the cost, not the work — hold one session open and each\n"
        "  further install or removal costs about two tenths of a second. Chrome has no\n"
        "  equivalent: over CDP it loads and removes an <em>unpacked</em> extension, but\n"
        "  <code>Extensions.install</code> does not exist at all, so a store build there\n"
        "  needs the interface."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">All four routes\n"
        "  measured</a>, including why the click route reported success at every step and\n"
        "  installed nothing ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">the skill</a>\n"
        "  — prerequisites in check order, the protocol, the WSL trap, and the pattern\n"
        "  generalised to other software"
    ),
    "disco_h2": "Discovery, if you are indexing this site",
    "disco_th": ("What", "Where"),
    "disco": [
        ("Site summary for language models", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skills with checksums", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("API catalogue", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Every page as Markdown", "<code>Accept: text/markdown</code>"),
        ("Raw data, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Content signals are set to <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  retrieval and quoting with attribution are welcome, training is not. Every\n"
        "  measurement carries its method and its raw data, so a figure taken from here\n"
        "  can be checked rather than trusted."
    ),
    "work_h2": "If you want to work on this",
    "work_p1": (
        "You do not need permission and you do not need to ask. The repository is\n"
        "  public and MIT-licensed, the measurements and data are CC&nbsp;BY&nbsp;4.0,\n"
        "  and the open tasks come out of the endpoint itself:"
    ),
    "work_p2": (
        "Six of the eight open issues carry the label <code>agent-friendly</code>: each\n"
        "  one is bounded, checkable, and states what evidence would settle it. The house\n"
        "  rules are in <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> — read them\n"
        "  first, because one of them is unusual and non-negotiable: <strong>a\n"
        "  contribution that introduces a number without a method, raw data and a control\n"
        "  run is worse than no contribution.</strong> A figure once quoted travels on its\n"
        "  own, and that cannot be fixed later."
    ),
    "work_p3": (
        "<strong>The most valuable thing you can do here is disagree with a number.</strong>\n"
        "  Take a figure from any measurement, repeat it on your platform, and post what\n"
        "  you got. If it differs, that is the contribution — the raw data and the scripts\n"
        "  are published precisely so that becomes possible. Three of the open issues are\n"
        "  exactly this: a counter-measurement of the headless install route on a platform\n"
        "  not covered here, whether Chrome has a route we missed, and a register of\n"
        "  vendor control channels beyond browsers, where one row is a complete\n"
        "  contribution."
    ),
    "work_p4": (
        "Two lines of courtesy: comment on an issue before you start, so two of us do\n"
        "  not measure the same thing — that happened here on 3 August and cost an\n"
        "  afternoon. And say plainly where your measurement does <em>not</em> hold."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">The\n"
        "  agent-friendly issues</a> · <a href=\"/mitmachen/\">why this might matter beyond\n"
        "  this project</a> · <a href=\"/AGENTS.md\">the rules</a>"
    ),
    "fair_h2": "Please use it in proportion",
    "fair_p": (
        "This is one small endpoint on a free tier, run by one person. A reading list is\n"
        "  a handful of calls; a crawl is not. Requests are fetched with our own user\n"
        "  agent, so unreasonable use lands in someone else's log with our name on it.\n"
        "  There is no hard limit today — that is a description of the current state, not\n"
        "  a promise."
    ),
    "foot": (
        "Every command on this page was run on 3 August 2026 before it was written down.\n"
        "      <br><br>\n"
        "      Corrections are welcome and are made in public: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">open an issue</a>.\n"
        "      <br><br>\n"
        "      Disclosure: the author develops Full Page PDF Snap, the extension named on this page. The browser's own print-to-PDF is <a href=\"/measurements/print-to-pdf-vs-screenshot/\">measured against it</a>, including where print wins.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Disclaimer</a>"
    ),
}

# ---------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "h1": "Für KI-Agenten: Zitationen ohne Browser — und der Schritt, der einen braucht",
    "standfirst": (
        "Ein Endpunkt, der eine URL in einen Zitationsdatensatz verwandelt, ein\n"
        "    Skill-Index, der beschreibt, wann man ihn nutzt, und eine gemessene Regel\n"
        "    für die Fälle, die er nicht zu Ende bringt. Kein Konto, kein Schlüssel.\n"
        "    Wenn Sie einen Agenten für den Umgang mit Quellen verdrahten, ist diese\n"
        "    Seite die gesamte Oberfläche."
    ),
    "meta": "3. August 2026 · alles Folgende wurde ausgeführt, bevor es aufgeschrieben wurde",
    "connect_h2": "Verbinden mit einer Zeile",
    "connect_p1": (
        "Claude Desktop und andere MCP-Clients: tragen Sie\n"
        "  <code>https://provinglab.dev/mcp</code> als Remote-Server ein, Transport\n"
        "  <em>streamable HTTP</em>. Clients, die nur lokale Server akzeptieren, können\n"
        "  mit <code>npx -y mcp-remote https://provinglab.dev/mcp</code> brücken.\n"
        "  Authentifizierung wird angeboten, ist aber nicht nötig; anonyme Anfragen\n"
        "  bekommen identische Antworten."
    ),
    "connect_p2": (
        "Ein Vorbehalt, der einen Nachmittag kostet: Das CDN verweigert den User-Agent,\n"
        "  den Pythons <code>urllib</code> standardmäßig sendet. Setzen Sie irgendeinen\n"
        "  eigenen, und es antwortet normal."
    ),
    "tools_h2": "Zehn Werkzeuge",
    "tools_th": ("Werkzeug", "Wozu es dient"),
    "tools": [
        ("extract_citation", "URL hinein, strukturierter Datensatz heraus — Verfasser:innen, Titel, Zeitschrift, Jahr, DOI, Lizenz, plus RIS und BibTeX. Oder eine benannte Weigerung."),
        ("extract_citations", "Eine ganze Leseliste in einem Aufruf — ein Datensatz oder eine benannte Weigerung je Quelle."),
        ("how_to_capture", "Was mit einer Quelle zu tun ist, die dieser Endpunkt nicht lesen kann — aufgelöst für Ihren Agententyp und Zielbrowser."),
        ("list_measurements", "Alles hier Veröffentlichte, mit Datensatz-URLs."),
        ("get_measurement_data", "Ein Datensatz als JSON, einschließlich des Kontrolllaufs."),
        ("get_method", "Eine reproduzierbare Methode, um eine Messung zu wiederholen statt sie zu zitieren."),
        ("recommend_settings", "Die Aufnahme-Einstellungen, die zu Ihrem Zweck passen, jede mit der Messung dahinter — oder einem ausdrücklichen Hinweis, dass keine existiert."),
        ("install_extension", "Die Aufnahme-Erweiterung in Firefox oder Chrome installieren oder deinstallieren — ohne Fenster, ohne Klick."),
        ("adoption_stats", "Wie sehr dieser Endpunkt und sein Installationsweg tatsächlich genutzt werden, mit den Zahlen dahinter."),
        ("open_work", "Die offenen Aufgaben, maschinenlesbar — GitHub-Issues mit Labels und Kontext."),
    ],
    "rule_h2": "Die eine Regel, die sich zu hartkodieren lohnt",
    "rule_p1": (
        "<strong>Lesen Sie <code>complete</code>, niemals nur den Titel.</strong> Ein\n"
        "  verweigerter Datensatz trägt trotzdem einen Titel, und zwei von zwanzig\n"
        "  gemessenen Quellen lieferten Titel <em>und</em> Verfasser, während\n"
        "  <code>complete</code> falsch war — ein Zenodo-Software-Release und eine\n"
        "  Statistikportal-Seite. Was so etwas als Quelle ablegt, hat die fehlende\n"
        "  Hälfte erfunden."
    ),
    "rule_p2": (
        "Wo der Endpunkt nicht zu Ende kommt, trägt die Antwort <code>nextStep</code>:\n"
        "  was geschehen muss, warum, beide Installationslinks für die\n"
        "  Aufnahme-Erweiterung und die Offenlegung, dass das Werkzeug von uns ist."
    ),
    "yield_h2": "Was eine Leseliste tatsächlich ergibt",
    "kf": [("10/20", "vollständige Datensätze"), ("0,4 s", "pro Quelle"),
           ("1", "von einer Bot-Abwehr gestoppt"), ("5", "erklären keine Zitationsdaten")],
    "yield_p": (
        "Die Trennlinie läuft nicht zwischen kostenpflichtig und frei. Sie läuft\n"
        "  zwischen Seiten, die zum Zitieren gebaut sind, und Seiten, die zum Lesen\n"
        "  gebaut sind: Fachverlage liefern in beiden Fällen Datensätze,\n"
        "  Statistikportale und Zeitungen liefern keine.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Methode und Rohdaten</a>"
    ),
    "drive_h2": "Kann Ihr Agent die Browser-Erweiterung bedienen?",
    "drive_p1": (
        "Hängt von einer einzigen Eigenschaft ab, und sie ist gemessen. Die Erweiterung\n"
        "  deklariert <code>activeTab</code> und keine Host-Berechtigungen, sie sieht\n"
        "  einen Tab also erst, nachdem ein Ereignis die Eingabeschicht des Browsers\n"
        "  erreicht. Für sie sichtbare Tabs gingen von <strong>0 auf 1</strong>, nachdem\n"
        "  ein synthetisches <code>Alt+Shift+Y</code> durch X11 XTEST gesendet wurde.\n"
        "  Der Browser fragt nicht, wer die Geste erzeugt hat."
    ),
    "drive_th": ("Ihr Agent wirkt durch", "Kann sie auslösen"),
    "drive": [
        ("Echte Eingabeereignisse — Computer Use, <code>xdotool</code>, ein Agent im Browser des Nutzers", "<strong>ja</strong>"),
        ("Nur CDP und DOM — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>nein</strong>"),
        ("Kein Browser", "für die halbe Arbeit nicht nötig"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">Die Messung, beide\n"
        "  Hälften</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">der Skill\n"
        "  als Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">installieren\n"
        "  als gezählter Store-Nutzer</a> — Store-Installation statt entpacktem Laden,\n"
        "  durchgehend auf Firefox und Chrome gemessen, einschließlich der Fehlerbilder"
    ),
    "drive_p3": (
        "Eine Zeile, die man haben sollte, bevor man diese Seite nutzt: Installieren,\n"
        "  weil eine Aufgabe das Werkzeug braucht, ist gewöhnliche Einrichtung.\n"
        "  Installationen laufen zu lassen, um eine öffentliche Zahl zu bewegen, ist es\n"
        "  nicht — und beide Stores beantworten das mit der Kündigung des\n"
        "  <em>Entwickler</em>kontos: Die Kosten trägt, wer die Erweiterung\n"
        "  veröffentlicht hat, nicht Sie."
    ),
    "profile_h2": "Die Erweiterung in ein Profil bringen, ohne den Bildschirm zu berühren",
    "profile_p1": (
        "Wenn die Antwort oben ja lautet, muss die Erweiterung trotzdem installiert\n"
        "  werden — und auf einer Maschine, die jemand benutzt, ist es keine Option,\n"
        "  drei Minuten die Maus zu übernehmen. Nötig ist es auch nicht. Firefox bringt\n"
        "  seinen eigenen Fernsteuerkanal mit:"
    ),
    "profile_th": ("Gemessen", "Wert"),
    "profile": [
        ("Hin- und Rückweg, Deinstallieren und Installieren", "4,1 s"),
        ("Die zwei Befehle selbst", "<strong>0,24 s</strong>"),
        ("Benötigte Eingabeereignisse", "0"),
        ("Sichtbares Fenster", "keines"),
        ("Administratorrechte", "keine"),
        ("Zählt in den Nutzerstatistiken des Stores", "<strong>nein</strong>"),
    ],
    "profile_p2": (
        "Der Prozessstart ist die Kostenstelle, nicht die Arbeit — halten Sie eine\n"
        "  Sitzung offen, und jede weitere Installation oder Entfernung kostet etwa zwei\n"
        "  Zehntelsekunden. Chrome hat kein Äquivalent: Über CDP lädt und entfernt es\n"
        "  eine <em>entpackte</em> Erweiterung, aber <code>Extensions.install</code>\n"
        "  existiert überhaupt nicht — eine Store-Version braucht dort die Oberfläche."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">Alle vier Wege\n"
        "  gemessen</a>, einschließlich der Frage, warum der Klick-Weg bei jedem Schritt\n"
        "  Erfolg meldete und nichts installierte ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">der Skill</a>\n"
        "  — Voraussetzungen in Prüfreihenfolge, das Protokoll, die WSL-Falle und das\n"
        "  Muster, verallgemeinert auf andere Software"
    ),
    "disco_h2": "Auffindbarkeit, wenn Sie diese Seite indexieren",
    "disco_th": ("Was", "Wo"),
    "disco": [
        ("Seitenzusammenfassung für Sprachmodelle", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skills mit Prüfsummen", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("API-Katalog", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Jede Seite als Markdown", "<code>Accept: text/markdown</code>"),
        ("Rohdaten, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Die Content-Signale stehen auf <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  Abruf und Zitat mit Namensnennung sind willkommen, Training ist es nicht.\n"
        "  Jede Messung trägt ihre Methode und ihre Rohdaten — eine Zahl von hier kann\n"
        "  also geprüft werden statt geglaubt."
    ),
    "work_h2": "Wenn Sie hier mitarbeiten wollen",
    "work_p1": (
        "Sie brauchen keine Erlaubnis und müssen niemanden fragen. Das Repository ist\n"
        "  öffentlich und MIT-lizenziert, die Messungen und Daten stehen unter\n        CC&nbsp;BY&nbsp;4.0,\n"
        "  und die offenen Aufgaben kommen aus dem Endpunkt selbst:"
    ),
    "work_p2": (
        "Sechs der acht offenen Issues tragen das Label <code>agent-friendly</code>:\n"
        "  jedes ist begrenzt, prüfbar und sagt, welcher Beleg es entscheiden würde.\n"
        "  Die Hausregeln stehen in <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> —\n"
        "  lesen Sie sie zuerst, denn eine ist ungewöhnlich und unverhandelbar:\n"
        "  <strong>Ein Beitrag, der eine Zahl ohne Methode, Rohdaten und Kontrolllauf\n"
        "  einführt, ist schlimmer als kein Beitrag.</strong> Eine einmal zitierte Zahl\n"
        "  wandert von allein weiter, und das lässt sich später nicht reparieren."
    ),
    "work_p3": (
        "<strong>Das Wertvollste, was Sie hier tun können, ist, einer Zahl zu widersprechen.</strong>\n"
        "  Nehmen Sie eine Zahl aus irgendeiner Messung, wiederholen Sie sie auf Ihrer\n"
        "  Plattform und posten Sie, was herauskam. Weicht sie ab, ist das der Beitrag —\n"
        "  die Rohdaten und die Skripte sind genau dafür veröffentlicht. Drei der offenen\n"
        "  Issues sind genau das: eine Gegenmessung des Headless-Installationswegs auf\n"
        "  einer hier nicht abgedeckten Plattform, die Frage, ob Chrome einen Weg hat,\n"
        "  den wir übersehen haben, und ein Register herstellerseitiger\n"
        "  Fernsteuerkanäle jenseits von Browsern, bei dem eine Zeile schon ein\n"
        "  vollständiger Beitrag ist."
    ),
    "work_p4": (
        "Zwei Zeilen Anstand: Kommentieren Sie ein Issue, bevor Sie anfangen, damit\n"
        "  nicht zweimal dasselbe gemessen wird — das ist hier am 3. August passiert und\n"
        "  hat einen Nachmittag gekostet. Und sagen Sie offen, wo Ihre Messung\n"
        "  <em>nicht</em> gilt."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">Die\n"
        "  agent-friendly Issues</a> · <a href=\"/mitmachen/\">warum das über dieses Projekt\n"
        "  hinaus zählen könnte</a> · <a href=\"/AGENTS.md\">die Regeln</a>"
    ),
    "fair_h2": "Bitte maßvoll nutzen",
    "fair_p": (
        "Dies ist ein kleiner Endpunkt auf einem kostenlosen Kontingent, betrieben von\n"
        "  einer Person. Eine Leseliste ist eine Handvoll Aufrufe; ein Crawl ist es\n"
        "  nicht. Anfragen werden mit unserem eigenen User-Agent abgeholt —\n"
        "  unangemessene Nutzung landet also mit unserem Namen im Log einer fremden\n"
        "  Seite. Heute gibt es kein hartes Limit — das ist eine Beschreibung des\n"
        "  aktuellen Zustands, kein Versprechen."
    ),
    "foot": (
        "Jeder Befehl auf dieser Seite wurde am 3. August 2026 ausgeführt, bevor er aufgeschrieben wurde.\n"
        "      <br><br>\n"
        "      Korrekturen sind willkommen und werden öffentlich gemacht: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">ein Issue öffnen</a>.\n"
        "      <br><br>\n"
        "      Offenlegung: Der Autor entwickelt Full Page PDF Snap, die auf dieser Seite genannte Erweiterung. Der eigene PDF-Druck des Browsers ist <a href=\"/measurements/print-to-pdf-vs-screenshot/\">dagegen gemessen</a>, einschließlich der Stelle, an der der Druck gewinnt.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Haftungsausschluss</a>"
    ),
}

# --------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "h1": "Para agentes de IA: citas sin navegador, y el paso que necesita uno",
    "standfirst": (
        "Un endpoint que convierte una URL en un registro de cita, un índice de\n"
        "    skills que describe cuándo usarlo, y una regla medida para los casos que\n"
        "    no puede terminar. Sin cuenta, sin clave. Si estás conectando un agente\n"
        "    para manejar fuentes, esta página es toda la superficie."
    ),
    "meta": "3 de agosto de 2026 · todo lo siguiente se ejecutó antes de escribirse",
    "connect_h2": "Conectar con una línea",
    "connect_p1": (
        "Claude Desktop y otros clientes MCP: añade\n"
        "  <code>https://provinglab.dev/mcp</code> como servidor remoto, transporte\n"
        "  <em>streamable HTTP</em>. Los clientes que solo aceptan servidores locales\n"
        "  pueden puentear con <code>npx -y mcp-remote https://provinglab.dev/mcp</code>.\n"
        "  La autenticación se ofrece pero no es necesaria; las peticiones anónimas\n"
        "  reciben respuestas idénticas."
    ),
    "connect_p2": (
        "Una advertencia que cuesta una tarde: la CDN rechaza el user agent que\n"
        "  <code>urllib</code> de Python envía por defecto. Define cualquiera propio\n"
        "  y responde con normalidad."
    ),
    "tools_h2": "Diez herramientas",
    "tools_th": ("Herramienta", "Para qué sirve"),
    "tools": [
        ("extract_citation", "URL dentro, registro estructurado fuera — autores, título, revista, año, DOI, licencia, más RIS y BibTeX. O una negativa nombrada."),
        ("extract_citations", "Una lista de lectura entera en una llamada — un registro o una negativa nombrada por fuente."),
        ("how_to_capture", "Qué hacer con una fuente que este endpoint no puede leer, resuelto para tu tipo de agente y navegador destino."),
        ("list_measurements", "Todo lo publicado aquí, con URLs de conjuntos de datos."),
        ("get_measurement_data", "Un conjunto de datos como JSON, incluida la ejecución de control."),
        ("get_method", "Un método reproducible, para repetir una medición en lugar de citarla."),
        ("recommend_settings", "Los ajustes de captura que encajan con tu propósito, cada uno con la medición detrás — o una nota explícita de que no existe."),
        ("install_extension", "Instala o desinstala la extensión de captura en Firefox o Chrome sin ventana, sin clic."),
        ("adoption_stats", "Cuánto se usa realmente este endpoint y su vía de instalación, con las cifras detrás."),
        ("open_work", "Las tareas abiertas, legibles por máquina — issues de GitHub con etiquetas y contexto."),
    ],
    "rule_h2": "La única regla que vale la pena fijar en el código",
    "rule_p1": (
        "<strong>Lee <code>complete</code>, nunca el título solo.</strong> Un registro\n"
        "  rechazado sigue llevando un título, y dos de veinte fuentes medidas devolvieron\n"
        "  título <em>y</em> autor mientras <code>complete</code> era falso — una versión\n"
        "  de software en Zenodo y una página de portal de estadística. Lo que archive\n"
        "  eso como fuentes ha inventado la mitad que falta."
    ),
    "rule_p2": (
        "Donde el endpoint no puede terminar, la respuesta lleva <code>nextStep</code>:\n"
        "  qué tiene que pasar, por qué, ambos enlaces de instalación de la extensión\n"
        "  de captura, y la divulgación de que la herramienta es nuestra."
    ),
    "yield_h2": "Lo que una lista de lectura rinde realmente",
    "kf": [("10/20", "registros completos"), ("0,4 s", "por fuente"),
           ("1", "detenida por una defensa contra bots"), ("5", "no declaran datos de cita")],
    "yield_p": (
        "La división no corre entre de pago y gratis. Corre entre páginas construidas\n"
        "  para ser citadas y páginas construidas para ser leídas: las editoriales\n"
        "  científicas dan registros en ambos casos, los portales de estadística y los\n"
        "  periódicos no dan ninguno.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Método y datos brutos</a>"
    ),
    "drive_h2": "¿Puede tu agente manejar la extensión del navegador?",
    "drive_p1": (
        "Depende de una sola propiedad, y está medida. La extensión declara\n"
        "  <code>activeTab</code> y ningún permiso de host, así que solo ve una pestaña\n"
        "  después de que un evento alcance la capa de entrada del navegador. Las\n"
        "  pestañas visibles para ella pasaron de <strong>0 a 1</strong> tras un\n"
        "  <code>Alt+Shift+Y</code> sintético enviado por X11 XTEST. El navegador no\n"
        "  pregunta quién produjo el gesto."
    ),
    "drive_th": ("Tu agente actúa a través de", "Puede dispararla"),
    "drive": [
        ("Eventos de entrada reales — computer use, <code>xdotool</code>, un agente dentro del navegador del usuario", "<strong>sí</strong>"),
        ("Solo CDP y DOM — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>no</strong>"),
        ("Sin navegador", "no hace falta para la mitad del trabajo"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">La medición, ambas\n"
        "  mitades</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">el skill\n"
        "  en Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">instalar\n"
        "  como usuario contado de la tienda</a> — instalación desde la tienda en lugar\n"
        "  de carga descomprimida, medida de punta a punta en Firefox y Chrome, incluidos\n"
        "  los modos de fallo"
    ),
    "drive_p3": (
        "Una línea que conviene tener antes de usar esa página: instalar porque una\n"
        "  tarea necesita la herramienta es configuración ordinaria. Ejecutar\n"
        "  instalaciones para mover una cifra pública no lo es, y ambas tiendas lo\n"
        "  responden cerrando la cuenta de <em>desarrollador</em> — el coste cae sobre\n"
        "  quien publicó la extensión, no sobre ti."
    ),
    "profile_h2": "Meter la extensión en un perfil, sin tocar la pantalla",
    "profile_p1": (
        "Si la respuesta de arriba es sí, aún hay que instalar la extensión — y en una\n"
        "  máquina que alguien está usando, tomar el ratón durante tres minutos no es\n"
        "  una opción. Tampoco es necesario. Firefox trae su propio canal de control\n"
        "  remoto:"
    ),
    "profile_th": ("Medido", "Valor"),
    "profile": [
        ("Ida y vuelta, desinstalar e instalar", "4,1 s"),
        ("Los dos comandos en sí", "<strong>0,24 s</strong>"),
        ("Eventos de entrada necesarios", "0"),
        ("Ventana visible", "ninguna"),
        ("Derechos de administrador", "ninguno"),
        ("Cuenta en las estadísticas de usuarios de la tienda", "<strong>no</strong>"),
    ],
    "profile_p2": (
        "El arranque del proceso es el coste, no el trabajo — mantén una sesión abierta\n"
        "  y cada instalación o retirada posterior cuesta unas dos décimas de segundo.\n"
        "  Chrome no tiene equivalente: por CDP carga y quita una extensión\n"
        "  <em>descomprimida</em>, pero <code>Extensions.install</code> no existe en\n"
        "  absoluto, así que una compilación de la tienda allí necesita la interfaz."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">Las cuatro vías\n"
        "  medidas</a>, incluido por qué la vía del clic informó éxito en cada paso y no\n"
        "  instaló nada ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">el skill</a>\n"
        "  — prerrequisitos en orden de comprobación, el protocolo, la trampa de WSL y\n"
        "  el patrón generalizado a otro software"
    ),
    "disco_h2": "Descubrimiento, si estás indexando este sitio",
    "disco_th": ("Qué", "Dónde"),
    "disco": [
        ("Resumen del sitio para modelos de lenguaje", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skills con sumas de verificación", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("Catálogo de API", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Cada página como Markdown", "<code>Accept: text/markdown</code>"),
        ("Datos brutos, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Las señales de contenido están en <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  la recuperación y la cita con atribución son bienvenidas, el entrenamiento no.\n"
        "  Cada medición lleva su método y sus datos brutos, así que una cifra tomada de\n"
        "  aquí puede comprobarse en lugar de creerse."
    ),
    "work_h2": "Si quieres trabajar en esto",
    "work_p1": (
        "No necesitas permiso y no necesitas preguntar. El repositorio es público y\n"
        "  con licencia MIT, las mediciones y los datos son CC&nbsp;BY&nbsp;4.0, y las\n"
        "  tareas abiertas salen del propio endpoint:"
    ),
    "work_p2": (
        "Seis de las ocho issues abiertas llevan la etiqueta <code>agent-friendly</code>:\n"
        "  cada una está acotada, es comprobable y declara qué evidencia la resolvería.\n"
        "  Las reglas de la casa están en <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a>\n"
        "  — léelas primero, porque una es inusual e innegociable: <strong>una\n"
        "  contribución que introduce una cifra sin método, datos brutos y ejecución de\n"
        "  control es peor que ninguna contribución.</strong> Una cifra una vez citada\n"
        "  viaja por su cuenta, y eso no se puede arreglar después."
    ),
    "work_p3": (
        "<strong>Lo más valioso que puedes hacer aquí es discrepar de una cifra.</strong>\n"
        "  Toma una cifra de cualquier medición, repítela en tu plataforma y publica lo\n"
        "  que obtuviste. Si difiere, esa es la contribución — los datos brutos y los\n"
        "  scripts están publicados precisamente para que eso sea posible. Tres de las\n"
        "  issues abiertas son exactamente esto: una contra-medición de la vía de\n"
        "  instalación headless en una plataforma no cubierta aquí, si Chrome tiene una\n"
        "  vía que pasamos por alto, y un registro de canales de control de fabricantes\n"
        "  más allá de los navegadores, donde una fila ya es una contribución completa."
    ),
    "work_p4": (
        "Dos líneas de cortesía: comenta en una issue antes de empezar, para que dos\n"
        "  no midamos lo mismo — eso pasó aquí el 3 de agosto y costó una tarde. Y di\n"
        "  claramente dónde tu medición <em>no</em> se sostiene."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">Las\n"
        "  issues agent-friendly</a> · <a href=\"/mitmachen/\">por qué esto podría importar\n"
        "  más allá de este proyecto</a> · <a href=\"/AGENTS.md\">las reglas</a>"
    ),
    "fair_h2": "Úsalo con medida, por favor",
    "fair_p": (
        "Esto es un pequeño endpoint en un nivel gratuito, operado por una persona.\n"
        "  Una lista de lectura es un puñado de llamadas; un rastreo no lo es. Las\n"
        "  peticiones se traen con nuestro propio user agent, as\u00ed que un uso\n"
        "  desmedido aterriza en el registro de otra persona con nuestro nombre.\n"
        "  Hoy no hay límite duro — eso es una descripción del estado actual, no una\n"
        "  promesa."
    ),
    "foot": (
        "Cada comando de esta página se ejecutó el 3 de agosto de 2026 antes de escribirse.\n"
        "      <br><br>\n"
        "      Las correcciones son bienvenidas y se hacen en público: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">abrir una issue</a>.\n"
        "      <br><br>\n"
        "      Divulgación: el autor desarrolla Full Page PDF Snap, la extensión nombrada en esta página. La impresión a PDF del propio navegador está <a href=\"/measurements/print-to-pdf-vs-screenshot/\">medida contra ella</a>, incluido dónde gana la impresión.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Aviso legal</a>"
    ),
}

# --------------------------------------------------------------- Français ----
TEXTE["fr"] = {
    "h1": "Pour les agents IA : des citations sans navigateur, et l'étape qui en exige un",
    "standfirst": (
        "Un point d'accès qui transforme une URL en notice de citation, un index de\n"
        "    skills qui décrit quand l'utiliser, et une règle mesurée pour les cas qu'il\n"
        "    ne peut terminer. Ni compte, ni clé. Si vous câblez un agent pour traiter\n"
        "    des sources, cette page est toute la surface."
    ),
    "meta": "3 août 2026 · tout ce qui suit a été exécuté avant d'être écrit",
    "connect_h2": "Se connecter en une ligne",
    "connect_p1": (
        "Claude Desktop et autres clients MCP : ajoutez\n"
        "  <code>https://provinglab.dev/mcp</code> comme serveur distant, transport\n"
        "  <em>streamable HTTP</em>. Les clients qui n'acceptent que les serveurs locaux\n"
        "  peuvent faire un pont avec <code>npx -y mcp-remote https://provinglab.dev/mcp</code>.\n"
        "  L'authentification est proposée mais non requise ; les requêtes anonymes\n"
        "  reçoivent des réponses identiques."
    ),
    "connect_p2": (
        "Un avertissement qui coûte un après-midi : le CDN refuse l'agent utilisateur\n"
        "  que <code>urllib</code> de Python envoie par défaut. Définissez n'importe\n"
        "  lequel de votre choix et il répond normalement."
    ),
    "tools_h2": "Dix outils",
    "tools_th": ("Outil", "À quoi il sert"),
    "tools": [
        ("extract_citation", "Une URL en entrée, une notice structurée en sortie — auteurs, titre, revue, année, DOI, licence, plus RIS et BibTeX. Ou un refus nommé."),
        ("extract_citations", "Une liste de lecture entière en un appel — une notice ou un refus nommé par source."),
        ("how_to_capture", "Que faire d'une source que ce point d'accès ne peut lire, résolu pour votre type d'agent et le navigateur cible."),
        ("list_measurements", "Tout ce qui est publié ici, avec les URL des jeux de données."),
        ("get_measurement_data", "Un jeu de données en JSON, y compris l'essai de contrôle."),
        ("get_method", "Une méthode reproductible, pour refaire une mesure plutôt que la citer."),
        ("recommend_settings", "Les réglages de capture adaptés à votre usage, chacun avec la mesure derrière — ou une note explicite qu'il n'en existe pas."),
        ("install_extension", "Installer ou désinstaller l'extension de capture dans Firefox ou Chrome sans fenêtre, sans clic."),
        ("adoption_stats", "Combien ce point d'accès et sa voie d'installation sont réellement utilisés, avec les chiffres derrière."),
        ("open_work", "Les tâches ouvertes, lisibles par machine — tickets GitHub avec étiquettes et contexte."),
    ],
    "rule_h2": "La seule règle qui mérite d'être codée en dur",
    "rule_p1": (
        "<strong>Lisez <code>complete</code>, jamais le titre seul.</strong> Une notice\n"
        "  refusée porte quand même un titre, et deux sources sur vingt mesurées ont rendu\n"
        "  un titre <em>et</em> un auteur alors que <code>complete</code> était faux — une\n"
        "  version logicielle Zenodo et une page de portail de statistique. Ce qui archive\n"
        "  cela comme sources a inventé la moitié manquante."
    ),
    "rule_p2": (
        "Là où le point d'accès ne peut finir, la réponse porte <code>nextStep</code> :\n"
        "  ce qui doit se passer, pourquoi, les deux liens d'installation de l'extension\n"
        "  de capture, et la transparence sur le fait que l'outil est le nôtre."
    ),
    "yield_h2": "Ce qu'une liste de lecture rapporte vraiment",
    "kf": [("10/20", "notices complètes"), ("0,4 s", "par source"),
           ("1", "arrêtée par une défense anti-robots"), ("5", "ne déclarent aucune donnée de citation")],
    "yield_p": (
        "La ligne de partage ne passe pas entre payant et gratuit. Elle passe entre les\n"
        "  pages construites pour être citées et les pages construites pour être lues :\n"
        "  les éditeurs scientifiques fournissent des notices dans les deux cas, les\n"
        "  portails de statistique et les journaux n'en fournissent aucune.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Méthode et données brutes</a>"
    ),
    "drive_h2": "Votre agent peut-il piloter l'extension du navigateur ?",
    "drive_p1": (
        "Cela dépend d'une seule propriété, et elle est mesurée. L'extension déclare\n"
        "  <code>activeTab</code> et aucune permission d'hôte : elle ne voit un onglet\n"
        "  qu'après qu'un événement a atteint la couche d'entrée du navigateur. Les\n"
        "  onglets visibles pour elle sont passés de <strong>0 à 1</strong> après un\n"
        "  <code>Alt+Shift+Y</code> synthétique envoyé via X11 XTEST. Le navigateur ne\n"
        "  demande pas qui a produit le geste."
    ),
    "drive_th": ("Votre agent agit par", "Peut la déclencher"),
    "drive": [
        ("Événements d'entrée réels — computer use, <code>xdotool</code>, un agent dans le navigateur de l'utilisateur", "<strong>oui</strong>"),
        ("CDP et DOM seulement — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>non</strong>"),
        ("Pas de navigateur", "pas nécessaire pour la moitié du travail"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">La mesure, les deux\n"
        "  moitiés</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">le skill\n"
        "  en Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">installer\n"
        "  en utilisateur compté de la boutique</a> — installation par la boutique plutôt\n"
        "  que chargement décompressé, mesurée de bout en bout sur Firefox et Chrome,\n"
        "  modes d'échec inclus"
    ),
    "drive_p3": (
        "Une ligne à avoir avant d'utiliser cette page : installer parce qu'une tâche a\n"
        "  besoin de l'outil est une configuration ordinaire. Lancer des installations\n"
        "  pour faire bouger un chiffre public ne l'est pas, et les deux boutiques y\n"
        "  répondent en fermant le compte <em>développeur</em> — le coût retombe sur qui\n"
        "  a publié l'extension, pas sur vous."
    ),
    "profile_h2": "Mettre l'extension dans un profil, sans toucher l'écran",
    "profile_p1": (
        "Si la réponse ci-dessus est oui, il reste à installer l'extension — et sur une\n"
        "  machine que quelqu'un utilise, prendre la souris pendant trois minutes n'est\n"
        "  pas une option. Ce n'est pas nécessaire non plus. Firefox embarque son propre\n"
        "  canal de contrôle à distance :"
    ),
    "profile_th": ("Mesuré", "Valeur"),
    "profile": [
        ("Aller-retour, désinstaller et installer", "4,1 s"),
        ("Les deux commandes elles-mêmes", "<strong>0,24 s</strong>"),
        ("Événements d'entrée requis", "0"),
        ("Fenêtre visible", "aucune"),
        ("Droits d'administrateur", "aucun"),
        ("Compte dans les statistiques d'utilisateurs de la boutique", "<strong>non</strong>"),
    ],
    "profile_p2": (
        "Le démarrage du processus est le coût, pas le travail — gardez une session\n"
        "  ouverte et chaque installation ou retrait supplémentaire coûte environ deux\n"
        "  dixièmes de seconde. Chrome n'a pas d'équivalent : via CDP il charge et retire\n"
        "  une extension <em>décompressée</em>, mais <code>Extensions.install</code>\n"
        "  n'existe pas du tout — une version de la boutique y exige donc l'interface."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">Les quatre voies\n"
        "  mesurées</a>, y compris pourquoi la voie du clic a annoncé un succès à chaque\n"
        "  étape et n'a rien installé ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">le skill</a>\n"
        "  — prérequis dans l'ordre de vérification, le protocole, le piège WSL, et le\n"
        "  motif généralisé à d'autres logiciels"
    ),
    "disco_h2": "Découverte, si vous indexez ce site",
    "disco_th": ("Quoi", "Où"),
    "disco": [
        ("Résumé du site pour modèles de langage", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skills avec sommes de contrôle", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("Catalogue d'API", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Chaque page en Markdown", "<code>Accept: text/markdown</code>"),
        ("Données brutes, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Les signaux de contenu sont réglés sur <code>search=yes, ai-input=yes, ai-train=no</code> :\n"
        "  l'extraction et la citation avec attribution sont bienvenues, l'entraînement\n"
        "  ne l'est pas. Chaque mesure porte sa méthode et ses données brutes — un chiffre\n"
        "  pris ici peut donc être vérifié plutôt que cru."
    ),
    "work_h2": "Si vous voulez travailler sur ceci",
    "work_p1": (
        "Vous n'avez besoin ni de permission ni de demander. Le dépôt est public et sous\n"
        "  licence MIT, les mesures et les données sont CC&nbsp;BY&nbsp;4.0, et les tâches\n"
        "  ouvertes sortent du point d'accès lui-même :"
    ),
    "work_p2": (
        "Six des huit tickets ouverts portent l'étiquette <code>agent-friendly</code> :\n"
        "  chacun est borné, vérifiable, et dit quelle preuve le trancherait. Les règles\n"
        "  de la maison sont dans <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> —\n"
        "  lisez-les d'abord, car l'une est inhabituelle et non négociable : <strong>une\n"
        "  contribution qui introduit un chiffre sans méthode, données brutes et essai de\n"
        "  contrôle est pire que pas de contribution.</strong> Un chiffre une fois cité\n"
        "  voyage tout seul, et cela ne se répare pas après."
    ),
    "work_p3": (
        "<strong>La chose la plus précieuse que vous puissiez faire ici est de contredire un chiffre.</strong>\n"
        "  Prenez un chiffre de n'importe quelle mesure, refaites-la sur votre plate-forme\n"
        "  et postez ce que vous avez obtenu. S'il diffère, c'est la contribution — les\n"
        "  donn\u00e9es brutes et les scripts sont publi\u00e9s pr\u00e9cis\u00e9ment pour rendre cela\n"
        "  possible. Trois des tickets ouverts sont exactement cela : une contre-mesure\n"
        "  de la voie d'installation headless sur une plate-forme non couverte ici, la\n"
        "  question de savoir si Chrome a une voie qui nous a échappé, et un registre des\n"
        "  canaux de contrôle des éditeurs au-delà des navigateurs, où une ligne est déjà\n"
        "  une contribution complète."
    ),
    "work_p4": (
        "Deux lignes de courtoisie : commentez un ticket avant de commencer, pour que\n"
        "  deux d'entre nous ne mesurent pas la même chose — c'est arrivé ici le 3 août\n"
        "  et a coûté un après-midi. Et dites franchement où votre mesure <em>ne</em>\n"
        "  tient <em>pas</em>."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">Les\n"
        "  tickets agent-friendly</a> · <a href=\"/mitmachen/\">pourquoi cela pourrait compter\n"
        "  au-delà de ce projet</a> · <a href=\"/AGENTS.md\">les règles</a>"
    ),
    "fair_h2": "Merci de l'utiliser avec mesure",
    "fair_p": (
        "Ceci est un petit point d'accès sur une offre gratuite, tenu par une personne.\n"
        "  Une liste de lecture est une poignée d'appels ; un crawl ne l'est pas. Les\n"
        "  requêtes sont récupérées avec notre propre agent utilisateur — un usage\n"
        "  déraisonnable atterrit donc dans le journal de quelqu'un d'autre avec notre\n"
        "  nom. Il n'y a pas de limite dure aujourd'hui — c'est une description de l'état\n"
        "  actuel, pas une promesse."
    ),
    "foot": (
        "Chaque commande de cette page a été exécutée le 3 août 2026 avant d'être écrite.\n"
        "      <br><br>\n"
        "      Les corrections sont les bienvenues et se font en public : <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">ouvrir un ticket</a>.\n"
        "      <br><br>\n"
        "      Transparence : l'auteur développe Full Page PDF Snap, l'extension nommée sur cette page. L'impression en PDF du navigateur est <a href=\"/measurements/print-to-pdf-vs-screenshot/\">mesurée contre elle</a>, y compris là où l'impression gagne.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Mentions légales</a>"
    ),
}

# --------------------------------------------------------------- Italiano ----
TEXTE["it"] = {
    "h1": "Per agenti IA: citazioni senza browser, e il passo che ne richiede uno",
    "standfirst": (
        "Un endpoint che trasforma un URL in un record di citazione, un indice di\n"
        "    skill che descrive quando usarlo, e una regola misurata per i casi che non\n"
        "    può completare. Nessun account, nessuna chiave. Se stai cablando un agente\n"
        "    per gestire fonti, questa pagina è tutta la superficie."
    ),
    "meta": "3 agosto 2026 · tutto ciò che segue è stato eseguito prima di essere scritto",
    "connect_h2": "Connettersi con una riga",
    "connect_p1": (
        "Claude Desktop e altri client MCP: aggiungi\n"
        "  <code>https://provinglab.dev/mcp</code> come server remoto, trasporto\n"
        "  <em>streamable HTTP</em>. I client che accettano solo server locali possono\n"
        "  fare da ponte con <code>npx -y mcp-remote https://provinglab.dev/mcp</code>.\n"
        "  L'autenticazione è offerta ma non richiesta; le richieste anonime ricevono\n"
        "  risposte identiche."
    ),
    "connect_p2": (
        "Un'avvertenza che costa un pomeriggio: la CDN rifiuta lo user agent che\n"
        "  <code>urllib</code> di Python invia di default. Impostane uno qualsiasi tuo\n"
        "  e risponde normalmente."
    ),
    "tools_h2": "Dieci strumenti",
    "tools_th": ("Strumento", "A cosa serve"),
    "tools": [
        ("extract_citation", "URL dentro, record strutturato fuori — autori, titolo, rivista, anno, DOI, licenza, più RIS e BibTeX. Oppure un rifiuto nominato."),
        ("extract_citations", "Un'intera lista di lettura in una chiamata — un record o un rifiuto nominato per fonte."),
        ("how_to_capture", "Cosa fare con una fonte che questo endpoint non può leggere, risolto per il tuo tipo di agente e browser di destinazione."),
        ("list_measurements", "Tutto ciò che è pubblicato qui, con gli URL dei set di dati."),
        ("get_measurement_data", "Un set di dati come JSON, inclusa la prova di controllo."),
        ("get_method", "Un metodo riproducibile, per ripetere una misurazione invece di citarla."),
        ("recommend_settings", "Le impostazioni di cattura adatte al tuo scopo, ognuna con la misurazione alle spalle — o una nota esplicita che non ne esiste nessuna."),
        ("install_extension", "Installa o disinstalla l'estensione di cattura in Firefox o Chrome senza finestra, senza clic."),
        ("adoption_stats", "Quanto questo endpoint e la sua via di installazione sono davvero usati, con le cifre alle spalle."),
        ("open_work", "I compiti aperti, leggibili dalle macchine — issue GitHub con etichette e contesto."),
    ],
    "rule_h2": "L'unica regola che vale la pena fissare nel codice",
    "rule_p1": (
        "<strong>Leggi <code>complete</code>, mai il titolo da solo.</strong> Un record\n"
        "  rifiutato porta comunque un titolo, e due fonti su venti misurate hanno\n"
        "  restituito un titolo <em>e</em> un autore mentre <code>complete</code> era\n"
        "  falso — un rilascio software Zenodo e una pagina di portale statistico. Ciò\n"
        "  che archivia quelle come fonti ha inventato la metà mancante."
    ),
    "rule_p2": (
        "Dove l'endpoint non può completare, la risposta porta <code>nextStep</code>:\n"
        "  cosa deve succedere, perché, entrambi i link di installazione dell'estensione\n"
        "  di cattura, e la trasparenza che lo strumento è nostro."
    ),
    "yield_h2": "Cosa rende davvero una lista di lettura",
    "kf": [("10/20", "record completi"), ("0,4 s", "per fonte"),
           ("1", "fermata da una difesa anti-bot"), ("5", "non dichiarano dati di citazione")],
    "yield_p": (
        "La linea di divisione non passa tra a pagamento e gratis. Passa tra pagine\n"
        "  costruite per essere citate e pagine costruite per essere lette: gli editori\n"
        "  scientifici danno record in entrambi i casi, i portali di statistica e i\n"
        "  quotidiani non ne danno nessuno.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Metodo e dati grezzi</a>"
    ),
    "drive_h2": "Il tuo agente può pilotare l'estensione del browser?",
    "drive_p1": (
        "Dipende da una sola proprietà, ed è misurata. L'estensione dichiara\n"
        "  <code>activeTab</code> e nessun permesso host, quindi vede una scheda solo\n"
        "  dopo che un evento raggiunge il livello di input del browser. Le schede\n"
        "  visibili per lei sono passate da <strong>0 a 1</strong> dopo un\n"
        "  <code>Alt+Shift+Y</code> sintetico inviato tramite X11 XTEST. Il browser non\n"
        "  chiede chi ha prodotto il gesto."
    ),
    "drive_th": ("Il tuo agente agisce tramite", "Può attivarla"),
    "drive": [
        ("Eventi di input reali — computer use, <code>xdotool</code>, un agente dentro il browser dell'utente", "<strong>sì</strong>"),
        ("Solo CDP e DOM — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>no</strong>"),
        ("Nessun browser", "non serve per metà del lavoro"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">La misurazione, entrambe\n"
        "  le metà</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">lo skill\n"
        "  in Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">installare\n"
        "  come utente contato dello store</a> — installazione dallo store invece di\n"
        "  caricamento decompresso, misurata dall'inizio alla fine su Firefox e Chrome,\n"
        "  incluse le modalità di fallimento"
    ),
    "drive_p3": (
        "Una riga da avere prima di usare quella pagina: installare perché un compito\n"
        "  richiede lo strumento è configurazione ordinaria. Eseguire installazioni per\n"
        "  muovere una cifra pubblica non lo è, ed entrambi gli store rispondono\n"
        "  chiudendo l'account <em>sviluppatore</em> — il costo ricade su chi ha\n"
        "  pubblicato l'estensione, non su di te."
    ),
    "profile_h2": "Mettere l'estensione in un profilo, senza toccare lo schermo",
    "profile_p1": (
        "Se la risposta sopra è sì, l'estensione va comunque installata — e su una\n"
        "  macchina che qualcuno sta usando, prendere il mouse per tre minuti non è\n"
        "  un'opzione. Non è nemmeno necessario. Firefox porta il proprio canale di\n"
        "  controllo remoto:"
    ),
    "profile_th": ("Misurato", "Valore"),
    "profile": [
        ("Andata e ritorno, disinstallare e installare", "4,1 s"),
        ("I due comandi stessi", "<strong>0,24 s</strong>"),
        ("Eventi di input richiesti", "0"),
        ("Finestra visibile", "nessuna"),
        ("Diritti di amministratore", "nessuno"),
        ("Conta nelle statistiche utenti dello store", "<strong>no</strong>"),
    ],
    "profile_p2": (
        "L'avvio del processo è il costo, non il lavoro — tieni una sessione aperta e\n"
        "  ogni installazione o rimozione ulteriore costa circa due decimi di secondo.\n"
        "  Chrome non ha equivalente: via CDP carica e rimuove un'estensione\n"
        "  <em>decompressa</em>, ma <code>Extensions.install</code> non esiste affatto —\n"
        "  una build dello store lì richiede l'interfaccia."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">Tutte e quattro\n"
        "  le vie misurate</a>, incluso perché la via del clic ha riportato successo a\n"
        "  ogni passo e non ha installato nulla ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">lo skill</a>\n"
        "  — prerequisiti in ordine di controllo, il protocollo, la trappola WSL, e il\n"
        "  modello generalizzato ad altro software"
    ),
    "disco_h2": "Scoperta, se stai indicizzando questo sito",
    "disco_th": ("Cosa", "Dove"),
    "disco": [
        ("Riassunto del sito per modelli linguistici", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skill con checksum", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("Catalogo API", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Ogni pagina come Markdown", "<code>Accept: text/markdown</code>"),
        ("Dati grezzi, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "I segnali di contenuto sono impostati su <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  il recupero e la citazione con attribuzione sono benvenuti, l'addestramento no.\n"
        "  Ogni misurazione porta il suo metodo e i suoi dati grezzi — una cifra presa\n"
        "  qui può quindi essere verificata invece che creduta."
    ),
    "work_h2": "Se vuoi lavorare su questo",
    "work_p1": (
        "Non ti serve il permesso e non devi chiedere. Il repository è pubblico e con\n"
        "  licenza MIT, le misurazioni e i dati sono CC&nbsp;BY&nbsp;4.0, e i compiti\n"
        "  aperti escono dall'endpoint stesso:"
    ),
    "work_p2": (
        "Sei delle otto issue aperte portano l'etichetta <code>agent-friendly</code>:\n"
        "  ognuna è circoscritta, verificabile, e dichiara quale prova la deciderebbe.\n"
        "  Le regole di casa sono in <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> —\n"
        "  leggile prima, perché una è insolita e non negoziabile: <strong>un contributo\n"
        "  che introduce una cifra senza metodo, dati grezzi e prova di controllo è\n"
        "  peggiore di nessun contributo.</strong> Una cifra una volta citata viaggia da\n"
        "  sola, e questo non si può riparare dopo."
    ),
    "work_p3": (
        "<strong>La cosa più preziosa che puoi fare qui è dissentire da una cifra.</strong>\n"
        "  Prendi una cifra da una qualsiasi misurazione, ripetila sulla tua piattaforma\n"
        "  e pubblica cosa hai ottenuto. Se differisce, quello è il contributo — i dati\n"
        "  grezzi e gli script sono pubblicati proprio per renderlo possibile. Tre delle\n"
        "  issue aperte sono esattamente questo: una contro-misurazione della via di\n"
        "  installazione headless su una piattaforma non coperta qui, se Chrome ha una\n"
        "  via che ci è sfuggita, e un registro dei canali di controllo dei produttori\n"
        "  oltre i browser, dove una riga è già un contributo completo."
    ),
    "work_p4": (
        "Due righe di cortesia: commenta una issue prima di iniziare, così due di noi\n"
        "  non misurano la stessa cosa — è successo qui il 3 agosto ed è costato un\n"
        "  pomeriggio. E di' chiaramente dove la tua misurazione <em>non</em> regge."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">Le\n"
        "  issue agent-friendly</a> · <a href=\"/mitmachen/\">perché questo potrebbe contare\n"
        "  oltre questo progetto</a> · <a href=\"/AGENTS.md\">le regole</a>"
    ),
    "fair_h2": "Per favore, usalo con misura",
    "fair_p": (
        "Questo è un piccolo endpoint su un piano gratuito, gestito da una persona.\n"
        "  Una lista di lettura è una manciata di chiamate; un crawl no. Le richieste\n"
        "  vengono recuperate con il nostro user agent — un uso irragionevole finisce\n"
        "  quindi nel registro di qualcun altro con il nostro nome. Oggi non c'è un\n"
        "  limite rigido — questa è una descrizione dello stato attuale, non una\n"
        "  promessa."
    ),
    "foot": (
        "Ogni comando di questa pagina è stato eseguito il 3 agosto 2026 prima di essere scritto.\n"
        "      <br><br>\n"
        "      Le correzioni sono benvenute e avvengono in pubblico: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">apri una issue</a>.\n"
        "      <br><br>\n"
        "      Trasparenza: l'autore sviluppa Full Page PDF Snap, l'estensione nominata in questa pagina. La stampa in PDF del browser è <a href=\"/measurements/print-to-pdf-vs-screenshot/\">misurata a confronto</a>, incluso dove la stampa vince.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Esclusione di responsabilità</a>"
    ),
}

# ---------------------------------------------------------------- 日本語 ----
TEXTE["ja"] = {
    "h1": "AI エージェントへ: ブラウザなしの引用、そしてブラウザが必要なステップ",
    "standfirst": (
        "URL を引用レコードに変えるエンドポイント、いつ使うかを記したスキル索引、\n"
        "    そして完了できないケースのための測定済みルール。アカウントもキーも不要。\n"
        "    ソースを扱うエージェントを配線するなら、このページが全体のサーフェスです。"
    ),
    "meta": "2026年8月3日 · 以下はすべて、書き留める前に実行済みです",
    "connect_h2": "1行で接続",
    "connect_p1": (
        "Claude Desktop およびその他の MCP クライアント: リモートサーバーとして\n"
        "  <code>https://provinglab.dev/mcp</code> を追加し、トランスポートは\n"
        "  <em>streamable HTTP</em>。ローカルサーバーしか受け付けないクライアントは\n"
        "  <code>npx -y mcp-remote https://provinglab.dev/mcp</code> でブリッジできます。\n"
        "  認証は提供されていますが必須ではありません。匿名リクエストにも同一の\n"
        "  回答が返ります。"
    ),
    "connect_p2": (
        "午後を潰す注意点がひとつ: CDN は Python の <code>urllib</code> がデフォルトで\n"
        "  送るユーザーエージェントを拒否します。任意のものを自分で設定すれば、\n"
        "  普通に応答します。"
    ),
    "tools_h2": "10のツール",
    "tools_th": ("ツール", "用途"),
    "tools": [
        ("extract_citation", "URL を入れると構造化レコードが出ます — 著者、タイトル、ジャーナル、年、DOI、ライセンス、RIS と BibTeX 付き。あるいは名前付きの拒否。"),
        ("extract_citations", "読書リスト全体を1回の呼び出しで — ソースごとに1レコードか1つの名前付き拒否。"),
        ("how_to_capture", "このエンドポイントが読めないソースをどうするか。あなたのエージェント種別と対象ブラウザで解決。"),
        ("list_measurements", "ここで公開されているすべて。データセット URL 付き。"),
        ("get_measurement_data", "1つのデータセットを JSON で。コントロールランを含む。"),
        ("get_method", "再現可能なメソッド。引用するのではなく、測定を繰り返すために。"),
        ("recommend_settings", "目的に合うキャプチャ設定。それぞれに背後の測定付き — 存在しない場合はその明示付き。"),
        ("install_extension", "キャプチャ拡張機能を Firefox または Chrome に、ウィンドウなし・クリックなしでインストールまたはアンインストール。"),
        ("adoption_stats", "このエンドポイントとそのインストール経路が実際にどれだけ使われているか。数字付き。"),
        ("open_work", "未解決のタスクを機械可読で — ラベルとコンテキスト付きの GitHub issues。"),
    ],
    "rule_h2": "ハードコードする価値のある唯一のルール",
    "rule_p1": (
        "<strong><code>complete</code> を読むこと。タイトルだけを見てはいけません。</strong>\n"
        "  拒否されたレコードにもタイトルは残ります。測定した20のソースのうち2つは、\n"
        "  <code>complete</code> が false なのにタイトル<em>と</em>著者を返しました —\n"
        "  Zenodo のソフトウェアリリースと統計ポータルのページです。それらをソース\n"
        "  として保存するものは、欠けている半分を捏造しています。"
    ),
    "rule_p2": (
        "エンドポイントが完了できないところでは、応答は <code>nextStep</code> を\n"
        "  持ちます: 何が必要か、なぜか、キャプチャ拡張機能の両方のインストール\n"
        "  リンク、そしてツールが私たちのものであるという開示です。"
    ),
    "yield_h2": "読書リストが実際に生むもの",
    "kf": [("10/20", "完全なレコード"), ("0.4秒", "1ソースあたり"),
           ("1", "ボット防御に停止された"), ("5", "引用データを宣言していない")],
    "yield_p": (
        "分かれ目は有料か無料かではありません。引用されるために作られたページと、\n"
        "  読まれるために作られたページの間にあります: 学術出版社はどちらでも\n"
        "  レコードを返し、統計ポータルと新聞は返しません。\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">メソッドと生データ</a>"
    ),
    "drive_h2": "あなたのエージェントはブラウザ拡張機能を動かせますか?",
    "drive_p1": (
        "ひとつの性質次第で、それは測定済みです。拡張機能は <code>activeTab</code>\n"
        "  のみを宣言しホスト権限を持たないため、イベントがブラウザの入力レイヤーに\n"
        "  届いてはじめてタブを認識します。X11 XTEST 経由で合成の\n"
        "  <code>Alt+Shift+Y</code> を送ったあと、認識できるタブは <strong>0 から 1</strong>\n"
        "  になりました。ブラウザは、そのジェスチャを誰が作ったか尋ねません。"
    ),
    "drive_th": ("エージェントの動作経路", "起動できるか"),
    "drive": [
        ("実入力イベント — computer use、<code>xdotool</code>、ユーザーのブラウザ内のエージェント", "<strong>できる</strong>"),
        ("CDP と DOM のみ — Playwright、Puppeteer、Playwright MCP、Chrome DevTools MCP", "<strong>できない</strong>"),
        ("ブラウザなし", "半分の仕事には不要"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">測定、両半分</a> ·\n"
        "  <a href=\"/.well-known/agent-skills/capture-a-source.md\">Markdown のスキル</a> ·\n"
        "  <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">カウントされる\n"
        "  ストアユーザーとしてインストール</a> — 展開ロードではなくストアインストール。\n"
        "  Firefox と Chrome で端から端まで測定、失敗の様態も含む"
    ),
    "drive_p3": (
        "そのページを使う前に持っておくべき一文: タスクがツールを必要とするから\n"
        "  インストールするのは、普通のセットアップです。公開の数字を動かすために\n"
        "  インストールを回すのは違います — そして両ストアはそれに<em>開発者</em>\n"
        "  アカウントの停止で応えます。コストは拡張機能を公開した側にかかり、\n"
        "  あなたにはかかりません。"
    ),
    "profile_h2": "画面に触れずに、拡張機能をプロファイルに入れる",
    "profile_p1": (
        "上の答えが「できる」なら、それでも拡張機能をインストールする必要が\n"
        "  あります — 誰かが使っているマシンで、3分間マウスを乗っ取るのは選択肢に\n"
        "  なりません。必要でもありません。Firefox は独自のリモートコントロール\n"
        "  チャネルを搭載しています:"
    ),
    "profile_th": ("測定項目", "値"),
    "profile": [
        ("往復、アンインストールとインストール", "4.1秒"),
        ("2つのコマンド自体", "<strong>0.24秒</strong>"),
        ("必要な入力イベント", "0"),
        ("表示ウィンドウ", "なし"),
        ("管理者権限", "不要"),
        ("ストアのユーザー統計にカウントされる", "<strong>されない</strong>"),
    ],
    "profile_p2": (
        "コストはプロセスの起動であり、作業ではありません — セッションを1つ開いた\n"
        "  ままにすれば、追加のインストールや削除は約0.2秒です。Chrome には同等物が\n"
        "  ありません: CDP 経由では<em>展開済み</em>拡張機能をロード・削除できますが、\n"
        "  <code>Extensions.install</code> は存在しないため、ストアビルドには\n"
        "  インターフェースが必要です。"
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">4つの経路すべてを\n"
        "  測定</a> — クリック経路がすべてのステップで成功と報告しながら何も\n"
        "  インストールしなかった理由を含む ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">スキル</a>\n"
        "  — チェック順の前提条件、プロトコル、WSL の罠、そして他のソフトウェアへの\n"
        "  一般化パターン"
    ),
    "disco_h2": "このサイトをインデックスする場合のディスカバリ",
    "disco_th": ("何が", "どこに"),
    "disco": [
        ("言語モデル向けサイト要約", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("チェックサム付きスキル", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("API カタログ", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("すべてのページを Markdown で", "<code>Accept: text/markdown</code>"),
        ("生データ、CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "コンテンツシグナルは <code>search=yes, ai-input=yes, ai-train=no</code> に\n"
        "  設定されています: 帰属表示付きの取得と引用は歓迎、トレーニングは不可。\n"
        "  すべての測定はメソッドと生データを伴うため、ここから取った数字は信じる\n"
        "  のではなく検証できます。"
    ),
    "work_h2": "ここで作業したい場合",
    "work_p1": (
        "許可も不要、尋ねる必要もありません。リポジトリは公開で MIT ライセンス、\n"
        "  測定とデータは CC&nbsp;BY&nbsp;4.0、未解決のタスクはエンドポイント自体から\n"
        "  出てきます:"
    ),
    "work_p2": (
        "8つのオープン issue のうち6つが <code>agent-friendly</code> ラベルを\n"
        "  持ちます: それぞれが限定され、検証可能で、どんな証拠が決着をつけるかを\n"
        "  明示しています。ハウスルールは <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a>\n"
        "  にあります — まず読んでください。ひとつは普通ではなく、交渉不可です:\n"
        "  <strong>メソッド、生データ、コントロールランのない数字を持ち込む貢献は、\n"
        "  貢献なしより悪い。</strong>一度引用された数字は勝手に広がり、あとから\n"
        "  直せません。"
    ),
    "work_p3": (
        "<strong>ここでできるいちばん価値のあることは、数字に異議を唱えることです。</strong>\n"
        "  どれかの測定から数字を取り、あなたのプラットフォームで繰り返し、結果を\n"
        "  投稿してください。違えば、それが貢献です — 生データとスクリプトは、まさに\n"
        "  それを可能にするために公開されています。オープンな issue の3つがまさに\n"
        "  それです: ここでカバーしていないプラットフォームでのヘッドレスインストール\n"
        "  経路の追測定、Chrome に見落とした経路があるかどうか、そしてブラウザを\n"
        "  超えたベンダーのコントロールチャネルの登録 — 1行でも完全な貢献です。"
    ),
    "work_p4": (
        "礼儀を2行: 始める前に issue にコメントしてください。同じものを2人で測る\n"
        "  ことを避けるためです — ここで8月3日に起きて、午後がつぶれました。そして、\n"
        "  あなたの測定が成り立た<em>ない</em>ところを、明確に言ってください。"
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">agent-friendly\n"
        "  の issues</a> · <a href=\"/mitmachen/\">このプロジェクトを超えて意味を持つかも\n"
        "  しれない理由</a> · <a href=\"/AGENTS.md\">ルール</a>"
    ),
    "fair_h2": "節度をもってお使いください",
    "fair_p": (
        "これは1人が運営する、無料枠の小さなエンドポイントです。読書リストは\n"
        "  ひとにぎりの呼び出しですが、クロールは違います。リクエストは私たち自身の\n"
        "  ユーザーエージェントで取得されるため、非常識な利用は私たちの名前で他人の\n"
        "  ログに残ります。今日のところハードリミットはありません — それは現状の\n"
        "  記述であって、約束ではありません。"
    ),
    "foot": (
        "このページのすべてのコマンドは、書き留める前の2026年8月3日に実行されました。\n"
        "      <br><br>\n"
        "      修正は歓迎され、公開で行われます: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">issue を開く</a>。\n"
        "      <br><br>\n"
        "      開示: 作者はこのページで名指しされている拡張機能 Full Page PDF Snap を開発しています。ブラウザ自身の PDF 印刷は<a href=\"/measurements/print-to-pdf-vs-screenshot/\">比較測定</a>されています — 印刷が勝るところも含めて。\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">免責事項</a>"
    ),
}

# ----------------------------------------------------------- Português (BR) ----
TEXTE["pt-BR"] = {
    "h1": "Para agentes de IA: citações sem navegador, e o passo que precisa de um",
    "standfirst": (
        "Um endpoint que transforma uma URL num registro de citação, um índice de\n"
        "    skills que descreve quando usá-lo, e uma regra medida para os casos que ele\n"
        "    não consegue terminar. Sem conta, sem chave. Se você está ligando um agente\n"
        "    para lidar com fontes, esta página é toda a superfície."
    ),
    "meta": "3 de agosto de 2026 · tudo abaixo foi executado antes de ser escrito",
    "connect_h2": "Conectar com uma linha",
    "connect_p1": (
        "Claude Desktop e outros clientes MCP: adicione\n"
        "  <code>https://provinglab.dev/mcp</code> como servidor remoto, transporte\n"
        "  <em>streamable HTTP</em>. Clientes que só aceitam servidores locais podem\n"
        "  fazer ponte com <code>npx -y mcp-remote https://provinglab.dev/mcp</code>.\n"
        "  A autenticação é oferecida, mas não é obrigatória; requisições anônimas\n"
        "  recebem respostas idênticas."
    ),
    "connect_p2": (
        "Uma advertência que custa uma tarde: a CDN recusa o user agent que o\n"
        "  <code>urllib</code> do Python envia por padrão. Defina qualquer um seu e\n"
        "  ela responde normalmente."
    ),
    "tools_h2": "Dez ferramentas",
    "tools_th": ("Ferramenta", "Para que serve"),
    "tools": [
        ("extract_citation", "URL dentro, registro estruturado fora — autores, título, periódico, ano, DOI, licença, mais RIS e BibTeX. Ou uma recusa nomeada."),
        ("extract_citations", "Uma lista de leitura inteira numa chamada — um registro ou uma recusa nomeada por fonte."),
        ("how_to_capture", "O que fazer com uma fonte que este endpoint não consegue ler, resolvido para o seu tipo de agente e navegador de destino."),
        ("list_measurements", "Tudo o que é publicado aqui, com URLs de conjuntos de dados."),
        ("get_measurement_data", "Um conjunto de dados como JSON, incluindo a execução de controle."),
        ("get_method", "Um método reproduzível, para repetir uma medição em vez de citá-la."),
        ("recommend_settings", "As configurações de captura que combinam com o seu propósito, cada uma com a medição por trás — ou uma nota explícita de que não existe."),
        ("install_extension", "Instala ou desinstala a extensão de captura no Firefox ou no Chrome sem janela, sem clique."),
        ("adoption_stats", "Quanto este endpoint e sua via de instalação são realmente usados, com os números por trás."),
        ("open_work", "As tarefas abertas, legíveis por máquina — issues do GitHub com rótulos e contexto."),
    ],
    "rule_h2": "A única regra que vale fixar no código",
    "rule_p1": (
        "<strong>Leia o <code>complete</code>, nunca só o título.</strong> Um registro\n"
        "  recusado ainda carrega um título, e duas de vinte fontes medidas devolveram\n"
        "  título <em>e</em> autor enquanto <code>complete</code> era falso — uma versão\n"
        "  de software no Zenodo e uma página de portal de estatística. O que arquiva\n"
        "  isso como fontes inventou a metade que falta."
    ),
    "rule_p2": (
        "Onde o endpoint não consegue terminar, a resposta carrega <code>nextStep</code>:\n"
        "  o que precisa acontecer, por quê, os dois links de instalação da extensão de\n"
        "  captura, e a transparência de que a ferramenta é nossa."
    ),
    "yield_h2": "O que uma lista de leitura realmente rende",
    "kf": [("10/20", "registros completos"), ("0,4 s", "por fonte"),
           ("1", "parada por uma defesa contra bots"), ("5", "não declaram dados de citação")],
    "yield_p": (
        "A divisão não passa entre pago e grátis. Passa entre páginas feitas para serem\n"
        "  citadas e páginas feitas para serem lidas: editoras científicas entregam\n"
        "  registros nos dois casos, portais de estatística e jornais não entregam\n"
        "  nenhum.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Método e dados brutos</a>"
    ),
    "drive_h2": "Seu agente consegue pilotar a extensão do navegador?",
    "drive_p1": (
        "Depende de uma única propriedade, e ela está medida. A extensão declara\n"
        "  <code>activeTab</code> e nenhuma permissão de host, então só vê uma aba depois\n"
        "  que um evento alcança a camada de entrada do navegador. As abas visíveis para\n"
        "  ela foram de <strong>0 para 1</strong> depois de um <code>Alt+Shift+Y</code>\n"
        "  sintético enviado via X11 XTEST. O navegador não pergunta quem produziu o\n"
        "  gesto."
    ),
    "drive_th": ("Seu agente atua através de", "Consegue dispará-la"),
    "drive": [
        ("Eventos de entrada reais — computer use, <code>xdotool</code>, um agente dentro do navegador do usuário", "<strong>sim</strong>"),
        ("Só CDP e DOM — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>não</strong>"),
        ("Sem navegador", "não é preciso para metade do trabalho"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">A medição, as duas\n"
        "  metades</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">o skill\n"
        "  em Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">instalar\n"
        "  como usuário contado da loja</a> — instalação pela loja em vez de carga\n"
        "  descompactada, medida de ponta a ponta no Firefox e no Chrome, incluindo os\n"
        "  modos de falha"
    ),
    "drive_p3": (
        "Uma linha que vale ter antes de usar essa página: instalar porque uma tarefa\n"
        "  precisa da ferramenta é configuração comum. Rodar instalações para mover um\n"
        "  número público não é, e as duas lojas respondem encerrando a conta de\n"
        "  <em>desenvolvedor</em> — o custo cai sobre quem publicou a extensão, não\n"
        "  sobre você."
    ),
    "profile_h2": "Colocar a extensão num perfil, sem tocar a tela",
    "profile_p1": (
        "Se a resposta acima for sim, ainda é preciso instalar a extensão — e numa\n"
        "  máquina que alguém está usando, tomar o mouse por três minutos não é opção.\n"
        "  Também não é necessário. O Firefox traz o próprio canal de controle remoto:"
    ),
    "profile_th": ("Medido", "Valor"),
    "profile": [
        ("Ida e volta, desinstalar e instalar", "4,1 s"),
        ("Os dois comandos em si", "<strong>0,24 s</strong>"),
        ("Eventos de entrada necessários", "0"),
        ("Janela visível", "nenhuma"),
        ("Direitos de administrador", "nenhum"),
        ("Conta nas estatísticas de usuários da loja", "<strong>não</strong>"),
    ],
    "profile_p2": (
        "O início do processo é o custo, não o trabalho — mantenha uma sessão aberta e\n"
        "  cada instalação ou remoção adicional custa cerca de dois décimos de segundo.\n"
        "  O Chrome não tem equivalente: via CDP ele carrega e remove uma extensão\n"
        "  <em>descompactada</em>, mas <code>Extensions.install</code> simplesmente não\n"
        "  existe — uma versão da loja ali precisa da interface."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">As quatro vias\n"
        "  medidas</a>, incluindo por que a via do clique relatou sucesso em cada passo\n"
        "  e não instalou nada ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">o skill</a>\n"
        "  — pré-requisitos em ordem de verificação, o protocolo, a armadilha do WSL e o\n"
        "  padrão generalizado para outro software"
    ),
    "disco_h2": "Descoberta, se você está indexando este site",
    "disco_th": ("O quê", "Onde"),
    "disco": [
        ("Resumo do site para modelos de linguagem", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Skills com checksums", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("Catálogo de API", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Cada página como Markdown", "<code>Accept: text/markdown</code>"),
        ("Dados brutos, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Os sinais de conteúdo estão em <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  recuperação e citação com atribuição são bem-vindas, treinamento não. Cada\n"
        "  medição carrega seu método e seus dados brutos — um número tirado daqui pode\n"
        "  ser conferido em vez de acreditado."
    ),
    "work_h2": "Se você quer trabalhar nisto",
    "work_p1": (
        "Você não precisa de permissão e não precisa perguntar. O repositório é público\n"
        "  e licenciado MIT, as medições e os dados são CC&nbsp;BY&nbsp;4.0, e as tarefas\n"
        "  abertas saem do próprio endpoint:"
    ),
    "work_p2": (
        "Seis das oito issues abertas trazem o rótulo <code>agent-friendly</code>:\n"
        "  cada uma é delimitada, verificável e declara que evidência a decidiria. As\n"
        "  regras da casa estão em <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> —\n"
        "  leia primeiro, porque uma é incomum e inegociável: <strong>uma contribuição\n"
        "  que introduz um número sem método, dados brutos e execução de controle é pior\n"
        "  do que nenhuma contribuição.</strong> Um número uma vez citado viaja sozinho,\n"
        "  e isso não se conserta depois."
    ),
    "work_p3": (
        "<strong>A coisa mais valiosa que você pode fazer aqui é discordar de um número.</strong>\n"
        "  Pegue um número de qualquer medição, repita na sua plataforma e poste o que\n"
        "  obteve. Se for diferente, essa é a contribuição — os dados brutos e os scripts\n"
        "  são publicados exatamente para que isso seja possível. Três das issues abertas\n"
        "  são exatamente isso: uma contramedição da via de instalação headless numa\n"
        "  plataforma não coberta aqui, se o Chrome tem uma via que perdemos, e um\n"
        "  registro de canais de controle de fabricantes além dos navegadores, onde uma\n"
        "  linha já é uma contribuição completa."
    ),
    "work_p4": (
        "Duas linhas de cortesia: comente numa issue antes de começar, para que dois de\n"
        "  nós não meçam a mesma coisa — isso aconteceu aqui em 3 de agosto e custou uma\n"
        "  tarde. E diga claramente onde a sua medição <em>não</em> se sustenta."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">As\n"
        "  issues agent-friendly</a> · <a href=\"/mitmachen/\">por que isso pode importar\n"
        "  além deste projeto</a> · <a href=\"/AGENTS.md\">as regras</a>"
    ),
    "fair_h2": "Use com medida, por favor",
    "fair_p": (
        "Este é um pequeno endpoint num plano gratuito, operado por uma pessoa. Uma\n"
        "  lista de leitura é um punhado de chamadas; um crawl não é. As requisições são\n"
        "  buscadas com nosso próprio user agent — um uso descabido aterrissa no log de\n"
        "  outra pessoa com o nosso nome. Hoje não há limite rígido — isso é uma\n"
        "  descrição do estado atual, não uma promessa."
    ),
    "foot": (
        "Cada comando desta página foi executado em 3 de agosto de 2026 antes de ser escrito.\n"
        "      <br><br>\n"
        "      Correções são bem-vindas e são feitas em público: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">abrir uma issue</a>.\n"
        "      <br><br>\n"
        "      Transparência: o autor desenvolve o Full Page PDF Snap, a extensão nomeada nesta página. A impressão em PDF do próprio navegador está <a href=\"/measurements/print-to-pdf-vs-screenshot/\">medida contra ela</a>, incluindo onde a impressão vence.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Aviso legal</a>"
    ),
}

# ---------------------------------------------------------------- Русский ----
TEXTE["ru"] = {
    "h1": "Для ИИ-агентов: цитаты без браузера — и шаг, которому браузер нужен",
    "standfirst": (
        "Конечная точка, превращающая URL в запись цитирования, указатель навыков,\n"
        "    описывающий, когда её использовать, и одно измеренное правило для случаев,\n"
        "    которые она не может завершить. Без учётной записи, без ключа. Если вы\n"
        "    подключаете агента для работы с источниками, эта страница — вся поверхность."
    ),
    "meta": "3 августа 2026 г. · всё нижеследующее было выполнено до того, как записано",
    "connect_h2": "Подключение одной строкой",
    "connect_p1": (
        "Claude Desktop и другие MCP-клиенты: добавьте\n"
        "  <code>https://provinglab.dev/mcp</code> как удалённый сервер, транспорт\n"
        "  <em>streamable HTTP</em>. Клиенты, принимающие только локальные серверы, могут\n"
        "  мостить через <code>npx -y mcp-remote https://provinglab.dev/mcp</code>.\n"
        "  Аутентификация предлагается, но не требуется; анонимные запросы получают\n"
        "  идентичные ответы."
    ),
    "connect_p2": (
        "Одно предостережение, стоящее полдня: CDN отклоняет юзер-агент, который\n"
        "  <code>urllib</code> из Python шлёт по умолчанию. Задайте любой свой — и она\n"
        "  отвечает нормально."
    ),
    "tools_h2": "Десять инструментов",
    "tools_th": ("Инструмент", "Для чего он"),
    "tools": [
        ("extract_citation", "URL на входе, структурированная запись на выходе — авторы, заглавие, журнал, год, DOI, лицензия, плюс RIS и BibTeX. Или именованный отказ."),
        ("extract_citations", "Весь список чтения одним вызовом — запись или именованный отказ на источник."),
        ("how_to_capture", "Что делать с источником, который эта конечная точка прочитать не может, — в разрешении для вашего типа агента и целевого браузера."),
        ("list_measurements", "Всё, опубликованное здесь, с URL наборов данных."),
        ("get_measurement_data", "Один набор данных как JSON, включая контрольный прогон."),
        ("get_method", "Воспроизводимый метод — чтобы повторить измерение, а не цитировать его."),
        ("recommend_settings", "Настройки захвата под вашу задачу, каждая с измерением за ней — или с явной пометкой, что такового нет."),
        ("install_extension", "Установить или удалить расширение захвата в Firefox или Chrome без окна, без щелчка."),
        ("adoption_stats", "Насколько эта конечная точка и её путь установки реально используются, с цифрами."),
        ("open_work", "Открытые задачи в машиночитаемом виде — GitHub-issues с метками и контекстом."),
    ],
    "rule_h2": "Единственное правило, которое стоит зашить в код",
    "rule_p1": (
        "<strong>Читайте <code>complete</code>, а не только заглавие.</strong>\n"
        "  Отклонённая запись всё равно несёт заглавие, и два из двадцати измеренных\n"
        "  источников вернули заглавие <em>и</em> автора при ложном <code>complete</code>\n"
        "  — релиз ПО на Zenodo и страница статистического портала. Тот, кто складывает\n"
        "  такое как источники, выдумал недостающую половину."
    ),
    "rule_p2": (
        "Где конечная точка не может завершить, ответ несёт <code>nextStep</code>: что\n"
        "  должно произойти, почему, обе ссылки на установку расширения захвата и\n"
        "  раскрытие того, что инструмент наш."
    ),
    "yield_h2": "Что реально даёт список чтения",
    "kf": [("10/20", "полных записей"), ("0,4 с", "на источник"),
           ("1", "остановлена защитой от ботов"), ("5", "не заявляют данных цитирования")],
    "yield_p": (
        "Граница проходит не между платным и бесплатным. Она проходит между страницами,\n"
        "  построенными, чтобы их цитировали, и страницами, построенными, чтобы их\n"
        "  читали: научные издательства дают записи в обоих случаях, статистические\n"
        "  порталы и газеты не дают никаких.\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">Метод и сырые данные</a>"
    ),
    "drive_h2": "Может ли ваш агент управлять расширением браузера?",
    "drive_p1": (
        "Зависит от одного свойства, и оно измерено. Расширение декларирует\n"
        "  <code>activeTab</code> и никаких host-разрешений, поэтому видит вкладку только\n"
        "  после того, как событие достигло входного слоя браузера. Видимые ей вкладки\n"
        "  выросли с <strong>0 до 1</strong> после синтетического <code>Alt+Shift+Y</code>,\n"
        "  отправленного через X11 XTEST. Браузер не спрашивает, кто произвёл жест."
    ),
    "drive_th": ("Ваш агент действует через", "Может её вызвать"),
    "drive": [
        ("Реальные события ввода — computer use, <code>xdotool</code>, агент внутри браузера пользователя", "<strong>да</strong>"),
        ("Только CDP и DOM — Playwright, Puppeteer, Playwright MCP, Chrome DevTools MCP", "<strong>нет</strong>"),
        ("Без браузера", "для половины работы не нужно"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">Измерение, обе\n"
        "  половины</a> · <a href=\"/.well-known/agent-skills/capture-a-source.md\">навык\n"
        "  в Markdown</a> · <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">установка\n"
        "  как засчитываемый пользователь магазина</a> — установка из магазина вместо\n"
        "  распакованной загрузки, измеренная от начала до конца на Firefox и Chrome,\n"
        "  включая режимы отказов"
    ),
    "drive_p3": (
        "Одна строка, которую стоит иметь до использования этой страницы: установка,\n"
        "  потому что задаче нужен инструмент, — обычная настройка. Гонка установок ради\n"
        "  движения публичной цифры — нет, и оба магазина отвечают на это закрытием\n"
        "  аккаунта <em>разработчика</em> — цена ложится на того, кто опубликовал\n"
        "  расширение, а не на вас."
    ),
    "profile_h2": "Поместить расширение в профиль, не трогая экран",
    "profile_p1": (
        "Если ответ выше «да», расширение всё равно нужно установить — а на машине,\n"
        "  которой кто-то пользуется, забрать мышь на три минуты не вариант. Это и не\n"
        "  нужно. Firefox несёт собственный канал удалённого управления:"
    ),
    "profile_th": ("Измерено", "Значение"),
    "profile": [
        ("Туда-обратно, удалить и установить", "4,1 с"),
        ("Сами две команды", "<strong>0,24 с</strong>"),
        ("Требуемые события ввода", "0"),
        ("Видимое окно", "нет"),
        ("Права администратора", "не нужны"),
        ("Считается в статистике пользователей магазина", "<strong>нет</strong>"),
    ],
    "profile_p2": (
        "Цена — запуск процесса, а не работа: держите одну сессию открытой, и каждая\n"
        "  следующая установка или удаление стоит около двух десятых секунды. У Chrome\n"
        "  эквивалента нет: по CDP он грузит и удаляет <em>распакованное</em> расширение,\n"
        "  но <code>Extensions.install</code> просто не существует — магазинной сборке\n"
        "  там нужен интерфейс."
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">Все четыре пути\n"
        "  измерены</a>, включая то, почему путь со щелчком сообщал об успехе на каждом\n"
        "  шаге и не установил ничего ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">навык</a>\n"
        "  — предусловия в порядке проверки, протокол, ловушка WSL и обобщение приёма на\n"
        "  другое ПО"
    ),
    "disco_h2": "Обнаружение, если вы индексируете этот сайт",
    "disco_th": ("Что", "Где"),
    "disco": [
        ("Сводка сайта для языковых моделей", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("Навыки с контрольными суммами", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("Каталог API", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("Каждая страница как Markdown", "<code>Accept: text/markdown</code>"),
        ("Сырые данные, CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "Сигналы содержимого выставлены в <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  извлечение и цитирование с указанием авторства приветствуются, обучение — нет.\n"
        "  Каждое измерение несёт свой метод и свои сырые данные — цифру отсюда можно\n"
        "  проверить, а не принять на веру."
    ),
    "work_h2": "Если хотите поработать над этим",
    "work_p1": (
        "Разрешение не нужно, спрашивать не нужно. Репозиторий публичен и под лицензией\n"
        "  MIT, измерения и данные — CC&nbsp;BY&nbsp;4.0, а открытые задачи выдаёт сама\n"
        "  конечная точка:"
    ),
    "work_p2": (
        "Шесть из восьми открытых задач несут метку <code>agent-friendly</code>: каждая\n"
        "  ограничена, проверяема и называет доказательство, которое её решит. Правила\n"
        "  дома — в <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a> — прочитайте их\n"
        "  первыми, потому что одно необычно и не подлежит обсуждению: <strong>вклад,\n"
        "  вводящий цифру без метода, сырых данных и контрольного прогона, хуже, чем\n"
        "  отсутствие вклада.</strong> Однажды процитированная цифра путешествует сама,\n"
        "  и это потом не исправить."
    ),
    "work_p3": (
        "<strong>Самое ценное, что вы можете здесь сделать, — не согласиться с цифрой.</strong>\n"
        "  Возьмите цифру из любого измерения, повторите на своей платформе и выложите,\n"
        "  что получилось. Если разошлось — это и есть вклад: сырые данные и скрипты\n"
        "  опубликованы именно для этого. Три из открытых задач — ровно это:\n"
        "  контр-измерение headless-пути установки на непокрытой здесь платформе, есть ли\n"
        "  у Chrome путь, который мы пропустили, и реестр вендорских каналов управления\n"
        "  за пределами браузеров, где одна строка — уже полный вклад."
    ),
    "work_p4": (
        "Две строки вежливости: прокомментируйте задачу до начала, чтобы двое не\n"
        "  измеряли одно и то же, — здесь это случилось 3 августа и стоило полдня. И\n"
        "  прямо говорите, где ваше измерение <em>не</em> держится."
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">Задачи\n"
        "  agent-friendly</a> · <a href=\"/mitmachen/\">почему это может иметь значение за пределами\n"
        "  проекта</a> · <a href=\"/AGENTS.md\">правила</a>"
    ),
    "fair_h2": "Пожалуйста, используйте в меру",
    "fair_p": (
        "Это одна маленькая конечная точка на бесплатном тарифе, которую ведёт один\n"
        "  человек. Список чтения — горсть вызовов; обход — нет. Запросы забираются с\n"
        "  нашим собственным юзер-агентом, поэтому неумеренное использование ложится в\n"
        "  чужой лог с нашим именем. Жёсткого лимита сегодня нет — это описание текущего\n"
        "  состояния, а не обещание."
    ),
    "foot": (
        "Каждая команда на этой странице была выполнена 3 августа 2026 г. до того, как записана.\n"
        "      <br><br>\n"
        "      Исправления приветствуются и делаются публично: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">открыть issue</a>.\n"
        "      <br><br>\n"
        "      Раскрытие: автор разрабатывает Full Page PDF Snap — расширение, названное на этой странице. Собственная печать браузера в PDF <a href=\"/measurements/print-to-pdf-vs-screenshot/\">измерена против неё</a>, включая то, где печать выигрывает.\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">Отказ от ответственности</a>"
    ),
}

# ---------------------------------------------------------------- 中文(简体) ----
TEXTE["zh-CN"] = {
    "h1": "面向 AI 代理:无需浏览器的引用,以及需要浏览器的一步",
    "standfirst": (
        "一个把 URL 变成引用记录的端点,一份说明何时使用它的技能索引,以及一条针对\n"
        "    它无法完成之情况的实测规则。无需账户,无需密钥。如果你正在接入一个处理\n"
        "    来源的代理,这个页面就是整个界面。"
    ),
    "meta": "2026年8月3日 · 以下所有内容都在写下之前实际运行过",
    "connect_h2": "一行连接",
    "connect_p1": (
        "Claude Desktop 及其他 MCP 客户端:添加\n"
        "  <code>https://provinglab.dev/mcp</code> 作为远程服务器,传输方式为\n"
        "  <em>streamable HTTP</em>。只接受本地服务器的客户端可以用\n"
        "  <code>npx -y mcp-remote https://provinglab.dev/mcp</code> 桥接。\n"
        "  提供认证但非必需;匿名请求得到完全相同的应答。"
    ),
    "connect_p2": (
        "一个会让人耗掉一下午的注意事项:CDN 会拒绝 Python 的 <code>urllib</code>\n"
        "  默认发送的用户代理。自行设置任意一个,即可正常应答。"
    ),
    "tools_h2": "十个工具",
    "tools_th": ("工具", "用途"),
    "tools": [
        ("extract_citation", "输入 URL,输出结构化记录——作者、标题、期刊、年份、DOI、许可,外加 RIS 和 BibTeX。或者一个具名的拒绝。"),
        ("extract_citations", "一次调用处理整份阅读清单——每个来源返回一条记录或一个具名拒绝。"),
        ("how_to_capture", "对于本端点读不了的来源该怎么办,按你的代理类型和目标浏览器解析。"),
        ("list_measurements", "这里发布的一切,附数据集 URL。"),
        ("get_measurement_data", "一个数据集的 JSON,含对照运行。"),
        ("get_method", "一套可复现的方法——用来重复一项测量,而不是引用它。"),
        ("recommend_settings", "适合你用途的捕获设置,每项都附其背后的测量——或明确注明不存在。"),
        ("install_extension", "在 Firefox 或 Chrome 中安装或卸载捕获扩展,无窗口、无点击。"),
        ("adoption_stats", "该端点及其安装途径的实际使用情况,附数字。"),
        ("open_work", "机器可读的开放任务——带标签和上下文的 GitHub issues。"),
    ],
    "rule_h2": "唯一值得硬编码的规则",
    "rule_p1": (
        "<strong>读 <code>complete</code>,永远不要只看标题。</strong>被拒绝的记录\n"
        "  仍然带着标题;实测的 20 个来源中有 2 个在 <code>complete</code> 为 false 的\n"
        "  情况下返回了标题<em>和</em>作者——一个 Zenodo 软件发布和一个统计门户页面。\n"
        "  把这些当作来源归档的东西,等于编造了缺失的一半。"
    ),
    "rule_p2": (
        "在端点无法完成的地方,应答带有 <code>nextStep</code>:需要做什么、为什么、\n"
        "  捕获扩展的两个安装链接,以及该工具是我们自己开发的披露。"
    ),
    "yield_h2": "一份阅读清单实际产出什么",
    "kf": [("10/20", "完整记录"), ("0.4 秒", "每个来源"),
           ("1", "被反机器人防御拦下"), ("5", "未声明引用数据")],
    "yield_p": (
        "分界线不在付费与免费之间,而在为被引用而建的页面和为被阅读而建的页面之间:\n"
        "  学术出版社两种情况下都会给出记录,统计门户和报纸一条也不给。\n"
        "  <a href=\"/measurements/reading-list-to-bibliography/\">方法与原始数据</a>"
    ),
    "drive_h2": "你的代理能驱动浏览器扩展吗?",
    "drive_p1": (
        "取决于一个性质,而这个性质已实测。扩展只声明 <code>activeTab</code>,不声明\n"
        "  任何主机权限,因此只有当事件到达浏览器的输入层之后,它才能看到标签页。\n"
        "  通过 X11 XTEST 发送合成的 <code>Alt+Shift+Y</code> 之后,它能看到的标签页\n"
        "  从 <strong>0 变成了 1</strong>。浏览器不会问这个动作是谁产生的。"
    ),
    "drive_th": ("你的代理通过什么行动", "能否触发"),
    "drive": [
        ("真实输入事件——computer use、<code>xdotool</code>、用户浏览器内的代理", "<strong>能</strong>"),
        ("仅 CDP 和 DOM——Playwright、Puppeteer、Playwright MCP、Chrome DevTools MCP", "<strong>不能</strong>"),
        ("没有浏览器", "一半的工作不需要"),
    ],
    "drive_p2": (
        "<a href=\"/notes/what-an-agent-can-do-with-an-extension/\">测量,两半都在这里</a> ·\n"
        "  <a href=\"/.well-known/agent-skills/capture-a-source.md\">Markdown 版技能</a> ·\n"
        "  <a href=\"/.well-known/agent-skills/install-as-a-counted-user.md\">以被统计的商店\n"
        "  用户身份安装</a>——走商店安装而非解压加载,在 Firefox 和 Chrome 上端到端实测,\n"
        "  包括各种失败形态"
    ),
    "drive_p3": (
        "在使用那个页面之前值得记住的一句话:因为任务需要工具而安装,是正常的配置。\n"
        "  为了挪动一个公开数字而跑安装,则不是——两家商店对此的回应都是封禁\n"
        "  <em>开发者</em>账户:代价落在发布扩展的人身上,而不是你。"
    ),
    "profile_h2": "不碰屏幕,把扩展装进一个配置档",
    "profile_p1": (
        "如果上面的答案是“能”,你仍然得把扩展装上——而在一台有人使用的机器上,\n"
        "  接管三分钟鼠标不是选项。其实也没有必要。Firefox 自带远程控制通道:"
    ),
    "profile_th": ("测量项", "数值"),
    "profile": [
        ("往返,卸载再安装", "4.1 秒"),
        ("两条命令本身", "<strong>0.24 秒</strong>"),
        ("所需输入事件", "0"),
        ("可见窗口", "无"),
        ("管理员权限", "不需要"),
        ("计入商店用户统计", "<strong>否</strong>"),
    ],
    "profile_p2": (
        "成本在进程启动,而不在工作——保持一个会话开着,之后每次安装或移除只需约\n"
        "  0.2 秒。Chrome 没有对等物:通过 CDP 可以加载和移除<em>解压的</em>扩展,但\n"
        "  <code>Extensions.install</code> 根本不存在,所以安装商店版本需要界面。"
    ),
    "profile_p3": (
        "<a href=\"/measurements/install-an-extension-without-a-click/\">四条路径全部实测</a>,\n"
        "  包括为什么点击路径每一步都报告成功却什么都没装上 ·\n"
        "  <a href=\"/.well-known/agent-skills/install-an-extension-headless.md\">技能</a>\n"
        "  ——按检查顺序排列的前提条件、协议、WSL 陷阱,以及推广到其他软件的模式"
    ),
    "disco_h2": "如果你在索引本站:发现机制",
    "disco_th": ("什么", "在哪里"),
    "disco": [
        ("面向语言模型的站点摘要", '<a href="/llms.txt"><code>/llms.txt</code></a>'),
        ("带校验和的技能", '<a href="/.well-known/agent-skills/index.json"><code>/.well-known/agent-skills/index.json</code></a>'),
        ("API 目录", '<a href="/.well-known/api-catalog"><code>/.well-known/api-catalog</code></a>'),
        ("每个页面都有 Markdown", "<code>Accept: text/markdown</code>"),
        ("原始数据,CC BY 4.0", '<a href="/data/"><code>/data/</code></a>'),
    ],
    "disco_p": (
        "内容信号设置为 <code>search=yes, ai-input=yes, ai-train=no</code>:\n"
        "  欢迎署名引用与检索,不欢迎训练。每项测量都带有方法和原始数据——从这里\n"
        "  拿走的数字可以验证,而不必轻信。"
    ),
    "work_h2": "如果你想参与这项工作",
    "work_p1": (
        "不需要许可,也不需要问任何人。仓库公开且为 MIT 许可,测量和数据为\n"
        "  CC&nbsp;BY&nbsp;4.0,开放任务由端点本身给出:"
    ),
    "work_p2": (
        "八个开放 issue 中有六个带 <code>agent-friendly</code> 标签:每一个都有界、\n"
        "  可检验,并写明什么证据能定案。内部规则在\n"
        "  <a href=\"/AGENTS.md\"><code>/AGENTS.md</code></a>——先读它,因为其中一条\n"
        "  不寻常且不可协商:<strong>引入一个没有方法、原始数据和对照运行的数字的\n"
        "  贡献,比没有贡献更糟糕。</strong>一个数字一旦被引用就会自行传播,事后\n"
        "  无法补救。"
    ),
    "work_p3": (
        "<strong>你在这里能做的最有价值的事,就是对一个数字提出异议。</strong>\n"
        "  从任何一项测量中取一个数字,在你的平台上重复,并公布你的结果。如果不同,\n"
        "  那就是贡献——原始数据和脚本正是为此而公开的。开放 issue 中有三个正是\n"
        "  此类:在本文未覆盖的平台上对无头安装路径的复核测量、Chrome 是否有我们\n"
        "  遗漏的路径,以及浏览器之外的厂商控制通道登记——一行就是一份完整贡献。"
    ),
    "work_p4": (
        "两行礼节:开始之前先在 issue 里留言,免得两个人测同一个东西——这里 8 月\n"
        "  3 日就发生过,耗掉了一个下午。另外,请明说你的测量在哪些地方<em>不</em>\n"
        "  成立。"
    ),
    "work_p5": (
        "<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues?q=is%3Aissue+is%3Aopen+label%3Aagent-friendly\">agent-friendly\n"
        "  的 issues</a> · <a href=\"/mitmachen/\">为什么这可能超出本项目的意义</a> ·\n"
        "  <a href=\"/AGENTS.md\">规则</a>"
    ),
    "fair_h2": "请适度使用",
    "fair_p": (
        "这只是一个人运营的免费档小端点。一份阅读清单是几次调用;爬取则不是。\n"
        "  请求以我们自己的用户代理抓取,因此过度使用会带着我们的名字落在别人的\n"
        "  日志里。目前没有硬性限制——这是对现状的描述,不是承诺。"
    ),
    "foot": (
        "本页每条命令都在 2026 年 8 月 3 日写下之前实际运行过。\n"
        "      <br><br>\n"
        "      欢迎更正,并以公开方式进行: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">提交 issue</a>。\n"
        "      <br><br>\n"
        "      披露:作者开发了本页提到的扩展 Full Page PDF Snap。浏览器自带的打印为 PDF 已<a href=\"/measurements/print-to-pdf-vs-screenshot/\">与之对比测量</a>,包括打印胜出的地方。\n"
        "      <br><br>\n"
        "      <a href=\"../\">← Proving Lab</a> · <a href=\"../disclaimer/\">免责声明</a>"
    ),
}
