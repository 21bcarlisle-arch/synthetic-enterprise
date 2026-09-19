**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — reconcile-must-drain-what-it-already-proves-lossless)

# The reconcile now drains a third class it can prove, and the two paths the item named are not in it

**2026-09-16, scheduled tick, worker seat.** The drawn item asked for three things and the tree had
already built two of them. The third is landed. The two live instances the item set as its mutation
proof are **still refused**, and the reason is a measurement, not a shortfall of effort: the proof
the item named does not reach the class it was drawn for. That is written up below rather than
worked around, because a remedy that cannot be shown to apply is the thing this queue keeps
refilling with.

## The premise, re-measured at turn start

| The item said | What the tree said |
|---|---|
| `identical_untracked_twins` "today only prints" | It has been **acting** since 2026-09-04: `advance_shared_tree` unlinks them under the tree lock. |
| `identical_tracked_twins` likewise | Acting since 2026-09-05, via `restore_tracked_twin`. |
| "(3) Refuse, loudly and by name, on everything left" | Already there — the `held` list. What it could **not** do is say *why* a path was held. |
| `background/launch_liveness.py` (+115/−49) must SURVIVE as a refusal | Spent. Its work **landed** as `8fc4b4c02`, and a lane then refreshed the copy (`61f9ebf7f preserved rival working copies before refresh-to-head: background/launch_liveness.py`). It has no diff against HEAD at all and is not a blocker of any kind. |
| `git rev-list --count HEAD..origin/main` must reach zero | Already **0** at turn start. The fork is closed; `origin_reconcile` prints `LEVEL: local and origin/main agree`. |
| The two stale test copies must refresh | **Refused.** See below. |

Both cited commits (`7991a4023`, `a509056aa`) are ancestors of `origin/main`, as the draw-time
premise check said. They are the *landings*, not the work — the item cited them as evidence of the
stale copies they left behind, and those copies are still on disk.

## What is new

`background/origin_reconcile.py` now asks a **third** question of the blockers the two hash proofs
could not take, and it asks it of `origin/main` rather than of HEAD:

- `stale_copy_verdicts()` — per tracked blocker, is this a rival working copy the tree it is about
  to hold strictly supersedes? The judgement is `tools/refresh_to_head.py`'s entire, not re-cut:
  supplies no name the base lacks (computed over both blobs), `stale_copy_refusal.judge` has a
  complaint, bytes preserved to a `refs/preserved/*` commit whose advertised `git log --all -S`
  recovery is **run** before a byte is destroyed.
- `refresh_stale_copies()` — the write, under the caller's tree lock, all-or-nothing with itself.
- `refresh_slug()` — keyed to HEAD. `git update-ref` *replaces*, so a fixed slug would make each
  advance's preservation delete the previous one's: the bytes go unreachable, the advertised
  recovery stops finding them, and nothing goes red until the run nobody has needed yet.
- The refusal now carries the **per-path reason**. "Not byte-identical to what origin brings" is
  equally true of holder work nobody may touch and of a file this tree has no reader for, and those
  want opposite acts.

`tools/refresh_to_head.py` gains a `base` parameter (`--base`). The judgement tree and the write
tree are now deliberately different: the question is asked of `origin/main` — the bytes the tree is
about to hold — and the bytes written are HEAD's, because what refuses a fast-forward is *worktree
differs from HEAD*. Writing origin's bytes would leave the path blocking.

## The two paths the item named are refused, and the refusal is honest

`tests/design/test_maturity_map_contract.py` (mtime 09-06, 3 lines behind) and
`tests/tools/test_the_within_year_remedy_is_indexed_on_decisions.py` (mtime 09-10, 18 lines behind)
are exactly the refill shape the item describes. Both fail precondition 2 —
`stale_copy_refusal.judge` returns `None`:

```
tests/design/...  last landing 7991a4023, 52 distinctive lines, ANY PRESENT: True  -> no complaint
tests/tools/...   last landing a509056aa, 64 distinctive lines, ANY PRESENT: True  -> no complaint
```

**The `PREDATES` rule is all-or-nothing over the whole file.** It fires when the copy holds *none*
of the landing commit's distinctive lines — a copy that predates the entire landing. These copies
predate the landing only *in the region it touched*; they carry 50-odd of its other lines because
their lane had pulled earlier landings. And the symbol rule cannot see them either: one changed a
frozenset member, the other a local variable, and neither is a name.

So the honest statement is: **the `surgical_land --content` refill is not, in general, provable by
the preconditions the item named.** It is provable for the sub-class where the copy predates the
whole landing, which is what the new leg drains. Widening `PREDATES` from "holds none of the
distinctive lines" to something region-aware is the next question, and it is a change to a control
that guards every landing in the repo — not something to bolt on in the same turn that wires it.

I also tested the two obvious cheap proofs and both are refuted:

- **Ancestor-blob equality** (is the worktree an older blob of this path reachable from HEAD?) —
  no match in the last 400 commits touching either path. `isolate_hunks` builds
  HEAD-plus-your-hunks, so the committed blob and the lane's copy are never equal by construction.
- **Three-way containment** against the landing's parent — `git merge-file` returns rc=0 and a
  result that is *not* HEAD, because the lane's copy forked from a base far older than `L^`. The
  right base is not knowable from the tree.

Filed as a finding beside this.

## Evidence

Ten controls in `tests/background/test_the_refill_that_no_landing_clears_was_refused_forever.py`,
against a real local tree behind a real origin (bare remote, two clones, real
`git merge --ff-only`). Reachability first: all three blocker classes asserted non-empty on one
tree before anything asserts what any of them does. Then the drain; then the preserved ref is the
one the refusal names; then the slug moves with HEAD; then **holder work survives** — a copy
carrying a name nothing upstream has is left byte-for-byte alone and refused by name with its
reason, because a run that sweeps it has become `git checkout <path>`, which is a wall here. Then:
one unprovable blocker holds the provable ones untouched; an ordinary value-level edit is not a
stale copy; an unreadable judgement refuses rather than clearing; a failed refresh leaves the twins
on disk. Last, the base control — the same copy is refused against HEAD and refreshable against
origin, which is the item's own correction made measurable.

117 pre-existing controls over `refresh_to_head`, `stale_copy_refusal` and the twin sweeps re-run
green.

## What is NOT claimed

The exit test the item wrote was "the reconcile clears a refill unaided". This turn cannot show
that on the live tree, because the live tree is **level** — there is no fork for the advance to
attempt and no blocking set to drain. What is shown is that the mechanism drains the class on a
constructed tree that has one, and that the two live instances are outside the class for a reason
that is now measured and written down. `.publish_gate_state.json`'s `last_clean_publish` is
untouched by this change and is not claimed.
