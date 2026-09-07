/* Alle Druckkombinationen und die Zitation im PDF.
 *
 * Anlass (18.08.2026): "sind druckformate mit allen raendern und einstellung
 * nun geprueft und die zitation im pdf". Berechtigt gefragt — bis dahin waren
 * einzelne Faelle geprueft, nicht die Matrix.
 *
 * Beim Aufsetzen dieser Pruefung zeigte sich, wie leicht man sich selbst in
 * die Irre fuehrt: Ein erster Durchlauf meldete zwei Fehler bei Letter mit
 * Rand. Nachgerechnet lag es nicht am Code, sondern am Pruefskript — es
 * bildete das Seitenverhaeltnis aus Millimetern, waehrend der Code in Punkten
 * rechnet. Zweimal runden, zwei Punkt Unterschied. Deshalb steht die Rechnung
 * hier in derselben Einheit wie dort.
 */
import { test } from "node:test";
import { readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import vm from "node:vm";

const WURZEL = join(dirname(fileURLToPath(import.meta.url)), "..");
let fehler = 0;
const p = (b, t) => { if (b) console.log("#   ok   " + t); else { console.log("# FEHL " + t); fehler++; } };

const ctx = { console, Math, JSON, Date, Uint8Array, Array, String, Number, Object,
              isFinite, parseInt, parseFloat };
ctx.globalThis = ctx; ctx.window = ctx;
vm.createContext(ctx);
vm.runInContext(readFileSync(join(WURZEL, "pdf-writer.js"), "utf8"), ctx);

const bg = readFileSync(join(WURZEL, "background.js"), "utf8");
function funktion(name) {
  const v = bg.indexOf(`function ${name}(`);
  const r = bg.slice(v);
  const m = r.match(/\n\}\n/);
  return r.slice(0, m.index + m[0].length);
}
vm.runInContext(funktion("druckMasse") + "\nglobalThis.dm = druckMasse;", ctx);

const JPEG = new Uint8Array([0xFF,0xD8,0xFF,0xE0,0,16,74,70,73,70,0,1,1,0,0,1,0,1,0,0,0xFF,0xD9]);

test("Alle Druckformate mit allen Raendern", () => {
  for (const papier of ["a4", "letter"]) {
    for (const quer of ["hoch", "quer"]) {
      for (const randMm of [0, 5, 10, 15]) {
        const masse = ctx.dm({ druckPapier: papier, druckQuer: quer });
        const blatt = { breite: Math.round(masse.breiteZoll * 72),
                        hoehe: Math.round(masse.hoeheZoll * 72) };
        const randPt = randMm * 72 / 25.4;

        // Dasselbe Verhaeltnis wie im Code — in PUNKTEN.
        const kurzPt = (papier === "letter" ? 612 : 595) - 2 * randPt;
        const langPt = (papier === "letter" ? 792 : 842) - 2 * randPt;
        const verh = quer === "quer" ? kurzPt / langPt : langPt / kurzPt;
        const pxW = 832, hPx = Math.round(pxW * verh);

        const bytes = ctx.PageShotPdf.buildPdf(
          [{ bytes: JPEG, widthPx: pxW, heightPx: hPx, yPx: 0 }],
          { dpi: 144, title: "T", version: "t", blattPt: blatt, randPt });
        const t = Buffer.from(bytes).toString("latin1");
        const c = [...t.matchAll(/q\n(-?[\d.]+) 0 0 (-?[\d.]+) (-?[\d.]+) (-?[\d.]+) cm/g)][0];
        const [bw, bh, x, y] = [c[1], c[2], c[3], c[4]].map(Number);
        const rest = { oben: blatt.hoehe - bh - y, unten: y,
                       links: x, rechts: blatt.breite - bw - x };

        const name = `${papier} ${quer} ${randMm}mm`;
        p(Object.values(rest).every(v => Math.abs(v - randPt) < 1.6),
          `${name}: Rest o/u/l/r ${rest.oben.toFixed(0)}/${rest.unten.toFixed(0)}/` +
          `${rest.links.toFixed(0)}/${rest.rechts.toFixed(0)} pt (Rand ${randPt.toFixed(0)})`);

        // Das Blatt traegt die Masse des gewaehlten Papiers.
        const sollBreiteMm = quer === "quer" ? (papier === "letter" ? 279 : 297)
                                             : (papier === "letter" ? 216 : 210);
        p(Math.abs(blatt.breite / 72 * 25.4 - sollBreiteMm) < 1,
          `${name}: Blattbreite ${(blatt.breite / 72 * 25.4).toFixed(0)} mm`);
      }
    }
  }
  console.log(fehler === 0 ? "# 16 Kombinationen geprueft" : `# ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});

test("Die Zitation steckt im PDF selbst", () => {
  const quelle = {
    art: "Zeitschriftenaufsatz", autoren: ["Müller, Klaus", "Anna Schmidt"],
    titel: "Digitale Belegführung", jahr: "2024", journal: "Zeitschrift für X",
    band: "66", heft: "3", seiteVon: "211", seiteBis: "229",
    doi: "10.1007/s11576-024-01234-5", issn: "1861-8936", verlag: "Springer",
    url: "https://example.org/a", urlZitat: "https://example.org/a",
    abrufzeit: "2026-08-18T10:00:00+02:00", abrufdatum: "2026-08-18",
    lizenz: "CC BY 4.0", herkunft: "citation_*", vollstaendig: true,
  };
  const bytes = ctx.PageShotPdf.buildPdf(
    [{ bytes: JPEG, widthPx: 832, heightPx: 1178, yPx: 0 }],
    { dpi: 144, title: "T", version: "t", source: quelle,
      provenance: { url: quelle.url, capturedAt: new Date("2026-08-18T10:00:00Z"),
                    sha256: "abc123" } });
  const t = Buffer.from(bytes).toString("latin1");

  /* Das ist der Grund, warum die Erweiterung ohne Datei daneben auskommt:
   * Alles, was eine Zitation braucht, steht in der Datei selbst. */
  p(/\/Type \/EmbeddedFile/.test(t) && /research-info-systems/.test(t),
    "RIS-Satz als Anlage");
  p(/quelle\.ris/.test(t), "Anlage heisst quelle.ris");
  p(/TY  - JOUR/.test(t), "RIS: Zeitschriftenaufsatz");
  p(/DO  - 10\.1007/.test(t), "RIS: DOI");
  /* Im RIS-Format hat ein Datum die Form JJJJ/MM/TT/Freitext — nicht ISO.
   * Citavi und EndNote lesen die ISO-Form nicht. */
  p(/Y2  - 2026\/08\/18\//.test(t), "RIS: Abrufdatum im RIS-Format");
  p(!/Y2  - 2026-08-18T/.test(t), "RIS: kein ISO-Zeitstempel mehr im Datumsfeld");
  p(/<x:xmpmeta/.test(t), "XMP-Datensatz");
  p(/dc:title/.test(t) && /dc:creator/.test(t), "XMP: Titel und Verfasser");
  p(/\/DOI/.test(t), "DOI als eigenes Dokumentfeld");
  p(/\/Journal/.test(t), "Zeitschrift als eigenes Dokumentfeld");
  p(/\/SourceURL/.test(t), "Quelladresse als eigenes Dokumentfeld");

  console.log(fehler === 0 ? "# alle Pruefungen bestanden" : `# ${fehler} Fehler`);
  if (fehler) throw new Error(`${fehler} Pruefungen fehlgeschlagen`);
});
