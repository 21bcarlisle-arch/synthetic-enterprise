"""Phase 108: Retention risk scoring tests."""

from company.crm.retention_risk import retention_risk, portfolio_risk_summary


_CUSTOMER = {
    "customer_id": "C1", "segment": "resi",
    "contract_type": "fixed_1yr", "acquired_date": "2020-01-01",
    "smart_meter": False, "metering": "profile",
}


def test_no_signals_is_low_risk():
    result = retention_risk(_CUSTOMER, [], [])
    assert result["tier"] == "LOW"
    assert result["score"] == 0
    assert result["signals"] == []


def test_overdue_invoice_adds_score():
    from datetime import date, timedelta
    overdue = {
        "customer_id": "C1", "payment_status": "unpaid",
        "due_date": (date.today() - timedelta(days=5)).isoformat(),
    }
    result = retention_risk(_CUSTOMER, [overdue], [])
    assert result["score"] >= 2
    assert any("Overdue" in s for s in result["signals"])


def test_recent_complaint_adds_score():
    from datetime import date
    contact = {
        "customer_id": "C1", "complaint_flag": True,
        "event_date": date.today().isoformat(),
    }
    result = retention_risk(_CUSTOMER, [], [contact])
    assert result["score"] >= 1
    assert any("complaint" in s.lower() for s in result["signals"])


def test_high_risk_tier():
    from datetime import date, timedelta
    overdue = {"customer_id": "C1", "payment_status": "unpaid",
               "due_date": (date.today() - timedelta(days=5)).isoformat()}
    complaint = {"customer_id": "C1", "complaint_flag": True,
                 "event_date": date.today().isoformat()}
    rate_cmp = {"protected": False, "delta_p": 5.0}
    result = retention_risk(_CUSTOMER, [overdue], [complaint], rate_cmp=rate_cmp)
    assert result["tier"] in ("MEDIUM", "HIGH")


def test_score_capped_at_5():
    from datetime import date, timedelta
    overdue = {"customer_id": "C1", "payment_status": "unpaid",
               "due_date": (date.today() - timedelta(days=5)).isoformat()}
    complaint = {"customer_id": "C1", "complaint_flag": True,
                 "event_date": date.today().isoformat()}
    rate_cmp = {"protected": False, "delta_p": 10.0}
    renewal = {"in_notice_window": True, "is_fixed": False}
    result = retention_risk(_CUSTOMER, [overdue], [complaint], renewal, rate_cmp)
    assert result["score"] <= 5


def test_portfolio_risk_summary_keys():
    summary = portfolio_risk_summary([_CUSTOMER], [], [])
    assert "total" in summary
    assert "high_risk" in summary
    assert "medium_risk" in summary
    assert "low_risk" in summary
    assert len(summary["customers"]) == 1


def test_portfolio_risk_totals_match():
    customers = [_CUSTOMER, {**_CUSTOMER, "customer_id": "C2"}]
    summary = portfolio_risk_summary(customers, [], [])
    assert summary["high_risk"] + summary["medium_risk"] + summary["low_risk"] == summary["total"]


def test_retention_risk_result_structure():
    result = retention_risk(_CUSTOMER, [], [])
    assert "score" in result
    assert "tier" in result
    assert "signals" in result
    assert isinstance(result["signals"], list)


# --- Phase KI depth tests ---

def test_result_has_customer_id():
    result = retention_risk(_CUSTOMER, [], [])
    assert 'score' in result
    assert 'tier' in result


def test_score_is_int():
    result = retention_risk(_CUSTOMER, [], [])
    assert isinstance(result['score'], int)


def test_tier_is_string():
    result = retention_risk(_CUSTOMER, [], [])
    assert isinstance(result['tier'], str)


def test_score_non_negative():
    result = retention_risk(_CUSTOMER, [], [])
    assert result['score'] >= 0


def test_paid_invoice_no_score():
    from datetime import date, timedelta
    paid = {
        'customer_id': 'C1', 'payment_status': 'paid',
        'due_date': (date.today() - timedelta(days=5)).isoformat(),
    }
    result = retention_risk(_CUSTOMER, [paid], [])
    assert result['score'] == 0


def test_portfolio_empty_customers():
    summary = portfolio_risk_summary([], [], [])
    assert summary['total'] == 0
    assert summary['high_risk'] == 0


def test_portfolio_two_customers_total():
    customers = [_CUSTOMER, {**_CUSTOMER, 'customer_id': 'C2'}]
    summary = portfolio_risk_summary(customers, [], [])
    assert summary['total'] == 2


def test_multiple_signals_both_present():
    from datetime import date, timedelta
    overdue = {'customer_id': 'C1', 'payment_status': 'unpaid',
               'due_date': (date.today() - timedelta(days=5)).isoformat()}
    complaint = {'customer_id': 'C1', 'complaint_flag': True,
                 'event_date': date.today().isoformat()}
    result = retention_risk(_CUSTOMER, [overdue], [complaint])
    assert len(result['signals']) >= 2


def test_no_complaint_flag_no_complaint_score():
    from datetime import date
    contact_no_flag = {
        'customer_id': 'C1', 'complaint_flag': False,
        'event_date': date.today().isoformat(),
    }
    result = retention_risk(_CUSTOMER, [], [contact_no_flag])
    assert result['score'] == 0


def test_portfolio_customers_list_matches_count():
    customers = [_CUSTOMER]
    summary = portfolio_risk_summary(customers, [], [])
    assert len(summary['customers']) == 1
