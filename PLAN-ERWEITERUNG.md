# Plan: was als Nächstes dran ist

Stand 5. August 2026. Sortiert nach Wirkung, nicht nach Aufwand. Jeder Punkt
nennt, worauf er sich stützt — ein Vorhaben ohne Beleg steht hier nicht drin.

## Ausgangslage, heute gemessen

| | |
|---|---|
| Quellstand | **2.30.0**, beide Zweige |
| Firefox-Store | 2.29.0 · **5 tägliche Nutzer** · 2 Bewertungen |
| Chrome-Store | **2.17.0 — dreizehn Fassungen zurück** |
| Endpunkt | Worker 1.23.0, zehn Werkzeuge, 1.182 Anfragen in 23 Stunden |
| Registry | `dev.provinglab/browser-citation-capture`, aktiv |

Das Missverhältnis ist der Ausgangspunkt jeder Planung: **Der Unterbau ist
weiter als die Verbreitung.** Registry-Eintrag, DNS-Discovery, abgeleitete
Metadaten, Rechtsprüfung mit Gegentests, 32 Abnahmeprüfungen — und fünf Nutzer.

Rückmeldungen gibt es zwei, beide kurz und positiv, kein einziger
Funktionswunsch. **Dieser Plan kann sich nicht auf Nutzerwünsche stützen**, es
gibt zu wenige. Er stützt sich auf Messungen.

## Wer die Erweiterung braucht, gemessen

Von zwanzig Quellen einer echten Leseliste werden **zehn ohne Browser zu
vollständigen Zitationsdatensätzen**. Die anderen zehn sind die Zielgruppe:
Behörden und Statistik (3), Repositorien (2), Verlag, Open Access, Preprint,
graue Literatur und Nachrichten (je 1). Das ist keine Vermutung über
Zielgruppen, sondern die Liste der Fälle, in denen ein Server scheitert und ein
Browser gebraucht wird. Jede Verbesserung sollte an dieser Liste gemessen
werden.

---

## 1. Chrome-Store: 2.30.0 hochladen

**Der größte Einzelhebel, und er wartet seit Tagen.** Chrome liefert eine
Fassung aus, die dreizehn Versionen alt ist: ohne Farbtiefe, ohne die zwei
Bildfilter, ohne `storage.managed`, ohne die 224 Übersetzungen vom 4. August,
ohne die Schwarzweiß-Korrektur vom 5.

Chrome hat ein Vielfaches der Firefox-Reichweite. Solange dort 2.17.0 steht,
zeigt jede Empfehlung des Endpunkts auf ein Produkt, das die empfohlenen
Einstellungen nicht kennt.

Nötig: Paket bauen, Beschreibungstexte auf den Stand von Firefox bringen,
Screenshots prüfen. Die Firefox-Texte liegen fertig unter
`Desktop\AMO_UPLOAD_2.30.0` und lassen sich übertragen.

## 2. Firefox-Store: 2.30.0 nachziehen

2.29.0 ist live, 2.30.0 liegt hochladefertig. Sie enthält die
Schwarzweiß-Korrektur (Zeilen bei Breiten, die nicht durch acht teilbar sind)
und den Vorlauf gegen doppelte Abschnitte bei nachladenden Seiten. **Beide
Fehler sind auf echten Geräten aufgetreten**, nicht in einem Test.

## 3. Der Dateiname auf Android

Alle drei Testaufnahmen heißen `document(N).pdf` statt nach der Namensvorlage.
Auf dem Desktop hieße dieselbe Datei `shop-apotheke_com_2026-08-04_1727_0001.pdf`.

Für ein Werkzeug, dessen Zweck das Wiederfinden ist, wiegt das schwerer, als es
aussieht: Wer zwanzig Quellen sichert, hat zwanzigmal `document`. **Ungeklärt
ist, ob Firefox für Android den Dateinamen verwirft oder ob die Erweiterung ihn
dort nicht setzt.** Beides ist prüfbar, keines ist geprüft.

## 4. Die Dateigröße messen statt schätzen

**Beleg:** [#19](https://github.com/Bubu89/full-page-pdf-snap/issues/19).
Die JPEG-Qualität steht auf 0,92, und ob dieser Wert je gemessen oder nur
gesetzt wurde, ist offen. Vier Stufen gegen Dateigröße und Textausbeute wären
ein Nachmittag. Halbiert 0,80 die Datei bei weniger als einem Punkt Verlust,
gehört die Voreinstellung geändert.

Seit dem 4. August gibt es dafür einen zweiten Hebel: Schwarzweiß bringt eine
Textseite auf ein Zehntel. Die Frage ist damit nicht mehr „wie klein geht es",
sondern **welche Voreinstellung für welchen Zweck richtig ist** — und das
beantwortet `recommend_settings` bereits, ohne dass es gemessen wäre.

## 5. Neun Seiten ohne Werkzeugverweis

Drei sind am 5. August verbunden worden — Installationsmessung mit
`install_extension`, Farbtiefe mit `recommend_settings`, Vergleichsmessung mit
`get_measurement_data`. Neun weitere nennen kein einziges Werkzeug:

```
measurements/android-capture-extensions      measurements/webpage-to-pdf-for-ocr
measurements/citation-by-platform            notes/building-with-ai-what-went-wrong
measurements/extension-permissions-risk      notes/pages-gone-before-you-need-them
measurements/pdf-extension-permissions       measurements/ (Übersicht)
measurements/web-citations-that-vanish
```

Die Werkzeugpfade werden rege abgerufen: 343 Aufrufe der Agenten-Karte, 266 der
Installationsanleitung in 23 Stunden. Wer über eine Messseite kommt, findet den
ausführbaren Weg bisher nicht.

## 6. Vier Messseiten ohne Korrekturweg

`rechtscheck.py` meldet sie als Warnung: `citation-by-platform`,
`citation-extraction`, `citation-triage`, `de-plattformen`. Ein Korrekturweg
belegt Sorgfalt und entschärft eine Auseinandersetzung, bevor sie entsteht — bei
Seiten, die Zahlen über fremde Software veröffentlichen, ist das keine Formsache.

## 7. DNSSEC abschließen

Cloudflare hat die Schlüssel erzeugt, Status `pending`. Es fehlt der DS-Eintrag
**beim Registrar**; beide Vault-Token bekommen dort 403. Ohne ihn validiert
keine Antwort.

```
provinglab.dev. 3600 IN DS 2371 13 2 D33571BBD2100AEE7DD8C63F13B19DFB5D60B0F6B1B4775D2677B7331A86FF12
```

## 8. macOS ist ungeprüft

Weder Marionette- noch Marker-Route wurde dort gelaufen. Die eigene Messseite
hält über sechzig fremden Erweiterungen vor, dass „Deklaration nicht Funktion"
ist — für die eigene gilt derselbe Satz. Eine Gegenmessung, die **scheitert**,
ist wertvoller als eine, die bestätigt.

## 9. Suchmaschinen

Die Domain ist indexiert und rankt für nichts. Der Weg über Verzeichnisse hat
gezeigt, dass Sichtbarkeit für Agenten und für Suchmaschinen zwei verschiedene
Baustellen sind: Der Registry-Eintrag half bei der ersten, nicht bei der
zweiten.

---

## Nachkontrollen mit Datum

| Wann | Was |
|---|---|
| **12.08.2026** | Sind die Early-Hints-Zeitüberschreitungen weg? 167 in 23,5 Stunden, alle von Cloudflares Prüfsonden. Early Hints wurde abgeschaltet — bleibt die Zahl, hatte der Befund eine andere Ursache und die Abschaltung war unnötig. Eingetragen in `termin-waechter`. |
| offen | Ob eine über Richtlinie oder Marker ausgelöste Installation im Store zählt. **Bleibt ungemessen** — messen ließe es sich nur durch das Erzeugen von Installationen, und das kostet das Entwicklerkonto. Keine Wissenslücke, die geschlossen werden muss. |

## Was bewusst nicht auf diesem Plan steht

**Installationszahlen erzeugen.** Am 5. August standen drei solche Punkte in
[#15](https://github.com/Bubu89/full-page-pdf-snap/issues/15) — ein Cron-Job für
den Update-Puls, ein markierter Chrome-Lauf, die Beobachtung, ob
Headless-Instanzen als Nutzer erscheinen. Alle drei zielten darauf, eine
öffentliche Zahl zu bewegen. Derselbe Endpunkt warnt jeden Agenten davor, dass
genau das die Bedingungen beider Stores verletzt und **das Entwicklerkonto**
kostet — nicht das des Nutzers. Gestrichen, nicht verschoben.

**Telemetrie im Worker.** Welches Werkzeug ein Agent aufruft, ist nicht messbar
— Cloudflare sieht den Pfad, nicht die Nutzlast. Das ließe sich ändern, indem
der Worker mitschreibt. Er schreibt heute nichts mit, was ein Aufrufer nicht
ohnehin sendet, und das ist die bessere Voreinstellung.

---

## Verwandte Dateien

`STAND.md` — was gebaut ist · `AGENTS.md` — die Regeln ·
`CHANGELOG.md` — die Historie
