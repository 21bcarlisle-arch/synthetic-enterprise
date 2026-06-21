# Source Guide — Authoritative Sources by Domain

Quality ratings: ★★★ primary/official data | ★★ secondary/analytical | ★ directional only

---

## Energy Consumption Data

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| DESNZ NEED Report | ★★★ | Residential gas + electricity medians, IQR, by property type. ~24M metered properties. England & Wales. | Annual (spring) | gov.uk search "National Energy Efficiency Data" |
| Ofgem TDCV Review | ★★★ | Regulatory typical consumption values: Low/Med/High bands for gas + electricity. Used in price cap. | As needed (2023, 2026) | ofgem.gov.uk "typical domestic consumption values" |
| EPC Open Register | ★★★ | 29.2M domestic + 2M non-domestic certs. Property type, floor area, energy intensity. | Monthly incremental | get-energy-performance-data.communities.gov.uk |
| DUKES (BEIS/DESNZ) | ★★★ | Digest of UK Energy Statistics — top-down national consumption totals | Annual (July) | gov.uk search "DUKES" |
| Bionic broker data | ★★ | SME electricity consumption by sector (based on contracts placed) | Annual | bionic.co.uk/business-energy/guides/ |

**Key caveat:** EPC `ENERGY_CONSUMPTION_CURRENT` overpredicts metered billing by 50–100%. Apply 0.65 correction. Source: ScienceDirect 2023 research.

---

## Regulatory and Ofgem Data

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Ofgem price cap | ★★★ | Cap formula components, quarterly rates, cost allowances | Quarterly | ofgem.gov.uk/energy-price-cap |
| Ofgem financial resilience | ★★★ | Capital floor/target requirements, ring-fencing rules | Ongoing | ofgem.gov.uk/financial-resilience |
| Elexon BSC documentation | ★★★ | BSC rules, imbalance pricing, credit cover, settlement mechanics | Continuous | bscdocs.elexon.co.uk |
| Elexon data portal | ★★★ | Half-hourly SSP/SBP prices, settlement data | Real-time | data.elexon.co.uk |
| RO buy-out price (Ofgem) | ★★★ | Annual Renewables Obligation level, buy-out price, mutualisation ceiling | Annual | ofgem.gov.uk search "RO buy-out price" |
| HoC Library briefings | ★★ | Policy summaries with cited statistics | As needed | commonslibrary.parliament.uk |
| Watt-Logic blog | ★★ | Deep technical analysis of UK energy regulation and supplier accounts. Author: Kathryn Porter. | Weekly | watt-logic.com |
| EMR Settlement | ★★★ | CfD levy rates, Capacity Market charges | Quarterly | emrsettlement.co.uk |

---

## Supplier Financial Data

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Companies House | ★★★ | UK supplier statutory accounts (P&L, balance sheet) | Annual (after filing) | companieshouse.gov.uk |
| Ofgem CSS | ★★★ | Consolidated Segmental Statements — mandatory profit/cost disclosure by fuel | Annual | ofgem.gov.uk/CSS |
| Octopus investor pages | ★★★ | Octopus group P&L, gross margin, customer count | Annual (FY results) | octopus.energy/press |
| Watt-Logic financial analysis | ★★ | OVO, British Gas, sector EBIT analysis with Ofgem data triangulation | As needed | watt-logic.com |
| Ofgem retail market indicators | ★★★ | Sector-wide EBIT, margin, customer switching, debt levels | Quarterly | ofgem.gov.uk/retail-market-indicators |

**Key caveat:** Statutory accounts distorted by IFRS 9 derivative MTM (OVO: ±£1bn swings). Always use "underlying EBIT" not statutory profit. Cross-reference with Ofgem CSS for consistency.

---

## Market Structure and Competition

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Ofgem retail market indicators | ★★★ | Supplier market shares, switching rates, complaint volumes | Quarterly | ofgem.gov.uk/retail-market-indicators |
| Ofgem domestic market report | ★★★ | Annual deep dive: competition, prices, consumer outcomes | Annual | ofgem.gov.uk/domestic-market-report |
| Energy UK | ★★ | Industry body publications, supplier landscape | Regular | energy-uk.org.uk |
| Which? supplier reviews | ★ | Customer satisfaction, directional only | Annual | which.co.uk |

---

## Customer Behaviour and Debt

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Citizens Advice energy reports | ★★ | Consumer debt, complaint volumes, vulnerable customers | Quarterly | citizensadvice.org.uk/energy |
| StepChange / National Energy Action | ★★ | Fuel poverty, debt volumes, payment plans | Annual | stepchange.org, nea.org.uk |
| Ofgem consumer vulnerability strategy | ★★★ | PSR obligations, payment difficulty requirements | Ongoing | ofgem.gov.uk/consumer-vulnerability |
| DESNZ smart meter statistics | ★★★ | Quarterly smart meter installation rates by segment | Quarterly | gov.uk search "smart meter statistics" |

---

## Weather and Climate Data

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Met Office HadUK-Grid | ★★★ | Historical UK temperature, wind, precipitation, 1km grid | Annual release | metoffice.gov.uk/hadobs/haduk-grid |
| Open-Meteo | ★★★ | Historical ERA5 weather data via API, no key required | Near real-time | open-meteo.com |
| NESO (National Energy System Operator) | ★★★ | Demand forecasts, wind generation, grid data | Real-time | neso.national.energy |

---

## Wholesale Market Data

| Source | Quality | What it covers | Update frequency | URL |
|--------|---------|---------------|-----------------|-----|
| Elexon Insights (SSP/SBP) | ★★★ | Half-hourly system sell/buy prices 2014-present | Daily | data.elexon.co.uk |
| ICE NBP gas prices | ★★★ | UK natural gas (National Balancing Point) spot + forward prices | Daily | theice.com (subscription) |
| NESO market data | ★★★ | Electricity forward curve, interconnector flows | Daily | neso.national.energy |
| Ofgem wholesale market reports | ★★ | Monthly wholesale gas + power price commentary | Monthly | ofgem.gov.uk |

---

## What to do when a source is paywalled

1. Check if the finding is citable from a free secondary source (Watt-Logic, HoC Library, Ofgem summary docs often republish the key numbers)
2. Check if a government/regulatory version exists (Ofgem often extracts the relevant statistics from Ofgem submissions)
3. Note the gap in `knowledge_map.md` with confidence ★ and flag for future access
4. Never extrapolate or hallucinate — mark as "unknown" and move on

Last updated: 2026-06-21
