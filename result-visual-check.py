#!/usr/bin/env python3
"""Rendert die Ergebnisseite und prueft, was tatsaechlich zu sehen ist.

Die Seite laesst sich sonst nur auf einem Geraet mit installierter Erweiterung
betrachten - hier laeuft sie in Firefox mit nachgebauter browser-API. Firefox
und nicht Chromium, weil das Ziel Firefox fuer Android ist: dieselbe Anzeige
(pdf.js) entscheidet dort darueber, ob die Vorschau ueberhaupt erscheint.
Geprueft wird, was schon zweimal danebengegangen ist: leere Flaechen, Text der
aus dem Rahmen faellt, Schaltflaechen unter der Mindestgroesse fuer Finger.

    python3 result-visual-check.py            # prueft, legt PNG ab
    python3 result-visual-check.py --show     # zusaetzlich Pfade ausgeben

Exitcode 1, sobald eine Erwartung nicht haelt.
"""
import asyncio
import base64
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
AUS = REPO / "_visual-check"
MIN_TIPPFLAECHE = 44          # px, uebliche Untergrenze fuer Fingerziele

# Ein winziges, gueltiges PDF - genug, damit der Betrachter etwas anzeigt.
MINI_PDF = (
    "JVBERi0xLjQKMSAwIG9iago8PC9UeXBlL0NhdGFsb2cvUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAw"
    "IG9iago8PC9UeXBlL1BhZ2VzL0tpZHNbMyAwIFJdL0NvdW50IDE+PgplbmRvYmoKMyAwIG9iago8"
    "PC9UeXBlL1BhZ2UvUGFyZW50IDIgMCBSL01lZGlhQm94WzAgMCAyMDAgMjAwXT4+CmVuZG9iagp4"
    "cmVmCjAgNAowMDAwMDAwMDAwIDY1NTM1IGYgCjAwMDAwMDAwMDkgMDAwMDAgbiAKMDAwMDAwMDA1"
    "NiAwMDAwMCBuIAowMDAwMDAwMTExIDAwMDAwIG4gCnRyYWlsZXIKPDwvU2l6ZSA0L1Jvb3QgMSAw"
    "IFI+PgpzdGFydHhyZWYKMTkwCiUlRU9G"
)

def testbild():
    """Ein Ersatz fuer die verkleinerte Seitenansicht - lang und mit Inhalt,
    damit sich eine leere Flaeche davon unterscheiden laesst."""
    from PIL import Image, ImageDraw
    import io
    breite, hoehe = 720, 2400
    bild = Image.new("RGB", (breite, hoehe), "white")
    zeichner = ImageDraw.Draw(bild)
    zeichner.rectangle([0, 0, breite, 90], fill=(37, 99, 235))
    for i in range(24, hoehe, 34):          # Textzeilen andeuten
        laenge = breite - 60 - (i * 7 % 260)
        zeichner.rectangle([30, i + 90, laenge, i + 104], fill=(70, 70, 80))
    puffer = io.BytesIO()
    bild.save(puffer, format="JPEG", quality=70)
    return base64.b64encode(puffer.getvalue()).decode()


# Nachbau der Erweiterungs-API. Nur so viel, wie die Seite anfasst.
STUB = """
window.browser = {
  runtime: {
    getURL: (p) => p,
    sendMessage: async (msg) => {
      if (msg.type === "pdfsnap:last") {
        return {
          ok: true,
          url: "data:application/pdf;base64,%PDF%",
          preview: "data:image/jpeg;base64,%BILD%",
          filename: "orf.at_2026-08-01_1245_0007.pdf",
          path: "Full Page PDF Snap/orf.at_2026-08-01_1245_0007.pdf",
          pages: 3,
          saved: true,
          downloadId: 42
        };
      }
      if (msg.type === "pdfsnap:open") return { ok: true };
      return null;
    }
  },
  storage: { local: { get: async (d) => d } },
  i18n: { getMessage: () => "", getUILanguage: () => "de" },
  downloads: { download: async () => 43 },
  tabs: { create: async () => ({ id: 1 }) }
};
""".replace("%PDF%", MINI_PDF)

STUB = STUB.replace("%BILD%", testbild())

FAELLE = [
    # (Name, Breite, Hoehe, dunkel?)
    ("handy-hell", 412, 915, False),
    ("handy-dunkel", 412, 915, True),
    ("desktop-hell", 1100, 800, False),
]


async def flaechen_streuung(seite, waehler):
    """Standardabweichung der Helligkeit im Ausschnitt eines Elements.

    Eine einfarbige Flaeche liegt nahe null - egal ob sie weiss, grau oder
    schwarz ist. Damit faellt eine leere Vorschau auf, die eine reine
    Groessenmessung durchwinkt.
    """
    kasten = await seite.locator(waehler).bounding_box()
    if not kasten or kasten["height"] < 10:
        return None
    roh = await seite.screenshot(clip={
        "x": kasten["x"], "y": max(0, kasten["y"]),
        "width": kasten["width"],
        "height": min(kasten["height"], 400),
    })
    from PIL import Image, ImageStat
    import io
    bild = Image.open(io.BytesIO(roh)).convert("L")
    return ImageStat.Stat(bild).stddev[0]


async def pruefe(pw, name, breite, hoehe, dunkel):
    browser = await pw.firefox.launch()
    ctx = await browser.new_context(
        viewport={"width": breite, "height": hoehe},
        device_scale_factor=2,
        color_scheme="dark" if dunkel else "light",
    )
    await ctx.add_init_script(STUB)
    seite = await ctx.new_page()
    fehler = []
    seite.on("pageerror", lambda e: fehler.append(f"JS-Fehler: {e}"))
    seite.on("console", lambda m: fehler.append(f"Konsole: {m.text}")
             if m.type == "error" else None)

    await seite.goto((REPO / "result.html").as_uri())
    await seite.wait_for_timeout(1800)

    befunde = []

    # 1. Dateiname sichtbar und nicht leer
    name_text = (await seite.inner_text("#name")).strip()
    if not name_text or name_text == "…":
        befunde.append("Dateiname wird nicht angezeigt")

    # 2. Beide Schaltflaechen da, gross genug, nebeneinander
    for knopf_id in ("download", "share"):
        kasten = await seite.locator(f"#{knopf_id}").bounding_box()
        if not kasten:
            befunde.append(f"#{knopf_id} nicht sichtbar")
            continue
        if kasten["height"] < MIN_TIPPFLAECHE:
            befunde.append(f"#{knopf_id} nur {kasten['height']:.0f} px hoch "
                           f"(mindestens {MIN_TIPPFLAECHE})")
    d = await seite.locator("#download").bounding_box()
    s = await seite.locator("#share").bounding_box()
    if d and s and abs(d["y"] - s["y"]) > 4:
        befunde.append("Schaltflaechen stehen nicht nebeneinander")

    # 3. Beschriftungen tragen Text (i18n-Ausfall faellt sonst nicht auf)
    for knopf_id in ("download", "share"):
        txt = (await seite.inner_text(f"#{knopf_id}")).strip()
        if not txt:
            befunde.append(f"#{knopf_id} ohne Beschriftung")

    # 4. Vorschau zeigt tatsaechlich etwas.
    #
    # Die erste Fassung dieser Pruefung mass nur die Hoehe des Rahmens und
    # meldete "bestanden", waehrend die Flaeche leer war. Geometrie allein sagt
    # nichts darueber, ob etwas zu sehen ist - deshalb wird jetzt der Inhalt
    # geprueft: geladene Bildmasse und die Farbstreuung der Flaeche.
    sichtbar = await seite.evaluate(
        "!document.body.classList.contains('kein-embed')")
    if not sichtbar:
        befunde.append("Vorschau faellt auf den Ersatztext zurueck")
    else:
        masse = await seite.evaluate("""() => {
            const b = document.getElementById('bild');
            return { w: b.naturalWidth, h: b.naturalHeight,
                     dargestellt: b.getBoundingClientRect().height };
        }""")
        if not masse["w"] or not masse["h"]:
            befunde.append("Vorschaubild wurde nicht geladen (naturalWidth 0)")
        elif masse["dargestellt"] < 200:
            befunde.append(f"Vorschau nur {masse['dargestellt']:.0f} px hoch")

        streuung = await flaechen_streuung(seite, "#bild")
        if streuung is not None and streuung < 3:
            befunde.append(f"Vorschauflaeche wirkt leer "
                           f"(Farbstreuung {streuung:.1f})")

    # 5. Nichts laeuft seitlich aus dem Fenster
    ueberlauf = await seite.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth")
    if ueberlauf > 2:
        befunde.append(f"Seite scrollt {ueberlauf} px waagerecht")

    AUS.mkdir(exist_ok=True)
    ziel = AUS / f"result-{name}.png"
    await seite.screenshot(path=str(ziel))
    await browser.close()
    return befunde + fehler, ziel


async def main():
    from playwright.async_api import async_playwright
    alle = []
    async with async_playwright() as pw:
        for name, b, h, dunkel in FAELLE:
            befunde, ziel = await pruefe(pw, name, b, h, dunkel)
            marke = "OK  " if not befunde else "FEHL"
            print(f"[{marke}] {name} ({b}x{h})  -> {ziel.name}")
            for f in befunde:
                print(f"         {f}")
            alle += befunde
    print()
    if alle:
        print(f"{len(alle)} Beanstandung(en).")
        return 1
    print("Alle Faelle bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
