**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted` — Lane 0 delivery

# A behind shared tree stops the seat landing its orientation, and the unlanded record keeps the tree behind

Item: `this-mondays-publish-reaches-origin`. The publish was refused `behind_origin` because the
shared tree could not fast-forward (26 behind, 0 ahead). What held it, measured against origin at
~08:55Z:

| Path | Against origin | Kind |
|---|---|---|
| nine `docs/staging/*_2026-10-05.md`, `tests/background/test_the_draw_follows_the_priority_order.py`, `background/supervisor.py` | byte-identical | twins (the reconciler clears these itself) |
| `docs/staging/reference/CLASS_UNCOMMITTED_AND_ORPHANED_WORK_2026-08-12.md` | staged blob older than origin's; disk = HEAD | generated census exhaust, superseded |
| `docs/direction/DIRECTION.yaml`, `decisions.jsonl`, `docs/status/SEAT_STRETCH_LOG.md`, `site/data/delivery.json` | differ | **hand work**: the 08:23Z orientation, never landed |

The four hand-work files were landed as written by this item (see the commit that carries this
note). The same shape as 987146bae, which landed the 23:22Z orientation six hours earlier.

## The cause is a loop, not a timeout

`docs/observability/delivery-seat-log.md`, 08:28:51Z:

> landing refused (DirectionNotLanded): docs/direction/decisions.jsonl on origin/main is not kept
> whole by this tree's copy (it is not origin's copy plus one inserted block)

The seat appends its row to the **shared tree's** `decisions.jsonl` and inserts its entry into the
shared tree's stretch log. When the shared tree is behind origin on those files (it is whenever
the previous orientation landed through the seat's own origin worktree but the shared checkout
didn't fast-forward), the copy is HEAD-plus-one-block, not origin-plus-one-block. The
append-only guard correctly refuses. The record then stays dirty in the shared tree, and that
blocks the fast-forward that would have let the next orientation land. **Each orientation that
happens while the tree is behind makes the tree stay behind.**

987146bae blamed the 23:20 run's systemd timeout. That run may also have timed out, but the 08:23
run exited 0 in 5½ minutes and was refused on this guard. A wider guard doesn't fix it: the
uncommitted edit to `background/delivery_seat.py` in the shared tree (mtime 04:03, `keeps_all_of`,
one inserted block anywhere) still refuses HEAD-plus-block against a moved origin.

## Proposal (not built here: `delivery_seat.py` holds another lane's uncommitted hunk)

In `land_direction_on_origin`, rebase each APPEND_ONLY file onto origin instead of refusing.
The block is `ours` minus `HEAD:path` (one contiguous insertion, which `keeps_all_of` already
detects). Insert it into `origin:path` at the same anchor: the end for `decisions.jsonl`, under
the header for the stretch log. Refuse only when the copy is not HEAD-plus-one-block.
`DIRECTION.yaml` and `delivery.json` are whole snapshots and already land over origin. After the
landing, write `HEAD:path` back into the shared copy so the fast-forward is clear. That is safe
because origin now holds the block. This item did the same thing by hand.

Control: a test where origin carries a row HEAD lacks, and the seat's copy is HEAD plus its own row.
The landing must keep both rows. On today's code it raises `DirectionNotLanded`.
