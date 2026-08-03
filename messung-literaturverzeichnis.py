#!/usr/bin/env python3
"""Misst den Weg von einer Quellenliste zum fertigen Literaturverzeichnis.

    python3 messung-literaturverzeichnis.py            # messen und Datensatz schreiben
    python3 messung-literaturverzeichnis.py --zeigen   # nur ausgeben, nichts schreiben

Die Frage ist nicht, ob ein Zitations-Leser Metadaten findet — das ist gemessen
(/measurements/citation-extraction/). Die Frage ist, was am Ende einer echten
Quellenliste steht: wie viele Eintraege ein Werkzeug vollstaendig liefert, welche
es zurueckgibt, und ob der Grund der Zurueckgabe die Wand der Seite ist oder ein
Fehler des Lesers.

Deshalb wird jede Quelle zweimal angefasst:

  1. serverseitig, wie es der Endpunkt tut  -> was ein Leser ohne Browser bekommt
  2. mit Browser-Kopfzeilen                 -> ob dieselbe Adresse einem Browser antwortet

Weichen beide voneinander ab, liegt es an der Bot-Abwehr der Seite, nicht am
Leser. Genau diese Faelle sind die, in denen ein Mensch die Seite im Browser
oeffnen und selbst sichern muss.

Die Liste ist vorher festgelegt und nicht danach ausgesucht, ob sie funktioniert.
"""
import argparse
import json
import pathlib
import time
import urllib.error
import urllib.request

MCP = "https://provinglab.dev/mcp"
HIER = pathlib.Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "data" / "2026-08-03-reading-list-to-bibliography.json"

BROWSER = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) "
                   "Gecko/20100101 Firefox/141.0"),
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "en-GB,en;q=0.9,de;q=0.8",
}

# Eine Quellenliste, wie sie in einer betriebswirtschaftlichen Modularbeit
# entsteht: Verlage, Open Access, Repositorien, Amtliches, Graue Literatur,
# ein Nachschlagewerk und eine nackte DOI. Vorher festgelegt.
LISTE = [
    ("publisher",   "https://www.sciencedirect.com/science/article/pii/S0148296319304564"),
    ("publisher",   "https://www.tandfonline.com/doi/full/10.1080/00207543.2020.1824085"),
    ("publisher",   "https://link.springer.com/article/10.1007/s11846-020-00426-9"),
    ("publisher",   "https://onlinelibrary.wiley.com/doi/10.1002/bse.2882"),
    ("publisher",   "https://journals.sagepub.com/doi/10.1177/0008125619867910"),
    ("open access", "https://www.mdpi.com/2071-1050/12/16/6597"),
    ("open access", "https://www.frontiersin.org/articles/10.3389/fpsyg.2021.620766/full"),
    ("open access", "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0247139"),
    ("repository",  "https://www.ssoar.info/ssoar/handle/document/71234"),
    ("repository",  "https://arxiv.org/abs/1706.03762"),
    ("repository",  "https://zenodo.org/records/3832945"),
    ("preprint",    "https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3529682"),
    ("official",    "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32016R0679"),
    ("official",    "https://www.oecd.org/en/publications/oecd-digital-economy-outlook-2024-volume-1_a1689dc5-en.html"),
    ("official",    "https://www.statistik.at/statistiken/forschung-innovation-digitalisierung"),
    ("grey lit",    "https://www.wko.at/eservices"),
    ("reference",   "https://en.wikipedia.org/wiki/Digital_transformation"),
    ("reference",   "https://plato.stanford.edu/entries/computing-responsibility/"),
    ("bare doi",    "https://doi.org/10.1016/j.jbusres.2019.09.022"),
    ("news",        "https://www.derstandard.at/story/3000000200000/"),
]

# Jede Adresse wurde vor dem Lauf einmal im Browser geprueft und antwortet mit
# 200 — ausser der OECD, die auch einem Browser aus einem Rechenzentrum 403
# gibt. Ein 404 aus einer geratenen Adresse waere kein Messwert, sondern eine
# eigene Panne, die als Ergebnis der Seite erschiene.


def zitat(url):
    """Ruft den Endpunkt so auf, wie es ein Agent tut."""
    koerper = json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "extract_citation", "arguments": {"url": url}},
    }).encode()
    # Der eigene Endpunkt liegt hinter Cloudflares Browser Integrity Check, und
    # der weist "Python-urllib/3.x" mit 1010 ab — die Standardbibliothek der
    # Sprache, in der die meisten Agenten geschrieben sind. Bis das pfadgenau
    # abgestellt ist, muss auch ein ehrlicher Client sich benennen.
    r = urllib.request.Request(MCP, koerper, {
        "content-type": "application/json",
        "user-agent": "provinglab-measurement/1.0 (+https://provinglab.dev/)",
    })
    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(r, timeout=60) as a:
            huelle = json.load(a)
        d = json.loads(huelle["result"]["content"][0]["text"])
    except Exception as e:
        return {"complete": False, "warning": f"endpoint: {type(e).__name__}"}, time.monotonic() - t0
    return d, time.monotonic() - t0


def abruf(url, kopf):
    """Status und Groesse einer Antwort. Weiterleitungen werden gefolgt."""
    r = urllib.request.Request(url, headers=kopf)
    try:
        with urllib.request.urlopen(r, timeout=45) as a:
            roh = a.read(400_000)
            return {"status": a.status, "bytes": len(roh)}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "bytes": 0}
    except Exception as e:
        return {"status": type(e).__name__, "bytes": 0}


def messen():
    eintraege = []
    for art, url in LISTE:
        wirt = url.split("/")[2]
        d, dauer = zitat(url)
        vollstaendig = bool(d.get("complete"))
        e = {
            "kind": art,
            "host": wirt,
            "url": url,
            "complete": vollstaendig,
            "seconds": round(dauer, 2),
            "warning": d.get("warning") or None,
            "has_ris": bool(d.get("ris")),
            "has_bibtex": bool(d.get("bibtex")),
            "fields": sorted(k for k in ("authors", "title", "year", "doi",
                                         "journal", "publisher", "licence")
                             if d.get(k)),
        }
        if not vollstaendig:
            # Nur bei Zurueckgabe interessiert, ob die Seite ueberhaupt antwortet.
            e["as_reader"] = abruf(url, {"user-agent": "provinglab-citation/1.0"})
            e["as_browser"] = abruf(url, BROWSER)
        eintraege.append(e)
        print(f"  {'OK ' if vollstaendig else '-- '} {wirt:34} {e['seconds']:5.2f}s"
              f"  {'' if vollstaendig else (e['warning'] or '')[:40]}")
    return eintraege


def auswerten(eintraege):
    ganz = [e for e in eintraege if e["complete"]]
    rest = [e for e in eintraege if not e["complete"]]
    # Eine Wand ist nachgewiesen, wenn der Browser durchkommt und der Leser nicht.
    wand = [e for e in rest
            if e.get("as_browser", {}).get("status") == 200
            and e.get("as_reader", {}).get("status") != 200]
    tot = [e for e in rest
           if e.get("as_browser", {}).get("status") != 200]
    duenn = [e for e in rest if e not in wand and e not in tot]
    nach_art = {}
    for e in eintraege:
        a = nach_art.setdefault(e["kind"], {"total": 0, "complete": 0})
        a["total"] += 1
        a["complete"] += 1 if e["complete"] else 0
    return {
        "sources": len(eintraege),
        "complete_records": len(ganz),
        "handed_back": len(rest),
        "handed_back_behind_a_wall": len(wand),
        "handed_back_page_unreachable": len(tot),
        "handed_back_thin_page": len(duenn),
        "seconds_total": round(sum(e["seconds"] for e in eintraege), 1),
        "seconds_per_source": round(sum(e["seconds"] for e in eintraege) / len(eintraege), 2),
        "by_kind": nach_art,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--zeigen", action="store_true")
    a = p.parse_args()

    print(f"{len(LISTE)} Quellen gegen {MCP}\n")
    eintraege = messen()
    z = auswerten(eintraege)
    print("\n", json.dumps(z, ensure_ascii=False, indent=1))

    if a.zeigen:
        return
    datensatz = {
        "measurement": "reading-list-to-bibliography",
        "date": "2026-08-03",
        "question": ("Twenty sources as a term paper collects them: how many become "
                     "citable records without a human, which are handed back, and is "
                     "the reason the page's wall or the reader's limit?"),
        "method": {
            "endpoint": MCP,
            "tool": "extract_citation",
            "sources": len(LISTE),
            "selection": ("Fixed before the run and not chosen for whether it works: "
                          "five publishers, three open access, three repositories, one "
                          "preprint server, three official bodies, grey literature, two "
                          "reference works, a bare DOI and a news article."),
            "control": ("Every handed-back source was fetched twice — once with the "
                        "reader's own user agent, once with a browser's. A source counts "
                        "as walled only when the browser is answered and the reader is not."),
        },
        "results": z,
        "per_source": eintraege,
        "license": "CC-BY-4.0",
    }
    ZIEL.write_text(json.dumps(datensatz, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    print(f"\ngeschrieben: {ZIEL.relative_to(HIER)}")


if __name__ == "__main__":
    main()
