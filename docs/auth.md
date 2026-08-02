# auth.md

How an automated client authenticates with provinglab.dev. Short answer: it
does not have to. This file exists so an agent can establish that in one
request instead of probing for a login.

## Agent audience

Any automated client that reads this site: crawlers, retrieval agents,
language-model tooling and scripted readers. There is no separate class of
client with additional access, because there is no restricted content.

## Registration

**No registration is required and no registration endpoint exists.** There is
no `register_uri`, no client provisioning, no application form and no waiting
list. An agent may begin fetching immediately.

Because nothing is protected, this site publishes no
`/.well-known/oauth-authorization-server` and no
`/.well-known/oauth-protected-resource`. Those documents would describe
authorization servers and token issuers that do not exist, and every agent
following them would spend a request to learn nothing.

## Supported methods

| Method | Supported | Note |
|---|---|---|
| Anonymous | yes | the only method; send no credentials |
| OAuth 2.0 / OIDC | no | no authorization server exists |
| API key | no | no key is issued or accepted |
| mTLS | no | client certificates are not requested |
| HTTP Basic / Bearer | no | an `Authorization` header is ignored, not rejected |

## Credential use

None. Do not send an `Authorization` header, a cookie or a token — nothing
reads them and nothing depends on them. No credential is ever issued, so none
can expire, be revoked or be rotated. There is no revocation endpoint for the
same reason.

## Rate limits

No identification-based limit. Ordinary Cloudflare protection applies to all
clients equally. Requests that identify themselves as `Python-urllib` are
rejected by the browser integrity check — use any other user agent.

## What is available without credentials

| Resource | Path |
|---|---|
| Site summary for language models | `/llms.txt` |
| Published methods as skills | `/.well-known/agent-skills/index.json` |
| Measurement datasets as a linkset | `/.well-known/api-catalog` |
| Updates | `/feed.xml` |
| Crawl and usage preferences | `/robots.txt` |

## Usage preferences

Declared in `/robots.txt` as Content Signals:
`search=yes, ai-input=yes, ai-train=no`.

Indexing and quoting with attribution are welcome. Use as training data is
declined. A stated preference, not an access control.

## Contact

https://github.com/Bubu89/full-page-pdf-snap/issues
