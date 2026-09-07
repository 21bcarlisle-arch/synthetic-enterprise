"""The seat's side of the conversation, each test named by the defect it catches.

Director, 2026-09-07: *"it records what I send and not what you reply, and the stretch log only
lands when a stretch closes — so between the two there's a window where my advisor can see the
instruction and not the answer."*

The dangerous way to close that window is to append the seat's replies to the console record. That
file is read as the DIRECTOR'S OWN WORDS by the release door, and putting the machine's words in it
would be the same defect that let daemon prompts in earlier the same day, one step further along.
The first test here is the one that forbids it.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import time
from pathlib import Path

import pytest

from background import staging_rooms
from tools import console_instruction_record as record

HOOK = record.PROJECT_DIR / ".claude" / "hooks" / "capture_seat_reply.py"


def _hook_module():
    spec = importlib.util.spec_from_file_location("capture_seat_reply", HOOK)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_A_REPLY_IS_NEVER_FILED_UNDER_THE_DIRECTORS_OWN_PREFIX(tmp_path):
    """THE AUTHORITY BOUNDARY, and it is the whole reason this is a separate document.

    `pull_forward_proposal.director_sources` reads `DIRECTOR_CONSOLE_*` as the director's own
    words. A reply written into that file — or under that prefix — hands a release door the
    machine's words carrying his authority. Naming it `DIRECTOR_CONSOLE_REPLY_` would have routed
    it to the right room with no code change, which is exactly what makes the mistake attractive.
    """
    written = record.append_reply("2026-09-07T14:00:00.000Z", "The capture is fixed.",
                                  staging=tmp_path)
    assert written is not None
    assert not written.name.startswith("DIRECTOR_CONSOLE"), (
        "the seat's reply is filed under the director's prefix and now reads as his authority")
    assert written.name == "SEAT_REPLY_2026-09-07.md"
    assert written.parent.name == "console", (
        "a reply landed in the staging ROOT, which rings the doorbell for a document carrying no "
        "ask and adds a document a day to a queue that already files faster than it disposes")

    console = record.record_path("2026-09-07", staging=tmp_path)
    assert not console.exists() or "The capture is fixed." not in console.read_text(
        encoding="utf-8"), "the seat's words landed inside the director's own record"


def test_A_REPLY_RECORD_IS_NOT_WORK_and_routes_to_the_console_room():
    """`SEAT_REPLY_` begins with the same four letters as `SEAT_FINDING_`. Classified as work it
    would flood the draw with one undrawable document per day; filed in the staging root it would
    ring the doorbell forever. It is a record, and it lives with the record it answers."""
    kind = staging_rooms.kind_of("SEAT_REPLY_2026-09-07.md")
    assert kind == staging_rooms.KIND_CONSOLE
    assert kind in staging_rooms.NOT_WORK
    assert staging_rooms.room_for(kind) == staging_rooms.CONSOLE_DIRNAME
    assert staging_rooms.kind_of("SEAT_FINDING_X_2026-09-07.md") != staging_rooms.KIND_CONSOLE, (
        "the new prefix swallowed real findings, which are work")


def test_THE_WINDOW_THE_DIRECTOR_NAMED_IS_A_FINDING(tmp_path, monkeypatch):
    """A day holding his turns and no replies is the gap itself: the advisor sees the instruction
    and not the answer. Checked against the RECORD rather than a clock, because a reply is owed per
    day of conversation, not per elapsed hour."""
    record.append_turn("2026-09-07T09:00:00.000Z", "Do the thing.", staging=tmp_path)
    stamp = tmp_path / ".human_last_input"
    stamp.write_text(str(time.time()), encoding="utf-8")
    monkeypatch.setattr(record, "HUMAN_PRESENCE_STAMP", stamp)
    monkeypatch.setattr(record, "STAGING_DIR", tmp_path)

    code, message = record.check(staging=tmp_path)
    assert code == 1 and "SEAT'S SIDE IS MISSING" in message

    record.append_reply("2026-09-07T09:05:00.000Z", "Done, and here is what moved.",
                        staging=tmp_path)
    code, message = record.check(staging=tmp_path)
    assert code == 0, f"both sides present and still reported as a gap: {message}"


def test_A_REPLY_IS_REDACTED_ON_THE_SAME_TERMS_AS_A_DIRECTOR_TURN(tmp_path):
    """The seat quotes back what the director pasted. A credential caught on his side and echoed
    on ours would leave by the other door — and this record ships to the same published tree."""
    written = record.append_reply(
        "2026-09-07T14:00:00.000Z",
        "Storing it as CF_API_TOKEN=abcdEFGH1234ijklMNOP5678qrstUVWX9012yzAB now.",
        staging=tmp_path)
    body = written.read_text(encoding="utf-8")
    assert "abcdEFGH1234ijklMNOP5678qrstUVWX9012yzAB" not in body
    assert record.REDACTION in body, "the span vanished without a marker, so the turn reads wrong"


def test_AN_EXACT_REPEAT_IS_NOT_WRITTEN_TWICE(tmp_path):
    """The Stop hook fires once per turn and may be retried; a doubled reply is not a record."""
    assert record.append_reply("2026-09-07T14:00:00.000Z", "Same answer.", staging=tmp_path)
    assert record.append_reply("2026-09-07T14:00:00.000Z", "Same answer.", staging=tmp_path) is None
    body = (tmp_path / "console" / "SEAT_REPLY_2026-09-07.md").read_text(encoding="utf-8")
    assert body.count("> Same answer.") == 1


def test_THE_REPLY_CARRIES_THE_TRANSCRIPTS_OWN_TIMESTAMP_not_the_wall_clock(tmp_path):
    """A hook firing late would otherwise file an answer under a time after the instruction it
    preceded, and the pair would sort wrong for the reader the record exists for."""
    module = _hook_module()
    transcript = tmp_path / "s.jsonl"
    transcript.write_text("\n".join(json.dumps(r) for r in [
        {"type": "assistant", "timestamp": "2026-09-07T09:01:00.000Z",
         "message": {"content": [{"type": "text", "text": "first"}]}},
        {"type": "assistant", "timestamp": "2026-09-07T09:02:00.000Z",
         "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
        {"type": "assistant", "timestamp": "2026-09-07T09:03:00.000Z",
         "message": {"content": [{"type": "text", "text": "last"}]}},
    ]), encoding="utf-8")

    stamp, text = module.last_assistant_text(transcript)
    assert (stamp, text) == ("2026-09-07T09:03:00.000Z", "last")
    assert [t for _s, t in module.assistant_turns(transcript)] == ["first", "last"], (
        "a tool call was recorded as something the seat said to the director")


@pytest.mark.parametrize("payload", ['{"session_id":"deadbeef"}', "not json", "{}"])
def test_THE_STOP_HOOK_NEVER_BLOCKS_AND_NEVER_SPEAKS(tmp_path, payload):
    """A Stop hook writing stdout is read by the harness as a decision about whether the turn may
    end. Capturing what was said must never become a way for the seat to refuse to stop."""
    done = subprocess.run(["python3", str(HOOK)], input=payload, text=True, capture_output=True,
                          env={"SE_SEAT": "foreign", "PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
    assert done.returncode == 0, f"the hook blocked on {payload!r}: {done.stderr[:300]}"
    assert done.stdout == "", "the hook spoke on stdout, which reads as a decision"


def test_THE_LIVE_RECORD_CARRIES_BOTH_SIDES_OF_TODAY():
    """The pass's own exit criterion, against the real tree: the day the director asked for this
    must itself hold his turns and the answers to them."""
    day = "2026-09-07"
    turns = record.turns_in_record(record.record_path(day))
    replies = record.turns_in_record(record.reply_path(day))
    if not turns:
        pytest.skip("no console record for the reference day on this machine")
    assert replies, "the day this was built holds instructions and no answers"

def test_A_SESSION_THE_DIRECTOR_NEVER_SPOKE_IN_WRITES_NOTHING(tmp_path):
    """THE DEFECT VERIFICATION FOUND, and it was found only because the director refused to assume
    the hook fired. `.claude/hooks/` is committed, so this runs in EVERY resident session --
    autonomous worker ticks and delivery-seat dispatches included. Within an hour of landing, two of
    them had written their own narration into his reply record: *"Released. Saving the
    control-failure class..."* filed as an answer to him. Three entries had to be purged.

    That is the mirror of the daemon-prompt defect repaired on his side the same morning: a record
    of what he was told carrying the machine talking to itself. An NTFY relay still counts, because
    it is genuinely him carried by a daemon -- which is why the test is `is_director_prompt` on the
    turns and not a guess about the session type."""
    module = _hook_module()

    worker = tmp_path / "worker.jsonl"
    worker.write_text("\n".join(json.dumps(r) for r in [
        {"type": "user", "timestamp": "2026-09-07T09:00:00.000Z",
         "message": {"content": "You are the autonomous worker, woken by a scheduled tick"}},
        {"type": "assistant", "timestamp": "2026-09-07T09:01:00.000Z",
         "message": {"content": [{"type": "text", "text": "Released. Saving the class."}]}},
    ]), encoding="utf-8")

    console = tmp_path / "console.jsonl"
    console.write_text("\n".join(json.dumps(r) for r in [
        {"type": "user", "timestamp": "2026-09-07T09:00:00.000Z",
         "message": {"content": "Verify it fires rather than assuming it will."}},
        {"type": "assistant", "timestamp": "2026-09-07T09:01:00.000Z",
         "message": {"content": [{"type": "text", "text": "Verified, and it found something."}]}},
    ]), encoding="utf-8")

    assert module.is_a_conversation_with_the_director(console) is True
    assert module.is_a_conversation_with_the_director(worker) is False, (
        "a worker tick counts as a conversation with the director, so its narration will be filed "
        "as an answer to him")
