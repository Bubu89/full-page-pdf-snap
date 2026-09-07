#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Der Artikeltext in neun Sprachen — getrennt vom Bauen der Seite.

Muster: texte_artikel_studierende.py. ENGLISCH ist die Ausgangsversion; faellt
eine Sprache aus, faellt die Seite auf sie zurueck.

Dieser Beitrag ist eine Anleitung, keine Messung: Er beschreibt die
Installationswege (Firefox inkl. Android, Chrome Web Store) und den
wissenschaftlichen Arbeitsablauf mit der Erweiterung. Zahlen kommen nur aus
zwei Quellen — den oeffentlichen Store-Seiten (mit Abrufdatum im selben Satz)
und bereits unter docs/data/ belegten Messungen (mit Datum und Rohdaten-Link).
Die Store-Staende wurden am 15. August 2026 live geprueft (AMO-API,
CWS-Seite, GitHub-Release-API): beide Stores 2.33.4, Release v2.27.0.

Rendering ueber build-forscher-post.py.
"""

SLUG = "researchers-firefox-chrome"
URL = "https://provinglab.dev/how-to/researchers-firefox-chrome/"
DATUM = "2026-08-15"

# Reihenfolge bestimmt die Reihenfolge der Bloecke in der Seite.
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]

TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "title": "Full Page PDF Snap in Firefox and Chrome: installation, and the academic workflow",
    "description": (
        "The install routes for Firefox (desktop and Android) and Chrome, then the research "
        "workflow: full page or visible area, citation data with a RIS record for Citavi, "
        "Zotero and EndNote, resolution scaling, A4 and the consent switch — and what "
        "version 2.33.4 changed. Store versions checked 15 August 2026."
    ),
    "h1": "Full Page PDF Snap in Firefox and Chrome: installation, and the academic workflow",
    "standfirst": (
        "This is the practical guide for researchers and students: how the extension gets "
        "into Firefox — including Firefox for Android — and into Chrome, and how a capture "
        "then carries a source through the academic workflow, from the choice between full "
        "page and visible area to the RIS record your reference manager imports. Store "
        "versions were checked on 15 August 2026 and are stated with that date."
    ),
    "meta": "15 August 2026 · store versions checked on the day",
    "body": """
<h2>1. Firefox: desktop and Android from one listing</h2>
<p>
  On the desktop the route is the
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">Firefox
  Add-ons listing</a>: one click, the file is signed by Mozilla, and the extension updates
  itself from there. When this was written the listing carried version 2.33.4 (checked
  15 August 2026); it needs Firefox 109 or newer.
</p>
<p>
  On a phone the same listing serves <strong>Firefox for Android</strong> (version 127 or
  newer): install it from the browser's own add-ons menu, then open the menu on a page and
  tap the extension — the capture starts immediately, without the popup the desktop shows.
  A single notification reports the finished PDF; tapping it opens the file, and the
  system's own share menu takes it from there.
</p>
<p>
  Firefox is also the only route on a phone, because Chrome for Android installs no
  extensions at all. And if you prefer no store at all, the
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">release page</a>
  serves the same signed file — with two honest caveats: the newest package there was
  2.27.0 when checked (15 August 2026), behind both stores, and an extension installed
  this way does not update itself. Which store currently carries which version is
  published machine-readable at
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>.
</p>

<h2>2. Chrome, Edge, Brave, Vivaldi</h2>
<p>
  For Chrome the route is the
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome
  Web Store listing</a> — likewise at version 2.33.4 when checked (15 August 2026), needing
  Chrome 116 or newer, and updating itself from the store. Brave and Vivaldi install from
  the Chrome Web Store as they are; Edge asks once to allow extensions from other stores;
  Opera needs its <em>Install Chrome Extensions</em> add-on first.
</p>
<p>
  Both builds come from one source, so the capture, the PDF and the RIS record are the
  same; what differs is the platform around them. On the desktop the fastest way to a
  capture is the keyboard: <code>Alt+Shift+Y</code>. A right-click on the toolbar icon
  carries the quick switches for scaling, download folder and banner handling.
</p>

<h2>3. The whole page, or only what you see</h2>
<p>
  The popup offers two captures. <strong>Full page</strong> scrolls the document from top
  to bottom and stitches every viewport into one seamless sheet — the right choice for
  anything you will cite. <strong>Visible area only</strong>, the second button, writes
  exactly what is on screen, as the same kind of PDF with the same citation details — the
  right choice when one post out of a long thread matters, or when a page keeps growing
  as you scroll and has no bottom to capture.
</p>
<p>
  Why this is worth doing at all — a source that disappears, a citation typed out by
  hand, a file no machine can read — is the subject of the
  <a href="/how-to/for-students/">companion article for students</a>, with a measurement
  behind each point. The honest comparison against the browser's own print export, which
  wins on selectable text, stands in the
  <a href="/how-to/save-a-webpage-as-pdf/">general guide</a>. Both are linked here instead
  of repeated.
</p>

<h2>4. Citation data: on the sheet, in the file, into the reference manager</h2>
<p>
  A capture reads the bibliographic metadata the page itself declares and puts it in three
  places. On the sheet: authors, journal, DOI, licence and the time of retrieval. In the
  file: the document properties, an XMP stream with Dublin Core and PRISM fields — the
  vocabularies reference managers read — and twelve further fields in the document
  information dictionary. And as a record: a <code>quelle.ris</code> attachment inside the
  PDF, plus a separate <code>.ris</code> file next to it that Citavi, Zotero and EndNote
  import directly. The separate file is a convenience and can be switched off in the
  settings; the embedded record always travels with the PDF.
</p>
<p>
  Since 7 August 2026 the file name carries the source too: the default template is
  <code>{title}_{site}_{date}_{time}</code>, with the title taken from the publisher's
  metadata rather than the window title — a folder of captures then reads like a
  bibliography instead of a list of addresses.
</p>
<p>
  The honest limit: the extension reads what the open page declares and queries no citation
  service. A thin page cannot be made to declare what it never declared — of 20 sources
  from a real reading list (measured 4 August 2026), 6 came back without a record.
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">Raw data</a>.
  How the reader compares against Citoid, the Wikimedia citation service, is measured at
  <a href="/measurements/citation-extraction/">citation extraction</a>.
</p>

<h2>5. Settings that matter in research work</h2>
<ul>
  <li><strong>Resolution scaling</strong> from 1.0x to 2.0x (default 1.5x on the desktop,
      1.0x on Android). In practice: turn it up for small print and figures, down when file
      size matters. If the PDF is meant for OCR or a language model, the threshold below
      which recognition collapses is measured, not guessed:
      <a href="/measurements/webpage-to-pdf-for-ocr/">webpage to PDF for OCR</a>.</li>
  <li><strong>Single sheet or A4.</strong> The default is one continuous page, with no
      seams for a machine to fall into. Where printed paper is the target, the A4 setting
      paginates with breaks that fall between lines instead of through them.</li>
  <li><strong>The consent switch.</strong> Consent banners often lock scrolling; the switch
      in the popup hides them for the duration of the capture and restores them afterwards.
      Nothing is clicked away in your name — hiding is not deciding.</li>
  <li><strong>The time anchor.</strong> Since 5 August 2026 a capture can stamp itself with
      a "not before" time taken from the public drand beacon — off by default, because it
      is the extension's only network request. It anchors that the capture is no older than
      the beacon's round; it says nothing about what the page showed, and it is not a
      qualified timestamp in the legal sense.</li>
</ul>

<h2>6. What the current version changed</h2>
<p>
  Version 2.33.4, in both stores when this was written (15 August 2026), moved the academic
  workflow to the front. From the
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">changelog</a>:
</p>
<ul>
  <li>Citation metadata now lives in the PDF itself — XMP with Dublin Core and PRISM,
      twelve document information fields — not only in the RIS record (7 August 2026).
      Licence, work type, version and modification date followed on 10 August, as did RIS
      output in the Chrome build.</li>
  <li>The RIS record is always embedded in the PDF as <code>quelle.ris</code>; the separate
      file beside it can be switched off (10 August 2026).</li>
  <li>Records without an author now begin with the title, as citation styles require,
      instead of a bare "(n. d.)."; a journal name duplicated as publisher is no longer
      written twice (10 August 2026).</li>
  <li>On Android the capture downloads directly in the tab you are on — one notification,
      no extra tab. The companion files (RIS record, link map, publisher's file) are
      desktop-only now; on the phone their content lives inside the PDF (7 August 2026).</li>
  <li>File names carry the page title from the publisher's metadata (7 August 2026).</li>
</ul>

<h2>What it does not do</h2>
<ul>
  <li>On a phone only Firefox works; Chrome for Android installs no extensions.</li>
  <li>The store-independent package on the release page was older than both stores when
      checked (2.27.0 against 2.33.4, 15 August 2026) and does not update itself.</li>
  <li>Six of twenty measured sources came back without a citation record. What a page does
      not declare, the capture cannot know.</li>
  <li>The time anchor is not a qualified timestamp, and no stamp says anything about
      whether the page showed what it showed.</li>
  <li>Capture only what you have legitimate access to. The extension reaches exactly what
      your browser already shows you — and a capture is documentation, not a legally
      certified record.</li>
</ul>

<p class="note">
  Disclosure: the extension described here is our own. Store versions were read from the
  public listings on 15 August 2026 and change with every release; the machine-readable
  current state is linked above. Measurements are cited with their dates and raw data.
  Corrections via <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">an issue</a>
  are taken up.
</p>
""",
}

# ---------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "title": "Full Page PDF Snap in Firefox und Chrome: Installation und wissenschaftlicher Arbeitsablauf",
    "description": (
        "Die Installationswege für Firefox (Desktop und Android) und Chrome, dazu der "
        "Arbeitsablauf in der Forschung: ganze Seite oder sichtbarer Bereich, Zitationsdaten "
        "mit RIS-Datensatz für Citavi, Zotero und EndNote, Auflösungsskalierung, A4 und der "
        "Consent-Schalter — und was Version 2.33.4 geändert hat. Store-Stände geprüft am "
        "15. August 2026."
    ),
    "h1": "Full Page PDF Snap in Firefox und Chrome: Installation und wissenschaftlicher Arbeitsablauf",
    "standfirst": (
        "Dies ist die praktische Anleitung für Wissenschaftler:innen und Studierende: wie "
        "die Erweiterung in Firefox — einschließlich Firefox für Android — und in Chrome "
        "kommt, und wie eine Aufnahme eine Quelle anschließend durch den wissenschaftlichen "
        "Arbeitsablauf trägt, von der Wahl zwischen ganzer Seite und sichtbarem Bereich bis "
        "zum RIS-Datensatz, den Ihre Literaturverwaltung importiert. Die Store-Stände wurden "
        "am 15. August 2026 geprüft und sind mit diesem Datum genannt."
    ),
    "meta": "15. August 2026 · Store-Stände am selben Tag geprüft",
    "body": """
<h2>1. Firefox: Desktop und Android aus einem Eintrag</h2>
<p>
  Am Rechner führt der Weg über den
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">Eintrag
  bei Firefox Add-ons</a>: ein Klick, die Datei ist von Mozilla signiert, und die Erweiterung
  aktualisiert sich von dort selbst. Als dieser Text entstand, trug der Eintrag die Version
  2.33.4 (geprüft am 15. August 2026); er braucht Firefox 109 oder neuer.
</p>
<p>
  Auf dem Telefon bedient derselbe Eintrag <strong>Firefox für Android</strong> (Version 127
  oder neuer): aus dem Add-ons-Menü des Browsers installieren, dann auf einer Seite das Menü
  öffnen und die Erweiterung antippen — die Aufnahme startet sofort, ohne das Popup, das der
  Desktop zeigt. Eine einzige Benachrichtigung meldet das fertige PDF; ein Antippen öffnet
  die Datei, und das Teilen-Menü des Systems übernimmt von dort.
</p>
<p>
  Firefox ist auf dem Telefon auch der einzige Weg, denn Chrome für Android installiert
  überhaupt keine Erweiterungen. Und wer ganz ohne Store arbeiten will, findet auf der
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">Release-Seite</a>
  dieselbe signierte Datei — mit zwei ehrlichen Einschränkungen: Das neueste Paket dort war
  bei der Prüfung die 2.27.0 (15. August 2026), hinter beiden Stores, und eine so
  installierte Erweiterung aktualisiert sich nicht selbst. Welcher Store gerade welche
  Version trägt, ist maschinenlesbar unter
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>
  veröffentlicht.
</p>

<h2>2. Chrome, Edge, Brave, Vivaldi</h2>
<p>
  Für Chrome führt der Weg über den
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Eintrag
  im Chrome Web Store</a> — bei der Prüfung ebenfalls auf Version 2.33.4 (15. August 2026),
  mit Chrome 116 oder neuer, ebenfalls mit Selbstaktualisierung aus dem Store. Brave und
  Vivaldi installieren aus dem Chrome Web Store ohne weiteres; Edge fragt einmal, ob
  Erweiterungen aus anderen Stores erlaubt sind; Opera braucht zuerst sein Add-on
  <em>Install Chrome Extensions</em>.
</p>
<p>
  Beide Fassungen kommen aus einer Quelle — Aufnahme, PDF und RIS-Datensatz sind dieselben;
  was sich unterscheidet, ist die Plattform darum herum. Am Rechner ist der schnellste Weg
  zur Aufnahme die Tastatur: <code>Alt+Umschalt+Y</code>. Ein Rechtsklick auf das Symbol in
  der Werkzeugleiste trägt die Schnellschalter für Skalierung, Download-Ordner und den
  Umgang mit Bannern.
</p>

<h2>3. Die ganze Seite — oder nur, was Sie sehen</h2>
<p>
  Das Popup bietet zwei Aufnahmen. <strong>Ganze Seite</strong> scrollt das Dokument von
  oben nach unten und fügt jeden Ausschnitt zu einem nahtlosen Blatt zusammen — die richtige
  Wahl für alles, was Sie zitieren werden. <strong>Nur sichtbarer Bereich</strong>, die
  zweite Schaltfläche, schreibt genau das, was auf dem Schirm steht, als ebensolches PDF mit
  denselben Zitationsdaten — die richtige Wahl, wenn ein einzelner Beitrag aus einem langen
  Verlauf zählt oder wenn eine Seite beim Scrollen weiterwächst und kein Ende hat, das man
  aufnehmen könnte.
</p>
<p>
  Warum sich das überhaupt lohnt — eine Quelle, die verschwindet, eine Zitation, die von
  Hand abgetippt wird, eine Datei, die keine Maschine liest —, ist das Thema des
  <a href="/how-to/for-students/">Begleitartikels für Studierende</a>, mit einer Messung
  hinter jedem Punkt. Der ehrliche Vergleich mit dem Druckexport des Browsers, der beim
  Text gewinnt, steht in der <a href="/how-to/save-a-webpage-as-pdf/">allgemeinen
  Anleitung</a>. Beides ist hier verlinkt statt wiederholt.
</p>

<h2>4. Zitationsdaten: auf dem Blatt, in der Datei, in der Literaturverwaltung</h2>
<p>
  Eine Aufnahme liest die bibliografischen Metadaten, die die Seite selbst deklariert, und
  legt sie an drei Stellen. Auf dem Blatt: Verfasser:innen, Zeitschrift, DOI, Lizenz und der
  Abrufzeitpunkt. In der Datei: die Dokumenteigenschaften, ein XMP-Strom mit Dublin Core
  und PRISM — die Vokabulare, die Literaturverwaltungen lesen — und zwölf weitere Felder im
  Dokument-Informationsblock. Und als Datensatz: eine Anlage <code>quelle.ris</code> im PDF,
  dazu eine separate <code>.ris</code>-Datei daneben, die Citavi, Zotero und EndNote direkt
  importieren. Die separate Datei ist eine Bequemlichkeit und lässt sich in den Einstellungen
  abschalten; der eingebettete Datensatz reist immer mit dem PDF.
</p>
<p>
  Seit dem 7. August 2026 trägt auch der Dateiname die Quelle: Die Voreinstellung ist
  <code>{title}_{site}_{date}_{time}</code>, der Titel kommt aus den Verlagsmetadaten statt
  aus dem Fenstertitel — ein Ordner voller Aufnahmen liest sich dann wie ein
  Literaturverzeichnis statt wie eine Adressliste.
</p>
<p>
  Die ehrliche Grenze: Die Erweiterung liest, was die offene Seite deklariert, und fragt
  keinen Zitationsdienst. Eine dünne Seite kann nicht deklarieren, was sie nie deklariert
  hat — von 20 Quellen einer echten Leseliste (gemessen am 4. August 2026) kamen 6 ohne
  Datensatz zurück.
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">Rohdaten</a>.
  Wie der Leser im Vergleich zu Citoid, dem Zitationsdienst der Wikimedia, abschneidet, ist
  unter <a href="/measurements/citation-extraction/">Zitationsextraktion</a> gemessen.
</p>

<h2>5. Einstellungen, die in der Forschungsarbeit zählen</h2>
<ul>
  <li><strong>Auflösungsskalierung</strong> von 1,0x bis 2,0x (Voreinstellung 1,5x am
      Rechner, 1,0x auf Android). In der Praxis: hoch für Kleingedrucktes und Abbildungen,
      herunter, wenn die Dateigröße zählt. Ist das PDF für OCR oder ein Sprachmodell
      gedacht, ist die Schwelle, unter der die Erkennung einbricht, gemessen statt geraten:
      <a href="/measurements/webpage-to-pdf-for-ocr/">Webseite als PDF für OCR</a>.</li>
  <li><strong>Ein Blatt oder A4.</strong> Voreinstellung ist eine durchgehende Seite — ohne
      Nähte, in die eine Maschine fallen könnte. Wo bedrucktes Papier das Ziel ist,
      umbrechen die A4-Einstellung so, dass die Brüche zwischen Zeilen fallen statt
      durch sie hindurch.</li>
  <li><strong>Der Consent-Schalter.</strong> Einwilligungsbanner sperren oft das Scrollen;
      der Schalter im Popup blendet sie für die Dauer der Aufnahme aus und stellt sie
      danach wieder her. Nichts wird in Ihrem Namen weggeklickt — Ausblenden ist
      nicht Entscheiden.</li>
  <li><strong>Der Zeitanker.</strong> Seit dem 5. August 2026 kann sich eine Aufnahme mit
      einer „nicht vor"-Zeit aus dem öffentlichen drand-Beacon stempeln — voreingestellt
      aus, weil es der einzige Netzzugriff der Erweiterung ist. Er verankert, dass die
      Aufnahme nicht älter ist als die Runde des Beacons; er sagt nichts darüber, was die
      Seite zeigte, und er ist kein qualifizierter Zeitstempel im Rechtssinn.</li>
</ul>

<h2>6. Was die aktuelle Version geändert hat</h2>
<p>
  Die Version 2.33.4, bei Entstehen dieses Textes in beiden Stores (15. August 2026), hat
  den wissenschaftlichen Arbeitsablauf nach vorn gerückt. Aus dem
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">Changelog</a>:
</p>
<ul>
  <li>Zitationsmetadaten stecken jetzt im PDF selbst — XMP mit Dublin Core und PRISM, zwölf
      Felder im Dokument-Informationsblock —, nicht nur im RIS-Datensatz (7. August 2026).
      Lizenz, Werkart, Fassung und Änderungsdatum folgten am 10. August, ebenso die
      RIS-Ausgabe in der Chrome-Fassung.</li>
  <li>Der RIS-Datensatz ist immer als <code>quelle.ris</code> ins PDF eingebettet; die
      separate Datei daneben lässt sich abschalten (10. August 2026).</li>
  <li>Datensätze ohne Verfasser beginnen jetzt mit dem Titel, wie es die Zitationsstile
      verlangen, statt mit einem nackten „(o. J.)."; ein doppelt eingetragener
      Zeitschriftenname als Verlag wird nicht mehr zweimal geschrieben (10. August 2026).</li>
  <li>Auf Android lädt die Aufnahme direkt in dem Reiter herunter, in dem Sie stehen — eine
      Benachrichtigung, kein Zusatzreiter. Die Beidateien (RIS-Datensatz, Linkkarte,
      Verlagsdatei) gibt es nur noch am Rechner; auf dem Telefon steckt ihr Inhalt im PDF
      selbst (7. August 2026).</li>
  <li>Dateinamen tragen den Seitentitel aus den Verlagsmetadaten (7. August 2026).</li>
</ul>

<h2>Was sie nicht tut</h2>
<ul>
  <li>Auf dem Telefon funktioniert nur Firefox; Chrome für Android installiert keine
      Erweiterungen.</li>
  <li>Das store-unabhängige Paket auf der Release-Seite war bei der Prüfung älter als beide
      Stores (2.27.0 gegenüber 2.33.4, 15. August 2026) und aktualisiert sich nicht selbst.</li>
  <li>Sechs von zwanzig gemessenen Quellen kamen ohne Zitationsdatensatz zurück. Was eine
      Seite nicht deklariert, kann die Aufnahme nicht wissen.</li>
  <li>Der Zeitanker ist kein qualifizierter Zeitstempel, und kein Stempel sagt etwas darüber,
      ob die Seite zeigte, was sie zeigte.</li>
  <li>Nehmen Sie nur auf, auf was Sie legitimen Zugriff haben. Die Erweiterung reicht genau
      so weit, wie Ihr Browser Ihnen die Seite ohnehin zeigt — und eine Aufnahme ist eine
      Dokumentation, kein beglaubigter Nachweis.</li>
</ul>

<p class="note">
  Offenlegung: Die hier beschriebene Erweiterung ist unsere eigene. Die Store-Stände wurden
  am 15. August 2026 aus den öffentlichen Einträgen gelesen und ändern sich mit jeder
  Veröffentlichung; der maschinenlesbare aktuelle Stand ist oben verlinkt. Messungen sind
  mit ihren Daten und Rohdaten zitiert. Korrekturen über ein
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">Issue</a> werden aufgenommen.
</p>
""",
}

# ---------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "title": "Full Page PDF Snap en Firefox y Chrome: instalación y flujo de trabajo académico",
    "description": (
        "Las vías de instalación para Firefox (escritorio y Android) y Chrome, y después el "
        "flujo de trabajo en investigación: página completa o zona visible, datos de citación "
        "con registro RIS para Citavi, Zotero y EndNote, escalado de resolución, A4 y el "
        "interruptor de consentimiento — y qué cambió la versión 2.33.4. Versiones de las "
        "tiendas comprobadas el 15 de agosto de 2026."
    ),
    "h1": "Full Page PDF Snap en Firefox y Chrome: instalación y flujo de trabajo académico",
    "standfirst": (
        "Esta es la guía práctica para investigadores y estudiantes: cómo instalar la "
        "extensión en Firefox —incluido Firefox para Android— y en Chrome, y cómo una "
        "captura acompaña después a una fuente por el flujo de trabajo académico, desde la "
        "elección entre página completa y zona visible hasta el registro RIS que importa su "
        "gestor de referencias. Las versiones de las tiendas se comprobaron el 15 de agosto "
        "de 2026 y se citan con esa fecha."
    ),
    "meta": "15 de agosto de 2026 · versiones de las tiendas comprobadas ese mismo día",
    "body": """
<h2>1. Firefox: escritorio y Android desde una misma ficha</h2>
<p>
  En el escritorio la vía es la
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">ficha de
  Firefox Add-ons</a>: un clic, el archivo está firmado por Mozilla y la extensión se
  actualiza sola desde allí. Cuando se escribió este texto, la ficha llevaba la versión
  2.33.4 (comprobado el 15 de agosto de 2026); necesita Firefox 109 o superior.
</p>
<p>
  En el teléfono, la misma ficha sirve <strong>Firefox para Android</strong> (versión 127 o
  superior): instálela desde el menú de complementos del propio navegador, luego abra el
  menú en una página y toque la extensión — la captura comienza de inmediato, sin la
  ventana emergente que muestra el escritorio. Una única notificación anuncia el PDF
  terminado; al tocarla se abre el archivo, y el menú de compartir del sistema se encarga
  del resto.
</p>
<p>
  Firefox es también la única vía en el teléfono, porque Chrome para Android no instala
  ninguna extensión. Y si prefiere prescindir de tiendas, la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">página de
  versiones</a> sirve el mismo archivo firmado — con dos salvedades honestas: el paquete
  más reciente allí era el 2.27.0 al comprobarlo (15 de agosto de 2026), por detrás de
  ambas tiendas, y una extensión instalada así no se actualiza sola. Qué tienda ofrece qué
  versión en cada momento se publica en formato legible por máquinas en
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>.
</p>

<h2>2. Chrome, Edge, Brave, Vivaldi</h2>
<p>
  Para Chrome la vía es la
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">ficha
  de Chrome Web Store</a> — también en la versión 2.33.4 al comprobarlo (15 de agosto de
  2026), con Chrome 116 o superior, y con actualización automática desde la tienda. Brave y
  Vivaldi instalan desde Chrome Web Store tal cual; Edge pregunta una vez si se permiten
  extensiones de otras tiendas; Opera necesita primero su complemento <em>Install Chrome
  Extensions</em>.
</p>
<p>
  Ambas versiones salen de una misma fuente: la captura, el PDF y el registro RIS son los
  mismos; lo que cambia es la plataforma que los rodea. En el escritorio, el camino más
  rápido a una captura es el teclado: <code>Alt+Mayús+Y</code>. Un clic derecho sobre el
  icono de la barra de herramientas ofrece los interruptores rápidos de escalado, carpeta de
  descarga y tratamiento de banners.
</p>

<h2>3. La página entera — o solo lo que ve</h2>
<p>
  La ventana emergente ofrece dos capturas. <strong>Página completa</strong> recorre el
  documento de arriba abajo y une cada segmento en una hoja sin costuras — la elección
  correcta para todo lo que vaya a citar. <strong>Solo la zona visible</strong>, el segundo
  botón, escribe exactamente lo que hay en pantalla, como el mismo tipo de PDF con los
  mismos datos de citación — la elección correcta cuando importa una sola entrada de un hilo
  largo, o cuando una página sigue creciendo al desplazarse y no tiene un final que capturar.
</p>
<p>
  Por qué merece la pena hacerlo —una fuente que desaparece, una cita que hay que teclear a
  mano, un archivo que ninguna máquina puede leer— es el tema del
  <a href="/how-to/for-students/">artículo complementario para estudiantes</a>, con una
  medición detrás de cada punto. La comparación honesta con la exportación de impresión del
  propio navegador, que gana en texto seleccionable, está en la
  <a href="/how-to/save-a-webpage-as-pdf/">guía general</a>. Ambos se enlazan aquí en lugar
  de repetirse.
</p>

<h2>4. Datos de citación: en la hoja, en el archivo, en el gestor de referencias</h2>
<p>
  Una captura lee los metadatos bibliográficos que la propia página declara y los coloca en
  tres lugares. En la hoja: autores, revista, DOI, licencia y momento de la consulta. En el
  archivo: las propiedades del documento, un flujo XMP con Dublin Core y PRISM —los
  vocabularios que leen los gestores de referencias— y doce campos más en el diccionario de
  información del documento. Y como registro: un adjunto <code>quelle.ris</code> dentro del
  PDF, más un archivo <code>.ris</code> separado junto a él que Citavi, Zotero y EndNote
  importan directamente. El archivo separado es una comodidad y puede desactivarse en los
  ajustes; el registro incrustado viaja siempre con el PDF.
</p>
<p>
  Desde el 7 de agosto de 2026 el nombre del archivo también lleva la fuente: la plantilla
  por defecto es <code>{title}_{site}_{date}_{time}</code>, con el título tomado de los
  metadatos del editor en lugar del título de la ventana — una carpeta de capturas se lee
  entonces como una bibliografía y no como una lista de direcciones.
</p>
<p>
  El límite honesto: la extensión lee lo que la página abierta declara y no consulta ningún
  servicio de citación. Una página pobre en datos no puede declarar lo que nunca declaró —
  de 20 fuentes de una lista de lectura real (medido el 4 de agosto de 2026), 6 volvieron
  sin registro.
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">Datos
  brutos</a>. Cómo se compara el lector con Citoid, el servicio de citación de Wikimedia,
  está medido en <a href="/measurements/citation-extraction/">extracción de citas</a>.
</p>

<h2>5. Ajustes que importan en el trabajo de investigación</h2>
<ul>
  <li><strong>Escalado de resolución</strong> de 1.0x a 2.0x (por defecto 1.5x en escritorio,
      1.0x en Android). En la práctica: súbalo para letra pequeña y figuras, bájelo cuando
      importe el tamaño del archivo. Si el PDF está destinado a OCR o a un modelo de
      lenguaje, el umbral bajo el cual el reconocimiento se derrumba está medido, no
      adivinado: <a href="/measurements/webpage-to-pdf-for-ocr/">página web a PDF para
      OCR</a>.</li>
  <li><strong>Una hoja o A4.</strong> Por defecto es una página continua, sin costuras en
      las que una máquina pueda caer. Cuando el destino es el papel impreso, el ajuste A4
      pagina con cortes que caen entre líneas en lugar de atravesarlas.</li>
  <li><strong>El interruptor de consentimiento.</strong> Los banners de consentimiento suelen
      bloquear el desplazamiento; el interruptor de la ventana emergente los oculta mientras
      dura la captura y los restaura después. Nada se clica en su nombre — ocultar no es
      decidir.</li>
  <li><strong>El ancla temporal.</strong> Desde el 5 de agosto de 2026 una captura puede
      sellarse con una hora «no antes de» tomada de la baliza pública drand — desactivada
      por defecto, porque es la única petición de red de la extensión. Ancla que la captura
      no es más antigua que la ronda de la baliza; no dice nada sobre lo que mostraba la
      página, y no es un sello de tiempo cualificado en sentido jurídico.</li>
</ul>

<h2>6. Qué cambió la versión actual</h2>
<p>
  La versión 2.33.4, presente en ambas tiendas cuando se escribió este texto (15 de agosto
  de 2026), puso el flujo de trabajo académico en primer plano. Según el
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">registro de
  cambios</a>:
</p>
<ul>
  <li>Los metadatos de citación viven ahora en el propio PDF —XMP con Dublin Core y PRISM,
      doce campos de información del documento—, no solo en el registro RIS (7 de agosto de
      2026). Licencia, tipo de obra, versión y fecha de modificación llegaron el 10 de
      agosto, igual que la salida RIS en la versión para Chrome.</li>
  <li>El registro RIS va siempre incrustado en el PDF como <code>quelle.ris</code>; el
      archivo separado puede desactivarse (10 de agosto de 2026).</li>
  <li>Los registros sin autor empiezan ahora con el título, como exigen los estilos de cita,
      en lugar de un desnudo «(s. f.).»; un nombre de revista duplicado como editorial ya no
      se escribe dos veces (10 de agosto de 2026).</li>
  <li>En Android la captura se descarga directamente en la pestaña en la que usted está —una
      notificación, sin pestaña extra. Los archivos acompañantes (registro RIS, mapa de
      enlaces, archivo del editor) existen ahora solo en escritorio; en el teléfono su
      contenido vive dentro del PDF (7 de agosto de 2026).</li>
  <li>Los nombres de archivo llevan el título de la página tomado de los metadatos del editor
      (7 de agosto de 2026).</li>
</ul>

<h2>Lo que no hace</h2>
<ul>
  <li>En el teléfono solo funciona Firefox; Chrome para Android no instala extensiones.</li>
  <li>El paquete independiente de la tienda en la página de versiones era más antiguo que
      ambas tiendas al comprobarlo (2.27.0 frente a 2.33.4, 15 de agosto de 2026) y no se
      actualiza solo.</li>
  <li>Seis de veinte fuentes medidas volvieron sin registro de citación. Lo que una página no
      declara, la captura no puede saberlo.</li>
  <li>El ancla temporal no es un sello de tiempo cualificado, y ningún sello dice nada sobre
      si la página mostraba lo que mostraba.</li>
  <li>Capture solo aquello a lo que tiene acceso legítimo. La extensión alcanza exactamente
      lo que su navegador ya le muestra — y una captura es documentación, no una prueba
      certificada legalmente.</li>
</ul>

<p class="note">
  Divulgación: la extensión descrita aquí es nuestra. Las versiones de las tiendas se
  leyeron de las fichas públicas el 15 de agosto de 2026 y cambian con cada publicación; el
  estado actual legible por máquinas está enlazado arriba. Las mediciones se citan con sus
  fechas y datos brutos. Las correcciones se reciben a través de un
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">issue</a>.
</p>
""",
}

# ---------------------------------------------------------------- Français ----
TEXTE["fr"] = {
    "title": "Full Page PDF Snap dans Firefox et Chrome : installation et flux de travail académique",
    "description": (
        "Les voies d'installation pour Firefox (bureau et Android) et Chrome, puis le flux de "
        "travail en recherche : page entière ou zone visible, données de citation avec "
        "enregistrement RIS pour Citavi, Zotero et EndNote, mise à l'échelle de la "
        "résolution, A4 et l'interrupteur de consentement — et ce que la version 2.33.4 a "
        "changé. Versions des boutiques vérifiées le 15 août 2026."
    ),
    "h1": "Full Page PDF Snap dans Firefox et Chrome : installation et flux de travail académique",
    "standfirst": (
        "Voici le guide pratique pour les chercheuses et chercheurs et les étudiantes et "
        "étudiants : comment installer l'extension dans Firefox — y compris Firefox pour "
        "Android — et dans Chrome, et comment une capture accompagne ensuite une source tout "
        "au long du flux de travail académique, du choix entre page entière et zone visible "
        "jusqu'à l'enregistrement RIS que votre gestionnaire de références importe. Les "
        "versions des boutiques ont été vérifiées le 15 août 2026 et sont citées avec cette "
        "date."
    ),
    "meta": "15 août 2026 · versions des boutiques vérifiées le jour même",
    "body": """
<h2>1. Firefox : bureau et Android depuis une même fiche</h2>
<p>
  Sur le bureau, la voie passe par la
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">fiche
  Firefox Add-ons</a> : un clic, le fichier est signé par Mozilla, et l'extension se met à
  jour toute seule depuis là. Au moment où ce texte était écrit, la fiche portait la version
  2.33.4 (vérifié le 15 août 2026) ; elle exige Firefox 109 ou plus récent.
</p>
<p>
  Sur téléphone, la même fiche sert <strong>Firefox pour Android</strong> (version 127 ou
  plus récente) : installez-la depuis le menu des modules du navigateur lui-même, puis
  ouvrez le menu sur une page et touchez l'extension — la capture démarre aussitôt, sans la
  fenêtre contextuelle qu'affiche le bureau. Une seule notification annonce le PDF terminé ;
  un appui ouvre le fichier, et le menu de partage du système prend le relais.
</p>
<p>
  Firefox est aussi la seule voie sur téléphone, car Chrome pour Android n'installe aucune
  extension. Et si vous préférez vous passer de boutique, la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">page des
  versions</a> sert le même fichier signé — avec deux réserves honnêtes : le paquet le plus
  récent y était le 2.27.0 lors de la vérification (15 août 2026), en retard sur les deux
  boutiques, et une extension installée ainsi ne se met pas à jour toute seule. Quelle
  boutique porte quelle version à un instant donné est publié en format lisible par machine
  à l'adresse
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>.
</p>

<h2>2. Chrome, Edge, Brave, Vivaldi</h2>
<p>
  Pour Chrome, la voie passe par la
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">fiche du
  Chrome Web Store</a> — également à la version 2.33.4 lors de la vérification (15 août
  2026), avec Chrome 116 ou plus récent, et mise à jour automatique depuis la boutique.
  Brave et Vivaldi installent depuis le Chrome Web Store tel quel ; Edge demande une fois
  d'autoriser les extensions d'autres boutiques ; Opera a d'abord besoin de son module
  <em>Install Chrome Extensions</em>.
</p>
<p>
  Les deux versions sortent d'une même source : la capture, le PDF et l'enregistrement RIS
  sont identiques ; ce qui diffère, c'est la plateforme autour. Sur le bureau, le chemin le
  plus rapide vers une capture est le clavier : <code>Alt+Maj+Y</code>. Un clic droit sur
  l'icône de la barre d'outils offre les interrupteurs rapides pour l'échelle, le dossier de
  téléchargement et le traitement des bannières.
</p>

<h2>3. La page entière — ou seulement ce que vous voyez</h2>
<p>
  La fenêtre contextuelle propose deux captures. <strong>Page entière</strong> fait défiler
  le document de haut en bas et assemble chaque segment en une feuille sans couture — le bon
  choix pour tout ce que vous citerez. <strong>Zone visible seulement</strong>, le second
  bouton, écrit exactement ce qui est à l'écran, sous la forme du même PDF avec les mêmes
  données de citation — le bon choix quand un seul message d'un long fil compte, ou quand
  une page continue de s'allonger au défilement et n'a pas de fin à capturer.
</p>
<p>
  Pourquoi cela vaut-il la peine — une source qui disparaît, une citation à retaper à la
  main, un fichier qu'aucune machine ne peut lire —, c'est le sujet de
  <a href="/how-to/for-students/">l'article complémentaire pour les étudiants</a>, avec une
  mesure derrière chaque point. La comparaison honnête avec l'export d'impression du
  navigateur lui-même, qui gagne sur le texte sélectionnable, se trouve dans le
  <a href="/how-to/save-a-webpage-as-pdf/">guide général</a>. Les deux sont liés ici plutôt
  que répétés.
</p>

<h2>4. Données de citation : sur la feuille, dans le fichier, dans le gestionnaire de références</h2>
<p>
  Une capture lit les métadonnées bibliographiques que la page elle-même déclare et les
  dépose en trois endroits. Sur la feuille : auteurs, revue, DOI, licence et moment de la
  consultation. Dans le fichier : les propriétés du document, un flux XMP avec Dublin Core
  et PRISM — les vocabulaires que lisent les gestionnaires de références — et douze champs
  supplémentaires dans le dictionnaire d'informations du document. Et comme enregistrement :
  une pièce jointe <code>quelle.ris</code> dans le PDF, plus un fichier <code>.ris</code>
  séparé à côté, que Citavi, Zotero et EndNote importent directement. Le fichier séparé est
  une commodité et peut être désactivé dans les réglages ; l'enregistrement intégré voyage
  toujours avec le PDF.
</p>
<p>
  Depuis le 7 août 2026, le nom du fichier porte lui aussi la source : le modèle par défaut
  est <code>{title}_{site}_{date}_{time}</code>, le titre étant pris dans les métadonnées de
  l'éditeur plutôt que dans le titre de la fenêtre — un dossier de captures se lit alors
  comme une bibliographie et non comme une liste d'adresses.
</p>
<p>
  La limite honnête : l'extension lit ce que la page ouverte déclare et n'interroge aucun
  service de citation. Une page pauvre ne peut pas déclarer ce qu'elle n'a jamais déclaré —
  sur 20 sources d'une vraie liste de lecture (mesuré le 4 août 2026), 6 sont revenues sans
  enregistrement.
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">Données
  brutes</a>. Comment le lecteur se compare à Citoid, le service de citation de Wikimedia,
  est mesuré à la page <a href="/measurements/citation-extraction/">extraction de
  citations</a>.
</p>

<h2>5. Réglages qui comptent dans le travail de recherche</h2>
<ul>
  <li><strong>Mise à l'échelle de la résolution</strong> de 1,0x à 2,0x (1,5x par défaut sur
      le bureau, 1,0x sur Android). En pratique : montez-la pour les petits caractères et les
      figures, baissez-la quand la taille du fichier compte. Si le PDF est destiné à l'OCR ou
      à un modèle de langage, le seuil sous lequel la reconnaissance s'effondre est mesuré,
      pas deviné : <a href="/measurements/webpage-to-pdf-for-ocr/">page web en PDF pour
      l'OCR</a>.</li>
  <li><strong>Une feuille ou A4.</strong> Par défaut, une page continue, sans coutures où une
      machine pourrait trébucher. Quand le papier imprimé est la cible, le réglage A4
      pagine avec des coupures qui tombent entre les lignes au lieu de les traverser.</li>
  <li><strong>L'interrupteur de consentement.</strong> Les bannières de consentement bloquent
      souvent le défilement ; l'interrupteur de la fenêtre contextuelle les masque pendant la
      capture et les rétablit ensuite. Rien n'est cliqué en votre nom — masquer n'est pas
      décider.</li>
  <li><strong>L'ancre temporelle.</strong> Depuis le 5 août 2026, une capture peut se tamponner
      d'une heure « pas avant » issue de la balise publique drand — désactivée par défaut, car
      c'est la seule requête réseau de l'extension. Elle ancre que la capture n'est pas plus
      ancienne que la ronde de la balise ; elle ne dit rien de ce que la page affichait, et ce
      n'est pas un horodatage qualifié au sens juridique.</li>
</ul>

<h2>6. Ce que la version actuelle a changé</h2>
<p>
  La version 2.33.4, présente dans les deux boutiques au moment où ce texte était écrit
  (15 août 2026), a mis le flux de travail académique au premier plan. D'après le
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">journal des
  modifications</a> :
</p>
<ul>
  <li>Les métadonnées de citation vivent désormais dans le PDF lui-même — XMP avec Dublin
      Core et PRISM, douze champs d'information du document —, et pas seulement dans
      l'enregistrement RIS (7 août 2026). Licence, type d'œuvre, version et date de
      modification ont suivi le 10 août, de même que la sortie RIS dans la version
      Chrome.</li>
  <li>L'enregistrement RIS est toujours intégré au PDF sous <code>quelle.ris</code> ; le
      fichier séparé peut être désactivé (10 août 2026).</li>
  <li>Les enregistrements sans auteur commencent désormais par le titre, comme l'exigent les
      styles de citation, au lieu d'un « (s. d.). » nu ; un nom de revue dupliqué comme
      éditeur n'est plus écrit deux fois (10 août 2026).</li>
  <li>Sur Android, la capture se télécharge directement dans l'onglet où vous êtes — une
      notification, pas d'onglet supplémentaire. Les fichiers d'accompagnement (enregistrement
      RIS, carte des liens, fichier de l'éditeur) n'existent plus que sur le bureau ; sur
      téléphone, leur contenu vit dans le PDF (7 août 2026).</li>
  <li>Les noms de fichiers portent le titre de la page issu des métadonnées de l'éditeur
      (7 août 2026).</li>
</ul>

<h2>Ce qu'elle ne fait pas</h2>
<ul>
  <li>Sur téléphone, seul Firefox fonctionne ; Chrome pour Android n'installe aucune
      extension.</li>
  <li>Le paquet indépendant de la boutique sur la page des versions était plus ancien que les
      deux boutiques lors de la vérification (2.27.0 contre 2.33.4, 15 août 2026) et ne se
      met pas à jour tout seul.</li>
  <li>Six sources sur vingt mesurées sont revenues sans enregistrement de citation. Ce qu'une
      page ne déclare pas, la capture ne peut pas le savoir.</li>
  <li>L'ancre temporelle n'est pas un horodatage qualifié, et aucun tampon ne dit quoi que ce
      soit sur ce que la page affichait réellement.</li>
  <li>Ne capturez que ce à quoi vous avez un accès légitime. L'extension atteint exactement ce
      que votre navigateur vous montre déjà — et une capture est une documentation, pas une
      preuve certifiée juridiquement.</li>
</ul>

<p class="note">
  Divulgation : l'extension décrite ici est la nôtre. Les versions des boutiques ont été lues
  sur les fiches publiques le 15 août 2026 et changent à chaque publication ; l'état actuel
  lisible par machine est lié ci-dessus. Les mesures sont citées avec leurs dates et leurs
  données brutes. Les corrections sont les bienvenues via un
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">ticket</a>.
</p>
""",
}

# ---------------------------------------------------------------- Italiano ----
TEXTE["it"] = {
    "title": "Full Page PDF Snap in Firefox e Chrome: installazione e flusso di lavoro accademico",
    "description": (
        "I percorsi di installazione per Firefox (desktop e Android) e Chrome, poi il flusso "
        "di lavoro nella ricerca: pagina intera o area visibile, dati di citazione con record "
        "RIS per Citavi, Zotero ed EndNote, scala di risoluzione, A4 e l'interruttore del "
        "consenso — e cosa è cambiato con la versione 2.33.4. Versioni degli store "
        "verificate il 15 agosto 2026."
    ),
    "h1": "Full Page PDF Snap in Firefox e Chrome: installazione e flusso di lavoro accademico",
    "standfirst": (
        "Questa è la guida pratica per chi fa ricerca e per chi studia: come installare "
        "l'estensione in Firefox — incluso Firefox per Android — e in Chrome, e come una "
        "cattura accompagna poi una fonte attraverso il flusso di lavoro accademico, dalla "
        "scelta tra pagina intera e area visibile fino al record RIS che il vostro gestore "
        "di riferimenti importa. Le versioni degli store sono state verificate il 15 agosto "
        "2026 e sono citate con quella data."
    ),
    "meta": "15 agosto 2026 · versioni degli store verificate in giornata",
    "body": """
<h2>1. Firefox: desktop e Android da una stessa scheda</h2>
<p>
  Sul desktop il percorso passa dalla
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">scheda di
  Firefox Add-ons</a>: un clic, il file è firmato da Mozilla e l'estensione si aggiorna da
  sola da lì. Quando questo testo è stato scritto, la scheda riportava la versione 2.33.4
  (verificato il 15 agosto 2026); richiede Firefox 109 o successivo.
</p>
<p>
  Sul telefono la stessa scheda serve <strong>Firefox per Android</strong> (versione 127 o
  successiva): installatela dal menu dei componenti aggiuntivi del browser stesso, poi
  aprite il menu su una pagina e toccate l'estensione — la cattura parte subito, senza il
  popup che mostra il desktop. Un'unica notifica annuncia il PDF finito; toccandola si apre
  il file, e il menu di condivisione del sistema fa il resto.
</p>
<p>
  Firefox è anche l'unica via sul telefono, perché Chrome per Android non installa alcuna
  estensione. E se preferite fare a meno degli store, la
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">pagina dei
  rilasci</a> serve lo stesso file firmato — con due avvertenze oneste: il pacchetto più
  recente lì era il 2.27.0 al momento della verifica (15 agosto 2026), indietro rispetto a
  entrambi gli store, e un'estensione installata così non si aggiorna da sola. Quale store
  porta quale versione in un dato momento è pubblicato in formato leggibile dalle macchine
  all'indirizzo
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>.
</p>

<h2>2. Chrome, Edge, Brave, Vivaldi</h2>
<p>
  Per Chrome il percorso passa dalla
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">scheda
  del Chrome Web Store</a> — anch'essa alla versione 2.33.4 al momento della verifica
  (15 agosto 2026), con Chrome 116 o successivo, e con aggiornamento automatico dallo
  store. Brave e Vivaldi installano dal Chrome Web Store così come sono; Edge chiede una
  volta di consentire le estensioni da altri store; Opera ha prima bisogno del suo
  componente <em>Install Chrome Extensions</em>.
</p>
<p>
  Entrambe le versioni nascono da un'unica fonte: la cattura, il PDF e il record RIS sono
  gli stessi; ciò che cambia è la piattaforma intorno. Sul desktop la via più rapida a una
  cattura è la tastiera: <code>Alt+Maiusc+Y</code>. Un clic destro sull'icona nella barra
  degli strumenti offre gli interruttori rapidi per scala, cartella di download e gestione
  dei banner.
</p>

<h2>3. La pagina intera — o solo ciò che vedete</h2>
<p>
  Il popup offre due catture. <strong>Pagina intera</strong> scorre il documento dall'alto
  in basso e unisce ogni segmento in un foglio senza cuciture — la scelta giusta per tutto
  ciò che citerete. <strong>Solo area visibile</strong>, il secondo pulsante, scrive
  esattamente ciò che è sullo schermo, come lo stesso tipo di PDF con gli stessi dati di
  citazione — la scelta giusta quando conta un solo intervento di una lunga discussione, o
  quando una pagina continua a crescere durante lo scorrimento e non ha un fondo da
  catturare.
</p>
<p>
  Perché valga la pena farlo — una fonte che sparisce, una citazione da riscrivere a mano,
  un file che nessuna macchina riesce a leggere — è l'argomento
  <a href="/how-to/for-students/">dell'articolo gemello per gli studenti</a>, con una
  misurazione dietro ogni punto. Il confronto onesto con l'esportazione di stampa del
  browser stesso, che vince sul testo selezionabile, è nella
  <a href="/how-to/save-a-webpage-as-pdf/">guida generale</a>. Entrambi sono linkati qui
  invece che ripetuti.
</p>

<h2>4. Dati di citazione: sul foglio, nel file, nel gestore di riferimenti</h2>
<p>
  Una cattura legge i metadati bibliografici che la pagina stessa dichiara e li depone in
  tre luoghi. Sul foglio: autori, rivista, DOI, licenza e momento della consultazione. Nel
  file: le proprietà del documento, un flusso XMP con Dublin Core e PRISM — i vocabolari
  che i gestori di riferimenti leggono — e altri dodici campi nel dizionario informativo
  del documento. E come record: un allegato <code>quelle.ris</code> dentro il PDF, più un
  file <code>.ris</code> separato accanto, che Citavi, Zotero ed EndNote importano
  direttamente. Il file separato è una comodità e si può disattivare nelle impostazioni;
  il record incorporato viaggia sempre con il PDF.
</p>
<p>
  Dal 7 agosto 2026 anche il nome del file porta la fonte: il modello predefinito è
  <code>{title}_{site}_{date}_{time}</code>, con il titolo preso dai metadati dell'editore
  invece che dal titolo della finestra — una cartella di catture si legge allora come una
  bibliografia anziché come un elenco di indirizzi.
</p>
<p>
  Il limite onesto: l'estensione legge ciò che la pagina aperta dichiara e non interroga
  alcun servizio di citazione. Una pagina povera non può dichiarare ciò che non ha mai
  dichiarato — su 20 fonti di una vera lista di lettura (misurato il 4 agosto 2026), 6 sono
  tornate senza record.
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">Dati
  grezzi</a>. Come il lettore si confronta con Citoid, il servizio di citazione di
  Wikimedia, è misurato alla pagina <a href="/measurements/citation-extraction/">estrazione
  delle citazioni</a>.
</p>

<h2>5. Impostazioni che contano nel lavoro di ricerca</h2>
<ul>
  <li><strong>Scala di risoluzione</strong> da 1.0x a 2.0x (predefinita 1.5x sul desktop,
      1.0x su Android). In pratica: alzatela per il testo piccolo e le figure, abbassatela
      quando conta la dimensione del file. Se il PDF è destinato all'OCR o a un modello
      linguistico, la soglia sotto la quale il riconoscimento crolla è misurata, non
      indovinata: <a href="/measurements/webpage-to-pdf-for-ocr/">pagina web in PDF per
      l'OCR</a>.</li>
  <li><strong>Un foglio o A4.</strong> Il predefinito è una pagina continua, senza cuciture
      in cui una macchina possa inciampare. Quando la meta è la carta stampata,
      l'impostazione A4 impagina con tagli che cadono tra le righe invece di attraversarle.</li>
  <li><strong>L'interruttore del consenso.</strong> I banner di consenso spesso bloccano lo
      scorrimento; l'interruttore nel popup li nasconde per la durata della cattura e li
      ripristina dopo. Nulla viene cliccato via in vostro nome — nascondere non è
      decidere.</li>
  <li><strong>L'ancora temporale.</strong> Dal 5 agosto 2026 una cattura può marcarsi con
      un'ora «non prima di» presa dal beacon pubblico drand — disattivata di default, perché
      è l'unica richiesta di rete dell'estensione. Ancora che la cattura non è più vecchia
      del round del beacon; non dice nulla su ciò che la pagina mostrava, e non è una marca
      temporale qualificata in senso giuridico.</li>
</ul>

<h2>6. Cosa è cambiato con la versione attuale</h2>
<p>
  La versione 2.33.4, presente in entrambi gli store quando questo testo è stato scritto
  (15 agosto 2026), ha portato in primo piano il flusso di lavoro accademico. Dal
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">registro
  delle modifiche</a>:
</p>
<ul>
  <li>I metadati di citazione ora vivono nel PDF stesso — XMP con Dublin Core e PRISM,
      dodici campi informativi del documento —, non solo nel record RIS (7 agosto 2026).
      Licenza, tipo di opera, versione e data di modifica sono arrivati il 10 agosto, così
      come l'output RIS nella versione per Chrome.</li>
  <li>Il record RIS è sempre incorporato nel PDF come <code>quelle.ris</code>; il file
      separato accanto si può disattivare (10 agosto 2026).</li>
  <li>I record senza autore ora iniziano con il titolo, come richiedono gli stili di
      citazione, invece che con un nudo «(s. d.).»; un nome di rivista duplicato come
      editore non viene più scritto due volte (10 agosto 2026).</li>
  <li>Su Android la cattura si scarica direttamente nella scheda in cui vi trovate — una
      notifica, nessuna scheda extra. I file di accompagnamento (record RIS, mappa dei link,
      file dell'editore) ora esistono solo sul desktop; sul telefono il loro contenuto vive
      dentro il PDF (7 agosto 2026).</li>
  <li>I nomi dei file portano il titolo della pagina preso dai metadati dell'editore
      (7 agosto 2026).</li>
</ul>

<h2>Cosa non fa</h2>
<ul>
  <li>Sul telefono funziona solo Firefox; Chrome per Android non installa estensioni.</li>
  <li>Il pacchetto indipendente dallo store sulla pagina dei rilasci era più vecchio di
      entrambi gli store al momento della verifica (2.27.0 contro 2.33.4, 15 agosto 2026) e
      non si aggiorna da solo.</li>
  <li>Sei fonti su venti misurate sono tornate senza record di citazione. Ciò che una pagina
      non dichiara, la cattura non può saperlo.</li>
  <li>L'ancora temporale non è una marca temporale qualificata, e nessun timbro dice nulla
      sul fatto che la pagina mostrasse ciò che mostrava.</li>
  <li>Catturate solo ciò a cui avete accesso legittimo. L'estensione raggiunge esattamente
      ciò che il vostro browser già vi mostra — e una cattura è documentazione, non una
      prova legalmente certificata.</li>
</ul>

<p class="note">
  Trasparenza: l'estensione descritta qui è la nostra. Le versioni degli store sono state
  lette dalle schede pubbliche il 15 agosto 2026 e cambiano a ogni rilascio; lo stato attuale
  leggibile dalle macchine è linkato sopra. Le misurazioni sono citate con le loro date e i
  dati grezzi. Le correzioni sono benvenute tramite una
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">segnalazione</a>.
</p>
""",
}

# ----------------------------------------------------------------- 日本語 ----
TEXTE["ja"] = {
    "title": "Firefox と Chrome で使う Full Page PDF Snap：インストールと研究ワークフロー",
    "description": (
        "Firefox（デスクトップと Android）と Chrome へのインストール方法、そして研究での"
        "使い方：ページ全体か表示領域か、Citavi・Zotero・EndNote 向け RIS レコード付きの"
        "書誌データ、解像度スケーリング、A4 設定、同意バナーのスイッチ——そしてバージョン"
        " 2.33.4 で変わったこと。ストアの版は 2026年8月15日に確認。"
    ),
    "h1": "Firefox と Chrome で使う Full Page PDF Snap：インストールと研究ワークフロー",
    "standfirst": (
        "これは研究者と学生のための実践ガイドです。拡張機能を Firefox（Android 版を含む）"
        "と Chrome に入れる方法、そしてキャプチャが情報源を研究のワークフローに沿って運ぶ"
        "仕組み——ページ全体と表示領域の選び方から、文献管理ソフトが読み込む RIS レコード"
        "まで。ストアの版は 2026年8月15日に確認し、その日付とともに記しています。"
    ),
    "meta": "2026年8月15日 · ストアの版は当日確認",
    "body": """
<h2>1. Firefox：デスクトップも Android も同じページから</h2>
<p>
  デスクトップでは
  <a href="https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/">Firefox
  Add-ons のページ</a>からインストールします。ワンクリックで、ファイルは Mozilla の署名
  付きで、拡張機能はそこから自動更新されます。執筆時点でこのページの版は 2.33.4 でした
  （2026年8月15日確認）。Firefox 109 以降が必要です。
</p>
<p>
  スマートフォンでは、同じページが <strong>Android 版 Firefox</strong>（バージョン 127
  以降）に対応します。ブラウザ自身のアドオンメニューからインストールし、ページ上で
  メニューを開いて拡張機能をタップすれば、デスクトップに出るポップアップなしでキャプ
  チャがすぐ始まります。完了は通知が1件届くだけで、それをタップするとファイルが開き、
  あとはシステムの共有メニューが引き継ぎます。
</p>
<p>
  スマートフォンでは Firefox が唯一の道です。Android 版 Chrome は拡張機能を一切インス
  トールできないからです。ストアを使いたくない場合は、
  <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">リリースページ</a>
  に同じ署名付きファイルがあります——ただし正直な注意点が2つあります。確認時点
  （2026年8月15日）でそこにある最新パッケージは 2.27.0 で両ストアより古く、この方法で
  入れた拡張機能は自動更新されません。現在どのストアがどの版を配布しているかは、
  <a href="/.well-known/extension-versions.json">/.well-known/extension-versions.json</a>
  で機械可読な形で公開しています。
</p>

<h2>2. Chrome、Edge、Brave、Vivaldi</h2>
<p>
  Chrome では
  <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">Chrome
  ウェブストアのページ</a>からインストールします。こちらも確認時点で 2.33.4（2026年
  8月15日）、Chrome 116 以降が必要で、ストアから自動更新されます。Brave と Vivaldi は
  そのまま Chrome ウェブストアから入ります。Edge は他ストアからの拡張機能を許可するか
  一度だけ尋ね、Opera は先に <em>Install Chrome Extensions</em> アドオンが必要です。
</p>
<p>
  両方のビルドは1つのソースから出ているので、キャプチャも PDF も RIS レコードも同じ
  です。違うのは周りのプラットフォームだけです。デスクトップで最速なのはキーボードで
  す：<code>Alt+Shift+Y</code>。ツールバーアイコンの右クリックには、スケーリング、
  ダウンロード先フォルダ、バナー処理のクイックスイッチがあります。
</p>

<h2>3. ページ全体か、見えている部分だけか</h2>
<p>
  ポップアップには2つのキャプチャがあります。<strong>ページ全体</strong>は文書を上から
  下までスクロールし、すべての区画を継ぎ目のない1枚につなぎます——引用するものには
  こちらが正解です。<strong>表示領域のみ</strong>（2つ目のボタン）は、画面に見えて
  いるものをそのまま、同じ書誌データ付きの同種の PDF として書き出します——長いスレッ
  ドの中の1つの投稿だけが重要な場合や、スクロールするたび伸び続けてキャプチャすべき
  下端がないページには、こちらが正解です。
</p>
<p>
  そもそもなぜやる価値があるのか——消える情報源、手で写す引用、機械に読めないファイル
  ——は、各論点に測定を添えた
  <a href="/how-to/for-students/">学生向けの姉妹記事</a>のテーマです。選択可能なテキス
  トではブラウザ自身の印刷エクスポートが勝るという正直な比較は、
  <a href="/how-to/save-a-webpage-as-pdf/">一般ガイド</a>にあります。どちらもここでは
  繰り返さずリンクします。
</p>

<h2>4. 書誌データ：紙面に、ファイルに、文献管理ソフトへ</h2>
<p>
  キャプチャはページ自身が宣言する書誌メタデータを読み取り、3か所に置きます。紙面に
  は：著者、ジャーナル、DOI、ライセンス、取得日時。ファイルには：文書プロパティ、
  Dublin Core と PRISM——文献管理ソフトが読む語彙——を含む XMP ストリーム、そして文書
  情報辞書の12の追加フィールド。レコードとしては：PDF 内の添付ファイル
  <code>quelle.ris</code> と、その隣に置かれる別ファイルの <code>.ris</code> で、
  Citavi、Zotero、EndNote がそのまま読み込めます。別ファイルは便宜上のもので設定で
  切れますが、埋め込まれたレコードは常に PDF と一緒に移動します。
</p>
<p>
  2026年8月7日以降、ファイル名にも出典が入ります。既定のテンプレートは
  <code>{title}_{site}_{date}_{time}</code> で、タイトルはウィンドウタイトルではなく
  出版者のメタデータから取られます——キャプチャのフォルダが、アドレスの一覧ではなく
  参考文献リストのように読めるようになります。
</p>
<p>
  正直な限界もあります。拡張機能は開いているページが宣言するものを読むだけで、引用
  サービスには問い合わせません。情報の薄いページに、宣言していないことを宣言させる
  ことはできません——実際の読書リストの20の情報源（2026年8月4日測定）のうち6件は
  レコードなしで返ってきました。
  <a href="/data/2026-08-04-reading-list-to-bibliography-nach-ableitung.json">生データ</a>。
  このリーダーが Wikimedia の引用サービス Citoid と比べてどうかは、
  <a href="/measurements/citation-extraction/">引用抽出の測定</a>にあります。
</p>

<h2>5. 研究作業で意味を持つ設定</h2>
<ul>
  <li><strong>解像度スケーリング</strong>は 1.0x から 2.0x（既定はデスクトップ 1.5x、
      Android 1.0x）。実務では、細かい文字や図では上げ、ファイルサイズが重要なら下げ
      ます。PDF を OCR や言語モデルに渡すなら、認識が崩れる閾値は推測ではなく測定済み
      です：<a href="/measurements/webpage-to-pdf-for-ocr/">OCR 用のウェブページ PDF 化</a>。</li>
  <li><strong>1枚か A4 か。</strong>既定は継ぎ目のない連続した1ページ——機械がつまずく
      継ぎ目がありません。印刷した紙が目的なら、A4 設定は行を切り裂くのではなく行間に
      改ページが落ちるようにページ分割します。</li>
  <li><strong>同意バナーのスイッチ。</strong>同意バナーはしばしばスクロールを固定します。
      ポップアップのスイッチはキャプチャの間だけバナーを隠し、終わったら元に戻します。
      あなたの名前で何かがクリックされることはありません——隠すことは決めることでは
      ありません。</li>
  <li><strong>時刻アンカー。</strong>2026年8月5日以降、キャプチャは公開 drand ビーコン
      から取った「この時刻より前ではない」時刻で自分に印を押せます——既定はオフです。
      拡張機能唯一のネットワーク要求だからです。これはキャプチャがビーコンのラウンド
      より古くないことを固定します。ページが何を表示していたかについては何も言わず、
      法的意味での認定タイムスタンプでもありません。</li>
</ul>

<h2>6. 現行バージョンで変わったこと</h2>
<p>
  執筆時点で両ストアにあったバージョン 2.33.4（2026年8月15日）は、研究のワークフロー
  を前面に押し出しました。
  <a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/CHANGELOG.md">変更履歴</a>
  から：
</p>
<ul>
  <li>書誌メタデータが RIS レコードだけでなく PDF 自身に入るようになりました——Dublin
      Core と PRISM の XMP、文書情報の12フィールド（2026年8月7日）。ライセンス、作品
      種別、版、変更日は8月10日に続き、Chrome 版の RIS 出力も同日でした。</li>
  <li>RIS レコードは常に <code>quelle.ris</code> として PDF に埋め込まれ、隣に置かれる
      別ファイルは切れるようになりました（2026年8月10日）。</li>
  <li>著者のいないレコードは、引用スタイルの求める通りタイトルで始まるようになりまし
      た。素っ気ない「(n. d.).」ではなく。出版社名として重複したジャーナル名が二度
      書かれることもなくなりました（2026年8月10日）。</li>
  <li>Android ではキャプチャが今いるタブで直接ダウンロードされます——通知は1件、余計
      なタブはなし。付属ファイル（RIS レコード、リンクマップ、出版社ファイル）は
      デスクトップ専用になり、スマホではその内容は PDF の中に入っています（2026年
      8月7日）。</li>
  <li>ファイル名が出版者メタデータのページタイトルを担うようになりました（2026年
      8月7日）。</li>
</ul>

<h2>できないこと</h2>
<ul>
  <li>スマートフォンで動くのは Firefox だけです。Android 版 Chrome は拡張機能を
      インストールできません。</li>
  <li>リリースページのストア非依存パッケージは、確認時点で両ストアより古いものでした
      （2.27.0 対 2.33.4、2026年8月15日）。自動更新もされません。</li>
  <li>測定した20の情報源のうち6件は引用レコードなしで返ってきました。ページが宣言して
      いないことを、キャプチャが知る術はありません。</li>
  <li>時刻アンカーは認定タイムスタンプではなく、どんな印も「ページが表示していたものが
      正しかったか」については何も言いません。</li>
  <li>正当なアクセス権のあるものだけをキャプチャしてください。拡張機能が届くのは、
      ブラウザがすでにあなたに見せているものまでです——そしてキャプチャは記録であって、
      法的に認証された証明ではありません。</li>
</ul>

<p class="note">
  開示：ここで説明した拡張機能は私たち自身のものです。ストアの版は2026年8月15日に公開
  ページから読み取ったもので、リリースごとに変わります。機械可読な現在の状態は上に
  リンクしています。測定は日付と生データ付きで引用しています。訂正は
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">Issue</a>
  で受け付けています。
</p>
""",
}
