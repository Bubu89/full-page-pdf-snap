# Changelog

## 2.12.0 — 2026-07-27 (beide)

**Was:** Das Tastenkürzel wird überall aus dem gemeldet, was der Browser
tatsächlich vergeben hat, und Chrome bekommt ein zweites Kürzel.

**Warum:** Der Hinweiskasten auf der Optionsseite nannte weiterhin
`Ctrl+Shift+Y`, obwohl der Standard längst `Alt+Shift+P` war — die Kombination
stand fest im HTML, während das Feld darüber schon den echten Wert las. Wer
sich auf den Kasten verließ, drückte in Firefox die Tastenkombination der
Bibliothek und wunderte sich, dass nichts geschieht.

**Wie:**
- `options.html`, Toolbar-Tooltip und Feld speisen sich aus `commands.getAll()`;
  eine fest verdrahtete Kombination gibt es nirgends mehr.
- Chrome erhält zusätzlich `Ctrl+Shift+Y`. Die Ctrl+Shift-Reihe ist dort im
  Gegensatz zu Firefox weitgehend frei, und es war das frühere Kürzel — wer es
  gewohnt war, behält es. Firefox bleibt bei einem, weil dort A, B, C, D, E, G,
  H, I, J, K, M, N, O, P, Q, R, T, V, W, Y und Z belegt sind.
- Der Befehlsempfänger reagiert auf jeden Namen mit dem Präfix
  `capture-full-page`, beide Kürzel lösen dasselbe aus.
- Der Tooltip wird beim Laden richtiggestellt, nicht erst nach der ersten
  Aufnahme.
- Eine deutsche Restzeile in der Android-Hilfe übersetzt.

**Ergebnis:** Die Optionsseite zeigt in Chrome `Alt+Shift+P / Ctrl+Shift+Y`, in
Firefox `Alt+Shift+P` — und zwar genau das, was auch auslöst. Beansprucht ein
Browser eine Kombination für sich, erscheint sie schlicht nicht.

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