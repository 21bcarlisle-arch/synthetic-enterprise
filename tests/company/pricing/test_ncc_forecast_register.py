"""Tests for company/pricing/ncc_forecast_register.py (Sprint CL)."""
import datetime as dt
import pytest

from company.pricing.ncc_forecast_register import (
    NCCForecastRegister,
    NCCComponent,
    Fuel,
)

P_START = dt.date(2024, 1, 1)
P_END = dt.date(2024, 12, 31)


def _reg():
    return NCCForecastRegister()


def test_record_id_starts_with_ncc_fc():
    reg = _reg()
    r = reg.add_forecast(P_START, P_END, NCCComponent.DUOS, Fuel.ELECTRICITY, 1.5, "p/kWh")
    assert r.record_id.startswith("NCC-FC-")


def test_component_stored():
    reg = _reg()
    r = reg.add_forecast(P_START, P_END, NCCComponent.BSUOS, Fuel.ELECTRICITY, 0.5, "p/kWh")
    assert r.component == NCCComponent.BSUOS


def test_fuel_stored():
    reg = _reg()
    r = reg.add_forecast(P_START, P_END, NCCComponent.TNUOS, Fuel.GAS, 0.3, "p/kWh")
    assert r.fuel == Fuel.GAS


def test_unit_rate_stored():
    reg = _reg()
    r = reg.add_forecast(P_START, P_END, NCCComponent.CM, Fuel.ELECTRICITY, 0.4, "p/kWh")
    assert r.unit_rate == 0.4


def test_period_end_before_start_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.add_forecast(P_END, P_START, NCCComponent.DUOS, Fuel.ELECTRICITY, 1.0, "p/kWh")


def test_negative_rate_raises():
    reg = _reg()
    with pytest.raises(ValueError):
        reg.add_forecast(P_START, P_END, NCCComponent.DUOS, Fuel.ELECTRICITY, -0.1, "p/kWh")


def test_total_ncc_pence_per_kwh_sums():
    reg = _reg()
    reg.add_forecast(P_START, P_END, NCCComponent.DUOS, Fuel.ELECTRICITY, 1.5, "p/kWh")
    reg.add_forecast(P_START, P_END, NCCComponent.BSUOS, Fuel.ELECTRICITY, 0.5, "p/kWh")
    total = reg.total_ncc_pence_per_kwh(P_START, Fuel.ELECTRICITY)
    assert abs(total - 2.0) < 0.001


def test_by_component_filters():
    reg = _reg()
    reg.add_forecast(P_START, P_END, NCCComponent.DUOS, Fuel.ELECTRICITY, 1.5, "p/kWh")
    reg.add_forecast(P_START, P_END, NCCComponent.CM, Fuel.ELECTRICITY, 0.4, "p/kWh")
    duos = reg.by_component(NCCComponent.DUOS)
    assert len(duos) == 1


def test_gas_elec_only_not_applicable():
    reg = _reg()
    r = reg.add_forecast(P_START, P_END, NCCComponent.BSUOS, Fuel.GAS, 0.5, "p/kWh")
    assert r.is_applicable_for_fuel() is False


def test_distinct_periods_returns_unique():
    reg = _reg()
    reg.add_forecast(P_START, P_END, NCCComponent.DUOS, Fuel.ELECTRICITY, 1.0, "p/kWh")
    reg.add_forecast(P_START, P_END, NCCComponent.CM, Fuel.ELECTRICITY, 0.5, "p/kWh")
    periods = reg.distinct_periods()
    assert len(periods) == 1
