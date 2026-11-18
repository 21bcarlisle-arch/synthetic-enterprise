**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`

# Pre-registration, second test: the 2021-22 cash-hole ranking with the world's own weather on gas volume (2026-11-18)

*Delivery seat, claim `world-ranks-2021-22-reregister-and-test-the-non-price-world`. Written before any weather number
from the world has been read for this window. It re-registers the first test
(`SEAT_PREREG_THE_WORLD_PUTS_A_BIGGER_CASH_HOLE_IN_THE_FAILED_STRATEGIES_THAN_IN_THE_CAP_TRACKING_SURVIVOR_2026-11-18.md`,
result in `SEAT_RESULT_THE_WORLD_PUTS_A_BIGGER_CASH_HOLE_IN_THE_FAILED_STRATEGIES_2026-11-18.md`). Everything not named
here is unchanged from that pre-registration: the window, the strategies S1-S5 and their published parameters, the
commodity basis, the static reading as primary, the F grid and the verdict rule.*

## 1. What changes, and why

1. **Fixed share 1.0 is dropped.** With no default-tariff book, S4 and S5 are the same book and tie by definition. The
   sweep is {0.5, 0.75}. This is the post-hoc removal from the first result, now made before the run.
2. **The credit-balance level sweep is dropped.** The level cancels out of H, as shown by algebra and held by a
   control. One level (NERA £65) is run. The *shape* still matters, and with weather it moves (item 3c).
3. **The world's real 2021-22 weather goes onto gas volume.** This is the first part of the world that is not price.
   It is Together's "demand uncertainties".

## 2. How the weather enters (fixed before the run)

- **Which weather.** It is the world's own store, `sim/weather_world` (HadUK-Grid 1 km daily mean temperature, all
  919 cells). Daily HDD per cell is max(0, 15.5 − mean temperature). The day's HDD is the equal-weight mean over
  cells. Per-cell HDD is averaged, not the HDD of the mean temperature, because HDD is convex.
- **Its anomaly, not its level.** The store reads about 1.2 °C warmer than the 1991-2020 England & Wales normal at
  urban cells (`sim/weather_hdd.py`). Its level would show up as less gas whatever the year. So each month's HDD is
  `REFERENCE_MONTHLY_HDD[m] × (store HDD in that month of 2021-22) / (store mean HDD in that calendar month,
  2016-2025)`. The baseline is the store's own ten years, not 1991-2020: that is a GAP, and its direction is that
  2016-2025 is warmer than 1991-2020, so the ratio reads 2021-22 as slightly *colder* than it was against the true
  normal. As a sensitivity, not part of the verdict, the store's level is also run straight (absolute store HDD).
- **What a supplier knew, and what happened.** Volumes the supplier *planned on* stay at normal weather. Volumes that
  *happened* use the 2021-22 weather. Concretely:
  - (a) Hedge cover is sized on the normal-weather volume (`cover × planned`). The difference between actual and
    planned is bought at spot when short, and sold at spot when long.
  - (b) Revenue is booked on actual volume: on the SVT at the cap's allowance, on the fixed book at the strike.
  - (c) Direct debits are set so that the year Apr-21 to Mar-22 balances at *normal* weather. Bills follow *actual*
    weather. A colder-than-normal winter draws balances down further, and a milder one less.
- **Electricity is unchanged** (PC1 at benchmark). Only gas is in scope.
- **Resolution.** Monthly. The gas spot is a monthly proxy, so a daily join would not resolve the cold-day/price-day
  covariance anyway. That covariance is not tested here, and it is said to be untested.

## 3. Pass rule (unchanged in form)

The test passes iff, under the static reading, there is a band of F (on the grid) at both fixed shares in which
H_S5 > −F and every S1-S4 hole is below −F, with no S1-S4 hole smaller than S5's at any sweep point. The rolling
reading is reported and is not part of the verdict.

## 4. Predictions, written before the run

From prior knowledge only: the 2021-22 heating season in GB was generally mild (a mild December end and a mild,
stormy February). Nothing from the store has been read for it.

1. **Weather volume.** Oct-21 to Mar-22 gas volume falls within ±10% of normal, most likely *below* normal by 3-8%.
2. **Direction on each strategy, if the winter was mild.** S1 and S2 buy less gas at a spot above the allowance, so
   their holes shrink. Over-covered books (S3, the fixed books, S5) sell surplus cover back at a spot above what they
   paid, which is a gain. Balances drain less. **Every hole shrinks, and none deepens.**
3. **Size.** No strategy's H moves by more than 10% of the first test's static value at the same sweep point.
4. **The verdict passes.** There is a band at both fixed shares, with no inversions. The S3/S4 order at 0.75 stays as
   it was: S4 is shallower than Together-S3.
5. **Refutation.** If the winter reads *colder* than normal on the anomaly basis, prediction 2 flips: S1/S2 holes
   deepen and the S5 credit drawdown deepens. That alone would not fail the verdict. A failed verdict would mean the
   weather moved S5 past an S1-S4 hole, and I expect that to need a volume error far beyond ±10%.

## 5. What a pass would and would not mean (F11)

A pass with holes that barely move says that, in 2021-22, weather was a second-order force on the ranking next to
price. It does **not** say weather is second-order in general: a cold winter at a high spot is the case that would
press. Leavers within the year and SoLR inflow are still GAPs.
