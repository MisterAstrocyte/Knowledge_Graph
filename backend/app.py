"""
Knowledge Graph backend (optional).

Two endpoints:
  GET  /api/graph        -> the graph as JSON {nodes, links}
  POST /api/ask {question}-> a natural-language answer about the graph (LLM)

Run locally:
  pip install -r requirements.txt
  export ANTHROPIC_API_KEY=sk-ant-...      # only needed for /api/ask
  uvicorn app:app --reload --port 8000

This is what the frontend's "dialog bar" would call. GitHub Pages CANNOT run
this file (Pages is static only) — deploy it to Render / Railway / Fly.io /
Cloud Run, then point the frontend at that URL.
"""
import csv
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

DATA_FILE = Path(__file__).parent.parent / "docs" / "data" / "graph.csv"

app = FastAPI(title="Knowledge Graph API")

# Allow the GitHub Pages site (and local dev) to call this API from the browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten to your Pages URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_rows():
    with open(DATA_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_graph(rows):
    nodes, seen = [], {}
    links = []
    for i, r in enumerate(rows):
        s, t = r.get("source", "").strip(), r.get("target", "").strip()
        if not s or not t:
            continue
        for name, grp in ((s, r.get("group_source", "")), (t, r.get("group_target", ""))):
            if name not in seen:
                seen[name] = {"id": name, "name": name, "group": (grp or "").strip()}
                nodes.append(seen[name])
        links.append({"id": f"e{i}", "source": s, "target": t,
                      "rel": (r.get("relationship") or "").strip()})
    return {"nodes": nodes, "links": links}


@app.get("/api/graph")
def graph():
    return build_graph(load_rows())


class Question(BaseModel):
    question: str


@app.post("/api/ask")
def ask(q: Question):
    rows = load_rows()
    triples = "\n".join(
        f"- {r['source']} {r.get('relationship','related to')} {r['target']}"
        for r in rows if r.get("source") and r.get("target")
    )
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return {"answer": "Set ANTHROPIC_API_KEY on the server to enable answers.",
                "facts": triples}
    # Lazy import so the server still starts without the SDK installed.
    import anthropic
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system="Answer questions using ONLY the knowledge-graph facts provided. "
               "If the facts do not contain the answer, say so.",
        messages=[{"role": "user",
                   "content": f"Facts:\n{triples}\n\nQuestion: {q.question}"}],
    )
    answer = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    return {"answer": answer}
