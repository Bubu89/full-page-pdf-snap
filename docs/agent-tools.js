/* WebMCP — exposes this site's data to an agent running in the browser.
 *
 * A reading site has no "actions" worth automating, so the tools here do the
 * one thing that is genuinely useful: hand over the measurement datasets and
 * the published methods directly, instead of making an agent scrape the pages
 * for numbers that already exist as JSON.
 *
 * Two things make the registration robust rather than clever:
 *
 *   1. The proposal has two shapes — provideContext({tools}) and
 *      registerTool(tool). Which one an implementation offers varies, so both
 *      are used, whichever is present.
 *   2. navigator.modelContext is an origin-trial API and is sometimes injected
 *      *after* page scripts run. Registering only at load time therefore misses
 *      it. A property setter catches a late assignment, and a short poll covers
 *      implementations that define it non-configurably.
 *
 * Where the API never appears, nothing happens and no error is raised.
 * https://webmachinelearning.github.io/webmcp/
 */
(function () {
  "use strict";

  var BASE = location.origin;
  var done = false;

  function json(path) {
    return fetch(BASE + path, { headers: { Accept: "application/json" } })
      .then(function (r) {
        if (!r.ok) throw new Error(path + " returned " + r.status);
        return r.json();
      });
  }

  function text(content) {
    return { content: [{ type: "text", text: content }] };
  }

  var TOOLS = [
    {
      name: "list_measurements",
      description:
        "List the measurements published on this site, each with its page URL, " +
        "the raw dataset URL where one exists, and what was measured. Start here.",
      inputSchema: { type: "object", properties: {}, additionalProperties: false },
      execute: function () {
        return json("/.well-known/api-catalog").then(function (cat) {
          var rows = cat.linkset
            .filter(function (e) { return e.anchor.indexOf("/data/") !== -1; })
            .map(function (e) {
              var via = e.via && e.via[0] ? e.via[0].href : "";
              return "- dataset: " + e.anchor + (via ? "\n  method: " + via : "");
            });
          return text(
            "Measurements with raw data (" + rows.length + "):\n" + rows.join("\n") +
            "\n\nNarrative index of everything published here: " + BASE + "/llms.txt"
          );
        });
      },
    },
    {
      name: "get_measurement_data",
      description:
        "Fetch one measurement dataset as JSON. Pass the dataset URL or filename " +
        "returned by list_measurements. Contains the measured values, the control " +
        "run and the conditions under which they were obtained.",
      inputSchema: {
        type: "object",
        properties: {
          dataset: {
            type: "string",
            description: "Dataset URL or bare filename, e.g. 2026-08-01-ocr-recall.json",
          },
        },
        required: ["dataset"],
        additionalProperties: false,
      },
      execute: function (args) {
        var d = String((args && args.dataset) || "");
        var path = d.indexOf("http") === 0
          ? d.replace(BASE, "")
          : "/data/" + d.replace(/^\/?(data\/)?/, "");
        return json(path).then(function (data) {
          return text(JSON.stringify(data, null, 2));
        });
      },
    },
    {
      name: "get_method",
      description:
        "Fetch a reproducible method published here as a skill: how to read a " +
        "browser extension's permissions, how to measure OCR recall with a control " +
        "run, or how to choose between print-to-PDF and screen capture. " +
        "Call without arguments to list the available methods.",
      inputSchema: {
        type: "object",
        properties: {
          name: {
            type: "string",
            description:
              "One of: check-extension-permissions, measure-ocr-recall, " +
              "compare-print-vs-capture. Omit to list them.",
          },
        },
        additionalProperties: false,
      },
      execute: function (args) {
        return json("/.well-known/agent-skills/index.json").then(function (idx) {
          var want = args && args.name;
          if (!want) {
            return text(idx.skills.map(function (s) {
              return "- " + s.name + ": " + s.description;
            }).join("\n"));
          }
          var hit = idx.skills.filter(function (s) { return s.name === want; })[0];
          if (!hit) {
            return text("No method named " + want + ". Available: " +
              idx.skills.map(function (s) { return s.name; }).join(", "));
          }
          return fetch(hit.url).then(function (r) { return r.text(); }).then(text);
        });
      },
    },
    /* The one tool here that is not about this site.
     *
     * It reaches the same /mcp endpoint an external client would call, from the
     * page rather than from a server — which costs one same-origin request and
     * keeps a single implementation of the extraction. An agent already reading
     * this page can therefore resolve a source without being told an address.
     *
     * The refusal path matters more than the success path: a page that turns out
     * to be a paywall still returns a title, so the warning is repeated at the
     * top of the answer where it cannot be skimmed past. */
    {
      name: "extract_citation",
      description:
        "Read the citation a web page declares about itself — authors, title, " +
        "journal, year, DOI, licence — and return it as a structured record with " +
        "a ready-to-import RIS entry and BibTeX. Where the page is a paywall, an " +
        "error page or a bot check rather than a work, it says so and refuses " +
        "instead of inventing a reference: check the warning before using the fields.",
      inputSchema: {
        type: "object",
        properties: {
          url: {
            type: "string",
            description: "Address of the page to read, e.g. https://doi.org/10.1038/s41586-020-2649-2",
          },
        },
        required: ["url"],
        additionalProperties: false,
      },
      execute: function (args) {
        var u = String((args && args.url) || "");
        if (!u) return Promise.resolve(text("No url given."));
        return fetch(BASE + "/mcp", {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            jsonrpc: "2.0", id: 1, method: "tools/call",
            params: { name: "extract_citation", arguments: { url: u } },
          }),
        }).then(function (r) {
          if (!r.ok) throw new Error("/mcp returned " + r.status);
          return r.json();
        }).then(function (d) {
          var body = d && d.result && d.result.content && d.result.content[0]
            ? d.result.content[0].text : JSON.stringify(d);
          var warn = "";
          try {
            var rec = JSON.parse(body);
            if (rec.warning) {
              warn = "NOT USABLE AS A REFERENCE — " + rec.warning +
                     "\nThe title below belongs to that wall, not to a work.\n\n";
            }
          } catch (e) { /* not JSON: hand it over unchanged */ }
          return text(warn + body);
        }).catch(function (e) {
          return text("Could not reach the citation endpoint: " + e.message);
        });
      },
    },
  ];

  function register(mc) {
    if (done || !mc) return;
    try {
      if (typeof mc.provideContext === "function") {
        mc.provideContext({ tools: TOOLS });
        done = true;
      } else if (typeof mc.registerTool === "function") {
        TOOLS.forEach(function (t) { mc.registerTool(t); });
        done = true;
      }
    } catch (e) {
      /* an implementation that rejects the shape is not an error worth raising */
    }
    if (done) {
      window.dispatchEvent(new CustomEvent("webmcp-tools-registered", {
        detail: { count: TOOLS.length },
      }));
    }
  }

  // Also expose the definitions plainly, so anything that inspects the page
  // rather than the API can see what is on offer.
  window.__webmcpTools = TOOLS.map(function (t) {
    return { name: t.name, description: t.description, inputSchema: t.inputSchema };
  });

  if (navigator.modelContext) {
    register(navigator.modelContext);
  } else {
    var late;
    try {
      Object.defineProperty(navigator, "modelContext", {
        configurable: true,
        enumerable: true,
        get: function () { return late; },
        set: function (v) { late = v; register(v); },
      });
    } catch (e) {
      /* non-configurable: the poll below covers it */
    }
    var tries = 0;
    var timer = setInterval(function () {
      if (done || ++tries > 40) { clearInterval(timer); return; }
      if (navigator.modelContext) { register(navigator.modelContext); clearInterval(timer); }
    }, 250);
  }
})();
