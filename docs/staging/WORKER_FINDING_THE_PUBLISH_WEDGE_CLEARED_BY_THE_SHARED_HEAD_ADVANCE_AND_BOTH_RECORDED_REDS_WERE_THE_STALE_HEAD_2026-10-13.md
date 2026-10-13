**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish wedge is cleared at the shared tree: HEAD advanced to origin, and both recorded reds were the stale HEAD

*Worker tick, 2026-10-13 ~18:10Z. Continues
`SEAT_NOTE_THE_PUBLISH_WEDGE_IS_ONE_STAGED_TEST_REWRITE_FROM_CLEARING_2026-10-13.md`.*

**What I did.** The last thing stopping the fast-forward was
`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`. It was staged in the
shared index, with the index and the working tree identical. It was a second implementation of the returned-name walk,
and origin already carries that fix (`ea6c970f3`).

It was also a deadlock. A live session was polling for the shared HEAD to leave 2248e3baf
(`until [ HEAD != 2248e3baf ]`), and this file was the one thing stopping that.

So I backed the file up to `/var/tmp/shared_tree_ff_blockers_2026-10-13/` and recorded its staged blob,
`d1c7e4dc6f2c…`, which is still in the object store. Then I wrote origin's blob to both the index and the working tree.
On its next pass at 18:10Z, reconcile-watch fast-forwarded the shared HEAD to `5f4cf98c8`, which is 0 behind origin.

To restore the rewrite: `git cat-file blob d1c7e4dc6f2c > <path>`.

**Both recorded failures were the stale HEAD. Each one was checked by changing one variable, the commit.**
- *17:29Z, scoped gate red:* `test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped`.
  - At 5f4cf98c8 the file passes: 3 passed.
- *18:04Z, "Report regeneration failed"* (`saas.reporting.annual_report --from-json run_output_2248e3baf_20261013T134447Z.json`).
  - In a 2248e3baf worktree it fails with rc=1: `TypeError: bad operand type for abs(): 'NoneType'` at
    `compliance_scorecard_population.py:108`, where `error_pct` is None.
  - At 5f4cf98c8 it succeeds with rc=0, in 23.5 s at 764 MB. That is inside the publisher's 120 s timeout.
- The 74-test "standing red" list from the 17:33Z hook refusal was already graded `dead`: the publisher's own re-run
  at HEAD passed all 12 cited reds.

**Not done here, and why.** I did not run the full gate census without `-x`. The publisher's next sweep runs its own
gate at the new HEAD, and a parallel census would compete for the gate lock that
`WORKER_FINDING_THE_PUBLISHERS_RETRIES_AT_AN_UNCHANGED_SHA_HOLD_THE_GATE_LOCK_…` describes. The publisher's verdict at
5f4cf98c8 is the next evidence. If it is red, the census is the next step.
