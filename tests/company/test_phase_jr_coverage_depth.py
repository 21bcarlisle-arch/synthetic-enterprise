"""Phase JR: Coverage Depth Sprint XL -- 30 tests.

Modules:
  hedge_policy: boundary conditions on company_evolve_hedge_fraction
  ofgem_price_cap: specific year values and boundary coverage
  service_log: CSAT and service behavior edge cases
"""
import pytest
from company.risk.hedge_policy import (
    COMPANY_MIN_HEDGE_FLOOR,
    COMPANY_EVOLUTION_STEP,
    COMPANY_MARGIN_TOLERANCE_GBP,
    company_evolve_hedge_fraction,
)
from company.pricing.ofgem_price_cap import get_cap_unit_rate_gbp_per_mwh
from company.crm.service_log import ServiceLog, ServiceEvent


def test_evolution_step_constant():
    assert COMPANY_EVOLUTION_STEP == pytest.approx(0.1)


def test_tolerance_constant():
    assert COMPANY_MARGIN_TOLERANCE_GBP == pytest.approx(5.0)


def test_exact_positive_tolerance_boundary_holds():
    diff = COMPANY_MARGIN_TOLERANCE_GBP
    hf, reason = company_evolve_hedge_fraction(0.90, naked_net_gbp=100.0, actual_net_gbp=100.0 + diff)
    assert hf == pytest.approx(0.90)
    assert "hold" in reason


def test_exact_negative_tolerance_boundary_holds():
    diff = COMPANY_MARGIN_TOLERANCE_GBP
    hf, reason = company_evolve_hedge_fraction(0.90, naked_net_gbp=100.0 + diff, actual_net_gbp=100.0)
    assert hf == pytest.approx(0.90)
    assert "hold" in reason


def test_just_above_positive_tolerance_raises():
    diff = COMPANY_MARGIN_TOLERANCE_GBP + 0.01
    hf, reason = company_evolve_hedge_fraction(0.90, naked_net_gbp=100.0, actual_net_gbp=100.0 + diff)
    assert hf == pytest.approx(0.90 + COMPANY_EVOLUTION_STEP)
    assert "raise" in reason


def test_just_below_negative_tolerance_trims():
    diff = COMPANY_MARGIN_TOLERANCE_GBP + 0.01
    hf, reason = company_evolve_hedge_fraction(1.0, naked_net_gbp=100.0 + diff, actual_net_gbp=100.0)
    assert hf == pytest.approx(1.0 - COMPANY_EVOLUTION_STEP)
    assert "trim" in reason


def test_multiple_raises_cap_at_one():
    hf = COMPANY_MIN_HEDGE_FLOOR
    for _ in range(3):
        hf, _ = company_evolve_hedge_fraction(hf, naked_net_gbp=50.0, actual_net_gbp=200.0)
    expected = min(1.0, COMPANY_MIN_HEDGE_FLOOR + 3 * COMPANY_EVOLUTION_STEP)
    assert hf == pytest.approx(expected)
    hf_capped, _ = company_evolve_hedge_fraction(1.0, naked_net_gbp=0.0, actual_net_gbp=500.0)
    assert hf_capped == pytest.approx(1.0)


def test_multiple_trims_floor_at_min_hedge():
    hf = 0.95
    for _ in range(5):
        hf, _ = company_evolve_hedge_fraction(hf, naked_net_gbp=200.0, actual_net_gbp=0.0)
    assert hf == pytest.approx(COMPANY_MIN_HEDGE_FLOOR)


def test_reason_contains_resulting_fraction():
    hf, reason = company_evolve_hedge_fraction(0.85, naked_net_gbp=50.0, actual_net_gbp=200.0)
    new_frac = round(COMPANY_MIN_HEDGE_FLOOR + COMPANY_EVOLUTION_STEP, 2)
    assert str(new_frac) in reason


def test_starting_at_0_95_trims_to_0_85():
    hf, _ = company_evolve_hedge_fraction(0.95, naked_net_gbp=200.0, actual_net_gbp=0.0)
    assert hf == pytest.approx(0.85)


def test_electricity_cap_2019_first_year():
    cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2019)
    assert cap is not None
    assert 100.0 < cap < 250.0


def test_electricity_cap_2022_crisis_above_300():
    cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
    assert cap is not None
    assert cap > 300.0


def test_gas_cap_2022_crisis_above_90():
    cap = get_cap_unit_rate_gbp_per_mwh("gas", 2022)
    assert cap is not None
    assert cap > 90.0


def test_electricity_cap_post_crisis_normalizes():
    cap_22 = get_cap_unit_rate_gbp_per_mwh("electricity", 2022)
    cap_24 = get_cap_unit_rate_gbp_per_mwh("electricity", 2024)
    assert cap_24 < cap_22


def test_gas_cap_post_crisis_normalizes():
    cap_22 = get_cap_unit_rate_gbp_per_mwh("gas", 2022)
    cap_24 = get_cap_unit_rate_gbp_per_mwh("gas", 2024)
    assert cap_24 < cap_22


def test_electricity_cap_2018_none():
    assert get_cap_unit_rate_gbp_per_mwh("electricity", 2018) is None


def test_gas_cap_2017_none():
    assert get_cap_unit_rate_gbp_per_mwh("gas", 2017) is None


def test_fallback_year_2030_returns_float():
    cap = get_cap_unit_rate_gbp_per_mwh("electricity", 2030)
    assert cap is not None
    assert isinstance(cap, float)
    cap_gas = get_cap_unit_rate_gbp_per_mwh("gas", 2030)
    assert cap_gas is not None
    assert isinstance(cap_gas, float)


def test_electricity_cap_always_above_gas_cap():
    for year in range(2019, 2026):
        elec = get_cap_unit_rate_gbp_per_mwh("electricity", year)
        gas = get_cap_unit_rate_gbp_per_mwh("gas", year)
        assert elec is not None and gas is not None
        assert elec > gas


def test_gas_cap_2024_specific_range():
    cap = get_cap_unit_rate_gbp_per_mwh("gas", 2024)
    assert cap is not None
    assert 40.0 < cap < 80.0


def _make_log():
    return ServiceLog()


def _make_event(cid="C1", csat=None, complaint=False, vuln=False):
    return ServiceEvent(
        customer_id=cid, event_date="2026-07-01",
        channel="phone", contact_reason="general",
        outcome="resolved", complaint_flag=complaint,
        vulnerability_flag=vuln, csat_score=csat,
    )


def test_csat_score_1_is_valid():
    log = _make_log()
    log.record_contact(_make_event(csat=1))
    s = log.csat_summary()
    assert s["count"] == 1
    assert s["mean"] == 1.0


def test_csat_score_0_raises():
    log = _make_log()
    log.record_contact(_make_event())
    cid = log.latest_contact_id("C1")
    with pytest.raises(ValueError):
        log.rate_contact(cid, 0)


def test_latest_contact_id_none_on_empty_log():
    log = _make_log()
    assert log.latest_contact_id("C1") is None


def test_latest_contact_id_returns_most_recent():
    log = _make_log()
    log.record_contact(_make_event())
    id1 = log.latest_contact_id("C1")
    log.record_contact(_make_event())
    id2 = log.latest_contact_id("C1")
    assert id2 > id1


def test_rate_contact_nonexistent_id_returns_false():
    log = _make_log()
    result = log.rate_contact(99999, 4)
    assert result is False


def test_csat_mean_computed_correctly():
    log = _make_log()
    for score in [2, 4, 4, 5]:
        log.record_contact(_make_event(csat=score))
    s = log.csat_summary()
    assert s["mean"] == pytest.approx(15 / 4, rel=1e-3)


def test_csat_promoter_pct_three_of_four():
    log = _make_log()
    for score in [5, 4, 4, 3]:
        log.record_contact(_make_event(csat=score))
    s = log.csat_summary()
    assert s["promoter_pct"] == pytest.approx(75.0)


def test_csat_score_3_not_a_promoter():
    log = _make_log()
    log.record_contact(_make_event(csat=3))
    s = log.csat_summary()
    assert s["promoter_pct"] == pytest.approx(0.0)


def test_complaint_rate_zero_when_no_complaints():
    log = _make_log()
    log.record_contact(_make_event(complaint=False))
    log.record_contact(_make_event(complaint=False))
    assert log.complaint_rate() == pytest.approx(0.0)


def test_contacts_for_customer_filters_correctly():
    log = _make_log()
    log.record_contact(_make_event(cid="C1"))
    log.record_contact(_make_event(cid="C2"))
    log.record_contact(_make_event(cid="C1"))
    c1 = log.contacts_for_customer("C1")
    c2 = log.contacts_for_customer("C2")
    assert len(c1) == 2
    assert len(c2) == 1
    assert all(e.customer_id == "C1" for e in c1)
