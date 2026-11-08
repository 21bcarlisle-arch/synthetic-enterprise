"""Phase HV: coverage expansion for contract_exposure_register, payment_ledger, gas_nomination_register."""
import datetime as dt
import pytest


# ===== payment_ledger =====


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
