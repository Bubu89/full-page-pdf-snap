#!/usr/bin/env python3
"""Fensterlos: Store-Installation, Deinstallation und Nutzer-Puls — garantiert
ohne ein einziges Fenster, auf keinem Display.

    headless-agent-install.py firefox install
    headless-agent-install.py firefox uninstall
    headless-agent-install.py firefox run [--minuten 5]
    headless-agent-install.py chromium install|uninstall|run
    headless-agent-install.py both verify --json

Warum dieser Weg und kein anderer (alles 2026-08-03/04 gemessen, siehe
protokoll-agent-install.md):

- Sichtbare Klicks (SendInput) funktionieren, stehlen aber Fokus und Maus.
- PostMessage direkt ans Fenster verwerfen Firefox wie Chrome.
- Xvfb + XTEST waere unsichtbar, aber das offizielle Firefox 153 mappt in
  dieser WSL kein Fenster (Inhalts-Sandbox mit chroot), und der User sah
  Rest-Dialoge — unerwuenschte Sichtbarkeit ist ein K.-o.-Kriterium.
- Bleibt der Weg, der konstruktiv kein Fenster hat: MOZ_HEADLESS /
  --headless=new. Dort gibt es keine Eingabe-Ebene, also keine Klicks —
  aber die braucht es nicht, weil beide Browser die Installation per
  Mechanismus selbst erledigen:

  Firefox:  distribution/policies.json -> ExtensionSettings
            normal_installed = installieren, blocked = deinstallieren
  Chromium: <install>/extensions/<id>.json mit external_update_url =
            installieren; Datei weg = deinstallieren

Die Installation ist eine echte Store-Installation: der Browser laedt die
signierte Datei vom Store und meldet sich fortan beim Update-Dienst. Der
Modus `run` startet die Profile nur, damit dieser Update-Puls laeuft —
das ist der Mechanismus, der in den Store-Statistiken als aktiver Nutzer
zaehlt (AMO: Telemetry/Update-Ping; CWS: Update-Check der letzten Woche).

Verifikation ausschliesslich ueber Dateien. Jede Aktion landet als JSONL in
_headless-lauf/aktionen-*.jsonl — der Lauf ist damit wiederholbar und
belegbar. Eine Capture (Alt+Shift+Y) ist hier bewusst NICHT dabei: ohne
Eingabe-Ebene gibt es keine Geste, die activeTab erteilt (gemessen). Dafuer
steht die Xvfb/XTEST-Route im Protokoll.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

HIER = Path(__file__).resolve().parent
ARBEIT = HIER / "_headless-lauf"
FF_DIR = Path.home() / "tools/firefox-release"
FF_EXE = FF_DIR / "firefox"
FF_POLICIES = FF_DIR / "distribution/policies.json"
CH_DIR = Path.home() / ".cache/ms-playwright/chromium-1208/chrome-linux64"
CH_EXE = CH_DIR / "chrome"
CH_EXTDIR = CH_DIR / "extensions"
GECKO_ID = "pageshot-pdf@bubu89.local"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
CWS_UPDATE = "https://clients2.google.com/service/update2/crx"
AMO_API = "https://addons.mozilla.org/api/v5/addons/addon/full_page_pdf_snap_webpagesave/"
FF_PROFIL = Path("/tmp/pl-hl/ff-prof")
CH_PROFIL = Path("/tmp/pl-hl/ch-prof")

LOG = None


def log(aktion, **details):
    eintrag = {"ts": datetime.now(timezone.utc).isoformat(timespec="milliseconds"),
               "aktion": aktion, **details}
    LOG.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    LOG.flush()
    print(f"  [{eintrag['ts'][11:19]}] {aktion} {json.dumps(details, ensure_ascii=False)[:110]}")


def amo_xpi():
    req = urllib.request.Request(AMO_API, headers={"User-Agent": "provinglab-headless/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    cv = d["current_version"]
    return cv["file"]["url"].split("?")[0], cv["version"]


# --- Firefox: policies.json ---------------------------------------------------

def ff_policy_schreiben(modus, xpi_url):
    """normal_installed installiert (entfernbar), blocked deinstalliert und
    sperrt. Fremde Eintraege in derselben Datei bleiben unangetastet."""
    bestand = {}
    if FF_POLICIES.exists():
        bestand = json.loads(FF_POLICIES.read_text(encoding="utf-8") or "{}")
    einstellungen = bestand.setdefault("policies", {}).setdefault("ExtensionSettings", {})
    if modus == "weg":
        einstellungen.pop(GECKO_ID, None)
    else:
        einstellungen[GECKO_ID] = {"installation_mode": modus, "install_url": xpi_url}
    FF_POLICIES.parent.mkdir(parents=True, exist_ok=True)
    FF_POLICIES.write_text(json.dumps(bestand, indent=2), encoding="utf-8")
    log("ff-policy", modus=modus)


# --- Chromium: external extension --------------------------------------------

def ch_marker_schreiben(an):
    ziel = CH_EXTDIR / f"{CWS_ID}.json"
    aus = CH_EXTDIR / f"{CWS_ID}.json.disabled"
    CH_EXTDIR.mkdir(parents=True, exist_ok=True)
    if an:
        if aus.exists():
            aus.rename(ziel)
        else:
            ziel.write_text(json.dumps({"external_update_url": CWS_UPDATE}), encoding="utf-8")
    else:
        # Verschieben statt loeschen — Rueckbau ohne Datenverlust.
        if ziel.exists():
            ziel.rename(aus)
    log("ch-marker", an=an)


# --- Start/Stop (fensterlos) --------------------------------------------------

def starte(browser):
    FF_PROFIL.mkdir(parents=True, exist_ok=True)
    CH_PROFIL.mkdir(parents=True, exist_ok=True)
    if browser == "firefox":
        env = dict(os.environ, MOZ_HEADLESS="1")
        argv = [str(FF_EXE), "-no-remote", "-profile", str(FF_PROFIL), "about:blank"]
    else:
        env = dict(os.environ)
        argv = [str(CH_EXE), "--headless=new", f"--user-data-dir={CH_PROFIL}",
                "--no-first-run", "--no-default-browser-check", "about:blank"]
    p = subprocess.Popen(argv, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         start_new_session=True)
    log("start", browser=browser, pid=p.pid, headless=True)
    return p


def stoppe(p):
    # SIGTERM, kein SIGKILL: ein harter Abbruch zwischen Install und sauberem
    # Shutdown liess die Firefox-Installation schon einmal verschwinden.
    try:
        os.killpg(p.pid, signal.SIGTERM)
        p.wait(timeout=20)
    except Exception:
        pass
    log("stopp", pid=p.pid)


def poll(fn, sekunden, intervall=2):
    ende = time.time() + sekunden
    while time.time() < ende:
        v = fn()
        if v:
            return v
        time.sleep(intervall)
    return None


def ff_version():
    datei = FF_PROFIL / "extensions.json"
    if not datei.exists():
        return None
    try:
        daten = json.loads(datei.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    for a in daten.get("addons", []):
        if a.get("id") == GECKO_ID and a.get("active"):
            return a.get("version")
    return None


def ch_version():
    basis = CH_PROFIL / "Default" / "Extensions" / CWS_ID
    if not basis.exists():
        return None
    for vd in sorted(basis.iterdir(), reverse=True):
        if (vd / "manifest.json").exists():
            return vd.name
    return None


# --- Phasen -------------------------------------------------------------------

def install(browser):
    xpi, store_version = amo_xpi()
    log("store-stand", version=store_version)
    if browser == "firefox":
        ff_policy_schreiben("normal_installed", xpi)
        pruefer = ff_version
    else:
        ch_marker_schreiben(True)
        pruefer = ch_version
    p = starte(browser)
    version = poll(pruefer, 90)
    stoppe(p)
    ok = bool(version)
    log("install-verifiziert", browser=browser, version=version, ok=ok)
    return ok


def uninstall(browser):
    xpi, _ = amo_xpi()
    if browser == "firefox":
        ff_policy_schreiben("blocked", xpi)
        weg = lambda: ff_version() is None
    else:
        ch_marker_schreiben(False)
        weg = lambda: ch_version() is None
    p = starte(browser)
    ok = poll(weg, 90)
    stoppe(p)
    if browser == "firefox":
        ff_policy_schreiben("weg", xpi)  # Sperre nicht stehen lassen
    log("deinstall-verifiziert", browser=browser, ok=bool(ok))
    return bool(ok)


def run(browser, minuten):
    """Der Nutzer-Puls: Profil laeuft, Browser meldet sich beim Update-Dienst.
    Fensterlos, CPU-arm, nach N Minuten sauber beendet."""
    p = starte(browser)
    ende = time.time() + minuten * 60
    while time.time() < ende:
        time.sleep(5)
        if p.poll() is not None:
            log("frueh-beendet", browser=browser, rc=p.returncode)
            p = starte(browser)
    stoppe(p)
    stand = ff_version() if browser == "firefox" else ch_version()
    log("run-ende", browser=browser, installiert=stand, ok=bool(stand))
    return bool(stand)


def verify(browser):
    ziele = ["firefox", "chromium"] if browser == "both" else [browser]
    ergebnis = {}
    for z in ziele:
        ergebnis[z] = ff_version() if z == "firefox" else ch_version()
        log("verify", browser=z, version=ergebnis[z])
    return ergebnis


def main():
    global LOG
    p = argparse.ArgumentParser()
    p.add_argument("browser", choices=["firefox", "chromium", "both"])
    p.add_argument("phase", choices=["install", "uninstall", "run", "verify", "all"])
    p.add_argument("--minuten", type=float, default=5)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    ARBEIT.mkdir(exist_ok=True)
    LOG = (ARBEIT / f"aktionen-{datetime.now().strftime('%Y%m%d-%H%M%S')}.jsonl").open(
        "a", encoding="utf-8")
    log("lauf-beginn", browser=args.browser, phase=args.phase)
    t0 = time.time()

    ziele = ["firefox", "chromium"] if args.browser == "both" else [args.browser]
    ok = True
    for z in ziele:
        if args.phase in ("install", "all"):
            ok = install(z) and ok
        if args.phase == "uninstall":
            ok = uninstall(z) and ok
        if args.phase in ("run", "all"):
            ok = run(z, args.minuten) and ok
    if args.phase == "verify" or args.json:
        ergebnis = verify(args.browser)
        if args.json:
            (ARBEIT / "stand.json").write_text(json.dumps(
                {"ts": datetime.now(timezone.utc).isoformat(), "stand": ergebnis},
                indent=2), encoding="utf-8")

    log("lauf-ende", sekunden=round(time.time() - t0, 1), ok=ok)
    LOG.close()
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
