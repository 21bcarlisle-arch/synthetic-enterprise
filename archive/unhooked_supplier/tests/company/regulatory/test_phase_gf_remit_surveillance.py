"""Tests for Phase GF: REMIT Market Abuse Surveillance Register."""
import datetime as dt
import pytest
from company.regulatory.remit_surveillance_register import (
    MarketAbuseType, SurveillanceAlertStatus, SurveillanceAlertRecord,
    REMITSurveillanceRegister,
)

RAISED = dt.date(2024, 3, 1)
AS_OF = dt.date(2024, 4, 30)

def make_record(status=SurveillanceAlertStatus.OPEN, abuse=MarketAbuseType.SUSPICIOUS_TIMING):
    return SurveillanceAlertRecord(
        alert_id="REMIT-SURV-00001", raised_date=RAISED,
        abuse_type=abuse, description="Unusual pattern",
        related_trade_ids=("T-001", "T-002"), status=status)

class TestSurveillanceAlertRecord:
    def test_is_open_when_open(self):
        assert make_record(SurveillanceAlertStatus.OPEN).is_open
    def test_is_open_under_investigation(self):
        assert make_record(SurveillanceAlertStatus.UNDER_INVESTIGATION).is_open
    def test_is_open_escalated(self):
        assert make_record(SurveillanceAlertStatus.ESCALATED).is_open
    def test_is_not_open_when_closed(self):
        r = make_record(SurveillanceAlertStatus.CLOSED_NO_ACTION)
        assert not r.is_open
    def test_is_escalated(self):
        assert make_record(SurveillanceAlertStatus.ESCALATED).is_escalated
    def test_str_submitted(self):
        r = SurveillanceAlertRecord(
            alert_id="X", raised_date=RAISED, abuse_type=MarketAbuseType.INSIDER_TRADING,
            description="D", related_trade_ids=(), status=SurveillanceAlertStatus.STR_SUBMITTED,
            str_submitted_date=dt.date(2024, 3, 10))
        assert r.str_submitted
    def test_potentially_requires_str_insider(self):
        r = make_record(abuse=MarketAbuseType.INSIDER_TRADING)
        assert r.potentially_requires_str
    def test_potentially_requires_str_wash_trade(self):
        r = make_record(abuse=MarketAbuseType.WASH_TRADE)
        assert r.potentially_requires_str
    def test_not_requires_str_suspicious_timing(self):
        r = make_record(abuse=MarketAbuseType.SUSPICIOUS_TIMING)
        assert not r.potentially_requires_str
    def test_days_open_no_closed_date(self):
        r = make_record()
        assert r.days_open(RAISED + dt.timedelta(15)) == 15
    def test_days_open_with_closed_date(self):
        r = SurveillanceAlertRecord(
            alert_id="X", raised_date=RAISED, abuse_type=MarketAbuseType.SUSPICIOUS_TIMING,
            description="D", related_trade_ids=(), status=SurveillanceAlertStatus.CLOSED_NO_ACTION,
            closed_date=RAISED + dt.timedelta(20))
        assert r.days_open(AS_OF) == 20
    def test_alert_summary_string(self):
        r = make_record()
        s = r.alert_summary()
        assert "REMIT-SURV-00001" in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.description = "changed"

class TestREMITSurveillanceRegister:
    def setup_method(self):
        self.reg = REMITSurveillanceRegister()
    def test_raise_alert_stored(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "Desc", ("T-001",))
        assert r.status == SurveillanceAlertStatus.OPEN
    def test_raise_alert_auto_id(self):
        r1 = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D1")
        r2 = self.reg.raise_alert(RAISED, MarketAbuseType.INSIDER_TRADING, "D2")
        assert r1.alert_id != r2.alert_id
    def test_commence_investigation(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D")
        inv = self.reg.commence_investigation(r.alert_id, "Checking logs")
        assert inv.status == SurveillanceAlertStatus.UNDER_INVESTIGATION
        assert "Checking" in inv.investigation_notes
    def test_escalate(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.PRICE_MANIPULATION, "D")
        esc = self.reg.escalate(r.alert_id)
        assert esc.is_escalated
    def test_close_no_action(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D")
        closed = self.reg.close_no_action(r.alert_id, dt.date(2024, 3, 15))
        assert closed.status == SurveillanceAlertStatus.CLOSED_NO_ACTION
        assert closed.closed_date == dt.date(2024, 3, 15)
    def test_submit_str(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.INSIDER_TRADING, "D")
        submitted = self.reg.submit_str(r.alert_id, dt.date(2024, 3, 10))
        assert submitted.str_submitted and submitted.str_submitted_date == dt.date(2024, 3, 10)
    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.escalate("REMIT-SURV-99999")
    def test_open_alerts(self):
        r1 = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D1")
        r2 = self.reg.raise_alert(RAISED, MarketAbuseType.INSIDER_TRADING, "D2")
        self.reg.close_no_action(r1.alert_id, dt.date(2024, 3, 15))
        assert len(self.reg.open_alerts()) == 1
    def test_escalated_alerts(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.PRICE_MANIPULATION, "D")
        self.reg.escalate(r.alert_id)
        assert len(self.reg.escalated_alerts()) == 1
    def test_str_submitted_alerts(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.INSIDER_TRADING, "D")
        self.reg.submit_str(r.alert_id, dt.date(2024, 3, 10))
        assert len(self.reg.str_submitted_alerts()) == 1
    def test_by_type(self):
        self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D1")
        self.reg.raise_alert(RAISED, MarketAbuseType.WASH_TRADE, "D2")
        assert len(self.reg.by_type(MarketAbuseType.SUSPICIOUS_TIMING)) == 1
    def test_potential_str_required(self):
        self.reg.raise_alert(RAISED, MarketAbuseType.INSIDER_TRADING, "D")
        self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D2")
        assert len(self.reg.potential_str_required()) == 1
    def test_long_open_alerts(self):
        self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D")
        long = self.reg.long_open_alerts(RAISED + dt.timedelta(11))
        assert len(long) == 1
        not_long = self.reg.long_open_alerts(RAISED + dt.timedelta(9))
        assert len(not_long) == 0
    def test_surveillance_summary(self):
        r = self.reg.raise_alert(RAISED, MarketAbuseType.SUSPICIOUS_TIMING, "D")
        s = self.reg.surveillance_summary(AS_OF)
        assert "1 alerts" in s
    def test_empty_summary(self):
        s = self.reg.surveillance_summary(AS_OF)
        assert "0 alerts" in s
