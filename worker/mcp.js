/**
 * provinglab.dev — MCP-Server und Markdown-Aushandlung als Cloudflare Worker.
 *
 * Zwei Aufgaben, ein Worker, weil beide denselben Ursprung brauchen:
 *
 *   POST /mcp                     MCP ueber Streamable HTTP (JSON-RPC 2.0),
 *                                 zustandslos — keine Durable Objects, damit
 *                                 der freie Tarif reicht (100.000 Anfragen/Tag).
 *   Accept: text/markdown         liefert jede HTML-Seite als Markdown aus.
 *                                 Cloudflares eigenes "Markdown for Agents"
 *                                 verlangt Pro; das hier kostet nichts.
 *
 * Sicherheitsnetz: Jeder unerwartete Fehler faellt auf fetch(request) zurueck,
 * also auf die unveraenderte Antwort von GitHub Pages. Ein Defekt in diesem
 * Worker darf die Seite nicht ausknipsen.
 */

// Die Daten liegen immer auf der Publikation — nicht auf der Domain, unter der
// dieser Worker gerade laeuft. Auf einer workers.dev-Adresse zeigte url.origin
// sonst auf den Worker selbst und jede Datenabfrage endete im 404.
const SITE = "https://provinglab.dev";
const VERSION = "1.1.0";
const PROTOCOL = "2025-06-18";

const TOOLS = [
  {
    name: "list_measurements",
    description:
      "List the measurements published on provinglab.dev with their dataset " +
      "URLs and the pages documenting how each was measured. Start here.",
    inputSchema: { type: "object", properties: {}, additionalProperties: false },
  },
  {
    name: "get_measurement_data",
    description:
      "Fetch one measurement dataset as JSON: measured values, the control run " +
      "and the conditions under which they were obtained.",
    inputSchema: {
      type: "object",
      properties: {
        dataset: { type: "string", description: "Dataset URL or bare filename" },
      },
      required: ["dataset"],
      additionalProperties: false,
    },
  },
  {
    name: "get_method",
    description:
      "Fetch a reproducible method: reading a browser extension's permissions, " +
      "measuring OCR recall with a control run, or choosing between " +
      "print-to-PDF and screen capture. Omit the argument to list them.",
    inputSchema: {
      type: "object",
      properties: { name: { type: "string" } },
      additionalProperties: false,
    },
  },
];

// Der Endpunkt liefert ausschliesslich oeffentliche Daten und kennt keine
// Sitzung — ein weit gefasstes CORS gibt hier nichts preis, oeffnet aber
// browserbasierten Clients ueberhaupt erst den Zugang.
const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type, mcp-protocol-version",
  "access-control-max-age": "86400",
};

const json = (body, status = 200, extra = {}) =>
  new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8", ...CORS, ...extra },
  });

const rpcOk = (id, result) => json({ jsonrpc: "2.0", id, result });
const rpcErr = (id, code, message) => json({ jsonrpc: "2.0", id, error: { code, message } });
const textResult = (s) => ({ content: [{ type: "text", text: s }] });

async function fetchJson(origin, path) {
  const url = origin + path;
  const r = await fetch(url, {
    headers: { accept: "application/json", "user-agent": "provinglab-mcp/1.0" },
    // Der Subrequest darf nicht am Edge-Cache haengen bleiben: die Discovery-
    // Dateien aendern sich haeufiger als der Rest und muessen aktuell sein.
    cf: { cacheTtl: 60, cacheEverything: false },
  });
  if (!r.ok) throw new Error(`GET ${url} -> ${r.status} ${r.statusText}`);
  return r.json();
}

async function runTool(origin, name, args) {
  if (name === "list_measurements") {
    const cat = await fetchJson(origin, "/.well-known/api-catalog");
    const rows = cat.linkset
      .filter((e) => e.anchor.includes("/data/"))
      .map((e) => {
        const via = e.via && e.via[0] ? e.via[0].href : "";
        return `- dataset: ${e.anchor}${via ? `\n  method: ${via}` : ""}`;
      });
    return textResult(
      `Measurements with raw data (${rows.length}):\n${rows.join("\n")}\n\n` +
        `Narrative index of everything published here: ${origin}/llms.txt`
    );
  }

  if (name === "get_measurement_data") {
    const d = String((args && args.dataset) || "");
    if (!d) throw new Error("dataset is required");
    // Nur der Dateiname zaehlt. Ein Praefixvergleich auf "/data/" reicht nicht:
    // "/data/../beliebig" beginnt damit und wird vom Server trotzdem
    // normalisiert — gemessen am 02.08.2026, es lieferte eine fremde Datei aus.
    // Deshalb wird der Name geprueft, nicht der Pfad zusammengesetzt.
    const roh = d.startsWith("http") ? new URL(d).pathname : d;
    const name2 = roh.split("/").pop() || "";
    if (!/^[A-Za-z0-9._-]+\.json$/.test(name2) || name2.includes("..")) {
      throw new Error("dataset must be a plain .json filename from /data/");
    }
    return textResult(JSON.stringify(await fetchJson(origin, "/data/" + name2), null, 2));
  }

  if (name === "get_method") {
    const idx = await fetchJson(origin, "/.well-known/agent-skills/index.json");
    const want = args && args.name;
    if (!want) {
      return textResult(idx.skills.map((s) => `- ${s.name}: ${s.description}`).join("\n"));
    }
    const hit = idx.skills.find((s) => s.name === want);
    if (!hit) {
      return textResult(
        `No method named ${want}. Available: ${idx.skills.map((s) => s.name).join(", ")}`
      );
    }
    const r = await fetch(hit.url);
    return textResult(await r.text());
  }

  throw new Error(`unknown tool: ${name}`);
}

async function handleMcp(request, origin) {
  if (request.method === "OPTIONS") {
    return new Response(null, { status: 204, headers: CORS });
  }
  if (request.method === "GET") {
    // Kein SSE: der Server ist zustandslos, es gibt nichts zu streamen.
    return json(
      { error: "This MCP endpoint is stateless. Send JSON-RPC over POST." },
      405,
      { allow: "POST" }
    );
  }
  if (request.method !== "POST") return json({ error: "method not allowed" }, 405);

  let msg;
  try {
    msg = await request.json();
  } catch {
    return rpcErr(null, -32700, "Parse error");
  }

  const batch = Array.isArray(msg) ? msg : [msg];
  const out = [];
  for (const m of batch) {
    const id = m && m.id !== undefined ? m.id : null;
    try {
      switch (m.method) {
        case "initialize":
          out.push({
            jsonrpc: "2.0",
            id,
            result: {
              protocolVersion: PROTOCOL,
              capabilities: { tools: { listChanged: false } },
              serverInfo: { name: "provinglab", version: VERSION },
              instructions:
                "Measurements on browser tools, OCR pipelines and AI-assisted " +
                "development. Every dataset here has a documented method and a " +
                "control run. Start with list_measurements.",
            },
          });
          break;
        case "notifications/initialized":
          break; // Benachrichtigung, keine Antwort
        case "ping":
          out.push({ jsonrpc: "2.0", id, result: {} });
          break;
        case "tools/list":
          out.push({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
          break;
        case "tools/call": {
          const p = m.params || {};
          const res = await runTool(origin, p.name, p.arguments || {});
          out.push({ jsonrpc: "2.0", id, result: res });
          break;
        }
        default:
          if (id !== null) out.push({ jsonrpc: "2.0", id, error: { code: -32601, message: `Method not found: ${m.method}` } });
      }
    } catch (e) {
      if (id !== null) {
        out.push({
          jsonrpc: "2.0",
          id,
          result: { content: [{ type: "text", text: `Error: ${e.message}` }], isError: true },
        });
      }
    }
  }
  if (!out.length) return new Response(null, { status: 202 });
  return json(Array.isArray(msg) ? out : out[0]);
}

/** Kompakter HTML→Markdown-Wandler. Bewusst klein: die Seiten hier sind
 *  handgeschriebenes, flaches HTML ohne Frameworks. */
function toMarkdown(html) {
  const titel = (html.match(/<title>([\s\S]*?)<\/title>/i) || [, ""])[1].trim();
  let s = html;
  s = s.replace(/<script[\s\S]*?<\/script>/gi, "");
  s = s.replace(/<style[\s\S]*?<\/style>/gi, "");
  s = s.replace(/<head[\s\S]*?<\/head>/gi, "");
  s = s.replace(/<nav[\s\S]*?<\/nav>/gi, "");
  s = s.replace(/<footer[\s\S]*?<\/footer>/gi, "");
  s = s.replace(/<!--[\s\S]*?-->/g, "");

  s = s.replace(/<h([1-6])[^>]*>([\s\S]*?)<\/h\1>/gi, (_, n, t) => `\n\n${"#".repeat(+n)} ${t.trim()}\n\n`);
  s = s.replace(/<li[^>]*>([\s\S]*?)<\/li>/gi, (_, t) => `- ${t.trim()}\n`);
  s = s.replace(/<(pre|code)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `\n\`\`\`\n${t.trim()}\n\`\`\`\n`);
  s = s.replace(/<a [^>]*href="([^"]*)"[^>]*>([\s\S]*?)<\/a>/gi, (_, h, t) => `[${t.trim()}](${h})`);
  s = s.replace(/<(strong|b)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `**${t.trim()}**`);
  s = s.replace(/<(em|i)[^>]*>([\s\S]*?)<\/\1>/gi, (_, __, t) => `*${t.trim()}*`);
  s = s.replace(/<(p|div|section|article|tr)[^>]*>/gi, "\n");
  s = s.replace(/<br\s*\/?>/gi, "\n");
  s = s.replace(/<t[dh][^>]*>([\s\S]*?)<\/t[dh]>/gi, (_, t) => `| ${t.trim()} `);
  s = s.replace(/<[^>]+>/g, "");

  s = s.replace(/&nbsp;/g, " ").replace(/&amp;/g, "&").replace(/&lt;/g, "<")
       .replace(/&gt;/g, ">").replace(/&quot;/g, '"').replace(/&#39;/g, "'")
       .replace(/&mdash;/g, "—").replace(/&ndash;/g, "–");
  s = s.replace(/[ \t]+/g, " ").replace(/\n{3,}/g, "\n\n").trim();
  return `---\ntitle: ${titel}\n---\n\n${s}\n`;
}

function wantsMarkdown(request) {
  const a = (request.headers.get("accept") || "").toLowerCase();
  if (!a.includes("text/markdown") && a !== "text/*") return false;
  // Browser senden text/html mit hoeherer Gewichtung — die bekommen HTML.
  const md = /text\/markdown(?:;q=([\d.]+))?/.exec(a);
  const ht = /text\/html(?:;q=([\d.]+))?/.exec(a);
  const q = (m) => (m ? (m[1] === undefined ? 1 : parseFloat(m[1])) : 0);
  return q(md) >= q(ht);
}

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);

      if (url.pathname === "/mcp" || url.pathname === "/mcp/") {
        return handleMcp(request, SITE);
      }

      const upstream = await fetch(request);
      const ct = upstream.headers.get("content-type") || "";
      if (!wantsMarkdown(request) || !ct.includes("text/html") || !upstream.ok) {
        return upstream;
      }

      const md = toMarkdown(await upstream.text());
      const h = new Headers(upstream.headers);
      h.set("content-type", "text/markdown; charset=utf-8");
      h.set("x-markdown-tokens", String(Math.ceil(md.length / 4)));
      h.append("vary", "accept");
      h.delete("content-length");
      return new Response(md, { status: upstream.status, headers: h });
    } catch (e) {
      // Niemals die Seite wegen eines Fehlers hier ausknipsen.
      return fetch(request);
    }
  },
};
