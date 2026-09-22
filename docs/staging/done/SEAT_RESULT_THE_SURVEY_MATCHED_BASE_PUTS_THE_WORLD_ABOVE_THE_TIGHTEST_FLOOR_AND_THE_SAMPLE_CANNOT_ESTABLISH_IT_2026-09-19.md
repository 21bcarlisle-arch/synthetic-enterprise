**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the headcount denominator is not a survey base either"

# Result: the survey-matched base puts the world ABOVE the tightest annual floor, and 254 accounts cannot establish it

*`482be1a8a` landed the kind-matched band `[0.129630, 0.185887]`, straddling the tightest annual
floor `0.167616`. The straddle exists because the band's LOWER leg rested on one named assumption
rather than on a measurement. The measurement has now been taken. The band does not narrow — but
what stands in the way has changed from an unmeasured definition to a named sample size, and the
direction of the best-matched estimate is the opposite of what the published endpoint suggested.*

Pre-registered at
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_AN_EXPOSURE_RESTRICTED_INCIDENCE_NARROWS_THE_J_SVT_BAND_ENOUGH_TO_DECIDE_THE_TIGHTEST_ANNUAL_FLOOR_2026-09-19.md`,
filed before anything was run. Predictions marked in §5 below, beside the result and not over it —
**one of them is refuted.**

---

## 1. The directed restriction is a trap, and the trap is now measured

The direction asked for "distinct converters over accounts carrying at least some minimum fraction
of the window on the product". That restriction conditions the denominator **on the outcome**:
converting is what ends a stint, and `simulation/renewals.py` bounds a passive stint at the
household's next anniversary. Measured on the committed capture:

| | mean exposure |
|---|---|
| converting account-years | **0.3697** of a year |
| every other account-year | **0.7450** of a year |
| ratio | **0.496** |

So raising the threshold strips converters out faster than anybody else, by construction. The
directed sweep falls from `0.126984` at no restriction to **exactly zero at a full year** — a
session that ran it and published its last row would have reported that this world's internal
return rate is nought. It is published anyway, because its shape is the evidence that it must not
be used.

## 2. The outcome-independent restriction, which is the one a verdict may rest on

An account-year's **opportunity** is the fraction of the year between its first day on the product
and 31 December — fixed by when the account *arrived*, which no conversion can move. Restricting on
it removes late joiners, who are exactly who a survey's base also would not contain.

| ≥ of year | base | conv | incidence | exact 95% interval | × floor |
|---|---|---|---|---|---|
| 0.0 | 378 | 48 | 0.126984 | [0.095132, 0.164817] | 0.76 |
| 0.5 | 340 | 48 | 0.141176 | [0.105961, 0.182787] | 0.84 |
| 0.8 | 290 | 48 | 0.165517 | [0.124632, 0.213392] | 0.99 |
| 0.9 | 271 | 48 | 0.177122 | [0.133578, 0.227885] | 1.06 |
| **1.0** | **254** | **48** | **0.188976** | **[0.142747, 0.242626]** | **1.13** |

**The numerator survives the restriction whole** — all 48 converting account-years open on 1
January, because a stint that ends in a conversion started in an earlier year. That is an
EQUIVALENCE of this capture's term lengths and not a property of the method: shorten fixed terms so
a conversion can open and close inside one year and this leg starts losing numerator too. It is
derived, not written down, so that stops being silent.

`t = 1.0` is the closest thing this capture has to a survey base: accounts already on the product on
1 January, asked whether they converted during the year.

## 3. The three things this changes

**(a) The direction of the best-matched estimate is inverted.** The published lower endpoint sits at
**0.76×** the tightest annual floor. The survey-matched estimate sits at **1.13×** it — on the other
side of the bar. The published endpoint was not a slightly-too-low reading of the record's quantity;
it was 0.67× of it.

**(b) The pair is not a band.** `0.188976` **exceeds** the world's published event rate `0.185887`.
`J ≤ E` is an ordering between two readings of the *same* population; restricting the base changes
the population and nothing carries the ordering across. So the survey-matched figure does **not**
become the band's new lower endpoint, and `as_an_incidence_which_is_what_the_record_bounds` is left
standing entirely unchanged. `the_two_are_still_ordered` is derived and reports `False`.

**(c) The verdict still fails closed, for a better reason.** The point estimate clears the floor;
its exact Clopper–Pearson interval straddles it. The verdict is keyed to the interval, so
`clears_the_tightest_annual_floor` stays `None` — as does the new reading's own verdict. **What
stands in the way is now a sample size and not a definition**, and the reading says how large:
**1,215 account-years at this rate**, 4.78× the 254 we have, would put the interval's lower limit
above the bar. That is a materially different finding from "we cannot tell": it names what would
settle it.

## 4. A second defect, found on the way and reported beside the figure

`accounts_that_converted` is binned on the year a **stint** ends; `svt_accounts_touched` on the year
a **segment** falls in. A stint whose last segment starts in December and runs into January ends in
the next year — and if the account has no segment of its own in that year, the conversion lands in a
numerator year whose denominator does not contain it. **One such cell exists here**
(`SYN-2016-001@2019`), so the published `0.129630` is 49 over a 378 that contains 48 of them. Aligned
on the touched base the figure is `0.126984`.

The published endpoint is **not** overwritten. The difference is one account in forty-nine and the
direction is that the published endpoint is very slightly high; what is worth reporting is the
mechanism, which no future capture is guaranteed to keep this small.

## 5. The predictions, marked

| | prediction | outcome |
|---|---|---|
| **P1** | converter mean exposure below 0.6× the non-converter mean | **HELD** — 0.496× |
| **P2** | directed sweep non-monotone, reaching 0 at `t = 1.0` | **HELD** — exactly 0 |
| **P3** | `J_opportunity(t)` weakly increasing | **HELD** — 0.126984 → 0.188976 |
| **P4** | at the largest `t` with base ≥ 100, incidence still **below** 0.167616 | **REFUTED** — 0.188976, which is 1.13× the floor |
| **P5** | refutation of P4 requires the CP95 lower limit above the floor too | **NOT MET** — lower limit 0.142747 |

**P4 is wrong and is kept here wrong.** I predicted the survey-matched population would still sit
below the bar and it does not; I had the confound right and the magnitude backwards. The
*conclusion* P4 carried — the band does not narrow enough to decide the floor — survives, but
through P5 and not through P4, which is a different claim about the world: the world is probably
above that bar and this capture cannot show it, rather than below it.

## 6. What this cannot say

It cannot say the world clears the tightest annual floor. The interval straddles it and fails closed.

It cannot repair the last mismatch, which runs the **other way** and which nothing in this capture
bounds: CIM's base is households on the default tariff *at fieldwork*, asked to recall the past six
months — so a household that switched internally during the window may be outside the base that is
asked about it, while this base contains every account on the product on 1 January whether it stayed
or not. Named rather than estimated.

And it refutes nothing about the world either way. The tightest annual floor is the `r = 0` corner of
a family whose `r` is a declared `None` — the tightest bar the record *could* support, not one it
makes. The bound actually in force (`r = 1`, `0.044919`) is cleared on every base measured here.

## 7. Where it lives

* `tools/fit_year_level_anchor.py` — `_internal_return_incidence_by_its_base` and its helpers;
  published under `the_base_the_lower_endpoint_divides_by` and printed by `--internal-return`.
* `docs/reports/svt_internal_return_and_tenure.json` — the artefact.
* `tests/tools/test_the_incidences_denominator_is_measured_against_a_survey_base.py` — eleven legs,
  each naming its own defect. Eight mutations run against them; seven fired on the leg written for
  them, and **the eighth did not** — deleting the stray-cell filter left the alignment leg green.
  That was a missing test, not an equivalence, and the leg is now a partition (`inside + reported
  outside == every converting cell`) which no filter error can satisfy.
