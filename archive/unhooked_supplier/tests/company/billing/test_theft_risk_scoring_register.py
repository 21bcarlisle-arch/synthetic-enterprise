"""Tests for company/billing/theft_risk_scoring_register.py (Sprint CLII)."""
import datetime as dt
import pytest

from company.billing.theft_risk_scoring_register import (
    TheftRiskScoringRegister,
    TheftRiskLevel,
    TheftRiskIndicator,
)

DATE = dt.date(2022, 6, 1)


def _reg():
    return TheftRiskScoringRegister()


def test_record_id_starts_with_trisk():
    reg = _reg()
    r = reg.score_account("C1", DATE, 45.0)
    assert r.record_id.startswith("TRISK-")


def test_account_id_stored():
    reg = _reg()
    r = reg.score_account("C1", DATE, 45.0)
    assert r.account_id == "C1"


def test_risk_score_stored():
    reg = _reg()
    r = reg.score_account("C1", DATE, 45.0)
    assert r.risk_score == 45.0


def test_risk_level_low_below_30():
    reg = _reg()
    r = reg.score_account("C1", DATE, 25.0)
    assert r.risk_level == TheftRiskLevel.LOW


def test_risk_level_medium_30_to_59():
    reg = _reg()
    r = reg.score_account("C1", DATE, 45.0)
    assert r.risk_level == TheftRiskLevel.MEDIUM


def test_risk_level_high_60_to_79():
    reg = _reg()
    r = reg.score_account("C1", DATE, 70.0)
    assert r.risk_level == TheftRiskLevel.HIGH


def test_risk_level_critical_at_80():
    reg = _reg()
    r = reg.score_account("C1", DATE, 80.0)
    assert r.risk_level == TheftRiskLevel.CRITICAL


def test_requires_inspection_high_and_critical():
    reg = _reg()
    r = reg.score_account("C1", DATE, 65.0)
    assert r.requires_inspection is True


def test_requires_inspection_false_medium():
    reg = _reg()
    r = reg.score_account("C1", DATE, 45.0)
    assert r.requires_inspection is False


def test_score_above_100_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.score_account("C1", DATE, 101.0)
