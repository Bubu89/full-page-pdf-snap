#!/usr/bin/env python3
"""Prueft die gesamte Website auf die Punkte, die rechtlich teuer werden.

Kein Ersatz fuer Rechtsberatung. Das Skript nimmt dem Menschen die stumpfe
Arbeit ab: Es findet die Formulierungen, die erfahrungsgemaess Aerger machen,
und meldet fehlende Pflichtbestandteile. Was es meldet, muss jemand lesen.

Grundlage ist der Skill `publikation-rechtssicher` mit seinen fuenf Pruefungen.
Zusaetzlich geprueft wird die maschinenlesbare Ebene (.well-known, MCP,
llms.txt), weil dort Zusagen stehen, die genauso gelten wie im Fliesstext.

    python3 rechtscheck.py             # lokal
    python3 rechtscheck.py --live      # zusaetzlich die veroeffentlichte Seite

Exitcode 1, sobald ein Punkt der Stufe FEHLER offen ist.
"""
import argparse
import hashlib
import json
import re
import sys
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parent
DOCS = REPO / "docs"
BASIS = "https://provinglab.dev"

# ------------------------------------------------------------------ Muster
#
# Jedes Muster hat einen Gegentest: eine Formulierung, die NICHT anschlagen
# darf. Ohne den wandert ein zu gieriges Muster unbemerkt in den Bestand und
# erzeugt bei jedem Lauf dieselben Fehlalarme, bis niemand mehr hinsieht.

def wort(*w):
    return re.compile(r"\b(" + "|".join(w) + r")\b", re.I)


BEHAUPTUNGEN = [
    # (Kennung, Muster, Stufe, Begruendung, darf-nicht-treffen)
    ("absicht-fremd",
     re.compile(r"\b(in order to (collect|harvest|monetise|monetize)"
                r"|the (developer|vendor|provider)s? (want|intend)"
                r"|um .{0,30}(Daten|Nutzer\w*) (zu sammeln|abzugreifen)"
                r"|damit sie .{0,20}(sammeln|verkaufen))\b", re.I),
     "FEHLER",
     "Aussage ueber die Absicht eines Dritten — beweispflichtig und praktisch nie beweisbar.",
     "when they want to save a page, the manifest declares <all_urls>."),

    ("herabsetzung",
     wort("Datenkrake", "dubios", "dreist", "nachlaessig", "nachlässig", "shady",
          "sloppy", "greedy", "predatory", "unseriös", "unserioes"),
     "FEHLER",
     "Herabsetzende Bewertung eines Mitbewerbers — § 2a UWG (AT) / § 6 UWG (DE).",
     "The extension declares broad host permissions."),

    ("pauschal-unsicher",
     re.compile(r"\b(is|are|ist|sind)\s+(unsicher|insecure|unsafe|dangerous|gefaehrlich|gefährlich)\b", re.I),
     "WARNUNG",
     "Werturteil mit Tatsachenkern ueber ein fremdes Produkt. Deklaration zeigen statt bewerten.",
     "A broad permission is not proof of misuse."),

    ("beweiskraft",
     re.compile(r"\b(gerichtsfest|court[- ]proof|legally binding proof|rechtssicherer Beweis"
                r"|admissible as evidence)\b", re.I),
     "FEHLER",
     "Zusicherung von Beweiskraft. Ein Bildschirmabbild leistet das nicht.",
     "It is not a qualified electronic document."),

    ("superlativ",
     # "the only …" bewusst NICHT hier: das ist fast immer eine belegbare
     # Feststellung ("the only browser with extensions on Android"), kein
     # Werbesuperlativ. Vier Fehlalarme, kein einziger echter Fall.
     re.compile(r"\b(the (best|safest|fastest|most secure) \w+"
                r"|der (beste|sicherste|schnellste)|die (beste|sicherste|schnellste)"
                r"|das (beste|sicherste|schnellste))\b", re.I),
     "WARNUNG",
     "Werbesuperlativ ohne Beleg. Entweder messen oder als Meinung kennzeichnen.",
     "the only mainstream browser where the question even arises"),

    ("garantie",
     re.compile(r"(?<!no )(?<!not )(?<!kein )(?<!keine )(?<!nicht )"
                r"\b(guarantees?|garantiert|100\s?% (sicher|secure|safe))\b", re.I),
     "WARNUNG",
     "Zusicherung, die im Streitfall eingehalten werden muss.",
     "measurements are measurements, not guarantees, and no guarantee is given"),
]

# Auf Seiten, die Daten ueber fremde Produkte oder Dienste zeigen, muss ein
# Abrufdatum stehen — sonst wird aus einer richtigen Angabe stillschweigend
# eine falsche.
# Nur Namen FREMDER Angebote. "manifest" und "permissions" standen hier zuerst
# mit drin und trafen jede Seite, die die eigenen Berechtigungen erklaert —
# neun Fehlalarme, die den Blick auf die echten Faelle verstellt haben.
# "Save as PDF" stand hier zuerst mit drin. Es ist zwar ein Erweiterungsname,
# aber vor allem eine alltaegliche Formulierung — der Alarm traf einen Satz
# ueber die eingebaute Funktion von Firefox. Produktnamen muessen eindeutig
# sein, sonst misst der Pruefer Sprache statt Sachverhalt.
FREMDDATEN = wort("PDFCrowd", "FireShot", "Awesome Screenshot", "Nimbus",
                  "Print Edit WE", r"Perma\.cc", "Internet Archive", "Wayback",
                  "PDF Mage")
ABRUFDATUM = re.compile(r"(retrieved|abgerufen|Stand|as of|as retrieved)\s*(on|am)?\s*\d|\d{4}-\d{2}-\d{2}", re.I)

# Rechtsaussagen brauchen den Ausschluss.
RECHTSTHEMA = wort("copyright", "Urheberrecht", "UrhG", "UWG", "licence", "Lizenz",
                   "evidence", "Beweis", "Schranke", "exceptions for private")
# Das Muster fasste zuerst nur "not legal advice" und "keine Rechtsberatung"
# woertlich — und meldete deshalb eine Seite, auf der "nothing on this page is
# legal advice" stand. Ein Pruefer, der die richtige Formulierung nicht erkennt,
# erzeugt Arbeit statt Sicherheit.
RECHTSAUSSCHLUSS = re.compile(
    r"(no(thing|t)\b[^.]{0,140}\b(legal|professional) advice"
    r"|(legal|professional) advice\b[^.]{0,40}\bnot\b"
    r"|(keine|nichts|kein)\b[^.]{0,140}\b(Rechtsberatung|fachliche Beratung)"
    # Ein Verweis auf den Haftungsausschluss erfuellt die Anforderung ebenso:
    # dort steht der Ausschluss vollstaendig, und ihn auf jeder Seite zu
    # wiederholen macht ihn nicht wirksamer, nur laenger. Am 3. August 2026
    # meldete der Pruefer eine Seite, die dreimal „licence" im Sinne von
    # Zugangsberechtigung schrieb und den Ausschluss bereits verlinkte.
    r"|href=\"[^\"]*disclaimer/?\""
    r"|href=\"[^\"]*haftungsausschluss/?\")", re.I)

EIGENPRODUKT = re.compile(r"Full Page PDF Snap", re.I)
OFFENLEGUNG = re.compile(r"(author develops|Der Autor entwickelt|disclos|Offenlegung|"
                         r"appears in (some of )?the(se)? measurements)", re.I)
KORREKTURWEG = re.compile(r"(github\.com/[\w-]+/[\w-]+/issues|Korrekturen|Corrections)", re.I)

# --- Erweiterung 03.08.2026: Risiken, die durch die Agenten-Anbindung entstanden ---

# Zusagen ueber Verfuegbarkeit, die man nicht halten will und die zum
# uebermaessigen Gebrauch einladen. "Kein Limit" ist eine Aussage ueber die
# Zukunft, keine Beschreibung — und ein offener Abrufdienst ohne Grenze laesst
# sich als Verstaerker gegen Dritte verwenden, mit unserem Kennzeichen im Log.
UNBEGRENZT = re.compile(
    r"(no rate limit|unlimited|kein (rate.?)?limit|ohne (jede )?(begrenzung|limit)"
    r"|as (much|often) as you (want|like)|beliebig oft)", re.I)

# Anleitungen, die das Umgehen fremder Schutzmassnahmen empfehlen. Der Unterschied
# zwischen "so kommst du an der Sperre vorbei" und "das funktioniert nicht und
# gehoert sich nicht" ist der ganze Unterschied.
UMGEHUNG = re.compile(
    r"(bypass|umgeh\w+|circumvent|get (a)?round the (block|wall|paywall)"
    r"|spoof (the )?user.?agent|pretend to be a browser)", re.I)
UMGEHUNG_ERLAUBT = re.compile(
    r"(do not|don't|never|nicht|statt dessen|stattdessen|does not work|funktioniert nicht"
    r"|is not something|keine? (route|weg))", re.I)

# Verweise auf fremde Projekte ohne Distanzierung. Wer Dritt-Software empfiehlt,
# ohne sie geprueft zu haben, sollte das sagen — sonst liest es sich als Zusage.
FREMDPROJEKT = re.compile(r"github\.com/(?!Bubu89/)[\w.-]+/[\w.-]+", re.I)
DISTANZIERUNG = re.compile(
    r"(not (an )?endorse|no endorsement|not audited|nicht geprueft|nicht gepr\u00fcft"
    r"|keine empfehlung|check .{0,20}yourself|ungeprueft)", re.I)


# --- Erweiterung 04.08.2026: Risiken aus der automatisierten Installation ---
#
# An einem Tag entstanden drei Beitraege ueber Wege, eine Erweiterung ohne
# Klick zu installieren. Jeder davon konnte auf drei Arten kippen, und keine
# davon faengt eine der bisherigen Regeln. Sie stehen hier, damit sie nicht
# von der Aufmerksamkeit dessen abhaengen, der gerade schreibt.

# 1. Wer Installationszahlen erwaehnt, muss die Grenze mitnennen.
#    Beide Stores kuendigen dem ENTWICKLER, wenn Zahlen aufgeblasen werden.
#    Ein Text, der die Zahl erwaehnt und das verschweigt, liest sich als
#    Anleitung dazu — auch wenn er es nicht meint.
# Erste Fassung traf jede Nennung von Nutzerzahlen — auch die Messung, die
# fremde Erweiterungen mit ihren Nutzerzahlen auflistet. Vier Fehlalarme, kein
# echter Fall. Gemeint ist nur der Zusammenhang „eigene Installation bewegt die
# Zahl"; das Berichten fremder Zahlen ist eine Angabe, kein Risiko.
ZAEHLUNG = re.compile(
    r"((counts?|counted|zaehlt|zaehlen) (as an? )?(store |in the store'?s? )?"
    r"(user|install|Nutzer)"
    r"|counts? in the store|zaehlt im Store"
    r"|(inflat|manipulat|aufblas)\w*[^.]{0,40}(count|number|Zahl)"
    r"|Nutzerstatistik des Stores)", re.I)
ZAEHLUNG_GRENZE = re.compile(
    r"(terminat\w+ the (developer|publisher)|Entwicklerkonto|developer account"
    r"|inflat\w+ (a |the )?(public )?(number|count|install)"
    r"|aufblas\w+|manipulat\w+|gegen die (Store-)?(Regeln|Bedingungen)"
    r"|forbid\w*|verboten|not something to (build|do))", re.I)

# 2. Wer ueber Installation auf fremden Geraeten schreibt, muss die
#    Einwilligung benennen. Der Mechanismus kennt sie nicht — die Marker-Datei
#    weiss nicht, wer sie geschrieben hat. Genau deshalb gehoert sie in den Text.
# Erste Fassung traf jedes „the user's browser" — auch Saetze darueber, dass
# ein Agent IM Browser des Nutzers arbeitet, was mit Installation nichts zu tun
# hat. Gemeint ist nur: etwas AUF einem fremden Geraet einrichten.
FREMDGERAET = re.compile(
    r"((install\w*|einricht\w*|aufspiel\w*|ausroll\w*)[^.]{0,60}"
    r"(someone else'?s|the user'?s|a user'?s|fremde[nrs]?|eines? (anderen|Dritten))"
    r"[^.]{0,20}(browser|machine|computer|device|Rechner|Geraet|Profil)"
    r"|(someone else'?s|fremde[nrs]?) (browser|machine|Rechner|Geraet)"
    r"[^.]{0,40}(install|einricht))", re.I)
EINWILLIGUNG = re.compile(
    r"(consent|permission of the (user|person)|asked (for it|to)|on (their|the "
    r"user'?s) instruction|Einwilligung|Zustimmung|beauftragt|darum gebeten)", re.I)

# 3. Eine Schlussfolgerung darf nicht wie eine Messung aussehen.
#    "Zaehlt vermutlich" ist keine Zahl. Wo so etwas steht, muss danebenstehen,
#    dass es ungemessen ist — sonst wandert es als Befund weiter.
VERMUTUNG = re.compile(
    r"(probably (counts?|works?|registers?)|likely (counts?|registers?)"
    r"|should count|duerfte zaehlen|vermutlich (zaehlt|funktioniert)"
    r"|wahrscheinlich (zaehlt|greift))", re.I)
VERMUTUNG_MARKIERT = re.compile(
    r"(not measured|ungemessen|nicht gemessen|inference|Schlussfolgerung"
    r"|keine Messung|is an? (inference|assumption)|unbelegt)", re.I)

# Aussagen ueber fremde Anbieter, die Absichten unterstellen statt Beobachtungen
# zu berichten. Beweispflichtig und praktisch nie beweisbar.
# "they want to" allein ist zu weit — es trifft Saetze ueber Nutzer ("they want
# to save a page"). Nur Formulierungen, die einem ANBIETER ein Motiv zuschreiben.
ABSICHT = re.compile(
    r"(deliberately (blocks?|hides?|withholds?)"
    r"|(publishers?|vendors?|they) (want|try|intend) to (block|stop|prevent|hide|keep)"
    r"|in order to (prevent|stop) (us|you|readers|agents)"
    r"|absichtlich (sperr|blockier|verberg)"
    r"|um zu verhindern, dass (wir|man|Leser))", re.I)



def text_aus(html):
    """Sichtbarer Text: Skripte, Stile und Auszeichnung raus."""
    h = re.sub(r"<script.*?</script>", " ", html, flags=re.S | re.I)
    h = re.sub(r"<style.*?</style>", " ", h, flags=re.S | re.I)
    h = re.sub(r"<!--.*?-->", " ", h, flags=re.S)
    h = re.sub(r"<[^>]+>", " ", h)
    h = (h.replace("&amp;", "&").replace("&nbsp;", " ").replace("&mdash;", "—")
          .replace("&#8222;", '"').replace("&#8220;", '"'))
    return re.sub(r"\s+", " ", h)


def umfeld(text, treffer, weite=90):
    a = max(0, treffer.start() - weite)
    return "…" + text[a:treffer.end() + weite].strip() + "…"


def ist_weiterleitung(html):
    """Eine Seite, die nur weiterleitet, traegt keinen eigenen Inhalt."""
    return bool(re.search(r'http-equiv="refresh"|window\.location\s*=', html, re.I))


def pruefe_seite(pfad, html, befunde):
    rel = str(pfad.relative_to(DOCS))
    if ist_weiterleitung(html):
        return                      # nichts zu belegen, nichts zu korrigieren
    txt = text_aus(html)

    for kennung, muster, stufe, grund, gegentest in BEHAUPTUNGEN:
        for t in muster.finditer(txt):
            befunde.append((stufe, rel, kennung, grund, umfeld(txt, t)))

    # Fremddaten ohne Abrufdatum
    if FREMDDATEN.search(txt) and not ABRUFDATUM.search(txt):
        befunde.append(("WARNUNG", rel, "kein-abrufdatum",
                        "Seite nennt fremde Produkte oder Dienste, aber kein Abrufdatum.", ""))

    # Rechtsthema ohne Ausschluss
    if RECHTSTHEMA.search(txt) and not RECHTSAUSSCHLUSS.search(txt) \
            and not RECHTSAUSSCHLUSS.search(html):
        n = len(RECHTSTHEMA.findall(txt))
        if n >= 3:                       # einzelne Nennung von "Lizenz" reicht nicht
            befunde.append(("WARNUNG", rel, "kein-rechtsausschluss",
                            f"Seite behandelt Rechtsthemen ({n} Fundstellen), "
                            "nennt aber nicht, dass sie keine Rechtsberatung ist.", ""))

    # Eigenes Produkt genannt -> Offenlegung noetig
    if EIGENPRODUKT.search(txt) and not OFFENLEGUNG.search(txt):
        if rel not in ("tools/full-page-pdf-snap/index.html",):   # dort ist es das Thema
            befunde.append(("FEHLER", rel, "keine-offenlegung",
                            "Eigenes Produkt genannt, aber keine Offenlegung der Beteiligung.", ""))

    # Haftungshinweis muss von jeder Seite aus erreichbar sein — er nuetzt
    # nichts, wenn er nur auf einer Unterseite steht, die niemand ansteuert.
    if "disclaimer" not in html and rel != "disclaimer/index.html":
        befunde.append(("FEHLER", rel, "kein-haftungshinweis",
                        "Kein Verweis auf die Haftungs- und Hinweisseite.", ""))

    # Korrekturweg
    if not KORREKTURWEG.search(html) and rel not in ("404.html",):
        befunde.append(("WARNUNG", rel, "kein-korrekturweg",
                        "Kein Weg angegeben, wie eine Korrektur gemeldet werden kann.", ""))

    # --- Erweiterung 03.08.2026 ---

    # Unbegrenzte Nutzung zusagen
    for t in UNBEGRENZT.finditer(txt):
        befunde.append(("FEHLER", rel, "zusage-ohne-grenze",
                        "Sagt unbegrenzte Nutzung zu. Das laedt zum Missbrauch eines offenen "
                        "Abrufdienstes ein und ist eine Zusage ueber die Zukunft.",
                        umfeld(txt, t)))
        break


    # --- 04.08.2026: die drei Faelle aus der automatisierten Installation ---

    # Installationszahlen erwaehnt, Grenze verschwiegen. Ganze Seite als
    # Umfeld, nicht der Absatz: die Grenze darf am Ende stehen, sie muss nur
    # ueberhaupt dastehen.
    if ZAEHLUNG.search(txt) and not ZAEHLUNG_GRENZE.search(txt):
        t = ZAEHLUNG.search(txt)
        befunde.append(("FEHLER", rel, "zaehlung-ohne-grenze",
                        "Spricht ueber Installations- oder Nutzerzahlen, ohne zu "
                        "nennen, dass ihr Aufblasen die Store-Bedingungen verletzt "
                        "und das Entwicklerkonto kostet. Ohne diesen Satz liest "
                        "sich der Text als Anleitung dazu.", umfeld(txt, t)))

    # Installation auf fremdem Geraet ohne ein Wort zur Einwilligung.
    if FREMDGERAET.search(txt) and re.search(r"install", txt, re.I) \
            and not EINWILLIGUNG.search(txt):
        t = FREMDGERAET.search(txt)
        befunde.append(("FEHLER", rel, "fremdgeraet-ohne-einwilligung",
                        "Beschreibt Installation auf einem fremden Geraet, ohne die "
                        "Einwilligung zu benennen. Der Mechanismus kennt sie nicht — "
                        "deshalb gehoert sie in den Text.", umfeld(txt, t)))

    # Vermutung, die wie ein Befund aussieht.
    for t in VERMUTUNG.finditer(txt):
        nahbereich = txt[max(0, t.start() - 300):t.end() + 300]
        if not VERMUTUNG_MARKIERT.search(nahbereich):
            befunde.append(("FEHLER", rel, "vermutung-als-befund",
                            "Eine Annahme steht da wie eine Messung. Im Umfeld fehlt, "
                            "dass sie ungemessen ist — so wandert sie als Zahl weiter.",
                            umfeld(txt, t)))
            break

    # Umgehungsanleitung ohne Abgrenzung im selben Absatz
    for t in UMGEHUNG.finditer(txt):
        nahbereich = txt[max(0, t.start() - 260):t.end() + 260]
        if not UMGEHUNG_ERLAUBT.search(nahbereich):
            befunde.append(("FEHLER", rel, "umgehungsanleitung",
                            "Nennt das Umgehen einer Schutzmassnahme, ohne im Umfeld "
                            "klarzustellen, dass es unterbleibt.", umfeld(txt, t)))
            break

    # Fremdprojekte ohne Distanzierung
    if FREMDPROJEKT.search(html) and not DISTANZIERUNG.search(txt):
        befunde.append(("WARNUNG", rel, "fremdprojekt-ohne-distanz",
                        "Verweist auf fremde Software, ohne zu sagen, dass sie hier weder "
                        "geprueft noch empfohlen wird.", ""))

    # Absichtsunterstellung gegenueber Dritten
    for t in ABSICHT.finditer(txt):
        befunde.append(("FEHLER", rel, "absicht-unterstellt",
                        "Behauptet eine Absicht eines Dritten. Beweispflichtig und von "
                        "aussen nicht belegbar — Beobachtung berichten statt Motiv.",
                        umfeld(txt, t)))
        break

    # Interne Ziele
    for m in re.finditer(r'href="(?!https?:|mailto:|#)([^"]+)"', html):
        ziel = m.group(1).split("#")[0].split("?")[0]
        if not ziel:
            continue
        # Ein fuehrender Schraegstrich meint die Wurzel der Seite, nicht den
        # Ordner der Datei. Ohne diese Unterscheidung meldet der Pruefer jeden
        # absoluten Verweis als tot — 60 Fehlalarme im ersten Lauf.
        p = (DOCS / ziel.lstrip("/")).resolve() if ziel.startswith("/") \
            else (pfad.parent / ziel).resolve()
        if p.is_dir():
            p = p / "index.html"
        if not p.exists() and not str(p).startswith(str(DOCS / ".well-known")):
            befunde.append(("FEHLER", rel, "toter-link",
                            f"Verweist auf {ziel}, existiert nicht.", ""))

    # Anker
    ids = set(re.findall(r'id="([^"]+)"', html))
    for m in re.finditer(r'href="#([^"]+)"', html):
        if m.group(1) not in ids:
            befunde.append(("FEHLER", rel, "toter-anker",
                            f'Anker #{m.group(1)} hat kein Ziel.', ""))


def pruefe_gegentests(befunde):
    """Kein Muster darf auf seinen eigenen Gegentest anschlagen."""
    for kennung, muster, _s, _g, gegentest in BEHAUPTUNGEN:
        if gegentest and muster.search(gegentest):
            befunde.append(("FEHLER", "rechtscheck.py", "muster-zu-gierig",
                            f"Muster '{kennung}' schlaegt auf eine zulaessige Formulierung an: "
                            f"{gegentest!r}", ""))


TEXTTYPEN = {"Article", "TechArticle", "BlogPosting", "NewsArticle", "FAQPage", "WebSite"}
SOFTWARELIZENZ = re.compile(r"(opensource\.org/licenses|/MIT\b|Apache-2|GPL)", re.I)
INHALTSLIZENZ = re.compile(r"creativecommons\.org", re.I)


def pruefe_lizenzen(befunde):
    """Eine Softwarelizenz deckt Code, keinen Fliesstext.

    Ein Artikel unter MIT ist nicht bloss unsauber, sondern sagt dem Leser
    nichts Verwertbares: MIT regelt Weitergabe und Haftung von Software.
    Umgekehrt gehoert Code nicht unter CC BY. Beides kam hier vor.
    """
    for pfad in sorted(DOCS.rglob("*.html")):
        html = pfad.read_text(encoding="utf-8")
        rel = str(pfad.relative_to(DOCS))
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S):
            try:
                d = json.loads(block)
            except json.JSONDecodeError:
                continue
            typ, lizenz = d.get("@type"), d.get("license", "")
            if not lizenz:
                continue
            if typ in TEXTTYPEN and SOFTWARELIZENZ.search(lizenz):
                befunde.append(("FEHLER", rel, "lizenz-vertauscht",
                                f"{typ} steht unter einer Softwarelizenz ({lizenz}). "
                                "Fuer Texte gehoert eine Inhaltslizenz hin.", ""))
            if typ == "SoftwareApplication" and INHALTSLIZENZ.search(lizenz):
                befunde.append(("WARNUNG", rel, "lizenz-vertauscht",
                                f"Software unter Inhaltslizenz ({lizenz}).", ""))


def pruefe_maschinenebene(befunde):
    """.well-known, llms.txt und Feed sind Zusagen wie jeder andere Text auch."""
    wk = DOCS / ".well-known"

    for datei in [wk / "agent-skills" / "index.json", wk / "api-catalog",
                  wk / "mcp" / "server-card.json", wk / "oauth-protected-resource"]:
        if not datei.exists():
            befunde.append(("WARNUNG", str(datei.relative_to(DOCS)), "fehlt",
                            "In den Seiten verlinkt, aber nicht vorhanden.", ""))
            continue
        try:
            json.loads(datei.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            befunde.append(("FEHLER", str(datei.relative_to(DOCS)), "kein-json",
                            f"Nicht lesbar: {e}", ""))

    # Angekuendigte Skills muessen existieren und zur Pruefsumme passen -
    # eine falsche Pruefsumme ist schlimmer als gar keine.
    idx = wk / "agent-skills" / "index.json"
    if idx.exists():
        d = json.loads(idx.read_text(encoding="utf-8"))
        for s in d.get("skills", []):
            datei = wk / "agent-skills" / s["url"].rsplit("/", 1)[1]
            if not datei.exists():
                befunde.append(("FEHLER", "agent-skills/index.json", "skill-fehlt",
                                f"{s['name']}: Datei fehlt.", ""))
                continue
            if "sha256" in s:
                ist = hashlib.sha256(datei.read_bytes()).hexdigest()
                if ist != s["sha256"]:
                    befunde.append(("FEHLER", "agent-skills/index.json", "pruefsumme",
                                    f"{s['name']}: Pruefsumme weicht ab.", ""))

    # Lizenzangaben: wer CC BY verspricht, muss es auf der Seite auch sagen.
    # schema.json ist kein Datensatz, sondern das Pruefschema der Datensaetze
    # (tools/daten-pruefen.py) — es traegt bewusst kein Lizenzfeld.
    for datei in DOCS.glob("data/*.json"):
        if datei.name == "schema.json":
            continue
        d = json.loads(datei.read_text(encoding="utf-8"))
        if "lizenz" not in d and "license" not in d:
            befunde.append(("WARNUNG", f"data/{datei.name}", "keine-lizenz",
                            "Datensatz ohne Lizenzangabe.", ""))


def pruefe_live(befunde):
    import requests
    ziele = ["/", "/tools/", "/data/", "/notes/", "/measurements/", "/about/",
             "/privacy.html", "/llms.txt", "/feed.xml", "/sitemap.xml", "/robots.txt",
             "/.well-known/agent-skills/index.json", "/.well-known/api-catalog",
             "/.well-known/mcp/server-card.json", "/agent-tools.js"]
    for z in ziele:
        try:
            r = requests.get(BASIS + z, timeout=20)
            if r.status_code != 200:
                befunde.append(("FEHLER", "live", "nicht-erreichbar",
                                f"{z} liefert HTTP {r.status_code}.", ""))
        except Exception as e:
            befunde.append(("FEHLER", "live", "nicht-erreichbar", f"{z}: {e}", ""))

    # Der in der Server-Card zugesagte Endpunkt muss antworten.
    karte = DOCS / ".well-known" / "mcp" / "server-card.json"
    if karte.exists():
        d = json.loads(karte.read_text(encoding="utf-8"))
        endpunkt = d.get("transport", {}).get("endpoint")
        if endpunkt:
            try:
                r = requests.post(endpunkt, timeout=20, json={
                    "jsonrpc": "2.0", "id": 1, "method": "tools/list"})
                if r.status_code != 200 or "result" not in r.json():
                    befunde.append(("FEHLER", "live", "mcp-zusage",
                                    f"Server-Card nennt {endpunkt}, dort antwortet kein MCP-Server.", ""))
                else:
                    zugesagt = {t["name"] for t in d.get("tools", [])}
                    da = {t["name"] for t in r.json()["result"].get("tools", [])}
                    if zugesagt - da:
                        befunde.append(("FEHLER", "live", "mcp-werkzeug-fehlt",
                                        f"Zugesagt, aber nicht vorhanden: {sorted(zugesagt - da)}", ""))
            except Exception as e:
                befunde.append(("FEHLER", "live", "mcp-zusage",
                                f"{endpunkt} nicht erreichbar: {e}", ""))



def pruefe_endpunkt(befunde):
    """Der Worker sagt dieselben Dinge wie die Seiten — und wurde nie geprueft.

    Am 4. August 2026 beschrieb `recommend_settings` einen Eingriff per
    Richtlinie und enthielt **keinen einzigen** rechtlichen Hinweis. Dieselbe
    Luecke haette diese Datei auf jeder HTML-Seite blockiert; sie las den
    Worker nur nicht.

    Geprueft wird **je Block**, nicht ueber die ganze Datei. Der erste Entwurf
    suchte "developer account" irgendwo in 1900 Zeilen, fand es in einem
    anderen Werkzeug und war zufrieden — der Gegentest blieb stumm, obwohl der
    Hinweis an der gepruefen Stelle entfernt war. Ein Muster ohne Kontext
    bestaetigt, was es finden will.
    """
    wk = REPO / "worker" / "mcp.js"
    if not wk.exists():
        return
    t = wk.read_text(encoding="utf-8")

    def block(name):
        """Den Textbereich eines Werkzeugbausteins herausschneiden.

        Die Grenze wird ueber die Klammerbilanz bestimmt, nicht ueber eine
        feste Zeichenzahl. Das vorherige 4000-Zeichen-Fenster meldete am
        4. August einen Hinweis als fehlend, der 4123 Zeichen hinter dem
        Blockanfang stand — ein Fehlalarm, der entstand, weil der Block
        wuchs. Eine Pruefung, deren Ergebnis von der Laenge des geprueften
        Texts abhaengt, misst die Laenge und nicht die Sache.
        """
        # Bausteine stehen als `name: {` ODER `name = {` im Quelltext. Der
        # erste Entwurf kannte nur die erste Form und meldete drei Bausteine
        # als fehlend, die vorhanden waren.
        for trenner in (":", " ="):
            i = t.find(name + trenner)
            if i >= 0:
                break
        else:
            return ""
        start = t.find("{", i)
        if start < 0:
            return t[i:i + 4000]
        tiefe = 0
        for k in range(start, len(t)):
            if t[k] == "{":
                tiefe += 1
            elif t[k] == "}":
                tiefe -= 1
                if tiefe == 0:
                    return t[i:k + 1]
        return t[i:]

    pflichten = [
        ("routeHeadless", "storeCounts",
         "Beschreibt die Installation ohne Klick, ohne zu nennen, dass das "
         "Aufblasen von Installationszahlen das Entwicklerkonto kostet."),
        ("antwort.limits", "consent",
         "recommend_settings beschreibt Eingriffe auf einem Rechner ohne "
         "einen Hinweis auf die Einwilligung."),
        ("antwort.limits", "noLegalAdvice",
         "recommend_settings trifft Aussagen zu Rechtsfragen ohne den Hinweis, "
         "dass es keine Rechtsberatung ist."),
        ("antwort.limits", "disclosure",
         "recommend_settings empfiehlt die eigene Erweiterung ohne Offenlegung."),
    ]
    for baustein, feld, text in pflichten:
        b = block(baustein)
        if not b:
            befunde.append(("WARNUNG", "worker/mcp.js", "endpunkt-baustein-fehlt",
                            f"Baustein {baustein} nicht gefunden — Pruefung "
                            "uebersprungen, nicht bestanden.", ""))
            continue
        if feld not in b:
            befunde.append(("FEHLER", "worker/mcp.js", f"endpunkt-{feld.lower()}",
                            text, ""))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="auch die veroeffentlichte Seite pruefen")
    a = ap.parse_args()

    befunde = []
    pruefe_gegentests(befunde)
    seiten = sorted(DOCS.rglob("*.html"))
    for p in seiten:
        pruefe_seite(p, p.read_text(encoding="utf-8"), befunde)
    pruefe_maschinenebene(befunde)
    pruefe_endpunkt(befunde)
    pruefe_lizenzen(befunde)
    if a.live:
        pruefe_live(befunde)

    fehler = [b for b in befunde if b[0] == "FEHLER"]
    warn = [b for b in befunde if b[0] == "WARNUNG"]

    print(f"Geprueft: {len(seiten)} Seiten"
          f"{' + Live-Abruf' if a.live else ''}\n")
    for stufe, liste in (("FEHLER", fehler), ("WARNUNG", warn)):
        if not liste:
            continue
        print(f"── {stufe} ({len(liste)}) " + "─" * 40)
        for _s, wo, kennung, grund, stelle in liste:
            print(f"  [{kennung}] {wo}")
            print(f"      {grund}")
            if stelle:
                print(f"      {stelle[:200]}")
        print()

    if not befunde:
        print("Keine Beanstandung.")
    else:
        print(f"{len(fehler)} Fehler, {len(warn)} Warnungen.")
    return 1 if fehler else 0


if __name__ == "__main__":
    sys.exit(main())
