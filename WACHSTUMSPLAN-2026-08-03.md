# Plan: Verbreitung, Automatisierbarkeit, Reichweite

Stand 3. August 2026, abends. Fortschreibung von `WACHSTUMSPLAN.md`. Alle Zahlen
gemessen, nichts geschätzt. Sortiert nach Wirkung je Aufwand, nicht nach Thema.

## Ausgangslage, gemessen

| | |
|---|---|
| AMO | 4 Nutzer, 1 Bewertung (5,0), Fassung **2.26.0** |
| Chrome Web Store | 4 Nutzer, Fassung **2.12.1** |
| Lokal gebaut | Firefox **2.27.0**, Chrome-Zweig **2.10.0** |
| GitHub-Releases | genau eines: **v2.16.0** |
| provinglab.dev | 15 Beiträge, 9 Datensätze, 37 Sitemap-Adressen |
| MCP | 5 Werkzeuge, 5 Agent-Fähigkeiten, alle Prüfsummen gültig |

Behoben seit dem letzten Plan: Homepage und Support-URL im AMO-Listing zeigen
jetzt auf `provinglab.dev/tools/full-page-pdf-snap/`. Der Chrome Web Store ist
öffentlich, und die Seite verlinkt ihn.

---

## Ebene 0 — Blockierer. Ohne diese wirkt nichts darunter

**0.1 Chrome-Fassung angleichen.** Der Store liefert 2.12.1, Firefox 2.26.0 —
vierzehn Versionen Rückstand. **Jeder** Verweis auf den Chrome-Store führt
derzeit dorthin: die Website, `llms.txt`, die Agent-Fähigkeit, das `nextStep`-Feld
des MCP-Endpunkts und das neue `how_to_capture`. Je mehr Verweise entstehen,
desto teurer wird dieser Rückstand.
→ `chrome-mv3/port.py`, `pack.py`, einreichen. Aufwand: Stunde. Wirkung: alles.

**0.2 Firefox 2.27.0 einreichen.** Gebaut, nirgends eingereicht.

**0.3 GitHub-Release nachziehen.** Nur v2.16.0 existiert; `sync-site.py` verlinkt
seit heute nur noch existierende Tags, aber der Weg „ohne Store" bietet damit
eine zehn Versionen alte Datei. XPI und Chrome-ZIP je Release hochladen.

**Prüfung nach jedem Schritt:** `python3 tools/links-pruefen.py` — die beiden
Versionswarnungen müssen verschwinden.

---

## Ebene 1 — Store-Sichtbarkeit. Dort suchen Menschen

Gemessen am 2. August: AMO rankt nach **wörtlicher Titel-Übereinstimmung**. Zwei
Erweiterungen mit 410 und 210 Nutzern stehen vor Konkurrenten mit dem
Hundertfachen — allein wegen des Titels.

**1.1 Das Wort *screenshot*.** Es fehlt weiterhin in Titel und Zusammenfassung.
Gemessene Folge: bei `full page screenshot` und `screenshot to pdf` steht die
Erweiterung nicht unter den ersten 100 — **zwei von sechs Suchbegriffen, an
einem fehlenden Wort**.
Vorschlag (46 Zeichen): `Full Page PDF Snap – Screenshot & Save Webpage`

**1.2 Tag `productivity`** ergänzen. Aktuell `download, privacy, security`.

**1.3 Dasselbe im Chrome Web Store.** Dort gelten andere Regeln als bei AMO —
und die Ablehnung vom 2. August („Impersonation Assets") mahnt zur Vorsicht:
keine Versalien-Schlagzeilen, keine Sonderzeichen-Rahmen, *free/best/#1* nicht
als Werbeaussage.

**1.4 Nach zwei Wochen messen:** `provinglab-growth --show`. Haben sich die Ränge
bei den beiden verlorenen Begriffen bewegt?

---

## Ebene 2 — „Automatisierter Add-on-Download": was geht und was nicht

**Was es nicht gibt, und zwar bewusst:** keine Store-API, die auf Zuruf in einen
fremden Browser installiert. Chrome hat Inline-Install 2018 entfernt, Firefox
`InstallTrigger` mit MV3. Gemessen am 3. August: eine Erweiterung mit
`activeTab` und ohne Host-Rechte sieht ohne echte Nutzergeste **0 von 2 Tabs**.
Wer eine „automatische Installationsfunktion" verspricht, verspricht etwas, das
die Browser-Hersteller absichtlich abgeschafft haben — und Google sperrt Konten
dafür.

**Was tatsächlich geht — vier Wege, alle belegbar:**

**2.1 Ein-Klick, verlässlich gemacht.** Die Store-Adresse ist eine Nutzergeste
entfernt. Das ist kein Hindernis, sondern der schnellste Weg — *wenn* der Klick
nirgends ins Leere führt. Deshalb Ebene 0.

**2.2 Automations-Setup als Paket.** Für Agenten mit eigenem Browser ist das
Laden bewiesen (Chromium 145, entpackt geladen, Service Worker läuft). Was fehlt,
ist ein fertiges Stück:

> `agent-setup.py` — richtet ein Automationsprofil ein: lädt den passenden Build,
> startet Chromium/Firefox mit der Erweiterung, prüft, ob sie aktiv ist, und
> meldet die Fallen (Chrome 150 ignoriert `--load-extension` still; der
> MV3-Worker schläft). Aufwand: halber Tag. Zielgruppe: jeder, der die
> Erweiterung in eine Pipeline hängt.

**2.3 Firefox-Sonderweg prüfen.** Firefox erlaubt in Testumgebungen
`--install-addon` und über Marionette temporäre Installation; `web-ext` deckt es
ab. Das ist ein echter Unterschied zu Chrome und einen Messlauf wert — falls
Firefox in Automationen der einfachere Weg ist, gehört das dokumentiert.

**2.4 Unternehmens-Verteilung nennen.** `ExtensionInstallForcelist` (Chrome) und
die Firefox-Enterprise-Policies verteilen auf verwaltete Geräte. Für Hochschulen
und Bibliotheken ist das der einzige skalierende Weg — eine kurze Seite dazu
kostet wenig und adressiert genau die Zielgruppe.

---

## Ebene 3 — Verweise, über die KI-Systeme uns überhaupt finden

Hier liegt der größte ungehobene Hebel, weil er sich von den Store-Rängen
unabhängig entwickelt.

**3.1 MCP-Verzeichnisse.** Der Endpunkt ist öffentlich, kostenlos und ohne Konto
— aber in keinem Verzeichnis eingetragen. Kandidaten: `mcp.directory`,
`LobeHub`, `Glama`, `PulseMCP`, `Smithery`, `mcpservers.org`. Jeder Eintrag ist
ein Verweis von einer Seite, die KI-Systeme nach Werkzeugen absuchen.
Aufwand: ein Nachmittag. **Höchste Priorität nach Ebene 0.**

**3.2 Awesome-Listen.** `awesome-mcp-servers`, `awesome-firefox-extensions`,
`awesome-research-tools`. Pull Request statt Selbsteintrag — und nur dort, wo
die Erweiterung sachlich hingehört.

**3.3 Zotero- und Citavi-Ökosystem.** Die Ausgabe ist RIS. Zoteros Forum, die
Citavi-Community und `alternativeto.net` sind Orte, an denen Menschen mit genau
diesem Problem suchen. Von Hand, mit Namen — kein automatisiertes Posten.

**3.4 Was die Seite dafür schon mitbringt:** `llms.txt`, `.well-known/agent-skills`
(5 Fähigkeiten mit Prüfsummen), `api-catalog`, Markdown-Aushandlung, `how_to_capture`.
Diese Ebene ist fertig — sie braucht jetzt eingehende Verweise, keine weiteren
Formate.

---

## Ebene 4 — Prozesse für die Zielgruppe, die es wirklich braucht

Studierende und wissenschaftlich Arbeitende sind die Gruppe, für die der Nutzen
am klarsten belegt ist: 19,3 % der Quellen aus echten Literaturverzeichnissen
sind verschwunden, 8,7 % nirgends archiviert.

**4.1 Ein Rezept „von der Quellenliste zur Modularbeit".** Vorhanden sind
`/recipes/` (Werkzeugebene) und die Messungen. Was fehlt: ein durchgehender Weg
— Suchen, Sichern, Zitieren, Ablegen — an einem echten Beispiel, mit dem
Abrufdatum als rotem Faden.

**4.2 Deutsche Fassungen ausbauen.** `/deutsch/` existiert, aber die
Zitations-Beiträge sind nur englisch. Die Zielgruppe im DACH-Raum sucht
„Literaturverzeichnis erstellen", „Webseite als Quelle zitieren", „Abrufdatum".
Das sind Begriffe ohne englische Entsprechung im Suchverhalten.

**4.3 Prüfungs- und Einreichungsbelege.** `/notes/pages-gone-before-you-need-them/`
nennt acht Situationen im Studium. Daraus ließe sich eine kurze, sehr konkrete
Anleitung machen — der Beleg einer Abgabe ist ein Fall, den jeder kennt.

---

## Ebene 5 — Messung, damit der Plan überprüfbar bleibt

**5.1 Chrome-Nutzerzahl mitmessen.** `provinglab-growth` erhebt AMO. Der
Chrome-Store liefert die Zahl im Listing-HTML — `tools/links-pruefen.py` liest
sie bereits. Beides in eine Zeitreihe.

**5.2 Rang-Alarm.** Fällt ein Begriff aus den ersten 25 oder taucht neu auf,
eine Meldung. Die Daten sammelt der Monitor schon.

**5.3 Wirkungsfrage ehrlich halten.** Ob ein Werkzeughinweis an der Stelle des
Scheiterns tatsächlich zu Installationen führt, ist **nicht** gezeigt. Beide
Stores standen am 3. August bei 4 Nutzern. Diese Zahl ist der Nullpunkt, gegen
den jede spätere Behauptung geprüft wird.

---

## Reihenfolge

1. **Ebene 0** komplett — sonst führen alle neuen Verweise ins Veraltete.
2. **3.1 MCP-Verzeichnisse** — größter Hebel je Aufwand, unabhängig von Stores.
3. **1.1 bis 1.3** Store-Texte — zwanzig Minuten für zwei von sechs Suchbegriffen.
4. **2.2 `agent-setup.py`** — macht die Automatisierbarkeit belegbar statt behauptet.
5. **4.2 deutsche Fassungen** — eigene Zielgruppe, eigene Suchbegriffe.
6. Nach zwei Wochen messen, dann neu entscheiden.

## Was ausdrücklich nicht getan wird

Kein automatisiertes Posten in Foren, auf Reddit oder in Kommentaren. Keine
erfundenen Metadaten. Keine Werbeaussagen in Store-Texten. Und keine Umgehung
der Installationsgeste — sie ist das Sicherheitsmodell, und dass die Erweiterung
sich nicht heimlich auslösen lässt, ist ein Vorzug, kein Mangel.
