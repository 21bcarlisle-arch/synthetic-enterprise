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


# --- Phase MQ depth tests ---

def test_gas_fuel_lower_base_churn_than_elec():
    from company.crm.churn_model import estimate_churn_probability, GAS_BASE_CHURN_RATE, BASE_CHURN_RATE
    gas = estimate_churn_probability(100.0, 100.0, 0.0, fuel="gas")
    elec = estimate_churn_probability(100.0, 100.0, 0.0, fuel="electricity")
    assert gas < elec
    assert gas == pytest.approx(GAS_BASE_CHURN_RATE)


def test_hedge_fraction_reduces_churn():
    from company.crm.churn_model import estimate_churn_probability
    unhd = estimate_churn_probability(100.0, 120.0, 0.0, hedge_fraction=0.0)
    fully = estimate_churn_probability(100.0, 120.0, 0.0, hedge_fraction=1.0)
    assert fully < unhd


def test_ic_segment_higher_base_churn():
    from company.crm.churn_model import estimate_churn_probability
    resi = estimate_churn_probability(100.0, 100.0, 0.0, segment="resi")
    ic = estimate_churn_probability(100.0, 100.0, 0.0, segment="I&C")
    assert ic > resi


def test_annual_consumption_zero_no_bill_stress():
    from company.crm.churn_model import estimate_churn_probability, BASE_CHURN_RATE, TENURE_DISCOUNT_PER_YEAR
    p = estimate_churn_probability(200.0, 200.0, 0.0, annual_consumption_kwh=0.0)
    assert p == pytest.approx(BASE_CHURN_RATE)


def test_high_consumption_adds_bill_stress():
    from company.crm.churn_model import estimate_churn_probability
    low = estimate_churn_probability(100.0, 100.0, 0.0, annual_consumption_kwh=0.0)
    high = estimate_churn_probability(400.0, 400.0, 0.0, annual_consumption_kwh=10_000.0)
    assert high > low


def test_hangover_adds_uplift():
    from company.crm.churn_model import estimate_churn_probability
    no_hang = estimate_churn_probability(100.0, 100.0, 0.0, hangover_periods_remaining=0)
    hang = estimate_churn_probability(100.0, 100.0, 0.0, hangover_periods_remaining=1)
    assert hang > no_hang


def test_estimate_passive_churn_returns_float():
    from company.crm.churn_model import estimate_passive_churn_probability
    p = estimate_passive_churn_probability(100.0, 110.0, 2.0)
    assert isinstance(p, float)


def test_passive_churn_capped_at_passive_cap():
    from company.crm.churn_model import estimate_passive_churn_probability, PASSIVE_CHURN_CAP
    p = estimate_passive_churn_probability(100.0, 5000.0, 0.0)
    assert p <= PASSIVE_CHURN_CAP


def test_is_active_renewal_returns_bool():
    from company.crm.churn_model import is_active_renewal
    result = is_active_renewal("2020-01-01", "C1")
    assert isinstance(result, bool)


def test_crisis_year_always_passive():
    from company.crm.churn_model import is_active_renewal
    result = is_active_renewal("2022-06-01", "C1")
    assert result is False
