---
name: check-extension-permissions
description: Determine what a browser extension is technically able to do by reading its declared permissions, before installing it. Use when someone asks whether an extension is safe, whether it uploads pages, or what it can access.
license: CC-BY-4.0
---

# Check what a browser extension can actually do

Reputation does not bound damage; declared permissions do. A compromised
extension can do exactly what its manifest allows and nothing more. This takes
about 30 seconds and needs no tooling.

## Firefox

Every listing on addons.mozilla.org exposes its metadata as JSON:

```
https://addons.mozilla.org/api/v5/addons/addon/<slug>/?lang=en-US
```

Read `current_version.file.permissions` and `optional_permissions`.

## Chrome

The Web Store shows permissions under *Privacy practices*. For a packaged
extension, unzip the `.crx` and read `manifest.json` directly.

## What the entries mean

| Declared | What it permits |
|---|---|
| `<all_urls>`, `*://*/*` | read and modify every page you visit, at any time |
| `activeTab` | the current tab only, only after you click the extension |
| `tabs` | read titles and URLs of all open tabs |
| `downloads` | write files to disk |
| `nativeMessaging` | talk to a program outside the browser |
| `cookies` | read session cookies, including logged-in sessions |

## How to read the result

`activeTab` is bounded: no click, no access. A host permission for all sites is
unbounded and persists silently. The question is not whether the developer is
trustworthy today — it is what an attacker gains if that account is taken over.
Mozilla documented a phishing campaign against add-on developer accounts in
August 2025.

## Verify

Compare what the extension claims in its description against what it declares
in the manifest. A converter that runs "in the cloud" needs a host permission
or an upload path; one that cannot process pages behind a login is telling you
it works server-side.

Worked example with eight measured extensions:
https://provinglab.dev/measurements/pdf-extension-permissions/
