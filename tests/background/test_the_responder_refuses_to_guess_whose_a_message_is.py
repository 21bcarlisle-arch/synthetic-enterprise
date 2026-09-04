"""When the sent-ids record is unreadable the responder must answer NEITHER "ours" nor "his".

THE JUDGEMENT `ntfy_utils.was_sent_by_us` HANDED OFF, PINNED HERE. That loader answers "is this id
in the record". When the record EXISTS and cannot be read there is no honest boolean, and the two
available ones are opposite defects of the RESPONDER:

    False  -> our own outbound is captured as INBOUND and staged as `from_rich_*.md`
              -- direction carrying the director's authority that he never gave.
    True   -> a real steer from him is silently suppressed.

So the responder refuses to classify: preserve in `docs/staging/quarantine/`, withhold from the
scanned staging root, and DO NOT reply. Not replying is the leg that keeps a misread echo from
feeding itself.

WHAT EVERY LEG ASSERTS IS THAT ABSENT AND PRESENT-BUT-UNREADABLE **DIFFER**, never that they match
-- a control pinning both to one branch is how `guard_episode`'s `prev=None` survived two lanes'
repairs. `test_an_absent_record_still_lets_a_real_steer_through` is the reachability null control:
without it, "differs" is satisfiable by a responder that quarantines everything, which would
suppress the director permanently and pass every other leg here.

The unreadable bytes are fed through the REAL `ntfy_utils.SENT_IDS_FILE`, never a monkeypatched
`sent_ids_unreadable` -- a stubbed predicate would test the stub. `null` and `[1, 2, 3]` are in the
partition on purpose: they PARSE, which is exactly why an `except JSONDecodeError` never saw them.

MUTANTS THIS CATCHES: delete the provenance branch in `check_once` (unreadable then falls to
`was_sent_by_us`, answers False, and stages); move the branch BELOW `was_sent_by_us` (same, because
by then the message is already past the only place that could catch it); make
`sent_ids_unreadable()` return True for an absent file (a real steer is quarantined forever);
send the status reply for a quarantined message (the echo loop); share the flood guard's
`last_alert` key (either guard's alert then silences the other's first-ever one).
"""
from __future__ import annotations

import json

import pytest

from background import action_needed as _action_needed
from background import ntfy_responder as responder
from background import ntfy_utils

#: Present-but-unreadable whatever the shape. A record that is not a list of strings was WRITTEN
#: and cannot be trusted; `msg_id in "abc"` is a substring test and `null` raises on the `in`.
UNREADABLE_BYTES = pytest.mark.parametrize(
    "raw",
    [
        pytest.param('["id1", "id2"', id="truncated"),
        pytest.param("", id="empty-file"),
        pytest.param("null", id="json-null"),
        pytest.param('{"ids": ["id1"]}', id="mapping-not-a-list"),
        pytest.param('"id1"', id="bare-string-a-substring-test"),
        pytest.param("[1, 2, 3]", id="list-of-non-strings"),
        # THE ONE MEMBER THAT MAKES THE ORDER MATTER, and it was missing from the first draft of
        # this file: a list that is PARTLY strings. Every other member above makes
        # `was_sent_by_us` return False by itself, so the provenance branch gives the same answer
        # above it or below it and the ordering mutant survived 17/17. Here `"id1" in ["id1", 2]`
        # is True, so BELOW `was_sent_by_us` the message is silently dropped as "ours" -- off a
        # record that has already been established as untrustworthy.
        pytest.param('["id1", 2]', id="list-partly-strings"),
    ],
)

OUR_OWN_ID = "id1"
HIS_ID = "steer-from-rich"
BODY = "Please kick off the overnight reconciliation batch now, thanks."


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    """Same isolation as test_ntfy_responder.py's autouse fixture -- staging, the register, the
    watermark and the log all in tmp -- plus the sent-ids record, which is what this file varies."""
    monkeypatch.setattr(responder, "PROJECT_DIR", tmp_path)
    (tmp_path / "docs" / "staging").mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(_action_needed, "open_items", lambda *a, **k: [])
    monkeypatch.setattr(responder, "STATE_FILE", tmp_path / "since.json")
    monkeypatch.setattr(responder, "OBSERVABILITY_DIR", tmp_path)
    monkeypatch.setattr(responder, "LOG_FILE", tmp_path / "log.md")
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", tmp_path / ".sent_ntfy_ids.json")


def _feed(monkeypatch, msg_id, msg_time, message):
    class FakeResponse:
        text = json.dumps(
            {"event": "message", "id": msg_id, "time": msg_time, "message": message}
        )

    monkeypatch.setattr(responder.requests, "get", lambda *a, **k: FakeResponse())


def _run(monkeypatch, tmp_path, msg_id, *, msg_time=100_000, body=BODY):
    """Drive one inbound message. Returns (staged_files, quarantined_files, notifications)."""
    sent: list[str] = []
    monkeypatch.setattr(responder, "notify", lambda msg, **k: sent.append(msg))
    _feed(monkeypatch, msg_id, msg_time, body)
    responder.check_once(msg_time - 1, [])

    staging_root = tmp_path / "docs" / "staging"
    quarantine_dir = staging_root / "quarantine"
    staged = list(staging_root.glob("from_rich_*.md"))  # non-recursive: the SCANNED root
    quarantined = list(quarantine_dir.glob("*.md")) if quarantine_dir.exists() else []
    return staged, quarantined, sent


# ---------------------------------------------------------------------------------------
# 1. UNREADABLE -- refuse to classify. Neither answer is taken.
# ---------------------------------------------------------------------------------------

@UNREADABLE_BYTES
def test_an_unreadable_record_quarantines_our_own_echo_instead_of_minting_a_from_rich(
    raw, tmp_path, monkeypatch
):
    """The False failure. `OUR_OWN_ID` really was ours -- and with the record unreadable nothing
    can prove it, so it must not become direction in the scanned staging root."""
    ntfy_utils.SENT_IDS_FILE.write_text(raw, encoding="utf-8")
    assert ntfy_utils.sent_ids_unreadable() is True, "fixture must actually be unreadable"

    staged, quarantined, _ = _run(monkeypatch, tmp_path, OUR_OWN_ID)

    assert staged == [], "our own echo reached the scanned staging root as a from_rich"
    assert len(quarantined) == 1, "and it was not preserved either -- the message was dropped"


@UNREADABLE_BYTES
def test_an_unreadable_record_preserves_a_real_steer_rather_than_suppressing_it(
    raw, tmp_path, monkeypatch
):
    """The True failure. A message that was NOT ours is equally unprovable, so it is preserved
    verbatim where a reader can recover it -- suppression would lose the director's steer."""
    ntfy_utils.SENT_IDS_FILE.write_text(raw, encoding="utf-8")

    staged, quarantined, _ = _run(monkeypatch, tmp_path, HIS_ID)

    assert len(quarantined) == 1
    assert BODY in quarantined[0].read_text(encoding="utf-8")


def test_the_check_must_sit_ABOVE_was_sent_by_us_and_the_two_orders_differ(tmp_path, monkeypatch):
    """THE ORDERING LEG, and it is the reason `list-partly-strings` is in the partition at all.

    An ordering control has to make the two orders produce DIFFERENT answers, and the first draft
    of this file did not: for every other unreadable shape `was_sent_by_us` returns False on its
    own, so moving the provenance check below it changed nothing and the mutant survived 17/17.
    `["id1", 2]` is the discriminator -- `"id1" in ["id1", 2]` is True, so below `was_sent_by_us`
    the message is dropped as "ours" on the authority of a record already known to be corrupt,
    and there is no file left behind to say it ever arrived.

    MUTANT: swap the two blocks in `check_once`. This leg fires; nothing else does."""
    ntfy_utils.SENT_IDS_FILE.write_text('["id1", 2]', encoding="utf-8")
    assert ntfy_utils.sent_ids_unreadable() is True
    assert ntfy_utils.was_sent_by_us(OUR_OWN_ID) is True, (
        "fixture must reach the state where the two orders disagree"
    )

    staged, quarantined, _ = _run(monkeypatch, tmp_path, OUR_OWN_ID)

    assert len(quarantined) == 1, (
        "the corrupt record's opinion won -- the message was dropped, not preserved"
    )
    assert staged == []


def test_the_quarantine_note_names_provenance_and_not_the_flood_guard(tmp_path, monkeypatch):
    """A reader who finds the file must not be sent to the wrong mechanism. MUTANT: drop `kind`
    and every quarantine reads as a flood, which is a different defect with a different remedy."""
    ntfy_utils.SENT_IDS_FILE.write_text("null", encoding="utf-8")

    _, quarantined, _ = _run(monkeypatch, tmp_path, HIS_ID)

    note = quarantined[0].read_text(encoding="utf-8")
    assert "provenance unknown" in note
    assert "machine-cadence flood" not in note


def test_a_quarantined_message_is_never_answered(tmp_path, monkeypatch):
    """The echo-loop leg. Replying to a message we cannot attribute is how our own reply comes
    back as the next unattributable inbound. MUTANT: send `build_status_reply` on this branch."""
    ntfy_utils.SENT_IDS_FILE.write_text("null", encoding="utf-8")

    _, _, sent = _run(monkeypatch, tmp_path, OUR_OWN_ID)

    assert [m for m in sent if "[PROVENANCE GUARD]" in m], "the seat was never told"
    assert not [m for m in sent if "[PROVENANCE GUARD]" not in m], (
        "a status reply went back onto the channel for a message of unknown provenance"
    )


def test_the_provenance_alert_has_its_own_cooldown_key(tmp_path, monkeypatch):
    """MUTANT: reuse the flood guard's `last_alert`. A flood alert would then silence the first
    provenance alert entirely, and the seat would never learn the record had rotted."""
    ntfy_utils.SENT_IDS_FILE.write_text("null", encoding="utf-8")
    stale_flood = responder._load_rate_state()
    stale_flood["last_alert"] = 9e9  # a flood alert "just" fired
    responder._save_rate_state(stale_flood)

    _, _, sent = _run(monkeypatch, tmp_path, HIS_ID)

    assert [m for m in sent if "[PROVENANCE GUARD]" in m]
    assert responder._load_rate_state()["last_provenance_alert"] > 0


# ---------------------------------------------------------------------------------------
# 2. THE NULL CONTROL -- absent and readable are DIFFERENT answers, and both let traffic move
# ---------------------------------------------------------------------------------------

def test_an_absent_record_still_lets_a_real_steer_through(tmp_path, monkeypatch):
    """REACHABILITY. Absent means nothing was ever sent, which is a fact, not a failure to read
    one -- so the director's message stages normally. Without this leg every assertion above is
    satisfied by a responder that quarantines unconditionally and never hears him again."""
    assert not ntfy_utils.SENT_IDS_FILE.exists()
    assert ntfy_utils.sent_ids_unreadable() is False, "absent is not unreadable"

    staged, quarantined, _ = _run(monkeypatch, tmp_path, HIS_ID)

    assert len(staged) == 1, "a real steer was withheld when the record was merely absent"
    assert quarantined == []


def test_a_readable_record_reaches_the_third_and_fourth_answers(tmp_path, monkeypatch):
    """With a LIVE prior the responder discriminates, which is the whole point of the record:
    our own id is skipped silently (no stage, no quarantine) and his is staged. Two answers that
    neither the absent nor the unreadable branch can produce."""
    ntfy_utils.SENT_IDS_FILE.write_text(json.dumps([OUR_OWN_ID, "id2"]), encoding="utf-8")

    staged, quarantined, _ = _run(monkeypatch, tmp_path, OUR_OWN_ID)
    assert staged == [] and quarantined == [], "our own outbound must be dropped, not preserved"

    staged, quarantined, _ = _run(monkeypatch, tmp_path, HIS_ID, msg_time=200_000)
    assert len(staged) == 1 and quarantined == []
