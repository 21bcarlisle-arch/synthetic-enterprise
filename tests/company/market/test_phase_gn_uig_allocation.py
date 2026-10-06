import datetime as dt

import pytest

from company.market.uig_allocation_register import (
    _HIGH_UIG_PCT,
    UIGAllocationRegister,
    UIGMonthlyRecord,
)

#: A TEST FIXTURE that exercises the banding; the module's own threshold is unsourced and None.
T = 2.0

MONTH = dt.date(2024, 1, 1)

def make_record(throughput=1000.0, uig=15.0):
    return UIGMonthlyRecord(
        record_id="UIG-00001", settlement_month=MONTH,
        total_throughput_mwh=throughput, uig_allocated_mwh=uig)

class TestUIGMonthlyRecord:
    def test_uig_rate_pct(self):
        r = make_record(1000.0, 15.0)
        assert abs(r.uig_rate_pct - 1.5) < 1e-9
    def test_uig_rate_pct_zero_throughput(self):
        r = make_record(0.0, 0.0)
        assert r.uig_rate_pct == 0.0
    def test_is_high_uig_at_threshold(self):
        r = make_record(1000.0, 20.0)  # 2.0% exactly
        assert r.exceeds(T)
    def test_is_high_uig_above_threshold(self):
        r = make_record(1000.0, 25.0)  # 2.5%
        assert r.exceeds(T)
    def test_is_not_high_uig_below_threshold(self):
        r = make_record(1000.0, 15.0)  # 1.5%
        assert not r.exceeds(T)
    def test_uig_summary_string(self):
        s = make_record().uig_summary()
        assert "UIG-00001" in s and "MWh" in s
    def test_uig_summary_carries_no_high_flag_without_a_sourced_threshold(self):
        r = make_record(1000.0, 38.1)  # 3.81%, the top of the published range
        assert "[HIGH]" not in r.uig_summary()
        assert r.is_high_uig is None
    def test_frozen(self):
        r = make_record()
        with pytest.raises((AttributeError, TypeError)):
            r.uig_allocated_mwh = 100.0

class TestUIGAllocationRegister:
    def setup_method(self):
        self.reg = UIGAllocationRegister()
    def test_record_allocation_stored(self):
        r = self.reg.record_allocation(MONTH, 1000.0, 15.0)
        assert r.total_throughput_mwh == 1000.0
    def test_settlement_month_normalised_to_first(self):
        r = self.reg.record_allocation(dt.date(2024, 3, 15), 1000.0, 15.0)
        assert r.settlement_month == dt.date(2024, 3, 1)
    def test_auto_id_increments(self):
        r1 = self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 15.0)
        r2 = self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 10.0)
        assert r1.record_id != r2.record_id
    def test_negative_throughput_raises(self):
        with pytest.raises(ValueError):
            self.reg.record_allocation(MONTH, -1.0, 5.0)
    def test_for_month(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 15.0)
        self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 10.0)
        r = self.reg.for_month(2024, 1)
        assert r is not None and r.total_throughput_mwh == 1000.0
    def test_for_month_none_when_missing(self):
        assert self.reg.for_month(2024, 12) is None
    def test_high_uig_periods(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 25.0)  # 2.5% high
        self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 15.0)  # 1.5% normal
        assert len(self.reg.high_uig_periods(threshold_pct=T)) == 1
    def test_total_uig_allocated_mwh(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 15.0)
        self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 10.0)
        assert abs(self.reg.total_uig_allocated_mwh() - 25.0) < 1e-9
    def test_total_throughput_mwh(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 15.0)
        self.reg.record_allocation(dt.date(2024, 2, 1), 800.0, 10.0)
        assert abs(self.reg.total_throughput_mwh() - 1800.0) < 1e-9
    def test_average_uig_rate_pct(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 15.0)
        self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 25.0)
        avg = self.reg.average_uig_rate_pct()
        assert abs(avg - 2.0) < 1e-9
    def test_average_uig_rate_none_when_empty(self):
        assert self.reg.average_uig_rate_pct() is None
    def test_rolling_3m_avg(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 10.0)
        self.reg.record_allocation(dt.date(2024, 2, 1), 1000.0, 20.0)
        self.reg.record_allocation(dt.date(2024, 3, 1), 1000.0, 30.0)
        avg = self.reg.rolling_3m_avg_rate_pct(2024, 3)
        assert abs(avg - 2.0) < 1e-9
    def test_rolling_3m_none_when_no_records(self):
        assert self.reg.rolling_3m_avg_rate_pct(2024, 1) is None
    def test_most_recent(self):
        self.reg.record_allocation(dt.date(2024, 1, 1), 1000.0, 10.0)
        self.reg.record_allocation(dt.date(2024, 3, 1), 1000.0, 20.0)
        r = self.reg.most_recent()
        assert r.settlement_month == dt.date(2024, 3, 1)
    def test_most_recent_none_when_empty(self):
        assert self.reg.most_recent() is None
    def test_uig_register_summary(self):
        self.reg.record_allocation(MONTH, 1000.0, 15.0)
        s = self.reg.uig_register_summary()
        assert "1 months" in s
    def test_empty_summary(self):
        s = self.reg.uig_register_summary()
        assert "0 months" in s


def test_the_unsourced_uig_threshold_is_none_and_high_is_cannot_tell():
    """Corrected 2026-10-06: the 2.0% "investigation trigger" had no source and sat below every
    published final UIG (2.19-3.81%, AUG Statement 2024-25 p.27). The partition: with a supplied
    threshold both sides are reachable; with none, the answer is None, not an empty list."""
    assert _HIGH_UIG_PCT is None
    reg = UIGAllocationRegister()
    reg.record_allocation(dt.date(2021, 10, 1), 1000.0, 25.0)   # 2.50%
    reg.record_allocation(dt.date(2017, 10, 1), 1000.0, 38.1)   # 3.81%
    assert reg.high_uig_periods() is None
    assert "n/a high-UIG periods" in reg.uig_register_summary()
    split = reg.high_uig_periods(threshold_pct=3.0)
    assert [r.settlement_month.year for r in split] == [2017]

