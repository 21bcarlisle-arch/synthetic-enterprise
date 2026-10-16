**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The draw ledger grades by path, so work mid-landing, work spent and work that merely shares a path read alike

**Fate (2026-10-16): FIXED, both defects** (direction `the-draw-ledger-credits-by-the-items-work-not-by-path-overlap`).
(1) `_binds_item` no longer credits an unowned commit for touching a subject path; it must name the
id. Over the live ledger's last 14 days, 9 of 44 swept rows had read `landed_unbound` that way, each
on another item's commit (merges, a gas-electronics change crediting the home-mover item); all 9 now
read `not_done` with a `path_touched_by` hint. (2) `MID_LANDING` is a sixth disposition: a live
`surgical_land` (its argv, read from `/proc`) whose message names the id or which writes a path the
item asks to change, or an owned worktree holding it, and the draw's held-work check sees live
landings too. Controls: `tests/background/test_a_commit_sharing_only_a_path_credits_no_item.py`
(partition over landed / mid_landing / not_done, and the path-only refusal with its rare branch);
three mutations recorded there, each fired. NOT DONE HERE: the "majority of the item's paths" leg
this finding proposed — the direction is stricter (trailer or subject only), and a single-path
item whose tick skipped `--landed` now reads `not_done` with the hint, which is the honest answer.

**Fate (2026-10-15):** TRIAGE -- a machine-class known issue, carried as `the-draw-ledger-cannot-tell-mid-landing-from-not-done` in docs/direction/wrong_triage.yaml.
**Fate (2026-10-12, clear-the-decks):** ATOM -- no "landing now" fourth verdict or live-claim/majority-path check found in background/delivery_lane.py; mid-landing items may still read as not_done and a single shared path may still credit a landing (P2)

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
