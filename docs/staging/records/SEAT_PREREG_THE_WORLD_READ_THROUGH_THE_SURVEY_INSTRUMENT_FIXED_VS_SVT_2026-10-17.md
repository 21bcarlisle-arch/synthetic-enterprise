**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Subjects:** `PB4_engagement_separated_from_elasticity`, `EP17_varied_population_draw` · **Claim:** `w2-tariff-gradient-instrument-emulation` (Lane 0 delivery)

# Pre-registration: the world's fixed:SVT switching ratio read through the survey's own instrument

Written 2026-10-17 at origin `c8a3918f9`, before any outcome below has been computed. What has been
read: the book's schema, its date range (2016-01-01 to 2025-06-08), its account count by id prefix,
and the aggregates already published in the 2026-10-17 payment-gradient finding. Nothing in this
file is edited after the run; the finding grades each line beside it.

**Measurement only. No world value changes.**

## The question

`docs/market_research/switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md` §1a
proved the published fixed:SVT ratio is the identity `L(1−F)/((1−L)F)` in where switchers land (L)
and the fixed share of the stock at interview (F). §1c names emulating the instrument as the test
the world can fail. This run does the emulation.

## The book and the population

`docs/reports/run_output_latest.json` in the shared tree, producing commit `78f77c34e` (the
finding's book). Residential accounts only: the roster's SME and I&C ids are dropped; the count is
printed. Decision leg = the electricity rows if the account has any, else gas.

## The instrument, defined before it is measured

Interview date `t`, window `W`.

- **Cohort:** accounts with a state row covering `t − W`.
- **Switchers S:** cohort accounts with a switch dated in `(t − W, t]`. A switch is a
  `customer_events` churn or an `svt_decisions` churn; neither list holds home moves.
- **Stayers:** cohort accounts with a row covering `t`; their tariff at interview is that row's.
- **Dropped:** cohort accounts that left by any other route (home move, end of book). The survey's
  frame cannot see a household that left the market.
- **Instrument, at landing share L:** fixed-now = fixed stayers + L·S; SVT-now = SVT stayers +
  (1 − L)·S. Ratio = (L·S / fixed-now) / ((1 − L)·S / SVT-now). F_instr = fixed-now / (S + stayers).

**CMA 2015 emulation:** `W` = 12 months, `t` = 1 March 2017, 2018, 2019, 2020, 2021 (windows
covering March 2016 to February 2021, all pre-crisis). Pooled by summing counts across the five
dates; per date also printed. L = 0.43, 0.593 (CMA proportional), 0.63, all on the fixed+SVT base
(CMA App. 9.1). Graded against the CMA's 1.9–4.3, **and paired**: the CMA's ratio at the same L is
`L·0.716/((1−L)·0.284)`, so at a matched L the world is above or below the CMA exactly when its
F_instr is below or above 0.284.

**CIM w6 emulation:** `W` = 6 months, `t` = 2025-02-01 (fieldwork January–February 2025), L = 0.82.
Printed beside the CMA figure against 2.8 and **labelled distorted by self-report**: CIM's F is
self-reported (0.62 of respondents say fixed against the market's 0.30–0.36), and 44% of SVT
households misreport (CMA ¶47). It is not a grade.

**Power control, the branch that must be able to fire.** The identity says the world's pre-switch
gradient reaches the ratio only by depleting the fixed or SVT stock inside the window. So the run
also prints, at L = 0.593 pooled pre-crisis, the instrument ratio under counterfactual pre-switch
gradients g = 0.3, the world's own, 1.0 and 2.8. Switch total S is held; S is re-split across the
starting tariffs in proportion to stock × g; the switches moved off the fixed stock are returned to
it at q = P(still fixed at t | fixed at t − W, not switched), the rest to SVT.

## Predictions

- **P1.** Pre-crisis pooled F_instr lies in **0.33–0.48** (the finding's exposure share was 0.41).
- **P2.** Pre-crisis pooled instrument ratio at L = 0.593 lies in **1.3–2.3**; at L = 0.43 in
  **0.8–1.5**; at L = 0.63 in **1.5–2.7**. So the world reads **at or below the bottom** of the CMA's
  1.9–4.3, and under the CMA at every matched L (P1 implies F_instr > 0.284).
- **P3.** No single pre-crisis date reads above the CMA's ratio at its matched L (0.593 → 3.68).
- **P4.** The CIM emulation (L 0.82, 6 months, 2025-02-01) reads **above 6**, far above 2.8, because
  the world's record fixed share in 2024–25 is about 0.2 and CIM's self-reported one is 0.62.
- **P5 (power).** Across g = 0.3 to 2.8 the instrument ratio moves by **less than 35%** of its value
  at the world's own g. If it moves by more, the instrument can see the pre-switch gradient and the
  knowledge page's "nothing about which tariff the switchers left appears" is too strong for a
  12-month window. If by less, this emulation grades the stock share F, not the gradient, and that
  is what the finding must say.
- **P6.** The world's own pre-switch fixed:SVT ratio over the same pooled windows lies in
  **0.45–0.80** (the finding's drawn 2016–20 was 0.59; this one is realised).

## What each outcome would mean

- Pass on the band (P2 inside 1.9–4.3): the world's record stock share is consistent with the CMA's
  at its landing share. That is a grade of F, and F on this book is mostly the company's own sales
  mix (57% of accounts open on a fix), not a world behaviour.
- Below the band at every L: the book carries more fixed stock than the 2015 market. Read with P5:
  unless P5 fails, nothing here says the world's pre-switch gradient is wrong, and
  `SVT_INERTIA_ANNUAL_RECENT` is not moved by it.
