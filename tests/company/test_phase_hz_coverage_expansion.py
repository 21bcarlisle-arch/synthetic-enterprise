"""Phase HZ: coverage expansion for revenue_protection_register, interruptible_supply_register, otc_margin_book."""
import datetime as dt
import pytest

from company.billing.revenue_protection_register import (
    RevenueProtectionRegister, RPCaseType, RPCaseStatus
)

def _case(reg, cid="RP001", account="C1", ctype=RPCaseType.METER_TAMPERING, kwh=5000.0, gbp=800.0):
    return reg.open_case(cid, account, ctype, dt.date(2023, 3, 1), kwh, gbp)

class TestRevenueProtectionRegister:
    def test_open_case_suspected_status(self):
        reg = RevenueProtectionRegister()
        case = _case(reg)
        assert case.status == RPCaseStatus.SUSPECTED and case.is_active

    def test_confirm_sets_status(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        confirmed = reg.confirm("RP001", dt.date(2023, 3, 10))
        assert confirmed.status == RPCaseStatus.CONFIRMED

    def test_raise_estimated_bill(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        reg.confirm("RP001")
        billed = reg.raise_estimated_bill("RP001")
        assert billed.status == RPCaseStatus.ESTIMATED_BILL_RAISED and billed.is_recoverable

    def test_recover_closes_case(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        assert not reg.recover("RP001").is_active

    def test_write_off_closes_case(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001")
        assert not reg.write_off("RP001").is_active

    def test_active_cases_excludes_closed(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001"); _case(reg, "RP002")
        reg.recover("RP001")
        assert len(reg.active_cases) == 1

    def test_total_estimated_loss_gbp(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001", gbp=800.0); _case(reg, "RP002", gbp=500.0)
        reg.recover("RP001")
        assert reg.total_estimated_loss_gbp == pytest.approx(500.0)

    def test_cases_by_type(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001", ctype=RPCaseType.METER_TAMPERING)
        _case(reg, "RP002", ctype=RPCaseType.ILLEGAL_RECONNECTION)
        _case(reg, "RP003", ctype=RPCaseType.METER_TAMPERING)
        bd = reg.cases_by_type()
        assert bd["meter_tampering"] == 2 and bd["illegal_reconnection"] == 1

    def test_confirmed_cases_filter(self):
        reg = RevenueProtectionRegister()
        _case(reg, "RP001"); reg.confirm("RP001")
        _case(reg, "RP002")
        assert len(reg.confirmed_cases) == 1

    def test_revenue_protection_summary_keys(self):
        reg = RevenueProtectionRegister()
        _case(reg)
        s = reg.revenue_protection_summary()
        assert "Revenue Protection" in s and "Active" in s


from company.market.interruptible_supply_register import (
    InterruptibleSupplyRegister, InterruptionReason
)

class TestInterruptibleSupplyRegister:
    def test_register_creates_contract(self):
        reg = InterruptibleSupplyRegister()
        c = reg.register("I1", dt.date(2023, 1, 1), 500_000)
        assert c.account_id == "I1" and c.discount_pct == 15.0

    def test_saving_vs_firm(self):
        reg = InterruptibleSupplyRegister()
        c = reg.register("I1", dt.date(2023, 1, 1), 100_000, discount_pct=10.0)
        assert c.saving_vs_firm_gbp_pa == pytest.approx(400.0)

    def test_record_interruption_notice_compliant(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        event = reg.record_interruption(dt.date(2023, 2, 1), "I1", InterruptionReason.COLD_WEATHER, 5000.0, 4.0)
        assert event.notice_compliant

    def test_notice_violation_under_2h(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        event = reg.record_interruption(dt.date(2023, 2, 1), "I1", InterruptionReason.COLD_WEATHER, 5000.0, 1.0)
        assert not event.notice_compliant and len(reg.notice_violations) == 1

    def test_events_for_account(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        reg.record_interruption(dt.date(2023, 2, 1), "I1", InterruptionReason.COLD_WEATHER, 5000.0, 3.0)
        reg.record_interruption(dt.date(2023, 3, 1), "I1", InterruptionReason.NETWORK_CONSTRAINT, 2000.0, 5.0)
        assert len(reg.events_for_account("I1")) == 2

    def test_annual_curtailment_days(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        for day in range(1, 6):
            reg.record_interruption(dt.date(2023, 2, day), "I1", InterruptionReason.COLD_WEATHER, 1000.0, 4.0)
        assert reg.annual_curtailment_days("I1", 2023) == 5

    def test_over_cap_accounts(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        for i in range(31):
            reg.record_interruption(dt.date(2023, 1, 1) + dt.timedelta(i), "I1", InterruptionReason.NGT_INSTRUCTION, 1000.0, 3.0)
        assert "I1" in reg.over_cap_accounts(2023)

    def test_total_portfolio_annual_kwh(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 300_000)
        reg.register("I2", dt.date(2023, 1, 1), 200_000)
        assert reg.total_portfolio_annual_kwh == pytest.approx(500_000)

    def test_interruptible_accounts(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 300_000)
        reg.register("I2", dt.date(2023, 1, 1), 200_000)
        assert set(reg.interruptible_accounts) == {"I1", "I2"}

    def test_interruptible_summary_keys(self):
        reg = InterruptibleSupplyRegister()
        reg.register("I1", dt.date(2023, 1, 1), 500_000)
        s = reg.interruptible_summary()
        assert "Interruptible Gas" in s and "Notice violations" in s


from company.trading.otc_margin_book import (
    OTCMarginBook, MarginCallDirection, MarginCallStatus
)

def _vm(book, cid="VM001", cdate=None, cp="Equinor", notional=50_000,
        loss=25_000, direction=MarginCallDirection.CALL, status=MarginCallStatus.PENDING):
    return book.record_call(cid, cdate or dt.date(2022, 3, 1), cp, notional, loss, direction, status)

class TestOTCMarginBook:
    def test_record_call_pending(self):
        book = OTCMarginBook()
        call = _vm(book)
        assert call.status == MarginCallStatus.PENDING and call.is_call_on_company

    def test_cash_impact_negative_for_outgoing_call(self):
        book = OTCMarginBook()
        call = _vm(book, direction=MarginCallDirection.CALL, loss=25_000)
        assert call.cash_impact_gbp == pytest.approx(-25_000)

    def test_cash_impact_positive_for_receipt(self):
        book = OTCMarginBook()
        call = _vm(book, direction=MarginCallDirection.RETURN, loss=15_000)
        assert call.cash_impact_gbp == pytest.approx(15_000)

    def test_settle_call_changes_status(self):
        book = OTCMarginBook()
        _vm(book, "VM001")
        settled = book.settle_call("VM001", dt.date(2022, 3, 2))
        assert settled.status == MarginCallStatus.MET and settled.settled_date == dt.date(2022, 3, 2)

    def test_total_cash_impact_settled_only(self):
        book = OTCMarginBook()
        _vm(book, "VM001", loss=25_000, direction=MarginCallDirection.CALL)
        _vm(book, "VM002", loss=15_000, direction=MarginCallDirection.RETURN)
        book.settle_call("VM001", dt.date(2022, 3, 2))
        book.settle_call("VM002", dt.date(2022, 3, 2))
        assert book.total_cash_impact_gbp == pytest.approx(-10_000)

    def test_pending_calls_filtered(self):
        book = OTCMarginBook()
        _vm(book, "VM001"); _vm(book, "VM002")
        book.settle_call("VM001", dt.date(2022, 3, 2))
        assert len(book.pending_calls) == 1

    def test_total_pending_outflow(self):
        book = OTCMarginBook()
        _vm(book, "VM001", loss=25_000, direction=MarginCallDirection.CALL)
        _vm(book, "VM002", loss=10_000, direction=MarginCallDirection.RETURN)
        assert book.total_pending_outflow_gbp == pytest.approx(25_000)

    def test_calls_by_counterparty(self):
        book = OTCMarginBook()
        _vm(book, "VM001", cp="Equinor", loss=20_000)
        _vm(book, "VM002", cp="Equinor", loss=5_000)
        book.settle_call("VM001", dt.date(2022, 3, 2))
        book.settle_call("VM002", dt.date(2022, 3, 2))
        assert book.calls_by_counterparty["Equinor"] == pytest.approx(-25_000)

    def test_net_cash_for_year(self):
        book = OTCMarginBook()
        _vm(book, "VM001", cdate=dt.date(2022, 3, 1), loss=10_000)
        book.settle_call("VM001", dt.date(2022, 3, 2))
        assert book.net_cash_for_year(2022) == pytest.approx(-10_000)

    def test_margin_book_summary_keys(self):
        book = OTCMarginBook()
        _vm(book)
        s = book.margin_book_summary()
        assert "OTC Margin Book" in s and "Pending" in s
