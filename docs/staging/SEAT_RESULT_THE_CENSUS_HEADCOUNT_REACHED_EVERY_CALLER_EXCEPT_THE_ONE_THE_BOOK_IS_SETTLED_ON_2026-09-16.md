**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0
delivery, director's Stage 1: *"the people layer"*

# The census headcount reached every caller except the one the book is settled on — 11.0% one-person households against GB's 30.1%

Delivery seat, 2026-09-16. Completes
`SEAT_FINDING_THE_WORLD_DREW_HEADCOUNT_FROM_BEDROOMS_AND_HAD_A_THIRD_OF_THE_ONE_PERSON_HOUSEHOLDS_GB_HAS_2026-09-08.md`,
which was archived as repaired and was repaired in one of four callers.

---

## What was measured

`behaviour_profile_for` has always **accepted** `people_count` and falls back to
`_PEOPLE_BY_BEDROOMS` when a caller omits it. On 2026-09-08 the headcount was anchored on ONS Census
2021 TS017 and wired into `household_physical_layer._profile_for`. It has four callers. **Three
omitted it**, and one of those three is `fabric_demand_path.build_fabric_series` — reached from
`build_fabric_series_for_site`, imported by `simulation/run_phase2b`, which is the path that settles
real money in the sim.

Measured over 2,000 residential premises off `draw_premise_population(2000, base_seed=20260916,
as_of=2024-04-01)`, same premises both ways:

| headcount | settled path (bedrooms) | census-anchored | ONS TS017 |
|---|---|---|---|
| 1 person | **11.0%** | 30.1% | 30.1% |
| 2 person | 37.5% | 34.0% | 34.0% |
| 3 person | 27.8% | 15.2% | 16.0% |
| 4 person | 17.3% | 13.1% | 12.9% |
| 5+ person | 6.5% | 7.5% | 7.0% |
| **mean** | **2.71** | **2.34** | 2.37 |

The 2026-09-08 finding measured 9.8% against 30.1% on a different draw and called it a three-fold
under-representation. **Eight days later the settled book still had it**, at 11.0%.

## Why this is the class, and it is not "a caller was missed"

The repair was correct, tested, and landed. What it did not do was ask **which readers of this
quantity exist**. `household_physical_layer._profile_for` carries a docstring saying it supplies
*"the census-anchored headcount it always accepted and never received"* — written in the voice of a
defect closed. It was closed for that caller.

This is the shape already written down three times in this repository this month: *a resolver was
not wired into the other readers of the file it was named for*. The tell is the same each time —
**the fixed caller and the unfixed caller cannot be told apart by any control**, because the
fallback is legitimate. `_PEOPLE_BY_BEDROOMS` is not broken; it is a reasonable default for a caller
that genuinely has no census draw. So the unfixed path runs green, produces plausible households,
and publishes a book whose largest GB household type is two thirds absent.

## Why it matters, in supplier terms and not in fit terms

One-person households are the **largest single band in GB** and this world settled a third of them.
They are a distinct demand vector, not a smaller version of a family: lowest annual volume, flattest
half-hourly shape, highest standing-charge share of the bill, and the population most exposed to the
fixed-cost leg of the cap. A book that thins them and fattens the 2–3 person middle understates
exactly the customers for whom the standing charge is the argument — which is the segment the
mission's *"saving them money"* has the least room to work in and the most need to be right about.

It also runs directly against the demand-vector canon of 2026-09-07: the sample must span
differences in response, and *"the value is in the uncommon combinations"*. This thinned the tail and
fattened the middle, which is the canon's named failure with the sign that flatters.

## The repair

One call, in `simulation/fabric_demand_path.build_fabric_series`:

```python
profile = behaviour_profile_for(
    customer_id, segments[0].household, seed=seed,
    people_count=people_count_for(customer_id),
)
```

`build_fabric_series` already passes `behaviour=profile` down to `generate_premise_trace`, so this
one argument fixes the whole settled path; `premise_trace`'s own fallback at the trace call is not
reached from here.

**A BASELINE FIDELITY CHANGE under R13, decided blind to P&L.** The world's homes now hold the
number of people the census says they hold. I did not look at what it does to margin before making
it and the direction it moves margin is not a reason for it. It will move demand volumes across the
whole fabric-driven book — mean headcount 2.71 → 2.34 — and that is a real change to the world the
company lives in, named here rather than arriving as silent drift.

## Controls

`tests/simulation/test_the_settled_book_draws_its_headcount_from_the_census_and_not_from_bedrooms.py`,
two legs, deliberately watching two different things:

1. **The wiring**, behaviourally — it spies the real `behaviour_profile_for` call the settled path
   makes and asserts a census headcount was supplied. Mutation-proven: removing the argument reds
   it with `assert 'people_count' in {'seed': 2016}`.
2. **The sources**, against the published anchor — the census draw must reproduce ONS TS017 within
   2pp, and the bedroom draw must still differ from it by more than 10pp. Without the second half,
   flattening the census marginal into the bedroom distribution would turn leg 1 green while
   deleting the whole repair. It is keyed to ONS, never to today's draw.

## What I did NOT do, and it is owed

**One of the two remaining callers is still unwired, by decision.**
`premise_trace.generate_premise_trace`'s own fallback (line ~1522) is unreached from the settled
path and is a legitimate default for a caller that genuinely has no census draw. Leaving it is a
decision, not an oversight: removing the fallback would make `behaviour_profile_for` refuse for
every caller that has no customer to key on, which is a different change and not this one.

`tools/explain_premise_year.py` is **not mine to land, and that is the finding about it.** It
explains a premise-year to a reader while drawing its own headcount, so it describes a household
the book never settled — occupancy, gains and appliance load all belonging to another home. A tool
that explains the book must not draw its own world.

I wrote the one-line fix into it, ran it green, and then **took it back out**: the file is
UNTRACKED. It exists on disk and in no ref, so it is another lane's work in progress, and landing
it would land their unfinished module inside mine under a REUSE block I cannot honestly write. The
correction belongs with whoever lands the file.

Recorded here rather than left as a note in a diff, because an untracked module is exactly the
thing that vanishes: `docs/staging/` holds several findings this month about work that reached no
ref at all. **Whoever lands `tools/explain_premise_year.py` owes it
`people_count=people_count_for(premise_id)` on its `behaviour_profile_for` call**, for the same
reason `build_fabric_series` now does.

I also did not measure what this does to the book. The change is justified on fidelity alone, and
measuring the P&L effect before landing it would have made the P&L part of the decision, which R13
forbids. The effect should be measured **after**, and reported whichever way it goes.

## Class registration

Belongs to `no_caller_and_never_runs`.

In the mirror shape this class needs stating explicitly: not a mechanism with no caller, but a
mechanism whose callers were never enumerated — three of four readers left on a legitimate fallback,
so the unwired path was green, plausible and wrong, and no control anywhere could tell the fixed
caller from the unfixed one.
