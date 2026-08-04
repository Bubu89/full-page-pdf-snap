#!/usr/bin/env python3
"""Erweiterung installieren und deinstallieren — ohne Klick, ohne Fenster.

    python3 tools/erweiterung-fernsteuern.py status
    python3 tools/erweiterung-fernsteuern.py install
    python3 tools/erweiterung-fernsteuern.py deinstall
    python3 tools/erweiterung-fernsteuern.py rundlauf     # deinstall, install, pruefen
    python3 tools/erweiterung-fernsteuern.py --json rundlauf

Warum nicht ueber die Oberflaeche
---------------------------------
Die Klick-Route (`schnelllauf-agent-install.py`) hat drei Eigenschaften, die
sie fuer einen Agenten unbrauchbar machen. Alle drei am 3. August 2026 gemessen:

  1. **Feste Koordinaten.** Der Lauf dauerte 179 Sekunden und installierte
     nichts. Jeder Klick meldete Erfolg, denn ein Klick ins Leere ist fuer
     Windows ein gueltiger Klick. Eine Route, die bei Misserfolg Erfolg
     meldet, ist schlimmer als keine Route.
  2. **Vordergrund noetig.** Echte Eingabe-Ereignisse gehen an das fokussierte
     Fenster. Wer sie sendet, uebernimmt Maus und Tastatur des Benutzers.
  3. **Nicht nachbaubar.** Andere Aufloesung, andere Schriftgroesse, andere
     Store-Fassung — andere Koordinaten.

Marionette hat keine davon: der Fernsteuerungs-Kanal, den Firefox selbst
mitbringt (derselbe, den geckodriver spricht), laeuft unter `-headless` ohne
jedes Fenster und antwortet auf jeden Befehl mit Erfolg **oder** Fehler.

Was dieser Weg nicht leistet
----------------------------
Eine so installierte Erweiterung zaehlt **nicht** in der Nutzerstatistik des
Stores — Marionette installiert die Datei, es besucht keine Store-Seite. Die
XPI stammt trotzdem aus dem Store und ist von Mozilla signiert: dieselbe
Datei, nur ohne den Klick, der sie zaehlt. Wer gezaehlt werden will, braucht
die Oberflaeche; siehe `install-as-a-counted-user.md`.

Die Richtlinien-Route scheidet auf dieser Maschine in **beide** Richtungen
aus, gemessen am 3. August 2026: `C:\\Program Files\\Mozilla FirefoxESR\\
distribution` ist nicht beschreibbar, `HKCU\\Software\\Policies` ist
ACL-geschuetzt. Ohne Administratorrechte kann eine Richtlinie weder
installieren noch entfernen. Marionette braucht keine Rechte ueber die
hinaus, die der Benutzer auf sein eigenes Profil ohnehin hat.

Wo dieses Skript laeuft
-----------------------
Auf der Seite, auf der der Browser laeuft. Firefox bindet Marionette an
`127.0.0.1` — und der Loopback von Windows ist aus WSL2 nicht erreichbar
(gemessen: weder ueber `127.0.0.1` noch ueber die Host-Adresse). Wird das
Skript unter WSL aufgerufen, reicht es sich deshalb selbst an das
Windows-Python weiter. Auf einem gewoehnlichen System entfaellt das.

Das Protokoll
-------------
Laengen-praefixiertes JSON auf einem TCP-Port:

    41:[0,1,"WebDriver:NewSession",{}]
    ^^ Bytes   ^ 0 = Befehl

Antwort `[1, id, fehler, ergebnis]`. Steht in `fehler` etwas, ist der Befehl
nachweislich gescheitert — nicht vermutlich.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ID = "pageshot-pdf@bubu89.local"
AMO_API = "https://addons.mozilla.org/api/v5/addons/addon/full_page_pdf_snap_webpagesave/"
KENNUNG = "provinglab-install/1.0 (+https://provinglab.dev/for-agents/)"
PORT = 2828
PROTOKOLL = []

# Reihenfolge ist Absicht: ESR zuerst, weil auf der Messmaschine nur ESR lag
# und ein Probieren des gewoehnlichen Pfades zuerst „Firefox nicht gefunden"
# meldete, waehrend Firefox lief. Benutzer-Installationen stehen mit drin —
# ohne Administratorrechte installiert Firefox nach %LOCALAPPDATA%, und genau
# dort sucht eine Liste aus Program-Files-Pfaden nie.
FF_KANDIDATEN = [
    r"C:\Program Files\Mozilla FirefoxESR\firefox.exe",
    r"C:\Program Files\Mozilla Firefox\firefox.exe",
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Mozilla Firefox\firefox.exe"),
    os.path.expandvars(r"%LOCALAPPDATA%\Programs\Mozilla Firefox\firefox.exe"),
    "/usr/bin/firefox", "/usr/bin/firefox-esr",
    "/usr/lib/firefox/firefox", "/usr/lib/firefox-esr/firefox-esr",
    "/usr/local/bin/firefox",
    "/snap/bin/firefox",
    "/var/lib/flatpak/exports/bin/org.mozilla.firefox",
    str(Path.home() / ".local/share/flatpak/exports/bin/org.mozilla.firefox"),
    "/Applications/Firefox.app/Contents/MacOS/firefox",
    str(Path.home() / "Applications/Firefox.app/Contents/MacOS/firefox"),
]

UNTER_WSL = sys.platform == "linux" and Path("/mnt/c/Windows").exists()


UHR = [time.time()]


def schritt(name, ok, detail=""):
    dauer = round(time.time() - UHR[0], 2)
    UHR[0] = time.time()
    PROTOKOLL.append({"schritt": name, "ok": bool(ok), "sekunden": dauer,
                      "detail": detail})
    print(f"  {'OK ' if ok else '-- '} {name:32} {dauer:6.2f}s  {detail}", flush=True)
    return ok


# ----------------------------------------------------- WSL-Weiterreichung

def _win_python():
    """Der Windows-Interpreter heisst nicht ueberall gleich.

    Eine Installation aus dem Microsoft Store legt `python.exe` in den
    Suchpfad, eine aus dem Installer oft nur `py.exe`. Wer nur den einen
    Namen probiert, bekommt auf der Haelfte der Rechner „not recognized"
    und sucht den Fehler beim Skript.
    """
    for name in ("python.exe", "py.exe"):
        r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                            f"(Get-Command {name} -EA SilentlyContinue).Source"],
                           capture_output=True, text=True, errors="replace")
        if r.stdout.strip():
            return name
    raise SystemExit("Kein Windows-Python gefunden (weder python.exe noch py.exe). "
                     "Ohne das kann der Marionette-Client nicht auf der Seite "
                     "des Browsers laufen.")


def an_windows_weiterreichen():
    """Das Skript nach %TEMP% kopieren und dort mit dem Windows-Python starten.

    Kopiert statt ueber `\\\\wsl.localhost` aufgerufen: der UNC-Pfad
    funktioniert, aber Windows-Python legt daneben ein `__pycache__` im
    WSL-Baum an und meldet auf stderr eine UNC-Warnung in der Windows-
    Codepage — die bricht das Dekodieren der Ausgabe ab.
    """
    ziel_w = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                             "$env:TEMP"], capture_output=True, text=True,
                            errors="replace").stdout.strip()
    ziel = Path(subprocess.run(["wslpath", "-u", ziel_w], capture_output=True,
                               text=True, check=True).stdout.strip())
    kopie = ziel / "erweiterung-fernsteuern.py"
    kopie.write_bytes(Path(__file__).read_bytes())
    # PYTHONIOENCODING: die Windows-Konsole steht auf einer Codepage, in der
    # Gedankenstrich und Umlaut als Fragezeichen ankommen.
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                        f"$env:PYTHONIOENCODING='utf-8'; "
                        f"{_win_python()} '{ziel_w}\\erweiterung-fernsteuern.py' "
                        + " ".join(sys.argv[1:])],
                       text=True, errors="replace")
    return r.returncode


# ------------------------------------------------------------- Profil/XPI

def firefox_exe():
    eigen = os.environ.get("FIREFOX")
    if eigen and Path(eigen).exists():
        return eigen
    for k in FF_KANDIDATEN:
        if k and Path(k).exists():
            return k
    # Zuletzt der Suchpfad: eine Installation an einer Stelle, die niemand
    # vorhersehen kann, ist immer noch auffindbar, wenn sie im PATH steht.
    for name in ("firefox", "firefox-esr"):
        gefunden = shutil.which(name)
        if gefunden:
            return gefunden
    raise SystemExit(
        "Firefox nicht gefunden. Gesucht wurde an "
        f"{len(FF_KANDIDATEN)} ueblichen Orten und im Suchpfad. "
        "Eigenen Pfad ueber die Umgebungsvariable FIREFOX setzen "
        "oder in FF_KANDIDATEN ergaenzen.")


def profil_pfad():
    """Das Profil, das Firefox beim naechsten Start selbst oeffnen wuerde.

    Aus `profiles.ini` gelesen, nicht geraten: auf dieser Maschine liegen
    sechs Profile nebeneinander, und in ein falsches installiert zu haben
    sieht von aussen genauso aus wie gar nicht installiert zu haben.
    """
    if os.name == "nt":
        basis = Path(os.environ["APPDATA"]) / "Mozilla" / "Firefox"
    elif sys.platform == "darwin":
        basis = Path.home() / "Library" / "Application Support" / "Firefox"
    else:
        basis = Path.home() / ".mozilla" / "firefox"
    ini = (basis / "profiles.ini").read_text(encoding="utf-8", errors="replace")
    for block in ini.split("["):
        if block.startswith("Install"):
            m = re.search(r"^Default=(.+)$", block, re.M)
            if m:
                return basis / m.group(1).strip()
    raise SystemExit("kein Install-Block in profiles.ini — Profil unbestimmbar")


def store_xpi(ziel):
    """Signierte Datei aus dem Store, mit Pruefsumme.

    Nicht selbst gepackt: eine selbst gebaute XPI ist unsigniert, und Firefox
    ausserhalb der Developer Edition lehnt sie ab. Der Fehler lautet dann
    „corrupt" und fuehrt auf die falsche Faehrte.
    """
    req = urllib.request.Request(AMO_API, headers={"user-agent": KENNUNG})
    with urllib.request.urlopen(req, timeout=30) as a:
        d = json.load(a)
    v, f = d["current_version"]["version"], d["current_version"]["file"]
    datei = ziel / f"full-page-pdf-snap-{v}.xpi"
    if not datei.exists():
        req = urllib.request.Request(f["url"], headers={"user-agent": KENNUNG})
        with urllib.request.urlopen(req, timeout=60) as a:
            datei.write_bytes(a.read())
    roh = datei.read_bytes()
    return datei, v, hashlib.sha256(roh).hexdigest()[:16], len(roh)


def installiert(profil):
    """Wahrheit aus der Datei, die Firefox selbst fuehrt — nicht aus der
    Antwort des Befehls. Ein Befehl kann Erfolg melden und nichts hinterlassen."""
    p = profil / "extensions.json"
    if not p.exists():
        return None
    try:
        d = json.loads(p.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    for a in d.get("addons", []):
        if a.get("id") == ID:
            return {"version": a.get("version"), "aktiv": a.get("active"),
                    "quelle": a.get("location")}
    return None


def profil_belegt(profil):
    """Zwei Instanzen auf einem Profil sperren einander aus. Wer hier den
    fremden Firefox abschiesst, kostet den Benutzer seine offenen Reiter —
    deshalb wird gemeldet, nicht beendet.

    Geprueft wird, ob die Sperrdatei **gehalten** wird, nicht ob sie da ist:
    `parent.lock` bleibt nach dem Beenden liegen. Ihre blosse Existenz als
    „belegt" zu lesen, sperrt das Werkzeug dauerhaft aus — am 3. August 2026
    genau so passiert.
    """
    for n in ("parent.lock", ".parentlock"):
        p = profil / n
        if not p.exists():
            continue
        try:
            with open(p, "a"):
                pass
        except (PermissionError, OSError):
            return True
    return False


# ------------------------------------------------------------- Marionette

class Marionette:
    """Firefox' eigener Fernsteuerungs-Kanal. Kein Fremdpaket, kein Treiber —
    ein Socket und zwei Dutzend Zeilen."""

    def __init__(self, port=PORT, timeout=45):
        ende, letzter = time.time() + timeout, None
        while time.time() < ende:
            try:
                self.s = socket.create_connection(("127.0.0.1", port), 5)
                self.s.settimeout(90)
                self._lesen()            # Begruessung des Servers
                self.id = 0
                return
            except OSError as e:
                letzter = e
                time.sleep(0.5)
        raise RuntimeError(f"Marionette antwortet nicht auf Port {port}: {letzter}")

    def _lesen(self):
        laenge = b""
        while not laenge.endswith(b":"):
            z = self.s.recv(1)
            if not z:
                raise OSError("Verbindung waehrend der Laengenangabe geschlossen")
            laenge += z
        rest, puffer = int(laenge[:-1]), b""
        while len(puffer) < rest:
            teil = self.s.recv(rest - len(puffer))
            if not teil:
                raise OSError("Verbindung waehrend der Nutzlast geschlossen")
            puffer += teil
        return json.loads(puffer)

    def ruf(self, befehl, params=None):
        self.id += 1
        roh = json.dumps([0, self.id, befehl, params or {}]).encode()
        self.s.sendall(f"{len(roh)}:".encode() + roh)
        antwort = self._lesen()
        fehler = antwort[2] if len(antwort) > 2 else None
        if fehler:
            raise RuntimeError(fehler.get("message", str(fehler))
                               if isinstance(fehler, dict) else str(fehler))
        return antwort[3] if len(antwort) > 3 else None

    def schliessen(self):
        try:
            self.ruf("Marionette:Quit", {"flags": ["eForceQuit"]})
        except Exception:
            pass
        try:
            self.s.close()
        except OSError:
            pass


def kein_fenster(proc):
    """Bricht ab, sobald der gestartete Browser ein sichtbares Fenster hat.

    „Headless" ist eine Zusage, kein Ergebnis. `-headless` kann fehlen, von
    einer Profileinstellung ueberstimmt werden oder in einer kuenftigen
    Fassung anders heissen — und dann steht ein Fenster auf dem Bildschirm des
    Benutzers, waehrend das Protokoll weiter „unsichtbar" meldet.

    Geprueft wird deshalb der Zustand, nicht die Absicht: existiert zum
    gestarteten Prozess ein Fenster mit einem Handle, wird sofort beendet und
    der Lauf als gescheitert gemeldet. Lieber kein Ergebnis als ein Ergebnis,
    das die Grundbedingung verletzt hat.
    """
    if os.name != "nt" and not UNTER_WSL:
        # X11: ein Fenster existiert nur, wenn ein Display gesetzt ist.
        return os.environ.get("DISPLAY") in (None, "")
    r = subprocess.run(
        ["powershell.exe", "-NoProfile", "-Command",
         f"(Get-Process -Id {proc.pid} -EA SilentlyContinue)."
         "MainWindowHandle"],
        capture_output=True, text=True, errors="replace")
    handle = r.stdout.strip()
    return handle in ("", "0")


def mit_firefox(profil, arbeit):
    """Firefox headless starten, Befehl absetzen, sauber beenden.

    `-no-remote` ist Pflicht: ohne das reicht ein bereits offener Firefox den
    Start an sich selbst weiter, der neue Prozess endet sofort, und Marionette
    kommt nie hoch — das sieht aus wie ein Zeitueberlauf und ist keiner.
    """
    proc = subprocess.Popen(
        [firefox_exe(), "-headless", "-no-remote", "-marionette",
         "-profile", str(profil)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        creationflags=0x08000000 if os.name == "nt" else 0)   # kein Konsolenblitz
    m = None
    try:
        # Erst die Grundbedingung, dann die Arbeit. Ein Lauf, der ein Fenster
        # oeffnet, ist kein langsamer Erfolg — er ist ein Fehlschlag.
        time.sleep(1.5)
        if not kein_fenster(proc):
            proc.kill()
            raise RuntimeError(
                "Der Browser hat ein sichtbares Fenster geoeffnet. Abgebrochen: "
                "unsichtbar zu bleiben ist die Bedingung dieses Wegs, nicht "
                "sein Nebeneffekt.")
        m = Marionette()
        m.ruf("WebDriver:NewSession", {"capabilities": {}})
        return arbeit(m)
    finally:
        if m:
            m.schliessen()
        try:
            proc.wait(timeout=20)
        except subprocess.TimeoutExpired:
            proc.kill()
        time.sleep(1.0)   # Firefox schreibt extensions.json beim Beenden


def main():
    p = argparse.ArgumentParser()
    p.add_argument("aktion", choices=["status", "install", "deinstall", "rundlauf"])
    p.add_argument("--json", action="store_true")
    p.add_argument("--protokoll", metavar="DATEI",
                   help="Rohdaten des Laufs als JSON schreiben")
    a = p.parse_args()

    if UNTER_WSL:
        return an_windows_weiterreichen()

    profil = profil_pfad()
    print(f"Profil: {profil.name}", flush=True)

    if a.aktion == "status":
        z = installiert(profil)
        print("  " + (f"installiert: {z['version']} (aktiv={z['aktiv']}, {z['quelle']})"
                      if z else "nicht installiert"))
        if a.json:
            print(json.dumps({"profil": profil.name, "zustand": z}, indent=2))
        return 0

    if profil_belegt(profil):
        print("  Firefox hat dieses Profil offen. Bitte schliessen — ein zweiter\n"
              "  Start auf demselben Profil scheitert an der Profilsperre.")
        return 2

    xpi, version, summe, groesse = store_xpi(Path(os.environ.get("TEMP", "/tmp")))
    schritt("XPI aus dem Store", True, f"{version}, {groesse} B, sha256:{summe}")

    # Beide Befehle in EINER Sitzung. Firefox zweimal zu starten kostete im
    # ersten Entwurf 4,4 s je Durchgang, also mehr als die Befehle selbst —
    # der Start ist hier der teure Teil, nicht die Arbeit.
    def arbeit(m):
        ergebnis = {}
        if a.aktion in ("deinstall", "rundlauf") and vorher:
            t = time.time()
            m.ruf("Addon:Uninstall", {"id": ID})
            ergebnis["uninstall"] = round(time.time() - t, 2)
        if a.aktion in ("install", "rundlauf"):
            t = time.time()
            ergebnis["install_antwort"] = m.ruf(
                "Addon:Install", {"path": str(xpi), "temporary": False})
            ergebnis["install"] = round(time.time() - t, 2)
        return ergebnis

    vorher = installiert(profil)
    if a.aktion == "deinstall" and not vorher:
        schritt("Addon:Uninstall", True, "war nicht installiert — nichts zu tun")
    else:
        try:
            r = mit_firefox(profil, arbeit)
            nach = installiert(profil)
            if a.aktion in ("deinstall", "rundlauf"):
                if vorher:
                    # Beim Rundlauf ist am Ende wieder installiert; der Beleg
                    # ist deshalb die Antwort des Befehls, nicht der Endstand.
                    schritt("Addon:Uninstall", True,
                            f"{r.get('uninstall')}s, Befehl ohne Fehler quittiert")
                else:
                    schritt("Addon:Uninstall", True, "war nicht installiert")
            if a.aktion in ("install", "rundlauf"):
                schritt("Addon:Install", nach is not None,
                        f"{r.get('install')}s, Profil meldet "
                        f"{nach['version'] if nach else 'nichts'}")
        except (RuntimeError, OSError) as e:
            schritt(f"Addon-Befehl ({a.aktion})", False, str(e)[:70])

    z = installiert(profil)
    print("\nStand: " + (f"v{z['version']} aktiv={z['aktiv']} ({z['quelle']})"
                         if z else "nicht installiert"))
    bericht = {"profil": profil.name, "browser": firefox_exe(),
               "kanal": "marionette", "sichtbares_fenster": False,
               "eingabe_ereignisse": 0, "protokoll": PROTOKOLL, "zustand": z,
               "gesamt_sekunden": round(sum(s["sekunden"] for s in PROTOKOLL), 2)}
    if a.json:
        print(json.dumps(bericht, indent=2, ensure_ascii=False))
    if a.protokoll:
        Path(a.protokoll).write_text(
            json.dumps(bericht, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Protokoll: {a.protokoll}")
    return 0 if all(s["ok"] for s in PROTOKOLL) else 1


if __name__ == "__main__":
    sys.exit(main())
