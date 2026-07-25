<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- PARKED 2026-07-25: AUTHORITATIVE reworded twin ("confirmed this morning") of
     DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25.md — SAME ruling, same six
     sections/substance. Additive infra BUILT for both (see docs/design/RUN_LEDGER_AND_SCORES_BUILD_2026-07-25.md).
     Two nuances unique to THIS version, both honoured: §6 "capture liquidity-minimum and cover-minimum
     per run from the start" -> RunOutcomes.liquidity_headroom_min_gbp / collateral_cover_min added (fields
     only; §6 metrics stay unbuilt); §5 "report non-domestic as part of the coverage report" -> fold the
     15 resi/4 SME/5 I&C audit into the coverage-report output at activation. OPEN blocking sub-item = the
     ACTIVATION CORE §1 (same as the twin). PROGRESS 2026-07-25: real SYN region draw LANDED (opt-in
     draw_region, drawn from the ratified curriculum region_marginal; live_population activated branch
     carries real regions; byte-identical default preserved) — region axis realises all 10 cells at
     N≈200, the R10 placeholder blocker is CLOSED. Gate still False on ONE tail cell
     (heating_fuel:lpg_bottled thin at N=200) — N/tail question, not region. REMAINING: N/λ
     reconciliation (ruling's N=200 vs director-signed λ=1.0 TRICKLE = R13, ESCALATED to director);
     tail-floor design call; ~19-entrypoint SYN hardening; flag-flip + re-baseline = held director-
     reserved release rung. §2 mechanism-only (values R13). §6 registered-only, director-session gated. -->

# [DIRECTOR-RULING] — Generator population ACTIVATED (R13); run rotation, run ledger, and the three separated scores (2026-07-25)

**Type:** [DIRECTOR-RULING] via advisor bridge. Answers the director-reserved wall on `SE_DRAW_POPULATION` and rules the run-management questions it raises. Confirmed by the director this morning.

## 1. R13 RULING — activate the drawn population

The live seam's **fixed CUSTOMERS literal is retired**. The generator draw is **ACTIVATED** with:

- **N = 200** — the nested worst-cell coverage completeness knee. Large enough that rates and distributions carry meaning; small enough to run fast.
- **Per-run variation ON** — a different draw each run, with the realised archetype mix **hidden from the company** (canon; the precondition for the epoch-4 tournament). The company discovers its book through onboarding and observables only.
- **Coverage report before any derived figure is published.** The first activated run emits realised cell counts against the curriculum target — which cells filled, which stayed thin — and **no site figure derived from the new population may be published until that report exists and is read.** Thin cells are a finding, not a defect to paper over.

**Expected and accepted:** every downstream number re-baselines — fidelity cells, financials, site panels, comparisons. That is the price of the numbers becoming real, and it is cheaper now than later. Re-baselining is not a regression; silently keeping old numbers beside new ones would be.

**Unchanged walls:** curriculum values, archetype definitions and the engagement mix remain director-reserved R13. This ruling activates the draw at the ratified values; it does not license tuning them.

## 2. Run rotation — stratified, never random

Runs rotate a **stratified grid over world-scenario × population-seed**, not a random pick. Coverage of the ratified worlds (history-default, NESO-central, crisis-replay, glut) is guaranteed and runs stay comparable. **Randomness lives inside the cell** — which households are drawn, which weather path — never in which cell is run. This extends the ratified scenario-spine rotation to the population axis; the two rotate together.

## 3. The RUN LEDGER — every run recorded as a row

Every run emits a manifest row: `run_id` · code SHA · curriculum version · world scenario **with its true-probability tag** · population seed · realised cell counts · outcome (survived / died + cause + date) · EV · £/tCO₂e · worst-cell fidelity. Without this ledger the ratified verdicts cannot be computed at all — probability-weighted EV and worst-case survival are both cross-run quantities — and improvement cannot be distinguished from luck.

**Artifact retention:** full artifacts for **every death** (rare and information-dense), a sample of survivors, and any run a fidelity trigger flags. Everything else keeps its ledger row. Storage discipline is yours to design; the row is mandatory.

## 4. Three scores, computed from the same runs, never conflated

- **Robustness** — unweighted, tail-focused: does the machinery cope with what it is shown? (development signal)
- **Commercial EV** — probability-weighted against the true measure: what is this company worth?
- **Survival** — worst-case, unweighted: does it die anywhere in the sampled set? (hard constraint)

The importance-sampling discipline already ratified applies unchanged: two weightings, never conflated; every run carries its true-probability tag; **an unweighted EV aggregate must fail loudly** (existing R15). Tail-heavy sampling does not raise the commercial bar — it lowers the cost of learning about the tail — *provided* reweighting is enforced. Report the three scores separately wherever performance is stated.

## 5. Market scope

Survival is judged on the **domestic book**: the mission is domestic personalisation-abatement and the 2021–22 failure evidence is domestic. If SME/I&C volume exists in the book, its P&L is **reported separately** and may never silently carry or sink the domestic story. Market-segmented survival criteria are an epoch-2 question, not this ruling. Report what is actually in the book today as part of the coverage report.

## 6. Registered, not ruled — "how do we make survival useful"

Binary survival is a weak signal (most runs live; deaths are noisy tail draws). Registered for its own design session, do not build ahead of it: **margin of survival** (minimum liquidity headroom and collateral cover reached, recorded from every run including survivors), **breaking strain** (dial world severity until death; record the dose — "survives 2021–22 replay at 1.0×, dies at 1.4×"), and **cause attribution** on every death and near-death. Survival remains a hard constraint; ranking would come from breaking strain and headroom. Ledger fields above are designed to make this computable later — capture liquidity-minimum and cover-minimum per run from the start.

**Risk & proportionality:** activation touches the population seam (reversible half already shipped) and re-baselines downstream figures — expected, gated on the coverage report before publication. Ledger and rotation are additive. Tag: **proceed; coverage report before any published figure; curriculum values remain reserved.**

— Advisor bridge, carrying the director's ruling, 2026-07-25.
