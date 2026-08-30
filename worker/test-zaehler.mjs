/* Prueft die Werkzeugzaehlung ohne Cloudflare.
 *
 * Der Zaehler laeuft im Worker und laesst sich dort nicht beobachten, ohne ihn
 * vorher zu deployen. Ein Deploy als erster Test waere die falsche Reihenfolge:
 * ein Fehler im Zaehler wuerde dann live auffallen. Hier wird der KV-Speicher
 * nachgebildet und die Logik dagegen gefahren.
 *
 *   node worker/test-zaehler.mjs
 */
import { readFileSync } from "node:fs";

const quelle = readFileSync(new URL("./mcp.js", import.meta.url), "utf8");

// Die Zaehlerfunktionen aus der Worker-Datei herausloesen und einzeln
// ausfuehrbar machen — sie haengen nur an WERKZEUGNAMEN.
const teile = [];
for (const name of ["const ZAEHLER_TAGE", "const SPUEL_MS", "const SPUEL_STUECK",
                    "let offen", "let offenAnzahl", "let zuletztGespuelt",
                    "function tagSchluessel", "async function spuelenIntern", "let spuelLauf", "function spuelen",
                    "function zuruecksetzen", "function vormerken", "function werkzeugZaehlen",
                    "function klientName", "function klientZaehlen",
                    "async function tageLesen", "async function zaehlerLesen"]) {
  const von = quelle.indexOf(name);
  if (von < 0) throw new Error(`nicht gefunden: ${name}`);
  // Bis zur naechsten Leerzeile gefolgt von einem Zeilenanfang ohne Einrueckung
  const rest = quelle.slice(von);
  const bis = rest.search(/\n(?=(const |let |function |async function |\/\* ))/);
  teile.push(rest.slice(0, bis > 0 ? bis : rest.length));
}
const WERKZEUGNAMEN_QUELLE =
  quelle.match(/const WERKZEUGNAMEN\s*=\s*new Set\(\[[\s\S]*?\]\);?/);
if (!WERKZEUGNAMEN_QUELLE) throw new Error("WERKZEUGNAMEN nicht gefunden");

const modul = await import("data:text/javascript," + encodeURIComponent(
  WERKZEUGNAMEN_QUELLE[0] + "\n" + teile.join("\n") +
  "\nexport { werkzeugZaehlen, klientZaehlen, zaehlerLesen, spuelen, "
  + "tagSchluessel, WERKZEUGNAMEN, zuruecksetzen };"));

// --- KV-Attrappe -----------------------------------------------------------
function kvAttrappe() {
  const daten = new Map();
  return {
    daten,
    async get(k) { return daten.has(k) ? daten.get(k) : null; },
    schreibvorgaenge: 0,
    async put(k, v) { this.schreibvorgaenge++; daten.set(k, v); },
    async list({ prefix = "", cursor } = {}) {
      const keys = [...daten.keys()].filter((k) => k.startsWith(prefix))
        .map((name) => ({ name }));
      return { keys, list_complete: true, cursor: null };
    },
  };
}

let fehler = 0;
function pruefe(name, ist, soll) {
  const ok = JSON.stringify(ist) === JSON.stringify(soll);
  console.log(`  ${ok ? "OK  " : "FEHL"}  ${name}`);
  if (!ok) {
    console.log(`          erwartet: ${JSON.stringify(soll)}`);
    console.log(`          bekommen: ${JSON.stringify(ist)}`);
    fehler++;
  }
}

const heute = new Date().toISOString().slice(0, 10);

console.log("=== A. Zaehlen ===");
{
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  for (let i = 0; i < 3; i++) modul.werkzeugZaehlen(env, "install_extension");
  modul.werkzeugZaehlen(env, "list_measurements");
  await modul.spuelen(env);
  const stand = JSON.parse(await ZAEHLER.get(`t:${heute}`));
  pruefe("dreimal aufgerufen -> Stand 3", stand.w.install_extension, 3);
  pruefe("zweites Werkzeug getrennt", stand.w.list_measurements, 1);
}

console.log("\n=== B. Nur echte Werkzeugnamen ===");
{
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  // Ein Aufrufer kann jeden Namen schicken. Ohne Filter waere der Speicher
  // von aussen mit beliebigen Schluesseln befuellbar.
  modul.werkzeugZaehlen(env, "gibt_es_nicht");
  modul.werkzeugZaehlen(env, "../../etc/passwd");
  await modul.spuelen(env);
  pruefe("erfundene Namen werden nicht gespeichert", ZAEHLER.daten.size, 0);
  modul.werkzeugZaehlen(env, "install_extension");
  await modul.spuelen(env);
  const stand = JSON.parse(await ZAEHLER.get(`t:${heute}`));
  pruefe("echter Name wird gespeichert", Object.keys(stand.w), ["install_extension"]);
}

console.log("\n=== C. Ohne Bindung kein Absturz ===");
{
  let geworfen = false;
  try {
    modul.werkzeugZaehlen(undefined, "install_extension");
    modul.werkzeugZaehlen({}, "install_extension");
    await modul.spuelen({});
  } catch (e) { geworfen = true; }
  pruefe("fehlende KV-Bindung wirft nicht", geworfen, false);
  pruefe("Lesen ohne Bindung gibt null", await modul.zaehlerLesen({}), null);
}

console.log("\n=== D. Auslesen und Summieren ===");
{
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  for (let i = 0; i < 5; i++) modul.werkzeugZaehlen(env, "install_extension");
  for (let i = 0; i < 2; i++) modul.werkzeugZaehlen(env, "get_method");
  await modul.spuelen(env);
  // Ein alter Eintrag ausserhalb des Fensters darf nicht mitzaehlen.
  await ZAEHLER.put("t:2020-01-01", JSON.stringify({ w: { install_extension: 999 } }));
  const d = await modul.zaehlerLesen(env, 30);
  pruefe("Summe ohne den alten Eintrag", d.gesamt, 7);
  pruefe("nach Haeufigkeit sortiert", Object.keys(d.jeWerkzeug),
         ["install_extension", "get_method"]);
  pruefe("Installationsaufrufe getrennt ausgewiesen",
         d.jeWerkzeug.install_extension, 5);
  pruefe("fruehester Tag im Fenster", d.seit, heute);
}

console.log("\n=== E. Alte Schluesselform wird weitergelesen ===");
{
  // Die Form w:WERKZEUG:TAG lief bis 30.08.2026 und laeuft erst nach 90
  // Tagen aus. Ein Bruch in der Zeitreihe waere schlimmer als die doppelte
  // Leseschleife.
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  await ZAEHLER.put(`w:install_extension:${heute}`, "40");
  modul.werkzeugZaehlen(env, "install_extension");
  modul.werkzeugZaehlen(env, "install_extension");
  await modul.spuelen(env);
  const d = await modul.zaehlerLesen(env, 30);
  pruefe("alte und neue Form addiert", d.jeWerkzeug.install_extension, 42);
}

console.log("\n=== F. Buendelung senkt die Schreiblast ===");
{
  // Der Anlass der Aenderung: 650 Schreibvorgaenge am Tag bei 1.000 im
  // kostenlosen Kontingent. Vorher war jedes Ereignis ein Schreibvorgang.
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  for (let i = 0; i < 60; i++) modul.werkzeugZaehlen(env, "install_extension");
  for (let i = 0; i < 60; i++) modul.klientZaehlen(env, "irgendein-client");
  pruefe("120 Ereignisse, noch nichts geschrieben", ZAEHLER.schreibvorgaenge, 0);
  await modul.spuelen(env);
  // Wie viele es genau werden, haengt daran, wann die Schwelle greift und
  // wann der angereihte Lauf drankommt — ein oder zwei. Festgehalten wird
  // deshalb die Aussage, um die es geht: sehr wenige statt einer je Ereignis.
  pruefe("120 Ereignisse -> hoechstens zwei Schreibvorgaenge statt 120",
         ZAEHLER.schreibvorgaenge <= 2 && ZAEHLER.schreibvorgaenge >= 1, true);
  const stand = JSON.parse(await ZAEHLER.get(`t:${heute}`));
  pruefe("keine Zaehlung verloren",
         [stand.w.install_extension, stand.c["irgendein-client"]], [60, 60]);
}

console.log("\n=== G. Menge loest von selbst aus ===");
{
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  // SPUEL_STUECK ist 100 — der hundertste Aufruf schreibt ohne Zutun.
  for (let i = 0; i < 99; i++) modul.werkzeugZaehlen(env, "install_extension");
  pruefe("99 Ereignisse: noch nichts geschrieben", ZAEHLER.schreibvorgaenge, 0);
  modul.werkzeugZaehlen(env, "install_extension");
  await new Promise((r) => setTimeout(r, 20));
  pruefe("der hundertste loest aus", ZAEHLER.schreibvorgaenge, 1);
}

console.log("\n=== I. Frische Instanz schreibt nicht sofort ===");
{
  // Der Fall, der im Betrieb auftrat und im Test fehlte: Eine neue Instanz
  // hat noch nie gespuelt. Stand die Uhr dabei auf null, galt das Fenster
  // sofort als abgelaufen und das erste Ereignis schrieb — bei laufend neu
  // erzeugten Instanzen also fast jedes.
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  // Geprueft am gebuendelten Pfad — adoption_stats und die Sitzungen. Die
  // inhaltlichen Werkzeuge schreiben absichtlich sofort (Fall J).
  modul.zuruecksetzen();               // Instanz wie frisch gestartet
  modul.werkzeugZaehlen(env, "adoption_stats");
  await new Promise((r) => setTimeout(r, 20));
  pruefe("erstes Ereignis einer frischen Instanz schreibt nicht",
         ZAEHLER.schreibvorgaenge, 0);
  await modul.spuelen(env);
  pruefe("beim ausdruecklichen Spuelen kommt es an",
         JSON.parse(await ZAEHLER.get(`t:${heute}`)).w.adoption_stats, 1);
}

console.log("\n=== J. Inhaltliche Werkzeuge gehen nicht verloren ===");
{
  // Der Fall, der im Betrieb auftrat: Drei Aufrufe von get_method wurden
  // vorgemerkt und nie geschrieben, weil die Instanz vor Ablauf des Fensters
  // endete. Fuer die seltenen inhaltlichen Werkzeuge ist Verlaesslichkeit
  // wichtiger als eingesparte Schreibvorgaenge.
  const ZAEHLER = kvAttrappe();
  const env = { ZAEHLER };
  modul.zuruecksetzen();
  modul.werkzeugZaehlen(env, "get_method");
  await new Promise((r) => setTimeout(r, 30));
  pruefe("get_method steht sofort im Speicher",
         JSON.parse(await ZAEHLER.get(`t:${heute}`) || "{}").w?.get_method, 1);

  // adoption_stats bleibt gebuendelt — es allein riss das Kontingent.
  modul.zuruecksetzen();
  const vorher = ZAEHLER.schreibvorgaenge;
  for (let i = 0; i < 20; i++) modul.werkzeugZaehlen(env, "adoption_stats");
  await new Promise((r) => setTimeout(r, 30));
  pruefe("20x adoption_stats schreibt nicht sofort",
         ZAEHLER.schreibvorgaenge, vorher);
}

console.log("\n=== H. Schreibfehler bleibt folgenlos ===");
{
  const kaputt = { get: async () => { throw new Error("KV weg"); },
                   put: async () => { throw new Error("KV weg"); },
                   list: async () => { throw new Error("KV weg"); } };
  let geworfen = false;
  try {
    modul.werkzeugZaehlen({ ZAEHLER: kaputt }, "install_extension");
    await modul.spuelen({ ZAEHLER: kaputt });
  } catch (e) { geworfen = true; }
  pruefe("Schreibfehler wirft nicht in den Werkzeugaufruf", geworfen, false);
  pruefe("Lesefehler gibt null statt Muell",
         await modul.zaehlerLesen({ ZAEHLER: kaputt }), null);
}

console.log("\n" + "=".repeat(58));
if (fehler) { console.log(`${fehler} FEHLER`); process.exit(1); }
console.log("Zaehlung arbeitet richtig.");
