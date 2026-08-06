# Plan: beste Qualität für Agenten-Navigation

Stand 6. August 2026. Jeder Punkt trägt seinen Messstand — **gemessen**,
**gebaut** (Prototyp läuft), **zu messen** (noch Vermutung).

## Der Befund, der alles ordnet: zwei Leser, ein Dokument

Ein aufgenommenes PDF wird von zwei völlig verschiedenen Lesern benutzt:

| | braucht | Größe heute |
|---|---|---|
| **Mensch** | ein Bild, das aussieht wie die Seite | 618–792 kB |
| **Agent** | Text, Verweise, Lage, Rolle, Herkunft | 0 kB — *ist nicht drin* |

Heute bekommt der Agent nur das Bild des Menschen und muss daraus zurückrechnen,
was ohnehin bekannt war. Das ist der eigentliche Verlust — nicht die Kompression.

**Daraus folgt die Priorität:** Erst die Struktur hineinlegen, dann über
Bildqualität reden. Die Struktur kostet zusammen **52 kB, unter neun Prozent
des Bildes**, und macht die Bildqualität für den Maschinenpfad fast belanglos.

## Die Schwarzweiß-Frage, gemessen

Gemessen an 117 Verweisen mit auswertbarer Schrift auf einer echten Seite
(`daten/2026-08-06-farbe.json`):

| | |
|---|---|
| Verweise **farbig** abgesetzt | 95 % |
| in **Graustufen** noch vom Fließtext unterscheidbar | 97 % |
| in **1 bit Schwarzweiß** zu identischem Schwarz | **17 % verloren** |

Farbe ist auf einer Webseite kein Schmuck, sondern Zustand: Ein Verweis ist
blau, eine Warnung rot, ein abgeschaltetes Feld grau. Graustufen erhalten das
weitgehend, weil Blau heller ist als schwarzer Text. Die harte Schwelle bei 128
wirft es weg.

**Die Antwort ist deshalb bedingt:**

- **Mit** eingebetteter Linkkarte ist Schwarzweiß der beste Modus — der Agent
  liest die Verweise aus dem Anhang, nicht aus dem Bild. 57 kB statt 618 kB.
- **Ohne** sie kostet Schwarzweiß 17 % der Verweisinformation. Dann ist
  **Graustufen** der richtige Sparmodus, nicht 1 bit.

Der Modus ist also keine Geschmacksfrage, sondern hängt daran, ob die Struktur
im Dokument liegt. *Grenze: eine Seite, ein Farbschema. Seiten mit subtileren
Verweisfarben wurden nicht gemessen.*

## Stufe 1 — die Struktur ins Dokument (größte Wirkung, geringste Kosten)

| # | Was | Kosten | Stand |
|---|---|---|---|
| 1 | **Unsichtbare Textebene** (`3 Tr`) | **39 kB** = 6,4 % | gemessen |
| 2 | **Linkkarte als Anhang** (`/EmbeddedFiles`) | **13 kB** = 2 % | gebaut |
| 3 | **Klickbare Verweise** (`/Annots /Link`) | vernachlässigbar | gebaut |
| 4 | **Herkunft als XMP** (`/Metadata`) | 0,5 kB | gebaut |

**Punkt 1 ist der stärkste des ganzen Plans.** Er macht die Aufnahme
durchsuchbar und kopierbar — **ohne OCR und damit ohne Erkennungsfehler**, weil
der Text aus dem Dokument selbst stammt statt aus einer Bilderkennung. 2.671
Textstücke, 67.029 Zeichen, komprimiert 39 kB. Jede andere Bildschirmaufnahme
der Welt braucht dafür OCR und liefert Fehler.

Punkt 2 löst nebenbei ein bestehendes Problem: Die `.links.json` liegt heute
*neben* der Datei und geht beim Weitergeben verloren.

Alle vier mit poppler und pypdf gegengelesen. **Ungeprüft: Acrobat, Firefox,
Chrome, Android** — das ist das Tor zu Stufe 1 und kommt zuerst.

## Stufe 2 — der Bildpfad

| # | Was | Wirkung | Stand |
|---|---|---|---|
| 5 | JPEG **0.85 statt 0.92** | −22 %, kein sichtbarer Unterschied | gemessen |
| 6 | **Graustufen** als Sparmodus, 1 bit nur mit Karte | 17 % Verweise gerettet | gemessen |
| 7 | Bildkacheln statt eines Riesenbildes | weniger Spitzenspeicher | zu messen |

Zu Punkt 5: PSNR fällt von 44,9 auf 40,6 dB, an Textkanten von 48,3 auf 44,4 —
beides im Bereich „für das Auge nicht unterscheidbar". Zwei Ausschnitte bei 2×
Vergrößerung nebeneinander bestätigen das. *Grenze: Textseite auf weißem Grund
ist der für JPEG günstige Fall.*

**Nicht weiterverfolgen** (gemessen, lohnt nicht): CCITT Gruppe 4 spart 2–7 %
gegenüber Flate, JPEG 2000 ist größer, LZW schlechter.

**JBIG2 offen** — `jbig2enc` fehlt, der einzige Kandidat mit echtem Vorsprung
bei Schwarzweiß. Nur die verlustfreie Betriebsart kommt in Frage; die
verlustbehaftete hat historisch Ziffern vertauscht, was ein Belegwerkzeug
disqualifiziert.

## Stufe 3 — Struktur, die Navigation erst möglich macht

| # | Was | Nutzen für einen Agenten | Stand |
|---|---|---|---|
| 8 | **Lesezeichen** (`/Outlines`) aus H1–H6 | springt zum Abschnitt statt zu scrollen | zu bauen |
| 9 | **Rollen in der Karte** (Gerüst / Inhalt) | 741 von 1.528 Verweisen sind Gerüst | im Schwesterprojekt gemessen |
| 10 | **Sichtbarkeitsprüfung** vor dem Eintragen | 45 % der Verweise sind unsichtbar | im Schwesterprojekt gebaut |
| 11 | **Ersatzbeschriftung** (`aria-label`, `title`, `alt`) | 8 % der Verweise sind sonst stumm | im Schwesterprojekt gebaut |
| 12 | **Suchfeld der Seite** in die Karte | Ziel per Anfrage statt per Verweisliste | zu messen |
| 13 | **Tagged PDF** (`/StructTreeRoot`) | Überschriftenhierarchie maschinenlesbar | zu bauen |
| 14 | **Hürden-Vermerk** (Anmeldung, Bezahlschranke) | Agent weiß, warum die Seite unvollständig ist | im Schwesterprojekt gebaut |

Die Punkte 9 bis 11 und 14 sind im Wegweiser bereits gemessen und gebaut. Sie
hier einzutragen kostet fast nichts — der Sammler läuft ohnehin.

Punkt 12 ist der interessanteste ungemessene: Auf drei von sechs Seiten steht
ein Suchformular, auf zwei eine OpenSearch-Beschreibung. Wer „finde X" sucht,
müsste dann keine 833 Verweise bewerten, sondern eine Anfrage stellen.

## Reihenfolge

1. **Reader-Prüfung** der vier Metaebenen (Acrobat, Firefox, Chrome, Android) —
   Tor zu allem Weiteren, alles andere hängt daran
2. **Textebene** (Punkt 1) — größter Einzelnutzen, 6,4 % Kosten
3. **Linkkarte als Anhang + klickbare Verweise + XMP** (2–4) — zusammen 2 %
4. **Rollen, Sichtbarkeit, Ersatzbeschriftung, Hürden** (9–11, 14) — fertig
   gemessen, nur zu übertragen
5. **JPEG 0.85 und Graustufen-Regel** (5–6) — misst sich selbst
6. **Lesezeichen** (8), dann **Suchfeld** (12) nach Messung
7. **Tagged PDF** (13) und **JBIG2** — beide erst, wenn die Reihen davor stehen

## Was in diesem Plan Vermutung bleibt

- Ob Anzeigeprogramme außer poppler und pypdf die Anhänge zeigen
- Ob die Textebene bei Seiten mit ungewöhnlicher Schriftführung
  (Spalten, rechts-nach-links, vertikal) an der richtigen Stelle landet
- Ob Kacheln den Spitzenspeicher tatsächlich senken
- Ob JBIG2 verlustfrei genug spart, um den Kodierer zu rechtfertigen
- Ob das Suchfeld schneller ans Ziel führt als die Rangfolge
