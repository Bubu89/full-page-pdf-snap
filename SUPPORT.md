# Support

## Reporting a problem

Open an issue: **[github.com/Bubu89/full-page-pdf-snap/issues](../../issues)**

To get a useful answer quickly, please include:

1. **Firefox version** — `about:support` → "Version"
2. **Operating system** — Windows / macOS / Linux / Android
3. **Extension version** — visible at the bottom of the settings page
4. **The page** where it happened (if it is public)
5. **What you expected** and what happened instead

## Known limitations

| Situation | Reason |
|---|---|
| Capture stops early on infinite-scroll feeds | The page never reaches a stable end — no fixed page height exists |
| Very long pages produce large files | Lower the JPEG quality or raise the tile height in the settings |
| Scaling has no effect on Android | `tabs.setZoom` is not available in Firefox for Android |
| Pages with `file://` URLs are not captured | Requires explicit file access, which the extension does not request |
| Content behind a login is captured as you see it | The extension captures the rendered page, nothing more |

## Privacy questions

The extension contacts no server. There is no analytics, no telemetry, no crash reporting. If you want to verify this, the complete source is in this repository — `background.js` holds all capture and PDF logic.

## Response time

This is a free, MIT-licensed side project maintained by one person. Issues are usually looked at within a few days.

---

# Support (Deutsch)

## Fehler melden

Issue eröffnen: **[github.com/Bubu89/full-page-pdf-snap/issues](../../issues)**

Bitte angeben:

1. **Firefox-Version** — `about:support` → „Version"
2. **Betriebssystem** — Windows / macOS / Linux / Android
3. **Erweiterungs-Version** — steht unten auf der Einstellungsseite
4. **Die betroffene Seite** (sofern öffentlich)
5. **Was du erwartet hast** und was stattdessen passiert ist

## Bekannte Grenzen

| Situation | Grund |
|---|---|
| Aufnahme endet früh bei Endlos-Scroll-Feeds | Die Seite erreicht kein stabiles Ende — es gibt keine feste Seitenhöhe |
| Sehr lange Seiten erzeugen große Dateien | JPEG-Qualität senken oder Kachelhöhe in den Einstellungen erhöhen |
| Skalierung wirkt auf Android nicht | `tabs.setZoom` ist in Firefox für Android nicht verfügbar |
| `file://`-Seiten werden nicht erfasst | Erfordert expliziten Dateizugriff, den die Erweiterung nicht anfordert |
| Inhalte hinter einem Login werden so erfasst, wie du sie siehst | Die Erweiterung nimmt die gerenderte Seite auf, nicht mehr |

## Antwortzeit

Freies MIT-Projekt, von einer Person gepflegt. Issues werden in der Regel innerhalb weniger Tage angesehen.
