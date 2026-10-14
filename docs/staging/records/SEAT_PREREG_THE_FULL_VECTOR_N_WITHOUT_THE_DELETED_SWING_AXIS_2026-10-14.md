**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** `how-many-synthetic-households` -- the page whose full-vector N this re-measures

# Pre-registration: the full-vector N without the deleted swing axis (2026-10-14)

*Delivery seat, LANE 0 draw `the-full-vector-n-is-re-measured-without-the-deleted-swing-axis`.
Filed BEFORE either run started, at base `ac3612a6f`.*

## What is measured

`smallest_n_chosen(generated_population(points=P, seed=0), AXES)` and the same over
`DISTRIBUTION_AXES`, at the default tolerance 0.05, for P = 20,000 and P = 120,000. This is the
`n_to_also_span_intervention_response` and `n_to_reproduce_the_distribution` of `measurement()`,
without the random-sample comparator (which the page does not lead with and which costs most of the
run). `AXES` no longer carries `seasonal_swing` (landed `ac3612a6f`).

## A property of the instrument that shapes the prediction

`smallest_n_chosen` walks `CHOSEN_NS` and returns the first rung that accepts, so the answer can
only be a rung: ... 4000, 5200, 6800, 8800, 11500 ... (the reported figure is the rung plus or minus
a few from per-stratum rounding in `choose_for_difference`). 6,816 and 8,822 are the 6800 and 8800
rungs; 5,215 is the 5200 rung. **So the instrument cannot resolve a change smaller than a rung gap
(~1,600-2,000 here)**, and a prediction must be a rung, not a number.

## Predictions

1. **20,000 full vector: the 5200 rung (5,215 or within ten of it).** The 09-09 bridge measured it
   at `7e699a126`; the commits since touched settlement choice and the household-count seam, not
   `generated_population` or the acceptance. If it is any other rung, something between 09-09 and
   now moved the instrument and the 20k figure must be re-attributed before the 120k one is read.
2. **120,000 full vector: the 6800 rung, ~60%; 5200, ~25%; 8800, ~15%.** Reasoning: at 20k removing
   the duplicate dropped one rung (6800 -> 5200), and with the duplicate the 120k figure sat one rung
   above the 20k one (6800 -> 8800). If both effects carry over, 120k lands one rung below 8800.
   Strictly below 8800 is the main claim; landing on 8800 would mean the duplicate cost nothing at
   the larger reference and the 09-09 30.7% was a 20k-only effect.
3. **Distribution axes, 20k: the 6800 rung** (09-09 measured 6,809 without the duplicate).
   120k distribution: no prior; recorded, not predicted.

## Falsifiers

- Prediction 2 is refuted by any rung other than 6800; the page carries whatever rung is measured.
- If 120k lands BELOW the 20k rung, the "grows with the reference" claim the page makes is no longer
  supported in its current form and the page must say so rather than keep the sentence.
