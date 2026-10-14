**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose single-seed N this replaces with a spread

# Pre-registration: the demand-vector N over five design seeds (2026-10-14)

*Delivery seat, LANE 0 draw `the-demand-vector-n-is-published-as-an-interval-over-design-seeds`.
Filed BEFORE any run started, at base `8082bd246`, `tools/demand_vector_coverage.py` identical to
origin.*

## What is measured, and what is not

`smallest_n_chosen(generated_population(points=P, seed=0), axes, seed=s)` at tolerance 0.05, for
design seeds s = 0..4. The design seed reaches ONE thing: `KMeans(random_state=s)` inside
`choose_for_difference`, i.e. which medoids are chosen at each rung. Held fixed, and so NOT in the
spread: the population (seed 0), the 64 test directions (seed 12345), and the weight fit (seed 999).
The spread is therefore "how much N moves when only the choosing is redrawn", not a full
uncertainty on N.

Cells: P = 20,000 full vector (`AXES`) and distribution axes; P = 120,000 full vector. Seed 0 is
the published figure in each cell (5,215 / 6,809 / 11,520) and is re-run at 20k as a control.

**What "the interval" will mean.** Five seeds give the minimum, median and maximum first-passing
rung. That is a five-draw range, not a confidence interval, and the page will say so.

## Predictions

1. **Control:** 20k full vector, seed 0, reproduces **5,215**. If not, the instrument moved since
   `8082bd246` and nothing below is read.
2. **20k full vector, seeds 0..4:** at least two distinct rungs; all inside {4000, 5200, 6800};
   median the 5200 rung. (~65%)
3. **120k full vector, seeds 0..4:** at least two distinct rungs; median the **8800** rung, so the
   published 11,520 sits at the top of the spread. (~55%) The weaker claim I hold more strongly
   (~80%): at least one seed passes at 6800 or 8800, because seed 0 missed 6800 by under 0.00005.
4. **20k distribution axes, seeds 0..4:** at least two distinct rungs. (~65%)

## Falsifiers

- If every seed lands on the same rung in every cell, the rung is stable to the choosing, the
  non-monotone curve is a property of k rather than of the draw, and the page says N is
  seed-stable at the precision the ladder has. That would refute the premise of this item.
- If the 120k spread overlaps the 20k spread, the "grows with the reference" sentence is no longer
  supported and comes off the page.
