# EU-ETS / UK-ETS allowance price series + EUR/GBP FX — sourcing report

**domain**: policy_costs
**assumption_tested**: `sim/merit_order_reconstruction.py`'s `ets_price_gbp_per_tonne` defaults to 0.0 (a named gap); only the flat Carbon Price Support (~GBP 18/tCO2) is currently priced into the SRMC stack. This assumption-check asks: can a real, citable, published EUA/UKA allowance price series be sourced to fill that gap, rather than backing the number out of price residuals (forbidden under R12/R13)?
**date**: 2026-08-03
**confidence**: H for the EU-ETS (EUA) series and the ECB FX series (both primary, machine-read from the actual downloaded files). M for the UK-ETS series (primary/official gov.uk source, but see the methodology caveat below — it is a statutory forward-referencing figure, not a same-year spot/auction average).

## Result: SUCCESS (with one important caveat on the UK-ETS numbers — read the caveat before using them)

Three real, fetched, citable series were obtained:
1. EU ETS (EUA) annual auction-clearing-price average, 2016–2024, EUR/tCO2 — computed directly from EEX's own downloadable primary-auction report files (daily auction data, volume-weighted).
2. UK ETS statutory "carbon price for civil penalties", 2021–2025, GBP/tCO2 — read directly off five separate gov.uk determination pages (DESNZ/UK ETS Authority).
3. EUR→GBP annual average exchange rate, 2016–2024 — computed directly from the ECB's official daily reference-rate dataset (fetched via the ECB Data Portal API).

No number below was estimated, interpolated, or recalled from training data. Every figure is either (a) a volume-weighted average computed in this session directly from a primary-source file fetched in this session, or (b) a number read verbatim off a fetched official government/ECB page. Where I "already knew" a ballpark from training data (e.g. that EUA averaged roughly EUR 5 in 2016), I did NOT use that memory as the source — I only report the number that came out of the fetched EEX file, and note where it happens to agree with prior general knowledge purely as a plausibility remark, never as the evidentiary basis.

---

## PROBE LOG

All probes below were made with `curl` and a normal browser `User-Agent` header on 2026-08-03, network confirmed available.

| # | URL | HTTP status | Outcome |
|---|-----|------|---------|
| 1 | `https://www.eex.com/en/market-data/environmental-markets/eua-primary-auction-spot-download` | 301 | Redirects to `/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download` |
| 1b | `https://www.eex.com/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download` | 200 | Landing page; contains a link to a bundled archive zip covering 2012–2025 |
| 1c | `https://www.eex.com/fileadmin/EEX/Downloads/Markets/Environmentals/EUA_Emission_Spot_Primary_Market_Auction_Report/Archive_Reports/emission-spot-primary-market-auction-report-2012-2025-data.zip` | 200 | **SUCCESS.** 784,392-byte zip containing one .xls (2012-2019, BIFF/OLE2 format) or .xlsx (2020-2025) file per year, each with a `Primary Market Auction` sheet: one row per daily EUA primary auction, columns `Auction Price EUR/tCO2` (or `€/tCO2` in later years), `Auction Volume (tCO2)`, bidder/revenue stats. This is EEX's own primary-market data, the platform on which the EU Emissions Trading System allowances are actually auctioned. |
| 2 | `https://climate.ec.europa.eu/eu-action/eu-emissions-trading-system-eu-ets_en` | 301 | Redirected; did not pursue further once the EEX raw-data source above was in hand (a Commission narrative "Carbon Market Report" PDF would only ever restate the same auction-clearing prices, so it was deprioritised once the primary auction data itself was obtained) |
| 3 | `https://sandbag.be/carbon-price-viewer/` | 200 | Page loads but is a JS-rendered chart widget; no CSV/JSON/XLSX download link found in the static HTML (`wp-json` REST links present but only serve page metadata, not price data). **No usable data extracted.** |
| 4 | `https://ember-energy.org/data/carbon-price-viewer/` | 301 | Redirects to `https://ember-energy.org/data/european-electricity-prices-and-costs/` |
| 4b | `https://ember-energy.org/data/european-electricity-prices-and-costs/` | 200 | Page loads; grepped for csv/xlsx/download links — none found in static HTML. Likely served via a JS data explorer with no static export link. **No usable data extracted.** |
| 5 | `https://carbonpricingdashboard.worldbank.org/` | 403 | Blocked even with a normal browser User-Agent. **Failed.** |
| 6 | `https://www.gov.uk/government/publications/uk-ets-auction-results` (guessed slug) | 404 | Wrong slug — not a real page |
| 6b | `https://www.gov.uk/search/all?keywords=UK+ETS+auction+results&order=relevance` | 200 | Search results surfaced the real page: `government/publications/determinations-of-the-uk-ets-carbon-price` |
| 6c | `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price` | 200 | **SUCCESS.** Index page listing 5 dated determination sub-pages (2021&2022, 2023, 2024, 2025, 2026), each a DESNZ/UK ETS Authority statutory publication under the Greenhouse Gas Emission Trading Scheme Order 2020 |
| 6d | `.../uk-ets-carbon-prices-for-use-in-civil-penalties-2021-and-2022` | 200 | **SUCCESS** — see table below |
| 6e | `.../uk-ets-carbon-prices-for-use-in-civil-penalties-2023` | 200 | **SUCCESS** |
| 6f | `.../uk-ets-carbon-prices-for-use-in-civil-penalties-2024` | 200 | **SUCCESS** |
| 6g | `.../uk-ets-carbon-prices-for-use-in-civil-penalties-2025` | 200 | **SUCCESS** (bonus, outside the requested 2021-2024 window) |
| 7 | `https://icapcarbonaction.com/en/ets-prices` | 200 | Page loads but chart is client-side JS rendered; no JSON/CSV/API link found in the static HTML. **No usable data extracted.** |
| 8 | `https://www.bankofengland.co.uk/boeapps/database/` | 200 | Landing page for the BoE "Statistical interactive database"; no direct link found to a EUR/GBP CSV export |
| 8b | `https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes&SeriesCodes=XUDLERS&CSVF=TN&UsingCodes=Y` | 200 | Returned an HTML page, not a CSV (endpoint/parameters likely stale or require a session/POST flow). **Abandoned** in favour of the ECB source below, which worked cleanly. |
| 8c | `https://www.bankofengland.co.uk/boeapps/database/FromShowColumns.asp?csv.x=yes&SeriesCodes=XUDLERS&CSVF=TN&UsingCodes=Y` | 200 | Same — HTML, not CSV. **Failed.** |
| 9 | `https://data-api.ecb.europa.eu/service/data/EXR/D.GBP.EUR.SP00.A?format=csvdata&startPeriod=2016-01-01&endPeriod=2024-12-31` | 200 | **SUCCESS.** ECB Data Portal API, official ECB reference-rate series `EXR.D.GBP.EUR.SP00.A` ("Pound sterling/Euro ECB reference exchange rate"), full daily series 2016-01-04 through 2024-12-31 fetched (2,305 daily observations), used in place of the BoE database. |
| 10 | `https://ourworldindata.org/grapher/carbon-prices.csv` | 404 | Wrong/guessed slug |
| 10b | `https://ourworldindata.org/grapher/carbon-price.csv` | 404 | Wrong/guessed slug |
| 10c | `https://ourworldindata.org/carbon-pricing` | 200 | Page loads (article page), not pursued further for a downloadable series once the EEX primary data was already in hand |

---

## 1. EU ETS — EUA annual auction-clearing price, 2016-2024

**Source**: EEX (European Energy Exchange) — "Emission Spot Primary Market Auction Report", the EEX's own bundled 2012-2025 archive.
**URL**: `https://www.eex.com/fileadmin/EEX/Downloads/Markets/Environmentals/EUA_Emission_Spot_Primary_Market_Auction_Report/Archive_Reports/emission-spot-primary-market-auction-report-2012-2025-data.zip` (retrieved via `https://www.eex.com/en/market-data/market-data-hub/environmentals/eex-eua-primary-auction-spot-download`)
**Retrieved**: 2026-08-03
**Method**: for each year's file, every daily auction row's `Auction Price` (EUR/tCO2) was volume-weighted by that day's `Auction Volume` (tCO2) to give the annual VWAP. This is EEX's own raw per-auction data — nothing here is a secondary aggregator.
**Caveat**: this is the **primary auction clearing price** (what buyers actually paid at EEX's daily EUA auctions), not a continuous secondary-market spot/futures price. EEX states EU ETS primary auctions are priced off — and track very closely — the secondary market (ICE EUA futures), so this VWAP is a reasonable and directly-evidenced proxy for the year's average EUA price, but it is not literally "the EUA spot price" — it is the auction-clearing price, a documented distinction.

| Year | VWAP (EUR/tCO2) | Simple daily average (EUR/tCO2) | # daily auctions |
|------|------------------|----------------------------------|-------------------|
| 2016 | 5.26 | 5.25 | 195 |
| 2017 | 5.79 | 5.80 | 206 |
| 2018 | 15.34 | 15.56 | 209 |
| 2019 | 24.65 | 24.72 | 216 |
| 2020 | 24.51 | 24.37 | 217 |
| 2021 | 52.93 | 54.13 | 230 |
| 2022 | 79.74 | 80.18 | 220 |
| 2023 | 83.24 | 83.60 | 223 |
| 2024 | 64.74 | 64.76 | 221 |

(2021-2024 EUA figures are included above for context/continuity even though the UK left the EU ETS scheme after 2020 — the EUA price remains relevant as the reference for EU-side wholesale power price formation and as a comparator to the UK's own scheme below.)

## 2. UK ETS — statutory carbon price for civil penalties, 2021-2025

**Source**: gov.uk, "Determinations of the UK ETS carbon price" (Department for Energy Security & Net Zero / UK ETS Authority), published under Article 46 of the Greenhouse Gas Emission Trading Scheme Order 2020.
**URLs** (one per year, each fetched and read directly):
- 2021 & 2022: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2021-and-2022`
- 2023: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2023`
- 2024: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2024`
- 2025: `https://www.gov.uk/government/publications/determinations-of-the-uk-ets-carbon-price/uk-ets-carbon-prices-for-use-in-civil-penalties-2025`
**Retrieved**: 2026-08-03

| "Scheme year" | Statutory carbon price (GBP/tCO2) | How the Authority calculated it (verbatim from the notice) |
|---|---|---|
| 2021 | £47.96 | Volume-weighted average **auction clearing price** of all UK ETS primary auctions held 1 Jan–11 Nov 2021 (Article 46(2)-(3)) — this one IS contemporaneous with 2021 itself. |
| 2022 | £52.56 | Average end-of-day **settlement price of the Dec-2022 UKA futures contract**, as traded 1 Jan–11 Nov **2021** (Article 46(4)-(6)) |
| 2023 | £83.03 | Average end-of-day settlement price of the Dec-2023 UKA futures contract, as traded during the 12 months ending 11 Nov **2022** |
| 2024 | £64.90 | Average end-of-day settlement price of the Dec-2024 UKA futures contract, as traded during the 12 months ending 11 Nov **2023** |
| 2025 | £41.84 | Average end-of-day settlement price of the Dec-2025 UKA futures contract, as traded during the 12 months ending 11 Nov **2024** |

**CRITICAL METHODOLOGY CAVEAT — read before using these numbers in the SRMC stack:**
Only the 2021 figure is a same-year, contemporaneous average (it is literally "the average UK ETS auction price during 2021"). From 2022 onward, the Order's formula is explicitly **forward-referencing**: the number labelled "carbon price for scheme year N" is the average **traded price of the December-N-vintage futures contract, observed during trading in year N-1** (roughly 12 months ending 11 November of the PRIOR year). That means:
- The figure labelled "2023" (£83.03) reflects futures trading that happened mostly during **2022**, for December-2023 delivery — it is a forward price observed in 2022, not the spot/auction price actually paid during 2023.
- Likewise "2024" (£64.90) reflects trading mostly during **2023**.
- This is a genuine statutory quirk (Article 46(4)-(6) of the 2020 Order), not a data error, and it is stated explicitly in each notice.

**Recommendation, stated not applied**: if `merit_order_reconstruction.py` wants a same-calendar-year UK carbon price, the year-labelled civil-penalty figures should NOT be applied directly year-for-year without accounting for this one-year forward-reference lag — doing so naively would misalign the carbon cost with the calendar year it's meant to represent. I have not attempted to re-derive or shift these figures onto a "true 2022/2023/2024 spot" basis myself, since that would require either (a) finding UK ETS's own primary auction data (which the EEX platform does not host — UK ETS auctions run on ICE Futures Europe, confirmed by the EEX UK ETS page linking out to ICE-style secondary market references and having no UKA auction-report download of its own) or (b) inferring/interpolating, which is forbidden. This is flagged as an open gap for the SIM/harness team to decide how to treat, not resolved here.

## 3. EUR → GBP annual average exchange rate, 2016-2024

**Source**: European Central Bank (ECB) Data Portal — official daily reference exchange rate series `EXR.D.GBP.EUR.SP00.A` ("Pound sterling/Euro ECB reference exchange rate, 2.15pm C.E.T.")
**URL**: `https://data-api.ecb.europa.eu/service/data/EXR/D.GBP.EUR.SP00.A?format=csvdata&startPeriod=2016-01-01&endPeriod=2024-12-31`
**Retrieved**: 2026-08-03
**Method**: simple mean of all daily reference-rate observations (255-258 trading days per year) within each calendar year. Units: GBP per 1 EUR.

| Year | Annual average GBP per EUR | # daily obs |
|------|------------------------------|--------------|
| 2016 | 0.8195 | 257 |
| 2017 | 0.8767 | 255 |
| 2018 | 0.8847 | 255 |
| 2019 | 0.8778 | 255 |
| 2020 | 0.8897 | 257 |
| 2021 | 0.8596 | 258 |
| 2022 | 0.8528 | 257 |
| 2023 | 0.8698 | 255 |
| 2024 | 0.8466 | 256 |

To convert the EU-ETS EUR/tCO2 series to GBP/tCO2 (context only — the EU-ETS figures above are not UK-applicable post-2020), multiply by the year's rate, e.g. 2016: 5.26 x 0.8195 ≈ GBP 4.31/tCO2; 2019: 24.65 x 0.8778 ≈ GBP 21.64/tCO2.

---

## Action warranted (recorded, not applied — this is a discovery-agent finding, not a code change)

- `sim/merit_order_reconstruction.py`'s `ets_price_gbp_per_tonne` defaulting to 0.0 for 2016-2017 (when EUA/UKA-equivalent carbon prices were genuinely low, ~EUR 5/tCO2 ≈ GBP 4/tCO2) is closer to reality than a flat CPS-only assumption in those years, but is not zero — a GBP 4-5/tCO2 EU-ETS-equivalent cost existed on top of the flat GBP 18/tCO2 CPS even then. For 2018-2020 the EUA gap is much larger (GBP ~13-22/tCO2 on top of CPS), which is where the reconstruction is most likely to overshoot low-carbon-year SRMC as the gap note predicted.
- For 2021 the UK-specific, same-year, primary-sourced figure is GBP 47.96/tCO2 (auction clearing price average) — this is the cleanest single number to slot in for 2021.
- For 2022-2024 the labelled UK civil-penalty figures (52.56 / 83.03 / 64.90) exist and are officially published, but carry the one-year forward-reference caveat above; whoever wires this into the SRMC stack needs to decide explicitly how to handle that lag (e.g., apply the "2023" figure to actual 2022 trading-year costs, or accept the mismatch as a known simplification) — this is a genuine open design question, not something this discovery task should resolve unilaterally.
