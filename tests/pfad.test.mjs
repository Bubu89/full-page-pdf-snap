import { readFileSync } from "node:fs";
const s = readFileSync(new URL("../background.js", import.meta.url), "utf8");
const f = new Function(s.slice(s.indexOf("function pfadFormatieren("),
  s.indexOf("async function pfadInZwischenablage")) + "\n return pfadFormatieren;")();
const faelle = [
  [String.raw`C:\Users\HOLO\Downloads\seite.pdf`, "wsl",     "/mnt/c/Users/name/Downloads/seite.pdf"],
  [String.raw`C:\Users\HOLO\Downloads\seite.pdf`, "windows", String.raw`C:\Users\HOLO\Downloads\seite.pdf`],
  [String.raw`D:\Downloads\Full Page PDF Snap\x.pdf`, "wsl", "/mnt/d/Downloads/Full Page PDF Snap/x.pdf"],
  ["/home/name/Downloads/seite.pdf", "posix",             "/home/name/Downloads/seite.pdf"],
  ["/Users/x/Downloads/a.pdf", "wsl",                     "/Users/x/Downloads/a.pdf"],
];
let fehl = 0;
for (const [p, form, soll] of faelle) {
  const ist = f(p, form), ok = ist === soll;
  if (!ok) fehl++;
  console.log(`  ${ok ? "ok  " : "FEHL"} ${form.padEnd(8)} ${ist}`);
}
console.log(fehl ? `  ${fehl} fehlgeschlagen` : "  alle 5 Pfadumrechnungen stimmen");
