**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# FINDING — the nine alarm documents that say the shared tree will not advance are the nine paths that stop it advancing

Drawn as `close-the-shared-tree-fork-that-holds-the-publisher-and-keeps-the-divergence-repair-inert`.
Grades `SEAT_PREREG_CAN_THE_CADENCE_THE_DISJOINT_ADMISSION_BETS_ON_EVER_PAY_2026-09-24.md`
— **P1 REFUTED, P2 not reached as stated, P3 confirmed** — kept beside the predictions.

## The premise, re-measured at draw — the item's stated WHY is SPENT

The item measured **10 ahead / 11 behind** at 01:5xZ. At **03:10Z** the shared tree was **1 ahead /
6 behind**, and:

* `e89d05840` **is an ancestor of the shared tree's `main`**, not only of `origin/main`.
* The repaired signature is in the shared tree's **working copy**:
  `background/origin_reconcile.py:411` reads `def _blocking_clause(blocking, ahead)`.

So the item's WHY — *"the shared tree's CHECKOUT cannot take it while it cannot fast-forward"* — is
**no longer true**. The checkout has the repair.

**The symptom survives under a different mechanism, and it is the one the memory rule names:** a
daemon holds the code it booted with. `reconcile-watch`'s own log line, every five minutes:

> boot-sha drift: background-worker (**55 modules behind**); deadmans-switch (55 modules behind);
> naive-organ (55 modules behind); sim-runner (55 modules behind); supervisor (13 modules behind)

The repair is on disk and in no running process. **Landing is not running, and a fast-forward would
not have fixed this either** — only a restart will. Closing the fork was never going to make the
repaired sentence appear in their logs, which is what the item predicted it would do.

## P1 REFUTED, and the refutation is the useful half

**P1 predicted `origin_reconcile` has no unattended merge leg** — that the disjoint admission bets
on a counterparty who structurally cannot pay. **Wrong.** `origin_reconcile:1721` runs
`surgical_land --merge origin/main` inside a throwaway worktree (`/var/tmp/se-origin-reconcile`),
and says in its own commit message why the unattended-merge objection does not reach it:

> Done in a throwaway worktree with its own index, so the objection the publish path's own refusal
> raises … cannot apply: the shared tree is never opened.

It works, and has worked many times: **15+ `merge origin/main: automatic reconciliation in an
isolated worktree` commits** are on `origin/main`. The bet is payable. **P3 confirmed** — the
admission is routine, not a race (138 `chore(liveness)` commits in `main`'s reflog), and
`_unabsorbed_publish_commits` correctly caps the strand at one.

So the fork is not a design gap. **The payer is simply not being called.**

## What is not being called, and it is not what the alarm says

`reconcile-watch` has logged, every five minutes without interruption from at least 02:31Z to
03:11Z:

> `reconcile DRIFT (9 alarm(s)); unchanged -> log only`

**`log only`.** It detects the drift and writes documents about it. It never calls `reconcile()`.
This is the memory rule *"`reconcile-watch` exits success every 5 min without advancing the shared
tree"* — confirmed here, with the mechanism named: it is not failing to advance, it is **not
attempting to**.

## The loop, which is the finding

Measured at 03:1xZ, `paths_blocking_fast_forward` names **12** paths — up from the **4** the
2026-09-24 00:38Z turn measured. The growth is entirely in the **tracked** class, and all nine of
the new ones are the same kind of file:

| path (all `docs/staging/WORKER_FINDING_REPEATING_ALARM_*`) | kind |
|---|---|
| `…DEADMAN_LAUNCH_ARTEFACT_UNLANDED_2026-09-18.md` | modified here, **and origin changes it too** |
| `…DEADMAN_ORIGIN_FORK_2026-09-15.md` | modified here, and origin changes it too |
| `…DEADMAN_WORKTREE_UNDECLARED_2026-09-15.md` | modified here, and origin changes it too |
| `…DELIVERY_LANE_STRANDED_2026-09-18.md` | modified here, and origin changes it too |
| `…RUN_MARKER_SWEEP_HAS_MADE_ZERO_PROGRESS…_2026-09-21.md` | modified here, and origin changes it too |
| `…SEAT_CLAIM_2026-09-15.md` | modified here, and origin changes it too |
| `…SEAT_CONTINUITY_2026-09-15.md` | modified here, and origin changes it too |
| `…STRETCH_LOG_2026-09-17.md` | modified here, and origin changes it too |
| `…TREE_DIVERGENCE_2026-09-15.md` | modified here, and origin changes it too |

**Nine.** The same nine `reconcile-watch` counts in `reconcile DRIFT (9 alarm(s))`. Both legs of
the collision verified independently: `git status --porcelain` reports all nine ` M`, and
`git diff --name-only main origin/main` reports origin changing all nine. Their mtimes move while
being measured — 04:05:34, 04:10:28, 04:10:30, 04:11:04, 04:12:51 — i.e. the writer is running now.

So:

> `reconcile-watch` detects the tree is behind → writes nine tracked alarm documents into the shared
> working tree → those nine become `FF_MODIFIED` collisions with origin's own copies →
> `advance_shared_tree` refuses the fast-forward → the tree stays behind → next cycle, the same nine.

**The alarm about the tree not advancing is what stops the tree advancing.** The purest instance is
`WORKER_FINDING_REPEATING_ALARM_TREE_DIVERGENCE_2026-09-15.md`: the document reporting the
divergence is one of the files preventing the divergence from closing.

### CORRECTION, written the same turn, kept beside the claim rather than replacing it

**Two sentences above are wrong, and the error is this project's own named trap.** I wrote that
`reconcile-watch` writes the nine documents and "never calls the reconciler it watches", and I read
its `reconcile DRIFT (9 alarm(s))` as *the same nine*. Both are unestablished:

* **`reconcile_watch` is not a watcher of `origin_reconcile`.** The name misled me. It reconciles
  *declared versus actual* across processes, schedules and gap-ledger rows and pages on transitions
  (`background/reconcile_watch.py:270-296`). It never claimed to call `origin_reconcile`, so "never
  calls the reconciler it watches" is a criticism of something it does not purport to do.
* **The two nines are different quantities.** `9 alarm(s)` is `len(sig)`, the drift-report
  signature. The nine blockers are nine *files*. I matched two counts and asserted an identity
  between them without asking what either counts — the exact failure CLAUDE.md names
  (*"before dividing two numbers, say out loud what each one counts"*) and the one my own note
  *"a regenerated channel's volume does not imply repetition — ask the grouping key"* exists to
  stop. The equal 9s are, so far as this turn established, a coincidence.

**The writer is `background/alarm_repetition.py`** (`:271`, `:427`), keyed by alarm *family*: it
locates an existing document by stem and rewrites it in place, which is why files dated 09-15 and
09-17 carry 04:12 mtimes. Its callers are many daemons, not one.

**What survives, and it is the stronger statement** — every leg below was measured directly, none
of it depended on the attribution:

> A repeating-alarm document is a **tracked** file that seats land to `origin` and the alarm
> machinery keeps **rewriting in place** in the shared working tree. Every alarm family that is
> both landed and still firing therefore holds a permanent `FF_MODIFIED` collision against
> origin's own copy of itself, and `advance_shared_tree`'s all-or-nothing rule means any one of
> them refuses the whole fast-forward.

That is a property of the alarm machinery as a class. It does not need `reconcile_watch` to be the
author, and it is why the blocking set grows with the number of *live* alarm families rather than
with anything about the fork.

## The system's own instrument proves the loop, and names which leg is blocked

`docs/observability/deadmans-switch-log.md`, **2026-09-24 02:52 UTC**, unprompted:

> ORIGIN FORK (NOT_ADVANCED): **the merge gated clean and was pushed**, but the shared tree did NOT
> advance and is still 3 commit(s) behind. Refused by 11 path(s): [the nine tracked
> `WORKER_FINDING_REPEATING_ALARM_*` files] … advance: 6 of 11 blocking path(s) could NOT be proven
> lossless, so clearing the 5 that could would touch files and still not advance.

So the cadence is **not** the problem and neither is the merge leg. `deadmans_switch.py:740` calls
`origin_reconcile.reconcile()` every five minutes; it merges, it gates, it pushes, **and then the
fast-forward of the shared checkout is refused by the alarm documents.** Every leg works except the
last one, and the last one is blocked by the files the earlier legs' own failure causes to be
written. That is the loop, stated by the machine rather than by me.

(At 03:10, 03:15 and 03:20 the same log reads `GATE_RUNNING` — the publish gate has held its run
lock since ~02:57Z, which is the same refusal this turn got at 03:2xZ. The deadman is not even
reaching the fork on those cadences.)

## The obvious fix is wrong, and the reason is the thing worth writing down

`WORKER_FINDING_REPEATING_ALARM_*` is **not** in the generated-paths oracle, so
`origin_reconcile._split_generated` classifies these daemon-written files as *authored* — "holder
work" — which is precisely why `advance_shared_tree` will not clear them. The one-line fix suggests
itself immediately: add the stem to the oracle, let the advance clear them losslessly, done.

**It is wrong, and the document says so in its own words:**

> Both counts are **DERIVED from this document's own dated lines** every time the alarm fires again,
> so they age with the document rather than with its first firing.

**The published artefact IS the state store.** There is no `.json` behind it. Clearing the file does
not lose a regenerable rendering, it loses the alarm's entire history — and the histories are large
and real: the working copy of `…SEAT_CONTINUITY_2026-09-15.md` is **+10,525 / −4 lines against
HEAD**, ten days of dated observations and 27 family members that origin's copy does not have.
`refs/preserved/…` would hold the bytes, but nothing would ever read them back, and the next
document would restart its counts from one while claiming to age with the condition.

Measured churn: hashes and mtimes move while being sampled (04:16:04, 04:20:35), so the pile is
**actively rewritten, not static** — a one-off landing races the writer and does not close it.

**The class, stated properly:** *a repeating-alarm document is simultaneously the state store and
the published work item, and it lives on a tracked path in the shared working tree that origin also
carries.* Any two of those three are fine. All three together make a permanent, self-refilling
`FF_MODIFIED` collision that no drain can clear and no cadence can absorb. The fix separates the
store from the artefact — the accumulating counts belong somewhere untracked, with the staging
document derived from them — and it is emphatically not a line in the generated oracle.

## This INVERTS the prior turn's conclusion at the second step, without contradicting it

`SEAT_RESULT_THE_UNTRACKED_BLOCKERS_ARE_NOT_THE_CAUSE…` concluded *"no path is the cause of this
wedge"*. **That was correct at `ahead = 10`** — `advance_shared_tree` refuses on divergence before
judging any path, so no path could be the cause.

It is correct only while the tree is diverged. **The moment the fork closes and `ahead` reaches 0,
`advance_shared_tree` starts judging paths — and all twelve become the cause.** Closing the fork is
necessary and *not sufficient*, and the obstacle waiting behind it has **tripled, 4 → 12**, while
the prior turn's finding said the instances were not the work. They were not the work *then*. They
are the work *next*, and nine of them are tracked, which no orphan drain touches.

## The door the item named second cannot close THIS fork, and that is structural

I gated the merge from this isolated worktree: `surgical_land --merge main` produced **`237c4a401`**,
clean, no conflict, and moving `agent_status.json` forward (02:40Z → 03:00Z), not back.
`promote_worktree_landing` then **refused, naming its reason**:

> REFUSED: `b26362f94` carries no verifying surgical_land receipt, so it was not gated — one of the
> 2 commits this push would add, beneath the tip

`b26362f94` is the liveness heartbeat, committed by `_commit_and_push_paths` through a plain
`git commit` under the pre-commit hook. It is gated, but it carries **no surgical-land receipt**, and
the promotion door promotes only receipted commits. `237c4a401` was therefore abandoned — it exists
in no branch and this worktree was reset back to `origin/main` to land this record. The nine-minute
gate it cost is the price of the measurement, and it is why this is written down.

**Therefore: a fork whose local side is a daemon commit cannot be closed by an isolated seat
worktree at all.** Any merge a seat gates has that unreceipted commit as a second parent, and the
promotion door refuses on it, correctly. `origin_reconcile` closes it because `_push` is a plain
`git push origin HEAD:main`, which asks for no receipt.

The item offered the two doors as alternatives — *"the reconciler's own merge leg … **or**
`surgical_land --merge origin/main`"*. **They are not alternatives for this class of fork.** Only
the first one works, and the second one spends a full nine-minute gate cycle to earn a refusal at
the very end. That is what it did here.

## What was done, and what was NOT

`python3 -m background.origin_reconcile` was run against the shared tree — the door that can
actually close this — after the promotion refusal established that the seat-worktree route cannot.
It returned **`GATE_RUNNING`**: the publish gate (PID 2672400, `run_complete_20260924T023001Z.md`)
has held the run lock since ~02:57Z and was still holding it 24 minutes later. That refusal is
**correct** — moving origin under a running gate spends the whole gate run — and it is the same
answer the deadman got on its 03:10, 03:15 and 03:20 cadences.

**THE FORK IS NOT CLOSED BY THIS TURN, and closing it would not have been enough anyway.** It stood
at 1 ahead / 6 behind at 03:10Z and had widened to 2 ahead / 7 behind by 03:3xZ. What this turn
establishes is that closing it is *not the work*: the deadman has closed it repeatedly (merge gated,
pushed) and the shared checkout still does not advance, because the fast-forward behind it is held
by twelve paths that regenerate themselves. **The next seat should not spend another turn on the
merge.**

## What is NOT done, and is the next work

1. **Separate the alarm's state store from its published artefact.** This is the class and the only
   fix that ends the loop. The counts must live somewhere untracked and the `docs/staging/`
   document must be derived from them, so that clearing the document is lossless and
   `advance_shared_tree` can treat it as regenerable. **Do not shortcut this by adding
   `WORKER_FINDING_REPEATING_ALARM_` to the generated-paths oracle** — the section above measures
   why that silently destroys ten days of alarm history on a path whose bytes nothing reads back.
2. **The 55-module boot drift.** A restart, not a fast-forward, is what makes any landed daemon
   repair live. Nothing in this turn changes it, and no fast-forward ever will.
3. **Not `reconcile-watch`.** An earlier draft of this document made it the culprit; the correction
   above retracts that. It is not a watcher of `origin_reconcile` and there is nothing to fix in it
   for this condition. `deadmans_switch.py:740` is the caller, and it works.
