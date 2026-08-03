#!/usr/bin/env python3
"""Misst, ob der Endpunkt deutschsprachige Wissenschaftsplattformen liest.

    python3 messung-de-plattformen.py            # messen und Datensatz schreiben
    python3 messung-de-plattformen.py --zeigen   # nur ausgeben, nichts schreiben

Die bisherige Plattform-Messung (/measurements/citation-by-platform/) pruefte
18 Plattformen, fast alle englischsprachig — die Zielgruppe schreibt aber an
deutschsprachigen Hochschulen. Diese Messung stellt dieselbe Frage an die
Plattformen, die dort tatsaechlich zitiert werden: Repositorien, Kataloge,
Verlage, Rechtsprechung und amtliche Statistik aus dem deutschsprachigen Raum.

Methode wie bei der Quellenlisten-Messung: Jede Adresse geht an den Endpunkt,
und jede zurueckgegebene Quelle wird zweimal angefasst — einmal mit dem
Kennzeichen des Lesers, einmal mit Browser-Kopfzeilen. Eine Sperre zaehlt nur,
wenn der Browser durchkommt und der Leser nicht; sonst waere nicht
unterscheidbar, ob die Seite sperrt oder schlicht unerreichbar ist.

Kandidatenliste, festgelegt am 3. August 2026 VOR dem Lauf (nicht danach
ausgesucht, ob sie funktioniert):

  - SSOAR — als Kontrolle: dessen Wand fuer serverseitige Leser ist aus der
    Quellenlisten-Messung bekannt, ein Lauf ohne diesen Befund waere
    verdaechtig, nicht das Gegenteil.
  - PsychArchives (ZPID), peDOCS (Fachportal Paedagogik) und ein OPUS-4-
    Repositorium — die Repositorien, aus denen deutschsprachige
    Geistes- und Sozialwissenschaft zitiert.
  - Deutsche Nationalbibliothek — Katalogeintrag ueber den d-nb.info-Resolver.
  - Springer Link mit einem deutschsprachigen Titel (Wirtschaftsdienst) und
    Nomos eLibrary — die beiden grossen deutschsprachigen Verlagsplattformen.
  - beck-online — eine lizenzierte juristische Datenbank; die Schranke ist
    hier selbst der moegliche Befund.
  - openJur — freie Rechtsprechung ohne Schranke.
  - Statistik Austria und Destatis — amtliche Statistik, die in nahezu jeder
    empirischen Arbeit zitiert wird.

Vorab-Pruefung am 3. August 2026: Jede Adresse wurde vor dem Lauf einmal mit
Browser-Kopfzeilen abgerufen (curl, Firefox-Kennung, Weiterleitungen gefolgt)
und antwortete mit 200. Zwei zuerst gewaehlte Adressen lieferten dabei 404
(eine geratene IDN der DNB, ein geratener Springer-DOI) und wurden durch
gepruefte Datensaetze ersetzt — die IDN ueber die SRU-Schnittstelle der DNB,
den DOI ueber die Artikelliste der Zeitschrift. Ein 404 aus einer geratenen
Adresse waere kein Messwert, sondern eine eigene Panne, die als Ergebnis der
Seite erschiene.
"""
import argparse
import json
import pathlib
import time
import urllib.error
import urllib.request

MCP = "https://provinglab.dev/mcp"
HIER = pathlib.Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "data" / "2026-08-03-de-plattformen.json"

BROWSER = {
    "user-agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:141.0) "
                   "Gecko/20100101 Firefox/141.0"),
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "accept-language": "de-AT,de;q=0.9,en;q=0.7",
}

# Art, Plattform, Adresse — siehe Modulkommentar fuer Festlegung und Vorab-Pruefung.
LISTE = [
    ("repository",  "SSOAR (Kontrolle)",
     "https://www.ssoar.info/ssoar/handle/document/71234"),
    ("repository",  "PsychArchives (ZPID)",
     "https://psycharchives.org/handle/20.500.12034/2487"),
    ("repository",  "peDOCS",
     "https://www.pedocs.de/frontdoor.php?source_opus=24629"),
    ("repository",  "OPUS 4 (KOBV/ZIB)",
     "https://opus4.kobv.de/opus4-zib/frontdoor/index/index/docId/8138"),
    ("catalogue",   "Deutsche Nationalbibliothek",
     "https://d-nb.info/1279437049"),
    ("publisher",   "Springer Link (Wirtschaftsdienst)",
     "https://link.springer.com/article/10.1007/s10273-022-3350-x"),
    ("publisher",   "Nomos eLibrary",
     "https://www.nomos-elibrary.de/10.5771/0506-7286-2024-1-5/"
     "europaeisches-verfassungsrecht-im-normativen-staatsnotstand"),
    ("licensed db", "beck-online",
     "https://beck-online.beck.de/Dokument?vpath=bibdata/zeits/zfr/2024/cont/zfr.2024.1.1.htm"),
    ("case law",    "openJur",
     "https://openjur.de/u/2386045.html"),
    ("official statistics", "Statistik Austria",
     "https://www.statistik.at/statistiken/bevoelkerung-und-soziales/bevoelkerung/bevoelkerungsstand"),
    ("official statistics", "Destatis",
     "https://www.destatis.de/DE/Themen/Gesellschaft-Umwelt/Bevoelkerung/Bevoelkerungsstand/_inhalt.html"),
]


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
    for art, name, url in LISTE:
        wirt = url.split("/")[2]
        d, dauer = zitat(url)
        vollstaendig = bool(d.get("complete"))
        e = {
            "kind": art,
            "platform": name,
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
        print(f"  {'OK ' if vollstaendig else '-- '} {name:34} {e['seconds']:5.2f}s"
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
        "measurement": "de-plattformen",
        "date": "2026-08-03",
        "question": ("Eleven platforms a student at a German-speaking university "
                     "actually cites — repositories, the national library, German "
                     "publishers, case law, official statistics. Does the endpoint "
                     "read them, and where it does not: is the page walled, "
                     "unreachable, or just thin?"),
        "method": {
            "endpoint": MCP,
            "tool": "extract_citation",
            "sources": len(LISTE),
            "selection": ("Fixed on 3 August 2026 before the run and not chosen for "
                          "whether it works: four repositories (SSOAR as a known-walled "
                          "control, PsychArchives, peDOCS, one OPUS 4 instance), the "
                          "German National Library, two German-language publishers "
                          "(Springer Link, Nomos), a licensed legal database "
                          "(beck-online), free case law (openJur) and two official "
                          "statistics bodies (Statistik Austria, Destatis). Every "
                          "address answered 200 to a browser in the pre-check the same day."),
            "control": ("Every handed-back source was fetched twice — once with the "
                        "reader's own user agent, once with a browser's. A source counts "
                        "as walled only when the browser is answered and the reader is not."),
            "network": ("Commercial VPN exit on the local network, AS209854 "
                        "Cyberzone S.A., Frankfurt DE — not a plain residential line"),
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
