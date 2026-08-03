#!/usr/bin/env python3
"""sync-site.py — haelt die Website auf dem Stand der veroeffentlichten Version.

Bei jeder neuen Version aendern sich Dinge, die an mehreren Stellen der Seite
stehen: Versionsnummer, die Download-URL des signierten XPI, das Datum. Von
Hand nachzuziehen heisst, es irgendwann zu vergessen — und eine Seite, die eine
alte Version anbietet, ist schlimmer als eine ohne Download.

Quelle der Wahrheit ist die AMO-API, nicht das lokale Manifest: massgeblich ist,
was Nutzer tatsaechlich installieren koennen.

    python3 sync-site.py            # pruefen und schreiben
    python3 sync-site.py --check    # nur pruefen, Exitcode 1 bei Abweichung

Nach dem Lauf: git add/commit/push. Der Aufruf gehoert in release.py und in
jede Routine, die eine neue Version einreicht.
"""
import json, re, sys, urllib.request, pathlib, datetime

SLUG = "full_page_pdf_snap_webpagesave"
API = f"https://addons.mozilla.org/api/v5/addons/addon/{SLUG}/?lang=en-US"
DOCS = pathlib.Path(__file__).resolve().parent / "docs"
CHECK = "--check" in sys.argv


def amo():
    with urllib.request.urlopen(API, timeout=20) as r:
        d = json.load(r)
    cv = d["current_version"]
    return {
        "version": cv["version"],
        "xpi": cv["file"]["url"].split("?")[0],
        "size": cv["file"].get("size"),
        "permissions": cv["file"].get("permissions", []),
        "released": (cv.get("reviewed") or cv.get("created") or "")[:10],
    }



def neuestes_release():
    """Tag des neuesten GitHub-Releases mit einer XPI-Datei, ohne fuehrendes v.

    Ohne diese Abfrage schreibt das Skript die Store-Version in einen
    Release-Pfad, den niemand veroeffentlicht hat.
    """
    r = urllib.request.Request(
        "https://api.github.com/repos/Bubu89/full-page-pdf-snap/releases",
        headers={"accept": "application/vnd.github+json",
                 "user-agent": "provinglab-sync/1.0"})
    try:
        with urllib.request.urlopen(r, timeout=20) as a:
            for rel in json.load(a):
                if any(x["name"].endswith(".xpi") for x in rel.get("assets") or []):
                    return rel["tag_name"].lstrip("v")
    except Exception as e:
        print(f"  Warnung: Releases nicht abrufbar ({type(e).__name__}); "
              "der Release-Link bleibt unveraendert.")
    return None

def patch(pfad, ersetzungen):
    """Wendet (Regex, Ersatz, Beschreibung) an und meldet jede Aenderung."""
    p = DOCS / pfad
    if not p.exists():
        return [f"FEHLT: {pfad}"]
    alt = p.read_text(encoding="utf-8")
    neu, meldungen = alt, []
    for muster, ersatz, was in ersetzungen:
        neu2, n = re.subn(muster, ersatz, neu)
        if n and neu2 != neu:
            meldungen.append(f"{pfad}: {was} ({n}x)")
        neu = neu2
    if neu != alt and not CHECK:
        p.write_text(neu, encoding="utf-8")
    return meldungen


def main():
    try:
        a = amo()
    except Exception as e:
        print(f"AMO nicht erreichbar: {e}", file=sys.stderr)
        return 2

    v, xpi = a["version"], a["xpi"]
    release = neuestes_release() or v
    print(f"  Veroeffentlicht auf AMO: {v}")
    print(f"  Signiertes XPI         : {xpi}")
    print(f"  Neuestes GitHub-Release: {release}"
          + ("" if release == v else "   (bleibt hinter dem Store zurueck)"))

    aenderungen = []

    # Produktseite: Versionsnummer im Install-Knopf, XPI-URL, softwareVersion
    aenderungen += patch("tools/full-page-pdf-snap/index.html", [
        # Muss die VOLLSTAENDIGE URL fassen, sonst haengt ein zweiter Lauf die
        # Endung erneut an: .../name -> .../name-2.16.0.xpi -> ...xpi-2.16.0.xpi
        (r"https://addons\.mozilla\.org/firefox/downloads/file/\d+/[\w.\-]+", xpi,
         "XPI-Direktlink"),
        # Die Version steht neben dem Knopf, nicht darauf: der Knopftext traegt
        # den Suchbegriff ("Download for Firefox"), die Fassung bleibt daneben
        # und wird hier weiter gepflegt.
        (r"(Version )\d+\.\d+\.\d+( — signed by Mozilla)", rf"\g<1>{v}\g<2>", "Versionsangabe EN"),
        (r"(Version )\d+\.\d+\.\d+( — von Mozilla signiert)", rf"\g<1>{v}\g<2>", "Versionsangabe DE"),
        (r'("softwareVersion":\s*")[\d.]+(")', rf"\g<1>{v}\g<2>", "JSON-LD softwareVersion"),
        # Nur auf ein Release zeigen, das es gibt. Die Store-Fassung laeuft den
        # GitHub-Releases voraus — am 03.08.2026 stand die Seite auf v2.26.0,
        # veroeffentlicht war v2.16.0, und der Weg "ohne Store" endete im 404.
        # Ein Link, der mit der Fassung mitwandert, muss der Fassung folgen, die
        # tatsaechlich abrufbar ist.
        (r"(releases/download/v)[\d.]+(/full-page-pdf-snap-)[\d.]+(\.xpi)",
         rf"\g<1>{release}\g<2>{release}\g<3>", "GitHub-Release-XPI"),
    ])

    # Startseite: seit dem Umbau steht der Installationsknopf auch dort, mit
    # demselben versionsgebundenen XPI-Link. Ohne diesen Block friert er auf
    # dem Stand ein, an dem er eingebaut wurde.
    aenderungen += patch("index.html", [
        (r"https://addons\.mozilla\.org/firefox/downloads/file/\d+/[\w.\-]+", xpi,
         "XPI-Direktlink Startseite"),
        (r"(Version )\d+\.\d+\.\d+( — signed by Mozilla)", rf"\g<1>{v}\g<2>",
         "Versionsangabe Startseite"),
    ])

    # llms.txt: Versionsangabe, falls vorhanden
    aenderungen += patch("llms.txt", [
        (r"(Full Page PDF Snap[^\n]*?)version [\d.]+", rf"\g<1>version {v}", "Version"),
    ])

    heute = datetime.date.today().isoformat()
    aenderungen += patch("sitemap.xml", [
        (r"(<loc>https://provinglab\.dev/tools/full-page-pdf-snap/</loc>\s*<lastmod>)[\d-]+",
         rf"\g<1>{heute}", "lastmod Produktseite"),
    ])

    if aenderungen:
        print("\n  Angepasst:" if not CHECK else "\n  Abweichungen (nichts geschrieben):")
        for m in aenderungen:
            print(f"    {m}")
    else:
        print("\n  Website ist auf dem Stand der veroeffentlichten Version.")

    # Gegenprobe: steht die aktuelle Version wirklich auf der Seite?
    seite = (DOCS / "tools/full-page-pdf-snap/index.html").read_text(encoding="utf-8")
    if xpi not in seite:
        print(f"\n  FEHLER: XPI-Link steht nicht auf der Seite", file=sys.stderr)
        return 1
    if v not in seite:
        print(f"\n  FEHLER: Version {v} steht nicht auf der Seite", file=sys.stderr)
        return 1
    print(f"  Gegenprobe: Version {v} und XPI-Link stehen auf der Produktseite.")

    if CHECK and aenderungen:
        return 1
    if aenderungen and not CHECK:
        print("\n  Nicht vergessen: git add docs/ && git commit && git push")
        print("  Und das Release: gh release upload vX.Y.Z <xpi> <chrome-zip>")
    return 0


if __name__ == "__main__":
    sys.exit(main())
