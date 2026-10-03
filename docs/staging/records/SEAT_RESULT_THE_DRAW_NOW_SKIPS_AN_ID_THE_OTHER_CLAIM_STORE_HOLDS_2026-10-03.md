# SEAT RESULT — the draw now skips an id the other claim store holds (2026-10-03)

**Severity:** MEDIUM — two whole executor turns were spent on one item in one afternoon, and
the second turn's claim overwrote the holder's row.

**What happened.** `build-the-supplier-dd-stopping-rule` was drawn by the seat executor at 14:29
and again at 14:39 BST. Both times a scheduled worker (pid 2590080) was building it, with its
work uncommitted on the shared tree. The first turn recorded the disposition in
`SEAT_RESULT_THE_DD_STOPPING_RULE_WAS_DRAWN_TWICE_AND_THE_RIVAL_WORKER_IS_BUILDING_IT_2026-10-03.md`.
This second turn found the same situation and did not build the item either. The worker's build
is not repeated here and the claim is not released, for the same reason given in that record.

**Cause.** `delivery_lane.next_item` filtered on `held()` for its OWN store only. `rival_claims`
saw the same-id row in `.seat_work_in_hand.json`, but it runs AFTER the draw and only writes a
note in the doorbell. `seat_executor.run_once` then claimed the id in both stores. That
overwrote the holder's `seat_work_in_hand` row with the executor's row, which `_hand_back`
releases when the turn ends. When this turn read the live stores, the two rows had identical
`claimed_at` stamps (14:39), so the holder's own row had already been replaced.

**Fix.** `next_item` now also treats an id as taken when another claim store holds it and the
row is not stale on that store's own deadline (`held_in_other_stores`). This applies only to the
production call (`path is None`), so tests with an isolated store do not read the live stores.
It is a hold, not a ban: once the other row is released or goes stale, the item can be drawn
again. Controls: `tests/background/test_the_draw_skips_an_id_held_in_the_other_claim_store.py`
(held → skipped and the next free item is drawn; free → drawn; stale → drawn). There are three
named mutations and all three fire.
