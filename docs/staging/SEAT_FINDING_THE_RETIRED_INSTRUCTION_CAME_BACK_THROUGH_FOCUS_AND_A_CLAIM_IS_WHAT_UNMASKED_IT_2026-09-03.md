**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# The retired instruction came back through `focus`, and a claim is what unmasked it

**Class:** `controls_that_cannot_fail` (primary), `measurements_that_mirror` (secondary)
**Filed:** 2026-09-03, delivery seat, Lane 0, tick drawn 17:59
**Subject:** `background/delivery_lane.py::next_item` — the second loop, over
`direction_mod.unreachable_focus`.

## What was found

`ea1ba2a03` (16:41) fixed a refuted continuation winning the draw, by teaching
`seat_continuation.live()` to drop superseded entries. It shipped a leg that asserts the **draw**,
not just `live()` — deliberately, because "`live()` being right is not the property that matters".

It was still broken at 17:59. This tick — 78 minutes after the fix landed — was handed
`land-the-live-world-undecomposed-floor-leg`, the refuted instruction, whose text says the artefact
"already exists" and "the only thing standing between this and done is a `git add`". That file was
deleted by `ensure_worktree`'s `git clean -qfd` at 15:35. The tick spent its orientation proving
the cited file did not exist — for the **second** time, which is the thing `ea1ba2a03` was written
to stop.

The refuted entry came back through a **different store**. `seat_executor` promotes a continuation
into `focus` at derivation (the entry's own `done_means` records this: *"promoted automatically by
seat_executor at derivation, not written by a session"*). So a refuted instruction exists twice:

* in the continuation store, where `live()` now correctly retires it — `--list` prints
  `RETIRED … not offered`, and it is genuinely absent from `live()`;
* in `focus`, as a twin that never learned it was refuted.

`next_item` walks `focus` when the continuation loop declines. Reproduced against the live store:

```
live() ids            -> ['pick-up-the-relaunched-undecomposed-floor-leg']   # retirement works
held() claims         -> ['pick-up-the-relaunched-undecomposed-floor-leg', …]
next_item() ACTUAL    -> 'land-the-live-world-undecomposed-floor-leg'        # the refuted twin
```

## Why it read as fixed, and this is the part worth keeping

**The claim is what unmasks it.** While the correction is unclaimed, the first loop returns it and
the twin is unreachable — the bug cannot be observed. The moment a seat CLAIMS the correction, the
first loop skips it and the second returns the refuted twin.

So the defect is live for **exactly as long as the corrected work is actually being done**, and
dormant whenever nobody is doing it. A control that looks for it at rest will never see it. That is
also why the 17:36 seat got the correct doorbell and the 17:59 tick did not: the first draw claimed
it, and every draw after that fell through to the twin.

## Why its own test stayed green

`test_a_refinement_under_a_NEW_id_RETIRES_the_refuted_one_rather_than_LOSING_to_it` asserts
`next_item` returns the correction. It passes, and it cannot fail this way, because its fixture
inverts both production conditions:

```python
monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])
```

It stubs `focus` to empty — **deleting the store the twin lives in** — and leaves the correction
unclaimed, so the first loop answers and the fall-through never runs. The leg reaches the draw, as
its docstring intends, but only through the one path that was already fixed.

This is the R15 shape *"a control over a mixed subject reports the OR"*: two stores hold the same
instruction, one was taught to retire it, and the control only ever exercised that one.

## The fix

`next_item` now filters `focus` by the same supersession fact, via a `_retired_ids()` helper
reusing the existing public `seat_continuation.superseded()`:

```python
if item.get("id") and item["id"] not in taken and item["id"] not in retired:
```

Not keyed to the clock, matching `_superseded_ids`'s own rule — once superseded, always superseded.
A `focus` twin outlives its correction's window by design (`focus` is re-derived every three
hours), so an expiring correction must not resurrect the refuted instruction here either.

`_retired_ids` fails **open** — an unreadable store reads as nothing retired — and says so. The
conservative direction would offer no focus work at all, and a lane that silently stops delivering
is the six-day walkover `draw` documents. A re-offered stale item is visible to the tick reading
it; an empty lane is visible to nobody.

## The control

`test_a_retired_entrys_FOCUS_TWIN_is_not_offered_once_the_CORRECTION_is_CLAIMED` reproduces the
production conditions the existing leg stubs away: `focus` returns the twin, and the correction is
**claimed** before the second draw.

Claiming is an explicit act — `draw` claims, `next_item` does not. The first draft of this test
omitted the `claims_mod.claim` call and **the mutation survived**: without a claim the first loop
keeps answering and the `focus` loop is never reached. That near-miss is the finding in miniature,
and it is why the claim is called out in the test body rather than left as setup.

MUTATION (verified): drop `and item["id"] not in retired` and the leg fires —
`the tick was handed 'land-the-artefact'`. Restored: 16 passed.

## What this does not fix

The twin still exists in `focus`. This filters it at the draw rather than preventing the promotion,
because `focus` being re-derived from the tree every three hours is what makes it robust to a lost
continuation write, and a promotion that consults supersession at write time would be keyed to the
clock in the way `_superseded_ids` refuses. The filter is the property; the promotion is not.

Not measured: whether any **other** reader of `focus` carries the same twin. `next_item` is the one
that feeds ticks, so it is the one that was costing turns, but the two-store split is now known to
exist and nothing has swept for a third consumer.
