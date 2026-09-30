**Severity:** RECORDED · **Lane:** H_harness · **Atom:** `unminted` · **Class:** `controls_that_cannot_fail`

# Two `--pattern` waiters on one subject saw each other, and the C1 bracket's run (c) waited six hours for nothing

**What happened.** Run (b) wrote `/var/tmp/se-c1-bracket-b/value_cycle_ab.json` at 08:41Z. The
wait ahead of (c) (inside unit `longjob-c1-bracket-c-20260928`) and the doorbell's wait both used
`--pattern se-c1-bracket-b/value_cycle_ab.json`. `tools/wait_for.py` struck out only its own
ancestry, so each waiter matched the other and neither could end: the (c) chain ran its full
21600s deadline and (c) started at ~11:59Z instead of ~08:41Z.

**And the late start voided it.** `producing_commit` is bound at import. By 11:59Z fork_salvage
had moved `/var/tmp/se-c1-bracket-src` to `6c34daa36`, so that attempt was stamped `6c34daa36`,
not `fcba478b7` -- void under the prereg. It was stopped 39 minutes in (log kept as
`/var/tmp/longjob-c1-bracket-c-20260928.voided-at-6c34daa36.log`).

**What was done (2026-09-28 12:39Z).** `git diff --name-only fcba478b7 6c34daa36` names only
`docs/` paths. The worktree's dirty `docs/` diff is saved at
`/var/tmp/se-c1-bracket-src-dirty-20260928.patch`. The salvage chain is kept at
`refs/preserved/c1-bracket-src-salvage-20260928`, which contains `994602944`, (b)'s stamp. Then
`checkout --detach fcba478b7`, and (c) relaunched through `background/launch_long_job` as
`longjob-c1-bracket-c-20260928` (main pid 4013250). The doorbell was re-armed with a `--pid` wait on
(c) only, as `longjob-c1-bracket-doorbell-c-20260928`. It overwrites
`SEAT_FINDING_THE_C1_BRACKET_HAS_RETURNED_AND_IS_UNGRADED_2026-09-28.md` when (c) exits.

**The class fix.** `wait_for._is_probe_noise` now treats another Python `-m tools.wait_for`
process as the act of looking, not the subject. A `bash -c` chain that waits and then runs the
subject stays visible, because it becomes the subject. Both legs are tested and both are
mutation-proven: dropping the clause reds the new waiter test, and widening it to any argv that
mentions `tools.wait_for` reds the partner.

**For the grader.** (b)'s `producing_commit` is `994602944`, a docs-only salvage of `fcba478b7`.
Record that as a deviation from the prereg, with the diff as evidence. Do not count it silently.
