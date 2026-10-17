**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity` (row untouched) · **Subjects:** `EP17_varied_population_draw` · **Claim:** `w2-tariff-gradient-instrument-emulation` (Lane 0 delivery)

# Read through the survey's own instrument, the pre-crisis world sits inside the CMA's band, and the instrument cannot see the gradient it was meant to grade

**DEVELOPMENT.** One book, one seed. Measurement only: no world value changed.

Predictions were filed first, at
`docs/staging/records/SEAT_PREREG_THE_WORLD_READ_THROUGH_THE_SURVEY_INSTRUMENT_FIXED_VS_SVT_2026-10-17.md`
(landed `4c47a26a3`, promoted before the probe was run).

## The answer

| emulation | world | published | reading |
|---|---|---|---|
| CMA 2015 (supplier records, 12 months), pooled March 2016 – Feb 2021, L = 0.43 | **1.98** (95% 1.77–2.20) | 1.90 at the same L | inside 1.9–4.3 |
| same, L = 0.593 (CMA proportional) | **3.27** (2.93–3.64) | 3.67 | inside; just under the CMA at matched L |
| same, L = 0.63 | **3.70** (3.31–4.11) | 4.29 | inside |
| CIM w6 (6 months to 2025-02-01), L = 0.82 — **distorted by self-report, not a grade** | **16.7** | 2.8 | far above |

**The pre-crisis world passes the CMA's band at every landing share the CMA allows.** The
knowledge page's arithmetic (1.0–1.95) and the item's reading ("at or just below the CMA's band")
were both wrong, in the flattering direction for nobody: the world is inside it.

**But the pass is not a grade of the world's fixed-vs-default split.** The power control shows the
instrument is blind to the pre-switch gradient:

| counterfactual pre-switch gradient g (fixed:SVT, per starting stock) | instrument ratio at L = 0.593 |
|---|---|
| 0.30 | 3.06 |
| 1.00 | 3.22 |
| **1.33 (the world's own, realised)** | **3.27** |
| 2.80 | 3.40 |

A ninefold change in the gradient moves the instrument by 11%, well inside the bootstrap interval of
any one reading. What the instrument grades is **F, the fixed share of the stock at interview**
(world 0.308 against the CMA's 0.284). On this book F is mostly made by two things that are not the
world's switching behaviour: the company's own sales mix (its pre-crisis acquisitions land on a fix
102 times in 121) and how fast fixed terms roll to default (only 24% of fixed households that did not
switch are still on a fix twelve months later).

So the instrument emulation is a test the world **can** fail, as §1c said, but it fails or passes on
the stock share, not on the split it was proposed to test. The GAP in §1c is therefore stronger than
written: **neither the published survey ratio nor any emulation of it can grade the world's
pre-switch fixed-vs-default gradient.** Only a supplier-returned loss series cut by tariff at loss
could.

## Per date (L = 0.593; CMA at that L is 3.67)

| interview | cohort | switchers | instrument | F_instr | realised pre-switch g |
|---|---|---|---|---|---|
| 2017-03-01 | 69 | 8 | 4.28 | 0.254 | 1.78 |
| 2018-03-01 | 417 | 78 | 3.79 | 0.278 | 1.44 |
| 2019-03-01 | 389 | 71 | 3.27 | 0.308 | 0.86 |
| 2020-03-01 | 324 | 52 | 2.47 | 0.371 | 1.51 |
| 2021-03-01 | 286 | 47 | 3.41 | 0.299 | 2.17 |

The per-date g column moves from 0.86 to 2.17 with no matching movement in the instrument column
(2019 has the lowest g and a middling ratio; 2020 has a middling g and the lowest ratio, because its
F is highest). That is the power control again, on the data rather than a counterfactual.

## The CIM line, and why it is not a grade

CIM's F is self-reported: 0.62 of respondents say they are on a fix, against a market of 0.30–0.36,
and only 44% of SVT households name their tariff correctly (CMA ¶47). The world's record F in
2024–25 is 0.21. With L = 0.82 the identity gives 16.7 on the world's F and 2.84 on CIM's own. The
gap is the misreporting, not the world. The 6-month windows hold only 5–12 switchers each.

## Each prediction beside its result (wrong ones kept)

- **P1 WRONG.** Pooled F_instr 0.308 at L = 0.593 (0.276–0.353 across L), below the predicted
  0.33–0.48. The prediction took the finding's exposure share (0.41) as the interview share. It is
  not: the cohort's fixed stock is 0.41 at the window's start and 0.24 among its stayers at the end,
  because fixed terms roll to default inside the year.
- **P2 WRONG on the band, HELD on the pairing.** 1.98 / 3.27 / 3.70 at L = 0.43 / 0.593 / 0.63,
  each above its predicted range and inside the CMA's 1.9–4.3. The pairing held: the world is under
  the CMA at every matched L, because F_instr > 0.284. It is under by 0.1–0.6, not by the margin
  predicted.
- **P3 WRONG.** Two dates read above the CMA's matched 3.67: 2017 (4.28, a cohort of 69) and 2018
  (3.79).
- **P4 HELD.** CIM emulation 16.7, above 6.
- **P5 HELD.** g from 0.3 to 2.8 moves the ratio 3.06 → 3.40, 10% of its value at the world's g,
  under the 35% bar. The emulation grades F, not the gradient.
- **P6 WRONG, and badly specified.** Realised pre-switch g is 1.33, above 0.45–0.80. The prediction
  borrowed the finding's 0.59, which is per account-year **on the tariff at departure**. This
  measure is per household **on the tariff at the window's start**, so a household that rolls off a
  fix and drifts away within the year counts as fixed here and as default there. They are two
  different quantities, and that should have been said before predicting one from the other.

## What this changes

1. **The knowledge page's §1b table and the payment-gradient finding's CORRECTED note** said the
   pre-crisis world reads 1.0–1.95 on the instrument. Measured, it reads 1.98–3.70. Both are
   corrected beside the claim, pointing here.
2. **`SVT_INERTIA_ANNUAL_RECENT` stays as it is**, and now with a proved reason: no published
   instrument, survey or emulated, can move it.
3. **The era reading in the payment-gradient finding** (2.61 in 2024–25 against 2.8) was already
   withdrawn as inadmissible. This run adds that the late world's high instrument reading (16.7) is
   about CIM's self-reported stock, not about the world.
4. **W-A is not tested here, and a question is owed on it.** The payment-method field carries the
   same at-interview contamination (knowledge page §2, size not published). The same power control,
   run on payment channel instead of tariff, would say whether CIM's 0.55 can see a pre-switch
   payment gradient at all. Unlike tariff, payment method rarely changes for a household that does
   not switch, so the answer is not known in advance. W-A is still graded against its own filed
   prediction after the 19 Oct publish.
   **Answered 2026-10-17, knowledge only:** the payment instrument does see the pre-switch gradient,
   scaled by `(1 − m)`, where `m` is the share of PPM switchers landing on credit. `m` is not published.
   Pre-crisis it is low by mechanism, with a ceiling of about 0.2–0.3. 0.55 grades W-A's 0.50–0.70
   band only if `m` ≲ 0.12. A drawn 0.70–0.85 would miss the prediction, not the record. See the K8
   page, §2a (`docs/market_research/switching_gradient_by_tariff_and_payment_what_the_record_can_grade.md`).

## Method, for the next session

- Book: `/home/rich/synthetic-enterprise/docs/reports/run_output_latest.json`, `producing_commit`
  `78f77c34e`, generated and not committed. Run from the repo root with `PYTHONPATH=.`.
- Population: 780 accounts in `account_state_log` after dropping the roster's SME and I&C ids. The
  payment-gradient finding counted 770; its filter is not on file, and the 10-account difference is
  not reconciled here.
- Decision leg: electricity rows if any, else gas. Tariff at a date: the row whose
  `[term_start, term_end]` covers it.
- Switches: `customer_events` and `svt_decisions` rows with `event_type == "churned"` (342 on this
  population). Neither list holds home moves.
- Instrument as defined in the prereg: closed cohort at `t − W`; switchers in `(t − W, t]`; stayers
  at their tariff at `t`; other exits dropped.
- Interval: 2,000-draw bootstrap over accounts (an account recurs across the five pooled dates, so
  the pooled counts are not independent; resampling accounts keeps that).
- Power control: switch total S held, re-split across starting stock in proportion to stock × g;
  switches moved off the fixed stock return as non-switchers at q = 0.241 still fixed, the rest to
  SVT; the SVT starters lose the same number of stayers. SVT-to-fixed conversion inside the window
  is ignored for the moved households (second order).
