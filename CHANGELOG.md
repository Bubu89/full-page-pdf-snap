## 2026-08-03 — Schalter im Hauptfenster, Einzelaufnahme, und ein Fehler, den nur der Integrationstest fand

### Der Fehler zuerst

Alle bisherigen Pruefungen liefen gegen **Ausschnitte** von `content.js` —
einzelne Funktionen, aus der Datei geschnitten und im Seitenkontext aufgerufen.
Ein Test, der die Datei als Ganzes laedt und ueber ihre echte
Nachrichten-Schnittstelle anspricht, zeigte sofort: **`collectSource` lieferte
nichts.**

Ursache: `nurSeitenname` und `nurNummer` wurden in der Warnungspruefung benutzt,
aber erst siebzig Zeilen weiter unten deklariert. JavaScript wirft dort einen
`ReferenceError`, und das `try`/`catch` des Listeners verschluckte ihn. Die
gesamte Quellenerfassung war in der Erweiterung tot, waehrend sie im
MCP-Endpunkt einwandfrei lief — derselbe Code, andere Umgebung.

`tests/integration.py` prueft das jetzt an drei Seitenarten: Skript laeuft ohne
Laufzeitfehler, `hideSticky` antwortet, `collectText` liefert Woerter und
Bloecke, `collectSource` liefert eine Quelle, und die Seitenhoehe wird nicht
kaputtgemacht.

### Schalter im Hauptfenster

Bisher liess sich das Ausblenden nur ueber die Einstellungsseite oder das
Kontextmenue umlegen. Es steht jetzt im Popup, weil es als einziges die
**Aufnahme sichtbar veraendert** — alle uebrigen Einstellungen werden einmal
gesetzt und vergessen. Der Wert liegt im selben Speicher wie zuvor: wer ihn im
Popup umlegt, sieht ihn in den Einstellungen und im Kontextmenue umgelegt.

Nach dem Umschalten erscheint eine kurze Rueckmeldung, welche Wirkung die
naechste Aufnahme hat. Schlaegt das Speichern fehl, springt der Schalter
zurueck — eine Anzeige, die etwas anderes behauptet als der Speicher, waere
schlimmer als gar keine.

### Sichtbaren Bereich aufnehmen

Zweiter Knopf, ein einziger Abschnitt. Bewusst **kein zweiter Ausgabeweg**:
dieselbe Kette, derselbe PDF-Schreiber, dieselbe Textebene, dieselbe
Nachweiszeile mit Zitation, Adresse, Zeitpunkt und Pruefsumme. Ein eigener Pfad
waere ein zweiter Ort fuer dieselben Fehler.

### Ausgeliefert

Beide Fassungen auf demselben Stand, Pakete gebaut:
`full-page-pdf-snap-firefox-2.18.0.zip` und
`full-page-pdf-snap-chrome-2.18.0.zip`.

## 2026-08-03 — Zustimmungsdialoge: nicht nur haesslich, sondern der Grund fuer abgebrochene Aufnahmen

Bisher wurden nur `position: fixed` und `sticky` ausgeblendet. Gemessen an acht
Seiten reichte das nicht:

- **Bei vier von acht war der Bildlauf gesperrt** (`overflow: hidden` am
  Dokument). Das ist kein Schoenheitsfehler: Bei spiegel.de meldete die Seite
  dadurch **900 Pixel Hoehe statt 43.101** — die Aufnahme waere auf einen
  einzigen Bildschirm zusammengeschrumpft, ohne dass es jemandem auffaellt.
- **Zwei von sechs Overlays trugen `position: absolute`**, eines davon ueber dem
  gesamten Sichtfenster. Die alte Regel sah sie nicht.

Erkannt wird jetzt nach Bauart: was sich als Dialog ausweist (`dialog[open]`,
`role=dialog`, `aria-modal`), oder was hoch gestapelt, positioniert und
grossflaechig ist. **Keine Namensliste** — die muesste gepflegt werden und waere
an dem Tag falsch, an dem eine Seite ihre Klassen umbenennt.

### Der Fehler, den diese Aenderung zuerst verursacht hat

Die erste Fassung blendete bei zeit.de den Hauptcontainer aus: hoch gestapelt,
absolut positioniert, grossflaechig — alle Merkmale erfuellt. Die Seitenhoehe
fiel von 48.437 auf 900 Pixel. Aus Stoerungsbereinigung wurde Datenverlust.

Zwei Bremsen dagegen: Was mehr als ein Viertel des Seitentextes traegt, ist
Inhalt. Und was hoeher ist als anderthalb Fensterhoehen, wird gescrollt und ist
damit ebenfalls Inhalt — Zustimmungsdialoge passen auf einen Bildschirm.

### Warum ausgeblendet und nicht weggeklickt

[Autoconsent](https://github.com/duckduckgo/autoconsent) und
[Consent-O-Matic](https://github.com/Consent-O-Matic/) loesen dasselbe Problem
anders: Sie **klicken** die Dialoge weg. Fuer taegliches Surfen ist das richtig.

Fuer ein Aufnahmewerkzeug ist es das nicht. Ein Klick auf "Ablehnen" oder
"Akzeptieren" ist eine Willenserklaerung im Namen des Nutzers, setzt Cookies und
veraendert den Zustand der Seite dauerhaft. Diese Erweiterung blendet nur fuer
die Dauer der Aufnahme aus und stellt danach jeden Eingriff zurueck — sie
entscheidet nichts, sie fotografiert.

### Gemessene Wirkung

| Seite | Bildlauf | Hoehe vorher | nachher |
|---|---|---|---|
| spiegel.de | gesperrt | 900 | **43.101** |
| zeit.de | gesperrt | 48.437 | 48.437 (unveraendert — richtig) |
| kurier.at | gesperrt | 36.452 | 36.452, Overlay-Text entfernt |
| orf.at | gesperrt | 6.369 | 6.369, Overlay-Text entfernt |

## 2026-08-02 — Was die Konkurrenz besser macht, und was davon uebertragbar war

Geprueft, wie Zotero es loest — der Unterbau von Citoid. Zotero arbeitet eine
Prioritaetskette ab: seitenspezifische Uebersetzer (100), unAPI (300), COinS
(310), DOI (320), eingebettete Angaben (400). **Wir implementieren nur die
unterste Stufe.**

Naheliegend waere gewesen, COinS und unAPI nachzuruesten. Gemessen an zehn
Seiten, darunter vier Bibliothekskataloge: **unAPI kommt nirgends vor, COinS nur
bei Wikipedia** — und dort beschreiben die Spans die *zitierten* Quellen des
Artikels, nicht den Artikel selbst. Fuer "diese Seite zitieren" also wertlos.
Ein negatives Ergebnis, das Arbeit an einer toten Ebene erspart hat.

Zotero holt seine Abdeckung aus 600 seitenspezifischen Uebersetzern. Das ist
kein Verfahren, das sich abkuerzen laesst — es ist gepflegte Handarbeit.

### Was tatsaechlich uebertragbar war

**Koerperschaft als Urheber.** Bei Behoerden-, Statistik- und Rechtsquellen gibt
es keine Person, und das ist kein Mangel: nach APA ist dort die herausgebende
Einrichtung der Urheber. Statistik Austria, Statistisches Bundesamt, EUR-Lex —
die Angabe steht in der Seite, wurde aber verworfen.

**Zwei echte Fehler, gefunden beim Vergleich der unvollstaendigen Datensaetze:**

- bioRxiv liefert `| bioRxiv` als Seitentitel. Das Abschneiden des
  Seitennamen-Anhaengsels machte daraus erst einen leeren, dann einen Titel, der
  nur noch aus dem Namen des Servers bestand. Jetzt: Mindestlaenge beim
  Abschneiden, und wenn nur der Seitenname uebrig bleibt, ist es keine
  Quellenangabe, sondern eine Warnung.
- Damit sinkt die Zahl gelieferter Datensaetze von 13 auf 12 — **eine
  Verbesserung, obwohl die Zahl faellt.** Ein Datensatz, dessen Titel der Name
  des Servers ist, war nie einer.

### Was offen bleibt

Die Koerperschaftsregel hat die Zahl vollstaendiger Zitationen nicht erhoeht,
weil bei diesen Quellen weiterhin das Jahr fehlt. Fuer eine laufend
aktualisierte Statistikseite ist "o. J." mit Abrufdatum aber die *richtige*
Zitierweise — hier misst die eigene Kennzahl am Zweck vorbei, nicht die Daten.
Das ist als naechstes zu klaeren, nicht durch Nachbessern der Extraktion.

Stand nach den Aenderungen, gegen Citoid: 8 zu 7 vollstaendige Zitationen,
0 zu 2 Zitationen aus Sperrseiten, Faktor 3,6 schneller.

## 2026-08-02 — Gemessen gegen Citoid, und eine Schwelle fuer Beitraege

Die Zitationserfassung des MCP-Endpunkts wurde an 26 Quellen aus zwoelf
Faechern gemessen — und zum ersten Mal **gegen ein fremdes Werkzeug**. Ohne
Vergleich ist "13 von 26" keine Aussage ueber Qualitaet, sondern eine Zahl ohne
Massstab.

Massstab ist **Citoid** (Wikimedia), das dasselbe Problem loest, oeffentlich
erreichbar ist und auf den Zotero-Translatoren aufsetzt.

| | eigener Endpunkt | Citoid |
|---|---|---|
| vollstaendige Zitationen | **8** | 8 |
| Datensatz ueberhaupt | 13 | **20** |
| **Zitation aus einer Sperrseite** | **0** | 2 |
| Median Sekunden | **0,34** | 1,63 |
| langsamster Aufruf | **10,0** | 29,2 |

Gleich viele vollstaendige Zitationen, in einem Drittel der Zeit. Citoid liefert
haeufiger *etwas* — aber zwei dieser Datensaetze sind Verweise auf eine
Bot-Wand: fuer EconStor und SSOAR gab Citoid *"Making sure you're not a bot!"*
als Titel des Werkes aus. Formatiert, vollstaendig aussehend, wertlos.

Ehrlich in die andere Richtung: Citoid erreicht drei Verlage, die uns aussperren
(MDPI, PeerJ, OECD). Wir erreichen zwei, die es verfehlt (Zenodo, Wikipedia).

### `provinglab-bench` — der Ablauf entscheidet, ob ein Beitrag entsteht

Neues Werkzeug, woechentlich ueber `backup-catchup` (drei Slots plus
Reboot-Nachlauf, weil der Rechner nicht durchlaeuft). Es misst beide Dienste an
derselben Liste und prueft drei Bedingungen:

1. nicht schlechter als der Vergleich bei vollstaendigen Zitationen,
2. **keine** eigene Zitation aus einer Sperrseite,
3. mindestens Faktor 1,5 schneller.

Halten nicht alle drei, entsteht kein Beitrag. Tempo allein genuegt
ausdruecklich nicht — das waere die falsche Botschaft fuer eine Seite, die
Messungen veroeffentlicht.

### Zwei Messfehler, die der Lauf selbst aufgedeckt hat

Der erste Durchgang meldete 26-mal `HTTP 403` in je 0,13 s. Zu schnell fuer
einen echten Abruf — und daran erkennbar: `urllib` sendet
`Python-urllib/3.x`, und Cloudflares Bot-Schutz weist genau diese Signatur ab.
`requests`, `node-fetch`, Go und Browser kommen durch. Wer den Endpunkt aus
einem Skript anspricht, sollte das wissen.

Der zweite: Citoid begrenzt anonyme Zugriffe. Ab dem zwoelften Aufruf kam
`HTTP 429`. Diese Antworten als "Citoid kann es nicht" zu zaehlen haette den
Vergleich zugunsten der eigenen Seite verfaelscht. Der Lauf wartet jetzt
zwischen den Aufrufen und wiederholt nach einem 429.

# Changelog

<!-- change-stream:auto-block:2026-08-02:START -->
### 2026-08-02 — Auto-Aggregat (change-stream)

_Quelle: change-stream, 91 Events, generiert 2026-08-03T07:02_

**Aktivitaet:** 21 Datei(en), 91 Tool-Calls (76 Edit, 14 Write, 1 Bash), 2 Session(s).

**Beruehrte Dateien:**
- `/home/holo/repos/full-page-pdf-snap-public/pdf-writer.js` (27x)
- `/home/holo/repos/full-page-pdf-snap-public/content.js` (20x)
- `/home/holo/repos/full-page-pdf-snap-public/background.js` (9x)
- `/home/holo/repos/full-page-pdf-snap-public/make-store-screenshots.py` (6x)
- `/home/holo/repos/full-page-pdf-snap-public/worker/mcp.js` (6x)
- `/home/holo/repos/full-page-pdf-snap-public/messung-quellen-archiv.py` (3x)
- `/home/holo/repos/full-page-pdf-snap-public/CHANGELOG.md` (3x)
- `/home/holo/repos/full-page-pdf-snap-public/STORE_LISTING_EN.md` (2x)
- `/home/holo/repos/full-page-pdf-snap-public/docs/agent-tools.js` (2x)
- `/home/holo/repos/full-page-pdf-snap-public/build-feed.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/docs/robots.txt` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/build-agent-discovery.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/build-android-post.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/rechtscheck.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/WACHSTUMSPLAN.md` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/build-de-index.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/build-mcp-post.py` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/options.html` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/PRIVACY.md` (1x)
- `/home/holo/repos/full-page-pdf-snap-public/README.md` (1x)

**Bemerkenswerte Commands:**
- `cd /home/holo/repos/full-page-pdf-snap-public && timeout 200 python3 rechtscheck.py 2>&1 | tail -5 && git add -A && git `

<!-- change-stream:auto-block:2026-08-02:END -->

<!-- Keine absoluten Pfade des Entwicklungsrechners in dieses Repo.
     Der Aggregator des Arbeitsplatzes traegt sie automatisch ein; sie
     verraten Benutzernamen und Verzeichnisstruktur und nuetzen keinem
     Leser. Vor dem Commit auf Heim- und Benutzerverzeichnisse pruefen. -->


## 2026-08-02 — MCP-Server bekommt ein Werkzeug: `extract_citation`

Bisher konnte der Endpunkt unter `/mcp` Auskunft geben, aber nichts tun: drei
Werkzeuge, alle nur lesend auf die eigenen Messdaten. Ein fremder Agent mit der
Aufgabe „diese Quelle zitierfaehig sichern" fand dort nichts.

`extract_citation(url)` liest die Zitationsangaben, die eine beliebige Seite
ueber sich selbst erklaert, und liefert einen strukturierten Datensatz samt
fertigem **RIS** und **BibTeX**. Erkannt werden Zeitschriftenaufsatz,
Buchkapitel, Buch, Konferenzbeitrag, Hochschulschrift, Preprint, Bericht,
Datensatz, Video und Internetquelle.

An elf Quellen geprueft: **acht von acht erreichbaren korrekt eingeordnet**.
Drei Verlage (MDPI, ScienceDirect, Wiley) sperren serverseitige Leser mit
HTTP 403 aus — das wird als 403 gemeldet, nicht als leeres Ergebnis. Genau
dort hilft die Erweiterung, die im Browser des Nutzers laeuft: die beiden Wege
ergaenzen sich, und keiner ersetzt den anderen.

Grenzen stehen in der Antwort selbst: serverseitig gelesen, ohne JavaScript;
was eine Seite nachtraegt, ist unsichtbar. Ziel-Adressen werden auf oeffentliche
Hosts eingeschraenkt, damit der Endpunkt kein Sprungbrett auf interne Dienste
wird, und der Leser nennt sich im User-Agent, damit ihn aussperren kann, wer
das moechte.

### Typerkennung: ISBN schlaegt Zeitschriftentitel

Repositorien fuellen fuer einen Sammelbandbeitrag oft beide Felder. Bisher
gewann der Zeitschriftentitel, und ein Handwoerterbuch-Artikel wurde als
Zeitschriftenaufsatz zitiert. Jetzt entscheidet das eindeutigere Merkmal: eine
ISBN mit Seitenangabe ist ein Kapitel, eine ISSN ein Periodikum. Belegt an
SSOAR.

Weiter erkannt: Dissertationen ueber `citation_dissertation_institution`,
Tagungsbaende ueber `citation_conference_title`, Videos ueber schema.org
`VideoObject` — dort ist der Kanal der Urheber und das Hochladedatum das Jahr,
weil `citation_*`-Felder fehlen. Beitraege in Sammelbaenden erscheinen als
„In <Werk> (S. x–y)" und im RIS unter `T2` statt `JO`, weil
Literaturprogramme `JO` nur bei Periodika auswerten.

## 2026-08-02 — Fuer wissenschaftliches Arbeiten: Quellenangaben und Druckumbruch

Zwei Erweiterungen, beide zuerst gemessen und dann gebaut.

### Seitenumbruch trifft keine Zeilen mehr

Der mehrseitige Modus schnitt bisher blind alle `pageHeightPx` Pixel. An vier
Verlagsseiten (Springer, PLOS ONE, MDPI, Wikipedia) gemessen: **30 von 46
Schnitten liefen mitten durch eine Textzeile.** Wird der Schnitt stattdessen in
die naechste Luecke gezogen, sind es **2 von 47** — die beiden Ausnahmen sind
Bloecke, die hoeher sind als das Toleranzfenster von 12 Prozent; dort bleibt nur
der harte Schnitt. Der Preis ist ein leerer Rand von **1,1 bis 2,5 Prozent** je
Seite.

Unteilbar sind nicht nur Textzeilen: Bilder, Tabellen, Codebloecke und
eingebettete Rahmen zaehlen mit. Ein Schnitt durch eine Abbildung ist derselbe
Fehler wie einer durch einen Satz.

Neu ist ausserdem das Format **A4**: die Seitenhoehe wird aus der aufgenommenen
Breite abgeleitet (180 x 267 mm Satzspiegel), sodass eine Seite das Blatt
ausfuellt, ohne beim Drucken skaliert zu werden.

### Die Textebene ueberlebt den Seitenumbruch

Bisher fiel sie weg, sobald mehr als eine Seite entstand — gedruckte Fassungen
waren also nicht durchsuchbar. Jetzt merkt sich jede Seite ihren Beginn im
Gesamtbild (`yPx`), und jedes Wort landet auf der Seite, auf der es abgebildet
ist. Gemessen am Testdokument: **100 Prozent der Woerter wiederauffindbar**
ueber zwei Seiten hinweg.

### Quellenangaben im PDF

Gelesen wird ausschliesslich die Seite, die ohnehin im Browser steht. An sechs
Wissenschaftsseiten geprueft: **fuenf liefern die vollstaendige Zitation** ueber
`citation_*`-Angaben im Seitenkopf (arXiv, Springer, PMC, PLOS, MDPI); Wikipedia
ueber schema.org. Ein Abruf bei einem Zitationsdienst haette **nichts ergaenzt** —
und haette diesem verraten, welche Arbeit gerade gelesen wird.

Erfasst werden Titel, Verfasser, Jahr, Zeitschrift, Band, Heft, Seiten, DOI,
ISSN/ISBN, Verlag, Sprache, Lizenz, kanonische Adresse, Fassungsadresse,
Aenderungsdatum sowie **Abrufzeitpunkt mit Uhrzeit und Zeitzone** — Datum allein
genuegt nicht, weil Seiten sich im Lauf eines Tages aendern.

Das landet an drei Stellen:

- **sichtbare Zeile** ueber der Nachweiszeile, im Format APA 7
- **Dokumentangaben** (Titel, Verfasser, Zitation, DOI)
- **angehaengter RIS-Satz** (`quelle.ris`) fuer Citavi, Zotero und EndNote —
  herauszuholen mit `pdfdetach -saveall` oder ueber die Anlagen-Ansicht

Geraten wird nichts. Liegt ein Feld nicht vor, fehlt es. Namen werden nur
umgestellt, wenn die Form erkennbar ist — bei Namenszusaetzen wie *van der* oder
*de la* bleibt der Name unveraendert, weil ein falsch zerlegter Name schlimmer
ist als ein nicht gekuerzter.

Zwei Falschangaben wurden dabei behoben, bevor sie ausgeliefert wurden:
`document.lastModified` liefert bei dynamischen Seiten den Zeitpunkt des
Seitenaufbaus und haette *"zuletzt geaendert: heute"* behauptet; und ein
Verlagsdatum wie `Jun 23, 2023` ist kein gueltiges RIS-Datum und laesst
Importprogramme stolpern.

### Originaldatei des Verlags — abschaltbar, Vorgabe aus

Wo die Seite eine Volltextadresse nennt, kann die Datei danebengelegt werden.
Das ist der **einzige** Vorgang, der eine Verbindung aufbaut, deshalb ist er
standardmaessig aus und in PRIVACY.md benannt. Geholt wird nur die Adresse, die
die Seite selbst angibt — derselbe Abruf, den ein Klick auf "PDF" ausloest, mit
demselben Zugang. Was hinter einer Schranke liegt, bleibt dort.

## 2026-08-02 — Fusszeile war unsichtbar, sobald eine Textebene dabei war

Beim ersten echten Gebrauch beider neuer Funktionen zugleich — Herkunftsfuss
und unsichtbare Textebene — fehlte im Ergebnis der Fusstext. Der graue Balken
war da, `pdftotext` fand den Text, sichtbar war er nicht.

**Ursache.** Textrendermodus (`Tr`) und horizontale Laufweite (`Tz`) gehoeren
nach ISO 32000 zum Grafikzustand, nicht zum Textobjekt. Sie ueberleben `ET`.
Die Textebene setzt je Wort `3 Tr` (unsichtbar); die danach geschriebene
Fusszeile erbte diesen Zustand vom letzten Wort — samt dessen Laufweite.

**Behebung.** Die Textebene wird in `q`/`Q` geklammert. Das setzt den
Grafikzustand zurueck und wirkt unabhaengig davon, was danach in den
Inhaltsstrom geschrieben wird — anders als ein blosses `0 Tr` in der
Fusszeile, das denselben Fehler beim naechsten Zusatz wiederholen wuerde.

Der Fehler konnte vorher nicht auffallen: einzeln funktioniert jede der beiden
Funktionen. Nur ihre Kombination war ungeprueft.

## 2026-08-02 — Sicherheitspruefung: Repository, GitHub, Cloudflare

**Repository.** Die vollstaendige Historie (104 Commits) auf Tokens, private
Schluessel und API-Geheimnisse durchsucht — **nichts gefunden**.

Zwei andere Funde:
- **29 absolute Pfade des Entwicklungsrechners** in CHANGELOG.md, eingetragen
  vom Aggregator des Arbeitsplatzes. In einem oeffentlichen Repository geben
  sie Kontonamen und Verzeichnisstruktur preis und nuetzen keinem Leser. Jetzt
  repo-relativ, mit Warnhinweis im Kopf der Datei.
- **`__pycache__/*.pyc` war versioniert.** Ein Kompilat traegt den absoluten
  Pfad seiner Quelldatei im Klartext. Aus der Versionierung entfernt und in
  `.gitignore` aufgenommen.

Die private Kontaktadresse in PRIVACY.md und about/ bleibt: Sie ist die
bewusst gewaehlte Adresse der pseudonymen Publikation, kein Versehen.

**GitHub.** Secret Scanning und Push-Schutz waren bereits aktiv — letzterer
verhindert, dass ein Geheimnis ueberhaupt hochgeladen wird. Keine Actions,
keine Repository-Secrets, also keine Angriffsflaeche dort. Ergaenzt:
Schwachstellen-Warnungen und automatische Sicherheitsfixes (Dependabot).
Wiki und Projects waren aktiv, aber ungenutzt — abgeschaltet, weil eine offene
Flaeche ohne Zweck nur Angriffsflaeche ist.

**Cloudflare.** HSTS, TLS 1.2 als Minimum, HTTPS-Zwang, Browser-Integritaet
und die vier Sicherheits-Header standen bereits. Zwei Luecken geschlossen:

- **Content-Security-Policy** ergaenzt. Gemessen: Die Seite laedt von keinem
  fremden Host — kein Skript, kein Stil, keine Schrift, kein Bild. Die
  Richtlinie ist entsprechend eng, mit `frame-ancestors 'none'` (ersetzt
  x-frame-options), `object-src 'none'`, `base-uri 'self'`,
  `form-action 'none'`. `'unsafe-inline'` bleibt noetig, weil CSP auch
  `application/ld+json` erfasst und die strukturierten Daten sonst wegfielen.
  Nach dem Setzen geprueft: null Konsolenfehler, JSON-LD unveraendert im DOM.
- **SSL von „full" auf „full (strict)".** Vorher prueft Cloudflare das
  Zertifikat des Ursprungs nicht — ein Angreifer zwischen Cloudflare und
  GitHub Pages haette ein beliebiges Zertifikat vorzeigen koennen. GitHub hat
  ein gueltiges Zertifikat fuer beide Hostnamen (Zustand „approved"), deshalb
  traegt strict. Mit Rueckrollung getestet: alle Pfade 200.

Der Signaturschluessel des OAuth-Endpunkts steht weiterhin offen im Code. Das
ist dokumentiert und beabsichtigt: Er verhindert nur, dass ein erfundenes
Token als gueltig gilt, und schuetzt keinen Zugang.

## 2026-08-02 — auth.md gruen, 13 von 15

`authMd` besteht: „Auth.md support detected (anonymous)".

**Wie es dazu kam, und was daran lehrreich ist.** Ich habe vier Runden lang
geraten, welche Struktur der `agent_auth`-Block braucht — jeweils aus der Prosa
der Fehlermeldung abgeleitet. Jede Runde brachte eine neue Meldung und keinen
Fortschritt. Erst der Blick in die Spezifikation selbst
(github.com/workos/auth.md) zeigte, dass die Felder anders heissen als die
Beschreibung nahelegt: **`identity_types_supported`**, nicht
`supported_identity_types`; **`credential_types_supported`** je Identitaetstyp,
nicht eine flache Liste daneben. Danach nannte der Pruefer die letzte Luecke
praezise — `claim_uri` — und die war in einem Zug gefuellt.

Vier Runden Raten gegen einen Blick in die Quelle. Die Quelle war schneller.

**Zwei neue Endpunkte, beide echt:**

`/oauth/claim` antwortet `claimable: false, reason: no_accounts` — eine anonyme
Identitaet an ein Konto zu binden setzt Konten voraus, und es gibt keine.
`/oauth/revoke` bestaetigt jeden Widerruf und sagt dazu, dass er nichts
aendert, weil ein Token ohnehin nichts freischaltet. Beide sagen die Wahrheit,
statt zu schweigen oder etwas vorzugeben.

**Verbleibend:** `dnsAid` haengt am Registrar (`cloudflare_dns: false`,
`ds_records: []`), nicht an der Zone. `a2aAgentCard` verlangt einen Agenten,
der Aufgaben bearbeitet — eine Publikation tut das nicht.

## 2026-08-02 — OAuth-Discovery gruen, 12 von 15

`oauthDiscovery` besteht: `/.well-known/oauth-authorization-server` nach
RFC 8414 mit issuer, token_endpoint, jwks_uri und grant_types_supported —
ausgeliefert vom Worker, nicht als statische Datei behauptet. Der Fluss wurde
end-to-end durchgespielt: registrieren, Token holen, MCP damit aufrufen.

**`authMd` bleibt offen.** Der Pruefer nannte in drei aufeinanderfolgenden
Laeufen jeweils eine andere Anforderung an den `agent_auth`-Block:
zuerst eine `skill`-URL, die auf `/auth.md` zeigt (gesetzt), dann
Identitaetstypen als eigene Objekte statt flacher Listen (gesetzt), dann
`credential_types_supported` statt `credential_types` (gesetzt) — und meldet
weiterhin „agent_auth metadata was not found". Die Anforderung ist aus den
Rueckmeldungen nicht vollstaendig rekonstruierbar; weiteres Raten waere
Aufwand ohne erkennbaren Nutzen fuer irgendeinen realen Client. Der Block
enthaelt, was die verlinkte Spezifikation nennt, und `/auth.md` beschreibt den
Weg vollstaendig und in Prosa.

**`dnsAid` haengt nicht an der Zone.** Die HTTPS-Records stehen und loesen
oeffentlich auf; DNSSEC ist in der Zone aktiviert, Algorithmus 13, Key-Tag
2371. Beim Registrar ist der DS-Eintrag aber leer, und der Grund steht dort
ebenfalls: `cloudflare_dns: false`. Der Registrar fuehrt die Domain nicht als
Cloudflare-DNS-verwaltet, obwohl die Nameserver gesetzt sind — daran haengt
die automatische DS-Uebernahme. Die Domain ist einen Tag alt und traegt noch
`addperiod`. Ueber die Zone-API ist das nicht aufloesbar; ein Registrar-Token
mit Schreibrechten waere die Ebene, auf der Kontaktdaten, Auto-Renew und
Transfer haengen — dafuer zu weitreichend.

## 2026-08-02 — OAuth: echt gebaut statt behauptet

Der Pruefer verlangte bei `auth.md` ein **nicht leeres**
`authorization_servers` — obwohl RFC 9728 die leere Liste ausdruecklich
erlaubt. Statt einen Eintrag zu erfinden, gibt es den Server jetzt wirklich.

**Was der Worker seit Version 1.2.0 kann:**

| Pfad | Verhalten |
|---|---|
| `/.well-known/oauth-authorization-server` | Metadaten inkl. `agent_auth`-Block |
| `POST /oauth/register` | Dynamische Registrierung nach RFC 7591, liefert eine stabile `client_id` |
| `POST /oauth/token` | Client Credentials, echtes signiertes Token, eine Stunde gueltig |
| `/oauth/authorize` | weist ab und erklaert warum — es gibt nichts zu autorisieren |
| `/oauth/jwks` | leer, die Signatur ist symmetrisch |

Vollstaendig durchgespielt: registrieren, Token holen, MCP damit aufrufen.

**Warum das kein Etikettenschwindel ist.** Manche MCP-Clients verbinden sich
ohne Autorisierungsserver gar nicht erst — fuer die ist das ein echter
Zugangsgewinn. Was hier ausdruecklich *nicht* passiert: so zu tun, als wuerde
damit etwas geschuetzt. Der MCP-Endpunkt antwortet mit und ohne Token
identisch (gemessen: beide Male dieselben drei Werkzeuge), jede Registrierung
wird angenommen, `agent_auth.authentication_required` steht auf `false`, und
`auth.md` sagt im ersten Absatz: *it does not have to*.

Der Signaturschluessel steht offen im Code. Er verhindert nur, dass ein
erfundenes Token als gueltig durchgeht — er schuetzt keinen Zugang, und ihn
geheim zu halten waere Theater.

`authorization_servers` in der Protected Resource Metadata ist damit
wahrheitsgemaess befuellt, ergaenzt um `authentication_required: false`, damit
niemand mehr hineinliest als dasteht.

## 2026-08-02 — Ein Token statt drei, alle Zone-Einstellungen gesetzt

**Token aufgeraeumt.** `provinglab-zone-full` selbst ueber die API erstellt und
gegen die Zone gemessen: DNS Write, Zone Settings Write, Cache Settings Write,
Zone Transform Rules Write, Cache Purge, Zone Read, Workers Routes Write —
alles auf provinglab.dev beschraenkt, Ablauf 2027-08-02. `rapid-night-d114`
geloescht, nachdem der Ersatz nachweislich jeden Endpunkt erreicht; er hatte
kein Ablaufdatum und stand am 01./02.08. im Chatverlauf.

**Damit gesetzt, was bisher an fehlenden Rechten scheiterte:**
Always Use HTTPS (http:// antwortet jetzt mit 301), HSTS ueber 180 Tage
inklusive Subdomains, min. TLS 1.2 statt 1.0, Early Hints, 0-RTT und
Always Online. Cache geleert, alles gegen die laufende Seite nachgemessen.

**Registrar-Zugriff bewusst nicht ausgeweitet.** DNSSEC haengt auf `pending`,
weil beim Registrar kein DS-Eintrag hinterlegt ist — mit einem Nur-Lese-Token
geprueft: `ds_records: []`. Setzen liesse sich das nur mit
„Registrar Domains Admin", also der Ebene, auf der Kontaktdaten, Auto-Renew
und Transfer haengen. Fuer einen einzelnen Pruefpunkt steht das in keinem
Verhaeltnis; der Lesetoken wurde nach der Diagnose sofort wieder geloescht.
Ein Klick unter DNS → Settings erledigt es.

Stand: 11 von 15, Level 5 (Agent-Native).

## 2026-08-02 — Sicherheitspruefung der Agent-Ebenen: zwei Funde, beide behoben

Nach dem Aufbau geprueft statt angenommen. Zwei echte Maengel:

**1. Verfuegbarkeitsrisiko durch die Worker-Route (schwerwiegend).**
Die Route `provinglab.dev/*` stand auf `request_limit_fail_open: false`. Ist
das Worker-Kontingent erschoepft — im freien Tarif 100.000 Anfragen am Tag —
antwortet damit die **ganze Website** mit einem Fehler, statt auf GitHub Pages
zurueckzufallen. Ein einzelner Aufrufer haette die Seite fuer den Rest des
Tages abschalten koennen. Das ist das Gegenteil dessen, wofuer Cache-Regel und
`serve_stale` gebaut wurden. Jetzt `true`: bei Ueberlastung liefert der
Ursprung weiter, nur die Zusatzfunktionen fallen aus.

**2. Pfadumgehung im MCP-Werkzeug `get_measurement_data`.**
Die Beschraenkung pruefte, ob der zusammengesetzte Pfad mit `/data/` beginnt.
`"../.well-known/oauth-protected-resource"` erfuellt das — der Server
normalisiert anschliessend, und die fremde Datei wurde ausgeliefert. Gemessen,
nicht vermutet. Kein Datenabfluss moeglich, weil auf dieser Domain ohnehin
alles oeffentlich ist und fremde Hosts korrekt abgewiesen wurden (nur der
Pfadanteil einer URL wird uebernommen, kein SSRF). Trotzdem war die
Beschraenkung wirkungslos. Jetzt wird der Dateiname geprueft statt der Pfad
zusammengesetzt: `^[A-Za-z0-9._-]+\.json$`.

**Ergaenzt: CORS.** Ohne `access-control-allow-origin` kommt kein
browserbasierter MCP-Client an den Endpunkt. Der liefert ausschliesslich
oeffentliche Daten und kennt keine Sitzung — ein weit gefasstes CORS gibt hier
nichts preis und oeffnet erst den Zugang. `OPTIONS` beantwortet die
Vorabanfrage mit 204.

Worker jetzt Version 1.1.0. Alle drei Punkte gegen den laufenden Endpunkt
nachgeprueft.

## 2026-08-02 — Durchsuchbares PDF: Textebene aus dem Dokument statt aus OCR

Die Aufnahme war bisher reines Pixelbild. Wer den Text brauchte, musste ihn
erkennen lassen — und die eigene Messung zeigte genau dort die einzige
Schwaeche: Druck gewann bei der Textrueckgewinnung, weil er eine echte
Textebene mitbringt.

Jetzt bringt die Aufnahme eine eigene mit, und zwar nicht aus Erkennung,
sondern aus dem Dokument selbst. Jedes Wort wird per Range einzeln vermessen
und unsichtbar (Textrendermodus 3) an seiner Stelle im PDF gesetzt.

**Gemessen an einer echten Seite** (1280 x 4729 px, 1068 Woerter):

| Verfahren | Wort-Recall | Fuenf-Wort-Folgen |
|---|---|---|
| OCR, Tesseract | 92,6 % | 73,9 % |
| Textebene zeilenweise (erster Versuch) | 97,8 % | 80,8 % |
| **Textebene wortgenau** | **100,0 %** | **91,8 %** |

Kein einziges Wort fehlt. Die Extraktion dauert 14 ms.

**Zwei eigene Messfehler auf dem Weg**, beide korrigiert:
Zuerst gegen Latin-1 statt CP1252 geprueft — daher schienen nur 85,4 % der
Zeichen darstellbar; `WinAnsiEncoding` kennt Gedankenstrich, typografische
Anfuehrungszeichen und Auslassungspunkte, tatsaechlich sind es 100 %. Und die
Laufweite wurde gegen eine Pauschale von 0,5 em gestaucht statt gegen die
echten Helvetica-Breiten (Mittel 0,489 em, Spanne 0,222 bis 0,944) — daher
sass der Text zwar auf der richtigen Zeile, aber nicht auf dem Wort.

**Warum das rechtlich sauber bleiben muss.** Ein PDF, dessen unsichtbarer Text
etwas anderes sagt als das sichtbare Bild, ist irrefuehrend — jemand kopiert
Text, der so nie auf dem Schirm stand. Deshalb wird der Text im selben
Seitenzustand gesammelt wie die Bilder: nach dem Ausblenden fixierter Elemente,
vor der Wiederherstellung. Und die Metadaten halten fest, woher er stammt:
`text-layer=extracted from the page's own DOM, not OCR`. Das ist keine
Formalie — OCR verliest sich, eine DOM-Uebernahme kann umgekehrt Text
mitnehmen, den eine Ueberdeckung im Bild verbirgt. Wer die Datei spaeter
pruefen muss, braucht diesen Unterschied.

Nur im Format „eine durchgehende Seite": im mehrseitigen Modus wird die
Aufnahme geschnitten, die Wortkoordinaten beziehen sich aber auf das ganze
Dokument. Eine falsch zugeordnete Textebene waere schlechter als gar keine.

Standard **an** — sie macht das PDF durchsuchbar, ohne das Bild zu veraendern.
Beide Zweige portiert, neun Sprachdateien auf 100 Eintraege.

## 2026-08-02 — Herkunftsangaben im PDF (Erweiterung)

Bisher enthielt das erzeugte PDF ausser den Bilddaten nichts: keinen Titel,
keine Quelle, keinen Zeitpunkt. Wer eine Aufnahme drei Monate spaeter im
Ordner fand, konnte nicht mehr sagen, woher sie stammte.

**Immer geschrieben — PDF-Metadaten:** `/Title` (Seitentitel), `/Subject`
(Quell-URL), `/CreationDate` und `/ModDate` mit Zeitzonenversatz, `/Producer`
mit Version, `/Keywords` mit Adresse, Zeitpunkt und SHA-256 der Bilddaten in
maschinenlesbarer Form. Unsichtbar, aendert die Aufnahme nicht, kostet nichts.
Nicht-ASCII wird als UTF-16BE mit BOM kodiert — geprueft mit Umlauten und
japanischer Schrift im Titel.

**Optional — sichtbare Herkunftszeile** unter der Aufnahme: Adresse,
Aufnahmezeitpunkt mit Zeitzone, SHA-256. Standard **aus**, weil sie das Bild
veraendert; die Seite waechst dann um 30 pt. Ohne die Option bleibt das PDF
bitgleich zu vorher.

**Zur Formulierung.** Die Zeile traegt den Hinweis: *„Self-made screen capture.
Not a qualified electronic document (eIDAS). Time from device clock. Checksum
covers this file's image data only, not the authenticity of the page."* Das ist
bewusst zurueckhaltend und deckt genau die drei Grenzen ab, die sonst
missverstanden werden — es gibt keine Signatur, die Zeit stammt von der
Geraeteuhr, und die Pruefsumme belegt Unveraendertheit der Datei ab Erstellung,
nicht wie die Seite aussah. Die Einstellung sagt dasselbe ausfuehrlicher, in
allen neun Sprachen.

Der Hinweis im PDF steht auf Englisch, auch bei uebersetzter Oberflaeche:
Standard-PDF-Schriften koennen nur WinAnsi darstellen, und eine Fussnote, die
auf Japanisch oder Russisch zu Kaestchen zerfaellt, dokumentiert nichts.

Beide Zweige (Firefox, Chrome MV3) ueber `port.py` synchronisiert, neun
Sprachdateien auf 98 Eintraege, Schrift und Textobjekte im PDF-Writer ergaenzt.
Drei Betriebsarten gegen echte PDFs geprueft und die Fussnote visuell
kontrolliert.

**Nicht erledigt:** Versionsnummer und Veroeffentlichung. Das gehoert in den
Release-Lauf, nicht in diesen Commit.

## 2026-08-02 (Abschluss II) — Android-Messung veroeffentlicht, eigene Behauptung korrigiert

Neuer Beitrag `/measurements/android-capture-extensions/` samt Datensatz.
248 Erweiterungen ueber acht AMO-Suchbegriffe geprueft, **60 deklarieren
Android-Unterstuetzung** — zusammen rund 998.000 taegliche Nutzer, SingleFile
allein 85.724. Der Median liegt bei 221.

**Damit ist die eigene Store-Behauptung widerlegt.** Das AMO-Listing sagt
„One of the few capture add-ons that run on Firefox for Android". Rund ein
Viertel der Werkzeuge, nach denen Leute suchen, deklariert es. Der Beitrag
sagt das ausdruecklich und nennt die eigene Erweiterung mit ihren drei
taeglichen Nutzern am unteren Ende derselben Liste.

Der Text trennt sauber zwischen Deklaration und Funktion: Ein Manifest-Eintrag
erlaubt die Installation, er belegt keine funktionierende Aufnahme. Nichts
davon wurde auf einem Geraet getestet, und das steht so im Text — wer diese
Arbeit macht, kann das Ergebnis ueber den Issue-Tracker beisteuern.

Warum das hier steht und nicht nur im Listing: Die Frage „welche Erweiterung
speichert auf dem Handy eine Seite" wird gesucht, und es gibt dazu keinen
oeffentlichen Datensatz. Chrome fuer Android kann ueberhaupt keine
Erweiterungen installieren — deshalb taucht Chrome in der Messung nicht auf.

Verknuepft in sitemap.xml, llms.txt, feed.xml und der Messungs-Uebersicht.
IndexNow fuer alle 18 URLs angestossen, HTTP 200. Visuell geprueft.

## 2026-08-02 (Abschluss) — Worker live, Level 5 erreicht

Der Worker `provinglab-mcp` laeuft auf der Route `provinglab.dev/*` und
erledigt beides:

- **MCP ueber `POST /mcp`**, JSON-RPC 2.0, zustandslos. Gegen echte Aufrufe
  geprueft: `initialize`, `tools/list` und alle drei Werkzeuge liefern
  Messdaten, Datensaetze und Methoden. Unbekannte Werkzeuge antworten sauber
  als `isError`.
- **Markdown-Aushandlung.** Eine Messungsseite faellt von 24.418 B HTML auf
  9.306 B Markdown, `x-markdown-tokens: 1320`. Browser bekommen unveraendert
  HTML. Cloudflares eigenes „Markdown for Agents" verlangt dafuer Pro — dieser
  Weg kostet nichts.

**Zwei Fehler auf dem Weg, beide gemessen statt vermutet:**

1. Die Datenquelle wurde aus der Request-URL abgeleitet. Auf einer
   workers.dev-Adresse zeigte sie auf den Worker selbst, jede Datenabfrage
   endete im 404. Jetzt fest auf die Publikation gesetzt.
2. Die Subrequests trugen keinen `user-agent`. Cloudflares Integritaetspruefung
   wies sie ab — dieselbe Regel, die auf dieser Zone `Python-urllib` mit
   Fehler 1010 blockiert. Auffaellig war, dass ein Aufruf funktionierte und
   zwei nicht; der Unterschied lag nicht am Pfad, sondern am Header.

**Stand: 11 von 15, Level 5 (Agent-Native)** — heute frueh: 4 von 15, Level 2.

Nach dem Verschieben der Server Card meldete der Pruefer sie zunaechst weiter
als fehlend. Ursache war ein **gecachter 404** (`cf-cache-status: HIT`,
`age: 154`) aus der Zeit vor dem Deployment. Negative Antworten liegen genauso
im Edge-Cache wie positive.

**Offen und ehrlich nicht erreichbar:** `oauthDiscovery`, `authMd` und
`a2aAgentCard` verlangen einen Autorisierungsserver, einen Registrierungsablauf
und einen A2A-Agenten. `dnsAid` wartet auf DNSSEC (`pending`, Registrar ist
Cloudflare, laeuft ohne Zutun) — damit waeren 12 von 15 das Maximum ohne
Falschangaben.

## 2026-08-02 (Nacht) — Antwort-Header gesetzt, Grenze des Erreichbaren erreicht

**Transform Rules** wurden am Token ergaenzt, damit ist gesetzt:

- `Link:` mit fuenf Beziehungen — `api-catalog`, `describedby` (Skills-Index),
  `service-doc` (llms.txt), `alternate` (Feed), `help` (auth.md). Agenten finden
  die Discovery-Dateien jetzt ueber den HTTP-Kopf, ohne die Seite zu parsen.
- `x-content-type-options: nosniff`, `referrer-policy`, `permissions-policy`,
  `cross-origin-opener-policy` — vier Header, die der Seite komplett fehlten und
  die in keinem Agent-Bericht vorkommen. GitHub Pages kann sie nicht liefern.
- `content-type: application/linkset+json` fuer `/.well-known/api-catalog`;
  ohne Dateiendung lieferte GitHub Pages `octet-stream`.

Stand: **9 von 15** Pruefpunkten (heute frueh: 4). Punktwert 29 → deutlich hoeher.

**Messfehler bei der Kontrolle:** `curl -sI` (HEAD) zeigte die neuen Header nicht
— es fehlten dort auch `cf-ray` und `cf-cache-status`. Mit GET waren alle da.
Antwort-Header nie per HEAD verifizieren.

**Wo Schluss ist — und warum.** Drei der verbleibenden sechs Punkte sind ohne
Falschangabe nicht erreichbar:

- `oauthDiscovery` verlangt Issuer, Authorization- und Token-Endpunkt.
- `oauthProtectedResource` ist zwar gruen, aber der `authMd`-Check verlangt
  zusaetzlich ein **nicht leeres** `authorization_servers`-Array. Gemessener
  Prueferbefund: „Missing authorization_servers array" — obwohl das Feld als
  leere Liste vorhanden ist, was RFC 9728 ausdruecklich erlaubt.
- `authMd` verlangt einen „complete standalone registration flow".

Alle drei setzen eine geschuetzte API voraus. Sie hier zu erfinden hiesse,
Agenten auf Endpunkte zu schicken, die nicht existieren. Der Score bliebe
gruen, die Seite wuerde luegen.

**Ohne Falschangabe noch erreichbar:** `dnsAid` (sobald DNSSEC von `pending` auf
aktiv wechselt — laeuft automatisch, Registrar ist Cloudflare) und
`mcpServerCard` (sobald ein echter MCP-Server existiert). Damit waeren 11 von 15
das ehrliche Maximum. `markdownNegotiation` braucht einen Pro-Plan.

## 2026-08-02 (spaeter Abend) — Protected Resource Metadata, AMO-Sichtbarkeit gemessen

**Agent-Discovery:** `/.well-known/oauth-protected-resource` nach RFC 9728
ergaenzt. Die Spezifikation verlangt nur `resource`; `authorization_servers`
ist optional, und eine leere Liste sagt korrekt aus, dass kein
Autorisierungsserver Tokens ausstellt. Damit steht nichts Falsches in der
Datei. `/.well-known/oauth-authorization-server` bleibt bewusst aus — sie
muesste Issuer, Authorization- und Token-Endpunkt nennen, die es nicht gibt.
Score dadurch 8/15 (Ausgangslage am Morgen: 4/15, Punktwert 29 → 57).

**Zwei Messungen zur Auffindbarkeit im Firefox-Store:**

1. Rang in der AMO-Suche, gemessen bis Platz 100: `full page pdf snap` 1,
   `pdf snap` 2, `full page pdf` 6, `save webpage as pdf` 11,
   `save page as pdf` 34, `webpage to pdf` 37 — und
   **`full page screenshot` gar nicht unter den ersten 100 von 361 Treffern.**
   Ursache: Das Wort *screenshot* kommt weder im Titel noch in der
   Zusammenfassung vor, nur in der Langbeschreibung. AMO gewichtet Titel und
   Zusammenfassung am staerksten.

2. 121 Erweiterungen aus sechs Capture-/PDF-Suchbegriffen geprueft:
   **33 davon deklarieren Android-Kompatibilitaet**, darunter PDF Mage (16.526
   Nutzer), Print to PDF (13.328), Save Screenshot (10.802), Save PDF (5.573),
   PageSaver (2.200) und FullPage Capture (1.556). Die AMO-Zusammenfassung
   behauptet derzeit *„One of the few capture add-ons that run on Firefox for
   Android"*. Deklaration ist nicht Funktion — aber ohne eigene Messung auf dem
   Geraet ist die Aussage in dieser Form nicht belegt und passt nicht zu einer
   Seite, die jede Behauptung mit einer Methode hinterlegt.

**Ebenfalls gemessen:** Die AMO-Homepage-Angabe zeigt auf
`bubu89.github.io/full-page-pdf-snap/` statt auf provinglab.dev. Der
AMO-JWT im Vault gehoert zu einem anderen Konto (Projekt SentinelX) und
bekommt beim Schreiben HTTP 403 — die Korrektur muss im Developer Hub
erfolgen.

## 2026-08-02 (Abend) — Agent-Discovery umgesetzt

Sechs der elf Punkte aus dem isitagentready-Bericht sind live, mit echtem
Inhalt statt Platzhaltern.

**`/.well-known/agent-skills/index.json`** — die drei Methoden, die diese Seite
ohnehin veroeffentlicht, jetzt als abrufbare Skills: Berechtigungen einer
Erweiterung lesen, OCR-Recall mit Kontrolllauf messen, Druck gegen Bildschirm-
aufnahme abwaegen. Die sha256-Summen werden aus den Dateien berechnet, nicht
gepflegt — der Index kann nicht abdriften. Live gegengeprueft: alle drei stimmen.

**`/.well-known/api-catalog`** (RFC 9727) — Linkset auf die drei Messdatensaetze,
jeder mit `describedby` auf die Seite, die die Methode dokumentiert.

**`/auth.md`** — die Auskunft, dass nichts geschuetzt ist, plus eine Tabelle
aller ohne Zugangsdaten erreichbaren Ressourcen.

**`agent-tools.js`** — WebMCP mit drei Werkzeugen: Messungen auflisten,
Datensatz als JSON holen, Methode holen. Faellt still zurueck, wo
`navigator.modelContext` fehlt, also derzeit ueberall ausser im Chrome-Trial.

**DNS-AID** — `_index._agents.provinglab.dev` und `_a2a._agents.provinglab.dev`
als HTTPS-Records mit `alpn`, `port` und `mandatory=alpn,port`, wie der Pruefer
sie erwartet. Cloudflare lehnt den `endpoint`-SvcParam ab (nur registrierte
Schluessel erlaubt); der Draft verlangt ihn nicht. Beide loesen oeffentlich auf.

**DNSSEC** aktiviert, Algorithmus 13, Key-Tag 2371. Status noch `pending` —
Registrar ist Cloudflare selbst, die DS-Uebernahme laeuft automatisch.

**`.nojekyll` war die Voraussetzung fuer all das.** GitHub Pages baut mit Jekyll,
und Jekyll ueberspringt Verzeichnisse mit fuehrendem Punkt und wandelt .md in
HTML um — `/.well-known/` waere nie ausgeliefert und `/auth.md` als HTML
gelandet. Die Seite nutzt weder Layouts noch Front Matter noch Liquid, also
geht nichts verloren. Gemessen danach: `/auth.md` kommt als `text/markdown`.

**Bekannte Einschraenkung:** `/.well-known/api-catalog` wird als
`application/octet-stream` ausgeliefert statt `application/linkset+json`.
GitHub Pages leitet den Typ aus der Dateiendung ab, und der von RFC 9727
vorgeschriebene Pfad hat keine. Nur ueber eine Response-Header-Transform-Regel
zu beheben — dasselbe fehlende Recht wie bei den Link-Headern.

**Weiterhin offen:** Link-Header (Transform Rules noetig), Markdown-Aushandlung
(Pro-Plan noetig). **Bewusst nicht angelegt:** OAuth- und OIDC-Metadaten sowie
MCP Server Card — es gibt keine geschuetzten Endpunkte und keinen MCP-Server.

## 2026-08-02 (spaeter) — Agent-Readiness-Bericht bewertet, ein Punkt umgesetzt

Ein Prueflauf von isitagentready.com meldete elf offene Punkte. Bewertet, nicht
abgehakt — die Liste ist generisch, und der groessere Teil verlangt Metadaten
fuer Infrastruktur, die es hier nicht gibt.

**Umgesetzt:** Content Signals in robots.txt.
`search=yes, ai-input=yes, ai-train=no`. Indexierung und Abruf zur Antwortzeit
sind erwuenscht — beide schicken Leser hierher, und eine zitierte Messung mit
Link ist der Zweck dieser Seite. Training ist abgelehnt: es verbraucht die
Arbeit, ohne je auf sie zurueckzuverweisen.

**Nicht umgesetzt, weil es Fassade waere:** API-Katalog (RFC 9727) ohne API,
OAuth- und OIDC-Discovery ohne geschuetzte Endpunkte, auth.md ohne Registrierung,
MCP Server Card ohne MCP-Server, Agent-Skills-Index ohne Skills, DNS-AID ohne
Agent-Endpunkt, WebMCP ohne Aktionen auf einer reinen Leseseite. Ein Agent, der
`/.well-known/api-catalog` findet und darin nichts Nutzbares vorfindet, hat Zeit
verloren — leere Metadaten sind schlechter als keine.

**Blockiert durch Rechte:** Link-Header (RFC 8288) brauchen Response-Header-
Transform-Regeln. Gemessen: `http_response_headers_transform` antwortet mit
HTTP 403, der Token hat nur Cache Rules. Dieselbe Regel wuerde auch die heute
komplett fehlenden `x-content-type-options`, `referrer-policy` und
`permissions-policy` setzen, die GitHub Pages nicht liefern kann.

**Blockiert durch Plan:** Markdown for Agents setzt Pro oder Business voraus,
die Zone laeuft auf Free. Das vorhandene llms.txt deckt den Zweck weitgehend ab
— es enthaelt bereits eine Zusammenfassung jedes Beitrags.

**Nebenwirkung der Cache-Regel bemerkt:** robots.txt zeigte nach dem Deployment
zehn Minuten lang die alte Fassung (`cf-cache-status: HIT`, `age: 588`). Das ist
die Origin-TTL von 600 s und damit erwartbar. Ein gezielter Purge ist mit dem
Token nicht moeglich (`Cache Purge` fehlt); bei dringenden Aenderungen hilft ein
Abruf mit Zufallsparameter zur Kontrolle, oder schlicht abwarten.

## 2026-08-02 (Nachmittag) — Feed, Edge-Cache, Suchmaschinen-Anstoss

**Atom-Feed.** Die Seite hatte keinen. Wer Feedly, NetNewsWire, Miniflux oder
Thunderbird benutzt, konnte ihr nicht folgen; Aggregatoren, die nur Feeds
annehmen, konnten sie nicht aufgreifen. `build-feed.py` liest die Beitraege
selbst — Titel aus `<title>`, Zusammenfassung aus der meta-description, Daten
aus dem JSON-LD, das ohnehin auf jeder Seite steht. Damit kann der Feed nicht
veralten, solange die Seiten stimmen. `<link rel="alternate">` in 16 Seiten
ergaenzt, sonst findet ihn kein Leser.

**Edge-Cache.** Cache-Regel ueber die Cloudflare-API gesetzt: HTML wird
gecacht (Edge-TTL nach Origin-Vorgabe, also 600 s), `serve_stale` liefert bei
Origin-Ausfall die letzte Kopie weiter. Vorher stand auf jeder HTML-Antwort
`cf-cache-status: DYNAMIC` — jeder Abruf ging bis GitHub Pages durch, ein
Ausfall dort schlug sofort auf Besucher durch. Nach der Regel: `HIT`.
Bewusst `respect_origin` statt fester Stunde, damit Aenderungen nicht
stundenlang unsichtbar bleiben.

**Brand-Logo** mit `width`/`height` versehen — das einzige Bild der Seite ohne
Groessenangabe und damit das einzige, das beim Laden das Layout verschieben
konnte.

**Nicht geaendert:** Die leeren `alt=""` am Logo bleiben. Das Logo steht im
selben Link direkt neben dem Text „Proving Lab" — ein gefuellter alt wuerde
Screenreadern den Namen doppelt vorlesen. Ein erster Pruefdurchlauf hatte das
faelschlich als Mangel gemeldet.

**IndexNow** fuer alle 14 URLs angestossen, HTTP 200. Erreicht Bing, Yandex,
Seznam und Naver; Google nimmt nicht daran teil.

**Offen:** `Zone Settings:Edit` fehlt dem Token weiterhin. Damit ungesetzt:
Always Use HTTPS, HSTS, Always Online, Early Hints, 0-RTT. `cf-provinglab-tune`
setzt sie, sobald das Recht da ist.

## 2026-08-02 — Erreichbarkeit provinglab.dev gemessen und nachgezogen

**Warum:** Nach der Absicherung der Mail-Ebene am 01.08. sollte geprueft werden,
wie gut die Domain tatsaechlich erreichbar ist — nicht nur ob sie antwortet.

**Gemessen:** apex und www liefern HTTP 200 bei ~0,26 s TTFB, HTTP/2 und HTTP/3,
Brotli aktiv, IPv6 vorhanden, HTTPS-RR mit ECH, zwei Nameserver, robots.txt und
sitemap.xml korrekt, alle 13 Sitemap-URLs erreichbar.

**Zwei echte Luecken gefunden:**

1. `/favicon.ico` und `/apple-touch-icon.png` antworteten mit 404. Beide Pfade
   werden von Browsern, Googles Favicon-Crawler und iOS per Konvention abgefragt,
   unabhaengig vom `<link rel="icon">` im HTML. In den Suchergebnissen blieb der
   Favicon-Platz dadurch leer. Erzeugt aus `icon-128.png`: ICO mit 16/32/48/64/128 px,
   apple-touch-icon auf Weiss geflacht, weil iOS Alpha als Schwarz rendert.
   Bewusst ohne HTML-Aenderung — die Konvention greift ueber den Pfad.

2. HTML liegt am Cloudflare-Edge als `cf-cache-status: DYNAMIC`, jeder Abruf geht
   bis GitHub Pages durch. Ein Origin-Ausfall schlaegt sofort auf Besucher durch.
   Die Cache-Regel dagegen braucht Rechte, die der API-Token nicht hat (HTTP 403).

**Weiter geaendert:** GitHub Pages `https_enforced` von False auf True.
Null-MX (`MX 0 "."`, RFC 7505) ergaenzt — vervollstaendigt SPF `-all` und DMARC
`reject`, damit Zustellversuche schon vor dem SMTP-Dialog scheitern.

**Einordnung .dev:** Die gesamte TLD steht in der HSTS-Preload-Liste. Browser
sprechen mit dieser Domain ohnehin nie unverschluesselt — der fehlende
HTTP->HTTPS-Redirect trifft nur Nicht-Browser-Clients und ist kein akuter Mangel.

**Offen:** Der Zone-Token hat nur `DNS:Edit`. Fuer Cache-Regel, Always Online,
Early Hints, 0-RTT und HSTS fehlen `Zone Settings:Edit` und `Cache Rules:Edit`.
Werkzeug dafuer liegt bereit: `~/.local/bin/cf-provinglab-tune` (idempotent,
`--dry-run` zeigt den Unterschied). Anleitung im Vault-Eintrag.

<!-- change-stream:auto-block:2026-08-01:START -->
### 2026-08-01 — Auto-Aggregat (change-stream)

_Quelle: change-stream, 102 Events, generiert 2026-08-02T10:08_

**Aktivitaet:** 23 Datei(en), 102 Tool-Calls (84 Edit, 17 Write, 1 Bash), 1 Session(s).

**Beruehrte Dateien:**
- `background.js` (25x)
- `docs/tools/full-page-pdf-snap/index.html` (14x)
- `result-visual-check.py` (9x)
- `docs/index.html` (7x)
- `result.js` (7x)
- `chrome-mv3/port.py` (5x)
- `README.md` (5x)
- `result.html` (5x)
- `sync-site.py` (4x)
- `docs/pdf-extension-permissions/index.html` (3x)
- `pack-firefox.py` (3x)
- `docs/about/index.html` (2x)
- `site-visual-check.py` (2x)
- `CHANGELOG.md` (1x)
- `docs/webpage-to-pdf-for-ocr/index.html` (1x)
- `docs/extension-permissions-risk/index.html` (1x)
- `docs/notes/building-with-ai-what-went-wrong/index.html` (1x)
- `ping-suchmaschinen.py` (1x)
- `docs/measurements/print-to-pdf-vs-screenshot/index.html` (1x)
- `docs/llms.txt` (1x)

**Bemerkenswerte Commands:**
- `cd <lokaler Pfad> && git add -A docs && git commit -q -F - <<'EOF'
Add /tools/, /data/ and a`

<!-- change-stream:auto-block:2026-08-01:END -->


<!-- change-stream:auto-block:2026-07-31:START -->
### 2026-07-31 — Auto-Aggregat (change-stream)

_Quelle: change-stream, 16 Events, generiert 2026-08-02T10:08_

**Aktivitaet:** 7 Datei(en), 16 Tool-Calls (13 Edit, 2 Write, 1 Bash), 2 Session(s).

**Beruehrte Dateien:**
- `CHANGELOG.md` (5x)
- `manifest.json` (3x)
- `chrome-mv3/port.py` (2x)
- `chrome-mv3/compat.js` (2x)
- `make-store-screenshots.py` (1x)
- `popup.html` (1x)
- `PRIVACY.md` (1x)

**Bemerkenswerte Commands:**
- `cd <lokaler Pfad> && git checkout -b mv3-firefox 2>&1 | tail -2 && git status --short | head`

<!-- change-stream:auto-block:2026-07-31:END -->
## 2.16.0 — Android: eine Meldung statt einer Reihe

Auf Android meldete sich die Erweiterung während der Aufnahme alle zwei
Segmente mit dem Fortschritt („Erfasse Seite … 61 %"), dazu eine beim Start.
Im Benachrichtigungsbereich stapelte sich das, obwohl niemand währenddessen
etwas tun kann. Jetzt kommt genau eine Meldung, und zwar wenn das PDF fertig
ist: „Fertig — n Seiten gespeichert. Tippen zum Anzeigen."

Das Antippen zeigt das PDF im Firefox-Viewer, wo die Download-Option direkt
erreichbar ist. Vorher lief es über `downloads.open()`, was das PDF an eine
fremde App übergab — und laut Kommentar im Code auf manchen Geräten still
hängen blieb. Der Tab-Weg existierte bereits als Notfall-Zweig für den Fall,
dass der Download scheitert; er ist jetzt der reguläre.

Ebenfalls weg: das automatische Öffnen direkt nach dem Speichern. Die Datei
liegt im Download-Ordner, angezeigt wird sie erst auf Wunsch.

Damit das Antippen auch Minuten später noch funktioniert, bleibt die Blob-URL
des PDF auf Android bestehen, statt nach 60 Sekunden freigegeben zu werden.
Freigegeben wird sie beim Start der nächsten Aufnahme — auch dann, wenn diese
fehlschlägt, damit ein Tippen auf eine Fehlermeldung nicht das alte PDF zeigt.
Ist der Hintergrundprozess zwischenzeitlich beendet worden und die URL damit
verloren, greift `downloads.open()` als Rückfallebene.

Am Desktop ändert sich nichts: Die Fortschrittsmeldungen liefen dort ohnehin
nie, das Rückmeldung gab das Popup.

## 2.15.0 — Manifest V3 (Firefox)

Der Firefox-Zweig lief noch auf Manifest V2, während der Chrome-Zweig seit
2.2.0 MV3 nutzt. MV2 ist die auslaufende Generation; eine Erweiterung, die
sich für das Recommended-Programm bewerben soll, sollte nicht darauf stehen.

Firefox setzt MV3 anders um als Chrome: Es bleibt bei einer Event Page statt
eines Service Workers. Damit entfällt der gesamte Umbau, den der Chrome-Port
gebraucht hat (OffscreenCanvas, createImageBitmap, data:-URLs) — das DOM ist
in der Hintergrundseite weiterhin da. Übrig bleiben vier Umbenennungen:

- `browser_action` → `action`, im Manifest und an 10 Stellen in `background.js`
- `browser.tabs.executeScript` → `browser.scripting.executeScript`, dazu die
  neue Berechtigung `scripting` (erzeugt keinen zusätzlichen Install-Prompt)
- Menü-Kontext `"browser_action"` → `"action"`
- `background.persistent` entfällt, MV3 kennt den Schlüssel nicht

Der Chrome-Zweig wird dadurch kleiner, nicht größer: Weil die Firefox-Quelle
jetzt dieselbe `scripting`-API mit derselben Signatur aufruft, entfallen der
zugehörige Patch in `port.py`, der `browserAction`-Alias und die Hilfsfunktion
`injectContentScript` in `compat.js`.

Geprüft: `web-ext lint` meldet 0 Fehler und 0 Notices. Die zwei verbleibenden
Warnungen betreffen `data_collection_permissions` (erst ab Firefox 140 bzw.
Android 142 unterstützt, `strict_min_version` steht auf 109/127) und bestanden
schon vor diesem Port — ältere Firefox-Versionen ignorieren den Schlüssel.
Offen: Funktionstest einer langen Seite in echtem Firefox, insbesondere ob die
Event Page über einen kompletten Capture hinweg am Leben bleibt.

<!-- change-stream:auto-block:2026-07-29:START -->
### 2026-07-29 — Auto-Aggregat (change-stream)

_Quelle: change-stream, 7 Events, generiert 2026-07-30T09:00_

**Aktivitaet:** 3 Datei(en), 7 Tool-Calls (6 Edit, 1 Bash), 1 Session(s).

**Beruehrte Dateien:**
- `CHANGELOG.md` (3x)
- `manifest.json` (2x)
- `pack-firefox.py` (1x)

**Bemerkenswerte Commands:**
- `cd ~/repos/full-page-pdf-snap-public && git add -A && git status --short && echo "=== diff stat"; git diff --cached --st`

<!-- change-stream:auto-block:2026-07-29:END -->
## 2.14.0 — 2026-07-31 (beide)

**Was:** Popup und Einstellungen richten sich jetzt nach dem Farbschema des
Browsers. Heller Browser → helle Oberfläche, dunkler Browser → dunkle.

**Warum:** Die beiden Oberflächen waren fest verdrahtet — und zwar
gegensätzlich. Das Popup war immer dunkel (`#1f2937`), die Einstellungsseite
immer hell. Ein Nutzer mit hellem Browser bekam also ein dunkles Popup, das im
Fenster wie ein Fremdkörper stand, und beim Klick auf „Settings" schlug ihm eine
weiße Seite entgegen. Aufgefallen ist es beim Vergleich der neuen
Store-Screenshots mit der tatsächlichen Oberfläche: Das Bild zeigte ein helles
Popup, das es so gar nicht gab — Store-Bilder müssen aber die echte Oberfläche
zeigen.

**Wie:**
- Farben laufen über CSS-Variablen. Hell ist der Ausgangswert, ein Block
  `@media (prefers-color-scheme: dark)` überschreibt ihn.
- `color-scheme: light dark` auf `:root` der Einstellungsseite. Ohne das bleiben
  die browsereigenen Bedienelemente — Auswahlfelder, Bildlaufleisten — hell und
  stechen im dunklen Fenster heraus.
- Eingabefelder und Auswahlfelder bekommen Hintergrund und Textfarbe
  ausdrücklich zugewiesen. Ohne das behalten sie ihre hellen Vorgabewerte, und
  weiße Felder auf dunklem Grund sind der übliche Ausrutscher an dieser Stelle.
- Auch die zehn Stellen mit fest im HTML stehenden Farben wurden umgestellt —
  eine davon war die Diagnose-Box, die sonst weiß geblieben wäre.

**Verifikation:** Automatisch in beiden Modi geprüft, gemessen an den
**tatsächlich gerenderten** Farben, nicht am CSS. Der Test prüft sich zuerst am
Referenzfall: Unterscheiden sich heller und dunkler Modus überhaupt? Täten sie
es nicht, wäre jede weitere Aussage wertlos. Danach Helligkeit von Grund und
Schrift sowie der Abstand zwischen beiden — auch für den grauen Nebentext, der
sonst gern im Grund verschwindet. Ergebnis hell `rgb(255,255,255)`, dunkel
`rgb(31,41,55)`, beide Seiten gleich. Zusätzlich beide Ansichten in Augenschein
genommen.

**Ergebnis:** Die Erweiterung fügt sich in beide Browser-Themen ein, Popup und
Einstellungen sind endlich einheitlich — und das helle Store-Bild zeigt jetzt
eine Oberfläche, die es wirklich gibt.

## 2.13.0 — 2026-07-31 (beide)

**Was:** Die Erweiterung fordert keinen Zugriff auf alle Websites mehr. Aus dem
Chrome-Manifest sind `host_permissions: <all_urls>` und das `tabs`-Recht
entfallen, aus dem Firefox-Manifest `<all_urls>` und `tabs`. Übrig bleibt
`activeTab` — Zugriff auf genau den einen Tab, und nur nachdem der Nutzer die
Erweiterung selbst ausgelöst hat.

**Warum:** Chrome stufte die Erweiterung im erweiterten Safe Browsing als „nicht
vertrauenswürdig" ein. Diese Einstufung hängt an Entwickler-Reputation und
Store-Alter und lässt sich durch keine Code-Änderung abschalten — sie verfällt
von selbst. Die Prüfung des Manifests förderte aber einen echten Missstand
zutage: Die Erweiterung verlangte dauerhaften Lese- und Schreibzugriff auf
**alle** Websites, obwohl sie ihn nie brauchte. Bei der Installation stand
deshalb „Alle Ihre Daten auf allen Websites lesen und ändern" — direkt neben
einer Vertrauenswarnung die wirksamste Abschreckung, die eine Store-Seite
bieten kann. Für eine Erweiterung, die mit „keine Datensammlung" wirbt, war das
zudem ein Widerspruch zwischen Anspruch und Manifest.

**Wie:**
- Alle drei Einstiegspunkte sind Nutzergesten: Klick auf das Symbol (mit oder
  ohne Popup), Tastenkürzel über die `commands`-API und das Kontextmenü. Jede
  dieser Gesten gewährt `activeTab` — dokumentiert für Chrome wie für Firefox.
  Genau die drei APIs, die Rechte brauchen, sind davon abgedeckt:
  `tabs.captureVisibleTab`, `scripting.executeScript` und der Zugriff auf
  `tab.url`/`tab.title` für Blacklist-Prüfung und Dateinamen.
- `tabs.sendMessage`, `tabs.create`, `tabs.getZoom`/`setZoom` und die
  `downloads`-API brauchen ohnehin keine Host-Rechte — das `tabs`-Recht war
  allein für `url`/`title` gesetzt, die `activeTab` mitliefert.
- Version über `bump-version.py --set` gesetzt, nachdem die AMO-Abfrage 2.12.1
  als bereits veröffentlicht meldete. Chrome-Zweig über `port.py` nachgezogen,
  alle 14 Ersetzungen mit erwarteter Trefferzahl.

**Verifikation:** In echtem Chrome 150 geladen (über CDP `Extensions.loadUnpacked`
— `--load-extension` wird von aktuellen Chrome-Versionen ignoriert). Der Service
Worker startet, die `importScripts`-Kette ist vollständig (`PageShotPdf`,
`injectContentScript`, `createCanvas` alle definiert), `isCapturable` urteilt
unverändert korrekt inklusive PDF-Direktmodus. Der Test prüft sich selbst am
Referenzfall: **ohne** Geste liefert `tabs.query` keine `url`, und
`captureVisibleTab` wie `executeScript` scheitern ausdrücklich am fehlenden
Recht. Damit ist belegt, dass die Reduktion real wirkt und der Test nicht ins
Leere misst.

**Offen:** Der End-to-End-Klick mit echter Geste ist automatisiert nicht
erreichbar — das Symbol einer Erweiterung lässt sich über CDP nicht anklicken.
Vor dem Hochladen einmal von Hand prüfen: entpackte Fassung laden, eine
beliebige Seite aufnehmen. Schlägt es fehl, wäre die Ursache eine fehlende
`url` in `runOnActiveTab`; der Tab ließe sich dann aus den Event-Parametern von
`onClicked`/`onCommand` durchreichen.

**Ergebnis:** Der Installationsdialog nennt keinen Zugriff auf alle Websites
mehr. Das Manifest deckt sich mit dem Versprechen der Store-Beschreibung, und
die Erweiterung fällt bei künftigen Store-Prüfungen nicht mehr in die Kategorie
mit weitreichenden Rechten.

### Store-Bilder neu — richtiges Kürzel, hell, lesbar

**Was:** Alle Store-Screenshots neu gebaut, erzeugt von
`make-store-screenshots.py`. Dazu ein viertes Bild zum Thema kostenlos und
datensparsam.

**Warum:** In den alten Bildern stand **`Alt+Shift+P`** — ein Kürzel, das es seit
dem Wechsel auf `Alt+Shift+Y` nicht mehr gibt. Es hat den Umstieg überlebt, weil
die Bilder von Hand gepflegt wurden und das Kürzel an mehreren Stellen steht.
Nutzer haben also monatelang eine Tastenkombination gesehen, die nichts tut.
Dazu kam: dunkelblauer Hintergrund, rund 40 % ungenutzte Fläche und ein
Einstellungsfenster, dessen Hilfetexte bei etwa 9 px im Store-Thumbnail
unlesbar waren.

**Wie:**
- Das Kürzel steht jetzt an **einer** Stelle im Skript (`KUERZEL`) und wird in
  alle Bilder eingesetzt. Der Fehler von Hand ist damit nicht wiederholbar.
- Heller Verlauf statt Dunkelblau, Überschriften 52 px, Fließtext 25 px,
  Bedienelemente im Mockup 19–27 px statt der Miniatur-Screenshots.
- Zeilenumbrüche in den Überschriften fest gesetzt — sonst rutschen einzelne
  Wörter je nach Schriftbreite in die nächste Zeile.
- Statt eines abfotografierten Einstellungsfensters eine nachgebaute Karte mit
  den drei Optionen, die den Unterschied ausmachen. Ein echter Screenshot ist
  bei dieser Bildgröße nicht lesbar.
- Viertes Bild: kostenlos, keine Werbung, kein Konto, kein Upload — samt dem
  Punkt, dass die Erweiterung ab 2.13.0 keinen Zugriff auf alle Websites mehr
  verlangt.

**Ergebnis:** `screenshots/01_capture_en.png` bis `04_free_en.png`, je
1280 × 800. Jedes Bild einzeln sichtgeprüft.

Die beiden Promo-Kacheln (440 × 280 und 1400 × 560) sind aus demselben Skript
nachgezogen — sie waren noch dunkelblau und hätten neben den hellen Screenshots
wie eine fremde Erweiterung gewirkt. Sie tragen bewusst nur Logo, Namen und
Kernnutzen: die kleine Kachel wird im Store so stark verkleinert, dass
Fließtext darin nicht mehr lesbar ist. Alle sechs Bilder sind 24-Bit-RGB ohne
Alphakanal, wie der Store es verlangt.

## 2.12.1 — 2026-07-29 (beide)

**Was:** Firefox zeigt jetzt dasselbe grün-gelbe Logo wie Chrome. Das blaue
SVG-Icon ist ersatzlos entfernt. Der Chrome-Port ist auf dieselbe Version
nachgezogen — dort war am Logo nichts zu korrigieren.

**Warum:** Die Erweiterung hatte zwei verschiedene Logos, ohne dass es jemandem
auffiel. In `icons/` lagen nebeneinander eine PNG-Familie (grün-gelber Verlauf,
weißes Dokument, „PDF"-Label) und ein SVG mit einem völlig anderen Motiv
(blauer Verlauf, Seite mit Textzeilen, grünes Schild, Schriftzug „PDF SNAP").
Das Firefox-Manifest verwies ausschließlich auf das SVG, der Chrome-Port
ersetzt es beim Portieren durch die PNGs, weil Chrome kein SVG rendert. Ergebnis:
im Chrome-Dashboard das grün-gelbe Logo, in Firefox ein blaues. Die PNGs lagen
zwar im Firefox-Paket, wurden aber von keiner Manifest-Zeile referenziert.

**Wie:**
- `icons` und `browser_action.default_icon` verweisen auf `icon-16/48/128.png`,
  identisch zum Chrome-Manifest.
- `icons/icon.svg` gelöscht und aus der Dateiliste von `pack-firefox.py`
  genommen. Zwei Bildquellen für ein Logo waren genau die Ursache — eine davon
  im Repo zu belassen, hätte den Fehler nur vertagt.
- Version über `bump-version.py --patch` gesetzt. Die AMO-Abfrage meldete 2.12.0
  als bereits veröffentlicht, daher 2.12.1 statt einer erneuten 2.12.0.
- Chrome-Seite über `port.py` + `pack.py` auf 2.12.1 nachgezogen. Am Icon war
  dort nichts zu tun: Ein Hash-Vergleich der PNGs im Repo, im eingereichten
  2.2.0-Paket und im gebauten Paket ergab durchweg Byte-Gleichheit mit den
  Firefox-PNGs, und kein Chrome-Paket enthielt je ein SVG. Der Port ersetzt
  das SVG seit jeher, weil Chrome es nicht rendern kann — genau deshalb war
  Chrome von dem Fehler nie betroffen.

**Ergebnis:** Toolbar-Symbol, Add-on-Verwaltung und AMO-Listing zeigen in beiden
Browsern dasselbe Logo. Das Paket enthält kein SVG mehr. Nebeneffekt: der
Schriftzug „PDF SNAP" war bei 16 px ohnehin nur ein grauer Fleck — die PNGs sind
für die kleinen Größen sauber gerastert.

<!-- change-stream:auto-block:2026-07-27:START -->
### 2026-07-27 — Auto-Aggregat (change-stream)

_Quelle: change-stream, 51 Events, generiert 2026-07-29T09:56_

**Aktivitaet:** 18 Datei(en), 51 Tool-Calls (37 Edit, 13 Write, 1 Bash), 1 Session(s).

**Beruehrte Dateien:**
- `background.js` (12x)
- `chrome-mv3/port.py` (10x)
- `content.js` (6x)
- `docs/index.html` (2x)
- `chrome-mv3/compat.js` (2x)
- `chrome-mv3/README.md` (2x)
- `chrome-mv3/pack.py` (2x)
- `options.html` (2x)
- `options.js` (2x)
- `CHANGELOG.md` (2x)
- `README.md` (1x)
- `SUPPORT.md` (1x)
- `docs/privacy.html` (1x)
- `chrome-mv3/tests/README.md` (1x)
- `pack-firefox.py` (1x)
- `bump-version.py` (1x)
- `release.py` (1x)
- `popup.js` (1x)

**Bemerkenswerte Commands:**
- `cd . && git add -A && git commit -q -m "Default shortcut moves to Alt+Shift+Y

`

<!-- change-stream:auto-block:2026-07-27:END -->


## 2.12.0 — 2026-07-27 (beide)

**Was:** Neues Standardkürzel `Alt+Shift+Y`, ein zweites `Ctrl+Shift+Y` für
Chrome, und jede Anzeige einer Tastenkombination stammt jetzt aus dem, was der
Browser tatsächlich vergeben hat.

**Warum:** Zwei Fehler in Folge, beide mit derselben Ursache. Der Hinweiskasten
auf der Optionsseite nannte `Ctrl+Shift+Y`, obwohl der Standard längst ein
anderer war — die Kombination stand fest im HTML, während das Feld darüber
schon den echten Wert las. Und `Alt+Shift+P` erwies sich in Firefox als
untauglich: `Alt+Shift` ist dort zugleich der Modifikator für
`accesskey`-Attribute, und der Profil-Dialog hat einen Knopf mit Accesskey `P`.
Die Aufnahme startete, nebenbei ging ein Profil-Fenster auf.

**Wie:**
- Standard ist `Alt+Shift+Y`. `Y` ist als Accesskey deutlich seltener als `P`,
  und der Buchstabe bleibt derselbe wie beim früheren `Ctrl+Shift+Y` — wer es
  gewohnt war, behält die Fingerbewegung.
- Chrome erhält zusätzlich `Ctrl+Shift+Y`. Diese Reihe ist dort im Gegensatz zu
  Firefox weitgehend frei; in Firefox sind A, B, C, D, E, G, H, I, J, K, M, N,
  O, P, Q, R, T, V, W, Y und Z belegt.
- Der Befehlsempfänger reagiert auf jeden Namen mit dem Präfix
  `capture-full-page`, beide Kürzel lösen dasselbe aus.
- Optionsseite, Hinweiskasten, Popup und Toolbar-Tooltip lesen alle
  `commands.getAll()`. Auch die Übersetzungen nennen keine Kombination mehr,
  der Tooltip setzt sie zur Laufzeit ein.
- Findet das Popup kein Kürzel, zeigt es `—` statt zu raten. Eine genannte,
  aber nicht vergebene Kombination ist schlimmer als keine Angabe.
- Eine deutsche Restzeile in der Android-Hilfe übersetzt.

**Ergebnis:** Die Optionsseite zeigt in Chrome `Alt+Shift+Y / Ctrl+Shift+Y`, in
Firefox `Alt+Shift+Y` — und zwar genau das, was auch auslöst. Beansprucht ein
Browser eine Kombination für sich, erscheint sie schlicht nicht, statt ein
Versprechen zu geben, das die Taste nicht hält.

## 2.3.0 — 2026-07-27 (Firefox)

**Was:** Die Verbesserungen an der Erfassung von App-Layouts, die beim
Chrome-Port entstanden sind, gelten ab dieser Version auch für Firefox.

**Warum:** Beide Fassungen teilen sich `content.js` und den Stitching-Block in
`background.js`. Ohne diese Version wäre die Firefox-Fassung schlechter als die
Chrome-Fassung, obwohl derselbe Code dahinter steht.

**Wie:**
- Zuschnitt auf den Scroll-Container: Menü und Seitenleiste erscheinen einmal
  oben statt in jedem Abschnitt, die frei werdende Fläche bekommt die aus dem
  Screenshot abgetastete Hintergrundfarbe.
- Scrollbare Nebenbereiche werden eigenständig durchgescrollt; die Seitenhöhe
  richtet sich nach dem längsten Bereich.
- Container-Auswahl nach Breite statt nach Scroll-Überhang.
- Neue Einstellung `appLayout` (Standard `context`) mit drei Möglichkeiten.
- `captureScale` von 1.5 auf 1.0 — das PDF zeigt die Seite wie am Bildschirm.

**Resultat:** Firefox- und Chrome-Paket sind funktional gleichwertig. Gegenprobe
an den fertigen Paketen: `content.js` ist bytegleich (SHA `ee2d09e79158`), der
Stitching-Block unterscheidet sich in genau einer Zeile — dem Chrome-Ersatz für
`document.createElement("canvas")`.


## 2.2.0-chrome — 2026-07-27 (Chrome-MV3-Zweig)

**Was:** Portierung nach Chrome Manifest V3 in `chrome-mv3/`, plus Verbesserungen
an der Erfassung von App-Layouts, die auch der Firefox-Fassung zugutekommen.

**Warum:** Chrome nimmt seit 2025 nur noch MV3 an. Beim Testen zeigten sich drei
Laufzeitfehler und zwei inhaltliche Schwaechen, die statische Pruefung nicht
findet.

**Wie:**
- `compat.js` kapselt die fehlenden Service-Worker-APIs: `OffscreenCanvas` statt
  `document.createElement`, `createImageBitmap` statt `new Image`, `data:`-URL
  statt Blob-URL. `port.py` erzeugt den Zweig reproduzierbar und bricht ab, wenn
  eine Ersetzung nicht mehr greift.
- Drossel auf 550 ms fuer `captureVisibleTab` — Chrome erlaubt nur zwei Aufrufe
  pro Sekunde, Firefox kennt die Grenze nicht.
- Container-Auswahl nach Breite statt nach Scroll-Ueberhang; eine schmale
  Navigationsspalte gewinnt sonst gegen den Lesebereich.
- Neue Einstellung `appLayout` (Standard `context`): Menue und Seitenleiste
  erscheinen einmal oben statt in jedem Abschnitt, die frei werdende Flaeche
  bekommt die aus dem Screenshot abgetastete Hintergrundfarbe.
- Scrollbare Nebenbereiche werden eigenstaendig durchgescrollt; die Seitenhoehe
  richtet sich nach dem laengsten Bereich, damit nichts abgeschnitten wird.
- `captureScale` von 1.5 auf 1.0: das PDF zeigt die Seite so, wie sie am
  Bildschirm steht. Hoehere Werte bleiben waehlbar, mit benanntem Zielkonflikt.

**Resultat:** Aufnahme auf Gmail laeuft durch, ohne wiederholtes Menue und ohne
sichtbare Farbkante. Geprueft mit acht Layout-Typen, neun Ende-Erkennungsfaellen
und pixelweiser Kontrolle des Zusammenfuegens — siehe `chrome-mv3/tests/`.


## 2.2.0 — 2026-07-21 (Keine Zwischen-Nachrichten mehr)

User-Feedback: Die Nachricht "Speichere PDF (X Seiten) ..." wirkte verwirrend, weil danach direkt die finale Nachricht kam (oder auch nicht).

- **Entfernt:** Zwischen-Notification "Speichere PDF ..." nach dem Scroll-Loop
- **Entfernt:** Zwischen-Notification "Speichere PDF (direkter Download) ..." im PDF-Direkt-Modus
- Der User sieht jetzt nach dem Scroll-Progress DIREKT das Endergebnis: entweder "Fertig — X Seiten gespeichert" oder "PDF im Browser bereit"
- Keine Verwirrung mehr durch Zwischenschritt-Feedback

## 2.1.9 — 2026-07-21 (Vereinfachte Android-UX: Tab-Oeffnung als Standard)

User-Feedback: SAF-Speichern-Dialog wird auf manchen Geraeten nicht getriggert. Wenn der direkte Save nicht klappt, will der Nutzer einfach dass die PDF im Browser landet — er speichert dann wenn er will.

- **Entfernt:** Attempt 3 mit `saveAs: true` (SAF-Dialog). Der Dialog oeffnet auf manchen Geraeten nicht.
- **Neuer Attempt 3 (frueher Attempt 4):** Tab-Oeffnung im Browser. PDF ist sofort sichtbar, User speichert selbst via Firefox-Download-Symbol.
- **Reduzierte Fallback-Nachricht:** kurz und klar. "PDF im Browser bereit — dort steht die Download-Option zur Verfuegung." Statt der 3-Punkte-Anleitung.
- **Fehler-Notifications minimiert:** keine technischen Details mehr in User-Nachrichten, keine Verwirrung durch Multi-Schritt-Anleitungen.
- Der PDF-Direkt-Modus (bei bereits geoeffneten PDFs, seit 2.1.8) folgt jetzt der gleichen Vereinfachung — statt System-Dialog wird der bestehende Tab genutzt.

## 2.1.8 — 2026-07-21 (PDF-Direkt-Download bei bereits geoeffneten PDFs)

User-Report: Beim Antippen der Extension auf einer bereits geoeffneten PDF (Firefox-PDF-Viewer) erschien die Fehlermeldung "Diese Seite erlaubt keine Erweiterungs-Skripte". Der Screenshot-Ansatz kann dort nicht funktionieren (Firefox-Policy blockiert Content-Scripts im PDF-Viewer).

**Loesung:**
- **Neuer Modus "pdf-direct":** Wenn die Extension eine PDF-URL erkennt (Endung `.pdf`), wird die Datei direkt via `downloads.download(url)` in den PDF-Snap-Ordner kopiert — kein Screenshot, kein Content-Script, keine Screenshot-Pipeline noetig
- Nutzt die gleiche 3-Stufen-Save-Strategie (subfolder / root / SAF-Dialog) wie der normale Screenshot-Modus
- Dateiname wird aus der URL abgeleitet (letzter Pfad-Teil ohne `.pdf`) — fallback auf Tab-Titel
- Notification: "Speichere PDF (direkter Download) ..." -> "PDF gespeichert: ..."

Damit funktioniert die Extension jetzt auch auf `https://.../datei.pdf` — nicht nur auf HTML-Seiten.

## 2.1.7 — 2026-07-21 (Attempt 3: SAF-Dialog + bessere Fallback-Anleitung)

User-Report Samsung: Attempt 3 (Tab-Öffnung) wurde regelmäßig ausgelöst. Verbesserungen:

- **Neuer Attempt 3:** Vor der Tab-Öffnung wird jetzt `saveAs: true` versucht — das öffnet den Android-System-Speichern-Dialog (SAF). Auf Samsung + Pixel praktisch immer erfolgreich, weil der System-Dialog die Storage-Zugriffs-Rechte selbst regelt
- Progress-Notification erklärt den Dialog im Voraus: "Bitte im gleich erscheinenden System-Dialog Speicherort wählen ..."
- Timeout auf 60 Sekunden erhöht (User braucht Zeit zum Wählen)
- **Tab-Öffnung ist jetzt Attempt 4** (nur wenn auch SAF-Dialog fehlschlägt)
- **Bessere Fallback-Anleitung:** konkrete Schritte statt vager Hinweise. "1. Tippe die 3 Punkte oben rechts / 2. Waehle 'Herunterladen' / Alternative: 'Teilen' → 'In Datei speichern'"

## 2.1.6 — 2026-07-21 (Rebuild)

Reiner Rebuild fuer erneuten AMO-Upload. Keine Code-Aenderung.

## 2.1.5 — 2026-07-21 (Rebuild)

Reiner Rebuild fuer erneuten AMO-Upload. Keine Code-Aenderung gegenueber 2.1.4.

## 2.1.4 — 2026-07-21 (Robuste 3-Stufen-Save-Strategie + Tab-Notausgang)

User-Report Samsung S24: "Speichere PDF ..." erscheint, aber danach passiert nichts. Keine Datei im Downloads-Ordner, kein neuer Ordner, keine Fehlermeldung.

Root-Cause: `browser.downloads.download()` auf Firefox for Android (v.a. Samsung One UI + SAF-Storage) kann die Promise NIE resolven oder rejecten — der Await bleibt still ewig hängen. Der bisherige `try/catch` fing das nicht ab weil kein Reject kommt.

**Neue 3-Stufen-Save-Strategie:**

1. **Attempt 1** — `downloads.download` mit Sub-Ordner + Timeout 5 s
2. **Attempt 2** — falls Timeout: `downloads.download` ohne Sub-Ordner (Root `Download/`) + Timeout 5 s
3. **Attempt 3** — falls auch das nicht klappt: `browser.tabs.create()` öffnet das PDF direkt im Firefox-Viewer. Der User kann dann über das Firefox-Download-Symbol in der Adressleiste manuell speichern

**Weitere Fixes:**
- `withTimeout()`-Helper wrappt jeden `downloads.download`-Aufruf — kein stiller Hänger mehr möglich
- Notification-Tap holt den Fallback-Tab in den Vordergrund, wenn Save via Tab-Open lief
- Save-State (`_lastDownloadId`, `_lastFilename`, `_lastFallbackTabId`) wird bei jedem neuen Capture reset
- Fallback-Notification erklärt WAS zu tun ist: "PDF wurde im Browser geöffnet. Nutze das Firefox-Download-Symbol oben in der Adressleiste um es lokal zu speichern."

Ergebnis: Selbst auf Geräten wo `downloads.download` komplett stillsteht, bekommt der User die PDF sichtbar — nie mehr "es passiert nichts".

## 2.1.3 — 2026-07-21 (Progress-Fix + Adaptive-Device-Anpassung + Subfolder-Fallback)

User-Report:
- Erfasse-Notification blieb bei 64% stehen, Notification-Tap tat nichts
- Zwei parallele Notifications ("Erfasse Seite ..." + "Erfasse Seite ... 64%")
- Keine PDF-Datei sichtbar im Downloads-Ordner (Samsung S24)

Ursachen:
1. Start-Notification hatte keine gemeinsame ID mit den Progress-Updates -> beide standen parallel
2. `downloads.download` mit Sub-Ordner-Pfad wird auf einigen Android-Geraeten (v.a. Samsung One UI mit SAF) still abgelehnt -> Datei landet nirgendwo, Loop endet ohne User-Feedback
3. Notification-Tap-Handler machte nichts wenn `_lastDownloadId` noch null war
4. tilePx=2000 ist nicht optimal fuer alle Geraete — Samsung S24 mit DPR 3.5 und 12 GB RAM verschenkt Performance, Low-End-Geraete mit 2 GB RAM koennten OOM bekommen

Fixes:
- **Notification-Dedup:** Start-Notification "Erfasse Seite ..." nutzt jetzt die gleiche `pdfsnap-progress`-ID wie die 64%-Updates. Es gibt nur noch EINE Progress-Notification, die sich in-place aktualisiert
- **Save-Phase-Update:** Nach dem Loop erscheint "Speichere PDF (X Seiten) ..." — damit der User sieht dass die 64% nicht der Endzustand sind
- **Subfolder-Fallback:** Wenn `downloads.download` mit Sub-Ordner-Pfad rejected wird, retry mit reinem Dateinamen in Root `Download/`. Die Fertig-Notification vermerkt "(Root Download-Ordner)" falls Fallback aktiv war
- **Downloads-Fehler transparent:** Fehler bei Save wird jetzt als Notification angezeigt statt still zu verschlucken
- **Notification-Tap reagiert immer:** waehrend Capture -> "Aufnahme laeuft noch"; wenn nichts fertig -> "Tippe zuerst auf das Erweiterungs-Symbol"; nach Fertig -> oeffnet PDF; bei Fehler -> zeigt Datei-Pfad
- **Adaptive Kachel-Groesse auf Android:** Content-Script rapportiert DPR + RAM + CPU-Cores. Background berechnet effektives tilePx: Basis 2500 CSS-Pixel skaliert mit `2/DPR`, RAM-Bonus/Malus. Samsung S24 Ultra (DPR 3.5, 12 GB) bekommt ~2000 px, Low-End (DPR 2, 2 GB) ~1750 px, Desktop bleibt User-Setting
- **Erweiterte Diagnose-Info in Options:** zeigt Bildschirm-Aufloesung, DPR, RAM, CPU-Kerne und die effektive adaptive Kachel-Groesse pro Geraet

## 2.1.2 — 2026-07-21 (Android-Simulator / Pre-Flight-Testrunner)

Neuer lokaler Testrunner `tests/simulate-android.js` — laeuft in unter einer Sekunde und findet Firefox-for-Android-Fallen bevor die Extension aufs Handy kommt.

- **Neu:** 79 Checks in 9 Sektionen (Manifest, Android-API-Fallen, Pipeline-Vollstaendigkeit 34/34, Defaults-Konsistenz, Android-Overrides, Content-Script, Options-UI, Sicherheitsnetze, HTML)
- **Neu:** Semantische Guard-Analyse — der Simulator versteht die umschliessende Funktion und prueft ob ein Android-Early-Return im Funktions-Scope existiert (nicht nur Fixed-Char-Window)
- **Neu:** Exit-Code 0/1 fuer CI-Integration, `README.md` in `tests/`
- Aufruf: `node tests/simulate-android.js` — keine Dependencies noetig, kein Emulator, kein Handy
- Ideal als Pre-Build-Hook vor jedem `web-ext build` und AMO-Upload

## 2.1.1 — 2026-07-21 (Options-UI: adaptive Ausloese-Anleitung)

- **Neu:** Die Einstellungs-Seite zeigt jetzt eine plattform-spezifische Ausloese-Anleitung. Auf Desktop erscheint der Desktop-Kasten (Toolbar-Klick, Ctrl+Shift+Y, Rechtsklick), auf Android der Android-Kasten (Menue → antippen, Progress in Benachrichtigungsleiste, Fertig-Notification tippen)
- **Neu:** Diagnose-Info am Ende der Options-Seite: erkanntes Betriebssystem + Extension-Version. Vereinfacht Support ("bei mir zeigt es X an").
- **Neu:** Android-spezifische Nutzungs-Hinweise direkt im Info-Kasten (Tab-Fokus, Hintergrund-Wechsel, Ordner-Pfad)

## 2.1.0 — 2026-07-21 (Android: Root-Cause "keine PDF sichtbar" + UX-Polish)

User-Report: Auf Firefox for Android bleibt "Erfasse Seite ..." als einzige Notification stehen, es erscheint keine Datei in den Downloads. Nach Analyse: wahrscheinlicher Root-Cause ist `browser.tabs.captureVisibleTab(tab.windowId, ...)` — auf Firefox for Android existiert die `windows`-API nicht, `tab.windowId` ist dort haeufig `undefined`. Der Aufruf schlaegt still fehl oder wirft, der Loop bricht ohne User-Feedback ab.

- **Root-Fix:** captureVisibleTab-Aufruf abgesichert — erst mit `windowId`, bei Fehler Fallback ohne Argument (Firefox waehlt dann aktuelles Window automatisch). Damit funktioniert der Screenshot auf Firefox for Android zuverlaessig
- **Progress-Feedback:** Alle 2 Segmente wird die "Erfasse Seite ..."-Notification mit Prozent-Fortschritt aktualisiert (z.B. "Erfasse Seite ... 45%"). Zusaetzlich zeigt der Badge die Segment-Anzahl. Nutzer sieht dass der Prozess laeuft
- **Tab-Wechsel-Schutz:** Vor jedem Screenshot pruefen ob der Ziel-Tab noch aktiv ist. Wenn der Nutzer zwischen Tabs wechselt, wird automatisch wieder auf den Original-Tab gewechselt, damit nicht der falsche Tab erfasst wird
- **Standard-Unterordner "Full Page PDF Snap"** — auf Desktop UND Android. Vorher hatte Android bewusst keinen Unterordner; die PDFs waren im Downloads-Ordner zwischen anderen Dateien verstreut. Jetzt sammelt sich alles unter `Download/Full Page PDF Snap/` (Android faellt bei fehlender Unterordner-Unterstuetzung stumm auf Root zurueck)
- **Options-UI Android-gefiltert:** Die "Ordner zeigen"-Optionen unter "Nach Erstellung" werden auf Android jetzt ausgeblendet (`downloads.show` existiert dort nicht). Der Hinweis zur Capture-Skalierung wird ebenfalls angepasst
- **Sicherheitsnetz `getSettings`:** Falls doch mal via Sync ein `afterCapture: "show"` auf Android landet, wird es transparent auf `"open"` gemappt
- **Bessere Fehler-Notifications:** Getrennt in "Hinweis" (bei nicht erfassbaren Seiten wie `about:*` oder `addons.mozilla.org`) und "Fehler" (bei technischem Problem). Die Progress-Notification wird bei Fehler und Erfolg jetzt aktiv geschlossen, damit sie nicht doppelt neben anderen Meldungen stehen bleibt
- **Popup-Handshake:** `browser.runtime.sendMessage`-Handler unterscheidet jetzt zwischen echtem Fehler und User-Hinweis, damit das Popup bei Fehler nicht mehr "Gespeichert (undefined Seiten)" zeigt

## 2.0.4 — 2026-07-21 (Notification-Icon-Fix)

Bei Vollcheck-Audit gefunden: Notifications referenzierten `icon.svg`. SVG-Notification-Icons werden auf Android und einigen Desktop-Themes nicht zuverlaessig gerendert (leeres Icon oder Standard-Firefox-Symbol).

- **Fix:** Notification-Icon auf `icon-48.png` umgestellt — PNG wird auf allen Plattformen konsistent gerendert
- Sonst keine Verhaltensaenderung — reine Kosmetik-/Konsistenz-Korrektur

## 2.0.3 — 2026-07-21 (Android: Notification-Tap oeffnet PDF + Root-Downloads)

User-Report: Nach dem Icon-Tap erschien "Erfasse Seite ..." als Notification, danach passierte nichts sichtbar mehr — kein Erfolg, kein Oeffnen. Ursache: `browser.downloads.open()` haengt auf Firefox for Android teilweise still im Await-Chain, sodass weder die Success-Notification noch der Badge-Wechsel je ausgefuehrt werden.

- **Fix:** Success-Notification wird jetzt SOFORT nach erfolgreichem Save gefeuert, BEVOR `downloads.open()` versucht wird. So sieht der Nutzer den Erfolg auch dann, wenn das Oeffnen still haengt
- **Fix:** `runAfterCapture` laeuft jetzt non-blocking mit 5-Sekunden-Timeout — die Extension bleibt nicht mehr am Oeffnen haengen
- **Fix:** Wait-Timeout auf Android von 30s auf 8s reduziert; auch wenn `downloads.onChanged.complete` nie feuert (bekannter Android-Fall), sieht der User trotzdem Feedback
- **Neu:** Notification tippen oeffnet die zuletzt gespeicherte Datei — Fallback zum haengenden Auto-Oeffnen
- **Neu:** Auf Android wird KEIN Unterordner mehr angelegt — die PDFs landen direkt im System-Downloads-Ordner (`Download/`, sichtbar in jeder Datei-App). Unterordner werden von Firefox for Android nicht auf allen Versionen zuverlaessig unterstuetzt
- **Neu:** Erfolgs-Notification zeigt den Dateinamen mit Hinweis "Tippen zum Oeffnen"

## 2.0.2 — 2026-07-21 (Android — klare Fehlermeldung auf geschuetzten Seiten)

Reaktion auf User-Report: Beim Antippen des Icons auf `addons.mozilla.org` oder dem PDF-Viewer erschien der technische Fehler "Diese Seite erlaubt keine Erweiterungs-Skripte (about:/addons.mozilla.org/PDF-Viewer etc.)". Ursache ist Firefox-Sicherheitspolicy — Content-Scripts sind auf diesen Seiten prinzipiell blockiert. Die Meldung wirkte aber wie ein Extension-Bug.

- **Neu:** Pre-flight-URL-Check vor jedem Capture-Versuch. Blockierte Domains (`addons.mozilla.org`, `accounts.firefox.com`, `support.mozilla.org`, `install.mozilla.org`), `about:*`-Seiten und PDF-Viewer werden erkannt, bevor `executeScript` ueberhaupt versucht wird
- **Neu:** Handlungsanleitende Fehlermeldung statt technischer Diagnostik — z.B. "Firefox schuetzt diese Seite. Bitte zu einer normalen Webseite wechseln (z.B. wikipedia.org)."
- **Neu:** Auf Android erscheint diese Meldung direkt als Notification (nicht nur als Log)

## 2.0.1 — 2026-07-21 (Android-UX)

Schnelle Usability-Wins fuer Firefox for Android.

- **In-Flight-Guard:** Doppel-Tap auf das Toolbar-Icon startet keinen zweiten Capture mehr, waehrend der erste noch laeuft
- **Sofort-Feedback beim Tap (Android):** Notification "Erfasse Seite ..." erscheint direkt beim Antippen, damit der Nutzer sieht dass etwas passiert (weil auf Android kein Popup mehr geoeffnet wird)
- **Erfolgs-Notification (Android):** "Fertig (N Seiten) — PDF wird geoeffnet." nach Abschluss
- **Badge-Text als Statusanzeige:** "..." (blau) waehrend Capture, "OK" (gruen) bei Erfolg, "!" (rot) bei Fehler — automatisches Ausblenden nach 3-4 Sekunden
- **Dynamischer Toolbar-Title:** waehrend Capture zeigt Langes-Druecken/Hover "Capture laeuft ..." statt Ctrl+Shift+Y-Hinweis

## 2.0.0 — 2026-07-21

Erstveroeffentlichung der **oeffentlichen Variante ohne OCR**.

Abgespalten vom internen Repo `firefox-pageshot` (dort verbleibt die Version mit Native-Messaging fuer lokalen Tesseract-Helfer).

### Aenderungen gegenueber der internen 1.4.0

- **Entfernt:** `nativeMessaging`-Permission
- **Entfernt:** OCR-Code (ocrViaNative, pingOcrHost, maybeOcrAfterDownload)
- **Entfernt:** OCR-Options-Sektion (ocrEnabled, ocrLang, OCR-Test-Button)
- **Entfernt:** Dokumente `OCR-SETUP-GUIDE.*`
- **Neu:** Default `jpegQuality` von 0.90 auf **0.92** angehoben (Screenshot-Standard)
- **Neu:** Default `captureScale` von 1.0 auf **1.5x** (Screenshot-Standard, deutlich schaerfere Screenshots)
- **Neu:** Android-Direktcapture — beim App-Start wird `browserAction.popup` auf leer gesetzt; Icon-Tap loest `onClicked` direkt aus, statt Popup-Fenster zu oeffnen
- **Neu:** Android-Override `afterCapture: "open"` statt `"none"` — PDF wird nach Erstellung direkt in der System-App geoeffnet (Ordner-Anzeige existiert unter Android nicht)
- **Neu:** Extension-ID `fullpage-pdf-snap@bubu89.public` (getrennter Slot fuer AMO-Listing)
- **Neu:** Kontextmenue wird auf Android nicht mehr aufgebaut (existiert dort nicht)