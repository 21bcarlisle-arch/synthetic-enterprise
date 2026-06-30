import datetime as dt
import pytest
from company.crm.tpi_conduct_register import (
    TPIMisconductType, TPIComplaintStatus, TPISanction,
    TPIComplaintRecord, TPIConductRegister, _INVESTIGATION_DAYS,
)

TPI = "TPI-BROKER-001"
ACCOUNT = "ACC-001"
RECEIVED = dt.date(2024, 5, 1)
AS_OF = dt.date(2024, 6, 1)


def make_record(status=TPIComplaintStatus.RECEIVED, misconduct=TPIMisconductType.MIS_SELLING):
    return TPIComplaintRecord(
        complaint_id="TPIC-00001", tpi_id=TPI, customer_account_id=ACCOUNT,
        received_date=RECEIVED, misconduct_type=misconduct, status=status)


class TestTPIComplaintRecord:
    def test_investigation_due(self):
        r = make_record()
        assert r.investigation_due == RECEIVED + dt.timedelta(days=_INVESTIGATION_DAYS)
    def test_is_overdue_past_due(self):
        r = make_record()
        late = r.investigation_due + dt.timedelta(1)
        assert r.is_overdue(late)
    def test_is_not_overdue_on_due_date(self):
        r = make_record()
        assert not r.is_overdue(r.investigation_due)
    def test_is_not_overdue_when_resolved(self):
        r = make_record(TPIComplaintStatus.UPHELD)
        assert not r.is_overdue(AS_OF)
    def test_is_serious_contract_forgery(self):
        r = make_record(misconduct=TPIMisconductType.CONTRACT_FORGERY)
        assert r.is_serious
    def test_is_serious_data_misuse(self):
        r = make_record(misconduct=TPIMisconductType.DATA_MISUSE)
        assert r.is_serious
    def test_is_not_serious_mis_selling(self):
        assert not make_record(misconduct=TPIMisconductType.MIS_SELLING).is_serious
    def test_is_open_received(self):
        assert make_record(TPIComplaintStatus.RECEIVED).is_open
    def test_is_open_under_investigation(self):
        assert make_record(TPIComplaintStatus.UNDER_INVESTIGATION).is_open
    def test_is_not_open_upheld(self):
        assert not make_record(TPIComplaintStatus.UPHELD).is_open
    def test_complaint_summary(self):
        s = make_record().complaint_summary()
        assert "TPIC-00001" in s and TPI in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = TPIComplaintStatus.UPHELD


class TestTPIConductRegister:
    def setup_method(self):
        self.reg = TPIConductRegister()

    def test_receive_complaint_stored(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        assert r.status == TPIComplaintStatus.RECEIVED

    def test_auto_id_increments(self):
        r1 = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        r2 = self.reg.receive_complaint(TPI, "ACC-002", RECEIVED, TPIMisconductType.CHERRY_PICKING)
        assert r1.complaint_id != r2.complaint_id

    def test_start_investigation(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        inv = self.reg.start_investigation(r.complaint_id, RECEIVED + dt.timedelta(2))
        assert inv.status == TPIComplaintStatus.UNDER_INVESTIGATION
        assert inv.investigation_date == RECEIVED + dt.timedelta(2)

    def test_uphold(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        upheld = self.reg.uphold(r.complaint_id, AS_OF, TPISanction.WARNING_ISSUED, 150.0)
        assert upheld.status == TPIComplaintStatus.UPHELD
        assert upheld.sanction == TPISanction.WARNING_ISSUED
        assert abs(upheld.customer_remedy_gbp - 150.0) < 1e-9

    def test_not_uphold(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        not_upheld = self.reg.not_uphold(r.complaint_id, AS_OF)
        assert not_upheld.status == TPIComplaintStatus.NOT_UPHELD

    def test_escalate_to_ofgem(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.CONTRACT_FORGERY)
        esc = self.reg.escalate_to_ofgem(r.complaint_id)
        assert esc.status == TPIComplaintStatus.ESCALATED_OFGEM
        assert esc.sanction == TPISanction.REPORTED_TO_OFGEM

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.not_uphold("TPIC-99999", AS_OF)

    def test_open_complaints(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        self.reg.not_uphold(r.complaint_id, AS_OF)
        self.reg.receive_complaint(TPI, "ACC-002", RECEIVED, TPIMisconductType.CHERRY_PICKING)
        assert len(self.reg.open_complaints()) == 1

    def test_overdue_investigations(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        late = r.investigation_due + dt.timedelta(1)
        assert len(self.reg.overdue_investigations(late)) == 1
        assert len(self.reg.overdue_investigations(RECEIVED)) == 0

    def test_complaints_for_tpi(self):
        self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        self.reg.receive_complaint("TPI-002", "ACC-002", RECEIVED, TPIMisconductType.CHERRY_PICKING)
        assert len(self.reg.complaints_for_tpi(TPI)) == 1

    def test_serious_complaints(self):
        self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.CONTRACT_FORGERY)
        self.reg.receive_complaint(TPI, "ACC-002", RECEIVED, TPIMisconductType.MIS_SELLING)
        assert len(self.reg.serious_complaints()) == 1

    def test_upheld_complaints(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        self.reg.uphold(r.complaint_id, AS_OF, TPISanction.WARNING_ISSUED)
        self.reg.receive_complaint(TPI, "ACC-002", RECEIVED, TPIMisconductType.CHERRY_PICKING)
        assert len(self.reg.upheld_complaints()) == 1

    def test_uphold_rate_pct(self):
        r1 = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        r2 = self.reg.receive_complaint(TPI, "ACC-002", RECEIVED, TPIMisconductType.CHERRY_PICKING)
        self.reg.uphold(r1.complaint_id, AS_OF, TPISanction.WARNING_ISSUED)
        self.reg.not_uphold(r2.complaint_id, AS_OF)
        rate = self.reg.uphold_rate_pct()
        assert rate == 50.0

    def test_uphold_rate_none_when_no_terminal(self):
        self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        assert self.reg.uphold_rate_pct() is None

    def test_total_customer_remedy_gbp(self):
        r = self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        self.reg.uphold(r.complaint_id, AS_OF, TPISanction.WARNING_ISSUED, 200.0)
        assert abs(self.reg.total_customer_remedy_gbp() - 200.0) < 1e-9

    def test_tpis_with_repeat_complaints(self):
        for _ in range(3):
            self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        self.reg.receive_complaint("TPI-002", ACCOUNT, RECEIVED, TPIMisconductType.CHERRY_PICKING)
        repeat_tpis = self.reg.tpis_with_repeat_complaints(threshold=3)
        assert TPI in repeat_tpis and "TPI-002" not in repeat_tpis

    def test_conduct_summary(self):
        self.reg.receive_complaint(TPI, ACCOUNT, RECEIVED, TPIMisconductType.MIS_SELLING)
        s = self.reg.conduct_summary(AS_OF)
        assert "1 complaints" in s and "1 open" in s
