import datetime as dt
import pytest
from company.trading.trade_confirmation_register import (
    ConfirmationMethod, ConfirmationStatus, TradeConfirmationRecord,
    TradeConfirmationRegister, _BILATERAL_CONFIRMATION_DAYS, _ESCALATION_DAYS,
)

TRADE_DATE = dt.date(2024, 5, 10)
AS_OF = dt.date(2024, 5, 20)
CPTY = "CTR-001"
TRADE_REF = "TRD-2024-0001"


def make_record(status=ConfirmationStatus.PENDING, method=ConfirmationMethod.SIGNED_CONFIRM):
    return TradeConfirmationRecord(
        confirm_id="TC-000001", trade_ref=TRADE_REF, counterparty_id=CPTY,
        trade_date=TRADE_DATE, commodity="power", notional_mwh=1000.0,
        notional_gbp=85000.0, confirmation_method=method, status=status)


class TestTradeConfirmationRecord:
    def test_confirmation_due_bilateral(self):
        r = make_record(method=ConfirmationMethod.SIGNED_CONFIRM)
        assert r.confirmation_due == TRADE_DATE + dt.timedelta(days=_BILATERAL_CONFIRMATION_DAYS)
    def test_confirmation_due_broker(self):
        r = make_record(method=ConfirmationMethod.BROKER_TERM_SHEET)
        assert r.confirmation_due == TRADE_DATE + dt.timedelta(days=1)
    def test_confirmation_due_exchange(self):
        r = make_record(method=ConfirmationMethod.EXCHANGE_AUTO)
        assert r.confirmation_due == TRADE_DATE + dt.timedelta(days=1)
    def test_is_open_pending(self):
        assert make_record(ConfirmationStatus.PENDING).is_open
    def test_is_open_sent(self):
        assert make_record(ConfirmationStatus.SENT).is_open
    def test_is_not_open_matched(self):
        assert not make_record(ConfirmationStatus.MATCHED).is_open
    def test_is_overdue_past_due(self):
        r = make_record()
        late = r.confirmation_due + dt.timedelta(days=1)
        assert r.is_overdue(late)
    def test_is_not_overdue_on_due_date(self):
        r = make_record()
        assert not r.is_overdue(r.confirmation_due)
    def test_is_not_overdue_when_matched(self):
        r = make_record(ConfirmationStatus.MATCHED)
        assert not r.is_overdue(AS_OF)
    def test_is_long_outstanding(self):
        r = make_record()
        long_date = TRADE_DATE + dt.timedelta(days=_ESCALATION_DAYS + 1)
        assert r.is_long_outstanding(long_date)
    def test_is_not_long_outstanding_within_window(self):
        r = make_record()
        assert not r.is_long_outstanding(TRADE_DATE + dt.timedelta(days=4))
    def test_days_outstanding_open(self):
        r = make_record()
        assert r.days_outstanding(TRADE_DATE + dt.timedelta(days=5)) == 5
    def test_days_outstanding_matched(self):
        r = TradeConfirmationRecord(
            confirm_id="X", trade_ref=TRADE_REF, counterparty_id=CPTY,
            trade_date=TRADE_DATE, commodity="gas", notional_mwh=500.0,
            notional_gbp=25000.0, confirmation_method=ConfirmationMethod.SIGNED_CONFIRM,
            status=ConfirmationStatus.MATCHED, matched_date=TRADE_DATE + dt.timedelta(days=2))
        assert r.days_outstanding(AS_OF) == 2
    def test_confirmation_summary(self):
        s = make_record().confirmation_summary()
        assert "TC-000001" in s and TRADE_REF in s and CPTY in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.status = ConfirmationStatus.MATCHED


class TestTradeConfirmationRegister:
    def setup_method(self):
        self.reg = TradeConfirmationRegister()

    def test_register_trade_stored(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        assert r.status == ConfirmationStatus.PENDING

    def test_auto_id_increments(self):
        r1 = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        r2 = self.reg.register_trade("TRD-002", CPTY, TRADE_DATE, "gas",
            500.0, 25000.0, ConfirmationMethod.BROKER_TERM_SHEET)
        assert r1.confirm_id != r2.confirm_id

    def test_negative_notional_raises(self):
        with pytest.raises(ValueError):
            self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
                -1.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)

    def test_send_confirmation(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        sent = self.reg.send_confirmation(r.confirm_id, TRADE_DATE + dt.timedelta(1))
        assert sent.status == ConfirmationStatus.SENT and sent.sent_date is not None

    def test_match_confirmation(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        matched = self.reg.match_confirmation(r.confirm_id, TRADE_DATE + dt.timedelta(2))
        assert matched.status == ConfirmationStatus.MATCHED

    def test_raise_dispute(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        disputed = self.reg.raise_dispute(r.confirm_id, "Volume mismatch")
        assert disputed.status == ConfirmationStatus.DISPUTED
        assert "mismatch" in disputed.dispute_reason.lower()

    def test_cancel(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        cancelled = self.reg.cancel(r.confirm_id)
        assert cancelled.status == ConfirmationStatus.CANCELLED

    def test_update_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.match_confirmation("TC-999999", TRADE_DATE)

    def test_pending_confirmations(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        self.reg.match_confirmation(r.confirm_id, TRADE_DATE + dt.timedelta(2))
        self.reg.register_trade("TRD-002", CPTY, TRADE_DATE, "gas",
            500.0, 25000.0, ConfirmationMethod.BROKER_TERM_SHEET)
        assert len(self.reg.pending_confirmations()) == 1

    def test_overdue_confirmations(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        late = r.confirmation_due + dt.timedelta(days=1)
        assert len(self.reg.overdue_confirmations(late)) == 1
        assert len(self.reg.overdue_confirmations(TRADE_DATE)) == 0

    def test_long_outstanding(self):
        self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        long_date = TRADE_DATE + dt.timedelta(days=_ESCALATION_DAYS + 1)
        assert len(self.reg.long_outstanding(long_date)) == 1

    def test_disputed(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        self.reg.raise_dispute(r.confirm_id, "Price mismatch")
        assert len(self.reg.disputed()) == 1

    def test_by_counterparty(self):
        self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        self.reg.register_trade("TRD-002", "CTR-002", TRADE_DATE, "gas",
            500.0, 25000.0, ConfirmationMethod.BROKER_TERM_SHEET)
        assert len(self.reg.by_counterparty(CPTY)) == 1

    def test_total_pending_notional_gbp(self):
        r = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        self.reg.register_trade("TRD-002", CPTY, TRADE_DATE, "gas",
            500.0, 25000.0, ConfirmationMethod.BROKER_TERM_SHEET)
        self.reg.match_confirmation(r.confirm_id, TRADE_DATE + dt.timedelta(2))
        assert abs(self.reg.total_pending_notional_gbp() - 25000.0) < 1e-9

    def test_confirmation_rate_pct(self):
        r1 = self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        r2 = self.reg.register_trade("TRD-002", CPTY, TRADE_DATE, "gas",
            500.0, 25000.0, ConfirmationMethod.BROKER_TERM_SHEET)
        self.reg.match_confirmation(r1.confirm_id, TRADE_DATE + dt.timedelta(2))
        self.reg.cancel(r2.confirm_id)
        rate = self.reg.confirmation_rate_pct()
        assert rate == 50.0

    def test_confirmation_rate_none_when_empty(self):
        assert self.reg.confirmation_rate_pct() is None

    def test_confirmation_summary(self):
        self.reg.register_trade(TRADE_REF, CPTY, TRADE_DATE, "power",
            1000.0, 85000.0, ConfirmationMethod.SIGNED_CONFIRM)
        s = self.reg.confirmation_summary(AS_OF)
        assert "1 trades" in s

    def test_empty_summary(self):
        s = self.reg.confirmation_summary(AS_OF)
        assert "0 trades" in s
