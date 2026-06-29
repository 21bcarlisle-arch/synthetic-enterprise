"""Phase Q tests: battery home energy storage settlement wiring.

Battery charges from excess solar (midday), discharges in evening peak (16:00-20:00,
periods 33-40). Only activates when customer has battery + solar + irradiance data.
"""
import pytest
from simulation.run_phase2b import (
    _BATTERY_EVENING_PEAK,
    _battery_daily_dispatch,
    _BATTERY_ROUNDTRIP_EFFICIENCY,
)
from simulation.household_demand import HouseholdDemandRegister
from saas.customers import CUSTOMERS


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _flat_load(kwh_per_period: float = 0.1) -> list[float]:
    return [kwh_per_period] * 48


def _solar_midday(midday_kwh: float = 0.5) -> list[float]:
    """Solar generating only midday (periods 17-32, 08:00-16:00)."""
    gen = [0.0] * 48
    for i in range(16, 32):  # 0-indexed periods 17-32
        gen[i] = midday_kwh
    return gen


def _solar_zero() -> list[float]:
    return [0.0] * 48


# ---------------------------------------------------------------------------
# _battery_daily_dispatch unit tests
# ---------------------------------------------------------------------------

class TestBatteryDailyDispatch:
    def test_no_solar_no_effect(self):
        gross = _flat_load(0.2)
        solar = _solar_zero()
        net = _battery_daily_dispatch(gross, solar, battery_kwh=10.0)
        # Without solar there is nothing to charge battery from
        assert all(abs(n - g) < 1e-9 for n, g in zip(net, gross))

    def test_solar_only_no_battery_reduces_midday(self):
        # Confirm standard solar reduction without battery (battery_kwh=0)
        gross = _flat_load(0.1)
        solar = _solar_midday(0.5)  # solar >> load midday
        net = _battery_daily_dispatch(gross, solar, battery_kwh=0.0)
        # Midday periods: solar > load → net == 0
        for i in range(16, 32):
            assert net[i] == pytest.approx(0.0)
        # Morning/evening: no solar → net == gross
        assert net[0] == pytest.approx(0.1)

    def test_evening_peak_reduced_by_battery(self):
        # Large solar midday, large battery — should reduce evening peak
        gross = _flat_load(0.5)
        solar = _solar_midday(2.0)  # excess 1.5 kWh × 16 periods = 24 kWh > battery
        net = _battery_daily_dispatch(gross, solar, battery_kwh=10.0)
        # Evening peak periods (0-indexed 32-39) should be lower than gross net-of-solar
        for i in range(32, 40):
            # Without battery: net[i] = 0.5 (no solar in evening)
            assert net[i] < 0.5, f"Period {i+1} not reduced: {net[i]}"

    def test_battery_soc_never_exceeds_capacity(self):
        # Even with huge excess solar, SOC stays <= battery_kwh
        gross = [0.001] * 48  # tiny load
        solar = [5.0] * 48   # massive solar all day
        battery_kwh = 7.5
        net = _battery_daily_dispatch(gross, solar, battery_kwh=battery_kwh)
        # We can't inspect SOC directly, but net in evening peak must be >= 0
        assert all(n >= 0.0 for n in net)
        # And evening discharge can't exceed battery_kwh
        evening_reduction = sum(max(0.0, 0.001 - net[i]) for i in range(32, 40))
        assert evening_reduction <= battery_kwh + 1e-9

    def test_charge_efficiency_reduces_stored_energy(self):
        # 1 kWh excess solar → 0.9 kWh stored (efficiency = 0.90)
        # Battery capacity 1 kWh; excess solar exactly 1 kWh
        gross = [0.0] * 48
        solar = [0.0] * 48
        solar[10] = 1.0  # 1 kWh excess at period 11 (not in evening peak)
        battery_kwh = 1.0
        net = _battery_daily_dispatch(gross, solar, battery_kwh=battery_kwh)
        # Stored = 1.0 * 0.90; discharged across periods 33-40
        evening_reduction = sum(max(0.0, -net[i]) for i in range(32, 40)) + sum(
            max(0.0, 0.0 - net[i]) for i in range(32, 40)
        )
        # Total discharged across evening peak
        total_discharged = sum(0.0 - min(0.0, n) for n in net[32:40])
        # What actually was discharged: stored = 1.0 * 0.9 = 0.9 kWh
        # Evening load = 0, so discharge = 0 (no import to offset)
        # Different test: evening load 0.5 kWh per period
        gross2 = [0.0] * 48
        for i in range(32, 40):
            gross2[i] = 0.5
        net2 = _battery_daily_dispatch(gross2, solar, battery_kwh=battery_kwh)
        total_reduction = sum(0.5 - net2[i] for i in range(32, 40))
        assert total_reduction == pytest.approx(1.0 * _BATTERY_ROUNDTRIP_EFFICIENCY, abs=1e-6)

    def test_evening_peak_periods_constant(self):
        assert 33 in _BATTERY_EVENING_PEAK
        assert 40 in _BATTERY_EVENING_PEAK
        assert 32 not in _BATTERY_EVENING_PEAK
        assert 41 not in _BATTERY_EVENING_PEAK

    def test_non_evening_periods_not_discharged(self):
        gross = _flat_load(0.5)
        solar = _solar_midday(2.0)
        net = _battery_daily_dispatch(gross, solar, battery_kwh=10.0)
        # Morning periods (1-32 excl. midday) should be max(0, 0.5 - 0.0) = 0.5
        # (solar only in midday 17-32, so morning and late evening unaffected)
        for i in range(0, 16):  # periods 1-16 morning
            assert net[i] == pytest.approx(0.5)

    def test_large_battery_vs_small_battery(self):
        # Large battery discharges more in evening peak than small battery
        gross = _flat_load(0.3)
        solar = _solar_midday(1.5)
        net_large = _battery_daily_dispatch(gross, solar, battery_kwh=13.5)
        net_small = _battery_daily_dispatch(gross, solar, battery_kwh=4.0)
        large_evening = sum(net_large[i] for i in range(32, 40))
        small_evening = sum(net_small[i] for i in range(32, 40))
        assert large_evening <= small_evening

    def test_winter_day_minimal_solar_minimal_discharge(self):
        # Winter: solar generation ~5% of summer
        gross = _flat_load(0.3)
        solar = [0.0] * 48
        for i in range(16, 32):
            solar[i] = 0.02  # minimal winter solar
        net_winter = _battery_daily_dispatch(gross, solar, battery_kwh=10.0)
        net_no_battery = _battery_daily_dispatch(gross, solar, battery_kwh=0.0)
        # Battery charges from tiny excess; evening reduction should be small
        winter_reduction = sum(
            net_no_battery[i] - net_winter[i] for i in range(32, 40)
        )
        # No excess solar in winter (load 0.3 > solar 0.02) → no charge → no discharge
        assert winter_reduction == pytest.approx(0.0, abs=1e-9)

    def test_output_always_non_negative(self):
        gross = _flat_load(0.1)
        solar = [2.0] * 48  # solar >> load all day
        net = _battery_daily_dispatch(gross, solar, battery_kwh=5.0)
        assert all(n >= 0.0 for n in net)

    def test_without_solar_customer_same_as_no_battery(self):
        gross = _flat_load(0.4)
        solar = _solar_zero()
        net_battery = _battery_daily_dispatch(gross, solar, battery_kwh=10.0)
        net_none = _battery_daily_dispatch(gross, solar, battery_kwh=0.0)
        assert net_battery == pytest.approx(net_none)


# ---------------------------------------------------------------------------
# dynamic_assets now exposes battery
# ---------------------------------------------------------------------------

class TestDynamicAssetsBattery:
    def test_battery_key_present(self):
        """dynamic_assets() now returns battery and battery_kwh."""
        register = HouseholdDemandRegister(CUSTOMERS, seed=42)
        assets = register.dynamic_assets("C1", "2019-01-01")
        assert "battery" in assets
        assert "battery_kwh" in assets

    def test_battery_false_pre_install(self):
        register = HouseholdDemandRegister(CUSTOMERS, seed=42)
        # C1 at baseline has no battery
        assets = register.dynamic_assets("C1", "2016-01-01")
        assert assets["battery"] is False
        assert assets["battery_kwh"] == pytest.approx(0.0)

    def test_battery_kwh_non_negative(self):
        register = HouseholdDemandRegister(CUSTOMERS, seed=42)
        for cid in ["C1", "C2", "C3", "C4"]:
            assets = register.dynamic_assets(cid, "2024-01-01")
            assert assets["battery_kwh"] >= 0.0
