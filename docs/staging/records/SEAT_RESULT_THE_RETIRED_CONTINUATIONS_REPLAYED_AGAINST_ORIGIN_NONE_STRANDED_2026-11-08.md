**Severity:** LATENT · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `replay-the-retired-continuations-against-origin-evidence` (Lane 0 delivery)
**Pre-registration:** `docs/staging/records/WORKER_PREREG_REPLAY_THE_RETIRED_CONTINUATIONS_AGAINST_ORIGIN_2026-11-08.md`

# The retired continuations replayed against origin: 784 refused, none found stranded, none re-offered

**2026-11-08, delivery seat.**

## What was run

I called `seat_continuation.origin_refusal(row, items=<whole store>)` on every row in `retired()`
that is not a `focus_row_tombstone`. The live stores were read through `shared_tree_dir()`. Then I
checked the refused rows against origin/main.

| | rows |
|---|---|
| retired, all | 1,566 |
| retired, not focus-row tombstones | 1,313 |
| refused by `origin_refusal` | **784 (60%)** |
| refused, N16 shape (landing bound in the ledger, never promoted) | **0** |
| refused, "no landing is bound and no spent premise is recorded" | 784 |

The refusals were retired between 6 Sep and 7 Nov, at 15 to 40 a day until 22 Oct and about 2 a
week after it. The drop follows the ledger-binding work of 15–16 Oct and the `--work-id` binding on
promotion.

## Did the work land under another id

- **All 19 rows retired since 23 Oct were checked one by one.** Each one's work is on origin under a
  commit that does not bind its id: the cast section in `weekly_rhythm._explore_cast_section`; the
  ToU registers (`2a2c5c5770`, `3dfe5cad40`); the gas-floor copy (`ff8437814e`); the collections
  re-offers (`796808aced`); the Futures row (`7b37a084ba`); the B8 regrade (`f612bd8776`); PB8 at 0.035
  (`71cb7debcf`); the externals steer (`67a893e749`); the meter-reads fuel split (`79bbd9a3d3`); the
  read-nets grade (graded 30 Oct in its own pre-registration); the reputation GAP pages (`d5567880e0`,
  `2c2ed8d2ef`); the 65bbdc6787 verdict (`204c76f9fd`); the PC2 per-register estimate (`308a3f168e`);
  Ask 2 (`ac5fe5e916`); the held opening estimates (`55623bfcf5`); the household-page term
  (`40842cdbe6`, `d14ff599e5`); and the triad cash (`12a470de72`). The sharded suite read was
  dispositioned "not started" in `385abf7018`. The dual-fuel closing-balance red **passes at HEAD
  e1ff923d22** (run today: 1 passed, 449 s).
- **The 765 older rows were triaged mechanically.** For 575, origin has a commit that touches a path
  the row names within ±3 days of its retirement; that is weak evidence but it is evidence. 159 name
  no path. 50 name paths that origin did not touch in that window. I read those 50 by hand. Most are
  analysis or observation rows that later work overtook. For the 12 build-shaped ones I checked the
  code directly (the surgical_land refusal reasons, the `load_run_output` gz reader, the 2025
  standing-charge rows, the ex-VAT SVT, the gas renewal commodity, the H50 teardown, the lane-unit
  crash, the household-charged accessor, the sold standing charge, the ToU-weighted sold rate, the
  segment's own forward, and the float32 trace day). All 12 are on origin.

## Against the prediction

- Share refused: predicted 20–60%; measured 60%. That is the upper edge, so the refusal is mostly
  noise for rows retired before binding was routine. **Held, just.**
- Really missing: predicted 0–3; found 0 among the 31 checked by hand. The 159 no-path rows and the
  38 non-build rows among the 50 were not each read, so 0 is a sample result, not a census.

## What this means

- **Nothing is re-offered.** Re-offering 784 rows on the refusal alone would put done work back
  into the draw.
- **The N16 shape was rare, not common.** Its instances were the ones already seen, and none is left
  among the retired rows.
- **617a2181e's gate is right, and it will hold rows.** On the historical record, 60% of
  retirements had no id-binding commit on origin. Since late October nearly every row binds through
  `promote_worktree_landing --work-id`, so the hold should fire rarely now. If `HANDOFF HELD`
  lines become frequent in the executor log, check first whether the work landed without
  `--work-id`, before treating it as stranding.
