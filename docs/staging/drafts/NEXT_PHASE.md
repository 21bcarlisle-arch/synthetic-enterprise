# Proposed Phase MV -- Economic Life Events: Income Stress in the SIM

**Drafted:** 2026-07-01T12:05:00Z
**4-hour opt-out window expires:** ~2026-07-01T16:05:00Z
**Replaces:** EPC Fabric Efficiency proposal (already implemented in simulation/household_demand.py)

## Summary
Add economic life events (job_loss, income_recovery, new_baby, retirement_starts) to
the SIM life events engine. Wire these to an IncomeStress state on the Household
dataclass. The SIM now knows when a customer is under financial pressure -- the company
observes this only via payment timing (which Phase MW will wire). Human Simulation
Layer -- Dimension 2 (Economic), first increment.

## Why now
Physical life events (solar, EV, heat pump, boiler, insulation, smart meter) are all
modelled (Phases A-G of the simulation). The EPC consumption multiplier is live.
The remaining real gap is the economic dimension: the SIM has no model of income stress,
job loss, or financial shocks. The canonical HSL scenario (new baby + reduced income ->
payment timing slip -> company misreads as high-risk debtor) cannot happen in the SIM
because economic life events do not fire.

## Epistemic note
IncomeStress is SIM ground truth. The company cannot read it directly -- it observes
payment timing, complaint frequency, and debt escalation as downstream signals.
Consistent with SIM/company barrier.

## Calibration sources
- DWP STAT-Xplore: UK employee job loss rate ~2.2%/yr (2016-2024 average)
- ONS Birth Statistics: UK birth rate ~11/1000/yr -> ~1.1%/yr per household (resi)
- ONS LFS: retirement transition rate ~3.5%/yr for 55-65 age band
- Income recovery: median job loss duration ~4.5 months (ONS LFS 2023)
All calibrated to resi customers only; SME/I&C customers are exempt from economic events.

## IncomeStress state transitions
  LOW (default) --job_loss--> HIGH
  HIGH --income_recovery--> LOW (after ~5 months median)
  LOW --new_baby--> MODERATE (new baby + partner income reduction)
  MODERATE --income_recovery--> LOW (typically 12-18 months)
  LOW --retirement_starts--> MODERATE (initial adjustment period)
  MODERATE (retirement) --income_stabilised--> LOW (after 3 months pension stabilises)

## Files to modify
- `simulation/household.py`:
  - Add `IncomeStress(str, Enum)`: LOW / MODERATE / HIGH
  - Add `income_stress: IncomeStress = IncomeStress.LOW` to Household dataclass
  - Add `income_stress_at_events(events) -> IncomeStress` classmethod helper

- `simulation/life_events.py`:
  - Add to EventType: "job_loss", "income_recovery", "new_baby", "retirement_starts"
  - Add `_job_loss_probability(year, segment) -> float`: ~0.022 for resi, 0 for SME/I&C
  - Add `_new_baby_probability(year, segment) -> float`: ~0.011 for resi
  - Add `_retirement_probability(year, segment, build_era) -> float`: era-calibrated
  - Extend `generate_life_events()` to fire economic events alongside physical ones

- `simulation/household_demand.py`:
  - Add `income_stress_at_date(customer_id, date_str) -> IncomeStress` method
    (reads from household_at_date, returns LOW if customer not in register)

## Files to create
- `tests/sim/test_phase_mv_economic_life_events.py` -- 20 tests:
  - IncomeStress enum has LOW/MODERATE/HIGH
  - EventType includes job_loss, income_recovery, new_baby, retirement_starts
  - job_loss_probability_resi_nonzero
  - job_loss_probability_sme_zero (SME exempt)
  - new_baby_probability_resi_nonzero
  - retirement_probability_pre_1919_higher (older cohort retires sooner)
  - generate_life_events_can_fire_job_loss (seeded RNG, verify at least 1 in 100)
  - job_loss_event_transitions_to_HIGH
  - income_recovery_after_job_loss_returns_to_LOW
  - new_baby_transitions_to_MODERATE
  - income_recovery_after_baby_returns_to_LOW
  - retirement_transitions_to_MODERATE
  - income_stabilised_returns_to_LOW
  - no_economic_events_remains_LOW
  - income_stress_at_date_unknown_customer_returns_LOW
  - income_stress_at_date_after_job_loss_date_is_HIGH
  - income_stress_at_date_before_job_loss_date_is_LOW
  - multiple_events_replay_in_order
  - sme_customer_no_economic_events
  - stress_does_not_affect_existing_physical_events (independence)

## Target
20 new tests, total 13,053.

## Impact
The SIM now models income shocks. Phase MW (to follow) will wire IncomeStress to
payment timing in the settlement loop. The canonical HSL scenario becomes possible:
job_loss fires in month 3, customer transitions to HIGH stress, late payment in
month 4, company observes (not reads), and service layer must respond correctly.
