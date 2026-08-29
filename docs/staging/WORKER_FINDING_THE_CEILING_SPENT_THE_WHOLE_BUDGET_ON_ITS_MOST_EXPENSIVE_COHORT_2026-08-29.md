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
artefact. Booked 45 → **92**, all ten years, on **fewer** settled customer-years than before.

**One loose end, filed open rather than tidied.** Two runs of the same code at the same seed give
90/0.1789 and 92/0.1834. The campaign is identical on every leg — 505 funnel wins, 2,358.4
customer-years to settle them all, 587 accounts held — and the whole difference is in the OPENING
book: the same 82 accounts carrying 767.5 customer-years in the producer's run against 778.2 in
mine. `rate = (budget − opening book) / campaign cost`, so it propagates straight through. Nothing
in this change touches the opening book. **The sample rate is only as reproducible as the opening
book is.** The published figure is the producer's, because that is what a reader sees.

What I established before stopping, so the next reader does not re-run it:

- **In-process it IS deterministic.** Three separate processes: `n=82`, `cy=778.2`, and an identical
  SHA over the sorted acquisition dates. So this is not an RNG drift.
- **No environment I can set reproduces 767.5.** `SIM_FAST_MODE=1`, `SE_FAST=1`,
  `SE_GROW_BOOK=1 SE_DRAW_POPULATION=1`, and the bare environment all give 778.2.
- **It is not the horizon and not the seed.** A different horizon would move `campaign_cy` too and
  it is 2,358.4 on both sides; a different seed would move the funnel and it is 505 on both.
- **`founder_book` is not memoised**, but it reads `founder_accounts()` out of
  `docs/design/FOUNDER_BOOK.yaml` — which is uncommitted-modified in this tree by another lane —
  and `draw_population_enabled()`. A curriculum artefact being read at different moments by
  different processes is the shape that fits; **I have not proved it** and am not asserting it.

The derivation, so it can be checked rather than trusted: `rate = (1200 − opening) / 2358.4`, so
`0.1834 → opening = 767.5 ± 0.3` from 4-dp rounding, against a measured 778.2.

**Why it matters beyond this run:** the opening book is R13 CURRICULUM, director-authored. If two
processes on this box can build the published book from different versions of it, that is a
curriculum-integrity question and not a rounding one.

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
   ("grow residential toward 200" was passed in 2018); 174 reach the published book. Every binding
   reason is commercial in all ten years.
4. **Unchanged and stated as such:** R6 headroom £316,009 and the ladder's gradable population were
   not re-measured against this run and must not be quoted from the old ones — the book they were
   taken on has doubled and spread.
