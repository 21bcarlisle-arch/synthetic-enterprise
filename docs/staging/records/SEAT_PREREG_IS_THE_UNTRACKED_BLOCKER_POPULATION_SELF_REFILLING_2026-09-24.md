# PRE-REGISTRATION — is the untracked-blocker population self-refilling?

**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

**Written 2026-09-24T00:40Z, before the measurement below was run.**

## What is already established, and is therefore NOT predicted here

These were read off the live shared tree at 00:38Z and off `background/origin_reconcile.py`'s
source. They are measurements and source readings, not predictions, and they are recorded here so
the predictions below cannot be confused with them:

- The shared tree `/home/rich/synthetic-enterprise` is **10 ahead / 9 behind** `origin/main`.
- `paths_blocking_fast_forward` names **4** blockers: 1 `FF_MODIFIED`
  (`docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md`, not a tracked twin) and 3
  `FF_UNTRACKED`, of which exactly 1 is a byte-identical twin.
- `advance_shared_tree` asks `commits_ahead` **before** it judges any path, and returns the
  divergence refusal when `ahead` is non-zero — *"No working-tree path is the cause and clearing
  twins would delete files and still not advance, so nothing was touched."*

## The predictions

**P1 — the pile is far larger than the blocking set.** The count of untracked files in the shared
tree under `docs/staging/` whose path `origin/main` **already carries** will be **≥ 10**, and
plausibly ≥ 30. Reasoning: an orphan only *blocks* while origin is still ADDING that path relative
to the tree's HEAD; once the tree advances past that commit the untracked draft stays on disk
forever and stops being counted. So the blocking set is a moving window over a monotonically
growing pile, and reading the window as the pile is the error the item makes.

**P2 — the mint rate is ≥ 1/day.** Distinct root-level `docs/staging/*.md` paths ADDED by
`origin/main` will average **≥ 1 per day** over 2026-09-17 → 2026-09-24. Each one is a candidate
orphan by the mechanism `untracked_orphan_verdicts` documents: a seat writes the draft into the
shared tree, lands an *edited* copy from an isolated worktree via `surgical_land --content`, and the
draft on disk is left untracked at a path origin now carries.

**P3 — clearing the instances this turn would move nothing.** Because `ahead = 10`, the door the
item names would refuse before touching a path. I predict the observed refusal string will name
divergence, not any of the 4 blocking paths.

## What would refute each

- P1 is refuted by a count < 10 — that would mean the pile really is finite and near-empty, and the
  blocking set is close to the whole of it.
- P2 is refuted by < 7 distinct root-level adds over the 7-day window.
- P3 is refuted by `advance_shared_tree` reaching its path judgement at all while `ahead > 0`.

## Why this is worth pre-registering

The item I drew asserts the untracked blockers are what holds the publisher, and offers "clear
them" as the remedy. If P1 and P3 hold, the instances are *not* the work and clearing them is a
deletion bought for no advance — the exact worst case `advance_shared_tree`'s own all-or-nothing
rule exists to prevent. Filing the prediction first is the only way that reading is distinguishable
from one written after the answer was known.
