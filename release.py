#!/usr/bin/env python3
"""Ein Befehl fuer den ganzen Auslieferungsweg.

Bisher waren es fuenf Schritte von Hand - Tests, Version setzen, portieren,
zweimal packen. Dabei ging zweimal die Versionsnummer daneben, weil der Store
bereits weiter war als die Arbeitskopie.

    python3 release.py            # Tests, Version hochstufen, beide Pakete
    python3 release.py --patch    # Patch- statt Minor-Sprung
    python3 release.py --check    # nur pruefen, nichts schreiben
    python3 release.py --keep     # Version unveraendert lassen, nur bauen

Bricht ab, sobald ein Schritt fehlschlaegt - ein halb gebautes Paket ist
schlimmer als gar keins, weil man ihm nichts ansieht.
"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECK = "--check" in sys.argv
KEEP = "--keep" in sys.argv

TESTS = ["coverage.test.js", "end-detection.test.js", "sidenav.test.js"]


def run(cmd, cwd=HERE, quiet=False):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if not quiet:
        for line in (r.stdout or "").rstrip().split("\n"):
            if line.strip():
                print("    " + line)
    if r.returncode != 0:
        err = (r.stderr or r.stdout or "").strip().split("\n")
        print("    " + "\n    ".join(err[-4:]))
    return r.returncode == 0, (r.stdout or "")


def step(n, title):
    print(f"\n[{n}] {title}")


def main():
    print("=" * 62)
    print("  Full Page PDF Snap - Auslieferung")
    print("=" * 62)

    # --- 1. Tests -----------------------------------------------------------
    step(1, "Tests")
    tdir = HERE / "chrome-mv3" / "tests"
    failed = []
    for t in TESTS:
        ok, out = run(["node", t], cwd=tdir, quiet=True)
        bestanden = ok and "ALLE BESTANDEN" in out
        print(f"    {'OK  ' if bestanden else 'FEHL'}  {t}")
        if not bestanden:
            failed.append(t)
    if failed:
        print(f"\n  ABBRUCH: {len(failed)} Test(s) fehlgeschlagen: {', '.join(failed)}")
        print("  Ausfuehren mit: cd chrome-mv3/tests && node <datei>")
        return 1

    # --- 2. Syntax ----------------------------------------------------------
    step(2, "Syntaxpruefung")
    for f in ["background.js", "content.js", "popup.js", "options.js",
              "pdf-writer.js", "i18n.js"]:
        ok, _ = run(["node", "--check", f], quiet=True)
        print(f"    {'OK  ' if ok else 'FEHL'}  {f}")
        if not ok:
            print("\n  ABBRUCH: Syntaxfehler")
            return 1

    # --- 3. Version ---------------------------------------------------------
    step(3, "Version")
    if KEEP:
        # --keep darf die Store-Pruefung nicht umgehen. Genau daran ist es
        # schiefgegangen: Code geaendert, Nummer behalten, Upload abgelehnt
        # mit "Version already exists".
        v = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["version"]
        ok, out = run(["python3", "bump-version.py", "--check"], quiet=True)
        veroeffentlicht = "Status       : VEROEFFENTLICHT" in out
        print(f"    unveraendert: {v}")
        if veroeffentlicht:
            print(f"    ABBRUCH: {v} ist bereits veroeffentlicht - --keep wuerde ein")
            print( "             Paket bauen, das der Store ablehnt. Ohne --keep laufen.")
            return 1
    else:
        args = ["python3", "bump-version.py"]
        if CHECK:
            args.append("--check")
        if "--patch" in sys.argv:
            args.append("--patch")
        ok, _ = run(args)
        if not ok:
            print("\n  ABBRUCH: Versionsnummer nicht setzbar")
            return 1

    if CHECK:
        print("\n  --check: keine Pakete gebaut.")
        return 0

    # --- 4. Chrome portieren und packen -------------------------------------
    step(4, "Chrome MV3")
    ok, out = run(["python3", "port.py"], cwd=HERE / "chrome-mv3", quiet=True)
    if not ok or "FEHL" in out:
        print("    ABBRUCH: Portierung fehlgeschlagen")
        for line in out.strip().split("\n"):
            if "FEHL" in line:
                print("    " + line.strip())
        return 1
    print("    OK    portiert")
    ok, _ = run(["python3", "pack.py"], cwd=HERE / "chrome-mv3")
    if not ok:
        return 1

    # --- 5. Firefox packen --------------------------------------------------
    step(5, "Firefox MV2")
    ok, _ = run(["python3", "pack-firefox.py"])
    if not ok:
        return 1

    # --- 6. Gegenprobe ------------------------------------------------------
    step(6, "Gegenprobe")
    import zipfile
    v = json.loads((HERE / "manifest.json").read_text(encoding="utf-8"))["version"]
    for label, folder in [
            ("Firefox", "/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Firefox/upload"),
            ("Chrome ", "/mnt/c/Users/HOLO/Documents/FullPagePDFSnap_Chrome/upload")]:
        zips = list(Path(folder).glob("*.zip"))
        if not zips:
            print(f"    FEHL  {label}: kein Paket")
            return 1
        z = zipfile.ZipFile(zips[0])
        m = json.loads(z.read("manifest.json"))
        loc = [n for n in z.namelist() if n.startswith("_locales/")]
        stimmt = m["version"] == v and len(loc) >= 2
        print(f"    {'OK  ' if stimmt else 'FEHL'}  {label}  v{m['version']}  "
              f"{len(z.namelist())} Dateien  {len(loc)} Sprachen")
        if not stimmt:
            return 1

    print(f"\n  Fertig. Version {v} liegt in beiden upload-Ordnern.")
    print("  Nicht vergessen: Release Notes anpassen, falls sich Sichtbares geaendert hat.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
