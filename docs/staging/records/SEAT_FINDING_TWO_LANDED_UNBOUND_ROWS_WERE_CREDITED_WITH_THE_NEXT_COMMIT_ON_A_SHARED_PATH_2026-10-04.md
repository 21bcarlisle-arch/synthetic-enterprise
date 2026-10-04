# Two landed_unbound Lane 0 rows were credited with the wrong commit. Both are now premise_spent

**Severity:** RECORDED · **Lane:** Lane 0 delivery · **Claim:** `bind-the-two-landed-unbound-lane-0-rows`

The duplicate-work note at draw time named `bind-the-two-landed-unbound-lane-0-rows` as "held by
another writer". That was this draw's own write: the claims store and `.seat_work_in_hand.json` carry
the same `claimed_at`. There was no rival.

## What each commit is, read against its item's text

| Row | Commit the join credited | What that commit is | The item's actual work | Disposition |
|---|---|---|---|---|
| `land-the-unlanded-dd-stopping-rule` | `dd7bbce0f` | PB8 **L2** money side. The item says "The L2 leg is NOT part of this item" | `1c34f6ef1`, PB8 L0->L1, on exactly the item's named paths. Stamped 16:52 BST. The draw was at 17:12 | `--premise-spent ... 1c34f6ef1` |
| `grade-the-payment-history-p-c-legs-on-exit` | `1dba82e95` | C33 Breathing Space closure. Its only overlap with the item is `docs/design/maturity_map.yaml` | Nothing was graded. Probe `585ea9746` (13:47, inside the window) answered the question. `b980d93ad` stops the C leg as superseded and records why in the prereg | `--premise-spent ... b980d93ad` |

`--landed --commit` was not available for either row. Both claims had already been swept, and
`--landed` refuses with "NOT CLAIMED". So `--premise-spent` was the remaining disposition that names
the commit. `drawn_without_landing()` now reads `premise_spent` for both, each with its commit and
reason.

## The class (not fixed here)

`_landed_unbound` credits any in-window commit that touches a path named in the item's prose. That
produces a wrong credit in two cases:

- **A commit stamped just before the draw.** If an item's work was committed but not yet on origin
  when the item was drawn, the commit falls outside the window. The join then credits the next leg's
  commit on the same file instead.
- **A widely shared path.** When the item names a file that many unrelated commits touch, such as
  `maturity_map.yaml`, any of those commits can be credited.

The label `landed_unbound` is honest: it says a commit landed on those paths and does not claim the
item was delivered. But the brief asks the reader to bind the credited sha, and binding these two
would have recorded the wrong commit. Read the commit against the item's text before you bind.

## DONE

Neither row is `landed_unbound` or `not_done`. Both stay in `lane_0_drawn_never_landed` until they
leave its 24h horizon (around 17:12 BST on 2026-10-04 for the later one), shown as dispositioned rows
that are "not yours to redo".

## Redrawn at 05:03 BST, after this record landed. Released, nothing redone

The focus id itself was drawn again 18 minutes after `d06af26a5` landed. That landing dispositioned
both rows but never ran `--release bind-the-two-landed-unbound-lane-0-rows`, so the DIRECTION.yaml
row stayed drawable. Again, the duplicate-work note's "held by another writer" was the draw's own
write. `ps` showed no rival.

When the redraw read it, `drawn_without_landing()` listed both rows as `premise_spent` with their
commits. That is the outcome this item wanted. The focus row's "DONE when neither id appears in the
drawn-never-landed list" cannot be met by any disposition: the list keeps every row drawn in the
last 24h and labels it, so both ids drop off only by age. Read it as "neither row is still
`landed_unbound`/`not_done`", which already held. `--premise-spent` on the focus id was refused
because the ledger already credits it with a landing after its last draw. `--release` then retired
it, and `_retired_ids()` keeps `_focus` from offering it again before the seat re-orients.
