"""The console capture stopping must be a FINDING, never a silence.

Every test here is named for a defect that actually occurred on 2026-09-07, when the capture was
found six days dead. The module already refused an UNREADABLE transcript and the state that
happened was a STALE one -- a folder that still existed, still held sixteen real transcripts, and
had simply stopped receiving new ones. Blindness was guarded; staleness was not, and the two render
identically to every reader.
"""
from __future__ import annotations

import time

import pytest

from tools import console_instruction_record as record


def _stamp(tmp_path, when: float):
    p = tmp_path / ".human_last_input"
    p.write_text(str(when), encoding="utf-8")
    return p


def _record(staging, day: str, text: str = "Do the thing."):
    record.append_turn(f"{day}T09:00:00.000Z", text, staging=staging)


def test_A_COLD_TRANSCRIPT_FOLDER_IS_A_FINDING_not_a_quiet_director(tmp_path, monkeypatch):
    """THE DEFECT, EXACTLY. The director typed today; the newest record is six days old. Nothing in
    the tree compared those two facts, so a capture that had stopped was indistinguishable from a
    director who had said nothing -- for six days, across the demand-vector brief and the whole
    weather programme."""
    staging = tmp_path / "staging"
    _record(staging, "2026-09-01")
    monkeypatch.setattr(record, "HUMAN_PRESENCE_STAMP", _stamp(tmp_path, time.time()))
    monkeypatch.setattr(record, "STAGING_DIR", staging)

    code, message = record.check(staging=staging)
    assert code == 1, "a six-day lapse reported as healthy -- silence and blindness render the same"
    assert "LAPSED" in message and "2026-09-01" in message


def test_THE_CHECK_READS_THE_SAME_ROOM_THE_WRITER_WRITES_TO(tmp_path, monkeypatch):
    """A SECOND-ORDER INSTANCE OF THE SAME DEFECT, committed inside the fix. The first draft of
    `_newest_captured_day` globbed the staging root and `done/` and never looked in `console/` --
    which is where `record_path` files every record -- so it reported a four-day lapse over files
    that were on disk. A guard that reads a different directory from the writer it guards is the
    original bug wearing a control's clothes."""
    staging = tmp_path / "staging"
    _record(staging, "2026-09-07")
    # The day needs BOTH sides, or the pairing check answers instead and this test stops being
    # about the room it was written to guard.
    record.append_reply("2026-09-07T09:05:00.000Z", "Answered.", staging=staging)
    assert (staging / "DIRECTOR_CONSOLE_2026-09-07.md").is_file(), (
        "the writer no longer files a new day into the root; this test's premise has moved")
    monkeypatch.setattr(record, "HUMAN_PRESENCE_STAMP", _stamp(tmp_path, time.time()))

    code, message = record.check(staging=staging)
    assert code == 0, f"a record written today read as a lapse: {message}"


def test_A_MISSING_PRESENCE_STAMP_FAILS_CLOSED(tmp_path, monkeypatch):
    """The control needs an INDEPENDENT signal. With no presence stamp there is nothing to compare
    the record against, and 'nothing to compare' must never render as 'all clear' -- that is the
    fail-open shape this whole repair exists to remove."""
    staging = tmp_path / "staging"
    _record(staging, "2026-09-07")
    monkeypatch.setattr(record, "HUMAN_PRESENCE_STAMP", tmp_path / "absent")

    code, message = record.check(staging=staging)
    assert code == 1 and "absent" in message


def test_A_DAEMON_PROMPT_IS_NEVER_RECORDED_AS_THE_DIRECTOR(tmp_path):
    """WORSE THAN THE GAP IT REPLACED. Pointed at the live transcript folder, the scanner swept
    daemon-injected turns into the record: 67% of 2026-09-04's captured 'director turns' and 84% of
    2026-09-06's were 'You are the autonomous worker...', quoted as his words in a file the release
    door reads as his authority.

    There is no structural discriminator to fall back on -- an interactive seat, a worker tick and
    a delivery-seat dispatch all write `userType: "external"` with identical cwd and version."""
    staging = tmp_path / "staging"
    assert record.append_turn("2026-09-07T09:00:00.000Z",
                              "You are the autonomous worker, woken by a scheduled tick",
                              staging=staging) is None
    assert record.append_turn("2026-09-07T09:01:00.000Z",
                              "[SUPERVISOR: grant] carry on", staging=staging) is None
    assert record.append_turn("2026-09-07T09:02:00.000Z",
                              "Fix the console capture.", staging=staging) is not None

    body = (staging / "DIRECTOR_CONSOLE_2026-09-07.md").read_text(encoding="utf-8")
    assert "autonomous worker" not in body and "SUPERVISOR" not in body
    assert "Fix the console capture." in body


def test_THE_BACKSTOP_MERGES_AND_CANNOT_SHRINK_A_RECORD(tmp_path, monkeypatch):
    """A CAPTURE THAT DELETES EVIDENCE, and it happened during the repair. `write()` reads only
    transcripts modified inside a three-day window, so re-running it regenerates an older day from
    nothing -- it cut the 2026-09-03 record from 22,907 bytes to 10,592, silently dropping turns it
    could no longer see, in the same hour it was being fixed for losing six days.

    A turn may only leave this record by a human deleting it."""
    staging = tmp_path / "staging"
    _record(staging, "2026-09-05", "An instruction only the old record holds.")
    monkeypatch.setattr(record, "STAGING_DIR", staging)
    monkeypatch.setattr(record, "director_turns_across", lambda paths: ([], []))
    monkeypatch.setattr(record, "recent_transcripts", lambda directory=None, days=3.0: [])

    record.write(staging=staging)
    body = (staging / "DIRECTOR_CONSOLE_2026-09-05.md").read_text(encoding="utf-8")
    assert "An instruction only the old record holds." in body, (
        "the backstop regenerated a day from an empty window and destroyed the turns on disk")


def test_THE_TRANSCRIPT_FOLDER_IS_DERIVED_FROM_THE_LAUNCH_DIRECTORY():
    """THE ROOT CAUSE. The folder name is a slug of the session's working directory. This module
    had `-` (the slug for `/`) baked in; the seat moved under systemd on 2026-09-03, its launch
    directory became the project, and the capture kept reading a folder nothing wrote to again.

    Keyed to the derivation, not to today's answer, so it stays true when the path moves again."""
    assert record.TRANSCRIPT_DIR.name == record._slug(record.PROJECT_DIR)
    assert record.TRANSCRIPT_DIR.name != "-", (
        "the transcript folder is back to the hardcoded legacy slug")
    assert any(d.name == "-" for d in record.LEGACY_TRANSCRIPT_DIRS), (
        "the legacy folder must still be read, or its history is orphaned")


def test_THE_CAPTURE_IS_VERBATIM_and_expands_nothing(tmp_path):
    """The module's standing refusal: shorthand stays shorthand, because resolving it to an atom
    is a judgement and an automatic capture doing that is putting words in his mouth."""
    staging = tmp_path / "staging"
    typed = "move EP1 and EP6 to build"
    record.append_turn("2026-09-07T09:00:00.000Z", typed, staging=staging)
    body = (staging / "DIRECTOR_CONSOLE_2026-09-07.md").read_text(encoding="utf-8")
    assert f"> {typed}" in body
    # Scoped to the CAPTURED TURN, not the file: the standing header explains the EP6 incident by
    # name, so asserting over the whole document tests the header's prose and not the capture.
    captured = body.split("### ")[-1]
    assert "EP6_wall_protocol_typing" not in captured, "the capture expanded his shorthand"


def test_AN_EXACT_REPEAT_IS_NOT_WRITTEN_TWICE(tmp_path):
    """The hook may be retried; a record that doubles every turn is not a verbatim record."""
    staging = tmp_path / "staging"
    assert record.append_turn("2026-09-07T09:00:00.000Z", "Same words.", staging=staging)
    assert record.append_turn("2026-09-07T09:00:00.000Z", "Same words.", staging=staging) is None
    body = (staging / "DIRECTOR_CONSOLE_2026-09-07.md").read_text(encoding="utf-8")
    assert body.count("> Same words.") == 1


def test_A_RECORD_IS_NEVER_FILED_UNDER_AN_UNPARSEABLE_DAY(tmp_path):
    """A turn with a broken timestamp must raise, not land in a file named for a day that does not
    exist -- an unfindable record is the same as no record."""
    with pytest.raises(ValueError, match="real day"):
        record.append_turn("not-a-timestamp", "Words.", staging=tmp_path / "staging")


@pytest.mark.parametrize("payload", ['{"prompt":"A real instruction."}', "not json", "{}"])
def test_THE_HOOK_NEVER_BLOCKS_THE_DIRECTORS_PROMPT(tmp_path, payload):
    """Capturing his words must not become a new way for his session to get stuck. Every failure
    exits 0 -- which is only safe BECAUSE `check()` above raises the finding when it does."""
    import subprocess

    hook = record.PROJECT_DIR / ".claude" / "hooks" / "capture_director_console.py"
    done = subprocess.run(["python3", str(hook)], input=payload, text=True,
                          capture_output=True, env={"SE_SEAT": "foreign", "PATH": "/usr/bin:/bin",
                                                    "HOME": str(tmp_path)})
    assert done.returncode == 0, f"the hook blocked on {payload!r}: {done.stderr[:300]}"
    assert done.stdout == "", "the hook wrote to stdout, which the harness reads as a decision"
