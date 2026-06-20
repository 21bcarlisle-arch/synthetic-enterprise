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
