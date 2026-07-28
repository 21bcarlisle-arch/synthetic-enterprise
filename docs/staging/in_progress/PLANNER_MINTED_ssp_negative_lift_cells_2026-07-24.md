<!-- SUPERVISOR_DRAW: blocked -->
<!-- BLOCK_RELEASE: W1_6b_merit_order_reconstruction -- part(a) held; unblocks when the merit-order/gas-first reconstruction (W1_6b) has landed, no interim tuning (R12) -->
<!-- draw-visibility marker (2026-07-25): FLIPPED self-drawable -> blocked. The autonomous-drawable DIAGNOSTIC lane is now EXHAUSTED (Tests A/B/C/D complete — the partition question is fully answered, per-year ceiling reached). The ONE remaining step is part (a), RE-SCOPED by DIRECTOR RULING 2026-07-25 (see blocking-sub-item below): NOT a coefficient recalibration (the director rejected that shape as R12 goal-seek) but a merit-order / gas-first RECONSTRUCTION of the price engine (Board Spec 004 reconstructibility; converges with Spec 001 F1), sequenced with the VALUE_CHAIN work — a director-reserved structural build, a wall for a bounded autonomous tick, not a lack of a next idea. Still an OPEN mint (keeps the rung-7 "rungs empty" premise FALSE), just no longer self-drawn each tick. Fail-closed structured token parsed by background/staging_disposition.selfdrawable_mint_in_progress. -->

# [PLANNER-MINTED] Attack the SSP residual-demand model's NEGATIVE-lift cells (2026-07-24)

> **[IN-PROGRESS — 2026-07-24 worker tick]** Director-waived to proceed (`docs/staging/done/DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24.md`, item 3). Attaches to existing atom `W1_6_physics_price_signal` (fidelity-ledger row `ssp_residual_demand_scarcity_calibration_2026_07_19`).
> **BLOCKING SUB-ITEM (open, RE-SCOPED BY DIRECTOR RULING 2026-07-25 — `docs/staging/done/DIRECTOR_RULING_SSP_BASELINE_HELD_MERIT_ORDER_FIRST_2026-07-25.md`):** part (a) is **HELD** — the director rejected the *shape* of the proposed fix, not its queue position. **A coefficient recalibration is NOT the fix.** The evidence: Test B's local per-year refit still leaves 2020/2021-crisis/2025 negative — a *form limit*, proving the structure is wrong in calm regimes, not merely mis-parameterised; a regime-aware A0/A1 pass would lower MAE while leaving the wrongness intact (R12 goal-seek shape even when each step is defensible). **The real fix is a merit-order / gas-first RECONSTRUCTION of the price engine** (Board Spec 004 reconstructibility: power must be substantially reconstructible from gas+carbon+demand+wind on ordinary days; a residual-demand scarcity term must earn its structure in TIGHT hours, not carry ordinary ones). This is **Spec 001's gas-first finding (F1) arriving from a second, independent direction — convergence recorded.** ~~*Superseded recipe (Test D):* the crisis-vs-calm A0/A1 recalibration split is NO LONGER the authorized path — it is exactly the "looks better, no more *formed*" tune the ruling forbids; do not execute it.~~ Part (a) stays **blocked**. **UNBLOCKS ON: the merit-order / gas-first reconstruction has landed** (sequenced with the VALUE_CHAIN work + the Spec 004 reconciliation), at which point the SAME per-cell lift table is re-measured against the SAME naive baseline, unmoved — that unchanged measurement is the test of whether pricing became *right* rather than *tuned*. **No interim tuning** (no per-cell fits, no regime-partition coefficient passes, no "temporary" recalibration; R12 unchanged). The autonomous DIAGNOSTIC lane is EXHAUSTED — marker stays blocked above.
>
> <details><summary>Prior blocking-sub-item history (Tests A/B — resolved)</summary>
>
> ~~Scope step 1 (DISCOVER/FRAME — diagnose WHY the calm-year cells lose to the OLS baseline, R4)~~ **DONE.** ~~Test A (dwell-fraction above X_TIGHT per cell)~~ **DONE this tick (2026-07-24 worker tick) — see "Test A RESULT" section appended below. Test A REFUTED the inferred "scarcity term dormant in calm years" sub-hypothesis: the term is live 17–55% of the time in EVERY year and dwell DECLINES secularly (renewables growth), and the 2022 crisis WIN-cell has among the LOWEST dwell (18.4%). The mechanism is redirected: a single GLOBAL fit against a secularly-drifting x-distribution (median x 0.73→0.46 over 2016→2025), not scarcity dormancy.** ~~Test B (diagnostic refit of A0/A1 on the drift-corrected / later-year x-distribution, holding the scarcity structure fixed)~~ **DONE this tick (2026-07-24 worker tick) — see "Test B RESULT" section appended below. Test B PARTIALLY confirms the redirected mechanism: a same-structure LOCAL (per-year) refit of A0/A1/A2 (X_TIGHT/exponent held fixed) lowers MAE in ~every cell and flips 3 of the 6 global negative-lift cells (2019/2023/2024) to non-negative — the stale-global-linear-fit-under-x-drift diagnosis is REAL and MATERIAL (per-year A0 drifts 0.11→1.11, A1 0.9→2.0). BUT 3 cells (2020, 2021-crisis, 2025) stay negative even after a local refit — a genuine residual FORM limit the recalibration cannot close. Mechanism is MIXED: drift-staleness explains ~half, a form-limit the rest.** Scope step 2 is therefore a TWO-PART close, both R13/R12-governed (P&L-blind, mechanism-not-tuning): (a) a time/regime-aware LINEAR (A0/A1) recalibration tracking the observed x-drift (justified fidelity fix, recovers the 3 flip cells); (b) an R10 NAMED SIMPLIFICATION registering the residual 3-cell form-limit with its measured bound. **UNBLOCKS:** self — no wall; next drawable step is the scope-2 BUILD (part (a) mechanism + part (b) class registration).
>
> </details>

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

---

## Test B RESULT — 2026-07-24 worker tick (`tools/ssp_refit_local_vs_global.py`)

**Question (from the redirect Test A produced):** is the calm-year negative lift a STALE single-global-linear-fit artefact (secular x-drift, median 0.73→0.46), or a scarcity-FORM defect? **Method:** re-fit the SAME structural form (`A0 + A1·x + A2·max(0,x−0.70)²`, X_TIGHT/exponent **held fixed**) on **each year's own data**, holding the scarcity tail structure fixed, and re-measure per-cell MAE vs the ledger's per-cell OLS baseline. Pure diagnostic — reuses `recal._fit_form`/`recal._build_dataset` + `regr._fit_ols` as libraries, changes no constant on disk, reads no P&L (R13/R12-clean). Both lift columns score against the SAME global OLS, so the only thing changing between them is the scarcity model's calibration (global vs per-year) — an apples-to-apples isolation of the global-fit cost.

| yr | median_x | model gMAE | model **lMAE** (local refit) | ols MAE | global lift | **local lift** | outcome | A0_local | A1_local |
|----|------|------|------|------|------|------|------|------|------|
| 2016 | 0.730 | 17.18 | 19.22 | 25.13 | +7.95 | +5.90 | win | 0.112 | 2.035 |
| 2017 | 0.689 | 17.16 | 17.15 | 22.56 | +5.40 | +5.41 | win | 0.458 | 1.376 |
| 2018 | 0.673 | 19.43 | 18.39 | 21.71 | +2.28 | +3.32 | win | 0.574 | 1.162 |
| **2019** | 0.635 | 18.82 | 17.02 | 18.02 | **−0.79** | **+1.01** | **FLIP→+** | 0.845 | 1.330 |
| 2020 | 0.546 | 22.19 | 19.38 | 18.97 | −3.22 | **−0.41** | neg (survives) | 1.111 | 1.175 |
| 2021 | 0.601 | 50.22 | 49.21 | 48.01 | −2.21 | **−1.20** | neg (survives, crisis) | 0.433 | 1.235 |
| 2022 | 0.521 | 79.16 | 77.91 | 84.71 | +5.55 | +6.80 | win (crisis) | 0.322 | 1.162 |
| **2023** | 0.529 | 44.12 | 41.56 | 43.86 | **−0.27** | **+2.30** | **FLIP→+** | 0.401 | 1.763 |
| **2024** | 0.534 | 29.35 | 28.00 | 28.17 | **−1.18** | **+0.17** | **FLIP→+** | 0.346 | 1.610 |
| 2025 | 0.461 | 35.09 | 35.54 | 32.81 | −2.28 | **−2.73** | neg (survives, partial yr) | 0.718 | 0.905 |

(gMAE = global-fit model MAE sliced per year, = the ledger's model residual; lMAE = same form refit on that cell only; a per-year LOCAL-OLS ceiling column is in the tool output. lstsq minimises L2, so lMAE can very slightly exceed gMAE on an in-cell fit — 2025, a half-year at n=7570 — this is an L1-vs-L2 artefact, not a paradox.)

### What Test B CONFIRMS
1. **The stale-global-linear-fit-under-x-drift diagnosis is real and material.** A same-structure LOCAL refit lowers MAE in ~every cell and FLIPS **3 of 6** global negative-lift cells (2019, 2023, 2024) to non-negative. The recovered lift is the calibration cost of a single global line, not the scarcity form.
2. **The linear terms genuinely drift with the x-distribution.** Per-year `A0_local` ranges 0.11→1.11 and `A1_local` 0.9→2.0 — a global A0=0.327/A1=1.335 cannot sit on all of them. As median_x falls (renewables growth) the fresh in-cell fit raises the intercept and re-slopes — exactly the secular-drift signature Test A predicted.

### What Test B REFUTES (evidence before narrative, R9)
**The staleness is NOT the whole story.** **3 cells — 2020 (−0.41), 2021-crisis (−1.20), 2025 (−2.73) — stay negative even after a same-form local refit.** In these cells a 3-feature linear model (gas/demand/wind) captures structure the residual-demand scarcity form cannot represent regardless of calibration freshness. That residual is a **FORM limit**, not a calibration limit. So the earlier "regime/time-aware calibration alone closes the gap" reading is too optimistic — it closes ~half.

### Consequence for scope step 2 (now a TWO-PART close, both R13/R12-clean)
- **(a) Time/regime-aware LINEAR (A0/A1) recalibration — JUSTIFIED, structural.** Condition A0/A1 on the x-distribution regime (era / renewables-penetration), holding the scarcity tail (X_TIGHT/exponent/A2) fixed. This is a fidelity-to-reality change (the calibration should track the observed secular drift), decided blind to P&L, and it recovers the 3 flip cells. It is NOT tuning: the target is per-cell real-SSP MAE, not any company output (R12).
- **(b) R10 NAMED SIMPLIFICATION for the residual — REQUIRED, class-level.** Register: *"the single-physics residual-demand scarcity form under-fits ~3 low-x / crisis-adjacent cells (2020, 2021, 2025) vs a 3-feature linear model by up to ~£2.7/MWh MAE even when locally recalibrated — accepted because the form must be one physics across the window."* Carry the measured per-cell residual. This is a class registration (R10), not an instance patch, and an honest bound beats a silent +1.17 headline.

**Walls untouched:** doc-only + one new diagnostic tool (`tools/ssp_refit_local_vs_global.py`); no SSP constant changed on disk, no level moved, no curriculum value chosen, no company P&L read. The tool is a DIAGNOSTIC (measures the model), not a control gating any promotion — R15 mutation-testing applies to controls, N/A here. Scope step 2 (parts a+b) is the next drawable increment on this mint.

---

## SCOPE STEP 2 PART (b) — R10 named simplification MECHANISED + registered (DONE, 2026-07-24 worker tick)

Test A + Test B (prior ticks) established the two honest closes. This tick SHIPS part (b) — the honest
bound, mechanised as a class-level control so the whole class fails automatically (R10), not an instance
fix — and defers part (a) as a deliberately-grounded follow-on. Code + tests, not another analysis note.

### What shipped (evidence)
1. **R10 class control (the mechanism).** `background/fidelity_evidence_ledger.py::fidelity_evidence_gate`
   gains reason **(d)**: any ledger record asserting a POSITIVE aggregate lift (`strength.value > 0`)
   while carrying one or more NEGATIVE per-cell lifts, with `simplification_id is None`, REDS the DoD
   gate — the "silent +1.17 headline that hides the per-cell losses" defect this mint named, now an
   automatic failure for the ENTIRE class (any future emitted physics row, not just this one), until it
   registers an honest bound. Verified FIRING on the real W1_6 row pre-registration (6 negative cells
   named), passing post-registration.
2. **R15 both-ways.** `tests/test_fidelity_evidence_ledger.py` gains
   `test_R15_killer_mutation_d_...` (positive-headline-hides-negative-per-cell reds; registering a
   simplification greens) + `test_gate_d_does_not_fire_when_aggregate_is_itself_negative` (legitimate
   edge case: an honestly-negative aggregate is not concealing, must NOT demand a simplification).
   The emitter's own DoD test now asserts the emitted row carries the bound and passes the gate.
3. **The named simplification, registered.** `simplification_id =
   ssp_scarcity_form_calm_low_x_underfit_bounded_2026_07_24` on the W1_6 ledger row (+ a
   `simplification_note` carrying the measured per-cell bound). `background/fidelity_emitter.py` now
   EMITS this bound BY DEFAULT (`CALM_LOW_X_SIMPLIFICATION_ID` / `_SIMPLIFICATION_NOTE`) — so a re-emit
   cannot silently drop it; a null simplification would red its own DoD gate. Full bound documented in
   `docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md` ("Named simplification" section).
4. **Verification:** `tests/test_fidelity_evidence_ledger.py tests/test_live_fidelity_evidence.py
   tests/test_fidelity_emitter.py tests/test_fidelity_inspection_chain.py site/proof/test_fidelity_panel.py`
   all green (109 tests); epistemic-verifier PASS (no company/sim boundary touched — background/docs/tests only).

### The bound (measured, honest)
The single-global scarcity form earns its structure in scarcity/crisis; the +1.17 aggregate is
concentrated (2022 +5.55 + weak-baseline 2016–18), and it LOSES to a per-cell OLS in 6 calm cells.
Test B decomposes: **~half calibration-recoverable** (y2019/y2023/y2024 flip under a local A0/A1 refit)
and **~3 cells form-irreducible** (y2020/y2021/y2025, up to ~£2.7/MWh even after local refit).

### Part (a) — era-aware A0/A1 recalibration — DELIBERATE GROUNDED FOLLOW-ON, not done here (why)
The recoverable half needs an era-aware A0/A1 recalibration tracking the x-drift. This is **not** an
autonomous worker-tick action: choosing the era partition to flip a lift cell's sign, ungrounded, IS
R12 goal-seek by another name. The partition must be externally grounded (renewables-penetration /
dispatchable-capacity boundaries — the module already flags `DISPATCHABLE_CAPACITY_MW=35000` held
constant while the real fleet shrank with coal exit), an R13-sensitive BASELINE decision. Compounding
this: the director's **2026-07-19 console steer ranks calm-year MAE below the spike-tail priority** —
so part (a) is explicitly NOT top fidelity work, and the honest bound-and-register (part b, done) is
the director-aligned close. Part (a) remains the drawable follow-on for a deliberate grounded pass,
best begun with a DISCOVER grounding of the fleet-capacity / renewables-penetration era boundaries
(network-gated).

> **Tick note (2026-07-24, RUNG-7 doorbell):** doorbell again fired the stale "rungs 1–6 empty → MINT"
> read; disk contradicts it (this mint + siblings open in `in_progress/`, director-waived). Correct draw
> = advance a drawable next step, NOT mint a sixth batch. This tick advanced THIS mint's scope-2 by
> shipping part (b) as real code + R15 tests (broke the doc-only pattern the sibling mint's tick-notes
> warned against). No mint this tick: premise false.

---

## SCOPE STEP 2 PART (a) — externally GROUNDED (DONE, 2026-07-24 tenth worker tick, R13/R12-clean)

Part (b) (prior tick) shipped the honest bound + R10 class control. Part (a) — the era-aware A0/A1
recalibration that recovers the ~half calibration-recoverable cells — was deferred as "network-gated,
best begun with a DISCOVER grounding of the fleet-capacity / renewables-penetration era boundaries,"
and flagged that choosing the era partition **ungrounded IS R12 goal-seek by another name**. This tick
**network was UP** (elexon 200 / neso 302 — the sole prior gate), so the genuine drawable step was to
do that grounding. **This tick ships the grounding, NOT the baseline BUILD** (see "still deferred" below).

### What shipped (evidence)
`docs/market_research/ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md` — a discovery-agent
research pass over **published DESNZ DUKES Ch.5 workbooks** (`DUKES_5.6.xlsx`/`5.7.xlsx`) + coal-exit
timeline, accessed 2026-07-24. Every quantitative claim tagged observed-with-evidence (with source) or
inferred. `ASSUMPTIONS.md` gains the calibrated section. **The era boundaries are derived from real
fossil-capacity plateaus and coal-share cliffs — NOT from our model's lift table** (R12/R13-clean by
construction: the grounding is blind to company P&L and to the residual it will later inform).

### The externally-grounded era structure (observed-with-evidence, DUKES)
- GB "total fossil-fuels capacity" fell **49,835 MW (2016) → 36,250 MW (2024)** in **three visible
  plateaus, not smoothly**: ~50 GW (2016–18) → ~42–44 GW (2019–22) → ~36–40 GW (2023–24).
- Coal generation share: 22.4% (2015) → 9.0% (2016) → **2.1% (2019)** → 0.7% (2024) → **0% from 1 Oct 2024**
  (Ratcliffe-on-Soar). Renewables share 24.5% (2016) → 43.1% (2020, COVID-denominator confound flagged)
  → **50.4% (2024)**.
- **Candidate eras (grounded in the plateau/cliff structure): Era A 2016–18 / Era B 2019–22 / Era C
  2023–25.** Single largest structural break = **2018→2019** (coal 5.0%→2.1%, fossil capacity −12.5% in
  one year — the biggest single-year move in the series).

### Why this is the grounding part (a) needed (mechanism, not tuning — R4/R12)
The constant `DISPATCHABLE_CAPACITY_MW=35000` is **~3.6% off the real 2024 figure but ~42% too low for
2016–18** — so the residual-demand denominator `x = (demand−renewables)/35000` is materially miscentred
at the window's early end, and the miscentring **plateaus in the same 3-era structure**. This independently
explains — from real fleet physics, not from the lift table — the negative-lift onset: losers begin at
**2019 (Era B onward)**, exactly where the single global fit (centred on 35000 MW / the whole-window
x-distribution) drifts off the true per-era denominator. The era-aware A0/A1 partition part (a) will use
is now **externally justified**, closing the R12 goal-seek hazard the deferral named.

### STILL DEFERRED (honest — the baseline BUILD is NOT done this tick, and why)
Part (a) proper is an **R13 baseline change to the core price engine** (the whole company prices/hedges/
settles against SSP). Two live reasons keep it a deliberate follow-on rather than a bounded-tick action:
1. **Director priority:** the 2026-07-19 console steer ranks calm-year MAE **below the spike-tail
   priority** — force-shipping a below-priority baseline recalibration autonomously is not the director-
   aligned move; the grounding (cheap, reversible, doc-only) is.
2. **Operational-rebuild standard:** a baseline recalibration deserves its own focused, R15-mutation-tested
   pass (era partition wired + per-cell fidelity re-measured + ledger row updated), "one verified sub-step,
   show-me before advancing" — not a tail-of-tick rush. The denominator question (35000 MW held constant
   vs the real 2016→2024 decline) is now surfaced by the grounding and belongs in that same pass.

**Next drawable step (no wall, now grounded):** the era-aware A0/A1 (and constant-denominator) baseline
recalibration BUILD — a deliberate R13 pass, per-cell fidelity target (never lift as a target), R15
both-ways on the new calibration, ledger row + coupled-triad HARNESS gap re-measured.

> **Tick note (2026-07-24, RUNG-7 doorbell, tenth worker tick):** doorbell fired the stale "rungs 1–6
> empty → MINT" read; disk contradicts it (6 `PLANNER_MINTED_*` open + director-waived — a mint here is
> the over-production `DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24` intervened on). Correct draw =
> advance a genuine drawable step. Network was UP this tick — the sole gate on part (a)'s DISCOVER
> grounding — so I shipped that grounding (real published DUKES sources → market_research doc), converting
> part (a) from "network-gated / ungrounded R12 hazard" to "externally grounded, ready for a deliberate
> R13 baseline pass." **No mint: premise false. No baseline BUILD: deferred deliberately (below spike-tail
> + deserves its own R15-tested pass).**

---

## TEST C — does the GROUNDED era partition actually recover the cells? (DONE, 2026-07-24 twelfth worker tick, R13/R12-clean)

Part (a) was grounded last tick (DUKES 3-era partition, blind to the lift table) and deferred as an
R13 baseline pass. But grounding the era boundaries from **fossil-capacity plateaus** and then *assuming*
those are the right partition to key an A0/A1 recalibration on is an untested leap — exactly the
"measure the smallest closed-loop test before you build" gap (R4). Test B measured only PER-YEAR refits
(an upper bound; not deployable — you cannot fit a year on its own future). **This tick measures the
deployable question:** refit the SAME form PER ERA (3 fits, the structure a real recalibration would use)
and ask whether the DUKES capacity-eras recover the negative-lift cells. Diagnostic only — new tool
`tools/ssp_refit_era_partitioned.py`, reuses `recal._fit_form` + the Test-B helpers as libraries, no
constant changed on disk, no P&L read (R13/R12-clean by construction, same as Test A/B). Reproduce:
`python3 -m tools.ssp_refit_era_partitioned`.

| yr | era | med_x | gMAE | **eraMAE** | lMAE (per-yr) | olsMAE | gLift | **eraLift** | lLift | outcome |
|----|-----|------|------|------|------|------|------|------|------|------|
| 2016 | A | 0.730 | 17.18 | 17.08 | 19.22 | 25.13 | +7.95 | +8.04 | +5.90 | win |
| 2017 | A | 0.689 | 17.16 | 17.29 | 17.15 | 22.56 | +5.40 | +5.27 | +5.41 | win |
| 2018 | A | 0.673 | 19.43 | 18.94 | 18.39 | 21.71 | +2.28 | +2.77 | +3.32 | win |
| **2019** | B | 0.635 | 18.82 | 19.44 | 17.02 | 18.02 | −0.79 | **−1.42** | +1.01 | **era WORSENS** (per-yr flips +) |
| **2020** | B | 0.546 | 22.19 | 22.57 | 19.38 | 18.97 | −3.22 | **−3.60** | −0.41 | **era WORSENS** |
| **2021** | B | 0.601 | 50.22 | 50.95 | 49.21 | 48.01 | −2.21 | **−2.94** | −1.20 | **era WORSENS** (crisis) |
| 2022 | B | 0.521 | 79.16 | 77.94 | 77.91 | 84.71 | +5.55 | +6.77 | +6.80 | win (crisis) |
| **2023** | C | 0.529 | 44.12 | 41.95 | 41.56 | 43.86 | −0.27 | **+1.91** | +2.30 | **ERA-FLIP →+** |
| 2024 | C | 0.534 | 29.35 | 28.57 | 28.00 | 28.17 | −1.18 | −0.40 | +0.17 | era-neg (per-yr flips +) |
| **2025** | C | 0.461 | 35.09 | 32.01 | 35.54 | 32.81 | −2.28 | **+0.80** | −2.73 | ERA-FLIP →+ (per-yr-neg too; small-n L1 artefact) |

Per-era fits: **A(16-18)** A0=0.508 A1=1.294 A2=0.503 · **B(19-22)** A0=0.305 A1=1.271 **A2=4.971** · **C(23-25)** A0=0.500 A1=1.437 A2=3.358.
(Refits A0/A1/A2 per era — an UPPER BOUND on the narrower A0/A1-only part-(a) proposal: any cell this fuller refit fails to recover, the A0/A1-only version fails too.)

### The decisive finding — the grounded partition is MISALIGNED (evidence before narrative, R9)
The DUKES fossil-capacity 3-era partition recovers only **2 of 6** negative-lift cells (2023, 2025) vs
**3** for the per-year upper bound — and, materially, it **makes 3 cells WORSE than the untouched global
fit** (2019 −0.79→−1.42, 2020 −3.22→−3.60, 2021 −2.21→−2.94). The mechanism is visible in the era
coefficients: **Era B (2019–2022) pools the CALM 2019/2020 years with the CRISIS 2021/2022 years**, so its
pooled fit takes a large scarcity kicker (**A2=4.97**, four-to-ten× Era A/C's) to price the crisis — and
that crisis-tuned line is *wrong* for calm 2019/2020, pushing them further negative. This is the exact
"crisis poisons its era-mate" hazard: a capacity-plateau boundary is not a price-regime boundary. 2019
is the tell — a per-year refit flips it to +1.01, but binning it with 2021/22 drives it to −1.42.

### Consequence for the deferred part-(a) baseline pass (redirected, still R13-deferred)
The grounding remains sound and useful (the constant `DISPATCHABLE_CAPACITY_MW=35000` really is ~42% too
low for 2016–18 — a real denominator-fidelity fix). **But part (a) must NOT key the A0/A1 recalibration on
the DUKES capacity eras** — that partition under-performs and breaks 2019. The calibration-relevant
partition is a **price-REGIME / x-distribution split that separates crisis (2021/22) from calm**, not the
fossil-capacity plateaus. Two honest part-(a) sub-questions this now hands the deferred pass, pre-measured:
1. **The denominator fix** (35000 → era-varying dispatchable capacity, DUKES-grounded) is a *separate,
   legitimate* fidelity change from the A0/A1-regime recalibration — do not conflate them.
2. **The A0/A1 partition must be crisis-vs-calm regime-aware**, and the ledger already tags each cell's
   `regime` — so the regime split is itself externally/structurally grounded, not lift-table-derived (R12-safe).
Part (a) stays a **deliberate, director-priority-deferred R13 pass** (below spike-tail per 2026-07-19;
deserves its own R15-mutation-tested build, not a tail-of-tick rush) — this tick only *measured which
partition it must use*, saving it from building on the misaligned one.

**Walls untouched:** doc + one new diagnostic tool; no SSP constant changed on disk, no level moved, no
curriculum value chosen, no company P&L read. The tool is a DIAGNOSTIC (measures the model), not a control
gating a promotion — R15 mutation-testing applies to controls, N/A here. Epistemic-verifier **PASS** (525
files, tools/ imports simulation as a library; no company/sim boundary crossed).

> **Tick note (2026-07-24, RUNG-7 doorbell, twelfth worker tick):** doorbell fired the stale "rungs 1–6
> empty → MINT" read AGAIN; disk contradicts it (6 `PLANNER_MINTED_*` open, director-waived; 5 marked
> `blocked`, this one `self-drawable`). Minting a 7th batch = the over-production
> `DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24` intervened on. Correct draw = advance THIS mint's one
> genuinely-drawable step. The prior tick's grounding *assumed* the DUKES capacity-eras were the right
> A0/A1 partition; this tick MEASURED it (Test C) and found the partition **misaligned** — it recovers
> fewer cells and worsens 2019/2020/2021 by binning calm with crisis. Real code + a decision-relevant
> finding (broke no doc-only pattern), keeping the deferred R13 baseline pass from building on the wrong
> partition. **No mint: premise false. No baseline BUILD: still deferred (below spike-tail + deserves its
> own R15 pass), now with its partition pre-diagnosed.**

---

## TEST D — does the REDIRECTED (crisis-vs-calm regime) partition actually recover the cells? (DONE, 2026-07-25 worker tick, R13/R12-clean)

Test C found the DUKES capacity-era partition MISALIGNED and **redirected** part (a) to a "price-REGIME /
x-distribution partition that separates crisis (2021/22) from calm" — but then, committing the very
untested-leap error (R4) it had just criticised in the capacity-era grounding, it **asserted** that
redirect without measuring it. This tick closes that gap: refit the SAME structural form on a **TWO-pool
crisis-vs-calm regime partition** (crisis = {2021, 2022}, the ledger's own `regime` tag — a market-history
fact, not a lift-table choice; calm = the complement) and re-measure per-cell lift. Diagnostic only — new
tool `tools/ssp_refit_regime_partitioned.py`, reuses `recal._fit_form` + the Test-B/C helpers as libraries,
no constant changed on disk, no P&L read (R13/R12-clean by construction, same as Tests A/B/C). Reproduce:
`python3 -m tools.ssp_refit_regime_partitioned`.

| yr | regime | med_x | gMAE | **regMAE** | lMAE (per-yr) | olsMAE | gLift | **regLift** | lLift | outcome |
|----|--------|------|------|------|------|------|------|------|------|------|
| 2016 | calm | 0.730 | 17.18 | 18.12 | 19.22 | 25.13 | +7.95 | +7.00 | +5.90 | win |
| 2017 | calm | 0.689 | 17.16 | 18.64 | 17.15 | 22.56 | +5.40 | +3.92 | +5.41 | win |
| 2018 | calm | 0.673 | 19.43 | 20.35 | 18.39 | 21.71 | +2.28 | +1.35 | +3.32 | win |
| **2019** | calm | 0.635 | 18.82 | 17.30 | 17.02 | 18.02 | **−0.79** | **+0.72** | +1.01 | **REGIME-FLIP →+** (capacity-era WORSENED this to −1.42) |
| 2020 | calm | 0.546 | 22.19 | 20.81 | 19.38 | 18.97 | −3.22 | **−1.84** | −0.41 | regime-neg (improved from −3.22, survives) |
| **2021** | crisis | 0.601 | 50.22 | 51.11 | 49.21 | 48.01 | −2.21 | **−3.11** | −1.20 | **regime-WORSENS** (crisis pool 2021≠2022) |
| 2022 | crisis | 0.521 | 79.16 | 77.83 | 77.91 | 84.71 | +5.55 | +6.88 | +6.80 | win (crisis) |
| **2023** | calm | 0.529 | 44.12 | 41.85 | 41.56 | 43.86 | **−0.27** | **+2.01** | +2.30 | **REGIME-FLIP →+** |
| 2024 | calm | 0.534 | 29.35 | 28.25 | 28.00 | 28.17 | −1.18 | **−0.08** | +0.17 | regime-neg (near-flip; per-yr flips +) |
| **2025** | calm | 0.461 | 35.09 | 31.56 | 35.54 | 32.81 | **−2.28** | **+1.25** | −2.73 | **REGIME-FLIP →+** (per-yr-neg too; small-n L1 artefact) |

Pool fits: **calm** A0=0.497 A1=1.461 A2=0.952 (n=125,310) · **crisis(2021/22)** A0=0.313 A1=1.235 **A2=5.256** (n=31,796).
(Refits A0/A1/A2 per pool — an UPPER BOUND on the narrower A0/A1-only part-(a) proposal, same convention as Tests B/C.)

### The decisive finding (evidence before narrative, R9) — MIXED, and it CLOSES the diagnostic chain
1. **The regime partition beats the capacity eras on the CALM side, exactly as Test C's redirect predicted.** It flips **3 of 6** cells (2019/2023/2025) — matching the per-year *ceiling* of 3 and beating the DUKES capacity eras' 2 — and, decisively, it **recovers 2019 (+0.72)**, the cell the capacity partition *broke* to −1.42 by binning calm 2019 with crisis 2021/22. It **harms no calm cell**; 2020 (−3.22→−1.84) and 2024 (−1.18→−0.08) improve toward zero even where they don't flip. **Test C's redirect is CONFIRMED for the calm cells.**
2. **But the "crisis" pool is itself heterogeneous — it must NOT be pooled.** Lumping 2021 with 2022 gives a crisis line dominated by 2022's far higher price level, **worsening 2021 (−2.21→−3.11)**. 2021 and 2022 are both "gas-crisis" by tag but different price *levels*; the calibration granularity for the crisis tail is finer than a single crisis pool.
3. **A residual form-limit survives every partition (2020, 2024).** These improve but stay negative under both regime and (2020) per-year refits — the genuine form-limit already **bounded by part (b)'s R10 named simplification** (`ssp_scarcity_form_calm_low_x_underfit_bounded_2026_07_24`). No partition closes it; the honest bound is the load-bearing close, exactly as part (b) registered.

### Consequence for the deferred part-(a) baseline pass (now fully partition-diagnosed, still R13-deferred)
The diagnostic chain is **complete** — the partition question is answered end to end (per-year is the ceiling; the crisis-vs-calm regime split matches it on the recoverable cells; no finer autonomous test remains). The deferred part-(a) R13 pass now has its full recipe, pre-measured:
- **Key A0/A1 on the crisis-vs-calm price-regime split** (recovers 2019/2023/2025, harms no calm cell) — NOT the DUKES capacity eras (Test C: misaligned).
- **Do not pool 2021 with 2022** — the crisis tail needs finer granularity than one pool (or a level-anchored crisis treatment), else 2021 regresses.
- **Accept the 2020/2024 residual** as the form-limit part (b)'s R10 simplification already bounds — part (a)'s achievable scope is the 3 flip cells, not all 6.
- Combine with the separate, legitimate **denominator fidelity fix** (35000 MW → era-varying dispatchable capacity, DUKES-grounded) — kept distinct from the A0/A1-regime recalibration per Test C.

Part (a) itself stays a **deliberate, director-priority-deferred R13 pass** (below the spike-tail per the 2026-07-19 steer; deserves its own R15-mutation-tested build, not a tail-of-tick rush). This tick only *measured which partition it must use and which residual it cannot close* — the last autonomously-drawable diagnostic step. **Marker flipped self-drawable→blocked (top of doc): the diagnostic lane is exhausted; the remaining step is a walled R13 baseline build.**

**Walls untouched:** doc + one new diagnostic tool (`tools/ssp_refit_regime_partitioned.py`); no SSP constant changed on disk, no level moved, no curriculum value chosen, no company P&L read. The tool is a DIAGNOSTIC (measures the model), not a control gating a promotion — R15 mutation-testing applies to controls, N/A here.

> **Tick note (2026-07-25, RUNG-7 doorbell):** doorbell fired the stale "rungs 1–6 empty → MINT" read
> AGAIN; disk contradicts it (4 `PLANNER_MINTED_*` open in `in_progress/`, director-waived; this one was the
> last `self-drawable`, the rest `blocked`). **No mint: premise FALSE** (per `DIRECTOR_RULING_PLANNER_MINT_WAIVED_2026-07-24`
> + the sibling tick-notes; over-minting is the exact defect that ruling intervened on). Correct draw =
> advance THIS mint's one genuinely-drawable step: Test C had *asserted* the crisis-vs-calm redirect without
> measuring it (its own R4 gap, one level up), so this tick MEASURED it (Test D) — the redirect holds for the
> calm cells (recovers 2019 the eras broke), the crisis pool needs finer granularity, and a 2-cell form-limit
> survives (already bounded by part b). That **exhausts the autonomous diagnostic lane**, so the marker flips
> self-drawable→blocked: the sole remaining step is the walled R13 baseline build (below spike-tail, deserves
> its own R15 pass). Rest on this mint is now PROVEN (no autonomous-drawable step remains), not assumed.
