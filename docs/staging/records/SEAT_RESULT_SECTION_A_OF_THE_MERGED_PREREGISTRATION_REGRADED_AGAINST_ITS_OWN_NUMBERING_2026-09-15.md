**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:**
`W2_29_the_coverage_is_re_measured_against_the_demand_vector`

# RESULT — §A of the merged pre-registration, graded against its own numbering: 4 hold, 1 is ungradeable, 0 fail

**Filed 2026-09-15, delivery seat.** Grades **§A** of
`SEAT_PREREGISTRATION_WHAT_CHOOSING_THE_SETTLED_SAMPLE_FOR_DIFFERENCE_MOVES_2026-09-11.md` — the
arm filed on the shared tree's side of the 09-11 origin fork, against fitted-joint homes.

**No new arm was run.** This is a re-grade of predictions that were already answered by measurements
filed on 2026-09-11, against the numbering and the bands §A actually used. Every number below is
read from
`SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` and
`SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md`. Nothing here
is a fresh measurement and nothing here re-bands anything.

---

## Why this file exists

The merged pre-registration holds two documents. **The grading that was filed graded §B — by name
and by band.** Its table reads "≥1.25×, kill below 1.10×" and "distinct fabric vectors ≥70", which
are §B's bands and not §A's. §A's P1 band is **[1.2×, 2.0×]**, its P2 is about **per-year shares**,
and it makes no prediction about distinct vectors at all.

So §A was graded **only by coincidence of content** — the measured 1.553× happens to fall inside
§A's band too, §A's P4 is §B's P7, §A's P5 is §B's P4 — and a reader could not follow any of that
from either document. A pre-registration graded by coincidence looks complete and is not. That is
what this file closes.

## The grading — §A's five predictions, §A's numbering, §A's bands

| | §A's prediction, as written | measured | |
|---|---|---|---|
| **P1a** | worst-axis KS ratio in **[1.2×, 2.0×]** | **1.553×** | **HOLDS** |
| **P1b** | the gain is concentrated on the **fabric axes** rather than on cost | not measured per axis | **UNGRADEABLE — see below** |
| **P2** | unweighted per-year shares move **>5pp** on at least one year; and the weights must reconstruct proportionality or the change is **refused** | 2017 at +84.9% relative (≈5.9pp of share); reconstructed to **0.1%** after the repair | **HOLDS, and the acceptance test is met by a repair** |
| **P3** | the settled count changes, so every published financial figure moves; **sign not predicted** | 90 → 84 settled; gross margin **−2.45%** | **HOLDS** |
| **P4** | the null case is byte-identical | identical but for two added keys | **HOLDS, corrected** |
| **P5** | the budget guard still binds; a dearer chosen set settles **fewer** accounts and that is correct | 84 settled, 1197.0 of ceiling 1200.0 | **HOLDS as pre-committed** |

> **EVERY FIGURE IN THE `measured` COLUMN IS A STATISTIC ABOUT THE HOMES, AND ITS BASE IS
> `3957ba848`, NOT THIS TREE** (noted 2026-09-15; cause established the same day in
> `SEAT_RESULT_P1B_IS_STILL_UNGRADEABLE_BECAUSE_THE_FILED_EVIDENCES_WORLD_IS_GONE_2026-09-15.md`).
> This file regrades §A against the evidence filed by
> `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md`, whose base is `3957ba848`,
> and `0d86d6dfe` — *"the world's homes are drawn from the fitted joint now"* — is **not an ancestor
> of it**; it arrived through the fork-closing merge `2212d0eed`. On today's base the same
> measurement gives worst-axis KS **0.09765 / 0.05878 → 1.661×**, arm B settles **83 at 1199.2**,
> and the population holds **105** distinct fabric vectors.
>
> **THE GRADING VERDICTS ARE UNCHANGED — this is a note about the numbers, not the column of
> HOLDS.** P1a's [1.2×, 2.0×] contains 1.661× as well as 1.553×, so it holds on either base; P3 and
> P5 hold on either. Two things in the column below do not carry over and are marked here rather
> than revised:
>
> * **the 109-distinct-vector ceiling, which §B's P2 failure surfaced and this file repeats as a
>   fact about the candidate population.** It is 105 on this tree. Of everything in this file it is
>   the figure most likely to be quoted forward as a standing property of the world, and it is the
>   one that moved.
> * **1.553×, the 84 / 1197.0, and the −2.45% carried in from P6.** Each is a real measurement on
>   `3957ba848`. None is a current figure, and −2.45% additionally carries the caveats already on
>   `SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md`.
>
> Nothing here is re-run. The base is named because re-running would grade a pre-registration filed
> against one world on another, and the whole point of §A's regrading was that the band and the
> evidence must be the ones that were actually written down.

### P1a — HOLDS, and §A's band was the looser one

1.553× is inside [1.2×, 2.0×]. It is also above §B's ≥1.25×. Both arms pass on this number; §A had
more room.

### P1b — UNGRADEABLE, and it is recorded as ungradeable rather than waved through

§A's P1 has a second clause that §B has no counterpart for: *"I predict the gain is concentrated on
the fabric axes (floor area, heat-loss coefficient, remaining insulation ceiling) rather than on
cost."* **The filed evidence reports worst-axis KS and not per-axis KS, so this clause cannot be
graded from it.** Grading it needs a per-axis run of both arms, which is a measurement and not a
reading, and inventing a verdict from "the worst axis improved" would be exactly the substitution
this file exists to end.

Two things are worth recording beside it:

* **§A named an axis that is not on the axis list.** The shipped choosing axes are floor area,
  fabric W/K, raw infiltration ACH and `customer_years`. There is no "remaining insulation ceiling"
  axis, so that third of P1b's fabric set has no column to be graded on and never had one.
* **§A's "rather than on cost" is answerable in principle and interesting**, because `customer_years`
  — the cost axis — later became a *constraint* rather than an axis (§B's P3 repair). A per-axis
  grading run before and after that repair is the honest way to take it.

**This is unrun work and is named as such**, not carried as a hold.

### P2 — HOLDS on both clauses, and the second one only after a repair

§A's first clause is in **percentage points of share** and the filed measurement is in **relative
error against each year's funnel wins** — two different units, and they are not silently equated
here. 2017 carried 35 of the 502 funnel wins (6.97% share) and was reconstructed at +84.9%, i.e.
≈64.7 wins against an exact campaign total, ≈12.89% share. **That is a move of ≈5.9pp, which clears
§A's >5pp bar** — and the unconstrained arm's worst-year error of 72.8% puts the clause beyond
argument whichever unit it is read in.

§A's second clause is an **acceptance test**: *"the per-account weights must reconstruct the per-year
proportionality; if they cannot, the change is refused."* They could not on the first measurement
(+84.9%) and they can now (**0.1%**) — but only because the year marginal was moved from an axis to
a constraint (`fit_weights(groups=...)`). **So the acceptance test is met by the repaired design and
was failed by the design as §A described it.** §A also pre-named the fallback — *"keep the year
stratification and choose for difference WITHIN each year"* — and that fallback was **not** the one
taken; the constraint is a third route neither document named in advance. Recorded because a
pre-registration whose acceptance test is met by an unnamed third option is a weaker instrument than
one that predicted the route, and saying so is the point of grading it at all.

### P3 — HOLDS, with its stated baseline belonging to a different base

The prediction's content holds: the settled count moved (90 → 84) and the P&L moved with it
(−2.45% gross, −5.75% net). §A explicitly declined to predict the sign, and the measured sign is
**against the change** — so the non-prediction was the right call and is not retro-fitted here.

**But §A quoted its baseline as "582 commercial, 173 settled, 91 of 500 wins settled, 409 refused",
and the measurement was run on `origin/main`'s base, which reads 502 / 90 / 17.96% / 412.** Those
are the shared tree's figures against the promoted base's. The merge that carries the
pre-registration is what put the fitted-joint homes and the chooser on one base, and the
two-bases caveat both documents carry expired there — so P3's *content* is gradeable on the graded
base, while its *quoted numbers* are not that base's. Stated rather than quietly reconciled: this
is the two-bases-differenced shape, and the safe reading is that P3's direction holds and its
absolute baseline should not be quoted forward.

### P4 — HOLDS, and §A's wording needs the same correction §B's did

§A wrote *"A run at 13 founders must be byte-identical to HEAD."* Measured: rate 1.0, all winners in
the same order, no settlement note, every pre-existing field identical — but `by_year` gained
`settlement_weight` and `settlement_selection`, and the outcome gained `settlement_selection` and
`settlement_weights`. **Additions, not changes** (1.0, `"uniform_count"`, all-ones under the null).
The correction filed against §B's P7 applies verbatim to §A's P4, whose wording is equally strict,
and it is repeated here rather than left to be inherited by a reader who only opens §A.

### P5 — HOLDS as pre-committed, which is the strongest form

§A wrote the outcome in advance: *"If the chooser's set is dearer than the cull's, fewer accounts
settle, and that is the correct outcome rather than a bug."* Measured: **84 settled against the
cull's 90, at 1197.0 of a 1200.0 ceiling that was never crossed.** The count fell, the ceiling held,
and §A had already said that shape was correct — so the drop could not be, and was not, read as a
defect after the fact.

## The finding this re-grade produces, and it does not flatter §A

**§A scores better than §B — 4 holds and no failures against §B's 6 holds and 4 failures — and that
is not §A being more right. It is §A being less falsifiable on exactly the two points where the
measurement found real defects.**

* §B's **P2** (distinct fabric vectors ≥70) failed at 59, and that failure is what surfaced the
  **109-distinct-vector ceiling in the candidate population** — a fact nobody had measured. §A
  predicted nothing about distinct vectors, so §A cannot fail there and learns nothing there.
* §B's **P3** (every year within ±25%) failed at +84.9%, and that failure is what caught **a correct
  headline over a false growth curve**. §A's P2 covers the same ground in a looser unit and with no
  numeric band on the reconstruction, so §A would have recorded "the weights reconstruct it" and
  moved on.

**A wider band is not a better prediction; it is a cheaper one.** §A's P1 band [1.2×, 2.0×] admits
1.553× and so does §B's ≥1.25×, but §B additionally pre-committed a kill line at 1.10× and §A did
not — so on a bad result §A had no pre-registered refusal to be held to. The one place §A is
genuinely stronger is **P5**, where it pre-named the fewer-accounts outcome as correct, and **P1b**,
where it made a per-axis claim §B never made — and P1b is the one clause nobody has measured.

## What this does NOT claim

* It does not re-open any §B grading. Those verdicts stand exactly as filed.
* It does not re-band anything in §A. §A's bands are quoted as written and graded as written; where
  a unit differs from the measurement's, the conversion is shown rather than assumed.
* It does not claim P1b is a hold. It is unmeasured, and the run that would settle it is named
  above as unrun work.
* It does not claim the pre-registration is now fully graded. **§A P1b remains open**, and this file
  is the pointer to it.

## Evidence

No new arm. Read from `SEAT_RESULT_THE_SETTLED_BOOK_IS_CHOSEN_AND_WEIGHTED_2026-09-11.md` (the
1.553×, the 59-of-109, the +84.9% and the 0.1% repair, the 84/1197.0, the null-case correction) and
`SEAT_RESULT_P6_THE_CHOSEN_BOOK_IS_2_45_PERCENT_WORSE_ON_GROSS_MARGIN_2026-09-11.md` (the −2.45%
gross and −5.75% net). The per-year funnel wins used for P2's unit conversion (35 in 2017 of 502)
are §B's own baseline block, §2.
