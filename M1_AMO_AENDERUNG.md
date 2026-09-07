# M1 — AMO-Eintrag am Anwendungsfall ausrichten

**Stand 17.08.2026.** Vorbereitet und gemessen; die Ausführung braucht einen
API-Schlüssel aus dem **Eigentümerkonto**.

---

## Warum das blockiert ist

| | |
|---|---|
| Eigentümer des Add-ons | AMO-Konto **20041617 „Silence"** |
| Einziger funktionierender Schlüssel im Vault | AMO-Konto **19887469 „Chris Yo"** |

Geprüft am 17.08.2026 über `/api/v5/accounts/profile/` — zerstörungsfrei, ohne
Schreibversuch. Die beiden anderen Vault-Einträge (`accounts.firefox.com`,
`Mozilla Firefox Account — Infra`) tragen kein vollständiges JWT-Paar.

**Ein Schreibzugriff ist damit unmöglich.** Es fehlt nicht das Werkzeug,
sondern ein Schlüssel, den nur ein interaktiver Login im Konto *Silence*
erzeugen kann: <https://addons.mozilla.org/developers/addon/api/key/>

---

## Vorher-Messung (die Begründung)

`python3 tools/amo-sichtbarkeit.py` — 14 Suchbegriffe, Position des Add-ons.

| Suchbegriff | Position | Treffer gesamt |
|---|---:|---:|
| full page pdf | **1** | 283 |
| citavi | **6** | 9 |
| save page as pdf | **9** | 516 |
| zotero | **10** | 28 |
| ris | 15 | 379 |
| cite webpage | 22 | 138 |
| web page pdf | 22 | 531 |
| source capture | 61 | 444 |
| **citation** | **nicht in Top 75** | 462 |
| **reference manager** | **nicht in Top 75** | 319 |
| **scholar** | **nicht in Top 75** | 181 |
| **research** | **nicht in Top 75** | 4.854 |
| archive webpage | nicht in Top 75 | 116 |
| screenshot pdf | nicht in Top 75 | 478 |

**Das Muster ist eindeutig:** Das Add-on rankt dort, wo sein **Name** passt
(„full page pdf" auf Platz 1), und fehlt dort, wo sein **Nutzen** liegt —
citation, reference manager, scholar, research.

Der Kurztext nennt DOI, RIS, Zotero und Citavi. Die Felder, nach denen AMO
sortiert, nennen davon nichts.

---

## Die Änderung

### Kategorien (höchstens drei)

| | Ist | Soll |
|---|---|---|
| 1 | `privacy-security` | `privacy-security` — bleibt, Aufnahme läuft lokal |
| 2 | `bookmarks` | `bookmarks` — bleibt, Quellen aufbewahren |
| 3 | `photos-music-videos` ❌ | **`download-management`** |

`photos-music-videos` ist für Medien-Add-ons. Das Werkzeug erzeugt eine
Datei — `download-management` ist die zutreffende Kategorie und wird von der
Zielgruppe durchsucht.

### Tags

| | Ist | Soll |
|---|---|---|
| 1 | `download` | `download` |
| 2 | `privacy` | `privacy` |
| 3 | `security` | **`scholar`** |

`scholar` ist ein gültiger AMO-Tag mit 759 Add-ons und wird von genau den
Fach-Erweiterungen benutzt, neben denen dieses Add-on stehen soll
(Webtero, Library Check for Zotero). `security` ist bei 2.140 Add-ons
nichtssagend und beschreibt den Nutzen nicht.

Nicht verwendbar, weil kein gültiger AMO-Tag: `research`, `productivity`,
`citation`, `reference` — jeweils 0 Add-ons, also nicht im Vokabular.

---

## Ausführung, sobald ein Schlüssel des Eigentümerkontos vorliegt

```bash
# Schlüssel erzeugen (interaktiv, Konto Silence):
#   https://addons.mozilla.org/developers/addon/api/key/
# danach als Vault-Eintrag ablegen, NICHT in eine Datei:
#   bw-claude add "Full Page PDF Snap (AMO JWT, Silence)" "<issuer>" \
#     "https://addons.mozilla.org/developers/addon/api/key/"

python3 tools/amo-listing-setzen.py            # zeigt den Diff, ändert nichts
python3 tools/amo-listing-setzen.py --anwenden # schreibt
```

Alternativ von Hand, zwei Minuten:
<https://addons.mozilla.org/developers/addon/full_page_pdf_snap_webpagesave/edit>

---

## Nachher-Messung

```bash
python3 tools/amo-sichtbarkeit.py
```

**Erfolgskriterium:** Auftauchen in den Top 75 bei `citation`,
`reference manager` und `scholar`. Diese drei sind heute die klaren Lücken.

**Zweitkriterium:** tägliche Nutzer nach 14 Tagen gegen den Ausgangswert
**31** (17.08.2026).

**Grenze:** AMO indexiert Änderungen nicht sofort; vor der Nachher-Messung
mindestens 48 Stunden warten. Und Suchpositionen schwanken auch ohne eigenes
Zutun — ein einzelner Messpunkt trägt keine Schlussfolgerung.
