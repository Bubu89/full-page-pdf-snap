# Arbeitsstand

Stand 4. August 2026. Gedacht für den Fall, dass jemand — Mensch oder Agent —
hier weitermacht, ohne die Vorgeschichte im Kopf zu haben. Was gebaut ist, was
offen ist, und was beim Anfassen zu beachten ist.

Die Regeln stehen in [AGENTS.md](AGENTS.md), die Reihenfolge der offenen Arbeit
in [PLAN-ERWEITERUNG.md](PLAN-ERWEITERUNG.md), die Historie im
[CHANGELOG](CHANGELOG.md).

## Wo die Fassungen stehen

| | Version | Bemerkung |
|---|---|---|
| Quellstand Firefox | 2.28.0 | in keinem Store |
| Quellstand Chrome | 2.28.0 | aus denselben Quellen erzeugt (`chrome-mv3/port.py`) |
| Firefox-Store | 2.26.0 | zwei Fassungen zurück |
| Chrome-Store | 2.17.0 | **elf Fassungen zurück** — Paket liegt hochladefertig |
| MCP-Endpunkt | Worker 1.20.0 | acht Werkzeuge |

Der Chrome-Rückstand hatte eine Ursache, keine Nachlässigkeit: `port.py` schrieb
die Version hartkodiert ins Manifest. Behoben; das Packwerkzeug lehnt eine
bereits vergebene Nummer außerdem ab.

## Was in 2.28.0 neu ist und noch niemand im Store hat

**Zwei Bildfilter, je Kachel gewählt.** Die Aufnahme vergleicht `DCTDecode`
(JPEG) mit verlustfreiem `FlateDecode` und nimmt das kleinere. Bei Text gewinnt
Flate deutlich, bei Fotos JPEG — das Verhältnis dreht sich um Faktor sechs,
deshalb wird verglichen statt umgestellt.

**Farbtiefe als Einstellung.** Schwarzweiß bringt eine Textseite auf **8,5 %**
der bisherigen Größe, und Tesseract liest **989 Wörter statt 987** — OCR
binarisiert ohnehin. Auf einer Bildseite bricht es ein (SSIM 0,199), daher
bleibt Farbe die Voreinstellung.

**`storage.managed`.** Dieselbe `policies.json`, die installiert, kann jetzt
auch die Einstellungen setzen. Vorrang: vorgegeben > lokal > Voreinstellung.

## Der Endpunkt

`worker/mcp.js`, ein Cloudflare Worker auf `provinglab.dev/*`. Er beantwortet
`/mcp` und reicht alles andere an GitHub Pages durch — **ein Fehler dort nimmt
die ganze Domain mit**, weshalb jeder unerwartete Fehler auf die unveränderte
Pages-Antwort zurückfällt.

Acht Werkzeuge. Zwei kamen zuletzt dazu:

- **`recommend_settings`** — Aufnahme-Einstellungen je Zweck (`citation`,
  `figure`, `archive`, `ocr`), jeder Wert mit seiner Messung **oder** dem
  ausdrücklichen Vermerk, dass keine existiert. Der `notMeasured`-Block ist
  Absicht: `captureScale`, `tilePx` und `settlingMs` hat nie jemand gemessen.
- **`routeHeadless`** in `how_to_capture` — der ausführbare Installationsweg
  statt einer Store-Adresse zum Anklicken.

## Installation ohne Klick — gemessen, beide Browser

| | Firefox | Chrome |
|---|---|---|
| Weg | Marionette **oder** `policies.json` | External-Extension-Marker |
| Installieren | 4,1 s | 10,7 s |
| Entfernen | ja | 15,0 s |
| Fenster / Eingaben | keins / null | keins / null |
| Woher | lokale XPI bzw. Store | **Store, von Chrome geholt** |

Vollständig nachvollzogen aus reinen Endpunkt-Angaben — ohne Repo, ohne
Vorwissen. Details und Fallen: `tools/erweiterung-fernsteuern.py`,
`vorlagen/README.md`.

**Die Trennlinie verläuft nicht zwischen Rechten, sondern zwischen wessen
Browser es ist.** System-Installation braucht Erhöhung, ein selbst entpackter
Browser nicht.

## Offen, nach Nutzen sortiert

1. **[#18](https://github.com/Bubu89/full-page-pdf-snap/issues/18) — die eigene
   Vergleichsmessung unterschätzt das Produkt.** `/measurements/print-to-pdf-vs-screenshot/`
   nennt 94,8 % gegen 92,7 %; gemessen wurde eine Fassung **ohne Textebene**,
   der Wert ist ein OCR-Ergebnis. Einen Tag später kam die Textebene aus dem
   DOM. **Dreizehn ausgelieferte Seiten tragen die Zahl.** Die Korrektur
   braucht einen echten Browser, weil die Aufnahme ein echtes Eingabe-Ereignis
   verlangt.
2. **Chrome-Upload 2.28.0** — Paket, Texte auf Englisch und Deutsch, fünf
   Bilder und eine Anleitung liegen unter
   `Desktop\PDF_SNAP_STORE_UPLOAD\CHROME_2.27.0\`. Der Store zeigt außerdem
   eine Beschreibung, die ihren ersten Satz wörtlich wiederholt.
3. **[#19](https://github.com/Bubu89/full-page-pdf-snap/issues/19) — Dateigröße.**
   Die JPEG-Qualität steht auf 0,92 und wurde nie über Seitentypen hinweg
   gemessen.
4. **Android** ist im Store-Text genannt und **nie auf einem Gerät geprüft**.
   Die eigene Messseite sagt über sechzig fremde Erweiterungen „Deklaration ist
   nicht Funktion" — für die eigene gilt derselbe Satz.
5. **Endpunkt und Erweiterung kennen einander nicht.** Beide erzeugen
   RIS-Sätze. Ob eine Verbindung Nutzen hätte, ist ungemessen und gehört
   gemessen, bevor sie gebaut wird.

## Betrieb — die zwei Schritte nach jedem Push

```bash
python3 tools/cache-nach-deploy.py   # wartet auf den Pages-Deploy, leert dann
python3 tools/indexnow.py            # meldet die Änderung
```

Der Purge **vor** dem fertigen Deploy ist schlimmer als keiner: Er holt die alte
Fassung frisch an den Edge und hält sie vier Stunden. Genau so passiert.

Vor jedem Commit die vier Prüfungen aus `AGENTS.md`. Was in der Pipeline
blockiert, gehört in diese Liste — `daten-pruefen.py` fehlte dort und kostete
einen roten Lauf.

## Was beim Anfassen leicht schiefgeht

- **`git add -A` ohne Blick.** Zweimal fremde Arbeit in einen Commit gezogen,
  einmal ein Laufprotokoll mit lokalen Pfaden.
- **`str.replace()`, das nicht greift, meldet nichts.** Einmal eine Fassung
  ausgeliefert mit der Behauptung, ein Block sei enthalten — er war es nicht.
  Nach dem Schreiben verifizieren, nicht nach dem Commit.
- **Der `post-commit`-Hook pusht selbst.** Ein eigenes `git push` danach meldet
  „cannot lock ref", obwohl alles draußen ist.
- **Ein neuer Prüfer, der viele Befunde meldet, ist zuerst selbst verdächtig.**
  Bei `seo-pruefen.py` waren sechzehn von zwanzig seine eigenen Fehler.

## Rechtliches

`rechtscheck.py` liest seit dem 4. August auch `worker/mcp.js`. Der Endpunkt
traf dieselben Aussagen wie die Seiten und wurde nie geprüft — `recommend_settings`
beschrieb einen Eingriff per Richtlinie und enthielt keinen einzigen Hinweis.

Drei Regeln blockieren die Auslieferung: **Installationszahlen ohne
Grenzhinweis**, **fremdes Gerät ohne Einwilligung**, **Vermutung als Befund**.
Jede hat einen Gegentest — ein Satz, der anschlagen muss, und einer, der es
nicht darf.

Die Bestandsaufnahme der Angriffsflächen steht in
[RECHTSPRUEFUNG-ANGRIFFSFLAECHEN.md](RECHTSPRUEFUNG-ANGRIFFSFLAECHEN.md).
Offen bleibt dort die Ratenbegrenzung auf `/mcp`, die nur im
Cloudflare-Dashboard setzbar ist.
