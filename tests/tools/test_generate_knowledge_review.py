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


def test_the_two_counts_measure_different_things():
    """Director, 2026-08-18: a stub and a written-but-unchecked page must not be one number.
    `needs_attention` counts what could MISLEAD (a full argument nobody has checked, or
    checked too long ago); `unwritten` counts the WORK still to do. Writing a page moves a
    topic between them and reduces neither risk -- only a check does."""
    payload = gen.build(REAL_FEED)
    assert gen.needs_attention(payload) == payload["tally"]["unchecked"] + payload["tally"]["due"]
    assert gen.unwritten(payload) == payload["tally"]["stub"]
    # The two must not be the same number by accident: a stub is excluded from the risk
    # count, so a feed with stubs in it must show them differing.
    if payload["tally"]["stub"]:
        assert gen.needs_attention(payload) != sum(payload["tally"].values()) - payload["tally"]["fresh"]


def test_the_worst_pages_sort_first():
    """An operator reads the top of the list. A page past its threshold outranks a stub,
    because it makes a claim that has gone unchecked while a stub makes no claim at all."""
    order = {"due": 0, "unchecked": 1, "stub": 2, "fresh": 3}
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


def test_MUTATION_a_written_page_losing_its_check_reports_unchecked(tmp_path):
    """The defect the report exists to surface, driven end to end: a WRITTEN page whose check
    disappears must be reported as one a reader could be misled by -- not as a stub, and never
    as fresh."""
    feed = json.loads(REAL_FEED.read_text(encoding="utf-8"))
    written = [t for t in feed["topics"] if t.get("kind") == "page"]
    assert written, "fixture assumption broke: no written pages"
    for topic in feed["topics"]:
        topic["reviewed"] = {"last_verified": None}
    doctored = tmp_path / "feed.json"
    doctored.write_text(json.dumps(feed), encoding="utf-8")
    payload = gen.build(doctored)
    assert payload["tally"]["unchecked"] == len(written)
    assert payload["tally"]["fresh"] == 0
    assert gen.needs_attention(payload) == len(written)


def test_MUTATION_writing_a_page_does_not_reduce_the_risk_count(tmp_path):
    """The property the director asked to be made visible. Promoting a stub to a written page
    moves it OUT of `unwritten` and INTO `needs_attention`. If writing ever reduced the risk
    count, the section could be made to look verified by typing prose."""
    feed = json.loads(REAL_FEED.read_text(encoding="utf-8"))
    # Every real topic is now written, so the stub is synthesised. Requiring a real one would
    # make this control vanish exactly when the section finished being written -- which is
    # when a regression in it would be least likely to be noticed.
    stub = {"id": "_probe", "title": "probe", "kind": "stub", "rate_of_change": "slow",
            "reviewed": {"last_verified": None}}
    feed["topics"].append(stub)
    before = gen.build(_write(tmp_path / "a.json", feed))
    stub["kind"] = "page"
    stub["reviewed"] = {"last_verified": None, "written": "2026-08-18"}
    after = gen.build(_write(tmp_path / "b.json", feed))
    assert gen.unwritten(after) == gen.unwritten(before) - 1
    assert gen.needs_attention(after) == gen.needs_attention(before) + 1


def _write(path, payload):
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def test_MUTATION_a_report_that_wrote_nothing_is_not_a_pass(tmp_path):
    """generate() must not leave a file behind when the source is unreadable — a stale
    report read as current is the same lie in a different place."""
    out = tmp_path / "out.json"
    with pytest.raises(gen.KnowledgeReviewUnavailable):
        gen.generate(out=out, feed_path=tmp_path / "missing.json")
    assert not out.exists()
