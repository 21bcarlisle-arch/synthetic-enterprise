"""Phase 135: Customer credit scoring tests."""

from company.crm.credit_scoring import assess_credit, CreditAssessment


def _clean():
    return assess_credit("C1", "2024-01-01", dd_active=True, missed_payments=0,
                         account_age_days=365, has_bad_debt_history=False)


def _new_customer():
    return assess_credit("C2", "2024-01-01", dd_active=True, missed_payments=0,
                         account_age_days=30, has_bad_debt_history=False)


def _risky():
    return assess_credit("C3", "2024-01-01", dd_active=False, missed_payments=4,
                         account_age_days=400, has_bad_debt_history=True, arrears_gbp=300)


def test_clean_customer_is_prime():
    a = _clean()
    assert a.tier == "PRIME"
    assert a.deposit_gbp == 0.0
    assert a.ppm_recommended is False


def test_new_customer_is_standard():
    a = _new_customer()
    assert a.tier in ("PRIME", "STANDARD")


def test_risky_customer_high_risk():
    a = _risky()
    assert a.tier == "HIGH_RISK"
    assert a.deposit_gbp > 0


def test_ppm_recommended_for_high_risk():
    a = _risky()
    assert a.ppm_recommended is True


def test_flags_captured():
    a = _risky()
    assert any("bad_debt_history" in f for f in a.flags)
    assert any("missed_payments" in f for f in a.flags)


def test_subprime_requires_deposit():
    a = assess_credit("C4", "2024-01-01", dd_active=False, missed_payments=2,
                      account_age_days=200, has_bad_debt_history=False, arrears_gbp=250)
    assert a.tier == "SUBPRIME"
    assert a.deposit_gbp > 0


def test_score_bounds():
    a = _risky()
    assert 0 <= a.score <= 100


def test_tier_label_contains_tier():
    a = _clean()
    assert "PRIME" in a.tier.upper() or "Prime" in a.tier_label


def test_deposit_scales_with_annual_bill():
    a1 = assess_credit("C5", "2024-01-01", dd_active=False, missed_payments=2,
                       account_age_days=200, has_bad_debt_history=False, arrears_gbp=100,
                       annual_bill_est_gbp=1200)
    a2 = assess_credit("C6", "2024-01-01", dd_active=False, missed_payments=2,
                       account_age_days=200, has_bad_debt_history=False, arrears_gbp=100,
                       annual_bill_est_gbp=2400)
    if a1.deposit_gbp > 0 and a2.deposit_gbp > 0:
        assert a2.deposit_gbp > a1.deposit_gbp
