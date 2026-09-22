# PRE-REGISTRATION — what `direction_path_check` says about the live continuation store

**Severity:** RECORDED
**Lane:** `H_harness`

A prediction, written before the measurement, about an instrument. RECORDED and not LATENT: it
asserts no live defect — the finding it was written to test is filed beside it.

*Written 2026-09-22 by the delivery seat, under claim
`the-hand-off-store-writes-items-blind-to-the-same-classifier-the-orientation-now-runs`, BEFORE
running anything.*

## The question

The commissioning item asks for `direction_path_check.grade_item` to be wired into
`seat_continuation.hand_off`, the third and last door prose reaches the draw through. Before wiring
it I want to know what it would actually SAY, because the module's own docstring names the failure
it would be walking into: *"a note that fires on everything is read by nobody."*

The worry is specific. `NOTHING_TO_LAND` fires when every path the item asks to be CHANGED is
identical to HEAD. For a focus item that says *"land this pile"*, that is a spent ask. For a
hand-off that says *"go and change file X"*, `already landed` is the **expected precondition** —
the work has not been done yet, so of course the file matches HEAD.

If that is right, the concern as written is the wrong measurement for this door, and wiring it
unchanged ships a note that fires on nearly every hand-off.

## The prediction

Over the entries live in the shared continuation store right now:

1. **A majority of live entries raise `NOTHING_TO_LAND`.** Concretely: **≥ 3 of the live
   entries**, and I expect the true fraction to be most of them.
2. **`REVERTING_REMEDY` fires on none of them**, because a hand-off is written before the work
   exists and has no occasion to prescribe `isolate_hunks`/`--content` over a stale copy.
3. My own drawn item (`the-hand-off-store-writes-items-blind-...`) is one of the entries that
   fires, and its work is entirely real — so the first instance I look at is already a
   counter-example to reading the concern as a verdict.

This is a prediction about an INSTRUMENT, not about the world: it says what the classifier does
when pointed at a store it was not written for. If (1) holds, the right build is **not** a
straight call.

*Result and whether this was refuted: filed beside this, in the SEAT_RESULT note for the same
claim.*
