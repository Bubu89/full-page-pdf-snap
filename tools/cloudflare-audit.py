#!/usr/bin/env python3
"""Erhebt und verbessert die Cloudflare-Einstellungen von provinglab.dev.

    python3 tools/cloudflare-audit.py            # nur erheben, nichts aendern
    python3 tools/cloudflare-audit.py --apply    # die vorgeschlagenen Aenderungen setzen

Der Token kommt aus Vaultwarden und wird nirgends auf Platte geschrieben:

    bw unlock            # oder: vault-unlock
    export BW_SESSION=…
    export CF_API_TOKEN=$(bw get item 0fd9f886-bdb1-40a2-b364-24961e4d2253 \
                          | python3 -c 'import json,sys;print(json.load(sys.stdin)["notes"])')

Warum ein Skript und keine Klicks im Dashboard: eine Einstellung, die von Hand
gesetzt wurde, ist in einem halben Jahr nicht mehr nachvollziehbar. Hier steht,
was gesetzt wurde und warum — und ein zweiter Lauf zeigt, ob es noch so ist.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ZONE = "0d7110c80d576750944785d0ae759209"   # provinglab.dev
BASIS = "https://api.cloudflare.com/client/v4"

# Sollwerte. Jeder Eintrag traegt die Begruendung, die im Dashboard fehlt.
SOLL = {
    "always_use_https": ("on", "Ein Aufruf ueber http wuerde sonst ungeschuetzt beginnen."),
    "brotli":           ("on", "Kleinere Uebertragung fuer Text; kostet nichts."),
    "early_hints":      ("on", "Der Browser laedt CSS, waehrend die Seite noch entsteht."),
    "http3":            ("on", "Schnellerer Verbindungsaufbau auf Mobilfunk."),
    "min_tls_version":  ("1.2", "TLS 1.0/1.1 gelten als gebrochen."),
    "0rtt":             ("off", "0-RTT erlaubt Wiedereinspielung von Anfragen. Kein Gewinn hier."),
}


def ruf(pfad, methode="GET", koerper=None, token=None):
    d = json.dumps(koerper).encode() if koerper is not None else None
    r = urllib.request.Request(BASIS + pfad, d, {
        "authorization": "Bearer " + token,
        "content-type": "application/json",
    }, method=methode)
    try:
        return json.loads(urllib.request.urlopen(r, timeout=30).read())
    except urllib.error.HTTPError as e:
        return json.loads(e.read() or b'{"success":false,"errors":[]}')


def fehlergrund(antwort):
    fs = antwort.get("errors") or []
    return "; ".join(f"{f.get('code')}: {f.get('message')}" for f in fs) or "unbekannt"


MCP = '(http.host in {"provinglab.dev" "www.provinglab.dev"} and starts_with(http.request.uri.path, "/mcp"))'


def regel_setzen(token, phase, regel, kennung, zuerst=False):
    """Legt eine Regel in einer Ruleset-Phase an — einmal, nicht bei jedem Lauf.

    Cloudflare legt die Einstiegs-Rulesets erst an, wenn die erste Regel kommt;
    ein fehlendes Ruleset ist also kein Fehler, sondern der Normalfall beim
    ersten Mal. Erkannt wird eine schon vorhandene Regel an ihrer Beschreibung.
    """
    rs = ruf(f"/zones/{ZONE}/rulesets", token=token)
    if not rs.get("success"):
        return "Rulesets nicht lesbar: " + fehlergrund(rs)
    treffer = [r for r in rs["result"] if r["phase"] == phase]
    if treffer:
        rid = treffer[0]["id"]
        det = ruf(f"/zones/{ZONE}/rulesets/{rid}", token=token)
        vorhandene = det["result"].get("rules") or []
        for x in vorhandene:
            if x.get("description") == kennung:
                return "steht schon"
        # Bei Cache-Regeln gewinnt die erste zutreffende. Ans Ende angehaengt
        # bliebe die Ausnahme wirkungslos, weil die allgemeine Regel der Zone
        # jeden Pfad zuerst faengt.
        if zuerst and vorhandene:
            regel = dict(regel, position={"before": vorhandene[0]["id"]})
        r = ruf(f"/zones/{ZONE}/rulesets/{rid}/rules", "POST", regel, token)
    else:
        r = ruf(f"/zones/{ZONE}/rulesets", "POST", {
            "name": "default", "kind": "zone", "phase": phase, "rules": [regel],
        }, token)
    return "gesetzt" if r.get("success") else "FEHLER " + fehlergrund(r)


def ausnahme_bic(token):
    """Nimmt /mcp vom Browser Integrity Check aus — nur diesen einen Pfad."""
    return regel_setzen(token, "http_request_firewall_custom", {
        "action": "skip",
        "action_parameters": {"products": ["bic"]},
        "expression": MCP,
        "description": "mcp-endpoint-skip-bic",
        "enabled": True,
    }, "mcp-endpoint-skip-bic")


def cache_aus(token):
    """Nimmt /mcp vom Rand-Cache aus. Eine Antwort je Anfrage, keine alte Fassung."""
    return regel_setzen(token, "http_request_cache_settings", {
        "action": "set_cache_settings",
        "action_parameters": {"cache": False},
        "expression": MCP,
        "description": "mcp-endpoint-no-cache",
        "enabled": True,
    }, "mcp-endpoint-no-cache", zuerst=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="Aenderungen wirklich setzen")
    a = p.parse_args()

    token = os.environ.get("CF_API_TOKEN")
    if not token:
        sys.exit("CF_API_TOKEN fehlt — siehe Kopf dieser Datei.")

    # Nicht ueber /user/tokens/verify pruefen: fuer Konto-Token (cfat_…) meldet
    # der Endpunkt "Invalid API Token", obwohl der Token arbeitet. Am 1.8.2026
    # wurden so drei gueltige Tokens fuer widerrufen gehalten. Die ehrliche
    # Probe ist die Zone selbst — genau das, was gebraucht wird.
    z = ruf(f"/zones/{ZONE}", token=token)
    if not z.get("success"):
        print("Zone nicht erreichbar:", fehlergrund(z))
        sys.exit(1)
    print(f"Zone: {z['result']['name']}  Plan: {z['result']['plan']['name']}  "
          f"Status: {z['result']['status']}")

    print("\n--- Zone-Einstellungen " + ("(werden gesetzt)" if a.apply else "(nur Bericht)"))
    ist = ruf(f"/zones/{ZONE}/settings", token=token)
    if not ist.get("success"):
        print("  nicht lesbar:", fehlergrund(ist))
        print("  → der Token hat keinen Zone-Settings-Zugriff; das ist kein Fehler,")
        print("    sondern der Scope. Ein Token mit 'Zone Settings:Edit' waere noetig.")
    else:
        werte = {s["id"]: s["value"] for s in ist["result"]}
        for name, (soll, warum) in SOLL.items():
            hat = werte.get(name, "—")
            if str(hat) == str(soll):
                print(f"  OK        {name:18} {hat}")
                continue
            print(f"  ABWEICHEND {name:18} ist={hat}  soll={soll}   {warum}")
            if a.apply:
                r = ruf(f"/zones/{ZONE}/settings/{name}", "PATCH", {"value": soll}, token)
                print("             →", "gesetzt" if r.get("success") else "FEHLER " + fehlergrund(r))

    print("\n--- DNSSEC")
    d = ruf(f"/zones/{ZONE}/dnssec", token=token)
    if d.get("success"):
        st = d["result"].get("status")
        print("  Status:", st)
        if st != "active":
            print("  Der Registrar ist Cloudflare selbst, der DS-Eintrag wird also")
            print("  automatisch gesetzt. Ohne DNSSEC laesst sich die Antwort auf dem Weg faelschen.")
            if a.apply:
                r = ruf(f"/zones/{ZONE}/dnssec", "PATCH", {"status": "active"}, token)
                print("  →", "aktiviert" if r.get("success") else "FEHLER " + fehlergrund(r))
    else:
        print("  nicht lesbar:", fehlergrund(d))

    print("\n--- Browser Integrity Check vor /mcp")
    bc = ruf(f"/zones/{ZONE}/settings/browser_check", token=token)
    print("  browser_check:", bc["result"]["value"] if bc.get("success") else fehlergrund(bc))
    print("  Gemessen 3.8.2026: eine Anfrage mit user-agent 'Python-urllib' bekommt")
    print("  HTTP 403 mit 'error code: 1010' — das ist der Browser Integrity Check,")
    print("  bevor der Worker die Anfrage sieht. Er trifft genau die wissenschaftliche")
    print("  Nutzung: ein Skript, das eine Literaturliste durch den Endpunkt schickt.")
    print("  Er schuetzt hier auch nichts — der Endpunkt ist oeffentlich, zustandslos")
    print("  und ohne Anmeldung. Die Ausnahme gilt nur fuer /mcp, nicht fuer die Website.")
    if a.apply:
        print("  →", ausnahme_bic(token))

    print("\n--- Cache auf /mcp")
    print("  Die allgemeine Cache-Regel der Zone deckt auch /mcp ab. Am 2.8. lag eine")
    print("  reparierte Antwort fuenf Minuten lang als alte Fassung am Rand.")
    if a.apply:
        print("  →", cache_aus(token))

    print("\n--- Weitere Rulesets")
    print("  Gemessen 3.8.2026: Anfragen mit user-agent 'Python-urllib' bekommen HTTP 403,")
    print("  bevor der Worker sie sieht. Das trifft genau die wissenschaftliche Nutzung —")
    print("  ein Skript, das eine Literaturliste durch den Endpunkt schickt.")
    rs = ruf(f"/zones/{ZONE}/rulesets", token=token)
    if rs.get("success"):
        for r in rs["result"]:
            print(f"  Ruleset: {r.get('phase'):34} {r.get('name')}")
    else:
        print("  Rulesets nicht lesbar:", fehlergrund(rs))
        print("  → braucht 'Zone WAF:Edit'. Ohne das bleibt nur das Dashboard:")
    print("  Massnahme: Security → Bots → Bot Fight Mode AUS,")
    print("  oder eine WAF-Skip-Regel  (http.request.uri.path eq \"/mcp\")  vor die Bot-Regeln.")

    print("\n--- Cache auf /mcp")
    print("  Der Endpunkt darf nicht am Rand zwischengespeichert werden: am 2.8. lag eine")
    print("  reparierte Antwort fuenf Minuten lang als alte Fassung im Cache.")
    print("  Massnahme: Caching → Cache Rules → (http.request.uri.path eq \"/mcp\") → Bypass cache.")


if __name__ == "__main__":
    main()
