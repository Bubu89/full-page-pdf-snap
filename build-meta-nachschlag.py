#!/usr/bin/env python3
"""Ergänzt Wahrnehmungs-Metadaten, die beim Bau der Seiten untergegangen sind.

Befund 15.08.2026: Nur die Beitragsseiten trugen Open Graph, Twitter-Card und
JSON-LD mit keywords — die Hub-Seiten (about, data, deutsch, measurements/,
notes/, tools/, privacy) hatten nichts davon, und <meta name="keywords">
fehlte überall. Ein geteilter Link auf eine Hub-Seite zeigte deshalb keine
Vorschau, und die Seiten tragen keine Schlagworte.

Drei Ergänzungen, alle idempotent:

  1. <meta name="keywords"> je Seite aus der Karte unten; wo ein JSON-LD-Block
     schon keywords trägt, werden die uebernommen statt der Karte.
  2. Fehlendes Open Graph + twitter:card auf Hub-Seiten, abgeleitet aus
     title/description/canonical der Seite — keine neuen Texte.
  3. JSON-LD: Hub-Seiten ohne Block bekommen ein WebPage/CollectionPage mit
     keywords; bestehende TechArticle/Article/HowTo-Bloecke ohne keywords
     bekommen die der Karte.

Nicht angefasst: Weiterleitungs-Stubs (meta refresh) und die 404-Seite.

    python3 build-meta-nachschlag.py           # schreiben
    python3 build-meta-nachschlag.py --check   # nur berichten, Exitcode 1 bei Rest
"""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
CHECK = "--check" in sys.argv

# Schlagworte je Seite. Seiten, deren JSON-LD schon keywords traegt, brauchen
# keinen Eintrag — die vorhandenen werden uebernommen. Deutsch, wo die Seite
# deutsch ist.
KEYWORDS = {
    "index.html": "measurements, browser tools, citation extraction, OCR, "
                  "AI agents, raw data, control run, web archiving",
    "about/index.html": "about, disclosure, non-commercial publication, "
                        "measurements, operator, contact",
    "anleitung/webseite-als-pdf-speichern/index.html":
        "Webseite als PDF speichern, Internetquelle sichern, Abrufdatum, "
        "Quellenangabe, PDF ohne Seitenumbruch, Beweissicherung",
    "data/index.html": "raw data, measurement data, JSON, CC BY 4.0, "
                       "OCR recall, extension permissions, control run",
    "deutsch/index.html": "deutschsprachige Fassungen, Zitationsdaten, "
                          "Literaturverzeichnis erstellen, Abrufdatum, "
                          "Internetquellen zitieren",
    "disclaimer/index.html": "disclaimer, limitation of liability, "
                             "Haftungsausschluss, no warranty",
    "for-agents/index.html": "MCP server, AI agents, citation endpoint, "
                             "extract_citation, RIS, BibTeX, headless install, "
                             "browser extension",
    "how-to/save-a-webpage-as-pdf/index.html":
        "save webpage as PDF, full page PDF, web archiving, citation, "
        "retrieval date, print to PDF, screenshot, OCR",
    "how-to/for-students/index.html":
        "students, term paper, citable source, permalink, retrieval date, "
        "print to PDF, screenshot, OCR, web archiving",
    "how-to/firefox-and-chrome/index.html":
        "Firefox add-on, Chrome extension, academic workflow, citation, "
        "print to PDF, screenshot, OCR, web archiving",
    "measurements/index.html": "measurements, browser tools, OCR recall, "
                               "extension permissions, method, raw data, "
                               "control run",
    "measurements/extension-permissions-risk/index.html":
        "extension permissions, activeTab, host permissions, "
        "browser extension security, risk assessment",
    "measurements/install-an-extension-without-a-click/index.html":
        "headless install, Marionette, browser extension, automation, "
        "Firefox, install without a click",
    "mitmachen/index.html": "Gegenmessung, Reproduktion, Rohdaten, Korrektur "
                            "melden, mitmachen",
    "notes/index.html": "notes, build reports, browser extensions, "
                        "AI assistant, failure analysis",
    "notes/building-with-ai-what-went-wrong/index.html":
        "AI assistant, software development, failure log, debugging, "
        "lessons learned",
    "notes/mcp-server-what-it-solves/index.html":
        "MCP server, Model Context Protocol, JSON-RPC, llms.txt, "
        "citation endpoint, context cost",
    "notes/nineteen-issues/index.html":
        "issue triage, browser extension, Firefox, Chrome, bug reports",
    "notes/smaller-files-better-ocr/index.html":
        "OCR, file size, image compression, grayscale, Tesseract, PDF",
    "notes/sources-a-machine-cannot-cite/index.html":
        "bot defence, paywall, citation, browser extension, retrieval date",
    "notes/what-an-agent-can-do-with-an-extension/index.html":
        "AI agent, browser extension, input events, XTEST, CDP, Playwright, "
        "activeTab",
    "notes/what-an-agent-may-install/index.html":
        "AI agent, extension install, consent, automation, Firefox, Chrome",
    "notes/who-actually-reads-this/index.html":
        "crawler logs, web analytics, GPTBot, ClaudeBot, reader statistics",
    "privacy.html": "privacy policy, no data collection, no tracking, "
                    "browser extension, activeTab",
    "recipes/index.html": "recipes, citation workflow, web source, RIS, "
                          "BibTeX, reading list",
    "tools/index.html": "tools, browser extension, webpage to PDF, "
                        "citation endpoint, MCP server",
}

# Deutsche Seiten fuer inLanguage im neuen JSON-LD-Block.
DEUTSCH = {"anleitung/webseite-als-pdf-speichern/index.html",
           "deutsch/index.html", "mitmachen/index.html"}

# Index-Seiten sind Sammlungen, keine Einzelseiten.
SAMMLUNG = {"measurements/index.html", "notes/index.html", "tools/index.html",
            "data/index.html", "deutsch/index.html"}

LD_TYPEN = {"TechArticle", "Article", "HowTo", "WebPage", "CollectionPage",
            "ItemList"}


def meta(s, name):
    m = re.search(r'<meta name="%s" content="([^"]*)"' % re.escape(name), s)
    return m.group(1) if m else None


def jsonld_bloecke(s):
    return re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                      s, re.S)


def jsonld_keywords(s):
    for roh in jsonld_bloecke(s):
        try:
            d = json.loads(roh)
        except ValueError:
            continue
        k = d.get("keywords")
        if isinstance(k, list):
            k = ", ".join(k)
        if k:
            return k
    return None


def schlagworte(pfad, s):
    """Die kuratierte Karte schlaegt JSON-LD: mehrere Seiten trugen kopierte
    Fremd-keywords ("Firefox for Android, AMO API" auf einer Crawler-Notiz).
    Ohne Karten-Eintrag gelten die vorhandenen JSON-LD-keywords."""
    return KEYWORDS.get(pfad) or jsonld_keywords(s)


def keywords_meta(s, kw):
    if not kw:
        return s, False
    alt = re.search(r'<meta name="keywords" content="([^"]*)"', s)
    if alt:
        if alt.group(1) == kw:
            return s, False
        return s[:alt.start()] + ('<meta name="keywords" content="%s">' % kw) + s[alt.end():], True
    ein = '<meta name="keywords" content="%s">' % kw
    desc = re.search(r'<meta name="description"[^>]*>', s)
    if desc:
        return s[:desc.end()] + "\n" + ein + s[desc.end():], True
    return s.replace("</head>", ein + "\n</head>", 1), True


def og_ergaenzen(s, pfad):
    if 'property="og:title"' in s:
        return s, False
    titel = re.search(r"<title>(.*?)</title>", s)
    desc = meta(s, "description")
    kanon = re.search(r'<link rel="canonical" href="([^"]*)"', s)
    if not (titel and desc and kanon):
        return s, False
    zeilen = [
        '<meta property="og:type" content="website">',
        '<meta property="og:title" content="%s">' % titel.group(1),
        '<meta property="og:description" content="%s">' % desc,
        '<meta property="og:url" content="%s">' % kanon.group(1),
        '<meta name="twitter:card" content="summary">',
    ]
    block = "\n".join(zeilen)
    robo = re.search(r'<meta name="robots"[^>]*>', s)
    if robo:
        return s[:robo.end()] + "\n" + block + s[robo.end():], True
    return s.replace("</head>", block + "\n</head>", 1), True


def robots_sichern(s):
    if '<meta name="robots"' in s:
        return s, False
    ein = '<meta name="robots" content="index, follow">'
    desc = re.search(r'<meta name="description"[^>]*>', s)
    if desc:
        return s[:desc.end()] + "\n" + ein + s[desc.end():], True
    return s, False


def jsonld_neu(pfad, s, kw):
    titel = re.search(r"<title>(.*?)</title>", s)
    desc = meta(s, "description")
    kanon = re.search(r'<link rel="canonical" href="([^"]*)"', s)
    if not (titel and desc and kanon):
        return None
    d = {
        "@context": "https://schema.org",
        "@type": "CollectionPage" if pfad in SAMMLUNG else "WebPage",
        "name": titel.group(1).replace("&amp;", "&"),
        "description": desc,
        "url": kanon.group(1),
        "inLanguage": "de" if pfad in DEUTSCH else "en",
        "isPartOf": {"@type": "WebSite", "name": "Proving Lab",
                     "url": "https://provinglab.dev/"},
    }
    if kw:
        d["keywords"] = kw
    return d


def jsonld_ergaenzen(s, pfad, kw):
    """Bestehende Bloecke um keywords ergaenzen; fehlt JSON-LD ganz, ein
    WebPage-/CollectionPage-Block dazu."""
    bloecke = jsonld_bloecke(s)
    if not bloecke:
        d = jsonld_neu(pfad, s, kw)
        if not d:
            return s, False
        ein = ('<script type="application/ld+json">\n'
               + json.dumps(d, ensure_ascii=False, indent=2)
               + "\n</script>\n</head>")
        return s.replace("</head>", ein, 1), True

    geaendert = False
    karte = KEYWORDS.get(pfad)

    def ersetze(m):
        nonlocal geaendert
        try:
            d = json.loads(m.group(1))
        except ValueError:
            return m.group(0)
        # Dataset-Bloecke beschreiben den Datensatz, nicht die Seite — die
        # gehoeren zu build-dataset-jsonld.py, nicht hierher.
        if d.get("@type") in LD_TYPEN and karte:
            k = d.get("keywords")
            if isinstance(k, list):
                k = ", ".join(k)
            if k != karte:
                d["keywords"] = karte
                geaendert = True
                return ('<script type="application/ld+json">\n'
                        + json.dumps(d, ensure_ascii=False, indent=2)
                        + "\n</script>")
        return m.group(0)

    neu = re.sub(r'<script type="application/ld\+json">(.*?)</script>',
                 ersetze, s, flags=re.S)
    return neu, geaendert


def main():
    seiten = sorted(DOCS.rglob("*.html"))
    offen = geaendert = 0
    for datei in seiten:
        pfad = str(datei.relative_to(DOCS))
        s0 = s = datei.read_text(encoding="utf-8")
        if 'http-equiv="refresh"' in s or datei.name == "404.html":
            continue
        kw = schlagworte(pfad, s)
        s, c1 = keywords_meta(s, kw)
        s, c2 = robots_sichern(s)
        s, c3 = og_ergaenzen(s, pfad)
        s, c4 = jsonld_ergaenzen(s, pfad, kw)
        if s != s0:
            if CHECK:
                offen += 1
                print(f"offen: {pfad}")
            else:
                datei.write_text(s, encoding="utf-8")
                geaendert += 1
                teile = [t for t, c in (("keywords", c1), ("robots", c2),
                                        ("og", c3), ("jsonld", c4)) if c]
                print(f"  {pfad}: {', '.join(teile)}")
    if CHECK:
        print(f"\n{offen} von {len(seiten)} Seiten noch offen.")
        sys.exit(1 if offen else 0)
    print(f"\n{geaendert} von {len(seiten)} Seiten geaendert.")


if __name__ == "__main__":
    main()
