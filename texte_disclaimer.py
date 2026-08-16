#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Die Disclaimer-Seite in neun Sprachen — getrennt vom Bauen.

Muster wie texte_for_agents.py: ENGLISCH ist die Ausgangsfassung,
Rendering ueber build_disclaimer.py. EN- und DE-Texte sind WOERTLICH
aus docs/disclaimer/index.html uebernommen (nur strukturiert), die
uebrigen sieben Sprachen sind idiomatische Uebersetzungen. Haftungsseite:
konservativ und praezise, keine Abschwaechung des Haftungsausschlusses,
keine neuen Tatsachen.

Die MIT-Gewaehrleistungsklausel (ZITAT) ist Lizenztext und bleibt in
jeder Sprache unveraendert englisch — die Uebersetzungen weisen jeweils
darauf hin, dass der englische Wortlaut massgeblich ist.

Aenderungen am Inhalt HIER, danach `python3 build_disclaimer.py`.
"""

URL = "https://provinglab.dev/disclaimer/"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# Lizenztext, kein Fliesstext — darum nicht uebersetzt und in allen
# Sprachfassungen identisch.
ZITAT = (
    'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,\n'
    "    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR\n"
    "    PURPOSE AND NONINFRINGEMENT."
)

# Pro Sprache: h1, standfirst, meta, kurz_stark + kurz (das "wichtig"-Feld)
# und "punkte" als Liste von (ueberschrift, absaetze). Ein Absatz ist
# ("p", html) oder ("z", None) fuer das MIT-Zitat.
TEXTE = {}

# --------------------------------------------------------------- English ----
TEXTE["en"] = {
    "h1": "Disclaimer and limitation of liability",
    "standfirst": (
        "This page states what is warranted and what is not — for the software published here and\n"
        "    for the articles and measurement data on this site. It applies to everything under\n"
        "    provinglab.dev and to the extension distributed from it."
    ),
    "meta": "Version of 3 August 2026",
    "kurz_stark": "In short.",
    "kurz": (
        "The software and the content are provided free of charge and\n"
        "  as they are. No warranty of any kind is given, and liability is excluded as far as the law\n"
        "  permits. What the law does not permit to exclude — intent, gross negligence, injury to life,\n"
        "  body or health, and any mandatory statutory liability — remains unaffected, and no wording\n"
        "  on this page changes that."
    ),
    "punkte": [
        ("1. The software: no warranty", [
            ("p", "Full Page PDF Snap is published under the MIT licence. Its warranty clause is part of the\n"
                  "    licence and applies in full:"),
            ("z", None),
            ("p", "In particular, no assurance is given that the extension is fit for any specific purpose,\n"
                  "    that it works on any specific page, browser version or device, or that it will remain\n"
                  "    available."),
        ]),
        ("2. Check the result before you rely on it", [
            ("p", "A capture can be incomplete without saying so. Pages that load while scrolling, that\n"
                  "    render differently at another window size, that hide content behind interaction, or that\n"
                  "    change while the capture runs can all produce a PDF that is missing something. The\n"
                  "    extension has no way to know what the page was supposed to contain."),
            ("p", "Where the content matters — a confirmation, a deadline, an amount, a transaction row —\n"
                  "    open the finished PDF and read the relevant part before you rely on it. That check takes\n"
                  "    seconds and is the only thing that establishes the capture actually holds what you need."),
        ]),
        ("3. Not a qualified electronic document", [
            ("p", "A PDF produced by screen capture records what a browser displayed. It carries no qualified\n"
                  "    electronic signature, no trusted timestamp and no chain of custody, and it does not by\n"
                  "    itself prove that a page existed in that form. It is suitable for your own records. Where\n"
                  "    evidentiary weight is required, a service built for that purpose is the right instrument."),
        ]),
        ("4. No professional advice", [
            ("p", "Nothing published here is legal, tax, financial, medical or any other form of professional\n"
                  "    advice, and no client relationship arises from reading it. Articles touch on questions with\n"
                  "    a legal dimension — permissions, licences, copyright, the evidentiary value of a record,\n"
                  "    rules on citation and deadlines. Those passages describe how things are generally\n"
                  "    understood; they do not decide your case. Institutional rules and applicable law take\n"
                  "    precedence over anything written here, and for a specific situation, qualified advice is\n"
                  "    the right route."),
        ]),
        ("5. Measurements are measurements, not guarantees", [
            ("p", "Figures published here come from single runs on stated inputs on a stated date, with the\n"
                  "    method and the raw data published so they can be recounted. They are not averages over\n"
                  "    many runs, not certified tests, and not a prediction of what you will measure on your\n"
                  "    system. Where a measurement has been corrected after publication, the correction is stated\n"
                  "    in the article rather than silently applied."),
        ]),
        ("6. The citation endpoint at <code>/mcp</code>", [
            ("p", "The endpoint reads what a page declares about itself and returns it as a structured\n"
                  "    record. It does not verify those declarations, and a page can declare something wrong,\n"
                  "    outdated or incomplete. A record marked <code>complete: false</code> is not a reference:\n"
                  "    it may still carry a title and an author, and it must not be filed as a source on that\n"
                  "    basis. Every record is a starting point for a citation, never the finished citation —\n"
                  "    check it against the work before it enters a bibliography, a thesis or anything submitted."),
            ("p", "The endpoint is offered free of charge, without an account and without any assurance of\n"
                  "    availability, correctness or continued existence. It may be changed, limited or withdrawn\n"
                  "    at any time. No liability is accepted for consequences of relying on a record it returned\n"
                  "    — in particular not for citation errors, rejected work, or deadlines missed because it was\n"
                  "    unavailable. Where a publisher offers its own citation export, that file is authoritative\n"
                  "    and this endpoint is not."),
            ("p", "It fetches only addresses a caller supplies, as an anonymous visitor, and it reaches\n"
                  "    nothing behind a login. Using it to place load on third-party servers is not permitted;\n"
                  "    requests carry an identifying user agent so that operators can distinguish and refuse\n"
                  "    them."),
        ]),
        ("7. Third-party products and external links", [
            ("p", "Statements about other products rest exclusively on what their providers publish about\n"
                  "    themselves — manifests, listings, help pages — with the retrieval date given. Nothing was\n"
                  "    decompiled, and no statement is made about any provider's intentions or about data\n"
                  "    actually transmitted. Such declarations change; check against the live source before\n"
                  "    relying on them."),
            ("p", "External links lead to content that is not ours. Responsibility for it rests with the\n"
                  "    respective operators. Links were checked when set; no continuous monitoring takes place.\n"
                  "    On notice of an infringement, the link will be removed."),
        ]),
        ("8. Limitation of liability", [
            ("p", "To the extent permitted by law, no liability is accepted for damages arising from the use\n"
                  "    of the software or from decisions taken on the basis of content published here — in\n"
                  "    particular not for lost or incomplete data, missed deadlines, or consequences of a capture\n"
                  "    being incomplete or unavailable."),
            ("p", "<strong>This limitation does not apply</strong> to damages caused intentionally or by gross\n"
                  "    negligence, to injury to life, body or health, and wherever mandatory statutory liability\n"
                  "    applies. Those remain in force regardless of anything stated here."),
        ]),
        ("9. Changes and corrections", [
            ("p", "Content and software change. This page carries the date of its current version; earlier\n"
                  "    versions are in the repository's history. Factual errors are corrected on notice —\n"
                  "    <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">open an issue</a>, and where\n"
                  "    a published figure changes, the correction is noted in the article."),
        ]),
        ("10. Who publishes this", [
            ("p", "A private, non-commercial project by an individual, operated under a pseudonym. Nothing is\n"
                  "    sold, there is no advertising, no affiliate link and no tracking. Contact and the extent\n"
                  "    of the disclosure are described under <a href=\"../about/\">About &amp; disclosure</a>; the\n"
                  "    identity behind the pseudonym is disclosed to a legitimate legal requester."),
        ]),
    ],
}

# --------------------------------------------------------------- Deutsch ----
TEXTE["de"] = {
    "h1": "Haftungsausschluss und Hinweise",
    "standfirst": (
        "Diese Seite legt fest, wofür eingestanden wird und wofür nicht — für die hier\n"
        "    veröffentlichte Software ebenso wie für die Artikel und Messdaten dieser Seite. Sie gilt\n"
        "    für alles unter provinglab.dev und für die darüber verbreitete Erweiterung."
    ),
    "meta": "Fassung vom 3. August 2026",
    "kurz_stark": "Kurz gefasst.",
    "kurz": (
        "Software und Inhalte werden unentgeltlich und so, wie sie\n"
        "  sind, zur Verfügung gestellt. Es wird keinerlei Gewährleistung übernommen, und die Haftung\n"
        "  ist ausgeschlossen, soweit das Gesetz es zulässt. Was das Gesetz nicht auszuschließen\n"
        "  erlaubt — Vorsatz, grobe Fahrlässigkeit, Verletzung von Leben, Körper oder Gesundheit sowie\n"
        "  jede zwingende gesetzliche Haftung — bleibt unberührt, und daran ändert keine Formulierung\n"
        "  auf dieser Seite etwas."
    ),
    "punkte": [
        ("1. Die Software: keine Gewährleistung", [
            ("p", "Full Page PDF Snap steht unter der MIT-Lizenz. Deren Gewährleistungsklausel ist Teil der\n"
                  "    Lizenz und gilt uneingeschränkt — sinngemäß: Die Software wird ohne jede Gewährleistung\n"
                  "    bereitgestellt, ausdrücklich oder stillschweigend, einschließlich der Gewährleistung der\n"
                  "    Marktgängigkeit, der Eignung für einen bestimmten Zweck und der Nichtverletzung von\n"
                  "    Rechten Dritter. Maßgeblich ist der englische Wortlaut der Lizenz:"),
            ("z", None),
            ("p", "Insbesondere wird nicht zugesichert, dass die Erweiterung für einen bestimmten Zweck\n"
                  "    geeignet ist, dass sie auf einer bestimmten Seite, Browserfassung oder einem bestimmten\n"
                  "    Gerät funktioniert, oder dass sie weiterhin verfügbar bleibt."),
        ]),
        ("2. Das Ergebnis prüfen, bevor man sich darauf verlässt", [
            ("p", "Eine Aufnahme kann unvollständig sein, ohne das anzuzeigen. Seiten, die beim Scrollen\n"
                  "    nachladen, die bei anderer Fenstergröße anders aufbauen, die Inhalte hinter einer\n"
                  "    Interaktion verbergen oder sich während der Aufnahme verändern, können ein PDF ergeben,\n"
                  "    in dem etwas fehlt. Die Erweiterung kann nicht wissen, was auf der Seite hätte stehen\n"
                  "    sollen."),
            ("p", "Wo es auf den Inhalt ankommt — eine Bestätigung, eine Frist, ein Betrag, eine\n"
                  "    Transaktionszeile — öffnen Sie das fertige PDF und lesen Sie die betreffende Stelle,\n"
                  "    bevor Sie sich darauf verlassen. Diese Prüfung dauert Sekunden und ist das Einzige, was\n"
                  "    belegt, dass die Aufnahme tatsächlich enthält, was Sie brauchen."),
        ]),
        ("3. Kein qualifiziertes elektronisches Dokument", [
            ("p", "Ein durch Bildschirmaufnahme erzeugtes PDF hält fest, was ein Browser angezeigt hat. Es\n"
                  "    trägt keine qualifizierte elektronische Signatur, keinen vertrauenswürdigen Zeitstempel\n"
                  "    und keine lückenlose Nachweiskette, und es beweist für sich genommen nicht, dass eine\n"
                  "    Seite in dieser Form existiert hat. Für die eigenen Unterlagen ist es geeignet. Wo es auf\n"
                  "    Beweiskraft ankommt, ist ein dafür gebauter Dienst das richtige Mittel."),
        ]),
        ("4. Keine fachliche Beratung", [
            ("p", "Nichts von dem hier Veröffentlichten ist Rechts-, Steuer-, Finanz-, medizinische oder\n"
                  "    sonstige fachliche Beratung, und durch das Lesen entsteht kein Mandats- oder\n"
                  "    Beratungsverhältnis. Beiträge berühren Fragen mit rechtlichem Bezug — Berechtigungen,\n"
                  "    Lizenzen, Urheberrecht, den Beweiswert von Aufzeichnungen, Regeln zu Zitation und Fristen.\n"
                  "    Diese Passagen beschreiben, wie die Dinge allgemein verstanden werden; sie entscheiden\n"
                  "    Ihren Fall nicht. Die Regeln Ihrer Einrichtung und das anwendbare Recht gehen allem hier\n"
                  "    Geschriebenen vor, und für den konkreten Fall ist eine fachkundige Beratung der richtige\n"
                  "    Weg."),
        ]),
        ("5. Messungen sind Messungen, keine Zusagen", [
            ("p", "Die hier veröffentlichten Zahlen stammen aus Einzeldurchläufen mit genannten Eingaben an\n"
                  "    einem genannten Datum; Methode und Rohdaten sind veröffentlicht, damit sie nachgerechnet\n"
                  "    werden können. Es sind keine Mittelwerte über viele Läufe, keine zertifizierten Prüfungen\n"
                  "    und keine Vorhersage dessen, was Sie auf Ihrem System messen werden. Wo eine Messung nach\n"
                  "    der Veröffentlichung korrigiert wurde, steht die Korrektur im Beitrag, statt still\n"
                  "    eingearbeitet zu werden."),
        ]),
        ("6. Der Zitations-Endpunkt unter <code>/mcp</code>", [
            ("p", "Der Endpunkt liest, was eine Seite über sich selbst angibt, und gibt es als\n"
                  "    strukturierten Datensatz zurück. Er prüft diese Angaben nicht, und eine Seite kann\n"
                  "    Falsches, Veraltetes oder Unvollständiges angeben. Ein Datensatz mit\n"
                  "    <code>complete: false</code> ist keine Quellenangabe: Er kann trotzdem Titel und\n"
                  "    Verfasser tragen und darf allein deshalb nicht als Quelle abgelegt werden. Jeder\n"
                  "    Datensatz ist ein Ausgangspunkt für eine Quellenangabe, nie die fertige Angabe — vor\n"
                  "    der Aufnahme in ein Literaturverzeichnis, eine Abschlussarbeit oder eine Einreichung\n"
                  "    am Werk gegenprüfen."),
            ("p", "Der Endpunkt wird unentgeltlich, ohne Konto und ohne jede Zusage zu Verfügbarkeit,\n"
                  "    Richtigkeit oder Fortbestand bereitgestellt. Er kann jederzeit geändert, begrenzt oder\n"
                  "    eingestellt werden. Für Folgen des Vertrauens auf einen zurückgegebenen Datensatz wird\n"
                  "    keine Haftung übernommen — insbesondere nicht für fehlerhafte Zitationen, zurückgewiesene\n"
                  "    Arbeiten oder versäumte Fristen wegen Nichterreichbarkeit. Wo ein Verlag einen eigenen\n"
                  "    Zitations-Export anbietet, ist diese Datei maßgeblich und nicht dieser Endpunkt."),
            ("p", "Er ruft ausschließlich Adressen ab, die ein Aufrufer nennt, als anonymer Besucher, und\n"
                  "    erreicht nichts hinter einer Anmeldung. Ihn zu verwenden, um fremde Server zu belasten,\n"
                  "    ist nicht gestattet; Abrufe tragen ein erkennbares Kennzeichen, damit Betreiber sie\n"
                  "    unterscheiden und abweisen können."),
        ]),
        ("7. Fremde Produkte und externe Verweise", [
            ("p", "Aussagen über andere Produkte stützen sich ausschließlich auf das, was deren Anbieter\n"
                  "    selbst veröffentlichen — Manifeste, Store-Einträge, Hilfeseiten — jeweils mit Abrufdatum.\n"
                  "    Es wurde nichts dekompiliert, und es wird keine Aussage über Absichten eines Anbieters\n"
                  "    oder über tatsächlich übertragene Daten getroffen. Solche Angaben ändern sich; prüfen Sie\n"
                  "    vor einer Verwendung gegen die Live-Quelle."),
            ("p", "Externe Verweise führen zu Inhalten, die nicht von uns stammen. Für sie sind die\n"
                  "    jeweiligen Betreiber verantwortlich. Die Verweise wurden bei der Aufnahme geprüft; eine\n"
                  "    fortlaufende Überwachung findet nicht statt. Bei Kenntnis einer Rechtsverletzung wird der\n"
                  "    Verweis entfernt."),
        ]),
        ("8. Haftungsbegrenzung", [
            ("p", "Soweit gesetzlich zulässig, wird keine Haftung für Schäden übernommen, die aus der\n"
                  "    Verwendung der Software oder aus Entscheidungen aufgrund hier veröffentlichter Inhalte\n"
                  "    entstehen — insbesondere nicht für verlorene oder unvollständige Daten, versäumte Fristen\n"
                  "    oder Folgen einer unvollständigen oder nicht verfügbaren Aufnahme."),
            ("p", "<strong>Diese Begrenzung gilt nicht</strong> für vorsätzlich oder grob fahrlässig\n"
                  "    verursachte Schäden, für die Verletzung von Leben, Körper oder Gesundheit sowie überall\n"
                  "    dort, wo zwingende gesetzliche Haftung greift. Diese bleibt unabhängig von allem hier\n"
                  "    Gesagten bestehen."),
        ]),
        ("9. Änderungen und Korrekturen", [
            ("p", "Inhalte und Software ändern sich. Diese Seite trägt das Datum ihrer aktuellen Fassung;\n"
                  "    frühere Fassungen stehen in der Historie des Repositorys. Sachliche Fehler werden bei\n"
                  "    Kenntnis berichtigt — <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">ein\n"
                  "    Issue eröffnen</a>; ändert sich eine veröffentlichte Zahl, wird die Korrektur im Beitrag\n"
                  "    vermerkt."),
        ]),
        ("10. Wer das veröffentlicht", [
            ("p", "Ein privates, nicht kommerzielles Projekt einer Einzelperson, betrieben unter einem\n"
                  "    Pseudonym. Es wird nichts verkauft, es gibt keine Werbung, keine Affiliate-Verweise und\n"
                  "    kein Tracking. Kontakt und Umfang der Offenlegung stehen unter\n"
                  "    <a href=\"../about/\">Offenlegung</a>; die Identität hinter dem Pseudonym wird einer\n"
                  "    berechtigten rechtlichen Anfrage gegenüber offengelegt."),
        ]),
    ],
}

# --------------------------------------------------------------- Español ----
TEXTE["es"] = {
    "h1": "Aviso legal y limitación de responsabilidad",
    "standfirst": (
        "Esta página establece por qué se responde y por qué no — tanto por el software publicado\n"
        "    aquí como por los artículos y datos de medición de este sitio. Se aplica a todo lo que se\n"
        "    encuentra bajo provinglab.dev y a la extensión distribuida desde él."
    ),
    "meta": "Versión del 3 de agosto de 2026",
    "kurz_stark": "En resumen.",
    "kurz": (
        "El software y los contenidos se ofrecen de forma gratuita y tal como están. No se otorga\n"
        "  garantía alguna, y la responsabilidad queda excluida en la medida en que la ley lo permite.\n"
        "  Lo que la ley no permite excluir — el dolo, la negligencia grave, las lesiones a la vida, la\n"
        "  integridad física o la salud, así como cualquier responsabilidad legal imperativa — no se ve\n"
        "  afectado, y ninguna formulación de esta página lo modifica."
    ),
    "punkte": [
        ("1. El software: sin garantía", [
            ("p", "Full Page PDF Snap se publica bajo la licencia MIT. Su cláusula de garantía forma parte\n"
                  "    de la licencia y se aplica íntegramente — en síntesis: el software se proporciona sin\n"
                  "    garantía de ningún tipo, expresa o implícita, incluidas las garantías de comerciabilidad,\n"
                  "    idoneidad para un fin determinado y no infracción. El texto vinculante es la versión\n"
                  "    inglesa de la licencia:"),
            ("z", None),
            ("p", "En particular, no se asegura que la extensión sea apta para un fin específico, que\n"
                  "    funcione en una página, versión de navegador o dispositivo concretos, ni que siga\n"
                  "    estando disponible."),
        ]),
        ("2. Compruebe el resultado antes de confiar en él", [
            ("p", "Una captura puede estar incompleta sin indicarlo. Las páginas que cargan contenido al\n"
                  "    desplazarse, que se representan de forma distinta con otro tamaño de ventana, que\n"
                  "    ocultan contenido tras una interacción o que cambian mientras se realiza la captura\n"
                  "    pueden producir un PDF al que le falte algo. La extensión no tiene forma de saber qué\n"
                  "    debía contener la página."),
            ("p", "Cuando el contenido importa — una confirmación, un plazo, un importe, una línea de\n"
                  "    transacción — abra el PDF terminado y lea la parte correspondiente antes de confiar en\n"
                  "    él. Esa comprobación lleva segundos y es lo único que demuestra que la captura contiene\n"
                  "    realmente lo que usted necesita."),
        ]),
        ("3. No es un documento electrónico cualificado", [
            ("p", "Un PDF generado mediante captura de pantalla registra lo que mostró un navegador. No\n"
                  "    lleva firma electrónica cualificada, ni sello de tiempo de confianza, ni cadena de\n"
                  "    custodia, y por sí solo no demuestra que una página existiera en esa forma. Es adecuado\n"
                  "    para sus propios registros. Cuando se requiere valor probatorio, el instrumento\n"
                  "    adecuado es un servicio creado para ese fin."),
        ]),
        ("4. No es asesoramiento profesional", [
            ("p", "Nada de lo publicado aquí constituye asesoramiento jurídico, fiscal, financiero, médico\n"
                  "    ni de ninguna otra índole profesional, y su lectura no crea relación de cliente alguna.\n"
                  "    Los artículos abordan cuestiones con dimensión jurídica — permisos, licencias, derechos\n"
                  "    de autor, el valor probatorio de un registro, normas sobre citación y plazos. Esos\n"
                  "    pasajes describen cómo se suelen entender las cosas; no resuelven su caso. Las normas\n"
                  "    institucionales y la legislación aplicable prevalecen sobre cualquier cosa escrita aquí,\n"
                  "    y para una situación concreta la vía adecuada es el asesoramiento cualificado."),
        ]),
        ("5. Las mediciones son mediciones, no garantías", [
            ("p", "Las cifras publicadas aquí proceden de ejecuciones únicas con las entradas indicadas en\n"
                  "    la fecha indicada, con el método y los datos brutos publicados para que puedan\n"
                  "    recontarse. No son promedios de muchas ejecuciones, ni pruebas certificadas, ni una\n"
                  "    predicción de lo que usted medirá en su sistema. Cuando una medición se ha corregido tras\n"
                  "    su publicación, la corrección se indica en el artículo en lugar de aplicarse en silencio."),
        ]),
        ("6. El punto de acceso de citación en <code>/mcp</code>", [
            ("p", "El punto de acceso lee lo que una página declara sobre sí misma y lo devuelve como un\n"
                  "    registro estructurado. No verifica esas declaraciones, y una página puede declarar algo\n"
                  "    erróneo, obsoleto o incompleto. Un registro marcado como <code>complete: false</code> no\n"
                  "    es una referencia: puede llevar título y autor, y no debe archivarse como fuente por ese\n"
                  "    solo motivo. Cada registro es un punto de partida para una cita, nunca la cita terminada —\n"
                  "    compruébelo contra la obra antes de que entre en una bibliografía, una tesis o cualquier\n"
                  "    trabajo que se presente."),
            ("p", "El punto de acceso se ofrece gratuitamente, sin cuenta y sin ninguna garantía de\n"
                  "    disponibilidad, corrección o continuidad. Puede modificarse, limitarse o retirarse en\n"
                  "    cualquier momento. No se acepta responsabilidad por las consecuencias de confiar en un\n"
                  "    registro devuelto — en particular no por errores de citación, trabajos rechazados o plazos\n"
                  "    perdidos por falta de disponibilidad. Cuando una editorial ofrece su propia exportación de\n"
                  "    citas, ese archivo es el que prevalece y no este punto de acceso."),
            ("p", "Solo obtiene las direcciones que le indica quien lo invoca, como visitante anónimo, y\n"
                  "    no alcanza nada que esté tras un inicio de sesión. No está permitido usarlo para cargar\n"
                  "    servidores de terceros; las solicitudes llevan un agente de usuario identificable para que\n"
                  "    los operadores puedan distinguirlas y rechazarlas."),
        ]),
        ("7. Productos de terceros y enlaces externos", [
            ("p", "Las afirmaciones sobre otros productos se basan exclusivamente en lo que sus\n"
                  "    proveedores publican sobre sí mismos — manifiestos, fichas de las tiendas, páginas de\n"
                  "    ayuda — con la fecha de consulta indicada. No se ha descompilado nada y no se afirma nada\n"
                  "    sobre las intenciones de ningún proveedor ni sobre los datos realmente transmitidos. Esas\n"
                  "    declaraciones cambian; contrástelas con la fuente en vivo antes de confiar en ellas."),
            ("p", "Los enlaces externos conducen a contenidos que no son nuestros. La responsabilidad por\n"
                  "    ellos recae en los operadores respectivos. Los enlaces se comprobaron al incluirlos; no\n"
                  "    se realiza una supervisión continua. Ante la notificación de una infracción, el enlace se\n"
                  "    retirará."),
        ]),
        ("8. Limitación de responsabilidad", [
            ("p", "En la medida permitida por la ley, no se acepta responsabilidad por daños derivados del\n"
                  "    uso del software o de decisiones tomadas sobre la base de contenidos publicados aquí —\n"
                  "    en particular no por datos perdidos o incompletos, plazos incumplidos o consecuencias de\n"
                  "    una captura incompleta o no disponible."),
            ("p", "<strong>Esta limitación no se aplica</strong> a los daños causados dolosamente o por\n"
                  "    negligencia grave, a las lesiones a la vida, la integridad física o la salud, ni en los\n"
                  "    casos en que exista responsabilidad legal imperativa. Estos supuestos siguen vigentes con\n"
                  "    independencia de lo aquí expuesto."),
        ]),
        ("9. Cambios y correcciones", [
            ("p", "Los contenidos y el software cambian. Esta página lleva la fecha de su versión actual;\n"
                  "    las versiones anteriores constan en el historial del repositorio. Los errores de hecho\n"
                  "    se corrigen cuando se tiene conocimiento de ellos —\n"
                  "    <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">abra una incidencia</a> — y\n"
                  "    cuando cambia una cifra publicada, la corrección se anota en el artículo."),
        ]),
        ("10. Quién publica esto", [
            ("p", "Un proyecto privado y no comercial de una persona, operado bajo un seudónimo. No se\n"
                  "    vende nada, no hay publicidad, ni enlaces de afiliado, ni seguimiento. El contacto y el\n"
                  "    alcance de la información publicada se describen en\n"
                  "    <a href=\"../about/\">Información y divulgación</a>; la identidad tras el seudónimo se revela\n"
                  "    ante una solicitud legal legítima."),
        ]),
    ],
}

# --------------------------------------------------------------- Français ---
TEXTE["fr"] = {
    "h1": "Clause de non-responsabilité et limitation de responsabilité",
    "standfirst": (
        "Cette page précise ce qui est garanti et ce qui ne l'est pas — pour le logiciel publié ici\n"
        "    comme pour les articles et les données de mesure de ce site. Elle s'applique à tout ce qui\n"
        "    se trouve sous provinglab.dev et à l'extension qui y est distribuée."
    ),
    "meta": "Version du 3 août 2026",
    "kurz_stark": "En bref.",
    "kurz": (
        "Le logiciel et les contenus sont fournis gratuitement et en l'état. Aucune garantie d'aucune\n"
        "  sorte n'est accordée, et la responsabilité est exclue dans la mesure où la loi le permet. Ce\n"
        "  que la loi ne permet pas d'exclure — le dol, la faute lourde, l'atteinte à la vie, à\n"
        "  l'intégrité corporelle ou à la santé, ainsi que toute responsabilité légale impérative —\n"
        "  demeure intact, et aucune formulation de cette page n'y change rien."
    ),
    "punkte": [
        ("1. Le logiciel : aucune garantie", [
            ("p", "Full Page PDF Snap est publié sous licence MIT. Sa clause de garantie fait partie de la\n"
                  "    licence et s'applique intégralement — en substance : le logiciel est fourni sans aucune\n"
                  "    garantie, expresse ou implicite, y compris les garanties de qualité marchande,\n"
                  "    d'adéquation à un usage particulier et d'absence de contrefaçon. Seul le texte anglais de\n"
                  "    la licence fait foi :"),
            ("z", None),
            ("p", "En particulier, il n'est pas garanti que l'extension convienne à un usage précis,\n"
                  "    qu'elle fonctionne sur une page, une version de navigateur ou un appareil donnés, ni\n"
                  "    qu'elle reste disponible."),
        ]),
        ("2. Vérifiez le résultat avant de vous y fier", [
            ("p", "Une capture peut être incomplète sans l'indiquer. Les pages qui se chargent au\n"
                  "    défilement, qui s'affichent différemment selon la taille de la fenêtre, qui masquent du\n"
                  "    contenu derrière une interaction ou qui changent pendant la capture peuvent produire un\n"
                  "    PDF auquel il manque quelque chose. L'extension n'a aucun moyen de savoir ce que la page\n"
                  "    était censée contenir."),
            ("p", "Lorsque le contenu compte — une confirmation, un délai, un montant, une ligne de\n"
                  "    transaction — ouvrez le PDF terminé et lisez le passage concerné avant de vous y fier.\n"
                  "    Cette vérification prend quelques secondes et est la seule chose qui établit que la\n"
                  "    capture contient réellement ce dont vous avez besoin."),
        ]),
        ("3. Pas un document électronique qualifié", [
            ("p", "Un PDF produit par capture d'écran enregistre ce qu'un navigateur a affiché. Il ne\n"
                  "    comporte ni signature électronique qualifiée, ni horodatage de confiance, ni chaîne de\n"
                  "    conservation, et il ne prouve pas à lui seul qu'une page a existé sous cette forme. Il\n"
                  "    convient à vos propres archives. Lorsqu'une valeur probante est requise, un service conçu\n"
                  "    à cet effet est l'instrument approprié."),
        ]),
        ("4. Aucun conseil professionnel", [
            ("p", "Rien de ce qui est publié ici ne constitue un conseil juridique, fiscal, financier,\n"
                  "    médical ou tout autre conseil professionnel, et sa lecture ne crée aucune relation de\n"
                  "    mandat. Les articles abordent des questions à dimension juridique — autorisations,\n"
                  "    licences, droit d'auteur, valeur probante d'un enregistrement, règles de citation et\n"
                  "    délais. Ces passages décrivent comment les choses sont généralement comprises ; ils ne\n"
                  "    tranchent pas votre cas. Les règles de votre institution et le droit applicable priment sur\n"
                  "    tout ce qui est écrit ici, et pour une situation précise, un conseil qualifié est la bonne\n"
                  "    voie."),
        ]),
        ("5. Les mesures sont des mesures, pas des garanties", [
            ("p", "Les chiffres publiés ici proviennent d'exécutions uniques sur des entrées indiquées à\n"
                  "    une date indiquée, la méthode et les données brutes étant publiées afin de pouvoir être\n"
                  "    recomptées. Ce ne sont ni des moyennes sur de nombreuses exécutions, ni des tests\n"
                  "    certifiés, ni une prédiction de ce que vous mesurerez sur votre système. Lorsqu'une mesure\n"
                  "    a été corrigée après publication, la correction est indiquée dans l'article plutôt\n"
                  "    qu'appliquée en silence."),
        ]),
        ("6. Le point d'accès de citation sous <code>/mcp</code>", [
            ("p", "Le point d'accès lit ce qu'une page déclare sur elle-même et le renvoie sous forme\n"
                  "    d'enregistrement structuré. Il ne vérifie pas ces déclarations, et une page peut déclarer\n"
                  "    quelque chose de faux, d'obsolète ou d'incomplet. Un enregistrement marqué\n"
                  "    <code>complete: false</code> n'est pas une référence : il peut néanmoins porter un titre et\n"
                  "    un auteur, et il ne doit pas être classé comme source sur cette seule base. Chaque\n"
                  "    enregistrement est un point de départ pour une citation, jamais la citation achevée —\n"
                  "    vérifiez-le sur l'œuvre avant qu'il n'entre dans une bibliographie, une thèse ou tout\n"
                  "    document soumis."),
            ("p", "Le point d'accès est proposé gratuitement, sans compte et sans aucune garantie de\n"
                  "    disponibilité, d'exactitude ou de pérennité. Il peut être modifié, limité ou retiré à tout\n"
                  "    moment. Aucune responsabilité n'est acceptée pour les conséquences de la confiance accordée\n"
                  "    à un enregistrement renvoyé — notamment pas pour des erreurs de citation, des travaux rejetés\n"
                  "    ou des délais manqués par indisponibilité. Lorsqu'un éditeur propose son propre export de\n"
                  "    citations, c'est ce fichier qui fait foi, et non ce point d'accès."),
            ("p", "Il ne récupère que les adresses fournies par l'appelant, en visiteur anonyme, et\n"
                  "    n'atteint rien derrière une connexion. L'utiliser pour charger des serveurs tiers n'est pas\n"
                  "    permis ; les requêtes portent un agent utilisateur identifiable afin que les opérateurs\n"
                  "    puissent les distinguer et les refuser."),
        ]),
        ("7. Produits tiers et liens externes", [
            ("p", "Les affirmations concernant d'autres produits reposent exclusivement sur ce que leurs\n"
                  "    fournisseurs publient eux-mêmes — manifestes, fiches des boutiques, pages d'aide — avec\n"
                  "    la date de consultation indiquée. Rien n'a été décompilé, et aucune affirmation n'est faite\n"
                  "    sur les intentions d'un fournisseur ni sur les données effectivement transmises. Ces\n"
                  "    déclarations évoluent ; vérifiez-les sur la source en ligne avant de vous y fier."),
            ("p", "Les liens externes mènent à des contenus qui ne sont pas les nôtres. La responsabilité\n"
                  "    en incombe aux opérateurs respectifs. Les liens ont été vérifiés lors de leur insertion ;\n"
                  "    aucune surveillance continue n'a lieu. En cas de connaissance d'une infraction, le lien\n"
                  "    sera retiré."),
        ]),
        ("8. Limitation de responsabilité", [
            ("p", "Dans la mesure permise par la loi, aucune responsabilité n'est acceptée pour les\n"
                  "    dommages résultant de l'utilisation du logiciel ou de décisions prises sur la base des\n"
                  "    contenus publiés ici — notamment pas pour des données perdues ou incomplètes, des délais\n"
                  "    manqués ou les conséquences d'une capture incomplète ou indisponible."),
            ("p", "<strong>Cette limitation ne s'applique pas</strong> aux dommages causés\n"
                  "    intentionnellement ou par faute lourde, aux atteintes à la vie, à l'intégrité corporelle\n"
                  "    ou à la santé, ni partout où une responsabilité légale impérative s'applique. Celles-ci\n"
                  "    demeurent en vigueur indépendamment de tout ce qui est indiqué ici."),
        ]),
        ("9. Modifications et corrections", [
            ("p", "Les contenus et le logiciel évoluent. Cette page porte la date de sa version actuelle ;\n"
                  "    les versions antérieures figurent dans l'historique du dépôt. Les erreurs factuelles sont\n"
                  "    corrigées dès qu'elles sont connues —\n"
                  "    <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">ouvrez un ticket</a> — et\n"
                  "    lorsqu'un chiffre publié change, la correction est notée dans l'article."),
        ]),
        ("10. Qui publie ceci", [
            ("p", "Un projet privé et non commercial d'une personne physique, exploité sous un pseudonyme.\n"
                  "    Rien n'est vendu, il n'y a ni publicité, ni lien d'affiliation, ni suivi. Le contact et\n"
                  "    l'étendue des informations publiées sont décrits sous\n"
                  "    <a href=\"../about/\">À propos et transparence</a> ; l'identité derrière le pseudonyme est\n"
                  "    communiquée à toute personne présentant une demande légale légitime."),
        ]),
    ],
}

# --------------------------------------------------------------- Italiano ---
TEXTE["it"] = {
    "h1": "Esclusione e limitazione di responsabilità",
    "standfirst": (
        "Questa pagina stabilisce per cosa si risponde e per cosa no — per il software qui pubblicato\n"
        "    come per gli articoli e i dati di misurazione di questo sito. Vale per tutto ciò che si\n"
        "    trova sotto provinglab.dev e per l'estensione da esso distribuita."
    ),
    "meta": "Versione del 3 agosto 2026",
    "kurz_stark": "In sintesi.",
    "kurz": (
        "Il software e i contenuti sono forniti gratuitamente e così come sono. Non si concede alcuna\n"
        "  garanzia di alcun tipo e la responsabilità è esclusa nei limiti consentiti dalla legge. Ciò\n"
        "  che la legge non consente di escludere — il dolo, la colpa grave, le lesioni alla vita,\n"
        "  all'integrità fisica o alla salute, nonché ogni responsabilità legale inderogabile — resta\n"
        "  impregiudicato, e nessuna formulazione di questa pagina lo modifica."
    ),
    "punkte": [
        ("1. Il software: nessuna garanzia", [
            ("p", "Full Page PDF Snap è pubblicato con licenza MIT. La clausola di garanzia della licenza\n"
                  "    ne fa parte e si applica integralmente — in sintesi: il software è fornito senza alcuna\n"
                  "    garanzia, espressa o implicita, comprese le garanzie di commerciabilità, idoneità a uno\n"
                  "    scopo particolare e non violazione di diritti di terzi. Fa fede il testo inglese della\n"
                  "    licenza:"),
            ("z", None),
            ("p", "In particolare, non si assicura che l'estensione sia idonea a uno scopo specifico, che\n"
                  "    funzioni su una determinata pagina, versione del browser o dispositivo, né che resti\n"
                  "    disponibile."),
        ]),
        ("2. Verificare il risultato prima di farvi affidamento", [
            ("p", "Una cattura può essere incompleta senza segnalarlo. Le pagine che caricano contenuti\n"
                  "    durante lo scorrimento, che si presentano diversamente con un'altra dimensione della\n"
                  "    finestra, che nascondono contenuti dietro un'interazione o che cambiano durante la\n"
                  "    cattura possono produrre un PDF a cui manca qualcosa. L'estensione non ha modo di sapere\n"
                  "    cosa avrebbe dovuto contenere la pagina."),
            ("p", "Quando il contenuto conta — una conferma, una scadenza, un importo, una riga di\n"
                  "    transazione — aprite il PDF finito e leggete la parte interessata prima di farvi\n"
                  "    affidamento. Questa verifica richiede pochi secondi ed è l'unica cosa che dimostra che la\n"
                  "    cattura contiene effettivamente ciò che vi serve."),
        ]),
        ("3. Non è un documento elettronico qualificato", [
            ("p", "Un PDF prodotto mediante cattura dello schermo registra ciò che un browser ha\n"
                  "    visualizzato. Non reca una firma elettronica qualificata, né una marca temporale\n"
                  "    attendibile, né una catena di custodia, e non prova di per sé che una pagina sia esistita\n"
                  "    in quella forma. È adatto alla propria documentazione. Dove occorre valore probatorio, lo\n"
                  "    strumento giusto è un servizio costruito a tale scopo."),
        ]),
        ("4. Nessuna consulenza professionale", [
            ("p", "Nulla di quanto qui pubblicato costituisce consulenza legale, fiscale, finanziaria,\n"
                  "    medica o di altra natura professionale, e dalla lettura non nasce alcun rapporto di\n"
                  "    mandato. Gli articoli toccano questioni con profili giuridici — autorizzazioni, licenze,\n"
                  "    diritto d'autore, valore probatorio di una registrazione, regole su citazioni e scadenze.\n"
                  "    Questi passaggi descrivono come le cose sono generalmente intese; non decidono il vostro\n"
                  "    caso. Le regole della vostra istituzione e il diritto applicabile prevalgono su quanto qui\n"
                  "    scritto, e per una situazione concreta la via giusta è la consulenza qualificata."),
        ]),
        ("5. Le misurazioni sono misurazioni, non garanzie", [
            ("p", "Le cifre qui pubblicate derivano da singole esecuzioni con gli input indicati alla data\n"
                  "    indicata, con metodo e dati grezzi pubblicati affinché possano essere ricalcolate. Non\n"
                  "    sono medie su molte esecuzioni, né test certificati, né una previsione di ciò che\n"
                  "    misurerete sul vostro sistema. Dove una misurazione è stata corretta dopo la pubblicazione,\n"
                  "    la correzione è indicata nell'articolo anziché applicata in silenzio."),
        ]),
        ("6. L'endpoint di citazione sotto <code>/mcp</code>", [
            ("p", "L'endpoint legge ciò che una pagina dichiara di sé e lo restituisce come record\n"
                  "    strutturato. Non verifica tali dichiarazioni, e una pagina può dichiarare qualcosa di\n"
                  "    errato, obsoleto o incompleto. Un record contrassegnato con <code>complete: false</code>\n"
                  "    non è un riferimento: può comunque riportare titolo e autore e non deve essere archiviato\n"
                  "    come fonte per questo solo motivo. Ogni record è un punto di partenza per una citazione, mai\n"
                  "    la citazione finita — verificatelo sull'opera prima che entri in una bibliografia, in una\n"
                  "    tesi o in qualsiasi documento presentato."),
            ("p", "L'endpoint è offerto gratuitamente, senza account e senza alcuna assicurazione di\n"
                  "    disponibilità, correttezza o continuità. Può essere modificato, limitato o ritirato in\n"
                  "    qualsiasi momento. Non si accetta alcuna responsabilità per le conseguenze dell'affidamento\n"
                  "    su un record restituito — in particolare non per errori di citazione, lavori respinti o\n"
                  "    scadenze mancate per indisponibilità. Dove un editore offre una propria esportazione di\n"
                  "    citazioni, quel file è quello che fa fede e non questo endpoint."),
            ("p", "Recupera solo gli indirizzi forniti dal chiamante, come visitatore anonimo, e non\n"
                  "    raggiunge nulla dietro un accesso. Non è consentito usarlo per caricare server di terzi;\n"
                  "    le richieste recano uno user agent riconoscibile affinché gli operatori possano\n"
                  "    distinguerle e rifiutarle."),
        ]),
        ("7. Prodotti di terzi e collegamenti esterni", [
            ("p", "Le affermazioni su altri prodotti si basano esclusivamente su ciò che i rispettivi\n"
                  "    fornitori pubblicano di sé — manifest, schede degli store, pagine di aiuto — con la data\n"
                  "    di consultazione indicata. Nulla è stato decompilato e non si afferma nulla sulle\n"
                  "    intenzioni di alcun fornitore né sui dati effettivamente trasmessi. Tali dichiarazioni\n"
                  "    cambiano; verificatele sulla fonte aggiornata prima di farvi affidamento."),
            ("p", "I collegamenti esterni conducono a contenuti che non sono nostri. La responsabilità\n"
                  "    spetta ai rispettivi gestori. I collegamenti sono stati verificati al momento\n"
                  "    dell'inserimento; non avviene alcun monitoraggio continuo. In caso di notizia di una\n"
                  "    violazione, il collegamento sarà rimosso."),
        ]),
        ("8. Limitazione di responsabilità", [
            ("p", "Nei limiti consentiti dalla legge, non si accetta alcuna responsabilità per danni\n"
                  "    derivanti dall'uso del software o da decisioni prese sulla base dei contenuti qui\n"
                  "    pubblicati — in particolare non per dati persi o incompleti, scadenze mancate o\n"
                  "    conseguenze di una cattura incompleta o non disponibile."),
            ("p", "<strong>Questa limitazione non si applica</strong> ai danni causati dolosamente o per\n"
                  "    colpa grave, alle lesioni alla vita, all'integrità fisica o alla salute, e ovunque\n"
                  "    sussista una responsabilità legale inderogabile. Queste restano in vigore\n"
                  "    indipendentemente da quanto qui indicato."),
        ]),
        ("9. Modifiche e correzioni", [
            ("p", "Contenuti e software cambiano. Questa pagina riporta la data della sua versione\n"
                  "    attuale; le versioni precedenti sono nella cronologia del repository. Gli errori di fatto\n"
                  "    vengono corretti non appena se ne ha conoscenza —\n"
                  "    <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">aprite una segnalazione</a> —\n"
                  "    e quando cambia una cifra pubblicata, la correzione viene annotata nell'articolo."),
        ]),
        ("10. Chi pubblica questo sito", [
            ("p", "Un progetto privato e non commerciale di una singola persona, gestito sotto pseudonimo.\n"
                  "    Non si vende nulla, non vi sono pubblicità, link di affiliazione né tracciamento.\n"
                  "    Contatti e portata delle informazioni pubblicate sono descritti alla pagina\n"
                  "    <a href=\"../about/\">Informazioni e trasparenza</a>; l'identità dietro lo pseudonimo viene\n"
                  "    rivelata a chi presenti una legittima richiesta legale."),
        ]),
    ],
}

# ------------------------------------------------------------------ 日本語 ---
TEXTE["ja"] = {
    "h1": "免責事項および責任の制限",
    "standfirst": (
        "このページでは、ここで公開されているソフトウェアならびに本サイトの記事や測定データについて、何を保証し、何を保証しないかを定めています。provinglab.dev 配下のすべてと、そこから配布される拡張機能に適用されます。"
    ),
    "meta": "2026年8月3日版",
    "kurz_stark": "要点。",
    "kurz": (
        "ソフトウェアおよびコンテンツは無償で、現状のまま提供されます。いかなる種類の保証も行わず、法律が認める範囲で責任を免責します。法律が免責を認めないもの——故意、重過失、生命・身体・健康への侵害、および強行法規上の責任——は影響を受けず、このページのいかなる表現もそれを変更しません。"
    ),
    "punkte": [
        ("1. ソフトウェア：保証なし", [
            ("p", "Full Page PDF Snap は MIT ライセンスの下で公開されています。同ライセンスの保証条項はライセンスの一部であり、全面的に適用されます。要旨：本ソフトウェアは、商品性、特定目的への適合性、権利非侵害の保証を含め、明示・黙示を問わずいかなる保証もなく提供されます。正文はライセンスの英語原文です："),
            ("z", None),
            ("p", "特に、拡張機能が特定の目的に適すること、特定のページ・ブラウザバージョン・デバイスで動作すること、あるいは今後も提供され続けることは、保証されません。"),
        ]),
        ("2. 依拠する前に結果を確認してください", [
            ("p", "キャプチャは、その旨表示されないまま不完全な場合があります。スクロールで読み込むページ、ウィンドウサイズによって表示が変わるページ、操作の背後にコンテンツを隠すページ、キャプチャ中に変化するページは、いずれも何かが欠けた PDF を生じさせることがあります。拡張機能は、ページに何が含まれるべきだったかを知る術を持ちません。"),
            ("p", "内容が重要な場合——確認書、期限、金額、取引明細行など——完成した PDF を開き、依拠する前に該当箇所をお読みください。この確認は数秒で済み、キャプチャに必要な内容が実際に含まれていることを裏付ける唯一の手段です。"),
        ]),
        ("3. 適格電子文書ではありません", [
            ("p", "画面キャプチャで生成された PDF は、ブラウザが表示した内容を記録したものです。適格電子署名、信頼できるタイムスタンプ、証拠保全の連鎖のいずれも備えておらず、それ自体ではページがその形で存在したことを証明しません。ご自身の記録用には適しています。証拠能力が求められる場面では、その目的のために構築されたサービスが適切な手段です。"),
        ]),
        ("4. 専門的助言ではありません", [
            ("p", "ここで公開されている内容は、法律・税務・金融・医療その他いかなる専門的助言でもなく、閲覧によって委任関係や助言関係は発生しません。記事は法的側面を持つ問題——権限、ライセンス、著作権、記録の証拠価値、引用や期限に関する規則——に触れます。それらの記述は一般的な理解を説明するものであり、個別の事案を決するものではありません。所属機関の規則および適用法がここに書かれたすべてに優先し、具体的な状況については資格のある専門家への相談が適切な道です。"),
        ]),
        ("5. 測定値は測定値であり、保証ではありません", [
            ("p", "ここで公開される数値は、示された入力について示された日付に行われた単一の実行に由来し、再計算できるよう手法と生データが公開されています。多数回の平均ではなく、認定試験でもなく、お使いのシステムで測定される値の予測でもありません。公開後に測定値が訂正された場合、訂正は黙って適用されるのではなく、記事内に明記されます。"),
        ]),
        ("6. <code>/mcp</code> の引用エンドポイント", [
            ("p", "このエンドポイントは、ページが自身について宣言している内容を読み取り、構造化レコードとして返します。それらの宣言を検証するものではなく、ページは誤った内容、古い内容、不完全な内容を宣言していることがあります。<code>complete: false</code> と付されたレコードは参照情報ではありません。タイトルや著者を含んでいることがあっても、そのことをもって出典として保管してはなりません。すべてのレコードは引用の出発点であり、完成した引用ではありません——文献目録、学位論文、提出物に入れる前に、原資料と照合してください。"),
            ("p", "このエンドポイントは無償で、アカウント不要、可用性・正確性・継続性についてのいかなる保証もなく提供されます。いつでも変更・制限・廃止され得ます。返されたレコードに依拠したことの結果——特に引用ミス、提出物の不受理、利用不能による期限遅過——について責任を負いません。出版社が独自の引用エクスポートを提供している場合、そのファイルが正式なものであり、このエンドポイントではありません。"),
            ("p", "呼び出し元が指定したアドレスのみを匿名の訪問者として取得し、ログインの先にあるものには届きません。第三者のサーバーに負荷をかける目的での利用は許可されません。運営者が識別・拒否できるよう、リクエストには識別可能なユーザーエージェントが付されています。"),
        ]),
        ("7. 第三者製品と外部リンク", [
            ("p", "他製品に関する記述は、提供元が自ら公開している情報——マニフェスト、ストア掲載情報、ヘルプページ——にのみ依拠し、取得日を明記しています。逆コンパイルは行っておらず、提供元の意図や実際に送信されるデータについての断定もしていません。こうした宣言は変わります。依拠する前に最新の一次情報で確認してください。"),
            ("p", "外部リンクは当方のものではないコンテンツへつながります。その責任は各運営者にあります。リンクは設定時に確認していますが、継続的な監視は行っていません。権利侵害の連絡を受けた場合、リンクは削除されます。"),
        ]),
        ("8. 責任の制限", [
            ("p", "法律が認める範囲で、ソフトウェアの使用またはここで公開されたコンテンツに基づく判断から生じる損害——特にデータの喪失・不完全、期限遅過、キャプチャの不完全または利用不能による結果——について責任を負いません。"),
            ("p", "<strong>この制限は適用されません</strong>：故意または重過失による損害、生命・身体・健康への侵害、および強行法規上の責任が及ぶすべての場合。これらはここに記された内容にかかわらず存続します。"),
        ]),
        ("9. 変更と訂正", [
            ("p", "コンテンツとソフトウェアは変化します。このページには現行版の日付が記され、過去の版はリポジトリの履歴にあります。事実誤認は判明次第訂正します——<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">Issue を立ててください</a>。公開済みの数値が変わる場合、訂正は記事内に記されます。"),
        ]),
        ("10. 公開者について", [
            ("p", "個人による私的かつ非営利のプロジェクトで、仮名で運営されています。販売はなく、広告・アフィリエイトリンク・トラッキングもありません。連絡先と開示の範囲は <a href=\"../about/\">概要と開示</a> に記しています。仮名の背後にある身分は、正当な法的請求者に開示されます。"),
        ]),
    ],
}

# --------------------------------------------------------------- Português --
TEXTE["pt-BR"] = {
    "h1": "Aviso legal e limitação de responsabilidade",
    "standfirst": (
        "Esta página define pelo que se responde e pelo que não — tanto pelo software publicado aqui\n"
        "    quanto pelos artigos e dados de medição deste site. Aplica-se a tudo o que está sob\n"
        "    provinglab.dev e à extensão distribuída a partir dele."
    ),
    "meta": "Versão de 3 de agosto de 2026",
    "kurz_stark": "Em resumo.",
    "kurz": (
        "O software e os conteúdos são fornecidos gratuitamente e como estão. Não se concede garantia\n"
        "  de espécie alguma, e a responsabilidade é excluída na medida permitida por lei. O que a lei\n"
        "  não permite excluir — dolo, culpa grave, lesão à vida, ao corpo ou à saúde, bem como qualquer\n"
        "  responsabilidade legal imperativa — permanece inalterado, e nenhuma redação desta página muda\n"
        "  isso."
    ),
    "punkte": [
        ("1. O software: sem garantia", [
            ("p", "O Full Page PDF Snap é publicado sob a licença MIT. A cláusula de garantia da licença\n"
                  "    faz parte dela e aplica-se integralmente — em síntese: o software é fornecido sem\n"
                  "    garantia de qualquer tipo, expressa ou implícita, incluindo as garantias de\n"
                  "    comercialização, adequação a uma finalidade específica e não violação de direitos. O\n"
                  "    texto que prevalece é a versão em inglês da licença:"),
            ("z", None),
            ("p", "Em particular, não se assegura que a extensão seja adequada a uma finalidade\n"
                  "    específica, que funcione em determinada página, versão de navegador ou dispositivo,\n"
                  "    nem que permaneça disponível."),
        ]),
        ("2. Verifique o resultado antes de confiar nele", [
            ("p", "Uma captura pode estar incompleta sem avisar. Páginas que carregam conteúdo ao rolar,\n"
                  "    que renderizam de forma diferente em outro tamanho de janela, que escondem conteúdo\n"
                  "    atrás de uma interação ou que mudam durante a captura podem produzir um PDF ao qual falta\n"
                  "    algo. A extensão não tem como saber o que a página deveria conter."),
            ("p", "Quando o conteúdo importa — uma confirmação, um prazo, um valor, uma linha de\n"
                  "    transação — abra o PDF pronto e leia a parte relevante antes de confiar nele. Essa\n"
                  "    verificação leva segundos e é a única coisa que comprova que a captura realmente contém o\n"
                  "    que você precisa."),
        ]),
        ("3. Não é um documento eletrônico qualificado", [
            ("p", "Um PDF produzido por captura de tela registra o que um navegador exibiu. Não carrega\n"
                  "    assinatura eletrônica qualificada, carimbo de tempo confiável nem cadeia de custódia, e\n"
                  "    não prova por si só que uma página existiu naquela forma. É adequado para os seus próprios\n"
                  "    registros. Onde se exige valor probatório, o instrumento correto é um serviço construído\n"
                  "    para esse fim."),
        ]),
        ("4. Não é aconselhamento profissional", [
            ("p", "Nada do que é publicado aqui constitui aconselhamento jurídico, fiscal, financeiro,\n"
                  "    médico ou qualquer outra forma de aconselhamento profissional, e a leitura não cria\n"
                  "    relação de cliente. Os artigos tocam em questões com dimensão jurídica — permissões,\n"
                  "    licenças, direitos autorais, o valor probatório de um registro, regras sobre citação e\n"
                  "    prazos. Essas passagens descrevem como as coisas são geralmente entendidas; não decidem o\n"
                  "    seu caso. As regras da sua instituição e a legislação aplicável prevalecem sobre qualquer\n"
                  "    coisa escrita aqui, e para uma situação específica o caminho certo é o aconselhamento\n"
                  "    qualificado."),
        ]),
        ("5. Medições são medições, não garantias", [
            ("p", "Os números publicados aqui vêm de execuções únicas com as entradas indicadas na data\n"
                  "    indicada, com o método e os dados brutos publicados para que possam ser recontados. Não\n"
                  "    são médias de muitas execuções, nem testes certificados, nem uma previsão do que você\n"
                  "    medirá no seu sistema. Quando uma medição foi corrigida após a publicação, a correção é\n"
                  "    indicada no artigo em vez de aplicada silenciosamente."),
        ]),
        ("6. O endpoint de citação em <code>/mcp</code>", [
            ("p", "O endpoint lê o que uma página declara sobre si mesma e o devolve como um registro\n"
                  "    estruturado. Ele não verifica essas declarações, e uma página pode declarar algo errado,\n"
                  "    desatualizado ou incompleto. Um registro marcado como <code>complete: false</code> não é\n"
                  "    uma referência: pode ainda assim trazer título e autor e não deve ser arquivado como fonte\n"
                  "    apenas por isso. Cada registro é um ponto de partida para uma citação, nunca a citação\n"
                  "    pronta — confira-o na obra antes de entrar em uma bibliografia, uma tese ou qualquer\n"
                  "    trabalho submetido."),
            ("p", "O endpoint é oferecido gratuitamente, sem conta e sem qualquer garantia de\n"
                  "    disponibilidade, correção ou continuidade. Pode ser alterado, limitado ou retirado a\n"
                  "    qualquer momento. Não se aceita responsabilidade por consequências de confiar em um\n"
                  "    registro devolvido — em particular não por erros de citação, trabalhos rejeitados ou prazos\n"
                  "    perdidos por indisponibilidade. Onde uma editora oferece sua própria exportação de\n"
                  "    citações, esse arquivo é o que prevalece, e não este endpoint."),
            ("p", "Ele busca apenas os endereços que o chamador fornece, como visitante anônimo, e não\n"
                  "    alcança nada atrás de um login. Usá-lo para sobrecarregar servidores de terceiros não é\n"
                  "    permitido; as requisições carregam um user agent identificável para que os operadores\n"
                  "    possam distingui-las e recusá-las."),
        ]),
        ("7. Produtos de terceiros e links externos", [
            ("p", "As afirmações sobre outros produtos baseiam-se exclusivamente no que seus fornecedores\n"
                  "    publicam sobre si mesmos — manifestos, páginas nas lojas, páginas de ajuda — com a data\n"
                  "    de consulta indicada. Nada foi descompilado, e nenhuma afirmação é feita sobre as\n"
                  "    intenções de qualquer fornecedor nem sobre dados efetivamente transmitidos. Essas\n"
                  "    declarações mudam; confira a fonte atual antes de confiar nelas."),
            ("p", "Os links externos levam a conteúdos que não são nossos. A responsabilidade por eles\n"
                  "    cabe aos respectivos operadores. Os links foram verificados quando inseridos; não há\n"
                  "    monitoramento contínuo. Ao ser notificado de uma violação, o link será removido."),
        ]),
        ("8. Limitação de responsabilidade", [
            ("p", "Na medida permitida por lei, não se aceita responsabilidade por danos decorrentes do\n"
                  "    uso do software ou de decisões tomadas com base em conteúdos publicados aqui — em\n"
                  "    particular não por dados perdidos ou incompletos, prazos perdidos ou consequências de uma\n"
                  "    captura incompleta ou indisponível."),
            ("p", "<strong>Esta limitação não se aplica</strong> a danos causados dolosamente ou por\n"
                  "    culpa grave, a lesões à vida, ao corpo ou à saúde, e sempre que houver responsabilidade\n"
                  "    legal imperativa. Essas hipóteses permanecem em vigor independentemente de qualquer coisa\n"
                  "    aqui declarada."),
        ]),
        ("9. Alterações e correções", [
            ("p", "Conteúdos e software mudam. Esta página traz a data da sua versão atual; as versões\n"
                  "    anteriores estão no histórico do repositório. Erros de fato são corrigidos assim que\n"
                  "    conhecidos — <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">abra uma\n"
                  "    issue</a> — e quando um número publicado muda, a correção é anotada no artigo."),
        ]),
        ("10. Quem publica isto", [
            ("p", "Um projeto privado e não comercial de uma pessoa, operado sob pseudônimo. Nada é\n"
                  "    vendido, não há publicidade, links de afiliados nem rastreamento. Contato e alcance das\n"
                  "    informações publicadas estão descritos em\n"
                  "    <a href=\"../about/\">Sobre e transparência</a>; a identidade por trás do pseudônimo é\n"
                  "    revelada a quem apresentar uma solicitação legal legítima."),
        ]),
    ],
}

# ----------------------------------------------------------------- Русский --
TEXTE["ru"] = {
    "h1": "Отказ от ответственности и ограничение ответственности",
    "standfirst": (
        "Эта страница определяет, за что здесь отвечают, а за что нет — как за публикуемое здесь\n"
        "    программное обеспечение, так и за статьи и данные измерений этого сайта. Она применяется ко\n"
        "    всему, что находится под provinglab.dev, и к распространяемому отсюда расширению."
    ),
    "meta": "Версия от 3 августа 2026 г.",
    "kurz_stark": "Кратко.",
    "kurz": (
        "Программное обеспечение и материалы предоставляются бесплатно и «как есть». Никакие гарантии\n"
        "  не предоставляются, а ответственность исключается в той мере, в какой это допускает закон.\n"
        "  То, что закон не позволяет исключить — умысел, грубая неосторожность, причинение вреда\n"
        "  жизни, здоровью или телу, а также любая императивная законная ответственность — остаётся\n"
        "  незатронутым, и никакая формулировка на этой странице этого не меняет."
    ),
    "punkte": [
        ("1. Программное обеспечение: без гарантий", [
            ("p", "Full Page PDF Snap публикуется под лицензией MIT. Её гарантийная оговорка является\n"
                  "    частью лицензии и действует в полном объёме — по существу: программное обеспечение\n"
                  "    предоставляется без каких-либо гарантий, явных или подразумеваемых, включая гарантии\n"
                  "    товарной пригодности, пригодности для конкретной цели и ненарушения прав. Обязательным\n"
                  "    является английский текст лицензии:"),
            ("z", None),
            ("p", "В частности, не гарантируется, что расширение пригодно для какой-либо конкретной\n"
                  "    цели, что оно работает на конкретной странице, версии браузера или устройстве, или что\n"
                  "    оно останется доступным."),
        ]),
        ("2. Проверьте результат, прежде чем на него полагаться", [
            ("p", "Захват может оказаться неполным без какого-либо указания на это. Страницы, которые\n"
                  "    подгружают содержимое при прокрутке, отображаются иначе при другом размере окна,\n"
                  "    скрывают содержимое за взаимодействием или изменяются во время захвата, могут дать PDF,\n"
                  "    в котором чего-то не хватает. Расширение не может знать, что страница должна была\n"
                  "    содержать."),
            ("p", "Когда содержимое важно — подтверждение, срок, сумма, строка транзакции — откройте\n"
                  "    готовый PDF и прочитайте соответствующую часть, прежде чем полагаться на него. Такая\n"
                  "    проверка занимает секунды и является единственным, что подтверждает: захват\n"
                  "    действительно содержит то, что вам нужно."),
        ]),
        ("3. Это не квалифицированный электронный документ", [
            ("p", "PDF, созданный путём захвата экрана, фиксирует то, что отображал браузер. Он не\n"
                  "    содержит квалифицированной электронной подписи, доверенной метки времени и цепочки\n"
                  "    хранения и сам по себе не доказывает, что страница существовала в таком виде. Для\n"
                  "    собственных записей он подходит. Там, где требуется доказательственная сила, правильным\n"
                  "    инструментом является служба, созданная для этой цели."),
        ]),
        ("4. Это не профессиональная консультация", [
            ("p", "Ничто из опубликованного здесь не является юридической, налоговой, финансовой,\n"
                  "    медицинской или иной профессиональной консультацией, и чтение не создаёт отношений\n"
                  "    клиента и консультанта. Статьи затрагивают вопросы с правовым измерением — разрешения,\n"
                  "    лицензии, авторское право, доказательственная ценность записи, правила цитирования и\n"
                  "    сроков. Эти фрагменты описывают, как вещи обычно понимаются; они не решают ваш случай.\n"
                  "    Правила вашего учреждения и применимое право имеют приоритет над всем написанным здесь, а\n"
                  "    для конкретной ситуации правильный путь — квалифицированная консультация."),
        ]),
        ("5. Измерения — это измерения, а не гарантии", [
            ("p", "Опубликованные здесь цифры получены в одиночных прогонах на указанных входных данных\n"
                  "    в указанную дату; метод и исходные данные опубликованы, чтобы их можно было перепроверить.\n"
                  "    Это не средние значения по множеству прогонов, не сертифицированные испытания и не\n"
                  "    прогноз того, что вы измерите на своей системе. Если измерение было исправлено после\n"
                  "    публикации, исправление указывается в статье, а не вносится незаметно."),
        ]),
        ("6. Конечная точка цитирования <code>/mcp</code>", [
            ("p", "Конечная точка читает то, что страница заявляет о себе, и возвращает это в виде\n"
                  "    структурированной записи. Она не проверяет эти заявления, и страница может заявлять\n"
                  "    что-то неверное, устаревшее или неполное. Запись с пометкой\n"
                  "    <code>complete: false</code> не является библиографической ссылкой: она может содержать\n"
                  "    название и автора и не должна сохраняться как источник только на этом основании. Каждая\n"
                  "    запись — отправная точка для цитирования, а не готовая ссылка, — сверьте её с\n"
                  "    произведением, прежде чем она попадёт в библиографию, диссертацию или любую подаваемую\n"
                  "    работу."),
            ("p", "Конечная точка предоставляется бесплатно, без учётной записи и без каких-либо\n"
                  "    заверений о доступности, корректности или дальнейшем существовании. Она может быть\n"
                  "    изменена, ограничена или отключена в любое время. Ответственность за последствия доверия\n"
                  "    к возвращённой записи не принимается — в частности, за ошибки цитирования, отклонённые\n"
                  "    работы или пропущенные сроки из-за её недоступности. Если издатель предлагает собственный\n"
                  "    экспорт цитирования, этот файл является официальным, а не данная конечная точка."),
            ("p", "Она запрашивает только адреса, указанные вызывающей стороной, как анонимный\n"
                  "    посетитель, и не получает доступ ни к чему за пределами входа в систему. Использовать её\n"
                  "    для создания нагрузки на серверы третьих лиц не разрешается; запросы содержат\n"
                  "    опознаваемый user agent, чтобы операторы могли их отличать и отклонять."),
        ]),
        ("7. Продукты третьих лиц и внешние ссылки", [
            ("p", "Утверждения о других продуктах опираются исключительно на то, что их поставщики\n"
                  "    публикуют о себе сами, — манифесты, страницы в магазинах, справочные страницы — с\n"
                  "    указанием даты обращения. Ничего не декомпилировалось, и никаких утверждений о намерениях\n"
                  "    поставщиков или о фактически передаваемых данных не делается. Такие заявления меняются;\n"
                  "    прежде чем полагаться на них, сверьтесь с актуальным источником."),
            ("p", "Внешние ссылки ведут на содержимое, которое нам не принадлежит. Ответственность за\n"
                  "    него несут соответствующие операторы. Ссылки были проверены при размещении; постоянный\n"
                  "    мониторинг не ведётся. При получении уведомления о нарушении ссылка будет удалена."),
        ]),
        ("8. Ограничение ответственности", [
            ("p", "В той мере, в какой это допускает закон, ответственность за ущерб, возникающий из\n"
                  "    использования программного обеспечения или из решений, принятых на основании\n"
                  "    опубликованных здесь материалов, не принимается — в частности, за потерянные или неполные\n"
                  "    данные, пропущенные сроки или последствия неполного либо недоступного захвата."),
            ("p", "<strong>Это ограничение не применяется</strong> к ущербу, причинённому умышленно или\n"
                  "    по грубой неосторожности, к вреду жизни, здоровью или телу, а также во всех случаях, где\n"
                  "    действует императивная законная ответственность. Она сохраняет силу независимо от всего\n"
                  "    сказанного здесь."),
        ]),
        ("9. Изменения и исправления", [
            ("p", "Содержимое и программное обеспечение меняются. На этой странице указана дата её\n"
                  "    текущей версии; прежние версии находятся в истории репозитория. Фактические ошибки\n"
                  "    исправляются по мере их выявления —\n"
                  "    <a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">откройте issue</a>; если\n"
                  "    опубликованная цифра меняется, исправление отмечается в статье."),
        ]),
        ("10. Кто это публикует", [
            ("p", "Частный некоммерческий проект одного человека, ведущийся под псевдонимом. Ничего не\n"
                  "    продаётся, нет рекламы, партнёрских ссылок и отслеживания. Контакт и объём раскрываемой\n"
                  "    информации описаны на странице\n"
                  "    <a href=\"../about/\">О проекте и раскрытие информации</a>; личность, стоящая за\n"
                  "    псевдонимом, раскрывается по правомерному юридическому запросу."),
        ]),
    ],
}

# ------------------------------------------------------------------ 简体中文 -
TEXTE["zh-CN"] = {
    "h1": "免责声明与责任限制",
    "standfirst": (
        "本页说明对哪些事项承担责任、对哪些事项不承担责任——既包括在此发布的软件，也包括本网站的文章和测量数据。适用于 provinglab.dev 之下的全部内容以及由此分发的扩展。"
    ),
    "meta": "2026年8月3日版本",
    "kurz_stark": "简而言之。",
    "kurz": (
        "软件和内容均免费提供，并以其现状提供。不提供任何形式的担保，责任在法律允许的范围内予以排除。法律不允许排除的部分——故意、重大过失、对生命、身体或健康的侵害，以及任何强制性法定责任——不受影响，本页的任何表述均不改变这一点。"
    ),
    "punkte": [
        ("1. 软件：不提供担保", [
            ("p", "Full Page PDF Snap 依据 MIT 许可证发布。其中的担保条款是许可证的一部分，完全适用——其要旨为：本软件按“现状”提供，不附带任何明示或默示的担保，包括对适销性、特定用途适用性和不侵权的担保。以许可证的英文原文为准："),
            ("z", None),
            ("p", "特别是不保证本扩展适用于任何特定用途、能在任何特定页面、浏览器版本或设备上运行，亦不保证其将持续可用。"),
        ]),
        ("2. 依赖结果之前请先核验", [
            ("p", "截取结果可能在没有任何提示的情况下不完整。滚动时才加载的页面、在不同窗口大小下呈现不同的页面、把内容隐藏在交互之后的页面，或在截取过程中发生变化的页面，都可能生成缺失内容的 PDF。扩展无从知晓页面本应包含什么。"),
            ("p", "当内容重要时——确认信息、截止日期、金额、交易记录行——请先打开生成的 PDF 并阅读相关部分，然后再加以依赖。这一检查只需几秒钟，也是唯一能证明截取结果确实包含您所需内容的办法。"),
        ]),
        ("3. 并非合格电子文档", [
            ("p", "通过屏幕截取生成的 PDF 记录的是浏览器所显示的内容。它不带有合格电子签名、可信时间戳或保管链，其本身不能证明某一页面曾以该形式存在。它适合用于您自己的存档。凡需要证明效力的场合，专为此目的构建的服务才是合适的工具。"),
        ]),
        ("4. 不构成专业建议", [
            ("p", "此处发布的任何内容均不构成法律、税务、金融、医疗或任何其他形式的专业建议，阅读也不产生任何委托关系。文章会触及具有法律维度的问题——权限、许可证、版权、记录的证明价值、引用与期限的规则。这些段落描述的是一般通行的理解；它们并不裁决您的具体个案。所在机构的规则和适用法律优先于此处所述的任何内容，针对具体情况，寻求合格的专业建议才是正确途径。"),
        ]),
        ("5. 测量数据是测量结果，而非保证", [
            ("p", "此处公布的数字来自在注明日期对注明输入进行的单次运行，方法和原始数据均已公开，以便他人复核。它们不是多次运行的平均值，不是经认证的测试，也不是对您在自己系统上将测得结果的预测。凡在发布后被更正的测量，更正会写明在文章中，而不是悄悄改入。"),
        ]),
        ("6. <code>/mcp</code> 引用端点", [
            ("p", "该端点读取页面关于自身的声明，并将其以结构化记录的形式返回。它不核验这些声明，而页面完全可能声明错误、过时或不完整的内容。标记为 <code>complete: false</code> 的记录不是文献引用：它可能仍带有标题和作者，但不得仅凭此就作为来源存档。每条记录都只是引用的起点，绝不是成形的引用——在进入参考文献、学位论文或任何提交材料之前，请与原始作品核对。"),
            ("p", "该端点免费提供，无需账户，且不对可用性、正确性或持续存在作任何保证。它可随时被更改、限制或撤销。对因信赖其返回的记录而产生的后果不承担责任——尤其不对引用错误、被退回的作业，或因其不可用而错过期限承担责任。凡出版方提供自有引用导出的，以该文件为准，本端点不作准。"),
            ("p", "它仅以匿名访客身份获取调用方提供的地址，无法触及登录之后的内容。不得利用它对第三方服务器施加负载；请求带有可识别的用户代理，以便运营方识别并拒绝。"),
        ]),
        ("7. 第三方产品与外部链接", [
            ("p", "关于其他产品的陈述完全以其提供方自行发布的信息为依据——清单文件、商店条目、帮助页面——并注明检索日期。未对任何内容进行反编译，也不就任何提供方的意图或实际传输的数据作出断言。此类声明会发生变化；在依赖之前请对照实时来源核实。"),
            ("p", "外部链接指向的内容并非我方所有。其责任由各自的运营方承担。链接在设置时经过检查；不进行持续监控。在获知侵权情况后，链接将被移除。"),
        ]),
        ("8. 责任限制", [
            ("p", "在法律允许的范围内，对因使用软件或基于此处发布内容作出的决定而产生的损害不承担责任——尤其不对丢失或不完整的数据、错过的期限，或截取不完整或不可用所造成的后果承担责任。"),
            ("p", "<strong>本限制不适用于</strong>因故意或重大过失造成的损害、对生命、身体或健康的侵害，以及一切适用强制性法定责任的情形。无论此处如何表述，这些责任始终有效。"),
        ]),
        ("9. 变更与更正", [
            ("p", "内容和软件会发生变化。本页标注了当前版本的日期；早期版本见代码仓库的历史记录。事实性错误一经知悉即予更正——<a href=\"https://github.com/Bubu89/full-page-pdf-snap/issues\">请提交 issue</a>；凡已公布数字发生变化，更正会在文章中注明。"),
        ]),
        ("10. 发布者", [
            ("p", "一个由个人以化名运营的非商业私人项目。不销售任何产品，没有广告、推广链接或跟踪。联系方式及信息披露范围见 <a href=\"../about/\">关于与披露</a>；化名背后的身份将向提出合法法律请求的一方披露。"),
        ]),
    ],
}
