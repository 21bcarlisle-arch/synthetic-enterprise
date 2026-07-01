"""Phase CJ: Initial Margin Register tests."""
import pytest
from datetime import date
from company.trading.initial_margin_register import (
    InitialMarginRegister, InitialMarginRecord,
    MarginAccountType, IMStatus
)

_D1 = date(2022, 1, 15)
_D2 = date(2022, 12, 31)


def _reg() -> InitialMarginRegister:
    r = InitialMarginRegister()
    r.post_margin("IM001", "T001", "Shell Energy", MarginAccountType.BILATERAL_OTC, 1000, 50_000, _D1, _D2)
    return r


# 1. post_margin creates record with POSTED status
def test_post_margin_status():
    r = _reg()
    assert r.active_records[0].status == IMStatus.POSTED


# 2. total_locked_gbp reflects posted amount
def test_total_locked_initial():
    r = _reg()
    assert r.total_locked_gbp == 50_000


# 3. additional call increases total_held
def test_additional_call_increases_total():
    r = _reg()
    r.issue_additional_call("IM001", 20_000)
    rec = r.active_records[0]
    assert rec.total_held_gbp == 70_000


# 4. additional call sets status CALLED
def test_additional_call_status():
    r = _reg()
    r.issue_additional_call("IM001", 5_000)
    assert r.active_records[0].status == IMStatus.CALLED


# 5. total_additional_calls_gbp tracks cumulative extra margin
def test_total_additional_calls():
    r = _reg()
    r.issue_additional_call("IM001", 10_000)
    r.issue_additional_call("IM001", 5_000)
    assert r.total_additional_calls_gbp == 15_000


# 6. return_margin removes from active_records
def test_return_margin_deactivates():
    r = _reg()
    r.return_margin("IM001", date(2022, 12, 31))
    assert len(r.active_records) == 0


# 7. total_locked_gbp = 0 after all returned
def test_locked_zero_after_return():
    r = _reg()
    r.return_margin("IM001", date(2022, 12, 31))
    assert r.total_locked_gbp == 0


# 8. margin_rate_pct_of_notional calculation
def test_margin_rate_pct():
    r = _reg()
    rec = r.active_records[0]
    # notional_mwh=1000 × £100/MWh = £100,000; IM=£50,000 → 50%
    assert abs(rec.margin_rate_pct_of_notional - 50.0) < 0.01


# 9. records_by_counterparty groups correctly
def test_by_counterparty():
    r = _reg()
    r.post_margin("IM002", "T002", "Shell Energy", MarginAccountType.BILATERAL_OTC, 500, 25_000, _D1, _D2)
    r.post_margin("IM003", "T003", "ICE Clear", MarginAccountType.EXCHANGE_CLEARED, 800, 40_000, _D1, _D2)
    by_cpty = r.records_by_counterparty()
    assert abs(by_cpty["Shell Energy"] - 75_000) < 0.01
    assert abs(by_cpty["ICE Clear"] - 40_000) < 0.01


# 10. is_active false for returned record
def test_is_active_after_return():
    r = _reg()
    r.return_margin("IM001", _D2)
    rec = [x for x in r._records if x.margin_id == "IM001"][0]
    assert not rec.is_active


# 11. multiple additional calls stack
def test_multiple_calls_stack():
    r = _reg()
    r.issue_additional_call("IM001", 10_000)
    r.issue_additional_call("IM001", 8_000)
    assert r.active_records[0].additional_call_gbp == 18_000


# 12. im_summary contains key fields
def test_im_summary():
    r = _reg()
    r.issue_additional_call("IM001", 5_000)
    summary = r.im_summary()
    assert "Initial Margin" in summary
    assert "55,000" in summary   # total locked
    assert "5,000" in summary    # additional calls


# --- Phase MF depth tests ---

def test_margin_id_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T-001", "BP", MarginAccountType.BILATERAL_OTC, 500, 25000, _D1, _D2)
    assert rec.margin_id == "IM-MF"


def test_trade_id_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "TRADE-MF", "BP", MarginAccountType.BILATERAL_OTC, 500, 25000, _D1, _D2)
    assert rec.trade_id == "TRADE-MF"


def test_counterparty_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "Equinor", MarginAccountType.EXCHANGE_CLEARED, 500, 25000, _D1, _D2)
    assert rec.counterparty == "Equinor"


def test_account_type_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "ICE", MarginAccountType.EXCHANGE_CLEARED, 500, 25000, _D1, _D2)
    assert rec.account_type == MarginAccountType.EXCHANGE_CLEARED


def test_notional_mwh_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 2000, 25000, _D1, _D2)
    assert rec.notional_mwh == pytest.approx(2000.0)


def test_margin_posted_gbp_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 500, 40000, _D1, _D2)
    assert rec.margin_posted_gbp == pytest.approx(40000.0)


def test_posted_date_stored():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 500, 25000, _D1, _D2)
    assert rec.posted_date == _D1


def test_actual_return_date_none_default():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 500, 25000, _D1, _D2)
    assert rec.actual_return_date is None


def test_post_margin_returns_initial_margin_record():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 500, 25000, _D1, _D2)
    assert isinstance(rec, InitialMarginRecord)


def test_total_held_gbp_equals_posted_plus_additional():
    reg = InitialMarginRegister()
    rec = reg.post_margin("IM-MF", "T001", "BP", MarginAccountType.BILATERAL_OTC, 500, 30000, _D1, _D2)
    reg.issue_additional_call("IM-MF", 5000)
    updated = [r for r in reg._records if r.margin_id == "IM-MF"][0]
    assert updated.total_held_gbp == pytest.approx(35000.0)
