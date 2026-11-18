**Severity:** RECORDED · **Lane:** W3_industry_systems · **Epoch:** unassigned · **Atom:** `unminted`
**Knowledge:** suppliers-accounts-and-capital -- `docs/market_research/why_gb_suppliers_failed_or_survived_2021_22.md`

# Pre-registration, third test: the 2021-22 cash hole with daily gas price against daily gas volume (2026-11-18)

*Delivery seat, claim `world-ranks-2021-22-gas-shape-on-a-daily-price`. Written BEFORE the instrument has been run
at daily resolution. It follows the second test
(`SEAT_RESULT_THE_2021_22_CASH_HOLE_RANKING_UNDER_THE_WORLDS_OWN_WEATHER_2026-11-18.md`), which found that weather
moves every strategy by about the same +£48 at monthly resolution, and named shape (cold days on price spikes) as the
one weather mechanism that might separate the strategies.*

## 1. The question

Does within-month gas shape, meaning daily volume from the world's weather against a daily GB gas price, separate a
well-hedged 2021-22 book from a badly hedged one? And does the verdict still hold when the gas spot is a real GB
day-ahead series instead of the monthly TTF proxy?

## 2. What changes, and nothing else

- **The price.** This is a new world record, `sim/gas_data/sap_daily.csv`: National Gas Transmission's System
  Average Price, actual day, as republished by ONS under OGL v3 (edition of 12 Nov 2026, sha256 pinned in
  `sim.gas_prices_history`). It runs 2018-01-01 to 2025-12-31 with no missing days. The cap's uplift `k` is applied
  to it exactly as it is to the monthly proxy.
- **The volume.** Daily HDD comes from the world's store through `WeatherWorld.for_cell`: each cell's daily HDD
  averaged with equal weight, the same reader as `world_monthly_hdd`, kept per day. Under `anomaly` each day's HDD is
  scaled by the month's factor `REFERENCE_MONTHLY_HDD[m] / mean_2016-2025(world HDD for month m)`. Under `level` it is
  used as it stands. Under `normal` it is flat at `REFERENCE_MONTHLY_HDD[m] / n`. In every case the daily volumes sum
  to the second test's monthly volume. `resi_daily_gas_kwh` is linear in HDD, so this holds exactly.
- **The plan and the cover.** Both are unchanged: cover is sized on normal-weather monthly volume and delivered
  baseload, which means flat across the days of the month, like the forward basket it is bought from. Each day's gap,
  need minus cover, is bought or sold at that day's SAP.
- Revenue, the credit-balance path, electricity, the strategies, the sweep (fixed shares 0.5 and 0.75, credit £65)
  and the pass rule (§4.1 of the first pre-registration) are all unchanged.

Three gas price modes are run so that the two changes can be told apart:
`ttf_monthly` (the second test, reproduced), `sap_monthly` (SAP monthly mean against monthly volume), and `sap_daily`
(SAP daily against daily volume). **Price-source effect** = `sap_monthly − ttf_monthly`. **Shape effect** =
`sap_daily − sap_monthly`.

## 3. Predictions, written before the run

1. **Shape cannot separate the strategies in this instrument (derived, exact).** The cash flow is linear in the
   daily gap, and cover is flat within the month. The shape effect is therefore
   Σ_d (need_d − mean need)(p_d − mean p) on the volume on supply. That volume depends on the fixed share and on the
   SVT survival curve, not on the hedge. **At each fixed share and weather reading, the shape effect will be the same
   for S1 to S5 to within £0.01.** A difference larger than that refutes the derivation, or shows the instrument
   is not doing what I think it does.
2. **The shape effect is exactly zero at `normal` weather**, because daily need is then flat. This is a control
   rather than a finding.
3. **Under `anomaly` and `level`, the shape effect is a small cost**: negative, between −£0.50 and −£15 per opening
   customer over Jul-21 to Mar-22. The reasoning is that cold days drew on the system and lifted the day-ahead price.
   I hold this weakly. The window was mild, and 1 Jan 2022 was both record-warm and a SAP collapse (£15/MWh), which is
   positive covariance. Refuted if the effect is positive (a gain) or larger than £15.
4. **The price-source effect does move the strategies apart, but does not reverse the verdict.** It acts on the
   unhedged volume, so S1 moves most and S5 least. Prediction: `sap_daily` under `anomaly` and `static` still
   passes, S5's hole stays at or below £25, and the band is at least £150 wide. Refuted if the verdict fails or any
   S1-S4 hole is shallower than S5's.

## 4. What a pass or a refutation would mean

If 1 holds, the second test's question ("can weather shape separate the strategies?") gets a structural answer: **not
while every disclosed strategy holds baseload cover.** Shape is then a cost every supplier bears in proportion to the
volume it has on supply, whatever its hedge. What separates suppliers is the price level on unhedged volume, which the
monthly test already measures. For the world to show shape separating suppliers, a strategy would need a SHAPED
position, such as a winter-weighted profile, storage or a weather derivative, and none of the five has a published
one. If 1 fails, the instrument has a non-linearity I have not seen, and that has to be found before anything is read
off the numbers.
