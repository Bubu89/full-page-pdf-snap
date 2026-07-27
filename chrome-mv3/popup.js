"use strict";

const $ = id => document.getElementById(id);

$("go").addEventListener("click", async () => {
  const status = $("status");
  status.className = "status";
  status.textContent = "Erfasse Seite ...";
  $("go").disabled = true;

  try {
    const res = await browser.runtime.sendMessage({ cmd: "capture" });
    if (res && res.ok) {
      status.className = "status ok";
      status.textContent = `Gespeichert (${res.result.pages} Seiten)`;
      setTimeout(() => window.close(), 800);
    } else {
      status.className = "status err";
      status.textContent = (res && res.error) || "Unbekannter Fehler";
    }
  } catch (e) {
    status.className = "status err";
    status.textContent = e.message || String(e);
  } finally {
    $("go").disabled = false;
  }
});

$("opts").addEventListener("click", () => {
  browser.runtime.openOptionsPage();
  window.close();
});
