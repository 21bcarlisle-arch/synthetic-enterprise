# Epoch-2 "Coupled World, ranked by value" — campaign decomposition

**Source:** `docs/staging/DIRECTOR_CAMPAIGN_EPOCH2_COUPLED_WORLD_2026-07-19.md` (director via advisor, 2026-07-19).
**Constraint:** DISCOVER/FRAME only — **W1 BUILD stays CLOSED** until the director opens it; site lane continues in parallel. Proceed-by-default; only genuine gate-opens (W1 BUILD, schema, epoch ceilings) are [ACT]s.

## The 5 requirements → decomposed atoms (homed, staged, sequenced by physical dependency)

The campaign is explicitly multi-atom; do NOT mega-effort. Homing + loop_stage below; the draw sequences. Scoring frame is **first** (defines success); cost/price discovery is **load-bearing** and can run parallel to the frame; correlations depend on the cascade structure; billing-delays sit downstream of usage; value/exposure ranking is the arbiter that ties it together.

| # | Atom (candidate, provenance: proposal) | Req | Lane / home | Stage | Depends on |
|---|---|---|---|---|---|
| A | **Scope-of-need SCORING FRAME** — archetype × regime grid spanning the *range of need* (affordability/collections, unusual consumption shape, export/self-gen, pass-through commercial, crisis-vs-calm); fidelity = **worst-explained cell**, not population average | 1 | G_data_learning (scoring) | FRAME first | — (defines success) |
| B | **GB wholesale price FORMATION discovery** — how the national wholesale print actually forms (global energy + weather → industrial/residential demand + interconnection); price as OUTPUT | 3 | W3_industry_systems / W1 | DISCOVER | — |
| C | **Supplier COST behaviour discovery** — a supplier's *actual* cost = weighted avg of prior purchases, NOT the spot print; where a price move bites vs doesn't; **test the hypothesis**: for a hedged supplier the dominant weather coupling runs through *volume* (consumption deviating from hedged qty, incremental transacted when most expensive) not the price of already-bought energy | 3 | E_finance_treasury / B_commercial | DISCOVER | B (partial) |
| D | **Cascade correlation ESTIMATION method** — nature AND strength of each cascade link from real data, defensible stats; **joint-tail > marginal**; asserted-not-estimated registered as simplifications | 4 | G_data_learning | DISCOVER | B, C, W1_COUPLED_WEATHER_CASCADE (already framed) |
| E | **Billing physics with real event delays** — estimated + late reads, settlement true-ups, meter→cash lag; downstream of usage | — | D_billing_metering | DISCOVER→FRAME | usage chain |
| F | **VALUE / exposure ranking** — rank measured belief-vs-truth gaps by value-at-risk, not gap size; the value cycle IS Epoch 2 (deliberately circular — needs enough value model to rank its own fidelity investments) | 2 | A_strategy_governance / B_commercial | FRAME | A (frame), the gap ledger |
| — | **Site observability** — standing parallel lane; no stage is "done" the site can't show honestly | parallel | site/** (L2 SITE) | continuous | each atom's output |

Builds on already-landed DISCOVER: `W1_COUPLED_WEATHER_CASCADE_DISCOVER.md` (weather→demand→gen→residual→price→imbalance→capital cascade + compounding tail + gap_cascade metric) and `W1_3_NATIONAL_WEATHER_JOINT_REGIME_DISCOVER.md` (joint cold-and-still tail). Atom D extends the cascade correlations from these.

## Sequencing proposal (physical dependency, not calendar)
1. **A (scoring frame) — FIRST**, in parallel with **B/C (cost/price discovery)** — both start now, independent.
2. **D (correlations)** after B/C + the weather-cascade DISCOVER give it structure.
3. **E (billing delays)** downstream of the usage chain.
4. **F (value ranking)** once the frame (A) + enough gap measurements exist to weight by exposure.
Exact stage-by-stage is the draw's to sequence; this is a diagnostic, not a target (LAW A).

## Wall / method (all atoms)
Randomness + generating structure live in the SIM (req 5); the company infers from observables; the measured belief-vs-truth gap IS the deliverable. Correlations estimated with defensible stats, joint-tail emphasis (req 4). Baseline physics vs director curriculum split (R13). Register every asserted-not-estimated relationship as a simplification (R10).

## Progress (2026-07-19)
- **Atom A — scope-of-need scoring frame: LANDED** (`EPOCH2_A_SCOPE_OF_NEED_SCORING_FRAME_DISCOVER.md`, 2c3d7c03f). 5×3 grid, worst-cell MAX-gap scoring, R15-failable. Director values-calls flagged (harm-weighted vs equal-cell; grid-completeness).
- **Atoms B/C — price formation + supplier cost: LANDED** (`EPOCH2_BC_PRICE_FORMATION_AND_SUPPLIER_COST_DISCOVER.md`, fe140d6b6). Price-as-output; cost=hedge-weighted-avg; the volume-vs-price HYPOTHESIS = SUPPORTED for a hedged book (joint-tail interaction, flips naked). Flagged a real in-repo gap: hedging.py collapses a laddered book into one term-start price.
- **Atom D — cascade correlation estimation methodology: DISCOVER in flight.**
- E (billing delays), F (value/exposure ranking): sequenced next.
- Upstream blocker surfaced by B/C: the price engine's SSP ~10× miscalibration (residual-demand form uncalibrated, carbon/UK-ETS term missing) — a hard dependency for any cascade-magnitude BUILD.

## Core DISCOVER phase COMPLETE (2026-07-19) + fidelity-evidence addendum
- **A-F ALL LANDED:** A scoring-frame (2c3d7c03f), B/C price-cost (fe140d6b6), D correlations (6a47b1172), E billing-delays (e6acd25fa), F value-ranking (0d5e6f875). Every atom doc-only, wall intact, W1 BUILD closed, director values-calls flagged not invented.
- **ADDENDUM — fidelity evidence** (`docs/staging/in_progress/DIRECTOR_ADDENDUM_FIDELITY_EVIDENCE_2026-07-19.md`): the campaign must EMIT inspectable fidelity evidence (4-layer chain evidence→world→belief/action→constraint) scored as a GRID of 3 measures (lift over a FROZEN un-gameable naive baseline; worst-cell coverage; ablation value under common-random-numbers) — none averages; emit-as-you-build (DoD, never retrofit); site as the director's fidelity instrument. New atoms:
  - **G — fidelity-evidence machinery** (3-measure grid + emit-ledger + inspection-chain data model + frozen-baseline/Goodhart): DISCOVER/FRAME **in flight**.
  - **H — emit-DoD doctrine**: recording (fitted relationship+strength+provenance, per-cell contribution, binding constraint, ablation) travels with every physics atom's definition-of-done. FRAME + rule.
  - **SITE-FID — the fidelity instrument** (renders the 4-layer chain; drill relationship→evidence; Expert-Hour answerable): SITE lane, after G's data model.
- **Emit requirement is retroactive-on-BUILD**, not on the DISCOVER docs: it binds each atom's future BUILD DoD (W1 BUILD still closed).

## DISCOVER/FRAME phase COMPLETE — awaiting director BUILD-open (2026-07-19)
- **Atom G — fidelity-evidence machinery: LANDED** (56da6f8da). 3 measures un-gameable (hash-pinned frozen baseline; map-of-ignorance; CRN ablation), emit-DoD as a phase-close gate into a SIBLING evidence ledger, inspection-chain data model with in-schema wall discipline, atom split G1(grid-scorer)/G2(emit-ledger+gate)/G3(inspection-chain data)/G4(site instrument).
- **The campaign's DISCOVER/FRAME design phase is COMPLETE: A,B/C,D,E,F,G all landed.** The full design spine exists (objective function, physics, estimation method, delay chain, value-ranking, fidelity-evidence machinery).
- **AWAITS THE DIRECTOR (not agent-decidable):** (1) W1 BUILD-open (all the above is DISCOVER/FRAME; nothing built); (2) the VALUES-CALLS surfaced across the docs — harm-weights in atom F's kappa + tau threshold, atom G's commercial_weight per cell, atom A's equal-cell-vs-harm-weighted worst-cell + grid-completeness, atom E's metric-normalisation, L_min gate floors (cat-6 one-way doors, R13 curriculum). (3) Upstream BUILD blocker: the price engine's ~10x SSP miscalibration + missing carbon/UK-ETS term + hedging.py single-price collapse — gates cascade MAGNITUDE (not direction) for any physics BUILD.
- Site lane (G4 + the existing doors) continues as the standing parallel window.

## BUILD phase underway (2026-07-19, gate-after + director "resume the campaign BUILD")
- **TASK 1 — SSP price-engine recal LANDED** (a2dd6dcac): the ~10× fix that unblocks cascade MAGNITUDE.
- **G machinery (the fidelity-evidence measurement infrastructure) being built on the IMPROVED constructs**
  (`EPOCH2_G_CONSTRUCT_CHALLENGE_RESPONSE.md` — best-of-naive-family / CVaR-generalizing-MAX / screen-then-ablate):
  - **G1 grid-scorer LANDED** (991b02007): `background/fidelity_grid_scorer.py`, 24 R15 tests, epistemic PASS, L1 PROPOSED.
  - **G2 emit-ledger + emit-DoD gate LANDED** (84efccdd7): `background/fidelity_evidence_ledger.py`, sibling ledger
    (no consumers wired — avoids the shared-surface wedge) + 3-red-condition R15 gate, fail-closed, 22 tests, L1 PROPOSED.
  - **G3 inspection-chain data model — IN FLIGHT** (4 record types + bidirectional link graph + in-schema wall discipline).
  - G4 (site fidelity instrument, SITE lane) sequenced after G3.
- All L1 PROPOSED (batched, cells not moved — director's per §0). Values-calls running on the asserted defaults
  (`EPOCH2_VALUES_CALLS_BATCH_1.md`). NEXT after G machinery: wire an emitter (a physics atom emits into G2's ledger),
  then D (cascade estimation) + A (scoring frame) BUILD. Campaign BUILD is by explicit dispatch until a director
  `FRONT_OPEN` makes it self-drawing (see `LOOP_CONTINUITY_FAILURE_DIAGNOSIS.md` RC1).
