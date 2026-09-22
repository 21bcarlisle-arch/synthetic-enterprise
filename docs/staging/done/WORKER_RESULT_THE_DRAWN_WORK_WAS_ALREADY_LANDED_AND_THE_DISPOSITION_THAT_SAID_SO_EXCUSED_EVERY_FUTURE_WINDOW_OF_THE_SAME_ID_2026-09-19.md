**Severity:** LATENT · **Lane:** H_harness · **Epoch:** 3 · **Atom:** delivery-lane-disposition

# The drawn work was already landed, and the disposition that said so excused every future window of the same id

**Drawn:** `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach` (Lane 0,
delivery seat). **Turn:** 2026-09-19, scheduled tick.

---

## The disposition first: nothing was owed

The item asked for two paths — `docs/staging/SEAT_RESULT_THE_PRODUCT_GATE_REFUSES_CAP_SEGMENTS_NOT_DECISIONS_AND_EVERY_DECISION_THAT_EXISTED_WAS_DECIDED_2026-09-19.md`
and `tools/svt_refusal_census.py` — to be landed, on the premise that they were untracked in the
shared tree. **They were not.** Both are tracked, clean, and present at `origin/main` in
`209f26be4` (`answer(A_strategy): the product gate refuses cap segments, not decisions...`), which
is an ancestor of `HEAD`. The content was checked at `origin/main`, not inferred from the sha —
`ANCESTOR SHA != landed CONTENT` is the trap this project has paid for before.

Nothing was redone. `UPLIFTABLE_TARIFF_TYPES` was not touched. The census was not re-run.

The paths are now **bound** to the claim (`--landed ... --commit 209f26be4`, 3 paths:
the two named plus `docs/design/orphan_baseline.json`). Before that bind the row read
`last_landing_at: None` with `last_landing_paths: []` — the lane could not see, by any surface it
has, that the work it had drawn three times was finished and published.

## The finding: the excuse outlived the window it was written for

The prior invocation had already filed the correct disposition — `premise_spent`, stamped
**04:37:43Z**, citing `209f26be4`, reason: *"the claim was swept by the 100-minute sweep while this
turn's gate ran, so `--landed` bound nothing"*. That is an accurate, well-formed record.

The item was then **re-drawn 216 seconds later, at 04:41:19Z.**

That redraw is not itself the defect — `premise_spent` is a reporting disposition and was never
meant to gate the draw. The defect is what the redraw exposed. `_disposition` in
`background/delivery_lane.py` opens with the two hand-written dispositions, and the docstring
directly above them argues the across-windows fail-open in so many words:

> A STALE CREDIT DOES NOT SETTLE A NEW WINDOW. `landed_under` sits on the row forever, so a
> credited id that is DRAWN AGAIN and lands nothing has both the credit and a genuine second miss.
> Reading the old credit as an explanation would let one join silence every future draw of the same
> id — the across-windows fail-open. The instant is therefore compared against THIS draw.

**The instant was compared for `landed_under`. It was not compared for `premise_spent`, one branch
above it**, which returned on the presence of a commit and nothing else. The guard was written
once, attached to the second of the two branches, and read ever after — including by me, on first
reading — as a property of both. The paragraph describing the hole sits directly on top of it.

Measured, before any repair:

```
window A (drawn=100, credit stated at 150): premise_spent   <- correct
window B (drawn=200, SAME credit at 150):   premise_spent   <- a new miss, wearing the old excuse
```

`note_premise_spent` has stamped `at` since the day the field existed, so the instant needed for
the comparison was **already on every row**. Nothing had to be collected; it simply was not read.

### Scale: one live instance, and it is the row I was holding

All 7 rows in the live draw ledger carrying `premise_spent` were surveyed. Exactly **one** is
stale-across-windows: `measure-whether-the-product-gate-is-the-real-ceiling-on-the-methods-reach`,
this turn's own item. Its 04:37 sentence was set to explain the 04:41 window and every window after
it, for ever.

That single instance is *not* evidence the class was nearly harmless, and the direction matters:
an id accumulates redraws precisely **because** it keeps not landing, so the rows that reach a
second window are exactly the rows a seat has already spent turns on. The two readings want
opposite actions — a real miss says *draw it again, it is workable*; a spent premise says *there
was nothing left to deliver* — and the fail-open converted the first into the second silently.

In this instance the stale reading happened to be **true**: the premise really was spent by
`209f26be4`. It was right by luck, not by the guard, which is the flattering reading this project
has a rule about.

## The repair

`_disposition` now compares the stated instant against **this** draw, exactly as the branch below
it always did. New helper `_stated_at` answers `0.0` — the loud direction — for a row that will not
say when, because a hand-edited or truncated row cannot say which window its sentence explains, so
it explains none of them. It answers `0.0` rather than raising: `_disposition` is what the
orientation brief calls for every swept row, and a reader that crashes on one bad row takes the
brief's whole reading with it.

**The cost is deliberate: a disposition is now per-window.** An id drawn again needs its premise
restated against the new window, and a sentence nobody is willing to restate was never an
explanation of that window to begin with.

`tests/background/test_a_stated_disposition_explains_its_own_window_and_not_the_next_one.py` —
keyed to the property (*a hand-written disposition explains the window it was stated in, and never
a later one*), with no live id, sha or count asserted anywhere. Both readings are asserted over
**one row** differing only in which draw instant it is read against, so neither a guard that
credits everything nor one that credits nothing survives. The `landed_under`/`premise_spent` pair
is parameterised into a single control, because one branch having the guard and the other not is
the whole defect.

Seven mutations were run in memory and **all seven fire, each caught by the leg its docstring names
for it** — including `(c1) >= to >`, caught only by the boundary control that straddles the edge by
one second, and `(f) drop the guard from landed_under`, caught only by the paired control.

### The sibling fixtures were asserting a shape no producer can make

Three partition controls reddened on the repair — and that is the finding's second half, not
collateral. `test_a_swept_row_asks_git_whether_the_work_landed_under_another_name.py`,
`test_a_window_that_closed_before_its_own_subject_existed_says_so.py` and
`test_every_disposition_names_what_was_checked.py` each hand-built
`premise_spent={"commit": ..., "reason": ...}` **without `at`** — a row the sole writer of that
field cannot produce. Those fixtures are how the hole stayed invisible: every control over this
partition was fed a shape in which the missing comparison could not show.

They are now faithful to the producer, each carrying a comment saying why `at` is part of the
shape. Note that `test_a_swept_row_names_which_of_the_three_dispositions_it_was.py` — the one
control that drives the **real** `note_premise_spent` instead of hand-building the row — stayed
green throughout, from both sides of the repair. The producer path was always correct; only the
fixtures modelling it were not.

## Attribution of the reds seen this turn

Four tests fail in `tests/background/`: two in `test_publish_gate_wedge_draw.py` and two in
`test_self_clearing_alarm_census.py`. **None are mine.** The same four fail identically with
`HEAD`'s `background/delivery_lane.py` loaded in place of the repaired one — one variable swapped,
everything else held. `test_self_clearing_alarm_census.py::test_every_live_hit_is_dispositioned`
is a registered HEAD red standing since 2026-09-04.

## What this does not claim

It does not claim `premise_spent` should stop a redraw. It is a reporting disposition and the draw
does not read it; whether the draw *should* is a separate question this turn did not settle, and
the honest note is that the item was re-drawn 216 seconds after its own disposition was filed and
the machinery was working as designed when it did.
