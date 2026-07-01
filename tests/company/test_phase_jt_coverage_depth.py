"""Phase JT: Coverage Depth Sprint XLII -- 30 tests."""
import datetime as dt
import pytest
from company.finance.credit_facility import DrawdownReason, CreditFacilityBook
from company.market.switch_governance import (
    ObjectionReason, ObjectionOutcome, ErroneousTransferStatus,
    CoolingOffCancellation, SwitchObjection, ErroneousTransfer,
    SwitchGovernanceBook,
)
from company.regulatory.licence_health import (
    LicenceCheckStatus, LicenceCheck, LicenceHealthReport, build_licence_health_report,
)


def _cf_book():
    book = CreditFacilityBook()
    book.register_facility("RCF01", "Barclays", 10_000_000.0,
        interest_rate_pct=5.5, commitment_fee_pct=0.5,
        maturity_date=dt.date(2025, 6, 30))
    return book


def test_cf_drawdown_id_dd0001():
    book = _cf_book()
    dd = book.drawdown("RCF01", 1_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WHOLESALE_SETTLEMENT)
    assert dd.drawdown_id == "DD-0001"


def test_cf_drawdown_ids_sequential():
    book = _cf_book()
    d1 = book.drawdown("RCF01", 1_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WORKING_CAPITAL)
    d2 = book.drawdown("RCF01", 2_000_000.0, dt.date(2022, 10, 2), DrawdownReason.BSC_CREDIT_COVER)
    assert d1.drawdown_id == "DD-0001"
    assert d2.drawdown_id == "DD-0002"


def test_cf_is_outstanding_false_after_repay():
    book = _cf_book()
    dd = book.drawdown("RCF01", 1_000_000.0, dt.date(2022, 10, 1), DrawdownReason.EMERGENCY)
    assert dd.is_outstanding
    book.repay(dd.drawdown_id, dt.date(2022, 11, 1))
    assert not dd.is_outstanding


def test_cf_multiple_drawdowns_accumulate():
    book = _cf_book()
    book.drawdown("RCF01", 2_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WORKING_CAPITAL)
    book.drawdown("RCF01", 3_000_000.0, dt.date(2022, 10, 5), DrawdownReason.BSC_CREDIT_COVER)
    assert book.outstanding_balance("RCF01") == pytest.approx(5_000_000.0)


def test_cf_repay_one_of_two_updates_balance():
    book = _cf_book()
    d1 = book.drawdown("RCF01", 2_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WORKING_CAPITAL)
    book.drawdown("RCF01", 3_000_000.0, dt.date(2022, 10, 5), DrawdownReason.BSC_CREDIT_COVER)
    book.repay(d1.drawdown_id, dt.date(2022, 11, 1))
    assert book.outstanding_balance("RCF01") == pytest.approx(3_000_000.0)


def test_cf_interest_stops_at_repay_date():
    book = _cf_book()
    dd = book.drawdown("RCF01", 1_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WHOLESALE_SETTLEMENT)
    book.repay(dd.drawdown_id, dt.date(2022, 10, 31))
    at_repay = book.total_interest_accrued_gbp(dt.date(2022, 10, 31))
    after = book.total_interest_accrued_gbp(dt.date(2022, 12, 31))
    assert after == pytest.approx(at_repay)


def test_cf_utilisation_pct_zero_no_drawdowns():
    book = _cf_book()
    assert book.utilisation_pct("RCF01") == pytest.approx(0.0)


def test_cf_interest_zero_same_day_drawdown():
    book = _cf_book()
    book.drawdown("RCF01", 1_000_000.0, dt.date(2022, 10, 1), DrawdownReason.EMERGENCY)
    assert book.total_interest_accrued_gbp(dt.date(2022, 10, 1)) == pytest.approx(0.0)


def test_cf_repay_unknown_id_raises():
    book = _cf_book()
    with pytest.raises(KeyError):
        book.repay("DD-9999", dt.date(2022, 11, 1))


def test_cf_drawdown_after_repay_within_limit():
    book = _cf_book()
    dd = book.drawdown("RCF01", 9_000_000.0, dt.date(2022, 10, 1), DrawdownReason.WORKING_CAPITAL)
    book.repay(dd.drawdown_id, dt.date(2022, 10, 15))
    book.drawdown("RCF01", 5_000_000.0, dt.date(2022, 10, 16), DrawdownReason.BSC_CREDIT_COVER)
    assert book.outstanding_balance("RCF01") == pytest.approx(5_000_000.0)


def test_sg_objection_id_obj0001():
    book = SwitchGovernanceBook()
    obj = book.raise_objection("MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 5), ObjectionReason.DEBT)
    assert obj.objection_id == "OBJ-0001"


def test_sg_objection_ids_sequential():
    book = SwitchGovernanceBook()
    o1 = book.raise_objection("MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 5), ObjectionReason.DEBT)
    o2 = book.raise_objection("MPAN002", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 5), ObjectionReason.IDENTITY_MISMATCH)
    assert o1.objection_id == "OBJ-0001"
    assert o2.objection_id == "OBJ-0002"


def test_sg_et_id_et0001():
    book = SwitchGovernanceBook()
    et = book.report_et("MPAN001", "LOSE", "GAIN", dt.date(2022, 10, 1), dt.date(2022, 10, 5))
    assert et.et_id == "ET-0001"


def test_sg_exact_14_day_cooling_off():
    c = CoolingOffCancellation("C001", "MPAN001", dt.date(2022, 10, 1), dt.date(2022, 10, 15))
    assert c.days_after_sale == 14
    assert c.within_cooling_off


def test_sg_day_15_not_cooling_off():
    c = CoolingOffCancellation("C001", "MPAN001", dt.date(2022, 10, 1), dt.date(2022, 10, 16))
    assert c.days_after_sale == 15
    assert not c.within_cooling_off


def test_sg_exact_15_day_in_objection_window():
    obj = SwitchObjection("OBJ-0001", "MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 16), ObjectionReason.CONTRACT_IN_TERM)
    assert obj.within_objection_window


def test_sg_day_16_outside_objection_window():
    obj = SwitchObjection("OBJ-0001", "MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 17), ObjectionReason.CUSTOMER_REQUEST)
    assert not obj.within_objection_window


def test_sg_et_closed_no_action_is_resolved():
    book = SwitchGovernanceBook()
    et = book.report_et("MPAN001", "L", "G", dt.date(2022, 10, 1), dt.date(2022, 10, 3))
    book.resolve_et(et.et_id, ErroneousTransferStatus.CLOSED_NO_ACTION, dt.date(2022, 10, 20))
    assert et.is_resolved


def test_sg_objection_reason_stored():
    book = SwitchGovernanceBook()
    obj = book.raise_objection("MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 5), ObjectionReason.IDENTITY_MISMATCH)
    assert obj.reason == ObjectionReason.IDENTITY_MISMATCH


def test_sg_annual_summary_objections_raised():
    book = SwitchGovernanceBook()
    book.raise_objection("MPAN001", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 5), ObjectionReason.DEBT)
    book.raise_objection("MPAN002", "S1", dt.date(2022, 10, 1), dt.date(2022, 10, 8), ObjectionReason.CONTRACT_IN_TERM)
    s = book.annual_summary(2022)
    assert s["objections_raised"] == 2


def _healthy():
    return build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )


def test_lh_pass_count_all_healthy():
    r = _healthy()
    assert r.pass_count == 6


def test_lh_watch_count_on_cash_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=9.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert r.watch_count >= 1


def test_lh_breach_is_not_going_concern():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=-1.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert not r.is_going_concern


def test_lh_get_returns_none_unknown():
    assert _healthy().get("nonexistent") is None


def test_lh_headroom_positive():
    check = LicenceCheck("n", "d", value=10.0, threshold=8.0, status=LicenceCheckStatus.PASS)
    assert check.headroom == pytest.approx(2.0)


def test_lh_headroom_negative():
    check = LicenceCheck("n", "d", value=5.0, threshold=8.0, status=LicenceCheckStatus.BREACH)
    assert check.headroom == pytest.approx(-3.0)


def test_lh_overall_watch_no_breach():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=9.0, bad_debt_ratio_pct=1.5, complaints_per_100=0.5,
    )
    assert r.breach_count == 0
    assert r.overall_status == LicenceCheckStatus.WATCH


def test_lh_bad_debt_exactly_5pct_is_watch():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=5.0, complaints_per_100=0.5,
    )
    assert r.get("bad_debt_ratio").status == LicenceCheckStatus.WATCH


def test_lh_complaints_exactly_1_is_pass():
    r = build_licence_health_report(
        as_of=dt.date(2022, 12, 31), active_customer_count=500,
        net_assets_gbp=2_000_000.0, treasury_gbp=800_000.0,
        weeks_cash_runway=20.0, bad_debt_ratio_pct=1.5, complaints_per_100=1.0,
    )
    assert r.get("complaints_per_100").status == LicenceCheckStatus.PASS


def test_lh_summary_as_of_iso():
    s = _healthy().summary()
    assert s["as_of"] == "2022-12-31"
