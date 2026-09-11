**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `union-the-departure-routes-and-declare-the-denominator`

# The sanctioned merge route advances HEAD past the working tree, and arms a silent revert in every file it brings forward

**Found 2026-09-02, worker tick, on myself, immediately after using the route CLAUDE.md names as the
legal one.** Not a defect in `surgical_land` — a consequence of what makes it safe, which nothing
currently discloses at the call site.

## What happened, in order

1. I landed `ae8e2ec3f` by pathspec. `git push` was rejected: origin carried two commits I did not
   have, one of them `6a5dc5251`, on the same subject (the level anchor's accountability).
2. CLAUDE.md's wall is explicit that a hand-built merge is never a judgement call and that
   `python3 -m tools.surgical_land` is the legal move. I used `--merge origin/main`. It landed
   `fd6e21132`, gated. Push succeeded, `HEAD...origin/main` verified `0 0`.
3. I then re-ran the two subject suites and got **56 passed, 2 xfailed** — *identical* to the
   pre-merge count, despite having just merged a commit that added 102 lines to
   `tests/architecture/test_switching_rate_commons.py`.

That identical count is the only thing that gave it away, and it is a weak signal: had origin's
commit added no test, or had I not happened to know its line count, nothing would have shown.

## The mechanism

`surgical_land` computes every tree in a **throwaway index and a throwaway checkout**
(`GIT_INDEX_FILE`, `tempfile.mkdtemp(prefix="surgical-land-")`). Its own docstring says so, and that
is precisely what makes it the safe landing move: the shared index is never opened, so another lane's
staged work cannot be swept into the commit.

**For `--merge`, the same property means the shared working tree is never updated.** `git merge`
would have written the merged content into the worktree. This does not. So after a successful
`--merge`:

* `HEAD` and `origin/main` agree and the push verifies clean — every check I ran said "landed".
* The **working tree** still holds the pre-merge content of every file the merge brought forward.

Here the worktree copy of `test_switching_rate_commons.py` was **89 lines behind HEAD**, missing
`_capture_anchor_column` and `test_the_capture_the_band_verdict_is_read_from_was_produced_by_the_live_anchor`
entirely.

## Why this is the armed-silent-revert shape and not just staleness

The next lane to commit that file **by pathspec** — the practice CLAUDE.md mandates, precisely to
avoid sweeping others' work — commits the worktree copy, and silently deletes origin's leg. The
pathspec discipline that protects against `-A` is what delivers the revert here. Both halves are
correct practice and the composition is the defect.

**And it is worse than a plain revert, because neither side was a superset.** The worktree also held
13 lines of *another lane's uncommitted* prose (the "SIX ABOVE AND ONE BELOW" direction correction on
the band leg's `xfail` reason) that HEAD does not carry. So:

* `git checkout <path>` — already a forbidden move here — would have destroyed that lane's work.
* Committing the worktree would have destroyed origin's leg.

This is the catalogued *a working tree file can hold a newer table and an older function, so neither
revert nor land is right*. It was resolved by composing: HEAD's content with the 13 uncommitted lines
re-applied, verified by `git diff HEAD --stat` reading **13 insertions, 0 deletions**. The worktree is
now a strict superset of HEAD and nothing is armed. Suite went **56 → 57 passed, 2 xfailed**; both
`xfail`s untouched. The pre-disarm worktree blob is preserved at
`refs/preserved/commons_worktree_20260902` rather than discarded.

## What I did NOT do

I did not commit the 13 prose lines. They are another lane's in-flight work and the worktree is the
right place for them; leaving them uncommitted and additive is the state that loses nothing.

I did not change `surgical_land`. Its isolation is the correct design and the one thing here that
must not be traded away — updating the shared worktree from inside the landing tool would reintroduce
exactly the sweep it exists to prevent.

## What is owed

**The disclosure, not the behaviour.** `--merge` returns `landed MERGE <sha>` and says nothing about
the worktree. The cheap, honest fix is for `--merge` to report which worktree paths now differ from
the commit it just made — it already knows both trees — so the operator is told to reconcile instead
of discovering it from a suite count that did not move. A control keyed to the property: **after a
`--merge`, no path in the merged commit may be behind the worktree copy without being named in the
tool's own output.**

**Not fixed in this tick and named rather than swept.** I am a bounded invocation and this needs the
tool's own tests. Filed LATENT because the instance is disarmed and the mechanism recurs on the next
`--merge` any lane runs — which, given the tree's landing cadence, is soon.

## Scope, stated because the last three findings on this thread each needed it

This is about `--merge` only. The pathspec path (`surgical_land` with positional paths) commits
content the worktree already has, so it does not advance HEAD past the worktree and does not carry
this shape.
