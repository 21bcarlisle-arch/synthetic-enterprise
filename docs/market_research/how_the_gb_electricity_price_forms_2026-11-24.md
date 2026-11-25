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

## 1a. Why the average price can sit below gas SRMC when no plant bids below cost

- **Mechanism.** A monthly or annual average price is a time-weighted mix of two regimes. When gas is
  marginal, price is at or above the marginal CCGT's SRMC. When residual demand is met by wind, nuclear and
  imports, something cheaper sets the price, often far below gas. The average sits below gas SRMC once the
  second regime is common enough, even if no generator bids below its own cost. The distance from SRMC to
  a non-gas price also scales with the SRMC level: a £90 SRMC leaves more room under it than a £40 one.
- **On the record (24 Nov,
  `docs/staging/records/WORKER_RESULT_GB_POWER_SITS_BELOW_GAS_SRMC_AFTER_THE_CRISIS_BECAUSE_GAS_IS_OFF_THE_MARGIN_MORE_OFTEN_AND_HALF_THE_GAP_WAS_THE_CARBON_PROXY_2026-11-24.md`).**
  The record splits half-hours by FUELHH CCGT output, as a proxy for gas being marginal. In the top quintile,
  MID sits £11-13 above fleet SRMC in 2018-20 and £14-24 above it in 2023-25. In the bottom quintile it sits
  £6-13 below in 2018-20 and £37-42 below in 2023-25. Half-hours with CCGT under 5 GW rose from 5-7% of the
  year (2018-19) to 25% (2023) and 37% (2024).
- **Candidates, as they now stand.** (a) The carbon proxy: half of the power grade's −£9.80 (on UKA auction
  carbon it is −£4.89). (b) Gas off the margin more often: what the record shows. (c) CCGTs bidding below
  spot SRMC (hedged or contracted): **not supported** where gas is plainly marginal. (d) Imports setting the
  price: **GAP**. At a given CCGT output, high-import half-hours price slightly higher, because flow follows
  the spread, so a one-way split cannot separate it (needs §13 GAP 2).
- **Published shares of "gas sets the price" disagree by definition, not only by year.** Electric Insights
  gives 98% of hours (2024 report). ECIU gives about 85% (2024). The Institute for Government's explainer gives
  60% "in 2026", against over 90% in 2021. They count different things: hours in which a gas unit is in the
  marginal stack, the technology of the marginal unit, or price near gas SRMC. None was read in full here
  [press]. The world needs the third of these, because that is what moves a price. GAP 4 stays open.
- **What a forward generator must show.** A price leg that is a no-intercept multiple of gas cannot make the
  low-CCGT regime deep enough at high gas. It needs a shape below gas whose depth scales with SRMC, and
  that shape must be driven by residual demand.
- **The chain against this, by band (24 Nov,
  `docs/staging/records/WORKER_RESULT_THE_CHAINS_POST_CRISIS_BIAS_SITS_MOSTLY_ON_THE_DAYS_GAS_IS_OFF_THE_MARGIN_AND_PARTLY_ON_THE_DAYS_IT_RUNS_HARDEST_2026-11-24.md`).**
  On daily CCGT quintiles, the chain matches the record within £2.5 in every band before the crisis. After it,
  on the lowest-CCGT fifth of days, the record clears £31 below the floor and the chain clears £6 below it.
  On the highest fifth the chain clears £23 above the floor and the record £13. So the shape also needs a top that
  flattens as the floor rises. **Corrected 24 Nov, beside the claim (§1b):** the record's top does not
  flatten as the floor rises. In the crisis, at the highest floor, it held its pre-crisis ratio. What
  changed after the crisis is how many days gas runs little, and the chain does not see it.

## 1b. What sets the price when gas is not marginal, and what the record says scales with gas

- **What the published record names.** Before 2018, fossil plant was more than 80% of GB's marginal
  generation (2013-2017), and coal's share of price-setting hours fell from 31% in 2012 to 11% in 2017.
  France's price was set by hydro and imports 89% of the time (UCL for Ofgem, Castagneto Gissey et al.,
  *The value of international electricity trading*, 2019, pp. 72 and 115, read from the PDF). With gas
  off the margin, the price setters are as follows.
  - **An import**, priced at the neighbour's own marginal cost: French nuclear and hydro, Norwegian hydro at
    its water value, or continental gas and coal at TTF and the EU ETS. The same study measures the
    coupling. One GW more GB wind cuts the GB-France day-ahead spread by €0.31/MWh off-peak and €0.41
    peak. One GW more continental wind widens it by €1.80 and €1.86 (p. 77). Continental wind moves GB's
    price relative to France's about five times as much as GB wind does [calc].
  - **A CCGT bidding below its own SRMC.** It does this to stay on through a trough rather than pay to
    shut down and restart. Modo's SRMC method (*Modelling thermal short run marginal costs*, updated
    Nov 2025) says such plant "might wish to stay online longer... and run for a few hours at a loss". It
    shapes its stack as a proportion of the day's SRMC. In the 2023 BM data, "the cheapest 20% of volume of
    bids and offers are below the average daily short-run marginal cost". That is a discount on a gas
    cost, so its depth scales with gas.
  - **Subsidised or must-run output** at or below zero: RO and early CfD wind, nuclear, CHP and biomass on
    support (§3). Its price does not scale with gas, so the distance from the gas floor down to it does.
    Negative day-ahead hours were 29 in 2022, 107 in 2023 and 149 in 2024 (Modo, *Negative prices*, Sep
    2024; body paywalled, only its summary was read).
- **Above gas**, the dearest offers come from less efficient plant and from plant pricing in a start
  (Modo, same page). A start burns gas, so part of that premium scales with gas. The wear part does not.
  No published split of the two has been read (GAP).
- **What the record says, measured 24 Nov** (`/var/tmp/mk25/ratio_by_ccgt_gw.py`, sha256 `44224ed5…`,
  read-only; the mk24 probe's data, with days binned on fixed 2 GW bands of real daily mean FUELHH CCGT
  output and not on quintiles within each year). Ratio is mean SSP ÷ mean floor, where the floor is
  (SAP + carbon × EF) ÷ 0.50:

  | CCGT GW | pre (2016-21 H1) | crisis (21 H2-23 H1) | post (23 H2-25 H1) |
  |---|---|---|---|
  | 0-4 | — | 0.62 (24 days) | 0.57 (90) |
  | 4-6 | 0.84 (59) | 0.91 (52) | 0.80 (151) |
  | 6-8 | 0.95 | 0.98 | 0.96 |
  | 8-10 | 1.01 | 1.01 | 1.00 |
  | 10-12 | 1.05 | 1.06 | 1.01 |
  | 12-14 | 1.10 | 1.10 | 1.07 |
  | 14-16 | 1.14 | 1.22 | 1.06 (46) |
  | 16-18 | 1.28 | 1.25 | 1.09 (20) |
  | 18-20 | 1.35 | 1.28 | 1.38 (22) |
  | mean floor £/MWh | 34-45 | 130-240 | 78-97 |

- **Read at a given amount of gas running, the price is the same multiple of the floor in every regime**,
  within about 0.05 from 6 to 14 GW, while the mean floor moved by a factor of about four. The multiplicative form
  (price = floor × a function of how much gas runs) is supported. Neither "a top that flattens as the floor
  rises" nor "a depth that grows faster than the floor" is needed to describe the record. The post-crisis
  dip at 14-18 GW rests on 66 days and is not attributed.
- **What changed after the crisis is the mix of days.** 241 of 708 post-crisis days have under 6 GW of CCGT
  running, against 59 of 1,918 before it. The deep quintile-1 gap (−£31) is mostly those days, at a
  ratio of 0.57-0.80, which the pre-crisis record barely contains. It is not a deeper discount at a given
  output.
- **So the chain's post-crisis miss is mostly in the leg that decides how much gas runs, not in the price
  leg's shape.** On the post-crisis days with 0-4 GW of CCGT, the chain prices at 0.91 of the floor, where
  the record clears at 0.57. Its x (demand less wind and solar over dispatchable capacity) does not see
  what displaced gas: imports at 33.4 TWh in 2024 (§5), batteries, and a nuclear output that halved (§4).
  Before acting on that, the next arm separates the two legs on the record, with its prediction filed first.
- **What this does NOT establish.** Real CCGT output is a record observable, used here only to diagnose the
  chain. A forward world has no real CCGT, so the build must produce gas running from its own residual
  demand. The 0.50 efficiency is a constant (§10's efficiency arm). Daily means blur the half-hourly split.

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
- **UKA market series (GAP 1, closed 24 Nov).** Every UK ETS auction from the first (19 May 2021) to
  10 Dec 2025, 116 in all, is transcribed from the UK ETS Authority's annual *Functioning of the UK
  carbon market* reports into `uk_ets_allowance_auction_clearing_prices_2021_2025.json`. The
  transcription reproduces the statutory 2021 price (£47.96, the auction VWAP to 11 Nov), the 2024
  table's revenue total to the pound, and every year's stated price range. Calendar-year
  volume-weighted clearing prices: **£51.41 (2021, from May), £75.42 (2022), £53.38 (2023), £37.18
  (2024), £48.05 (2025)**. The civil-penalty proxy above sat £5-12/t higher in 2022-2024, because it
  averaged futures traded before the 2023 fall. At fleet efficiency that is about £2-4/MWh of SRMC
  [calc], so it explains a minority of the post-crisis −£9.80 gap in the power grade, not most of it.
  The clearing price is the primary-auction price, within about £2 of the prevailing secondary price
  at every 2025 auction (the 2025 report prints both).

## 2a. Forward carbon: the published band, and what it leaves out

*Added 24 Nov 2026 (worker), K8 before any forward carbon is built. Item 3 closed the record's carbon. This
section covers the years after it.*

- **The source.** DESNZ, *Traded carbon values used for modelling purposes, 2025*, published 3 Feb 2026, OGL
  v3. It was read in full from the gov.uk HTML page on 24 Nov. No 2026 edition exists (the analogous URL
  returns 404). Its Table 1 is in £/tCO2e, real 2025, and gives four trajectories. Selected rows:

  | Year | Market | Low (high fossil prices, low growth) | Central (Net Zero Strategy aligned) | High (low fossil prices, high growth) |
  |---|---|---|---|---|
  | 2025 | 44 | 22 | 29 | 37 |
  | 2026 | 42 | 22 | 38 | 47 |
  | 2028 | 41 | 23 | 40 | 54 |
  | 2030 | 50 | 25 | 50 | 66 |
  | 2035 | 70 | 45 | 70 | 92 |
  | 2040 | 136 | 74 | 136 | 178 |
  | 2050 | 235 | 167 | 235 | 298 |

  Market and Central differ only in 2025-29. DESNZ assumes the market's "unobservable" factors "dissipate
  over four years". The table runs annually to 2050.
- **What it is.** DESNZ's Carbon Markets Model finds where allowance demand meets the cap plus the bank. It
  uses four-year foresight, a 3.25% cost of carry and a 67m starting surplus. It models the **standalone**
  UK ETS at its scope at the start of 2025. It "excludes potential UK-EU ETS linking negotiations". The page
  says the values "should not be considered as forecasts". The Market column is started from five months of
  2025 ICE UKA futures.
- **Against the record [calc].** Market 2025 is £44. The auctions' 2025 volume-weighted clearing price is
  £48.05 (§2), and in 2025 real 2025 money is nominal money. The published band therefore starts 8% under the
  record's last year.
- **CPS is not in it.** The page does not mention Carbon Price Support. CPS is frozen at £18/tCO2 to 31 Mar 2028
  (`sim/merit_order_reconstruction.py`, from gov.uk's Climate Change Levy rates). After 2028 it is a GAP. An
  £18 held in nominal money falls in real money.
- **The band moves against gas, by construction.** DESNZ's Low carbon case is its high-fossil-price case, and
  its High carbon case is its low-fossil-price case. `docs/design/curriculum/forward_years.json` draws gas from
  DESNZ's fossil fuel price cases A-C. Drawing carbon independently of gas would produce futures DESNZ does not
  model, such as high gas with high carbon. That pairing is a curriculum choice. It is named here, not made.
- **What it leaves out.** (1) UK-EU linking. DESNZ names the negotiations and excludes them. A linked price
  would follow the EU allowance. No linking path or date has been read (GAP). (2) Price base. The gas band is
  real 2024 and this band is real 2025. The CPI path that converts them is the same curriculum input that
  forward CfD strikes need (§3).
- **What the chain needs.** Each forward day's carbon is CPS plus the UKA level for that year, entering the
  floor the same way as on the record (§2). This section sources the band. Which band, and whether it is drawn
  with gas, is the director's curriculum.

## 3. CfD, RO and negative prices

- **Renewables Obligation (RO).** RO plant earns Renewables Obligation Certificates per MWh generated.
  The buy-out price was £44.77 per ROC in 2016-17 and £52.88 in 2022-23 (Ofgem), and banded technologies
  earn more than one ROC per MWh. ROC income comes with generation and does not depend on the power price
  [inference from the issuing rule; no source states it in these words]. So RO plant will keep running
  at a negative power price until the price is below minus its ROC value. That is what lets the
  clearing price go below zero.
- **Contracts for Difference (CfD).** A CfD generator sells into the market and receives (strike −
  reference price), or pays it when the reference is above the strike. Intermittent CfDs reference the
  day-ahead hourly price. The negative-hour rule by round (GAP 3, read 24 Nov from primary text):
  - **AR6 (Standard Terms v6, 13 Mar 2024, Part 5B, read in full for these clauses).** An "Intermittent
    Negative Price Period" is "any period of one (1) or more Settlement Units in respect of which the
    Intermittent Market Reference Price is negative (that is, less than £0/MWh)", and in it "the
    Intermittent Difference Amount shall be zero (0)". The IMRP is built from "Day Ahead Hourly Prices"
    (the APX and N2EX intermittent indices). The Terms leave "Settlement Unit" to each CfD Agreement,
    which was not read. Baseload contracts (Part 5A) test the same IMRP over hour-long periods, not their
    own seasonal reference. A price of exactly £0 is not negative, so the difference is still paid.
  - **Before AR4 (BEIS, *Government response to consultation on proposed amendments to the CfD
    scheme*, Nov 2020, p.51).** Under "the current rule ... generators still receive difference
    payments when there are less than six consecutive hours of negative pricing". The response extends
    the rule "for future CfD contracts" only, so contracts already signed keep the six-hour rule. Its
    reason: the old rule "encourages CfD generators to keep generating during these periods of low
    demand and also facilitates negative bidding into the balancing mechanism".
  - **AR1 (DECC, *CFD Standard Terms and Conditions*, Version 1, 29 Aug 2014, Part 5B; read 24 Nov
    from the PDF).** No negative-price rule. The Intermittent Difference Amount is "Difference × MAX
    (MIN (Qt × ht × TLMt , Mt ),0 )", with no proviso, and the text holds no "negative price" or
    "consecutive" hours wording. The gov.uk page says these terms "will be used in the first CFD
    Allocation Round". So an AR1 unit keeps its difference in every negative hour, which agrees with
    Modo [press].
  - **The six-hour rule's first text (DECC, *CFD Standard Terms and Conditions*, draft of 26 Oct 2015,
    published as the December 2015 update; read 24 Nov).** Part 5B adds the proviso "in respect of any
    and all Settlement Units which form part of an Intermittent Rolling Negative Price Period, the
    Intermittent Difference Amount shall be zero (0)". The defined period is "a period of six (6) or
    more consecutive Settlement Units (irrespective of whether or not such Settlement Units fall within
    the same Billing Period) in repect [sic] of which the Intermittent Market Reference Price is negative
    (that is, less than £0/MWh)". Baseload units (Part 5A) lose theirs over "twelve (12) or more
    consecutive Settlement Units" whose six hour-long IMRP periods are negative. The February 2017
    draft (tracked against August 2014) keeps both clauses. So the "current rule" that BEIS's 2020
    response describes covers the rounds signed on the 2015-2017 terms (AR2-AR3) [inference from the
    dates when written; AR3's own Version 3 terms were read 25 Nov and carry it, below].
  - **The FID-enabling investment contracts (DECC, *Investment Contract ... laid before Parliament
    pursuant to Paragraph 1 of Schedule 2 to the Energy Act 2013*, May 2014; the four ZIPs on gov.uk's
    *Final Investment Decision (FID) Enabling for Renewables - Investment Contracts*, 10 June 2014,
    OGL; read 24 Nov).** No negative-price rule. There are fourteen phase contracts across eight
    projects: Beatrice P1-P2, Burbo Bank Extension, Dudgeon P1-P3, Hornsea One P1-P3, Walney Extension
    P1-P2 (offshore wind, Part 5B), and Drax, Lynemouth and Teesside (MGT) (biomass, Part 5A). Each IC
    Conditions Part 5B defines "Intermittent Difference Amount = Difference × MAX (MIN (Qt × ht × TLMt ,
    Mt ),0 )". The text and the 25 lines after it are byte-identical in all fourteen (text layer, by
    hash). Part 5A's Baseload Difference Amount has the same shape, with RQM and CHPQM. None of the
    fourteen has "negative price", "rolling negative" or "price is negative" anywhere. So the
    investment contracts are paid in every hour, like AR1.
  - **AR3, AR4, AR5, AR7 and AR8 (the round Standard Terms on gov.uk: Version 3, 1 May 2019; Version 4,
    25 Nov 2021; Version 5, 16 Mar 2023; Version 7, 24 Jul 2025; Version 8, 6 Jul 2026; OGL; read 25 Nov,
    replacing the inference that stood here).** AR3 carries the six-hour rule in the October 2015 wording:
    "“Intermittent Rolling Negative Price Period” means a period of six (6) or more consecutive Settlement
    Units ... in respect of which the Intermittent Market Reference Price is negative (that is, less than
    £0/MWh)", with Baseload at "twelve (12) or more". AR4, AR5, AR7 and AR8 carry AR6's rule: "“Intermittent
    Negative Price Period” means any period of one (1) or more Settlement Units in respect of which the
    Intermittent Market Reference Price is negative (that is, less than £0/MWh)". That definition, and the
    Part 5B proviso that zeroes the difference in it, are identical in all four (whitespace-normalised, by
    hash). Baseload (Part 5A) tests the hourly IMRP in all four, as in AR6. AR8's IMRP still names the APX
    and N2EX intermittent indices. The prediction filed before reading (AR3 six-hour; AR4, AR5 and AR7
    one-hour) held. AR8 was not in the prediction. AR2's round-specific terms were not read: the six-hour
    rule is in both the October 2015 and February 2017 drafts that bracket it [inference that AR2 carries it].
  **So a forward levy carries three rules by vintage:** AR1 and the investment contracts are paid in every hour, AR2-AR3 are zeroed only
  inside six-hour negative runs, and AR4 onwards are zeroed in any negative hour. The 2027-29 tranche
  mixes them: the fleet page has AR3 and AR4 offshore phases starting then, so a forward levy applies
  the rule per unit by round, never one rule to the tranche.
  So older CfD plant still bids below zero in short negative runs, and plant from AR4 on has a reason
  to stop at zero. **For the world:** the rule is tested on the hourly day-ahead price. The world
  settles at the half-hourly imbalance price, which goes negative far more often (§10). Testing the
  rule on SSP would zero too many hours for AR4+ units and find too many six-hour runs for older ones.
  An endogenous levy needs an hourly day-ahead price, or the rule applied to a stated proxy with its
  error measured. The nearest series the world holds is Elexon's MID (`sim/market_index_history`), a
  half-hourly short-term traded price, not the day-ahead hourly auction. **Measured 24 Nov at the count
  level:** built into hours, MID goes negative in 1.6-2.3 times the auction's published negative hours
  (67 against 29 in 2022, 203 against 107 in 2023, 233 against 139-149 in 2024; 1.25-1.59× in 2025), and
  in 29 hours of 2017-18 when the auction had none. So MID is not an unadjusted proxy: a forward levy
  must source the auction or carry that ratio as its error (result record
  `WORKER_RESULT_THE_TRADED_PRICE_GOES_NEGATIVE_IN_1_6_TO_2_3_TIMES_THE_DAY_AHEAD_AUCTIONS_HOURS_SO_IT_IS_NOT_AN_UNADJUSTED_PROXY_FOR_THE_CFD_RULE_2026-11-24.md`).
  Still GAP 3: which hours match (the auction's hourly series is not held), and the six-hour-run count
  the pre-AR4 rule needs.
- **When reference is above strike, generators pay.** In late 2021 and 2022 the reference price was
  above most strikes, and CfD generators paid LCCC, which refunds suppliers (Ofgem, *Decision on the CfD
  allowance methodology*, June 2022). About £205m was paid back from September 2021 to March 2022, and
  £108.3m was returned to suppliers by a June 2022 parliamentary answer [press, low confidence].
  **Corrected 24 Nov from LCCC's own data, beside the press figure:** the net CfD payment from
  Sep 2021 to Mar 2022 was **−£273.4m**, and generator paybacks alone were −£448.0m (LCCC
  `actual-cfd-generation-and-avoided-ghg-emissions`; result record
  `WORKER_RESULT_THE_CFD_LEVY_BUILT_FROM_THE_WORLDS_PRICE_MATCHES_THE_RECORD_TO_A_FEW_PERCENT_2026-11-24.md`).
- **Correction to the steer's wording.** Item 5 of the finding says "the negative 2022 rate". **The
  Interim Levy Rate cannot be set below £0/MWh** under the CfD regulations (Ofgem, same decision). LCCC
  forecast negative supplier payments for cap period nine, which "would imply a negative ILR", and Ofgem
  replaced the ILR in the cap's allowance with an expected levy payment that can be negative. An
  endogenous CfD levy in the world must therefore produce a negative NET payment through reconciliation,
  not a negative ILR. LCCC's **reconciled** daily levy rate (net payment over eligible demand) does go
  negative: on 85 days of 2021 and 238 of 2022, with a low of −£22.68/MWh on 8 Mar 2022 (LCCC
  `reconciled-daily-levy-rates`). That reconciled rate, not the ILR, is what the world should produce.
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

## 4a. From residual demand to gas running: the supply identity, and what each series meters

*Added 24 Nov 2026 by the autonomous worker, for item 4 of the weather-to-price steer. The separating arm
(`docs/staging/records/WORKER_RESULT_BOTH_LEGS_CARRY_THE_CHAINS_POST_CRISIS_MISS_ITS_RESIDUAL_NEVER_RUNS_GAS_LOW_AND_ITS_PRICE_LEG_HAS_NO_LOW_GAS_DAYS_TO_LEARN_FROM_2026-11-24.md`)
found the chain's residual demand can never produce a low-gas day. This section says what does decide how much
gas runs, before any arm is built on it (K8).*

- **What the thing is.** Gas running is the CCGT output that is left after every other source has met the
  demand the transmission system carries. Said as an identity on transmission-metered quantities:
  CCGT ≈ INDO + net export − transmission wind − nuclear − coal − biomass − hydro − pumped storage − other −
  oil − OCGT. Every term on the right except INDO and the flows is a FUELHH fuel type.
- **What each series meters.** INDO "does not include station transformer load, pumped storage demand or
  interconnector demand" and is "metered by the Transmission Company based on its operational metering"
  (Elexon, `data.elexon.co.uk` OpenAPI spec, `/demand/outturn`, read 24 Nov). So output from embedded
  generation (wind and solar without transmission metering) never reaches INDO: it has already reduced it.
  NESO's ND "is equivalent to INDO", and its TSD adds "an estimate of station load of 500MW in BST and 600MW
  in GMT" (NESO, *Historic demand data*, read 24 Nov). NESO estimates embedded wind at 10.7-18.2 TWh a year
  and embedded solar at 9.6-18.7 TWh over 2016-2025 [calc from NESO's `demanddata_YYYY.csv`]. FUELHH is
  "half-hourly generation outturn ... aggregated by Fuel Type category" (same OpenAPI spec). It has no SOLAR,
  BATTERY or embedded code. Its scope sentence was not found, so whether it sums embedded (E-type) BM units is
  a GAP. Its nearest relative, FUELINST, is "system generation connected to the high voltage transmission
  system" (Elexon glossary).
- **The identity, measured on the record** (FUELHH latest publish per fuel and half-hour; the chain's daily
  record for INDO and AGWS; net flow from the interconnector arm's half-hourly file, built from FUELHH's INT types;
  3,321 days with ≥ 46 periods. Probes: `/var/tmp/mk26/fuel_by_year.py`, `identity.py`, `identity_daily.py`,
  `legs_by_year.py`, read-only):

| Regime | Days | Identity gap, mean / SD (GW) | R² of real CCGT on the identity | R² on the chain's form (INDO + export − AGWS wind − AGWS solar), slope | Nuclear + coal + biomass, mean / SD (GW) | Days CCGT < 6 GW |
|---|---|---|---|---|---|---|
| pre (2016 to Jun 2021) | 1,906 | −0.56 / 0.33 | 0.993 | 0.796, 0.61 | 9.31 / 2.22 | 61 |
| crisis (Jul 2021 to Jun 2023) | 707 | −0.59 / 0.19 | 0.998 | 0.808, 0.80 | 7.00 / 1.29 | 76 |
| post (Jul 2023 on) | 708 | −0.78 / 0.30 | 0.996 | 0.737, 0.70 | 6.57 / 0.99 | 241 |

  By year, the identity's gap sits between −0.20 and −1.19 GW in every year 2016-2025. The chain's form
  misses by −0.59 to −3.39 GW, and the miss moves with the solar fleet and the year. The steady −0.6 GW is
  not attributed, but station load fits it in size. FUELHH meters generation gross of station load, INDO excludes it, and NESO puts it at 500-600 MW. The other candidates are units outside FUELHH and the INDO estimate itself.
- **What this says about the chain.** Three things sit between the chain's residual and gas running, and the
  chain holds none of them.
  1. **Must-run output that moved by year.** Nuclear, coal and biomass together fell from 9.3 GW to 6.6 GW
     (mean), and their daily SD before the crisis was 2.2 GW. FUELHH carries biomass under OTHER until late
     2017, so the 2016-17 part of that figure is low. A leg fitted on the chain's residual alone sees this
     term as noise, which fits its slope of 0.6-0.8 rather than 1, and the separating arm's leg H being
     "nearly flat in r".
  2. **Embedded solar counted twice.** INDO is already net of embedded generation, and GB solar is almost
     all embedded. So subtracting AGWS solar from INDO removes it a second time
     (`sim/generation_demand_history.aggregate_solar_generation` says so in its docstring). The size is
     1.2-1.5 GW on average, 1.9-2.2 GW in June-August and 0.3-0.4 GW in December-January. The carbon
     dispatch fixed this defect on 30 Sep (`295e9ad64b`, EP13 s19). `sim/weather_price_chain.residual_demand`
     (whose docstring calls demand − wind − solar "the exact identity") still has it. So does the price
     leg's refit, through `simulation/run_phase3b_recalibration._dedup_latest_renewable_generation`.
  3. **Demand that fell, held flat.** The chain's demand leg is base + HDD + CDD on temperature, with no
     year term (`sim/weather_price_chain.demand_from_weather`). Transmission demand did not stay flat. NESO's
     ND, "equivalent to INDO", was 276 TWh in 2016, 257 in 2019, 233 in 2022 and 231 in 2024 [calc from
     NESO's `demanddata_YYYY.csv`]. On the chain's record INDO averages 30.4 GW (2016), 27.1 (2020) and
     26.0-26.3 (2023-24), while the chain's demand averages 27.7-28.4 GW in every year. Its residual is
     therefore 2.0-3.4 GW too low in 2016-18 and 1.4-2.0 GW too high in 2022-24. In 2025, the part year to
     7 Jun, the gap is +7.2 GW, of which −4.9 GW is the renewable leg, where the fleet trajectory is clamped
     to 2024. **Ranked by size for the post-crisis miss:** demand (+1.7 to +2.0 GW in 2023-24) is the
     largest term. Must-run fell about 2.7 GW from pre to post. Holding it by year would raise
     the chain's post-crisis gas running, so it cannot explain an overstatement; it makes the demand term's
     share larger. The solar double count changes by about 0.25 GW between the regimes
     and its level is absorbed by the fit. None of these is attributed until an arm moves one at a time.
- **AGWS wind is not FUELHH wind.** With AGWS wind in place of FUELHH wind (still no solar), the identity's
  gap is −0.81 / 0.76, +0.30 / 1.63 and −0.43 / 2.66 GW (mean / SD) by regime. AGWS sits above FUELHH
  before the crisis (+0.26 GW) and below it after (−0.89 and −0.36). §6a says AGWS covers BM-unit wind
  only. These measurements do not contradict that on the level, but day by day the two series part by up to
  2.7 GW SD after the crisis. Why they part is a GAP. The chain's wind leg is fitted to AGWS, so its target is the noisier series of the two for this purpose.
- **Batteries.** DUKES 5.16 counts grid-scale battery power capacity at 140 MW (2017), 1,536 MW (2021) and
  7,512 MW (2025). Output was 2,274 GWh and input 2,688 GWh in 2025 (DESNZ, DUKES 5.16, 30 Jul 2026). That
  is about −0.05 GW net on a daily mean [calc], so batteries do not move a daily identity. They shift energy
  inside the day, which is where they reach price. In Elexon's BM unit reference, 45 of 94 battery-named
  units carry fuel type OTHER and 49 carry none. So FUELHH OTHER (0.08 GW in 2018, 0.55 GW in 2025) holds
  some battery output. Pumped storage is 2,744 MW and a net consumer (2025: 1,767 GWh in, 1,437 GWh out;
  DUKES 5.16), and FUELHH carries it as a signed PS term. INDO excludes pumping, so the identity adds it
  back, as written.
- **How it reaches price.** Through the merit order (§1b). At a given amount of gas running, the record's
  SSP is the same multiple of the floor in every regime. So a chain that knows how much gas runs knows most
  of the price shape. The arm that builds gas running from this identity takes its must-run terms from the
  record by year on the record, and from a capacity path for forward years. That path is the director's
  curriculum (R13).
- **GAP.** (1) FUELHH's documented unit scope, and whether it holds E-type units. (2) Why AGWS wind and
  FUELHH wind part day by day. (3) Battery capacity by connection, and energy capacity (GWh) by year: DESNZ
  says it has "no reliable data source". (4) Nuclear unit availability by month, already gap 5. (5) A forward
  must-run path (nuclear closures, biomass contracts), which is curriculum and needs a sourced band.

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

## 5a. A forward net-flow path: what FES publishes, and what the leg needs

*Added 24 Nov 2026 by the autonomous worker, for item 4 of the weather-to-price steer. The net-export arm
(`docs/staging/records/WORKER_RESULT_ON_SAP_PLUS_GB_NET_EXPORT_THE_PRICE_LEG_TAKES_A_QUARTER_OFF_ITS_CRISIS_MISS_AND_ITS_POST_CRISIS_BIAS_TO_ZERO_2026-11-24.md`)
found that GB's net export, added to INDO, is the term a build would ship. Real FUELHH flow cannot cross into
forward years, so that term needs a sourced forward path before it enters `sim/weather_price_chain` (K8). This
section sources it. It sets no forward number.*

- **What the thing is.** In the leg, the term is FUELHH's signed interconnector rows summed per half-hour, with the
  sign flipped so that + is export, in MW, added to INDO. Its annual mean on the record (MW): 2016 −1,914 ...
  2022 **+506** ... 2024 −3,793. 2024's −3,793 MW is −33.2 TWh [calc], against DUKES 5.13's 33.4 TWh net
  import, so FUELHH and DUKES agree on the year both cover. A forward path has to be in this quantity: net, signed,
  transmission-metered and half-hourly. It is not gross imports, and it is not an annual total.
- **What FES publishes.** NESO's *FES 2025 Electricity Supply data table ES1* (`fes2025_es1_v006.csv`, NESO Data
  Portal, read 24 Nov 2026) gives interconnector Capacity (MW), Import (TWh), Export (TWh, negative) and
  Netflows (TWh, + is import) per pathway and calendar column, 2024-2050, at transmission only. The *2026 Ten
  Year Outlook* table (`10yo2026_es1_v001.csv`) gives the same for one central case. Read as totals across
  all links:

  | Netflows, TWh (+ import) | 2025 | 2026 | 2028 | 2030 | 2032 | 2035 |
  |---|---|---|---|---|---|---|
  | Falling Behind | 39.6 | 35.6 | 20.0 | −5.9 | −31.3 | −40.6 |
  | Electric Engagement | 30.6 | 28.6 | 24.2 | −3.1 | −29.3 | −47.8 |
  | Holistic Transition | 29.0 | 26.9 | 30.5 | −3.2 | −42.3 | −81.2 |
  | Hydrogen Evolution | 32.7 | 29.9 | 24.5 | +3.9 | −24.7 | −62.2 |
  | Ten Year Forecast (FES 2025) | 32.7 | 29.2 | 11.9 | −23.8 | −50.4 | −71.8 |
  | Ten Year Outlook (2026) | 35.6 | 23.0 | 9.2 | 8.1 | −0.9 | −34.0 |

  Capacity (GW, same tables): 10.3 in 2025-27 in every case. Then 11.7 by 2028-30, and 11.7-20.6 by 2035
  (Falling Behind 12.9, Electric Engagement 20.6, 2026 Outlook 16.4). §5's link list gives 10.3 GW at
  end-2023 and 10.8 GW once Greenlink is in (2025). ES1's 2025 is 10.3, so 0.5 GW is unexplained: Greenlink's
  timing or a derate. This has not been checked. Ofgem's pipeline
  behind the rise: the Window 3 cap-and-floor IPA (Nov 2024) approved LirIC 0.7 GW, MaresConnect 0.75 GW and
  Tarchon 1.4 GW in principle. The pilot offshore-hybrid IPA approved LionLink 1.8 GW and Nautilus 1.4 GW, by
  2032. Both are conditional (conditions amended Aug 2025). Ofgem gives 11.7 GW "operational or under
  construction" (Ofgem, *Window 3 IPA decision* and press release, Nov 2024).
- **What the band says.** Every case keeps GB a net importer to 2028, by 9-40 TWh (about 1.0-4.5 GW mean
  import [calc, ÷8.76]). Between 2030 and 2032 every case turns GB into a net exporter, or close to it. This is
  NESO's modelled result of GB renewables outgrowing GB demand. It is not an observed trend: the record's net
  import grew to 2024. The 2026 Outlook is the slowest case, with a crossover only by 2032. Across the cases in
  one year, the spread (2030: −23.8 to +8.1 TWh, about 3.7 GW) is larger than any year-to-year move in the record
  outside 2022.
- **The 2024 column does not reconcile, stated before anyone uses it.** ES1 2025's 2024 column is 19.2 TWh
  import, 14.5 TWh export and 4.7 TWh net, the same in every pathway. DUKES 5.13 has 33.4 TWh net import, and
  FUELHH agrees with DUKES. Its 2025 column (29.0-39.6 net) sits around DUKES 2025's 29.7. So the 2024 column
  is not the outturn on the basis the leg uses. Why is a GAP (13: 11a). **A forward path must start from the
  2025 column, or splice from the record's 2024. It must never difference against ES1's own 2024.**
- **Why an annual path is not enough.** Flow follows the price spread (§5, mechanism). GB exports in windy,
  low-price hours and imports in still, high-price ones. So the half-hourly net export is correlated with the
  leg's own residual, and the leg's coefficient was fitted on that joint shape. FES publishes annual totals
  only. No published source read gives a forward half-hourly or seasonal flow shape. The shape is set by the
  continental price, which the world does not carry. There are three ways to build it:
  1. **An annual level from the band, plus the record's within-year shape conditioned on GB residual demand.**
     The shape keeps the 2021+ explicit-allocation regime (§5) and is re-levelled to the drawn annual net.
     This is the smallest build. Its risk is that a net-export GB shifts the shape as well as the level, and
     that cannot be checked on the record (one export year, 2022, for a different cause).
  2. **Endogenous flow from a spread.** This needs a continental price path (TTF plus EU ETS through a
     continental merit order). It is a second world market, and it is out of scope here.
  3. **Leave the term out of forward years.** This asserts the 2024-25 mean net import of about 3.8 GW for
     every forward year (K2: omission asserts a value). Every FES case is below that by 2028.
- **Choice this section makes.** Option 1 is the candidate. The annual level is a **drawn input in a sourced
  band**: the FES 2025 pathways plus the 2026 Outlook, per year from 2026. Like forward carbon, which band the
  company lives through is the director's curriculum, and it is not set here. Before any build, one arm on the
  record has to say how much of the leg's net-export gain is the annual level and how much is the within-year
  shape. That means refitting with net export replaced by its annual mean. If the annual mean carries most of
  it, option 1's shape risk is small. If not, every forward year carries the error beside it.
- **Downstream, stated so nobody rediscovers it.** The same forward flow sets imported carbon in
  `sim/grid_carbon_intensity` (NESO counts imports at the exporting country's factor). A forward path used for
  price must be the one used for carbon, or the world's two forward legs disagree.
- **GAP.** (11a) Why ES1 2025's 2024 column (4.7 TWh net) is not DUKES's 33.4. (11b) Any published forward
  seasonal or hourly flow shape, by link. (11c) Which of the Window 3 and pilot-OHA links reach final investment
  decision. Each is named, and none is filled with a number.

## 5b. A neighbour's shortfall: what it is, how often the record shows one, and why a forward annual level cannot carry it

- **What it is, said before it is counted.** A *neighbour shortfall* here means one thing: GB's net flow with
  **France** (IFA, IFA2 and ElecLink together) runs at or below zero for a calendar-month mean, so GB is not
  importing from the neighbour it imports from most. France is the one named because it is GB's largest import
  source in every year but 2022 (§5) and because French supply is mostly nuclear, so its shortfalls have a
  physical cause that can be dated. It is not a GB scarcity measure, and it is not a price measure. A month
  that meets it is a month in which a usually cheap block of GB supply (about 1-3 GW of import) is absent or
  reversed into demand.
- **The measure** [calc, from the world's own FUELHH cache `sim/cache/elexon_fuelhh_carbon_relevant.json`,
  fuel types INTFR + INTIFA2 + INTELEC, last row wins per half hour and cable, Elexon's sign: + is import].
  Annual totals reconcile with DUKES 5.13's France column to within 0.6 TWh in every year (FUELHH: 9.9, 7.8,
  12.9, 11.1, 8.7, 13.6, −10.0, 12.9, 19.4, 21.9 TWh for 2016-2025). Monthly mean net import, GW:

  | Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|
  | 2016 | 1.54 | 1.93 | 1.95 | 1.55 | 1.81 | 1.69 | 1.49 | 1.44 | 0.66 | **−0.16** | **−0.11** | **−0.21** |
  | 2017 | **−0.61** | 0.58 | 1.76 | 1.81 | 1.62 | 1.22 | 1.59 | 1.59 | 1.12 | 0.21 | **−0.56** | 0.35 |
  | 2018 | 1.91 | 1.58 | 1.42 | 1.42 | 1.73 | 1.47 | 1.74 | 1.53 | 1.21 | 1.00 | 0.97 | 1.65 |
  | 2019 | 1.29 | 1.83 | 1.84 | 0.89 | 1.52 | 1.17 | 1.29 | 1.20 | 1.06 | 0.75 | 1.23 | 1.22 |
  | 2020 | 1.01 | 1.58 | 1.66 | 1.30 | 1.16 | 0.68 | **−0.34** | 0.87 | 0.23 | 1.21 | 1.36 | 1.22 |
  | 2021 | 1.80 | 2.00 | 1.95 | 1.54 | 2.29 | 2.39 | 2.53 | 2.51 | 1.52 | 0.59 | **−0.19** | **−0.21** |
  | 2022 | 0.07 | 0.31 | 0.01 | **−0.87** | **−1.59** | **−2.17** | **−2.42** | **−1.53** | **−2.07** | **−1.75** | **−1.92** | 0.31 |
  | 2023 | 0.93 | 1.24 | 1.71 | 1.45 | 2.99 | 1.86 | 0.86 | 1.14 | 0.99 | 1.49 | 1.83 | 1.11 |
  | 2024 | 1.23 | 2.26 | 3.13 | 2.68 | 2.94 | 3.19 | 3.11 | 2.27 | 1.83 | 1.15 | 1.66 | 1.14 |
  | 2025 | 1.44 | 1.60 | 3.30 | 2.88 | 2.66 | 2.08 | 3.14 | 3.34 | 2.66 | 1.99 | 2.16 | 2.72 |

- **What the table says.** 16 of 120 months meet the definition, in five runs: Oct 2016-Jan 2017 (4), Nov 2017
  (1), Jul 2020 (1), Nov-Dec 2021 (2) and Apr-Nov 2022 (8). If the near-zero Jan and Mar 2022 (0.07, 0.01 GW)
  are read as the same event, Nov 2021-Nov 2022 is one thirteen-month episode with a one-month break. Four of
  five runs start in October or November. 2022 is the only one that runs through a summer, and it is the only
  one large enough to turn GB's annual France balance negative. 2018-2019 and 2023-2025 have none.
- **Two of the five runs have a dated physical cause, both on the French nuclear fleet.**
  - **Autumn 2016.** The French safety authority (ASN) required checks on steam-generator channel heads made at
    Le Creusot and JCFC after a carbon-segregation anomaly. About 20 reactors were offline in late October 2016,
    some held into 2017. French forward baseload for 2017 hit a contract high on 27 Oct 2016, and ICIS reported
    GB turning to net export to France at peak in early November [press: ICIS 26 Oct, 3 Nov and 29 Dec 2016;
    POWER magazine; ASN annual report 2016].
  - **2021-2022.** Stress-corrosion cracking found on safety-injection pipework (Civaux, late 2021), on top of
    maintenance deferred by Covid. French nuclear output in 2022 was **279.0 TWh**, the lowest since 1988, at a
    fleet availability of **54%** against 73% on average in 2015-2019, and France was a net importer
    (16.5 TWh) for the first time since 1980 (RTE, *Bilan électrique 2022*, Feb 2023). Output recovered to
    361.7 TWh in 2024 (RTE, *Bilan électrique 2024*), and France's net export was a record 89 TWh in 2024 and
    92.3 TWh in 2025 [press, quoting RTE's 2025 bilan; not re-read].
  - **Nov 2017 and Jul 2020 are not attributed here.** Both are single months. A cold French November and low
    summer nuclear availability in the Covid year are candidate causes, and neither has been checked. They are
    counted, and their cause is a GAP.
- **Mechanism, for the price.** France's price is set by French nuclear availability against French demand,
  which is strongly temperature-driven in winter because of electric heating. When French nuclear is short,
  France's price rises above GB's, flow reverses (§5), and GB loses an import block and gains an export load.
  GB's residual demand on gas rises by the swing (about 2-4 GW in 2022 against the 2018-19 months [calc]), so gas runs
  harder and sits on the margin more often. On the record this is the term that carries 2022's markup on SAP
  (`c2f65d9e92`) and the seasonal shape the price leg needs in the crisis (the net-export timescale arm: 92%
  month-to-month). The leave-one-year-out profile arm carried none of it (`781ad788be`), because the shape is the
  event and not a GB season.
- **Why a forward annual level cannot carry it.** §5a's candidate forward term is the FES annual net-flow level.
  An annual level averages a shortfall into a slightly smaller import year, so a 2022-type event moves the
  forward price's level a little and its months not at all. On the record, the part that is lost is about
  £2.6/MWh of crisis monthly MAE on the chain's price leg (net-export timescale arm). Leaving the event out
  asserts that no neighbour shortfall happens in any forward year (K2), and the record shows runs in five of
  ten years.
- **Three ways a forward year could carry it, none chosen here.**
  1. **A drawn event.** A forward year draws whether a French shortfall happens, its start month and its length
     from the record's frequency (five runs in ten years, one of them large), and imposes the record's swing
     on the annual level's within-year shape. This is the smallest build. Its risk is that ten years is one
     large event, so its size is a single observation.
  2. **A French availability input.** A forward French nuclear availability path (EDF publishes an annual
     output guidance range, and RTE an adequacy outlook) drives the flow through a spread. This needs the
     continental price §5a option 2 already rules out of scope.
  3. **State it beside the figure.** Every forward figure carries the sentence that a 2022-type neighbour
     shortfall is outside it, and its record-scale size. This is what the forward years do today.
- **Choice this section makes.** None is built. Option 3 is the standing state, and it is honest. Option 1 is
  the candidate if the director wants forward years to be able to defeat the company through a neighbour (the
  coupled-triad requirement that the world can press back). Whether forward years draw such an event, and how
  often, is a curriculum choice and the director's, like the forward bands in §2a, §5a and §8a.
- **GAP.** (13a) The causes of the Nov 2017 and Jul 2020 runs. (13b) French nuclear output by month 2016-2025
  from RTE eco2mix or EDF, so that a run is matched to an availability series rather than to press dates.
  (13c) **Measured, partly closed (`docs/staging/records/WORKER_RESULT_THE_PRE_CRISIS_FRANCE_SHORTFALL_RUNS_PRICED_AGAINST_SAP_AND_NET_EXPORT_CARRIES_39_PERCENT_2026-11-24.md`).** Yes, at the month,
  in two of the three pre-crisis runs. GB SSP over the gas-plus-carbon floor was 1.48 in Oct 2016-Jan 2017
  against 1.11 in the same calendar months of other pre-crisis years, and 1.19 against 1.11 in Jul 2020. Nov
  2017 did not move (1.09 against 1.05). The chain's shippable form runs £5.24 low in those six months against
  its own calendar-month control, and Nov 2016 alone is −£22.7. Each month's own GB net export takes out 39% of
  that gap, so the net-flow level is not the whole mechanism. The rest is not attributed. GB's own winter margin
  that month is a candidate, and it has not been checked. (13d) EDF's forward output guidance by year.

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

## 6a. From wind speed to fleet output: the aggregate power curve

*Added 24 Nov by the worker, before the fleet power-curve arm (item 4, step iii), as K8 requires. The
weather-coupling arm (`WORKER_RESULT_THE_CHAINS_OVER_COUPLING_TO_WIND_IS_IN_ITS_POWER_CURVE_NOT_ITS_PRICE_LEG_2026-11-24.md`)
put the chain's over-coupling to wind in this link.*

- **What a fleet is.** GB wind output is the sum of many farms, onshore and offshore, from the south
  coast to Shetland. Each one sees its own wind at its own hub height. A country's output
  therefore does not ramp like one turbine at the country's average wind. On a day with a moderate
  national mean, some sites are at rated output and others are below cut-in.
- **The published method (Staffell and Pfenninger, 2016, *Energy* 114, 1224-1239, open access, read in
  full for this section).** The Virtual Wind Farm model behind renewables.ninja works farm by farm. It
  (a) takes reanalysis wind at 2, 10 and 50 m; (b) interpolates to each farm's coordinates; (c)
  extrapolates to hub height with the logarithmic profile; and (d) converts speed to power through the
  manufacturer's curve, "smoothed to represent a farm of several geographically dispersed turbines"
  (§3.1). The smoothing is a Gaussian filter of width σ = 0.6 + 0.2·w m/s (their Eq. 1), "to capture the
  increase in spatial and temporal variation at high wind speeds", with parameters "determined
  empirically". Speeds are bias-corrected as w′ = αw + β (Eq. 5). Two parameters are used because "using
  two parameters allows both the level and the variability of CF to be controlled. One parameter used
  alone could exaggerate or dampen the variability of wind speeds" (§3.2).
- **What it achieves for Britain.** Before correction, MERRA put Britain's mean capacity factor at 39.2%
  against 29.0% observed over 2005-14. The correction factors are 0.70 onshore and 0.82 offshore
  (§3.2). After correction, national hourly output has R² 0.935, an RMS error of 4.68 percentage points
  of CF, and a 1.24-point error on percentiles (Table 3, 2009-14, NG and Elexon data covering 92% of
  capacity). The current British fleet averages 32.4% ± 2.1% CF across 20 weather years (§5.1).
- **Smoothing grows with area.** "Individual countries have a wide distribution of CF, whereas the
  aggregate European distribution is much narrower" (§5.2). The same mechanism operates inside one
  country: the spread of site speeds around the national mean flattens the national curve against a
  single turbine's.
- **Multi-turbine curves.** Nørgård and Holttinen (2004, "A multi-turbine power curve approach",
  VTT/Risø) build a regional curve by smoothing a single curve over the distribution of site speeds. A
  secondary description (Aalto, Holttinen) gives the operation as a combination of the curve shifted by
  ±1 m/s. **[not re-read]**: the primary text was not obtained in this session.
- **What the world does instead (`sim/price_engine.wind_power_output_fraction`,
  `sim/weather_price_chain.fit_chain`).** One idealised turbine (cubic from 3 to 12 m/s, rated to 25) is
  applied to **one national speed**. That speed is the mean of four Open-Meteo `wind_speed_10m_mean`
  daily series at the customer towns C1-C4 (`sim/weather_tail_demonstration.load_national_daily`).
  Across 2016-2025 those series average 3.7-4.6 m/s, with a daily standard deviation of about 1.7 m/s.
  So the world's input differs from the published chain at all four stages. It has no site
  interpolation. It has no hub-height extrapolation: a 10 m town speed is not a hub speed offshore. It
  has no bias correction. It has no smoothing. It also uses a daily mean, not hourly speeds, so the
  cube is taken of an average rather than averaged. Its fleet scale is then mean-matched to AGWS output,
  which corrects the level and leaves the slope wrong. The 2.3-3.9× excess in MW per m/s that the
  coupling arm measured is what that combination predicts.
- **What output the record holds.** AGWS covers BM-unit wind only. Embedded onshore wind
  is outside it (W1_7 page). A curve fitted against AGWS is a curve for the transmission-connected
  fleet. That is the fleet the price leg was fitted against, so the two are consistent.
- **The design choice for the arm, and why.** The world has one national speed and no farm register, so
  the VWF method cannot be reproduced. The arm keeps its form and moves it to the fleet: the
  single-turbine curve, convolved with a Gaussian σ, on a transferred speed w′ = a·w + b. Here (a, b)
  stand in for hub height, site exposure and the town-to-site bias, and σ for the spread of site speeds
  around the national mean. All three are fitted on the record. The σ of Eq. 1 is a WITHIN-farm width,
  so the fitted national σ is expected to be larger, and Eq. 1 is a floor to compare against, not a
  value to adopt.
- **GAP.** No published GB national-aggregate curve against a single national (or 10 m town) wind
  speed has been read. A per-site register of GB farms with coordinates and hub heights (REPD holds
  coordinates) has not been brought into the world. Without it, the curve has to be fitted, not
  built.

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

## 8a. A forward transmission-demand path: what FES publishes, and what the chain needs

*Added 24 Nov 2026 by the autonomous worker, for item 4 of the weather-to-price steer. The gas-running arm
(`docs/staging/records/WORKER_RESULT_A_DEMAND_YEAR_TERM_TAKES_HALF_THE_CHAINS_GAS_RUNNING_MISS_AND_THE_IDENTITY_FORM_LEAVES_1_9_GW_UNEXPLAINED_2026-11-24.md`)
found a demand year term is a build term. That term must be sourced for forward years before it enters
`sim/weather_price_chain.demand_from_weather` (K8). This section sources it. It sets no forward number.*

- **What the thing is.** The chain's demand leg stands for transmission demand: INDO, which NESO's ND "is
  equivalent to" (§4a). Embedded wind and solar have already reduced it, and it excludes station load,
  pumping and exports. The year term the arm used is that quantity's annual mean, minus the chain's own mean
  for the year. A forward path has to be in the same unit, or it moves the residual by a definition and not by
  a demand.
- **What FES publishes is a different quantity.** FES 2025's headline annual demand is "Customer demand plus
  on-grid electrolysis meeting GB hydrogen demand only, plus losses, equivalent to GBFES System Demand Total in
  ED1 of data workbook" (NESO, *Future Energy Scenarios: Pathways to Net Zero*, V.5, Nov 2025, Table 3
  footnote). The underlying "end consumer demand" is counted "regardless of where (transmission, distribution
  or on site) the electricity is generated" and is "weather corrected". It "does not include losses, exports,
  station demand, pumping station demand or other forms of storage demand". Losses average "around eight per
  cent", and annual figures are "normally given in financial year" (NESO, *FES 2025 Modelling Methods*,
  §2). So FES is gross of embedded generation, includes losses, is weather-corrected and is fiscal. ND is net
  of embedded generation, observed, and calendar. NESO's ED2 definitions table marks Transmission System
  Demand "Used in FES? No".
- **The bridge on the one year both cover.** FY2024 ED1 system demand is 289.7 TWh. Calendar 2024 ND is 230.9
  TWh. The gap is 58.8 TWh. NESO's embedded wind and solar estimates account for 31.0 TWh of it. **The other
  ~28 TWh is not decomposed in any NESO source read** [calc; GAP 10a]. Losses, other embedded and
  behind-the-meter generation, weather correction and the fiscal year are candidates, with shares unknown.
  The report's own prose gives "In 2024, electricity demand was 267 TWh", and its Table 3 gives 287. Neither is
  ND.
- **The record, in ND terms** (NESO, *Historic demand data*, `demanddata_YYYY.csv`, read 24 Nov; annual TWh =
  Σ half-hourly MW × 0.5 / 10⁶ [calc], checked twice independently):

| Year | ND | Embedded wind | Embedded solar | ND + embedded |
|---|---|---|---|---|
| 2016 | 275.6 | 10.7 | 9.6 | 295.9 |
| 2019 | 257.2 | 15.5 | 11.5 | 284.2 |
| 2020 | 238.5 | 18.2 | 12.1 | 268.9 |
| 2022 | 233.2 | 16.6 | 13.2 | 263.0 |
| 2023 | 228.2 | 15.6 | 13.4 | 257.2 |
| 2024 | 230.9 | 17.0 | 14.0 | 261.8 |
| 2025 | 229.1 | 17.1 | 18.7 | 264.9 |

  ND fell 16.9% from 2016 to 2025, and ND plus embedded wind and solar fell 10.5%. So about a third of the fall
  in transmission demand was embedded generation taking load off the grid, and the rest was demand itself
  [calc]. NESO's mechanism: "As solar and other generation on the regional distribution networks increases, the
  requirement for electricity to flow across the national network reduces" (NESO, *Summer Outlook* press
  release, 16 Apr 2025).
- **Out of sample: 2026, which the world does not hold.** Over 1 January to 3 November (307 days), ND was
  186.9, 188.1, 187.0 and 186.8 TWh in 2023, 2024, 2025 and 2026. That is a mean of 25.4 GW every year, within
  0.7%. ND plus embedded wind and solar rose from 212.0 to 221.4 TWh (+4.4% over three years), and embedded
  solar alone rose from 12.8 to 20.6 TWh [calc, same files]. **Since 2023, growth in demand has been met almost
  exactly by embedded generation, so transmission demand has been flat.** This is real 2026 data read as
  knowledge only. It is never a runtime input the world or the company reads (W6).
- **What FES projects** (ED1 "GBFES System Demand: Total", TWh, fiscal year; FES 2025 and NESO's *Ten Year
  Outlook 2026* `10yo2026_ed1_v001.csv`, both read 24 Nov):

| Path | FY24 | FY25 | FY26 | FY28 | FY30 | FY35 | FY30 vs FY24 |
|---|---|---|---|---|---|---|---|
| Holistic Transition | 289.7 | 290.9 | 295.0 | 314.3 | 339.3 | 433.4 | +17.1% |
| Electric Engagement | 289.7 | 291.7 | 296.1 | 314.3 | 344.8 | 450.1 | +19.0% |
| Hydrogen Evolution | 289.7 | 293.4 | 297.5 | 311.6 | 334.9 | 464.3 | +15.6% |
| Falling Behind | 289.7 | 295.2 | 298.5 | 308.3 | 323.7 | 372.9 | +11.8% |
| Ten Year Forecast (FES 2025) | 289.7 | 292.1 | 295.1 | 308.6 | 330.9 | 396.8 | +14.2% |
| Ten Year Outlook 2026 | — | 292.6 | 295.3 | 306.3 | 323.6 | 385.0 | +11.7% |

  FES has moved to "a three-yearly publication cycle", and the Ten Year Outlook is updated yearly (NESO, *What
  is the Ten-Year Outlook 2026?*, Sep 2026). So the Ten Year Outlook is the current near-term source. FES 2025
  and the 2026 Outlook agree within 1.5% to FY2027 and part after it.
- **How a forward ND path is built, and what it must share.** ND for a forward year ≈ system demand − losses −
  embedded generation − the undecomposed bridge. Every term except the first is either a GAP or a fleet. The
  embedded term is the solar and small-wind fleet: FES 2025 has solar going from 18.8 GW (2024) to 43-47 GW
  (2030), much of it embedded (`scenario_spine_and_friction_anchors_2026-07-23.md` §1.2). If the world's demand
  path took FES's system demand while its fleet stayed flat after 2025 (`sim/renewable_capacity_trend`, R13
  hold-flat), forward ND would rise about 12-19% by 2030. If it took FES's demand together with FES's solar,
  most of that rise would be netted off, as it was in 2023-26. **So forward transmission demand and the forward
  embedded fleet are one capacity path, not two inputs.** This is the same disagreement the forward CfD fleet
  page found for the levy (`the_forward_cfd_fleet_from_lccc_contract_portfolio_2026-11-24.md`). Pairing a FES
  demand with a flat fleet would raise the chain's residual, and so its gas running and its price, through a
  definition mismatch alone.
- **How it reaches price.** Through residual demand and gas running (§4a), which at a given gas level sets the
  floor multiple (§1b). On the record, 1 GW of residual is the size of a third of the post-crisis gas-running miss
  (gas-running arm, G1).
- **Choice this section makes.** No forward value is set, because the path is the director's curriculum (R13).
  The defensible default is the one the record supports: hold ND at its 2023-25 level. Two things support it.
  It is what happened in 2026 to within 0.7%, and it is consistent with a hold-flat fleet only if the embedded
  fleet also holds flat. A curriculum band needs both legs from one source. FES 2025 or the 2026 Ten Year
  Outlook gives system demand. ES1 gives distributed generation, which is a dispatch output on one weather year
  and not a demand deduction, so it is GAP 10b until its relation to NESO's embedded estimates is checked.
- **GAP.** (10a) The ~28 TWh between FES system demand and ND plus embedded wind and solar in 2024. (10b) A
  published forward embedded-generation path on the demand side; ES1 is a dispatch output. (10c) Any NESO
  statement on when transmission demand turns up; none was found, and ETYS was not read. (10d) FES's
  weather correction and fiscal year against ND's observed calendar year. Neither offset has been measured.

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
  **Rebuilt 24 Nov 2026 (steer item 4).** The chain now ships the §6a aggregate curve, fitted on 2016-19
  and held flat from its in-record maximum (9.2 m/s) upward. It uses each year's wind fleet, matched on
  that curve, and carbon (CPS plus the §2 allowance price by month) in the call, with A0-A2 refitted on
  it. Monthly MAE is 6.50 / 17.20 / 8.19 (pre / crisis / post) against the gas-only null's 5.4 /
  24.5 / 6.7. It beats the null in the crisis and still loses by £1-1.5 either side, on the price leg.
  Every forward figure carries that error beside it. Interconnectors, nuclear availability and CfD/RO
  negative bidding are still absent, and the gas input is still the TTF proxy.
- **The chain as the code builds it**, leg by leg, with what each reads, who reads the chain, and where this
  week's graded misses sit: `docs/design/WORLD_POWER_PRICE_AREA_MAP_2026-11-24.md`. Three things the code does that
  this page's mechanisms do not show: the wind leg was one turbine's curve times a mean-matched 128.7 GW (replaced
  24 Nov by the aggregate curve above), the gas input is the monthly TTF proxy (flat within each month), and the
  record's AGWS wind double-counted republished half-hours (fixed 24 Nov in the shared aggregator). No
  forward-years generator reads the chain yet.

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
  gas-plus-carbon SRMC, and the cause is not yet attributed (§2 GAP 1 separates the candidates). *Correction, 24 Nov, beside it:*
  £9.80 was on the civil-penalty carbon proxy. On UKA auction carbon it is £4.89. What remains is mostly
  gas being off the margin more often (§1a).
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
   they average. They are futures for the following December, not spot. *Superseded 24 Nov for
   2021-2025 by the auction series (§2); the grade that used the proxy is kept as run.*
4. **No forward number is set here.** Forward gas, carbon and fleet are curriculum, and the director's
   (R13). This page says which mechanisms a forward generator must be able to show.

## 13. Named gaps, in the order the rebuild needs them

1. ~~A UKA market price series 2021-2025 (§2).~~ Closed 24 Nov from the UK ETS Authority's auction tables (§2).
2. Hourly GB-continent price spreads and flows by link, 2016-2025, and the size of the post-2021
   explicit-allocation loss (§5).
3. ~~The CfD Standard Terms' negative-price clauses by round (§3).~~ Read 24 Nov for AR6 and for the pre-AR4
   six-hour rule; AR1 (Aug 2014, no rule) and the six-hour rule's first text (Oct 2015) read the same day.
   The investment contracts were read the same day: none has a rule, across all fourteen phase contracts. Still
   open: ~~the AR4/AR5/AR7 texts (§3)~~ (read 25 Nov with AR3 and AR8: AR3 six-hour, AR4 onwards one-hour), and AR2's own terms (inferred six-hour). ~~LCCC's reconciliation amounts for
   2021-23~~ are held, as daily payments per unit and reconciled levy rates from the LCCC Data Portal (24 Nov).
   Still open for item 5: the forward CfD fleet (`cfd-contract-portfolio-status`, `forecast-cfd-generation`,
   not yet read).
4. Marginal-technology shares by year and the marginal CCGT's efficiency (§1).
5. Nuclear unit availability by month (§4).
6. A published price response by residual-demand band (§6), and a de-rated margin series (§7).
7. The 2013-14 to 2015-16 CPS rates, the CM suspension dates, and the post-2020 coupling texts, which
   are marked [not re-read] above.
8. A GB fleet-aggregate power curve against a national wind speed, and a per-site farm register
   (REPD coordinates plus hub heights) that would let the world build the curve rather than fit it
   (§6a).
9. FUELHH's unit scope (E-type units), why AGWS and FUELHH wind part day by day, battery capacity by
   connection and in GWh, and a forward must-run path in a sourced band (§4a).
10. The bridge from FES system demand to ND (about 28 TWh not decomposed in 2024), a forward embedded-
    generation path on the demand side, and when transmission demand turns up (§8a).
11. A forward net-flow path (§5a): why ES1 2025's 2024 column is not DUKES, a forward within-year flow shape,
    and which approved links reach FID.
12. Forward carbon (§2a): CPS after 31 Mar 2028, a UK-EU linking path and date, and the CPI path that puts the
    DESNZ band (real 2025) on the gas band's real-2024 base.
13. A neighbour's shortfall (§5b): the causes of the Nov 2017 and Jul 2020 runs, French nuclear output by
    month, what beyond net flow carried Oct 2016-Jan 2017's price (13c remainder), and EDF's forward output guidance.
