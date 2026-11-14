"""On 14 Nov the console record filed three machine turns as the director's words: an image
caption, the whole phase-close skill expansion, and a ScheduleWakeup prompt ("Check
/tmp/c32_land.log ..."), which became the orientation brief's ONLY director input. G8 gives his
words full authority, so this is the most expensive misreading the machine can make.

The transcript says which turns were typed: the `user` record carries `turnOrigin` and `isMeta`.
The wakeup's `queue-operation` enqueue twin carries neither, and it won the text dedup.

Mutations: drop the enqueue-twin lookup and the wakeup test goes red. Drop the skill-expansion
text floor and the transcript-free relabel test goes red. Match 'Base directory' anywhere instead
of as a prefix and the mid-sentence test goes red. Make `is_his` ignore the heading label and the
brief tests go red. Make every turn NOT HIS and the partition control goes red.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from background import delivery_seat as seat
from tools import console_instruction_record as cir

DAY = "2026-11-14"
SKILL = "Base directory for this skill: /x/.claude/skills/phase-close\n\n# Phase-close checklist"
WAKEUP = "Check /tmp/c32_land.log for the C32 surgical_land result; if landed run it."
TYPED = "move C32 to the front of the queue"


def _user(text, ts, **fields):
    return json.dumps({"type": "user", "timestamp": ts, **fields,
                       "message": {"content": [{"type": "text", "text": text}]}})


def _enqueue(text, ts):
    return json.dumps({"type": "queue-operation", "operation": "enqueue", "timestamp": ts,
                       "content": text})


def _transcripts(tmp_path, lines):
    d = tmp_path / "t"
    d.mkdir(exist_ok=True)
    (d / "s.jsonl").write_text("\n".join(lines), encoding="utf-8")
    return d


def _brief(staging, monkeypatch):
    monkeypatch.setattr(seat, "STAGING_DIR", staging)
    return seat.director_inputs(datetime(2026, 11, 14, tzinfo=timezone.utc),
                                datetime(2026, 11, 14, 23, 0, tzinfo=timezone.utc))


def test_one_typed_turn_and_one_skill_expansion_yield_exactly_one_director_input(
        tmp_path, monkeypatch):
    d = _transcripts(tmp_path, [
        _user(TYPED, f"{DAY}T10:00:00.000Z", turnOrigin="human", promptSource="typed"),
        _user(SKILL, f"{DAY}T10:01:00.000Z", isMeta=True),
    ])
    staging = tmp_path / "staging"
    cir.write(directory=d, staging=staging)
    record = cir.record_path(DAY, staging)
    turns = cir.turns_in_record(record)

    # Kept in the record, labelled; one his, one not -- both arms of the partition taken.
    assert [cir.is_his(s, t) for s, t in turns] == [True, False]
    assert "NOT HIS: isMeta" in turns[1][0]
    assert _brief(staging, monkeypatch) == [
        f"{record.relative_to(staging).as_posix()}@{DAY}T10:00:00.000Z"]


def test_a_wakeup_prompt_is_not_his_though_its_enqueue_twin_carries_no_origin(
        tmp_path, monkeypatch):
    d = _transcripts(tmp_path, [
        _user(TYPED, f"{DAY}T09:00:00.000Z", turnOrigin="human", promptSource="queued"),
        _enqueue(WAKEUP, f"{DAY}T19:16:00.163Z"),
        _user(WAKEUP, f"{DAY}T19:16:00.224Z", isMeta=True, promptSource="system",
              turnOrigin="scheduled"),
    ])
    assert cir.director_turns(cir.newest_transcript(d)) == [(f"{DAY}T09:00:00.000Z", TYPED)]
    staging = tmp_path / "staging"
    cir.write(directory=d, staging=staging)
    labels = [cir.split_heading(s) for s, _ in cir.turns_in_record(cir.record_path(DAY, staging))]
    assert labels == [(f"{DAY}T09:00:00.000Z", None),
                      (f"{DAY}T19:16:00.163Z", "turnOrigin=scheduled")]
    assert len(_brief(staging, monkeypatch)) == 1


def test_a_record_written_before_the_label_is_relabelled_on_the_next_write(tmp_path,
                                                                           monkeypatch):
    """Today's file: the wakeup and the skill expansion sit unlabelled on disk."""
    staging = tmp_path / "staging"
    record = staging / "console" / f"DIRECTOR_CONSOLE_{DAY}.md"
    record.parent.mkdir(parents=True)
    record.write_text(cir.render(DAY, [(f"{DAY}T16:34:37.414Z", SKILL),
                                       (f"{DAY}T19:16:00.163Z", WAKEUP)], "old"),
                      encoding="utf-8")
    assert len(_brief(staging, monkeypatch)) == 1  # the skill floor works with no transcript
    d = _transcripts(tmp_path, [
        _user(TYPED, f"{DAY}T21:00:00.000Z", turnOrigin="human"),
        _enqueue(WAKEUP, f"{DAY}T19:16:00.163Z"),
        _user(WAKEUP, f"{DAY}T19:16:00.224Z", isMeta=True, turnOrigin="scheduled"),
    ])
    cir.write(directory=d, staging=staging)
    turns = cir.turns_in_record(record)
    assert [cir.is_his(s, t) for s, t in turns] == [False, False, True]
    assert _brief(staging, monkeypatch) == [f"console/{record.name}@{DAY}T21:00:00.000Z"]


def test_a_typed_turn_that_quotes_base_directory_mid_sentence_is_still_his():
    text = "why did the record file 'Base directory for this skill:' as mine?"
    assert cir.is_director_prompt(text)
    assert cir.text_says_not_his(text) is None
    assert not cir.is_director_prompt(SKILL)


def test_the_live_hook_labels_a_skill_expansion_and_files_a_typed_turn_plain(tmp_path):
    staging = tmp_path / "staging"
    cir.append_turn(f"{DAY}T10:00:00.000Z", TYPED, staging=staging)
    cir.append_turn(f"{DAY}T10:01:00.000Z", SKILL, staging=staging)
    turns = cir.turns_in_record(cir.record_path(DAY, staging))
    assert [cir.is_his(s, t) for s, t in turns] == [True, False]


def test_a_day_with_only_machine_turns_gets_no_record(tmp_path):
    d = _transcripts(tmp_path, [
        _user(TYPED, "2026-11-13T10:00:00.000Z", turnOrigin="human"),
        _user(WAKEUP, f"{DAY}T19:16:00.224Z", isMeta=True, turnOrigin="scheduled"),
    ])
    staging = tmp_path / "staging"
    cir.write(directory=d, staging=staging)
    assert cir.record_path("2026-11-13", staging).exists()
    assert not cir.record_path(DAY, staging).exists()
