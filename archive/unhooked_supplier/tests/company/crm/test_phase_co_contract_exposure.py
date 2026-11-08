"""Phase CO: Contract Exposure Register tests."""
import pytest
from datetime import date, timedelta
from company.crm.contract_exposure_register import (
    ContractExposureRegister, ContractRecord,
    ContractStatus, ContractSegment
)


def _today():
    return date.today()


def _fixed_contract(account_id="C1", days_remaining=180) -> ContractRecord:
    end = _today() + timedelta(days=days_remaining)
    return ContractRecord(
        account_id=account_id,
        segment=ContractSegment.DOMESTIC,
        status=ContractStatus.FIXED_TERM,
        contract_start=date(2024, 1, 1),
        contract_end=end,
        annual_kwh=3500,
        unit_rate_gbp_per_kwh=0.28,
        standing_charge_gbp_per_day=0.60,
    )


def _svt_contract(account_id="C2") -> ContractRecord:
    return ContractRecord(
        account_id=account_id,
        segment=ContractSegment.DOMESTIC,
        status=ContractStatus.STANDARD_VARIABLE,
        contract_start=date(2023, 1, 1),
        contract_end=None,
        annual_kwh=3000,
        unit_rate_gbp_per_kwh=0.30,
        standing_charge_gbp_per_day=0.65,
    )


def _reg_with_both() -> ContractExposureRegister:
    r = ContractExposureRegister()
    r.register_contract(_fixed_contract())
    r.register_contract(_svt_contract())
    return r


# 1. Register stores contract
def test_register_stores_contract():
    r = ContractExposureRegister()
    c = r.register_contract(_fixed_contract())
    assert r.get_contract("C1") == c


# 2. is_fixed_term property
def test_is_fixed_term():
    c = _fixed_contract()
    assert c.is_fixed_term


# 3. is_svt property
def test_is_svt():
    c = _svt_contract()
    assert c.is_svt


# 4. days_remaining correct
def test_days_remaining():
    c = _fixed_contract(days_remaining=100)
    assert c.days_remaining == 100


# 5. SVT has None days_remaining
def test_svt_days_remaining_none():
    c = _svt_contract()
    assert c.days_remaining is None


# 6. is_in_notice_window correct for 30 days remaining
def test_in_notice_window():
    c = _fixed_contract(days_remaining=30)
    assert c.is_in_notice_window


# 7. Not in notice window at 180 days
def test_not_in_notice_window():
    c = _fixed_contract(days_remaining=180)
    assert not c.is_in_notice_window


# 8. annual_contract_revenue_gbp calculation
def test_annual_revenue():
    c = _fixed_contract()
    # 3500 × 0.28 + 0.60 × 365 = 980 + 219 = 1199
    expected = 3500 * 0.28 + 0.60 * 365
    assert abs(c.annual_contract_revenue_gbp - expected) < 0.01


# 9. fixed_term_contracts and svt_contracts filtered correctly
def test_filter_by_type():
    r = _reg_with_both()
    assert len(r.fixed_term_contracts) == 1
    assert len(r.svt_contracts) == 1


# 10. svt_revenue_at_risk_gbp includes only SVT
def test_svt_revenue_at_risk():
    r = _reg_with_both()
    # SVT: 3000 × 0.30 + 0.65 × 365 = 900 + 237.25 = 1137.25
    expected_svt = 3000 * 0.30 + 0.65 * 365
    assert abs(r.svt_revenue_at_risk_gbp - expected_svt) < 0.01


# 11. notice_not_issued identifies SLC 22 breach risk
def test_notice_not_issued():
    r = ContractExposureRegister()
    near = _fixed_contract("C_near", days_remaining=30)  # notice window, not issued
    r.register_contract(near)
    r.register_contract(ContractRecord(
        account_id="C_notified",
        segment=ContractSegment.DOMESTIC,
        status=ContractStatus.FIXED_TERM,
        contract_start=date(2024, 1, 1),
        contract_end=_today() + timedelta(days=25),
        annual_kwh=3000, unit_rate_gbp_per_kwh=0.28,
        standing_charge_gbp_per_day=0.60, notice_issued=True,
    ))
    assert len(r.notice_not_issued) == 1
    assert r.notice_not_issued[0].account_id == "C_near"


# 12. exposure_summary contains key fields
def test_exposure_summary():
    r = _reg_with_both()
    summary = r.exposure_summary()
    assert "Contract Exposure" in summary
    assert "Fixed: 1" in summary
    assert "SVT: 1" in summary


# --- Phase LT depth tests ---

def test_account_id_stored():
    c = _fixed_contract(account_id='ACCT_LT')
    assert c.account_id == 'ACCT_LT'


def test_segment_stored():
    c = _fixed_contract()
    assert c.segment == ContractSegment.DOMESTIC


def test_status_stored():
    c = _fixed_contract()
    assert c.status == ContractStatus.FIXED_TERM


def test_annual_kwh_stored():
    c = _fixed_contract()
    assert c.annual_kwh == pytest.approx(3500)


def test_unit_rate_stored():
    c = _fixed_contract()
    assert c.unit_rate_gbp_per_kwh == pytest.approx(0.28)


def test_standing_charge_stored():
    c = _fixed_contract()
    assert c.standing_charge_gbp_per_day == pytest.approx(0.60)


def test_notice_issued_default_false():
    c = _fixed_contract()
    assert c.notice_issued is False


def test_register_contract_returns_record():
    reg = ContractExposureRegister()
    c = _fixed_contract()
    result = reg.register_contract(c)
    assert result is c


def test_get_contract_found():
    reg = ContractExposureRegister()
    c = _fixed_contract(account_id='CGET')
    reg.register_contract(c)
    assert reg.get_contract('CGET') is c


def test_annual_contract_revenue_computed():
    c = _fixed_contract()
    expected = 3500 * 0.28 + 0.60 * 365
    assert c.annual_contract_revenue_gbp == pytest.approx(expected, rel=0.01)
