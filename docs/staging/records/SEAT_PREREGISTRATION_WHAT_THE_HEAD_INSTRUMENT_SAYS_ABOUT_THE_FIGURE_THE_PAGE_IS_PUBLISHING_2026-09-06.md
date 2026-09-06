**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: what the HEAD instrument says about the figure the page is publishing

*Delivery seat, 2026-09-06, claim `the-r1-ceiling-is-a-selected-maximum-published-as-a-bound`.
Written BEFORE the run. Nothing below is an observation.*

---

## Why this measurement exists

The selection correction this claim was drawn for **landed** at `06fc90189`, and the household
keying correction landed at `3851553ec`. But `docs/observability/r1_inference_ceiling.json` was
last committed at `613f9bd17`, which is **before** the keying fix. So the artefact the site renders
from — and `site/data/delivery.json` with it — was produced by the **pre-keying instrument**, on a
book the instrument's own docstring now says was 213 supply points where there were 149 households,
with **38% of the target column drawn by hashing a gas-leg id that belongs to no household**.

The page therefore publishes `+0.6127`, `p=0.0249`, `clears` as R1's ceiling today, and those three
numbers were computed on a target column that is part real and part invented. That is the exact
shape this claim is named for, one rung further out than where it was found.

## Disclosure, because it changes what this prediction is worth

**I have already read another lane's uncommitted working copy in the shared tree**, which holds a
regenerated artefact reading `households: 164`, ceiling `+0.6308`, `p=0.0299`, `bound_p95 0.5776`,
and a leg census of `264 supply points → 177 households, 87 legs folded`. So P1 and P3 below are
**informed, not blind**, and I am not entitled to any credit for them.

What is genuinely unknown, and what this run is actually for: that lane's copy of
`tools/r1_inference_ceiling.py` is **+451/−278 lines** against the committed one — it adds a
three-way-partition honest point estimate and a per-field scope table. Their `+0.6308` is the output
of *their* instrument. **Nobody has run the instrument as it exists at HEAD against the current
book.** That is the number that tells us what the committed code publishes, and it is the only one
I am entitled to land.

## The predictions, fixed now

**P1 — the household count falls from 213 to somewhere in 149–177**, and the run refuses nothing:
`true_traits`' leg guard passes, because `observable_rows` now keys through `household_of`. If it
*refuses*, the two corrections are not composed at HEAD and that is a worse finding than this one.

**P2 — the ceiling moves by more than 0.02 from the published +0.6127.** This is the one I hold
most loosely and it is the point of the exercise: 38% of the target column changing from noise to
truth is a large perturbation, and the winner is selected on `abs(held_out)`, so it may move a long
way in either direction. **A ceiling that lands within 0.02 of +0.6127 would be evidence the leg
contamination did not much matter**, which would refute the finding's own account of why the
full-coverage rung read `cannot tell`.

**P3 — the verdict still `clears`, and still marginally: margin over the bound below +0.10.** I
expect the "flips on two households" property to survive re-keying, because re-keying changes the
book's size and not the fact that the rung is small and the bound is near the observed value.

**P4 — the full-coverage rung stops reading `cannot tell` at p≈0.85.** The finding claims that
p=0.8507 "was never a coverage result — it is what a rung reads when a share of its target column
belongs to no household." If re-keying leaves it near 0.85, **that claim is refuted** and the
published causal story is wrong a second time. This is the prediction most likely to embarrass the
record and it is the reason the run is worth doing.

## The grading rule, fixed in advance

- Every prediction is graded against the printed run, in a finding, beside the result, whichever way
  it falls. P2 and P4 are the two that can refute the existing published account, and if they do
  the refutation is what gets published.
- **I will not land a regenerated `site/data/delivery.json` or `docs/observability/*.json` that
  competes with the other lane's in-flight work.** Their instrument is further along than HEAD's and
  landing a third variant of the same figure is the defect this project calls two lanes fixing one
  defect concurrently. What this run produces is *evidence about what HEAD publishes*, filed as a
  finding.
- If the HEAD instrument and their instrument disagree materially on the same book, that is a
  finding about their in-flight change and it gets written down for them rather than acted on.

## What this measurement CANNOT settle

It cannot say whether the ceiling is real. It is one book, and the instrument's own power bound is
unchanged: at a rung of this size only a ceiling above roughly +0.55 is distinguishable from a
45-way search of noise at all. It also cannot attribute any move to re-keying alone — the run
output is a *later* book than the published one as well as a re-keyed reading of it, so both moved.
**Two things changed, so I cannot attribute**, and the finding must say so rather than crediting
the keying fix with whatever the number does.
