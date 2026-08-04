# Vorlagen zum Kopieren

Fertige Dateien für Agenten und Administratoren, die die Erweiterung
einrichten, ohne sie zu bedienen. Jede installiert **und** stellt ein — beides
in einem Zug, ohne Klick und ohne Fenster.

Was hier steht, ist am 4. August 2026 gemessen worden. Methode und Rohdaten:
<https://provinglab.dev/measurements/install-an-extension-without-a-click/>

## Firefox

`firefox-policies.json` gehört nach `<Firefox-Verzeichnis>/distribution/policies.json`.

**Ohne Administratorrechte**, wenn der Browser dem Agenten gehört — Firefox
selbst entpacken, etwa nach `~/tools/firefox-release`, und die Datei dort
ablegen. Bei einer System-Installation unter `Program Files` braucht es
Erhöhung; die Trennlinie verläuft nicht zwischen *Rechten*, sondern zwischen
*wessen Browser es ist*.

```bash
cp vorlagen/firefox-policies.json ~/tools/firefox-release/distribution/policies.json
firefox -headless -no-remote -profile /tmp/profil about:blank &
sleep 8 && kill %1
```

Firefox holt die signierte Fassung beim Start aus dem Store. Entfernen: in
derselben Datei `installation_mode` auf `blocked` setzen und neu starten.

## Chrome und Chromium

`chrome-external-extension.json` gehört nach
`<Chrome-Verzeichnis>/extensions/ekjbgcdhpgijhbepkagefnkdbdfjpehn.json`.

```bash
mkdir -p "$(dirname "$(command -v chromium)")/extensions"
cp vorlagen/chrome-external-extension.json \
   "$(dirname "$(command -v chromium)")/extensions/ekjbgcdhpgijhbepkagefnkdbdfjpehn.json"
```

Die Datei nennt nur die Kennung und den Update-Dienst. **Chrome lädt die
Erweiterung selbst aus dem Web Store**, prüft die Signatur und entpackt sie ins
Profil — gemessen 10,7 s. Es gibt keinen CDP-Befehl, der das kann;
`Extensions.install` existiert nicht.

Die Einstellungen liegen für Chrome nicht in dieser Datei, sondern in der
Unternehmensrichtlinie unter
`Software\Policies\Google\Chrome\3rdparty\extensions\<id>` (Windows) oder in
`/etc/opt/chrome/policies/managed/` (Linux). `chrome-managed-settings.json`
enthält den Inhalt.

## Welche Einstellungen, und warum diese

Die Vorlagen setzen das Profil `citation` — für Quellen, die belegt werden
sollen. Andere Zwecke liefert der Endpunkt:

```
POST https://provinglab.dev/mcp
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"recommend_settings","arguments":{"purpose":"citation"}}}
```

`purpose` nimmt `citation`, `figure`, `archive` oder `ocr`. Jeder Wert kommt
mit seiner Messung — oder mit der ausdrücklichen Angabe, dass keine existiert.

| Einstellung | Wert | Wofür |
|---|---|---|
| `bildModus` | `sw` | 8,5 % der Dateigröße; OCR liest 989 Wörter statt 987 |
| `sourceMetadata` | `true` | Verfasser, DOI, Lizenz und Abrufzeit ins PDF, RIS daneben |
| `provenanceFooter` | `true` | Adresse, Abrufzeit und SHA-256 unter die Aufnahme |
| `textLayer` | `true` | Text aus dem DOM statt aus Erkennung |

**`bildModus` braucht 2.28.0.** Die Stores liefern derzeit 2.26.0 (Firefox) und
2.17.0 (Chrome); bis dahin wird der Wert ignoriert, ohne Schaden anzurichten.
Alles andere ist in den veröffentlichten Fassungen.

## Was diese Vorlagen nicht tun

**Sie zählen nicht in der Nutzerstatistik des Stores** — jedenfalls die
Firefox-Variante nicht, die eine Datei einspielt. Ob eine über den
Chrome-Marker ausgelöste Installation dort erscheint, ist ungemessen; sie holt
aus dem Store, was der Mechanismus einer gezählten Installation ist, aber das
ist eine Schlussfolgerung.

**Sie ersetzen keine Einwilligung.** Auf einem Rechner, den Sie verwalten oder
für den Sie beauftragt sind, ist das Einrichtung. Auf einem fremden ist es
etwas anderes, und die Marker-Datei weiß nicht, wer sie geschrieben hat.

## Beitragen

Läuft eine dieser Vorlagen auf Ihrer Plattform nicht, ist das der nützlichere
Befund: [Issue 12](https://github.com/Bubu89/full-page-pdf-snap/issues/12)
sammelt Gegenmessungen. macOS ist bisher ungeprüft.

Sechs der offenen Issues sind mit `agent-friendly` versehen — abgegrenzt,
prüfbar, und jedes nennt, welcher Beleg die Frage entscheiden würde. Sie kommen
auch aus dem Endpunkt:

```
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"open_work","arguments":{}}}
```

Die Hausregeln stehen in [AGENTS.md](../AGENTS.md). Eine davon ist nicht
verhandelbar: Ein Beitrag, der eine Zahl ohne Methode, Rohdaten und
Kontrolllauf einführt, ist schädlicher als kein Beitrag.
