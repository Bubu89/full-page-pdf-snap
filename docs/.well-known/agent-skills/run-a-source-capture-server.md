---
name: run-a-source-capture-server
description: Turn an address into a citable source with a local MCP server — fetch the file the publisher actually serves, read the citation metadata of the page describing it, write a RIS record, index the full text. For when sources must land in a collection an agent can search later, without any cloud account or credential.
---

# Running a source-capture server

A source is two things: the file, and the claim of where it came from. Tools
that fetch a PDF give you the first. This gives you both, and puts them
somewhere searchable.

## When to use it

- Sources have to accumulate in a collection an agent can query later
- Citation metadata must survive alongside the file, not in a separate app
- No cloud account is acceptable — for a shared machine, a student project,
  or anything that must not carry someone's credentials

## When NOT to use it

- **Licensed literature.** The server authenticates nowhere. A publisher
  paywall needs a browser session; that is a browser extension's job.
- **Broad site coverage.** Zotero maintains several hundred site translators.
  This handles the common metadata standards well and unusual sites not at all.
- **Circumventing access controls.** Where a provider blocks retrieval, it
  stops with a message.

## The three rules worth hard-coding

**1. The extension is a claim, not a fact.** An address ending in `.pdf` may
return HTML. Zenodo's preview URL does exactly that — the pdf.js viewer, 7 kB.
Check the first five bytes (`%PDF-`), never the extension and never a size
threshold. A guessed threshold of 5 kB let a 7 kB viewer page through.

**2. The publisher knows where the file is.** Where a page carries
`citation_pdf_url`, prefer it over any address found in an iframe. On Zenodo
the iframe points at `/preview/` and the citation tag at `/files/` — same
document, one of them real.

**3. Metadata increasingly lives in JSON-LD.** Zenodo publishes no
`citation_publication_date`; the year appears only in the schema.org block.
Reading `citation_*` alone degrades quietly: you get a file, correctly named
except for the year, which reads `oJ`.

## Connecting

```json
{ "mcpServers": {
    "quellen": { "command": "python3",
                 "args": ["/path/to/quellen-mcp/server.py"],
                 "env": { "QUELLEN_ORDNER": "/path/to/sources" } } } }
```

Five tools:

| tool | purpose |
|---|---|
| `quelle_pruefen` | does this address serve a PDF — without downloading it |
| `quelle_zitation` | citation metadata only, no file |
| `quelle_holen` | fetch, store with a RIS record, index the full text |
| `bestand_suchen` | full-text search across what has been captured |
| `bestand_stand` | size of the collection |

`pdftotext` and `pdfinfo` (poppler-utils) make the text searchable. Without
them a source is stored but not indexed — the reply says so with
`seiten_durchsuchbar: 0` rather than failing silently.

## Verifying it works

The reference run is published with its raw data:
https://provinglab.dev/measurements/mcp-source-capture/ — four addresses of
increasing difficulty, 23 of 23 checks, every file byte-identical to a
reference established beforehand with `curl`.

The fourth case is the one worth copying into your own tests: a page named
`PDF` that is not one. A tool that finds something everywhere finds nothing
reliably.
