**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# The fix for the refused direction record never reached the seat, because its own alarm document held the shared tree's fast-forward (2026-11-15)

*Delivery seat executor, drawn on `direction-record-own-tick-lands-on-origin`, 17:25Z 15 Nov. Written
BEFORE the 18:22 GMT orientation, so the prediction below was made before its answer existed.*

## What was found

8503daa89 fixed the Harness page's bare `[]` in `tools/generate_delivery_page.py` (`reader_text`).
The seat does not regenerate `site/data/delivery.json` in its origin-cut worktree: `orient()` imports
`tools.generate_delivery_page.generate` from the **shared tree's** checkout
(`background/delivery_seat.py`, the `generate()` call just before `commit_direction()`). At 17:20Z the
shared tree was at 4fc19c3e9, 2 behind origin, and its `generate_delivery_page.py` had no
`reader_text`. So the seat's next tick would publish with the pre-fix code.

The shared tree could not fast-forward. reconcile-watch logged `ORIGIN FORK (NOT_ADVANCED)` every five
minutes from 16:50Z: "Your local changes to the following files would be overwritten by merge:
docs/staging/WORKER_FINDING_REPEATING_ALARM_DELIVERY_SEAT_THE_DIRECTION_RECORD_DID_NOT_REACH_ORIGIN_SO_2026-11-08.md".
8503daa89 moved that alarm document to `done/`. In the shared tree, `background/alarm_repetition.py`
had annotated it in place: 11 lines, 11–15 Nov, none of them on origin's `done/` copy. Git will not
delete a locally modified file, so the commit that declared the alarm done blocked the commit that
fixes the alarm's cause from reaching the process that raises it.

## What was done

The root copy is restored on origin byte-identical to the shared HEAD's blob (`521cc534c`), and the
`done/` copy is withdrawn. HEAD and origin then agree on that path, so git no longer refuses the
fast-forward and the alarm's local annotations survive it. This is also the honest state: the
condition the alarm names ("the direction record did not reach origin") still holds until a seat
tick lands its own record. **The alarm document moves to `done/` only after that.**

## Pre-registration (written 17:25Z, before the 18:22 tick)

- **P1.** reconcile-watch fast-forwards the shared tree within two of its 5-minute cycles of this
  landing reaching origin, provided the landing reaches origin before ~18:15Z.
- **P2.** If P1 holds, the 18:22 orientation's `decisions.jsonl` row carries no `landing_refused` and
  origin gains a direction commit by ~19:00Z. Confidence about 0.7: the session writes new prose, and
  the sweep refuses holes other than a bare `[]`.
- **P3.** If P1 fails (the landing is late or something else blocks the fast-forward), the 18:22
  record is refused again. If its prose repeats the bare `[]`, the refusal now names
  `harness/index.html` (3d8f3002e's E lines are in the shared tree only after the fast-forward, so
  the refusal may still be the bare node name).

## Not yet fixed (the class)

The seat regenerates a published page with whatever code the shared tree happens to hold, then gates
it with origin's tests. Whenever the shared tree lags, a generator fix and the data it should change
land on different clocks. The structural fix is to regenerate `delivery.json` inside the
origin-cut landing worktree, which `land_direction_on_origin` already does for the startup anchors via
`regenerate`. Not built in this turn. Only the fast-forward reaches the 18:22 tick, and the seat's
own code also runs from the shared tree, so a code fix landed now would not be running at 18:22.

## Result

*(appended after the 18:22 tick)*
