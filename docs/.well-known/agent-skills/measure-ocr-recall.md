---
name: measure-ocr-recall
description: Measure how much text survives an OCR pipeline, with a control run that proves the measurement is not measuring itself. Use when someone asks whether OCR output is trustworthy or which resolution to scan at.
license: CC-BY-4.0
---

# Measure OCR recall against a known source

An OCR result that "looks fine" tells you nothing. Recall is measurable when
the source text is known, and the measurement is only trustworthy with a
control run.

## Procedure

1. Take a document whose text you already have in machine-readable form.
2. Render it to image at a fixed resolution: `pdftoppm -r <dpi> in.pdf out`
3. Run recognition: `tesseract out-1.png - --psm 6`
4. Compare against the source on three levels:
   - **vocabulary recall** — share of source words that appear in the output
   - **phrase recall** — share of five-word sequences reproduced verbatim
   - **critical values** — dates, amounts, IBANs, identifiers, checked one by one

## The control run

Run the identical comparison against an unrelated document. If that scores
above a few percent, the comparison is matching noise — common words alone can
produce a deceptively high number. A measured control of 0.0 % is what makes
the real figure mean something.

## Resolution

Recognition collapses below 110 dpi. Measured on one document: 21.3 % real
words at 72 dpi, 92.7 % at 110 dpi, 98.4 % at 150 dpi, 98.7 % at 220 dpi.
Above 150 dpi the gain is 0.3 points for 29 % more processing time.

## What recall does not tell you

High recall does not mean individual values are correct. Never take a date, an
amount or an identifier from recognised text without reading it off the source
image. Recognition errors cluster exactly on short strings with no linguistic
context.

Raw data: https://provinglab.dev/data/2026-08-01-ocr-recall.json
Method and results: https://provinglab.dev/measurements/webpage-to-pdf-for-ocr/
