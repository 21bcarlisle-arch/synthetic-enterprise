Phase D -- Gas EAC Integration with Household Demand Register

Status: BUILDING (2026-06-27, auto-session)

Context:
Phase C wired the household physical model (EPC, EV, solar) into electricity
settlement via eac_multiplier_for_date(). Gas settlement still uses static
declared AQ regardless of household insulation. The EPC band is the primary
driver of space heating demand -- for gas-heated homes it determines how much
gas is consumed, not electricity.

Gap: C1g (EPC-D, urban flat) bills at 12,000 kWh/yr whether the home is
poorly or well insulated. C4g (EPC-E, rural detached) at 22,000 kWh/yr.
A real supplier's gas AQ would reflect the home's EPC band.

What Phase D builds:

  simulation/household_demand.py (2 additions):
    GAS_HEAT_PUMP_RESIDUAL_FRACTION = 0.12  (cooking + hot water backup)
    HouseholdDemandRegister.gas_eac_multiplier_for_date(customer_id, date_str):
      I&C / non-residential: 1.0 (industrial gas, not EPC-driven)
      heat pump installed at date: GAS_HEAT_PUMP_RESIDUAL_FRACTION
      gas boiler (resi/SME): epc_consumption_multiplier()
      not in register: 1.0

  simulation/run_phase2b.py (3 lines in gas term block):
    After `aq_kwh = gas_customer["aq_kwh"]`, apply multiplier:
      _gas_mult = household_demand_register.gas_eac_multiplier_for_date(cid, term_start_str)
      aq_kwh = max(1, round(aq_kwh * _gas_mult))
    Multiplier captured at term signing; applies to full term (correct for annual gas contracts).

  tests/simulation/test_phase_d_gas_household_demand.py (~16 tests)

Fidelity delta:
  C1g (EPC-D):  12,000 -> 15,000 kWh (+25%). Poorly insulated 2-bed London flat.
  C2g (EPC-D):  15,000 -> 18,750 kWh (+25%). Poorly insulated 3-bed suburban semi.
  C3g (EPC-E):  14,000 -> 21,700 kWh (+55%). Cold tenement flat, poor insulation.
  C4g (EPC-E):  22,000 -> 34,100 kWh (+55%). Large rural detached, draughty.
  C_IC3g (I&C): 5,000,000 kWh unchanged. Process heat, not EPC-driven.

Total resi gas volume +42%. Gas P&L magnitude increases proportionally.
First time EPC band affects gas consumption. Connects household.py (Phase A),
life_events.py (Phase B), household_demand.py (Phase C) to gas_settlement.py.

Not in Phase D (later):
  Insulation-upgrade events improving EPC band mid-simulation (Phase E)
  Half-hourly EV load shape for ToU tariff impact (Phase E)
