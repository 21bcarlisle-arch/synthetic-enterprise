# Pre-registration: the coin-drawn holdout re-graded now that a household has one payment method

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `regrade-coin-drawn-holdout-after-one-payment-method`

Filed 2026-10-26 before any run below. The result goes in a separate finding; this file is not edited after the runs.

## The question

`e35ce23f6` made the roster's `payment_method` read `payment_channel_for_customer`. Before it, the
label was a second, independent 72% draw that agreed with the world's channel for 60% of households
(`SEAT_FINDING_THE_ROSTER_AND_THE_WORLD_DRAW_A_HOUSEHOLDS_PAYMENT_METHOD_ON_TWO_INDEPENDENT_STREAMS_2026-10-26.md`).
Does the per-channel offer effect in `tools/grade_coin_drawn_holdout.py decide` now differ, and does
anything else move?

## The run: one variable

`decide --arm real --cut 7.5`, learned on seed 42 at 4,700 per year, decided on fresh seed 101 at
850 per year, both margin ends. It is run twice on the same base: once at `bad3cedd93` (the parent of
`e35ce23f6`, the old label), and once at `e35ce23f6` (the new label). Only that commit differs. Alongside,
on the seed-42 training set, the world's own per-label effect is read as the mean of
`p_stay_treated - p_stay_holdout` within each label. That is the TRUE per-channel effect, so it can
tell a real gap from noise in the estimate.

## What I read before predicting (the reasoning, not a measurement)

- The world's renewal P(stay) never reads the roster label. `roll_lifecycle_event` reaches payment
  method only through `experienced_bill_shock_at_renewal`, which calls
  `payment_channel_for_customer` itself (`simulation/experienced_bill_shock.py`). The per-household
  price response (`price_elasticity_for_customer`) has no channel input.
- `e35ce23f6` still takes the old `rng.random()`, so every other value drawn on the stream is
  byte-identical.

## Predictions

1. **Pooled: identical to the last digit.** Pooled estimate, interval, true effect, cut shares and
   every £ per decision are the same at both commits. The pooled estimator does not group by label,
   and the world's numbers on each row do not read it. Any difference refutes "only the label changed".
2. **True per-label effect, old label: both labels within 0.002 of the pooled true effect.** An
   independent label splits the book at random.
3. **True per-channel effect, new label: a small gap, |DD − other| under 0.005.** The channel moves the
   world's base churn (prepayment carries no shock uplift) but not its price response. So a cut
   reaches the channels differently only through the base it acts on. I do not predict the sign.
4. **Estimated per-channel effects: the intervals still overlap at both commits.** The item asked me to
   predict that they "separate more than before". I predict the opposite of that being shown. The
   2026-10-08 gap (DD +0.0159 against `other` +0.0006) was on a random label, so it was noise. The
   real gap at prediction 3 is smaller than the noise on the `other` arm (half-width about 0.014).
   The estimated gap may get larger or smaller, and neither tells us anything.
5. **Decision reads: pooled on every fresh decision at both commits.** Neither channel reaches the
   pooled effect's per-arm count. DD's share is 72% on both labels, so its arm size barely moves.

If 1 fails, something besides the label changed, and nothing else in this re-grade can be read.
