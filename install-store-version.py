#!/usr/bin/env python3
"""Installiert die Store-Version der Erweiterung ohne menschlichen Klick.

Fuer Agenten, die einen eigenen Browser bzw. ein eigenes Profil fahren und die
Erweiterung so installieren wollen, dass die Installation eine echte
Store-Installation ist: ueber die Enterprise-Policies der Browser. Nur
Store-Installationen melden sich beim Update-Dienst des Stores — ein entpackt
geladener Ordner (--load-extension) tut das nicht und taucht in keiner
Store-Statistik auf.

    install-store-version.py firefox            # Policy setzen (normal_installed)
    install-store-version.py chrome
    install-store-version.py both --json
    install-store-version.py firefox --mode force
    install-store-version.py both --check       # nur Ist-Zustand melden
    install-store-version.py both --remove      # Rollback: nur eigene Eintraege

Windows: die Eintraege gehen nach HKCU — kein Admin noetig, beide Browser
lesen ihre Policies auch aus dem Benutzer-Hive. Aus WSL heraus wird reg.exe
ueber die Windows-Interop aufgerufen.

Linux: die Policy-Dateien liegen systemweit (/etc/firefox/policies/,
/etc/opt/chrome/policies/managed/) und brauchen root. Ohne Schreibrecht
endet das Skript mit Code 2 und gibt die exakten Befehle aus, statt still
durchzufallen.

Rollback ist Teil des Vertrags: --remove entfernt ausschliesslich die Werte,
die dieses Skript gesetzt hat (an Hand des Inhalts erkannt), nie fremde
Policy-Eintraege anderer Werkzeuge.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import urllib.request

SLUG = "full_page_pdf_snap_webpagesave"
AMO_API = f"https://addons.mozilla.org/api/v5/addons/addon/{SLUG}/"
GECKO_ID = "pageshot-pdf@bubu89.local"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
CWS_UPDATE = "https://clients2.google.com/service/update2/crx"

FF_SCHLUESSEL = r"HKCU\Software\Policies\Mozilla\Firefox"
FF_WERT = "ExtensionSettings"
CH_SCHLUESSEL = r"HKCU\Software\Policies\Google\Chrome\ExtensionInstallForcelist"


def amo_xpi_url():
    """Die install_url muss auf eine signierte XPI zeigen; die aktuelle
    Datei-URL kommt aus der AMO-API, nicht aus einer geratenen Zeichenkette."""
    req = urllib.request.Request(AMO_API, headers={"User-Agent": "provinglab-install/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        d = json.load(r)
    cv = d["current_version"]
    return cv["file"]["url"].split("?")[0], cv["version"]


def ff_policy(modus, xpi_url):
    return json.dumps({
        GECKO_ID: {
            "installation_mode": f"{modus}_installed",
            "install_url": xpi_url,
        }
    }, separators=(",", ":"))


def ch_eintrag():
    return f"{CWS_ID};{CWS_UPDATE}"


# --- Windows (auch aus WSL via reg.exe) -------------------------------------

def reg(args):
    """reg.exe ohne Shell aufrufen, damit JSON-Anfuehrungszeichen unangetastet
    bleiben. Funktioniert auf Windows und aus WSL (Interop) gleichermassen."""
    exe = "reg.exe" if shutil.which("reg.exe") else "reg"
    # reg.exe antwortet in der OEM-Codepage der Windows-Konsole; die eigenen
    # Werte sind ASCII-JSON, darum reicht ein tolerantes Decoding.
    return subprocess.run([exe] + args, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def win_ist_wert_vorhanden(schluessel, name):
    r = reg(["query", schluessel, "/v", name])
    if r.returncode != 0:
        return None
    for zeile in r.stdout.splitlines():
        teile = zeile.split()
        if len(teile) >= 3 and teile[0] == name:
            return " ".join(teile[2:])
    return None


def win_ff_setzen(policy_json):
    r = reg(["add", FF_SCHLUESSEL, "/v", FF_WERT, "/t", "REG_SZ", "/d", policy_json, "/f"])
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def win_ff_pruefen():
    ist = win_ist_wert_vorhanden(FF_SCHLUESSEL, FF_WERT)
    if ist is None:
        return {"gesetzt": False, "eigener": False}
    eigener = GECKO_ID in ist
    return {"gesetzt": True, "eigener": eigener, "inhalt": ist}


def win_ff_entfernen():
    ist = win_ff_pruefen()
    if not ist["gesetzt"]:
        return True, "kein Eintrag vorhanden"
    if not ist["eigener"]:
        # Fremde ExtensionSettings duerfen nie angefasst werden — auch nicht
        # "nur der eigene Teil", denn der Wert ist ein einzelnes JSON.
        return False, "ExtensionSettings enthaelt fremde Eintraege — wird nicht angefasst"
    r = reg(["delete", FF_SCHLUESSEL, "/v", FF_WERT, "/f"])
    return r.returncode == 0, (r.stdout + r.stderr).strip()


def win_ch_indices():
    """Belegte Forcelist-Indices lesen, damit ein fremder Eintrag nie
    ueberschrieben wird und der eigene beim Entfernen sicher erkannt ist."""
    r = reg(["query", CH_SCHLUESSEL])
    belegt = {}
    if r.returncode == 0:
        for zeile in r.stdout.splitlines():
            teile = zeile.split()
            if len(teile) >= 3 and teile[0].isdigit():
                belegt[int(teile[0])] = " ".join(teile[2:])
    return belegt


def win_ch_setzen():
    belegt = win_ch_indices()
    ziel = ch_eintrag()
    for i, inhalt in belegt.items():
        if inhalt == ziel:
            return True, f"bereits gesetzt (Index {i})"
    frei = 1
    while frei in belegt:
        frei += 1
    r = reg(["add", CH_SCHLUESSEL, "/v", str(frei), "/t", "REG_SZ", "/d", ziel, "/f"])
    return r.returncode == 0, f"Index {frei}: {(r.stdout + r.stderr).strip()}"


def win_ch_pruefen():
    belegt = win_ch_indices()
    eigene = {i: v for i, v in belegt.items() if v == ch_eintrag()}
    return {"gesetzt": bool(eigene), "indices": eigene, "belegt": belegt}


def win_ch_entfernen():
    ist = win_ch_pruefen()
    if not ist["gesetzt"]:
        return True, "kein eigener Eintrag vorhanden"
    ok = True
    for i in ist["indices"]:
        r = reg(["delete", CH_SCHLUESSEL, "/v", str(i), "/f"])
        ok = ok and r.returncode == 0
    return ok, f"Indices entfernt: {sorted(ist['indices'])}"


# --- Linux -------------------------------------------------------------------

def linux_ff_pfade():
    return ["/etc/firefox/policies/policies.json"]


def linux_schreiben(pfad, politik):
    """Bestehende policies.json wird gemerged — andere Werkzeuge duerfen dort
    eigene Policies haben, und die gehen einen Agenten nichts an."""
    try:
        bestand = {}
        if os.path.exists(pfad):
            bestand = json.loads(open(pfad, encoding="utf-8").read() or "{}")
        bestand.setdefault("policies", {})
        einstellungen = bestand["policies"].setdefault("ExtensionSettings", {})
        einstellungen.update(politik)
        os.makedirs(os.path.dirname(pfad), exist_ok=True)
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(bestand, f, indent=2)
        return True, pfad
    except PermissionError:
        return False, pfad


def linux_ff_setzen(modus, xpi_url):
    politik = {GECKO_ID: {"installation_mode": f"{modus}_installed", "install_url": xpi_url}}
    return linux_schreiben(linux_ff_pfade()[0], politik)


def linux_ff_entfernen():
    pfad = linux_ff_pfade()[0]
    if not os.path.exists(pfad):
        return True, "keine Datei vorhanden"
    try:
        bestand = json.loads(open(pfad, encoding="utf-8").read() or "{}")
        einstellungen = bestand.get("policies", {}).get("ExtensionSettings", {})
        if GECKO_ID not in einstellungen:
            return True, "kein eigener Eintrag vorhanden"
        del einstellungen[GECKO_ID]
        if not einstellungen:
            bestand["policies"].pop("ExtensionSettings", None)
        with open(pfad, "w", encoding="utf-8") as f:
            json.dump(bestand, f, indent=2)
        return True, pfad
    except PermissionError:
        return False, pfad


def linux_ff_pruefen():
    pfad = linux_ff_pfade()[0]
    try:
        bestand = json.loads(open(pfad, encoding="utf-8").read() or "{}")
        eintrag = bestand.get("policies", {}).get("ExtensionSettings", {}).get(GECKO_ID)
        return {"gesetzt": eintrag is not None, "inhalt": eintrag, "pfad": pfad}
    except FileNotFoundError:
        return {"gesetzt": False, "pfad": pfad}


CH_LINUX_PFAD = "/etc/opt/chrome/policies/managed/pdf-snap.json"


def linux_ch_setzen():
    politik = {"ExtensionInstallForcelist": [ch_eintrag()]}
    try:
        os.makedirs(os.path.dirname(CH_LINUX_PFAD), exist_ok=True)
        with open(CH_LINUX_PFAD, "w", encoding="utf-8") as f:
            json.dump(politik, f, indent=2)
        return True, CH_LINUX_PFAD
    except PermissionError:
        return False, CH_LINUX_PFAD


def linux_ch_entfernen():
    if not os.path.exists(CH_LINUX_PFAD):
        return True, "keine eigene Datei vorhanden"
    try:
        # Nur die eigene Datei (eindeutiger Name) — fremde Policy-Dateien im
        # selben Ordner bleiben unangetastet. Verschieben statt loeschen.
        ziel = CH_LINUX_PFAD + ".removed"
        os.replace(CH_LINUX_PFAD, ziel)
        return True, f"verschoben nach {ziel}"
    except PermissionError:
        return False, CH_LINUX_PFAD


def linux_ch_pruefen():
    if not os.path.exists(CH_LINUX_PFAD):
        return {"gesetzt": False, "pfad": CH_LINUX_PFAD}
    try:
        d = json.loads(open(CH_LINUX_PFAD, encoding="utf-8").read())
        return {"gesetzt": ch_eintrag() in d.get("ExtensionInstallForcelist", []),
                "pfad": CH_LINUX_PFAD}
    except json.JSONDecodeError:
        return {"gesetzt": False, "pfad": CH_LINUX_PFAD, "fehler": "Datei ist kein JSON"}


# --- Steuerung ----------------------------------------------------------------

def auf_windows():
    """reg.exe ist auf Windows vorhanden und aus WSL per Interop erreichbar."""
    return sys.platform == "win32" or (sys.platform.startswith("linux") and shutil.which("reg.exe"))


def aktion(browser, modus, befehl):
    ergebnis = {"browser": browser, "aktion": befehl}
    xpi_url, version = amo_xpi_url()
    ergebnis["store_version"] = version
    win = auf_windows()

    if browser == "firefox":
        if win:
            if befehl == "check":
                ergebnis.update(win_ff_pruefen())
            elif befehl == "remove":
                ok, detail = win_ff_entfernen()
                ergebnis.update(ok=ok, detail=detail)
            else:
                ok, detail = win_ff_setzen(ff_policy(modus, xpi_url))
                ergebnis.update(ok=ok, detail=detail, modus=f"{modus}_installed")
        elif sys.platform.startswith("linux"):
            if befehl == "check":
                ergebnis.update(linux_ff_pruefen())
            elif befehl == "remove":
                ok, detail = linux_ff_entfernen()
                ergebnis.update(ok=ok, detail=detail)
            else:
                ok, detail = linux_ff_setzen(modus, xpi_url)
                ergebnis.update(ok=ok, detail=detail, modus=f"{modus}_installed")
                if not ok:
                    ergebnis["anleitung"] = (
                        f"root noetig. Von Hand: {detail} mit "
                        f"'policies.ExtensionSettings.{GECKO_ID}' = "
                        f"{json.dumps({'installation_mode': f'{modus}_installed', 'install_url': xpi_url})}")
        else:
            ergebnis.update(ok=False, detail="macOS: Konfigurationsprofil noetig, "
                            "siehe https://mozilla.github.io/policy-templates/#extensionsettings")
    else:  # chrome
        if win:
            if befehl == "check":
                ergebnis.update(win_ch_pruefen())
            elif befehl == "remove":
                ok, detail = win_ch_entfernen()
                ergebnis.update(ok=ok, detail=detail)
            else:
                ok, detail = win_ch_setzen()
                ergebnis.update(ok=ok, detail=detail)
        elif sys.platform.startswith("linux"):
            if befehl == "check":
                ergebnis.update(linux_ch_pruefen())
            elif befehl == "remove":
                ok, detail = linux_ch_entfernen()
                ergebnis.update(ok=ok, detail=detail)
            else:
                ok, detail = linux_ch_setzen()
                ergebnis.update(ok=ok, detail=detail)
                if not ok:
                    ergebnis["anleitung"] = (
                        f"root noetig. Von Hand: {detail} mit 'ExtensionInstallForcelist' = "
                        f"[{json.dumps(ch_eintrag())}]")
        else:
            ergebnis.update(ok=False, detail="macOS: Konfigurationsprofil noetig, "
                            "siehe https://chromeenterprise.google/policies/#ExtensionInstallForcelist")

    if "ok" not in ergebnis:
        ergebnis["ok"] = True  # check ist kein Pass/Fail
    return ergebnis


def main():
    p = argparse.ArgumentParser(description="Installiert die Store-Version per Browser-Policy.")
    p.add_argument("browser", choices=["firefox", "chrome", "both"])
    p.add_argument("--mode", choices=["normal", "force"], default="normal",
                   help="Firefox: normal_installed (entfernbar) oder force_installed (gesperrt)")
    p.add_argument("--check", action="store_true", help="nur Ist-Zustand melden")
    p.add_argument("--remove", action="store_true", help="eigene Eintraege entfernen")
    p.add_argument("--json", action="store_true", help="Ausgabe als JSON")
    args = p.parse_args()

    befehl = "check" if args.check else "remove" if args.remove else "set"
    ziele = ["firefox", "chrome"] if args.browser == "both" else [args.browser]
    ergebnisse = []
    for z in ziele:
        try:
            ergebnisse.append(aktion(z, args.mode, befehl))
        except Exception as e:  # einzelner Browser darf den anderen nicht mitreissen
            ergebnisse.append({"browser": z, "aktion": befehl, "ok": False,
                               "detail": f"{type(e).__name__}: {e}"})

    if args.json:
        print(json.dumps(ergebnisse, indent=2, ensure_ascii=False))
    else:
        for e in ergebnisse:
            status = "OK" if e.get("ok") else "FEHLER"
            print(f"[{status}] {e['browser']}: {e.get('detail', e.get('inhalt', ''))}")
            if e.get("anleitung"):
                print(f"       {e['anleitung']}")
            if e["aktion"] == "check":
                print(f"       gesetzt={e.get('gesetzt')} store_version={e.get('store_version')}")

    return 0 if all(e.get("ok") for e in ergebnisse) else 1


if __name__ == "__main__":
    sys.exit(main())
