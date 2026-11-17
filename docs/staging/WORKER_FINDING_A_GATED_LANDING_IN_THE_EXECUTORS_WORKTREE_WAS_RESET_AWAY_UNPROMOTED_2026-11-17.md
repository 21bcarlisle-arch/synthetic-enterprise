**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# A gated landing in the executor's worktree was reset away unpromoted, and it cost D5 its fifth landing (2026-11-17)

**What happened.** The seat-executor landed `482e82bf8` at 03:35Z with `surgical_land`: the
commit-gate-hour fix (D5's selection drops from 186 to 177 files, -1477 s). Gate rc 0, and the receipt
verifies. It landed on the **detached HEAD of `/var/tmp/se-seat-executor`**, not on main
(`.git/worktrees/se-seat-executor/logs/HEAD` line 2537). Nothing promoted it. At 03:46:40Z
`fork_salvage` committed `SALVAGE(auto)` on top of it (398358e82f), and the worktree was then reset to
`67ba0b694e`. Neither commit is reachable from any ref; only that reflog still holds them.

D5 attempt 8 (`longjob-d5-land8`) was written on the assumption that the gate-hour landing was on main
("behind the gate-hour landing ... -1477 s off D5's selection"). It ran on a tree without the fix. Its
pytest finished at 04:19:39Z, 25 s inside the 3600 s hook limit, and the hooks after it took the chain
over: `C1 EXIT 1 04:20:10Z`, gate killed. That was the fifth death of the D5 landing, the landing that
is holding the publish wedge (`background/next_book_requires.yaml`).

**Repaired in this tick.** I re-landed `482e82bf8`'s own bytes on main. Its six paths are unchanged on
main since its parent `d67d02a4bc`. D5 attempt 9 follows in the same unit, then the switch-on sha goes
into `next_book_requires.yaml` (`longjob-d5-land9`, log `/var/tmp/d5land9/land.log`).

**Why it will recur.** `surgical_land` prints `landed <sha>` in a worktree exactly as it does on main.
Every reader of that line (a later lane's `run.sh`, the claim note, this draw) takes it to mean "on
main". Promotion is a separate step (`tools/promote_worktree_landing.py`), and a turn that ends between
the landing and the promotion leaves a gated commit that the next `ensure_worktree` reset deletes.

**Recommendation (one leg).** When the root is not the primary worktree, `surgical_land`'s success line
should name where it landed: `landed <sha> IN WORKTREE <path> -- NOT ON MAIN until promote_worktree_landing`.
Alternatively, the executor's reset should refuse, and run the promotion instead, when HEAD carries a
surgical-land receipt that origin/main does not contain. The second leg prevents the loss. The first
only stops the misreading. I recommend the second.

**Reverse:** archive this file.

## A second instance, four hours later (worker, 17 Nov ~08:00Z)

The executor landed `cffc748d4` at 07:36:57Z in `/var/tmp/se-seat-executor`: the director's
cost-per-result steer, 9 paths, gate rc 0. Its later promote run (`/var/tmp/cpr/c3m.log`) promoted
`7ef606c3e`, a different landing, with "0 path(s)". `cffc748d4` was on no ref by 07:57Z, and the
worktree was back at `7ef606c3e2`. A worker draw at 07:56 still listed the steer as unactioned, and
so did the executor's own draw. Both would have rebuilt it, and one parallel build had already been
stood down earlier for it (c2f7b9a46).

Repaired: merged unchanged as `db81ccba95` (`surgical_land --merge cffc748d41`; none of its paths
had moved since its parent) and pushed.

Two instances in one morning: it stays LATENT, because nothing published or gated is invalidated, but it is now a pattern, not a one-off. The second leg
recommended above (refuse the reset, and promote, when HEAD carries a surgical-land receipt that
origin/main lacks) would have kept both landings.
