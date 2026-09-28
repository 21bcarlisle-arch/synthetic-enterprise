# A landed SEAT_RESULT spends its prereg's grading premise: landed, and the two rows dispositioned

**Item:** `a-landed-seat-result-spends-its-preregs-grading-premise` (lane 0, 2026-09-28).

**Built by an earlier invocation, landed by this one.** `background/delivery_lane.py` and
`tests/background/test_a_landed_seat_result_spends_its_preregs_grading_premise.py` were already in
the shared tree (11:25 to 11:26), unlanded, with no live claim. This invocation re-read them and did
not rebuild them:
- `prereg_result(text, written_at)`: when an item names a `SEAT_PREREG_<stem>_<date>.md` and
  origin/main holds a `SEAT_RESULT_<stem>_*.md`, it returns the commit that first put that result
  there. A result that is OLDER than the item is treated as context and does not spend it.
- `next_item` skips such items. The same check is the first derived branch in `_disposition`, and
  it only counts a result that was already there when the window opened.
- The control covers both branches: the spent prereg is skipped AND the prereg with no result (C1
  bracket) is still handed out. Five mutations were run in a scratch worktree
  (always-False, always-True, no written_at guard, no disposition branch, no window guard) and
  every one fired.
- Against real git, the fixture case resolves to `7dc8f150d`.

**Dispositions.**
- `grade-the-balance-rule-two-state-diff-against-the-cefd2c04a-baseline` reads `premise_spent`
  with `7dc8f150d`. That was already stated at 11:26 by the earlier invocation, and the new
  derived branch now reaches the same answer from git on its own.
- `the-billing-ledger-and-the-pnl-book-one-write-off`: `--landed ... --commit fcba478b7`
  REFUSED ("NOT CLAIMED"), because the 03:24 re-draw had been swept. No CLI door records a landing
  on an unclaimed row. I wrote the tombstone that `--landed` would have written by calling
  `_remember_landing` directly, with fcba478b7's own `%ct` (04:07) and paths. After that the row
  drops out of `drawn_without_landing`. **To reverse it:** restore `last_landing_at` 1790561433.0
  and the previous paths on that row in `.seat_work_in_hand.draws.json`.

**Gap:** there is no door for "a swept window's work did land". If this comes up again, give
`--landed` a `--swept` form that writes only the tombstone.
