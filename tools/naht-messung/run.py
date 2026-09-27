"""Nahtmessung: Erweiterung (Chrome-Fassung) headless gegen eine Testseite laufen lassen.
   python3 run.py <chrome-mv3-Ordner> <label> [seite.html]
Baut eine Testkopie mit <all_urls> (Ausloesung ohne Geste), nimmt die Seite auf,
legt out/<label>.pdf und die rohen Einzelaufnahmen out/<label>-shotN.png ab.
Bricht mit Exit 1 ab, wenn die Erweiterung nicht laedt, kein Hintergrundprozess
antwortet, die Aufnahme scheitert oder keine PDF entsteht. Altdateien desselben
Labels werden vorher geloescht - ein alter Stand darf nie als neuer gelten."""
import json, shutil, sys, time, tempfile, base64
from pathlib import Path
from playwright.sync_api import sync_playwright

SRC = Path(sys.argv[1]).resolve()
LABEL = sys.argv[2]
SEITE = sys.argv[3] if len(sys.argv) > 3 else "gmail-like.html"
T = Path(__file__).resolve().parent
OUT = T / "out"; OUT.mkdir(exist_ok=True)
for alt in list(OUT.glob(f"{LABEL}.pdf")) + list(OUT.glob(f"{LABEL}-shot*.png")):
    alt.unlink()

ext = Path(tempfile.mkdtemp(prefix="snapext-")) / "ext"
shutil.copytree(SRC, ext, ignore=shutil.ignore_patterns("tests", "*.md", "*.txt", "*.py", "__pycache__"))
m = json.loads((ext / "manifest.json").read_text(encoding="utf-8"))
m["host_permissions"] = sorted(set(m.get("host_permissions", []) + ["<all_urls>"]))
(ext / "manifest.json").write_text(json.dumps(m, indent=1), encoding="utf-8")

chrome = sorted(Path.home().glob(".cache/ms-playwright/chromium-*/chrome-linux*/chrome"))[-1]
prof = Path(tempfile.mkdtemp(prefix="snapprof-")); dl = Path(tempfile.mkdtemp(prefix="snapdl-"))

def fehl(text):
    print("FEHLER:", text); sys.exit(1)

with sync_playwright() as p:
    ctx = p.chromium.launch_persistent_context(
        user_data_dir=str(prof), executable_path=str(chrome), headless=False,
        args=["--headless=new", f"--disable-extensions-except={ext}", f"--load-extension={ext}",
              "--no-first-run", "--no-default-browser-check", "--window-size=1666,1147", "--force-device-scale-factor=1"],
        accept_downloads=True, downloads_path=str(dl), viewport={"width": 1666, "height": 1019})
    page = ctx.new_page(); page.goto("file://" + str(T / "site" / SEITE)); page.wait_for_timeout(800)
    v = ctx.new_page(); v.goto("chrome://extensions/"); v.wait_for_timeout(800)
    info = v.evaluate("""async()=>{const r=await new Promise(res=>chrome.developerPrivate.getExtensionsInfo(res));
      return r.map(x=>({id:x.id,name:x.name,state:x.state,version:x.version,
        manifestErrors:(x.manifestErrors||[]).map(e=>e.message),runtimeErrors:(x.runtimeErrors||[]).map(e=>e.message)}))}""")
    print("Erweiterungen:", json.dumps(info, ensure_ascii=False)[:800])
    treffer = [x for x in info if "PDF" in x["name"] or "Snap" in x["name"] or "extName" in x["name"]]
    if not treffer:
        ctx.close(); fehl("Erweiterung nicht geladen")
    eid = treffer[0]["id"]
    w = ctx.new_page(); w.goto(f"chrome-extension://{eid}/popup.html")
    sw = None
    for _ in range(60):
        sw = next((s for s in ctx.service_workers), None)
        if sw: break
        time.sleep(0.25)
    w.close(); v.close(); page.bring_to_front()
    if not sw:
        ctx.close(); fehl("kein Service Worker")
    sw.evaluate("""()=>{ self.__shots=[]; const orig=chrome.tabs.captureVisibleTab.bind(chrome.tabs);
      chrome.tabs.captureVisibleTab=async function(...a){ const d=await orig(...a); self.__shots.push(d); return d; }; }""")
    res = sw.evaluate("""async()=>{ try{ const r=await runOnActiveTab({region:false}); return {ok:r&&r.ok!==false,err:r&&r.error}; }
      catch(e){ return {ok:false,err:String(e.message||e)} } }""")
    print("Aufnahme:", res)
    if not res.get("ok"):
        ctx.close(); fehl("Aufnahme abgebrochen: " + str(res.get("err")))
    for i, d in enumerate(sw.evaluate("()=>self.__shots||[]")):
        (OUT / f"{LABEL}-shot{i}.png").write_bytes(base64.b64decode(d.split(",", 1)[1]))
    for _ in range(60):
        if any(x.is_file() and x.read_bytes()[:4] == b"%PDF" for x in dl.rglob("*")): break
        time.sleep(0.5)
    ctx.close()

pdfs = [x for x in dl.rglob("*") if x.is_file() and x.read_bytes()[:4] == b"%PDF"]
shutil.rmtree(prof, ignore_errors=True); shutil.rmtree(ext.parent, ignore_errors=True)
if not pdfs:
    fehl("keine PDF entstanden")
shutil.copy(pdfs[0], OUT / f"{LABEL}.pdf"); print("PDF ->", OUT / f"{LABEL}.pdf")
