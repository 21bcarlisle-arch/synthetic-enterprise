"""Tests for Phase T: ToU Tariff Profitability Assessor."""
import pytest
from company.pricing.tou_tariff_assessor import (
    DemandShapeClass,
    ToUProfitabilityComparison,
    ToURateStructure,
    ToUTariffAssessorBook,
    WholesaleBandRates,
    DEFAULT_FLAT_RATE_P_PER_KWH,
)

FLAT = DEFAULT_FLAT_RATE_P_PER_KWH  # 28.5p
NORMAL = WholesaleBandRates.normal()
CRISIS = WholesaleBandRates.crisis()
TOU = ToURateStructure.default()


def _book():
    return ToUTariffAssessorBook()


# --- Wholesale cost economics ---

def test_ev_flat_margin_exceeds_standard_flat_margin():
    b = _book()
    ev = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    std = b.assess("S1", 2023, 3000.0, DemandShapeClass.STANDARD_FLAT, FLAT, NORMAL)
    assert ev.flat_margin_gbp > std.flat_margin_gbp
    assert ev.wholesale_cost_gbp < std.wholesale_cost_gbp


def test_ev_tou_margin_less_than_flat_margin():
    b = _book()
    c = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert c.tou_margin_gbp < c.flat_margin_gbp


def test_ev_is_tou_not_beneficial_for_supplier():
    b = _book()
    c = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert c.is_tou_beneficial_for_supplier is False
    assert c.supplier_preferred_tariff == "flat"


def test_ev_customer_saves_on_tou():
    b = _book()
    c = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert c.customer_saving_gbp > 0
    assert c.customer_saving_gbp == round(c.flat_revenue_gbp - c.tou_revenue_gbp, 2)


def test_ev_known_values():
    b = _book()
    c = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert c.flat_revenue_gbp == pytest.approx(855.0)
    assert c.wholesale_cost_gbp == pytest.approx(108.48)
    assert c.flat_margin_gbp == pytest.approx(746.52)
    assert c.tou_revenue_gbp == pytest.approx(297.9)
    assert c.tou_margin_gbp == pytest.approx(189.42)
    assert c.customer_saving_gbp == pytest.approx(557.1)


# --- Peak-heavy customer ---

def test_peak_heavy_tou_revenue_exceeds_flat():
    b = _book()
    c = b.assess("P1", 2023, 3000.0, DemandShapeClass.PEAK_HEAVY, FLAT, NORMAL)
    assert c.tou_revenue_gbp > c.flat_revenue_gbp


def test_peak_heavy_tou_beneficial_for_supplier():
    b = _book()
    c = b.assess("P1", 2023, 3000.0, DemandShapeClass.PEAK_HEAVY, FLAT, NORMAL)
    assert c.is_tou_beneficial_for_supplier is True
    assert c.supplier_preferred_tariff == "tou"


# --- Crisis market ---

def test_crisis_wholesale_much_higher_than_normal():
    b = _book()
    ev_normal = b.assess("EV1", 2019, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    ev_crisis = b.assess("EV1", 2022, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, CRISIS)
    assert ev_crisis.wholesale_cost_gbp > ev_normal.wholesale_cost_gbp * 7


def test_crisis_overnight_band_still_cheaper_than_peak():
    assert CRISIS.overnight_gbp_mwh < CRISIS.peak_gbp_mwh
    assert NORMAL.overnight_gbp_mwh < NORMAL.peak_gbp_mwh


# --- Dataclass and properties ---

def test_frozen_dataclass_immutable():
    b = _book()
    c = b.assess("X1", 2023, 3000.0, DemandShapeClass.STANDARD_FLAT, FLAT, NORMAL)
    with pytest.raises(Exception):
        c.flat_margin_gbp = 999.0


def test_margin_delta_equals_tou_minus_flat():
    b = _book()
    c = b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert c.margin_delta_gbp == pytest.approx(c.tou_margin_gbp - c.flat_margin_gbp)


# --- WholesaleBandRates ---

def test_wholesale_band_rates_normal_vs_crisis():
    n = WholesaleBandRates.normal()
    cr = WholesaleBandRates.crisis()
    assert cr.overnight_gbp_mwh > n.overnight_gbp_mwh
    assert cr.peak_gbp_mwh > n.peak_gbp_mwh
    assert n.overnight_gbp_mwh < n.standard_gbp_mwh < n.peak_gbp_mwh


# --- WINTER_HEAVY (ASHP) ---

def test_winter_heavy_modest_margin_delta():
    b = _book()
    ashp = b.assess("HP1", 2023, 5500.0, DemandShapeClass.WINTER_HEAVY, FLAT, NORMAL)
    ev = b.assess("EV1", 2023, 5500.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    assert abs(ashp.margin_delta_gbp) < abs(ev.margin_delta_gbp)


# --- Portfolio and book methods ---

def test_portfolio_summary_keys():
    b = _book()
    b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    b.assess("S1", 2023, 3000.0, DemandShapeClass.STANDARD_FLAT, FLAT, NORMAL)
    s = b.portfolio_summary(2023)
    for key in ["accounts_assessed", "flat_preferred_count", "tou_preferred_count",
                 "overnight_heavy_count", "total_customer_saving_if_all_tou_gbp"]:
        assert key in s, f"missing key: {key}"
    assert s["accounts_assessed"] == 2
    assert s["overnight_heavy_count"] == 1


def test_flat_preferred_accounts_includes_ev():
    b = _book()
    b.assess("EV1", 2023, 3000.0, DemandShapeClass.OVERNIGHT_HEAVY, FLAT, NORMAL)
    b.assess("P1", 2023, 3000.0, DemandShapeClass.PEAK_HEAVY, FLAT, NORMAL)
    flat_pref = b.flat_preferred_accounts(2023)
    assert any(c.account_id == "EV1" for c in flat_pref)
    tou_pref = b.tou_preferred_accounts(2023)
    assert any(c.account_id == "P1" for c in tou_pref)


def test_empty_portfolio_summary():
    b = _book()
    s = b.portfolio_summary(2023)
    assert s == {"accounts_assessed": 0}
