import datetime as dt
import pytest
from company.billing.payment_method_register import (
    PaymentMethod, PaymentMethodSource, PaymentMethodRecord, PaymentMethodRegister,
)


D1 = dt.date(2022, 1, 1)
D2 = dt.date(2023, 6, 15)


def make_record(
    account_id="A1",
    method=PaymentMethod.DIRECT_DEBIT,
    effective_date=D1,
    source=PaymentMethodSource.VOLUNTARY,
    notes="",
):
    return PaymentMethodRecord(
        account_id=account_id,
        method=method,
        effective_date=effective_date,
        source=source,
        notes=notes,
    )


class TestPaymentMethodRecord:
    def test_is_direct_debit_true(self):
        r = make_record(method=PaymentMethod.DIRECT_DEBIT)
        assert r.is_direct_debit is True

    def test_is_direct_debit_false(self):
        r = make_record(method=PaymentMethod.PREPAYMENT_METER)
        assert r.is_direct_debit is False

    def test_is_prepayment_true(self):
        r = make_record(method=PaymentMethod.PREPAYMENT_METER)
        assert r.is_prepayment is True

    def test_is_prepayment_false(self):
        r = make_record(method=PaymentMethod.DIRECT_DEBIT)
        assert r.is_prepayment is False

    def test_is_debt_mandated_true(self):
        r = make_record(source=PaymentMethodSource.DEBT_MANDATED)
        assert r.is_debt_mandated is True

    def test_is_debt_mandated_false(self):
        r = make_record(source=PaymentMethodSource.VOLUNTARY)
        assert r.is_debt_mandated is False

    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.method = PaymentMethod.CASH  # type: ignore[misc]


class TestPaymentMethodRegister:
    def test_set_and_current(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        cur = reg.current("A1")
        assert cur is not None
        assert cur.method == PaymentMethod.DIRECT_DEBIT

    def test_current_none_unknown_account(self):
        reg = PaymentMethodRegister()
        assert reg.current("UNKNOWN") is None

    def test_current_returns_latest(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A1", PaymentMethod.PREPAYMENT_METER, D2)
        assert reg.current("A1").method == PaymentMethod.PREPAYMENT_METER

    def test_history_for(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A1", PaymentMethod.PREPAYMENT_METER, D2)
        hist = reg.history_for("A1")
        assert len(hist) == 2
        assert hist[0].method == PaymentMethod.DIRECT_DEBIT

    def test_history_for_empty(self):
        reg = PaymentMethodRegister()
        assert reg.history_for("X") == []

    def test_accounts_by_method(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A2", PaymentMethod.PREPAYMENT_METER, D1)
        reg.set_method("A3", PaymentMethod.DIRECT_DEBIT, D1)
        dd = reg.accounts_by_method(PaymentMethod.DIRECT_DEBIT)
        assert set(dd) == {"A1", "A3"}

    def test_dd_accounts(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A2", PaymentMethod.CASH, D1)
        assert reg.dd_accounts() == ["A1"]

    def test_ppm_accounts(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.PREPAYMENT_METER, D1)
        reg.set_method("A2", PaymentMethod.DIRECT_DEBIT, D1)
        assert reg.ppm_accounts() == ["A1"]

    def test_debt_mandated_ppm(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.PREPAYMENT_METER, D1,
                       source=PaymentMethodSource.DEBT_MANDATED)
        reg.set_method("A2", PaymentMethod.PREPAYMENT_METER, D1,
                       source=PaymentMethodSource.VOLUNTARY)
        reg.set_method("A3", PaymentMethod.DIRECT_DEBIT, D1,
                       source=PaymentMethodSource.DEBT_MANDATED)
        assert reg.debt_mandated_ppm() == ["A1"]

    def test_method_breakdown(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A2", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A3", PaymentMethod.PREPAYMENT_METER, D1)
        bd = reg.method_breakdown()
        assert bd["direct_debit"] == 2
        assert bd["prepayment_meter"] == 1

    def test_method_change_updates_breakdown(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A1", PaymentMethod.PREPAYMENT_METER, D2)
        bd = reg.method_breakdown()
        assert bd.get("direct_debit", 0) == 0
        assert bd["prepayment_meter"] == 1

    def test_payment_method_summary_keys(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1)
        reg.set_method("A2", PaymentMethod.PREPAYMENT_METER, D1,
                       source=PaymentMethodSource.DEBT_MANDATED)
        s = reg.payment_method_summary()
        assert s["total_accounts"] == 2
        assert s["dd_count"] == 1
        assert s["ppm_count"] == 1
        assert s["debt_mandated_ppm_count"] == 1

    def test_summary_bacs_count(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.BACS_TRANSFER, D1)
        s = reg.payment_method_summary()
        assert s["bacs_count"] == 1

    def test_vulnerability_protection_source(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.DIRECT_DEBIT, D1,
                       source=PaymentMethodSource.VULNERABILITY_PROTECTION)
        cur = reg.current("A1")
        assert cur.source == PaymentMethodSource.VULNERABILITY_PROTECTION
        assert not cur.is_debt_mandated

    def test_notes_stored(self):
        reg = PaymentMethodRegister()
        reg.set_method("A1", PaymentMethod.CASH, D1, notes="counter payment")
        assert reg.current("A1").notes == "counter payment"
