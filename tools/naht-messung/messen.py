#!/usr/bin/env python3
"""Nahtmessung — Pflichtschritt vor jeder Auslieferung.

    python3 tools/naht-messung/messen.py [chrome-mv3-Ordner]

Nimmt drei Testseiten mit der Erweiterung auf (echter Chromium, headless) und
prueft am Ergebnisbild, was ein Mensch am PDF pruefen wuerde:
  - jede nummerierte Zeile genau einmal (keine Luecke, keine Dopplung),
  - gleichmaessiger Zeilenabstand ueber alle Naehte,
  - eine Leiste, die beim Scrollen fest wird, erscheint genau einmal.

Die drei Seiten decken die drei Layouts ab, an denen bisher Fehler auftraten:
  gmail-like       innerer Scroll-Container, klebende Kopfzeile, scrollbare
                   Seitenleiste (Gmail, 27.09.2026)
  fenster-sticky   Fenster-Scroll, Leiste wird beim Scrollen fest
                   (Google-Suche, 14.09.2026)
  innen-ohne-kopf  innerer Container ohne Kopfzeile, schmaler als das Fenster
                   (Notion-Fall; hier trat der Massstabsfehler aus 2.42.0 auf)

Warum das Pflicht ist: 2.42.0 aenderte den Massstab und wurde nur am
Fenster-Scroll gemessen - dort sind Fenster- und Containerbreite gleich. Der
Fehler lag im zweiten Layout und fiel erst beim Nutzer auf. Eine Aenderung an
Massstab, Naht, Zuschnitt oder Ausblendung gilt erst als geprueft, wenn alle
drei Seiten gruen sind. Exit 0 = gruen, Exit 1 = mindestens eine Seite rot.
"""
import base64, glob, json, os, subprocess, sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
BUILD = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HIER.parent.parent / "chrome-mv3"
OUT = HIER / "out"
SEITEN = [  # (Datei, Soll-Marken = Zeilen + ENDE, Leiste erwartet, Kopfzeile erwartet)
    ("gmail-like.html", 53, None, 1),      # klebende Kopfzeile #2a2a2e: genau einmal, oben (seit 2.44.0)
    ("fenster-sticky.html", 71, 1, None),
    ("innen-ohne-kopf.html", 61, None, 0),
]


def rot(p): return p[0] > 150 and p[1] < 90 and p[2] < 90


def gesamtbild(pdf, tag):
    from PIL import Image
    for f in glob.glob(str(OUT / f"{tag}-img-*")): os.remove(f)
    subprocess.run(["pdfimages", "-j", str(pdf), str(OUT / f"{tag}-img")], capture_output=True)
    ims = [Image.open(f).convert("RGB") for f in sorted(glob.glob(str(OUT / f"{tag}-img-*")))]
    if not ims: return None
    W = ims[0].size[0]; H = sum(i.size[1] for i in ims); big = Image.new("RGB", (W, H)); y = 0
    for i in ims: big.paste(i, (0, y)); y += i.size[1]
    return big


def marken(im):
    W, H = im.size
    cols = [0] * W
    for y in range(0, H, 3):
        for x in range(0, W, 2):
            if rot(im.getpixel((x, y))): cols[x] += 1
    x0 = max(range(0, W - 120, 10), key=lambda x: sum(cols[x:x + 120])); x1 = x0 + 120
    ys = [y for y in range(H) if sum(1 for x in range(x0, x1, 2) if rot(im.getpixel((x, y)))) >= 6]
    m = []
    for y in ys:
        if m and y - m[-1][1] <= 6: m[-1][1] = y
        else: m.append([y, y])
    return [a for a, b in m]


def leisten(im):
    W, H = im.size
    rows = [y for y in range(H) if sum(1 for x in range(0, W, 8)
            if (lambda p: p[0] > 230 and 110 < p[1] < 160 and p[2] < 40)(im.getpixel((x, y)))) > W / 8 * 0.6]
    b = []
    for y in rows:
        if b and y - b[-1][1] <= 3: b[-1][1] = y
        else: b.append([y, y])
    return sum(1 for a, c in b if c - a >= 20)


def kopfzeilen(im):
    """Dunkle Kopfzeile (#2a2a2e) ueber >= 60 % der Breite, Baender >= 100 px hoch.
    2.43.0: 0 (vor der ersten Aufnahme ausgeblendet, leere Flaeche). 2.44.0: 1."""
    W, H = im.size
    rows = [y for y in range(H) if sum(1 for x in range(0, W, 8)
            if (lambda p: abs(p[0] - 42) < 8 and abs(p[2] - 46) < 8)(im.getpixel((x, y)))) > W / 8 * 0.6]
    b = []
    for y in rows:
        if b and y - b[-1][1] <= 3: b[-1][1] = y
        else: b.append([y, y])
    return sum(1 for a, c in b if c - a >= 100)


def main():
    from pypdf import PdfReader
    OUT.mkdir(exist_ok=True)
    rot_gesamt = False
    print(f"Nahtmessung gegen {BUILD}")
    for datei, soll, leiste_soll, kopf_soll in SEITEN:
        tag = "mess-" + datei.replace(".html", "")
        r = subprocess.run([sys.executable, str(HIER / "run.py"), str(BUILD), tag, datei], capture_output=True, text=True)
        pdf = OUT / f"{tag}.pdf"
        if r.returncode != 0 or not pdf.exists():
            print(f"  FEHL  {datei:18} Aufnahme gescheitert: {(r.stdout + r.stderr).strip().splitlines()[-1][:100] if (r.stdout+r.stderr).strip() else '?'}")
            rot_gesamt = True; continue
        diag = json.loads(base64.b64decode(PdfReader(str(pdf)).metadata["/PSDiag"]))
        big = gesamtbild(pdf, tag)
        t = marken(big); dd = [t[i + 1] - t[i] for i in range(len(t) - 1)]
        med = sorted(dd)[len(dd) // 2] if dd else 0
        ausreisser = [x for x in dd if abs(x - med) > 4]
        nl = leisten(big) if leiste_soll is not None else None
        nk = kopfzeilen(big) if kopf_soll is not None else None
        fehler = []
        if len(t) != soll: fehler.append(f"{len(t)} statt {soll} Zeilenmarken")
        if ausreisser: fehler.append(f"Abstaende {ausreisser} statt ~{med}")
        if leiste_soll is not None and nl != leiste_soll: fehler.append(f"Leiste {nl}x statt {leiste_soll}x")
        if kopf_soll is not None and nk != kopf_soll: fehler.append(f"Kopfzeile {nk}x statt {kopf_soll}x")
        ok = not fehler
        rot_gesamt |= not ok
        lay = diag["layout"]
        print(f"  {'OK  ' if ok else 'FEHL'}  {datei:18} Marken {len(t)}/{soll}, Abstand ~{med} px"
              + (f", Leiste {nl}x" if nl is not None else "")
              + (f", Kopfzeile {nk}x" if nk is not None else "")
              + f"  [win={lay['isWindow']} clip={lay.get('clip')} step={diag['stepCss']} seg={diag['segmente']} v={diag['v']}]"
              + ("" if ok else "  <- " + "; ".join(fehler)))
    print("  Ergebnis:", "ROT" if rot_gesamt else "GRUEN")
    return 1 if rot_gesamt else 0


if __name__ == "__main__":
    sys.exit(main())
