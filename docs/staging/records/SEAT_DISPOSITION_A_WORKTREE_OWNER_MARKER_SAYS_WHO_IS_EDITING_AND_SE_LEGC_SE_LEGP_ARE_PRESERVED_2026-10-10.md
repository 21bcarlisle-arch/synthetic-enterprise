# Disposition: who restamped ~105 owner markers; the draw now asks for editing, not a lease; se-legC and se-legP preserved and removed

*Delivery item `a-worktree-owner-marker-says-who-is-editing`, 2026-10-10.*

**What wrote `2197437` into ~105 markers.** None of the four candidate daemons. `delivery_seat.py`,
`seat_executor.py` and `origin_reconcile.py` all write `os.getpid()`, which is a Python pid, and
2197437 is a `claude` process: the worker seat started under systemd on 2026-09-25 (session
`22080be5-…`). That session wrote its own pid into every worktree it cut (`echo 2197437 >
…/.se_worktree_owner`, about 105 of them since 09-25). It then started a scratchpad loop,
`renew_claims.sh` (pid 177330), which `touch`es every marker naming 2197437 every 600 s for as
long as the session lives. It did this to follow the memory rule "an ownership marker is a LEASE,
renew it under long agent builds". So the restamps "in one pass" are not a single event. They
recur every ten minutes; 104 markers carried 23:18:23–24 BST when this was read. The renewer was
**left running**: the session is still working in three of those worktrees, and fork_salvage's
lease is the thing it protects.

**The draw's refusal now needs evidence of editing.** `delivery_lane._live_holders` used to take a
fresh marker naming a live pid as a holder. It now asks `editing_now`, where any one of three legs
holds:
1. a live process whose cwd is inside the worktree (`/proc/*/cwd`);
2. a write to the diff inside the lane's own claim window (`CLAIM_STALE_SECONDS`, 100 min);
3. a diff whose digest (each held path's mtime and size; the marker excluded) differs from the
   digest recorded at that worktree's previous held-work refusal (`record_held_refusals` now writes
   `diff_digest`).

Measured on the box at 23:2x BST, the same probe before and after: **105 marker-live worktree
holders became 3**: `/var/tmp/se-follow`, `se-save-live` and `se-seat-executor`, each with a live
pid inside. The two running long jobs are unaffected.

Leg 2 is beyond the item's own two legs, and it was added on purpose. `draw(claim=False)`, the
watchdog's read, also records refusals. Without leg 2, a watchdog read minutes after a real edit
would record its digest, and the next real draw would release the item from under the editor.

**Control:** `tests/background/test_a_restamped_owner_marker_on_an_untouched_draft_holds_nothing.py`.
A real git fixture has a fresh live marker and a week-old diff. With no process inside, it does not
refuse. With a `sleep` running inside it, it does. Five mutations were run, and each went red: the
process leg removed, the window leg removed, the changed-since-refusal leg removed, `editing_now`
made unconditional (the old behaviour), and the digest dropped from the refusal record.

**se-legC and se-legP.** Both were locked detached worktrees owned by 2197437, at `e0370bf94` and
`c2ba8649c`. Each had the same 8 dirty paths, with newest content written 2026-10-03 (code at
03:42, run outputs by 15:15). Nothing was running in either. The only code change was
`tools/run_value_cycle_ab.py`, byte-identical in both (blob `a621dbbb8`): the per-renewal list, the
`svt_segment_decisions` count and `RENEWAL_BELIEF_FIELDS`. **Every added line is on origin/main**,
where the file was last touched at `cfd8ae74d`. The other paths are run outputs: the handshake,
`coupled_gap_ledger.json`, `fidelity_evidence_ledger.json`, `token-log.md` and the two untracked
`book_*` JSONs. Each working state, untracked files included and the marker excluded, was
snapshotted onto its base as **`refs/preserved/se-legC-2026-10-03`** (`02e65a30b`) and
**`refs/preserved/se-legP-2026-10-03`** (`4fe26ffda`). The untracked JSONs were checked
byte-equal. Both worktrees were then unlocked and removed. Nothing was landed, because nothing
was novel.

**To reverse:** `git worktree add /var/tmp/se-legC refs/preserved/se-legC-2026-10-03 && git -C
/var/tmp/se-legC reset --soft HEAD~1` (likewise for legP).

**7379375f6 is reachable from a remote ref.** It is one commit, a 23-line staging finding, on
`abb925ec7`, which is on origin. It was pushed as **`origin/preserved/single-levy-run-7379375f6`**,
so Monday's publish can cite it as `producing_commit`. To reverse: `git push origin
:refs/heads/preserved/single-levy-run-7379375f6`.
