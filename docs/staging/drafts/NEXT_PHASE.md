Phase C -- Household-Driven EAC Integration

Status: PROPOSED (2026-06-27T auto-session)
4h opt-out window: expires 2026-06-27T~12:00 BST

Context:
Phases A and B built the household physical model and life events engine.
These modules are 68 tests passing but currently dead code -- no simulation
path imports them. Every customer in a segment uses the same flat EAC
regardless of physical characteristics. EPC-G home = 2.2x segment average,
EPC-A = 0.75x. EV acquisition increases demand. Solar reduces net import.
None of this currently affects consumption or billing.

What Phase C builds:

  simulation/household_demand.py (new, ~120 lines):
    HouseholdDemandRegister:
      build_household_register() for all 18 customers at init
      generate_life_events() per customer 2016-2025 (seeded RNG)
      eac_multiplier_for_date(customer_id, date_str) -> float
        Composite: epc_multiplier * (1 + ev_fraction) * (1 - solar_fraction)
      household_at_date(customer_id, date_str) -> Household

  simulation/run_phase2b.py (2-3 line change):
    Instantiate HouseholdDemandRegister at simulation start.
    Multiply base consumption by eac_multiplier_for_date(cid, period_date).

Fidelity delta:
  C1 (EPC-D, no solar/EV): 1.25x segment EAC baseline
  C2 (EPC-C, EV ~2019): 1.0x + 2143 kWh/yr after acquisition date
  C3 (EPC-E, no assets): 1.55x segment EAC
  C4 (EPC-B, solar ~2020-2022): 0.75x * (1 - solar_fraction) post-install
  18-customer register, events over 2016-2025.
  2022 crisis figures diverge by EPC band.

Files:
  simulation/household_demand.py -- new module (~120 lines)
  simulation/run_phase2b.py -- 2-3 line change
  tests/simulation/test_phase_c_household_demand.py -- ~22 tests

Not in Phase C (later):
  Gas adjustment for heat pump installs (Phase D)
  Half-hourly EV load shape (Phase D)
  Company-observable EPC inference (Phase E)

Expected: ~22 new tests (4,648 total)
Connects to: household.py (Phase A), life_events.py (Phase B), run_phase2b.py
