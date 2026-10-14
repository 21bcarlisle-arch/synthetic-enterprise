**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose single-seed N this replaces with a spread

# The demand-vector N over five design seeds (2026-10-14)

*Delivery seat, LANE 0 draw `the-demand-vector-n-is-published-as-an-interval-over-design-seeds`.
Pre-registration: `SEAT_PREREG_THE_DEMAND_VECTOR_N_OVER_FIVE_DESIGN_SEEDS_2026-10-14`, landed on
origin as `4e95d2bff` before any seed ran. Measured at base `d696e95a9`, after `58e1e8905` (the
PC1/PC3 shape files resolve from the module, so the run's directory can no longer change N). Every
run reported `peak_window_share_is_constant: false`.*

## What varies, and what does not

Only the design seed varies. It is `KMeans(random_state=s)` inside `choose_for_difference`, so it
decides which medoids are chosen at each rung. The population (seed 0), the 64 acceptance directions
and the weight fit are held fixed. These spreads say how far N moves when only the choosing is
redrawn. They are a five-draw range, not a confidence interval.

## Result against the predictions

| Cell (tolerance 0.05) | Seeds 0..4, first passing size | Rungs | Predicted | |
|---|---|---|---|---|
| 20k full vector | 5,215 · 5,219 · 6,812 · 6,813 · 6,815 | 5200 ×2, 6800 ×3 | ≥2 rungs, all in {4000,5200,6800}, median 5200 | **median REFUTED** (6800). Rest held |
| 20k distribution axes | 6,809 · 6,811 · 5,211 · 6,811 · 6,810 | 5200 ×1, 6800 ×4 | ≥2 rungs | held |
| 120k full vector | 11,520 (published) · seeds 1..4 IN FLIGHT | pending | ≥2 rungs, median 8800 (~55%); ≥1 seed at 6800 or 8800 (~80%) | pending |

Control (prediction 1): 20k full vector at seed 0 gave **5,215** again. The instrument has not moved
since `8082bd246`.

The near-misses show that the rung is set by where one draw crosses the line. At 20k full vector,
seed 4 failed at 5,218 with a distance of 0.0502 and passed at 6,815 with 0.0499. Seed 1 passed at
5,219 with 0.0498. In the other direction, seed 3 missed at 5,221 with 0.0542.

**120k is in flight at the time of this increment.** Seeds 1..4 were launched at 08:38 and 08:55 under /var/tmp/dvn. A later commit in this same draw fills in the row and the page. Until it does, nothing on the page has changed.

## What this changes on the page

Nothing yet. The 20k half already refutes one sentence on the page. 5,215 is not "the" 20k figure. It is the low end of a range whose median is the 6,800 rung. The page changes once the 120k spread is in, so that the slope sentence ("grows with the reference") is judged on both spreads at once, as the pre-registration's second falsifier requires.

## Falsifiers

- `PYTHONPATH=. python3 -c "from tools.demand_vector_coverage import *; p=generated_population(points=20000, seed=0); print(smallest_n_chosen(p, AXES, seed=2)[0])"`
  → 6812 at `d696e95a9`. Run it from the repo root. The fixed module paths make that matter less,
  but it is still the reference.
- Swap in the seed and the cell to reproduce any row above. The runner is the same call in a loop.
  Each 20k seed costs about 2 to 7 minutes on a loaded box. Each 120k seed costs 20 minutes alone
  and about an hour with four running at once.
