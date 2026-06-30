"""Tests for Customer Resentment Ledger (Phase EA)."""
import datetime as dt
import pytest
from company.core.resentment_ledger import (
    FrictionEventType, FrictionEvent, CustomerResentmentState,
    ResentmentLedger,
    _BASE_FRICTION_SCORES, _DEFAULT_CHURN_THRESHOLD, _MONTHLY_DECAY_RATE,
)


DATE = dt.date(2024, 6, 15)
PAST = dt.date(2024, 1, 1)   # 5 months before DATE


@pytest.fixture
def ledger():
    return ResentmentLedger()


class TestFrictionScores:
    def test_complaint_unresolved_highest(self):
        assert _BASE_FRICTION_SCORES[FrictionEventType.COMPLAINT_UNRESOLVED] == 20.0

    def test_repair_negative(self):
        assert _BASE_FRICTION_SCORES[FrictionEventType.COMPLAINT_RESOLVED_WELL] < 0

    def test_bill_shock_high(self):
        assert _BASE_FRICTION_SCORES[FrictionEventType.BILL_SHOCK] >= 15.0


class TestCustomerResentmentState:
    def test_initial_score_zero(self):
        state = CustomerResentmentState(account_id="C1")
        assert state.current_score(DATE) == pytest.approx(0.0)

    def test_score_accumulates(self):
        state = CustomerResentmentState(account_id="C1")
        event = FrictionEvent(
            event_type=FrictionEventType.BILLING_ERROR,
            occurred_at=DATE,
            score_delta=15.0,
        )
        state.record(event)
        assert state.current_score(DATE) == pytest.approx(15.0)

    def test_score_decays_over_months(self):
        state = CustomerResentmentState(account_id="C1")
        state.record(FrictionEvent(
            event_type=FrictionEventType.BILLING_ERROR,
            occurred_at=PAST,
            score_delta=15.0,
        ))
        # 5 months later: 15 - 5*1 = 10
        assert state.current_score(DATE) == pytest.approx(10.0)

    def test_score_never_below_zero(self):
        state = CustomerResentmentState(account_id="C1")
        state.record(FrictionEvent(
            event_type=FrictionEventType.CALL_WAIT_LONG,
            occurred_at=PAST,
            score_delta=6.0,
        ))
        # 5 months decay: 6-5=1, but that's ok actually; test for much older event
        old = dt.date(2023, 1, 1)
        state2 = CustomerResentmentState(account_id="C2")
        state2.record(FrictionEvent(
            event_type=FrictionEventType.CALL_WAIT_LONG,
            occurred_at=old,
            score_delta=6.0,
        ))
        assert state2.current_score(DATE) == pytest.approx(0.0)

    def test_repair_reduces_score(self):
        state = CustomerResentmentState(account_id="C1")
        state.record(FrictionEvent(
            event_type=FrictionEventType.BILLING_ERROR,
            occurred_at=DATE,
            score_delta=15.0,
        ))
        state.record(FrictionEvent(
            event_type=FrictionEventType.COMPLAINT_RESOLVED_WELL,
            occurred_at=DATE,
            score_delta=-5.0,
        ))
        assert state.current_score(DATE) == pytest.approx(10.0)

    def test_amplifier(self):
        state = CustomerResentmentState(account_id="C1")
        state.record(FrictionEvent(
            event_type=FrictionEventType.BILLING_ERROR,
            occurred_at=DATE,
            score_delta=15.0,
            amplifier=2.0,  # severity ×2
        ))
        assert state.current_score(DATE) == pytest.approx(30.0)

    def test_threshold_triggers_burn(self):
        state = CustomerResentmentState(account_id="C1", churn_threshold=20.0)
        state.record(FrictionEvent(
            event_type=FrictionEventType.COMPLAINT_UNRESOLVED,
            occurred_at=DATE,
            score_delta=25.0,
        ))
        assert state.check_threshold(DATE)
        assert state.is_burned

    def test_burned_score_is_inf(self):
        state = CustomerResentmentState(account_id="C1", churn_threshold=20.0)
        state.record(FrictionEvent(
            event_type=FrictionEventType.COMPLAINT_UNRESOLVED,
            occurred_at=DATE,
            score_delta=25.0,
        ))
        state.check_threshold(DATE)
        assert state.current_score(DATE) == float("inf")


class TestResentmentLedger:
    def test_record_and_score(self, ledger):
        ledger.record_friction("C1", FrictionEventType.BILLING_ERROR, DATE)
        assert ledger.current_score("C1", DATE) == pytest.approx(15.0)

    def test_missing_account_score_zero(self, ledger):
        assert ledger.current_score("MISSING", DATE) == pytest.approx(0.0)

    def test_burned_accounts(self, ledger):
        ledger.record_friction("C1", FrictionEventType.COMPLAINT_UNRESOLVED, DATE,
                               amplifier=3.0)  # 20*3=60 > 50 threshold
        ledger.check_churn_threshold("C1", DATE)
        burned = ledger.burned_accounts()
        assert "C1" in burned

    def test_at_risk_accounts(self, ledger):
        # Add 70% of threshold = 35 pts
        ledger.record_friction("C1", FrictionEventType.BILL_SHOCK, DATE, amplifier=2.0)
        # 18*2=36 > 50*0.7=35
        at_risk = ledger.at_risk_accounts(DATE)
        assert "C1" in at_risk

    def test_high_scorers(self, ledger):
        ledger.record_friction("C1", FrictionEventType.BILLING_ERROR, DATE)  # 15
        ledger.record_friction("C2", FrictionEventType.BILL_SHOCK, DATE)     # 18
        top = ledger.high_scorers(DATE, top_n=1)
        assert top[0][0] == "C2"

    def test_resentment_summary(self, ledger):
        ledger.record_friction("C1", FrictionEventType.BILLING_ERROR, DATE)
        s = ledger.resentment_summary(DATE)
        assert "Resentment Ledger" in s
        assert "burned" in s.lower()

    def test_constants(self):
        assert _DEFAULT_CHURN_THRESHOLD == pytest.approx(50.0)
        assert _MONTHLY_DECAY_RATE == pytest.approx(1.0)
