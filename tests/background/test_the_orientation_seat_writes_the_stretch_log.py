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


def test_every_run_that_recorded_a_reason_writes_and_a_refusal_does_not():
    """Partition in one control over oriented / skipped / refused. A skipped run writes too
    (2026-09-30): if it did not, a quiet stretch or the director's tick-mode hold would escalate
    exactly like a stopped writer, and the page could not say which. A refused run has neither a
    reading nor a skip reason, and writing for it would invent one."""
    got = []
    grab = lambda s, b: got.append((s, b))  # noqa: E731
    assert seat.write_stretch_entry(dict(ROW), append_fn=grab) is True
    skipped = {"outcome": "skipped", "why": "no substantive commit in the stretch", "thesis_read": ""}
    assert seat.write_stretch_entry(skipped, append_fn=grab) is True
    assert seat.write_stretch_entry({"outcome": "refused", "why": "x"}, append_fn=grab) is False
    assert len(got) == 2
    assert got[1][0].startswith("orientation skipped:") and "no substantive commit" in got[1][1]
    assert "reading of this stretch" in got[1][1], "a skip entry must say no reading was made"


def test_an_orientation_writes_its_thesis_read_into_a_real_log(tmp_path, monkeypatch):
    """The control the item asked for: the REAL append path, no stub, into a temp log, and the
    entry's text carries the row's thesis_read. Mutating the append call in `write_stretch_entry`
    away reds this leg (recorded in the commit)."""
    log = tmp_path / "SEAT_STRETCH_LOG.md"
    monkeypatch.setattr(seat.stretch_log_mod, "LOG", log)
    assert seat.write_stretch_entry(dict(ROW)) is True
    text = log.read_text(encoding="utf-8")
    assert ROW["thesis_read"] in text
    assert "Written by the orientation seat" in text


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


def test_a_skipped_orientation_reaches_the_writer(monkeypatch):
    """Drives `orient()` down its skip branch. The source-order leg above cannot see this call: its
    first match for the writer is satisfied by either branch."""
    brief = {"since": "2026-09-30T11:00:00+00:00", "commit_count": 0, "substantive_count": 0,
             "previous_focus_drawn": None}
    monkeypatch.setattr(seat, "build_brief", lambda now: brief)
    monkeypatch.setattr(seat, "is_material", lambda b: (False, "no substantive commit"))
    monkeypatch.setattr(seat, "map_levels", lambda: {})
    monkeypatch.setattr(seat, "_log", lambda m: None)
    monkeypatch.setattr(seat.direction_mod, "append_decision", lambda row: None)
    written = []
    monkeypatch.setattr(seat, "write_stretch_entry", lambda row, append_fn=None: written.append(row))
    row = seat.orient()
    assert row["outcome"] == "skipped" and written == [row]
