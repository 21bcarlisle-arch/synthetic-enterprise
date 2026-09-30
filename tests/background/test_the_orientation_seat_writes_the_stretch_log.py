"""The defect: the stretch log's only writer was an interactive session, present only while the
director is, so every fix to its alarm went quiet within a week while the orientation seat wrote the
same reflection every three hours into `decisions.jsonl` and was barred from the log
(`docs/staging/SEAT_FINDING_THE_STRETCH_LOG_HAS_ONE_WRITER_...`, 2026-09-30)."""
from __future__ import annotations

import inspect

from background import delivery_seat as seat

ROW = {"at": "2026-09-30T11:23:00+00:00", "since": "2026-09-30T08:24:57+00:00", "commits": 8,
       "substantive": 7, "outcome": "oriented",
       "thesis_read": "The thesis test is still waiting on its answer. Both steer items landed.",
       "wrong": [{"what": "said the run was never drawn", "corrected": True},
                 {"what": "the OOM price was a floor", "corrected": False}],
       "not_now": ["the bulk drain of parked docs"], "focus": ["finish-the-five-seed-grade"]}


def test_an_oriented_row_writes_and_a_skipped_one_does_not_both_ways():
    """Partition in one control: a writer that never writes, or one that writes for a skipped
    stretch (inventing a reflection nobody recorded), fails a leg."""
    got = []
    assert seat.write_stretch_entry(dict(ROW), append_fn=lambda s, b: got.append((s, b))) is True
    assert len(got) == 1
    skipped = {"outcome": "skipped", "why": "no substantive commit", "thesis_read": ""}
    assert seat.write_stretch_entry(skipped, append_fn=lambda s, b: got.append((s, b))) is False
    assert len(got) == 1


def test_the_entry_is_the_rows_own_words_and_invents_nothing():
    subject, body = seat.stretch_entry_from_row(ROW)
    assert subject == "orientation: The thesis test is still waiting on its answer"
    assert "The thesis test is still waiting on its answer. Both steer items landed." in body
    assert "- corrected: said the run was never drawn" in body
    assert "- NOT corrected: the OOM price was a floor" in body
    assert "- the bulk drain of parked docs" in body and "`finish-the-five-seed-grade`" in body


def test_a_subject_the_log_would_refuse_falls_back_rather_than_losing_the_entry():
    row = dict(ROW, thesis_read="As discussed. The rest.")   # conversational, and too short
    subject, _ = seat.stretch_entry_from_row(row)
    assert seat.stretch_log_mod.validate_subject(subject) is None, subject


def test_a_failing_append_is_recorded_and_never_raises():
    def boom(s, b):
        raise OSError("disk full")
    row = dict(ROW)
    assert seat.write_stretch_entry(row, append_fn=boom) is False and row["stretch_entry"] is False


def test_orient_calls_the_writer_and_the_commit_carries_the_log():
    """Order and reach: the entry is written after the decision row and before the commit, and the
    commit's pathspec includes the log -- a written entry that is never committed reaches nobody."""
    src = inspect.getsource(seat.orient)
    assert src.index("append_decision(row)") < src.index("write_stretch_entry(row)") \
        < src.index("commit_direction()")
    assert "SEAT_WRITTEN" in inspect.getsource(seat.commit_direction)
    assert "docs/status/SEAT_STRETCH_LOG.md" in seat.SEAT_WRITTEN
