# Anleitung: die Schritte, die nur Sie ausführen können

Stand 3. August 2026. Nach Wirkung sortiert. Jeder Schritt nennt, was ich
vorbereitet habe und wo genau Ihre Hand nötig ist.

---

## Schritt 1 — Chrome-Store auf Stand bringen (20 Minuten, größte Wirkung)

Der Store liefert **2.12.1**, gebaut und geprüft liegt **2.27.0**. Jeder Verweis
auf den Chrome-Store — Website, `llms.txt`, Agent-Fähigkeit, das `nextStep`-Feld
des MCP-Endpunkts — führt derzeit zu einer vierzehn Versionen alten Fassung.

**Fertig vorbereitet:**

    C:\Users\HOLO\Documents\FullPagePDFSnap_Chrome\upload\
      full-page-pdf-snap-chrome-2.27.0.zip     143 KB, 26 Dateien
      SHA-256: 86654df14b9d59fa…

**Ihre Schritte:**

1. <https://chrome.google.com/webstore/devconsole> öffnen, Konto
   `denkmaschinchen@gmail.com`.
2. *Full Page PDF Snap* → **Paket** → **Neues Paket hochladen** → die ZIP wählen.
3. **Store-Eintrag** → Titel und Zusammenfassung aus
   `store-texte/EINREICHEN_2026-08-03.md` einsetzen.
4. **Zur Überprüfung einreichen.**

**Vorsicht bei den Texten** — die Ablehnung vom 2. August („Impersonation
Assets") hing an Gestaltung, nicht an Inhalt: keine Versalien-Schlagzeilen,
keine Sonderzeichen-Rahmen, und *free*, *best*, *#1*, *recommended* nicht als
Werbeaussage. Sachliche Verneinungen und Lizenzangaben sind zulässig.

---

## Schritt 2 — Firefox 2.27.0 einreichen (10 Minuten)

Live steht 2.26.0.

1. <https://addons.mozilla.org/developers/addon/full_page_pdf_snap_webpagesave/versions/submit/>
2. XPI hochladen — `pack-firefox.py` legt es unter
   `Documents\FullPagePDFSnap_Firefox\upload\` ab.
3. Bei der Gelegenheit **Titel und Zusammenfassung** ersetzen
   (`EINREICHEN_2026-08-03.md`). Das Wort *screenshot* fehlt bisher und kostet
   laut Messung zwei von sechs Suchbegriffen.
4. Kategorie *Privacy & Security* → *Bookmarks* tauschen. Begründung und Zahlen
   stehen in derselben Datei.

---

## Schritt 3 — Publisher-Domain im Chrome-Store (15 Minuten, einmalig)

Ergibt das **Established-Publisher-Abzeichen**. Es hängt an nachgewiesenem
Domain-Eigentum.

1. <https://search.google.com/search-console> öffnen.
2. **Property hinzufügen** → **Domain** → `provinglab.dev`.
3. Google zeigt einen **TXT-Eintrag** an, etwa
   `google-site-verification=AbC…`.
4. **Diesen Wert schicken Sie mir** — ich setze den DNS-Eintrag über die
   Cloudflare-API und melde, sobald er aufgelöst wird.
5. Zurück in der Search Console **Bestätigen** klicken.
6. Im Chrome-Dashboard unter **Konto** die verifizierte Domain hinterlegen.

**Einordnung, damit die Erwartung stimmt:** Rund 75 % des Stores tragen dieses
Abzeichen. Es ist notwendig, nicht hinreichend — im Januar 2026 erreichten zwei
nachahmende Erweiterungen 900.000 Menschen, eine davon mit *Featured*-Abzeichen.
Es schadet nicht und kostet nichts, aber es ist kein Wachstumshebel.

---

## Schritt 4 — Ersten Herkunftsnachweis auslösen (2 Minuten)

Der Ablauf liegt fertig in `.github/workflows/release-mit-herkunftsnachweis.yml`
und wartet auf einen Versions-Tag.

    git tag v2.27.0
    git push origin v2.27.0

Das erzeugt Firefox- und Chromium-Paket **in der Pipeline** (eine hochgeladene
Datei ließe sich nicht bezeugen), hängt Prüfsummen an und legt einen
Sigstore-Nachweis im Transparenzprotokoll ab. Danach kann jeder prüfen:

    gh attestation verify full-page-pdf-snap-chrome-2.27.0.zip \
       --repo Bubu89/full-page-pdf-snap

Der Ablauf **bricht ab**, wenn die beiden Manifeste unterschiedliche Fassungen
tragen — genau der Fehler, der vierzehn Versionen lang unbemerkt blieb.

---

## Schritt 5 — `cool-frog-b57a` löschen (2 Minuten, Sicherheit)

<https://dash.cloudflare.com/profile/api-tokens>, Konto `Blockinhalt@gmail.com`.

Dieser Token hat **kein Ablaufdatum** und darf *Account API Tokens Write* — er
kann sich also selbst beliebige Rechte geben. Er stand im Chatverlauf. Ihr
Projektgedächtnis hat ihn seit dem 2. August zur Löschung vorgemerkt.

**Nichts hängt mehr an ihm:** Die Pipeline nutzt seit heute
`provinglab-ci-workers-only` (nur Workers Scripts, Ablauf 2027-02-03, geprüft
gegen Token-Verwaltung, DNS und Cache-Purge). Der Zone-Token
`provinglab-zone-full-v2` deckt Cache und DNS ab.

Ich fasse ihn nicht an, weil Löschen irreversibel ist.

---

## Schritt 6 — Ratenbegrenzung im Dashboard (5 Minuten)

Über die API auf dem Gratis-Tarif **nicht erreichbar** — geprüft, ein eigens
erzeugter Token mit *Firewall Services: Write* bekam weiterhin
*Authentication error*. Cloudflare Free erlaubt **eine** kostenlose Regel, und
nur über die Oberfläche.

**Sicherheit** → **WAF** → **Rate limiting rules** → **Create rule**

| Feld | Wert |
|---|---|
| Wenn | `URI Path` **equals** `/mcp` |
| Rate | 60 Anfragen pro 1 Minute |
| Nach | IP-Adresse |
| Dann | Block, Dauer 1 Minute |

Damit lässt sich der offene Endpunkt nicht mehr als Verstärker gegen Dritte
verwenden. 60 pro Minute liegt weit über jedem echten Gebrauch — eine
Quellenliste sind zwanzig Aufrufe.

---

## Was danach von selbst läuft

- **Jeder Push** löst Rechtscheck, Tests, Sitemap-, Platzhalter- und
  Pfadprüfung aus; nur bei null Fehlern wird der Worker ausgeliefert.
- **Nach jedem Push** `python3 tools/cache-nach-deploy.py` ausführen — sonst
  hält der Edge bis zu vier Stunden die alte Fassung. (Die vier Stunden sind
  der Grund, warum es die 504-Ausfälle nicht mehr gibt.)
- `python3 build-versionen.py` hält `/.well-known/extension-versions.json`
  aktuell. Sobald die Stores gleichziehen, verschwinden die beiden Hinweise
  dort von selbst.

## Und der Punkt, der über allem bleibt

Die Domain ist indexiert und rankt für nichts — `provinglab` liefert bei Bing,
Google und DuckDuckGo null Treffer. Der billigste Hebel dagegen ist unverändert
offen: **der MCP-Endpunkt steht in keinem einzigen Verzeichnis.**
`mcp.directory`, LobeHub, Glama, PulseMCP, Smithery. Ein Nachmittag, fachlich
einschlägig, kein Spam — und unabhängig von jedem Store-Rang.
