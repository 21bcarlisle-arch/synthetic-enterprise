"""Tests for FlexibilityRevenueBook -- Phase AF."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock

from company.market.flexibility_revenue_book import (
    FlexibilityRevenueBook,
    FlexibilityRevenueRecord,
    _DFS_LAUNCH_YEAR,
)
from company.market.flexibility_potential import (
    _EV_FLEX_KW,
    _BATTERY_FLEX_KW,
    _ASHP_FLEX_KW,
    _CAPACITY_MARKET_GBP_PER_KW_YR,
    _DFS_RATE_GBP_PER_MWH,
    _DISPATCH_EVENTS_PER_YR,
    _DISPATCH_DURATION_HRS,
)


def _make_register(assets_by_cid: dict) -> MagicMock:
    """Build a mock HouseholdDemandRegister."""
    reg = MagicMock()
    def dynamic_assets(cid, date_str):
        return assets_by_cid.get(cid, {})
    reg.dynamic_assets.side_effect = dynamic_assets
    return reg


def test_no_assets_returns_empty():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {}, "C2": {}})
    result = book.compute_year(2020, reg, ["C1", "C2"])
    assert result == {}
    assert book.total_revenue_for_year(2020) == 0.0


def test_ev_only_cm_pre_dfs():
    """Before 2022: EV customer earns CM revenue only."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    result = book.compute_year(2021, reg, ["C1"])
    assert "C1" in result
    expected_cm = round(_EV_FLEX_KW * _CAPACITY_MARKET_GBP_PER_KW_YR, 2)
    assert result["C1"] == expected_cm
    rec = book.records_for_year(2021)[0]
    assert rec.dfs_revenue_gbp == 0.0
    assert rec.capacity_market_revenue_gbp == expected_cm


def test_ev_earns_dfs_from_2022():
    """From 2022 (DFS launch): EV customer earns CM + DFS revenue."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    result = book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.dfs_revenue_gbp > 0.0
    expected_dfs = round(
        _EV_FLEX_KW * _DFS_RATE_GBP_PER_MWH * _DISPATCH_EVENTS_PER_YR * _DISPATCH_DURATION_HRS, 2
    )
    assert rec.dfs_revenue_gbp == expected_dfs
    assert rec.total_revenue_gbp == round(rec.capacity_market_revenue_gbp + rec.dfs_revenue_gbp, 2)


def test_battery_and_ev_additive_flex():
    """EV+battery: combined flex_kw is additive."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C2": {"ev": True, "ashp": False, "battery": True}})
    result = book.compute_year(2024, reg, ["C2"])
    rec = book.records_for_year(2024)[0]
    expected_flex_kw = _EV_FLEX_KW + _BATTERY_FLEX_KW
    assert rec.flex_kw == pytest.approx(expected_flex_kw, abs=0.01)


def test_ashp_only_cm_revenue():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C3": {"ev": False, "ashp": True, "battery": False}})
    result = book.compute_year(2019, reg, ["C3"])
    rec = book.records_for_year(2019)[0]
    expected_cm = round(_ASHP_FLEX_KW * _CAPACITY_MARKET_GBP_PER_KW_YR, 2)
    assert rec.capacity_market_revenue_gbp == expected_cm
    assert rec.dfs_revenue_gbp == 0.0


def test_multi_customer_mixed():
    """Some customers with assets, some without."""
    book = FlexibilityRevenueBook()
    reg = _make_register({
        "C1": {"ev": True, "ashp": False, "battery": False},
        "C2": {},
        "C3": {"ev": False, "ashp": True, "battery": True},
    })
    result = book.compute_year(2023, reg, ["C1", "C2", "C3"])
    assert "C1" in result
    assert "C2" not in result
    assert "C3" in result
    assert len(book.records_for_year(2023)) == 2


def test_total_revenue_for_year():
    book = FlexibilityRevenueBook()
    reg = _make_register({
        "C1": {"ev": True, "ashp": False, "battery": False},
        "C2": {"ev": False, "ashp": True, "battery": False},
    })
    result = book.compute_year(2024, reg, ["C1", "C2"])
    total = book.total_revenue_for_year(2024)
    assert total == pytest.approx(sum(result.values()), abs=0.01)


def test_multi_year_accumulates():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2020, reg, ["C1"])
    book.compute_year(2021, reg, ["C1"])
    book.compute_year(2023, reg, ["C1"])
    assert book.total_revenue_all_years() > 0.0
    assert len(book.records_for_year(2020)) == 1
    assert len(book.records_for_year(2023)) == 1


def test_dfs_revenue_zero_before_2022():
    """DFS was not launched before 2022."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    for year in range(2016, 2022):
        book.compute_year(year, reg, ["C1"])
    total_dfs = book.total_dfs_revenue()
    assert total_dfs == 0.0


def test_cm_revenue_non_zero_from_start():
    """CM revenue earned from simulation start (2016)."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2016, reg, ["C1"])
    assert book.total_cm_revenue() > 0.0


def test_flexibility_summary_structure():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    book.compute_year(2023, reg, ["C1"])
    summary = book.flexibility_summary()
    assert "total_flexibility_revenue_gbp" in summary
    assert "total_cm_revenue_gbp" in summary
    assert "total_dfs_revenue_gbp" in summary
    assert "years_with_revenue" in summary
    assert "peak_year_revenue_gbp" in summary
    assert "per_year" in summary
    assert summary["enrolled_customer_years"] == 2


def test_flexibility_summary_empty():
    book = FlexibilityRevenueBook()
    reg = _make_register({})
    book.compute_year(2020, reg, [])
    summary = book.flexibility_summary()
    assert summary["total_flexibility_revenue_gbp"] == 0.0
    assert summary["peak_year_revenue_gbp"] == 0.0
    assert summary["years_with_revenue"] == []


def test_record_is_frozen():
    rec = FlexibilityRevenueRecord(
        customer_id="C1",
        year=2023,
        has_ev=True,
        has_ashp=False,
        has_battery=False,
        flex_kw=7.4,
        capacity_market_revenue_gbp=555.0,
        dfs_revenue_gbp=666.0,
        total_revenue_gbp=1221.0,
    )
    with pytest.raises(Exception):
        rec.customer_id = "C2"


def test_per_year_detail_in_summary():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2023, reg, ["C1"])
    summary = book.flexibility_summary()
    assert "2023" in summary["per_year"] or 2023 in summary["per_year"]
    yr_data = summary["per_year"].get(2023) or summary["per_year"].get("2023")
    assert yr_data is not None
    assert "total_gbp" in yr_data
    assert "cm_gbp" in yr_data
    assert "dfs_gbp" in yr_data
    assert yr_data["enrolled_customers"] == 1


def test_dfs_launch_year_constant():
    assert _DFS_LAUNCH_YEAR == 2022


# --- Phase MR depth tests ---

def test_record_customer_id_stored():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.customer_id == "C1"


def test_record_year_stored():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2023, reg, ["C1"])
    rec = book.records_for_year(2023)[0]
    assert rec.year == 2023


def test_record_has_ev_stored():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.has_ev is True


def test_record_has_ashp_stored():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": False, "ashp": True, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.has_ashp is True


def test_record_has_battery_stored():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": False, "ashp": False, "battery": True}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.has_battery is True


def test_record_flex_kw_positive():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.flex_kw > 0.0


def test_record_total_equals_cm_plus_dfs():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.total_revenue_gbp == pytest.approx(
        rec.capacity_market_revenue_gbp + rec.dfs_revenue_gbp, abs=0.01
    )


def test_total_cm_revenue_accumulates():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2021, reg, ["C1"])
    book.compute_year(2022, reg, ["C1"])
    rec2021 = book.records_for_year(2021)[0]
    rec2022 = book.records_for_year(2022)[0]
    assert book.total_cm_revenue() == pytest.approx(
        rec2021.capacity_market_revenue_gbp + rec2022.capacity_market_revenue_gbp, abs=0.01
    )


def test_total_dfs_revenue_sums():
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2022, reg, ["C1"])
    book.compute_year(2023, reg, ["C1"])
    rec2022 = book.records_for_year(2022)[0]
    rec2023 = book.records_for_year(2023)[0]
    assert book.total_dfs_revenue() == pytest.approx(
        rec2022.dfs_revenue_gbp + rec2023.dfs_revenue_gbp, abs=0.01
    )


def test_records_for_year_empty_when_no_records():
    book = FlexibilityRevenueBook()
    assert book.records_for_year(2099) == []
