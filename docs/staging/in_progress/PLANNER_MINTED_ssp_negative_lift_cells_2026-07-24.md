# [PLANNER-MINTED] Attack the SSP residual-demand model's NEGATIVE-lift cells (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 3). Attaches to existing atom `W1_6_physics_price_signal` (fidelity-ledger row `ssp_residual_demand_scarcity_calibration_2026_07_19`).
> **BLOCKING SUB-ITEM (open):** Scope step 1 (DISCOVER/FRAME — diagnose WHY the calm-year cells lose to the OLS baseline, R4) is drawable now (doc-only, idle-drawable). A baseline-changing BUILD proceeds under reversible authority once the mechanism is named, **strictly R13/R12-governed** (P&L-blind, mechanism-diagnosis not benchmark-tuning; the honest close may be an R10 named simplification). **UNBLOCKS:** self — no wall; DISCOVER not yet done this tick (generator FRAME drew first per sequencing guard). Next drawable DISCOVER item.

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7). Minted from a fidelity-ledger row. **Propose-then-proceed.**

## Fidelity-ledger row served
`docs/observability/fidelity_evidence_ledger.json` →
`W1_6_physics_price_signal::ssp_residual_demand_scarcity_calibration_2026_07_19`.

The row's own per-cell lift table (measured against the best naive baseline `ols_regression_3feature`) shows the calibrated residual-demand scarcity model is **WORSE than the naive OLS baseline in 6 of 10 year-cells** (negative lift):

| cell | lift (MAE improvement over best naive) |
|------|------|
| y2016 | +2.23 |
| y2017 | +0.25 |
| y2018 | +0.04 |
| **y2019** | **−0.79** |
| **y2020** | **−3.22** |
| **y2021** | **−2.21** |
| y2022 | +5.55 |
| **y2023** | **−0.27** |
| **y2024** | **−1.18** |
| **y2025** | **−2.28** |

Full-window aggregate lift is only +1.17 MAE, carried almost entirely by the 2022 crisis year; in the calm/normal years the "physics" model *underperforms a 3-feature linear regression*.

## Ratified goal served
**DIRECTOR_AXES v1 — Axis 3 (Believability):** *wholesale prices ... does it feel like the real UK market to a 20-year veteran.* A scarcity-price model that only beats a linear fit during one crisis year, and loses in every calm year, is a believability defect a veteran would spot: the merit-order/residual-demand story is supposed to earn its structure in normal conditions, not just in 2022.

## Real-world fidelity gained
Closing (or honestly bounding) the negative-lift cells means the SSP the whole company prices, hedges and settles against behaves like the real merit order across regimes — not a crisis-only curve fit. Also guards the anti-goal-seek law (R12): the fix must be a *mechanism* diagnosis (R4), never tuning the output toward a benchmark.

## Scope (propose)
1. DISCOVER/FRAME (doc-only, always drawable): diagnose WHY the calm-year cells lose — is it the scarcity term dominating when residual demand is low, a conditioning-window artefact, or a genuine regime the structural form can't represent? Name the nearest working analogue (the 2022 cell that wins) and state the diff (R4).
2. Propose the mechanism change (structural, not a per-cell tune) OR, if the calm-year loss is irreducible under the honest structural form, register it as a **named simplification** (R10 class registration) with its measured bound — an honest "the residual-demand model earns its keep only in scarcity regimes" is a legitimate close, a silent +1.17 headline is not.
3. R13 discipline: any change to the SSP is a **baseline/fidelity-to-reality** change, decided blind to company P&L — never because company results look wrong.
4. Re-measure the per-cell lift and update the ledger row (the coupled-triad HARNESS gap).

## Walls untouched
R13 baseline wall (fidelity-only, P&L-blind); generator ground truth; no curriculum tuning. Doc/DISCOVER half is drawable now; any sim change proceeds under reversible-build authority.

## Propose-then-proceed window
DISCOVER/FRAME proceeds immediately (idle-drawable). A baseline-changing BUILD proceeds under reversible authority once the mechanism is named; if the honest answer is "register a simplification," that lands without a wall.
