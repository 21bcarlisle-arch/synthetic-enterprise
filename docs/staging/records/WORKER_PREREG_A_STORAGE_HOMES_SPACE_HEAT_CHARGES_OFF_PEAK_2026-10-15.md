**Severity:** ADVISORY · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Knowledge:** what-a-house-does-to-its-energy -- `docs/market_research/when_an_electrically_heated_homes_water_heater_runs.md` §1 E6, §6

# Pre-registration: a storage home's space heat charges off-peak (stream 1 of 2)

**Claim:** `a-storage-home-charges-off-peak-in-both-streams`
**Written before the build below was run.** The defect is
`docs/staging/WORKER_FINDING_THE_WORLDS_STORAGE_HEATER_IS_A_DIRECT_ACTING_HEATER_AND_CHARGES_NOTHING_OFF_PEAK_2026-10-15.md`.

## The one variable

Stream 1 only: where an `ELECTRIC_STORAGE` home's space-heat ELECTRICITY lands in the day. The room
physics are untouched — the heat is still released when the room calls for it, so
`heat_delivered_kwh`, the indoor temperature and the duty cycle are bit-for-bit what they were. What
moves is `fuel_kwh` (the metered draw): the day's total is charged across the off-peak window
(00:30–07:30, the earlier end of Element Energy §6's "12:30 or 1:00 am to 7:30 or 8:00 am"), with
SAP 10.2 Table 12a's high-rate fraction (0.00, "other storage heaters") left at the moments of demand.
Hot water (stream 2) stays at the draw in this step.

## Predictions

1. **Conservation.** Every home's daily electricity total is unchanged to 1e-9, so annual kWh and
   every daily statistic are unchanged. Non-storage homes are bit-for-bit unchanged.
2. **P0033's texture does not move.** The harness nets space heat at `heating_fuel_kwh`, and this step
   moves the meter and that field together, so every net-of-space-heat statistic (H38, L1.1 texture,
   the P0033 reversal 0.0869 → 0.0556) is bit-for-bit unchanged. The reversal is a water-stream
   question and stream 1 cannot touch it. If P0033's netted texture moves, the netting is reading
   something other than the field and that is a finding.
3. **The whole meter goes overnight-dominant.** P0033 on the drawn 60 (seed 17, C1 Jan–Apr 2022):
   its share of whole-meter electricity 00:00–06:00 rises from under 20% to over 40%. The LCL
   overnight-dominant cluster reads 51% annually; a winter window should reach it or exceed it only
   where space heat is most of the meter.
4. **Whole-meter population statistics move only through storage homes.** Any pinned measurement
   in `tests/harness/test_premise_two_level.py` that moves does so because a storage home's whole
   meter moved; none that is computed net of space heat moves.

## What would refute it

A moved netted statistic (2), a moved daily total (1), or a storage home whose overnight share stays
below 30% in Jan–Apr (3) — the last would mean its space heat is a smaller share of its winter meter
than assumed, which is itself worth knowing before stream 2.

## Results

Run 2026-10-15 in one process per arm on an `origin/main` worktree (068928f47), probe
`generate_premise_trace` over the drawn 60, before and after `fabric_physics.storage_charge_kwh`.
Only one home in the drawn 60 is a storage home (P0033); the other two electric homes are direct.

1. **Holds.** No home's daily total moved by more than 1e-9; 59 of 60 homes are bit-for-bit unchanged.
2. **Holds in substance, wrong in letter.** P0033's net-of-space texture moved 0.08689726861949118 →
   0.08689726861949089 (3e-16, float summation order); net-of-both 0.0556 unchanged. I predicted
   bit-for-bit; it is equal to the 15th digit, not bitwise. The P0033 reversal is untouched by
   stream 1, as predicted: it is a water-stream question.
3. **Holds.** P0033's whole-meter share 00:00–06:00: 0.043 → **0.522** (space heat is 63% of its
   Jan–Apr meter). That is the LCL overnight-dominant cluster's 51%, read here on a winter window.
   Its whole-meter texture falls 0.0826 → 0.0488.
4. **Holds** — only P0033 moved. The pinned harness measurements: see the commit.

**Not predicted, and worth carrying:** P0033's largest half-hour rises 8.55 → 8.78 kWh (17.6 kW),
the uncapped charge on the coldest day. Its direct-acting peak was already 17.1 kW because the
source is sized at 1.5× design loss; the stock's real storage input rating is NOT ESTABLISHED
(named beside `storage_charge_kwh`).

**Downstream.** The world demand digest moves 87d94399 → 2876e687 with this step (it reads the probe
homes' half-hourly meter). The value-arms lane's 10:22 re-take for 87d94399 had not started a unit;
the seat cancelled it and re-takes once, after both storage streams land
(`retake-the-blind-arms-after-the-storage-streams-land`, recorded in
`SEAT_PREREGISTRATION_THE_BLIND_ARMS_IN_THE_ACTIVE_USE_COUPLED_DEMAND_WORLD_2026-10-15.md`).
