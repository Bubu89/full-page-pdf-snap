# AGENTS.md

Anleitung für KI-Agenten, die an diesem Projekt arbeiten. Gelesen von Claude
Code, Codex, Cursor, Copilot und allem, was der `agents.md`-Konvention folgt.
Menschen lesen besser die [README](README.md) — hier steht, was ein Agent
wissen muss, bevor er etwas ändert.

## Worum es geht

`provinglab.dev` veröffentlicht **Messungen zu Browser-Werkzeugen und
Zitationsdaten** und die Erweiterung *Full Page PDF Snap*. Der Anspruch der
Seite ist eng: **Jede Zahl hat eine Methode, Rohdaten und einen Kontrolllauf.**
Was sich nicht nachrechnen lässt, wird nicht geschrieben.

Das ist keine Stilfrage, sondern die Bedingung, unter der die Seite zitiert
werden kann. Ein Beitrag, der eine Zahl ohne Beleg einführt, ist schädlicher als
kein Beitrag.

## Vor der ersten Änderung

```bash
python3 rechtscheck.py          # muss 0 Fehler melden
node --test tests/*.mjs         # muss vollstaendig gruen sein
python3 tools/links-pruefen.py  # interne Ziele und Store-Stände
```

Läuft eines davon schon vorher rot, ist das der erste Befund — melde ihn, statt
darauf aufzubauen.

## Die Regeln, die hier anders sind als üblich

**1. Belegpflicht vor Formulierung.** Jede Tatsachenbehauptung braucht Quelle
und Abrufdatum, oder sie wird zur Meinung umformuliert, oder sie fällt raus.
`rechtscheck.py` prüft das maschinell und blockiert die Auslieferung.

**2. Keine Aussage über Absichten Dritter.** „MDPI blockiert absichtlich" ist
beweispflichtig und nicht beweisbar. „Der Server antwortete mit 403" ist eine
Beobachtung. Der Prüfer kennt das Muster und schlägt an.

**3. Ein Vergleich, den das eigene Werkzeug nur gewinnt, ist Werbung.** Jede
Gegenüberstellung nennt mindestens eine Kategorie, in der die Alternative besser
ist. Der Druckexport des Browsers gewinnt beim Text — das steht so auf der
Seite und bleibt dort.

**4. Kein Ergebnis ist ein Fehler, kein Nullwert.** Wenn eine Messung 0 von 20
liefert, ist zuerst die Messung verdächtig. Am selben Tag ist das dreimal
passiert: ein Prüfer verglich Bytes statt Adressen, einer löste relative Pfade
falsch auf, einer fand sich selbst.

**5. Deutsch für Kommentare und Dokumentation, Englisch für die Seite.** Die
Kommentare erklären **warum**, nicht was. Ein Kommentar, der den Code
wiederholt, wird gelöscht.

## Wie die Seite gebaut wird

Kein Framework, kein Bundler. Jede Seite entsteht aus einem `build-*.py`, das
Kopf und Fuß aus einer bestehenden Seite übernimmt, damit Navigation und Stil
nicht auseinanderlaufen.

| Datei | Erzeugt |
|---|---|
| `build-*-post.py` | je einen Beitrag |
| `build-einstiegsseiten.py` | `/how-to/`, `/anleitung/`, `/for-agents/` |
| `build-sitemap.py` | `docs/sitemap.xml` — **nie von Hand** |
| `build-feed.py` | `docs/feed.xml` |
| `build-versionen.py` | `/.well-known/extension-versions.json` |
| `chrome-mv3/port.py` | den Chrome-Zweig aus den Firefox-Quellen |

**Falle, die zweimal zugeschlagen hat:** Diese Skripte nutzen f-Strings. Ein
eingebetteter Textblock mit `{NAME}` wird zu `{{NAME}}` maskiert — und landet
dann als literale Klammer auf der ausgelieferten Seite. Die Pipeline prüft
darauf; lokal hilft `grep -rE '\{[A-Z_]{3,}\}' docs`.

## Der Endpunkt

`worker/mcp.js` ist ein Cloudflare Worker auf der Route `provinglab.dev/*`. Er
beantwortet `/mcp` und reicht alles andere durch. **Ein Fehler dort nimmt die
ganze Seite mit** — deshalb fällt jeder unerwartete Fehler auf die unveränderte
Antwort von GitHub Pages zurück, und das muss so bleiben.

Ausliefern übernimmt die Pipeline bei einer Änderung an `worker/`. Von Hand nur
mit einem Token, das ausschließlich Worker-Skripte schreiben darf.

## Was ohne Rückfrage nicht geändert wird

- **Berechtigungen im Manifest.** `activeTab` und keine Host-Rechte sind der
  Kern des Versprechens und in mehreren Messungen belegt.
- **Der Haftungsausschluss** und die Offenlegungen auf `/about/`.
- **Versionsnummern.** `bump-version.py` ist der einzige Weg; eine vergebene
  Nummer fällt beim Store-Upload durch.
- **Alles unter `docs/data/`.** Rohdaten werden nicht nachträglich geglättet.
  Eine Korrektur wird als Korrektur im Beitrag benannt.

## Wo Beiträge am meisten helfen

Sortiert nach Nutzen, nicht nach Aufwand:

1. **Deutsche Fassungen der Zitations-Beiträge.** Die Zielgruppe sucht
   „Abrufdatum", „Literaturverzeichnis erstellen" — Begriffe ohne englische
   Entsprechung, und der Wettbewerb dort ist um ein Vielfaches dünner.
2. **Neue Messungen nach dem vorhandenen Muster.** Eine Frage, die jemand
   tatsächlich stellt, eine reproduzierbare Methode, ein Kontrolllauf, Rohdaten
   nach `docs/data/`.
3. **Gegenmessungen.** Wer eine hier veröffentlichte Zahl nicht reproduzieren
   kann, hat den wertvollsten Beitrag. Die Rohdaten liegen offen, damit genau
   das möglich ist.
4. **Der Endpunkt.** Neue Formate, bessere Erkennung von Sperrseiten, weitere
   Plattformen.

Offene Aufgaben stehen als [Issues](https://github.com/Bubu89/full-page-pdf-snap/issues),
und der Endpunkt liefert sie maschinenlesbar über das Werkzeug `open_work`.

## Mehrere Agenten am selben Baum

An diesem Repository arbeitet **mehr als ein Prozess gleichzeitig** — Claude in
diesem Fenster und Kimi in einem eigenen Terminal. Beide sind gleichberechtigt,
und **Aenderungen des jeweils anderen sind gueltig.** Sie werden nicht
zurueckgesetzt, nicht umgeschrieben und nicht ausgesperrt.

Was schiefgehen kann, ist etwas anderes: Am 3. August 2026 landeten zweimal
fremde Aenderungen in einem Commit, der sie nicht meinte — ein Messdatensatz und
das `pageType`-Feld im Endpunkt. Beide waren gute Arbeit. Nur stand ueber ihnen
eine Nachricht ueber etwas voellig anderes, und niemand hatte sie gelesen.

**Deshalb: kein `git add -A` ohne vorherigen Blick.**

```bash
git status --short          # was liegt ueberhaupt da?
git diff --cached --stat    # was nehme ich mit?
```

Findet sich fremde Arbeit im Baum, gilt der Reihe nach:

1. **Ansehen.** Was tut die Aenderung, und ist sie lauffaehig? Ein Skript, das
   noch nicht durchlaeuft, ist mitten in Arbeit.
2. **Fertig?** Dann einen **eigenen Commit** mit einer Nachricht, die *ihre*
   Aenderung beschreibt — nicht angehaengt an die eigene.
3. **Halbfertig?** Stehen lassen. Der andere Prozess ist noch dran; ein von
   aussen veroeffentlichter Zwischenstand hilft niemandem.

Der Sinn ist nicht Abgrenzung, sondern Nachvollziehbarkeit: Wer in einem halben
Jahr in die Historie sieht, soll finden, *warum* eine Zeile so aussieht — und
das steht in der Commit-Nachricht, die zu ihr gehoert.

**Vor dem Anfangen kurz Bescheid geben.** Wer ein Issue uebernimmt, schreibt
vorher einen Zweizeiler hinein — „arbeite dran, voraussichtlich X". Am
3. August wurde dasselbe Issue von beiden Prozessen bearbeitet und doppelt
kommentiert. Zwei Zeilen haetten das erspart.


## Ein Beitrag gilt als fertig, wenn

- `rechtscheck.py` 0 Fehler meldet,
- die Tests grün sind,
- eine neue Zahl ihre Rohdaten unter `docs/data/` hat,
- `CHANGELOG.md` sagt **was, warum, wie und mit welchem Ergebnis** — der
  Aggregator erfasst nur Dateipfade, das Warum gehört von Hand hinein,
- und keine lokalen Pfade im Auslieferungsstand stehen. Das Repo ist öffentlich,
  eine `.pyc` hat schon einmal das ganze Arbeitsverzeichnis verraten.

## Was hier nicht passiert

Kein automatisiertes Posten in Foren oder Kommentaren. Keine erfundenen
Metadaten. Keine Werbeaussagen in Store-Texten. Und keine Umgehung fremder
Schutzmaßnahmen — wo eine Seite einen Leser aussperrt, wird das berichtet, nicht
umgangen.
