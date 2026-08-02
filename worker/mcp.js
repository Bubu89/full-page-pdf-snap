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
const VERSION = "1.4.0";
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


/* --- OAuth: echt, aber nicht erforderlich ---------------------------------
 *
 * Nichts auf dieser Seite ist geschuetzt, und daran aendert sich nichts. Der
 * Grund fuer diesen Teil ist ein anderer: Manche MCP-Clients erwarten einen
 * Autorisierungsserver und verbinden sich sonst gar nicht erst. Fuer die
 * bietet der Endpunkt einen vollstaendigen Weg an — dynamische Registrierung
 * nach RFC 7591, Token nach Client Credentials, und der MCP-Endpunkt nimmt das
 * Token entgegen.
 *
 * Was hier NICHT passiert: so zu tun, als wuerde damit etwas geschuetzt. Der
 * MCP-Endpunkt antwortet mit und ohne Token identisch, jede Registrierung wird
 * angenommen, und auth.md sagt das ausdruecklich. Ein Token, das nichts
 * freischaltet, darf nicht so aussehen, als taete es das.
 *
 * Die Signatur verhindert nur, dass ein erfundenes Token als gueltig gilt —
 * sie schuetzt keinen Zugang. Der Schluessel steht deshalb offen im Code;
 * ihn geheim zu halten waere Theater.
 */
const OAUTH_KEY = "provinglab-public-endpoint-no-secret-needed";
const TOKEN_TTL = 3600;

async function hmac(daten) {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(OAUTH_KEY),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const sig = await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(daten));
  return btoa(String.fromCharCode(...new Uint8Array(sig)))
    .replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function tokenErzeugen(clientId) {
  const nutz = btoa(JSON.stringify({
    sub: clientId, iss: "https://provinglab.dev", aud: "https://provinglab.dev",
    iat: Math.floor(Date.now() / 1000), exp: Math.floor(Date.now() / 1000) + TOKEN_TTL,
  })).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return nutz + "." + (await hmac(nutz));
}

function autorisierungsserver() {
  return {
    issuer: "https://provinglab.dev",
    authorization_endpoint: "https://provinglab.dev/oauth/authorize",
    token_endpoint: "https://provinglab.dev/oauth/token",
    registration_endpoint: "https://provinglab.dev/oauth/register",
    jwks_uri: "https://provinglab.dev/oauth/jwks",
    scopes_supported: ["read"],
    response_types_supported: ["code"],
    grant_types_supported: ["client_credentials", "authorization_code"],
    token_endpoint_auth_methods_supported: ["none", "client_secret_post"],
    code_challenge_methods_supported: ["S256"],
    service_documentation: "https://provinglab.dev/auth.md",
    // Aufbau nach der auth.md-Spezifikation (github.com/workos/auth.md).
    // Die Feldnamen lauten dort identity_types_supported und
    // credential_types_supported je Typ — nicht umgekehrt, wie die Prosa
    // des Pruefberichts nahelegt. Drei Runden Raten haetten sich mit einem
    // Blick in die Spezifikation erledigt.
    agent_auth: {
      skill: "https://provinglab.dev/auth.md",
      register_uri: "https://provinglab.dev/oauth/register",
      claim_uri: "https://provinglab.dev/oauth/claim",
      revocation_uri: "https://provinglab.dev/oauth/revoke",
      identity_endpoint: "https://provinglab.dev/oauth/register",
      claim_endpoint: "https://provinglab.dev/oauth/claim",
      events_endpoint: null,
      identity_types_supported: ["anonymous", "service_auth"],
      anonymous: {
        credential_types_supported: ["none"],
        register_uri: "https://provinglab.dev/oauth/register",
        claim_uri: "https://provinglab.dev/oauth/claim",
        description: "Send no credentials. The normal case, and it grants full access.",
      },
      service_auth: {
        credential_types_supported: ["client_secret_post", "none"],
        claim_uri: "https://provinglab.dev/oauth/claim",
        register_uri: "https://provinglab.dev/oauth/register",
        token_uri: "https://provinglab.dev/oauth/token",
        grant_types_supported: ["client_credentials"],
        description: "For clients that require an OAuth flow. Grants nothing beyond anonymous.",
      },
      events_supported: [],
      // Der wichtigste Eintrag: Es ist nicht noetig.
      authentication_required: false,
      note: "All resources are public. Credentials are accepted for clients that require an OAuth flow, and grant no additional access.",
    },
  };
}

async function handleOAuth(pfad, request) {
  if (request.method === "OPTIONS") return new Response(null, { status: 204, headers: CORS });

  if (pfad === "/oauth/register") {
    // RFC 7591: jede Registrierung wird angenommen, weil es nichts zu pruefen
    // gibt. Der Client bekommt eine echte, stabile Kennung.
    let wunsch = {};
    try { wunsch = await request.json(); } catch { /* leerer Rumpf ist zulaessig */ }
    const id = "pl_" + (await hmac(JSON.stringify(wunsch.client_name || "anonymous"))).slice(0, 24);
    return json({
      client_id: id,
      client_id_issued_at: Math.floor(Date.now() / 1000),
      client_name: wunsch.client_name || "anonymous",
      grant_types: ["client_credentials"],
      token_endpoint_auth_method: "none",
      scope: "read",
    }, 201);
  }

  if (pfad === "/oauth/token") {
    let clientId = "anonymous";
    try {
      const ct = request.headers.get("content-type") || "";
      if (ct.includes("json")) {
        const b = await request.json();
        clientId = b.client_id || clientId;
      } else {
        const f = new URLSearchParams(await request.text());
        clientId = f.get("client_id") || clientId;
      }
    } catch { /* ohne Angabe: anonym */ }
    return json({
      access_token: await tokenErzeugen(clientId),
      token_type: "Bearer",
      expires_in: TOKEN_TTL,
      scope: "read",
    });
  }

  if (pfad === "/oauth/claim") {
    // Eine anonyme Identitaet an ein Konto zu binden, setzt Konten voraus.
    // Es gibt keine — und der Endpunkt sagt das, statt zu schweigen.
    return json({
      claimable: false,
      reason: "no_accounts",
      description:
        "There are no accounts to bind an identity to. Every resource on " +
        "provinglab.dev is public, so an anonymous identity already has full " +
        "access and nothing is gained by claiming it.",
      documentation: "https://provinglab.dev/auth.md",
    }, 200);
  }

  if (pfad === "/oauth/revoke") {
    // RFC 7009 verlangt 200 auch fuer unbekannte Token. Hier gilt das immer:
    // Ein Token schaltet nichts frei, es zurueckzuziehen aendert nichts.
    return json({
      revoked: true,
      note: "Tokens grant no access, so revocation has no effect on what a client can reach.",
    }, 200);
  }

  if (pfad === "/oauth/jwks") {
    // Symmetrisch signiert — es gibt keinen oeffentlichen Schluessel zu zeigen.
    return json({ keys: [] });
  }

  if (pfad === "/oauth/authorize") {
    return json({
      error: "not_required",
      error_description:
        "All resources on provinglab.dev are public. Use the token endpoint with " +
        "grant_type=client_credentials if your client needs a token, or send no " +
        "credentials at all.",
    }, 400);
  }

  return json({ error: "not_found" }, 404);
}

export default {
  async fetch(request, env, ctx) {
    try {
      const url = new URL(request.url);

      if (url.pathname === "/mcp" || url.pathname === "/mcp/") {
        return handleMcp(request, SITE);
      }

      if (url.pathname.startsWith("/oauth/")) {
        return handleOAuth(url.pathname, request);
      }

      if (url.pathname === "/.well-known/oauth-authorization-server") {
        return json(autorisierungsserver());
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
