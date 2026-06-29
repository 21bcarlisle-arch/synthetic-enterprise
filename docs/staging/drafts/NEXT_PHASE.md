Phase F — Heat Pump Electricity Uplift

Status: PROPOSED (2026-06-29)

Context:
Phase D wired heat_pump_installed life events into gas settlement: ASHP homes
get GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12 (12% of gas AQ for residual cooking).
Phase E closed insulation caps. But electricity settlement is still incomplete:
an ASHP home consumes significantly more electricity for space heating, yet
eac_multiplier_for_date() ignores heating system entirely.

Gap:
A household that installs ASHP in 2022 sees:
  - Gas AQ correctly falls to ~12% of baseline (Phase D) ✓
  - Electricity EAC unchanged at EPC * EV * solar — WRONG
  - Reality: ASHP consumes ~5,500 kWh/yr electricity for space heating + hot water
  - Net result: electricity EAC should rise by ~5,500 kWh from installation date

Calibration source:
  BEIS Electrification of Heat Trial 2021-22 (743 ASHP installations):
  average 3,503 kWh/yr electricity @ mean seasonal COP 2.72.
  Broader UK Climate Change Committee estimates 4,000-6,000 kWh/yr for
  average home. EPC-D/E homes (higher thermal demand, lower CoP) toward
  upper end. Using ASHP_BASE_ELECTRICITY_KWH = 5_500 as midpoint for
  the synthetic portfolio (EPC-C/D mix). Consistent with DESNZ 2023 Heat
  Pump Roadmap median of 5,200 kWh/yr for pre-2000 UK stock.

What Phase F builds:

  simulation/household.py (1 method):
    ashp_annual_kwh(self) -> float:
      # Returns 0 for non-heat-pump homes; ASHP_BASE_ELECTRICITY_KWH for ASHP
      return ASHP_BASE_ELECTRICITY_KWH if self.is_heat_pump else 0.0
    ASHP_BASE_ELECTRICITY_KWH = 5_500  (constant in household.py)

  simulation/household_demand.py (update eac_multiplier_for_date):
    Current:  epc * (1 + ev_fraction) * (1 - solar_fraction)
    Phase F:  epc * (1 + ev_fraction + ashp_fraction) * (1 - solar_fraction)
    Where:
      ashp_fraction = hh.ashp_annual_kwh() / base_eac
    Note: EPC multiplier unchanged (building thermal demand; ASHP changes fuel not insulation).
    Combined effect with Phase D gas: from ASHP install date, gas drops 88%
    and electricity rises by ~5,500 kWh — net fuel-switching is modelled end-to-end.

  tests/simulation/test_phase_f_ashp_electricity.py (~16 tests):
    TestASHPElectricityKwh: gas-heated → 0, heat-pump-air → 5500, heat-pump-ground → 5500
    TestEACMultiplierASHPUplift: eac_multiplier higher for ASHP home, gas home same EPC
    TestASHPLifeEventEffect: before install → no uplift; after install → uplift applied
    TestASHPGasElectricityCombined: both gas reduction + electricity uplift from same event
    TestHouseholdDemandRegisterASHP: register eac_multiplier increases post-ASHP install

Fidelity delta:
  Any household that installs ASHP via life_events.py (heat_pump_installed event):
    - Electricity EAC increases by ~5,500 kWh from installation date
    - Gas AQ drops to 12% from installation date (already working, Phase D)
    - First time a single life event (heat_pump_installed) produces correct dual-fuel
      effects: gas settlement falls AND electricity settlement rises.
    - Electrification-of-heating P&L impact now visible in annual report.

Not in Phase F (later):
  EPC score improvement from heat pump (affects epc_consumption_multiplier — complex
  because it's a building + system combination; SAP calc not modelled)
  Ground-source vs air-source COP differentiation
  Seasonal COP variation (winter vs summer)
