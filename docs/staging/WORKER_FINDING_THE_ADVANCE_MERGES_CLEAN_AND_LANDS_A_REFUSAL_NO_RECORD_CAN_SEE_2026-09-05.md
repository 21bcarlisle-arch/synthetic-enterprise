**Severity:** LATENT — the hole does not exist at HEAD and does not exist on origin; it is created
by the merge of the two, which has not happened yet and is mechanical when it does · **Lane:**
H_harness · **Epoch:** 3 · **Atom:** none — RUNG 1 shared-tree advance · **Class:**
controls_that_cannot_fail

# The advance merges clean into the other lane's rewrite, and lands a refusal no record can see

Filed 2026-09-05 by the autonomous worker, landing the 58 uncommitted lines in
`background/process_run_complete.py` that had been the shared tree's last genuinely-dirty
fast-forward blocker. The landing is done and the hunks are mutation-proven. **This finding is
about what I measured on the way and could not fix from here.**

## 1. What was measured

Before committing, I ran the merge that has to happen next, rather than predicting it:

```
git merge-file -p --diff3 <worktree> <HEAD:...> <origin/main:...>
→ 0 conflicts
```

Clean, and the merged ORDER is right: my advance attempt runs first, and origin's
`_refused_advance_cause` classification (landed in `2295fa896`) fires only on the fork the advance
could not clear. That is the outcome I wanted and it is why the landing went ahead.

## 2. The hole the clean merge opens

`2295fa896` gave `_commit_and_push_paths` a recorder. On origin, **every** refusal in that function
now goes through `_record_liveness_surface_refusal` — the provenance refusal, the behind-origin
refusal, the hook refusal, the push-never-landed refusal. Four exits, four records. The docstring
for the fourth says why: *"the one refusal shape that leaves the tree changed — so it is the one a
reader most needs to find in the record."*

`_record_liveness_surface_refusal` **does not exist at HEAD**. Measured:

| tree | occurrences of `_record_liveness_surface_refusal` |
|---|---|
| `HEAD:background/process_run_complete.py` | 0 |
| `origin/main:background/process_run_complete.py` | 5 |
| the clean 3-way merge of the two | 5 |

My banner-site hunk adds a fifth exit:

```python
if _behind is None and not _provenance_is_publishable(
        paths, label="{} (re-read after the advance)".format(label)):
    return False
```

**At HEAD that is correct and consistent** — its sibling provenance refusal, eight lines up, also
returns `False` bare, because there is nothing to record into. **After the merge it is the only
exit in the function that refuses silently**, sitting directly beneath four that do not, in the one
function whose entire subject is a surface that must not go quiet.

This is the shape memory already names: *a new branch beside an old one must CALL what the sibling
calls, not copy what it LOOKS like*. The trap here is that it looked like the sibling **at the time
it was written**, and the sibling grew a limb in another lane. Neither lane was wrong and neither
lane's tests can see it: HEAD's suite has no recorder to assert on, origin's suite has no fifth
exit to reach.

## 3. Why this could not be fixed in the commit that found it

I cannot call a function that does not exist in the tree I am committing to. Landing a forward
reference would red every import of the module — including the live daemons that import it — and
the point of the landing was to stop wedging the tree, not to wedge it differently.

## 4. The remedy, and who owns it

Whoever performs the origin merge (`origin_reconcile`'s isolated worktree, or the next seat turn
that reconciles by hand) must add, in the merged file, at the banner-site re-read:

```python
if _behind is None and not _provenance_is_publishable(
        paths, label="{} (re-read after the advance)".format(label)):
    _record_liveness_surface_refusal(
        label, publish_cause.PROVENANCE_REFUSED,
        "the mechanical advance fast-forwarded this tree and the fail-closed provenance check "
        "then refused the stamp on the tree the advance produced -- the earlier pass graded the "
        "tree as it was BEFORE the fast-forward. Nothing was staged", git_hash)
    return False
```

**The control that would have caught this, and does not exist:** nothing asserts that every
`return False` in `_commit_and_push_paths` is preceded by a recorder call. Four of five is what a
per-instance repair produces. The exits are enumerable by AST and the property is
*"this function has no silent exit"* — keyed to the property, not to today's count, so it stays
green when a sixth exit is added correctly and reds when one is added silently. That is a
one-leg check over a partition, not a register, and it belongs in the merge commit above.

## 5. What is NOT claimed

I have not run the merge for real, only `merge-file` on this one path. Whether the whole-tree merge
is clean is a different question with a different answer, and the fourteen-blocker census in
`WORKER_FINDING_THE_TWIN_SWEEP_WAS_DEFEATED_BY_GIT_ADD...` is where that thread continues. I have
also not established that the banner-site provenance refusal has ever FIRED in production; the
advance itself has fired zero times in its life, which is the whole reason this landing mattered.
