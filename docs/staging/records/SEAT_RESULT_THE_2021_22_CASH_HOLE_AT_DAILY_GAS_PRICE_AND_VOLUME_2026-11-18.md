**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`

# Result, third test: the 2021-22 cash hole at daily gas price against daily gas volume (2026-11-18)

*Delivery seat, claim `world-ranks-2021-22-gas-shape-on-a-daily-price`. Pre-registration, written before the run and
unchanged: `SEAT_PREREG_THE_2021_22_CASH_HOLE_AT_DAILY_GAS_PRICE_AND_VOLUME_2026-11-18.md`. Instrument:
`python3 -m tools.strategy_cash_hole_2021_22 --third-test`. Full output:
`SEAT_RESULT_CASH_HOLE_AT_DAILY_GAS_PRICE_2021_22_2026-11-18.json` beside this file. The second test's output was
reproduced exactly after the refactor (every H, every run).*

## The world now has a daily GB gas price

`sim/gas_data/sap_daily.csv` holds National Gas Transmission's System Average Price for each actual gas day, as
republished by ONS under OGL v3 ("System Average Price (SAP) of gas", edition of 12 Nov 2026, sha256 pinned). It runs
2018-01-01 to 2025-12-31, all 2,922 days, with no gaps. It is read by `sim.gas_prices_history.load_sap_daily`. This is
the PUBOB603 series that `docs/data-sources/gas-nbp.md` named, reached without the MIPI OAuth login, so **no
credential question arises**. It sits beside `nbp_sap.csv` (the monthly TTF proxy) and does not replace it. Only
this instrument reads the new record, and the proxy still feeds the world's forward curve (see "What is handed on").

## Headline

**Shape does not separate the strategies, and it cannot while every disclosed hedge is baseload.** This was predicted
from the instrument's algebra and confirmed by the run. With the daily price against the world's daily weather, the
shape term is **−£15.54 per opening customer at fixed share 0.5 and −£15.86 at 0.75 (anomaly weather), identical for
S1 to S5 to four decimal places**, under both the static and rolling readings. Shape is a cost every supplier bears in
proportion to its volume on supply, whatever it hedged. The second test's open question ("is shape the weather
mechanism that separates a well-hedged book from a badly hedged one?") therefore has a structural answer in this
world: **no, not for these five strategies.** Separating them would take a shaped position (a winter-weighted
profile, storage, a weather derivative), and none of them has a published one.

**The verdict holds on the real GB price.** Under `sap_daily`, anomaly weather and the static reading, the test passes:
S5's hole is −£18.74, the smallest S1–S4 hole is −£238.46 (S4 at 0.75), and there are no inversions. All 18 runs
pass: 3 weathers × 3 gas prices × 2 readings.

## The two effects, separated (static; wholesale cash Jul-21 to Mar-22, £ per opening customer)

| | price source (SAP monthly − TTF proxy), normal weather | shape (SAP daily − SAP monthly), anomaly | shape, level |
|---|---|---|---|
| S1 unhedged, 0.5 / 0.75 | +80.56 / +82.07 | −15.54 / −15.86 | −14.26 / −14.56 |
| S2 20%/15% | +65.64 / +67.16 | same | same |
| S3 PFP · Together, 0.5 | +34.10 · +30.55 | same | same |
| S4 Pure Planet, 0.5 / 0.75 | +35.74 / +17.87 | same | same |
| S5 cap 6-2-12, 0.5 / 0.75 | −3.03 / −1.52 | same | same |

The price source is what moves the strategies apart. Over the window the GB SAP ran below the TTF proxy converted at
1.28 $/£ (for example Dec-21: £91.49/MWh SAP), and the unhedged books gain most from that. The shape term is a
common shift.

## Holes (static, anomaly weather, credit £65; deepest per strategy across fixed shares)

| | TTF monthly (test two) | SAP monthly | SAP daily |
|---|---|---|---|
| S1 | −956.05 | −879.76 | −895.31 |
| S2 | −780.58 | −719.21 | −734.75 |
| S3 | −426.77 | −396.94 | −412.48 |
| S4 | −456.05 | −424.59 | −440.13 |
| S5 | 0.00 | −2.87 | −18.74 |
| band | 0 to 236.12 | 2.87 to 222.60 | 18.74 to 238.46 |

## Prediction beside outcome

| Predicted (before the run) | Outcome |
|---|---|
| 1. Shape effect identical across S1–S5 to £0.01 at each fixed share and weather | **Right**, to £0.0001 |
| 2. Shape exactly zero at normal weather | **Right** |
| 3. Shape a cost between −£0.50 and −£15 | **Sign right, magnitude just outside on the primary basis:** −£15.54 and −£15.86 under anomaly; −£14.26 and −£14.56 under level. I under-guessed the covariance in a mild winter. A cold Dec-21 week on the spike, and the warm, cheap New Year, both add cost in this term |
| 4. The verdict passes on `sap_daily`; S5's hole ≤ £25; band ≥ £150 wide | **Right:** S5 −£18.74, band £219.72 wide |

## What this does and does not establish (F11)

- It does **not** net the shape cost against the cap's own shaping allowance. The uplift `k` scales every spot price,
  and the cap's allowance prices an *expected* shape. The −£15 is therefore the realised covariance on a baseload
  book before any allowance. It is common to all strategies, so it cannot move the ranking, but it should not be
  read as a loss the cap failed to fund.
- Day-ahead SAP is the price at which a supplier balances its daily gap. Within-day and imbalance (SMP buy/sell) cost
  more and are not modelled. Every strategy pays them alike for the same reason as above.
- Still GAPs, unchanged: leavers within the year and SoLR inflow, and a cold winter at a high spot.

## What is handed on

The world's forward curve and every gas run still read the monthly TTF proxy (`nbp_sap.csv`). The daily SAP covers
2018 onwards only, so it cannot replace the proxy for the 2015-10 lookback. Whether the world should splice SAP from
2018 (a fidelity change to the baseline, decided blind to company results) is the next question. The price-source
effect above (+£80 on an unhedged book over nine months) shows the change would not be cosmetic.
