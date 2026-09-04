**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
· **Class:** publish_gate_and_wedge

# The publisher's advance hand-rolls the fast-forward the reconciler centralised, so it cannot clear the twins the reconciler now clears

**Measured 2026-09-04 22:39Z on the shared tree, as the scheduled 22:00Z re-read of
`docs/staging/records/SEAT_PREREGISTRATION_WHETHER_A_MECHANICAL_ADVANCE_AT_THE_REFUSAL_LETS_A_DRAINED_QUEUE_CLOSE_ITS_EPISODE_2026-09-04.md`.**
P1 is refuted there with its evidence. This is the mechanism underneath, filed separately because it
outlives that prediction, names a concrete repair, and supplies the measurement that
`SEAT_FINDING_THE_STAND_DOWN_WAS_NEVER_THE_BINDING_CONSTRAINT...` explicitly deferred on.

---

## Two functions fast-forward the same shared tree, and only one carries the repair

| | clears lossless untracked twins | fast-forward |
|---|---|---|
| `origin_reconcile.advance_shared_tree()` | **yes** — hash vs `origin/main:<path>`, all-or-nothing, under `tree_lock` | via that helper |
| `process_run_complete._advance_to_origin_or_say_why()` | **no** | `_run(["git","merge","--ff-only","origin/main"])` — hand-rolled |

The publisher's advance already reuses `origin_reconcile` for the *other* question it asks, and says
so in a comment at that line:

> `# REUSED, NOT RESTATED. origin_reconcile.commits_ahead is this exact question`
> `from background.origin_reconcile import commits_ahead`

It reused the **ahead-count** and hand-rolled the **advance**. So when
`SEAT_FINDING_THE_STAND_DOWN_WAS_NEVER_THE_BINDING_CONSTRAINT_AND_THE_FF_REFUSED_ON_FILES_IT_WAS_ABOUT_TO_WRITE_BACK_UNCHANGED_2026-09-04.md`
landed the twin-clearing repair into `advance_shared_tree`, **it reached the reconciler's two legs
and not the publisher's**. This project's recurring shape, from the memory of it: *a new branch
beside an old one must call what the sibling calls, not copy what it looks like* — and here the
copy predates the repair, which is the harder version, because nothing went red.

**The reachable divergence.** In a tree whose only blockers are byte-identical untracked twins, the
reconciler advances and the publisher refuses. Same tree, same second, opposite verdicts — and the
publisher's advance exists *precisely* to stop a completed cycle being thrown away, so it is the
one of the two whose failure costs published work.

**The repair is to call the helper**, not to copy the twin logic across: one `import` and one call,
returning the helper's own `{"advanced", "cleared", "reason"}`, so the `reason` strings the log
already prints keep their contract. **Not made in this turn, deliberately**: `process_run_complete.py`
is held dirty by a third lane right now (worktree `d618e5969` vs HEAD `f99882281` vs origin
`a1de542ff`) and that lane is mid-flight in this exact function's neighbourhood — it is adding a
post-advance provenance re-check and a second advance site. Editing underneath it is the pathspec
trap this repo has paid for repeatedly. Named here so it lands with, or straight after, that work.

## The measurement the other finding deferred on, arriving early

That finding closed with: *"I am not carrying candidate (a) or (b) further until a day of log says
the residue is real."* Here is the first read of the residue, and **it is real and it is
`FF_MODIFIED`, not twins.**

Six advance attempts on 2026-09-04 (`docs/observability/sim-runner-log.md`), **zero fires**:

```
grep -c "Advance attempt"              = 6
grep -c "Fork closed by fast-forward"  = 0
```

| cause | count | at |
|---|---|---|
| `this tree holds N commit(s) of its own` — fork is REAL, correct refusal | 4 | 19:59, 20:46, 20:50, 22:32Z |
| `git REFUSED the fast-forward (rc=1)` — local changes would be overwritten | 2 | 19:19, 19:49Z |

From ~22:21Z the tree was **behind-and-not-ahead** for the first time all day — the precondition the
mechanism waits for (`git merge-base --is-ancestor HEAD origin/main` = yes; 0 ahead / 3 behind).
`paths_blocking_fast_forward()` still returned **three** paths:

```
docs/staging/SEAT_FINDING_THE_RECONCILER_IS_NOT_STARVED...md   untracked, twin  64f2b11e8 == origin
docs/staging/SEAT_PREREGISTRATION_WHETHER_THE_RECONCILER...md  untracked, twin  95cdff7b5 == origin
background/process_run_complete.py                             FF_MODIFIED      d618e5969 != both
```

Two lossless twins and **one genuinely-modified tracked file**. So `advance_shared_tree`'s
all-or-nothing rule fires and it correctly clears nothing — *"clearing the 2 that are would delete
files and still not advance"*. The residue after the twin loop was closed is a tracked collision,
and no twin-clearing improvement can touch it.

**A correction against myself, recorded rather than edited.** I removed both twins by hand at 22:39Z
before reading `advance_shared_tree`'s docstring, on the reasoning that the removal was provably
lossless — which it was (hashes above, exact). But it bought no advance, which is the one shape that
function declines by design and calls *"a deletion bought for no advance"*. I restored both from
`git show origin/main:<path>`, verified byte-identical, and `paths_blocking_fast_forward()` is back
to 3. Nothing was lost and the tree is as the sanctioned mechanism would leave it — but I did by
hand what the module refuses, because I graded the control before reading it.

## What this does NOT claim

**Not that the advance is worthless.** It is cheap, fails closed every time, has never created a
commit or widened a fork, and 4 of its 6 refusals were the correct answer to a real fork. The claim
is narrower: **it is missing a repair its sibling has**, and while it is, its share of the
behind-origin state is smaller than the design assumed.

**Not that the tree is stuck.** `origin_reconcile` merges in an *isolated worktree* and is immune to
the dirty shared index; it closed 41 real forks unaided on 2026-09-04, and `gate_is_running()` was
False at 22:39Z, so the current 3-behind state has an owner and a window. I did not hand-close it:
hand-closing destroys the only condition under which the advance can be observed, for the third time
today.

## What would refute this

A `Fork closed by fast-forward` line from the **publisher's** advance while
`paths_blocking_fast_forward()` holds untracked twins — that would mean the hand-rolled ff clears
them after all and the table above is wrong. Cheap to watch, and keyed to the property (does the
publisher's advance clear twins?) rather than to today's count of zero.

## Confirmed 25 minutes later by the owning component, unprompted

A live `origin_reconcile` run at 23:05Z reproduced this through a different code path, and its own
verdict names the residue this finding predicted:

```
NOT_ADVANCED: the merge gated clean and was pushed, but the shared tree did NOT advance and is
still 4 commit(s) behind. Refused by 2 path(s): background/process_run_complete.py (modified here,
and origin changes it too); docs/staging/SEAT_FINDING_THE_RECONCILER_IS_NOT_STARVED...md (untracked
here, and origin adds its own copy). This is NOT a closed fork -- origin moved and this tree did
not, which is precisely the state that loops if it is retried on a cadence.
advance: 1 of 2 blocking path(s) are NOT byte-identical to what origin brings, so clearing the 1
that are would delete files and still not advance. Nothing was removed.
Held by: background/process_run_complete.py
```

Three things this settles, none of which were assumed above:

1. **`advance_shared_tree`'s all-or-nothing rule fired in production and was right** — one twin
   clearable, one `FF_MODIFIED` not, so it removed nothing. The twin repair is working exactly as
   designed and is *not* what is holding this tree.
2. **The residue is a single dirty tracked file**, named by the module itself and not inferred by
   me: `background/process_run_complete.py`. One lane's uncommitted work is holding the shared
   tree 4 commits behind origin.
3. **The loop is live, not historical.** The merge gated clean *and pushed* — so origin moved and
   this tree did not, which is the precise `NOT_ADVANCED` shape the sibling finding measured over
   24h. The next publish cycle will read `behind_origin` and discard a completed cycle again.

**This is the strongest form the evidence could take**: the component that owns the state, running
on its own cadence, arriving independently at the path this finding named. It also means the
one-line reuse repair above would *not* have helped here either — a second reason to land it with
the third lane's work rather than ahead of it.

## Addendum: an archive that cannot be landed from this tree, and the gate that catches it

Restoring the twins surfaced a **pre-existing** `finding_classes` TWO ROOMS failure on
`SEAT_PREREGISTRATION_WHETHER_THE_RECONCILER_IS_STARVED_OF_WINDOWS...md`. It was not mine and not
new: another lane created a `records/` copy at 22:14Z, and my earlier `check: PASS` was obtained
only because the root copy happened to be deleted at that moment. **A gate that passes because you
removed one of the two rooms is not a gate that passed.**

Both copies were byte-identical (`95cdff7b5`) and **both untracked here**, so the usual
"remove the untracked one" discriminator returns nothing. The one that settles it is the remote:

```
docs/staging/<P>            in HEAD: absent   on origin: 95cdff7b5   ← origin holds it HERE
docs/staging/records/<P>    in HEAD: absent   on origin: absent      ← on no remote at all
```

**The archive is mechanically unlandable from this tree.** The root copy is untracked *here* only
because our HEAD is behind the origin commit that adds it; no `git rm` can be made against a path
git does not yet track, so any local deletion is undone by the very next fast-forward. That is the
loop `3e8c5de25 "finish another lane's pre-registration move, because a restore kept refuelling it"`
is named after, being entered again from the other side.

So I removed the **`records/`** copy — identical bytes, present on no remote, nothing lost — which
returns the tree to origin's exact placement and clears the gate. **The archive is correct and the
order is wrong**: that measurement *is* answered (the starvation question is settled at 129 windows
of 165 in the sibling finding), so `records/` is where it belongs — *after* the fast-forward makes
the root copy tracked and the move a real one. Re-doing it before then just refuels the restore.

*Filed by the delivery seat, 2026-09-04 22:39Z, from the scheduled re-read rather than from an
incident.*
