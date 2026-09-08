**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `unminted`

**Knowledge:** `how-many-synthetic-households` -- landed at `3745b9c0d` and carrying this finding.
The declaration said "blocked on the site lane" when this was written; the page has since landed and
its `theory` and `expected_shape` rungs publish the driver-versus-axis distinction measured here.

# Adding a driver is not adding an axis: hot water and occupancy moved the sample size by three households

**Measured 2026-09-08**, delivery seat, at `00f2a1771`. One variable, same population size, same
seed, same ladder. Reproduce: the script is recorded in the commit body; it monkeypatches
`hot_water_base.kwh_over_months` to zero and runs `smallest_n_chosen` on both arms.

---

## The prediction, and it was wrong

I filed this in the gas discovery brief, before building:

> *"N should rise, and for the first time for a reason that is not a stratum. Set-point and schedule
> are the first household properties that are independent of fabric and weather... My estimate is a
> 2-4x rise from breaking the r ~ 0.99 degeneracy."*

The same reasoning covered hot water and occupancy: a term driven by headcount is independent of
fabric and weather, so it should break the degeneracy and raise the requirement.

## What happened

| vector | population | N at tolerance 0.05 |
|---|---:|---:|
| hot water and occupancy OFF | 20,000 | **6,813** |
| hot water and occupancy ON | 20,000 | **6,816** |

**Three households in six thousand eight hundred. 0.04%.** The mechanism I predicted did not fire,
and it is not a matter of the effect being small -- it is that the reasoning was about the wrong
thing.

## Why, and this is the part worth keeping

**The demand vector measures seven OUTPUT quantities. Occupancy is not one of them.**

    annual_gas_kwh   annual_electricity_kwh   seasonal_swing
    weather_sensitivity_kwh_per_degree_day    peak_window_share
    insulation_ceiling_kwh                    turndown_ceiling_kwh

Wiring hot water gave occupancy a route into two of those -- it moves the gas level, and it selects
the electricity shape. But it added **no new direction the sample has to span**. A household's
headcount perturbs where it sits along axes that already existed; it does not create an axis on
which two households can be far apart in a way nothing else captures.

**A stratum multiplies N because coverage is owed WITHIN it on every axis.** An axis raises N
because the sample must span a new dimension. **A driver does neither.** It moves points around
inside a space whose shape is already being reproduced -- and a distributional acceptance test only
ever sees the shape.

That distinction did not exist in my prediction, which is why the prediction could not have been
right. "Independent of fabric and weather" was true of occupancy and irrelevant, because the test
does not score fabric and weather; it scores the seven outputs.

## What this does NOT say

**It does not say the hot-water term was not worth building.** It moved the modelled gas total from
0.883x to 0.992x the observed metered gas for the same households, which is the model getting closer
to reality by a fifth of the gap. Fidelity and sample size are different questions and this is the
clearest example so far that they can move independently: **a change can make the world markedly
more truthful and leave the sample size untouched.**

It also does not say occupancy is unimportant to the mission. A customer asking what turning their
thermostat down does needs a model where their own household is represented; that is a question
about the model's response, not about how many households the book needs.

## What WOULD raise it, on the same reasoning

Something the vector does not already measure. On today's evidence the candidates are:

- **A genuine seasonal-shape axis.** `seasonal_swing` is currently an affine transform of
  `weather_sensitivity` and carries no information at all -- see
  `SEAT_FINDING_TWO_AXES_OF_THE_DEMAND_VECTOR_ARE_THE_SAME_AXIS_2026-09-08`. A real one, computed
  over a full year rather than the 1 Oct - 31 Mar window, WOULD be a new direction, and it is
  precisely where the hot-water term would show up: a five-person household's gas is flatter across
  the year than a single person's in the same dwelling, because more of it is hot water. **The
  driver has nowhere to appear until that axis is real.**
- **Further strata.** Read pattern and arrears remain unmeasured and remain strata.

## The correction to the published mechanism

The knowledge page currently says three uncounted axes are strata and "should therefore multiply"
the count. That stands. What must be added beside it is the negative half, which the page does not
have: **not everything added to the world is added to the vector, and only what is in the vector can
move N.** Four of the seven "uncounted axes" listed there are drivers or correlated quantities, not
strata, and on this evidence they will move the figure by approximately nothing.


---

## AMENDED, same day — repeated where the measurement is NOT resolution-limited

The result above was measured at a 20,000-household reference, and **6,816 of 20,000 is 34% of the
reference population**, which is not a compression at all. An earlier finding in this module already
named that ratio as the resolution limit. The comparison was CONTROLLED — both arms on one
population — so the *difference* was attributable, but a null result measured at a resolution
limit is exactly where a real effect can hide. So it was repeated at the reference the published
figures use.

| reference | sample as a share of it | hot water OFF | hot water ON |
|---:|---:|---:|---:|
| 20,000 | 34% | 6,813 | 6,816 |
| **120,000** | **7.4%** | **8,820** | **8,822** |

**Two households in 8,822.** The null holds, and it holds where the sample is a genuine compression
of the population rather than a third of it. The mechanism stands: a driver moves households inside
a shape the acceptance test already reproduces, and only what the sample is scored on can move the
count.

**And the level is now on a defensible footing for the first time.** Every figure this instrument
published before today was scored at a reference where the sample was a large fraction of the
population. 8,822 against 120,000 is the first that is not, which matters more for how the number
should be read than the hot-water term does.
