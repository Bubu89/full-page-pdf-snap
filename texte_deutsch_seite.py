#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/deutsch/ in neun Sprachen — die deutschsprachige Einstiegsseite.

Ausgangstext ist die AUSGELIEFERTE Seite docs/deutsch/index.html, woertlich
uebernommen — nicht build-de-index.py. Der Builder liest den Inhalt aus den
Seiten selbst und wuerde beim naechsten Lauf andere (leere) Vorschautexte
erzeugen, weil sein Muster `<p lang="de">` die neue Neunsprachen-Auszeichnung
nicht mehr trifft. Siehe tools/builder-drift.py.

Besonderheit dieser Seite: Sie ist als einzige durchgehend deutsch verfasst.
Deshalb steht der vorgefundene Text als `de`, und `en` ist daraus abgeleitet.
BASIS bleibt "en", wie auf allen uebrigen Seiten.

Unveraendert in jeder Sprache:

* alle Adressen (`_EINTRAEGE`, `_ANLEITUNG`, `_ENGLISCHE_SEITE`, Fusszeile),
* die TITEL der verlinkten Beitraege. Sie sind die Titel der Dokumente, auf
  die verwiesen wird; elf davon sind englisch verfasst, einer deutsch. Ein
  uebersetzter Titel wuerde eine Fassung versprechen, die es nicht gibt.
* die Zahl 12, das Datum 3. August 2026 (nur die Schreibweise folgt der
  Sprache), `Deutsch` als Beschriftung des Menuepunkts und
  `tools/seo-pruefen.py`.

Die Vorschautexte sind in der Quelle hart bei 190 Zeichen abgeschnitten
(build-de-index.py, Zeile 46) und enden mitten im Satz. Das ist woertlich
uebernommen: die Uebersetzungen brechen an derselben inhaltlichen Stelle ab,
allerdings an einer Wortgrenze — ein Schnitt mitten im Wort ist ein Artefakt
der deutschen Zeichenzahl, kein Inhalt.

Rendern:  python3 tools/seite-neunsprachig.py texte_deutsch_seite.py
"""

URL = "https://provinglab.dev/deutsch/"
ZIEL = "deutsch/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
# Diese eine Seite hat "de" als Basis, nicht "en". Sie ist die deutschsprachige
# Einstiegsseite: Titel und Beschreibung im Kopf sagen "Deutschsprachige
# Fassungen", und wer sie ohne JavaScript oeffnet, soll Deutsch sehen. Auf allen
# uebrigen Seiten bleibt "en" die Basis. (16.08.2026)
BASIS = "de"

# (Adresse, Titel) — in jeder Sprache gleich. Reihenfolge wie ausgeliefert
# (der Builder sortiert nach Titel).
_EINTRAEGE = [
    ("/about/",
     "About &amp; disclosure"),
    ("/measurements/citation-triage/",
     "An agent can cite eight of twelve sources. The useful part is knowing "
     "which four it cannot"),
    ("/disclaimer/",
     "Disclaimer and limitation of liability"),
    ("/how-to/firefox-and-chrome/",
     "For researchers and students: the add-on in Firefox and Chrome — setup "
     "and the academic workflow"),
    ("/how-to/for-students/",
     "For students: a source that cites itself, survives, and can be read by "
     "a machine"),
    ("/tools/full-page-pdf-snap/",
     "Full Page PDF Snap — download an entire webpage as one seamless PDF"),
    ("/measurements/de-plattformen/",
     "German-language scholarly platforms measured: four read, seven handed "
     "back"),
    ("/notes/pages-gone-before-you-need-them/",
     "Pages that are gone before you need them: eight moments in a degree"),
    ("/tools/pushdictate/",
     "PushDictate — push-to-talk dictation for Windows that works in the "
     "terminal"),
    ("/measurements/reading-list-to-bibliography/",
     "Twenty links, ten citations: what a machine finishes and what it hands "
     "back"),
    ("/measurements/web-citations-that-vanish/",
     "Web citations that vanish: what happens to a source after you cite it"),
    ("/measurements/citation-by-platform/",
     "Where citation data actually lives: 18 scholarly platforms measured"),
]

_ANLEITUNG_HREF = "/anleitung/webseite-als-pdf-speichern/"
_ANLEITUNG_TITEL = "Webseite als PDF speichern — die Anleitung"

# Beschriftet die englische Seite und ist selbst englisch — mit lang="en"
# ausgezeichnet, also in jeder Fassung unveraendert.
_ENGLISCHE_SEITE = '<a href="/" hreflang="en" lang="en">English site</a>'

_SEO = "<code>tools/seo-pruefen.py</code>"

_ZURUECK = '<a href="../">← Proving Lab</a>'
_UEBER = '<a href="../about/">'
_ISSUES = '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">'
_HAFTUNG = '<a href="../disclaimer/">'


def _fuss(ueber, korrekturen, issues, haftung):
    """Fusszeile. Die vier Beschriftungen sind woertlich die aus
    texte_indexseiten.py — dieselben Ziele sollen ueberall gleich heissen."""
    return (f"<footer>{_ZURUECK} · {_UEBER}{ueber}</a> · {korrekturen} "
            f"{_ISSUES}{issues}</a> · {_HAFTUNG}{haftung}</a></footer>")


def _liste(vorschau):
    """Die zwoelf Eintraege. Adressen und Titel stehen nur in _EINTRAEGE."""
    if len(vorschau) != len(_EINTRAEGE):
        raise SystemExit(f"{len(vorschau)} Vorschautexte, "
                         f"{len(_EINTRAEGE)} Eintraege")
    return "\n".join(
        f'<div class="item">\n  <h2><a href="{h}">{t}</a></h2>\n'
        f'  <p>{v}</p>\n</div>'
        for (h, t), v in zip(_EINTRAEGE, vorschau))


def _seite(h1, standfirst, menuehinweis, vorschau,
           anleitung, befund, h2_warum, warum, fuss):
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{menuehinweis} ·
    {_ENGLISCHE_SEITE}</p>
</header>

{_liste(vorschau)}

<div class="item">
  <h2><a href="{_ANLEITUNG_HREF}">{_ANLEITUNG_TITEL}</a></h2>
  <p>
    {anleitung}
  </p>
  <p style="font-size:.9rem">
    {befund}
  </p>
</div>

<div class="item">
  <h2>{h2_warum}</h2>
  <p>
    {warum}
  </p>
</div>

{fuss}'''


INHALT = {}

# ==================================================================== en ====
INHALT["en"] = _seite(
    h1="German-language versions",
    standfirst=("This site is written in English. 12 posts additionally carry "
                "a full German version on the same page. They are not "
                "translations but versions of the same argument in their own "
                "right, written for readers in Austria and Germany."),
    menuehinweis=("On those pages the “Deutsch” link in the menu leads "
                  "straight to the German part, everywhere else it leads "
                  "here."),
    vorschau=[
        "",
        ("A reading list goes in, citable records come out — for two thirds "
         "of it. The remaining third the publishers refuse to every server "
         "that asks. What makes the endpoint useful"),
        ("This page sets out what is answered for and what is not — for the "
         "software published here as much as for the articles and "
         "measurement data on this site. It applies to everything under "
         "proving"),
        ("The counterpart to why a web source fails in a seminar paper is "
         "this post: how the extension is set up in Firefox and Chrome, and "
         "how the capture–cite–archive"),
        ("Three things go wrong with a web source in a seminar paper. It "
         "disappears before the submission date. Its citation has to be "
         "typed out by hand. And the file you kept is"),
        ("Download the entire webpage seamlessly as a PDF — high resolution, "
         "in one file. Auto-scroll captures the whole page: no cropping, no "
         "page breaks, no print dialog, no upload"),
        ("A paper at a German-language university cites SSOAR, the National "
         "Library, Nomos and Destatis — not PubMed. On 3 August 2026, eleven "
         "such platforms went through the citation"),
        ("A measurement of our own on this site examined what happens to "
         "sources after they are cited. Most of the moments in a degree in "
         "which something on screen counts later have to do with"),
        ("Hold Ctrl+Space, speak, let go — the text appears where the cursor "
         "is blinking. In the terminal too, where Windows speech recognition "
         "gives up."),
        ("A reading list of twenty sources through a citation endpoint. Ten "
         "came back as complete records with RIS and BibTeX, in eight "
         "seconds. The interesting half are the others"),
        ("Every bibliography carries retrieval dates, and hardly anyone is "
         "told what for. The reason: a web source is not a book. After being "
         "cited it can be changed, moved or deleted"),
        ("A source reference is only as good as the data behind it. Eighteen "
         "platforms that researchers realistically use were asked what they "
         "declare about their own articles. Eleven"),
    ],
    anleitung=("Written for people, every figure linked to its measurement: "
               "why an extension instead of the print dialog, where the print "
               "export wins anyway, what works on Android, and why a "
               "reference needs the retrieval date."),
    befund=("Until 3 August 2026 this site linked only the English version — "
            "the German one existed but was reachable from nowhere, and thus "
            "as good as absent for search engines. It was found by " + _SEO +
            ", the only genuine result among twenty reports, sixteen of which "
            "turned out to be faults of the checker itself."),
    h2_warum="Why not the whole site?",
    warum=("Because a half-maintained translation is worse than an honest "
           "partial one. The measurements contain figures, methods and "
           "corrections that change; letting two language versions of them "
           "drift apart would be exactly the kind of mistake written about "
           "here otherwise. So what gets translated is what can also be kept "
           "complete in German."),
    fuss=_fuss("About &amp; disclosure", "Corrections:", "GitHub issues",
               "Disclaimer"),
)

# ==================================================================== de ====
INHALT["de"] = _seite(
    h1="Deutschsprachige Fassungen",
    standfirst=("Diese Seite ist auf Englisch geschrieben. 12 Beiträge tragen "
                "zusätzlich eine vollständige deutsche Fassung auf derselben "
                "Seite. Es sind keine Übersetzungen, sondern eigenständige "
                "Fassungen desselben Arguments, geschrieben für Leser in "
                "Österreich und Deutschland."),
    menuehinweis=("Der Link „Deutsch“ im Menü führt auf diesen Seiten direkt "
                  "zum deutschen Teil, überall sonst hierher."),
    vorschau=[
        "",
        ("Eine Leseliste geht hinein, zitierfähige Nachweise kommen heraus — "
         "für zwei Drittel davon. Das restliche Drittel verweigern die "
         "Verlage jedem Server, der nachfragt. Was den Endpunkt nützlich"),
        ("Diese Seite legt fest, wofür eingestanden wird und wofür nicht — "
         "für die hier veröffentlichte Software ebenso wie für die Artikel "
         "und Messdaten dieser Seite. Sie gilt für alles unter proving"),
        ("Das Gegenstück zu warum eine Webquelle in der Seminararbeit "
         "scheitert ist dieser Beitrag: wie die Erweiterung in Firefox und "
         "Chrome eingerichtet wird und wie der Ablauf aufnehmen–zitieren–ar"),
        ("Drei Dinge gehen mit einer Webquelle in einer Seminararbeit schief. "
         "Sie verschwindet vor der Abgabe. Ihre Zitation muss von Hand "
         "abgetippt werden. Und die Datei, die Sie aufgehoben haben, is"),
        ("Die gesamte Webseite nahtlos als PDF herunterladen — hochauflösend, "
         "in einer Datei. Auto-Scroll erfasst die ganze Seite: kein "
         "Zuschneiden, keine Seitenumbrüche, kein Druckdialog, kein Upload"),
        ("Eine Arbeit an einer deutschsprachigen Hochschule zitiert SSOAR, "
         "die Nationalbibliothek, Nomos und Destatis — nicht PubMed. Elf "
         "solcher Plattformen gingen am 3. August 2026 durch den Zitatio"),
        ("Eine eigene Messung auf dieser Seite hat untersucht, was mit "
         "Quellen nach dem Zitieren geschieht. Die meisten Momente im "
         "Studium, in denen ein Bildschirminhalt später zählt, haben mit "
         "dem Li"),
        ("Strg+Leertaste halten, sprechen, loslassen — der Text erscheint "
         "dort, wo der Cursor blinkt. Auch im Terminal, wo die "
         "Windows-Spracherkennung aufgibt."),
        ("Eine Leseliste aus zwanzig Quellen durch einen Zitations-Endpunkt. "
         "Zehn kamen als vollständige Nachweise mit RIS und BibTeX zurück, "
         "in acht Sekunden. Die interessante Hälfte sind die anderen"),
        ("In jedem Literaturverzeichnis stehen Abrufdaten, und kaum jemandem "
         "wird gesagt, wozu. Der Grund: Eine Webquelle ist kein Buch. Sie "
         "kann nach dem Zitieren geändert, verschoben oder gelöscht w"),
        ("Ein Quellennachweis ist nur so gut wie die Daten dahinter. "
         "Achtzehn Plattformen, die Forschende realistischerweise nutzen, "
         "wurden gefragt, was sie über ihre eigenen Artikel ausweisen. "
         "Elf an"),
    ],
    anleitung=("Für Menschen geschrieben, jede Zahl mit ihrer Messung "
               "verlinkt: warum eine Erweiterung statt des Druckdialogs, wo "
               "der Druckexport trotzdem gewinnt, was auf Android geht und "
               "warum in eine Quellenangabe das Abrufdatum gehört."),
    befund=("Diese Seite verlinkte bis zum 3. August 2026 nur die englische "
            "Fassung — die deutsche existierte, war aber von nirgendwo "
            "erreichbar und damit für Suchmaschinen praktisch nicht "
            "vorhanden. Gefunden hat es " + _SEO + " als einzigen echten "
            "Befund unter zwanzig Meldungen, von denen sich sechzehn als "
            "Fehler des Prüfers herausstellten."),
    h2_warum="Warum nicht die ganze Seite?",
    warum=("Weil eine halb gepflegte Übersetzung schlechter ist als eine "
           "ehrliche Teilfassung. Die Messungen enthalten Zahlen, Methoden "
           "und Korrekturen, die sich ändern; zwei Sprachfassungen davon "
           "auseinanderlaufen zu lassen wäre genau die Art Fehler, über die "
           "hier sonst geschrieben wird. Übersetzt wird daher, was auch auf "
           "Deutsch vollständig gepflegt werden kann."),
    fuss=_fuss("Über &amp; Offenlegung", "Korrekturen:", "GitHub Issues",
               "Haftungsausschluss"),
)

# ==================================================================== es ====
INHALT["es"] = _seite(
    h1="Versiones en alemán",
    standfirst=("Este sitio está escrito en inglés. 12 publicaciones llevan "
                "además una versión alemana completa en la misma página. No "
                "son traducciones, sino versiones autónomas del mismo "
                "argumento, escritas para lectores de Austria y Alemania."),
    menuehinweis=("En esas páginas el enlace «Deutsch» del menú lleva "
                  "directamente a la parte alemana; en todas las demás, "
                  "lleva aquí."),
    vorschau=[
        "",
        ("Entra una lista de lecturas, salen referencias citables — para dos "
         "tercios de ella. El tercio restante lo niegan las editoriales a "
         "todo servidor que pregunta. Lo que hace útil al endpoint"),
        ("Esta página establece de qué se responde y de qué no — tanto del "
         "software publicado aquí como de los artículos y los datos de "
         "medición de este sitio. Rige para todo lo que hay bajo proving"),
        ("La contraparte de por qué una fuente web fracasa en un trabajo de "
         "seminario es esta publicación: cómo se instala la extensión en "
         "Firefox y Chrome y cómo el flujo capturar–citar–archi"),
        ("Tres cosas salen mal con una fuente web en un trabajo de "
         "seminario. Desaparece antes de la entrega. Su cita hay que "
         "teclearla a mano. Y el archivo que usted guardó es"),
        ("Descargar la página web entera y sin costuras como PDF — en alta "
         "resolución, en un solo archivo. El auto-scroll capta la página "
         "completa: sin recortes, sin saltos de página, sin diálogo de "
         "impresión, sin subida"),
        ("Un trabajo en una universidad de habla alemana cita SSOAR, la "
         "Biblioteca Nacional, Nomos y Destatis — no PubMed. Once "
         "plataformas de ese tipo pasaron el 3 de agosto de 2026 por el "
         "endpoint de citas"),
        ("Una medición propia de este sitio examinó qué ocurre con las "
         "fuentes después de citarlas. La mayoría de los momentos de una "
         "carrera en los que lo que hay en pantalla cuenta más tarde tienen "
         "que ver con"),
        ("Mantener Ctrl+Espacio, hablar, soltar — el texto aparece donde "
         "parpadea el cursor. También en la terminal, donde el "
         "reconocimiento de voz de Windows se rinde."),
        ("Una lista de lecturas de veinte fuentes a través de un endpoint de "
         "citas. Diez volvieron como referencias completas con RIS y BibTeX, "
         "en ocho segundos. La mitad interesante son las otras"),
        ("En toda bibliografía figuran fechas de consulta, y a casi nadie se "
         "le dice para qué. La razón: una fuente web no es un libro. Después "
         "de citarla puede cambiarse, moverse o borrarse"),
        ("Una referencia solo vale lo que valen los datos que hay detrás. A "
         "dieciocho plataformas que los investigadores usan de forma "
         "realista se les preguntó qué declaran sobre sus propios artículos. "
         "Once"),
    ],
    anleitung=("Escrita para personas, cada cifra enlazada con su medición: "
               "por qué una extensión en lugar del diálogo de impresión, "
               "dónde gana aun así la exportación de impresión, qué funciona "
               "en Android y por qué una referencia necesita la fecha de "
               "consulta."),
    befund=("Hasta el 3 de agosto de 2026 esta página enlazaba solo la "
            "versión inglesa — la alemana existía, pero no era alcanzable "
            "desde ningún sitio y, por tanto, para los buscadores era como "
            "si no existiera. Lo encontró " + _SEO + ", como único hallazgo "
            "real entre veinte avisos, de los cuales dieciséis resultaron "
            "ser fallos del propio verificador."),
    h2_warum="¿Por qué no el sitio entero?",
    warum=("Porque una traducción a medio mantener es peor que una versión "
           "parcial honesta. Las mediciones contienen cifras, métodos y "
           "correcciones que cambian; dejar que dos versiones lingüísticas "
           "de ellas se separen sería exactamente el tipo de error sobre el "
           "que aquí se escribe. Por eso se traduce lo que también puede "
           "mantenerse completo en alemán."),
    fuss=_fuss("Acerca de &amp; divulgación", "Correcciones:",
               "issues de GitHub", "Aviso legal"),
)

# ==================================================================== fr ====
INHALT["fr"] = _seite(
    h1="Versions en allemand",
    standfirst=("Ce site est rédigé en anglais. 12 articles portent en outre "
                "une version allemande complète sur la même page. Ce ne sont "
                "pas des traductions, mais des versions autonomes du même "
                "argument, écrites pour des lecteurs d’Autriche et "
                "d’Allemagne."),
    menuehinweis=("Sur ces pages, le lien « Deutsch » du menu mène "
                  "directement à la partie allemande ; partout ailleurs, il "
                  "mène ici."),
    vorschau=[
        "",
        ("Une liste de lectures entre, des références citables sortent — pour "
         "deux tiers d’entre elles. Le tiers restant, les éditeurs le "
         "refusent à tout serveur qui demande. Ce qui rend le point d’accès "
         "utile"),
        ("Cette page fixe ce dont il est répondu et ce dont il ne l’est pas — "
         "pour le logiciel publié ici comme pour les articles et les données "
         "de mesure de ce site. Elle vaut pour tout ce qui se trouve sous "
         "proving"),
        ("Le pendant de pourquoi une source web échoue dans un mémoire de "
         "séminaire, c’est cet article : comment installer l’extension dans "
         "Firefox et Chrome et comment le déroulé capturer–citer–archi"),
        ("Trois choses tournent mal avec une source web dans un mémoire de "
         "séminaire. Elle disparaît avant la remise. Sa citation doit être "
         "retapée à la main. Et le fichier que vous avez conservé est"),
        ("Télécharger la page web entière, sans raccord, en PDF — haute "
         "résolution, en un seul fichier. Le défilement automatique saisit "
         "toute la page : pas de recadrage, pas de sauts de page, pas de "
         "boîte de dialogue d’impression, pas de téléversement"),
        ("Un travail dans une université germanophone cite SSOAR, la "
         "Bibliothèque nationale, Nomos et Destatis — pas PubMed. Onze "
         "plateformes de ce type sont passées le 3 août 2026 par le point "
         "d’accès de citation"),
        ("Une mesure propre à ce site a examiné ce qu’il advient des sources "
         "après leur citation. La plupart des moments d’un cursus où ce qui "
         "est à l’écran comptera plus tard tiennent à"),
        ("Maintenir Ctrl+Espace, parler, relâcher — le texte apparaît là où "
         "le curseur clignote. Dans le terminal aussi, là où la "
         "reconnaissance vocale de Windows abandonne."),
        ("Une liste de vingt sources à travers un point d’accès de citation. "
         "Dix sont revenues en références complètes avec RIS et BibTeX, en "
         "huit secondes. La moitié intéressante, ce sont les autres"),
        ("Toute bibliographie porte des dates de consultation, et on ne dit "
         "presque à personne à quoi elles servent. La raison : une source "
         "web n’est pas un livre. Après avoir été citée, elle peut être "
         "modifiée, déplacée ou supprimée"),
        ("Une référence ne vaut que ce que valent les données qui la portent. "
         "Dix-huit plateformes que les chercheurs utilisent réellement ont "
         "été interrogées sur ce qu’elles déclarent de leurs propres "
         "articles. Onze"),
    ],
    anleitung=("Écrit pour des humains, chaque chiffre relié à sa mesure : "
               "pourquoi une extension plutôt que la boîte de dialogue "
               "d’impression, où l’export d’impression l’emporte malgré "
               "tout, ce qui fonctionne sur Android et pourquoi une "
               "référence a besoin de la date de consultation."),
    befund=("Jusqu’au 3 août 2026, cette page ne renvoyait qu’à la version "
            "anglaise — l’allemande existait, mais n’était accessible de "
            "nulle part et donc, pour les moteurs de recherche, pour ainsi "
            "dire inexistante. C’est " + _SEO + " qui l’a trouvée, seul "
            "constat réel parmi vingt signalements, dont seize se sont "
            "révélés être des erreurs du vérificateur lui-même."),
    h2_warum="Pourquoi pas tout le site ?",
    warum=("Parce qu’une traduction à demi entretenue vaut moins qu’une "
           "version partielle honnête. Les mesures contiennent des chiffres, "
           "des méthodes et des corrections qui changent ; laisser deux "
           "versions linguistiques diverger serait exactement le genre "
           "d’erreur dont il est question ici par ailleurs. On traduit donc "
           "ce qui peut aussi être tenu à jour intégralement en allemand."),
    fuss=_fuss("À propos &amp; transparence", "Corrections :",
               "tickets GitHub", "Mentions légales"),
)

# ==================================================================== it ====
INHALT["it"] = _seite(
    h1="Versioni in tedesco",
    standfirst=("Questo sito è scritto in inglese. 12 contributi portano "
                "inoltre una versione tedesca completa nella stessa pagina. "
                "Non sono traduzioni, ma versioni autonome dello stesso "
                "argomento, scritte per lettori in Austria e in Germania."),
    menuehinweis=("Su queste pagine il collegamento «Deutsch» nel menu porta "
                  "direttamente alla parte tedesca, ovunque altrove porta "
                  "qui."),
    vorschau=[
        "",
        ("Entra una lista di letture, escono riferimenti citabili — per due "
         "terzi di essa. Il terzo restante gli editori lo negano a ogni "
         "server che chiede. Ciò che rende utile l’endpoint"),
        ("Questa pagina stabilisce di che cosa si risponde e di che cosa no — "
         "tanto per il software qui pubblicato quanto per gli articoli e i "
         "dati di misura di questo sito. Vale per tutto ciò che sta sotto "
         "proving"),
        ("Il contraltare del perché una fonte web fallisce in una tesina è "
         "questo contributo: come si configura l’estensione in Firefox e "
         "Chrome e come il percorso catturare–citare–archi"),
        ("Tre cose vanno storte con una fonte web in una tesina. Sparisce "
         "prima della consegna. La sua citazione va ribattuta a mano. E il "
         "file che avete conservato è"),
        ("Scaricare l’intera pagina web senza giunture come PDF — ad alta "
         "risoluzione, in un solo file. L’auto-scroll cattura tutta la "
         "pagina: nessun ritaglio, nessuna interruzione di pagina, nessuna "
         "finestra di stampa, nessun caricamento"),
        ("Un lavoro in un’università di lingua tedesca cita SSOAR, la "
         "Biblioteca nazionale, Nomos e Destatis — non PubMed. Undici "
         "piattaforme di questo tipo sono passate il 3 agosto 2026 "
         "attraverso l’endpoint di citazione"),
        ("Una misurazione propria di questo sito ha esaminato che cosa "
         "succede alle fonti dopo la citazione. La maggior parte dei momenti "
         "di un percorso di studi in cui ciò che è a schermo conta più tardi "
         "ha a che fare con"),
        ("Tenere premuto Ctrl+Spazio, parlare, rilasciare — il testo compare "
         "dove lampeggia il cursore. Anche nel terminale, dove il "
         "riconoscimento vocale di Windows si arrende."),
        ("Una lista di venti fonti attraverso un endpoint di citazione. Dieci "
         "sono tornate come riferimenti completi con RIS e BibTeX, in otto "
         "secondi. La metà interessante sono le altre"),
        ("In ogni bibliografia compaiono le date di consultazione, e quasi a "
         "nessuno viene detto a che cosa servano. Il motivo: una fonte web "
         "non è un libro. Dopo essere stata citata può essere modificata, "
         "spostata o cancellata"),
        ("Un riferimento vale quanto i dati che gli stanno dietro. A diciotto "
         "piattaforme che i ricercatori usano realisticamente è stato "
         "chiesto che cosa dichiarino sui propri articoli. Undici"),
    ],
    anleitung=("Scritta per persone, ogni cifra collegata alla sua "
               "misurazione: perché un’estensione invece della finestra di "
               "stampa, dove l’esportazione di stampa vince comunque, che "
               "cosa funziona su Android e perché in un riferimento serve la "
               "data di consultazione."),
    befund=("Fino al 3 agosto 2026 questa pagina rimandava solo alla versione "
            "inglese — quella tedesca esisteva, ma non era raggiungibile da "
            "nessuna parte e quindi, per i motori di ricerca, praticamente "
            "inesistente. L’ha trovata " + _SEO + ", come unico reperto reale "
            "fra venti segnalazioni, sedici delle quali si sono rivelate "
            "errori del verificatore stesso."),
    h2_warum="Perché non tutto il sito?",
    warum=("Perché una traduzione mantenuta a metà è peggio di una versione "
           "parziale onesta. Le misurazioni contengono cifre, metodi e "
           "correzioni che cambiano; lasciare che due versioni linguistiche "
           "divergano sarebbe esattamente il tipo di errore di cui qui si "
           "scrive altrimenti. Si traduce dunque ciò che può essere tenuto "
           "completo anche in tedesco."),
    fuss=_fuss("Informazioni &amp; trasparenza", "Correzioni:",
               "issue su GitHub", "Esclusione di responsabilità"),
)

# ==================================================================== ja ====
INHALT["ja"] = _seite(
    h1="ドイツ語版",
    standfirst=("このサイトは英語で書かれています。12 本の記事は、同じページ上に"
                "完全なドイツ語版を併せて備えています。翻訳ではなく、同じ論旨を"
                "自立した形で書き直したもので、オーストリアとドイツの読者に向け"
                "て書かれています。"),
    menuehinweis=("メニューの「Deutsch」は、それらのページではドイツ語部分へ直接"
                  "移動し、それ以外の場所ではここへ導きます。"),
    vorschau=[
        "",
        ("読書リストが入り、引用可能な書誌データが出てくる——その三分の二について"
         "は。残りの三分の一は、出版社が問い合わせるどのサーバーにも拒みます。"
         "このエンドポイントを有用にしているのは"),
        ("このページは、何について責任を負い、何について負わないかを定めます——"
         "ここで公開されているソフトウェアについても、本サイトの記事と測定データ"
         "についても同様です。proving 以下のすべてに適用され"),
        ("ゼミ論文でウェブ出典が失敗する理由と対をなすのがこの記事です。Firefox "
         "と Chrome で拡張機能をどう設定するか、そして取得–引用–保存という流れが"),
        ("ゼミ論文でウェブ出典に起きる不都合は三つあります。提出前に消えること。"
         "引用を手で打ち直さねばならないこと。そして、保存しておいたファイルが"),
        ("ウェブページ全体を継ぎ目なく PDF としてダウンロード——高解像度で、一つ"
         "のファイルに。オートスクロールがページ全体を捉えます。切り取りなし、"
         "改ページなし、印刷ダイアログなし、アップロードなし"),
        ("ドイツ語圏の大学の論文が引用するのは SSOAR、国立図書館、Nomos、Destatis "
         "であって、PubMed ではありません。そうした 11 のプラットフォームが "
         "2026年8月3日に引用エンドポイントを"),
        ("本サイト独自の測定が、引用された後に出典に何が起こるかを調べました。"
         "学修のなかで画面上のものが後になって効いてくる場面の多くは"),
        ("Ctrl+スペースを押しながら話し、離す——カーソルが点滅している場所に文字が"
         "現れます。Windows の音声認識が音を上げるターミナルでも動きます。"),
        ("二十件の出典からなる読書リストを引用エンドポイントに通しました。十件は "
         "RIS と BibTeX を伴う完全な書誌データとして、八秒で返ってきました。"
         "興味深いのは残りの半分です"),
        ("どの文献目録にも取得日が記されていますが、その意味を教えられる人はほとん"
         "どいません。理由は、ウェブ出典が書物ではないからです。引用された後に変"
         "更され、移動され、削除され"),
        ("出典表示は、その背後にあるデータの質を超えません。研究者が現実に使う十八"
         "のプラットフォームに、自らの論文について何を明示しているかを尋ねました。"
         "十一件が"),
    ],
    anleitung=("人間のために書かれ、どの数値もその測定へリンクしています。なぜ印刷"
               "ダイアログではなく拡張機能なのか、それでも印刷書き出しが勝つのは"
               "どこか、Android では何ができるのか、そしてなぜ出典表示に取得日が"
               "必要なのか。"),
    befund=("このページは 2026年8月3日まで英語版だけをリンクしていました——ドイツ語"
            "版は存在していたのに、どこからもたどり着けず、検索エンジンにとっては"
            "事実上存在しないも同然でした。見つけたのは " + _SEO + " です。二十件"
            "の指摘のうち唯一の本物の発見であり、そのうち十六件は検査ツール自身の"
            "誤りだと判明しました。"),
    h2_warum="なぜサイト全体ではないのか",
    warum=("中途半端に手入れされた翻訳は、正直な部分訳より劣るからです。測定には"
           "変わりうる数値・方法・訂正が含まれます。その二つの言語版を食い違わせる"
           "ことは、まさにこのサイトが普段書いている種類の誤りにあたります。"
           "したがって訳すのは、ドイツ語でも完全に維持できるものだけです。"),
    fuss=_fuss("概要と開示", "修正:", "GitHub issues", "免責事項"),
)

# ================================================================= pt-BR ====
INHALT["pt-BR"] = _seite(
    h1="Versões em alemão",
    standfirst=("Este site é escrito em inglês. 12 publicações trazem além "
                "disso uma versão alemã completa na mesma página. Não são "
                "traduções, mas versões autônomas do mesmo argumento, "
                "escritas para leitores na Áustria e na Alemanha."),
    menuehinweis=("Nessas páginas, o link “Deutsch” no menu leva direto à "
                  "parte alemã; em todo o resto, leva para cá."),
    vorschau=[
        "",
        ("Entra uma lista de leitura, saem referências citáveis — para dois "
         "terços dela. O terço restante as editoras negam a todo servidor que "
         "pergunta. O que torna o endpoint útil"),
        ("Esta página estabelece por que se responde e por que não — tanto "
         "pelo software aqui publicado quanto pelos artigos e dados de "
         "medição deste site. Vale para tudo o que está sob proving"),
        ("A contraparte de por que uma fonte da web fracassa num trabalho de "
         "seminário é esta publicação: como a extensão é configurada no "
         "Firefox e no Chrome e como o fluxo capturar–citar–arqui"),
        ("Três coisas dão errado com uma fonte da web num trabalho de "
         "seminário. Ela desaparece antes da entrega. A citação precisa ser "
         "digitada à mão. E o arquivo que você guardou é"),
        ("Baixar a página web inteira e sem emendas como PDF — em alta "
         "resolução, num único arquivo. O auto-scroll capta a página toda: "
         "sem cortes, sem quebras de página, sem caixa de impressão, sem "
         "upload"),
        ("Um trabalho numa universidade de língua alemã cita SSOAR, a "
         "Biblioteca Nacional, Nomos e Destatis — não PubMed. Onze "
         "plataformas desse tipo passaram em 3 de agosto de 2026 pelo "
         "endpoint de citação"),
        ("Uma medição própria deste site examinou o que acontece com as "
         "fontes depois de citadas. A maioria dos momentos de um curso em que "
         "o que está na tela conta mais tarde tem a ver com"),
        ("Segurar Ctrl+Espaço, falar, soltar — o texto aparece onde o cursor "
         "pisca. Também no terminal, onde o reconhecimento de voz do Windows "
         "desiste."),
        ("Uma lista de leitura de vinte fontes por um endpoint de citação. "
         "Dez voltaram como referências completas com RIS e BibTeX, em oito "
         "segundos. A metade interessante são as outras"),
        ("Em toda bibliografia constam datas de acesso, e quase a ninguém se "
         "diz para quê. O motivo: uma fonte da web não é um livro. Depois de "
         "citada, ela pode ser alterada, movida ou apagada"),
        ("Uma referência só vale o quanto valem os dados por trás dela. "
         "Dezoito plataformas que pesquisadores realisticamente usam foram "
         "perguntadas sobre o que declaram a respeito dos próprios artigos. "
         "Onze"),
    ],
    anleitung=("Escrito para pessoas, cada número ligado à sua medição: por "
               "que uma extensão em vez da caixa de impressão, onde a "
               "exportação de impressão ainda assim vence, o que funciona no "
               "Android e por que uma referência precisa da data de acesso."),
    befund=("Até 3 de agosto de 2026 esta página vinculava apenas a versão "
            "inglesa — a alemã existia, mas não era alcançável de lugar "
            "nenhum e, portanto, para os buscadores era praticamente "
            "inexistente. Quem encontrou foi " + _SEO + ", como único achado "
            "verdadeiro entre vinte avisos, dos quais dezesseis se revelaram "
            "erros do próprio verificador."),
    h2_warum="Por que não o site inteiro?",
    warum=("Porque uma tradução mantida pela metade é pior do que uma versão "
           "parcial honesta. As medições contêm números, métodos e correções "
           "que mudam; deixar duas versões linguísticas delas divergirem "
           "seria exatamente o tipo de erro sobre o qual aqui se escreve. "
           "Traduz-se, portanto, o que também pode ser mantido completo em "
           "alemão."),
    fuss=_fuss("Sobre &amp; transparência", "Correções:", "issues no GitHub",
               "Aviso legal"),
)

# ==================================================================== ru ====
INHALT["ru"] = _seite(
    h1="Версии на немецком языке",
    standfirst=("Этот сайт написан на английском. 12 материалов дополнительно "
                "несут полную немецкую версию на той же странице. Это не "
                "переводы, а самостоятельные версии того же рассуждения, "
                "написанные для читателей в Австрии и Германии."),
    menuehinweis=("На этих страницах ссылка «Deutsch» в меню ведёт прямо к "
                  "немецкой части, во всех остальных случаях — сюда."),
    vorschau=[
        "",
        ("На вход — список литературы, на выход — пригодные для цитирования "
         "записи, но лишь для двух третей. Оставшуюся треть издательства "
         "закрывают от любого сервера, который спрашивает. Полезной эту "
         "конечную точку делает"),
        ("Эта страница определяет, за что берётся ответственность, а за что "
         "нет, — как для опубликованного здесь программного обеспечения, так "
         "и для статей и данных измерений этого сайта. Она распространяется "
         "на всё, что находится под proving"),
        ("Дополнением к тому, почему веб-источник подводит в семинарской "
         "работе, служит этот материал: как расширение настраивается в "
         "Firefox и Chrome и как порядок «снять–процитировать–сохран"),
        ("С веб-источником в семинарской работе не так идут три вещи. Он "
         "исчезает до срока сдачи. Ссылку на него приходится набирать "
         "вручную. И файл, который вы сохранили,"),
        ("Скачать всю веб-страницу целиком и без швов в PDF — с высоким "
         "разрешением, одним файлом. Автопрокрутка захватывает страницу "
         "полностью: без обрезки, без разрывов страниц, без диалога печати, "
         "без загрузки на сервер"),
        ("Работа в немецкоязычном вузе ссылается на SSOAR, Национальную "
         "библиотеку, Nomos и Destatis, а не на PubMed. Одиннадцать таких "
         "платформ прошли 3 августа 2026 г. через цитатную"),
        ("Собственное измерение на этом сайте выяснило, что происходит с "
         "источниками после цитирования. Большинство моментов учёбы, когда "
         "содержимое экрана оказывается важным позже, связаны с"),
        ("Удерживайте Ctrl+Пробел, говорите, отпускайте — текст появляется "
         "там, где мигает курсор. В том числе в терминале, где распознавание "
         "речи Windows сдаётся."),
        ("Список из двадцати источников через цитатную конечную точку. Десять "
         "вернулись полными записями с RIS и BibTeX за восемь секунд. "
         "Интересна другая половина"),
        ("В каждом списке литературы стоят даты обращения, и почти никому не "
         "объясняют зачем. Причина: веб-источник — не книга. После "
         "цитирования его могут изменить, перенести или удалить"),
        ("Библиографическая запись хороша ровно настолько, насколько хороши "
         "данные за ней. Восемнадцать платформ, которыми исследователи "
         "реально пользуются, спросили о том, что они сообщают о собственных "
         "статьях. Одиннадцать"),
    ],
    anleitung=("Написано для людей, каждое число связано со своим измерением: "
               "почему расширение вместо диалога печати, где экспорт печати "
               "всё же выигрывает, что работает на Android и почему в "
               "библиографической записи нужна дата обращения."),
    befund=("До 3 августа 2026 г. эта страница ссылалась только на английскую "
            "версию — немецкая существовала, но была недостижима ниоткуда и "
            "потому для поисковых систем практически отсутствовала. Нашёл её "
            + _SEO + " — единственная настоящая находка среди двадцати "
            "сообщений, шестнадцать из которых оказались ошибками самого "
            "проверяющего инструмента."),
    h2_warum="Почему не весь сайт?",
    warum=("Потому что наполовину поддерживаемый перевод хуже честной "
           "частичной версии. Измерения содержат числа, методы и "
           "исправления, которые меняются; дать двум языковым версиям "
           "разойтись было бы ровно той ошибкой, о которой здесь обычно и "
           "пишут. Поэтому переводится то, что можно полноценно "
           "поддерживать и по-немецки."),
    fuss=_fuss("О сайте и раскрытие", "Исправления:", "issues на GitHub",
               "Отказ от ответственности"),
)

# ================================================================= zh-CN ====
INHALT["zh-CN"] = _seite(
    h1="德语版本",
    standfirst=("本站以英文撰写。有 12 篇文章在同一页面上另附完整的德语版本。"
                "它们不是译文，而是同一论点的独立写法，写给奥地利和德国的读者。"),
    menuehinweis=("在这些页面上，菜单里的「Deutsch」直接跳到德语部分；"
                  "在其他任何地方，它都指向这里。"),
    vorschau=[
        "",
        ("一份阅读清单进去，可直接引用的著录出来——但只有其中三分之二。"
         "剩下的三分之一，出版社对每一个前来询问的服务器都拒绝。"
         "让这个端点真正有用的是"),
        ("本页规定了哪些事由我们承担、哪些不承担——既针对这里发布的软件，"
         "也针对本站的文章与测量数据。它适用于 proving 之下的一切"),
        ("与「一份网络来源为何会在研讨论文里失效」相对应的，就是这篇文章："
         "如何在 Firefox 和 Chrome 中设置该扩展，以及抓取–引用–归"),
        ("在研讨论文里，一份网络来源会出三种岔子。它在交稿前消失。"
         "它的引文必须手工敲一遍。而你保存下来的那个文件，是"),
        ("把整个网页无缝下载为 PDF——高分辨率，一个文件。自动滚动会捕捉整页："
         "不裁切、不分页、不弹打印对话框、不上传"),
        ("一篇德语高校的论文引用的是 SSOAR、国家图书馆、Nomos 和 Destatis，"
         "而不是 PubMed。十一个这样的平台在 2026年8月3日走了一遍引用"),
        ("本站自己的一次测量考察了来源被引用之后会发生什么。"
         "求学过程中那些屏幕上的内容日后才见分晓的时刻，多半与"),
        ("按住 Ctrl+空格说话，松开——文字就出现在光标闪烁的地方。"
         "在终端里也一样，而 Windows 的语音识别在那里会放弃。"),
        ("一份二十条来源的阅读清单，走一遍引用端点。十条带着 RIS 和 BibTeX "
         "作为完整著录返回，用时八秒。有意思的是另一半"),
        ("每份参考文献表里都写着访问日期，却几乎没人被告知它有什么用。"
         "原因是：网络来源不是书。它在被引用之后仍可被修改、移动或删除"),
        ("一条来源著录，好不过它背后的数据。十八个研究者实际会用的平台，"
         "被问及它们对自己的文章公布了什么。十一个"),
    ],
    anleitung=("为人而写，每个数字都链接到它的测量：为什么用扩展而不是打印对话框，"
               "打印导出在哪些情况下仍然更好，Android 上能做什么，"
               "以及为什么来源标注里要有访问日期。"),
    befund=("这个页面在 2026年8月3日之前只链接英文版——德文版存在，"
            "却从任何地方都无法到达，因此对搜索引擎而言形同不存在。"
            "发现它的是 " + _SEO + "，这是二十条报告里唯一真正的发现，"
            "其中十六条后来证明是检查工具自己的错误。"),
    h2_warum="为什么不做整站？",
    warum=("因为一份维护到一半的译文，比一份诚实的部分译本更糟。"
           "测量里包含会变动的数字、方法和更正；让两个语言版本各走各的，"
           "恰恰是本站平时所写的那类错误。因此只翻译那些在德语里"
           "同样能够完整维护的内容。"),
    fuss=_fuss("关于与披露", "更正:", "GitHub issues", "免责声明"),
)
