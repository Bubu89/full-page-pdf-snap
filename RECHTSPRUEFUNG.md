# Rechtsprüfung: öffentliches Repo, offener Endpunkt, persönliche Exposition

Stand 3. August 2026. **Keine Rechtsberatung.** Eine strukturierte Selbstprüfung
mit dem Ziel, die häufigsten Risiken zu senken und offene Punkte zu benennen.
Bei Abmahnung, Klage oder Unterlassungsaufforderung: Anwalt, nicht dieses
Dokument. Rechtsraum: Österreich (Betreiber), mit Blick auf DE und die
Store-Regeln der Anbieter.

---

## 1. Was von der Person öffentlich ist — Ist-Aufnahme

Gemessen an den ausgelieferten Dateien:

| Kennzeichen | Fundstellen | Bewertung |
|---|---|---|
| `Bubu89` (GitHub-Konto) | 73 | gewollt — Repo-Verweise, Releases, Issues |
| `Silence` (Pseudonym) | 3 | auf `/about/` offengelegt |
| `chris.vis@goldfishgateway.com` | 2 (nur `/about/`) | Kontaktadresse |
| Klarname, Anschrift, Telefon | **0** | nicht veröffentlicht |

`/about/` sagt ausdrücklich: Veröffentlichung unter dem Pseudonym *Silence*,
dasselbe Kürzel wie auf addons.mozilla.org und als *Bubu89* auf GitHub;
Identität und Postanschrift werden **einem berechtigten Anfragenden
unverzüglich offengelegt**.

**Bewertung.** Die Verknüpfung Pseudonym ↔ GitHub-Konto ist bewusst offengelegt
und in sich schlüssig. Wer sie trennen wollte, müsste ein eigenes Konto oder
eine Organisation verwenden — beides nur über die Web-Oberfläche anlegbar.
Solange die Verknüpfung gewollt ist, gibt es hier nichts zu heilen.

**Geprüft am 3. August 2026:** Die RDAP-Abfrage zu `goldfishgateway.com` bei
Verisign gibt als einzige Stelle den Registrar (EuroDNS S.A.) zurück — **keine
Registrierungsdaten des Inhabers**, Status `client transfer prohibited`. Über
diesen Weg fällt die Pseudonymität also nicht. Das war der einzige Kanal, der
von außen mehr hätte preisgeben können als die Seite selbst.

---

## 2. Formalien: Offenlegung (§ 25 MedienG, § 5 ECG)

**§ 5 ECG** gilt für Diensteanbieter, die kommerzielle Kommunikation betreiben.
Die Seite verkauft nichts, wirbt nicht, nimmt keine Zahlung entgegen und bietet
keine Leistung gegen Entgelt — das steht so auf `/about/` und ist strukturell
umgesetzt (keine Werbung, kein Tracking, keine Affiliate-Links, MIT-Lizenz).
Damit greift § 5 ECG nach hiesiger Einschätzung nicht.

**§ 25 MedienG** verlangt für wiederkehrende elektronische Medien eine
Offenlegung. Für „kleine Websites" (Abs 5) genügen Name und Wohnort des
Medieninhabers. Ob ein Pseudonym mit Offenlegung *auf Anfrage* diese Pflicht
erfüllt, ist **strittig**. Die Praxis verfolgt es bei nicht-kommerziellen
Privatseiten selten; ein Restrisiko bleibt.

**Handlungsoptionen, nach Aufwand:**

1. So belassen und das Restrisiko tragen — vertretbar bei belegter
   Nicht-Kommerzialität.
2. Wohnort ohne Straße ergänzen (z. B. „Salzburg, Österreich") — senkt das
   Risiko erheblich, gibt wenig preis.
3. Vollständige Offenlegung — beseitigt das Thema, hebt die Pseudonymität auf.

**Empfehlung:** Option 2. Sie kostet eine Zeile und nimmt der Diskussion die
Grundlage, ohne die Anschrift zu veröffentlichen.

---

## 3. Missbrauch der eigenen Strukturen — der Teil mit dem größten Zuwachs

Durch die Agenten-Anbindung ist aus einer Publikation ein **Dienst** geworden,
der auf Zuruf fremde Adressen abruft. Das verändert die Risikolage.

### 3.1 Offener Abrufdienst ohne Grenze — teilweise behoben

`extract_citation` holt jede genannte öffentliche Adresse ab. Der Abruf trägt
unser Kennzeichen (`provinglab-mcp/…`) und kommt von Cloudflare-Adressen. Ohne
Begrenzung lässt sich der Endpunkt als **Verstärker gegen Dritte** verwenden:
Der Angreifer schickt Anfragen an uns, die Last landet beim Ziel, und im Log des
Ziels steht unser Name.

**Heute behoben:**
- Die Zusage „no rate limit" stand auf vier Seiten. Sie war eine Aussage über
  die Zukunft und eine Einladung. Ersetzt durch „no account and no key · fair
  use, please" bzw. eine Bitte um Verhältnismäßigkeit.
- `rechtscheck.py` prüft jetzt auf solche Zusagen (`zusage-ohne-grenze`).

**Geprüft am 3. August 2026, und die Antwort ist unbequem.** Ein Token mit
*Firewall Services: Write* auf die Zone wurde eigens erzeugt: Er sieht die Zone
(`provinglab.dev` kommt zurück), aber die Phase `http_ratelimit` antwortet
weiterhin mit *Authentication error*. **Ratenbegrenzungs-Regeln sind auf dem
Gratis-Tarif über die API nicht erreichbar.** Der Token wurde wieder gelöscht,
statt ihn ungenutzt stehen zu lassen.

**Was bleibt, ohne Kosten zu verursachen:**

- Die eine kostenlose Regel, die Cloudflare Free vorsieht, im **Dashboard**
  setzen — das ist der einzige Weg, der ohne Tarifwechsel bleibt.
- Der Missbrauch, um den es geht, ist gedämpft, aber nicht ausgeschlossen: Jede
  Anfrage löst höchstens einen externen Abruf plus eine DOI-Auflösung aus, und
  Weiterleitungen sind seit Worker 1.11.0 auf fünf Sprünge begrenzt.
- **Kein Kostenrisiko besteht in keiner Richtung:** Gemessen über 24 Stunden
  laufen rund 4.400 Anfragen über den Worker, also **4,4 % des Gratis-Kontingents
  von 100.000 pro Tag**. Und Cloudflare schaltet bei Überschreitung ab, statt zu
  verrechnen — Ausfall ist möglich, eine Rechnung nicht.

**Web Analytics wurde geprüft und bewusst nicht eingerichtet.** Es wäre gratis,
verlangt aber ein Zählskript auf jeder Seite. `/about/` sagt zu: *no tracking*.
Diese Zusage ist mehr wert als die Besucherstatistik.

### 3.2 Serverseitige Anfragefälschung über Weiterleitungen — behoben

Die Adressprüfung (kein `localhost`, keine privaten Bereiche) griff nur beim
**zuerst genannten** Hostnamen; danach folgte `fetch` mit `redirect: "follow"`
jeder Weiterleitung ungeprüft. Eine öffentliche Adresse, die auf `127.0.0.1`
weiterleitet, umging die Prüfung vollständig.

**Behoben** in Worker 1.11.0: `redirect: "manual"`, jede Weiterleitung wird
gegen dieselbe Regel geprüft, höchstens fünf Sprünge. Gegenprobe: DOI-Resolver
→ Verlag und `http://arxiv.org` → `https://` liefern weiterhin vollständige
Datensätze.

**Offengelegt:** Der Negativtest gelang nicht sauber — der verwendete
Weiterleitungsdienst antwortete mit 503, es gab also gar keine Weiterleitung zu
prüfen. Die Plattform selbst unterbindet Zugriffe eines Workers auf private
Bereiche zusätzlich. Die Härtung stützt sich daher auf die Code-Prüfung, nicht
auf einen bestandenen Angriffsversuch.

### 3.3 Anleitung zur Umgehung fremder Schutzmaßnahmen — geprüft, unkritisch

Die neuen Texte könnten als Anleitung gelesen werden, Bot-Sperren zu umgehen.
Sie sind bewusst umgekehrt formuliert: *„Do not imitate a browser user agent to
get past a rule aimed at you. It does not work on the measured cases and it is
not something to build a citation on."* `rechtscheck.py` prüft das jetzt
maschinell (`umgehungsanleitung`): Wo Umgehung erwähnt wird, muss im Umfeld eine
Abgrenzung stehen.

### 3.4 Verweise auf fremde Software — abgesichert

`how_to_capture` und die Agent-Fähigkeit nennen `chrome-use`,
`browser-agent-bridge`, `openchrome`, `chrome-devtools-mcp`, `xdotool`. Jede
Nennung trägt: *not endorsements, not audited here, check any of them yourself*.
Neue Prüfung `fremdprojekt-ohne-distanz` erzwingt das künftig.

**Warum das zählt:** Ein Verweis ohne Distanzierung liest sich als Zusage. Wenn
eines dieser Projekte Schaden anrichtet, ist der Unterschied zwischen „empfohlen"
und „als Fundstelle genannt, ungeprüft" erheblich.

---

## 4. Aussagen über fremde Anbieter

Die Messungen nennen MDPI, ScienceDirect, SSRN, OECD, EUR-Lex, SSOAR und andere
mit Befunden wie „403", „bot wall", „declares no citation metadata".

**Einordnung:** Das sind **Beobachtungen mit Methode, Datum und Rohdaten**, keine
Werturteile. Jede Messung nennt die Bedingungen, unter denen sie entstand, und
sagt ausdrücklich, dass vier der Ablehnungen Sperren gegen
**Rechenzentrums-Adressen** sind — also nichts über den Anbieter aussagen,
sondern über die anfragende Stelle.

**Neu geprüft:** `absicht-unterstellt` schlägt an, wo einem Anbieter ein Motiv
zugeschrieben wird („deliberately blocks", „publishers want to block"). Das
Muster wurde am Referenzfall gegengetestet: Es trifft die vier Beispielsätze
richtig und meldet den Satz „tools people search for when they want to save a
page" korrekt **nicht**.

**Bewertung nach § 2a UWG (AT):** Vergleiche stützen sich auf objektiv
nachprüfbare Eigenschaften, nennen keine Charaktereigenschaften, und die eigene
Beteiligung ist auf jeder betroffenen Seite offengelegt. Die
Print-gegen-Aufnahme-Messung nennt ausdrücklich die Fälle, in denen die
**Browser-eigene** Funktion besser abschneidet — das ist zugleich der beste
Beleg für Objektivität.

---

## 5. Urheberrecht: was die Erweiterung tut

Sie speichert eine Seite, die der Nutzer bereits geöffnet hat, als PDF auf sein
Gerät. Das ist eine Vervielfältigung zum eigenen Gebrauch (§ 42 UrhG AT). Kein
Umgehen technischer Schutzmaßnahmen, keine Weitergabe, keine Server-Verarbeitung
— die Erweiterung führt keine Host-Rechte und arbeitet lokal.

Diese Einordnung steht in jeder Anleitung: *„Capturing pages you are entitled to
read is a copy for your own use. It is not a way past a paywall or a licence you
do not hold."* Sie steht auch im MCP-Feld `legal`, damit ein Agent sie
weitergibt.

---

## 6. Datenschutz

Kein Tracking, keine Analytik, kein Newsletter, keine Formulare — auf `/about/`
zugesagt und in den ausgelieferten Seiten nachprüfbar (keine externen Skripte).
Verbleibende Verarbeitung: Server-Logs bei Cloudflare und GitHub Pages als
Auftragsverarbeiter, sowie die vom Nutzer selbst genannten Adressen beim Aufruf
des Endpunkts.

**Erledigt am 3. August 2026:** `wrangler.toml` setzt `[observability] enabled = true`,
ohne eine Aufbewahrungsdauer festzulegen — es gilt die Voreinstellung von
Cloudflare Workers Logs. `privacy.html` benennt jetzt in beiden Sprachfassungen,
was gespeichert wird (Anfrage-Protokolle der Plattform: Methode und Adresse der
Anfrage, Antwort, technische Metadaten; der Worker selbst schreibt keine eigenen
Einträge), wo (Workers Logs im Cloudflare-Konto des Betreibers) und wie lange:
höchstens 3 Tage im Tarif Workers Free, 7 Tage in Workers Paid (Quelle:
Cloudflare-Dokumentation, abgerufen am 3. August 2026 — die dort genannten
Werte wurden an diesem Tag gegen die Live-Seite geprüft). Der Tarif des Kontos
war über den vorhandenen API-Token nicht auslesbar (nur Zone-Rechte), die
Formulierung nennt deshalb beide Werte statt zu schätzen. Die Zusage „no
tracking" auf `/about/` bleibt bestehen: Sie meint Zählskripte und Analytik,
und `privacy.html` benennt jetzt, was dennoch anfällt.

---

## 7. Was heute geändert wurde

| Änderung | Wirkung |
|---|---|
| Weiterleitungen werden einzeln gegen die Adressregel geprüft (Worker 1.11.0) | schließt die Umgehung der SSRF-Prüfung |
| „no rate limit" auf vier Seiten entfernt | keine Zusage, keine Einladung |
| `rechtscheck.py` um vier Prüfungen erweitert | `zusage-ohne-grenze`, `umgehungsanleitung`, `fremdprojekt-ohne-distanz`, `absicht-unterstellt` |
| Muster am Referenzfall gegengetestet | ein Fehlalarm gefunden und behoben, bevor er Praxis wurde |

## 8. Offene Punkte, nach Dringlichkeit

1. **Ratenbegrenzung auf `/mcp`** — braucht einen Cloudflare-Token mit
   Firewall-Rechten. Solange sie fehlt, ist der Endpunkt als Verstärker
   verwendbar.
2. **Wohnort in `/about/` ergänzen** (Option 2 aus Abschnitt 2) — eine Zeile,
   nimmt der Offenlegungsfrage die Grundlage.

**Erledigt am 3. August:** Whois-Kanal geprüft (gibt nichts preis), die vier
Befunde aus `rechtscheck.py` abgearbeitet — der Prüfer meldet erstmals
**0 Fehler** — und die Log-Aufbewahrung in `privacy.html` benannt (Abschnitt 6):
was gespeichert wird, wo und wie lange, mit Quelle und Abrufdatum.
