# The growth curve was bounded by our wall clock, and here is the measurement

**Director, 2026-08-24:** *"Your settlement-engine finding is exactly what I want surfaced: if
our own code binds growth rather than the simulated economics, say so on the site and fix it if
it's cheap. A growth curve that's an artefact of our engine is an inconsistency, not a result."*

It does bind, it is not cheap, and this is what was measured rather than assumed.

> **READ WITH TWO LATER DOCUMENTS, 2026-08-29.** `SETTLEMENT_CEILING_REMEASURED_2026-08-29.md`
> found this file's cost note 36% low and its time argument circular. `SETTLEMENT_CEILING_
> ALLOCATION_2026-08-29.md` found that the ceiling's *shape* rather than its size is what emptied
> 2018–2025, and changed it. **The specific claim below that no longer holds** is the framing that
> the engine "binds growth": it does not stop a year any more, it takes a uniform sample of the
> campaign, so the growth curve's shape is commercial and only its height is ours. The
> director's instruction quoted above is unchanged and is still what the surfacing serves.

## What was measured

| book | segments | settlement periods | wall clock | net margin |
|---|---|---|---|---|
| 33 accounts | resi + I&C + SME | 3,226,200 | 8.5 min | £1,352,579 |
| 49 accounts | residential only | 3,217,400 | 8.4 min | £16,972 |

Both are full 2016–2025 runs at base seed 20260724, completing green.

**The cost is linear in accounts × half-hours and there is no redundancy in it.** Two books of
very different composition and size produced almost the same period count and almost the same
elapsed time, because what the loop does is per-account-per-period work: build the demand shape,
apply the fabric physics, settle, bill. Extrapolating the measured rate, **200 residential
accounts is roughly 13 million settlement periods and roughly 34 minutes of wall clock per
run** — against a publish cycle that currently completes in about 25.

## The cheap fix that was tried and did not work

A profile of a short run pointed at one function: `fabric_physics.reconstruct_ambient_profile`,
reached through `_diurnal_shape` **8,254,848 times**, with `fabric_providers_for_book` taking
13.5s of a 24s run — the largest single cost in the build.

The hypothesis was sound. That function is pure in five scalars, runs an 80-step bisection, is
called once per **customer**-day, and depends only on the weather at a **site** and its
latitude. N households sharing a site should have been recomputing one identical day N times.

Measured, on the 49-account book over the full window:

```
CacheInfo(hits=1, misses=13783)
elapsed 8.4 min — identical to the uncached run
```

**One hit.** 13,783 distinct keys over 3,650 days is about 3.8 distinct (site, latitude) pairs
— the number of *fabric-eligible* customers — and that number did not move when the book went
from 13 accounts to 49, because the drawn households are not fabric-eligible. The redundancy
does not exist at any book size this project has, and the cost the cache was aimed at is not
the cost that scales.

The cache was **removed**. A 0.007% hit rate is not a small win; it is machinery every future
reader has to understand for nothing, and the first version of it silently broke two tests by
serving results computed under one monkeypatched state to a test running under another. The
negative result is kept as a comment where the cache would have gone, because the next person
to profile this run will land on the same function for the same good reason.

## What binds, stated plainly

Not the balance sheet. At £250,000 of founding capital the company can capitalise and acquire
far more than 200 domestic accounts — see `docs/design/curriculum/founding_capital.json`.

Not the funnel. It converts at 18.7% measured over 4,000 quotes, and at any plausible quote
volume it delivers more wins than the engine will settle.

**Our settlement loop, against the publish cadence.** That is a property of this machine and
this implementation, and it has nothing to do with the simulated economics.

## What the site says about it

The book size on the published site is capped by
`simulation/net_new_acquisition.py::SETTLEMENT_CUSTOMER_YEAR_BUDGET`, and every year the
campaign reports its own `binding` reason — `growth_rate`, `capital`, `market` or
`settlement_engine`. A year bound by `settlement_engine` is a year where **we** stopped the
book growing, and the run says so rather than letting a flattening curve read as a supplier
that ran out of money. Those are different facts and a reader cannot tell them apart from a
chart.

## The honest fix, not done here

Vectorising the settlement build — numpy over the half-hourly arrays instead of a Python loop
per account-day — is the change that would move this by an order of magnitude. It is a real
piece of work on the hottest path in the project, it needs its own before-and-after evidence on
every settled figure, and doing it inside a book-growth change would mean two large diffs in one
commit with no way to attribute a regression to either.

It is named here as owed. Until it lands, the published book stops where the engine stops and
says so.

## The unit was also wrong, and that is recorded rather than quietly corrected

`SETTLEMENT_CUSTOMER_YEAR_BUDGET` was derived from AO12's scale probe, which died at 8,145,405
**half-hourly settlement records** — 465 customer-years *of half-hourly metering*. Applying that
to a residential book charges profile-class households at the half-hourly rate, which
over-states their cost.

The measurements above supersede it: what actually constrains a run is wall clock, and wall
clock is what the budget is now set from. The customer-year unit is retained as the mechanism
because it is what the campaign can compute while planning — but its VALUE is now derived from
the measured minutes-per-period, not from the probe.
