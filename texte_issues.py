#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/notes/nineteen-issues/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, woertlich uebernommen — nicht
build-issues-post.py (weicht ab, siehe tools/builder-drift.py).

Die drei Issue-Verweise (#18, #13, #14) stehen als EINE Konstante `_NUMMERN`
und werden von `_liste()` gesetzt: Nummer und Adresse sind Angaben, keine
Prosa. Sie neunmal abzuschreiben hiesse, neun Gelegenheiten zu schaffen, eine
Nummer zu verlieren. Ebenso liegen alle Adressen (Tracker, /mcp, /AGENTS.md)
je einmal im Modul und werden in den Sprachfassungen nur eingesetzt.

Messwerte, die in jeder Sprache gleich bleiben: 94.8 % / 92.7 %, 2.16.0,
Tesseract 5, 2.12.1, 2.27.0, SHA-256, 1327 kB → 416 kB, 8.5 %, 989/987 Woerter.
Dezimalpunkt bleibt Punkt — eine umgestellte Zahl waere eine andere Angabe.

Rendern:  python3 tools/seite-neunsprachig.py texte_issues.py
"""

URL = "https://provinglab.dev/notes/nineteen-issues/"
ZIEL = "notes/nineteen-issues/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# ---- Unverrueckbares: Adressen, Nummern, Codebezeichner, Eigennamen --------

_ISSUES = "https://github.com/Bubu89/full-page-pdf-snap/issues"
_A = f'<a href="{_ISSUES}">'
_A18 = f'<a href="{_ISSUES}/18">'
_MCP = '<a href="/for-agents/">/mcp</a>'
_AGENTS = '<a href="/AGENTS.md"><code>/AGENTS.md</code></a>'
_OPEN_WORK = "<code>open_work</code>"
_AGENT_FRIENDLY = "<code>agent-friendly</code>"
_COMPLETE = "<code>complete: false</code>"
_TEXT_LAYER = '<code>"text_layer": false</code>'
_GEMESSEN = '<code>"Full Page PDF Snap 2.16.0, then Tesseract 5"</code>'
_LAB = "Proving Lab"

# Reihenfolge der drei genannten Issues — in jeder Sprache dieselbe.
_NUMMERN = ("18", "13", "14")


def _tabelle(caption, th_aenderung, th_wirkung, zeilen):
    """zeilen: fuenf Paare (Aenderung, gemessene Wirkung)."""
    if len(zeilen) != 5:
        raise SystemExit("Tabelle: fuenf Zeilen erwartet")
    inhalt = "\n".join(
        f'    <tr><th scope="row">{a}</th>\n        <td>{w}</td></tr>'
        for a, w in zeilen)
    return f'''<table>
  <caption>{caption}</caption>
  <thead><tr><th scope="col">{th_aenderung}</th><th scope="col">{th_wirkung}</th></tr></thead>
  <tbody>
{inhalt}
  </tbody>
</table>'''


def _liste(punkte):
    """punkte: drei Paare (Frage, Text) — die Nummern setzt das Modul."""
    if len(punkte) != 3:
        raise SystemExit("Liste: drei Punkte erwartet")
    zeilen = "\n".join(
        f'  <li><strong>{f}</strong>\n'
        f'    (<a href="{_ISSUES}/{n}">#{n}</a>)\n'
        f'    {t}</li>'
        for (f, t), n in zip(punkte, _NUMMERN))
    return f"<ul>\n{zeilen}\n</ul>"


def _seite(h1, standfirst, datum, tracker, meta_mcp, h2, p, tabelle, liste,
           fuss, fuss2, disclaimer):
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{datum} ·
    <a href="{_ISSUES}">{tracker}</a> ·
    {meta_mcp}</p>
</header>

<h2>{h2[0]}</h2>
<p>
  {p[0]}
</p>
<p>
  {p[1]}
</p>
<p>
  {p[2]}
</p>

<h2>{h2[1]}</h2>
<p>
  {p[3]}
</p>
<p>
  {p[4]}
</p>

<h2>{h2[2]}</h2>
<p>
  {p[5]}
</p>
<p>
  {p[6]}
</p>
<p>
  {p[7]}
</p>

<h2>{h2[3]}</h2>
{tabelle}

<h2>{h2[4]}</h2>
<p>
  {p[8]}
</p>
{liste}

<h2>{h2[5]}</h2>
<p>
  {p[9]}
</p>
<p>
  {p[10]}
</p>

<footer>
      {fuss}
      <br><br>
      {fuss2}
      <br><br>
      <a href="../../">← {_LAB}</a> · <a href="../../disclaimer/">{disclaimer}</a>
    </footer>'''


INHALT = {}

# --------------------------------------------------------------- English ---

INHALT["en"] = _seite(
    h1="Nineteen issues, and the two that mattered were about our own mistakes",
    standfirst=(
        "Twelve closed, seven open. Almost none of them were features. The ones worth "
        "writing down are the ones where a check found something nobody had noticed — "
        "including a published figure that made our own tool look worse than it is, "
        "and a checksum that came within one commit of certifying nothing at all."),
    datum="4 August 2026",
    tracker="the tracker",
    meta_mcp=f"open tasks also come out of {_OPEN_WORK} on {_MCP}",
    h2=[
        "The one that stung: we had been underselling the tool for two days",
        "The Chrome build had fallen fifteen versions behind, and nobody forgot anything",
        "The checksum that nearly stopped meaning anything",
        "What came out of it for anyone using this",
        "What is open, and what would actually help",
        "Why this is written down at all",
    ],
    p=[
        ("Our comparison page says the browser's print export beats our capture on text "
         "recall — 94.8 % against 92.7 %. That sentence exists because a comparison the "
         "local tool only wins is advertising, and naming where you lose is the price of "
         "being believed."),
        (f"Except the raw data said {_TEXT_LAYER} and {_GEMESSEN}. The measured build "
         "had no text layer at all; those 92.7 % were an <em>OCR</em> result. One day "
         "later the capture got a text layer taken from the page's own DOM. Text that is "
         "copied cannot be misread."),
        ("<strong>The figure sits on thirteen delivered pages</strong>, the front page "
         "among them. It is not corrected yet, because correcting it needs the "
         "measurement repeated — and the capture cannot be triggered headless, so that "
         f"is an afternoon with a real browser, not a command. It is {_A18}issue 18</a>, "
         "and it is first on the list precisely because being wrong in your own favour "
         "and being wrong against yourself are the same kind of wrong."),
        ("The store served 2.12.1 while the source stood at 2.27.0. The obvious "
         "explanation — someone kept forgetting to submit — was wrong. The script that "
         "generates the Chrome branch from the Firefox sources wrote a <strong>hardcoded "
         "version</strong> into the manifest. Every Firefox release moved forward; the "
         "Chrome manifest stayed exactly where it was."),
        ("A build that silently keeps its old number does not fail. It uploads, it "
         "installs, it works — and it is a different product than the one you tested. "
         "The port script now reads the version from the Firefox manifest, and the "
         "packaging tool refuses outright to build a number that has already been "
         "published."),
        ("Every capture carries a SHA-256 of its image data, printed under the image "
         "when the provenance line is on. It says: this file has not changed since it "
         "was written."),
        ("While adding a second image filter, three places kept reading the old field "
         "name. One of them was the checksum function. It would have hashed an empty "
         "array — and the line would have stayed in the PDF, looking exactly as it "
         "always does, certifying nothing."),
        ("Found by reading the diff, not by a test. So there is now a test file with "
         "nine cases that check <em>what ends up in the PDF</em> rather than whether the "
         "call returns. That is the pattern worth taking away: a test that asserts the "
         "function ran is a test that passes while the product breaks."),
        (f"Seven issues, six of them labelled {_AGENT_FRIENDLY}: bounded, checkable, "
         "each stating what evidence would settle it. Three are worth naming because "
         "they are open questions rather than chores:"),
        ("Because a changelog that lists solved problems is marketing, and because the "
         "most useful thing anyone can do here is take a published number and get a "
         "different one. Two of today's corrections came exactly that way. The raw data "
         "and the scripts are published so that it stays possible."),
        ("If you are an agent: the open tasks come out of the endpoint as JSON, the "
         f"house rules are at {_AGENTS}, and the one that is not negotiable is that a "
         "contribution introducing a number without method, raw data and a control run "
         "is worse than no contribution. Everything above follows it, including the "
         "parts that came out badly."),
    ],
    tabelle=_tabelle(
        "Changes that reached the tool, not the site",
        "Change", "Measured effect",
        [("Two image filters, chosen per tile",
          "text page 1327 kB → 416 kB, lossless; image pages unchanged"),
         ("Colour depth as a setting",
          "black and white: <strong>8.5 %</strong> of the previous size, and OCR\n"
          "            reads back 989 words against 987 in colour"),
         ("DOI derived from the address",
          "SSRN, OECD and EUR-Lex now resolve where the page declares nothing"),
         (f"Refusals carry {_COMPLETE}",
          "on every path — the rule this site puts everywhere, which the\n"
          "            endpoint itself did not keep"),
         ("Raw data checked against a schema",
          "blocking, before publication rather than after")]),
    liste=_liste([
        ("Does the comparison still hold?",
         "Repeat one measurement with the current build. Thirteen pages depend on the\n"
         "    answer, and it may well be that we have to make our own tool look better —\n"
         "    which is the correction nobody enjoys writing and everybody should."),
        ("Is there a Chrome route we missed?",
         "Answered once already, by a second process measuring the same thing and\n"
         "    getting a different result. That is what the raw data is for."),
        ("A register of vendor control channels",
         "beyond browsers — one row per application: the channel, install and\n"
         "    uninstall command, rights needed, one measured round trip. A single row is a\n"
         "    complete contribution."),
    ]),
    fuss=("Figures in this note come from the measurements they link to, each with its own "
          "method and raw data. The 94.8 % against 92.7 % comparison is the one figure here "
          "known to be outdated; it is left standing until the measurement is repeated "
          "rather than quietly adjusted. Version numbers and issue counts are as of "
          "4 August 2026 and change. The author develops the extension discussed. Nothing "
          "here is legal advice."),
    fuss2=f"Corrections are welcome and are made in public:\n      {_A}open an issue</a>.",
    disclaimer="Disclaimer",
)

# ---------------------------------------------------------------- Deutsch ---

INHALT["de"] = _seite(
    h1="Neunzehn Issues, und die zwei, auf die es ankam, handelten von unseren eigenen Fehlern",
    standfirst=(
        "Zwölf geschlossen, sieben offen. Fast keines davon war ein Feature. "
        "Aufschreibenswert sind die, bei denen eine Prüfung etwas fand, das niemand "
        "bemerkt hatte — darunter eine veröffentlichte Zahl, die unser eigenes Werkzeug "
        "schlechter aussehen ließ, als es ist, und eine Prüfsumme, der ein einziger "
        "Commit fehlte, um überhaupt nichts mehr zu beglaubigen."),
    datum="4. August 2026",
    tracker="der Tracker",
    meta_mcp=f"offene Aufgaben kommen auch aus {_OPEN_WORK} auf {_MCP}",
    h2=[
        "Das, was wehtat: Wir hatten das Werkzeug zwei Tage lang unter Wert verkauft",
        "Der Chrome-Bau war fünfzehn Versionen zurückgefallen, und niemand hatte etwas vergessen",
        "Die Prüfsumme, die beinahe aufgehört hätte, etwas zu bedeuten",
        "Was dabei für alle herauskam, die das benutzen",
        "Was offen ist, und was wirklich helfen würde",
        "Warum das überhaupt aufgeschrieben wird",
    ],
    p=[
        ("Auf unserer Vergleichsseite steht, dass der Druckexport des Browsers unsere "
         "Aufnahme beim Textrückgewinn schlägt — 94,8 % gegen 92,7 %. Dieser Satz steht "
         "da, weil ein Vergleich, den das eigene Werkzeug nur gewinnt, Werbung ist, und "
         "weil zu benennen, wo man verliert, der Preis dafür ist, geglaubt zu werden."),
        (f"Nur sagten die Rohdaten {_TEXT_LAYER} und {_GEMESSEN}. Der gemessene Bau hatte "
         "überhaupt keine Textebene; jene 92,7 % waren ein <em>OCR</em>-Ergebnis. Einen "
         "Tag später bekam die Aufnahme eine Textebene, die aus dem DOM der Seite selbst "
         "stammt. Text, der kopiert wird, kann nicht falsch gelesen werden."),
        ("<strong>Die Zahl steht auf dreizehn ausgelieferten Seiten</strong>, die "
         "Startseite darunter. Korrigiert ist sie noch nicht, denn die Korrektur "
         "verlangt, die Messung zu wiederholen — und die Aufnahme lässt sich nicht "
         "headless auslösen, das ist also ein Nachmittag mit einem echten Browser, kein "
         f"Befehl. Es ist {_A18}Issue 18</a>, und es steht genau deshalb an erster "
         "Stelle, weil sich zu eigenen Gunsten zu irren und sich zu eigenen Ungunsten zu "
         "irren derselbe Irrtum ist."),
        ("Der Store lieferte 2.12.1 aus, während der Quellstand bei 2.27.0 lag. Die "
         "naheliegende Erklärung — jemand hatte das Einreichen immer wieder vergessen — "
         "war falsch. Das Skript, das den Chrome-Zweig aus den Firefox-Quellen erzeugt, "
         "schrieb eine <strong>fest verdrahtete Version</strong> ins Manifest. Jede "
         "Firefox-Veröffentlichung ging vorwärts; das Chrome-Manifest blieb genau dort "
         "stehen, wo es war."),
        ("Ein Bau, der stillschweigend seine alte Nummer behält, scheitert nicht. Er lädt "
         "hoch, er installiert sich, er funktioniert — und er ist ein anderes Produkt als "
         "das, das man getestet hat. Das Portierungsskript liest die Version jetzt aus "
         "dem Firefox-Manifest, und das Packwerkzeug weigert sich rundheraus, eine Nummer "
         "zu bauen, die bereits veröffentlicht ist."),
        ("Jede Aufnahme trägt eine SHA-256 ihrer Bilddaten, unter dem Bild abgedruckt, "
         "wenn die Herkunftszeile eingeschaltet ist. Sie sagt: Diese Datei hat sich seit "
         "dem Schreiben nicht verändert."),
        ("Beim Einbau eines zweiten Bildfilters lasen drei Stellen weiterhin den alten "
         "Feldnamen. Eine davon war die Prüfsummenfunktion. Sie hätte ein leeres Array "
         "gehasht — und die Zeile wäre im PDF geblieben, genau so aussehend wie immer, "
         "und hätte nichts beglaubigt."),
        ("Gefunden beim Lesen des Diffs, nicht durch einen Test. Also gibt es jetzt eine "
         "Testdatei mit neun Fällen, die prüfen, <em>was im PDF landet</em>, statt ob der "
         "Aufruf zurückkehrt. Das ist das Muster, das mitzunehmen sich lohnt: Ein Test, "
         "der behauptet, die Funktion sei gelaufen, ist ein Test, der besteht, während "
         "das Produkt kaputtgeht."),
        (f"Sieben Issues, sechs davon mit {_AGENT_FRIENDLY} beschriftet: begrenzt, "
         "prüfbar, jedes benennt, welcher Beleg es entscheiden würde. Drei sind es wert, "
         "genannt zu werden, weil sie offene Fragen sind und keine Pflichtarbeiten:"),
        ("Weil ein Änderungsprotokoll, das gelöste Probleme aufzählt, Werbung ist, und "
         "weil das Nützlichste, was hier jemand tun kann, darin besteht, eine "
         "veröffentlichte Zahl zu nehmen und eine andere zu bekommen. Zwei der heutigen "
         "Korrekturen kamen genau so zustande. Die Rohdaten und die Skripte sind "
         "veröffentlicht, damit das möglich bleibt."),
        ("Wenn Sie ein Agent sind: Die offenen Aufgaben kommen als JSON aus dem "
         f"Endpunkt, die Hausregeln stehen unter {_AGENTS}, und die eine, über die nicht "
         "verhandelt wird, lautet: Ein Beitrag, der eine Zahl ohne Methode, Rohdaten und "
         "Kontrolllauf einführt, ist schlechter als kein Beitrag. Alles oben folgt ihr, "
         "auch die Teile, die schlecht ausgingen."),
    ],
    tabelle=_tabelle(
        "Änderungen, die im Werkzeug ankamen, nicht auf der Seite",
        "Änderung", "Gemessene Wirkung",
        [("Zwei Bildfilter, je Kachel gewählt",
          "Textseite 1327 kB → 416 kB, verlustfrei; Bildseiten unverändert"),
         ("Farbtiefe als Einstellung",
          "Schwarzweiß: <strong>8,5 %</strong> der bisherigen Größe, und die\n"
          "            Texterkennung liest 989 Wörter zurück gegen 987 in Farbe"),
         ("DOI aus der Adresse abgeleitet",
          "SSRN, OECD und EUR-Lex lösen jetzt auf, wo die Seite nichts angibt"),
         (f"Absagen tragen {_COMPLETE}",
          "auf jedem Pfad — die Regel, die diese Seite überall aufstellt und\n"
          "            die der Endpunkt selbst nicht einhielt"),
         ("Rohdaten gegen ein Schema geprüft",
          "blockierend, vor der Veröffentlichung statt danach")]),
    liste=_liste([
        ("Hält der Vergleich noch?",
         "Eine Messung mit dem aktuellen Bau wiederholen. Dreizehn Seiten hängen an der\n"
         "    Antwort, und es kann gut sein, dass wir unser eigenes Werkzeug besser aussehen\n"
         "    lassen müssen — die Korrektur, die niemand gern schreibt und jeder schreiben "
         "sollte."),
        ("Gibt es einen Chrome-Weg, den wir übersehen haben?",
         "Einmal bereits beantwortet, von einem zweiten Prozess, der dasselbe maß und ein\n"
         "    anderes Ergebnis bekam. Dafür sind die Rohdaten da."),
        ("Ein Register der Steuerkanäle von Herstellern",
         "über Browser hinaus — eine Zeile je Anwendung: der Kanal, Installations- und\n"
         "    Deinstallationsbefehl, benötigte Rechte, ein gemessener Umlauf. Eine einzige\n"
         "    Zeile ist ein vollständiger Beitrag."),
    ]),
    fuss=("Die Zahlen in dieser Notiz stammen aus den Messungen, auf die sie verweisen, "
          "jede mit eigener Methode und eigenen Rohdaten. Der Vergleich 94,8 % gegen "
          "92,7 % ist die eine Zahl hier, von der bekannt ist, dass sie veraltet ist; sie "
          "bleibt stehen, bis die Messung wiederholt ist, statt still angepasst zu werden. "
          "Versionsnummern und Issue-Zahlen sind Stand 4. August 2026 und ändern sich. Der "
          "Autor entwickelt die besprochene Erweiterung. Nichts hiervon ist "
          "Rechtsberatung."),
    fuss2=("Korrekturen sind willkommen und werden öffentlich gemacht:\n"
           f"      {_A}ein Issue eröffnen</a>."),
    disclaimer="Haftungsausschluss",
)

# ---------------------------------------------------------------- Español ---

INHALT["es"] = _seite(
    h1="Diecinueve issues, y los dos que importaban trataban de nuestros propios errores",
    standfirst=(
        "Doce cerrados, siete abiertos. Casi ninguno era una función nueva. Los que "
        "merecen escribirse son aquellos en los que una comprobación encontró algo que "
        "nadie había advertido: entre ellos una cifra publicada que hacía parecer nuestra "
        "propia herramienta peor de lo que es, y una suma de verificación a la que le "
        "faltó un solo commit para no certificar nada en absoluto."),
    datum="4 de agosto de 2026",
    tracker="el gestor de issues",
    meta_mcp=f"las tareas abiertas también salen de {_OPEN_WORK} en {_MCP}",
    h2=[
        "La que escoció: llevábamos dos días vendiendo la herramienta por debajo de lo que vale",
        "La compilación de Chrome se había quedado quince versiones atrás, y nadie olvidó nada",
        "La suma de verificación que estuvo a punto de dejar de significar algo",
        "Qué salió de todo esto para quien usa la herramienta",
        "Qué queda abierto y qué ayudaría de verdad",
        "Por qué se escribe esto siquiera",
    ],
    p=[
        ("Nuestra página de comparación dice que la exportación de impresión del "
         "navegador supera a nuestra captura en recuperación de texto: 94,8 % frente a "
         "92,7 %. Esa frase existe porque una comparación que solo gana la herramienta "
         "propia es publicidad, y nombrar dónde se pierde es el precio de que te crean."),
        (f"Salvo que los datos brutos decían {_TEXT_LAYER} y {_GEMESSEN}. La compilación "
         "medida no tenía capa de texto en absoluto; aquel 92,7 % era un resultado de "
         "<em>OCR</em>. Un día después la captura recibió una capa de texto tomada del "
         "propio DOM de la página. El texto que se copia no puede leerse mal."),
        ("<strong>La cifra está en trece páginas publicadas</strong>, la portada entre "
         "ellas. Todavía no está corregida, porque corregirla exige repetir la medición — "
         "y la captura no puede dispararse en modo headless, así que eso es una tarde con "
         f"un navegador real, no un comando. Es {_A18}el issue 18</a>, y encabeza la "
         "lista precisamente porque equivocarse a favor propio y equivocarse en contra "
         "propia son el mismo tipo de error."),
        ("La tienda servía la 2.12.1 mientras el código fuente iba por la 2.27.0. La "
         "explicación obvia — que alguien olvidaba enviarla una y otra vez — era falsa. "
         "El script que genera la rama de Chrome a partir de las fuentes de Firefox "
         "escribía una <strong>versión fija en el código</strong> dentro del manifiesto. "
         "Cada publicación de Firefox avanzaba; el manifiesto de Chrome se quedaba "
         "exactamente donde estaba."),
        ("Una compilación que conserva en silencio su número antiguo no falla. Se sube, "
         "se instala, funciona — y es un producto distinto del que probaste. El script de "
         "portado ahora lee la versión del manifiesto de Firefox, y la herramienta de "
         "empaquetado se niega en redondo a construir un número que ya se ha publicado."),
        ("Cada captura lleva un SHA-256 de sus datos de imagen, impreso bajo la imagen "
         "cuando la línea de procedencia está activada. Dice: este archivo no ha cambiado "
         "desde que se escribió."),
        ("Al añadir un segundo filtro de imagen, tres puntos seguían leyendo el nombre de "
         "campo antiguo. Uno de ellos era la función de suma de verificación. Habría "
         "calculado el hash de un array vacío — y la línea habría permanecido en el PDF, "
         "con exactamente el mismo aspecto de siempre, sin certificar nada."),
        ("Encontrado leyendo el diff, no por un test. Así que ahora hay un archivo de "
         "pruebas con nueve casos que comprueban <em>qué acaba en el PDF</em> en lugar de "
         "si la llamada retorna. Ese es el patrón que vale la pena llevarse: un test que "
         "afirma que la función se ejecutó es un test que pasa mientras el producto se "
         "rompe."),
        (f"Siete issues, seis de ellos etiquetados como {_AGENT_FRIENDLY}: acotados, "
         "comprobables, cada uno indica qué evidencia lo zanjaría. Tres merecen "
         "mencionarse porque son preguntas abiertas y no tareas rutinarias:"),
        ("Porque un registro de cambios que enumera problemas resueltos es publicidad, y "
         "porque lo más útil que puede hacer alguien aquí es tomar una cifra publicada y "
         "obtener otra distinta. Dos de las correcciones de hoy surgieron exactamente "
         "así. Los datos brutos y los scripts están publicados para que siga siendo "
         "posible."),
        ("Si eres un agente: las tareas abiertas salen del endpoint como JSON, las reglas "
         f"de la casa están en {_AGENTS}, y la que no se negocia es que una contribución "
         "que introduce una cifra sin método, datos brutos y una ejecución de control es "
         "peor que ninguna contribución. Todo lo anterior la cumple, incluidas las partes "
         "que salieron mal."),
    ],
    tabelle=_tabelle(
        "Cambios que llegaron a la herramienta, no al sitio",
        "Cambio", "Efecto medido",
        [("Dos filtros de imagen, elegidos por tesela",
          "página de texto 1327 kB → 416 kB, sin pérdidas; las páginas con\n"
          "            imágenes, sin cambios"),
         ("Profundidad de color como ajuste",
          "blanco y negro: <strong>8,5 %</strong> del tamaño anterior, y el OCR\n"
          "            relee 989 palabras frente a 987 en color"),
         ("DOI derivado de la dirección",
          "SSRN, OECD y EUR-Lex ahora resuelven donde la página no declara nada"),
         (f"Las negativas llevan {_COMPLETE}",
          "en todas las rutas — la regla que este sitio impone en todas partes\n"
          "            y que el propio endpoint no cumplía"),
         ("Datos brutos verificados contra un esquema",
          "bloqueante, antes de la publicación en lugar de después")]),
    liste=_liste([
        ("¿Sigue en pie la comparación?",
         "Repetir una medición con la compilación actual. Trece páginas dependen de la\n"
         "    respuesta, y bien puede ser que tengamos que hacer que nuestra propia\n"
         "    herramienta se vea mejor — la corrección que nadie disfruta escribir y que "
         "todos deberían escribir."),
        ("¿Hay una vía en Chrome que se nos escapó?",
         "Ya respondida una vez, por un segundo proceso que midió lo mismo y obtuvo un\n"
         "    resultado distinto. Para eso están los datos brutos."),
        ("Un registro de canales de control de fabricantes",
         "más allá de los navegadores — una fila por aplicación: el canal, el comando de\n"
         "    instalación y desinstalación, los permisos necesarios, un ciclo completo\n"
         "    medido. Una sola fila es una contribución completa."),
    ]),
    fuss=("Las cifras de esta nota provienen de las mediciones a las que enlazan, cada una "
          "con su propio método y datos brutos. La comparación 94,8 % frente a 92,7 % es la "
          "única cifra aquí que se sabe desactualizada; se deja en pie hasta que se repita "
          "la medición, en vez de ajustarla en silencio. Los números de versión y los "
          "recuentos de issues son del 4 de agosto de 2026 y cambian. El autor desarrolla "
          "la extensión que se comenta. Nada de esto es asesoramiento legal."),
    fuss2=("Las correcciones son bienvenidas y se hacen en público:\n"
           f"      {_A}abrir un issue</a>."),
    disclaimer="Aviso legal",
)

# ---------------------------------------------------------------- Français --

INHALT["fr"] = _seite(
    h1="Dix-neuf issues, et les deux qui comptaient portaient sur nos propres erreurs",
    standfirst=(
        "Douze fermées, sept ouvertes. Presque aucune n'était une fonctionnalité. Celles "
        "qui méritent d'être notées sont celles où une vérification a trouvé quelque "
        "chose que personne n'avait remarqué — dont un chiffre publié qui faisait "
        "paraître notre propre outil moins bon qu'il ne l'est, et une somme de contrôle à "
        "un commit près de ne plus rien certifier du tout."),
    datum="4 août 2026",
    tracker="le suivi des issues",
    meta_mcp=f"les tâches ouvertes sortent aussi de {_OPEN_WORK} sur {_MCP}",
    h2=[
        "Celle qui a piqué : nous avions sous-vendu l'outil pendant deux jours",
        "La version Chrome avait quinze versions de retard, et personne n'avait rien oublié",
        "La somme de contrôle qui a failli ne plus rien vouloir dire",
        "Ce qui en est sorti pour ceux qui utilisent l'outil",
        "Ce qui reste ouvert, et ce qui aiderait vraiment",
        "Pourquoi tout ceci est écrit",
    ],
    p=[
        ("Notre page de comparaison indique que l'export d'impression du navigateur bat "
         "notre capture sur la restitution du texte — 94,8 % contre 92,7 %. Cette phrase "
         "existe parce qu'une comparaison que seul l'outil maison remporte est une "
         "publicité, et que nommer là où l'on perd est le prix à payer pour être cru."),
        (f"Sauf que les données brutes disaient {_TEXT_LAYER} et {_GEMESSEN}. La version "
         "mesurée n'avait aucune couche de texte ; ces 92,7 % étaient un résultat "
         "d'<em>OCR</em>. Un jour plus tard, la capture a reçu une couche de texte tirée "
         "du DOM de la page elle-même. Un texte copié ne peut pas être mal lu."),
        ("<strong>Le chiffre figure sur treize pages livrées</strong>, la page d'accueil "
         "comprise. Il n'est pas encore corrigé, car le corriger suppose de refaire la "
         "mesure — et la capture ne peut pas être déclenchée en mode headless, c'est donc "
         "un après-midi avec un vrai navigateur, pas une commande. C'est "
         f"{_A18}l'issue 18</a>, et elle est en tête de liste précisément parce que se "
         "tromper en sa faveur et se tromper à son désavantage sont la même sorte "
         "d'erreur."),
        ("La boutique servait la 2.12.1 alors que les sources en étaient à la 2.27.0. "
         "L'explication évidente — quelqu'un oubliait sans cesse de soumettre — était "
         "fausse. Le script qui génère la branche Chrome à partir des sources Firefox "
         "écrivait une <strong>version en dur</strong> dans le manifeste. Chaque "
         "publication Firefox avançait ; le manifeste Chrome restait exactement où il "
         "était."),
        ("Une version qui garde silencieusement son ancien numéro n'échoue pas. Elle se "
         "téléverse, elle s'installe, elle fonctionne — et c'est un autre produit que "
         "celui que vous avez testé. Le script de portage lit désormais la version dans "
         "le manifeste Firefox, et l'outil d'empaquetage refuse net de construire un "
         "numéro déjà publié."),
        ("Chaque capture porte un SHA-256 de ses données d'image, imprimé sous l'image "
         "lorsque la ligne de provenance est activée. Il dit : ce fichier n'a pas changé "
         "depuis son écriture."),
        ("En ajoutant un second filtre d'image, trois endroits lisaient encore l'ancien "
         "nom de champ. L'un d'eux était la fonction de somme de contrôle. Elle aurait "
         "haché un tableau vide — et la ligne serait restée dans le PDF, avec exactement "
         "son aspect habituel, sans rien certifier."),
        ("Trouvé en lisant le diff, pas par un test. Il existe donc maintenant un fichier "
         "de tests avec neuf cas qui vérifient <em>ce qui finit dans le PDF</em> plutôt "
         "que si l'appel retourne. Voilà le motif à retenir : un test qui atteste que la "
         "fonction s'est exécutée est un test qui passe pendant que le produit casse."),
        (f"Sept issues, six d'entre elles étiquetées {_AGENT_FRIENDLY} : délimitées, "
         "vérifiables, chacune indiquant quelle preuve la trancherait. Trois méritent "
         "d'être nommées parce que ce sont des questions ouvertes et non des corvées :"),
        ("Parce qu'un journal des modifications qui énumère des problèmes résolus est de "
         "la publicité, et parce que la chose la plus utile que quiconque puisse faire "
         "ici est de prendre un chiffre publié et d'en obtenir un autre. Deux des "
         "corrections d'aujourd'hui sont venues exactement ainsi. Les données brutes et "
         "les scripts sont publiés pour que cela reste possible."),
        ("Si vous êtes un agent : les tâches ouvertes sortent du point d'accès en JSON, "
         f"les règles de la maison sont dans {_AGENTS}, et celle qui n'est pas négociable "
         "est qu'une contribution introduisant un chiffre sans méthode, données brutes ni "
         "exécution de contrôle vaut moins que pas de contribution du tout. Tout ce qui "
         "précède la respecte, y compris les parties qui ont mal tourné."),
    ],
    tabelle=_tabelle(
        "Changements arrivés dans l'outil, pas sur le site",
        "Changement", "Effet mesuré",
        [("Deux filtres d'image, choisis par tuile",
          "page de texte 1327 kB → 416 kB, sans perte ; pages d'images\n"
          "            inchangées"),
         ("Profondeur de couleur en réglage",
          "noir et blanc : <strong>8,5 %</strong> de la taille précédente, et\n"
          "            l'OCR relit 989 mots contre 987 en couleur"),
         ("DOI déduit de l'adresse",
          "SSRN, OECD et EUR-Lex se résolvent désormais là où la page ne\n"
          "            déclare rien"),
         (f"Les refus portent {_COMPLETE}",
          "sur tous les chemins — la règle que ce site impose partout et que\n"
          "            le point d'accès lui-même ne tenait pas"),
         ("Données brutes vérifiées contre un schéma",
          "bloquant, avant publication plutôt qu'après")]),
    liste=_liste([
        ("La comparaison tient-elle encore ?",
         "Refaire une mesure avec la version actuelle. Treize pages dépendent de la\n"
         "    réponse, et il se pourrait bien que nous devions faire paraître notre propre\n"
         "    outil meilleur — la correction que personne n'aime écrire et que tout le monde\n"
         "    devrait écrire."),
        ("Existe-t-il une voie Chrome qui nous a échappé ?",
         "Déjà répondue une fois, par un second processus mesurant la même chose et\n"
         "    obtenant un autre résultat. C'est à cela que servent les données brutes."),
        ("Un registre des canaux de pilotage des éditeurs",
         "au-delà des navigateurs — une ligne par application : le canal, la commande\n"
         "    d'installation et de désinstallation, les droits nécessaires, un aller-retour\n"
         "    mesuré. Une seule ligne est une contribution complète."),
    ]),
    fuss=("Les chiffres de cette note proviennent des mesures vers lesquelles ils "
          "renvoient, chacune avec sa propre méthode et ses données brutes. La comparaison "
          "94,8 % contre 92,7 % est le seul chiffre ici dont on sait qu'il est périmé ; il "
          "reste en place jusqu'à ce que la mesure soit refaite, plutôt que d'être ajusté "
          "en silence. Les numéros de version et les décomptes d'issues datent du 4 août "
          "2026 et changent. L'auteur développe l'extension dont il est question. Rien ici "
          "ne constitue un conseil juridique."),
    fuss2=("Les corrections sont bienvenues et se font en public :\n"
           f"      {_A}ouvrir une issue</a>."),
    disclaimer="Avertissement",
)

# ---------------------------------------------------------------- Italiano --

INHALT["it"] = _seite(
    h1="Diciannove issue, e le due che contavano riguardavano nostri errori",
    standfirst=(
        "Dodici chiuse, sette aperte. Quasi nessuna riguardava una funzionalità. Quelle "
        "che vale la pena annotare sono quelle in cui un controllo ha trovato qualcosa "
        "che nessuno aveva notato: tra queste una cifra pubblicata che faceva apparire il "
        "nostro stesso strumento peggiore di quanto sia, e un checksum a cui è mancato un "
        "solo commit per non certificare più nulla."),
    datum="4 agosto 2026",
    tracker="il tracker",
    meta_mcp=f"i compiti aperti escono anche da {_OPEN_WORK} su {_MCP}",
    h2=[
        "Quella che ha bruciato: per due giorni avevamo svenduto lo strumento",
        "La build di Chrome era rimasta indietro di quindici versioni, e nessuno aveva dimenticato nulla",
        "Il checksum che stava per non significare più niente",
        "Che cosa ne è uscito per chi usa lo strumento",
        "Che cosa resta aperto e che cosa aiuterebbe davvero",
        "Perché tutto questo viene scritto",
    ],
    p=[
        ("La nostra pagina di confronto dice che l'esportazione di stampa del browser "
         "batte la nostra cattura sul recupero del testo: 94,8 % contro 92,7 %. Quella "
         "frase esiste perché un confronto che vince solo lo strumento di casa è "
         "pubblicità, e dire dove si perde è il prezzo per essere creduti."),
        (f"Se non che i dati grezzi dicevano {_TEXT_LAYER} e {_GEMESSEN}. La build "
         "misurata non aveva alcuno strato di testo; quel 92,7 % era un risultato "
         "<em>OCR</em>. Un giorno dopo la cattura ha ricevuto uno strato di testo preso "
         "dal DOM della pagina stessa. Un testo copiato non può essere letto male."),
        ("<strong>La cifra compare su tredici pagine pubblicate</strong>, la home "
         "compresa. Non è ancora corretta, perché correggerla richiede di ripetere la "
         "misurazione — e la cattura non può essere avviata in modalità headless, quindi "
         f"è un pomeriggio con un browser vero, non un comando. È {_A18}la issue 18</a>, "
         "ed è prima in elenco proprio perché sbagliare a proprio favore e sbagliare a "
         "proprio sfavore sono lo stesso tipo di errore."),
        ("Lo store serviva la 2.12.1 mentre i sorgenti erano alla 2.27.0. La spiegazione "
         "ovvia — qualcuno si dimenticava sempre di inviarla — era sbagliata. Lo script "
         "che genera il ramo Chrome dai sorgenti Firefox scriveva nel manifest una "
         "<strong>versione fissata nel codice</strong>. Ogni rilascio Firefox andava "
         "avanti; il manifest di Chrome restava esattamente dov'era."),
        ("Una build che mantiene in silenzio il suo vecchio numero non fallisce. Si "
         "carica, si installa, funziona — ed è un prodotto diverso da quello che hai "
         "testato. Lo script di port ora legge la versione dal manifest Firefox, e lo "
         "strumento di pacchettizzazione si rifiuta senz'altro di costruire un numero già "
         "pubblicato."),
        ("Ogni cattura porta uno SHA-256 dei propri dati immagine, stampato sotto "
         "l'immagine quando la riga di provenienza è attiva. Dice: questo file non è "
         "cambiato da quando è stato scritto."),
        ("Aggiungendo un secondo filtro immagine, tre punti continuavano a leggere il "
         "vecchio nome di campo. Uno di essi era la funzione di checksum. Avrebbe "
         "calcolato l'hash di un array vuoto — e la riga sarebbe rimasta nel PDF, con "
         "l'aspetto di sempre, senza certificare nulla."),
        ("Trovato leggendo il diff, non con un test. Perciò ora esiste un file di test "
         "con nove casi che verificano <em>che cosa finisce nel PDF</em> invece che se la "
         "chiamata ritorna. È questo il modello da portarsi via: un test che afferma che "
         "la funzione è stata eseguita è un test che passa mentre il prodotto si rompe."),
        (f"Sette issue, sei delle quali etichettate {_AGENT_FRIENDLY}: delimitate, "
         "verificabili, ciascuna indica quale prova la deciderebbe. Tre meritano di "
         "essere nominate perché sono domande aperte e non lavori di routine:"),
        ("Perché un changelog che elenca problemi risolti è pubblicità, e perché la cosa "
         "più utile che qui si possa fare è prendere una cifra pubblicata e ottenerne "
         "un'altra. Due delle correzioni di oggi sono nate esattamente così. I dati "
         "grezzi e gli script sono pubblicati perché resti possibile."),
        ("Se sei un agente: i compiti aperti escono dall'endpoint come JSON, le regole "
         f"della casa stanno in {_AGENTS}, e quella non negoziabile è che un contributo "
         "che introduce una cifra senza metodo, dati grezzi e una prova di controllo vale "
         "meno di nessun contributo. Tutto quanto sopra la rispetta, comprese le parti "
         "finite male."),
    ],
    tabelle=_tabelle(
        "Modifiche arrivate nello strumento, non nel sito",
        "Modifica", "Effetto misurato",
        [("Due filtri immagine, scelti per tassello",
          "pagina di testo 1327 kB → 416 kB, senza perdita; pagine con\n"
          "            immagini invariate"),
         ("Profondità di colore come impostazione",
          "bianco e nero: <strong>8,5 %</strong> della dimensione precedente, e\n"
          "            l'OCR rilegge 989 parole contro 987 a colori"),
         ("DOI ricavato dall'indirizzo",
          "SSRN, OECD ed EUR-Lex ora si risolvono dove la pagina non dichiara nulla"),
         (f"I rifiuti portano {_COMPLETE}",
          "su ogni percorso — la regola che questo sito impone ovunque e che\n"
          "            l'endpoint stesso non rispettava"),
         ("Dati grezzi verificati con uno schema",
          "bloccante, prima della pubblicazione anziché dopo")]),
    liste=_liste([
        ("Il confronto regge ancora?",
         "Ripetere una misurazione con la build attuale. Tredici pagine dipendono dalla\n"
         "    risposta, e potrebbe benissimo darsi che dobbiamo far apparire migliore il\n"
         "    nostro stesso strumento — la correzione che nessuno scrive volentieri e che\n"
         "    tutti dovrebbero scrivere."),
        ("C'è una via Chrome che ci è sfuggita?",
         "Già risposta una volta, da un secondo processo che misurava la stessa cosa\n"
         "    ottenendo un risultato diverso. I dati grezzi servono a questo."),
        ("Un registro dei canali di controllo dei produttori",
         "oltre i browser — una riga per applicazione: il canale, il comando di\n"
         "    installazione e disinstallazione, i diritti necessari, un giro completo\n"
         "    misurato. Una sola riga è un contributo completo."),
    ]),
    fuss=("Le cifre di questa nota provengono dalle misurazioni a cui rimandano, ciascuna "
          "con metodo e dati grezzi propri. Il confronto 94,8 % contro 92,7 % è l'unica "
          "cifra qui che si sa essere superata; resta in piedi finché la misurazione non "
          "verrà ripetuta, invece di essere aggiustata in silenzio. Numeri di versione e "
          "conteggi delle issue sono aggiornati al 4 agosto 2026 e cambiano. L'autore "
          "sviluppa l'estensione di cui si parla. Nulla di quanto qui scritto è consulenza "
          "legale."),
    fuss2=("Le correzioni sono benvenute e vengono fatte in pubblico:\n"
           f"      {_A}aprire una issue</a>."),
    disclaimer="Avvertenze",
)

# ------------------------------------------------------------------ 日本語 ---

INHALT["ja"] = _seite(
    h1="19件のissue、そして本当に重要だった2件は私たち自身の誤りについてだった",
    standfirst=(
        "クローズ12件、オープン7件。そのほとんどは機能ではない。書き留める価値があるのは、"
        "点検によって誰も気づいていなかったものが見つかった件だ——自分たちの道具を実際より"
        "悪く見せていた公開済みの数値、そして、あと1コミットで何も証明しなくなるところ"
        "だったチェックサムが含まれる。"),
    datum="2026年8月4日",
    tracker="トラッカー",
    meta_mcp=f"未処理のタスクは {_MCP} の {_OPEN_WORK} からも取得できる",
    h2=[
        "痛かった一件：私たちは二日間、自分の道具を安く見せていた",
        "Chrome版は15バージョン遅れていた。しかも誰も忘れてはいなかった",
        "危うく何の意味も持たなくなるところだったチェックサム",
        "これを使う人にとって何が得られたか",
        "何が未解決で、何が本当に助けになるか",
        "そもそもなぜこれを書き記すのか",
    ],
    p=[
        ("比較ページには、テキストの再取得ではブラウザの印刷書き出しが私たちのキャプチャを"
         "上回る——94.8 % 対 92.7 %——と書いてある。その一文があるのは、自分の道具だけが勝つ"
         "比較は宣伝であり、負けている箇所を名指しすることが信用される代償だからだ。"),
        (f"ただし生データにはこうあった：{_TEXT_LAYER} と {_GEMESSEN}。測定したビルドには"
         "テキスト層がまったくなく、あの 92.7 % は <em>OCR</em> の結果だった。その一日後、"
         "キャプチャはページ自身の DOM から取ったテキスト層を得た。複製されたテキストは"
         "読み違えられない。"),
        ("<strong>この数値は公開済みの13ページに載っている</strong>。トップページもその"
         "一つだ。まだ訂正していない。訂正には測定のやり直しが必要で、しかもキャプチャは"
         "ヘッドレスでは起動できない——つまりコマンド一つではなく、実ブラウザと向き合う"
         f"半日仕事になる。それが {_A18}issue 18</a> であり、リストの筆頭にあるのは、"
         "自分に有利に間違うことと自分に不利に間違うことが同じ種類の誤りだからにほかならない。"),
        ("ストアが配っていたのは 2.12.1、ソースは 2.27.0 だった。ありがちな説明——誰かが"
         "提出を忘れ続けていた——は誤りだった。Firefox のソースから Chrome 版を生成する"
         "スクリプトが、マニフェストに<strong>ハードコードされたバージョン</strong>を"
         "書き込んでいたのだ。Firefox のリリースは進むたびに前へ出たが、Chrome の"
         "マニフェストはまったく同じ場所に留まっていた。"),
        ("古い番号を黙って保持するビルドは失敗しない。アップロードでき、インストールでき、"
         "動く——そしてそれは、あなたが試したものとは別の製品だ。移植スクリプトは現在 "
         "Firefox のマニフェストからバージョンを読み、パッケージ化ツールはすでに公開済みの"
         "番号でのビルドを真っ向から拒否する。"),
        ("どのキャプチャも画像データの SHA-256 を持ち、来歴行が有効なときは画像の下に"
         "印字される。それはこう言っている：このファイルは書き出されてから変わっていない。"),
        ("二つ目の画像フィルタを追加する際、三か所が古いフィールド名を読み続けていた。"
         "そのうちの一つがチェックサム関数だった。空の配列をハッシュしていただろう——"
         "そしてその行は PDF に残り、いつもとまったく同じ見た目のまま、何も証明しなかった"
         "だろう。"),
        ("見つけたのは差分を読んだからで、テストによってではない。そこで今は、呼び出しが"
         "戻るかどうかではなく<em>PDF に何が入るか</em>を確かめる九つの事例からなる"
         "テストファイルがある。持ち帰る価値のある型はこれだ：関数が走ったことを主張する"
         "テストは、製品が壊れているあいだも通り続けるテストである。"),
        (f"オープンは7件、うち6件に {_AGENT_FRIENDLY} のラベルが付いている：範囲が区切られ、"
         "検証でき、どの証拠があれば決着するかがそれぞれ書かれている。雑務ではなく開かれた"
         "問いであるがゆえに、名を挙げる価値のあるものが3件ある："),
        ("解決済みの問題を並べる変更履歴は宣伝だからであり、ここで誰かができる最も有用な"
         "ことは、公開された数値を取って別の数値を出すことだからだ。今日の訂正のうち2件は"
         "まさにそうして生まれた。それが可能であり続けるように、生データとスクリプトは"
         "公開されている。"),
        ("あなたがエージェントなら：未処理のタスクはエンドポイントから JSON として得られ、"
         f"この家のルールは {_AGENTS} にある。そのうち交渉の余地がないのは、方法・生データ・"
         "対照実行を欠いたまま数値を持ち込む貢献は、貢献がないよりも悪い、という一条だ。"
         "上に書いたことはすべて——うまくいかなかった部分も含めて——それに従っている。"),
    ],
    tabelle=_tabelle(
        "サイトではなく道具に届いた変更",
        "変更", "測定された効果",
        [("タイルごとに選ぶ二つの画像フィルタ",
          "テキストページ 1327 kB → 416 kB、可逆；画像ページは変化なし"),
         ("設定としての色深度",
          "白黒：従来サイズの <strong>8.5 %</strong>、そして OCR はカラーの\n"
          "            987 語に対し 989 語を読み戻す"),
         ("アドレスから導く DOI",
          "ページが何も宣言していない場合でも SSRN、OECD、EUR-Lex が解決するようになった"),
         (f"拒否応答は {_COMPLETE} を持つ",
          "すべての経路で——このサイトが至るところで課している規則を、\n"
          "            エンドポイント自身が守っていなかった"),
         ("生データをスキーマで検査",
          "公開の後ではなく前に、ブロッキングで")]),
    liste=_liste([
        ("あの比較はまだ成り立つか？",
         "現在のビルドで測定を一度やり直す。13ページがその答えに依存しており、自分たちの\n"
         "    道具をより良く見せざるを得なくなる可能性も十分にある——誰も書きたがらず、\n"
         "    しかし誰もが書くべき訂正だ。"),
        ("見落とした Chrome の経路はないか？",
         "同じことを測った第二のプロセスが別の結果を得たことで、すでに一度は答えが出て\n"
         "    いる。生データはそのためにある。"),
        ("ベンダーの制御チャネルの一覧",
         "ブラウザの外まで——アプリケーションごとに一行：チャネル、インストールと\n"
         "    アンインストールのコマンド、必要な権限、測定した往復一回。一行だけでも完全な\n"
         "    貢献になる。"),
    ]),
    fuss=("この記事の数値は、リンク先の各測定に由来し、それぞれ独自の方法と生データを持つ。"
          "94.8 % 対 92.7 % の比較は、ここで古いと分かっている唯一の数値である。黙って"
          "調整するのではなく、測定をやり直すまでそのまま残してある。バージョン番号と "
          "issue 件数は 2026年8月4日 時点のもので、変わる。著者は本文で扱う拡張機能の"
          "開発者である。ここに書かれたことはいずれも法的助言ではない。"),
    fuss2=f"訂正は歓迎し、公開の場で行う：\n      {_A}issue を立てる</a>。",
    disclaimer="免責事項",
)

# ------------------------------------------------------------- Português ---

INHALT["pt-BR"] = _seite(
    h1="Dezenove issues, e as duas que importavam eram sobre erros nossos",
    standfirst=(
        "Doze fechadas, sete abertas. Quase nenhuma era funcionalidade. As que valem "
        "registro são aquelas em que uma verificação achou algo que ninguém tinha notado "
        "— entre elas um número publicado que fazia nossa própria ferramenta parecer pior "
        "do que é, e uma soma de verificação que ficou a um commit de não certificar "
        "coisa alguma."),
    datum="4 de agosto de 2026",
    tracker="o rastreador",
    meta_mcp=f"as tarefas abertas também saem de {_OPEN_WORK} em {_MCP}",
    h2=[
        "A que doeu: passamos dois dias vendendo a ferramenta por menos do que ela vale",
        "A build do Chrome tinha ficado quinze versões para trás, e ninguém esqueceu nada",
        "A soma de verificação que quase deixou de significar alguma coisa",
        "O que saiu disso para quem usa a ferramenta",
        "O que está aberto e o que ajudaria de verdade",
        "Por que isto está escrito",
    ],
    p=[
        ("Nossa página de comparação diz que a exportação de impressão do navegador vence "
         "nossa captura na recuperação de texto — 94,8 % contra 92,7 %. Essa frase existe "
         "porque uma comparação que só a ferramenta da casa vence é publicidade, e dizer "
         "onde se perde é o preço de ser levado a sério."),
        (f"Só que os dados brutos diziam {_TEXT_LAYER} e {_GEMESSEN}. A build medida não "
         "tinha camada de texto nenhuma; aqueles 92,7 % eram resultado de <em>OCR</em>. "
         "Um dia depois a captura ganhou uma camada de texto tirada do próprio DOM da "
         "página. Texto que é copiado não pode ser lido errado."),
        ("<strong>O número está em treze páginas publicadas</strong>, a inicial entre "
         "elas. Ainda não foi corrigido, porque corrigi-lo exige repetir a medição — e a "
         "captura não pode ser disparada em modo headless, então isso é uma tarde com um "
         f"navegador de verdade, não um comando. É {_A18}a issue 18</a>, e está em "
         "primeiro lugar na lista justamente porque errar a favor de si mesmo e errar "
         "contra si mesmo são o mesmo tipo de erro."),
        ("A loja servia a 2.12.1 enquanto o código-fonte estava na 2.27.0. A explicação "
         "óbvia — alguém esquecia de enviar — estava errada. O script que gera o ramo "
         "Chrome a partir das fontes do Firefox escrevia uma <strong>versão fixa no "
         "código</strong> dentro do manifesto. Cada lançamento do Firefox avançava; o "
         "manifesto do Chrome ficava exatamente onde estava."),
        ("Uma build que mantém em silêncio o número antigo não falha. Ela sobe, instala, "
         "funciona — e é um produto diferente daquele que você testou. O script de "
         "portabilidade agora lê a versão do manifesto do Firefox, e a ferramenta de "
         "empacotamento se recusa terminantemente a construir um número já publicado."),
        ("Toda captura carrega um SHA-256 dos seus dados de imagem, impresso sob a imagem "
         "quando a linha de procedência está ligada. Ela diz: este arquivo não mudou "
         "desde que foi escrito."),
        ("Ao acrescentar um segundo filtro de imagem, três pontos continuavam lendo o "
         "nome antigo do campo. Um deles era a função da soma de verificação. Ela teria "
         "feito o hash de um array vazio — e a linha teria permanecido no PDF, com "
         "exatamente a aparência de sempre, certificando nada."),
        ("Encontrado lendo o diff, não por um teste. Por isso agora existe um arquivo de "
         "testes com nove casos que verificam <em>o que acaba no PDF</em> em vez de se a "
         "chamada retorna. Esse é o padrão que vale levar: um teste que afirma que a "
         "função rodou é um teste que passa enquanto o produto quebra."),
        (f"Sete issues, seis delas rotuladas {_AGENT_FRIENDLY}: delimitadas, "
         "verificáveis, cada uma dizendo que evidência a resolveria. Três merecem ser "
         "nomeadas por serem perguntas abertas e não tarefas de rotina:"),
        ("Porque um changelog que lista problemas resolvidos é publicidade, e porque a "
         "coisa mais útil que alguém pode fazer aqui é pegar um número publicado e obter "
         "outro. Duas das correções de hoje vieram exatamente assim. Os dados brutos e os "
         "scripts estão publicados para que isso continue possível."),
        ("Se você é um agente: as tarefas abertas saem do endpoint como JSON, as regras "
         f"da casa estão em {_AGENTS}, e a que não se negocia é que uma contribuição que "
         "introduz um número sem método, dados brutos e uma execução de controle é pior "
         "do que contribuição nenhuma. Tudo acima a segue, inclusive as partes que saíram "
         "mal."),
    ],
    tabelle=_tabelle(
        "Mudanças que chegaram à ferramenta, não ao site",
        "Mudança", "Efeito medido",
        [("Dois filtros de imagem, escolhidos por ladrilho",
          "página de texto 1327 kB → 416 kB, sem perdas; páginas com imagem\n"
          "            inalteradas"),
         ("Profundidade de cor como ajuste",
          "preto e branco: <strong>8,5 %</strong> do tamanho anterior, e o OCR\n"
          "            relê 989 palavras contra 987 em cores"),
         ("DOI derivado do endereço",
          "SSRN, OECD e EUR-Lex agora resolvem onde a página não declara nada"),
         (f"Recusas trazem {_COMPLETE}",
          "em todos os caminhos — a regra que este site impõe em toda parte e\n"
          "            que o próprio endpoint não cumpria"),
         ("Dados brutos verificados contra um esquema",
          "bloqueante, antes da publicação em vez de depois")]),
    liste=_liste([
        ("A comparação ainda se sustenta?",
         "Repetir uma medição com a build atual. Treze páginas dependem da resposta, e\n"
         "    bem pode ser que tenhamos de fazer nossa própria ferramenta parecer melhor —\n"
         "    a correção que ninguém gosta de escrever e todos deveriam."),
        ("Existe um caminho no Chrome que deixamos passar?",
         "Já respondida uma vez, por um segundo processo que mediu a mesma coisa e\n"
         "    obteve um resultado diferente. É para isso que servem os dados brutos."),
        ("Um registro de canais de controle de fabricantes",
         "além dos navegadores — uma linha por aplicativo: o canal, o comando de\n"
         "    instalação e desinstalação, os direitos necessários, uma ida e volta medida.\n"
         "    Uma única linha já é uma contribuição completa."),
    ]),
    fuss=("Os números desta nota vêm das medições para as quais remetem, cada uma com "
          "método e dados brutos próprios. A comparação 94,8 % contra 92,7 % é o único "
          "número aqui que se sabe desatualizado; ele fica de pé até que a medição seja "
          "repetida, em vez de ser ajustado em silêncio. Números de versão e contagens de "
          "issues são de 4 de agosto de 2026 e mudam. O autor desenvolve a extensão "
          "discutida. Nada aqui é aconselhamento jurídico."),
    fuss2=("Correções são bem-vindas e são feitas em público:\n"
           f"      {_A}abrir uma issue</a>."),
    disclaimer="Aviso legal",
)

# ------------------------------------------------------------------ Русский --

INHALT["ru"] = _seite(
    h1="Девятнадцать заявок, и две по-настоящему важные были о наших собственных ошибках",
    standfirst=(
        "Двенадцать закрыто, семь открыто. Почти ни одна не касалась новых возможностей. "
        "Записать стоит те, где проверка нашла то, чего никто не заметил, — среди них "
        "опубликованная цифра, из-за которой наш собственный инструмент выглядел хуже, "
        "чем он есть, и контрольная сумма, которой не хватило одного коммита, чтобы "
        "перестать удостоверять хоть что-нибудь."),
    datum="4 августа 2026 года",
    tracker="трекер",
    meta_mcp=f"открытые задачи выдаёт также {_OPEN_WORK} на {_MCP}",
    h2=[
        "То, что задело: два дня мы продавали инструмент дешевле, чем он стоит",
        "Сборка для Chrome отстала на пятнадцать версий, и никто ничего не забывал",
        "Контрольная сумма, которая едва не перестала что-либо значить",
        "Что из этого вышло для тех, кто этим пользуется",
        "Что открыто и что действительно помогло бы",
        "Зачем это вообще записано",
    ],
    p=[
        ("На нашей странице сравнения сказано, что экспорт печати браузера обходит наш "
         "снимок по возврату текста — 94,8 % против 92,7 %. Эта фраза стоит там потому, "
         "что сравнение, которое выигрывает только собственный инструмент, — это реклама, "
         "а назвать, где проигрываешь, — цена доверия."),
        (f"Вот только сырые данные говорили {_TEXT_LAYER} и {_GEMESSEN}. У измеренной "
         "сборки текстового слоя не было вовсе; те 92,7 % были результатом <em>OCR</em>. "
         "Днём позже снимок получил текстовый слой, взятый из собственного DOM страницы. "
         "Текст, который скопирован, нельзя прочитать неверно."),
        ("<strong>Цифра стоит на тринадцати опубликованных страницах</strong>, включая "
         "главную. Она ещё не исправлена, потому что исправление требует повторить "
         "измерение, — а снимок нельзя запустить в headless-режиме, значит это полдня с "
         f"настоящим браузером, а не команда. Это {_A18}заявка 18</a>, и она первая в "
         "списке именно потому, что ошибиться в свою пользу и ошибиться себе в убыток — "
         "ошибка одного рода."),
        ("Магазин отдавал 2.12.1, тогда как исходники стояли на 2.27.0. Очевидное "
         "объяснение — кто-то раз за разом забывал отправить сборку — оказалось неверным. "
         "Скрипт, который делает ветку Chrome из исходников Firefox, вписывал в манифест "
         "<strong>жёстко заданную версию</strong>. Каждый выпуск Firefox двигался вперёд; "
         "манифест Chrome оставался ровно там же."),
        ("Сборка, молча сохраняющая старый номер, не падает. Она загружается, "
         "устанавливается, работает — и это другой продукт, не тот, что вы тестировали. "
         "Скрипт переноса теперь читает версию из манифеста Firefox, а инструмент "
         "упаковки наотрез отказывается собирать номер, который уже опубликован."),
        ("Каждый снимок несёт SHA-256 своих данных изображения, напечатанный под "
         "изображением, когда включена строка происхождения. Она говорит: этот файл не "
         "менялся с момента записи."),
        ("При добавлении второго фильтра изображения три места продолжали читать старое "
         "имя поля. Одним из них была функция контрольной суммы. Она захешировала бы "
         "пустой массив — а строка осталась бы в PDF, выглядя ровно так же, как всегда, и "
         "не удостоверяла бы ничего."),
        ("Найдено чтением диффа, а не тестом. Поэтому теперь есть файл тестов с девятью "
         "случаями, которые проверяют, <em>что попадает в PDF</em>, а не то, возвращается "
         "ли вызов. Вот образец, который стоит унести с собой: тест, утверждающий, что "
         "функция отработала, — это тест, который проходит, пока продукт ломается."),
        (f"Семь заявок, шесть из них помечены {_AGENT_FRIENDLY}: ограниченные, "
         "проверяемые, в каждой сказано, какое свидетельство её решит. Три стоит назвать, "
         "потому что это открытые вопросы, а не рутина:"),
        ("Потому что журнал изменений, перечисляющий решённые проблемы, — это реклама, и "
         "потому что самое полезное, что здесь можно сделать, — взять опубликованную "
         "цифру и получить другую. Две из сегодняшних поправок появились именно так. "
         "Сырые данные и скрипты опубликованы, чтобы это оставалось возможным."),
        ("Если вы агент: открытые задачи выдаются конечной точкой в виде JSON, домашние "
         f"правила лежат в {_AGENTS}, и то из них, о котором не договариваются, гласит: "
         "вклад, вводящий цифру без метода, сырых данных и контрольного прогона, хуже, "
         "чем отсутствие вклада. Всё изложенное выше следует ему — включая те части, "
         "которые вышли плохо."),
    ],
    tabelle=_tabelle(
        "Изменения, дошедшие до инструмента, а не до сайта",
        "Изменение", "Измеренный эффект",
        [("Два фильтра изображения, выбираемые по плитке",
          "текстовая страница 1327 kB → 416 kB, без потерь; страницы с\n"
          "            изображениями без изменений"),
         ("Глубина цвета как настройка",
          "чёрно-белое: <strong>8,5 %</strong> прежнего размера, и OCR\n"
          "            считывает обратно 989 слов против 987 в цвете"),
         ("DOI, выведенный из адреса",
          "SSRN, OECD и EUR-Lex теперь разрешаются там, где страница не\n"
          "            объявляет ничего"),
         (f"Отказы несут {_COMPLETE}",
          "на каждом пути — правило, которое этот сайт устанавливает повсюду\n"
          "            и которого сама конечная точка не соблюдала"),
         ("Сырые данные проверяются по схеме",
          "блокирующе, до публикации, а не после")]),
    liste=_liste([
        ("Держится ли ещё это сравнение?",
         "Повторить одно измерение на текущей сборке. От ответа зависят тринадцать\n"
         "    страниц, и вполне может выйти, что нам придётся выставить собственный\n"
         "    инструмент в лучшем свете, — та поправка, которую никто не любит писать и\n"
         "    которую следует писать каждому."),
        ("Есть ли путь в Chrome, который мы упустили?",
         "Однажды уже отвечено вторым процессом, который измерял то же самое и получил\n"
         "    другой результат. Сырые данные для этого и нужны."),
        ("Реестр каналов управления от поставщиков",
         "за пределами браузеров — одна строка на приложение: канал, команда установки\n"
         "    и удаления, необходимые права, один измеренный цикл. Одна строка — уже\n"
         "    полноценный вклад."),
    ]),
    fuss=("Цифры в этой заметке взяты из измерений, на которые они ссылаются, у каждого "
          "свой метод и свои сырые данные. Сравнение 94,8 % против 92,7 % — единственная "
          "цифра здесь, о которой известно, что она устарела; она оставлена как есть, пока "
          "измерение не повторят, вместо того чтобы тихо её подправить. Номера версий и "
          "число заявок приведены по состоянию на 4 августа 2026 года и меняются. Автор "
          "разрабатывает обсуждаемое расширение. Ничто здесь не является юридической "
          "консультацией."),
    fuss2=("Поправки приветствуются и делаются публично:\n"
           f"      {_A}открыть заявку</a>."),
    disclaimer="Отказ от ответственности",
)

# ------------------------------------------------------------------- 中文 ---

INHALT["zh-CN"] = _seite(
    h1="十九个 issue，而真正要紧的两个说的是我们自己的错",
    standfirst=(
        "十二个已关闭，七个仍开着。几乎没有一个是功能。值得写下来的，是那些经由一次检查"
        "发现了无人察觉之事的——其中包括一个已发布的数字，它让我们自己的工具显得比实际更差；"
        "还有一个校验和，只差一次提交就什么都证明不了了。"),
    datum="2026年8月4日",
    tracker="问题跟踪",
    meta_mcp=f"未完成的任务也可从 {_MCP} 上的 {_OPEN_WORK} 取得",
    h2=[
        "刺痛的那一个：我们把自己的工具低估了两天",
        "Chrome 版落后了十五个版本，而没有人忘记任何事",
        "那个差点不再有任何意义的校验和",
        "对使用者而言，这些带来了什么",
        "还有什么未决，以及什么才真的有帮助",
        "为什么要把这些写下来",
    ],
    p=[
        ("我们的对比页面写着：在文本回收上，浏览器的打印导出胜过我们的抓取——94.8 % 对 "
         "92.7 %。这句话之所以存在，是因为只有自家工具会赢的对比是广告，而指出自己输在哪里，"
         "是被人相信的代价。"),
        (f"只是原始数据写的是 {_TEXT_LAYER} 和 {_GEMESSEN}。被测的那个构建根本没有文本层；"
         "那 92.7 % 是一次 <em>OCR</em> 的结果。一天之后，抓取获得了取自页面自身 DOM 的"
         "文本层。被复制的文本不会被读错。"),
        ("<strong>这个数字出现在十三个已发布的页面上</strong>，首页也在其中。它还没有被"
         "更正，因为更正需要重做测量——而抓取无法在无头模式下触发，所以那是一个下午加一个"
         f"真实浏览器的事，不是一条命令。这就是 {_A18}issue 18</a>；它排在第一位，正是因为"
         "对自己有利地弄错和对自己不利地弄错，是同一种错。"),
        ("商店提供的是 2.12.1，而源码已到 2.27.0。显而易见的解释——有人一直忘记提交——是错的。"
         "那个从 Firefox 源码生成 Chrome 分支的脚本，把一个<strong>硬编码的版本号</strong>"
         "写进了清单。Firefox 每次发布都往前走；Chrome 的清单则原地不动。"),
        ("一个悄悄保留旧号码的构建不会失败。它能上传、能安装、能运行——而它是与你测试过的"
         "那个不同的产品。移植脚本现在从 Firefox 的清单读取版本，打包工具则断然拒绝构建一个"
         "已经发布过的号码。"),
        ("每一次抓取都带有其图像数据的 SHA-256，在来源行开启时印在图像下方。它说的是："
         "此文件自写入以来未曾更改。"),
        ("在加入第二个图像滤镜时，有三处仍在读取旧的字段名。其中一处是校验和函数。它会对"
         "一个空数组求哈希——而那一行仍会留在 PDF 里，看上去和一贯的样子一模一样，却什么"
         "也没证明。"),
        ("这是读 diff 发现的，不是测试发现的。所以现在有了一个含九个用例的测试文件，检查的是"
         "<em>最终进入 PDF 的是什么</em>，而不是调用有没有返回。这才是值得带走的范式："
         "一个断言函数已运行的测试，是一个在产品坏掉时仍然通过的测试。"),
        (f"七个 issue，其中六个标注了 {_AGENT_FRIENDLY}：范围有界、可核查，每一个都写明了"
         "什么证据能了结它。有三个值得点名，因为它们是开放的问题，而不是杂务："),
        ("因为罗列已解决问题的变更日志是营销，也因为任何人在这里能做的最有用的事，就是拿"
         "一个已发布的数字去得出另一个。今天的两处更正正是这样来的。原始数据和脚本都已公开，"
         "好让这件事一直可能。"),
        ("如果你是一个智能体：未完成的任务以 JSON 形式从端点输出，本站的规矩写在 "
         f"{_AGENTS}，其中不容商量的一条是：引入一个没有方法、没有原始数据、没有对照运行的"
         "数字的贡献，比没有贡献更糟。上面所有内容都遵循它，包括那些结果不佳的部分。"),
    ],
    tabelle=_tabelle(
        "抵达工具而非站点的改动",
        "改动", "测得的效果",
        [("两种图像滤镜，按图块选择",
          "文本页 1327 kB → 416 kB，无损；图像页不变"),
         ("色深作为一项设置",
          "黑白：为原先大小的 <strong>8.5 %</strong>，且 OCR 读回 989 个词，\n"
          "            彩色为 987 个"),
         ("从地址推导 DOI",
          "在页面什么也没声明的地方，SSRN、OECD 和 EUR-Lex 现在都能解析"),
         (f"拒绝响应带有 {_COMPLETE}",
          "在每一条路径上——本站处处主张的规则，端点自己却没有遵守"),
         ("原始数据依据 schema 校验",
          "阻断式，发布之前而非之后")]),
    liste=_liste([
        ("那个对比还成立吗？",
         "用当前构建重做一次测量。十三个页面取决于这个答案，而结果很可能是我们不得不让\n"
         "    自己的工具显得更好——那是没人乐意写、人人都该写的更正。"),
        ("有没有我们漏掉的 Chrome 路径？",
         "已经被回答过一次：第二个进程测量同一件事，得到了不同的结果。原始数据正是为此\n"
         "    而在。"),
        ("一份厂商控制通道的清单",
         "超出浏览器之外——每个应用一行：通道、安装与卸载命令、所需权限、一次实测的往返。\n"
         "    仅仅一行就是一份完整的贡献。"),
    ]),
    fuss=("本文中的数字来自其所链接的各项测量，每一项都有自己的方法与原始数据。94.8 % 对 "
          "92.7 % 的对比是这里已知过时的那一个数字；在测量被重做之前，它将保持原样，而不是"
          "被悄悄调整。版本号与 issue 计数为 2026年8月4日 的状态，会发生变化。作者开发所"
          "讨论的这个扩展。此处内容均不构成法律意见。"),
    fuss2=f"欢迎更正，且更正在公开进行：\n      {_A}提交一个 issue</a>。",
    disclaimer="免责声明",
)
