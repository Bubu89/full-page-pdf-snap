# Visuelle Pruefung

Stand: 2026-08-01 11:49

| Seite | Ergebnis | Bildflaechen |
|---|---|---|
| [Produktseite](https://provinglab.dev/tools/full-page-pdf-snap/) | fehlt sichtbar: „qualified electronic document“; nur 0 sichtbare Bildflaechen, erwartet 3 | 0 |

Aufnahmen liegen in `_visual-check/`.

Methode: Seite in echtem Chrome gerendert, per Tesseract zurueckgelesen,
gegen Erwartungen verglichen. Findet Fehler, die im HTML unsichtbar sind —
nicht geladene Bilder, falsche Inhalte in Grafiken, unsichtbaren Text.