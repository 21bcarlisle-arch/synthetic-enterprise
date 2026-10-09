**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `source-the-microwave-level-from-hes-26-vs-56`

# The microwave's level is short on time in use, against HES's 56 kWh a year

Delivery seat, 2026-10-09. Decided blind to company results: nothing below reads a company figure.
Continues `SEAT_FINDING_THE_COOKING_CLASS_DOES_NOT_SCALE_WITH_HEADCOUNT_IN_HES_2026-10-09.md`
(ecd94c38c), next step 1.

**Duplicate-work note.** The draw said this id was "already held" in `.seat_work_in_hand.json`. The
only `claude -p` process carrying it was this invocation (`ps`), so the claim was the draw's own
write. **Premise:** at `origin/main` ecd94c38c the microwave is still `0.9 kW x 0.10 h x 0.8/day`,
and nothing has landed on it since. The premise is live.

## What the sources say, and what they do not

- **HES (Intertek R66141, 2012) §11.8, p.319 and Table 14:** 56 kWh/yr per owning household, n=219.
  The microwave is "used throughout the day" (Figs 444-445), "commonly for reheating drinks and food".
  **HES publishes no uses a day and no energy per use for the microwave.** It is not in Appendix VI.
  The appliance index lists Figs 442-445 and nothing else. The item asked for an Appendix VI profile,
  and none exists.
- **DOE microwave SNOPR, Technical Support Document ch.7 (US):** 71 hours a year of active operation.
  That is carried from the 2008 cooking-products TSD and scaled by RECS 2005 survey frequency. It is
  US, and it is survey-derived, not metered. It is used here only as corroboration, not as a value.
- **ECUK 2023 A1/A2:** the microwave series is a 2010 projection (108 -> 98 kWh/appliance). It is not
  evidence of a trend, so no dating ratio is applied, as for the kettle.

**Which term carries the gap.** At the world's 0.9 kW, 56 kWh needs about 62 h/yr of use. The world
gives 0.8 x 0.10 h x ~365 = about 29 h. DOE's 71 h/yr is on the high side of 62, and nowhere near 29.
So the shortfall is **time in use, not power**. Time in use is uses a day x minutes a use, and **no
source found splits it.** The split is a judgement, and it is marked as one in the code:

- The duration is held at 6 minutes a use, already long for reheating, which is HES's stated
  dominant use.
- `events_per_day` carries the whole gap. The other option, 13 minutes a use, is the less plausible
  event for a reheat. The texture (event size) stays the same, and the event count rises.

## Pre-registration (written before the run)

**Measurement.** `/tmp/cook/est.py`: 3,000 drawn premises (seeds 17/29/41, as of 2022-01-01),
residential only, FLAT arm, on the book's census headcount. One variable: the microwave's
`events_per_day`, set to `0.8 x 56 / L0`, where L0 is the base FLAT level read in the same run.

**Predictions.**
1. Base FLAT microwave all-household: **26.0-26.6**, as ecd94c38c read it (26.3).
2. The refitted events a day: **1.68-1.72**.
3. After: the all-household level is **55.5-56.5**. That holds by construction, because the
   estimator is linear in the rate. This leg checks only the arithmetic.
4. Every type mean stays within **±1%** of the all-household mean. The shape RMS against Table 23
   is unchanged at **0.139 ± 0.002**, because a scalar on a flat term moves no shape.
5. The engine's meter: the population's mean annual kWh rises about **+28 to +32**. That is 30 a
   home, because every home owns a microwave in the world; see the ownership gap below. This is not
   measured by the estimator. It is graded only if a pinned control prints a mean.
6. `tests/harness/test_premise_two_level.py` reds some pins. Going from 0.8 to 1.7 a day adds
   `randint` draws inside each day's appliance substream. So every appliance drawn after the
   microwave (oven, hob, laundry) **re-shuffles** its start times, and texture pins can move from
   the RNG as well as from energy. I cannot predict which pins move. The strict calm-electric leg
   that passed by 0.03% is the one I expect most likely to red.

**Decision rule.** Ship if (1) to (4) hold. If (1) misses, the base has moved under me, and I
name the cause before changing anything.

## Not established (carried in the code, not filled)

- **The split of time in use into uses a day x minutes a use.** No HES, EFUS, DOE or ECUK figure
  found. HES's load curves (Figs 444-445) have no numeric labels to read.
- **Ownership.** The world gives every home a microwave. EFUS 2017 puts it at 89.7% (2011: 82.6%).
  HES's 56 is per owning home, so the world's population mean runs about 10% high on this term. That
  is a separate one-variable change: add `microwave` to `owned_stock`.

## Result (`/tmp/cook/est.py`, 3,000 residential homes, seeds 17/29/41, C1 2022)

| | HES Table 23 | FLAT before | FLAT after (shipped) |
|---|---|---|---|
| Microwave by type, all | 44 / 66 / 51 / 57 / 59 (56) | 26.6 / 26.2 / 26.6 / 26.3 / 26.2 (26.3) | 56.5 / 55.7 / 56.5 / 56.0 / 55.7 (56.0) |
| Max deviation of a type, shape RMS | | 0.009, 0.139 | 0.009, 0.139 |

**Predictions graded.**
1. **Held.** Base 26.3.
2. **Held.** 0.8 x 56 / 26.3 = 1.70. Shipped as `_MICROWAVE_USES_PER_DAY = 1.70`.
3. **Held.** 56.0.
4. **Held.** Within 0.9%, and RMS 0.139 unchanged.
5. **Ungraded.** No control re-taken here prints the population's mean meter.
6. **Held on "some pins red". Wrong on which.** The strict calm-electric leg I expected to red stayed
   green. The leg that redded was the L1.1 mutation's "same calmest home" leg, where P0018 and P0033
   sit 0.03% apart.

## What the change redded, and how each was taken

The same 30 files as ecd94c38c (`/tmp/cook/files.txt`). `test_rng_substream` is red at base, as
before. Every other red is below, and each was green at base. The extra microwave draws re-shuffle
every later appliance's start times in the day's substream. So each move below is energy and RNG
together, and **cannot be attributed to either alone**.

| Control | Base -> now | Disposition |
|---|---|---|
| Texture quantile counts | [3, 15, 27, 45] -> [3, 15, 27, 44] | Re-pinned. |
| Calmest home | P0018 0.0633 -> P0018 0.0647 | Re-pinned. |
| L1.2 worst home | P0023 0.555 -> P0023 0.527 (band 0.6) | Re-pinned. Still a gas home. |
| L1.1n worst home | P0040 1.025 -> P0040 0.9955 | Re-pinned. 1 of 60 below its flat day, against 7.0% of real LCL homes. The rate leg passes. |
| MINTS raw r | 0.619 -> 0.554 | Re-pinned. The partialled leg under 0.4 still holds. |
| L1.1 mutation: same calmest home | P0018 live, P0033 mutated | **Leg deleted, keyed to the property.** It pinned today's answer on a 0.03% tie. The kept leg (the minimum falls under the mutation) still reds on a no-op mutation. |
| `test_couple_fabric` affine triple | 16/17/18 not constant (D7 flips at 16.5) | Moved to 17/18/19 by its own guard. Swept at 0.5p, constant 16.5-21.5. |
| `test_couple_fabric` calmest panel home; homes under the real median | S9 0.0629 -> 0.0634; 8 -> 6 of 15 (expected 7.5) | Re-pinned. |

**New control:** `tests/simulation/test_a_microwave_owners_year_is_hes_56_kwh.py`. Two legs, each
mutation-proven alone:
- Use count back to 0.8: the level leg reds.
- A 0.2125 h use at 0.8 a day, which still gives 56: the reheat leg reds.

## Next (handed on)

**Microwave ownership.** Every world home owns one, against EFUS 2017's 89.7%. Add `microwave` to
`owned_stock` at 0.897. EFUS 2011 Report 9 may give it by size, so read that first. One variable, and
about -6 kWh/yr on the population mean.
