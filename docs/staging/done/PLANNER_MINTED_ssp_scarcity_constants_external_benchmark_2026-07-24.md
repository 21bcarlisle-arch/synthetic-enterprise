# [PLANNER-MINTED] Ground the SSP scarcity constants (A0/A1/A2) against a PUBLISHED UK benchmark — the ledger's own named S3 gap (2026-07-24)

**Type:** RUNG-7 planner mint (WORK_IS_THE_DEFAULT 2026-07-23, rung 7; rungs 1–6 empty this tick). **Propose-then-proceed. DISCOVER-lane (doc-only).**

## What ratified goal / ledger row this serves
- **Fidelity-ledger row:** `W1_6_physics_price_signal::ssp_residual_demand_scarcity_calibration_2026_07_19` (`docs/observability/fidelity_evidence_ledger.json`).
- **The row names this gap in its own `independent_anchor` field:** *"no third-party published benchmark was used to cross-check the fitted A0/A1/A2 constants themselves in this pass — a named gap (docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md S3), not concealed."* The fidelity doc (line ~182) repeats it: the constants are fit entirely against the no-carbon floor and *"would be grounded by"* an external anchor.
- **Axis served:** Axis 3 **Believability** (`DIRECTOR_AXES.md`) — *"wholesale products and prices … does it feel like the real UK market to a 20-year veteran."*

## Why this is DISTINCT from the in-flight `ssp_negative_lift_cells` mint
That mint (in `docs/staging/in_progress/`) attacks the calm-year **negative-lift** cells via a drift-aware **recalibration** of the *same* structure — an internal fit-quality question. **This mint is the orthogonal external-validity question:** are the *fitted constant magnitudes* consistent with a **published** UK marginal-cost / scarcity-pricing benchmark (gas-plant SRMC ranges, scarcity-adder / VOLL-style literature, Ofgem/Elexon/academic merit-order studies)? A model can lower its own MAE and still have physically wrong constants. Different question, different lane, no overlap.

## Real-world fidelity gained
Turns the scarcity constants from *"OLS-fit, internally motivated"* into *"cross-checked against what the real GB merit order actually prices"* — the exact 20-year-veteran smell test. A confirmed or refuted external anchor is a fidelity gain either way (an honest refutation is a finding, not a failure).

## Scope (propose-then-proceed, DISCOVER only)
1. **PROBE network first** (per the no-network-in-autonomous-runs lesson): trial-fetch before declaring drained. Sources to seek: published GB gas-plant SRMC / heat-rate ranges, scarcity-pricing / loss-of-load-adder literature, Elexon/NESO/Ofgem merit-order commentary.
2. Record findings to `docs/market_research/` (structured, cited, provenance-tagged) — dispatch to the **discovery-agent** (read-only research role).
3. Update `docs/fidelity/EPOCH2_PRICE_ENGINE_FIDELITY_EVIDENCE.md` S3: either an external anchor row for A0/A1/A2, or a recorded "no comparable published benchmark found — gap stands, bounded by X."

## Walls this mint does NOT cross
- **R13 (baseline/curriculum split) is honoured:** this is a **fidelity-to-reality** check decided **blind to company P&L**. It may motivate a constants change *only* for reality-consistency — **never** tune the constants toward company results, and **never** toward a benchmark to hit a number (R12 anti-goal-seek). This mint only *gathers and records* the external anchor; any recalibration is the separate `ssp_negative_lift_cells` mint, R4/R13-governed.
- No generator ground-truth edit here (director-reserved); DISCOVER produces evidence, not a curriculum change.

## Propose-then-proceed window
Standard planner window; DISCOVER is fully reversible (doc-only). Register a finding/atom rather than editing the price engine on sight (SELF_INTERRUPT_DISCIPLINE: queue, don't fix-on-sight).


---

## DISPOSITION — DISCOVER DONE (2026-07-24 worker tick)

Dispatched to the read-only discovery-agent. Network was available; general web search engines were bot-blocked, but direct gov.uk URL-walking + gov.uk's `/api/search.json` yielded **two genuine anchors** (both `observed-with-evidence`, cited):
1. **DECC Capacity Market (2015):** DDM price ceiling **£6,000/MWh** — the fitted multiplier's max output (~£574/MWh) sits ~1 order of magnitude below both this ceiling and the real SSP max (£4,038/MWh), externally GROUNDING (not newly finding) the already-honest tail-underproduction gap.
2. **Statutory Security of Supply Report (2025):** GB Reliability Standard **LOLE ≤ 3 hrs/yr** (~0.034% of periods) — the code's scarcity kicker firing on ~30–40% of periods reads as a general tight-margin markup, not a literal loss-of-load mechanism (interpretation note, `inferred`).

**No source using the identical functional form was found → A0/A1/A2 as literal magnitudes remain UNBENCHMARKED; the S3 gap STANDS, now bounded** by the two anchors. R12/R13 held throughout: gather-only, NO constant changed, NO recalibration performed or recommended, decided blind to company P&L. Recorded to `docs/market_research/ssp_scarcity_constants_external_benchmark_2026-07-24.md` (+ ASSUMPTIONS.md rows) and folded into the fidelity doc as simplification item 5. An honest bounded-partial is a fidelity gain, not a failure. Any recalibration is the separate `ssp_negative_lift_cells` mint (R4/R12/R13-governed). Archived to done/.
