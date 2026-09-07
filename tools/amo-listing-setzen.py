#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kategorien und Tags des AMO-Eintrags setzen (M1).

Ohne `--anwenden` wird NICHTS geschrieben: das Werkzeug zeigt den Ist-Stand,
den Soll-Stand und den Unterschied. Ein Listing ist oeffentlich; ein
versehentlicher Lauf soll es nicht veraendern.

Der Schluessel muss aus dem **Eigentuemerkonto** stammen. Das Werkzeug
prueft das VOR dem Schreiben ueber `/accounts/profile/` und bricht ab, wenn
das Konto nicht unter den Autoren steht — sonst kaeme ein 403 erst beim
Schreibversuch, und der Grund waere nicht ersichtlich.
"""
import base64
import hashlib
import hmac
import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request

SLUG = "full_page_pdf_snap_webpagesave"
API = "https://addons.mozilla.org/api/v5"

SOLL_KATEGORIEN = ["privacy-security", "bookmarks", "download-management"]
SOLL_TAGS = ["download", "privacy", "scholar"]

ANWENDEN = "--anwenden" in sys.argv


def vault_jwt_paar():
    """Issuer und Secret aus dem Vault holen. Gibt (issuer, secret, name)."""
    roh = subprocess.run(
        ["bash", "-c", 'bw list items --session "$(cat /dev/shm/bw-session)"'],
        capture_output=True, text=True, timeout=120).stdout
    try:
        items = json.loads(roh)
    except Exception:
        return None, None, None
    kandidaten = []
    for i in items:
        if not re.search(r"amo|addons\.mozilla", json.dumps(i), re.I):
            continue
        f = {(x.get("name") or "").lower(): x.get("value")
             for x in (i.get("fields") or [])}
        iss = next((v for k, v in f.items()
                    if "issuer" in k or "aussteller" in k), None)
        sec = next((v for k, v in f.items() if "secret" in k), None)
        if iss and sec:
            kandidaten.append((iss, sec, i.get("name", "")))
    # Ein Eintrag, der das Add-on im Namen fuehrt, hat Vorrang
    kandidaten.sort(key=lambda k: 0 if "snap" in k[2].lower() else 1)
    return kandidaten[0] if kandidaten else (None, None, None)


def jwt(issuer, secret):
    def b64(b):
        return base64.urlsafe_b64encode(b).rstrip(b"=")
    kopf = b64(json.dumps({"alg": "HS256", "typ": "JWT"}).encode())
    jetzt = int(time.time())
    nutz = b64(json.dumps({"iss": issuer, "jti": str(jetzt),
                           "iat": jetzt, "exp": jetzt + 280}).encode())
    sig = b64(hmac.new(secret.encode(), kopf + b"." + nutz,
                       hashlib.sha256).digest())
    return (kopf + b"." + nutz + b"." + sig).decode()


def hole(pfad, token=None, daten=None, methode="GET"):
    req = urllib.request.Request(API + pfad, method=methode)
    req.add_header("User-Agent", "provinglab-m1/1.0")
    if token:
        req.add_header("Authorization", "JWT " + token)
    if daten is not None:
        req.add_header("Content-Type", "application/json")
        req.data = json.dumps(daten).encode()
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read() or b"{}")


def main():
    ist = hole(f"/addons/addon/{SLUG}/")
    ist_kat = sorted(ist.get("categories") or [])
    ist_tags = sorted(ist.get("tags") or [])
    autoren = {a.get("id"): a.get("name") for a in ist.get("authors", [])}

    print(f"Add-on   : {SLUG}")
    print(f"Autoren  : {autoren}")
    print(f"Kategorien  ist : {ist_kat}")
    print(f"            soll: {sorted(SOLL_KATEGORIEN)}")
    print(f"Tags        ist : {ist_tags}")
    print(f"            soll: {sorted(SOLL_TAGS)}")
    aenderung = (ist_kat != sorted(SOLL_KATEGORIEN)
                 or ist_tags != sorted(SOLL_TAGS))
    if not aenderung:
        print("\nNichts zu tun — Ist entspricht Soll.")
        return 0
    print("\nUnterschied:")
    for weg in sorted(set(ist_kat) - set(SOLL_KATEGORIEN)):
        print(f"  Kategorie  -  {weg}")
    for neu in sorted(set(SOLL_KATEGORIEN) - set(ist_kat)):
        print(f"  Kategorie  +  {neu}")
    for weg in sorted(set(ist_tags) - set(SOLL_TAGS)):
        print(f"  Tag        -  {weg}")
    for neu in sorted(set(SOLL_TAGS) - set(ist_tags)):
        print(f"  Tag        +  {neu}")

    if not ANWENDEN:
        print("\nTrockenlauf. Zum Schreiben: --anwenden")
        return 0

    iss, sec, name = vault_jwt_paar()
    if not iss:
        print("\nKein AMO-JWT-Paar im Vault gefunden.")
        return 2
    tok = jwt(iss, sec)
    try:
        profil = hole("/accounts/profile/", tok)
    except urllib.error.HTTPError as e:
        print(f"\nSchluessel nicht gueltig (HTTP {e.code}).")
        return 2
    kid = profil.get("id")
    print(f"\nSchluessel aus Vault-Eintrag {name!r} -> Konto {kid} "
          f"({profil.get('display_name')!r})")
    if kid not in autoren:
        print("ABBRUCH: Dieses Konto ist NICHT Autor des Add-ons. "
              "Ein Schreibversuch waere ein 403.")
        print("Ein Schluessel des Eigentuemerkontos wird gebraucht: "
              "https://addons.mozilla.org/developers/addon/api/key/")
        return 3

    ergebnis = hole(f"/addons/addon/{SLUG}/", tok,
                    {"categories": SOLL_KATEGORIEN, "tags": SOLL_TAGS},
                    "PATCH")
    print("Geschrieben. Neuer Stand laut Antwort:")
    print(f"  Kategorien: {sorted(ergebnis.get('categories') or [])}")
    print(f"  Tags      : {sorted(ergebnis.get('tags') or [])}")
    print("\nNachher-Messung fruehestens in 48 h: "
          "python3 tools/amo-sichtbarkeit.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
