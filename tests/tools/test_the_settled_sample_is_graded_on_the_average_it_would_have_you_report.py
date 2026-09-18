"""Does the settled sample estimate the BOOK'S OWN AVERAGES better, or only its distribution?

WHY THIS IS A SEPARATE QUESTION FROM THE KS (2026-09-18). `grade()` answers "is the settled
sample's DISTRIBUTION closer to the population's", and §A's P1b holds on it at 1.66x on the worst
axis. **That is not the claim the sample has to earn.** The settled book is the population every
published figure is summed over — margin, carbon, the intervention ranking — and what those figures
inherit is the sample's ERROR ON THE MEAN.

Those can disagree. KS is driven by the worst point of the CDF; a mean is driven by the tails' mass.
A sample can be distributionally closer and estimate the average worse, and a book summed over it
would then be more wrong while the headline statistic improved.

Measured on the live campaign the day this was written, they agree and strongly — choosing beats
counting on all four axes, by 1.8x to 42.2x, and the cull's worst error is **+3.165% on
`raw_infiltration_ach`**: it reports a leakier book than exists, which on a gas-heated book
overstates space heat.

These legs are about the INSTRUMENT, not that result. They fix what the verdict may claim, so a
future run that disagrees is read as a disagreement rather than as a bug.
"""
from __future__ import annotations

import pytest

from tools.settlement_per_axis_gain import estimator_error, estimator_verdict

#: Four axes, matching `simulation.settlement_choice.CHOICE_AXES` in order.
POPULATION = [
    [10.0, 100.0, 1.0, 2.0],
    [20.0, 200.0, 2.0, 4.0],
    [30.0, 300.0, 3.0, 6.0],
    [40.0, 400.0, 4.0, 8.0],
]


def _arm(positions, weights):
    return {"positions": list(positions), "weights": list(weights)}


def test_a_perfectly_representative_arm_has_no_error():
    """The floor. An arm holding the whole population at equal weight cannot be wrong about it."""
    err = estimator_error(POPULATION, _arm(range(4), [1.0] * 4))
    for axis, row in err.items():
        assert row["signed_error_pct"] == pytest.approx(0.0, abs=1e-9), axis
        assert row["arm_mean"] == pytest.approx(row["population_mean"])


def test_the_error_is_SIGNED_because_too_high_and_too_low_are_different_errors():
    """A book 3% too leaky and one 3% too tight have different consequences for a gas-heated book.

    An absolute value would report them as the same, and the cull's real failure is directional —
    it OVERSTATES infiltration, so it overstates space heat, and the sign is the whole meaning.
    """
    high = estimator_error(POPULATION, _arm([3], [1.0]))     # the largest home only
    low = estimator_error(POPULATION, _arm([0], [1.0]))      # the smallest home only
    assert high["floor_area_m2"]["signed_error_pct"] > 0
    assert low["floor_area_m2"]["signed_error_pct"] < 0


def test_the_weights_are_honoured_and_not_just_the_positions():
    """A weighted sample is not its unweighted membership, and reading only positions would be a
    silent, plausible, wrong answer — the arm's whole point is that it carries weights."""
    flat = estimator_error(POPULATION, _arm([0, 3], [1.0, 1.0]))
    tilted = estimator_error(POPULATION, _arm([0, 3], [9.0, 1.0]))
    assert flat["floor_area_m2"]["arm_mean"] == pytest.approx(25.0)
    assert tilted["floor_area_m2"]["arm_mean"] == pytest.approx(13.0)


def test_an_arm_carrying_no_weight_refuses_rather_than_dividing_by_zero():
    """Nothing can be estimated from a sample of weight zero, and a zero mean would read as a real
    estimate of a very small book."""
    with pytest.raises(ValueError, match="no weight"):
        estimator_error(POPULATION, _arm([0, 1], [0.0, 0.0]))


def test_the_verdict_reaches_all_three_states():
    """Chosen-better, cull-better and SPLIT must each be reachable.

    A verdict that can only say one thing proves nothing about the sample, and the split state is
    the one that matters: it is what the live run would have to report if choosing helped some axes
    and hurt others.
    """
    cull = estimator_error(POPULATION, _arm([3], [1.0]))          # badly high
    close = estimator_error(POPULATION, _arm(range(4), [1.0] * 4))  # exact
    assert estimator_verdict(cull, close)["verdict"] == "CHOOSING ESTIMATES THE BOOK BETTER"
    assert estimator_verdict(close, cull)["verdict"] == "COUNTING ESTIMATES THE BOOK BETTER"

    # SPLIT: chosen wins one axis and loses another. Built by hand because a real arm that splits
    # cleanly is hard to construct, and the state must be reachable to be trusted.
    err_cull = {"floor_area_m2": {"signed_error_pct": 5.0},
                "fabric_w_per_k": {"signed_error_pct": 0.1},
                "raw_infiltration_ach": {"signed_error_pct": 0.1},
                "customer_years": {"signed_error_pct": 0.1}}
    err_chosen = {"floor_area_m2": {"signed_error_pct": 1.0},
                  "fabric_w_per_k": {"signed_error_pct": 5.0},
                  "raw_infiltration_ach": {"signed_error_pct": 5.0},
                  "customer_years": {"signed_error_pct": 5.0}}
    split = estimator_verdict(err_cull, err_chosen)
    assert split["verdict"].startswith("SPLIT")
    assert split["axes_where_choosing_estimates_better"] == 1
    assert split["axes_graded"] == 4


def test_a_split_is_never_resolved_by_majority():
    """Three axes better and one worse is a SPLIT, not a win.

    A book is summed over all four axes at once, so a majority verdict would let a real
    deterioration on one axis be voted away by the others.
    """
    err_cull = {a: {"signed_error_pct": 5.0} for a in
                ("floor_area_m2", "fabric_w_per_k", "raw_infiltration_ach", "customer_years")}
    err_chosen = dict(err_cull)
    err_chosen = {a: {"signed_error_pct": 1.0} for a in err_cull}
    err_chosen["customer_years"] = {"signed_error_pct": 9.0}
    v = estimator_verdict(err_cull, err_chosen)
    assert v["verdict"].startswith("SPLIT")
    assert v["axes_where_choosing_estimates_better"] == 3
    assert "customer_years" not in v["axes_won"]


def test_an_axis_whose_population_mean_is_zero_is_not_graded():
    """Fails closed on the one input that makes a percentage error meaningless, rather than
    reporting an infinity as a result."""
    flat = [[0.0, 1.0, 1.0, 1.0], [0.0, 2.0, 2.0, 2.0]]
    err = estimator_error(flat, _arm([0, 1], [1.0, 1.0]))
    assert err["floor_area_m2"]["signed_error_pct"] is None
    v = estimator_verdict(err, err)
    assert "NOT GRADED" in v["per_axis"]["floor_area_m2"]["verdict"]
    assert v["axes_graded"] == 3
