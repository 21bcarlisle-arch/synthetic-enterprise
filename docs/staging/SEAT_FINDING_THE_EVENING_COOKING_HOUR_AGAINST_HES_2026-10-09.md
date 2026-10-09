**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `the-evening-cooking-hour-against-hes-fig-245`

# The cooking hour against HES: oven and hob move onto HES's own curves, microwave and kettle stay, and S2 falls 0.528 -> 0.495 with the peak moving 20:00 -> 19:00

Worker on the delivery seat's lane-0 item, 2026-10-09. Decided blind to company results: nothing
below reads a company figure. Pre-registration:
`docs/staging/records/SEAT_PREREG_THE_EVENING_COOKING_HOUR_AGAINST_HES_2026-10-09.md`, landed as
`611cae007` before any world-side run.

## The source

The item pointed at Fig 245's cooking bars, which cover all cooking in all households. HES also
publishes each cooking appliance's own curve, over its owning households: oven Figs 432–433, hob
Figs 440–441, microwave 444–445 and kettle 448–449. I used those instead. They were read by pixel,
and the reading reproduces HES's annual table: microwave 57 against 56, kettle 174 against 167,
oven 272 against 290, and hob 275 against 226. The hob curve rests on only 11 homes. The full
reading is in the pre-registration and in
`docs/market_research/the_seasonal_swing_of_a_gas_heated_homes_electricity.md` (last section).

## Predictions graded (same 2,431 gas no-PV homes, seeds 17/29/41, C1 2022, one process)

| # | Prediction | Result | |
|---|---|---|---|
| 1 | Oven share 18–24 0.55–0.70; share before 16:00 ≤ 0.05 | **0.731**; 0.032 | **range wrong (higher)**; rule crossed as predicted |
| 2 | Hob share 18–24 0.60–0.75 | **0.788** | **range wrong (higher)**; rule crossed as predicted |
| 3 | Microwave 0.25–0.38, inside the rule (HES 0.328) | 0.377 | held |
| 4 | Kettle 0.22–0.32, inside the rule (HES 0.229) | **0.325** | **range wrong by 0.005**; inside the rule (0.096) |
| 5 | Both moved: S2 −0.03 to −0.08, to 0.45–0.50, peak at 18:00–19:30; S1 < 0.003; S3 < 0.01; S4 < 15 | −0.033 → **0.4952** at **19:00**; 0; +0.0066; +1.8 | held |
| 6 | Oven alone carries ≥ ¾ of the S2 fall | −0.0281 of −0.0330 (85%) | held |

I underestimated how late the world cooks. The routine offset and the weekend shift push uniform
16:00–21:30 starts later still, and nothing can start before 16:00. Under HES's curves the world's
oven puts 0.461 of its day in 18:00–24:00 and 0.328 before 16:00 (HES: 0.358 and 0.378). The hob
puts 0.497 and 0.352 (HES: 0.410 and 0.388). Both are inside the rule, and both still sit a little
late. That residue is the household clock, which is not part of this change.

## The SERL cells (`fabric_gap_ledger.level_and_season_vs_serl`)

| Cell | Before | Oven alone | Hob alone | Both | SERL 2022 | Verdict |
|---|---|---|---|---|---|---|
| S1 trough | 0.1388 | 0.1388 | 0.1388 | 0.1388 | 0.125–0.135 | **FAIL, high** |
| S2 peak | 0.5282 at 20:00 | 0.5001 at 19:00 | 0.5197 at 20:00 | **0.4952 at 19:00** | 0.445–0.485 at 18:30 | **FAIL, high by 0.010** |
| S3 month max/min | 1.2201 | 1.2278 | 1.2239 | **1.2267** | 1.36–1.47 | **FAIL, flat** |
| S4 annual | 2,660 | 2,663 | 2,662 | 2,662 | crisis-free ≈ 2,674–2,717 | unjudged |

18:30 now reads 0.493. The total's half-hours from 16:00 to 22:00 (kWh/h): 0.391 0.407 0.469 0.489
0.513 0.520 0.525 0.524 0.515 0.500 0.481 0.454. That is a plateau from 18:00 to 20:00, the shape
HES describes ("flat from 17:00 to 20:00"), one hour late and about 0.01–0.04 high.

**S2 is still red, and no scalar is fitted to close it.** Across the two timing moves, S2 has closed
0.066 of its 0.076 excess over the band's top (0.561 → 0.495). What remains is about level, not
hour: the plateau is the right shape, a little too high and a little late.

## Not moved, and why

- **Microwave**: 0.377 against HES 0.328, inside the rule. Its curve is flat (max/median 1.02), so
  there is no peak hour to compare.
- **Kettle**: 0.325 against 0.229, a difference of 0.096. That is inside the rule by 0.004, and its
  world curve is flat (max/median 1.01). HES's kettle peaks at 07:00–08:00 (0.17 of its day), and
  the world's morning puts 0.08 there. **Named, not moved**: it sits on the rule's edge. A
  morning-peak read would be its own one-variable step, and it would move S2 down a little more.
- **Toaster**: no HES curve was read. It is 16 kWh/yr, all in the morning.

## Controls

- New: `tests/simulation/test_the_oven_and_hob_start_on_hes_hours.py`. It checks that the oven and
  hob carry HES's curve, that the world's share 18–24 for oven, hob and dishwasher is within the
  rule of the curve, and that a meal can be cooked before 16:00. I ran two mutations. Clipping the
  window back to (32, 42) with the curve kept reds 2 tests. A full revert reds 3.
- `tests/harness/test_premise_two_level.py`: I re-pinned each value that moved and attributed it by
  running the oven change alone, then the hob change alone. Texture counts [3, 13, 26, 45] →
  [3, 14, 27, 44]. The calm count 13 → 14 (P0054 joins). L1.2 worst P0023 0.563 → 0.530. Raw
  partialled r +0.623 → +0.461. L1.1n worst 1.048 → **1.337**, and the worst home changed from
  P0040 to P0006. That move is **not additive**: oven alone gives 1.077 and hob alone 0.977, both
  for P0040. A weighted start draws the day's random stream differently from a uniform one, so
  every later appliance's start time reshuffles too.
- The calmest judged home is gas P0018 again (0.0647), so
  `test_net_of_both_machines_no_electric_home_is_calmer_than_every_gas_home` passes again, and its
  strict xfail is removed. It is still a knife-edge, and its comment says so.
- `test_L1_1_texture_FIRES_when_the_trace_is_smoothed` required `after < before / 2`. At origin,
  home 0 passed that by only 0.02 (ratio 0.481). The move takes it to 0.583, because a cook on a
  repeated daily curve keeps its shape under a 7-day smoothing. The property the control exists for
  is that smoothing reds the population cell, and that still holds: all four quantiles are over
  expected. So the precondition is now `after < before`. A no-op smoothing still reds both legs.

## SIMPLIFICATIONS carried

- I used one all-days curve per appliance, (5 × workday + 2 × holiday) / 7. The world's weekend
  shift moves it, and HES's separate holiday curve is not used.
- A start is clamped to waking hours, so HES's small night share (about 0.03 for the oven) goes to
  the waking hours.
- The gas cooking meal clock (`cooking_period_kwh`) is gas, not electricity, and is out of scope.
  It still places a gas cook on the household's own evening clock and was not read against HES.

## Recorded, not mine

Across the 42 test files that reach the premise trace, 1,460 passed. One is red:
`tests/simulation/test_rng_substream.py::test_no_new_private_seed_derivation_and_no_stale_exemption`,
on `sim/customer_state_layer.py`'s `_substream` (from `5531ef8a6`). This change does not touch
`sim/`, and that red is already on `docs/staging/reference/HEAD_RED_REGISTER.md`.
