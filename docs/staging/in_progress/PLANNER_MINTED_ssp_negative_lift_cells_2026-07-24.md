# [PLANNER-MINTED] Attack the SSP residual-demand model's NEGATIVE-lift cells (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 3). Attaches to existing atom `W1_6_physics_price_signal` (fidelity-ledger row `ssp_residual_demand_scarcity_calibration_2026_07_19`).
> **BLOCKING SUB-ITEM (open):** ~~Scope step 1 (DISCOVER/FRAME — diagnose WHY the calm-year cells lose to the OLS baseline, R4)~~ **DONE.** ~~Test A (dwell-fraction above X_TIGHT per cell)~~ **DONE this tick (2026-07-24 worker tick) — see "Test A RESULT" section appended below. Test A REFUTED the inferred "scarcity term dormant in calm years" sub-hypothesis: the term is live 17–55% of the time in EVERY year and dwell DECLINES secularly (renewables growth), and the 2022 crisis WIN-cell has among the LOWEST dwell (18.4%). The mechanism is redirected: a single GLOBAL fit against a secularly-drifting x-distribution (median x 0.73→0.46 over 2016→2025), not scarcity dormancy.** Scope step 2 BUILD (regime/time-aware calibration OR an R10 named simplification) proceeds under reversible authority, **strictly R13/R12-governed** (P&L-blind, mechanism-not-tuning). **UNBLOCKS:** self — no wall; the next drawable step is now **Test B** (diagnostic refit of A0/A1 on the drift-corrected / later-year x-distribution, holding the scarcity structure fixed) then the structural refit-vs-simplification decision.

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

---

## DISCOVER/FRAME diagnosis (2026-07-24 worker tick, R4) — the mechanism is named

**Evidence read (R9 — evidence before narrative):** `docs/observability/fidelity_evidence_ledger.json` (the per-cell row), `sim/price_engine.py` lines 18–103 (the model form + its calibration provenance + the constants). Every claim below is `observed-with-evidence` from those two files unless tagged `inferred`.

### The model form (observed, `sim/price_engine.py:132–166`)
`P_HH = P_gas_floor × multiplier`, where
`multiplier = A0 + A1·x + A2·max(0, x − X_TIGHT)^SCARCITY_EXPONENT`, `x = (demand − renewables) / DISPATCHABLE_CAPACITY_MW`.
Calibrated constants (`price_engine.py:98–103`): `A0=0.326998`, `A1=1.334629`, `A2=3.828327`, `X_TIGHT=0.70`, `SCARCITY_EXPONENT=2.0`, `DISPATCHABLE_CAPACITY_MW=35000`.
The A2 convex "scarcity kicker" is **exactly zero whenever `x ≤ 0.70`** (residual demand below 70% of dispatchable capacity). Below that threshold the model collapses to the **two-parameter line** `P_gas_floor × (A0 + A1·x)`.

### The calibration is a SINGLE GLOBAL fit (observed, `price_engine.py:56–61, 93–97`)
The docstring states the fit was done "**full window** … MAE-minimizing grid search over X_TIGHT/SCARCITY_EXPONENT, then closed-form least-squares for A0/A1/A2" over 2016‑03‑01..2025‑06‑07 (n=157,106), and reports it "beating … the 3-feature OLS regression (MAE=£33.96) **on the same window**" (model MAE=£32.79). So the model's entire published edge is an **aggregate-window** claim. A0/A1/A2 are one shared parameter set across all regimes.

### Root cause (two compounding effects — the "diff to the working analogue", R4)

The nearest working analogue is the winner it loses to: **`ols_regression_3feature`** (a per-window free-weight linear fit on 3 features). Two mechanisms explain every negative cell:

1. **Yardstick switch — the loss is co-timed with the baseline getting stronger, not the model getting worse.** The `best_baseline_id` per cell is `gas_floor_alone` for **2016/2017/2018** and switches to `ols_regression_3feature` for **2019 onward**. The model *wins* against the weak floor baseline (2016 +2.23, 2017 +0.25, 2018 +0.04) and *loses* against the strong OLS baseline in every calm cell from 2019 on. The sign flip is aligned to the *yardstick*, not to any change in the model. (Note the ledger tags **y2021 regime="crisis"**, not calm as the mint's summary table implied — so the true calm-year losers are 2019, 2020, 2023, 2024, 2025; 2021/2022 are crisis and 2022 is the +5.55 win. The mint's headline "6 of 10 calm cells lose" should read **5 calm cells lose to OLS; the model wins both the weak-baseline early years and the crisis peak**.)

2. **Compromise-fit — the scarcity tail poisons the calm-year line.** Because A0/A1 are fit *globally* to minimise full-window MAE, they are pulled by the crisis observations the A2 tail is meant to price. In calm years residual demand rarely crosses `x=0.70`, so A2 is dormant `[inferred — Test A below confirms]` and the model is effectively the global line `A0+A1·x`, whose slope/intercept were compromised to also serve 2021/2022. A dedicated per-cell OLS is under no such constraint and fits each calm cell's gas-passthrough directly — hence the 0.27–3.22 MAE it claws back. The gap is largest in **2020 (−3.22)** and **2025 (−2.28)**, the calm cells furthest in time from the crisis anchor `[inferred]`.

**This is not R12 goal-seek and not a model regression.** The +1.17 aggregate lift is real but *concentrated*: earned against the weak baseline pre-2019 and in the 2022 crisis peak. The believability defect (Axis 3) is that a 20-year veteran reading the per-cell table sees a merit-order model that only earns its structure in scarcity, and is beaten by a plain regression in normal conditions — the structure isn't paying its way where the market spends most of its time.

### Smallest closed-loop tests (R4 — cheapest first, both P&L-blind / R13-safe)
- **Test A (pure data, no refit — run first):** for each year-cell compute the fraction of half-hours with `x = (demand−renewables)/35000 > 0.70`. Prediction: near-zero in the 5 calm losing cells, materially positive in 2021/2022. Confirms the scarcity term is dormant in calm years → the model is effectively `A0+A1·x` there and the loss is a *linear-fit* loss, not a scarcity-form loss.
- **Test B (diagnostic refit — confirms the compromise mechanism):** re-fit **A0/A1 on calm-regime observations only** while holding the scarcity structure (X_TIGHT/SCARCITY_EXPONENT/A2) fixed, and re-measure calm-cell MAE. If the gap to OLS closes, the compromise-fit hypothesis is confirmed. This is a *diagnosis* refit against real Elexon SSP — fidelity-to-reality, P&L-blind (R13), and it does not tune toward a benchmark target (R12): it tests a mechanism claim.

### The two honest closes for scope-2 BUILD (walled to reversible authority, R13/R12-bound)
1. **Regime-aware calibration (structural, preferred):** fit the calm-regime linear coefficients on calm-regime data and the scarcity tail on tight observations, so the calm-year line is no longer distorted by the crisis anchor. The model already carries a `regime` tag per cell, so this is a *structural* change (one physics, regime-conditioned calibration), **not** a per-cell output tune. Success criterion is fidelity-to-real-SSP per cell, decided blind to company P&L.
2. **R10 named simplification (if the calm-year gap is irreducible under one honest global form):** register "the residual-demand merit-order form earns its structure in scarcity regimes; in calm regimes it trades up to ~£3/MWh MAE vs a per-cell linear refit, accepted because the form must be *one* physics across the window and scarcity is where merit-order pricing is commercially load-bearing" — with the measured per-cell residual. A silent +1.17 headline that hides the per-cell losses is **not** an acceptable close (R10 class registration required, not an instance fix).

**Next drawable step (no wall):** run Test A (a ~20-line data pass over the existing SSP/demand/renewables series — no sim change, no calibration change), attach the dwell-fraction table to this doc, then take the regime-aware-refit-vs-simplification decision. All of it stays P&L-blind (R13) and mechanism-not-target (R12).

---

## Test A RESULT — scarcity-term dwell fraction per year (DONE 2026-07-24 worker tick, R4/R13/R12-clean)

**Harness:** `tools/ssp_scarcity_dwell_fraction.py` — a pure data pass over the SAME series the model is calibrated against (`sim/cache/elexon_demand_full.json` demand + `sim/cache/elexon_agws_full.json` wind+solar), joined per `(settlementDate, settlementPeriod)`, using the model's OWN constants (`X_TIGHT=0.70`, `DISPATCHABLE_CAPACITY_MW=35000`, imported from `sim.price_engine`). No calibration constant touched, no company P&L read — R13 (fidelity-to-reality, P&L-blind) and R12 (mechanism, not benchmark-tuning) both hold by construction. Re-runnable: `python3 -m tools.ssp_scarcity_dwell_fraction`.

`x = (demand_mw − renewable_generation_mw) / 35000`. `dwell_fraction` = fraction of half-hours with `x > 0.70`, i.e. where the convex scarcity kicker `A2·(x−0.70)^2` is LIVE (it is exactly zero at or below the threshold).

| year | HH n | dwell_n (x>0.70) | **dwell_fraction** | median x | max x | lift (from ledger) | best baseline |
|------|-----:|-----:|-----:|-----:|-----:|-----:|---|
| 2016 | 14484 | 8025 | **0.554** | 0.730 | 1.41 | +2.23 win | gas_floor |
| 2017 | 17169 | 8219 | **0.479** | 0.689 | 1.36 | +0.25 win | gas_floor |
| 2018 | 17308 | 7807 | **0.451** | 0.673 | 1.32 | +0.04 win | gas_floor |
| 2019 | 17231 | 6569 | **0.381** | 0.635 | 1.30 | −0.79 LOSS | ols_3feat |
| 2020 | 16576 | 4031 | **0.243** | 0.545 | 1.23 | −3.22 LOSS | ols_3feat |
| 2021 | 16834 | 5153 | **0.306** | 0.601 | 1.26 | −2.21 LOSS (crisis) | ols_3feat |
| 2022 | 14967 | 2760 | **0.184** | 0.520 | 1.21 | +5.55 WIN (crisis) | ols_3feat |
| 2023 | 17463 | 3613 | **0.207** | 0.528 | 1.20 | −0.27 LOSS | ols_3feat |
| 2024 | 17523 | 3633 | **0.207** | 0.534 | 1.24 | −1.18 LOSS | ols_3feat |
| 2025 |  7570 | 1326 | **0.175** | 0.461 | 1.21 | −2.28 LOSS | ols_3feat |

(HH n < 17520/yr as expected: 2016 starts ~March per the cache coverage note; 2025 is a partial year to ~June. Coverage is sound for a distributional read.)

### What Test A REFUTES (evidence before narrative, R9)
The prior tick's DISCOVER/FRAME hypothesis 2 asserted, tagged `[inferred — Test A below confirms]`: *"In calm years residual demand rarely crosses x=0.70, so A2 is dormant."* **Test A refutes this.**
1. **The scarcity term is NOT dormant in any calm year** — it is live 17.5%–38.1% of the time in every "calm losing" cell (2019 0.38, 2020 0.24, 2023 0.21, 2024 0.21, 2025 0.18). "Rarely crosses" is false; it crosses one to two half-hours in five.
2. **Dwell does not separate winners from losers.** The 2022 cell WINS by the largest margin (+5.55) with among the LOWEST dwell (0.184) — *lower* than 2019/2020/2021 which all LOSE. If the scarcity kicker earned the wins, the +5.55 crisis cell would have the highest dwell; it does not. So the 2022 edge is the **gas-floor passthrough** catching the gas-crisis price level (`P = P_gas_floor × multiplier` — the floor tracks the crisis directly), NOT the scarcity term. `[inferred from the co-occurrence of the largest win with a low dwell; consistent with 2016–18 also winning against the weak gas_floor-alone baseline.]`

### What Test A REDIRECTS the diagnosis toward (the corrected mechanism)
**Secular distributional drift in x, not scarcity dormancy.** `median x` falls monotonically 0.730 (2016) → 0.461 (2025) as renewables penetration grows and residual demand shrinks. A **single global** A0/A1/A2 fit is centred on the whole-window x-distribution; it is therefore progressively **miscentred** for the later low-x years, exactly the calm cells that lose. A per-cell OLS re-centres on each year's own (lower) x-distribution and gas-passthrough regime, so it claws back 0.27–3.22 MAE. The compromise is not "crisis observations pull A2"; it is "one global line cannot sit correctly on a distribution whose centre moves ~0.27 in x across the decade AND whose gas-floor level regime-shifts."

### Consequence for the scope-2 decision (unchanged shortlist, better-grounded)
- **Regime/time-aware calibration (preferred, structural):** condition A0/A1 on the x-distribution regime (equivalently on era/renewables-penetration), holding the scarcity structure (X_TIGHT/exponent/A2) fixed — one physics, drift-aware calibration. Success = fidelity-to-real-SSP per cell, decided blind to P&L (R13). **Test B is the confirming step:** re-fit A0/A1 on later-year (low-x) observations only, hold the scarcity tail fixed, re-measure the calm-cell MAE; if the gap to OLS closes, drift-miscentring is confirmed as the mechanism.
- **R10 named simplification (fallback):** register "a single global residual-demand line trades up to ~£3/MWh MAE in the low-x renewables-heavy later years vs a per-era refit, accepted because the form must be one physics across the window" — with the measured per-cell residual. Still requires class registration, not an instance patch.

**Walls untouched:** doc-only + one new diagnostic tool; no SSP constant changed, no level moved, no curriculum value chosen, no company P&L read. `tools/ssp_scarcity_dwell_fraction.py` is a DIAGNOSTIC (measures the model), not a control gating any promotion — R15 mutation-testing applies to controls, N/A here.
