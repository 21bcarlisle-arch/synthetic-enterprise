"""The insight rows a reader should challenge next, and the brief they challenge them against.

Director, 4 Nov (Ask 5 of the knowledge-and-insight steer): "Every insight carries a review date.
The cold reader, or an independent reader, challenges insights as well as figures. A refuted
insight stays visible, marked refuted, with what refuted it."

Every insight row in `site/data/knowledge_facets.json` carries `falsified_by` and `review_by`.
This reads them. `--due` lists the rows whose review date falls within the window, earliest
first. `--brief` writes those rows as a brief for a reader who sees only the published pages and
the published record, never our code or runs. The brief asks the reader to look for the evidence
the row itself says would show it wrong, and to say "cannot tell" when it finds neither.

A refuted row is not re-challenged: it stays on the site with what refuted it. A row with no
`review_by` counts as due now, since it has never been given a date.

The reader's verdict goes back into the record by hand, beside the row: `status`, `checked`,
a new `review_by`, and, for a refutation, `falsified_by` rewritten to say what refuted it.

    python3 -m tools.insight_challenge --due [--within 30] [--as-of 2026-11-04]
    python3 -m tools.insight_challenge --brief <out.md> [--within 30]

REUSE: tools/insight_challenge.py
CLASS: CUSTOM
INDEX: searched "insight challenge", "review_by", "cold reader brief". The index returned
       `tools/blind_review.py`: it builds a blind packet from a capability's plain words and gets
       back a practitioner battery. It has no claim, falsifier or review date, so it cannot select
       rows by date; its whitelisted packet is the pattern the brief follows. `tools/blind_worktree.py`
       builds the cold reader's tree for a book; it has no brief and no insight rows. The site's
       `layer_marks.js` and what-we-think.html show `review_by` but select nothing for review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FACETS = ROOT / "site" / "data" / "knowledge_facets.json"
SITE_URL = "https://poesys.net/knowledge/"


def due(facets: dict, as_of: dt.date, within_days: int) -> list[dict]:
    """Rows not refuted whose `review_by` is on or before `as_of` + `within_days`, earliest first."""
    horizon = (as_of + dt.timedelta(days=within_days)).isoformat()
    rows = [dict(r, page=slug) for slug, p in facets["pages"].items() for r in p.get("insights", [])
            if r.get("status") != "refuted" and (r.get("review_by") or "") <= horizon]
    return sorted(rows, key=lambda r: (r.get("review_by") or "", r["page"]))


def brief(rows: list[dict], as_of: dt.date) -> str:
    out = [
        f"# Challenge these {len(rows)} insights (brief written {as_of.isoformat()})",
        "",
        "Each row below is our own interpretation, not an outside fact. It is published on the page",
        "named, with what it rests on and what would show it wrong. Read only the published page and",
        "the published record (regulators, statistics, research, news). Do not read our code or runs.",
        "",
        "For each row:",
        "1. Look for the evidence named under *Would be shown wrong by*, and for anything else that",
        "   contradicts the claim.",
        "2. Return one verdict: **held** (you looked and found support, no contradiction),",
        "   **contested** (credible evidence on both sides), **refuted** (the falsifier is met), or",
        "   **cannot tell** (you found neither). Do not upgrade a guess to held.",
        "3. Name each source you rely on, with its date and a link.",
        "",
    ]
    for i, r in enumerate(rows, 1):
        out += [
            f"## {i}. {r['claim']}",
            "",
            f"- **Page:** {SITE_URL}{r['page']}/ (section: {r.get('section', '')})",
            f"- **Status now:** {r.get('status')}"
            + (" (drawn from our own simulation)" if r.get("from_sim") else ""),
            f"- **Rests on:** {'; '.join(r.get('rests_on') or []) or 'nothing named'}",
            f"- **Would be shown wrong by:** {r.get('falsified_by') or 'nothing named'}",
            f"- **Last checked:** {r.get('checked') or 'never'} · **review by:** {r.get('review_by') or 'none set'}",
            "",
        ]
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--due", action="store_true", help="list the rows due for challenge")
    ap.add_argument("--brief", type=Path, help="write the challenge brief for the due rows here")
    ap.add_argument("--within", type=int, default=30, help="days ahead of --as-of (default 30)")
    ap.add_argument("--as-of", type=dt.date.fromisoformat, default=dt.date.today())
    a = ap.parse_args(argv)
    rows = due(json.loads(FACETS.read_text(encoding="utf-8")), a.as_of, a.within)
    if a.brief:
        a.brief.write_text(brief(rows, a.as_of) + "\n", encoding="utf-8")
        print(f"insight-challenge: {len(rows)} rows written to {a.brief}")
    if a.due or not a.brief:
        for r in rows:
            print(f"{r.get('review_by') or 'no date':10}  {r['status']:10}  {r['page']}: {r['claim'][:90]}")
        print(f"insight-challenge: {len(rows)} rows due by {a.as_of + dt.timedelta(days=a.within)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
