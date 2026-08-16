#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/notes/sources-a-machine-cannot-cite/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, woertlich uebernommen — kein
build-*.py: vierzehn von vierzehn Buildern weichen von ihrer Seite ab, vier
loeschen Text (tools/builder-drift.py).

Unveraendert in jeder Sprache: Zahlen (20, 10, 1, 4, 5, 403, 4.0), Datums-
werte (3. August 2026), Dateiformate und Datenformate (PDF, HTML, JSON, RIS,
BibTeX), Feld- und Statusnamen (<code>complete: false</code>,
<code>warning</code>), der Schaltflaechenname <em>Cite</em>, Eigennamen
(Full Page PDF Snap, Proving Lab) sowie ALLE Adressen. Der Pruefbefehl steht
als eine Konstante und wird nirgends uebersetzt — er ist Code, keine Prosa;
eine uebersetzte Zahl waere eine andere Messung.

Rendern:  python3 tools/seite-neunsprachig.py texte_zitierbarkeit.py
"""

URL = "https://provinglab.dev/notes/sources-a-machine-cannot-cite/"
ZIEL = "notes/sources-a-machine-cannot-cite/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# Adressen — in jeder Sprache dieselben. Sie hier zu halten schliesst aus, dass
# eine Fassung auf eine andere Seite zeigt als die uebrigen acht.
_MESSUNG = '<a href="/measurements/reading-list-to-bibliography/">'
_SNAP = '<a href="/tools/full-page-pdf-snap/">'
_VERSCHWINDEN = '<a href="/measurements/web-citations-that-vanish/">'
_DATEN = '<a href="/data/2026-08-03-reading-list-to-bibliography.json">'
_ISSUES = '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">'
_DRUCK = '<a href="/measurements/print-to-pdf-vs-screenshot/">'

# Der Pruefbefehl: Code, kein Fliesstext. Die Kommentare bleiben englisch, weil
# sie in der Zwischenablage eines Terminals landen und die Spaltenausrichtung
# jede Uebersetzung zerschlagen wuerde.
_PRUEFUNG = '''<pre><code>curl -sI -A 'my-reader/1.0' "$URL" | head -1     # as a reader
curl -sI -A "$BROWSER_UA"    "$URL" | head -1     # as a browser</code></pre>'''


def _seite(h1, standfirst, meta, h2, p, punkte, fuss, disclaimer):
    """Rumpf der Seite. Struktur einmal, Text neunmal."""
    li = "\n".join(f"  <li>{x}</li>" for x in punkte)
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{meta}</p>
</header>

<p>
  {p[0]}
</p>
<p>
  {p[1]}
</p>

<h2>{h2[0]}</h2>
<p>
  {p[2]}
</p>
<p>
  {p[3]}
</p>
<p>
  {p[4]}
</p>

<h2>{h2[1]}</h2>
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
<p>
  {p[8]}
</p>
<p>
  {p[9]}
</p>
<p>
  {p[10]}
</p>

<h2>{h2[3]}</h2>
<p>
  {p[11]}
</p>
{_PRUEFUNG}
<p>
  {p[12]}
</p>

<h2>{h2[4]}</h2>
<ul>
{li}
</ul>
<footer>
      {fuss[0]}
      <br><br>
      {fuss[1]} <br><br>
      {fuss[2]}
      <br><br>
      <a href="../../">← Proving Lab</a> · <a href="../../disclaimer/">{disclaimer}</a>
    </footer>'''


INHALT = {}

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="The sources a machine cannot cite for you — and how to cite them anyway",
    standfirst=(
        "Of twenty sources in a reading list, ten came back as finished citations and "
        "ten were handed back. Handing them back is the right behaviour. This is what "
        "to do with them, which differs by cause — and only one of the three cases is "
        "solved by opening the page in a browser."),
    meta=("3 August 2026 · from the\n    " + _MESSUNG + "twenty-source\n    "
          "measurement</a>"),
    h2=[
        "Case 1 — the page answers a browser but not a reader",
        "Case 2 — the page refuses everyone from this address",
        "Case 3 — the page answers in full and has nothing to declare",
        "Telling the three apart in one step",
        "What this is not",
    ],
    p=[
        ("Anyone assembling a reference list from web sources meets the same wall "
         "eventually: the automated part stops, and it is not obvious whether the tool "
         "failed, the page is defended, or there was never anything there to collect. "
         "The three look identical from the outside — an empty result — and they need "
         "completely different work. Guessing wrong wastes an afternoon on a page that "
         "will never yield a record, or gives up on one that opens on the first click."),
        ("So the useful question is not <em>how do I get a citation</em>. It is "
         "<em>which of the three is this?</em>"),
        ("<strong>1 of the twenty.</strong> A server-side reader gets 403; a "
         "browser gets the page. This is a bot defence, and it is the only case where "
         "opening the source yourself changes what is available."),
        ("What to do: open it in the browser you already have. Your session, your "
         "network, your institutional access. Then take the source with you before it "
         "changes — a " + _SNAP + "full-page capture</a> writes the page as "
         "one PDF with the URL and the retrieval date on it, which is what a reference "
         "to a web source has to carry anyway. The metadata for the entry is then in "
         "the header of your own file rather than in a service's index."),
        ("Why bother capturing at all, rather than noting the link: because "
         + _VERSCHWINDEN + "we measured what happens to "
         "web sources after they are cited</a>. A URL in a reference list is a promise "
         "about a page you no longer control."),
        ("<strong>4 of the twenty.</strong> 403 to a browser user agent as "
         "readily as to a reader. Here the client is not the problem: requests coming "
         "from a data centre are refused whatever they claim to be. Publishers do this "
         "to deter bulk downloading, and it catches every automated tool equally."),
        ("What to do: nothing clever. Open the page from your own connection, where "
         "these same publishers answer normally, and use their own export — most journal "
         "pages offer <em>Cite</em> → RIS or BibTeX, and that file is better than "
         "anything a reader can reconstruct. If you need the article itself rather than "
         "the entry, that is a library question, not a tooling question."),
        ("The one thing not to do is retry from the same place with a different user "
         "agent. It does not work, and a tool that pretends to be a browser to get past "
         "a rule that is aimed at it is a tool you cannot cite in good conscience."),
        ("<strong>5 of the twenty — the largest group, and the one people "
         "expect least.</strong> Fifty to ninety kilobytes of readable HTML, no defence "
         "of any kind, and no author, no date, no title of a work. A statistics portal "
         "page, a chamber-of-commerce service page, a news article, a software release."),
        ("What to do: write the entry yourself, because the decision the machine cannot "
         "make is <em>what the work is</em>. Is the source the statistics portal page, "
         "the dataset behind it, or the release the portal announces? A citation tool "
         "that answers here has picked one for you without saying so."),
        ("Two things make that manual entry defensible. First, the retrieval date, which "
         "for a page with no publication date is the only date the reference can carry. "
         "Second, the state of the page as you saw it — a "
         + _SNAP + "capture</a> stamped with the URL and the "
         "date, kept with the work. For grey literature and official web pages this is "
         "not belt and braces; a corporate page or an agency portal is rebuilt on no "
         "schedule and with no notice."),
        ("Two requests answer it. If the second succeeds where the first fails, it is "
         "case 1. If both fail, case 2. If both succeed and the record still comes back "
         "<code>complete: false</code>, case 3."),
        ("In an AI workflow the same three cases fall out of the record itself: a "
         "<code>warning</code> naming a wall is case 1 or 2, and "
         "<code>complete: false</code> with no warning is case 3. Which is why the flag "
         "matters more than the title — the "
         + _MESSUNG + "measurement</a> has two "
         "records that carry a title, an author, and no completeness."),
    ],
    punkte=[
        ("<strong>Not a way past a paywall.</strong> Every case above assumes you\n"
         "    have access — your own, or your institution's. Capturing a page you may\n"
         "    read is a copy for your own use; it is not a route to one you may not."),
        ("<strong>Not a replacement for a publisher's export.</strong> Where a\n"
         "    <em>Cite</em> button exists, use it."),
        ("<strong>Not stable.</strong> 4 of these refusals are refusals of\n"
         "    a data centre address and would not reproduce from a home connection. The\n"
         "    " + _DATEN + "data</a> says which."),
    ],
    fuss=[
        ("Follows the twenty-source measurement of 3 August 2026.\n"
         "      Raw data: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Corrections are welcome and are made in public: " + _ISSUES
         + "open an issue</a>. If a figure here is wrong, the data and the script "
           "are published so it can be shown to be wrong."),
        ("Disclosure: the author develops Full Page PDF Snap, the capture extension "
         "linked above. It is one way to do the step it is named for and not the only "
         "one — the browser's own print-to-PDF is compared against it in a "
         + _DRUCK + "published measurement</a>, including the cases where print wins."),
    ],
    disclaimer="Disclaimer",
)

# -------------------------------------------------------------------- Deutsch
INHALT["de"] = _seite(
    h1="Die Quellen, die eine Maschine nicht für Sie zitieren kann — und wie man sie trotzdem zitiert",
    standfirst=(
        "Von zwanzig Quellen einer Leseliste kamen zehn als fertige Zitationen zurück "
        "und zehn wurden zurückgegeben. Sie zurückzugeben ist das richtige Verhalten. "
        "Hier steht, was mit ihnen zu tun ist — und das unterscheidet sich nach "
        "Ursache: Nur einer der drei Fälle löst sich dadurch, dass man die Seite im "
        "Browser öffnet."),
    meta=("3. August 2026 · aus der\n    " + _MESSUNG + "Messung an zwanzig\n    "
          "Quellen</a>"),
    h2=[
        "Fall 1 — die Seite antwortet einem Browser, aber keinem Leseprogramm",
        "Fall 2 — die Seite verweigert sich allen von dieser Adresse",
        "Fall 3 — die Seite antwortet vollständig und hat nichts anzugeben",
        "Die drei in einem Schritt auseinanderhalten",
        "Was das nicht ist",
    ],
    p=[
        ("Wer aus Webquellen ein Literaturverzeichnis zusammenstellt, stößt irgendwann "
         "auf dieselbe Wand: Der automatische Teil hört auf, und es ist nicht "
         "ersichtlich, ob das Werkzeug versagt hat, ob die Seite abgeschirmt ist oder "
         "ob es dort nie etwas zu holen gab. Von außen sehen die drei gleich aus — ein "
         "leeres Ergebnis — und sie verlangen völlig verschiedene Arbeit. Wer falsch "
         "rät, verschwendet einen Nachmittag an eine Seite, die niemals einen Datensatz "
         "hergibt, oder gibt eine auf, die sich beim ersten Klick öffnet."),
        ("Die nützliche Frage lautet deshalb nicht <em>wie komme ich zu einer "
         "Zitation</em>. Sie lautet <em>welcher der drei Fälle ist das?</em>"),
        ("<strong>1 von zwanzig.</strong> Ein serverseitiges Leseprogramm bekommt 403; "
         "ein Browser bekommt die Seite. Das ist eine Bot-Abwehr, und es ist der "
         "einzige Fall, in dem sich etwas ändert, wenn Sie die Quelle selbst öffnen."),
        ("Was zu tun ist: Öffnen Sie sie in dem Browser, den Sie ohnehin haben. Ihre "
         "Sitzung, Ihr Netz, Ihr Hochschulzugang. Nehmen Sie die Quelle dann mit, bevor "
         "sie sich ändert — eine " + _SNAP + "Ganzseitenaufnahme</a> schreibt die Seite "
         "als ein PDF mit der Adresse und dem Abrufdatum darauf, und genau das muss ein "
         "Nachweis auf eine Webquelle ohnehin tragen. Die Angaben für den Eintrag "
         "stehen dann im Kopf Ihrer eigenen Datei statt im Index eines Dienstes."),
        ("Warum überhaupt aufnehmen, statt nur den Link zu notieren: weil "
         + _VERSCHWINDEN + "wir gemessen haben, was mit Webquellen geschieht, nachdem "
         "sie zitiert wurden</a>. Eine Adresse in einem Literaturverzeichnis ist ein "
         "Versprechen über eine Seite, die Sie nicht mehr in der Hand haben."),
        ("<strong>4 von zwanzig.</strong> 403 für eine Browser-Kennung genauso "
         "bereitwillig wie für ein Leseprogramm. Hier ist nicht der Klient das Problem: "
         "Anfragen aus einem Rechenzentrum werden abgewiesen, was immer sie zu sein "
         "behaupten. Verlage tun das, um Massen-Downloads abzuschrecken, und es trifft "
         "jedes automatische Werkzeug gleichermaßen."),
        ("Was zu tun ist: nichts Kunstvolles. Öffnen Sie die Seite über Ihre eigene "
         "Verbindung, wo dieselben Verlage normal antworten, und nutzen Sie deren "
         "eigenen Export — die meisten Zeitschriftenseiten bieten <em>Cite</em> → RIS "
         "oder BibTeX, und diese Datei ist besser als alles, was ein Leseprogramm "
         "rekonstruieren kann. Wenn Sie den Aufsatz selbst brauchen und nicht den "
         "Eintrag, ist das eine Bibliotheksfrage und keine Werkzeugfrage."),
        ("Das Einzige, was man nicht tun sollte, ist, es von derselben Stelle mit einer "
         "anderen Browser-Kennung erneut zu versuchen. Es funktioniert nicht, und ein "
         "Werkzeug, das sich als Browser ausgibt, um an einer Regel vorbeizukommen, die "
         "genau ihm gilt, ist ein Werkzeug, das man nicht guten Gewissens zitieren kann."),
        ("<strong>5 von zwanzig — die größte Gruppe, und die, mit der am wenigsten "
         "gerechnet wird.</strong> Fünfzig bis neunzig Kilobyte lesbares HTML, "
         "keinerlei Abwehr, und kein Verfasser, kein Datum, kein Werktitel. Eine Seite "
         "eines Statistikportals, eine Serviceseite einer Wirtschaftskammer, ein "
         "Nachrichtenartikel, eine Softwareveröffentlichung."),
        ("Was zu tun ist: den Eintrag selbst schreiben, denn die Entscheidung, die die "
         "Maschine nicht treffen kann, ist <em>was das Werk ist</em>. Ist die Quelle "
         "die Seite des Statistikportals, der Datensatz dahinter oder die "
         "Veröffentlichung, die das Portal ankündigt? Ein Zitationswerkzeug, das hier "
         "antwortet, hat eines für Sie ausgewählt, ohne es zu sagen."),
        ("Zweierlei macht diesen Handeintrag belastbar. Erstens das Abrufdatum, das bei "
         "einer Seite ohne Veröffentlichungsdatum das einzige Datum ist, das der "
         "Nachweis tragen kann. Zweitens der Zustand der Seite, wie Sie ihn gesehen "
         "haben — eine " + _SNAP + "Aufnahme</a>, gestempelt mit der Adresse und dem "
         "Datum, bei der Arbeit aufbewahrt. Bei grauer Literatur und amtlichen "
         "Webseiten ist das keine Übervorsicht; eine Unternehmensseite oder ein "
         "Behördenportal wird nach keinem Zeitplan und ohne Ankündigung neu gebaut."),
        ("Zwei Anfragen beantworten es. Gelingt die zweite dort, wo die erste "
         "scheitert, ist es Fall 1. Scheitern beide, Fall 2. Gelingen beide und der "
         "Datensatz kommt trotzdem mit <code>complete: false</code> zurück, Fall 3."),
        ("In einem KI-Arbeitsablauf ergeben sich dieselben drei Fälle aus dem Datensatz "
         "selbst: eine <code>warning</code>, die eine Wand benennt, ist Fall 1 oder 2, "
         "und <code>complete: false</code> ohne Warnung ist Fall 3. Deshalb zählt das "
         "Merkmal mehr als der Titel — die " + _MESSUNG + "Messung</a> hat zwei "
         "Datensätze, die einen Titel und einen Verfasser tragen und keine "
         "Vollständigkeit."),
    ],
    punkte=[
        ("<strong>Kein Weg an einer Bezahlschranke vorbei.</strong> Jeder Fall oben\n"
         "    setzt voraus, dass Sie Zugang haben — Ihren eigenen oder den Ihrer\n"
         "    Einrichtung. Eine Seite aufzunehmen, die Sie lesen dürfen, ist eine Kopie\n"
         "    zum eigenen Gebrauch; ein Weg zu einer, die Sie nicht lesen dürfen, ist es nicht."),
        ("<strong>Kein Ersatz für den Export eines Verlags.</strong> Wo es eine\n"
         "    <em>Cite</em>-Schaltfläche gibt, nutzen Sie sie."),
        ("<strong>Nicht stabil.</strong> 4 dieser Abweisungen sind Abweisungen einer\n"
         "    Rechenzentrums-Adresse und würden sich von einem Privatanschluss aus nicht\n"
         "    wiederholen. Die " + _DATEN + "Daten</a> sagen, welche."),
    ],
    fuss=[
        ("Folgt der Messung an zwanzig Quellen vom 3. August 2026.\n"
         "      Rohdaten: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Korrekturen sind willkommen und werden öffentlich vorgenommen: " + _ISSUES
         + "ein Issue eröffnen</a>. Wenn eine Zahl hier falsch ist, sind die Daten "
           "und das Skript veröffentlicht, damit sich das zeigen lässt."),
        ("Offenlegung: Der Autor entwickelt Full Page PDF Snap, die oben verlinkte "
         "Aufnahme-Erweiterung. Sie ist ein Weg, den Schritt zu tun, nach dem sie "
         "benannt ist, und nicht der einzige — der browsereigene Druck nach PDF wird "
         "ihr in einer " + _DRUCK + "veröffentlichten Messung</a> gegenübergestellt, "
         "samt der Fälle, in denen der Druck gewinnt."),
    ],
    disclaimer="Haftungsausschluss",
)

# -------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Las fuentes que una máquina no puede citar por usted — y cómo citarlas igualmente",
    standfirst=(
        "De veinte fuentes de una lista de lectura, diez volvieron como citas "
        "terminadas y diez fueron devueltas. Devolverlas es el comportamiento correcto. "
        "Esto es lo que hay que hacer con ellas, y difiere según la causa: solo uno de "
        "los tres casos se resuelve abriendo la página en un navegador."),
    meta=("3 de agosto de 2026 · de la\n    " + _MESSUNG + "medición de veinte\n    "
          "fuentes</a>"),
    h2=[
        "Caso 1 — la página responde a un navegador pero no a un lector",
        "Caso 2 — la página rechaza a todos desde esta dirección",
        "Caso 3 — la página responde por completo y no tiene nada que declarar",
        "Distinguir los tres en un solo paso",
        "Lo que esto no es",
    ],
    p=[
        ("Quien reúne una lista de referencias a partir de fuentes web acaba topando "
         "con el mismo muro: la parte automática se detiene y no queda claro si falló "
         "la herramienta, si la página está defendida o si nunca hubo allí nada que "
         "recoger. Los tres se ven idénticos desde fuera — un resultado vacío — y "
         "exigen trabajos completamente distintos. Adivinar mal cuesta una tarde en una "
         "página que jamás dará un registro, o hace abandonar una que se abre al primer "
         "clic."),
        ("Así que la pregunta útil no es <em>cómo consigo una cita</em>. Es "
         "<em>¿cuál de los tres es este?</em>"),
        ("<strong>1 de las veinte.</strong> Un lector del lado del servidor recibe 403; "
         "un navegador recibe la página. Esto es una defensa contra bots, y es el único "
         "caso en el que abrir usted mismo la fuente cambia lo que está disponible."),
        ("Qué hacer: ábrala en el navegador que ya tiene. Su sesión, su red, su acceso "
         "institucional. Después llévese la fuente antes de que cambie — una "
         + _SNAP + "captura de página completa</a> escribe la página como un único PDF "
         "con la dirección y la fecha de consulta encima, que es lo que una referencia "
         "a una fuente web tiene que llevar de todos modos. Los datos de la entrada "
         "están entonces en la cabecera de su propio archivo y no en el índice de un "
         "servicio."),
        ("Por qué capturar en absoluto, en lugar de anotar el enlace: porque "
         + _VERSCHWINDEN + "hemos medido qué les ocurre a las fuentes web después de "
         "ser citadas</a>. Una dirección en una lista de referencias es una promesa "
         "sobre una página que usted ya no controla."),
        ("<strong>4 de las veinte.</strong> 403 a un agente de usuario de navegador con "
         "la misma prontitud que a un lector. Aquí el cliente no es el problema: las "
         "peticiones que llegan desde un centro de datos se rechazan digan lo que digan "
         "ser. Las editoriales lo hacen para disuadir la descarga masiva, y alcanza por "
         "igual a toda herramienta automática."),
        ("Qué hacer: nada ingenioso. Abra la página desde su propia conexión, donde "
         "esas mismas editoriales responden con normalidad, y use su propia exportación "
         "— la mayoría de las páginas de revistas ofrecen <em>Cite</em> → RIS o BibTeX, "
         "y ese archivo es mejor que cualquier cosa que un lector pueda reconstruir. Si "
         "necesita el artículo en sí y no la entrada, eso es una cuestión de biblioteca "
         "y no de herramientas."),
        ("Lo único que no hay que hacer es reintentar desde el mismo sitio con otro "
         "agente de usuario. No funciona, y una herramienta que finge ser un navegador "
         "para sortear una regla dirigida precisamente a ella es una herramienta que no "
         "se puede citar en conciencia."),
        ("<strong>5 de las veinte — el grupo más grande, y el que menos se "
         "espera.</strong> Cincuenta a noventa kilobytes de HTML legible, ninguna "
         "defensa de ningún tipo, y ningún autor, ninguna fecha, ningún título de obra. "
         "Una página de un portal de estadística, una página de servicios de una cámara "
         "de comercio, un artículo periodístico, una versión de software."),
        ("Qué hacer: escribir la entrada usted mismo, porque la decisión que la máquina "
         "no puede tomar es <em>cuál es la obra</em>. ¿Es la fuente la página del "
         "portal de estadística, el conjunto de datos que hay detrás, o la versión que "
         "el portal anuncia? Una herramienta de citación que responda aquí ha elegido "
         "una por usted sin decirlo."),
        ("Dos cosas hacen defendible esa entrada manual. Primera, la fecha de consulta, "
         "que en una página sin fecha de publicación es la única fecha que la "
         "referencia puede llevar. Segunda, el estado de la página tal como usted la "
         "vio — una " + _SNAP + "captura</a> sellada con la dirección y la fecha, "
         "guardada junto al trabajo. Para la literatura gris y las páginas web "
         "oficiales esto no es exceso de celo; una página corporativa o un portal de "
         "una administración se rehace sin calendario y sin aviso."),
        ("Dos peticiones lo responden. Si la segunda tiene éxito donde la primera "
         "falla, es el caso 1. Si fallan las dos, caso 2. Si las dos tienen éxito y el "
         "registro sigue volviendo con <code>complete: false</code>, caso 3."),
        ("En un flujo de trabajo de IA los mismos tres casos se desprenden del propio "
         "registro: una <code>warning</code> que nombra un muro es el caso 1 o 2, y "
         "<code>complete: false</code> sin advertencia es el caso 3. Por eso el "
         "indicador importa más que el título — la " + _MESSUNG + "medición</a> tiene "
         "dos registros que llevan título, autor y ninguna completitud."),
    ],
    punkte=[
        ("<strong>No es una vía para saltarse un muro de pago.</strong> Todos los\n"
         "    casos anteriores dan por supuesto que usted tiene acceso: el suyo o el de\n"
         "    su institución. Capturar una página que puede leer es una copia para uso\n"
         "    propio; no es una ruta hacia una que no puede leer."),
        ("<strong>No es un sustituto de la exportación de una editorial.</strong> Donde\n"
         "    exista un botón <em>Cite</em>, úselo."),
        ("<strong>No es estable.</strong> 4 de estos rechazos son rechazos a una\n"
         "    dirección de centro de datos y no se reproducirían desde una conexión\n"
         "    doméstica. Los " + _DATEN + "datos</a> dicen cuáles."),
    ],
    fuss=[
        ("Sigue a la medición de veinte fuentes del 3 de agosto de 2026.\n"
         "      Datos brutos: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Las correcciones son bienvenidas y se hacen en público: " + _ISSUES
         + "abrir una incidencia</a>. Si una cifra de aquí está mal, los datos y el "
           "script están publicados para que pueda demostrarse."),
        ("Divulgación: el autor desarrolla Full Page PDF Snap, la extensión de captura "
         "enlazada arriba. Es una manera de dar el paso al que debe su nombre, y no la "
         "única — la impresión a PDF propia del navegador se compara con ella en una "
         + _DRUCK + "medición publicada</a>, incluidos los casos en los que gana la "
         "impresión."),
    ],
    disclaimer="Aviso legal",
)

# ------------------------------------------------------------------- Français
INHALT["fr"] = _seite(
    h1="Les sources qu'une machine ne peut pas citer à votre place — et comment les citer quand même",
    standfirst=(
        "Sur vingt sources d'une liste de lecture, dix sont revenues sous forme de "
        "citations achevées et dix ont été rendues. Les rendre est le bon comportement. "
        "Voici ce qu'il faut en faire, et cela diffère selon la cause : un seul des "
        "trois cas se règle en ouvrant la page dans un navigateur."),
    meta=("3 août 2026 · d'après la\n    " + _MESSUNG + "mesure sur vingt\n    "
          "sources</a>"),
    h2=[
        "Cas 1 — la page répond à un navigateur mais pas à un lecteur",
        "Cas 2 — la page refuse tout le monde depuis cette adresse",
        "Cas 3 — la page répond intégralement et n'a rien à déclarer",
        "Distinguer les trois en une seule étape",
        "Ce que ce n'est pas",
    ],
    p=[
        ("Quiconque constitue une bibliographie à partir de sources web finit par se "
         "heurter au même mur : la partie automatique s'arrête, et l'on ne voit pas si "
         "l'outil a échoué, si la page est protégée, ou s'il n'y a jamais rien eu à y "
         "recueillir. Vus de l'extérieur, les trois cas sont identiques — un résultat "
         "vide — et ils demandent un travail entièrement différent. Se tromper de "
         "diagnostic coûte un après-midi sur une page qui ne livrera jamais de notice, "
         "ou fait renoncer à une page qui s'ouvre au premier clic."),
        ("La question utile n'est donc pas <em>comment obtenir une citation</em>. Elle "
         "est <em>lequel des trois cas est-ce ?</em>"),
        ("<strong>1 sur les vingt.</strong> Un lecteur côté serveur reçoit 403 ; un "
         "navigateur reçoit la page. C'est une défense contre les robots, et c'est le "
         "seul cas où ouvrir la source soi-même change ce qui est disponible."),
        ("Que faire : l'ouvrir dans le navigateur que vous avez déjà. Votre session, "
         "votre réseau, votre accès institutionnel. Emportez ensuite la source avant "
         "qu'elle ne change — une " + _SNAP + "capture pleine page</a> écrit la page en "
         "un seul PDF portant l'adresse et la date de consultation, ce qu'une référence "
         "à une source web doit de toute façon porter. Les métadonnées de la notice se "
         "trouvent alors dans l'en-tête de votre propre fichier plutôt que dans l'index "
         "d'un service."),
        ("Pourquoi capturer, plutôt que noter le lien : parce que "
         + _VERSCHWINDEN + "nous avons mesuré ce qu'il advient des sources web après "
         "leur citation</a>. Une adresse dans une bibliographie est une promesse "
         "portant sur une page que vous ne maîtrisez plus."),
        ("<strong>4 sur les vingt.</strong> 403 à un agent utilisateur de navigateur "
         "aussi volontiers qu'à un lecteur. Ici le client n'est pas en cause : les "
         "requêtes venant d'un centre de données sont refusées quoi qu'elles "
         "prétendent être. Les éditeurs procèdent ainsi pour décourager le "
         "téléchargement en masse, et cela frappe également tout outil automatique."),
        ("Que faire : rien d'ingénieux. Ouvrez la page depuis votre propre connexion, "
         "où ces mêmes éditeurs répondent normalement, et servez-vous de leur export — "
         "la plupart des pages de revues proposent <em>Cite</em> → RIS ou BibTeX, et ce "
         "fichier vaut mieux que tout ce qu'un lecteur peut reconstituer. S'il vous "
         "faut l'article lui-même et non la notice, c'est une question de bibliothèque, "
         "pas d'outillage."),
        ("La seule chose à ne pas faire est de réessayer depuis le même endroit avec un "
         "autre agent utilisateur. Cela ne marche pas, et un outil qui se fait passer "
         "pour un navigateur afin de contourner une règle qui le vise précisément est "
         "un outil que l'on ne peut pas citer en conscience."),
        ("<strong>5 sur les vingt — le groupe le plus important, et celui auquel on "
         "s'attend le moins.</strong> Cinquante à quatre-vingt-dix kilooctets de HTML "
         "lisible, aucune défense d'aucune sorte, et pas d'auteur, pas de date, pas de "
         "titre d'œuvre. Une page de portail statistique, une page de services d'une "
         "chambre de commerce, un article de presse, une version de logiciel."),
        ("Que faire : rédiger la notice vous-même, car la décision que la machine ne "
         "peut pas prendre est <em>ce qu'est l'œuvre</em>. La source est-elle la page "
         "du portail statistique, le jeu de données derrière elle, ou la version que le "
         "portail annonce ? Un outil de citation qui répond ici en a choisi une pour "
         "vous sans le dire."),
        ("Deux choses rendent cette notice manuelle défendable. D'abord la date de "
         "consultation, qui, pour une page sans date de publication, est la seule date "
         "que la référence puisse porter. Ensuite l'état de la page tel que vous l'avez "
         "vu — une " + _SNAP + "capture</a> estampillée de l'adresse et de la date, "
         "conservée avec le travail. Pour la littérature grise et les pages web "
         "officielles, ce n'est pas un luxe : une page d'entreprise ou un portail "
         "administratif est refait sans calendrier et sans préavis."),
        ("Deux requêtes y répondent. Si la seconde réussit là où la première échoue, "
         "c'est le cas 1. Si les deux échouent, cas 2. Si les deux réussissent et que "
         "la notice revient tout de même avec <code>complete: false</code>, cas 3."),
        ("Dans un flux de travail d'IA, les mêmes trois cas ressortent de la notice "
         "elle-même : un <code>warning</code> nommant un mur, c'est le cas 1 ou 2, et "
         "<code>complete: false</code> sans avertissement, c'est le cas 3. C'est "
         "pourquoi l'indicateur compte plus que le titre — la " + _MESSUNG + "mesure</a> "
         "comporte deux notices qui portent un titre, un auteur, et aucune complétude."),
    ],
    punkte=[
        ("<strong>Pas un moyen de franchir un péage.</strong> Chaque cas ci-dessus\n"
         "    suppose que vous avez l'accès — le vôtre, ou celui de votre établissement.\n"
         "    Capturer une page que vous avez le droit de lire est une copie pour votre\n"
         "    usage propre ; ce n'est pas une voie vers une page que vous n'avez pas le\n"
         "    droit de lire."),
        ("<strong>Pas un remplacement de l'export d'un éditeur.</strong> Là où un\n"
         "    bouton <em>Cite</em> existe, utilisez-le."),
        ("<strong>Pas stable.</strong> 4 de ces refus sont des refus opposés à une\n"
         "    adresse de centre de données et ne se reproduiraient pas depuis une\n"
         "    connexion domestique. Les " + _DATEN + "données</a> disent lesquels."),
    ],
    fuss=[
        ("Fait suite à la mesure sur vingt sources du 3 août 2026.\n"
         "      Données brutes : " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Les corrections sont bienvenues et sont faites en public : " + _ISSUES
         + "ouvrir un ticket</a>. Si un chiffre est faux ici, les données et le "
           "script sont publiés pour qu'on puisse le démontrer."),
        ("Divulgation : l'auteur développe Full Page PDF Snap, l'extension de capture "
         "liée ci-dessus. C'est une façon d'accomplir l'étape dont elle porte le nom, "
         "et non la seule — l'impression en PDF propre au navigateur lui est comparée "
         "dans une " + _DRUCK + "mesure publiée</a>, y compris les cas où l'impression "
         "l'emporte."),
    ],
    disclaimer="Avertissement",
)

# ------------------------------------------------------------------- Italiano
INHALT["it"] = _seite(
    h1="Le fonti che una macchina non può citare al posto vostro — e come citarle lo stesso",
    standfirst=(
        "Di venti fonti di una lista di letture, dieci sono tornate come citazioni "
        "complete e dieci sono state restituite. Restituirle è il comportamento "
        "corretto. Ecco cosa farne, e varia secondo la causa: solo uno dei tre casi si "
        "risolve aprendo la pagina in un browser."),
    meta=("3 agosto 2026 · dalla\n    " + _MESSUNG + "misurazione su venti\n    "
          "fonti</a>"),
    h2=[
        "Caso 1 — la pagina risponde a un browser ma non a un lettore",
        "Caso 2 — la pagina rifiuta chiunque da questo indirizzo",
        "Caso 3 — la pagina risponde per intero e non ha nulla da dichiarare",
        "Distinguere i tre in un solo passo",
        "Cosa non è",
    ],
    p=[
        ("Chi mette insieme una bibliografia partendo da fonti web prima o poi incontra "
         "lo stesso muro: la parte automatica si ferma e non si capisce se lo strumento "
         "abbia fallito, se la pagina sia difesa, o se lì non ci sia mai stato nulla da "
         "raccogliere. Dall'esterno i tre casi sono identici — un risultato vuoto — e "
         "richiedono un lavoro completamente diverso. Sbagliare la diagnosi costa un "
         "pomeriggio su una pagina che non darà mai un record, oppure fa rinunciare a "
         "una che si apre al primo clic."),
        ("La domanda utile non è quindi <em>come ottengo una citazione</em>. È "
         "<em>quale dei tre è questo?</em>"),
        ("<strong>1 delle venti.</strong> Un lettore lato server riceve 403; un browser "
         "riceve la pagina. Questa è una difesa contro i bot, ed è l'unico caso in cui "
         "aprire la fonte di persona cambia ciò che è disponibile."),
        ("Cosa fare: apritela nel browser che avete già. La vostra sessione, la vostra "
         "rete, il vostro accesso istituzionale. Poi portatevi via la fonte prima che "
         "cambi — una " + _SNAP + "cattura a pagina intera</a> scrive la pagina come un "
         "unico PDF con l'indirizzo e la data di consultazione sopra, che è ciò che un "
         "riferimento a una fonte web deve comunque portare. I dati per la voce si "
         "trovano allora nell'intestazione del vostro file e non nell'indice di un "
         "servizio."),
        ("Perché catturare, invece di annotare soltanto il link: perché "
         + _VERSCHWINDEN + "abbiamo misurato cosa succede alle fonti web dopo che sono "
         "state citate</a>. Un indirizzo in una bibliografia è una promessa su una "
         "pagina che non controllate più."),
        ("<strong>4 delle venti.</strong> 403 a uno user agent da browser con la stessa "
         "prontezza con cui lo dà a un lettore. Qui il problema non è il client: le "
         "richieste che arrivano da un centro dati vengono rifiutate qualunque cosa "
         "dichiarino di essere. Gli editori lo fanno per scoraggiare lo scaricamento di "
         "massa, e colpisce allo stesso modo ogni strumento automatico."),
        ("Cosa fare: niente di ingegnoso. Aprite la pagina dalla vostra connessione, "
         "dove quegli stessi editori rispondono normalmente, e usate la loro "
         "esportazione — la maggior parte delle pagine di riviste offre <em>Cite</em> → "
         "RIS o BibTeX, e quel file è migliore di qualunque cosa un lettore possa "
         "ricostruire. Se vi serve l'articolo e non la voce, è una questione di "
         "biblioteca, non di strumenti."),
        ("L'unica cosa da non fare è riprovare dallo stesso posto con un altro user "
         "agent. Non funziona, e uno strumento che finge di essere un browser per "
         "aggirare una regola rivolta proprio a lui è uno strumento che non si può "
         "citare in coscienza."),
        ("<strong>5 delle venti — il gruppo più numeroso, e quello che meno ci si "
         "aspetta.</strong> Da cinquanta a novanta kilobyte di HTML leggibile, nessuna "
         "difesa di alcun tipo, e nessun autore, nessuna data, nessun titolo di "
         "un'opera. La pagina di un portale statistico, la pagina di servizi di una "
         "camera di commercio, un articolo di giornale, una versione di software."),
        ("Cosa fare: scrivere la voce da soli, perché la decisione che la macchina non "
         "può prendere è <em>quale sia l'opera</em>. La fonte è la pagina del portale "
         "statistico, il set di dati dietro di essa, o la versione che il portale "
         "annuncia? Uno strumento di citazione che qui risponde ne ha scelta una per "
         "voi senza dirlo."),
        ("Due cose rendono difendibile quella voce manuale. Primo, la data di "
         "consultazione, che per una pagina senza data di pubblicazione è l'unica data "
         "che il riferimento possa portare. Secondo, lo stato della pagina come l'avete "
         "visto — una " + _SNAP + "cattura</a> timbrata con l'indirizzo e la data, "
         "conservata insieme al lavoro. Per la letteratura grigia e le pagine web "
         "ufficiali questa non è prudenza eccessiva; una pagina aziendale o un portale "
         "di un ente vengono rifatti senza calendario e senza preavviso."),
        ("Due richieste rispondono alla domanda. Se la seconda riesce dove la prima "
         "fallisce, è il caso 1. Se falliscono entrambe, caso 2. Se riescono entrambe e "
         "il record torna comunque con <code>complete: false</code>, caso 3."),
        ("In un flusso di lavoro con IA gli stessi tre casi emergono dal record stesso: "
         "un <code>warning</code> che nomina un muro è il caso 1 o 2, e "
         "<code>complete: false</code> senza avviso è il caso 3. Per questo il "
         "contrassegno conta più del titolo — la " + _MESSUNG + "misurazione</a> ha due "
         "record che portano un titolo, un autore e nessuna completezza."),
    ],
    punkte=[
        ("<strong>Non è un modo per superare un paywall.</strong> Ogni caso qui sopra\n"
         "    presuppone che abbiate accesso — il vostro, o quello della vostra\n"
         "    istituzione. Catturare una pagina che potete leggere è una copia per uso\n"
         "    personale; non è una via verso una che non potete leggere."),
        ("<strong>Non è un sostituto dell'esportazione di un editore.</strong> Dove\n"
         "    esiste un pulsante <em>Cite</em>, usatelo."),
        ("<strong>Non è stabile.</strong> 4 di questi rifiuti sono rifiuti verso un\n"
         "    indirizzo di centro dati e non si riprodurrebbero da una connessione\n"
         "    domestica. I " + _DATEN + "dati</a> dicono quali."),
    ],
    fuss=[
        ("Segue la misurazione su venti fonti del 3 agosto 2026.\n"
         "      Dati grezzi: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Le correzioni sono benvenute e vengono fatte in pubblico: " + _ISSUES
         + "aprire una segnalazione</a>. Se una cifra qui è sbagliata, i dati e lo "
           "script sono pubblicati perché lo si possa dimostrare."),
        ("Dichiarazione: l'autore sviluppa Full Page PDF Snap, l'estensione di cattura "
         "collegata sopra. È un modo di compiere il passo da cui prende il nome e non "
         "l'unico — la stampa in PDF propria del browser le viene confrontata in una "
         + _DRUCK + "misurazione pubblicata</a>, compresi i casi in cui vince la stampa."),
    ],
    disclaimer="Avvertenze legali",
)

# --------------------------------------------------------------------- 日本語
INHALT["ja"] = _seite(
    h1="機械があなたに代わって引用できない情報源 — それでも引用する方法",
    standfirst=(
        "文献リストの20件の情報源のうち、10件は完成した引用として返り、10件は差し戻された。"
        "差し戻すことは正しい振る舞いである。ここでは、それらをどう扱うかを述べる。"
        "扱いは原因によって異なり、ブラウザでページを開けば片づくのは三つのうち一つだけである。"),
    meta=("2026年8月3日 ·\n    " + _MESSUNG + "20件の情報源による\n    測定</a>より"),
    h2=[
        "ケース 1 — ページはブラウザには答えるが読み取り側には答えない",
        "ケース 2 — ページはこのアドレスからの誰をも拒む",
        "ケース 3 — ページは完全に応答し、申告するものが何もない",
        "三つを一手で見分ける",
        "これは何ではないか",
    ],
    p=[
        ("ウェブ上の情報源から参考文献一覧を組み立てる人は、いずれ同じ壁に突き当たる。"
         "自動処理が止まり、道具が失敗したのか、ページが防御されているのか、"
         "そもそもそこに集めるものが何もなかったのかが分からない。"
         "外から見ればこの三つは同じ——空の結果——に見えるが、必要な作業はまったく違う。"
         "取り違えれば、決して記録を出さないページに午後を丸ごと費やすか、"
         "最初のクリックで開くページをあきらめることになる。"),
        ("したがって役に立つ問いは<em>どうすれば引用が得られるか</em>ではない。"
         "<em>これは三つのうちどれか</em>である。"),
        ("<strong>20件のうち 1 件。</strong>サーバー側の読み取りには 403 が返り、"
         "ブラウザにはページが返る。これはボット対策であり、"
         "自分で情報源を開くことで得られるものが変わる唯一の場合である。"),
        ("すべきこと：すでに手元にあるブラウザで開く。自分のセッション、自分の回線、"
         "自分の機関アクセスで。そしてページが変わる前に情報源を持ち帰る——"
         + _SNAP + "全ページ取り込み</a>は、アドレスと取得日を記した一つの PDF として"
         "ページを書き出す。ウェブ情報源への参照はいずれにせよそれを備えていなければならない。"
         "項目のための書誌事項は、サービスの索引ではなく自分のファイルのヘッダーに載ることになる。"),
        ("リンクを控えるだけでなく、そもそもなぜ取り込むのか。"
         + _VERSCHWINDEN + "引用されたあとウェブ情報源に何が起きるかを測定した</a>からである。"
         "参考文献一覧の中のアドレスは、もはや自分の手の内にないページについての約束である。"),
        ("<strong>20件のうち 4 件。</strong>ブラウザのユーザーエージェントにも、"
         "読み取り側と同じくらいあっさりと 403 を返す。ここではクライアントが問題なのではない。"
         "データセンターから来る要求は、何を名乗ろうと拒まれる。"
         "出版社は大量ダウンロードを抑止するためにこれを行い、"
         "あらゆる自動化された道具が等しく巻き添えになる。"),
        ("すべきこと：小細工はしない。同じ出版社が普通に応答する自分の回線からページを開き、"
         "出版社自身の書き出しを使う。多くの学術誌ページは <em>Cite</em> → RIS または "
         "BibTeX を備えており、そのファイルは読み取り側が再構成できるどんなものより優れている。"
         "項目ではなく論文そのものが必要なら、それは道具の問題ではなく図書館の問題である。"),
        ("してはならない唯一のことは、同じ場所から別のユーザーエージェントで再試行することである。"
         "効き目はないし、まさに自分に向けられた規則をすり抜けるためにブラウザのふりをする道具は、"
         "良心をもって引用できる道具ではない。"),
        ("<strong>20件のうち 5 件 — 最も大きな群であり、最も予想されていない群である。</strong>"
         "読み取り可能な HTML が 50 から 90 キロバイト、いかなる防御もなく、著者もなく、"
         "日付もなく、著作の標題もない。統計ポータルのページ、商工会議所のサービスページ、"
         "報道記事、ソフトウェアのリリース。"),
        ("すべきこと：項目を自分で書く。機械が下せない判断は<em>何が著作なのか</em>だからである。"
         "情報源は統計ポータルのページなのか、その背後のデータセットなのか、"
         "ポータルが告知しているリリースなのか。ここで答えを返す引用ツールは、"
         "そうと言わずに一つを選んでしまっている。"),
        ("その手書きの項目を弁明可能にするものが二つある。第一に取得日。"
         "公開日のないページにとって、参照が備えうる唯一の日付である。"
         "第二に、自分が見たとおりのページの状態——アドレスと日付を刻印した"
         + _SNAP + "取り込み</a>を、成果物とともに保管する。"
         "灰色文献や公的なウェブページでは、これは念の入れすぎではない。"
         "企業のページや官庁のポータルは、予定もなく予告もなく作り替えられる。"),
        ("二つの要求で答えが出る。一つ目が失敗し二つ目が成功すればケース 1。"
         "両方とも失敗すればケース 2。両方とも成功してなお記録が "
         "<code>complete: false</code> で返るならケース 3。"),
        ("AI の作業手順では、同じ三つの場合が記録そのものから導かれる。"
         "壁を名指しする <code>warning</code> があればケース 1 か 2、"
         "警告なしの <code>complete: false</code> はケース 3 である。"
         "だからこそ標題よりもこの印のほうが重い——" + _MESSUNG + "測定</a>には、"
         "標題と著者を備えながら完全性を欠く記録が二件ある。"),
    ],
    punkte=[
        ("<strong>有料の壁を越える手段ではない。</strong>上のどの場合も、\n"
         "    自分自身のあるいは所属機関のアクセス権があることを前提としている。\n"
         "    読んでよいページを取り込むのは私的使用のための複製であり、\n"
         "    読んではならないページへの経路ではない。"),
        ("<strong>出版社の書き出しの代わりではない。</strong>\n"
         "    <em>Cite</em> ボタンがあるなら、それを使うこと。"),
        ("<strong>不変ではない。</strong>これらの拒否のうち 4 件は\n"
         "    データセンターのアドレスに対する拒否であり、家庭の回線からは再現しないだろう。\n"
         "    どれがそうかは" + _DATEN + "データ</a>が示している。"),
    ],
    fuss=[
        ("2026年8月3日の20件の情報源による測定に続くもの。\n"
         "      生データ：" + _DATEN + "JSON</a>、CC BY 4.0。"),
        ("訂正は歓迎し、公開の場で行う：" + _ISSUES
         + "issue を開く</a>。ここに誤った数値があれば、"
           "それを示せるようにデータとスクリプトが公開されている。"),
        ("開示：著者は上でリンクした取り込み拡張機能 Full Page PDF Snap を開発している。"
         "それは名前が示す工程を行う一つの方法であって唯一の方法ではない——"
         "ブラウザ自身の PDF 印刷との比較は" + _DRUCK + "公開された測定</a>にあり、"
         "印刷のほうが勝る場合も含めて示している。"),
    ],
    disclaimer="免責事項",
)

# ---------------------------------------------------------- Português (Brasil)
INHALT["pt-BR"] = _seite(
    h1="As fontes que uma máquina não consegue citar por você — e como citá-las mesmo assim",
    standfirst=(
        "De vinte fontes de uma lista de leitura, dez voltaram como citações prontas e "
        "dez foram devolvidas. Devolvê-las é o comportamento certo. Aqui está o que "
        "fazer com elas, e isso varia conforme a causa: apenas um dos três casos se "
        "resolve abrindo a página em um navegador."),
    meta=("3 de agosto de 2026 · da\n    " + _MESSUNG + "medição de vinte\n    "
          "fontes</a>"),
    h2=[
        "Caso 1 — a página responde a um navegador, mas não a um leitor",
        "Caso 2 — a página recusa todo mundo a partir deste endereço",
        "Caso 3 — a página responde por inteiro e não tem nada a declarar",
        "Distinguir os três em um passo",
        "O que isto não é",
    ],
    p=[
        ("Quem monta uma lista de referências a partir de fontes da web acaba "
         "esbarrando no mesmo muro: a parte automática para, e não fica claro se a "
         "ferramenta falhou, se a página está protegida ou se nunca houve nada ali para "
         "recolher. Vistos de fora, os três são idênticos — um resultado vazio — e "
         "exigem trabalhos completamente diferentes. Errar o diagnóstico custa uma "
         "tarde em uma página que jamais entregará um registro, ou faz desistir de uma "
         "que abre no primeiro clique."),
        ("Portanto, a pergunta útil não é <em>como consigo uma citação</em>. É "
         "<em>qual dos três é este?</em>"),
        ("<strong>1 das vinte.</strong> Um leitor do lado do servidor recebe 403; um "
         "navegador recebe a página. Isso é uma defesa contra robôs, e é o único caso "
         "em que abrir a fonte você mesmo muda o que está disponível."),
        ("O que fazer: abra-a no navegador que você já tem. Sua sessão, sua rede, seu "
         "acesso institucional. Depois leve a fonte com você antes que ela mude — uma "
         + _SNAP + "captura de página inteira</a> grava a página como um único PDF com "
         "o endereço e a data de acesso nele, que é o que uma referência a uma fonte da "
         "web precisa carregar de qualquer forma. Os dados da entrada ficam então no "
         "cabeçalho do seu próprio arquivo, e não no índice de um serviço."),
        ("Por que capturar, em vez de apenas anotar o link: porque "
         + _VERSCHWINDEN + "medimos o que acontece com as fontes da web depois de "
         "citadas</a>. Um endereço numa lista de referências é uma promessa sobre uma "
         "página que você não controla mais."),
        ("<strong>4 das vinte.</strong> 403 para um agente de usuário de navegador com "
         "a mesma prontidão que para um leitor. Aqui o cliente não é o problema: "
         "pedidos vindos de um centro de dados são recusados, seja lá o que afirmem "
         "ser. As editoras fazem isso para desestimular o download em massa, e isso "
         "atinge igualmente toda ferramenta automatizada."),
        ("O que fazer: nada de engenhoso. Abra a página pela sua própria conexão, onde "
         "essas mesmas editoras respondem normalmente, e use a exportação delas — a "
         "maioria das páginas de periódicos oferece <em>Cite</em> → RIS ou BibTeX, e "
         "esse arquivo é melhor do que qualquer coisa que um leitor consiga "
         "reconstruir. Se você precisa do artigo em si, e não da entrada, isso é uma "
         "questão de biblioteca, não de ferramenta."),
        ("A única coisa a não fazer é tentar de novo do mesmo lugar com outro agente de "
         "usuário. Não funciona, e uma ferramenta que finge ser um navegador para "
         "passar por uma regra dirigida justamente a ela é uma ferramenta que não se "
         "pode citar em sã consciência."),
        ("<strong>5 das vinte — o maior grupo, e aquele que menos se espera.</strong> "
         "Cinquenta a noventa kilobytes de HTML legível, nenhuma defesa de espécie "
         "alguma, e nenhum autor, nenhuma data, nenhum título de obra. Uma página de "
         "portal de estatística, uma página de serviços de uma câmara de comércio, uma "
         "matéria jornalística, uma versão de software."),
        ("O que fazer: escrever a entrada você mesmo, porque a decisão que a máquina "
         "não consegue tomar é <em>qual é a obra</em>. A fonte é a página do portal de "
         "estatística, o conjunto de dados por trás dela, ou a versão que o portal "
         "anuncia? Uma ferramenta de citação que responde aqui escolheu uma por você "
         "sem dizer."),
        ("Duas coisas tornam essa entrada manual defensável. Primeiro, a data de "
         "acesso, que para uma página sem data de publicação é a única data que a "
         "referência pode carregar. Segundo, o estado da página como você a viu — uma "
         + _SNAP + "captura</a> carimbada com o endereço e a data, guardada junto ao "
         "trabalho. Para literatura cinzenta e páginas oficiais isso não é excesso de "
         "zelo; uma página corporativa ou um portal de órgão público é refeito sem "
         "calendário e sem aviso."),
        ("Duas requisições respondem. Se a segunda tiver sucesso onde a primeira falha, "
         "é o caso 1. Se ambas falharem, caso 2. Se ambas tiverem sucesso e o registro "
         "ainda voltar com <code>complete: false</code>, caso 3."),
        ("Em um fluxo de trabalho com IA, os mesmos três casos saem do próprio "
         "registro: um <code>warning</code> que nomeia um muro é o caso 1 ou 2, e "
         "<code>complete: false</code> sem aviso é o caso 3. É por isso que a marca "
         "importa mais do que o título — a " + _MESSUNG + "medição</a> tem dois "
         "registros que carregam título, autor e nenhuma completude."),
    ],
    punkte=[
        ("<strong>Não é um jeito de furar um paywall.</strong> Todo caso acima\n"
         "    pressupõe que você tenha acesso — o seu, ou o da sua instituição.\n"
         "    Capturar uma página que você pode ler é uma cópia para uso próprio; não é\n"
         "    um caminho para uma que você não pode ler."),
        ("<strong>Não substitui a exportação de uma editora.</strong> Onde existir um\n"
         "    botão <em>Cite</em>, use-o."),
        ("<strong>Não é estável.</strong> 4 dessas recusas são recusas a um endereço\n"
         "    de centro de dados e não se repetiriam a partir de uma conexão doméstica.\n"
         "    Os " + _DATEN + "dados</a> dizem quais."),
    ],
    fuss=[
        ("Segue a medição de vinte fontes de 3 de agosto de 2026.\n"
         "      Dados brutos: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Correções são bem-vindas e são feitas em público: " + _ISSUES
         + "abrir uma issue</a>. Se um número aqui estiver errado, os dados e o "
           "script estão publicados para que se possa demonstrá-lo."),
        ("Divulgação: o autor desenvolve o Full Page PDF Snap, a extensão de captura "
         "vinculada acima. É uma maneira de dar o passo que lhe dá nome, e não a única "
         "— a impressão em PDF do próprio navegador é comparada a ela em uma "
         + _DRUCK + "medição publicada</a>, incluindo os casos em que a impressão vence."),
    ],
    disclaimer="Aviso legal",
)

# --------------------------------------------------------------------- Русский
INHALT["ru"] = _seite(
    h1="Источники, которые машина не может процитировать за вас, — и как процитировать их всё равно",
    standfirst=(
        "Из двадцати источников списка литературы десять вернулись готовыми ссылками, а "
        "десять были возвращены обратно. Возвращать их — правильное поведение. Здесь о "
        "том, что с ними делать: это зависит от причины, и лишь один из трёх случаев "
        "решается тем, что вы откроете страницу в браузере."),
    meta=("3 августа 2026 · из\n    " + _MESSUNG + "измерения на двадцати\n    "
          "источниках</a>"),
    h2=[
        "Случай 1 — страница отвечает браузеру, но не программе-читателю",
        "Случай 2 — страница отказывает всем с этого адреса",
        "Случай 3 — страница отвечает полностью, и ей нечего объявить",
        "Как различить три случая за один шаг",
        "Чем это не является",
    ],
    p=[
        ("Всякий, кто собирает список литературы из веб-источников, рано или поздно "
         "упирается в одну и ту же стену: автоматическая часть останавливается, и "
         "неясно, отказал ли инструмент, защищена ли страница или там изначально нечего "
         "было брать. Снаружи все три выглядят одинаково — пустой результат — и требуют "
         "совершенно разной работы. Ошибка в догадке стоит вечера, потраченного на "
         "страницу, которая никогда не даст записи, либо приводит к отказу от той, что "
         "открывается с первого щелчка."),
        ("Поэтому полезный вопрос не <em>как получить ссылку</em>. Он звучит так: "
         "<em>какой из трёх случаев перед нами?</em>"),
        ("<strong>1 из двадцати.</strong> Серверная программа-читатель получает 403; "
         "браузер получает страницу. Это защита от ботов, и это единственный случай, "
         "когда открытие источника вами самими меняет то, что доступно."),
        ("Что делать: открыть её в том браузере, который у вас уже есть. Ваша сессия, "
         "ваша сеть, ваш институциональный доступ. Затем заберите источник с собой, "
         "пока он не изменился, — " + _SNAP + "снимок всей страницы</a> записывает её "
         "одним PDF с адресом и датой обращения на нём, а именно это ссылка на "
         "веб-источник и так обязана нести. Данные для записи оказываются тогда в шапке "
         "вашего собственного файла, а не в индексе стороннего сервиса."),
        ("Зачем вообще делать снимок, а не просто записывать ссылку: потому что мы "
         + _VERSCHWINDEN + "измерили, что происходит с веб-источниками после того, как "
         "их процитировали</a>. Адрес в списке литературы — это обещание о странице, "
         "которая вам больше не подвластна."),
        ("<strong>4 из двадцати.</strong> 403 браузерному user agent так же охотно, как "
         "и программе-читателю. Здесь дело не в клиенте: запросы из центра обработки "
         "данных отклоняются, кем бы они себя ни называли. Издательства делают это, "
         "чтобы отбить охоту к массовой выгрузке, и это одинаково задевает любой "
         "автоматический инструмент."),
        ("Что делать: ничего хитроумного. Откройте страницу со своего собственного "
         "подключения, где те же издательства отвечают нормально, и воспользуйтесь их "
         "же экспортом — большинство журнальных страниц предлагают <em>Cite</em> → RIS "
         "или BibTeX, и этот файл лучше всего, что может восстановить "
         "программа-читатель. Если вам нужна сама статья, а не запись, это вопрос к "
         "библиотеке, а не к инструментам."),
        ("Единственное, чего делать не стоит, — повторять попытку с того же места с "
         "другим user agent. Это не работает, а инструмент, выдающий себя за браузер, "
         "чтобы обойти правило, направленное именно против него, — это инструмент, "
         "который нельзя цитировать с чистой совестью."),
        ("<strong>5 из двадцати — самая большая группа и та, которой ожидают меньше "
         "всего.</strong> От пятидесяти до девяноста килобайт читаемого HTML, никакой "
         "защиты, и ни автора, ни даты, ни названия произведения. Страница "
         "статистического портала, страница услуг торговой палаты, новостная статья, "
         "выпуск программы."),
        ("Что делать: написать запись самому, потому что решение, которое машина "
         "принять не может, — это <em>что именно является произведением</em>. "
         "Источник — это страница статистического портала, набор данных за ней или "
         "выпуск, о котором портал сообщает? Инструмент цитирования, который здесь "
         "отвечает, выбрал за вас один вариант, не сказав об этом."),
        ("Две вещи делают такую ручную запись обоснованной. Первое — дата обращения, "
         "которая для страницы без даты публикации является единственной датой, какую "
         "ссылка может нести. Второе — состояние страницы в том виде, в каком вы её "
         "видели: " + _SNAP + "снимок</a> со штампом адреса и даты, хранимый вместе с "
         "работой. Для серой литературы и официальных веб-страниц это не "
         "перестраховка; корпоративная страница или ведомственный портал "
         "перестраиваются без всякого расписания и без предупреждения."),
        ("Ответ дают два запроса. Если второй удаётся там, где первый не проходит, это "
         "случай 1. Если оба не проходят — случай 2. Если оба удаются, а запись всё "
         "равно возвращается с <code>complete: false</code>, — случай 3."),
        ("В рабочем процессе с ИИ те же три случая следуют из самой записи: "
         "<code>warning</code>, называющий стену, — это случай 1 или 2, а "
         "<code>complete: false</code> без предупреждения — случай 3. Именно поэтому "
         "признак значит больше, чем заглавие: в " + _MESSUNG + "измерении</a> есть две "
         "записи, несущие заглавие, автора и никакой полноты."),
    ],
    punkte=[
        ("<strong>Это не способ обойти платный доступ.</strong> Каждый случай выше\n"
         "    предполагает, что доступ у вас есть — свой собственный или вашего\n"
         "    учреждения. Снимок страницы, которую вам можно читать, — это копия для\n"
         "    личного пользования; путём к той, которую читать нельзя, он не является."),
        ("<strong>Это не замена экспорту издательства.</strong> Там, где есть кнопка\n"
         "    <em>Cite</em>, пользуйтесь ею."),
        ("<strong>Это не постоянно.</strong> 4 из этих отказов — отказы адресу центра\n"
         "    обработки данных, и с домашнего подключения они бы не повторились.\n"
         "    " + _DATEN + "Данные</a> говорят, какие именно."),
    ],
    fuss=[
        ("Продолжение измерения на двадцати источниках от 3 августа 2026.\n"
         "      Исходные данные: " + _DATEN + "JSON</a>, CC BY 4.0."),
        ("Исправления приветствуются и вносятся публично: " + _ISSUES
         + "открыть issue</a>. Если какая-то цифра здесь неверна, данные и скрипт "
           "опубликованы, чтобы это можно было показать."),
        ("Раскрытие: автор разрабатывает Full Page PDF Snap, расширение для снимков, на "
         "которое дана ссылка выше. Это один способ выполнить шаг, по которому оно "
         "названо, и не единственный — собственная печать браузера в PDF сопоставлена с "
         "ним в " + _DRUCK + "опубликованном измерении</a>, включая случаи, когда "
         "печать выигрывает."),
    ],
    disclaimer="Отказ от ответственности",
)

# ------------------------------------------------------------------- 简体中文
INHALT["zh-CN"] = _seite(
    h1="机器无法替你引用的来源 — 以及如何仍旧把它们引用出来",
    standfirst=(
        "一份阅读清单中的二十个来源，十个以完成的引文返回，十个被退回。"
        "退回是正确的行为。本文讲的是如何处理这些被退回的来源：处理方式因原因而异，"
        "而三种情况中只有一种能靠在浏览器里打开页面来解决。"),
    meta=("2026年8月3日 · 出自\n    " + _MESSUNG + "二十个来源的\n    测量</a>"),
    h2=[
        "情况 1 — 页面回应浏览器，却不回应读取程序",
        "情况 2 — 页面拒绝来自这个地址的所有人",
        "情况 3 — 页面完整回应，却没有什么可申报",
        "一步分清这三种情况",
        "这不是什么",
    ],
    p=[
        ("凡是从网络来源整理参考文献的人，迟早会撞上同一堵墙：自动化的部分停住了，"
         "而看不出是工具失灵、页面设了防护，还是那里本来就没有可采集的东西。"
         "从外面看，这三者一模一样——一个空结果——可它们需要完全不同的工作。"
         "判断错了，就会把一个下午耗在一个永远给不出著录的页面上，"
         "或者放弃一个第一次点击就能打开的页面。"),
        ("所以有用的问题不是<em>我怎样得到一条引文</em>，"
         "而是<em>这是三者中的哪一种？</em>"),
        ("<strong>二十个中的 1 个。</strong>服务器端的读取程序得到 403；浏览器得到页面。"
         "这是一种反爬防护，也是唯一一种自己去打开来源就会改变可得内容的情况。"),
        ("该怎么做：用你手头已有的浏览器打开它。你的会话、你的网络、你所在机构的访问权。"
         "然后在页面变化之前把来源带走——" + _SNAP + "整页取样</a>把页面写成一个 PDF，"
         "上面带着网址和获取日期，而这本来就是一条网络来源的参考文献必须承载的内容。"
         "这样，著录所需的信息就在你自己文件的页眉里，而不在某个服务的索引里。"),
        ("为什么非要抓取，而不是记下链接就好：因为我们"
         + _VERSCHWINDEN + "测量过网络来源被引用之后会发生什么</a>。"
         "参考文献里的一个网址，是对一个你已不再掌控的页面所作的承诺。"),
        ("<strong>二十个中的 4 个。</strong>对浏览器的 user agent 给出 403，"
         "跟对读取程序一样痛快。这里问题不在客户端：来自数据中心的请求，"
         "无论自称是什么都会被拒。出版商这样做是为了遏制批量下载，"
         "而它同样地波及每一个自动化工具。"),
        ("该怎么做：不要耍花招。用你自己的连接打开页面——同样这些出版商在那里会正常回应"
         "——然后使用他们自己的导出功能：多数期刊页面都提供 <em>Cite</em> → RIS 或 "
         "BibTeX，那个文件比读取程序能重建出来的任何东西都好。"
         "如果你要的是文章本身而不是著录条目，那是图书馆的问题，不是工具的问题。"),
        ("唯一不该做的，是从同一个地方换一个 user agent 再试一次。这行不通，"
         "而且一个为了绕过恰恰针对它的规则而假装成浏览器的工具，"
         "是一个你无法问心无愧地去引用的工具。"),
        ("<strong>二十个中的 5 个——最大的一组，也是人们最想不到的一组。</strong>"
         "50 到 90 千字节可读的 HTML，没有任何防护，也没有作者、没有日期、没有作品标题。"
         "一个统计门户的页面、一个商会的服务页面、一篇新闻报道、一次软件发布。"),
        ("该怎么做：自己写这条著录，因为机器无法做出的判断是<em>作品究竟是什么</em>。"
         "来源是统计门户的这个页面、它背后的数据集，还是门户所公告的那次发布？"
         "在这里给出答案的引用工具，已经替你选了一个，却没有说出来。"),
        ("有两样东西让这条手写著录站得住脚。第一是获取日期，"
         "对于没有发布日期的页面，这是参考文献唯一能承载的日期。"
         "第二是你所见到的页面状态——一份盖上了网址和日期的" + _SNAP + "取样</a>，"
         "与作品一同保存。对于灰色文献和官方网页，这不是多此一举；"
         "一个企业页面或一个机关门户，重建起来既无时间表，也无预告。"),
        ("两个请求就能回答。若第二个成功而第一个失败，是情况 1。若两个都失败，是情况 2。"
         "若两个都成功，而记录仍旧带着 <code>complete: false</code> 返回，是情况 3。"),
        ("在 AI 工作流中，同样这三种情况可以从记录本身读出：点名一堵墙的 "
         "<code>warning</code> 是情况 1 或 2，而没有警告的 <code>complete: false</code> "
         "是情况 3。这就是为什么这个标志比标题更重要——" + _MESSUNG + "那次测量</a>里"
         "有两条记录，带着标题、带着作者，却没有完整性。"),
    ],
    punkte=[
        ("<strong>这不是绕过付费墙的办法。</strong>上面每一种情况都假定你有访问权\n"
         "    ——你自己的，或者你所在机构的。抓取一个你可以阅读的页面，\n"
         "    是供自己使用的复制；它不是通往一个你不可以阅读的页面的路径。"),
        ("<strong>这不能取代出版商的导出。</strong>凡是有 <em>Cite</em> 按钮的地方，\n"
         "    就用它。"),
        ("<strong>这并不稳定。</strong>其中 4 次拒绝是针对数据中心地址的拒绝，\n"
         "    从家庭连接不会重现。" + _DATEN + "数据</a>说明了是哪几次。"),
    ],
    fuss=[
        ("承接 2026年8月3日二十个来源的测量。\n"
         "      原始数据：" + _DATEN + "JSON</a>，CC BY 4.0。"),
        ("欢迎指正，并且公开进行：" + _ISSUES
         + "提交一个 issue</a>。如果这里的某个数字有误，"
           "数据和脚本都已公开，以便能够指出来。"),
        ("披露：作者开发上文链接的取样扩展 Full Page PDF Snap。"
         "它是完成其名称所指那一步的一种方式，并非唯一的方式——"
         "浏览器自带的打印为 PDF 已在一次" + _DRUCK + "公开的测量</a>中与之作了比较，"
         "其中也包括打印胜出的情形。"),
    ],
    disclaimer="免责声明",
)
