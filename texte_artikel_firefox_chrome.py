#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Der Beitrag zur Einrichtung in Firefox und Chrome — in neun Sprachen.

Getrennt vom Bauen der Seite, damit eine Nachbesserung an einer Uebersetzung
keine HTML-Vorlage anfasst und ein Umbau der Seite keine neun Texte. Englisch
ist die Ausgangsfassung; faellt eine Sprache aus, faellt die Seite auf sie
zurueck.

Warum dieser Beitrag neben /how-to/for-students/ besteht: Dort steht, WARUM
eine Webquelle in der Semesterarbeit scheitert und was dagegen gemessen wurde.
Hier steht, WIE die Erweiterung in beiden Browsern eingerichtet und im
wissenschaftlichen Arbeitsfluss angewendet wird — Installationswege, Aufnahme,
RIS-Import, die vier Einstellungen, die fuer Arbeiten zaehlen.

Jede Aussage ueber Verhalten stammt aus den veroeffentlichten Projektdokumenten
(README, Werkzeugseite, CHANGELOG); jede Zahl traegt ihr Erhebungsdatum im
selben Satz und liegt als Datensatz unter docs/data/. Keine neuen Messwerte.

Rendering ueber build-firefox-chrome-post.py.
"""

SLUG = "firefox-and-chrome"
URL = "https://provinglab.dev/how-to/firefox-and-chrome/"
DATUM = "2026-08-15"

# Reihenfolge bestimmt die Reihenfolge der Bloecke in der Seite.
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]

TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "title": "For researchers and students: the add-on in Firefox and Chrome — setup and the academic workflow",
    "description": (
        "How to install Full Page PDF Snap in Firefox (desktop and Android) and in Chrome, "
        "and how to run the academic capture workflow: full page or visible area, citation "
        "details on the sheet, the RIS record into Citavi, Zotero or EndNote, and the four "
        "settings that matter for papers."
    ),
    "h1": "For researchers and students: the add-on in Firefox and Chrome",
    "standfirst": (
        "The companion piece to <a href=\"/how-to/for-students/\">why a web source fails in a "
        "term paper</a> is this one: how to set the extension up in Firefox and Chrome and how "
        "to run the capture–cite–archive workflow in practice. Install routes first, then the "
        "workflow, then the settings that matter — and an honest list of what it does not do."
    ),
    "meta": "15 August 2026 · setup and workflow, no new measurements",
    "body": """
<h2>1. Install: Firefox — desktop and Android</h2>
<p>
  One click on <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  opens the install dialog. The file is served and signed by Mozilla, which is what
  keeps automatic updates working. No account is needed — not for Firefox, not for
  the store.
</p>
<p>
  On a phone it is the same route: Firefox for Android runs extensions, and the
  same listing installs there. Tap the extension icon and the capture starts
  immediately. There is no APK and there will not be one — this is a browser
  extension, and on a phone it lives inside Firefox.
</p>
<p>
  Prefer no store at all? The same signed file is on the project's
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">release page</a>.
  Firefox verifies Mozilla's signature, not the origin, so the dialog opens exactly
  as from the store. The trade-off: installed this way it will not update itself.
</p>

<h2>2. Install: Chrome, Edge and other Chromium browsers</h2>
<p>
  The extension has been in the
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  since 3 August 2026. One click, and it updates itself from there. It needs
  Chrome 116 or newer. Brave and Vivaldi install from the Chrome Web Store as they
  are; Edge asks once to allow extensions from other stores; Opera needs its
  <em>Install Chrome Extensions</em> add-on first. The same capture, the same PDF,
  the same RIS record as the Firefox build.
</p>
<p>
  Without the store: the unpacked package is on the
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">release page</a> —
  <code>chrome://extensions</code>, <em>Developer mode</em>, <em>Load unpacked</em>.
  Loaded that way it will not update itself either.
</p>
<p>
  On Android none of the Chromium browsers work —
  <a href="/measurements/android-capture-extensions/">Chrome for Android installs no
  extensions at all</a>. On a phone, Firefox is the only route.
</p>

<h2>3. The workflow: capture, cite, archive</h2>
<p>
  Open the source — including pages behind the login of your library or institute,
  because everything runs in your own browser and nothing is uploaded. Click the
  extension icon. Two buttons are offered: the <strong>full page</strong>, scrolled
  from top to bottom and stitched into one sheet, or the <strong>visible area
  only</strong>, same PDF and same details. For a source you will cite, take the
  full page — a bibliography entry that points at half a page is a gap you will
  meet again at the deadline.
</p>
<p>
  The finished sheet carries its own citation: authors, journal, DOI, licence and
  the time of retrieval, read from the page you already had open — no citation
  service is queried. Since version 2.33.x (10 August 2026) these details are
  written into the PDF's XMP metadata as well — 18 fields on a full journal
  article, among them the DOI in <code>dc:identifier</code> and
  <code>prism:doi</code> — so they survive even if the separate record is lost.
</p>
<p>
  Into the literature manager goes the <strong>RIS record</strong>. There are two
  routes, and the difference matters: every PDF that carries citation details has
  the record embedded as an attachment named <code>quelle.ris</code> — always, that
  part cannot be switched off. The separate <code>.ris</code> download next to the
  PDF is the convenient path, on by default, and can be switched off in the
  settings; switching it off loses the convenience, not a single field. Citavi,
  Zotero and EndNote all import RIS. If you ever have the PDF without the download,
  <code>pdfdetach -saveall</code> or the attachment view of your PDF reader brings
  the record back out — verified on a real capture, 10 August 2026.
</p>

<h2>4. The four settings that matter for papers</h2>
<ul>
  <li><strong>One sheet or pages.</strong> The default is a single continuous PDF
      with no seams — the right form for OCR and for language models, which read
      text, not pixels, and complete a severed sentence rather than flag it.
      Multi-page output is optional, with page breaks that fall between lines
      instead of through them, and an A4 setting that fits printed paper.</li>
  <li><strong>Resolution.</strong> Scaling runs from 1.0x to 2.0x. Where a document
      has no text layer, recognition has to recover the words — in the measurement
      of 1 August 2026, 92.6&nbsp;% of the vocabulary survived at 150&nbsp;dpi —
      and resolution is the lever.
      <a href="/measurements/webpage-to-pdf-for-ocr/">The OCR measurement</a>.</li>
  <li><strong>Consent banners.</strong> Hidden before the capture, restored
      afterwards, with a switch in the popup. This is not about tidiness: consent
      dialogs often lock scrolling, and on one news site the page reported 900
      pixels of height instead of 43,101 — the capture would have quietly
      collapsed to a single screen. Nothing is clicked away on your behalf; a
      click on "accept" is a decision in your name and sets cookies.</li>
  <li><strong>Filename templates.</strong> Site, date, time, counter and page title
      — set once, and the archive sorts itself by the date you retrieved the
      source, which is the date your citation style asks for.</li>
</ul>

<h2>5. Why it works behind a university login</h2>
<p>
  The extension requests <code>activeTab</code> and no host permissions — it reads
  exactly the tab you start it on, while you start it. There is no server of the
  author's, no analytics, no telemetry; the PDF is built in the browser process on
  your device. That is why it captures what a web archiver cannot reach: the page
  as your session shows it, behind the library VPN you are signed into. Capture
  only what you have legitimate access to — that limit is yours to keep.
  <a href="/measurements/pdf-extension-permissions/">What eight capture extensions
  declare</a>, measured on their manifests.
</p>

<h2>What it does not do</h2>
<ul>
  <li>Installed without a store, it does not update itself — you come back to the
      release page for the next version. Everything else is identical.</li>
  <li>A thin page cannot be made to declare what it never declared: of 20 sources
      collected for a term paper (4 August 2026), 6 came back without a record.
      The details and the raw data are in the
      <a href="/how-to/for-students/">companion piece</a>.</li>
  <li>Same-page captures can differ: one page captured twice within a minute first
      returned no citation details, then all of them — its metadata had not been
      set yet when the first run read them. If the citation block is missing,
      capture again.</li>
  <li>On Android there is no Chromium route; on a phone the extension runs inside
      Firefox for Android only.</li>
  <li>A capture is documentation, not a legally certified record.</li>
</ul>

<p class="note">
  Disclosure: this guide describes our own extension; behaviour details come from
  the published project documents, and every figure links the measurement it comes
  from. Store states change — the install routes above reflect 15 August 2026.
  Corrections via <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">an
  issue</a> are taken up.
</p>
""",
}

# ---------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "title": "Für Wissenschaftler:innen und Studierende: die Erweiterung in Firefox und Chrome — Einrichtung und Arbeitsfluss",
    "description": (
        "Wie Sie Full Page PDF Snap in Firefox (Desktop und Android) und in Chrome installieren "
        "und den wissenschaftlichen Arbeitsfluss fahren: ganze Seite oder sichtbarer Bereich, "
        "Zitationsdaten auf dem Blatt, der RIS-Datensatz nach Citavi, Zotero oder EndNote — "
        "und die vier Einstellungen, die für Arbeiten zählen."
    ),
    "h1": "Für Wissenschaftler:innen und Studierende: die Erweiterung in Firefox und Chrome",
    "standfirst": (
        "Das Gegenstück zu <a href=\"/how-to/for-students/\">warum eine Webquelle in der "
        "Seminararbeit scheitert</a> ist dieser Beitrag: wie die Erweiterung in Firefox und "
        "Chrome eingerichtet wird und wie der Ablauf aufnehmen–zitieren–archivieren in der "
        "Praxis läuft. Zuerst die Installationswege, dann der Arbeitsfluss, dann die "
        "Einstellungen, die zählen — und eine ehrliche Liste dessen, was sie nicht tut."
    ),
    "meta": "15. August 2026 · Einrichtung und Arbeitsfluss, keine neuen Messungen",
    "body": """
<h2>1. Installation: Firefox — Desktop und Android</h2>
<p>
  Ein Klick auf <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  öffnet den Installationsdialog. Die Datei liegt bei Mozilla und ist von dort
  signiert — dadurch funktionieren die automatischen Updates weiter. Ein Konto
  braucht es nicht, weder bei Firefox noch im Store.
</p>
<p>
  Auf dem Telefon ist es derselbe Weg: Firefox für Android führt Erweiterungen
  aus, und dasselbe Verzeichnis installiert dort. Erweiterungssymbol antippen, und
  die Aufnahme startet sofort. Ein APK gibt es nicht und wird es nicht geben —
  dies ist eine Browser-Erweiterung, und auf dem Telefon lebt sie in Firefox.
</p>
<p>
  Lieber ganz ohne Store? Dieselbe signierte Datei liegt auf der
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">Release-Seite</a>
  des Projekts. Firefox prüft Mozillas Signatur, nicht die Herkunft — der Dialog
  öffnet sich genau wie aus dem Store. Der Preis dafür: So installiert aktualisiert
  sie sich nicht selbst.
</p>

<h2>2. Installation: Chrome, Edge und andere Chromium-Browser</h2>
<p>
  Im <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  ist die Erweiterung seit dem 3. August 2026. Ein Klick, und sie hält sich von
  dort selbst aktuell. Sie braucht Chrome 116 oder neuer. Brave und Vivaldi
  installieren ohne Umweg aus dem Chrome Web Store; Edge fragt einmal, ob
  <em>Erweiterungen aus anderen Stores</em> zugelassen werden; Opera braucht
  zuerst seine Erweiterung <em>Install Chrome Extensions</em>. Dieselbe Aufnahme,
  dasselbe PDF, derselbe RIS-Satz wie in der Firefox-Fassung.
</p>
<p>
  Ohne Store: Das entpackte Paket liegt auf der
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">Release-Seite</a> —
  <code>chrome://extensions</code>, <em>Entwicklermodus</em>, <em>Entpackte
  Erweiterung laden</em>. So geladen aktualisiert sie sich ebenfalls nicht selbst.
</p>
<p>
  Auf Android funktioniert keiner der Chromium-Browser —
  <a href="/measurements/android-capture-extensions/">Chrome für Android installiert
  überhaupt keine Erweiterungen</a>. Auf dem Telefon führt nur Firefox zum Ziel.
</p>

<h2>3. Der Arbeitsfluss: aufnehmen, zitieren, archivieren</h2>
<p>
  Öffnen Sie die Quelle — auch Seiten hinter dem Login Ihrer Bibliothek oder Ihres
  Instituts, denn alles läuft in Ihrem eigenen Browser, und nichts wird
  hochgeladen. Klicken Sie das Erweiterungssymbol. Zwei Schaltflächen werden
  angeboten: die <strong>ganze Seite</strong>, von oben bis unten gescrollt und zu
  einem Blatt gefügt, oder <strong>nur der sichtbare Bereich</strong>, gleiches PDF
  und gleiche Angaben. Für eine Quelle, die Sie zitieren werden, nehmen Sie die
  ganze Seite — ein Literaturverweis auf eine halbe Seite ist eine Lücke, die Ihnen
  zur Abgabe wiederbegegnet.
</p>
<p>
  Das fertige Blatt trägt seine Zitation selbst: Verfasser:innen, Zeitschrift, DOI,
  Lizenz und den Abrufzeitpunkt, gelesen aus der Seite, die Sie bereits offen
  hatten — kein Zitationsdienst wird befragt. Seit Version 2.33.x (10. August 2026)
  stehen diese Angaben zusätzlich in den XMP-Metadaten des PDF — 18 Felder bei
  einem vollständigen Zeitschriftenartikel, darunter der DOI in
  <code>dc:identifier</code> und <code>prism:doi</code> — und überleben damit
  selbst den Verlust des separaten Datensatzes.
</p>
<p>
  Ins Literaturprogramm geht der <strong>RIS-Datensatz</strong>. Es gibt zwei Wege,
  und der Unterschied zählt: Jedes PDF mit Quellenangaben trägt den Datensatz als
  Anlage namens <code>quelle.ris</code> eingebettet — immer, dieser Teil lässt
  sich nicht abschalten. Der separate <code>.ris</code>-Download neben dem PDF ist
  der bequeme Weg, standardmäßig an, und lässt sich in den Einstellungen
  abschalten; Abschalten verliert die Bequemlichkeit, kein einziges Feld. Citavi,
  Zotero und EndNote importieren alle RIS. Haben Sie einmal das PDF ohne den
  Download, holt <code>pdfdetach -saveall</code> oder die Anlagen-Ansicht Ihres
  PDF-Betrachters den Datensatz wieder heraus — geprüft an einer echten Aufnahme
  am 10. August 2026.
</p>

<h2>4. Die vier Einstellungen, die für Arbeiten zählen</h2>
<ul>
  <li><strong>Ein Blatt oder Seiten.</strong> Voreinstellung ist ein fortlaufendes
      PDF ohne Nahtstellen — die richtige Form für OCR und für Sprachmodelle, die
      Text lesen, keine Pixel, und einen durchtrennten Satz eher vervollständigen
      als melden. Mehrseitig geht optional, mit Umbrüchen, die zwischen Zeilen
      fallen statt durch sie hindurch, und einer A4-Einstellung für bedrucktes
      Papier.</li>
  <li><strong>Auflösung.</strong> Die Skalierung läuft von 1,0x bis 2,0x. Wo ein
      Dokument keine Textebene hat, muss die Erkennung die Wörter zurückgewinnen —
      in der Messung vom 1. August 2026 überlebten 92,6&nbsp;% des Wortschatzes bei
      150&nbsp;dpi — und die Auflösung ist der Hebel.
      <a href="/measurements/webpage-to-pdf-for-ocr/">Die OCR-Messung</a>.</li>
  <li><strong>Consent-Banner.</strong> Vor der Aufnahme ausgeblendet, danach
      zurückgesetzt, mit einem Schalter im Popup. Das ist keine Kosmetik:
      Consent-Dialoge sperren oft das Scrollen, und auf einer Nachrichtenseite
      meldete die Seite 900 Pixel Höhe statt 43.101 — die Aufnahme wäre still auf
      einen Bildschirm eingefallen. Nichts wird in Ihrem Namen weggeklickt; ein
      Klick auf „Akzeptieren" ist eine Entscheidung in Ihrem Namen und setzt
      Cookies.</li>
  <li><strong>Dateinamen-Vorlagen.</strong> Seite, Datum, Uhrzeit, Zähler und
      Seitentitel — einmal gesetzt, sortiert sich das Archiv selbst nach dem Tag,
      an dem Sie die Quelle abgerufen haben. Genau dieses Datum fragt Ihr
      Zitierstil ab.</li>
</ul>

<h2>5. Warum es hinter einem Hochschul-Login funktioniert</h2>
<p>
  Die Erweiterung fragt <code>activeTab</code> an und keine Host-Berechtigungen —
  sie liest genau den Tab, auf dem Sie sie starten, und nur während Sie sie
  starten. Es gibt keinen Server des Anbieters, keine Analytik, keine Telemetrie;
  das PDF entsteht im Browser-Prozess auf Ihrem Gerät. Deshalb nimmt sie auf, was
  ein Web-Archivierer nicht erreicht: die Seite, wie Ihre Sitzung sie zeigt,
  hinter dem Bibliotheks-VPN, in das Sie angemeldet sind. Nehmen Sie nur auf, wozu
  Sie legitimen Zugang haben — diese Grenze liegt bei Ihnen.
  <a href="/measurements/pdf-extension-permissions/">Was acht Aufnahme-Erweiterungen
  deklarieren</a>, gemessen an ihren Manifesten.
</p>

<h2>Was sie nicht tut</h2>
<ul>
  <li>Ohne Store installiert, aktualisiert sie sich nicht selbst — für die nächste
      Version kommen Sie zur Release-Seite zurück. Alles andere ist identisch.</li>
  <li>Eine dünne Seite kann nicht erklären, was sie nie erklärt hat: Von 20 Quellen
      einer Seminararbeits-Leseliste (4. August 2026) kamen 6 ohne Datensatz
      zurück. Die Einzelheiten und die Rohdaten stehen im
      <a href="/how-to/for-students/">Schwesterbeitrag</a>.</li>
  <li>Zwei Aufnahmen derselben Seite können sich unterscheiden: eine Seite,
      zweimal innerhalb einer Minute aufgenommen, lieferte zuerst keine
      Quellenangaben, dann alle — ihre Metadaten waren beim ersten Lesen noch
      nicht gesetzt. Fehlt der Zitationsblock: noch einmal aufnehmen.</li>
  <li>Auf Android gibt es keinen Chromium-Weg; auf dem Telefon läuft die
      Erweiterung nur in Firefox für Android.</li>
  <li>Eine Aufnahme ist Dokumentation, kein juristisch beglaubigter Nachweis.</li>
</ul>

<p class="note">
  Offenlegung: Diese Anleitung beschreibt unsere eigene Erweiterung; die
  Verhaltensangaben stammen aus den veröffentlichten Projektdokumenten, und jede
  Zahl verweist auf die Messung, aus der sie stammt. Store-Stände ändern sich —
  die Installationswege oben bilden den 15. August 2026 ab. Korrekturen über
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">ein Issue</a>
  werden aufgegriffen.
</p>
""",
}

# --------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "title": "Para investigadores y estudiantes: la extensión en Firefox y Chrome — instalación y flujo de trabajo",
    "description": (
        "Cómo instalar Full Page PDF Snap en Firefox (escritorio y Android) y en Chrome, y cómo "
        "llevar el flujo de trabajo académico: página completa o zona visible, datos de cita en "
        "la hoja, el registro RIS hacia Citavi, Zotero o EndNote — y los cuatro ajustes que "
        "importan para los trabajos."
    ),
    "h1": "Para investigadores y estudiantes: la extensión en Firefox y Chrome",
    "standfirst": (
        "El complemento de <a href=\"/how-to/for-students/\">por qué una fuente web falla en un "
        "trabajo académico</a> es este artículo: cómo configurar la extensión en Firefox y Chrome "
        "y cómo funciona en la práctica el ciclo capturar–citar–archivar. Primero las vías de "
        "instalación, después el flujo de trabajo, luego los ajustes que importan — y una lista "
        "honesta de lo que no hace."
    ),
    "meta": "15 de agosto de 2026 · instalación y flujo de trabajo, sin nuevas mediciones",
    "body": """
<h2>1. Instalación: Firefox — escritorio y Android</h2>
<p>
  Un clic en <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  abre el diálogo de instalación. El archivo lo sirve y lo firma Mozilla, que es lo
  que mantiene las actualizaciones automáticas. No hace falta cuenta — ni en
  Firefox ni en la tienda.
</p>
<p>
  En el teléfono es la misma vía: Firefox para Android ejecuta extensiones, y el
  mismo listado se instala allí. Toca el icono de la extensión y la captura
  comienza de inmediato. No hay APK ni la habrá — esto es una extensión de
  navegador, y en el teléfono vive dentro de Firefox.
</p>
<p>
  ¿Prefieres prescindir de la tienda? El mismo archivo firmado está en la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">página de
  versiones</a> del proyecto. Firefox verifica la firma de Mozilla, no el origen,
  así que el diálogo se abre igual que desde la tienda. El precio: instalada así,
  no se actualiza sola.
</p>

<h2>2. Instalación: Chrome, Edge y otros navegadores Chromium</h2>
<p>
  La extensión está en la
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  desde el 3 de agosto de 2026. Un clic y se mantiene actualizada desde allí.
  Necesita Chrome 116 o superior. Brave y Vivaldi instalan directamente desde la
  Chrome Web Store; Edge pregunta una vez si se permiten extensiones de otras
  tiendas; Opera necesita primero su extensión <em>Install Chrome Extensions</em>.
  La misma captura, el mismo PDF, el mismo registro RIS que en la versión de
  Firefox.
</p>
<p>
  Sin la tienda: el paquete descomprimido está en la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">página de
  versiones</a> — <code>chrome://extensions</code>, <em>Modo de desarrollador</em>,
  <em>Cargar extensión sin empaquetar</em>. Cargada así tampoco se actualiza sola.
</p>
<p>
  En Android no funciona ningún navegador Chromium —
  <a href="/measurements/android-capture-extensions/">Chrome para Android no instala
  extensiones en absoluto</a>. En el teléfono, Firefox es la única vía.
</p>

<h2>3. El flujo de trabajo: capturar, citar, archivar</h2>
<p>
  Abre la fuente — también páginas tras el inicio de sesión de tu biblioteca o
  instituto, porque todo se ejecuta en tu propio navegador y nada se sube. Haz
  clic en el icono de la extensión. Se ofrecen dos botones: la <strong>página
  completa</strong>, recorrida de arriba abajo y unida en una sola hoja, o
  <strong>solo la zona visible</strong>, con el mismo PDF y los mismos datos. Para
  una fuente que vas a citar, toma la página completa — una referencia que apunta
  a media página es un hueco que reencontrarás en la fecha de entrega.
</p>
<p>
  La hoja terminada lleva su propia cita: autores, revista, DOI, licencia y el
  momento de la consulta, leídos de la página que ya tenías abierta — no se
  consulta ningún servicio de citas. Desde la versión 2.33.x (10 de agosto de
  2026) estos datos se escriben además en los metadatos XMP del PDF — 18 campos en
  un artículo de revista completo, entre ellos el DOI en <code>dc:identifier</code>
  y <code>prism:doi</code> — de modo que sobreviven incluso a la pérdida del
  registro separado.
</p>
<p>
  Al gestor de referencias llega el <strong>registro RIS</strong>. Hay dos vías, y
  la diferencia importa: todo PDF con datos de cita lleva el registro incrustado
  como adjunto llamado <code>quelle.ris</code> — siempre, esa parte no se puede
  desactivar. La descarga <code>.ris</code> separada junto al PDF es el camino
  cómodo, activada por defecto, y se puede desactivar en los ajustes; desactivarla
  pierde la comodidad, no un solo campo. Citavi, Zotero y EndNote importan RIS. Si
  alguna vez tienes el PDF sin la descarga, <code>pdfdetach -saveall</code> o la
  vista de adjuntos de tu lector de PDF recupera el registro — verificado en una
  captura real el 10 de agosto de 2026.
</p>

<h2>4. Los cuatro ajustes que importan para los trabajos</h2>
<ul>
  <li><strong>Una hoja o páginas.</strong> Por defecto es un PDF continuo sin
      costuras — la forma adecuada para OCR y para modelos de lenguaje, que leen
      texto, no píxeles, y completan una frase cortada en lugar de señalarla. La
      salida multipágina es opcional, con saltos que caen entre líneas en lugar de
      atravesarlas, y un ajuste A4 para papel impreso.</li>
  <li><strong>Resolución.</strong> La escala va de 1,0x a 2,0x. Donde un documento
      no tiene capa de texto, el reconocimiento tiene que recuperar las palabras —
      en la medición del 1 de agosto de 2026 sobrevivió el 92,6&nbsp;% del
      vocabulario a 150&nbsp;dpi — y la resolución es la palanca.
      <a href="/measurements/webpage-to-pdf-for-ocr/">La medición de OCR</a>.</li>
  <li><strong>Banners de consentimiento.</strong> Ocultos antes de la captura,
      restaurados después, con un interruptor en la ventana emergente. No es
      estética: los diálogos de consentimiento suelen bloquear el desplazamiento,
      y en un sitio de noticias la página informó 900 píxeles de altura en lugar
      de 43.101 — la captura se habría reducido en silencio a una sola pantalla.
      Nada se clica en tu nombre; un clic en «Aceptar» es una decisión en tu
      nombre y crea cookies.</li>
  <li><strong>Plantillas de nombre de archivo.</strong> Sitio, fecha, hora,
      contador y título de la página — configúralo una vez y el archivo se ordena
      solo por el día en que consultaste la fuente, que es la fecha que pide tu
      estilo de citación.</li>
</ul>

<h2>5. Por qué funciona tras un inicio de sesión universitario</h2>
<p>
  La extensión solicita <code>activeTab</code> y ningún permiso de host — lee
  exactamente la pestaña en la que la inicias, y solo mientras la inicias. No hay
  servidor del autor, ni analítica, ni telemetría; el PDF se construye en el
  proceso del navegador en tu dispositivo. Por eso captura lo que un archivador
  web no alcanza: la página tal como la muestra tu sesión, tras la VPN de la
  biblioteca en la que has iniciado sesión. Captura solo aquello a lo que tienes
  acceso legítimo — ese límite es tuyo.
  <a href="/measurements/pdf-extension-permissions/">Lo que declaran ocho
  extensiones de captura</a>, medido en sus manifiestos.
</p>

<h2>Lo que no hace</h2>
<ul>
  <li>Instalada sin tienda, no se actualiza sola — vuelves a la página de
      versiones para la siguiente. Todo lo demás es idéntico.</li>
  <li>Una página escueta no puede declarar lo que nunca declaró: de 20 fuentes
      reunidas para un trabajo académico (4 de agosto de 2026), 6 volvieron sin
      registro. Los detalles y los datos brutos están en el
      <a href="/how-to/for-students/">artículo hermano</a>.</li>
  <li>Dos capturas de la misma página pueden diferir: una página capturada dos
      veces en un minuto devolvió primero ningún dato de cita y luego todos — sus
      metadatos aún no estaban listos en la primera lectura. Si falta el bloque de
      cita: captura de nuevo.</li>
  <li>En Android no hay vía Chromium; en el teléfono la extensión solo funciona
      dentro de Firefox para Android.</li>
  <li>Una captura es documentación, no una constancia con certificación legal.</li>
</ul>

<p class="note">
  Divulgación: esta guía describe nuestra propia extensión; los detalles de
  comportamiento provienen de los documentos publicados del proyecto, y cada cifra
  enlaza con la medición de la que procede. Los estados de las tiendas cambian —
  las vías de instalación anteriores reflejan el 15 de agosto de 2026. Las
  correcciones mediante <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">un
  issue</a> son bienvenidas.
</p>
""",
}

# --------------------------------------------------------------- Français ----
TEXTE["fr"] = {
    "title": "Pour les chercheuses, chercheurs et étudiant·e·s : l'extension dans Firefox et Chrome — installation et flux de travail",
    "description": (
        "Comment installer Full Page PDF Snap dans Firefox (bureau et Android) et dans Chrome, "
        "et comment mener le flux de travail académique : page entière ou zone visible, données "
        "de citation sur la feuille, l'enregistrement RIS vers Citavi, Zotero ou EndNote — et "
        "les quatre réglages qui comptent pour les travaux."
    ),
    "h1": "Pour les chercheuses, chercheurs et étudiant·e·s : l'extension dans Firefox et Chrome",
    "standfirst": (
        "Le pendant de <a href=\"/how-to/for-students/\">pourquoi une source web échoue dans un "
        "mémoire</a>, c'est cet article : comment configurer l'extension dans Firefox et Chrome "
        "et comment se déroule en pratique le cycle capturer–citer–archiver. D'abord les voies "
        "d'installation, puis le flux de travail, ensuite les réglages qui comptent — et une "
        "liste honnête de ce qu'elle ne fait pas."
    ),
    "meta": "15 août 2026 · installation et flux de travail, sans nouvelles mesures",
    "body": """
<h2>1. Installation : Firefox — bureau et Android</h2>
<p>
  Un clic sur <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  ouvre la boîte de dialogue d'installation. Le fichier est servi et signé par
  Mozilla, ce qui maintient les mises à jour automatiques. Aucun compte n'est
  nécessaire — ni pour Firefox, ni pour la boutique.
</p>
<p>
  Sur téléphone, c'est la même voie : Firefox pour Android exécute les extensions,
  et la même fiche s'y installe. Touchez l'icône de l'extension et la capture
  démarre aussitôt. Il n'y a pas d'APK et il n'y en aura pas — c'est une extension
  de navigateur, et sur téléphone elle vit dans Firefox.
</p>
<p>
  Vous préférez vous passer de boutique ? Le même fichier signé se trouve sur la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">page des
  versions</a> du projet. Firefox vérifie la signature de Mozilla, pas
  l'origine — la boîte de dialogue s'ouvre exactement comme depuis la boutique.
  La contrepartie : installée ainsi, elle ne se met pas à jour toute seule.
</p>

<h2>2. Installation : Chrome, Edge et les autres navigateurs Chromium</h2>
<p>
  L'extension est dans le
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  depuis le 3 août 2026. Un clic, et elle se maintient à jour depuis là. Elle
  exige Chrome 116 ou plus récent. Brave et Vivaldi s'installent directement
  depuis le Chrome Web Store ; Edge demande une fois d'autoriser les extensions
  d'autres boutiques ; Opera a d'abord besoin de son extension <em>Install Chrome
  Extensions</em>. Même capture, même PDF, même enregistrement RIS que dans la
  version Firefox.
</p>
<p>
  Sans la boutique : le paquet décompressé est sur la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">page des
  versions</a> — <code>chrome://extensions</code>, <em>Mode développeur</em>,
  <em>Charger l'extension non empaquetée</em>. Chargée ainsi, elle ne se met pas
  non plus à jour toute seule.
</p>
<p>
  Sur Android, aucun navigateur Chromium ne fonctionne —
  <a href="/measurements/android-capture-extensions/">Chrome pour Android n'installe
  aucune extension</a>. Sur téléphone, Firefox est la seule voie.
</p>

<h2>3. Le flux de travail : capturer, citer, archiver</h2>
<p>
  Ouvrez la source — y compris les pages derrière l'identification de votre
  bibliothèque ou de votre institut, car tout s'exécute dans votre propre
  navigateur et rien n'est téléversé. Cliquez sur l'icône de l'extension. Deux
  boutons sont proposés : la <strong>page entière</strong>, parcourue de haut en
  bas et assemblée en une seule feuille, ou la <strong>zone visible
  uniquement</strong>, même PDF et mêmes données. Pour une source que vous allez
  citer, prenez la page entière — une référence qui pointe vers une demi-page est
  un trou que vous retrouverez à la date de remise.
</p>
<p>
  La feuille terminée porte sa propre citation : auteurs, revue, DOI, licence et
  moment de la consultation, lus depuis la page que vous aviez déjà ouverte —
  aucun service de citation n'est interrogé. Depuis la version 2.33.x (10 août
  2026), ces données sont également écrites dans les métadonnées XMP du PDF —
  18 champs pour un article de revue complet, dont le DOI dans
  <code>dc:identifier</code> et <code>prism:doi</code> — elles survivent donc même
  à la perte de l'enregistrement séparé.
</p>
<p>
  Vers le gestionnaire de bibliographie passe l'<strong>enregistrement
  RIS</strong>. Il y a deux voies, et la différence compte : tout PDF portant des
  données de citation contient l'enregistrement en pièce jointe sous le nom
  <code>quelle.ris</code> — toujours, cette partie ne se désactive pas. Le
  téléchargement <code>.ris</code> séparé à côté du PDF est la voie confortable,
  activée par défaut, et se désactive dans les réglages ; le désactiver fait
  perdre le confort, pas un seul champ. Citavi, Zotero et EndNote importent tous
  le RIS. Si un jour vous avez le PDF sans le téléchargement,
  <code>pdfdetach -saveall</code> ou la vue des pièces jointes de votre lecteur
  PDF ressort l'enregistrement — vérifié sur une capture réelle le 10 août 2026.
</p>

<h2>4. Les quatre réglages qui comptent pour les travaux</h2>
<ul>
  <li><strong>Une feuille ou des pages.</strong> Par défaut, un PDF continu sans
      coutures — la bonne forme pour l'OCR et pour les modèles de langage, qui
      lisent du texte, pas des pixels, et complètent une phrase coupée au lieu de
      la signaler. La sortie multipage est optionnelle, avec des sauts qui tombent
      entre les lignes au lieu de les traverser, et un réglage A4 pour le papier
      imprimé.</li>
  <li><strong>Résolution.</strong> L'échelle va de 1,0x à 2,0x. Là où un document
      n'a pas de couche texte, la reconnaissance doit retrouver les mots — dans la
      mesure du 1er août 2026, 92,6&nbsp;% du vocabulaire a survécu à
      150&nbsp;dpi — et la résolution est le levier.
      <a href="/measurements/webpage-to-pdf-for-ocr/">La mesure OCR</a>.</li>
  <li><strong>Bandeaux de consentement.</strong> Masqués avant la capture,
      restaurés après, avec un interrupteur dans la fenêtre popup. Ce n'est pas
      une question d'esthétique : les dialogues de consentement verrouillent
      souvent le défilement, et sur un site d'information la page a annoncé 900
      pixels de hauteur au lieu de 43&nbsp;101 — la capture se serait
      silencieusement réduite à un seul écran. Rien n'est cliqué en votre nom ; un
      clic sur « Accepter » est une décision en votre nom et dépose des
      cookies.</li>
  <li><strong>Modèles de nom de fichier.</strong> Site, date, heure, compteur et
      titre de la page — réglé une fois, l'archive se trie d'elle-même selon le
      jour où vous avez consulté la source, qui est la date que demande votre
      style de citation.</li>
</ul>

<h2>5. Pourquoi cela fonctionne derrière une identification universitaire</h2>
<p>
  L'extension demande <code>activeTab</code> et aucune permission d'hôte — elle
  lit exactement l'onglet sur lequel vous la lancez, et seulement pendant que vous
  la lancez. Il n'y a ni serveur de l'auteur, ni analytique, ni télémétrie ; le
  PDF est construit dans le processus du navigateur sur votre appareil. C'est
  pourquoi elle capture ce qu'un archiveur web ne peut atteindre : la page telle
  que votre session la montre, derrière le VPN de la bibliothèque où vous êtes
  identifié. Ne capturez que ce à quoi vous avez légitimement accès — cette limite
  vous appartient.
  <a href="/measurements/pdf-extension-permissions/">Ce que déclarent huit
  extensions de capture</a>, mesuré sur leurs manifestes.
</p>

<h2>Ce qu'elle ne fait pas</h2>
<ul>
  <li>Installée sans boutique, elle ne se met pas à jour toute seule — vous
      revenez sur la page des versions pour la suivante. Tout le reste est
      identique.</li>
  <li>Une page pauvre ne peut déclarer ce qu'elle n'a jamais déclaré : sur 20
      sources réunies pour un mémoire (4 août 2026), 6 sont revenues sans
      enregistrement. Les détails et les données brutes sont dans
      <a href="/how-to/for-students/">l'article jumeau</a>.</li>
  <li>Deux captures de la même page peuvent différer : une page capturée deux fois
      en une minute a d'abord rendu aucune donnée de citation, puis toutes — ses
      métadonnées n'étaient pas encore posées lors de la première lecture. Si le
      bloc de citation manque : capturez à nouveau.</li>
  <li>Sur Android, il n'y a pas de voie Chromium ; sur téléphone, l'extension ne
      fonctionne que dans Firefox pour Android.</li>
  <li>Une capture est une documentation, pas un constat doté d'une certification
      légale.</li>
</ul>

<p class="note">
  Transparence : ce guide décrit notre propre extension ; les détails de
  comportement proviennent des documents publiés du projet, et chaque chiffre
  renvoie à la mesure dont il est issu. Les états des boutiques changent — les
  voies d'installation ci-dessus reflètent le 15 août 2026. Les corrections via
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">un ticket</a>
  sont prises en compte.
</p>
""",
}

# --------------------------------------------------------------- Italiano ----
TEXTE["it"] = {
    "title": "Per ricercatori, ricercatrici e studenti: l'estensione in Firefox e Chrome — installazione e flusso di lavoro",
    "description": (
        "Come installare Full Page PDF Snap in Firefox (desktop e Android) e in Chrome, e come "
        "condurre il flusso di lavoro accademico: pagina intera o area visibile, dati di "
        "citazione sul foglio, il record RIS verso Citavi, Zotero o EndNote — e le quattro "
        "impostazioni che contano per gli elaborati."
    ),
    "h1": "Per ricercatori, ricercatrici e studenti: l'estensione in Firefox e Chrome",
    "standfirst": (
        "Il pendant di <a href=\"/how-to/for-students/\">perché una fonte web fallisce in un "
        "elaborato</a> è questo articolo: come configurare l'estensione in Firefox e Chrome e "
        "come funziona in pratica il ciclo catturare–citare–archiviare. Prima le vie di "
        "installazione, poi il flusso di lavoro, quindi le impostazioni che contano — e una "
        "lista onesta di ciò che non fa."
    ),
    "meta": "15 agosto 2026 · installazione e flusso di lavoro, senza nuove misurazioni",
    "body": """
<h2>1. Installazione: Firefox — desktop e Android</h2>
<p>
  Un clic su <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  apre la finestra di installazione. Il file è servito e firmato da Mozilla, ed è
  questo che mantiene gli aggiornamenti automatici. Non serve alcun account — né
  per Firefox né per lo store.
</p>
<p>
  Sul telefono la via è la stessa: Firefox per Android esegue le estensioni, e la
  stessa scheda si installa lì. Tocca l'icona dell'estensione e la cattura parte
  subito. Non esiste un APK e non esisterà — questa è un'estensione del browser, e
  sul telefono vive dentro Firefox.
</p>
<p>
  Preferisci fare a meno dello store? Lo stesso file firmato è sulla
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">pagina dei
  rilasci</a> del progetto. Firefox verifica la firma di Mozilla, non
  l'origine — la finestra si apre esattamente come dallo store. Il prezzo:
  installata così, non si aggiorna da sola.
</p>

<h2>2. Installazione: Chrome, Edge e gli altri browser Chromium</h2>
<p>
  L'estensione è nel
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  dal 3 agosto 2026. Un clic, e si mantiene aggiornata da lì. Richiede Chrome 116
  o più recente. Brave e Vivaldi installano direttamente dal Chrome Web Store;
  Edge chiede una volta di consentire le estensioni da altri store; Opera ha prima
  bisogno della sua estensione <em>Install Chrome Extensions</em>. Stessa cattura,
  stesso PDF, stesso record RIS della versione Firefox.
</p>
<p>
  Senza lo store: il pacchetto decompresso è sulla
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">pagina dei
  rilasci</a> — <code>chrome://extensions</code>, <em>Modalità sviluppatore</em>,
  <em>Carica estensione non pacchettizzata</em>. Caricata così, nemmeno lei si
  aggiorna da sola.
</p>
<p>
  Su Android non funziona nessun browser Chromium —
  <a href="/measurements/android-capture-extensions/">Chrome per Android non installa
  alcuna estensione</a>. Sul telefono, Firefox è l'unica via.
</p>

<h2>3. Il flusso di lavoro: catturare, citare, archiviare</h2>
<p>
  Apri la fonte — comprese le pagine dietro il login della tua biblioteca o del
  tuo istituto, perché tutto avviene nel tuo browser e nulla viene caricato.
  Clicca sull'icona dell'estensione. Vengono offerti due pulsanti: la
  <strong>pagina intera</strong>, scorsa dall'alto in basso e unita in un unico
  foglio, oppure <strong>solo l'area visibile</strong>, stesso PDF e stessi dati.
  Per una fonte che citerai, prendi la pagina intera — un riferimento che punta a
  mezza pagina è una lacuna che ritroverai alla consegna.
</p>
<p>
  Il foglio finito porta la propria citazione: autori, rivista, DOI, licenza e
  momento della consultazione, letti dalla pagina che avevi già aperta — nessun
  servizio di citazioni viene interrogato. Dalla versione 2.33.x (10 agosto 2026)
  questi dati vengono scritti anche nei metadati XMP del PDF — 18 campi in un
  articolo di rivista completo, tra cui il DOI in <code>dc:identifier</code> e
  <code>prism:doi</code> — così sopravvivono persino alla perdita del record
  separato.
</p>
<p>
  Al gestore bibliografico arriva il <strong>record RIS</strong>. Ci sono due vie,
  e la differenza conta: ogni PDF con dati di citazione porta il record incorporato
  come allegato di nome <code>quelle.ris</code> — sempre, questa parte non si può
  disattivare. Il download <code>.ris</code> separato accanto al PDF è la via
  comoda, attiva per impostazione predefinita, e si può disattivare nelle
  impostazioni; disattivarlo perde la comodità, non un solo campo. Citavi, Zotero
  ed EndNote importano tutti RIS. Se un giorno hai il PDF senza il download,
  <code>pdfdetach -saveall</code> o la vista allegati del tuo lettore PDF tira
  fuori di nuovo il record — verificato su una cattura reale il 10 agosto 2026.
</p>

<h2>4. Le quattro impostazioni che contano per gli elaborati</h2>
<ul>
  <li><strong>Un foglio o pagine.</strong> L'impostazione predefinita è un PDF
      continuo senza cuciture — la forma giusta per l'OCR e per i modelli
      linguistici, che leggono testo, non pixel, e completano una frase tagliata
      invece di segnalarla. L'output multipagina è opzionale, con interruzioni che
      cadono tra le righe invece di attraversarle, e un'impostazione A4 per la
      carta stampata.</li>
  <li><strong>Risoluzione.</strong> La scala va da 1,0x a 2,0x. Dove un documento
      non ha livello testo, il riconoscimento deve recuperare le parole — nella
      misurazione del 1° agosto 2026 è sopravvissuto il 92,6&nbsp;% del
      vocabolario a 150&nbsp;dpi — e la risoluzione è la leva.
      <a href="/measurements/webpage-to-pdf-for-ocr/">La misurazione OCR</a>.</li>
  <li><strong>Banner del consenso.</strong> Nascosti prima della cattura,
      ripristinati dopo, con un interruttore nel popup. Non è estetica: i dialoghi
      di consenso spesso bloccano lo scorrimento, e su un sito di notizie la
      pagina ha riportato 900 pixel di altezza invece di 43.101 — la cattura si
      sarebbe silenziosamente ridotta a una sola schermata. Nulla viene cliccato
      in tuo nome; un clic su «Accetta» è una decisione in tuo nome e imposta
      cookie.</li>
  <li><strong>Modelli di nome file.</strong> Sito, data, ora, contatore e titolo
      della pagina — impostalo una volta e l'archivio si ordina da solo per il
      giorno in cui hai consultato la fonte, che è la data richiesta dal tuo
      stile di citazione.</li>
</ul>

<h2>5. Perché funziona dietro un login universitario</h2>
<p>
  L'estensione richiede <code>activeTab</code> e nessun permesso host — legge
  esattamente la scheda su cui la avvii, e solo mentre la avvii. Non c'è un server
  dell'autore, né analitica, né telemetria; il PDF viene costruito nel processo
  del browser sul tuo dispositivo. Per questo cattura ciò che un archiviatore web
  non raggiunge: la pagina come la mostra la tua sessione, dietro la VPN della
  biblioteca in cui hai effettuato l'accesso. Cattura solo ciò a cui hai accesso
  legittimo — quel limite è tuo.
  <a href="/measurements/pdf-extension-permissions/">Cosa dichiarano otto
  estensioni di cattura</a>, misurato sui loro manifest.
</p>

<h2>Cosa non fa</h2>
<ul>
  <li>Installata senza store, non si aggiorna da sola — per la versione successiva
      torni alla pagina dei rilasci. Tutto il resto è identico.</li>
  <li>Una pagina povera non può dichiarare ciò che non ha mai dichiarato: di 20
      fonti raccolte per un elaborato (4 agosto 2026), 6 sono tornate senza
      record. I dettagli e i dati grezzi sono
      nell'<a href="/how-to/for-students/">articolo gemello</a>.</li>
  <li>Due catture della stessa pagina possono differire: una pagina catturata due
      volte in un minuto ha restituito prima nessun dato di citazione, poi tutti —
      i suoi metadati non erano ancora stati impostati alla prima lettura. Se il
      blocco di citazione manca: cattura di nuovo.</li>
  <li>Su Android non c'è una via Chromium; sul telefono l'estensione funziona solo
      dentro Firefox per Android.</li>
  <li>Una cattura è documentazione, non un atto con certificazione legale.</li>
</ul>

<p class="note">
  Trasparenza: questa guida descrive la nostra stessa estensione; i dettagli sul
  comportamento provengono dai documenti pubblicati del progetto, e ogni cifra
  rimanda alla misurazione da cui deriva. Gli stati degli store cambiano — le vie
  di installazione qui sopra riflettono il 15 agosto 2026. Le correzioni tramite
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">una issue</a>
  vengono accolte.
</p>
""",
}

# ---------------------------------------------------------------- 日本語 ----
TEXTE["ja"] = {
    "title": "研究者・学生の方へ: Firefox と Chrome での拡張機能 — セットアップと学術ワークフロー",
    "description": (
        "Full Page PDF Snap を Firefox(デスクトップと Android)と Chrome にインストールする方法と、"
        "学術的なワークフローの進め方: ページ全体か表示領域のみか、シート上の引用データ、Citavi・"
        "Zotero・EndNote への RIS レコード、そして論文で重要な4つの設定。"
    ),
    "h1": "研究者・学生の方へ: Firefox と Chrome での拡張機能",
    "standfirst": (
        "<a href=\"/how-to/for-students/\">レポートでウェブ資料がなぜ失敗するか</a>の姉妹編がこの記事です: "
        "Firefox と Chrome で拡張機能をセットアップする方法と、キャプチャ→引用→アーカイブの流れの実践。"
        "まずインストール経路、次にワークフロー、そして重要な設定 — 最後に、できないことの正直なリスト。"
    ),
    "meta": "2026年8月15日 · セットアップとワークフロー(新規測定なし)",
    "body": """
<h2>1. インストール: Firefox — デスクトップと Android</h2>
<p>
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  でワンクリックするとインストールダイアログが開きます。ファイルは Mozilla が提供・署名しており、
  それによって自動更新が機能し続けます。アカウントは不要です — Firefox にもストアにも。
</p>
<p>
  スマートフォンでも同じ経路です: Android 版 Firefox は拡張機能を実行でき、同じリストから
  インストールできます。拡張機能のアイコンをタップすれば、キャプチャがすぐ始まります。
  APK はなく、今後も作られません — これはブラウザ拡張機能であり、スマートフォンでは
  Firefox の中で動きます。
</p>
<p>
  ストアを使いたくない場合は? 同じ署名済みファイルがプロジェクトの
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">リリースページ</a>にあります。
  Firefox は配信元ではなく Mozilla の署名を検証するため、ダイアログはストアからの場合と
  まったく同じように開きます。その代償として、この方法でインストールすると自動更新されません。
</p>

<h2>2. インストール: Chrome、Edge、その他の Chromium 系ブラウザ</h2>
<p>
  この拡張機能は2026年8月3日から
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome ウェブストア</a>に
  あります。ワンクリックで、以後はストアから自動的に更新されます。Chrome 116 以降が必要です。
  Brave と Vivaldi は Chrome ウェブストアからそのままインストールできます。Edge は一度だけ
  「他のストアからの拡張機能を許可する」を求められます。Opera は最初に拡張機能
  <em>Install Chrome Extensions</em> が必要です。キャプチャも PDF も RIS レコードも
  Firefox 版と同一です。
</p>
<p>
  ストアを使わない場合: 展開済みパッケージが
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">リリースページ</a>にあります —
  <code>chrome://extensions</code> で<em>デベロッパーモード</em>を有効にし、
  <em>パッケージ化されていない拡張機能を読み込む</em>を選びます。この方法でも自動更新はされません。
</p>
<p>
  Android では Chromium 系ブラウザはどれも使えません —
  <a href="/measurements/android-capture-extensions/">Android 版 Chrome は拡張機能を一切
  インストールできません</a>。スマートフォンでは Firefox が唯一の経路です。
</p>

<h2>3. ワークフロー: キャプチャ、引用、アーカイブ</h2>
<p>
  資料を開きます — 図書館や所属機関のログインの後ろにあるページも含みます。すべてが自分の
  ブラウザ内で実行され、何もアップロードされないからです。拡張機能のアイコンをクリックすると、
  2つのボタンが表示されます: 上から下までスクロールして1枚のシートに継ぎ合わせる<strong>ページ
  全体</strong>、または同じ PDF・同じ詳細情報の<strong>表示領域のみ</strong>。引用する資料なら
  ページ全体を取りましょう — 半ページを指す参考文献は、提出期限にまた出くわす隙間です。
</p>
<p>
  完成したシートには引用情報が載っています: 著者、ジャーナル、DOI、ライセンス、取得時刻。
  これらは開いていたページから読み取られ、引用サービスには問い合わせません。
  バージョン 2.33.x(2026年8月10日)以降、これらの情報は PDF の XMP メタデータにも
  書き込まれます — 完全なジャーナル論文で18フィールド、DOI は <code>dc:identifier</code> と
  <code>prism:doi</code> の両方に — そのため、別ファイルのレコードを失っても情報は残ります。
</p>
<p>
  文献管理ソフトには <strong>RIS レコード</strong>が入ります。経路は2つあり、その違いが重要です:
  引用情報を持つ PDF はすべて、<code>quelle.ris</code> という名前の添付ファイルとしてレコードを
  埋め込んでいます — 常にです。この部分はオフにできません。PDF の隣にダウンロードされる
  別ファイルの <code>.ris</code> は便利な経路で、既定でオン、設定でオフにできます。
  オフにして失われるのは便利さだけで、フィールドは一つも失われません。Citavi、Zotero、
  EndNote はいずれも RIS をインポートできます。PDF だけが手元にある場合は、
  <code>pdfdetach -saveall</code> や PDF ビューアの添付ファイル表示でレコードを取り出せます —
  2026年8月10日に実際のキャプチャで検証済みです。
</p>

<h2>4. 論文で重要な4つの設定</h2>
<ul>
  <li><strong>1枚のシートか、複数ページか。</strong> 既定は継ぎ目のない連続 PDF です —
      OCR や言語モデルに適した形です。言語モデルはピクセルではなくテキストを読み、
      分断された文を指摘するより補完してしまいます。複数ページ出力は任意で、行をまたぐのでは
      なく行の間に落ちる改ページと、印刷用紙に合う A4 設定があります。</li>
  <li><strong>解像度。</strong> スケーリングは 1.0x から 2.0x まで。テキストレイヤーのない
      文書では、認識が語句を復元する必要があります — 2026年8月1日の測定では、150 dpi で
      語彙の 92.6% が残りました — 解像度がそのレバーです。
      <a href="/measurements/webpage-to-pdf-for-ocr/">OCR の測定</a>。</li>
  <li><strong>同意バナー。</strong> キャプチャ前に非表示にし、後で元に戻します。ポップアップに
      スイッチがあります。これは見た目の問題ではありません: 同意ダイアログはしばしばスクロールを
      ロックし、あるニュースサイトではページが 43,101 ピクセルあるべき高さを 900 ピクセルと
      報告しました — キャプチャは静かに1画面分に縮んでいたでしょう。あなたの名前で何かが
      クリックされることはありません。「同意する」のクリックはあなたの名前での決定であり、
      Cookie を設定します。</li>
  <li><strong>ファイル名テンプレート。</strong> サイト、日付、時刻、カウンター、ページタイトル —
      一度設定すれば、アーカイブは資料を取得した日付で自動的に整列します。その日付こそ、
      引用スタイルが求める日付です。</li>
</ul>

<h2>5. 大学のログインの後ろで機能する理由</h2>
<p>
  この拡張機能が要求するのは <code>activeTab</code> のみで、ホスト権限はありません —
  あなたが起動したタブを、起動している間だけ読みます。作者のサーバー、アナリティクス、
  テレメトリーはなく、PDF はあなたのデバイス上のブラウザプロセスで作られます。だからこそ、
  ウェブアーカイバーが届かないものをキャプチャできます: あなたがログインしている図書館 VPN の
  後ろで、あなたのセッションに表示される通りのページです。正当なアクセス権のあるものだけを
  キャプチャしてください — その境界はあなたのものです。
  <a href="/measurements/pdf-extension-permissions/">8つのキャプチャ拡張機能が宣言していること</a>、
  マニフェストで測定。
</p>

<h2>できないこと</h2>
<ul>
  <li>ストアを使わずにインストールした場合、自動更新されません — 次のバージョンはリリースページに
      戻って入手します。それ以外は同一です。</li>
  <li>薄いページは、宣言していないことを宣言させられません: レポート用に集めた20件の資料
      (2026年8月4日)のうち、6件はレコードなしで返されました。詳細と生データは
      <a href="/how-to/for-students/">姉妹編</a>にあります。</li>
  <li>同じページの2回のキャプチャは異なることがあります: 1分以内に2回キャプチャしたページは、
      最初は引用情報なし、次は全部を返しました — 最初の読み取り時にメタデータがまだ設定
      されていなかったのです。引用ブロックがなければ、もう一度キャプチャしてください。</li>
  <li>Android には Chromium の経路がありません。スマートフォンでは Android 版 Firefox の中で
      のみ動きます。</li>
  <li>キャプチャは記録であり、法的に認証された証憑ではありません。</li>
</ul>

<p class="note">
  開示: このガイドは私たち自身の拡張機能を説明しています。動作の詳細は公開されたプロジェクト
  文書に由来し、すべての数値はその出典である測定にリンクしています。ストアの状態は変わります —
  上記のインストール経路は2026年8月15日時点のものです。修正は
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">issue</a> で受け付けています。
</p>
""",
}

# ----------------------------------------------------------- Português (BR) ----
TEXTE["pt-BR"] = {
    "title": "Para pesquisadores e estudantes: a extensão no Firefox e no Chrome — instalação e fluxo de trabalho",
    "description": (
        "Como instalar o Full Page PDF Snap no Firefox (desktop e Android) e no Chrome, e como "
        "conduzir o fluxo de trabalho acadêmico: página inteira ou área visível, dados de citação "
        "na folha, o registro RIS para o Citavi, Zotero ou EndNote — e as quatro configurações "
        "que importam para os trabalhos."
    ),
    "h1": "Para pesquisadores e estudantes: a extensão no Firefox e no Chrome",
    "standfirst": (
        "O complemento de <a href=\"/how-to/for-students/\">por que uma fonte da web falha num "
        "trabalho acadêmico</a> é este artigo: como configurar a extensão no Firefox e no Chrome "
        "e como funciona na prática o ciclo capturar–citar–arquivar. Primeiro as vias de "
        "instalação, depois o fluxo de trabalho, em seguida as configurações que importam — e "
        "uma lista honesta do que ela não faz."
    ),
    "meta": "15 de agosto de 2026 · instalação e fluxo de trabalho, sem novas medições",
    "body": """
<h2>1. Instalação: Firefox — desktop e Android</h2>
<p>
  Um clique em <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  abre o diálogo de instalação. O arquivo é servido e assinado pela Mozilla, o que mantém as
  atualizações automáticas funcionando. Não é preciso conta — nem no Firefox, nem na loja.
</p>
<p>
  No celular o caminho é o mesmo: o Firefox para Android executa extensões, e a mesma página se
  instala lá. Toque no ícone da extensão e a captura começa na hora. Não há APK e não haverá —
  isto é uma extensão de navegador, e no celular ela vive dentro do Firefox.
</p>
<p>
  Prefere passar sem loja? O mesmo arquivo assinado está na
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">página de versões</a>
  do projeto. O Firefox verifica a assinatura da Mozilla, não a origem — o diálogo abre exatamente
  como na loja. O preço: instalada assim, ela não se atualiza sozinha.
</p>

<h2>2. Instalação: Chrome, Edge e outros navegadores Chromium</h2>
<p>
  A extensão está na
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  desde 3 de agosto de 2026. Um clique, e ela se mantém atualizada a partir daí. Exige Chrome 116
  ou mais recente. Brave e Vivaldi instalam direto da Chrome Web Store; o Edge pergunta uma vez se
  permite extensões de outras lojas; o Opera precisa antes da sua extensão <em>Install Chrome
  Extensions</em>. A mesma captura, o mesmo PDF, o mesmo registro RIS da versão Firefox.
</p>
<p>
  Sem a loja: o pacote descompactado está na
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">página de versões</a> —
  <code>chrome://extensions</code>, <em>Modo do desenvolvedor</em>, <em>Carregar extensão
  descompactada</em>. Carregada assim, ela também não se atualiza sozinha.
</p>
<p>
  No Android, nenhum navegador Chromium funciona —
  <a href="/measurements/android-capture-extensions/">o Chrome para Android não instala extensão
  alguma</a>. No celular, o Firefox é a única via.
</p>

<h2>3. O fluxo de trabalho: capturar, citar, arquivar</h2>
<p>
  Abra a fonte — inclusive páginas atrás do login da sua biblioteca ou instituto, porque tudo roda
  no seu próprio navegador e nada é enviado. Clique no ícone da extensão. Dois botões são
  oferecidos: a <strong>página inteira</strong>, percorrida de cima a baixo e unida numa folha só,
  ou <strong>só a área visível</strong>, mesmo PDF e mesmos dados. Para uma fonte que você vai
  citar, capture a página inteira — uma referência que aponta para meia página é uma lacuna que
  você reencontra no prazo de entrega.
</p>
<p>
  A folha pronta carrega a própria citação: autores, periódico, DOI, licença e o momento da
  consulta, lidos da página que você já tinha aberta — nenhum serviço de citação é consultado.
  Desde a versão 2.33.x (10 de agosto de 2026), esses dados também são gravados nos metadados XMP
  do PDF — 18 campos num artigo de periódico completo, entre eles o DOI em
  <code>dc:identifier</code> e <code>prism:doi</code> — e assim sobrevivem até à perda do registro
  separado.
</p>
<p>
  Para o gerenciador de referências vai o <strong>registro RIS</strong>. Há duas vias, e a
  diferença importa: todo PDF com dados de citação traz o registro embutido como anexo chamado
  <code>quelle.ris</code> — sempre, essa parte não pode ser desligada. O download
  <code>.ris</code> separado ao lado do PDF é o caminho cômodo, ligado por padrão, e pode ser
  desligado nas configurações; desligar perde a comodidade, não um único campo. Citavi, Zotero e
  EndNote importam RIS. Se um dia você tiver o PDF sem o download, <code>pdfdetach -saveall</code>
  ou a visualização de anexos do seu leitor de PDF recupera o registro — verificado numa captura
  real em 10 de agosto de 2026.
</p>

<h2>4. As quatro configurações que importam para os trabalhos</h2>
<ul>
  <li><strong>Uma folha ou páginas.</strong> O padrão é um PDF contínuo sem emendas — a forma certa
      para OCR e para modelos de linguagem, que leem texto, não pixels, e completam uma frase
      cortada em vez de sinalizá-la. A saída em várias páginas é opcional, com quebras que caem
      entre as linhas em vez de atravessá-las, e uma configuração A4 para papel impresso.</li>
  <li><strong>Resolução.</strong> A escala vai de 1,0x a 2,0x. Onde um documento não tem camada de
      texto, o reconhecimento precisa recuperar as palavras — na medição de 1º de agosto de 2026,
      92,6&nbsp;% do vocabulário sobreviveu a 150&nbsp;dpi — e a resolução é a alavanca.
      <a href="/measurements/webpage-to-pdf-for-ocr/">A medição de OCR</a>.</li>
  <li><strong>Banners de consentimento.</strong> Ocultados antes da captura, restaurados depois,
      com um interruptor no popup. Não é estética: diálogos de consentimento costumam travar a
      rolagem, e num site de notícias a página informou 900 pixels de altura em vez de 43.101 — a
      captura teria encolhido em silêncio para uma única tela. Nada é clicado em seu nome; um
      clique em «Aceitar» é uma decisão em seu nome e grava cookies.</li>
  <li><strong>Modelos de nome de arquivo.</strong> Site, data, hora, contador e título da página —
      configure uma vez e o arquivo se ordena sozinho pelo dia em que você consultou a fonte, que
      é a data que o seu estilo de citação pede.</li>
</ul>

<h2>5. Por que funciona atrás de um login universitário</h2>
<p>
  A extensão pede <code>activeTab</code> e nenhuma permissão de host — ela lê exatamente a aba em
  que você a inicia, e só enquanto você a inicia. Não há servidor do autor, nem analítica, nem
  telemetria; o PDF é construído no processo do navegador no seu dispositivo. Por isso ela captura
  o que um arquivador web não alcança: a página como a sua sessão a mostra, atrás da VPN da
  biblioteca em que você está logado. Capture apenas aquilo a que você tem acesso legítimo — esse
  limite é seu.
  <a href="/measurements/pdf-extension-permissions/">O que oito extensões de captura declaram</a>,
  medido em seus manifestos.
</p>

<h2>O que ela não faz</h2>
<ul>
  <li>Instalada sem loja, ela não se atualiza sozinha — você volta à página de versões para a
      próxima. Todo o resto é idêntico.</li>
  <li>Uma página pobre não pode declarar o que nunca declarou: de 20 fontes reunidas para um
      trabalho acadêmico (4 de agosto de 2026), 6 voltaram sem registro. Os detalhes e os dados
      brutos estão no <a href="/how-to/for-students/">artigo irmão</a>.</li>
  <li>Duas capturas da mesma página podem divergir: uma página capturada duas vezes em um minuto
      devolveu primeiro nenhum dado de citação, depois todos — seus metadados ainda não tinham
      sido definidos na primeira leitura. Se o bloco de citação faltar: capture de novo.</li>
  <li>No Android não há via Chromium; no celular a extensão só roda dentro do Firefox para
      Android.</li>
  <li>Uma captura é documentação, não um registro com certificação legal.</li>
</ul>

<p class="note">
  Transparência: este guia descreve a nossa própria extensão; os detalhes de comportamento vêm dos
  documentos publicados do projeto, e cada número aponta para a medição de onde saiu. Os estados
  das lojas mudam — as vias de instalação acima refletem 15 de agosto de 2026. Correções via
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">uma issue</a> são bem-vindas.
</p>
""",
}

# ---------------------------------------------------------------- Русский ----
TEXTE["ru"] = {
    "title": "Исследователям и студентам: расширение в Firefox и Chrome — установка и рабочий процесс",
    "description": (
        "Как установить Full Page PDF Snap в Firefox (компьютер и Android) и в Chrome и как "
        "выстроить академический рабочий процесс: вся страница или видимая область, данные для "
        "цитирования на листе, RIS-запись в Citavi, Zotero или EndNote — и четыре настройки, "
        "которые важны для научных работ."
    ),
    "h1": "Исследователям и студентам: расширение в Firefox и Chrome",
    "standfirst": (
        "Парой к статье <a href=\"/how-to/for-students/\">о том, почему веб-источник подводит в "
        "курсовой</a>, служит этот текст: как настроить расширение в Firefox и Chrome и как на "
        "практике выглядит цикл «захват–цитирование–архив». Сначала способы установки, затем "
        "рабочий процесс, потом важные настройки — и честный список того, чего расширение не "
        "делает."
    ),
    "meta": "15 августа 2026 г. · установка и рабочий процесс, без новых измерений",
    "body": """
<h2>1. Установка: Firefox — компьютер и Android</h2>
<p>
  Один щелчок на <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  открывает диалог установки. Файл раздаёт и подписывает Mozilla — благодаря этому продолжают
  работать автоматические обновления. Учётная запись не нужна — ни в Firefox, ни в магазине.
</p>
<p>
  На телефоне путь тот же: Firefox для Android выполняет расширения, и та же страница каталога
  устанавливается там. Коснитесь значка расширения — и захват начинается сразу. APK нет и не
  будет — это расширение браузера, и на телефоне оно живёт внутри Firefox.
</p>
<p>
  Хотите совсем без магазина? Тот же подписанный файл лежит на
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">странице релизов</a>
  проекта. Firefox проверяет подпись Mozilla, а не источник — диалог открывается точно так же,
  как из магазина. Цена вопроса: установленное так расширение само не обновляется.
</p>

<h2>2. Установка: Chrome, Edge и другие браузеры на Chromium</h2>
<p>
  Расширение находится в
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome Web Store</a>
  с 3 августа 2026 года. Один щелчок — и дальше оно обновляется оттуда само. Требуется Chrome 116
  или новее. Brave и Vivaldi устанавливаются из Chrome Web Store напрямую; Edge один раз спрашивает
  разрешения на расширения из других магазинов; Opera сначала требует своё расширение
  <em>Install Chrome Extensions</em>. Тот же захват, тот же PDF, та же RIS-запись, что и в версии
  для Firefox.
</p>
<p>
  Без магазина: распакованный пакет лежит на
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">странице релизов</a> —
  <code>chrome://extensions</code>, <em>Режим разработчика</em>, <em>Загрузить распакованное
  расширение</em>. Загруженное так оно тоже не обновляется само.
</p>
<p>
  На Android ни один из браузеров на Chromium не работает —
  <a href="/measurements/android-capture-extensions/">Chrome для Android вообще не устанавливает
  расширения</a>. На телефоне единственный путь — Firefox.
</p>

<h2>3. Рабочий процесс: захват, цитирование, архив</h2>
<p>
  Откройте источник — включая страницы за логином вашей библиотеки или института, ведь всё
  выполняется в вашем собственном браузере и ничего не отправляется. Щёлкните значок расширения.
  Предлагаются две кнопки: <strong>вся страница</strong>, прокрученная сверху донизу и сшитая в
  один лист, или <strong>только видимая область</strong> — тот же PDF и те же данные. Для источника,
  который вы будете цитировать, берите всю страницу — ссылка на полстраницы в библиографии это
  брешь, которая встретится вам снова к сроку сдачи.
</p>
<p>
  Готовый лист несёт свою цитату сам: авторы, журнал, DOI, лицензия и время обращения — прочитанные
  со страницы, которая уже была у вас открыта; никакой сервис цитирования не опрашивается. С версии
  2.33.x (10 августа 2026 г.) эти данные записываются ещё и в XMP-метаданные PDF — 18 полей для
  полной журнальной статьи, среди них DOI в <code>dc:identifier</code> и <code>prism:doi</code> —
  так что они переживают даже потерю отдельной записи.
</p>
<p>
  В библиографический менеджер попадает <strong>RIS-запись</strong>. Путей два, и разница важна:
  каждый PDF с данными для цитирования несёт запись встроенной — как вложение с именем
  <code>quelle.ris</code>, всегда, эту часть отключить нельзя. Отдельная загрузка
  <code>.ris</code> рядом с PDF — удобный путь, включён по умолчанию и отключается в настройках;
  отключение теряет удобство, но ни одного поля. Citavi, Zotero и EndNote импортируют RIS. Если
  однажды у вас есть PDF без загрузки, <code>pdfdetach -saveall</code> или панель вложений вашей
  читалки PDF извлечёт запись обратно — проверено на реальном захвате 10 августа 2026 г.
</p>

<h2>4. Четыре настройки, важные для научных работ</h2>
<ul>
  <li><strong>Один лист или страницы.</strong> По умолчанию — единый непрерывный PDF без швов:
      правильная форма для OCR и для языковых моделей, которые читают текст, а не пиксели, и
      разорванное предложение скорее допишут, чем отметят. Многостраничный вывод — опция, с
      разрывами, падающими между строк, а не сквозь них, и настройкой A4 под печатную бумагу.</li>
  <li><strong>Разрешение.</strong> Масштаб — от 1,0x до 2,0x. Там, где у документа нет текстового
      слоя, распознавание должно вернуть слова — в измерении от 1 августа 2026 г. при 150 dpi
      уцелело 92,6&nbsp;% словаря — и разрешение здесь рычаг.
      <a href="/measurements/webpage-to-pdf-for-ocr/">Измерение OCR</a>.</li>
  <li><strong>Баннеры согласия.</strong> Скрываются перед захватом и возвращаются после —
      переключатель во всплывающем окне. Это не косметика: диалоги согласия часто блокируют
      прокрутку, и на одном новостном сайте страница сообщила о высоте 900 пикселей вместо
      43&nbsp;101 — захват тихо схлопнулся бы до одного экрана. За вас ничего не «откликивается»:
      щелчок по «Принять» — решение от вашего имени, и он ставит куки.</li>
  <li><strong>Шаблоны имён файлов.</strong> Сайт, дата, время, счётчик и заголовок страницы —
      настройте один раз, и архив сам рассортируется по дню обращения к источнику. Именно эту дату
      спрашивает ваш стиль цитирования.</li>
</ul>

<h2>5. Почему это работает за университетским логином</h2>
<p>
  Расширение запрашивает <code>activeTab</code> и никаких host-разрешений — оно читает ровно ту
  вкладку, на которой вы его запускаете, и только пока вы его запускаете. Нет сервера автора, нет
  аналитики, нет телеметрии; PDF собирается в процессе браузера на вашем устройстве. Поэтому оно
  захватывает то, чего веб-архиватор не достанет: страницу такой, какой её показывает ваша сессия,
  за библиотечным VPN, в который вы вошли. Захватывайте только то, к чему у вас есть законный
  доступ — эта граница остаётся за вами.
  <a href="/measurements/pdf-extension-permissions/">Что декларируют восемь расширений для
  захвата</a> — измерено по их манифестам.
</p>

<h2>Чего оно не делает</h2>
<ul>
  <li>Установленное без магазина, оно само не обновляется — за следующей версией вы возвращаетесь
      на страницу релизов. Всё остальное идентично.</li>
  <li>Тонкая страница не может заявить то, чего никогда не заявляла: из 20 источников, собранных
      для курсовой (4 августа 2026 г.), 6 вернулись без записи. Подробности и сырые данные — в
      <a href="/how-to/for-students/">статье-паре</a>.</li>
  <li>Два захвата одной страницы могут различаться: страница, захваченная дважды за минуту, сначала
      вернула никаких данных для цитирования, затем все — её метаданные к моменту первого чтения
      ещё не были установлены. Нет блока цитирования — захватите снова.</li>
  <li>На Android пути через Chromium нет; на телефоне расширение работает только внутри Firefox для
      Android.</li>
  <li>Захват — это документация, а не юридически заверенная фиксация.</li>
</ul>

<p class="note">
  Раскрытие: это руководство описывает наше собственное расширение; детали поведения взяты из
  опубликованных документов проекта, и каждая цифра ссылается на измерение, из которого она
  происходит. Состояния магазинов меняются — способы установки выше отражают 15 августа 2026 г.
  Исправления через <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">issue</a>
  принимаются.
</p>
""",
}

# ---------------------------------------------------------------- 中文(简体) ----
TEXTE["zh-CN"] = {
    "title": "致研究人员和学生:Firefox 与 Chrome 中的扩展——安装与学术工作流",
    "description": (
        "如何在 Firefox(桌面端与 Android)和 Chrome 中安装 Full Page PDF Snap,以及如何运行学术"
        "工作流:整页还是可见区域、纸张上的引用数据、导入 Citavi、Zotero 或 EndNote 的 RIS 记录,"
        "以及对论文至关重要的四项设置。"
    ),
    "h1": "致研究人员和学生:Firefox 与 Chrome 中的扩展",
    "standfirst": (
        "与<a href=\"/how-to/for-students/\">《为什么网络来源会在课程论文中出问题》</a>相配套的,是本文:"
        "如何在 Firefox 和 Chrome 中配置该扩展,以及“捕获—引用—归档”流程的实际操作。先讲安装途径,"
        "再讲工作流,然后是关键设置——最后是一份诚实说明它不做什么的清单。"
    ),
    "meta": "2026年8月15日 · 安装与工作流,无新增测量",
    "body": """
<h2>1. 安装:Firefox —— 桌面端与 Android</h2>
<p>
  在 <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">addons.mozilla.org</a>
  上点击一下即可打开安装对话框。文件由 Mozilla 提供并签名,自动更新因此得以持续工作。无需任何
  账户——Firefox 不需要,商店也不需要。
</p>
<p>
  在手机上路径相同:Android 版 Firefox 支持扩展,同一个上架页面即可安装。点击扩展图标,捕获
  立即开始。没有 APK,也不会有——这是浏览器扩展,在手机上它运行于 Firefox 之中。
</p>
<p>
  不想用商店?同一份签名文件也在项目的
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">发布页面</a>上。Firefox
  验证的是 Mozilla 的签名而非来源,因此对话框与从商店安装时完全一样。代价是:以此方式安装后,
  它不会自动更新。
</p>

<h2>2. 安装:Chrome、Edge 及其他 Chromium 浏览器</h2>
<p>
  该扩展自 2026 年 8 月 3 日起上架
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome 应用商店</a>。
  一键安装,之后从商店自动更新。需要 Chrome 116 或更高版本。Brave 和 Vivaldi 可直接从 Chrome
  应用商店安装;Edge 会询问一次是否允许来自其他商店的扩展;Opera 需要先安装其
  <em>Install Chrome Extensions</em> 扩展。与 Firefox 版相同的捕获、相同的 PDF、相同的 RIS 记录。
</p>
<p>
  不用商店的方式:解压包在
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">发布页面</a>上——
  打开 <code>chrome://extensions</code>,启用<em>开发者模式</em>,选择<em>加载已解压的扩展程序</em>。
  以此方式加载后,它同样不会自动更新。
</p>
<p>
  在 Android 上,任何 Chromium 浏览器都行不通——
  <a href="/measurements/android-capture-extensions/">Android 版 Chrome 根本无法安装扩展</a>。
  在手机上,Firefox 是唯一途径。
</p>

<h2>3. 工作流:捕获、引用、归档</h2>
<p>
  打开来源页面——包括位于您的图书馆或机构登录之后的页面,因为一切都在您自己的浏览器中运行,
  不会有任何上传。点击扩展图标,会出现两个按钮:<strong>整页</strong>——从头滚到底并拼合为一张
  长页,或<strong>仅可见区域</strong>——同样的 PDF 和同样的信息。对于要引用的来源,请捕获整页:
  指向半页内容的参考文献条目,是您会在截止日再次遇到的缺口。
</p>
<p>
  完成的长页自带引用信息:作者、期刊、DOI、许可和获取时间,均读取自您已经打开的页面——不查询
  任何引文服务。自 2.33.x 版本(2026 年 8 月 10 日)起,这些信息还会写入 PDF 的 XMP 元数据——
  一篇完整的期刊文章有 18 个字段,其中 DOI 同时写入 <code>dc:identifier</code> 和
  <code>prism:doi</code>——因此即使单独的记录文件丢失,这些信息仍然存在。
</p>
<p>
  进入文献管理器的是 <strong>RIS 记录</strong>。有两条路径,区别很重要:每个带有引用信息的 PDF
  都内嵌了名为 <code>quelle.ris</code> 的附件——始终如此,这一部分无法关闭。PDF 旁的单独
  <code>.ris</code> 下载是便捷路径,默认开启,可在设置中关闭;关闭失去的只是便捷,不会丢失任何
  字段。Citavi、Zotero 和 EndNote 都支持导入 RIS。如果您手上只有 PDF 而没有下载文件,
  <code>pdfdetach -saveall</code> 或 PDF 阅读器的附件视图可以重新取出该记录——已于 2026 年
  8 月 10 日在真实捕获中验证。
</p>

<h2>4. 对论文至关重要的四项设置</h2>
<ul>
  <li><strong>一张长页还是分页。</strong>默认是无接缝的连续 PDF——这是适合 OCR 和语言模型的形式:
      语言模型读的是文字而非像素,遇到被截断的句子会自行补全而不是标记出来。多页输出为可选,
      分页符落在行与行之间而非穿过文字,另有适配打印纸张的 A4 设置。</li>
  <li><strong>分辨率。</strong>缩放范围为 1.0x 至 2.0x。当文档没有文本层时,识别必须还原文字——
      在 2026 年 8 月 1 日的测量中,150 dpi 下 92.6% 的词汇得以保留——分辨率就是杠杆。
      <a href="/measurements/webpage-to-pdf-for-ocr/">OCR 测量</a>。</li>
  <li><strong>同意横幅。</strong>捕获前隐藏,之后还原,弹窗中有一个开关。这不是为了美观:同意
      对话框常会锁定滚动,在某新闻网站上,页面报告的高度是 900 像素而非 43,101 像素——捕获会
      悄无声息地塌缩成一个屏幕。不会以您的名义点击任何东西;点击"接受"是以您的名义做出的决定,
      并会设置 Cookie。</li>
  <li><strong>文件名模板。</strong>站点、日期、时间、计数器和页面标题——设置一次,档案就会按您
      获取来源的日期自动排序,而这正是您的引用格式所要求的日期。</li>
</ul>

<h2>5. 为什么它能在大学登录之后正常工作</h2>
<p>
  该扩展只请求 <code>activeTab</code>,不请求任何主机权限——它只读取您启动它时所在的那个标签页,
  且仅在启动期间读取。没有开发者的服务器,没有分析,没有遥测;PDF 在您设备上的浏览器进程中
  生成。正因如此,它能捕获网络存档工具无法触及的内容:您登录的图书馆 VPN 之后、以您的会话
  呈现的页面。请只捕获您有合法访问权限的内容——这条界限由您自己把握。
  <a href="/measurements/pdf-extension-permissions/">八款捕获扩展声明了什么</a>,基于其清单文件测量。
</p>

<h2>它不做什么</h2>
<ul>
  <li>不通过商店安装时,它不会自动更新——下一个版本需要您回到发布页面获取。其余完全相同。</li>
  <li>内容单薄的页面无法声明它从未声明过的信息:为课程论文收集的 20 个来源(2026 年 8 月 4 日)
      中,有 6 个未能返回记录。详情和原始数据见
      <a href="/how-to/for-students/">姊妹篇</a>。</li>
  <li>同一页面的两次捕获可能不同:一个页面在一分钟内捕获两次,第一次没有返回任何引用信息,
      第二次全部返回——第一次读取时其元数据尚未设置。如果缺少引用块:请再捕获一次。</li>
  <li>在 Android 上没有 Chromium 途径;在手机上,该扩展只能运行于 Android 版 Firefox 之中。</li>
  <li>捕获是文档记录,不是经法律认证的存证。</li>
</ul>

<p class="note">
  披露:本指南描述的是我们自己的扩展;行为细节来自已公开的项目文档,每个数字都链接到其出处
  的测量。商店状态会变化——上述安装途径反映的是 2026 年 8 月 15 日的情况。欢迎通过
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">issue</a> 提出更正。
</p>
""",
}
