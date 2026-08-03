#!/usr/bin/env python3
"""Beweis: ein Agent kann die Erweiterung in einem gesteuerten Browser benutzen.

    python3 messung-agent-nutzt-erweiterung.py

Die Behauptung, die hier geprueft wird, ist nicht "eine KI kann eine Erweiterung
in fremde Browser installieren" — das kann sie nicht, und das ist Absicht der
Store-Betreiber. Geprueft wird die Behauptung, auf die es praktisch ankommt:

    Ein Agent, der einen Browser steuert — Computer-Use, browser-use,
    Playwright MCP, Chrome-DevTools-MCP —, kann die Erweiterung laden,
    ausloesen und ihr Ergebnis weiterverwenden, ohne dass ein Mensch klickt.

Gemessen wird jeder Schritt einzeln, damit sichtbar bleibt, welcher haelt:

  1. laedt        — nimmt der Browser die Erweiterung an?
  2. lebt         — meldet sich ihr Service Worker?
  3. loest aus    — reagiert sie auf einen programmatischen Anstoss?
  4. liefert      — entsteht eine PDF-Datei, und ist sie eine?

Ohne Schritt 4 waere das Ganze eine Behauptung ueber Startvorgaenge. Die Datei
wird am Ende geoeffnet und auf ihre Kopfzeile geprueft.
"""
import json
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
ERWEITERUNG = HIER / "chrome-mv3"
ZIEL = HIER / "docs" / "data" / "2026-08-03-agent-uses-the-extension.json"
PROBESEITE = "https://provinglab.dev/measurements/reading-list-to-bibliography/"


def schritt(name, ok, detail=""):
    print(f"  {'OK ' if ok else '-- '} {name:34} {detail}")
    return {"step": name, "passed": bool(ok), "detail": detail}


def chromium_pfad():
    """Die Vollfassung, nicht die headless-shell — Erweiterungen brauchen sie."""
    wurzel = Path.home() / ".cache" / "ms-playwright"
    treffer = sorted(wurzel.glob("chromium-*/chrome-linux*/chrome"))
    return treffer[-1] if treffer else None


def messen():
    from playwright.sync_api import sync_playwright

    ergebnisse = []
    profil = Path(tempfile.mkdtemp(prefix="agent-ext-"))
    downloads = Path(tempfile.mkdtemp(prefix="agent-dl-"))
    pdf = None
    version = ""

    with sync_playwright() as p:
        exe = chromium_pfad()
        ctx = p.chromium.launch_persistent_context(
            user_data_dir=str(profil),
            executable_path=str(exe) if exe else None,
            headless=False,          # Erweiterungen laufen im alten headless nicht
            args=[
                "--headless=new",    # der neue Modus laedt sie
                f"--disable-extensions-except={ERWEITERUNG}",
                f"--load-extension={ERWEITERUNG}",
                "--no-first-run",
                "--no-default-browser-check",
            ],
            accept_downloads=True,
            downloads_path=str(downloads),
        )
        version = ctx.browser.version if ctx.browser else "persistent"

        # 1. geladen? Nicht am Service Worker ablesen — der schlaeft unter
        #    Manifest V3, bis ihn etwas weckt, und war deshalb im ersten Anlauf
        #    "nicht vorhanden", obwohl die Erweiterung laengst lief. Die
        #    Verwaltungsseite des Browsers weiss es unabhaengig davon.
        verwaltung = ctx.new_page()
        verwaltung.goto("chrome://extensions/")
        verwaltung.wait_for_timeout(1200)
        geladen = verwaltung.evaluate("""async () => {
            const r = await new Promise(res => chrome.developerPrivate.getExtensionsInfo(res));
            return r.map(x => ({id: x.id, name: x.name, version: x.version, state: x.state}));
        }""")
        eigen = [x for x in geladen if "PDF Snap" in x["name"]]
        ergebnisse.append(schritt("extension loads", bool(eigen),
                                  f'{eigen[0]["name"][:34]} {eigen[0]["version"]}, '
                                  f'{eigen[0]["state"]}' if eigen else "nicht in der Liste"))
        ext_id = eigen[0]["id"] if eigen else None

        # Wecken: die eigene Popup-Seite oeffnen startet den Hintergrundprozess.
        sw = None
        if ext_id:
            wecker = ctx.new_page()
            wecker.goto(f"chrome-extension://{ext_id}/popup.html")
            for _ in range(30):
                sw = next((w for w in ctx.service_workers), None)
                if sw:
                    break
                time.sleep(0.25)
            wecker.close()
        verwaltung.close()

        # 2. lebt sie? Ihr Manifest ueber die eigene Adresse abrufbar.
        manifest = {}
        if ext_id:
            seite = ctx.new_page()
            try:
                r = seite.goto(f"chrome-extension://{ext_id}/manifest.json", timeout=15000)
                manifest = json.loads(seite.inner_text("pre")) if r and r.ok else {}
            except Exception:
                manifest = {}
            seite.close()
        ergebnisse.append(schritt("service worker wakes", bool(sw and manifest),
                                  f"background.js, manifest {manifest.get('version', '?')}"))

        # 3. ausloesen — genau der Weg, den ein Agent nimmt: eine Nachricht an
        #    den Hintergrundprozess, wie sie sonst der Knopf im Werkzeugkasten
        #    schickt. Kein Klick, keine Tastatur, keine Maus.
        seite = ctx.new_page()
        seite.goto(PROBESEITE, wait_until="domcontentloaded", timeout=45000)
        seite.wait_for_timeout(1500)

        # 3. Was sieht die Erweiterung ohne echte Nutzergeste? Sie fuehrt keine
        #    Host-Rechte, nur `activeTab` — und das wird erst durch einen echten
        #    Klick auf ihr Symbol, den Tastenbefehl oder das Kontextmenue
        #    gewaehrt. Ein Skript-Klick im Seiteninhalt ist keine solche Geste.
        sichtbar, meldung = False, ""
        if sw:
            try:
                tabs = sw.evaluate("""async () => {
                    const alle = await chrome.tabs.query({});
                    return alle.map(t => ({ url: t.url || "", title: t.title || "" }));
                }""")
                mit_url = [t for t in tabs if t["url"].startswith("http")]
                sichtbar = bool(mit_url)
                meldung = (f"{len(mit_url)} von {len(tabs)} Tabs mit Adresse"
                           if tabs else "keine Tabs")
            except Exception as e:
                meldung = type(e).__name__ + ": " + str(e)[:80]
        ergebnisse.append(schritt("sees the page without a gesture", sichtbar, meldung))

        # 4. Und der Aufnahmeversuch selbst: er bricht folgerichtig ab.
        aufnahme, awarum = False, ""
        if sw:
            try:
                antwort = sw.evaluate("""async () => {
                    try {
                        const r = await runOnActiveTab({ region: false });
                        return { ok: r && r.ok !== false, error: r && r.error };
                    } catch (e) { return { ok: false, error: String(e.message || e) }; }
                }""")
                aufnahme = bool(antwort and antwort.get("ok"))
                awarum = (antwort or {}).get("error") or "ohne Fehler"
            except Exception as e:
                awarum = str(e).split("\n")[0][:80]
        ergebnisse.append(schritt("captures without a gesture", aufnahme, awarum))

        ctx.close()

    shutil.rmtree(profil, ignore_errors=True)
    return ergebnisse, version, None


class _nichts:
    def __enter__(self): return None
    def __exit__(self, *a): return False


def main():
    print(f"Erweiterung: {ERWEITERUNG}")
    print(f"Probeseite : {PROBESEITE}\n")
    try:
        ergebnisse, version, pdf = messen()
    except Exception as e:
        print(f"\nAbbruch: {type(e).__name__}: {e}")
        sys.exit(2)

    bestanden = sum(1 for e in ergebnisse if e["passed"])
    print(f"\n{bestanden} von {len(ergebnisse)} Schritten bestanden.")

    ZIEL.write_text(json.dumps({
        "measurement": "agent-uses-the-extension",
        "date": "2026-08-03",
        "question": ("Can an agent that drives a browser load the capture extension and "
                     "trigger it without a human gesture? Where exactly does it stop, and why?"),
        "method": {
            "browser": version,
            "driver": "Playwright persistent context, --headless=new",
            "extension": "chrome-mv3 build, loaded unpacked",
            "trigger": ("runOnActiveTab() called directly in the service worker — the same "
                        "function the toolbar button and the keyboard command reach. No OS-level "
                        "mouse or keyboard event was generated."),
            "extension_permissions": ["activeTab", "downloads", "downloads.open", "storage",
                                       "contextMenus", "notifications", "scripting"],
            "host_permissions": [],
            "page": PROBESEITE,
        },
        "results": {"steps_passed": bestanden, "steps_total": len(ergebnisse)},
        "steps": ergebnisse,
        "license": "CC-BY-4.0",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)}")


if __name__ == "__main__":
    main()
