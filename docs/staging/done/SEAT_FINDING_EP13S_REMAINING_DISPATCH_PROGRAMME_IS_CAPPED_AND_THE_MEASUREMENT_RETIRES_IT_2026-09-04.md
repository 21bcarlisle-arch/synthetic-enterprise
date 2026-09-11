**Severity:** LATENT · **Lane:** W4_the_wall · **Epoch:** 3 · **Atom:** EP13_adapter_carbon_intensity

# EP13's remaining dispatch programme is capped, and the measurement retires it

**Found:** 2026-09-04, delivery seat, on the director's instruction to spend reclaimed time in the
lanes rather than the harness. Measured with `tools/ep13_input_ceiling.py`, which already existed
and had never been run to a recorded verdict.

---

## The question

EP13 has held at L2 through six build passes. Five moved a LEVEL error at the clean end; the axis
that actually holds the level is CORRELATION — 0.746 in 2024, in the module's own words *"the shape
knows how clean a quiet half hour is and not which half hours were quiet."*

Coal, the cables, the thermal floor, the measured must-run fleet and the biomass envelope have all
been built. Across all of it the correlation axis moved **0.726 → 0.746**.

The question the seventh pass has to answer before it starts: **can any dispatch model on these
inputs do better?**

## The measurement

`ep13_input_ceiling` hands the model's own inputs to the best possible function of them — the bound
on every dispatch model buildable on demand, wind, solar, the measured must-run fleet and the
cables, however good its merit order, efficiency curve, coal availability or outage model.

```
year   baseline   INPUT CEILING   gain
2019    0.8815       0.8757      -0.0057
2020    0.8732       0.8726      -0.0006
2021    0.9075       0.9087      +0.0013
2022    0.8699       0.8931      +0.0231
2023    0.7973       0.8071      +0.0098
2024    0.7425       0.7268      -0.0157

mean gain available to ANY dispatch model on these inputs: +0.0020
years where the ceiling is BELOW the shipped model:        3 of 6
```

**And every positive gain is smaller than the instrument's own noise floor.** The null rung refits
the ceiling against a SHUFFLED target; its absolute maximum runs +0.088 to +0.241 by year. The best
real gain, 2022's +0.0231, is under a quarter of that year's null maximum of +0.0998.

The resolution sweep says the same thing from the other side: mean held-out gain peaks at +0.0020
across 24 to 512 cells, while in-sample gain reaches +0.0120 — the difference between the two is
the overfit the held-out split exists to expose.

## The instrument's own controls, all green

- `null_collapses`: True in all six years — a shuffled target does not reproduce the result.
- `cells_are_populations`: True — the fit is not reading single half hours.
- `ceiling_reaches_the_published_feed`: **False** — the ceiling is structurally not publishable,
  so this cannot become a route by which NESO's own series leaks into the reconstruction.
- Split: fit on ODD days of the month, scored on EVEN days, whole days either side.

## What this retires

**The remaining dispatch programme for EP13.** A better merit order, a plant-level outage model,
a finer efficiency curve, more coal availability detail, more interconnector coverage — every one
of them is a function of these same inputs, and the best possible function of these inputs is not
measurably better than what is already shipped.

Six passes of "build the next term, measure, still L2" is the shape of a programme that should have
measured its own ceiling first. `tools/ep13_biomass_oracle_bound.py` did exactly that one term down
and retired an outage model; this is the same move one level up, and it retires the rest.

## What it does NOT say

It does not say EP13 is finished, and it does not say L3 is unreachable. It says the correlation
axis cannot be moved **from inside the dispatch model on its current inputs**. Anything that would
move it has to be a NEW INPUT — something outside demand, wind, solar, the must-run fleet and the
cables — and whether such an input exists, is published, and can cross the wall without becoming
NESO's own arithmetic is a separate question this measurement does not answer.

It also does not license reporting the atom as done. L3 means the thing FAILS LIKE REALITY, and at
0.746 in 2024 this instrument would still point a customer at the wrong half hours.

## What would close this

A recorded disposition on the atom: either a named new input with an argument for how it crosses
the wall, or an explicit decision that EP13's target level is not reachable by this route and the
atom is closed at L2 with the ceiling as the reason. Both are the director's call on sequencing;
the measurement is what makes it a decision rather than a sixth guess.

Not written as a **Discharged:** field, deliberately — that field is a claim the repair has landed.
