**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# One foreign commit on the ops remote stopped every ops push for 57 hours, and nothing read the failure (2026-11-13)

**What was found.** `background/ops_repo.commit_and_push` committed and then ran a bare
`git push origin main`. It never fetched. On 10 Nov 21:10 the off-box-deadman schedule change
(199bf3f32) was pushed to the ops remote directly. From then on every push was a non-fast-forward.
The local checkout reached ahead 442, behind 1. The sim-runner log holds a heartbeat line every 30
minutes reading "ops repo write failed (CalledProcessError ... push origin main ... exit status 1)".
The last one before the repair was 06:30 UTC 13 Nov. The ntfy mirror, the director input log and
the company-data backup all write through the same function, so all three stopped reaching the
remote together. CLAUDE.md promises that every message is kept in the ops mirror, and the advisor
reads it there.

**What was done.**
1. The live checkout was rebased onto origin under `ops_tree_lock`, then pushed:
   199bf3f32..210bec5cc, 07:16 UTC 13 Nov. There was no overlap, because the foreign commit touches
   only `.github/workflows/off-box-deadman.yml`. Nothing was forced, and the foreign commit is kept.
2. `commit_and_push` now fetches and rebases onto `origin/main` before it pushes. On a conflict it
   aborts the rebase, so the checkout is left usable, and raises a named error.
3. There are two new controls in
   `tests/background/test_the_ops_repo_push_had_no_refusal_at_the_choke_point.py`.
   - One is red on a remote that holds one foreign commit. It also asserts that the foreign commit
     survives, so a force-push cannot pass it.
   - The other is red when a conflicting commit leaves a rebase open.

   Each was seen red before the fix. Deleting the rebase call reds both, and deleting the abort
   reds the second.

**Still open (not corrected).** The failure was logged faithfully for 57 hours. It reached a reader
only because the orientation seat counted log lines. A leg that fails on every cycle has no route
to the director's surface. This is the same class as the launch register's "refused landing
recorded as success" row: a logged failure nobody reads is no log. The daemons also still import
pre-fix code until they restart. Until then the running writer has no rebase, and a second foreign
commit would stop the mirror again.

**The open class is closed, 13 Nov (claim `a-leg-that-fails-every-cycle-reaches-a-reader`).**
`process_run_complete._liveness_leg_reaches_a_reader` now sends both liveness legs, the ops repo
and the public `liveness` branch, through `notify`'s transition contract on every beat. Each leg
has its own key (`liveness_leg:<leg>`) and a state of `refused` or `landed`. A repeated refusal
is suppressed as a page but counted. At `alarm_repetition.ESCALATE_AFTER_REPEATS` (3) it becomes
a `WORKER_FINDING_REPEATING_ALARM_*` in staging, which the draw reads, and the next landing
closes it. Under this rule the 10 Nov failure would have reached staging at its third beat,
about 90 minutes in, not 57 hours later. Control:
`tests/background/test_the_idle_heartbeat_makes_no_commit_on_main.py::test_each_leg_reaches_the_notify_contract_keyed_so_a_repeat_escalates`.
It was seen red with the ops call removed. Still open: the running daemons pick this up only
when they restart, which is the same caveat as above.
