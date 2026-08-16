#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/mitmachen/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, woertlich uebernommen — kein
Builder. Die Seite ist auf Deutsch geschrieben: `de` traegt den vorhandenen
Text, `en` ist daraus uebersetzt und bleibt die BASIS, die uebrigen sieben
uebersetzen die englische Fassung.

Unveraendert in jeder Sprache: Zahlen (10 von 20, 100 %, 79 %, 92,6 %, 60 von
248, 18, 179 s, 4,1 s, 403, Issue 14), Lizenzen (MIT, CC BY 4.0), Eigennamen
(Citoid, Marionette, VS Code, JetBrains, Thunderbird, Obsidian, GitHub,
Reddit, Android), Werkzeugnamen (<code>open_work</code>), der Befehl im
<code>pre</code>-Block und alle Adressen. Dezimaltrennzeichen folgen der
Sprache — 92,6 % in de/es/fr/it/pt-BR/ru, 92.6 % in en/ja/zh-CN; die Ziffern
bleiben dieselben.

Rendern:  python3 tools/seite-neunsprachig.py texte_mitmachen.py
"""

URL = "https://provinglab.dev/mitmachen/"
ZIEL = "mitmachen/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# Bausteine, die in jeder Sprache gleich bleiben. Sie hier zu halten spart
# neunfaches Abschreiben und schliesst aus, dass eine Adresse in einer Sprache
# abweicht.
_ISSUES = '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">'
_ISSUE14 = '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues/14">'
_OPEN_WORK = "<code>open_work</code>"
_MCP = '<a href="/for-agents/">/mcp</a>'
_FOR_AGENTS = '<a href="/for-agents/">'
_FOR_AGENTS_LINK = '<a href="/for-agents/">/for-agents/</a>'
_DATA = '<a href="/data/">'
_DATA_CODE = '<a href="/data/"><code>/data/</code></a>'
_AGENTS_MD = '<a href="/AGENTS.md"><code>/AGENTS.md</code></a>'
_INSTALL = '<a href="/measurements/install-an-extension-without-a-click/">'
_PRINT = '<a href="/measurements/print-to-pdf-vs-screenshot/">'
_ZURUECK = '<a href="../">'
_DISCLAIMER = '<a href="../disclaimer/">'
_BEFEHL = ("<pre><code>claude mcp add --transport http provinglab "
           "https://provinglab.dev/mcp</code></pre>")

# Adressen der vier Messungen in der ersten Tabelle — Reihenfolge fest.
_MESSUNGEN = [
    "/measurements/reading-list-to-bibliography/",
    "/measurements/citation-extraction/",
    "/measurements/webpage-to-pdf-for-ocr/",
    "/measurements/android-capture-extensions/",
]


def _tabelle_wackelt(th_angabe, th_warum, zeilen):
    """Die vier wackeligen Angaben.

    `zeilen` ist eine Liste aus (Linktext, Rest der Zelle, Begruendung). Die
    Adressen stehen in _MESSUNGEN, nicht in den Sprachen — so kann keine
    Fassung auf eine andere Messung zeigen.
    """
    tr = "\n".join(
        f'    <tr><td><a href="{href}">{lt}</a>\n'
        f'        {rest}</td>\n'
        f'        <td>{warum}</td></tr>'
        for href, (lt, rest, warum) in zip(_MESSUNGEN, zeilen))
    return f'''<table>
  <thead><tr><th scope="col">{th_angabe}</th><th scope="col">{th_warum}</th></tr></thead>
  <tbody>
{tr}
  </tbody>
</table>'''


def _tabelle_agenten(th_was, th_wo, was, wo_werkzeug, issues_text):
    """Was ein Agent braucht und wo es liegt. Vier von fuenf Zielzellen sind
    reine Adressen und stehen deshalb hier."""
    return f'''<table>
  <thead><tr><th scope="col">{th_was}</th><th scope="col">{th_wo}</th></tr></thead>
  <tbody>
    <tr><td>{was[0]}</td><td>{_AGENTS_MD}</td></tr>
    <tr><td>{was[1]}</td><td>{wo_werkzeug}</td></tr>
    <tr><td>{was[2]}</td><td>{_ISSUES}{issues_text}</a></td></tr>
    <tr><td>{was[3]}</td><td>{_DATA_CODE}</td></tr>
    <tr><td>{was[4]}</td><td>{_FOR_AGENTS_LINK}</td></tr>
  </tbody>
</table>'''


def _tabelle_weg(th_weg, th_dauer, th_ergebnis, r_ui, e_ui, r_kanal, e_kanal,
                 dez=","):
    """Oberflaeche gegen Herstellerkanal. Die beiden Zeiten stehen nur hier;
    `dez` setzt nur das Trennzeichen, die Ziffern bleiben."""
    return f'''<table>
  <thead><tr><th scope="col">{th_weg}</th><th scope="col">{th_dauer}</th><th scope="col">{th_ergebnis}</th></tr></thead>
  <tbody>
    <tr><th scope="row">{r_ui}</th><td>179 s</td>
        <td>{e_ui}</td></tr>
    <tr><th scope="row">{r_kanal}</th><td>4{dez}1 s</td>
        <td>{e_kanal}</td></tr>
  </tbody>
</table>'''


def _punkte(eintraege):
    return "\n".join(f"  <li>{e}</li>" for e in eintraege)


def _seite(h1, standfirst, meta, h2, h3, p, tab1, tab2, tab3, regeln, nicht,
           fuss, korrekturen, offenlegung, disclaimer_text):
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{meta}</p>
</header>

<h2>{h2[0]}</h2>
<p>
  {p[0]}
</p>
{tab1}
<p>
  {p[1]}
</p>

<h2>{h2[1]}</h2>
<p>
  {p[2]}
</p>
{tab2}
{_BEFEHL}
<p>
  {p[3]}
</p>

<h3>{h3}</h3>
<p>
  {p[4]}
</p>
{tab3}
<p>
  {p[5]}
</p>
<p>
  {p[6]}
</p>
<p>
  {p[7]}
</p>

<h2>{h2[2]}</h2>
<ol>
{_punkte(regeln)}
</ol>

<h2>{h2[3]}</h2>
<ul>
{_punkte(nicht)}
</ul>

<h2>{h2[4]}</h2>
<p>
  {p[8]}
</p>
<footer>
      {fuss}
      <br><br>
      {korrekturen}
      <br><br>
      {offenlegung}
      <br><br>
      {_ZURUECK}← Proving Lab</a> · {_DISCLAIMER}{disclaimer_text}</a>
    </footer>'''


INHALT = {}

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="Recalculate one number. Preferably the one that is wrong.",
    standfirst=(
        "Every figure here has a method, raw data and a control run — so that "
        "it can be recalculated, not so that it can be believed. The most "
        "useful contribution to this project is therefore not a new "
        "measurement but a <strong>counter-measurement that comes out "
        "differently</strong>."),
    meta=("3 August 2026 · open tasks: " + _ISSUES + "GitHub</a> · "
          "machine-readable through the tool " + _OPEN_WORK + " on " + _MCP),
    h2=["Where it is most likely to give way",
        "For AI agents",
        "The five rules, briefly",
        "What is not needed here",
        "What to expect"],
    h3="Why this might be of interest beyond this project",
    p=[
        ("This is no formula of modesty — the weak spots are named because "
         "they belong in the open:"),
        ("Anyone who reproduces one of these numbers and gets something else "
         "has delivered the most valuable contribution this project can "
         "accept. The " + _DATA + "raw data</a> is open under CC BY 4.0, and "
         "every post carries a section saying where the measurement probably "
         "does not hold."),
        ("This project is set up so that an agent can work on it without "
         "asking anyone first. What it needs for that sits at fixed "
         "addresses:"),
        ("After that this is enough: <em>“Look at the open tasks on provinglab "
         "and take one.”</em> The tool delivers tasks with labels, an excerpt "
         "and the five rules that are different here from the usual ones."),
        ("Not as an appeal but as an observation: every system that installs "
         "software on someone else’s machine faces the same question — operate "
         "the interface, or use the channel the vendor ships anyway. The "
         + _INSTALL + "measurement on this</a> came out unambiguous, and not "
         "because of the speed:"),
        ("The difference that matters is the second column from the right. A "
         "route that reports success on failure poisons everything that comes "
         "after it — and that is more expensive than any minute lost. For a "
         "system that carries out such steps unsupervised, that is the "
         "difference between usable and unusable."),
        ("That is why " + _ISSUE14 + "issue&nbsp;14</a> is open: a directory "
         "of such vendor channels, one line per application — channel, install "
         "and uninstall command, privileges required, one measured runtime. "
         "VS&nbsp;Code, JetBrains, Thunderbird and Obsidian are in there as "
         "candidates; not one is measured. A single line is a complete "
         "contribution, and whoever adds it has the result first — here it "
         "then stands under CC&nbsp;BY&nbsp;4.0 for everyone else."),
        ("The same goes for the " + _FOR_AGENTS + "citation endpoint</a>: a "
         "measured 10 of 20 sources become complete records without a browser, "
         "and the remaining ten are named one by one instead of dismissed "
         "wholesale. Anyone who re-measures that and gets a different number "
         "improves a foundation they use themselves."),
        ("This is a private, non-commercial project by a single person. There "
         "is no bounty programme, no promised response time and no return "
         "beyond being named in the post. Contributions are read and answered; "
         "what holds is adopted and named as a correction. The software is "
         "under MIT, the measurements under CC BY 4.0 — both stay that way."),
    ],
    tab1=_tabelle_wackelt(
        "Figure", "Why it could give way",
        [("10 of 20 sources", "become citation records",
          "Four refusals are blocks against a <em>data-centre address</em>. "
          "From a home or campus network the rate ought to be higher — "
          "<strong>that has not been measured.</strong>"),
         ("100 % against 79 %", "compared with Citoid",
          "18 randomly drawn works, one draw. A different sample can produce "
          "a different number."),
         ("92.6 % text yield", "from the text recognition",
          "One article, one resolution series, one recognition engine. Other "
          "scripts and languages are untested."),
         ("60 of 248", "extensions with an Android declaration",
          "What an extension <em>declares</em>, not what it does on a device. "
          "Not one was installed.")]),
    tab2=_tabelle_agenten(
        "What", "Where",
        ["Rules, construction, limits",
         "Open tasks, machine-readable",
         "Open tasks, for humans",
         "Raw data for recalculating",
         "Connection in one line"],
        "Tool " + _OPEN_WORK + " on <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Route", "Duration", "Result",
        "Interface with real clicks",
        "reported success at every step and installed <strong>nothing</strong>",
        "Vendor channel (Marionette)",
        "installs and uninstalls, reports errors as errors",
        dez="."),
    regeln=[
        ("<strong>Evidence before wording.</strong> Every factual claim needs "
         "a source and a retrieval date, or it becomes an opinion, or it drops "
         "out. A check enforces that before delivery."),
        ("<strong>Do not assert the intent of third parties.</strong> “The "
         "server answered with 403” is an observation. “They are blocking on "
         "purpose” carries a burden of proof and cannot be proven."),
        ("<strong>A comparison your own tool can only win is "
         "advertising.</strong> That is why this site says that the browser’s "
         "print export wins on text."),
        ("<strong>No result is an error, not a zero value.</strong> If a "
         "measurement returns zero, the measurement is the first suspect."),
        ("<strong>Raw data is not smoothed.</strong> A correction is named as "
         "a correction, not quietly worked in."),
    ],
    nicht=[
        ("No contributions that introduce a number without evidence. That is "
         "the one mistake that cannot be repaired afterwards — a figure once "
         "cited travels on by itself."),
        ("No automated posting in forums, on Reddit or in comments. Where "
         "people are reached, it happens by hand and with a name."),
        ("No circumvention of other people’s protective measures. Where a site "
         "locks a reader out, that is reported, not circumvented."),
    ],
    fuss=("Open tasks stand as GitHub issues and are delivered "
          "machine-readably by the tool open_work on /mcp."),
    korrekturen=("Corrections are welcome and are made in public: "
                 + _ISSUES + "open an issue</a>."),
    offenlegung=("Disclosure: the author develops Full Page PDF Snap, the "
                 "extension named on this page. The browser’s own print-to-PDF "
                 "is " + _PRINT + "measured against it</a>, including where "
                 "print wins."),
    disclaimer_text="Disclaimer",
)

# ------------------------------------------------------------------- Deutsch
INHALT["de"] = _seite(
    h1="Rechnen Sie eine Zahl nach. Am liebsten die, die falsch ist.",
    standfirst=(
        "Jede Angabe hier hat eine Methode, Rohdaten und einen Kontrolllauf — "
        "damit sie nachgerechnet werden kann, nicht damit sie geglaubt wird. "
        "Der nützlichste Beitrag zu diesem Projekt ist deshalb keine neue "
        "Messung, sondern eine <strong>Gegenmessung, die etwas anderes "
        "ergibt</strong>."),
    meta=("3 August 2026 · offene Aufgaben: " + _ISSUES + "GitHub</a> · "
          "maschinenlesbar über das Werkzeug " + _OPEN_WORK + " auf " + _MCP),
    h2=["Wo es am wahrscheinlichsten hakt",
        "Für KI-Agenten",
        "Die fünf Regeln, kurz",
        "Was hier nicht gebraucht wird",
        "Womit zu rechnen ist"],
    h3="Warum das über dieses Projekt hinaus interessant sein könnte",
    p=[
        ("Das ist keine Bescheidenheitsfloskel — die Stellen sind benannt, "
         "weil sie benannt gehören:"),
        ("Wer eine dieser Zahlen nachstellt und etwas anderes bekommt, hat den "
         "wertvollsten Beitrag geliefert, den dieses Projekt annehmen kann. "
         "Die " + _DATA + "Rohdaten</a> liegen unter CC BY 4.0 offen, und in "
         "jedem Beitrag steht ein Abschnitt, der sagt, wo die Messung "
         "vermutlich nicht trägt."),
        ("Dieses Projekt ist so eingerichtet, dass ein Agent daran arbeiten "
         "kann, ohne vorher jemanden zu fragen. Was er dafür braucht, liegt an "
         "festen Adressen:"),
        ("Danach genügt: <em>„Sieh dir die offenen Aufgaben auf provinglab an "
         'und nimm eine."</em> Das Werkzeug liefert Aufgaben mit Labels, '
         "Auszug und den fünf Regeln, die hier anders sind als üblich."),
        ("Nicht als Appell, sondern als Beobachtung: Jedes System, das "
         "Software auf einer fremden Maschine einrichtet, steht vor derselben "
         "Frage — Oberfläche bedienen oder den Kanal nutzen, den der Hersteller "
         "ohnehin mitbringt. Die " + _INSTALL + "Messung dazu</a> fiel "
         "eindeutig aus, und zwar nicht wegen der Geschwindigkeit:"),
        ("Der Unterschied, auf den es ankommt, ist die zweite Spalte von "
         "rechts. Ein Weg, der bei Misserfolg Erfolg meldet, vergiftet alles, "
         "was danach kommt — und das ist teurer als jede verlorene Minute. Für "
         "ein System, das solche Schritte unbeaufsichtigt ausführt, ist das "
         "der Unterschied zwischen brauchbar und unbrauchbar."),
        ("Deshalb ist " + _ISSUE14 + "Issue&nbsp;14</a> offen: ein Verzeichnis "
         "solcher Herstellerkanäle, eine Zeile je Anwendung — Kanal, "
         "Installations- und Deinstallationsbefehl, benötigte Rechte, eine "
         "gemessene Laufzeit. VS&nbsp;Code, JetBrains, Thunderbird und "
         "Obsidian stehen als Kandidaten drin, gemessen ist keiner. Eine "
         "einzelne Zeile ist ein vollständiger Beitrag, und wer sie "
         "beisteuert, hat das Ergebnis selbst zuerst — hier steht es danach "
         "unter CC&nbsp;BY&nbsp;4.0 für alle anderen."),
        ("Dasselbe gilt für den " + _FOR_AGENTS + "Zitations-Endpunkt</a>: "
         "gemessene 10 von 20 Quellen werden ohne Browser zu vollständigen "
         "Datensätzen, und die zehn übrigen sind einzeln benannt statt "
         "pauschal abgetan. Wer das nachmisst und eine andere Zahl bekommt, "
         "verbessert eine Grundlage, die er selbst benutzt."),
        ("Dies ist ein privates, nicht-kommerzielles Projekt einer einzelnen "
         "Person. Es gibt kein Prämienprogramm, keine zugesagte Antwortzeit "
         "und keine Gegenleistung außer der Nennung im Beitrag. Beiträge "
         "werden gelesen und beantwortet; was zutrifft, wird übernommen und "
         "als Korrektur benannt. Die Software steht unter MIT, die Messungen "
         "unter CC BY 4.0 — beides bleibt so."),
    ],
    tab1=_tabelle_wackelt(
        "Angabe", "Warum sie wackeln könnte",
        [("10 von 20 Quellen", "werden zu Zitationsdatensätzen",
          "Vier Ablehnungen sind Sperren gegen eine "
          "<em>Rechenzentrums-Adresse</em>. Aus einem Heim- oder Campusnetz "
          "müsste die Quote höher liegen — <strong>gemessen ist das "
          "nicht.</strong>"),
         ("100 % gegen 79 %", "gegenüber Citoid",
          "18 zufällig gezogene Werke, eine Ziehung. Eine andere Stichprobe "
          "kann eine andere Zahl ergeben."),
         ("92,6 % Textausbeute", "aus der Texterkennung",
          "Ein Artikel, eine Auflösungsreihe, ein Erkennungsprogramm. Andere "
          "Schriften und Sprachen sind ungeprüft."),
         ("60 von 248", "Erweiterungen mit Android-Angabe",
          "Was eine Erweiterung <em>deklariert</em>, nicht was sie auf einem "
          "Gerät tut. Keine wurde installiert.")]),
    tab2=_tabelle_agenten(
        "Was", "Wo",
        ["Regeln, Bauweise, Grenzen",
         "Offene Aufgaben, maschinenlesbar",
         "Offene Aufgaben, für Menschen",
         "Rohdaten zum Nachrechnen",
         "Anbindung in einer Zeile"],
        "Werkzeug " + _OPEN_WORK + " auf <code>/mcp</code>",
        "GitHub-Issues"),
    tab3=_tabelle_weg(
        "Weg", "Dauer", "Ergebnis",
        "Oberfläche mit echten Klicks",
        "meldete an jedem Schritt Erfolg und installierte "
        "<strong>nichts</strong>",
        "Herstellerkanal (Marionette)",
        "installiert und deinstalliert, meldet Fehler als Fehler"),
    regeln=[
        ("<strong>Beleg vor Formulierung.</strong> Jede Tatsachenbehauptung "
         "braucht Quelle und Abrufdatum, oder sie wird zur Meinung, oder sie "
         "fällt raus. Eine Prüfung erzwingt das vor der Auslieferung."),
        ("<strong>Keine Absicht Dritter behaupten.</strong> „Der Server "
         'antwortete mit 403" ist eine Beobachtung. „Die sperren absichtlich" '
         "ist beweispflichtig und nicht beweisbar."),
        ("<strong>Ein Vergleich, den das eigene Werkzeug nur gewinnt, ist "
         "Werbung.</strong> Deshalb steht auf dieser Seite, dass der "
         "Druckexport des Browsers beim Text gewinnt."),
        ("<strong>Kein Ergebnis ist ein Fehler, kein Nullwert.</strong> Wenn "
         "eine Messung null liefert, ist zuerst die Messung verdächtig."),
        ("<strong>Rohdaten werden nicht geglättet.</strong> Eine Korrektur "
         "wird als Korrektur benannt, nicht stillschweigend eingearbeitet."),
    ],
    nicht=[
        ("Keine Beiträge, die eine Zahl ohne Beleg einführen. Das ist der eine "
         "Fehler, der sich später nicht mehr reparieren lässt — eine einmal "
         "zitierte Angabe wandert alleine weiter."),
        ("Kein automatisiertes Posten in Foren, auf Reddit oder in "
         "Kommentaren. Wo Menschen erreicht werden, geschieht das von Hand und "
         "mit Namen."),
        ("Keine Umgehung fremder Schutzmaßnahmen. Wo eine Seite einen Leser "
         "aussperrt, wird das berichtet, nicht umgangen."),
    ],
    fuss=("Offene Aufgaben stehen als GitHub-Issues und werden vom Werkzeug "
          "open_work auf /mcp maschinenlesbar ausgeliefert."),
    korrekturen=("Korrekturen sind willkommen und werden öffentlich gemacht: "
                 + _ISSUES + "ein Issue öffnen</a>."),
    offenlegung=("Offenlegung: Der Autor entwickelt Full Page PDF Snap, die "
                 "auf dieser Seite genannte Erweiterung. Der eigene PDF-Druck "
                 "des Browsers ist " + _PRINT + "dagegen gemessen</a>, "
                 "einschließlich der Stelle, an der der Druck gewinnt."),
    disclaimer_text="Haftungsausschluss",
)

# ------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Rehaga usted una cifra. Preferiblemente la que está mal.",
    standfirst=(
        "Cada dato de aquí tiene un método, datos brutos y una ejecución de "
        "control — para que se pueda recalcular, no para que se lo crea. Por "
        "eso la aportación más útil a este proyecto no es una medición nueva, "
        "sino una <strong>contramedición que dé otro resultado</strong>."),
    meta=("3 de agosto de 2026 · tareas abiertas: " + _ISSUES + "GitHub</a> · "
          "legible por máquinas mediante la herramienta " + _OPEN_WORK
          + " en " + _MCP),
    h2=["Dónde es más probable que falle",
        "Para agentes de IA",
        "Las cinco reglas, en breve",
        "Qué no hace falta aquí",
        "Con qué hay que contar"],
    h3="Por qué esto podría interesar más allá de este proyecto",
    p=[
        ("No es una fórmula de modestia: los puntos débiles están nombrados "
         "porque merecen estarlo:"),
        ("Quien repita una de estas cifras y obtenga otra cosa habrá "
         "entregado la aportación más valiosa que este proyecto puede "
         "aceptar. Los " + _DATA + "datos brutos</a> están abiertos bajo "
         "CC BY 4.0, y en cada publicación hay un apartado que dice dónde es "
         "probable que la medición no se sostenga."),
        ("Este proyecto está montado de modo que un agente pueda trabajar en "
         "él sin preguntar antes a nadie. Lo que necesita para eso está en "
         "direcciones fijas:"),
        ("Después basta con esto: <em>«Mira las tareas abiertas en provinglab "
         "y toma una.»</em> La herramienta entrega tareas con etiquetas, un "
         "extracto y las cinco reglas que aquí son distintas de lo habitual."),
        ("No como llamamiento, sino como observación: todo sistema que instala "
         "software en una máquina ajena se enfrenta a la misma pregunta — "
         "manejar la interfaz o usar el canal que el fabricante ya trae "
         "consigo. La " + _INSTALL + "medición al respecto</a> resultó "
         "inequívoca, y no por la velocidad:"),
        ("La diferencia que cuenta es la segunda columna por la derecha. Un "
         "camino que ante el fracaso informa de éxito envenena todo lo que "
         "viene después — y eso sale más caro que cualquier minuto perdido. "
         "Para un sistema que ejecuta tales pasos sin supervisión, esa es la "
         "diferencia entre utilizable e inutilizable."),
        ("Por eso está abierta la " + _ISSUE14 + "issue&nbsp;14</a>: un "
         "directorio de esos canales de fabricante, una línea por aplicación "
         "— canal, orden de instalación y de desinstalación, permisos "
         "necesarios, un tiempo de ejecución medido. VS&nbsp;Code, JetBrains, "
         "Thunderbird y Obsidian figuran como candidatos; ninguno está "
         "medido. Una sola línea es una aportación completa, y quien la "
         "aporte tiene el resultado primero — aquí queda después bajo "
         "CC&nbsp;BY&nbsp;4.0 para todos los demás."),
        ("Lo mismo vale para el " + _FOR_AGENTS + "endpoint de citas</a>: 10 "
         "de 20 fuentes medidas se convierten en registros completos sin "
         "navegador, y las diez restantes están nombradas una a una en lugar "
         "de descartadas en bloque. Quien lo vuelva a medir y obtenga otra "
         "cifra mejora una base que él mismo usa."),
        ("Este es un proyecto privado y no comercial de una sola persona. No "
         "hay programa de recompensas, ni tiempo de respuesta prometido, ni "
         "contraprestación más allá de la mención en la publicación. Las "
         "aportaciones se leen y se responden; lo que resulta cierto se asume "
         "y se nombra como corrección. El software está bajo MIT, las "
         "mediciones bajo CC BY 4.0 — ambas cosas siguen así."),
    ],
    tab1=_tabelle_wackelt(
        "Dato", "Por qué podría tambalearse",
        [("10 de 20 fuentes", "se convierten en registros de cita",
          "Cuatro rechazos son bloqueos contra una <em>dirección de centro de "
          "datos</em>. Desde una red doméstica o de campus la tasa debería ser "
          "mayor — <strong>eso no está medido.</strong>"),
         ("100 % frente a 79 %", "en comparación con Citoid",
          "18 obras extraídas al azar, una extracción. Otra muestra puede dar "
          "otra cifra."),
         ("92,6 % de texto recuperado", "del reconocimiento de texto",
          "Un artículo, una serie de resoluciones, un programa de "
          "reconocimiento. Otras escrituras y lenguas están sin comprobar."),
         ("60 de 248", "extensiones con declaración de Android",
          "Lo que una extensión <em>declara</em>, no lo que hace en un "
          "dispositivo. No se instaló ninguna.")]),
    tab2=_tabelle_agenten(
        "Qué", "Dónde",
        ["Reglas, construcción, límites",
         "Tareas abiertas, legibles por máquinas",
         "Tareas abiertas, para personas",
         "Datos brutos para recalcular",
         "Conexión en una línea"],
        "Herramienta " + _OPEN_WORK + " en <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Camino", "Duración", "Resultado",
        "Interfaz con clics reales",
        "informó de éxito en cada paso e instaló <strong>nada</strong>",
        "Canal del fabricante (Marionette)",
        "instala y desinstala, informa de los errores como errores"),
    regeln=[
        ("<strong>Prueba antes que formulación.</strong> Toda afirmación de "
         "hecho necesita fuente y fecha de consulta, o pasa a ser opinión, o "
         "se cae. Una comprobación lo impone antes de la entrega."),
        ("<strong>No atribuir intenciones a terceros.</strong> «El servidor "
         "respondió con 403» es una observación. «Bloquean a propósito» exige "
         "prueba y no se puede probar."),
        ("<strong>Una comparación que la propia herramienta solo puede ganar "
         "es publicidad.</strong> Por eso en este sitio consta que la "
         "exportación de impresión del navegador gana en el texto."),
        ("<strong>Ningún resultado es un error, no un valor cero.</strong> Si "
         "una medición devuelve cero, la primera sospechosa es la medición."),
        ("<strong>Los datos brutos no se alisan.</strong> Una corrección se "
         "nombra como corrección, no se incorpora en silencio."),
    ],
    nicht=[
        ("Ninguna aportación que introduzca una cifra sin prueba. Ese es el "
         "único error que después ya no se puede reparar — un dato citado una "
         "vez sigue viajando solo."),
        ("Ninguna publicación automatizada en foros, en Reddit o en "
         "comentarios. Donde se llega a personas, se hace a mano y con "
         "nombre."),
        ("Ninguna elusión de medidas de protección ajenas. Donde una página "
         "deja fuera a un lector, eso se informa, no se elude."),
    ],
    fuss=("Las tareas abiertas figuran como GitHub issues y las entrega de "
          "forma legible por máquinas la herramienta open_work en /mcp."),
    korrekturen=("Las correcciones son bienvenidas y se hacen en público: "
                 + _ISSUES + "abrir una issue</a>."),
    offenlegung=("Divulgación: el autor desarrolla Full Page PDF Snap, la "
                 "extensión nombrada en esta página. La impresión a PDF del "
                 "propio navegador está " + _PRINT + "medida contra ella</a>, "
                 "incluido dónde gana la impresión."),
    disclaimer_text="Aviso legal",
)

# ------------------------------------------------------------------- Français
INHALT["fr"] = _seite(
    h1="Refaites le calcul d’un chiffre. De préférence celui qui est faux.",
    standfirst=(
        "Chaque indication ici a une méthode, des données brutes et une "
        "exécution de contrôle — pour qu’on puisse la recalculer, non pour "
        "qu’on la croie. La contribution la plus utile à ce projet n’est donc "
        "pas une nouvelle mesure, mais une <strong>contre-mesure qui donne "
        "autre chose</strong>."),
    meta=("3 août 2026 · tâches ouvertes : " + _ISSUES + "GitHub</a> · "
          "lisible par machine via l’outil " + _OPEN_WORK + " sur " + _MCP),
    h2=["Là où cela risque le plus de céder",
        "Pour les agents d’IA",
        "Les cinq règles, en bref",
        "Ce dont on n’a pas besoin ici",
        "À quoi il faut s’attendre"],
    h3="Pourquoi cela pourrait intéresser au-delà de ce projet",
    p=[
        ("Ce n’est pas une formule de modestie : les points faibles sont "
         "nommés parce qu’ils doivent l’être :"),
        ("Qui refait l’une de ces mesures et obtient autre chose a fourni la "
         "contribution la plus précieuse que ce projet puisse accepter. Les "
         + _DATA + "données brutes</a> sont ouvertes sous CC BY 4.0, et chaque "
         "publication comporte une section qui dit où la mesure ne tient "
         "probablement pas."),
        ("Ce projet est agencé de telle sorte qu’un agent puisse y travailler "
         "sans demander à personne au préalable. Ce dont il a besoin pour cela "
         "se trouve à des adresses fixes :"),
        ("Ensuite il suffit de : <em>« Regarde les tâches ouvertes sur "
         "provinglab et prends-en une. »</em> L’outil livre les tâches avec "
         "leurs étiquettes, un extrait et les cinq règles qui, ici, diffèrent "
         "de l’usage."),
        ("Non comme un appel, mais comme une observation : tout système qui "
         "installe un logiciel sur une machine étrangère se heurte à la même "
         "question — piloter l’interface ou utiliser le canal que le fabricant "
         "fournit de toute façon. La " + _INSTALL + "mesure à ce sujet</a> a "
         "été sans ambiguïté, et pas à cause de la vitesse :"),
        ("La différence qui compte est l’avant-dernière colonne. Un chemin qui "
         "annonce un succès en cas d’échec empoisonne tout ce qui vient "
         "ensuite — et cela coûte plus cher que n’importe quelle minute "
         "perdue. Pour un système qui exécute de telles étapes sans "
         "surveillance, c’est la différence entre utilisable et inutilisable."),
        ("C’est pourquoi le " + _ISSUE14 + "ticket&nbsp;14</a> est ouvert : un "
         "répertoire de ces canaux de fabricant, une ligne par application — "
         "canal, commande d’installation et de désinstallation, droits "
         "nécessaires, un temps d’exécution mesuré. VS&nbsp;Code, JetBrains, "
         "Thunderbird et Obsidian y figurent comme candidats ; aucun n’est "
         "mesuré. Une seule ligne est une contribution complète, et celui qui "
         "l’apporte a le résultat en premier — il figure ensuite ici sous "
         "CC&nbsp;BY&nbsp;4.0 pour tous les autres."),
        ("Il en va de même pour le " + _FOR_AGENTS + "point de terminaison de "
         "citation</a> : 10 sources mesurées sur 20 deviennent des notices "
         "complètes sans navigateur, et les dix autres sont nommées une par "
         "une au lieu d’être écartées en bloc. Qui le remesure et obtient un "
         "autre chiffre améliore une base qu’il utilise lui-même."),
        ("Il s’agit d’un projet privé et non commercial mené par une seule "
         "personne. Il n’y a pas de programme de primes, pas de délai de "
         "réponse promis et pas de contrepartie hors la mention dans la "
         "publication. Les contributions sont lues et font l’objet d’une "
         "réponse ; ce qui se vérifie est repris et nommé comme correction. Le "
         "logiciel est sous MIT, les mesures sous CC BY 4.0 — les deux le "
         "restent."),
    ],
    tab1=_tabelle_wackelt(
        "Indication", "Pourquoi elle pourrait vaciller",
        [("10 sources sur 20", "deviennent des notices de citation",
          "Quatre refus sont des blocages contre une <em>adresse de centre de "
          "données</em>. Depuis un réseau domestique ou universitaire, le taux "
          "devrait être plus élevé — <strong>cela n’est pas mesuré.</strong>"),
         ("100 % contre 79 %", "par rapport à Citoid",
          "18 ouvrages tirés au hasard, un seul tirage. Un autre échantillon "
          "peut donner un autre chiffre."),
         ("92,6 % de texte récupéré", "par la reconnaissance de texte",
          "Un article, une série de résolutions, un programme de "
          "reconnaissance. D’autres écritures et langues ne sont pas "
          "vérifiées."),
         ("60 sur 248", "extensions avec une déclaration Android",
          "Ce qu’une extension <em>déclare</em>, non ce qu’elle fait sur un "
          "appareil. Aucune n’a été installée.")]),
    tab2=_tabelle_agenten(
        "Quoi", "Où",
        ["Règles, construction, limites",
         "Tâches ouvertes, lisibles par machine",
         "Tâches ouvertes, pour les humains",
         "Données brutes pour recalculer",
         "Raccordement en une ligne"],
        "Outil " + _OPEN_WORK + " sur <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Chemin", "Durée", "Résultat",
        "Interface avec de vrais clics",
        "annonçait un succès à chaque étape et n’installait "
        "<strong>rien</strong>",
        "Canal du fabricant (Marionette)",
        "installe et désinstalle, signale les erreurs comme des erreurs"),
    regeln=[
        ("<strong>La preuve avant la formulation.</strong> Toute affirmation "
         "de fait a besoin d’une source et d’une date de consultation, sinon "
         "elle devient une opinion, sinon elle saute. Un contrôle l’impose "
         "avant la mise en ligne."),
        ("<strong>Ne pas prêter d’intention à des tiers.</strong> « Le serveur "
         "a répondu 403 » est une observation. « Ils bloquent exprès » est "
         "soumis à la charge de la preuve et n’est pas démontrable."),
        ("<strong>Une comparaison que son propre outil ne peut que gagner est "
         "de la publicité.</strong> C’est pourquoi ce site indique que "
         "l’export d’impression du navigateur gagne sur le texte."),
        ("<strong>Aucun résultat est une erreur, pas une valeur nulle.</strong> "
         "Si une mesure renvoie zéro, c’est d’abord la mesure qui est "
         "suspecte."),
        ("<strong>Les données brutes ne sont pas lissées.</strong> Une "
         "correction est nommée comme correction, non intégrée en silence."),
    ],
    nicht=[
        ("Pas de contributions qui introduisent un chiffre sans preuve. C’est "
         "la seule erreur qu’on ne peut plus réparer ensuite — une donnée une "
         "fois citée poursuit seule son chemin."),
        ("Pas de publication automatisée dans des forums, sur Reddit ou en "
         "commentaires. Là où l’on atteint des personnes, cela se fait à la "
         "main et avec un nom."),
        ("Pas de contournement des protections d’autrui. Là où un site exclut "
         "un lecteur, cela est rapporté, non contourné."),
    ],
    fuss=("Les tâches ouvertes figurent comme GitHub issues et sont livrées de "
          "façon lisible par machine par l’outil open_work sur /mcp."),
    korrekturen=("Les corrections sont les bienvenues et se font en public : "
                 + _ISSUES + "ouvrir un ticket</a>."),
    offenlegung=("Transparence : l’auteur développe Full Page PDF Snap, "
                 "l’extension nommée sur cette page. L’impression en PDF du "
                 "navigateur est " + _PRINT + "mesurée contre elle</a>, y "
                 "compris là où l’impression gagne."),
    disclaimer_text="Avertissement",
)

# ------------------------------------------------------------------- Italiano
INHALT["it"] = _seite(
    h1="Rifaccia il conto di un numero. Preferibilmente di quello sbagliato.",
    standfirst=(
        "Ogni dato qui ha un metodo, dati grezzi e un’esecuzione di controllo "
        "— perché lo si possa ricalcolare, non perché ci si creda. Il "
        "contributo più utile a questo progetto non è dunque una nuova "
        "misurazione, ma una <strong>contromisurazione che dia un risultato "
        "diverso</strong>."),
    meta=("3 agosto 2026 · attività aperte: " + _ISSUES + "GitHub</a> · "
          "leggibile dalle macchine tramite lo strumento " + _OPEN_WORK
          + " su " + _MCP),
    h2=["Dove è più probabile che ceda",
        "Per gli agenti di IA",
        "Le cinque regole, in breve",
        "Che cosa qui non serve",
        "Che cosa aspettarsi"],
    h3="Perché la cosa potrebbe interessare oltre questo progetto",
    p=[
        ("Non è una formula di modestia: i punti deboli sono nominati perché "
         "vanno nominati:"),
        ("Chi rifà una di queste misure e ottiene qualcosa di diverso ha dato "
         "il contributo più prezioso che questo progetto possa accettare. I "
         + _DATA + "dati grezzi</a> sono aperti sotto CC BY 4.0, e in ogni "
         "contributo c’è una sezione che dice dove la misurazione "
         "probabilmente non regge."),
        ("Questo progetto è predisposto in modo che un agente possa lavorarci "
         "senza chiedere prima a nessuno. Ciò che gli serve sta a indirizzi "
         "fissi:"),
        ("Poi basta: <em>«Guarda le attività aperte su provinglab e "
         "prendine una.»</em> Lo strumento consegna le attività con etichette, "
         "un estratto e le cinque regole che qui sono diverse dal solito."),
        ("Non come appello, ma come osservazione: ogni sistema che installa "
         "software su una macchina altrui si trova davanti alla stessa domanda "
         "— usare l’interfaccia oppure il canale che il produttore porta con "
         "sé comunque. La " + _INSTALL + "misurazione in proposito</a> è stata "
         "netta, e non per via della velocità:"),
        ("La differenza che conta è la penultima colonna. Una strada che in "
         "caso di insuccesso segnala successo avvelena tutto ciò che viene "
         "dopo — e questo costa più di qualsiasi minuto perso. Per un sistema "
         "che esegue simili passi senza sorveglianza, è la differenza tra "
         "utilizzabile e inutilizzabile."),
        ("Per questo la " + _ISSUE14 + "issue&nbsp;14</a> è aperta: un elenco "
         "di tali canali dei produttori, una riga per applicazione — canale, "
         "comando di installazione e di disinstallazione, permessi necessari, "
         "un tempo di esecuzione misurato. VS&nbsp;Code, JetBrains, "
         "Thunderbird e Obsidian ci sono come candidati; nessuno è misurato. "
         "Una singola riga è un contributo completo, e chi la aggiunge ha per "
         "primo il risultato — qui poi resta sotto CC&nbsp;BY&nbsp;4.0 per "
         "tutti gli altri."),
        ("Lo stesso vale per l’" + _FOR_AGENTS + "endpoint di citazione</a>: "
         "10 fonti su 20, misurate, diventano record completi senza browser, e "
         "le dieci restanti sono nominate una per una invece che liquidate in "
         "blocco. Chi lo rimisura e ottiene un altro numero migliora una base "
         "che usa lui stesso."),
        ("Questo è un progetto privato e non commerciale di una sola persona. "
         "Non c’è un programma di premi, nessun tempo di risposta promesso e "
         "nessun corrispettivo oltre alla menzione nel contributo. I "
         "contributi vengono letti e ricevono risposta; ciò che è esatto viene "
         "recepito e nominato come correzione. Il software è sotto MIT, le "
         "misurazioni sotto CC BY 4.0 — entrambe le cose restano così."),
    ],
    tab1=_tabelle_wackelt(
        "Dato", "Perché potrebbe vacillare",
        [("10 fonti su 20", "diventano record di citazione",
          "Quattro rifiuti sono blocchi contro un <em>indirizzo di centro "
          "dati</em>. Da una rete domestica o universitaria la quota dovrebbe "
          "essere più alta — <strong>non è misurato.</strong>"),
         ("100 % contro 79 %", "rispetto a Citoid",
          "18 opere estratte a caso, una sola estrazione. Un altro campione "
          "può dare un altro numero."),
         ("92,6 % di testo recuperato", "dal riconoscimento del testo",
          "Un articolo, una serie di risoluzioni, un programma di "
          "riconoscimento. Altre scritture e lingue non sono verificate."),
         ("60 su 248", "estensioni con dichiarazione Android",
          "Ciò che un’estensione <em>dichiara</em>, non ciò che fa su un "
          "dispositivo. Nessuna è stata installata.")]),
    tab2=_tabelle_agenten(
        "Che cosa", "Dove",
        ["Regole, costruzione, limiti",
         "Attività aperte, leggibili dalle macchine",
         "Attività aperte, per le persone",
         "Dati grezzi per rifare i conti",
         "Collegamento in una riga"],
        "Strumento " + _OPEN_WORK + " su <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Strada", "Durata", "Esito",
        "Interfaccia con clic reali",
        "segnalava successo a ogni passo e installava "
        "<strong>nulla</strong>",
        "Canale del produttore (Marionette)",
        "installa e disinstalla, segnala gli errori come errori"),
    regeln=[
        ("<strong>Prova prima della formulazione.</strong> Ogni affermazione "
         "di fatto ha bisogno di fonte e data di consultazione, oppure diventa "
         "opinione, oppure cade. Un controllo lo impone prima della "
         "pubblicazione."),
        ("<strong>Non attribuire intenzioni a terzi.</strong> «Il server ha "
         "risposto con 403» è un’osservazione. «Bloccano di proposito» è "
         "soggetto a onere della prova e non è dimostrabile."),
        ("<strong>Un confronto che il proprio strumento può solo vincere è "
         "pubblicità.</strong> Per questo su questo sito sta scritto che "
         "l’esportazione di stampa del browser vince sul testo."),
        ("<strong>Nessun risultato è un errore, non un valore zero.</strong> "
         "Se una misurazione restituisce zero, la prima sospettata è la "
         "misurazione."),
        ("<strong>I dati grezzi non si lisciano.</strong> Una correzione viene "
         "nominata come correzione, non incorporata in silenzio."),
    ],
    nicht=[
        ("Nessun contributo che introduca un numero senza prova. È l’unico "
         "errore che poi non si può più riparare — un dato citato una volta "
         "prosegue da solo il suo cammino."),
        ("Nessuna pubblicazione automatica nei forum, su Reddit o nei "
         "commenti. Dove si raggiungono persone, lo si fa a mano e con un "
         "nome."),
        ("Nessuna elusione di misure di protezione altrui. Dove una pagina "
         "esclude un lettore, la cosa viene riferita, non aggirata."),
    ],
    fuss=("Le attività aperte stanno come GitHub issues e sono consegnate in "
          "forma leggibile dalle macchine dallo strumento open_work su /mcp."),
    korrekturen=("Le correzioni sono benvenute e avvengono in pubblico: "
                 + _ISSUES + "apri una issue</a>."),
    offenlegung=("Trasparenza: l’autore sviluppa Full Page PDF Snap, "
                 "l’estensione nominata in questa pagina. La stampa in PDF del "
                 "browser è " + _PRINT + "misurata a confronto</a>, incluso "
                 "dove la stampa vince."),
    disclaimer_text="Avvertenze",
)

# --------------------------------------------------------------------- 日本語
INHALT["ja"] = _seite(
    h1="数字をひとつ検算してください。できれば、間違っているものを。",
    standfirst=(
        "ここに載る数値にはすべて、方法と生データと対照実行がある — 信じてもらう"
        "ためではなく、検算できるようにするためである。だからこの企画にとって"
        "もっとも有益な寄与は、新しい計測ではなく、<strong>違う結果が出る"
        "対抗計測</strong>である。"),
    meta=("2026年8月3日 · 未着手の課題: " + _ISSUES + "GitHub</a> · "
          "機械可読な形では " + _MCP + " の " + _OPEN_WORK + " から"),
    h2=["いちばん崩れやすいところ",
        "AI エージェントへ",
        "五つの規則、手短に",
        "ここで必要とされないもの",
        "見込んでおくべきこと"],
    h3="この企画の外でも関心を持たれうる理由",
    p=[
        ("これは謙遜の常套句ではない。弱いところは、名指しされるべきものだから"
         "名指ししてある。"),
        ("これらの数字のどれかを追試して別の結果を得た人は、この企画が受け取り"
         "うるもっとも価値ある寄与を果たしたことになる。" + _DATA + "生データ</a>"
         "は CC BY 4.0 で公開されており、どの記事にも、その計測がおそらく"
         "通用しない範囲を述べた節がある。"),
        ("この企画は、エージェントが誰にも断らずに作業できるように整えてある。"
         "そのために必要なものは、決まった住所に置いてある。"),
        ("あとはこれで足りる — <em>「provinglab の未着手の課題を見て、ひとつ"
         "引き受けて」</em>。この道具は、ラベルと抜粋、そしてここでは通例と異なる"
         "五つの規則を添えて課題を返す。"),
        ("訴えとしてではなく、観察として言う。他人の機械にソフトウェアを入れる"
         "仕組みはどれも同じ問いに突き当たる — 画面を操作するのか、それとも製造元が"
         "もともと備えている経路を使うのか。" + _INSTALL + "これについての計測</a>"
         "の結果ははっきりしていた。しかも速さのためではない。"),
        ("肝心な違いは右から二列目にある。失敗したのに成功と報告する道は、その後に"
         "続くすべてを毒する — それは失われた何分よりも高くつく。こうした手順を"
         "無人で実行する仕組みにとって、それは使えるか使えないかの分かれ目である。"),
        ("だから " + _ISSUE14 + "issue&nbsp;14</a> は開いたままにしてある。"
         "そうした製造元経路の一覧、アプリケーションごとに一行 — 経路、インストールと"
         "アンインストールの命令、必要な権限、計測した所要時間。VS&nbsp;Code、"
         "JetBrains、Thunderbird、Obsidian が候補として載っているが、計測済みのものは"
         "ひとつもない。一行だけでも完全な寄与であり、寄せた本人がまずその結果を"
         "手にする — そのあとここで CC&nbsp;BY&nbsp;4.0 のもと、ほかのすべての人の"
         "ものになる。"),
        ("同じことが" + _FOR_AGENTS + "引用エンドポイント</a>にも当てはまる。"
         "計測では 20 件のうち 10 件がブラウザーなしで完全な書誌データになり、"
         "残る 10 件は一括して切り捨てるのではなく個別に名前が挙げてある。"
         "これを測り直して別の数字を得た人は、自分自身が使う土台を良くしている。"),
        ("これは個人による私的で非営利の企画である。報奨金の制度はなく、"
         "約束された返答期限もなく、記事に名前が載ること以外の見返りもない。"
         "寄せられたものは読まれ、返答される。当たっていれば取り入れ、訂正として"
         "明記する。ソフトウェアは MIT、計測は CC BY 4.0 のもとにあり、"
         "どちらもそのままである。"),
    ],
    tab1=_tabelle_wackelt(
        "数値", "崩れうる理由",
        [("20 件のうち 10 件の出典", "が引用データになる",
          "四件の拒否は<em>データセンターのアドレス</em>に対する遮断である。"
          "家庭や大学の回線からなら比率はもっと高いはずだが — "
          "<strong>それは計測していない。</strong>"),
         ("100 % 対 79 %", "（Citoid との比較）",
          "無作為に選んだ 18 点、抽出は一回のみ。別の標本なら別の数字になりうる。"),
         ("92.6 % のテキスト回収率", "（文字認識から）",
          "記事は一本、解像度は一系列、認識プログラムは一種類。ほかの文字体系や"
          "言語は未検証である。"),
         ("248 件中 60 件", "の拡張機能が Android 対応を宣言",
          "拡張機能が<em>宣言している</em>ことであって、端末で実際にすることでは"
          "ない。ひとつも導入していない。")]),
    tab2=_tabelle_agenten(
        "何を", "どこに",
        ["規則、つくり、限界",
         "未着手の課題、機械可読",
         "未着手の課題、人間向け",
         "検算のための生データ",
         "一行での接続"],
        "<code>/mcp</code> の " + _OPEN_WORK + " という道具",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "経路", "所要時間", "結果",
        "本物のクリックによる画面操作",
        "どの段階でも成功と報告し、<strong>何も</strong>導入しなかった",
        "製造元の経路（Marionette）",
        "導入も削除もでき、失敗は失敗として報告する",
        dez="."),
    regeln=[
        ("<strong>言い回しより先に典拠を。</strong>事実の主張にはどれも出典と"
         "取得日が要る。なければ意見に格下げされるか、落とされる。公開前に検査が"
         "それを強制する。"),
        ("<strong>第三者の意図を決めつけない。</strong>「サーバーは 403 を返した」"
         "は観察である。「わざと遮断している」は立証責任を負い、しかも立証できない。"),
        ("<strong>自分の道具しか勝ちようのない比較は広告である。</strong>"
         "だからこのサイトには、テキストではブラウザーの印刷書き出しが勝ると"
         "書いてある。"),
        ("<strong>結果が出ないのは誤りであって、ゼロという値ではない。</strong>"
         "計測がゼロを返したら、まず疑うべきは計測のほうである。"),
        ("<strong>生データはならさない。</strong>訂正は訂正として名指しし、"
         "黙って織り込むことはしない。"),
    ],
    nicht=[
        ("典拠のない数字を持ち込む寄与はいらない。それは後から直せない唯一の"
         "誤りである — 一度引用された数値はひとりで歩き出す。"),
        ("掲示板や Reddit、コメント欄への自動投稿はしない。人に届くところでは、"
         "手で、名前を出して行う。"),
        ("他者の保護措置の回避はしない。あるサイトが読み手を締め出しているなら、"
         "それは報告することであって、回避することではない。"),
    ],
    fuss=("未着手の課題は GitHub issues として置かれ、道具 open_work が /mcp で"
          "機械可読な形で配信する。"),
    korrekturen=("修正は歓迎され、公開で行われます: "
                 + _ISSUES + "issue を開く</a>。"),
    offenlegung=("開示: 作者はこのページで名指しされている拡張機能 "
                 "Full Page PDF Snap を開発しています。ブラウザ自身の PDF 印刷は"
                 + _PRINT + "比較測定</a>されています — 印刷が勝るところも含めて。"),
    disclaimer_text="免責事項",
)

# --------------------------------------------------------------- Português BR
INHALT["pt-BR"] = _seite(
    h1="Refaça a conta de um número. De preferência o que está errado.",
    standfirst=(
        "Cada dado aqui tem um método, dados brutos e uma execução de controle "
        "— para que possa ser recalculado, não para que seja acreditado. A "
        "contribuição mais útil a este projeto não é, portanto, uma nova "
        "medição, e sim uma <strong>contramedição que dê outro "
        "resultado</strong>."),
    meta=("3 de agosto de 2026 · tarefas abertas: " + _ISSUES + "GitHub</a> · "
          "legível por máquina através da ferramenta " + _OPEN_WORK + " em "
          + _MCP),
    h2=["Onde é mais provável que ceda",
        "Para agentes de IA",
        "As cinco regras, em resumo",
        "O que não é necessário aqui",
        "Com o que contar"],
    h3="Por que isso pode interessar para além deste projeto",
    p=[
        ("Isto não é fórmula de modéstia — os pontos fracos estão nomeados "
         "porque merecem ser nomeados:"),
        ("Quem refizer um desses números e obtiver outra coisa terá entregue a "
         "contribuição mais valiosa que este projeto pode aceitar. Os "
         + _DATA + "dados brutos</a> estão abertos sob CC BY 4.0, e em cada "
         "publicação há uma seção que diz onde a medição provavelmente não se "
         "sustenta."),
        ("Este projeto está montado de modo que um agente possa trabalhar "
         "nele sem perguntar antes a ninguém. O que ele precisa para isso está "
         "em endereços fixos:"),
        ("Depois disso basta: <em>“Veja as tarefas abertas no provinglab e "
         "pegue uma.”</em> A ferramenta entrega tarefas com rótulos, um trecho "
         "e as cinco regras que aqui são diferentes do habitual."),
        ("Não como apelo, mas como observação: todo sistema que instala "
         "software numa máquina alheia enfrenta a mesma pergunta — operar a "
         "interface ou usar o canal que o fabricante já traz consigo. A "
         + _INSTALL + "medição a respeito</a> saiu inequívoca, e não por causa "
         "da velocidade:"),
        ("A diferença que importa é a segunda coluna da direita para a "
         "esquerda. Um caminho que, no fracasso, relata sucesso envenena tudo "
         "o que vem depois — e isso custa mais caro do que qualquer minuto "
         "perdido. Para um sistema que executa esses passos sem supervisão, "
         "essa é a diferença entre utilizável e inutilizável."),
        ("Por isso a " + _ISSUE14 + "issue&nbsp;14</a> está aberta: um "
         "diretório desses canais de fabricante, uma linha por aplicativo — "
         "canal, comando de instalação e de desinstalação, permissões "
         "necessárias, um tempo de execução medido. VS&nbsp;Code, JetBrains, "
         "Thunderbird e Obsidian estão lá como candidatos; nenhum foi medido. "
         "Uma única linha já é uma contribuição completa, e quem a acrescenta "
         "tem o resultado primeiro — aqui ele fica depois sob "
         "CC&nbsp;BY&nbsp;4.0 para todos os outros."),
        ("O mesmo vale para o " + _FOR_AGENTS + "endpoint de citação</a>: 10 "
         "de 20 fontes medidas viram registros completos sem navegador, e as "
         "dez restantes estão nomeadas uma a uma em vez de descartadas em "
         "bloco. Quem remedir isso e obtiver outro número melhora uma base que "
         "ele mesmo usa."),
        ("Este é um projeto privado e não comercial de uma única pessoa. Não "
         "há programa de recompensas, nem tempo de resposta prometido, nem "
         "contrapartida além da menção na publicação. As contribuições são "
         "lidas e respondidas; o que procede é incorporado e nomeado como "
         "correção. O software está sob MIT, as medições sob CC BY 4.0 — os "
         "dois continuam assim."),
    ],
    tab1=_tabelle_wackelt(
        "Dado", "Por que poderia oscilar",
        [("10 de 20 fontes", "viram registros de citação",
          "Quatro recusas são bloqueios contra um <em>endereço de centro de "
          "dados</em>. A partir de uma rede doméstica ou de campus a taxa "
          "deveria ser maior — <strong>isso não está medido.</strong>"),
         ("100 % contra 79 %", "em comparação com o Citoid",
          "18 obras sorteadas ao acaso, um sorteio. Outra amostra pode dar "
          "outro número."),
         ("92,6 % de texto recuperado", "do reconhecimento de texto",
          "Um artigo, uma série de resoluções, um programa de reconhecimento. "
          "Outras escritas e línguas estão sem verificação."),
         ("60 de 248", "extensões com declaração de Android",
          "O que uma extensão <em>declara</em>, não o que ela faz num "
          "aparelho. Nenhuma foi instalada.")]),
    tab2=_tabelle_agenten(
        "O quê", "Onde",
        ["Regras, construção, limites",
         "Tarefas abertas, legíveis por máquina",
         "Tarefas abertas, para pessoas",
         "Dados brutos para refazer as contas",
         "Conexão em uma linha"],
        "Ferramenta " + _OPEN_WORK + " em <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Caminho", "Duração", "Resultado",
        "Interface com cliques reais",
        "relatou sucesso em cada passo e instalou <strong>nada</strong>",
        "Canal do fabricante (Marionette)",
        "instala e desinstala, relata erros como erros"),
    regeln=[
        ("<strong>Prova antes da formulação.</strong> Toda afirmação de fato "
         "precisa de fonte e data de acesso, ou vira opinião, ou cai fora. Uma "
         "verificação impõe isso antes da entrega."),
        ("<strong>Não atribuir intenção a terceiros.</strong> “O servidor "
         "respondeu com 403” é uma observação. “Eles bloqueiam de propósito” "
         "exige prova e não é demonstrável."),
        ("<strong>Uma comparação que a própria ferramenta só pode vencer é "
         "publicidade.</strong> Por isso está escrito neste site que a "
         "exportação de impressão do navegador vence no texto."),
        ("<strong>Nenhum resultado é um erro, não um valor zero.</strong> Se "
         "uma medição devolve zero, a primeira suspeita é a medição."),
        ("<strong>Dados brutos não são alisados.</strong> Uma correção é "
         "nomeada como correção, não incorporada em silêncio."),
    ],
    nicht=[
        ("Nenhuma contribuição que introduza um número sem prova. Esse é o "
         "único erro que depois não dá mais para consertar — um dado uma vez "
         "citado segue viajando sozinho."),
        ("Nenhuma postagem automatizada em fóruns, no Reddit ou em "
         "comentários. Onde se alcança pessoas, isso acontece à mão e com "
         "nome."),
        ("Nenhuma burla de medidas de proteção alheias. Onde uma página tranca "
         "um leitor do lado de fora, isso é relatado, não contornado."),
    ],
    fuss=("As tarefas abertas ficam como GitHub issues e são entregues de "
          "forma legível por máquina pela ferramenta open_work em /mcp."),
    korrekturen=("Correções são bem-vindas e são feitas em público: "
                 + _ISSUES + "abrir uma issue</a>."),
    offenlegung=("Transparência: o autor desenvolve o Full Page PDF Snap, a "
                 "extensão nomeada nesta página. A impressão em PDF do próprio "
                 "navegador está " + _PRINT + "medida contra ela</a>, "
                 "incluindo onde a impressão vence."),
    disclaimer_text="Aviso legal",
)

# -------------------------------------------------------------------- Русский
INHALT["ru"] = _seite(
    h1="Пересчитайте одно число. Лучше то, которое неверно.",
    standfirst=(
        "У каждой величины здесь есть метод, исходные данные и контрольный "
        "прогон — чтобы её можно было пересчитать, а не чтобы в неё верили. "
        "Поэтому самый полезный вклад в этот проект — не новое измерение, а "
        "<strong>встречное измерение, дающее иной результат</strong>."),
    meta=("3 августа 2026 · открытые задачи: " + _ISSUES + "GitHub</a> · "
          "в машиночитаемом виде через инструмент " + _OPEN_WORK + " на "
          + _MCP),
    h2=["Где вероятнее всего слабое место",
        "Для ИИ-агентов",
        "Пять правил, коротко",
        "Что здесь не нужно",
        "На что рассчитывать"],
    h3="Почему это может быть интересно за пределами проекта",
    p=[
        ("Это не фигура скромности — слабые места названы, потому что им "
         "положено быть названными:"),
        ("Тот, кто повторит одно из этих чисел и получит другое, сделает самый "
         "ценный вклад, какой этот проект может принять. " + _DATA
         + "Исходные данные</a> открыты по CC BY 4.0, и в каждой публикации "
         "есть раздел о том, где измерение, вероятно, не держится."),
        ("Проект устроен так, что агент может работать над ним, никого "
         "предварительно не спрашивая. Всё нужное для этого лежит по "
         "постоянным адресам:"),
        ("Дальше достаточно: <em>«Посмотри открытые задачи на provinglab и "
         "возьми одну.»</em> Инструмент выдаёт задачи с метками, выдержкой и "
         "пятью правилами, которые здесь не такие, как обычно."),
        ("Не как призыв, а как наблюдение: всякая система, которая "
         "устанавливает программу на чужую машину, упирается в один и тот же "
         "вопрос — управлять интерфейсом или использовать канал, который "
         "производитель и так поставляет. " + _INSTALL + "Измерение на этот "
         "счёт</a> оказалось однозначным, и вовсе не из-за скорости:"),
        ("Разница, которая важна, — во втором столбце справа. Путь, который "
         "при неудаче сообщает об успехе, отравляет всё, что идёт следом, — и "
         "это дороже любой потерянной минуты. Для системы, выполняющей такие "
         "шаги без присмотра, это разница между пригодным и непригодным."),
        ("Поэтому " + _ISSUE14 + "issue&nbsp;14</a> открыт: перечень таких "
         "каналов производителей, по строке на приложение — канал, команда "
         "установки и удаления, требуемые права, одно измеренное время "
         "выполнения. VS&nbsp;Code, JetBrains, Thunderbird и Obsidian стоят "
         "там кандидатами, но не измерен ни один. Одна-единственная строка — "
         "это полноценный вклад, и тот, кто её добавит, первым получит "
         "результат — здесь он потом лежит под CC&nbsp;BY&nbsp;4.0 для всех "
         "остальных."),
        ("То же касается " + _FOR_AGENTS + "конечной точки цитирования</a>: "
         "измеренные 10 из 20 источников становятся полными записями без "
         "браузера, а остальные десять названы поимённо, а не отброшены "
         "скопом. Кто перемерит это и получит другое число, улучшит основу, "
         "которой пользуется сам."),
        ("Это частный некоммерческий проект одного человека. Нет программы "
         "вознаграждений, нет обещанного времени ответа и нет иной отдачи, "
         "кроме упоминания в публикации. Присланное читают и на него "
         "отвечают; то, что верно, принимается и называется исправлением. "
         "Программа под MIT, измерения под CC BY 4.0 — и то и другое так и "
         "остаётся."),
    ],
    tab1=_tabelle_wackelt(
        "Величина", "Почему она может шататься",
        [("10 из 20 источников", "становятся записями цитирования",
          "Четыре отказа — это блокировки против <em>адреса центра "
          "обработки данных</em>. Из домашней или университетской сети доля "
          "должна быть выше — <strong>но это не измерено.</strong>"),
         ("100 % против 79 %", "по сравнению с Citoid",
          "18 случайно выбранных работ, одна выборка. Другая выборка может "
          "дать другое число."),
         ("92,6 % извлечённого текста", "из распознавания текста",
          "Одна статья, один ряд разрешений, одна программа распознавания. "
          "Другие письменности и языки не проверены."),
         ("60 из 248", "расширений с указанием Android",
          "То, что расширение <em>объявляет</em>, а не то, что оно делает на "
          "устройстве. Ни одно не устанавливалось.")]),
    tab2=_tabelle_agenten(
        "Что", "Где",
        ["Правила, устройство, границы",
         "Открытые задачи, машиночитаемо",
         "Открытые задачи, для людей",
         "Исходные данные для пересчёта",
         "Подключение в одну строку"],
        "Инструмент " + _OPEN_WORK + " на <code>/mcp</code>",
        "GitHub issues"),
    tab3=_tabelle_weg(
        "Путь", "Время", "Результат",
        "Интерфейс с настоящими щелчками",
        "на каждом шаге сообщал об успехе и не установил "
        "<strong>ничего</strong>",
        "Канал производителя (Marionette)",
        "ставит и удаляет, об ошибках сообщает как об ошибках"),
    regeln=[
        ("<strong>Доказательство прежде формулировки.</strong> Всякому "
         "утверждению о факте нужны источник и дата обращения, иначе оно "
         "становится мнением или выпадает вовсе. Проверка требует этого до "
         "публикации."),
        ("<strong>Не приписывать намерений третьим лицам.</strong> «Сервер "
         "ответил 403» — это наблюдение. «Они блокируют нарочно» требует "
         "доказательства и недоказуемо."),
        ("<strong>Сравнение, в котором собственный инструмент может только "
         "выиграть, — это реклама.</strong> Потому на этом сайте и написано, "
         "что по тексту выигрывает печатный экспорт браузера."),
        ("<strong>Отсутствие результата — это ошибка, а не нулевое "
         "значение.</strong> Если измерение даёт ноль, подозрение падает "
         "сначала на само измерение."),
        ("<strong>Исходные данные не сглаживают.</strong> Исправление "
         "называется исправлением, а не вносится молча."),
    ],
    nicht=[
        ("Не нужны вклады, вводящие число без доказательства. Это та "
         "единственная ошибка, которую потом уже не починить — однажды "
         "процитированная величина дальше идёт сама."),
        ("Никакой автоматической публикации на форумах, в Reddit или в "
         "комментариях. Там, где обращаются к людям, это делается вручную и "
         "под именем."),
        ("Никакого обхода чужих защитных мер. Там, где сайт не пускает "
         "читателя, об этом сообщают, а не обходят это."),
    ],
    fuss=("Открытые задачи стоят как GitHub issues и выдаются в машиночитаемом "
          "виде инструментом open_work на /mcp."),
    korrekturen=("Исправления приветствуются и делаются публично: "
                 + _ISSUES + "открыть issue</a>."),
    offenlegung=("Раскрытие: автор разрабатывает Full Page PDF Snap — "
                 "расширение, названное на этой странице. Собственная печать "
                 "браузера в PDF " + _PRINT + "измерена против неё</a>, "
                 "включая то, где печать выигрывает."),
    disclaimer_text="Отказ от ответственности",
)

# --------------------------------------------------------------------- 简体中文
INHALT["zh-CN"] = _seite(
    h1="请核算其中一个数字。最好是错的那一个。",
    standfirst=(
        "这里的每一项数据都有方法、原始数据和一次对照运行——是为了让人重新算一遍，"
        "而不是为了让人相信。因此，对本项目最有用的贡献不是一次新的测量，而是一次"
        "<strong>算出不同结果的反向测量</strong>。"),
    meta=("2026年8月3日 · 待办任务: " + _ISSUES + "GitHub</a> · 通过 "
          + _MCP + " 上的工具 " + _OPEN_WORK + " 提供机器可读版本"),
    h2=["最可能出问题的地方",
        "致 AI 代理",
        "五条规则，简述",
        "这里不需要什么",
        "该有什么预期"],
    h3="为什么这件事在本项目之外也可能有意思",
    p=[
        ("这不是谦辞——薄弱之处被点名，是因为它们本该被点名："),
        ("谁把这些数字中的任何一个重做一遍并得出别的结果，谁就作出了本项目"
         "所能接受的最有价值的贡献。" + _DATA + "原始数据</a>以 CC BY 4.0 公开，"
         "并且每篇文章都有一节说明该测量大概在哪里站不住脚。"),
        ("本项目的安排使代理无需事先征询任何人便可参与其中。它为此所需的东西"
         "都在固定地址上："),
        ("此后只需一句：<em>“看看 provinglab 上的待办任务，挑一个。”</em>"
         "该工具会连同标签、摘录以及这里有别于惯例的五条规则一起交付任务。"),
        ("不是呼吁，而是观察：凡是在他人机器上安装软件的系统，都会遇到同一个"
         "问题——是操作界面，还是使用厂商本来就提供的通道。"
         + _INSTALL + "关于此事的测量</a>结果毫不含糊，而且原因并不在速度："),
        ("真正要紧的差别在倒数第二列。一条在失败时报告成功的路径，会毒害其后"
         "的一切——这比损失多少分钟都贵。对于无人看管地执行此类步骤的系统而言，"
         "这就是可用与不可用之别。"),
        ("因此 " + _ISSUE14 + "issue&nbsp;14</a> 一直开着：一份此类厂商通道的"
         "清单，每个应用一行——通道、安装与卸载命令、所需权限、一次实测耗时。"
         "VS&nbsp;Code、JetBrains、Thunderbird 和 Obsidian 作为候选列在其中，"
         "却一个也没有测过。单独一行就是一份完整的贡献，提供它的人会最先拿到"
         "结果——随后它在这里以 CC&nbsp;BY&nbsp;4.0 归所有其他人使用。"),
        ("同样的话适用于" + _FOR_AGENTS + "引用端点</a>：实测 20 个来源中有 10 个"
         "无需浏览器即可成为完整记录，其余 10 个也逐一点名，而非笼统带过。"
         "谁重新测量并得到别的数字，谁就改进了自己也在使用的基础。"),
        ("这是一位个人的私人非商业项目。没有赏金计划，没有承诺的响应时间，"
         "除了在文章中署名之外也没有回报。来稿都会被阅读并得到答复；属实的会被"
         "采纳，并作为更正加以说明。软件采用 MIT，测量采用 CC BY 4.0——两者都"
         "保持不变。"),
    ],
    tab1=_tabelle_wackelt(
        "数据", "为什么它可能站不稳",
        [("20 个来源中有 10 个", "成为引用记录",
          "四次拒绝是针对<em>数据中心地址</em>的封锁。从家庭网络或校园网出发，"
          "比例本应更高——<strong>但这没有测量过。</strong>"),
         ("100 % 对 79 %", "（与 Citoid 相比）",
          "随机抽取的 18 部作品，只抽了一次。换一个样本可能得出另一个数字。"),
         ("92.6 % 的文本产出", "来自文字识别",
          "一篇文章、一组分辨率、一个识别程序。其他文字体系和语言未经检验。"),
         ("248 个中有 60 个", "扩展声明支持 Android",
          "这是扩展所<em>声明</em>的内容，而不是它在设备上实际做到的。"
          "一个也没有安装过。")]),
    tab2=_tabelle_agenten(
        "什么", "在哪里",
        ["规则、构造、边界",
         "待办任务，机器可读",
         "待办任务，供人阅读",
         "供核算的原始数据",
         "一行完成接入"],
        "<code>/mcp</code> 上的工具 " + _OPEN_WORK,
        "GitHub issues"),
    tab3=_tabelle_weg(
        "路径", "耗时", "结果",
        "以真实点击操作界面",
        "每一步都报告成功，却<strong>什么也没有</strong>装上",
        "厂商通道（Marionette）",
        "既能安装也能卸载，把错误报告为错误",
        dez="."),
    regeln=[
        ("<strong>先有证据，后有措辞。</strong>每一项事实主张都需要来源和"
         "检索日期，否则它降为意见，或者被删掉。发布前有一道检查强制执行这一点。"),
        ("<strong>不断言第三方的意图。</strong>“服务器返回了 403”是观察。"
         "“他们是故意封锁”负有举证责任，而且无法证明。"),
        ("<strong>自己的工具只可能赢的比较，是广告。</strong>所以本站写明："
         "在文本方面，浏览器的打印导出胜出。"),
        ("<strong>没有结果是一个错误，而不是一个零值。</strong>如果一次测量"
         "给出零，首先可疑的是这次测量本身。"),
        ("<strong>原始数据不作平滑处理。</strong>更正要被称为更正，"
         "而不是悄悄并入。"),
    ],
    nicht=[
        ("不要引入无凭据数字的投稿。那是事后再也修不好的唯一错误——一个数据"
         "一旦被引用，就会自己走下去。"),
        ("不在论坛、Reddit 或评论区做自动发帖。凡是触达真人的地方，都由人手"
         "并且具名进行。"),
        ("不绕过他人的保护措施。凡是网站把读者挡在门外的地方，都如实报告，"
         "而不是绕开。"),
    ],
    fuss=("待办任务以 GitHub issues 形式存在，并由工具 open_work 在 /mcp 上以"
          "机器可读的形式提供。"),
    korrekturen=("欢迎更正，并以公开方式进行: " + _ISSUES + "提交 issue</a>。"),
    offenlegung=("披露: 作者开发了本页提到的扩展 Full Page PDF Snap。"
                 "浏览器自带的打印为 PDF 已" + _PRINT + "与之对比测量</a>，"
                 "包括打印胜出的地方。"),
    disclaimer_text="免责声明",
)
