#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Recipes-Seite in neun Sprachen — getrennt vom Bauen.

Muster wie texte_for_agents.py: ENGLISCH ist die Ausgangsfassung (woertlich aus
der bestehenden Seite uebernommen), Rendering ueber build-recipes-page.py.
Code-Bloecke (pre) stehen als Konstanten im Builder und bleiben in jeder
Sprache unveraendert — es sind Befehle, keine Prosa. Anker-IDs ebenfalls.

Aenderungen am Inhalt HIER, danach `python3 build-recipes-page.py`.
"""

URL = "https://provinglab.dev/recipes/"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "crumb": "Recipes",
    "h1": "Recipes: turn a web source into a citation",
    "standfirst": (
        "Short, complete instructions for the citation endpoint at\n"
        "    <code>/mcp</code> — in a terminal, in WSL, in Python, and in AI tools that\n"
        "    speak MCP. Every one of them was run on 3 August 2026 before it was written\n"
        "    down; an untested recipe is a claim."
    ),
    "meta": (
        "No account and no key · fair use, please ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">what the endpoint is and what it refuses</a>"
    ),
    "getback_h3": "What you get back",
    "getback_p": (
        "For a page that is a work: authors, title, journal, year, volume, pages,\n"
        "    DOI, ISSN and licence — plus a ready-to-import <strong>RIS record</strong>\n"
        "    and a <strong>BibTeX entry</strong>. For a page that is a paywall, an error\n"
        "    or a bot check: <code>complete: false</code> and a warning naming the wall.\n"
        "    <strong>Test <code>complete</code> before you file the result</strong> — a\n"
        "    refused record still carries a title, and it will read like a work."
    ),
    "rl_h2": "A reading list becomes a .ris file",
    "rl_p1": (
        "The recipe most people actually want. One URL per line in\n"
        "  <code>reading-list.txt</code>, one importable file out. Sources that cannot be\n"
        "  read are named on stderr and left out of the file rather than half-imported."
    ),
    "rl_p2": (
        "Then <strong>Zotero → File → Import</strong>, or <strong>Citavi →\n"
        "  Import → RIS</strong>. Measured on three scholarly URLs: three records,\n"
        "  under two seconds, imported without editing."
    ),
    "cc_h2": "Claude Code, in one line",
    "cc_p": (
        "<code>claude mcp list</code> then reports <code>✔ Connected</code>. After that\n"
        "  you can simply say: <em>\"cite these four links for my bibliography\"</em> — the\n"
        "  tool is called for each one, and the ones behind a wall are reported as such\n"
        "  instead of invented."
    ),
    "cd_h2": "Claude Desktop and other MCP clients",
    "cd_p": (
        "Add <code>https://provinglab.dev/mcp</code> as a <strong>remote MCP\n"
        "  server</strong> (transport: streamable HTTP). Authentication is offered but not\n"
        "  required; anonymous requests get identical answers. In clients that only accept\n"
        "  local servers, the usual bridge works:"
    ),
    "py_h2": "Python — mind the user agent",
    "py_p": (
        "The standard library identifies itself as <code>Python-urllib</code>, and the\n"
        "  CDN in front of this site answers that with <strong>HTTP 403</strong> before the\n"
        "  worker ever sees the request. Any user agent of your own is enough. This is not\n"
        "  a rule against automation — it is a filter that does not know the difference."
    ),
    "wsl_h2": "WSL: from the browser into the terminal",
    "wsl_p1": (
        "The two halves of the work sit on different sides of the filesystem boundary.\n"
        "  A source behind a university login can only be captured in the browser, and\n"
        "  the file then has to be found from a shell."
    ),
    "wsl_p2": (
        "In <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>, switch on\n"
        "  <em>Copy file path after saving</em> and set the format to <strong>WSL</strong>\n"
        "  under Settings. After a capture the path is on the clipboard in the shape a\n"
        "  Linux shell understands:"
    ),
    "wsl_p3": (
        "Paste it straight after a command, or into a chat with an AI tool that can read\n"
        "  files. The RIS record for the same capture sits next to the PDF with the same\n"
        "  name and a <code>.ris</code> extension."
    ),
    "wr_h2": "Which of the two routes for which source",
    "wr_th": ("The endpoint", "The extension"),
    # Zeile: (Beschriftung, Endpunkt-Zelle, deren Klasse, Erweiterungs-Zelle, deren Klasse)
    "wr_rows": [
        ("Runs", "on a server, anonymous", "", "in your browser, logged in", ""),
        ("Gives you", "the reference", "", "the reference <em>and</em> the document", ""),
        ("Behind a login", "no", "lose", "yes", "win"),
        ("Cost per source", "none, scriptable", "win", "one click", ""),
        ("Output", "RIS + BibTeX", "", "PDF with the fields inside, plus RIS", ""),
    ],
    "wr_p": (
        "So the division is not a compromise: <strong>the endpoint for volume, the\n"
        "  extension for the ones it refuses</strong>. Both emit the same RIS format, so\n"
        "  everything lands in one Zotero or Citavi library regardless of the route. The\n"
        "  refusal list from the first pass tells you which sources need the second."
    ),
    "ma_h2": "For an agent rather than a person",
    "ma_p": (
        "These recipes are also published as a machine-readable skill, alongside the\n"
        "  measurement methods:"
    ),
    # (href, Verweistext, Erlaeuterung dahinter)
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— the skills with their checksums"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— this page as a procedure"),
        ("/llms.txt", "llms.txt",
         "— everything published here, as plain text"),
        ("/.well-known/mcp/server-card.json", "server card",
         "— the tools and the transport"),
    ],
    "proves_h3": "What none of this proves",
    "proves_p": (
        "A citation record says what a page declares about itself. It is not a check\n"
        "    that the work exists, that the DOI resolves to it, or that the page is\n"
        "    honest — for the eight of eighteen platforms where the data is thin, that\n"
        "    matters. A screen capture, likewise, is a picture of a screen and\n"
        "    <a href=\"/disclaimer/\">not a qualified electronic document</a>. Where the\n"
        "    content decides something, read the source."
    ),
    "disclosure": (
        "Disclosure: this site is run by the developer of Full Page PDF Snap, the "
        "extension named on this page. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "The browser's own print-to-PDF is measured against it</a>, including where "
        "print wins. Corrections: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "GitHub issues</a> · <a href=\"/disclaimer/\">Disclaimer</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Tools</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">About the endpoint</a> ·\n"
        "  <a href=\"/disclaimer/\">Disclaimer</a>"
    ),
}

# --------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "crumb": "Rezepte",
    "h1": "Rezepte: aus einer Webquelle eine Literaturangabe machen",
    "standfirst": (
        "Kurze, vollständige Anleitungen für den Zitations-Endpunkt unter\n"
        "    <code>/mcp</code> — im Terminal, in WSL, in Python und in KI-Werkzeugen,\n"
        "    die MCP sprechen. Jede einzelne wurde am 3. August 2026 ausgeführt, bevor\n"
        "    sie aufgeschrieben wurde; ein ungetestetes Rezept ist eine Behauptung."
    ),
    "meta": (
        "Kein Konto und kein Schlüssel · bitte fair nutzen ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">was der Endpunkt ist und was er ablehnt</a>"
    ),
    "getback_h3": "Was zurückkommt",
    "getback_p": (
        "Für eine Seite, die ein Werk ist: Autor:innen, Titel, Zeitschrift, Jahr,\n"
        "    Jahrgang, Seiten, DOI, ISSN und Lizenz — dazu ein importfertiger\n"
        "    <strong>RIS-Datensatz</strong> und ein <strong>BibTeX-Eintrag</strong>. Für eine\n"
        "    Seite, die eine Paywall, ein Fehler oder eine Bot-Prüfung ist:\n"
        "    <code>complete: false</code> und eine Warnung, die die Sperre benennt.\n"
        "    <strong>Prüfen Sie <code>complete</code>, bevor Sie das Ergebnis ablegen</strong>\n"
        "    — ein abgelehnter Datensatz trägt trotzdem einen Titel und liest sich wie ein Werk."
    ),
    "rl_h2": "Aus einer Leseliste wird eine .ris-Datei",
    "rl_p1": (
        "Das Rezept, das die meisten tatsächlich wollen. Eine URL pro Zeile in\n"
        "  <code>reading-list.txt</code>, eine importierbare Datei als Ergebnis. Quellen,\n"
        "  die nicht gelesen werden können, werden auf stderr genannt und bleiben aus\n"
        "  der Datei draußen, statt halb importiert zu werden."
    ),
    "rl_p2": (
        "Dann <strong>Zotero → Datei → Importieren</strong> oder <strong>Citavi →\n"
        "  Importieren → RIS</strong>. Gemessen an drei wissenschaftlichen URLs: drei\n"
        "  Datensätze, unter zwei Sekunden, ohne Nachbearbeitung importiert."
    ),
    "cc_h2": "Claude Code, in einer Zeile",
    "cc_p": (
        "<code>claude mcp list</code> meldet danach <code>✔ Connected</code>. Ab dann\n"
        "  genügt: <em>„zitiere diese vier Links für mein Literaturverzeichnis\"</em> —\n"
        "  das Werkzeug wird für jeden aufgerufen, und die hinter einer Sperre werden\n"
        "  als solche gemeldet statt erfunden."
    ),
    "cd_h2": "Claude Desktop und andere MCP-Clients",
    "cd_p": (
        "<code>https://provinglab.dev/mcp</code> als <strong>entfernten MCP-Server</strong>\n"
        "  eintragen (Transport: streamable HTTP). Eine Anmeldung wird angeboten, ist\n"
        "  aber nicht nötig; anonyme Anfragen bekommen identische Antworten. In Clients,\n"
        "  die nur lokale Server akzeptieren, funktioniert die übliche Brücke:"
    ),
    "py_h2": "Python — den User-Agent beachten",
    "py_p": (
        "Die Standardbibliothek meldet sich als <code>Python-urllib</code>, und das CDN\n"
        "  vor dieser Seite antwortet darauf mit <strong>HTTP 403</strong>, bevor der\n"
        "  Worker die Anfrage überhaupt sieht. Jeder eigene User-Agent genügt. Das ist\n"
        "  keine Regel gegen Automatisierung — es ist ein Filter, der den Unterschied\n"
        "  nicht kennt."
    ),
    "wsl_h2": "WSL: vom Browser ins Terminal",
    "wsl_p1": (
        "Die beiden Hälften der Arbeit liegen auf verschiedenen Seiten der\n"
        "  Dateisystem-Grenze. Eine Quelle hinter einem Hochschul-Login lässt sich nur\n"
        "  im Browser erfassen, und die Datei muss danach von einer Shell aus zu\n"
        "  finden sein."
    ),
    "wsl_p2": (
        "In <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>\n"
        "  <em>Copy file path after saving</em> einschalten und in den Einstellungen das\n"
        "  Format <strong>WSL</strong> wählen. Nach einer Erfassung liegt der Pfad in der\n"
        "  Zwischenablage in der Form, die eine Linux-Shell versteht:"
    ),
    "wsl_p3": (
        "Fügen Sie ihn direkt hinter einen Befehl ein oder in einen Chat mit einem\n"
        "  KI-Werkzeug, das Dateien lesen kann. Der RIS-Datensatz zur selben Erfassung\n"
        "  liegt mit gleichem Namen und der Endung <code>.ris</code> neben der PDF."
    ),
    "wr_h2": "Welcher der beiden Wege für welche Quelle",
    "wr_th": ("Der Endpunkt", "Die Erweiterung"),
    "wr_rows": [
        ("Läuft", "auf einem Server, anonym", "", "in Ihrem Browser, angemeldet", ""),
        ("Liefert", "die Literaturangabe", "", "die Literaturangabe <em>und</em> das Dokument", ""),
        ("Hinter einem Login", "nein", "lose", "ja", "win"),
        ("Aufwand pro Quelle", "keiner, skriptfähig", "win", "ein Klick", ""),
        ("Ausgabe", "RIS + BibTeX", "", "PDF mit den Feldern darin, plus RIS", ""),
    ],
    "wr_p": (
        "Die Aufteilung ist also kein Kompromiss: <strong>der Endpunkt für die Menge,\n"
        "  die Erweiterung für die, die er ablehnt</strong>. Beide geben dasselbe\n"
        "  RIS-Format aus, also landet alles in derselben Zotero- oder Citavi-Bibliothek,\n"
        "  egal über welchen Weg. Die Ablehnungsliste aus dem ersten Durchlauf sagt,\n"
        "  welche Quellen den zweiten brauchen."
    ),
    "ma_h2": "Für einen Agenten statt für einen Menschen",
    "ma_p": (
        "Diese Rezepte liegen auch als maschinenlesbarer Skill vor, zusammen mit den\n"
        "  Messmethoden:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— die Skills mit ihren Prüfsummen"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— diese Seite als Prozedur"),
        ("/llms.txt", "llms.txt",
         "— alles Veröffentlichte hier als Klartext"),
        ("/.well-known/mcp/server-card.json", "Server-Karte",
         "— die Werkzeuge und der Transport"),
    ],
    "proves_h3": "Was all das nicht beweist",
    "proves_p": (
        "Ein Zitationsdatensatz sagt, was eine Seite über sich selbst deklariert. Er\n"
        "    prüft nicht, ob das Werk existiert, ob die DOI darauf auflöst oder ob die\n"
        "    Seite ehrlich ist — für die acht von achtzehn Plattformen, bei denen die\n"
        "    Daten dünn sind, ist das relevant. Eine Bildschirmaufnahme ist ebenfalls\n"
        "    ein Bild eines Bildschirms und <a href=\"/disclaimer/\">kein qualifiziertes\n"
        "    elektronisches Dokument</a>. Wo der Inhalt etwas entscheidet, lesen Sie\n"
        "    die Quelle."
    ),
    "disclosure": (
        "Offenlegung: Diese Seite wird vom Entwickler von Full Page PDF Snap betrieben, "
        "der auf dieser Seite genannten Erweiterung. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "Der eigene Druck-zu-PDF des Browsers ist dagegen gemessen</a>, einschließlich "
        "der Fälle, in denen Drucken gewinnt. Korrekturen: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "GitHub Issues</a> · <a href=\"/disclaimer/\">Haftungsausschluss</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Werkzeuge</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">Über den Endpunkt</a> ·\n"
        "  <a href=\"/disclaimer/\">Haftungsausschluss</a>"
    ),
}

# --------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "crumb": "Recetas",
    "h1": "Recetas: convierte una fuente web en una cita",
    "standfirst": (
        "Instrucciones cortas y completas para el endpoint de citas en\n"
        "    <code>/mcp</code> — en un terminal, en WSL, en Python y en herramientas\n"
        "    de IA que hablan MCP. Cada una se ejecutó el 3 de agosto de 2026 antes\n"
        "    de escribirse; una receta no probada es una afirmación."
    ),
    "meta": (
        "Sin cuenta y sin clave · uso justo, por favor ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">qué es el endpoint y qué rechaza</a>"
    ),
    "getback_h3": "Lo que recibes de vuelta",
    "getback_p": (
        "Para una página que es una obra: autores, título, revista, año, volumen,\n"
        "    páginas, DOI, ISSN y licencia — además de un <strong>registro RIS</strong>\n"
        "    listo para importar y una <strong>entrada BibTeX</strong>. Para una página\n"
        "    que es un muro de pago, un error o una prueba anti-bots:\n"
        "    <code>complete: false</code> y una advertencia que nombra el muro.\n"
        "    <strong>Comprueba <code>complete</code> antes de archivar el resultado</strong>\n"
        "    — un registro rechazado sigue llevando un título y se leerá como una obra."
    ),
    "rl_h2": "Una lista de lectura se convierte en un archivo .ris",
    "rl_p1": (
        "La receta que la mayoría realmente quiere. Una URL por línea en\n"
        "  <code>reading-list.txt</code>, un archivo importable como resultado. Las\n"
        "  fuentes que no se pueden leer se nombran en stderr y quedan fuera del\n"
        "  archivo en lugar de importarse a medias."
    ),
    "rl_p2": (
        "Después, <strong>Zotero → Archivo → Importar</strong>, o <strong>Citavi →\n"
        "  Importar → RIS</strong>. Medido con tres URL académicas: tres registros,\n"
        "  menos de dos segundos, importados sin edición."
    ),
    "cc_h2": "Claude Code, en una línea",
    "cc_p": (
        "<code>claude mcp list</code> informa entonces <code>✔ Connected</code>. Después\n"
        "  basta decir: <em>\"cita estos cuatro enlaces para mi bibliografía\"</em> — la\n"
        "  herramienta se llama para cada uno, y los que están detrás de un muro se\n"
        "  reportan como tales en lugar de inventarse."
    ),
    "cd_h2": "Claude Desktop y otros clientes MCP",
    "cd_p": (
        "Añade <code>https://provinglab.dev/mcp</code> como <strong>servidor MCP\n"
        "  remoto</strong> (transporte: streamable HTTP). La autenticación se ofrece\n"
        "  pero no es necesaria; las peticiones anónimas reciben respuestas idénticas.\n"
        "  En clientes que solo aceptan servidores locales, el puente habitual funciona:"
    ),
    "py_h2": "Python — cuidado con el user agent",
    "py_p": (
        "La biblioteca estándar se identifica como <code>Python-urllib</code>, y el CDN\n"
        "  delante de este sitio responde a eso con <strong>HTTP 403</strong> antes de\n"
        "  que el worker llegue a ver la petición. Cualquier user agent propio es\n"
        "  suficiente. No es una regla contra la automatización — es un filtro que no\n"
        "  conoce la diferencia."
    ),
    "wsl_h2": "WSL: del navegador al terminal",
    "wsl_p1": (
        "Las dos mitades del trabajo están a lados distintos de la frontera del\n"
        "  sistema de archivos. Una fuente detrás de un login universitario solo puede\n"
        "  capturarse en el navegador, y luego hay que encontrar el archivo desde\n"
        "  una shell."
    ),
    "wsl_p2": (
        "En <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>, activa\n"
        "  <em>Copy file path after saving</em> y pon el formato <strong>WSL</strong>\n"
        "  en Settings. Tras una captura, la ruta queda en el portapapeles en la forma\n"
        "  que entiende una shell de Linux:"
    ),
    "wsl_p3": (
        "Pégala directamente tras un comando, o en un chat con una herramienta de IA\n"
        "  que pueda leer archivos. El registro RIS de la misma captura está junto al\n"
        "  PDF con el mismo nombre y la extensión <code>.ris</code>."
    ),
    "wr_h2": "Cuál de las dos rutas para cada fuente",
    "wr_th": ("El endpoint", "La extensión"),
    "wr_rows": [
        ("Se ejecuta", "en un servidor, anónimo", "", "en tu navegador, con sesión iniciada", ""),
        ("Te da", "la referencia", "", "la referencia <em>y</em> el documento", ""),
        ("Detrás de un login", "no", "lose", "sí", "win"),
        ("Coste por fuente", "ninguno, scriptable", "win", "un clic", ""),
        ("Salida", "RIS + BibTeX", "", "PDF con los campos dentro, más RIS", ""),
    ],
    "wr_p": (
        "Así que la división no es un compromiso: <strong>el endpoint para el volumen,\n"
        "  la extensión para las que rechaza</strong>. Ambos emiten el mismo formato\n"
        "  RIS, así que todo llega a la misma biblioteca de Zotero o Citavi sea cual\n"
        "  sea la ruta. La lista de rechazos del primer paso te dice qué fuentes\n"
        "  necesitan la segunda."
    ),
    "ma_h2": "Para un agente en lugar de una persona",
    "ma_p": (
        "Estas recetas también se publican como un skill legible por máquinas, junto\n"
        "  a los métodos de medición:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— los skills con sus sumas de verificación"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— esta página como procedimiento"),
        ("/llms.txt", "llms.txt",
         "— todo lo publicado aquí, como texto plano"),
        ("/.well-known/mcp/server-card.json", "ficha del servidor",
         "— las herramientas y el transporte"),
    ],
    "proves_h3": "Lo que nada de esto demuestra",
    "proves_p": (
        "Un registro de cita dice lo que una página declara sobre sí misma. No\n"
        "    comprueba que la obra exista, que el DOI resuelva a ella o que la página\n"
        "    sea honesta — para las ocho de dieciocho plataformas donde los datos son\n"
        "    escasos, eso importa. Una captura de pantalla, igualmente, es una imagen\n"
        "    de una pantalla y <a href=\"/disclaimer/\">no un documento electrónico\n"
        "    cualificado</a>. Donde el contenido decide algo, lee la fuente."
    ),
    "disclosure": (
        "Aviso: este sitio lo gestiona el desarrollador de Full Page PDF Snap, la "
        "extensión nombrada en esta página. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "La impresión a PDF del propio navegador está medida contra ella</a>, incluyendo "
        "dónde gana la impresión. Correcciones: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "issues de GitHub</a> · <a href=\"/disclaimer/\">Aviso legal</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Herramientas</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">Sobre el endpoint</a> ·\n"
        "  <a href=\"/disclaimer/\">Aviso legal</a>"
    ),
}

# --------------------------------------------------------------- Français ---
TEXTE["fr"] = {
    "crumb": "Recettes",
    "h1": "Recettes : transformer une source web en citation",
    "standfirst": (
        "Des instructions courtes et complètes pour le point d'accès de citation\n"
        "    sous <code>/mcp</code> — dans un terminal, dans WSL, en Python et dans\n"
        "    des outils d'IA qui parlent MCP. Chacune a été exécutée le 3 août 2026\n"
        "    avant d'être écrite ; une recette non testée est une affirmation."
    ),
    "meta": (
        "Ni compte ni clé · usage équitable, merci ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">ce qu'est le point d'accès et ce qu'il refuse</a>"
    ),
    "getback_h3": "Ce que vous récupérez",
    "getback_p": (
        "Pour une page qui est une œuvre : auteurs, titre, revue, année, volume,\n"
        "    pages, DOI, ISSN et licence — plus un <strong>enregistrement RIS</strong>\n"
        "    prêt à importer et une <strong>entrée BibTeX</strong>. Pour une page qui\n"
        "    est un mur payant, une erreur ou un contrôle anti-robots :\n"
        "    <code>complete: false</code> et un avertissement qui nomme le mur.\n"
        "    <strong>Testez <code>complete</code> avant d'archiver le résultat</strong>\n"
        "    — un enregistrement refusé porte toujours un titre et se lira comme une œuvre."
    ),
    "rl_h2": "Une liste de lecture devient un fichier .ris",
    "rl_p1": (
        "La recette que la plupart veulent vraiment. Une URL par ligne dans\n"
        "  <code>reading-list.txt</code>, un fichier importable en sortie. Les sources\n"
        "  illisibles sont nommées sur stderr et laissées hors du fichier plutôt\n"
        "  qu'importées à moitié."
    ),
    "rl_p2": (
        "Puis <strong>Zotero → Fichier → Importer</strong>, ou <strong>Citavi →\n"
        "  Importer → RIS</strong>. Mesuré sur trois URL universitaires : trois\n"
        "  enregistrements, moins de deux secondes, importés sans retouche."
    ),
    "cc_h2": "Claude Code, en une ligne",
    "cc_p": (
        "<code>claude mcp list</code> affiche alors <code>✔ Connected</code>. Ensuite,\n"
        "  il suffit de dire : <em>« cite ces quatre liens pour ma bibliographie »</em>\n"
        "  — l'outil est appelé pour chacun, et ceux derrière un mur sont signalés\n"
        "  comme tels au lieu d'être inventés."
    ),
    "cd_h2": "Claude Desktop et les autres clients MCP",
    "cd_p": (
        "Ajoutez <code>https://provinglab.dev/mcp</code> comme <strong>serveur MCP\n"
        "  distant</strong> (transport : streamable HTTP). L'authentification est\n"
        "  proposée mais pas requise ; les requêtes anonymes obtiennent des réponses\n"
        "  identiques. Dans les clients qui n'acceptent que des serveurs locaux, le\n"
        "  pont habituel fonctionne :"
    ),
    "py_h2": "Python — attention au user agent",
    "py_p": (
        "La bibliothèque standard s'identifie comme <code>Python-urllib</code>, et le\n"
        "  CDN devant ce site répond par <strong>HTTP 403</strong> avant même que le\n"
        "  worker voie la requête. N'importe quel user agent à vous suffit. Ce n'est\n"
        "  pas une règle contre l'automatisation — c'est un filtre qui ne connaît pas\n"
        "  la différence."
    ),
    "wsl_h2": "WSL : du navigateur au terminal",
    "wsl_p1": (
        "Les deux moitiés du travail se situent de part et d'autre de la frontière\n"
        "  du système de fichiers. Une source derrière un login universitaire ne peut\n"
        "  être capturée que dans le navigateur, et le fichier doit ensuite être\n"
        "  retrouvé depuis un shell."
    ),
    "wsl_p2": (
        "Dans <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>, activez\n"
        "  <em>Copy file path after saving</em> et réglez le format sur\n"
        "  <strong>WSL</strong> dans les paramètres. Après une capture, le chemin est\n"
        "  dans le presse-papiers dans la forme qu'un shell Linux comprend :"
    ),
    "wsl_p3": (
        "Collez-le directement après une commande, ou dans un chat avec un outil\n"
        "  d'IA capable de lire des fichiers. L'enregistrement RIS de la même capture\n"
        "  se trouve à côté du PDF, avec le même nom et l'extension <code>.ris</code>."
    ),
    "wr_h2": "Laquelle des deux voies pour quelle source",
    "wr_th": ("Le point d'accès", "L'extension"),
    "wr_rows": [
        ("S'exécute", "sur un serveur, anonyme", "", "dans votre navigateur, connecté", ""),
        ("Vous donne", "la référence", "", "la référence <em>et</em> le document", ""),
        ("Derrière un login", "non", "lose", "oui", "win"),
        ("Coût par source", "aucun, scriptable", "win", "un clic", ""),
        ("Sortie", "RIS + BibTeX", "", "PDF avec les champs dedans, plus RIS", ""),
    ],
    "wr_p": (
        "La répartition n'est donc pas un compromis : <strong>le point d'accès pour\n"
        "  le volume, l'extension pour celles qu'il refuse</strong>. Les deux émettent\n"
        "  le même format RIS, donc tout aboutit dans une même bibliothèque Zotero ou\n"
        "  Citavi, quelle que soit la voie. La liste des refus du premier passage\n"
        "  indique quelles sources ont besoin de la seconde."
    ),
    "ma_h2": "Pour un agent plutôt qu'une personne",
    "ma_p": (
        "Ces recettes sont aussi publiées comme skill lisible par machine, aux côtés\n"
        "  des méthodes de mesure :"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— les skills avec leurs sommes de contrôle"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— cette page comme procédure"),
        ("/llms.txt", "llms.txt",
         "— tout ce qui est publié ici, en texte brut"),
        ("/.well-known/mcp/server-card.json", "fiche serveur",
         "— les outils et le transport"),
    ],
    "proves_h3": "Ce que rien de tout cela ne prouve",
    "proves_p": (
        "Un enregistrement de citation dit ce qu'une page déclare d'elle-même. Il ne\n"
        "    vérifie ni que l'œuvre existe, ni que le DOI mène à elle, ni que la page\n"
        "    est honnête — pour les huit plateformes sur dix-huit où les données sont\n"
        "    minces, cela compte. Une capture d'écran, de même, est l'image d'un écran\n"
        "    et <a href=\"/disclaimer/\">pas un document électronique qualifié</a>. Là\n"
        "    où le contenu décide, lisez la source."
    ),
    "disclosure": (
        "Transparence : ce site est géré par le développeur de Full Page PDF Snap, "
        "l'extension nommée sur cette page. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "L'impression en PDF du navigateur est mesurée face à elle</a>, y compris là "
        "où l'impression gagne. Corrections : <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "issues GitHub</a> · <a href=\"/disclaimer/\">Mentions légales</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Outils</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">À propos du point d'accès</a> ·\n"
        "  <a href=\"/disclaimer/\">Mentions légales</a>"
    ),
}

# --------------------------------------------------------------- Italiano ---
TEXTE["it"] = {
    "crumb": "Ricette",
    "h1": "Ricette: trasforma una fonte web in una citazione",
    "standfirst": (
        "Istruzioni brevi e complete per l'endpoint di citazione su <code>/mcp</code>\n"
        "    — in un terminale, in WSL, in Python e negli strumenti di IA che parlano\n"
        "    MCP. Ognuna è stata eseguita il 3 agosto 2026 prima di essere scritta;\n"
        "    una ricetta non testata è un'affermazione."
    ),
    "meta": (
        "Nessun account e nessuna chiave · uso corretto, per favore ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">cos'è l'endpoint e cosa rifiuta</a>"
    ),
    "getback_h3": "Cosa ricevi indietro",
    "getback_p": (
        "Per una pagina che è un'opera: autori, titolo, rivista, anno, volume,\n"
        "    pagine, DOI, ISSN e licenza — più un <strong>record RIS</strong> pronto\n"
        "    per l'importazione e una <strong>voce BibTeX</strong>. Per una pagina che\n"
        "    è un paywall, un errore o un controllo anti-bot: <code>complete: false</code>\n"
        "    e un avviso che nomina il muro. <strong>Verifica <code>complete</code>\n"
        "    prima di archiviare il risultato</strong> — un record rifiutato porta\n"
        "    comunque un titolo e si leggerà come un'opera."
    ),
    "rl_h2": "Una lista di lettura diventa un file .ris",
    "rl_p1": (
        "La ricetta che la maggior parte delle persone vuole davvero. Un URL per\n"
        "  riga in <code>reading-list.txt</code>, un file importabile in uscita. Le\n"
        "  fonti che non si possono leggere vengono nominate su stderr e lasciate\n"
        "  fuori dal file invece di essere importate a metà."
    ),
    "rl_p2": (
        "Poi <strong>Zotero → File → Importa</strong>, oppure <strong>Citavi →\n"
        "  Importa → RIS</strong>. Misurato su tre URL accademici: tre record, meno\n"
        "  di due secondi, importati senza modifiche."
    ),
    "cc_h2": "Claude Code, in una riga",
    "cc_p": (
        "<code>claude mcp list</code> riporta quindi <code>✔ Connected</code>. Dopo\n"
        "  puoi semplicemente dire: <em>\"cita questi quattro link per la mia\n"
        "  bibliografia\"</em> — lo strumento viene chiamato per ciascuno, e quelli\n"
        "  dietro un muro vengono segnalati come tali invece di essere inventati."
    ),
    "cd_h2": "Claude Desktop e altri client MCP",
    "cd_p": (
        "Aggiungi <code>https://provinglab.dev/mcp</code> come <strong>server MCP\n"
        "  remoto</strong> (trasporto: streamable HTTP). L'autenticazione è offerta\n"
        "  ma non richiesta; le richieste anonime ricevono risposte identiche. Nei\n"
        "  client che accettano solo server locali, il solito bridge funziona:"
    ),
    "py_h2": "Python — attenzione allo user agent",
    "py_p": (
        "La libreria standard si identifica come <code>Python-urllib</code>, e il CDN\n"
        "  davanti a questo sito risponde con <strong>HTTP 403</strong> prima ancora\n"
        "  che il worker veda la richiesta. Qualsiasi user agent tuo è sufficiente.\n"
        "  Non è una regola contro l'automazione — è un filtro che non conosce la\n"
        "  differenza."
    ),
    "wsl_h2": "WSL: dal browser al terminale",
    "wsl_p1": (
        "Le due metà del lavoro stanno ai lati opposti del confine del filesystem.\n"
        "  Una fonte dietro un login universitario può essere catturata solo nel\n"
        "  browser, e il file va poi ritrovato da una shell."
    ),
    "wsl_p2": (
        "In <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>, attiva\n"
        "  <em>Copy file path after saving</em> e imposta il formato <strong>WSL</strong>\n"
        "  nelle impostazioni. Dopo una cattura il percorso è negli appunti nella\n"
        "  forma che una shell Linux capisce:"
    ),
    "wsl_p3": (
        "Incollalo direttamente dopo un comando, o in una chat con uno strumento di\n"
        "  IA che sa leggere i file. Il record RIS della stessa cattura si trova\n"
        "  accanto al PDF con lo stesso nome e l'estensione <code>.ris</code>."
    ),
    "wr_h2": "Quale delle due vie per quale fonte",
    "wr_th": ("L'endpoint", "L'estensione"),
    "wr_rows": [
        ("Gira", "su un server, anonimo", "", "nel tuo browser, connesso", ""),
        ("Ti dà", "il riferimento", "", "il riferimento <em>e</em> il documento", ""),
        ("Dietro un login", "no", "lose", "sì", "win"),
        ("Costo per fonte", "nessuno, scriptabile", "win", "un clic", ""),
        ("Output", "RIS + BibTeX", "", "PDF con i campi dentro, più RIS", ""),
    ],
    "wr_p": (
        "Quindi la divisione non è un compromesso: <strong>l'endpoint per il volume,\n"
        "  l'estensione per quelle che rifiuta</strong>. Entrambi emettono lo stesso\n"
        "  formato RIS, così tutto finisce in un'unica biblioteca Zotero o Citavi\n"
        "  indipendentemente dalla via. L'elenco dei rifiuti del primo passaggio ti\n"
        "  dice quali fonti hanno bisogno della seconda."
    ),
    "ma_h2": "Per un agente invece che per una persona",
    "ma_p": (
        "Queste ricette sono pubblicate anche come skill leggibile dalle macchine,\n"
        "  insieme ai metodi di misurazione:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— gli skill con i loro checksum"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— questa pagina come procedura"),
        ("/llms.txt", "llms.txt",
         "— tutto ciò che è pubblicato qui, in testo semplice"),
        ("/.well-known/mcp/server-card.json", "scheda del server",
         "— gli strumenti e il trasporto"),
    ],
    "proves_h3": "Cosa tutto questo non dimostra",
    "proves_p": (
        "Un record di citazione dice ciò che una pagina dichiara di sé. Non verifica\n"
        "    che l'opera esista, che il DOI rimandi a lei o che la pagina sia onesta\n"
        "    — per le otto piattaforme su diciotto in cui i dati sono scarsi, questo\n"
        "    conta. Una cattura dello schermo, allo stesso modo, è l'immagine di uno\n"
        "    schermo e <a href=\"/disclaimer/\">non un documento elettronico\n"
        "    qualificato</a>. Dove il contenuto decide qualcosa, leggi la fonte."
    ),
    "disclosure": (
        "Trasparenza: questo sito è gestito dallo sviluppatore di Full Page PDF Snap, "
        "l'estensione nominata in questa pagina. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "La stampa in PDF del browser è misurata a confronto</a>, incluso dove la "
        "stampa vince. Correzioni: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "issue su GitHub</a> · <a href=\"/disclaimer/\">Disclaimer</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Strumenti</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">Informazioni sull'endpoint</a> ·\n"
        "  <a href=\"/disclaimer/\">Disclaimer</a>"
    ),
}

# ----------------------------------------------------------------- 日本語 ----
TEXTE["ja"] = {
    "crumb": "レシピ",
    "h1": "レシピ:ウェブの情報源を引用情報に変える",
    "standfirst": (
        "<code>/mcp</code> の引用エンドポイントのための、短く完全な手順集 ——\n"
        "    ターミナル、WSL、Python、そして MCP を話す AI ツール向け。すべて\n"
        "    2026年8月3日に実行してから書き起こしています。テストしていない\n"
        "    レシピは主張にすぎません。"
    ),
    "meta": (
        "アカウントもキーも不要 · 公正な利用をお願いします ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">エンドポイントの概要と拒否するもの</a>"
    ),
    "getback_h3": "返ってくるもの",
    "getback_p": (
        "著作物であるページの場合:著者、タイトル、雑誌名、年、巻、ページ、DOI、\n"
        "    ISSN、ライセンス —— 加えて、そのままインポートできる <strong>RIS\n"
        "    レコード</strong>と <strong>BibTeX エントリ</strong>。ペイウォール、エラー、\n"
        "    ボットチェックのページの場合:<code>complete: false</code> と、その壁を\n"
        "    名指しする警告。<strong>結果を保存する前に <code>complete</code> を確認して\n"
        "    ください</strong> —— 拒否されたレコードにもタイトルは残り、著作物のように\n"
        "    読めてしまいます。"
    ),
    "rl_h2": "読書リストが .ris ファイルになる",
    "rl_p1": (
        "ほとんどの人が本当に欲しいレシピ。<code>reading-list.txt</code> に 1 行\n"
        "  1 URL、出力はインポート可能な 1 ファイル。読み取れない情報源は stderr\n"
        "  に名前が出て、半端にインポートされるのではなくファイルから外されます。"
    ),
    "rl_p2": (
        "あとは <strong>Zotero → ファイル → インポート</strong>、または <strong>Citavi\n"
        "  → インポート → RIS</strong>。学術系 URL 3 件で実測:レコード 3 件、2 秒\n"
        "  未満、編集不要でインポート完了。"
    ),
    "cc_h2": "Claude Code、たった 1 行",
    "cc_p": (
        "<code>claude mcp list</code> が <code>✔ Connected</code> と表示します。あとは\n"
        "  <em>「この 4 つのリンクを参考文献用に引用して」</em>と言うだけ —— それぞれに\n"
        "  ツールが呼び出され、壁の向こうにあるものは捏造ではなく、壁があるとその\n"
        "  通りに報告されます。"
    ),
    "cd_h2": "Claude Desktop とその他の MCP クライアント",
    "cd_p": (
        "<code>https://provinglab.dev/mcp</code> を<strong>リモート MCP サーバー</strong>\n"
        "  として追加します(トランスポート: streamable HTTP)。認証は提供されて\n"
        "  いますが必須ではなく、匿名リクエストにも同じ回答が返ります。ローカル\n"
        "  サーバーしか受け付けないクライアントでは、おなじみのブリッジが使えます:"
    ),
    "py_h2": "Python —— ユーザーエージェントに注意",
    "py_p": (
        "標準ライブラリは <code>Python-urllib</code> と名乗ります。このサイトの前段の\n"
        "  CDN は、worker がリクエストを見る前に <strong>HTTP 403</strong> を返します。\n"
        "  自分のユーザーエージェントを 1 つ設定すれば十分です。これは自動化への\n"
        "  禁止ではありません —— 区別のつかないフィルターです。"
    ),
    "wsl_h2": "WSL:ブラウザからターミナルへ",
    "wsl_p1": (
        "作業の 2 つの半分は、ファイルシステムの境界の両側にあります。大学\n"
        "  ログインの向こうにある情報源はブラウザでしかキャプチャできず、その\n"
        "  ファイルをシェルから見つける必要があります。"
    ),
    "wsl_p2": (
        "<a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a> で <em>Copy file\n"
        "  path after saving</em> をオンにし、設定でフォーマットを <strong>WSL</strong>\n"
        "  にします。キャプチャ後、パスは Linux シェルが理解できる形でクリップ\n"
        "  ボードに入ります:"
    ),
    "wsl_p3": (
        "コマンドの直後に貼るか、ファイルを読める AI ツールとのチャットに貼って\n"
        "  ください。同じキャプチャの RIS レコードは、同じ名前に <code>.ris</code>\n"
        "  拡張子を付けて PDF の隣に保存されています。"
    ),
    "wr_h2": "2 つの経路、どちらをどの情報源に",
    "wr_th": ("エンドポイント", "拡張機能"),
    "wr_rows": [
        ("動作場所", "サーバー上、匿名", "", "あなたのブラウザ内、ログイン済み", ""),
        ("得られるもの", "書誌情報", "", "書誌情報<em>と</em>ドキュメント", ""),
        ("ログインの向こう", "不可", "lose", "可能", "win"),
        ("1 件あたりのコスト", "ゼロ、スクリプト可", "win", "1 クリック", ""),
        ("出力", "RIS + BibTeX", "", "フィールドを内蔵した PDF、加えて RIS", ""),
    ],
    "wr_p": (
        "つまりこの分担は妥協ではありません:<strong>件数にはエンドポイント、\n"
        "  拒否されたものには拡張機能</strong>。どちらも同じ RIS 形式を出力するので、\n"
        "  経路に関係なくすべて 1 つの Zotero または Citavi ライブラリに収まります。\n"
        "  最初のパスの拒否リストが、2 番目の経路が必要な情報源を教えてくれます。"
    ),
    "ma_h2": "人ではなくエージェントへ",
    "ma_p": (
        "これらのレシピは、測定方法と並んで、機械可読のスキルとしても公開して\n"
        "  います:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "—— スキルとそのチェックサム"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "—— このページを手続きとして"),
        ("/llms.txt", "llms.txt",
         "—— ここで公開しているすべて、プレーンテキストで"),
        ("/.well-known/mcp/server-card.json", "サーバーカード",
         "—— ツールとトランスポート"),
    ],
    "proves_h3": "これらが証明しないこと",
    "proves_p": (
        "引用レコードは、ページが自分について宣言していることを示すだけです。\n"
        "    著作物が実在すること、DOI がそれに解決されること、ページが正直である\n"
        "    ことを確認するものではありません —— データが薄い 18 プラットフォーム中\n"
        "    8 件では、それが重要です。画面キャプチャも同様に、画面の画像であり、\n"
        "    <a href=\"/disclaimer/\">適格な電子文書ではありません</a>。内容がものを\n"
        "    言う場面では、情報源そのものを読んでください。"
    ),
    "disclosure": (
        "開示:このサイトは、このページで名前の挙がっている拡張機能 Full Page PDF "
        "Snap の開発者が運営しています。<a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "ブラウザ自身の PDF 印刷との比較測定</a>では、印刷が勝る場合も含めています。"
        "訂正: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">GitHub "
        "issues</a> · <a href=\"/disclaimer/\">免責事項</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">ツール</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">エンドポイントについて</a> ·\n"
        "  <a href=\"/disclaimer/\">免責事項</a>"
    ),
}

# --------------------------------------------------------------- Português --
TEXTE["pt-BR"] = {
    "crumb": "Receitas",
    "h1": "Receitas: transforme uma fonte da web em uma citação",
    "standfirst": (
        "Instruções curtas e completas para o endpoint de citação em\n"
        "    <code>/mcp</code> — em um terminal, no WSL, em Python e em ferramentas\n"
        "    de IA que falam MCP. Cada uma foi executada em 3 de agosto de 2026 antes\n"
        "    de ser escrita; uma receita não testada é uma alegação."
    ),
    "meta": (
        "Sem conta e sem chave · uso justo, por favor ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">o que é o endpoint e o que ele recusa</a>"
    ),
    "getback_h3": "O que você recebe de volta",
    "getback_p": (
        "Para uma página que é uma obra: autores, título, periódico, ano, volume,\n"
        "    páginas, DOI, ISSN e licença — além de um <strong>registro RIS</strong>\n"
        "    pronto para importar e uma <strong>entrada BibTeX</strong>. Para uma página\n"
        "    que é um paywall, um erro ou uma verificação de bot: <code>complete:\n"
        "    false</code> e um aviso que nomeia o muro. <strong>Teste <code>complete</code>\n"
        "    antes de arquivar o resultado</strong> — um registro recusado ainda carrega\n"
        "    um título e vai se ler como uma obra."
    ),
    "rl_h2": "Uma lista de leitura vira um arquivo .ris",
    "rl_p1": (
        "A receita que a maioria realmente quer. Uma URL por linha em\n"
        "  <code>reading-list.txt</code>, um arquivo importável como saída. Fontes que\n"
        "  não podem ser lidas são nomeadas no stderr e ficam fora do arquivo em vez\n"
        "  de serem importadas pela metade."
    ),
    "rl_p2": (
        "Depois, <strong>Zotero → Arquivo → Importar</strong>, ou <strong>Citavi →\n"
        "  Importar → RIS</strong>. Medido em três URLs acadêmicas: três registros,\n"
        "  menos de dois segundos, importados sem edição."
    ),
    "cc_h2": "Claude Code, em uma linha",
    "cc_p": (
        "<code>claude mcp list</code> então reporta <code>✔ Connected</code>. Depois\n"
        "  disso, basta dizer: <em>\"cite estes quatro links para a minha bibliografia\"</em>\n"
        "  — a ferramenta é chamada para cada um, e os que estão atrás de um muro são\n"
        "  reportados como tal em vez de inventados."
    ),
    "cd_h2": "Claude Desktop e outros clientes MCP",
    "cd_p": (
        "Adicione <code>https://provinglab.dev/mcp</code> como <strong>servidor MCP\n"
        "  remoto</strong> (transporte: streamable HTTP). A autenticação é oferecida,\n"
        "  mas não é obrigatória; requisições anônimas recebem respostas idênticas.\n"
        "  Em clientes que só aceitam servidores locais, a ponte habitual funciona:"
    ),
    "py_h2": "Python — atenção ao user agent",
    "py_p": (
        "A biblioteca padrão se identifica como <code>Python-urllib</code>, e o CDN à\n"
        "  frente deste site responde a isso com <strong>HTTP 403</strong> antes mesmo\n"
        "  de o worker ver a requisição. Qualquer user agent seu é suficiente. Isso não\n"
        "  é uma regra contra automação — é um filtro que não conhece a diferença."
    ),
    "wsl_h2": "WSL: do navegador para o terminal",
    "wsl_p1": (
        "As duas metades do trabalho ficam em lados diferentes da fronteira do\n"
        "  sistema de arquivos. Uma fonte atrás de um login universitário só pode ser\n"
        "  capturada no navegador, e o arquivo precisa então ser encontrado a partir\n"
        "  de um shell."
    ),
    "wsl_p2": (
        "No <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a>, ative\n"
        "  <em>Copy file path after saving</em> e defina o formato <strong>WSL</strong>\n"
        "  nas configurações. Após uma captura, o caminho está na área de\n"
        "  transferência na forma que um shell Linux entende:"
    ),
    "wsl_p3": (
        "Cole diretamente após um comando, ou em um chat com uma ferramenta de IA\n"
        "  que saiba ler arquivos. O registro RIS da mesma captura fica ao lado do PDF\n"
        "  com o mesmo nome e a extensão <code>.ris</code>."
    ),
    "wr_h2": "Qual das duas rotas para qual fonte",
    "wr_th": ("O endpoint", "A extensão"),
    "wr_rows": [
        ("Roda", "em um servidor, anônimo", "", "no seu navegador, logado", ""),
        ("Entrega", "a referência", "", "a referência <em>e</em> o documento", ""),
        ("Atrás de um login", "não", "lose", "sim", "win"),
        ("Custo por fonte", "nenhum, scriptável", "win", "um clique", ""),
        ("Saída", "RIS + BibTeX", "", "PDF com os campos dentro, mais RIS", ""),
    ],
    "wr_p": (
        "Então a divisão não é um compromisso: <strong>o endpoint para o volume, a\n"
        "  extensão para as que ele recusa</strong>. Ambos emitem o mesmo formato RIS,\n"
        "  então tudo cai na mesma biblioteca do Zotero ou Citavi, qualquer que seja\n"
        "  a rota. A lista de recusas da primeira passada diz quais fontes precisam\n"
        "  da segunda."
    ),
    "ma_h2": "Para um agente, não para uma pessoa",
    "ma_p": (
        "Estas receitas também são publicadas como um skill legível por máquina,\n"
        "  junto aos métodos de medição:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— os skills com seus checksums"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— esta página como procedimento"),
        ("/llms.txt", "llms.txt",
         "— tudo o que é publicado aqui, em texto puro"),
        ("/.well-known/mcp/server-card.json", "cartão do servidor",
         "— as ferramentas e o transporte"),
    ],
    "proves_h3": "O que nada disso prova",
    "proves_p": (
        "Um registro de citação diz o que uma página declara sobre si mesma. Não\n"
        "    verifica se a obra existe, se o DOI resolve para ela ou se a página é\n"
        "    honesta — para as oito de dezoito plataformas em que os dados são\n"
        "    escassos, isso importa. Uma captura de tela, da mesma forma, é a imagem\n"
        "    de uma tela e <a href=\"/disclaimer/\">não um documento eletrônico\n"
        "    qualificado</a>. Onde o conteúdo decide algo, leia a fonte."
    ),
    "disclosure": (
        "Transparência: este site é mantido pelo desenvolvedor do Full Page PDF Snap, "
        "a extensão citada nesta página. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "A impressão em PDF do próprio navegador é medida em comparação</a>, incluindo "
        "onde a impressão vence. Correções: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "issues no GitHub</a> · <a href=\"/disclaimer/\">Aviso legal</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Ferramentas</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">Sobre o endpoint</a> ·\n"
        "  <a href=\"/disclaimer/\">Aviso legal</a>"
    ),
}

# ----------------------------------------------------------------- Русский --
TEXTE["ru"] = {
    "crumb": "Рецепты",
    "h1": "Рецепты: превратить веб-источник в библиографическую запись",
    "standfirst": (
        "Короткие, полные инструкции для конечной точки цитирования по адресу\n"
        "    <code>/mcp</code> — в терминале, в WSL, в Python и в ИИ-инструментах,\n"
        "    говорящих на MCP. Каждая была выполнена 3 августа 2026 года до того,\n"
        "    как была записана; непроверенный рецепт — это утверждение."
    ),
    "meta": (
        "Без аккаунта и без ключа · пожалуйста, используйте умеренно ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">что такое эта конечная точка и что она отклоняет</a>"
    ),
    "getback_h3": "Что вы получаете обратно",
    "getback_p": (
        "Для страницы, которая является произведением: авторы, название, журнал,\n"
        "    год, том, страницы, DOI, ISSN и лицензия — плюс готовая к импорту\n"
        "    <strong>запись RIS</strong> и <strong>запись BibTeX</strong>. Для страницы,\n"
        "    которая является платным барьером, ошибкой или проверкой на бота:\n"
        "    <code>complete: false</code> и предупреждение, называющее барьер.\n"
        "    <strong>Проверяйте <code>complete</code>, прежде чем сохранить результат</strong>\n"
        "    — отклонённая запись всё равно несёт заголовок и будет читаться как\n"
        "    произведение."
    ),
    "rl_h2": "Список чтения превращается в файл .ris",
    "rl_p1": (
        "Рецепт, который большинству действительно нужен. По одному URL на строку\n"
        "  в <code>reading-list.txt</code> — на выходе один импортируемый файл.\n"
        "  Источники, которые не удалось прочитать, называются в stderr и не попадают\n"
        "  в файл, вместо того чтобы импортироваться наполовину."
    ),
    "rl_p2": (
        "Затем <strong>Zotero → Файл → Импорт</strong> или <strong>Citavi → Импорт\n"
        "  → RIS</strong>. Замерено на трёх научных URL: три записи, меньше двух\n"
        "  секунд, импортированы без правок."
    ),
    "cc_h2": "Claude Code, одной строкой",
    "cc_p": (
        "<code>claude mcp list</code> затем показывает <code>✔ Connected</code>. После\n"
        "  этого можно просто сказать: <em>«процитируй эти четыре ссылки для моей\n"
        "  библиографии»</em> — инструмент вызывается для каждой, а те, что за\n"
        "  барьером, так и докладываются — вместо того чтобы выдумываться."
    ),
    "cd_h2": "Claude Desktop и другие MCP-клиенты",
    "cd_p": (
        "Добавьте <code>https://provinglab.dev/mcp</code> как <strong>удалённый\n"
        "  MCP-сервер</strong> (транспорт: streamable HTTP). Аутентификация\n"
        "  предлагается, но не требуется; анонимные запросы получают идентичные\n"
        "  ответы. В клиентах, принимающих только локальные серверы, работает\n"
        "  обычный мост:"
    ),
    "py_h2": "Python — не забудьте про user agent",
    "py_p": (
        "Стандартная библиотека представляется как <code>Python-urllib</code>, и CDN\n"
        "  перед этим сайтом отвечает на это <strong>HTTP 403</strong> ещё до того,\n"
        "  как worker увидит запрос. Достаточно любого собственного user agent. Это\n"
        "  не правило против автоматизации — это фильтр, который не знает разницы."
    ),
    "wsl_h2": "WSL: из браузера в терминал",
    "wsl_p1": (
        "Две половины работы находятся по разные стороны границы файловых систем.\n"
        "  Источник за университетским логином можно захватить только в браузере,\n"
        "  а файл затем нужно найти из командной строки."
    ),
    "wsl_p2": (
        "В <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a> включите\n"
        "  <em>Copy file path after saving</em> и установите формат <strong>WSL</strong>\n"
        "  в настройках. После захвата путь лежит в буфере обмена в виде, понятном\n"
        "  Linux-оболочке:"
    ),
    "wsl_p3": (
        "Вставьте его сразу после команды или в чат с ИИ-инструментом, умеющим\n"
        "  читать файлы. Запись RIS для того же захвата лежит рядом с PDF с тем же\n"
        "  именем и расширением <code>.ris</code>."
    ),
    "wr_h2": "Какой из двух путей — для какого источника",
    "wr_th": ("Конечная точка", "Расширение"),
    "wr_rows": [
        ("Работает", "на сервере, анонимно", "", "в вашем браузере, с логином", ""),
        ("Выдаёт", "библиографическое описание", "", "описание <em>и</em> документ", ""),
        ("За логином", "нет", "lose", "да", "win"),
        ("Цена за источник", "ноль, скриптуется", "win", "один клик", ""),
        ("Вывод", "RIS + BibTeX", "", "PDF с полями внутри, плюс RIS", ""),
    ],
    "wr_p": (
        "Так что разделение — не компромисс: <strong>конечная точка — для объёма,\n"
        "  расширение — для тех, кого она отклоняет</strong>. Обе выдают один и тот же\n"
        "  формат RIS, поэтому всё попадает в одну библиотеку Zotero или Citavi\n"
        "  независимо от пути. Список отказов первого прохода подскажет, каким\n"
        "  источникам нужен второй."
    ),
    "ma_h2": "Для агента, а не для человека",
    "ma_p": (
        "Эти рецепты также опубликованы как машиночитаемый навык, рядом с методами\n"
        "  измерений:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "— навыки с их контрольными суммами"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "— эта страница в виде процедуры"),
        ("/llms.txt", "llms.txt",
         "— всё опубликованное здесь, простым текстом"),
        ("/.well-known/mcp/server-card.json", "карточка сервера",
         "— инструменты и транспорт"),
    ],
    "proves_h3": "Чего всё это не доказывает",
    "proves_p": (
        "Библиографическая запись говорит лишь то, что страница заявляет о себе.\n"
        "    Она не проверяет, существует ли произведение, ведёт ли DOI на него и\n"
        "    честна ли страница — для восьми из восемнадцати платформ, где данные\n"
        "    скудны, это важно. Снимок экрана, так же, — это изображение экрана, а\n"
        "    <a href=\"/disclaimer/\">не квалифицированный электронный документ</a>.\n"
        "    Там, где решает содержание, читайте источник."
    ),
    "disclosure": (
        "Раскрытие информации: этот сайт ведёт разработчик Full Page PDF Snap — "
        "расширения, названного на этой странице. <a href=\"/measurements/print-to-pdf-vs-screenshot/\">"
        "Собственная печать в PDF браузера измерена в сравнении с ним</a>, включая "
        "случаи, где печать выигрывает. Исправления: <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "GitHub issues</a> · <a href=\"/disclaimer/\">Отказ от ответственности</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">Инструменты</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">О конечной точке</a> ·\n"
        "  <a href=\"/disclaimer/\">Отказ от ответственности</a>"
    ),
}

# ------------------------------------------------------------------ 中文 -----
TEXTE["zh-CN"] = {
    "crumb": "配方",
    "h1": "配方:把网页来源变成引文",
    "standfirst": (
        "<code>/mcp</code> 引文端点的简短完整用法说明 —— 可在终端、WSL、Python\n"
        "    以及支持 MCP 的 AI 工具中使用。每一条都在 2026 年 8 月 3 日实际运行\n"
        "    过之后才被写下来;未经测试的配方只是空谈。"
    ),
    "meta": (
        "无需账户和密钥 · 请合理使用 ·\n"
        "    <a href=\"/notes/mcp-server-what-it-solves/\">该端点是什么、会拒绝什么</a>"
    ),
    "getback_h3": "你会得到什么",
    "getback_p": (
        "对于是作品的页面:作者、标题、期刊、年份、卷、页码、DOI、ISSN 和许可\n"
        "    —— 外加可直接导入的 <strong>RIS 记录</strong>和 <strong>BibTeX 条目</strong>。\n"
        "    对于付费墙、错误页或机器人检查页:<code>complete: false</code> 和一条\n"
        "    指明是哪堵墙的警告。<strong>在归档结果之前先检查 <code>complete</code></strong>\n"
        "    —— 被拒绝的记录仍带有标题,读起来会像一件作品。"
    ),
    "rl_h2": "阅读清单变成 .ris 文件",
    "rl_p1": (
        "大多数人真正想要的配方。<code>reading-list.txt</code> 中每行一个 URL,\n"
        "  产出一个可导入的文件。无法读取的来源会在 stderr 中列名,并从文件中\n"
        "  剔除,而不是导入一半。"
    ),
    "rl_p2": (
        "然后 <strong>Zotero → 文件 → 导入</strong>,或 <strong>Citavi → 导入 →\n"
        "  RIS</strong>。在三个学术 URL 上实测:三条记录,不到两秒,无需编辑即可导入。"
    ),
    "cc_h2": "Claude Code,一行搞定",
    "cc_p": (
        "<code>claude mcp list</code> 随后会显示 <code>✔ Connected</code>。之后你只需说:\n"
        "  <em>\"为我的参考文献引用这四个链接\"</em> —— 每个链接都会调用该工具,被墙\n"
        "  挡住的会如实报告,而不是凭空编造。"
    ),
    "cd_h2": "Claude Desktop 和其他 MCP 客户端",
    "cd_p": (
        "将 <code>https://provinglab.dev/mcp</code> 添加为<strong>远程 MCP 服务器</strong>\n"
        "  (传输方式:streamable HTTP)。提供身份验证但非必需;匿名请求会得到完全\n"
        "  相同的回答。在只接受本地服务器的客户端中,常用的桥接方式可行:"
    ),
    "py_h2": "Python —— 注意 user agent",
    "py_p": (
        "标准库会自报为 <code>Python-urllib</code>,本站前面的 CDN 会在 worker 看到\n"
        "  请求之前就对其返回 <strong>HTTP 403</strong>。随便设置一个自己的 user\n"
        "  agent 即可。这不是针对自动化的规定 —— 而是一个分不清区别的过滤器。"
    ),
    "wsl_h2": "WSL:从浏览器到终端",
    "wsl_p1": (
        "工作的两半位于文件系统边界的两侧。大学登录墙后面的来源只能在浏览器里\n"
        "  捕获,然后还要能从 shell 里找到这个文件。"
    ),
    "wsl_p2": (
        "在 <a href=\"/tools/full-page-pdf-snap/\">Full Page PDF Snap</a> 中打开\n"
        "  <em>Copy file path after saving</em>,并在设置里把格式设为 <strong>WSL</strong>。\n"
        "  捕获之后,路径会以 Linux shell 能看懂的形式放进剪贴板:"
    ),
    "wsl_p3": (
        "直接粘贴在命令后面,或粘贴到能读取文件的 AI 工具聊天里。同一次捕获的\n"
        "  RIS 记录就以相同的文件名加 <code>.ris</code> 扩展名保存在 PDF 旁边。"
    ),
    "wr_h2": "两条路线,分别适合什么来源",
    "wr_th": ("端点", "扩展"),
    "wr_rows": [
        ("运行位置", "服务器上,匿名", "", "你的浏览器里,已登录", ""),
        ("给你", "参考文献条目", "", "条目<em>和</em>文档", ""),
        ("登录墙之后", "不行", "lose", "可以", "win"),
        ("每个来源的成本", "零,可脚本化", "win", "一次点击", ""),
        ("输出", "RIS + BibTeX", "", "内嵌字段的 PDF,外加 RIS", ""),
    ],
    "wr_p": (
        "所以这种分工不是妥协:<strong>批量走端点,被端点拒绝的走扩展</strong>。\n"
        "  两者输出相同的 RIS 格式,因此无论走哪条路线,所有内容都会进入同一个\n"
        "  Zotero 或 Citavi 库。第一遍的拒绝列表会告诉你哪些来源需要第二条路线。"
    ),
    "ma_h2": "面向代理而非人类",
    "ma_p": (
        "这些配方还以机器可读的 skill 形式发布,与测量方法放在一起:"
    ),
    "ma_items": [
        ("/.well-known/agent-skills/index.json", "agent-skills/index.json",
         "—— 各 skill 及其校验和"),
        ("/.well-known/agent-skills/cite-a-web-source.md", "cite-a-web-source.md",
         "—— 本页面的流程化版本"),
        ("/llms.txt", "llms.txt",
         "—— 本站发布的所有内容,纯文本"),
        ("/.well-known/mcp/server-card.json", "服务器卡片",
         "—— 工具与传输方式"),
    ],
    "proves_h3": "这些都不能证明什么",
    "proves_p": (
        "一条引文记录只能说明页面如何自我声明。它不验证作品是否存在、DOI 是否\n"
        "    解析到它、页面是否诚实 —— 在十八个平台中有八个数据稀薄,这一点很\n"
        "    重要。屏幕截图同样只是屏幕的图像,<a href=\"/disclaimer/\">并非合格的\n"
        "    电子文档</a>。在内容起决定作用的地方,请阅读原文。"
    ),
    "disclosure": (
        "披露:本站由本页提到的扩展 Full Page PDF Snap 的开发者运营。"
        "<a href=\"/measurements/print-to-pdf-vs-screenshot/\">浏览器自带的打印为 PDF "
        "已与之对比测量</a>,包括打印胜出的情形。更正:<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">"
        "GitHub issues</a> · <a href=\"/disclaimer/\">免责声明</a>"
    ),
    "foot": (
        "<a href=\"../\">← Proving Lab</a> · <a href=\"/tools/\">工具</a> ·\n"
        "  <a href=\"/notes/mcp-server-what-it-solves/\">关于该端点</a> ·\n"
        "  <a href=\"/disclaimer/\">免责声明</a>"
    ),
}
