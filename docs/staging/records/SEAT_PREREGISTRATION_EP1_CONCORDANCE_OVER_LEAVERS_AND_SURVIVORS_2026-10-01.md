**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: grading EP1's per-account belief by concordance over leavers AND survivors

Claim `ep1-concordance-grade-over-leavers-and-survivors`. This is filed BEFORE any belief or
observable is joined to an outcome. Up to filing I have looked at the population census only:
counts, first-valuation years and last settled months. Successor of
`SEAT_PREREGISTRATION_EP1_WHICH_SNAPSHOT_OBSERVABLE_RANKS_A_LIFETIME_MARGIN_2026-10-01` (n = 66
leavers, noise floor ±0.24, nothing cleared it).

## Say what the thing is before measuring it

Realised lifetime margin R = m_r × T_r is **not a time-to-event quantity**. A survivor's margin to
date is not a lower bound on its lifetime margin, because margins go negative (2021–22). So Harrell's
C on R itself with survivors censored has no valid comparable-pair rule. The grade therefore splits
R into its two factors. Each factor can be graded over the whole book:

- **Tenure, censored: Harrell's C.** T_fwd is the time from the snapshot cutoff (`{y}-12-31`) to
  the last settled month, plus one month. The event is that the account is on the world's
  `churned_billing_accounts`, and survivors are censored at 2025-06. A pair is comparable when the
  account with the shorter T_fwd is a leaver. C is P(higher predictor → longer stay). Predictor ties
  score ½. A value below 0.5 means the predictor anti-ranks.
- **Margin rate, uncensored as a rate: Spearman.** m_r is `net_margin_after_cost_to_serve_gbp`
  divided by settled tenure in years, to exit or to the run's end. A survivor's rate covers fewer
  years than its lifetime will, so it is a rate observed to date. That caveat applies to
  survivors only.

**Population.** Every account with a numeric H2 belief in `three_horizon_clv_snapshots` (the graded
series), taken at its FIRST valuation year: **128 accounts, 69 leavers and 59 survivors**. 65 of
them are first valued in 2017. The run knows 248 accounts, and the other 120 are never valued, so
they cannot enter a grade of the belief. That is a denominator to state, not a defect found here.

**Noise floor.** It comes from a permutation null for each arm: shuffle the predictor 2,000 times,
seed 0, and take the 95% two-sided band. A binary arm's tie structure differs from a continuous
arm's, so each arm gets its own band. An arm inside its band is graded "cannot tell".

## The belief, re-built with HEAD code at each first-valuation cutoff (as `/tmp/ep1dec/built.py`)

| term | what it is |
|---|---|
| B | the H2 `tenure_expected` value, as graded |
| L_b | the life-years term: survival-discounted sum over the cohort life table at the account's tenure position |
| m_b | B / L_b |
| p_c | the company's churn probability at the cutoff, from the latest `build_churn_risk` entry |

## Predictions

- **Q0 (floor).** The C band at this n is about ±0.07 for a continuous arm and wider for a sparse
  binary arm.
- **Q1.** C(L_b, T_fwd) ≈ **0.55**. The life table varies only by tenure position, so it carries a
  little real tenure signal and no more.
- **Q2.** C(B, T_fwd) ≈ **0.52**. The margin term dilutes the tenure term.
- **Q3.** C(−p_c, T_fwd) = **0.50 ± 0.02**. p_c is the 0.05 floor for nearly every first-year
  account, so it is almost all ties. Prediction: no variance, no grade.
- **Q4.** Spearman(m_b, m_r) ≈ **+0.20**. It was +0.111 on the 66 leavers. Adding survivors adds the
  post-crisis margins, which the belief cannot see.
- **Q5 (the observables, C on T_fwd).** A1 consumption 0.53 · A2 dual fuel 0.55 · A3 direct debit
  0.55 · A4 SVT 0.47 · A5 fixed_1yr 0.50 · A7 bill-shock count to the cutoff 0.48 · A8 gas
  0.50 · A9 smart meter 0.50. A6 segment is refused if the book is all resi.
- **Q6 (the observables, Spearman on m_r).** All inside ±0.18, the n = 128 floor.
- **Headline (QH).** At most one observable clears its C floor on tenure, and none clears on
  margin rate. Either way, QH is enough to say the whole-book instrument has the power the
  66-leaver one lacked. An arm inside a ±0.07 band is a result. It is not "noise floor too wide".

Results will be written beside these, wrong ones included.

## Results (scripts `/tmp/ep1c/grade.py`, `stats.py`, `diag.py`; data `/tmp/ep1bk/run.pkl` + `run_output_latest.json`)

**The population as graded is 120, not 128: 66 leavers and 54 survivors.** Two exclusions were
named before any predictor was joined to an outcome:
- 3 seed accounts (C1, C5, C7, first valued in 2016) have no H2 belief under the HEAD rebuild.
- 5 accounts are first valued at the 2025-12-31 cutoff. The run ends in 2025-06, so they have no
  forward follow-up.

The instrument, so it can be rebuilt without `/tmp`: `T = months(last settled month) −
months({y}-12)`, in years. `E` = on `churned_billing_accounts`. C sums over ordered pairs (i, j)
where i is a leaver and either `T_i < T_j`, or `T_i == T_j` and j is censored. A pair scores 1 if
`pred_i < pred_j` and ½ on a predictor tie. **Within-year C** restricts the pairs to the same
first-valuation year. The null is 1,000 shuffles of the predictor (2,000 for Spearman), seed 0,
95% two-sided.

| arm | pooled C(T) [null] | **within-year C(T)** [null] | pooled sp(m_r) [null] | 2017 cohort sp(m_r), n≈65 [null] |
|---|---|---|---|---|
| B, belief H2 | 0.492 [0.42, 0.58] | **0.488** [0.41, 0.58] | +0.003 [±0.18] | +0.071 [±0.24] |
| L_b, life-years | **0.429 BELOW** [0.43, 0.57] | **0.500**: one value per cohort | **−0.336 BELOW** | refused: one value |
| m_b, margin term | 0.494 | 0.488 | +0.032 | +0.071 |
| −p_c, company churn | **refused: 0.05 for all 120** | — | — | — |
| A1 consumption | 0.509 | 0.528 [0.41, 0.58] | −0.083 | −0.034 |
| A2 dual fuel | **0.617 ABOVE** [0.43, 0.56] | **0.508** [0.43, 0.57] | **+0.380 ABOVE** | −0.084 |
| A3 direct debit | 0.486 | 0.471 [0.43, 0.58] | −0.045 | −0.082 |
| A4 SVT | 0.492 | 0.486 [0.44, 0.56] | +0.054 | +0.024 |
| A5 fixed_1yr | 0.484 | 0.487 [0.47, 0.53] | −0.076 | +0.006 |
| A6 segment | **refused: 127 resi, 1 SME** | | | |
| A7 bill-shock count | 0.553 | 0.530 [0.42, 0.59] | +0.163 | +0.126 |
| A8 gas | 0.491 | 0.507 [0.46, 0.54] | **−0.244 BELOW** | −0.095 |
| A9 smart meter | 0.462 | 0.449 [0.44, 0.56] | −0.098 | −0.278 [−0.25, +0.25] |

**Every pooled exceedance is cohort composition. The within-year column is the grade.**
- Dual fuel is 10/65 in the 2017 cohort and 48/55 across the later cohorts.
- The later cohorts are mostly survivors, so they are censored long, and they earn post-crisis
  margins. Median m_r by first-valuation year runs £62 (2017), £81, £167, £168, £186, £219, £285,
  £184 (2024).
- Within a year, dual fuel reads 0.508. One look-ahead confound was checked and refuted: A2 read
  from records up to the cutoff equals A2 read over the whole run on all 120 rows.
- A9's −0.278 inside the 2017 cohort is the one marginal exceedance in about 16 within-cohort
  tests. That is about what chance gives at 5%, and it is not a result.

Against the predictions:
- **Q0 — about right.** The continuous-arm band is ±0.08. Binary arms run from ±0.03 to ±0.07.
- **Q1 — WRONG, and the reason is structural.** C(L_b) is 0.429 pooled and 0.500 within a year.
  At first valuation every account sits at tenure position 1, so L_b takes exactly ONE value per
  cohort: 3.33 life-years in 2017, 2.77, 2.17, 2.27, 2.20, 3.05, 3.86, 3.25 in 2024. Its pooled
  anti-ranking is between cohorts only, and it carries no per-account tenure information at all.
- **Q2 — the not-informative half is right; the sign is wrong.** C(B) is 0.492, within-year 0.488.
- **Q3 — CONFIRMED, more strongly than predicted.** p_c is 0.05 for every one of the 120 accounts,
  not only the 2017 cohort. A first valuation is always a first year.
- **Q4 — WRONG.** Spearman(m_b, m_r) is +0.003 pooled and +0.071 within 2017.
- **Q5 — pooled, one arm cleared (A2), as allowed.** Within a year, none cleared.
- **Q6 — WRONG pooled.** A2 and A8 fall outside the band. Within 2017, none does.
- **QH — WRONG pooled, CONFIRMED within cohort.** The instrument has the power: a ±0.08 band on
  2,057 within-year comparable pairs, against ±0.24 at n = 66. Within a cohort, nothing at first
  valuation ranks tenure, and nothing ranks margin rate.
