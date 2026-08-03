#!/usr/bin/env python3
"""Schnelllauf: Store-Installation + Capture in einem Zug, mit Zeitmessung.

    python3 schnelllauf-agent-install.py firefox
    python3 schnelllauf-agent-install.py chrome
    python3 schnelllauf-agent-install.py both --json

Unterschiede zu messung-agent-install-als-nutzer.py: Tempo und Robustheit.

- Fenster werden an (0,0) auf 1400x900 fixiert; alle Klicks sind
  FENSTER-relative Koordinaten (clickrel.ps1 rechnet per ClientToScreen um).
  Damit haengen die Koordinaten nur noch vom Fenster-Layout ab, nicht von
  Bildschirmaufloesung oder Skalierung.
- Jeder Helfer ruft zuerst SetProcessDPIAware() — sonst liefert Windows bei
  125/150 % Skalierung virtualisierte Werte und Koordinaten verrutschen.
  (Hier: 96 dpi = 100 %, also 1:1. Auf anderen Maschinen nicht.)
- Verifikation ueber Dateien (extensions.json / Extensions-Dir / PDF-Kopf)
  mit engem Polling — kein Warten auf geratene Zeiten, keine Screenshots
  mitten im Lauf. Ein einziger winshot (PrintWindow, kein Fokuswechsel)
  prueft Dialog-Zustaende bei Bedarf.
- Ausgabe: Schritt-Laufzeiten in Sekunden, fuer das Zeitbudget im Protokoll.

Koordinaten stammen aus dem gemessenen 1400x900-Fenster (protokoll-
agent-install.md). Sie gelten bei fixierter Fenstergroesse, gleicher
Store-Seiten-Sprache (Firefox AMO en-US, CWS de-DE) und gleichem
Seitenlayout. Abweichung = einmal winshot, neu ablesen, Tabelle unten
pflegen.
"""
import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

HIER = Path(__file__).resolve().parent
W_TEMP = r"C:\Users\HOLO\AppData\Local\Temp\pl-agent-speed"
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

L_TEMP = Path(f"/mnt/c/Users/{_BENUTZER}/AppData/Local/Temp/pl-agent-speed")
FF_PROFIL_W = rf"{W_TEMP}\ff-profil"
CH_PROFIL_W = rf"{W_TEMP}\ch-profil"
FF_EXE = r"C:\Program Files\Mozilla FirefoxESR\firefox.exe"
CH_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
AMO = "https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/"
CWS = "https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn"
GECKO_ID = "pageshot-pdf@bubu89.local"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
DOWNLOAD_DIR = Path("/mnt/d/Downloads/Full Page PDF Snap")

# Fenster-relative Koordinaten, Fenster 1400x900 an (0,0).
FF_KOORD = {
    "tou_continue": (649, 330),   # nur noetig, wenn der ToU-Dialog kommt
    "add": (1115, 340),
    "confirm": (1248, 386),
    "adressleiste": (550, 65),
    "doorhanger_ok": (1352, 206),
}
CH_KOORD = {
    "seite_mitte": (500, 550),
    "consent_ablehnen": (595, 675),
    "add": (980, 241),
    "confirm": (702, 325),
}

_DPI = "[DllImport(\"user32.dll\")] public static extern bool SetProcessDPIAware();"
_FINDE = """
$target=[IntPtr]::Zero
$liste = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($item in $liste) {
  $proc = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
  if ($proc -and $proc.MainWindowHandle -ne 0) { $target=$proc.MainWindowHandle }
}
if ($target -eq [IntPtr]::Zero) { Write-Output 'NOWINDOW'; exit 1 }
"""

PS = {
    "clickrel.ps1": f"""param([string]$Match,[int]$X,[int]$Y)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class CR {{{_DPI}
 [DllImport("user32.dll")] public static extern bool ClientToScreen(IntPtr h, ref PT p);
 [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
 [DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,IntPtr e);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int s);
 [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r);
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
 public struct PT {{ public int X, Y; }}
}}'
[CR]::SetProcessDPIAware() | Out-Null
{_FINDE}
[CR]::ShowWindow($target, 9) | Out-Null
[CR]::MoveWindow($target, 0, 0, 1400, 900, $true) | Out-Null
$zero=[uint32]0
$cur=[CR]::GetCurrentThreadId()
$fgH=[CR]::GetForegroundWindow()
$fgT=[CR]::GetWindowThreadProcessId($fgH,[ref]$zero)
$tgtT=[CR]::GetWindowThreadProcessId($target,[ref]$zero)
[CR]::AttachThreadInput($cur,$fgT,$true) | Out-Null
[CR]::AttachThreadInput($cur,$tgtT,$true) | Out-Null
[CR]::BringWindowToTop($target) | Out-Null
[CR]::SetForegroundWindow($target) | Out-Null
[CR]::AttachThreadInput($cur,$fgT,$false) | Out-Null
[CR]::AttachThreadInput($cur,$tgtT,$false) | Out-Null
Start-Sleep -Milliseconds 350
if ([CR]::GetForegroundWindow() -ne $target) {{ Write-Output 'NOTFG'; exit 2 }}
$pt = New-Object CR+PT; $pt.X=$X; $pt.Y=$Y
[CR]::ClientToScreen($target, [ref]$pt) | Out-Null
[CR]::SetCursorPos($pt.X, $pt.Y) | Out-Null
Start-Sleep -Milliseconds 150
[CR]::mouse_event(2,0,0,0,[IntPtr]::Zero)
Start-Sleep -Milliseconds 60
[CR]::mouse_event(4,0,0,0,[IntPtr]::Zero)
Write-Output 'SENT'
""",
    "focuskey.ps1": f"""param([string]$Match,[string]$Keys)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class W {{{_DPI}
 [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
 [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
 [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h,int s);
 [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h,int x,int y,int w,int ht,bool r);
 [DllImport("user32.dll")] public static extern uint GetWindowThreadProcessId(IntPtr h, out uint pid);
 [DllImport("user32.dll")] public static extern bool AttachThreadInput(uint a, uint b, bool f);
 [DllImport("kernel32.dll")] public static extern uint GetCurrentThreadId();
 [DllImport("user32.dll")] public static extern bool BringWindowToTop(IntPtr h);
}}'
Add-Type -AssemblyName System.Windows.Forms
[W]::SetProcessDPIAware() | Out-Null
{_FINDE}
[W]::ShowWindow($target, 9) | Out-Null
[W]::MoveWindow($target, 0, 0, 1400, 900, $true) | Out-Null
Start-Sleep -Milliseconds 250
$zero=[uint32]0
$cur=[W]::GetCurrentThreadId()
$fgH=[W]::GetForegroundWindow()
$fgT=[W]::GetWindowThreadProcessId($fgH,[ref]$zero)
$tgtT=[W]::GetWindowThreadProcessId($target,[ref]$zero)
[W]::AttachThreadInput($cur,$fgT,$true) | Out-Null
[W]::AttachThreadInput($cur,$tgtT,$true) | Out-Null
[W]::BringWindowToTop($target) | Out-Null
[W]::SetForegroundWindow($target) | Out-Null
[W]::AttachThreadInput($cur,$fgT,$false) | Out-Null
[W]::AttachThreadInput($cur,$tgtT,$false) | Out-Null
Start-Sleep -Milliseconds 350
if ([W]::GetForegroundWindow() -ne $target) {{ Write-Output 'NOTFG'; exit 2 }}
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Milliseconds 250
if ([W]::GetForegroundWindow() -ne $target) {{ Write-Output 'LOSTFG'; exit 3 }}
Write-Output 'SENT'
""",
    "closewin.ps1": f"""param([string]$Match)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class C {{ [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }}'
{_FINDE.replace('if ($target -eq [IntPtr]::Zero) { Write-Output \'NOWINDOW\'; exit 1 }', 'if ($target -eq [IntPtr]::Zero) { exit 0 }')}
[C]::PostMessage($target, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
""",
    "winshot.ps1": f"""param([string]$Match,[string]$Out)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class P {{{_DPI}
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
 public struct R {{ public int Left,Top,Right,Bottom; }}
}}'
Add-Type -AssemblyName System.Drawing
[P]::SetProcessDPIAware() | Out-Null
{_FINDE}
$r = New-Object P+R
[P]::GetWindowRect($target,[ref]$r) | Out-Null
$w = $r.Right - $r.Left; $h = $r.Bottom - $r.Top
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$dc = $g.GetHdc()
$null = [P]::PrintWindow($target, $dc, 3)
$g.ReleaseHdc($dc)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
Write-Output "OK $w x $h"
""",
}


def helfer_anlegen():
    L_TEMP.mkdir(parents=True, exist_ok=True)
    for name, inhalt in PS.items():
        (L_TEMP / name).write_text(inhalt, encoding="ascii")


def ps(datei, *args):
    return subprocess.run(["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass",
                           "-File", f"{W_TEMP}\\{datei}"] + [str(a) for a in args],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=90)


def starte(exe, arg_liste):
    args_ps = ",".join(f"'{a}'" for a in arg_liste)
    r = subprocess.run(["powershell.exe", "-NoProfile", "-Command",
                        f"$p = Start-Process -FilePath '{exe}' -ArgumentList {args_ps} -PassThru; $p.Id"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    return int(r.stdout.strip())


def poll(fn, timeout_s, intervall=0.6):
    ende = time.time() + timeout_s
    while time.time() < ende:
        v = fn()
        if v:
            return v
        time.sleep(intervall)
    return None


def w_l_pfad(w_pfad):
    return Path("/mnt/c") / w_pfad.replace("C:\\", "").replace("\\", "/")


def ff_version():
    datei = w_l_pfad(FF_PROFIL_W) / "extensions.json"
    if not datei.exists():
        return None
    try:
        daten = json.loads(datei.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    for a in daten.get("addons", []):
        if a.get("id") == GECKO_ID and a.get("active"):
            return a.get("version")
    return None


def ch_version():
    basis = w_l_pfad(CH_PROFIL_W) / "Default" / "Extensions" / CWS_ID
    if not basis.exists():
        return None
    for vd in sorted(basis.iterdir(), reverse=True):
        if (vd / "manifest.json").exists():
            return vd.name
    return None


ZEITEN = []


def schritt(name, fn, ok_wert=True):
    t0 = time.time()
    erg = fn()
    dt = time.time() - t0
    ok = (erg == ok_wert) if ok_wert is not True else bool(erg)
    ZEITEN.append({"schritt": name, "sekunden": round(dt, 1), "ok": bool(ok), "wert": str(erg)[:80]})
    print(f"  {'OK ' if ok else '-- '} {name:34} {dt:6.1f}s  {str(erg)[:60]}")
    return erg


def lauf_firefox():
    print("== Firefox ==")
    w_l_pfad(FF_PROFIL_W).mkdir(parents=True, exist_ok=True)
    (w_l_pfad(FF_PROFIL_W) / "user.js").write_text(
        'user_pref("browser.shell.checkDefaultBrowser", false);\n'
        'user_pref("startup.homepage_welcome_url", "");\n'
        'user_pref("browser.aboutwelcome.enabled", false);\n', encoding="ascii")
    schritt("start", lambda: starte(FF_EXE, ["-no-remote", "-profile", FF_PROFIL_W, AMO]) > 0)
    # Fenster da? ToU-Dialog kommt beim ersten Lauf des Profils — abwarten
    # und per winshot pruefen, ob er steht (kein Fokuswechsel noetig).
    schritt("warte fenster", lambda: poll(lambda: ps("winshot.ps1", "ff-profil", f"{W_TEMP}\\s.png").returncode == 0, 30))
    tou = (L_TEMP / "s.png")
    if tou.exists() and tou.stat().st_size > 200000:  # grosses Bild = Dialog sichtbar? grob
        schritt("tou continue", lambda: ps("clickrel.ps1", "ff-profil", *FF_KOORD["tou_continue"]).returncode)
        time.sleep(2)
    schritt("klick add", lambda: ps("clickrel.ps1", "ff-profil", *FF_KOORD["add"]).returncode)
    time.sleep(3)
    schritt("klick confirm", lambda: ps("clickrel.ps1", "ff-profil", *FF_KOORD["confirm"]).returncode)
    schritt("install verifiziert", lambda: poll(ff_version, 60))
    schritt("nav+kommando", lambda: (
        ps("clickrel.ps1", "ff-profil", *FF_KOORD["adressleiste"]).returncode == 0
        and ps("focuskey.ps1", "ff-profil", "example.com{ENTER}").returncode == 0))
    time.sleep(5)
    vorher = set(DOWNLOAD_DIR.glob("example_com*.pdf"))
    schritt("alt+shift+y", lambda: ps("focuskey.ps1", "ff-profil", "%+Y").returncode)
    pdf = schritt("pdf verifiziert", lambda: poll(
        lambda: next((p for p in DOWNLOAD_DIR.glob("example_com*.pdf") if p not in vorher), None), 90))
    if pdf:
        print(f"       {pdf.name}, {pdf.stat().st_size} bytes, kopf={pdf.open('rb').read(5)!r}")
    schritt("sauber schliessen", lambda: ps("closewin.ps1", "ff-profil").returncode)
    time.sleep(8)
    schritt("persistenz", ff_version)


def lauf_chrome():
    print("== Chrome ==")
    w_l_pfad(CH_PROFIL_W).mkdir(parents=True, exist_ok=True)
    schritt("start", lambda: starte(CH_EXE, [f"--user-data-dir={CH_PROFIL_W}", "--no-first-run",
                                             "--no-default-browser-check", CWS]) > 0)
    schritt("warte fenster", lambda: poll(lambda: ps("winshot.ps1", "ch-profil", f"{W_TEMP}\\c.png").returncode == 0, 30))
    # Consent steht auf neuen Profilen praktisch immer; der Klick ins Leere
    # auf derselben Position ist auf der CWS-Seite harmlos (Seitenmitte).
    schritt("scroll ende", lambda: (ps("clickrel.ps1", "ch-profil", *CH_KOORD["seite_mitte"]).returncode == 0
                                    and ps("focuskey.ps1", "ch-profil", "{END}").returncode == 0))
    schritt("consent ablehnen", lambda: ps("clickrel.ps1", "ch-profil", *CH_KOORD["consent_ablehnen"]).returncode)
    time.sleep(6)
    schritt("klick add", lambda: ps("clickrel.ps1", "ch-profil", *CH_KOORD["add"]).returncode)
    time.sleep(3)
    schritt("klick confirm", lambda: ps("clickrel.ps1", "ch-profil", *CH_KOORD["confirm"]).returncode)
    schritt("install verifiziert", lambda: poll(ch_version, 60))
    vorher = set(DOWNLOAD_DIR.glob("example_com*.pdf"))
    schritt("schliessen+neustart", lambda: (
        ps("closewin.ps1", "ch-profil").returncode == 0
        and (time.sleep(6) or True)
        and starte(CH_EXE, [f"--user-data-dir={CH_PROFIL_W}", "--no-first-run",
                            "--no-default-browser-check", "https://example.com/"]) > 0))
    time.sleep(8)
    schritt("alt+shift+y", lambda: ps("focuskey.ps1", "ch-profil", "%+Y").returncode)
    pdf = schritt("pdf verifiziert", lambda: poll(
        lambda: next((p for p in DOWNLOAD_DIR.glob("example_com*.pdf") if p not in vorher), None), 90))
    if pdf:
        print(f"       {pdf.name}, {pdf.stat().st_size} bytes, kopf={pdf.open('rb').read(5)!r}")
    schritt("sauber schliessen", lambda: ps("closewin.ps1", "ch-profil").returncode)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("browser", choices=["firefox", "chrome", "both"])
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    helfer_anlegen()
    t0 = time.time()
    if args.browser in ("firefox", "both"):
        lauf_firefox()
    if args.browser in ("chrome", "both"):
        lauf_chrome()
    gesamt = time.time() - t0
    print(f"\nGesamt: {gesamt:.1f}s")
    if args.json:
        (L_TEMP / "zeiten.json").write_text(json.dumps(
            {"gesamt_sekunden": round(gesamt, 1), "schritte": ZEITEN}, indent=2), encoding="utf-8")
        print(f"Zeiten: {L_TEMP / 'zeiten.json'}")
    return 0 if all(z["ok"] for z in ZEITEN) else 1


if __name__ == "__main__":
    sys.exit(main())
