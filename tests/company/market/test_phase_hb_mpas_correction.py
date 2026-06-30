"""Tests for MPAS Standing Data Correction Register -- Phase HB."""
import datetime as dt
import pytest
from company.market.mpas_standing_data_correction_register import (
    StandingDataField, CorrectionStatus,
    MPASCorrectionRecord, MPASStandingDataCorrectionRegister,
    _add_working_days, _ACK_WORKING_DAYS, _RESOLUTION_WORKING_DAYS,
    _SETTLEMENT_IMPACTING,
)

TODAY = dt.date(2024, 6, 10)
MPAN = "1000000000001"
ACC = "A001"


def make_reg():
    return MPASStandingDataCorrectionRegister()


def raise_cor(reg=None, mpan=MPAN, account=ACC, field=StandingDataField.PROFILE_CLASS,
              current="1", correct="2", date=TODAY, impact=None):
    if reg is None:
        reg = make_reg()
    return reg, reg.raise_correction(mpan, account, field, current, correct, date, impact)


class TestSettlementImpacting:
    def test_pc_is_settlement_impacting(self):
        _, rec = raise_cor(field=StandingDataField.PROFILE_CLASS)
        assert rec.is_settlement_impacting

    def test_llfc_is_settlement_impacting(self):
        _, rec = raise_cor(field=StandingDataField.LLFC, current="L1", correct="L2")
        assert rec.is_settlement_impacting

    def test_da_id_not_settlement_impacting(self):
        _, rec = raise_cor(field=StandingDataField.DA_ID, current="DA1", correct="DA2")
        assert not rec.is_settlement_impacting

    def test_dc_id_not_settlement_impacting(self):
        _, rec = raise_cor(field=StandingDataField.DC_ID, current="DC1", correct="DC2")
        assert not rec.is_settlement_impacting


class TestMPASCorrectionRecord:
    def test_is_open_when_raised(self):
        _, rec = raise_cor()
        assert rec.is_open

    def test_is_not_open_when_applied(self):
        reg, rec = raise_cor()
        applied = reg.apply(rec.correction_id, TODAY)
        assert not applied.is_open

    def test_acknowledgement_due_is_2_wd(self):
        _, rec = raise_cor(date=dt.date(2024, 6, 10))
        expected = _add_working_days(dt.date(2024, 6, 10), _ACK_WORKING_DAYS)
        assert rec.acknowledgement_due == expected

    def test_resolution_due_none_before_ack(self):
        _, rec = raise_cor()
        assert rec.resolution_due is None

    def test_resolution_due_after_ack(self):
        reg, rec = raise_cor()
        ack_date = dt.date(2024, 6, 13)
        reg.acknowledge(rec.correction_id, ack_date)
        ack_rec = reg.corrections_for_account(ACC)[0]
        expected = _add_working_days(ack_date, _RESOLUTION_WORKING_DAYS)
        assert ack_rec.resolution_due == expected

    def test_is_acknowledgement_overdue(self):
        _, rec = raise_cor(date=TODAY)
        ack_due = _add_working_days(TODAY, _ACK_WORKING_DAYS)
        assert rec.is_acknowledgement_overdue(ack_due + dt.timedelta(days=1))

    def test_is_not_acknowledgement_overdue_on_due_date(self):
        _, rec = raise_cor(date=TODAY)
        ack_due = _add_working_days(TODAY, _ACK_WORKING_DAYS)
        assert not rec.is_acknowledgement_overdue(ack_due)

    def test_is_resolution_overdue(self):
        reg, rec = raise_cor()
        ack_date = TODAY
        reg.acknowledge(rec.correction_id, ack_date)
        ack_rec = reg.corrections_for_account(ACC)[0]
        res_due = _add_working_days(ack_date, _RESOLUTION_WORKING_DAYS)
        assert ack_rec.is_resolution_overdue(res_due + dt.timedelta(days=1))

    def test_is_not_resolution_overdue_when_raised(self):
        _, rec = raise_cor()
        far_future = dt.date(2030, 1, 1)
        assert not rec.is_resolution_overdue(far_future)

    def test_correction_summary_contains_id(self):
        _, rec = raise_cor()
        assert rec.correction_id in rec.correction_summary()

    def test_frozen(self):
        _, rec = raise_cor()
        with pytest.raises((AttributeError, TypeError)):
            rec.mpan = "other"


class TestMPASStandingDataCorrectionRegister:
    def setup_method(self):
        self.reg = make_reg()

    def _raise(self, mpan=MPAN, account=ACC, field=StandingDataField.PROFILE_CLASS,
               current="1", correct="2", date=TODAY, impact=None):
        return self.reg.raise_correction(mpan, account, field, current, correct, date, impact)

    def test_raise_returns_raised_status(self):
        rec = self._raise()
        assert rec.status == CorrectionStatus.RAISED

    def test_auto_id_prefix(self):
        rec = self._raise()
        assert rec.correction_id.startswith("MPAS-COR-")

    def test_auto_id_increments(self):
        r1 = self._raise()
        r2 = self._raise(mpan="2000000000001", current="3", correct="4")
        assert r1.correction_id != r2.correction_id

    def test_same_value_raises(self):
        with pytest.raises(ValueError):
            self.reg.raise_correction(MPAN, ACC, StandingDataField.PROFILE_CLASS,
                                      "1", "1", TODAY)

    def test_acknowledge_transitions(self):
        rec = self._raise()
        acked = self.reg.acknowledge(rec.correction_id, TODAY)
        assert acked.status == CorrectionStatus.ACKNOWLEDGED

    def test_acknowledge_unknown_raises(self):
        with pytest.raises(KeyError):
            self.reg.acknowledge("MPAS-COR-99999", TODAY)

    def test_acknowledge_non_raised_raises(self):
        rec = self._raise()
        self.reg.acknowledge(rec.correction_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.acknowledge(rec.correction_id, TODAY)

    def test_apply_from_raised(self):
        rec = self._raise()
        applied = self.reg.apply(rec.correction_id, TODAY)
        assert applied.status == CorrectionStatus.APPLIED

    def test_apply_from_acknowledged(self):
        rec = self._raise()
        self.reg.acknowledge(rec.correction_id, TODAY)
        applied = self.reg.apply(rec.correction_id, TODAY)
        assert applied.status == CorrectionStatus.APPLIED

    def test_apply_non_open_raises(self):
        rec = self._raise()
        self.reg.apply(rec.correction_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.apply(rec.correction_id, TODAY)

    def test_reject_sets_reason(self):
        rec = self._raise()
        rejected = self.reg.reject(rec.correction_id, "PC already correct in MPAS")
        assert rejected.status == CorrectionStatus.REJECTED
        assert "PC already correct" in rejected.rejected_reason

    def test_escalate_transitions(self):
        rec = self._raise()
        escalated = self.reg.escalate(rec.correction_id)
        assert escalated.status == CorrectionStatus.ESCALATED

    def test_escalate_non_open_raises(self):
        rec = self._raise()
        self.reg.apply(rec.correction_id, TODAY)
        with pytest.raises(ValueError):
            self.reg.escalate(rec.correction_id)

    def test_open_corrections(self):
        r1 = self._raise()
        self._raise(mpan="2000000000001", current="3", correct="4")
        self.reg.apply(r1.correction_id, TODAY)
        assert len(self.reg.open_corrections) == 1

    def test_overdue_acknowledgements(self):
        self._raise(date=TODAY)
        ack_due = _add_working_days(TODAY, _ACK_WORKING_DAYS)
        overdue = self.reg.overdue_acknowledgements(ack_due + dt.timedelta(days=1))
        assert len(overdue) == 1

    def test_not_overdue_on_ack_due_date(self):
        self._raise(date=TODAY)
        ack_due = _add_working_days(TODAY, _ACK_WORKING_DAYS)
        assert len(self.reg.overdue_acknowledgements(ack_due)) == 0

    def test_overdue_resolutions(self):
        rec = self._raise(date=TODAY)
        ack_date = TODAY
        self.reg.acknowledge(rec.correction_id, ack_date)
        res_due = _add_working_days(ack_date, _RESOLUTION_WORKING_DAYS)
        overdue = self.reg.overdue_resolutions(res_due + dt.timedelta(days=1))
        assert len(overdue) == 1

    def test_corrections_for_account(self):
        self._raise(account=ACC)
        self._raise(mpan="2000000000001", account="A002", current="3", correct="4")
        assert len(self.reg.corrections_for_account(ACC)) == 1

    def test_corrections_for_mpan(self):
        self._raise(mpan=MPAN)
        self._raise(mpan="2000000000001", account="A002", current="3", correct="4")
        assert len(self.reg.corrections_for_mpan(MPAN)) == 1

    def test_by_field(self):
        self._raise(field=StandingDataField.PROFILE_CLASS, current="1", correct="2")
        self._raise(mpan="2000000000001", field=StandingDataField.LLFC,
                    current="L1", correct="L2")
        assert len(self.reg.by_field(StandingDataField.LLFC)) == 1

    def test_settlement_impacting_corrections_open_only(self):
        r1 = self._raise(field=StandingDataField.PROFILE_CLASS, current="1", correct="2")
        self._raise(mpan="2000000000001", field=StandingDataField.PROFILE_CLASS,
                    current="3", correct="4")
        self.reg.apply(r1.correction_id, TODAY)
        assert len(self.reg.settlement_impacting_corrections) == 1

    def test_total_financial_impact_gbp(self):
        r1 = self._raise(impact=500.0)
        self._raise(mpan="2000000000001", current="3", correct="4", impact=300.0)
        self.reg.apply(r1.correction_id, TODAY)
        assert abs(self.reg.total_financial_impact_gbp - 300.0) < 1e-9

    def test_total_financial_impact_excludes_none(self):
        self._raise(impact=None)
        assert self.reg.total_financial_impact_gbp == 0.0

    def test_summary_contains_total(self):
        self._raise()
        s = self.reg.correction_register_summary(TODAY)
        assert "1 total" in s

    def test_empty_summary(self):
        s = self.reg.correction_register_summary(TODAY)
        assert "0 total" in s
