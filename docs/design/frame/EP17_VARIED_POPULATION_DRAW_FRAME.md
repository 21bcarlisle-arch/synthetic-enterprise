# FRAME — EP17_varied_population_draw: the cast is fixed by one argument nobody passes, and "different" is capped at 10% of the book

**Atom:** `EP17_varied_population_draw` (lane `W2_customer_generator`, epoch 4, `level_current: 0`, `loop_stage: idle`,
`provenance: director_ruling`, `block_reason:` director-reserved curriculum sequencing R13).
**Pass:** DISCOVER/FRAME only, worker tick 2026-08-14, LANE 3 idle draw. **No BUILD code written**; `file_scope` is `[]`
and nothing outside this doc + the atom's own store record was touched. EPOCH_GATING_AND_ATOM_AUTHORSHIP rule 1 makes
DISCOVER/FRAME available on a parked atom while BUILD is not.

**Measured at HEAD `420b7449f`.** `docs/design/maturity_map.yaml`, the atom's store file and `docs/design/frame/` were
all clean in the shared tree at draw time, so every number below was read off the desk tree directly — no detached
worktree was needed this tick. Every claim is `observed-with-evidence` unless labelled `inferred` (R9).

---

## 0. The question this pass had to answer first

The atom's own `origin_note` records a duplicate-risk check at mint: *"W2_2_population_draw covers the single-run draw,
not run-to-run variation."* Two knobs that only ever appear as a difference are one knob, so the first job was to test
that separation rather than inherit it.

**It survives, but not in the shape the atom's name implies.** W2_2 built a generator that genuinely varies. What EP17
names — variation *across runs* — is not an unbuilt mechanism either: it is designed, half-built under a different id,
and disconnected at exactly one argument.

---

## 1. FINDING 1 — the generator already produces a different cast; the seam pins it to one

`simulation/population_draw.py` (W2_2, L2, activated 2026-08-13) varies materially with its `base_seed`. Drawing the
live seam at twenty seeds:

| seed | SYN customers drawn |
|---|---|
| `20260724` (the live one) | 2 |
| 0 / 1 / 2 / 3 (the rotation grid's seeds) | 5 / 3 / 2 / 5 |
| 0–19 | min 2, median 4, max 10 |

The mix moves with it, not just the count — at seed 0 the drawn cohort is `{resi 3, I&C 1, SME 1}` /
`{MEDIUM 3, LOW 1, HIGH 1}` / `{DD 3, other 2}`; at seed 3 it is `{resi 4, I&C 1}` / `{MEDIUM 4, LOW 1}` / `{DD 5}`.
So segment mix, consumption skew and payment mix all vary by seed. **The generator is not the gap.**

The gap is the seam. `simulation/live_population.py:123` is `live_population(base_seed: Optional[int] = None)`, and
line 82 sets `_DEFAULT_BASE_SEED = 20260724` with the comment *"a MECHANISM default (determinism), NOT a curriculum
knob."* **Every production call site calls it bare.** Fourteen of them —

```
simulation/run_phase2a.py:67   simulation/run_phase2b.py:174   simulation/run_phase4c_on_phase2b.py:102
tools/run_phase0c.py:31        tools/run_phase1c.py:31         tools/run_phase1c_full_window.py:42
tools/run_phase3a.py:27        tools/generate_dashboard_data.py:75   tools/generate_customer_sample.py:52
tools/generate_hh_data.py:106  tools/band_null_sweep.py:56     (+ the seam's own re-entries)
```

— and not one passes `base_seed`. Verified live: `draw_population_enabled()` is `True`, `live_population()` returns 20
customers, and the drawn pair is `SYN-2021-001`, `SYN-2025-001` — the same two the activation curriculum artefact
records under `base_seed.realised_draw`. Since activation on 2026-08-13, **every run has faced a byte-identical cast.**

EP17's BUILD is therefore not "build a varying draw". It is "let something choose the seed".

## 2. FINDING 2 — the thing that would choose it is built, and has never run

`background/run_rotation.py` is the stratified world×seed rotation from
`docs/design/frame/stratified_run_rotation_FRAME.md` (axis B = population seed). It is real code:
`docs/design/run_rotation_grid.json` enumerates `"population_seeds": [0, 1, 2, 3]`, `enumerate_cells()` crosses them
with the four ratified worlds, `select_next_cell()` advances an IaC cursor, and thirteen tests cover it including two
R15 mutations.

**It has zero non-test callers.** `grep` for `run_rotation|manifest_for_next_run|select_next_cell` outside
`tests/` and the module itself returns one comment reference in `sim/scenario/spine.py:278` and nothing else. The
cursor `docs/observability/run_rotation_cursor.json` reads `{"index": 0}` and has **exactly one commit in its entire
history** — `f52a94133`, the build commit that created it on 2026-07-29. It has never advanced, because nothing has
ever asked it for a cell.

This is the no-caller/never-runs class, and it means EP17's remaining work is smaller and more specific than its
`level_target: 3` suggests: give the rotation a production caller, and route the cell's `population_seed` into
`live_population(base_seed=…)`. The design work is done and is not EP17's to redo.

## 3. FINDING 3 — the axis's dormancy condition expired eight days before this pass, in two live documents

Both the FRAME (§4) and `run_rotation.py`'s own docstring state that the seed axis is dormant *"until the
director-reserved release rung flips"*, that rung being `SE_DRAW_POPULATION`. The FRAME is explicit that there is **no
separate door**: *"the population-seed axis is designed now, wired-but-dormant behind `SE_DRAW_POPULATION`, and goes
live with activation."*

That rung flipped on **2026-08-13** — `docs/design/curriculum/population_draw_activation.json` carries
`activated.value: true` on the director's console word, and `draw_population_enabled()` returns `True` at HEAD. So the
stated precondition for axis B is met and both documents still read as though it is pending. Nothing in the machine is
wrong yet — the axis is dormant because nothing calls it, not because the flag is off — but the recorded *reason* for
its dormancy has been false for a day, and a reader triaging this atom would conclude the work is director-blocked when
it is caller-blocked. **QUEUED, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): both paths are outside this atom's
empty `file_scope` and belong to the rotation atom.

## 4. FINDING 4 — the rotation takes the activation state as an argument, not from the record (R15-shaped)

`enumerate_cells(grid, *, draw_population_enabled: bool)` requires the activation state to be **supplied by its
caller**. The single source of record for that state is the committed curriculum artefact, read by
`simulation.live_population.draw_population_enabled()`; the rotation never reads it. One truth, two sources.

A future wiring that passes `False` (or a stale constant) collapses axis B to a single no-op cell — and the coverage
control cannot catch it, because coverage is defined over the *world* axis: `test_one_period_visits_every_ratified_
world_dormant_seed_axis` asserts the guarantee in the dormant-axis configuration by name, and
`test_seed_axis_active_expands_grid` exercises the active path only against a hand-passed `True`. **No test pins the
axis-B state against the live curriculum record**, so the sweep would go on reporting guaranteed coverage of four
worlds while silently sampling one population forever. The control's subject is handed to it by the thing it checks.

**Recommendation for BUILD (not taken here):** `enumerate_cells` should DEFAULT to `draw_population_enabled()`, keeping
the parameter as a test-only override, plus an R15 test whose mutation is exactly *"pass `False` while the curriculum
says activated"* → red.

## 5. FINDING 5 — the ceiling: at the live seed, 10% of the cast can differ between runs

The activated book is **18 static hand-authored customers + N drawn**. W2_2's founding decision (2026-07-13) is
`ADDITIVE, not REPLACIVE` — it deliberately does not touch the hand-authored cast, because ~370 downstream
test/dashboard references depend on it. That decision sets a hard ceiling on what any seed can do:

- at the live seed `20260724`: N=2, so **2 of 20 = 10.0%** of the book can differ run to run;
- across seeds 0–19: N ranges 2–10, so **7.1% – 35.7%**;
- therefore **at least 64% of the cast is byte-identical in every run, by construction**, and at today's seed 90% is.

It goes further than composition. `simulation/life_events.py::_base_seed_for` and
`simulation/self_rationing.py::_base_seed_for` both derive their base seed from a **stable md5 of the `customer_id`**
when no explicit seed is passed. The static 18 keep the same ids in every run, so they receive the same life-event
stream and the same rationing behaviour in every run, forever — the invariance reaches past who is in the book into
what happens to them.

EP17's stated `gain` is *"the company stops memorising its customers and has to cope with a population it did not
choose."* **Under the current architecture that gain is capped at a tenth of the book**, and the company can memorise
the other 90% and be right every run. Making it true requires a replacive or partially-replacive draw — a curriculum
act (R13, director-reserved) with a ~370-reference blast radius. That is the decision this atom should put in front of
the director, and it is the one thing here no amount of seed wiring can deliver.

## 6. FINDING 6 — of the three things the atom's name promises to hide, two exist and one has no truth line

The atom is named *"mix, skew and vulnerability hidden from the company — the third line on the wall (truth / belief /
the draw)."* Taking those three separately:

- **Mix — LIVE.** Segment/commodity/band/payment vary by seed (§1) and `to_customer_dict()` renders only observables.
- **Skew — LIVE.** Consumption band and EAC vary by seed; the hidden `SyntheticCustomer.cohort` is populated
  (`assign_cohorts=True`, live in the seam since the CA1 ruling) and is omitted from the saas-shaped dict by
  construction, with the wall re-proven post-activation by
  `test_wall_drawn_book_never_exposes_ground_truth_cohort`.
- **Vulnerability — NO TRUTH LINE ON THE DRAWN CUSTOMER.** `SyntheticCustomer` has no vulnerability field. The world
  layer models vulnerability-adjacent *behaviour* (`simulation/self_rationing.py`, `activation_energy.py`,
  `willingness_classification.py`, `switching_propensity.py`), but the twelve-flag `VulnerabilityFlag` taxonomy lives
  entirely in `company/crm/vulnerability_register.py` and is fed by company-side detection (`service_log`,
  `life_event_detector`). So the company's vulnerability picture is a belief with **no drawn ground truth to be wrong
  about** — the third line of the wall is missing for the third axis, and no gap is computable there.

And the truth line that does exist covers only the drawn cohort: the hidden `cohort` object exists for the 2 SYN
customers and for none of the 18 static ones, so the belief-vs-truth gap this atom exists to enable is currently
measurable over **10% of the book**.

---

## What this pass changes about EP17

**It is not W2_2 relabelled, and it is not a fresh mechanism.** Restated from the evidence, EP17 is three items, only
the last of which is genuinely new work:

1. **Wire the built rotation to the seam** — a production caller for `run_rotation`, its cell's `population_seed` into
   `live_population(base_seed=…)`, plus §4's independence fix. Small; the design exists; no new mechanism.
2. **Put the additive ceiling to the director** — 90% of the cast is fixed at the live seed (§5). Replacive draw is
   R13 curriculum and the atom cannot decide it. This is what actually gates the stated `gain`.
3. **Draw vulnerability as world truth** (§6) — the only part of the atom's name with nothing behind it, and the only
   part that is EP17's own build rather than another atom's wiring.

`level_current` stays **0** and `loop_stage` stays **idle**: the deliverable of this atom is a mechanism, not this
document, so DISCOVER/FRAME output moves nothing. `depends_on: EP16_anchored_generators` is itself at level 0 and
epoch-4 parked, so the dependency is unmet either way. R12: no published number tuned; nothing written to any published
artefact. R13: no curriculum value authored, proposed or changed — §5 names a decision as the director's, it does not
take it.

**Queued, not taken** (SELF-INTERRUPT DISCIPLINE): the two stale dormancy statements (§3) and the `enumerate_cells`
independence fix (§4), both outside this atom's `file_scope` and owned by
`stratified_run_rotation_mechanism_2026-07-25`.

— FRAME, worker tick 2026-08-14, at HEAD `420b7449f`.
