# Knowledge Graph

An interactive **3D knowledge graph** of people and the transitions between them
(built for the vacation / bachelor-party calculation). Drag to orbit, scroll to
zoom, click a person to fly in and trace their connections.

- `docs/` — the frontend. Served by **GitHub Pages**. Pure HTML/CSS/JS, no build step.
- `docs/data/graph.csv` — the graph data. Edit this file to change the graph.
- `backend/` — optional API (graph data + LLM question answering). Source only;
  it is **not** run by GitHub Pages — deploy it separately (see `backend/README.md`).

Live site (after you enable Pages): **https://misterastrocyte.github.io/Knowledge_Graph/**

---

## 1. Put the files in the repo

Easiest (no command line): on the repo page click **Add file ▸ Upload files**,
drag in the whole folder structure (`docs/…`, `backend/…`, `README.md`,
`.gitignore`), then **Commit changes**.

With git:

```bash
git clone https://github.com/MisterAstrocyte/Knowledge_Graph.git
cd Knowledge_Graph
# copy these files in, then:
git add .
git commit -m "Add 3D knowledge graph frontend + backend"
git push
```

## 2. Turn on GitHub Pages

Repo **Settings ▸ Pages**:

- **Source:** Deploy from a branch
- **Branch:** `main`  ·  **Folder:** `/docs`
- **Save**

Wait ~1 minute. Your site goes live at
`https://misterastrocyte.github.io/Knowledge_Graph/`.
Because it is a real hosted page, the WebGL animation works (unlike pasting raw
code into Google Sites).

## 3. (Optional) Embed it in a Google Site

In your Google Site: **Insert ▸ Embed ▸ By URL**, paste the Pages URL above.
Non-technical viewers get the Google Site; the heavy 3D viewer is just an iframe
to GitHub Pages.

## 4. Change the data

Edit `docs/data/graph.csv`. One row per transition. Header columns:

| column          | meaning                                  | required |
|-----------------|------------------------------------------|----------|
| `source`        | person the relationship starts from      | yes      |
| `relationship`  | the label on the edge (e.g. "owes")      | no       |
| `target`        | person it points to                      | yes      |
| `group_source`  | role/category of source (colors the node)| no       |
| `group_target`  | role/category of target                  | no       |

Commit the change and Pages redeploys automatically.

You can also point the frontend at a **published Google Sheet** instead of the
repo file: open `docs/index.html`, find `CONFIG.sheetCsvUrl`, and paste the
Sheet's published-to-web CSV link.

## 5. (Optional) Add the backend

See `backend/README.md`. It powers a "ask a question about the graph" dialog and
can read a private Google Drive sheet. It must be hosted somewhere that runs code
(Render, Railway, Fly.io, Google Cloud Run) or as a Google Apps Script web app.
