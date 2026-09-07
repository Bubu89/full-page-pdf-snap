# Privacy Policy

**Full Page PDF Snap – Save Webpage as PDF**
Last updated: 2026-08-17

## Summary

This extension collects nothing about you and transmits nothing about you.
Capturing, assembling and saving happen entirely on your device.

One exception, and it is deliberate: the **time anchor** fetches a public random
value from the drand network before saving. It sends nothing — no address, no
page content, no identifier — it only asks for a number that is the same for
everybody in that round. Since version 2.34.0 this is on by default, because a
capture whose date rests solely on the device clock is worth little as evidence.
See "Network activity" below.

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

The extension has no analytics, no telemetry, no crash reporting, no advertising
and no accounts. Nothing about you or about the pages you capture leaves your
device.

It makes exactly one request of its own:

- **The time anchor** (`drand`) — a public randomness beacon. Before a PDF is
  saved, the extension asks it for the current round's random value and places
  that value in the capture. This proves the file cannot have been produced
  before that round, without having to trust your device's clock. The request
  carries no address, no page content and no identifier; the answer is identical
  for every person asking in that round. **On by default since 2.34.0.** If the
  network is unreachable, the capture proceeds without the anchor.

Two further addresses can be opened, both only on your explicit action:

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
| `debugger` | **Optional, Chrome only, off until you ask for it.** Needed for the text-PDF path: it lets the browser typeset the page as a PDF itself, which is what produces selectable text, working links and much smaller files. It is requested the moment you switch that option on, and released again when you switch it off. It is used solely to issue the print command to the tab you are capturing — no debugging session is opened, nothing is read from other tabs, and nothing is sent anywhere. |

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
