**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 4 · **Atom:** `unminted` · **Claim:** `settlement-budget-reprices-on-the-fixed-code-peak`

# The settlement re-price waits on a shared checkout 46 behind, so no fixed-code peak can exist yet

## Premise, re-measured at draw (2026-10-06 ~16:10 BST)

- **Duplicate-work note:** the live claim it named is this draw's own write (`claimed_at` 16:07:23,
  same id). Nobody else holds it.
- **The ask is not spent.** `SETTLEMENT_CUSTOMER_YEAR_BUDGET` in `simulation/net_new_acquisition.py` is
  still `1050.0` on origin/main (`9b6b752ab`), and the journal leg of the ceiling test (9b6b752ab) still
  skips, because no peak from the curve's code exists yet.
- **The item's first check gives the answer it warned about.** `sim-runner.service` (MainPID 2970956)
  started 04:59 BST and runs the shared checkout, whose HEAD is `aa38800a1`. `06b7c821a` is **not** an
  ancestor of `aa38800a1`, so every run in this lifetime is pre-curve code. Its systemd peak (4.9 G) is
  not a fixed-code peak and must not be used for the re-price.

## The real blocker

The shared tree is 46 behind origin and 0 ahead. Every 5-minute `reconcile-watch` pass since at least
14:32 UTC has logged `NOT_ADVANCED [STILL OPEN]`: the tree went from 44 to 46 behind, and 22 paths
refuse the fast-forward. Of those, 9 are modified here and changed by origin (among them
`maturity_map.yaml`, `DIRECTION.yaml`, `simulation/settlement_daily.py` and its test), 12 are untracked
here while origin adds its own copy, and 1 is generated (`site/data/delivery.json`).

Two live Claude processes have the shared tree as their cwd: an interactive seat that has been up for
11 days, and a `-p` session that has been up for 35 minutes. Several of the 22 paths are probably in-flight
work belonging to one of them. That is why this isolated draw did not touch them:
reverting or landing another writer's uncommitted bytes from here is exactly what isolation forbids.
One reading worth checking by whoever clears it: `simulation/settlement_daily.py` on the shared tree
has mtime 2026-09-07. That is older than origin's recent commits to the file, so it may be a
`predates landing` copy (the door for that is `tools.refresh_to_head`), not holder work.

## What unblocks the re-price, in order

1. A lane on the shared tree clears the 22 paths, following the reconcile log's own instructions,
   and the tree fast-forwards to origin. That checkout then contains `06b7c821a`.
2. `sim-runner.service` restarts onto that checkout. Until the boot sha contains `06b7c821a`, no peak
   counts.
3. That lifetime ends, or runs long enough to settle a full book. Its systemd peak is then read
   (`MemoryPeak`), and the budget becomes
   `max(50, 1199.7 + (0.25*total_mb - peak)/2.884)` on the 20261006 curve, with its ORIGIN note updated.

Steps 1 and 2 are not the re-price item's work. Step 3 is a fresh draw once 1 and 2 have happened. The
handoff is filed under a new id so that the release of this one does not retire it.

## Re-drawn at 16:13 BST, six minutes after the handoff: still pre-curve, not re-priced

The handoff `settlement-reprice-after-the-runner-boots-on-the-curve-code` was drawn about six minutes
after it was written. It carried its precondition as prose and no embargo, so the draw had nothing to
hold it back. The re-check gave the same answer as before:

- `sim-runner.service` is the same lifetime: MainPID 2970956, started 04:59:30 BST, cwd the shared tree.
- The shared checkout is `aa38800a1`, now **47** behind origin (`d9b826f57`).
  `git merge-base --is-ancestor 06b7c821a aa38800a1` is false, so the code is still pre-curve.
- `MemoryPeak` has risen to 5,287,014,400 B (≈5.29 GB, up from 4.9 G). It is still a pre-fix peak and
  is **not** used for the re-price.
- `SETTLEMENT_CUSTOMER_YEAR_BUDGET` is left unchanged.

Disposition: this id is released. It is re-issued under a new id that supersedes it and carries a
`DO NOT DRAW BEFORE` stamp under six hours out, so that it is not re-drawn before steps 1 and 2 can
have happened. If a later draw finds the runner still pre-curve, it should re-embargo the item and
not re-measure it again. The real blocker is step 1, the shared tree's 22 contested paths, and that
belongs to the fork/reconcile alarms, not to this item.
