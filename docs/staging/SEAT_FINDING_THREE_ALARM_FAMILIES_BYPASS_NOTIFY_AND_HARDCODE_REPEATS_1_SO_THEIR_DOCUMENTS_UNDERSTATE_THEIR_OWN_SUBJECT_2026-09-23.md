**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** unminted

# FINDING — three alarm families bypass `notify()` and hardcode `repeats=1`, so their documents understate their own subject by two orders of magnitude

Found while building the alarm re-ask (landed `465a0dfca`), by following the thread of why four of
eleven alarm families have no key in `.notify_transitions.json`. The re-ask does not need this fixed
— it reads the documents' own dated lines precisely because the store is unreliable here — so this
is filed rather than routed around.

## The measurement

Three callers reach `alarm_repetition.escalate()` **directly**, never through `notify()`:

| caller | line | key | `repeats` passed |
|---|---|---|---|
| `background/seat_continuity.py` | 670 | `seat-continuity` | `1` |
| `background/seat_work_in_hand.py` | 410 | `seat-claim:{work_id}` | `1` |
| `background/delivery_lane.py` | 356, 377 | `delivery-lane-stranded:{focus_id}` | `1` |

All four call sites pass the literal `1`. So every document these families file opens with:

- `SEAT_CONTINUITY_2026-09-15.md`: *"fired **1 times without its state changing**, over **95.9h**"*
- `SEAT_CLAIM_2026-09-15.md`: *"fired **1 times without its state changing**, over **95.5h**"*
- `DELIVERY_LANE_STRANDED_2026-09-18.md`: *"fired **1 times without its state changing**, over **1.7h**"*

`SEAT_CONTINUITY` carries eight consecutive days of still-live lines and eighteen instances.
`SEAT_CLAIM` gained four new instance lines on 2026-09-23 alone. Their headers say it happened once.

## Why this is a defect and not a cosmetic slip

**The document's own body states the standard it fails.** Every one of these documents says, in
prose `escalate()` wrote: *"The repetition is the finding. Something is failing the same way on a
loop and nothing is converging on it."* A header stating a repetition count of **1** is the weakest
possible reading of exactly the thing that justifies the document existing — and it is the first
line a draw sees.

**It defeats the module's own threshold.** `ESCALATE_AFTER_REPEATS = 3` exists, in its own words,
because *"a single retry that then succeeds is noise in the draw, and a draw full of noise is the
treadmill."* `notify()` enforces it (`if repeats >= _ESCALATE_AFTER`). A direct `escalate()` call
with `repeats=1` is **below the bar the constant exists to set**, and nothing refuses it. Three of
the eleven families in the queue have never been asked to clear it.

**It propagates into the still-live lines.** `_note_still_live` is passed the same frozen constant,
so `DELIVERY_LANE_STRANDED` has four daily lines each reading *"1 repeats over 1.7h"* — identical
numbers every day, because they are not measurements of anything.

**And the direction matters.** These documents sit at ORDER 60, below every human ask, in a queue
where nothing above them ever empties. Understating the subject in the direction that makes it look
like a one-off is the direction that keeps it there. This is a plausible partial answer to why the
alarm backlog was never drawn, and it is checkable against the draw log rather than assumed.

## What it does NOT claim

Not that the three callers should go through `notify()`. They may have good reasons not to — the
transition store's paging suppression is not obviously what a stale-claim sweep wants, and
`seat_work_in_hand`'s own docstring says `escalate()` is called directly deliberately. **The defect
is the hardcoded `1`, not the door.**

## The remedy, and the question it turns on

The honest count is already on disk: the document's own instance and still-live lines are the record
of how many times the condition has been observed. So the candidate fix is for `escalate()` to
DERIVE the count from the live document when it finds one, rather than trusting a caller's argument
— which would fix all four call sites at once and any future one, instead of patching three (R10:
the class, not the instance).

The design question a next turn has to settle before writing it: `repeats` currently means
*consecutive firings without a state change*, which is a `notify()` concept the direct callers have
no access to. Deriving it from the document would change the meaning to *observations recorded*.
Those are different quantities and the header prose would have to change with it — **say what the
thing is before measuring it.** Two sound options: rename the field for everyone, or give the
document a second, separately-named count. Do not difference them.

`tests/background/test_alarm_repetition.py` already has the fixtures for this
(`_file_alarm`, `_population`) from the re-ask work.
