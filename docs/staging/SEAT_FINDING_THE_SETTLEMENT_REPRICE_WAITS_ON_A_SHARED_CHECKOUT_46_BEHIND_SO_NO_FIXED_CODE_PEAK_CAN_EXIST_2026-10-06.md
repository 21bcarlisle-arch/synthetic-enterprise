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
