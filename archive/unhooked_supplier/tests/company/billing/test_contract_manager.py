import datetime as dt
import pytest
from company.billing.contract_manager import (
    ContractStatus, ContractType, SupplyContract, ContractManager
)


def _manager_with_contract() -> tuple:
    mgr = ContractManager()
    c = mgr.register(
        'CTR001', 'C001', 'MPAN001', ContractType.FIXED_TERM,
        dt.date(2022, 1, 1), dt.date(2022, 12, 31),
        unit_rate_pence_per_kwh=28.0, standing_charge_pence_per_day=50.0,
        annual_quantity_kwh=3000.0,
    )
    return mgr, c


def test_contract_registered_active():
    mgr, c = _manager_with_contract()
    assert c.status == ContractStatus.ACTIVE
    assert c.contract_type == ContractType.FIXED_TERM


def test_term_months():
    _, c = _manager_with_contract()
    assert c.term_months == pytest.approx(12, abs=1)


def test_notice_deadline_42_days():
    _, c = _manager_with_contract()
    nd = c.notice_deadline()
    assert nd == dt.date(2022, 11, 19)


def test_in_notice_window():
    _, c = _manager_with_contract()
    assert c.is_in_notice_window(dt.date(2022, 11, 25))
    assert not c.is_in_notice_window(dt.date(2022, 10, 1))


def test_days_to_expiry():
    _, c = _manager_with_contract()
    assert c.days_to_expiry(dt.date(2022, 12, 1)) == 30


def test_annual_cost_estimate():
    _, c = _manager_with_contract()
    expected = 3000 * 28.0 / 100 + 50.0 / 100 * 365
    assert c.annual_cost_estimate_gbp() == pytest.approx(expected, rel=0.01)


def test_serve_notice():
    mgr, c = _manager_with_contract()
    mgr.serve_notice('CTR001', dt.date(2022, 11, 20))
    assert c.status == ContractStatus.IN_NOTICE
    assert c.notice_served_date == dt.date(2022, 11, 20)


def test_expiring_within():
    mgr, _ = _manager_with_contract()
    expiring = mgr.expiring_within(dt.date(2022, 12, 1), 31)
    assert len(expiring) == 1
    not_expiring = mgr.expiring_within(dt.date(2022, 12, 1), 15)
    assert len(not_expiring) == 0


def test_portfolio_summary():
    mgr, _ = _manager_with_contract()
    s = mgr.portfolio_summary(dt.date(2022, 11, 25))
    assert s['active'] == 1
    assert s['in_notice_window'] == 1
    assert 'by_type' in s


# --- Phase KU depth tests ---

def test_contract_id_stored():
    _, c = _manager_with_contract()
    assert c.contract_id == 'CTR001'


def test_customer_id_stored():
    _, c = _manager_with_contract()
    assert c.customer_id == 'C001'


def test_mpan_stored():
    _, c = _manager_with_contract()
    assert c.mpan == 'MPAN001'


def test_unit_rate_stored():
    _, c = _manager_with_contract()
    assert c.unit_rate_pence_per_kwh == pytest.approx(28.0)


def test_standing_charge_stored():
    _, c = _manager_with_contract()
    assert c.standing_charge_pence_per_day == pytest.approx(50.0)


def test_annual_quantity_stored():
    _, c = _manager_with_contract()
    assert c.annual_quantity_kwh == pytest.approx(3000.0)


def test_start_date_stored():
    _, c = _manager_with_contract()
    assert c.start_date == dt.date(2022, 1, 1)


def test_end_date_stored():
    _, c = _manager_with_contract()
    assert c.end_date == dt.date(2022, 12, 31)


def test_active_contracts_returns_list():
    mgr, _ = _manager_with_contract()
    contracts = mgr.active_contracts()
    assert isinstance(contracts, list)
    assert len(contracts) == 1


def test_notice_served_date_none_before_notice():
    _, c = _manager_with_contract()
    assert c.notice_served_date is None
