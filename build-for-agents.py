#!/usr/bin/env python3
"""Baut docs/for-agents/index.html aus texte_for_agents.py — neun Sprachen.

Gleiches Muster wie build-firefox-chrome-post.py: Kopf und Fuss aus der
bestehenden Seite, alle Sprachen als data-lang-Bloecke in einer Datei,
Code-Bloecke bleiben in jeder Sprache unveraendert.

    python3 build-for-agents.py
"""
import json
import re
from pathlib import Path

import texte_for_agents as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "for-agents" / "index.html"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)

# Die drei Code-Bloecke der Seite — Befehle, keine Prosa, darum unuebersetzt.
PRE_CONNECT = "claude mcp add --transport http provinglab https://provinglab.dev/mcp"
PRE_RULE = 'if not record["complete"]:\n    hand_back(url, record.get("warning"), record.get("nextStep"))'
PRE_PROFILE = (
    "firefox -headless -no-remote -marionette -profile &lt;profile&gt;\n"
    '[0,1,"WebDriver:NewSession",{}]\n'
    '[0,2,"Addon:Install",{"path":"&lt;signed xpi&gt;","temporary":false}]\n'
    '[0,3,"Addon:Uninstall",{"id":"&lt;extension id&gt;"}]'
)
PRE_WORK = (
    '{"jsonrpc":"2.0","id":1,"method":"tools/call",\n'
    ' "params":{"name":"open_work","arguments":{}}}'
)


def tabelle(koepfe, zeilen, rowheader=False):
    th = "".join(f'<th scope="col">{k}</th>' for k in koepfe)
    aus = [f"<table>\n  <thead><tr>{th}</tr></thead>\n  <tbody>"]
    for z in zeilen:
        if rowheader:
            aus.append(f'    <tr><th scope="row">{z[0]}</th>\n        <td>{z[1]}</td></tr>')
        else:
            aus.append(f"    <tr><td>{z[0]}</td><td>{z[1]}</td></tr>")
    aus.append("  </tbody>\n</table>")
    return "\n".join(aus)


def werkzeugtabelle(d):
    th = "".join(f'<th scope="col">{k}</th>' for k in d["tools_th"])
    aus = [f"<table>\n  <thead><tr>{th}</tr></thead>\n  <tbody>"]
    for name, was in d["tools"]:
        aus.append(f'    <tr><th scope="row"><code>{name}</code></th>\n        <td>{was}</td></tr>')
    aus.append("  </tbody>\n</table>")
    return "\n".join(aus)


def block(l):
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    kf = "\n".join(
        f'  <div class="kf{" b" if i == 0 else ""}"><div class="n">{n}</div><div class="l">{t}</div></div>'
        for i, (n, t) in enumerate(d["kf"])
    )
    return f'''<div data-lang="{l}"{an} lang="{l}">
<header>
  <h1>{d["h1"]}</h1>
  <p class="standfirst">
    {d["standfirst"]}
  </p>
  <p class="meta">{d["meta"]}</p>
</header>

<h2>{d["connect_h2"]}</h2>
<pre><code>{PRE_CONNECT}</code></pre>
<p>
  {d["connect_p1"]}
</p>
<p style="font-size:.9rem">
  {d["connect_p2"]}
</p>

<h2>{d["tools_h2"]}</h2>
{werkzeugtabelle(d)}

<h2>{d["rule_h2"]}</h2>
<p>
  {d["rule_p1"]}
</p>
<pre><code>{PRE_RULE}</code></pre>
<p>
  {d["rule_p2"]}
</p>

<h2>{d["yield_h2"]}</h2>
<div class="kf-row">
{kf}
</div>
<p>
  {d["yield_p"]}
</p>

<h2>{d["drive_h2"]}</h2>
<p>
  {d["drive_p1"]}
</p>
{tabelle(d["drive_th"], d["drive"])}
<p>
  {d["drive_p2"]}
</p>
<p style="font-size:.9rem">
  {d["drive_p3"]}
</p>

<h2>{d["profile_h2"]}</h2>
<p>
  {d["profile_p1"]}
</p>
<pre><code>{PRE_PROFILE}</code></pre>
{tabelle(d["profile_th"], d["profile"], rowheader=True)}
<p>
  {d["profile_p2"]}
</p>
<p>
  {d["profile_p3"]}
</p>

<h2>{d["disco_h2"]}</h2>
{tabelle(d["disco_th"], d["disco"])}
<p>
  {d["disco_p"]}
</p>

<h2>{d["work_h2"]}</h2>
<p>
  {d["work_p1"]}
</p>
<pre><code>{PRE_WORK}</code></pre>
<p>
  {d["work_p2"]}
</p>
<p>
  {d["work_p3"]}
</p>
<p>
  {d["work_p4"]}
</p>
<p>
  {d["work_p5"]}
</p>

<h2>{d["fair_h2"]}</h2>
<p>
  {d["fair_p"]}
</p>
<footer>
      {d["foot"]}
    </footer>
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
    ld = {
        "@context": "https://schema.org", "@type": "TechArticle",
        "headline": b["h1"],
        "datePublished": "2026-08-03", "dateModified": "2026-08-16",
        "inLanguage": T.SPRACHEN, "url": T.URL,
        "author": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
        "publisher": {"@type": "Organization", "name": "Proving Lab", "url": "https://provinglab.dev/"},
    }
    neu = '<script type="application/ld+json">\n' + json.dumps(ld, indent=2, ensure_ascii=False) + "\n</script>"
    k = re.sub(r'<script type="application/ld\+json">.*?</script>', lambda _: neu, k, count=1, flags=re.S)
    return k


def main():
    s = ZIEL.read_text(encoding="utf-8")
    kopf = s[: s.index('<div class="wrap">') + len('<div class="wrap">')]
    ende = s[s.rindex("</div>\n</body>") :]
    kopf = kopf_anpassen(kopf)
    if "[data-lang]{display:none}" not in kopf:
        kopf = kopf.replace("</style>", REGELN + "</style>", 1)

    fehlt = [l for l in T.SPRACHEN if l not in T.TEXTE]
    if fehlt:
        print(f"WARNUNG: ohne Fassung fuer {', '.join(fehlt)} — Seite unvollstaendig")
    bloecke = "\n\n".join(block(l) for l in T.SPRACHEN if l in T.TEXTE)
    ZIEL.write_text(kopf + "\n" + bloecke + "\n" + ende, encoding="utf-8")
    print(f"geschrieben: {ZIEL.relative_to(HIER)} ({len(T.TEXTE)} Fassungen)")


if __name__ == "__main__":
    main()
