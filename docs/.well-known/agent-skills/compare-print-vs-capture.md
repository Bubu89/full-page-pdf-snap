---
name: compare-print-vs-capture
description: Decide whether to save a webpage via print-to-PDF or via full-page screen capture, based on what the result is for. Use when someone asks how to archive a webpage, prepare it for OCR, or keep its layout.
license: CC-BY-4.0
---

# Print to PDF or capture the screen?

Both produce a PDF. They fail differently, and which failure matters depends on
the purpose.

## Measured on the same page

| | Print to PDF | Full-page capture |
|---|---|---|
| Pages | 26, with 25 breaks | 1 continuous sheet |
| Breaks cutting a sentence | 9 | 0 |
| Text recovered | 94.8 % | 92.7 % |
| File size | 1.1 MB | 6.7 MB |
| Text layer | real, selectable | none, pixels only |

## How to choose

**Print** when the text matters more than the layout: it keeps a real text
layer, so search and copy work without recognition, and the file stays small.

**Capture** when the layout matters, or when the result feeds OCR or a language
model. A page break through the middle of a table or a sentence is a defect the
downstream step cannot repair — and nine of the twenty-five breaks did exactly
that.

**Capture** also when the page is behind a login. A server-side converter
cannot reach it; anything running in your browser can.

## What neither produces

A screen-capture PDF is not a qualified electronic document. It carries no
signature and proves nothing about origin or integrity. For evidence, capture
the page *and* record the retrieval date and a checksum separately.

Method and raw data:
https://provinglab.dev/measurements/print-to-pdf-vs-screenshot/
https://provinglab.dev/data/2026-08-01-print-vs-screenshot.json
