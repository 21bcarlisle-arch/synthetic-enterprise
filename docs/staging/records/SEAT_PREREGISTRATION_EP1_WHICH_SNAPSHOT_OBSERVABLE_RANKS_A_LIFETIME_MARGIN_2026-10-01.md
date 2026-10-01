**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: which snapshot observable ranks an account's lifetime margin

Claim `ep1-what-ranks-a-lifetime-margin`. Filed BEFORE any observable is joined to a realised value.
What I have looked at so far: the distributions of the observables over the 66 graded rows, not
their relation to anything realised.

## The population and the quantity

The 66 graded leavers from `/tmp/ep1dec/rows.json`, which is the set behind gap 1.066 /
Spearman 0.122 after `127c007f0`. 51 of the 66 are 2017 snapshots, so this is close to one cohort.
**Realised lifetime margin** `R = m_r × T_r`: realised margin per settled year times realised
tenure in years, as the harness defines it. Each arm is one observable, read off the customer record
or the company's own settlement records up to the snapshot, and nothing else. The statistic is its
Spearman against R, with ties averaged, plus a bootstrap 90% interval (2,000 resamples, seed 0).

**Noise floor.** At n = 66 the two-sided 95% null band for a Spearman is about ±0.24. An arm inside
it is reported as "cannot tell", not as a weak effect.

## Observables, and what each arm can be

| arm | observable (what a supplier holds) | variation on the 66 |
|---|---|---|
| A1 | `eac_kwh` / `aq_kwh`: annual consumption | continuous |
| A2 | dual fuel: the billing account has both an electricity and a gas leg | from the records |
| A3 | `payment_method == direct_debit` | 39 DD / 22 other / 5 none |
| A4 | `tariff_type == svt` | 12 svt / 54 none |
| A5 | `contract_type == fixed_1yr` | 5 / 61 |
| A6 | `segment` | **all 66 resi. No arm is possible.** Refused by name, not measured |
| A7 | company-side bill-shock count to the snapshot (`score_experience_signals`, yoy, 0.15) | count |
| A8 | `commodity == gas` (the account's primary leg) | 10 / 56 |
| A9 | `smart_meter` | 15 / 48 / 3 none |

## Predictions

- **P0 (which factor R ranks on).** Spearman(R, m_r) ≈ +0.75 and Spearman(R, T_r) ≈ +0.35. R
  ranks mainly on its margin, so an observable that ranks R will rank m_r.
- **P1.** A1 consumption: +0.20. Bigger accounts make bigger margins in both directions, and the
  2021–22 losses scale with volume too. This is the arm most likely to clear the floor, and I
  predict it does not quite.
- **P2.** A2 dual fuel: +0.10.
- **P3.** A3 direct debit: +0.10. Lower bad debt, offset by no tenure difference.
- **P4.** A4 SVT: +0.15. SVT carried more margin before the cap.
- **P5.** A5 fixed_1yr: 0 ± 0.1. Five rows, so cannot tell either way.
- **P7.** A7 bill-shock count: −0.10.
- **P8.** A8 gas: −0.05.
- **P9.** A9 smart meter: 0 ± 0.1.
- **Headline (PH).** No single observable clears the ±0.24 floor. If one does, it is A1.
  If PH holds, a one-variable observable cannot be what the belief is missing at this sample size.
  The next question is then the sample, the book EP1 can grade, rather than the variable.

Results will be written beside these predictions in this file, wrong ones included.

## Added after the arms ran and before this was measured: is m_r the account or the era?

The arms show that R ranks on m_r and that nothing observed ranks m_r. One explanation is that the
realised margin per year is set by which market years the account lived through, not by the
account. If so, no snapshot observable can carry it. The exit date `y + T_rem` is not observable at
the snapshot. It is a diagnostic here, never a candidate.

- **P10.** Spearman(m_r, exit year) ≤ −0.40. Accounts that live into 2021–22 earn less per year.
- **P11.** Within the 2017 cohort (n = 51), Spearman(m_b, m_r) stays under 0.24. The cohort
  restriction does not rescue the margin rank.
- **P12.** The share of m_r explained by era: Spearman(m_r, the cohort-mean m_r of accounts that
  exit in the same year) ≥ 0.5.
- **P13 (added before measuring).** The company's own per-account churn probability at the snapshot
  (latest `build_churn_risk` entry) against realised tenure T_r. A correct belief is negative: higher
  churn means a shorter stay. Given the retention belief's anti-ranking
  (`WORKER_FINDING_THE_RETENTION_BELIEFS_ANTI_RANKING_..._2026-10-01`), I predict **+0.10**, the
  wrong sign and inside the noise floor.

## Results (scripts `/tmp/ep1obs/measure.py`, `era.py`, `churn.py`; data `/tmp/ep1bk/run.pkl`)

| arm | n | Spearman vs R [90% boot] | vs m_r | vs T_r | prediction |
|---|---|---|---|---|---|
| A1 consumption | 64 | +0.124 [−0.08, +0.33] | +0.003 | +0.159 | +0.20: within the noise, as PH said |
| A2 dual fuel (19 rows) | 66 | +0.061 [−0.16, +0.28] | +0.036 | +0.112 | +0.10 ✓ |
| A3 direct debit | 61 | −0.070 [−0.27, +0.14] | −0.072 | −0.012 | +0.10: wrong sign, inside the noise |
| A4 SVT | 66 | −0.045 [−0.25, +0.16] | −0.039 | −0.058 | +0.15: wrong sign, inside the noise |
| A5 fixed_1yr | 66 | +0.041 | +0.053 | +0.023 | 0 ± 0.1 ✓ |
| A6 segment | — | **refused: all 66 resi** | | | ✓ |
| A7 bill-shock count to snapshot | 66 | +0.187 [−0.03, +0.38] | +0.176 | +0.112 | −0.10: **wrong sign**, the strongest arm, still inside the noise |
| A8 gas | 66 | +0.067 | −0.058 | +0.179 | −0.05: inside the noise |
| A9 smart meter | 63 | −0.168 [−0.37, +0.04] | −0.193 | −0.058 | 0 ± 0.1: wrong, inside the noise |
| (ref) the belief's m_b | 66 | +0.103 | +0.111 | +0.168 | — |

- **PH — CONFIRMED.** No observable clears ±0.24 against R, m_r or T_r.
- **P0 — HALF WRONG.** Spearman(R, m_r) = **0.895**, as predicted. Spearman(R, T_r) = **0.632**,
  not 0.35. Tenure carries far more of the rank than I expected, because m_r and T_r are themselves
  correlated (+0.294).
- **P10 — WRONG IN SIGN.** Spearman(m_r, exit year) = **+0.46**. Accounts that live longer earn
  MORE per year. Exits in 2023–24 average about £200 a year against £40–80 for 2017–20 exits: the
  survivors reach the post-crisis margins.
- **P11 — CONFIRMED, narrowly.** Within the 2017 cohort, Spearman(m_b, m_r) = 0.227.
- **P12 — REFUTED.** 0.133. The leave-one-out exit-year means are noisy: the 2019 mean is −£64
  against a median of £69, so one or two large losses set it.
- **P13 — UNMEASURABLE, and that is the result.** The company's churn probability at the snapshot
  is **0.05 for all 66 accounts**: one renewal entry each, `bill_shock_count` 0. It has no variance
  to rank with.
