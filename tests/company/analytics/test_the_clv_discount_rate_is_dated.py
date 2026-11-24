"""EP1: the CLV discount rate is dated, and every published CLV is also stated at 9.3% and 12.3%.

The defect this guards against is the flat 0.10 that the knowledge page
(`docs/market_research/clv_discount_rate_and_terminal_value_for_a_gb_supplier.md`) shows is wrong
from 1 Oct 2023, when Ofgem's 12.3% took effect. A flat 0.10 fails
`test_the_rate_in_force_moves_on_the_day_ofgem_moved_it` and
`test_a_book_valued_after_october_2023_publishes_twelve_point_three`.

Taken at real inputs (run 6a588a832f, H2 mean per counted account), the dated rate moves the
2023-2025 year-end beliefs by about -10% (GBP 516 -> 467, 790 -> 704, 655 -> 589) and leaves
2017-2022 unchanged.
"""

from __future__ import annotations

import dataclasses

import pytest

from company.analytics.clv_three_horizon import (
    DISCOUNT_RATE,
    REPORTED_DISCOUNT_RATES,
    discount_rate_at,
    estimate_book,
)
from company.analytics.customer_value_view import (
    build_customer_value_view,
    build_three_horizon_clv_snapshots,
)
from company.policy import decision_policy
from company.pricing.value_based_renewal import decide_margin
from saas.reporting.annual_report import _three_horizon_clv_section
from tests.company.analytics.test_clv_snapshot_series import (
    PRICE_DIFFERENTIAL_PCT,
    _customers,
    _records,
)
from tests.saas.reporting.test_three_horizon_clv_section import BOOK


@pytest.mark.parametrize(
    "day, rate",
    [
        ("2016-01-01", 0.10),
        ("2023-09-30", 0.10),
        ("2023-10-01", 0.123),
        ("2025-12-31", 0.123),
    ],
)
def test_the_rate_in_force_moves_on_the_day_ofgem_moved_it(day, rate):
    assert discount_rate_at(day) == pytest.approx(rate)


def test_the_reported_rates_are_the_published_low_and_high_ends():
    assert REPORTED_DISCOUNT_RATES == (0.093, 0.123)


def _records_to(cutoff: str) -> list[dict]:
    return [r for r in _records() if r["settlement_date"] <= cutoff]


def test_a_book_valued_after_october_2023_publishes_twelve_point_three():
    late = build_customer_value_view(
        _records_to("2024-12-31"), _customers(), PRICE_DIFFERENTIAL_PCT).three_horizon_clv
    early = build_customer_value_view(
        _records_to("2022-12-31"), _customers(), PRICE_DIFFERENTIAL_PCT).three_horizon_clv
    assert (early.discount_rate, late.discount_rate) == (DISCOUNT_RATE, 0.123)


def test_each_snapshot_year_carries_the_rate_in_force_at_its_own_edge():
    years = build_three_horizon_clv_snapshots(
        _records(), _customers(), PRICE_DIFFERENTIAL_PCT)["years"]
    assert {y: s["discount_rate"] for y, s in years.items()} == {
        "2019": 0.10, "2020": 0.10, "2021": 0.10, "2022": 0.10, "2023": 0.123, "2024": 0.123}


def test_every_published_book_states_its_aggregates_at_both_reported_rates():
    payload = estimate_book(BOOK).as_published_dict()
    bands = payload["at_reported_rates"]
    assert sorted(bands) == ["0.093", "0.123"]
    low = bands["0.093"]["portfolio"]["mean_value_gbp"]
    mid = payload["portfolio"]["mean_value_gbp"]
    high = bands["0.123"]["portfolio"]["mean_value_gbp"]
    # A profitable book is worth more at a lower rate; equal values would mean the band was
    # computed at the headline rate and only relabelled.
    assert low > mid > high > 0
    assert set(bands["0.123"]["cohorts"]) == set(payload["cohorts"])


def test_the_report_prints_both_reported_rates():
    text = _three_horizon_clv_section({"three_horizon_clv": estimate_book(BOOK).as_published_dict()})
    assert "At a 9.3% discount rate" in text and "At a 12.3% discount rate" in text


_ACCOUNT = dict(
    customer_id="EP1-RATE",
    arm="value_based",
    current_rate_gbp_per_mwh=150.0,
    base_rate_gbp_per_mwh=120.0,
    eac_kwh=3000.0,
    tenure_years=2.0,
    cost_to_serve_gbp_per_year=90.0,
    renewal_year=2024,
)


def test_the_dated_rate_reaches_decisions_only_through_the_named_switch():
    # The branch CAN be taken: the rate the decision is handed reaches what it scores.
    flat = decide_margin(**_ACCOUNT)
    dated = decide_margin(**_ACCOUNT, discount_rate=0.123)
    assert dated.expected_value_gbp != flat.expected_value_gbp
    # And the standing policy does not take it until the pre-registered books are graded.
    assert decision_policy.EP1_DATED_DISCOUNT_RATE_IN_THE_STANDING_POLICY is False
    assert decision_policy.CURRENT_POLICY.renewal_discount_rate_dated is False
    default = {f.name: f.default for f in dataclasses.fields(decision_policy.DecisionPolicy)}
    assert default["renewal_discount_rate_dated"] is False
