"""Tests for sim/system_prices_history.py -- mocked Elexon API calls."""

from unittest.mock import MagicMock, patch

import sim.system_prices_history as sph


def _mock_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {"data": data}
    return resp


def _record(date_str, period, ssp=60.0, sbp=65.0):
    return {
        "settlementDate": date_str,
        "settlementPeriod": period,
        "systemSellPrice": ssp,
        "systemBuyPrice": sbp,
    }


def test_two_days_concatenates_records():
    day1_records = [_record("2022-01-01", p) for p in range(1, 3)]
    day2_records = [_record("2022-01-02", p) for p in range(1, 2)]
    responses = iter([_mock_response(day1_records), _mock_response(day2_records)])

    with patch.object(sph._session, "get", side_effect=lambda url: next(responses)):
        result = sph.get_system_prices_range("2022-01-01", "2022-01-02")

    assert len(result) == 3


def test_non_200_skips_that_day():
    day1_records = [_record("2022-01-01", 1)]
    responses = iter([_mock_response([], status=404), _mock_response(day1_records)])

    with patch.object(sph._session, "get", side_effect=lambda url: next(responses)):
        result = sph.get_system_prices_range("2022-01-01", "2022-01-02")

    # day1 returned 404 → 0 records; day2 returned 1 record
    assert len(result) == 1


def test_empty_data_field_returns_empty():
    with patch.object(sph._session, "get", return_value=_mock_response([])):
        result = sph.get_system_prices_range("2022-01-01", "2022-01-01")
    assert result == []


def test_same_start_end_queries_exactly_one_day():
    calls = []
    def record_call(url):
        calls.append(url)
        return _mock_response([_record("2022-06-15", 1)])

    with patch.object(sph._session, "get", side_effect=record_call):
        sph.get_system_prices_range("2022-06-15", "2022-06-15")

    assert len(calls) == 1


def test_three_day_range_queries_three_days():
    calls = []
    def record_call(url):
        calls.append(url)
        return _mock_response([])

    with patch.object(sph._session, "get", side_effect=record_call):
        sph.get_system_prices_range("2022-01-01", "2022-01-03")

    assert len(calls) == 3


def test_records_contain_settlement_date():
    day_records = [_record("2022-05-10", 1)]
    with patch.object(sph._session, "get", return_value=_mock_response(day_records)):
        result = sph.get_system_prices_range("2022-05-10", "2022-05-10")
    assert result[0]["settlementDate"] == "2022-05-10"
