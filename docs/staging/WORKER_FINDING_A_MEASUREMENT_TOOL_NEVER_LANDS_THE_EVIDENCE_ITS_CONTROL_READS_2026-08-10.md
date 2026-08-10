# WORKER FINDING — a measurement tool never lands the evidence its own control reads

**Filed:** 2026-08-10 · **Class:** R15 fail-closed control starved of its input · **Status:** instance FIXED (`c228b48f5`), class OPEN

## The instance (observed-with-evidence)

The publish gate was wedged ~1760 min / 149 consecutive failures naming exactly one test:

```
tests/background/test_publish_gate_subject_is_head.py::test_the_timeout_clears_the_floor_the_measurement_implies
```

Run in the working tree it reports `1 passed`. That is the whole defect's leverage: the
cheapest, most natural diagnostic step **exonerates the real cause**.

Three-row proof (`git archive HEAD | tar -x` extract):

| subject | result |
|---|---|
| working tree | `1 passed` |
| HEAD (`cff7a31a4`) | `1 failed` — *"answers no floor — the bound's evidence is gone"* |
| HEAD + the record file | `30 passed` (whole file) |

Cause: the test reads `docs/observability/publish_gate_subject_cost.json`. That file was
**untracked** — not gitignored (`git check-ignore` rc=1), simply never committed by anything.
`tools/measure_publish_gate_subject_cost.py::_checkpoint()` writes it; no code path lands it.
The gate's subject is a clean HEAD checkout, where the file does not exist, so
`measured_gate_timeout_floor()` returns `None` and the control fails **closed** — correctly,
per R15's "an unavailable check is a FAILED check".

**The control was right. It was starved.** The instance fix landed the evidence
(`c228b48f5`), floor `1291.9s × 2 = 2583 ≤ 2600s`. The control was *not* weakened.

## Why this is a class, not an instance (R10)

An R15 fail-closed control is only as available as its evidence file, and **a tool that
produces evidence for a committed control but has no landing step guarantees this failure**
on any tree where the gate's subject is HEAD. The instance fix does not stop the next
`_checkpoint()` write from re-diverging: the measurement still has `in_tree_baseline` owed,
and when it resumes it will rewrite the record in the working tree only, restoring exactly
the split that caused this wedge — now silently, because the file is tracked and the drift
becomes an uncommitted modification rather than an absent file.

## Proposed class closure (queued per SELF_INTERRUPT_DISCIPLINE, not fixed on sight)

1. **`_checkpoint()` lands its own record** via `tools.surgical_land` (the tree is shared and
   dirty; a bare commit would sweep other lanes). The checkpoint is already "never raises" —
   a failed land must log, not kill a live measurement.
2. **A census control**: enumerate every path read by a fail-closed control at gate time and
   assert each is tracked at HEAD. This is the generalisation that would have caught it
   before the wedge — and it catches the *next* starved control, not just this one.

## Standing lesson

Same family as `feedback_a_control_committed_without_its_mechanism_reds_head`,
`feedback_untracked_build_passes_local_green`,
`feedback_named_blocking_test_passes_when_you_run_it`. The new part: the producing **tool**,
not the builder, is the thing missing the landing step — so no amount of build-time discipline
closes it. Only the tool committing its own output, or a census, does.
