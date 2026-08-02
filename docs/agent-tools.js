/* WebMCP — exposes this site's data to an agent running in the browser.
 *
 * A reading site has no "actions" worth automating, so the tools here do the
 * one thing that is genuinely useful: hand over the measurement datasets and
 * the published methods directly, instead of making an agent scrape the pages
 * for numbers that already exist as JSON.
 *
 * Progressive: if navigator.modelContext is absent, nothing happens and no
 * error is raised. The API is a Chrome origin trial at the time of writing.
 * https://webmachinelearning.github.io/webmcp/
 */
(function () {
  "use strict";
  if (!navigator.modelContext || !navigator.modelContext.provideContext) return;

  var BASE = location.origin;

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

  navigator.modelContext.provideContext({
    tools: [
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
              return text(
                idx.skills.map(function (s) {
                  return "- " + s.name + ": " + s.description;
                }).join("\n")
              );
            }
            var hit = idx.skills.filter(function (s) { return s.name === want; })[0];
            if (!hit) {
              return text(
                "No method named " + want + ". Available: " +
                idx.skills.map(function (s) { return s.name; }).join(", ")
              );
            }
            return fetch(hit.url).then(function (r) { return r.text(); }).then(text);
          });
        },
      },
    ],
  });
})();
