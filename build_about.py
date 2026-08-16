#!/usr/bin/env python3
"""Baut docs/about/index.html aus texte_about.py — neun Sprachen.

Gleiches Muster wie build-for-agents.py: Kopf und Fuss aus der bestehenden
Seite, alle Sprachen als data-lang-Bloecke in einer Datei. h1 und lead stehen
IN den Bloechen, damit sie mit der Sprache umschalten; der gemeinsame Fuss
(Disclaimer-/Privacy-Verweis) bleibt ausserhalb. Idempotent: ein zweiter Lauf
erzeugt keinen Unterschied.

    python3 build_about.py
"""
import json
import re
from pathlib import Path

import texte_about as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "about" / "index.html"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)


def block(l):
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    box = "\n".join(f"      <li>{x}</li>" for x in d["box_items"])
    zahlen = "\n".join(f"    <li>{x}</li>" for x in d["fig_items"])
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <h1>{d["h1"]}</h1>
  <p class="lead">{d["lead"]}</p>
</header>

<h2>{d["what_h2"]}</h2>
<p>
  {d["what_p"]}
</p>

<div class="box">
  <h3>{d["box_h3"]}</h3>
  <ul>
{box}
  </ul>
</div>

<h2>{d["who_h2"]}</h2>
<dl>
  <dt>{d["op_dt"]}</dt>
  <dd>{d["op_dd"]}</dd>
  <dt>{d["contact_dt"]}</dt>
  <dd>{d["contact_dd"]}</dd>
  <dt>{d["legal_dt"]}</dt>
  <dd>{d["legal_dd"]}</dd>
</dl>

<h2>{d["disco_h2"]}</h2>
<p>
  {d["disco_p1"]}
</p>
<p>
  {d["disco_p2"]}
</p>

<h2>{d["fig_h2"]}</h2>
<ul>
{zahlen}
</ul>

<div class="box warn">
  <h3>{d["warn_h3"]}</h3>
  <p>
    {d["warn_p1"]}
  </p>
  <p>
    {d["warn_p2"]}
  </p>
  <p>
    {d["warn_p3"]}
  </p>
  <p>
    {d["warn_p4"]}
  </p>
</div>

<h2>{d["links_h2"]}</h2>
<p>
  {d["links_p"]}
</p>

<h2>{d["corr_h2"]}</h2>
<p>
  {d["corr_p"]}
</p>

<h2>{d["reuse_h2"]}</h2>
<p>
  {d["reuse_p"]}
</p>
</div>'''


def kopf_anpassen(kopf):
    b = T.TEXTE[T.BASIS]
    k = kopf
    # hreflang-Satz auf diese Adresse, wie bei den anderen neunsprachigen Seiten.
    k = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", k)
    verweise = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{T.URL}">' for l in T.SPRACHEN
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{T.URL}">'
    k = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + "\n" + verweise, k, count=1)
    # ld+json: gleiche Felder wie bisher, aber inLanguage als Liste aller neun.
    alt = re.search(r'<script type="application/ld\+json">(.*?)</script>', k, flags=re.S)
    ld = json.loads(alt.group(1))
    ld["inLanguage"] = T.SPRACHEN
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)
    return k


def main():
    s = ZIEL.read_text(encoding="utf-8")
    kopf = s[: s.index('<div class="wrap">') + len('<div class="wrap">')]
    # Der gemeinsame Fuss (Disclaimer-/Privacy-Verweis) ist sprachneutral und
    # bleibt ausserhalb der Bloecke; die Bloecke selbst tragen kein <footer>.
    fuss = s[s.rindex("<footer>"):]
    kopf = kopf_anpassen(kopf)
    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE]
    if fehlt:
        print(f"WARNUNG: ohne Fassung fuer {', '.join(fehlt)} — Seite unvollstaendig")
    bloecke = "\n\n".join(block(l) for l in T.SPRACHEN if l in T.TEXTE)
    ZIEL.write_text(kopf + "\n" + bloecke + "\n\n" + fuss, encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)} ({len(T.TEXTE)} Fassungen)")


if __name__ == "__main__":
    main()
