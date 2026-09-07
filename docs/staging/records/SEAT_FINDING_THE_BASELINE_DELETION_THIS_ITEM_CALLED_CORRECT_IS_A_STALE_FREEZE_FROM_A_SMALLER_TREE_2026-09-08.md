**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `every-lane-is-refused-by-two-causes-this-stretch-created`)

# The orphan-baseline deletion the item called correct is a stale freeze taken in a smaller tree

The drawn item said both halves were one file each. Half (b) was. Half (a)'s premise was wrong in
the one way that mattered: it said the deletion was correct and merely uncommitted, and told me to
land it. Landing it would have converted an attributable refusal into an unattributable one and
left every lane still refused.

## What the item claimed, and what was measured

| The item's claim | Measured, 2026-09-08 |
|---|---|
| The working copy deletes `demand_vector_coverage`, `file_director_document`, `stock_joint_generator` | It deletes `demand_vector_coverage`, `published_row_scalar_census`, `reduction_dimension`, `stock_joint_generator`. `file_director_document` is untouched. |
| "All three were wired this stretch by `122c08ec3` and `ab6f36d10`, so the deletion is correct" | **All four are still orphans at `origin/main`.** Nothing wired any of them. |
| Land the three lines with `isolate_hunks` + `surgical_land --content` | Landing them makes `tools/orphan_ratchet.py` refuse in a clean extract, so `surgical_land` refuses the commit — the gate would have caught me. |

The measurement, in the clean worktree at `origin/main` = `04361d6c7`:

```
tools.demand_vector_coverage       ORPHAN
tools.reduction_dimension          ORPHAN
tools.stock_joint_generator        ORPHAN
tools.published_row_scalar_census  ORPHAN
module_count 1122   entrypoints 58   problems []
```

## Why landing the deletion could never have cleared it

`orphan_ratchet.attribute_added` splits the accusation on HEAD's copy of the baseline. Today
`published_row_scalar_census` is frozen at HEAD and missing from the working copy, so the refusal
is the *attributable* one: **"AN UNCOMMITTED EDIT TO THE BASELINE IS WHY THIS REFUSES — NOT YOUR
COMMIT"**, naming the file and the lane to go to.

Land the deletion and HEAD stops freezing it. The module is still unreachable, so the accusation
does not go away — it changes text to **"THIS COMMIT ADDS WORK THAT NOTHING RUNS"**, blaming
whichever innocent lane commits next. Exit code 1 either way, and the diagnosis that made it
findable in under an hour is gone. That attribution split exists *because* this class stood 22
hours once; landing the deletion is the act that re-buries it.

**The general shape, and it is the reason this is filed rather than fixed silently:** when a
refusal offers two texts and one of them names a cause, "clear the refusal" and "commit the thing
it names" are different acts, and the second can destroy the first while leaving the red exactly
where it was.

## What the deletion actually is

`module_count` in the working copy reads **1110**. Measured at `origin/main` the tree has **1122**
modules; HEAD's committed baseline says 1111. `freeze()` writes that field from the tree it ran in,
so the working copy is the output of a `freeze()` taken in a tree twelve modules smaller than this
one — an isolated worktree extract or an older checkout — pasted into the shared tree. The four
deletions are artefacts of *that* tree's reachability, not a justified shrink of this one. Three of
them happen to be consistent with the shared tree's dirty state, which is why the ratchet accused
only the fourth and why the other three looked like landed work.

`module_count` is read by nothing, which is exactly why it survived as evidence.

## What was done

The shared working copy's `orphans` array was restored to HEAD's, by re-inserting the four lines
in place. `module_count` was left at 1110 — it is not the ratchet's business and touching it would
widen the footprint on a file another lane holds dirty. `tools/orphan_ratchet.py` now exits **0**
in `/home/rich/synthetic-enterprise`; the whole remaining diff on that path is the one
`module_count` line.

Nothing was committed for half (a). There is nothing to commit: the correct state of that file is
the one already at HEAD.

## Half (b), which was as described

`commons_source_supersession` and `commons_citation_supports_provenance` were added to
`tools/git-hooks/pre-commit` at lines 294 and 312 with no row in `_REFUSING_GATE_BANNERS`. Two rows
added, in chain order, after `scope-evidence ratchet` and before `write-time gate` (which the
suite's own order leg requires to stay last).

The needles are the literal parts of the gates' f-strings, up to the interpolation:

```
commons source supersession: REFUSED (
commons citation supports provenance: REFUSED (
```

**The trailing `(` is load-bearing.** Each gate's PASS line is the same sentence with one word
swapped — `commons source supersession: PASS (9 artefacts askable)` — so a needle ending at
`REFUSED` would still be a distinct string, but a needle ending at the colon would name a gate that
let the commit through. That is the fail-open twin this table already carries a leg for.

**Poison round, because "the suite is green" is ambiguous.** The suite proves the needle is a
string the emitter prints; it does not prove the classifier fires. Both gates pass against the real
commons today, so each was driven through its own refusal statement and the buffer handed to
`_parse_refusing_gate`:

| | verdict on a real refusal | verdict on today's real PASS |
|---|---|---|
| `commons_source_supersession` (poisoned commons copy, rc=1) | `commons-source-supersession gate` | `None` |
| `commons_citation_supports_provenance` (own refusal branch, rc=1) | `commons-citation-provenance gate` | `None` |

38 tests green across
`tests/background/test_a_refusing_gate_banner_is_a_string_a_gate_prints.py` and
`tests/background/test_a_non_test_gate_refusal_is_named.py`.

## What is next

1. **`tools.published_row_scalar_census` is an orphan and the baseline is the honest place for it
   today.** It was built this stretch (`b6c06a4f0`), it found four more homes for published law,
   and nothing schedules it. Whoever wants it running should wire it and land the baseline shrink
   *with* the wiring, which is what the baseline's own `_doc` asks for.
2. **Seven baseline rows are now reachable and could be shrunk**: `company.market.capacity_market`,
   `company.regulatory.seg_book`, `tools.domain_constant_origins`,
   `tools.ofgem_cap_unit_rate_composition`, `tools.people_physical_layer`,
   `tools.tou_extreme_day_concentration`, `tools.tou_price_shape_episode`. Shrinking is free and
   never refuses. Not done here: it is a different act from clearing a wedge, and mixing them is
   how the stale freeze got pasted in the first place.
3. **`freeze()` writes `module_count` and nothing ever reads it.** It was the only evidence that
   distinguished a justified shrink from a stale paste. A one-leg check — the ratchet warning when
   the baseline's `module_count` disagrees with the tree it is being measured against — would have
   named this in the refusal text instead of costing a premise re-measurement. Filed as a
   suggestion, not built: it is a control over a control, and CLAUDE.md's rule is to prefer the
   one leg only when it would catch the defect. This one would have.
