**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose first named limit is that N has not converged

# The demand-vector N against a 240,000 reference (2026-10-14)

*Delivery seat, LANE 0 draw `demand-vector-n-240k-grade`. Graded against
`SEAT_PREREG_THE_DEMAND_VECTOR_N_PAST_120K_2026-10-14`, which was filed before any 240k seed ran.
The runs used units `longjob-dvn240-seeds-a` (seeds 0, 1, 2) and `-b` (seeds 3, 4), one seed at a
time, in `/var/tmp/se-dvn240` at `fa7ac5168`. `tools/demand_vector_coverage.py` there is identical
to `b585d3733` and to origin at grading. Every `.err` is empty and every run reported
`peak_window_share_is_constant: false`.*

## Result

| Seed | First passing size | Rung | Worst KS one rung below | Wall time | Peak RSS |
|---|---|---|---|---|---|
| 0 | 11,528 | 11,500 | 0.0601 at 8,829 | 45 min | 1,164 MB |
| 1 | 8,828 | 8,800 | 0.0600 at 6,831 | 32 min | 1,163 MB |
| 2 | 11,525 | 11,500 | 0.0609 at 8,828 | 40 min | 1,164 MB |
| 3 | 15,025 | 15,000 | 0.0592 at 11,527 | 53 min | 1,238 MB |
| 4 | 8,829 | 8,800 | 0.0636 at 6,834 | 34 min | 1,164 MB |

**240k range: 8,828 to 15,025** (rungs 8,800 ×2, 11,500 ×2, 15,000 ×1; median 11,500). At 120k it was 8,823 to 11,522 (rungs 8,800 ×2 and 11,500 ×3). At 20k
it was 5,215 to 6,815.

## Against the predictions

1. **Median rung 15,000: REFUTED.** The median rung is 11,500, the same as at 120k. The weaker
   claim, that every seed lands in {11,500, 15,000, 19,500}, is also **REFUTED**, because seed 1
   passed at 8,800. Both verdicts were fixed before seed 4 finished. With seeds 0 to 3 at 8,800,
   11,500, 11,500 and 15,000, the third of five values is 11,500 whatever the fifth is. Seed 4 then
   passed at 8,800.
2. **At least one seed passes at 11,500: HELD.** Seeds 0 and 2 did.
3. **No seed runs off the ladder: HELD.** The highest was 15,025, and the 19,500 and 25,000 rungs were never reached.

The power law through the two medians predicted about 14,200. The median did not move at all
between 120k and 240k. One seed reached a higher rung than anything at 120k (seed 3, 15,000) and
two reached the lower 120k rung (seeds 1 and 4, 8,800). As in the 120k cell, my prior leaned the wrong
way, this time high. I extrapolated a trend from two points that were each one rung wide.

## How it reads

The reading rule's **flattening** branch fires on both of its legs. The median rung is 11,500. And
at least two seeds fall inside the 120k range: four seeds land on rungs that the 120k cell also
reached (8,800 twice and 11,500 twice). The "still growing" branch needs a median above 11,500 and
fewer than two seeds on 11,500. Neither holds.

What this does and does not establish:

- **It is evidence the growth slows between 120k and 240k.** Between 20k and 120k the ranges did not
  overlap. Between 120k and 240k four of the five 240k draws land on the two
  rungs the 120k draws used.
- **It does not establish convergence.** That is one doubling, five draws, and one population per
  size. The 240k population is a fresh generation and not a superset of the 120k one, so a seed
  number at 240k is not paired with the same seed at 120k. Only the distributions over seeds are
  compared. Seed 3's 15,000 and the 240k spread being wider than the 120k spread (three rungs
  against two) are consistent with a slow residual rise and with plain draw noise. Five draws
  cannot tell those apart.
- **Non-monotone passing shows up again.** Seed 3 was closer to passing at 8,830 (0.0553) than at
  11,527 (0.0592). Seed 1 sat at 0.0600 at 6,831, a point above the line. Seed 4 was closer at 3,035 (0.0880) than at
4,036 (0.0975). At 240k, as at 120k, the
  rung is set by where one draw crosses 0.05.

## What changes on the page

`how-many-synthetic-households`: the first named limit stops saying "grows with the reference"
without qualification. It now gives the 240k range and says the growth slowed between 120k and
240k: the medians are equal and the ranges overlap. One doubling with five draws cannot establish
convergence. The headline range stays at 120k, because that is the reference the sample-to-reference
ratios and the history are stated against. The one-line summary's "still rising" now says that
the middle draw did not move at twice the reference, so the rise has slowed, and that one doubling
cannot show it has stopped. The live-evidence series gains the 240k range and its 3.7% to 6.3%
sample-to-reference ratio.

## Falsifiers

- `PYTHONPATH=. python3 /var/tmp/dvn240/run.py 240000 1` from a tree whose
  `tools/demand_vector_coverage.py` equals `b585d3733`'s. Expect `"n": 8828`. It takes about 30 to
  50 minutes alone at about 1.2 GB.
- Each of the other rows is the same call with its seed.
