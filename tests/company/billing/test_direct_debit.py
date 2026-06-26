"""Phase 113: Direct Debit mandate management tests."""

from company.billing.direct_debit import DirectDebitBook, DDPaymentAttempt


def _book():
    return DirectDebitBook()


def test_create_mandate_returns_mandate():
    b = _book()
    m = b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    assert m.customer_id == "C1"
    assert m.status == "active"
    assert m.monthly_amount_gbp == 80.0


def test_mandate_reference_includes_customer_id():
    b = _book()
    m = b.create_mandate("C2", "56-78-**", "1234", 60.0, "2024-01-01")
    assert "C2" in m.mandate_reference


def test_next_collection_date_28_days_later():
    b = _book()
    m = b.create_mandate("C3", "12-34-**", "9999", 50.0, "2024-01-01")
    assert m.next_collection_date == "2024-01-29"


def test_successful_collection_advances_next_date():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.record_attempt(DDPaymentAttempt(
        mandate_reference="DD-C1-20240101", customer_id="C1",
        attempt_date="2024-01-29", amount_gbp=80.0, outcome="collected",
    ))
    m = b.get_mandate("C1")
    assert m.next_collection_date == "2024-02-26"
    assert m.failed_attempts == 0


def test_failed_attempt_increments_counter():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.record_attempt(DDPaymentAttempt(
        mandate_reference="DD-C1-20240101", customer_id="C1",
        attempt_date="2024-01-29", amount_gbp=80.0, outcome="failed",
        failure_reason="insufficient_funds",
    ))
    m = b.get_mandate("C1")
    assert m.failed_attempts == 1
    assert m.status == "active"


def test_two_failures_suspends_mandate():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    for _ in range(2):
        b.record_attempt(DDPaymentAttempt(
            mandate_reference="DD-C1-20240101", customer_id="C1",
            attempt_date="2024-01-29", amount_gbp=80.0, outcome="failed",
            failure_reason="insufficient_funds",
        ))
    m = b.get_mandate("C1")
    assert m.status == "suspended"


def test_failed_mandates_list():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.create_mandate("C2", "99-88-**", "1111", 50.0, "2024-01-01")
    for _ in range(2):
        b.record_attempt(DDPaymentAttempt(
            mandate_reference="DD-C1-20240101", customer_id="C1",
            attempt_date="2024-01-29", amount_gbp=80.0, outcome="failed",
        ))
    assert len(b.failed_mandates()) == 1
    assert b.failed_mandates()[0].customer_id == "C1"


def test_cancel_mandate():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    assert b.cancel_mandate("C1") is True
    assert b.get_mandate("C1").status == "cancelled"


def test_reinstate_mandate_resets_failures():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.get_mandate("C1").failed_attempts = 2
    b.get_mandate("C1").status = "suspended"
    b.reinstate_mandate("C1")
    m = b.get_mandate("C1")
    assert m.status == "active"
    assert m.failed_attempts == 0


def test_dd_summary_counts():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.create_mandate("C2", "56-78-**", "2222", 60.0, "2024-01-01")
    b.cancel_mandate("C2")
    s = b.dd_summary()
    assert s["active"] == 1
    assert s["cancelled"] == 1
    assert s["total_monthly_gbp"] == 80.0


def test_dd_summary_total_monthly_excludes_cancelled():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.create_mandate("C2", "56-78-**", "9999", 40.0, "2024-01-01")
    b.cancel_mandate("C2")
    assert b.dd_summary()["total_monthly_gbp"] == 80.0


def test_attempts_for_customer():
    b = _book()
    b.create_mandate("C1", "12-34-**", "5678", 80.0, "2024-01-01")
    b.record_attempt(DDPaymentAttempt("DD-C1", "C1", "2024-01-29", 80.0, "collected"))
    b.record_attempt(DDPaymentAttempt("DD-C1", "C1", "2024-02-26", 80.0, "failed"))
    assert len(b.attempts_for_customer("C1")) == 2
    assert len(b.failed_attempts_for_customer("C1")) == 1
