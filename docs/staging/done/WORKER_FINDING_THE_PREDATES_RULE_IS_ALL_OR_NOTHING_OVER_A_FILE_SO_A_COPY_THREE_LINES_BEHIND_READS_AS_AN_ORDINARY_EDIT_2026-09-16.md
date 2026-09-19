**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — reconcile-must-drain-what-it-already-proves-lossless)

# The PREDATES rule is all-or-nothing over a whole file, so a copy three lines behind reads as an ordinary edit

**2026-09-16, scheduled tick, worker seat.**

## The defect

`tools/stale_copy_refusal.py`'s `judge()` decides "this copy predates the last landing here" by
asking whether the copy holds **none** of that landing commit's distinctive lines:

```python
distinctive = distinctive_lines(root, path, commit)
present = {ln.strip() for ln in new_text.splitlines()}
if not any(d in present for d in distinctive):
    return Loss(path, PREDATES, ...)
```

`distinctive_lines` is computed over the landing commit's **whole file**, not over the region that
commit changed. A landing that touched one function in a 700-line test file contributes 50-odd
distinctive lines, and a rival working copy that is three lines behind holds nearly all of them —
so `any(...)` is True and there is no complaint.

The rule therefore fires only for a copy that predates the *entire* landing. The copy the tree
actually grows — a lane's working copy left behind by its own `surgical_land --content`, which
deliberately does not write the working tree — is behind in the landed region only, because the
lane had pulled earlier landings into the rest of the file. It reads as an ordinary edit.

## Measured

Two live instances, both left by landings that are ancestors of `origin/main`:

| path | mtime | behind by | last landing | distinctive lines | any present | verdict |
|---|---|---|---|---|---|---|
| `tests/design/test_maturity_map_contract.py` | 2026-09-06T16:14 | 3 lines | `7991a4023` | 52 | **True** | no complaint |
| `tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py` | 2026-09-10T12:28 | 18 lines | `a509056aa` | 64 | **True** | no complaint |

The second rule cannot see them either. `symbols()` is function/class granularity: the first copy
differs by a frozenset member, the second by a local variable and a docstring. Neither is a name,
so `after < before` is False.

Consequence: `tools/refresh_to_head.py` refuses both with `refused_head_does_not_supersede_it`, and
`background/origin_reconcile.py`'s new third leg — which delegates to exactly that judgement —
cannot drain them. They will refuse the next fast-forward this tree needs, as they have since
2026-09-06.

## Why the refusal is nonetheless the right one today

`judge()` having a complaint is the precondition that stops `refresh_to_head` being `git checkout
<path>` with a nicer name, which is a wall here. Deleting or loosening it without a replacement
proof would turn a fail-closed refusal into a fail-open sweep over every lane's working copy. The
refusal is honest; it is the *proof* that is missing, not the *guard* that is wrong.

## Two candidate proofs, both refuted by measurement

- **Ancestor-blob equality** — is the working copy byte-equal to this path's blob in some ancestor
  of HEAD? Neither path matched in the last 400 commits touching it. `tools/isolate_hunks.py`
  builds HEAD-plus-your-hunks, so the committed blob is (HEAD-at-land-time + hunks) while the
  lane's copy is (older base + hunks). They are never equal by construction.
- **Three-way containment** — `git merge-file` with base `L^`, ours = worktree, theirs = HEAD. rc=0
  for both, and the merged result is **not** HEAD's blob: the lane's copy forked from a base far
  older than the landing's parent, so the region reads as "ours changed it". The correct base is
  the state the lane forked from, which the tree does not record.

## The shape of a repair

Make `PREDATES` **region-aware**: ask whether the copy holds none of the distinctive lines the
landing commit ADDED *in the hunks it changed*, rather than none of the distinctive lines in the
whole resulting file. That is the property the rule is named for, and the current implementation is
a coarser predicate standing in for it.

This is a change to a control that guards every landing in the repo, so it wants its own turn,
its own mutation proof over both directions (a copy that should now be caught, and an ordinary edit
that must still not be), and a re-run of `tools/stale_copy_refusal.py --census` before and after to
show which of the standing refusals move. It is not a change to make in the same turn that wires
the consumer.

## Reversal

Nothing about this finding is in force. The consumer wired this turn fails closed on exactly these
paths; if the repair above is wrong, the state it returns to is today's.
