**Severity:** RECORDED · **Lane:** G_data_learning · **Atom:** `W1_6_physics_price_signal`

# Result: the world's power record has the right monthly level, and twice the within-day noise and negative tail of the traded price; gas plus carbon explains the traded price with nothing fitted (2026-11-24)

Pre-registered in `SEAT_PREREG_GRADE_THE_WORLDS_POWER_RECORD_AGAINST_THE_ELECTRICITY_PAGE_BY_REGIME_2026-11-24.md`,
landed as `6c828bc2c` before the probe first ran. The probe ran unchanged, read-only, in 6 s, from
the shared repo root. The page graded against is
`docs/market_research/how_the_gb_electricity_price_forms_2026-11-24.md`.

## The numbers

World = SSP (the imbalance price every run settles at). MID = Elexon's traded short-term price.
SRMC = monthly SAP ÷ DUKES fleet CCGT efficiency, plus (CPS + allowance) × 0.1829 ÷ efficiency.
Nothing is fitted: no intercept, no slope.

| | pre-crisis | crisis 2021-07..2023-06 | post-crisis |
|---|---|---|---|
| E1 monthly MAE SSP vs MID, £/MWh (bias SSP − MID) | 2.03 (+0.30), 58 months | 4.57 (+1.13), 24 | 1.76 (+0.05), 24 |
| E2 median MID − SRMC with carbon, £/MWh | +2.51 | +10.09 | **−9.80** |
| E2 monthly MAE: with carbon · gas only | **2.80 · 17.58** | 14.99 · 44.81 | 11.03 · 14.21 |
| E4 half-hours above £500: SSP · MID | 62 · 14 | 526 · 357 | 21 · 16 |
| E5 within-day SD, SSP ÷ MID | 2.12 | 1.95 | 1.83 |
| E8 corr(MID − SRMC, FUELHH wind share), monthly | −0.45 | −0.56 | −0.64 |
| E9 MID winter/summer | 1.09 | 1.05 | 1.21 |

Pre-crisis is 2016-09-12..2021-06-30 for E1/E4/E5/E9 and 2018-01..2021-06 for E2/E8 (SAP starts 2018).
Post-crisis runs to 2025-06-07, and to 2024-12 for E2/E8 (no allowance price is held for 2025).

| Year | Negative half-hours SSP · MID | France net TWh | All links net TWh | Norway | Ireland (Moyle+EWIC) | Nuclear TWh (FUELHH) |
|---|---|---|---|---|---|---|
| 2016 | 133 · 0 (MID from Sep) | +9.90 | +17.85 | 0 | +0.54 | 66.7 |
| 2017 | 68 · 41 | +7.81 | +15.67 | 0 | +1.00 | 65.5 |
| 2018 | 108 · 18 | +12.87 | +19.24 | 0 | −0.20 | 60.6 |
| 2019 | 139 · 60 | +11.14 | +21.24 | 0 | −0.80 | 52.7 |
| 2020 | 341 · 329 | +8.71 | +18.34 | 0 | +0.62 | 47.4 |
| 2021 | 149 · 65 | +13.65 | +24.81 | +1.41 | −1.36 | 43.4 |
| 2022 | 314 · 133 | **−9.98** | **−4.21** | +2.78 | +0.88 | 44.7 |
| 2023 | 850 · 428 | +12.86 | +23.39 | +8.53 | −3.71 | 38.3 |
| 2024 | 1,073 · 495 | +19.45 | +33.30 | +9.62 | −5.18 | 38.3 |
| 2025 | 444 (to 7 Jun) · 489 | +21.94 | +31.96 | +8.97 | −3.92 | 34.1 |

FUELHH against DUKES (published, not graded): France 2022 −9.98 against DUKES −10.0; all links 2022
−4.21 against −5.3; nuclear 66.7 against 71.7 (2016) and 38.3 against 40.6 (2024). FUELHH is
transmission-metered.

## Predictions against outcomes (kept as filed)

| Check | Predicted | Outcome | Held? |
|---|---|---|---|
| E1 pre | MAE ≤ £4, bias −1..+4 | 2.03, +0.30 | held |
| E1 crisis | MAE £8-30 | 4.57 | **missed**: SSP tracked the traded price more closely in the crisis than I expected |
| E1 post | ≤ £6 | 1.76 | held |
| E2 pre median | −5..+10 | +2.51 | held |
| E2 crisis | median > +10, MAE > 2 × pre | +10.09, 14.99 against 5.6 | held (the median by £0.09) |
| E2 post median | −5..+15 | −9.80 | **missed**: the traded price sat below gas-plus-carbon SRMC after the crisis |
| E2 carbon lowers MAE, all regimes | | 2.80 < 17.58, 14.99 < 44.81, 11.03 < 14.21 | held |
| E3 MID ≤ 5 negative half-hours in 2016-18 | | 0, 41, 18 | **missed**: my prior was the day-ahead count (none before Dec 2019). The within-day traded price went negative from 2017. |
| E3 MID ≥ 50 in 2023, ≥ 150 in 2024 | | 428, 495 | held |
| E3 SSP ≥ 3 × MID, 2017-2024 | | 1.0-6.0×, mostly about 2× | **missed** |
| E4 SSP above £500 pre ≥ 30 | | 62 | held |
| E4 MID above £500 pre ≤ 5 | | 14 | **missed** |
| E4 MID crisis ≥ 20 | | 357 | held |
| E4 SSP ≥ 2 × MID every regime | | 4.4×, 1.5×, 1.3× | **missed** in crisis and post |
| E5 SSP ÷ MID ≥ 1.5 every regime | | 2.12, 1.95, 1.83 | held |
| E6 France negative in 2022, positive 2017-21 and 2024 | | −9.98; all positive | held |
| E6 all links negative in 2022 | | −4.21 | held |
| E6 Norway positive in 2022 | | +2.78 | held |
| E6 Ireland negative every year | | positive in 2016, 2017, 2020, 2022 | **missed**: GB exports to Ireland only from 2018, and not in every year |
| E7 nuclear 55-72 (2016), 35-45 (2024), fall ≥ 30% | | 66.7, 38.3, −42.5% | held |
| E8 ≤ −0.3 pre and post | | −0.45, −0.64 | held |
| E9 pre 1.05-1.35 | | 1.09 | held |

Twenty-two rows: fifteen held, seven missed. Four of the misses (E3 early years, E3 ratio, E4 MID pre,
E4 ratio) share one cause. My priors for the traded price were taken from the day-ahead auction, and
MID is the within-day traded price, which has its own negatives and spikes. The other three are
substantive: E1 crisis, E2 post and E6 Ireland.

## What it means, mechanism by mechanism (page sections)

1. **Level (§0): the world's record is right at the month.** SSP's monthly mean is within £2 of the
   traded price outside the crisis and £4.57 inside it, with a bias under £1.20 in every regime. Unlike
   gas (MAE £16.40 in the crisis), the power level is not the fault.
2. **Gas plus carbon (§1-2): it explains the traded price with nothing fitted, and carbon is most of
   the fix.** Pre-crisis, gas-plus-carbon SRMC at fleet efficiency misses the monthly traded price by
   £2.80. Gas alone misses by £17.58. The chain's −£12 pre-crisis bias is of the size of the missing
   allowance (page §2). This gives item 3, the carbon arm, its prediction: adding CPS and the allowance
   price should remove most of the chain's pre-crisis bias. **Filed here, before that arm runs:** with
   CPS and the allowance in its merit order, the chain's pre-crisis monthly bias moves from −£12.0 to
   within ±£4, and its pre-crisis monthly MAE falls from £12.4 to ≤ £7. The crisis and post-crisis
   errors fall by less, because carbon is not the largest of their gaps.
3. **Post-crisis, the traded price sat £9.80 below gas-plus-carbon SRMC. I cannot yet say why.** Three
   candidates, unranked. (a) The carbon input is a civil-penalty proxy averaged over the PREVIOUS year's
   futures, and the UKA fell through 2023-24, so the proxy is likely too high. (b) More hours with gas off
   the margin: record imports (33 TWh in 2024) and more wind. (c) The marginal plant was more efficient
   than the fleet average. The UKA market series (page GAP 1) separates (a) from (b) and (c).
4. **Imbalance against traded (§0, §7): the world's record carries about twice the within-day noise.**
   SSP's within-day SD is 1.8-2.1 times the traded price's in every regime. It has about twice the
   negative half-hours in most years, and 4.4 times the £500+ spikes before the crisis. Everything in
   the world valued on within-day shape (ToU spreads, flexibility, a shift's value, imbalance exposure)
   is valued on a price that no supplier's hedged energy pays. **This is the larger finding for the
   company's tariff and flex work.** It is a baseline-fidelity matter, and it is filed beside this record.
5. **Interconnectors (§5): the page's 2022 account holds.** FUELHH puts France at −9.98 TWh in 2022,
   against DUKES −10.0. The world has the flow data but no interconnector term in its price.
6. **Nuclear (§4) fell 42% on FUELHH between 2016 and 2024**, as DUKES says. **Wind (§6)**: the monthly
   gap between the traded price and gas-plus-carbon SRMC falls as the wind share rises (−0.45 to −0.64).
   That is the "wind pushes gas off the margin" mechanism, seen on the record.

## What this does NOT establish

- MID is within-day traded, not the day-ahead auction. Day-ahead is not held. A supplier's forward
  cost is smoother still, so every SSP-over-MID ratio here understates the gap from what a supplier pays.
- Nothing here grades the forward-year chain. The chain grade did that. This record says which
  mechanisms the chain's rebuild needs most: carbon first, then the imbalance-versus-traded definition
  of the price it is fit to.
- The allowance series is a proxy (page §2, choice 3).

## The probe

As filed in the pre-registration, unchanged. Run from the shared repo root: `python3 probe.py` with the
text of the PREREG record's code block. Output was saved and is reproduced in the tables above.
