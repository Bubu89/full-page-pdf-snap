#!/usr/bin/env python3
"""site-visual-check.py — prueft die Website so, wie ein Besucher sie sieht.

Warum es das gibt: Am 01.08.2026 standen auf der Produktseite drei leere
Bildrahmen und ein Screenshot mit dem falschen Tastenkuerzel. Beides war im
HTML nicht zu sehen — die Bilder lieferten HTTP 200, das Kuerzel stand in einer
PNG-Datei. Gefunden wurde es erst, weil jemand die Seite ausgedruckt und
hingeschaut hat.

Diese Pruefung rendert jede Seite in echtem Chrome, liest sie per OCR zurueck
und vergleicht gegen Erwartungen. Sie findet damit drei Klassen von Fehlern,
die HTML-Pruefungen entgehen:

  1. Text, der im Quelltext steht, aber nicht sichtbar wird (Layout, CSS, Farbe)
  2. Bilder, die nicht laden oder keine Hoehe bekommen
  3. Falsche Inhalte INNERHALB von Bildern — Tastenkuerzel, Versionsnummern

    python3 site-visual-check.py                 # alle Seiten
    python3 site-visual-check.py --seite tools   # nur eine
    python3 site-visual-check.py --bericht       # Markdown-Protokoll schreiben

Exitcode 1, wenn eine Erwartung verletzt ist — fuer den Einsatz nach jedem
Deployment.
"""
import argparse, json, re, shutil, subprocess, sys, time, urllib.request
from pathlib import Path

BASIS = "https://provinglab.dev"
CHROME = "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
PORT = 9226
HIER = Path(__file__).resolve().parent
AUSGABE = HIER / "_visual-check"

# --- Was auf jeder Seite SICHTBAR sein muss ----------------------------------
# "text": muss im OCR-Ergebnis auftauchen
# "nicht": darf NICHT auftauchen (haeufigste Fehlerquelle: alte Kuerzel)
# "bilder": Mindestzahl nicht-leerer Bildflaechen
SEITEN = {
    "": {
        "name": "Startseite",
        "text": ["Proving Lab", "Measurements", "Notes", "Tools"],
        "nicht": [],
        "bilder": 0,
    },
    "tools/full-page-pdf-snap/": {
        "name": "Produktseite",
        "text": ["Full Page PDF Snap", "Install", "activeTab", "qualified electronic document"],
        # "APK" allein waere falsch: die Seite sagt legitim "there is no Android APK".
        # Geprueft wird das FALSCHE Kuerzel und ein Versprechen, das es nicht gibt.
        "nicht": ["Ctrl+Shift+Y", "Download APK", "APK herunterladen"],
        "bilder": 3,
    },
    "measurements/webpage-to-pdf-for-ocr/": {
        "name": "OCR-Messung",
        "text": ["92.6", "150 dpi", "personal report", "Questions"],
        "nicht": [],
        "bilder": 0,
    },
    "measurements/pdf-extension-permissions/": {
        "name": "Berechtigungen",
        "text": ["personal report", "all_urls", "1 August 2026"],
        "nicht": [],
        "bilder": 0,
    },
    "about/": {
        "name": "Offenlegung",
        "text": ["Proving Lab", "non-commercial", "Silence"],
        "nicht": [],
        "bilder": 0,
    },
}


def chrome_starten():
    if not Path(CHROME).exists():
        sys.exit(f"Chrome nicht gefunden: {CHROME}")
    # Profil verwerfen. Ohne das liefert Chrome aus dem Cache und die Pruefung
    # bewertet einen alten Stand — am 01.08. zeigte sie deshalb leere Bilder und
    # ein altes Layout, obwohl beides live in Ordnung war.
    import shutil as _sh
    _sh.rmtree("/mnt/c/Temp/pdfsnap-vischeck", ignore_errors=True)
    # Profil muss ein Windows-Pfad sein — Chrome laeuft dort, nicht in WSL.
    p = subprocess.Popen([CHROME, "--headless=new", "--disable-gpu",
                          f"--remote-debugging-port={PORT}",
                          "--user-data-dir=C:\\Temp\\pdfsnap-vischeck",
                          "--no-first-run", "--hide-scrollbars",
                          "--window-size=1280,2400", "about:blank"],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    for _ in range(40):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json/version", timeout=1)
            return p
        except Exception:
            time.sleep(0.5)
    p.terminate()
    sys.exit("Chrome antwortet nicht auf dem Debug-Port")


def seite_aufnehmen(page, pfad, ziel):
    """Volle Seite als PNG ueber CDP.

    Nicht ueber `chrome --screenshot=<pfad>`: Chrome ist hier die Windows-
    Anwendung und kann mit einem WSL-Pfad nichts anfangen — die Datei entsteht
    schlicht nie. Playwright empfaengt die Bilddaten ueber das Protokoll und
    schreibt sie selbst, deshalb funktioniert der Pfad dort.
    """
    # Cache-Buster: sonst greift trotz frischem Profil der CDN-Zwischenspeicher
    trenner = "&" if "?" in pfad else "?"
    page.goto(f"{BASIS}/{pfad}{trenner}_vc={int(time.time())}",
              wait_until="networkidle", timeout=45000)
    # Bilder brauchen einen Moment, sonst misst man leere Rahmen —
    # genau der Fehler, den diese Pruefung finden soll.
    # Auf tatsaechlich dekodierte Bilder warten, nicht auf eine Wartezeit hoffen
    try:
        page.wait_for_function(
            "Array.from(document.images).every(i => i.complete && i.naturalHeight > 0)",
            timeout=20000)
    except Exception:
        pass
    page.wait_for_timeout(800)
    page.screenshot(path=str(ziel), full_page=True)
    return ziel.exists() and ziel.stat().st_size > 5000


def ocr(bild):
    if not shutil.which("tesseract"):
        return ""
    aus = bild.with_suffix("")
    subprocess.run(["tesseract", str(bild), str(aus), "--psm", "6"],
                   capture_output=True, env={"OMP_THREAD_LIMIT": "1", "PATH": "/usr/bin:/bin"},
                   timeout=300)
    txt = aus.with_suffix(".txt")
    return txt.read_text(encoding="utf-8", errors="ignore") if txt.exists() else ""


def bildflaechen_zaehlen(bild, mindest_hoehe=80):
    """Zaehlt zusammenhaengende Flaechen, die sich vom Hintergrund abheben.

    Ein leerer Bildrahmen hat die Hintergrundfarbe — er zaehlt hier nicht mit.
    Damit faellt genau der Fehler auf, der am 01.08. unbemerkt live ging.
    """
    try:
        from PIL import Image
        import statistics
    except ImportError:
        return -1
    im = Image.open(bild).convert("L")
    b, h = im.size
    px = im.load()
    hintergrund = statistics.median([px[b // 2, y] for y in range(0, h, max(1, h // 200))])
    flaechen, lauf = 0, 0
    for y in range(0, h, 4):
        zeile = [px[x, y] for x in range(0, b, max(1, b // 60))]
        abweichend = sum(1 for v in zeile if abs(v - hintergrund) > 28)
        if abweichend > len(zeile) * 0.45:
            lauf += 4
        else:
            if lauf >= mindest_hoehe:
                flaechen += 1
            lauf = 0
    if lauf >= mindest_hoehe:
        flaechen += 1
    return flaechen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seite", help="nur Seiten, deren Pfad diesen Text enthaelt")
    ap.add_argument("--bericht", action="store_true", help="Markdown-Protokoll schreiben")
    a = ap.parse_args()

    AUSGABE.mkdir(exist_ok=True)
    auswahl = {k: v for k, v in SEITEN.items() if not a.seite or a.seite in k}
    print(f"Visuelle Pruefung von {len(auswahl)} Seiten\n")

    proc = chrome_starten()
    from playwright.sync_api import sync_playwright
    pw = sync_playwright().start()
    browser = pw.chromium.connect_over_cdp(f"http://127.0.0.1:{PORT}")
    ctx = browser.contexts[0]
    page = ctx.pages[0] if ctx.pages else ctx.new_page()
    page.set_viewport_size({"width": 1280, "height": 2400})

    ergebnisse, fehler_gesamt = [], 0
    for pfad, erw in auswahl.items():
        name = erw["name"]
        png = AUSGABE / (pfad.strip("/").replace("/", "_") or "start")
        png = png.with_suffix(".png")
        print(f"  {name} …", end=" ", flush=True)

        if not seite_aufnehmen(page, pfad, png):
            print("AUFNAHME FEHLGESCHLAGEN")
            ergebnisse.append((name, pfad, ["Aufnahme fehlgeschlagen"], 0)); fehler_gesamt += 1
            continue

        text = ocr(png)
        flaechen = bildflaechen_zaehlen(png)
        maengel = []
        for t in erw["text"]:
            # OCR verwechselt haeufig O/0 und I/l — tolerant vergleichen
            weich = re.sub(r"[O0]", "[O0]", re.escape(t))
            weich = re.sub(r"[Il1]", "[Il1]", weich)
            if not re.search(weich, text, re.I):
                maengel.append(f"fehlt sichtbar: „{t}“")
        for t in erw["nicht"]:
            if re.search(re.escape(t), text, re.I):
                maengel.append(f"darf nicht vorkommen: „{t}“")
        if erw["bilder"] and 0 <= flaechen < erw["bilder"]:
            maengel.append(f"nur {flaechen} sichtbare Bildflaechen, erwartet {erw['bilder']}")

        if maengel:
            print(f"{len(maengel)} Befund(e)")
            for m in maengel:
                print(f"      - {m}")
            fehler_gesamt += len(maengel)
        else:
            print("in Ordnung")
        ergebnisse.append((name, pfad, maengel, flaechen))

    if a.bericht:
        heute = time.strftime("%Y-%m-%d %H:%M")
        z = ["# Visuelle Pruefung", "", f"Stand: {heute}", "",
             "| Seite | Ergebnis | Bildflaechen |", "|---|---|---|"]
        for name, pfad, m, f in ergebnisse:
            z.append(f"| [{name}]({BASIS}/{pfad}) | {'OK' if not m else '; '.join(m)} | {f} |")
        z += ["", "Aufnahmen liegen in `_visual-check/`.",
              "", "Methode: Seite in echtem Chrome gerendert, per Tesseract zurueckgelesen,",
              "gegen Erwartungen verglichen. Findet Fehler, die im HTML unsichtbar sind —",
              "nicht geladene Bilder, falsche Inhalte in Grafiken, unsichtbaren Text."]
        (AUSGABE / "bericht.md").write_text("\n".join(z), encoding="utf-8")
        print(f"\n  Protokoll: {AUSGABE / 'bericht.md'}")

    browser.close(); pw.stop()
    try: proc.terminate()
    except Exception: pass

    print(f"\n  {len(auswahl)} Seiten geprueft, {fehler_gesamt} Befund(e)")
    return 1 if fehler_gesamt else 0


if __name__ == "__main__":
    sys.exit(main())
