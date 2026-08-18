#!/usr/bin/env python3
"""The Knowledge review report — the publish-path half of SITE5's review control.

This module runs on every publish, so its failure mode is the one that matters: reporting
that nothing is due because it could not read anything. Every degenerate input below must
RAISE rather than write a clean-looking report.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from tools import generate_knowledge_review as gen

REAL_FEED = Path(__file__).resolve().parents[2] / "site" / "data" / "knowledge_wholesale.json"


def test_the_report_counts_every_topic():
    payload = gen.build(REAL_FEED)
    feed = json.loads(REAL_FEED.read_text(encoding="utf-8"))
    assert len(payload["topics"]) == len(feed["topics"])
    assert sum(payload["tally"].values()) == len(feed["topics"])


def test_pages_needing_attention_are_never_and_due_together():
    """A page nobody has ever reviewed misleads a reader exactly as much as one past its
    threshold. Counting only the second would report this section as almost fine."""
    payload = gen.build(REAL_FEED)
    assert gen.needs_attention(payload) == payload["tally"]["never"] + payload["tally"]["due"]


def test_the_worst_pages_sort_first():
    """An operator reads the top of the list. Never-reviewed, then due, then fresh."""
    order = {"never": 0, "due": 1, "fresh": 2}
    states = [order[t["state"]] for t in gen.build(REAL_FEED)["topics"]]
    assert states == sorted(states), states


def test_the_report_carries_its_stamp_and_names_the_rule():
    payload = gen.build(REAL_FEED)
    assert payload["generated_at"]
    assert payload["rule"] == "site/knowledge/review_state.py"
    assert payload["source"].endswith("knowledge_wholesale.json")
    assert payload["policy"], "the thresholds the verdicts rest on are not published"


@pytest.mark.parametrize("payload", ['{"topics": []}', "{}", "not json at all", "[]"])
def test_MUTATION_FAIL_OPEN_an_empty_or_broken_feed_raises(tmp_path, payload):
    bad = tmp_path / "feed.json"
    bad.write_text(payload, encoding="utf-8")
    with pytest.raises(gen.KnowledgeReviewUnavailable):
        gen.build(bad)


def test_MUTATION_FAIL_OPEN_a_missing_feed_raises(tmp_path):
    with pytest.raises(gen.KnowledgeReviewUnavailable):
        gen.build(tmp_path / "nope.json")


def test_MUTATION_a_topic_losing_its_review_record_reports_never(tmp_path):
    """The defect the report exists to surface, driven end to end."""
    feed = json.loads(REAL_FEED.read_text(encoding="utf-8"))
    for topic in feed["topics"]:
        topic["reviewed"] = {"last_verified": None}
    doctored = tmp_path / "feed.json"
    doctored.write_text(json.dumps(feed), encoding="utf-8")
    payload = gen.build(doctored)
    assert payload["tally"]["never"] == len(feed["topics"])
    assert payload["tally"]["fresh"] == 0
    assert gen.needs_attention(payload) == len(feed["topics"])


def test_MUTATION_a_report_that_wrote_nothing_is_not_a_pass(tmp_path):
    """generate() must not leave a file behind when the source is unreadable — a stale
    report read as current is the same lie in a different place."""
    out = tmp_path / "out.json"
    with pytest.raises(gen.KnowledgeReviewUnavailable):
        gen.generate(out=out, feed_path=tmp_path / "missing.json")
    assert not out.exists()
