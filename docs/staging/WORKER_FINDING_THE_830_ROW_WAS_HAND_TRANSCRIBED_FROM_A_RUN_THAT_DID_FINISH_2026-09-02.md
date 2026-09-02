# [WORKER FINDING] The 830 row was hand-transcribed from a run that DID finish, and only its pass count was lost

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`
**Filed:** 2026-09-02, from the delivery seat's Lane 0 item
*"the 830-red second observation must be recordable"*.

`docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_TMPFS_DIAGNOSIS_EXPLAINS_THE_830_RED_2026-09-02.md`
left this open and named three possible answers: the run was **truncated**, **killed**, or the
store was **seeded by hand**. It is the third, and the reason matters more than the label, because
the second reading — a partial run — is what forced 830 to be treated as a floor of unknown depth
for a day.

## The evidence

`journalctl --user -u head-green-census.service`, 2026-09-02:

```
Sep 02 03:31:04  Starting head-green-census.service …
Sep 02 04:30:02  NEW_RED: 830 test(s) newly failing: … [causes: OSError x760, AssertionError x33, …]
Sep 02 04:30:02  head-green-census.service: Main process exited, code=exited, status=1/FAILURE
Sep 02 04:30:02  Consumed 59min 30.834s CPU … 58min 57.803s wall clock, 5.3G memory peak
```

**The run finished.** `status=1` is `main()`'s own return value for `NEW_RED`, and `verdict()`
cannot return `NEW_RED` unless `parse_passed_count` returned an integer. The run therefore *had* a
pass count and printed a complete verdict. It was neither truncated nor killed.

**It was not that run that wrote the row.** Two independent tells:

1. **The wording.** The journal says `830 test(s) newly failing`. That is the phrasing
   `bc57c8e30` replaced *because it was false* — so the process that ran at 04:30 was executing
   pre-register code, in which `head_red_register` did not exist and `_record_observation` was
   never called. It wrote no row and could not have.
2. **The clock.** The journal is local (BST): the run finished 04:30:02 BST = **03:30:02 UTC**.
   The stored row is stamped `2026-09-02T04:30:02+00:00` — 05:30:02 BST, **one hour later**, with
   the minutes and seconds identical. `_now_iso` uses `datetime.now(timezone.utc)`; a machine call
   an hour later would not land on the same minute and second. The stamp was transcribed from the
   journal line and labelled UTC.

## And the part that is better than the pre-registration assumed

The transcription is **complete**. Every `NEW RED` node id in the journal against every key in the
store:

```
journal NEW RED node ids : 830
store tests              : 830
in journal not in store  : 0
in store not in journal  : 0
```

So 830 is **the complete `FAILED` set of a run that finished**, hand-copied, with exactly one field
dropped. It is not a partial count. **This refutes the pre-registration's stated reason for calling
it a floor**, and that correction is written beside the claim in the prereg itself.

One narrower caveat survives and is not the same thing: `parse_failures` reads only `FAILED` lines,
so any test reported as a collection/setup `ERROR` is outside the count. Whether the 04:30 run
emitted `ERROR` lines is **not establishable** — the journal holds the census's own printout, not
raw pytest output. That caveat applies identically to every run, so run 1 against run 2 is still a
like-for-like comparison; it bounds the absolute number, not the delta.

## What it cost, and the repair

The cost was a day of the director's question. A count that cannot be told apart from a partial one
has to be graded as a floor, and every clause of the prereg was weakened to match.

`record()` now **refuses a run row with no pass count**, naming its reason. The argument is that
`verdict()` calls a run UNPROVEN exactly when `passed` is `None` or zero, and `_record_observation`
— the only sanctioned caller — turns UNPROVEN away; so `passed is None` arriving at `record` means
the row is not a census observation at all, whatever the store's `_doc` claims about being
machine-written. **The refusal is unreachable from the nightly path on purpose. Its subject is the
other way a row can arrive, which is the way the only row here did arrive.**

The register also stops calling a missing count `unreadable`. That word says the machine tried to
parse a summary and failed; the truth is that no completed run wrote the row, and a reader
comparing two runs needs that distinction to know whether the earlier count is comparable at all.

Three controls, each mutation-proven (mutation applied, confirmed failing, reverted):

| control | mutation that kills it |
|---|---|
| `test_a_run_row_with_no_pass_count_is_refused_because_no_completed_census_can_produce_one` | drop the guard in `record` |
| `test_a_completed_runs_pass_count_reaches_the_stored_row` | row takes `len(failing)` instead of the run's count |
| `test_a_missing_pass_count_is_never_called_unreadable` | restore the `unreadable` label |

The positive leg reads end-to-end from a pytest log through `evaluate` into `record`, not by handing
`record` a number: the chain is where the count was lost, so asserting on `record` alone would have
passed on the defect.

## What is now known about tonight's run

Measured, not argued — `evaluate()` on a realistic completed-run log
(830 `FAILED` lines, 760 `OSError` traceback lines, `830 failed, 23456 passed, 12 skipped in
3537.02s`):

```
status = NEW_RED | passed = 23456 | red = 830
row     = {'head': 'deadbeef', 'red': 830, 'passed': 23456}
```

The write path is sound: a run that finishes tonight lands a row with `passed` populated. The
remaining risk is not the store — it is whether the run finishes at all, which
`SUITE_TIMEOUT_SECONDS = 7200` against a worst observed 3537 s now covers.

**Not run by hand today, deliberately.** `pgrep -af process_run_complete` showed PID 415986 live on
a full-suite publish run at the start of this turn; a second heavy suite beside it would have
manufactured the failure being measured. The census fires on its own at 2026-09-03 03:34 BST.

## The residual reds already have their route

Verified live rather than rebuilt — `bc57c8e30` built this and it works:

```
$ python3 -m background.head_red_register
HEAD-RED: 830 owed, 0 accepted by name        (rc=1)
$ reg.drawable() -> 830
```

`staging_rooms._with_the_head_red_register` splices the register into `work_queue()` at rank 37
while `drawable()` is non-empty, so all 830 — including the ~10 non-environmental ones tmpfs never
explained — are in the draw now. What run 2 changes is the SIZE of that set, not whether it has a
route.

## Owed next

Grading the prereg clause by clause against run 2. That cannot be done before the run exists: C1,
C2, C3, C4 and C6 all read run 2's numbers. **C5 is the one clause this finding bears on, and it is
now a live control rather than a hope** — if tonight's row comes back `null` again, `record` will
have refused it and said why, instead of writing a row nobody can grade.
