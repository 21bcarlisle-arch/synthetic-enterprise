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

---

# PASS 2 — the draw has no consumer in the measurement layer

**Pass:** DISCOVER/FRAME only, worker tick 2026-08-17, LANE 3 idle draw. **No BUILD code written**; `file_scope` is
still `[]`. Measured at HEAD `71071ccf7`, with this doc, the atom's store file and `docs/design/maturity_map.yaml` all
clean in the shared tree at draw time.

## 7.0 Pass 1's six findings all survive, unrepaired

Re-checked at this HEAD before adding anything, because a closed DISCOVER doc is a hypothesis, not a record:
`run_rotation_cursor.json` is still `{"index": 0}` with still exactly one commit in its history (`f52a94133`, its own
build commit); `enumerate_cells(grid, *, draw_population_enabled)` still takes the flag as a caller-supplied argument
(`background/run_rotation.py:121`); all fourteen production call sites still call `live_population()` bare;
`SyntheticCustomer` still carries no vulnerability field. Nothing below re-narrates them.

## 7.1 The finding: wiring the rotation would move no measured gap

Pass 1 called item 1 — wire the built rotation to the seam — *"small, design exists; no new mechanism."* That is true
about the wiring and **wrong about the consequence**. The layer that would consume a varied population does not read
the seam at all.

**Observed, 12 of 12 coupled tools:** every `tools/couple_*.py` has **zero** references to `live_population`. Each
constructs its own population inline instead:

- `tools/couple_cohort.py` — the coupled pair for `W2_2_population_draw`, the exact atom EP17 varies —
  `build_scenario(n_customers, base_seed: int = 20260721)`, a bare `for i in range(n_customers)` over synthesised
  customer ids, `measure(n_customers: int = 3000)`.
- `tools/couple_w2_7_c9.py` — `build_scenario(n_customers)`, same `for i in range(n_customers)` shape,
  `measure(n_customers: int = 60000)`.

**The two frozen populations are not even the same frozen population.** `simulation/live_population.py:79` pins
`_DEFAULT_BASE_SEED = 20260724`; `couple_cohort.py` pins `base_seed = 20260721` in both `build_scenario` and `measure`,
and exposes it as `--seed` with the same default. So the atom's own coupled score is taken over a population drawn with
a seed the live seam has never used, at `n_customers: 3000` (the value recorded in the live ledger row) against a live
book of **20**.

**Consequence, stated as the mechanism it is:** wiring `run_rotation`'s cell `population_seed` into
`live_population(base_seed=…)` would change the 20-customer book that the publishing tools read, and would leave every
coupled gap in `docs/observability/coupled_gap_ledger.json` **byte-identical**, because none of those numbers is
computed over the book. Under R11's no-orphan-transitions rule that is a release whose effect is nothing — not nothing
*visible*, nothing *measured*. The COUPLED TRIAD's rule is that the gap is the score; EP17's stated purpose is to be
"the tournament's stated precondition and the third line on the wall." The draw and the score currently do not touch.

## 7.2 Why it hid: the seam-conformance control's subject is the publishing tools

The "route the book through the one seam" discipline was applied, and tested, on the **publishing** side only —
`tests/tools/test_generate_dashboard_data_population_seam.py`, `test_generate_hh_data_population_seam.py`,
`test_generate_customer_sample_population_seam.py`, `tests/simulation/test_run_phase_settlement_population_seam.py`.
There is **no seam-conformance test for any coupled tool**, and `grep live_population tests/tools/` returns hits from
the publishing-tool tests only. The control's population is the set of tools that *publish* a book; the set that
*measures against* a book was never in its subject. That is the wrong-population shape, and it is why twelve tools
drifted to hand-rolled populations without a red test.

**The needed shape exists exactly once, on the other side of a split:** `tools/couple_fabric.py:376` takes
`population_seed` and threads it into `ppop.draw_premise_population(n, base_seed=population_seed, …)` — but that is the
**premise** population (W1 fabric), not the customer book. So the parameter EP17 needs is already demonstrated as
workable in one coupled tool, against a different population.

## 7.3 What this changes about EP17's three items

Item 1 is **not** "small wiring." It is two things, and the second is the larger one:

1a. **The seam wiring** — a production caller for `run_rotation`, cell seed into `live_population(base_seed=…)`, plus
    pass 1 §4's independence fix. Still small, design still exists.
1b. **A measurement consumer** — until at least the coupled pair for `W2_2_population_draw` draws its population
    through the seam (or takes the rotation cell's seed), the varied draw is unobservable in the only place the project
    calls a score. This is where EP17's exit test has to live: not "the book differs run to run" (that is
    `W2_2`'s already-passing property) but "a coupled gap **moves** when the cell seed moves, and does not when it does
    not." Note the sequencing consequence: 1b interacts with the §5 ceiling — at N=2 drawn of 20, a gap taken over the
    book would have a support problem that the current n=3000 synthetic population does not, which is the honest reason
    the tools were written this way and must be designed for, not waved at.

Items 2 (the additive ceiling, director's under R13) and 3 (vulnerability as world truth) are unchanged.

`level_current` stays **0**, `loop_stage` stays **idle** — the deliverable is a mechanism, not this document. R12: no
published number tuned, nothing written to any published artefact. R13: no curriculum value authored, proposed or
changed. **Queued, not fixed on sight** (SELF-INTERRUPT DISCIPLINE): the twelve tools' population construction and the
missing seam-conformance control are outside this atom's `file_scope` and belong to the coupled-pair tools' own owners;
§7.2's missing control is the falsifier to build when 1b is drawn.

— FRAME pass 2, worker tick 2026-08-17, at HEAD `71071ccf7`.

---

# PASS 3 — the exit test pass 2 proposed cannot fire on the pair it was proposed for

*Worker tick 2026-08-17, DISCOVER/FRAME only, at HEAD `9996e4d16` with the map, the store file and this
document all clean in the shared tree at draw time. `level_current` stays **0**, `loop_stage` stays `idle`,
nothing in `file_scope` touched (it is empty). No BUILD code written.*

Pass 2 closed by naming where EP17's exit test belongs: *"not 'the book differs run to run' (that is `W2_2`'s
already-passing property) but 'a coupled gap **moves** when the cell seed moves, and does not when it does
not.'"* That is a claim about a measurement nobody had taken. This pass took it — the whole pass is one
question, run against `tools/couple_cohort.py`, the coupled pair for `W2_2_population_draw`, the exact atom
EP17 varies.

**It does not fire.** Not marginally: on the rotation grid's own declared seed axis it fires **zero** times
out of six pairs, while the population underneath differs on all six.

## 8.1 The measurement — the grid's own seed axis moves nothing the pair publishes

`docs/design/run_rotation_grid.json` declares `"population_seeds": [0, 1, 2, 3]`. That list is the entire
seed axis EP17 would rotate. Running the pair at each of them (n_customers=3000, the value in the live
ledger row):

```
seed=0   headline=1.0  worst3=1.0  worst_cell=accommodation::tenure=own_outright
seed=1   headline=1.0  worst3=1.0  worst_cell=accommodation::tenure=own_outright
seed=2   headline=1.0  worst3=1.0  worst_cell=accommodation::tenure=own_outright
seed=3   headline=1.0  worst3=1.0  worst_cell=accommodation::tenure=own_outright

pairs whose HEADLINE differs:          0/6
pairs whose worst3_mean_gap differs:   0/6      (the redundancy guard does not rescue it)
pairs whose 20-CELL VECTOR differs:    6/6      (8 of the 20 cells move on every pair)
```

Not "close to equal" — `1.0` exactly, on all four, on both published statistics. The draw changed; the score
did not. Under R11's no-orphan-transitions rule, an EP17 wired exactly as pass 2's item 1a describes and
tested exactly as pass 2's item 1b proposes would ship a release whose measured effect is **nothing**, and
would ship it with a green exit test's opposite: a test that correctly reports no movement.

**Base rate, seeds 0–99 at n=3000** (so this is not four unlucky seeds):

```
headline EXACTLY 1.0 (pinned at the no-skill floor):   73/100
headline range:                                        1.000000 .. 1.552941   (28 distinct values)
underlying price_sensitivity worst cell:               0.7021   .. 1.5529     (95 distinct values)
underlying channel_pref     worst cell:                0.1374   .. 0.3736
```

The population signal is large — the underlying quantity takes 95 distinct values across 100 seeds and spans
0.85. The headline transmits 65% of that span and, for 73% of seeds, **none of it**.

## 8.2 Why — the headline is a one-sided detector for "worse than no-skill"

The cause is already filed and still OPEN:
`docs/staging/WORKER_FINDING_A_WORST_CELL_HEADLINE_FLOORED_AT_THE_NO_SKILL_BASELINE_2026-08-10.md`. Twelve of
the twenty cells (accommodation/cars/nssec × 4 tenures) read exactly `1.0` **by construction** — those axes
have no company-side discovery mechanism, so the belief *is* the prior, so `gap = raw/g0 = 1.0` identically.
Re-measured here across all 100 seeds: those twelve never leave 1.0, on any seed.

What this pass adds is the other four. **`channel_pref` never exceeded 1.0 in 100 seeds** (max 0.3736). So the
published `worst_cell_score` is not max-of-20 and not even max-of-8 — it is arithmetically

```
headline = max(1.0, max over price_sensitivity's 4 cells)
```

a **one-sided detector**: it can only report that the drawn population made the company *worse than no-skill*,
and is structurally blind to a draw that made it better. EP17 exists so the company "stops memorising its
customers"; the pair's headline is, by construction, incapable of registering that as anything but the floor
unless the company also degrades past zero skill.

**This re-ranks the 2026-08-10 finding.** That doc requested rank `backlog` and reasoned "the row it affects
landed clean this tick and is honestly noted" — true of the row, and now refuted as a rank: the floor is the
direct blocker on EP17's stated exit test, an Epoch-4 floor item named in the ruling §1. **QUEUED, not
re-ranked on sight** (SELF-INTERRUPT DISCIPLINE) — that doc is outside this atom's `file_scope` and the
re-rank is its owner's, with this section as the evidence.

## 8.3 The other end: at the live book the pair does not degrade, it RAISES

Pass 2 flagged small-n as "a support problem … the honest reason the tools were written this way, [to] be
designed for, not waved at." Measured, it is not a support *problem*, it is a hard stop:

```
n=2      ValueError: no cell cleared the n_min=30 support bar   <- the drawn cohort alone
n=20     ValueError: no cell cleared the n_min=30 support bar   <- THE LIVE BOOK (18 static + 2 drawn)
n=30     ValueError            n=60   ValueError
n=120    eligible=10/20        n=300  eligible=20/20            <- first scoreable n is in (60, 120]
```

`N_MIN = 30` is a per-(axis, tenure-cell) bar, and a 20-customer book spreads across four tenure cells, so the
largest cell holds 10. Pass 2's item 1b — "the coupled pair draws its population through the seam" — as
written therefore replaces a published number with an exception at the only book size EP17 is about. The two
ends bracket the whole range and neither is usable: **below ~n=100 there is no score, above it the score is
floored on 73% of seeds.**

## 8.4 Third-order, and it is about the published row, not just EP17

At the ledger's own seed (20260721) the headline is not stable in n either:

```
n=300  1.500000   n=600  1.137931   n=1200 1.000000
n=3000 1.034483   n=6000 1.000000   n=12000 1.000000
```

`1.0344827586206897` is the value in `coupled_gap_ledger.json`. It is above the floor **only at the n the tool
happens to default to**; the same population process at a strictly better sample (n=6000, n=12000) reads
exactly 1.0. So the pair's one published claim — that the company is worse than no-skill in one cell — does
not survive its own sample being enlarged. QUEUED against the pair's owner, not fixed here; it is named
because EP17's score would inherit it.

## 8.5 What pass 3 changes about EP17

Item 1b is not "add a measurement consumer." It is **"EP17 has no fit-for-purpose score today, and finding one
is the atom's first build step, ahead of any wiring."** Concretely, and in this order:

1. **The exit test must be over the cell vector, not the headline.** The vector moved 6/6 where the headline
   moved 0/6; it is the statistic that already has the sensitivity the exit test needs. A defensible EP17
   falsifier: *the 8 discoverable cells' gap vector moves when the rotation cell's `population_seed` moves,
   and is byte-identical when it does not* — with the mutation being "thread a constant instead of the cell
   seed" → red. Note this is buildable **only at n ≥ ~120**, which is not the live book, so it tests the
   generator's variation, not the book's — an honest partial, and it must be labelled as one rather than
   presented as EP17's gain being measured.
2. **The floor and the support bar are upstream of the wiring.** Item 1a (pass 1 §4's independence fix, cell
   seed into `live_population(base_seed=…)`) stays small and stays correct, but sequencing it first buys a
   release with no observable. The two blockers named above are its precondition.
3. Items 2 (the additive ceiling, director's under R13) and 3 (vulnerability as world truth) are unchanged
   across all three passes.

## 8.6 Pass 1 and pass 2 re-verified at this HEAD

A closed DISCOVER doc is a hypothesis; every prior finding was re-checked before this section was added.
All survive, unrepaired. Two counts are **corrected upward**, in EP17's disfavour:

- Cursor `docs/observability/run_rotation_cursor.json` still `{"index": 0}`, still **exactly one commit** in
  its whole history (`f52a94133`, its own build commit). Never advanced.
- `enumerate_cells(grid, *, draw_population_enabled: bool)` still caller-supplied (`run_rotation.py:121`) —
  pass 1 §4's R15 independence defect stands.
- **Correction to pass 1 finding 1:** it recorded "all 14 production call sites call it bare." At this HEAD it
  is **27 bare call sites across 15 production modules** — pass 1's list omitted `saas/customers.py`,
  `saas/property_model.py` and `saas/reporting/annual_report.py`. The stronger statement is the exact one:
  `grep` for `live_population(` with a `base_seed` argument returns **one line in the whole repository, and it
  is the `def`**. The parameter EP17 must thread has no caller anywhere — not in production, not in a test.
- All 12 `tools/couple_*.py` still have zero `live_population` references.
- `SyntheticCustomer` still has no vulnerability field (`grep -c vulnerab simulation/population_draw.py` → 0).

R12: no published number tuned; every figure above is a read, and nothing was written to any published
artefact. R13: no curriculum value authored, proposed or changed.

— FRAME pass 3, worker tick 2026-08-17, at HEAD `9996e4d16`.
