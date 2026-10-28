**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The worktree reaper took a queued run's worktree, because a queued launch is not yet its cwd (2026-10-28)

**What happened.** At 06:24:26 the deadman's `WORKTREE REAP (enforce)` removed one worktree:
`/var/tmp/fresh-run-wt-20e7d66234`. That is the gas-leg re-measure's run, which was queued in
`longjob-fresh-run-20e7d66234-queued` behind `head_green_census` for memory. At 06:27:30 the queue
found room and refused: "the workdir ... is not a directory". 1h34m of queue was lost. The run was
not.

**Cause.** `evaluate_worktree_reap` has two liveness legs. One is a writer's claim. The other is a
process whose cwd is in the worktree, added 2026-09-03 after the reaper killed `se-floor-all`. A
queued launch is neither. It waits outside the worktree and names it only as `--workdir <path>`.
The worktree was clean, unlocked, detached on a merged commit and old enough, so it was eligible.
The launcher's refusal already names the workaround ("recreate it (and `git worktree lock` it)").
Nothing makes a queued launch do that.

**Fixed.** `_live_cwd_default` now also counts a live process whose argv names the worktree or a
path inside it, bare or as `--flag=path`. This is the same property shape as the cwd leg: it reads
`/proc`, and it releases when the process exits. Test, red with the leg removed:
`tests/background/test_fork_reconciler.py::test_a_queued_launch_naming_the_worktree_keeps_the_reaper_off_it`.

**Recovered.** The worktree was recreated at 20e7d66234 with `git worktree add --lock`, and the run
was re-queued with its original arguments at about 06:33. Its output directory was empty, so nothing was
mixed.
