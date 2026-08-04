# Plan: das Add-on verbessern

Stand 4. August 2026. Sortiert nach Nutzen, nicht nach Aufwand. Jeder Punkt
nennt, worauf er sich stützt — ein Vorhaben ohne Beleg steht hier nicht drin.

## Ausgangslage, gemessen

| | |
|---|---|
| Firefox-Store | 2.26.0, **4 Nutzer**, 8 Downloads/Woche, 2 Bewertungen (5,0) |
| Chrome-Store | 2.17.0 — **zehn Fassungen zurück** |
| Quellstand | 2.27.0, beide Zweige |
| Rückmeldung | *„Super gelöst! Dankeschön!"* · *„Find ich gut, einfache Handhabung."* |

Zwei kurze, positive Bewertungen und kein einziger Funktionswunsch. **Dieser Plan
kann sich nicht auf Nutzerwünsche stützen** — es gibt zu wenige Nutzer, um daraus
etwas abzuleiten. Er stützt sich auf die eigenen Messungen, und das ist bei
diesem Projekt ohnehin der vorgesehene Weg.

Von siebzehn bisherigen Issues betraf **keines** die Erweiterung. Alle
verbesserten Domain, Endpunkt oder Werkzeuge. Das ist die Lücke, die dieser Plan
schließt.

## Wer das Add-on braucht, gemessen

Von zwanzig Quellen einer echten Leseliste werden **zehn ohne Browser zu
vollständigen Zitationsdatensätzen**. Die anderen zehn sind die Zielgruppe:

| Art der Quelle | Anzahl |
|---|---|
| Behörden und Statistik | 3 |
| Repositorien | 2 |
| Verlag, Open Access, Preprint, graue Literatur, Nachrichten | je 1 |

Das ist keine Vermutung über Zielgruppen, sondern die Liste der Fälle, in denen
ein Server scheitert und ein Browser gebraucht wird. Jede Verbesserung sollte an
dieser Liste gemessen werden.

---

## 1. Die eigene Vergleichsmessung ist überholt — und unterschätzt das Produkt

**Beleg:** [#18](https://github.com/Bubu89/full-page-pdf-snap/issues/18).
`/measurements/print-to-pdf-vs-screenshot/` nennt 94,8 % gegen 92,7 %
Textausbeute. Die Rohdaten sagen dazu `"text_layer": false` und
`"Full Page PDF Snap 2.16.0, then Tesseract 5"` — die gemessene Fassung hatte
keine Textebene, die 92,7 % sind ein **OCR**-Wert. Einen Tag später kam die
Textebene aus dem DOM dazu (Commit `d89992c`, 2. August). Übernommener Text kann
nicht falsch erkannt werden.

**Warum zuerst:** Die Zahlen stehen auf **dreizehn ausgelieferten Seiten**,
Startseite eingeschlossen. Der Satz „der Druckexport gewinnt beim Text" ist
möglicherweise seit zwei Tagen nicht mehr wahr. Eine Messung, die das eigene
Produkt zu schlecht darstellt, ist genauso falsch wie eine, die es zu gut
darstellt — sie fällt nur niemandem auf.

**Aufwand:** ein Messlauf, aber mit Xvfb-Aufbau, weil die Aufnahme ein echtes
Eingabe-Ereignis braucht.

## 2. Die Datei ist sechsmal so groß wie der Druckexport

**Beleg:** [#19](https://github.com/Bubu89/full-page-pdf-snap/issues/19).
6,7 MB gegen 1,1 MB, derselbe Artikel, derselbe Tag. Gemessen und bisher ohne
Einordnung stehengelassen.

**Warum es zählt:** Für einen Belegordner zu einer Abschlussarbeit ist das der
Unterschied zwischen 50 MB und 300 MB. Es fällt beim ersten Beleg nicht auf und
beim dreißigsten sehr.

**Was zu tun ist:** die JPEG-Qualität überhaupt erst einmal messen — vier Stufen,
je Dateigröße und Textausbeute. Ob der heutige Wert je gemessen oder nur gesetzt
wurde, ist offen. Falls 80 % die Datei halbiert und die Ausbeute um weniger als
einen Punkt senkt, ist das eine Voreinstellung, die geändert gehört.

## 3. Der Chrome-Store liegt zehn Fassungen zurück

**Beleg:** `tools/links-pruefen.py` meldet Chrome 2.17.0 gegen Quellstand
2.27.0.

**Ursache ist bekannt und behoben:** `chrome-mv3/port.py` schrieb die Version
hartkodiert ins Manifest, jede Firefox-Fassung zog vorbei. Was fehlt, ist nur
noch der Upload — Paket, Texte und Bilder liegen fertig unter
`Desktop\PDF_SNAP_STORE_UPLOAD\CHROME_2.27.0\`.

**Dazu gehört:** die deutsche Store-Fassung eintragen. Die Erweiterung liefert
neun Sprachen aus (`_locales`), das Chrome-Listing bisher nur Englisch.

## 4. Android ist deklariert und nie auf einem Gerät geprüft

**Beleg:** `/measurements/android-capture-extensions/` sagt es selbst:
*„We did not install or test any of these on a device."* Das galt für die
sechzig fremden Erweiterungen — und gilt für die eigene genauso.

**Warum das unangenehm ist:** Der Store-Text nennt Android als Merkmal. Eine
Vollseitenaufnahme muss scrollen, auf nachgeladene Bilder warten, Abschnitte
zusammenfügen und die Datei an einen Dateiauswahldialog übergeben — jeder dieser
Schritte verhält sich auf Android anders. Deklaration ist nicht Funktion, und
das steht so auf der eigenen Messseite.

**Aufwand:** ein Gerät, eine halbe Stunde, ein Protokoll. Der billigste Punkt
auf dieser Liste, gemessen an dem, was er ausräumt.

## 5. Die Brücke vom Endpunkt zum Add-on ist dokumentiert, aber nicht gebaut

**Beobachtung, kein Messwert:** Wenn `extract_citation` eine Quelle mit
`complete: false` zurückgibt, nennt die Antwort seit Worker 1.13.0 einen
`nextStep` mit beiden Store-Adressen. Das ist ein Verweis — mehr nicht.

**Was fehlen könnte:** Die Erweiterung schreibt einen RIS-Satz neben das PDF.
Der Endpunkt erzeugt RIS-Sätze. Beide kennen einander nicht. Ob eine Verbindung
Nutzen hätte — etwa dass die Erweiterung beim Aufnehmen die Angaben des
Endpunkts einholt, wenn die Seite selbst nichts deklariert —, ist **ungemessen**
und gehört gemessen, bevor es gebaut wird.

**Warum es hier trotzdem steht:** Es ist der einzige Punkt, an dem das Projekt
etwas könnte, was andere Aufnahme-Erweiterungen nicht können. Die anderen vier
Punkte machen das Produkt besser; dieser würde es unterscheidbar machen.

---

## Was nicht auf dieser Liste steht, und warum

**Mehr Funktionen.** Dreizehn Einstellungen bei vier Nutzern sind nicht zu
wenige. Beide Bewertungen loben die einfache Handhabung — das ist das einzige
Signal, das es gibt, und es spricht gegen weitere Schalter.

**Nutzerzahlen steigern.** Nicht durch Automatik: Beide Stores beenden dafür
das Entwicklerkonto, und die Firefox-Route ist für den Zähler ohnehin
unsichtbar. Was zählt, sind Installationen von Menschen, die das Werkzeug
brauchen — und dafür ist Punkt 3 (der Store liefert eine zehn Fassungen alte
Version aus) der größte Hebel auf dieser Liste.

**Eine eigene OCR.** Die Textebene aus dem DOM ist besser als jede Erkennung,
weil sie den Originaltext übernimmt. Wo sie fehlt — bei eingebetteten Bildern —,
löst OCR das Problem nicht, sondern verschiebt es.

## Reihenfolge

1. **#18** — weil dreizehn Seiten eine möglicherweise falsche Zahl tragen
2. **Punkt 3** — weil der Upload fertig danebenliegt und zehn Fassungen kostet
3. **#19** — weil die Dateigröße jeden Nutzer trifft, der mehr als drei Belege sammelt
4. **Punkt 4** — weil er billig ist und eine Zusage im Store betrifft
5. **Punkt 5** — erst messen, ob es Nutzen hat, dann entscheiden

Die ersten drei sind belegt und umrissen. Die letzten beiden sind offen genug,
dass jemand anderes sie besser zuschneiden könnte.
