#!/usr/bin/env python3
"""Erzeugt die Store-Screenshots (1280x800) aus HTML-Vorlagen.

Warum als Skript und nicht von Hand: Die Tastenkuerzel stehen an mehreren
Stellen in den Bildern. Beim Wechsel von Alt+Shift+P auf Alt+Shift+Y blieb das
alte Kuerzel in zwei Bildern stehen und war monatelang im Store zu sehen.
Hier steht es an EINER Stelle - siehe KUERZEL weiter unten.

    python3 make-store-screenshots.py            # nach screenshots/
    python3 make-store-screenshots.py --out DIR

Vorschau ohne Chrome:  die erzeugten .html im Browser oeffnen.
"""
import argparse
import shutil
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen

HIER = Path(__file__).resolve().parent
CHROME = "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe"
PORT = 9225
CDP = f"http://127.0.0.1:{PORT}"
BREITE, HOEHE = 1280, 800

# --- Einzige Quelle fuer die Kuerzel -----------------------------------------
KUERZEL = "Alt+Shift+Y"
KUERZEL2 = "Ctrl+Shift+Y"

STIL = """
* { margin:0; padding:0; box-sizing:border-box; }
body {
  width:@@B@@px; height:@@H@@px; overflow:hidden;
  font-family:"Segoe UI",system-ui,-apple-system,sans-serif;
  background:linear-gradient(135deg,#ffffff 0%,#f4f7fb 55%,#e8eef7 100%);
  color:#0f172a; display:flex; align-items:center;
}
.inhalt { display:flex; align-items:center; gap:56px; padding:0 64px; width:100%; }
.links { width:520px; flex-shrink:0; }
.marke {
  display:inline-block; background:#2563eb; color:#fff; font-size:17px;
  font-weight:700; letter-spacing:1.4px; padding:9px 20px; border-radius:999px;
  margin-bottom:26px;
}
h1 { font-size:52px; line-height:1.13; font-weight:800; letter-spacing:-1px; margin-bottom:30px; }
h1 em { font-style:normal; color:#2563eb; }
ul { list-style:none; }
li {
  font-size:25px; line-height:1.42; color:#334155; margin-bottom:19px;
  padding-left:34px; position:relative; font-weight:500;
}
li::before {
  content:""; position:absolute; left:0; top:11px; width:13px; height:13px;
  border-radius:50%; background:#2563eb;
}
li b { color:#0f172a; font-weight:700; }
kbd {
  font-family:"Cascadia Mono",Consolas,monospace; font-size:21px; font-weight:700;
  background:#0f172a; color:#fff; padding:4px 12px; border-radius:7px;
  white-space:nowrap;
}
.rechts { flex:1; display:flex; justify-content:center; }
.karte {
  background:#fff; border-radius:18px; width:100%; max-width:600px;
  box-shadow:0 26px 60px rgba(15,23,42,.20), 0 0 0 1px rgba(15,23,42,.07);
  overflow:hidden;
}
.leiste {
  background:#f1f5f9; border-bottom:1px solid #e2e8f0; padding:13px 18px;
  font-size:16px; color:#475569; font-weight:600; display:flex;
  justify-content:space-between; align-items:center;
}
.punkte span { display:inline-block; width:12px; height:12px; border-radius:50%; margin-left:8px; }
.rumpf { padding:32px; }
"""


def html(inhalt, breite=BREITE, hoehe=HOEHE):
    stil = STIL.replace("@@B@@", str(breite)).replace("@@H@@", str(hoehe))
    return f"<!doctype html><meta charset='utf-8'><style>{stil}</style>{inhalt}"


# --- 1. Aufnehmen -------------------------------------------------------------
BILD1 = html(f"""
<div class="inhalt">
  <div class="links">
    <span class="marke">CAPTURE</span>
    <h1>One click saves<br>the <em>entire page</em></h1>
    <ul>
      <li>Toolbar button, menu or <kbd>{KUERZEL}</kbd></li>
      <li>Auto-scrolls through <b>lazy-loading</b> pages</li>
      <li>No print dialog, no upload, <b>no account</b></li>
    </ul>
  </div>
  <div class="rechts"><div class="karte" style="max-width:470px">
    <div class="leiste"><span>Full Page PDF Snap</span>
      <span class="punkte"><span style="background:#cbd5e1"></span>
      <span style="background:#cbd5e1"></span><span style="background:#f87171"></span></span></div>
    <div class="rumpf" style="text-align:center;padding:42px 36px">
      <div style="font-size:27px;font-weight:800;margin-bottom:26px">Save the whole page as PDF</div>
      <div style="background:#2563eb;color:#fff;font-size:26px;font-weight:700;
                  padding:20px;border-radius:12px;box-shadow:0 8px 22px rgba(37,99,235,.34)">
        Capture whole page</div>
        <div style="background:#f1f5f9;color:#0f172a;font-size:22px;font-weight:600;
                    padding:16px;border-radius:10px;border:1px solid #cbd5e1;
                    margin-top:14px">Select an area&hellip;</div>
        <div style="display:flex;align-items:center;gap:14px;margin-top:16px;
                    background:#f1f5f9;border:1px solid #cbd5e1;border-radius:10px;
                    padding:14px 16px;text-align:left">
          <span style="width:46px;height:27px;border-radius:14px;background:#2563eb;
                       position:relative;flex:0 0 auto">
            <span style="position:absolute;top:3px;left:22px;width:21px;height:21px;
                         border-radius:50%;background:#fff"></span></span>
          <span style="font-size:19px;font-weight:700;color:#0f172a">Hide banners and pop-ups</span>
        </div>
      <div style="margin-top:26px;font-size:20px;color:#475569">
        Whole page shortcut: <kbd style="font-size:19px">{KUERZEL}</kbd></div>
      <div style="margin-top:22px;font-size:19px;color:#2563eb;font-weight:600;
                  text-decoration:underline">Settings</div>
    </div>
  </div></div>
</div>""")

# --- 2. Einstellungen ---------------------------------------------------------
def zeile(titel, wert, breit=False):
    return f"""
    <div style="margin-bottom:19px">
      <div style="font-size:16px;font-weight:700;color:#475569;margin-bottom:7px">{titel}</div>
      <div style="border:2px solid #cbd5e1;border-radius:9px;padding:12px 15px;
                  font-size:{19 if not breit else 18}px;color:#0f172a;background:#f8fafc">{wert}</div>
    </div>"""


BILD2 = html(f"""
<div class="inhalt">
  <div class="links">
    <span class="marke">SETTINGS</span>
    <h1>Tuned exactly<br><em>the way you want</em></h1>
    <ul>
      <li>Filename templates with <b>site, date, time</b></li>
      <li>Resolution up to <b>2.0x</b> for sharp text</li>
      <li>Hide <b>cookie banners</b> and sticky bars</li>
    </ul>
  </div>
  <div class="rechts"><div class="karte">
    <div class="leiste"><span>Settings — Full Page PDF Snap</span>
      <span class="punkte"><span style="background:#cbd5e1"></span>
      <span style="background:#cbd5e1"></span><span style="background:#f87171"></span></span></div>
    <div class="rumpf">
      {zeile("Filename template", "{site}_{date}_{time}_{n}")}
      {zeile("PDF format", "One continuous page — no visible seams &nbsp;&nbsp;⌄")}
      {zeile("Capture scaling (resolution)", "2.0x — sharp text and images &nbsp;&nbsp;⌄")}
      <div style="display:flex;align-items:center;gap:13px;margin-top:24px">
        <div style="width:26px;height:26px;border-radius:6px;background:#2563eb;
                    color:#fff;font-size:18px;font-weight:800;text-align:center;
                    line-height:26px">✓</div>
        <div style="font-size:19px;color:#0f172a;font-weight:600">
          Hide sticky headers before capture</div>
      </div>
      <div style="margin-top:20px;font-size:17px;color:#64748b">
        Interface in <b style="color:#0f172a">9 languages</b> — follows your browser</div>
    </div>
  </div></div>
</div>""")

# --- 3. Ergebnis --------------------------------------------------------------
BILD3 = html(f"""
<div class="inhalt">
  <div class="links">
    <span class="marke">OUTPUT</span>
    <h1>One seamless page,<br><em>not a print job</em></h1>
    <ul>
      <li>The page <b>exactly as you saw it</b></li>
      <li>No seams — ideal for <b>OCR and AI</b></li>
      <li>Multi-page output optionally, for printing</li>
    </ul>
  </div>
  <div class="rechts" style="gap:26px">
    <div style="text-align:center">
      <div style="font-size:17px;font-weight:700;color:#dc2626;margin-bottom:13px">
        ✕ &nbsp;Browser print</div>
      <div style="display:flex;flex-direction:column;gap:9px">
        {"".join(f'''<div style="width:158px;height:104px;background:#fff;border-radius:6px;
             box-shadow:0 4px 12px rgba(15,23,42,.13);padding:11px">
             <div style="height:7px;background:#fecaca;border-radius:3px;margin-bottom:6px"></div>
             <div style="height:7px;background:#e2e8f0;border-radius:3px;width:{w}%;
                  margin-bottom:6px"></div>
             <div style="height:7px;background:#e2e8f0;border-radius:3px;width:60%"></div>
           </div>''' for w in (80, 70, 85))}
      </div>
      <div style="font-size:15px;color:#64748b;margin-top:11px">cut into pieces</div>
    </div>
    <div style="text-align:center">
      <div style="font-size:17px;font-weight:700;color:#16a34a;margin-bottom:13px">
        ✓ &nbsp;Full Page PDF Snap</div>
      <div style="width:230px;height:348px;background:#fff;border-radius:9px;
                  box-shadow:0 16px 40px rgba(15,23,42,.20);padding:17px;overflow:hidden">
        <div style="height:15px;background:#2563eb;border-radius:4px;width:65%;
                    margin-bottom:12px"></div>
        {"".join(f'<div style="height:8px;background:#e2e8f0;border-radius:3px;width:{w}%;margin-bottom:8px"></div>' for w in (100, 94, 100, 88, 100, 96, 72))}
        <div style="height:62px;background:#dbeafe;border-radius:6px;margin:12px 0"></div>
        {"".join(f'<div style="height:8px;background:#e2e8f0;border-radius:3px;width:{w}%;margin-bottom:8px"></div>' for w in (100, 90, 100, 76))}
      </div>
      <div style="font-size:15px;color:#64748b;margin-top:11px">one continuous page</div>
    </div>
  </div>
</div>""")

# --- 4. Kostenlos & privat ----------------------------------------------------
def haken(text):
    return f"""<div style="display:flex;align-items:flex-start;gap:14px;margin-bottom:17px">
      <div style="width:27px;height:27px;border-radius:50%;background:#16a34a;color:#fff;
                  font-size:17px;font-weight:800;text-align:center;line-height:27px;
                  flex-shrink:0">✓</div>
      <div style="font-size:21px;color:#0f172a;font-weight:600;line-height:1.35">{text}</div>
    </div>"""


BILD4 = html(f"""
<div class="inhalt">
  <div class="links">
    <span class="marke">LICENSE</span>
    <h1>Nothing to buy.<br><em>Nothing to sign up.</em></h1>
    <ul>
      <li>Everything runs <b>on your device</b></li>
      <li>Open source under the <b>MIT license</b></li>
      <li>No access to <b>all your websites</b></li>
    </ul>
  </div>
  <div class="rechts"><div class="karte" style="max-width:530px">
    <div class="rumpf" style="padding:38px 40px">
      {haken("No ads, no watermark, no page limit")}
      {haken("No account, no sign-up, no subscription")}
      {haken("No upload — the page never leaves your computer")}
      {haken("No analytics, no telemetry, no tracking")}
      <div style="margin-top:26px;padding-top:22px;border-top:2px solid #e2e8f0;
                  font-size:18px;color:#475569;line-height:1.5">
        There is no paid tier, because
        <b style="color:#0f172a">there is nothing to sell you</b>.</div>
    </div>
  </div></div>
</div>""")


# --- Promo-Kacheln ------------------------------------------------------------
# Beide zeigen NUR Logo, Name und Kernnutzen. Die kleine Kachel wird im Store
# stark verkleinert - Screenshots oder Fliesstext sind darin nicht lesbar.

def badge(text, farbe="#2563eb", gross=False):
    return (f'<span style="display:inline-block;background:{farbe};color:#fff;'
            f'font-size:{15 if gross else 11}px;font-weight:700;letter-spacing:.7px;'
            f'padding:{8 if gross else 5}px {16 if gross else 10}px;'
            f'border-radius:999px;margin-right:{10 if gross else 6}px">{text}</span>')


# Neue Kategorie: was die Aufnahme zitierfaehig macht. Bewusst nicht "besser als
# andere", sondern was im PDF steht — pruefbar und ohne Rangbehauptung, die
# Google beanstanden koennte.
BILD5 = html(f"""
<div class="inhalt">
  <div class="links">
    <span class="marke">CITE</span>
    <h1>Every capture,<br><em>ready to cite</em></h1>
    <ul>
      <li>Authors, journal, <b>DOI</b> and licence read from the page</li>
      <li>Retrieval time <b>with time zone</b>, and a checksum</li>
      <li><b>RIS record attached</b> — Citavi, Zotero, EndNote</li>
      <li>Searchable text from the page, not from pixels</li>
    </ul>
  </div>
  <div class="rechts" style="flex-direction:column;align-items:center">
    <div style="width:392px;background:#fff;border-radius:11px;
                box-shadow:0 18px 46px rgba(15,23,42,.20);overflow:hidden">
      <div style="padding:19px 21px 15px">
        <div style="height:12px;background:#0f172a;border-radius:3px;width:72%;
                    margin-bottom:13px"></div>
        {"".join(f'<div style="height:7px;background:#e2e8f0;border-radius:3px;width:{w}%;margin-bottom:8px"></div>' for w in (100, 93, 100, 86, 97))}
      </div>
      <div style="background:#e2e8f0;padding:11px 21px 13px;border-top:1px solid #cbd5e1">
        <div style="font-size:11.5px;color:#0f172a;font-weight:600;line-height:1.35">
          Fr&uuml;hauf, S., Gerger, H. &amp; Barth, J. (2013). Efficacy of
          Psychological Interventions. <i>Archives of Sexual Behavior, 42</i>(6).</div>
        <div style="font-size:10px;color:#475569;margin-top:5px;font-family:ui-monospace,monospace">
          captured 2026-08-03 09:14 +02:00 &nbsp;|&nbsp; SHA-256 5516fdd6&hellip;</div>
      </div>
    </div>
    <div style="margin-top:15px;display:flex;align-items:center;gap:9px;
                background:#fff;border-radius:8px;padding:10px 14px;
                box-shadow:0 4px 14px rgba(15,23,42,.12)">
      <span style="font-size:13px;font-weight:700;color:#2563eb">quelle.ris</span>
      <span style="font-size:12px;color:#64748b">attached to the PDF</span>
    </div>
  </div>
</div>""")


KACHEL_KLEIN = html(f"""
<div style="width:440px;height:280px;display:flex;flex-direction:column;
            align-items:center;justify-content:center;text-align:center;padding:28px">
  <img src="icon-128.png" style="width:74px;height:74px;margin-bottom:16px">
  <div style="font-size:29px;font-weight:800;line-height:1.15;letter-spacing:-.5px">
    Full Page<br>PDF Snap</div>
  <div style="font-size:15px;color:#475569;margin-top:11px;font-weight:500">
    The whole webpage as one PDF</div>
  <div style="font-size:14px;color:#64748b;margin-top:14px;line-height:1.5">
    Runs on your device · No tracking</div>
</div>""", 440, 280)

KACHEL_GROSS = html(f"""
<div style="width:1400px;height:560px;display:flex;align-items:center;
            justify-content:center;gap:52px;padding:0 80px">
  <img src="icon-128.png" style="width:186px;height:186px;flex-shrink:0">
  <div>
    <div style="font-size:66px;font-weight:800;letter-spacing:-1.5px;line-height:1.1">
      Full Page PDF Snap</div>
    <div style="font-size:29px;color:#334155;margin-top:18px;font-weight:500;
                line-height:1.4">
      Save any webpage as <b style="color:#0f172a">one seamless PDF</b>.<br>
      Auto-scrolls the whole page — no cropping, no print dialog.</div>
    <div style="margin-top:28px;font-size:21px;color:#64748b;font-weight:500">
      Runs on your device · No tracking · Open source (MIT)</div>
  </div>
</div>""", 1400, 560)

BILDER = [("01_capture_en", BILD1, 1280, 800), ("02_settings_en", BILD2, 1280, 800),
          ("03_output_en", BILD3, 1280, 800), ("04_nocost_en", BILD4, 1280, 800),
          ("05_cite_en", BILD5, 1280, 800),
          ("promo_tile_440x280", KACHEL_KLEIN, 440, 280),
          ("marquee_promo_1400x560", KACHEL_GROSS, 1400, 560)]


def chrome_laeuft():
    try:
        with urlopen(f"{CDP}/json/version", timeout=3):
            return True
    except Exception:
        return False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HIER / "screenshots"))
    args = ap.parse_args()
    ziel = Path(args.out)
    ziel.mkdir(parents=True, exist_ok=True)

    tmp_win = Path("/mnt/c/Temp/pdfsnap-shots")
    tmp_win.mkdir(parents=True, exist_ok=True)
    for name, inhalt, _, _ in BILDER:
        (tmp_win / f"{name}.html").write_text(inhalt, encoding="utf-8")
        (ziel / f"{name}.html").write_text(inhalt, encoding="utf-8")
    shutil.copy(HIER / "icons" / "icon-128.png", tmp_win / "icon-128.png")

    if not chrome_laeuft():
        subprocess.Popen(
            [CHROME, "--headless=new", "--disable-gpu", f"--remote-debugging-port={PORT}",
             "--user-data-dir=C:\\Temp\\pdfsnap-shotprof", "--no-first-run",
             "--hide-scrollbars", f"--window-size={BREITE},{HOEHE}", "about:blank"],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        for _ in range(30):
            if chrome_laeuft():
                time.sleep(1.5)
                break
            time.sleep(1)
        else:
            sys.exit("Chrome antwortet nicht.")

    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.connect_over_cdp(CDP)
        ctx = b.contexts[0]
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        for name, _, br, ho in BILDER:
            page.set_viewport_size({"width": br, "height": ho})
            page.goto(f"file:///C:/Temp/pdfsnap-shots/{name}.html")
            page.wait_for_timeout(700)
            d = ziel / f"{name}.png"
            page.screenshot(path=str(d), clip={"x": 0, "y": 0,
                                               "width": br, "height": ho})
            print(f"  {d.name}  {d.stat().st_size/1024:.0f} KB")
        b.close()

    shutil.rmtree(tmp_win, ignore_errors=True)
    print(f"\n{len(BILDER)} Bilder in {ziel}  (Kuerzel {KUERZEL})")


if __name__ == "__main__":
    main()
