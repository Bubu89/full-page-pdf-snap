# Neun Sprachen — was noch offen ist

Stand: 16.08.2026 · **13 von 41 Seiten fertig**, 28 offen.

## Verfahren je Seite

1. Ausgangstext ist die **ausgelieferte Seite**, nie ein alter `build-*.py`.
   Vierzehn von vierzehn Buildern weichen ab, vier loeschen Text —
   `build-mcp-post.py` schneidet seine Seite von 1281 auf 673 Woerter.
   Vor jedem Neubau: `python3 tools/builder-drift.py`
2. Rumpf holen: alles zwischen `<div class="wrap">` und `</div>` vor `</body>`.
3. `texte_<name>.py` anlegen mit `URL`, `ZIEL`, `SPRACHEN`, `BASIS`, `INHALT`.
   Muster: `texte_kompression.py` (reiner Fliesstext) oder `texte_android.py`
   (grosse Tabelle als gemeinsame Konstante, nicht neunmal abgeschrieben).
4. Bauen: `python3 tools/seite-neunsprachig.py texte_<name>.py`
   (`--pruefen` baut nichts, meldet nur Wortzahlen)
5. Abnehmen: `python3 tools/pruefe-alle-sprachen.py` — echtes DOM, kein Markup.

## Unverrueckbar in jeder Sprache

Zahlen, Masseinheiten, Versionsnummern, Dateiformate, Werkzeug- und
Funktionsnamen, Eigennamen, alle Adressen. Eine uebersetzte Zahl waere eine
andere Messung. Nach jeder Seite gegenlesen, dass jede Kennzahl in allen neun
Fassungen vorkommt.

## Offene Seiten, nach Umfang

| Woerter | Seite |
|---:|---|
| 660 | `/deutsch/` |
| 667 | `/anleitung/webseite-als-pdf-speichern/` |
| 696 | `/notes/who-actually-reads-this/` |
| 729 | `/how-to/save-a-webpage-as-pdf/` |
| 853 | `/mitmachen/` |
| 1025 | `/notes/nineteen-issues/` |
| 1049 | `/notes/sources-a-machine-cannot-cite/` |
| 1105 | `/notes/installing-your-own-tool/` |
| 1143 | `/privacy.html` |
| 1144 | `/measurements/pdf-extension-permissions/` |
| 1219 | `/measurements/citation-triage/` |
| 1222 | `/measurements/citation-extraction/` |
| 1248 | `/notes/agent-cites-a-source/` |
| 1281 | `/notes/mcp-server-what-it-solves/` |
| 1328 | `/measurements/extension-permissions-risk/` |
| 1403 | `/measurements/citation-by-platform/` |
| 1494 | `/measurements/install-an-extension-without-a-click/` |
| 1539 | `/measurements/webpage-to-pdf-for-ocr/` |
| 1662 | `/notes/what-an-agent-can-do-with-an-extension/` |
| 1685 | `/measurements/print-to-pdf-vs-screenshot/` |
| 1701 | `/notes/what-an-agent-may-install/` |
| 1727 | `/notes/building-with-ai-what-went-wrong/` |
| 1873 | `/tools/pushdictate/` |
| 1875 | `/measurements/de-plattformen/` |
| 2291 | `/notes/pages-gone-before-you-need-them/` |
| 3188 | `/measurements/web-citations-that-vanish/` |
| 3322 | `/measurements/reading-list-to-bibliography/` |
| 4273 | `/tools/full-page-pdf-snap/` |

Summe Ausgangstext **43402 Woerter**; mal acht weitere Sprachen rund
**347.216 Woerter** Uebersetzung. Erfahrungswert aus den beiden am
16.08. gebauten Seiten: eine Seite kostet rund 25.000 Token Ausgabe.

Drei alte Adressen sind Weiterleitungen ohne Prosa und zaehlen nicht mit;
`pruefe-alle-sprachen.py` ueberspringt sie seit 16.08.2026.
