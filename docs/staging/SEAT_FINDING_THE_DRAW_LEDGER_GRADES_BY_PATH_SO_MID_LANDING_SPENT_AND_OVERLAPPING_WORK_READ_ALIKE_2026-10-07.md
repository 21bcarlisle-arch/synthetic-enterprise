**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The draw ledger grades by path, so work mid-landing, work spent and work that merely shares a path read alike

*Console seat, 2026-10-07, from the triage of the delivery seat's carried "what it got wrong" items
(`docs/direction/wrong_triage.yaml`). Two carried items share one cause, so they share this home.*

## The cause

The draw ledger, `direction_path_check` and the continuation queue answer "did this item land?"
by asking origin whether a commit touched the item's named paths. That one question cannot tell
apart three states that need different actions: never started, landing right now, and already
spent. It also cannot tell an item's own landing from another item's commit on a shared path.

## The two defects

1. **Mid-landing reads as not done.** On 2026-10-05 the draw-follows-the-order item read
   `not_done` while it sat finished as `acff52923`. It recurred on 2026-10-06 (b7-slice-3 read
   "nothing to land" with its `surgical_land` running, and the queue still offered it) and on
   2026-10-07 (weighted-per-win-envelope, `surgical_land` pid 2895736). The queue re-offers work a
   lander already holds. Carried as `the-draw-ledger-cannot-tell-mid-landing-from-not-done`,
   18 listings.

2. **A path overlap is credited as a landing.** On 2026-10-07 the ledger graded
   `retention-guard-nets-the-companys-own-bad-debt-belief` `landed_unbound` against `81732ffe2`
   (W2_20's heating draw). The two share only one path from the item's long path list, and no
   netting code existed on any ref. This shape was corrected once before, for a `landed_elsewhere`
   verdict on 2026-09-30, and recorded in
   `SEAT_FINDING_TWO_LANDED_UNBOUND_ROWS_WERE_CREDITED_WITH_THE_NEXT_COMMIT_ON_A_SHARED_PATH_2026-10-04`.
   It has come back. Carried as `the-draw-ledger-credits-an-item-by-path-overlap`, 1 listing.

## What done means

- The ledger reads the live claim and landing state (`.seat_work_in_hand.json`, a running
  `surgical_land` for the item's id) before it grades. "Landing now" is a fourth verdict, and the
  queue does not offer an item in that state.
- A `landed_*` verdict needs the commit to name the item: by trailer, by claim id, or by a majority
  of the item's paths. One shared path is not enough. A single overlapping path is graded
  `cannot say`, not landed.
