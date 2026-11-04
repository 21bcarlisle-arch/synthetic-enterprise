"""`tools/insight_challenge.py` selects insight rows by their review date, never re-challenges a
refuted row, and treats a row with no date as due now (Ask 5 of the 4 Nov knowledge-and-insight
steer)."""
from __future__ import annotations

import datetime as dt
import json

import tools.insight_challenge as ic
from background.weekly_rhythm import _insights_due_section
from tools.insight_challenge import brief, due

AS_OF = dt.date(2026, 11, 4)


def _row(claim, status="hypothesis", review_by="2026-11-20", **kw):
    return dict(claim=claim, status=status, review_by=review_by, section="s", rests_on=["x"],
                from_sim=False, falsified_by="F-" + claim, checked="2026-10-01", use=[], **kw)


FACETS = {"pages": {
    "a": {"insights": [_row("soon"), _row("late", review_by="2027-06-01")]},
    "b": {"insights": [_row("refuted", status="refuted", review_by="2026-01-01"),
                       _row("undated", review_by=None)]},
}}


def test_the_window_admits_some_rows_and_excludes_others():
    got = [r["claim"] for r in due(FACETS, AS_OF, 30)]
    assert got == ["undated", "soon"]
    assert [r["claim"] for r in due(FACETS, AS_OF, 400)] == ["undated", "soon", "late"]


def test_a_refuted_row_is_never_rechallenged_however_old_its_date():
    assert "refuted" not in [r["claim"] for r in due(FACETS, AS_OF, 10_000)]


def test_the_brief_carries_each_rows_falsifier_and_page():
    text = brief(due(FACETS, AS_OF, 30), AS_OF)
    assert "Challenge these 2 insights" in text
    assert "F-soon" in text and "https://poesys.net/knowledge/a/" in text
    assert "review by:** none set" in text


def test_mondays_step_lists_the_rows_due_and_says_none_when_none_are(tmp_path, monkeypatch):
    f = tmp_path / "facets.json"
    monkeypatch.setattr(ic, "FACETS", f)
    f.write_text(json.dumps(FACETS), encoding="utf-8")
    text = "\n".join(_insights_due_section())
    assert "row(s) due within 30 days" in text and "a: soon" in text and "refuted" not in text
    f.write_text(json.dumps({"pages": {"a": {"insights": [_row("late", review_by="2099-01-01")]}}}),
                 encoding="utf-8")
    assert "None within 30 days." in "\n".join(_insights_due_section())
    f.write_text("not json", encoding="utf-8")
    assert "UNAVAILABLE, not clean" in "\n".join(_insights_due_section())
