**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 2 · **Atom:** EP1_clv_three_horizon — Lane 0 delivery

# EP1: a fitted fuel-split forecast fails out of sample, and the leg count is not a tenure proxy

Claim `ep1-forecast-with-fuel-split-out-of-sample`. The pre-registration is
`records/SEAT_PREREGISTRATION_EP1_FUEL_SPLIT_FORECAST_LEAVE_ONE_CUTOFF_OUT_2026-10-01.md`, filed
before any held-out number was computed. The scripts are `/tmp/ep1s/loco.py`, `conf.py` and
`lex.py`; the logs are beside them. There are 298 later snapshots over 7 graded cutoffs
(2018–2024) and 88 accounts. The target is forward margin net of cost to serve (`fn`). All
figures are within-cutoff Spearman with per-account cluster CIs.

## Verdict

- **The licence rule is NOT met.** The pre-registered fitted forecast, F1 = b̂·I2 + ĝ·L, is
  *worse* than EP1's current input once the training folds exclude the held-out accounts:
  −0.157 [−0.303, −0.021].
- **No company-side change to EP1's forecast is licensed by this work.**
- The bare leg count is still the best ranker of forward net margin. Nothing fitted beat it.

## Results against the predictions

| | Prediction | Result |
|---|---|---|
| P1 | F1 − F0 (LOCO) in [+0.08, +0.18], CI excludes 0 | **+0.082 [+0.041, +0.125]. HELD**, but only at the band's lower edge. |
| P2 | F1 − FL in [−0.03, +0.06], CI contains 0 | **−0.074 [−0.192, +0.044]. NOT HELD.** The CI contains 0, but the point estimate is below the band: the blend ranks worse than legs alone. |
| P3 | LOCO-disjoint F1 within 0.02 of LOCO | **REFUTED.** Disjoint +0.230 against LOCO +0.469; the difference is −0.239 [−0.379, −0.100]. |
| P4 | ĝ/b̂ > 0, b̂ > 0 in all 7 LOCO folds | **HELD for LOCO**, with g/b between +16 and +164. Under disjoint, 4 of 7 folds flip sign. When 2023 and 2024 are held out, b̂ ≈ 1.8 and ĝ ≈ −230 to −290. |
| P5 | k̂ ≥ 55 every fold, and F2 within 0.03 of F1 | **k̂ ≥ 55 HELD.** It is 220 in every LOCO fold and 55–220 under disjoint. **F2 ≈ F1 NOT HELD:** F2 beats F1 by +0.054 [+0.016, +0.099]. |

### Why P3 failed

Plain LOCO leaks an account's own persistence into the fit: the same account recurs at other
cutoffs. Strip that out and the level-space OLS has 63–115 training rows. Those rows come from a
different fuel mix: dual fuel is 8/49 of rows at 2018 and 33/48 at 2024. The fitted coefficients
then swing wildly between folds. **A fitted blend in level space is not usable at this n.** That
confirms the in-sample warning in the prior finding.

### What did hold up

F2 is the rank-tuned per-leg credit (I2 + k̂·L). It still beats F0 under disjoint folds:
**+0.104 [+0.050, +0.161]**. Held-out, it reads +0.491, which is below legs alone (+0.544).

The pre-registration named "rank by fuel split, then by rate" as the change for the case where
the blend does not beat legs. That rule has no fitted parameter.

| Comparison | Result |
|---|---|
| Lexicographic (L, then I1): F0 | +0.524, a difference of **+0.131 [+0.069, +0.211]** |
| Lexicographic (L, then I1): legs alone | −0.020 [−0.114, +0.085] |

**This is NOT out-of-sample evidence.** The rule has nothing to fit. But the leg count's signal
was discovered on these same 298 rows, so grading it here grades the hypothesis on its own
discovery sample. It is a candidate, not a licence. What would license it is an independent run.

## The open mechanism

### M1: separation. NOT HELD; the opposite holds.

The leg count separates the to-date gross rate *more* sharply than the forward target:

| | Within-cutoff AUC of L |
|---|---|
| Against I2 | 0.911 |
| Against `fn` | 0.834 |
| Against I1 | 0.806 |

The strata do not drift apart after the cutoff. The to-date rate already carries the between-fuel
gap, and then dilutes it with within-fuel variation that does not persist.

### M2: dispersion. NOT HELD; the opposite holds, and this is the mechanism.

Median within-(cutoff, L) interquartile range (IQR), £/yr:

| | I2 (to date) | `fn` (forward) | Ratio |
|---|---|---|---|
| Single fuel | 29.6 | 123.9 | 0.24 |
| Dual fuel | 90.8 | 90.1 | 1.01 |

- **Single-fuel accounts look alike to date and diverge forward.** Their spread grows about
  fourfold after the cutoff.
- Their median forward *net* rate (190) exceeds their median to-date *gross* rate (131).
- The to-date rate cannot say which single-fuel account will diverge, because to date they had
  not.
- That is why within-stratum I1 reads only +0.19, and why the leg count, which is free of
  within-stratum noise, wins.

**Fidelity question, not chased:** is a £30/yr IQR among single-fuel accounts' to-date margins
plausible? It is near-uniform pricing followed by heterogeneous exposure. 2022 is the cutoff
where I1 reads −0.241. This is a prompt for the world lane, not a defect claim.

### M3: composition. Split result.

- **HELD:** the leg count ranks `fn` in both halves.
  - Early cutoffs (2018–20): +0.386 [+0.17, +0.57].
  - Late cutoffs (2021–24): +0.633 [+0.49, +0.74].
- **NOT HELD:** |sp(L, pos)| < 0.2. It is **−0.701**. Within a cutoff, dual-fuel accounts sit at
  much earlier tenure positions.

The next check was post hoc and was not pre-registered (`conf.py`). It asks whether the fuel split
is standing in for tenure:

| Test | Result |
|---|---|
| L vs `fn` within (cutoff, tenure position), on the 211 rows in mixed-fuel strata | **+0.413 [+0.22, +0.58]** |
| Tenure position vs `fn` within (cutoff, L) | −0.01 [−0.20, +0.18] |

**The fuel split is not a tenure proxy. If anything, tenure's own reading (+0.386) is the fuel
split's shadow.**

## What this licenses, and what is next

- **Nothing company-side yet.** The pre-registered licence failed, and the remedies that survive
  are graded on their own discovery sample.
- **Next:** replicate on an independent run, meaning a different population seed. Use the
  parameter-free rule (lexicographic L then I1, against I1 and against L alone) and the
  dispersion read (M2). That run must be built before it can be graded.
- **Wall note:** an account's fuel legs are observable to a real supplier, so a forecast using
  them would be wall-clean.
- **Practitioner check (third side):** that dual-fuel accounts are worth more is industry common
  knowledge. It is not, by itself, evidence for this run's *magnitude*.
