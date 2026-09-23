**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery
**Class:** `uncommitted_and_orphaned_work` (primary)

# The stale knowledge map is discarded, and the draw's own tag licensed the door that would have landed the revert

**Claim:** `refresh-the-shared-trees-stale-knowledge-map-before-a-pathspec-commit-reverts-three-landings`
**Disposition:** the work is done — `docs/institutional/knowledge_map.md` on the shared tree is
byte-identical to HEAD and the revert is disarmed. On the way there the item's own PATH CHECK
graded the copy `holder work` and named a door that would have landed the revert it was drawn to
prevent. That second part is the finding, and it is about the classifier, not about this path.

## What was enacted

    docs/institutional/knowledge_map.md   3 stale rows discarded, 5 landed rows preserved

`git status --porcelain docs/institutional/knowledge_map.md` on `/home/rich/synthetic-enterprise`
is now **empty**, and the path no longer appears anywhere in `python3 -m tools.stale_copy_refusal`
(0 mentions across the whole census). That is the control's own oracle, not my word.

Preserved before a byte was written:

    refs/preserved/refresh-to-head/knowledge-map-predates-landing-2026-09-23   25023f2ba

Recoverable with `git show 25023f2ba:docs/institutional/knowledge_map.md`.

The copy was a pure reversion — I read the full diff before choosing a door. Every line it added
was a strictly weaker predecessor of a line it dropped: the pre-2026-09-19 *Retention offers* cell
(restoring the since-refuted *"the sim has no SVT→FIXED edge at all"*), the pre-refutation *ERA5
retrieval budget* cell, the *Active vs passive renewal* cell without its two-sided internal-conversion
band, and the wholesale deletion of two rows — *Does the LEVEL of a household's own bill drive
switching?* and *What a conversion decision at a cap boundary IS*. Four landings, one pathspec.

## The finding: `holder work` does not establish that a landable hunk exists

The doorbell's own rule text says, in terms:

> `holder work` is the only tag `isolate_hunks --survey` + `surgical_land --content` is licensed for.

**For this copy that licence was wrong, and the real door said so.** Three classifications of the
same bytes, within minutes of each other:

| asked | verdict |
|---|---|
| the draw's PATH CHECK (`_path_verdict`, at draw time) | `holder work` — *"supplies 3 name(s) HEAD lacks … **land by hunk, never whole**"* |
| `tools.refresh_to_head` (default) | `refused_replacement_no_landable_hunk` — *"every hunk carrying one also deletes a name HEAD has, so `--keep` has no selection that takes the work without the revert, and `--content` would land the revert"* |
| `stale_copy_refusal` clock rule | `predates_landing_by_clock` against `dddfa6778` |

`isolate_hunks --keep N` had **no legal N** here, and `--content` would have landed the revert.
The draw named both of those and only those.

**The mechanism, and it is not a mis-tag on one path.** `background/delivery_lane.py:3785` branches
on `loss.novel` alone:

```python
if loss.novel:
    return ("holder work", "supplies {} name(s) HEAD lacks ({}) AND would revert {} -- "
                           "land by hunk, never whole".format(...))
```

`landable_hunks` — the function `stale_copy_refusal` uses to separate real holder work from a
REPLACEMENT — **appears nowhere in `delivery_lane.py`** (`grep`: zero hits). So the draw takes the
door's `judge` and stops one step short of the door's own conclusion. Its docstring claims the
opposite and is the reason nobody looked:

> THE CLASSIFICATION IS THE LANDING DOOR'S, NOT A SECOND ONE. … Re-deriving "is this a revert" here
> would put two answers in the tree and the draw's would be the one nobody maintains.

It *is* a second one. It answers "is this a revert" the same way and "which door applies" a
different way, and the draw's is indeed the one nobody maintains. The docstring's own argument
lands on it.

**Why it fires hardest on prose.** `symbols()` for markdown keys on the table-row prefix, so an
*edited* row is simultaneously a name HEAD lacks and a name HEAD has. Every substantive edit to a
knowledge-map row therefore reads as `novel` non-empty — `holder work` — while being a REPLACEMENT
with no landable hunk. The knowledge map is the file every session reads before writing a domain
constant, and it is the file whose stale copies this tag will systematically mislabel.

**This is fail-dangerous, not fail-closed.** The tag does not merely withhold a door; it *names*
one, and the named door lands the revert the item was drawn to prevent. A lane that trusted the
tag — which the doorbell instructs it to do, over the item's own word — would have re-armed four
landings.

## The remedy, not taken here

`_path_verdict` should call `door.landable_hunks` on the bytes `--keep` would build and split
`holder work` into `holder work` (a landable hunk exists) and `replacement` (none does → the door
is `refresh_to_head --base-wins`, gated on the clock). That is a change to the draw classifier,
which is another lane's file and outside this item's pathspec; filed here rather than done, because
doing it inside a delivery item would be exactly the sweep this project keeps paying for.

A control over it has a shape that can fail: a fixture copy whose every hunk both adds and deletes
a name must grade `replacement`, and the current code returns `holder work` for it.

## Corrections to the item's own words, kept beside them

- *"run: `python3 -m tools.refresh_to_head docs/institutional/knowledge_map.md`"* — that command
  **refuses** (rc=1). The working door needed `--base-wins`, which the item did not name.
- *"if another lane has since added real work to that copy, use `isolate_hunks --survey` instead"* —
  `isolate_hunks` was never available for this copy in either branch. The either/or was not one.
- The item's WHY was right on every substantive point: the copy was a predates-landing revert of
  four landings, and a pathspec commit would have taken them all.
