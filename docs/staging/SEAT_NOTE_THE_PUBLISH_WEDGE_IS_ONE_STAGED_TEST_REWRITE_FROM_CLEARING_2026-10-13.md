**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The publish wedge is now one staged test rewrite away from clearing

*Worker tick, 2026-10-13 ~18:05Z. Doorbell: publish gate red ~406 min, scoped gate at graded_sha=2248e3baf names
`test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py::test_the_census_selects_enough_logs_to_be_capable_of_finding_one_dropped`.*

**Diagnosis. This is not a live red, and it was already on record.** It is the same cause as
`SEAT_FINDING_THE_PUBLISH_IS_HELD_BY_THE_SHARED_TREES_STALE_HEAD_NOT_BY_A_LIVE_RED_2026-10-13.md`. The publisher grades a
checkout of the shared tree's HEAD, which is 2248e3baf (73 behind origin). That HEAD lacks 81c129fe8's repair of the
returned-name walk. Re-measured at origin b47a3de53, in a clean worktree: 3 passed. The scoped gate named exactly
one red, so there is no hidden second red behind it at the depth that gate reaches.

**Done (shared tree, no commit needed).** `paths_blocking_fast_forward` listed 7 paths. I re-hashed each against origin:
- 4 were already byte-identical twins.
- The two ADVISOR_FINDINGS archive moves were deleted at the root, with 13-hour-old `done/` copies. Origin ruled both
  ATOM and holds a superset; the only line missing from origin is one auto-applied header that origin replaced. I wrote
  origin's bytes back at the root and removed the `done/` copies. They are now twins.
- The untracked `SEAT_FINDING_THE_SHARED_TREE_IS_HELD_…` copy held 0 lines origin lacks, so I wrote origin's bytes over it.
  It is now a twin.

Backups of every overwritten or removed copy are in `/var/tmp/shared_tree_ff_blockers_2026-10-13/`.

**The one remaining blocker, left alone:**
`tests/saas/reporting/test_a_log_the_run_makes_and_a_section_reads_survives_the_reduction.py`. It is staged in the
shared index, written 17:49Z, ten minutes before this tick, and it is a second implementation of the fix origin
already carries. That is live work in another lane, most likely the console seat's landing sequence, so this tick did
not move it. Its owner can clear the wedge in one step: unstage it and take origin's blob, or land it onto origin.
After that the reconciler clears the six twins, the shared HEAD fast-forwards, and the queued `run_complete` publishes.
