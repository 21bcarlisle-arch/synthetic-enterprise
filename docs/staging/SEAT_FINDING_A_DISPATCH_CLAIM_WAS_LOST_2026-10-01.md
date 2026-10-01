**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `PB4_engagement_separated_from_elasticity`

# The worker's dispatch claim was lost, and the claim stores had no lock

Claim `land-pb4-swap-with-value-arms-retaken-in-the-new-world`, drawn a fourth time at 15:39:33Z by
the isolated executor. The worker (pid 2082292) was still running it: PB4 capture C2 was pid
2083381, 21 minutes in. This turn built none of the PB4 work. **The premise is not spent**, for the
reason `SEAT_FINDING_PB4_SWAP_LANDING_WAS_DRAWN_TWICE_AND_THE_WORKER_HOLDS_IT_2026-10-01.md` gives.

## What the earlier note got wrong

It said the step-aside was the cause of the redraws, and that the fix belonged in the draw. Both
were wrong. `next_item` does skip a held id. Measured against a copy of the live store with the
PB4 row present, it returned `attribute-the-renewal-feedback-on-the-ex-vat-standing-charge`.
**Draws 2 to 4 happened because the worker's claim was no longer in the store.**

- `worker-tick-log.md`: `15:17:20 lane-0 claim taken at dispatch: land-pb4-swap-...`.
- `.delivery_lane_claims.draws.json`: `first_drawn_at` is 15:17:20 and `last_drawn_at` is 15:19:54.
  The executor drew the item at 15:19:54, so the row was already gone by then.
- Nobody released it. The worker's transcript runs no `--release` or `--landed`; it only quotes
  them from the doorbell. The executor turn before (`close-the-vat-basis-class-in-the-world`, child
  exited 15:17:06) had its own claim released by its tick, so `_hand_back` wrote nothing.
- No preserved `.unreadable` copy exists. A truncated read takes that route, so it was not a
  truncation race.

**Which writer saved the stale dict, I cannot yet say.** Every writer of both claim stores
(`claim`, `release` and `bind_paths` in `background/seat_work_in_hand.py`) did load, modify and save
with no lock, through a non-atomic `write_text`. The daemons calling them run concurrently.

## Measured, with the prediction written before the run

Eight processes each claimed 25 ids into one store. The prediction was that fewer than 200 rows
survive unlocked and all 200 survive locked. **Unlocked: 21 of 200 survived. Locked: 200 of 200.**

## Repair

`seat_work_in_hand._exclusive` takes an `flock` over each writer's whole load, modify and save, and
`_save` writes atomically through a temporary sibling and `os.replace`. This is the same pattern as
`ntfy_utils.record_sent_id`. The control is
`tests/background/test_concurrent_claim_writers_lose_no_row.py`, and two mutants each turn it red:
a no-op lock, and a temporary file left behind.

**Residue:** the draws ledger (`.delivery_lane_claims.draws.json`, written at four sites in
`delivery_lane.py`) still does an unlocked read-modify-write. It is a record, not a guard, so a lost
row there cannot cause a redraw. It can drop a `first_drawn_at`.

## Disposition

The executor re-claimed the id in both stores at 15:45:55Z, with a note naming the worker. It has a
fresh `claimed_at`, so this turn's `_hand_back` does not match it and the item stops being offered.
When the worker finishes, its `--release` drops it. If the worker dies first, the 100-minute sweep
does.
