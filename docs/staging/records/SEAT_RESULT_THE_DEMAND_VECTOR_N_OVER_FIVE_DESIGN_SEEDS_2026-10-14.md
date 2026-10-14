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
| 120k full vector | 11,520 (published) · 11,522 · 8,823 · 8,825 · 11,520 | 8800 ×2, 11520 ×3 | ≥2 rungs, median 8800 (~55%); ≥1 seed at 6800 or 8800 (~80%) | **median REFUTED** (11520). ≥2 rungs held; the weaker claim held (seeds 2, 3 at 8800) |

Control (prediction 1): 20k full vector at seed 0 gave **5,215** again. The instrument has not moved
since `8082bd246`.

The near-misses show that the rung is set by where one draw crosses the line. At 20k full vector,
seed 4 failed at 5,218 with a distance of 0.0502 and passed at 6,815 with 0.0499. Seed 1 passed at
5,219 with 0.0498. In the other direction, seed 3 missed at 5,221 with 0.0542.

**120k (seeds 1..4 finished 09:46 to 10:04, under /var/tmp/dvn).** Seed 4 repeats seed 0's shape. It missed at 6,825 by under 0.00005 (printed 0.0500) and then missed at 8,821 by 0.0119. So the 6800-rung near-miss is not a one-seed accident. It happens on the draws that end at 11,520. No seed passed at 6,800. Each 120k seed took 63 to 69 minutes with four running at once, at about 1.1 GB peak RSS each.

Both medians came out one rung higher than predicted. My priors leaned low in both cells because I anchored on the published seed-0 figure being the high end at 120k. At 20k it turned out to be the low end, and at 120k the median.

## What this changes on the page

The second falsifier (spreads overlap → the "grows with the reference" sentence is withdrawn) **did not fire**. 20k spans 5,215 to 6,815 and 120k spans 8,823 to 11,522, so there is no overlap and the sentence stays. It now carries both ranges.

`how-many-synthetic-households` now publishes N as a five-draw range, **8,823 to 11,522 against 120,000** and 5,215 to 6,815 against 20,000. It says that only the choosing was redrawn and that the range is not a confidence interval. The sample-to-reference ratios become 26 to 34% and 7.4 to 9.6%. The 243 → full-vector rise becomes 36 to 47 fold.

**The swing-axis deletion is now shown to be inside the noise, not just argued to be.** Before the deletion the figures were 8,822 at 120k and 6,816 at 20k. After it they were 11,520 and 5,215. All four sit inside the five-draw ranges for the vector without the axis. The page's second limit now says this from measurement, where before it argued it from the curve's non-monotonicity.

What stays open: the spread here covers the choosing only. The population seed, the test directions and the weight-fit seed are held fixed, so the full uncertainty on N is at least this wide. Convergence with the reference is still unsettled, because both ranges rise and nothing larger than 120k has been run.

## Falsifiers

- `PYTHONPATH=. python3 -c "from tools.demand_vector_coverage import *; p=generated_population(points=20000, seed=0); print(smallest_n_chosen(p, AXES, seed=2)[0])"`
  → 6812 at `d696e95a9`. Run it from the repo root. The fixed module paths make that matter less,
  but it is still the reference.
- Swap in the seed and the cell to reproduce any row above. The runner is the same call in a loop.
  Each 20k seed costs about 2 to 7 minutes on a loaded box. Each 120k seed costs 20 minutes alone
  and about an hour with four running at once.
