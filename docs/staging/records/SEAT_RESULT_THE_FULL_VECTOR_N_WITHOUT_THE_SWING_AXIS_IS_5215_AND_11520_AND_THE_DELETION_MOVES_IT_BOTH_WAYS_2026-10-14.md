**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page corrected by this result

# The full-vector N without the swing axis is 5,215 and 11,520, and the deletion moves it both ways (2026-10-14)

*Delivery seat, LANE 0 draw `the-full-vector-n-is-re-measured-without-the-deleted-swing-axis`.
Pre-registration: `SEAT_PREREG_THE_FULL_VECTOR_N_WITHOUT_THE_DELETED_SWING_AXIS_2026-10-14`, landed
on origin as `4724431af` before the 120k run answered.*

## Result against the predictions

| Quantity (tolerance 0.05, seed 0) | Predicted | Measured | |
|---|---|---|---|
| 20k full vector | 5200 rung (5,215) | **5,215** | held |
| 20k distribution axes | 6800 rung | **6,809** | held |
| 120k full vector | 6800 rung (~60%), strictly below 8800 | **11,520** | **REFUTED, wrong direction** |
| 120k distribution axes | not predicted | 8,822 | recorded |

**One-variable bridge at 120k.** The same script at `c91e5aeac` (`ac3612a6f^`, the duplicate axis
still in `AXES`, everything else identical) gives **8,822**, which is exactly the published figure.
So the deletion alone moves the 120k full-vector N from 8,822 to 11,520 (+30.6%). At 20k the 09-09
bridge moved it from 6,816 to 5,215 (−23.5%). **The same one-line change moves N in opposite
directions at the two references.**

## Why I do not read either move as an effect

The acceptance curves (worst weighted KS distance by rung, full vector, 120k, axis removed):

    6,826  0.0500  fails   (by less than 0.00005)
    8,823  0.0553  fails
    11,520 0.0395  passes

At 20k, distribution axes: 4,019 at 0.0579, 5,214 at **0.0677**, 6,809 at 0.0437. **Worst distance
is not monotone in sample size.** `choose_for_difference` picks a different set at each k, so each
rung is effectively a fresh draw, and N is "the first rung where one draw lands under 0.05". With
the 120k 6,800 rung missing by a rounding error, the reported N can move a whole rung (about 30%)
on noise. A change of one rung is therefore not evidence, and a sign that flips with the reference
looks like a threshold wandering, not like the axis doing anything. That answers item 4 of the 09-09
document ("why N is not monotonic in the axis count") at least partly. N is not monotonic in the
axis count because **it is not monotonic in k either**.

What the 09-09 document called "inflated by 30.7%" was a one-rung move at one reference. The
direction of its claim (the duplicate inflated the headline) does not hold at 120k. The reason to
delete the axis stands: it was invented, and it was a duplicate. What does not stand is any claim
that deleting it made the figure smaller.

## What landed

`site/data/knowledge_topics.json`, `how-many-synthetic-households`: the headline, one-line, theory,
live-evidence and residuals now publish **5,215 / 11,520**. The residuals carry a new limit: the
figure is known only to about one rung, with the curve above as the reason. The "seven axes" limit
now says six declared axes and five directions, with the removal dated. On both this page and
`who-lives-where`, the occupancy "6,813 to 6,816" is now called rounding inside one rung. Before,
it was called a three-household effect.

## What is next

1. **N needs an interval, not a rung.** The cheapest instrument change that can fail is to run
   `smallest_n_chosen` over several `choose_for_difference` seeds and publish the spread of first-passing
   rungs. Without that, every future "the figure moved" on this page is unattributable. 120k costs
   ~20 min per seed per axis set.
2. The convergence claim ("grows with the reference") still holds on these two points
   (5,215 → 11,520). The convergence is now steeper than the page said before (×2.2, where it said ×1.3).
   That is one more reason for item 1 before anyone reads the slope.

## Falsifiers

- `PYTHONPATH=. python3 -c "from tools.demand_vector_coverage import *; p=generated_population(points=120000, seed=0); print(smallest_n_chosen(p, AXES)[0])"` → 11520 at `ac3612a6f`.
- The same at `c91e5aeac` → 8822. If it does not, the bridge is not one-variable and the +30.6% is unattributed.
