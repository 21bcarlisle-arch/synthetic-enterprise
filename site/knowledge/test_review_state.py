#!/usr/bin/env python3
"""The review-due control (SITE5, structural half).

THE REQUIREMENT, brief §4: "Every page carries a last-reviewed date, and flips to a visible
'review due' state past a threshold. Staleness must be visible on the page, not discovered by
a reader." And §7: "A knowledge page past its review threshold renders as review-due rather
than silently stale."

The named defect this control must fire on is therefore precise: **a page that is past its
threshold and does not say so.** Every mutation below drives that, or the fail-open beneath
it.

TWO IMPLEMENTATIONS, ON PURPOSE, AND THE COST PAID FOR IT. The rule lives in
`review_state.py` and is mirrored in JavaScript inside `_stub/index.html`, because these
pages have no build step and a reader must see the state on first paint rather than after a
generator runs. Two copies of one rule is a drift risk, so the drift is what is tested:
`test_the_javascript_mirror_agrees_with_python_on_every_topic` and the boundary tests drive
BOTH and require identical verdicts, including on the days either side of every threshold.
If they ever disagree, this file goes red rather than the page going quietly wrong.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SITE = HERE.parent
FEED = SITE / "data" / "knowledge_wholesale.json"
# MOVED, 2026-08-20. This read site/knowledge/_stub/index.html; that template was being
# DEPLOYED to the live site, so it moved out of the published tree rather than being deleted --
# it is still the one carrier of the JavaScript mirror this file grades, and deleting it would
# have retired a real control by accident.
STUB_TEMPLATE = HERE.parent.parent / "docs" / "site_templates" / "knowledge" / "_stub.html"

sys.path.insert(0, str(HERE))

from review_state import (  # noqa: E402
    DUE, FRESH, STUB, UNCHECKED, review_state, states_for, threshold_days)


@pytest.fixture(scope="module")
def feed() -> dict:
    return json.loads(FEED.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# The record carries what the control needs
# ---------------------------------------------------------------------------
def test_every_topic_carries_a_review_record(feed):
    for topic in feed["topics"]:
        assert "reviewed" in topic, f"{topic['id']} has no review record at all"
        assert "last_verified" in topic["reviewed"], topic["id"]
        assert topic.get("rate_of_change") in feed["review_policy"]["threshold_days"], (
            f"{topic['id']} has rate_of_change {topic.get('rate_of_change')!r}, which has no threshold"
        )


def test_the_policy_states_a_reason_for_each_threshold(feed):
    """A threshold with no reason is a number someone picked. Each class says why it is that
    long, so the next person can argue with the reasoning rather than the digit."""
    policy = feed["review_policy"]
    for cls in policy["threshold_days"]:
        assert policy["why"].get(cls), f"threshold class {cls!r} has no stated reason"


def test_the_thresholds_differ_by_how_fast_the_subject_moves(feed):
    """Ofgem resets the cap quarterly; the merit order is structural. One global threshold
    would either nag about the second or stay silent about the first."""
    days = feed["review_policy"]["threshold_days"]
    assert days["fast"] < days["medium"] < days["slow"], days
    by_id = {t["id"]: t for t in feed["topics"]}
    assert by_id["price-cap"]["rate_of_change"] == "fast", (
        "the price cap is reset quarterly by the regulator; a slower class would let a "
        "wrong page sit unflagged for a year"
    )


# ---------------------------------------------------------------------------
# The state itself
# ---------------------------------------------------------------------------
def test_an_unchecked_page_is_never_fresh(feed):
    """THE fail-open. If 'no recorded check' read as 'fine', this control would be decorative
    and the section would look maintained precisely because nobody had maintained it. The
    unchecked state now splits in two -- STUB for a page that makes no claim, UNCHECKED for a
    written one nobody has verified -- and NEITHER may read fresh."""
    for topic in feed["topics"]:
        state = review_state(topic, feed["review_policy"])
        if not topic["reviewed"]["last_verified"]:
            assert state["state"] in (STUB, UNCHECKED), (topic["id"], state["state"])
            assert state["state"] != FRESH, topic["id"]


def test_a_written_page_with_no_check_is_unchecked_not_a_stub(feed):
    """The distinction the director asked for, driven on the real record: a written page that
    nobody has checked must not hide among the stubs, because it makes a full argument."""
    written_unchecked = [t["id"] for t in feed["topics"]
                         if t.get("kind") == "page" and not t["reviewed"]["last_verified"]]
    for tid in written_unchecked:
        topic = next(t for t in feed["topics"] if t["id"] == tid)
        assert review_state(topic, feed["review_policy"])["state"] == UNCHECKED, tid


@pytest.mark.parametrize("bad", [None, "", "not-a-date", "2026-13-45", 20260725, {}, []])
def test_MUTATION_FAIL_OPEN_an_unparseable_date_is_never_fresh(bad):
    state = review_state({"rate_of_change": "slow", "reviewed": {"last_verified": bad}},
                         {"threshold_days": {"slow": 365}})
    assert state["state"] in (STUB, UNCHECKED), f"{bad!r} read as {state['state']}"
    assert state["state"] != FRESH


def test_MUTATION_FAIL_OPEN_a_missing_policy_uses_the_tightest_threshold():
    """Guessing generously is how a fail-open arrives by accident."""
    assert threshold_days("slow", None) == 92
    assert threshold_days("unknown-class", {"threshold_days": {"slow": 365}}) == 92


def test_MUTATION_a_page_past_its_threshold_renders_review_due(feed):
    """The brief's own named defect: 'a knowledge page past its review threshold renders as
    review-due rather than silently stale'."""
    topic = {"id": "x", "rate_of_change": "fast",
             "reviewed": {"last_verified": "2026-01-01"}}
    policy = feed["review_policy"]
    just_past = date(2026, 1, 1) + timedelta(days=policy["threshold_days"]["fast"] + 1)
    state = review_state(topic, policy, today=just_past)
    assert state["state"] == DUE
    assert state["label"] == "Review due"
    assert state["overdue_by"] == 1


def test_the_boundary_is_exact_and_does_not_fire_a_day_early(feed):
    """A control that fires early gets muted. Asserted on both sides of the line."""
    policy = feed["review_policy"]
    for cls, days in policy["threshold_days"].items():
        topic = {"rate_of_change": cls, "reviewed": {"last_verified": "2026-01-01"}}
        on_the_day = date(2026, 1, 1) + timedelta(days=days)
        assert review_state(topic, policy, today=on_the_day)["state"] == FRESH, cls
        assert review_state(topic, policy, today=on_the_day + timedelta(days=1))["state"] == DUE, cls


def test_no_review_date_exists_without_evidence_of_the_check(feed):
    """SITE5 (2026-08-18): this pinned the review-date set to exactly
    ["electricity-wholesale"], which was right while that was the only checked page and wrong
    the moment a second page was genuinely checked -- the director checked the price cap
    against Ofgem the same day. The count was never the invariant. The invariant is that a
    date cannot be typed in without saying WHAT was checked against, which is what stops the
    section being made to look reviewed by editing a field.
    """
    by_id = {t["id"]: t for t in feed["topics"]}
    assert by_id["electricity-wholesale"]["reviewed"]["last_verified"] == \
        feed["meta"]["claim_freshness"]["last_verified"], "the deep page's own record moved"

    for topic in feed["topics"]:
        rec = topic["reviewed"]
        if not rec.get("last_verified"):
            continue
        assert rec.get("source"), (
            f"{topic['id']} carries a review date with no source -- a date nobody can trace "
            "is not evidence of a check"
        )


def test_a_check_records_how_it_was_done_where_the_route_is_not_obvious(feed):
    """The price cap could not be checked by this project's own tooling: Ofgem's pages render
    with JavaScript and return only navigation to an automated fetch. The route that DID work
    -- a person reading it in a browser -- is recorded, because the next person to re-check it
    in 92 days will otherwise repeat the dead end."""
    by_id = {t["id"]: t for t in feed["topics"]}
    rec = by_id["price-cap"]["reviewed"]
    assert rec["last_verified"], "the price cap check is not recorded"
    assert rec.get("route"), "the checking route is not recorded"
    assert rec.get("claims_checked"), "no claim is named as checked -- 'verified' means what?"
    assert len(rec["claims_checked"]) >= 2


def test_MUTATION_a_review_date_with_no_source_fires(feed):
    """The defect the control exists for: making the section look reviewed by typing a date."""
    doctored = [dict(t) for t in feed["topics"]]
    doctored[0] = dict(doctored[0], reviewed={"last_verified": "2026-08-18"})
    offenders = [t["id"] for t in doctored
                 if t["reviewed"].get("last_verified") and not t["reviewed"].get("source")]
    assert offenders, "a bare date passed the check"


# ---------------------------------------------------------------------------
# The page shows it — and the two implementations agree
# ---------------------------------------------------------------------------
def _js_state(topic_id: str, feed: dict, today_iso: str) -> dict:
    """Drive the PAGE's own JavaScript rule, not a re-implementation of it."""
    js = STUB_TEMPLATE.read_text(encoding="utf-8")
    start = js.index("function reviewState(")
    end = js.index("function renderReview(")
    script = js[start:end]
    runner = script + f"""
const feed = {json.dumps(feed)};
const topic = feed.topics.find(t => t.id === {json.dumps(topic_id)});
const out = reviewState(topic, feed.review_policy, new Date({json.dumps(today_iso)} + "T00:00:00Z"));
console.log(JSON.stringify(out));
"""
    proc = subprocess.run(["node", "--input-type=module", "-e", runner],
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0, proc.stderr[:400]
    return json.loads(proc.stdout)


def test_the_page_renders_a_review_state_element():
    html = STUB_TEMPLATE.read_text(encoding="utf-8")
    assert 'id="review-state"' in html, "the page has nowhere to show staleness"
    assert "renderReview(" in html, "the review state is never rendered"


def test_the_javascript_mirror_agrees_with_python_on_every_topic(feed):
    today = date.today()
    py = states_for(feed, today)
    for topic in feed["topics"]:
        js = _js_state(topic["id"], feed, today.isoformat())
        assert js["state"] == py[topic["id"]]["state"], (
            f"{topic['id']}: page says {js['state']}, control says {py[topic['id']]['state']}"
        )


def test_the_javascript_mirror_agrees_on_every_threshold_boundary(feed):
    """Where a drift would actually hide: one implementation using >= and the other >."""
    policy = feed["review_policy"]
    by_id = {t["id"]: t for t in feed["topics"]}
    probe = dict(by_id["electricity-wholesale"])
    probe["reviewed"] = {"last_verified": "2026-01-01", "source": None}
    for cls, days in policy["threshold_days"].items():
        probe["rate_of_change"] = cls
        doctored = dict(feed, topics=[probe])
        for offset in (days - 1, days, days + 1):
            when = (date(2026, 1, 1) + timedelta(days=offset)).isoformat()
            js = _js_state(probe["id"], doctored, when)
            py = review_state(probe, policy, today=date.fromisoformat(when))
            assert js["state"] == py["state"], f"{cls} at +{offset}d: page {js['state']} vs control {py['state']}"


def test_MUTATION_the_javascript_fail_open_is_closed_too(feed):
    """The mirror must fail closed on the same inputs the Python does. A page that renders
    'fine' on a missing date is the exact failure this whole control exists to prevent."""
    probe = {"id": "probe", "title": "probe", "rate_of_change": "slow",
             "reviewed": {"last_verified": None}}
    doctored = dict(feed, topics=[probe])
    js = _js_state("probe", doctored, date.today().isoformat())
    assert js["state"] in ("stub", "unchecked"), js
