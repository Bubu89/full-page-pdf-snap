---
name: cite-a-web-source
description: Turn a web page into a citation record with RIS and BibTeX, decide which sources a server can read and which need a browser, and know when a returned record must not be used. Use when someone asks to cite links, build a bibliography from URLs, or archive a source for a thesis.
license: CC-BY-4.0
---

# Cite a web source

A source becomes citable when four things are known: who wrote it, what it is
called, where it appeared, and **when it was retrieved**. The first three the
page usually declares about itself. The fourth only exists at the moment you
look, which is why it has to be recorded rather than reconstructed later.

## Two routes, and the rule for choosing

| | Endpoint | Browser extension |
|---|---|---|
| Reads as | an anonymous visitor | you, already logged in |
| Returns | the reference | the reference and the document |
| Behind a login | no | yes |
| Cost per source | none, scriptable | one click |

**Run the endpoint first over the whole list.** What it refuses is the list of
sources that need a browser. Do not decide this in advance — a paywall is not
predictable from the domain.

## Procedure

1. Collect the source URLs, one per line.
2. For each, call `extract_citation` on `https://provinglab.dev/mcp`
   (JSON-RPC 2.0 over HTTP POST, no account, no key):

   ```
   {"jsonrpc":"2.0","id":1,"method":"tools/call",
    "params":{"name":"extract_citation","arguments":{"url":"<URL>"}}}
   ```

3. **Check `complete` before using anything.** A refused record still carries a
   `title`, and it will be something like *"Checking your browser"*. Where
   `complete` is false, `warning` names the wall that stopped the read.
4. Concatenate the `ris` field of the complete records into one file and import
   it: Zotero → File → Import, or Citavi → Import → RIS.
5. For the refused ones, open the page in a browser and capture it with an
   extension that writes the same fields into the PDF and saves an RIS record
   beside it. That is the only route to a source behind a licence.

## Where the data actually comes from

Measured across 18 scholarly platforms: **resolving the DOI beats visiting the
article page.** The same work that a publisher's own page served without page
numbers came back complete through `https://doi.org/…` — authors, year, journal,
volume, pages, ISSN. If a DOI is known, use it as the URL.

## Pitfalls

- **A generic user agent gets blocked.** A request identifying as
  `Python-urllib` is answered with HTTP 403 by the CDN before the server sees
  it. Send a user agent of your own.
- **Do not treat coverage as accuracy.** A record can be complete and wrong.
  Measured against Wikimedia's Citoid on random samples: equal coverage, but the
  competing service returned a wrong field in about a fifth of cases. Spot-check
  the ones a claim depends on.
- **Handles are not authors.** A page's Twitter account in a meta tag will look
  like a person's name to a naive reader.
- **The retrieval time is your device's clock.** It is evidence of when you
  looked, not proof of what the page said.

## What this does not establish

That the work exists, that the DOI resolves to it, or that the page is honest
about itself. A citation record reports a declaration. Where the content decides
something, read the source.

Recipes with runnable code: https://provinglab.dev/recipes/
Method and measurements: https://provinglab.dev/measurements/citation-by-platform/
