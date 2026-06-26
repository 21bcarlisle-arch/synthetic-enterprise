"""Phase 88: Direct Debit mandate tests."""

import pytest

from company.billing.direct_debit import (
    DDMandate,
    set_mandate,
    get_mandate,
    cancel_mandate,
    is_dd_customer,
    list_mandates,
)


def test_set_mandate_returns_dataclass(tmp_path):
    db = tmp_path / "dd.db"
    m = set_mandate("C1", "20-00-00", "12345678", 1, db)
    assert isinstance(m, DDMandate)
    assert m.account_id == "C1"
    assert m.sort_code == "20-00-00"
    assert m.active is True


def test_get_mandate_returns_none_when_absent(tmp_path):
    db = tmp_path / "dd.db"
    result = get_mandate("C1", db)
    assert result is None


def test_get_mandate_returns_active_mandate(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "12345678", 15, db)
    m = get_mandate("C1", db)
    assert m is not None
    assert m.payment_day == 15


def test_cancel_mandate_makes_inactive(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "12345678", 1, db)
    result = cancel_mandate("C1", db)
    assert result is True
    assert get_mandate("C1", db) is None


def test_cancel_mandate_returns_false_if_none(tmp_path):
    db = tmp_path / "dd.db"
    result = cancel_mandate("C1", db)
    assert result is False


def test_is_dd_customer_true_when_active(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "12345678", 1, db)
    assert is_dd_customer("C1", db) is True


def test_is_dd_customer_false_when_absent(tmp_path):
    db = tmp_path / "dd.db"
    assert is_dd_customer("C1", db) is False


def test_is_dd_customer_false_after_cancel(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "12345678", 1, db)
    cancel_mandate("C1", db)
    assert is_dd_customer("C1", db) is False


def test_list_mandates_returns_all_active(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "11111111", 1, db)
    set_mandate("C2", "30-00-00", "22222222", 15, db)
    mandates = list_mandates(db)
    assert len(mandates) == 2
    assert all(m.active for m in mandates)


def test_list_mandates_excludes_cancelled(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "11111111", 1, db)
    set_mandate("C2", "30-00-00", "22222222", 15, db)
    cancel_mandate("C1", db)
    mandates = list_mandates(db)
    assert len(mandates) == 1
    assert mandates[0].account_id == "C2"


def test_set_mandate_invalid_payment_day_raises(tmp_path):
    db = tmp_path / "dd.db"
    with pytest.raises(ValueError):
        set_mandate("C1", "20-00-00", "12345678", 0, db)
    with pytest.raises(ValueError):
        set_mandate("C1", "20-00-00", "12345678", 29, db)


def test_set_mandate_replaces_existing(tmp_path):
    db = tmp_path / "dd.db"
    set_mandate("C1", "20-00-00", "11111111", 1, db)
    set_mandate("C1", "30-00-00", "99999999", 20, db)
    m = get_mandate("C1", db)
    assert m.sort_code == "30-00-00"
    assert m.payment_day == 20
