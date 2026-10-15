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
