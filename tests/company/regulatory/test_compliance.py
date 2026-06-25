"""Tests for M2: Regulatory reporting (Phase 74)."""

import pytest
from company.regulatory.compliance import (
    COMPLAINT_RESOLUTION_TARGET,
    annual_turnover_fee,
    check_price_cap_compliance,
    generate_css_filing,
    smart_meter_compliance_status,
    smart_meter_target,
)


def test_smart_meter_target_resi_2022():
    assert smart_meter_target(2022, "resi") == pytest.approx(0.70)


def test_smart_meter_target_ic_always_100pct():
    for yr in range(2016, 2026):
        assert smart_meter_target(yr, "ic") == 1.0


def test_smart_meter_target_sme_lower_than_resi():
    t_resi = smart_meter_target(2022, "resi")
    t_sme = smart_meter_target(2022, "sme")
    assert t_sme < t_resi


def test_smart_meter_compliance_compliant():
    status = smart_meter_compliance_status(0.75, 2022, "resi")
    assert status == "COMPLIANT"


def test_smart_meter_compliance_at_risk():
    status = smart_meter_compliance_status(0.67, 2022, "resi")
    assert status == "AT_RISK"


def test_smart_meter_compliance_breach():
    status = smart_meter_compliance_status(0.50, 2022, "resi")
    assert status == "BREACH"


def test_price_cap_compliance_all_clear():
    records = [
        {"customer_id": "C1", "unit_rate_p_per_kwh": 30.0, "standing_charge_p_per_day": 50.0}
    ]
    result = check_price_cap_compliance(records, cap_unit_rate_p_per_kwh=35.0,
                                        cap_standing_charge_p_per_day=60.0)
    assert result["compliant"] is True
    assert result["breaches"] == []
    assert result["checked"] == 1


def test_price_cap_compliance_breach_on_unit_rate():
    records = [
        {"customer_id": "C2", "unit_rate_p_per_kwh": 50.0, "standing_charge_p_per_day": 50.0}
    ]
    result = check_price_cap_compliance(records, cap_unit_rate_p_per_kwh=35.0,
                                        cap_standing_charge_p_per_day=60.0)
    assert result["compliant"] is False
    assert len(result["breaches"]) == 1
    assert result["breaches"][0]["customer_id"] == "C2"


def test_price_cap_compliance_empty_records():
    result = check_price_cap_compliance([], 35.0, 60.0)
    assert result["compliant"] is True
    assert result["checked"] == 0


def test_css_filing_structure():
    events = [
        {"event_date": "2022-03-01", "complaint_flag": True, "outcome": "resolved",
         "vulnerability_flag": False, "channel": "phone"},
        {"event_date": "2022-05-01", "complaint_flag": True, "outcome": "escalated",
         "vulnerability_flag": True, "channel": "email"},
        {"event_date": "2022-07-01", "complaint_flag": False, "outcome": "resolved",
         "vulnerability_flag": False, "channel": "portal"},
    ]
    result = generate_css_filing(events, 2022)
    assert result["year"] == 2022
    assert result["total_contacts"] == 3
    assert result["total_complaints"] == 2
    assert result["complaints_resolved"] == 1
    assert result["complaint_resolution_rate"] == pytest.approx(0.5)
    assert result["resolution_target_met"] is False
    assert result["vulnerable_customers_contacted"] == 1


def test_css_filing_year_filter():
    events = [
        {"event_date": "2022-03-01", "complaint_flag": False, "outcome": "resolved",
         "vulnerability_flag": False},
        {"event_date": "2023-03-01", "complaint_flag": False, "outcome": "resolved",
         "vulnerability_flag": False},
    ]
    result = generate_css_filing(events, 2022)
    assert result["total_contacts"] == 1


def test_css_resolution_target_met_when_all_resolved():
    events = [
        {"event_date": "2022-01-01", "complaint_flag": True, "outcome": "resolved",
         "vulnerability_flag": False}
    ]
    result = generate_css_filing(events, 2022)
    assert result["resolution_target_met"] is True
    assert result["complaint_resolution_rate"] == pytest.approx(1.0)


def test_annual_turnover_fee():
    fee = annual_turnover_fee(1_000_000.0)
    assert fee == pytest.approx(700.0)
