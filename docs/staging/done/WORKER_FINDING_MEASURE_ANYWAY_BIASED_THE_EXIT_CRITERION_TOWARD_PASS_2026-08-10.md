# [WORKER-FINDING] "Measure anyway" biased the exit criterion toward PASS (2026-08-10)

**Atom:** `OPS2_publish_gate_head_worktree` (exit criterion 1 — the warm/in-tree ratio)
**Status:** CLOSED by this commit. Filed in `done/` because it was found and fixed in one tick.
**Class:** R15 FAIL-OPEN — a guard whose degraded mode moves the measured verdict in the
passing direction.

## Observed, with evidence

`tools/measure_publish_gate_subject_cost.py` had two bounded admission guards —
`_wait_for_quiet` (no live publisher) and `_wait_for_memory_headroom` (≥4096MB free). Both fell
through on timeout to *"measuring anyway, flagged contended"*, justified in the source as
*"a harness that can hang forever is worse than a noisy number that is labelled noisy."*

That trade was wrong, twice, and in two different ways.

**1. It does not produce a noisy number. It produces NO number.** — *observed*

```
$ systemctl --user status publish-gate-subject-cost.service
     Active: failed (Result: oom-kill) since Mon 2026-08-10 19:25:11 BST
   Duration: 1h 36min 41.358s      Mem peak: 11.1G (swap: 669.2M)

Aug 10 18:25:58  [measure] phase 3/3 BASELINE -- the live working tree, the pre-ruling subject
Aug 10 18:25:58  [measure]   . waiting for the live publisher to finish before timing
Aug 10 19:25:11  publish-gate-subject-cost.service: The kernel OOM killer killed some processes
```

The quiet-wait timed out at ~19:11 (`QUIET_WAIT_SECONDS` = 2700s from 18:25:58), started the
baseline suite beside a live publisher, and was OOM-killed 14 minutes in. Two full suites do not
fit in this box's 15.9G. The previous launch died identically in the WARM phase at 13:55:30Z
(6.5G peak). Cost: two ~1h36m launches, and `in_tree_baseline` is still owed.

**2. When it does NOT kill the run, it biases the exit criterion toward MEETS.** — *inferred
from the arithmetic, and this is the half that matters more.*

The criterion is `warm / in_tree <= 1.3`. The phase that keeps losing the race for the box is
`in_tree_baseline` — **the denominator**. A baseline timed against a live publisher runs slow,
which makes the ratio **smaller**, which makes the criterion likelier to read MEETS. And it
would have done so silently: `box_was_quiet: false` sits inside a phase record, while
`meets_exit_criterion` is the field anyone actually reads.

So the surviving path produces a number that is wrong *in the direction of passing the atom's
own exit test*. That is the fail-open shape R15 names, sitting inside the harness that certifies
an exit criterion.

## The fix

The timeout **defers** instead. Both guards raise `_Deferred`; `_run_measurement` catches it,
banks the phases already measured, records `deferred{reason, at_phase, at}`, and returns **0**
(a deferral is a correct outcome — a non-zero exit would make the systemd unit report `failed`
for a run that did the right thing).

This costs nothing that dying did not already cost: phases were **already resumable**, so
exiting cleanly loses exactly what the OOM lost, minus the OOM and minus the false number. The
next launch resumes from the banked phases.

**The invariant it buys:** `box_was_quiet` / `had_memory_headroom` are now invariantly true on
any banked phase. They stop being a caveat attached to a number that gets used anyway and become
a property the record is checked against.

**The risk it takes on, made visible rather than argued away:** a box that is never quiet long
enough would now never converge. `deferral_count` accumulates across launches, so that shows up
as a rising number in the artefact instead of a measurement that silently never lands.

## R15 both ways — mutations run, not asserted

| Mutation | Result |
|---|---|
| `_wait_for_quiet` returns `False` instead of raising (the old behaviour) | **2 failed** |
| `_wait_for_memory_headroom` returns `False` instead of raising | **2 failed** |
| `_prior_deferral_count` returns 0 unconditionally | **1 failed** |
| `except _Deferred` no longer catches the deferral | **2 failed** |
| unmutated | **45 passed** |

Both directions are covered: `test_both_guards_pass_through_when_the_box_is_actually_fit` pins
that a fit box is admitted, so the guards cannot degenerate into controls that only refuse.

## The superseded test is kept, not deleted

`test_a_starved_box_is_measured_anyway_and_flagged` asserted `is False` — it *pinned the
defect*. It is renamed `test_a_starved_box_is_deferred_not_measured_anyway` and keeps the old
subject in its docstring, so the contract change is legible rather than silently dropped. (A
green test can pin a defect; this is one that did.)

## What is still owed on the atom

`in_tree_baseline` — the ratio cannot be computed without it, so exit criterion 1 remains
**unmet and unclaimed**. Criterion 2's `GATE_SUITE_TIMEOUT_SECONDS` re-derivation depends on the
same measurement. `level_current` stays **0**; nothing here promotes it.

— worker tick, 2026-08-10
