# How the GB electricity price forms, driver by driver, 2016-2025

**Knowledge:** electricity-wholesale

The K8 page the director asked for on 24 Nov 2026 (05:40 addendum to the signed steer `452de5285`, item
2): "merit order: gas SRMC with carbon (CPS plus UK/EU ETS), CfD/RO and negative prices, nuclear,
interconnectors by year (FR, BE, NL, NO, DK, IE) including the 2022 exports, the Capacity Market,
scarcity and the BM, and weather-driven demand. Mechanism, not only numbers." It follows the gas page
(`how_the_gb_gas_price_forms_nbp_and_sap_2026-11-24.md`) and does not repeat it. Two older pages hold
other parts of the subject. `how_gb_gas_and_power_prices_move_2026-10-25.md` holds how much the price
MOVES. `ssp_multiplant_srmc_stack_heat_rates_2026-07-25.md` holds the plant-level cost inputs. This
page holds WHY the price is what it is: each driver, how it reaches the price, its size, and its GAPs.

Written by the delivery seat, 2026-11-24. **Sources** are named at each claim. Most volumes are from
DESNZ, *Digest of UK Energy Statistics 2026*, chapter 5: Table 5.1 (generation), 5.1.2 and 5.13
(interconnectors), 5.10.C (efficiency). These were read from the published workbooks. "[calc]" marks
arithmetic on published figures. "[press]" marks trade or analyst sources (Modo Energy, Montel,
Electricity Maps, Drax), read through their pages or search results: a direction and an order of
size, not a series. "[not re-read]" marks a fact this page states from established market knowledge
whose primary text was not re-read in this session. Each one is a GAP to check, not a citation.

## 0. Which price, said before it is measured

GB electricity has no single "wholesale price". There are four, and the world uses only one of them.

- **Forward and futures** (seasons, quarters, months, ahead). Suppliers buy most of their energy here,
  through brokers or exchange. Ofgem's cap indexes a 12-month forward window.
- **Day-ahead auctions** (EPEX and N2EX hourly, and EPEX half-hourly). This is the reference price that
  CfD baseload and intermittent strike prices settle against, and the price press "hourly negative
  price" counts use.
- **Within-day continuous trading.** Elexon's **Market Index Data (MID)** is the volume-weighted price
  of short-term exchange trades for each settlement period, as reported by APX/EPEX and N2EX. It is
  the nearest published half-hourly measure of where electricity actually TRADED.
- **The imbalance (cash-out) price.** After gate closure only NESO acts, in the Balancing Mechanism
  (BM). A party whose metered position differs from its contracted one is cashed out at the **System
  Price**. Since BSC Modification P305 (5 Nov 2015) the Sell and Buy prices have been one price (Elexon,
  P305). It is built from the most expensive 1 MWh of energy balancing actions (the Price Average
  Reference volume). PAR fell from 50 MWh to 1 MWh on 1 Nov 2018, when VoLL rose from £3,000 to
  £6,000/MWh (Elexon, *System Price Analysis*). Reserve scarcity pricing applies for STOR actions.

**The world settles everything at the System Sell Price (SSP).** The record is the half-hourly SSP
replay (`sim/cache/elexon_ssp_full.json`, 2015-11-07 to 2025-06-07). The forward-year chain
(`sim/weather_price_chain.py` over `sim/price_engine.py`) is calibrated to SSP. SSP is a real
published price, but it is not the price a supplier's hedged energy cost. A supplier pays it only on
its imbalance. `sim/market_index_history.py` records this, and it is graded in §10.

## 1. The merit order: the price is the running cost of the last plant needed

- **Mechanism.** Under NETA/BETTA, generators self-dispatch against contracts and the exchanges. In
  each period the clearing price is near the short-run marginal cost (SRMC) of the dearest unit that
  must run to meet demand. What decides which unit is marginal is **residual demand**: demand less wind,
  solar, nuclear and other must-run output. Every unit cheaper than the marginal one earns the same
  price.
- **Gas SRMC.** SRMC = gas price ÷ efficiency + carbon cost ÷ efficiency + variable O&M. The GB CCGT
  fleet's average efficiency is 48.4-49.9% on a gross-CV (HHV) basis, every year 2016-2024 (DUKES
  5.10.C). The best new H-class plant is about 60% on an LHV basis (DESNZ/GHD, *Unabated gas
  electricity generation costs 2025*). The two figures are on different bases. Gas emits 0.1829
  tCO2 per MWh of gas burned, gross CV (DESNZ conversion factors 2024). So a £1/MWh move in gas moves
  fleet SRMC by about £2.04/MWh [calc, 1/0.49]. The marginal plant is often older and less efficient
  than the fleet average, so the real slope at the margin is steeper. Its size is a GAP.
- **How often gas sets the price.** Gas was marginal in about 85% of hours in 2024, down from close to
  90% in 2018 (ECIU, *Marginal Gains*, 2025; already checked on our live page). That is why GB power
  is, most of the time, a gas price in different units.
- **What is above and below gas.** Below gas: wind, solar, nuclear, run-of-river, and biomass on
  support. Biomass bids its fuel cost less its subsidy, and must-run CHP runs to its heat load. Above
  gas: OCGTs and reciprocating engines, pumped storage and batteries pricing their opportunity cost,
  and coal until it closed. Coal went from 22.4% of generation in 2015 to 9.0% in 2016 after the
  carbon price floor rose. It was 0.7% in 2024 and 0% from 1 Oct 2024, when Ratcliffe closed
  (`ssp_dispatchable_fleet_renewables_era_boundaries_2026-07-24.md`, from DUKES).
- **GAP.** No published series of the marginal technology by hour has been read beyond ECIU's annual
  shares. No published efficiency of the marginal (rather than average) CCGT is held.

## 2. Carbon: Carbon Price Support plus the traded allowance

- **Carbon Price Support (CPS).** This is a UK tax on fossil fuel burned for power, on top of the
  allowance price. It has been capped at £18/tCO2 from 2016-17, a cap announced at Budget 2014 [press,
  The Conversation] and in the Budget 2016 policy costings (HMT). It was held for each year since and
  extended to 2027-28 [press, Osborne Clarke]. The 2013-14 to 2015-16 rates were not found in a
  primary source (GAP). The rise to the April 2015 rate is what pushed coal off the margin (§1).
- **The traded allowance.** Until 2020 this was the EU ETS. The EEX auction VWAP was €5.26 (2016),
  €5.79 (2017), €15.34 (2018), €24.65 (2019) and €24.51 (2020), or about £4.3, £5.1, £13.6, £21.6 and
  £21.8 at ECB annual FX [calc] (`eu_uk_ets_carbon_price_series_2026-08-03.md`). From 2021 it is the
  UK ETS. Its 2021 auction average was £47.96. For 2022-2024 the only held figures are the statutory
  civil-penalty prices, which are futures averages traded the year before. Taking each in the year it
  was traded gives about £83 in 2022, £65 in 2023 and £42 in 2024 [calc on the gov.uk determinations].
- **Size at the margin [calc, fleet efficiency, EF 0.1829].** Carbon added about £8.5/MWh to CCGT SRMC
  in 2017, £14.9 in 2019, £24.6 in 2021 and £37.6 in 2022. Carbon is not a small term next to the gas
  term in any year.
- **How it reaches price.** One for one through the marginal plant's SRMC, in the hours gas or coal is
  marginal. Through the margin it also moves the order: a higher carbon price moved coal behind gas.
- **Correction to the record.** `sim/merit_order_reconstruction.py` prices CPS but sets the allowance
  to 0.0 as a named gap (2026-08-03 page). The weather-to-price chain's pre-crisis bias of −£12/MWh
  (`WORKER_RESULT_THE_WEATHER_TO_PRICE_CHAIN_LOSES_...`) is the size the allowance alone would leave in
  2019-20 (£11-12 at 2019-20 prices [calc]). That is consistent with missing carbon, but this page does
  not attribute it. Item 3 of the steer does that, with its prediction filed first.
- **GAP.** No daily or monthly UKA market series is held. The civil-penalty price is not the market
  price.

## 3. CfD, RO and negative prices

- **Renewables Obligation (RO).** RO plant earns Renewables Obligation Certificates per MWh generated.
  The buy-out price was £44.77 per ROC in 2016-17 and £52.88 in 2022-23 (Ofgem), and banded technologies
  earn more than one ROC per MWh. ROC income comes with generation and does not depend on the power price
  [inference from the issuing rule; no source states it in these words]. So RO plant will keep running
  at a negative power price until the price is below minus its ROC value. That is what lets the
  clearing price go below zero.
- **Contracts for Difference (CfD).** A CfD generator sells into the market and receives (strike −
  reference price), or pays it when the reference is above the strike. Intermittent CfDs reference the
  day-ahead hourly price. Per Modo Energy [press]: AR1 CfDs keep the difference payment in negative
  hours. AR2 and AR3 lose it only after six consecutive negative hours. From AR4, no difference is paid
  in any negative hour. The primary text (the CfD Standard Terms) has not been read (GAP). So older CfD
  plant also bids below zero, and newer plant has a reason to stop at zero.
- **When reference is above strike, generators pay.** In late 2021 and 2022 the reference price was
  above most strikes, and CfD generators paid LCCC, which refunds suppliers (Ofgem, *Decision on the CfD
  allowance methodology*, June 2022). About £205m was paid back from September 2021 to March 2022, and
  £108.3m was returned to suppliers by a June 2022 parliamentary answer [press, low confidence].
- **Correction to the steer's wording.** Item 5 of the finding says "the negative 2022 rate". **The
  Interim Levy Rate cannot be set below £0/MWh** under the CfD regulations (Ofgem, same decision). LCCC
  forecast negative supplier payments for cap period nine, which "would imply a negative ILR", and Ofgem
  replaced the ILR in the cap's allowance with an expected levy payment that can be negative. An
  endogenous CfD levy in the world must therefore produce a negative NET payment through reconciliation,
  not a negative ILR.
- **Negative prices.** The first negative N2EX/EPEX day-ahead hour was on 9 Dec 2019 (Argus). Negative
  day-ahead hours were 29 in 2022, 107 in 2023 and 149 in 2024 (Modo), or 139 in 2024 and 149 in 2025
  (Montel, EPEX), or 141 and 190 (Electricity Maps) [press; counts differ by auction]. The mechanism
  needs low demand, high wind and solar, and must-run plant with income outside the price (RO, early
  CfDs, nuclear, CHP) to coincide. The imbalance price goes negative far more often, because BM bids
  to turn wind down are priced below zero (graded in §10).
- **GAP.** No published hourly negative-price series for 2016-2021. No published ROC-adjusted bid
  curve.

## 4. Nuclear: baseload that left

- **Size.** UK nuclear generation was 71.7 TWh (2016), 65.1 (2018), 50.2 (2020), 46.1 (2021),
  47.4 (2022), 40.6 (2023), 40.6 (2024) and 35.9 (2025) (DUKES 5.1). Output halved over the decade
  [calc].
- **Closures.** Dungeness B (2021) [not re-read], Hunterston B (generation ended 7 Jan 2022),
  Hinkley Point B (reactor 2 shut 6 Jul 2022; retirement announced 1 Aug 2022) [WNN, press]. EDF's
  2025 fleet update runs Heysham 1 and Hartlepool to March 2028 and Torness and Heysham 2 to March
  2030. A July 2026 report moves the first pair to 2030 [unconfirmed search result].
- **Mechanism.** Nuclear runs at near-zero marginal cost and does not follow price. Each TWh it loses
  is mostly made up by gas, so it raises the number of hours gas is marginal, and the price level.
  Outages also matter: AGR graphite inspections and boiler issues took units out for months.
- **How it reaches price.** Through residual demand. The 2022 French nuclear outages reached GB
  through the interconnectors (§5).
- **GAP.** No unit-level availability series has been read. FUELHH nuclear (transmission-metered) is
  graded against DUKES in §10.

## 5. Interconnectors by year: capacity, flow and coupling

- **Capacity** (DUKES 5.13A, MW, year commissioned): IFA (France) 2,000, 1986; Moyle (Northern Ireland)
  500, 2001; BritNed (Netherlands) 1,000, 2011; EWIC (Ireland) 500, 2012; Nemo Link (Belgium) 1,000,
  2019; IFA2 (France) 1,000, 2021; North Sea Link (Norway) 1,400, 2021; ElecLink (France) 1,000, 2022;
  Viking Link (Denmark) 1,400, commissioned 29 Dec 2023 (Energinet), ramping from about 800 MW;
  Greenlink (Ireland) 500, 2025. That is 5.0 GW at the start of 2019 and 10.3 GW by the end of 2023
  [calc].
- **Net imports** (DUKES 5.13, TWh, UK basis, + is import): 2016 17.7; 2017 14.8; 2018 19.1; 2019 21.2;
  2020 17.9; 2021 24.6; **2022 −5.3**; 2023 23.8; 2024 33.4; 2025 29.7. From France: 9.7, 7.2, 12.9,
  11.1, 8.7, 13.7, **−10.0**, 12.9, 19.5, 21.9.
- **The 2022 exports.** 2022 is the only net-export year in the series. DUKES 2026 chapter 5 says exports
  "were unusually high due to widespread outages in the French nuclear fleet". France's prices rose above
  GB's for most of 2022. GB gas was cheap against TTF that summer (gas page §5), so GB CCGTs ran to
  export power to France. GB power was being priced from GB gas, and France was being priced from
  scarcity.
- **Mechanism.** Flow goes from the cheaper market to the dearer one, up to the link's capacity, and
  each link narrows the gap between the two prices. Norway (hydro) and France (nuclear) are usually
  cheaper, so GB imports. Ireland is usually dearer, so GB exports to it. When a link is full, the two
  prices separate.
- **Coupling after 2020.** Until 31 Dec 2020 GB's day-ahead market was implicitly coupled with the
  EU's single day-ahead coupling, so interconnector flows were scheduled in the same auction as
  prices. Since 1 Jan 2021 capacity has been sold in separate explicit auctions, and flows are
  nominated by traders ahead of the price [not re-read: the Trade and Cooperation Agreement's
  electricity provisions and Ofgem's guidance are the primary texts]. Explicit allocation leaves more
  hours with flow running against the price spread. Its size is a GAP.
- **How it reaches price.** Imports act as cheap supply in the merit order, and push gas off the margin
  in some hours. Exports act as extra demand. Through the links GB's price is pulled towards the
  continent's, and the continent's price is mostly set by gas and carbon too, but at TTF and the EU ETS.
- **GAP.** No hourly cross-border price-spread series is held. Interconnector flows by direction are
  held only as FUELHH (graded in §10).

## 6. Wind and solar: what moves residual demand

- **Size.** Renewables were 24.5% of generation in 2016 and 50.4% in 2024 (DUKES via the 2026-07-24
  fleet page).
- **Mechanism.** Wind output follows the cube of wind speed between cut-in and rated speed. A windy
  day pushes residual demand down the stack, often below the gas units, and a still day pushes it up.
  Two days with the same demand can have very different prices. In 2025, hours with gas below 20% of
  the mix averaged about £60/MWh, against about £130 where gas was above 50% (ECIU). In 2024, wind
  lowered day-ahead prices by up to about £24-25/MWh against a modelled £96-101 without it (ECIU, via
  the 2026-10-25 page §5).
- **How it reaches price.** Through which unit is marginal, not a fixed £ per GW. While gas stays
  marginal, more wind barely moves the price. When wind pushes gas off the margin, the price falls to
  the next plant's bid, which may be below zero (§3).
- **GAP.** No published price-response curve by residual demand band for GB has been read.

## 7. Capacity Market, scarcity and the Balancing Mechanism

- **Capacity Market (CM).** CM pays firm capacity £/kW-year to be available, through auctions four
  years (T-4) and one year (T-1) ahead. Suppliers pay for it through a levy. T-4 clearing prices
  (EMRS, CPI-adjusted table, £/kW-yr): 2018/19 £19.40; 2019/20 £18.00; 2020/21 £22.50; 2021/22 £8.40;
  2022/23 no T-4 (the 2019 T-3 cleared at £6.44); 2023/24 £15.97; 2024/25 £18.00; 2025/26 £30.59;
  2026/27 £63.00; 2027/28 about £65 and 2028/29 about £60 [press, Drax and Montel]. The levy on
  suppliers was £1.10/MWh in 2017/18 and £3.37-5.86 in 2018/19-2022/23
  (`capacity_market_levy_2016_2024.md`). The scheme was suspended from November 2018 to late 2019 after
  the EU General Court judgment [not re-read].
- **Mechanism.** The CM pays for capacity that the energy price alone would not, the "missing money".
  Peaking plant then does not need to recover its fixed costs from rare scarcity prices. It keeps plant
  on the system, and so it lowers how often and how far the energy price spikes. It is a cost to
  suppliers per MWh that does not move with the wholesale price.
- **Scarcity.** When the margin is thin, the BM's most expensive actions set the System Price.
  Reserve scarcity pricing and VoLL (£6,000/MWh since Nov 2018) are the ceiling for those actions. The
  System Price reached £4,000 on 8 Jan 2021 and £4,037.80 on 9 Sep 2021 (Elexon, via the 2026-10-25
  page). Day-ahead reached £2,500.01 on 15 Sep 2021. Over 2015-2020 the System Price was above £500 in
  50 periods, 62% of them in autumn and none in summer (Elexon).
- **The BM and cash-out.** NESO buys offers and bids after gate closure, to balance and to manage
  transmission constraints. A constraint (for example Scottish wind that cannot reach English demand)
  is paid off in the BM and reaches suppliers through BSUoS, not through the energy price. A national
  price hides it (`regional_supply_cost_under_one_national_price_2026-10-25.md`). The imbalance price
  is the marginal energy action's price, so it carries spikes and negative bids that the traded price
  does not.
- **GAP.** No published series of the de-rated margin against price, and no BM bid-offer stack, has
  been read.

## 8. Weather-driven demand

- **Mechanism.** GB transmission demand peaks on cold, dark winter weekday evenings. Electric heating
  is still a small share, so the temperature response is weaker than gas's, and it grows as heat pumps
  spread. Cold weather also raises gas demand, and so the gas price (gas page §6). A cold, still spell
  therefore raises the power price three ways at once: more demand, less wind, and dearer gas. On the
  record, cold-and-still days were priced 1.78-1.99 times a typical day across the three regimes
  (chain grade).
- **How it reaches price.** Through residual demand and the convex top of the stack, plus the gas
  price. Summer demand is lower, but solar and maintenance outages tighten some summer evenings.
- **GAP.** No published GB price-response per degree. The demand forecast error by lead time is held
  (`published_demand_forecast_error_by_lead_day_bmrs_2021_2026.csv`).

## 9. The 2021-23 shock in power

1. **Gas** (gas page §7) set the level: SRMC is about 2 × gas, and gas rose about tenfold.
2. **Carbon** rose to about £83 traded in 2022, adding about £38/MWh at the margin [calc, §2].
3. **Low wind in 2021** kept gas on the margin. 2021 also had a heat wave and low northern European
   hydro [not re-read].
4. **French nuclear outages in 2022** turned GB into a net exporter (§5). That held GB power up even
   in the summer when GB gas was cheap against TTF.
5. **Scarcity events** in autumn 2021 (9 and 15 Sep) printed BM and day-ahead extremes (§7).
6. **CfDs paid back** while the reference was above strikes (§3), which lowered supplier costs that
   no wholesale price shows.

## 10. What the world does against this page

- **The record runs read** is the SSP replay. It is a real price, but it is the imbalance price
  (§0). It is graded against the traded price (MID), and against the gas-plus-carbon mechanism, in
  `docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_POWER_RECORD_AGAINST_THE_ELECTRICITY_PAGE_BY_REGIME_2026-11-24.md`,
  which was pre-registered before the probe ran. The result's headline is in §10a.
- **The forward-year chain** prices from weather → demand and renewables → residual demand → a merit
  order fit to SSP. It has gas but no carbon allowance, no interconnectors, no nuclear availability, and
  no CfD or RO bidding below zero. It loses to a gas-only null at the month in every regime (chain grade).

### 10a. The grade, in brief

Fifteen of twenty-two predictions held. The seven misses stay beside the outcomes in the record.

- **Level: right.** The SSP replay's monthly mean is within £2.03 (pre-crisis), £4.57 (crisis) and
  £1.76 (post-crisis) of the traded price (MID), with bias under £1.20. The power level is not the
  fault, unlike gas.
- **Shape: about twice the traded price's.** SSP's within-day SD is 1.8-2.1 times MID's in every regime.
  It has about twice the negative half-hours in most years (1,073 against 495 in 2024), and 4.4 times
  the £500+ spikes before the crisis. Filed as a LATENT finding: anything valued on within-day shape is
  valued on a price no supplier's hedged energy pays.
- **Gas plus carbon explains the traded price, with nothing fitted.** Pre-crisis the monthly MAE is
  £2.80 with carbon and £17.58 with gas alone. Post-crisis the traded price sat £9.80 below
  gas-plus-carbon SRMC, and the cause is not yet attributed (§2 GAP 1 separates the candidates).
- **Interconnectors:** FUELHH has France at −9.98 TWh in 2022, against DUKES −10.0. **Nuclear** fell
  42% from 2016 to 2024. **Wind:** the gap between the traded price and SRMC falls as the wind share
  rises (monthly correlation −0.45 to −0.64).

## 11. What this page corrects

1. **Our live page's "Live evidence" said the simulation "does not generate a wholesale price".**
   It generates one for forward years (the chain, §10). It also called SSP the "real published Elexon
   system price record" without saying it is the imbalance price. Both are corrected on the page.
2. **The steer's "negative 2022 ILR".** The ILR has a floor of zero. The 2022 benefit came through
   reconciliation and generator paybacks (§3).
3. **"The ~2:1 gas-to-power slope" was stated before carbon.** Carbon added £8-38/MWh at the margin
   in 2017-2022 (§2), and the chain carries none of the allowance.

## 12. Choices this page makes, and why

1. **MID, not day-ahead, is the traded reference in the grade**, because it is the only half-hourly
   traded GB series held for the whole window. Its gap from the hourly day-ahead auction is a GAP.
2. **Fleet-average efficiency, not marginal-unit efficiency**, because it is the published one. The
   marginal plant is less efficient, so the SRMC here is a lower bound.
3. **The civil-penalty UK ETS prices are taken in the year they were traded**, because that is what
   they average. They are futures for the following December, not spot.
4. **No forward number is set here.** Forward gas, carbon and fleet are curriculum, and the director's
   (R13). This page says which mechanisms a forward generator must be able to show.

## 13. Named gaps, in the order the rebuild needs them

1. A UKA market price series 2021-2025 (§2). Item 3, the carbon arm, needs it first.
2. Hourly GB-continent price spreads and flows by link, 2016-2025, and the size of the post-2021
   explicit-allocation loss (§5).
3. The CfD Standard Terms' negative-price clauses by round, and LCCC's quarterly reconciliation
   amounts for 2021-23 (§3). Item 5, the endogenous levy, needs them.
4. Marginal-technology shares by year and the marginal CCGT's efficiency (§1).
5. Nuclear unit availability by month (§4).
6. A published price response by residual-demand band (§6), and a de-rated margin series (§7).
7. The 2013-14 to 2015-16 CPS rates, the CM suspension dates, and the post-2020 coupling texts, which
   are marked [not re-read] above.
