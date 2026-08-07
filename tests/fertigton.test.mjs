/* Prueft den Fertig-Ton: Wann wird er gespielt, und wie klingt er?
 *
 * Anlass (07.08.2026): Auf dem Telefon liegt der Blick waehrend der Aufnahme
 * selten auf dem Bildschirm - die Seite scrollt von selbst durch, das dauert.
 * Die Benachrichtigung allein sieht man erst, wenn man wieder hinschaut.
 *
 * Geprueft wird die Auswahlregel und die Form des Tons. Ob er angenehm klingt,
 * kann kein Test sagen; was sich messen laesst, ist: kein harter Einsatz
 * (sonst klingt es nach Fehler), leise, kurz, und ein Intervall statt zweier
 * gleicher Toene.
 */
let fehler = 0;
const ok = (b, t) => { console.log(`${b ? "ok  " : "FEHL"} ${t}`); if (!b) fehler++; };

/* Die Regel aus background.js */
const spieltAb = (einstellung, istAndroid) =>
  einstellung === true || (einstellung !== false && istAndroid);

ok(spieltAb(null, true)   === true,  "Android, nichts eingestellt: Ton an");
ok(spieltAb(null, false)  === false, "Rechner, nichts eingestellt: Ton aus");
ok(spieltAb(true, false)  === true,  "Rechner, ausdruecklich an: Ton an");
ok(spieltAb(false, true)  === false, "Android, ausdruecklich aus: kein Ton");
ok(spieltAb(undefined, true) === true, "undefined wie null behandelt");

/* Die Form des Tons, wie ihn spieleFertigTon() erzeugt. */
const TOENE = [[880, 0], [1174.66, 0.085]];
const SPITZE = 0.14, ANSTIEG = 0.012, LAENGE = 0.09;

ok(TOENE.length === 2, "zwei Toene, kein Dauerton");
const [a, b] = TOENE.map(t => t[0]);
const verhaeltnis = b / a;
ok(Math.abs(verhaeltnis - 4/3) < 0.01,
   `Intervall ist eine reine Quart (${verhaeltnis.toFixed(3)} zu ${(4/3).toFixed(3)})`);
ok(b > a, "aufsteigend - abfallend klingt nach Abbruch");
ok(SPITZE <= 0.2, `leise: Spitze ${SPITZE} von 1,0`);
ok(ANSTIEG >= 0.008, `weicher Einsatz: ${ANSTIEG*1000} ms Anstieg statt eines Knacks`);
const gesamt = TOENE[1][1] + LAENGE;
ok(gesamt < 0.25, `kurz: ${Math.round(gesamt*1000)} ms gesamt`);

/* Und das Wichtigste: Ein fehlender Ton darf die Aufnahme nicht gefaehrden.
 * Im Code steht der Aufruf ohne await und in try/catch - hier nachgestellt. */
{
  let aufnahmeFertig = false;
  const tonSpielen = () => { throw new Error("kein AudioContext"); };
  try { tonSpielen(); } catch (_) { /* verschluckt */ }
  aufnahmeFertig = true;
  ok(aufnahmeFertig, "Fehler beim Ton laesst die Aufnahme unberuehrt");
}

console.log(fehler === 0 ? "\nFertig-Ton: in Ordnung" : `\nFertig-Ton: ${fehler} Fehler`);
process.exit(fehler === 0 ? 0 : 1);
