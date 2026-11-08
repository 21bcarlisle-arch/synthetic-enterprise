import datetime as dt
import pytest
from company.market.dno_network_charge_dispute_register import (
    DUoSDisputeGround, DUoSDisputeStatus, DUoSDisputeRecord,
    DNONetworkChargeDisputeRegister, _DNO_RESPONSE_DAYS,
)

MPAN = "1012345678901"
DNO = "WPD"
INV = "INV-2024-001"
RAISED = dt.date(2024, 3, 1)
AS_OF = dt.date(2024, 6, 1)


def make_record(status=DUoSDisputeStatus.RAISED, amount=500.0):
    return DUoSDisputeRecord(
        dispute_id="DUOS-DISP-00001", mpan=MPAN, dno_code=DNO,
        invoice_ref=INV, raised_date=RAISED,
        ground=DUoSDisputeGround.WRONG_LLFC,
        disputed_amount_gbp=amount, status=status)


class TestDUoSDisputeRecord:
    def test_is_open_raised(self):
        assert make_record(DUoSDisputeStatus.RAISED).is_open
    def test_is_open_acknowledged(self):
        assert make_record(DUoSDisputeStatus.ACKNOWLEDGED).is_open
    def test_is_not_open_resolved(self):
        assert not make_record(DUoSDisputeStatus.RESOLVED_CREDIT).is_open
    def test_dno_response_due(self):
        r = make_record()
        assert r.dno_response_due == RAISED + dt.timedelta(days=_DNO_RESPONSE_DAYS)
    def test_is_dno_response_overdue(self):
        r = make_record()
        overdue_date = r.dno_response_due + dt.timedelta(days=1)
        assert r.is_dno_response_overdue(overdue_date)
    def test_is_not_overdue_when_on_time(self):
        r = make_record()
        assert not r.is_dno_response_overdue(r.dno_response_due)
    def test_is_not_overdue_when_resolved(self):
        r = make_record(DUoSDisputeStatus.RESOLVED_NO_CREDIT)
        assert not r.is_dno_response_overdue(AS_OF)
    def test_outstanding_recovery_open(self):
        r = make_record(DUoSDisputeStatus.RAISED, 500.0)
        assert abs(r.outstanding_recovery_gbp - 500.0) < 1e-9
    def test_outstanding_recovery_resolved_credit_partial(self):
        r = DUoSDisputeRecord(
            dispute_id="X", mpan=MPAN, dno_code=DNO, invoice_ref=INV, raised_date=RAISED,
            ground=DUoSDisputeGround.CALCULATION_ERROR, disputed_amount_gbp=500.0,
            status=DUoSDisputeStatus.RESOLVED_CREDIT, credit_received_gbp=300.0)
        assert abs(r.outstanding_recovery_gbp - 200.0) < 1e-9
    def test_outstanding_recovery_resolved_no_credit_is_zero(self):
        r = make_record(DUoSDisputeStatus.RESOLVED_NO_CREDIT)
        assert r.outstanding_recovery_gbp == 0.0
    def test_outstanding_recovery_withdrawn_is_zero(self):
        r = make_record(DUoSDisputeStatus.WITHDRAWN)
        assert r.outstanding_recovery_gbp == 0.0
    def test_dispute_summary(self):
        s = make_record().dispute_summary()
        assert "DUOS-DISP-00001" in s and MPAN in s and DNO in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = DUoSDisputeStatus.WITHDRAWN


class TestDNONetworkChargeDisputeRegister:
    def setup_method(self):
        self.reg = DNONetworkChargeDisputeRegister()

    def test_raise_dispute_stored(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        assert r.is_open and r.status == DUoSDisputeStatus.RAISED

    def test_auto_id_increments(self):
        r1 = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        r2 = self.reg.raise_dispute(MPAN, "UKPN", "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        assert r1.dispute_id != r2.dispute_id

    def test_zero_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 0.0)

    def test_negative_amount_raises(self):
        with pytest.raises(ValueError):
            self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, -10.0)

    def test_acknowledge(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        ack = self.reg.acknowledge(r.dispute_id, dt.date(2024, 3, 15))
        assert ack.status == DUoSDisputeStatus.ACKNOWLEDGED
        assert ack.dno_response_date == dt.date(2024, 3, 15)

    def test_resolve_with_credit(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.CALCULATION_ERROR, 500.0)
        res = self.reg.resolve_with_credit(r.dispute_id, 400.0, dt.date(2024, 4, 10))
        assert res.status == DUoSDisputeStatus.RESOLVED_CREDIT
        assert abs(res.credit_received_gbp - 400.0) < 1e-9

    def test_resolve_no_credit(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_PC, 500.0)
        res = self.reg.resolve_no_credit(r.dispute_id, dt.date(2024, 4, 10))
        assert res.status == DUoSDisputeStatus.RESOLVED_NO_CREDIT

    def test_escalate_gema(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.METERING_ERROR, 1200.0)
        esc = self.reg.escalate_gema(r.dispute_id)
        assert esc.status == DUoSDisputeStatus.ESCALATED_GEMA

    def test_withdraw(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 300.0)
        w = self.reg.withdraw(r.dispute_id)
        assert w.status == DUoSDisputeStatus.WITHDRAWN

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.acknowledge("DUOS-DISP-99999", dt.date(2024, 3, 15))

    def test_open_disputes(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        self.reg.resolve_no_credit(r.dispute_id, dt.date(2024, 4, 1))
        self.reg.raise_dispute(MPAN, DNO, "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        assert len(self.reg.open_disputes()) == 1

    def test_overdue_dno_responses(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        late = r.dno_response_due + dt.timedelta(days=1)
        assert len(self.reg.overdue_dno_responses(late)) == 1
        assert len(self.reg.overdue_dno_responses(RAISED)) == 0

    def test_by_dno(self):
        self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        self.reg.raise_dispute(MPAN, "UKPN", "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        assert len(self.reg.by_dno(DNO)) == 1

    def test_by_ground(self):
        self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        self.reg.raise_dispute(MPAN, DNO, "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        assert len(self.reg.by_ground(DUoSDisputeGround.WRONG_LLFC)) == 1

    def test_total_open_disputed_gbp(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        self.reg.raise_dispute(MPAN, DNO, "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        self.reg.resolve_no_credit(r.dispute_id, dt.date(2024, 4, 1))
        assert abs(self.reg.total_open_disputed_gbp() - 200.0) < 1e-9

    def test_total_credits_received_gbp(self):
        r = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.CALCULATION_ERROR, 500.0)
        self.reg.resolve_with_credit(r.dispute_id, 350.0, dt.date(2024, 4, 10))
        assert abs(self.reg.total_credits_received_gbp() - 350.0) < 1e-9

    def test_success_rate_pct(self):
        r1 = self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        r2 = self.reg.raise_dispute(MPAN, DNO, "INV-002", RAISED, DUoSDisputeGround.CALCULATION_ERROR, 200.0)
        self.reg.resolve_with_credit(r1.dispute_id, 400.0, dt.date(2024, 4, 1))
        self.reg.resolve_no_credit(r2.dispute_id, dt.date(2024, 4, 5))
        assert self.reg.success_rate_pct() == 50.0

    def test_success_rate_none_when_empty(self):
        assert self.reg.success_rate_pct() is None

    def test_duos_dispute_summary(self):
        self.reg.raise_dispute(MPAN, DNO, INV, RAISED, DUoSDisputeGround.WRONG_LLFC, 500.0)
        s = self.reg.duos_dispute_summary(AS_OF)
        assert "1 disputes" in s and "1 open" in s
