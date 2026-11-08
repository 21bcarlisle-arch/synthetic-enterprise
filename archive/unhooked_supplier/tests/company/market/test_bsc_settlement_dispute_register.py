import datetime as dt
import pytest
from company.market.bsc_settlement_dispute_register import (
    BSCSettlementDisputeRegister, DisputeGround, SQStatus,
)

SD = dt.date(2022, 1, 15)
RD = dt.date(2022, 2, 1)


def _reg():
    r = BSCSettlementDisputeRegister()
    r.raise_dispute(SD, "R1", DisputeGround.METER_READ_ERROR, 0.5, 5000.0, RD)
    return r


def test_dispute_id_prefix():
    reg = _reg()
    assert reg._records[0].dispute_id.startswith("SQ-")


def test_status_default_raised():
    reg = _reg()
    assert reg._records[0].status == SQStatus.RAISED


def test_zero_error_gwh_raises():
    reg = BSCSettlementDisputeRegister()
    with pytest.raises(ValueError):
        reg.raise_dispute(SD, "R1", DisputeGround.LLF_ERROR, 0.0, 1000.0, RD)


def test_start_investigation_changes_status():
    reg = _reg()
    did = reg._records[0].dispute_id
    updated = reg.start_investigation(did, RD)
    assert updated.status == SQStatus.UNDER_INVESTIGATION


def test_uphold_sets_recovery():
    reg = _reg()
    did = reg._records[0].dispute_id
    reg.start_investigation(did, RD)
    upheld = reg.uphold(did, dt.date(2022, 3, 1), 4500.0)
    assert upheld.status == SQStatus.UPHELD
    assert upheld.recovery_amount_gbp == 4500.0


def test_reject_sets_rejected():
    reg = _reg()
    did = reg._records[0].dispute_id
    reg.start_investigation(did, RD)
    updated = reg.reject(did, dt.date(2022, 3, 1))
    assert updated.status == SQStatus.REJECTED


def test_appeal_from_rejected():
    reg = _reg()
    did = reg._records[0].dispute_id
    reg.start_investigation(did, RD)
    reg.reject(did, dt.date(2022, 3, 1))
    updated = reg.appeal(did, dt.date(2022, 3, 15))
    assert updated.status == SQStatus.APPEALED


def test_total_financial_impact_open_only():
    reg = _reg()
    assert reg.total_financial_impact_gbp == 5000.0


def test_total_recovered_sums_upheld():
    reg = _reg()
    did = reg._records[0].dispute_id
    reg.start_investigation(did, RD)
    reg.uphold(did, dt.date(2022, 3, 1), 4500.0)
    assert reg.total_recovered_gbp == 4500.0


def test_uphold_rate_none_empty():
    reg = BSCSettlementDisputeRegister()
    assert reg.uphold_rate_pct() is None
