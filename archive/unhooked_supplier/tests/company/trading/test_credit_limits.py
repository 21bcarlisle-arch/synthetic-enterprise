"""Phase 132: Counterparty credit limit tests."""

import pytest
from company.trading.credit_limits import CounterpartyLimit, CounterpartyCreditManager


def _mgr():
    m = CounterpartyCreditManager()
    m.set_limit(CounterpartyLimit("EDF", "EDF Energy", "A-", 500_000, "CCGT_generator"))
    m.set_limit(CounterpartyLimit("SHELL", "Shell Energy", "AA", 1_000_000, "bank"))
    return m


def test_set_and_get_limit():
    m = _mgr()
    lim = m.get_limit("EDF")
    assert lim is not None
    assert lim.limit_gbp == 500_000


def test_no_limit_blocks_trade():
    m = _mgr()
    result = m.check_trade("UNKNOWN", 10_000)
    assert result.approved is False
    assert result.status == "NO_LIMIT"


def test_green_trade_approved():
    m = _mgr()
    result = m.check_trade("EDF", 100_000)  # 20% of 500k
    assert result.approved is True
    assert result.status == "GREEN"


def test_amber_trade_approved_with_monitoring():
    m = _mgr()
    m.update_exposure("EDF", 380_000)  # 76% of 500k before trade
    result = m.check_trade("EDF", 10_000)  # 78%
    assert result.approved is True
    assert result.status == "AMBER"


def test_red_trade_blocked():
    m = _mgr()
    m.update_exposure("EDF", 460_000)  # 92% already
    result = m.check_trade("EDF", 5_000)  # 93%
    assert result.approved is False
    assert result.status == "RED"


def test_update_exposure():
    m = _mgr()
    m.update_exposure("EDF", 200_000)
    m.update_exposure("EDF", 50_000)
    assert m.current_exposure("EDF") == 250_000


def test_breached_limits():
    m = _mgr()
    m.update_exposure("EDF", 460_000)  # 92% — breached
    breached = m.breached_limits()
    assert any(cp == "EDF" for cp, _, _ in breached)


def test_summary_structure():
    m = _mgr()
    s = m.summary()
    for k in ("total_limits", "active_limits", "breached", "total_exposure_gbp", "total_limit_gbp"):
        assert k in s


def test_utilisation_pct_correct():
    m = _mgr()
    m.update_exposure("EDF", 100_000)
    result = m.check_trade("EDF", 0)  # 0 new trade to just check current
    assert result.utilisation_pct == 20.0


# --- Phase KT depth tests ---

def test_counterparty_id_stored():
    lim = CounterpartyLimit('TEST_ID', 'Test Corp', 'BBB', 200_000, 'bank')
    assert lim.counterparty_id == 'TEST_ID'


def test_name_stored():
    lim = CounterpartyLimit('T1', 'Bright Corp', 'A', 100_000, 'trader')
    assert lim.name == 'Bright Corp'


def test_credit_rating_stored():
    lim = CounterpartyLimit('T1', 'X', 'AA', 100_000, 'bank')
    assert lim.credit_rating == 'AA'


def test_limit_gbp_stored():
    lim = CounterpartyLimit('T1', 'X', 'A', 750_000, 'bank')
    assert lim.limit_gbp == 750_000


def test_category_stored():
    lim = CounterpartyLimit('T1', 'X', 'A', 100_000, 'exchange')
    assert lim.category == 'exchange'


def test_active_true_by_default():
    lim = CounterpartyLimit('T1', 'X', 'A', 100_000, 'bank')
    assert lim.active is True


def test_current_exposure_zero_initially():
    m = CounterpartyCreditManager()
    m.set_limit(CounterpartyLimit('T1', 'X', 'A', 100_000, 'bank'))
    assert m.current_exposure('T1') == pytest.approx(0.0)


def test_get_limit_none_missing():
    m = CounterpartyCreditManager()
    assert m.get_limit('NOBODY') is None


def test_check_trade_message_present():
    m = _mgr()
    result = m.check_trade('EDF', 100_000)
    assert isinstance(result.message, str)


def test_two_accumulations():
    m = _mgr()
    m.update_exposure('EDF', 100_000)
    m.update_exposure('EDF', 150_000)
    assert m.current_exposure('EDF') == pytest.approx(250_000)
