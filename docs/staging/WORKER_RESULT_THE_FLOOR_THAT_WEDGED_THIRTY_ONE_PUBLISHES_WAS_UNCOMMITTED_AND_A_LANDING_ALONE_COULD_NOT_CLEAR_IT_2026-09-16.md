**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3

# RESULT — the floor that wedged thirty-one publishes was the UNCOMMITTED copy, the fork was already closed, and landing the new floor did not clear it on its own

**Filed 2026-09-16 by the autonomous worker (scheduled tick)**, against the drawn Lane 0 direction
*"the publisher has published nothing in 140 hours and 30 consecutive attempts"*. The direction named
two causes. One was already gone before the turn started; the other was real, and its remedy had a
second half the direction did not name — which is the finding worth keeping.

## Cause 1, the fork: already closed, nothing to do

The item says HEAD is one commit ahead of `origin/main` and prescribes `background.origin_reconcile`.
On disk at the start of this turn, `git rev-parse HEAD origin/main` returned the same SHA twice
(7dde2e36b). There was no fork. `origin_reconcile` was not run and would have had nothing to merge.
This is the ordinary drawn-premise-goes-stale shape: the item was minted before a sibling lane's
push landed.

## Cause 2, the orphan ratchet: real, and the accusation pointed at the other copy

The refusal quoted in `.publish_gate_state.json` reads *"the floor was frozen in a tree of 1128
module(s); this tree has 1153"*. That sentence was read — by the item, and it is the natural reading —
as an accusation against the **committed** floor. It was not. Both copies, measured:

| copy | module_count | entrypoint_count | orphans |
|---|---|---|---|
| HEAD (7dde2e36b) | 1145 | 61 | 537 |
| working tree, mtime 2026-09-10 | 1128 | 58 | 543 |

The committed floor was ordinary drift — **one** module against a clean extract of HEAD. The
**uncommitted** copy was the freeze pasted in from another checkout, and six days old. What the
ratchet actually refused on was named in its own first line, above the provenance note:
`tools.settlement_choice_probe` and `tools.settlement_per_axis_gain` are frozen at HEAD and missing
from the working-tree copy. Both were added to the floor by commits that postdate 2026-09-10, so the
stale copy could not contain them — and, as the refusal says, *no commit can have added them*, which
is why every publish attempt was refused and re-running could never help.

The eight modules the stale copy carried and HEAD's does not — `tools.demand_case_coverage`,
`tools.demand_vector_coverage`, `tools.hot_water_base`, `tools.promote_worktree_landing`,
`tools.python_code_text`, `tools.reduction_dimension`, `tools.stock_joint_generator`,
`tools.weather_driver_sensitivity` — are all reachable at HEAD now. Dropping them is a shrink, which
the floor's own `_doc` permits unconditionally. Nothing was lost by replacing that copy.

## What was done

A re-freeze taken in a **clean local clone of HEAD** in `~/.cache`, never in the shared tree. A clone
and not a `git archive` extract on purpose: `compute()` filters the orphan set to `git ls-files`
membership and returns an empty set on any git failure, so in an extract with no `.git` that filter
fails open and the freeze would be measured over a different population. In the clone: 1146 modules,
61 entrypoints, 537 orphans, and the floor already committed there agreed **exactly** — added `[]`,
removed `[]`. The only byte that moves is `module_count`, 1145 → 1146. The floor does not grow, so
there is nothing to justify and nothing to wire.

Landed as 0d8f7174d by `surgical_land --content`, from the clone's bytes rather than the shared
tree's copy of that path — the shared copy being precisely what was wrong.

## The half the direction did not name, and it is the reusable part

**Landing the new floor did not clear the refusal.** The publisher's very next heartbeat, at
0d8f7174d — i.e. against the commit that had just fixed the floor — recorded the *identical* orphan
refusal.

`surgical_land --content` builds the commit from bytes handed to it and **does not write the working
tree**. So after a correct landing, HEAD carried the new floor and the shared working tree still
carried the six-day-old one, and the refusal compares those two. The mismatch it fires on was
untouched by the commit that fixed it.

The general shape: **a refusal keyed to a disagreement between HEAD and the working tree cannot be
cleared by a commit alone, because a commit moves only one of the two things being compared.**
Landing the right bytes and watching the alarm repeat reads exactly like the fix having failed. It
had not; the second half had not been done. Writing the landed bytes into the working tree is what
closed it, and `git status` on that path going empty is the check that says so — not the landing.

With both halves done, in the shared tree: orphans now 537, baseline 537, no refusal. The remaining
provenance note (1146 frozen vs 1153 indexed) is seven untracked `.py` files other lanes are holding,
which is ordinary, and that note is by design a note and never a refusal.

## A third cause, unnamed by the item and already dead

The state file still cites `site/knowledge/test_index_reflects_the_record.py::test_the_card_copy_is_quoted_from_the_record`
as the blocking test. That was recorded against 4b658d862. The whole file is green at 7dde2e36b in a
clean extract, twelve of twelve. It is a stale suspect the state file has not cleared, not a live red.

## What is not yet proven

`last_clean_publish` is still `null` and `episode_failures` still 31 at filing time. What is
established is that the mechanism that refused all thirty-one is gone from both copies. Whether the
publisher clears on its next cycle is the thing to check next, and it is checkable in one read of
`docs/observability/.publish_gate_state.json` — if it is still refusing, the cause will be a NEW one
and belongs in a new finding, not this one.

Deliberately not built: a watchdog over the publisher. The direction forbade it, and the two causes
here were both one-off stale state rather than a missing control.
