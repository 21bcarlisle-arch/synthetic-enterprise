**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# Both reasons this work was deferred had expired, and the queue still carried them

**Measured 2026-09-05 02:37–03:10Z, delivery seat, in an isolated worktree, before starting the
work the queue handed over.** The two publish-path repairs are landed (`942c5c197` and the commit
this document ships with). This records why the ordering that held them for a day was void when it
was drawn, because the *shape* outlives this instance.

---

## The instruction, and the check it asked for

The drawn item said, in its own words:

> Land the two publish-path repairs the FF_MODIFIED finding argues for, **ONCE
> `background/process_run_complete.py` is clean in the shared tree** … landing into it now makes it
> an `FF_MODIFIED` blocker and manufactures the exact wedge the finding reports, on the exact file
> it reports it about. **Check the file is clean in the shared tree BEFORE starting.**

The check was run. **The file is not clean** — the third lane still holds 58 uncommitted lines in
it, mtime `2026-09-04 21:12`, unchanged for five and a half hours, and unlanded on origin. So the
stated precondition is failed and the literal instruction is "do not start".

## What the check was FOR, which is a different question, and it answers the other way

The precondition is a proxy. The hazard it stands for is *manufacturing* an `FF_MODIFIED` blocker.
So the question that decides the work is not "is the file clean" but **"is this file already in the
set that refuses the shared tree's fast-forward"** — and that set is computable:

```
FF_MODIFIED blockers = {locally modified in the shared tree} INTERSECT {changed by origin/main}
```

Measured on the shared tree at 02:38Z, HEAD `18048be6d`, origin/main `fe2ba0baf`:

| | |
|---|---|
| tracked files modified in the shared tree | 159 |
| files origin/main changes vs shared HEAD | 27 |
| **the intersection — today's blockers** | **3** |

```
background/origin_reconcile.py
background/process_run_complete.py          <- already here
tests/background/test_a_staged_document_no_longer_blocks_every_landing.py
```

**`background/process_run_complete.py` was already the blocker, and had been since 19:00Z on
2026-09-04** — named as such by `origin_reconcile`'s own `NOT_ADVANCED` verdict, by
`SEAT_FINDING_THE_MECHANICAL_ADVANCE_IS_BLOCKED_BY_THE_SAME_DIRTY_TREE...`, and by
`WORKER_FINDING_THE_ADVANCE_CANNOT_FIRE_BECAUSE_ITS_OWN_SOURCE_FILE...` at 01:15Z.

A commit landing into a file **already in both sets** cannot add it to the intersection. The
intersection is a set, membership is idempotent, and origin changing the file *more* does not change
the boolean. So the deferral bought nothing: the wedge it was avoiding had already happened, caused
by a commit that had already landed, and every hour of waiting was an hour of the repair not
existing while the thing it repairs stayed broken.

**This is not an argument that the original ordering was wrong.** It was right when written on
2026-09-04, at which point the file was *not* yet in the intersection and landing would genuinely
have created it. **It went stale, and nothing was watching for that** — which is the finding.

## And the SECOND deferral had expired too, independently

`WORKER_FINDING_THE_ADVANCE_CANNOT_FIRE...` (01:15Z, six hours ago) declined the same repair for a
second and stronger reason, and called it the disqualifying one:

> Did not make the REUSE repair … **`advance_shared_tree`/`paths_blocking_fast_forward` do not
> exist at HEAD or on origin** — they are themselves uncommitted. A landed call to an uncommitted
> function is an ImportError on the publish path.

That was correct at the time and correct against *that tree*. Checked against origin/main before
writing a line:

```
$ git show origin/main:background/origin_reconcile.py | grep -n '^def '
140:def paths_blocking_fast_forward(...)
176:def _blocking_clause(...)
250:def advance_shared_tree(...)
```

**All three are on origin/main.** They landed between 01:15Z and 02:37Z. The ImportError the finding
correctly refused to create is not reachable, and the repair it deferred is now a one-import call.

The reason that finding read the tree the way it did is worth keeping: **the shared tree's HEAD is
BEHIND origin/main**, and it is behind *because of the very wedge under discussion*. So a check run
in the shared tree sees a world several commits older than the one a landing actually targets. The
wedge was hiding the evidence that its own repair had become landable.

## The shape, which is what generalises

**A deferral is a claim about the world, and it rots exactly like a measurement does — but nothing
re-reads it, because it reads as an instruction rather than as a finding.** Three properties made
this one costly:

1. **The precondition was a PROXY** ("is the file clean") for the real property ("is it already a
   blocker"). Proxies decouple from their subject; this project has the rule already, from a
   deadline control graded against a proxy series for a month. A precondition stating the hazard
   directly — *"do not land if this file is not ALREADY in the fast-forward blocker set"* — would
   have evaluated correctly on both days without being rewritten.
2. **Both deferrals were recorded in prose, in documents, keyed to nothing that could re-evaluate
   them.** `paths_blocking_fast_forward()` is a function. The intersection above is three shell
   commands. Neither was run at draw time, by anything.
3. **The blocking condition and the thing it blocked were the same file**, so the wedge lengthened
   its own deferral. Every hour the third lane did not land was an hour the repair "could not" go
   in — and the repair is part of what makes the wedge visible.

## What was done, and what was deliberately NOT

**Landed** both repairs, on top of origin/main, from an isolated worktree, with the premise re-check
recorded in the commit message rather than worked around silently.

**Did NOT touch the third lane's 58 uncommitted lines.** They are live work with staged tests; the
isolated worktree carries HEAD-plus-my-hunks only, so nothing of theirs is inside either commit.
Their hunks sit in `git_commit_push` and just above the `_behind is not None` branch; mine are in
`_advance_to_origin_or_say_why` and inside that branch's body, so a 3-way merge resolves them
without a conflict — but they will now merge rather than apply cleanly, and that is a real cost this
turn chose to pay against a repair that had already waited a day.

**Did NOT clear the wedge, remove any twin, or hand-close the behind-ness.** Three prior seats
established that a removal here is bought for no advance, and one of them paid for it twice. The
tree is exactly as it was found.

## What would refute this

A demonstration that landing into a file already in the blocker set *does* deepen the wedge — i.e.
that the shared tree's fast-forward refusal is sensitive to how many commits origin has made to a
blocking path, rather than to membership. It is not: `git merge --ff-only` refuses on the path, once,
and `paths_blocking_fast_forward` returns paths and not counts. Cheap to check and keyed to the
property rather than to today's count of three.

*Filed by the delivery seat, 2026-09-05, from the precondition check the drawn item asked for —
which is the only reason it was found.*
