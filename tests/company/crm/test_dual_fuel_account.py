import pytest
from company.crm.dual_fuel_account import (
    FuelType, FuelLeg, DualFuelAccount, DualFuelAccountBook,
)


def make_elec_leg(account_id="A1", tariff="Standard", unit_rate=28.0,
                  standing=60.0, kwh=3500.0, active=True):
    return FuelLeg(
        account_id=account_id,
        fuel=FuelType.ELECTRICITY,
        supply_point_ref="1012345678901",
        tariff_name=tariff,
        unit_rate_pence=unit_rate,
        standing_charge_pence=standing,
        estimated_annual_kwh=kwh,
        active=active,
    )


def make_gas_leg(account_id="A1", tariff="Standard", unit_rate=7.0,
                 standing=30.0, kwh=12000.0, active=True):
    return FuelLeg(
        account_id=account_id,
        fuel=FuelType.GAS,
        supply_point_ref="1234567890",
        tariff_name=tariff,
        unit_rate_pence=unit_rate,
        standing_charge_pence=standing,
        estimated_annual_kwh=kwh,
        active=active,
    )


class TestFuelLeg:
    def test_annual_cost_electricity(self):
        leg = make_elec_leg(unit_rate=28.0, standing=60.0, kwh=3500.0)
        expected = round((3500 * 28 / 100) + (365 * 60 / 100), 2)
        assert leg.estimated_annual_cost_gbp == expected

    def test_annual_cost_gas(self):
        leg = make_gas_leg(unit_rate=7.0, standing=30.0, kwh=12000.0)
        expected = round((12000 * 7 / 100) + (365 * 30 / 100), 2)
        assert leg.estimated_annual_cost_gbp == expected

    def test_frozen(self):
        leg = make_elec_leg()
        with pytest.raises((AttributeError, TypeError)):
            leg.unit_rate_pence = 0.0  # type: ignore[misc]

    def test_fuel_type_stored(self):
        leg = make_elec_leg()
        assert leg.fuel == FuelType.ELECTRICITY

    def test_active_default_true(self):
        leg = make_gas_leg()
        assert leg.active is True


class TestDualFuelAccount:
    def test_is_dual_fuel(self):
        acc = DualFuelAccount("A1", make_elec_leg(), make_gas_leg())
        assert acc.is_dual_fuel is True

    def test_is_electricity_only(self):
        acc = DualFuelAccount("A1", make_elec_leg(), None)
        assert acc.is_electricity_only is True
        assert acc.is_dual_fuel is False

    def test_is_gas_only(self):
        acc = DualFuelAccount("A1", None, make_gas_leg())
        assert acc.is_gas_only is True
        assert acc.is_dual_fuel is False

    def test_has_any_supply_true(self):
        acc = DualFuelAccount("A1", make_elec_leg(), None)
        assert acc.has_any_supply is True

    def test_has_any_supply_false(self):
        acc = DualFuelAccount("A1", None, None)
        assert acc.has_any_supply is False

    def test_combined_annual_cost_dual(self):
        e = make_elec_leg(unit_rate=28.0, standing=60.0, kwh=3500.0)
        g = make_gas_leg(unit_rate=7.0, standing=30.0, kwh=12000.0)
        acc = DualFuelAccount("A1", e, g)
        expected = round(e.estimated_annual_cost_gbp + g.estimated_annual_cost_gbp, 2)
        assert acc.combined_annual_cost_gbp == expected

    def test_combined_cost_excludes_inactive_leg(self):
        e = make_elec_leg(active=True)
        g = make_gas_leg(active=False)
        acc = DualFuelAccount("A1", e, g)
        assert acc.combined_annual_cost_gbp == e.estimated_annual_cost_gbp

    def test_combined_cost_elec_only(self):
        e = make_elec_leg()
        acc = DualFuelAccount("A1", e, None)
        assert acc.combined_annual_cost_gbp == e.estimated_annual_cost_gbp

    def test_active_fuels_dual(self):
        acc = DualFuelAccount("A1", make_elec_leg(), make_gas_leg())
        assert set(acc.active_fuels) == {"electricity", "gas"}

    def test_active_fuels_inactive_gas(self):
        acc = DualFuelAccount("A1", make_elec_leg(), make_gas_leg(active=False))
        assert acc.active_fuels == ["electricity"]

    def test_frozen(self):
        acc = DualFuelAccount("A1", make_elec_leg(), None)
        with pytest.raises((AttributeError, TypeError)):
            acc.account_id = "X"  # type: ignore[misc]


class TestDualFuelAccountBook:
    def test_register_and_get_dual(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("A1"))
        book.register_gas_leg(make_gas_leg("A1"))
        acc = book.get_account("A1")
        assert acc is not None
        assert acc.is_dual_fuel

    def test_get_account_none_unknown(self):
        book = DualFuelAccountBook()
        assert book.get_account("UNKNOWN") is None

    def test_register_wrong_fuel_raises(self):
        book = DualFuelAccountBook()
        with pytest.raises(ValueError):
            book.register_electricity_leg(make_gas_leg("A1"))

    def test_dual_fuel_accounts(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("A1"))
        book.register_gas_leg(make_gas_leg("A1"))
        book.register_electricity_leg(make_elec_leg("A2"))
        assert len(book.dual_fuel_accounts()) == 1

    def test_electricity_only(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("A1"))
        book.register_electricity_leg(make_elec_leg("A2"))
        book.register_gas_leg(make_gas_leg("A2"))
        result = book.electricity_only()
        assert len(result) == 1
        assert result[0].account_id == "A1"

    def test_gas_only(self):
        book = DualFuelAccountBook()
        book.register_gas_leg(make_gas_leg("A1"))
        assert len(book.gas_only()) == 1

    def test_total_combined_annual_cost(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("A1"))
        book.register_gas_leg(make_gas_leg("A1"))
        total = book.total_combined_annual_cost_gbp()
        e = make_elec_leg("A1")
        g = make_gas_leg("A1")
        expected = round(e.estimated_annual_cost_gbp + g.estimated_annual_cost_gbp, 2)
        assert abs(total - expected) < 0.01

    def test_dual_fuel_summary_keys(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("A1"))
        book.register_gas_leg(make_gas_leg("A1"))
        book.register_electricity_leg(make_elec_leg("A2"))
        s = book.dual_fuel_summary()
        assert s["total_accounts"] == 2
        assert s["dual_fuel"] == 1
        assert s["electricity_only"] == 1
        assert s["gas_only"] == 0
        assert "combined_annual_cost_gbp" in s

    def test_all_accounts_sorted(self):
        book = DualFuelAccountBook()
        book.register_electricity_leg(make_elec_leg("B1"))
        book.register_electricity_leg(make_elec_leg("A1"))
        ids = [a.account_id for a in book.all_accounts()]
        assert ids == sorted(ids)
