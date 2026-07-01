"""Tests for company/billing/account_adjustment_register.py (Sprint CLI)."""
import datetime as dt
import pytest

from company.billing.account_adjustment_register import (
    AccountAdjustmentRecord,
    AdjustmentType,
    AdjustmentDirection,
    AdjustmentStatus,
    approval_tier_required,
)

try:
    from company.billing.account_adjustment_register import AccountAdjustmentRegister
    _HAS_REGISTER = True
except ImportError:
    _HAS_REGISTER = False

DATE = dt.date(2022, 7, 1)


def test_approval_tier_auto_at_25():
    assert approval_tier_required(25.0) == "auto"


def test_approval_tier_team_leader_at_50():
    assert approval_tier_required(50.0) == "team_leader"


def test_approval_tier_management_at_200():
    assert approval_tier_required(200.0) == "management"


def test_approval_tier_director_above_500():
    assert approval_tier_required(501.0) == "director"


def test_adjustment_direction_enum_has_credit():
    assert AdjustmentDirection.CREDIT.value == "credit"


def test_adjustment_direction_enum_has_debit():
    assert AdjustmentDirection.DEBIT.value == "debit"


def test_adjustment_type_enum_has_goodwill():
    assert AdjustmentType.GOODWILL.value == "goodwill"


def test_adjustment_status_has_approved():
    assert AdjustmentStatus.APPROVED.value == "approved"


def test_adjustment_status_has_applied():
    assert AdjustmentStatus.APPLIED.value == "applied"


def test_auto_approve_boundary_26_is_team_leader():
    assert approval_tier_required(26.0) == "team_leader"
