**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1, over the whole book: nothing a supplier holds at first valuation ranks tenure within a cohort, and the belief's own tenure term is one number per cohort

Claim `ep1-concordance-grade-over-leavers-and-survivors`. The predictions were filed first. The
results and the exact instrument sit beside them in
`docs/staging/records/SEAT_PREREGISTRATION_EP1_CONCORDANCE_OVER_LEAVERS_AND_SURVIVORS_2026-10-01.md`.
No code changed.

## What was done

Realised lifetime margin is not a time-to-event quantity, because a survivor's margin to date is
no bound on its lifetime margin. So it was graded as its two factors:
- tenure, by Harrell's C with survivors right-censored at 2025-06;
- margin per settled year, by Spearman.

The population is 120 accounts at first valuation: 66 leavers and 54 survivors, against the 66
leavers before. Per-arm permutation nulls were used, and C was also counted **within
first-valuation year**.

## What was found

1. **The instrument has the power the 66-leaver one lacked.** The within-year C band is ±0.08 on
   2,057 comparable pairs, against ±0.24 before. "Cannot tell" now means a small effect is ruled
   out. It no longer means the sample was too small.
2. **Within a cohort, nothing ranks.** The belief itself scores within-year C 0.488. Its margin
   term scores Spearman +0.071 on the 2017 cohort. Every one of the eight observables lies in
   0.449–0.530, inside its band. The company's churn probability is 0.05 for all 120 and is
   refused for having no variance.
3. **Every pooled signal is cohort composition, and would have been the wrong thing to act on.**
   - Dual fuel reads C 0.617 and Spearman +0.38 pooled, but 0.508 within a year. It is 10/65 of
     the 2017 cohort and 48/55 of the later cohorts, which are mostly censored survivors on
     post-crisis margins.
   - L_b anti-ranks pooled (0.429, and −0.336 on margin rate). That too is between cohorts only.
4. **The belief's tenure term is structurally constant at first valuation.** Every account is at
   tenure position 1 when first valued, so L_b is ONE value per cohort: 3.33 life-years in 2017,
   down to 2.17 in 2019. p_c is the floor. The belief has no per-account tenure input at the moment
   it is graded. That holds over the whole book, not only for the 66 leavers.

## What this settles and what it does not

- EP1's ranking defect at first valuation is **not a missing observable the company could add
  today.** In this world, no sign-up observable carries tenure within a cohort. A belief cannot
  learn an association the world does not hold.
- That is **not** a reason to change the world. The baseline/curriculum split forbids changing it
  on company results. The world's first-year hazard is already being re-derived for FIDELITY
  reasons: `rederive-the-worlds-bill-shock-hazard-so-it-fires-in-year-one` (PB4) is landing now.
  Its first increment emits `sim_experienced_bill_shock` without yet driving the hazard. When the
  swap lands, this grade is the instrument to re-run. Its within-year column is the reading.
- **Not asked here:** acquisition `channel`. In the industry, price-comparison-acquired switchers
  are understood to leave sooner, and channel is an `AccountObservables` field. It was not in the
  pre-registered set, so it gets its own pre-registration rather than a post-hoc arm.
- **Not asked here:** 120 of the 248 accounts the run knows are never valued. Who they are is a
  denominator question for the harness. It is not part of this grade.
- A second valuation (tenure position 2+) is where the belief's tenure term and p_c first vary per
  account. Grading every account-snapshot is the other route to a per-account tenure grade. Its
  repeated measures need a cluster-aware null.
