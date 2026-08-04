# auth.md

How an automated client authenticates with provinglab.dev.

**Short answer: it does not have to.** Every resource here is public. A full
OAuth flow is offered anyway, because some clients refuse to connect without
one — but a token grants no access that anonymous requests do not already have.

## Agent audience

Any automated client that reads this site: crawlers, retrieval agents, MCP
clients and scripted readers. There is no class of client with additional
access, because there is no restricted content.

## Registration

Not required. If your client needs it, register at
`POST /oauth/register` (RFC 7591). Any request is accepted; you receive a
stable `client_id`. No secret is issued and none is needed.

```
curl -X POST https://provinglab.dev/oauth/register   -H 'content-type: application/json'   -d '{"client_name":"my-agent"}'
```

## Supported methods

| Method | Supported | Note |
|---|---|---|
| Anonymous | yes | the normal case; send nothing |
| OAuth 2.0 client credentials | yes | `POST /oauth/token`, returns a bearer token valid one hour |
| Dynamic client registration | yes | `POST /oauth/register`, RFC 7591 |
| Authorization code | advertised, refused | there is nothing to authorize; use client credentials |
| API key | no | none is issued or accepted |
| mTLS | no | client certificates are not requested |

```
curl -X POST https://provinglab.dev/oauth/token   -d 'grant_type=client_credentials&client_id=pl_...'
```

## Credential use

A bearer token may be sent on `/mcp`. It is read and accepted, and it changes
nothing: the endpoint answers identically with and without it. Tokens expire
after one hour and are not revocable, because there is nothing to revoke —
losing one costs you nothing and gains an attacker nothing.

Metadata: `/.well-known/oauth-authorization-server` and
`/.well-known/oauth-protected-resource` (RFC 9728), the latter carrying
`authentication_required: false`.

## Rate limits

No identification-based limit. Ordinary Cloudflare protection applies to every
client equally, and no user agent is treated differently.

Until 4 August 2026 the browser integrity check rejected requests identifying
as `Python-urllib` — 24 of them in the preceding 24 hours, all on `/mcp`, all
from clients doing nothing wrong. It is off: a default library user agent now
receives the same answer as any other.

## What is available without any of this

| Resource | Path |
|---|---|
| MCP endpoint (JSON-RPC over POST) | `/mcp` |
| Everything an agent needs, one fetch (~1,200 tokens) | `/agent.md` |
| Index of everything published | `/llms.txt` |
| The same index with full text | `/llms-full.txt` |
| Published methods as skills | `/.well-known/agent-skills/index.json` |
| Measurement datasets as a linkset | `/.well-known/api-catalog` |
| Markdown of any page | any URL with `Accept: text/markdown` |
| Updates | `/feed.xml` |
| Crawl and usage preferences | `/robots.txt` |

## Usage preferences

Declared in `/robots.txt` as Content Signals:
`search=yes, ai-input=yes, ai-train=no`.

Indexing and quoting with attribution are welcome. Use as training data is
declined. A stated preference, not an access control.

## Contact

https://github.com/Bubu89/full-page-pdf-snap/issues
