/* Prueft die Abhaengigkeit der drei Felder fuer die Seitenaufteilung.
 *
 * Anlass (07.08.2026): Die Felder standen unabhaengig nebeneinander. Wer
 * "Eine fortlaufende Seite" gewaehlt hatte, konnte darunter eine Seitengroesse
 * und eine Pixelhoehe einstellen, die nichts bewirkten. Und wer auf "Mehrere
 * Seiten (zum Drucken)" wechselte, musste das Druckformat in einem zweiten
 * Feld nachziehen - obwohl der Zweck im Namen der Auswahl steht.
 *
 * Aufruf: node tests/seitenformat.test.mjs
 */
let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

// Die Logik aus options.js, nachgestellt
function oberflaeche(start = {}) {
  const feld = {
    singlePagePdf: start.singlePagePdf ?? "true",
    pageFormat: start.pageFormat ?? "a4",
    pageHeightPx: start.pageHeightPx ?? "2400",
  };
  const aus = { pageFormat: false, pageHeightPx: false };
  let vomNutzer = feld.pageFormat === "free";

  function aktualisieren() {
    const mehrseitig = feld.singlePagePdf === "false";
    aus.pageFormat = !mehrseitig;
    aus.pageHeightPx = !mehrseitig;
    if (mehrseitig) aus.pageHeightPx = feld.pageFormat === "a4";
  }
  aktualisieren();

  return {
    feld, aus,
    waehleFormat(v) { feld.singlePagePdf = v;
      if (v === "false" && !vomNutzer) feld.pageFormat = "a4";
      aktualisieren(); },
    waehleGroesse(v) { feld.pageFormat = v; vomNutzer = true; aktualisieren(); },
  };
}

// 1. Frische Installation: fortlaufende Seite, abhaengige Felder ohne Wirkung
{
  const o = oberflaeche();
  ok(o.aus.pageFormat && o.aus.pageHeightPx,
     "Fortlaufende Seite: Seitengroesse und Pixelhoehe sind ausgegraut");
}

// 2. Wechsel auf mehrseitig setzt A4 und macht das Feld nutzbar
{
  const o = oberflaeche();
  o.waehleFormat("false");
  ok(o.feld.pageFormat === "a4", "Wechsel auf mehrseitig waehlt A4");
  ok(!o.aus.pageFormat, "Seitengroesse ist jetzt nutzbar");
  ok(o.aus.pageHeightPx, "Pixelhoehe bleibt ausgegraut, solange A4 gilt");
}

// 3. Wer die feste Hoehe waehlt, bekommt sie nutzbar
{
  const o = oberflaeche();
  o.waehleFormat("false");
  o.waehleGroesse("free");
  ok(!o.aus.pageHeightPx, "Feste Hoehe gewaehlt: Pixelfeld wird nutzbar");
}

// 4. Eine ausdrueckliche Wahl wird nicht ueberschrieben - der wichtigste Fall.
//    Wer "feste Hoehe" eingestellt hat, soll sie behalten, auch wenn er
//    zwischen den Formaten hin und her wechselt.
{
  const o = oberflaeche();
  o.waehleFormat("false");
  o.waehleGroesse("free");
  o.waehleFormat("true");            // zurueck auf eine Seite
  o.waehleFormat("false");           // und wieder auf mehrseitig
  ok(o.feld.pageFormat === "free", "Ausdrueckliche Wahl 'feste Hoehe' bleibt erhalten");
}

// 5. Bestandsnutzer mit gespeichertem "free" wird nicht umgestellt
{
  const o = oberflaeche({ singlePagePdf: "true", pageFormat: "free" });
  o.waehleFormat("false");
  ok(o.feld.pageFormat === "free", "Gespeichertes 'feste Hoehe' ueberlebt den Wechsel");
}

// 6. Gegenprobe: ohne die Automatik bliebe es beim gespeicherten Wert
{
  const ohne = (start) => {
    const feld = { singlePagePdf: "true", pageFormat: "free" , ...start };
    return { waehleFormat(v) { feld.singlePagePdf = v; }, feld };
  };
  const o = ohne({});
  o.waehleFormat("false");
  ok(o.feld.pageFormat === "free",
     "Gegenprobe: ohne Automatik bleibt 'free' - genau das war der Zustand vorher");
}

console.log(fehler === 0 ? "\nSeitenformat: alles in Ordnung" : `\nSeitenformat: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
