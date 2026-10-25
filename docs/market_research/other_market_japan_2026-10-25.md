# Japan compared with GB: household energy market (knowledge only)

**Knowledge:** other-market-japan

**Status:** knowledge only. The director, 25 Oct 2026 07:17 GMT: "this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built." Build nothing from this note.

**Provenance:** the advisor's cited evidence pack `docs/staging/advisor/done/DIRECTOR_EVIDENCE_OTHER_MARKET_JAPAN_VS_GB_2026-10-25.md`, kept below as written (its [unverified] and [derived] tags stand), followed by the verification pass made while drafting the page.

---

# Japan vs GB: household energy market evidence pack for Poesys (v2)

The coordinator's dimensions 12–16 are included, and the contrast and transferability tables now carry rows for them.

**Caveats.** This pack is for understanding only, not a build plan. Every figure has its source beside it. **[derived]** marks my own arithmetic. **[unverified]** marks something recalled but not confirmed in this session. Most GB figures are recalled. I did not re-fetch them, so they carry **[unverified]**. The web-search limit ran out once during this work. Section (d) lists what is still missing.

---

## 1. Weather and climate

- **The climate range is far wider than GB's.** JMA 1991–2020 normals ([JMA](https://www.data.jma.go.jp/stats/data/en/normal/normal.html)):

  | Station | January mean | August mean | Annual mean |
  |---|---|---|---|
  | Sapporo | −3.2 °C | 22.3 °C | 9.2 °C |
  | Tokyo | 5.4 °C | 26.9 °C | 15.8 °C |
  | Naha | 17.3 °C | 29.0 °C | 23.3 °C |

  GB is roughly 4–6 °C in January and 15–17 °C in summer [unverified].
- **Degree days.** CEIC gives **4,741 HDD and 998 CDD** for Japan in 2020 ([CEIC](https://www.ceicdata.com/en/japan/environmental-climate-risk)). This series is probably area-weighted, so it is not comparable with GB's population-weighted HDD of about 2,000–2,300 (base 15.5 °C) [unverified]. What matters is that Japan has real CDD and GB has close to none.
- **Regional spend differs sharply.** Annual household energy spend in 2023 was ¥245,500 in Hokkaido, including ¥79,000 on kerosene. Kanto was ¥168,200 and Okinawa ¥159,300 ([MoE](https://www.env.go.jp/earth/ondanka/kateico2tokei/energy/detail/02/)).

## 2. Energy system and wholesale market

- **Generation mix, 2024:** fossil fuels 69%, solar about 10%, nuclear 8.3%, wind about 1% ([Ember via GreentechLead](https://greentechlead.com/renewable-energy/japans-clean-energy-grows-by-21-twh-in-2024-driven-by-nuclear-and-solar-gains-49378)). In 2019, renewables were 19% of generation. Fossil fuels were 88% of primary energy and nuclear about 4%, against about 15% before 2011 ([IEA Japan 2021](https://www.iea.org/reports/japan-2021)).
- **Gas is imported LNG.** There is no pipeline import and no traded hub like NBP. LNG is mostly oil-indexed [unverified].
- **JEPX market design.**
  - The day-ahead market is a blind single-price auction for **48 thirty-minute products** ([JEPX](https://www.jepx.jp/en/electricpower/outline/)).
  - Gate closure is 10:00 on the day before delivery ([Tensor](https://docs.tensorenergy.jp/en/reference/trading/jepx)).
  - The market splits into **9 area prices**, 3 in the East and 6 in the West ([CME](https://www.cmegroup.com/education/articles-and-reports/introduction-to-the-japanese-power-market)).
  - JEPX volume was **33.5% of demand in FY2024**.
  - The average system price was **¥12.29/kWh in FY2024** and ¥10.74 in FY2023 ([EGC monitoring 2025 no.3](https://www.egc.meti.go.jp/english/committee/pdf/monitoringreport2025no3.pdf)).
  - Bids can range from ¥0.01 to ¥200/kWh, according to a third-party source ([Tensor](https://docs.tensorenergy.jp/en/reference/trading/jepx)).
  - A capacity market and a balancing market exist alongside [unverified detail].
- **The winter 2020–21 crisis.** JEPX peaked at **¥251/kWh** after an LNG shortage combined with cold weather. New entrants on fixed low tariffs failed or suspended sales ([Electricity Forum/Reuters](https://electricityforum.com/news/japan-blackouts); [Kyoto REEKU](https://www.econ.kyoto-u.ac.jp/renewable_energy/stage2/pbfile/m000583/REEKU_DP0052.pdf)).
- **The 50/60 Hz split.** Tokyo–Chubu frequency converters total **2.1 GW**. They are planned to reach 3.0 GW, now expected around December 2028 ([OCCTO](https://www.occto.or.jp/assets/iinkai/kouikikeitouseibi/2025/files/seibi_94_04_01.pdf)).

## 3. Grid

- **Unbundling.** The EPCOs' T&D arms were legally unbundled in **April 2020** ([IEA](https://www.iea.org/reports/japan-2021)). Okinawa may be exempt [unverified].
  - Ten **general T&D operators** each combine the TSO and DSO roles. GB has one TSO and 14 DNO areas [unverified].
  - OCCTO coordinates between areas and runs the switching system.
  - The big gas companies' pipeline arms were unbundled in April 2022 ([ANRE](https://www.enecho.meti.go.jp/about/whitepaper/2021/html/3-6-2.html)).
- **Household connection.** Supply is single-phase three-wire at 100/200 V [unverified].
  - In TEPCO's area and other ampere-system areas, the household picks a **contract-ampere breaker of 10–60 A**. TEPCO changes it free of charge ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)).
  - The breaker size sets the basic charge, from ¥311.75 for 10 A to ¥1,870.50 for 60 A ([Selectra](https://selectra.jp/energy/kaisha/tepco/bill)).
  - Kansai, Chugoku, Shikoku and Okinawa use minimum charges instead [unverified].
- **Network tariffs.** A revenue cap applies from April 2023. TEPCO PG's average low-voltage network revenue is **¥9.02/kWh**, about +2.3% [derived] ([TEPCO PG](https://www.tepco.co.jp/pg/company/press-information/press/2022/1664516_8617.html)). I did not obtain the tariff components or any time-of-use structure.

## 4. Population and households

- **56.2 million households** in 2023 ([Statistics Bureau](https://www.stat.go.jp/info/guide/asu/pdf/2025asu_3-2.pdf)).
- Average household size was 2.21 in the 2020 census [unverified] ([stat.go.jp](https://www.stat.go.jp/data/chiri/map/c_koku/setai/index.html)).
- That is about **2× GB's roughly 28 million households** [unverified].

## 5. Housing and consumption

- **Dwelling stock** ([Statistics Bureau](https://www.stat.go.jp/info/guide/asu/pdf/2025asu_3-2.pdf)):
  - 65.05 million dwellings, of which 13.8% are vacant
  - **flats 44.9%** of occupied dwellings
  - detached houses about 52.8% [derived]
  - GB is about 20% flats [unverified]
- **Heating is room-based.** The share of households whose main heating is an air conditioner rose from **33% to 39%** between 2017 and 2023. Kerosene matters in the north. Heat-pump water heaters went from **13% to 17%** of households over the same period ([MoE](https://www.env.go.jp/council/content/i_05/000397368.pdf)).
- **Water-heating stock.** EcoCute heat-pump water heaters passed 10 million cumulative units in March 2025, with 664,000 shipped in FY2024 ([Dempa](https://dempa-digital.com/?p=655542)). There are also about 510,000 Ene-Farm units, undated ([Newswitch](https://newswitch.jp/p/41679)).
- **Average consumption per household, 2023** ([MoE](https://www.env.go.jp/earth/ondanka/kateico2tokei/energy/detail/02/)):
  - electricity **3,911 kWh**
  - city gas 177 m³, about 2,200 kWh [derived]
  - LPG 23 m³
  - kerosene 119 L

  GB's Ofgem typical consumption values are 2,700 kWh electricity and 11,500 kWh gas [unverified].

## 6. Core regulation

- **Liberalisation dates.** Electricity retail opened fully in April 2016 and gas in April 2017 ([IEA](https://www.iea.org/reports/japan-2021)). METI/ANRE is the ministry and the EGC is the market surveillance regulator. Retailers register to trade.
- **New-entrant share** of low-voltage volume was **24.2%** in May 2025 ([EGC](https://www.egc.meti.go.jp/info/public/pdf/20250815001a.pdf)). It was above 28% in mid-2025 ([EGC monitoring](https://www.egc.meti.go.jp/english/committee/pdf/monitoringreport2025no3.pdf)).
- **Regulated transitional tariffs still exist.** Incumbents have 44.4 million regulated contracts against 23.7 million free contracts in their legacy areas, so **about 65% are regulated** [derived] ([EGC](https://www.egc.meti.go.jp/info/public/pdf/20250815001a.pdf)).
  - Only the incumbent offers the regulated tariff, and its price is set by METI-approved cost.
  - GB's price cap is different: it covers every supplier's standard variable tariff.
- **Gas competition.** By December 2020, 14.3% of households had switched gas supplier. New entrants held 12.2% of household gas volume ([ANRE](https://www.enecho.meti.go.jp/about/whitepaper/2021/html/3-6-2.html)).
- **Failures.** In FY2021, **31 of about 700 new entrants exited**, including 14 bankruptcies ([BCN/Teikoku Databank](https://www.bcnretail.com/market/detail/20220331_272916.html)).
- **Retailer count.** About 700+ are registered [unverified]. 94 took part in METI's 2025 customer-service ranking ([METI](https://www.meti.go.jp/press/2025/12/20251224001/20251224001-1.pdf)).

## 7. Smart meters

- **99.9% coverage, about 81.5 million meters, by end March 2025.** The T&D operators own the meters ([Selectra](https://selectra.jp/energy/guides/meter/smartmeter)).
- Data reaches the T&D operator over the A-route at 30-minute resolution. The in-home B-route supports HEMS.
- **Next-generation meters** run from FY2025 to FY2034. They record **5-minute data** and add Wi-Fi and an IoT route (same source).
- GB is about two-thirds smart [unverified] ([DESNZ](https://www.gov.uk/government/collections/smart-meters-statistics)). GB suppliers own the meters, and communications run through the DCC.

## 8. Billing

- **Monthly bills on actual reads.** Japan has no estimated advances and no annual true-up ([Selectra](https://selectra.jp/energy/guides/meter/smartmeter)).
- **TEPCO regulated tariff** ([Selectra](https://selectra.jp/energy/kaisha/tepco/bill)):
  - Three energy tiers: ¥29.80/kWh up to 120 kWh, ¥36.40/kWh from 120 to 300 kWh, and ¥40.49/kWh above 300 kWh.
  - A monthly **fuel cost adjustment**, which has a cap on the regulated tariff. The example for October 2026 is −¥9.30/kWh.
  - A **renewable surcharge** of ¥4.18/kWh in FY2026. Earlier values were ¥3.98 (FY2025), ¥3.49 (FY2024) and ¥1.40 (FY2023) ([Selectra](https://selectra.jp/energy/news/renewable-energy-surcharge-2026-update)).
- **Worked example.** A 30 A household using 300 kWh a month pays about **¥12,300**, before the fuel cost adjustment and subsidies [derived].
- **Payment.** Customers pay by payment slip or by direct debit ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)). Card payment and convenience-store payment are also common, and prepayment is absent [unverified].
- **Per-kWh bill subsidies** are paid on the bill through retailers ([Enechange](https://enechange.jp/articles/electricity-subsidy)):

  | Period of use | Electricity (¥/kWh) | City gas (¥/m³) |
  |---|---|---|
  | Jan–Aug 2023 | 7 | 30 |
  | Sep 2023–Apr 2024 | 3.5 | 15 |
  | Aug–Sep 2024 | 4 | — |
  | Jan–Feb 2025 | 2.5 | — |
  | Jul–Sep 2025 | 2.0–2.4 | — |
  | Jan–Feb 2026 | 4.5 | — |
  | Jul–Sep 2026 | 3.5–4.5 | — |

## 9. Settlement

- **Thirty-minute imbalance for everyone.** Dispatch runs in 5-minute units ([EGC](https://www.egc.meti.go.jp/activity/emsc_system/pdf/093_04_00.pdf)).
- **Imbalance price cap.** The cap has been ¥200/kWh since FY2022. It rises to **¥300 from FY2026**, and falls back to ¥100 after sustained scarcity ([EGC](https://www.egc.meti.go.jp/info/public/pdf/20250710a.pdf)).
- Balancing groups submit 30-minute plans up to gate closure, 1 hour before delivery [unverified].
- Profiling and reconciliation timelines are unconfirmed. GB is moving to market-wide half-hourly settlement (MHHS) over 2025–27 [unverified].

## 10. Debt and vulnerability

- **TEPCO-type disconnection timeline** ([Selectra](https://selectra.jp/energy/kaisha/tepco/forced-cancellation)):
  - payment due about 30 days after the meter read
  - final deadline about 50 days after the read
  - notice about 5 days before cut-off
  - cut-off around day 51, on weekdays only and not over New Year
  - **no winter ban**
- There is **no social tariff and no priority services register (PSR) equivalent** [unverified]. Support comes as universal per-kWh subsidies (section 8).
- I did not obtain arrears data.

## 11. EV, PV, batteries

- **Rooftop PV.** About **3.0 million** residential PV systems under 10 kW, totalling 13.4 GW, sit on about 10% of detached homes (2022) ([JPEA](https://www.jpea.gr.jp/wp-content/uploads/20230207_jpea.pdf)). 7.0% of households had PV in FY2019 ([MoE](https://www.env.go.jp/content/900516264.pdf)).
- **Post-FIT households.** Systems began leaving FIT in November 2019. By 2023, **1.65 million systems (6.7 GW)** had left ([METI](https://www.meti.go.jp/shingikai/energy_environment/energy_resource/pdf/008_09_00.pdf)).
- **Batteries.** **153,645 stationary lithium-ion units shipped in FY2025** (about 10 kWh each). The cumulative total is 1.14 million units and 9.6 GWh ([JEMA](https://www.jema-net.or.jp/stat/evefa20000004v9u-att/libsystem_FY2025.pdf)).
- **EVs.** 2024 sales were 56,299 BEVs (about 2%) and 63,691 PHEVs (about 2%) ([Inovev](https://inovev.com/index.php/en/market-analyses/category-blog/21299-2025-05-5)). GB's BEV share is about 19% [unverified].

## 12. Cooling

- **Air-conditioner ownership is near-universal outside Hokkaido.**
  - The 2009 national survey found **88.1% penetration and 2,478 units per 1,000 households** (two-or-more-person households) ([Statistics Bureau 2009](https://www.stat.go.jp/data/zensho/2009/taikyu/pdf/yoyaku.pdf)).
  - A third-party compilation puts penetration at about 91–95% in 2024–25, with Hokkaido at about 55–61% and Tokyo at about 99%. Its internal figures conflict ([Assist-All](https://lifestyle.assist-all.co.jp/air-conditioner-penetration-rate-japan-ranking/)).
  - GB air-conditioner ownership is under 5% [unverified].
- **The same unit heats and cools.** The average cooling set-point is 26.7 °C and the average heating set-point is 23.2 °C ([MoE FY2019](https://www.env.go.jp/content/900516264.pdf)). Air conditioners are increasingly the main heating device as well (section 5).
- **Summer peak.** CDD is about 1,000 (section 1). In July–September 2025, the day-ahead price peaked at ¥37.51/kWh on 29 July, and 12 days were at or above ¥30 ([EGC](https://www.egc.meti.go.jp/english/committee/pdf/monitoringreport2025no3.pdf)). The government ran summer subsidies in 2024, 2025 and 2026 (section 8).
- I did not obtain cooling's share of household energy.

## 13. Cooking

- **Three cooking fuels coexist:** city gas (urban areas), LPG (rural and suburban) and electric IH induction. All-electric homes (オール電化) combine IH, EcoCute and air conditioning ([Enechange](https://enechange.jp/articles/about-electrification-house), definition only).
- I found **no national cooking-fuel mix.** A gas-cooker majority with an IH minority is plausible [unverified].
- **Proxy for all-electric new build.** About half of detached homes built after 2016 have a heat-pump water heater, against about 10% of new flats ([MoE](https://www.env.go.jp/council/content/i_05/000397368.pdf)).
- **Cooking is a large share of gas use.** Average city-gas use is only 177 m³ a year (section 5), so cooking and hot water dominate gas demand, unlike GB, where space heating dominates [derived inference].
- GB is mostly gas hobs with a growing share of electric/induction [unverified].

## 14. Switching

- **The process runs through OCCTO's switching support system.**
  1. The customer applies to the new retailer.
  2. The new retailer checks the supply-point number (供給地点特定番号) and pulls the site and usage data, with the customer's consent.
  3. The new retailer requests cancellation through the system.
  4. The old retailer verifies identity and approves the cancellation.
  5. The start and cancellation requests are matched ([ITmedia](https://www.itmedia.co.jp/smartjapan/articles/1609/07/news013.html)).
- **Timescale.** The switch date falls at least **1 business day plus 2 calendar days** after matching if the site has a smart meter. Without one it is 8 business days plus 2 days. Old retailers must check proxy-cancellation requests at least hourly ([OCCTO draft rules](https://www.occto.or.jp/iinkai/sw/2018/files/swshien_38_07.pdf)).
- **No debt-based block.** The rules contain no objection mechanism for debt. They do require a warning about exit penalties (same source).
- **Cooling-off** is **8 days** for door-to-door and telephone sales only ([Selectra](https://selectra.jp/energy/electricity/cooling-off)).
- **Switching rates.** There have been 35.9 million cumulative low-voltage switches since 2016, and 240,836 in May 2025 alone. That is about 3.5% a year against 81.5 million meters [derived] ([EGC](https://www.egc.meti.go.jp/info/public/pdf/20250815001a.pdf)).
- GB is 5 working days, moving towards next-day, with a 14-day cooling-off on all channels and a debt objection for prepayment and arrears [unverified].

## 15. Home moves

- **There is no default or deemed supplier.** A new occupant must choose a retailer and apply ([Selectra](https://selectra.jp/hikkoshi/energy/denki-today)).
  - **Smart-meter sites:** the T&D operator energises remotely, and without a contract the breaker gives no power.
  - **Conventional-meter sites:** power may flow, and the occupant later receives a T&D letter asking them to contract.
  - **Hokkaido from May 2026:** the occupant must apply before moving in.
  - In TEPCO's area, a newcomer who switches power on before applying posts a use-start form left in the dwelling ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)).
- **Backdating** of a move-in date is limited to 31 days ([OCCTO](https://www.occto.or.jp/iinkai/sw/2018/files/swshien_38_07.pdf)). Most retailers bill unregistered use from the date use began (46 of 69 respondents) ([METI survey](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/055_03_02.pdf)).
- **Move-out.** The leaving customer files a stop request (廃止) and the retailer passes it to the T&D operator. The first bill is pro-rated ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)). The final bill is presumably on the stop-date smart read [unverified].
- GB, by contrast, puts the new occupant on a **deemed contract** with the incumbent supplier.

## 16. Where debt sits

- **The retailer owns customer debt.** The retailer bills and collects, and the T&D operator charges the retailer network fees [unverified for low voltage, but structural].
- **Who disconnects.** The retailer terminates the contract and asks the T&D operator, through the switching system, to stop supply. The T&D operator carries out the stop, remotely where a smart meter is fitted ([OCCTO](https://www.occto.or.jp/iinkai/sw/2018/files/swshien_38_07.pdf); [Selectra](https://selectra.jp/energy/kaisha/tepco/forced-cancellation)).
- **Who funds bad debt.** I found **no mutualisation**: the retailer bears its own bad debt [unverified]. A METI survey listed unpaid bills as a retailer risk and mentioned a separate report on unpaid network charges ([METI](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/055_03_02.pdf)).
- **Debt does not follow the customer.** Switching is not blocked. However, the incumbent may refuse a new contract until arrears are paid ([Selectra](https://selectra.jp/energy/kaisha/tepco/forced-cancellation)). I found no shared arrears register.
- **Last-resort supply (最終保障供給)** is provided by the **general T&D operators**, but **only to high-voltage and extra-high-voltage customers** ([Enechange Biz](https://enechange.jp/articles/biz/final-guarantee-terms-cost); [TEPCO PG](https://www.tepco.co.jp/pg/company/press-information/press/2022/1663979_8617.html)).
  - After the 2021–22 retailer exits, contracts rose from 5,133 to 13,045 between 30 April and 20 May 2022 ([SBBIT](https://www.sbbit.jp/article/refers/88546)).
  - They peaked at **45,871 in October 2022** and fell to 17,414 by June 2023 ([Enechange Biz](https://enechange.jp/articles/biz/final-guarantee-terms-cost)). METI's chart shows about 6 GW under last-resort supply in early 2023 ([METI](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/060_04_00.pdf)).
  - Its price became **market-linked from 1 September 2022**, with the standard rate as a floor ([METI survey](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/055_03_02.pdf); [Enechange Biz](https://enechange.jp/articles/biz/final-guarantee-terms-cost)).
- **Low-voltage households have no last-resort supply.** Their backstop is the incumbent's regulated transitional tariff, and households are expected to move to last-resort supply once those tariffs end ([Enechange Biz](https://enechange.jp/articles/biz/final-guarantee-terms-cost)).
  - Exiting retailers in 2022 gave notice of anywhere from about 15 days to over 5 months.
  - 32% of terminating retailers left some customers with no contract ([METI](https://www.meti.go.jp/shingikai/enecho/denryoku_gas/denryoku_gas/pdf/055_03_02.pdf)).
  - GB's Supplier of Last Resort (SoLR) process, by contrast, moves customers with credit balances protected and the costs mutualised through levies [unverified].

---

## (a) Contrast table: Japan vs GB

| Dimension | Japan | GB | Difference that matters |
|---|---|---|---|
| 1 Climate | Subarctic to subtropical; CDD about 1,000 | Mild; heating only | Cooling term and multi-zone weather |
| 2 System | 69% fossil, LNG, no gas hub; 9 area prices; 50/60 Hz with 2.1 GW converters | One price zone, NBP, wind-heavy | Area-price spreads; LNG scarcity shocks |
| 3 Grid | 10 T&D operators that own meters; 10–60 A contract breaker | TSO plus DNOs; fixed fuse | Capacity is a tariff product |
| 4 Households | 56.2 million, about 2.2 people | About 28 million | About 2× the scale |
| 5 Housing | 45% flats; room heating with air conditioners and kerosene; 3,911 kWh | Houses with gas central heating; 2,700 kWh / 11,500 kWh gas | Electricity-led, little wet heating |
| 6 Regulation | Incumbent-only regulated tariff on 65% of incumbent contracts | Cap on all suppliers | Incumbent vs entrant world |
| 7 Meters | 99.9%, operator-owned, 30-min, moving to 5-min | About 2/3 smart, supplier-owned | Data assured, finer granularity |
| 8 Billing | Monthly actuals; tiers plus fuel cost adjustment plus surcharge; per-kWh subsidies | Direct-debit advances; flat rate plus standing charge | No true-up; indexed tiered tariffs |
| 9 Settlement | 30-min plans; imbalance cap ¥200, rising to ¥300 | MHHS transition | Plan duty; capped imbalance |
| 10 Debt and vulnerability | Cut-off around day 51; no winter ban or social tariff | Strong protections | Disconnection is a live path |
| 11 Assets | 3 million PV systems, 1.65 million post-FIT, 1.1 million batteries, 2% BEV share | Fewer batteries, more BEVs | Post-FIT buy-back and battery products |
| 12 Cooling | About 90%+ air-conditioner ownership (about 55–61% in Hokkaido); summer peak and subsidies | Negligible | Summer load and price peak |
| 13 Cooking | City gas, LPG and IH; all-electric new build | Mostly gas hob | Gas load is cooking and hot water, not space heat |
| 14 Switching | OCCTO system; about 3 days with a smart meter; no debt block; 8-day cooling-off for door and phone sales | About 5 days; debt objection | Fast switching that ignores debt |
| 15 Home moves | No deemed supplier; remote energisation needs a contract | Deemed contract with the incumbent supplier | Move-in is an acquisition event |
| 16 Where debt sits | Retailer holds it; T&D disconnects on request; no mutualisation; last resort is high voltage only, households fall back on the regulated tariff | Supplier holds it; SoLR and levies | Failure risk lands on the incumbent tariff |

## (b) Transferability of the GB build

**World components**

| Component | Rating | Why |
|---|---|---|
| Weather-driven demand | Medium | Needs a cooling term and multiple climate zones. |
| Building thermal model | Low | Japan is room-by-room with air conditioners and kerosene, not wet central heating. |
| Household behaviour and finances | Medium | Needs ampere choice, tier response, cooking fuel and kerosene budgets, and move-in. |
| Wholesale price replay | Medium | Needs 9 area prices plus coupling. |
| Settlement clock and reconciliation | High | Settlement is 30-minute native. |
| Smart-meter data feed | High | Data is universal at 30 minutes. Add the B-route and a 5-minute mode. |
| Network and connection limits | Low | Ampere breaker trips are a tariff variable. |
| Cooling and appliances (new) | Low | No GB equivalent. |
| Cooking fuel (new) | Low | Three-fuel cooking does not exist in the GB build. |
| Home moves (new) | Medium | Move events carry over, but there is no deemed supplier. |

**Supplier components**

| Component | Rating | Why |
|---|---|---|
| Tariffs and price compliance | Low | Ampere plus three tiers plus fuel cost adjustment plus surcharge, benchmarked against the incumbent regulated tariff. |
| Quoting, acquisition and switching | Medium | The flow differs (OCCTO system, 1 business day + 2 days, no debt block, cooling-off by channel). Acquisition also happens at move-in. |
| Billing and payments | Low | Monthly actuals, payment slips, subsidy pass-through. |
| Direct debit, collections and debt | Low | Short timeline to disconnection; debt cannot be carried across a switch. |
| Vulnerability duties | Low | Mostly absent in Japan. |
| Hedging and wholesale | Medium | Needs area spreads and LNG shocks. |
| Settlement and imbalance | Medium | Needs plan submission and capped imbalance. |
| Capital and financial rules | Low | No SoLR or mutualisation. Exit means notice and handover to the incumbent or last-resort supply. |
| Advice and asset offers | Medium | Add post-FIT buy-back, EcoCute and IH electrification, and air-conditioner efficiency. |

## (c) New features needed

**New simulation features**
1. Cooling-degree demand driven by an air-conditioner stock, with near-zero ownership in parts of Hokkaido and full ownership in Okinawa and Tokyo.
2. Multi-zone weather.
3. Nine JEPX area prices with converter limits, and an LNG-scarcity scenario.
4. Ampere breakers, including the household's choice of size and trip events.
5. Appliance and fuel world: room-AC heat pumps, kerosene heaters, EcoCute, Ene-Farm, and a per-household cooking fuel (city gas, LPG or IH).
6. An LPG and kerosene market.
7. Post-FIT PV households and home batteries.
8. The incumbent's regulated tariff and fuel cost adjustment as competitor signals.
9. Per-kWh subsidy calendars.
10. A 5-minute meter mode.
11. Imbalance caps.
12. Move-in and move-out events with no deemed supplier: remote energisation gating, a backdating window up to 31 days, and unregistered-use periods.
13. Retailer-exit events that send customers to the incumbent's regulated tariff.

**New supplier features**
1. Tariff engine covering ampere charges or minimum charges, three tiers, the fuel cost adjustment formula and cap, and the renewable surcharge.
2. Monthly actual billing, payment-slip and convenience-store payment, and subsidy line items.
3. A collections path aligned to the roughly 51-day disconnection, plus disconnection requests to the T&D operator through OCCTO.
4. Bad-debt provisioning with no ability to carry debt across a switch.
5. OCCTO switching integration: data pulls with consent, hourly response to proxy-cancellation requests, cooling-off handling by sales channel, and exit-penalty warnings.
6. A move-in acquisition journey with same-day cut-off times.
7. 30-minute plan submission and capped imbalance.
8. Area-price hedging.
9. Post-FIT buy-back, battery and EcoCute scheduling, ampere-downgrade advice, and advice on air-conditioner use and pre-cooling.
10. An orderly-exit playbook with a notice period and customer handover.

## (d) Named gaps

- **Degree days.** No population-weighted HDD/CDD series, and no cooling share of household energy.
- **Appliance ownership.** No current official air-conditioner figure: the official one dates from 2009 and the 2024–25 figures are third-party and conflict. No national cooking-fuel or all-electric share.
- **Customer base and market structure.** No total of low-voltage contracts, so the switching rate uses meter count as a proxy. No retailer count or HHI.
- **Network tariffs.** No low-voltage component values and no confirmation of a time-of-use structure. The scope of the minimum-charge areas is unconfirmed.
- **Settlement and regulated tariffs.** Gate closure and reconciliation timelines are unconfirmed, as are the June 2023 regulated tariff increases.
- **Households and housing.** No LPG household count, payment mix, arrears data, owner-occupation rate or building age.
- **Debt and retailer failure.**
  - The low-voltage bad-debt treatment is unconfirmed in rules.
  - Whether arrears information is shared between retailers is unconfirmed.
  - I have no figures for how many low-voltage customers fell back to regulated tariffs in 2022.
  - No figures for retailer-exit notice rules.
- **Other.** The Ene-Farm figure is undated. Okinawa's unbundling status is uncertain. GB comparison figures were not re-verified.

The search limit was hit once during this work. A follow-up message would let me continue on these gaps.

---

## Verification of [unverified] items (drafting pass, 25 Oct 2026)

Per the director's steer of 25 Oct 07:52 GMT: each [unverified] item is confirmed, corrected or left open. Other-markets packs are the lowest priority, so only the headline items were fetched; the rest stay open and the page does not use them as claims.

- Caveats.** This pack is for understanding only, not a build plan. Every figure has its source beside it. **[derived]** marks my own arithmetic. **[unverified]** marks something recalled but not confirmed in this session. Most GB figures are recalled. I did not...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB is roughly 4–6 °C in January and 15–17 °C in summer [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Degree days.** CEIC gives **4,741 HDD and 998 CDD** for Japan in 2020 ([CEIC](https://www.ceicdata.com/en/japan/environmental-climate-risk)). This series is probably area-weighted, so it is not comparable with GB's population-weighted HDD of about 2,000–2,300 ...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Gas is imported LNG.** There is no pipeline import and no traded hub like NBP. LNG is mostly oil-indexed [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- A capacity market and a balancing market exist alongside [unverified detail].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Unbundling.** The EPCOs' T&D arms were legally unbundled in **April 2020** ([IEA](https://www.iea.org/reports/japan-2021)). Okinawa may be exempt [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Ten **general T&D operators** each combine the TSO and DSO roles. GB has one TSO and 14 DNO areas [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Household connection.** Supply is single-phase three-wire at 100/200 V [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Kansai, Chugoku, Shikoku and Okinawa use minimum charges instead [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Average household size was 2.21 in the 2020 census [unverified] ([stat.go.jp](https://www.stat.go.jp/data/chiri/map/c_koku/setai/index.html)).
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- That is about **2× GB's roughly 28 million households** [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB is about 20% flats [unverified]
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB's Ofgem typical consumption values are 2,700 kWh electricity and 11,500 kWh gas [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Retailer count.** About 700+ are registered [unverified]. 94 took part in METI's 2025 customer-service ranking ([METI](https://www.meti.go.jp/press/2025/12/20251224001/20251224001-1.pdf)).
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB is about two-thirds smart [unverified] ([DESNZ](https://www.gov.uk/government/collections/smart-meters-statistics)). GB suppliers own the meters, and communications run through the DCC.
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Payment.** Customers pay by payment slip or by direct debit ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)). Card payment and convenience-store payment are also common, and prepayment is absent [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Balancing groups submit 30-minute plans up to gate closure, 1 hour before delivery [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Profiling and reconciliation timelines are unconfirmed. GB is moving to market-wide half-hourly settlement (MHHS) over 2025–27 [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- There is **no social tariff and no priority services register (PSR) equivalent** [unverified]. Support comes as universal per-kWh subsidies (section 8).
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- EVs.** 2024 sales were 56,299 BEVs (about 2%) and 63,691 PHEVs (about 2%) ([Inovev](https://inovev.com/index.php/en/market-analyses/category-blog/21299-2025-05-5)). GB's BEV share is about 19% [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB air-conditioner ownership is under 5% [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- I found **no national cooking-fuel mix.** A gas-cooker majority with an IH minority is plausible [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB is mostly gas hobs with a growing share of electric/induction [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB is 5 working days, moving towards next-day, with a 14-day cooling-off on all channels and a debt objection for prepayment and arrears [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Move-out.** The leaving customer files a stop request (廃止) and the retailer passes it to the T&D operator. The first bill is pro-rated ([TEPCO](https://www.tepco.co.jp/e-rates/individual/basic/moving/moving02-j.html)). The final bill is presumably on the stop-...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- The retailer owns customer debt.** The retailer bills and collects, and the T&D operator charges the retailer network fees [unverified for low voltage, but structural].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Who funds bad debt.** I found **no mutualisation**: the retailer bears its own bad debt [unverified]. A METI survey listed unpaid bills as a retailer risk and mentioned a separate report on unpaid network charges ([METI](https://www.meti.go.jp/shingikai/enecho...
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- GB's Supplier of Last Resort (SoLR) process, by contrast, moves customers with credit balances protected and the costs mutualised through levies [unverified].
  - **still open: not fetched in this pass (other-markets packs are the lowest verification priority)**
- Average household size 2.21 (2020 census) [unverified]
  - **still open: the census outline PDF (stat.go.jp, outline_01.pdf) was fetched on 2026-10-25 but its text could not be extracted to the figure; the English summary page carries no figure**
- Degree days: Japan 4,741 HDD and 998 CDD (CEIC, 2020) against GB
  - **still open: Eurostat publishes no Japanese series. For the GB side, Eurostat still publishes UK degree days: UK HDD 2,710-2,961 over 2018-2025 (2024: 2,812) and CDD 0.1-7.0 (2024: 0.43); Eurostat nrg_chdd_a via the dissemination API (unit NR), dataset updated 2026-05-08, accessed 2026-10-25**

**Counts:** confirmed 0, corrected 0, still open 30.
