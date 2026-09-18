**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** delivery_lane_draw

# PREREGISTRATION — whether a draw-time embargo can be read from the prose that has already failed four times

**Filed:** 2026-09-18 03:20, BEFORE writing the parser or running a single mutation.
**Claim id:** `read-the-next12-twelve-seed-family-after-the-thrice-remeasured-1233-eta`

---

## The thing being decided

`docs/direction/DIRECTION.yaml` items carry a line of the shape

```
DO NOT START BEFORE 12:45 on 2026-09-18
```

(the same item has also been written `DO NOT DRAW BEFORE 10:45 on 2026-09-18`). **Nothing reads
it.** It is prose inside a work description, and the draw that hands the item out has never looked
at it. Four consecutive invocations — 00:37, 02:35, and this one at 03:12, plus the one before
them — have been spent arriving before the artefact they were sent to read could exist.

The prior turn filed this as owed: *"the guard needs a mechanism or needs deleting. A precondition
that has silently failed three times is worse than none, because each failure reads as a seat
error."* This preregisters the mechanism.

## What I predict, before building

**P1 — the parse is the easy half and the LOOP is where this will go wrong.** My predicted defect
is not the regex: it is that skipping an embargoed item returns `None` and idles the whole lane,
rather than walking on to the next eligible item. I expect to write that bug and expect the
partition control to catch it.

**P2 — the mutation that will NOT fire on a naive control.** A control that asserts only "an
embargoed item is not returned" is passed by a `next_item` that returns `None` for *everything*.
That is this project's most-repeated control failure and I am writing the control over the whole
partition to forbid it: the same assertion must show the embargoed item withheld AND a sibling
item still delivered AND the same item delivered once its instant passes.

**P3 — direction of failure on an unparseable stamp: OPEN, deliberately.** An item whose stamp I
cannot parse stays drawable. I predict a reviewer will call this fail-open and be half right. The
asymmetry is real and is the reason: a false negative costs ONE wasted invocation, which is the
status quo and is visible to the tick that reads it; a false positive silently withholds work and
an empty lane is visible to nobody — the six-day walkover `draw()` documents. I am recording the
choice here so it cannot later be presented as an oversight.

**P4 — I predict the stamp is in `what` and NOT reliably only there.** I will scan every string
field of the item rather than the one field today's instance happens to use. Prediction: scanning
`why` as well introduces no false embargo on the live direction record, because only a stamp with
a FUTURE instant defers anything, and rhetorical mentions of past dates are inert by construction.
**If a live focus item is deferred by this that should not be, P4 is refuted and the scan narrows
to `what`.**

## What would refute the whole thing

- The mechanism defers an item the machine should have drawn → wrong direction, revert.
- Both mutation legs below fail to fire → the control cannot fail and must be rewritten before the
  code lands.

## The mutation table I am committing to run (answers unknown at filing)

| mutation | must fire |
|---|---|
| embargo filter deleted from the focus loop | the withholding leg |
| filter returns `None` instead of continuing the walk | the sibling-still-delivered leg |
| comparison inverted (`now > until` → `now < until`) | the expiry leg |
| stamp parsed but the date ignored (time-only) | the withholding leg, on a stamp whose TIME has passed today but whose DATE is tomorrow |

Filed before any of these were run. The results go beside this file, in the RESULT, whichever way
they land.

## What this preregistration does NOT cover

The twelve-seed read itself. That artefact still does not exist — re-measured this turn at 33
`Starting treasury` markers, 5.50 of 12 seeds, ETA band **11:31–13:37** with the whole-run average
at **12:43**. The prediction filed in two preregs — that the twelve's mean is NEGATIVE, and that a
positive re-opens `NOISE_FLOOR_PATH` in `tools/generate_value_arms_data.py` — is untouched and has
not been revised.
