"""Phase 93: Warm Home Discount (WHD) module tests."""

from company.regulatory.warm_home_discount import (
    whd_rebate_amount,
    whd_eligible_customers,
    compute_whd_liability,
    whd_summary,
)
from company.crm.service_log import ServiceLog, ServiceEvent


def _log_with_vuln(*customer_ids):
    log = ServiceLog()
    for cid in customer_ids:
        ev = ServiceEvent(
            customer_id=cid, event_date="2026-06-26",
            channel="portal", contact_reason="general",
            outcome="pending", vulnerability_flag=True,
        )
        log.record_contact(ev)
    return log


def test_rebate_amount_2022():
    assert whd_rebate_amount(2022) == 150.0


def test_rebate_amount_2021():
    assert whd_rebate_amount(2021) == 140.0


def test_rebate_amount_unknown_year():
    assert whd_rebate_amount(2030) == 150.0  # default


def test_eligible_empty_log():
    log = ServiceLog()
    assert whd_eligible_customers(log) == []


def test_eligible_with_vuln_customers():
    log = _log_with_vuln("C1", "C5")
    eligible = whd_eligible_customers(log)
    assert set(eligible) == {"C1", "C5"}


def test_compute_liability_zero():
    assert compute_whd_liability(0, 2025) == 0.0


def test_compute_liability_three_customers():
    assert compute_whd_liability(3, 2025) == 450.0


def test_whd_summary_structure():
    log = _log_with_vuln("C1")
    summary = whd_summary(log, 2025)
    assert summary["eligible_count"] == 1
    assert summary["total_liability_gbp"] == 150.0
    assert summary["rebate_per_customer_gbp"] == 150.0
    assert "scheme_year" in summary


def test_whd_scheme_year_format():
    log = ServiceLog()
    summary = whd_summary(log, 2025)
    assert summary["scheme_year"] == "WHD 2025/26"


def test_regulatory_page_has_whd_section():
    from starlette.testclient import TestClient
    from company.portal.app import app
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "Warm Home Discount" in r.text


def test_dashboard_shows_whd_badge_for_vulnerable(tmp_path):
    from company.portal.app import _SERVICE_LOG
    from starlette.testclient import TestClient
    from company.portal.app import app
    ev = ServiceEvent(
        customer_id="C1", event_date="2026-06-26",
        channel="phone", contact_reason="general",
        outcome="pending", vulnerability_flag=True,
    )
    _SERVICE_LOG.record_contact(ev)
    client = TestClient(app, raise_server_exceptions=True)
    r = client.get("/account/C1")
    assert "Warm Home Discount eligible" in r.text
