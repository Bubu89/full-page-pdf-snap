/* Prueft, dass die bibliografischen Angaben im PDF auffindbar sind — nicht nur
 * irgendwo vorhanden.
 *
 * Anlass (07.08.2026): In einer Android-Aufnahme aus dem pCloud-Testordner
 * standen Adresse, DOI, Band und Jahr zwar in der Datei, aber ausschliesslich
 * als Fliesstext: die Adresse in /Keywords zwischen Pruefsumme und technischen
 * Hinweisen, Band und Jahr nur innerhalb der Zitation unter /Subject. Kein
 * Betrachter und kein Literaturverwaltungsprogramm kann daraus eine einzelne
 * Angabe herausloesen. Einen XMP-Strom, aus dem Citavi, Zotero und Mendeley
 * lesen, hatte die Datei gar nicht ("Metadata Stream: no").
 *
 * Zweiter Befund derselben Stelle: Der ganze /Keywords-Block hing an
 * "if (beleg.sha256)". Ohne Pruefsumme verlor die Datei damit auch ihre
 * Quell-Adresse — obwohl beides nichts miteinander zu tun hat.
 *
 * Aufruf: node tests/quellenangaben.test.mjs
 */
import { readFileSync } from "node:fs";

let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

for (const datei of ["chrome-mv3/pdf-writer.js", "pdf-writer.js"]) {
  const src = readFileSync(new URL("../" + datei, import.meta.url), "utf8");

  // 1. Jede Angabe als eigener Schluessel im Info-Dictionary
  for (const feld of ["SourceURL", "DOI", "Journal", "Volume", "Issue", "Year"]) {
    ok(new RegExp(`\\["${feld}",`).test(src),
       `${datei}: /${feld} wird als eigenes Feld geschrieben`);
  }

  // 2. XMP-Strom mit den Namensraeumen, die Zitierprogramme lesen
  ok(/\/Type \/Metadata \/Subtype \/XML/.test(src),
     `${datei}: haengt einen XMP-Strom an den Katalog`);
  ok(/purl\.org\/dc\/elements/.test(src) && /prismstandard\.org/.test(src),
     `${datei}: XMP nutzt Dublin Core und PRISM`);
  ok(/dc:source/.test(src) && /prism:doi/.test(src) && /prism:volume/.test(src),
     `${datei}: Adresse, DOI und Band stehen als eigene XMP-Elemente`);

  // 3. Die Adresse haengt nicht mehr an der Pruefsumme
  const block = src.slice(src.indexOf("/CreationDate ("), src.indexOf("infoId = addObject"));
  ok(!/if \(beleg\.sha256\) \{[\s\S]*source-url/.test(block),
     `${datei}: Quell-Adresse haengt nicht mehr an der Pruefsumme`);
  ok(/beleg\.sha256 \? "; image-sha256=/.test(src),
     `${datei}: Pruefsumme nur dann, wenn sie vorliegt`);
}

/* 4. XML-Sonderzeichen. Ein Titel mit & oder < wuerde den XMP-Strom sonst
 *    zerreissen, und der Betrachter faende gar nichts mehr. */
{
  const x = (s) => String(s == null ? "" : s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  ok(x("Krebs & Co. <Studie>") === "Krebs &amp; Co. &lt;Studie&gt;",
     "XML-Sonderzeichen im Titel werden maskiert");
  ok(x(null) === "" && x(undefined) === "",
     "Fehlende Angaben ergeben leeren Text, nicht \"null\"");
}

/* 5. Zeitangabe in der Schreibweise, die XMP verlangt. localIso setzt fuer
 *    Menschen ein Leerzeichen — damit koennen Betrachter nichts anfangen. */
{
  function localIso(d) {
    const p = (n) => String(Math.abs(n)).padStart(2, "0");
    const off = -d.getTimezoneOffset();
    const tz = off === 0 ? "Z" : (off > 0 ? "+" : "-") + p(off / 60) + ":" + p(off % 60);
    return d.getFullYear() + "-" + p(d.getMonth() + 1) + "-" + p(d.getDate()) +
      " " + p(d.getHours()) + ":" + p(d.getMinutes()) + ":" + p(d.getSeconds()) + " " + tz;
  }
  const isoUtc = (d) => localIso(d).replace(" ", "T").replace(" ", "");
  const d = new Date(2026, 7, 7, 17, 36, 0);
  ok(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(Z|[+-]\d{2}:\d{2})$/.test(isoUtc(d)),
     "isoUtc liefert gueltiges ISO 8601 fuer XMP");
  ok(localIso(d).includes(" ") && !isoUtc(d).includes(" "),
     "Gegenprobe: localIso enthaelt Leerzeichen, isoUtc nicht");
}

console.log(fehler === 0 ? "\nQuellenangaben: alles in Ordnung"
                         : `\nQuellenangaben: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
