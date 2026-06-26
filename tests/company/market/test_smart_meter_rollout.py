import pytest
from company.market.smart_meter_rollout import (
    SmartMeterRolloutBook, MeterPortfolioSnapshot, MeterGeneration,
    RolloutStatus, _ANNUAL_TARGETS
)


def _snap(year, trad, s1, s2):
    return MeterPortfolioSnapshot(year=year, traditional_count=trad, smets1_count=s1, smets2_count=s2)


def test_smart_count():
    s = _snap(2022, 20, 30, 50)
    assert s.smart_count == 80
    assert s.total_meters == 100


def test_smart_penetration_pct():
    s = _snap(2022, 20, 30, 50)
    assert abs(s.smart_penetration_pct - 80.0) < 0.01


def test_remote_reads_pct():
    s = _snap(2022, 0, 100, 0)
    assert abs(s.remote_reads_pct - 75.0) < 0.01


def test_manual_read_cost():
    s = _snap(2022, 10, 0, 0)
    assert abs(s.annual_manual_read_cost_gbp - 10 * 15.0) < 0.01


def test_zero_meters():
    s = _snap(2022, 0, 0, 0)
    assert s.smart_penetration_pct == 0.0
    assert s.remote_reads_pct == 0.0


def test_on_track():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2022, 40, 30, 30))
    assert book.rollout_status(2022) == RolloutStatus.ON_TRACK


def test_behind():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2022, 70, 20, 10))
    assert book.rollout_status(2022) in (RolloutStatus.BEHIND, RolloutStatus.SIGNIFICANTLY_BEHIND)


def test_significantly_behind():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2022, 95, 3, 2))
    assert book.rollout_status(2022) == RolloutStatus.SIGNIFICANTLY_BEHIND


def test_annual_progress_keys():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2022, 40, 30, 30))
    ap = book.annual_progress()
    assert len(ap) == 1
    for k in ("year", "smart_penetration_pct", "target_pct", "status",
               "remote_reads_pct", "annual_manual_read_cost_gbp"):
        assert k in ap[0]


def test_annual_progress_sorted():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2023, 20, 40, 40))
    book.record_snapshot(_snap(2021, 50, 30, 20))
    ap = book.annual_progress()
    assert ap[0]["year"] == 2021
    assert ap[1]["year"] == 2023


def test_rollout_summary_keys():
    book = SmartMeterRolloutBook()
    book.record_snapshot(_snap(2024, 20, 30, 50))
    s = book.rollout_summary()
    for k in ("years_tracked", "latest_year", "latest_penetration_pct",
               "latest_status", "total_meters", "smets2_share_pct"):
        assert k in s


def test_rollout_summary_empty():
    book = SmartMeterRolloutBook()
    s = book.rollout_summary()
    assert s["years_tracked"] == 0
