**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The test log is an append log, and it no longer holds the shared tree's advance

*Seat executor, 2026-10-09, drawn item `give-the-test-execution-log-a-reconciler-class-so-it-cannot-hold-the-advance-forever`.
Follows `SEAT_DISPOSITION_THE_TWIN_RULE_WAS_ALREADY_BUILT_AND_THE_FOUR_TWINS_WERE_A_REFUSED_DIRECTION_RECORD_2026-10-09.md`.*

## Premise re-measured

Still live. The shared copy of `docs/observability/test_execution_log.jsonl` had 2,727 lines against
HEAD's 266. Origin's copy had 267: d29dcddc3 (10-08) added the line
`{"timestamp": "2026-10-08T15:57:46...", "test_count": 287}`, which is **not** in the shared copy,
so origin wrote it from another tree. Neither twin class nor the 48 h class can ever take this
path. The duplicate-work claim under the same id was this draw's own write, 27 s old.

## The decision: merge it as an append log

Of the three options in the item:

- **Untrack it and gitignore it.** Rejected. `tools/publish_from_a_clean_tree.py` runs the evidence
  generator in a clean checkout of HEAD, which reads the committed copy. Untracking it breaks that
  publisher. Also, a fast-forward over a deletion of a locally modified file is refused too, so it
  would block the advance once more on the way out.
- **Class it as GENERATED (restore to HEAD).** Rejected. That deletes about 2,460 local run records.
  The generated-path oracles leave appends out on purpose (`WRITING_MODE_CHARS` in
  `tools/file_scope_generated_paths.py`), because an append cannot be re-derived.
- **Merge it as an append log.** Built. Both readers ignore line order:
  `generate_evidence_data.suite_snapshot` takes the max, and `test_execution_metric` sums. So a
  union loses nothing.

`background/origin_reconcile.py` now has an eighth class:

1. `APPEND_LOGS` declares the path by name. It is declared rather than inferred, for the reason
   above.
2. `append_log_verdicts` asks only about the tracked blockers that the stale and generated classes
   left.
3. Under the tree lock, the local bytes are read and committed to
   `refs/preserved/origin-reconcile-append-log/<slug>`. The log is restored to HEAD and the
   fast-forward runs.
4. The file is then rewritten as `merge_append_log(current disk, local)`. That is origin's lines
   plus every local line origin lacks, counted as a multiset. If the advance is refused, or a later
   path fails to clear, the local bytes go back verbatim.

It still clears nothing unless every other blocker clears too, so the all-or-nothing rule is
unchanged.

**One residual window, named:** a pytest line appended between the read and the restore (two
adjacent statements) is lost. A line appended after the restore is kept, because the current
disk is read before the write-back.

## Controls

`tests/background/test_an_append_log_cannot_hold_the_advance_forever.py` has 6 tests, and 5 of
them use real git (a bare origin and two clones). Mutations that each red a test:

- dropping the class from `resolvable`
- writing back HEAD's bytes on a refused advance
- set-merge in place of multiset
- declaring every path an append log
- skipping the write-back on a mid-loop clearing failure

The last of these first stayed green, which meant a test was missing. The missing test was added
and the mutation now reds it.

## What this does not do

It does not advance the shared tree. On 10-09 there were ~19 other blockers, and those age out or
land by their own routes. The new class takes effect once the reconciler daemon runs code that has
it, and that is the same checkout gap this item was about.
