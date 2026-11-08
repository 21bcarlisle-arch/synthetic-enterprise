"""Tests for company/market/map_contract_register.py (Sprint CLI)."""
import datetime as dt
import pytest

from company.market.map_contract_register import (
    MAPContractRegister,
    MAPContractStatus,
    MAPServiceType,
    MAPServiceRate,
)

START = dt.date(2022, 1, 1)
END = dt.date(2025, 12, 31)


def _reg():
    return MAPContractRegister()


def test_contract_id_starts_with_mapcon():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.50)
    assert r.contract_id.startswith("MAPCON-")


def test_provider_name_stored():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.50)
    assert r.provider_name == "SmartCo"


def test_is_active_true_by_default():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.50)
    assert r.is_active is True


def test_is_current_as_of_within_range():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.50)
    assert r.is_current_as_of(dt.date(2023, 6, 1)) is True


def test_monthly_rental_cost_computed():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 200, 5.0)
    assert abs(r.monthly_rental_cost_gbp() - 1000.0) < 0.01


def test_annual_rental_cost_is_12x_monthly():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.0)
    assert abs(r.annual_rental_cost_gbp() - 4800.0) < 0.01


def test_contract_end_before_start_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.register_contract("SmartCo", END, START, 100, 4.0)


def test_terminate_sets_status():
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.0)
    t = reg.terminate(r.contract_id, dt.date(2023, 3, 1))
    assert t.status == MAPContractStatus.TERMINATED


def test_active_contracts_as_of_filters():
    reg = _reg()
    reg.register_contract("SmartCo", START, END, 100, 4.0)
    assert len(reg.active_contracts(dt.date(2023, 6, 1))) == 1
    assert len(reg.active_contracts(dt.date(2026, 1, 1))) == 0


def test_service_rate_for_returns_matching():
    rate = MAPServiceRate(MAPServiceType.SMETS2_NEW_INSTALL, 100.0, "per_visit")
    reg = _reg()
    r = reg.register_contract("SmartCo", START, END, 100, 4.0, service_rates=(rate,))
    found = r.service_rate_for(MAPServiceType.SMETS2_NEW_INSTALL)
    assert found is not None
    assert found.unit_cost_gbp == 100.0
