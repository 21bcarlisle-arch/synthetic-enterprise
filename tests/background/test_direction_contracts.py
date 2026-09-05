"""The contracts `background/direction.py` states in prose, proved BESIDE THE MODULE.

WHY THIS FILE EXISTS, and it is not that the contracts were untested. Six of the eight were tested.
They were tested in `test_delivery_seat.py` and
`test_the_self_audit_declared_a_correction_and_nothing_carried_it.py` -- suites belonging to other
modules, which is where whoever needed the behaviour happened to be working at the time. Measured
2026-09-05 by mutation, per caller suite
(`SEAT_FINDING_THE_DRAWS_OWN_RULE_0_IS_PROVED_BY_THE_WRITERS_SUITE_AND_NOT_THE_READERS_2026-09-05`):

    contract                                        proved by
    focus_multiplier ALWAYS >= 1.0                  test_delivery_seat.py
    forbidden keys refused at any depth             test_delivery_seat.py
    an empty not_now is refused                     test_delivery_seat.py
    read_direction NEVER RAISES                     test_delivery_lane.py + test_delivery_seat.py
    corrected must be a BOOLEAN                     test_the_self_audit...py
    a legacy wrong row is None, not False           test_the_self_audit...py
    focus_weights untouched on length mismatch      NOTHING
    is_live bounded BELOW as well as above          NOTHING

The first line is the one that mattered. `focus_multiplier` is the only thing in the module
annotated `MUTATION (must fire):`, it has no external caller, and it is reached only through
`focus_weights` -- whose four call sites are ALL in `background/supervisor.py`, the module that by
design cannot see `delivery_seat.py`. And `test_supervisor.py` cannot prove it either: line 150 of
its shared fixture points `DIRECTION_PATH` at a tmp file nothing writes, so `focus_weights`
short-circuits at `if not focus` and `focus_multiplier` is invoked ZERO times in that suite's 200
tests. Correct isolation, and it means the consumer's suite can never fail when the consumed
contract breaks.

So this file is not a duplicate of those tests. It is the module's own suite, keyed to the
PROPERTIES rather than to whichever caller happens to exist, so that a contract's proof stops being
an accident of refactoring order. Every test below names the defect it exists to catch.

Every one of these calls passes `path=` explicitly. `direction` takes a path on every read, so
nothing here needs to monkeypatch a module attribute -- and an isolation guard keyed to a mutable
module attribute is defeated by the very monkeypatch that documents it.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from background import direction as d


def _record(**over) -> dict:
    """A minimal record that VALIDATES, so each test below breaks exactly one thing."""
    base = {
        "version": 1,
        "oriented_at": datetime.now(timezone.utc).isoformat(),
        "focus": [{"id": "atom-a", "why": "because"}],
        "not_now": [{"what": "something else", "why": "later"}],
    }
    base.update(over)
    return base


def _write(tmp_path, record: dict | str):
    import yaml
    path = tmp_path / "DIRECTION.yaml"
    path.write_text(record if isinstance(record, str) else yaml.safe_dump(record),
                    encoding="utf-8")
    return path


def test_the_fixture_record_is_actually_VALID_or_every_test_below_passes_vacuously():
    """THE VACUITY GUARD. Every test here breaks one field of `_record()` and asserts a refusal.
    If `_record()` were itself invalid they would all pass for the wrong reason, and this file
    would be eight controls that cannot fail."""
    assert d.validate(_record()) == []


# ── focus_multiplier: A WEIGHT, NEVER A GATE ────────────────────────────────


def test_direction_can_only_ADD_attention_across_the_WHOLE_partition():
    """Defect: `focus_multiplier` returns below 1.0 for some atom, making direction a filter
    wearing a weight's clothes -- and a direction record able to make work HARDER to reach.

    Written over the whole partition rather than a leg per branch. A guard that returned 1.0 for
    everything would pass a per-branch test of the unnamed case; what makes this one able to fail
    is the companion assertion that every rank is REACHABLE and distinct.
    """
    focus = ("first", "second", "third", "fourth", "fifth")
    got = {a: d.focus_multiplier(a, focus) for a in (*focus, "unnamed", "")}

    assert min(got.values()) >= 1.0, f"direction filtered something: {got}"
    # The rare branches are reachable AND distinct -- without this the test above is satisfied by
    # a function that ignores focus entirely and always returns 1.0.
    assert got["first"] == 4.0 and got["second"] == 3.0 and got["third"] == 2.0
    assert got["fourth"] == got["fifth"] == 1.5, "the tail rank is unreachable"
    assert got["unnamed"] == got[""] == 1.0


def test_a_focus_record_can_never_ZERO_a_candidates_weight(tmp_path):
    """Defect: Rule 0 here -- a direction record empties the feasible set, so the draw becomes
    unable to reach something rather than merely slower to."""
    path = _write(tmp_path, _record(focus=[{"id": "atom-a", "why": "w"}]))
    cands = [{"id": "atom-a"}, {"id": "atom-b"}]
    out = d.focus_weights(cands, [1.0, 1.0], path=path)
    assert all(w > 0 for w in out), out
    assert out[0] > out[1], "the steer did not bite at all"


def test_a_MISMATCHED_candidate_list_leaves_the_weights_BYTE_IDENTICAL(tmp_path):
    """Defect: a bug in advice changes a draw. When the two lists disagree in length the bias is
    meaningless, and returning a partial or zipped result would silently reweight the wrong atoms.

    PROVED BY NOTHING before this file -- mutation M2 survived all four caller suites.
    """
    path = _write(tmp_path, _record(focus=[{"id": "atom-a", "why": "w"}]))
    weights = [1.0, 2.0, 3.0]
    cands = [{"id": "atom-a"}]  # deliberately shorter
    assert d.focus_weights(cands, weights, path=path) == weights
    # ...and the same call with the lists AGREEING does change something, so the assertion above
    # is not passing merely because the record failed to load.
    agreeing = d.focus_weights([{"id": "atom-a"}], [1.0], path=path)
    assert agreeing == [4.0], agreeing


# ── validate(): the record may say WHAT TO WORK ON, never WHAT COUNTS AS SUCCESS ──


@pytest.mark.parametrize("depth_builder,label", [
    (lambda k: {k: 3}, "top level"),
    (lambda k: {"focus": [{"id": "a", "why": "w", k: 3}]}, "inside a list of dicts"),
    (lambda k: {"stretch_reviewed": {"a": {"b": {k: 3}}}}, "three dicts deep"),
])
@pytest.mark.parametrize("key", ["target", "kpi", "benchmark", "THRESHOLD", " Metrics "])
def test_a_TARGET_SHAPED_key_is_refused_AT_ANY_DEPTH(depth_builder, label, key):
    """Defect: `_forbidden_keys_in` stops recursing, so a target buried one level down is accepted
    and the next stretch optimises it. R12's whole subject."""
    problems = d.validate(_record(**depth_builder(key)))
    assert any("target-shaped" in p for p in problems), f"{key!r} {label} was accepted: {problems}"


def test_a_number_in_the_PROSE_is_not_a_target():
    """Defect: the check keys off the prose rather than the key, so quoting a measurement in a
    `why` is refused -- which buys vagueness and nothing else. The INVERSE of the test above, and
    without it a guard that refused everything would pass that one."""
    assert d.validate(_record(focus=[{"id": "a", "why": "the belief error is +0.5pp"}])) == []


def test_a_direction_that_REJECTED_NOTHING_is_refused():
    """Defect: a record listing only what was chosen hides the judgement it exists to expose."""
    for empty in ([], None):
        problems = d.validate(_record(not_now=empty))
        assert any("not_now is empty" in p for p in problems), (empty, problems)


@pytest.mark.parametrize("corrected,ok", [
    (True, True), (False, True),
    ("yes", False), (1, False), (None, False), ("", False),
])
def test_a_recorded_ERROR_needs_a_BOOLEAN_correction_state(corrected, ok):
    """Defect: `corrected` accepted as merely PRESENT. A string `"yes"` is not a grade -- it cannot
    be counted, and it reads from outside exactly like an honest boolean."""
    row = {"what": "something went wrong"}
    if corrected is not None or not ok:
        row["corrected"] = corrected
    problems = [p for p in d.validate(_record(wrong=[row])) if "corrected" in p]
    assert (problems == []) is ok, (corrected, problems)


# ── read_direction: FAIL-SOFT, and the breadth is the point ─────────────────


def test_read_direction_NEVER_RAISES_whatever_is_wrong_with_the_file(tmp_path):
    """Defect: the `except` is narrowed to one error class, so an unreadable-but-present record
    wedges the draw instead of yielding no advice. Missing, unreadable and malformed are ONE
    answer -- advice that wedges the draw when it goes missing is worse than no advice.

    The three cases are deliberately different EXCEPTION FAMILIES: FileNotFoundError, a non-OSError
    OSError, and a yaml error that is not an OSError at all.
    """
    missing = tmp_path / "nope" / "DIRECTION.yaml"
    a_directory = tmp_path / "is_a_dir"
    a_directory.mkdir()
    malformed = _write(tmp_path, "this: [is not: valid yaml\n")
    not_a_mapping = _write(tmp_path, "- just\n- a\n- list\n")

    for path in (missing, a_directory, malformed, not_a_mapping):
        assert d.read_direction(path=path) is None, path
        assert d.current_focus(path=path) == ()
        assert d.unreachable_focus(["atom-a"], path=path) == []


def test_a_BROKEN_record_leaves_the_draw_BYTE_IDENTICAL(tmp_path):
    """Defect: a broken record changes the draw rather than simply not steering it."""
    broken = _write(tmp_path, "this: [is not: valid yaml\n")
    weights = [1.0, 2.0, 3.0]
    cands = [{"id": "atom-a"}, {"id": "atom-b"}, {"id": "atom-c"}]
    assert d.focus_weights(cands, weights, path=broken) == weights


# ── is_live: bounded BELOW as well as above ────────────────────────────────


@pytest.mark.parametrize("age_hours,live", [
    (0.0, True),
    (d.FOCUS_MAX_AGE_HOURS - 0.1, True),
    (d.FOCUS_MAX_AGE_HOURS + 0.1, False),      # stale: steers toward what mattered yesterday
    (-0.5, False),                              # FUTURE-DATED
    (-100.0, False),
])
def test_a_FUTURE_DATED_record_does_not_steer_any_more_than_a_STALE_one(tmp_path, age_hours, live):
    """Defect: the lower bound is dropped, so a record stamped in the future steers for ever --
    it can never age out, because its age only ever grows toward zero. A clock skew or a bad stamp
    then pins the draw to one orientation permanently.

    PROVED BY NOTHING before this file -- mutation M7 survived all four caller suites.
    """
    now = datetime.now(timezone.utc)
    stamp = now - timedelta(hours=age_hours)
    path = _write(tmp_path, _record(oriented_at=stamp.isoformat(),
                                    focus=[{"id": "atom-a", "why": "w"}]))
    assert d.current_focus(path=path, now=now) == (("atom-a",) if live else ())
    assert d.unreachable_focus([], path=path, now=now) != [] if live else True
    record = d.read_direction(path=path)
    assert record is not None and record.is_live(now) is live


# ── wrong_rows: an unknown is not a failure ────────────────────────────────


@pytest.mark.parametrize("stored,expected", [
    ([{"what": "a", "corrected": True}], [{"what": "a", "corrected": True}]),
    ([{"what": "a", "corrected": False}], [{"what": "a", "corrected": False}]),
    (["a legacy bare string"], [{"what": "a legacy bare string", "corrected": None}]),
    ([{"what": "a"}], [{"what": "a", "corrected": None}]),
    ([{"what": "a", "corrected": "yes"}], [{"what": "a", "corrected": None}]),
])
def test_an_UNRECORDED_correction_state_is_None_and_never_False(stored, expected):
    """Defect: a legacy row reads as `corrected: False`. "we did not record whether this was fixed"
    and "this was not fixed" are DIFFERENT CLAIMS and only one of them is true -- and the published
    panel counts the second one as an outstanding error the seat never made.

    69 recorded orientations carry the legacy shape and they are an append-only record, so they are
    read rather than rewritten.
    """
    assert d.wrong_rows({"wrong": stored}) == expected
