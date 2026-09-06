**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what the selection-corrected null does to R1's published ceiling

*Delivery seat, 2026-09-06, claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Written BEFORE the corrected null was implemented or run. Nothing below is an observation.*

---

## The measurement about to be made

`tools/r1_inference_ceiling.py` scores 45 feature pairs, ranks them by `abs(held_out)`, reports the
winner as **the input ceiling**, and grades it against a null drawn **for that pair alone**. The
reported figure is therefore a *selected maximum* compared against the distribution of a *single
comparison*, which is the multiple-comparisons defect in its textbook form.

The correction: shuffle the household → trait assignment across the whole book, re-run **the entire
ranked sweep** on the shuffled world, and take the winner's `abs(held_out)`. Repeat 200 times. That
gives the distribution of the quantity actually reported — the maximum of 45 — and the observed
ceiling is graded against *it*.

## The predictions, fixed now

**P1 — the corrected null is materially higher than the per-pair null the winner was graded on.**
Specifically the corrected 95th percentile lands at or above the highest per-pair null already in
the committed artefact (`null_floor_abs_max` = 0.5019, from
`docs/observability/r1_inference_ceiling.json`, run `run_output_1beec7215_20260904T163914Z.json`).

**P2 — the observed ceiling does NOT clear it: p > 0.05.** Stated as a number so it can refute me:
I expect between 15 and 120 of 200 shuffled worlds to produce a winner at or above the observed
ceiling.

**P3 — the published `ceiling_clears_the_null: true` flips to false, and the honest headline becomes
"we cannot tell".** Not "there is no signal": a refusal to distinguish, which is a different claim
and the one the evidence supports.

**P4 — the full-coverage single-feature rung's verdict does not change.** It is already `false`, and
a selection correction can only make a verdict more conservative, so correcting that rung too must
leave it `false`. If it changes at all, my implementation is wrong rather than my prediction.

The reasoning behind P1–P3, so the prediction is falsifiable rather than a hedge: the per-pair nulls
already in the artefact run from 0.24 to 0.50 across the top eight pairs, on 12 draws each. A
maximum over 45 pairs must sit at the top of that range or above it, and the observed winner is
0.5661 — inside it. The corroborating tell is already recorded in
`SEAT_FINDING_R1S_INFERENCE_CEILING_IS_AT_THE_NULL_AND_R2_CANNOT_PAY_UNTIL_R1_LANDS_2026-09-04`:
held-out +0.5661 against in-sample +0.1724 is a fit scoring three times better on data it never saw,
which no real fit does.

## What this measurement CANNOT detect, stated before it runs

With 200 draws the smallest p-value expressible is 1/201 ≈ 0.005, so the instrument can never
report better than that however real the signal. More binding: it can only call a ceiling real if
that ceiling exceeds the 95th percentile of the selected-max distribution. On the existing per-pair
nulls that threshold is somewhere near 0.45–0.55 at n=71. **So on this book, at this sample size,
the corrected instrument can only ever confirm a very large effect, and a genuine ceiling of, say,
0.30 would be indistinguishable from chance.** That is a statement about the book's power, not
about the world, and it must be published beside whatever verdict comes out — otherwise "we cannot
tell" will be read as "there is nothing there".

## The grading rule, fixed in advance

- P2 is graded on the p-value the run prints. Anything outside 15–120 exceedances refutes the range
  even where the verdict direction is right, and the refutation gets written next to the result.
- A verdict of "clears" would refute P2 and P3 together, and would be published as the ceiling
  standing up to the correction — the flattering answer is not the one being fished for here.
- The uncorrected figure stays in the output beside the corrected one permanently. The point is not
  to delete the wrong number; it is to make the two readable together.
