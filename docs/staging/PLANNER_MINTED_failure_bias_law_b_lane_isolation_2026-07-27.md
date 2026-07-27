<!-- SUPERVISOR_DRAW: self-drawable -->
# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — LAW B: lane isolation — gates are per-cluster, never global (2026-07-27)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from `docs/staging/in_progress/DIRECTOR_RULING_FAILURE_BIAS_LAWS_2026-07-27.md`, which names LAW B but leaves it un-drawn.

**Serves:**
- **DIRECTOR_RULING_FAILURE_BIAS_LAWS LAW B** — "A block in one lane may never suppress drawing or minting in another. Gates are per-cluster, never global. A director-held population decision must leave site, price-engine, billing and discovery lanes fully drawable."
- **RULE-0 / THREE_LANES** — an empty feasible set is a defect in the dials; one held decision (population λ vs N) must not zero the site, merit-order, premise-demand and DD-cashflow lanes. This is the class fix for exactly that failure ([[project_eighth_class_pending_batch_deadlock_2026_07_27]]): the pending-batch gate blocked minting **globally** when the pending batch was all-blocked.

**Robustness gained (one sentence):** a block (director-held or otherwise) in any single lane leaves every other lane fully drawable, because every draw/mint gate is scoped to its own cluster and no gate can ever evaluate over the global set.

---

## Scope — BUILD (harness lane; director-ruled, drawable now)

1. **Find the global gates.** In `background/supervisor.py`: the pending-batch gate (`_self_refill_draw` / `_maturity_map_draw`), any throttle that reads the whole authorized set to decide whether to draw/mint at all. The ruling's failure #2 is the canonical instance (all-blocked pending batch → global mint block).
2. **Re-scope to per-cluster.** A gate evaluates only over its lane/cluster (site / price-engine / billing / discovery / harness). An all-blocked cluster forbids only *its own* draw; sibling clusters stay in the feasible set. Lane/cluster taxonomy already exists in the draw code — key the gate on it, don't invent a new one (SIMPLICITY GUARD).
3. **R15 both ways (binding — R15):** artificially hold ONE lane (e.g. mark the population cluster all-blocked) and prove EVERY other lane (site, price-engine, billing, discovery) still draws AND still mints. Mutation: revert to a global gate and prove the test REDS (the held lane wrongly zeros the siblings). Add the fixture-isolation for any new register path ([[feedback_new_draw_rung_needs_fixture_isolation]]).

## Walls untouched (director-reserved)
- One-way doors: none — git-reversible harness change.
- L3 level moves stay `blocked_on: director_level_up`.
- Does NOT touch which population decision is held (that stays director-reserved, R13) — only that the hold cannot leak across lanes.

## Window
Director-ruled mechanism; no propose window. Drawable now. Disjoint file_scope from LAW A and LAW C (though all three touch `supervisor.py`/deadman/note — coordinate via tree_lock, or sequence if scopes overlap in the same function).

— Planner mint, RUNG-7 refill, 2026-07-27.
