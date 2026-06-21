# Backend (optional)

A tiny API for the knowledge graph. **GitHub Pages cannot run this** — it serves
static files only. Host it on a service that runs code, then point the frontend
at its URL.

## Endpoints
- `GET  /api/graph` — the graph as JSON (reads `../docs/data/graph.csv`)
- `POST /api/ask` `{ "question": "Who does Daniel owe?" }` — LLM answer over the graph

## Run locally
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...      # only needed for /api/ask
uvicorn app:app --reload --port 8000
# test: http://localhost:8000/api/graph
```

## Deploy (pick one)
- **Render / Railway / Fly.io**: start command `uvicorn app:app --host 0.0.0.0 --port $PORT`
- **Google Cloud Run**: containerize and deploy; set ANTHROPIC_API_KEY as a secret.

After deploying, in `docs/index.html` you can fetch `https://YOUR-BACKEND/api/graph`
instead of the local CSV, and wire a dialog box to `POST /api/ask`.

## Alternative: Google Apps Script (stays inside Google, reads private Drive)
See `apps_script/Code.gs`. Good if the data must live in a **private** Google
Sheet and you don't want to run a server.
