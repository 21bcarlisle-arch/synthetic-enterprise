"""Filed evidence is matched to a world, and a world with none refuses instead of falling back.

THE DEFECT (2026-09-16). `settlement_per_axis_gain` held ONE filed record, measured 2026-09-11 at
base `3957ba848`. On 2026-09-15 it stopped reproducing and the cause was established rather than
suspected: the fitted-joint home draw (`0d86d6dfe`) is not an ancestor of that base, so a KS over
the fabric axes was comparing statistics about two different housing stocks. The refusal was
CORRECT and was never a tolerance to widen.

But a correct refusal is not a population, and this one left §A's P1b ungradable for five days --
on the very claim the director's Stage 1 ask names, that the sample earn its place on the
settlement selection. Re-pointing the one record at today's numbers would have re-created the same
staleness the next time the stock moves: a control keyed to today's answer goes red when the code
becomes more honest and stays green when the claim rots.

So the record is keyed to its WORLD (departure-level digest + home-stock digest), and these are the
legs that make that keying able to fail. They are deliberately NOT about the arithmetic -- the
arithmetic already had its own self-check, and it was right.
"""
from __future__ import annotations

import pytest

from tools import settlement_per_axis_gain as spg


def _live_world():
    from simulation.departure_level_anchor import world_level_identity
    from simulation.world_home_identity import home_stock_identity
    return world_level_identity()["digest"], home_stock_identity()["digest"]


def test_this_world_has_filed_evidence_and_it_is_the_entry_measured_in_it():
    """The whole point of the re-file: the claim is gradable on the world we actually run."""
    record, why = _filed = spg._filed_for_this_world()
    assert why == "", why
    assert record is not None
    level, homes = _live_world()
    assert record["world"]["level_digest"] == level
    assert record["world"]["home_digest"] == homes
    del _filed


def test_a_world_no_entry_was_measured_in_refuses_and_names_what_it_has(monkeypatch):
    """The branch that matters, and it must be REACHABLE -- not merely correct when unreached.

    A guard that refuses everything passes every test asking whether it refuses correctly; a guard
    that accepts everything passes every test asking whether it accepts. This is the accept/refuse
    partition's other half.
    """
    import simulation.world_home_identity as whi
    monkeypatch.setattr(whi, "home_stock_identity",
                        lambda **kw: {"digest": "0000000000000000"})
    record, why = spg._filed_for_this_world()
    assert record is None
    assert "no filed evidence was measured in this world" in why
    assert "0000000000000000" in why, "the refusal must name the world it could not match"
    for entry in spg.FILED_RECORDS:
        assert entry["filed"] in why, "and the entries it does have, so nobody re-derives them"
    assert "do not re-point an existing entry" in why


def test_a_null_home_digest_never_matches_a_live_world(monkeypatch):
    """`None` on the 09-11 entry means "there was no field to fill", NOT "matches anything".

    This is the trap the whole shape turns on. A missing stamp that compares equal to a live digest
    would silently restore the exact defect the world keying exists to end -- and would do it
    quietly, which is how every control in this project has failed.
    """
    import simulation.departure_level_anchor as dla
    import simulation.world_home_identity as whi
    old = spg.FILED_RECORDS[0]
    assert old["filed"] == "2026-09-11" and old["world"]["home_digest"] is None

    monkeypatch.setattr(dla, "world_level_identity",
                        lambda *a, **k: {"digest": old["world"]["level_digest"]})
    monkeypatch.setattr(whi, "home_stock_identity", lambda **kw: {"digest": "abc123abc123abc1"})
    record, why = spg._filed_for_this_world()
    assert record is None, "the 09-11 entry matched on a null home digest"
    assert "no filed evidence was measured in this world" in why


@pytest.mark.parametrize("broken", ["level", "homes"])
def test_an_unreadable_digest_refuses_and_does_not_fall_back_to_the_newest_entry(monkeypatch, broken):
    """Fails CLOSED. "I cannot tell which world this is" is not "this is the newest world".

    Collapsing those two is how a figure measured in one world comes to bound a figure from
    another, which is the class this repository has now found in four separate readers.
    """
    import simulation.departure_level_anchor as dla
    import simulation.world_home_identity as whi
    if broken == "level":
        monkeypatch.setattr(dla, "world_level_identity", lambda *a, **k: {"digest": None})
    else:
        monkeypatch.setattr(whi, "home_stock_identity", lambda **kw: {"digest": None})

    record, why = spg._filed_for_this_world()
    assert record is None
    assert "could not be read" in why and "nothing is graded" in why


def test_an_exception_reading_the_world_is_cannot_establish_not_fine(monkeypatch):
    import simulation.world_home_identity as whi

    def _boom(**kw):
        raise RuntimeError("stock artefact missing")

    monkeypatch.setattr(whi, "home_stock_identity", _boom)
    record, why = spg._filed_for_this_world()
    assert record is None
    assert "could not be identified" in why and "stock artefact missing" in why


def test_no_filed_record_is_one_disagreement_and_never_zero():
    """Passing None must not read as "nothing disagreed", which is what would grade the claim."""
    out = spg._self_check(arms={}, ks={}, filed=None)
    assert out == ["no filed evidence exists for this world"]


def test_the_refuted_prediction_is_kept_beside_the_result():
    """A wrong prediction kept next to its result is the only evidence it was filed beforehand."""
    filed_dates = [r["filed"] for r in spg.FILED_RECORDS]
    assert "2026-09-11" in filed_dates, (
        "the entry that P1b was originally filed against was deleted -- re-filing must never "
        "erase the record that shows the world moved"
    )
    old = next(r for r in spg.FILED_RECORDS if r["filed"] == "2026-09-11")
    assert old["world"]["home_digest_absent_because"], (
        "a null stamp must carry its reason, or the next reader cannot tell 'no field existed' "
        "from 'nobody filled it in'"
    )
