# G4_unified_failure_register — FRAME (canonical per-atom, doc-only)

**Atom:** `G4_unified_failure_register` · lane `G_data_learning` · epoch 2 · `provenance: proposal`
· `level_current: 0` → `level_target: 3` · `loop_stage: idle` · dial 3

**Turn:** H17 Lane-3 FRAME (doc-only, no BUILD code — EPOCH_GATING Rule 1; no map edit — F1,
level reported via `docs/design/atom_status/G4_unified_failure_register.yaml`).

---

## Why this doc exists (and why it is NOT churn)

G4's FRAME-stage design is already **complete** — it lives in
`docs/design/UNIFIED_FAILURE_REGISTER.md` (281 lines: problem statement, an 8-retro-derived
failure-class taxonomy, the append-only JSONL register schema, the global per-class strike
counter + `[R3-ALARM]` contract, Method-door surfacing shape, an R15 mutation-test plan, and a
BUILD decomposition). There is nothing left to re-derive.

The problem is purely **detectability**: the intrinsic frame-saturation guard
(`background/supervisor.py::_atom_has_frame_doc`) recognises a per-atom FRAME doc only when its
**filename** contains `FRAME` or the atom's id/slug. `UNIFIED_FAILURE_REGISTER.md` contains
neither — and the guard's own docstring names this exact case as a known, accepted gap: *"A
per-atom FRAME doc whose FILENAME carries neither `FRAME` nor the id/slug (e.g. G4's
`UNIFIED_FAILURE_REGISTER.md`) is out of reach of any filename heuristic without risking a
false-positive on a partial design doc — for those the documented `frame_saturated: true`
explicit override (a map-writer step) remains the intended escape."* Absent that override (a
map edit this fork may not make, per F1), G4 kept being — correctly, given the guard's own
rules — re-offered by the idle DISCOVER/FRAME draw as genuinely un-FRAMEd, even though its FRAME
work was done.

This doc is the missing **detectable terminus**: a thin pointer at a filename the guard's
existing heuristic already matches (`G4_unified_failure_register_FRAME.md`, under `docs/design/`,
contains both `FRAME` and the atom's own id). Adding its path to G4's `evidence` list makes
`_is_frame_saturated(G4)` return `True` on the next cycle — computed from disk, MAKE_IT_STICK,
no marker to remember — **without re-emitting a single line of the design**. Re-deriving the
taxonomy/schema/counter here would itself be the churn SELF_INTERRUPT_DISCIPLINE + R12 forbid;
this doc consolidates a pointer, not the content.

`docs/design/UNIFIED_FAILURE_REGISTER.md` remains untouched and authoritative for the full
design — forward-only, per the standing "don't rework shipped docs" convention.

---

## The design, in one screen (distilled from UNIFIED_FAILURE_REGISTER.md — cited, not restated)

- **Problem:** R3 ("two-strike redesign") currently counts strikes **per component**, implicitly,
  by human attention — three real incidents (wake-doorbell, tmux-injection, stale-running-code)
  show the *same failure class* recurring across *different* components, with R3 firing late or
  only by luck of who happened to be tracing the thread.
- **Fix:** an append-only cross-retro index (`docs/retrospectives/failure_register.jsonl`, one
  JSON object per line — matches the existing `naive_organ_log.jsonl`/`test_execution_log.jsonl`
  precedent) tagging each occurrence with one or more **failure-class tags** from an open,
  retro-derived taxonomy (`shared-primitive-bypass`, `committed-not-running`,
  `external-state-misdetection`, `landed-verification-gap`,
  `fail-silent-self-referential-monitor`, `false-completion-claim`,
  `control-tautology-or-fail-open`).
- **The key mechanism:** strike-counting is **GLOBAL per class**, not per component —
  `count_strikes(class_tag)` counts every entry ever tagged with that class, anywhere in the
  codebase, so the Nth strike of a *class* is a computed property, not a per-instance one a human
  has to notice across unrelated-looking components.
- **Alarm:** on every append, recompute the tag's global count; `>= 2` emits a non-blocking
  `[R3-ALARM]` finding (advisory, queued per SELF_INTERRUPT_DISCIPLINE — never halts BUILD) naming
  the class, the count, and every prior instance's retro link — making "second strike mandates
  redesign" true by construction instead of by hindsight.
- **Surfacing:** a `failure_register_summary` section added to `site/data/method.json`
  (`tools/generate_method_data.py`'s existing generation pass), alongside the Method door's
  existing R1–R6 rules list and retro library — read-only, R11-verified on the live page.
- **Verification:** three named R15 mutation tests before the strike-alarm counts as evidence —
  fires on a planted second strike (must-catch), does not fail-open on an empty/missing register
  (returns a distinct "unavailable" state, not a same-shaped `0`), does not fail-silent on a
  malformed line (skips + surfaces `parse_errors`, never silently under-counts).
- Full spec, worked schema, and the three retro-sourced examples: `docs/design/
  UNIFIED_FAILURE_REGISTER.md` §1–§6 — authoritative, cited here not duplicated.

---

## The single BUILD-unblock gate

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `G4_unified_failure_register` | 2 | **0 (→3)** | No upstream atom `depends_on` — G4 has no coupled twin and no data-availability blocker. Epoch 2 is already the current open epoch (`docs/design/DIRECTOR_CANON.md` §"Epoch 2 is the current open epoch"), so the ONLY gate is the per-atom BUILD-open authorization itself: **TWIN's standing-approver call to move `loop_stage` off `idle`** (`DIRECTOR_CANON.md` v2 §3a — "BUILD authorization within an open epoch... explicitly delegated to the twin"). Once opened, BUILD is the small, SIMPLICITY-GUARD-sized decomposition already named in UNIFIED_FAILURE_REGISTER.md §7 (L2: `failure_register.jsonl` + `tools/failure_register.py` + its R15 tests; L3: the Method-door surfacing). | DIAL (per-atom epoch-open call, not a cross-atom dependency) |

**Disposition:** level **HELD at 0** (proposal atom; FRAME complete ≠ built; BUILD-gated per
EPOCH_GATING Rule 1). This FRAME is G4's canonical, detectable terminus — the next idle draw
reads G4 as frame-saturated and yields to genuinely-un-FRAMEd work instead. No BUILD code, no
map edit (F1).

---

*Source consolidated (not re-derived): `docs/design/UNIFIED_FAILURE_REGISTER.md` (full taxonomy,
schema, counter/alarm contract, Method-door surfacing shape, R15 test plan, BUILD decomposition).
Detection rule satisfied: `background/supervisor.py::_atom_has_frame_doc` (~line 565), whose own
docstring names G4's `UNIFIED_FAILURE_REGISTER.md` as the exact filename-heuristic false-negative
this doc closes.*
