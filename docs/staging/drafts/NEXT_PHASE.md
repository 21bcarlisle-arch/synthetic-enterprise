# Phase 52 Proposal: ToU Demand Response Model

**The gap:** ToU pricing infrastructure is complete (Phases 49-51) — we know who is eligible,
we have the peak/off-peak rate structure. But ToU customers currently consume at the same
PC1/PC4 profile shape as standard tariff customers. There is no load-shifting. The distinctive
economics of ToU (peak shedding, off-peak uplift, supplier hedging benefit) are entirely absent.

**What to build:**

1. `saas/demand_response.py` — `DemandResponseModel` class:
   - `compute_shift_fraction(customer, year)`: returns fraction of peak-window consumption
     that shifts to off-peak. Basis: UK smart charging / Octopus Go study data (~10-20% typical,
     higher for EV owners). Parameters: `base_shift_pct` (15%), `ev_boost_pct` (+12% for EVs),
     `heat_pump_boost_pct` (+8% for heat pumps), year-varying as smart meter penetration grows.
   - `apply_demand_shift(hh_profile, peak_windows, shift_fraction)`: redistributes kWh from
     peak windows (16:00-19:00) to off-peak (23:00-07:00), conserving total consumption.
     Returns modified half-hourly profile.

2. Integration in `simulation/run_phase2b.py`: for ToU-eligible customers in each settlement
   half-hour, pass the HH profile through `DemandResponseModel.apply_demand_shift()` before
   calculating tariff revenue and wholesale cost. Non-ToU customers unaffected.

3. New per-customer settlement field: `demand_shifted_kwh` (total kWh moved peak→off-peak
   in the period), and `demand_response_benefit_gbp` (saving on wholesale cost from
   buying more off-peak volume at lower spot prices).

4. Tests (~12 new): shift conserves total consumption; non-ToU customers unaffected;
   shift fraction bounded [0, 1]; EV/heat pump boost applies only when asset present;
   year-varying penetration increases shift over time; demand_response_benefit_gbp positive
   in normal markets, negative or zero when off-peak spot exceeds peak.

**Business signal this unlocks:** Are ToU customers more or less profitable than
standard fixed-tariff customers after demand response? Is the supplier's hedging book
helped or hurt by peak-shifting (they bought forward at a peak-weighted average — if
customers shift load off-peak, actual delivery cost falls). This is the core Phase 5
thesis: smart tariffs + demand response = better margin for the supplier.

**Scope:** saas/ only (demand_response.py) + integration touch in simulation/run_phase2b.py.
No interface seam changes. Epistemic verifier compatible (company observes shifted meter reads,
does not see simulation internals).

**Estimated tests:** ~12 new (total → ~1,342 passing)
