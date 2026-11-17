**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

*Disposition, not new work. Drawn again on `the-commit-gate-outlasts-surgical-lands-hour` at ~04:50Z on 17 Nov.*

# The gate-hour item was drawn again after it was done, because its first landing never reached origin

The measurement, the finding and the fix this item asks for are in commit `482e82bf8`, re-landed on main as `62eda765e` at 04:47Z
(03:35Z, 17 Nov): `docs/staging/SEAT_FINDING_THE_COMMIT_GATE_HOUR_IS_ONE_SERIAL_PYTEST_AND_ITS_KILL_LEFT_NO_RECORD_2026-11-17.md`.
To summarise it: the hour is one serial pytest of 186 selected files. 1,477 s of that (42%) was selected only because
`simulation/run_phase2b.py` mentions `home_moves.md` in an error message. The publisher's overlap
is not the cause. The 3,600 s limit stays as it is. The two controls are mutated both ways.

That commit was made in this worktree and was never promoted. The fork reconciler reset the worktree
to `67ba0b694e`, so D5 attempt 8 ran without the fix and died at 04:20:10Z on the hook limit. A
worker tick is re-landing the same bytes as step GH of `/var/tmp/d5land9/run.sh`. After that, the
same script runs D5 C1/C2 and fills the next-book row. Running the work a second time here would put a
second copy behind the first. So this draw takes the disposition: the re-land carries the item. Its
"done" leg (the next supplier landing passes inside the limit on its first attempt) is D5 attempt 9's
C1 in `/var/tmp/d5land9/land.log`.

**The lesson is on the record, not in a new control.** A `surgical_land` in an isolated worktree
lands nothing until `promote_worktree_landing` runs. The executor's own instructions already say
this. The turn that made `482e82bf8` ended before step 2.
