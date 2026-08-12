# FINDING — an exit criterion can outlive the box's ability to meet it, and nothing asks

**Severity:** LATENT · **Lane:** H_harness

**Atom:** OPS2_publish_gate_head_worktree (lane H_harness, level 0→2, certified this tick)
**Date:** 2026-08-12
**Class:** the draw machinery asks "is the criterion met?" and never "can any future draw meet it?"

## Observed, with evidence

`OPS2_publish_gate_head_worktree` was drawn thirteen times. Its `build_note` closes twelve
consecutive ticks with some form of *"THE LEVEL DOES NOT MOVE AND THE OWED ITEM IS UNCHANGED:
a completed `in_tree_baseline`"* — 2026-08-11 eighth, ninth and tenth ticks say it in those
words. `level_current` stayed 0 across all of them while every tick landed real, green,
mutation-proven work on criteria 2–5.

The owed item was a runtime measurement. From 2026-08-12 it is not obtainable on this box:

- `tools/measure_publish_gate_subject_cost.py::_bounded_argv` REFUSES the phase before it
  starts when `PHASE_CEILING_IS_SUFFICIENT` is False.
- Re-derived from the kernel at the time of writing, not read off the artefact:
  `/proc/meminfo` `MemTotal: 16293956 kB` → `_box_safe_cap_mb()` = 11816 (with the 4096MB
  publisher reserve), against `PHASE_MEMORY_DEMAND_FLOOR_MB` = 10240 needing 12800MB at
  `CEILING_HEADROOM` 1.25. `PHASE_CEILING_IS_SUFFICIENT` is False.

So the state changed from *not yet measured* to *cannot be measured here* — and **no consumer
noticed**. `PHASE_CEILING_IS_SUFFICIENT` existed and nothing outside that tool read it. The
atom stayed `loop_stage: build`, stayed drawable, and would have been drawn a fourteenth time
with the same first criterion.

## Why this is silent rather than loud

An atom blocked on a *dependency* declares it (`blocked_on`, `depends_on`) and the queue can
see it. An atom blocked on a **criterion its hardware cannot satisfy** looks identical to an
atom that is simply not finished yet:

- it is drawable, so the rest-proof is satisfied and no stall alarm fires;
- every draw does genuine work, so no "idle turn" or "quiet busywork" metric trips;
- the level never moves, but a level that has not moved is the *normal* state of a `build`
  atom, so there is no transition for R5 to alert on.

The cost is therefore invisible by construction: twelve draws of real work, and the one
sentence deciding whether the atom can ever close was never re-asked.

## The class, and why it is not the two already filed

This project has filed the neighbours from the other side:

- `feedback_a_new_layer_above_a_control_must_inherit_its_subject` — an elimination must move
  the controls that pin it.
- the OPS2 tenth-tick pin (`test_the_exit_criterion_agrees_with_the_checkout_mechanism_that_ships`)
  — a criterion must not require a mechanism the code ships disabled.

Both are about the criterion disagreeing with the **code**. This one is the criterion
disagreeing with the **machine**: the mechanism ships, the code is correct, the criterion is
well-formed, and it is still unmeetable — because the box is too small. No amount of building
closes it and no existing control says so.

## Recommendation — and this is what I would take

Add a **feasibility** field to the map beside `blocked_on`, distinct from it: `infeasible_here`
with a free-text reason and, where one exists, the name of the live predicate that decides it
(here `measure_publish_gate_subject_cost.PHASE_CEILING_IS_SUFFICIENT`). Two consequences,
both mechanical:

1. `supervisor.py`'s draw treats an atom whose remaining exit criteria are all `infeasible_here`
   as **not drawable for BUILD** (DISCOVER/FRAME still available per the epoch-gating rule), so
   it stops consuming build ticks.
2. The digest reports it as a named category — "N atoms carry a criterion this box cannot
   satisfy" — because that is a *hardware* answer, and hardware is one of the few things the
   director can actually change.

Keying the field to a live predicate rather than a boolean is the R15 half: it must be able to
flip back to feasible on better hardware with nobody re-reading any prose. A hand-set boolean
would be the same prose-only rule CLAUDE.md says evaporates.

**Not taken this tick, deliberately** (SELF-INTERRUPT DISCIPLINE): it is a `supervisor.py` draw
change, which is BUILD work on a shared file, and OPS2 itself is now certified and off the
BUILD queue — so nothing is blocked by queueing this. Registered here rather than fixed on
sight.

## What was done instead

OPS2 was certified L0→L2 on criteria 2–5 delivered and criterion 1 closed as UNPAYABLE-HERE
(commit `224de7436`), with the tax carried in the map as a RESIDUAL rather than an open exit
criterion, an explicit do-not-relaunch, and a re-open instruction at `level_target` 3 on a
bigger box. Holding at level 0 on a measurement the hardware is proven unable to take is the
empty-feasible-set defect Rule 0 names.
