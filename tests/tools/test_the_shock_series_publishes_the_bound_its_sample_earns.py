"""The defect: a published mean whose reader has no way to tell it from a typical one.

`monthly_ops.monthly[].avg_shock_pct` published "315.6%" off five bill-shock events,
and "205.6%" off seven, with nothing beside either but a raw `shock_count`. The
standing rule is that a figure published without the bound its sample size earns is
worse than no figure, and a bare `n` is the raw material for that bound rather than
the bound itself.

Every control here is keyed to a PROPERTY of the published series, never to today's
numbers. A control pinned to "2016-08 reads 315.6%" would go red the moment the
series became more honest and stay green while the claim rotted.

REUSE: tests/tools/test_generate_dashboard_monthly.py is the existing home for
`extract_monthly_ops` and covers its AGGREGATION -- which months appear, what
`shock_count` counts, how the crisis flag is set. This file's subject is the
published CLAIM the aggregation makes: that a mean is readable, and that a reader
can tell which bills it is a mean over. Its central control asserts the aggregate
did NOT move, which is the opposite property to everything in that file.
"""
import statistics

import pytest

from tools.generate_dashboard_data import (
    _bootstrap_mean_interval,
    extract_monthly_ops,
)


def _events(month, pcts):
    return [
        {"customer_id": f"C{i}", "period_end": f"{month}-28", "bill_shock_pct": p}
        for i, p in enumerate(pcts)
    ]


def _series(**months):
    return {"years": {"2022": {"bill_shock_events": [
        e for m, pcts in months.items() for e in _events(m, pcts)
    ]}}}


def _row(result, month):
    return next(r for r in result["monthly"] if r["month"] == month)


# --------------------------------------------------------------------------
# The bound must be able to say "we cannot tell"
# --------------------------------------------------------------------------

def test_a_dispersed_month_publishes_a_wider_interval_than_a_tight_one_of_the_same_size():
    """The defect this kills: an interval that is a function of n alone.

    A bound derived only from sample size cannot distinguish five events that agree
    from five that do not, and would publish the same width for both -- a precision
    claim about the wrong thing. Same n, same mean, different dispersion.
    """
    r = extract_monthly_ops(_series(**{
        "2022-01": [0.50, 0.50, 0.50, 0.50, 0.50],
        "2022-02": [0.02, 0.10, 0.40, 0.90, 1.08],
    }))
    tight, spread = _row(r, "2022-01"), _row(r, "2022-02")
    assert tight["shock_count"] == spread["shock_count"] == 5
    assert tight["avg_shock_pct"] == pytest.approx(spread["avg_shock_pct"], abs=0.2)

    tight_w = tight["avg_shock_pct_ci95_high"] - tight["avg_shock_pct_ci95_low"]
    spread_w = spread["avg_shock_pct_ci95_high"] - spread["avg_shock_pct_ci95_low"]
    assert spread_w > tight_w, (
        f"same n and same mean, but the dispersed month's interval ({spread_w:.1f}pp) "
        f"is not wider than the tight month's ({tight_w:.1f}pp) -- the bound is "
        "keyed to sample size rather than to what the sample actually says"
    )


def test_a_month_that_cannot_bound_itself_publishes_null_and_not_a_narrow_interval():
    """FAIL-OPEN killer. A single observation has no spread, so a naive bootstrap
    resamples the same value every time and returns a ZERO-WIDTH interval -- which
    publishes perfect confidence off one bill. Null is the honest answer; a
    degenerate interval is the flattering one, and it is the one a reader would
    trust most."""
    r = extract_monthly_ops(_series(**{"2022-01": [7.5]}))
    row = _row(r, "2022-01")
    assert row["shock_count"] == 1
    assert row["avg_shock_pct_ci95_low"] is None
    assert row["avg_shock_pct_ci95_high"] is None


def test_the_interval_brackets_the_mean_it_is_the_bound_for():
    """A bound that does not contain its own point estimate is bounding something
    else. Checked across sizes so it is not a property of one fixture."""
    r = extract_monthly_ops(_series(**{
        "2022-01": [0.2, 0.9],
        "2022-02": [0.1, 0.3, 0.3, 2.4],
        "2022-03": [0.25] * 30,
    }))
    for month in ("2022-01", "2022-02", "2022-03"):
        row = _row(r, month)
        assert row["avg_shock_pct_ci95_low"] <= row["avg_shock_pct"] <= row["avg_shock_pct_ci95_high"], (
            f"{month}: interval "
            f"[{row['avg_shock_pct_ci95_low']}, {row['avg_shock_pct_ci95_high']}] "
            f"does not contain its own mean {row['avg_shock_pct']}"
        )


def test_the_published_interval_is_reproducible_from_the_same_run():
    """A re-render is not a new measurement. If the bound moved every time the
    dashboard was regenerated from one unchanged run artefact, a reader comparing
    two publishes would read RNG as a change in the world."""
    data = _series(**{"2022-01": [0.1, 0.4, 0.9, 1.7, 0.3, 0.2]})
    first = _row(extract_monthly_ops(data), "2022-01")
    second = _row(extract_monthly_ops(data), "2022-01")
    assert first["avg_shock_pct_ci95_low"] == second["avg_shock_pct_ci95_low"]
    assert first["avg_shock_pct_ci95_high"] == second["avg_shock_pct_ci95_high"]


def test_the_interval_does_not_depend_on_global_random_state():
    """The reproducibility control above passes trivially inside one process. This
    is the same property under the mutation that actually threatens it: a bootstrap
    drawing from the `random` module's global state reproduces only until something
    else in the publish run draws a number first, and then the published bound moves
    for a reason found nowhere in the data.

    Seeding the shared global and drawing between calls must change nothing.
    """
    import random as _random

    _random.seed(1)
    first = _bootstrap_mean_interval([0.1, 0.4, 0.9, 1.7, 0.2], "2022-01")
    _random.seed(999)
    [_random.random() for _ in range(17)]
    second = _bootstrap_mean_interval([0.1, 0.4, 0.9, 1.7, 0.2], "2022-01")
    assert first == second


# --------------------------------------------------------------------------
# The median is published BESIDE the mean, not instead of it
# --------------------------------------------------------------------------

def test_the_median_is_published_beside_the_mean_and_is_not_a_copy_of_it():
    """On a skewed month the two must differ. A generator that emitted the mean
    twice under two names would satisfy every 'field is present' check and tell the
    reader nothing -- and it would do so most convincingly on exactly the skewed
    months the field exists for."""
    r = extract_monthly_ops(_series(**{"2022-01": [0.10, 0.12, 0.15, 0.18, 9.00]}))
    row = _row(r, "2022-01")
    assert row["median_shock_pct"] < row["avg_shock_pct"]
    assert row["median_shock_pct"] == pytest.approx(15.0, abs=0.1)


def test_the_mean_is_still_published_so_the_robust_statistic_cannot_be_the_only_one():
    """Publishing only the median would move the headline from 108.1% to 49.7% and
    would be choosing the flattering statistic. The skew is a real property of the
    book and the reader is owed both."""
    r = extract_monthly_ops(_series(**{"2022-01": [0.10, 0.12, 0.15, 0.18, 9.00]}))
    row = _row(r, "2022-01")
    assert row["avg_shock_pct"] > row["median_shock_pct"]
    assert row["avg_shock_pct"] == pytest.approx(
        statistics.mean([0.10, 0.12, 0.15, 0.18, 9.00]) * 100, abs=0.1)


# --------------------------------------------------------------------------
# Each average names the population it is a mean over
# --------------------------------------------------------------------------

def test_each_average_shock_field_names_its_own_population_and_points_at_the_other():
    """The defect: two published fields both called the average bill shock, means
    over different populations, differing by 3.6x in 2016, neither naming its own on
    any surface. Naming one is half a repair -- a reader who found only one label
    would take the unlabelled field for the general case."""
    pop = extract_monthly_ops(_series(**{"2022-01": [0.5]}))["avg_shock_pct_population"]
    assert "avg_bill_shock_pct" in pop, (
        "the flagged-only series must point the reader at the all-bills mean, "
        "or the two numbers still have nothing to reconcile them"
    )
    assert "NOT all bills" in pop


def test_the_bound_note_says_which_way_a_null_interval_reads():
    """Fail closed, and say so on the surface. A null interval that the page does
    not explain reads as a missing value rather than as a refusal."""
    note = extract_monthly_ops(_series(**{"2022-01": [0.5]}))["avg_shock_pct_bound_note"]
    assert "median_shock_pct" in note
    assert "null interval" in note


# --------------------------------------------------------------------------
# The bound moved nothing it was not supposed to move
# --------------------------------------------------------------------------

def test_adding_the_bound_did_not_move_the_figure_it_bounds():
    """The whole commit's claim in one control: this is additive. The mean and the
    max are computed from the sample alone and no bound may reach back into them."""
    pcts = [0.10, 0.12, 0.15, 0.18, 9.00]
    row = _row(extract_monthly_ops(_series(**{"2022-01": pcts})), "2022-01")
    assert row["avg_shock_pct"] == round(statistics.mean(pcts) * 100, 1)
    assert row["max_shock_pct"] == round(max(pcts) * 100, 1)
    assert row["shock_count"] == len(pcts)
