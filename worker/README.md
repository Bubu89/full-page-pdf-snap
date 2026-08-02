# MCP-Server und Markdown-Aushandlung als Worker

Ein Worker, zwei Aufgaben — beide brauchen denselben Ursprung wie die Seite:

| Pfad / Bedingung | Verhalten |
|---|---|
| `POST /mcp` | MCP über Streamable HTTP, JSON-RPC 2.0, zustandslos |
| `Accept: text/markdown` | jede HTML-Seite als Markdown |
| alles andere | unverändert von GitHub Pages durchgereicht |

Zustandslos heißt: keine Durable Objects, damit der **freie Tarif** reicht
(100.000 Anfragen/Tag). Gemessen im Trockenlauf: eine Messungsseite schrumpft
von 24.366 B HTML auf 9.264 B Markdown — 62 % weniger Text für einen Agenten.

## Warum die Route die ganze Zone abfängt

Die Markdown-Aushandlung muss auf jeder Seite greifen, nicht nur unter einem
Präfix. Das Risiko dabei ist real: Ein Defekt im Worker würde die ganze Seite
treffen. Deshalb liegt der komplette `fetch` in einem `try`, dessen `catch`
nichts anderes tut als `fetch(request)` — die unveränderte Antwort des
Ursprungs. Ein Fehler kostet dann die Zusatzfunktion, nicht die Website.

## Deployment

Der Token braucht **Account → Workers Scripts → Edit** und
**Zone → Workers Routes → Edit**. Beides ist Account-Scope und gehört deshalb
in einen eigenen Token, nicht zum Zone-Token dazu.

```bash
cd worker
export CLOUDFLARE_API_TOKEN="…"      # aus Vaultwarden, nie aus dem Chat
npx wrangler deploy
```

## Danach — und keinen Schritt früher

`server-card.json` liegt bewusst **hier** und nicht unter `docs/.well-known/`.
Sie nennt `https://provinglab.dev/mcp` als Endpunkt. Solange der Worker nicht
läuft, zeigt sie ins Leere, und jeder Agent, der ihr folgt, verliert eine
Anfrage. Erst wenn der Endpunkt antwortet, gehört sie veröffentlicht:

```bash
mkdir -p docs/.well-known/mcp
mv worker/server-card.json docs/.well-known/mcp/
curl -s -X POST https://provinglab.dev/mcp \
  -H 'content-type: application/json' \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' | head -c 300
```

## Prüfpunkte, die damit fallen

`mcpServerCard` und `markdownNegotiation` — letzteres ohne den Pro-Tarif, den
Cloudflares eigenes „Markdown for Agents" voraussetzt.
