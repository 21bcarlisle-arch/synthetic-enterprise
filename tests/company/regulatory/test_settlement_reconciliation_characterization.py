"""CHARACTERIZATION: freezes current behaviour, including behaviour that may be
defective. Characterized, not endorsed.

Target: company/regulatory/settlement_reconciliation.py — the Elexon BSC
R1/R2/R3/RF reconciliation cash-flow exposure model. This is what tells the
board how much already-billed revenue is still open to adjustment, and what the
worst-case adverse settlement swing is. The RAG rating it produces is a control.

All inputs are fixed literals; the module reads no clock (the "year end" is
structural, not `today`), so there is no time-dependent path to work around.
"""
from __future__ import annotations

import pytest

from company.regulatory.settlement_reconciliation import (
    _HH_RECON_VARIANCE,
    _NON_HH_RECON_VARIANCE,
    ReconciliationExposure,
    _blended_variance,
    _outstanding_months_at_year_end,
    _rag,
    build_reconciliation_series,
    largest_exposure_year,
)


def accounts(**years):
    """management_accounts shaped {"by_year": {"2022": {"revenue_gbp": ...}}}."""
    return {"by_year": {y: {"revenue_gbp": v} for y, v in years.items()}}


# ---------------------------------------------------------------------------
# The variance blend and the outstanding-months constant
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hh_fraction,expected",
    [(0.0, 0.040), (1.0, 0.005), (0.5, 0.0225), (0.90, 0.0085)],
)
def test_blended_variance_is_a_straight_linear_interpolation(hh_fraction, expected):
    assert _blended_variance(hh_fraction) == pytest.approx(expected)


def test_blended_variance_does_not_bound_its_input():
    # DELIBERATELY CORRUPT INPUT: hh_fraction is a fraction, but nothing checks
    # it. SURPRISE: hh_fraction = 2.0 produces a NEGATIVE variance, which flows
    # straight through to a negative max_adverse_gbp and a GREEN rating (see
    # test_a_corrupt_hh_fraction_produces_a_negative_exposure_rated_green).
    assert _blended_variance(2.0) == pytest.approx(-0.030)
    assert _blended_variance(-1.0) == pytest.approx(0.075)


def test_outstanding_months_is_a_fixed_constant_of_the_run_share_table():
    # 0.60x2 + 0.25x2 + 0.12x23 + 0.03x0 = 4.46 months.
    assert _outstanding_months_at_year_end() == pytest.approx(4.46)


def test_the_pool_fraction_comment_understates_the_value_it_documents():
    # SURPRISE: `build_reconciliation_series` computes pool_fraction as
    # outstanding_months / 12 and its inline comment says "e.g. 2 months / 12 =
    # 0.17". The actual constant is 4.46 months → 0.372, more than double the
    # documented example. The comment appears to predate the R3 tail weighting.
    assert _outstanding_months_at_year_end() / 12.0 == pytest.approx(0.3717, abs=1e-4)


# ---------------------------------------------------------------------------
# _rag — the RAG control
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "adverse,monthly,rag",
    [
        (4.0, 100.0, "GREEN"),    # 4%
        (5.0, 100.0, "AMBER"),    # exactly 5% — the < is strict, so not GREEN
        (14.99, 100.0, "AMBER"),
        (15.0, 100.0, "RED"),     # exactly 15% — strict again
        (100.0, 100.0, "RED"),
    ],
)
def test_rag_bands_and_their_strict_boundaries(adverse, monthly, rag):
    assert _rag(adverse, monthly) == rag


def test_rag_fires_on_exposure_with_no_revenue_behind_it():
    # R15 MUTATION PROOF (was the frozen defect, fail-open class). A company with
    # no revenue and a £1,000,000 worst-case adverse settlement adjustment was
    # rated GREEN: the divide-by-zero guard answered "is this exposure safe?"
    # with "yes" rather than declining to answer. Zero revenue with open
    # settlement exposure is the WORST case a supplier can be in — the SoLR shape
    # exactly. Restore `return "GREEN"` under the guard and both lines go green.
    assert _rag(1_000_000.0, 0.0) == "RED"
    assert _rag(1_000_000.0, -50.0) == "RED"


def test_rag_still_rates_no_exposure_at_all_green():
    # The other half of the mutation: nothing at risk is genuinely GREEN, so the
    # fix must not turn a dormant book into a red flag.
    assert _rag(0.0, 0.0) == "GREEN"


def test_rag_does_not_read_a_negative_adverse_amount_as_safety():
    # A negative "max adverse" is nonsense input, not a gain to be reassured by.
    assert _rag(-1_000_000.0, 100.0) == "RED"


# ---------------------------------------------------------------------------
# build_reconciliation_series
# ---------------------------------------------------------------------------


def test_a_single_year_series_is_fully_determined_by_revenue_and_hh_fraction():
    series = build_reconciliation_series(accounts(**{"2023": 12_000_000.0}))
    assert len(series) == 1
    e = series[0]
    assert isinstance(e, ReconciliationExposure)
    assert e.year == 2023
    assert e.annual_revenue_gbp == 12_000_000.0
    assert e.hh_fraction == 0.90
    assert e.outstanding_pool_gbp == 4_460_000.0        # 12m x 4.46/12
    assert e.max_adverse_gbp == 37_910.0                # pool x 0.0085
    assert e.expected_adjustment_gbp == 18_955.0        # half the max band
    assert e.months_outstanding == 4.5                  # 4.46 rounded to 1dp
    assert e.rag == "GREEN"
    assert e.is_crisis_year is False


def test_max_adverse_never_reaches_amber_at_the_default_hh_fraction():
    # The exposure is a fixed 0.372 x 0.0085 = 0.316% of ANNUAL revenue, i.e.
    # 3.79% of MONTHLY revenue — a constant, whatever the revenue. SURPRISE: at
    # the default hh_fraction the RAG rating can therefore never be anything but
    # GREEN. The control has one reachable output for every real portfolio.
    for revenue in (1_000.0, 1_000_000.0, 5_000_000_000.0):
        (e,) = build_reconciliation_series(accounts(**{"2023": revenue}))
        assert e.rag == "GREEN"
        assert e.max_adverse_gbp / (revenue / 12.0) == pytest.approx(0.0379, abs=1e-4)


def test_a_small_books_published_exposure_rounds_away_to_zero_pounds():
    # SURPRISE: the published max_adverse_gbp/expected_adjustment_gbp are rounded
    # to pennies while the RAG rating is computed on the un-rounded value. A £1
    # book reports a worst-case adverse adjustment of £0.00 — indistinguishable
    # from "no open settlement exposure" — with no flag that it was rounded away.
    (e,) = build_reconciliation_series(accounts(**{"2023": 1.0}))
    assert e.max_adverse_gbp == 0.0
    assert e.expected_adjustment_gbp == 0.0
    assert e.outstanding_pool_gbp == 0.37


def test_amber_is_reachable_only_by_moving_the_hh_fraction_toward_non_hh():
    # A wholly non-HH (domestic profile-class) book: variance 4%, exposure
    # 1.487% of annual = 17.8% of monthly revenue → RED.
    (e,) = build_reconciliation_series(accounts(**{"2023": 12_000_000.0}), hh_revenue_fraction=0.0)
    assert e.rag == "RED"
    (amber,) = build_reconciliation_series(
        accounts(**{"2023": 12_000_000.0}), hh_revenue_fraction=0.70
    )
    assert amber.rag == "AMBER"


def test_a_corrupt_hh_fraction_produces_a_negative_exposure_rated_green():
    # DELIBERATELY CORRUPT INPUT: hh_revenue_fraction = 2.0 (a fraction > 1).
    # STILL CHARACTERIZED, PARTLY FIXED. The exposure still comes out NEGATIVE —
    # the fraction is not bounded, and that remains open (finding F62) — but the
    # RAG control no longer rates the nonsense GREEN, so the corruption is now
    # visible at the surface the board reads instead of being laundered into a
    # reassuring rating. Bounding the fraction itself is queued, not done here.
    (e,) = build_reconciliation_series(
        accounts(**{"2023": 12_000_000.0}), hh_revenue_fraction=2.0
    )
    assert e.max_adverse_gbp == -133_800.0
    assert e.expected_adjustment_gbp == -66_900.0
    assert e.rag == "RED"                        # was GREEN — the control fires
    assert e.hh_fraction == 2.0  # echoed back verbatim into the published record


def test_crisis_years_are_a_hardcoded_pair_that_changes_no_number():
    # SURPRISE: the module docstring promises a "crisis-year bias: during price
    # spikes, demand destruction causes actual < estimated consumption -> net
    # credit in late reconciliation". `is_crisis_year` is set for 2021/2022 and
    # then used by nothing — the pool, the adverse band and the expected
    # adjustment are all identical to a non-crisis year with the same revenue.
    # The documented asymmetry does not exist in the numbers.
    series = build_reconciliation_series(accounts(**{"2020": 12e6, "2022": 12e6}))
    calm, crisis = series
    assert (calm.is_crisis_year, crisis.is_crisis_year) == (False, True)
    assert calm.max_adverse_gbp == crisis.max_adverse_gbp
    assert calm.expected_adjustment_gbp == crisis.expected_adjustment_gbp
    assert calm.outstanding_pool_gbp == crisis.outstanding_pool_gbp


def test_years_are_ordered_by_string_sort_of_the_key():
    series = build_reconciliation_series(accounts(**{"2022": 1e6, "2019": 1e6, "2021": 1e6}))
    assert [e.year for e in series] == [2019, 2021, 2022]


def test_a_zero_or_negative_revenue_year_vanishes_from_the_series():
    # SURPRISE: `if rev <= 0: continue`. A loss-making or zero-revenue year is
    # not rated GREEN — it is not reported at all. A reader of the series cannot
    # tell a year with no settlement exposure from a year that was dropped, and
    # `len(series)` silently stops matching the number of trading years.
    series = build_reconciliation_series(accounts(**{"2021": 0.0, "2022": -5e6, "2023": 12e6}))
    assert [e.year for e in series] == [2023]


def test_a_year_with_no_revenue_key_is_dropped_the_same_way():
    # DELIBERATELY CORRUPT INPUT: the year's dict is missing revenue_gbp entirely.
    # `.get(..., 0.0)` makes malformed input indistinguishable from a zero year,
    # and it too disappears silently.
    series = build_reconciliation_series({"by_year": {"2023": {}, "2024": {"revenue_gbp": 12e6}}})
    assert [e.year for e in series] == [2024]


def test_missing_or_empty_by_year_returns_an_empty_series():
    assert build_reconciliation_series({}) == []
    assert build_reconciliation_series({"by_year": {}}) == []


def test_a_non_numeric_year_key_raises_rather_than_being_skipped():
    # The one malformed input that is NOT swallowed: int() on the key raises.
    with pytest.raises(ValueError):
        build_reconciliation_series({"by_year": {"FY23": {"revenue_gbp": 12e6}}})


def test_the_exposure_record_is_frozen_and_immutable():
    (e,) = build_reconciliation_series(accounts(**{"2023": 12e6}))
    with pytest.raises(Exception):
        e.rag = "RED"  # type: ignore[misc]


# ---------------------------------------------------------------------------
# largest_exposure_year
# ---------------------------------------------------------------------------


def test_largest_exposure_year_picks_the_biggest_adverse_band():
    series = build_reconciliation_series(accounts(**{"2021": 6e6, "2022": 24e6, "2023": 12e6}))
    assert largest_exposure_year(series).year == 2022


def test_largest_exposure_year_of_an_empty_series_is_none():
    assert largest_exposure_year([]) is None


def test_largest_exposure_year_takes_the_first_on_a_tie():
    series = build_reconciliation_series(accounts(**{"2021": 12e6, "2022": 12e6}))
    assert largest_exposure_year(series).year == 2021


def test_largest_exposure_is_a_max_not_a_max_by_absolute_value():
    # With a corrupt hh_fraction every band is negative, so "largest exposure"
    # returns the least-negative year — the one with the SMALLEST revenue.
    series = build_reconciliation_series(
        accounts(**{"2021": 24e6, "2022": 6e6}), hh_revenue_fraction=2.0
    )
    assert largest_exposure_year(series).year == 2022


def test_the_published_variance_constants_match_the_cited_source_bands():
    assert (_HH_RECON_VARIANCE, _NON_HH_RECON_VARIANCE) == (0.005, 0.040)
