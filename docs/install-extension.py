#!/usr/bin/env python3
"""Install or remove Full Page PDF Snap in a browser profile you control —
no window, no click, no administrator rights, no dependencies beyond the
Python standard library.

    python3 install-extension.py firefox install
    python3 install-extension.py firefox uninstall
    python3 install-extension.py chrome install --browser-path /path/to/chrome
    python3 install-extension.py both verify --json

Measured on 31 August 2026: Firefox install 2.9 s, uninstall 2.1 s,
Chrome install 4.1 s, uninstall 2.1 s — whole process, including starting
and stopping the browser.

Every step verifies itself against the profile on disk, not against what the
browser answered. Four traps below are the reason: each one made a failed run
report success, or a successful run report failure.

Full method, raw data and the reproduction command:
https://provinglab.dev/measurements/install-an-extension-without-a-click/

The extension is MPL-2.0; this script is CC-BY-4.0. Installing on a machine
that is not yours is a decision this script cannot make for you.
"""
import argparse
import json
import os
import shutil
import signal
import socket
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

GECKO_ID = "pageshot-pdf@bubu89.local"
CWS_ID = "ekjbgcdhpgijhbepkagefnkdbdfjpehn"
CWS_UPDATE = "https://clients2.google.com/service/update2/crx"
AMO_API = ("https://addons.mozilla.org/api/v5/addons/addon/"
           "full_page_pdf_snap_webpagesave/")
WORK = Path(os.environ.get("PLSNAP_WORK", Path.home() / ".cache/pdfsnap-install"))

PROTOKOLL = []


def log(action, **details):
    entry = dict(action=action, **details)
    PROTOKOLL.append(entry)
    if not ARGS.json:
        print("  " + action + " " + json.dumps(details, ensure_ascii=False),
              file=sys.stderr)


# --- finding the browser -----------------------------------------------------

FIREFOX_CANDIDATES = [
    "firefox", "firefox-esr", "/usr/bin/firefox", "/usr/lib/firefox/firefox",
    "/Applications/Firefox.app/Contents/MacOS/firefox",
    r"C:\Program Files\Mozilla Firefox\firefox.exe",
    r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe",
]
CHROME_CANDIDATES = [
    "google-chrome", "google-chrome-stable", "chromium", "chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]


def find_browser(kind):
    if ARGS.browser_path:
        p = Path(ARGS.browser_path)
        if not p.exists():
            raise SystemExit(f"--browser-path does not exist: {p}")
        return p
    for c in (FIREFOX_CANDIDATES if kind == "firefox" else CHROME_CANDIDATES):
        found = shutil.which(c) if not os.path.sep in c else (c if Path(c).exists() else None)
        if found:
            return Path(found)
    raise SystemExit(
        f"No {kind} found. Pass --browser-path. A browser you unpacked into "
        f"your own home directory is the case this script is built for: the "
        f"line that matters is not root versus user, it is whose browser it is."
    )


def profile_dir(kind):
    if ARGS.profile:
        return Path(ARGS.profile)
    return WORK / f"{kind}-profile"


# --- the store build ---------------------------------------------------------

def amo_current():
    """AMO and the Chrome Web Store carry their own version numbers and drift
    apart (2.37.0 against 2.38.0 on 31 August 2026). Only compare Firefox
    against this figure."""
    req = urllib.request.Request(AMO_API, headers={"User-Agent": "provinglab-install/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    cv = d["current_version"]
    return cv["file"]["url"].split("?")[0], cv["version"]


def fetch_xpi(url, version):
    """TRAP 3: a cache file without the version in its name is never renewed.
    A run reported the store version it had just looked up and installed a
    build four weeks older — the numbers still looked like numbers."""
    WORK.mkdir(parents=True, exist_ok=True)
    target = WORK / f"pdfsnap-{version}.xpi"
    if not target.exists():
        urllib.request.urlretrieve(url, target)
    # An unsigned or truncated file is rejected as "corrupt", which sends you
    # looking in the wrong place. Check it here instead.
    with zipfile.ZipFile(target) as z:
        got = json.loads(z.read("manifest.json"))["version"]
    if got != version:
        target.unlink()
        raise SystemExit(f"XPI says {got}, store says {version} — refusing.")
    return target


# --- Firefox: Marionette -----------------------------------------------------

class Marionette:
    """Firefox's own remote-control channel: length-prefixed JSON on TCP 2828.
    No driver, no package. Every command answers with success OR an error —
    which is exactly what the click route did not do."""

    def __init__(self, port=2828, timeout=60):
        end = time.time() + timeout
        while True:
            try:
                self.sock = socket.create_connection(("127.0.0.1", port), timeout=10)
                break
            except OSError:
                if time.time() > end:
                    raise SystemExit(
                        "Marionette never came up. The usual cause is a running "
                        "Firefox that took over the launch — -no-remote is not "
                        "optional."
                    )
                time.sleep(1)
        self._read()          # the server greets first
        self.counter = 0

    def _read(self):
        data = b""
        while True:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("marionette: connection closed")
            data += chunk
            if b":" in data:
                length_s, rest = data.split(b":", 1)
                length = int(length_s)
                if len(rest) >= length:
                    return json.loads(rest[:length].decode())

    def call(self, name, params):
        self.counter += 1
        payload = json.dumps([0, self.counter, name, params])
        self.sock.sendall(f"{len(payload)}:{payload}".encode())
        answer = self._read()
        if len(answer) > 2 and answer[2]:
            raise RuntimeError(f"{name}: {answer[2]}")
        return answer


def ff_policies_path(exe):
    return exe.parent / "distribution" / "policies.json"


def ff_clear_block(exe):
    """TRAP 1: a `blocked` entry left behind by an earlier uninstall stops
    every later install — silently. Marionette still answers Addon:Install
    with the add-on ID, as though it had worked. Measured 31 August 2026:
    six runs in a row reported success and installed nothing."""
    path = ff_policies_path(exe)
    if not path.exists():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8") or "{}")
    except json.JSONDecodeError:
        return False
    entry = data.get("policies", {}).get("ExtensionSettings", {}).get(GECKO_ID)
    if not entry or entry.get("installation_mode") != "blocked":
        return False
    data["policies"]["ExtensionSettings"].pop(GECKO_ID, None)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    log("policy-block-cleared", id=GECKO_ID)
    return True


def ff_installed_version(profile):
    """The truth lives in the profile, not in the browser's answer. This file
    is written when Firefox shuts down — see trap 2."""
    f = profile / "extensions.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8", errors="replace"))
    except json.JSONDecodeError:
        return None
    for a in data.get("addons", []):
        if a.get("id") == GECKO_ID and a.get("active"):
            return a.get("version")
    return None


def ff_action(action, exe, profile, xpi=None):
    profile.mkdir(parents=True, exist_ok=True)
    userjs = profile / "user.js"
    pref = 'user_pref("marionette.enabled", true);\n'
    existing = userjs.read_text(encoding="utf-8") if userjs.exists() else ""
    if "marionette.enabled" not in existing:
        userjs.write_text(existing + pref, encoding="utf-8")

    env = dict(os.environ, MOZ_HEADLESS="1", MOZ_MARIONETTE="1")
    proc = subprocess.Popen(
        [str(exe), "-no-remote", "-marionette", "-profile", str(profile), "about:blank"],
        env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    log("browser-started", pid=proc.pid, headless=True)
    clean = False
    try:
        m = Marionette()
        m.call("WebDriver:NewSession", {})
        if action == "install":
            m.call("Addon:Install", {"path": str(xpi), "temporary": False})
        else:
            try:
                m.call("Addon:Uninstall", {"id": GECKO_ID})
            except RuntimeError as e:
                if "not installed" not in str(e):
                    raise
                log("already-absent", id=GECKO_ID)
        # TRAP 2: end the session with Marionette:Quit, not with a signal.
        # A SIGTERM leaves the uninstall pending until the next start:
        # extensions.json still carried the extension, the run reported
        # failure, and only a later launch made the removal visible.
        # A hard kill between install and shutdown discards the install
        # outright.
        m.call("Marionette:Quit", {})
        clean = True
    finally:
        if clean:
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                stop(proc)
        else:
            stop(proc)
        log("browser-stopped", pid=proc.pid, clean=clean)


def stop(proc):
    try:
        os.killpg(proc.pid, signal.SIGTERM)
        proc.wait(timeout=20)
    except Exception:
        pass


# --- Chrome: external extension marker ---------------------------------------

def ch_marker_path(exe):
    return exe.parent / "extensions" / f"{CWS_ID}.json"


def ch_installed_version(profile):
    base = profile / "Default" / "Extensions" / CWS_ID
    if not base.exists():
        return None
    for d in sorted(base.iterdir(), reverse=True):
        if (d / "manifest.json").exists():
            return d.name
    return None


def ch_action(action, exe, profile):
    """Chrome has no install command over CDP — Extensions.install does not
    exist (-32601) and --load-extension takes unpacked folders only. What does
    work is a 75-byte marker beside the binary: Chrome fetches the signed
    build from the store itself, checks the signature, unpacks it."""
    marker = ch_marker_path(exe)
    if action == "install":
        marker.parent.mkdir(parents=True, exist_ok=True)
        marker.write_text(json.dumps({"external_update_url": CWS_UPDATE}), encoding="utf-8")
    elif marker.exists():
        marker.unlink()
    log("chrome-marker", present=(action == "install"), path=str(marker))

    profile.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [str(exe), "--headless=new", f"--user-data-dir={profile}",
         "--no-first-run", "--no-default-browser-check", "about:blank"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    log("browser-started", pid=proc.pid, headless=True)
    want = (lambda: ch_installed_version(profile)) if action == "install" \
        else (lambda: ch_installed_version(profile) is None)
    poll(want, 90)
    stop(proc)
    log("browser-stopped", pid=proc.pid, clean=True)


# --- verification ------------------------------------------------------------

def poll(fn, seconds, interval=1):
    end = time.time() + seconds
    while time.time() < end:
        v = fn()
        if v:
            return v
        time.sleep(interval)
    return None


def verify(kind, exe=None, profile=None):
    if kind == "firefox":
        return ff_installed_version(profile or profile_dir("firefox"))
    return ch_installed_version(profile or profile_dir("chrome"))


# --- phases ------------------------------------------------------------------

def install(kind):
    exe, profile = find_browser(kind), profile_dir(kind)
    url, store_version = amo_current()
    log("store-version", amo=store_version)
    if kind == "firefox":
        ff_clear_block(exe)
        ff_action("install", exe, profile, fetch_xpi(url, store_version))
    else:
        ch_action("install", exe, profile)
    # TRAP 4: read the profile only after the browser has gone. Checking one
    # moment too early is how a working run reports failure.
    got = poll(lambda: verify(kind, exe, profile), 20)
    expected = store_version if kind == "firefox" else None
    log("install-verified", browser=kind, version=got, ok=bool(got),
        expected=expected, current=(got == expected) if expected else None)
    return bool(got)


def uninstall(kind):
    exe, profile = find_browser(kind), profile_dir(kind)
    if kind == "firefox":
        ff_action("uninstall", exe, profile)
    else:
        ch_action("uninstall", exe, profile)
    gone = poll(lambda: verify(kind, exe, profile) is None, 20)
    log("uninstall-verified", browser=kind, ok=bool(gone))
    return bool(gone)


def main():
    global ARGS
    ap = argparse.ArgumentParser(
        description="Install or remove Full Page PDF Snap without a window or a click.")
    ap.add_argument("browser", choices=["firefox", "chrome", "chromium", "both"])
    ap.add_argument("phase", choices=["install", "uninstall", "verify"])
    ap.add_argument("--browser-path", help="path to the browser binary")
    ap.add_argument("--profile", help="profile directory to use")
    ap.add_argument("--json", action="store_true", help="machine-readable result on stdout")
    ARGS = ap.parse_args()

    kinds = ["firefox", "chrome"] if ARGS.browser == "both" else \
            ["chrome" if ARGS.browser == "chromium" else ARGS.browser]
    result, ok = {}, True
    started = time.time()
    for kind in kinds:
        try:
            if ARGS.phase == "install":
                good = install(kind)
            elif ARGS.phase == "uninstall":
                good = uninstall(kind)
            else:
                v = verify(kind)
                log("verify", browser=kind, version=v)
                good, result[kind] = True, v
                continue
            result[kind] = verify(kind)
            ok = ok and good
        except SystemExit as e:
            log("skipped", browser=kind, reason=str(e)[:200])
            result[kind], ok = None, False

    if ARGS.json:
        print(json.dumps({"phase": ARGS.phase, "ok": ok, "installed": result,
                          "seconds": round(time.time() - started, 1),
                          "log": PROTOKOLL}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


ARGS = argparse.Namespace(json=False, browser_path=None, profile=None)

if __name__ == "__main__":
    sys.exit(main())
