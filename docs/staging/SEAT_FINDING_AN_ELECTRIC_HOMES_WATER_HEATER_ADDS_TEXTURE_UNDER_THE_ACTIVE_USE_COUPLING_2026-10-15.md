# An electric home's water heater adds texture under the active-use coupling

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 3 · **Atom:** `W1_29_the_worlds_homes_are_drawn_too_alike_in_half_hourly_behaviour`

*Delivery seat, 2026-10-15, building `l2-4-the-active-use-rides-with-the-always-on-load`.*

## What was measured

Since this build, a home's active use rides with its always-on load (`pt.active_use_multiplier`,
β 0.7, measured from Low Carbon London; see the texture doc's 2026-10-15 build section). On the
drawn 60 (seed 17, C1 Jan–Apr 2022), the three electrically heated homes read:

| home | always-on | multiplier | net of space heat | net of space + water | at `active_use=1.0` (space → both) |
|---|---|---|---|---|---|
| P0008 | 59 W | 0.74 | 0.1052 | 0.1480 | 0.0998 → 0.1353 |
| P0020 | 98 W | 1.06 | 0.0909 | 0.1237 | 0.0923 → 0.1269 |
| **P0033** | **331 W** | **2.49** | **0.0869** | **0.0556** | 0.0519 → 0.0651 |

H38 says that netting the water heater RAISES an electric home's texture. That is a denominator effect:
the water heater adds few steps. P0033 (storage, five people) now does the reverse. Net of both machines
it is the calmest of the 60, below the calmest gas home (P0046, 0.0589). Three H38 legs in
`tests/harness/test_premise_two_level.py` are strict xfails on `_P0033_NETTING_REASON`.

## What is not established

- Which stream does it. One candidate is the storage home's water-heating draw meeting a ×2.49 active
  load, where steps that were the median's are now the water heater's. The other is a coupling too
  strong for an electrically heated home. LCL's 0.459 slope was read over whole-meter Std homes,
  electric-heated ones included. The summer slope (0.384) is the cleaner one, and it implies β ≈ 0.6.
- Whether it holds on other draws. One home on one seed is a home to diagnose (R4), not a prevalence.

## What would settle it

Decompose P0033's step distribution by stream, with and without the coupling: one variable, one home.
Then read the three-home pattern across seeds 18, 19 and 23. If electric homes go calm there too, rerun
the LCL slope on summer-only data per heating class (the sample carries no heating label, so use
night-to-day ratio as the proxy) before touching β.

## Pre-registration (2026-10-15, before any of the runs below)

*Delivery seat, `l2-4-an-electric-homes-water-heater-adds-texture-under-the-coupling`.*

Texture is median |step| ÷ mean. Taking the water heater out lowers the mean (H38's denominator
effect) and also removes the steps its draws make. A five-person home draws `round(5 × 1.4)` = 7 hot-water
events a day, so up to ~14 of 48 steps are the water heater's, not the "six in 47" H38 reasoned from.
If those steps are larger than the median, they move the median's RANK: with them in, the median is
roughly the p70 of the other steps, not their p50. That lift is large when the p50–p70 gap is large, and
the coupling widens that gap by scaling the switched banks and event sizes ×2.49 on top of a constant 331 W.

Predictions, written before running:

1. **Stream (one variable, P0033, seed 17).** Couple only the switched banks (lighting + electronics
   ×2.49, events at 1.0), then only the events (event rate ×2.49, banks at 1.0). The switched-only arm
   reproduces the reversal (net of both < net of space). The events-only arm does not.
2. **Mechanism.** At the coupled build, ≥ 20% of P0033's steps touch a water-heat draw. Net of space,
   its median step sits at the p65–p75 of its net-of-both step distribution.
3. **Water heater with no coupling elsewhere.** At `active_use=1.0` the reversal is absent (already
   measured: 0.0519 → 0.0651). This is not a prediction; it is the control.
4. **Other draws (seeds 18, 19, 23, n 60, the drawn-60 recipe).** The reversal appears in at least one
   electrically heated home on at least two of the three seeds, and it appears only in homes with
   ≥ 4 people. Net of both machines, an electric home is calmer than the calmest gas home on at least one
   of the three seeds.

If 1 holds and 4 holds, the cause is the statistic's median meeting a stream with many per-person draws.
That is a fact about the load set and the netting, not evidence that β is too strong for electric homes.
If 1 fails (events-only reproduces it), the coupling's event rate is the suspect and the LCL per-class
slope is the next run.

## Result (2026-10-15, same turn, at origin 1ca6dfcf5)

Probes: one home, generated four ways with `active_use` and the two switched-bank constants set
directly (seed 17). Then every home of the drawn-60 recipe on seeds 17, 18, 19 and 23, with
coupling and at `active_use=1.0`. Gas homes are read net of zero machines, as in the module.

**1. Stream. REFUTED.** Each arm alone reproduces the reversal:

| P0033, seed 17 | net of space | net of both | median step (space → both) | mean (space → both) |
|---|---|---|---|---|
| shipped (both coupled) | 0.0869 | 0.0556 | 0.0478 → 0.0243 | 0.550 → 0.437 |
| uncoupled | 0.0519 | 0.0651 | 0.0217 → 0.0199 | 0.419 → 0.306 |
| switched banks only ×2.49 | 0.0652 | 0.0542 | 0.0327 → 0.0211 | 0.502 → 0.389 |
| events only ×2.49 | 0.0689 | 0.0586 | 0.0322 → 0.0208 | 0.467 → 0.354 |

**2. Mechanism. REFUTED on the numbers, right on the shape.** 18.2% of steps touch a water draw,
not ≥ 20%. The net-of-space median sits at the p57 of the net-of-both steps, not p65–75. A seven-point
rank move is enough because the net-of-both step distribution has a cliff there: coupled p50 0.0243,
p70 0.1397. Just over half of P0033's steps are quiet ones: night, away, and the cold appliances. The
median sits on the edge between those and the active ones, and the water heater's seven draws a day
push it over. The coupling does not change the rank move (p56 uncoupled, p57 coupled). It makes the
active side of the edge taller, so the same move lifts the median 2× instead of 1.1×. The water draws
are not coupled (`draw_dhw_events` reads only headcount), so this is two streams meeting at the median.

**4. Other draws. REFUTED on both legs.** 16 electric homes over four seeds. The reversal occurs in 2:
P0033 (seed 17, 5 people, ×2.49) and P0049 (seed 23, 6 people, ×1.72). It is not on two of seeds
18/19/23. Both are 5+ people with a multiplier above 1.5; P0008 on seed 23 (5 people, ×0.74) does not
reverse. Uncoupled, 0 of 16 reverse. Net of both machines, no electric home is calmer than the calmest
gas home on seeds 18, 19 or 23 (P0049 is 4th of 60, P0039 10th).

| seed | calmest gas, coupled | uncoupled | electric homes | reversed | electric calmer than all gas |
|---|---|---|---|---|---|
| 17 | 0.0589 | 0.0647 | 3 | 1 | 1 (P0033) |
| 18 | 0.0554 | 0.0668 | 7 | 0 | 0 |
| 19 | 0.0596 | 0.0671 | 1 | 0 | 0 |
| 23 | 0.0537 | 0.0660 | 5 | 1 | 0 |

**Reading.** The pre-registration's fork resolves to its first branch. The cause is the statistic's
median meeting a stream with many per-person draws, and it needs a large active load to show. It is not
evidence that β is too strong for electrically heated homes. The coupling calms large-base homes
whatever their heating: the calmest gas home falls by 0.006–0.013 on every seed. Electric homes are not
calmed more than that. So the per-heating-class LCL slope rerun is **not indicated** and β stays at
0.7. The three H38 legs stay strict xfails, and their reason now says what was measured. They are true
statements the seed-17 draw violates, and they turn XPASS if the world changes what makes P0033 calm.

**What this exposes, filed as a GAP rather than built (K8).** The world heats an electrically heated
home's water at the moment of each draw, 1:1 (`_dhw_fuel_kwh`). That is the stream that does this.
The knowledge layer does not say when a storage-heated home's water heater runs. The industry
expectation is an off-peak immersion charging a cylinder overnight, and SAP 10.2's off-peak tables
are the place to establish it. If so, the meter carries a night block, not seven daytime draws, and
H38's denominator reading would hold by construction. It needs a knowledge page first. It moves the electrically heated homes:
16 of the 240 drawn here, 10 of them storage.

**Not done here:** the value-arms re-take after the world redrew (aa8a7c444). It is a separate
item: ≈53 minutes per seed pass.
