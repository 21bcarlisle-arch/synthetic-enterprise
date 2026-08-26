**Severity:** LATENT · **Lane:** H_harness

# A pathspec protects other lanes from my index. Nothing protects them from my stale copy of a shared file.

**Found:** 2026-08-18, landing `SITE4` (commit `8a3e002d6`). Caught before it did damage —
but by hand, on the fourth commit attempt, not by any mechanism.

**Class:** `uncommitted_and_orphaned_work` — the shared-tree family.

---

## The rule as written, and the half it covers

`CLAUDE.md`, concurrent writers:

> `git add` untracked paths under the lock, then commit UNLOCKED by pathspec — **the
> pathspec, not the lock, prevents the sweep.**

That is true and it works. A pathspec commit takes only the named paths, so another lane's
*staged* work is never swept into my commit. `tools/surgical_land.py` hardens the same
property further, using a throwaway index so the caller's real index is never opened.

Both mechanisms protect other lanes **from my index**. Neither protects them **from my own
working copy of a file we both edit.**

## What actually happened, observed-with-evidence

1. 07:30 — this session appended the `SITE4`–`SITE11` mint to `docs/design/maturity_map.yaml`
   and held the file open across a long build.
2. 08:23 — a concurrent lane landed `6ed24044d`, which edited **the same file**. That lane
   went to real trouble to protect this one: its commit message records swapping the map to
   "HEAD-plus-that-line for the gate window, so the `SITE4..SITE11` mint another lane holds
   STAGED in this file is not swept into this commit."
3. The protection was **one-directional**. This session's working copy was now HEAD-minus-57
   lines. `git diff HEAD -- docs/design/maturity_map.yaml` showed **57 deletion lines**: that
   lane's `SITE2` Expert-Hour notes, its count changes, its narrative rehoming — all of which
   a pathspec commit would have reverted, correctly and silently, because a pathspec commits
   the *working tree* version of the paths it names.
4. Caught only because the fourth attempt diffed the pathspec against everything that had
   landed since the session's starting HEAD. The mint was re-applied on top of HEAD's version
   and the diff became pure addition, 0 deletions.

**Nothing in the toolchain reported this.** Not the pre-commit gate, which judges the tree the
commit creates and has no opinion on whether that tree silently reverts a committed line. Not
`surgical_land`, which is about the index. Not `git`, which has no concept of "stale" for a
file the caller never conflicted on.

## Why the existing controls cannot see it

The gate's subject is *"the tree `HEAD` would become if exactly the named paths were
committed"* — and that tree is perfectly valid. Every test passes on it. It is a coherent
repository state. It just happens to be one in which another lane's committed work has been
deleted by a file that predates it.

That is the signature of this class: **no state is corrupt, so no checker fires.** The same
shape as `WORKER_FINDING_THE_SITE_LANE_GATES_THE_WORKING_TREE_NOT_THE_COMMIT` and
`WORKER_FINDING_THE_PRECOMMIT_GATE_VALIDATES_THE_TREE_NOT_THE_COMMIT` — a scope mismatch
between what is checked and what is at risk — but on a new axis: not index-vs-tree, but
**tree-vs-elapsed-time.**

## The exposure is proportional to how long a draw holds a file

Long draws are the norm here, and the commit gate itself makes them longer: the nine-gate
chain runs past ten minutes per attempt, so a single contested landing can hold a shared file
open for the better part of an hour. `docs/design/maturity_map.yaml` is the worst case — 314
atoms, edited by every lane, and the one file a mint, a level move and a simplification count
all have to touch.

## What would close it (none built; this is QUEUED, not fixed)

A check with the right subject: for every path a commit names, if `HEAD` moved since the
working copy was last synced with it, the commit must show **zero deletions** against `HEAD`
for that path — or state, in the message, which deletions are deliberate. One `git diff HEAD
-- <paths> | grep '^-'` away from being mechanical, which is what makes leaving it as prose
indefensible under MAKE_IT_STICK.

Two properties it must have, from the two near-misses this class has already produced:
- It must fire on a **committed** line disappearing, never on an uncommitted one — otherwise
  it red-lists every legitimate partial commit on this tree, which is most of them.
- It must be **answerable**: a deliberate revert is a real act, so the escape is a stated
  reason in the commit message, not a flag.

`SITE4`'s own commit message carries that statement by hand today (the rebase and the carried
`SITE2` count line are both named in it). By hand is exactly the property that decays.

## Not claimed (R9)

- No damage occurred. The revert was caught pre-commit; `8a3e002d6` diffs as pure addition.
- Whether any PAST commit on this repo silently reverted a shared line this way was **not
  checked**. That audit is the obvious next question and this document does not answer it.
- The concurrent lane's own conduct was correct and better than required — it protected this
  session's staged work explicitly. The gap is that its care could not be reciprocated by any
  mechanism, only by a hand-diff that nearly did not happen.
