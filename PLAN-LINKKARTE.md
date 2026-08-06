# Vorüberlegung: eine Linkkarte zur Aufnahme

Stand 6. August 2026. Die Frage war, ob aus der Erweiterung ein zweites Projekt
werden soll, das Webseiten kartografiert — Links im Bild an der richtigen Stelle,
anklickbar, mit Zwischenspeicher für schnelle Navigation.

**Zuerst die Recherche, weil drei Teile davon bereits existieren.** Was übrig
bleibt, ist kleiner als die Idee und liegt näher am bestehenden Produkt.

## Was es schon gibt

### Klickbare Links im PDF — gelöst, vom Browser

Gemessen am 5. August an derselben Wikipedia-Seite:

| | Verweis-Annotationen | verschiedene Ziele |
|---|---|---|
| Chrome `--print-to-pdf` | **1.450** | 382 |
| Full Page PDF Snap | **0** | 0 |

Der Druckweg erzeugt vollständige, positionsgenaue Verweise ohne Zutun. Wer nur
ein PDF mit klickbaren Links will, braucht dafür nichts zu bauen — und die
eigene Vergleichsmessung sollte das erwähnen, tut es bisher nicht.

### Kartografierung als URL-Liste — gelöst, mehrfach

Firecrawl, Crawl4AI und fastCRW bieten alle ein `map`-Werkzeug über MCP. Die
Antwort von Firecrawl besteht aus `url`, `title`, `description`. Aus der
Dokumentation, wörtlich:

> No visual or layout information is included. It does not provide anchor text,
> element positions, or any rendering data.

Ein weiteres Werkzeug, das URL-Listen liefert, wäre das vierte seiner Art.

### Vollständige Archivierung — gelöst

WARC und die Webrecorder-Werkzeuge halten eine Seite samt aller Verweise
navigierbar. Wer eine Seite später begehen will, nimmt das.

## Was es nicht gibt

**Links mit ihrer Position im aufgenommenen Bild.** Kein Crawler liefert das,
weil keiner ein Bild erzeugt. Der Druckexport hat die Verweise, gibt sie aber
nicht als Daten heraus — sie stecken als Annotationen im PDF.

Wofür das gebraucht würde: für einen Agenten, der ein Bild der Seite hat und
keinen Zugriff auf das DOM. Das ist kein konstruierter Fall, sondern genau der,
für den dieses Produkt gebaut ist — die Seite hinter der Anmeldung, die ein
Server nicht lesen kann.

## Machbarkeit, gemessen statt geschätzt

An drei Seiten erhoben, jeweils Rahmen in Dokumentkoordinaten, Ziel, Ankertext:

| Seite | Links | intern | extern | Anker | ohne Text |
|---|---|---|---|---|---|
| Wikipedia (765 × 24.784 px) | **1.528** | 1.297 | 231 | 273 | 0 |
| Behördenportal RIS | 28 | 23 | 5 | 1 | 0 |
| **PubMed** | **0** | — | — | — | — |

Der dritte Fall ist der aufschlussreichste. Die Seite lud unter headless Chrome
nicht — 437 px Höhe statt einiger Tausend. **Dieselben Quellen, die ein Crawler
nicht erfasst, entziehen sich auch einer headless erhobenen Linkkarte.** Im
echten Browser, in dem die Erweiterung läuft, ist die Seite längst gerendert.

Das entscheidet die Architektur: Die Erhebung gehört dorthin, wo die Aufnahme
entsteht, nicht in einen zweiten Dienst, der die Seite noch einmal holt.

## Vorschlag

### Schritt 1 — als Funktion der bestehenden Erweiterung

`collectText` sammelt bereits Wortpositionen in Dokumentkoordinaten. Dieselbe
Schleife über `a[href]` liefert die Linkkarte. Daraus zwei Ausgaben:

- **Verweis-Annotationen im PDF**, an derselben Stelle wie im Bild. Damit
  schließt sich eine Lücke, die heute mit 0 zu 1.450 gegen den Druckexport
  steht.
- **Eine JSON-Karte neben dem PDF**, wie schon der RIS-Datensatz: Rahmen,
  Ziel, Ankertext, intern oder extern. Das ist die Datei, die ein Agent liest.

Klein, prüfbar, und es verbessert das Produkt, das es schon gibt.

### Schritt 2 — erst danach entscheiden

Mehrseitige Kartografie und Zwischenspeicher lohnen als eigenes Projekt erst,
wenn Schritt 1 zeigt, dass die Karte tatsächlich benutzt wird. Beides ist
aufwendig und beides gibt es in Teilen schon.

Zum Zwischenspeicher gehört außerdem eine Vorfrage, die noch niemand gestellt
hat: **Wie oft wird dieselbe Seite überhaupt zweimal abgefragt?** Der Endpunkt
zählt heute nicht mit, welche Adresse ein Agent verarbeitet. Ein
Zwischenspeicher, dessen Trefferquote niemand kennt, ist eine Vermutung mit
Laufzeitkosten.

## Was gegen ein zweites Projekt spricht

Die Erweiterung hat **fünf tägliche Nutzer** und steht im Chrome-Store dreizehn
Fassungen zurück. Ein zweites Produkt teilt dieselbe Aufmerksamkeit auf, bevor
das erste dort angekommen ist, wo es hingehört.

Sollte Schritt 1 zeigen, dass die Karte trägt, ist der Weg zu einem eigenen
Endpunkt kurz — die Werkzeugstruktur steht, das Veröffentlichen in der Registry
ist automatisiert.

## Rohdaten

`linkkarte-probe.json` im Arbeitsverzeichnis: drei Seiten, Zählungen und je acht
Beispiel-Links mit Koordinaten. Erhoben mit Chromium 1208 über CDP, ein Lauf je
Seite, keine Mittelwerte.
