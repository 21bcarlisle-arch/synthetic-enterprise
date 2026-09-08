# [SEAT-FINDING] The world drew headcount from bedrooms, and had a third of the one-person households GB has (2026-09-08)

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** W2_31_people_phase1_the_physical_layer_stands_alone

**Knowledge:** how-many-synthetic-households

---

## What was found

Occupancy had two sources in this tree and they disagreed.

`simulation/household_segments.py` holds `OCCUPANCY_POPULATION_SHARE`, anchored on ONS Census 2021
table TS017 — 1-person 30.1%, 2-person 34.0%, 3-4-person 28.9%, 5+-person 7.0%, mean 2.37.

`simulation/premise_trace.py::behaviour_profile_for` draws `people_count` from **bedrooms**, on its
own substream, via `_PEOPLE_BY_BEDROOMS`. Its docstring says the segmentation fields "attach
UNCHANGED where a caller has them" — and **no caller ever supplied one**. So the headcount that
reaches the demand path was a function of the bedroom draw, and the census marginal reached nothing.

Measured over 1,954 residential premises off the live draw (`draw_population(11,
acquisitions_per_year_lambda=400.0)`), same premises both ways:

| Headcount | Bedrooms-derived (live) | Census-anchored | ONS TS017 |
|---|---|---|---|
| 1 person | **9.8%** | 29.6% | 30.1% |
| 2 person | 37.1% | 34.8% | 34.0% |
| 3 person | 28.3% | 16.0% | 16.0% |
| 4 person | 18.1% | 12.6% | 12.9% |
| 5+ person | 6.7% | 7.0% | 7.0% |
| **Mean** | **2.76** | **2.38** | **2.37** |

**One-person households are the largest single band in GB at 30.1%, and the world had 9.8% of
them** — a three-fold under-representation, with the mass pushed into the 2-3 person middle.

## Why it matters, and it is not a rounding point

The director's canon of 2026-09-07 says the sample must span "differences in response", not match
averages, and that "the value is in the uncommon combinations". This is the opposite failure and it
flatters in the direction the canon predicts: it thinned the tail and fattened the middle. A
one-person household is a distinct demand vector — lowest annual volume, flattest half-hourly shape,
highest standing-charge share of bill, and the population most exposed to the fixed-cost leg of the
cap. The world had a third of them.

It also lands on a live figure. `behaviour_profile_for` sets `appliance_intensity =
(people_count / 2.4) ** 0.6` and `daytime_occupancy` off the same draw, and both feed
`premise_trace`'s non-heating electricity. A mean headcount 16.5% high propagates into every
electricity trace in the book.

## What was done

`simulation/household_physical_layer.py` (this atom) is the caller that was missing: it supplies the
census-anchored count to `behaviour_profile_for` through the parameter that was always there.
Nothing in `premise_trace` changed. Within-band headcount uses the published TS017 splits (3-person
16.0% / 4-person 12.9%; 5/6/7/8+ at 4.5/1.5/0.5/0.4%) renormalised within band, so no headcount
number is invented. The assembled draw reproduces TS017 to within 0.6pp on every band and 0.008 on
the mean.

`tests/simulation/test_household_physical_layer.py::test_the_headcount_reproduces_the_census_marginal_and_the_bedrooms_draw_does_not`
asserts both legs — the census match, and that the bedrooms-derived draw is *outside* the same
tolerance. The second leg is what stops the control being vacuous: without it the tolerance could
widen until it accepted the draw this replaced.

**It killed on the poison round only after being re-pointed.** The first draft called
`people_count_for` directly, so putting `physical_layer_for` back on the bedrooms draw left it green
— it graded the estimator and was blind to the wiring, which is the only thing the demand path sees.
It now reads the headcount off the assembled layer.

## What is NOT done, and is deliberately not done here

**The demand path is not re-pointed.** `fabric_demand_path` still calls `behaviour_profile_for`
without a headcount, so the book still runs on the bedrooms draw. Fixing that moves the electricity
trace of every household in the book, which is a curriculum-scale change and belongs in its own atom
with its own before/after — not smuggled in beside a layer cut. **Until that atom lands, this
finding describes a defect that is measured and still live.**

## What is next

1. An atom re-pointing `fabric_demand_path`/`premise_demand` at the census-anchored headcount, with
   the annual-electricity distribution printed before and after against NEED Table A14's per-adult
   medians (already anchored in `occupancy_consumption_volume_shape_w2_13.md`).
2. That NEED table is *adults-only*, and TS017 is *all occupants* — the same document names this gap.
   The re-point must say which population it is matching before it claims a match.

— Delivery seat, 2026-09-08.
