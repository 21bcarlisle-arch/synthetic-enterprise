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


# ===== payment_ledger =====
from company.billing.payment_ledger import (
    PaymentLedger, PaymentRecord, PaymentMethodType, PaymentOutcome
)

def _rec(pid="P1", account="C1", amount=100.0, outcome=PaymentOutcome.SUCCESS,
         method=PaymentMethodType.DIRECT_DEBIT, pdate="2024-03-01"):
    return PaymentRecord(
        payment_id=pid, account_id=account, payment_date=pdate,
        amount_gbp=amount, method=method, outcome=outcome,
        reference="REF001", invoice_numbers=(101,)
    )

class TestPaymentLedger:
    def test_record_and_retrieve(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1"))
        assert len(ledger.payments_for_account("C1")) == 1

    def test_successful_total_gbp(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", amount=100.0, outcome=PaymentOutcome.SUCCESS))
        ledger.record(_rec("P2", amount=50.0, outcome=PaymentOutcome.FAILED))
        assert ledger.successful_total_gbp("C1") == pytest.approx(100.0)

    def test_failed_payments_filtered(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", outcome=PaymentOutcome.FAILED))
        ledger.record(_rec("P2", outcome=PaymentOutcome.SUCCESS))
        assert len(ledger.failed_payments("C1")) == 1

    def test_pending_payments_filtered(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", outcome=PaymentOutcome.PENDING))
        assert len(ledger.pending_payments("C1")) == 1

    def test_payments_by_date_ordered(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", pdate="2024-06-01"))
        ledger.record(_rec("P2", pdate="2024-01-01"))
        ordered = ledger.payments_by_date("C1")
        assert ordered[0].payment_date < ordered[1].payment_date

    def test_method_breakdown_keys(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", method=PaymentMethodType.DIRECT_DEBIT))
        bd = ledger.payment_method_breakdown("C1")
        assert PaymentMethodType.DIRECT_DEBIT.value in bd

    def test_ledger_summary_in_credit(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", amount=120.0, outcome=PaymentOutcome.SUCCESS))
        s = ledger.ledger_summary("C1", total_billed_gbp=100.0)
        assert s["in_credit"] is True
        assert s["balance_gbp"] == pytest.approx(20.0)

    def test_ledger_summary_owing(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", amount=80.0, outcome=PaymentOutcome.SUCCESS))
        s = ledger.ledger_summary("C1", total_billed_gbp=100.0)
        assert s["in_credit"] is False
        assert s["amount_owing_gbp"] == pytest.approx(20.0)

    def test_all_accounts(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", account="C1"))
        ledger.record(_rec("P2", account="C2"))
        assert sorted(ledger.all_accounts()) == ["C1", "C2"]

    def test_portfolio_summary_failure_rate(self):
        ledger = PaymentLedger()
        ledger.record(_rec("P1", outcome=PaymentOutcome.FAILED))
        ledger.record(_rec("P2", outcome=PaymentOutcome.SUCCESS))
        ps = ledger.portfolio_summary()
        assert ps["failure_rate_pct"] == pytest.approx(50.0)


# ===== gas_nomination_register =====
from company.market.gas_nomination_register import (
    GasNominationRegister, NominationStatus, ImbalanceDirection
)

class TestGasNominationRegister:
    def test_nominate_creates_record(self):
        reg = GasNominationRegister()
        rec = reg.nominate(dt.date(2023, 1, 1), 1000.0)
        assert rec.nominated_kwh == 1000.0
        assert rec.status == NominationStatus.INITIAL

    def test_revise_updates_effective_kwh(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1000.0)
        rev = reg.revise(dt.date(2023, 1, 1), 1200.0)
        assert rev.effective_nominated_kwh == 1200.0
        assert rev.status == NominationStatus.REVISED

    def test_settle_records_actual(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1000.0)
        settled = reg.settle(dt.date(2023, 1, 1), 1050.0)
        assert settled.actual_consumed_kwh == 1050.0
        assert settled.status == NominationStatus.SETTLED

    def test_imbalance_kwh_long(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1100.0)
        s = reg.settle(dt.date(2023, 1, 1), 1000.0)
        assert s.imbalance_kwh == pytest.approx(100.0)

    def test_direction_long(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1200.0)
        s = reg.settle(dt.date(2023, 1, 1), 1000.0)
        assert s.direction == ImbalanceDirection.LONG

    def test_direction_short(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 900.0)
        s = reg.settle(dt.date(2023, 1, 1), 1000.0)
        assert s.direction == ImbalanceDirection.SHORT

    def test_balanced_within_tolerance(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1000.0)
        s = reg.settle(dt.date(2023, 1, 1), 1020.0)  # 2% delta, within 5%
        assert s.is_in_tolerance is True

    def test_out_of_tolerance_days(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1300.0)
        reg.settle(dt.date(2023, 1, 1), 1000.0)  # 30% long — out of tolerance
        assert len(reg.out_of_tolerance_days) == 1

    def test_mean_imbalance_pct(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1100.0)
        reg.settle(dt.date(2023, 1, 1), 1000.0)  # +10%
        reg.nominate(dt.date(2023, 1, 2), 900.0)
        reg.settle(dt.date(2023, 1, 2), 1000.0)  # -10%
        mean = reg.mean_imbalance_pct
        assert mean == pytest.approx(0.0, abs=0.1)

    def test_nomination_summary_keys(self):
        reg = GasNominationRegister()
        reg.nominate(dt.date(2023, 1, 1), 1000.0)
        s = reg.nomination_summary()
        assert "Gas Nomination" in s and "Short" in s
