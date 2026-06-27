import json
import pytest
from pathlib import Path
from company.billing.hh_consumption import (
    get_hh_consumption,
    recent_hh_periods,
    is_feed_available,
)


@pytest.fixture
def feed_path(tmp_path):
    data = {
        "records": [
            {"customer_id": "C1", "date": "2022-01-01", "period": 1, "kwh": 0.5, "hour": 0},
            {"customer_id": "C1", "date": "2022-01-01", "period": 2, "kwh": 0.6, "hour": 0},
            {"customer_id": "C1", "date": "2022-01-02", "period": 1, "kwh": 0.4, "hour": 0},
            {"customer_id": "C2", "date": "2022-01-01", "period": 1, "kwh": 1.0, "hour": 0},
        ]
    }
    p = tmp_path / "consumption_feed.json"
    p.write_text(json.dumps(data))
    return p


class TestGetHHConsumption:
    def test_returns_empty_when_feed_missing(self, tmp_path):
        result = get_hh_consumption("C1", tmp_path / "missing.json")
        assert result == []

    def test_filters_by_customer(self, feed_path):
        records = get_hh_consumption("C1", feed_path)
        assert len(records) == 3
        assert all(r["customer_id"] == "C1" for r in records)

    def test_c2_independent(self, feed_path):
        records = get_hh_consumption("C2", feed_path)
        assert len(records) == 1

    def test_sorted_by_date_period(self, feed_path):
        records = get_hh_consumption("C1", feed_path)
        keys = [(r["date"], r["period"]) for r in records]
        assert keys == sorted(keys)

    def test_unknown_customer_empty(self, feed_path):
        assert get_hh_consumption("UNKNOWN", feed_path) == []


class TestRecentHHPeriods:
    def test_returns_last_n(self):
        records = [{"period": i} for i in range(100)]
        result = recent_hh_periods(records, n_periods=48)
        assert len(result) == 48
        assert result[-1]["period"] == 99

    def test_default_48(self):
        records = [{"period": i} for i in range(100)]
        result = recent_hh_periods(records)
        assert len(result) == 48

    def test_fewer_than_n_returns_all(self):
        records = [{"period": i} for i in range(10)]
        result = recent_hh_periods(records, n_periods=48)
        assert len(result) == 10


class TestIsFeedAvailable:
    def test_missing_returns_false(self, tmp_path):
        assert not is_feed_available(tmp_path / "missing.json")

    def test_existing_returns_true(self, feed_path):
        assert is_feed_available(feed_path)
