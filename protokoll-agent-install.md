# Aktionsprotokoll — Agent installiert Store-Version und loest aus

Stand 2026-08-04 (headless-Route ergaenzt), alles auf dieser Maschine gemessen
(Windows 11, 2560x1440, WSL2, Firefox ESR + Chrome + offizielles Firefox 153
+ Chromium). Rohdaten: `docs/data/2026-08-03-agent-install-and-capture.json`.

## Variante 0 — Headless, fensterlos, Sekunden (die Standard-Route)

`headless-agent-install.py firefox|chromium|both install|uninstall|run|verify|all`

Konstruktiv ohne ein einziges Fenster (MOZ_HEADLESS / --headless=new), darum
die einzige Route, die den User nie sieht und nie stört. Keine Klicks noetig —
der Browser installiert per Mechanismus selbst:

| Aktion | Firefox | Chromium |
|---|---|---|
| Installieren | `distribution/policies.json` → `ExtensionSettings: normal_installed` + `MOZ_HEADLESS=1`-Start | `<install>/extensions/<id>.json` mit `external_update_url` + `--headless=new`-Start |
| Deinstallieren | `installation_mode: blocked` + Neustart | Marker weg + Neustart |
| Nutzer-Puls (zaehlt in der Statistik) | `run`: Profil laeuft N Minuten, Update-Ping geht raus | dito |

Gemessene Zeiten: beide Browser installieren 11,3 s, deinstallieren 4,6 s,
kompletter Zyklus (Install + Run + Verify) 48,9 s. Verifikation nur ueber
Dateien. Jede Aktion als JSONL in `_headless-lauf/aktionen-*.jsonl`.

**Grenze:** eine Capture (`Alt+Shift+Y`) braucht eine Geste — die ist hier
aber seit 2026-08-04 ebenfalls unsichtbar moeglich:
`headless-agent-install.py chromium capture` startet Chromium auf Xvfb und
sendet das Kommando per XTEST (erfuellt `activeTab`, gemessen: valide PDF
in 19,1 s). Nur Chromium: kein Firefox-Build mappt auf dieser WSL2/Xvfb ein
Fenster (offiziell 153 und Playwright 146, mit/ohne dbus, GPU- und
Sandbox-Flags gemessen) — Firefox-Captures bleiben der Windows-Route
vorbehalten.
**Chromium-Hinweis:** der CWS-Update-Dienst lieferte 2.17.0_0, die
CWS-Web-Seite zeigte 2.12.1, AMO 2.26.0 — bei Verifikation Quelle nennen.
**Firefox-153-Hinweis:** unter WSL2/Xvfb mappt das offizielle Firefox kein
Fenster (chroot-Inhaltssandbox) — die Xvfb-Variante braucht dort den
Playwright-Firefox-Build oder eine VM.

---

Stand 2026-08-03 (urspruengliche Messung), Rohdaten:
`docs/data/2026-08-03-agent-install-and-capture.json`.

Drei Varianten, absteigend nach Stoerfreiheit fuer den User:

| Variante | Stoert den User? | Voraussetzung | Gemessen |
|---|---|---|---|
| **A — Schnellablauf** (Fokus + SendInput) | ja, ~60-90 s Fenster im Vordergrund | nichts | ja, beide Browser gruen |
| **B — Sandkasten** (Windows Sandbox / 2. Session / VM) | nein | Sandbox-Feature oder 2. Benutzer | Konzept, hier nicht ausgefuehrt |
| **C — Policy** (install-store-version.py) | nein | Schreibrecht auf Policy-Ablage | hier ACL-gesperrt, sonst Standard |

**Nicht vorhanden: eine Variante, die im selben Desktop still laeuft.**
PostMessage-Eingaben (WM_KEYDOWN/WM_SYSKEYDOWN/WM_CHAR/WM_LBUTTONDOWN direkt
ans Fenster, auch an `Chrome_RenderWidgetHostHWND`) werden von Firefox wie
Chrome verworfen — Tastatur UND Maus, beides 2026-08-03 gemessen. Das ist
das Sicherheitsmodell (`activeTab`), kein Bug: nur der echte Eingabe-Stack
(SendInput/XTEST) zaehlt als Geste. Wer es still will, braucht Variante B
oder C — oder akzeptiert das 60-Sekunden-Fenster von Variante A.

---

## Helfer (PowerShell, ASCII only, Ablage z. B. %TEMP%\pl-agent-meas)

### shot.ps1 — Vollbild-Screenshot (beruehrt keinen Fokus)

```powershell
param([string]$Out)
Add-Type -AssemblyName System.Drawing,System.Windows.Forms
$b = [System.Windows.Forms.SystemInformation]::VirtualScreen
$bmp = New-Object System.Drawing.Bitmap $b.Width, $b.Height
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Left, $b.Top, 0, 0, $bmp.Size)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose(); $bmp.Dispose()
```

### winshot.ps1 — Fenster-Screenshot OHNE Fokuswechsel (PrintWindow)

Funktioniert auch fuer verdeckte Fenster. Damit lassen sich Zustaende
pruefen, ohne dem User etwas vor den Schirm zu schieben.

```powershell
param([string]$Match,[string]$Out)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class P {
 [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h,IntPtr dc,uint f);
 [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out R r);
 public struct R { public int Left,Top,Right,Bottom; }
}'
Add-Type -AssemblyName System.Drawing
$target=[IntPtr]::Zero
$liste = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($item in $liste) {
  $proc = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
  if ($proc -and $proc.MainWindowHandle -ne 0) { $target=$proc.MainWindowHandle }
}
if ($target -eq [IntPtr]::Zero) { Write-Output 'NOWINDOW'; exit 1 }
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
```

### click.ps1 — echter Mausklick (SendInput-Ebene)

```powershell
param([int]$X,[int]$Y)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class M { [DllImport("user32.dll")] public static extern bool SetCursorPos(int x,int y);
[DllImport("user32.dll")] public static extern void mouse_event(uint f,uint x,uint y,uint d,IntPtr e); }'
[M]::SetCursorPos($X,$Y) | Out-Null
Start-Sleep -Milliseconds 200
[M]::mouse_event(2,0,0,0,[IntPtr]::Zero)
Start-Sleep -Milliseconds 80
[M]::mouse_event(4,0,0,0,[IntPtr]::Zero)
Start-Sleep -Milliseconds 300
```

### key.ps1 — echte Taste (SendKeys/SendInput; `%+Y` = Alt+Shift+Y)

```powershell
param([string]$Keys)
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait($Keys)
Start-Sleep -Milliseconds 300
```

### focus.ps1 / focuskey.ps1 — Fokus erzwingen UND belegen

`SetForegroundWindow` aus einem Hintergrundprozess wird von Windows still
ignoriert (gemessen). Erst AttachThreadInput macht den Wechsel erzwingbar,
und erst GetForegroundWindow danach macht ihn belegt. focuskey.ps1 sendet
die Taste im selben Prozess — zwei getrennte Aufrufe lassen eine
Fokus-Race, in der ein fremdes Fenster die Tasten bekommt (gemessen:
getippter Text landete fast in einem fremden Terminal).

```powershell
param([string]$Match,[string]$Keys)   # focuskey.ps1; focus.ps1 = ohne Keys-Teil
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
$target=[IntPtr]::Zero
$liste = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($item in $liste) {
  $proc = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
  if ($proc -and $proc.MainWindowHandle -ne 0) { $target=$proc.MainWindowHandle }
}
if ($target -eq [IntPtr]::Zero) { Write-Output 'NOWINDOW'; exit 1 }
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
if ([W]::GetForegroundWindow() -ne $target) { Write-Output 'NOTFG'; exit 2 }
if ($Keys -ne "") {
  [System.Windows.Forms.SendKeys]::SendWait($Keys)
  Start-Sleep -Milliseconds 250
  if ([W]::GetForegroundWindow() -ne $target) { Write-Output 'LOSTFG'; exit 3 }
}
Write-Output 'SENT'
```

### closewin.ps1 — sauber schliessen (NIEMALS killen)

Ein hartes Beenden zwischen Install-Klick und sauberem Shutdown liess die
Firefox-Installation verschwinden (extensions.json zurueckgesetzt, gemessen).

```powershell
param([string]$Match)
Add-Type -TypeDefinition 'using System;using System.Runtime.InteropServices;
public class C { [DllImport("user32.dll")] public static extern bool PostMessage(IntPtr h, uint m, IntPtr w, IntPtr l); }'
$liste = Get-CimInstance Win32_Process -Filter "Name='firefox.exe' or Name='chrome.exe'" | Where-Object { $_.CommandLine -and $_.CommandLine.Contains($Match) }
foreach ($item in $liste) {
  $proc = Get-Process -Id $item.ProcessId -ErrorAction SilentlyContinue
  if ($proc -and $proc.MainWindowHandle -ne 0) { [C]::PostMessage($proc.MainWindowHandle, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null }
}
```

---

## Variante A — Schnellablauf Firefox (gemessen, ~90 s)

Fenster liegt nach focus.ps1 fest bei (0,0), Groesse 1400x900. Koordinaten
gelten fuer diesen Stand, Seite en-US, 2560x1440 bei 100 % Skalierung.
**Jede Koordinate vor Wiederverwendung per Screenshot gegenpruefen** —
Layout, Sprache und Fensterstand variieren.

| # | Aktion | Befehl / Koordinate | Verifikation |
|---|---|---|---|
| 1 | Starten | `firefox.exe -no-remote -profile <tmp>\ff-profile https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/` | PID bekannt |
| 2 | 12-15 s warten | — | winshot.ps1 ff-profile |
| 3 | ToU-Dialog: **Continue** | click.ps1 649 330 | winshot |
| 4 | **Add to Firefox** | click.ps1 1115 340 | winshot: Doorhanger |
| 5 | **Add** | click.ps1 1248 386 | — |
| 6 | **Install verifizieren (Datei!)** | extensions.json: `pageshot-pdf@bubu89.local`, active:true, Version = AMO-Stand | **das ist der Beweis, kein Screenshot noetig** |
| 7 | Adressleiste | click.ps1 550 65 | — |
| 8 | `example.com{ENTER}` | key.ps1 | winshot: Seite geladen |
| 9 | Doorhanger OK | click.ps1 1352 206 | — |
| 10 | **Capture** | focuskey.ps1 ff-profile `%+Y` | — |
| 11 | **PDF verifizieren (Datei!)** | neue `example_com_*.pdf` in der System-Download-Ablage, Kopf `%PDF-` | Beweis |
| 12 | Sauber schliessen | closewin.ps1 ff-profile, 10 s | extensions.json enthaelt Erweiterung weiterhin |

Schritt 8 ist der einzige Tipp-Schritt. Alternative ohne Tippen: Schritt 7/8
durch Neustart der Instanz mit Ziel-URL als Argument ersetzen — Klicks sind
positionsgebunden, Tasten gehen an das Fenster mit Fokus (gemessenes Risiko
auf geteiltem Desktop).

## Variante A — Schnellablauf Chrome (gemessen, ~90 s)

| # | Aktion | Befehl / Koordinate | Verifikation |
|---|---|---|---|
| 1 | Starten | `chrome.exe --user-data-dir=<tmp>\ch-profile --no-first-run --no-default-browser-check https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn` | PID |
| 2 | Consent: ans Ende scrollen | click.ps1 500 550, key.ps1 `{END}` | winshot |
| 3 | **Alle ablehnen** | click.ps1 595 675 | winshot: CWS-Seite |
| 4 | **Hinzufuegen** | click.ps1 980 241 | winshot: Dialog |
| 5 | **Erweiterung hinzufuegen** | click.ps1 702 325 | — |
| 6 | **Install verifizieren (Datei!)** | `ch-profile\Default\Extensions\ekjbgcdhpgijhbepkagefnkdbdfjpehn\<version>\manifest.json` | Beweis |
| 7 | Sauber schliessen + Neustart auf Zielseite | closewin.ps1, Start mit `https://example.com/` | — |
| 8 | **Capture** | focuskey.ps1 ch-profile `%+Y` | — |
| 9 | **PDF verifizieren (Datei!)** | wie Firefox (hier 22559 bytes) | Beweis |
| 10 | Sauber schliessen | closewin.ps1 ch-profile | Extensions-Verzeichnis bleibt |

Der Consent-Dialog (Schritt 2/3) ist regions- und sprachabhaengig; im
en-US-Raum faellt er meist kleiner oder ganz weg. Chrome akzeptiert als
zweites Kuerzel auch Strg+Shift+Y.

## Zeitbudget (gemessen)

Start bis Seite steht 12-15 s, Install-Dialog 4 s, Installation 5-8 s,
Capture bis PDF 10-15 s. Gesamt pro Browser rund 90 s, davon stoerend
(Fenster vorn) die gesamte Zeit — deshalb Variante A nur, wenn der User
kurz nicht am Geraet ist, oder Variante B/C.

## Variante B — Sandkasten (still, hier nicht ausgefuehrt)

Dieselbe Variante-A-Sequenz laeuft unveraendert in der **Windows Sandbox**
(Feature "WindowsSandbox" aktivierbar), in einer zweiten Windows-Session
(eigener lokaler Benutzer, RDP auf localhost) oder einer VM. Eigene
Session = eigener Eingabe-Stack = null Beruehrung mit dem User. Die
Profile sind wegwerfbar; die Store-Installation zaehlt trotzdem, solange
die Instanz periodisch laeuft (Update-Ping). Vor produktiver Nutzung
einmal mit derselben Datei-Verifikation durchmessen.

## Variante C — Policy (still, kein Klick)

`python3 install-store-version.py firefox|chrome [--check|--remove]`.
Schreibt ExtensionSettings (Firefox) bzw. ExtensionInstallForcelist
(Chrome) in die Policy-Ablage; Browser installiert beim naechsten Start
aus dem Store. Hier gemessen: HKCU\Software\Policies per ACL gesperrt —
dann Variante A oder B. Details und Linux-Pfade im Skript-Docstring und in
`.well-known/agent-skills/install-as-a-counted-user.md`.

## Fehlerbilder-Tabelle (alle heute aufgetreten)

| Symptom | Ursache | Reaktion |
|---|---|---|
| Installation nach Restart weg | Instanz hart beendet vor sauberem Shutdown | closewin.ps1 (WM_CLOSE), nie taskkill |
| Alt+Shift+Y wirkungslos, kein Fehler | Erweiterung gar nicht (mehr) installiert | erst extensions.json pruefen |
| Capture auf Store-Seite wirkungslos | AMO/CWS sind restricted domains | auf normaler Seite ausloesen |
| Keine PDF in C:\Users\...\Downloads | System-Ablage liegt woanders (hier D:\Downloads\Full Page PDF Snap\) | Ablage aus Systemeinstellung lesen |
| focus.ps1 meldet Erfolg, Tasten gehen ins Leere | SetForegroundWindow still ignoriert | AttachThreadInput-Variante + GetForegroundWindow-Beweis |
| Getippter Text landet fremd | Fokus-Race auf geteiltem Desktop | focuskey (ein Prozess), Klicks bevorzugen |
| NOWINDOW | Instanz wurde von dritter Seite geschlossen | neu starten, Messung wiederholen |
| PostMessage ohne Wirkung | Browser verwerfen synthetische Nachrichten | kein Bug — SendInput-Ebene oder Sandkasten |
| PowerShell: "kann nicht in Int32 konvertiert werden" | Schleifenvariable `$x` kollidiert mit `param([int]$X)` (case-insensitiv!) | Loop-Variablen nie wie Parameter nennen |
| PowerShell: Out-Printer-Fehler | `lp` ist Alias fuer Out-Printer | Funktionen nie wie Aliase nennen |
