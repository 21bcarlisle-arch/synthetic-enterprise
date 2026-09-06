**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# Pre-registration: an unbiased point estimate of R1's ceiling MAGNITUDE

*Delivery seat, 2026-09-06, claim `r1-ceiling-magnitude-is-a-selected-maximum-with-no-unbiased-estimate`.
Written BEFORE the three-way split was implemented or run. Nothing below is an observation.*

---

## What is already settled, and what is not

Two corrections have landed on `tools/r1_inference_ceiling.py` and neither touches the magnitude:

- `selection_corrected_null` grades **whether** the ceiling is real. On the current book it clears
  at p=0.0249, by +0.0598 over a p95 bound of +0.5529 — a marginal pass.
- `held_out_exceeds_in_sample_on_the_reported_winner` reports that the winning fit scores 3.66x
  better out of sample than in it, and says on the surface that this is the signature of a search.

The published figure **+0.6127 is the maximum of 45 candidates ranked on `abs(held_out)`**. A
maximum is biased up as an estimate of the thing it is the maximum of, and clearing a null does not
un-bias it. A49 gates R3 and R4 on this number. A gate keyed to a figure biased up will pass work
the true ceiling would not support.

## The measurement about to be made

A **three-way split**. Households are partitioned globally — the same household in the same fold for
every candidate, so selection on one fold cannot leak into another through a different candidate's
membership:

- **fold A — fit.** Cell means are built here and nowhere else.
- **fold B — select.** All candidates are scored on B; the winner is the one with the largest
  `abs(corr)` on B. This is the fold that absorbs the selection bias.
- **fold C — estimate.** The winner's `abs(corr)` on C is reported. C is untouched by both the fit
  and the selection, so it is an unbiased estimate **of the magnitude this selection procedure
  delivers**, which is the quantity A49 needs.

The existing two-way split (even index fits, odd index scores) cannot do this: it *selects* on the
same fold it *reports*, which is exactly the bias.

The second option on the table — shrinking +0.6127 toward the null median +0.3673 — is measured too,
but it is **not** unbiased and is pre-registered as such: it assumes the selection inflation under
the alternative equals the inflation under the null, which nothing here establishes.

## The predictions, fixed now

**P1 — the pair rung has no power for a three-way split and the estimator will REFUSE there.**
n=69 gives folds of ~23. The fit fold spread over 2x2 = 4 cells is ~5.75 households per cell,
under this file's own `MIN_HOUSEHOLDS_PER_CELL = 8`. I predict a named refusal, not a number.

**P2 — the full-coverage rung will ANSWER, and its estimate will be at the floor.** n≈149-213 on a
single axis is 2 cells; a fit fold of ~50-71 gives ~25-35 per cell, comfortably over the control.
I predict `abs(estimate) < 0.25` at that rung, because that rung already reads p=0.85 against its
own selection-corrected null.

**P3 — if the pair rung is forced past its own power control, the fold-C estimate comes in far
below +0.6127.** I predict `abs(estimate) < 0.40` — i.e. at or below the null median of +0.3673 —
because on the null's own showing a best-of-45 reaches +0.3673 on a world with no signal at all.

**P4 — the shrinkage figure is +0.2454** (0.6127 − 0.3673), arithmetic, stated so it cannot be
presented later as a discovery.

**P5 — the honest published outcome is "no unbiased point estimate on this book".** If P1 and P2
both hold, the rung that carries the published magnitude cannot support an unbiased estimate and the
rung that can support one reads the floor. That is the answer, and it is a refusal, not a number.

## What would refute me

A fold-C estimate at the pair rung of **+0.55 or above** would say the magnitude substantially
survives the selection correction, and P3 is wrong. A full-coverage fold-C estimate above **+0.25**
would say P2 is wrong and there is recoverable signal at full power that the two-way split missed.

Either refutation is a better outcome for the programme than the one I predict, and I would publish
it in the same place.

## What done means

Whichever way it comes out, `tools/r1_inference_ceiling.py` publishes a magnitude field that is
either an unbiased estimate with its fold sizes beside it, or a **named refusal** — never a
number standing in for one. The gate A49 reads must be able to see which of those it got.
