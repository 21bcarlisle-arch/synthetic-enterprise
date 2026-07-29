# B11 — Evolutionary tournament HARNESS: DISCOVER + FRAME

**Atom:** `B11_evolutionary_tournament_harness` (`docs/design/maturity_map.yaml`)
**Lane:** H_harness · **value_stream:** close_to_learn · **epoch:** 4 · **loop_stage:** `idle`
**Stage produced here:** DISCOVER (0→1) + FRAME (1→2). **No BUILD code was written** — this atom is
epoch-gated (`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` Rule 1: a parked atom is parked for BUILD only).
**Date:** 2026-07-29
**Depends on:** `SPINE_1_scenario_world_state` (map `depends_on`) · `A5_tournament_fitness_mortality`
(fitness/mortality values, `A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md`) · `A4_sim_approver` (soft,
named for feasibility, not a hard build dependency) · `A8_experiment_loop_speed` (soft, named "the
arithmetically feasible" prerequisite in this atom's own registration note, not a hard dependency).

Every claim below is labelled `observed-with-evidence` (read off disk this tick, file:line quoted) or
`inferred` (R9). This is B11's OWN FRAME doc — its `evidence:` list carries only this file, never a
sibling's `*_FRAME.md` (the exact fail-silent bug this atom's `evidence:` comment already documents:
`supervisor._atom_has_frame_doc` marks an atom FRAME-saturated on ANY `docs/design/*FRAME*.md`
evidence entry, so citing SPINE_1's/A5's shared FRAME doc previously made this atom read as framed
when it was not).

---

## PART 1 — DISCOVER: what already exists, and what the real gap is

### 1.1 `background/tournament_harness.py` does not exist — but a sibling built most of the mechanics

`observed-with-evidence`: `ls background/tournament_harness.py` → `No such file or directory`. The
file_scope's second half, `tests/background/test_tournament_harness.py`, likewise does not exist.

But `tools/tournament_runner.py` (2,796 lines fetched in full) **already exists**, built under the
sibling atom `A8_experiment_loop_speed` (its L2→L3 lever, landed 2026-07-16), and does a large share of
the low-level machinery a tournament harness needs:

- `LifeSpec`/`LifeResult` dataclasses — one life = one independent `python3 -m
  saas.reporting.annual_report --fast --save-json ... --output ...` subprocess, writing to an isolated
  output dir, with `LifeSpec.env` explicitly documented as "a caller-supplied seed/scenario/variant
  knob... the caller owns what the knobs mean" (`tournament_runner.py:205`) — an existing hook, not
  something B11 needs to invent, for injecting a scenario id per life.
- `run_tournament()` — a bounded, memory-safe, self-calibrating process pool fanning N independent
  lives, collecting each life's fitness JSON (`_FITNESS_FIELDS`: `total_net_gbp`, `total_gross_gbp`,
  `enterprise_value_gbp`, `final_treasury_gbp`, `net_margin_after_cost_to_serve_gbp`,
  `administration_event` — `:239-246`).
- `run_tiered_tournament()` — a cheap SCREEN tier (every candidate truncated to `screen_end_year`)
  ranks by `score_field` and culls to the top `survive_fraction`; only survivors pay for the expensive
  FULL tier. This is structurally a one-generation cull-and-survive step — the nearest existing
  analogue to a tournament "generation," built for a different reason (cutting dev cycle time, not
  running Epoch-4 evolution).
- A **fail-closed publish guard already built and R15 mutation-tested**: "a fast/tournament run is a
  DEVELOPMENT tool. It may NEVER publish, promote an atom, or feed the board pack" (`:23-39`),
  mechanised as forced `--fast`, a forbidden-output-roots check (`docs/staging`, `docs/reports`,
  `site/`), and "never imports/invokes `process_run_complete`, never writes a `run_complete` marker,
  never runs git." **B11's own publish guard (§2.6) should extend this exact pattern, not invent a
  parallel one** (SIMPLICITY GUARD).

**Named danger this DISCOVER pass surfaces (WALL risk #1, load-bearing for §2.4):**
`run_tiered_tournament`'s `score_field` parameter **defaults to `"total_net_gbp"`**
(`tournament_runner.py:511`), and nothing else in the module selects a fitness. This default is
honestly scoped — the module's own docstring says "harness/orchestration only," never claims to be a
director-authored fitness — but it is a real, single-objective, agent-chosen number sitting exactly
where B11's fitness-reading logic would need to plug in. If B11 reused `run_tiered_tournament` by
simply calling it with its default `score_field`, that would BE the silent self-authored-fitness
fallback this atom's own simplifications note names as the thing that must fail closed instead. This
is not a flaw in `tournament_runner.py` (it was never meant to carry a ratified fitness) — it is the
exact seam B11 must wrap deliberately rather than call through carelessly.

### 1.2 `A5_tournament_fitness_mortality` — no ratified artefact exists yet to read

`observed-with-evidence`: `A5_tournament_fitness_mortality` is `level_current: 0`, `loop_stage: idle`,
`provenance: proposal`. Its sole evidence is `docs/design/A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md`
(read in full). That document is explicit: **"FRAME OPTIONS ONLY... This document does not recommend a
default."** It catalogues 5 candidate fitness-function shapes (A pure-EV **strawman**, B
EV-hard-gated-on-compliance, C multi-objective Pareto/NSGA-II, D balanced-scorecard weighted-sum, E
constraint-satisfaction-with-EV-as-tiebreaker) × 4 candidate mortality rules (threshold cull,
instant-death-on-hard-breach, tournament/pairwise selection, elitism+diversity preservation),
independently combinable, **nothing chosen**.

There is consequently **no artefact format defined yet** — no committed file path, no YAML schema, no
`ratified:`/`ratification:` convention parallel to SPINE_1's curriculum artefacts. "B11 reads the
fitness definition from A5's artefact" (this atom's own registration note) has, today, literally
nothing to read. This is not a defect to fix here — it is the correct, honest state of a
values-decision atom still at FRAME — but it means B11's central fail-closed control (§2.4) is,
right now, **trivially and permanently true**: there is no artefact, so the harness must refuse, full
stop. §2.5 below names the *shape* of the artefact A5 would eventually need to produce for B11 to be
buildable at all — this is a descriptive interface requirement, not a value choice; B11 proposes no
fitness function, no mortality rule, and no weight.

**A tension flagged, not resolved:** `docs/design/BACKLOG.md`'s B11 entry glosses the atom in plain
English as *"EV is fitness, mortality is selection"* (`BACKLOG.md:174`). A5's own FRAME explicitly
names pure-EV as **"the strawman, to make the danger legible, not as a viable option"**
(`A5_TOURNAMENT_FITNESS_MORTALITY_FRAME.md:43`). BACKLOG's shorthand must not be read as pre-empting
A5's director-reserved decision — B11's design below treats the fitness function as unknown-until-
ratified, consistent with A5, not with BACKLOG's simplified gloss.

### 1.3 `SPINE_1_scenario_world_state` — the scenario set is enumerable, but nothing consumes it yet

`observed-with-evidence`: `sim/scenario/spine.py` exists (338 lines, read in full) — a frozen
`ScenarioSpine` dataclass, `load_world`/`available_worlds`/`rotation_set`/`select_for_rotation`,
`grid_label_index`/`resolve_grid_label`. `available_worlds()` lists the curriculum artefacts under
`sim/scenario/curriculum/*.yaml` (per the map's own 2026-07-29 rotation-binding note: `history_replay`,
`neso_central`, `crisis_2021_22`, `supply_glut`). `rotation_set()` returns only
`ratified and in_rotation and not is_baseline` worlds — **currently empty**, since (per the map's own
log) all four real worlds still carry `true_probability: null` and `rotation_eligible: False`.

**Critical gap for B11, confirmed by direct grep:** `grep -rn "paths_as_of"` across the whole tree
(excluding worktree mirrors and tests) returns exactly **two** hits, both inside `spine.py` itself
(the method's own definition and its docstring). **Zero generators call it.** No SIM generator
(`gas_scenario_generator.py`, `bimodal_generator.py`, `forward_curve.py`, etc.) reads a
`ScenarioSpine`'s overridden paths. So selecting a non-baseline `world_id` today changes **nothing**
about what a life actually experiences — a tournament wired today, passing a different `world_id` per
`LifeSpec.env`, would produce byte-identical lives regardless of which world was named, because nothing
downstream consumes the override.

**Implication for B11:** the map's `depends_on: [SPINE_1_scenario_world_state]` is correctly named but
should be read precisely — it depends on SPINE_1 being **consumed** by a generator, not merely on the
object/registry existing. Today SPINE_1 is a real, necessary precondition still one wiring-step (a
different atom's BUILD, not B11's) away from mattering to an actual rerun.

### 1.4 `A8_experiment_loop_speed` — arithmetic feasibility state

`observed-with-evidence`: `level_current: 2` (target 3), `loop_stage: idle` (parked per its own log,
pending `ARCH1_internal_seams` wiring `build_sim_interface` into the run path — re-verified stale
across at least four 2026-07-16 turns per its simplifications). Two of its three named in-scope levers
are landed and directly reusable by B11 (self-calibrating worker cap; tiered SCREEN/FULL culling — both
inside `tools/tournament_runner.py`, §1.1 above). The remaining big lever (mock-interface composition,
~8-10×) is blocked on ARCH1 and outside both A8's and B11's file_scope.

Per-life cost is still real and un-shrunk by anything B11 can do: `tournament_runner.py`'s own measured
comments record ~24s for a truncated (`--end-year 2016`) life and ~351s/5.67GB RSS for a full-window
life. A5's own arithmetic (10,000 lives at ~500s serial ≈ 58 days; feasibility target ≈60s/life) is
therefore **unchanged in its full-fidelity form** — A8's landed levers cut wall-clock for running a
*fixed* population, they do not cut the per-life cost itself. A genuinely full-population,
full-fidelity tournament remains a multi-day undertaking even with A8 fully landed; the FRAME below
does not paper over this.

### 1.5 `A4_sim_approver` — soft dependency, not blocking B11's FRAME

`observed-with-evidence`: `level_current: 0`, `loop_stage: idle`, its own FRAME doc exists
(`docs/design/frame/A4_sim_approver_FRAME.md`), BUILD deferred pending `A3_approval_interface`. It
plays a policy-agent standing in for a human approver across many tournament lives. B11's FRAME does
not require A4 to exist — a harness that runs, scores, and culls lives does not need an in-loop human-
analogue approver to be *designed*. A real multi-day unattended BUILD of B11 will eventually want
something in that role; named here as a soft dependency matching the map's own framing of A8 as merely
"arithmetically feasible," not a hard blocker.

### 1.6 The existing single-run entrypoint B11 should reuse, and the four things nothing yet does

`observed-with-evidence`: `saas/reporting/annual_report.py`, invoked via
`python3 -m saas.reporting.annual_report --fast --save-json <path> --output <path> [--end-year N]`, is
the **one** existing "run the company to completion, get a scored JSON" entrypoint in the tree, already
wrapped by `tools/tournament_runner.py`. B11 should reuse this entrypoint and `tournament_runner.py`'s
process-pool/isolation/tiering machinery wholesale (SIMPLICITY GUARD) rather than build a second
orchestration layer. What is genuinely missing, confirmed absent by this DISCOVER pass:

1. **Per-life scenario selection actually consumed** — blocked on §1.3's generator-wiring gap, not on
   B11 itself.
2. **A multi-generation reproduction loop** — `tournament_runner.py` runs **one wave** of independent
   lives and stops; there is no generation→generation survivor-reproduction loop anywhere in the tree.
3. **Fitness/mortality read from a ratified artefact** instead of a caller-supplied `score_field`
   default (§1.1's named danger).
4. **A death/endpoint definition** richer than "the fitness JSON exists" — today `LifeResult.ok` only
   checks that `total_net_gbp` is present; nothing classifies a life as DIED vs SURVIVED vs
   ENDPOINT-REACHED, though `administration_event` is already an observable field sitting unused for
   exactly this purpose (`_FITNESS_FIELDS`, `tournament_runner.py:245`).

---

## PART 2 — FRAME: the harness's design (nothing built)

### 2.1 Purpose, in one sentence

A rerun loop that takes a company **configuration** + a director-ratified **scenario set** (SPINE_1's
rotation) + a director-ratified **fitness-and-mortality artefact reference** (never a self-authored
one) and executes N lives to death-or-endpoint, scores each, ranks, culls per the ratified mortality
rule, and publishes a finding — reusing `tools/tournament_runner.py`'s process-pool/isolation machinery
for the mechanical fan-out, adding only what §1.6 found missing: generation-to-generation reproduction,
scenario consumption, ratified-artefact reading, and an explicit death/endpoint classification.

### 2.2 Death vs endpoint — two distinct, concrete operational definitions

- **Death (mid-life, unconditional, structural):** `administration_event = true` in the life's fitness
  JSON (already an observable field, §1.6.4) is treated as an unconditional hard death **regardless of
  what the ratified fitness score would otherwise read**. A company that goes bust does not get ranked
  against solvent survivors on EV — that is a physical/structural fact about the life, not a scored
  judgement, and no fitness function (however A5 eventually ratifies it) should be able to override it.
- **Death (generation-boundary cull):** whichever of A5's 4 candidate mortality rules is ratified
  (threshold cull / instant-death-on-hard-breach / pairwise / elitism+diversity) — read from the
  artefact at generation-transition time, never hardcoded in B11 (§2.4, §2.7 Control 3).
- **Endpoint:** the scenario's own defined horizon (a fixed calendar window or ledger-period count tied
  to the world's curriculum artefact). A life that reaches its endpoint without triggering structural
  death is scored SURVIVED. B11 does not itself decide how long "long enough" is — that is curriculum
  (R13), the same director-authored artefact family that defines the scenario worlds' own extents.
- Both concepts are necessary together: a horizon with no death check lets a company limp to the
  endpoint mid-insolvency and be scored as a survivor; a death check with no horizon has no stopping
  rule for a company that neither goes bust nor obviously "wins."

### 2.3 The rerun loop shape (mechanism only, no values)

- Reuse `LifeSpec.env` to carry (a) the scenario `world_id` — a documented no-op today per §1.3 (this
  is honestly disclosed, not a lie: B11 can be BUILT and TESTED against today's byte-identical-baseline
  behaviour, and will pick up real per-scenario variation for free the day a generator starts reading
  `paths_as_of`, with no change required in B11 itself) — and (b) a company **configuration** id, whose
  internal meaning (what actually varies between configurations) is explicitly **out of scope for
  B11**; B11 receives a configuration and reruns it, it does not define the search space a
  configuration is drawn from.
- **One generation** = `tournament_runner.run_tournament()` (or `run_tiered_tournament()`, reused as-
  is) fanning every surviving configuration across every scenario-set member the director has ratified
  into rotation (`SPINE_1.rotation_set()`) for that generation. BACKLOG's own DoD says "reruns... across
  B1's scenario set" (plural) — one **life** is therefore `(configuration × scenario)`, not one life per
  configuration.
- **Reproduction between generations** — the part §1.6.2 found has no precedent anywhere in the tree:
  given generation *g*'s scored+ranked+culled survivors, generation *g+1*'s population is derived per
  A5's ratified mortality rule. B11 **mechanises** this transition (read survivors, read the rule,
  compute *g+1*'s population); it never **authors** the rule.
- **Per-scenario score aggregation is itself a nested value-shaped gap**, named honestly rather than
  guessed at: when one configuration runs against several scenarios in a generation, combining those
  per-scenario scores into one ranking number (mean? worst-case? Pareto per-scenario?) is a choice A5's
  artefact must specify, or B11 has no principled way to combine them and must refuse rather than guess
  (folded into the artefact contract, §2.5).

### 2.4 THE WALL — the fail-closed control (named in this atom's own simplifications note)

- **Named defect:** the harness silently falls back to a self-authored/default fitness (e.g.
  `tournament_runner.py`'s existing `score_field="total_net_gbp"` default, or any hardcoded EV-only
  scoring) when A5's ratified artefact is absent, malformed, or not yet ratified.
- **Test:** `tests/background/test_tournament_harness.py::test_refuses_to_run_without_ratified_fitness`
  — asserts the harness's entrypoint **raises** (never returns a summary, never writes a
  `tournament_summary.json`, never runs a single life) when: (a) no fitness/mortality artefact file
  exists at the agreed path; (b) an artefact exists but lacks a `ratified: true` **plus** a
  `ratification: {...}` record — mirroring SPINE_1's own R13 ratification guard verbatim
  (`sim/scenario/spine.py:225-232`: "a `ratified: true` with no ratification record is a malformed
  curriculum and is REJECTED — never loaded as silently rotation-eligible"; reuse that exact pattern
  rather than invent a parallel one, SIMPLICITY GUARD); (c) an artefact exists and is ratified, but is
  missing a field the harness needs to compute a score — fail on the missing field, never on a silently
  substituted default.
- **Mutation that must go RED:** delete/rename the artefact path and confirm a naive reuse of
  `run_tiered_tournament`'s default `score_field` would otherwise let a life run anyway — proving that
  §1.1's named danger (the existing default) is exactly the fail-open case this control exists to
  catch. B11 must **wrap** `tournament_runner`'s functions with its own artefact-reading gate in front,
  never call them with a fitness sourced from anywhere but the ratified artefact.

### 2.5 The artefact contract B11 needs A5 to eventually produce (descriptive, not a value choice)

For B11 to be buildable at all, A5's eventual ratified output needs to name (not fill in) these fields:

- a **fitness computation reference** — which of A5's 5 candidate shapes is chosen, and that shape's
  own parameters/weights/thresholds;
- a **mortality rule reference** — which of A5's 4 candidate rules, and its parameters (e.g. cull
  fraction);
- a **per-scenario score aggregation rule** (§2.3's nested gap);
- a `ratified: true` + `ratification: {...}` record, structurally identical to SPINE_1's curriculum
  convention (§2.4).

B11 proposes no values for any of these fields here — it only names that they must exist for the
interface to be checkable, the same "contract without content" move already made at the SIM/company
wall itself (`interface/contracts/`).

### 2.6 Publication — what gets published, and the guard against pre-empting A5

- **Publish target:** a tournament FINDING artefact (e.g.
  `docs/observability/tournament_results/<run_id>.json` + a short summary) — explicitly **not** the
  board pack, the annual report, or `site/`, reusing `tournament_runner.py`'s own forbidden-output-roots
  guard verbatim (`docs/staging`, `docs/reports`, `site/`), extended with a tournament-findings root if
  one is needed.
- The published finding reports scores and rankings **as computed by A5's ratified artefact** — it must
  never present commentary implying a fitness judgement B11 itself authored (e.g. it may report "ranked
  #1 by ratified fitness definition v3," never an unqualified "the winning configuration is best" in
  the harness's own voice) — the distinction matters because a casual reader must not mistake the
  harness's mechanical report for a values statement B11 is not authorised to make.

### 2.7 R15 controls — three, each with a named defect and a concrete mutation

**Control 1 (§2.4) — refuses to run without a ratified fitness artefact.** Covered above.

**Control 2 — structural death overrides a good score.**
- *Named defect:* a life with `administration_event = true` but a high `total_net_gbp` (e.g. the sim
  recorded a strong headline number moments before insolvency) is scored as a ranked survivor instead
  of DIED.
- *Mutation that must go RED:* force `administration_event = true` with a high `total_net_gbp` in a
  fixture life; the harness must classify it DIED and exclude it from the generation's ranked-survivor
  list regardless of score.

**Control 3 — the mortality rule actually applied is read, not hardcoded.**
- *Named defect:* the harness always applies the same cull mechanic (e.g. a hardcoded "bottom 50%")
  irrespective of what the artefact says.
- *Mutation that must go RED:* run the harness twice against an identical population+scores but two
  artefacts ratifying **different** mortality rules (e.g. threshold-cull vs elitism+diversity); the two
  runs must produce **different** survivor sets. Identical survivor sets across differently-ratified
  artefacts proves the rule is decorative, not consumed.

### 2.8 Scale/portability constraints (standing constraints, applied here)

- **C-S2 (determinism):** each life is a fresh subprocess (already true of `tournament_runner.py`'s
  isolation); generation-to-generation seeding must derive deterministically from
  `(generation, configuration_id, scenario_id)`, never from wall-clock time, so a tournament replay
  reproduces identical generations.
- **C-S5:** the number of lives/generations/scenarios per generation are declared run parameters, never
  hardcoded constants inside the harness.
- **SIMPLICITY GUARD:** no new process-pool or subprocess-orchestration machinery. B11's own
  `file_scope` (`background/tournament_harness.py`) is a thin generation-loop + artefact-reading +
  death-classification + publication layer sitting **on top of** `tools/tournament_runner.py`'s
  existing `run_tournament`/`run_tiered_tournament`, not a parallel reimplementation.

### 2.9 DoD mapped to BACKLOG.md's own acceptance criteria

BACKLOG.md's B11 entry (`docs/design/BACKLOG.md:177-178`): *"a harness reruns a company configuration
across B1's scenario set, scores each on Survive/Earn/Abate, and ranks; mortality removes
configurations; results published as a finding."* Mapped to this FRAME:

| BACKLOG clause | This FRAME's answer |
|---|---|
| "reruns a company configuration across B1's scenario set" | §2.3 — one generation fans (configuration × ratified-rotation-scenario) via reused `tournament_runner.run_tournament` |
| "scores each on Survive/Earn/Abate" | Survive = §2.2's death/endpoint classification (Control 2); Earn/Abate = fields inside A5's ratified fitness reference (§2.5) — **not** B11's to define, consistent with A5's own multi-objective options (C/D/E), not the BACKLOG gloss's pure-EV shorthand (§1.2) |
| "mortality removes configurations" | §2.3's generation-boundary reproduction step, driven by A5's ratified mortality rule (Control 3) |
| "results published as a finding" | §2.6 — an isolated finding artefact, never the board pack |

### 2.10 Level

**`level_current` held at 0.** Nothing is built — BUILD is epoch-gated (epoch 4) and this pass wrote
no code. Saturation via this FRAME artefact (cited alone in this atom's `evidence:` list, per §-header
above) is what stops the DISCOVER/FRAME re-draw, not a level bump — the same disposition
`H29_import_time_env_capture_test_isolation` and `B8_discovered_price_sensitivity_holdout` already took.

### 2.11 What BUILD would do first, in order (once opened)

1. The artefact-reading + fail-closed refusal (§2.4) — buildable and testable **today**, since "no
   ratified artefact exists" is the live, true, currently-observed state (§1.2).
2. Death classification wrapping the existing `administration_event` field (§2.7 Control 2) — needs no
   new sim work.
3. Wire `LifeSpec.env`'s scenario slot to `SPINE_1.select_for_rotation()` — a documented no-op today
   (§2.3), becomes real the day a generator consumes `paths_as_of` (a different atom's job).
4. The multi-generation reproduction loop itself (§2.3) — the part with no existing precedent anywhere
   in the tree.
5. Publication artefact + forbidden-roots guard extension (§2.6).

`inferred`: steps 1–2 carry the real leverage today, because — unusually for this atom — they need no
upstream atom to land first and are directly testable against the tree's actual current state.
