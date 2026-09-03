**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

# Pre-registration: does the fitted year anchor re-express a mechanism the world already carries?

*Delivery seat, 2026-09-03, written BEFORE the measurement is run. Filed because the director's
instruction on `ace28fa44` was to repair the level fit rather than tune it, and the first thing a
repair needs is to know what the anchor is actually carrying.*

---

## Why this is asked at all

`DIRECTOR_CANON_WORLD_VALIDATION_LADDER_2026-08-31` settles the design question that
`SEAT_FINDING_THE_FIT_SOLVES_ONTO_THE_BANDS_CEILING...` escalated, and settles it against that
finding's own recommendation. **The canon's words: "The one move that is always wrong: clamping an
aggregate to pass a check."** and *"Rung failures repair downward, never sideways. A rung 1 failure
is fixed by correcting the individual model's attributes or rationale until the emergent level
moves — not by scaling the aggregate."*

`YEAR_LEVEL_ANCHOR` is a per-year scalar, running 2.03 to 7.37, bisected by
`tools/fit_year_level_anchor.fit_whole_book` until expected departures over accounts equals
`market_departure_rate(year)`. It multiplies three of the four renewal hazards in
`simulation/departure_risks.py`. It is the clamped aggregate, and moving its target from the band's
ceiling to the band's midpoint would leave it exactly as clamped — which is why that
recommendation was wrong and is corrected beside the claim rather than quietly dropped.

## The question a repair has to answer first

The renewal hazards ALREADY carry year-varying, mechanism-driven terms:
`market_switching_propensity.market_switching_multiplier(year)` and `market_opportunity`. Those are
rung 2 — a mechanism responding to conditions. So either

  * **(A) the anchor re-expresses them**, in which case the world is saying the same thing twice
    and the level can emerge once the double-count is removed; or
  * **(B) the anchor is orthogonal to them**, in which case it is carrying something real that no
    household-level driver in the world currently expresses — and identifying *what* is the repair,
    because that is a missing individual-level rationale, not a missing scalar.

These have different repairs and only one of them is cheap. Which it is, is a number nobody has
looked at.

## The prediction, made before running it

**I predict (B): the fitted anchor will NOT track the market terms.** Spearman |rho| < 0.5 between
`YEAR_LEVEL_ANCHOR[year]` and `market_switching_multiplier(year)` across the seven fitted years.

My reasoning, so it can be graded rather than admired: the anchor's spread is 3.6x
(2.033 in 2023 to 7.373 in 2017) and it is fitted on the RESIDUAL after the SVT route's
contribution is held fixed, over a renewal population whose size swings by an order of magnitude
year to year. A quantity that absorbs a changing denominator is mostly absorbing the denominator.

**And a distinct second prediction, on the sign, because the first can be right for the wrong
reason:** if there IS correlation, I predict it is POSITIVE — the anchor high in the same years the
multiplier is high. That is the direction that would mean the mechanism moves the right way and too
weakly, with the anchor amplifying it. The NEGATIVE direction — the anchor compensating downward
for a mechanism that already does the work — is the one I think less likely and it is the one that
would make the double-count immediate and the repair cheap.

## Constraints on the measurement, so it cannot be steered

1. Seven fitted years only (2017-2021, 2023, 2024). 2016, 2022 and 2025 are refused by
   `UNFITTED_YEARS` and pulling them in to move a correlation would be choosing the population
   after seeing the answer.
2. n=7. Spearman on seven points is weak evidence and its confidence interval will be reported
   beside it. **A rho that does not clear its own null is reported as "cannot tell", not as (B)
   confirmed** — the prediction above is the flattering reading of exactly that outcome and must
   not be allowed to collect it by default.
3. The anchors are read from `simulation/departure_level_anchor.YEAR_LEVEL_ANCHOR` as committed,
   not re-fitted for this measurement.
4. Nothing about the world changes in the commit that reports this. It is a reading.

## What must NOT happen

No value in `YEAR_LEVEL_ANCHOR` is edited, and no target is moved, on the strength of this
reading. This measurement chooses between two repairs; it is not itself one.

— Filed before the run. The grading goes beside it.
