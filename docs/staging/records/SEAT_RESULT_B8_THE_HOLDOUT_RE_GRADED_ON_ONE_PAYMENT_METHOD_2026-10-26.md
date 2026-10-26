# The holdout re-graded on one payment method: nothing pooled moved, and the world has no per-channel offer effect to find

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `regrade-coin-drawn-holdout-after-one-payment-method`

*Delivery seat, 2026-10-26.* Pre-registration, filed before the runs:
`SEAT_PREREG_B8_THE_HOLDOUT_RE_GRADED_ON_ONE_PAYMENT_METHOD_2026-10-26.md`. Four of five held. The
fifth failed, and the failure is a finding.

## The run

`grade_decision` at a £7.5/MWh cut, real arm. It learned on seed 42 at 4,700 per year (92,862
decisions) and decided on fresh seed 101 at 850 per year (16,788 decisions), at both margin ends. It
was run once at `bad3cedd93` (old label) and once at `e35ce23f6` (one label). Only that commit
differs. The "true" columns are the world's own mean of `p_stay_treated - p_stay_holdout` within each
label, on the training set.

| | old label (`bad3cedd93`) | one label (`e35ce23f6`) |
|---|---|---|
| pooled estimate (95%) | +0.0118 (+0.0055, +0.0181) | identical |
| pooled true effect | +0.01147 | identical |
| learned cut share, £ per decision (all three rules, both margins) | 0%; 18.18 / 133.93 | identical |
| **true** effect, direct debit | +0.01147 (66,873 decisions) | +0.01144 (67,214) |
| **true** effect, other | +0.01148 (25,989) | +0.01157 (25,648) |
| estimated, direct debit | +0.0142 (+0.0068, +0.0216) | +0.0102 (+0.0028, +0.0176) |
| estimated, other | +0.0056 (−0.0063, +0.0175) | +0.0160 (+0.0040, +0.0280) |
| fresh decisions read on direct debit's own estimate | 12,301 of 16,788 | 12,096 of 16,788 |

## Against the predictions

1. **Pooled identical to the last digit. Held.** Only the label changed.
2. **Old label, both true per-label effects within 0.002 of pooled. Held.** The gap is 0.00001.
3. **One label, true |DD − other| under 0.005. Held, by a long way.** It is 0.00013. On this
   evidence, the world has no per-channel offer effect at all.
4. **Estimated intervals still overlap at both commits. Held.** The estimated gap went from DD ahead
   by 0.0086 to `other` ahead by 0.0058. That is a change of sign around a true gap of 0.0001, so it
   is noise both times. The item's own prediction, that the per-channel effects "separate more than
   before", is not shown. There was nothing for the old label to dilute.
5. **Every fresh decision reads pooled. FAILED.** Direct debit's arm (about 33,600) now passes the
   27,073 decisions per arm the pooled effect needs, so 72% of fresh decisions read direct debit's own
   estimate at both commits. I predicted from the 2026-10-08 arm sizes (about 25,000 per arm on a
   69,000-decision set). The set has since grown to 92,862 decisions, and I did not re-ask its size.
   The decision does not change at this cut: 0% are cut either way. But the read takes a channel
   estimate that is +0.0102 on one seed and +0.0142 on another for a true +0.0114. That is
   `SEAT_FINDING_THE_PER_CHANNEL_READ_IS_GATED_ON_POWER_NOT_ON_A_DIFFERENCE_2026-10-26.md`.

## What this establishes and what it does not

- **`e35ce23f6` is safe for the holdout.** No pooled number, verdict or £ figure moved.
- **The per-channel instrument now groups by the right label, and the world gives it nothing to
  find.** The world's renewal price response has no payment-channel input
  (`price_elasticity_for_customer`). The channel reaches P(stay) only through the bill-shock base, and
  that moves the cut's effect by about 0.0001. Whether real prepayment and standard-credit households
  respond to a retention cut differently from direct-debit ones is not established here. It is a
  question for the knowledge layer, not something to read off this world.
