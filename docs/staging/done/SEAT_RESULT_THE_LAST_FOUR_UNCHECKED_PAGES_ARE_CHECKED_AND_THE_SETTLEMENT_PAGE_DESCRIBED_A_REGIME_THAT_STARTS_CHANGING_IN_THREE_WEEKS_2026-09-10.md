# SEAT RESULT — the last four unchecked pages are checked, and the settlement page described a regime that starts changing in three weeks

**Severity:** RECORDED · **Lane:** H_harness

**Date:** 2026-09-10 (delivery seat, lane 0 draw)
**Claim:** `seven-knowledge-pages-now-say-unchecked-and-nobody-has-checked-them`

---

## The premise was two-thirds spent, and I re-measured before starting

The item named seven pages. Three — `gb-electricity-market`, `merit-order-residual-demand`,
`carbon-price` — had already been checked earlier the same day by a sibling seat session. That
work is **uncommitted in the shared tree**, not at HEAD, and its result document is untracked, so
it is theirs to land. This turn did the remaining **four** and landed only its own hunks
(`tools.isolate_hunks`, keeping 7 of 10), leaving their three intact and unswept in the working
tree.

Tally moved by this commit: **unchecked 7 → 3, fresh 9 → 13.** The residual three are the
sibling's, and clear when they land.

## What the four checks found

The prior for this exercise was the 2026-08-19 pass over these topics' predecessors: two of six
materially wrong. This pass: **two corrected, one sharpened, one clean.** The prior held.

### `imbalance-cashout-settlement` — CORRECTED (the material one)

The page's economics are right and its **dating** was not, in the page whose subject *is* the
settlement timetable.

*"Reconciliation runs … out beyond a year"* and *"non-half-hourly customers are allocated by
profile class"* were stated in the present tense, as standing features of the market. Both are
facts about 2016–2025 that MHHS retires on a published schedule:

- Final Reconciliation 14 months → seven, for settlement days from **1 October 2026** — three
  weeks after this check
- seven → four months from 1 April 2027; Initial Settlement 15 → seven working days from 1 July 2027
- profile classes lapse as meters migrate; migration completes 7 May 2027, and a migrated meter
  carries no profile class at all

This is the **same class of error** the sibling's check corrected on `gb-electricity-market` the
same day, in a second page, independently. A present-tense description of a dated regime is
evidently this rewrite's characteristic failure, not a one-off.

Also sharpened: single-price cash-out is real and datable — BSC modification P305, approved
2 April 2015, implemented 5 November 2015 — and since winter 2018/19 the price comes from the
**single most expensive** balancing action (PAR1), not an average. That is stronger than the
page's "derived from the actions the operator took", and it is the actual mechanism behind the fat
tail the page's own `expected_shape` rung predicts.

### `hedging-forward-market` — CORRECTED, twice, and both make its argument stronger

**"Several GB suppliers failed in exactly this way in 2021."** It was **28** — about half of all GB
supplier failures since 2016, moving more than four million households. A page whose thesis is that
unhedged promises end companies described the event that proves it as "several". Corrected.

**"How much to hedge … depends on risk appetite, capital."** True until 2023. Ofgem's Strengthening
Financial Resilience decision (April 2023) and the enhanced Financial Responsibility Principle
(July 2023) impose a positive obligation to evidence sufficient capital and manage mutualisable
price risk — with failure to hedge named as a concern — plus a minimum capital requirement. There
is a regulatory floor now. The rung's actual claim (no optimum exists; a simulation producing one
would have fitted its own history) still stands and was left alone.

### `gas-wholesale` — SHARPENED

Every mechanism claim holds: NBP as a virtual point, gas-day rather than half-hourly balancing with
linepack absorbing the intraday mismatch, cash-out at system marginal buy/sell prices, ~50% CCGT
efficiency giving the ~2:1 gas-to-power slope.

The correction is an **omission that cut against the page's own conclusion**. It rested the whole
shape-of-the-market argument on gas being storable, without saying GB stores very little: ~1.7 bcm,
roughly seven days of average winter demand, among the thinnest in Europe and thinner since Rough
closed in 2017. Storage here smooths **days, not seasons** — which is precisely why GB competes for
LNG cargoes rather than drawing down a buffer, the thing the page asserted but never grounded.

### `electricity-wholesale` — CHECKED, no error established

Marginal pricing, residual demand as the selecting quantity, the four trading horizons and the
~2:1 slope all hold. Two sharpenings, both the same shape: *a true claim stated as though it were
timeless*.

- "For most half-hours a gas plant is the last one dispatched" — right, and undated. It is ~85% of
  hours in 2024, down from close to 90% in 2018. The direction of travel is the interesting part.
- `scope_delta`'s single-price-zone note read as a simplification awaiting a reform that might
  overturn it. REMA decided against zonal pricing on 10 July 2025. Settled, not pending.

**Deliberately not changed:** the page's `expected_shape` predicts the price distribution goes
bimodal as renewable share rises, and published 2025 evidence now supports it (hours with gas below
20% of the mix averaged ~£60/MWh against ~£130/MWh where gas exceeded 50%). Citing a page's own
confirmation inside that page is scoring yourself. Recorded in the review record instead.

## What else this turned up

`SEAT_FINDING_THREE_KNOWLEDGE_PAGES_CARRY_THEIR_REVIEW_CLASS_IN_TWO_HOMES_…` — the rate-of-change
class is written in both the index and each page's body, nothing compares them, and three of ten
disagree. One was settled by this check and fixed; two are filed unsettled rather than picked.

## What is not established

The four checks are of **assertions against published sources**. They say nothing about whether
each page's `live_evidence` rung describes what the simulation actually does — that is a different
question, against a different subject, and no date here covers it.
