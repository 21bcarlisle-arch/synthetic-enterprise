# Proposed Phase MV -- EPC Fabric Efficiency: Heating Demand Now EPC-Dependent

**Drafted:** 2026-07-01T11:40:00Z
**4-hour opt-out window expires:** ~2026-07-01T15:40:00Z
**Replaces:** Coverage Depth Sprint CXX proposal (coverage sprint; lower impact)

## Summary
Wire EPC rating into `simulation/demand_model.py` so that heating demand scales
with insulation quality. EPC A customers use ~25% of the heating load of EPC G.
Human Simulation Layer -- Dimension 1 (Physical), first increment.

## Why now
Gaps 1 (real forward curve) and 2 (Triad curtailment) are closed. Gap 3
(Human Simulation Layer) is the only remaining capability gap. Coverage sprints
add tests to existing working code; this adds a real physical relationship.

The demand model (`simulation/demand_model.py`) already reads `property["epc_rating"]`
from the property dict but does NOT use it -- GAS_HEATING_KWH_PER_DEGREE_DAY is
a flat constant applied equally to all customers regardless of insulation.

Real UK data (BRE/EPC Register): EPC A heat demand ~40 kWh/m2/yr,
EPC D (UK average) ~110 kWh/m2/yr, EPC G ~250 kWh/m2/yr. These ratios
give EPC fabric scalars relative to D: A=0.36, B=0.55, C=0.73, D=1.00,
E=1.36, F=1.82, G=2.27.

## Epistemic note
EPC rating is observable (public EPC Register). The company sees the customer's
EPC rating and will observe higher-than-expected winter consumption from EPC G
customers. The fabric scalar itself is a SIM internal -- company cannot read it
directly (consistent with SIM/company barrier).

## Files to modify
- `simulation/demand_model.py`:
  - Add `EPC_FABRIC_SCALAR: dict[str, float]` (A-G + fallback)
  - Modify `build_demand_shape()` to multiply heating extra by
    `EPC_FABRIC_SCALAR.get(property.get("epc_rating", "D"), 1.0)`

## Files to create
- `tests/sim/test_phase_mv_epc_fabric.py` -- 16 tests:
  - epc_fabric_scalar_has_all_ratings (A through G)
  - epc_A_below_1 (A customers use less than baseline)
  - epc_D_is_1 (D is the baseline)
  - epc_G_above_2 (G customers use more than 2x baseline)
  - ordering_A_lt_B_lt_C_lt_D_lt_E_lt_F_lt_G
  - unknown_epc_fallback_is_1
  - gas_build_demand_epc_A_less_than_epc_G (high HDD scenario)
  - gas_build_demand_epc_D_baseline
  - gas_build_demand_zero_hdd_epc_irrelevant
  - elec_heat_pump_epc_A_less_than_epc_G
  - gas_epc_A_vs_G_ratio_approx_correct (ratio within 10% of scalar ratio)
  - property_without_epc_key_falls_back
  - build_demand_shape_unchanged_for_no_heating (cooling-only day)
  - build_demand_shape_gas_peak_periods_correct (heating lands in morning/evening)
  - occupancy_multiplier_still_applied_after_epc_scaling
  - solar_still_subtracted_after_epc_scaling

## Target
16 new tests, total 13,049.

## Impact
Every simulated customer's winter gas bill now reflects their actual insulation
quality. EPC G customers cost the supplier more in cold winters (higher volume
risk). EPC A customers are lower-risk but also lower-revenue. Opens the door to
tariff differentiation by EPC band (a real UK pricing strategy).
