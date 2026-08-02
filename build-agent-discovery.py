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
        "service-doc": [{"href": f"{BASIS}/llms.txt", "type": "text/plain"},
                        {"href": f"{BASIS}/about/", "type": "text/html"}],
        "describedby": [{"href": f"{BASIS}/.well-known/agent-skills/index.json",
                         "type": "application/json"}],
        "alternate": [{"href": f"{BASIS}/feed.xml", "type": "application/atom+xml"}],
    })
    return {"linkset": linkset}


AUTH_MD = """# auth.md

Agent audience: any automated client reading this site.

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
"""


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
    abweichung |= schreiben(DOCS / "auth.md", AUTH_MD, a.check)

    print(f"  {len(idx['skills'])} Skills, {len(datensaetze())} Datensaetze")
    return 1 if (a.check and abweichung) else 0


if __name__ == "__main__":
    sys.exit(main())
