/* Verfolgt die Angabe "welche Ausgabeart" vom Knopf bis zur Aufnahme.
 *
 * Anlass (18.08.2026): Drei Meldungen nacheinander — "Aufnahme fuer Druck"
 * erzeugt weiter eine Endlosbahn, Querformat aendert nichts, der
 * Artikel-Knopf "macht nur normales pdf". Drei Symptome, eine Ursache: In
 * runOnActiveTab stand
 *
 *     await captureFullPage(tab, { region: gewaehlterBereich });
 *
 * Der Modus wurde entgegengenommen und nicht weitergereicht. Damit lief JEDER
 * Knopf in dieselbe gewoehnliche Aufnahme.
 *
 * Warum kein Test das fand: Jedes Teilstueck war geprueft — die Blattrechnung
 * mit vier Formaten, der Vektorweg an einer echten Seite, die Artikelerkennung
 * mit 15.578 Zeichen. Nur die KETTE hatte niemand nachverfolgt. Ein Glied, das
 * nichts weitergibt, ist an keinem seiner Enden zu sehen.
 *
 * Geprueft wird deshalb die Weitergabe selbst, Station fuer Station.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const HIER = dirname(fileURLToPath(import.meta.url));
const WURZEL = join(HIER, "..");

let fehler = 0;
const pruefe = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

test("Der Modus kommt vom Knopf bis zur Aufnahme durch", () => {
  const popup = readFileSync(join(WURZEL, "popup.js"), "utf8");

  // Station 1: Der Knopf schickt einen Modus mit.
  pruefe(/aufnehmen\("a4"/.test(popup), "popup.js: Druck-Knopf sendet den Modus \"a4\"");
  pruefe(/aufnehmen\("artikel"/.test(popup), "popup.js: Artikel-Knopf sendet den Modus \"artikel\"");
  pruefe(/modus:\s*modus\s*\|\|\s*null/.test(popup),
         "popup.js: der Modus steht in der Nachricht");

  for (const [name, datei] of [["firefox", "background.js"],
                               ["chrome", join("chrome-mv3", "background.js")]]) {
    const bg = readFileSync(join(WURZEL, datei), "utf8");

    // Station 2: Der Empfaenger liest ihn aus der Nachricht.
    pruefe(/runOnActiveTab\(\{[^}]*modus:\s*msg\.modus/.test(bg),
           `${name}: die Nachricht wird mit Modus an runOnActiveTab gegeben`);

    /* Station 3 — hier war der Bruch.
     *
     * captureFullPage muss den Modus BEKOMMEN. Ein Aufruf, der nur die
     * Bereichsangabe weitergibt, laesst jeden Knopf dasselbe tun. */
    const aufruf = bg.match(/captureFullPage\(tab,\s*\{[\s\S]{0,220}?\}\)/);
    pruefe(!!aufruf, `${name}: der Aufruf von captureFullPage ist auffindbar`);
    pruefe(!!aufruf && /modus/.test(aufruf[0]),
           `${name}: captureFullPage bekommt den Modus (nicht nur region)`);

    // Station 4: Dort wird er ausgewertet.
    pruefe(/wahl\.modus === "a4"/.test(bg), `${name}: "a4" wird ausgewertet`);
    pruefe(/wahl\.modus === "artikel"/.test(bg), `${name}: "artikel" wird ausgewertet`);

    // Station 5: "a4" stellt tatsaechlich auf mehrere Seiten um.
    const a4 = bg.slice(bg.indexOf('wahl.modus === "a4"'));
    pruefe(/singlePagePdf\s*=\s*false/.test(a4.slice(0, 900)),
           `${name}: "a4" schaltet die fortlaufende Seite ab`);
    pruefe(/pageVerhaeltnis/.test(a4.slice(0, 2600)),
           `${name}: Papierformat wirkt ueber das Seitenverhaeltnis`);
  }

  /* Gegenprobe: Wuerde die Pruefung den alten Zustand bemerken?
   * Ohne sie waere nicht zu unterscheiden, ob der Modus wirklich ankommt
   * oder ob nur das Suchmuster zu nachsichtig ist. */
  const alterAufruf = "await captureFullPage(tab, { region: gewaehlterBereich });";
  pruefe(!/modus/.test(alterAufruf),
         "Gegenprobe: der alte Aufruf wuerde hier durchfallen");

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Modus-Kette: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});

test("Der Artikel-Knopf erscheint nur, wo er traegt", () => {
  const popup = readFileSync(join(WURZEL, "popup.js"), "utf8");
  const html = readFileSync(join(WURZEL, "popup.html"), "utf8");
  let f = 0;
  const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); f++; } };

  /* Der Artikel-Weg setzt die Seite als Lesedokument und braucht dafuer
   * Chromiums Druckschnittstelle. In Firefox liesse sich zwar eine
   * Leseansicht aufnehmen, aber als BILD statt als Text — dieselbe
   * Schaltflaeche haette dort also eine andere Bedeutung. Eine Funktion, die
   * je nach Browser etwas anderes liefert, ist schlechter als eine, die es
   * nur dort gibt, wo sie haelt was sie verspricht. */
  p(/id="zeileArtikel"/.test(html), "die Artikel-Zeile ist benannt und damit entfernbar");
  p(/browser\.debugger/.test(popup) && /zeileArtikel/.test(popup),
    "popup.js entfernt sie, wenn das DevTools-Protokoll fehlt");
  p(/fachArtikel/.test(popup), "das zugehoerige Fach wird mitentfernt");

  /* Entschieden wird anhand dessen, was der Browser KANN, nicht anhand
   * seines Namens: Kennungen lassen sich faelschen und aendern sich, eine
   * fehlende Schnittstelle nicht. */
  const stelle = popup.slice(popup.indexOf("artikelNurWoErTraegt"),
                             popup.indexOf("artikelNurWoErTraegt") + 700);
  p(!/userAgent|navigator\.|Firefox|Gecko/.test(stelle),
    "die Entscheidung faellt ueber die Faehigkeit, nicht ueber die Browserkennung");

  console.log(f === 0 ? "# alle Pruefungen bestanden" : `# Artikel-Knopf: ${f} Fehler`);
  if (f) throw new Error(`${f} Pruefungen fehlgeschlagen`);
});
