**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `OPS10_finding_class_consolidation`

# A time-bombed fixture went red on a calendar date, and the refusal named whoever's change pulled it into the selection

**Filed 2026-09-15 by the delivery seat (isolated worktree), claim
`the-no-caller-pattern-cannot-reach-its-own-archived-instance`.** RECORDED: repaired in the same
commit that found it. Not the subject of that claim — it was in the way of landing it, and this is
what it was.

## What happened

`tools.surgical_land` refused my commit with two reds in `tests/background/test_class_debt.py`:

```
E  ValueError: list.index(x): x not in list
FAILED test_an_accruing_undecided_class_is_work
FAILED test_an_accruing_class_outranks_a_finding_and_yields_to_a_persons_ask
```

**Proven pre-existing at clean HEAD**, not caused by my change, by extracting `HEAD` with
`git archive` into a fresh directory and running the same two tests there: same two failures,
none of my edits present.

## The cause: two clocks in one test

- `_accruing()` wrote its instances with a **calendar date in the filename**, `2026-08-30`.
- `_debt()` grades them against a **frozen** `TODAY = dt.date(2026, 9, 1)`.
- The two failing tests go through `sr.work_queue()`, which takes **no `today` and reads the real
  clock**, because the draw it serves is a real-time queue.

`ACCRUAL_WINDOW_DAYS = 7`. So the fixture and the wall clock agreed until **2026-09-06** and
disagreed from **2026-09-07**, at which point `class_debt.drawable()` stopped calling the class
accruing, `_with_accruing_class_registers` declined to splice the register, and an `index()` on a
name that was no longer in the queue raised.

The fixture was written on **2026-09-01** (`bfc43b427`). It was armed on the day it was committed
and had six days to live.

## The part that is worth more than the fix

**The refusal named nothing about its own subject.** `ValueError: x not in list` is what you get
from an `index()` call, and the actual condition — *the register was not promoted into the queue
because the class stopped accruing* — never appears, because
`_with_accruing_class_registers` is **fail-open by design** and returns the unmodified queue rather
than raising. The fail-open is correct (a draw that cannot rank its work must still see it) and it
is exactly what made the failure unreadable.

**And the red was attributed to whoever's change pulled it into the test selection.** The gate runs
a selection, not the whole suite, so this did not refuse every commit from 2026-09-07 onward —
`92aa394dd` landed on 2026-09-07, after it was already red. It waited, invisibly, for a commit
whose selection reached it, and then presented as *that commit broke class_debt*. A red that is
intermittent **by selection** rather than by flakiness is worse than a permanent one: it has no age,
it never accumulates, and it arrives as an accusation.

It is in no register: `docs/staging/reference/HEAD_RED_REGISTER.md` does not name it, because a red
that the selection usually skips is not a red the HEAD-red sweep sees either.

## The repair

Keyed to the property rather than to a date. `_accruing()` now stamps its instances
`dt.date.today() - 1 day` — which is what *"inside the accrual window"* actually means — so the
frozen and the real clock can no longer disagree, and no future date can make them. The two
assertions that spelled the fixture's filename out by hand now derive it from `_accruing_name()`;
retyping it is how one stale date acquired three homes.

The `day=` parameter is kept for the one test that deliberately wants instances OUTSIDE the window
(`test_a_class_that_stopped_recurring_is_not_drawn_however_expensive_it_was`), which is a property
too and a different one.

31 of 31 pass.

## What is still owed, and is not done here

Two separate things this turn did not do, either of which would have made the above legible:

1. **`_with_accruing_class_registers` fails open silently.** It should say, on some surface, that it
   declined to promote a register and why. The fail-open must stay; the silence need not.
2. **Nothing scans for fixtures that encode a calendar date near a windowed comparison.** This is a
   class, not an instance: any fixture whose meaning is *recent* and whose spelling is *a date* is
   armed the day it is written. A grep for a date literal in a test that also imports a
   `*_WINDOW_DAYS` constant would find the rest of them, and has not been run.

## Class registration

Belongs to `controls_that_cannot_fail` — a control that could not fail on its subject and then
failed on the calendar instead, reporting a condition unrelated to what it exists to check.
