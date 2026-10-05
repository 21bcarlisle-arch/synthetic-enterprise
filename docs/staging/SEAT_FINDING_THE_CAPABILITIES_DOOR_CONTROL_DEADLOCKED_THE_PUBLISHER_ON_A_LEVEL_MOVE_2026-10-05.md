**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `SITE7_capabilities_tab`

# The capabilities door's status control deadlocked the publisher on the first level move that changed a stage

Claim `the-shared-checkout-reaches-origin-so-the-publisher-can-publish`, seat executor 2026-10-05 ~16:00 BST.

## 1. The drawn premise was already spent

The item asked for the shared checkout to be advanced to origin past nine colliding dirty paths
(`behind_origin`). At draw time the shared tree read `0 0` against `origin/main` (575ede43c): the
reconciler had already advanced it. The claim in `.seat_work_in_hand.json` the duplicate-work check
cited was this draw's own write (22 s old, no rival seat or `surgical_land` on that id in `ps`).

## 2. The live refusal is a different cause

`.publish_gate_state.json`'s newest failure (run_complete_20261005T142640Z, publish at 7a3cdd060)
is `gate_refusal`, one red: `site/capabilities/test_capabilities_door.py::test_status_matches_the_record_for_every_entry`
— "The collections journey, end to end: Planned != Building". Its `citation_at_head: dead`
(green at HEAD) is true and misleading: the red exists only in the publish commit's tree.

Mechanism, measured:

- `publish_from_a_clean_tree` builds `capabilities_door.json` in a clean checkout of HEAD, so it
  reads HEAD's COMMITTED `site/data/maturity_map.json` — EP4 `level_current: 0` (Planned). Its
  docstring states the one-cycle lag as the deliberate trade.
- The same publish regenerates `maturity_map.json` in the working tree from the yaml, where
  `8f5518e88` (12:57 today) moved EP4 to 2 — Building.
- The control compared the door against the working-tree map feed, so it reds the publish commit.
  Only the publisher commits the map feed, so the next cycle reads the same stale committed copy
  and reds again: **a permanent deadlock from any level move that changes a capability's stage.**

## 3. Remedy

The three status-vs-record controls (`test_status_matches_the_record_for_every_entry`,
`test_the_use_case_status_is_recomputed_from_the_record`,
`test_the_waiting_condition_names_only_truths_that_are_actually_missing`) now read the map feed at
the commit the door's own `published_from` stamp names, when the stamp vouches the inputs were that
commit's bytes; otherwise the working-tree map feed as before.

- With the publish's own bytes (door + regenerated map copied from the shared tree): 44/44 green.
- Mutation: the same bytes with EP4's entry flipped to `Building` — the control reds.

What this gives up, said plainly: a door frozen at an old stamp now passes these three controls,
because it matches the record it says it read. Staleness of the published door is the publish
liveness surface's question (`last_landed_publish`), not a status control's.

## 4. Not done here

`test_every_capability_cites_work_that_exists` still reads the working-tree map feed. An atom
leaving the live map (closed and refiled) would deadlock the same way; it has not happened and is
left as is.
