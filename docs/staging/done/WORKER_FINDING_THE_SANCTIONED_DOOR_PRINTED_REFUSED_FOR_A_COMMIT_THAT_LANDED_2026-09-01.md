# [WORKER FINDING] The sanctioned door printed REFUSED for a commit that landed, for a quarter of an hour at a time

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted
**Found:** 2026-09-01, by the delivery seat, on its own landing of `396bb09ba`.

## Class registration

Belongs to `uncommitted_and_orphaned_work`.

## What happened

    [surgical-land] REFUSED: the commit LANDED but refreshing the index for its paths failed
    rc=128: ...index.lock': File exists.

The commit was on HEAD. `git log --oneline -1` returned it. The tool reported a refusal for work
that had shipped, and the sentence contradicts itself inside its own first clause.

The mechanism: after `commit-tree` + `update-ref`, `_refresh_index_for` brings the shared index into
line for the landed paths. That call took `.git/index.lock`, which another lane's `git commit` was
holding, failed once, and raised **`LandingRefused`** — the same exception type the tool raises for
a **RED GATE**.

## Why it matters more than a confusing message

`land()`'s documented contract is *"returns the new commit sha, or raises LandingRefused"*, and the
whole safety argument of the module rests on that being trustworthy. A caller keying on the type
concludes the work is unlanded and then does one of two harmful things:

* **re-lands it** — a second commit whose tree is already the parent, i.e. an empty duplicate with a
  full duplicate message; or
* **reports failure for work that shipped** — which is a false claim in the direction this project
  cares about most.

And a human reads the word REFUSED. I only caught it because I checked HEAD out of habit; a bounded
turn that trusted the verdict would have re-run the landing.

**The window is not a rare race.** The lock is held by another lane's `git commit`, and a commit
here is ten to fifteen minutes of gate. So this failure was available for roughly a quarter of an
hour every time any lane committed, on a tree with six concurrent lanes. The instance that produced
this document cleared after **75 seconds** of waiting.

## The second half: the index is left claiming a deletion

While unrefreshed, the shared index still holds the PARENT's content for those paths — so
`git status` shows the landing as a staged **revert**, and any index-based commit by any lane would
un-land it. Measured immediately after the failure:

    git diff --cached --stat -- <my three paths>
    3 files changed, 252 deletions(-)

252 deletions staged, of work that was on HEAD. Nothing but the tool's own printed hint stood
between that and a lane running `git commit`. That hint is good behaviour; it is not a mechanism.

## The repair, landed with this

1. **`_refresh_with_retry` outlasts the lock holder**, bounded by a wall-clock deadline it cannot
   outlive. It runs *after* the commit is on HEAD, so waiting costs nobody anything, and the holder
   is by construction a process that will finish. Only a **held lock** is retried — identified from
   git's own message, not from `rc=128`, which also covers a corrupt object; retrying a real error
   would turn one bad landing into twenty minutes of silence.
2. **`IndexNotRefreshed`**, a `LandingRefused` subclass carrying the landed `sha`. Existing
   fail-closed handlers keep working; a caller that wants the truth can now get it; the message
   leads with THE COMMIT LANDED and ends with *do NOT re-land*.

Proof: `tests/tools/test_a_landed_commit_is_never_reported_as_refused.py`, five legs, including both
directions of the retry rule and a leg keyed to the call sites so a refactor cannot silently drop
the sha and leave every message saying "(sha unavailable)".

## Why it is `uncommitted_and_orphaned_work`

The class is about work that finishes and does not become part of the tree. This is its mirror at
the same address: work that **did** become part of the tree and was **reported as though it had
not** — and which the shared index was simultaneously staged to remove. Both halves end with a
correct commit that a later reader believes is absent.

## What is not claimed

The original code was not careless. It refuses rather than continuing quietly, it names the exact
repair, and its docstring is explicit that leaving the index alone would be corruption rather than
courtesy. The defect is narrow: it used one exception type for two opposite outcomes, and it did not
wait for a lock whose holder it knew would finish.
