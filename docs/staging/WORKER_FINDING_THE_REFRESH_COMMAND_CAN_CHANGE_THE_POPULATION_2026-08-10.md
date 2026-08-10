# WORKER FINDING — the drain's refresh command re-takes the measurement on a *different population*

**Date:** 2026-08-10 (worker tick) · **Atom:** `H_GAP_fabric_belief_truth_gap` (RUNG 4b, its own drain)
**Class:** a freshness control whose repair action satisfies the control while silently replacing
the quantity it was protecting.
**Status:** OPEN, queued (SELF_INTERRUPT_DISCIPLINE — registered, not fixed on sight).
**Rank requested:** backlog, behind the declared-defect queue. Nothing is wedged by it.

## The finding, observed with evidence

RUNG 4b (`background/supervisor.py::_stale_gap_row_draw`) drew
`W2_11_payment_behaviour_source` as stale and offered
`python3 -m tools.couple_w2_11_d5 --write-ledger`. That command ran rc=0 and the row now reads
CURRENT. The acceptance test the rung states — *"re-run the reconciler and show the row reading
CURRENT"* — passed exactly as designed.

The number moved, and **the population moved with it**:

```
BEFORE   gap 0.0859375              universe_size 1557    truth_size 31
AFTER    gap 0.013094021461420541   universe_size 12000   truth_size 1215
```

The published row was written **in-run by `run_phase2b`**, over the population that run actually
had. `tools/couple_w2_11_d5.py` has its own CLI defaults, and `refresh_command()` emits the **base
invocation and nothing cleverer** — deliberately, and for a good reason it states: inventing
arguments here would be a second, drifting copy of each tool's CLI.

So the re-run did not *re-take* the measurement. It **took a different one** and wrote it to the
same row. Freshness is now genuinely satisfied — the code that produced this number is the code at
HEAD — but a 6.6x move on a public figure is being carried by the ledger as though it were the
same measurement refreshed, and nothing in the reconcile can tell the two apart.

**This is not an argument for reverting the row.** The old figure was produced by code HEAD no
longer contains; it was ungradeable, which is what `stale` means. Both facts are true at once: the
new number is the honest one *and* it is not comparable with what it replaced.

## It self-healed within six minutes, and that is the sharpest part of the finding

The tool wrote at `13:22:40`. At `13:28:30` a live `run_phase2b` re-wrote the same row from its own
run — back to `gap 0.0859375`, `universe_size 1557`, stamped at the current HEAD — and the
reconcile reads clean at 14 of 14. **The committed ledger carries the in-run figure, not the
tool's**, because the in-run writer is the row's real owner and simply reclaimed it.

That is genuinely reassuring for `W2_11` and it is exactly what makes the class worth filing:

- For a row with a **live in-run writer**, the wrong-population window is minutes, and nobody was
  ever going to see it. The control is effectively self-correcting.
- For a row with **no live writer** — every row produced only by a standalone `couple_*` tool run
  on demand — there is no reclaim. Whatever the drain wrote is what the public door carries until
  someone runs something again.

So the exposure is not uniform across the family, and the reconcile cannot distinguish the two
cases. A row that is re-measured by a running process every few minutes and a row that is
re-measured only when a rung draws it are graded by identical logic and reported with identical
confidence.

**Corollary worth checking separately:** if `run_phase2b` owns `W2_11` and rewrites it on every
run, then that row can only ever go stale *between* runs, and RUNG 4b drawing it is arguably wasted
work — the next run clears it regardless. Whether the drain should skip rows with a live in-run
writer is a real question this finding does not answer.

## Why it matters

This is the `one name, two numbers` shape (`feedback_one_name_two_numbers_across_dimensions`)
arriving through a new door — not two dimensions disagreeing, but one dimension disagreeing with
its own past self across a refresh. The reconciler grades **who measured** (which commit) and is
blind to **what was measured over** (which population). A control that verifies provenance and
ignores support will call a replaced quantity a refreshed one every time.

It also touches R14's spirit: the row carries its clock (`run_git_commit`, `measured_at`) but not
its *support*. A figure whose denominator can change by 8x between two readings of the same row
name wants that denominator recorded beside the clock.

## What would close it (not built here)

1. **Record the support in the row.** `universe_size` / `truth_size` already exist inside
   `components` for this metric family but are not part of the reconcile's contract. Promote a
   support descriptor to a first-class ledger field every writer must set.
2. **Have the reconcile report a support change** as its own status — not `stale`, not `current`,
   but *"this row's population moved between measurements"*, which is a fact about the row and
   wants a human reading rather than a silent republish.
3. **Decide, per row, whether the tool's defaults ARE the row's population.** For rows written by
   a standalone `couple_*` tool they are, by construction. For `W2_11`, written in-run, they are
   not, and that mismatch is the whole finding. This is a design question, deliberately not
   guessed here — the same refusal `WORKER_FINDING_DERIVED_ARTEFACT_STALENESS_IS_A_WEDGE_CLASS`
   applied to re-run ownership.

Do **not** close this by pinning arguments into `refresh_command()`. That rebuilds each tool's CLI
in a second place, which is the defect that function's docstring already refuses.

## Evidence

- `docs/observability/coupled_gap_ledger.json` — `W2_11_payment_behaviour_source`, before/after
  values above, taken this tick.
- `background/gap_ledger_reconciler.py::refresh_command` — the base-invocation rule and its reason.
- `background/supervisor.py::_stale_gap_row_draw` — the acceptance test the re-run satisfied.
