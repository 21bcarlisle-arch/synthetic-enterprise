"""Tests for get_churn_estimate on SimInterface implementations."""
import pytest

from company.crm.churn_model import estimate_churn_probability
from company.interfaces.sim_interface import LiveSimInterface, StubSimInterface


def test_stub_get_churn_estimate_matches_model():
    """StubSimInterface.get_churn_estimate delegates to estimate_churn_probability."""
    iface = StubSimInterface()
    result = iface.get_churn_estimate("C1", 100.0, 120.0, 3.0)
    expected = estimate_churn_probability(100.0, 120.0, 3.0)
    assert result == pytest.approx(expected)


def test_stub_churn_estimate_clamps_to_zero():
    iface = StubSimInterface()
    result = iface.get_churn_estimate("C1", 200.0, 100.0, 5.0)
    assert result >= 0.0


def test_stub_churn_estimate_clamps_to_max():
    iface = StubSimInterface()
    result = iface.get_churn_estimate("C1", 100.0, 10000.0, 0.0)
    assert result == 0.95


def test_stub_churn_estimate_ignores_account_id():
    """account_id is not used in computation — observable signals only."""
    iface = StubSimInterface()
    r1 = iface.get_churn_estimate("C1", 100.0, 110.0, 2.0)
    r2 = iface.get_churn_estimate("C99", 100.0, 110.0, 2.0)
    assert r1 == r2


def test_live_get_churn_estimate_matches_model():
    """LiveSimInterface.get_churn_estimate also delegates to estimate_churn_probability."""
    iface = LiveSimInterface()
    result = iface.get_churn_estimate("C1", 100.0, 130.0, 1.5)
    expected = estimate_churn_probability(100.0, 130.0, 1.5)
    assert result == pytest.approx(expected)


# --- Phase KH depth tests ---

def test_stub_result_between_zero_and_one():
    iface = StubSimInterface()
    r = iface.get_churn_estimate('C1', 110.0, 115.0, 2.0)
    assert 0.0 <= r <= 1.0


def test_live_result_between_zero_and_one():
    iface = LiveSimInterface()
    r = iface.get_churn_estimate('C1', 110.0, 115.0, 2.0)
    assert 0.0 <= r <= 1.0


def test_stub_and_live_give_same_result():
    stub = StubSimInterface()
    live = LiveSimInterface()
    own, mkt, tenure = 100.0, 120.0, 3.0
    r_stub = stub.get_churn_estimate('C1', own, mkt, tenure)
    r_live = live.get_churn_estimate('C1', own, mkt, tenure)
    assert r_stub == pytest.approx(r_live)


def test_stub_higher_tenure_lowers_churn():
    iface = StubSimInterface()
    r_new = iface.get_churn_estimate('C1', 100.0, 120.0, 0.0)
    r_loyal = iface.get_churn_estimate('C1', 100.0, 120.0, 10.0)
    assert r_loyal < r_new


def test_stub_higher_market_price_increases_churn():
    iface = StubSimInterface()
    r_low = iface.get_churn_estimate('C1', 100.0, 105.0, 2.0)
    r_high = iface.get_churn_estimate('C1', 100.0, 150.0, 2.0)
    assert r_high > r_low


def test_stub_equal_prices_non_negative():
    iface = StubSimInterface()
    r = iface.get_churn_estimate('C1', 100.0, 100.0, 2.0)
    assert r >= 0.0


def test_stub_returns_float():
    iface = StubSimInterface()
    r = iface.get_churn_estimate('C1', 100.0, 120.0, 1.0)
    assert isinstance(r, float)


def test_live_clamps_to_max():
    iface = LiveSimInterface()
    r = iface.get_churn_estimate('C1', 100.0, 10000.0, 0.0)
    assert r == pytest.approx(0.95)


def test_stub_zero_tenure_matches_model():
    iface = StubSimInterface()
    r = iface.get_churn_estimate('C1', 100.0, 100.0, 0.0)
    expected = estimate_churn_probability(100.0, 100.0, 0.0)
    assert r == pytest.approx(expected)


def test_stub_different_accounts_same_inputs_same_result():
    iface = StubSimInterface()
    r1 = iface.get_churn_estimate('CUST_A', 100.0, 110.0, 2.0)
    r2 = iface.get_churn_estimate('CUST_Z', 100.0, 110.0, 2.0)
    assert r1 == pytest.approx(r2)
