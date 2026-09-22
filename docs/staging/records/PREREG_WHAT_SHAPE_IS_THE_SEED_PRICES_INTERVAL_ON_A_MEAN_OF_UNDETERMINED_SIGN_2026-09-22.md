**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** 3 · **Atom:** none — Lane 0 delivery

# PREREG — what shape is the seed price's interval, on a mean whose sign is undetermined?

**Filed:** 2026-09-22, BEFORE the arithmetic below was run. Drawn as Lane 0 delivery,
`the-arms-page-cannot-say-whether-the-advantage-is-choosing-or-the-price-level`. The item hands me
three of these numbers already (101, 19, 471), so those three are not what is being predicted —
**the SHAPE between the endpoints is**, and it is the whole reason the control the item asks for
has to be keyed to a property rather than to a bound.

## The subject

`seeds_to_state_a_sign(mean, stdev)` (`tools/run_value_cycle_ab.py:6243`) searches upward for the
smallest `m` with `|mean| > t(m-1) · sd / sqrt(m)`. On `next12` — the twelve-seed floor whose book
(154 settled accounts) is the published figure's own — the selection leg reads

    mean = -1069.4751089166675   stdev = 5398.31430804405   n = 12   sem = 1558.3591094597205

`sems_from_zero` is 0.686 against a bar of 2.201 at n=12, so the family does **not** clear its own
bar and `clears_its_own_bar` is False. That is exactly the state in which the current code
publishes a seed price, and `|mean|` is the denominator of the price.

## Predictions, written before running

- **P1.** `seeds_to_state_a_sign(-1069.475, 5398.314)` returns **101**. (The artefact's own
  `distance_to_a_sign` says 102 at a FIXED bar of 2.0; the self-consistent solve should come in at
  or just under it, and the item says 101.)
- **P2.** At the low end of one standard error of the denominator, `mean - sem = -2627.834`, the
  price is **small — under 25**, and the item's 19 is what I expect.
- **P3.** At the high end, `mean + sem = +488.884`, the price is **large — between 400 and 550**,
  and the item's 471 is what I expect.
- **P4 — THE ONE THAT IS NOT ARITHMETIC I HAVE BEEN HANDED.** The price is **NOT monotone across
  `[mean-sem, mean+sem]` and `[19, 471]` is NOT its range.** Because `mean - sem < 0 < mean + sem`,
  the interval of the denominator CONTAINS ZERO, and `(t·s/|m|)²` diverges as `|m| → 0`. So I
  predict the search returns **`None` (the family needs more than `_SEEDS_SEARCH_CEILING` = 10,000
  draws) for a band of `m` strictly inside the interval** — i.e. the honest statement of the price
  is not "19 to 471" but "**unbounded above**", and quoting 19..471 as a range would itself be the
  narrower, flattering read of an interval that has no upper end.
- **P5.** The width of that divergent band is wide enough to matter, not a knife edge: I predict
  the price exceeds 10,000 for **more than 1% of the denominators in the interval** — i.e. it is
  not a measure-zero singularity a reader could wave away.

## What would refute each

P1–P3 are refuted by any other integer. **P4 is refuted if the search returns a finite count at
every `m` sampled across the interval** — which would mean the divergence is unreachable in
practice and the "no upper bound" claim is a theoretical one rather than a live one, and the
control below should then be written differently. P5 is refuted by a band narrower than 1%.

## What this prereg is FOR

If P4 holds, then `seeds_needed_to_state_a_sign` is a point estimate of a quantity with **no upper
confidence bound**, published exactly and only in the state where its denominator's sign is
undetermined. That is not a bound that happens to be wide; it is a number that is not a bound at
all. The control the item asks for follows from the property, not from today's 101.
