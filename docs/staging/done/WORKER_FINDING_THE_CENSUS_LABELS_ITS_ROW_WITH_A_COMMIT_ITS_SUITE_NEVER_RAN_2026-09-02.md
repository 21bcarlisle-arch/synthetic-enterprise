# [WORKER FINDING] The census labels its stored row with a commit its suite never ran

**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Class:** `figures_on_a_superseded_clock`
**Filed:** 2026-09-02, from the delivery seat's Lane 0 item
*"the 830-red second observation must be recordable"*.

Found while establishing that tonight's census could write a complete row. The row can now be
written — and until this commit it would have been written against **the wrong commit**.

## The defect

`tools/head_green_census.py` read `process_run_complete._head_sha()` **twice**, with the entire
unscoped suite in between:

| line | call | what it was for |
|---|---|---|
| 252, in `head_subject_checkout` | `head_sha = prc._head_sha()` | the commit MATERIALISED into the subject checkout |
| 395, in `_record_observation` | `head_sha=prc._head_sha()` | the commit STORED on the observation row |

On this box the gap between those two reads is **just under an hour**, on a tree that five other
lanes land into continuously. Nothing held them together — not a test, not a comment. The row's
`head` field is the key every downstream question is asked against (*is this red new? did the fix
work? which commit do I bisect?*), and this census is the control that certifies every other claim
in the repo.

## Observed live, not argued

Measured against a census that was **still running** while this was written — the honest version of
the evidence, because it could not have been staged:

```
$ ps -o lstart= -p 450950
Wed Sep  2 12:52:44 2026

$ git -C /var/tmp/head-green-census-gt8ng4uv rev-parse HEAD     # the subject it is measuring
f5b19b43f24bc3a92a336970e8628c99416a1184

$ git rev-parse HEAD                                            # the shared tree, same moment
2a84aec8e...
```

**Six commits landed between the two.** That run's suite ran against `f5b19b43f` and had it not
been for this repair its row would have said `2a84aec8e` — a commit against which it did not run a
single test.

> **THEREFORE, FOR WHOEVER GRADES THE NEXT ROW:** the observation written by the run that started
> **2026-09-02 12:52:44** has its subject recorded here and nowhere else. Its true subject is
> **`f5b19b43f`**. That run loaded this module before the repair, so the repair cannot reach it —
> a running process does not re-read its own source. **Do not read that row's `head` field.** The
> repair binds from the next run onward.

## The repair

The sha is read back **out of the subject checkout that was measured**, by
`subject_head_sha(subject)`, and carried to the row on the result. Reading it back from the tree
rather than from the variable that built it means the two cannot disagree by construction, and it
also catches a checkout that materialised something other than what was asked for.

Where a run cannot name its subject — `--from-log`, or an unreadable checkout — the row records
**`None`**, not today's HEAD. That is the same rule the store's first row broke: a plausible sha is
read as established and a `None` cannot be.

Three controls, each mutation-proven (applied, confirmed failing, reverted):

| control | mutation that kills it |
|---|---|
| `test_the_recorded_head_is_the_commit_the_SUITE_RAN_not_the_one_HEAD_reached_afterwards` | restore `prc._head_sha()` in `_record_observation` |
| `test_a_run_that_cannot_name_its_subject_records_no_sha_rather_than_todays` | default `subject_head` to the live HEAD |
| `test_run_suite_actually_fills_in_the_subject_it_measured` | delete the `observed[...]` assignment in `run_suite` |

The first control's fixture builds a subject holding a **deliberately different** sha from the live
tree. A fixture where the two agreed would have passed on the defect — which is the whole reason
this survived: on a quiet tree the two reads return the same string, so the bug is invisible
exactly when nobody is landing anything.

## The control that was itself fail-silent, caught by its own mutation

The third control first read:

```python
if observed.get("subject_head") is None:
    pytest.skip("checkout machinery unavailable on this box")
```

Under the mutation it was written to catch, it **skipped rather than failed** — the value is `None`
both when the box cannot build a checkout and when the assignment has been deleted, and the skip
swallowed the second. Discriminating on the **key's presence** separates them: `run_suite` sets
`subject_head` unconditionally, to `None` when no subject could be built, so a *missing key* means
the wire is cut and a *None value* means the environment is unavailable.

Worth recording because review did not catch it and the mutation did. A control asserted green in
both worlds for the ten minutes between writing it and mutating it.

## What this does and does not change about the 830

Nothing about the count. 830 remains the complete `FAILED` set of the run that finished at 04:30,
as established in
`WORKER_FINDING_THE_830_ROW_WAS_HAND_TRANSCRIBED_FROM_A_RUN_THAT_DID_FINISH_2026-09-02.md`.

What it changes is the meaning of *"a second row at a post-fix head"*, which is the Lane 0 item's
own done-means. Before this repair that phrase was **unverifiable**: the row would have carried a
post-fix sha whether or not the suite had run against one, so the field could not have told the
difference. The done-means was satisfiable by a row that lied. It is now keyed to the property.
