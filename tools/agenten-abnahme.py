#!/usr/bin/env python3
"""Ruft jedes Werkzeug auf, das ein Agent hier benutzen soll — mit echten Argumenten.

    python3 tools/agenten-abnahme.py
    python3 tools/agenten-abnahme.py --json

Der Unterschied zu `tools/links-pruefen.py`: dort wird geprueft, ob eine Adresse
antwortet. Hier wird geprueft, ob die **Antwort brauchbar** ist. Ein Endpunkt,
der 200 und einen leeren Datensatz liefert, besteht jeden Verfuegbarkeitstest
und ist trotzdem kaputt.

Jede Pruefung nennt deshalb eine Bedingung an den Inhalt, nicht am Status.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request

BASIS = "https://provinglab.dev"
KENNUNG = "provinglab-abnahme/1.0 (+https://provinglab.dev/for-agents/)"
ERGEBNIS = []


def hol(pfad, kopf=None):
    req = urllib.request.Request(BASIS + pfad,
                                 headers={"user-agent": KENNUNG, **(kopf or {})})
    t = time.time()
    with urllib.request.urlopen(req, timeout=45) as a:
        return a.read(), a.status, round(time.time() - t, 2)


def mcp(name, argumente, id_=1):
    koerper = json.dumps({"jsonrpc": "2.0", "id": id_, "method": "tools/call",
                          "params": {"name": name, "arguments": argumente}}).encode()
    req = urllib.request.Request(BASIS + "/mcp", koerper,
                                 {"content-type": "application/json",
                                  "user-agent": KENNUNG})
    t = time.time()
    with urllib.request.urlopen(req, timeout=60) as a:
        d = json.load(a)
    dauer = round(time.time() - t, 2)
    if "error" in d:
        raise RuntimeError(d["error"].get("message", str(d["error"])))
    text = d["result"]["content"][0]["text"]
    try:
        return json.loads(text), dauer, len(text)
    except json.JSONDecodeError:
        return text, dauer, len(text)


def pruefe(name, fn, bedingung):
    """`bedingung` bekommt das Ergebnis und gibt einen Satz zurueck, wenn es
    NICHT stimmt — sonst None. Formuliert als „was muss wahr sein", damit im
    Fehlerfall dasteht, was erwartet wurde."""
    try:
        wert, dauer, groesse = fn()
    except Exception as e:
        ERGEBNIS.append({"werkzeug": name, "ok": False,
                         "grund": f"{type(e).__name__}: {str(e)[:70]}"})
        print(f"  --  {name:<40} {type(e).__name__}: {str(e)[:44]}")
        return
    fehler = bedingung(wert)
    ERGEBNIS.append({"werkzeug": name, "ok": not fehler, "sekunden": dauer,
                     "bytes": groesse, "grund": fehler})
    zeichen = "OK " if not fehler else "-- "
    print(f"  {zeichen} {name:<40} {dauer:>5.2f}s {groesse:>7} B  {fehler or ''}")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    a = p.parse_args()

    print("=== MCP: die sechs Werkzeuge, mit echten Argumenten ===")

    pruefe("initialize", lambda: (
        json.loads(urllib.request.urlopen(urllib.request.Request(
            BASIS + "/mcp",
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05",
                                   "capabilities": {},
                                   "clientInfo": {"name": "abnahme", "version": "1"}}}).encode(),
            {"content-type": "application/json", "user-agent": KENNUNG}),
            timeout=30).read()), 0, 0),
        lambda d: None if d.get("result", {}).get("serverInfo", {}).get("version")
        else "keine Serverfassung in der Antwort")

    pruefe("tools/list", lambda: (
        json.loads(urllib.request.urlopen(urllib.request.Request(
            BASIS + "/mcp",
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list",
                        "params": {}}).encode(),
            {"content-type": "application/json", "user-agent": KENNUNG}),
            timeout=30).read()), 0, 0),
        lambda d: None if len(d.get("result", {}).get("tools", [])) >= 6
        else f"nur {len(d.get('result', {}).get('tools', []))} Werkzeuge statt 6")

    pruefe("extract_citation (offen zugaenglich)",
           lambda: mcp("extract_citation",
                       {"url": "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0245023"}),
           lambda d: None if d.get("complete") and d.get("title") and d.get("ris")
           else "complete, title oder ris fehlt — der Datensatz ist unbrauchbar")

    pruefe("extract_citation (Sperrseite)",
           lambda: mcp("extract_citation",
                       {"url": "https://www.sciencedirect.com/science/article/pii/S0148296319304564"}),
           lambda d: None if d.get("complete") is False and d.get("nextStep")
           else "eine Ablehnung muss complete:false UND nextStep tragen")

    pruefe("how_to_capture",
           lambda: mcp("how_to_capture", {"agent": "computer-use", "browser": "firefox"}),
           lambda d: None if json.dumps(d).find("addons.mozilla.org") > 0
           else "keine Store-Adresse in der Antwort")

    pruefe("open_work",
           lambda: mcp("open_work", {}),
           lambda d: None if len(d.get("open_tasks") or d.get("tasks") or []) > 0
           else "keine offenen Aufgaben geliefert")

    pruefe("list_measurements",
           lambda: mcp("list_measurements", {}),
           lambda d: None if len(json.dumps(d)) > 500 else "verdaechtig kurze Liste")

    # Der Parameter heisst `dataset` und will einen .json-Dateinamen — das
    # steht im inputSchema, und der erste Entwurf dieser Abnahme hat es nicht
    # gelesen und `id` geschickt. Der Endpunkt antwortete korrekt mit einer
    # Fehlermeldung, die genau das sagte; die Abnahme meldete trotzdem einen
    # Defekt. Eine Pruefung, die das Schema ignoriert, misst sich selbst.
    pruefe("get_measurement_data",
           lambda: mcp("get_measurement_data",
                       {"dataset": "2026-08-03-install-without-a-click.json"}),
           lambda d: None if json.dumps(d).find("marionette") > 0
           else "der angeforderte Datensatz kam nicht zurueck")

    pruefe("get_method",
           lambda: mcp("get_method", {"name": "citation-extraction"}),
           lambda d: None if len(json.dumps(d)) > 300 else "verdaechtig kurze Methode")

    print("\n=== Auffindbarkeit: was ein Agent liest, bevor er handelt ===")
    for pfad, muss in (
        ("/agent.md", "Accept: text/markdown"),
        ("/llms.txt", "llms-full.txt"),
        ("/llms-full.txt", "provinglab"),
        ("/AGENTS.md", "rechtscheck"),
        ("/.well-known/agent-skills/index.json", "install-an-extension-headless"),
        ("/.well-known/mcp/server-card.json", "provinglab"),
        ("/.well-known/api-catalog", "agent.md"),
        ("/.well-known/security.txt", "Expires"),
        ("/sitemap.xml", "install-an-extension"),
        ("/robots.txt", "Sitemap"),
    ):
        pruefe(pfad, lambda p=pfad: (hol(p)[0].decode("utf-8", "replace"),
                                     hol(p)[2], len(hol(p)[0])),
               lambda t, m=muss: None if m in t else f"'{m}' fehlt im Inhalt")

    print("\n=== Die sieben Faehigkeiten als Markdown ===")
    roh, _, _ = hol("/.well-known/agent-skills/index.json")
    for s in json.loads(roh)["skills"]:
        adr = s["url"].replace(BASIS, "")
        pruefe(s["name"], lambda a=adr: (hol(a)[0].decode("utf-8", "replace"),
                                         hol(a)[2], len(hol(a)[0])),
               lambda t: None if len(t) > 800 else "verdaechtig kurz")

    print("\n=== Markdown statt HTML (spart 61-66 %) ===")
    for pfad in ("/for-agents/", "/measurements/install-an-extension-without-a-click/"):
        pruefe(f"{pfad} als Markdown",
               lambda p=pfad: (hol(p, {"accept": "text/markdown"})[0].decode("utf-8", "replace"),
                               hol(p, {"accept": "text/markdown"})[2],
                               len(hol(p, {"accept": "text/markdown"})[0])),
               lambda t: None if not t.lstrip().startswith("<")
               else "liefert HTML statt Markdown")

    print("\n=== Der Werkzeugname als Adresse (der haeufige Irrtum) ===")
    pruefe("/open_work weist den Weg",
           lambda: (urllib.request.urlopen(urllib.request.Request(
               BASIS + "/open_work", headers={"user-agent": KENNUNG}), timeout=20).read()
               if False else _fehler_koerper("/open_work")),
           lambda t: None if "tools/call" in t else "kein Hinweis auf den richtigen Aufruf")

    n = sum(1 for x in ERGEBNIS if x["ok"])
    print(f"\n{n} von {len(ERGEBNIS)} Pruefungen bestanden.")
    if a.json:
        print(json.dumps(ERGEBNIS, indent=2, ensure_ascii=False))
    return 0 if n == len(ERGEBNIS) else 1


def _fehler_koerper(pfad):
    """Der Worker antwortet hier bewusst mit 404 und einem hilfreichen Koerper —
    urlopen wirft dabei, der Koerper steckt in der Ausnahme."""
    try:
        req = urllib.request.Request(BASIS + pfad, headers={"user-agent": KENNUNG})
        with urllib.request.urlopen(req, timeout=20) as a:
            return a.read().decode("utf-8", "replace"), 0, 0
    except urllib.error.HTTPError as e:
        roh = e.read().decode("utf-8", "replace")
        return roh, 0, len(roh)


if __name__ == "__main__":
    sys.exit(main())
