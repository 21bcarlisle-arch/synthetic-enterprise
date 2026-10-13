**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-publish-run-of-2026-10-13-reaches-origin` (Lane 0 delivery)

# The run outgrew its fixed two-hour timeout and was killed while writing its report

**Fate (2026-10-13, clear-the-decks):** DONE -- 6f7ec5fb1 Adaptive timeout (twice last success) landed and confirmed in background/sim_runner.py.

*2026-10-13 15:35 BST, delivery seat (executor).*

**What happened.** The 11:24Z run (pid 2607003, `run_output_2248e3baf_20261013T112441Z.json`) did not
die on a None. sim-runner killed it: `Run TIMED OUT after 7200s` at 13:24Z. The simulation itself
finished (`OUTCOME: SURVIVED — full window completed` at 13:16Z, 1h52m in). The kill came about eight
minutes into post-processing, which needs about ten. No JSON was written and nothing was published.
The captured stderr tail is only the pytensor g++ warning. It is not a diagnostic.

**Why.** `background/sim_runner.py` gives the child `subprocess.run(..., timeout=7200)`, a fixed
number. The run's wall time has been rising for days (sim-runner journal, "Run complete"):

| Run | Wall time |
|---|---|
| 2026-10-11, five runs at ed9aa25eb | 4273–4823s |
| 2026-10-12 05:04Z, 47e8e6993 | 4941s |
| 2026-10-12 10:03Z, 47e8e6993 | 5119s |
| 2026-10-13 11:24Z, 2248e3baf | >7200s, killed (needed about 7300s) |

The bound was never derived from the run. It was a constant the run grew into. The state file
recorded `elapsed_s` but overwrote it on every failure, so the last good duration was lost
exactly when it was needed.

**The fix (this commit).** The timeout is now twice the last successful run's wall time
(`last_success_elapsed_s`, which failures carry forward and do not overwrite). It is never less
than the old 7200s, and it is twice 7200s when no success has been recorded. A hang is still
killed, at twice what the run last needed. Repeated timeouts cannot escalate the bound, because
only a success moves it. Control: `tests/background/test_sim_runner_run_budget.py`.

**Why the fix does not save today's publish on its own.** sim-runner imports the shared tree's
on-disk copy. The shared HEAD is 2248e3baf, 53 behind origin, and cannot fast-forward
(`SEAT_FINDING_THE_PUBLISH_IS_HELD_BY_THE_SHARED_TREES_STALE_HEAD_NOT_BY_A_LIVE_RED_2026-10-13.md`).
The landed bound is inert until the shared tree reaches origin and sim-runner restarts. Even a run
that finishes inside the budget then meets the second blocker: the publish-path gate runs against
that same stale HEAD. Two independent blockers sit on one subject, and each hides the other.

**Prediction, filed 14:35Z, before it is observed.** The run in flight (pid 357420, started 13:44:47Z,
`run_output_2248e3baf_20261013T134447Z.json`) is on pace to finish its simulation about 3 minutes
ahead of the killed run. That puts completion at about 7050–7150s against a kill at 7200s (15:44:47Z).
I give it roughly even odds. If it finishes, I predict its publish is refused on the stale-HEAD census
test, as the earlier finding predicted. If it is killed, sim-runner retries on the same code and the
same bound, and every retry is a coin flip until the shared tree advances.

**Outcome:** *(filled in below when observed)*
