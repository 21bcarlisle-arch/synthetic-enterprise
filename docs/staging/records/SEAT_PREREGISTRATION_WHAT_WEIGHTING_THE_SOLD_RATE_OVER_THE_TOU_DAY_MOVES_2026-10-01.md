**Lane:** B_commercial · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery, claim `weight-the-sold-rate-over-the-tou-day`

# Pre-registration: what weighting the sold rate over the ToU day moves

Written before the run. The parent is
`docs/staging/SEAT_FINDING_THE_SVT_SEGMENT_NOW_BILLS_EX_VAT_AND_NO_FIRST_TERM_SITS_ABOVE_THE_EX_VAT_CAP_2026-10-01.md`, handed-on item 1.

## The change

`settlement_daily.fold_to_days` now writes `unit_rate_weighted_gbp_per_mwh` on each daily row:
Σ(rate × kWh) / Σ kWh over the day's rated periods. `experienced_bill_shock.sold_unit_rate`
reads it first and falls back to `unit_rate_gbp_per_mwh` only on a row the fold did not make.
Nothing in the run reads either field while the run is going (`experienced_bill_shock_at_renewal`
is recorded, not yet what the hazard reads), so the run is the same with or without the change.
For that reason ONE run reads both: `old` strips the new field and `new` keeps it. This is the
only variable. Script: `/var/tmp/se-touweight-run/measure.py`, on origin/main `649112975`.

## What the 30/70 split says

The supplier's ToU pair is peak 1.5× flat. Off-peak is set so that a 30% peak share is neutral,
which gives 11/14. So a household's weighted rate over flat is 0.7857 + 0.7143·s, where s is its
peak share of kWh. The world's peak band is weekdays 07:00–11:00 and 16:00–20:00, which is 16 of
48 periods and covers both of the domestic load peaks. I predict s ≈ 0.31 (0.25–0.36) in the
first month.

## Predictions

- **P1.** Every account with no intra-day rate spread (flat and gas): new == old to 1e-9. 0 moved.
- **P2.** Every ToU account: old/flat = 0.7857 (flat taken as max ÷ 1.5).
- **P3.** Every ToU account: new/flat in [0.96, 1.04]. Median in [0.98, 1.02].
- **P4.** The 8 ToU SVT accounts: sold ÷ inc-VAT cap goes from 0.7483 to [0.91, 0.99].
  Because the median s is predicted just above 0.30, I predict that 2–6 of the 8 now read above
  the ex-VAT cap ×1.001. That is a real property of a ToU split under a flat cap, not a defect of
  this change. It is reported, not fixed.
- **P5.** DD opening ratio (opening at sold ÷ opening at cap) for those 8 goes from 0.83–0.84 to
  [0.95, 1.03].
