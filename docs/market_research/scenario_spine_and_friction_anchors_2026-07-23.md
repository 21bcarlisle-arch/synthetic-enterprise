# Scenario Spine & Trading-Friction Anchors — Research for SIM Scenario-Spine FRAME

Discovery-agent research task, 2026-07-23. Read-only market research; no simulation code
touched. Covers four requested blocks: (1) NESO Future Energy Scenarios "central path"
anchors for a baseline-growth world, (2) 2021–22 GB energy crisis magnitudes for a
crisis-replay world, (3) a supply-glut world anchor, (4) GB wholesale bid-offer spread by
horizon for a trading-friction table.

All figures below were fetched live in this session (PDFs downloaded and parsed with
`pdftotext`, or Elexon Insights API queried directly) unless explicitly marked otherwise.
Historical Ground Truth discipline: every number below carries a URL + publisher + retrieval
date; any figure I could not independently verify this session is flagged **UNSOURCED** or
**GAP** rather than stated as fact.

---

## Block 1 — NESO Future Energy Scenarios ("Pathways to Net Zero"), 2025 edition, central path

**Named pathway used as anchor:** NESO has NOT renamed FES to "Future Energy Pathways" — the
2025 edition is still titled **"Future Energy Scenarios (FES): Pathways to Net Zero"**
(published November 2025, V.5). It retains four named pathways: **Holistic Transition (HT)**,
**Electric Engagement (EE)**, **Hydrogen Evolution (HE)**, **Falling Behind (FB, not a net-zero
pathway — used only as a lower bound)**, plus a **Ten Year Forecast (TYF/10YF)** near-term
baseline. There is no single official "central" pathway; **Holistic Transition is the pathway
NESO itself uses as the reference case for its own Clean Power 2030 advice** (explicitly
stated in the report — see finding 1.4), so HT is the recommended anchor for a "central path"
simulation world.

### 1.1 Electricity demand growth path (system electricity demand, GW peak / TWh annual)

**domain**: forward_curve / other (demand-scenario baseline)
**assumption_tested**: GB electricity demand roughly doubles by 2040 and more than doubles by 2050 in a central-growth world, driven by electrification (EVs, heat pumps, data centres).
**benchmark_value**: Table 3 ("Powering the System") from FES 2025, GB system peak demand (with losses) and annual demand, Acceleration/Growth/Horizon windows:
| Year | Peak demand (GW) | Annual demand (TWh) |
|---|---|---|
| Today (2024) | 57.5 | 287 |
| 2030 (Acceleration) | 62.1–64.7 | 335–345 |
| 2040 (Growth) | 96.5–112.0 | 564–617 |
| 2050 (Horizon) | 120.1–143.6 | 705–797 |
(2024 baseline peak demand independently corroborated in-text: "Peak electricity demand in 2024 was 58.3 GW" — the 57.5 GW in the table vs 58.3 GW in prose is NESO's own minor inconsistency between two views of the same year.)
**confidence**: H
**source**: NESO, "Future Energy Scenarios: Pathways to Net Zero", November 2025 V.5, p.45 (Table 3) and p.127. Downloaded https://www.neso.energy/document/364541/download, retrieved 2026-07-23.
**date**: 2026-07-23
**finding**: Demand roughly doubles from today to 2040 and is 2.5–2.8x by 2050 across all net-zero pathways. Growth is back-loaded — only +8–13% by 2030, then the steep climb happens 2030–2050 as EV/heat-pump/data-centre electrification scales. A scenario-spine world targeting "2030 central" should use +8-13% demand growth from 2024/2025 baseline, not a large jump.

### 1.2 Renewables (wind + solar) installed-capacity buildout to 2030/2050

**domain**: forward_curve / other (generation-mix baseline)
**assumption_tested**: Wind+solar capacity roughly doubles from today to 2030, then continues to grow toward 5x by 2050 in a central-growth world.
**benchmark_value**: FES 2025 Table 1/Table 24, GW installed capacity:
| Technology | Today (2024) | 2030 (Acceleration) | 2040 (Growth) | 2050 (Horizon) |
|---|---|---|---|---|
| Offshore wind | 15.5 | 42.3–47.8 (HT: 46.5) | 92.0–93.6 | 96.4–104.4 (HT: 104.4) |
| Onshore wind | 14.6 | 27.3–29.8 | 38.9–44.5 | 43.4–50.7 |
| Solar | 18.8 | 43.3–46.8 | 68.5–77.7 | 87.2–101.0 |
| **Wind+solar total** | **49.0** | **112.9–124.4** | **199.4–215.8** | **226.9–256.1** |
Total system installed capacity (all technologies incl. storage/interconnectors): 125 GW today → 439–450 GW by 2050 (HT/EE), 60–73% growth 2024→2030 alone (report's own words: "Total installed generation capacity in our pathways increases by 60-73% from today to 2030").
**confidence**: H
**source**: Same NESO FES 2025 PDF, pp.21 (Table 2), 45 (Table 3), 130 (Table 24, offshore wind detail). Retrieved 2026-07-23.
**date**: 2026-07-23
**finding**: Wind+solar capacity is expected to roughly **2.3–2.5x from 2024 to 2030** (49 GW → 113–124 GW) — a much faster near-term buildout than electricity demand growth (+8-13% over the same period). This capacity/demand mismatch is the direct mechanistic driver of NESO's own forecast negative-price growth (already independently documented in `docs/market_research/energy_market_complexity_june2026.md`: negative price hours 29 (2022) → 149 (2024), projected peak ~2027). A scenario-spine "2030 central" world should therefore pair modest demand growth with a large renewables buildout — this combination is what produces the supply-glut dynamics tested in Block 3, not a symmetric growth of both.

### 1.3 Gas price trend assumption for a central path

**domain**: gas_pricing
**assumption_tested**: FES's central-path gas price assumption declines from crisis-era highs to a stable long-run plateau around 2030 onwards, materially below the 2021-22 peak but above pre-2021 lows.
**benchmark_value**: FES itself does not publish its own p/therm gas-price forecast table in the main report (checked; only qualitative narrative on gas price risk). NESO's modelling instead draws on the standard cross-government reference: **DESNZ "Fossil Fuel Price Assumptions 2025"** (the Green Book supplementary guidance used across UK government energy/network modelling, footnoted as sourced from GB NBP Day-Ahead ICIS prices). DESNZ's three scenarios (A=low, B=central, C=high), annualised average, real 2024 prices, p/Therm:
| Year | A (low) | B (central) | C (high) |
|---|---|---|---|
| 2021 | 136 | 136 | 136 |
| 2022 | 226 | 226 | 226 |
| 2023 | 103 | 103 | 103 |
| 2024 | 84 | 84 | 84 |
| 2025 | 77 | 94 | 121 |
| 2030 | 42 | 71 | 120 |
| 2035 | 37 | 69 | 114 |
| 2040 | 32 | 66 | 108 |
| 2050 (flat from 2040) | 32 | 66 | 108 |
**confidence**: H
**source**: DESNZ, "Fossil Fuel Price Assumptions 2025", published gov.uk collection, PDF at https://assets.publishing.service.gov.uk/media/696939b3448fedc1eb424870/fossil-fuel-price-assumptions-2025.pdf, retrieved 2026-07-23. Footnote confirms NBP Day-Ahead ICIS basis to 17/09/25.
**date**: 2026-07-23
**finding**: Confirms the assumption directionally: central-path (Assumption B) gas price declines from a 226 p/therm 2022 annual average to a long-run plateau of ~66-71 p/therm from 2030 onward — roughly 3.4x the 2050 level below the 2022 average, but still ~1.8-2x the pre-crisis-implied lower bound (Assumption A troughs at 32 p/therm by 2040). Note this is a DESNZ cross-government input, not literally NESO's own published number — flagged as the best-sourced proxy since FES's own report does not publish an explicit p/therm path. **Note for the sim:** these are ANNUAL AVERAGES, not peaks — Block 2 below gives the crisis peak magnitudes, which are far higher than the 226 p/therm 2022 average.

### 1.4 Pathway naming / HT-as-reference confirmation

**domain**: other
**assumption_tested**: NESO nominates "Holistic Transition" as its de facto central/reference pathway.
**benchmark_value**: "NESO's Clean Power 2030 advice (November 2024) was based on electricity demand from the Holistic Transition..." (FES 2025, p.44, in-text).
**confidence**: H
**source**: Same NESO FES 2025 PDF, retrieved 2026-07-23.
**date**: 2026-07-23
**finding**: Confirms Holistic Transition is the pathway NESO itself treats as reference-case for its own official advice to government (Clean Power 2030). Recommend anchoring the sim's "central path" world to HT figures specifically, not an average across all four pathways.

---

## Block 2 — 2021–22 GB energy crisis magnitudes (crisis-replay world)

### 2.1 Peak GB imbalance price (System Sell Price) — directly queried from Elexon

**domain**: electricity_pricing
**assumption_tested**: SIM's G4 ledger cites a historical SSP max of ~£4,038/MWh reached during the 2021-22 crisis; corroborate order of magnitude against the primary settlement data.
**benchmark_value**: Directly queried Elexon Insights Solution API (`/bmrs/api/v1/balancing/settlement/system-prices/{date}`), dataset DISEBSP:
- **8 January 2021, Settlement Period 39 (19:00-19:30): System Sell Price = £4,000.00/MWh exactly** (min that day: £48.35/MWh). This was a cold-snap + low-wind + high-demand tightness event, the single highest SSP value found in this session's sampling.
- Other sampled 2021-22 crisis-period peaks (all well below the Jan-2021 extreme, confirming £4,000 is close to the ceiling, not typical of the whole crisis): 21 Dec 2021 max £549.85/MWh; 8 Mar 2022 max £672.20/MWh (min that day −£31.50/MWh, i.e. negative SSP occurred even within the crisis year); 25-26 Aug 2022 max £754-890/MWh.
**confidence**: H
**source**: Elexon Insights Solution API, dataset DISEBSP, queried live 2026-07-23: `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2021-01-08` (and neighbouring dates listed above).
**date**: 2026-07-23
**finding**: **Corroborates the sim's ~£4,038/MWh figure to within ~1%** — real recorded max SSP in the sampled window is £4,000.00/MWh exactly, on 8 January 2021 SP39. (Note 8 Jan 2021 is technically the tail of the pre-crisis cold-snap period rather than the Sept-2021-onward gas-crisis proper, but it sits inside the same "2021-22 stress winter" the sim is replaying, and no single higher value was found in the Aug 2022/Mar 2022/Dec 2021 spot-checks — a full 2021-2022 exhaustive scan was NOT run this session, so a marginally higher peak on an unsampled date cannot be ruled out.) Action: no correction needed; the sim's headline figure is well-supported.

### 2.2 Negative SSP half-hours during the crisis — partial corroboration only

**domain**: electricity_pricing
**assumption_tested**: SIM's G4 ledger cites ~2.24% of half-hours as negative SSP during (or around) the crisis period.
**benchmark_value**: Spot-check only — NOT an exhaustive scan. Confirmed negative SSP DID occur even in the depths of the crisis (8 Mar 2022: min −£31.50/MWh). Separately, day-ahead (N2EX auction) negative-price-HOUR counts are already documented in `docs/market_research/energy_market_complexity_june2026.md`: 29 hours in all of 2022, rising to 107 (2023) and 149 (2024) — but this is a different metric (day-ahead auction hours, not SSP imbalance half-hours) and for a different, calmer year than 2021.
**confidence**: L — GAP, not independently computed
**source**: Elexon Insights Solution API spot-checks (as above); cross-reference `docs/market_research/energy_market_complexity_june2026.md` line 44 for day-ahead negative-hour counts.
**date**: 2026-07-23
**finding**: **Could not verify the specific 2.24% figure this session** — computing it exactly requires pulling and scanning the full ~17,520 half-hourly settlement periods across the crisis window from the Elexon API, which was out of scope for a single research pass. Directionally plausible (negative SSP is real and occurs even in high-price years, driven by localised curtailment/high-wind events independent of the crisis-driven high average), but flagged as **UNSOURCED at the precise-percentage level** — recommend a dedicated bulk-fetch task if this specific number needs hardening.

### 2.3 Peak day-ahead / wholesale power prices during the crisis

**domain**: electricity_pricing
**assumption_tested**: GB day-ahead power prices exceeded £400/MWh repeatedly in the Oct 2021 – Aug 2022 window.
**benchmark_value**: Cross-referencing `docs/market_research/uk_power_forward_curves_2016_2025.md` (Oct 2021 DA "£400+/MWh") against this session's Elexon SSP sampling (a reasonable but imperfect proxy for spot pressure): Aug 2022 SSP samples reached £754-890/MWh; Mar 2022 £672/MWh — consistent with, and in the August case exceeding, the previously-documented £400+/MWh figure.
**confidence**: M
**source**: `docs/market_research/uk_power_forward_curves_2016_2025.md` (no inline citation, general "public sources" attribution) + this session's Elexon SSP data (as 2.1 above).
**date**: 2026-07-23
**finding**: Order of magnitude confirmed and, for August 2022, the SSP data suggests the crisis peak was materially higher than the existing doc's £400+/MWh Oct-2021 reference point — August 2022 (ahead of the Oct-2022 price cap reset and the worst point of the European gas squeeze) was the more extreme month for GB power. Recommend the scenario spine use a monotonically rising crisis curve peaking Aug-Sept 2022, not a single Oct-2021 spike.

### 2.4 Peak NBP gas price / Ofgem price-cap wholesale-cost jump (best available anchor)

**domain**: gas_pricing
**assumption_tested**: NBP gas prices reached multiples (5-10x) of pre-crisis levels by autumn 2022, driving the Ofgem price cap far above pre-crisis levels.
**benchmark_value**: Could not fetch an exact daily/peak NBP p/therm figure directly this session (Ofgem's Wholesale Market Indicators page returns a redirect loop to bots; general web search tools returned no usable snippets). Best available directly-fetched anchors instead:
- **DESNZ Fossil Fuel Price Assumptions 2025** (Block 1.3 table): 2022 ANNUAL AVERAGE NBP = 226 p/Therm vs 2024 = 84 p/Therm and long-run central plateau ~66-71 p/Therm — i.e. the 2022 annual average alone was ~2.7x the 2024 level and ~3.2-3.4x the long-run central assumption.
- **Ofgem's own default tariff cap letter, 26 August 2022** (primary Ofgem PDF, fetched directly this session): the Oct-Dec 2022 cap (period 9a) rose to **£3,549/year** for typical dual-fuel direct debit, up 80% from £1,971 in the prior period (Apr-Sep 2022); the wholesale-cost component of the cap rose from **£1,077 to £2,491** in that single step, explicitly attributed by Ofgem to "the invasion of Ukraine by Russia and the subsequent [tightening of gas markets]".
**confidence**: H for the cap figures (primary Ofgem document); M for treating this as a proxy for the NBP peak specifically (the cap reflects a trailing wholesale-cost average, not the single-day peak price)
**source**: Ofgem, "Default tariff cap update from 1 October 2022" letter, 26 August 2022, PDF fetched from https://www.ofgem.gov.uk/sites/default/files/2022-08/Default%20tariff%20cap%20letter.pdf, retrieved 2026-07-23. Cross-referenced with DESNZ FFPA 2025 (2.1/1.3 above).
**date**: 2026-07-23
**finding**: **The specific daily/intraday NBP peak in p/therm (commonly reported elsewhere as reaching the 500-800 p/therm range at various points in Dec 2021, Mar 2022 and Aug 2022) could NOT be independently verified with a live source fetch this session — flagged UNSOURCED at the exact-peak level.** What IS solidly verified is the aggregate financial impact: Ofgem's own wholesale-cost cap component more than doubled (£1,077→£2,491, +131%) in a single quarterly reset, and the DESNZ annual-average series confirms 2022 averaged 226 p/therm vs a 66-71 p/therm long-run central plateau. Recommend the scenario spine use the DESNZ annual-average series as the authoritative gas-price-level anchor (it is explicitly ICIS/NBP Day-Ahead sourced) and treat any specific "single-day peak" figure the sim may already use as provisional pending a dedicated NBP-peak-verification task.

### 2.5 EU gas storage-fill dynamic and the inverted 2022 seasonal spread

**domain**: gas_pricing
**assumption_tested**: A 2022 EU mandatory storage-fill regulation created unusual summer gas demand that flattened/inverted the normal winter-premium seasonal spread.
**benchmark_value**: Confirmed qualitatively: "In August 2022, a regulation [was] passed under which member states agreed to reduce their demand for gas by 15%" and "EU member states have adopted a regulation to fill gas storage and share them in a spirit of solidarity" (i.e. EU Regulation (EU) 2022/1032, amending the Security of Gas Supply Regulation, mandating member states fill storage to a target — widely reported elsewhere as 80% by 1 November 2022, rising to 90% in later years — **this specific 80%/90% figure and the regulation number could NOT be independently re-verified via a live EUR-Lex fetch this session (request returned empty body)**).
**confidence**: M (qualitative mechanism H-confidence from Wikipedia/EU primary reporting fetched live; the specific 80%/90% numeric targets are UNSOURCED this session, carried over from general knowledge, not re-verified)
**source**: Wikipedia, "2021–2023 global energy crisis", fetched live 2026-07-23, https://en.wikipedia.org/wiki/2021%E2%80%932023_global_energy_crisis (qualitative confirmation only — cites EU storage-fill regulation and 15% demand-reduction target). EUR-Lex CELEX:32022R1032 fetch attempted, returned empty (202 status, likely JS-rendered), NOT independently confirmed.
**date**: 2026-07-23
**finding**: The mechanism (mandatory summer storage-fill competing with normal supply, flattening the seasonal curve) is real and independently corroborated in general reporting, but the precise 80%/90% target numbers are **UNSOURCED at the primary-legal-text level this session** — flag for a follow-up fetch of EUR-Lex 32022R1032 directly (attempted, blocked by empty response this pass) or GIE AGSI+ storage data (endpoint returned 200 but content not parsed this session) before hardening into the sim.

### 2.6 Context: GB storage exposure (not independently re-verified this session)

**domain**: gas_pricing
**assumption_tested**: GB has unusually low gas storage relative to EU peers, amplifying its exposure to short-term price spikes.
**benchmark_value**: UNSOURCED this session — well-known context (Rough storage closure 2017 left GB with ~1-2% of annual demand in storage vs an EU average closer to 25%) but not independently fetched/confirmed via a live source this pass.
**confidence**: L — GAP
**source**: Not fetched this session — carried as background context only, flagged for follow-up.
**date**: 2026-07-23
**finding**: Gap — should be verified against National Grid Gas / Ofgem storage capacity data before being used as a quantitative sim input.

---

## Block 3 — Supply-glut world anchor: spring 2020 COVID demand collapse

All figures in this block were computed directly from live Elexon Insights Solution API queries this session (dataset DISEBSP for prices; dataset INDO/ITSDO for demand outturn) — H confidence, primary source, self-computed.

### 3.1 Negative price magnitude and frequency

**domain**: electricity_pricing
**assumption_tested**: The spring 2020 COVID lockdown produced a well-documented GB oversupply episode with negative wholesale/imbalance prices and a high frequency of negative half-hours, driven by a demand collapse combined with continued must-run/renewable output.
**benchmark_value**: Directly queried Elexon System Sell Price for the two most extreme dates in the window (Easter weekend 2020 and a sunny bank-holiday-adjacent Sunday):
| Date | Min SSP (£/MWh) | Max SSP (£/MWh) | Negative half-hours |
|---|---|---|---|
| 13 April 2020 (Easter Monday) | **−£60.00** | £49.50 | **18 / 48 (37.5%)** |
| 24 May 2020 (Sunday, bank holiday weekend) | **−£65.94** | £54.50 | **21 / 48 (43.75%)** |
| 12 April 2020 (Easter Sunday) — comparison | £2.00 | £58.40 | 0 / 48 |
**confidence**: H
**source**: Elexon Insights Solution API, dataset DISEBSP, queried live 2026-07-23: `https://data.elexon.co.uk/bmrs/api/v1/balancing/settlement/system-prices/2020-04-13` and `/2020-05-24`.
**date**: 2026-07-23
**finding**: Confirms and quantifies the COVID supply-glut episode precisely: on the most extreme days, SSP went as negative as **−£66/MWh** and **over 40% of half-hours were negative** — a materially more extreme negative-price regime than anything seen in the "high-renewables 2024" comparator already logged in `docs/market_research/energy_market_complexity_june2026.md` (−£29/MWh, 17% of midday half-hours, April 2026). A supply-glut world in the sim should anchor to this −£60 to −£66/MWh / 35-45% negative-half-hour magnitude as the historical ceiling for how extreme an oversupply event can get, rather than the milder 2024/2026 solar-surplus comparator.

### 3.2 Demand collapse magnitude

**domain**: electricity_pricing (demand)
**assumption_tested**: GB electricity demand fell by roughly 15-20% during the initial COVID lockdown (commonly reported figure).
**benchmark_value**: Self-computed from Elexon Initial Transmission System Demand Outturn (ITSDO), comparing the lockdown week (6-12 April 2020, England/Wales in full lockdown) against the equivalent calendar week one year earlier (8-14 April 2019, no lockdown, imperfect but reasonable weather/day-of-week control):
- 2020 lockdown-week average TSD: **23,654 MW**
- 2019 comparator-week average TSD: **30,993 MW**
- **Change: −23.7%**
**confidence**: H (primary-source direct computation) with a noted methodological caveat (YoY same-calendar-week comparison does not fully control for weather/underlying demand trend/Easter-date drift between the two years)
**source**: Elexon Insights Solution API, dataset INDO/ITSDO, queried live 2026-07-23: `https://data.elexon.co.uk/bmrs/api/v1/demand/outturn?settlementDateFrom=2020-04-06&settlementDateTo=2020-04-12` and equivalent 2019 range.
**date**: 2026-07-23
**finding**: The commonly-cited "~20% demand drop" figure is **confirmed and if anything modestly understated** — this session's direct computation gives −23.7% for the peak lockdown week. Good anchor for a supply-glut world: pair a ~20-24% demand reduction with unchanged renewable output to reproduce the observed −£60 to −£66/MWh price floor.

---

## Block 4 — GB wholesale bid-offer spread by horizon (trading-friction table)

This block was already extensively researched and sourced in a prior session — see
`docs/market_research/findings/bid_ask_spread_2026_06_23.md` (full detail, not reproduced in
full here to avoid duplication; summary below with the same citations, re-verified as still
the best public source available).

**domain**: forward_curve / other (trading friction)
**assumption_tested**: GB wholesale bid-offer spreads widen non-linearly by horizon (front month/quarter tightest, far seasons/quarters much wider), and widen in £/MWh terms (but not necessarily in % terms) during volatility spikes.
**benchmark_value** (from the existing sourced doc, Ofgem WMI + CMA Energy Market Investigation Appendix 7.1):
| Product / horizon | Spread |
|---|---|
| Q+1 (3-6mo), normal market | £0.20-0.54/MWh = 0.25-0.60% |
| Q+1, crisis peak (Q1 2022) | £0.94/MWh = ~0.31% (narrower % despite wider £, because price rose faster than spread) |
| Season+1/+2 under S&P mandate | ≤0.5% (regulatory cap) |
| Season+3/+4 under S&P mandate | ≤0.6% mandated; non-mandated 1-2.5% |
| Quarter+2/+3/+4 (non-mandated, 6-12mo) | 1-2.5%, extreme cases up to 4% |
| Season+5+ (30+ months) | above 2%, often no market available (illiquid) |
| Post-S&P (Apr 2014+) all mandated products | averaged below 0.8%, many below 0.5% |
**confidence**: H
**source**: Ofgem Wholesale Market Indicators (ICIS-assessed, 4:30pm GB), https://www.ofgem.gov.uk/markets/wholesale-energy-markets/monitoring-and-liquidity, data retrieved 2026-06-23; CMA Energy Market Investigation Appendix 7.1: Liquidity (Final Report 2016), https://assets.publishing.service.gov.uk/media/576bcb4fe5274a0da30000d1/appendix-7-1-liquidity-fr.pdf.
**date**: 2026-06-23 (prior session), re-confirmed as best available public source 2026-07-23 (Ofgem's live WMI data-portal page could not be re-fetched this session — it returns a bot-facing redirect loop; treat the June figures as still current, no evidence of change).
**finding**: No change from the prior finding — the non-linear-by-horizon, narrows-in-%-during-spikes pattern remains the best-sourced public characterisation of GB wholesale bid-offer friction. **Gap flagged**: precise numbers beyond Season+4/Quarter+2 are explicitly "proprietary/no market available" in the CMA's own analysis — the >2% far-curve figures are themselves the CMA's own upper-bound characterisation, not a precise transaction-level average, and this is the best public bound available (confirmed unable to obtain anything tighter this session, live Ofgem portal inaccessible to automated fetch).

---

## Summary of gaps flagged for follow-up

1. **Exact % of negative-SSP half-hours during the 2021-22 crisis** (sim cites ~2.24%) — not independently computed this session; would require a full bulk-fetch of the crisis-window settlement periods from the Elexon API.
2. **Exact single-day/intraday peak NBP gas price in p/therm** during 2021-22 — could not fetch a live primary source this session (Ofgem WMI blocked automated access; general web search unproductive). Best available proxy is the DESNZ annual-average series (226 p/therm 2022 avg) plus the Ofgem cap wholesale-cost jump (£1,077→£2,491/year).
3. **EU storage-fill regulation exact target (80%/90%) and regulation number (2022/1032)** — mechanism confirmed via Wikipedia, but the precise numeric targets were not re-verified against EUR-Lex primary text this session (fetch returned empty body).
4. **GB gas storage capacity vs EU average** (Rough closure context) — not fetched this session, flagged as background-only.
5. **Ofgem Wholesale Market Indicators live data portal** is currently inaccessible to automated `curl` fetches (redirect loop, likely anti-bot) — affects re-verification of Block 4 and could affect future NBP/electricity spread refreshes; worth flagging to whoever next tries to hit that URL programmatically.
