**Severity:** INFO · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Pre-registration: what I expect to find when I grade the shared checkout's fast-forward blockers

Claim id: `enact-the-fast-forward-now-that-rule-1b-opens-the-comment-revert-door`.
Written 2026-09-24 18:10 BST, **before** running any blocker census. Measured state at writing,
which is not a prediction because it is already read:

```
deploy_restart.checkout_drift('/home/rich/synthetic-enterprise')
  -> {'behind': 28, 'ahead': 5, 'contains_origin': False, 'gap_paths': 48}
shared HEAD                        ffa14f065
origin/main                        193fa7caa
git show HEAD:tools/stale_copy_refusal.py | grep -c reverted_comment_block   ->  0
```

**Rule 1b is INERT on the shared tree.** The commit that carries it is not an ancestor of the
shared checkout's HEAD. The drawn item said to check exactly this and said what follows if the grep
is zero: advancing the checkout is the whole job, not a precondition to it. It is zero.

## The predictions

1. **The binding refusal is DIVERGENCE, not any working-tree path.** `advance_shared_tree` asks
   `commits_ahead` first and refuses on it; at `ahead == 5` no path class is reached at all. So
   grading the 48 gap paths cannot, on its own, make the tree advanceable. I predict
   `advance_shared_tree(dry)` refuses with a diverged reason and `cleared == []`.

2. **The ahead leg is being closed right now by another process, not by me.** `origin_reconcile`
   has a `surgical_land --merge origin/main` in flight (pid 2362783, started 17:56, its gate
   pytest running). If it pushes, the shared tree's 5 commits become ancestors of origin/main and
   `ahead` goes to 0 without anything of mine. I predict I will observe `ahead` fall to 0 and
   `behind` GROW, because the merge commit it pushes is itself a new commit the checkout lacks.
   That is the shape already in this seat's memory — the ahead leg closes and the behind leg grows,
   so `contains_origin` stays false for the opposite reason.

3. **The comment-revert path grades `refreshable` and rule 1b is why.** For
   `tests/background/test_a_swept_row_names_the_sibling_that_holds_its_windows_commit.py` I predict
   `stale_copy_refusal` returns a verdict naming `reverts_a_landed_comment_block`, and that the
   same path graded against a `tools/stale_copy_refusal.py` WITHOUT rule 1b returns a refusal
   instead. Both arms, or the claim that rule 1b opened this door is untested — the door being open
   at origin says nothing about the door the shared tree's own code has.

4. **Blocker-class census.** Of the 48 gap paths I predict fewer than half resolve to one of the
   five blocker classes, and that the residue is dominated by `docs/observability/` dotfiles —
   daemon state, rewritten every tick. I am recording this because a residue count is the number I
   am most likely to talk myself into after seeing it.

## What would refute each

1 is refuted if `advance_shared_tree` reaches a path verdict at `ahead > 0`. 2 is refuted if
`behind` falls when `ahead` does. 3 is refuted if the no-rule-1b arm ALSO returns a verdict — that
would mean some other rule already saw this copy and rule 1b is not load-bearing here. 4 is refuted
by any census I then reinterpret rather than report.

## What this turn will NOT do

Clear another lane's uncommitted working copies in the shared tree by hand to buy a fast-forward.
`origin_reconcile` refuses that unattended for a reason, and my isolation from the shared index is
the only thing that makes this invocation safe to run at all. A verdict is a reading; enacting a
discard is a separate judgement, and rule 1b's own design says so by keeping
`reverts_a_landed_comment_block` out of `BASE_WINS_RULES`.
