#!/usr/bin/env python3
"""Baut /recipes/ aus texte_recipes.py — neun Sprachen.

Gleiches Muster wie build-for-agents.py: Kopf und Fuss aus der bestehenden
Seite, alle Sprachen als data-lang-Bloecke in einer Datei, Code-Bloecke
(Befehle, keine Prosa) bleiben in jeder Sprache unveraendert.

Warum eine eigene Seite und kein Abschnitt in der Notiz: die Notiz begruendet,
ob der Server sich lohnt. Wer ihn benutzen will, sucht nicht nach einer
Begruendung, sondern nach einer Zeile zum Einfuegen.

Jedes Rezept hier wurde am 03.08.2026 ausgefuehrt, bevor es aufgeschrieben
wurde. Ein ungetestetes Rezept ist eine Behauptung.

    python3 build-recipes-page.py
"""
import json
import re
from pathlib import Path

import texte_recipes as T

HIER = Path(__file__).resolve().parent
ZIEL = HIER / "docs" / "recipes" / "index.html"

REGELN = (
    "  [data-lang]{display:none}\n"
    "  [data-lang].on{display:block}\n"
    "  li[data-lang].on{display:list-item}\n"
    "  span[data-lang].on,a[data-lang].on{display:inline}\n"
)

# Die fuenf Code-Bloecke der Seite — Befehle, keine Prosa, darum unuebersetzt.
PRE_READING = r'''while read -r u; do
  curl -sX POST https://provinglab.dev/mcp \
    -H 'content-type: application/json' \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"tools/call\",
         \"params\":{\"name\":\"extract_citation\",\"arguments\":{\"url\":\"$u\"}}}" \
  | python3 -c 'import json,sys
d = json.loads(json.load(sys.stdin)["result"]["content"][0]["text"])
sys.stdout.write(d["ris"]) if d.get("complete") else \
  sys.stderr.write("skipped: " + d.get("warning","") + "\n")'
done &lt; reading-list.txt &gt; literature.ris'''

PRE_CC = "claude mcp add --transport http provinglab https://provinglab.dev/mcp"

PRE_CD = '''{
  "mcpServers": {
    "provinglab": {
      "command": "npx",
      "args": ["-y", "mcp-remote", "https://provinglab.dev/mcp"]
    }
  }
}'''

PRE_PY = '''import json, urllib.request

def cite(url):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "extract_citation", "arguments": {"url": url}}}).encode()
    req = urllib.request.Request("https://provinglab.dev/mcp", body, {
        "content-type": "application/json",
        "user-agent": "my-bibliography-script/1.0",   # <- without this: 403
    })
    answer = json.loads(urllib.request.urlopen(req, timeout=60).read())
    return json.loads(answer["result"]["content"][0]["text"])

record = cite("https://doi.org/10.1038/s41586-020-2649-2")
if record.get("complete"):
    print(record["ris"])
else:
    print("not usable:", record["warning"])'''

PRE_WSL = "/mnt/c/Users/&lt;you&gt;/Downloads/Full Page PDF Snap/pubmed_2026-08-03_0911_0001.pdf"


def zelle(text, cls):
    return f'<td class="{cls}">{text}</td>' if cls else f"<td>{text}</td>"


def routentabelle(d):
    th = '<th scope="col"></th>' + "".join(f'<th scope="col">{k}</th>' for k in d["wr_th"])
    zeilen = []
    for name, ep, ep_cls, ext, ext_cls in d["wr_rows"]:
        zeilen.append("    <tr><td>{}</td>{}{}</tr>".format(
            name, zelle(ep, ep_cls), zelle(ext, ext_cls)))
    return ("<table>\n  <thead><tr>" + th + "</tr></thead>\n  <tbody>\n"
            + "\n".join(zeilen) + "\n  </tbody>\n</table>")


def block(l):
    d = T.TEXTE[l]
    an = ' class="on"' if l == T.BASIS else ""
    eintraege = "\n".join(
        f'  <li><a href="{href}">{text}</a>\n      {desc}</li>'
        for href, text, desc in d["ma_items"]
    )
    return f'''<div data-lang="{l}"{an} lang="{l}">
<p class="crumb"><a href="../">Proving Lab</a> · {d["crumb"]}</p>

<header>
  <h1>{d["h1"]}</h1>
  <p class="standfirst">
    {d["standfirst"]}
  </p>
  <p class="meta-line">{d["meta"]}</p>
</header>

<div class="box">
  <h3>{d["getback_h3"]}</h3>
  <p>
    {d["getback_p"]}
  </p>
</div>

<h2 id="reading-list">{d["rl_h2"]}</h2>
<p>
  {d["rl_p1"]}
</p>
<pre><code>{PRE_READING}</code></pre>
<p>
  {d["rl_p2"]}
</p>

<h2 id="claude-code">{d["cc_h2"]}</h2>
<pre><code>{PRE_CC}</code></pre>
<p>
  {d["cc_p"]}
</p>

<h2 id="claude-desktop">{d["cd_h2"]}</h2>
<p>
  {d["cd_p"]}
</p>
<pre><code>{PRE_CD}</code></pre>

<h2 id="python">{d["py_h2"]}</h2>
<p>
  {d["py_p"]}
</p>
<pre><code>{PRE_PY}</code></pre>

<h2 id="wsl">{d["wsl_h2"]}</h2>
<p>
  {d["wsl_p1"]}
</p>
<p>
  {d["wsl_p2"]}
</p>
<pre><code>{PRE_WSL}</code></pre>
<p>
  {d["wsl_p3"]}
</p>

<h2 id="which-route">{d["wr_h2"]}</h2>
<div class="tblwrap">{routentabelle(d)}</div>
<p>
  {d["wr_p"]}
</p>

<h2 id="machine">{d["ma_h2"]}</h2>
<p>
  {d["ma_p"]}
</p>
<ul>
{eintraege}
</ul>

<div class="box">
  <h3>{d["proves_h3"]}</h3>
  <p>
    {d["proves_p"]}
  </p>
</div>

<p style="font-size:.9rem;color:var(--dim)">{d["disclosure"]}</p>
<footer>{d["foot"]}</footer>
</div>'''


def kopf_anpassen(kopf):
    k = kopf
    # hreflang-Satz auf diese Adresse, wie bei den anderen neunsprachigen Seiten.
    k = re.sub(r'\s*<link rel="alternate" hreflang="[^"]*" href="[^"]*">', "", k)
    verweise = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{T.URL}">' for l in T.SPRACHEN
    ) + f'\n<link rel="alternate" hreflang="x-default" href="{T.URL}">'
    k = re.sub(r'(<link rel="canonical" href="[^"]*">)', lambda m: m.group(1) + "\n" + verweise, k, count=1)
    # Die Seite spricht jetzt neun Sprachen — das LD muss es wissen.
    k = re.sub(r'"inLanguage":\s*(?:"en"|\[[^\]]*\])',
               lambda _: '"inLanguage": ' + json.dumps(T.SPRACHEN), k, count=1)
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
