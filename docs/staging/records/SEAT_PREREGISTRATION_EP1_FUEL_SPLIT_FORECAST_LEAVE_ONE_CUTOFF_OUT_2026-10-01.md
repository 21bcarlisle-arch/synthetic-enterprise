**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# Pre-registration: does a forecast that uses the fuel split beat EP1's to-date rate out of sample?

Claim `ep1-forecast-with-fuel-split-out-of-sample`. The duplicate-work note named this same id as
"already held". That was this draw's own hand-off from the seat that landed `719e71173` three
minutes earlier; no rival `surgical_land` was running (05:42). The premise is not spent:
`719e71173` landed the in-sample finding and says the forecast "is not built" and needs "its own
out-of-sample pre-registration". Filed BEFORE any held-out number is computed.

## Premise (in-sample, from `SEAT_FINDING_EP1_THE_FUEL_SPLIT_CARRIES_..._2026-10-01.md`)

On 300 later snapshots, within-cutoff Spearman against the forward margin net of cost to serve
(`fn`): legs alone +0.545 [+0.40, +0.65], gross rate I2 +0.451, EP1's input I1 +0.387. Within a
fuel stratum I1 reads +0.19 with a CI containing 0. In-sample OLS and shrinkage did not help.

Composition, read before filing (counts only, no target): the dual-fuel share of rows rises by
cutoff from 8/49 (2018) to 33/48 (2024). The 2017 cutoff has 2 rows, so the within-cutoff
statistic drops it, leaving 7 graded cutoffs and 298 rows.

## Instrument

Rows, I1, I2, L and `fn` are exactly `/tmp/ep1s/strat_rows.json` (built by `/tmp/ep1s/strat.py`
from `/tmp/ep1bk/run.pkl`). The statistic is `wsp` from `/tmp/ep1s/snapstats.py`, unchanged. The new
script is `/tmp/ep1s/loco.py`.

Forecasts. Each held-out cutoff's forecast is fitted only on the other cutoffs:

- **F0 = I1.** This is EP1's current input. It needs no fitting.
- **FL = L.** The leg count alone, as reference. It needs no fitting and is heavily tied.
- **F1 = b̂·I2 + ĝ·L.** b̂ and ĝ come from OLS of `fn` on (I2, L), with all three demeaned within
  cutoff, on the training cutoffs. Within a cutoff its ranking depends only on ĝ/b̂ when b̂ > 0.
- **F2 = I2 + k̂·L.** k̂ is the grid value in {−110, −55, 0, 27.5, …, 330} that maximises the
  training cutoffs' `wsp` against `fn`. This tunes the per-leg credit on the graded objective
  itself.

Two fold schemes:

- **LOCO.** Leave one cutoff out, as directed.
- **LOCO-disjoint.** The same, except training also drops every account that appears in the
  held-out cutoff. An account recurs across cutoffs, so plain LOCO lets its own persistence leak
  into the fit.

Grade: `wsp` over all held-out predictions pooled (each row carries its own fold's forecast). The
CIs are a per-account cluster bootstrap (1000, seed 0) over the paired differences, with the
forecasts held fixed. That omits fitting variance, which is stated rather than hidden.

## Predictions

| | Prediction |
|---|---|
| P1 | F1 − F0 (LOCO) lies in [+0.08, +0.18], and its cluster CI excludes 0. |
| P2 | F1 − FL lies in [−0.03, +0.06], and its CI contains 0. The rate adds little beyond the legs. |
| P3 | LOCO-disjoint F1 is within 0.02 of LOCO F1. |
| P4 | ĝ/b̂ > 0 with b̂ > 0 in all 7 LOCO folds, so every fold credits dual fuel. |
| P5 | F2's k̂ is ≥ +55 in every fold, and F2 lands within 0.03 of F1. |

**Licence rule, fixed now:** a company-side change to EP1's forecast is licensed only if
F1 − F0 under **LOCO-disjoint** has a cluster CI whose lower bound is > 0. If F1 also fails to
beat FL (P2), the change is "rank by fuel split, then by rate". It is not a fitted blend.

## The open mechanism (descriptive, with directional predictions)

- **M1, separation.** Within cutoff, compute the AUC with which L separates I2 and the AUC with
  which it separates `fn`. Prediction: AUC(fn) > AUC(I2). The strata are more separated forward
  than to date, which is consistent with to-date noise and not with a median shift.
- **M2, dispersion.** Compare the within-(cutoff, L) robust spread (IQR) of I2 against that of
  `fn`, for each L. Prediction: I2's spread exceeds `fn`'s for single fuel by more than it does
  for dual fuel. The single-fuel to-date rate is the noisier one.
- **M3, composition.** Split the L-alone `wsp` into early cutoffs (2018–2020) and late cutoffs
  (2021–2024). Also compute within-cutoff sp(L, pos), where pos is the tenure position.
  Prediction: L ranks `fn` in both halves (both > +0.3), so the effect is not one cohort's.
  Prediction: |sp(L, pos)| < 0.2, so the leg count is not standing in for tenure.
