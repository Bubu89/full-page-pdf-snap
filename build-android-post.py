#!/usr/bin/env python3
"""build-android-post.py — erzeugt den Beitrag zur Android-Messung.

Kopf und Fuss stammen aus einer bestehenden Messungsseite, damit Navigation,
Stil und die gemeinsamen Meta-Angaben nicht auseinanderlaufen. Nur die
seitenspezifischen Angaben werden ersetzt.
"""
import json
import re
from pathlib import Path

HIER = Path(__file__).resolve().parent
DOCS = HIER / "docs"
VORLAGE = DOCS / "measurements" / "print-to-pdf-vs-screenshot" / "index.html"
ZIEL = DOCS / "measurements" / "android-capture-extensions"
DATEN = json.load(open(HIER.parent / "daten_android.json")) if False else None

SLUG = "android-capture-extensions"
URL = f"https://provinglab.dev/measurements/{SLUG}/"
TITEL = "Which page-saving extensions actually run on Firefox for Android?"
BESCHREIBUNG = (
    "248 Firefox extensions for saving or capturing a page, checked against the "
    "add-ons API on 2 August 2026. 60 declare Android support — including "
    "SingleFile with 85,724 users. Declaration is not function, and that "
    "distinction is where most claims fall apart."
)


def kopf_und_fuss():
    s = VORLAGE.read_text(encoding="utf-8")
    i = s.index('<div class="wrap">')
    j = s.index("<footer")
    return s[:i], s[j:]


def anpassen(kopf, daten):
    """Ersetzt die seitenspezifischen Angaben im uebernommenen Kopf."""
    k = kopf
    k = re.sub(r"<title>.*?</title>", f"<title>{TITEL} — Proving Lab</title>", k, flags=re.S)
    k = re.sub(r'(<meta name="description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)
    k = re.sub(r'(<link rel="canonical" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<link rel="alternate" hreflang="[^"]*" href=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:url" content=")[^"]*(")', rf"\g<1>{URL}\g<2>", k)
    k = re.sub(r'(<meta property="og:title" content=")[^"]*(")', rf"\g<1>{TITEL}\g<2>", k)
    k = re.sub(r'(<meta property="og:description" content=")[^"]*(")',
               lambda m: m.group(1) + BESCHREIBUNG + m.group(2), k)

    # JSON-LD ersetzen: TechArticle + Dataset, wie auf den anderen Messungsseiten
    ld = {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": TITEL,
        "description": BESCHREIBUNG,
        "datePublished": "2026-08-02",
        "dateModified": "2026-08-02",
        "inLanguage": "en",
        "url": URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "about": {
            "@type": "Dataset",
            "name": "Firefox page-saving extensions declaring Android support, 2026-08-02",
            "description": (
                f"{daten['searched']} extensions retrieved from the addons.mozilla.org API "
                f"across eight search terms; {daten['declaring_android']} declare Android "
                "compatibility in their current version."
            ),
            "license": "https://creativecommons.org/licenses/by/4.0/",
            "distribution": [{
                "@type": "DataDownload",
                "encodingFormat": "application/json",
                "contentUrl": "https://provinglab.dev/data/2026-08-02-android-capture-extensions.json",
            }],
        },
    }
    # Als Funktion ersetzen: json.dumps erzeugt \u-Sequenzen, die re.sub in einem
    # String-Ersatz als Rueckverweis lesen wuerde.
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>',
               lambda _: neu, k, count=1, flags=re.S)
    return k


def tabelle(eintraege, n=15):
    zeilen = []
    for e in eintraege[:n]:
        bew = f"{e['rating']:.1f} ({e['reviews']})" if e["reviews"] else "—"
        zeilen.append(
            f'      <tr><td><a href="{e["url"]}" rel="nofollow">{e["name"]}</a></td>'
            f'<td class="num">{e["users"]:,}</td><td class="num">{bew}</td>'
            f'<td class="num">{e["android_min"] or "—"}</td></tr>'
        )
    return "\n".join(zeilen)


def inhalt(daten):
    relevant = [e for e in daten["extensions"] if any(
        w in e["name"].lower() for w in
        ("pdf", "save", "capture", "screenshot", "print", "page", "scrap", "archive", "single")
    )]
    summe = sum(e["users"] for e in relevant)
    return f"""<div class="wrap">

<header>
  <h1>{TITEL}</h1>
  <p class="standfirst">
    Firefox for Android has supported extensions since 2023, and that is the one thing
    Chrome for Android still cannot do at all. So the interesting question is not whether
    extensions run there — it is how many of the ones you would actually reach for do.
    We checked {daten["searched"]} of them.
  </p>
  <p class="meta">Retrieved {daten["retrieved"]} · addons.mozilla.org API v5 ·
    <a href="/data/2026-08-02-android-capture-extensions.json">raw data</a></p>
</header>

<h2>What was measured</h2>
<p>
  Eight search terms were run against the add-ons search API — <em>full page screenshot</em>,
  <em>save page as pdf</em>, <em>webpage to pdf</em>, <em>screenshot pdf</em>,
  <em>capture page</em>, <em>print to pdf</em>, <em>save webpage</em>, <em>page capture</em> —
  two result pages each, duplicates merged. An extension counts as declaring Android support
  when the current version lists an <code>android</code> entry in its compatibility data.
</p>

<h2>Result</h2>
<p>
  Of {daten["searched"]} extensions, <strong>{daten["declaring_android"]} declare Android
  support</strong>. Their combined user base is roughly {sum(e["users"] for e in daten["extensions"]):,}
  daily users, but that number is dominated by a handful of large ones — the median is
  {sorted(e["users"] for e in daten["extensions"])[len(daten["extensions"]) // 2]} users.
</p>

<table>
  <caption>The fifteen most-used extensions declaring Android support</caption>
  <thead>
    <tr><th scope="col">Extension</th><th class="num">Daily users</th><th class="num">Rating</th>
        <th class="num">Min. Android version</th></tr>
  </thead>
  <tbody>
{tabelle(daten["extensions"])}
  </tbody>
</table>

<h2>Declaration is not function</h2>
<p>
  This is the part that matters, and it is why the number above should not be read as a
  ranking. A manifest entry means the extension <em>may be installed</em> on Firefox for
  Android. It says nothing about whether the feature works there.
</p>
<p>
  Capture extensions are especially exposed to this. A full-page capture needs to scroll the
  document, wait for lazy-loaded images, stitch segments and hand the result to a file
  picker — and every one of those steps behaves differently on Android. The
  <code>min. Android version</code> column hints at the split: entries at 48 or 57 predate
  the current extension platform on Android entirely and were carried over, while 113 and
  above were set after Firefox reopened the platform in 2023.
</p>
<p>
  <strong>We did not install or test any of these on a device.</strong> Verifying sixty
  extensions on real hardware is a different piece of work, and until someone does it,
  nobody — including us — can claim which of them actually deliver a usable file on a phone.
</p>

<h2>What this means for the claim "one of the few"</h2>
<p>
  It does not hold. {len(relevant)} of the extensions found here are page-saving or capture
  tools with Android in their manifest, together around {summe:,} daily users. SingleFile
  alone has 85,724. Our own extension, Full Page PDF Snap, is one entry among them, and its
  three daily users put it at the very bottom of that list.
</p>
<p>
  We had that claim in our own store listing until this measurement. It is being removed.
  The accurate statement is narrower and still useful: the extension <em>does</em> run on
  Firefox for Android, and that puts it in a minority of roughly a quarter of the tools
  people search for when they want to save a page — not in a category of its own.
</p>

<h2>Why Chrome does not appear here</h2>
<p>
  Chrome for Android cannot install extensions at all. That is not a gap in this
  measurement; it is the reason the measurement only covers Firefox. If you want a page
  saved as a file on a phone, with an extension, Firefox is currently the only mainstream
  browser where the question even arises.
</p>

<h2>Questions</h2>
<h3>Does a higher minimum Android version mean better support?</h3>
<p>
  It means the entry was set recently, nothing more. An extension declaring 113 or 120 was
  updated after Firefox reopened the Android platform, so its author at least saw the
  current environment. An entry of 48 was written for a platform that no longer exists in
  that form.
</p>
<h3>Which of these actually work?</h3>
<p>
  Unknown, and we will not guess. If you test any of them on a device and want the result
  published here with your method, the
  <a href="https://github.com/Bubu89/full-page-pdf-snap/issues">issue tracker</a> is open.
</p>

"""


def main():
    daten = json.load(open(HIER / "docs" / "data" / "2026-08-02-android-capture-extensions.json"))
    kopf, fuss = kopf_und_fuss()
    kopf = anpassen(kopf, daten)
    fuss = re.sub(
        r"<footer>.*?</footer>",
        '<footer>\n      Method: eight search terms against the addons.mozilla.org API v5, two result\n'
        '      pages each, duplicates merged by slug; Android support read from\n'
        '      <code>current_version.compatibility</code>. Retrieved 2 August 2026. No extension was\n'
        '      installed or tested on a device — declaration is not function. User counts are AMO\n'
        '      daily averages and fluctuate. The author develops one of the extensions listed.\n'
        '      <br><br>\n      <a href="../../">← Proving Lab</a>\n    </footer>',
        fuss, count=1, flags=re.S)
    ZIEL.mkdir(parents=True, exist_ok=True)
    (ZIEL / "index.html").write_text(kopf + inhalt(daten) + fuss, encoding="utf-8")
    print(f"  geschrieben: {(ZIEL / 'index.html').relative_to(DOCS)} "
          f"({len((ZIEL / 'index.html').read_text(encoding='utf-8'))} Zeichen)")


if __name__ == "__main__":
    main()
