# Fehlerhistorie der Zitationserfassung

Jeder Eintrag ist ein Fehler, der im Betrieb aufgetreten ist — nicht in einem
Testfall, der ihn erwartet hat. Notiert ist, woran er auffiel, denn das ist
uebertragbarer als der Fehler selbst.

Alle am 2. August 2026, in der Reihenfolge des Auftretens.

| # | Fehler | Aufgefallen an | Behebung |
|---|---|---|---|
| 1 | Fusszeile unsichtbar, sobald eine Textebene dabei war | grauer Balken ohne Text, obwohl `pdftotext` ihn fand | `Tr`/`Tz` gehoeren zum Grafikzustand und ueberleben `ET`; Textebene in `q`/`Q` geklammert |
| 2 | DOI aus der Adresse geraten: `10.3389/fpsyg.2021.618509/full` | loest nicht auf | Muster ueberschreitet keinen Schraegstrich mehr |
| 3 | Zitation aus einer Fehlerseite gebaut | ScienceDirect-Wartewand wurde zur Quellenangabe | Sperrseiten werden erkannt und statt einer Referenz gemeldet |
| 4 | Ausgelieferte Methode veraltet | `get_method` beschrieb Capture als "text layer: none" | Methode auf den Stand gebracht |
| 5 | Sperrseite "Making sure you're not a bot!" durchgerutscht | Live-Test gegen SSOAR | Muster suchte nur am Titelanfang |
| 6 | ...und die Verbreiterung erzeugte Fehlalarm | "Error Analysis in Second Language Acquisition" | zwei Gruppen: eindeutige Formulierungen ueberall, generische nur am Anfang |
| 7 | Reparatur wirkte nicht | Sperrseite antwortet mit HTTP 200 und lag im Edge-Cache | Zwischenspeicherung fuer dieses Werkzeug abgeschaltet |
| 8 | Titel `"\| bioRxiv"` wurde zum Titel `"bioRxiv"` | Durchsicht unvollstaendiger Datensaetze | Mindestlaenge beim Abschneiden; nur-Seitenname ist keine Quelle |
| 9 | Sechs leere Verfasser als vollstaendig gewertet | Zufallsstichprobe: `content=";;;;;"` | leere Namen aussortiert, BibTeX erzeugte `{ and  and }` |
| 10 | Datensatznummer als Werktitel | Zufallsstichprobe: Titel `"1643858"` | rein numerische Titel gelten nicht als Titel |
| 11 | Kennung statt Titel | `"Archive BacDiveID:10.13145/..."` | nicht korrigiert, sondern benannt — eine Korrektur waere geraten |
| 12 | Sichtbare Zitation zu Interpunktion zerfallen | russische Quelle: `", . . & , . . (2007)."` | PDF-Standardschrift kann nur WinAnsi; bleibt unter 60 % erhalten, wird auf die beigelegte RIS-Datei verwiesen |

## Fehler in der eigenen Messung

Diese Haelfte ist die unangenehmere, weil sie Ergebnisse verfaelscht haette.

| # | Messfehler | Woran erkannt | Folge |
|---|---|---|---|
| A | 26-mal `HTTP 403` in je 0,13 s | zu schnell fuer einen echten Abruf | `urllib` sendet `Python-urllib/3.x`, Cloudflares Bot-Schutz weist das ab |
| B | Drei gueltige Cloudflare-Token als widerrufen gemeldet | Dashboard zeigte sie aktiv | `/user/tokens/verify` gilt nicht fuer Konto-Token |
| C | Citoid ab dem zwoelften Aufruf `HTTP 429` | alle spaeteren Werte identisch fehlerhaft | haette den Vergleich zugunsten der eigenen Seite verfaelscht; Wartezeit eingebaut |
| D | `ER  - ` als "leeres RIS-Feld" beanstandet | vier von fuenf Stichproben gleich | ER ist der Endmarker und traegt per Definition keinen Wert |
| E | **Auswahlverzerrung**: erste Messreihe ergab Gleichstand mit Citoid | Zufallsstichprobe ergab 4 zu 7 | die 26er-Liste enthielt Quellen, die zuvor als funktionierend ausgewaehlt worden waren |
| F | PMC als "liefert keine Metadaten" gemessen | `curl` fand 13 Felder | Playwright lief in eine Bot-Wand |

Befund E ist der schwerwiegendste: Er hat einen bereits geschriebenen Beitrag
entwertet, dessen Kernaussage "gleich viele vollstaendige Zitationen" lautete.
Eine Messreihe aus selbst gewaehlten Quellen misst die Auswahl, nicht das
Werkzeug.

## Was daraus als Verfahren geworden ist

- **Zufallsstichproben statt Listen.** OpenAlex zieht das Werk, nicht der Autor
  der Messung.
- **Eine unabhaengige Referenz.** Verglichen wird gegen OpenAlex, nicht die
  Werkzeuge untereinander — sonst misst man, wer wem aehnelt.
- **`provinglab-bench` entscheidet ueber Beitraege**, nicht der Eindruck: kein
  Beitrag ohne Vorsprung bei vollstaendigen Zitationen, null eigene Zitationen
  aus Sperrseiten, mindestens Faktor 1,5 schneller.
