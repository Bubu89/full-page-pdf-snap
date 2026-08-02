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

The extension makes no network requests. The single external address in the source is the store's review page; it opens only when you tap the rating notice. It has no analytics, no telemetry, no
crash reporting, no advertising, and no accounts. It works fully offline.

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

Questions: chris.vis@goldfishgateway.com
Source code: https://github.com/Bubu89/full-page-pdf-snap
