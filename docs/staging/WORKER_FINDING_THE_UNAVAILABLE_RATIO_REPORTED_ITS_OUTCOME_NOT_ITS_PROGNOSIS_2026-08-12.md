# FINDING — the unavailable ratio reported its outcome, not its prognosis

**Severity:** LATENT · **Lane:** H_harness

**Atom:** OPS2_publish_gate_head_worktree (lane H_harness, level 0→2)
**Date:** 2026-08-12
**Class:** a record that describes what happened but not whether it can be fixed

## Observed, with evidence

`docs/observability/publish_gate_subject_cost.json` carried:

> `ratio_unavailable_because`: "these phases did not run to completion, so their seconds
> is a lower bound and cannot be a ratio term: in_tree_baseline"

Accurate about the **outcome**, and silent on the **prognosis**. Every consumer reads it as
transient — run it again. On this box it is not, and had not been for a day.

The ratchet built on 2026-08-11 had already reached its designed terminus, unremarked:

| quantity | value | source |
|---|---|---|
| banked demand floor | 10240 MB | `in_tree_baseline.hit_memory_ceiling: true`, killed AT its ceiling |
| ceiling that implies at 1.25x | 12800 MB | `_derive_phase_ceiling_mb` |
| what this box can spare | 11816 MB | 15912 MB MemTotal − 4096 MB publisher reserve |
| `PHASE_CEILING_IS_SUFFICIENT` | **False** | `_ceiling_is_sufficient` |

So `_bounded_argv` **refuses the phase before it starts**. That refusal is correct and was
already R15-proven (`test_a_demand_this_box_cannot_bound_refuses_the_phase_rather_than_clamping_it`).
What was missing is that nothing *said* so where a reader looks.

## Why it matters

The atom's own EXIT text still read "the CEILING must be re-derived from a measured peak
**before any relaunch can complete**" — which reads as *re-derive, then relaunch*. The
re-derivation is done; its verdict is that the phase is unrunnable here. A reader following the
old text funds launch 15 to re-learn what launches 12–14 each cost ~25 minutes to learn.

This is the same shape as the defect that produced the ratchet: `WORKER_FINDING_THE_CEILING_KILL_WAS_BANKED_AS_A_SIGTERM_2026-08-11`
had the record misreport a ceiling kill as a plain SIGTERM. Both times the mechanism was right
and **the record understated what it knew**.

## Fixed

- `_terminus_clause(phases, box_total_mb)` — names the measured demand, the ceiling it implies,
  and what the box can spare, or returns `""` when a relaunch is still worth funding. Derived
  from the record's own phases, never from the import-time `PHASE_CEILING_IS_SUFFICIENT`, so a
  run that banks a new floor describes the floor it just banked.
- Distinguishes "box too small" from "kernel would not report MemTotal" — both refuse the phase
  and call for different next moves.
- `_record_ratio` extracted from `_run_measurement` so the **wiring** is reachable without
  paying 40 minutes for two timed suites.
- Live record re-derived over its unchanged phases (no re-timing) — it now states the terminus.
- Atom EXIT text updated: criterion 1 is **not deliverable on this box**, not "still owed".

## R15 both ways

| test | proves |
|---|---|
| `test_an_unrunnable_phase_says_a_relaunch_cannot_fix_it` | the clause names all three figures |
| `test_mutation_a_phase_that_still_fits_gets_no_terminus_clause` | it is not a fixed string — a phase that fits stays retryable |
| `test_a_record_with_no_demand_evidence_makes_no_prognosis` | silence is not evidence the box is too small |
| `test_a_box_that_will_not_say_its_size_is_told_apart_from_a_box_that_is_too_small` | the two refusals differ |
| `test_the_prognosis_reaches_the_artefact_a_reader_actually_opens` | **wiring** — mutation (drop the clause from the format call) reds this while all four unit tests above still pass |

That last mutation was run: it reddened exactly one test and left the other four green, which is
the gap a helper-only test would have left.

`box_total_mb` is threaded as a parameter for the reason the `runnable_ceiling` fixture gives —
a test whose verdict is decided by how much RAM the machine happens to have is not a test of the
clause.

## Side evidence for criterion 4, observed not inferred

While editing `tools/measure_publish_gate_subject_cost.py`, a live publish gate (PID 888362) was
running that same module's tests. Its `/proc/888362/cwd` was `/var/tmp/publish-gate-head-cp1qjcm1`
— a HEAD checkout — so the working-tree edits, including a ~1s mutation window, were invisible to
it. That is the property the 2026-08-09 ruling bought, seen working under a real concurrent edit.

## Status of the atom

Criteria 2–5 are built and R15-proven (timeout 4500s ≥ the 3752s the record implies; sweep;
own test module; single-place hash contract). Criterion 1 is now **reported as undeliverable
here with its arithmetic**, rather than pending. The throwaway/in-tree tax stays estimated until
there is a box that can hold the in-tree phase — that is a hardware fact, not a work item.
