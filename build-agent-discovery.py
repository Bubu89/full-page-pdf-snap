#!/usr/bin/env python3
"""build-agent-discovery.py — erzeugt die Discovery-Dateien unter /.well-known/.

Agenten finden eine Seite nicht dadurch, dass sie sie lesen, sondern dadurch,
dass sie an festgelegten Pfaden nachsehen. Diese Datei erzeugt genau die
Eintraege, fuer die es hier tatsaechlich etwas zu finden gibt:

  /.well-known/agent-skills/index.json  die drei Methoden, die diese Seite
                                        veroeffentlicht, als abrufbare Skills
  /.well-known/api-catalog              die drei Messdatensaetze als Linkset
                                        (RFC 9727 / RFC 9264)
  /auth.md                              die Auskunft, dass nichts geschuetzt ist

Bewusst NICHT erzeugt werden OAuth- und OIDC-Metadaten sowie eine MCP Server
Card: Es gibt keine geschuetzten Endpunkte und keinen MCP-Server. Eine Datei,
die das Gegenteil behauptet, kostet jeden Agenten, der ihr folgt, einen
vergeblichen Aufruf — leere Metadaten sind schlechter als keine.

Die sha256-Summen im Skills-Index werden aus den Dateien berechnet, nicht
gepflegt. Damit kann der Index nicht von den Skills abdriften.

    python3 build-agent-discovery.py           # schreiben
    python3 build-agent-discovery.py --check   # nur pruefen, Exitcode 1 bei Abweichung
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

BASIS = "https://provinglab.dev"
DOCS = Path(__file__).resolve().parent / "docs"
SKILLS = DOCS / ".well-known" / "agent-skills"


def frontmatter(text):
    """Liest name und description aus dem YAML-Kopf einer SKILL-Datei."""
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for zeile in m.group(1).split("\n"):
        if ":" in zeile and not zeile.startswith(" "):
            k, v = zeile.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def skills_index():
    eintraege = []
    for datei in sorted(SKILLS.glob("*.md")):
        roh = datei.read_bytes()
        fm = frontmatter(roh.decode("utf-8"))
        eintraege.append({
            "name": fm.get("name", datei.stem),
            "type": "skill",
            "description": fm.get("description", ""),
            "url": f"{BASIS}/.well-known/agent-skills/{datei.name}",
            "sha256": hashlib.sha256(roh).hexdigest(),
            "license": fm.get("license", "CC-BY-4.0"),
        })
    return {
        "$schema": "https://agentskills.io/schema/v0.2.0/index.json",
        "version": "0.2.0",
        "name": "Proving Lab",
        "description": (
            "Reproducible methods from published measurements: how to read an "
            "extension's permissions, how to measure OCR recall with a control "
            "run, and how to choose between print-to-PDF and screen capture."
        ),
        "skills": eintraege,
    }


def datensaetze():
    """Die Messdatensaetze — echte, maschinenlesbare Ressourcen dieser Seite."""
    out = []
    for datei in sorted((DOCS / "data").glob("*.json")):
        try:
            inhalt = json.loads(datei.read_text(encoding="utf-8"))
        except Exception:
            inhalt = {}
        out.append({
            "datei": datei.name,
            "titel": inhalt.get("title") or inhalt.get("name") or datei.stem,
            "seite": inhalt.get("source") or inhalt.get("url") or "",
        })
    return out


def api_catalog():
    """RFC 9727: ein Linkset, das auf die veroeffentlichten Datensaetze zeigt.

    Es gibt hier keine aufrufbare API — wohl aber stabile, versionierte
    Datensaetze mit dokumentierter Methode. Genau die werden ausgewiesen,
    mit 'describedby' auf die Seite, die erklaert wie gemessen wurde.
    """
    linkset = []
    for d in datensaetze():
        url = f"{BASIS}/data/{d['datei']}"
        eintrag = {
            "anchor": url,
            "type": [{"href": "application/json"}],
            "describedby": [{"href": f"{BASIS}/data/", "type": "text/html"}],
            "license": [{"href": "https://creativecommons.org/licenses/by/4.0/"}],
        }
        if d["seite"]:
            eintrag["via"] = [{"href": d["seite"], "type": "text/html"}]
        linkset.append(eintrag)

    linkset.append({
        "anchor": f"{BASIS}/",
        "service-doc": [{"href": f"{BASIS}/agent.md", "type": "text/markdown"},
                        {"href": f"{BASIS}/llms.txt", "type": "text/plain"},
                        {"href": f"{BASIS}/llms-full.txt", "type": "text/plain"},
                        {"href": f"{BASIS}/about/", "type": "text/html"}],
        "describedby": [{"href": f"{BASIS}/.well-known/agent-skills/index.json",
                         "type": "application/json"}],
        "alternate": [{"href": f"{BASIS}/feed.xml", "type": "application/atom+xml"}],
    })
    return {"linkset": linkset}


AUTH_MD = """# auth.md

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
curl -X POST https://provinglab.dev/oauth/register \
  -H 'content-type: application/json' \
  -d '{"client_name":"my-agent"}'
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
curl -X POST https://provinglab.dev/oauth/token \
  -d 'grant_type=client_credentials&client_id=pl_...'
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
client equally. Requests identifying as `Python-urllib` are rejected by the
browser integrity check — use any other user agent.

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
"""


def protected_resource():
    """RFC 9728 — und zwar wahrheitsgemaess.

    Die Spezifikation verlangt nur 'resource'. 'authorization_servers' ist
    optional; eine leere Liste sagt korrekt aus, dass kein Autorisierungsserver
    Tokens fuer diese Ressource ausstellt. Damit steht in der Datei nichts
    Falsches — anders als bei einer erfundenen
    /.well-known/oauth-authorization-server, die Endpunkte behaupten wuerde,
    die es nicht gibt. Die wird deshalb weiterhin nicht angelegt.
    """
    return {
        "resource": BASIS,
        # Seit 02.08.2026 gibt es den Server wirklich: der Worker beantwortet
        # /.well-known/oauth-authorization-server, /oauth/register und
        # /oauth/token. Der Eintrag ist damit wahr — vorher stand hier eine
        # leere Liste, was ebenfalls wahr war, aber Clients half, die einen
        # Autorisierungsserver voraussetzen, nicht weiter.
        "authorization_servers": [BASIS],
        "scopes_supported": ["read"],
        "bearer_methods_supported": ["header"],
        # Das Entscheidende, damit niemand mehr hineinliest als dasteht:
        "authentication_required": False,
        "resource_documentation": f"{BASIS}/auth.md",
        "resource_policy_uri": f"{BASIS}/privacy.html",
        "resource_name": "Proving Lab",
        "tls_client_certificate_bound_access_tokens": False,
    }



def mcp_karte():
    """Server Card mit der Version aus dem Worker — nicht doppelt gepflegt.

    Sie stand einmal auf 1.0.0, waehrend der Worker 1.4.0 auslieferte. Eine
    Karte, die eine andere Version nennt als der Server, ist schlimmer als
    keine: Ein Client glaubt ihr.
    """
    quelle = DOCS.parent / "worker" / "mcp.js"
    version = "1.0.0"
    if quelle.exists():
        m = re.search(r'const VERSION = "([^"]+)"', quelle.read_text(encoding="utf-8"))
        if m:
            version = m.group(1)
    ziel = DOCS / ".well-known" / "mcp" / "server-card.json"
    if not ziel.exists():
        return None
    d = json.loads(ziel.read_text(encoding="utf-8"))
    d["serverInfo"]["version"] = version
    return d


def schreiben(pfad, inhalt, pruefen):
    if isinstance(inhalt, (dict, list)):
        neu = json.dumps(inhalt, indent=2, ensure_ascii=False) + "\n"
    else:
        neu = inhalt
    alt = pfad.read_text(encoding="utf-8") if pfad.exists() else ""
    zustand = "aktuell" if alt == neu else ("weicht ab" if pruefen else "geschrieben")
    if alt != neu and not pruefen:
        pfad.parent.mkdir(parents=True, exist_ok=True)
        pfad.write_text(neu, encoding="utf-8")
    print(f"  {str(pfad.relative_to(DOCS)):44} {len(neu):>6} B  {zustand}")
    return alt != neu


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    a = p.parse_args()

    idx = skills_index()
    if not idx["skills"]:
        sys.exit("Keine SKILL-Dateien gefunden — liegt etwas in docs/.well-known/agent-skills/?")

    abweichung = False
    abweichung |= schreiben(SKILLS / "index.json", idx, a.check)
    abweichung |= schreiben(DOCS / ".well-known" / "api-catalog", api_catalog(), a.check)
    abweichung |= schreiben(DOCS / ".well-known" / "oauth-protected-resource",
                            protected_resource(), a.check)
    karte = mcp_karte()
    if karte:
        abweichung |= schreiben(DOCS / ".well-known" / "mcp" / "server-card.json",
                                karte, a.check)
    abweichung |= schreiben(DOCS / "auth.md", AUTH_MD, a.check)

    print(f"  {len(idx['skills'])} Skills, {len(datensaetze())} Datensaetze")
    return 1 if (a.check and abweichung) else 0


if __name__ == "__main__":
    sys.exit(main())
