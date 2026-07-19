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
