# Increment 3: the legs of tests/company/test_phase_hv_coverage_expansion.py that test archived modules. Its live legs stay there.
"""Phase HV: coverage expansion for contract_exposure_register, payment_ledger, gas_nomination_register."""
import datetime as dt
import pytest

# ===== contract_exposure_register =====
from company.crm.contract_exposure_register import (
    ContractExposureRegister, ContractRecord, ContractSegment, ContractStatus
)

def _fixed_contract(account_id="A1", days_ahead=100, notice_issued=False):
    end = dt.date.today() + dt.timedelta(days=days_ahead)
    return ContractRecord(
        account_id=account_id, segment=ContractSegment.DOMESTIC,
        status=ContractStatus.FIXED_TERM,
        contract_start=dt.date(2024, 1, 1), contract_end=end,
        annual_kwh=3000, unit_rate_gbp_per_kwh=0.28,
        standing_charge_gbp_per_day=0.60, notice_issued=notice_issued
    )

def _svt_contract(account_id="A2"):
    return ContractRecord(
        account_id=account_id, segment=ContractSegment.DOMESTIC,
        status=ContractStatus.STANDARD_VARIABLE,
        contract_start=dt.date(2023, 1, 1), contract_end=None,
        annual_kwh=3000, unit_rate_gbp_per_kwh=0.32,
        standing_charge_gbp_per_day=0.65, notice_issued=False
    )

class TestContractExposureRegister:
    def test_register_and_retrieve(self):
        reg = ContractExposureRegister()
        rec = reg.register_contract(_fixed_contract("A1"))
        assert reg.get_contract("A1") is rec

    def test_fixed_term_classified(self):
        reg = ContractExposureRegister()
        reg.register_contract(_fixed_contract("A1"))
        assert len(reg.fixed_term_contracts) == 1

    def test_svt_classified(self):
        reg = ContractExposureRegister()
        reg.register_contract(_svt_contract("A2"))
        assert len(reg.svt_contracts) == 1

    def test_svt_days_remaining_none(self):
        c = _svt_contract()
        assert c.days_remaining is None

    def test_in_notice_window(self):
        c = _fixed_contract(days_ahead=30)
        assert c.is_in_notice_window

    def test_not_in_notice_window_far_away(self):
        c = _fixed_contract(days_ahead=100)
        assert not c.is_in_notice_window

    def test_notice_not_issued_breach_risk(self):
        reg = ContractExposureRegister()
        reg.register_contract(_fixed_contract("A1", days_ahead=20, notice_issued=False))
        assert len(reg.notice_not_issued) == 1

    def test_notice_issued_not_in_breach_list(self):
        reg = ContractExposureRegister()
        reg.register_contract(_fixed_contract("A1", days_ahead=20, notice_issued=True))
        assert len(reg.notice_not_issued) == 0

    def test_total_annual_revenue(self):
        reg = ContractExposureRegister()
        c = _fixed_contract("A1")
        reg.register_contract(c)
        expected = 3000 * 0.28 + 0.60 * 365
        assert reg.total_annual_revenue_gbp == pytest.approx(expected, rel=1e-3)

    def test_exposure_summary_keys(self):
        reg = ContractExposureRegister()
        reg.register_contract(_fixed_contract("A1"))
        reg.register_contract(_svt_contract("A2"))
        s = reg.exposure_summary()
        assert "Contract Exposure" in s and "Fixed" in s and "SVT" in s
