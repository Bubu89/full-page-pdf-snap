#!/usr/bin/env python3
"""ping-suchmaschinen.py — meldet neue und geaenderte Seiten aktiv an.

Warten, bis ein Crawler von selbst vorbeikommt, kostet Wochen. IndexNow ist ein
offenes Protokoll, mit dem eine Seite ihre URLs direkt einreicht — Bing, Yandex,
Seznam und Naver nehmen daran teil, Google nicht. Es braucht kein Konto, nur
eine Schluesseldatei im Wurzelverzeichnis.

    python3 ping-suchmaschinen.py            # alle URLs aus sitemap.xml
    python3 ping-suchmaschinen.py --url PFAD # nur eine
    python3 ping-suchmaschinen.py --check    # nur pruefen, nichts senden

Gehoert nach jedem Deployment aufgerufen. Der Aufruf ist billig und die
Wirkung ist die einzige, die man ohne Konto ueberhaupt anstossen kann.
"""
import argparse, json, re, sys, urllib.request, urllib.error
from pathlib import Path

HOST = "provinglab.dev"
BASIS = f"https://{HOST}"
DOCS = Path(__file__).resolve().parent / "docs"
ENDPUNKT = "https://api.indexnow.org/IndexNow"


def schluessel():
    p = DOCS / "indexnow-key.txt"
    if not p.exists():
        sys.exit("indexnow-key.txt fehlt — erst anlegen.")
    return p.read_text(encoding="utf-8").strip()


def urls_aus_sitemap():
    p = DOCS / "sitemap.xml"
    if not p.exists():
        sys.exit("sitemap.xml fehlt.")
    return re.findall(r"<loc>([^<]+)</loc>", p.read_text(encoding="utf-8"))


def erreichbar(url):
    try:
        req = urllib.request.Request(url, method="HEAD",
                                     headers={"User-Agent": "provinglab-ping/1.0"})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status == 200
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", help="einzelner Pfad statt aller aus der Sitemap")
    ap.add_argument("--check", action="store_true", help="nur pruefen, nichts senden")
    a = ap.parse_args()

    key = schluessel()
    urls = [f"{BASIS}/{a.url.lstrip('/')}"] if a.url else urls_aus_sitemap()

    # Schluesseldatei muss oeffentlich liegen, sonst lehnt IndexNow ab
    key_url = f"{BASIS}/{key}.txt"
    if not erreichbar(key_url):
        sys.exit(f"Schluesseldatei nicht erreichbar: {key_url}\n"
                 f"Erst deployen, dann melden.")
    print(f"  Schluesseldatei: {key_url}  OK")

    # Nur melden, was tatsaechlich abrufbar ist — eine 404 zu melden schadet
    gut = [u for u in urls if erreichbar(u)]
    schlecht = [u for u in urls if u not in gut]
    for u in schlecht:
        print(f"  uebersprungen (nicht erreichbar): {u}")
    if not gut:
        sys.exit("Keine erreichbare URL.")

    print(f"\n  {len(gut)} URL(s) zu melden:")
    for u in gut:
        print(f"    {u}")

    if a.check:
        print("\n  --check: nichts gesendet.")
        return 0

    nutzlast = json.dumps({
        "host": HOST, "key": key, "keyLocation": key_url, "urlList": gut,
    }).encode()
    req = urllib.request.Request(ENDPUNKT, data=nutzlast, method="POST",
                                 headers={"Content-Type": "application/json; charset=utf-8"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            code = r.status
    except urllib.error.HTTPError as e:
        code = e.code
    except Exception as e:
        print(f"\n  Fehler: {e}", file=sys.stderr)
        return 1

    # 200 = angenommen, 202 = angenommen aber Schluessel wird noch geprueft
    bedeutung = {200: "angenommen", 202: "angenommen, Schluessel wird geprueft",
                 400: "fehlerhafte Anfrage", 403: "Schluessel abgelehnt",
                 422: "URLs passen nicht zum Host", 429: "zu viele Anfragen"}
    print(f"\n  IndexNow: HTTP {code} — {bedeutung.get(code, 'unbekannt')}")
    return 0 if code in (200, 202) else 1


if __name__ == "__main__":
    sys.exit(main())
