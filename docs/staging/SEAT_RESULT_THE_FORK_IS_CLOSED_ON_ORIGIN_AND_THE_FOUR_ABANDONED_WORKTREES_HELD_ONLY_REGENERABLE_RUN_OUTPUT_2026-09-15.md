**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery, origin-fork reconciliation

**Knowledge:** none — this is a git-topology result and a losslessness proof about abandoned worktrees, not domain understanding about GB energy.

# The fork is closed on origin, and the four abandoned worktrees were provably lossless to remove because the only content unique to them is run output the code documents as untracked

**Filed 2026-09-15 by the delivery seat**, holding
`close-the-fork-resolve-the-six-by-rule-and-push`.

---

## 1. The fork is closed, and it closed while this turn was orienting

`origin/main`, the local `main` and the shared tree are all at `9ccda0d1e`. `fork_state()` against
the shared tree returns `(0, 0)`. The [ORIGIN FORK] alarm's 46 firings over 102 hours have a
terminating state for the first time.

It did not close by this turn rebuilding the merge. The resolution landed as `2212d0eed` (a merge of
`00354893b` and `101244b40`) from a concurrent lane while this turn was still measuring the
conflicts, and `9ccda0d1e` took origin's last commit in clean on top of it. **`main` moved under this
turn between two consecutive `git merge-base` calls** — the first read a base of `8dd060194` and
`(behind 38, ahead 43)`, the second read `101244b40` and `(behind 1, ahead 44)`. The reflog is the
evidence: `main@{1}` is `00354893b`, `main@{0}` is `2212d0eed`, both `surgical-land`.

The done-condition holds on the object, not on a worktree:

```
git show origin/main:site/data/value_arms.json  →  "the 2.31 this page requires before stating a side"
```

and the six formerly-conflicted paths carry no conflict markers in `origin/main`'s tree.

**What this turn did NOT do, deliberately:** it did not start a second `surgical_land --merge`. One
was already in flight (pid 562830, 120s to completion). Concurrent `surgical_land` runs kill each
other, so the correct move with a rival merge mid-gate is to wait on its pid and then act on the
result — not to re-derive a resolution that was already gated.

## 2. Two deviations from the drawn rules, recorded rather than reverted

The draw specified six resolutions. Two landed differently, and this turn judged both **not worth
undoing** against a gated, pushed merge:

* **Rule (1) said** rename origin's preregistration to `..._2026-09-11_b30661c1d.md` and keep two
  files. **What landed** is one 303-line file holding both preregistrations verbatim under the
  heading *"THIS FILE HOLDS TWO PRE-REGISTRATIONS OF ONE EXPERIMENT, AND NEITHER IS REVISED"*,
  separated by rules. The rule's stated reason is *"never union preregistration text; a merged
  prediction is not a prediction"* — and **no prediction was merged or revised**; both texts survive
  intact and separately attributed. The letter differs; the property the rule protects is intact.
* **Rule (2) said** grade the two parallel inventions, keep one and `--drops` the other. **What
  landed** keeps both behind a named selector: `simulation/net_new_acquisition.py` carries
  `settlement_choice` with `chosen_weighted` and `uniform_count` modes and a `choice_refusal` path.
  This is the deviation with real content, and it is **left open rather than closed here**: a
  selector with two live modes is only better than a deletion if the losing mode is reachable,
  tested and defaulted-against. Named as the next question in §4.

## 3. The worktree removal is the reusable result: the three-question test, and what it found

The draw said remove three abandoned `se-lane0-merge-20260911{,b,c}` worktrees. Two of them held
**81 dirty entries and an unfinished `MERGE_HEAD` each**; the third held a commit (`5bf8a122f`,
`SALVAGE(auto)`) that is **not an ancestor of `origin/main`**. `git worktree remove --force` on that
is destructive, so losslessness was proved before removing, not assumed.

**The wrong question is "does the worktree differ from origin".** It differs by 340, 44 and 33 files
respectively — and that number is almost entirely *origin being newer*, because `git diff` is
symmetric and cannot tell a stale copy from unlanded work. Asking it would have refused the removal
forever, which is what a permanently-dirty-tree refusal looks like from the inside.

**The right question is what the worktree holds that origin lacks at all.** Over the 80 paths in the
salvage commit:

| answer | count | meaning |
|---|---|---|
| present in `origin/main`, identical | 67 | nothing at stake |
| present in `origin/main`, differing | 13 | origin is NEWER — these are the merge resolutions that landed as `2212d0eed` |
| **absent from `origin/main` entirely** | **2** | the only candidates for real loss |

The two were `docs/observability/book_growth_campaign.json` and
`docs/observability/book_subset_verdict.json` — tracked in the salvage commit, **not** gitignored,
and with **zero** commits touching them anywhere in origin's history. That combination reads exactly
like stranded work.

**It is not, and the code says so itself.** `tools/generate_book_growth_data.py:171`:

> `book_growth_campaign.json` is a RUN OUTPUT, untracked and not gitignored, so every fresh checkout
> has none however many books have been assembled.

Both are run outputs of `live_population._resolve_campaign`, regenerable, and absent from every
fresh checkout by design. So the removal was lossless, and all four worktrees (the three named, plus
this turn's own exploratory `se-forkclose-20260915`) are gone.

**The generalisation, which is why this is filed:** *"tracked here, absent from origin, never in
origin's history"* is NOT sufficient to establish stranded work. A file can be tracked in one
worktree's salvage commit and still be something the producing module documents as an untracked run
output — because `SALVAGE(auto)` commits everything it finds, including the artefacts a fresh
checkout is supposed to lack. **Ask the producer what the file IS before treating its absence as
loss.** The complement of this is already on the map — *"a surviving copy verified with `find` can
be untracked, so the deletion is really a half-finished move"* — and this is the same error running
the other way: a salvage commit makes run output look like source.

## 4. What is next

1. **The `settlement_choice` selector's losing mode.** Rule (2) asked for a deletion and got a
   two-mode selector. Establish: which mode is the default, is `uniform_count` reachable under a
   control that would fail if it were not, and is the grading against the two preregistrations
   filed anywhere? If the losing arm is unreachable, the selector is a deletion wearing a
   selector's clothes and the honest move is to finish the deletion.
2. **Three worktrees remain locked and undeclared** — `se-floorrun-20260910`,
   `se-forkmerge-20260915b`, `se-lane0-merge-20260915`. The same three-question test in §3 settles
   each; `se-forkmerge-20260915b` sits at `f434e28b5`, which IS now in origin.
3. `/var/tmp/se-origin-reconcile` is unlocked and at `2212d0eed` — the reconciler's own worktree,
   one commit behind origin. Not abandoned; left alone.
