**Severity:** LATENT · **Lane:** W3_industry_systems · **Epoch:** 2 · **Atom:** `W3_1b_intra_year_price_cap_granularity` — Lane 0 delivery

# The SVT segment now bills ex-VAT, and no first term sits above the ex-VAT cap

Claim `bill-the-svt-segment-ex-vat`. These are results against
`docs/staging/records/SEAT_PREREGISTRATION_WHAT_BILLING_THE_SVT_SEGMENT_EX_VAT_MOVES_2026-10-01.md`,
which was written before either run. The parent finding is
`SEAT_FINDING_THE_EX_VAT_RENEWAL_CEILING_CLEARS_22_OF_28_AND_THE_LAST_6_ARE_THE_WORLDS_SVT_SEGMENT_2026-10-01.md`.

## What changed

`simulation/svt_product.build_svt_schedule` now writes every leg ex-VAT, through `_ex_vat`, which
divides by `1 + price_cap_enforcement.DOMESTIC_VAT_RATE`. The three legs are
`unit_rate_gbp_per_mwh`, `household_charged_unit_rate_gbp_per_mwh` and
`hmt_epg_receipt_gbp_per_mwh`. Including the receipt keeps `unit = charged + receipt` exact.
`svt_rates` is untouched and stays inc-VAT. Before this, settlement booked an SVT household's
inc-VAT cap as ex-VAT revenue, so its revenue was 5% high. Every reader that grosses up again (the
DD opening, `experienced_bill_shock._inc_vat`) added VAT twice. And `bill_shock_tracker` saw a
spurious +5% on every fixed→SVT step, because it compares that charged leg against ex-VAT fixed
rates.

Four controls pinned the old reading as `segment rate == published series`. They now assert
`segment rate × (1 + VAT) == published`, recomputed from the published figure. Each one goes red
if the division is dropped: the full run showed exactly those 4 red on the change before they
were re-keyed. The four are:
- `test_svt_product::test_the_rate_is_the_published_series_and_is_never_struck`
- `test_the_hmt_receipt_leg…::test_the_billed_rate_did_not_move…`
- `test_the_gas_leg_rolls_onto_the_cap…::test_a_gas_segment_is_billed_off_the_published_GAS_cap…`
- `test_svt_assignment::test_the_svt_stint_carries_no_notice_and_no_struck_rate`

## The 8 "unexplained" accounts were ToU, and also on the inc-VAT cap

All 8 sat at exactly 11/14 of the cap, which is `TOU_OFFPEAK_MULTIPLIER`. They are smart-meter
households on a ToU split of the same flat inc-VAT cap. `settlement_daily.fold_to_days` carries each
day's opening-period rate, which is off-peak at 00:00, so `sold_unit_rate` reads the off-peak leg.
So the defect covered 14 accounts, not 6. The full reasoning is in the pre-registration.

## Results: one variable, two runs of the same world on origin/main `5e02bbdda`

| prediction | base | with change | verdict |
|---|---|---|---|
| P1: above the ex-VAT cap | 6 (the parent's six) | **0 of 120** | HOLDS |
| P2: 6 flat SVT, sold ÷ inc-VAT cap | 1.0000 | **0.9524** each; DD opening ratio 1.03–1.04 → 1.0000 | HOLDS |
| P3: 8 ToU SVT | 0.7857 | **0.7483** each | HOLDS |
| P4: non-SVT accounts moved more than £0.01 (≤ 5 predicted) | | **0 of 106** | HOLDS |
| P5: N | 120 | 120 | HOLDS |
| P6: above the inc-VAT cap | 0 | 0 | HOLDS |

Rows: `/var/tmp/se-svtvat-base/rows.json` and `/var/tmp/se-svtvat-new/rows.json`. The comparison
script is `/var/tmp/se-svtvat-new/compare.py`.

Between the parent's finding and this one, the 28 first terms the parent found above the ex-VAT cap
are now 0.

## Handed on: two more of the same class, not fixed here

1. **The ToU sold-rate instrument.** `experienced_bill_shock.sold_unit_rate` reads the daily
   `unit_rate_gbp_per_mwh`, which is the off-peak rate on every ToU account, not the bill's
   consumption-weighted rate. The daily row already has what is needed: the summed `revenue_gbp`
   and consumption of the hedged writer, plus `unit_rate_min/max`. So the DD opening for every ToU
   household is sized about 21% low on the unit leg. That is what the 0.83–0.84 ratios above are.
2. **The switching reference compares across VAT bases.**
   `simulation/customer_events._price_differential_vs_market` takes `(offer − reference) /
   reference`. The offer is an ex-VAT company rate. The reference is the inc-VAT published SVT,
   through `_reference_level_gbp_per_mwh` and `competitor_reference`. There is no VAT term anywhere
   in either module. Every offer therefore reads about 4.8% cheaper than the household's real
   alternative, which drives churn. This is the VAT rule's sixth implementation. It moves the
   world's churn, so it needs its own pre-registration and run.
