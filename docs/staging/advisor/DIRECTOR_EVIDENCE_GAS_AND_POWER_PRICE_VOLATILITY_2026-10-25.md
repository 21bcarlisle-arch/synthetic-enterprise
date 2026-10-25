# Director evidence: gas and power price volatility

**Severity:** LATENT · **Lane:** W1_market_weather · **Epoch:** unassigned · **Atom:** `unminted`

## Why this is here

- 05:15 GMT: "Is there no way to use the spare tokens productively? On knowledge creation for example ? Or improving the website? Things that don't impact it's need to run tasks in series"

The advisor spent spare allowance outside your serial gate on research for the knowledge pages the map found missing. This file is one of seven cited evidence packs landed in one commit.

## What to do with it

- Turn it into a published Knowledge page under the map steer (DIRECTOR_STEER_THE_MAP_ONE_CONCEPT_REGISTER_FOUR_SPINES_AND_A_KNOWLEDGE_PLAN). Register its concepts in the concept register.
- The headline-bands table at the end gives candidate world claims for the knowledge-checks-the-world gate. Grade the simulated world against them and say where it falls outside.
- Items marked [derived] are arithmetic you can re-run. Items marked [unverified] are not claims until you source them.
- Each named gap is a research task. Close it, or record that nothing is published.
- This is drafting work. Do it without displacing the serial queue. The research cost has already been spent.
- This pack also feeds the forward-years volatility pass marks (DIRECTOR_STEER_FORWARD_YEARS_MUST_REPRODUCE_VOLATILITY_AT_EVERY_SCALE). Use its grading-bands table as the starting set of claims. Where it names a gap (backwardation share, half-lives, spread series), that gap is a data pull for you, not a reason to drop the claim.

---

# How GB gas and power prices move, 2016-2025: volatility by time scale, forward-curve shape and spark spreads

*Evidence pack for a GB energy-market simulation's knowledge layer. Compiled 25 Oct 2026. Every figure has a source URL next to it. Where I converted units or did arithmetic myself, it is marked "derived". Where a figure comes from memory and not from a fetched source, it is marked "unverified". Ofgem's Wholesale Market Indicators page does not expose its chart values as text. Direct API pulls from Elexon and Ofgem were blocked in this environment, so no time series were computed from raw data.*

---

## 1. NBP gas: levels, peaks, volatility

**Annual levels.** The only annual series I could retrieve was the Heren NBP index, in USD/MMBtu, now discontinued: 2016 4.69, 2017 5.81, 2018 8.06, 2019 4.47, 2020 3.42, 2021 15.80. There is no 2022-25 data in this series ([YCharts](https://ycharts.com/indicators/uk_heren_nbp_index_natural_gas_prices)). Before 2021, GB gas averaged £14.24/MWh. It peaked at £155.29/MWh on 22 Dec 2021 ([EnAppSys 2021 GB summary](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)). NBP averaged £27.26/MWh in Q3 2025, 3% lower year on year ([Montel Q3 2025](https://montel.energy/resources/reports/gb-electricity-market-summary-q3-2025)). That is about 80 p/th (derived).

**Peaks and records**
- **Beast from the East, 1 Mar 2018.** Day-ahead peaked at 279.5 p/th and settled at 229.75 p/th, its highest close ever. OTC within-day traded at 350 p/th, and National Grid issued a Gas Deficit Warning at 05:48 ([ICIS](https://www.icis.com/resources/news/2018/03/01/10198518/british-nbp-within-day-gas-breaks-the-300th-barrier/)). S&P reports 535 p/th paid on the OCM that day ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/070722-lack-of-baseload-drives-winter-2022-european-gas-to-new-lifetime-high)). Spot reached 11.2 p/kWh against an annual average of 1.5 p/kWh ([Electric Insights](https://reports.electricinsights.co.uk/?p=484)).
- **2021.** Front-month set a record of 116.10 p/th on 11 Aug 2021. The previous record was 111.50 p/th in 2005 ([Platts via Hellenic Shipping News](https://www.hellenicshippingnews.com/?p=881938)). Day-ahead traded briefly at 355 p/th on 6 Oct 2021 ([The Energyst](https://theenergyst.com/wholesale-gas-trades-at-record-355-pence-per-therm-as-heavy-users-urge-johnson-to-step-in/)).
- **2022.** The NBP front-month (prompt) contract peaked at 800 p/th on 7 Mar 2022. Summer 2022, as front season, was assessed at a record 479.90 p/th. Winter 2022 reached 443 p/th intraday on 7 Jul 2022 ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/070722-lack-of-baseload-drives-winter-2022-european-gas-to-new-lifetime-high)). Wholesale gas "reached 19p/kWh in August 2022 … and have been below 4p/kWh since spring 2023" ([House of Commons Library](https://commonslibrary.parliament.uk/research-briefings/cbp-9714/)). That is about 557 p/th and about 117 p/th (derived).
- **NBP–TTF basis blowout.** On 15 Jul 2022 there was "a $23.287/MMBtu spread between NBP and TTF" ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/071522-european-lng-sellers-look-away-from-uk-amid-wide-discounts)). GB had LNG it could not export at that point, so a simulator that hard-links NBP to TTF will miss episodes like this.

**Published volatility statistics**
- **Front-month volatility, 1997-2011** ([OIES NG60, Alterman 2012](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2012/02/NG_60.pdf)). This is monthly realised volatility of daily log returns on NBP front-month futures. The roll-adjusted series trends from about 8% to about 15% a month. Winter months (Nov–Mar) average 13.0%, against 9.9% for the rest of the year. Crisis spikes reached 37% in 2006. Annualised (×√12, derived), these are roughly 28-52%.
- **Risk premium.** UK forward prices are "biased predictors" of spot, and the risk premium is positive. Spot and forward prices are cointegrated, and storage affects the spot–forward link in a non-linear way ([Hobæk Haff et al. 2008, Energy Economics](https://ideas.repec.org/a/eee/eneeco/v30y2008i5p2420-2440.html)).
- **Premium by horizon.** The day-ahead premium averages about 0.5% per day. Accrued rollover premiums are about 4-20% annualised over 3-6 month horizons. "All risk premiums are larger and more volatile in winter" ([Int. Rev. Econ. & Finance 2018](https://ideas.repec.org/a/eee/reveco/v58y2018icp621-636.html)).
- **Mean reversion and fat tails.** Relevant papers exist: [Energy 2014, "Modeling natural gas price volatility: the case of the UK"](https://www.sciencedirect.com/science/article/abs/pii/S0360544214005659), [Energy Economics 2025, "Seasonality and spikes in the natural gas market"](https://www.sciencedirect.com/science/article/pii/S0140988325004104), and [jump processes in gas markets](https://www.sciencedirect.com/science/article/abs/pii/S0140988314002254). ScienceDirect blocked retrieval, so **no half-life or kurtosis figures are verified here.**
- **Realised volatility for 2021-22.** None was found in a fetchable primary source. Oxera's study for ICE charts 10-day annualised TTF volatility but does not give the values in text ([Oxera/ICE 2022](https://www.ice.com/publicdocs/Oxera_Study_into_the_Functioning_of_the_European_Gas_Market.pdf)). *Unverified recollection: TTF/NBP front-month realised volatility exceeded 100% annualised for parts of 2022.*

## 2. GB power: levels, volatility, negatives, spikes

**Annual day-ahead levels**
- **2015-16 and 2016-17.** Mean £38.63/MWh (daily standard deviation £5.91) in the year before the EU referendum. Mean £45.49 (standard deviation £12.74) in the year after. Conditional variance rose 51% ([UCL for Ofgem, Gissey et al. 2018](https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/report_ace_project_ucl_gissey_et_al_20181009_submitted_version_v3_0.pdf)).
- **2019.** The April-ahead forward baseload contract averaged €58.4/MWh, down 2.8% on 2018 ([EDF 2019 URD](https://edf.publispeak.com/2019-universal-registration-document/article/247)).
- **2020 and 2021.** Average day-ahead was £35.26 in 2020 and £118.29 in 2021, a rise of 235%. Super-peak (16:00–19:30) was £153.19 and off-peak £93.98 in 2021 ([EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)).
- **2022.** The price "centred on £200/MWh over the year", about five times the 2010-19 average. Over 2009-22 the highest annual average was £198.16 and the lowest £33.88 ([Electric Insights 2022](https://reports.electricinsights.co.uk/?p=1862); [Q4 2022 report](https://reports.electricinsights.co.uk/wp-content/uploads/2023/02/Drax_Electric_Insights_Report_2022_Q4.pdf)).
- **2023.** Q1 2023 averaged about £128 and Q1 2024 about £65 ([Solar Power Portal/Montel](https://www.solarpowerportal.co.uk/solar-projects/uk-power-prices-drop-by-50-yoy-in-q1-2024)). No full-year 2023 figure was verified.
- **2024.** EPEX GB day-ahead averaged £72.27 baseload and £81.38 peak ([EPEX annual results](https://www.epexspot.com/sites/default/files/download_center_files/2025-01-28_EPEX%20SPOT_Annual%20Power%20Trading%20Results%202024_finaldraft_0.pdf)).
- **2025.** £81.2, against £74.0 in 2024 ([Electricity Maps](https://www.electricitymaps.com/grid-in-review-2025/great-britain)).

**Intraday and daily shape.** In 2025 the average daily price swing (max minus min) was £68/MWh. The largest was £866/MWh on 22 Jan 2025, ranging from £92 to £958 ([Electricity Maps](https://www.electricitymaps.com/grid-in-review-2025/great-britain)).

**Spikes**
- **8 Jan 2021.** The system price hit £4,000/MWh. Between 2016 and 2020, 62% of system prices above £500 occurred in autumn and 0% in summer ([Elexon](https://www.elexon.co.uk/bsc/article/bsc-insight-unprecedented-price-spikes-in-2021/)).
- **September 2021.** On 9 Sep the system price was £4,037.80/MWh, and £38m of balancing actions made it the most expensive day on record. Day-ahead cleared at £867 on 9 Sep and £2,500 on 15 Sep on Nord Pool ([LCP](https://www.lcp.com/en/insights/blogs/what-is-causing-the-record-prices-in-the-gb-power-market); [Elexon](https://www.elexon.co.uk/bsc/article/system-prices-spike-on-7-september-2021/)). The £2,500.01 print was "a 614% rise on the previous record of £350.00/MWh" ([EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)).
- **2021 system prices overall.** The average was £113/MWh, the highest since 2001, and 33 settlement periods exceeded £1,000 ([Elexon](https://www.elexon.co.uk/article/bsc-insights-why-did-the-average-system-price-increase-in-2021/)).
- **23 Aug 2022.** The daily average day-ahead price was a record £539.59/MWh ([Energy Live News](http://www.energylivenews.com/2022/08/23/uk-day-ahead-energy-prices-smash-new-records/)).
- **22 Jan 2025.** The hourly maximum was £958.5/MWh ([Electricity Maps](https://www.electricitymaps.com/grid-in-review-2025/great-britain)).

**Negative prices**
- The first-ever negative GB day-ahead price was −£2.84/MWh on 9 Dec 2019, with wind at 16.2 GW ([Cornwall Insight via Electrical Review](https://electricalreview.co.uk/2019/12/18/cornwall-insight-comments-on-negative-wholesale-prices)).
- Negative hours by year, using Aurora and Modo figures ([ESS News](https://www.ess-news.com/2025/01/03/britains-six-fold-increase-in-negative-prices-an-opportunity-for-big-batteries-analyst/)):

| Year | Aurora | Modo |
|---|---|---|
| 2022 | 19 | 29 |
| 2023 | 86 | 107 |
| 2024 | 139 | 149 (to Sep) |

- NextEnergy Capital also counts 107 negative one-hour day-ahead periods in 2023 (N2EX basis) ([NextEnergy Capital](https://www.nextenergysolarfund.com/wp-content/uploads/2024/09/NextEnergy-Capital-Insights-Negative-Power-Prices-GB-Wholesale-Energy-Market-Sept-2024.pdf)).
- 2025 had 190 negative hours across 33 days, with a minimum of −£30.5 ([Electricity Maps](https://www.electricitymaps.com/grid-in-review-2025/great-britain)). The longest run was 17 consecutive hours on 25 May 2025, equalling 16 Jul 2023, when the price reached −£54.17 ([Argus](https://www.argusmedia.com/en/news-and-insights/latest-market-news/2692698-uk-n2ex-hits-record-negative-hour-streak)).

## 3. Forward-curve shape

- **2021 rally.** The Winter-21 contract opened at 55 p/th and expired at 236.30 p/th, a 330% rise. After early July 2021, day-ahead "consistently trad[ed] above" front-quarter forwards ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/101521-winter-gas-up-four-fold-during-summer-spot-in-three-fold-return)). Spot above forward points to backwardation, but S&P does not use that label.
- **Seasonal spread collapse.** The NBP Winter-vs-day-ahead spread averaged about 50 p/th in Q2 2023 and about 19 p/th in Q2 2024. Centrica called its Rough storage outlook "challenging given low seasonal spreads" ([S&P Global](https://www.spglobal.com/energy/en/news-research/latest-news/natural-gas/072524-uks-centrica-sees-challenging-outlook-for-gas-storage-business-on-low-spreads)).
- **Inverted spread, Feb 2025.** On 3 Feb 2025, NBP Summer-25 was 128.53 p/th and Winter-25 was 120.60 p/th, so summer traded about 7.9 p/th above winter (derived). TTF summer–winter was "just above €6/MWh" ([MNI](https://www.mnimarkets.com/articles/ttf-and-nbp-maintain-summer-premium-over-winter-1738586980995)).
- **Return to normal shape, Apr 2025.** As front-month TTF fell from €58 to about €33, "the steep backwardation observed in February has flipped into contango", which restored the usual pattern of summer cheaper than winter ([Timera](https://timera-energy.com/blog/seasonal-pricing-shape-returns-to-ttf-forward-curve/)).
- **Slope versus spot level.** The episodes above share one pattern: when spot is high or rising, the curve is backwardated and the seasonal spread is compressed or inverted. When spot falls, the curve returns to contango. This is qualitative only. **No study measuring the share of days in backwardation for NBP or GB power was found.**
- **Ofgem's NBP chart.** Ofgem publishes an "NBP summer-winter spreads" indicator, but its values are not available as text ([Ofgem WMI](https://ofgem.gov.uk/node/171239)).

## 4. Clean spark and dark spreads

- **Conventions.** The UK market uses 49.13% as a standard CCGT efficiency: "Spark Spread = Power Price – (Gas cost/0.4913)". For the clean spark spread, subtract carbon × 0.411 t/MWh. Dark spreads assume 35% efficiency and 0.971 t/MWh ([Wikipedia: Spark spread](https://en.wikipedia.org/wiki/Spark_spread), a secondary source). Electric Insights gives gas generation as about 1 t CO₂ per 2.5 MWh ([Electric Insights](https://reports.electricinsights.co.uk/?p=2567)).
- **Carbon.** Carbon Price Support is £18/t on top of the ETS price. The UK ETS's first auction was on 19 May 2021. The UK ETS hit about £35/t in Oct 2023, the lowest since it began, and was 28% cheaper than the EU even including CPS ([Modo](https://modoenergy.com/research/carbon-prices-falling-polluting-uk)). GB gas plants paid about £65/t in H1 2021, against €44 on the continent, and £62/t in H1 2025, against €73. From 2024 the UK price sat about £18/t below the EU. The 2025 carbon rally added about £8/MWh to gas-generation costs over the nine months to September 2025 ([Electric Insights](https://reports.electricinsights.co.uk/?p=2567)).
- **Spread levels** ([Timera, Jan 2023](https://timera-energy.com/blog/gb-clean-spark-spreads-fall-ma-2023/)):

| Period | Baseload CSS | Peak CSS |
|---|---|---|
| Before 2021 (benchmark) | not given | about £4-10/MWh |
| 2022 high, month-ahead | about £280/MWh | about £610/MWh |
| Late Jan 2023, month-ahead | £16/MWh | £46/MWh |

  Timera adds that "Baseload CSS forward prices are structurally negative from summer 2026 onwards".
- **Coal–gas switching.** In Q4 2021 the least efficient coal units (30%) had lower breakeven costs than the most efficient CCGTs (55%), so coal was cheaper to run than gas ([EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)).
- **Marginal price-setter.** Gas set the price 65.4% of the time in 2017 ([UCL](https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/report_ace_project_ucl_gissey_et_al_20181009_submitted_version_v3_0.pdf)) and about 85% of the time in 2024 ([ECIU](https://eciu.net/analysis/reports/2025/marginal-gains-how-wind-is-pushing-gas-out-of-the-power-market-and-cutting-costs)).

## 5. Weather–price links

- **Low wind and spikes.** In the 2021 spike periods (system price above £500), wind averaged 1.1 GWh per settlement period, against 3.4 GWh in other periods. Gas units supplied 91% of the accepted offer volume ([Elexon](https://www.elexon.co.uk/bsc/article/bsc-insight-unprecedented-price-spikes-in-2021/)). In early September 2021, 50% of periods had wind below 15% of the annual maximum ([LCP](https://www.lcp.com/en/insights/blogs/what-is-causing-the-record-prices-in-the-gb-power-market)). Annual wind output was 62.4 TWh in 2021, against 68.3 TWh in 2020 ([EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)).
- **High wind and negatives.** Negative system-price periods averaged 13.8 GW of wind and 21.3 GW of demand ([EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)).
- **Wind's level effect.** In 2024, wind may have cut day-ahead prices by up to 25%, about £24-25/MWh. The modelled counterfactual without wind is £96-101/MWh, against an actual £73-76/MWh ([ECIU](https://eciu.net/analysis/reports/2025/marginal-gains-how-wind-is-pushing-gas-out-of-the-power-market-and-cutting-costs)).
- **Cold snaps.** On 1 Mar 2018 gas demand hit 4,600 GWh/day, the highest since 2010. Storage was at its lowest since 2010, and coal displaced gas in power generation ([Electric Insights](https://reports.electricinsights.co.uk/?p=484)).
- **Gas–power correlation.** No GB daily gas–power correlation coefficient was retrieved. In the ECB's data, the wholesale-to-consumer gas price correlation rose from 0.36 (2005-21) to 0.92 in H2 2021 ([ECB EB 3/2022](https://www.ecb.europa.eu/pub/economic-bulletin/focus/2022/html/ecb.ebbox202203_05%7E6d1fb8f5b0.en.html)), but that is euro-area retail, not GB.

## 6. Forecast error growth

- Forward and futures prices are biased predictors of NBP spot. The bias is a positive premium that grows with horizon and is larger in winter ([Haff et al.](https://ideas.repec.org/a/eee/eneeco/v30y2008i5p2420-2440.html); [IREF 2018](https://ideas.repec.org/a/eee/reveco/v58y2018icp621-636.html)).
- Since mid-2021, "gas futures failed to anticipate large price increases" ([European Commission, Autumn 2022](https://ec.europa.eu/economy_finance/forecasts/2022/autumn/TB%20-%20Futures%20prices%20in%20forecast%20assumptions.pdf)).
- In ECB staff projections, energy-assumption errors added 1.6 pp to the one-quarter-ahead inflation error in Q1 2022, against about 0.2 pp before COVID. The surge was "largely unanticipated by market participants" ([ECB](https://www.ecb.europa.eu/pub/economic-bulletin/focus/2022/html/ecb.ebbox202203_05%7E6d1fb8f5b0.en.html)).
- **No published RMSE-by-horizon for NBP or GB power forwards against outturn was found.**

---

## Grading bands for a simulated price generator

"Evidence" means the band comes straight from the cited figures. "Proposed" means it is my inference from those figures, and the derivation is given.

| Measure | Band | Basis |
|---|---|---|
| NBP front-month monthly realised vol, normal regime | 8-15% (about 28-52% annualised) | Evidence for 1997-2011 ([OIES](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2012/02/NG_60.pdf)); proposed for 2016-20 |
| Winter-to-summer volatility ratio (NBP) | about 1.3 (13.0% / 9.9%) | Evidence ([OIES](https://www.oxfordenergy.org/wpcms/wp-content/uploads/2012/02/NG_60.pdf)) |
| NBP crisis peak to pre-crisis average | about 10-25× (front-month 800 p/th; derived) | Proposed; pre-crisis baseline unverified |
| GB day-ahead annual mean, normal regime | £35-46/MWh (2015-20) | Evidence ([UCL](https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/report_ace_project_ucl_gissey_et_al_20181009_submitted_version_v3_0.pdf); [EnAppSys](https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf)) |
| GB day-ahead annual mean, crisis regime | £118 (2021) to about £200 (2022) | Evidence |
| GB day-ahead annual mean, post-crisis | £72-81/MWh (2024-25) | Evidence |
| Daily standard deviation of day-ahead, normal | £6-13/MWh | Evidence ([UCL](https://www.ofgem.gov.uk/sites/default/files/docs/2018/10/report_ace_project_ucl_gissey_et_al_20181009_submitted_version_v3_0.pdf)) |
| Mean daily max–min swing, 2025 | about £68/MWh | Evidence ([Electricity Maps](https://www.electricitymaps.com/grid-in-review-2025/great-britain)) |
| Negative day-ahead hours per year | 0 (≤2018); 19-29 (2022); 86-107 (2023); 139-149 (2024); about 190 (2025) | Evidence |
| Maximum hourly day-ahead price, non-crisis year | £490-960/MWh (2024-25) | Evidence |
| Annual count of system prices above £500 | 31 in 2016 (highest year 2016-20); 24 in 2021 up to 12 Apr | Evidence ([Elexon](https://www.elexon.co.uk/bsc/article/bsc-insight-unprecedented-price-spikes-in-2021/)) |
| Seasonal timing of system prices above £500 | autumn > spring > winter; summer ≈ 0 | Evidence (2016-20) |
| Peak clean spark spread, normal regime | £4-10/MWh | Evidence ([Timera](https://timera-energy.com/blog/gb-clean-spark-spreads-fall-ma-2023/)) |
| Month-ahead clean spark spread, crisis maximum | baseload about £280, peak about £610/MWh | Evidence |
| NBP Winter-minus-spot spread, Q2 | 19-50 p/th (2023-24); can invert (Feb 2025) | Evidence |
| Share of days in backwardation | No data | Gap |
| Gas share of hours setting the marginal price | 65% (2017) to 85% (2024) | Evidence |

## Named gaps

1. NBP realised volatility for 2016-2025 by year, daily or annualised, including the 2021-22 regime. Needs ICE settlement data or Ofgem WMI downloads.
2. Mean-reversion half-lives and jump or kurtosis estimates for NBP and GB power. The papers exist but are paywalled.
3. Official annual GB day-ahead baseload and peak series for 2016-2019 and 2022-2023. Needs N2EX/EPEX or Elexon MID data, which was blocked here.
4. Share of days with NBP and GB power forward curves in backwardation, and a regression of curve slope on spot level.
5. Clean spark and dark spreads by year for 2016-2025 on the 49.13% convention, including the share of negative days. Ofgem's values are chart-only.
6. A GB daily gas–power correlation, and a price-per-GW-of-wind elasticity.
7. RMSE of NBP and GB power forwards against outturn by horizon.
8. NBP annual averages for 2022-2025 in p/th from a primary source.