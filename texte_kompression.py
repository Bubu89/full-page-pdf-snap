#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/notes/smaller-files-better-ocr/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, woertlich uebernommen — nicht
build-kompression-teaser.py: der Builder wuerde 33 Woerter loeschen
(tools/builder-drift.py). Englisch ist die Basis, alle anderen Fassungen
uebersetzen sie.

Unveraendert in jeder Sprache: Zahlen, Masseinheiten, Versionsnummern,
Dateiformate (FlateDecode, DCTDecode, JBIG2, MRC, WebP, AVIF, RIS), Werkzeug-
und Funktionsnamen (Tesseract, recommend_settings) sowie alle Adressen. Eine
uebersetzte Zahl waere eine andere Messung.

Rendern:  python3 tools/seite-neunsprachig.py texte_kompression.py
"""

URL = "https://provinglab.dev/notes/smaller-files-better-ocr/"
ZIEL = "notes/smaller-files-better-ocr/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# Bausteine, die in jeder Sprache gleich bleiben. Sie hier zu halten spart
# neunfaches Abschreiben und schliesst aus, dass eine Zahl in einer Sprache
# abweicht.
_META = ('<a href="/data/2026-08-04-kompression-aufnahme.json">')
_ISSUE = ('<a href="https://github.com/Bubu89/full-page-pdf-snap/issues/19">'
          'issue 19</a>')
_MCP = '<a href="/mcp">'
_ZURUECK = '<a href="../../">'
_DISCLAIMER = '<a href="../../disclaimer/">'


def _tabelle(caption, th_mode, th_file, th_share, th_words,
             r_colour, r_grey, r_bw):
    """Die Messtabelle. Zahlen stehen nur hier — in allen Sprachen dieselben."""
    return f'''<table>
  <caption>{caption}</caption>
  <thead><tr><th scope="col">{th_mode}</th><th scope="col">{th_file}</th>
    <th scope="col">{th_share}</th><th scope="col">{th_words}</th></tr></thead>
  <tbody>
    <tr><th scope="row">{r_colour}</th><td class="num">416 kB</td>
        <td class="num">100 %</td><td class="num">987</td></tr>
    <tr><th scope="row">{r_grey}</th><td class="num">243 kB</td>
        <td class="num">58 %</td><td class="num">989</td></tr>
    <tr><th scope="row">{r_bw}</th><td class="num"><strong>113 kB</strong></td>
        <td class="num"><strong>27 %</strong></td><td class="num">989</td></tr>
  </tbody>
</table>'''


def _seite(h1, standfirst, gemessen, rohdaten, tabelle, absaetze,
           h2_1, h2_2, h2_3, h2_4, fuss, korrekturen, disclaimer_text):
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{gemessen} ·
    {_META}{rohdaten}</a></p>
</header>

<h2>{h2_1}</h2>
{tabelle}
<p>
  {absaetze[0]}
</p>

<h2>{h2_2}</h2>
<p>
  {absaetze[1]}
</p>

<h2>{h2_3}</h2>
<p>
  {absaetze[2]}
</p>
<p>
  {absaetze[3]}
</p>

<h2>{h2_4}</h2>
<p>
  {absaetze[4]}
</p>
<p>
  {absaetze[5]}
</p>

<p>
  {absaetze[6]}
</p>

<footer>
      {fuss}
      <br><br>
      {korrekturen}
      {_ISSUE}.
      <br><br>
      {_ZURUECK}← Proving Lab</a> · {_DISCLAIMER}{disclaimer_text}</a>
    </footer>'''


INHALT = {}

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="A capture at 8.5 % of the size, and OCR reads it slightly better",
    standfirst=(
        "Our own measurement had the capture at 6.7 MB against 1.1 MB for the "
        "browser's print export — noted on the comparison page and left there "
        "without comment. Looking into it turned up something better than a "
        "compression setting: for a page of text, dropping the colour costs "
        "nothing that matters and saves almost everything."),
    gemessen="Measured 2026-08-04",
    rohdaten="raw data",
    tabelle=_tabelle(
        "1400 × 3200 px, lossless compression, OCR with Tesseract 5.3.4",
        "Mode", "File", "Share", "Words read back",
        "Full colour", "Greyscale", "Black and white"),
    h2_1="One page of text, three colour depths",
    h2_2="Why it will not be the default",
    h2_3="What is built, and what is not",
    h2_4="What was checked and rejected",
    absaetze=[
        ("Against the 1327 kB the current build produces as JPEG, the last row "
         "is <strong>8.5 %</strong>. And the text recognition does not suffer "
         "— it reads back <em>two words more</em> than from the colour "
         "version, at 99.9 % agreement. That is not a coincidence: OCR "
         "binarises the image anyway. Handing it colour means handing it work "
         "it immediately throws away."),
        ("The same setting on a page of photographs produces a structural "
         "similarity of <strong>0.199</strong> — the image is gone. No single "
         "value is right for both, which is why this belongs in the hands of "
         "whoever knows what they are capturing. A statute, a repository "
         "record, a page of tables: black and white. A figure, a map, a "
         "photograph: colour."),
        ("The setting exists in <strong>2.28.0</strong>, in both branches, and "
         "both browsers load that build. Alongside it the capture stopped "
         "always embedding JPEG: each tile is now compared and the smaller of "
         "lossless <code>FlateDecode</code> and <code>DCTDecode</code> is used."),
        ("<strong>It is not in either store yet.</strong> What is measured is "
         "the encoding and the recognition; what is not measured is a full "
         "capture in a real browser, because that needs a genuine input event "
         "the test setup cannot produce. No date is promised here — the stores "
         "currently serve 2.26.0 and 2.17.0, and this site does not make "
         "claims about when that changes."),
        ("MRC, the standard behind small scanned PDFs, reaches a factor of "
         "eight to ten. It relies on JBIG2, which replaces similar glyphs with "
         "one shared pattern and has documented digit substitution. For a tool "
         "whose output is meant to serve as evidence, a file in which a year "
         "could quietly change is worth nothing — the saving does not enter "
         "into it. WebP and AVIF are not part of PDF at all."),
        ("The source details are untouched by any of this. Text layer, "
         "metadata and image are separate objects in the file; the RIS record "
         "and the checksum sit beside it. Changing how the image is stored "
         "does not change what the capture says about where it came from."),
        ("<strong>Which setting for which purpose:</strong> "
         "<code>recommend_settings</code> on " + _MCP + "the endpoint</a> "
         "answers by purpose — citation, figure, archive or ocr — and carries "
         "the measurement behind each value, or an explicit note that none "
         "exists."),
    ],
    fuss=("Method: two synthetic pages at 1400 × 3200 px, one text-heavy and "
          "one image-heavy, each encoded at three colour depths and compressed "
          "losslessly. OCR with Tesseract 5.3.4, German model, output compared "
          "to the colour run by sequence similarity. The structural comparison "
          "used here works on luminance and therefore does not see colour loss "
          "— greyscale scores 1.000 despite having none. Synthetic pages, so "
          "the order of magnitude holds and the individual figures do not. "
          "Nothing here is legal advice."),
    korrekturen="Corrections are welcome and are made in public:",
    disclaimer_text="Disclaimer",
)

# -------------------------------------------------------------------- Deutsch
INHALT["de"] = _seite(
    h1="Eine Aufnahme mit 8,5 % der Größe — und die Texterkennung liest sie etwas besser",
    standfirst=(
        "Die eigene Messung hatte die Aufnahme bei 6,7 MB gegen 1,1 MB für den "
        "Druckexport des Browsers — auf der Vergleichsseite vermerkt und dort "
        "unkommentiert stehen geblieben. Beim Nachgehen kam etwas Besseres "
        "heraus als eine Kompressionseinstellung: Bei einer Textseite kostet "
        "der Verzicht auf Farbe nichts, worauf es ankommt, und spart fast "
        "alles."),
    gemessen="Gemessen am 04.08.2026",
    rohdaten="Rohdaten",
    tabelle=_tabelle(
        "1400 × 3200 px, verlustfreie Kompression, OCR mit Tesseract 5.3.4",
        "Modus", "Datei", "Anteil", "Zurückgelesene Wörter",
        "Vollfarbe", "Graustufen", "Schwarzweiß"),
    h2_1="Eine Textseite, drei Farbtiefen",
    h2_2="Warum es nicht die Voreinstellung wird",
    h2_3="Was gebaut ist und was nicht",
    h2_4="Was geprüft und verworfen wurde",
    absaetze=[
        ("Gegen die 1327 kB, die der aktuelle Bau als JPEG erzeugt, sind es in "
         "der letzten Zeile <strong>8,5 %</strong>. Und die Texterkennung "
         "leidet nicht — sie liest <em>zwei Wörter mehr</em> zurück als aus "
         "der Farbfassung, bei 99,9 % Übereinstimmung. Das ist kein Zufall: "
         "OCR binarisiert das Bild ohnehin. Ihm Farbe zu geben heißt, ihm "
         "Arbeit zu geben, die es sofort wegwirft."),
        ("Dieselbe Einstellung auf einer Fotoseite ergibt eine strukturelle "
         "Ähnlichkeit von <strong>0,199</strong> — das Bild ist weg. Kein "
         "einzelner Wert passt für beides, und darum gehört das in die Hand "
         "dessen, der weiß, was er aufnimmt. Ein Gesetzestext, ein "
         "Repositoriums-Eintrag, eine Tabellenseite: Schwarzweiß. Eine "
         "Abbildung, eine Karte, ein Foto: Farbe."),
        ("Die Einstellung gibt es in <strong>2.28.0</strong>, in beiden "
         "Zweigen, und beide Browser laden diesen Bau. Daneben bettet die "
         "Aufnahme nicht mehr immer JPEG ein: Jede Kachel wird jetzt "
         "verglichen, und es wird die kleinere von verlustfreiem "
         "<code>FlateDecode</code> und <code>DCTDecode</code> genommen."),
        ("<strong>In keinem der beiden Stores ist es bisher.</strong> "
         "Gemessen sind die Kodierung und die Erkennung; nicht gemessen ist "
         "eine vollständige Aufnahme in einem echten Browser, denn dafür "
         "braucht es ein echtes Eingabeereignis, das der Prüfaufbau nicht "
         "erzeugen kann. Ein Datum wird hier nicht versprochen — die Stores "
         "liefern derzeit 2.26.0 und 2.17.0 aus, und diese Seite behauptet "
         "nicht, wann sich das ändert."),
        ("MRC, der Standard hinter kleinen gescannten PDFs, erreicht Faktor "
         "acht bis zehn. Es beruht auf JBIG2, das ähnliche Zeichen durch ein "
         "gemeinsames Muster ersetzt und dokumentierte Ziffernverwechslungen "
         "hat. Für ein Werkzeug, dessen Ausgabe als Beleg dienen soll, ist "
         "eine Datei, in der sich eine Jahreszahl still ändern kann, nichts "
         "wert — die Ersparnis spielt dabei keine Rolle. WebP und AVIF sind "
         "gar nicht Teil von PDF."),
        ("Die Herkunftsangaben bleiben von alldem unberührt. Textebene, "
         "Metadaten und Bild sind getrennte Objekte in der Datei; der "
         "RIS-Datensatz und die Prüfsumme liegen daneben. Zu ändern, wie das "
         "Bild gespeichert wird, ändert nicht, was die Aufnahme über ihre "
         "Herkunft sagt."),
        ("<strong>Welche Einstellung wofür:</strong> "
         "<code>recommend_settings</code> an " + _MCP + "der Schnittstelle</a> "
         "antwortet nach Zweck — Zitat, Abbildung, Archiv oder OCR — und trägt "
         "die Messung hinter jedem Wert mit sich, oder den ausdrücklichen "
         "Hinweis, dass es keine gibt."),
    ],
    fuss=("Methode: zwei synthetische Seiten mit 1400 × 3200 px, eine "
          "textlastig und eine bildlastig, jeweils in drei Farbtiefen kodiert "
          "und verlustfrei komprimiert. OCR mit Tesseract 5.3.4, deutsches "
          "Modell, Ausgabe über Sequenzähnlichkeit mit dem Farblauf "
          "verglichen. Der hier verwendete strukturelle Vergleich arbeitet auf "
          "der Helligkeit und sieht Farbverlust deshalb nicht — Graustufen "
          "erreichen 1,000, obwohl sie keine Farbe haben. Synthetische Seiten: "
          "die Größenordnung hält, die Einzelwerte nicht. Nichts hiervon ist "
          "eine Rechtsberatung."),
    korrekturen="Korrekturen sind willkommen und werden öffentlich vorgenommen:",
    disclaimer_text="Haftungsausschluss",
)

# -------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Una captura al 8,5 % del tamaño, y el OCR la lee algo mejor",
    standfirst=(
        "Nuestra propia medición situaba la captura en 6,7 MB frente a 1,1 MB "
        "de la exportación de impresión del navegador — anotado en la página "
        "de comparación y dejado allí sin comentario. Al investigarlo apareció "
        "algo mejor que un ajuste de compresión: en una página de texto, "
        "renunciar al color no cuesta nada que importe y ahorra casi todo."),
    gemessen="Medido el 2026-08-04",
    rohdaten="datos brutos",
    tabelle=_tabelle(
        "1400 × 3200 px, compresión sin pérdida, OCR con Tesseract 5.3.4",
        "Modo", "Archivo", "Proporción", "Palabras releídas",
        "Color completo", "Escala de grises", "Blanco y negro"),
    h2_1="Una página de texto, tres profundidades de color",
    h2_2="Por qué no será el ajuste predeterminado",
    h2_3="Qué está construido y qué no",
    h2_4="Qué se comprobó y se descartó",
    absaetze=[
        ("Frente a los 1327 kB que la compilación actual produce como JPEG, la "
         "última fila es el <strong>8,5 %</strong>. Y el reconocimiento de "
         "texto no se resiente: relee <em>dos palabras más</em> que en la "
         "versión en color, con un 99,9 % de coincidencia. No es casualidad: "
         "el OCR binariza la imagen de todos modos. Darle color es darle "
         "trabajo que descarta de inmediato."),
        ("El mismo ajuste en una página de fotografías da una similitud "
         "estructural de <strong>0,199</strong> — la imagen desaparece. Ningún "
         "valor único sirve para ambos casos, y por eso esto corresponde a "
         "quien sabe qué está capturando. Una ley, un registro de repositorio, "
         "una página de tablas: blanco y negro. Una figura, un mapa, una "
         "fotografía: color."),
        ("El ajuste existe en la <strong>2.28.0</strong>, en ambas ramas, y "
         "los dos navegadores cargan esa compilación. Junto a ello, la captura "
         "dejó de incrustar siempre JPEG: ahora se compara cada mosaico y se "
         "usa el menor entre <code>FlateDecode</code> sin pérdida y "
         "<code>DCTDecode</code>."),
        ("<strong>Todavía no está en ninguna de las dos tiendas.</strong> Lo "
         "medido es la codificación y el reconocimiento; lo no medido es una "
         "captura completa en un navegador real, porque eso exige un evento de "
         "entrada genuino que el montaje de prueba no puede producir. Aquí no "
         "se promete ninguna fecha: las tiendas sirven actualmente 2.26.0 y "
         "2.17.0, y este sitio no afirma cuándo cambiará eso."),
        ("MRC, el estándar detrás de los PDF escaneados pequeños, alcanza un "
         "factor de ocho a diez. Se apoya en JBIG2, que sustituye glifos "
         "parecidos por un patrón común y tiene sustituciones de dígitos "
         "documentadas. Para una herramienta cuya salida debe servir como "
         "prueba, un archivo en el que un año podría cambiar en silencio no "
         "vale nada — el ahorro no entra en la cuenta. WebP y AVIF ni siquiera "
         "forman parte de PDF."),
        ("Los datos de procedencia quedan intactos en todo esto. Capa de "
         "texto, metadatos e imagen son objetos separados dentro del archivo; "
         "el registro RIS y la suma de verificación están al lado. Cambiar "
         "cómo se almacena la imagen no cambia lo que la captura dice sobre su "
         "origen."),
        ("<strong>Qué ajuste para qué fin:</strong> "
         "<code>recommend_settings</code> en " + _MCP + "el endpoint</a> "
         "responde por propósito — cita, figura, archivo u ocr — y lleva "
         "consigo la medición que respalda cada valor, o la indicación "
         "explícita de que no existe ninguna."),
    ],
    fuss=("Método: dos páginas sintéticas de 1400 × 3200 px, una con mucho "
          "texto y otra con mucha imagen, codificadas cada una en tres "
          "profundidades de color y comprimidas sin pérdida. OCR con Tesseract "
          "5.3.4, modelo alemán, salida comparada con la ejecución en color "
          "por similitud de secuencia. La comparación estructural empleada "
          "trabaja sobre la luminancia y por tanto no ve la pérdida de color "
          "— la escala de grises puntúa 1,000 pese a no tener ninguno. Páginas "
          "sintéticas: se sostiene el orden de magnitud, no las cifras "
          "individuales. Nada de esto es asesoramiento jurídico."),
    korrekturen="Las correcciones son bienvenidas y se hacen en público:",
    disclaimer_text="Aviso legal",
)

# -------------------------------------------------------------------- Français
INHALT["fr"] = _seite(
    h1="Une capture à 8,5 % de la taille, et l’OCR la lit un peu mieux",
    standfirst=(
        "Notre propre mesure donnait la capture à 6,7 Mo contre 1,1 Mo pour "
        "l’export d’impression du navigateur — noté sur la page de comparaison "
        "et laissé là sans commentaire. En y regardant de plus près, il est "
        "ressorti mieux qu’un réglage de compression : pour une page de texte, "
        "renoncer à la couleur ne coûte rien qui compte et fait presque tout "
        "gagner."),
    gemessen="Mesuré le 2026-08-04",
    rohdaten="données brutes",
    tabelle=_tabelle(
        "1400 × 3200 px, compression sans perte, OCR avec Tesseract 5.3.4",
        "Mode", "Fichier", "Part", "Mots relus",
        "Couleur", "Niveaux de gris", "Noir et blanc"),
    h2_1="Une page de texte, trois profondeurs de couleur",
    h2_2="Pourquoi ce ne sera pas le réglage par défaut",
    h2_3="Ce qui est construit, et ce qui ne l’est pas",
    h2_4="Ce qui a été examiné et écarté",
    absaetze=[
        ("Face aux 1327 ko que la version actuelle produit en JPEG, la "
         "dernière ligne représente <strong>8,5 %</strong>. Et la "
         "reconnaissance de texte n’en souffre pas : elle relit <em>deux mots "
         "de plus</em> que sur la version en couleur, avec 99,9 % de "
         "concordance. Ce n’est pas un hasard : l’OCR binarise l’image de "
         "toute façon. Lui donner de la couleur, c’est lui donner un travail "
         "qu’il jette aussitôt."),
        ("Le même réglage sur une page de photographies donne une similarité "
         "structurelle de <strong>0,199</strong> — l’image a disparu. Aucune "
         "valeur unique ne convient aux deux, et c’est pourquoi cela revient à "
         "celui qui sait ce qu’il capture. Un texte de loi, une notice de "
         "dépôt, une page de tableaux : noir et blanc. Une figure, une carte, "
         "une photographie : couleur."),
        ("Le réglage existe en <strong>2.28.0</strong>, dans les deux "
         "branches, et les deux navigateurs chargent cette version. En même "
         "temps, la capture n’intègre plus systématiquement du JPEG : chaque "
         "tuile est désormais comparée et l’on retient le plus petit entre "
         "<code>FlateDecode</code> sans perte et <code>DCTDecode</code>."),
        ("<strong>Ce n’est encore dans aucune des deux boutiques.</strong> Ce "
         "qui est mesuré, c’est l’encodage et la reconnaissance ; ce qui ne "
         "l’est pas, c’est une capture complète dans un vrai navigateur, car "
         "cela demande un véritable événement d’entrée que le montage de test "
         "ne peut pas produire. Aucune date n’est promise ici — les boutiques "
         "servent actuellement 2.26.0 et 2.17.0, et ce site n’avance rien sur "
         "le moment où cela changera."),
        ("MRC, la norme derrière les PDF numérisés de petite taille, atteint "
         "un facteur de huit à dix. Elle repose sur JBIG2, qui remplace les "
         "glyphes semblables par un motif commun et présente des substitutions "
         "de chiffres documentées. Pour un outil dont la sortie doit servir de "
         "preuve, un fichier dans lequel une année pourrait changer en silence "
         "ne vaut rien — l’économie n’entre pas en ligne de compte. WebP et "
         "AVIF ne font pas du tout partie de PDF."),
        ("Les indications de provenance ne sont en rien touchées. Couche de "
         "texte, métadonnées et image sont des objets distincts dans le "
         "fichier ; la notice RIS et la somme de contrôle se trouvent à côté. "
         "Changer la manière dont l’image est stockée ne change pas ce que la "
         "capture dit de son origine."),
        ("<strong>Quel réglage pour quel usage :</strong> "
         "<code>recommend_settings</code> sur " + _MCP + "le point de "
         "terminaison</a> répond par finalité — citation, figure, archive ou "
         "ocr — et porte avec lui la mesure derrière chaque valeur, ou la "
         "mention explicite qu’il n’en existe aucune."),
    ],
    fuss=("Méthode : deux pages synthétiques de 1400 × 3200 px, l’une chargée "
          "en texte et l’autre en images, encodées chacune en trois "
          "profondeurs de couleur et compressées sans perte. OCR avec "
          "Tesseract 5.3.4, modèle allemand, sortie comparée à la version en "
          "couleur par similarité de séquence. La comparaison structurelle "
          "utilisée ici travaille sur la luminance et ne voit donc pas la "
          "perte de couleur — les niveaux de gris obtiennent 1,000 alors "
          "qu’ils n’en ont aucune. Pages synthétiques : l’ordre de grandeur "
          "tient, les valeurs individuelles non. Rien de tout cela n’est un "
          "conseil juridique."),
    korrekturen="Les corrections sont bienvenues et faites en public :",
    disclaimer_text="Avertissement",
)

# -------------------------------------------------------------------- Italiano
INHALT["it"] = _seite(
    h1="Una cattura all’8,5 % della dimensione, e l’OCR la legge un po’ meglio",
    standfirst=(
        "La nostra misurazione dava la cattura a 6,7 MB contro 1,1 MB "
        "dell’esportazione di stampa del browser — annotato nella pagina di "
        "confronto e lasciato lì senza commento. Approfondendo è emerso "
        "qualcosa di meglio di un’impostazione di compressione: per una pagina "
        "di testo, rinunciare al colore non costa nulla che conti e fa "
        "risparmiare quasi tutto."),
    gemessen="Misurato il 2026-08-04",
    rohdaten="dati grezzi",
    tabelle=_tabelle(
        "1400 × 3200 px, compressione senza perdita, OCR con Tesseract 5.3.4",
        "Modalità", "File", "Quota", "Parole rilette",
        "Colore pieno", "Scala di grigi", "Bianco e nero"),
    h2_1="Una pagina di testo, tre profondità di colore",
    h2_2="Perché non sarà l’impostazione predefinita",
    h2_3="Che cosa è realizzato e che cosa no",
    h2_4="Che cosa è stato valutato e scartato",
    absaetze=[
        ("Rispetto ai 1327 kB che la build attuale produce in JPEG, l’ultima "
         "riga è l’<strong>8,5 %</strong>. E il riconoscimento del testo non "
         "ne risente: rilegge <em>due parole in più</em> rispetto alla "
         "versione a colori, con il 99,9 % di concordanza. Non è un caso: "
         "l’OCR binarizza comunque l’immagine. Dargli il colore significa "
         "dargli un lavoro che scarta subito."),
        ("La stessa impostazione su una pagina di fotografie dà una "
         "somiglianza strutturale di <strong>0,199</strong> — l’immagine è "
         "sparita. Nessun valore singolo va bene per entrambi i casi, ed è per "
         "questo che la scelta spetta a chi sa che cosa sta catturando. Un "
         "testo di legge, una scheda di archivio, una pagina di tabelle: "
         "bianco e nero. Una figura, una mappa, una fotografia: colore."),
        ("L’impostazione esiste nella <strong>2.28.0</strong>, in entrambi i "
         "rami, ed entrambi i browser caricano quella build. Accanto a ciò, la "
         "cattura ha smesso di incorporare sempre JPEG: ogni tassello viene "
         "ora confrontato e si usa il minore tra <code>FlateDecode</code> "
         "senza perdita e <code>DCTDecode</code>."),
        ("<strong>Non è ancora in nessuno dei due store.</strong> Ciò che è "
         "misurato sono la codifica e il riconoscimento; ciò che non è "
         "misurato è una cattura completa in un browser reale, perché richiede "
         "un vero evento di input che l’ambiente di prova non può produrre. "
         "Qui non si promette alcuna data — gli store servono attualmente "
         "2.26.0 e 2.17.0, e questo sito non afferma quando ciò cambierà."),
        ("MRC, lo standard dietro i PDF scansionati di piccole dimensioni, "
         "raggiunge un fattore da otto a dieci. Si basa su JBIG2, che "
         "sostituisce glifi simili con un unico modello condiviso e presenta "
         "sostituzioni di cifre documentate. Per uno strumento il cui esito "
         "deve valere come prova, un file in cui un anno potrebbe cambiare in "
         "silenzio non vale nulla — il risparmio non entra nel conto. WebP e "
         "AVIF non fanno affatto parte del PDF."),
        ("I dati di provenienza restano del tutto intatti. Livello di testo, "
         "metadati e immagine sono oggetti distinti nel file; il record RIS e "
         "la somma di controllo stanno accanto. Cambiare il modo in cui "
         "l’immagine è memorizzata non cambia ciò che la cattura dice sulla "
         "propria origine."),
        ("<strong>Quale impostazione per quale scopo:</strong> "
         "<code>recommend_settings</code> sull’" + _MCP + "endpoint</a> "
         "risponde per finalità — citazione, figura, archivio od ocr — e porta "
         "con sé la misurazione dietro ogni valore, oppure l’indicazione "
         "esplicita che non ne esiste nessuna."),
    ],
    fuss=("Metodo: due pagine sintetiche da 1400 × 3200 px, una ricca di testo "
          "e una ricca di immagini, ciascuna codificata in tre profondità di "
          "colore e compressa senza perdita. OCR con Tesseract 5.3.4, modello "
          "tedesco, output confrontato con l’esecuzione a colori per "
          "somiglianza di sequenza. Il confronto strutturale qui usato lavora "
          "sulla luminanza e quindi non vede la perdita di colore — la scala "
          "di grigi ottiene 1,000 pur non avendone. Pagine sintetiche: tiene "
          "l’ordine di grandezza, non i singoli valori. Nulla di ciò "
          "costituisce consulenza legale."),
    korrekturen="Le correzioni sono benvenute e vengono fatte in pubblico:",
    disclaimer_text="Avvertenze",
)

# ------------------------------------------------------------------- 日本語
INHALT["ja"] = _seite(
    h1="サイズは 8.5 %、しかも OCR はわずかに読みやすくなる",
    standfirst=(
        "自分たちの計測では、キャプチャが 6.7 MB、ブラウザーの印刷書き出しが "
        "1.1 MB だった。比較ページに記したまま、注釈もつけずに置いてあった。"
        "調べてみると、圧縮設定より良いものが出てきた。テキストのページなら、"
        "色を捨てても大事なものは何も失われず、ほとんどすべてが節約できる。"),
    gemessen="計測日 2026-08-04",
    rohdaten="生データ",
    tabelle=_tabelle(
        "1400 × 3200 px、可逆圧縮、OCR は Tesseract 5.3.4",
        "モード", "ファイル", "割合", "読み戻せた語数",
        "フルカラー", "グレースケール", "白黒"),
    h2_1="1 ページのテキスト、3 つの色深度",
    h2_2="なぜ既定値にはしないのか",
    h2_3="実装済みのものと、そうでないもの",
    h2_4="検討して見送ったもの",
    absaetze=[
        ("現行ビルドが JPEG として生成する 1327 kB に対し、最終行は "
         "<strong>8.5 %</strong> である。しかも文字認識は劣化しない。カラー版より "
         "<em>2 語多く</em> 読み戻し、一致率は 99.9 % だった。偶然ではない。OCR は"
         "どのみち画像を二値化する。色を渡すことは、すぐ捨てられる仕事を渡すことに"
         "等しい。"),
        ("同じ設定を写真のページに使うと、構造的類似度は <strong>0.199</strong> "
         "になる。画像は失われている。どちらにも合う単一の値は存在しない。だから"
         "これは、何を取り込もうとしているかを知っている人の手に委ねられる。法令、"
         "リポジトリの書誌、表のページなら白黒。図、地図、写真ならカラー。"),
        ("この設定は <strong>2.28.0</strong> に、両方のブランチに存在し、"
         "両ブラウザーともそのビルドを読み込む。あわせて、キャプチャは常に JPEG を"
         "埋め込むのをやめた。各タイルを比較し、可逆の <code>FlateDecode</code> と "
         "<code>DCTDecode</code> のうち小さいほうを用いる。"),
        ("<strong>どちらのストアにもまだ出ていない。</strong>計測したのは符号化と"
         "認識であり、計測していないのは実際のブラウザーでの完全なキャプチャである。"
         "それには本物の入力イベントが要るが、試験環境では作れない。ここで期日は"
         "約束しない。ストアは現在 2.26.0 と 2.17.0 を配信しており、本サイトは"
         "それがいつ変わるかについて主張しない。"),
        ("小さなスキャン PDF の背後にある標準 MRC は 8〜10 倍に達する。これは "
         "JBIG2 に依存しており、似た字形をひとつの共通パターンに置き換えるため、"
         "数字の取り違えが文書化されている。出力が証拠として使われる道具にとって、"
         "年号が黙って変わりうるファイルには何の価値もない。節約は勘定に入らない。"
         "WebP と AVIF はそもそも PDF の一部ではない。"),
        ("出典の記載はこれらの影響を受けない。テキスト層、メタデータ、画像は"
         "ファイル内の別々のオブジェクトであり、RIS レコードとチェックサムは"
         "その傍らにある。画像の保存方法を変えても、そのキャプチャが自らの出所に"
         "ついて述べる内容は変わらない。"),
        ("<strong>用途ごとの設定:</strong> " + _MCP + "エンドポイント</a> の "
         "<code>recommend_settings</code> が用途別に答える — 引用、図版、保存、"
         "または ocr。各値の根拠となる計測を伴い、根拠がない場合はその旨を"
         "明示する。"),
    ],
    fuss=("方法: 1400 × 3200 px の合成ページ 2 枚。一方はテキスト中心、他方は"
          "画像中心。それぞれ 3 つの色深度で符号化し、可逆圧縮した。OCR は "
          "Tesseract 5.3.4、ドイツ語モデル。出力は系列類似度でカラー版と比較した。"
          "ここで用いた構造的比較は輝度を対象とするため色の損失を見ない — "
          "グレースケールは色がないのに 1.000 を示す。合成ページなので、"
          "桁は保たれるが個々の数値は保たれない。以上のいずれも法的助言ではない。"),
    korrekturen="訂正は歓迎され、公開の場で行われる:",
    disclaimer_text="免責事項",
)

# ---------------------------------------------------------------- Português BR
INHALT["pt-BR"] = _seite(
    h1="Uma captura com 8,5 % do tamanho, e o OCR a lê um pouco melhor",
    standfirst=(
        "Nossa própria medição colocava a captura em 6,7 MB contra 1,1 MB da "
        "exportação de impressão do navegador — anotado na página de "
        "comparação e deixado ali sem comentário. Ao investigar, apareceu algo "
        "melhor do que um ajuste de compressão: numa página de texto, abrir "
        "mão da cor não custa nada que importe e economiza quase tudo."),
    gemessen="Medido em 2026-08-04",
    rohdaten="dados brutos",
    tabelle=_tabelle(
        "1400 × 3200 px, compressão sem perdas, OCR com Tesseract 5.3.4",
        "Modo", "Arquivo", "Proporção", "Palavras relidas",
        "Cor total", "Escala de cinza", "Preto e branco"),
    h2_1="Uma página de texto, três profundidades de cor",
    h2_2="Por que não será o padrão",
    h2_3="O que está pronto e o que não está",
    h2_4="O que foi avaliado e descartado",
    absaetze=[
        ("Contra os 1327 kB que a compilação atual produz como JPEG, a última "
         "linha é <strong>8,5 %</strong>. E o reconhecimento de texto não "
         "piora: ele relê <em>duas palavras a mais</em> do que na versão "
         "colorida, com 99,9 % de concordância. Não é coincidência: o OCR "
         "binariza a imagem de qualquer modo. Entregar cor a ele é entregar um "
         "trabalho que ele descarta na hora."),
        ("O mesmo ajuste numa página de fotografias produz uma similaridade "
         "estrutural de <strong>0,199</strong> — a imagem se perdeu. Nenhum "
         "valor único serve para os dois casos, e por isso isso cabe a quem "
         "sabe o que está capturando. Uma lei, um registro de repositório, uma "
         "página de tabelas: preto e branco. Uma figura, um mapa, uma "
         "fotografia: cor."),
        ("O ajuste existe na <strong>2.28.0</strong>, nos dois ramos, e ambos "
         "os navegadores carregam essa compilação. Junto com isso, a captura "
         "deixou de incorporar sempre JPEG: cada bloco agora é comparado e "
         "usa-se o menor entre <code>FlateDecode</code> sem perdas e "
         "<code>DCTDecode</code>."),
        ("<strong>Ainda não está em nenhuma das duas lojas.</strong> O que "
         "está medido é a codificação e o reconhecimento; o que não está "
         "medido é uma captura completa num navegador real, porque isso exige "
         "um evento de entrada genuíno que o ambiente de teste não consegue "
         "produzir. Nenhuma data é prometida aqui — as lojas servem atualmente "
         "2.26.0 e 2.17.0, e este site não afirma quando isso vai mudar."),
        ("MRC, o padrão por trás dos PDFs digitalizados pequenos, alcança um "
         "fator de oito a dez. Ele se apoia em JBIG2, que substitui glifos "
         "parecidos por um padrão comum e tem substituições de dígitos "
         "documentadas. Para uma ferramenta cuja saída deve servir de prova, "
         "um arquivo em que um ano poderia mudar em silêncio não vale nada — a "
         "economia não entra na conta. WebP e AVIF nem fazem parte do PDF."),
        ("Os dados de procedência ficam intocados por tudo isso. Camada de "
         "texto, metadados e imagem são objetos separados no arquivo; o "
         "registro RIS e a soma de verificação ficam ao lado. Mudar como a "
         "imagem é armazenada não muda o que a captura diz sobre sua origem."),
        ("<strong>Qual ajuste para qual finalidade:</strong> "
         "<code>recommend_settings</code> no " + _MCP + "endpoint</a> responde "
         "por finalidade — citação, figura, arquivo ou ocr — e carrega consigo "
         "a medição por trás de cada valor, ou a observação explícita de que "
         "não existe nenhuma."),
    ],
    fuss=("Método: duas páginas sintéticas de 1400 × 3200 px, uma com muito "
          "texto e outra com muita imagem, cada uma codificada em três "
          "profundidades de cor e comprimida sem perdas. OCR com Tesseract "
          "5.3.4, modelo alemão, saída comparada à execução em cores por "
          "similaridade de sequência. A comparação estrutural usada aqui "
          "trabalha sobre a luminância e portanto não enxerga a perda de cor — "
          "a escala de cinza pontua 1,000 apesar de não ter nenhuma. Páginas "
          "sintéticas: a ordem de grandeza se sustenta, os valores "
          "individuais não. Nada disto é aconselhamento jurídico."),
    korrekturen="Correções são bem-vindas e feitas em público:",
    disclaimer_text="Aviso legal",
)

# -------------------------------------------------------------------- Русский
INHALT["ru"] = _seite(
    h1="Снимок в 8,5 % от размера — и OCR читает его чуть лучше",
    standfirst=(
        "Наше собственное измерение давало снимок в 6,7 МБ против 1,1 МБ у "
        "экспорта на печать из браузера — отмечено на странице сравнения и "
        "оставлено там без комментария. При разборе нашлось кое-что получше "
        "настройки сжатия: для текстовой страницы отказ от цвета не стоит "
        "ничего существенного и экономит почти всё."),
    gemessen="Измерено 2026-08-04",
    rohdaten="исходные данные",
    tabelle=_tabelle(
        "1400 × 3200 px, сжатие без потерь, OCR с Tesseract 5.3.4",
        "Режим", "Файл", "Доля", "Слов прочитано обратно",
        "Полный цвет", "Оттенки серого", "Чёрно-белый"),
    h2_1="Одна страница текста, три глубины цвета",
    h2_2="Почему это не станет настройкой по умолчанию",
    h2_3="Что уже сделано, а что нет",
    h2_4="Что рассмотрели и отклонили",
    absaetze=[
        ("Против 1327 кБ, которые текущая сборка выдаёт в JPEG, последняя "
         "строка — это <strong>8,5 %</strong>. И распознавание текста не "
         "страдает: оно вычитывает <em>на два слова больше</em>, чем из "
         "цветного варианта, при совпадении 99,9 %. Это не случайность: OCR "
         "всё равно бинаризует изображение. Отдать ему цвет — значит отдать "
         "работу, которую он тут же выбрасывает."),
        ("Та же настройка на странице с фотографиями даёт структурное "
         "сходство <strong>0,199</strong> — изображения больше нет. Ни одно "
         "значение не подходит для обоих случаев, и потому выбор остаётся за "
         "тем, кто знает, что именно снимает. Закон, запись репозитория, "
         "страница таблиц — чёрно-белый. Рисунок, карта, фотография — цвет."),
        ("Настройка есть в <strong>2.28.0</strong>, в обеих ветках, и оба "
         "браузера загружают эту сборку. Вместе с этим снимок перестал всегда "
         "встраивать JPEG: каждый фрагмент теперь сравнивается, и берётся "
         "меньший из <code>FlateDecode</code> без потерь и "
         "<code>DCTDecode</code>."),
        ("<strong>Ни в одном из магазинов этого пока нет.</strong> Измерены "
         "кодирование и распознавание; не измерен полный снимок в настоящем "
         "браузере, потому что для него нужно подлинное событие ввода, "
         "которого испытательный стенд создать не может. Сроков здесь не "
         "обещают: магазины сейчас отдают 2.26.0 и 2.17.0, и этот сайт не "
         "утверждает, когда это изменится."),
        ("MRC, стандарт за малыми сканированными PDF, достигает восьми- — "
         "десятикратного выигрыша. Он опирается на JBIG2, который заменяет "
         "похожие начертания одним общим образцом и имеет задокументированные "
         "подмены цифр. Для инструмента, вывод которого должен служить "
         "доказательством, файл, в котором год может незаметно измениться, не "
         "стоит ничего — экономия тут не в счёт. WebP и AVIF вообще не входят "
         "в PDF."),
        ("Сведения о происхождении всё это не затрагивает. Текстовый слой, "
         "метаданные и изображение — отдельные объекты в файле; запись RIS и "
         "контрольная сумма лежат рядом. Изменить способ хранения изображения "
         "не значит изменить то, что снимок говорит о своём источнике."),
        ("<strong>Какая настройка для какой цели:</strong> "
         "<code>recommend_settings</code> на " + _MCP + "конечной точке</a> "
         "отвечает по назначению — цитата, рисунок, архив или ocr — и несёт с "
         "собой измерение, стоящее за каждым значением, либо прямое указание, "
         "что такого измерения нет."),
    ],
    fuss=("Метод: две синтетические страницы 1400 × 3200 px, одна насыщена "
          "текстом, другая изображениями; каждая закодирована в трёх глубинах "
          "цвета и сжата без потерь. OCR с Tesseract 5.3.4, немецкая модель, "
          "вывод сопоставлен с цветным прогоном по сходству "
          "последовательностей. Использованное здесь структурное сравнение "
          "работает по яркости и поэтому не видит потери цвета — оттенки "
          "серого получают 1,000, хотя цвета в них нет. Страницы "
          "синтетические: порядок величины держится, отдельные значения нет. "
          "Ничто из этого не является юридической консультацией."),
    korrekturen="Исправления приветствуются и вносятся публично:",
    disclaimer_text="Отказ от ответственности",
)

# --------------------------------------------------------------------- 简体中文
INHALT["zh-CN"] = _seite(
    h1="体积只有 8.5 % 的抓取，OCR 反而读得略好",
    standfirst=(
        "我们自己的测量结果是：抓取 6.7 MB，浏览器的打印导出 1.1 MB。这条记录写在"
        "对比页上，一直没有加注。深究之后，找到了比压缩设置更好的东西：对一页文字"
        "而言，放弃颜色不会损失任何要紧的内容，却几乎省下了全部体积。"),
    gemessen="测量于 2026-08-04",
    rohdaten="原始数据",
    tabelle=_tabelle(
        "1400 × 3200 px，无损压缩，OCR 使用 Tesseract 5.3.4",
        "模式", "文件", "占比", "回读词数",
        "全彩", "灰度", "黑白"),
    h2_1="一页文字，三种色深",
    h2_2="为什么它不会成为默认值",
    h2_3="已经做好的与尚未做到的",
    h2_4="考察过并且放弃的方案",
    absaetze=[
        ("相对于当前版本以 JPEG 生成的 1327 kB，最后一行是 <strong>8.5 %</strong>。"
         "而且文字识别并未变差——它比彩色版本多读回 <em>两个词</em>，一致率 99.9 %。"
         "这不是巧合：OCR 本来就会把图像二值化。给它颜色，等于交给它一份随即丢弃的"
         "工作。"),
        ("同样的设置用在照片页上，结构相似度是 <strong>0.199</strong>——图像已经没了。"
         "没有哪一个取值能同时适用于两者，所以这件事应当交给知道自己在抓取什么的人。"
         "法条、仓储条目、表格页：黑白。插图、地图、照片：彩色。"),
        ("该设置存在于 <strong>2.28.0</strong>，两个分支都有，两种浏览器都加载这一"
         "版本。与此同时，抓取不再总是嵌入 JPEG：现在会逐块比较，取无损 "
         "<code>FlateDecode</code> 与 <code>DCTDecode</code> 中较小的一个。"),
        ("<strong>两个商店都还没有上架。</strong>已测量的是编码与识别；未测量的是"
         "在真实浏览器中的完整抓取，因为那需要一个真实的输入事件，而测试环境无法"
         "产生。这里不承诺日期——商店目前提供 2.26.0 和 2.17.0，本站不就何时改变"
         "作出任何说法。"),
        ("MRC 是小体积扫描 PDF 背后的标准，可以达到八到十倍。它依赖 JBIG2，"
         "后者把相似字形替换为同一个共用图样，并且有记录在案的数字混淆。对于一件"
         "输出要用作凭证的工具来说，一个年份可能悄悄改变的文件毫无价值——省下的"
         "体积不在考虑之列。WebP 和 AVIF 根本不属于 PDF。"),
        ("出处信息不受这些改动影响。文本层、元数据和图像在文件中是各自独立的对象；"
         "RIS 记录和校验和另置一旁。改变图像的存储方式，并不改变这份抓取关于自身"
         "来源所说的内容。"),
        ("<strong>什么用途配什么设置：</strong>" + _MCP + "端点</a> 上的 "
         "<code>recommend_settings</code> 按用途作答——引用、插图、存档或 ocr——"
         "并附上每个取值背后的测量；若没有测量，则明确说明。"),
    ],
    fuss=("方法：两页 1400 × 3200 px 的合成页面，一页以文字为主，一页以图像为主，"
          "各以三种色深编码并无损压缩。OCR 使用 Tesseract 5.3.4 德语模型，输出以"
          "序列相似度与彩色版本比较。此处使用的结构性比较基于亮度，因此看不到颜色"
          "损失——灰度虽无颜色，得分却是 1.000。页面为合成，故数量级成立，单项数值"
          "不成立。以上内容均不构成法律建议。"),
    korrekturen="欢迎指正，更正将公开进行：",
    disclaimer_text="免责声明",
)
