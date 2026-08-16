#!/usr/bin/env python3
"""Teilt llms.txt in Index und Volltext — und erzeugt ein Blatt fuer den Erstkontakt.

    python3 build-llms-index.py
    python3 build-llms-index.py --check     # Exitcode 1, wenn nicht aktuell

Gemessen am 3. August 2026: Ein Agent, der sich hier einarbeitet, laedt
`/llms.txt` (5.339 Tok), `/for-agents/` (5.235), `/AGENTS.md` (1.973), den
Skill-Index (964), den Install-Skill (3.136) und die Sitemap (2.309) —
zusammen **rund 19.000 Token in sechs Abrufen**, bevor er handeln kann. Die
Latenz ist dabei nie das Problem (0,15–0,33 s je Abruf); der Kontext ist es.

Zwei Ursachen, beide behebbar:

1. **`llms.txt` war ein Volltext.** Der Vorschlag sieht sie als
   Inhaltsverzeichnis vor — kurze Zeilen mit Verweis — und den ausgeschriebenen
   Text in `llms-full.txt`. Hier standen 19 von 34 Eintraegen ueber 400 Zeichen,
   der laengste 1.428. Wer nur wissen will, was es gibt, zahlt den ganzen Text.

2. **HTML ist fuer einen Agenten zu 64 % Ballast.** `/for-agents/` misst
   20.894 B, davon 7.454 B Text. Der Rest ist Stil, Navigation und Markup, das
   kein Modell braucht.

Erzeugt werden deshalb:

  llms.txt        Index — je Eintrag der erste Satz, sonst nichts
  llms-full.txt   der bisherige Inhalt, unveraendert
  agent.md        ein Blatt fuer den Erstkontakt: verbinden, die eine Regel,
                  die Werkzeuge, die Installation, wo die Arbeit liegt

`agent.md` ersetzt die ersten vier Abrufe durch einen. Wer mehr braucht, findet
am Fuss die Verweise — der Index kommt vor der Tiefe, nicht statt ihrer.
"""
import argparse
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
QUELLE = DOCS / "llms.txt"


def erster_satz(text):
    """Bis zum ersten Satzende, aber nie mitten in einer Abkuerzung.

    Ein naives `.split(".")` zerschneidet „0.4 s", „10.1371/journal" und
    „provinglab.dev" — und liefert dann Bruchstuecke, die schlechter sind als
    gar keine Kuerzung.
    """
    t = text.strip()
    for m in re.finditer(r"[.!?](?=\s)", t):
        i = m.start()
        vor, nach = t[max(0, i - 12):i], t[i + 1:i + 3]
        if re.search(r"\d$", vor) and re.match(r"\s*\d", nach):
            continue                      # Dezimalzahl
        if re.search(r"\b[A-Za-z]$", vor) and len(vor.split()[-1]) <= 2:
            continue                      # Abkuerzung wie „z. B."
        return t[:i + 1]
    return t


GRENZE = 220


def index_zeile(zeile):
    """`- [Titel](URL): Text` → `- [Titel](URL): erster Satz, hoechstens GRENZE`

    Der erste Satz allein reicht nicht: ein Eintrag hatte keinen Punkt in den
    ersten tausend Zeichen und blieb ungekuerzt stehen. Ein Index, dessen
    Zeilenlaenge davon abhaengt, wie jemand interpunktiert, ist kein Index.
    Deshalb zusaetzlich eine harte Grenze, am Wort geschnitten — was danach
    kommt, steht vollstaendig in llms-full.txt.
    """
    m = re.match(r"^(- \[[^\]]+\]\([^)]+\)):\s*(.+)$", zeile, re.S)
    if not m:
        return zeile
    kurz = erster_satz(m.group(2))
    if len(kurz) > GRENZE:
        kurz = kurz[:GRENZE].rsplit(" ", 1)[0].rstrip(",;:—-") + " …"
    return f"{m.group(1)}: {kurz}"


def index_bauen(voll):
    aus, in_block = [], False
    for zeile in voll.split("\n"):
        if zeile.startswith("- ["):
            aus.append(index_zeile(zeile))
            in_block = True
            continue
        in_block = False
        aus.append(zeile)
    kopf = ("\n> This file is an index. The same entries with their full text are in\n"
            "> [llms-full.txt](https://provinglab.dev/llms-full.txt); a single sheet\n"
            "> that gets an agent from nothing to working is\n"
            "> [agent.md](https://provinglab.dev/agent.md).\n")
    # Nach dem einleitenden Zitatblock einsetzen, nicht davor: der erste Absatz
    # sagt, worum es geht, und das gehoert vor jeden Hinweis auf andere Dateien.
    text = "\n".join(aus)
    i = text.find("\n\n", text.find("> "))
    return text[:i] + "\n" + kopf + text[i:] if i > 0 else kopf + text


AGENT_MD = """# provinglab.dev — one sheet

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

## Ten tools

| Tool | For |
|---|---|
| `extract_citation` | URL in, structured record out — authors, title, year, DOI, RIS, BibTeX. Or a named refusal with a `nextStep`. |
| `extract_citations` | a whole reading list in one call — one record or one named refusal per source |
| `how_to_capture` | what to do with a source this endpoint cannot read, resolved for your agent type and browser |
| `list_measurements` | everything published here, with dataset URLs |
| `get_measurement_data` | one dataset as JSON, including the control run |
| `get_method` | a reproducible method, to repeat a measurement rather than cite it |
| `recommend_settings` | the capture settings that fit your purpose, each with the measurement behind it |
| `install_extension` | install or uninstall the capture extension without a window or a click |
| `adoption_stats` | how much this endpoint and its install route are actually used, with the figures behind it |
| `open_work` | the open tasks, machine-readable |

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
"""


def schreiben(ziel, inhalt, pruefen):
    alt = ziel.read_text(encoding="utf-8") if ziel.exists() else None
    if alt == inhalt:
        print(f"  {ziel.name:<20} {len(inhalt):>6} B  aktuell")
        return False
    if pruefen:
        print(f"  {ziel.name:<20} {len(inhalt):>6} B  ABWEICHUNG")
        return True
    ziel.write_text(inhalt, encoding="utf-8")
    print(f"  {ziel.name:<20} {len(inhalt):>6} B  geschrieben")
    return False


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()

    voll = QUELLE.read_text(encoding="utf-8")
    # Der Volltext ist die bisherige Datei — aber nur, solange sie noch der
    # Volltext IST. Nach dem ersten Lauf ist llms.txt der Index, und dann darf
    # llms-full.txt nicht daraus ueberschrieben werden.
    ziel_voll = DOCS / "llms-full.txt"
    ist_schon_index = "> This file is an index." in voll
    if ist_schon_index and ziel_voll.exists():
        voll = ziel_voll.read_text(encoding="utf-8")

    abweichung = False
    abweichung |= schreiben(ziel_voll, voll, a.check)
    abweichung |= schreiben(QUELLE, index_bauen(voll), a.check)
    abweichung |= schreiben(DOCS / "agent.md", AGENT_MD, a.check)

    if a.check and abweichung:
        print("\n  Nicht aktuell — `python3 build-llms-index.py` ausfuehren.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
