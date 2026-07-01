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


# --- Phase JY depth tests ---

def test_classify_score_6_is_detractor():
    assert classify_nps(6) == 'detractor'


def test_classify_score_7_is_passive():
    assert classify_nps(7) == 'passive'


def test_nps_response_is_promoter_at_9():
    r = NPSResponse('C1', 9, dt.date(2022, 1, 1), 'residential', 'post_call')
    assert r.is_promoter is True


def test_nps_response_is_detractor_at_6():
    r = NPSResponse('C1', 6, dt.date(2022, 1, 1), 'residential', 'post_call')
    assert r.is_detractor is True


def test_nps_response_not_detractor_at_7():
    r = NPSResponse('C1', 7, dt.date(2022, 1, 1), 'residential', 'post_call')
    assert r.is_detractor is False


def test_nps_in_period_none_when_empty():
    t = NPSTracker()
    result = t.nps_in_period(dt.date(2022, 1, 1), dt.date(2022, 12, 31))
    assert result is None


def test_record_score_zero_valid():
    t = NPSTracker()
    r = t.record('C001', 0, dt.date(2022, 1, 1), 'residential')
    assert r.score == 0
    assert r.is_detractor is True


def test_record_score_negative_raises():
    t = NPSTracker()
    with pytest.raises(ValueError):
        t.record('C001', -1, dt.date(2022, 1, 1), 'residential')


def test_monthly_nps_none_for_empty_month():
    t = NPSTracker()
    t.record('C001', 9, dt.date(2022, 1, 10), 'residential')
    monthly = t.monthly_nps(2022)
    assert monthly[3] is None  # March has no responses


def test_annual_summary_empty_year():
    t = _tracker()  # has responses in 2022
    s = t.annual_summary(2021)
    assert s['responses'] == 0
    assert s['nps'] is None
    assert s['promoter_pct'] is None
    assert s['detractor_pct'] is None
