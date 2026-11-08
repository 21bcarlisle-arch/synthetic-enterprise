"""Tests for Phase GH: Energy Theft Risk Scoring Register."""
import datetime as dt
import pytest
from company.billing.theft_risk_scoring_register import (
    TheftRiskIndicator, TheftRiskLevel, TheftRiskScoringRecord,
    TheftRiskScoringRegister, _derive_risk_level,
)

SCORE_DATE = dt.date(2024, 3, 1)
AS_OF = dt.date(2024, 4, 30)
ACCT = "IC-001"

def make_record(score=25.0, indicators=()):
    return TheftRiskScoringRecord(
        record_id="TRISK-00001", account_id=ACCT,
        score_date=SCORE_DATE, risk_score=score, indicators=indicators)

class TestDerive:
    def test_low(self):
        assert _derive_risk_level(0) == TheftRiskLevel.LOW
    def test_low_boundary(self):
        assert _derive_risk_level(29) == TheftRiskLevel.LOW
    def test_medium(self):
        assert _derive_risk_level(30) == TheftRiskLevel.MEDIUM
    def test_high(self):
        assert _derive_risk_level(60) == TheftRiskLevel.HIGH
    def test_critical(self):
        assert _derive_risk_level(80) == TheftRiskLevel.CRITICAL
    def test_critical_100(self):
        assert _derive_risk_level(100) == TheftRiskLevel.CRITICAL

class TestTheftRiskScoringRecord:
    def test_risk_level_low(self):
        assert make_record(15.0).risk_level == TheftRiskLevel.LOW
    def test_risk_level_medium(self):
        assert make_record(45.0).risk_level == TheftRiskLevel.MEDIUM
    def test_risk_level_high(self):
        assert make_record(65.0).risk_level == TheftRiskLevel.HIGH
    def test_risk_level_critical(self):
        assert make_record(85.0).risk_level == TheftRiskLevel.CRITICAL
    def test_requires_inspection_high(self):
        assert make_record(65.0).requires_inspection
    def test_requires_inspection_critical(self):
        assert make_record(85.0).requires_inspection
    def test_no_inspection_required_low(self):
        assert not make_record(10.0).requires_inspection
    def test_is_critical(self):
        assert make_record(90.0).is_critical
    def test_not_critical(self):
        assert not make_record(70.0).is_critical
    def test_risk_summary(self):
        r = make_record(85.0, (TheftRiskIndicator.CANNABIS_GROW_PROFILE,))
        s = r.risk_summary()
        assert "TRISK-00001" in s and "critical" in s
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.risk_score = 99.0

class TestTheftRiskScoringRegister:
    def setup_method(self):
        self.reg = TheftRiskScoringRegister()
    def test_score_account_stored(self):
        r = self.reg.score_account(ACCT, SCORE_DATE, 45.0)
        assert r.risk_score == 45.0
    def test_auto_id_increments(self):
        r1 = self.reg.score_account(ACCT, SCORE_DATE, 45.0)
        r2 = self.reg.score_account("IC-002", SCORE_DATE, 75.0)
        assert r1.record_id != r2.record_id
    def test_invalid_score_low_raises(self):
        with pytest.raises(ValueError):
            self.reg.score_account(ACCT, SCORE_DATE, -1.0)
    def test_invalid_score_high_raises(self):
        with pytest.raises(ValueError):
            self.reg.score_account(ACCT, SCORE_DATE, 101.0)
    def test_trigger_inspection(self):
        r = self.reg.score_account(ACCT, SCORE_DATE, 80.0)
        triggered = self.reg.trigger_inspection(r.record_id, dt.date(2024, 3, 5))
        assert triggered.inspection_triggered and triggered.inspection_triggered_date == dt.date(2024, 3, 5)
    def test_trigger_inspection_missing_raises(self):
        with pytest.raises(KeyError):
            self.reg.trigger_inspection("TRISK-99999", dt.date(2024, 3, 5))
    def test_current_score_for_latest(self):
        r1 = self.reg.score_account(ACCT, SCORE_DATE, 45.0)
        r2 = self.reg.score_account(ACCT, SCORE_DATE + dt.timedelta(30), 75.0)
        cur = self.reg.current_score_for(ACCT)
        assert cur.record_id == r2.record_id
    def test_current_score_for_none_when_unknown(self):
        assert self.reg.current_score_for("UNKNOWN") is None
    def test_all_scores_for_account(self):
        self.reg.score_account(ACCT, SCORE_DATE, 45.0)
        self.reg.score_account(ACCT, SCORE_DATE + dt.timedelta(30), 75.0)
        self.reg.score_account("IC-002", SCORE_DATE, 50.0)
        assert len(self.reg.all_scores_for(ACCT)) == 2
    def test_accounts_above_threshold(self):
        self.reg.score_account(ACCT, SCORE_DATE, 80.0)
        self.reg.score_account("IC-002", SCORE_DATE, 40.0)
        above = self.reg.accounts_above_threshold(60.0)
        assert len(above) == 1 and above[0].account_id == ACCT
    def test_critical_accounts(self):
        self.reg.score_account(ACCT, SCORE_DATE, 85.0)
        self.reg.score_account("IC-002", SCORE_DATE, 50.0)
        crit = self.reg.critical_accounts()
        assert len(crit) == 1
    def test_inspection_required(self):
        r1 = self.reg.score_account(ACCT, SCORE_DATE, 80.0)
        r2 = self.reg.score_account("IC-002", SCORE_DATE, 75.0)
        self.reg.trigger_inspection(r1.record_id, dt.date(2024, 3, 5))
        pending = self.reg.inspection_required()
        assert len(pending) == 1 and pending[0].account_id == "IC-002"
    def test_by_indicator(self):
        self.reg.score_account(ACCT, SCORE_DATE, 85.0,
            indicators=(TheftRiskIndicator.CANNABIS_GROW_PROFILE,))
        self.reg.score_account("IC-002", SCORE_DATE, 40.0,
            indicators=(TheftRiskIndicator.PAYMENT_PATTERN_ANOMALY,))
        by_ind = self.reg.by_indicator(TheftRiskIndicator.CANNABIS_GROW_PROFILE)
        assert len(by_ind) == 1
    def test_total_high_risk_accounts(self):
        self.reg.score_account(ACCT, SCORE_DATE, 80.0)
        self.reg.score_account(ACCT, SCORE_DATE + dt.timedelta(1), 90.0)  # same account
        self.reg.score_account("IC-002", SCORE_DATE, 45.0)
        assert self.reg.total_high_risk_accounts() == 1
    def test_risk_scoring_summary(self):
        self.reg.score_account(ACCT, SCORE_DATE, 85.0)
        s = self.reg.risk_scoring_summary(AS_OF)
        assert "1 records" in s
    def test_empty_summary(self):
        s = self.reg.risk_scoring_summary(AS_OF)
        assert "0 records" in s
