**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — the publisher has never recorded a clean publish in this episode)

# The publish reached origin after 146 hours, and the cause was a stale working copy of the publisher itself

**2026-09-16, scheduled tick, worker seat.** The public surface is live again. The run
`run_output_770497ddd_20260916T125142Z.json` — 226 accounts, 9,996 bills, net £163,302 — is on
`origin/main`, carried there by publish commit `05add41ab`, which `git merge-base --is-ancestor`
confirms is an ancestor of `origin/main`. `docs/status/LATEST.md` on origin is stamped
2026-09-16T13:28:42Z. The wedge stood 145.8 hours.

The counter the item set as its exit test, `episode_clean_publishes`, is **still 0**. That is not a
softening and not a miss — it is a second, separate defect, and it is filed beside this as
`WORKER_FINDING_THE_PUBLISH_SUCCEEDS_BY_REACHABILITY_AND_IS_GRADED_BY_EQUALITY_2026-09-16`.

## The premise was spent, and the real cause was in the tree, not in git

The item cited four commits and predicted `behind_origin` "cannot fire". At turn start HEAD and
`origin/main` were both `c4809c5fc` — level, exactly as predicted. Then the live cycle refused
`behind_origin` anyway, at 13:27 UTC, because origin had moved 4 commits underneath it during the
23-minute cycle. The prediction was true when written and false when it mattered; origin here
moves about every four minutes.

But `behind_origin` should no longer have been fatal. `770497ddd` (13:33) had landed
`_publish_surface_collisions`: *ahead > 0 is a state, not a collision* — a publish commit whose
paths are disjoint from what origin is bringing can be committed and absorbed by the reconciler.

**It was not in force.** `background/process_run_complete.py` in the shared tree had mtime
**11:27:40** and was 51 insertions / 183 deletions against HEAD. Two landings to that file came
after that mtime:

| commit | time | added |
|---|---|---|
| `8dfb28f9f` | 11:59:53 | a clean close says a publish happened, not merely that nothing failed |
| `770497ddd` | 13:33:02 | `_publish_surface_collisions`, `PUBLISH_EXTRA_RELATIVE` |

Both landed through an isolated worktree. `surgical_land --content` **never writes the working
tree** — deliberately; that is what makes it safe for a two-lane file. So HEAD moved past the
shared copy twice and the shared copy stayed at 11:27.

## The gate's subject is HEAD; the publisher's own code is the working tree

`DIRECTOR_RULING_PUBLISH_GATE_SUBJECT_2026-08-09` moved the gate's subject to a clean checkout of
HEAD, and this cycle's log confirms it: the suite ran in `/var/tmp/publish-gate-head-ns33k2yg`.
That ruling is right and is not in question here.

But the *daemon* runs from the shared tree (`cwd = /home/rich/synthetic-enterprise`) and imports
its module from disk. For the one file that is both **the thing gated** and **the thing running**,
those are two different trees:

- the gate proved HEAD green, including `test_the_publish_refusal_asks_whether_the_fork_touches_its_own_paths`, the control written for `770497ddd`;
- the live publisher ran the 11:27 draft, in which that mechanism does not exist.

The tell was in the failure record and had been for two cycles: the stored `cause_evidence` quotes
the **old** refusal string verbatim — *"Do NOT run `surgical_land --merge origin/main` in the shared
tree…"* — which is the working copy's wording. HEAD's is shorter and different. A landed, tested,
green repair was inert in the only process that could use it.

## Why nothing noticed

`tools/stale_copy_refusal.py` is a **commit-time** door; its live callers are
`tools/surgical_land.py` and the pre-commit hook. It refuses a commit whose copy of a file predates
the last landing to that file. Nobody was committing `background/process_run_complete.py`, so the
refusal never had a subject — while the daemon imported those bytes every cycle.

Its `--census` mode (working tree vs HEAD) names it immediately. `--census` has **no caller**: it is
a manual diagnostic. On the live tree it currently reports `WOULD REVERT A LANDING: 8`.

**The gap is a class.** A stale working copy of any module a *daemon* imports is invisible to a
commit-time control, because a daemon is not a commit. The subject a running daemon's code needs is
"the bytes on disk", and the only thing that reads those is a tool nothing calls.

## What was done, and how the judgement was checked rather than asserted

`python3 -m tools.refresh_to_head background/process_run_complete.py --write --slug
lane0-publisher-1127-draft` — the sanctioned tool for this exact class. It recomputed both
preconditions independently rather than taking the seat's word:

> rival copy: supplies no name HEAD lacks, and the stale-copy control refuses it
> `[predates_landing]`. HEAD strictly supersedes it.

Measured over both blobs with `stale_copy_refusal.symbols`: names the 11:27 copy supplied that HEAD
lacks — **none**; names HEAD supplied that it lacked — `PUBLISH_EXTRA_RELATIVE`,
`_publish_surface_collisions`. The 51 discarded lines are preserved on
`refs/preserved/refresh-to-head/lane0-publisher-1127-draft`, with the `git log --all -S` recovery
route run rather than printed.

## The repair changed the verdict, measured on one variable

Same tree, same fork, one file swapped — the two versions disagree:

| | verdict on the live 4-commit fork |
|---|---|
| the 11:27 copy | refuse, `behind_origin` |
| HEAD's copy | `collisions == []` → **publish** |

Every arriving path in that fork was under `tests/`; not one was on the publish surface. The
refusal was about a fork that could not have touched the commit it refused.

The next cycle, run with the refreshed bytes, logged the line the stale copy could not produce:

    origin/main is 5 commit(s) ahead, but NONE of its incoming paths is one this publish
    commit writes -- so this commit cannot conflict with the fork it would widen, and
    `origin_reconcile` absorbs it on the next cadence. Publishing.

It committed. Its own `git push` was then rejected non-fast-forward (it was 5 behind), and
`python3 -m background.origin_reconcile` carried the commit to origin in an isolated worktree —
*"the merge gated clean and was pushed"* — which is precisely the absorption the mechanism's own
note predicts.

## What is NOT done

1. `episode_clean_publishes` is 0. Separate defect, filed beside this.
2. The stale-copy class is repaired at this instance only. `--census` still has no caller, so the
   next daemon module a landing moves past goes stale the same silent way. Deliberately not built
   this turn: it is a second control on the publish path and the turn's subject was the publish.
3. `origin_reconcile` pushed the merge but could not advance the shared checkout — 3 paths are
   other lanes' uncommitted work (`docs/design/self_clearing_alarm_dispositions.json`,
   `tests/design/test_maturity_map_contract.py`,
   `tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py`). Those lanes' to land.
