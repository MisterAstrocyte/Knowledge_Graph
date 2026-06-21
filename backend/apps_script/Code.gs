/**
 * Google Apps Script web app — reads a PRIVATE Google Sheet on your Drive and
 * returns the graph as JSON. Stays entirely inside Google (no server to host).
 *
 * Setup:
 *   1. script.google.com -> New project -> paste this in.
 *   2. Put your Sheet ID below (the long string in the sheet URL).
 *   3. Deploy -> New deployment -> type "Web app"
 *        Execute as: Me
 *        Who has access: Anyone
 *   4. Copy the /exec URL. In docs/index.html set CONFIG.sheetCsvUrl to it,
 *      OR fetch it as JSON from your dialog/frontend.
 *
 * Sheet layout: first row headers -> source | relationship | target | group_source | group_target
 */
const SHEET_ID = "PASTE_YOUR_SHEET_ID_HERE";
const TAB_NAME = "Sheet1";

function doGet() {
  const rows = SpreadsheetApp.openById(SHEET_ID).getSheetByName(TAB_NAME).getDataValues();
  const head = rows.shift().map(h => String(h).trim().toLowerCase());
  const col = name => head.indexOf(name);
  const iS = col("source"), iT = col("target"), iR = col("relationship");
  const iGS = col("group_source"), iGT = col("group_target");

  const nodes = {}, links = [];
  rows.forEach((r, k) => {
    const s = String(r[iS] || "").trim(), t = String(r[iT] || "").trim();
    if (!s || !t) return;
    const add = (n, g) => { if (!nodes[n]) nodes[n] = { id: n, name: n, group: g }; };
    add(s, iGS > -1 ? String(r[iGS] || "").trim() : "");
    add(t, iGT > -1 ? String(r[iGT] || "").trim() : "");
    links.push({ id: "e" + k, source: s, target: t,
                 rel: iR > -1 ? String(r[iR] || "").trim() : "" });
  });

  return ContentService
    .createTextOutput(JSON.stringify({ nodes: Object.values(nodes), links }))
    .setMimeType(ContentService.MimeType.JSON);
}
