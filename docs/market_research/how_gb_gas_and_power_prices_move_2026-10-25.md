# How GB gas and power prices move, 2016-2025: volatility by time scale, forward-curve shape and spark spreads

**Knowledge:** how-gb-gas-and-power-prices-move

Written 2026-10-25 from the advisor's cited evidence pack
`docs/staging/advisor/done/DIRECTOR_EVIDENCE_GAS_AND_POWER_PRICE_VOLATILITY_2026-10-25.md`, for the
director's steer of the same day that the forward years must reproduce the volatility, and the calm,
of weather and prices at every time scale. This is the K8 page that steer asks for first; its
headline bands are the starting set of world claims for grading the forward generators (EP16).
Figures marked **[derived]** are arithmetic on cited numbers; **[unverified]** items are not claims.
Every pack item marked [unverified] was re-checked on 2026-10-25 against its primary source where
one could be fetched; the outcome of each is in §8.

Neighbouring pages own the mechanisms: `gas-wholesale` (how NBP is set), `electricity-wholesale`
and `merit-order-residual-demand` (how gas sets power at the margin), `hedging-forward-market` (why a
supplier buys ahead), `carbon-price` (the carbon term in the spread), `price-cap` (how the market
reaches a capped bill). This note holds only how much those prices MOVE, over which horizons, and
how the curve and the spread behave.

## 0. What the world and the company do today (read from code, not run, except §0.3)

### 0.1 The replayed gas price has no daily or weekly volatility at all

- `sim/gas_prices_history.py:1-25` states it: the series the world calls NBP is **FRED PNGASEUUSDM,
  the IMF monthly European gas price (a TTF proxy, not NBP)**, converted at a **fixed GBPUSD of 1.28**
  (`GBPUSD = 1.28`, line 38) and **expanded to one repeated value per calendar day**.
- Measured on the file the run reads (`sim/gas_data/nbp_sap.csv`, 3,538 days, 2015-10-01 to
  2025-06-07): **the price moves on 116 days** -- once a month. Every month holds one value.
- Consequences, each against a pack band:
  - Daily and weekly gas volatility is zero by construction. The record's NBP front-month moved
    about 8-15% a month in normal years (OIES, §1) and far more in 2021-22.
  - The 2022 peak in the series is a monthly average of **£186.5/MWh** (Aug 2022). Front-month NBP
    printed 800 p/th on 7 Mar 2022, about **£273/MWh** [derived: 800 p/th ÷ 29.3071 kWh/th].
  - The NBP-TTF basis blowout of July 2022 (a $23/MMBtu discount) cannot appear: the series IS TTF.
  - The dollar-sterling rate moved over the decade and the conversion holds it at 1.28, so every
    FX move becomes a gas-price error of the same size. Its size is not measured here; the Bank of
    England's daily series would settle it.
- So any statistic of gas volatility taken from the run measures the proxy's construction, not the
  market. Every gas claim below is a claim the world **cannot currently meet** at daily or weekly
  scale. That is the first finding of this page, and it is the world's, not the forward generator's.

### 0.2 The forward quote: a lagged spot average times a seasonal shape times a positive premium

- `sim/forward_curve.py:10-31,140-145,227-237`: forward = 30-day-half-life EWMA of past daily spot ×
  a fixed monthly seasonal shape × (1 + premium × √tenor), premium 6% electricity, 5% gas at one year.
- The premium is **always positive**, so the curve never sits below the recent average for a
  structural reason. Backwardation can only arise from the seasonal shape or from the EWMA lagging a
  rising spot. Whether that reproduces the record's mix of backwardation and contango is **not
  measured**: the record's own share of backwardated days is unpublished (gap 4, below).
- The seasonal shape is fixed per month for all years, so the Feb 2025 inversion (summer above
  winter) and the 2023-24 collapse of the winter-summer spread cannot be produced.

### 0.3 The replayed power price, measured (system sell price, not day-ahead)

The world replays Elexon's half-hourly system sell price, 2015-11-07 to 2025-06-07 (168,026
records). Measured 2026-10-25 by reading `elexon_ssp_full.json` from the shared cache (`sim/cache_store.py`) and `sim/gas_data/nbp_sap.csv`; the 20-line read-only script is reproduced in §10
(re-runnable, read-only). The system price is the imbalance price, noisier than day-ahead, so its
spread is not the day-ahead's.

| Year | Mean of daily means £/MWh | SD of daily means | Negative half-hours | Max half-hour | Half-hours > £500 | Mean daily max-min |
|---|---|---|---|---|---|---|
| 2016 | 39.4 | 18.8 | 133 | 1,529 | 30 | 121.8 |
| 2017 | 44.3 | 13.7 | 68 | 1,510 | 4 | 89.4 |
| 2018 | 57.3 | 17.3 | 108 | 990 | 4 | 86.9 |
| 2019 | 42.0 | 11.2 | 139 | 375 | 0 | 70.2 |
| 2020 | 35.1 | 15.4 | 341 | 2,242 | 10 | 80.8 |
| 2021 | 113.3 | 79.6 | 149 | 4,038 | 80 | 241.8 |
| 2022 | 200.1 | 98.5 | 314 | 4,036 | 466 | 307.0 |
| 2023 | 94.6 | 34.6 | 850 | 1,950 | 4 | 162.0 |
| 2024 | 71.2 | 23.0 | 1,073 | 669 | 6 | 115.9 |
| 2025 (to 7 Jun) | 89.8 | 55.4 | 444 | 2,900 | 15 | 144.4 |

- **It agrees with Elexon to the period.** Elexon counts 74 system prices above £500 from 5 Nov 2015
  to 12 Apr 2021, 24 of them in 2021. The replay holds 2+30+4+4+0+10 = **50 for 2015-2020**, which
  is exactly 74 − 24. Elexon names 31 in 2016; the replay's 2016 is 30 and its late-2015 is 2, so one
  period sits on the other side of a year boundary or a strict/inclusive threshold.
- Annual means sit on the day-ahead record where both exist: 2021 113 against day-ahead 118; 2022
  200 against "centred on £200"; 2024 71.2 against EPEX 72.27 (not re-fetched: EPEX returned 403).
- The daily SD of the system price (11-19 in 2016-2020) is above the day-ahead's 6-13 (UCL): the
  imbalance price is the noisier series, as it should be.

### 0.4 What the company sees

The company forms forward quotes from the same seam-crossing history through
`company/interfaces/point_in_time_view.py` and takes risk sigmas through `sim/risk_engine.py`
(`calculate_sigma_recent`). Neither is graded here. Its gas sigma, read off a monthly-flat series,
is a monthly-step sigma, whatever the code calls it.

## 1. NBP gas: levels, peaks, volatility

- Annual Heren NBP (USD/MMBtu): 2016 4.69, 2017 5.81, 2018 8.06, 2019 4.47, 2020 3.42, 2021 15.80;
  discontinued (YCharts). Before 2021 GB gas averaged **£14.24/MWh**; it peaked at **£155.29/MWh on
  22 Dec 2021** (EnAppSys 2021, confirmed). The 7 Mar 2022 front-month print of 800 p/th (≈£273/MWh) is
  about 19× that pre-2021 mean [derived] (confirmed 25 Oct, second read; mixed basis: a front-month print
  over a spot average). Q3 2025 NBP averaged £27.26/MWh (Montel).
- Beast from the East, 1 Mar 2018: day-ahead 279.5 p/th intraday, settled 229.75 p/th; within-day
  350 p/th; 535 p/th on the OCM (ICIS; S&P).
- 2021: front-month record 116.10 p/th (11 Aug); day-ahead 355 p/th (6 Oct).
- 2022: front-month 800 p/th (7 Mar); Summer-22 front season 479.90 p/th; Winter-22 443 p/th
  (7 Jul) (S&P). House of Commons Library: 19p/kWh in Aug 2022 (≈557 p/th [derived]), below 4p/kWh
  since spring 2023.
- NBP-TTF basis: $23.287/MMBtu on 15 Jul 2022 (S&P), when GB had LNG it could not export.
- **Published volatility (OIES NG60, Alterman 2012, confirmed).** Front-month NBP, monthly realised
  volatility = SD of daily log returns × √(trading days in the month). Controlled series trends from
  about **8% (1997) to about 15% (2011)**. Winter months (Nov-Mar) averaged **13.0%**, the rest of the
  year **9.9%**, ratio ≈1.3 [derived]. Spikes: **37%** (Russia-Ukraine 2006), 22% (2009); NBP's
  monthly minimum averaged about 5.7% and its maximum reached 50.0% (original series). Annualised
  ×√12 ≈ 28-52% [derived].
- Risk premium: forwards are biased predictors of spot; premium positive, larger and more volatile in
  winter; about 0.5% a day at day-ahead and 4-20% annualised over 3-6 months (Haff et al. 2008;
  IREF 2018; not re-fetched, both behind publisher pages).
- 2021-22 realised volatility: **no fetchable primary source.** "Above 100% annualised for parts of
  2022" stays **[unverified]** and is not used as a claim.

## 2. GB power: levels, volatility, negatives, spikes

- Day-ahead annual means: 2015-16 £38.63 (daily SD £5.91), 2016-17 £45.49 (SD £12.74), conditional
  variance +51% after the referendum (UCL for Ofgem 2018, confirmed). 2020 £35.26, 2021 £118.29, up
  235%; 2021 super-peak £153.19, off-peak £93.98 (EnAppSys, confirmed). 2022 "centred on £200"
  (Electric Insights). 2024 £72.27 base, £81.38 peak (EPEX; 403 on re-fetch, not confirmed).
  2024 £74.0 and 2025 £81.2 (Electricity Maps, hourly basis, confirmed).
- 2025: mean daily swing **£68/MWh**; largest **£866** on 22 Jan (£92 to £958.5); **190 negative
  hours over 33 days**, minimum −£30.5 (Electricity Maps, confirmed; it counts 141 negative hours in
  2024 on its own basis).
- Spikes: 8 Jan 2021 system price £4,000; 9 Sep 2021 £4,037.80 (Elexon); day-ahead £2,500.01 on 15
  Sep 2021, 614% over the previous £350 record (EnAppSys, confirmed). 2021 system prices averaged
  £113, 33 periods above £1,000 (Elexon). 23 Aug 2022 daily day-ahead record £539.59.
- **Seasonality of spikes (Elexon, confirmed):** of system prices above £500 in 2016-2020, **62% autumn,
  26% spring, 12% winter, 0% summer**.
- Negative day-ahead hours: first ever −£2.84 on 9 Dec 2019; 2022 19-29, 2023 86-107, 2024 139-149
  (to Sep, Modo), 2025 ≈190 (Aurora, Modo, NextEnergy, Electricity Maps). Longest run 17 hours
  (16 Jul 2023 and 25 May 2025).

## 3. Forward-curve shape

- Winter-21 opened at 55 p/th and expired at 236.30 p/th (+330%); from July 2021 day-ahead traded
  above front-quarter (S&P).
- NBP winter-vs-day-ahead spread averaged about 50 p/th in Q2 2023 and about 19 p/th in Q2 2024;
  Centrica called the Rough outlook "challenging given low seasonal spreads" (S&P).
- 3 Feb 2025: Summer-25 128.53 p/th above Winter-25 120.60 p/th, an inverted seasonal spread (MNI);
  by April 2025 TTF had "flipped into contango" (Timera).
- Qualitative rule the episodes share: high or rising spot → backwardation and a compressed or
  inverted seasonal spread; falling spot → contango. **No published share of backwardated days.**

## 4. Clean spark and dark spreads

- Convention: spark = power − gas/0.4913; clean spark subtracts carbon × 0.411 t/MWh; dark spreads at
  35% and 0.971 t/MWh (secondary source; not a primary convention document).
- Carbon: Carbon Price Support £18/t on top of the UK ETS; UK ETS about £35/t in Oct 2023; GB gas
  plant paid about £65/t in H1 2021 and £62/t in H1 2025 (Modo; Electric Insights).
- Levels (Timera, Jan 2023, confirmed): peak CSS about £4-10/MWh before 2021; month-ahead crisis
  maxima about **£280 base and £610 peak**; late Jan 2023 £16 base, £46 peak; "baseload CSS forward
  prices are structurally negative from summer 2026 onwards".
- Q4 2021: the least efficient coal (30%) had lower breakeven than the best CCGTs (55%) (EnAppSys).
- Gas set the price **65.4%** of the time in 2017 (UCL, confirmed) and about 85% in 2024 (ECIU).

## 5. Weather-price links

- 2021 spike periods: wind 1.1 GWh per settlement period against 3.4 GWh otherwise (Elexon,
  confirmed); gas 91% of accepted offers. Negative system-price periods: 13.8 GW wind against
  21.3 GW demand (EnAppSys, confirmed).
- 2024: wind cut day-ahead by up to about £24-25/MWh against a modelled £96-101 without it (ECIU).
- 1 Mar 2018: gas demand 4,600 GWh/day, storage lowest since 2010, coal displaced gas.
- No GB daily gas-power correlation and no price-per-GW-of-wind elasticity was found.

## 6. Forecast error and horizon

Forwards are biased predictors with a premium that grows with horizon and is larger in winter; since
mid-2021 futures "failed to anticipate large price increases" (European Commission, Autumn 2022);
energy assumptions added 1.6 pp to the ECB's one-quarter-ahead inflation error in Q1 2022 against
about 0.2 pp before COVID. **No published RMSE-by-horizon for NBP or GB power forwards.**

## 7. Headline bands (candidate world claims; calibration only)

| Measure | Band | Basis | The world today |
|---|---|---|---|
| NBP front-month monthly realised vol, normal regime | 8-15% (≈28-52% annualised) | OIES 1997-2011, confirmed; 2016-20 proposed | **0** inside each month (monthly-flat proxy) |
| NBP winter/summer volatility ratio | ≈1.3 (13.0/9.9) | OIES, confirmed | not measurable on the proxy |
| GB day-ahead annual mean, normal | £35-46/MWh (2015-20) | UCL, EnAppSys | system price 35.1-57.3 |
| GB day-ahead annual mean, crisis | £118 (2021) to ≈£200 (2022) | EnAppSys, Electric Insights | 113.3, 200.1 |
| GB day-ahead annual mean, post-crisis | £72-81 (2024-25) | Electricity Maps, EPEX | 71.2, 89.8 (part year) |
| Daily SD of day-ahead, normal | £6-13/MWh | UCL | system price 11-19 (noisier series) |
| Mean daily max-min swing, 2025 | ≈£68/MWh (hourly day-ahead) | Electricity Maps | half-hourly system price 144 |
| Negative day-ahead hours a year | 0 (≤2018); 19-29 (2022); 86-107 (2023); 139-149 (2024); ≈190 (2025) | several, confirmed for 2025 | not comparable: system-price half-hours |
| System prices above £500 a year | 31 in 2016 (max of 2016-20); 50 over 2015-20 | Elexon, confirmed | 30 in 2016; 50 over 2015-20 |
| Seasonal timing of system prices > £500 | autumn 62%, spring 26%, winter 12%, summer 0% (2016-20) | Elexon, confirmed | not yet measured |
| Peak clean spark spread, normal | £4-10/MWh | Timera, confirmed | not computed (gas proxy) |
| Month-ahead CSS, crisis max | ≈£280 base, ≈£610 peak | Timera, confirmed | not computed |
| NBP winter-minus-spot, Q2 | 19-50 p/th (2023-24); can invert | S&P, MNI | cannot invert (fixed shape) |
| Share of days in backwardation | **none published** | gap | not measured |
| Gas share of marginal hours | 65% (2017) to ≈85% (2024) | UCL (confirmed), ECIU | merit order page owns it |

These are aggregate properties of the record, to grade generators against. They are never a target
for a supplier outcome, and never tuned to.

## 8. Verification of the pack's unverified and key items (2026-10-25)

| Item | Outcome | Source, accessed 2026-10-25 |
|---|---|---|
| OIES winter 13.0% / rest 9.9%; trend 8%→15%; 2006 spike 37% | **confirmed** | OIES NG60 pdf, pp. 26-28, 34 |
| OIES method (SD daily log returns × √days) | **confirmed**; the ×√12 annualisation stays [derived] | OIES NG60 §1 |
| Elexon: 31 prices > £500 in 2016; 24 in 2021 to 12 Apr; 62/26/12/0 seasonal split; wind 1.1 vs 3.4 GWh | **confirmed** | elexon.co.uk BSC insight, 2021 |
| UCL: £38.63 (SD 5.91), £45.49 (SD 12.74), +51% variance, gas marginal 65.4% (2017) | **confirmed** | Ofgem-hosted UCL report, Table 3, p. 21-22 |
| EnAppSys: £35.26→£118.29; £155.29 gas peak; £14.24 pre-2021 gas mean; £2,500.01; 13.8 GW | **confirmed** | EnAppSys 2021 GB summary pdf |
| Electricity Maps 2025: £81.2, £68 swing, 190 negative hours over 33 days, −£30.5, £958.5 | **confirmed** | electricitymaps.com grid in review 2025 |
| Timera CSS £280/£610, £16/£46, structurally negative from summer 2026 | **confirmed** | timera-energy.com, Jan 2023 |
| EPEX 2024 £72.27 / £81.38 | **still open**: EPEX returned 403 | — |
| TTF/NBP realised vol > 100% annualised in parts of 2022 [unverified] | **still open**; not promoted | no fetchable source |
| NBP crisis peak 10-25× pre-crisis average [proposed] | **still open**: baseline unverified | — |
| Mean-reversion half-lives, kurtosis | **still open** (paywalled) | — |
| Share of backwardated days; spark spread series; gas-power correlation; forward RMSE by horizon | **still unpublished** (findings, gaps 4-7) | — |

**Counts: 7 confirmed (covering 24 figures), 0 corrected, 5 still open.**

## 9. Named gaps

1. NBP realised volatility 2016-2025 by year and scale: needs ICE settlement data or Ofgem WMI
   downloads. The world's own gas series cannot supply it (§0.1).
2. Mean-reversion half-lives and jump or kurtosis estimates for NBP and GB power.
3. Official annual day-ahead base and peak 2016-2019 and 2022-2023 (N2EX/EPEX).
4. Share of days with NBP and GB power curves in backwardation; slope regressed on spot.
5. Clean spark and dark spreads by year 2016-2025 at 49.13%, with the share of negative days.
6. A GB daily gas-power correlation and a price-per-GW-of-wind elasticity.
7. RMSE of NBP and GB power forwards against outturn by horizon.
8. NBP annual averages 2022-2025 in p/th from a primary source.
9. **New, from the code read:** a daily NBP (or at least daily TTF plus daily FX) history for the
   world's own replay. Until it exists, the world's gas price cannot be graded at any scale below a
   month, and neither can any forward generator fitted to it.

## 10. The measurement script (read-only; run from the repo root)

```python
"""Re-runnable: realised statistics of the price record the world replays (read-only)."""
import collections, json, math, statistics as st, sys, csv
sys.path.insert(0, ".")
from sim.cache_store import CACHE_DIR
recs = json.load(open(CACHE_DIR / "elexon_ssp_full.json"))
print("SSP records", len(recs), recs[0], recs[-1])
day = collections.defaultdict(list)
for r in recs:
    day[r["settlementDate"]].append(float(r["systemSellPrice"]))
days = sorted(day)
dm = {d: st.mean(day[d]) for d in days}
by = collections.defaultdict(list)
for d in days: by[d[:4]].append(d)
print("year mean_daily  sd_daily  neg_halfhours  max_hh  hh>500  mean_daily_swing")
for y in sorted(by):
    ds = by[y]; vals = [dm[d] for d in ds]
    hh = [p for d in ds for p in day[d]]
    sw = st.mean(max(day[d]) - min(day[d]) for d in ds)
    print(y, round(st.mean(vals), 1), round(st.pstdev(vals), 1), sum(p < 0 for p in hh), round(max(hh)), sum(p > 500 for p in hh), round(sw, 1))
# gas: monthly-flat series
rows = list(csv.DictReader(open("sim/gas_data/nbp_sap.csv")))
g = [float(r["systemSellPrice"]) for r in rows]
moves = sum(1 for i in range(1, len(g)) if g[i] != g[i-1])
print("gas days", len(g), "days on which price moves", moves)
```

## Second read: the advisor's verification pass, 25 Oct 2026

The advisor read two of the tags independently (`docs/staging/advisor/DIRECTOR_EVIDENCE_VERIFICATION_OF_THE_GB_PACKS_UNVERIFIED_ITEMS_2026-10-25.md`, pass 3, pack 7). Rows not listed were not in its scope; their outcomes stand.

| Item | Prior outcome | Advisor | Reconciled | Source |
|---|---|---|---|---|
| TTF/NBP realised vol > 100% annualised in 2022 | still open | still open: a 2021 options review charts implied vol on a 0–160% axis, no readable values | **still open** | https://commodityvol.com/aux/doc/w9Et788A/WEBSCROLL/UjpK6ECp/YearEnd2021.pdf |
| NBP crisis peak 10–25× pre-crisis average | still open (baseline unverified) | confirmed: about 19× [derived] | **confirmed** [derived]. Both inputs are already confirmed on this page: EnAppSys's £14.24/MWh (≈41.7 p/th) and the 800 p/th front-month print. Mixed basis (front-month over spot), so 19× is a ratio of a print to a mean, not of like series | https://www.enappsys.com/wp-content/uploads/2023/01/2021_Annual_Market_Summary_GB.pdf |

**Counts: confirmed 8 · corrected 0 · still open 4.**
