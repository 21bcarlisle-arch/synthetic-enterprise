"""Tests for background/trust_ledger.py -- TRUST_LEDGER_AND_BILLING_CHECK.md
item 1 (P1, 2026-07-13). The Goodhart safeguards are the load-bearing
behaviour here: an evaluator not on the whitelist must be structurally
impossible to record, not merely discouraged."""
import json

import pytest

from background import trust_ledger as tl


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(tl, "LEDGER_PATH", tmp_path / "trust_ledger.json")
    yield


def test_record_verdict_rejects_unknown_evaluator():
    """The core safeguard: 'the builder may never modify, tune, or select
    its own evaluator -- closed at the tool level, not by policy.' A
    self-reported or made-up evaluator identity must raise, not silently
    record."""
    with pytest.raises(ValueError, match="not a recognised independent evaluator"):
        tl.record_verdict(
            tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.PASS,
            evaluator_name="the-builder-itself", subject="commit abc123",
        )


def test_record_verdict_rejects_empty_evaluator_name():
    with pytest.raises(ValueError):
        tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS, evaluator_name="", subject="x")


@pytest.mark.parametrize("evaluator", sorted(tl.INDEPENDENT_EVALUATORS))
def test_record_verdict_accepts_every_whitelisted_evaluator(evaluator):
    entry = tl.record_verdict(
        tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.PASS,
        evaluator_name=evaluator, subject="commit abc123",
    )
    assert entry.evaluator_name == evaluator


def test_record_verdict_persists_to_disk():
    tl.record_verdict(
        tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.PASS,
        evaluator_name="phase-close-evaluator", subject="commit abc123",
    )
    assert tl.LEDGER_PATH.exists()
    data = json.loads(tl.LEDGER_PATH.read_text())
    assert len(data) == 1
    assert data[0]["task_class"] == "harness_supervisor"
    assert data[0]["verdict"] == "pass"


def test_entries_for_class_filters_correctly():
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.PASS, evaluator_name="phase-close-evaluator", subject="a")
    tl.record_verdict(tl.TaskClass.PRICING, tl.Verdict.PASS, evaluator_name="phase-close-evaluator", subject="b")
    tl.record_verdict(tl.TaskClass.BILLING, tl.Verdict.NEEDS_WORK, evaluator_name="cold-eyes-walk", subject="c")
    billing = tl.entries_for_class(tl.TaskClass.BILLING)
    assert len(billing) == 2
    assert all(e["task_class"] == "billing" for e in billing)


def test_autonomy_level_insufficient_data_below_three_entries():
    tl.record_verdict(tl.TaskClass.SITE_PRESENTATION, tl.Verdict.PASS, evaluator_name="phase-close-evaluator", subject="a")
    tl.record_verdict(tl.TaskClass.SITE_PRESENTATION, tl.Verdict.PASS, evaluator_name="phase-close-evaluator", subject="b")
    assert tl.autonomy_level(tl.TaskClass.SITE_PRESENTATION) == "insufficient_data"


def test_autonomy_level_earned_above_threshold():
    for i in range(5):
        tl.record_verdict(
            tl.TaskClass.DOCS_DISCOVERY, tl.Verdict.PASS,
            evaluator_name="cold-eyes-walk", subject=f"atom-{i}",
        )
    assert tl.autonomy_level(tl.TaskClass.DOCS_DISCOVERY) == "earned"


def test_autonomy_level_under_review_when_quality_slips():
    """The staged instruction's own core property: 'automatically REVOKED
    when quality slips -- a class that starts failing goes back under
    review without anyone deciding.'"""
    for i in range(5):
        tl.record_verdict(
            tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.PASS,
            evaluator_name="phase-close-evaluator", subject=f"good-{i}",
        )
    assert tl.autonomy_level(tl.TaskClass.HARNESS_SUPERVISOR) == "earned"
    for i in range(3):
        tl.record_verdict(
            tl.TaskClass.HARNESS_SUPERVISOR, tl.Verdict.NEEDS_WORK,
            evaluator_name="phase-close-evaluator", subject=f"bad-{i}",
        )
    # No separate "revoke" call anywhere -- the SAME function re-derives
    # from the now-worse record and returns a different answer.
    assert tl.autonomy_level(tl.TaskClass.HARNESS_SUPERVISOR) == "under_review"


def test_autonomy_level_only_considers_recent_window():
    for i in range(20):
        tl.record_verdict(
            tl.TaskClass.PRICING, tl.Verdict.NEEDS_WORK,
            evaluator_name="cold-eyes-walk", subject=f"old-bad-{i}",
        )
    for i in range(10):
        tl.record_verdict(
            tl.TaskClass.PRICING, tl.Verdict.PASS,
            evaluator_name="cold-eyes-walk", subject=f"recent-good-{i}",
        )
    assert tl.autonomy_level(tl.TaskClass.PRICING, window=10) == "earned"


def test_check_grader_capture_tell_flags_rising_pass_falling_defects():
    for i in range(3):
        tl.record_verdict(
            tl.TaskClass.BILLING, tl.Verdict.NEEDS_WORK,
            evaluator_name="phase-close-evaluator", subject=f"a{i}",
            defects_found_post_close=3,
        )
    for i in range(3):
        tl.record_verdict(
            tl.TaskClass.BILLING, tl.Verdict.PASS,
            evaluator_name="phase-close-evaluator", subject=f"b{i}",
            defects_found_post_close=0,
        )
    tell = tl.check_grader_capture_tell(tl.TaskClass.BILLING)
    assert tell is not None
    assert "GRADER CAPTURE TELL" in tell


def test_check_grader_capture_tell_none_when_no_pattern():
    for i in range(6):
        tl.record_verdict(
            tl.TaskClass.SITE_PRESENTATION, tl.Verdict.PASS,
            evaluator_name="cold-eyes-walk", subject=f"a{i}",
            defects_found_post_close=0,
        )
    assert tl.check_grader_capture_tell(tl.TaskClass.SITE_PRESENTATION) is None


def test_check_grader_capture_tell_none_with_too_few_entries():
    tl.record_verdict(tl.TaskClass.DOCS_DISCOVERY, tl.Verdict.PASS, evaluator_name="cold-eyes-walk", subject="a")
    assert tl.check_grader_capture_tell(tl.TaskClass.DOCS_DISCOVERY) is None


def test_ledger_missing_file_degrades_gracefully():
    assert not tl.LEDGER_PATH.exists()
    assert tl.entries_for_class(tl.TaskClass.BILLING) == []
    assert tl.autonomy_level(tl.TaskClass.BILLING) == "insufficient_data"
