**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `draw-microwave-ownership-at-efus-not-every-home-v2`

# A home owns a microwave at EFUS 2017's 89.7%, not always

Worker, 2026-10-09. Decided blind to company results: nothing below reads a company figure.
Continues `SEAT_FINDING_THE_MICROWAVE_LEVEL_IS_TIME_IN_USE_AGAINST_HES_56_2026-10-09.md` (fbf3e3ba2),
"Next". **Premise**, read at `origin/main` d5b89aaae: `owned_stock` draws the dishwasher, tumble dryer
and separate freezer only, so every home owns a microwave, at 1.70 uses a day since fbf3e3ba2. Live.

## What the sources say

- **EFUS 2011 Report 9, Table 14:** a microwave by persons 1/2/3/4/5+ = **80 / 83 / 85 / 82 / 87%**
  (n 734/907/424/365/186). Every 95% CI overlaps every other, and the report calls microwave ownership
  "fairly uniform across different type of households". National 82.6% (Table 13).
- **EFUS 2017, §4 and Table 4.1:** 89.7% of homes, up from 79.8% (2011 basis) and 73.9% (1998).
  "Ownership of ovens and microwaves did not vary by household characteristics."

**Which one is used, and why the by-size row is declined.** The item said to use a by-persons row
if one is published. One is, but it is a 2011 level that sits seven points below 2017. Its gradient
is inside its own sampling error. And the later survey states plainly that there is no gradient.
Rescaling the 2011 row up to 2017 would invent a shape that neither survey supports. So the share
is **national, 0.897**. The run window is 2016-2025, and 2017 is the nearer survey. Ownership is
probably still rising across the window (+10 points 2011 -> 2017). No later survey publishes it, so
it is held flat. That is marked in the code as a SIMPLIFICATION.

## Pre-registration (written before the run)

**Measurement.** `/tmp/cook/own.py`: 3,000 drawn premises (seeds 17/29/41, as of 2022-01-01),
residential only. A home's microwave year is `power x hours x uses x days`, times 1 if it owns one
and 0 if not. One variable: `microwave` enters `owned_stock` at 0.897.

**Predictions.**
1. Before: the population mean microwave year is **55.5-56.5**, and every home owns one.
2. After: **49.6-50.8** (0.897 x 56, plus or minus binomial noise on 3,000 homes). The change is
   **-5.2 to -6.4 kWh/yr**. The per-owner mean stays **55.5-56.5**, so
   `test_a_microwave_owners_year_is_hes_56_kwh` stays green.
3. The owned share is **0.887-0.907**, flat by size within sampling noise.
4. A non-owner still consumes its draws (`draw_appliance_events`), so **no other appliance moves**.
   Only the microwave-less homes change.
5. Pins: `test_premise_two_level.py` and `test_couple_fabric.py` move only where a pinned home is
   one of the ~10% that lose the microwave, or where a control aggregates over the panel. The panel
   texture moves through the lost 56 kWh, in either direction. I cannot say in advance which pins
   red. The draw for each home's microwave comes from a new substream (`owns::microwave`). So which
   panel homes lose it is fixed by the seed and cannot be predicted by reasoning.

**Decision rule.** Ship if 1-4 hold. If 1 misses, the base has moved, and I name the cause before
changing anything.

## Result (`/tmp/cook/own.py`, 3,000 residential homes, seeds 17/29/41, C1 2022)

| | Before | After (shipped) |
|---|---|---|
| Population mean microwave year | 55.99 | 50.49 (**-5.50**) |
| Per-owner mean | 55.99 | 55.98 |
| Owned share, persons 1/2/3/4/5+ | 1 / 1 / 1 / 1 / 1 | 0.911 / 0.900 / 0.900 / 0.889 / 0.892 (0.902) |

**Predictions graded.** 1 **held** (55.99). 2 **held** (50.49, -5.50; owner 55.98). 3 **held**
(0.902, flat by size within noise). 4 **held by construction**: the existing control
`test_an_unowned_appliance_never_runs_and_the_owned_ones_replay_exactly` asserts it for any owned
set.

**Control.** `tests/simulation/test_a_home_owns_only_the_appliances_efus_says_a_home_its_size_owns.py`
gains the microwave at 0.897 at each size, and in the reachable-and-nothing-else-drawn partition.
Mutation: delete `shares["microwave"]`, and 4 legs red.

## What the change redded

The same 30 files as fbf3e3ba2 (`/tmp/cook/files.txt`) were run at base d5b89aaae and after.
`test_rng_substream::test_no_new_private_seed_derivation...` (`sim/customer_state_layer.py`) and
`test_generate_value_arms_data::test_the_arms_substrate_covers_every_module_the_run_imports`
(`tools/dwelling_size_joint.py`) are **red at base**. They are not this change and are left alone.
One red is this change:

| Control | Base -> now | Disposition |
|---|---|---|
| L1.1n worst home | P0040 0.9955 -> P0040 1.039 | Re-pinned. P0040 is one of the four panel homes (P0034/P0040/P0047/P0059) that draw no microwave. 0 of 60 now read below their flat day. The rate leg passes. |

Prediction 5 **held**: the moves are confined to homes that lost the microwave. `test_couple_fabric`
stayed green, so none of its pinned homes moved past a tolerance. Four of the 60 panel homes have no
microwave (6.7%). That is below the 10.3% expected, but inside binomial noise at n=60.

## Not established

- Microwave ownership after 2017. It rose ten points 2011 -> 2017, and no later survey is found.
- The joint with income or tenure. EFUS 2017 says there is none for microwaves, so independence is
  the published reading here, not a simplification.
