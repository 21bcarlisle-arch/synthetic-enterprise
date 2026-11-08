"""Tests for Phase U: EV Customer Cross-Subsidy Register."""
import pytest
from company.pricing.ev_cross_subsidy import CrossSubsidyRecord, CrossSubsidyRegister
from company.pricing.tou_tariff_assessor import WholesaleBandRates

FLAT = 28.5
NORMAL = WholesaleBandRates.normal()
CRISIS = WholesaleBandRates.crisis()


def _reg():
    return CrossSubsidyRegister()


def test_cross_subsidy_equals_flat_minus_tou_margin():
    r = _reg()
    rec = r.record("EV1", 2023, 3000.0, 2, FLAT, NORMAL)
    assert rec.cross_subsidy_gbp == pytest.approx(rec.flat_margin_gbp - rec.tou_margin_gbp)
    assert rec.cross_subsidy_gbp == pytest.approx(557.1)


def test_cross_subsidy_positive_for_ev_customer():
    r = _reg()
    rec = r.record("EV1", 2023, 3000.0, 1, FLAT, NORMAL)
    assert rec.cross_subsidy_gbp > 0
    assert rec.is_at_risk is True


def test_frozen_dataclass_immutable():
    r = _reg()
    rec = r.record("EV1", 2023, 3000.0, 1, FLAT, NORMAL)
    with pytest.raises(Exception):
        rec.flat_margin_gbp = 999.0


def test_top_n_returns_descending_order():
    r = _reg()
    r.record("EV_HIGH", 2023, 8000.0, 3, FLAT, NORMAL)
    r.record("EV_MED", 2023, 3000.0, 1, FLAT, NORMAL)
    r.record("EV_LOW", 2023, 1000.0, 1, FLAT, NORMAL)
    top = r.top_n_by_cross_subsidy(2, 2023)
    assert top[0].cross_subsidy_gbp >= top[1].cross_subsidy_gbp
    assert top[0].account_id == "EV_HIGH"


def test_total_cross_subsidy_gbp_sums_all():
    r = _reg()
    r1 = r.record("EV1", 2023, 3000.0, 1, FLAT, NORMAL)
    r2 = r.record("EV2", 2023, 3000.0, 1, FLAT, NORMAL)
    assert r.total_cross_subsidy_gbp(2023) == pytest.approx(r1.cross_subsidy_gbp + r2.cross_subsidy_gbp)


def test_average_cross_subsidy_gbp():
    r = _reg()
    r.record("EV1", 2023, 3000.0, 1, FLAT, NORMAL)
    r.record("EV2", 2023, 5000.0, 1, FLAT, NORMAL)
    total = r.total_cross_subsidy_gbp(2023)
    assert r.average_cross_subsidy_gbp(2023) == pytest.approx(total / 2)


def test_high_consumption_ev_has_higher_cross_subsidy():
    r = _reg()
    low = r.record("EV_LOW", 2023, 1000.0, 1, FLAT, NORMAL)
    high = r.record("EV_HIGH", 2023, 8000.0, 1, FLAT, NORMAL)
    assert high.cross_subsidy_gbp > low.cross_subsidy_gbp


def test_crisis_year_cross_subsidy_still_present():
    r = _reg()
    crisis_rate = 80.0
    rec = r.record("EV1", 2022, 3000.0, 1, crisis_rate, CRISIS)
    assert rec.cross_subsidy_gbp > 0


def test_year_filter():
    r = _reg()
    r.record("EV1", 2022, 3000.0, 1, FLAT, NORMAL)
    r.record("EV1", 2023, 3000.0, 2, FLAT, NORMAL)
    assert len(r._for_year(2022)) == 1
    assert len(r._for_year(2023)) == 1
    assert len(r._for_year(None)) == 2


def test_at_risk_if_tou_launched_threshold():
    r = _reg()
    r.record("EV_BIG", 2023, 8000.0, 1, FLAT, NORMAL)
    r.record("EV_SMALL", 2023, 500.0, 1, FLAT, NORMAL)
    big_sub = r.records_for("EV_BIG")[0].cross_subsidy_gbp
    at_risk = r.at_risk_if_tou_launched(threshold_gbp=big_sub - 1.0, year=2023)
    assert len(at_risk) == 1
    assert at_risk[0].account_id == "EV_BIG"


def test_empty_register_summary():
    r = _reg()
    s = r.portfolio_summary(2023)
    assert s == {"ev_accounts": 0}


def test_portfolio_summary_keys():
    r = _reg()
    r.record("EV1", 2023, 3000.0, 2, FLAT, NORMAL)
    r.record("EV2", 2023, 5000.0, 3, FLAT, NORMAL)
    s = r.portfolio_summary(2023)
    for k in ["ev_accounts", "total_cross_subsidy_gbp", "average_cross_subsidy_gbp",
               "at_risk_count", "top_account_id"]:
        assert k in s, f"missing key: {k}"
    assert s["ev_accounts"] == 2
    assert s["top_account_id"] == "EV2"


def test_cross_subsidy_proportional_to_consumption():
    r = _reg()
    r1 = r.record("EV1", 2023, 2000.0, 1, FLAT, NORMAL)
    r2 = r.record("EV2", 2023, 4000.0, 1, FLAT, NORMAL)
    assert r2.cross_subsidy_gbp == pytest.approx(r1.cross_subsidy_gbp * 2)


def test_years_with_ev_stored_correctly():
    r = _reg()
    rec = r.record("EV1", 2023, 3000.0, 5, FLAT, NORMAL)
    assert rec.years_with_ev == 5


def test_records_for_account():
    r = _reg()
    r.record("EV1", 2022, 3000.0, 1, FLAT, NORMAL)
    r.record("EV1", 2023, 3500.0, 2, FLAT, NORMAL)
    r.record("EV2", 2023, 2000.0, 1, FLAT, NORMAL)
    assert len(r.records_for("EV1")) == 2
    assert len(r.records_for("EV2")) == 1


def test_top_n_no_records_returns_empty():
    r = _reg()
    r.record("EV1", 2022, 3000.0, 1, FLAT, NORMAL)
    top = r.top_n_by_cross_subsidy(5, year=2023)
    assert top == []
