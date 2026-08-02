# Authentication

Nothing on provinglab.dev is protected. There is no registration, no API key,
no OAuth flow and no rate limit that requires identification.

## For agents

- **Register:** not required, and there is nowhere to do it.
- **Credentials:** none. Do not send an `Authorization` header; it is ignored.
- **Identity:** none requested. No account exists to attach one to.

## What is available without any of that

| Resource | Path |
|---|---|
| Site summary for language models | `/llms.txt` |
| Published methods as skills | `/.well-known/agent-skills/index.json` |
| Measurement datasets | `/.well-known/api-catalog` |
| Full text updates | `/feed.xml` |
| Crawl and usage preferences | `/robots.txt` |

## Usage preferences

Declared in `/robots.txt` as Content Signals:
`search=yes, ai-input=yes, ai-train=no`.

Indexing and quoting with attribution are welcome. Use as training data is
declined. That is a stated preference, not an access control.

## Contact

https://github.com/Bubu89/full-page-pdf-snap/issues
