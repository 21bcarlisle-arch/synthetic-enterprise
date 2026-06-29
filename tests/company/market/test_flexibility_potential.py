"""Tests for Phase AA: Demand Flexibility Potential Assessor."""
from __future__ import annotations

import pytest

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

    def test_capacity_market_revenue_positive(self):
        e = self._ev_estimate()
        assert e.capacity_market_revenue_gbp_pa > 0

    def test_total_annual_revenue_is_sum(self):
        e = self._ev_estimate()
        assert abs(e.total_annual_revenue_gbp - (e.dfs_revenue_gbp_pa + e.capacity_market_revenue_gbp_pa)) < 0.01

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
