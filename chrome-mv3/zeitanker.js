// Zeitanker — belegt eine Untergrenze fuer den Aufnahmezeitpunkt, ohne der
// Geraeteuhr zu glauben.
//
// Die Fussnote dieses Add-ons sagt heute zu Recht, dass ihr Zeitstempel von der
// Geraeteuhr stammt und damit wenig beweist. Wer rueckdatieren will, stellt die
// Uhr. Dagegen hilft ein Wert, den zum fraglichen Zeitpunkt noch niemand kennen
// konnte: das drand-Netz der League of Entropy (Cloudflare, EPFL, Protocol Labs
// u. a.) veroeffentlicht alle drei Sekunden einen per threshold-BLS signierten
// Zufallswert. Steht er in der Aufnahme, ist sie nicht aelter als seine Runde.
//
// Bewusste Entscheidungen:
//  - Keine Bibliothek. WebCrypto und fetch genuegen.
//  - Keine neue Berechtigung. api.drand.sh sendet 'Access-Control-Allow-Origin: *',
//    der Abruf laeuft ohne host_permissions. Die Liste bleibt bei activeTab.
//  - Standardmaessig AUS. Der Abruf ist ein Netzzugriff; solange er nicht
//    verlangt wurde, findet er nicht statt.
//  - Es wird nichts gesendet. Ein GET holt einen oeffentlichen Wert ab; weder
//    die Seite noch die Aufnahme noch ein Hash verlassen das Geraet.
//
// Was das NICHT leistet: Es beweist nicht, dass die Seite zeigte, was sie zeigt,
// und macht die Aufnahme nicht zu einem qualifizierten Zeitstempel nach eIDAS.
// Belegt ist allein: nicht vor dieser Runde entstanden.

const PageShotZeitanker = (() => {
  "use strict";

  // quicknet, 3-Sekunden-Takt, unchained: eine Runde ist allein aus ihrer
  // Nummer pruefbar, ohne die Kette davor zu laden.
  const KETTE = "52db9ba70e0cc0f6eaf7803dd07447a1f5477735fd3f661792ba94600c84e971";
  const GENESIS = 1692803367;
  const PERIODE = 3;
  const HOSTS = ["https://api.drand.sh", "https://drand.cloudflare.com", "https://api2.drand.sh"];
  const TIMEOUT_MS = 4000;

  function rundenZeit(runde) {
    return GENESIS + (runde - 1) * PERIODE;
  }

  // Plausibilitaet: Eine Runde, die weit in der Zukunft laege, waere entweder
  // ein Fehler oder ein Manipulationsversuch. Ein grosszuegiges Fenster nach
  // hinten bleibt zulaessig — eine falsch gehende Geraeteuhr soll den Anker
  // nicht verwerfen, sie ist ja gerade der Grund fuer ihn.
  function plausibel(zeitSek) {
    const jetzt = Date.now() / 1000;
    return zeitSek < jetzt + 120;
  }

  async function holen() {
    const fehler = [];
    for (const host of HOSTS) {
      const ab = new AbortController();
      const t = setTimeout(() => ab.abort(), TIMEOUT_MS);
      try {
        const r = await fetch(`${host}/${KETTE}/public/latest`,
                              { cache: "no-store", signal: ab.signal });
        if (!r.ok) throw new Error("HTTP " + r.status);
        const d = await r.json();
        if (!d || typeof d.round !== "number" || !d.randomness) throw new Error("unerwartete Antwort");
        const zeit = rundenZeit(d.round);
        if (!plausibel(zeit)) throw new Error("Rundenzeit unplausibel");
        return {
          netz: "drand-quicknet",
          kette: KETTE,
          runde: d.round,
          zufall: d.randomness,
          signatur: d.signature || "",
          nichtVor: zeit,
          quelle: host,
        };
      } catch (e) {
        fehler.push(host.replace("https://", "") + ": " + (e && e.message));
      } finally {
        clearTimeout(t);
      }
    }
    throw new Error(fehler.join(" | "));
  }

  // Kanonische Form: sortierte Schluessel, kein Whitespace. Muss identisch zur
  // Python-Referenz sein (proof-stamp/prototyp/stempel.py), sonst laesst sich
  // eine am Handy erzeugte Aufnahme am PC nicht nachrechnen.
  function kanonisch(w) {
    if (w === null || typeof w !== "object") return JSON.stringify(w);
    if (Array.isArray(w)) return "[" + w.map(kanonisch).join(",") + "]";
    return "{" + Object.keys(w).sort()
      .map(k => JSON.stringify(k) + ":" + kanonisch(w[k])).join(",") + "}";
  }

  async function sha256Hex(bytes) {
    const b = typeof bytes === "string" ? new TextEncoder().encode(bytes) : bytes;
    const d = await crypto.subtle.digest("SHA-256", b);
    return Array.from(new Uint8Array(d)).map(x => x.toString(16).padStart(2, "0")).join("");
  }

  // Verbindet Bild-Pruefsumme, Herkunftsangaben und Anker zu einem Wert.
  // Dass die Herkunftsangaben mitgehen, ist der Punkt: auch eine nachtraeglich
  // geaenderte Adresse faellt auf, obwohl das Bild unberuehrt blieb.
  async function stempeln(bildSha256, angaben, anker) {
    const felder = {
      v: "ps-1",
      inhalt_sha256: bildSha256,
      metadaten: angaben || {},
      beacon: { netz: anker.netz, kette: anker.kette, runde: anker.runde, zufall: anker.zufall },
    };
    return await sha256Hex(kanonisch(felder));
  }

  return { holen, stempeln, kanonisch, sha256Hex, rundenZeit };
})();

if (typeof module !== "undefined") module.exports = PageShotZeitanker;
