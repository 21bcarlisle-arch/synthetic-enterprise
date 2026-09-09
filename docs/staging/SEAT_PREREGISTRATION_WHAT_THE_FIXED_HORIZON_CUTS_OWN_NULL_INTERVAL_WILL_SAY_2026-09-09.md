**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the honest concordance is published without the bound its sample earns) · **Class:** measurements_that_mirror

# PRE-REGISTRATION — what the fixed-horizon cut's OWN null interval will say

**Written 2026-09-09, before `concordance_null_spread` had ever been run on any leg of the
fixed-horizon bridge, and before the run that will carry those intervals was launched.** Nothing
below is a reading of an output. It is filed so the result can refute it.

Commissioned by the Lane 0 delivery item
`the-honest-concordance-is-published-without-the-bound-its-sample-earns`, which is item 3 of
`docs/staging/SEAT_RESULT_THE_UNSELECTED_CUT_IS_0_POINT_42_AND_THE_CENSORING_TERM_WAS_MISSING_FROM_MY_OWN_BRIDGE_2026-09-08.md`:

> **Neither cut clears its null.** 0.5337 sat inside [0.4494, 0.5503]; 0.4209 is below that
> interval, but the interval belongs to the *other* leg's population and this document does not
> borrow it. The estimand's own permutation null is not computed — `concordance_null_spread` runs
> on the concordance's points only. Until it is, **0.4209 is a point estimate with no bound of its
> own, and no claim that the arm ranks worse than chance is available from it.**

---

## The definition, written before the split

**The cause split follows from the definition; never let the definition be inferred from the
split.** So the readings are named here, before any interval exists to sort them into.

A concordance is a rank statistic on a stated population. Against the interval a signal carrying
**no information** reaches on **that population's own n**, exactly four things can be true, and a
page that does not tell them apart is a page that lets a reader pick:

| key | when | what it means |
|---|---|---|
| `this_run_cannot_tell` | there is no interval at all | nothing about the method can be read. Not a flat reading — **no reading**. |
| `not_distinguishable_from_no_information` | `low ≤ observed ≤ high` | the run cannot separate this figure from a signal carrying nothing. The director's own words apply: *we cannot tell*. |
| `worse_than_chance` | `observed < low` | the ranking is real and **inverted** beyond what a no-information signal reaches at this n. |
| `better_than_chance` | `observed > high` | the ranking carries information in the flattering direction. |

The first two are the pair a reader conflates, and they are opposite: one says the instrument
returned nothing, the other says the instrument had nothing to return. `detectability` already
separates *"a flat method"* from *"no instrument"* inside the second row and is published beside it.

The third and fourth exist so this is keyed to the **property** and not to today's answer: on the
day the arm starts ranking departures correctly, the same code says so with nobody editing it.

## What is being predicted

The four legs of `method_skill.fixed_horizon`, as measured by the run of 2026-09-08b
(`docs/observability/value_cycle_ab_s1_three_arm_20260908b.json`), are:

| leg | decisions | concordance |
|---|---:|---:|
| 0 `the_published_population_ratio_outcome` | 168 | 0.5338 |
| 1 `settled_only_ratio_outcome` | 124 | 0.4993 |
| 2 `settled_only_pounds_outcome` | 124 | 0.5130 |
| 3 `every_priced_decision_pounds_outcome` — **the estimand** | **161** | **0.4209** |

The published survivor concordance on that run is 0.5338 on 168 decisions with a permutation
interval of **[0.4494, 0.5503]** at p = 0.192 — half-width **0.0505**.

None of the four legs has ever been permuted. `concordance_null_spread` has only ever run on
`method_skill`'s own points.

### P1 — the estimand's interval will be WIDER than the survivor cut's

Half-width **between 0.050 and 0.075**, against the survivor cut's 0.0505 at n = 168.

Why: n falls from 168 to 161 (a 1/√n widening of about 2%), and 37 of the 161 decisions share one
outcome — the zero their term produced. `_concordance` excludes outcome-tied pairs entirely, so
666 of 12,880 pairs never enter the statistic and the effective sample is smaller than n suggests.

**I cannot predict the tie-driven part and am not pretending to.** The 37 zeroes tie with each
other but remain comparable with all 124 settled decisions, so whether the null widens by 2% or by
40% is a question about the permutation and not about arithmetic I can do here. The range above is
wide on purpose; a half-width outside it refutes P1.

### P2 — the estimand will read `worse_than_chance`

0.4209 will sit **below** its own lower bound. Under P1's widest half-width (0.075) the lower bound
is 0.425 and 0.4209 is still below it, though only just; under the narrowest (0.050) it is 0.450
and 0.4209 is clearly below.

**This is the prediction most likely to be wrong, and its failure is the more valuable outcome.**
A half-width above 0.079 puts 0.4209 inside its own null, and then the honest reading of the whole
2026-09-08 result is *not* "the arm ranks worse than chance" but "neither cut can be told from a
signal carrying nothing, and the direction of the point estimate is not evidence." That would
refute the reading of the direction I was handed, and it is why the page must render the verdict
the numbers compose rather than a sentence anyone types beside them.

### P3 — `p_two_sided` on the estimand will be below 0.05

Between 0.005 and 0.05. Tied to P2: if P2 is refuted this is refuted with it, and both fail in the
same direction, so they are **one** prediction with two readings and are graded as such.

### P4 — legs 1 and 2 will BOTH read `not_distinguishable_from_no_information`

0.4993 and 0.5130 on 124 decisions, against a half-width that must exceed the survivor cut's 0.0505
(fewer decisions). 0.4993 is 0.0007 from the null centre and cannot clear anything. 0.5130 is 0.013
from it and would need a half-width under 0.013, which n = 124 cannot buy.

If leg 2 clears its null, something is wrong with the permutation and not with the book.

### P5 — leg 0's interval will reproduce the published concordance's, within 0.005 on each end

**A CONTROL, NOT A FINDING.** Leg 0 is the concordance's own population and outcome rebuilt through
a different code path, so its permutation must agree — same points, same seed, same draws. It will
not agree *exactly*: `concordance_null_spread` shuffles a list whose initial order differs between
the two call sites, so the two are different 20,000-draw samples of the same distribution and will
differ in the third or fourth decimal.

A disagreement larger than 0.005 means leg 0's population is not the concordance's, which is a
defect in the bridge and not a fact about the book. It is exactly the check that caught the missing
censoring term on 2026-09-08.

### P6 — the null point stays exactly 0.5 on every leg, and the interval does not

`null_constant_signal_concordance` is a function of the signal alone and must stay at 0.5 (this
held on all four legs on 2026-09-08). The **interval** must move between legs, because it is a
function of the population. Two legs with different n carrying the same interval would mean the
interval was copied rather than computed, which is the defect the control landing with this work is
aimed at.

## What will NOT move, and why that is a separate claim

The four **point** estimates. Adding a permutation to each leg reads the leg's existing points and
writes a new key; it touches no population, no outcome and no ordering. If any of 0.5338 / 0.4993 /
0.5130 / 0.4209 moves in the run carrying this work, the change was not additive and the
attribution of everything above is void.

This is provable independent rather than merely conceptually separate: `_horizon_leg` computes
`concordance` from `points` before `concordance_null_spread` is called, and the spread function
takes `points` by value and mutates only its own copy of the signal list.

## How it will be graded

Against the run launched with this document — a full three-arm pass over 2016–2025, `--level-arm`,
the same book and the same world as the 09-08b run. Graded on `method_skill.fixed_horizon.legs`,
leg by leg, in a RESULT document beside this one, with each prediction's verdict written next to
the number that settled it.
