"""`benign` on the census answers ONE question, and two carriers were failing a different one.

THE CENSUS'S `benign` VERDICT MEANS: no write to this file can SHORTEN an episode. It is not a clean
bill of health. `.sent_ntfy_ids.json` and `.notify_transitions.json` are both correctly benign --
neither carries an episode-scoped field -- and both conflated ABSENT with PRESENT-BUT-UNREADABLE,
which is a different defect with a different consequence. Measured 2026-09-04:

    record_sent_id, prior = three ids we had sent
        LIVE PRIOR (control) -> ['id1','id2','id3','id_new']   was_sent_by_us('id1')=True
        missing file         -> ['id_new']                     was_sent_by_us('id1')=False  correct
        truncated / empty    -> ['id_new']                     was_sent_by_us('id1')=False  ALL LOST
        null / {"a": 1}      -> AttributeError inside the flock, on the send path

    _read_transitions
        null                 -> None, out of a function annotated `-> dict`

The first one matters because of what reads it. `was_sent_by_us` False for our OWN outbound is how
`ntfy_responder` captures it as INBOUND and stages a bogus `from_rich` -- a message carrying the
director's authority that he never sent. `record_sent_id`'s own docstring says the file exists to
prevent exactly that, and the flock it describes only ever protected against a race losing ONE id.

WHAT IS DELIBERATELY NOT PINNED HERE: what `was_sent_by_us` should ANSWER when it cannot tell. That
is a judgement about the responder's fail direction, and guessing it would produce a control nobody
chose. `sent_ids_unreadable()` makes the third state askable; the judgement is handed off.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import notify as notify_mod  # noqa: E402
from background import ntfy_utils  # noqa: E402

UNREADABLE = pytest.mark.parametrize("raw", [
    pytest.param('["a", "b"', id="truncated"),
    pytest.param("", id="empty-file"),
    pytest.param("null", id="json-null"),
    pytest.param('{"a": 1}', id="a-mapping"),
    pytest.param('"abc"', id="a-bare-string"),
])


@pytest.fixture
def sent_ids(tmp_path, monkeypatch):
    """The real `SENT_IDS_FILE` is a hardcoded ABSOLUTE path into the shared tree, so it is
    monkeypatched rather than derived -- a test that wrote the live one would be writing a
    protected observability surface."""
    p = tmp_path / ".sent_ntfy_ids.json"
    monkeypatch.setattr(ntfy_utils, "SENT_IDS_FILE", p)
    return p


def test_recording_onto_a_readable_file_keeps_every_earlier_id(sent_ids):
    """REACHABILITY. Without this leg the assertions below are satisfiable by a recorder that
    remembers nothing at all, which is close to what the unreadable path actually did."""
    sent_ids.write_text(json.dumps(["id1", "id2", "id3"]))
    ntfy_utils.record_sent_id("id_new")
    assert json.loads(sent_ids.read_text()) == ["id1", "id2", "id3", "id_new"]
    assert ntfy_utils.was_sent_by_us("id1") is True


@UNREADABLE
def test_an_unreadable_sent_ids_file_is_never_silently_destroyed_by_the_next_send(sent_ids, raw):
    """MUTATION: drop the `_preserve_unreadable_sent_ids()` call and this fires.

    The send must still go -- a notifier that dies of its own bookkeeping is worse than a lost id
    -- so the new list is written either way. What must not happen is the old bytes vanishing with
    it: they are the only record of which outbound messages were ours.
    """
    sent_ids.write_text(raw)
    ntfy_utils.record_sent_id("id_new")

    assert json.loads(sent_ids.read_text()) == ["id_new"], "the send must still be recorded"
    kept = sent_ids.with_name(sent_ids.name + ".unreadable")
    assert kept.is_file() and kept.read_text() == raw, (
        "the unreadable sent-ids file was overwritten, and with it every id proving our own "
        "outbound was ours")


def test_a_missing_sent_ids_file_is_told_apart_from_an_unreadable_one(sent_ids):
    """The two must DIFFER, never take one branch. MUTATION: make `sent_ids_unreadable` return
    False for a corrupt file, or preserve bytes on the absent path too, and this fires."""
    assert ntfy_utils.sent_ids_unreadable() is False, "no file means nothing was ever sent"
    ntfy_utils.record_sent_id("first")
    assert ntfy_utils.sent_ids_unreadable() is False

    sent_ids.write_text('["a", "b"')
    assert ntfy_utils.sent_ids_unreadable() is True, (
        "a file that is THERE and cannot be parsed is not the same fact as no file at all")


@pytest.mark.parametrize("raw", ["null", '{"a": 1}', '"abc"', "[1, 2, 3]"])
def test_a_file_that_PARSES_but_is_not_a_list_of_ids_is_unreadable_too(sent_ids, raw):
    """The legs that PARSE are the ones that escape every except-clause, and the first draft of
    this file tested only the truncated case -- which takes the `except` branch, so replacing the
    final screen with `return False` survived. Caught by mutation, and it was a MISSING TEST rather
    than an equivalence: `null`, a mapping, a bare string and a list of ints all reach the last
    line of `sent_ids_unreadable` and none of them is a record of what we sent.

    MUTATION: `return False` on that last line, and this fires.
    """
    sent_ids.write_text(raw)
    assert ntfy_utils.sent_ids_unreadable() is True


@UNREADABLE
def test_no_member_of_the_partition_raises_on_the_send_path(sent_ids, raw):
    """MUTATION: restore the bare `ids = json.loads(...)` / `ids.append(msg_id)` pair and the
    `null` and mapping cases raise AttributeError -- inside the flock, on every ntfy send."""
    sent_ids.write_text(raw)
    ntfy_utils.record_sent_id("id_new")
    assert ntfy_utils.was_sent_by_us("id_new") is True


def test_a_corrupt_sent_ids_file_can_never_claim_an_id_nobody_sent(sent_ids):
    """MUTATION: drop the `isinstance(ids, list)` screen in `was_sent_by_us` and this fires.

    `json.loads('"abc"')` is a STRING, and `msg_id in "abc"` is a substring test -- so a corrupt
    file could answer True for an id that was never recorded, which is the opposite failure to the
    one in the docstring and just as capable of misrouting a message.
    """
    sent_ids.write_text('"abcdef"')
    assert ntfy_utils.was_sent_by_us("abc") is False, (
        "a substring of a corrupt file's contents was accepted as an id we had sent")


@UNREADABLE
def test_the_transition_memory_always_returns_a_dict(tmp_path, monkeypatch, raw):
    """MUTATION: drop the `isinstance(loaded, dict)` screen and `null` returns None from a
    function annotated `-> dict`, one `.get` away from every caller. `-> dict` is not
    enforcement, which is the same lesson `episode_prior` was built on."""
    p = tmp_path / ".notify_transitions.json"
    p.write_text(raw)
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", p)
    assert isinstance(notify_mod._read_transitions(), dict)


def test_the_transition_memory_reaches_a_different_answer_when_readable(tmp_path, monkeypatch):
    """REACHABILITY: `isinstance(x, dict)` is satisfied by a function that returns `{}` always."""
    p = tmp_path / ".notify_transitions.json"
    p.write_text(json.dumps({"k": {"state": "RED", "ts": 1.0}}))
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", p)
    assert notify_mod._read_transitions()["k"]["state"] == "RED"
