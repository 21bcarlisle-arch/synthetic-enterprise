**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# A rewrite deleted the binding repair and left its nine controls red, so every promotion since 09:03 bound NOTHING

**Found:** 2026-09-06, delivery seat, live, on the promotion of an unrelated landing. Repaired in
the same turn. Class: `controls_that_cannot_fail` — except that these controls *could* fail, did
fail, and nobody was looking.

---

## What it looked like from the seat

```
promoted 5b8f79767 -> origin/main (1 path(s), from a6bcf76a0)
bound NOTHING to the-r1-ceiling-is-a-selected-maximum-published-as-a-bound:
  the binding could not be attempted (TypeError: record_landing() got an unexpected
  keyword argument 'since')
```

The push succeeded. The binding did not. **The turn is judged on whether the bound paths moved on
the shared tree, so a promotion that binds nothing is logged `LANDED NOTHING` and the item is
re-offered however much landed** — the exact shape of
`feedback_landed_but_unbound_gets_swept_and_redrawn`, arriving through the one door built to
prevent it.

## The cause, in two commits

| commit | what it did |
|---|---|
| `b06fa3528` (09-05) | repaired the promote seam: passes the pre-push `origin/main` as `since`, and added `since` to `_commit_facts` / `record_landing` / `refusal_reason`. Landed **with** `tests/tools/test_the_promotion_seam_binds_the_landing.py`. |
| `424818d56` (09-05) | repaired the standalone `--landed`: added `_merge_base_side` and the `--since` CLI flag. Landed **with** `tests/background/test_the_standalone_landed_binds_this_lanes_paths_not_the_other_sides.py`. |
| **`9b08d302f` (09-06 09:03)** | *"dispatch is the claim"* — rewrote `background/delivery_lane.py`, **297 lines changed, 151 deleted**, and took `_merge_base_side`, every `since` parameter and the `--since` flag with it. The two test files stayed. |

This is the class already on the map as *a merge adopting one side's rewrite deletes the other's
purely additive work* — here without a merge: one lane's whole-file rewrite, landed green, silently
reverting two of yesterday's repairs.

**Nine controls went red at 09:03 and stood red for the rest of the day**: six in the standalone
file, three in the promotion-seam file. Proven by poison round rather than assumed — removing
`since` from `record_landing` again reds exactly those three, so the seam control is not blind, it
was simply never run after the rewrite.

## Why nothing noticed, and this is the part worth keeping

**The landing gate's pytest selection is path-scoped.** `9b08d302f` touched
`background/delivery_lane.py`, `background/worker_tick.py` and its own new test — and the two suites
that specify the deleted mechanisms live under `tests/background/` and `tests/tools/` with names
that match neither. My own landing an hour earlier touched none of `background/`, so it never
selected them either. **A whole-file rewrite is exactly the change least likely to select the tests
of the things it deleted**, because the deleted thing's tests are named after the deleted thing.

The live symptom was equally quiet: `_bind_to_claim` catches broadly, by design —
*"a bookkeeping failure must not cost a landing"* — so the `TypeError` became one line of output on
a command whose headline said `promoted`. Correct design, and it means the only reader who can
catch this is a human looking at the second line.

## The repair, landed here

- `_merge_base_side(commit, parents)` restored, and it still **refuses rather than falling back**:
  a merge whose parents are both ancestors of `origin/main` (every merge, once pushed) and a tree
  with no readable `origin/main` both return no base and a reason naming both candidate sides by
  sha, plus the two ways out.
- `since` restored on `_commit_facts`, `record_landing`, `refusal_reason`, and `--since` on the CLI.
- The local `since` in `record_landing`/`refusal_reason` — a float — is renamed `first_drawn`, since
  it now shadowed a `str | None` parameter of the same name. That collision is how a later reader
  reintroduces this.
- All nine controls green. The 13 tests across both files pass.

## What it does NOT fix

The path-scoped selection. A rewrite that deletes a mechanism still will not select the mechanism's
own tests, and the next instance of this class will look identical. The smallest thing that would
have caught it is not a new register: it is that **a commit deleting a `def` should select the
suites that name it**. Filed as the finding rather than built, because it belongs to whoever owns
the gate's selection and building it here would be a second writer to that seam.

**Verify before trusting this write-up:** `git show 9b08d302f -- background/delivery_lane.py | grep
'^-.*_merge_base_side'` returns the deleted definition; `python3 -m pytest
tests/background/test_the_standalone_landed_binds_this_lanes_paths_not_the_other_sides.py` was 6
failed at `9b08d302f` and is green at this commit.
