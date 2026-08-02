# Wachstumsplan: von 3 Nutzern aufwärts

Stand 2. August 2026. Alle Zahlen gemessen, nicht geschätzt.

## Die Ausgangslage

| | |
|---|---|
| AMO-Nutzer | **3** |
| Bewertungen | 1 (5,0) |
| Seit | 17. Juli 2026 |
| Inhalte auf provinglab.dev | 6 Messungen, 5 Datensätze, 20 Sitemap-Einträge |
| Agent-Readiness | 13 von 15, Level 5 |

## Was die Agent-Strukturen leisten — und was nicht

Wir haben MCP, WebMCP, Skills-Index, API-Katalog, Markdown-Aushandlung,
Link-Header, OAuth und DNS-AID aufgebaut. **Davon kommt heute kein einziger
Nutzer.** Die Standards sind Entwürfe, und es gibt kaum Software, die danach
sucht. Der Worker zählt eine Handvoll Aufrufe, sämtlich aus eigenen Tests.

Das ist keine verlorene Arbeit — aber es ist Vorbereitung, keine Verbreitung.
Wer daraus Nutzerwachstum ableitet, verwechselt beides.

## Der eine Mechanismus, über den KI tatsächlich Nutzer bringt

Nicht Agentenprotokolle. **Zitate in Antworten.**

Wenn jemand ChatGPT, Perplexity, Copilot oder Google fragt *„wie speichere ich
eine Webseite als PDF, auch auf dem Handy"*, entscheidet sich dort, ob
provinglab.dev als Quelle erscheint. Dafür braucht es drei Dinge, und alle drei
sind bereits erfüllt oder messbar:

1. **Im Index sein, aus dem die Antwortsysteme schöpfen.** ChatGPT und Copilot
   nutzen Bing, Google AI Overviews den Google-Index. Bing hat die Seite
   (geprüft). Google braucht Wochen.
2. **Zitierfähig sein.** Eine Zahl mit Methode und Kontrolllauf wird zitiert;
   eine Meinung nicht. Genau darin liegt die Stärke der Seite — jede Messung
   hat Rohdaten und einen Kontrolllauf.
3. **Erlaubt sein.** `ai-input=yes` in den Content Signals steht.

Daraus folgt der ganze Plan: **mehr zitierfähige Messungen zu Fragen, die
Menschen tatsächlich stellen.**

## Was automatisiert wird

### Läuft bereits: `provinglab-growth`

Dreimal täglich, über `backup-catchup.sh` (der Rechner läuft nicht 24/7).
Misst AMO-Nutzer, Bewertungen, den Rang in sechs Suchbegriffen und ob der Store
überhaupt auf die Seite verweist. Schreibt eine Zeile je Tag nach
`~/.claude/logs/provinglab-growth.ndjson`.

Ohne diese Reihe ist jede Maßnahme eine Vermutung. Mit ihr lässt sich in zwei
Wochen sagen, was gewirkt hat.

    provinglab-growth --show

### Als Nächstes sinnvoll

**Datensätze frisch halten.** Die Android-Messung (60 von 248 Erweiterungen)
veraltet. Ein monatlicher Lauf, der die AMO-API neu abfragt, den Datensatz
schreibt, die Zahlen im Beitrag aktualisiert und IndexNow anstößt. Frische
Daten ranken besser und geben einen Grund zum erneuten Zitieren.

**Rang-Alarm.** Fällt ein Begriff aus den ersten 25 oder taucht ein neuer auf,
eine Meldung. Die Daten dafür sammelt der Monitor bereits.

**Deployment-Anstoß.** IndexNow nach jedem Push automatisch statt von Hand.

## Was ausdrücklich nicht automatisiert wird

**Keine Beiträge in Foren, auf Reddit, Hacker News oder in Kommentaren.**
Automatisiertes Posten verstößt gegen deren Regeln, wird zuverlässig als Spam
erkannt und schadet dem Ruf der Seite mehr, als hundert Klicks ihr nützen. Eine
Seite, deren Anspruch „Measurements, not opinions" ist, kann sich das am
wenigsten leisten. Wo Menschen erreicht werden, geschieht das von Hand und mit
Namen.

**Keine erfundenen Metadaten.** Aus demselben Grund stehen auf der Seite keine
OAuth-Endpunkte, die es nicht gibt, und keine A2A-Karte ohne Agenten.

## Was den größten Unterschied macht — und nicht automatisierbar ist

Nach Wirkung sortiert:

1. **Chrome Web Store.** Der korrigierte Upload liegt fertig in
   `Desktop\PDF_SNAP_STORE_UPLOAD`. Chrome hat ein Vielfaches der
   Firefox-Nutzerbasis. Zehn Minuten Arbeit, größter Einzelhebel.

2. **Die Store-Homepage.** Sie zeigt weiterhin auf `bubu89.github.io`. Der
   Monitor warnt bei jedem Lauf. Solange das so ist, schickt der Store keinen
   einzigen Besucher auf die Seite — und alles hier Beschriebene läuft ins
   Leere.

3. **Das Wort *screenshot* in der Store-Zusammenfassung.** Es fehlt, und
   deshalb steht die Erweiterung bei *full page screenshot* nicht unter den
   ersten 100 von 361 Treffern. Bei *screenshot to pdf* ebenso wenig. Das sind
   zwei der sechs gemessenen Begriffe — ein Drittel der Sichtbarkeit, an einem
   fehlenden Wort.

4. **Menschen erreichen.** Der Aufhänger liegt bereit: 60 Erweiterungen
   deklarieren Android-Unterstützung, niemand hat sie je getestet, und
   Chrome für Android kann überhaupt keine installieren. Das ist eine Zahl,
   über die geschrieben wird — r/androidapps, r/firefox, gHacks. Von Hand.

## Der ehrliche Erwartungswert

Punkt 1 bis 3 sind zusammen etwa zwanzig Minuten Arbeit und betreffen die
Stellen, an denen Menschen suchen. Alles Übrige auf dieser Seite — die
Agent-Ebenen, der MCP-Server, die Discovery-Metadaten — wirkt erst, wenn es
Systeme gibt, die danach fragen. Diese Reihenfolge umzudrehen wäre der
teuerste Fehler.

---

# Teil 2: Keywords, Titel und Verlinkung

Gemessen am 2. August 2026 an den Spitzenplätzen der AMO-Suche.

## Der Befund: AMO rankt nach wörtlicher Titel-Übereinstimmung

| Suchbegriff | Spitzenreiter | dessen Nutzer |
|---|---|---|
| `webpage to pdf` | **Webpage to PDF** | 410 |
| `full page screenshot` | **Full Page Screenshot** | 210 |
| `save page as pdf` | Save as PDF | 19.867 |
| `screenshot to pdf` | Awesome Screenshot | 125.328 |

Zwei Erweiterungen mit 410 und 210 Nutzern stehen vor Konkurrenten mit dem
Hundertfachen an Nutzern — allein, weil ihr Titel der Suchanfrage wörtlich
entspricht. Nutzerzahl schlägt Titel **nicht**.

`PageSaver – Webpage to PDF or Image` (2.200 Nutzer) taucht bei **drei von
fünf** Begriffen in den Top 5 auf: Markenname plus zwei Begriffspaare.

## Der aktuelle Titel und was ihm fehlt

    Full Page PDF Snap – Save Webpage as PDF     (40 Zeichen)

| Begriff | im Titel | Rang heute |
|---|---|---|
| `full page pdf` | ja | **6** |
| `save webpage as pdf` | ja | **11** |
| `save page as pdf` | teilweise | 34 |
| `webpage to pdf` | teilweise | 37 |
| `full page screenshot` | **nein** | **>100** |
| `screenshot to pdf` | **nein** | **>100** |

Der Zusammenhang ist eindeutig: Wo der Begriff im Titel steht, steht die
Erweiterung vorn. Wo er fehlt, ist sie unauffindbar. **Ein einziges fehlendes
Wort kostet zwei von sechs Begriffen.**

## Vorschlag für den Titel

AMO erlaubt 50 Zeichen. Drei Möglichkeiten, nach abnehmender Wirkung auf die
Suche und zunehmender Schonung des Markennamens:

**A — maximale Abdeckung** (45 Zeichen)

    Full Page Screenshot & PDF Snap – Save Webpage

Enthält *full page screenshot* als zusammenhängende Wortfolge, dazu *pdf*,
*save*, *webpage*. Deckt alle sechs gemessenen Begriffe ab. Preis: Der
Markenname steht nicht mehr allein am Anfang.

**B — Ausgleich** (46 Zeichen)

    Full Page PDF Snap – Screenshot & Save Webpage

Markenname bleibt vorn, *screenshot* kommt hinzu. `full page screenshot` wird
nicht als Wortfolge getroffen, die Einzelwörter aber alle.

**C — kleinster Eingriff** (47 Zeichen)

    Full Page PDF Snap – Save Webpage Screenshot

Ein Wort ergänzt, sonst unverändert.

Empfehlung: **B**. Bei drei Nutzern ist der Markenname noch kein Kapital, das
geschont werden müsste — aber B kostet nichts und lässt sich später zu A
schärfen, wenn die Messreihe zeigt, dass es nicht reicht.

## Zusammenfassung — Ersatzvorschlag

Die derzeitige Fassung enthält *screenshot* nicht und behauptet, was unsere
eigene veröffentlichte Messung widerlegt („one of the few"):

    Save a whole web page as one high-resolution PDF — a full-page screenshot
    without page breaks, on desktop and on Firefox for Android. Auto-scrolls
    the entire page: no cropping, no print dialog, no account.

204 von 250 Zeichen. Enthält *screenshot*, *full-page*, *PDF*, *save*,
*web page*, *Android*, *scroll* — und keine Rangbehauptung.

## Tags

Aktuell `download, privacy, security`. AMO erlaubt weitere aus einer festen
Liste; **productivity** passt und fehlt.

## Verlinkung: die kaputte Kette

    Store  ──✗──>  provinglab.dev  ──✓──>  Store

Die Seite verlinkt sauber zum Store. Der Store verweist auf
`bubu89.github.io` — eine alte Adresse, die von den Messungen nichts weiß.
**Jeder Besucher, der im Store auf „Homepage" klickt, landet an der falschen
Stelle.** Das ist die billigste Reparatur im ganzen Plan.

## Interne Weiterführung

Die Messungen stehen weitgehend für sich. Was fehlt, sind Querverweise
zwischen thematisch benachbarten Beiträgen — wer über OCR liest, sollte den
Weg zu *print vs capture* finden, und wer über verschwindende Quellen liest,
den zur Erweiterung. Konkret:

- `webpage-to-pdf-for-ocr` → `print-to-pdf-vs-screenshot` (beide messen
  Textrückgewinnung)
- `web-citations-that-vanish` → `tools/full-page-pdf-snap` (das Werkzeug für
  genau dieses Problem)
- `android-capture-extensions` → `tools/full-page-pdf-snap` (die Erweiterung
  ist eine der 60)
- Jede Messung → `/data/` (Rohdaten sind ein Grund zum Verlinken durch Dritte)

## Reihenfolge

1. AMO-Homepage korrigieren — ohne das wirkt nichts anderes
2. Titel und Zusammenfassung ersetzen, `productivity` ergänzen
3. Chrome Web Store einreichen
4. Querverweise ergänzen
5. Nach zwei Wochen `provinglab-growth --show`: Haben sich die Ränge bei
   `full page screenshot` und `screenshot to pdf` bewegt?

Schritt 1 bis 3 sind zusammen etwa zwanzig Minuten und betreffen ausschließlich
Stellen, an denen Menschen suchen.
