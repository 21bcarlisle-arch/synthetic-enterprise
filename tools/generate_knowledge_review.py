#!/usr/bin/env python3
"""Publish which Knowledge pages are due for review — `site/data/knowledge_review.json`.

WHY THIS EXISTS RATHER THAN THE RULE SITTING IN A TEST. `site/knowledge/review_state.py`
holds the review rule, and the orphan ratchet refused its first landing for a good reason:
nothing that runs imported it. A rule exercised only by its own test is the no-caller class —
it looks like a mechanism and behaves like a document.

So the rule now produces something. Each publish computes the review state of every Knowledge
topic and writes it here, which gives three things a test cannot:

  * an OPERATOR signal — the publish log says how many pages are due, so staleness surfaces
    without anyone opening the site;
  * a feed the Knowledge index can render, so a reader sees which pages are stale before
    clicking into one (SITE6's job, and this is the input it will need);
  * a dated artefact, so "nothing was due" is a claim with a timestamp behind it rather than
    an absence of evidence.

The topic pages themselves do NOT read this file. They compute the state in their own
JavaScript against the reader's clock, because a page must show staleness on first paint and
because a state frozen at publish time is exactly the fail-open this control exists to
prevent — if publishing stopped, a stale page would go on reporting itself fresh.
`site/knowledge/test_review_state.py` drives both implementations and requires them to agree
on every topic and on the days either side of every threshold.

FAIL-CLOSED: an unreadable or empty feed raises rather than writing an empty report. A report
saying "no pages are due" because it could not read any pages is worse than no report.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
SITE = PROJECT / "site"
KNOWLEDGE = SITE / "knowledge"
if str(KNOWLEDGE) not in sys.path:
    sys.path.insert(0, str(KNOWLEDGE))

from review_state import DUE, FRESH, STUB, UNCHECKED, states_for  # noqa: E402

FEED = SITE / "data" / "knowledge_wholesale.json"
OUT = SITE / "data" / "knowledge_review.json"


class KnowledgeReviewUnavailable(RuntimeError):
    """The source could not be read. NOT an empty report."""


def build(feed_path: Path = FEED) -> dict:
    try:
        feed = json.loads(feed_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        raise KnowledgeReviewUnavailable(f"knowledge feed unreadable: {e}") from e
    # A JSON array parses perfectly well and is not a feed. Caught by this module's own
    # mutation test, which drove `[]` and got an AttributeError instead of the typed
    # failure -- a shape that reaches the publish path as an unhandled crash rather than a
    # named one, and tells whoever reads the log nothing about what was wrong.
    if not isinstance(feed, dict):
        raise KnowledgeReviewUnavailable(
            f"knowledge feed is a {type(feed).__name__}, not an object"
        )
    if not feed.get("topics"):
        raise KnowledgeReviewUnavailable("knowledge feed carries no topics")

    states = states_for(feed)
    by_id = {t["id"]: t for t in feed["topics"]}
    rows = [
        {"id": tid, "title": by_id[tid].get("title", tid),
         "rate_of_change": by_id[tid].get("rate_of_change"), **state}
        for tid, state in states.items()
    ]
    # Worst first, and "worst" is DUE rather than STUB: a page past its threshold makes a
    # claim that has gone unchecked, while a stub makes no claim at all.
    rows.sort(key=lambda r: ({DUE: 0, UNCHECKED: 1, STUB: 2, FRESH: 3}.get(r["state"], 4), r["id"]))
    return {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "source": "site/data/knowledge_wholesale.json",
        "rule": "site/knowledge/review_state.py",
        "policy": feed.get("review_policy"),
        "tally": {s: sum(1 for r in rows if r["state"] == s)
                  for s in (DUE, UNCHECKED, STUB, FRESH)},
        "topics": rows,
    }


def generate(out: Path = OUT, feed_path: Path = FEED) -> dict:
    payload = build(feed_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def needs_attention(payload: dict) -> int:
    """Pages a reader could be MISLED by: they make a full argument that nobody has checked,
    or checked too long ago.

    A stub is deliberately excluded. It declares on its own face that it is not written, so
    it makes no claim to distrust -- counting it here would mix the section's honest half in
    with its risky half and move both together.
    """
    return payload["tally"].get(UNCHECKED, 0) + payload["tally"].get(DUE, 0)


def unwritten(payload: dict) -> int:
    """Topics with no page yet. This is the section's WORK list, and it is a different number
    from the one above -- which is the point. Writing a page moves a topic out of this count
    and into `unchecked`; only a check against the source moves it any further."""
    return payload["tally"].get(STUB, 0)


if __name__ == "__main__":  # pragma: no cover - operator convenience
    p = generate()
    print(f"wrote {OUT.relative_to(PROJECT)}: {p['tally']} — "
          f"{needs_attention(p)} could mislead a reader, {unwritten(p)} not written yet")
