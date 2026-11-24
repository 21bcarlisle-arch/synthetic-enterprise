# The world's synthetic forward against the published forward, 2021-2025

**Knowledge:** hedging-forward-market

*Worker tick, 2026-11-16, for `G15_forward_curve_series_to_backtest_hedging_by_physics` (L0). The step after
`what_a_baseload_hedge_at_the_published_forward_leaves_open_for_domestic_demand_2026-11-14.md`, which measured a hedge
at the published forward. Every hedge the world books today is booked at a different number:
`sim.forward_curve.generate_forward_price` (a K8 note of 12 Oct made it "the market's quote"). That function is a
model: a 30-day-half-life EWMA of daily spot over the 90 days before the trade, times a seasonal shape over the
delivery months, times a term premium of 6% (electricity) or 5% (gas). This page asks how far that model sits from the
traded price a real supplier could have dealt at, week by week.*

## What is compared, said before it is measured

- **Published, `F_pub`.** Ofgem's weekly broker average for 12 months of baseload from `delivery_start`, as of
  `trade_week_end` (`ofgem_forward_weekly_with_delivery_start_2021_2026.json`, 566 rows).
- **Synthetic, `F_syn`.** `generate_forward_price` called with `acquisition_date` = the day after `trade_week_end`, so
  it sees only prices up to the trade week's end, as the published price did, and a 12-month contract. The function's
  seasonal shape starts at the trade month, not the delivery month; over 12 months both tables average 1.00 within
  0.01, so the difference is ignored. The cold-spell multiplier is off (it is not passed temperatures here).
- **Spot inputs:** the world's own: SSP half-hourly (`sim/cache/elexon_ssp_full.json`, then the live rolling cache) and
  the monthly IMF gas series in `sim/gas_data/nbp_sap.csv` (see the 14 Nov page's correction: not SAP).
- **Reported:** by fuel and trade year, the median of `F_syn / F_pub`, its interquartile range, the median gap in
  GBP/MWh, and the share of weeks where `F_syn` is within 15% of `F_pub`.

## Predictions, filed before the run (16 Nov)

1. **Electricity, 2024 and 2025 trade years (calm):** median ratio between 0.85 and 1.20, and at least half the weeks
   within 15%.
2. **Electricity, 2022:** the synthetic sits below the published, median ratio below 0.85. The traded forward priced
   the winter of 2022/23 above what spot had already shown.
3. **Electricity, 2023:** still below, median ratio 0.70 to 0.95: spot fell faster than the 12-month-ahead price.
4. **Electricity, 2021:** above, median ratio 1.00 to 1.40: autumn 2021 spot ran ahead of a forward for delivery a year out.
5. **Gas follows the same signs by year**, noisier, because its spot input is one price per month.
6. **Across all weeks, fewer than half are within 15%** for either fuel. If more than half are, the synthetic model is a
   fair stand-in for the traded quote and this atom's backtest can lean on it; if fewer, a hedge booked in the world is
   booked at a number no supplier could have dealt at.

## Measured (16 Nov, after the predictions above)

Script: `/var/tmp/g15syn/compare.py`, at this tree's `sim/forward_curve.py`. 283 electricity weeks (to trade week
ending 2026-07) and 227 gas weeks (the gas spot cache ends 2025-06-07, so later gas weeks are not graded).

| Fuel | Trade year | Weeks | Published (median) | Synthetic (median) | Ratio median | Ratio IQR | Gap median (GBP/MWh) | Within 15% |
|---|---|---:|---:|---:|---:|---|---:|---:|
| electricity | 2021 | 48 | 79.8 | 90.0 | 1.19 | 1.07-1.34 | +13.3 | 21/48 |
| electricity | 2022 | 52 | 248.4 | 204.1 | 0.81 | 0.59-1.04 | -58.7 | 15/52 |
| electricity | 2023 | 52 | 124.1 | 93.4 | 0.85 | 0.73-1.01 | -20.4 | 26/52 |
| electricity | 2024 | 52 | 80.1 | 72.0 | 0.94 | 0.82-1.05 | -4.4 | 33/52 |
| electricity | 2025 | 52 | 80.1 | 79.7 | 1.05 | 0.97-1.15 | +3.5 | 39/52 |
| electricity | 2026 | 27 | 94.4 | 95.0 | 1.02 | 0.97-1.18 | +1.3 | 19/27 |
| electricity | all | 283 | 89.7 | 92.0 | 1.00 | 0.85-1.12 | +0.2 | 153/283 |
| gas | 2021 | 48 | 25.4 | 30.4 | 1.13 | 1.06-1.56 | +2.5 | 26/48 |
| gas | 2022 | 52 | 95.4 | 93.3 | 1.10 | 0.92-1.21 | +10.0 | 23/52 |
| gas | 2023 | 52 | 44.0 | 35.1 | 0.86 | 0.68-1.09 | -5.8 | 18/52 |
| gas | 2024 | 52 | 31.8 | 29.2 | 0.98 | 0.87-1.04 | -0.8 | 44/52 |
| gas | 2025 | 23 | 34.1 | 39.0 | 1.12 | 1.02-1.20 | +3.5 | 14/23 |
| gas | all | 227 | 38.1 | 36.4 | 1.04 | 0.89-1.18 | +1.1 | 125/227 |

**The extremes are in the crisis, and they run both ways.** Electricity's ratio runs from 1.65 (trade week ending
2021-09-10) to 0.51 (2022-07-29: published GBP 413.59, synthetic GBP 210.22). Gas runs from 2.10 (2021-11-12) to 0.61
(2023-08-25). Sampled every fourth week, electricity reads 1.28 to 1.54 from Aug to Nov 2021, then 0.51 to 0.64 from
Jul to Nov 2022.

### The predictions, graded

1. **Electricity, 2024 and 2025, median 0.85 to 1.20 with at least half within 15%: held** (0.94, 33/52; 1.05, 39/52).
2. **Electricity, 2022, median below 0.85: held** (0.81). The interquartile range, 0.59 to 1.04, says the year is two
   regimes, not one bias: above 1 to April, then far below from June.
3. **Electricity, 2023, 0.70 to 0.95: held** (0.85).
4. **Electricity, 2021, 1.00 to 1.40: held** (1.19).
5. **Gas follows electricity's signs by year: refuted for 2022.** Gas reads 1.10 in 2022 where electricity reads
   0.81. Gas's synthetic input is one price per month, and that price had already risen by spring 2022, so its EWMA
   caught up sooner. 2021 and 2023 held.
6. **Fewer than half of all weeks within 15%: refuted.** 153 of 283 electricity weeks (54%) and 125 of 227 gas weeks
   (55%) are within 15%, and the all-weeks median ratio is 1.00 and 1.04. Over the whole record the synthetic quote is
   unbiased. Its error is concentrated in 2021 to 2023, where the money is.

## What it means

- **The synthetic forward has no term structure, and the crisis was a term-structure event.** It is spot, smoothed,
  plus a fixed premium. In autumn 2021 spot ran far above a backwardated forward, and the model quoted up to 1.65 times
  the dealable price. In summer 2022 the market priced the coming winter well above spot, and the model quoted half the
  dealable price. A real supplier dealing in those weeks met the published price, not either of these.
- **So a world hedge booked from June to December 2022 is booked about GBP 60 to 200/MWh cheaper than any supplier
  could have dealt.** That flatters a 2022 hedger in the world by the gap times the volume. A hedge booked in autumn 2021
  is booked dearer than the market, which penalises it. Any hedging-by-physics backtest on the world's quotes inherits
  both errors, and they fall in the years that decide the result.
- **In calm years the model is a fair stand-in.** In 2024 to 2026 the median sits within 6% of the published price, and
  most weeks are within 15%.
- **This is not yet a build.** It does not change which number the world books at. The K8 choice, recorded here so a
  build can cite it: where the published series covers a trade week (2021-02 onward, both fuels), the world's quote for
  a 12-month baseload hedge should be the published price as of that week's end, which is point-in-time by
  construction (`the_published_forward_has_an_as_of_axis_and_no_delivery_axis_2026-10-07.md`). Before 2021, the
  synthetic model stays, and it carries its measured calm-year error (median ratio 0.94 to 1.05) as its stated range.
  The swap belongs to `sim/forward_curve.py`, the world. It is a fidelity change, decided blind to company results, so
  it may move the company's 2021-2023 margins either way. That move is the evidence, not a reason to hold it.
- **GAP.** The published series is 12-month baseload only. A quote for any other tenor or a peak product has no
  published anchor here, and the synthetic model's error on those is unmeasured.
- **GAP, gas.** The gas comparison inherits the 14 Nov page's instrument caveat: the synthetic gas input is a monthly
  IMF series at a fixed FX, not daily NBP.

## Built 2026-11-23: a world hedge executes at the published forward

`sim.forward_curve.published_forward_quote(trade_date, fuel)` returns the published 12-month price from the latest
week a trader could have seen by `trade_date`. Ofgem says a row is knowable from its Friday, so the row is read from
the following Monday. It returns None before 2021-02-08, and None once the newest row is a week or more stale (the series
ends with the week of 2026-06-29). In `run_phase2b`, the electricity hedge (`run_hedged_term`, the company's
`open_term_hedge` agreed price, the I&C volume-tolerance unwind) and the gas hedge leg (`run_gas_term`) execute at
that price wherever it exists, and at the synthetic model otherwise. Nothing else moves: the company's strike and
hedge sizing (`company_fwd`), the VaR inputs and the basis-risk log still read the synthetic `forward_price`. That
keeps it one variable.

**Prediction, filed before any book is run with it.** Terms starting from Aug 2021 to Mar 2022 book hedges below
the old price (synthetic/published 1.19 to 1.65), so hedge P&L on those terms rises. Terms starting from Jun 2022 to
Mar 2023 book hedges about GBP 60 to 200/MWh dearer, into the 2023 fall in spot, so hedge P&L on those terms falls by
more than the 2021 gain. **Net hedge P&L over 2021 to 2023 term starts falls; 2016 to Jan 2021 term starts are
unchanged to the penny.** If the 2016 to 2020 hedge P&L moves at all, the swap leaked outside its window, and that is a
defect.
