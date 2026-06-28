"""
Fetches the JGA Google Sheet, computes minimum debt-settlement transactions,
and writes the result to docs/data/graph.csv.

Run locally:   python backend/sync_graph.py
Run via CI:    triggered by .github/workflows/sync_sheet.yml
"""
import csv
import io
import math
import urllib.request
from pathlib import Path

SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "11CZBFL9jqI7fOmSSI1GF4gW1WFRRLN7iKnqspHbHS9g"
    "/export?format=csv&gid=0"
)
OUTPUT = Path(__file__).parent.parent / "docs" / "data" / "graph.csv"
EPS = 0.005


# ── helpers ──────────────────────────────────────────────────────────────────

def parse_german_float(s: str) -> float:
    s = (s or "").strip()
    if not s:
        return math.nan
    return float(s.replace(".", "").replace(",", "."))


def r2(x: float) -> float:
    return round(x, 2)


# ── fetch & parse ─────────────────────────────────────────────────────────────

def fetch_balances() -> list[dict]:
    with urllib.request.urlopen(SHEET_URL) as resp:
        text = resp.read().decode("utf-8")

    reader = csv.reader(io.StringIO(text))
    rows = list(reader)
    if not rows:
        raise ValueError("Empty response from Google Sheet")

    head = [h.strip().lower() for h in rows[0]]
    i_rest = next((i for i, h in enumerate(head) if "restbetrag" in h), -1)
    if i_rest == -1:
        raise ValueError("No 'Restbetrag' column in sheet")

    people = []
    for row in rows[1:]:
        name = row[0].strip() if row else ""
        if not name:
            continue
        raw = row[i_rest].strip() if len(row) > i_rest else ""
        balance = parse_german_float(raw)
        if not math.isnan(balance):
            people.append({"name": name, "balance": balance})
    return people


# ── debt settlement ───────────────────────────────────────────────────────────

def settle_debts(people: list[dict]) -> list[dict]:
    """
    Two-phase minimum-transaction algorithm.

    Phase 1 – each debtor makes exactly one payment (smallest debtors first).
               This ensures every person with a non-zero balance appears in
               the graph even when total debts > total credits (incomplete data).

    Phase 2 – standard greedy for any residual credit capacity.
               Kicks in when the data is fully balanced (all bills entered).
    """
    creditors = sorted(
        [{"name": p["name"], "balance": p["balance"]} for p in people if p["balance"] > EPS],
        key=lambda x: x["balance"],          # ascending
    )
    debtors = sorted(
        [{"name": p["name"], "balance": -p["balance"]} for p in people if p["balance"] < -EPS],
        key=lambda x: x["balance"],          # ascending
    )
    if not creditors or not debtors:
        return []

    txns: list[dict] = []
    done: set[str] = set()

    # Phase 1
    for cred in creditors:
        for debt in debtors:
            if debt["name"] in done or debt["balance"] < EPS or cred["balance"] < EPS:
                continue
            amt = r2(min(debt["balance"], cred["balance"]))
            if amt < EPS:
                continue
            txns.append({
                "source":       debt["name"],
                "relationship": f"zahlt {amt:.2f}€",
                "group_source": "Schuldner",
                "target":       cred["name"],
                "group_target": "Gläubiger",
            })
            debt["balance"] = r2(debt["balance"] - amt)
            cred["balance"] = r2(cred["balance"] - amt)
            done.add(debt["name"])

    # Phase 2
    rc = sorted([c for c in creditors if c["balance"] > EPS], key=lambda x: -x["balance"])
    rd = sorted([d for d in debtors   if d["balance"] > EPS], key=lambda x: -x["balance"])
    ci = di = 0
    while ci < len(rc) and di < len(rd):
        amt = r2(min(rc[ci]["balance"], rd[di]["balance"]))
        if amt > EPS:
            txns.append({
                "source":       rd[di]["name"],
                "relationship": f"zahlt {amt:.2f}€",
                "group_source": "Schuldner",
                "target":       rc[ci]["name"],
                "group_target": "Gläubiger",
            })
        rc[ci]["balance"] = r2(rc[ci]["balance"] - amt)
        rd[di]["balance"] = r2(rd[di]["balance"] - amt)
        if rc[ci]["balance"] < EPS:
            ci += 1
        if rd[di]["balance"] < EPS:
            di += 1

    return txns


# ── write CSV ─────────────────────────────────────────────────────────────────

FIELDS = ["source", "relationship", "group_source", "target", "group_target"]


def write_csv(txns: list[dict]) -> None:
    with open(OUTPUT, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(txns)


# ── main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    people = fetch_balances()
    print(f"Fetched {len(people)} people from sheet")
    txns = settle_debts(people)
    print(f"Computed {len(txns)} minimum transactions")
    write_csv(txns)
    print(f"Written to {OUTPUT}")
    for t in txns:
        print(f"  {t['source']} → {t['target']}: {t['relationship']}")
