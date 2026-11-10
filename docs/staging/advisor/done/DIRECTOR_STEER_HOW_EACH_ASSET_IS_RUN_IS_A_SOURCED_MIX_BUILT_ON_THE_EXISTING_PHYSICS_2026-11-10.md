**Severity:** LATENT · **Lane:** W · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] How each asset is run is a sourced mix, built on the existing physics (2026-11-10)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_A_REAL_RANGE_OF_PV_BATTERY_EV_AND_LOAD_IN_THE_WORLD_INSPIRED_BY_PREDBAT_2026-11-10.md`. The director's words, from chat on Tue 10 Nov:

- 19:37 GMT: "Its quite complex to simulate solar based on the weather, house load, battery based on schedule/modes or optimisation. And also EV based on driving and parking patterns plus schedules, or not (many don't) and optimisation if permitted. This needs knowledge first I'm guessing"
- 19:37 GMT, on the advisor's recommendation below: "Add it"

## 1. Build on what exists, never beside it

The physics is partly built. Read it first:
- `simulation/fabric_physics.py::reconstruct_irradiance_profile`: irradiance from the weather record;
- `simulation/premise_trace.py::pv_generation_kwh`: PV output by orientation against that field;
- `simulation/premise_trace.py::draw_ev_day`: miles driven, then a state-of-charge deficit, then a charge event. It plugs in below a threshold, "the single biggest" behaviour. It has an optional `smart_charging_window` and zero-mileage days.
- Knowledge pages: `pv-roofs-orientation-and-yield`, `solar-pv-and-home-batteries`, `ev-charging-and-the-saving-against-petrol-and-diesel`, `ev-solar-and-batteries-as-products`.

Extend these. A second PV model, EV-day model or battery model beside them is the several-homes class. The REUSE block must name them.

## 2. How each asset is run is the crux, and it is a population mix

The world must know not only who owns what, but how each asset is operated, because the mix decides the load shape a supplier sees:
- **Battery:** default solar self-consumption, a fixed schedule, tariff-optimised (an app, a Predbat-style planner or a supplier-managed service), or idle or misconfigured.
- **EV:** plug in and charge at once, a timer, supplier-managed smart charging where the household permits it, or charging mostly away from home. He notes "many don't" optimise.

The **shares** of each mode, and how they vary with tariff, tenure, age and tech-confidence, are knowledge to establish first: grade them, or carry them as a GAP with a range. Moving a household between modes, where it permits it, is a supplier lever. So the world needs the mode and its friction (willingness, hassle, the permission to control), and the value of that move must come out of the world, never be assumed.

## 3. Driving and parking

When the car is at home and plugged in, how mileage varies across households, weekdays and seasons, and off-street parking. Source this from the National Travel Survey (trip diaries) and published charging studies. `draw_ev_day`'s single plug-in threshold and zero-mileage probability become household traits drawn from those distributions, not world-wide constants.

## 4. The wall

The supplier sees only what a real supplier sees: half-hourly import, export where it is metered, and what the customer chooses to tell it. Asset settings, modes and the car's location never cross. Inferring "this home has a battery on a timer" from the meter is the supplier's work, and the world must make it inferable but not given.

## Order

Knowledge pages first (ownership and joint patterns; operating modes and their shares; driving and parking). Then switch on assets one at a time. Then modes. The invariant gate runs before publish at every step.

## Risk

Touches: the existing physics modules and their knowledge pages, and the population draw.
Blast radius: every run's population and load shapes. Re-baselining is expected.
Probable failure mode: mode shares invented to fill a slot, such as "50% smart", which would decide every personalisation result downstream. Every share is sourced, or carried as a ranged GAP.
Proportionality: contract-touching — implement with the named mitigations.

— Director steer, 10 Nov 2026, his words above; the code reading and drafting are the advisor's.

## Done

(seat executor, 10 Nov ~20:50 GMT.) **Seen; moved on the executor's instruction.** The executor refused this file:
its header names lane `W`, which is not a known lane. The director's words are quoted, so it was filed rather than
shelved: second of the three asset steers in `held_behind_the_exit_test` (`docs/direction/priority_order.yaml`),
after the range steer it adds to. It is step 8 work, knowledge first, as his 19:37 message says.
