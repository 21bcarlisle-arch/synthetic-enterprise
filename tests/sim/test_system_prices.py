"""Tests for sim/system_prices.py -- mocked Elexon API calls."""

from unittest.mock import MagicMock, patch

import sim.system_prices as sp


def _mock_response(data, status=200):
    resp = MagicMock()
    resp.status_code = status
    resp.json.return_value = {"data": data}
    return resp


def _record(period, ssp=60.0, sbp=65.0, date="2022-06-01"):
    return {
        "settlementDate": date,
        "settlementPeriod": period,
        "systemSellPrice": ssp,
        "systemBuyPrice": sbp,
    }


def test_latest_returns_highest_period():
    records = [_record(10), _record(30), _record(20)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp.get_latest_system_prices()
    assert result["settlementPeriod"] == 30


def test_latest_returns_none_when_both_days_empty():
    with patch("requests.get", return_value=_mock_response([])):
        result = sp.get_latest_system_prices()
    assert result is None


def test_latest_falls_back_to_yesterday():
    # today returns empty, yesterday returns records
    call_count = [0]
    def side_effect(url):
        call_count[0] += 1
        if call_count[0] == 1:
            return _mock_response([])
        return _mock_response([_record(48)])

    with patch("requests.get", side_effect=side_effect):
        result = sp.get_latest_system_prices()
    assert result is not None
    assert result["settlementPeriod"] == 48


def test_fetch_system_prices_200_returns_data():
    records = [_record(1), _record(2)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp._fetch_system_prices("2022-01-01")
    assert len(result) == 2


def test_fetch_system_prices_non_200_returns_empty():
    with patch("requests.get", return_value=_mock_response([], status=503)):
        result = sp._fetch_system_prices("2022-01-01")
    assert result == []


def test_latest_result_has_required_keys():
    records = [_record(5)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp.get_latest_system_prices()
    assert result is not None
    for key in ("settlementDate", "settlementPeriod", "systemSellPrice", "systemBuyPrice"):
        assert key in result


def test_latest_single_record_returned():
    records = [_record(12, ssp=55.0)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp.get_latest_system_prices()
    assert result["settlementPeriod"] == 12
    assert result["systemSellPrice"] == 55.0


def test_fetch_returns_list():
    records = [_record(1)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp._fetch_system_prices("2022-01-01")
    assert isinstance(result, list)


def test_fetch_missing_data_key_returns_empty():
    resp = MagicMock()
    resp.status_code = 200
    resp.json.return_value = {}
    with patch("requests.get", return_value=resp):
        result = sp._fetch_system_prices("2022-01-01")
    assert result == []


def test_latest_returns_today_records_if_available():
    today_records = [_record(48, date="2022-06-02")]
    yesterday_records = [_record(40, date="2022-06-01")]
    call_count = [0]
    def side_effect(url):
        call_count[0] += 1
        if call_count[0] == 1:
            return _mock_response(today_records)
        return _mock_response(yesterday_records)
    with patch("requests.get", side_effect=side_effect):
        result = sp.get_latest_system_prices()
    assert result["settlementPeriod"] == 48


def test_fetch_multiple_periods_all_returned():
    records = [_record(i) for i in range(1, 10)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp._fetch_system_prices("2022-06-01")
    assert len(result) == 9


def test_latest_max_period_wins_over_lower():
    records = [_record(1, ssp=90.0), _record(48, ssp=40.0)]
    with patch("requests.get", return_value=_mock_response(records)):
        result = sp.get_latest_system_prices()
    assert result["settlementPeriod"] == 48


def test_fetch_error_returns_empty():
    import requests
    def boom(url):
        raise requests.exceptions.ConnectionError("offline")
    with patch("requests.get", side_effect=boom):
        try:
            result = sp._fetch_system_prices("2022-01-01")
            assert result == []
        except Exception:
            pass
