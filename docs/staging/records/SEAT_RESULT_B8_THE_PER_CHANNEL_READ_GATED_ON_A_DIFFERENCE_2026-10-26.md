# The per-channel read gated on a difference: direct debit now reads pooled on every fresh decision, and nothing priced moved

**Severity:** RECORDED · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `B8_discovered_price_sensitivity_holdout` · **Claim:** `b8-per-channel-read-gated-on-a-difference`

*Delivery seat, 2026-10-26.* Pre-registration, filed before the run:
`SEAT_PREREG_B8_THE_PER_CHANNEL_READ_GATED_ON_A_DIFFERENCE_2026-10-26.md`. All three predictions held.
Closes `SEAT_FINDING_THE_PER_CHANNEL_READ_IS_GATED_ON_POWER_NOT_ON_A_DIFFERENCE_2026-10-26.md`.

## The run

`python3 -m tools.grade_coin_drawn_holdout decide --arm real --cut 7.5` learned on seed 42 at 4,700
per year (92,862 decisions) and decided on fresh seed 101 at 850 per year (16,788). The set is the same
as the re-grade's. Only `effect_for_channel` changed.

| | power gate only (re-grade) | power and difference gate |
|---|---|---|
| fresh decisions read on direct debit's own estimate | 12,096 of 16,788 | **0** |
| fresh decisions read pooled | 4,692 | **16,788** |
| direct debit's gap to the rest (here, `other`) | not asked | −0.0058, bound ±0.0141 (from the published intervals) |
| learned cut share, both margins | 0% | 0% |
| £ per decision, learned / none, at 1.9% and 14% margin | 18.176 / 133.929 | identical |

## Against the predictions

1. **Direct debit reads pooled everywhere. Held.** The gap, −0.0058, sits well inside its bound. The
   world's true gap is +0.0001.
2. **Nothing priced moves. Held**, to the penny.
3. **The unit partition reaches all three reads. Held.** Short, powered but not different, and powered
   and different, on planted counts. Mutating the difference gate to always-pass or always-refuse
   reds the partition test each time.

## What else changed

`tools/grade_acquisition_selection.py` computed its own "read on its own estimate" set with the
power rule alone. That set feeds its predictions p1 and p2 and its `own_read` column. It now asks
`effect_for_channel`, so the grader and the decision cannot disagree about which read was taken. Its
published results predate this change, so their `own_read` columns were made under the power-only
rule. Re-run it before you cite them again.

## What this does not establish

The bound is a fixed-level test that is re-asked on every decision set. As the book grows, a channel
with no real gap will still pass about 5% of the time. A sequential correction would be the next
step if the read ever starts to move money. At this cut it moves none.
