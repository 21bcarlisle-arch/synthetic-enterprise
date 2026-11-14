# What a baseload hedge at the published forward leaves open for domestic demand

**Knowledge:** hedging-forward-market

*Worker tick, 2026-11-14, for `G15_forward_curve_series_to_backtest_hedging_by_physics` (L0). This is the step named in
c85ef6e557: "a demand-shaped hedge cost by delivery year against this series". Series:
`ofgem_forward_weekly_with_delivery_start_2021_2026.json`. Rule for its delivery axis:
`the_published_forward_gets_its_delivery_axis_from_the_cap_indexation_rule_2026-10-10.md`.*

## What is measured, said before it is measured

A supplier serving domestic demand `q_h` buys, at trade week `w`, a flat (baseload) volume equal to the mean demand
`b = mean(q_h)` over the delivery year at the published forward `F_w`, and buys or sells everything else at spot `p_h`.
Its cost per MWh delivered is

    hedged = F_w + (P_shape - P_base)

where `P_shape = sum(q_h p_h) / sum(q_h)` (spot weighted by the demand shape) and `P_base = mean(p_h)` (spot weighted
by time). Unhedged, it pays `P_shape`. So:

- **The shape premium `P_shape - P_base`** is what the baseload forward does not price: the extra a demand shape pays
  over flat delivery. It is paid hedged or unhedged. It is the part of the cost set by physics (when households use
  energy), not by when the supplier traded.
- **The hedge's gain against floating is `P_base - F_w`.** The demand shape does not enter it: a flat hedge on a shaped
  load gains or loses exactly what a flat hedge on a flat load does. So "applying a demand shape" changes the level of
  the hedged cost, and not the hedge's P&L.

Each quantity, in words:
- `F_w`: Ofgem's volume-weighted broker average for the cap's baseload reference contracts in trade week `w`, for 12
  months from the week's `delivery_start`. A traded price, published as of `trade_week_end`.
- `p_h`, electricity: Elexon system sell price (SSP) per half hour (`sim/cache/elexon_ssp_full.json`, then
  `elexon_ssp_live_rolling.json`). It is the imbalance cash-out price, not a traded day-ahead index. MID, the traded
  index, is cached only to 2020 (`sim/market_index_history.py`). So `P_base - F_w` carries the SSP-vs-traded basis.
- `p_h`, gas: `sim/gas_data/nbp_sap.csv`. Despite its name, this is **not** SAP. It is the IMF's monthly Europe gas
  price (FRED PNGASEUUSDM, which the IMF sources from UK NBP) at a fixed GBPUSD of 1.28, expanded to days
  (`docs/data-sources/gas-nbp.md`). So it is one price per month, and its pound level is off by the year's FX (GBPUSD
  averaged about 1.24 in 2022). The shape premium is a ratio inside one series, so the fixed FX cancels from it; the
  level gap `P_base - F_w` does not. *Correction beside the 10 Oct page's claim:* its "NBP SAP" realised gas column is
  this same monthly IMF series, not SAP.
- `q_h`, electricity: Profile Class 1 group average demand per half hour, by season and day type
  (`sim/profile_class_1.py`, Elexon's 1997 reference GAD via UKERC). Settlement-grade shape, but a 1997 shape.
- `q_h`, gas: DESNZ Energy Trends 4.2 domestic monthly shares, the 2023-2025 average
  (`how_a_supplier_shapes_an_estimate_for_an_unread_month.md` section 4). One weight per calendar month; within a
  month gas is flat, which the price series is too.

A delivery year is counted only if the price cache covers at least 330 of its days.

## Predictions, filed before the run (14 Nov)

1. **Electricity shape factor `P_shape / P_base` is above 1 on every delivery year, between 1.02 and 1.12.** PC1's
   evening peak meets the evening price peak, and its winter weight meets winter prices.
2. **Gas shape factor is above 1 on most delivery years, between 1.02 and 1.15, but at least one 2022 delivery start
   reads below 1.** A delivery year starting 1 Apr 2022 holds the Aug-Sep 2022 price peak in months when households
   burn little gas, so the winter weighting can fall on the cheaper months.
3. **`P_base - F_w`, the hedge's gain, keeps the signs of the 10 Oct table by trade year:** hedging in 2021 gained
   (forward below realised), hedging in 2022 and 2023 lost, 2024 roughly even.
4. **The shape premium is small beside the hedge's gain or loss** in 2021-2023: below a fifth of `|P_base - F_w|` in
   median, for both fuels. Outside the crisis it may not be.

If prediction 1 fails low (a factor at or below 1), either the PC1 shape is mis-aligned to settlement periods or SSP's
evening peak is weaker than its cash-out spikes elsewhere in the day.

## Measured (14 Nov, after the predictions above)

Scripts: `/var/tmp/g15shape/measure.py` and `mid_vs_ssp.py`. Series, one row per fuel per assigned trade week plus one
cap-style ladder row per delivery start: `ofgem_forward_weekly_hedge_backtest_by_delivery_year_2021_2025.json`. 400 weeks
are graded: 232 electricity, to trade week 2025-08-11, and 168 gas, which stops at delivery start 2024-07-01 because its
price cache ends 2025-06-07.

### The shape premium, by delivery start (GBP/MWh)

| Delivery start | Elec base | Elec PC1-weighted | factor | Gas base | Gas domestic-weighted | factor |
|---|---:|---:|---:|---:|---:|---:|
| 2021-10-01 | 203.92 | 210.60 | 1.033 | 102.44 | 90.28 | **0.881** |
| 2022-04-01 | 184.16 | 189.43 | 1.029 | 90.04 | 71.78 | **0.797** |
| 2022-10-01 | 117.19 | 129.69 | 1.107 | 44.71 | 54.25 | 1.213 |
| 2023-01-01 | 94.43 | 102.30 | 1.083 | 34.28 | 38.15 | 1.113 |
| 2023-04-01 | 77.96 | 81.43 | 1.045 | 28.93 | 28.60 | 0.989 |
| 2023-07-01 | 72.00 | 75.96 | 1.055 | 28.08 | 27.69 | 0.986 |
| 2023-10-01 | 70.22 | 74.51 | 1.061 | 28.63 | 27.85 | 0.973 |
| 2024-01-01 | 71.17 | 75.72 | 1.064 | 29.06 | 28.76 | 0.990 |
| 2024-04-01 | 80.77 | 87.96 | 1.089 | 32.80 | 35.27 | 1.075 |
| 2024-07-01 | 82.64 | 89.50 | 1.083 | 34.09 | 36.05 | 1.057 |
| 2024-10-01 | 83.44 | 89.82 | 1.076 | | | |
| 2025-01-01 | 80.56 | 86.22 | 1.070 | | | |
| 2025-04-01 | 77.47 | 81.71 | 1.055 | | | |
| 2025-07-01 | 83.33 | 86.86 | 1.042 | | | |
| 2025-10-01 | 95.97 | 97.95 | 1.021 | | | |

### The hedge's gain against floating, by trade year (medians over the year's weeks, GBP/MWh)

| Fuel | Trade year | Weeks | Forward | Gain `P_base - F` (range) | Shape premium | Hedged | Floating | `|prem|/|gain|` |
|---|---|---:|---:|---|---:|---:|---:|---:|
| Electricity | 2021 | 48 | 79.8 | +123.3 (-56.4 to +150.8) | 6.68 | 85.9 | 210.6 | 0.05 |
| | 2022 | 49 | 245.6 | -140.8 (-416.8 to +24.8) | 12.50 | 254.7 | 129.7 | 0.09 |
| | 2023 | 51 | 124.1 | -53.9 (-117.0 to -3.6) | 4.29 | 128.4 | 75.7 | 0.08 |
| | 2024 | 52 | 80.1 | +0.7 (-11.4 to +21.1) | 6.38 | 86.0 | 88.7 | 1.27 |
| | 2025 | 32 | 83.0 | +3.2 (-26.6 to +17.7) | 3.53 | 85.4 | 86.9 | 0.31 |
| Gas | 2021 | 48 | 25.4 | +74.2 (-2.1 to +86.7) | -12.16 | 10.3 | 90.3 | 0.16 |
| | 2022 | 49 | 92.6 | -55.8 (-167.9 to +36.1) | 9.54 | 102.2 | 54.2 | 0.15 |
| | 2023 | 51 | 44.2 | -15.7 (-36.7 to +2.4) | -0.33 | 43.8 | 28.6 | 0.02 |
| | 2024 | 20 | 26.9 | +6.2 (+3.8 to +10.2) | 1.96 | 29.3 | 36.0 | 0.39 |

The cap-style ladder (the mean forward over all of a delivery start's assigned weeks, which is what the cap's own
index averages) is in the file's `ladder_by_delivery_start`. Its hedged cost for electricity delivered from
2023-01-01 is GBP 398.64/MWh against GBP 102.30 floating: the window that set the Q1 2023 cap is the window of
the 2022 peak.

### The predictions, graded

1. **Electricity factor in 1.02 to 1.12, above 1 every year: held.** 15 of 15 delivery starts, 1.021 to 1.107. The
   premium is GBP 2.0 to 12.5/MWh.
2. **Gas factor above 1 on most delivery years: refuted.** 4 of 10 are above 1; 6 are below. The 2022 leg held, and more
   than predicted: the delivery years from 1 Oct 2021 (0.88) and 1 Apr 2022 (0.80) both put most of their weight on
   months cheaper than the 2022 summer-autumn peak. What I did not predict is the four delivery years from Apr 2023 to
   Jan 2024 at 0.97 to 0.99: in this series, the winter of 2023/24 was not dearer than the summer around it. I cannot yet
   say whether that is the market or the instrument (next section).
3. **The signs of the hedge's gain by trade year: held.** 2021 gained, 2022 and 2023 lost, 2024 about even, on both fuels.
4. **The shape premium is below a fifth of the hedge's gain or loss in median, 2021 to 2023: held** (0.02 to 0.16).
   Outside the crisis it is not: in 2024 the electricity shape premium is larger than the hedge's median gain (1.27).

### One variable checked: is SSP the wrong spot for the shape?

On 2017-2020, where MID (the traded index) is cached, the PC1 shape factor on the same half hours reads:

| Year | MID | SSP |
|---|---:|---:|
| 2017 | 1.066 | 1.061 |
| 2018 | 1.045 | 1.040 |
| 2019 | 1.062 | 1.057 |
| 2020 | 1.088 | 1.093 |

They agree within 0.006. So SSP's cash-out spikes do not inflate the electricity shape premium; the level gap
`P_base - F` still carries the SSP-vs-traded basis, which this check does not size.

## What it changes, and what it does not settle

- **For hedging by physics:** the electricity shape premium of PC1 demand over baseload is real, steady and physical:
  2 to 11% in every delivery year since 2021, on a traded and a cash-out price alike. A baseload hedge leaves it open
  in all of them. It is small beside a crisis-year hedge P&L and dominant in a calm year. That is the size of what a
  supplier's shaping (peak blocks, or the cap's own shaping allowance) must buy.
- **The demand shape does not change the hedge's P&L against floating** (section 1's identity). So any backtest that
  reports a hedge "gain" from a demand-shaped run is reporting `P_base - F` plus whatever its shape model gets wrong.
- **GAP, the gas instrument.** The gas shape rests on one monthly price per month from an IMF series at a fixed FX,
  documented as NBP-sourced. NBP's own day-ahead is widely reported to have traded at a deep discount to continental hubs
  in summer 2022, when GB's export capacity was full (not sourced on this page); if the IMF series follows a continental hub in those months, it
  overstates GB summer prices, and the gas factors below 1 would be partly the instrument. Not checked here: it needs
  a daily NBP SAP series (National Gas MIPI, PUBOB603), which `docs/data-sources/gas-nbp.md` records as behind a
  login. Until then the gas rows are published with this caveat, and the electricity rows stand on their own.
- **GAP, the 1997 shape.** PC1's group average demand is the 1997 reference year. A 2020s domestic load (LED lighting,
  some heat pumps and EVs, solar) has a different evening ramp; `docs/data-sources/profile-class-1.md` keeps the
  provenance. A newer shape would move the premium; this does not size by how much.
- **Not a supplier's hedge P&L yet.** No hedge ladder beyond the single week and the cap-style mean, no peak products,
  no volume risk (demand that moves with the price, which is where hedging by physics really bites: weather moves
  both). Those need the world's demand on the delivery axis, and that is a world build in `sim/`, not made here.
