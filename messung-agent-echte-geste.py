#!/usr/bin/env python3
"""Der positive Beweis: mit einer echten Eingabe loest ein Agent die Erweiterung aus.

    python3 messung-agent-echte-geste.py

Die Gegenprobe zu `messung-agent-nutzt-erweiterung.py`. Dort wurde gemessen,
dass ein Agent, der nur das Dokument steuert, die Erweiterung **nicht** ausloesen
kann: sie fuehrt `activeTab` und keine Host-Rechte, und ohne echte Nutzergeste
bleiben Adresse und Titel jedes Tabs leer.

Hier wird die andere Haelfte gemessen. Statt eines Klicks im Dokument erzeugt
das Programm eine echte Eingabe auf Ebene des Fenstersystems — dasselbe, was
ein Computer-Use-Modell tut, wenn es Maus und Tastatur des Rechners bedient,
und was xdotool-gestuetzte Agenten tun, wenn sie das Symbol einer Erweiterung
anklicken. Fuer den X-Server ist dieses Ereignis von einem Tastendruck des
Menschen nicht unterscheidbar; genau darauf beruht die Aussage.

Kein Netzwerkzugriff, kein fremder Dienst: XTEST ist eine Erweiterung des
X-Servers, die synthetische Eingaben in denselben Weg einspeist, den echte
Geraete nehmen.
"""
import json
import re
import subprocess
import tempfile
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
ERWEITERUNG = HIER / "chrome-mv3"
ZIEL = HIER / "docs" / "data" / "2026-08-03-agent-real-gesture.json"
PROBESEITE = "https://provinglab.dev/measurements/reading-list-to-bibliography/"


def schritt(name, ok, detail=""):
    print(f"  {'OK ' if ok else '-- '} {name:38} {detail}")
    return {"step": name, "passed": bool(ok), "detail": detail}


def chromium():
    treffer = sorted(Path.home().glob(".cache/ms-playwright/chromium-*/chrome-linux*/chrome"))
    return treffer[-1]


def taste_senden(anzeige, kombination):
    """Alt+Shift+Y ueber XTEST — auf demselben Weg wie eine echte Tastatur."""
    from Xlib import X, XK
    from Xlib.ext import xtest

    def code(name):
        return anzeige.keysym_to_keycode(XK.string_to_keysym(name))

    halten = [code(n) for n in kombination[:-1]]
    letzte = code(kombination[-1])
    for k in halten:
        xtest.fake_input(anzeige, X.KeyPress, k)
    xtest.fake_input(anzeige, X.KeyPress, letzte)
    anzeige.sync()
    time.sleep(0.05)
    xtest.fake_input(anzeige, X.KeyRelease, letzte)
    for k in reversed(halten):
        xtest.fake_input(anzeige, X.KeyRelease, k)
    anzeige.sync()


def fenster_nach_vorn(anzeige, teil="Proving Lab"):
    """Das Browserfenster fokussieren — ohne Fokus geht die Eingabe ins Leere."""
    from Xlib import X
    wurzel = anzeige.screen().root
    NET_NAME = anzeige.intern_atom("_NET_WM_NAME")
    NET_ACTIVE = anzeige.intern_atom("_NET_ACTIVE_WINDOW")

    def suchen(fenster, tiefe=0):
        try:
            name = fenster.get_full_property(NET_NAME, 0)
            titel = name.value.decode("utf-8", "replace") if name else (fenster.get_wm_name() or "")
        except Exception:
            titel = ""
        # "Chromium clipboard" und aehnliche Hilfsfenster tragen zwar den
        # Programmnamen, nehmen aber keine Eingaben entgegen. Deshalb ueber den
        # Seitentitel gehen und Fenster ohne Ausdehnung verwerfen.
        if titel and teil.lower() in titel.lower():
            try:
                g = fenster.get_geometry()
                if g.width > 300 and g.height > 300:
                    return fenster, titel
            except Exception:
                pass
        if tiefe > 3:
            return None, ""
        try:
            for k in fenster.query_tree().children:
                t, n = suchen(k, tiefe + 1)
                if t:
                    return t, n
        except Exception:
            pass
        return None, ""

    fenster, titel = suchen(wurzel)
    if not fenster:
        return None
    from Xlib.protocol import event
    e = event.ClientMessage(window=fenster, client_type=NET_ACTIVE, data=(32, [1, 0, 0, 0, 0]))
    wurzel.send_event(e, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
    anzeige.sync()
    time.sleep(0.4)
    try:
        fenster.configure(stack_mode=X.Above)
        anzeige.sync()
        fenster.set_input_focus(X.RevertToParent, X.CurrentTime)
        anzeige.sync()
    except Exception:
        # Manche Fenstermanager verweigern den direkten Fokus; der
        # _NET_ACTIVE_WINDOW-Weg oben hat dann bereits gewirkt.
        pass
    time.sleep(0.6)
    return titel


def main():
    from Xlib import display
    from playwright.sync_api import sync_playwright

    ergebnisse = []
    profil = tempfile.mkdtemp(prefix="geste-")
    ablage = Path(tempfile.mkdtemp(prefix="geste-dl-"))
    anzeige = display.Display()
    ergebnisse.append(schritt("X server with XTEST", bool(anzeige.query_extension("XTEST").present),
                              f"{anzeige.get_display_name()}, "
                              f"{anzeige.screen().width_in_pixels}x{anzeige.screen().height_in_pixels}"))

    pdf, kurz = None, ""
    with sync_playwright() as p:
        ctx = p.chromium.launch_persistent_context(
            profil, executable_path=str(chromium()),
            headless=False,               # sichtbar: eine Eingabe braucht ein Fenster
            args=[f"--disable-extensions-except={ERWEITERUNG}",
                  f"--load-extension={ERWEITERUNG}",
                  "--no-first-run", "--no-default-browser-check",
                  "--window-size=1400,1000", "--window-position=40,40"],
            accept_downloads=True, downloads_path=str(ablage),
            viewport={"width": 1400, "height": 900},
        )
        seite = ctx.pages[0] if ctx.pages else ctx.new_page()
        seite.goto(PROBESEITE, wait_until="load", timeout=60000)
        seite.wait_for_timeout(2500)

        # Welcher Tastenbefehl ist registriert?
        verwaltung = ctx.new_page()
        verwaltung.goto("chrome://extensions/shortcuts")
        verwaltung.wait_for_timeout(800)
        verwaltung.close()
        seite.bring_to_front()
        seite.wait_for_timeout(500)

        titel = fenster_nach_vorn(anzeige) or fenster_nach_vorn(anzeige, "Chromium")
        ergebnisse.append(schritt("browser window focused", bool(titel), (titel or "nicht gefunden")[:52]))

        vorher = {f.name for f in ablage.glob("**/*.pdf")} | {
            f.name for f in (Path.home() / "Downloads").glob("*.pdf")}
        beginn = time.time()

        def sichtbare_tabs():
            w = next(iter(ctx.service_workers), None)
            if not w:
                return -1
            try:
                return w.evaluate("""async () => {
                    const alle = await chrome.tabs.query({});
                    return alle.filter(t => t.url && t.url.startsWith("http")).length;
                }""")
            except Exception:
                return -1

        # Die Erweiterung wecken, ohne ihr eine Geste zu geben.
        wecker = ctx.new_page()
        eid = None
        v2 = ctx.new_page(); v2.goto("chrome://extensions/"); v2.wait_for_timeout(800)
        try:
            eid = v2.evaluate("""async () => {
                const r = await new Promise(res => chrome.developerPrivate.getExtensionsInfo(res));
                const x = r.find(y => y.name.includes("PDF Snap"));
                return x && x.id; }""")
        except Exception:
            pass
        v2.close()
        if eid:
            wecker.goto(f"chrome-extension://{eid}/popup.html"); wecker.wait_for_timeout(1200)
        wecker.close()
        seite.bring_to_front(); fenster_nach_vorn(anzeige) or fenster_nach_vorn(anzeige, "Chromium")
        vor_geste = sichtbare_tabs()
        ergebnisse.append(schritt("before the gesture", vor_geste == 0,
                                  f"{vor_geste} Tabs mit Adresse sichtbar"))

        # Die echte Eingabe. Alt+Shift+Y ist der Standardbefehl der Erweiterung.
        taste_senden(anzeige, ["Alt_L", "Shift_L", "y"])
        time.sleep(2.5)
        nach_geste = sichtbare_tabs()
        ergebnisse.append(schritt("after the gesture", nach_geste > 0,
                                  f"{nach_geste} Tabs mit Adresse sichtbar "
                                  f"(vorher {vor_geste})"))

        for _ in range(240):
            treffer = [f for o in (ablage, Path.home() / "Downloads", Path(profil))
                       for f in o.glob("**/*.pdf")
                       if f.name not in vorher and f.stat().st_mtime >= beginn - 5
                       and f.stat().st_size > 1000]
            if treffer:
                pdf = sorted(treffer, key=lambda f: f.stat().st_mtime)[-1]
                break
            time.sleep(0.5)

        # Was meldet die Erweiterung selbst?
        sw = next(iter(ctx.service_workers), None)
        if sw:
            try:
                sichtbar = sw.evaluate("""async () => {
                    const alle = await chrome.tabs.query({});
                    return alle.filter(t => t.url && t.url.startsWith("http")).length;
                }""")
                kurz = f"{sichtbar} Tabs mit Adresse sichtbar"
            except Exception as e:
                kurz = type(e).__name__
        ctx.close()

    roh = pdf.read_bytes() if pdf else b""
    seiten = len(re.findall(rb"/Type\s*/Page[^s]", roh)) if roh else 0
    ergebnisse.append(schritt("extension produced a PDF", roh[:5] == b"%PDF-",
                              f"{pdf.name}, {len(roh)//1024} kB, {seiten} Seiten"
                              if pdf else f"keine Datei ({kurz})"))

    bestanden = sum(1 for e in ergebnisse if e["passed"])
    print(f"\n{bestanden} von {len(ergebnisse)} Schritten bestanden.")

    ZIEL.write_text(json.dumps({
        "measurement": "agent-real-gesture",
        "date": "2026-08-03",
        "question": ("Does a synthetic input event at window-system level — what a computer-use "
                     "model produces — satisfy the activeTab gesture requirement and drive the "
                     "extension to completion?"),
        "method": {
            "display": anzeige.get_display_name(),
            "input": "XTEST fake_input, the same path a physical keyboard takes",
            "keys": "Alt+Shift+Y (the extension's default command)",
            "browser": "Playwright Chromium, headful, extension loaded unpacked",
            "page": PROBESEITE,
            "counterpart": "docs/data/2026-08-03-agent-uses-the-extension.json",
        },
        "results": {"steps_passed": bestanden, "steps_total": len(ergebnisse),
                    "pdf": pdf.name if pdf else None,
                    "pdf_bytes": len(roh) if roh else 0, "pdf_pages": seiten},
        "steps": ergebnisse,
        "license": "CC-BY-4.0",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)}")


if __name__ == "__main__":
    main()
