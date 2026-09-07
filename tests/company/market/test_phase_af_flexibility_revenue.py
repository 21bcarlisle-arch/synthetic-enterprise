"""Tests for FlexibilityRevenueBook -- Phase AF."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from company.market import dfs_published_record
from company.market.flexibility_potential import (
    _ASHP_FLEX_KW,
    _BATTERY_FLEX_KW,
    _DISPATCH_DURATION_HRS,
    _EV_FLEX_KW,
)
from company.market.flexibility_revenue_book import (
    _DFS_LAUNCH_YEAR,
    FlexibilityRevenueBook,
    FlexibilityRevenueRecord,
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


def test_ev_only_books_nothing_pre_dfs_because_the_cm_leg_is_refused():
    """Before 2022 a household earns NOTHING here, and the CM leg is why.

    This test used to be called `test_ev_only_cm_pre_dfs` and asserted
    `_EV_FLEX_KW * _CAPACITY_MARKET_GBP_PER_KW_YR`, which is the production formula spelled
    twice: a TAUTOLOGY that passed for every value of the constant, including the GBP75/kW that
    was a capped T-1 result for delivery year 2022/23 mislabelled "T-4 auction 2023". The file's
    own next test already carried that warning about the DFS leg; the CM leg beside it kept the
    shape anyway.

    It now asserts the REFUSAL, which cannot be satisfied by any price: a household holds no
    Capacity Market agreement, so the pre-DFS years book zero.
    """
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    result = book.compute_year(2021, reg, ["C1"])
    assert "C1" in result, "the customer must still be assessed, not filtered out"
    rec = book.records_for_year(2021)[0]
    assert rec.flex_kw == _EV_FLEX_KW, "the household still HAS flex — it just cannot sell it here"
    assert rec.capacity_market_revenue_gbp == 0.0
    assert rec.dfs_revenue_gbp == 0.0
    assert result["C1"] == 0.0


def test_ev_earns_dfs_from_2022():
    """From 2022 (DFS launch): EV customer earns CM + DFS revenue.

    The DFS leg is asserted against the PUBLISHED per-participant economics, not against the
    production formula. The version of this test that recomputed
    `_EV_FLEX_KW / 1000 * _DISPATCH_DURATION_HRS * _DFS_RATE_GBP_PER_MWH * _DISPATCH_EVENTS_PER_YR`
    was a tautology -- it passed for every value of the rate, which is exactly how a rate that was
    737x too low survived in two files. See tests/company/market/test_dfs_published_record.py.
    """
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    result = book.compute_year(2022, reg, ["C1"])
    rec = book.records_for_year(2022)[0]
    assert rec.dfs_revenue_gbp > 0.0

    # An EV household holds ~7.8x the flex of the published average participant, so it must earn
    # materially more than the average and nothing like the whole book.
    per_average = dfs_published_record.revenue_gbp_per_participant_winter(2022)
    assert rec.dfs_revenue_gbp > per_average
    assert rec.dfs_revenue_gbp == pytest.approx(
        per_average * (_EV_FLEX_KW / dfs_published_record.REFERENCE_PARTICIPANT_FLEX_KW), rel=0.01)
    assert rec.total_revenue_gbp == round(rec.capacity_market_revenue_gbp + rec.dfs_revenue_gbp, 2)


def test_battery_and_ev_additive_flex():
    """EV+battery: combined flex_kw is additive."""
    book = FlexibilityRevenueBook()
    reg = _make_register({"C2": {"ev": True, "ashp": False, "battery": True}})
    result = book.compute_year(2024, reg, ["C2"])
    rec = book.records_for_year(2024)[0]
    expected_flex_kw = _EV_FLEX_KW + _BATTERY_FLEX_KW
    assert rec.flex_kw == pytest.approx(expected_flex_kw, abs=0.01)


def test_ashp_only_books_no_cm_revenue():
    """Same refusal for the smallest flexible asset, which is the harder direction.

    An ASHP household is 3.0 kW: it takes 334 of them to reach the 1 MW minimum CMU, so if the
    threshold argument holds anywhere it holds here. Asserted separately from the EV case because
    a refusal keyed to asset SIZE rather than to the agreement would pass one and fail the other.
    """
    book = FlexibilityRevenueBook()
    reg = _make_register({"C3": {"ev": False, "ashp": True, "battery": False}})
    book.compute_year(2019, reg, ["C3"])
    rec = book.records_for_year(2019)[0]
    assert rec.flex_kw == _ASHP_FLEX_KW
    assert rec.capacity_market_revenue_gbp == 0.0
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
    # 2020 and 2021 book nothing (CM refused, pre-DFS); 2023's winter is the unestablished one,
    # so this total rests on 2024 being absent rather than on any year paying. Asserted as a
    # record count plus a non-negative total: `> 0.0` was true only because of the refused leg.
    assert book.total_revenue_all_years() >= 0.0
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


def test_domestic_cm_revenue_is_zero_from_the_start_of_the_record():
    """Inverted on 2026-09-07, and the inversion is the finding.

    This asserted "CM revenue earned from simulation start (2016)". A GB household has never been
    able to hold a Capacity Market agreement -- the minimum CMU is 1 MW -- so the book was
    crediting every flexible household with availability payments in every year of the run, from
    a constant that was a capped T-1 price for a single delivery year. The correct claim about
    2016 is the opposite of the one that was asserted.
    """
    book = FlexibilityRevenueBook()
    reg = _make_register({"C1": {"ev": True, "ashp": False, "battery": False}})
    book.compute_year(2016, reg, ["C1"])
    assert book.total_cm_revenue() == 0.0
    assert len(book.records_for_year(2016)) == 1, (
        "the household must still be assessed — a zero that comes from nobody being measured "
        "would pass this test while meaning something entirely different"
    )


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
