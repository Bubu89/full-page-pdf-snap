#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/anleitung/webseite-als-pdf-speichern/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite docs/anleitung/
webseite-als-pdf-speichern/index.html, woertlich uebernommen — nicht
build-einstiegsseiten.py, der beide Einstiegsseiten aus einer Vorlage erzeugt
und beim naechsten Lauf die Neunsprachen-Auszeichnung wieder ueberschriebe.

Diese Seite ist NICHT die Uebersetzung von /how-to/save-a-webpage-as-pdf/,
sondern eine eigene Fassung desselben Arguments (texte_howto_pdf.py). Sie
fuehrt zusaetzlich § 42 UrhG und einen vierten Punkt zur Rechtsberatung, nennt
die Add-ons-API nicht, und ihr Tastenkuerzel heisst <code>Alt+Umschalt+Y</code>
statt <code>Alt+Shift+Y</code>. Deshalb zwei Module: ein gemeinsames waere an
jeder dieser Stellen eine Behauptung, die auf einer der beiden Seiten nicht
stimmt.

Der vorgefundene deutsche Text steht als `de` — woertlich, einschliesslich
seiner Umschrift (`ue`, `oe`, `ae` statt Umlauten) und der beiden englisch
gebliebenen Fusszeilen. Beides ist so ausgeliefert und passt zum Kopf der
Seite, der ebenfalls umschrieben ist; es zu glaetten waere eine inhaltliche
Aenderung, keine Uebersetzung. Die acht anderen Fassungen sind daraus
abgeleitet und schreiben die Fusszeilen in ihrer Sprache.

EINE Ausnahme von „die Datei auf der Platte ist die Quelle": Tabellenzeile 3
und der Absatzanfang darunter standen dort mit 94,8 % / 92,6 % und „Beim Text
gewinnt der Druckexport" — genau den Zahlen, die Commit 3c57e3b (#18,
„withdraw the old figures") zurueckgezogen hat. Die Arbeitskopie war an dieser
Stelle die Ausgabe eines veralteten build-einstiegsseiten.py (Zeile 294), also
aelter als der eingecheckte Text. Uebernommen ist deshalb die Fassung aus HEAD:
87,6 % gegen 91,5 %, gemessen am 5. August, mit der Aufnahme vorn.

Ausgelassen: die Zeile `· <a href="/how-to/save-a-webpage-as-pdf/">English
version</a>` in der Kopfangabe. Die Seite traegt ihre englische Fassung jetzt
selbst; ein Verweis „English version" im englischen Block waere ein Zirkel.

Unveraendert in jeder Sprache: alle Zahlen (26, 9, 1, 0, 87,6 %, 91,5 %, 20, 5,
248, 60, 150, 19,3 %, 8,7 %, 603, 8,1 s, 10), Versionsangaben (Chrome 116+),
die Fundstelle § 42 UrhG, Dateiformate und Werkzeugnamen (PDF, RIS, BibTeX,
DOI, Zotero, Citavi, EndNote, Mendeley, Full Page PDF Snap, Install Chrome
Extensions), das Tastenkuerzel und alle Adressen. Nur das Dezimalzeichen folgt
der Sprache (91.5 % im Englischen) — die Messung ist dieselbe.

Rendern:  python3 tools/seite-neunsprachig.py texte_anleitung_pdf.py
"""

URL = "https://provinglab.dev/anleitung/webseite-als-pdf-speichern/"
ZIEL = "anleitung/webseite-als-pdf-speichern/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# Adressen — in jeder Sprache dieselben.
_AMO = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
_CWS = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"
_M_DRUCK = "/measurements/print-to-pdf-vs-screenshot/"
_M_ANDROID = "/measurements/android-capture-extensions/"
_M_QUELLEN = "/measurements/web-citations-that-vanish/"
_M_LISTE = "/measurements/reading-list-to-bibliography/"
_REZEPTE = "/recipes/"
_ISSUES = "https://github.com/Bubu89/full-page-pdf-snap/issues"
_KUERZEL = "Alt+Umschalt+Y"
_CHROME = "Chrome 116+, Edge, Brave, Vivaldi"
_PARAGRAF = "§ 42 UrhG"


def _tabelle(th_druck, th_aufnahme, zeilen,
             c_seiten, c_blatt, c_text_druck, c_text_aufnahme,
             c_eingebaut, c_nein, dez=","):
    """Die Vergleichstabelle. Die Messwerte stehen NUR hier — sie neunmal
    abzuschreiben hiesse, neun Gelegenheiten zu schaffen, eine Zahl zu
    verlieren. Die Zellentexte kommen als Vorlage mit {n} herein, damit die
    Zahl auch dort stehen kann, wo die Sprache sie hinstellt."""
    seiten = c_seiten.replace("{n}", "26")
    blatt = c_blatt.replace("{n}", "1")
    t_druck = c_text_druck.replace("{n}", f"87{dez}6 %")
    t_aufnahme = c_text_aufnahme.replace("{n}", f"91{dez}5 %")
    return f'''<table>
  <thead><tr><th scope="col"></th><th scope="col">{th_druck}</th><th scope="col">{th_aufnahme}</th></tr></thead>
  <tbody>
    <tr><td>{zeilen[0]}</td><td>{seiten}</td><td><strong>{blatt}</strong></td></tr>
    <tr><td>{zeilen[1]}</td><td>9</td><td>0</td></tr>
    <tr><td>{zeilen[2]}</td><td><strong>{t_druck}</strong></td><td><strong>{t_aufnahme}</strong></td></tr>
    <tr><td>{zeilen[3]}</td><td>{c_eingebaut}</td><td>{c_nein}</td></tr>
  </tbody>
</table>'''


def _seite(h1, standfirst, meta, btn_ff, install, h2, tabelle,
           p_druck, l_druck, p_login, p_handy, l_android,
           p_quelle, l_quelle, p_ris, p_liste, l_rezepte, l_messung,
           li, fuss, korrekturen, l_issue, offenlegung1, l_offenlegung,
           offenlegung2, disclaimer):
    punkte = "\n".join(f"  <li>{x}</li>" for x in li)
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{meta}</p>
</header>

<p>
  <a class="btn" href="{_AMO}">{btn_ff}</a>
  &nbsp;<a class="btn" href="{_CWS}">{_CHROME}</a>
</p>
<p style="font-size:.9rem">
  {install}
</p>

<h2>{h2[0]}</h2>
{tabelle}
<p>
  {p_druck}
  <a href="{_M_DRUCK}">{l_druck}</a>
</p>

<h2>{h2[1]}</h2>
<p>
  {p_login}
</p>

<h2>{h2[2]}</h2>
<p>
  {p_handy}
  <a href="{_M_ANDROID}">{l_android}</a>
</p>

<h2>{h2[3]}</h2>
<p>
  {p_quelle}
  <a href="{_M_QUELLEN}">{l_quelle}</a>
</p>
<p>
  {p_ris}
</p>

<h2>{h2[4]}</h2>
<p>
  {p_liste}
  <a href="{_REZEPTE}">{l_rezepte}</a> ·
  <a href="{_M_LISTE}">{l_messung}</a>
</p>

<h2>{h2[5]}</h2>
<ul>
{punkte}
</ul>
<footer>
      {fuss}
      <br><br>
      {korrekturen} <a href="{_ISSUES}">{l_issue}</a>.
      <br><br>
      {offenlegung1} <a href="{_M_DRUCK}">{l_offenlegung}</a>{offenlegung2}
      <br><br>
      <a href="../../">← Proving Lab</a> · <a href="../../disclaimer/">{disclaimer}</a>
    </footer>'''


INHALT = {}

# ------------------------------------------------------------------- Deutsch
# Der ausgelieferte Text, woertlich — Umschrift und englische Fusszeilen
# eingeschlossen. Einzige Auslassung: der Verweis auf die englische Seite,
# siehe Modulkopf.
INHALT["de"] = _seite(
    h1="Webseite als PDF speichern — ein Blatt, mit Quelle und Abrufdatum darauf",
    standfirst=(
        "Kurz: eine Aufnahme-Erweiterung statt des Druckdialogs. Der Druckexport "
        "teilt in Seiten auf — derselbe Artikel kam als <strong>26 Seiten heraus, 9 "
        "Umbrueche schnitten mitten durch einen Satz</strong>. Eine Aufnahme schreibt "
        "ein durchgehendes Blatt und kann Herkunft und Abrufzeit hineinschreiben."),
    meta="3 August 2026 · jede Zahl verweist auf die Messung dahinter",
    btn_ff="Firefox, Rechner und Android",
    install=(
        "Kostenlos, MIT-Lizenz, laeuft auf dem Geraet. Edge fragt einmal, ob "
        "Erweiterungen aus anderen Stores zugelassen werden; Opera braucht zuerst "
        "seine Erweiterung <em>Install Chrome Extensions</em>. Dann: Seite oeffnen, "
        f"<code>{_KUERZEL}</code> druecken oder auf das Symbol klicken."),
    h2=["Drucken oder aufnehmen? Der ehrliche Vergleich",
        "Hinter einem Login oder einer Schranke, zu der Sie Zugang haben",
        "Am Handy",
        "Warum das Abrufdatum in die Datei gehoert",
        "Eine ganze Quellenliste auf einmal",
        "Was es nicht leistet"],
    tabelle=_tabelle(
        "Druckexport", "Vollseiten-Aufnahme",
        ["Derselbe Artikel ergibt", "Umbrueche mitten im Satz",
         "Markierbarer, durchsuchbarer Text", "Kostet etwas"],
        "{n} Seiten", "{n} Blatt", "{n}", "{n}",
        "nein, eingebaut", "nein"),
    p_druck=(
        "<strong>Beim Text liegt die Aufnahme vorn, seit sie eine Textebene trägt — "
        "91,5 % gegen 87,6 %, gemessen am 5. August.</strong> Wer nur eine lesbare, "
        "durchsuchbare Kopie braucht und sich an der Seitenaufteilung nicht stoert, "
        "kommt mit der Funktion aus, die im Browser schon steckt — das steht hier, "
        "statt es zu verschweigen. Eine Aufnahme lohnt, wenn das Layout zaehlt, wenn "
        "ein Umbruch durch eine Tabelle fiele, oder wenn die Quellenangaben mit der "
        "Datei mitreisen sollen."),
    l_druck="Methode und Rohdaten",
    p_login=(
        "Eine Aufnahme-Erweiterung liest, was Ihre eigene Sitzung ohnehin zeigt: ein "
        "lizenzierter Zeitschriftenartikel, ein Kursraum, eine Bestellbestaetigung — "
        "gesichert, wie Sie es sehen. Kein serverseitiger Dienst kann das. Gemessen an "
        "20 gemischten Quellen wurde ein serverseitiger Leser von 5 davon rundweg "
        "abgewiesen. Eine Seite zu sichern, die Sie lesen duerfen, ist eine Kopie zum "
        f"eigenen Gebrauch ({_PARAGRAF}) — kein Weg zu Inhalten ohne Zugang."),
    p_handy=(
        "Nur Firefox. <strong>Chrome fuer Android installiert ueberhaupt keine "
        "Erweiterungen</strong>, die Frage stellt sich also nur dort. Von 248 "
        "geprueften Erweiterungen geben 60 Android-Unterstuetzung an — getestet hatte "
        "sie vorher keine."),
    l_android="Die Android-Messung",
    p_quelle=(
        "Eine Adresse im Literaturverzeichnis ist ein Versprechen ueber eine Seite, die "
        "Ihnen nicht gehoert. Geprueft an 150 Quellen aus echten Verzeichnissen: "
        "<strong>19,3 % waren verschwunden</strong>, 8,7 % nirgends archiviert, und wo "
        "eine Sicherung bestand, war sie im Mittel 603 Tage alt. Bei einer Seite ohne "
        "Veroeffentlichungsdatum ist die Abrufzeit das einzige Datum, das die Angabe "
        "tragen kann — und es existiert nur in dem Moment, in dem Sie hinsehen."),
    l_quelle="Was mit einer Quelle geschieht, nachdem man sie zitiert hat",
    p_ris=(
        "Eine Aufnahme schreibt das hinein: Verfasser, Titel, DOI, Lizenz und die "
        "genaue Zeit — im PDF und in einem RIS-Satz daneben, den Zotero, Citavi, "
        "EndNote und Mendeley einlesen."),
    p_liste=(
        "Fuer ein Literaturverzeichnis statt einer einzelnen Seite braucht der "
        "groessere Teil gar keinen Browser. Von 20 gemischten Quellen wurden "
        "<strong>10 in 8,1 Sekunden zu vollstaendigen Datensaetzen</strong> mit RIS und "
        "BibTeX — ohne Konto, ohne Schluessel. Die anderen zehn kommen mit Begruendung "
        "zurueck, damit Sie wissen, welche Adressen Sie selbst oeffnen muessen."),
    l_rezepte="Die Rezepte",
    l_messung="die Messung",
    li=["Es erreicht keine Inhalte, zu denen Sie keinen Zugang haben.",
        "Eine Bildschirmaufnahme ist kein qualifiziertes elektronisches Dokument. "
        "Sie haelt fest, wie eine Seite zu einem Zeitpunkt aussah — das ist etwas "
        "anderes, als es zu beweisen.",
        "Wo ein Verlag einen eigenen <em>Zitieren → RIS</em>-Export anbietet, ist "
        "diese Datei massgeblich und besser als alles Rekonstruierte.",
        "Die Hinweise zum Urheberrecht auf dieser Seite sind eine Einordnung, keine "
        "Rechtsberatung. Im Zweifel und bei einer Auseinandersetzung fragen Sie eine "
        "Anwaeltin oder einen Anwalt, nicht diese Seite."],
    fuss=("Zahlen gemessen zwischen 1. und 3. August 2026, jede mit Methode und "
          "Rohdaten verlinkt."),
    korrekturen="Corrections are welcome and are made in public:",
    l_issue="open an issue",
    offenlegung1=("Disclosure: the author develops Full Page PDF Snap, the extension "
                  "named on this page. The browser's own print-to-PDF is"),
    l_offenlegung="measured against it",
    offenlegung2=", including where print wins.",
    disclaimer="Disclaimer",
)

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="Save a web page as PDF — one sheet, with its source and retrieval date on it",
    standfirst=(
        "In short: a capture extension instead of the print dialog. The print export "
        "paginates — the same article came out as <strong>26 pages, and 9 breaks cut "
        "through the middle of a sentence</strong>. A capture writes one continuous "
        "sheet and can write the origin and the time of retrieval into it."),
    meta="3 August 2026 · every figure links to the measurement behind it",
    btn_ff="Firefox, desktop and Android",
    install=(
        "Free, MIT licence, runs on the device. Edge asks once whether extensions from "
        "other stores are allowed; Opera first needs its <em>Install Chrome "
        f"Extensions</em> add-on. Then: open the page, press <code>{_KUERZEL}</code> or "
        "click the icon."),
    h2=["Print or capture? The honest comparison",
        "Behind a login or a barrier you have access to",
        "On a phone",
        "Why the retrieval date belongs in the file",
        "A whole list of sources at once",
        "What it does not do"],
    tabelle=_tabelle(
        "Print export", "Full-page capture",
        ["The same article comes out as", "Breaks in mid-sentence",
         "Selectable, searchable text", "Costs anything"],
        "{n} pages", "{n} sheet", "{n}", "{n}",
        "no, built in", "no", dez="."),
    p_druck=(
        "<strong>The capture leads on text since it carries a text layer — 91.5 % "
        "against 87.6 %, measured 5 August.</strong> If all you need is a "
        "readable, searchable copy and the pagination does not trouble you, the "
        "function already built into the browser will do — and that is said here "
        "rather than kept quiet. A capture is worth it when the layout counts, when a "
        "break would fall through a table, or when the source details are to travel "
        "with the file."),
    l_druck="Method and raw data",
    p_login=(
        "A capture extension reads what your own session already shows: a licensed "
        "journal article, a course page, an order confirmation — saved as you see it. "
        "No server-side service can do this. Measured across 20 mixed sources, a "
        "server-side reader was flatly refused by 5 of them. Saving a page you are "
        f"allowed to read is a copy for your own use ({_PARAGRAF}) — not a route to "
        "content you have no access to."),
    p_handy=(
        "Only Firefox. <strong>Chrome for Android installs no extensions at "
        "all</strong>, so the question only arises there. Of 248 extensions checked, "
        "60 declare Android support — none of them had been tested before."),
    l_android="The Android measurement",
    p_quelle=(
        "An address in a bibliography is a promise about a page that is not yours. "
        "Checked against 150 sources from real reference lists: <strong>19.3 % had "
        "vanished</strong>, 8.7 % were archived nowhere, and where a snapshot existed "
        "it was a median of 603 days old. For a page without a publication date, the "
        "time of retrieval is the only date the reference can carry — and it exists "
        "only at the moment you look."),
    l_quelle="What happens to a source after you have cited it",
    p_ris=(
        "A capture writes that in: authors, title, DOI, licence and the exact time — "
        "in the PDF and in an RIS record beside it, which Zotero, Citavi, EndNote and "
        "Mendeley read."),
    p_liste=(
        "For a bibliography rather than a single page, the larger part needs no browser "
        "at all. Of 20 mixed sources, <strong>10 became complete records in 8.1 "
        "seconds</strong> with RIS and BibTeX — no account, no key. The other ten come "
        "back with a reason, so you know which addresses you have to open yourself."),
    l_rezepte="The recipes",
    l_messung="the measurement",
    li=["It does not reach content you have no access to.",
        "A screen capture is not a qualified electronic document. It records what a "
        "page looked like at a given time — that is something other than proving it.",
        "Where a publisher offers its own <em>Cite → RIS</em> export, that file is "
        "authoritative and better than anything reconstructed.",
        "The notes on copyright on this page are an assessment, not legal advice. In "
        "case of doubt, and in a dispute, ask a lawyer, not this page."],
    fuss=("Figures measured between 1 and 3 August 2026, each linked to method and "
          "raw data."),
    korrekturen="Corrections are welcome and are made in public:",
    l_issue="open an issue",
    offenlegung1=("Disclosure: the author develops Full Page PDF Snap, the extension "
                  "named on this page. The browser's own print-to-PDF is"),
    l_offenlegung="measured against it",
    offenlegung2=", including where print wins.",
    disclaimer="Disclaimer",
)

# ------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Guardar una página web como PDF — una hoja, con la fuente y la fecha de consulta encima",
    standfirst=(
        "En corto: una extensión de captura en lugar del diálogo de impresión. La "
        "exportación de impresión reparte en páginas — el mismo artículo salió como "
        "<strong>26 páginas, y 9 saltos cortaron por la mitad de una frase</strong>. "
        "Una captura escribe una hoja continua y puede inscribir en ella la "
        "procedencia y la hora de consulta."),
    meta="3 de agosto de 2026 · cada cifra remite a la medición que hay detrás",
    btn_ff="Firefox, escritorio y Android",
    install=(
        "Gratis, licencia MIT, se ejecuta en el dispositivo. Edge pregunta una vez si "
        "se permiten extensiones de otras tiendas; Opera necesita antes su extensión "
        f"<em>Install Chrome Extensions</em>. Después: abra la página, pulse "
        f"<code>{_KUERZEL}</code> o haga clic en el icono."),
    h2=["¿Imprimir o capturar? La comparación honesta",
        "Detrás de un inicio de sesión o de una barrera a la que tiene acceso",
        "En el teléfono",
        "Por qué la fecha de consulta pertenece al archivo",
        "Toda una lista de fuentes de una vez",
        "Lo que no hace"],
    tabelle=_tabelle(
        "Exportación de impresión", "Captura de página completa",
        ["El mismo artículo da", "Saltos en mitad de la frase",
         "Texto seleccionable y con búsqueda", "Cuesta algo"],
        "{n} páginas", "{n} hoja", "{n}", "{n}",
        "no, va incluido", "no"),
    p_druck=(
        "<strong>En el texto va por delante la captura desde que lleva una capa de "
        "texto — 91,5 % frente a 87,6 %, medido el 5 de agosto.</strong> Quien solo "
        "necesita una copia legible y con búsqueda, y a quien no le molesta el reparto "
        "en páginas, se apaña con la función que ya está en el navegador — se dice "
        "aquí en vez de callarlo. Una captura merece la pena cuando cuenta la "
        "maquetación, cuando un salto caería por medio de una tabla, o cuando los "
        "datos de la fuente deben viajar con el archivo."),
    l_druck="Método y datos brutos",
    p_login=(
        "Una extensión de captura lee lo que su propia sesión ya muestra: un artículo "
        "de revista con licencia, un aula virtual, una confirmación de pedido — "
        "guardado tal como usted lo ve. Ningún servicio del lado del servidor puede "
        "hacerlo. Medido en 20 fuentes mixtas, un lector del lado del servidor fue "
        "rechazado de plano por 5 de ellas. Guardar una página que usted puede leer es "
        f"una copia para uso propio ({_PARAGRAF}) — no una vía hacia contenidos sin "
        "acceso."),
    p_handy=(
        "Solo Firefox. <strong>Chrome para Android no instala ninguna "
        "extensión</strong>, así que la pregunta solo se plantea allí. De 248 "
        "extensiones comprobadas, 60 declaran compatibilidad con Android — ninguna "
        "había sido probada antes."),
    l_android="La medición en Android",
    p_quelle=(
        "Una dirección en la bibliografía es una promesa sobre una página que no le "
        "pertenece. Comprobado con 150 fuentes de listas de referencias reales: "
        "<strong>el 19,3 % había desaparecido</strong>, el 8,7 % no estaba archivado en "
        "ningún sitio, y donde había una copia de seguridad, tenía de media 603 días. "
        "En una página sin fecha de publicación, la hora de consulta es la única fecha "
        "que puede llevar la referencia — y solo existe en el momento en que usted "
        "mira."),
    l_quelle="Qué le pasa a una fuente después de haberla citado",
    p_ris=(
        "Una captura lo escribe dentro: autores, título, DOI, licencia y la hora exacta "
        "— en el PDF y en un registro RIS al lado, que Zotero, Citavi, EndNote y "
        "Mendeley leen."),
    p_liste=(
        "Para una bibliografía en lugar de una sola página, la mayor parte no necesita "
        "navegador alguno. De 20 fuentes mixtas, <strong>10 se convirtieron en "
        "registros completos en 8,1 segundos</strong> con RIS y BibTeX — sin cuenta, "
        "sin clave. Las otras diez vuelven con su motivo, para que sepa qué "
        "direcciones tiene que abrir usted mismo."),
    l_rezepte="Las recetas",
    l_messung="la medición",
    li=["No alcanza contenidos a los que usted no tiene acceso.",
        "Una captura de pantalla no es un documento electrónico cualificado. Retiene "
        "cómo se veía una página en un momento dado — eso es algo distinto de probarlo.",
        "Donde una editorial ofrece su propia exportación <em>Citar → RIS</em>, ese "
        "archivo es el que manda y es mejor que todo lo reconstruido.",
        "Las indicaciones sobre derechos de autor de esta página son una "
        "clasificación, no asesoramiento jurídico. En caso de duda y ante un litigio, "
        "pregunte a una abogada o a un abogado, no a esta página."],
    fuss=("Cifras medidas entre el 1 y el 3 de agosto de 2026, cada una enlazada con "
          "su método y sus datos brutos."),
    korrekturen="Las correcciones son bienvenidas y se hacen en público:",
    l_issue="abrir una incidencia",
    offenlegung1=("Divulgación: el autor desarrolla Full Page PDF Snap, la extensión "
                  "nombrada en esta página. La impresión a PDF propia del navegador "
                  "está"),
    l_offenlegung="medida frente a ella",
    offenlegung2=", incluidos los casos en los que gana la impresión.",
    disclaimer="Aviso legal",
)

# ------------------------------------------------------------------- Français
INHALT["fr"] = _seite(
    h1="Enregistrer une page web en PDF — une feuille, avec la source et la date de consultation dessus",
    standfirst=(
        "En bref : une extension de capture au lieu de la boîte de dialogue "
        "d’impression. L’export d’impression découpe en pages — le même article est "
        "sorti en <strong>26 pages, et 9 sauts ont coupé au milieu d’une phrase</strong>. "
        "Une capture écrit une feuille continue et peut y inscrire la provenance et "
        "l’heure de consultation."),
    meta="3 août 2026 · chaque chiffre renvoie à la mesure qui est derrière",
    btn_ff="Firefox, ordinateur et Android",
    install=(
        "Gratuit, licence MIT, s’exécute sur l’appareil. Edge demande une fois si les "
        "extensions d’autres boutiques sont autorisées ; Opera a d’abord besoin de son "
        "extension <em>Install Chrome Extensions</em>. Ensuite : ouvrez la page, "
        f"appuyez sur <code>{_KUERZEL}</code> ou cliquez sur l’icône."),
    h2=["Imprimer ou capturer ? La comparaison honnête",
        "Derrière une connexion ou une barrière à laquelle vous avez accès",
        "Sur un téléphone",
        "Pourquoi la date de consultation a sa place dans le fichier",
        "Toute une liste de sources d’un coup",
        "Ce que cela ne fait pas"],
    tabelle=_tabelle(
        "Export d’impression", "Capture pleine page",
        ["Le même article donne", "Sauts au milieu d’une phrase",
         "Texte sélectionnable et cherchable", "Coûte quelque chose"],
        "{n} pages", "{n} feuille", "{n}", "{n}",
        "non, intégré", "non"),
    p_druck=(
        "<strong>Sur le texte, la capture mène depuis qu’elle porte une couche de "
        "texte — 91,5 % contre 87,6 %, mesuré le 5 août.</strong> Qui n’a besoin "
        "que d’une copie lisible et cherchable, et que le découpage en pages ne gêne "
        "pas, se contente de la fonction déjà présente dans le navigateur — c’est écrit "
        "ici plutôt que tu. Une capture vaut la peine quand la mise en page compte, "
        "quand un saut tomberait au milieu d’un tableau, ou quand les indications de "
        "source doivent voyager avec le fichier."),
    l_druck="Méthode et données brutes",
    p_login=(
        "Une extension de capture lit ce que votre propre session affiche déjà : un "
        "article de revue sous licence, un espace de cours, une confirmation de "
        "commande — sauvegardé tel que vous le voyez. Aucun service côté serveur ne "
        "peut le faire. Mesuré sur 20 sources variées, un lecteur côté serveur a été "
        "refusé net par 5 d’entre elles. Sauvegarder une page que vous avez le droit de "
        f"lire est une copie pour votre usage propre ({_PARAGRAF}) — et non un chemin "
        "vers des contenus sans accès."),
    p_handy=(
        "Seulement Firefox. <strong>Chrome pour Android n’installe aucune "
        "extension</strong>, la question ne se pose donc que là. Sur 248 extensions "
        "vérifiées, 60 déclarent la prise en charge d’Android — aucune n’avait été "
        "testée auparavant."),
    l_android="La mesure Android",
    p_quelle=(
        "Une adresse dans la bibliographie est une promesse au sujet d’une page qui ne "
        "vous appartient pas. Vérifié sur 150 sources tirées de vraies listes de "
        "références : <strong>19,3 % avaient disparu</strong>, 8,7 % n’étaient archivées "
        "nulle part, et là où une sauvegarde existait, elle avait en moyenne 603 jours. "
        "Pour une page sans date de publication, l’heure de consultation est la seule "
        "date que la référence puisse porter — et elle n’existe qu’à l’instant où vous "
        "regardez."),
    l_quelle="Ce qu’il advient d’une source après qu’on l’a citée",
    p_ris=(
        "Une capture l’inscrit dedans : auteurs, titre, DOI, licence et l’heure exacte "
        "— dans le PDF et dans une notice RIS à côté, que Zotero, Citavi, EndNote et "
        "Mendeley lisent."),
    p_liste=(
        "Pour une bibliographie plutôt qu’une seule page, la plus grande part n’a "
        "besoin d’aucun navigateur. Sur 20 sources variées, <strong>10 sont devenues "
        "des notices complètes en 8,1 secondes</strong> avec RIS et BibTeX — sans "
        "compte, sans clé. Les dix autres reviennent motivées, pour que vous sachiez "
        "quelles adresses vous devez ouvrir vous-même."),
    l_rezepte="Les recettes",
    l_messung="la mesure",
    li=["Cela n’atteint pas des contenus auxquels vous n’avez pas accès.",
        "Une capture d’écran n’est pas un document électronique qualifié. Elle retient "
        "l’aspect d’une page à un instant donné — ce qui n’est pas la même chose que "
        "de le prouver.",
        "Là où un éditeur propose son propre export <em>Citer → RIS</em>, ce fichier "
        "fait autorité et vaut mieux que tout ce qui est reconstruit.",
        "Les indications relatives au droit d’auteur sur cette page sont un "
        "positionnement, pas un conseil juridique. En cas de doute et en cas de "
        "litige, adressez-vous à une avocate ou à un avocat, pas à cette page."],
    fuss=("Chiffres mesurés entre le 1er et le 3 août 2026, chacun relié à sa méthode "
          "et à ses données brutes."),
    korrekturen="Les corrections sont bienvenues et faites en public :",
    l_issue="ouvrir un ticket",
    offenlegung1=("Divulgation : l’auteur développe Full Page PDF Snap, l’extension "
                  "nommée sur cette page. L’impression PDF propre au navigateur est"),
    l_offenlegung="mesurée face à elle",
    offenlegung2=", y compris là où l’impression l’emporte.",
    disclaimer="Avertissement",
)

# ------------------------------------------------------------------- Italiano
INHALT["it"] = _seite(
    h1="Salvare una pagina web in PDF — un foglio, con la fonte e la data di consultazione sopra",
    standfirst=(
        "In breve: un’estensione di cattura al posto della finestra di stampa. "
        "L’esportazione di stampa divide in pagine — lo stesso articolo è uscito come "
        "<strong>26 pagine, e 9 interruzioni hanno tagliato a metà una frase</strong>. "
        "Una cattura scrive un foglio continuo e può scrivervi dentro la provenienza e "
        "l’ora di consultazione."),
    meta="3 agosto 2026 · ogni cifra rimanda alla misurazione che le sta dietro",
    btn_ff="Firefox, computer e Android",
    install=(
        "Gratuito, licenza MIT, gira sul dispositivo. Edge chiede una volta se sono "
        "ammesse estensioni da altri store; Opera ha prima bisogno della sua estensione "
        f"<em>Install Chrome Extensions</em>. Poi: apri la pagina, premi "
        f"<code>{_KUERZEL}</code> oppure fai clic sull’icona."),
    h2=["Stampare o catturare? Il confronto onesto",
        "Dietro un accesso o una barriera a cui hai diritto",
        "Sul telefono",
        "Perché la data di consultazione va nel file",
        "Un’intera lista di fonti in una volta",
        "Che cosa non fa"],
    tabelle=_tabelle(
        "Esportazione di stampa", "Cattura a pagina intera",
        ["Lo stesso articolo dà", "Interruzioni a metà frase",
         "Testo selezionabile e ricercabile", "Costa qualcosa"],
        "{n} pagine", "{n} foglio", "{n}", "{n}",
        "no, è integrata", "no"),
    p_druck=(
        "<strong>Sul testo la cattura è in vantaggio da quando porta uno strato di "
        "testo — 91,5 % contro 87,6 %, misurato il 5 agosto.</strong> Chi ha bisogno solo "
        "di una copia leggibile e ricercabile e non è disturbato dalla suddivisione in "
        "pagine se la cava con la funzione già presente nel browser — lo si scrive qui "
        "invece di tacerlo. Una cattura conviene quando conta l’impaginazione, quando "
        "un’interruzione cadrebbe dentro una tabella, o quando i dati della fonte "
        "devono viaggiare con il file."),
    l_druck="Metodo e dati grezzi",
    p_login=(
        "Un’estensione di cattura legge ciò che la tua sessione già mostra: un articolo "
        "di rivista in licenza, un’aula virtuale, una conferma d’ordine — salvato come "
        "lo vedi. Nessun servizio lato server può farlo. Misurato su 20 fonti miste, un "
        "lettore lato server è stato respinto in pieno da 5 di esse. Salvare una pagina "
        f"che hai diritto di leggere è una copia per uso personale ({_PARAGRAF}) — non "
        "una via verso contenuti senza accesso."),
    p_handy=(
        "Solo Firefox. <strong>Chrome per Android non installa alcuna "
        "estensione</strong>, quindi la domanda si pone soltanto lì. Di 248 estensioni "
        "verificate, 60 dichiarano il supporto ad Android — nessuna era stata provata "
        "prima."),
    l_android="La misurazione su Android",
    p_quelle=(
        "Un indirizzo in bibliografia è una promessa su una pagina che non ti "
        "appartiene. Verificato su 150 fonti prese da bibliografie reali: <strong>il "
        "19,3 % era sparito</strong>, l’8,7 % non era archiviato da nessuna parte, e "
        "dove una copia esisteva era vecchia in media di 603 giorni. In una pagina "
        "senza data di pubblicazione, l’ora di consultazione è l’unica data che il "
        "riferimento possa portare — ed esiste solo nell’istante in cui guardi."),
    l_quelle="Che cosa succede a una fonte dopo che la si è citata",
    p_ris=(
        "Una cattura lo scrive dentro: autori, titolo, DOI, licenza e l’ora esatta — "
        "nel PDF e in un record RIS accanto, che Zotero, Citavi, EndNote e Mendeley "
        "leggono."),
    p_liste=(
        "Per una bibliografia invece che per una singola pagina, la parte maggiore non "
        "ha bisogno di alcun browser. Di 20 fonti miste, <strong>10 sono diventate "
        "record completi in 8,1 secondi</strong> con RIS e BibTeX — senza account, "
        "senza chiave. Le altre dieci tornano con la motivazione, così sai quali "
        "indirizzi devi aprire da solo."),
    l_rezepte="Le ricette",
    l_messung="la misurazione",
    li=["Non raggiunge contenuti a cui non hai accesso.",
        "Una cattura dello schermo non è un documento elettronico qualificato. Fissa "
        "come appariva una pagina in un dato momento — che è cosa diversa dal provarlo.",
        "Dove un editore offre il proprio export <em>Cita → RIS</em>, quel file fa fede "
        "ed è migliore di tutto ciò che è ricostruito.",
        "Le indicazioni sul diritto d’autore in questa pagina sono un inquadramento, "
        "non una consulenza legale. Nel dubbio e in caso di controversia rivolgiti a "
        "un’avvocata o a un avvocato, non a questa pagina."],
    fuss=("Cifre misurate tra il 1º e il 3 agosto 2026, ciascuna collegata al metodo e "
          "ai dati grezzi."),
    korrekturen="Le correzioni sono benvenute e vengono fatte in pubblico:",
    l_issue="apri una segnalazione",
    offenlegung1=("Trasparenza: l’autore sviluppa Full Page PDF Snap, l’estensione "
                  "citata in questa pagina. La stampa in PDF integrata nel browser è"),
    l_offenlegung="misurata a confronto",
    offenlegung2=", compresi i casi in cui vince la stampa.",
    disclaimer="Avvertenze",
)

# --------------------------------------------------------------------- 日本語
INHALT["ja"] = _seite(
    h1="ウェブページを PDF として保存する — 1 枚の紙に、出典と取得日を載せて",
    standfirst=(
        "手短に言えば、印刷ダイアログではなくキャプチャ拡張機能を使う。印刷の書き出しは"
        "ページに分ける — 同じ記事が <strong>26 ページになり、9 か所の改ページが文の"
        "途中を切った</strong>。キャプチャは 1 枚の連続した紙に書き出し、出どころと"
        "取得時刻をその中に書き込める。"),
    meta="2026年8月3日 · どの数値も、その背後にある計測にリンクしている",
    btn_ff="Firefox（パソコンと Android）",
    install=(
        "無料、MIT ライセンス、処理は端末上で行われる。Edge は他のストアの拡張機能を"
        "認めるかを一度だけ尋ねる。Opera は先に拡張機能 <em>Install Chrome "
        f"Extensions</em> が必要になる。あとは、ページを開いて <code>{_KUERZEL}</code> を"
        "押すか、アイコンをクリックする。"),
    h2=["印刷かキャプチャか — 正直な比較",
        "ログインの向こう側、あるいは自分に権利のある制限の向こう側",
        "スマートフォンでは",
        "なぜ取得日がファイルの中に必要なのか",
        "出典リストをまとめて",
        "これができないこと"],
    tabelle=_tabelle(
        "印刷の書き出し", "全ページキャプチャ",
        ["同じ記事の結果", "文の途中での改ページ", "選択でき、検索できる文字", "費用"],
        "{n} ページ", "{n} 枚", "{n}", "{n}",
        "なし（標準機能）", "なし", dez="."),
    p_druck=(
        "<strong>文字については、テキスト層を備えて以来キャプチャが上回っている — "
        "91.5 % 対 87.6 %、8月5日の計測。</strong>読めて検索できる複製だけが"
        "必要で、ページに分かれることが気にならないなら、ブラウザーにもとから入っている"
        "機能で足りる — 黙っておかずに、ここに書いておく。キャプチャが値打ちを持つのは、"
        "レイアウトが物を言うとき、改ページが表を突き抜けてしまうとき、あるいは出典の"
        "記載がファイルと一緒に旅をすべきときだ。"),
    l_druck="方法と生データ",
    p_login=(
        "キャプチャ拡張機能が読むのは、あなた自身のセッションがすでに表示しているもので"
        "ある。ライセンス契約のある学術論文、講義の部屋、注文確認 — 見えているとおりに"
        "保存される。サーバー側のサービスにはできない。20 件の多様な出典で計測したところ、"
        "サーバー側のリーダーはそのうち 5 件から明確に拒否された。読む権利のあるページを"
        f"保存することは私的な複製であり（{_PARAGRAF}）、権利のない内容への近道ではない。"),
    p_handy=(
        "Firefox だけである。<strong>Chrome for Android は拡張機能をいっさい"
        "入れられない</strong>ので、この問いが立つのはそこだけだ。調べた 248 件の"
        "拡張機能のうち 60 件が Android 対応を掲げているが、それまで試された"
        "ものは一つもなかった。"),
    l_android="Android の計測",
    p_quelle=(
        "参考文献表のアドレスは、あなたのものではないページについての約束である。実際の"
        "文献表から取った 150 件の出典で確かめたところ、<strong>19.3 % は消えており"
        "</strong>、8.7 % はどこにも保存されていなかった。控えがあった場合でも、平均して "
        "603 日前のものだった。公開日のないページでは、取得の時刻だけが記載の担える"
        "唯一の日付になる — そしてそれは、あなたが見るその瞬間にしか存在しない。"),
    l_quelle="引用したあと、その出典に何が起きるか",
    p_ris=(
        "キャプチャはそれを書き込む。著者、タイトル、DOI、ライセンス、正確な時刻を — "
        "PDF の中に、そして隣に置く RIS レコードに。Zotero、Citavi、EndNote、Mendeley が"
        "それを読み込む。"),
    p_liste=(
        "一つのページではなく参考文献表が相手なら、大きい方の部分にブラウザーは要らない。"
        "20 件の多様な出典のうち、<strong>10 件が 8.1 秒で完全なレコードになった</strong>"
        " — RIS と BibTeX を伴い、アカウントも鍵もなしに。残る 10 件は理由を添えて返るので、"
        "どのアドレスを自分で開かねばならないかが分かる。"),
    l_rezepte="レシピ",
    l_messung="その計測",
    li=["権利のない内容に到達することはできない。",
        "画面のキャプチャは適格電子文書ではない。ある時点でページがどう見えたかを"
        "とどめるだけであり、それを証明することとは別である。",
        "出版社が独自の <em>引用 → RIS</em> 書き出しを備えている場合は、そのファイルが"
        "正であり、再構成したどれよりも優れている。",
        "このページの著作権に関する記述は位置づけであって、法律相談ではない。疑わしい"
        "とき、また争いになったときは、このページではなく弁護士に尋ねてほしい。"],
    fuss="数値は 2026年8月1日から3日のあいだに計測し、それぞれ方法と生データにリンクしている。",
    korrekturen="訂正は歓迎され、公開の場で行われる:",
    l_issue="issue を開く",
    offenlegung1=("開示: 著者は、このページで挙げた拡張機能 Full Page PDF Snap の"
                  "開発者である。ブラウザー自身の PDF 印刷は"),
    l_offenlegung="それと突き合わせて計測しており",
    offenlegung2="、印刷が勝つ場面も含めて示している。",
    disclaimer="免責事項",
)

# ---------------------------------------------------------------- Português BR
INHALT["pt-BR"] = _seite(
    h1="Salvar uma página web em PDF — uma folha, com a fonte e a data de consulta nela",
    standfirst=(
        "Em resumo: uma extensão de captura em vez da caixa de impressão. A exportação "
        "de impressão reparte em páginas — o mesmo artigo saiu como <strong>26 páginas, "
        "e 9 quebras cortaram no meio de uma frase</strong>. Uma captura escreve uma "
        "folha contínua e pode escrever nela a procedência e a hora da consulta."),
    meta="3 de agosto de 2026 · cada número remete à medição que está por trás",
    btn_ff="Firefox, computador e Android",
    install=(
        "Gratuito, licença MIT, roda no aparelho. O Edge pergunta uma vez se extensões "
        "de outras lojas são permitidas; o Opera precisa antes da sua extensão "
        f"<em>Install Chrome Extensions</em>. Depois: abra a página, pressione "
        f"<code>{_KUERZEL}</code> ou clique no ícone."),
    h2=["Imprimir ou capturar? A comparação honesta",
        "Atrás de um login ou de uma barreira à qual você tem acesso",
        "No celular",
        "Por que a data de consulta pertence ao arquivo",
        "Uma lista de fontes inteira de uma vez",
        "O que não faz"],
    tabelle=_tabelle(
        "Exportação de impressão", "Captura de página inteira",
        ["O mesmo artigo dá", "Quebras no meio da frase",
         "Texto selecionável e pesquisável", "Custa algo"],
        "{n} páginas", "{n} folha", "{n}", "{n}",
        "não, já vem embutido", "não"),
    p_druck=(
        "<strong>No texto, a captura está à frente desde que carrega uma camada de "
        "texto — 91,5 % contra 87,6 %, medido em 5 de agosto.</strong> Quem só precisa de "
        "uma cópia legível e pesquisável e não se incomoda com o reparte em páginas se "
        "vira com a função que já está no navegador — isso está escrito aqui, em vez de "
        "ser calado. Uma captura vale a pena quando o layout conta, quando uma quebra "
        "cairia atravessando uma tabela, ou quando os dados da fonte devem viajar com o "
        "arquivo."),
    l_druck="Método e dados brutos",
    p_login=(
        "Uma extensão de captura lê o que a sua própria sessão já mostra: um artigo de "
        "periódico licenciado, uma sala de curso, uma confirmação de pedido — salvo "
        "como você o vê. Nenhum serviço do lado do servidor consegue isso. Medido em 20 "
        "fontes variadas, um leitor do lado do servidor foi recusado de saída por 5 "
        "delas. Salvar uma página que você pode ler é uma cópia para uso próprio "
        f"({_PARAGRAF}) — não um caminho para conteúdos sem acesso."),
    p_handy=(
        "Só o Firefox. <strong>O Chrome para Android não instala extensão "
        "nenhuma</strong>, então a pergunta só se coloca ali. De 248 extensões "
        "verificadas, 60 declaram suporte a Android — nenhuma delas tinha sido testada "
        "antes."),
    l_android="A medição no Android",
    p_quelle=(
        "Um endereço na bibliografia é uma promessa sobre uma página que não é sua. "
        "Verificado em 150 fontes de listas de referências reais: <strong>19,3 % tinham "
        "sumido</strong>, 8,7 % não estavam arquivadas em lugar nenhum, e onde havia uma "
        "cópia, ela tinha em média 603 dias. Numa página sem data de publicação, a hora "
        "da consulta é a única data que a referência pode carregar — e ela só existe no "
        "momento em que você olha."),
    l_quelle="O que acontece com uma fonte depois de tê-la citado",
    p_ris=(
        "Uma captura escreve isso dentro: autores, título, DOI, licença e a hora exata "
        "— no PDF e num registro RIS ao lado, que o Zotero, o Citavi, o EndNote e o "
        "Mendeley leem."),
    p_liste=(
        "Para uma bibliografia em vez de uma única página, a maior parte não precisa de "
        "navegador algum. De 20 fontes variadas, <strong>10 viraram registros completos "
        "em 8,1 segundos</strong> com RIS e BibTeX — sem conta, sem chave. As outras dez "
        "voltam com a justificativa, para você saber quais endereços precisa abrir você "
        "mesmo."),
    l_rezepte="As receitas",
    l_messung="a medição",
    li=["Não alcança conteúdos aos quais você não tem acesso.",
        "Uma captura de tela não é um documento eletrônico qualificado. Ela retém como "
        "uma página estava num dado momento — o que é diferente de prová-lo.",
        "Onde uma editora oferece a própria exportação <em>Citar → RIS</em>, esse "
        "arquivo é o que vale e é melhor do que tudo o que for reconstruído.",
        "As observações sobre direito autoral nesta página são um enquadramento, não "
        "aconselhamento jurídico. Na dúvida e em caso de litígio, pergunte a uma "
        "advogada ou a um advogado, não a esta página."],
    fuss=("Números medidos entre 1 e 3 de agosto de 2026, cada um ligado ao método e "
          "aos dados brutos."),
    korrekturen="Correções são bem-vindas e feitas em público:",
    l_issue="abrir uma issue",
    offenlegung1=("Divulgação: o autor desenvolve o Full Page PDF Snap, a extensão "
                  "citada nesta página. A impressão em PDF do próprio navegador é"),
    l_offenlegung="medida contra ela",
    offenlegung2=", inclusive onde a impressão ganha.",
    disclaimer="Aviso legal",
)

# -------------------------------------------------------------------- Русский
INHALT["ru"] = _seite(
    h1="Сохранить веб-страницу в PDF — одним листом, с источником и датой обращения на нём",
    standfirst=(
        "Коротко: расширение для съёмки вместо диалога печати. Экспорт на печать "
        "разбивает на страницы — та же статья вышла как <strong>26 страниц, и 9 "
        "разрывов прошли посреди предложения</strong>. Съёмка пишет один непрерывный "
        "лист и может вписать в него происхождение и время обращения."),
    meta="3 августа 2026 · каждое число отсылает к измерению, которое стоит за ним",
    btn_ff="Firefox, компьютер и Android",
    install=(
        "Бесплатно, лицензия MIT, работает на устройстве. Edge один раз спрашивает, "
        "допускать ли расширения из других магазинов; Opera сначала требует своё "
        f"расширение <em>Install Chrome Extensions</em>. Дальше: откройте страницу, "
        f"нажмите <code>{_KUERZEL}</code> или щёлкните по значку."),
    h2=["Печатать или снимать? Честное сравнение",
        "За логином или за преградой, к которой у вас есть доступ",
        "На телефоне",
        "Почему дата обращения должна быть в файле",
        "Весь список источников разом",
        "Чего это не делает"],
    tabelle=_tabelle(
        "Экспорт на печать", "Съёмка всей страницы",
        ["Та же статья даёт", "Разрывы посреди предложения",
         "Выделяемый, доступный поиску текст", "Стоит ли денег"],
        "{n} страниц", "{n} лист", "{n}", "{n}",
        "нет, встроено", "нет"),
    p_druck=(
        "<strong>По тексту съёмка впереди с тех пор, как она несёт текстовый слой — "
        "91,5 % против 87,6 %, измерено 5 августа.</strong> Кому нужна только "
        "читаемая, доступная поиску копия и кого не смущает разбиение на страницы, тому "
        "хватит функции, которая уже есть в браузере, — это написано здесь, а не "
        "умолчано. Съёмка окупается, когда важна вёрстка, когда разрыв пришёлся бы на "
        "таблицу, или когда сведения об источнике должны путешествовать вместе с "
        "файлом."),
    l_druck="Метод и исходные данные",
    p_login=(
        "Расширение для съёмки читает то, что ваша собственная сессия и так "
        "показывает: лицензированную журнальную статью, учебный курс, подтверждение "
        "заказа — сохранённые так, как вы их видите. Никакая серверная служба этого не "
        "может. На 20 разнородных источниках серверному читателю отказали 5 из них "
        "наотрез. Сохранить страницу, которую вам позволено читать, — это копия для "
        f"личного пользования ({_PARAGRAF}), а не путь к содержимому без доступа."),
    p_handy=(
        "Только Firefox. <strong>Chrome для Android не устанавливает расширений "
        "вовсе</strong>, так что вопрос возникает лишь здесь. Из 248 проверенных "
        "расширений 60 заявляют поддержку Android — ни одно из них до этого не "
        "испытывали."),
    l_android="Измерение на Android",
    p_quelle=(
        "Адрес в списке литературы — это обещание о странице, которая вам не "
        "принадлежит. Проверено на 150 источниках из реальных списков: <strong>19,3 % "
        "исчезли</strong>, 8,7 % нигде не были заархивированы, а там, где копия "
        "сохранилась, ей было в среднем 603 дня. У страницы без даты публикации время "
        "обращения — единственная дата, которую может нести описание, и она существует "
        "только в тот момент, когда вы смотрите."),
    l_quelle="Что происходит с источником после того, как его процитировали",
    p_ris=(
        "Съёмка вписывает это внутрь: авторов, заглавие, DOI, лицензию и точное время — "
        "в PDF и в запись RIS рядом, которую читают Zotero, Citavi, EndNote и Mendeley."),
    p_liste=(
        "Для списка литературы, а не для отдельной страницы, большая часть работы "
        "обходится вовсе без браузера. Из 20 разнородных источников <strong>10 стали "
        "полными записями за 8,1 секунды</strong> с RIS и BibTeX — без учётной записи и "
        "без ключа. Остальные десять возвращаются с обоснованием, чтобы вы знали, какие "
        "адреса придётся открыть самому."),
    l_rezepte="Рецепты",
    l_messung="измерение",
    li=["Оно не даёт доступа к содержимому, которого у вас нет.",
        "Снимок экрана — не квалифицированный электронный документ. Он удерживает то, "
        "как страница выглядела в определённый момент, — а это не то же самое, что "
        "доказать это.",
        "Там, где издатель предлагает собственный экспорт <em>Цитировать → RIS</em>, "
        "именно этот файл имеет силу и лучше всего восстановленного.",
        "Замечания об авторском праве на этой странице — это оценка, а не юридическая "
        "консультация. В сомнительном случае и при споре спросите адвоката, а не эту "
        "страницу."],
    fuss=("Числа измерены между 1 и 3 августа 2026 года, каждое связано с методом и "
          "исходными данными."),
    korrekturen="Исправления приветствуются и вносятся публично:",
    l_issue="открыть issue",
    offenlegung1=("Раскрытие: автор разрабатывает Full Page PDF Snap — расширение, "
                  "названное на этой странице. Встроенная в браузер печать в PDF"),
    l_offenlegung="измерена в сравнении с ним",
    offenlegung2=", включая случаи, где печать выигрывает.",
    disclaimer="Отказ от ответственности",
)

# --------------------------------------------------------------------- 简体中文
INHALT["zh-CN"] = _seite(
    h1="把网页保存为 PDF —— 一整张，并带上出处与访问日期",
    standfirst=(
        "简单说：用抓取扩展，而不是打印对话框。打印导出会把内容分成许多页——同一篇文章"
        "印出来是 <strong>26 页，9 处分页从句子中间切开</strong>。抓取写出的是一张连续"
        "的长纸，还能把来源和访问时间写进去。"),
    meta="2026年8月3日 · 每一个数字都指向它背后的那次测量",
    btn_ff="Firefox（桌面与 Android）",
    install=(
        "免费，MIT 许可，在本机上运行。Edge 会问一次是否允许来自其他商店的扩展；"
        "Opera 需要先装它自己的扩展 <em>Install Chrome Extensions</em>。然后：打开网页，"
        f"按 <code>{_KUERZEL}</code> 或点击图标。"),
    h2=["打印还是抓取？一个诚实的对比",
        "在登录墙或你有权访问的门槛之后",
        "在手机上",
        "为什么访问日期应当写进文件",
        "一次处理整份来源清单",
        "它做不到的事"],
    tabelle=_tabelle(
        "打印导出", "整页抓取",
        ["同一篇文章的结果", "句子中间的分页", "可选中、可检索的文字", "是否花钱"],
        "{n} 页", "{n} 张", "{n}", "{n}",
        "不花钱，系统自带", "不花钱", dez="."),
    p_druck=(
        "<strong>论文字，自从抓取带上了文本层，它就领先了——91.5 % 对 87.6 %，"
        "测量于 8月5日。</strong>只需要一份能读、能搜的副本，"
        "又不介意内容被分成许多页的人，用浏览器里现成的功能就够了——这一点写在这里，"
        "而不是避而不谈。抓取值得的时候是：版面要紧、某个分页会穿过一张表格，"
        "或者出处信息必须跟着文件一起走。"),
    l_druck="方法与原始数据",
    p_login=(
        "抓取扩展读的是你自己的会话本就显示出来的内容：有订阅的期刊论文、课程空间、"
        "订单确认——你看到什么样，就保存成什么样。服务器端的服务做不到这一点。"
        "在 20 个混合来源上测量，服务器端阅读器被其中 5 个直接拒绝。保存一个你有权阅读的"
        f"页面，是供自己使用的复制件（{_PARAGRAF}）——不是通往无权访问内容的路径。"),
    p_handy=(
        "只有 Firefox。<strong>Chrome for Android 根本不安装任何扩展</strong>，"
        "所以这个问题只在那里出现。在核查过的 248 个扩展中，60 个声明支持 Android"
        "——此前没有一个真正试过。"),
    l_android="Android 测量",
    p_quelle=(
        "参考文献里的一个网址，是对一个并不属于你的页面所作的承诺。以真实文献表中的 "
        "150 个来源核查：<strong>19.3 % 已经消失</strong>，8.7 % 在任何地方都没有存档；"
        "而在有备份的地方，它平均已有 603 天之久。对于没有出版日期的页面，"
        "访问时间是这条著录唯一能承载的日期——而它只存在于你查看的那一刻。"),
    l_quelle="一个来源在被引用之后会怎样",
    p_ris=(
        "抓取会把这些写进去：作者、标题、DOI、许可与准确时间——写在 PDF 里，"
        "并在旁边附一份 RIS 记录，Zotero、Citavi、EndNote 和 Mendeley 都能读入。"),
    p_liste=(
        "如果要的是一份参考文献表而不是单个页面，其中较大的一部分根本不需要浏览器。"
        "20 个混合来源中，<strong>10 个在 8.1 秒内成为完整记录</strong>，带 RIS 与 "
        "BibTeX——不要账号，不要密钥。另外十个会连同理由一起退回，"
        "好让你知道哪些网址必须自己打开。"),
    l_rezepte="配方",
    l_messung="那次测量",
    li=["它无法取得你没有权限的内容。",
        "屏幕抓取不是合格的电子文书。它留下的是一个页面在某一时刻的样子——"
        "这与证明它是两回事。",
        "凡是出版方提供了自己的 <em>引用 → RIS</em> 导出，那份文件才是权威的，"
        "胜过一切重建出来的东西。",
        "本页关于著作权的说明是一种归类，不是法律咨询。有疑问时、发生争议时，"
        "请询问律师，而不是这个页面。"],
    fuss="数据测量于 2026年8月1日至3日之间，每一项都链接到方法与原始数据。",
    korrekturen="欢迎指正，更正将公开进行：",
    l_issue="提交 issue",
    offenlegung1=("披露：作者是本页所提到的扩展 Full Page PDF Snap 的开发者。"
                  "浏览器自带的打印成 PDF 已经"),
    l_offenlegung="与之做过对比测量",
    offenlegung2="，包括打印占优的情形。",
    disclaimer="免责声明",
)
