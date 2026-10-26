# The per-channel offer read is gated on power, not on a difference, so it takes a noisier estimate where the channels do not differ

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout`

*Delivery seat, 2026-10-26. Found by prediction 5 of
`SEAT_PREREG_B8_THE_HOLDOUT_RE_GRADED_ON_ONE_PAYMENT_METHOD_2026-10-26.md` failing.*

## What was measured

`company/pricing/discovered_price_sensitivity.effect_for_channel` reads a channel's own estimate
whenever that channel's smaller arm reaches `decisions_needed_per_arm(pooled)`. On the current
92,862-decision training set (seed 42, 4,700 per year, £7.5/MWh), direct debit has about 33,600 per
arm against 27,073 needed. So 12,096 of 16,788 fresh decisions read direct debit's own estimate.

That estimate is +0.0102 (+0.0028, +0.0176). The world's true direct-debit effect is +0.01144, and its
true effect for `other` is +0.01157: the channels do not differ
(`SEAT_RESULT_B8_THE_HOLDOUT_RE_GRADED_ON_ONE_PAYMENT_METHOD_2026-10-26.md`). The pooled estimate,
+0.0118 (+0.0055, +0.0181), is closer to the truth and narrower. The read swaps it for a noisier
subset of the same data.

## Why it matters

Having enough decisions to estimate a channel says nothing about whether the channel differs. A
power gate passes as the book grows, whether or not any heterogeneity exists. The read then adds
variance and no signal. At £7.5/MWh no decision changes, because the cut is declined either way. Near
the break-even effect (about +0.048 at a 14% margin) a noisy channel read could flip decisions in
both directions.

## Proposal

A supplier can see whether its channels differ. Read a channel's own estimate only where the
difference between that channel and the rest is distinguishable from zero, as well as powered.
Otherwise read pooled, and name the reason ("direct_debit: powered but not different from pooled").
The control should be one partition that asserts all three reads can be taken: pooled (short),
pooled (powered, no difference), and channel (powered and different). Use a planted per-channel
effect, so the third branch is reachable. Then re-run `decide` and check that the 12,096 channel
reads fall to about the false-positive rate.

## Closed 2026-10-26

Actioned: the read now also asks the gap to the rest of the book. Result: `SEAT_RESULT_B8_THE_PER_CHANNEL_READ_GATED_ON_A_DIFFERENCE_2026-10-26.md` (12,096 channel reads fell to 0, nothing priced moved).
