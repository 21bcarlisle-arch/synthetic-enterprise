# How the GB gas price forms: NBP and SAP, driver by driver, 2016-2025

**Knowledge:** gas-wholesale

The K8 page the director asked for on 24 Nov 2026 (05:40 addendum to the signed steer `452de5285`):
"Start with gas, getting gas right first is key as it drives elec often." It extends two pages and
does not repeat them. `how_gb_gas_and_power_prices_move_2026-10-25.md` holds how much the price MOVES
(levels, peaks, volatility, curve shape). `the_worlds_gas_price_record_splices_daily_sap_from_2018_2026-11-18.md`
holds what the world's record is. This page holds WHY the price is what it is: each driver, the
mechanism by which it reaches the price, its size from the published record, and its GAPs. The
electricity page (merit order, interconnectors, CfD/RO, carbon) is the next item, not this one.

Written by the delivery seat, 2026-11-24. **Sources** are named at each claim. Most quantities come
from DESNZ, *Digest of UK Energy Statistics 2026*, Chapter 4 (natural gas), Excel tables 4.1, 4.4a/b,
4.5a/b and 4.6, published 29 Sep 2026, read directly. "[calc]" marks arithmetic on those tables.
"[press]" marks trade press (S&P Global Commodity Insights / Platts, Argus) read through search
results and not the full article: a direction and an order of size, not a series.

## 0. The price, said before it is measured

- **NBP** (National Balancing Point) is a virtual trading point: gas anywhere on the National
  Transmission System is deemed to be there. It is traded OTC and on ICE from within-day out to
  seasons and years. It has no single daily "price"; a day-ahead or front-month assessment is a
  publisher's index (Heren/ICIS, Platts, Argus).
- **SAP** (System Average Price) is the volume-weighted average of the day's trades on the
  on-the-day commodity market (OCM), published by National Gas Transmission. It is what the world's
  daily record now holds from 2018 (`sim/gas_data/sap_daily.csv`). SAP is a within-day price. On a
  stress day it can sit far from the day-ahead NBP that a supplier actually bought at.
- **Cash-out.** A shipper out of balance at the end of the gas day is cashed out at System Marginal
  Buy or Sell Price, which sit outside SAP. That is why shippers trade to balance and why SAP is
  the reference point. A supplier's GAS cost is therefore forward and day-ahead NBP, with SAP and
  cash-out at the margin.

The price at NBP is the price at which GB's last needed molecule arrives, or at which its first
surplus molecule leaves. On most days since 2017 that molecule is a flexible LNG cargo or a flow
through the pipes to Belgium and the Netherlands. That is why NBP tracks the continental hub TTF
and, through LNG, the Asian price JKM, rather than any GB cost of production.

## 1. UK Continental Shelf (UKCS) production: large, declining, a price-taker

- **Size.** 436 TWh in 2019, 423 TWh in 2022 and 344 TWh in 2024: 46%, 41% and 43% of gross supply
  [calc]. Peak was 1,260 TWh in 2000; 2024 is about 27% of it [calc], the lowest since 1973 (DUKES
  4.1 and chapter text).
- **Mechanism.** UKCS gas flows when it is produced. Fields are run to their own plans, oil-linked in
  many cases, and swing very little with price or weather. It sets the volume GB must import, not
  the price. Its decline moved GB from exporter to importer in 2004 and makes each year more
  dependent on the marginal import.
- **How it reaches price.** Indirectly: lower baseload supply means more of each winter day's demand
  is met by the price-setting imports. An unplanned UKCS outage (e.g. a terminal fault in a cold
  week) raises within-day prices because it must be replaced at short notice.
- **GAP.** No published figure for the within-day price effect of a UKCS outage, and no daily UKCS
  flow series has been read. NSTA's production projections have not been read for forward years.

## 2. Norwegian pipeline flows: the largest import, near-baseload, maintenance-driven

- **Size.** 296 TWh in 2019 (32% of gross supply), 339 TWh in 2022 (33%), 341 TWh in 2024 (43%)
  [calc]. Norway was 76% of GB imports in 2024 (DUKES text).
- **Routes.** DUKES 4.5b maximum flows, mcm/day: Langeled 72, Vesterled 39, Tampen Link 27, Gjøa 17,
  and the UK-sector CATS 48 and SAGE 5 that also carry Norwegian gas. Some share downstream pipes, so
  their sum (208) overstates what can arrive at once.
- **Mechanism.** Norwegian producers (Equinor and partners, transport through Gassco) sell into
  whichever of GB and the continent pays more, within the pipe network's limits. Flows run near
  capacity most of the year. They fall in summer maintenance (mainly August-September), and an
  unplanned outage at a processing plant (Kollsnes, Nyhamna) or field cuts GB supply at once.
- **How it reaches price.** Through the margin: a cut in Norwegian supply must be met by more LNG or
  less export, each at a higher price. Because Norway also supplies the continent, its outages
  move NBP and TTF together.
- **GAP.** No daily Norwegian-flow series has been read and no outage-to-price response published.
  The split of Norwegian gas between GB and the continent is not modelled anywhere in the world.

## 3. LNG and the global LNG market: the price-setting swing supply

- **Size.** 186 TWh in 2019 (20% of gross supply), 278 TWh in 2022 (27%), 111 TWh in 2024 (14%)
  [calc]. Share by year [calc]: 2019 19.8%, 2020 21.8%, 2021 17.3%, 2022 26.7%, 2023 24.0%,
  2024 13.9%.
- **Terminals.** DUKES 4.5b regas capacity, mcm/day: Isle of Grain 73, South Hook 58, Dragon 24.66.
  About 156 mcm/d, or about 57 bcm a year [calc], which is large against the import need.
- **Origin.** Qatar was about half of GB's LNG in 2019 [calc]. The US was 50% in 2022, 61% in 2023,
  68% in 2024 [calc] and 76% in 2025 (DUKES text). US LNG is sold free-on-board and can go anywhere.
- **Mechanism.** A flexible cargo goes to the market that pays most after shipping. If Asian JKM is
  above the north-west European price by more than the extra freight, it goes to Asia; NBP must
  rise to attract it. So in a tight global market NBP is set by competition with Asian buyers, and
  in a loose one by the cost of getting cargoes in at all. GB's large regas capacity makes it a
  "sink" in a loose market and a price-taker in a tight one.
- **How it reaches price.** Most directly: LNG is the marginal molecule on most winter days. The
  2022 record shows the other side too: Europe's LNG imports rose 64 bcm in 2022 when global supply
  grew 25 bcm, so Europe outbid Asia; TTF moved from a 12% discount to Asian spot LNG in 2021 to a
  19% premium in 2022 (IEA, *Gas Market Lessons from the 2022-2023 Energy Crisis*).
- **GAP.** No JKM series has been read, and there is no published elasticity of GB LNG send-out to
  the NBP-JKM spread. The world has no LNG term at all.

## 4. Storage, and the loss of Rough in 2017: GB smooths days, not seasons

- **What closed.** Centrica announced on 20 June 2017 that Rough, the UK's only large seasonal store
  (about 3.3 bcm working gas, reported as about 70% of UK storage [press]), would not be refilled.
  It reopened in late 2022 at about a fifth of its former capacity and was raised to about 1.5 bcm in
  2023 (DUKES 4.4b lists Rough at 1,509 mcm) [press for the dates].
- **What remains.** DUKES 4.4a total storage capacity: 14,410 GWh in 2019 (about 1.3 bcm [calc]),
  25,553 GWh in 2022, 35,450 GWh in 2023 (about 3.2 bcm [calc]). The remaining sites are mainly
  fast-cycle salt caverns (Aldbrough, Hornsea, Hatfield Moor, Holford and others) built for days,
  not seasons. UK storage was about 5% of annual demand in 2024 against an EU average of 29% (Lords
  written answer); Centrica (Jan 2025) put it at 12 average days against Germany 89, France 103 and
  the Netherlands 123.
- **Correction to our own page.** `knowledge_gas_wholesale.json` said "around 1.7 bcm, roughly seven
  days of average winter demand, ... since Rough closed in 2017". That figure is from a Commons
  answer that does not say which year it describes. DUKES puts 2019 at about 1.3 bcm and 2023, with
  Rough partly back, at about 3.2 bcm. The page now carries the DUKES figures by year.
- **Mechanism.** Storage buys gas when the summer price is low and sells in winter. On the continent
  that seasonal arbitrage is large and flattens the winter-summer spread. GB's storage is too small
  to do it, so GB meets winter by importing more: more LNG and more continental gas, at the
  continental winter price. After 2017 the GB winter premium is set mostly by the continent's
  storage economics, plus a GB premium on cold days when the pipes are full.
- **How it reaches price.** Two routes. (a) Seasonal: the summer-winter spread follows continental
  storage. In 2021 EU storage entered winter at a near-decade low (IEA), and that was a cause of
  the crisis. (b) Within-day: fast-cycle sites and linepack absorb hours, and when they run down
  in a cold spell the within-day price jumps (1 Mar 2018: storage at its lowest since 2010; SAP
  £127/MWh, see the 2026-10-25 page §1).
- **GAP.** There is no published series of the NBP summer-winter spread in the knowledge layer.
  Ofgem's wholesale indicators publish one ("Gas summer-winter spreads at the NBP"); it has not been
  downloaded. The Rough closure's measured effect on the GB winter premium is not established.

## 5. Interconnection to the continent: IUK, BBL, and coupling to TTF

- **The pipes.** DUKES 4.5b, mcm/day: IUK (Bacton-Zeebrugge) 58 import and 55 export; BBL
  (Balgzand-Bacton) 22 import and 15.3 export. BBL was one-way into GB until physical reverse
  flow became possible on 12 July 2019 [press; Ofgem's 2019 call for evidence gives about
  170 GWh/d]. Moffat carries gas to the island of Ireland (30 mcm/d) and is an export for GB.
- **Mechanism.** When NBP is above the continental hubs by more than the cost of moving gas, gas flows
  into GB; when it is below, gas flows out. Arbitrage through IUK and BBL holds NBP within a
  transport-cost band of Zeebrugge and TTF, so in normal times NBP and TTF move almost together.
  The band is a few p/therm. Argus put IUK monthly capacity at about 2 p/th in 2017 [press].
- **When the coupling breaks.** When the pipes are full, the band no longer binds. In summer 2022 GB
  received more LNG than it could burn or export: exports were a record 260 TWh, 25% of gross supply,
  with 169 TWh going to Belgium and 46 TWh to the Netherlands (DUKES 4.5a) [calc]. Continental
  regas was full, so cargoes landed in GB and the gas could not leave. NBP fell far below TTF: about
  €15 against €86/MWh day-ahead on 10 May 2022, and a Q3 2022 month-ahead discount of about €91/MWh
  [press]. The opposite happened in autumn 2021, with Zeebrugge at a record 30 p/th over NBP
  [press].
- **How it reaches price.** Most of the time it is the transmission belt that makes NBP a TTF price.
  When it is saturated, it is what separates them, and the separation can be larger than the
  pre-crisis price itself.
- **GAP.** No daily NBP-TTF basis series has been read, so the normal band is an anecdote, not a
  distribution. Daily IUK/BBL flows (published by the operators and on National Gas's data portal)
  have not been read.

## 6. Weather-driven demand: the swing in what must be met

- **Size.** GB demand was 854 TWh in 2019, 795 TWh in 2022 and 687 TWh in 2024 (about 78, 72 and
  62 bcm [calc]). Households were 34%, 34% and 37% of it, and power stations 32%, 32% and 26%
  [calc] (DUKES 4.1).
- **Mechanism.** Household and commercial demand is heating, so it follows temperature (and wind
  chill). National Gas forecasts non-daily-metered demand from the Composite Weather Variable
  (effective temperature, wind chill, cold upturn, summer cut-off). Power-station burn follows the
  electricity residual: a still, cold day raises both at once. Peak days run at several times a
  summer day. National Gas's 2022/23 winter review cites about 417 mcm as the highest since the
  Beast from the East [press-level read].
- **How it reaches price.** Demand sets how much marginal supply is called. A forecast cold spell
  raises the forward and day-ahead price before the day; an unforecast one lands in within-day and
  SAP. Because GB storage is thin (§4), a cold week reaches the price more directly than on the
  continent. Gas-for-power also couples gas to wind: a still week raises gas burn and NBP.
- **GAP.** No published price response per degree or per mcm of demand has been found. The world
  derives household gas from weather, but its gas PRICE does not respond to its own weather at all
  (see the grade in §8). §6a measures the record's own response; it is not a published one.

## 6a. Measured on the record: how far GB SAP moves with temperature (worker, 24 Nov)

Measured, not published, so it does not close the GAP above. It does give the rebuild an order of
magnitude. Method: on each day, take the log of SAP over its centred 31-day median, and the national
temperature (`sim.weather_tail_demonstration.load_national_daily`, the world's four-town Open-Meteo
mean) minus its own centred 31-day median. Then regress the first on the second, by year and by half
of the year. Taking deviations from a centred median removes the level and the season, so the slope
is the response to a cold spell *relative to its month*. The record ends 2025-06-07, where the
weather ends. The probe is reproduced below, and it is read-only.

| Year | Nov-Mar %/°C (r) | Apr-Oct %/°C (r) | SAP monthly realised vol, mean · winter · rest · max |
|---|---|---|---|
| 2018 | **−3.69** (−0.41) | −0.42 (−0.31) | 29.9 · 51.4 · 14.5 · 144.7% |
| 2019 | −0.27 (−0.15) | −0.96 (−0.19) | 31.1 · 20.9 · 38.3 · 61.5% |
| 2020 | −0.36 (−0.15) | −0.69 (−0.18) | 30.1 · 25.4 · 33.5 · 54.6% |
| 2021 | −0.93 (−0.25) | −0.57 (−0.18) | 29.2 · 34.5 · 25.3 · 63.2% |
| 2022 | **−3.11** (−0.36) | **−3.18** (−0.19) | 106.2 · 68.6 · 133.0 · 273.1% |
| 2023 | −0.66 (−0.32) | −0.82 (−0.18) | 25.6 · 21.1 · 28.8 · 42.8% |
| 2024 | −0.56 (−0.27) | −0.24 (−0.13) | 14.5 · 16.2 · 13.2 · 23.0% |
| 2025 H1 | −0.37 (−0.25) | −1.15 (−0.52, 53 days) | 14.4 · 13.6 · 15.1 · 28.0% |

Monthly realised vol is the SD of daily log returns × √(days), the OIES method from the 2026-10-25
page. It is computed on SAP, a within-day price.

- **The sign holds every year and in both halves: a colder day than its month prices higher.** In
  calm years the size is small: 0.24-1.15% per °C, so a cold spell 5 °C below its month moves SAP
  about 1-6%. Two years are large, at about 3% per °C. In 2018 the large slope comes from the Beast
  from the East alone (§4). In 2022 it holds in both halves, which fits a tight system, where every
  marginal mcm was dear.
- **It is not a heating-season effect.** The summer slope is as large as the winter one in five of
  eight years. Temperature here also carries the wind and the gas-for-power burn that come with
  the same weather (§6), so the slope is the response to *the weather of a cold day*, not to
  heating demand alone. **Not attributed.** Separating it needs daily NTS demand by sector, and
  that has not been downloaded.
- **The winter volatility premium is not stable in SAP.** Winter/rest ratios run 3.5, 0.55, 0.76,
  1.36, 0.52, 0.73, 1.23 and 0.90. The OIES ≈1.3 ratio is for front-month NBP, 1997-2011, so it is
  not contradicted. It does not carry over to the within-day series either, and a forward generator
  should not impose a fixed winter volatility multiplier on a daily price.
- **For the rebuild (item 4 of the steer).** A forward daily gas price has to show both a small
  persistent cold-day premium and the regime switch (calm about 0.5%/°C, tight about 3%/°C). The
  world's record and its forward draw show neither: their slope is 0 by construction (§8).
  Correlations of −0.15 to −0.41 mean temperature explains under a fifth of SAP's daily deviation
  in any year, so most of the daily structure is supply-side (§2-5).

```python
"""Re-runnable from the repo root, read-only: SAP's response to temperature and its monthly vol."""
import csv, math, statistics as st, sys, collections
sys.path.insert(0, ".")
from sim.weather_tail_demonstration import load_national_daily
sap = {r["settlementDate"]: float(r["systemAveragePrice"]) for r in csv.DictReader(open("sim/gas_data/sap_daily.csv"))}
nat, _doy, dates = load_national_daily()
T = {d.strftime("%Y-%m-%d"): float(nat["temperature_mean_c"][i]) for i, d in enumerate(dates)}
ds = sorted(d for d in sap if d in T)
WINTER = (11, 12, 1, 2, 3)
def slope(y, months):
    xs, ys = [], []
    for i in range(15, len(ds) - 15):
        d = ds[i]
        if not d.startswith(str(y)) or int(d[5:7]) not in months: continue
        w = ds[i-15:i+16]
        xs.append(T[d] - st.median(T[k] for k in w))
        ys.append(math.log(sap[d] / st.median(sap[k] for k in w)))
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((x-mx)*(v-my) for x, v in zip(xs, ys)) / sum((x-mx)**2 for x in xs)
    return len(xs), 100*b, st.correlation(xs, ys)
by = collections.defaultdict(list)
for d in ds: by[d[:7]].append(sap[d])
vol = {m: 100 * st.pstdev([math.log(v[i]/v[i-1]) for i in range(1, len(v))]) * math.sqrt(len(v) - 1)
       for m, v in by.items()}
for y in range(2018, 2026):
    w = slope(y, WINTER); s = slope(y, tuple(m for m in range(1, 13) if m not in WINTER))
    ym = {m: v for m, v in vol.items() if m.startswith(str(y))}
    vw = [v for m, v in ym.items() if int(m[5:]) in WINTER]; vr = [v for m, v in ym.items() if int(m[5:]) not in WINTER]
    print(y, w, s, round(st.mean(ym.values()), 1), round(st.mean(vw), 1), round(st.mean(vr), 1), round(max(ym.values()), 1))
```

## 7. The 2021-23 shock: every driver at once

The record is a sequence, not one cause (IEA, *Gas Market Lessons from the 2022-2023 Energy Crisis*
and *Anatomy of a natural gas crisis*):

1. **2021.** Post-pandemic demand recovery, Asian LNG demand, a low-wind northern-European summer,
   low EU storage after the 2021 injection season, and Russian pipeline flows to Europe down about
   25% year on year in Q4 2021. NBP front-month set a record 116 p/th on 11 Aug 2021 and day-ahead
   reached 355 p/th on 6 Oct (2026-10-25 page §1).
2. **2022.** The invasion of Ukraine (24 Feb) and the cut in Russian pipeline gas to OECD Europe of
   about 50% (83 bcm) over the year, then Nord Stream's stop (Jun-Sep). Europe replaced it with
   LNG and outbid Asia. NBP front-month printed 800 p/th on 7 Mar 2022, and spot reached about
   520-580 p/th in late August [press].
3. **The GB twist.** GB had little direct Russian exposure but imported the continental price
   through IUK/BBL in winter. In summer it was a landing point the continent could not draw from
   fast enough, so NBP traded at a deep discount (§5). SAP averaged £71/MWh in 2022 against the
   world's TTF-derived £100 (the 18 Nov splice page).
4. **2023 onward.** EU storage refilled, demand fell (DUKES: GB demand down 7% from 2019 to 2022 and
   a further 14% to 2024 [calc]), and new LNG arrived. Prices fell back, but stayed above
   pre-2021 levels: SAP about £34/MWh in 2023 and £29/MWh in 2024 against about £8-21 in 2018-20.
- **GAP.** How much of the 2021-22 level was fundamentals and how much repriced risk is not
  settled by any source read. The world replays the record and takes no view; the forward years
  must, and nothing yet does.

## 8. What the world does against this page

- **The record runs read** (`sim.gas_prices_history.load_nbp_history`) is a monthly TTF proxy spread
  flat over days, at a fixed exchange rate. It carries the global level (§3) and nothing else on
  this page: no daily movement (§6), no hub basis (§5), no storage or cold-snap spike (§4).
- **The forward gas draw** (`sim.scenario.gas_scenario_generator`) draws each day independently from
  a two-regime Gaussian. None of the drivers above appears in it: no season, no persistence, no
  LNG or storage state, no weather.
- Both are graded by regime against GB SAP in
  `docs/staging/records/SEAT_RESULT_GRADING_THE_WORLDS_GAS_PRICE_RECORD_AGAINST_THE_GAS_PAGE_BY_REGIME_2026-11-24.md`,
  pre-registered in the `SEAT_PREREG_` record beside it.

## 9. Choices this page makes, and why

1. **SAP, not NBP day-ahead, is the graded reference**, because it is the only free licensed daily GB
   series held (18 Nov page). Its stress-day gap to day-ahead is a named GAP there.
2. **Mechanism before magnitude.** Each driver carries its mechanism and route to price first, its
   size second. A forward generator is to reproduce the mechanisms, not to match this page's
   numbers. A cold, still, low-LNG winter must move price for the reason it did in reality.
3. **No forward number is set here.** Forward gas levels are curriculum, the director's (R13).
   This page says what a forward draw must be able to show, not what it should draw.

## 10. Named gaps, in the order the rebuild needs them

1. Daily NBP-TTF basis 2016-2025, and daily IUK/BBL flows (§5).
2. Ofgem's NBP summer-winter spread series (§4).
3. A JKM series and the NBP-JKM-TTF relationship (§3).
4. A published price response to demand or temperature for GB gas (§6). The record's own response
   is measured in §6a; it is not attributed between heating, wind and gas-for-power.
5. Daily Norwegian flows and outages (§2).
6. Pre-2018 daily SAP (18 Nov page; the NGT series needs a login).
