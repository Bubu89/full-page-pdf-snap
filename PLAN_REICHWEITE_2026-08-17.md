# Reichweite MCP + Add-on — Befund und Plan (17.08.2026)

Gemessen, nicht geschätzt. Alle Zahlen aus Cloudflare-Zonenanalytik
(23,5-h-Fenster), dem Werkzeugzähler im Worker und der AMO-API.

---

## 1. Zuerst eine Korrektur

`adoption_stats` liefert **zwei Datenstände in einer Antwort**, und das ist
irreführend:

| Feld | Stand |
|---|---|
| `toolCalls` | **live** |
| `endpoint`, `whatAgentsRead` | **eingefroren 04./05.08.2026** |

Das Feld `measuredOver` sagt es, aber die Zahlen stehen gleichberechtigt
nebeneinander. Wer die Antwort heute liest, hält 150 Server-Card-Abrufe für
den Ist-Stand. Live sind es **16**.

**Der Unterschied ist der ganze Punkt:** Die Zahlen vom 04./05.08. sind der
Ausschlag der Registry-Eintragung. Der ist abgeklungen.

---

## 2. Der Trichter, live gemessen

| Stufe | 04./05.08. (eingefroren) | 17.08. (live) |
|---|---:|---:|
| Anfragen an `/mcp` | 1.130 | 1.365 |
| davon Monitore/Registry-Prüfer | — | ~98,8 % |
| Abrufe der Agenten-Beschreibungen | ~700 | **43** |
| Werkzeugaufrufe | nicht gezählt | **≈ 16/Tag** |

### Die 43 Beschreibungsabrufe aufgeschlüsselt

| Aufrufer | Anzahl | Einordnung |
|---|---:|---|
| ohne User-Agent | 15 | unbestimmbar |
| MCPCensus | 10 | Registry-Crawler |
| Safari iPhone **iOS 13.2.3** | 8 | gefälschte Kennung (Version von 2019) |
| Windows Chrome | 4 | unbestimmbar |
| agent-trust-index | 3 | Registry-artig |
| AgenstryBot | 2 | Registry-artig |
| curl | 1 | Skript |

**Echte, handlungsfähige Agenten: praktisch null.**

### Der Widerspruch, der die Diagnose trägt

16 Werkzeugaufrufe pro Tag bei ~0 Beschreibungsabrufen von echten Agenten.
Wer die Werkzeuge aufruft, hat die Beschreibung **nicht vorher gelesen** —
also Registry-Zwischenspeicher, feste Konfigurationen oder Eigenverkehr.
Zwei der vier `adoption_stats`-Aufrufe stammen aus dieser Analyse selbst.

---

## 3. Befund

**Der Engpass ist die Entdeckung, nicht die Umwandlung.**

Bisher lag die Annahme nahe: viele schauen, wenige handeln — also muss die
Umwandlung besser werden. Die Live-Messung sagt das Gegenteil. Es schaut
fast niemand. Jede Maßnahme an der Umwandlung ginge ins Leere.

**Das Add-on steht besser da als der MCP.** 31 tägliche Nutzer nach einem
Monat, ohne Werbung, 5,0 Sterne. Der Store trägt sich selbst; der MCP nicht.

---

## 4. Maßnahmen, nach Hebel geordnet

### M1 — AMO-Eintrag zeigt den falschen Anwendungsfall (sofort, kostenlos)

| | Ist | Soll |
|---|---|---|
| Kategorien | privacy-security, bookmarks, photos-music-videos | Kategorien mit Bezug zu Recherche/Produktivität |
| Tags | download, privacy, security | citation, research, zotero, reference, pdf |

Der Kurztext nennt DOI, RIS, Zotero und Citavi — die **Auffindbarkeitsfelder
nennen davon nichts**. Wer auf AMO „citation" oder „zotero" sucht, findet
das Add-on nicht.

*Messbar:* Position bei fünf AMO-Suchbegriffen vorher/nachher, tägliche
Nutzer über zwei Wochen.

### M2 — Bewertungen sind der stärkste AMO-Ranghebel (zwei Wochen)

2 Bewertungen bei 31 täglichen Nutzern. AMO gewichtet Bewertungszahl stark.

*Vorschlag:* **einmalig** nach echtem Nutzen (z. B. der zehnten Aufnahme),
im Ergebnis-Tab, kein Popup, dauerhaft abschaltbar. Ein zweites Mal fragen
kostet mehr als es bringt.

*Messbar:* Bewertungen nach 14 Tagen.

### M3 — MCP steht in Maschinen-Verzeichnissen, nicht dort wo Menschen wählen

Vorhanden: offizielle Registry, Glama (automatisch übernommen).

Es fehlen die Orte, an denen ein **Mensch** einen Connector aussucht:
Smithery, mcp.so, PulseMCP, die Connector-Verzeichnisse der Clients
(Claude, Cursor, VS Code, Windsurf).

Die Registry speist Crawler. Die Verzeichnisse speisen Nutzer. Das ist der
Unterschied zwischen 1.365 Monitor-Anfragen und 16 Werkzeugaufrufen.

*Messbar:* Werkzeugaufrufe je Tag, aufgeschlüsselt nach Client (siehe M6).

### M4 — Die Server-Beschreibung sagt, was es ist, nicht wofür man es braucht

> „Measurement datasets and reproducible methods on browser tools, OCR
> pipelines and AI-assisted development."

Die **Werkzeug**beschreibungen sind vorbildlich aufgabenorientiert
(„Use when a claim … needs a number behind it"). Die **Server**ebene nicht —
und die ist der erste Filter in jedem Verzeichnis.

Ein Agent, dessen Nutzer „ich muss diese Webseite zitieren" sagt, matcht
nicht auf „measurement datasets".

*Vorschlag:* Erster Satz nennt die Aufgabe, zweiter die Belegtiefe.

### M5 — Auto-Installation: der ausgebaute Weg ist der seltene

Die Marionette- und Policy-Wege sind technisch das Beste am Projekt —
gemessen, mit Fehlerfällen, mit Rechte-Grenzen. Sie bedienen aber Agenten,
**die einen Browser steuern**. Das ist ein sehr kleiner Kreis.

Der breite Weg ist: Agent sagt dem Menschen „installier das hier", Mensch
klickt im Store. Diesen Weg deckt `how_to_capture` mit den Store-Links
bereits ab.

**Was fehlt, ist nicht die Anleitung, sondern der Auslöser** — eine klare
Aussage, *wann* ein Agent das empfehlen soll. Ohne die bleibt das Werkzeug
ungenutzt, auch wenn es perfekt dokumentiert ist.

*Vorschlag:* Im Server-Card und in `agent.md` einen Abschnitt „empfehle das
Add-on, wenn …" mit drei konkreten Nutzeraussagen.

### M6 — Messlücke: Aufrufe ohne Herkunft

Der Zähler erfasst bewusst keinen Aufrufer. Damit lässt sich nicht sagen, ob
16 Aufrufe/Tag echte Adoption oder Eigenverkehr sind — eine Frage, die jede
Maßnahmenbewertung braucht.

*Vorschlag:* Zusätzlich die **Client-Kennung** aus `initialize`
(`clientInfo.name`) zählen — kein IP, keine Argumente, kein Nutzer. Bleibt
im Datensparsamkeits-Rahmen des Projekts und beantwortet die Frage.

### M7 — `adoption_stats` mischt zwei Datenstände

Siehe Abschnitt 1. Entweder die Pfadzahlen live erheben oder sie in einen
Block `frozenSnapshot` verschieben, damit niemand sie für aktuell hält.

---

## 4a. Stand der Umsetzung (17.08.2026)

| Nr. | Stand |
|---|---|
| **M7** Datenstände trennen | **erledigt und live** — `readMeFirst`, `live`, `frozenSnapshot` getrennt, Alter des Schnappschusses wird berechnet |
| **M1** AMO-Felder | **erledigt und live** — `download-management` statt `photos-music-videos`, Tag `scholar` statt `security`. Schlüssel des Eigentümerkontos 20041617 kam vom Nutzer, liegt im Vault |
| **M6** Client-Zähler | **erledigt und live** — zählt `clientInfo.name` je Tag, Ausgabe unter `live.clients` |

### Erste Erkenntnis aus M6 (nach 15 Minuten)

Fünf Sitzungen von fünf verschiedenen Clients. Die **echten** darunter:
`glimind-probe`, `mcpbeat`, `mcp` — allesamt Monitore. **Kein Claude, kein
ChatGPT, kein Cursor.**

Das bestätigt die Diagnose aus Abschnitt 3 mit einer zweiten, unabhängigen
Messung: Es sind keine Agent-Clients da, die etwas benutzen könnten. M3
(Verzeichnisse) ist damit die richtige nächste Maßnahme — und ab jetzt
messbar.

### M1 ist jetzt belegt, nicht behauptet

`tools/amo-sichtbarkeit.py`, 14 Suchbegriffe:

| gefunden | Position | | nicht in Top 75 | Treffer |
|---|---:|---|---|---:|
| full page pdf | 1 | | **citation** | 462 |
| citavi | 6 | | **reference manager** | 319 |
| save page as pdf | 9 | | **scholar** | 181 |
| zotero | 10 | | research | 4.854 |
| ris | 15 | | archive webpage | 116 |

Das Add-on rankt, wo sein **Name** passt, und fehlt, wo sein **Nutzen**
liegt. Genau das behebt M1.

## 5. Reihenfolge

| Nr. | Aufwand | Wirkung | Wann |
|---|---|---|---|
| M1 AMO-Felder | Minuten | hoch | sofort |
| M7 Datenstände trennen | klein | Ehrlichkeit | sofort |
| M6 Client-Zähler | klein | ermöglicht Bewertung | vor M3 |
| M4 Server-Beschreibung | klein | mittel | diese Woche |
| M3 Verzeichnisse | mittel | hoch | diese Woche |
| M5 Empfehlungs-Auslöser | mittel | mittel | danach |
| M2 Bewertungen | mittel | hoch für AMO | danach |

M6 vor M3: sonst lässt sich hinterher nicht sagen, ob die Verzeichnisse
etwas gebracht haben.

---

## 6. Was ich nicht empfehle

**Keine Maßnahmen an der Umwandlung**, solange die Entdeckung bei null
liegt. Bessere Werkzeugbeschreibungen, mehr Fähigkeiten, feinere
Installationswege — all das verbessert etwas, das niemand erreicht.

**Keine Zahlen aus dem eingefrorenen Schnappschuss** als Erfolgsbeleg. Sie
messen den Ausschlag der Registry-Eintragung, nicht den Betrieb.

---

## 7. Grenzen dieser Auswertung

- Fenster 23,5 h (kostenloser Cloudflare-Plan). Ein einzelner ruhiger Tag
  kann täuschen — vor jeder Bewertung über mehrere Tage gegenprüfen.
- Der Werkzeugzähler läuft erst seit 15.08. Kein Trend, nur ein Stand.
- User-Agents sind Selbstauskunft. „Echte Agenten ≈ 0" heißt genau: keine
  *erkennbaren*. Ein Agent ohne Kennung ist darin nicht sichtbar.
- Zwei der gezählten Werkzeugaufrufe stammen aus dieser Analyse.

---

## 8. Nachtrag 18./19.08.2026 — zwei Tage Client-Zähler

### Die Zahl, für die M6 gebaut wurde

839 Sitzungen von 55 verschiedenen Clients seit 17.08.

| Herkunft | Sitzungen | Anteil |
|---|---:|---:|
| Monitore und Verzeichnisse | 537 | 64,0 % |
| **eigene Prüfaufrufe (siehe unten)** | **244** | **29,1 %** |
| alles übrige | 58 | 6,9 % |

Und die 58 „übrigen" halten der Nachschau nicht stand. Darunter:
`mcp-rugpull-research`, `schema-survey`, `sasame-audit`, `mcpvet`,
`mcpgrade`, `mcp-scraper`, `reliability-bureau-spike`, `x402-observatory`,
`ProPlus.Mcp.ToolDiscovery.Console` — allesamt Audit-, Scan- und
Katalogwerkzeuge, nur nicht vom Namensmuster erfasst. Wirklich
unzuordenbar bleiben eine Handvoll: `k0`, `p`, `otter`, `test`, `mcp`.

**Kein einziger benannter Agent-Client.** Kein `claude-ai`, kein
`claude-desktop`, kein `chatgpt`, kein `cursor`, kein `windsurf`,
kein `vscode`.

Damit ist die Diagnose aus Abschnitt 3 nicht mehr erschlossen, sondern
gemessen: **Es sind keine Agent-Clients da.** M3 bleibt die richtige
nächste Maßnahme.

### Eigene Verunreinigung — 29 % der Sitzungen

Die Abnahme der Worker-Deploys lief über Warteschleifen der Form
`until curl … grep -q "Cite or capture"; do sleep 15; done`. Jeder
Durchlauf öffnete eine `initialize`-Sitzung mit
`clientInfo.name = "m4-abnahme"`. Ergebnis: **240 synthetische Sitzungen**,
dazu vier weitere aus Einzelprüfungen.

Das verzerrt genau die Kennzahl, die zur Bewertung von M3 dienen soll —
und zwar in die schmeichelhafte Richtung.

**Nicht entfernbar:** Der Worker-Token hat keine KV-Leserechte,
`wrangler kv key list` liefert `[]`. Die Schlüssel bleiben stehen.

**Konsequenz für die Auswertung:** Als Ausgangswert für M3 gilt **nicht**
die Gesamtzahl, sondern der Anteil „alles übrige" — heute 58 Sitzungen in
zwei Tagen, also rund 29 am Tag, praktisch vollständig Scanner.

**Konsequenz für künftige Abnahmen:** Prüfschleifen gegen einen Endpunkt,
der sich selbst zählt, brauchen einen eigenen, klar erkennbaren Namen —
oder besser einen Pfad, der nicht gezählt wird. Eine Messung, die durch
ihre eigene Kontrolle wächst, misst die Kontrolle.

### Nebenbefund: Werkzeugaufrufe

6.756 seit 15.08. — gegenüber 130 am 17.08. mittags. Der Sprung stammt
aus derselben Quelle wie die Sitzungen: Scanner, die reihum jedes Werkzeug
aufrufen. Die Zahl taugt ohne Aufschlüsselung nach Aufrufer nicht als
Erfolgsmaß.

### AMO nach der Umstellung

Tägliche Nutzer **31 → 38** (+22,6 %) binnen zwei Tagen nach M1. Ein
einzelner Messpunkt, keine Kausalität — der Wert schwankt auch ohne
Zutun. Die belastbare Prüfung ist die Suchposition:
`python3 tools/amo-sichtbarkeit.py`, Erfolgskriterium sind die drei
Lücken `citation`, `reference manager`, `scholar`.
