# PB1 FRAME — the price does not exist, and the instrument cannot say so

**Atom:** `PB1_population_target_and_its_price` (`docs/design/maturity_map.yaml`, lane
`W2_customer_generator`, epoch 2, `loop_stage: idle`, `provenance: director_ruling`, dial 3).
**Reads first:** `docs/design/PB1_POPULATION_TARGET_DISCOVER.md` (the DISCOVER half — the proposed
target 4,000 and the finding that AO12 never priced this object). **Sibling:**
`docs/design/PB2_UNWON_REMAINDER_FRAME.md`. **Source ruling:**
`docs/staging/in_progress/DIRECTOR_RULING_POPULATION_AND_BOOK_GROWTH_2026-08-11.md` (deliverable 1).

**This is a LANE-3 DISCOVER/FRAME pass. No BUILD.** The atom is `idle`, which parks it for BUILD only
(`EPOCH_GATING_AND_ATOM_AUTHORSHIP.md` rule 1, `MATURITY_MAP.md` §9.7). `level_current` stays **0**,
`loop_stage` stays `idle`, no `file_scope` path was touched, no curriculum value moved (R13). Nothing
below is a measurement: this pass specifies the instrument that would take one, and deliberately does
not take it — exit (b) says the cost is READ from AO12's artefact, so a number produced here would be
the re-derivation the exit forbids.

---

## 0. What this pass adds to DISCOVER

DISCOVER found that AO12 has no stage whose subject is `simulation/premise_population.py`, and
therefore that PB1's exit (b) is unsatisfiable by construction. It named "one new AO12 stage" as
prerequisite (1) and stopped there. This pass does the three things that leaves owed:

| | |
|---|---|
| **§1 — why the gap was invisible** | AO12's three registry controls are **mutually closed**: they prove `STAGES`, `BINDING_RESOURCE` and `STAGE_FUNCS` agree *with each other*. Nothing anywhere relates the stage set to the subjects a consumer prices against, so a missing subject is not a red control — it is not a control's subject at all |
| **§2 — the missing measurement, specified** | `premise_population_draw` as a sixth stage: unit, binding resource, `target_units` conversion, `unmeasured` list, and the two R15 falsifiers that make it able to fail |
| **§3 — the coverage control** | `PRICED_SUBJECTS` + a `subjects_without_a_stage` report field, so exit (b) reads a machine field instead of comparing `detail` prose by eye. This is the durable half; the stage alone would fix the instance and leave the class |
| **§4 — the map finding** | PB1 `depends_on: [AO12]`, AO12 is `level_current: 2` of `level_target: 2`. **The edge is satisfied and the dependency is not.** `depends_on` is a completion relation; PB1 needed a coverage relation. Reported as ONE observed instance, not a base rate |
| **§5 — upgraded from claim to read** | DISCOVER's saturation scope-note was flagged there as "a claim about the shipped signature, not a measurement". Read at HEAD this pass: it holds, and it is stronger than stated |

**Recommendation, and I am not asking which:** build §2 and §3 together as one increment in AO12's
`file_scope`, §3 first. §2 alone turns PB1's UNDECIDED into a number and leaves the next consumer to
rediscover the same hole by eye. Level stays 0 — reasoning in §6, which is the part I would most
like contradicted.

---

## 1. Why a missing subject was invisible to a probe built to fail closed

AO12 is unusually careful about not-knowing. Its report carries a three-valued pressure algebra
(`tools/scale_probe_10k.py:180`) explicitly so "an unmeasured stage can never be silently ranked
LAST, which is precisely how a fail-open" reading happens (line 62); every stage carries an
`unmeasured: list[str]`; a zero per-unit cost degrades to a lower bound rather than to "free"
(`below_resolution`); and the report's own `reading_note` closes with the sentence a consumer is
supposed to obey:

> *"A stage with no projection is UNKNOWN and is never priced at zero — a consumer that substitutes 0 for an unknown has re-introduced the fail-open shape this report exists to avoid."*

That vocabulary has exactly two shapes in it: **a stage that ran and could not measure a component**
(`unmeasured`), and **a stage that did not run** (`test_report_lists_every_unrun_stage_as_unmeasured`).
There is no third shape for **a subject that was never a stage**, and that is the shape PB1 hit.

The controls behave accordingly. Both registry tests are closure assertions over the probe's own
constants:

```python
# tests/tools/test_scale_probe_10k.py:510
def test_every_stage_declares_a_binding_resource():
    assert set(probe.BINDING_RESOURCE) == set(probe.STAGES)
    assert set(probe.ADVISOR_PREDICTED_ORDER) <= set(probe.STAGES)

# tests/tools/test_scale_probe_10k.py:517
def test_stage_funcs_cover_every_declared_stage():
    assert set(probe.STAGE_FUNCS) == set(probe.STAGES)
```

Every term on both sides is drawn from `STAGES`. Delete `premise_population` from the world and both
stay green; they were green while PB1's exit was unsatisfiable. This is not a broken control — its
own docstring states its real subject accurately ("a control that never fires because it was never
wired"). It is a control whose subject is **the probe's internal consistency**, standing where a
reader expects one whose subject is **the probe's coverage**. R15's tautology shape, in its mildest
and most durable form: the checked value and the checking value come from the same set.

The consequence is the whole of DISCOVER §2. The only way to discover that no stage priced a premise
was to read five `detail` strings and notice that the one called `population_draw` says *"drew 10258
customers via simulation.population_draw"* — prose, compared by eye, by a reader who happened to
suspect it. A consumer who trusted the stage's NAME would have read 859.69 B/unit off
`population_draw` and priced 4,000 premises at 3.4 MB. That number is available, plausible, wrong,
and nothing in the artefact would have objected.

---

## 2. The missing measurement, specified

A sixth stage, `premise_population_draw`, in AO12's `file_scope` (`tools/scale_probe_10k.py`,
`tests/tools/test_scale_probe_10k.py`). Named for its subject, not its role, so the naming collision
that produced this pass cannot recur: `population_draw` keeps its name and its docstring gains the
sentence that it is the *acquisition* draw.

**Subject.** `simulation.premise_population.draw_premise_population(n, *, base_seed, as_of)`, read at
HEAD (`simulation/premise_population.py:646`). Returns `tuple[DrawnPremise, ...]`; `DrawnPremise` is
a frozen dataclass of `premise_id`, `household`, `epc_band`, `meter_cadence_days`, `epc_lodged`
(line 533), so the measured working set is the raked joint plus n records — the shape the stage must
report per unit.

| Field | Value | Why |
|---|---|---|
| `stage` | `premise_population_draw` | |
| `subject_kind` | `real` | it calls the shipped function, not a replica — unlike `site_publish`/`git_transport` |
| `unit` | `premise` | a new unit in this report; every existing one is `customer`, `record` or `file` |
| `BINDING_RESOURCE` | `rss_bytes` | the draw is in-memory construction with no output artefact; wall is not what tears (`population_draw`'s wall pressure is 0.0037 of budget) |
| `units_completed` | `len(population)` | and see falsifier F1 — a short draw is a DEFECT here, not saturation |
| `output_bytes` | `None` | it writes nothing. `None`, never `0` — the report's own rule |
| `baseline_rss_bytes` | `_vm_hwm_bytes()` after `raked_joint()` is computed and before the draw loop | `project_stage` subtracts it (line 375); include the raking and the stage prices the fit, not the population |
| `unmeasured` | see below, and it must not be empty | |

**`target_units` — the one place this can silently become the wrong subject again.** The probe has a
single knob, `--customers`, and each stage expresses that one target in its own unit (`_target_units`,
line 1186; `settlement_build` converts via its measured `records_per_customer`). A premise stage must
do the same, and the conversion is the funnel: `N_premises = ⌈q × N_book⌉`, `q` = quotes per win.
**`q` is a design constant from PB2 §4 (5.8324), not a measurement**, which makes it exactly the kind
of number that must be cited rather than inlined. Therefore:

* the stage takes `q` from PB2's cited source and records it in `extra` as `quotes_per_win`, the way
  `settlement_build` records `records_per_customer`;
* **fail-closed on its absence:** if `q` is unavailable, `target_units` is `None` and the stage's
  affordability is `UNDECIDED`. It must NOT default to `args.customers` — that silently prices a
  world where population equals book 1:1, which is both false and the precise fail-open this atom
  exists to avoid. A defaulted `q` would re-commit the original error inside the fix for it.

**`unmeasured`, non-empty by construction.** At minimum: *"the JOIN. This stage prices drawing a
premise stock. It does not price sampling the acquisition draw from that stock, because on today's
seam no such join exists (`simulation/population_draw.py` does not import `premise_population`).
A joined world's per-premise cost is this figure plus an unmeasured term, and the two must not be
read as the same number."* Same construction as `run_output_serialization`'s REDUCTION note, and it
inherits `test_a_stage_with_an_unmeasured_component_can_never_come_back_measured` (line 427), which
already forces such a stage to a lower bound forever.

**R15 falsifiers — the stage must be able to fail, on its own named defect.**

* **F1, the short draw.** Patch `draw_premise_population` to return fewer than `n`. The stage must
  raise, not report. This is the premise analogue of `test_the_probe_refuses_a_book_it_did_not_get`
  (line 270) — but the reason differs and that difference is the point: the customer stage tolerates
  batching because its generator saturates (line 237), whereas the premise draw is a plain
  `for i in range(n)` with no Poisson anywhere in it (§5), so a short draw there is a broken
  instrument and must never be projected from.
* **F2, the wrong subject — the mutation that would have caught this pass's finding.** Point the
  stage's body at `simulation.population_draw` while leaving its name and `detail` unchanged. The
  suite must RED. If it stays green, the stage is a label rather than a measurement and is worth
  nothing; a stage named for a subject it does not call is the whole defect, reproduced. Assert on
  the object actually constructed (`DrawnPremise` instances, `premise_id` prefix `P`), never on the
  `detail` string, which is the prose that failed the first time.

---

## 3. The coverage control — the durable half

§2 fixes the instance. A consumer pricing the *next* object still has only prose to check against.
The class fix is to give the probe a vocabulary for "this subject has no stage":

**`PRICED_SUBJECTS: dict[str, str]`** — a fourth registry mapping a subject's importable module path
to the stage that prices it (`simulation.population_draw` → `population_draw`,
`simulation.premise_population` → `premise_population_draw`, …). Two consequences, and the second is
the one that matters:

1. **A report field, `subjects_without_a_stage`.** Populated from `PRICED_SUBJECTS` minus the stages
   that ran. Exit (b) of this atom then reads a machine field. Today's answer would have been
   `["simulation.premise_population"]` and DISCOVER §2 would have been a one-line lookup instead of
   a forensic read of five `detail` strings.
2. **A refusal at the consumer's end.** A lookup for a subject not in the register returns UNKNOWN
   and raises rather than returning the nearest stage. The failure mode this pass exists to describe
   is not "the report lied" — it is "the report was silent and a neighbouring number was in reach".
   Silence must be loud at the point of the ask.

**Its own R15 falsifier, and it must not be a fourth closure assertion.** The mutation is: delete
`premise_population_draw` from `STAGES` while leaving `simulation.premise_population` in
`PRICED_SUBJECTS`, and assert the control REDs. That works *only* because the two registries have
independent sources — one lists what the probe does, the other lists what consumers ask it for.
`PRICED_SUBJECTS` must therefore be maintained from the consumer side (an atom that prices something
adds its subject), never generated from `STAGES`. Generated from `STAGES`, it is a fifth mutually
closed set and this entire section is decoration — which is the failure mode most likely to happen
if §3 is built carelessly, so it is stated here as the acceptance condition rather than left to
judgement.

---

## 4. The map finding: a satisfied edge over an unmet dependency

Read at HEAD (`docs/design/maturity_map.yaml`):

* `PB1_population_target_and_its_price` — `depends_on: ['AO12_scale_probe_10k']`, `level_current: 0`.
* `AO12_scale_probe_10k` — `level_current: 2`, `level_target: 2`, `loop_stage: build`. At target. Ran.
  Produced its artefact. By every reading the map supports, **PB1's dependency is satisfied.**

And PB1's exit (b) is unsatisfiable, because AO12 measured a different object.

`depends_on` encodes *"the thing I need has been completed"*. PB1 needed *"the thing I need covers my
subject"*. Those coincide for most edges and came apart here, and when they come apart the map reads
GREEN on the dependency and the atom stalls at level 0 with no red anywhere — no failing test, no
blocked flag, no unmet edge. The atom is drawable forever and completable never. That is why this
atom has now taken two full passes without moving: not a lane problem or a draw problem, a
**coverage relation the map has no way to express**.

**One instance, stated as one instance.** I have not measured how often a `depends_on` edge points at
a completed atom that does not cover its dependant, and one observed divergence is not a base rate.
What would measure it: for each edge, whether the dependant's exit text names an artefact or subject
the dependency's `file_scope` actually produces. That is a repo-wide census over 200+ atoms, it is
not this atom's work, and inventing a rate from this single case would be the error this project
files under its own name. Recorded here so the next reader of a stalled-at-0 atom with a green edge
has somewhere to look first.

---

## 5. Upgraded from claim to read: the premise draw has no saturation

DISCOVER §5 carried a scope note flagged in its own text as *"a claim about the shipped signature,
not a measurement"* — that a premise stage would inherit no λ≈745 limit. Read at HEAD this pass, it
holds, and it is stronger than it was stated:

```python
# simulation/premise_population.py:646
def draw_premise_population(n, *, base_seed, as_of) -> tuple[DrawnPremise, ...]:
    """Draw `n` premises. Growing `n` APPENDS — `P0007` never changes."""
    ...
    return tuple(draw_premise(f"P{i:04d}", ...) for i in range(n))
```

A plain `range(n)`, no Poisson, no batching, no λ. `_stage_population_draw`'s whole batching apparatus
(`max_batches`, the `+ batch * 7919` reseed, the `B{batch:04d}` id prefix, and
`test_the_generator_saturates_above_745`) exists for a saturation the premise draw does not have, so
the new stage is simpler than the one it sits beside — one call, no loop. Two further properties the
docstring's one sentence buys, both load-bearing downstream and neither previously written down:

* **Append-stability.** Raising the target later does not reshuffle premise identities, so a premise
  the company has won stays the same premise. Without that, "grow the population" would silently
  re-draw the book's premises underneath it — a curriculum change disguised as a scale change.
* **Cheap monotone measurement.** Because the draw is append-only in `n`, the stage can be measured
  at several `n` in one run and the per-unit constant checked for linearity, rather than assumed from
  one point. Every existing stage's per-unit constant is a single-point estimate; this one need not be.

Neither is a measurement and neither is claimed as one. Both are properties of the shipped signature,
read, quoted, and cited.

---

## 6. Level: held at 0, and here is the argument against holding

`level_current` stays **0**. The rule is that a DISCOVER/FRAME doc moves a level when the doc IS the
deliverable, so the honest test is what this atom's own record says its deliverable is. Its `gain`:

> *"Population scale stops being an inherited default and becomes a proposed number that was PRICED before it was bought."*

Two halves. The number exists (4,000, derived, DISCOVER §1). **The price does not**, and no document
can make it exist — exit (b) requires a reading from an instrument, and this pass has just specified
the instrument rather than produced it. Exit (b) is not partly met; it is unmet, and the atom's gain
is not half-delivered but blocked on its second half. A level move here would record "priced" against
an UNKNOWN, which is the fail-open shape both this atom's exit (d) and AO12's own `reading_note`
exist to refuse. So: 0.

**The argument against, stated because I would rather be contradicted than quietly right:** two full
passes have now produced substantive artefacts with no cell movement, and this project has a filed
report on exactly that pattern (`WORKER_REPORT_FIFTEEN_DRAWS_OF_REAL_WORK_AND_THE_LEVEL_NEVER_MOVED`).
The counter-argument is that PB1's blocker is now *named, specified and cheap* rather than diffuse —
§2 and §3 are one increment in an atom that is already at target and whose file_scope is open — so
the fix for the stall is to build the instrument, not to move the cell. If the director reads it the
other way, the move to make is not a level bump on PB1 but a **restatement of exit (b)** to permit a
price measured by this atom itself, and that restatement is his, not mine (R13-adjacent: the exit came
from his ruling's own governor sentence).

---

## 7. What this pass deliberately did not do

* **No BUILD.** No code, no test, no `file_scope` path touched. §2 and §3 are specifications with
  acceptance conditions, not implementations; both land in **AO12's** scope, not PB1's.
* **No measurement of the premise draw**, for the same reason DISCOVER declined it: exit (b) says the
  cost is read from the probe's artefact, and a figure taken here would have no instrument behind it
  and would hide the finding it was meant to surface.
* **No map edit beyond the bookkeeping sync.** `level_current` stays 0, `loop_stage` stays `idle`,
  `depends_on` is untouched — §4 is a finding about what the edge can *express*, not a proposal to
  rewire it. The one scalar that does move is `simplifications_count` 1→2, which
  `tools/merge_atom_status.py` requires to track the store and which
  `background/supervisor.py:4694` reads as this atom's progress signal — the mechanism by which a
  pass that honestly holds its level still registers as work rather than as a stall. Note and
  evidence were appended through `tools/simplifications_store.py`'s own API
  (`append_for_atom` / `append_to_record_for_atom`), never by hand-editing the YAML, so the other
  tenants of that file are preserved structurally.
* **No new atom minted** for §2/§3. They belong in AO12's existing `file_scope`, and a second atom
  over one tool would be a second way to do one thing (`MATURITY_MAP.md` §9.8's own bar).
* **No edit to PB2's documents**, and DISCOVER's queued finding against PB2 §4 (the 860 B/customer
  constant read onto premises — the same wrong-subject substitution this pass generalises) stays
  queued in PB1's record rather than fixed on sight (SELF_INTERRUPT_DISCIPLINE).
