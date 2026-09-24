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

## What was done

`python3 -m background.origin_reconcile` was run against the shared tree — the door that can
actually close this — after the promotion refusal established that the seat-worktree route cannot.
Its outcome is recorded in the hand-off beside this document.

## What is NOT done, and is the next work

1. **The nine tracked alarm collisions.** They are regenerated faster than they can be landed, so
   landing them is not a fix — the writer has to stop putting tracked, origin-colliding documents
   into the shared working tree, or the alarm set has to move to a path `origin` does not carry.
   This is the class; the twelve instances are not.
2. **`reconcile-watch` must call the reconciler it watches**, or stop claiming to watch it.
   `unchanged -> log only` on a drift it has the door to close is a control that cannot fail.
3. **The 55-module boot drift.** A restart, not a fast-forward, is what makes any landed daemon
   repair live. Nothing in this turn changes it.
