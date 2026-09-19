**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery,
"the headcount denominator is not a survey base either"

# Pre-registration: does an exposure-restricted incidence narrow the `J_svt` band enough to decide the tightest annual floor?

*`482be1a8a` landed the kind-matched band `[0.129630, 0.185887]`, and it STRADDLES the tightest
annual floor `0.167616`, so `clears_the_tightest_annual_floor` is honestly `None` where it used to
read `True`. The band is wide because its LOWER leg rests on one named assumption rather than on a
measurement. This is filed before taking that measurement.*

**Filed 2026-09-19, delivery seat, Lane 0, BEFORE running anything over the capture.** Claim
`svt-band-the-headcount-denominator-is-not-a-survey-base-either`.

**Subject:** `tools.fit_year_level_anchor._internal_return_as_an_incidence` — specifically
`incidence_per_svt_account_touched`, the band's lower endpoint, and the sentence that licenses it:
*"`accounts_touched` includes accounts on the product for weeks, which dilutes the incidence
downward."* That sentence is a DIRECTION claim, and nobody has measured its SIZE.

---

## 0. What is being asked, in one line

The record's denominator is a survey's point-in-time default-tariff base: households on the product
**at fieldwork**, each carrying a full window's opportunity to have switched. The world's lower
endpoint divides by `svt_accounts_touched`: every account that was on the product for **any** part
of the calendar year, including one that was on it for six weeks. Those short-stay accounts sit in
the denominator and (mostly) not in the numerator, so they dilute the incidence downward — which is
why `J_touched` is a LOWER bound and not the quantity.

The direction drawn says: restrict the denominator by exposure, sweep the threshold, and see
whether the lower endpoint rises far enough to clear `0.167616` and collapse the straddle.

## 1. The confound I expect to dominate, named BEFORE the sweep

**Conversion terminates exposure.** `_svt_stints` bins a conversion on the year the stint ENDS, and
`simulation/renewals.py` bounds a passive stint at the household's next anniversary. So an account
whose anniversary falls in March and which converts there carries roughly **0.21 of that calendar
year** on the product — and that is the year its conversion is counted in. An account that does NOT
convert keeps accruing days to 31 December.

So the directed restriction conditions the denominator **on the outcome**: raising the threshold
removes converters faster than it removes non-converters, by construction and not by anything about
the world. This is the same shape as `docs/design/CONTROLS_THAT_CANNOT_FAIL.md`'s selection traps —
a filter that empties the evidence in the direction that flatters, except here it runs the other
way and would make the world look WORSE than it is.

**Therefore two measures, not one**, and the second is the one any verdict may rest on:

* **`J_exposure(t)`** — as directed. Distinct converters over accounts carrying at least `t` of the
  calendar year on the product, both numerator and denominator restricted to the same set. Reported
  because it was asked for, and because its shape is the evidence for or against §1.
* **`J_opportunity(t)`** — outcome-independent. An account-year's **opportunity** is the fraction of
  the calendar year between its FIRST SVT day that year and 31 December. That is fixed by when the
  account ARRIVED on the product, which no conversion can move. Restricting on opportunity ≥ `t`
  removes late joiners — the accounts a survey's base would also not contain — without removing
  anybody for having converted.

`J_opportunity(1.0)` is the closest thing this capture has to a survey base: accounts already on the
product on 1 January, asked whether they converted during the year.

## 2. Predictions, sharp, before anything runs

**P1 (mechanical, the confound).** Mean exposure among account-years that CONVERTED is strictly
below mean exposure among account-years that did not — and by a wide margin, not a whisker. I
predict the converter mean lands **below 0.6** of the non-converter mean.

**P2 (the directed measure fails, and for that reason).** `J_exposure(t)` is **not** monotonically
increasing. It falls over most of the upper range and reaches **0 at t = 1.0** — no account that
converted carries a full year of exposure in the year it converted. Consequence: the directed
restriction cannot raise the lower endpoint at all, and a naive reading of it would have moved the
band the WRONG WAY.

**P3 (the honest measure, direction).** `J_opportunity(t)` is weakly increasing in `t`.

**P4 (the honest measure, magnitude — the one the verdict turns on).** At the largest `t` whose
denominator still holds at least **100 account-years**, `J_opportunity(t)` is still **below**
`0.167616`. So the band does NOT narrow enough, and `clears_the_tightest_annual_floor` stays `None`.

**P5 (what would refute P4).** `J_opportunity(t) > 0.167616` at some `t`, **with its exact
Clopper–Pearson 95% lower bound also above `0.167616`**. A point estimate above the floor on a thin
denominator is not a decision; it is a coin. This criterion is fixed here so it cannot be relaxed
after the numbers are seen.

## 3. What the answer may NOT be used for

* It may not mint a point inside the band. `SVT_INTERNAL_CONVERSION_RATE` refuses to be a constant
  and this cannot become one by arriving through a threshold sweep.
* A threshold chosen because it produces a clearing verdict is a fitted number. If the sweep clears
  the floor at exactly one `t` and nowhere else, that is a NEGATIVE result and will be reported as
  one.
* Whichever way it lands, it says nothing about the world being right or wrong. The tightest annual
  floor is the `r = 0` corner of a family whose `r` is a declared `None` — the tightest bar the
  record COULD support, not one it makes. The bound actually in force (`r = 1`, `0.044919`) is
  cleared by both endpoints either way.

## 3a. MARKED AGAINST THE RESULT, 2026-09-19, after the measurement

*Written here beside the predictions and not over them. Result:
`docs/staging/SEAT_RESULT_THE_SURVEY_MATCHED_BASE_PUTS_THE_WORLD_ABOVE_THE_TIGHTEST_FLOOR_AND_THE_SAMPLE_CANNOT_ESTABLISH_IT_2026-09-19.md`.*

* **P1 HELD.** Converter mean exposure `0.3697` against `0.7450`, a ratio of `0.496` — inside the
  predicted `< 0.6`.
* **P2 HELD.** `J_exposure(1.0)` is exactly `0`. The directed restriction measures the recorder.
* **P3 HELD.** `J_opportunity` rises monotonically, `0.126984` → `0.188976`.
* **P4 REFUTED.** I predicted the survey-matched incidence would still sit below `0.167616` at the
  largest usable threshold. It is `0.188976` — **1.13× the floor, on the other side of the bar**. I
  had the confound right and the magnitude backwards, and the error was in the direction that made
  the published endpoint look more nearly correct than it is.
* **P5 NOT MET**, which is what keeps the verdict `None`: the exact 95% interval is
  `[0.142747, 0.242626]` and its lower limit is below the bar.

**So the conclusion P4 carried survives and the claim underneath it does not.** The band still
cannot decide the tightest annual floor — but the reason is a sample size (1,215 account-years
would settle it, 4.78× what the capture has) and not the definitional gap P4 asserted. "The world
is probably above that bar and this capture cannot show it" is a different statement about the
world from "the world is below it", and I filed the second.

## 4. Done means

A reading on disk, in the artefact the band already lives in, carrying the sweep, the confound
measurement that grades the directed measure, the Clopper–Pearson bound on each endpoint, and a
three-valued verdict that FAILS CLOSED. Plus this file's predictions marked against the result,
beside them and not over them.
