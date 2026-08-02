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
