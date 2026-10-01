**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `D_opening_dd_seasonal_sizing` — Lane 0 delivery

# Pre-registration: what billing the SVT segment ex-VAT moves

Claim `bill-the-svt-segment-ex-vat`. Filed before the change is measured.

## First, the 8 accounts at 0.79–0.87 of the cap: explained, and not by this change

The parent finding
(`SEAT_FINDING_THE_EX_VAT_RENEWAL_CEILING_CLEARS_22_OF_28_AND_THE_LAST_6_ARE_THE_WORLDS_SVT_SEGMENT_2026-10-01.md`)
left 8 SVT-origin electricity accounts unexplained. They are PROS-2022-0010, -2022-0097,
-2023-0237, -2024-0199, -2024-0305, -2024-0324, -2025-0013 and -2025-0077. The ratio is not a range.
All 8 sit at **exactly 0.785714 = 11/14** of the inc-VAT cap. The ratio was unchanged by the ex-VAT
ceiling, which never reached them.

11/14 is `saas.tariff_pricing.TOU_OFFPEAK_MULTIPLIER = (1 − 0.30 × 1.5) / 0.70`. These 8 are
smart-meter households, and `company/pricing/tou_desk.decide_tou_offer` splits their flat rate into a
peak and off-peak pair. Their **contracted flat rate is the full inc-VAT cap**, the same as the other
6 (163.43 / 0.785714 = 208.0).

They read as the off-peak leg because of the instrument. `simulation/settlement_daily.fold_to_days`
carries `unit_rate_gbp_per_mwh` from each day's OPENING record. Period 1 (00:00) is off-peak every
day, and the true range survives only in `unit_rate_min/max_gbp_per_mwh`. `simulation.
experienced_bill_shock.sold_unit_rate` reads `unit_rate_gbp_per_mwh`. So for every ToU account it
reports the off-peak rate as "the rate on the first bill". Not one of the 120 rows has more than one
rate value in its first month. That is a separate measuring defect, filed separately (below). It
means **the SVT segment on the inc-VAT cap is 14 accounts, not 6.**

## The change

`simulation/svt_product.build_svt_schedule` divides all three legs by
`1 + simulation.price_cap_enforcement.DOMESTIC_VAT_RATE`: `unit_rate_gbp_per_mwh`,
`household_charged_unit_rate_gbp_per_mwh` and `hmt_epg_receipt_gbp_per_mwh`. All three are read
inc-VAT from the commons. The receipt is included because `unit = charged + receipt` is controlled,
and de-VATing two of three legs would break it by 5% of the receipt. `svt_rates` stays inc-VAT.

## The measurement: one variable

There are two runs of the same default world with the same script
(`/var/tmp/se-exvat/measure_exvat.py`, re-pointed). Both run on the same base, origin/main
`5e02bbdda`. One is the base alone, the other is the base plus this change. The base has moved 22+
commits since the parent's rows were taken, so comparing against those rows would be two variables.

## Predictions

- **P1.** First-month rate above the company's ex-VAT cap by more than 0.1%: **0 of N** with the
  change. The base run should reproduce the parent's 6.
- **P2.** The 6 flat SVT accounts move from sold ÷ inc-VAT cap 1.0000 to **0.9524**.
- **P3.** The 8 ToU SVT accounts move from 0.7857 to **0.7483** (0.7857 / 1.05).
- **P4.** At most 5 of the 106 non-SVT accounts move by more than £0.01/MWh. Any feedback would be
  book-level, through the portfolio premium reading settled margin, and none is predicted to cross
  the ex-VAT cap.
- **P5.** N is 120 ± 3 in both runs.
- **P6.** No account is above the inc-VAT cap in either run.
