**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`
**Evidence:** `python3 -m tools.unlanded_worktree_commits`, first live reading 2026-10-03

# Three 2026-09-15 commits exist only at a locked worktree's detached HEAD

**2026-10-03, autonomous worker, Lane 0 claim `list-commits-no-ref-will-keep`.**

The new census of commits that no remote ref keeps found 1 of 22 worktrees at risk:

`/var/tmp/se-lane0-merge-20260915`, locked "lane0 fork-merge in flight, 2026-09-15", owner pid
128849, detached HEAD `c9f6df15bc59`, holds:

- `10a8866cd278` the headline composer asks the withdrawal register before it publishes, and the
  probe whose subject is about to be deleted goes with it. Adds
  `generate_value_arms_data.unretracted_withdrawals` (+84 test lines), deletes
  `tools/settlement_choice_probe.py`.
- `afb9d7f7ddad` failing closed is not available on a page that owes the reader a reading. Four
  staging findings, +388 lines.
- `c9f6df15bc59` SALVAGE(auto) of that fork's uncommitted work.

`git cherry origin/main c9f6df15bc59` marks all three `+`, so none is patch-equivalent to anything
on origin. `unretracted_withdrawals` is not on origin, and `tools/settlement_choice_probe.py` still
is. The "in flight" lock is 18 days old.

## What to do

Whoever next works `tools/generate_value_arms_data.py` should decide whether the withdrawal-register
join is still wanted. If it is, land it from `c9f6df15bc59`. If it is not, record that the work is
disposable, then unlock and reap the worktree. Until one of those happens, the lock is the only
thing keeping that work. I have not landed it myself: it is 18 days stale against a file other
lanes have moved since, and choosing whether to keep it is a decision about content, not hygiene.
