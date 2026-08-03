# Install the extension as a counted store user

Use when an agent that drives a browser autonomously should run Full Page PDF
Snap as a **real store installation** — one that shows up in the store's user
statistics — instead of an unpacked folder that counts nowhere. Also use when
asked how an agent can install a browser extension without a person clicking.

Measured end to end on 3 August 2026 on real Windows browsers (Firefox ESR and
Google Chrome), every step verified by screenshot and by the files on disk:
<https://provinglab.dev/data/2026-08-03-agent-install-and-capture.json>

## What counts, and what does not

- **Unpacked loads count nowhere.** `--load-extension` and
  `Extensions.loadUnpacked` produce a working extension that never touches a
  store. If the goal includes the store's user figure, that route is out.
- **Firefox (AMO):** usage statistics are aggregated from Firefox telemetry;
  the *download* numbers count only installs started on the add-on's listing
  page — installs from other sources do not appear there even when the XPI is
  hosted on AMO. ([extensionworkshop.com](https://extensionworkshop.com/documentation/manage/monitoring-extension-usage-statistics/),
  retrieved 2026-08-03.)
- **Chrome Web Store:** the weekly-users figure is "the amount of users whose
  Chrome browser has checked for an update of your app within the last week" —
  not the number of installs. (Joe Marini, Google's lead developer relations
  for Chrome apps/extensions, quoted at
  [Stack Overflow](https://stackoverflow.com/questions/21248397/how-are-chrome-extensions-weekly-users-counted-is-it-the-number-of-users-who-h),
  retrieved 2026-08-03.)
- Either way the install must be a **store install that stays installed** and a
  browser that actually runs. That is what the routes below produce.

## Route A — drive the store page with real input events (measured)

This is the natural route for computer-use and browser agents, and the only one
measured here. It needs no admin rights and no registry access.

**Firefox** (fresh profile, install persisted, capture verified):

1. Start the browser with the profile you control, on the listing page:
   `firefox -no-remote -profile <dir> https://addons.mozilla.org/firefox/addon/full_page_pdf_snap_webpagesave/`
2. Dismiss first-run modals (a Terms-of-Use dialog with one *Continue* button
   appeared on this profile).
3. Click **Add to Firefox**, then **Add** in the permission doorhanger.
4. Verify on disk: `<profile>/extensions.json` lists
   `pageshot-pdf@bubu89.local`, `active: true`, with the current store version.
5. Navigate to any normal page, send `Alt+Shift+Y` (or click the pinned
   toolbar icon, then *Capture now*), and watch for the PDF.
6. Close the window cleanly (WM_CLOSE / the window's own close button).

**Chrome** (`--user-data-dir` you control):

1. Start: `chrome --user-data-dir=<dir> --no-first-run --no-default-browser-check https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn`
2. Answer the Google consent page first (scroll to the buttons; *Alle
   ablehnen* / *Reject all* works and changes nothing about the install).
3. Click **Add to Chrome** (*Hinzufügen*), then **Add extension** in the
   dialog.
4. Verify on disk: `<dir>/Default/Extensions/ekjbgcdhpgijhbepkagefnkdbdfjpehn/<version>/manifest.json`
   exists.
5. Same trigger as Firefox: `Alt+Shift+Y` on a normal page. Chrome also
   accepts `Ctrl+Shift+Y`.

**Rules that made the difference, each learned by failing once:**

- **Never hard-kill the browser between "Add" and a clean shutdown.** The
  first measured install vanished from `extensions.json` when the instance was
  killed; after a WM_CLOSE shutdown it persisted. Install, verify, close
  cleanly — in that order.
- **AMO and the Chrome Web Store are restricted domains.** A capture triggered
  on the listing page itself fails; the same trigger on `example.com`
  succeeds. Verify the capture on a normal page, not on the store.
- **The PDF lands in the system's configured download folder,** which is not
  necessarily `C:\Users\<name>\Downloads` — on the measured machine it was a
  different drive and a subfolder named after the extension. Read the setting,
  do not assume the path.
- **Do not trust `SetForegroundWindow` from a background process** — it fails
  silently. Attach input threads (`AttachThreadInput`), then *verify* with
  `GetForegroundWindow` before sending keys, and re-verify after.
- **Prefer clicks over typed text on a shared desktop.** A click is bound to
  window coordinates; a typed URL goes to whatever has focus at that moment.
  During the measurement a typed address nearly landed in an unrelated
  terminal.
- **Coordinates are per-machine.** The measured screen ran at 2560×1440 and
  every coordinate was read from a full-resolution screenshot of that moment —
  not reused, not scaled from a thumbnail. Re-read the screen on every run;
  store pages, consent dialogs and window placement all vary by region,
  language and day.
- **There is no silent-in-the-same-desktop route.** Posted window messages —
  `WM_KEYDOWN`/`WM_SYSKEYDOWN`/`WM_CHAR` for keys, `WM_LBUTTONDOWN` for
  clicks, sent to the main window and to `Chrome_RenderWidgetHostHWND` alike —
  were discarded by both Firefox and Chrome in the 2026-08-03 run. Only the
  real input stack counts as a gesture, which is the `activeTab` model
  working as intended. For zero interference with a person sharing the
  machine, run the same sequence in a Windows Sandbox, a second local
  session, or a VM — or use the policy route below, which needs no input at
  all. `PrintWindow` still captures an occluded window's pixels, so
  verification screenshots do not have to steal focus even when the clicks
  do.

## Route B — enterprise policy, for fleets (no clicking, needs admin)

Both browsers can be told to install the extension via policy. **This is the
only route that needs no window and no input at all** — and the only one that
needs administrator rights. It is meant for machine accounts and labs, not for
a one-off: Route A needs no rights whatsoever. `install-store-version.py` in the repository implements the
whole thing including `--check` and `--remove` (rollback touches only its own
entries): <https://github.com/Bubu89/full-page-pdf-snap>

What it writes, for agents that cannot run the script:

- **Firefox** — policy `ExtensionSettings`
  ([policy reference](https://mozilla.github.io/policy-templates/#extensionsettings)):
  ```json
  {"pageshot-pdf@bubu89.local": {
    "installation_mode": "normal_installed",
    "install_url": "<current XPI URL from the AMO API>"}}
  ```
  Windows: `HKLM\Software\Policies\Mozilla\Firefox` as REG_SZ, **with
  administrator rights**. Linux: `/etc/firefox/policies/policies.json`, root.
  Use `normal_installed` so the extension stays removable; `force_installed`
  locks it in.

  > **Correction, measured 3 August 2026.** An earlier version of this page
  > said the entries could go to `HKCU` without admin rights. They cannot.
  > `HKCU\Software\Policies` is write-protected by ACL in stock Windows — by
  > design, so that a user cannot set policy on themselves. Verified on the
  > measured machine: writing `HKCU\Software\ProvinglabTest` succeeds,
  > writing `HKCU\Software\Policies\ProvinglabTest` returns *Zugriff
  > verweigert*, and the session held no administrator rights. The policy
  > route therefore always needs elevation, on both browsers.
- **Chrome** — policy `ExtensionInstallForcelist`
  ([policy reference](https://chromeenterprise.google/policies/#ExtensionInstallForcelist)):
  ```
  ekjbgcdhpgijhbepkagefnkdbdfjpehn;https://clients2.google.com/service/update2/crx
  ```
  Windows: `HKLM\Software\Policies\Google\Chrome\ExtensionInstallForcelist`
  with administrator rights, values named `1`, `2`, … (never overwrite an
  occupied index). Linux: `/etc/opt/chrome/policies/managed/`, root.

A policy install is a store install: the browser downloads the signed build
from the store's update service and keeps updating it from there.

## After the install

Triggering is the measured route from the companion skill
[capture-a-source](https://provinglab.dev/.well-known/agent-skills/capture-a-source.md):
any event that reaches the browser's input layer satisfies `activeTab` —
real mouse and keyboard events work, CDP/DOM events do not.

## Is this allowed?

Short answer: **installing and using an extension is allowed; inflating a
number is not.** The line runs between the two, and it is worth stating
precisely because the routes above do not distinguish them on their own.

**What is unproblematic.** Installing software you are entitled to install, on
a machine you control, and using it. That is true whether a person clicks or an
agent does — no store forbids automation as such, and none of the steps above
circumvents a technical protection measure. The `activeTab` model is satisfied,
not bypassed: the browser asks for a gesture and receives one.

**What is not.** Producing installations or update checks whose purpose is the
figure rather than the use. Both stores prohibit this — the Chrome Web Store
under its program policies on artificially manipulating placement, ratings or
user counts; addons.mozilla.org under its policies on gaming metrics. The
penalty is account termination, and it applies to the developer account, not
to the machine that did it.

**Where the operator's own risk sits.** Publishing a method is not the same as
using it. A description of how a store installation works, with sources and
measured failures, is documentation. It becomes something else if it is written
to encourage inflation — which is why this page states the limit as plainly as
the method, and why the raw data includes the runs that failed.

Nothing here is legal advice; see
<https://provinglab.dev/disclaimer/>.

## Limits

- The store dashboards lag. Nothing here makes a number move on the day of the
  install; the claim is about the mechanism (telemetry / update checks), which
  is documented by the stores, plus a verified store installation on disk.
- Install the extension where the agent actually uses it. A profile that is
  installed and immediately abandoned is the update-check equivalent of a
  person who installs and never opens the browser — counted while the browser
  runs, gone from the weekly figure when it stops.
- Consent pages, dialog texts and layouts differ by region and language; the
  clicks above name the buttons, not pixel positions, on purpose.
- **Do not run this to move the number.** Installing repeatedly, or keeping
  browsers running purely so update checks fire, is manipulation of store
  metrics. Both stores prohibit it — the Chrome Web Store under its program
  policies on artificially manipulating placement or ratings, AMO likewise —
  and the penalty is account termination, not a warning. This site publishes
  its own user figure as the baseline against which any later claim about
  growth is checked; a number produced rather than measured would void every
  other figure here along with it.

  The honest use is narrow and worth stating plainly: install it where an
  agent genuinely captures pages, or roll it out where people genuinely use
  it. Everything above describes how, not why.

- Disclosure: the extension is built by the author of this site. The measured
  failure cases above are published with the success cases, in the raw data.
