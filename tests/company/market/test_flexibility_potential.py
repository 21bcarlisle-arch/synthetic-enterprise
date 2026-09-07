"""Tests for Phase AA: Demand Flexibility Potential Assessor."""
from __future__ import annotations

import pytest

from company.market import capacity_market_published_record as rec
from company.market.flexibility_potential import (
    FlexibilityAssetType,
    FlexibilityEstimate,
    FlexibilityPotentialBook,
)


class TestFlexibilityEstimate:
    def _ev_estimate(self) -> FlexibilityEstimate:
        book = FlexibilityPotentialBook()
        return book.assess("C1", has_ev=True)

    def test_ev_flex_kw(self):
        e = self._ev_estimate()
        assert e.flex_kw == pytest.approx(7.4, abs=0.1)

    def test_ev_asset_type(self):
        e = self._ev_estimate()
        assert e.asset_type == FlexibilityAssetType.EV

    def test_ev_is_dfs_eligible(self):
        assert self._ev_estimate().is_dfs_eligible is True

    def test_ashp_only_eligible(self):
        book = FlexibilityPotentialBook()
        e = book.assess("C2", has_ashp=True)
        assert e.is_dfs_eligible is True
        assert e.asset_type == FlexibilityAssetType.ASHP

    def test_ev_and_battery_combined_kw(self):
        book = FlexibilityPotentialBook()
        e = book.assess("C3", has_ev=True, has_battery=True)
        assert e.flex_kw > 7.4  # must exceed EV alone
        assert e.asset_type == FlexibilityAssetType.EV_AND_BATTERY

    def test_battery_only_asset_type(self):
        book = FlexibilityPotentialBook()
        e = book.assess("C4", has_battery=True)
        assert e.asset_type == FlexibilityAssetType.BATTERY

    def test_dfs_revenue_positive(self):
        e = self._ev_estimate()
        assert e.dfs_revenue_gbp_pa > 0

    def test_capacity_market_revenue_is_refused_with_a_reason(self):
        """Asserted `> 0` until 2026-09-07, which any price whatsoever would have satisfied.

        The price it was satisfied by was GBP75/kW -- the capped T-1 result for delivery year
        2022/23 -- times the household's RATED asset power, GBP930/year for an agreement no
        household can hold. The refusal carries its reason so the reason can be argued with.
        """
        e = self._ev_estimate()
        assert e.capacity_market_revenue_gbp_pa is None
        assert "cannot hold a Capacity Market agreement" in e.capacity_market_refusal_reason
        # KEYED TO THE PROPERTY, NOT THE WORDING. This leg read `"1,000 kW minimum CMU" in ...`
        # and went red on 2026-09-07 when the refusal was rewritten to carry the register's
        # evidence -- i.e. when the claim got narrower and better sourced. Second home of the
        # identical pinned assertion; the other was in test_capacity_market_published_record.
        assert f"{rec.MINIMUM_CMU_CAPACITY_KW:,.0f} kW" in e.capacity_market_refusal_reason

    def test_total_annual_revenue_is_sum(self):
        e = self._ev_estimate()
        cm = e.capacity_market_revenue_gbp_pa or 0.0
        assert abs(e.total_annual_revenue_gbp - (e.dfs_revenue_gbp_pa + cm)) < 0.01

    def test_ev_battery_higher_revenue_than_ev_alone(self):
        book = FlexibilityPotentialBook()
        ev_only = book.assess("C1", has_ev=True)
        ev_battery = book.assess("C2", has_ev=True, has_battery=True)
        assert ev_battery.total_annual_revenue_gbp > ev_only.total_annual_revenue_gbp

    def test_flex_mwh_per_event(self):
        e = self._ev_estimate()
        assert abs(e.flex_mwh_per_event - e.flex_kwh_per_event / 1000.0) < 0.0001

    def test_estimate_is_frozen(self):
        e = self._ev_estimate()
        with pytest.raises((AttributeError, TypeError)):
            e.flex_kw = 99.0


class TestFlexibilityPotentialBook:
    def test_no_assets_returns_none(self):
        book = FlexibilityPotentialBook()
        result = book.assess("C1")
        assert result is None

    def test_assess_stores_estimate(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        assert len(book.all_estimates) == 1

    def test_no_asset_not_stored(self):
        book = FlexibilityPotentialBook()
        book.assess("C1")
        assert len(book.all_estimates) == 0

    def test_dfs_eligible_filters_below_1kw(self):
        """All assets produce >= 1 kW, so all should be DFS eligible."""
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        book.assess("C2", has_battery=True)
        assert len(book.dfs_eligible()) == 2

    def test_total_portfolio_flex_kw(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        book.assess("C2", has_battery=True)
        assert book.total_portfolio_flex_kw > 0

    def test_total_portfolio_revenue(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        book.assess("C2", has_battery=True)
        assert book.total_portfolio_revenue_gbp_pa > 0

    def test_by_asset_type(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        book.assess("C2", has_ev=True)
        book.assess("C3", has_battery=True)
        ev_customers = book.by_asset_type(FlexibilityAssetType.EV)
        assert len(ev_customers) == 2

    def test_top_by_flex_kw(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        book.assess("C2", has_ev=True, has_battery=True, has_ashp=True)
        book.assess("C3", has_ashp=True)
        top = book.top_by_flex_kw(2)
        assert len(top) == 2
        assert top[0].flex_kw >= top[1].flex_kw

    def test_flexibility_summary_keys(self):
        book = FlexibilityPotentialBook()
        book.assess("C1", has_ev=True)
        s = book.flexibility_summary()
        for key in ["customers_assessed", "dfs_eligible_count", "total_flex_kw",
                    "total_annual_revenue_gbp", "ev_customers", "battery_customers"]:
            assert key in s

    def test_flexibility_summary_empty(self):
        book = FlexibilityPotentialBook()
        s = book.flexibility_summary()
        assert s["customers_assessed"] == 0
        assert s["total_flex_kw"] == 0.0
        assert s["total_annual_revenue_gbp"] == 0.0

    def test_portfolio_flex_additive(self):
        book = FlexibilityPotentialBook()
        e1 = book.assess("C1", has_ev=True)
        e2 = book.assess("C2", has_battery=True)
        assert abs(book.total_portfolio_flex_kw - (e1.flex_kw + e2.flex_kw)) < 0.01


# --- The de-rating caller pass, 2026-09-07 (a51). The deliberate answer here was NO FACTOR, EVER.


def test_a_published_derating_factor_never_makes_the_domestic_leg_return_a_number():
    """The defect: 'derating_factor() serves real numbers now, so wire the CM leg back up'.

    The domestic leg refuses because nobody publishes an aggregator's pass-through, and a factor
    is a multiplier -- it can make a number smaller and cannot make one exist. This control is
    over the WHOLE run window rather than a sampled year, because the tempting edit is "wire it up
    for the years we have a factor for", which a single-year leg would not catch.

    REACHABILITY FIRST: the factor must exist for every year asserted, or "still None" is measuring
    an empty register rather than a refusal that holds.
    """
    from company.market import capacity_market_published_record as rec

    years = [y for y in range(rec.FIRST_DELIVERY_YEAR, rec.RUN_WINDOW_LAST_DELIVERY_YEAR + 1)]
    with_factor = [y for y in years
                   if rec.derating_factor(rec.DSR_TECHNOLOGY_CLASS, y, "T-4") is not None]
    assert len(with_factor) >= 8, (
        f"only {len(with_factor)} run-window years carry a published DSR factor; this control "
        "would be asserting a refusal against an empty register")

    book = FlexibilityPotentialBook()
    for flex_kw in (3.0, 7.4, 12.4, 15.4):
        assert rec.household_revenue_gbp_pa(flex_kw) is None
    estimate = book.assess(account_id="C-DERATE", has_ev=True, has_ashp=True, has_battery=True)
    assert estimate.capacity_market_revenue_gbp_pa is None
    assert estimate.capacity_market_refusal_reason, "a refusal must carry its reason to the surface"
    # The CM leg contributes nothing to the total -- the structural zero, not a small number.
    assert estimate.total_annual_revenue_gbp == pytest.approx(estimate.dfs_revenue_gbp_pa)


def test_the_refusal_reason_reaching_this_module_is_the_register_backed_one():
    """The defect: the estimate's printed reason drifting from the record's own refusal.

    The row carries the reason to whatever surface prints it, so the two must be the same string
    and not two paraphrases that can disagree -- which is how this book got three homes for one
    clearing price in the first place.
    """
    from company.market import capacity_market_published_record as rec

    book = FlexibilityPotentialBook()
    estimate = book.assess(account_id="C-REASON", has_ev=True)
    assert estimate.capacity_market_refusal_reason == rec.DOMESTIC_PARTICIPATION_REFUSAL
    assert "in its own right" in estimate.capacity_market_refusal_reason, (
        "the surface must print the NARROWED claim; the register refutes the unqualified one")
