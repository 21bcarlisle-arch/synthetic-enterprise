<!-- DISPOSITION-BUILT 2026-07-29 (self-drawable BUILD executed): scope items 2+3 LANDED.
     Mechanism = background/run_rotation.py — IaC-committed grid (docs/design/run_rotation_grid.json,
     four ruling §2 worlds transcribed, all true_probability null=R13 director-reserved) + committed
     cursor (docs/observability/run_rotation_cursor.json) + deterministic pure next-cell selector
     (peek/select, C-S2 replay) + the rotation->manifest emission seam (manifest_for_next_run feeds
     build_manifest world+true_prob from the cursor). Coverage R15 test tests/background/test_run_rotation.py
     (13 pass; sibling run_manifest 16 pass): both R15 mutations proven both-ways — skipped-cell coverage
     assert fires RED when neutered to pass (checked against the enumerated grid oracle, not the visited
     set); untagged-EV keeps commercial_ev REFUSING a null-prob rotation row. Seed axis DORMANT behind
     SE_DRAW_POPULATION (single no-op cell until draw_population_enabled; wired-but-dormant). NO run
     entrypoint wired, NO flag flipped, NO scenario/probability authored — activation + level moves stay
     director-reserved (blocked_on: director_level_up, R16). Archived to done/. -->
<!-- SUPERVISOR_DRAW: consumed (BUILD executed 2026-07-29; no drawable-now work remains — activation is director-reserved) -->
<!-- RELEASED 2026-07-29T02:07Z (RUNG-7 planner tick): propose-then-proceed window (open until 2026-07-28, 72h from mint) has ELAPSED with NO director revision (git log shows only the 07-28 mechanical block-hygiene backfill 65ad9d83c). Per the doc the scenario-axis MECHANISM build is now buildable (deterministic next-cell selector + committed cursor, wire scenario-axis rotation into manifest emission, coverage-of-worlds R15 test). Flipped blocked->self-drawable so the build-draw surfaces it (no-orphan-transition, R11). WALLED and untouched: SE_DRAW_POPULATION seed-axis activation (director release rung -- seed axis stays a dormant no-op single cell), scenario values + true-probability tags (R13), level moves (director_level_up, R16). Only the mechanism draws; the gate is the backstop. -->
<!-- DISPOSITION 2026-07-25: FRAME landed (scope item 1) →
     docs/design/frame/stratified_run_rotation_FRAME.md (grid axes + cell enumeration + deterministic
     IaC-committed-cursor selector + honest partial-coverage-until-activation + the coverage-of-worlds R15
     test with its mutations; grounded in background/run_manifest.py + the §4 mixed-basis guard). REMAINING
     open sub-items = item 2 (wire the selector into build_manifest emission) + item 3 (build the coverage
     test) = mechanism BUILD, held behind the propose-then-proceed window to 2026-07-28; the population-seed
     axis stays dormant behind the director-reserved SE_DRAW_POPULATION release rung. BLOCKED now (was
     self-drawable): the FRAME is the only drawable-now half and it has landed — the remaining work is
     purely the window-held mechanism BUILD, so there is NO drawable-now work. blocked_on: propose-then-
     proceed BUILD window closes 2026-07-28 (mechanism only; scenario/true-prob values stay R13; seed axis
     stays on the SE_DRAW_POPULATION release rung). The daily planner re-plan re-evaluates it. -->

# [PLANNER-MINTED / PROPOSE-THEN-PROCEED] — Stratified run-rotation mechanism (world scenario × population seed): FRAME + mechanism wiring (2026-07-25)

**Provenance:** RUNG-7 planner refill (director ruling `WORK_IS_THE_DEFAULT_2026-07-23`). Minted from a ratified goal: `DIRECTOR_RULING_POPULATION_ACTIVATION_AND_RUN_LEDGER_2026-07-25.md` §2 (and its authoritative twin §2) rule a **stratified grid over world-scenario × population-seed**. The build doc `RUN_LEDGER_AND_SCORES_BUILD_2026-07-25.md` §"REGISTERED — held / not built" item 2 records this as **not built** — this doc makes the non-walled *mechanism* half drawable (R16: a next-step registered only inside a design-doc body is invisible to the draw).

**Serves:**
- **The generator-activation ruling §2** — "runs rotate a stratified grid … coverage of the ratified worlds (history-default, NESO-central, crisis-replay, glut) is guaranteed rather than hoped for, and runs stay comparable. Randomness lives inside the cell, never in which cell is run."
- **Ruling §3/§4 (already BUILT) — closes the loop they need.** The run manifest/ledger and the three separated scores (Robustness / Commercial EV / Survival) are cross-run quantities: probability-weighted EV and worst-case survival cannot be computed without *guaranteed, comparable coverage* of the ratified worlds. Random cell-choice would leave the tail under-sampled and the verdicts un-computable — the ledger rows already emit, but nothing yet governs which cell fills them.
- **DIRECTOR_AXES axis 3 (Believability) — indirectly**, and the epoch-4 tournament precondition (varied-population-per-run is canon; this sequences the variation deterministically instead of by chance).
- **Extends the ratified scenario-spine rotation** ([[project_scenario_spine_frame]]) onto the population axis — the ruling: "the two rotate together."

**Fidelity gained (one sentence):** run selection moves from an ad-hoc/random single-world cadence to a deterministic stratified sweep that guarantees every ratified world and population-seed cell is visited on a known schedule, so improvement can be told from luck and the tail is sampled on purpose rather than by accident.

---

## Scope — FRAME + mechanism (drawable NOW where decoupled from activation)

The **values** are director-reserved; only the **mechanism** is minted. Drawable-now, doc + mechanism-seam work:

1. **FRAME the grid and the seam.** One page: the axes (world-scenario × population-seed), the cell enumeration, and the deterministic next-cell selector (a stratified sweep with a committed cursor in the repo — IaC: no rotation state outside the readable tree, per OPERATIONAL_LAYER). Randomness is confined *inside* a chosen cell (which households drawn, which weather path via the C-S2 named RNG substream discipline) and never chooses the cell.
2. **Wire the scenario-axis rotation** (already exists as the ratified scenario spine) into the manifest emission so each run's ledger row carries its `world scenario` + `true-probability tag` from the rotation cursor rather than a hand-set constant — the tag the three-scores R15 guard already requires (legacy `run_history.json` rows correctly REFUSE a commercial-EV aggregate for lack of the tag; this feeds the tag forward).
3. **Define the coverage-of-worlds check** (R15): a test that the sweep visits every ratified world within one grid period, and that an unweighted EV aggregate over a mixed-basis set still fails loudly (re-uses the existing §4 guard).

## Population-seed axis — BLOCKED on activation (stated, not hidden)

The **population-seed** half of the grid only becomes meaningful once `SE_DRAW_POPULATION` is activated (the generator draw is live) — that flag flip is the **director-reserved release rung** in the population-activation ruling, held pending the coverage report + the escalated N/λ R13 reconciliation. So:
- The seed-axis enumeration + selector is **designed now** (FRAME), **wired but dormant** behind the same flag, and **goes live with activation** — no separate door.
- Until activation, the sweep rotates the **scenario axis only** (which is already ratified and live); the seed axis is a no-op single cell. This is honest partial coverage, logged, not a silent gap.

## Propose-then-proceed window

- **Open until 2026-07-28 (72h from mint).** The FRAME + the scenario-axis mechanism wiring is the "then propose" artefact and is buildable within the window (mechanism only, no values). The seed-axis activation stays gated on the director release rung regardless of the window.

## Walls untouched (director-reserved)

- **Scenario values + true-probability tags** — R13, director-reserved. This wires the *mechanism* that carries them; it never authors a scenario or a probability.
- **`SE_DRAW_POPULATION` activation flip + downstream re-baseline** — the held director-reserved release rung; the seed axis waits on it.
- **Curriculum values, §6 survival-usefulness metrics** — reserved / director-session gated.
- **One-way doors** — none; mechanism + tests are git-reversible, behind the epistemic wall.
- **L3 level moves** — stay `blocked_on: director_level_up`.

— Planner mint, RUNG-7 refill, 2026-07-25.
