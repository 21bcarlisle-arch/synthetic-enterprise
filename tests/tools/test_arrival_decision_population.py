"""Controls on the two-world decision-population instrument.

EACH TEST NAMES THE DEFECT IT EXISTS FOR. The three that matter are the ones that would let this
instrument publish a comfortable number it had not measured: a rebind that reached no call site, a
verdict that cannot say "not at all", and a null width taken from the other leg's roster.
"""
from __future__ import annotations

import math

import pytest

from tools.arrival_decision_population import (
    LEG_OFF,
    LEG_ON,
    Z_95,
    _assert_the_patch_fired,
    _verdict,
    fold,
)


def _roster(retained: int, left: int, *, spread: float = 0.01) -> list[dict]:
    """A scored roster with a real signal, so the AUC is not degenerate and ties are few."""
    rows = []
    for i in range(retained):
        rows.append({"account": f"R{i}", "term_start": "2019-01-01",
                     "believed_p_retain": 0.6 + i * spread, "retained": True})
    for i in range(left):
        rows.append({"account": f"L{i}", "term_start": "2019-01-01",
                     "believed_p_retain": 0.4 + i * spread, "retained": False})
    return rows


def _leg(name: str, roster: list[dict], *, svt: int, priced: int) -> dict:
    stages = [{"stage": "acquisition_term", "count": 10},
              {"stage": "product_not_upliftable", "count": 100},
              {"stage": "declined", "count": 0},
              {"stage": "priced", "count": priced}]
    return {
        "leg": name,
        "roster_tariff_type_census": {"svt_records": svt},
        "pass_seconds": 1.0,
        "renewal_funnel": {
            "available": True,
            "renewals_the_world_offered": 110 + priced,
            "priced": priced,
            "declined": 0,
            "stages": stages,
            "product_not_upliftable_by_tariff_type": {"'svt'": 100},
            "decisions_that_existed": {"decisions_that_existed": priced},
        },
        "belief_vs_outcome": {
            "scored_decisions": roster,
            "discrimination_auc": 0.62,
        },
    }


def test_an_off_leg_that_drew_an_svt_record_raises_because_the_rebind_did_not_reach_the_draw():
    """THE INERT PATCH. A rebind applied after `run_phase2b` binds its book reaches the draw module
    and changes nothing; the two legs are then one world and their difference is zero for a reason
    that has nothing to do with the producer."""
    with pytest.raises(AssertionError, match="rebind did not reach the draw"):
        _assert_the_patch_fired(LEG_OFF, {"svt_records": 1})


def test_an_on_leg_with_no_svt_record_raises_rather_than_reporting_a_costless_producer():
    """THE MIRROR, and it is a different failure: the producer reaching no account on this roster.
    Both directions are asserted because a counter that can only fail one way leaves the other
    world unmeasured and the flattering headline standing."""
    with pytest.raises(AssertionError, match="reached no account"):
        _assert_the_patch_fired(LEG_ON, {"svt_records": 0})


def test_both_legs_pass_their_counter_in_the_state_the_instrument_is_built_to_produce():
    """THE PARTITION'S OTHER HALF. A counter that refused EVERYTHING would pass both tests above,
    so the reachable-pass branch is asserted here rather than assumed."""
    _assert_the_patch_fired(LEG_OFF, {"svt_records": 0})
    _assert_the_patch_fired(LEG_ON, {"svt_records": 35})


def test_the_verdict_can_say_all_three_things_including_not_at_all():
    """A VERDICT PINNED TO ONE ANSWER. The question is whether the rank leg got cheaper, stayed the
    same, or did not move; a function that cannot reach 'not at all' would report every widening as
    'the same' and the route would close on a reading it never made."""
    assert "cheaper" in _verdict(0.80)
    assert "the same" in _verdict(1.00)
    assert "NOT AT ALL" in _verdict(1.30)
    assert "cannot tell" in _verdict(None)


def test_each_legs_width_is_computed_from_its_own_roster_and_not_from_the_other_legs():
    """THE BORROWED RULER, which is the defect `_auc_against_its_own_null` was repaired for on
    2026-09-19 one instrument over: a null taken from one run and applied to another. The two legs
    here have deliberately different outcome counts, so a fold that graded both with one ruler
    would publish identical widths."""
    off = _leg(LEG_OFF, _roster(60, 44), svt=0, priced=104)
    on = _leg(LEG_ON, _roster(30, 20), svt=35, priced=50)
    folded = fold(off, on)

    widths = folded["null_half_width_95"]
    assert widths[LEG_OFF] == pytest.approx(Z_95 * math.sqrt(105 / (12.0 * 60 * 44)), rel=1e-3)
    assert widths[LEG_ON] == pytest.approx(Z_95 * math.sqrt(51 / (12.0 * 30 * 20)), rel=1e-3)
    assert widths[LEG_ON] > widths[LEG_OFF]
    assert folded["null_half_width_ratio_on_over_off"] > 1.05
    assert "NOT AT ALL" in folded["did_the_rank_leg_get_cheaper"]
    assert folded["scored_decisions_delta"] == -54


def test_the_fold_reports_the_decision_counts_the_legs_own_funnels_derived():
    """The counts must be the funnels' own, never re-derived here: a counter carrying its own copy
    of the eligibility rule is how a funnel comes to report a population its subject does not
    have."""
    folded = fold(_leg(LEG_OFF, _roster(60, 44), svt=0, priced=104),
                  _leg(LEG_ON, _roster(55, 40), svt=35, priced=95))
    assert folded["legs"][LEG_OFF]["decisions_that_existed"] == 104
    assert folded["legs"][LEG_ON]["decisions_that_existed"] == 95
    assert folded["decisions_that_existed_delta"] == -9


def test_a_leg_with_one_empty_outcome_class_is_cannot_tell_rather_than_a_null_of_no_width():
    """FAIL-CLOSED. An empty outcome class has no rank statistic and therefore no null; a zero
    width would read as a null every observed value clears."""
    off = _leg(LEG_OFF, _roster(60, 44), svt=0, priced=104)
    on = _leg(LEG_ON, _roster(40, 0), svt=35, priced=40)
    folded = fold(off, on)
    assert folded["null_half_width_95"][LEG_ON] is None
    assert "cannot tell" in folded["did_the_rank_leg_get_cheaper"]


def test_halving_the_half_width_needs_about_four_times_the_decisions():
    """The arithmetic the question turns on, asserted as a PROPERTY (~1/sqrt(n)) rather than
    against today's answer, so it stays true when the book grows."""
    folded = fold(_leg(LEG_OFF, _roster(60, 44), svt=0, priced=104),
                  _leg(LEG_ON, _roster(55, 40), svt=35, priced=95))
    needed = folded["scored_decisions_needed_to_halve_the_off_legs_half_width"]
    assert 3.5 * 104 < needed < 4.5 * 104
