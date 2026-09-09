**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** (Lane 0 delivery — land-the-w2-28-level-claim-or-lower-it-then-publish-and-take-the-next-refusal) · **Class:** uncommitted_and_orphaned_work

# FINDING — the shared index still held the failed cycle's pre-landing blobs, so the next plain commit would have reverted the control and deleted the document it depends on

`surgical_land` builds and gates the tree the commit *would* create. It does not refresh the shared
index. So when a cycle fails and then a later cycle lands the same paths by surgical route, the
shared index is left holding the **failed** cycle's blobs — indefinitely, and invisibly, because
every working-tree reading agrees with HEAD.

---

## The drawn premise was spent, and the item's own warning is what caught it

The item said: the level-promotion gate refuses `W2_28` at `level_current: 1` on evidence not in the
tree the commit would create; the control is staged but NOT_IN_HEAD; `tools/reduction_dimension.py`
is in HEAD but modified; the cited document is untracked. Measured on real disk/git state at draw
time:

| | reading at draw |
|---|---|
| `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` in HEAD | **present** (`9aaf78e82`) |
| `tools/reduction_dimension.py` in HEAD | present, and **worktree byte-identical** |
| the cited `docs/staging/done/SEAT_FINDING_TWO_LANES_BUILT_W1_14S_…md` in HEAD | **present** (`2b8b3018f`) |
| `W2_28.level_current` at HEAD | **1** |
| `python3 -m tools.level_promotion_gate` | **rc=0** |

All four paths of the minimum landable unit the map row computes landed together in `31aff7abd`,
before this tick. The named cause was gone. The item said in terms that *"stopping at 'the named
cause is gone' is the failure mode to avoid"* — so the question became what is holding the tree
now, and the answer was in the index.

## What was actually there

`git diff --cached` reads HEAD → index. On the three tracked paths of that unit it reported
**14 insertions, 249 deletions** — the index is *behind* HEAD, not ahead of it:

| path | index blob | which commit that blob is from |
|---|---|---|
| `tools/reduction_dimension.py` | `59d57f9ca` | `31aff7abd~1` = `a0a62f918` — **pre-landing** |
| `tests/architecture/test_a_coverage_claim_declares_what_it_reduces_over.py` | `275584e4f` | no commit — an intermediate working copy of the failing lane |
| `docs/design/maturity_map.yaml` | `003c45ae6` | not HEAD (`4d8a778be`) |
| `docs/staging/done/SEAT_FINDING_TWO_LANES_BUILT_W1_14S_…md` | *no entry* | **staged deletion** (`D ` beside `??`) |

`a0a62f918` is the git hash recorded against the 04:44 UTC publish failure in
`docs/observability/.publish_gate_state.json`. The index is that failed cycle's staging, frozen.
The working tree, meanwhile, is byte-identical to HEAD on all four paths — `git hash-object` on each
disk copy returns exactly the HEAD blob. **Every reading that looks at the working tree says the
tree is clean and the work is landed. Only the index disagrees, and nothing reads it.**

## The failure this would have caused

A commit taken from that index — a plain `git commit`, or any pathspec wide enough to carry these
paths — creates a tree that:

1. reverts `tools/reduction_dimension.py` to its pre-`31aff7abd` version (−70 lines), and
2. reverts the control test to a version that is in no commit, and
3. **deletes** `docs/staging/done/SEAT_FINDING_TWO_LANES_BUILT_W1_14S_…md` (−126 lines).

That third one is load-bearing: `test_every_outstanding_row_names_a_document_that_still_exists`
calls `.exists()` on it, and the map row records the measurement that made the point —
16/16 with the citation present, 1 failed/15 passed with it removed. So the commit would have
undone `31aff7abd` in full and rebuilt the wedge this Lane 0 item was drawn to clear, while every
working-tree check stayed green.

This is the same shape as `SEAT_FINDING_THE_RECONCILE_REFUSAL_TOLD_ME_TO_LAND_A_PRODUCERS_OUTPUT…`
from the previous turn — an instruction whose single named action would have restored something
another lane had just deleted — reached this time through the index rather than through a refusal.

## The repair

`git reset HEAD -- <the four paths>`: path-limited and mixed, so it rewrites those four index
entries to their HEAD blobs and **does not touch the working tree**. Because disk already equals
HEAD, the four paths go clean rather than modified. Nothing else in the index is touched — the
publisher's ~200 staged `site/` paths and two other lanes' new staged test files
(`tests/tools/test_the_rows_that_concluded_on_a_sibling.py`,
`tests/tools/test_settlement_ceiling_probe.py`) are left exactly as their lanes staged them.

Not `git checkout <path>` and not `git stash`: both would overwrite the working tree, which is the
only copy that is *correct*.

## The correction the item's second instruction needed

The item also said: `python3 -m tools.reduction_dimension --undeclared` reports the single
OUTSTANDING row `simulation.weather_cell_siting` **STALE** — *"delete it in the same unit"*.

**Do not.** That reading is an artefact of the shared tree. Measured in a `git worktree add --detach
HEAD` extract:

| tree | census verdict for `simulation.weather_cell_siting` |
|---|---|
| shared working tree | `STALE ROW … declares now -- delete its OUTSTANDING row` |
| clean HEAD extract | `DEBT … (archive_coverage)` — **still silent** |

`simulation/weather_cell_siting.py` is ` M` in the shared tree: the declaration exists **only as
another lane's uncommitted edit**, and `git show HEAD:simulation/weather_cell_siting.py` contains no
declaration at all. Deleting the OUTSTANDING row would make `unexpected_silence()` non-empty at
HEAD, so `--undeclared` exits 1 and the control's own suite goes red in every commit while staying
green in the shared tree — the precise inversion the row was written to avoid.

`tools/reduction_dimension.stale_outstanding` already says this in its docstring, and says why it is
printed rather than asserted: *"the shared working tree and every clean HEAD extract disagree about
whether `simulation.weather_cell_siting` is silent, so a leg keyed to it is green in one tree and
red in the other."* The CLI line is a report about the tree it was run from, and the drawn
instruction read it as a fact about the repository. **The row is discharged when the declaration is
committed, not when the census prints STALE.**

## What is next

- The mechanism generalises and is not repaired by this instance: **a `surgical_land` landing leaves
  the shared index holding whatever the previous failed attempt staged**, and no control reads the
  index against HEAD. `git status` shows it as `MM`/`D `, which every lane reads as "another lane
  has work in flight" rather than "this is residue that will revert HEAD". A one-leg check —
  index-behind-HEAD on any path is residue, not work — is the smallest mechanism that would catch
  it, and it belongs beside the existing stale-copy census rather than in a new register.
- The census CLI prints `STALE ROW` without naming which tree it measured. It should say so, for the
  same reason the docstring gives.
