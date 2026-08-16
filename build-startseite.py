#!/usr/bin/env python3
"""Baut docs/index.html aus texte_startseite.py — die Startseite in neun Sprachen.

Alle Sprachen in derselben Datei, jede als data-lang-Block; sichtbar ist genau
eine (docs/site-lang.js, domainweite Wahl). Kopf und Navigation kommen aus der
bestehenden Seite, damit Aenderungen am Kopf (Meta, Styles, Menue) nicht
auseinanderlaufen.

Warum ein Bauer statt Handpflege: Die Startseite wurde von Hand editiert, und
jede Hand-Aenderung musste die Uebersetzungen mitziehen oder liess acht
Fassungen still zurueck. Eintraege (Notes, Messungen, Tools) gehoeren jetzt in
texte_startseite.py — ein Lauf dieses Skripts schreibt die Seite neu.

    python3 build-startseite.py
"""
import html as htmlmod
from pathlib import Path

import texte_startseite as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "index.html"


def eintraege(liste):
    """Ein .item je Eintrag; figures-Zeile nur, wenn welche da sind."""
    aus = []
    for e in liste:
        teile = ['      <div class="item">']
        if e.get("date"):
            teile.append(f'        <p class="date">{e["date"]}</p>')
        teile.append(f'        <h3><a href="{e["href"]}">{e["title"]}</a></h3>')
        teile.append(f"        <p>\n          {e['text']}\n        </p>")
        if e.get("figures"):
            teile.append('        <div class="figures">')
            for f in e["figures"]:
                teile.append(f"          <span>{f}</span>")
            teile.append("        </div>")
        teile.append("      </div>")
        aus.append("\n".join(teile))
    return "\n".join(aus)


def block(l):
    """Eine Sprachfassung: header + alle Sections + footer in einem data-lang-Block."""
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    dzahlen = "\n".join(f"        <span>{z}</span>" for z in d["dzahlen"])
    prinzipien = "\n".join(
        f'      <div class="pr">\n        <h3>{h}</h3>\n        <p>\n          {p}\n        </p>\n      </div>'
        for h, p in d["prinzipien"]
    )
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <div class="wrap">
    <p class="mark">Proving Lab</p>
    <h1>{d["h1"]}</h1>
    <p class="tagline">
      {d["tagline1"]}
    </p>
    <p class="tagline" style="margin-top:14px;font-size:.98rem">
      {d["tagline2"]}
    </p>
  </div>
</header>

<section class="direkt">
  <div class="wrap">
    <div class="dkarte">
      <div class="dtext">
        <p class="dmark">{d["dmark"]}</p>
        <h2>Full Page PDF Snap</h2>
        <p>{d["dtext"]}</p>
        <p class="dzahlen">
{dzahlen}
      </p>
      <p class="dbeleg">{d["dbeleg"]}</p>
      </div>
      <div class="dknopf">
        <a class="dprim" href="https://addons.mozilla.org/firefox/downloads/file/4944968/full_page_pdf_snap_webpagesave-2.33.4.xpi">{d["ddownload"]}</a>
        <p class="dklein">{d["dversion"]}</p>
        <p class="dklein">
          <a href="https://github.com/Bubu89/full-page-pdf-snap/releases/latest">{d["dohne"]}</a> ·
          <a href="https://chromewebstore.google.com/detail/ekjbgcdhpgijhbepkagefnkdbdfjpehn">{d["dchrome"]}</a> ·
          <a href="tools/full-page-pdf-snap/">{d["dwas"]}</a>
        </p>
      </div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>{d["notes_h2"]}</h2>
    <p class="sub">{d["notes_sub"]}</p>
    <div class="items">
{eintraege(d["notes"])}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>{d["meas_h2"]}</h2>
    <p class="sub">{d["meas_sub"]}</p>

    <div class="items">
{eintraege(d["meas"])}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>{d["prinzip_h2"]}</h2>
    <div class="principles">
{prinzipien}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>{d["tools_h2"]}</h2>
    <p class="sub">
      {d["tools_sub"]}
    </p>
    <div class="items">
{eintraege(d["tools"])}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <h2>{d["nach_h2"]}</h2>
    <p class="sub">
      {d["nach_sub"]}
    </p>
    <div class="items">
{eintraege(d["nach"])}
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="disclosure">
      <h3>{d["disc_h3"]}</h3>
      <p>
        {d["disc_p1"]}
      </p>
      <p>
        {d["disc_p2"]}
      </p>
    </div>
  </div>
</section>

<footer>
  <div class="wrap">
    <p>{d["foot_1"]}</p>
    <p>{d["foot_2"]}</p>
  </div>
</footer>
</div>'''


def main():
    s = ZIEL.read_text(encoding="utf-8")
    # Fruehestes Zeichen der Sprachbloecke: normalerweise der oeffnende
    # data-lang-div, bei einer Seite ohne Bloecke der <header>. Nur bis dahin
    # darf der Kopf reichen — ein div-Fragment im Kopf ueberlebt sonst jeden
    # Lauf (15.08.2026: fuenf EN-Oeffner aus einer defekten Zwischenfassung).
    anfang = s.index("<header>")
    div0 = s.find('<div data-lang=')
    if 0 <= div0 < anfang:
        anfang = div0
    kopf = s[:anfang]
    # Alles zwischen erstem <header> und letztem </footer> sind die Sprachbloecke
    # und wird neu geschrieben. s.index("</footer>") trifft den Fuss des ersten
    # Blocks — das hatte bei jedem Lauf die Bloecke danach noch einmal angehaengt
    # (drei EN-Fassungen nach drei Laeufen, 15.08.2026).
    ende = s[s.rindex("</body>") :]

    # Die Umschaltung lebt von diesen Regeln; die Startseite trug sie nie,
    # weil sie bisher keine Sprachbloecke hatte. Ohne sie stapeln sich alle
    # Fassungen sichtbar untereinander (aufgetreten 15.08.2026).
    if "[data-lang]{display:none}" not in kopf:
        regeln = (
            "  [data-lang]{display:none}\n"
            "  [data-lang].on{display:block}\n"
            "  li[data-lang].on{display:list-item}\n"
            "  span[data-lang].on,a[data-lang].on{display:inline}\n"
        )
        kopf = kopf.replace("</style>", regeln + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE]
    if fehlt:
        print(f"WARNUNG: ohne Fassung fuer {', '.join(fehlt)} — Seite unvollstaendig")
    bloecke = "\n\n".join(block(l) for l in T.SPRACHEN if l in T.TEXTE)
    seite = kopf + bloecke + "\n" + ende
    ZIEL.write_text(seite, encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)} ({len(seite):,} Zeichen, {len(T.TEXTE)} Fassungen)")


if __name__ == "__main__":
    main()
