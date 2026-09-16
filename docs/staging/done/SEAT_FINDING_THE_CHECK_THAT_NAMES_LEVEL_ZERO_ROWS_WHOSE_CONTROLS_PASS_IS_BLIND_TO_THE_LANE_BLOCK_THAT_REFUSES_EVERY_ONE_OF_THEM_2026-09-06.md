**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** H41_the_map_ratchet_has_no_ongoing_drain

# The check that names level-0 rows whose controls pass is blind to the lane block that refuses every one of them

**Found:** 2026-09-06, delivery seat, while actioning the LANE 0 DELIVERY item the doorbell drew —
*"four rows at `level_current: 0` whose own controls pass … run the controls its `file_scope` names,
move the level to what the run earns."*

---

## The measurement

Four rows were named: `SPINE_1_scenario_world_state`, `H41_the_map_ratchet_has_no_ongoing_drain`,
`SITE4_ia_register_and_nav`, `PB4_engagement_separated_from_elasticity`.

```
  SPINE_1  already at level_current: 2   -- another lane moved it before the tick fired
  H41      lane H_harness   -- level move REFUSED at the writer
  SITE4    lane H_harness   -- level move REFUSED at the writer
```

`background.gate_authorization.record_level_up_self_certified` raises `LaneBlockedError` for both:

> OPS11: the level-raise on `H41_…` is REFUSED — lane `H_harness` holds **13 live BLOCKING
> finding(s)**, so a new level here would be certified by an instrument this lane's own findings say
> may be wrong.

So of the four rows the check told the seat to move, one had already moved and two **cannot** move —
not for want of evidence, but because the lane they live in is blocked by construction. The check
asks "do this row's controls pass?" and never asks "would the writer accept the answer?".

## Why that is a defect in the check and not in OPS11

OPS11 is right, and the correct action here was to leave the level at 0 and land the work anyway
(H41's mechanism is built and proven; the row records the hold). `record_limitation_accepted` would
have moved the number today and is exactly the laundering the rule exists to stop.

The defect is that the check **spends the seat's turn** on rows whose outcome is already determined,
and reports them in the same voice as rows that would actually move. A seat reading the doorbell
cannot tell "this row is one control-run from level 2" from "this row is thirteen findings from
being ratifiable at all", and those are different pieces of work — the second one is *drain the
lane*, which is not what the item says to do.

## The residual this sits beside

The same doorbell item already names the bigger hole: **28 of 34 level-0 rows name no control a
runner can execute**, so the check is silent on the majority. This is the same class one turn
further on — the six it *can* see are filtered by a criterion (controls pass) that is necessary and
not sufficient.

## What would close it

One predicate, at the point the check ranks a row: `refuse_level_raise_if_lane_blocked` is already
importable and already pure enough to ask without writing anything. A row whose lane is blocked is
still worth reporting — but as *"H_harness: 13 blocking findings gate 2 ready rows"*, which is one
line naming the actual next action, instead of two rows that read as ready and are not.

**Not minted as its own atom.** It belongs to whatever owns the orientation check, and the seat's own
direction on this item says the fix goes at the *minting path*, not into a sweep. Filed so the next
orientation has the measurement rather than rediscovering it.

## Prediction, filed before the answer is known

If the check gains the lane-block predicate, the four-row list becomes a one-row list plus one lane
line. If instead the H_harness findings are drained first, H41 and SITE4 ratify with no further
control work — their runs are already recorded (H41: 70 controls across two suites; SITE4: 38, with
13 mutation legs). Whichever happens first refutes the other reading of "these rows are ready".
