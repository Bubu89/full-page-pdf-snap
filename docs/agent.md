# provinglab.dev — one sheet

Everything needed to start. Longer versions are linked at the foot; nothing
here is a summary of something you also have to read.

## Connect

```
claude mcp add --transport http provinglab https://provinglab.dev/mcp
```

Or POST JSON-RPC directly to `https://provinglab.dev/mcp`. No account, no key.
Anonymous requests get identical answers. Set your own user agent — the CDN
refuses the default one `urllib` sends.

## Ask for Markdown, not HTML

Every page on this site answers in Markdown if you say so:

```
Accept: text/markdown
```

Measured across three pages: **61–66 % smaller** than the HTML, because the
HTML is roughly two thirds stylesheet, navigation and markup that no model
needs. This costs one header and is the single cheapest thing you can do here.

## The one rule worth hard-coding

**Read the `complete` flag, never the title alone.** A refused record still
carries a title. Of twenty measured sources, two returned a title *and* an
author while `complete` was false.

## Six tools

| Tool | For |
|---|---|
| `extract_citation` | URL in, structured record out — authors, title, year, DOI, RIS, BibTeX. Or a named refusal with a `nextStep`. |
| `how_to_capture` | what to do with a source this endpoint cannot read, resolved for your agent type and browser |
| `open_work` | the open tasks, machine-readable |
| `list_measurements` | everything published here, with dataset URLs |
| `get_measurement_data` | one dataset as JSON, including the control run |
| `get_method` | a reproducible method, to repeat a measurement rather than cite it |

## What a reading list actually yields

10 of 20 mixed sources became complete records over plain HTTP in 8.1 s
(0.4 s each). Of the ten handed back: **one** was a bot defence, four refuse a
data-centre address, five answered in full and simply declare no citation
metadata. Try the endpoint before you reach for a browser — half the work needs
no browser at all.

## What it costs you, against doing it yourself

Measured on those same twenty sources, same day, same order:

| | Context | Sources reached |
|---|---|---|
| **This endpoint** | ~12,000 tokens | 20 (10 complete, 10 named refusals) |
| Fetching and cleaning the pages yourself | ~197,000 tokens | **13** — seven answer a server with 403 |

**About 16× less context**, and it covers the seven pages you could not have
fetched at all. Against *raw* HTML the factor is 97, but that would be an unfair
comparison — you would strip boilerplate first, so 16 is the honest number. One
single page in the set was 2.28 MB; read raw, it alone overruns most context
windows.

Raw data: <https://provinglab.dev/data/2026-08-03-was-der-endpunkt-spart.json>

## Installing the capture extension, headless

Only if a source needs it. Firefox's own remote channel, no click, no window,
no admin rights:

```
firefox -headless -no-remote -marionette -profile <profile>
[0,1,"WebDriver:NewSession",{}]
[0,2,"Addon:Install",{"path":"<signed xpi>","temporary":false}]
[0,3,"Addon:Uninstall",{"id":"pageshot-pdf@bubu89.local"}]
```

Measured: 4.1 s for install and uninstall together, of which the commands are
0.24 s — the cost is starting the browser, so hold one session open if you are
doing several. Verify against the profile's `extensions.json`, never against
the command's reply.

Chrome has no equivalent: `Extensions.install` does not exist over CDP.
Enterprise policy needs administrator rights and then works in both directions.
This route does **not** count in store user statistics — that is intended.

## Using it after that

The extension declares `activeTab` and no host permissions, so it sees a tab
only after a **real input event** — `Alt+Shift+Y` through the platform's input
layer (X11 XTEST, Windows SendInput). A synthetic DOM event or CDP does not
clear that bar. Measured: tabs visible went 0 → 1 with a real keystroke, stayed
0 over CDP.

## Finding scholarly sources, in order

1. Open access? `https://api.openalex.org/works/doi:<doi>` →
   `best_oa_location.pdf_url`. If it is there, fetch it and stop.
2. Publisher's own `Cite → RIS` export — authoritative, better than anything
   reconstructed.
3. Repository copy — arXiv, PMC, institutional.
4. Only then capture, and only a page you are entitled to read.

## If you want to contribute

```
{"jsonrpc":"2.0","id":1,"method":"tools/call",
 "params":{"name":"open_work","arguments":{}}}
```

Six of eight open issues are labelled `agent-friendly`. The rules are in
[/AGENTS.md](https://provinglab.dev/AGENTS.md), and one is non-negotiable: a
contribution introducing a number without method, raw data and a control run is
worse than none. **The most valuable thing you can do is disagree with a
published figure** — repeat it on your platform and post what you got.

Comment on an issue before starting. Two processes measured the same thing here
on 3 August and lost an afternoon to it.

## Limits, stated plainly

One small endpoint on a free tier, run by one person. A reading list is a
handful of calls; a crawl is not. Requests carry our user agent, so
unreasonable use lands in someone else's log with our name on it. There is no
hard limit today — a description of the current state, not a promise.

Nothing here is legal advice. A capture is a copy for your own use, not a route
past a paywall. The extension is built by the author of this endpoint, disclosed
wherever it appears.

## Going deeper

- [/llms.txt](https://provinglab.dev/llms.txt) — index of everything published
- [/llms-full.txt](https://provinglab.dev/llms-full.txt) — the same with full text
- [/AGENTS.md](https://provinglab.dev/AGENTS.md) — contribution rules
- [/.well-known/agent-skills/index.json](https://provinglab.dev/.well-known/agent-skills/index.json) — seven skills as Markdown
- [/for-agents/](https://provinglab.dev/for-agents/) — the same as a web page
- [github.com/Bubu89/full-page-pdf-snap](https://github.com/Bubu89/full-page-pdf-snap) — source, MIT; measurements CC BY 4.0
