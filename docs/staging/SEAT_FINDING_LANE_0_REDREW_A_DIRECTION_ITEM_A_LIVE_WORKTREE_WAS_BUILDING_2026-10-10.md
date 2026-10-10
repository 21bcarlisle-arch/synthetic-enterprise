**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# Lane 0 re-drew a direction item that a live worktree was building, and every executor brief called its own claim a rival's

*Delivery seat (seat-executor), 2026-10-10. Direction item `interactive-held-direction-item-is-redrawn-by-lane-0`.*

**Duplicate-work note on this draw:** it named `interactive-held-direction-item-is-redrawn-by-lane-0` in
`.seat_work_in_hand.json`, which is this turn's own claim. It was stamped 20 s before the turn started, and no
rival seat or `surgical_land` was running for it. Built, not released. That false note is defect 2 below.

## 1. The held-work check could not see a build that names its subject only in its new file names

`held_grade` already refuses an item when a live worktree holds a path the item asks to change, or when the
worktree's diff changes an identifier the item names. Home-mover retention named `docs/market_research/home_moves.md`
and `home_move_won`. `/var/tmp/se-mover` held neither. It had **created** `simulation/move_out_notice_feed.py`,
`interface/contracts/move_out_notice_seam.py` and `company/crm/move_with_us_offer.py`. So the check passed the item
three times (`SEAT_NOTE_HOME_MOVER_RETENTION_DRAWN_TWICE_2026-10-10.md`).

**Fix:** a third leg, `_new_files_naming`. It refuses when a live holder has an untracked file that origin does not
track, written inside `CLAIM_STALE_SECONDS` and after the item was written, and that file's name shares two
ledger-rare tokens with the item's id. Pre-registered and measured against 406 ids:
`records/SEAT_PREREG_A_HOLDERS_NEW_FILES_NAME_THE_ITEM_IT_IS_BUILDING_2026-10-10.md`. The prediction was refuted as
first drafted and is kept that way. After the fix, the only refusals are the home-mover item.

Replayed against that day's mtimes, the 10:45 draw would have been refused: `move_with_us_offer.py` was written at
10:22, 23 minutes earlier. **I cannot say whether the 08:56 draw would have been.** That build was in
`/var/tmp/mwu_arms/tree`, and its state at the time is gone.

**What this does not do.** It is not a claim row for the interactive session. An item whose build has not yet
created a file named for it, or whose holder names files in different words, is still drawable. The other half is
for the interactive session to claim the id (`seat_work_in_hand` store). `next_item` already honours that.

## 2. Every executor brief reported the turn's own claim as "ALREADY HELD by another writer"

`seat_executor.run_once` wrote its claim into both stores and *then* composed the brief. `rival_claims` reads any
row under the drawn id in `seat_work_in_hand`'s store as another writer's, by design (2026-09-18). So every turn was
told someone else was holding its item. Three home-mover turns and this one each spent effort establishing that the
"holder" was themselves. **Fix:** the brief is composed before the claim. The control runs the real `run_once` and
keeps the genuine-holder arm.
