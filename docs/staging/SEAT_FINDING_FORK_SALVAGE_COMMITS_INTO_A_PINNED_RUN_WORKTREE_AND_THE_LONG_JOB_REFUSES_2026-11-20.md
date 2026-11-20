**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# fork_salvage commits into a pinned run worktree, so the run's own pin check refuses it (2026-11-20)

**What happened.** The §12f replication (`THE_VALUE_TEST_REDESIGN.md`) runs from `/var/tmp/value-test-cut012`.
That tree is `870201d1e7` plus an uncommitted port, and its driver refuses to run unless
`git diff --binary 870201d1e7 -- <code dirs>` hashes to a pin (`2b312c4d…114d`). At 11:35:40Z, from
`worker-tick.service`'s ExecStopPost, `background/fork_salvage.py` committed the port as `SALVAGE(auto)`
(`3d276fa874`). The commit took in the `sim/cache` symlink, which had been untracked, so the diff now
carried a fourth file. At 11:41:33Z, `longjob-value-test-cut012-rep` refused in 60 ms: "REFUSED: the tree's
diff from 870201d1e7 is f2c41ffc…, pinned 2b312c4d…; nothing run". Exit 5. The replication had been
recorded as launched, and it had not run.

The same tree had been deleted once before, on 18 Nov (§12f's skip1 entry). Scratch run worktrees are
exposed to both daemons, and the only protection on offer is an owner marker whose lease is far shorter
than a 23 h job.

**Repaired.** At 12:05Z I ran `git reset 870201d1e7` (mixed: HEAD moved, working tree untouched). With
that, the diff equals the pin again, and the tree is `git worktree lock`ed. The re-armed watcher
(`/var/tmp/box-plan/arm_cut012_rep.sh`) repeats that repair before it launches. It only does so if the
diff without `sim/cache` still equals the pin. Otherwise it gives up and names the reason.

**Why it will recur.** `fork_salvage.scan_worktrees` skips only the main worktree, protected branches,
bare trees and worktrees with a live owner marker. It does not read the `locked` line that
`git worktree list --porcelain` emits. A lock is the one marker git itself offers to say "leave this
tree alone", and both scratch trees on this value test were locked for exactly that reason.

**Recommendation (one leg).** In `scan_worktrees`, skip any worktree whose porcelain record carries
`locked`, and print its lock reason in the sweep log. To show the guard can be taken, its test asserts
that a locked, dirty, detached worktree is skipped while an unlocked one beside it is salvaged.

**Fixed, ec432f21a (on origin, 20 Nov).** `scan_worktrees` reads the porcelain `locked` line. `salvage_all`
reports every locked tree as `SKIPPED_LOCKED`, whether or not it is dirty, and the sweep log prints one
`SKIPPED <path> (locked: <reason>)` line for each. `tests/background/test_fork_salvage_never_commits_into_a_locked_worktree.py`
builds a locked, detached, dirty tree and an unlocked twin beside it. The locked tree's HEAD, diff and
status come out byte-identical, and the twin is salvaged. With the guard removed, both tests go red. The
`wrong` row about salvaging into a pinned tree (DIRECTION.yaml) can now be marked corrected. That file
belongs to the seat, so I have left it alone.

**Open, not yet established.** At the time of the fix, 0 of the ~200 registered worktrees are
`.claude/worktrees/agent-*`, so this does not show whether Claude Code locks its own agent forks. If it
does, this guard also skips the trees salvage exists for. The first sweep log that names an `agent-*`
tree as `SKIPPED` would show this. The remedy would be to skip only locks whose reason is not the
harness's own.
