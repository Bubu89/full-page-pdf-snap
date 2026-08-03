# Wo ist dieses Projekt angreifbar?

Stand 3. August 2026, nach vollständiger Durchsicht aller öffentlichen Flächen.
**Keine Rechtsberatung.** Eine Bestandsaufnahme mit konkreten Fundstellen,
sortiert nach Wahrscheinlichkeit mal Schaden. Bei Abmahnung, Klage oder
Unterlassungsaufforderung: Anwalt, nicht dieses Dokument.

Geprüft wurden: 30 ausgelieferte Seiten, 9 Datensätze, der Endpunkt unter
`/mcp`, die Agent-Fähigkeiten, die Store-Texte, das öffentliche Repository, die
DNS-Zone und der Haftungsausschluss.

---

## Zusammenfassung vorweg

Die vier Flächen, die üblicherweise Ärger machen — **unbelegte Behauptungen,
Aussagen über Wettbewerber, Markennutzung und fehlende Formalien** — sind hier
überdurchschnittlich sauber bearbeitet. Was bleibt, ist weniger eine Frage der
Texte als eine des **Betriebs**: Ein Dienst, der auf Zuruf fremde Server abruft,
und eine Pseudonymität, die formal strittig bleibt.

---

## 1. Rang: Der Endpunkt war im Haftungsausschluss nicht erfasst — behoben

**Das Risiko.** Seit heute wird `/mcp` prominent beworben: eigene Seite
`/for-agents/`, ein Werkzeug `how_to_capture`, Einträge in `llms.txt` und in den
Agent-Fähigkeiten. Er liefert Zitationsdaten, die in Abschlussarbeiten und
Einreichungen fließen. Ein falscher Datensatz kann dort zu einer fehlerhaften
Quellenangabe führen — und daran hängen Plagiatsvorwürfe und
Prüfungsentscheidungen.

**Der Befund.** Der Haftungsausschluss war ausgezeichnet gearbeitet, deckte den
Endpunkt aber mit **null** Erwähnungen nicht ab: kein Treffer für *endpoint*,
*MCP* oder *citation record*. Die Software war erfasst, die Messungen waren
erfasst, der Dienst nicht.

**Behoben** mit einem eigenen Abschnitt 6 in beiden Sprachfassungen: keine
Prüfung der Angaben durch den Endpunkt, `complete: false` ist keine
Quellenangabe, jeder Datensatz ist Ausgangspunkt und nie fertige Angabe, keine
Zusage zu Verfügbarkeit oder Fortbestand, Vorrang des Verlags-Exports, und das
ausdrückliche Verbot, den Dienst zur Belastung fremder Server zu verwenden.

---

## 2. Rang: Der offene Abrufdienst

**Das Risiko.** `extract_citation` ruft jede genannte öffentliche Adresse ab.
Der Abruf trägt unser Kennzeichen und kommt von Cloudflare-Adressen. Wer den
Endpunkt in Schleife anspricht, erzeugt Last bei einem Dritten — und im Log des
Dritten steht unser Name. Das ist die realistischste Konstellation, in der
jemand mit einer Forderung an die Tür kommt.

**Was dagegen steht:** Weiterleitungen werden seit Worker 1.11.0 einzeln geprüft
und auf fünf Sprünge begrenzt; private Adressbereiche sind gesperrt; die Zusage
„kein Limit" ist von vier Seiten entfernt; das Kennzeichen ist eindeutig und
erlaubt jedem Betreiber, uns auszusperren; seit heute steht das Verbot im
Haftungsausschluss.

**Was fehlt:** Eine echte Ratenbegrenzung. Über die API auf dem Gratis-Tarif
nicht erreichbar — geprüft, ein eigens erzeugter Token mit *Firewall Services:
Write* bekam weiterhin *Authentication error*. **Die eine kostenlose Regel muss
im Dashboard gesetzt werden**, Anleitung in
`store-texte/ANLEITUNG_NAECHSTE_SCHRITTE.md`, Schritt 6.

Solange das offen ist, ist dies der Punkt mit dem größten Restrisiko.

---

## 3. Rang: Offenlegung unter Pseudonym (§ 25 MedienG)

**Der Stand.** `/about/` legt das Pseudonym *Silence* offen, nennt eine
Kontaktadresse und sagt zu, Identität und Anschrift einem berechtigten
Anfragenden unverzüglich offenzulegen. Klarname, Anschrift und Telefon stehen
nirgends. Der Whois-Kanal gibt nichts preis — RDAP liefert nur den Registrar.

**Das Risiko.** Ob ein Pseudonym mit Offenlegung *auf Anfrage* § 25 MedienG
genügt, ist strittig. § 5 ECG greift nach hiesiger Einschätzung nicht, weil die
Nicht-Kommerzialität strukturell belegt ist. Die Praxis verfolgt so etwas bei
privaten Seiten selten — aber „selten" ist kein Rechtsgrund.

**Billigste Abhilfe:** Wohnort ohne Straße in `/about/` („Salzburg,
Österreich"). Eine Zeile, nimmt der Diskussion die Grundlage.

---

## 4. Rang: Der direkte Leistungsvergleich mit Citoid

**Das Risiko.** `/measurements/citation-extraction/` stellt dem eigenen Dienst
**Citoid** gegenüber — den Zitationsdienst der Wikimedia Foundation — und nennt
Zahlen: *100 % Genauigkeit gegen 79 %*, *2 Fehlreferenzen aus Sperrseiten gegen
0*. Das ist eine Tatsachenbehauptung über einen fremden Dienst und damit
beweispflichtig.

**Warum das trotzdem trägt.** § 2a UWG erlaubt vergleichende Werbung, wenn sie
objektiv nachprüfbare, wesentliche Eigenschaften vergleicht und nicht
herabsetzt. Hier: gleiche 18 Adressen in gleicher Reihenfolge, Rohdaten
veröffentlicht, Methode angegeben, keine Charaktereigenschaften, kein wertendes
Adjektiv. Und der Artikel legt die **eigene frühere Fehlmessung offen** („The
earlier measurement was wrong, and how") — genau das, was Objektivität belegt.

**Was ich trotzdem beobachten würde:** Wikimedia ist eine Stiftung mit
Rechtsabteilung. Sollte je eine Beschwerde kommen, ist die tragfähige Antwort
die Messung selbst — nicht eine Umformulierung. Die Rohdaten müssen deshalb
abrufbar bleiben.

---

## 5. Rang: Die Wettbewerber-Tabelle

`/measurements/pdf-extension-permissions/` führt acht fremde Erweiterungen
namentlich mit Nutzerzahl, deklarierten Hosts und Datum der letzten
Aktualisierung — *PDF Mage* mit `<all_urls>` und Stand 2021, *PDFmyURL* mit
Stand 2019, *FireShot* mit 169.961 Nutzern.

**Bewertung: geringes Risiko.** Alle Angaben stammen aus der öffentlichen
Mozilla-Schnittstelle mit Abrufdatum. Nirgends steht, was eine Erweiterung
*tut* — nur, was sie *deklariert*. Die Überschrift ist eine Frage („Does your
PDF extension upload the page?"), keine Behauptung. Kein Decompiling, keine
Absichtsaussage. Genau die Form, die im Streitfall hält.

---

## 6. Markennennungen

**Zotero, Citavi, EndNote, Mendeley** erscheinen als Kompatibilitätsangabe
(„ein RIS-Satz, den Zotero und Citavi einlesen"). Das ist nominative Nutzung
nach § 10 Abs 3 Z 3 MSchG — zulässig, weil zur Angabe der Bestimmung
erforderlich. Geprüft: keine Fremdmarke im Produktnamen, keine Logos, keine
markenähnliche Gestaltung, keine behauptete Partnerschaft.

**Chrome, Firefox, Edge** werden zur Bezeichnung der Browser verwendet. Mozillas
Markenregel („[Name] for Firefox") ist nicht berührt, weil kein Markenname im
Titel steht.

---

## 7. Was gerade *kein* Problem ist, obwohl es so wirken könnte

- **Die Agent-Anleitungen.** Jede Erwähnung von Paywall oder Umgehung ist eine
  **Abgrenzung**: „not a route past a paywall", „Do not imitate a browser user
  agent". `rechtscheck.py` erzwingt das seit heute maschinell.
- **Die Verweise auf `chrome-use`, `openchrome`, `xdotool`.** Jeder trägt „not
  endorsements, not audited here".
- **Die Erweiterung selbst.** Sie führt `activeTab` und keine Host-Rechte,
  arbeitet lokal, überträgt nichts. Eine Kopie zum eigenen Gebrauch nach
  § 42 UrhG. Sie umgeht keine technische Schutzmaßnahme — gemessen ist sogar,
  dass sie sich nicht einmal von Software auslösen lässt.
- **Aussagen über Verlage.** „The server answered 403 Forbidden" ist eine
  Beobachtung. Der Artikel sagt ausdrücklich, dass vier der Ablehnungen Sperren
  gegen **Rechenzentrums-Adressen** sind, also nichts über den Anbieter
  aussagen. Und: „measured on one afternoon and liable to change".

---

## 8. Offene Punkte, nach Dringlichkeit

1. **Ratenbegrenzung** im Cloudflare-Dashboard setzen (Schritt 6 der Anleitung).
   Der einzige Punkt mit nennenswertem Restrisiko.
2. **Log-Aufbewahrung** benennen. `observability = true` ohne festgelegte Dauer;
   die abgefragten Adressen sind der einzige personenbeziehbare Datenpunkt, den
   der Endpunkt erzeugt, und eine abgefragte Adresse verrät, woran jemand
   arbeitet. Gehört in `privacy.html` oder wird ausdrücklich kurz gesetzt.
3. **Wohnort in `/about/`** ergänzen.
4. **`cool-frog-b57a` löschen** — kein Rechts-, aber ein Sicherheitsrisiko: kein
   Ablauf, kann sich selbst beliebige Rechte geben.

## 9. Was diese Prüfung nicht leistet

Sie bewertet nach österreichischem Recht mit Blick auf Deutschland und die
Store-Regeln. Sie sagt nichts darüber, wie ein Gericht entscheiden würde,
insbesondere nicht zu § 25 MedienG. Sie ersetzt keine anwaltliche Prüfung, und
sie kann Ansprüche aus Rechtsordnungen, die hier nicht betrachtet wurden, weder
ausschließen noch beziffern.
