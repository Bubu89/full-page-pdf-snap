"""Baut eine Testkopie der Chrome-Fassung mit <all_urls> (ohne Geste auslösbar),
öffnet die Fixture headless in Chromium, löst die Aufnahme aus und legt die PDF
plus Diagnose in out/ ab.   python3 run.py <ext-src-dir> <label>"""
import json, shutil, sys, time, tempfile, base64, re
from pathlib import Path
from playwright.sync_api import sync_playwright
SRC=Path(sys.argv[1]).resolve(); LABEL=sys.argv[2]; T=Path(__file__).parent; OUT=T/'out'; OUT.mkdir(exist_ok=True)
ext=Path(tempfile.mkdtemp(prefix='snapext-'))/'ext'; shutil.copytree(SRC,ext,ignore=shutil.ignore_patterns('tests','*.md','*.txt','*.py','__pycache__'))
m=json.loads((ext/'manifest.json').read_text(encoding='utf-8')); m.setdefault('host_permissions',[]); m['host_permissions']=list(set(m['host_permissions']+['<all_urls>'])); (ext/'manifest.json').write_text(json.dumps(m,indent=1),encoding='utf-8')
chrome=sorted(Path.home().glob('.cache/ms-playwright/chromium-*/chrome-linux*/chrome'))[-1]
prof=Path(tempfile.mkdtemp(prefix='snapprof-')); dl=Path(tempfile.mkdtemp(prefix='snapdl-'))
with sync_playwright() as p:
    ctx=p.chromium.launch_persistent_context(user_data_dir=str(prof),executable_path=str(chrome),headless=False,
        args=['--headless=new',f'--disable-extensions-except={ext}',f'--load-extension={ext}','--no-first-run','--no-default-browser-check','--window-size=1666,1147','--force-device-scale-factor=1'],
        accept_downloads=True,downloads_path=str(dl),viewport={'width':1666,'height':1019})
    page=ctx.new_page(); page.goto('file://'+str(T/'site'/'gmail-like.html')); page.wait_for_timeout(800)
    sw=None
    for _ in range(40):
        sw=next((w for w in ctx.service_workers),None)
        if sw: break
        time.sleep(0.25)
    if not sw:
        v=ctx.new_page(); v.goto('chrome://extensions/'); v.wait_for_timeout(800)
        info=v.evaluate("async()=>{const r=await new Promise(res=>chrome.developerPrivate.getExtensionsInfo(res));return r.map(x=>({id:x.id,name:x.name}))}")
        eid=[x for x in info if 'PDF' in x['name']][0]['id']; w=ctx.new_page(); w.goto(f'chrome-extension://{eid}/popup.html')
        for _ in range(40):
            sw=next((w2 for w2 in ctx.service_workers),None)
            if sw: break
            time.sleep(0.25)
        w.close(); v.close(); page.bring_to_front()
    print('SW:',bool(sw))
    sw.evaluate("""()=>{ self.__shots=[]; const orig=chrome.tabs.captureVisibleTab.bind(chrome.tabs); chrome.tabs.captureVisibleTab=async function(...a){ const d=await orig(...a); self.__shots.push(d); return d; }; }""")
    res=sw.evaluate("""async()=>{ try{ const r=await runOnActiveTab({region:false}); return {ok:r&&r.ok!==false,err:r&&r.error}; }catch(e){ return {ok:false,err:String(e.message||e)} } }""")
    shots=sw.evaluate("()=>self.__shots||[]")
    for i,d in enumerate(shots):
        (OUT/f'{LABEL}-shot{i}.png').write_bytes(base64.b64decode(d.split(',',1)[1]))
    print('Einzelaufnahmen:',len(shots))
    print('Aufnahme:',res)
    for _ in range(60):
        pdfs=list(dl.glob('**/*.pdf'))+list(dl.glob('**/*'))
        if any(str(x).endswith('.pdf') for x in pdfs): break
        time.sleep(0.5)
    ctx.close()
pdfs=[x for x in dl.rglob('*') if x.is_file()]
print('Dateien:',[x.name for x in pdfs])
for x in pdfs:
    if x.suffix.lower()=='.pdf' or x.read_bytes()[:4]==b'%PDF':
        dst=OUT/f'{LABEL}.pdf'; shutil.copy(x,dst); print('PDF ->',dst); break
shutil.rmtree(prof,ignore_errors=True); shutil.rmtree(ext.parent,ignore_errors=True)
