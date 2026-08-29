**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `A46_book_depth_is_a_curriculum_question`

# The ceiling spent the whole budget on its most expensive cohort, and three controls went quiet when it did

Direction of 2026-08-29 (lane 0): *"from 2018 the settlement engine books zero of every year's wins
… fix the settlement ceiling so the campaign's wins actually reach the book"*, and separately, the
ceiling's time argument is circular and needs a non-circular basis rather than a bigger number.

Design doc, with the predictions filed before the change and the results beside them:
`docs/design/SETTLEMENT_CEILING_ALLOCATION_2026-08-29.md`.

**The ceiling was not raised.** It had the wrong shape, not the wrong size.

## 1. The mechanism — this class, `controls_that_cannot_fail` for §3, allocation for this part

`_customer_years` charges a won account for its settlement tail to the horizon, so a win's price is
a function of *when* it was won: **9.83 customer-years for a 2016 win, 0.78 for a 2025 one.** The
budget was then spent **first-come**. 82 founders take 778.2 of the 1,200; the remaining 421.8 buys
45 accounts if you buy 2016's, and it buys the whole of 2025 four times over. It was exhausted
inside 2017 and booked **zero in each of the eight years after**.

The tell that this is allocation and not scale: **no budget avoids that shape.** Any B is exhausted
at some year and every later year books zero; B only moves where the cliff is. Eight of ten years
had exactly zero variance, so every downstream comparison keyed on year was dead — P9's book depth
(cohort and depth were the same variable), B10's ladder, and PB3 below.

**Fixed by making the ceiling decide the book's SCALE instead of which years exist.** One sampling
fraction, `f = headroom / (customer-years all funnel wins would cost)`, taken systematically over
the campaign's win sequence so each year's booked wins are proportional to its funnel wins. `f ≥ 1`
is a no-op and the run is byte-identical, which is the null result showing it is aimed at the
artefact. Booked 45 → **90**, all ten years, on **fewer** settled customer-years than before.

**A LOOSE END I FILED AS A CURRICULUM-INTEGRITY RISK, AND IT WAS ME.** Kept here rather than
deleted, because the wrong reading is the evidence that the right one was checked.

For about ninety minutes two runs of the same code at the same seed disagreed: my in-process
`_resolve_campaign` gave rate 0.1789 / 90 booked, the producer's record of 06:32Z gave 0.1834 / 92.
The campaign was identical on every leg — 505 funnel wins, 2,358.4 customer-years to settle them
all, 587 accounts held — so the entire difference sat in the OPENING book (778.2 customer-years
against a derived 767.5), propagating through `rate = (budget − opening) / campaign cost`. I
established that it is deterministic in-process (three processes: `n=82`, `cy=778.2`, identical SHA
over the sorted acquisition dates), that no environment I could set reproduced 767.5
(`SIM_FAST_MODE`, `SE_FAST`, `SE_GROW_BOOK`+`SE_DRAW_POPULATION`, bare), and that it was neither the
horizon nor the seed. I wrote it up as possible non-determinism in a director-authored curriculum
artefact — explicitly the worse of the two possibilities, and explicitly not proved.

**It was neither possibility.** The producer's next cycle reads **0.1789 / 90**, matching the
in-process runs exactly; 0.1834 has not recurred. The producer executes the WORKING TREE, and at
06:32 that tree was being edited — by this session and by at least one other lane concurrently.

**A figure read off the producer's artefact while the tree is under edit is not a measurement.**
That is the mirror finding of the same morning turned around: there, a probe adopted the producer's
book because both wrote the same path; here the producer adopted a half-written tree because I was
the one writing it. *Ask who else is touching the thing you are measuring* — and check "me, right
now" before reaching for a structural explanation. I reached for the structural one first, and it
would have cost the next reader a curriculum audit that had nothing to audit.

## 2. The same wall breach, second leg, left behind nine lines from the first

`accounts += 1` fired only on a SETTLED win. `accounts_held` sizes both the Ofgem capital headroom
and the 33% growth-rate cap, so from 2018 the supplier planned eight years against an account count
frozen by our wall clock. This is the breach fixed at `wins_to_date` on 2026-08-28 — *the same
ruling, the same paragraph* — and only one of its two legs was moved. **When a leak has two legs,
name both or the second one keeps running.** Predicted before the fix that booked wins would stay at
exactly 45; they did, and 2016–17 came back byte-identical.

## 3. Three controls that went QUIET, none of which went red

- **PB3's coupled-triad gap was published as an identity.** `couple_pb3_book_growth` excludes
  machine-bound years, which is right. Nine of ten years were excluded, leaving **{2016} alone** —
  and 2016 plans on the founding belief, so `abs_error == abs_error_no_skill` and `gap = 1.0` is
  arithmetic, not a result. The module's own docstring asserted *"the excluded partition is EMPTY"*.
  It was written when the ceiling was slack and went false when the founder book made it taut.
  **The partition was written as a control and became the population.**
- **The growth page's headline** keyed on `binding == settlement_engine`. Correct while the ceiling
  stopped a year dead; under sampling no year is stopped, so it would have published *"no year was
  bound by our settlement engine"* while four wins in five were refused.
- **The learned-rate caveat** keyed on a positional latch over those same years. It broke in **both
  directions inside four days** — still caveating a rate the 2026-08-28 fix had already cleaned
  (the page claimed a decay to 0.051 against a record flat at ~0.175), and about to flip to "none of
  them is an artefact" — without going red once.

All three re-keyed to properties: the gap refuses its normalised headline when no scored year
planned on a learned rate; the headline states the sample rate; the caveat asks whether the rate the
company planned on equals what its own funnel converted, which is checkable on every row and reds if
anyone re-wires the planner onto booked wins.

**PB3's gap is now a measurement: 0.830 over ten years, nine planning on a learned rate.** Learning
from its own quote book beat never updating. `_realised_rate` also had to move to `funnel_wins` — the
belief has been built from the funnel since 2026-08-28, so scoring it against booked wins compared a
belief formed on one population with a truth measured on another, and only n=1 hid it.

## 4. The ceiling's basis — neither leg sets 1,200, and the constant now says so

- **Memory** is non-circular (a slower run does not make the box bigger) and **slack by 4.5×**:
  4,193 MB peak against a 24,032 MB guest with 19,009 MB available.
- **Time** is the binding leg and **has no valid basis today**. The circular argument is struck from
  the constant. Replacing it needs a publish interval somebody *chose* and named; the non-circular
  anchor for that choice is external — how often the inputs this site reports actually change.

So **1,200 stands on no current evidence.** What makes that survivable is §1: the ceiling now sets a
sample rate rather than deciding which years exist, so getting it wrong costs the book's precision
rather than its coverage, and it can wait for a real answer instead of forcing an invented one.

## WHAT THIS CREATES

1. **A director decision, priced.** The publish interval. Memory would support roughly 4× the
   current ceiling; wall clock is what stops it and there is nothing legitimate to check wall clock
   against.
2. **The next engineering ceiling in the same chain.** Three of ten years are now MARKET-BOUND at
   `PROSPECTS_PER_YEAR = 400` — in 2024 the company could afford 861 quotes and only 400 prospects
   exist. Our number, not the GB switching market's.
3. **The director's target is met and the book is a sample of it.** The supplier holds 587 accounts
   ("grow residential toward 200" was passed in 2018); 172 reach the published book. Every binding
   reason is commercial in all ten years.
4. **Unchanged and stated as such:** R6 headroom £316,009 and the ladder's gradable population were
   not re-measured against this run and must not be quoted from the old ones — the book they were
   taken on has doubled and spread.
