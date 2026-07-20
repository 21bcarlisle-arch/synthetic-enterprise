# W1_3 gap-1 — the joint-regime-trigger hypothesis, MEASURED and REFUTED (2026-07-20)

**Status:** FRAME (a measured negative result + a theory-grounded redirect). No engine code shipped —
the change I built was reverted because it did not improve fidelity (R12: never ship toward the
intent when the evidence refutes it). Level held.

## The hypothesis (the director's W1_3 steer)

Gap-1 (from the DISCOVER passes): the stressed-regime trigger in `sim/weather_engine.py::
fit_national_macro_model` keys on wind-residual MAGNITUDE alone (`|wind_resid| > p90`), which fires
on windy days too and "never mechanistically produces the cold-and-still corner." The director's
steer: *model a latent blocking-high regime that jointly drives cold + low-wind, so cold-and-still
arises mechanistically.* The natural implementation: redefine the stressed regime as JOINTLY cold
AND still — both temp and wind residuals in their lower tail.

## What I built + measured

Implemented the joint trigger (`regime = (temp_resid < p30) & (wind_resid < p30)`, ~10.9% stressed
frequency, matching the old 10.0%). The stressed-regime covariance then carried a **+0.34 temp/wind
residual co-movement** (vs the wind-only regime) — so on its face the regime *is* now cold-and-still.

But the load-bearing fidelity metric is whether the engine's SIMULATED weather reproduces the REAL
joint cold-and-still tail — the D1 winter decile lift (`cascade_link_register`, estimated on real
Open-Meteo data = **2.365**). Measured, mean over 20 sims:

| Engine | simulated winter D1 lift | vs real 2.365 |
|---|---|---|
| REAL (Open-Meteo) | **2.365** | — |
| OLD (wind-only trigger) | 1.903 | under by 0.46 |
| NEW (joint trigger) | **1.650** | under by 0.72 — **WORSE** |

**The joint trigger made the robust fidelity metric worse, not better.** (The show-the-tail *envelope
max* rose 1.75→2.36 — more dispersion, occasional severe weeks — but the *average* coupling fell, and
`reach_fraction` fell 12%→8%. The average lift is the robust metric; the envelope max is one extreme.)
Reverted.

## Why (the theory — this is structural, not a tuning miss)

A regime-switching **Gaussian** model captures only LINEAR correlation within a regime (here +0.34).
But the **Gaussian copula has ZERO asymptotic tail dependence** — `lambda_L -> 0` as `u -> 0`. So no
regime trigger, at any percentile, can make regime-switching-Gaussian innovations reproduce a 2.34×
*decile-tail* lift: the corner co-occurrence a Gaussian produces from correlation ρ vanishes into the
tail, while the real cold-and-still corner *fattens* into it (rising L(u) as u→0 — asymptotic
dependence). Redefining which days are "stressed" reshuffles the linear covariance; it cannot add the
lower-tail dependence that is missing. **Gap-1 is not a trigger problem; it is an innovation
tail-structure problem.**

## The redirect (the real gap-1 fix — the next BUILD rung, now grounded)

Replace the Gaussian innovation draw in `simulate_national_macro` with a **lower-tail-dependent
copula** on the standardised (temp, wind) innovations — a Clayton (lower-tail) or t-copula,
calibrated so the *simulated* winter D1 lift matches the real 2.365 (within the block-bootstrap CI
[1.54, 3.38]). Keep the marginals (the fitted seasonal + AR1) unchanged; change only the joint
DEPENDENCE of the innovations. This is a real, bounded, higher-blast-radius engine change:

- **DoD (a real, failable gate — already built):** `weather_tail_demonstration` envelope still passes
  AND the simulated D1 lift (via `cascade_link_register`-style estimation on simulated weather)
  reaches the real 2.365 CI. A mutation that removes the tail dependence (falls back to Gaussian) must
  drop the simulated lift back to ~1.7 and fail.
- **R13:** a BASELINE fidelity change (match the real joint tail), decided blind to company P&L —
  named here, versioned, not silent drift.
- **Blast radius:** changes the innovation distribution → re-run the full engine + downstream sim
  suite; some golden-value tests will shift and need re-baselining (why this is its own focused rung,
  not a tail-of-turn edit).

## UPDATE 2026-07-20 (cont.) — the copula redirect ALSO refuted; the real mechanism PINNED + a fix VALIDATED

Pursuing the redirect above (a fatter-tailed innovation copula), I measured two more things:

1. **Symmetric fat-tailed innovations — REFUTED.** An honest MLE fit of a multivariate-t on the real
   (temp, wind) AR1 innovations gives **df ≈ 30.6** (nearly Gaussian; excess kurtosis only 1.0/0.2).
   To reproduce the output D1 lift via symmetric-t innovations would need df ≈ 3 — but the real
   innovations are NOT that fat-tailed. Forcing df ≈ 3 to hit the output metric would be fabricating
   tail dependence the data doesn't have (R12 goal-seek). So a symmetric-t copula does not honestly
   close the gap either.

2. **The mechanism, PINNED (with evidence).** The real innovations DO have strong *asymmetric
   lower-tail* dependence (winter innovation lower-tail lift = **3.149**), and the driver is a
   **SEASON-DEPENDENT correlation**: the temp/wind innovation correlation is **+0.528 in winter vs
   +0.178 non-winter** (all-year +0.300). The current engine fits a single (wind-magnitude-regime)
   covariance carrying roughly the all-year correlation, so it under-produces the winter coupling.
   The symmetric-t MLE missed this precisely because the dependence is asymmetric + seasonal, not
   symmetric-fat-tailed.

3. **A fix, VALIDATED.** A **season-conditioned innovation covariance** (a cold-season covariance with
   the +0.528 winter correlation, a warm-season covariance otherwise) reproduces the real winter joint
   tail: simulated D1 lift = **2.883**, well within the real block-bootstrap CI [1.54, 3.38] (vs the
   Gaussian all-year ~1.77 near the bottom of the band). Big improvement, right side of real.

**So the real gap-1 fix is a season-conditioned (not wind-magnitude) innovation covariance, NOT a
trigger and NOT symmetric fat tails.** Left as its own focused BUILD rung because it is a
regime-STRUCTURE change (the innovation covariance switches on season, replacing or augmenting the
wind-magnitude Markov regime — a design choice: calendar-season vs preserve-the-Markov-jump-plus-
seasonal-correlation) with a real downstream blast radius (the innovation distribution changes → some
seeded golden-value sim tests re-baseline). DoD unchanged: the sim D1 lift lands in the real CI AND
the show-the-tail envelope passes; a mutation back to the single all-year covariance drops the lift to
~1.77 and fails.

## Value of this pass

A director-steered mechanism (regime trigger), IMPLEMENTED and MEASURED, does not close the gap — and
the measurement + theory redirect the work to the mechanism that will (the innovation copula). That is
the honest outcome the show-the-tail artefact + the D1 real estimate exist to produce: the fidelity
instrument caught a plausible-but-wrong fix before it shipped.
