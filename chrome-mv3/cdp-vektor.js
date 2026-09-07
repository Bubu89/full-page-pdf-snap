"use strict";

/* Vektor-Aufnahme ueber das DevTools-Protokoll (nur Chromium).
 *
 * Der uebrige Weg dieser Erweiterung setzt die Seite aus Bildschirmfotos
 * zusammen: scrollen, aufnehmen, aneinanderlegen. Das ergibt ein Bild der
 * Seite — treu, aber gross, ohne auswaehlbaren Text und ohne Verweise, die
 * sich anklicken lassen.
 *
 * Chromium kann dieselbe Seite selbst als PDF setzen. Dabei entstehen echte
 * Buchstaben, Vektorgrafik, Verweis-Anmerkungen und Sprungmarken aus den
 * id-Attributen des Dokuments — in einem Durchgang, ohne Scrollen. Gemessen
 * an einer Referenzseite (platform.kimi.ai, 12.822 px hoch): 489 kB gegenueber
 * mehreren Megabyte im Bildweg, bei besserer Darstellung.
 *
 * Drei Dinge muessen dafuer stimmen, und jedes davon ist eine eigene Falle:
 *
 *  1. Ohne "Emulation.setEmulatedMedia" mit "screen" druckt Chromium die
 *     Druckansicht der Seite. Seitenleisten, Navigation und alles, was in
 *     "@media print" ausgeblendet wird, fehlen dann — genau das, was der
 *     Bildweg zeigt und was hier auch stehen soll.
 *
 *  2. Ohne "Emulation.setDeviceMetricsOverride" auf die volle Dokumenthoehe
 *     bleiben nachgeladene Bilder leer und Elemente mit "position: sticky"
 *     stehen an der falschen Stelle. Die Hoehe muss VOR dem Druck gesetzt
 *     werden, nicht waehrenddessen.
 *
 *  3. Der Massstab des Reiters gehoert in die Rechnung. Wer die Seite auf
 *     150 % gestellt hat, dessen Dokument ist in CSS-Pixeln schmaler — wird
 *     das uebergangen, schneidet der Druck rechts ab.
 *
 * Die Schnittstelle verlangt die Erlaubnis "debugger". Sie wird bewusst erst
 * bei Bedarf erfragt (siehe vektorErlaubt) und nicht im Manifest verlangt:
 * Wer den Bildweg nutzt, soll bei der Installation keine Warnung sehen.
 */

const PageShotVektor = (function () {

  // Chromium setzt bei sehr hohen Blaettern still aus. Gemessen an der
  // Referenz-Erweiterung, die oberhalb dieser Grenze auf mehrere Blaetter
  // ausweicht: 800 Zoll, also rund 76.800 CSS-Pixel. Das sind etwa sechzig
  // Bildschirmhoehen — daruber ist ein einzelnes Blatt ohnehin keine
  // sinnvolle Ausgabe mehr, und die Aufnahme faellt auf Seiten zurueck.
  const MAX_BLATT_ZOLL = 800;

  // CSS-Pixel je Zoll. Das PDF rechnet in Zoll, das Dokument in Pixeln.
  const PX_JE_ZOLL = 96;

  const TAG = "[PDFSnap/vektor]";
  const log = (...a) => console.log(TAG, ...a);

  /* Steht die Schnittstelle ueberhaupt zur Verfuegung?
   *
   * In Firefox gibt es sie nicht — dort bleibt es beim Bildweg. Die Pruefung
   * faellt bewusst still aus: ein fehlendes DevTools-Protokoll ist kein
   * Fehler, sondern ein anderer Browser. */
  function vektorMoeglich() {
    return typeof browser !== "undefined"
        && browser.debugger
        && typeof browser.debugger.attach === "function";
  }

  /* Liegt die Erlaubnis vor?
   *
   * Angefordert wird sie NICHT hier. "permissions.request" verlangt eine
   * Nutzerhandlung und scheitert im Hintergrunddienst — die Anfrage gehoert
   * in die Einstellungsseite, wo ein Klick sie traegt. Hier wird nur
   * nachgesehen. */
  async function vektorErlaubt() {
    if (!vektorMoeglich()) return false;
    try {
      return await browser.permissions.contains({ permissions: ["debugger"] });
    } catch (e) {
      log("Erlaubnis nicht abfragbar:", e && e.message);
      return false;
    }
  }

  function senden(tabId, methode, parameter) {
    return browser.debugger.sendCommand({ tabId }, methode, parameter || {});
  }

  async function angehaengt(tabId) {
    try {
      const ziele = await browser.debugger.getTargets();
      return ziele.some(z => z.tabId === tabId && z.attached);
    } catch (_) { return false; }
  }

  /* Die Masse des Dokuments.
   *
   * Nicht nur "scrollHeight": Seiten mit ueberstehenden Elementen — absolut
   * gesetzte Fusszeilen, aufgeklappte Menues — sind hoeher als ihr
   * Scrollbereich. Der Rueckgabewert nimmt das Groesste aus drei Messungen,
   * damit unten nichts abgeschnitten wird. Genau diese drei Messungen nimmt
   * auch die Referenz-Erweiterung. */
  async function masseMessen(tabId) {
    const ausdruck = `(() => {
      const wurzel = document.scrollingElement || document.documentElement;
      const y = window.scrollY, x = window.scrollX;
      const hoehe = Math.max(
        wurzel.scrollHeight,
        document.documentElement.getBoundingClientRect().bottom + y,
        document.body ? document.body.getBoundingClientRect().bottom + y : 0
      );
      const breite = Math.max(
        wurzel.scrollWidth,
        document.documentElement.getBoundingClientRect().right + x,
        document.body ? document.body.getBoundingClientRect().right + x : 0,
        document.documentElement.clientWidth
      );
      return { breite: Math.ceil(breite), hoehe: Math.ceil(hoehe) };
    })()`;
    const antwort = await senden(tabId, "Runtime.evaluate",
      { expression: ausdruck, returnByValue: true });
    const wert = antwort && antwort.result && antwort.result.value;
    if (!wert || !wert.hoehe) throw new Error("Dokumentmasse nicht lesbar");
    return wert;
  }

  /* Nachladende Bilder anstossen.
   *
   * Das Setzen der Fenstergroesse allein reicht nicht: Viele Seiten laden
   * erst, wenn ein Beobachter den Ausschnitt meldet. Ein Sprung ans Ende und
   * zurueck loest das zuverlaessiger aus als jedes Warten — und kostet
   * nichts, weil das Fenster ohnehin schon die volle Hoehe hat. */
  async function nachladenAnstossen(tabId, ruheMs) {
    const ausdruck = `(() => {
      window.scrollTo(0, document.body ? document.body.scrollHeight : 0);
      window.scrollTo(0, 0);
      const bilder = Array.from(document.images || []);
      bilder.forEach(b => { if (b.loading === "lazy") b.loading = "eager"; });
      return bilder.length;
    })()`;
    try { await senden(tabId, "Runtime.evaluate", { expression: ausdruck, returnByValue: true }); }
    catch (e) { log("Nachladen nicht angestossen:", e && e.message); }
    await new Promise(r => setTimeout(r, Math.max(120, ruheMs || 400)));
  }

  /* Nur den Artikel drucken.
   *
   * Gemeint ist der Lesetext ohne Navigation, Seitenleisten, Banner und
   * Empfehlungslisten. Das Dokument wird dabei NICHT umgebaut — umgestellte
   * Knoten kommen nicht zuverlaessig zurueck, und ein zerschossener Reiter
   * ist ein hoeherer Preis als ein unsauberer Ausschnitt. Stattdessen wird
   * ausgeblendet: der Artikel und seine Vorfahren bleiben stehen, alles
   * daneben verschwindet. Ein einziges Stylesheet und ein Attribut, beides
   * restlos zuruecknehmbar.
   *
   * Die Auswahl geht nach Textmenge und Linkanteil. Navigationsbloecke haben
   * viel Verweistext und wenige Absaetze, Lesetext umgekehrt — das trennt die
   * beiden zuverlaessiger als jede Liste bekannter Klassennamen, die bei der
   * naechsten Seite ohnehin nicht mehr passt. */
  /* Zwei Schreibweisen derselben Marke, und das ist kein Versehen.
   *
   * "el.dataset.pdfsnapArtikelAus" legt das Attribut "data-pdfsnap-artikel-aus"
   * an — dataset uebersetzt Binnengrossschreibung in Trennstriche. Ein
   * CSS-Selektor "[data-pdfsnapArtikelAus]" trifft deshalb nichts. Beide
   * Formen stehen hier nebeneinander, damit die Umschreibung sichtbar bleibt
   * statt sich in zwei Zeichenketten zu verstecken, die nur zufaellig
   * zusammenpassen. */
  const MARKE_DATASET = "pdfsnapArtikelAus";
  const MARKE_ATTRIBUT = "data-pdfsnap-artikel-aus";

  async function artikelAn(tabId, schriftgroesse) {
    const ausdruck = `(() => {
      /* Der Rumpf des Dokuments gehoert NICHT in diese Liste.
       *
       * Er enthaelt jeden Kandidaten und damit zwangslaeufig mehr Text als
       * jeder von ihnen — bei der Messung an platform.kimi.ai kam er auf 22.562
       * Punkte gegen 17.652 des <main>. Als Mitbewerber gewinnt er deshalb
       * immer, und der Artikelmodus schaltete sich mit "kein Artikel
       * erkennbar" ab, obwohl ein brauchbarer Kandidat dastand. Fehlt jeder
       * Kandidat, bleibt es ohnehin bei der ganzen Seite. */
      const kandidaten = Array.from(document.querySelectorAll(
        "article, main, [role=main], [itemprop=articleBody], .post, .entry-content, .article-body, #content, .content"
      )).filter(el => el !== document.body && el !== document.documentElement);

      const bewerten = (el) => {
        const text = (el.innerText || "").trim();
        if (text.length < 200) return -1;
        let verweistext = 0;
        for (const a of el.querySelectorAll("a")) verweistext += (a.innerText || "").length;
        const absaetze = el.querySelectorAll("p").length;
        const anteil = verweistext / Math.max(1, text.length);
        // Viel Text, viele Absaetze, wenig Verweisanteil.
        return text.length * (1 + absaetze / 10) * (1 - Math.min(0.95, anteil));
      };

      let bester = null, bestwert = -1;
      for (const k of kandidaten) {
        const w = bewerten(k);
        if (w > bestwert) { bestwert = w; bester = k; }
      }
      if (!bester || bester === document.body) return { ok: false };

      let knoten = bester;
      while (knoten && knoten.parentElement && knoten !== document.documentElement) {
        for (const geschwister of Array.from(knoten.parentElement.children)) {
          if (geschwister !== knoten) geschwister.dataset.${MARKE_DATASET} = "1";
        }
        knoten = knoten.parentElement;
      }
      bester.dataset.pdfsnapArtikel = "1";

      /* Den Artikel neu setzen, nicht nur freistellen.
       *
       * Bis 2.35.2 wurde nur ausgeblendet, was neben dem Artikel stand. Der
       * Text behielt dabei die Gestaltung der Website: dunkle Codefelder,
       * enge Zeilen, Schriftgroessen fuer einen Bildschirm. Auf einem Blatt
       * und erst recht auf einem Telefon liest sich das schlecht — gemeldet
       * am 18.08.2026 mit genau dieser Beobachtung.
       *
       * Deshalb bekommt der Artikel eine eigene Typografie: heller Grund,
       * dunkle Schrift, ruhige Zeilenlaenge, Bilder auf Blattbreite begrenzt,
       * Codefelder hell und umgebrochen statt waagerecht schiebbar — auf
       * Papier gibt es kein Schieben, was rechts hinausragt, fehlt.
       *
       * Alles laeuft ueber EIN Stylesheet und zwei Attribute; der Aufbau des
       * Dokuments bleibt unangetastet und laesst sich restlos zuruecknehmen. */
      const stil = document.createElement("style");
      stil.id = "pdfsnap-artikel-stil";
      stil.textContent = [
        "[${MARKE_ATTRIBUT}] { display: none !important; }",
        "html, body { background: #fff !important; margin: 0 !important;",
        "  padding: 0 !important; overflow: visible !important; height: auto !important; }",
        "[data-pdfsnap-artikel] {",
        "  display: block !important; float: none !important; position: static !important;",
        "  width: auto !important; max-width: none !important;",
        "  margin: 0 !important; padding: 1.5em 1.6em !important;",
        "  background: #fff !important; color: #111 !important;",
        "  font-size: ${Number(schriftgroesse) || 18}px !important;",
        "  line-height: 1.65 !important;",
        "  font-family: Georgia, 'Times New Roman', serif !important;",
        "}",
        "[data-pdfsnap-artikel] * { background-color: transparent !important;",
        "  color: #111 !important; max-width: 100% !important; box-shadow: none !important; }",
        "[data-pdfsnap-artikel] p, [data-pdfsnap-artikel] li {",
        "  font-size: 1em !important; line-height: 1.65 !important; margin: .7em 0 !important; }",
        "[data-pdfsnap-artikel] h1 { font-size: 1.9em !important; line-height: 1.25 !important;",
        "  margin: 0 0 .5em !important; }",
        "[data-pdfsnap-artikel] h2 { font-size: 1.45em !important; line-height: 1.3 !important;",
        "  margin: 1.4em 0 .4em !important; }",
        "[data-pdfsnap-artikel] h3 { font-size: 1.2em !important; margin: 1.2em 0 .3em !important; }",
        "[data-pdfsnap-artikel] a { color: #1a4fa0 !important; text-decoration: underline !important; }",
        "[data-pdfsnap-artikel] img, [data-pdfsnap-artikel] figure, [data-pdfsnap-artikel] svg {",
        "  max-width: 100% !important; height: auto !important; margin: 1em 0 !important; }",
        "[data-pdfsnap-artikel] pre, [data-pdfsnap-artikel] code {",
        "  background: #f5f5f5 !important; color: #111 !important;",
        "  font-family: ui-monospace, Menlo, Consolas, monospace !important;",
        "  font-size: .82em !important; white-space: pre-wrap !important;",
        "  word-break: break-word !important; overflow: visible !important; }",
        "[data-pdfsnap-artikel] pre { padding: .8em !important; border: 1px solid #ddd !important;",
        "  border-radius: 4px !important; margin: 1em 0 !important; }",
        "[data-pdfsnap-artikel] table { width: 100% !important; border-collapse: collapse !important;",
        "  font-size: .9em !important; }",
        "[data-pdfsnap-artikel] th, [data-pdfsnap-artikel] td {",
        "  border: 1px solid #ccc !important; padding: .4em .6em !important; }",
        "[data-pdfsnap-artikel] blockquote { border-left: 3px solid #ccc !important;",
        "  padding-left: 1em !important; margin: 1em 0 !important; font-style: italic !important; }"
      ].join("\\n");
      document.documentElement.appendChild(stil);
      return { ok: true, zeichen: (bester.innerText || "").length };
    })()`;
    try {
      const antwort = await senden(tabId, "Runtime.evaluate",
        { expression: ausdruck, returnByValue: true });
      const wert = antwort && antwort.result && antwort.result.value;
      if (wert && wert.ok) { log("Artikel erkannt:", wert.zeichen, "Zeichen"); return true; }
      log("Kein Artikel erkennbar — ganze Seite.");
      return false;
    } catch (err) {
      log("Artikelmodus nicht angewandt:", err && err.message);
      return false;
    }
  }

  async function artikelAus(tabId) {
    const ausdruck = `(() => {
      const stil = document.getElementById("pdfsnap-artikel-stil");
      if (stil) stil.remove();
      document.querySelectorAll("[${MARKE_ATTRIBUT}]").forEach(
        el => delete el.dataset.${MARKE_DATASET});
      document.querySelectorAll("[data-pdfsnap-artikel]").forEach(
        el => delete el.dataset.pdfsnapArtikel);
      return true;
    })()`;
    try { await senden(tabId, "Runtime.evaluate", { expression: ausdruck, returnByValue: true }); }
    catch (err) { log("Artikelmodus nicht zurueckgenommen:", err && err.message); }
  }

  /* Mitlaufende Balken ausblenden.
   *
   * Ein Element mit "position: fixed" klebt am Fenster, nicht am Dokument.
   * Bei einem Fenster von der Hoehe des ganzen Dokuments steht es dadurch
   * genau einmal im Bild — meistens quer ueber dem Text. Cookie-Banner,
   * Kopfleisten und schwebende Schaltflaechen gehoeren nicht in den Beleg. */
  async function balkenAusblenden(tabId) {
    const ausdruck = `(() => {
      const stil = document.createElement("style");
      stil.id = "pdfsnap-balken-stil";
      let getroffen = 0;
      const treffer = [];
      for (const el of Array.from(document.body ? document.body.querySelectorAll("*") : [])) {
        const s = getComputedStyle(el);
        if (s.position === "fixed" || s.position === "sticky") {
          el.dataset.pdfsnapBalken = "1"; getroffen++;
          if (getroffen > 400) break;
        }
      }
      stil.textContent = "[data-pdfsnap-balken] { display: none !important; }";
      document.documentElement.appendChild(stil);
      return getroffen;
    })()`;
    try {
      const antwort = await senden(tabId, "Runtime.evaluate",
        { expression: ausdruck, returnByValue: true });
      const n = antwort && antwort.result && antwort.result.value;
      if (n) log("Mitlaufende Elemente ausgeblendet:", n);
    } catch (err) { log("Balken nicht ausgeblendet:", err && err.message); }
  }

  async function balkenZeigen(tabId) {
    const ausdruck = `(() => {
      const stil = document.getElementById("pdfsnap-balken-stil");
      if (stil) stil.remove();
      document.querySelectorAll("[data-pdfsnap-balken]").forEach(
        el => delete el.dataset.pdfsnapBalken);
      return true;
    })()`;
    try { await senden(tabId, "Runtime.evaluate", { expression: ausdruck, returnByValue: true }); }
    catch (err) { log("Balken nicht wiederhergestellt:", err && err.message); }
  }

  /* Der eigentliche Druck.
   *
   * "generateDocumentOutline" kennen aeltere Chromium-Fassungen nicht und
   * antworten mit einem Fehler statt es zu uebergehen. Deshalb der zweite
   * Versuch ohne den Schalter: ein Inhaltsverzeichnis ist eine Zugabe, kein
   * Grund, die Aufnahme scheitern zu lassen. */
  async function drucken(tabId, parameter) {
    try {
      return await senden(tabId, "Page.printToPDF", parameter);
    } catch (e) {
      const txt = (e && e.message) || "";
      if (/generateDocumentOutline|Invalid parameters/i.test(txt)) {
        const ohne = Object.assign({}, parameter);
        delete ohne.generateDocumentOutline;
        log("Ohne Inhaltsverzeichnis erneut versucht.");
        return await senden(tabId, "Page.printToPDF", ohne);
      }
      throw e;
    }
  }

  function base64ZuBytes(b64) {
    const roh = atob(b64);
    const aus = new Uint8Array(roh.length);
    for (let i = 0; i < roh.length; i++) aus[i] = roh.charCodeAt(i);
    return aus;
  }

  /* Nimmt den Reiter als Vektor-PDF auf.
   *
   * Gibt { bytes, breite, hoehe, blaetter, einBlatt } zurueck. Wirft, wenn
   * der Weg nicht gangbar ist — der Aufrufer faellt dann auf den Bildweg
   * zurueck, statt dem Nutzer einen Fehler zu zeigen. */
  async function vektorAufnehmen(tabId, einstellungen) {
    const e = einstellungen || {};
    let hing = false;
    const artikelModus = e.modus === "artikel";
    let artikelGesetzt = false;
    let balkenGesetzt = false;

    await browser.debugger.attach({ tabId }, "1.3");
    hing = true;
    try {
      // Bildschirmansicht statt Druckansicht — sonst fehlen die Seitenleisten.
      await senden(tabId, "Emulation.setEmulatedMedia", { media: "screen" });

      /* Beides veraendert die Hoehe des Dokuments und muss deshalb VOR dem
       * Messen geschehen. Wird erst gemessen und dann ausgeblendet, ist das
       * Blatt zu hoch und endet in einer leeren Flaeche. */
      if (artikelModus) {
        artikelGesetzt = await artikelAn(tabId, e.artikelSchriftgroesse);
      }
      if (artikelModus || e.hideSticky !== false) {
        await balkenAusblenden(tabId);
        balkenGesetzt = true;
      }

      // Der Massstab des Reiters geht in die Fenstergroesse ein.
      let massstab = 1;
      try { massstab = await browser.tabs.getZoom(tabId); } catch (_) { massstab = 1; }
      if (!massstab || !isFinite(massstab)) massstab = 1;

      /* Feste Blattbreite fuer das Leselayout.
       *
       * Im Artikelmodus soll nicht die Fensterbreite gelten, sondern die des
       * Papiers: Der Text bricht dann so um, wie er auf dem Blatt steht, statt
       * in einer Zeilenlaenge, die vom zufaellig geoeffneten Fenster stammt.
       * Dafuer muss die Breite VOR dem Messen gesetzt werden — die Hoehe
       * ergibt sich erst aus dem umgebrochenen Text.
       *
       * Nachgemessen am Vergleichsstueck (web to pdf, Artikelausgabe
       * derselben Seite): 598 pt breit, also A4 hoch, bei 4.354 pt Hoehe auf
       * einem einzigen Blatt. Genau diese Form entsteht hier. */
      if (e.blattBreitePx) {
        await senden(tabId, "Emulation.setDeviceMetricsOverride", {
          width: Math.round(e.blattBreitePx),
          height: 900,
          deviceScaleFactor: 1, scale: 1, mobile: false,
        });
        // Dem Umbruch Zeit lassen, sonst wird die Hoehe der alten Breite gemessen.
        await new Promise(r => setTimeout(r, 250));
        massstab = 1;   // die Breite ist gesetzt, der Reiterzoom spielt keine Rolle mehr
      }

      const masse = await masseMessen(tabId);

      await senden(tabId, "Emulation.setDeviceMetricsOverride", {
        width: Math.round((e.blattBreitePx || masse.breite) * massstab),
        height: Math.round(masse.hoehe * massstab),
        deviceScaleFactor: 1,
        scale: 1,
        mobile: false,
      });

      await nachladenAnstossen(tabId, e.settlingMs);

      // Nach dem Nachladen kann die Seite gewachsen sein — noch einmal messen.
      const endgueltig = await masseMessen(tabId);
      /* Im Leselayout bleibt die Blattbreite massgeblich.
       * Die Messung liefert dort gelegentlich ein paar Pixel mehr — ein
       * ueberstehendes Codefeld, eine breite Tabelle. Wuerde man das
       * uebernehmen, waere das Blatt nicht mehr A4 breit, und der Zweck der
       * festen Breite waere dahin. Was uebersteht, wird beschnitten; das ist
       * dieselbe Entscheidung, die ein Drucker auch trifft. */
      const breite = e.blattBreitePx || Math.max(masse.breite, endgueltig.breite);
      const hoehe = Math.max(masse.hoehe, endgueltig.hoehe);

      const breiteZoll = breite / PX_JE_ZOLL;
      const hoeheZoll = hoehe / PX_JE_ZOLL;
      const einBlatt = hoeheZoll <= MAX_BLATT_ZOLL;

      const grund = {
        printBackground: true,
        marginTop: 0, marginRight: 0, marginBottom: 0, marginLeft: 0,
        preferCSSPageSize: false,
        displayHeaderFooter: false,
        paperWidth: breiteZoll,
        generateDocumentOutline: true,
        transferMode: "ReturnAsBase64",
      };

      /* Ein Blatt, so hoch wie das Dokument — das ist der Kern der Sache.
       *
       * Oberhalb der Grenze wird stattdessen auf Blaetter von 800 Zoll
       * umgestellt. Das ist kein Notbehelf, sondern die ehrlichere Ausgabe:
       * ein Blatt von ueber sechzig Bildschirmhoehen laesst sich weder
       * anzeigen noch drucken. */
      /* Fuer den Druck echte Blaetter, sonst ein durchgehendes.
       *
       * Bis 2.35.2 kannte der Vektorweg nur die Endlosseite. "Aufnahme fuer
       * Druck" stellte zwar den Bildweg um, wurde hier aber nicht beachtet —
       * wer den Vektorweg eingeschaltet hatte, bekam trotzdem eine einzige
       * Bahn von mehreren Metern. Auf Papier ist das unbrauchbar.
       *
       * Jetzt bekommt der Druckfall die tatsaechlichen Blattmasse und KEIN
       * pageRanges: Chromium bricht den Inhalt dann selbst auf so viele
       * Blaetter um, wie er braucht, und zwar an Stellen, an denen keine Zeile
       * zerschnitten wird. Die Raender sind bewusst nicht null — ohne sie
       * steht der Text bis an die Blattkante, und jeder Drucker schneidet dort
       * etwas ab. */
      let parameter;
      if (e.druckblatt) {
        parameter = Object.assign({}, grund, {
          paperWidth: e.druckblatt.breiteZoll,
          paperHeight: e.druckblatt.hoeheZoll,
          marginTop: 0.4, marginRight: 0.4, marginBottom: 0.4, marginLeft: 0.4,
        });
        log("Druckblaetter:", e.druckblatt.breiteZoll.toFixed(2) + " x "
          + e.druckblatt.hoeheZoll.toFixed(2) + " Zoll");
      } else if (einBlatt) {
        parameter = Object.assign({}, grund, { paperHeight: hoeheZoll, pageRanges: "1" });
      } else {
        parameter = Object.assign({}, grund, { paperHeight: MAX_BLATT_ZOLL });
      }

      if (!einBlatt) {
        log("Dokument hoeher als " + MAX_BLATT_ZOLL + " Zoll (" + Math.round(hoehe)
          + " px) — Ausgabe auf mehreren Blaettern.");
      }

      const ergebnis = await drucken(tabId, parameter);
      if (!ergebnis || !ergebnis.data) throw new Error("Kein PDF zurueckgeliefert");

      const bytes = base64ZuBytes(ergebnis.data);
      log("Vektor-PDF:", Math.round(bytes.length / 1024) + " kB,",
          Math.round(breite) + "x" + Math.round(hoehe) + " px,",
          einBlatt ? "ein Blatt" : "mehrere Blaetter");

      return { bytes, breite, hoehe, massstab,
               einBlatt: e.druckblatt ? false : einBlatt,
               modus: artikelGesetzt ? "artikel" : (e.druckblatt ? "druck" : "seite") };
    } finally {
      /* Aufraeumen in jedem Fall — und einzeln abgesichert.
       *
       * Bleibt die Fenstergroesse gesetzt, sieht der Nutzer eine verzerrte
       * Seite und weiss nicht warum. Bleibt der Debugger haengen, laesst sich
       * der Reiter nicht mehr aufnehmen. Ein Fehler beim Aufraeumen darf den
       * bereits erzeugten PDF-Inhalt nicht verwerfen. */
      if (hing) {
        if (artikelGesetzt) await artikelAus(tabId);
        if (balkenGesetzt) await balkenZeigen(tabId);
        try { await senden(tabId, "Emulation.clearDeviceMetricsOverride"); }
        catch (err) { log("Fenstergroesse nicht zurueckgesetzt:", err && err.message); }
        try { await senden(tabId, "Emulation.setEmulatedMedia", { media: "" }); }
        catch (err) { log("Medienart nicht zurueckgesetzt:", err && err.message); }
        try { if (await angehaengt(tabId)) await browser.debugger.detach({ tabId }); }
        catch (err) { log("Debugger nicht geloest:", err && err.message); }
      }
    }
  }

  return {
    vektorMoeglich,
    vektorErlaubt,
    vektorAufnehmen,
    MAX_BLATT_ZOLL,
  };
})();

if (typeof globalThis !== "undefined") globalThis.PageShotVektor = PageShotVektor;
