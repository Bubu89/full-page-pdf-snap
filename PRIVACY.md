# Privacy Policy

**Full Page PDF Snap – Save Webpage as PDF**
Last updated: 2026-07-31

## Summary

This extension collects nothing, transmits nothing, and contacts no server.
Everything happens on your device.

## What the extension does with page data

When you start a capture, the extension scrolls the active tab, takes screenshots
of it, and assembles them into a PDF. The image data exists only in your browser's
memory until the PDF is written to your download folder. It is never uploaded,
shared, or retained anywhere else.

The page title and the site's hostname are read for one purpose only: to build the
file name (`{title}`, `{site}` in the file name template). They are not stored
separately and not sent anywhere.

## What is stored on your device

Your settings and one counter are saved with the browser's local extension storage
(`storage.local`) — for example the target subfolder, image quality, file name
template, and interface language. This data stays on the device; it is not part of
Firefox Sync and never leaves the browser. Removing the extension deletes it.

No browsing history, no visited URLs, no page contents, no identifiers, and no
usage statistics are stored.

## Network activity

The extension makes no network requests of its own. It has no analytics, no telemetry, no
crash reporting, no advertising, and no accounts. It works fully offline.

Two addresses can be opened, both only on your explicit action:

- **The store's review page** — opens when you tap the rating notice.
- **The publisher's original file** — only if you switch on *"Also download the
  publisher's original file"*, which is **off by default**. It then downloads the
  full-text address the page you are capturing declares in its own metadata
  (`citation_pdf_url`). That is the same request your browser makes when you click
  "PDF" on that page, with the same access rights and to the same server you are
  already visiting. Nothing is sent to the author of this extension, and nothing
  behind a paywall becomes reachable.

Citation details — authors, journal, DOI, licence, access time — are read from the
page that is already loaded in your browser. **No citation service is contacted.**
This is deliberate: asking a service to resolve a DOI would tell that service which
paper you are reading.

## Permissions and why they are needed

| Permission | Purpose |
|---|---|
| `activeTab` | Read the current tab only while you run a capture |
| `downloads` | Save the finished PDF to your download folder |
| `downloads.open` | Open the PDF after saving, if you enable that option |
| `storage` | Keep your settings on this device |
| `menus` | Add the "Save page as PDF" context menu entry |
| `notifications` | Show capture progress and the "saved" message |

The manifest declares `data_collection_permissions: ["none"]`, which is Firefox's
built-in way of stating that no data is collected.

## Third parties

None. No data is shared with anyone, because none is collected.

## Contact

Questions: contact@provinglab.dev
Source code: https://github.com/Bubu89/full-page-pdf-snap

## Liability

See [Disclaimer and limitation of liability](https://provinglab.dev/disclaimer/) for the
scope of warranty and liability for this extension.
