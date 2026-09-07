# PRE-REGISTRATION — whether the ToU sharing ceiling clears its null once the panel sizes are matched

**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** A49_the_ceiling_comes_before_the_programme_on_r3_and_r4

**Written:** 2026-09-07, by the delivery seat.
**Claim:** `a49-ceilings-the-sharing-side-of-r3`

## What was already printed before this was written, and why that is not a violation

CLAUDE.md carries two rules that pull in opposite directions here and both were followed in the
order the file gives them:

> *Print the numbers at real inputs before you ship a formula. … Do it before you write the test,
> not after.*

and

> *a pre-registration BEFORE any measurement whose answer you do not already know.*

The **level** of the created-value figure was printed first, deliberately, because the first draft
of a formula is where a units error lives and printing a table across the real range is the only
thing that catches it. Those prints are on the record: £13.33/MWh avoided per shifted kWh over 1,520
whole days of Elexon MID, 2016-09 to 2020-12, against a whole-panel skill-free null of £0.36/MWh.

What was **not** known when this was written, and is what this pre-registers, is below. It is a
different question from the level and its answer changes what the instrument is allowed to claim.

## The question

R3 reports its timing ceiling clearing its null by **4.82×**. The sharing instrument, run on the
whole MID panel, clears its null by **36.8×**.

Those two ratios are not comparable and I do not intend to publish them side by side as though they
were. R3's null is a mean over a 20-day panel; mine is a mean over 1,520 days. A mean over more days
has a smaller sampling spread, so the *maximum over 200 draws* of a skill-free optimiser falls as
the panel grows — **for reasons that have nothing to do with signal.** A reader comparing 36.8×
against 4.82× would be comparing two panel sizes.

So: **does the sharing ceiling still clear its null when the null is computed over a panel the same
size as R3's?**

## What I predict, before looking

1. **It clears.** The signal is a real diurnal price shape and 1,520 days of it agree on sign.
2. **The ratio falls a long way** — I expect it in the range **3× to 12×**, i.e. the same order as
   R3's 4.82× rather than an order above it. My reasoning: R3's null max is 21% of its hindsight
   figure at n=20; if the sampling spread of the price null behaves similarly, matching the panel
   should put the ratio within a factor of two or three of R3's.
3. **If the matched ratio lands above 15×, my model of where the 36.8× came from is wrong** and the
   difference is signal rather than panel size. That would be a more favourable result than I
   expect, and I am writing the bound down first so it cannot be claimed afterwards.

## What refutes this

A matched-panel ratio at or below 1.0 refutes the instrument outright: it would mean the price
shape's cleanest window is not reliably cleaner than a window picked at random, and a ToU tariff on
this book would have nothing to pass through. Because the created-value bound is a true CEILING —
the company holds both sides of the subtraction, the half-hourly traded price and its own EAC — a
reading at or below the null **retires the ToU product**, and I will publish that if it is what the
measurement says.

## What this pre-registration does NOT cover

- The **level** of the created value. Printed first, per the rule above, and on the record here.
- The **pass-through split**. There is nothing to predict: the frontier is an identity, not a
  measurement. Household share plus company share equals the created value at every pass-through by
  construction, and the instrument asserts it rather than discovering it.
- The **shiftable share** of domestic load. No source in the knowledge layer, the commons or the
  market research establishes one — the same named gap R3 carries — so the curve is published and no
  row of it is claimed.
