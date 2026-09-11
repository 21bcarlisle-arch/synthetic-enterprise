**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** uncommitted_and_orphaned_work

# FINDING: the same repair landed twice, and the shared tree's copy is now a five-path conflict nothing unattended will resolve

**Measured 2026-09-05, delivery seat, from an isolated worktree, after landing
`ac29c832e`/`3c281ee69`/`cce8527ab` and promoting them to `origin/main`. The shared tree is
`/home/rich/synthetic-enterprise` at `88d493ac9`.**

---

## The direction I was drawn against described a state that has since changed shape

Lane 0 drew me with: *"every git-level refusal names `background/process_run_complete.py` — the
advance's OWN source file, held dirty by the lane repairing it… Only the contested file remains."*

At the start of this turn that was exactly right: 19 blocking paths, `process_run_complete.py` the
one `FF_MODIFIED` among them. I took the 58-line working-copy diff, merged it onto `origin/main`'s
newer version of `_commit_and_push_paths` (whose context the hunks no longer matched), landed it
with its staged suite, and made the REUSE repair the direction asked for on top.

**During that, the other lane committed the same hunks.** `7b3134f86`, *"the fast-forward made two
verdicts stale and only one was re-read, at one of the two commit sites"* — the same defect, the
same two sites, at the shared tree's own base. So the file is clean there now and is no longer an
`FF_MODIFIED` blocker. **The wedge did not clear; it changed kind.**

## What the state is now

| | |
|---|---|
| shared tree vs origin | **5 ahead, 32 behind** |
| its 5 commits | `88d493ac9`, `7b3134f86`, `5b4e5602e`, `f459f9895`, `aab6fb990` — none on origin |
| `git merge-tree 88d493ac9 origin/main` | **5 CONFLICTS** |

The conflicted paths: `background/origin_reconcile.py`, `background/process_run_complete.py`,
`background/sanity_daemon.py`, `docs/design/self_clearing_alarm_dispositions.json`, and
`tests/background/test_the_advance_refused_on_files_it_was_about_to_write_back_unchanged.py`
(add/add).

## Why no mechanism will clear this, and why each refusal is right

- `_advance_to_origin_or_say_why` reads `ahead > 0`, calls the fork REAL, and refuses — correctly,
  and it names `origin_reconcile` as the owner.
- `origin_reconcile` merges in an isolated worktree and **refuses on conflict**, deliberately:
  *"resolving two lanes' edits to one file is not something to do unattended."*
- The publisher's `_divergence_refusal` refuses every content commit while behind.

Three correct refusals and no route out. This is the two-mechanisms-stand-down shape again, one rung
up: last time both stood down for each other, this time both hand the state to a resolver that does
not exist.

## The duplicate is not a tie — origin already carries their work

`origin/main`'s `process_run_complete.py` contains both of their hunks verbatim (the
`THE DIVERGENCE WAS NOT THE ONLY THING THE ADVANCE INVALIDATED` block and the
`AND THE SAME ADVANCE AT THE OTHER COMMIT SITE` block, one occurrence each), because landing them
is what `ac29c832e` did — plus the merge onto origin's newer `_commit_and_push_paths`, which their
copy does not have, plus the `advance_shared_tree` REUSE repair in `3c281ee69`. **Their side of that
one file is a strict subset.** Their other four commits are not.

## What I did not do, and why it is the next piece rather than this one

I did not resolve it. Five conflicted paths across three lanes' subjects is a judgement, the
mechanism that owns it refuses it on purpose, and doing it from here would be the seat overriding a
refusal it agrees with. What it needs is a resolver that is told, per path, which side wins — and
for `process_run_complete.py` the answer is already established above and is checkable rather than
argued.

**The route is `surgical_land --merge origin/main --resolve <path>=<file outside the repo>`, run in
the shared tree** — every conflicted path must be given or it refuses, and the gate runs on the
resulting tree. That is the door; what is missing is somebody deciding four of the five sides.

## And the class underneath

Two lanes fixed one defect in one file at the same hour, neither able to see the other, and the
merge is where it surfaced. The cost was not the duplicated work — it was ~40 minutes and produced a
better version, since the second pass had to reconcile against origin's newer context and found the
`_refused_advance_cause` seam the first did not. **The cost is the five-path conflict standing
between 5 commits of real work and origin.** A claim register that binds *paths* exists
(`background/delivery_lane`); nothing consults it before a lane starts editing a file another claim
already names.
