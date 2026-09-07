/* Prueft, dass bei eingeschalteter Zitation auch etwas danebenliegt.
 *
 * Anlass (18.08.2026), mehrfach gemeldet: Schalter an, im Ordner nur PDFs —
 * keine .txt, keine .ris. Dazu hiess jede Datei "Quickstart_...", obwohl die
 * Seite "Kimi K2.6" heisst.
 *
 * Beides hatte dieselbe Wurzel: quelle blieb null. Der Dateiname faellt dann
 * auf tab.title zurueck (bei nachladenden Seiten der Titel der
 * EINSTIEGSSEITE), und der Beilagen-Block laeuft gar nicht erst an.
 *
 * Drei Absicherungen, die hier festgehalten werden:
 *   1. Die Ersatzangabe steht unmittelbar VOR dem Ablegen, nicht nur im Zweig
 *      der Meta-Auswertung. Bricht die ab, gibt es trotzdem Beilagen.
 *   2. Der Titel kommt aus der Seite (cmd "seitenTitel"), nicht aus dem
 *      Reiter — eine schlanke Abfrage, die auch dann durchkommt, wenn die
 *      grosse Auswertung scheitert.
 *   3. Der RIS-Satz liegt IN der Zitationsdatei. Browser lassen eine
 *      Erweiterung nur begrenzt viele Dateien ohne Rueckfrage ablegen; eine
 *      Beilage weniger heisst ein Download weniger.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

test("Beilagen entstehen, sobald die Zitation eingeschaltet ist", () => {
  const inhalt = readFileSync(join(WURZEL, "content.js"), "utf8");
  p(/case "seitenTitel"/.test(inhalt), "content.js beantwortet die schlanke Titelabfrage");
  p(/^  function ueberschriftTitel\(\)/m.test(inhalt),
    "ueberschriftTitel steht auf der aeusseren Ebene und ist erreichbar");

  for (const [name, datei] of [["firefox", "background.js"],
                               ["chrome", join("chrome-mv3", "background.js")]]) {
    const bg = readFileSync(join(WURZEL, datei), "utf8");

    /* 1. Ersatzangabe unmittelbar vor dem Ablegen. */
    const vorAblage = bg.indexOf("Ersatzangabe vor dem Ablegen gebildet");
    const ablage = bg.indexOf("await belegeAblegen(stamm, quelle, linkKarte");
    p(vorAblage > -1, `${name}: die Ersatzangabe steht vor dem Ablegen`);
    p(vorAblage > -1 && ablage > vorAblage,
      `${name}: sie steht VOR belegeAblegen, nicht danach`);

    /* 2. Der Titel kommt aus der Seite. */
    p(/cmd: "seitenTitel"/.test(bg), `${name}: fragt den Titel bei der Seite ab`);
    const stelle = bg.slice(vorAblage - 900, vorAblage);
    p(/seitenTitel \|\| \(tab\.title/.test(stelle),
      `${name}: Seitentitel hat Vorrang vor dem Reitertitel`);

    /* 3. Der RIS-Satz liegt in der Zitationsdatei UND auf Wunsch daneben.
     *
     * Bis 2.35.17 stand hier "risSidecar: false" als Erwartung — die eigene
     * .ris war abgeschafft, weil sie einen zusaetzlichen Download kostete.
     * Das half aber gerade denen nicht, die sie brauchen: Citavi, Zotero und
     * EndNote lesen keinen Fliesstext. Jetzt gibt es beide Beilagen, jede
     * einzeln abwaehlbar, und beide haengen am Zitationsschalter. */
    p(/ris: risSatz/.test(bg), `${name}: der RIS-Satz wird der Zitationsdatei mitgegeben`);
    p(/risDatei: settings\.sourceMetadata !== false && settings\.risDatei !== false/.test(bg),
      `${name}: die .ris-Datei haengt an Zitationsschalter UND eigener Einstellung`);
    p(/zitatDatei: settings\.sourceMetadata !== false && settings\.zitatDatei !== false/.test(bg),
      `${name}: die .zitate.txt ebenso`);
    p(/if \(z\.risDatei !== false/.test(bg), `${name}: die Ablage liest den .ris-Schalter`);
    p(/if \(z\.zitatDatei !== false/.test(bg), `${name}: die Ablage liest den .txt-Schalter`);

    /* Und die Beilage, die es nicht mehr geben soll.
     *
     * Geprueft wird die ABLAGE, nicht die Zeichenkette: Der Name steht
     * weiterhin im Text, der erklaert, warum es sie nicht mehr gibt. Ein
     * Pruefer, der darauf anschlaegt, verbietet die Erklaerung statt der
     * Sache. */
    p(!/legen\("\.links\.json"/.test(bg), `${name}: keine .links.json mehr neben dem PDF`);

    /* Gegenprobe: Findet die Suche in dieser Datei ueberhaupt etwas? */
    p(/belegeAblegen/.test(bg), `${name}: Gegenprobe — belegeAblegen kommt vor`);

    /* Und die Bedingung selbst: nur noch sourceMetadata. */
    p(/if \(!p\.isAndroid && settings\.sourceMetadata !== false && !quelle\)/.test(bg),
      `${name}: die Ersatzangabe haengt nur am Zitationsschalter`);
  }

  /* Gegenprobe: Wuerde die Pruefung den alten Zustand bemerken? */
  const alt = 'if (!p.isAndroid && quelle) {';
  p(!/Ersatzangabe vor dem Ablegen/.test(alt),
    "Gegenprobe: der alte Zustand wuerde hier durchfallen");

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# Beilagen: ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
