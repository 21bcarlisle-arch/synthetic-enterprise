"""The three carriers the census had never dispositioned answered "I cannot read this" as "nothing".

WHY THIS FILE EXISTS AND `test_episode_prior_partition.py` COULD NOT HAVE CAUGHT IT. That control
derives its subject from the self-clearing-alarm census's own `real` rows -- deliberately, so a new
carrier of the class fails there rather than joining it quietly. A derived subject has one blind
spot, exactly where the derivation reads nothing: **a carrier with NO disposition row is in no
verdict set, so it is outside that control by construction.** At `23c63e296` the census named three,
and `--check` had been exiting 1 on them:

    .weekly_rhythm.json           background/weekly_rhythm.py
    .seat_continuation.json       background/seat_continuation.py
    .sim_next_run_not_before.json background/sim_runner.py

All three conflated ABSENT with PRESENT-BUT-UNREADABLE, and two of them raised on a member of the
partition -- the same `json.loads` accepts `[1, 2, 3]` shape fixed in three other carriers the day
before, still live in these because nothing had ever looked at them.

WHAT EVERY LEG HERE ASSERTS IS THAT THE TWO ANSWERS **DIFFER**, never that they match. A control
that pins absent and unreadable to one branch holds the defect green while reading as deliberate,
which is how `guard_episode`'s `prev=None` survived two lanes' repairs. Each carrier also has a
REACHABILITY leg proving a readable prior reaches a THIRD answer -- without it, "differs" is
satisfiable by a carrier that answers the same thing to everything.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pytest

PROJECT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_DIR))

from background import seat_continuation as sc  # noqa: E402
from background import sim_runner  # noqa: E402
from background import weekly_rhythm as wr  # noqa: E402
from background.episode_prior import ABSENT, READABLE, UNREADABLE  # noqa: E402

#: Present-but-unreadable whatever the record's shape. `null` and `[1, 2, 3]` are in here on
#: purpose: they PARSE, which is exactly why an `except JSONDecodeError` never saw them.
_ALWAYS_UNREADABLE = [
    pytest.param('{"truncated": ', id="truncated"),
    pytest.param("", id="empty-file"),
    pytest.param("null", id="json-null"),
    pytest.param("[1, 2, 3]", id="not-a-mapping"),
]

#: A MAPPING WITH THE WRONG CONTENTS IS NOT ONE FACT ACROSS THE THREE, and pretending it is would
#: be this sweep's own defect wearing the other coat. For the baton and the continuation store it
#: is present-but-unreadable -- a baton whose `step` is not a step, or a store that is not a list
#: of entries, is a file that was written and cannot be trusted. For the deadline it is a perfectly
#: readable state that simply does not carry the key, which is a THIRD answer and is pinned as one
#: by `test_a_deadline_file_missing_only_its_key_is_a_third_answer`.
UNREADABLE_BYTES = pytest.mark.parametrize(
    "raw", [*_ALWAYS_UNREADABLE, pytest.param('{"unrelated": 1}', id="mapping-that-is-not-this-record")]
)
UNREADABLE_BYTES_ANY_RECORD = pytest.mark.parametrize("raw", _ALWAYS_UNREADABLE)

OPEN_BATON = json.dumps({
    "step": "monday_ranking", "due_on": "2026-09-01", "armed_by": "bootstrap",
    "armed_at": "2026-08-31T09:00:00+01:00", "opened_at": "2026-09-01T09:00:00+01:00",
    "closed_at": None, "finding_filed_for": None,
})
TWO_LIVE = json.dumps([
    {"id": "alpha", "what": "w", "why": "y", "done_means": "d", "written_at": 9e9},
    {"id": "beta", "what": "w", "why": "y", "done_means": "d", "written_at": 9e9},
])


def _tick_at(path, staging, day=4):
    return wr.tick(now=datetime(2026, 9, day, 9, 0, tzinfo=wr.LONDON), path=path, staging=staging)


# --------------------------------------------------------------------------------------
# 1. weekly_rhythm -- the baton's `due_on` IS an episode start and `days_late` is read off it
# --------------------------------------------------------------------------------------

def test_the_rhythm_reaches_a_third_answer_when_the_baton_IS_readable(tmp_path):
    """REACHABILITY. Without this leg every assertion below is satisfiable by a tick that answers
    BOOTSTRAP to everything -- which is precisely what it did before this sweep."""
    baton = tmp_path / "baton.json"
    baton.write_text(OPEN_BATON)
    out = _tick_at(baton, tmp_path)
    assert out["action"] == "FINDING" and out["days_late"] == 3, (
        "a readable, open, three-days-late baton must reach the FINDING the rhythm exists to file")
    assert wr.read_baton_with_verdict(baton)[1] == READABLE


@UNREADABLE_BYTES
def test_an_unreadable_baton_is_told_apart_from_no_baton_and_its_bytes_survive(tmp_path, raw):
    """MUTATION: make `read_baton_with_verdict` return ABSENT for an unreadable baton, or drop the
    `_preserve_unreadable_baton` call, and this fires.

    Both rebuild -- the rhythm must keep running and never files a document about itself. What must
    differ is the RECORD: an unreadable baton is a step that may have been open and lost, so the
    rebuild says so and the bytes are kept. `due_on` moving forward on a file we could not read is
    the 2026-08-09 self-clearing shape, and here the write also destroyed the evidence.
    """
    absent = tmp_path / "gone.json"
    unreadable = tmp_path / "broken.json"
    unreadable.write_text(raw)

    assert wr.read_baton_with_verdict(absent)[1] == ABSENT
    assert wr.read_baton_with_verdict(unreadable)[1] == UNREADABLE, (
        "a file that is THERE and cannot be trusted is not the same fact as no file at all")

    from_absent = _tick_at(absent, tmp_path)
    from_unreadable = _tick_at(unreadable, tmp_path)

    assert not from_absent.get("prior_unreadable"), "a cold start must not claim a lost prior"
    assert from_unreadable.get("prior_unreadable") is True, (
        "the tick rebuilt over a baton it could not read and reported it as an ordinary cold start")
    assert json.loads(unreadable.read_text()).get("prior_unreadable") is True, (
        "the flag must be on the BATON: `daily_self_note` calls tick() as a passenger and throws "
        "the return value away, so a report living only there reaches nobody")
    kept = unreadable.with_name(unreadable.name + ".unreadable")
    assert kept.is_file() and kept.read_text() == raw, (
        "the bytes we could not read were destroyed by the rebuild that replaced them")


def test_a_second_unreadable_baton_never_overwrites_the_first_preserved_copy(tmp_path):
    """The FIRST loss is the one that still had the open step in it. MUTATION: drop the `exists()`
    skip in `_preserve_unreadable_baton` and the second corruption erases the first evidence."""
    baton = tmp_path / "baton.json"
    baton.write_text("first corruption")
    _tick_at(baton, tmp_path)
    baton.write_text("second corruption")
    _tick_at(baton, tmp_path)
    assert (tmp_path / "baton.json.unreadable").read_text() == "first corruption"
    assert (tmp_path / "baton.json.unreadable.1").read_text() == "second corruption"


# --------------------------------------------------------------------------------------
# 2. seat_continuation -- the READER is right to degrade to []; the WRITER must not write it back
# --------------------------------------------------------------------------------------

def test_a_handoff_onto_a_readable_store_reaches_a_third_answer(tmp_path):
    """REACHABILITY, and the thing the two legs below are measured against."""
    store = tmp_path / "cont.json"
    store.write_text(TWO_LIVE)
    sc.hand_off("gamma", "w", "y", "d", now=9e9, path=store)
    assert [i["id"] for i in json.loads(store.read_text())] == ["alpha", "beta", "gamma"]


@UNREADABLE_BYTES
def test_a_handoff_over_an_unreadable_store_keeps_the_entries_it_cannot_read(tmp_path, raw):
    """MUTATION: use `_load` instead of `_load_with_verdict` in `hand_off`, or make the loader
    report UNREADABLE as ABSENT, and this fires.

    `_load` returning `[]` to a reader is CORRECT and is not what was wrong -- `delivery_lane.draw`
    documents that a lane which can throw takes every other lane down. What was wrong is that `[]`
    was the whole answer, so a hand-off wrote a one-entry store over however many live
    continuations were in the one it could not parse. This is the only copy of that store.
    """
    absent = tmp_path / "gone.json"
    unreadable = tmp_path / "broken.json"
    unreadable.write_text(raw)

    assert sc._load_with_verdict(absent)[1] == ABSENT
    assert sc._load_with_verdict(unreadable)[1] == UNREADABLE

    sc.hand_off("gamma", "w", "y", "d", now=9e9, path=absent)
    sc.hand_off("gamma", "w", "y", "d", now=9e9, path=unreadable)

    from_absent = json.loads(absent.read_text())
    from_unreadable = json.loads(unreadable.read_text())
    assert "prior_store_unreadable_kept_at" not in from_absent[0], (
        "writing one entry over NOTHING is correct and must not claim a loss")
    assert from_unreadable[0]["prior_store_unreadable_kept_at"], (
        "the entry must record that it was written over a store that could not be read")
    kept = unreadable.with_name(unreadable.name + ".unreadable")
    assert kept.is_file() and kept.read_text() == raw, (
        "the unreadable store was overwritten, and with it every live continuation in it")


@UNREADABLE_BYTES
def test_no_reader_of_the_continuation_store_raises_on_any_member_of_the_partition(tmp_path, raw):
    """MUTATION: loosen the loader's element check back to `isinstance(raw, list)` and the
    `[1, 2, 3]` case raises `AttributeError: 'int' object has no attribute 'get'`.

    A JSON list of non-mappings IS a list, so checking only the OUTER type passed a shape the
    module cannot use through as if it were data -- and `live()` is on the draw's path.
    """
    store = tmp_path / "cont.json"
    store.write_text(raw)
    assert sc.live(now=9e9, path=store) == []
    assert sc.expired(now=9e9, path=store) == []
    assert sc.superseded(path=store) == []


# --------------------------------------------------------------------------------------
# 3. sim_runner -- the crash was the FIRST statement of main(), outside every try in the module
# --------------------------------------------------------------------------------------

def test_a_readable_deadline_still_holds_the_pause(tmp_path):
    """REACHABILITY: the refusals below are only meaningful if a real pause is reachable at all."""
    p = tmp_path / "next.json"
    p.write_text(json.dumps({"next_run_not_before": 1600.0}))
    owed, why = sim_runner.pause_owed_from_a_previous_process(now=1000.0, path=p)
    assert owed == 600.0 and "resuming" in why


@UNREADABLE_BYTES_ANY_RECORD
def test_an_unreadable_deadline_file_never_reports_itself_as_a_missing_one(tmp_path, raw):
    """MUTATION: return the ABSENT reason for an unreadable file, and this fires.

    The DECISION is the same for both and that asymmetry is argued at the function: a wrong 0.0
    costs one early run, a wrong large number parks the producer forever. The REASON is not the
    same, and it is the sentence an operator reads out of the log when the cadence looks wrong.
    """
    absent = tmp_path / "gone.json"
    unreadable = tmp_path / "broken.json"
    unreadable.write_text(raw)

    owed_absent, why_absent = sim_runner.pause_owed_from_a_previous_process(now=1000.0, path=absent)
    owed_bad, why_bad = sim_runner.pause_owed_from_a_previous_process(now=1000.0, path=unreadable)

    assert owed_absent == 0.0 and owed_bad == 0.0, "both must still fail toward RUNNING"
    assert why_absent != why_bad, (
        "a file that is present and unreadable was reported as 'no deadline was recorded'")
    assert "no deadline was recorded" in why_absent
    assert "present" in why_bad


def test_a_deadline_file_missing_only_its_key_is_a_third_answer(tmp_path):
    """ABSENT, UNREADABLE and READABLE-BUT-WITHOUT-THE-KEY are three facts, and the log line has to
    be able to tell an operator which one it met. Collapsing any two of them is the class this
    sweep is about, so the control names all three rather than the two it started with."""
    absent = tmp_path / "gone.json"
    unreadable = tmp_path / "broken.json"
    unreadable.write_text("null")
    no_key = tmp_path / "nokey.json"
    no_key.write_text(json.dumps({"unrelated": 1}))

    whys = [sim_runner.pause_owed_from_a_previous_process(now=1000.0, path=p)[1]
            for p in (absent, unreadable, no_key)]
    assert len(set(whys)) == 3, f"three distinct states gave {len(set(whys))} distinct reasons: {whys}"


def test_a_non_mapping_deadline_file_does_not_stop_the_producer_from_starting(tmp_path):
    """MUTATION: restore `(raw or {}).get(...)` and this raises instead of returning.

    `pause_owed_from_a_previous_process()` is the first statement of `sim_runner.main()` and is
    outside every `try` in that module, so this was not a wrong pause -- it was a producer daemon
    that could not start, from one line of JSON in a bookkeeping file it writes itself.
    """
    p = tmp_path / "next.json"
    p.write_text("[1, 2, 3]")
    owed, why = sim_runner.pause_owed_from_a_previous_process(now=1000.0, path=p)
    assert owed == 0.0 and why, "a non-mapping must be a refusal WITH a reason, never an exception"


# --------------------------------------------------------------------------------------
# 4. The property, keyed to the class rather than to these three files
# --------------------------------------------------------------------------------------

def test_every_carrier_swept_here_is_now_dispositioned_by_the_census(tmp_path):
    """Keyed to the PROPERTY, not to today's answer: these three are the carriers this file swept,
    and a row disappearing (or reverting to undispositioned) must go red HERE too rather than only
    in the census's own check -- because the census's check is what was red for them at HEAD."""
    from background import self_clearing_alarm_census as census
    disp = census.load_dispositions()
    for key in (".weekly_rhythm.json", ".seat_continuation.json", ".sim_next_run_not_before.json"):
        row = disp.get(key)
        assert isinstance(row, dict), f"{key} lost its disposition row"
        assert row.get("verdict") in ("real", "benign"), f"{key} carries no verdict"
        assert str(row.get("why", "")).strip(), f"{key} has a verdict with no reason"
