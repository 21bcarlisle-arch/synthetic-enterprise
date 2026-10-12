**Severity:** RECORDED · **Lane:** W_world · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `world-2022-price-response-on-in-the-settled-book`

# Pre-registration: the settled book takes the SERL price response

Written 2026-10-11, before the switch is thrown or anything below is run. Follows
`SEAT_RESULT_A_PER_HOUSEHOLD_SERL_ELASTICITY_GETS_THE_2022_GAS_DISTRIBUTION_AND_MISSES_ELECTRICITY_AND_THE_CALENDAR_YEAR_2026-10-11.md`.
A baseline fidelity change, decided blind to company results. Not edited after the run.

## The change (one variable)

`fabric_demand_path.build_fabric_series_for_site` — the only door `run_phase2b` settles a fabric
premise through — passes `price_response=SETTLED_BOOK_PRICE_RESPONSE`, and that constant is `True`.
Nothing else in the trace moves. In the same landing, `premise_trace.comfort_constraint_for` loses
its unfed price leg (`_PRICE_ELASTICITY = 0.45` and the `unit_price_p_per_kwh` /
`reference_price_p_per_kwh` arguments). No production caller passed a price, so the leg's term was
`0.45 × max(0, 4.0/4.0 − 1) = 0` on every call: deleting it is an equivalence on every settled
volume, and only the one unit test that fed it a price can tell.

## What it moves, predicted

- **P1. Nothing before 2022-04-01.** Every premise's gas and electricity on every day before
  response year 2022 is byte-identical with the switch on and off.
- **P2. From April 2022, by the graded amounts.** Winter 22/23 gas reduction per premise has a median
  within sampling of the graded 11.7% (IQR 0.4–20.7) and electricity of 6.4%. The graded run used
  `build_fabric_series` directly; this asks the door the book actually settles through, so the
  prediction is the graded distribution itself, not a new one.
- **P3. The world stamp could not see this before, and must after.** The departure digest
  (`cdba75ebb9197b33`) and the home-stock digest (`35f8efe8ff02f245`) do not
  move: no departure rate and no house changes. The DEMAND digest, as it stands, also cannot move:
  its probe runs `premise_trace.generate_premise_trace` for one January week of 2020, beneath and
  before the layer the response sits in. So the switch would land with every world stamp unchanged
  and a value-arms bound taken before it would read as measured in the world after it — the
  2026-10-06 defect one layer up. The landing extends the demand probe to the response the settled
  book applies; the demand digest then moves (from `c20a2cd403410ed7`), and turning the switch off
  in-process moves it back.
- **P4. The value arms are not re-taken in this landing.** A re-take is ~53 min per pass and 3 passes
  per seed (~8 h for three seeds), past one turn. Every arm on disk is refused by
  `_blind_envelope_demand_refusal` once the demand digest moves, which is the honest state until
  they are re-run. Handed on as a continuation.

## Live stamps at write time

Printed by `world_level_identity()` on `ef7a52d5c` before the change: departure `cdba75ebb9197b33`,
homes `35f8efe8ff02f245`, demand `c20a2cd403410ed7`, payment methods `86560148d7db82b7`.
