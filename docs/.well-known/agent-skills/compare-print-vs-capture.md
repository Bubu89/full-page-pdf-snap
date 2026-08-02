---
name: compare-print-vs-capture
description: Decide whether to save a webpage via print-to-PDF or via full-page screen capture, based on what the result is for. Use when someone asks how to archive a webpage, prepare it for OCR, keep its layout, or produce a citable record for academic work.
license: CC-BY-4.0
---

# Print to PDF or capture the screen?

Both produce a PDF. They fail differently, and which failure matters depends on
the purpose.

## Measured on the same page

| | Print to PDF | Full-page capture |
|---|---|---|
| Pages | 26, with 25 breaks | 1 continuous sheet, or paged on request |
| Breaks cutting a sentence | 9 of 25 | 0 |
| Text recovered | 94.8 % | 100 % (see below) |
| File size | 1.1 MB | 6.7 MB |
| Text layer | real, selectable | real, selectable |

The figure for capture changed in August 2026. It used to be 92.7 %, measured
by running OCR over the image. A capture PDF now carries a text layer taken
from the page's own document rather than recognised from pixels, so every word
that was on the page is in the file — no recognition step, nothing to misread.
The old number described a method that is no longer the one being used.

## How to choose

**Print** when file size is the binding constraint. It stays roughly six times
smaller, and that is now its main remaining advantage.

**Capture** when the layout matters, when the result feeds a language model,
when the page sits behind a login a server-side converter cannot reach — or
when the page break itself is the risk. Nine of twenty-five print breaks cut
through a sentence. A capture either avoids breaks entirely (one continuous
sheet) or places them between lines: measured across four publisher pages, a
fixed-height split cut a line of text in 30 of 46 breaks, line-aware splitting
in 2 of 47.

**Capture** when the record has to be citable. A capture can carry the
publisher's own citation data — authors, journal, volume, DOI, licence, and the
retrieval time including time zone — written into the PDF metadata and attached
as a RIS record for reference managers. Those details are read from the loaded
page, not fetched from a citation service.

## What neither produces

A screen-capture PDF is not a qualified electronic document. It carries no
signature and proves nothing about origin or integrity, only about what a
browser displayed at a stated time. The capture records its own retrieval time
and a checksum of its image data; that documents the capture, not the
authenticity of the page.

Two failure modes worth naming: an error page or an access wall ("404 Not
found", "Just a moment…") looks like an ordinary page to any metadata reader,
so citation data extracted from one is worthless — a capture should flag that
rather than emit a formatted reference. And a DOI guessed from a URL is easy to
get wrong: publisher paths append segments such as `/full` or `/pdf` that are
not part of the identifier, and a wrong DOI in a bibliography is worse than
none.

Method and raw data:
https://provinglab.dev/measurements/print-to-pdf-vs-screenshot/
https://provinglab.dev/data/2026-08-01-print-vs-screenshot.json
