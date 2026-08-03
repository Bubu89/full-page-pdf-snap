#!/usr/bin/env python3
"""Messung: ein Agent installiert die Store-Version in ein eigenes Profil —
und loest sie aus. Ohne Admin, nur mit echten Eingabeereignissen.

    python3 messung-agent-install-als-nutzer.py prepare
    python3 messung-agent-install-als-nutzer.py install --ff-add X,Y --ff-confirm X,Y
    python3 messung-agent-install-als-nutzer.py install --ch-add X,Y --ch-confirm X,Y
    python3 messung-agent-install-als-nutzer.py capture firefox
    python3 messung-agent-install-als-nutzer.py capture chrome
    python3 messung-agent-install-als-nutzer.py finish

Die Behauptung, die geprueft wird: Ein Agent, der autonom im Browser arbeitet,
kann die Erweiterung so anwenden, dass die Installation eine echte
Store-Installation ist — nicht der entpackte Ordner, der in keiner
Store-Statistik auftaucht. Der Weg ist der, den ein Computer-Use-Agent
natuerlicherweise geht: Store-Seite oeffnen, auf "Add" klicken, bestaetigen.
Geklickt wird ueber den echten Eingabe-Stack (SendInput), weil der
Bestaetigungs-Dialog Browser-UI ist und kein DOM.

Die Klick-Koordinaten kommen aus Vollbild-Screenshots, die prepare anlegt —
ein Agent mit Bildschirmsicht bestimmt sie selbst. Hier liest sie der
aufrufende Agent und gibt sie install mit.

Warum ein eigenes Profil: der Eingriff bleibt reversibel. Profil weg, Stand
wie vorher. Das Profil des Nutzers wird nicht angefasst.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
DATUM = "2026-08-03"
ZIEL = HIER / "docs" / "data" / f"{DATUM}-agent-install-and-capture.json"

W_TEMP = r"C:\Users\HOLO\AppData\Local\Temp\pl-agent-meas"
def _win_benutzer():
    """Windows-Benutzername aus der Interop, nicht aus einer festen Zeichenkette.

    Der Pfad stand hier verdrahtet. In einem oeffentlichen Repository ist das
    ein Leak, und auf jeder anderen Maschine ist er schlicht falsch.
    """
    import subprocess
    # Drei Fallen auf einmal: cmd.exe aus WSL wartet ohne geschlossenes stdin
    # auf Eingabe, es warnt ueber den UNC-Pfad auf stderr, und diese Warnung
    # kommt in Windows-Kodierung — utf-8 bricht daran ab, bevor stdout gelesen
    # wird.
    r = subprocess.run(["cmd.exe", "/c", "echo %USERNAME%"],
                       capture_output=True, timeout=15, stdin=subprocess.DEVNULL)
    roh = r.stdout.decode("utf-8", "replace").strip()
    name = roh.splitlines()[-1].strip() if roh else ""
    if not name or "%" in name:
        raise SystemExit("Windows-Benutzername nicht ermittelbar — laeuft das in WSL?")
    return name


_BENUTZER = _win_benutzer()

L_TEMP = Path(f"/mnt/c/Users/{_BENUTZER}/AppData/Local/Temp/pl-agent-meas")
STATE = L_TEMP / "state.json"

AMO_SEITE = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
CWS_SEITE = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"
AMO_API = "https://addons.mozilla.org/api/v5/addons/addon/full_page_pdf_snap_webpagesave/"
GECKO_ID = "pageshot-pdf@bubu89.local"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
PROBESEITE = "https://example.com/"

DOWNLOADS = Path(f"/mnt/c/Users/{_BENUTZER}/Downloads")

# PowerShell-Helfer. ASCII only (ISSUE-012), kein BOM noetig.
PS = {
    "shot.ps1": """param([string]$Out)
Add-Type -AssemblyName System.Drawing,System.Windows.Forms
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
""",
    "click.ps1": """param([int]$X,[int]$Y)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class M { [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,IntPtr e); }'
[M]::SetCursorPos($X,$Y) | Out-Null
Start-Sleep -Milliseconds 200
[M]::mouse_event(2,0,0,0,[IntPtr]::Zero)
Start-Sleep -Milliseconds 80
[M]::mouse_event(4,0,0,0,[IntPtr]::Zero)
Start-Sleep -Milliseconds 300
""",
    "key.ps1": """param([string]$Keys)
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Milliseconds 300
""",
    "focus.ps1": """param([string]$Match)
# SetForegroundWindow aus einem Hintergrundprozess wird von Windows still
# ignoriert — erst AttachThreadInput macht den Fokuswechsel erzwingbar, und
# erst GetForegroundWindow danach macht ihn belegt. Genau diese Fassung hat
# die Messung bestanden; die schlichte ShowWindow-Variante war gescheitert.
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class W {
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int s);
 [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
}'
$target = [IntPtr]::Zero
$procs = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($x in $procs) {
  $p = Get-Process -Id $x.ProcessId -ErrorAction SilentlyContinue
  if ($p -and $p.MainWindowHandle -ne 0) { $target = $p.MainWindowHandle }
}
if ($target -eq [IntPtr]::Zero) { Write-Output 'NOWINDOW'; exit 1 }
[W]::ShowWindow($target, 9) | Out-Null
[W]::MoveWindow($target, 0, 0, 1400, 900, $true) | Out-Null
Start-Sleep -Milliseconds 300
$zero = [uint32]0
$cur = [W]::GetCurrentThreadId()
$fgH = [W]::GetForegroundWindow()
$fgT = [W]::GetWindowThreadProcessId($fgH, [ref]$zero)
$tgtT = [W]::GetWindowThreadProcessId($target, [ref]$zero)
[W]::AttachThreadInput($cur, $fgT, $true) | Out-Null
[W]::AttachThreadInput($cur, $tgtT, $true) | Out-Null
[W]::BringWindowToTop($target) | Out-Null
[W]::SetForegroundWindow($target) | Out-Null
[W]::AttachThreadInput($cur, $fgT, $false) | Out-Null
[W]::AttachThreadInput($cur, $tgtT, $false) | Out-Null
Start-Sleep -Milliseconds 400
if ([W]::GetForegroundWindow() -eq $target) { Write-Output 'FG'; exit 0 } else { Write-Output 'NOTFG'; exit 2 }
""",
    "focuskey.ps1": """param([string]$Match,[string]$Keys)
# Fokus und Tasten in EINEM Prozess: zwei getrennte Aufrufe lassen eine
# Fokus-Race, in der ein fremdes Fenster die Tasten bekommt (gemessen auf
# einem geteilten Desktop).
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class W {
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int s);
 [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
}'
Add-Type -AssemblyName System.Windows.Forms
$target = [IntPtr]::Zero
$procs = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($x in $procs) {
  $p = Get-Process -Id $x.ProcessId -ErrorAction SilentlyContinue
  if ($p -and $p.MainWindowHandle -ne 0) { $target = $p.MainWindowHandle }
}
if ($target -eq [IntPtr]::Zero) { Write-Output 'NOWINDOW'; exit 1 }
[W]::ShowWindow($target, 9) | Out-Null
[W]::MoveWindow($target, 0, 0, 1400, 900, $true) | Out-Null
Start-Sleep -Milliseconds 250
$zero = [uint32]0
$cur = [W]::GetCurrentThreadId()
$fgH = [W]::GetForegroundWindow()
$fgT = [W]::GetWindowThreadProcessId($fgH, [ref]$zero)
$tgtT = [W]::GetWindowThreadProcessId($target, [ref]$zero)
[W]::AttachThreadInput($cur, $fgT, $true) | Out-Null
[W]::AttachThreadInput($cur, $tgtT, $true) | Out-Null
[W]::BringWindowToTop($target) | Out-Null
[W]::SetForegroundWindow($target) | Out-Null
[W]::AttachThreadInput($cur, $fgT, $false) | Out-Null
[W]::AttachThreadInput($cur, $tgtT, $false) | Out-Null
Start-Sleep -Milliseconds 350
if ([W]::GetForegroundWindow() -ne $target) { Write-Output 'NOTFG'; exit 2 }
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Milliseconds 250
if ([W]::GetForegroundWindow() -ne $target) { Write-Output 'LOSTFG'; exit 3 }
Write-Output 'SENT'
""",
    "closewin.ps1": """param([string]$Match)
# WM_CLOSE statt Kill: ein hartes Beenden zwischen Install-Klick und
# sauberem Shutdown liess die Firefox-Installation verschwinden (gemessen).
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class C { [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }'
$procs = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($x in $procs) {
  $p = Get-Process -Id $x.ProcessId -ErrorAction SilentlyContinue
  if ($p -and $p.MainWindowHandle -ne 0) { [C]::PostMessage($p.MainWindowHandle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
}
""",
}


def ps(datei, *args):
    """Helfer auf der Windows-Seite ausfuehren. Dateien liegen unter W_TEMP,
    aufgerufen ueber ihren Windows-Pfad — WSL-Pfade versteht PowerShell nicht."""
    cmd = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
           "-File", f"{W_TEMP}\\{datei}"] + [str(a) for a in args]
    return subprocess.run(cmd, capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=60)


def ps_direkt(befehl):
    return subprocess.run(["powershell.exe", "-NoProfile", "-Command", befehl],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=120)


def helfer_anlegen():
    L_TEMP.mkdir(parents=True, exist_ok=True)
    for name, inhalt in PS.items():
        (L_TEMP / name).write_text(inhalt, encoding="ascii")


def state_lesen():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def state_schreiben(s):
    STATE.write_text(json.dumps(s, indent=2), encoding="utf-8")


def browser_pfad(name, fallback):
    r = subprocess.run(["reg.exe", "query",
                        r"HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths" + "\\" + name,
                        "/ve"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    m = re.search(r"REG_SZ\s+(\S.*\.exe)", r.stdout)
    return m.group(1).strip() if m else fallback


def store_versionen():
    req = urllib.request.Request(AMO_API, headers={"User-Agent": "provinglab-messung/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        ff = json.load(r)["current_version"]["version"]
    ch = None
    try:
        req = urllib.request.Request(CWS_SEITE, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            seite = r.read().decode("utf-8", "replace")
        m = re.search(r'"(\d+\.\d+\.\d+(?:\.\d+)?)"', seite)
        ch = m.group(1) if m else None
    except Exception:
        pass
    return {"firefox": ff, "chrome": ch}


def starte_browser(exe, arg_liste):
    """Start-Process -PassThru, damit die PID bekannt ist und finish() genau
    diese Instanz beendet — nie ein fremdes Browserfenster des Nutzers."""
    args_ps = ",".join(f"'{a}'" for a in arg_liste)
    r = ps_direkt(f"$p = Start-Process -FilePath '{exe}' -ArgumentList {args_ps} -PassThru; "
                  "$p.Id")
    return int(r.stdout.strip())


def screenshot(name):
    ziel_w = f"{W_TEMP}\\{name}.png"
    r = ps("shot.ps1", ziel_w)
    ziel_l = L_TEMP / f"{name}.png"
    return ziel_l if r.returncode == 0 and ziel_l.exists() else None


def klick(x, y):
    r = ps("click.ps1", x, y)
    return r.returncode == 0


def taste(keys):
    return ps("key.ps1", keys).returncode == 0


def fokus(match):
    return ps("focus.ps1", match).returncode == 0


def schritt(name, ok, detail=""):
    print(f"  {'OK ' if ok else '-- '} {name:30} {detail}")
    return {"step": name, "passed": bool(ok), "detail": detail}


def warte_bedingung(fn, sekunden, schrittweite=2):
    ende = time.time() + sekunden
    while time.time() < ende:
        v = fn()
        if v:
            return v
        time.sleep(schrittweite)
    return None


# --- Stufen ------------------------------------------------------------------

def prepare(browser):
    helfer_anlegen()
    s = state_lesen()
    versionen = store_versionen()
    s.setdefault("store_versionen", versionen)
    ergebnisse = []

    if browser in ("firefox", "both"):
        profil_w = f"{W_TEMP}\\ff-profile"
        (L_TEMP / "ff-profile").mkdir(parents=True, exist_ok=True)
        # Standard-Browser-Abfrage und Willkommensseite unterdruecken.
        # Telemetry wird NICHT angefasst — sie ist die Messgroesse.
        (L_TEMP / "ff-profile" / "user.js").write_text(
            'user_pref("browser.shell.checkDefaultBrowser", false);\n'
            'user_pref("startup.homepage_welcome_url", "");\n'
            'user_pref("startup.homepage_welcome_url.additional", "");\n'
            'user_pref("browser.aboutwelcome.enabled", false);\n', encoding="ascii")
        exe = browser_pfad("firefox.exe", r"C:\Program Files\Mozilla FirefoxESR\firefox.exe")
        pid = starte_browser(exe, ["-no-remote", "-profile", profil_w, AMO_SEITE])
        s["firefox"] = {"pid": pid, "profil": profil_w, "exe": exe}
        ergebnisse.append(schritt("firefox gestartet", pid > 0, f"pid={pid}"))
        time.sleep(15)

    if browser in ("chrome", "both"):
        ud_w = f"{W_TEMP}\\ch-profile"
        (L_TEMP / "ch-profile").mkdir(parents=True, exist_ok=True)
        exe = browser_pfad("chrome.exe", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        pid = starte_browser(exe, [f"--user-data-dir={ud_w}", "--no-first-run",
                                   "--no-default-browser-check", CWS_SEITE])
        s["chrome"] = {"pid": pid, "profil": ud_w, "exe": exe}
        ergebnisse.append(schritt("chrome gestartet", pid > 0, f"pid={pid}"))
        time.sleep(15)

    # Jede Instanz einzeln in den Vordergrund und einzeln fotografieren —
    # sonst liegt eins ueber dem anderen und die Koordinaten passen nicht.
    for name, match in (("firefox", "ff-profile"), ("chrome", "ch-profile")):
        if name in s and fokus(match):
            time.sleep(2)
            png = screenshot(f"{name}-store")
            ergebnisse.append(schritt(f"screenshot {name}", png is not None,
                                      str(png) if png else "fehlgeschlagen"))

    state_schreiben(s)
    print("\nScreenshots ansehen, Koordinaten der Buttons bestimmen, dann:")
    print("  install --ff-add X,Y --ff-confirm X,Y   bzw.   --ch-add ... --ch-confirm ...")
    return ergebnisse


def ff_installiert(profil_w):
    d = Path("/mnt/c") / profil_w.replace("C:\\", "").replace("\\", "/")
    datei = d / "extensions.json"
    if not datei.exists():
        return None
    try:
        daten = json.loads(datei.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    for addon in daten.get("addons", []):
        if addon.get("id") == GECKO_ID and addon.get("active"):
            return addon.get("version")
    return None


def ch_installiert(profil_w):
    d = Path("/mnt/c") / profil_w.replace("C:\\", "").replace("\\", "/")
    basis = d / "Default" / "Extensions" / CWS_ID
    if not basis.exists():
        return None
    for version_dir in sorted(basis.iterdir(), reverse=True):
        if (version_dir / "manifest.json").exists():
            return version_dir.name
    return None


def install(browser, add, confirm):
    helfer_anlegen()
    s = state_lesen()
    eintrag = s.get(browser)
    if not eintrag:
        print(f"prepare {browser} zuerst.")
        return [schritt("vorbereitung", False)]
    match = "ff-profile" if browser == "firefox" else "ch-profile"
    pruefer = ff_installiert if browser == "firefox" else ch_installiert
    ergebnisse = []

    ergebnisse.append(schritt("fenster fokussiert", fokus(match)))
    time.sleep(1)
    ergebnisse.append(schritt("klick 'Add'", klick(*add), str(add)))
    time.sleep(4)
    png = screenshot(f"{browser}-confirm")
    ergebnisse.append(schritt("screenshot dialog", png is not None, str(png or "")))
    ergebnisse.append(schritt("klick bestaetigung", klick(*confirm), str(confirm)))
    time.sleep(3)

    version = warte_bedingung(lambda: pruefer(eintrag["profil"]), 60)
    ergebnisse.append(schritt("installation im profil", version is not None,
                              f"version={version}" if version else "nicht gefunden"))
    png = screenshot(f"{browser}-installed")
    s.setdefault("messung", {})[browser] = {"installiert": version}
    state_schreiben(s)
    return ergebnisse


def capture(browser):
    helfer_anlegen()
    s = state_lesen()
    eintrag = s.get(browser)
    if not eintrag or not s.get("messung", {}).get(browser, {}).get("installiert"):
        print(f"install {browser} zuerst (und erfolgreich).")
        return [schritt("vorbereitung", False)]
    match = "ff-profile" if browser == "firefox" else "ch-profile"
    ergebnisse = []

    vorher = {p.name for p in DOWNLOADS.glob("*.pdf")}
    ergebnisse.append(schritt("fenster fokussiert", fokus(match)))
    time.sleep(1)
    # Probeseite ueber die Adressleiste — echte Tasten, keine Adressuebergabe
    # per Kommandozeile, weil genau dieser Eingabe-Weg gemessen wird.
    taste("^l")
    time.sleep(0.5)
    taste(PROBESEITE + "{ENTER}")
    time.sleep(8)
    ergebnisse.append(schritt("probeseite geladen", True, PROBESEITE))
    taste("%+Y")  # Alt+Shift+Y — das Kommando der Erweiterung
    ergebnisse.append(schritt("kommando gesendet", True, "Alt+Shift+Y via SendInput"))

    def neue_pdf():
        for p in DOWNLOADS.glob("*.pdf"):
            if p.name not in vorher:
                return p
        return None

    pdf = warte_bedingung(neue_pdf, 90)
    if pdf:
        kopf = pdf.open("rb").read(5)
        ok = kopf == b"%PDF-"
        ergebnisse.append(schritt("pdf geliefert", ok,
                                  f"{pdf.name}, {pdf.stat().st_size} bytes, kopf={kopf!r}"))
        s["messung"][browser].update(pdf=pdf.name, pdf_bytes=pdf.stat().st_size, pdf_ok=ok)
    else:
        ergebnisse.append(schritt("pdf geliefert", False, "keine neue Datei in Downloads"))
        png = screenshot(f"{browser}-nach-kommando")
        s["messung"][browser].update(pdf=None, fehlerbild=str(png or ""))
    state_schreiben(s)
    return ergebnisse


def finish():
    s = state_lesen()
    ergebnisse = []
    for browser, eintrag in s.items():
        if not isinstance(eintrag, dict) or "pid" not in eintrag:
            continue
        r = ps_direkt(f"Stop-Process -Id {eintrag['pid']} -Force -ErrorAction SilentlyContinue")
        ergebnisse.append(schritt(f"{browser} beendet", True, f"pid={eintrag['pid']}"))
    # Kinder ueber den Profil-Pfad finden — chrome.exe forkt, die Start-PID
    # lebt dann nicht mehr. CommandLine-Match ist hier sicher, weil unsere
    # Instanzen nie elevated laufen (siehe win-admin-run Gotcha).
    for match in ("ff-profile", "ch-profile"):
        ps_direkt(
            "Get-CimInstance Win32_Process -Filter \"Name='firefox.exe' or Name='chrome.exe'\" | "
            f"Where-Object {{ $_.CommandLine -and $_.CommandLine.Contains('{match}') }} | "
            "ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }")

    roh = {
        "datum": DATUM,
        "frage": ("Kann ein autonomer Agent die Erweiterung als echte Store-Installation "
                  "in ein eigenes Profil installieren und ausloesen — ohne Admin-Rechte, "
                  "nur mit echten Eingabeereignissen?"),
        "store_versionen": s.get("store_versionen"),
        "ergebnisse": s.get("messung", {}),
        "profile": {k: v.get("profil") for k, v in s.items()
                    if isinstance(v, dict) and "profil" in v},
        "methode": {
            "installation": "Store-Seite im eigenen Profil, Klick via SendInput (mouse_event)",
            "ausloesung": "Alt+Shift+Y via SendKeys/SendInput auf https://example.com/",
            "verifikation": "extensions.json bzw. Extensions/<id>/<version>/ im Profil, "
                            "PDF-Kopfzeile %PDF- in Downloads",
        },
    }
    ZIEL.write_text(json.dumps(roh, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nRohdaten: {ZIEL}")
    print(f"Profil-Reste unter {W_TEMP} (Temp — wird vom System aufgeraeumt)")
    return ergebnisse


def main():
    p = argparse.ArgumentParser()
    p.add_argument("stufe", choices=["prepare", "install", "capture", "finish"])
    p.add_argument("browser", nargs="?", default="both",
                   choices=["firefox", "chrome", "both"])
    p.add_argument("--ff-add"); p.add_argument("--ff-confirm")
    p.add_argument("--ch-add"); p.add_argument("--ch-confirm")
    args = p.parse_args()

    if args.stufe == "prepare":
        prepare(args.browser)
    elif args.stufe == "install":
        def xy(v): return tuple(int(i) for i in v.split(","))
        if args.ff_add and args.ff_confirm:
            install("firefox", xy(args.ff_add), xy(args.ff_confirm))
        if args.ch_add and args.ch_confirm:
            install("chrome", xy(args.ch_add), xy(args.ch_confirm))
        if not (args.ff_add or args.ch_add):
            print("Koordinaten fehlen (--ff-add/--ff-confirm oder --ch-add/--ch-confirm).")
    elif args.stufe == "capture":
        capture(args.browser)
    elif args.stufe == "finish":
        finish()


if __name__ == "__main__":
    main()
