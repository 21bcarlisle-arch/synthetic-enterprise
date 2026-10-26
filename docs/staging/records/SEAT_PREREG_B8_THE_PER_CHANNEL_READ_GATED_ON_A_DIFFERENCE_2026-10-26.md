# Pre-registration: the per-channel offer read gated on the channel differing from the rest

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-per-channel-read-gated-on-a-difference`

Filed 2026-10-26 before the code change is run against the real set. Answers
`SEAT_FINDING_THE_PER_CHANNEL_READ_IS_GATED_ON_POWER_NOT_ON_A_DIFFERENCE_2026-10-26.md`. The result
goes in a separate file; this one is not edited after the run.

## The change

`effect_for_channel` keeps the power gate and adds a second one. A channel's own estimate is read
only where its effect differs from the effect on the REST of the book (pooled counts minus the
channel's) by more than the two-sided `INTERVAL_COVERAGE` bound on that difference. The variance of
each arm's difference of shares is the Wald one, and the two variances add because the channel and
the rest share no rows. Otherwise the pooled estimate is read, and the reason names the gap and its
bound. A channel that is the whole book has no rest, so it reads pooled.

## The run: one variable

`tools/grade_coin_drawn_holdout.py decide --arm real --cut 7.5`, trained on seed 42 at 4,700 per
year and decided on fresh seed 101 at 850 per year. This is the same set as the 2026-10-26 re-grade.
Only `effect_for_channel` differs.

## Predictions (worked from the re-grade's published intervals, not from a run)

1. **Direct debit reads pooled on every fresh decision.** DD is +0.0102 (half-width about 0.0074)
   and `other` is +0.0160 (half-width about 0.0120). The rest of the book for DD is `other`, so the
   gap is -0.0058 against a bound of about 1.96 x 0.0071 = 0.014. Reads: `pooled` 16,788 of 16,788,
   against 12,096 channel reads before.
2. **Nothing priced moves.** Cut share stays 0% at both margin ends. The £ per decision for all
   three rules matches the re-grade to the penny (18.18 / 133.93), because the cut was declined on
   either estimate.
3. **The unit partition takes all three reads**: pooled because the channel is short, pooled because it
   is powered but not different, and the channel's own estimate when it is powered and different
   (planted counts).

If 1 fails, the difference bound is narrower than the published intervals imply, and I read why
before anything else.
