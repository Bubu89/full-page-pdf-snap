/* Prueft isSideNavigation: Welche fixed/sticky-Elemente sind Navigation
   (bleiben im ersten Segment stehen) und welche sind Stoerer (fliegen raus)?
   Geometrie aus echten Seiten. */
const winW = 1384, winH = 805;
function isSideNavigation(r) {
  const tall = r.height >= winH * 0.5;
  const narrow = r.width <= winW * 0.4;
  const edge = Math.max(12, winW * 0.05);
  const atEdge = r.left <= edge || r.right >= winW - edge;
  return tall && narrow && atEdge;
}
const R = [];
const check = (name, rect, want) => {
  const got = isSideNavigation({ ...rect, right: rect.left + rect.width });
  R.push(`${got === want ? "OK  " : "FEHL"}  ${want ? "behalten  " : "ausblenden"}  ${name}`);
  return got === want;
};

// Aus kimi.com/code/docs gemessen
check("VitePress Sidebar links (272x805 @0)",      {left:0,    width:272,  height:805}, true);
check("VitePress Inhaltsverz. rechts (224x805)",   {left:1113, width:224,  height:805}, true);
check("VitePress Sticky-Kopfzeile (1369x64)",      {left:0,    width:1369, height:64},  false);
check("VitePress Curtain (257x64)",                {left:0,    width:257,  height:64},  false);
check("VitePress Aside-Curtain (224x32)",          {left:1113, width:224,  height:32},  false);

// Typische Stoerer anderer Seiten
check("Cookie-Banner unten (1384x180)",            {left:0,    width:1384, height:180}, false);
check("Chat-Blase rechts unten (64x64)",           {left:1300, width:64,   height:64},  false);
check("Newsletter-Overlay mittig (600x400)",       {left:392,  width:600,  height:400}, false);
check("Schwebender Zurueck-Button (48x48)",        {left:20,   width:48,   height:48},  false);
// Grenzfaelle
check("Schmale Navi mit Aussenabstand (200x700)",  {left:40,   width:200,  height:700}, true);
check("Halbhohe Spalte am Rand (200x300)",         {left:0,    width:200,  height:300}, false);
check("Breite Spalte am Rand (700x805)",           {left:0,    width:700,  height:805}, false);

console.log(R.join("\n"));
console.log("\nERGEBNIS: " + (R.some(l => l.startsWith("FEHL")) ? "FEHLER" : "ALLE BESTANDEN"));
