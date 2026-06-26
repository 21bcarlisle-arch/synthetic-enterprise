import datetime as dt
import pytest
from company.crm.nps_tracker import classify_nps, NPSResponse, NPSTracker


def test_classify_promoter():
    assert classify_nps(9) == 'promoter'
    assert classify_nps(10) == 'promoter'


def test_classify_passive():
    assert classify_nps(7) == 'passive'
    assert classify_nps(8) == 'passive'


def test_classify_detractor():
    assert classify_nps(6) == 'detractor'
    assert classify_nps(0) == 'detractor'


def _tracker():
    t = NPSTracker()
    t.record('C001', 9, dt.date(2022, 1, 10), 'residential')
    t.record('C002', 4, dt.date(2022, 1, 15), 'residential')
    t.record('C003', 10, dt.date(2022, 2, 5), 'sme')
    t.record('C004', 7, dt.date(2022, 2, 20), 'residential')
    return t


def test_invalid_score_raises():
    t = NPSTracker()
    with pytest.raises(ValueError):
        t.record('C001', 11, dt.date(2022, 1, 1), 'residential')


def test_nps_in_period():
    t = _tracker()
    nps = t.nps_in_period(dt.date(2022, 1, 1), dt.date(2022, 1, 31))
    assert nps == pytest.approx(0.0)


def test_nps_segment_filter():
    t = _tracker()
    nps = t.nps_in_period(dt.date(2022, 1, 1), dt.date(2022, 12, 31), segment='sme')
    assert nps == pytest.approx(100.0)


def test_monthly_nps_has_12_months():
    t = _tracker()
    monthly = t.monthly_nps(2022)
    assert len(monthly) == 12


def test_by_segment():
    t = _tracker()
    by_seg = t.by_segment(2022)
    assert 'sme' in by_seg
    assert 'residential' in by_seg
    assert by_seg['sme'] == pytest.approx(100.0)


def test_annual_summary():
    t = _tracker()
    s = t.annual_summary(2022)
    assert s['responses'] == 4
    assert 'nps' in s
    assert 'promoter_pct' in s
    assert 'detractor_pct' in s
