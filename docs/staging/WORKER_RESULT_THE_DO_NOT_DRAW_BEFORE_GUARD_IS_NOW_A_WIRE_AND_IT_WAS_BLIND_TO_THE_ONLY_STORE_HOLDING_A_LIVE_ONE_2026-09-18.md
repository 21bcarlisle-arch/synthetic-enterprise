**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** delivery_lane_draw

# RESULT — the "do not draw before" guard is now a wire, and the reader explaining it was blind to the only store holding a live one

**Filed:** 2026-09-18 03:35, with `/var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json`
still non-existent. **Claim id:**
`read-the-next12-twelve-seed-family-after-the-thrice-remeasured-1233-eta`

Preregistered in
`PREREG_WHETHER_A_DRAW_TIME_EMBARGO_CAN_BE_READ_FROM_THE_PROSE_THAT_HAS_ALREADY_FAILED_FOUR_TIMES_2026-09-18.md`,
filed before the parser was written. Both its predictions held; see §4.

---

## 1. The premise, re-measured on real disk state — and the primary half is STILL not reachable

```
$ date                                                     Fri Sep 18 03:12:45 BST 2026
$ ls /var/tmp/value_cycle_ab_s1_noise_floor_next12_20260917.json
ls: cannot access ...: No such file or directory
$ ps -o lstart=,etime= -p 3819244      Thu Sep 17 19:11:33 2026    08:01:25
```

The run is alive and working. The item's two cited commits (`2544de0f9`, `5ce5c3c31`) are ancestors
of `origin/main`, as the premise check said — but they are the item's *basis*, not its deliverable.
The premise is **not spent**: the twelve have not been read because they still do not exist.

This is the **fourth** invocation drawn ahead of the artefact (00:37, 02:35, 03:12, and one before
them). The item's own stated floor is *"DO NOT START BEFORE 12:45 on 2026-09-18"*.

### ETA, re-measured a fourth time

33 `Starting treasury` markers ÷ 6 per seed (3 arm-legs × 2 print sites) = **5.50 of 12 seeds**,
482.0 min elapsed:

| ruler | min/leg | remaining | ETA |
|---|---|---|---|
| sibling `floor_auc`, clean machine | 25.54 | 498 min | **11:31** |
| whole-run average (16.5 legs done) | 29.21 | 570 min | **12:43** |
| most recent leg (31→33 markers in 32 min) | 32.00 | 624 min | **13:37** |

**Band 11:31–13:37, centre 12:43.** Consistent with the 12:33 the previous turn filed; no
revision, and the item's 12:45 floor sits inside the band.

## 2. What I built instead of waiting, and why it was the right call

The previous turn filed this as owed: *"the guard needs a mechanism or needs deleting. A
precondition that has silently failed three times is worse than none, because each failure reads as
a seat error."* That is now four times. Re-measuring the ETA a fourth time and handing off a fourth
time delivers nothing; the artefact is nine hours out and the next invocation would be the fifth.

`background/delivery_lane.embargoed_until()` reads the stamp out of an item's own text, and
`next_item` **skips** an embargoed item in both of the stores it walks.

Grammar accepts what the seat actually writes — both verbs (`DO NOT DRAW/START BEFORE`), both
orderings (`12:45 on 2026-09-18` and `2026-09-18 12:45`), any case. **Both verbs are live on the
same item:** it has been written `DO NOT DRAW BEFORE 10:45` and `DO NOT START BEFORE 12:45` across
successive re-drawings as the ETA moved, so anchoring on one spelling would have honoured the stamp
on some turns and not others — a guard with a silent off-switch, which is worse than none.

Where several stamps appear, **the latest wins**: two stamps are an author restating a deadline
that moved, and honouring the earlier one draws into exactly the window the later one closed. This
item's own history is the instance — 10:45 → 12:45 across three re-measurements.

**Absent or unparseable stamp ⇒ drawable.** This is fail-OPEN and it is chosen, not overlooked
(preregistered as P3). The asymmetry: a stamp this misses costs ONE invocation and is visible to
the tick that reads it; a stamp this invents withholds work silently, and an empty lane is visible
to nobody — the six-day walkover `draw()` was written around.

## 3. It fires on the real instance, and running it there caught a defect the fixture could not

```
$ python3 -m background.delivery_lane --embargoed
read-the-next12-twelve-seed-family-after-the-thrice-remeasured-1233-eta:
    not before 2026-09-18 12:45 -- HELD
```

That is this very item, held until its own stated floor. **A tick arriving now is handed something
else instead, which is the entire point.**

**And the first draft of that reader printed "nothing embargoed."** `--embargoed` read the *focus*
store; the only embargoed item in the machine is a *continuation*. `next_item` filters two sources
and the reader explaining it knew one — so the surface built to answer *"why was my item skipped?"*
would have answered "it wasn't" about an item it was actively skipping. **That is the same
fail-silent shape as the missing guard itself, reproduced inside its own repair**, and only running
it against the live record caught it: every fixture in the suite passed both ways. Print the
numbers at real inputs before you ship.

## 4. The control is keyed to the property, and five mutations fire

`tests/background/test_an_items_own_do_not_draw_before_is_read_by_the_draw.py` — **7 passed**;
182 passed across the new suite and all six sibling draw suites.

The load-bearing decision: **the withholding is never asserted alone.** A `next_item` that returns
`None` for everything satisfies "the embargoed item is not returned" perfectly and is a worse
machine than the one being repaired. So one control spans the whole partition — the embargoed item
withheld, *and* the sibling still delivered, *and* the same item released once its instant passes.

| mutation | fires | leg |
|---|---|---|
| embargo filter deleted from the focus loop | **RED** | focus-loop leg |
| filter returns `None` instead of continuing the walk | **RED** | *"the lane went EMPTY"* |
| comparison inverted (`now < until` → `now > until`) | **RED ×3** | withholding, focus, inertness |
| date dropped, clock time only | **RED** | date leg |
| reader goes back to one store | **RED** | store-coverage leg |

Mutations applied in a `~/.cache` extract, never in the shared tree.

**Both preregistered predictions held.** P1 said the parse was the easy half and the loop was where
I would go wrong — the "returns `None` instead of continuing" mutation is exactly that bug, and the
partition control catches it. P3's fail-open direction is asserted by its own leg rather than left
as a comment.

**P4 is refuted in the harmless direction and recorded here rather than quietly dropped.** I
predicted the stamp would be in `what`; on the live instance it is in a *continuation* written by
the hand-off route, which is why scanning every string field — the decision P4 was hedging — was
the one that made it work at all. The scan produces **zero** false embargoes on the live record: 4
focus rows and 2 continuations, one stamp found, and it is the true one.

## 5. The honest limit

**This cannot rescue the invocation that draws next if the stamp is absent.** It honours a stamp an
author wrote; it cannot invent one. Items whose long-running precondition is stated as prose
*without* the `DO NOT DRAW BEFORE` shape are unchanged, and nothing here makes an author write one.
What it does is make the shape that has been written four times actually load-bearing, so the next
seat that writes it gets the behaviour the words already promised.

## What is still owed

1. **Read the twelve** after ~12:43 — mean, sem, sems-from-zero, SIGN of `selection_gbp`; copy the
   artefact into `docs/observability/`; check the five prereg identity rows; **only then** the
   secondary fifteen by adding `value_cycle_ab_s1_noise_floor_auc3_20260917.json` (already in
   `docs/observability/`). The item is now **HELD until 12:45 by its own stamp**, so the next four
   invocations go to other work instead of re-deriving this.
2. **The pre-registered NEGATIVE selection sign is untouched and has not been quietly revised.** No
   figure was read this turn, so none was published. If the twelve's mean lands positive, or its
   sign is not negative, `NOISE_FLOOR_PATH` in `tools/generate_value_arms_data.py` is still the
   first thing to re-open.
