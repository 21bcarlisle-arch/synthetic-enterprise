**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** (Lane 0 delivery — `the-level-selection-retake-died-twice-and-its-own-correction-asserts-it-live`)

**Knowledge:** none new. This scores a standing preregistration and publishes a bound; no domain
constant moves.

# RESULT — the selection leg is not distinguishable from zero, and the share is readable for the first time

Beside `SEAT_PREREGISTRATION_WHAT_THE_UNDECOMPOSED_FLOOR_LEG_MUST_RETURN_IN_THE_LIVE_WORLD_2026-09-03.md`,
`SEAT_RESULT_THE_CURRENT_BOOK_RETAKE_LANDED_AND_ITS_SPLIT_IS_STILL_UNREADABLE_2026-09-08.md` and
`SEAT_FINDING_THE_RETAKE_DIED_A_THIRD_TIME…_2026-09-08.md`. All stand; none is edited. **The record
beside this one says the split "is still unreadable". On the evidence below that is now out of
date, and this file supersedes it rather than editing it.**

## The floor leg landed

Launched 02:39:56, finished **05:10:28, `rc=0`**, `Result=success` — the fifth launch of this
family and the second to survive, both under a transient user unit.

| | |
|---|---|
| artefact | `docs/observability/value_cycle_ab_s1_noise_floor_20260908.json` |
| mode | `all` — the undecomposed floor, the only mode whose spread bounds the published figure |
| seeds | 11111 / 22222 / 33333, 928 elasticity draws re-drawn, 0 held |
| world | `39a192ce04c1eda8` — **the same world as the arms** |
| commit | `04361d6c7` — **the same commit as the arms** |
| stamp | 04:10:26Z against the arms' 00:19:54Z — **the bound is newer than the figure it bounds** |

All four conditions the constant's own comment demands. Both constants moved **together**, which is
the only legal way to move either.

## The result

| leg | across the three re-draws | crosses zero? |
|---|---|---|
| **level** | £18,582.41 / £20,337.28 / £19,569.26 — mean £19,496, sd £880 | **no** |
| **selection** | +£1,199.55 / −£3,075.22 / +£433.07 — mean **−£480.86**, sd £2,279.22 | **yes** |
| whole advantage | mean £19,015, sd £1,522 | no |

`selection_distinguishable_from_zero`: **false**. SEM £1,315.91 against a published point estimate
of £270.21 — the draw sits at 0.21 standard errors from nothing.

**The published single draw is the flattering end of its own family.** The three-arm run reported
selection at **+£270.21**; the family it belongs to averages **−£480.86** and its widest draw is
−£3,075. The page now carries the centre as well as the range, because a reader told only the range
still takes the point estimate as the answer.

## What is new, and it is not the number — it is that the number can be read at all

The record beside this one refused the share, and refused it correctly: in the 09-03 measurement the
**level leg itself changed sign** (−£882 to +£9,085), and a leg undetermined in direction cannot be
expressed as a share of anything. The share spanned −60.1% to +2,014.5%.

**On the current book the level leg does not change sign.** £18,582 to £20,337, three draws, tight.
So the share is expressible for the first time:

> **`level_share_of_advantage`: mean 103.2%, range 93.9% – 117.8%** (sd 12.8pp)

A share at or above 1.0 means the level explains all of the advantage and the selection leg is worth
nothing or less. **The band sits astride 100% and does not reach down toward zero.**

So the answer to the question this lane has been asking since 08-27: **on this book the advantage is
the price level. Per-customer selection is not distinguishable from zero.**

## What that means for the mission, stated unflatteringly

The mission's first rule is that value is created and *then* shared, and that transfer is not
creation. A level advantage is a price charged — it **moves** value. The selection leg is the only
quantity on this page that could be value **created**, and it is inside its own noise.

**As measured, this company is currently moving value rather than creating it.** That is the
unflattering reading and it is the one the evidence supports.

Three things stop it being the whole story, and none of them softens it:

1. **It is a fact about THIS BOOK, not about the method.** The world's households differ only by
   circumstance, so there is very little for per-customer inference to select *on*. A
   level-dominated result is what the mechanism would predict independently of any seed.
2. **Roughly two in three priced decisions have their margin set by a bound, not by the household**
   (143 of 214 at the cap in the published run). Where the cap decides, there is nothing to infer.
   This is a diagnostic and **not a target** (R12) — the move it must not license is relaxing the
   cap guard so the population looks better.
3. **n = 3.** The bound this earns is stated, not glossed: sd £2,279 on three seeds.

## The standing preregistration, graded honestly

**P7 — HOLDS.** Predicted `selection_distinguishable_from_zero` stays **false** in the live world.
It is false. Same world digest, so this is the prediction's own subject and not a substitute.

**P6 — NOT GRADED, deliberately.** P6 predicted `selection_gbp_spread.stdev` of **5,923.04 ± 5%**
for the 09-03 `all` leg. This is the **09-08** `all` leg, and the book roughly tripled in priced
renewals between them (104 → 281). Grading this run against P6 would be exactly the leg-swap the
preregistration itself was written to stop. **P6 stays pending on its own artefact.**

Recorded because it will be asked: the floor **narrowed**, 5,923 → 2,279, against P6's direction.
More than one thing changed — book size, the gas repair, the fuel mix — so **I cannot attribute it**,
and a bigger book tightening its own floor is only the most obvious of several candidates. The
one-variable version has not been run.

## What reached the surface

`site/data/value_arms.json` regenerated: `bound_available` **true on all three legs**, each bounded
by its own contrast rather than a neighbour's. 115 generator controls green; 57 site controls green.

## A control that was keyed to the day's answer, and went red for being right

`test_the_creation_leg_carries_its_own_live_world_bound_and_not_the_advantages` asserted the
literals `-£8,634`, `£2,350`, `-£1,861` and `1 of the 3` — the **09-03 floor's own figures**. Moving
to a floor from the same world and the same commit as the arms it bounds, the strictly more honest
pairing this file exists to make safe, turned it red while nothing about the property changed.

**A control that reds when the page gets a better bound is backwards.** Re-keyed to the property:
the centre, both ends of the range and the resolving count must reach the headline, derived from
whichever floor is current. Plus one new leg — the family centre must not render identically to the
published draw, or the control would pass on a page that printed the point estimate three times.

Mutation-proven: centre dropped from the headline → **1 failed**; resolving count dropped →
**1 failed**; centre replaced by the published draw → **1 failed**.

## And a second control of the same class, one leg along — this one refused the landing

`site/test_the_baseline_comparison_reaches_the_reader.py::test_the_figure_from_the_world_that_is_live_reaches_the_reader_and_never_as_resolved`
refused the commit outright. Its own comment records being re-keyed on 2026-09-03 for going red
"the day the page became MORE honest". **It did it again, and the repair had missed by one leg.**

The rung's subject is the **whole advantage**; the string it asserts on is produced by the
**selection leg**. That never mattered while a single stale floor left both unreadable. It matters
now, because the two legs part company for the first time:

- the advantage's own re-draws span £17,262 – £20,002 and **resolve**;
- the selection leg's span −£3,075 – £1,200 and **reverse**.

So one headline legitimately states a verdict on one quantity and withholds on another — and the
rung read the *resolved* leg's flag against the *withheld* leg's sentence and called the page
fail-open.

Repaired to the property: `STATES NO VERDICT` must correspond to **some** leg that actually
withheld, and must carry **that leg's own** reversing range. A second defect fell out of writing it
— the existing edge check formats with `"£{:,.0f}"`, which renders `£-3,075` and would never match
the `-£3,075` the reader meets. The advantage's range is positive, so no one had noticed; the
creation leg's straddles zero, which is the whole finding.

Mutation-proven **against the feed, not the test** — the control must red when page and feed
disagree:

| feed mutation | result |
|---|---|
| leg's withheld flag cleared while the page still refuses | **1 failed** |
| the reversing range removed | **1 failed** |
| the range moved away from what the page renders | **1 failed** |

620 site controls green.

**Both re-keyed controls are the same shape and it is worth naming once:** a control keyed to
today's answer reds when the code becomes more honest and stays green when the claim rots. Two of
them fired in one turn, on one page, because a floor finally arrived that made the two legs
disagree.

## What is still owed

1. **A shared launcher.** Untouched. Five bespoke `/var/tmp` scripts now.
2. **Checkpointing.** This 2h31m run writes its artefact once, at the end.
3. **The one-variable question:** did the bound share rise because of the fuel mix, or for a reason
   independent of it? Not run.
4. **n = 3 is thin** for a quantity whose sd is 4.7× its own centre. More seeds would tighten it;
   whether that is worth 2.5 hours a seed is a judgement, not a defect.

## What this does not claim

That per-customer selection cannot create value. It claims that **on this book, in this world, with
these three seeds, it is not distinguishable from zero** — which is a complete result and not a
lesser one, and explicitly **not** a cue to re-run until a seed agrees (R12).
