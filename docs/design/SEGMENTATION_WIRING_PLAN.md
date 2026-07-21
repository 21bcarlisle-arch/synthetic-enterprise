# Segmentation wiring plan — the trait axis (D-SEGMENT), propose-then-proceed

**Status:** PROPOSAL (director tag: contract-touching → propose and proceed; only genuine gate-opens as [ACT]). Serves DIRECTOR_STEER_LEGIBILITY_AND_SEGMENTATION_2026-07-20 Part 2. Author: main session, 2026-07-21.

## The gap in one line
Today the population carries its factors **one axis at a time** (engagement archetype, payment channel, tenure in `household_segments.py`; income_stress/EPC/EV/solar in `household.py`; hidden traits in `nudge_physics.py`; the W2 hidden-state atoms). The mission needs **cohorts as data-derived combinations/clusters across the axes** — "you cannot show a cohort the model does not have" (Part 1 is blocked on this). The value lives in the *permutations*, and the valuable/dangerous cells are rare combinations, so the score is the **worst cell, not the average**.

## What this plan is NOT (scope walls)
- **Traits only, not states.** Timing/events/salience (the state layer) is a separate later track — this sets the *distribution the states move within*. Do not conflate.
- **No generator change without DISCOVER→FRAME first.** The population model is upstream of nearly everything; a silent archetype-ground-truth change mid-campaign is forbidden (R13 baseline discipline). This plan sequences the generator change *behind* a landed DISCOVER + FRAME.
- **Not Atom A.** `A_scope_of_need_scoring_frame` is the *scoring frame*; this is the *population model having the structure the frame scores*. They couple; they are distinct atoms.

## The three factor families (the axes the combinations span)
Grounded in what already exists, so we cluster real structure rather than invent a parallel taxonomy:
1. **Need** — house physics + occupancy: EPC/thermal (`household.py`), heating type, occupancy pattern, premise demand shape (W1_5), adoption assets (EV/heat-pump, W1_10).
2. **Attitudes & values** — bill-shock aversion, trust/reassurance need, framing/tone susceptibility (`nudge_physics.py`), willingness-to-pay trait (W2_7), CO₂/mission salience (new, thin today).
3. **Engagement capacity & behaviour** — engagement level + payment channel + tenure (`household_segments.py`), budget margin/hardship (W2_4), self-rationing propensity (W2_8), adoption journey (C4).

## Sequenced plan (DISCOVER → FRAME → BUILD), each step its own gate

### Step 1 — DISCOVER (doc-only, safe, proceeding now)
- Inventory every trait axis already generated across `simulation/` + the W2 atoms; map which are **independent draws** vs **already-correlated** (e.g. W2_7 ability couples byte-identical to W2_4 budget — a real joint structure already present).
- Find **external, disjoint anchors** for joint structure — published GB segmentation with cross-tab evidence (e.g. Nesta consumption-pattern clusters already cited in C4; DESNZ/BEIS household typologies; Ofgem vulnerability cross-tabs). GENERATOR anchors and VALIDATOR anchors must come from **different** sources (anti-marking-own-homework).
- Output: `docs/market_research/segmentation_joint_structure.md` — what joint structure is evidenced vs what would be asserted.

### Step 2 — FRAME (doc-only)
- Define the cohort model as a **clustering over the existing per-premise trait vector**, not a new hand-cut taxonomy: each generated household already has a trait vector; cohorts are clusters/combinations in that space, estimated (k-means / latent-class shape TBD in FRAME) from the generated population and **validated against the disjoint external cross-tabs**, never against SIM ground truth.
- Specify the **worst-cell metric**: cohort value/risk scored per cell, the reported score = the worst populated cell (couples to Atom A's scoring frame).
- Declare every **asserted** (un-estimable) combination as an R10 simplification with provenance — e.g. a joint incidence with no external cross-tab becomes a named director-curriculum assumption (R13), not a silent parameter.
- Register the coupled-triad: the company **discovers** cohorts from observables (never reads the SIM trait vector); the gap = discovered-cohort structure vs true joint structure.

### Step 3 — BUILD (gated behind a landed FRAME; additive, zero-blast-radius)
- Add a **cohort-assignment layer** that reads the existing trait vector and emits a cohort label + the joint-structure metadata — as a *pure additive* forward extension (identity when the clustering is trivial, so the existing archetype ground truth is byte-identical and no calm-year/regression gate re-opens — same discipline used for W1_5's `premise_demand_shape`).
- Company-side discovery consumer + harness gap (coupled-triad), worst-cell scored, R15 controls mutation-proven.
- Surfaces the cohort into the site so Part 1 can show "what this is like for an individual customer" as a member of a real combination cohort.

## Genuine gate-opens ([ACT] — the only things needing the director)
1. **Values call:** if the DISCOVER pass finds no external cross-tab for a load-bearing combination, its joint incidence becomes a **director-curriculum assumption** (R13) — director-set, not agent-tuned. Batched, not blocking.
2. **Level ratifications** for the new atom(s) — proposed, never self-moved (R16).
Everything else proceeds (correct-after; contract-touching but reversible).

## Why this shape (fit to the whole)
- Clusters the **real** trait structure the sim already generates → no second taxonomy, no drift from archetype ground truth.
- Independence + worst-cell + disjoint anchors are the same fidelity discipline as the weather cascade; the company still discovers through the wall and is allowed to be wrong.
- Additive build → the generator change is provably ground-truth-preserving, satisfying "do not silently alter existing archetype ground truth mid-campaign."
