#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/how-to/save-a-webpage-as-pdf/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite docs/how-to/save-a-webpage-as-pdf/
index.html, woertlich uebernommen — nicht build-einstiegsseiten.py, der beide
Einstiegsseiten aus einer Vorlage erzeugt und beim naechsten Lauf die
Neunsprachen-Auszeichnung wieder ueberschriebe.

Die deutsche Schwesterseite /anleitung/webseite-als-pdf-speichern/ ist NICHT
derselbe Text (texte_anleitung_pdf.py): sie fuehrt zusaetzlich § 42 UrhG und
einen vierten Punkt zur Rechtsberatung, nennt die Add-ons-API nicht und traegt
ein anderes Tastenkuerzel. Darum zwei Module statt eines gemeinsamen.

EINE Ausnahme von „die Datei auf der Platte ist die Quelle": Tabellenzeile 3
und der Absatzanfang darunter standen dort mit 94.8 % / 92.6 % und „Print wins
on text" — genau den Zahlen, die Commit 3c57e3b (#18, „withdraw the old
figures") zurueckgezogen hat. Die Arbeitskopie war an dieser Stelle die Ausgabe
eines veralteten build-einstiegsseiten.py (Zeile 164), also aelter als der
eingecheckte Text. Uebernommen ist deshalb die Fassung aus HEAD: 87.6 % gegen
91.5 %, gemessen am 5. August, mit der Aufnahme vorn. Neunmal eine
zurueckgezogene Messung zu veroeffentlichen waere der teuerste Fehler dieser
Seite gewesen.

Unveraendert in jeder Sprache: alle Zahlen (26, 9, 1, 0, 87.6 %, 91.5 %, 20, 5,
248, 60, 150, 19.3 %, 8.7 %, 603, 8.1 s, 10), Versionsangaben (Chrome 116+),
Dateiformate und Werkzeugnamen (PDF, RIS, BibTeX, HTTP, DOI, OCR, MIT, Zotero,
Citavi, EndNote, Mendeley, Full Page PDF Snap, Install Chrome Extensions), das
Tastenkuerzel <code>Alt+Shift+Y</code> und alle Adressen. Nur die Schreibweise
des Dezimalzeichens folgt der Sprache (91,5 % im Deutschen) — die Messung ist
dieselbe.

Rendern:  python3 tools/seite-neunsprachig.py texte_howto_pdf.py
"""

URL = "https://provinglab.dev/how-to/save-a-webpage-as-pdf/"
ZIEL = "how-to/save-a-webpage-as-pdf/index.html"
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
_KUERZEL = "Alt+Shift+Y"
_CHROME = "Chrome 116+, Edge, Brave, Vivaldi"


def _tabelle(th_druck, th_aufnahme, zeilen,
             c_seiten, c_blatt, c_recall_druck, c_recall_aufnahme,
             c_eingebaut, c_nein, dez="."):
    """Die Vergleichstabelle. Die Messwerte stehen NUR hier — sie neunmal
    abzuschreiben hiesse, neun Gelegenheiten zu schaffen, eine Zahl zu
    verlieren. Die Zellentexte kommen als Vorlage mit {n} herein, damit die
    Zahl auch dort stehen kann, wo die Sprache sie hinstellt."""
    seiten = c_seiten.replace("{n}", "26")
    blatt = c_blatt.replace("{n}", "1")
    r_druck = c_recall_druck.replace("{n}", f"87{dez}6 %")
    r_aufnahme = c_recall_aufnahme.replace("{n}", f"91{dez}5 %")
    return f'''<table>
  <thead><tr><th scope="col"></th><th scope="col">{th_druck}</th><th scope="col">{th_aufnahme}</th></tr></thead>
  <tbody>
    <tr><td>{zeilen[0]}</td><td>{seiten}</td><td><strong>{blatt}</strong></td></tr>
    <tr><td>{zeilen[1]}</td><td>9</td><td>0</td></tr>
    <tr><td>{zeilen[2]}</td><td><strong>{r_druck}</strong></td><td><strong>{r_aufnahme}</strong></td></tr>
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

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="How to save a web page as a PDF — one sheet, with its source on it",
    standfirst=(
        "The short answer: use a capture extension, not the print dialog. Print "
        "paginates — the same article came out as <strong>26 pages with 9 breaks "
        "cutting through a sentence</strong>. A capture writes one continuous sheet "
        "and can stamp the page with where it came from and when."),
    meta=("3 August 2026 · every figure on this page links to the "
          "measurement it comes from"),
    btn_ff="Firefox, desktop and Android",
    install=(
        "Free, MIT licensed, runs on the device. Edge asks once to allow extensions "
        "from other stores; Opera needs its <em>Install Chrome Extensions</em> add-on "
        f"first. Then: open the page, press <code>{_KUERZEL}</code> or click the icon."),
    h2=["Print to PDF or capture? The honest comparison",
        "Behind a login or a paywall you have access to",
        "On a phone",
        "Why the file should carry its source",
        "A whole reading list at once",
        "What this does not do"],
    tabelle=_tabelle(
        "Browser print", "Full-page capture",
        ["Same article comes out as", "Page breaks cutting a sentence",
         "Text you can select and search", "Costs anything"],
        "{n} pages", "{n} sheet", "{n} recall", "{n} recall",
        "no, built in", "no"),
    p_druck=(
        "<strong>The capture leads on text since it carries a text layer — 91.5 % "
        "against 87.6 %, measured 5 August.</strong> If all you need is a readable, searchable "
        "copy and the pagination does not bother you, the function already in your "
        "browser is enough — and this page says so rather than pretending otherwise. "
        "A capture is worth it when the layout matters, when a break would fall through "
        "a table, or when the source details have to travel with the file."),
    l_druck="Method and raw data",
    p_login=(
        "A capture extension reads what your own session already shows. A licensed "
        "journal article, a course page, an order confirmation — saved as you see it. "
        "No server-side converter can do this, because it does not have your session: "
        "measured across 20 mixed sources, a server-side reader was refused by 5 of "
        "them outright. Capturing a page you may read is a copy for your own use; it is "
        "not a route to content you do not have access to."),
    p_handy=(
        "Only Firefox. <strong>Chrome for Android installs no extensions at all</strong>, "
        "so the question only arises there. Of 248 page-saving extensions checked "
        "against the add-ons API, 60 declare Android support and none had been tested on "
        "a device before we did."),
    l_android="The Android measurement",
    p_quelle=(
        "A URL in a bibliography is a promise about a page you do not control. Checked "
        "against 150 sources taken from real reference lists: <strong>19.3 % were "
        "gone</strong>, 8.7 % had no archived copy anywhere, and where a snapshot "
        "existed it was a median of 603 days old. For a page that declares no "
        "publication date, the time of retrieval is the only date a reference can carry "
        "— and it exists only at the moment you look."),
    l_quelle="What happens to a source after you cite it",
    p_ris=(
        "A capture can write that in: authors, title, DOI, licence and the exact time, "
        "inside the PDF and in an RIS record beside it — a format that imports into "
        "Zotero, Citavi, EndNote or Mendeley."),
    p_liste=(
        "For a bibliography rather than a single page, most of the work needs no "
        "browser. Of 20 mixed sources, <strong>10 became complete records with RIS and "
        "BibTeX in 8.1 seconds</strong> over plain HTTP — no account, no key. The other "
        "ten are handed back with the reason, so you know which addresses need you."),
    l_rezepte="The recipes",
    l_messung="the measurement",
    li=["It does not reach content you have no access to.",
        "A screen capture is not a qualified electronic document. It records what a "
        "page looked like at a time, which is a different thing from proving it.",
        "Where a publisher offers its own <em>Cite → RIS</em> export, that file is "
        "authoritative and better than anything reconstructed from the page."],
    fuss=("Figures measured between 1 and 3 August 2026, each linked to its method "
          "and raw data."),
    korrekturen="Corrections are welcome and are made in public:",
    l_issue="open an issue",
    offenlegung1=("Disclosure: the author develops Full Page PDF Snap, the extension "
                  "named on this page. The browser's own print-to-PDF is"),
    l_offenlegung="measured against it",
    offenlegung2=", including where print wins.",
    disclaimer="Disclaimer",
)

# ------------------------------------------------------------------- Deutsch
INHALT["de"] = _seite(
    h1="Wie man eine Webseite als PDF speichert — ein Blatt, mit der Quelle darauf",
    standfirst=(
        "Die kurze Antwort: eine Aufnahme-Erweiterung, nicht der Druckdialog. Der "
        "Druck teilt in Seiten auf — derselbe Artikel kam als <strong>26 Seiten "
        "heraus, mit 9 Umbrüchen mitten durch einen Satz</strong>. Eine Aufnahme "
        "schreibt ein durchgehendes Blatt und kann der Seite aufprägen, woher sie "
        "stammt und wann."),
    meta=("3. August 2026 · jede Zahl auf dieser Seite verweist auf die Messung, "
          "aus der sie stammt"),
    btn_ff="Firefox, Rechner und Android",
    install=(
        "Kostenlos, MIT-Lizenz, läuft auf dem Gerät. Edge fragt einmal, ob "
        "Erweiterungen aus anderen Stores zugelassen werden; Opera braucht zuerst "
        "seine Erweiterung <em>Install Chrome Extensions</em>. Dann: Seite öffnen, "
        f"<code>{_KUERZEL}</code> drücken oder auf das Symbol klicken."),
    h2=["Drucken oder aufnehmen? Der ehrliche Vergleich",
        "Hinter einem Login oder einer Schranke, zu der Sie Zugang haben",
        "Am Handy",
        "Warum die Datei ihre Quelle tragen sollte",
        "Eine ganze Leseliste auf einmal",
        "Was es nicht leistet"],
    tabelle=_tabelle(
        "Druckexport des Browsers", "Vollseiten-Aufnahme",
        ["Derselbe Artikel ergibt", "Umbrüche mitten im Satz",
         "Markier- und durchsuchbarer Text", "Kostet etwas"],
        "{n} Seiten", "{n} Blatt", "{n} Trefferquote", "{n} Trefferquote",
        "nein, eingebaut", "nein", dez=","),
    p_druck=(
        "<strong>Beim Text liegt die Aufnahme vorn, seit sie eine Textebene trägt — "
        "91,5 % gegen 87,6 %, gemessen am 5. August.</strong> Wer nur eine lesbare, "
        "durchsuchbare Kopie braucht und sich an der Seitenaufteilung nicht stört, "
        "kommt mit der Funktion aus, die im Browser schon steckt — und diese Seite "
        "sagt das, statt etwas anderes vorzugeben. Eine Aufnahme lohnt sich, wenn "
        "das Layout zählt, wenn ein Umbruch durch eine Tabelle fiele, oder wenn die "
        "Quellenangaben mit der Datei mitreisen sollen."),
    l_druck="Methode und Rohdaten",
    p_login=(
        "Eine Aufnahme-Erweiterung liest, was Ihre eigene Sitzung ohnehin zeigt. Ein "
        "lizenzierter Zeitschriftenartikel, ein Kursraum, eine Bestellbestätigung — "
        "gesichert, wie Sie es sehen. Kein serverseitiger Umwandler kann das, weil er "
        "Ihre Sitzung nicht hat: gemessen an 20 gemischten Quellen wurde ein "
        "serverseitiger Leser von 5 davon rundweg abgewiesen. Eine Seite zu sichern, "
        "die Sie lesen dürfen, ist eine Kopie zum eigenen Gebrauch; es ist kein Weg "
        "zu Inhalten, zu denen Sie keinen Zugang haben."),
    p_handy=(
        "Nur Firefox. <strong>Chrome für Android installiert überhaupt keine "
        "Erweiterungen</strong>, die Frage stellt sich also nur dort. Von 248 "
        "Seiten-Speicher-Erweiterungen, die gegen die Add-ons-API geprüft wurden, "
        "geben 60 Android-Unterstützung an, und keine davon war vor uns auf einem "
        "Gerät getestet worden."),
    l_android="Die Android-Messung",
    p_quelle=(
        "Eine Adresse im Literaturverzeichnis ist ein Versprechen über eine Seite, "
        "die Sie nicht in der Hand haben. Geprüft an 150 Quellen aus echten "
        "Verzeichnissen: <strong>19,3 % waren verschwunden</strong>, 8,7 % waren "
        "nirgends archiviert, und wo eine Sicherung bestand, war sie im Mittel 603 "
        "Tage alt. Bei einer Seite ohne Veröffentlichungsdatum ist der Zeitpunkt des "
        "Abrufs das einzige Datum, das eine Quellenangabe tragen kann — und es "
        "existiert nur in dem Moment, in dem Sie hinsehen."),
    l_quelle="Was mit einer Quelle geschieht, nachdem man sie zitiert hat",
    p_ris=(
        "Eine Aufnahme kann das hineinschreiben: Verfasser, Titel, DOI, Lizenz und "
        "die genaue Zeit, im PDF und in einem RIS-Satz daneben — ein Format, das "
        "sich in Zotero, Citavi, EndNote oder Mendeley einlesen lässt."),
    p_liste=(
        "Für ein Literaturverzeichnis statt einer einzelnen Seite braucht der größere "
        "Teil der Arbeit gar keinen Browser. Von 20 gemischten Quellen wurden "
        "<strong>10 in 8,1 Sekunden zu vollständigen Datensätzen mit RIS und "
        "BibTeX</strong>, über einfaches HTTP — ohne Konto, ohne Schlüssel. Die "
        "anderen zehn kommen mit Begründung zurück, damit Sie wissen, welche "
        "Adressen Sie selbst brauchen."),
    l_rezepte="Die Rezepte",
    l_messung="die Messung",
    li=["Es erreicht keine Inhalte, zu denen Sie keinen Zugang haben.",
        "Eine Bildschirmaufnahme ist kein qualifiziertes elektronisches Dokument. "
        "Sie hält fest, wie eine Seite zu einem Zeitpunkt aussah — das ist etwas "
        "anderes, als es zu beweisen.",
        "Wo ein Verlag einen eigenen <em>Zitieren → RIS</em>-Export anbietet, ist "
        "diese Datei maßgeblich und besser als alles aus der Seite Rekonstruierte."],
    fuss=("Zahlen gemessen zwischen dem 1. und 3. August 2026, jede mit ihrer "
          "Methode und ihren Rohdaten verlinkt."),
    korrekturen="Korrekturen sind willkommen und werden öffentlich vorgenommen:",
    l_issue="ein Issue eröffnen",
    offenlegung1=("Offenlegung: Der Autor entwickelt Full Page PDF Snap, die auf "
                  "dieser Seite genannte Erweiterung. Der eingebaute Druckexport des "
                  "Browsers wird"),
    l_offenlegung="dagegen gemessen",
    offenlegung2=", einschließlich der Fälle, in denen der Druck gewinnt.",
    disclaimer="Haftungsausschluss",
)

# ------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Cómo guardar una página web como PDF — una sola hoja, con su fuente encima",
    standfirst=(
        "La respuesta corta: una extensión de captura, no el diálogo de impresión. La "
        "impresión pagina — el mismo artículo salió como <strong>26 páginas con 9 "
        "saltos que cortaban una frase</strong>. Una captura escribe una hoja continua "
        "y puede estampar en la página de dónde vino y cuándo."),
    meta=("3 de agosto de 2026 · cada cifra de esta página enlaza con la medición "
          "de la que procede"),
    btn_ff="Firefox, escritorio y Android",
    install=(
        "Gratis, con licencia MIT, se ejecuta en el dispositivo. Edge pregunta una vez "
        "si permite extensiones de otras tiendas; Opera necesita antes su complemento "
        "<em>Install Chrome Extensions</em>. Después: abra la página, pulse "
        f"<code>{_KUERZEL}</code> o haga clic en el icono."),
    h2=["¿Imprimir a PDF o capturar? La comparación honesta",
        "Detrás de un inicio de sesión o de un muro de pago al que tiene acceso",
        "En el teléfono",
        "Por qué el archivo debe llevar su fuente",
        "Toda una lista de lecturas de una vez",
        "Lo que esto no hace"],
    tabelle=_tabelle(
        "Impresión del navegador", "Captura de página completa",
        ["El mismo artículo sale como", "Saltos de página que cortan una frase",
         "Texto que se puede seleccionar y buscar", "Cuesta algo"],
        "{n} páginas", "{n} hoja", "{n} de exhaustividad", "{n} de exhaustividad",
        "no, va incluido", "no", dez=","),
    p_druck=(
        "<strong>En el texto va por delante la captura desde que lleva una capa de "
        "texto — 91,5 % frente a 87,6 %, medido el 5 de agosto.</strong> Si solo necesita una copia "
        "legible y con búsqueda y la paginación no le molesta, la función que ya trae "
        "su navegador basta — y esta página lo dice en lugar de fingir lo contrario. "
        "Una captura merece la pena cuando importa la maquetación, cuando un salto "
        "caería en medio de una tabla, o cuando los datos de la fuente tienen que "
        "viajar con el archivo."),
    l_druck="Método y datos brutos",
    p_login=(
        "Una extensión de captura lee lo que su propia sesión ya muestra. Un artículo "
        "de revista con licencia, una página de curso, una confirmación de pedido — "
        "guardados tal como usted los ve. Ningún convertidor del lado del servidor "
        "puede hacerlo, porque no tiene su sesión: medido en 20 fuentes mixtas, un "
        "lector del lado del servidor fue rechazado de plano por 5 de ellas. Capturar "
        "una página que usted puede leer es una copia para uso propio; no es una vía "
        "hacia contenidos a los que no tiene acceso."),
    p_handy=(
        "Solo Firefox. <strong>Chrome para Android no instala ninguna "
        "extensión</strong>, así que la pregunta solo se plantea allí. De 248 "
        "extensiones para guardar páginas comprobadas contra la API de complementos, "
        "60 declaran compatibilidad con Android y ninguna había sido probada en un "
        "dispositivo antes de que lo hiciéramos nosotros."),
    l_android="La medición en Android",
    p_quelle=(
        "Una dirección en una bibliografía es una promesa sobre una página que usted "
        "no controla. Comprobado con 150 fuentes tomadas de listas de referencias "
        "reales: <strong>el 19,3 % había desaparecido</strong>, el 8,7 % no tenía "
        "copia archivada en ningún sitio, y donde existía una instantánea, tenía una "
        "mediana de 603 días. Para una página que no declara fecha de publicación, el "
        "momento de la consulta es la única fecha que puede llevar una referencia — y "
        "solo existe en el instante en que usted mira."),
    l_quelle="Qué le pasa a una fuente después de citarla",
    p_ris=(
        "Una captura puede escribirlo dentro: autores, título, DOI, licencia y la hora "
        "exacta, en el PDF y en un registro RIS al lado — un formato que se importa en "
        "Zotero, Citavi, EndNote o Mendeley."),
    p_liste=(
        "Para una bibliografía en lugar de una sola página, la mayor parte del trabajo "
        "no necesita navegador. De 20 fuentes mixtas, <strong>10 se convirtieron en "
        "registros completos con RIS y BibTeX en 8,1 segundos</strong> por HTTP simple "
        "— sin cuenta, sin clave. Las otras diez se devuelven con el motivo, para que "
        "sepa qué direcciones le necesitan a usted."),
    l_rezepte="Las recetas",
    l_messung="la medición",
    li=["No alcanza contenidos a los que usted no tiene acceso.",
        "Una captura de pantalla no es un documento electrónico cualificado. Registra "
        "cómo se veía una página en un momento dado, que es algo distinto de probarlo.",
        "Donde una editorial ofrece su propia exportación <em>Citar → RIS</em>, ese "
        "archivo es el que manda y es mejor que cualquier cosa reconstruida a partir "
        "de la página."],
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
    h1="Comment enregistrer une page web en PDF — une seule feuille, avec sa source dessus",
    standfirst=(
        "La réponse courte : une extension de capture, pas la boîte de dialogue "
        "d’impression. L’impression pagine — le même article est sorti en "
        "<strong>26 pages, avec 9 sauts coupant une phrase</strong>. Une capture écrit "
        "une feuille continue et peut inscrire sur la page d’où elle vient et quand."),
    meta=("3 août 2026 · chaque chiffre de cette page renvoie à la mesure dont il "
          "provient"),
    btn_ff="Firefox, ordinateur et Android",
    install=(
        "Gratuit, sous licence MIT, s’exécute sur l’appareil. Edge demande une fois "
        "d’autoriser les extensions d’autres boutiques ; Opera a d’abord besoin de son "
        "module <em>Install Chrome Extensions</em>. Ensuite : ouvrez la page, appuyez "
        f"sur <code>{_KUERZEL}</code> ou cliquez sur l’icône."),
    h2=["Imprimer en PDF ou capturer ? La comparaison honnête",
        "Derrière une connexion ou un accès payant dont vous disposez",
        "Sur un téléphone",
        "Pourquoi le fichier doit porter sa source",
        "Toute une liste de lectures d’un coup",
        "Ce que cela ne fait pas"],
    tabelle=_tabelle(
        "Impression du navigateur", "Capture pleine page",
        ["Le même article sort en", "Sauts de page coupant une phrase",
         "Texte sélectionnable et cherchable", "Coûte quelque chose"],
        "{n} pages", "{n} feuille", "{n} de rappel", "{n} de rappel",
        "non, intégré", "non", dez=","),
    p_druck=(
        "<strong>Sur le texte, la capture mène depuis qu’elle porte une couche de "
        "texte — 91,5 % contre 87,6 %, mesuré le 5 août.</strong> S’il vous faut seulement "
        "une copie lisible et cherchable et que la pagination ne vous gêne pas, la "
        "fonction déjà présente dans votre navigateur suffit — et cette page le dit "
        "plutôt que de prétendre le contraire. Une capture vaut la peine quand la mise "
        "en page compte, quand un saut tomberait au milieu d’un tableau, ou quand les "
        "indications de source doivent voyager avec le fichier."),
    l_druck="Méthode et données brutes",
    p_login=(
        "Une extension de capture lit ce que votre propre session affiche déjà. Un "
        "article de revue sous licence, une page de cours, une confirmation de "
        "commande — enregistrés tels que vous les voyez. Aucun convertisseur côté "
        "serveur ne peut le faire, car il n’a pas votre session : mesuré sur 20 sources "
        "variées, un lecteur côté serveur a été refusé net par 5 d’entre elles. "
        "Capturer une page que vous avez le droit de lire est une copie pour votre "
        "usage ; ce n’est pas un chemin vers des contenus auxquels vous n’avez pas "
        "accès."),
    p_handy=(
        "Seulement Firefox. <strong>Chrome pour Android n’installe aucune "
        "extension</strong>, la question ne se pose donc que là. Sur 248 extensions "
        "d’enregistrement de pages vérifiées auprès de l’API des modules, 60 déclarent "
        "la prise en charge d’Android et aucune n’avait été testée sur un appareil "
        "avant nous."),
    l_android="La mesure Android",
    p_quelle=(
        "Une adresse dans une bibliographie est une promesse au sujet d’une page que "
        "vous ne maîtrisez pas. Vérifié sur 150 sources tirées de vraies listes de "
        "références : <strong>19,3 % avaient disparu</strong>, 8,7 % n’avaient de copie "
        "archivée nulle part, et là où un instantané existait, il avait une médiane de "
        "603 jours. Pour une page qui ne déclare aucune date de publication, le moment "
        "de la consultation est la seule date qu’une référence puisse porter — et il "
        "n’existe qu’à l’instant où vous regardez."),
    l_quelle="Ce qu’il advient d’une source après qu’on l’a citée",
    p_ris=(
        "Une capture peut l’inscrire : auteurs, titre, DOI, licence et l’heure exacte, "
        "dans le PDF et dans une notice RIS à côté — un format qui s’importe dans "
        "Zotero, Citavi, EndNote ou Mendeley."),
    p_liste=(
        "Pour une bibliographie plutôt que pour une seule page, l’essentiel du travail "
        "n’a pas besoin de navigateur. Sur 20 sources variées, <strong>10 sont devenues "
        "des notices complètes avec RIS et BibTeX en 8,1 secondes</strong> en HTTP "
        "simple — sans compte, sans clé. Les dix autres sont rendues avec le motif, "
        "pour que vous sachiez quelles adresses ont besoin de vous."),
    l_rezepte="Les recettes",
    l_messung="la mesure",
    li=["Cela n’atteint pas des contenus auxquels vous n’avez pas accès.",
        "Une capture d’écran n’est pas un document électronique qualifié. Elle "
        "consigne l’aspect d’une page à un instant, ce qui n’est pas la même chose que "
        "de le prouver.",
        "Là où un éditeur propose son propre export <em>Citer → RIS</em>, ce fichier "
        "fait autorité et vaut mieux que tout ce qui est reconstruit à partir de la "
        "page."],
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
    h1="Come salvare una pagina web in PDF — un solo foglio, con la sua fonte sopra",
    standfirst=(
        "La risposta breve: un’estensione di cattura, non la finestra di stampa. La "
        "stampa impagina — lo stesso articolo è uscito come <strong>26 pagine con 9 "
        "interruzioni che tagliavano una frase</strong>. Una cattura scrive un foglio "
        "continuo e può imprimere sulla pagina da dove viene e quando."),
    meta=("3 agosto 2026 · ogni cifra di questa pagina rimanda alla misurazione da "
          "cui proviene"),
    btn_ff="Firefox, computer e Android",
    install=(
        "Gratuito, licenza MIT, gira sul dispositivo. Edge chiede una volta se "
        "consentire estensioni da altri store; Opera ha prima bisogno del suo "
        "componente <em>Install Chrome Extensions</em>. Poi: apri la pagina, premi "
        f"<code>{_KUERZEL}</code> oppure fai clic sull’icona."),
    h2=["Stampare in PDF o catturare? Il confronto onesto",
        "Dietro un accesso o un paywall a cui hai diritto",
        "Sul telefono",
        "Perché il file deve portare con sé la fonte",
        "Un’intera lista di letture in una volta",
        "Che cosa non fa"],
    tabelle=_tabelle(
        "Stampa del browser", "Cattura a pagina intera",
        ["Lo stesso articolo esce come", "Interruzioni di pagina che tagliano una frase",
         "Testo selezionabile e ricercabile", "Costa qualcosa"],
        "{n} pagine", "{n} foglio", "{n} di richiamo", "{n} di richiamo",
        "no, è integrata", "no", dez=","),
    p_druck=(
        "<strong>Sul testo la cattura è in vantaggio da quando porta uno strato di "
        "testo — 91,5 % contro 87,6 %, misurato il 5 agosto.</strong> Se serve solo una copia leggibile "
        "e ricercabile e l’impaginazione non disturba, basta la funzione già presente "
        "nel browser — e questa pagina lo dice invece di far finta di niente. Una "
        "cattura conviene quando conta l’impaginazione, quando un’interruzione "
        "cadrebbe dentro una tabella, o quando i dati della fonte devono viaggiare con "
        "il file."),
    l_druck="Metodo e dati grezzi",
    p_login=(
        "Un’estensione di cattura legge ciò che la tua sessione già mostra. Un articolo "
        "di rivista in licenza, una pagina di corso, una conferma d’ordine — salvati "
        "come li vedi. Nessun convertitore lato server può farlo, perché non ha la tua "
        "sessione: misurato su 20 fonti miste, un lettore lato server è stato respinto "
        "in pieno da 5 di esse. Catturare una pagina che puoi leggere è una copia per "
        "uso personale; non è una via verso contenuti a cui non hai accesso."),
    p_handy=(
        "Solo Firefox. <strong>Chrome per Android non installa alcuna "
        "estensione</strong>, quindi la domanda si pone soltanto lì. Di 248 estensioni "
        "per salvare pagine verificate tramite l’API dei componenti aggiuntivi, 60 "
        "dichiarano il supporto ad Android e nessuna era stata provata su un "
        "dispositivo prima di noi."),
    l_android="La misurazione su Android",
    p_quelle=(
        "Un indirizzo in bibliografia è una promessa su una pagina che non controlli. "
        "Verificato su 150 fonti prese da bibliografie reali: <strong>il 19,3 % era "
        "sparito</strong>, l’8,7 % non aveva copia archiviata da nessuna parte, e dove "
        "esisteva un’istantanea era vecchia in mediana di 603 giorni. Per una pagina "
        "che non dichiara una data di pubblicazione, il momento della consultazione è "
        "l’unica data che un riferimento possa portare — ed esiste solo nell’istante in "
        "cui guardi."),
    l_quelle="Che cosa succede a una fonte dopo che l’hai citata",
    p_ris=(
        "Una cattura può scriverlo dentro: autori, titolo, DOI, licenza e l’ora esatta, "
        "nel PDF e in un record RIS accanto — un formato che si importa in Zotero, "
        "Citavi, EndNote o Mendeley."),
    p_liste=(
        "Per una bibliografia invece che per una singola pagina, la maggior parte del "
        "lavoro non ha bisogno del browser. Di 20 fonti miste, <strong>10 sono "
        "diventate record completi con RIS e BibTeX in 8,1 secondi</strong> via "
        "semplice HTTP — senza account, senza chiave. Le altre dieci tornano indietro "
        "con la motivazione, così sai quali indirizzi hanno bisogno di te."),
    l_rezepte="Le ricette",
    l_messung="la misurazione",
    li=["Non raggiunge contenuti a cui non hai accesso.",
        "Una cattura dello schermo non è un documento elettronico qualificato. "
        "Registra come appariva una pagina in un dato momento, che è cosa diversa dal "
        "provarlo.",
        "Dove un editore offre il proprio export <em>Cita → RIS</em>, quel file fa fede "
        "ed è migliore di qualunque ricostruzione dalla pagina."],
    fuss=("Cifre misurate tra il 1º e il 3 agosto 2026, ciascuna collegata al proprio "
          "metodo e ai dati grezzi."),
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
    h1="ウェブページを PDF として保存する方法 — 1 枚の紙に、出典を載せて",
    standfirst=(
        "短い答え: 印刷ダイアログではなく、キャプチャ拡張機能を使う。印刷はページに"
        "分割する — 同じ記事が <strong>26 ページになり、9 か所の改ページが文の途中を"
        "切った</strong>。キャプチャは 1 枚の連続した紙に書き出し、どこから取得したか、"
        "そしていつ取得したかをページに刻める。"),
    meta="2026年8月3日 · このページの数値はすべて、その出どころとなった計測にリンクしている",
    btn_ff="Firefox（パソコンと Android）",
    install=(
        "無料、MIT ライセンス、処理は端末上で完結する。Edge は他のストアの拡張機能を"
        "許可するか一度だけ尋ねる。Opera は先に <em>Install Chrome Extensions</em> が"
        f"必要になる。あとは、ページを開いて <code>{_KUERZEL}</code> を押すか、"
        "アイコンをクリックするだけ。"),
    h2=["PDF に印刷するか、キャプチャするか — 正直な比較",
        "ログインの向こう側、あるいは自分に権利のある有料領域",
        "スマートフォンでは",
        "なぜファイルが出典を持つべきなのか",
        "文献リストをまとめて",
        "これができないこと"],
    tabelle=_tabelle(
        "ブラウザーの印刷", "全ページキャプチャ",
        ["同じ記事の出力", "文を分断する改ページ", "選択・検索できる文字", "費用"],
        "{n} ページ", "{n} 枚", "再現率 {n}", "再現率 {n}",
        "なし（標準機能）", "なし"),
    p_druck=(
        "<strong>文字については、テキスト層を備えて以来キャプチャが上回っている — "
        "91.5 % 対 87.6 %、8月5日の計測。</strong>読めて検索できる複製さえあればよく、"
        "ページ分割が気にならないなら、ブラウザーに最初から入っている機能で足りる — "
        "このページはそれを隠さずに書く。キャプチャが効くのは、レイアウトが意味を持つ"
        "とき、改ページが表を割ってしまうとき、あるいは出典の情報をファイルと一緒に"
        "運びたいときだ。"),
    l_druck="方法と生データ",
    p_login=(
        "キャプチャ拡張機能は、自分のセッションがすでに表示しているものを読み取る。"
        "ライセンス契約のある学術論文、講義ページ、注文確認 — 見えているとおりに"
        "保存される。サーバー側の変換サービスにはできない。あなたのセッションを"
        "持っていないからだ。20 件の多様な出典で計測したところ、サーバー側のリーダーは"
        "そのうち 5 件から明確に拒否された。読む権利のあるページを保存するのは私的な"
        "複製であって、権利のない内容に手を伸ばす方法ではない。"),
    p_handy=(
        "Firefox だけである。<strong>Chrome for Android は拡張機能をいっさい"
        "入れられない</strong>ので、この問いが立つのはそこだけだ。アドオン API に"
        "照らして調べた 248 件のページ保存拡張機能のうち、60 件が Android 対応を"
        "宣言しているが、私たちが試すまで、実機で確かめられたものは一つもなかった。"),
    l_android="Android の計測",
    p_quelle=(
        "参考文献のアドレスは、自分の手の届かないページについての約束である。実際の"
        "参考文献表から取った 150 件の出典を調べたところ、<strong>19.3 % はすでに"
        "消えており</strong>、8.7 % はどこにも保存されていなかった。控えが存在した"
        "場合でも、その古さは中央値で 603 日だった。公開日を示さないページでは、"
        "取得した時点だけが参考文献に載せられる唯一の日付になる — そしてそれは、"
        "見たその瞬間にしか存在しない。"),
    l_quelle="引用したあと、その出典に何が起きるか",
    p_ris=(
        "キャプチャはそれを書き込める。著者、タイトル、DOI、ライセンス、正確な時刻を "
        "PDF の中に、そして隣に置く RIS レコードに — Zotero、Citavi、EndNote、"
        "Mendeley が読み込める形式で。"),
    p_liste=(
        "1 ページではなく参考文献表が相手なら、作業の大半にブラウザーは要らない。"
        "20 件の多様な出典のうち、<strong>10 件が 8.1 秒で RIS と BibTeX を備えた"
        "完全なレコードになった</strong> — 素の HTTP で、アカウントも鍵もなしに。"
        "残る 10 件は理由を添えて返るので、どのアドレスに人手が要るかが分かる。"),
    l_rezepte="レシピ",
    l_messung="その計測",
    li=["権利のない内容に到達することはできない。",
        "画面のキャプチャは適格電子文書ではない。ある時点でページがどう見えたかを"
        "記録するだけであり、それを証明することとは別である。",
        "出版社が独自の <em>引用 → RIS</em> 書き出しを提供している場合は、その"
        "ファイルが正であり、ページから再構成したものより優れている。"],
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
    h1="Como salvar uma página web em PDF — uma única folha, com a fonte nela",
    standfirst=(
        "A resposta curta: uma extensão de captura, não a caixa de impressão. A "
        "impressão pagina — o mesmo artigo saiu como <strong>26 páginas com 9 quebras "
        "cortando uma frase</strong>. Uma captura escreve uma folha contínua e pode "
        "carimbar na página de onde ela veio e quando."),
    meta=("3 de agosto de 2026 · cada número desta página leva à medição de onde "
          "ele vem"),
    btn_ff="Firefox, computador e Android",
    install=(
        "Gratuito, licença MIT, roda no aparelho. O Edge pergunta uma vez se permite "
        "extensões de outras lojas; o Opera precisa antes da extensão <em>Install "
        f"Chrome Extensions</em>. Depois: abra a página, pressione <code>{_KUERZEL}</code> "
        "ou clique no ícone."),
    h2=["Imprimir em PDF ou capturar? A comparação honesta",
        "Atrás de um login ou de um paywall ao qual você tem acesso",
        "No celular",
        "Por que o arquivo deve carregar a sua fonte",
        "Uma lista de leitura inteira de uma vez",
        "O que isto não faz"],
    tabelle=_tabelle(
        "Impressão do navegador", "Captura de página inteira",
        ["O mesmo artigo sai como", "Quebras de página cortando uma frase",
         "Texto que dá para selecionar e buscar", "Custa algo"],
        "{n} páginas", "{n} folha", "{n} de revocação", "{n} de revocação",
        "não, já vem embutido", "não", dez=","),
    p_druck=(
        "<strong>No texto, a captura está à frente desde que carrega uma camada de "
        "texto — 91,5 % contra 87,6 %, medido em 5 de agosto.</strong> Se você só precisa de uma cópia "
        "legível e pesquisável e a paginação não incomoda, a função que já existe no "
        "navegador basta — e esta página diz isso em vez de fingir o contrário. Uma "
        "captura compensa quando o layout importa, quando uma quebra cairia no meio de "
        "uma tabela, ou quando os dados da fonte precisam viajar junto com o arquivo."),
    l_druck="Método e dados brutos",
    p_login=(
        "Uma extensão de captura lê o que a sua própria sessão já mostra. Um artigo de "
        "periódico licenciado, uma página de curso, uma confirmação de pedido — salvos "
        "como você os vê. Nenhum conversor do lado do servidor consegue isso, porque "
        "não tem a sua sessão: medido em 20 fontes variadas, um leitor do lado do "
        "servidor foi recusado de saída por 5 delas. Capturar uma página que você pode "
        "ler é uma cópia para uso próprio; não é um caminho para conteúdos aos quais "
        "você não tem acesso."),
    p_handy=(
        "Só o Firefox. <strong>O Chrome para Android não instala extensão "
        "nenhuma</strong>, então a pergunta só se coloca ali. De 248 extensões de "
        "salvar páginas verificadas contra a API de complementos, 60 declaram suporte "
        "a Android e nenhuma tinha sido testada num aparelho antes de nós."),
    l_android="A medição no Android",
    p_quelle=(
        "Um endereço numa bibliografia é uma promessa sobre uma página que não é sua. "
        "Verificado em 150 fontes tiradas de listas de referências reais: "
        "<strong>19,3 % tinham sumido</strong>, 8,7 % não tinham cópia arquivada em "
        "lugar nenhum, e onde havia um instantâneo ele tinha mediana de 603 dias. Para "
        "uma página que não declara data de publicação, o momento da consulta é a única "
        "data que uma referência pode carregar — e ela só existe no instante em que "
        "você olha."),
    l_quelle="O que acontece com uma fonte depois de você citá-la",
    p_ris=(
        "Uma captura pode escrever isso dentro: autores, título, DOI, licença e a hora "
        "exata, no PDF e num registro RIS ao lado — um formato que entra no Zotero, no "
        "Citavi, no EndNote ou no Mendeley."),
    p_liste=(
        "Para uma bibliografia em vez de uma única página, a maior parte do trabalho "
        "não precisa de navegador. De 20 fontes variadas, <strong>10 viraram registros "
        "completos com RIS e BibTeX em 8,1 segundos</strong> por HTTP simples — sem "
        "conta, sem chave. As outras dez voltam com o motivo, para você saber quais "
        "endereços precisam de você."),
    l_rezepte="As receitas",
    l_messung="a medição",
    li=["Não alcança conteúdos aos quais você não tem acesso.",
        "Uma captura de tela não é um documento eletrônico qualificado. Ela registra "
        "como uma página estava num momento, o que é diferente de prová-lo.",
        "Onde uma editora oferece a própria exportação <em>Citar → RIS</em>, esse "
        "arquivo é o que vale e é melhor do que qualquer coisa reconstruída a partir "
        "da página."],
    fuss=("Números medidos entre 1 e 3 de agosto de 2026, cada um ligado ao seu método "
          "e aos dados brutos."),
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
    h1="Как сохранить веб-страницу в PDF — одним листом, с указанием источника",
    standfirst=(
        "Короткий ответ: расширение для съёмки страницы, а не диалог печати. Печать "
        "разбивает на страницы — та же статья вышла как <strong>26 страниц, и 9 "
        "разрывов прошли посреди предложения</strong>. Съёмка пишет один непрерывный "
        "лист и может проставить на странице, откуда она взята и когда."),
    meta=("3 августа 2026 · каждое число на этой странице ведёт к измерению, из "
          "которого оно взято"),
    btn_ff="Firefox, компьютер и Android",
    install=(
        "Бесплатно, лицензия MIT, работает на устройстве. Edge один раз спросит, "
        "разрешить ли расширения из других магазинов; Opera сначала требует своё "
        "дополнение <em>Install Chrome Extensions</em>. Дальше: откройте страницу и "
        f"нажмите <code>{_KUERZEL}</code> или щёлкните по значку."),
    h2=["Печать в PDF или съёмка? Честное сравнение",
        "За логином или за платной стеной, к которой у вас есть доступ",
        "На телефоне",
        "Почему файл должен нести свой источник",
        "Весь список литературы разом",
        "Чего это не делает"],
    tabelle=_tabelle(
        "Печать браузера", "Съёмка всей страницы",
        ["Та же статья выходит как", "Разрывы страниц посреди предложения",
         "Текст, который можно выделить и найти", "Стоит ли денег"],
        "{n} страниц", "{n} лист", "полнота {n}", "полнота {n}",
        "нет, встроено", "нет", dez=","),
    p_druck=(
        "<strong>По тексту съёмка впереди с тех пор, как она несёт текстовый слой — "
        "91,5 % против 87,6 %, измерено 5 августа.</strong> Если нужна только читаемая и "
        "доступная поиску копия, а разбиение на страницы не мешает, хватит той "
        "функции, что уже есть в браузере, — и эта страница говорит об этом прямо, а "
        "не делает вид, будто иначе. Съёмка стоит того, когда важна вёрстка, когда "
        "разрыв пришёлся бы на таблицу или когда сведения об источнике должны "
        "путешествовать вместе с файлом."),
    l_druck="Метод и исходные данные",
    p_login=(
        "Расширение снимает то, что уже показывает ваша собственная сессия. "
        "Лицензированная журнальная статья, страница курса, подтверждение заказа — "
        "сохраняются такими, какими вы их видите. Серверная служба так не может, "
        "потому что у неё нет вашей сессии: на 20 разнородных источниках серверному "
        "читателю отказали 5 из них наотрез. Сохранить страницу, которую вам позволено "
        "читать, — это копия для личного пользования; это не путь к содержимому, к "
        "которому у вас нет доступа."),
    p_handy=(
        "Только Firefox. <strong>Chrome для Android не устанавливает расширений "
        "вовсе</strong>, так что вопрос возникает лишь здесь. Из 248 расширений для "
        "сохранения страниц, проверенных через API дополнений, 60 заявляют поддержку "
        "Android, и ни одно из них не проверялось на устройстве до нас."),
    l_android="Измерение на Android",
    p_quelle=(
        "Адрес в списке литературы — это обещание о странице, которая вам не "
        "подчиняется. Проверено на 150 источниках из реальных списков литературы: "
        "<strong>19,3 % исчезли</strong>, у 8,7 % нигде не нашлось архивной копии, а "
        "там, где снимок был, его возраст составил в медиане 603 дня. Для страницы без "
        "даты публикации время обращения — единственная дата, которую может нести "
        "ссылка, и она существует только в тот момент, когда вы смотрите."),
    l_quelle="Что происходит с источником после того, как вы его процитировали",
    p_ris=(
        "Съёмка может записать это внутрь: авторов, заглавие, DOI, лицензию и точное "
        "время — в самом PDF и в записи RIS рядом, в формате, который читают Zotero, "
        "Citavi, EndNote и Mendeley."),
    p_liste=(
        "Если речь о списке литературы, а не об одной странице, большая часть работы "
        "обходится без браузера. Из 20 разнородных источников <strong>10 стали полными "
        "записями с RIS и BibTeX за 8,1 секунды</strong> по обычному HTTP — без учётной "
        "записи и без ключа. Остальные десять возвращаются с указанием причины, чтобы "
        "вы знали, какие адреса требуют вас."),
    l_rezepte="Рецепты",
    l_messung="измерение",
    li=["Оно не даёт доступа к содержимому, которого у вас нет.",
        "Снимок экрана — не квалифицированный электронный документ. Он фиксирует, как "
        "страница выглядела в определённый момент, а это не то же самое, что доказать "
        "это.",
        "Там, где издатель предлагает собственный экспорт <em>Цитировать → RIS</em>, "
        "именно этот файл имеет силу и лучше всего, что восстановлено из страницы."],
    fuss=("Числа измерены с 1 по 3 августа 2026 года, каждое связано со своим методом "
          "и исходными данными."),
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
    h1="如何把网页保存为 PDF —— 一整张，并带上出处",
    standfirst=(
        "简短的答案：用抓取扩展，而不是打印对话框。打印会分页——同一篇文章印出来是 "
        "<strong>26 页，其中 9 处分页把句子拦腰截断</strong>。抓取写出的是一张连续的"
        "长纸，还能把来源和时间盖在页面上。"),
    meta="2026年8月3日 · 本页每一个数字都链接到它出自的那次测量",
    btn_ff="Firefox（桌面与 Android）",
    install=(
        "免费，MIT 许可，全部在本机运行。Edge 会问一次是否允许来自其他商店的扩展；"
        "Opera 需要先装上它的 <em>Install Chrome Extensions</em>。然后：打开网页，按 "
        f"<code>{_KUERZEL}</code> 或点击图标。"),
    h2=["打印成 PDF 还是抓取？一个诚实的对比",
        "在登录墙或你有权访问的付费墙之后",
        "在手机上",
        "为什么文件应当带着自己的出处",
        "一次处理整份阅读清单",
        "它做不到的事"],
    tabelle=_tabelle(
        "浏览器打印", "整页抓取",
        ["同一篇文章的结果", "把句子截断的分页", "可选中、可检索的文字", "是否花钱"],
        "{n} 页", "{n} 张", "召回率 {n}", "召回率 {n}",
        "不花钱，系统自带", "不花钱"),
    p_druck=(
        "<strong>论文字，自从抓取带上了文本层，它就领先了——91.5 % 对 87.6 %，"
        "测量于 8月5日。</strong>如果你只需要一份能读、能搜的副本，"
        "也不在意分页，浏览器里现成的功能就够了——本页把这一点说出来，而不是装作没有。"
        "值得抓取的情形是：版面本身要紧、某个分页会正好切在表格中间，或者出处信息必须"
        "跟着文件一起走。"),
    l_druck="方法与原始数据",
    p_login=(
        "抓取扩展读取的是你自己的会话已经显示出来的内容。有订阅的期刊论文、课程页面、"
        "订单确认——你看到什么样，就保存成什么样。服务器端的转换服务做不到这一点，"
        "因为它没有你的会话：在 20 个混合来源上测量，服务器端阅读器被其中 5 个直接拒绝。"
        "保存一个你有权阅读的页面，是供自己使用的复制件；它不是通往你无权访问内容的路径。"),
    p_handy=(
        "只有 Firefox。<strong>Chrome for Android 根本不安装任何扩展</strong>，"
        "所以这个问题只在那里出现。对照附加组件 API 核查了 248 个保存网页的扩展，"
        "其中 60 个声明支持 Android，而在我们之前，没有一个真正在设备上试过。"),
    l_android="Android 测量",
    p_quelle=(
        "参考文献里的一个网址，是对一个你无法掌控的页面所作的承诺。以真实参考文献表中的 "
        "150 个来源核查：<strong>19.3 % 已经消失</strong>，8.7 % 在任何地方都没有存档"
        "副本；即便存在快照，其年龄中位数也有 603 天。对于不声明出版日期的页面来说，"
        "访问时间是参考文献唯一能承载的日期——而它只存在于你查看的那一刻。"),
    l_quelle="一个来源在被引用之后会怎样",
    p_ris=(
        "抓取可以把这些写进去：作者、标题、DOI、许可与准确时间，写在 PDF 内部，"
        "并在旁边附一份 RIS 记录——这种格式可以导入 Zotero、Citavi、EndNote 或 Mendeley。"),
    p_liste=(
        "如果面对的是一份参考文献表而不是单个页面，大部分工作根本不需要浏览器。"
        "20 个混合来源中，<strong>10 个在 8.1 秒内变成了带 RIS 与 BibTeX 的完整记录"
        "</strong>，走的是普通 HTTP——不要账号，不要密钥。另外十个会连同原因一起退回来，"
        "好让你知道哪些网址需要你亲自去处理。"),
    l_rezepte="配方",
    l_messung="那次测量",
    li=["它无法取得你没有权限的内容。",
        "屏幕抓取不是合格的电子文书。它记录的是一个页面在某一时刻的样子，"
        "这与证明它是另一回事。",
        "凡是出版方提供了自己的 <em>引用 → RIS</em> 导出，那份文件才是权威的，"
        "胜过任何从页面重建出来的东西。"],
    fuss="数据测量于 2026年8月1日至3日之间，每一项都链接到其方法与原始数据。",
    korrekturen="欢迎指正，更正将公开进行：",
    l_issue="提交 issue",
    offenlegung1=("披露：作者是本页所提到的扩展 Full Page PDF Snap 的开发者。"
                  "浏览器自带的打印成 PDF 已经"),
    l_offenlegung="与之做过对比测量",
    offenlegung2="，包括打印占优的情形。",
    disclaimer="免责声明",
)
