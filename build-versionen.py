#!/usr/bin/env python3
"""Erzeugt /.well-known/extension-versions.json — was wo tatsaechlich ausgeliefert wird.

    python3 build-versionen.py            # schreiben
    python3 build-versionen.py --check    # nur melden, Exitcode 1 bei Abweichung

Warum eine eigene Adresse dafuer: Wer wissen will, ob die Erweiterung, die er
gerade installiert hat, die aktuelle ist, muss heute zwei Stores und ein
Repository von Hand vergleichen. Am 3. August 2026 standen dort drei
verschiedene Zahlen — Firefox 2.26.0, Chrome 2.12.1, GitHub-Release 2.16.0 —
und keine Stelle sagte das.

Die Datei nennt beide Store-Staende, den Quellstand und die deklarierten
Berechtigungen an einer Adresse, maschinenlesbar. Das ist zugleich das
Ehrlichste, was eine Domain zur Anerkennung ihrer eigenen Auslieferungen
beitragen kann: nicht behaupten, aktuell zu sein, sondern nachpruefbar machen,
was gilt.

Die Zahlen kommen aus den Schnittstellen der Stores, nicht aus dem eigenen
Repository — massgeblich ist, was Nutzer installieren koennen.
"""
import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / ".well-known" / "extension-versions.json"
AMO_SLUG = "full_page_pdf_snap_webpagesave"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
BROWSER = {"user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")}


def hole(url):
    r = urllib.request.Request(url, headers=BROWSER)
    with urllib.request.urlopen(r, timeout=30) as a:
        return a.read().decode("utf-8", "replace")


def amo():
    try:
        d = json.loads(hole(f"https://addons.mozilla.org/api/v5/addons/addon/{AMO_SLUG}/?lang=en-US"))
        cv = d["current_version"]
        return {"version": cv["version"], "status": d.get("status"),
                "users": d.get("average_daily_users"),
                "url": f"https://addons.mozilla.org/firefox/addon/{AMO_SLUG}/",
                "signed_file": cv["file"]["url"].split("?")[0]}
    except Exception as e:
        return {"error": type(e).__name__}


def cws():
    try:
        s = hole(f"https://chromewebstore.google.com/detail/{CWS_ID}")
        m = re.search(r'"(\d+\.\d+\.\d+)"', s)
        n = re.search(r">([\d,]+) users<", s)
        return {"version": m.group(1) if m else None,
                "users": int(n.group(1).replace(",", "")) if n else None,
                "url": f"https://chromewebstore.google.com/detail/{CWS_ID}"}
    except Exception as e:
        return {"error": type(e).__name__}


def release():
    try:
        d = json.loads(hole("https://api.github.com/repos/Bubu89/full-page-pdf-snap/releases/latest"))
        return {"tag": d.get("tag_name"),
                "assets": [a["name"] for a in d.get("assets", [])],
                "url": d.get("html_url")}
    except Exception as e:
        return {"error": type(e).__name__}


def bauen():
    quelle = json.loads((HIER / "manifest.json").read_text(encoding="utf-8"))
    ch = json.loads((HIER / "chrome-mv3" / "manifest.json").read_text(encoding="utf-8"))
    a, c, r = amo(), cws(), release()

    # Ein Hinweis, der sich selbst pflegt: weichen die ausgelieferten Fassungen
    # voneinander ab, steht es hier, statt dass es jemandem auffallen muss.
    fassungen = {x.get("version") for x in (a, c) if x.get("version")}
    hinweise = []
    if len(fassungen) > 1:
        hinweise.append(f"Die Stores liefern unterschiedliche Fassungen: "
                        f"Firefox {a.get('version')}, Chromium {c.get('version')}.")
    if a.get("version") and quelle["version"] != a["version"]:
        hinweise.append(f"Der Quellstand ({quelle['version']}) ist nicht der "
                        f"ausgelieferte ({a['version']}).")

    return {
        "$schema_comment": (
            "Kein Standard, sondern eine Auskunft. Wer wissen will, ob seine "
            "Fassung die aktuelle ist, findet hier beide Store-Staende und den "
            "Quellstand an einer Adresse. Erzeugt von build-versionen.py."),
        "name": "Full Page PDF Snap",
        "source": "https://github.com/Bubu89/full-page-pdf-snap",
        "license": "MIT",
        "homepage": "https://provinglab.dev/tools/full-page-pdf-snap/",
        "security_contact": "https://provinglab.dev/.well-known/security.txt",
        "published": {"firefox": a, "chromium": c, "signed_releases": r},
        "source_state": {
            "firefox": quelle["version"],
            "chromium": ch["version"],
            "requires": {
                "firefox": quelle["browser_specific_settings"]["gecko"]["strict_min_version"],
                "firefox_android": quelle["browser_specific_settings"]["gecko_android"]["strict_min_version"],
                "chromium": ch.get("minimum_chrome_version"),
            },
        },
        "permissions": {
            "declared": quelle.get("permissions", []),
            "host_permissions": quelle.get("host_permissions", []),
            "note": ("Keine Host-Rechte. Die Erweiterung sieht einen Tab erst nach "
                     "einer Nutzergeste — Messung: "
                     "https://provinglab.dev/notes/what-an-agent-can-do-with-an-extension/"),
        },
        "notices": hinweise,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()

    neu = bauen()
    for h in neu["notices"]:
        print("  Hinweis:", h)
    if not neu["notices"]:
        print("  Alle Auslieferungen auf demselben Stand.")

    text = json.dumps(neu, ensure_ascii=False, indent=2) + "\n"
    alt = ZIEL.read_text(encoding="utf-8") if ZIEL.exists() else ""
    if a.check:
        # Nur die Fassungen vergleichen, nicht Nutzerzahlen — die aendern sich
        # taeglich und wuerden jede Pipeline rot faerben.
        def kern(t):
            try:
                d = json.loads(t)
                return (d["published"]["firefox"].get("version"),
                        d["published"]["chromium"].get("version"),
                        d["source_state"])
            except Exception:
                return None
        sys.exit(1 if kern(text) != kern(alt) else 0)

    ZIEL.write_text(text, encoding="utf-8")
    print(f"  geschrieben: {ZIEL.relative_to(HIER)}")


if __name__ == "__main__":
    main()
