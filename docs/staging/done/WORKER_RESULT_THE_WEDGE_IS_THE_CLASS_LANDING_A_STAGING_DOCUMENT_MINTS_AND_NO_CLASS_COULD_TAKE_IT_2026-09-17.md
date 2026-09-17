# The wedge is the class that landing a staging document mints, and no class could take it

**Date:** 2026-09-17
**Lane:** H_harness
**Severity:** LATENT — a mechanism is landed and the class it clears is closed. One instance
remains on the shared tree and it is a different class (tracked holder work), named below.
**Claim:** `the-publisher-is-wedged-behind-origin-and-the-tree-cannot-fast-forward`
**Subject:** `background/origin_reconcile.py`;
`tests/background/test_an_untracked_orphan_draft_is_preserved_before_the_advance_clears_it.py`
(new); `tests/background/test_the_publishers_advance_reached_the_twin_repair_it_had_been_told_it_missed.py`

---

## The premise, re-measured before anything was built

The item cites `054cf8ca2`, already an ancestor of `origin/main`. That does **not** spend it: the
premise is a tree state, not a commit. Measured at draw time, 23:30 BST:

| | item said | measured |
|---|---|---|
| `git rev-list --count HEAD..origin/main` | 11 | **5** |
| `git rev-list --count origin/main..HEAD` | 0 | **0** |
| `.publish_gate_state.json` `last_clean_publish` | null | **null** |
| `episode_failures` | 68 | **71** |

Still behind, still nothing unpushed, still no clean publish. The premise holds.

**On the duplicate-work note:** the live claim
`the-page-prices-a-sign-off-a-spliced-family-and-nobody-has-asked-where-the-variance-comes-from`
holds `site/data/value_arms.json`. It is **not** this work. That claim is about which family the
proof page prices a sign off; this one is about why the checkout those producers run in cannot
fast-forward. They share no path. Carrying on was correct and no disposition is owed.

## What actually held the tree, path by path — the question the item asked

Two paths, and they are **two different classes wearing the same colour**:

1. `tests/tools/test_fold_noise_floor_family.py` — **tracked holder work**, and correctly refused.
   The working copy supplies `_producer_made_floors` and a control that neither `HEAD` nor
   `origin/main` carries. mtime 19:07:45; four and a half hours old and its author is gone. Whoever
   holds it landed a *different* change to the same file at 22:49 (`471dfd417`, +103 lines) from an
   isolated worktree. It is stranded, not in flight — but it is real work in a form that exists
   nowhere else, and no mechanism may displace it. **This is not repaired here.**

2. `docs/staging/SEAT_RESULT_THE_PUBLISHED_EIGHTEEN_POOLS_TWO_VALUE_ARMS...md` — **an untracked
   draft of a document `origin/main` adds at the same path.** 8,906 bytes written here at 22:36,
   against origin's 9,846 bytes landed at 22:49 in the same `471dfd417`. The difference is one
   paragraph: `~~Give fold_noise_floor_family a value-arm predicate.~~ **DONE, landed with this
   finding.**`

**The item's framing was producer exhaust. That is not what this is, and the real answer is worse,
because it has no cadence to throttle — it is what a CORRECT landing does, once per landing.** A
seat writes a staging document in the shared tree, where it is untracked. It lands it through
`surgical_land --content`, which by design does not write the shared working tree — that is exactly
what makes it safe on a file two lanes hold. And landing a finding *edits* it: the document gains
its own "DONE, landed with this finding" line in the act. So the copy origin adds is never the copy
on disk here, and the next fast-forward refuses on it.

## Why nothing could clear it, and that was structural

`advance_shared_tree` had three resolvable classes and this path is in none of them, by
construction rather than by oversight:

- the **untracked twin sweep** needs hash equality — the landed copy had gained a paragraph;
- **`stale_copy_verdicts`** needs HEAD's blob as a base and an untracked path has none. Asked
  anyway it answers `NO_BASE`; asked about this one it answered *"this control has no reader for
  .md files"*;
- so `advance_shared_tree` **subtracted untracked non-twins out of its candidate set entirely** —
  the path did not even reach a refusal that named it.

A class that refills once per landing, standing in front of a fast-forward, with no member of it
ever resolvable. That is the 7.68-day wedge, and it is not the publisher's alone: a checkout five
behind means every daemon on this box executes superseded code.

## The repair — a fourth class, whose losslessness is MANUFACTURED and not found

`background/origin_reconcile.py`: `untracked_orphan_verdicts` and `preserve_untracked_orphans`,
wired into `advance_shared_tree` ahead of the clearing loop and inside the same tree lock.

The other three classes each rest on an argument that the bytes are **already** safe somewhere.
This one cannot — untracked means on no branch. So its safety is **built**: the bytes go to
`refs/preserved/origin-reconcile-orphan/<slug>` through a throwaway `GIT_INDEX_FILE` (the holder's
real index is never touched), and `verify_recoverable`'s **both** legs run — the blob under the
commit must hash to what is on disk, and the advertised `git log --all -S` lookup must actually
FIND the commit — **before a byte is removed**. A preservation that did not verify is a refusal
that has touched nothing.

And the path is not emptied. What stands there after the fast-forward is origin's copy of the same
document, which is why this supersedes a draft by the landed version of itself rather than deleting
a lane's work to buy a fast-forward.

**Tracked holder work is unchanged and still refuses everything.** That is the boundary, and it has
its own control.

## A control this contradicted, corrected beside the claim rather than quietly

`test_a_twin_whose_bytes_differ_is_never_deleted_and_never_advanced_over` asserted
`advanced is False` over exactly this shape, on the property *"a local file that is NOT what origin
holds is somebody's unlanded work: it must survive, and the fork must stay open."*

Right about the first half; the second half is what pinned the wedge. It is rewritten as
`test_an_untracked_draft_origin_also_adds_survives_on_a_ref_and_the_fork_closes`, which asserts the
part that mattered — the bytes survive and come back through the advertised route — and the old
wording is kept verbatim in the new docstring beside what replaced it. A new null,
`test_an_untracked_file_origin_does_not_touch_is_never_preserved_or_removed`, holds the boundary
the old leg was over-serving.

## Mutation results, including the three that did not fire

Nine legs in the new suite, six mutations fire. **Three did not, and each was established rather
than assumed to be the flattering answer:**

- **A MISSING TEST.** Widening `untracked_only` to every blocking path left the file 9/9 green: the
  fixture's verdict function answers `False` for anything not in its hard-coded list, so it gave
  the right answer to a question the caller should never have asked. The control now records which
  paths were **offered** to the class, not only which were approved, and the mutation reds.
- **TWO EQUIVALENCES, now stated in the docstrings that claimed them.** Dropping `-p HEAD` from
  `commit-tree` does not break the `-S` route — a parentless commit diffs against the empty tree —
  so the parent buys a readable `git show`, not reachability; the firing mutation is dropping
  `update-ref`. And the missing-path refusal is held by three independent gates (`hash-object` rc,
  `update-index` rc, the read-back loop); no single-site mutation defeats it and all three together
  do.

## What is still owed, and it is not this class

`git rev-list --count HEAD..origin/main` is **not yet 0**. The orphan class is closed; the tracked
holder copy at `tests/tools/test_fold_noise_floor_family.py` still holds the tree and the all-or-
nothing rule correctly refuses the whole advance while it stands. That copy is stranded work from a
dead 19:07 invocation and it needs **landing**, not displacing — `isolate_hunks --survey` over it,
landing only the hunks that add without deleting what `471dfd417` put in the same file. That is the
next item and it is a different class from this one; conflating them is what would license
displacing holder work.
