<!-- SUPERVISOR_DRAW: self-drawable -->
<!-- FRAME (doc-only, drawable now). Item 1 of PLANNER_MINTED_stratified_run_rotation_mechanism_2026-07-25.md.
     Items 2-3 (wire the mechanism into manifest emission + coverage-of-worlds R15 test) are code, held
     behind the propose-then-proceed window (to 2026-07-28). Seed axis dormant behind SE_DRAW_POPULATION
     until the director-reserved release rung. -->

# FRAME — Stratified run-rotation grid (world-scenario × population-seed)

**Serves:** `DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25` §2 (and its authoritative twin
§2); closes the loop for §3/§4 (the run manifest/ledger and three separated scores need *guaranteed,
comparable* coverage of the ratified worlds to compute probability-weighted EV and worst-case survival).
Registered as **not built** in `docs/design/RUN_LEDGER_AND_SCORES_BUILD_2026-07-25.md` §"REGISTERED" item 2.

**Status:** FRAME (doc-only). Mechanism BUILD held (window to 2026-07-28). Values (scenario mix,
true-probability tags) are **R13 director-reserved** — this frames the *mechanism* that carries them, never
authors one. Any level claim stays `blocked_on: director_level_up`.

**The one-line principle (director §2):** *"Randomness lives inside the cell, never in which cell is run."*

---

## 1. What exists today (evidence-cited)

- **`background/run_manifest.py`** already carries the per-run identity a rotation would fill:
  `RunManifest.world_scenario` (required), `true_probability` (Optional — the director-reserved true-measure
  weight, §3/§2), `population_seed` (Optional), `draw_population_enabled` (was `SE_DRAW_POPULATION` on).
  `build_manifest(...)` stamps a `run_id = run-{sha8}-{world_scenario}-{seed_tag}-{gen}`.
- **Three separated scores** (`robustness`, `commercial_ev`, `survival`) + the mixed-basis guard
  (`assert_homogeneous_basis` / `MixedBasisError`) are BUILT and R15-guarded: `commercial_ev` **correctly
  REFUSES** an aggregate when rows lack a `true_probability` tag (proven on 100 legacy `run_history.json`
  rows).
- **The ratified scenario spine** exists (`sim/scenario/` — bimodal / gas-scenario generators, fidelity
  check; [[project_scenario_spine_frame]]).
- **The gap:** *nothing governs which cell is filled.* The manifest fields are optional and hand-set; there
  is no deterministic selector, no committed cursor, no coverage guarantee. Random or ad-hoc single-world
  cadence leaves the tail under-sampled and the §4 verdicts un-computable — the ledger rows emit, but nothing
  decides what fills them.

## 2. The grid (the two axes and the cell enumeration)

- **Axis A — world scenario** (LIVE, already ratified): the ruling names four ratified worlds —
  `history-default`, `NESO-central`, `crisis-replay`, `glut`. Enumerated from the ratified spine, **not
  authored here**; each cell carries the director-reserved `true_probability` tag as data.
- **Axis B — population seed** (DORMANT until activation): a small enumerated set of seeds feeding the C-S2
  **named RNG substream** discipline (which households drawn, which weather path), so a seed change never
  shifts another subsystem's draws. Meaningful only once `SE_DRAW_POPULATION` is live.
- **Cell** = (world_scenario, population_seed). Randomness (household draw, weather path) is confined *inside*
  the chosen cell via the named substream; it never chooses the cell.

## 3. The deterministic next-cell selector (IaC-committed cursor)

- A **stratified sweep** with a **committed cursor in the readable tree** (per OPERATIONAL_LAYER IaC: no
  rotation state outside the repo; reconstruct-from-repo-alone). The cursor advances one cell per run in a
  fixed round-robin over the grid, so coverage of every ratified world is *guaranteed within one grid period*
  rather than hoped for, and runs stay comparable.
- **Deterministic, replayable** (C-S2): given the cursor state committed in the tree, the next cell is a pure
  function — no `Date.now()`/`random()` in the *choice*. Re-running from a cursor reproduces the same cell
  order.
- **Emission wiring (item 2, BUILD):** the selector feeds `build_manifest(world_scenario=…,
  true_probability=…, population_seed=…)` from the cursor, so each ledger row carries its world + true-prob
  tag from the rotation rather than a hand-set constant — feeding forward exactly the tag the §4
  `commercial_ev` guard already requires (legacy rows correctly refuse for lack of it).

## 4. Honest partial coverage until activation (stated, not hidden)

The **population-seed axis is designed now, wired-but-dormant behind `SE_DRAW_POPULATION`, and goes live with
activation** — no separate door. Until the director-reserved release rung flips (held pending the coverage
report + the escalated N/λ R13 reconciliation — [[project_population_activation_infra]]), the sweep rotates
the **scenario axis only** (already ratified and live) and the seed axis is a **no-op single cell**. This is
logged as honest partial coverage, never a silent gap.

## 5. The coverage-of-worlds check (item 3, R15 — defined now, built with the mechanism)

A test asserting: (a) the sweep **visits every ratified world within one grid period**; (b) an **unweighted
EV aggregate over a mixed-basis set still fails loudly** (re-uses the existing §4 `assert_homogeneous_basis`
guard). The R15 mutations it must survive:
1. **Skipped-cell mutation:** a selector that silently drops the `crisis-replay` (tail) cell must go **RED** —
   coverage is checked against the enumerated grid, not against whatever the cursor happened to visit
   (independence: a FAIL-OPEN selector that never emits the tail is exactly the defect §4 exists to prevent).
2. **Untagged-EV mutation:** a rotation that emits a row without its `true_probability` must keep the
   `commercial_ev` aggregate **REFUSING** (not silently averaging) — the guard already does this; the test
   pins that the rotation cannot bypass it.

## 6. Walls untouched (director-reserved)
- **Scenario values + true-probability tags** — R13; this wires the mechanism that carries them, never
  authors a scenario or a probability.
- **`SE_DRAW_POPULATION` activation flip + downstream re-baseline** — held director-reserved release rung; the
  seed axis waits on it.
- **§6 survival-usefulness metrics** — registered-only, director-session gated.
- **One-way doors** — none; mechanism + tests are git-reversible, behind the epistemic wall.
- **L3 level moves** — stay `blocked_on: director_level_up`.

— FRAME, drawn from `PLANNER_MINTED_stratified_run_rotation_mechanism_2026-07-25.md` scope item 1, 2026-07-25.
