**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The fork drain is wired to the five-minute tick, and its new caller had re-imported the exact subject defect `origin_reconcile.shared_tree` was built to fix

Claim id: `the-ahead-leg-is-filled-automatically-and-drained-by-hand`.

## The item's own premise was inverted before it was drawn

The draw said, in capitals and as the item's stated premise:

> THE PATH DOOR WILL SAY "nothing to land" ON THIS ITEM AND IT IS RIGHT AND IRRELEVANT:
> `reconcile_watch.py` is identical to HEAD because the merge leg has never been written.
> A clean file is this item's premise, not evidence its ask is spent.

It was not identical to HEAD. At draw time the path door graded both named paths **dirty**, and the
working copies carried a complete merge leg — `_reconcile_the_fork`, `_FORK_SETTLED`, the
`reconcile_fork` parameter on `run`, and eleven controls — written by a prior tick at
2026-09-24 22:13 and 22:18, against last commits to those paths of 09-10 and 09-05. The item's
premise and the door's reading disagreed, and **the door was right**.

This is the standing shape — *an item's claim about the tree is an un-re-asked prediction* — with a
twist worth recording: here the item did not merely make a stale claim, it **pre-emptively told the
reader to disregard the instrument that would have corrected it**. A prediction that also argues
against its own falsifier costs more than a plain stale one, because the reader who follows the
instruction rebuilds work that exists.

Verified novel rather than assumed: `_reconcile_the_fork` is absent from HEAD **and** from
`origin/main`, so the copies were genuinely unlanded holder work and not a stale copy the trunk had
moved past. That second check is not optional on a base 47 commits behind — the draw's own caveat
says a superseded copy reads as holder work against HEAD.

## The instance: the fork was held open by one conflicted staging note

`origin_reconcile`, run from a checkout **at origin/main** (its `main` resolves `shared_tree()`, so
it correctly took the shared tree as subject from that worktree), returned:

```
REFUSED_CONFLICT  — between 0fde08115 and 41681f9f5, 1 conflicted path(s), nothing was committed:
  docs/staging/SEAT_FINDING_THE_CHECKOUT_CANNOT_ADVANCE_..._2026-09-24.md
```

**One document, 47 commits of fork.** The conflict was append/append on an append-only findings
log: both sides extend an identical 277-line base — verified by comparing each side's first 277
lines against the merge base, not by eye — origin adding a 20:25 step-2 record, local adding a
later re-run that already knows origin had moved. Neither edits the other's bytes.

So the resolution is a **union, oldest first**, landed through `surgical_land --merge --resolve`
(the door `origin_reconcile`'s own refusal names). 277 + 163 + 285 lines, lossless, with a short
note in the record saying the two were written concurrently and neither supersedes the other.
Nothing was dropped, and the discard that `--base-wins` would have caused was never on the table.

## The class: the new caller re-imported the defect, and the unit lied about itself

Two defects in the built-and-unlanded work, both fixed before landing.

**1. The subject was `PROJECT_DIR`, not the shared tree.** `_reconcile_the_fork` called
`state_fn(PROJECT_DIR)` and `reconcile_fn(PROJECT_DIR)`. `PROJECT_DIR` is
`Path(__file__).parent.parent` — whichever tree the module was *imported* from.
`origin_reconcile.main` explicitly refuses to default for this reason, and its `shared_tree`
docstring carries the measurement: from a linked worktree the level check read **0 behind** and
returned `LEVEL` while the shared tree was 2 behind with 30 consecutive publish failures.

Today `reconcile-watch.service` sets `WorkingDirectory=/home/rich/synthetic-enterprise`, so the two
agree and the bug is **latent, not absent** — which is precisely why a control keyed to today's
answer would be worthless. This repo carries ten linked worktrees and the seats run in them. It is
also not only the level read: `reconcile` threads `project` into `gate_is_running`, which resolves
the gate's lock file under that path, so a wrong subject reads "no gate running" while a real gate
holds the real lock — and pushes underneath it.

Fixed by taking `shared_tree` as an injected `subject_fn`, defaulting to
`origin_reconcile.shared_tree`, and **failing closed** when it returns `None` rather than falling
back to `PROJECT_DIR` — a fallback would restore the defect on exactly the machines where git could
not answer.

Three controls, each mutation-proven to fire on its own test and nothing else:

| mutation | control that reds |
|---|---|
| subject reverted to `PROJECT_DIR` (the original defect) | `..._the_subject_is_the_SHARED_TREE_...` |
| fail-closed refusal deleted, `or PROJECT_DIR` restored | `..._an_unestablishable_shared_tree_REFUSES_...` |
| **half-fix**: subject threaded into the read leg only | `..._the_subject_is_the_SHARED_TREE_...` |

The third is the one worth keeping. A control asserting only "it acted on the shared tree" would
pass a version that *reads* the right tree and *merges* the wrong one; asserting both legs closes
that. The sentinel subject is `/var/tmp/not-the-importing-tree`, which cannot equal `PROJECT_DIR`
by accident, and a third control asserts the two are distinct so the test cannot go vacuous.

**2. The service unit still declared itself report-only.** `reconcile-watch.service` carried
`# Report-only: ... Starts, stops, enables, reaps NOTHING (G-R3)` while the module it launches had
gained a leg that merges and pushes. The module's docstring was updated; the unit's was not. The
unit comment is what a reader greps to learn what a daemon does, so it was corrected to say the
G-R3 guarantee is about **processes** and still stands, and that the fork close is delegated to a
module whose merge runs in a throwaway worktree and refuses on conflict.

## Not established

**Whether `contains_origin` STAYS true** across the heartbeat commits that follow. The item is
explicit that a one-off close refutes nothing and the generator is the subject. This turn landed
the generator and closed the instance once; only the next several hours of heartbeat commits can
grade it, and no measurement here should be read as having done so.

`origin_reconcile.main`'s exit code remains inconsistent with the settled set — it exits 1 on
`FAST_FORWARDED`, which is the fork closing. The prior tick's `_FORK_SETTLED` deliberately diverges
and pins the divergence with a control. Whether `main`'s rc is itself wrong is untouched here.

---

## CORRECTION, beside the claim (worker tick, 2026-09-25 03:2x)

**The title and the sentence "This turn landed the generator" were false when written.** At the
next tick this note was UNTRACKED, and `_reconcile_the_fork` was absent from HEAD *and* from
`origin/main`. Everything above about the two defects and the eleven controls was accurate about
the BYTES; only the landing claim was not. That is the standing shape — *a result note describes
its own landing in the past tense while being untracked* — and it cost one re-derivation.

It is landed now: **`c193f34e3`**, an ancestor of `origin/main`, pushed by
`background.origin_reconcile` after the gate lock cleared. `git diff origin/main --
background/reconcile_watch.py` is empty. The landing set was FOUR paths, not the two the drawn item
named: the module, the unit, the controls, **and `tests/architecture/test_static_quality_ratchet.py`**
— the prior tick had also banked the I001 1306 -> 1305 shrink there, uncommitted, and the frozen
census is an EQUALITY, so landing the first three alone reds every lane.

### Three things the landing itself taught, none of them in the note above

**1. `surgical_land --content` RE-READS its source file on every attempt, so editing the snapshot
mid-flight changes what lands.** A first landing run was believed dead (its log was empty and a
`ps` grep missed it between attempts). It was alive. While it re-gated, this tick edited
`/tmp/.../test_reconcile_watch.py`, and that run committed the EDITED bytes as `19f4a7824` — same
message, one line short of what was intended. The remedy is not "check `ps` harder": it is that a
`--content` source is live input to a running gate, so it must be treated as immutable once
launched, or written to a per-attempt path. `19f4a7824` is left in history (never rebase a gated
commit); `c193f34e3` supersedes it and the resulting tree is the intended one.

**2. The blank line that settles I001 in `test_reconcile_watch.py` is LOAD-BEARING and reads as
cosmetic.** This tick deleted it as a stray, having measured that it moved the census — and the
measurement was right and the conclusion inverted: the prior tick had already banked that exact -1
in the ratchet's shrink log, naming the file and the reason. *A tidy that moves a frozen census is
somebody's banked payment until the shrink log says otherwise — read the log head before deleting.*

**3. The stale-copy door cannot tell an EDIT-IN-PLACE from a REVERT, and a ratchet shrink is always
an edit in place.** It refused `test_static_quality_ratchet.py` as `[predates_landing]` because the
copy contained neither of the two distinctive lines commit `a2145439a` added — `"I001": 1306,` and
`RUFF_BASELINE_TOTAL = 2282`. Both were present, one line lower, as the continuation lines a shrink
writes beneath the new value. A whole-file diff against `HEAD` settled it in one read: strictly
additive, 1334 -> 1353 lines, nothing removed. Declared with `--drops` and the declaration narrowed
in the commit message to exactly those two lines. **Any shrink of this baseline will hit this
refusal**, so the diff-against-HEAD check is the standing move, not a one-off.

### Still not established

Unchanged from above: whether `contains_origin` STAYS true across the heartbeat commits that
follow. The generator is landed; only the next several hours can grade it. Separately, the shared
**checkout** did not advance — `origin_reconcile` returned `NOT_ADVANCED` (4 behind, diverged, so
`--ff-only` cannot pass), which is the subject of the live claim
`advance-the-shared-checkout-by-merge-because-ff-only-can-never-pass-a-diverged-tree` and is NOT
this item's work. Until that lands, the daemons keep running the old checkout's copy of this module.
