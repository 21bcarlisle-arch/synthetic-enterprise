**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Other markets are knowledge only: what transfers from the GB build, and what a second market would need (2026-10-25)

**Type:** STEER, through the advisor channel. The director's words, from chat on Sun 25 Oct:

- 07:17 GMT: "Ok. What is like you to do is create some knowledge of how other countries differ. I'm interested in Australia, France, germany, italy, Spain, Belgium, Japan. To start with."
- 07:17 GMT: "To be clear this is not to turn into SIM or supplier action at this stage it just to understand how transferable what we are building in the UK is to other markets and where new SIM and new supplier features would have to be built. Ignore language for now."
- 07:22 GMT: "You may have to look at cooling and cooking  too? Also switching, homemove? Does debt sit with supplier or dno?"

## The rule

**This is knowledge, not work.** Do not change any world or supplier priority, and do not build anything from these seven packs. Publish them as Knowledge pages under a new "Other markets" section of the map. Each pack is a country set against GB on 16 dimensions:

1. weather
2. energy system and wholesale market
3. grid and how homes connect
4. population
5. housing and heating
6. regulation
7. smart meters
8. billing
9. settlement
10. debt and vulnerability
11. EV, PV, batteries and heat pumps
12. cooling
13. cooking
14. switching
15. home moves
16. where debt sits

Each pack also has a transferability rating for every component of the build.

**One design consequence is allowed, and it is cheap.** Where a GB component hard-codes something the packs show varies by market, the hard-coding can be noted in the design docs as a parameter to keep open. Examples: the 30-minute settlement interval, the existence of prepayment, the deemed contract on move-in. Note it; don't build it.

## The advisor's synthesis across the seven

**Transfers well almost everywhere**
- **The weather → building → demand engine.** Every market except Germany and Belgium needs a cooling term.
- **Advice and asset offers** (EV, PV, battery, heat pump). This is strongest in Australia, Germany and Spain.
- **The wholesale replay mechanism.** It ranks High for Germany and Belgium. Australia (5-minute pricing across 5 regions), Italy (zonal) and Japan (9 area prices) need regional prices.

**Transfers poorly almost everywhere. These GB features are unusual, not standard:**
- **Prepayment at GB scale.** It is absent or negligible in all seven. Debt is handled instead by:
  - power limitation: France reduces power; Italy limits to 15% for 15 days; Spain falls back to a 3.5 kW minimum supply;
  - hardship plans (Australia);
  - the DSO as social supplier with prepaid meters (Belgium);
  - straight disconnection: Germany about 239k a year; Japan around day 51.
- **Fixed monthly direct debit building a credit balance.**
  - Germany, Belgium and France use monthly advances plus an annual true-up.
  - Spain, Italy and Japan bill monthly or bimonthly on actual readings.
  - Australia bills quarterly, in arrears.
- **A price cap covering every supplier's default tariff.**
  - France, Spain and Japan have a regulated tariff that only the incumbent may sell. In France and Japan it is still dominant at about 55–65%.
  - Australia has the DMO/VDO, which caps standing offers only and serves as an advertising reference.
  - Italy auctions its default service.
  - Germany's default supplier is not price-capped.
  - Belgium has no cap, only a social tariff.
- **Supplier-owned meters through the DCC.** In six of the seven markets the network operator owns the meters. Australia uses a metering coordinator appointed by the retailer. Data arrives from the DSO.
- **The deemed contract on move-in.** Only Australia, through a designated retailer's standing offer, and Germany, through basic supply, have a default supplier. France, Italy, Spain and Japan require the new occupant to contract. Belgium routes unclaimed points to the DSO.
- **SoLR with a mutualised levy.** No other market socialises failure costs this way.
  - Australia and Germany move customers to large retailers or the default supplier.
  - Japan's last-resort supply covers high-voltage customers only, so households fall back on the regulated tariff.
  - In Belgium, the network absorbs the debt of social-supply customers.

**Cross-cutting features a second market would need**
1. **A configurable settlement clock.** It is 15 minutes across the EU markets (DE, BE, FR imbalance, IT, ES), 5 minutes in Australia and 30 minutes in Japan.
2. **Contracted capacity or a breaker per home.**
   - kVA subscription: France (3–36 kVA), Spain (two contracted powers).
   - kW subscription: Italy (3 kW typical, trips at 3.3).
   - Ampere breaker: Japan (10–60 A).
   - A peak-based network charge: Flanders, on the 12-month average of 15-minute peaks with a 2.5 kW floor.
3. **Network time-of-use calendars as a constraint on households.** Examples: Spain's 2.0TD, France's per-home off-peak hours, Germany's §14a dimming, Australian network tariffs.
4. **An incumbent regulated tariff as a competitor price signal.** Its formula is published: France's TRVE cost stack, Spain's PVPC futures blend, and Japan's tiers plus fuel cost adjustment.
5. **A debt path with power limitation and DSO execution,** with rules for where the debt sits:
   - Italy's CMOR lets arrears follow the customer.
   - Belgium moves debtors to the DSO.
   - Everywhere else, the debt stays with the old supplier.
6. **Cooling demand.** Air-conditioning ownership is about 90%+ in Japan, about 74% in Australia, 56% in Italy, 43%+ in Spain and about 25% in France. It drives summer peaks.
7. **Cooking and heating fuels the GB build lacks:** kerosene and LPG (Japan), oil (Belgium, Germany), district heating (Germany), building-level gas heating (Italy, Spain, France), bottled butane (Spain).
8. **PV export regimes:**
   - per-phase limits and dynamic exports (Australia);
   - monthly netting capped at consumption (Spain);
   - legacy cohorts of net-metered homes (Belgium, Italy);
   - post-FIT buy-back (Japan);
   - the 60% feed-in cap and no payment at negative prices (Germany);
   - regulated purchase of surplus (France).

**Rough order of how far each market is from GB** (advisor's judgement; closest first):
1. **Germany and Belgium:** similar climate and wholesale. They differ in billing, settlement and debt.
2. **Australia:** asset offers transfer very well, but market and settlement mechanics are far apart.
3. **France and Spain:** regulated-tariff benchmark, capacity subscription, electric heating and cooling.
4. **Italy:** all of the above, plus legal heating seasons, CMOR and 3 kW limits.
5. **Japan:** room-based heating, a three-fuel world, ampere tariffs and an incumbent-dominated market.

## Ask

- Publish the seven packs as Knowledge pages in an "Other markets" section, plus one comparison page built from the synthesis above. Mark every page **"knowledge — not on the roadmap"**.
- In the design docs, note each GB hard-coding the synthesis names as a parameter a second market would need. Make no code change.
- Nothing here changes `priority_order.yaml`.

## Done

Seat-executor, 2026-10-25 ~11:55Z.
- The seven packs are published as Knowledge pages under a new "Other markets" theme (7fb1aabcc3, `site/knowledge/other-market-*`).
- The GB hard-codings the synthesis names are noted as rows 8-16 of `docs/design/PORTABILITY_DEBT.md`, in this commit. Row #3 already covered the settlement clock. No code changed and `priority_order.yaml` is untouched, as the steer requires.
- **Not done:** the single comparison page built from the synthesis. The seven per-country pages carry the comparison against GB, but no cross-market page exists. It is handed on as `other-markets-comparison-page`. It is knowledge only and blocks nothing.
