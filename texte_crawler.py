#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""/notes/who-actually-reads-this/ in neun Sprachen.

Ausgangstext ist die AUSGELIEFERTE Seite, woertlich uebernommen — nicht
build-crawler-post.py: der Builder wuerde rund 40 Woerter loeschen
(tools/builder-drift.py). Englisch ist die Basis, alle anderen Fassungen
uebersetzen sie.

Der Stand wird NICHT aktualisiert. Die Seite traegt eine Tagesmessung vom
03.08.2026; sie zu uebersetzen heisst, sie zu erhalten, nicht sie
nachzurechnen.

Die drei Tabellen stehen als gemeinsame Konstanten: Bot-Namen, Anfragezahlen,
Datenmengen, Anteile und die gesuchten Pfade sind Messwerte und Eigennamen,
keine Prosa. Uebersetzt werden nur Beschriftung und Ueberschriften. Eine
uebersetzte Zahl waere eine andere Messung.

Ebenfalls unveraendert in jeder Sprache: Versionsangaben, Dateiformate,
Werkzeug- und Feldnamen (Cloudflare GraphQL Analytics,
httpRequestsAdaptiveGroups, tools/crawler-bericht.py) sowie alle Adressen und
<code>-Inhalte.

Rendern:  python3 tools/seite-neunsprachig.py texte_crawler.py
"""

URL = "https://provinglab.dev/notes/who-actually-reads-this/"
ZIEL = "notes/who-actually-reads-this/index.html"
SPRACHEN = ["en", "de", "es", "fr", "it", "ja", "pt-BR", "ru", "zh-CN"]
BASIS = "en"

# --------------------------------------------------------------- Bausteine
# Adressen und Codeschnipsel stehen einmal hier. Neunfaches Abschreiben waere
# neunmal die Gelegenheit, eine Adresse zu verlieren.
_ROH = '<a href="/data/ki-crawler-aktuell.json">'
_ABFRAGE = ('<a href="https://github.com/Bubu89/full-page-pdf-snap/blob/main/'
            'tools/crawler-bericht.py"><code>tools/crawler-bericht.py</code>'
            '</a>')
_ISSUES = '<a href="https://github.com/Bubu89/full-page-pdf-snap/issues">'
_ZURUECK = '<a href="../../">'
_DISCLAIMER = '<a href="../../disclaimer/">'

# Platzhalter fuer die einzige Zeilenbeschriftung, die Prosa enthaelt: der
# Klammerzusatz hinter ChatGPT-User sagt, dass die Anfrage im Auftrag eines
# Menschen kommt. Der Eigenname bleibt, der Zusatz wird uebersetzt.
_CU = "{cu}"

# (Name, Anfragen, Daten, Anteil) — in jeder Sprache dieselben.
_KI_ZEILEN = [
    ("ClaudeBot (Anthropic)", "135", "795 kB", "45 %"),
    ("GPTBot (OpenAI)", "96", "798 kB", "32 %"),
    ("PerplexityBot", "22", "213 kB", "7 %"),
    ("CCBot (Common Crawl)", "16", "69 kB", "5 %"),
    (_CU, "15", "152 kB", "5 %"),
    ("OAI-SearchBot (OpenAI)", "9", "43 kB", "3 %"),
    ("Amazonbot", "6", "45 kB", "2 %"),
]

_SUCH_ZEILEN = [
    ("Googlebot", "134", "2658 kB", "48 %"),
    ("YandexBot", "130", "1306 kB", "46 %"),
    ("Bingbot", "10", "78 kB", "4 %"),
    ("Applebot", "8", "53 kB", "3 %"),
]

# (Name, Anfragen, gesuchter Pfad) — Pfade sind Codeschnipsel, nie uebersetzt.
_SCAN_ZEILEN = [
    ("Bingbot", "5", "/.env.prod"),
    ("PerplexityBot", "5", "/terraform.tfvars"),
    ("OAI-SearchBot (OpenAI)", "5", "/.git/HEAD"),
    (_CU, "5", "/keys.json"),
]


def _vier(caption, th1, th2, th3, th4, zeilen, cu):
    """Die beiden Messtabellen mit vier Spalten. Zahlen stehen nur oben."""
    rumpf = "\n".join(
        f'      <tr><th scope="row">{n.replace(_CU, cu)}</th>'
        f'<td class="num">{a}</td><td class="num">{d}</td>'
        f'<td class="num">{p}</td></tr>'
        for n, a, d, p in zeilen)
    return f'''<table>
  <caption>{caption}</caption>
  <thead><tr><th scope="col">{th1}</th><th scope="col">{th2}</th>
    <th scope="col">{th3}</th><th scope="col">{th4}</th></tr></thead>
  <tbody>
{rumpf}
  </tbody>
</table>'''


def _scan(caption, th1, th2, th3, cu):
    """Die Tabelle der Zugangsdaten-Scans. Pfade bleiben <code>-Schnipsel."""
    rumpf = "\n".join(
        f'      <tr><th scope="row">{n.replace(_CU, cu)}</th>'
        f'<td class="num">{a}</td><td><code>{p}</code></td></tr>'
        for n, a, p in _SCAN_ZEILEN)
    return f'''<table>
  <caption>{caption}</caption>
  <thead><tr><th scope="col">{th1}</th><th scope="col">{th2}</th>
    <th scope="col">{th3}</th></tr></thead>
  <tbody>
{rumpf}
  </tbody>
</table>'''


def _seite(h1, standfirst, erhoben, fenster, rohdaten, cu,
           kap_ki, sp_ki, kap_such, sp_such, kap_scan, sp_scan,
           h2, p, fuss, korrekturen, issue_text, disclaimer_text):
    tab_ki = _vier(kap_ki, *sp_ki, _KI_ZEILEN, cu)
    tab_such = _vier(kap_such, *sp_such, _SUCH_ZEILEN, cu)
    tab_scan = _scan(kap_scan, *sp_scan, cu)
    return f'''<header>
  <h1>{h1}</h1>
  <p class="standfirst">
    {standfirst}
  </p>
  <p class="meta">{erhoben} · {fenster} ·
    {_ROH}{rohdaten}</a></p>
</header>

<h2>{h2[0]}</h2>
<p>
  {p[0]}
</p>
<p>
  {p[1]}
</p>

<h2>{h2[1]}</h2>
{tab_ki}

<h2>{h2[2]}</h2>
{tab_such}
<p>
  {p[2]}
</p>

<h2>{h2[3]}</h2>
<p>
  {p[3]}
</p>
{tab_scan}
<p>
  {p[4]}
</p>

<h2>{h2[4]}</h2>
<p>
  {p[5]}
</p>

<h2>{h2[5]}</h2>
<p>
  {p[6]}
  {_ABFRAGE}{p[7]}
</p>
<p>
  {p[8]}
</p>
<p>
  {p[9]}
</p>

<footer>
      {fuss}
      <br><br>
      {korrekturen}
      {_ISSUES}{issue_text}</a>.
      <br><br>
      {_ZURUECK}← Proving Lab</a> · {_DISCLAIMER}{disclaimer_text}</a>
    </footer>'''


INHALT = {}

# ------------------------------------------------------------------- English
INHALT["en"] = _seite(
    h1="Who actually reads this site: 24 hours of crawler logs, published",
    standfirst=(
        "Plenty is claimed about AI crawlers and very little is shown. Anyone "
        "running a site can see in their own logs which systems actually "
        "arrive, what they take and how often — and almost nobody publishes "
        "it. Here is one day of it, with the query that produced it."),
    erhoben="Collected 2026-08-03",
    fenster="23.9 h window",
    rohdaten="raw data",
    cu="ChatGPT-User (OpenAI, on behalf of a human)",
    kap_ki="Requests by AI user agent, 23.9 hours to 2026-08-03 18:04 UTC",
    sp_ki=("System", "Requests", "Data", "Share"),
    kap_such="Same window, conventional crawlers",
    sp_such=("Crawler", "Requests", "Data", "Share"),
    kap_scan="Credential scans arriving under AI or crawler user agents",
    sp_scan=("User agent claimed", "Requests", "Paths sought"),
    h2=["The headline",
        "AI systems",
        "Search engines, for comparison",
        "Twenty requests were not reading",
        "What the AI systems actually fetched",
        "What this is not"],
    p=[
        ("<strong>AI systems made more requests than search engines did"
         "</strong> — 299 against 282. The search engines pulled more data "
         "(4.0 MB against 2.1 MB), because Googlebot fetches images and "
         "stylesheets that a language model has no use for."),
        ("This domain was registered on 1 August 2026. It is two days old, "
         "ranks for nothing, and has no inbound links worth counting — and "
         "seven distinct AI systems have already read it."),
        ("YandexBot at 130 requests is within reach of Googlebot, which is "
         "not the ratio most sites see. Bingbot at 10 is the surprise in the "
         "other direction."),
        ("Separated out rather than counted: requests carrying an AI user "
         "agent that went straight for files nobody links to."),
        ("<strong>A user agent is not an identity.</strong> It is a string "
         "the client chooses. Whether these came from the named operators or "
         "from someone borrowing their name cannot be determined from this "
         "side, and this page does not claim to know. What can be said: they "
         "were not reading, all of them got 404, and nothing they sought "
         "exists here."),
        ("The most-requested paths across all of them are the "
         "machine-readable ones — <code>/sitemap.xml</code>, "
         "<code>/llms.txt</code>, <code>/mcp</code> — before the articles. "
         "That is the whole argument for maintaining those files: they are "
         "not decoration, they are what gets read first."),
        ("<strong>These numbers cannot be checked from outside.</strong> They "
         "come from our own provider's analytics, retrieved with a token only "
         "the operator holds. Nobody can recompute them. What is published "
         "instead is the method: the query runs in"),
        (", in plain text, and anyone with a Cloudflare zone can run the same "
         "one against their own."),
        ("So this is a self-report with a disclosed method, not a measurement "
         "someone could repeat. Everywhere else on this site that distinction "
         "is the point, and it would be dishonest to blur it here because the "
         "numbers happen to be flattering."),
        ("Two further limits. One day is one day — a crawler that visits "
         "weekly is invisible in it. And requests are counted at the edge, so "
         "a system reading a cached copy through an intermediary never "
         "appears at all."),
    ],
    fuss=("Method: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, grouped by user agent "
          "over a 24-hour window, collected 2026-08-03. Requests for paths "
          "that only a scanner seeks are separated out and not counted as "
          "reading. The query is published; the underlying log is not "
          "accessible to anyone but the operator, so these figures are a "
          "self-report and are labelled as one. A user agent can be set "
          "freely and is not proof of origin. Nothing here is legal advice."),
    korrekturen="Corrections are welcome and are made in public:",
    issue_text="open an issue",
    disclaimer_text="Disclaimer",
)

# ------------------------------------------------------------------- Deutsch
INHALT["de"] = _seite(
    h1="Wer diese Seite wirklich liest: 24 Stunden Crawler-Protokoll, veröffentlicht",
    standfirst=(
        "Über KI-Crawler wird viel behauptet und wenig gezeigt. Wer eine Seite "
        "betreibt, kann im eigenen Protokoll sehen, welche Systeme tatsächlich "
        "kommen, was sie holen und wie oft — und fast niemand veröffentlicht "
        "es. Hier ist ein Tag davon, mitsamt der Abfrage, die ihn erzeugt hat."),
    erhoben="Erhoben am 03.08.2026",
    fenster="Zeitfenster 23,9 h",
    rohdaten="Rohdaten",
    cu="ChatGPT-User (OpenAI, im Auftrag eines Menschen)",
    kap_ki="Anfragen nach KI-User-Agent, 23,9 Stunden bis 2026-08-03 18:04 UTC",
    sp_ki=("System", "Anfragen", "Daten", "Anteil"),
    kap_such="Dasselbe Zeitfenster, herkömmliche Crawler",
    sp_such=("Crawler", "Anfragen", "Daten", "Anteil"),
    kap_scan="Zugangsdaten-Scans unter KI- oder Crawler-User-Agents",
    sp_scan=("Behaupteter User-Agent", "Anfragen", "Gesuchte Pfade"),
    h2=["Der Befund",
        "KI-Systeme",
        "Suchmaschinen zum Vergleich",
        "Zwanzig Anfragen haben nicht gelesen",
        "Was die KI-Systeme tatsächlich geholt haben",
        "Was das nicht ist"],
    p=[
        ("<strong>Die KI-Systeme haben mehr Anfragen gestellt als die "
         "Suchmaschinen</strong> — 299 gegen 282. Die Suchmaschinen haben mehr "
         "Daten gezogen (4,0 MB gegen 2,1 MB), weil Googlebot Bilder und "
         "Stilvorlagen holt, mit denen ein Sprachmodell nichts anfangen kann."),
        ("Diese Domain wurde am 1. August 2026 registriert. Sie ist zwei Tage "
         "alt, rankt für nichts und hat keine nennenswerten eingehenden Links "
         "— und sieben verschiedene KI-Systeme haben sie bereits gelesen."),
        ("YandexBot liegt mit 130 Anfragen in Reichweite von Googlebot, und "
         "das ist nicht das Verhältnis, das die meisten Seiten sehen. Bingbot "
         "mit 10 ist die Überraschung in die andere Richtung."),
        ("Herausgerechnet statt mitgezählt: Anfragen mit einem KI-User-Agent, "
         "die direkt auf Dateien zielten, die niemand verlinkt."),
        ("<strong>Ein User-Agent ist keine Identität.</strong> Er ist eine "
         "Zeichenkette, die der Client wählt. Ob diese Anfragen von den "
         "genannten Betreibern kamen oder von jemandem, der sich ihren Namen "
         "leiht, lässt sich von dieser Seite aus nicht feststellen, und diese "
         "Seite behauptet nicht, es zu wissen. Sagen lässt sich: Sie haben "
         "nicht gelesen, alle bekamen 404, und nichts von dem, was sie "
         "suchten, gibt es hier."),
        ("Die meistgefragten Pfade über alle hinweg sind die "
         "maschinenlesbaren — <code>/sitemap.xml</code>, "
         "<code>/llms.txt</code>, <code>/mcp</code> — vor den Artikeln. Das "
         "ist das ganze Argument dafür, diese Dateien zu pflegen: Sie sind "
         "keine Zierde, sie sind das, was zuerst gelesen wird."),
        ("<strong>Diese Zahlen sind von außen nicht überprüfbar.</strong> Sie "
         "stammen aus der Auswertung unseres eigenen Anbieters, abgerufen mit "
         "einem Token, das nur der Betreiber hat. Niemand kann sie "
         "nachrechnen. Veröffentlicht wird stattdessen die Methode: Die "
         "Abfrage steht in"),
        (", im Klartext, und wer eine Cloudflare-Zone hat, kann dieselbe gegen "
         "die eigene laufen lassen."),
        ("Das hier ist also eine Selbstauskunft mit offengelegter Methode, "
         "keine Messung, die jemand wiederholen könnte. Überall sonst auf "
         "dieser Seite ist genau dieser Unterschied der Punkt, und es wäre "
         "unredlich, ihn hier zu verwischen, weil die Zahlen zufällig "
         "schmeichelhaft sind."),
        ("Zwei weitere Grenzen. Ein Tag ist ein Tag — ein Crawler, der "
         "wöchentlich vorbeikommt, ist darin unsichtbar. Und gezählt wird am "
         "Rand des Netzes, ein System also, das über einen Zwischenspeicher "
         "eine Kopie liest, taucht überhaupt nicht auf."),
    ],
    fuss=("Methode: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, gruppiert nach "
          "User-Agent über ein 24-Stunden-Fenster, erhoben am 2026-08-03. "
          "Anfragen auf Pfade, die nur ein Scanner sucht, sind "
          "herausgerechnet und nicht als Lesen gezählt. Die Abfrage ist "
          "veröffentlicht; das zugrunde liegende Protokoll ist für niemanden "
          "außer dem Betreiber zugänglich, diese Zahlen sind also eine "
          "Selbstauskunft und als solche gekennzeichnet. Ein User-Agent lässt "
          "sich frei setzen und ist kein Herkunftsnachweis. Nichts davon ist "
          "eine Rechtsberatung."),
    korrekturen="Korrekturen sind willkommen und werden öffentlich gemacht:",
    issue_text="ein Issue eröffnen",
    disclaimer_text="Haftungsausschluss",
)

# ------------------------------------------------------------------- Español
INHALT["es"] = _seite(
    h1="Quién lee realmente este sitio: 24 horas de registros de rastreadores, publicadas",
    standfirst=(
        "Sobre los rastreadores de IA se afirma mucho y se muestra muy poco. "
        "Quien gestiona un sitio puede ver en sus propios registros qué "
        "sistemas llegan de verdad, qué se llevan y con qué frecuencia — y "
        "casi nadie lo publica. Aquí hay un día de ello, junto con la "
        "consulta que lo produjo."),
    erhoben="Recogido el 2026-08-03",
    fenster="ventana de 23,9 h",
    rohdaten="datos en bruto",
    cu="ChatGPT-User (OpenAI, por encargo de una persona)",
    kap_ki="Peticiones por agente de usuario de IA, 23,9 horas hasta 2026-08-03 18:04 UTC",
    sp_ki=("Sistema", "Peticiones", "Datos", "Cuota"),
    kap_such="La misma ventana, rastreadores convencionales",
    sp_such=("Rastreador", "Peticiones", "Datos", "Cuota"),
    kap_scan="Escaneos de credenciales llegados bajo agentes de usuario de IA o de rastreadores",
    sp_scan=("Agente de usuario declarado", "Peticiones", "Rutas buscadas"),
    h2=["El titular",
        "Sistemas de IA",
        "Motores de búsqueda, para comparar",
        "Veinte peticiones no estaban leyendo",
        "Qué recuperaron realmente los sistemas de IA",
        "Qué no es esto"],
    p=[
        ("<strong>Los sistemas de IA hicieron más peticiones que los motores "
         "de búsqueda</strong> — 299 frente a 282. Los motores de búsqueda se "
         "llevaron más datos (4,0 MB frente a 2,1 MB), porque Googlebot "
         "recupera imágenes y hojas de estilo que a un modelo de lenguaje no "
         "le sirven de nada."),
        ("Este dominio se registró el 1 de agosto de 2026. Tiene dos días, no "
         "posiciona para nada y no tiene enlaces entrantes dignos de contarse "
         "— y siete sistemas de IA distintos ya lo han leído."),
        ("YandexBot, con 130 peticiones, está al alcance de Googlebot, y esa "
         "no es la proporción que ve la mayoría de los sitios. Bingbot, con "
         "10, es la sorpresa en la dirección contraria."),
        ("Separadas en lugar de contadas: peticiones que llevaban un agente "
         "de usuario de IA y fueron directas a archivos que nadie enlaza."),
        ("<strong>Un agente de usuario no es una identidad.</strong> Es una "
         "cadena que elige el cliente. Si estas vinieron de los operadores "
         "nombrados o de alguien que toma prestado su nombre no puede "
         "determinarse desde este lado, y esta página no pretende saberlo. Lo "
         "que sí puede decirse: no estaban leyendo, todas recibieron 404 y "
         "nada de lo que buscaban existe aquí."),
        ("Las rutas más solicitadas por todos ellos son las legibles por "
         "máquina — <code>/sitemap.xml</code>, <code>/llms.txt</code>, "
         "<code>/mcp</code> — antes que los artículos. Ese es todo el "
         "argumento para mantener esos archivos: no son adorno, son lo que se "
         "lee primero."),
        ("<strong>Estas cifras no pueden comprobarse desde fuera.</strong> "
         "Proceden de la analítica de nuestro propio proveedor, obtenidas con "
         "un token que solo tiene el operador. Nadie puede recalcularlas. Lo "
         "que se publica en su lugar es el método: la consulta está en"),
        (", en texto plano, y cualquiera que tenga una zona de Cloudflare "
         "puede ejecutar la misma contra la suya."),
        ("Así que esto es un autoinforme con el método revelado, no una "
         "medición que alguien pudiera repetir. En todo el resto de este "
         "sitio esa distinción es justamente el asunto, y sería deshonesto "
         "difuminarla aquí porque las cifras resulten halagadoras."),
        ("Dos límites más. Un día es un día — un rastreador que pasa "
         "semanalmente es invisible en él. Y las peticiones se cuentan en el "
         "borde, así que un sistema que lee una copia en caché a través de un "
         "intermediario no aparece en absoluto."),
    ],
    fuss=("Método: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, agrupado por agente de "
          "usuario sobre una ventana de 24 horas, recogido el 2026-08-03. Las "
          "peticiones a rutas que solo busca un escáner se separan y no se "
          "cuentan como lectura. La consulta está publicada; el registro "
          "subyacente no es accesible para nadie salvo el operador, de modo "
          "que estas cifras son un autoinforme y se etiquetan como tal. Un "
          "agente de usuario puede fijarse libremente y no prueba el origen. "
          "Nada de esto es asesoramiento jurídico."),
    korrekturen="Las correcciones son bienvenidas y se hacen en público:",
    issue_text="abrir un issue",
    disclaimer_text="Aviso legal",
)

# ------------------------------------------------------------------ Français
INHALT["fr"] = _seite(
    h1="Qui lit vraiment ce site : 24 heures de journaux de robots, publiées",
    standfirst=(
        "On affirme beaucoup de choses sur les robots d’IA et on en montre "
        "très peu. Qui exploite un site peut voir dans ses propres journaux "
        "quels systèmes arrivent réellement, ce qu’ils prennent et à quelle "
        "fréquence — et presque personne ne le publie. En voici une journée, "
        "avec la requête qui l’a produite."),
    erhoben="Relevé le 2026-08-03",
    fenster="fenêtre de 23,9 h",
    rohdaten="données brutes",
    cu="ChatGPT-User (OpenAI, pour le compte d’un humain)",
    kap_ki="Requêtes par agent utilisateur d’IA, 23,9 heures jusqu’au 2026-08-03 18:04 UTC",
    sp_ki=("Système", "Requêtes", "Données", "Part"),
    kap_such="Même fenêtre, robots classiques",
    sp_such=("Robot", "Requêtes", "Données", "Part"),
    kap_scan="Scans d’identifiants arrivés sous des agents utilisateurs d’IA ou de robots",
    sp_scan=("Agent utilisateur déclaré", "Requêtes", "Chemins recherchés"),
    h2=["Le constat",
        "Systèmes d’IA",
        "Moteurs de recherche, pour comparaison",
        "Vingt requêtes ne lisaient pas",
        "Ce que les systèmes d’IA ont réellement récupéré",
        "Ce que ceci n’est pas"],
    p=[
        ("<strong>Les systèmes d’IA ont fait plus de requêtes que les moteurs "
         "de recherche</strong> — 299 contre 282. Les moteurs de recherche "
         "ont tiré plus de données (4,0 MB contre 2,1 MB), parce que "
         "Googlebot récupère des images et des feuilles de style dont un "
         "modèle de langue n’a aucun usage."),
        ("Ce domaine a été enregistré le 1er août 2026. Il a deux jours, ne "
         "se classe sur rien et n’a aucun lien entrant digne d’être compté — "
         "et sept systèmes d’IA distincts l’ont déjà lu."),
        ("YandexBot, avec 130 requêtes, est à portée de Googlebot, et ce "
         "n’est pas le rapport que voient la plupart des sites. Bingbot, avec "
         "10, est la surprise dans l’autre sens."),
        ("Mises à part plutôt que comptées : des requêtes portant un agent "
         "utilisateur d’IA et allant droit vers des fichiers que personne ne "
         "lie."),
        ("<strong>Un agent utilisateur n’est pas une identité.</strong> C’est "
         "une chaîne que le client choisit. Savoir si celles-ci venaient des "
         "opérateurs nommés ou de quelqu’un qui emprunte leur nom ne peut pas "
         "être déterminé depuis ce côté-ci, et cette page ne prétend pas le "
         "savoir. Ce qu’on peut dire : elles ne lisaient pas, toutes ont reçu "
         "404, et rien de ce qu’elles cherchaient n’existe ici."),
        ("Les chemins les plus demandés, tous confondus, sont ceux lisibles "
         "par machine — <code>/sitemap.xml</code>, <code>/llms.txt</code>, "
         "<code>/mcp</code> — avant les articles. C’est tout l’argument pour "
         "entretenir ces fichiers : ce ne sont pas des ornements, ce sont eux "
         "qu’on lit en premier."),
        ("<strong>Ces chiffres ne sont pas vérifiables de l’extérieur."
         "</strong> Ils viennent de l’analytique de notre propre "
         "fournisseur, récupérée avec un jeton que seul l’exploitant détient. "
         "Personne ne peut les recalculer. Ce qui est publié à la place, "
         "c’est la méthode : la requête se trouve dans"),
        (", en clair, et quiconque dispose d’une zone Cloudflare peut lancer "
         "la même contre la sienne."),
        ("Ceci est donc une auto-déclaration à méthode divulguée, pas une "
         "mesure que quelqu’un pourrait répéter. Partout ailleurs sur ce site "
         "cette distinction est le sujet même, et il serait malhonnête de la "
         "brouiller ici parce que les chiffres se trouvent être flatteurs."),
        ("Deux limites de plus. Un jour est un jour — un robot qui passe "
         "chaque semaine y est invisible. Et les requêtes sont comptées en "
         "bordure de réseau : un système qui lit une copie en cache via un "
         "intermédiaire n’apparaît pas du tout."),
    ],
    fuss=("Méthode : Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, groupé par agent "
          "utilisateur sur une fenêtre de 24 heures, relevé le 2026-08-03. "
          "Les requêtes vers des chemins que seul un scanner cherche sont "
          "mises à part et ne comptent pas comme lecture. La requête est "
          "publiée ; le journal sous-jacent n’est accessible à personne "
          "d’autre qu’à l’exploitant, ces chiffres sont donc une "
          "auto-déclaration et sont signalés comme tels. Un agent utilisateur "
          "peut être fixé librement et ne prouve pas l’origine. Rien de ceci "
          "n’est un conseil juridique."),
    korrekturen="Les corrections sont bienvenues et sont faites en public :",
    issue_text="ouvrir un issue",
    disclaimer_text="Avertissement",
)

# ------------------------------------------------------------------ Italiano
INHALT["it"] = _seite(
    h1="Chi legge davvero questo sito: 24 ore di registri dei crawler, pubblicate",
    standfirst=(
        "Sui crawler di IA si afferma molto e si mostra pochissimo. Chi "
        "gestisce un sito può vedere nei propri registri quali sistemi "
        "arrivano davvero, che cosa prendono e con quale frequenza — e quasi "
        "nessuno lo pubblica. Eccone una giornata, con la query che l’ha "
        "prodotta."),
    erhoben="Rilevato il 2026-08-03",
    fenster="finestra di 23,9 h",
    rohdaten="dati grezzi",
    cu="ChatGPT-User (OpenAI, per conto di una persona)",
    kap_ki="Richieste per user agent di IA, 23,9 ore fino al 2026-08-03 18:04 UTC",
    sp_ki=("Sistema", "Richieste", "Dati", "Quota"),
    kap_such="Stessa finestra, crawler convenzionali",
    sp_such=("Crawler", "Richieste", "Dati", "Quota"),
    kap_scan="Scansioni di credenziali giunte sotto user agent di IA o di crawler",
    sp_scan=("User agent dichiarato", "Richieste", "Percorsi cercati"),
    h2=["Il dato principale",
        "Sistemi di IA",
        "Motori di ricerca, per confronto",
        "Venti richieste non stavano leggendo",
        "Che cosa hanno davvero prelevato i sistemi di IA",
        "Che cosa questo non è"],
    p=[
        ("<strong>I sistemi di IA hanno fatto più richieste dei motori di "
         "ricerca</strong> — 299 contro 282. I motori di ricerca hanno tirato "
         "più dati (4,0 MB contro 2,1 MB), perché Googlebot preleva immagini "
         "e fogli di stile che a un modello linguistico non servono."),
        ("Questo dominio è stato registrato il 1° agosto 2026. Ha due giorni, "
         "non si posiziona per nulla e non ha link in entrata degni di essere "
         "contati — e sette sistemi di IA distinti lo hanno già letto."),
        ("YandexBot, con 130 richieste, è a portata di Googlebot, e non è il "
         "rapporto che vede la maggior parte dei siti. Bingbot, con 10, è la "
         "sorpresa nella direzione opposta."),
        ("Messe da parte anziché contate: richieste che portavano uno user "
         "agent di IA e puntavano dritto a file che nessuno collega."),
        ("<strong>Uno user agent non è un’identità.</strong> È una stringa "
         "che sceglie il client. Se queste siano venute dagli operatori "
         "nominati o da qualcuno che ne prende in prestito il nome non è "
         "determinabile da questo lato, e questa pagina non pretende di "
         "saperlo. Quello che si può dire: non stavano leggendo, tutte hanno "
         "ricevuto 404 e nulla di ciò che cercavano esiste qui."),
        ("I percorsi più richiesti nel complesso sono quelli leggibili dalla "
         "macchina — <code>/sitemap.xml</code>, <code>/llms.txt</code>, "
         "<code>/mcp</code> — prima degli articoli. È tutto qui l’argomento "
         "per mantenere quei file: non sono decorazione, sono ciò che viene "
         "letto per primo."),
        ("<strong>Questi numeri non sono verificabili dall’esterno.</strong> "
         "Vengono dall’analitica del nostro stesso fornitore, recuperata con "
         "un token che ha solo il gestore. Nessuno può ricalcolarli. Ciò che "
         "si pubblica al loro posto è il metodo: la query sta in"),
        (", in chiaro, e chiunque abbia una zona Cloudflare può eseguire la "
         "stessa sulla propria."),
        ("Questa è quindi un’autodichiarazione con metodo dichiarato, non una "
         "misura che qualcuno potrebbe ripetere. In ogni altro punto di "
         "questo sito quella distinzione è il punto, e sarebbe disonesto "
         "sfumarla qui perché i numeri risultano lusinghieri."),
        ("Altri due limiti. Un giorno è un giorno — un crawler che passa "
         "ogni settimana lì è invisibile. E le richieste si contano al bordo "
         "della rete, quindi un sistema che legge una copia in cache tramite "
         "un intermediario non compare affatto."),
    ],
    fuss=("Metodo: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, raggruppato per user "
          "agent su una finestra di 24 ore, rilevato il 2026-08-03. Le "
          "richieste verso percorsi che solo uno scanner cerca sono messe da "
          "parte e non contate come lettura. La query è pubblicata; il "
          "registro sottostante non è accessibile a nessuno tranne al "
          "gestore, quindi queste cifre sono un’autodichiarazione e come tali "
          "sono etichettate. Uno user agent può essere impostato liberamente "
          "e non è prova di origine. Nulla di qui è consulenza legale."),
    korrekturen="Le correzioni sono benvenute e vengono fatte in pubblico:",
    issue_text="aprire un issue",
    disclaimer_text="Avvertenza",
)

# --------------------------------------------------------------------- 日本語
INHALT["ja"] = _seite(
    h1="このサイトを実際に読んでいるのは誰か——クローラー記録 24 時間分の公開",
    standfirst=(
        "AI クローラーについては多くが語られ、ほとんど示されていない。"
        "サイトを運用していれば、どのシステムが実際に来て、何を持ち去り、"
        "どれくらいの頻度で来るのかを、自分の記録で見ることができる。"
        "それを公開する者はほとんどいない。ここにその一日分を、生成に使った"
        "クエリとともに置く。"),
    erhoben="取得日 2026-08-03",
    fenster="対象期間 23.9 時間",
    rohdaten="生データ",
    cu="ChatGPT-User (OpenAI、人間の依頼による)",
    kap_ki="AI ユーザーエージェント別のリクエスト数、2026-08-03 18:04 UTC までの 23.9 時間",
    sp_ki=("システム", "リクエスト", "データ量", "割合"),
    kap_such="同じ期間、従来型のクローラー",
    sp_such=("クローラー", "リクエスト", "データ量", "割合"),
    kap_scan="AI またはクローラーのユーザーエージェントで届いた認証情報スキャン",
    sp_scan=("名乗ったユーザーエージェント", "リクエスト", "求めたパス"),
    h2=["要点",
        "AI システム",
        "比較としての検索エンジン",
        "20 件のリクエストは読んでいなかった",
        "AI システムが実際に取得したもの",
        "これが何ではないか"],
    p=[
        ("<strong>AI システムのほうが検索エンジンより多くリクエストした。"
         "</strong>299 対 282 である。データ量では検索エンジンのほうが多く"
         "（4.0 MB 対 2.1 MB）、Googlebot が画像やスタイルシートまで取得する"
         "からで、それらは言語モデルには用がない。"),
        ("このドメインは 2026 年 8 月 1 日に登録された。二日目であり、何の"
         "検索順位もなく、数えるに値する被リンクもない。それでも七つの異なる "
         "AI システムがすでに読んでいる。"),
        ("YandexBot は 130 リクエストで Googlebot に手が届く位置にあり、これは"
         "たいていのサイトが見る比率ではない。Bingbot の 10 は、逆方向の"
         "驚きである。"),
        ("数えずに切り分けたもの——AI のユーザーエージェントを名乗りながら、"
         "誰もリンクしていないファイルへ一直線に向かったリクエストである。"),
        ("<strong>ユーザーエージェントは身元ではない。</strong>クライアントが"
         "選ぶ文字列にすぎない。これらが名指しされた運営者から来たのか、"
         "その名を借りた誰かから来たのかは、こちら側からは判定できず、"
         "本ページはそれを知っているとは主張しない。言えるのは、"
         "それらは読んでいなかった、すべて 404 を受け取った、"
         "求めていたものはここに何一つ存在しない、ということである。"),
        ("すべてを通じて最も多く求められたパスは、機械可読なもの——"
         "<code>/sitemap.xml</code>、<code>/llms.txt</code>、"
         "<code>/mcp</code>——であり、記事より先である。これらのファイルを"
         "整備する理由はそれに尽きる。飾りではなく、最初に読まれるものだ。"),
        ("<strong>これらの数字は外部から検証できない。</strong>自分たちの"
         "事業者の解析から得たもので、運営者しか持たないトークンで取得した。"
         "誰も再計算できない。代わりに公開するのは方法である。クエリは"),
        ("に平文で置いてあり、Cloudflare のゾーンを持つ者は誰でも、"
         "同じものを自分のゾーンに対して実行できる。"),
        ("したがってこれは方法を開示した自己申告であって、誰かが再現できる"
         "測定ではない。本サイトの他のどこでもこの区別こそが要点であり、"
         "数字がたまたま好都合だからといってここでぼかすのは不誠実だろう。"),
        ("さらに二つの限界がある。一日は一日でしかない——週に一度来る"
         "クローラーはそこには映らない。そしてリクエストは配信の縁で数える"
         "ので、仲介を経てキャッシュされた複製を読む系統はまったく現れない。"),
    ],
    fuss=("方法：Cloudflare GraphQL Analytics の "
          "<code>httpRequestsAdaptiveGroups</code> を、24 時間の窓で"
          "ユーザーエージェント別に集計。取得日は 2026-08-03。"
          "スキャナーしか探さないパスへのリクエストは切り分け、"
          "読んだものとしては数えていない。クエリは公開しているが、"
          "元の記録は運営者以外に閲覧できないため、これらの数値は自己申告であり、"
          "そう明示している。ユーザーエージェントは自由に設定でき、"
          "出所の証明にはならない。ここに書かれたことは法的助言ではない。"),
    korrekturen="訂正は歓迎し、公開の場で行う：",
    issue_text="issue を立てる",
    disclaimer_text="免責事項",
)

# --------------------------------------------------------- Português (Brasil)
INHALT["pt-BR"] = _seite(
    h1="Quem realmente lê este site: 24 horas de registros de rastreadores, publicadas",
    standfirst=(
        "Sobre rastreadores de IA afirma-se muito e mostra-se muito pouco. "
        "Quem mantém um site pode ver nos próprios registros quais sistemas "
        "de fato chegam, o que levam e com que frequência — e quase ninguém "
        "publica isso. Aqui está um dia disso, com a consulta que o produziu."),
    erhoben="Coletado em 2026-08-03",
    fenster="janela de 23,9 h",
    rohdaten="dados brutos",
    cu="ChatGPT-User (OpenAI, a pedido de uma pessoa)",
    kap_ki="Requisições por agente de usuário de IA, 23,9 horas até 2026-08-03 18:04 UTC",
    sp_ki=("Sistema", "Requisições", "Dados", "Participação"),
    kap_such="Mesma janela, rastreadores convencionais",
    sp_such=("Rastreador", "Requisições", "Dados", "Participação"),
    kap_scan="Varreduras de credenciais chegadas sob agentes de usuário de IA ou de rastreadores",
    sp_scan=("Agente de usuário declarado", "Requisições", "Caminhos procurados"),
    h2=["O achado principal",
        "Sistemas de IA",
        "Buscadores, para comparação",
        "Vinte requisições não estavam lendo",
        "O que os sistemas de IA de fato buscaram",
        "O que isto não é"],
    p=[
        ("<strong>Os sistemas de IA fizeram mais requisições do que os "
         "buscadores</strong> — 299 contra 282. Os buscadores puxaram mais "
         "dados (4,0 MB contra 2,1 MB), porque o Googlebot busca imagens e "
         "folhas de estilo que não servem para um modelo de linguagem."),
        ("Este domínio foi registrado em 1º de agosto de 2026. Tem dois dias, "
         "não posiciona para nada e não tem links de entrada dignos de "
         "contagem — e sete sistemas de IA distintos já o leram."),
        ("O YandexBot, com 130 requisições, está ao alcance do Googlebot, e "
         "essa não é a proporção que a maioria dos sites vê. O Bingbot, com "
         "10, é a surpresa na direção oposta."),
        ("Separadas em vez de contadas: requisições que traziam um agente de "
         "usuário de IA e foram direto a arquivos que ninguém liga."),
        ("<strong>Um agente de usuário não é uma identidade.</strong> É uma "
         "cadeia de caracteres que o cliente escolhe. Se estas vieram dos "
         "operadores nomeados ou de alguém que toma emprestado o nome deles "
         "não se pode determinar deste lado, e esta página não afirma saber. "
         "O que se pode dizer: não estavam lendo, todas receberam 404 e nada "
         "do que procuravam existe aqui."),
        ("Os caminhos mais requisitados no conjunto são os legíveis por "
         "máquina — <code>/sitemap.xml</code>, <code>/llms.txt</code>, "
         "<code>/mcp</code> — antes dos artigos. É esse todo o argumento para "
         "manter esses arquivos: não são enfeite, são o que se lê primeiro."),
        ("<strong>Estes números não podem ser verificados de fora.</strong> "
         "Vêm da analítica do nosso próprio provedor, obtida com um token que "
         "só o operador tem. Ninguém pode recalculá-los. O que se publica em "
         "vez disso é o método: a consulta está em"),
        (", em texto claro, e quem tiver uma zona Cloudflare pode rodar a "
         "mesma contra a sua."),
        ("Portanto isto é um autorrelato com método divulgado, não uma "
         "medição que alguém pudesse repetir. Em todo o resto deste site essa "
         "distinção é justamente a questão, e seria desonesto borrá-la aqui "
         "porque os números por acaso são lisonjeiros."),
        ("Mais dois limites. Um dia é um dia — um rastreador que passa "
         "semanalmente é invisível nele. E as requisições são contadas na "
         "borda, de modo que um sistema que lê uma cópia em cache por meio de "
         "um intermediário não aparece de jeito nenhum."),
    ],
    fuss=("Método: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, agrupado por agente de "
          "usuário sobre uma janela de 24 horas, coletado em 2026-08-03. "
          "Requisições a caminhos que só um scanner procura são separadas e "
          "não contadas como leitura. A consulta está publicada; o registro "
          "subjacente não é acessível a ninguém além do operador, portanto "
          "estes números são um autorrelato e estão rotulados como tal. Um "
          "agente de usuário pode ser definido livremente e não é prova de "
          "origem. Nada aqui é aconselhamento jurídico."),
    korrekturen="Correções são bem-vindas e são feitas em público:",
    issue_text="abrir um issue",
    disclaimer_text="Aviso legal",
)

# --------------------------------------------------------------------- Русский
INHALT["ru"] = _seite(
    h1="Кто на самом деле читает этот сайт: 24 часа журналов краулеров, опубликованные",
    standfirst=(
        "Об ИИ-краулерах утверждают много, а показывают крайне мало. Тот, кто "
        "держит сайт, может увидеть в собственных журналах, какие системы "
        "приходят на самом деле, что забирают и как часто, — и почти никто "
        "этого не публикует. Вот один день, вместе с запросом, который его "
        "получил."),
    erhoben="Собрано 2026-08-03",
    fenster="окно 23,9 ч",
    rohdaten="исходные данные",
    cu="ChatGPT-User (OpenAI, по поручению человека)",
    kap_ki="Запросы по ИИ-агентам пользователя, 23,9 часа до 2026-08-03 18:04 UTC",
    sp_ki=("Система", "Запросы", "Данные", "Доля"),
    kap_such="То же окно, обычные краулеры",
    sp_such=("Краулер", "Запросы", "Данные", "Доля"),
    kap_scan="Сканирование учётных данных под ИИ- или краулерными агентами пользователя",
    sp_scan=("Заявленный агент пользователя", "Запросы", "Искомые пути"),
    h2=["Главное",
        "ИИ-системы",
        "Поисковые машины для сравнения",
        "Двадцать запросов ничего не читали",
        "Что ИИ-системы на самом деле забрали",
        "Чем это не является"],
    p=[
        ("<strong>ИИ-системы сделали больше запросов, чем поисковые машины"
         "</strong> — 299 против 282. Поисковые машины вытянули больше данных "
         "(4,0 MB против 2,1 MB), потому что Googlebot забирает изображения и "
         "таблицы стилей, которые языковой модели ни к чему."),
        ("Этот домен зарегистрирован 1 августа 2026 года. Ему два дня, он ни "
         "по чему не ранжируется и не имеет входящих ссылок, достойных "
         "подсчёта, — и семь разных ИИ-систем уже его прочитали."),
        ("YandexBot со 130 запросами находится в пределах досягаемости "
         "Googlebot, и это не то соотношение, которое видит большинство "
         "сайтов. Bingbot с 10 — неожиданность в другую сторону."),
        ("Выделено отдельно, а не засчитано: запросы с ИИ-агентом "
         "пользователя, шедшие прямо к файлам, на которые никто не ссылается."),
        ("<strong>Агент пользователя — не удостоверение личности.</strong> "
         "Это строка, которую выбирает клиент. Пришли ли эти запросы от "
         "названных операторов или от того, кто позаимствовал их имя, с этой "
         "стороны определить нельзя, и эта страница не утверждает, что знает. "
         "Сказать можно вот что: они не читали, все получили 404, и ничего из "
         "того, что они искали, здесь нет."),
        ("Самые запрашиваемые пути по всем вместе — машиночитаемые: "
         "<code>/sitemap.xml</code>, <code>/llms.txt</code>, "
         "<code>/mcp</code> — раньше статей. В этом и весь довод за то, чтобы "
         "эти файлы вести: они не украшение, они то, что читают первым."),
        ("<strong>Эти числа нельзя проверить снаружи.</strong> Они получены "
         "из аналитики нашего собственного провайдера, извлечены токеном, "
         "который есть только у оператора. Пересчитать их никто не может. "
         "Вместо этого публикуется метод: запрос лежит в"),
        (", открытым текстом, и всякий, у кого есть зона Cloudflare, может "
         "выполнить такой же для своей."),
        ("Итак, это самоотчёт с раскрытым методом, а не измерение, которое "
         "кто-то мог бы повторить. Везде на этом сайте именно это различие и "
         "составляет суть, и было бы нечестно размывать его здесь только "
         "потому, что числа случайно лестны."),
        ("Ещё два ограничения. День есть день — краулер, приходящий раз в "
         "неделю, в нём невидим. И запросы считаются на границе сети, поэтому "
         "система, читающая кэшированную копию через посредника, не "
         "появляется вовсе."),
    ],
    fuss=("Метод: Cloudflare GraphQL Analytics, "
          "<code>httpRequestsAdaptiveGroups</code>, сгруппировано по агенту "
          "пользователя за 24-часовое окно, собрано 2026-08-03. Запросы к "
          "путям, которые ищет только сканер, выделены отдельно и не "
          "засчитаны как чтение. Запрос опубликован; лежащий в основе журнал "
          "недоступен никому, кроме оператора, поэтому эти цифры — самоотчёт, "
          "и они так и обозначены. Агент пользователя можно задать свободно, "
          "и он не доказывает происхождение. Ничто здесь не является "
          "юридической консультацией."),
    korrekturen="Исправления приветствуются и вносятся публично:",
    issue_text="открыть issue",
    disclaimer_text="Отказ от ответственности",
)

# ---------------------------------------------------------------------- 中文
INHALT["zh-CN"] = _seite(
    h1="究竟谁在读这个站点：24 小时爬虫日志，公开",
    standfirst=(
        "关于 AI 爬虫，说的多，拿出来看的极少。任何运营站点的人都能在自己的"
        "日志里看到哪些系统真的来过、取走了什么、来得多频繁——却几乎没有人"
        "把它公开。这里是其中一天，连同产生它的那条查询。"),
    erhoben="采集于 2026-08-03",
    fenster="时间窗 23.9 h",
    rohdaten="原始数据",
    cu="ChatGPT-User (OpenAI，代表人类发起)",
    kap_ki="按 AI 用户代理统计的请求数，截至 2026-08-03 18:04 UTC 的 23.9 小时",
    sp_ki=("系统", "请求数", "数据量", "占比"),
    kap_such="同一时间窗，传统爬虫",
    sp_such=("爬虫", "请求数", "数据量", "占比"),
    kap_scan="以 AI 或爬虫用户代理到达的凭据扫描",
    sp_scan=("声称的用户代理", "请求数", "所求路径"),
    h2=["要点",
        "AI 系统",
        "搜索引擎，用作对照",
        "有二十次请求不是在读",
        "AI 系统实际取走了什么",
        "这不是什么"],
    p=[
        ("<strong>AI 系统发出的请求比搜索引擎更多</strong>——299 对 282。"
         "搜索引擎拉走的数据更多（4.0 MB 对 2.1 MB），因为 Googlebot 会取"
         "图片和样式表，而语言模型用不上这些。"),
        ("这个域名注册于 2026 年 8 月 1 日。它只有两天大，没有任何排名，也没有"
         "值得计入的外部链接——而已经有七个不同的 AI 系统读过它。"),
        ("YandexBot 以 130 次请求已在 Googlebot 的射程之内，这不是大多数站点"
         "看到的比例。Bingbot 的 10 次，则是反方向上的意外。"),
        ("单列出来而不计入：带着 AI 用户代理、却径直奔向无人链接的文件的请求。"),
        ("<strong>用户代理不是身份。</strong>它只是客户端自己选定的一个字符串。"
         "这些请求究竟来自被点名的运营方，还是来自借用其名号的人，从这一侧"
         "无法判定，本页也不声称知道。可以说的是：它们不是在读，全部收到 404，"
         "它们所寻找的东西这里一样都没有。"),
        ("在所有请求中被要得最多的路径是机器可读的那几个——"
         "<code>/sitemap.xml</code>、<code>/llms.txt</code>、"
         "<code>/mcp</code>——排在文章之前。维护这些文件的全部理由就在这里："
         "它们不是装饰，它们是最先被读到的东西。"),
        ("<strong>这些数字无法从外部核验。</strong>它们出自我们自己服务商的"
         "分析数据，用只有运营者持有的令牌取得。没有人能重算。作为替代，"
         "公开的是方法：这条查询就在"),
        ("里，以明文写出；任何拥有 Cloudflare 区域的人，都可以对自己的区域"
         "运行同一条。"),
        ("所以这是一份公开了方法的自述，而不是一次别人能够重复的测量。"
         "在本站其他任何地方，这个区分正是要点所在；仅仅因为数字碰巧好看"
         "就在这里把它抹糊，那是不诚实的。"),
        ("还有两条界限。一天就只是一天——每周才来一次的爬虫在其中是看不见的。"
         "而且请求是在网络边缘计数的，因此经由中间层读取缓存副本的系统"
         "根本不会出现。"),
    ],
    fuss=("方法：Cloudflare GraphQL Analytics 的 "
          "<code>httpRequestsAdaptiveGroups</code>，以 24 小时为窗口按用户代理"
          "分组，采集于 2026-08-03。只有扫描器才会去找的路径，其请求被单列出来，"
          "不计为阅读。查询已公开；底层日志除运营者外无人可以访问，"
          "因此这些数字是自述，并已如此标注。用户代理可以随意设置，"
          "不构成来源证明。此处内容均不构成法律建议。"),
    korrekturen="欢迎指正，更正将公开进行：",
    issue_text="提一个 issue",
    disclaimer_text="免责声明",
)
