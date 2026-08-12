"""Tests for tools/model_tier_report.py — the tiering pilot's measurement (2026-08-12).

R15 applies to a measurement the same way it applies to a control: "where a control can't be
mutation-tested, OUTCOME-test — no verdict-organ escapes measurement". The specific failure this
file guards against is the one that would make the whole pilot dishonest: a report that says
nothing is wrong because it is not looking. So the assertions below are mostly about the report
REFUSING to imply safety — reporting zero Sonnet ticks as "no comparison possible" rather than as
"no harm found", and keeping unattributable commits visible instead of folding them into a tier.
"""
from __future__ import annotations

import json

import pytest

from tools import model_tier_report as rep


def _write_log(path, rows):
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")


def test_no_decisions_reports_absence_not_success(tmp_path, monkeypatch):
    """An empty log must not render as a clean bill of health."""
    monkeypatch.setattr(rep, "TIER_LOG", tmp_path / "empty.jsonl")
    r = rep.build_report()
    assert r["decisions"] == 0
    assert "not spawned" in r["note"]
    assert "no tier decisions" in rep.render(r)


def test_zero_sonnet_ticks_renders_as_no_comparison_possible(tmp_path, monkeypatch):
    """THE HONESTY ASSERTION. If the pilot never fired, the report must say the comparison is
    impossible — not print empty Sonnet rows that read as 'Sonnet caused no problems'."""
    log = tmp_path / "t.jsonl"
    _write_log(log, [{"ts": 1786500000, "tier": "opus", "classes": ["level_move"]}])
    monkeypatch.setattr(rep, "TIER_LOG", log)
    out = rep.render(rep.build_report(window_all=True, now=1786500600))
    assert "has not fired yet" in out
    assert "never an absence of harm" in out


def test_a_torn_append_loses_one_sample_and_does_not_crash(tmp_path, monkeypatch):
    log = tmp_path / "t.jsonl"
    log.write_text(
        json.dumps({"ts": 1786500000, "tier": "opus", "classes": []}) + "\n"
        + '{"ts": 1786500100, "tier": "sonn'  # torn mid-write
        + "\n" + json.dumps({"ts": 1786500200, "tier": "sonnet", "classes": ["site_surface"]}) + "\n"
    )
    monkeypatch.setattr(rep, "TIER_LOG", log)
    r = rep.build_report(window_all=True, now=1786500900)
    assert r["decisions"] == 2


def test_intervals_do_not_overlap_and_the_last_is_flagged_open_ended():
    """Attribution rests on invocations not overlapping (Type=oneshot blocks the tick). If the
    interval maths ever double-counts a commit, every rate in the report is inflated."""
    decisions = [{"ts": 100, "tier": "opus"}, {"ts": 200, "tier": "sonnet"}, {"ts": 300, "tier": "opus"}]
    ivs = rep._intervals(decisions, now=400)
    assert [(i.ts, i.end) for i in ivs] == [(100, 200), (200, 300), (300, 400)]
    assert [i.open_ended for i in ivs] == [False, False, True]
    assert rep.render(rep.build_report.__wrapped__ if False else {  # render's flag path
        "decisions": 3, "window": {"from": "a", "to": "b"}, "commits_attributed": 0,
        "commits_unattributable": 0, "ticks_by_tier": {"opus": 2, "sonnet": 1},
        "ticks_by_tier_and_class": {}, "rework": {}, "findings_raised": {}, "gate_failures": {},
        "open_ended_interval": True,
    }).count("open-ended") == 1


def test_rework_reports_broad_and_narrow_separately():
    """The two measures must never be reconciled into one number: broad over-counts iteration,
    narrow under-counts silent repairs, and their disagreement is the informative part."""
    iv = rep.Interval(ts=100, end=200, tier="sonnet", classes=["site_surface"], commits=[
        {"sha": "a", "ts": 110, "author": "x", "subject": "add the surface", "paths": ["site/p.html"]},
        {"sha": "b", "ts": 120, "author": "x", "subject": "add another", "paths": ["site/q.html"]},
    ])
    later = list(iv.commits) + [
        # touches p.html again, and reads like a repair -> broad AND narrow for commit a
        {"sha": "c", "ts": 300, "author": "x", "subject": "the filter did not filter",
         "paths": ["site/p.html"]},
        # touches q.html again, ordinary iteration -> broad only for commit b
        {"sha": "d", "ts": 310, "author": "x", "subject": "extend the panel", "paths": ["site/q.html"]},
    ]
    s = rep._rework([iv], later)["sonnet"]
    assert s == {"commits": 2, "broad": 2, "narrow": 1}


def test_treadmill_paths_are_not_counted_as_rework():
    """docs/status, site/data and friends are rewritten every publish cycle. Counting them would
    put every tier at 100% rework and make the metric useless in exactly the same way for both,
    which reads as 'no difference found' — a false negative, the expensive direction here."""
    iv = rep.Interval(ts=100, end=200, tier="sonnet", classes=[], commits=[
        {"sha": "a", "ts": 110, "author": "x", "subject": "publish", "paths": ["docs/status/LATEST.md"]},
    ])
    later = list(iv.commits) + [
        {"sha": "b", "ts": 300, "author": "x", "subject": "fix the thing", "paths": ["docs/status/LATEST.md"]},
    ]
    assert rep._rework([iv], later)["sonnet"]["broad"] == 0


@pytest.mark.parametrize("subject,expected", [
    # Real subjects from `git log --since=7.days` on 2026-08-12.
    ("fix(H_harness): the two reds my own verification run introduced, and one it only exposed", True),
    ("coldwalk(SITE2): the wall exhibit's customer view does not filter the exhibit", True),
    ("fix(OPS9): finding_severity refuses to start on foreign soil", True),
    ("build(D36): the printed bill foots on its face, in pence", False),
    ("OPS10 L0->L2: five class documents, fifty-one instances archived", False),
    ("status(SITE2): LATEST.md records the wall exhibit landing", False),
])
def test_the_repair_vocabulary_matches_how_this_repo_actually_writes_commits(subject, expected):
    """ANTI-TAUTOLOGY: pinned to subjects this repo really wrote, not to invented ones."""
    assert bool(rep._REPAIR_WORDS.search(subject)) is expected


def test_the_narrow_measure_has_a_known_and_stated_blind_spot():
    """A repair whose subject only DESCRIBES the bug, with no prefix and no vocabulary word, is
    missed. Asserting the miss rather than tuning the regex until it disappears is the point: narrow
    is a FLOOR on the rework rate. If this ever starts matching, the docstring's claim that narrow
    under-counts has changed and the report's framing must change with it."""
    missed = "KNIFE3: the self-refill doorbell was replaying the mint-time first step"
    assert rep._REPAIR_WORDS.search(missed) is None


def test_the_pilot_line_reports_zero_firing_as_no_comparison_possible(tmp_path, monkeypatch):
    """The self-note line carries the same honesty rule as the full report. This is the line the
    director actually reads each morning, so it is the one that must never imply safety it has not
    measured."""
    log = tmp_path / "t.jsonl"
    _write_log(log, [{"ts": 1786500000, "tier": "opus", "classes": ["level_move"]}])
    monkeypatch.setattr(rep, "TIER_LOG", log)
    line = rep.pilot_line()
    assert "NOT FIRED YET" in line
    assert "never an absence of harm" in line


def test_the_pilot_line_says_closed_after_the_window(tmp_path, monkeypatch):
    """Once the window shuts the line must stop reporting a live experiment. Otherwise the note goes
    on implying a pilot is running months after the code stopped running one."""
    cfg = tmp_path / "pilot.yaml"
    cfg.write_text("version: 1\nends: '2000-01-01'\nclasses:\n  stale_gap_row: {enabled: true}\n")
    monkeypatch.setattr(rep, "PILOT_CONFIG", cfg)
    line = rep.pilot_line()
    assert "CLOSED" in line and "back on Opus" in line


def test_the_pilot_line_is_fail_closed_on_a_missing_config(tmp_path, monkeypatch):
    monkeypatch.setattr(rep, "PILOT_CONFIG", tmp_path / "nope.yaml")
    assert "pre-pilot behaviour" in rep.pilot_line()


def test_the_daily_self_note_actually_calls_the_pilot_line():
    """THE ORPHAN-RATCHET CONTRACT. tools/model_tier_report.py exists to be run, and the thing that
    runs it is daily-self-note.timer. If that call is removed the tool goes back to being work
    nothing runs — the no-caller class this repo has hit 13 times in 13 days."""
    src = (rep.ROOT / "background" / "daily_self_note.py").read_text(encoding="utf-8")
    assert "from tools.model_tier_report import pilot_line" in src
    assert "Model tiering pilot" in src


def test_the_baseline_covers_a_real_period_and_reports_its_caveat():
    """The baseline is what makes the pilot a comparison rather than a set of orphan numbers. It
    must also state that it is an all-work baseline, because a per-class Opus baseline cannot be
    recovered retrospectively — the pre-pilot log recorded no work class."""
    b = rep.build_baseline(7)
    assert b["period"]["days"] == 7
    assert b["commits"] > 0, "no commits in the baseline period — attribution is broken"
    assert "per-class" in b["caveat"]
    assert "CAVEAT" in rep.render_baseline(b)
