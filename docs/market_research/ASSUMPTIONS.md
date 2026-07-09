# Synthetic Enterprise — Assumption Library

Living log of simulation assumptions validated against real UK energy market data.
Updated by discovery agent and manually when phases change assumptions.

Last seeded: 2026-07-09 from current codebase.

---

## Bill Structure

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Non-commodity cost — electricity (resi) | £55/MWh | £50–65/MWh (network ~£35, levies ~£20) | Ofgem energy price stats, Elexon charges | 2026-06-18 | ✓ OK |
| Non-commodity cost — electricity (SME) | £42/MWh | £35–55/MWh (DUoS/TNUoS/BSUoS, lighter levy load) | Elexon, Ofgem | 2026-06-18 | ? Needs refresh |
| Non-commodity cost — gas (resi) | £10/MWh | £8–15/MWh (NTS, LDZ, Warm Homes levy) | Ofgem, Xoserve | 2026-06-18 | ✓ OK |
| Non-commodity cost — gas (SME) | £8/MWh | £6–12/MWh | Xoserve, industry | 2026-06-18 | ? Needs refresh |
| Non-commodity as % of all-in bill | ~35% | 30–45% (varies by year & segment) | Ofgem Electricity/Gas Stats | 2026-06-18 | ✓ OK (rough) |
| Standing charge — electricity (resi) | £0.27/day | £0.25–0.35/day | Ofgem Price Cap Q1-Q4 2024 | 2026-06-18 | ✓ OK |
| Standing charge — electricity (SME) | £0.55/day | £0.40–0.70/day | Industry tariff survey | 2026-06-18 | ✓ OK |
| Standing charge — gas (resi) | £0.25/day | £0.22–0.32/day | Ofgem Price Cap Q1-Q4 2024 | 2026-06-18 | ✓ OK |
| Standing charge — gas (SME) | £0.40/day | £0.30–0.55/day | Industry | 2026-06-18 | ✓ OK |
| VAT — residential | 5% | 5% (reduced domestic rate) | HMRC VAT Notice 701/19 | 2026-06-18 | ✓ OK |
| VAT — SME | 20% | 20% (standard rate; de minimis <33kWh/day qualifies for 5% — not modelled) | HMRC | 2026-06-18 | ? De minimis not modelled |

## Supplier Margin & Profitability

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Net margin as % of revenue (Phase 9a) | 9.1% | 2–5% | Ofgem Retail Market Report; Cornwall Insight | 2026-06-18 | ⚠ Above benchmark |
| Net margin as % of revenue (commodity only) | 3.5% | 2–5% | Same | 2026-06-18 | ✓ OK |
| Net margin as % of revenue (Phase 45c run, all-segments) | 2.9% | 2–5% | Phase 45c sanity check vs Ofgem/CMA | 2026-06-23 | ✓ OK |
| Gross margin as % of revenue (Phase 9a) | 9.8% | 8–15% (varies by year) | Ofgem | 2026-06-18 | ✓ OK |
| Capital cost ratio (Phase 9a, % of gross) | 8.1% | 5–20% (hedging cost varies) | Industry | 2026-06-18 | ✓ OK |
| Company elec forward risk premium (Phase 45c) | 8% above 120-day mean | 5–8% above NAP/baseload (I&C competitive) | Broker intelligence; Phase 45c sanity check | 2026-06-23 | ✓ OK |
| Company gas forward risk premium (Phase 46a) | 5% above 120-day mean | Near-zero in stable markets; UK resi gas suppliers earn ~1-2% in normal years (Cornwall Insight 2020) | NBP market; Phase 46a analysis | 2026-06-23 | ✓ OK |
| **EBIT% — dom electricity (CSS pre-cap 2016-2018)** | **NOT MODELLED separately** | **~2–5%** | **EDF/BG CSS 2023-2024 PDFs + CMA 2016 + Ofgem sector data** | **2026-06-23** | **✓ OK (pre-2019 sim range plausible)** |
| **EBIT% — dom electricity (CSS post-cap 2019-2022)** | **Cap applied Phase 47a. Sim 2021=-6.6%, 2022=+6.7%** | **Negative: approx -4% to -10% per year; sector -£4bn cumulative** | **Ofgem published aggregate + EDF CSS 2023-2024** | **2026-06-25** | **⚠ 2022 still positive in sim — cap biting but mutualization/wholesale partially offsetting** |
| **EBIT% — dom electricity (CSS recovery 2023)** | **NOT MODELLED** | **4.2% (EDF); 7.8% (British Gas) — above-normal post-crisis** | **EDF CSS 2023 PDF; British Gas CSS 2023 PDF** | **2026-06-23** | **⚠ Context: 2023 exceptional due to hedge gains** |
| **EBIT% — dom electricity (CSS 2024, normalising)** | **NOT MODELLED** | **5.4% (EDF); Ofgem EBIT allowance in cap = 1.9%** | **EDF CSS 2024 PDF** | **2026-06-23** | **⚠ Long-run normal should be ~1.9-3%** |
| **EBIT% — dom gas (CSS 2023-2024)** | **Gas cap applied Phase 47a. Sim 2023=-86.1%, 2024=-6.3%** | **-6.1% (EDF 2023); -5.4% (EDF 2024) — persistently loss-making** | **EDF CSS 2023 + 2024 PDFs** | **2026-06-25** | **⚠ 2023 extreme (-86%) vs benchmark (-6%); 2024 close to benchmark** |
| **EBIT% — non-dom electricity (CSS 2023-2024)** | **2.9% overall net (Phase 45c)** | **4.5% (EDF 2023); 1.7% (EDF 2024); 3.8% (BG 2023)** | **EDF CSS 2023-2024 PDFs; British Gas CSS 2023 PDF** | **2026-06-23** | **✓ SIM within normal range for I&C segment** |

## Hedging & Risk

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Minimum hedge floor (MIN_HEDGE_FLOOR) | 85% | 80–95% (supply obligation first) | EDF/Centrica investor disclosures; Phase 5c design | 2026-06-18 | ✓ OK |
| Capital cost basis | Unhedged (naked) volume only | Industry standard | Phase 5c design | 2026-06-18 | ✓ OK |
| OTC electricity forward bid-ask spread | 0.5% (3m) to 1.5% (2yr+) of fwd price | Q+1 OTC: 0.25–0.60% normal market; S&P mandate cap: 0.5–0.6% (≤Season+4); non-mandated Quarter+2+: 1–2.5%; Season+5+: 2%+ often illiquid | Ofgem WMI (ICIS/OTC, 4:30pm GB) 2022–2026; CMA Energy Market Investigation Appendix 7.1 (2016) | 2026-06-23 | ✓ OK (3m base slightly high; cap reasonable for ≤2yr hedging) |

## Customer & Portfolio

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Bad debt rate — residential | 2.0% of revenue | 1–3% | Ofgem Annual Report; Cornwall Insight | 2026-06-18 | ✓ OK |
| Bad debt rate — SME | 1.0% of revenue | 0.5–2% | Industry | 2026-06-18 | ✓ OK |
| Customer count (portfolio) | 9–13 (incl. successors) | n/a (synthetic portfolio) | Design | 2026-06-18 | n/a |
| Churn model basis | Bill-shock driven (Shifted-BG CLV) | Industry-aligned | Phase 4 design | 2026-06-18 | ✓ OK |
| DCA recovery rate — engaged/"overwhelmed" archetype | 30% of placed balance | 20–35% general utility-collections recovery-rate range (no UK energy-specific published figure found) | tratta.io collections-industry benchmark (via web search, 2026-07-05) | 2026-07-05 | ⚠ Unverified — general industry range, not energy-specific |
| DCA recovery rate — neutral archetype | 20% of placed balance | Same 20–35% range, midpoint-low used for customers without a clear engagement/avoidance signal | Same as above | 2026-07-05 | ⚠ Unverified — same caveat |
| DCA commission (contingency fee on recovered amount) | 15% of recovered GBP | 5–25% typical UK DCA commission (as low as 8% for larger debts, higher for older/smaller balances) | UK debt-collection fee-structure industry sources (via web search, 2026-07-05) | 2026-07-05 | ⚠ Unverified — general range |
| Debt-sale haircut — "avoidant" archetype | 12% of face value | 3–20% cited range for UK unsecured consumer debt sales (commercially negotiated, not publicly disclosed per-deal; FCA CONC governs conduct not price) | UK consumer debt-purchase market sources (via web search, 2026-07-05) | 2026-07-05 | ⚠ Unverified — no energy-specific published haircut found; genuine research gap per discovery-agent (2026-07-05) |
| DCA placement window (WRITTEN_OFF → PLACED_WITH_DCA) | +30 days | Not found — nearest published figure (60–90 days) is for the earlier internal-fail → DCA-referral transition, already captured pre-write-off | Illustrative assumption, not benchmarked | 2026-07-05 | Gap — no post-write-off placement-timing benchmark found |
| Context: share of UK energy arrears with no repayment plan | n/a (informs archetype mix, not a SIM parameter) | ~75% of £4.43bn domestic energy debt (June 2025) sits with customers on no repayment plan | Citizens Advice / Ofgem debt-strategy reporting (via web search, 2026-07-05) | 2026-07-05 | ✓ Source confirmed, directional context only |

## Growth & Acquisition

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Acquisition cost — residential | £150/customer | £100–250 | Cornwall Insight; industry surveys | 2026-06-18 | ✓ OK |
| Acquisition cost — SME | £400/customer | £250–600 | Industry | 2026-06-18 | ✓ OK |
| Fixed overhead | £50/month | n/a (symbolic placeholder) | Phase 8a design | 2026-06-18 | ❌ Underscaled |
| Growth mandate | flat (no active acquisition) | n/a | Config | 2026-06-18 | ✓ OK |


## Household Physical Property Attributes

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| EPC band distribution (England 2022) | Not yet modelled in household.py | A/B 3.3%, C 44.8%, D 42.6%, E 6.8%, F 2.1%, G 0.5% | EHS 2022-23 Energy Chapter AT1_2 (MHCLG, July 2024) | 2026-06-27 | Gap — household.py not yet built |
| Property type distribution (England 2022) | Not yet modelled | Terraced 29%, semi-detached 25%, detached 17%, flat 21%, bungalow 8% | EHS 2022-23 AT1_5 (MHCLG, July 2024) | 2026-06-27 | Gap — household.py not yet built |
| Build era distribution (England 2022) | Not yet modelled | Pre-1919 20%, 1919-44 15%, 1945-64 18%, 1965-80 19%, 1981-90 7%, post-1990 21% | EHS 2022-23 AT1_5 (MHCLG, July 2024) | 2026-06-27 | Gap — household.py not yet built |
| Heating system: gas boiler % | Not modelled at property level | ~86% of homes gas-fired; heat pump ~0.8% (2022) rising to ~2% (2025) | EHS 2023-24 Low Carbon Tech AT4; EHS 2022-23 AT3_1 | 2026-06-27 | Gap — household.py not yet built |
| Solar PV penetration | Phase 50 smart_meter model only | 3.0% (2016) → 5.7% (2025) of UK households | DESNZ Solar PV Deployment April 2026, Table 1 cumulative count | 2026-06-27 | Gap — EHS 2023-24 confirms 5.9% (2023-24) |
| EV adoption (resi) | Not modelled at property level | ~0.3% (2016) → ~7% (2025) of UK households | DfT licensed ULEV data; EHS 2023-24 AT3 (7.4% by 2023-24) | 2026-06-27 | Gap — household.py not yet built |
| Smart meter penetration (resi elec) | Phase 50: 10% (2016) → 75% (2025) | DESNZ: 10.6% (2016) → 68.9% (2024) → est. 72-75% (2025) | DESNZ Q4 2024 Smart Meters Stats Table 5a | 2026-06-27 | ✓ OK — Phase 50 model well-calibrated |
| EPC D vs C consumption uplift | Not modelled at property level | Metered: D uses ~20-30% more electricity, ~30-40% more gas than band C (same property type) | EHS 2022-23 AT1_6 (modelled cost: D +44% vs A/B/C avg); adjusted for prebound effect | 2026-06-27 | Gap — household.py not yet built |
| Loft insulation rate | Not modelled at property level | ~67% of loft-eligible homes insulated (~58% of all homes) | DESNZ HEE Dec 2024; EHS AT_4_10 | 2026-06-27 | Gap — household.py not yet built |
| Cavity wall insulation rate | Not modelled at property level | ~63% of cavity-eligible homes insulated (~38-40% of all homes) | DESNZ HEE Dec 2024 cumulative ECO installs + pre-ECO stock | 2026-06-27 | Gap — household.py not yet built |

## Household Segment & Psychology (Phase 2, CORE_FIDELITY_PHASES.md — archetype layer)

Closes the five genuine gaps identified for Table A ("Household segment & psychology design")
in `docs/design/CORE_FIDELITY_PHASES.md` Phase 1. Property attributes (EPC/type/era/heating/
solar/EV/insulation) are already covered above and NOT repeated here.

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Occupancy / household size distribution (England, 1/2/3-4/5+ person) | Not yet modelled — no per-customer occupancy field exists | 1-person 30.1%, 2-person 34.0%, 3-4-person 28.9% (3-person 16.0%, 4-person 12.9%), 5+-person 7.0% (5-person 4.5%, 6-person 1.5%, 7-person 0.5%, 8+-person 0.4%). Mean 2.37 persons/household. | ONS Census 2021 table TS017 "Household size", England-only aggregate computed directly from the published LTLA-level CSV (census day 21 March 2021; static.ons.gov.uk/datasets/TS017-2021-3.csv, fetched 2026-07-08) | 2026-07-08 | H — primary census microdata, aggregated directly by discovery agent, not a secondary citation |
| Occupancy — cross-check against EHS (mean household size trend) | n/a — corroborating check only | EHS mean persons/household: 2.4 (2019-20, pre-pandemic) → 2.2 (2023-24, first post-pandemic-methodology reading); mortgagors/private renters highest (2.7/2.3), outright owners lowest (1.8) | EHS 2023-24 Headline Report on Demographics and Household Resilience, Chapter 1 (MHCLG, published Nov 2024, PDF fetched 2026-07-08) | 2026-07-08 | H — the Census 2021 figure above (2.37) sits consistent with this trend (a 2021 census-day reading between the 2019-20 and 2023-24 EHS means, as expected) |
| Tenure split (England, owner-occupier / private-rented / social-rented) | Not yet modelled — no per-customer tenure field exists | Owner-occupier 65% (35% outright owners, 30% mortgagors); private renters 19%; social renters 16% (10% housing association, 6% local authority) | EHS 2023-24 Headline Report on Demographics and Household Resilience, Chapter 1, "Trends in tenure" (MHCLG, published Nov 2024, PDF fetched 2026-07-08) | 2026-07-08 | H — EHS is the authoritative tenure series (accredited official statistic), figure stable since 2019-20 |
| Fuel poverty rate (England, LILEE metric) | Not modelled — no income-band or fuel-poverty flag exists per customer | 11.0% of English households (2.73 million) in fuel poverty under LILEE, 2024 (down from 11.4%/2.80m in 2023); DESNZ projects 11.2%/2.78m for 2025. Fuel-poverty rate by electricity payment method: prepayment 22.3%, standard credit 18.5%, direct debit 8.8% (2024). | DESNZ "Annual Fuel Poverty Statistics in England, 2025 (2024 data)", 27 March 2025, Accredited Official Statistics (PDF fetched 2026-07-08) | 2026-07-08 | H — official DESNZ annual release, LILEE is the current statutory metric (post-2019, replaced the old 10%-of-income LIHC metric) |
| Fuel poverty — affordability cross-check (>10% income on energy, AHC) | n/a — corroborating alternative metric only | 36.3% of English households (8.99 million) spent >10% of income (after housing costs) on domestic energy in 2024, up from 35.5% (8.73m) in 2023 | Same DESNZ report as above, headline statistics section | 2026-07-08 | H — same source; shows the older ">10% of income" definition gives a much higher rate (36.3%) than the current LILEE metric (11.0%) — a real methodological gap worth reflecting if the SIM ever models both definitions |
| Payment method mix — Direct Debit share (GB domestic, standard/credit meters) | Not modelled at population level — `arrears_engine.py::payment_method()` is segment-aware (resi/SME/I&C) but not archetype-aware within resi | Direct Debit was 72% of standard electricity customers and 75% of gas customers, end of March 2026 — up ~3-5 percentage points over the preceding 5 years | DESNZ "Quarterly Energy Prices: June 2026" commentary PDF, "Payment methods" section (published gov.uk, fetched 2026-07-08) | 2026-07-08 | H — official DESNZ quarterly series, most recent data point (end-March 2026) |
| Payment method mix — prepayment vs standard credit split (remainder) | Not modelled | Not found this session — DESNZ QEP June 2026 gives DD share only (72%/75%); the ~25-28% non-DD remainder's PPM-vs-standard-credit split was not published in the commentary text fetched (may exist in the accompanying detailed data tables, not retrieved) | DESNZ QEP June 2026 (as above) | 2026-07-08 | Gap — genuine sub-gap; DD share is solid, the 3-way split is not closed this session |
| Active vs passive/disengaged switcher rate (proxy: default-tariff tenure length) | `simulation/household_segments.py` (Phase 2 Layer 1, built 2026-07-08) — per-customer ACTIVE/PASSIVE/DISENGAGED archetype (48%/23%/29% population shares, proxied from the OLDER 2018 Ofgem Consumer Engagement Survey SVT-tenure cohorts), calibrated so the weighted aggregate reproduces `company/crm/churn_model.py`'s existing anchored ~35% flat rate — deliberately NOT recalibrated to the newer 45.1% figure this pass (see Status) | As of October 2025 (non-prepayment domestic accounts, electricity): 45.1% on actively-chosen tariffs; 54.9% on default tariffs, split 20.3% held 3+ years (clearly disengaged) vs 34.6% held <3 years. Gas: 45.4% actively chosen, 54.6% default (23.1% held 3+ years, 31.5% <3 years). | Ofgem Retail Market Indicators data portal, "Number of domestic customer accounts by supplier... on default tariffs" panel (ofgem.gov.uk/energy-data-and-research/data-portal/retail-market-indicators, fetched 2026-07-08) | 2026-07-08 | ⚠ Flagged for director recalibration decision — official Ofgem Oct 2025 data puts the real active share (~45%) materially higher than the SIM's existing anchored 35% baseline (itself sourced from the OLDER 2018-2019 Consumer Engagement Survey). Phase 2 Layer 1 deliberately preserved the existing 35% aggregate rather than silently drifting a portfolio-wide calibration constant as a side effect of adding archetype heterogeneity — recalibrating to ~45% is a separate, larger decision (shifts churn/revenue dynamics broadly) flagged here for the next weekly re-rank, not actioned unilaterally |

## Competitor Platform Landscape (structural reference only)

`docs/market_research/COMPETITOR_PLATFORMS_2026.md` (director-supplied, 2026-07-08) is an
unsourced, AI-assisted compilation surveying seven real energy-retail platforms (MaxBill,
Gorilla, Gentrack g2, Kraken, Kaluza, Axle/Amber, SAP+Salesforce). Used only as a structural
reference for `docs/market_research/ESTATE_GAP_ANALYSIS.md`'s capability cross-check — never as
a source of figures. All quantitative claims below are explicitly flagged UNVERIFIED in the
source document itself.

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Kraken cost-to-serve reduction from unified monolith | n/a — architectural reference only | "30-40% operational cost reduction claimed" | COMPETITOR_PLATFORMS_2026.md §4 (director-supplied, AI-assisted, unsourced) | 2026-07-08 | ⚠ Unverified — no primary source cited in the survey itself |
| Gentrack g2 production AI agent count | n/a — architectural reference only | "17+ autonomous AI agents in live production" | COMPETITOR_PLATFORMS_2026.md §3 (director-supplied, AI-assisted, unsourced) | 2026-07-08 | ⚠ Unverified — no primary source cited in the survey itself |
| Kaluza Flex OEM integration count | n/a — architectural reference only | "400+ device OEMs" | COMPETITOR_PLATFORMS_2026.md §5 (director-supplied, AI-assisted, unsourced) | 2026-07-08 | ⚠ Unverified — no primary source cited in the survey itself |

## Meter-Read Arrival Delay, Estimation & Failure (Phase 3, CORE_FIDELITY_PHASES.md)

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Smart meter "not communicating" / traditional-mode rate (all meters, GB) | `simulation/meter_reads.py::SMART_METER_NOT_COMMUNICATING_RATE = 0.10` (of installed smart meters) | 6.4% of all meters operating in "traditional mode" (manual read needed); ~10% of installed smart meters not in smart mode, end 2024 | DESNZ Q4 2024 Smart Meters Statistics Report (fetched direct, 2026-07-08) | 2026-07-08 | ✓ OK — Phase 3 item 1 built, blended elec/gas (see module docstring for the not-fuel-differentiated caveat) |
| Read-estimation-exposed domestic electricity meters | Not directly modelled as a standalone rate — captured implicitly via meter_type_for_customer() reusing the existing Phase 50 smart-meter-penetration curve | ~35.8% (31.1% non-smart/dumb + 4.7% smart-in-traditional-mode), end 2024 | DESNZ Q4 2024 Smart Meters Stats, Table 1/5a domestic split | 2026-07-08 | Reference only — see saas/smart_meter_rollout.py for the calibrated penetration curve this derives from |
| Read-estimation-exposed domestic gas meters | Not fuel-differentiated (documented simplification, see meter_reads.py docstring) | ~45.3% (36.2% non-smart/dumb + 9.1% smart-in-traditional-mode), end 2024 — gas notably worse than electricity | DESNZ Q4 2024 Smart Meters Stats, Table 1/5a domestic split | 2026-07-08 | Known gap — follow-up if a fuel-differentiated model is needed |
| Traditional (non-smart) meter actual-read cadence | `simulation/meter_reads.py::TRADITIONAL_ACTUAL_READ_PROBABILITY = 1/6` (≈6-monthly) | ~6-monthly actual read cycle industry practice, self-read/estimate between visits (precise Ofgem SLC 21A text not independently fetched this session) | Citizens Advice consumer guidance (mechanism confirmed); SLC text — genuine gap | 2026-07-08 | ⚠ Unverified precise cadence — mechanism confirmed, number not; SIM uses the confirmed ~6-monthly figure |
| Back-billing correction deadline | `simulation/meter_reads.py::MAX_CONSECUTIVE_ESTIMATED_PERIODS = 12`; `acquisition_funnel.py`/`credit_refund_events.py` unaffected | 12 months — supplier cannot bill for energy used >12 months ago unless a timely bill was issued and left unpaid | Citizens Advice ("If you haven't received an accurate energy bill in a while"), retrieved 2026-07-08 | 2026-07-08 | ✓ OK — real regulatory ceiling, encoded as the Phase 3 forced-catch-up cap |
| Non-domestic (SME/I&C) smart/advanced meter operating rate | Not reconciled — meter_reads.py reuses the same smart/traditional split for all segments | 58% of non-domestic meters smart/advanced overall (elec 61%, gas 32%) end 2024 | DESNZ Q4 2024 Smart Meters Stats Table 1 | 2026-07-08 | Gap — not reconciled against domestic split; follow-up if a segment-specific model is needed |
| Bill generation/delivery lag | `tools/generate_billing_ledger.py::BILL_GENERATION_DELAY_MEAN_DAYS = 3.0` | Not independently benchmarked this round | — | 2026-07-08 | ⚠ Provisional — no DESNZ/Ofgem billing-cycle-latency benchmark registered yet; industry-convention placeholder |
| Contact-centre channel mix (phone/email/webchat) | `simulation/contact_centre.py::CHANNEL_WEIGHTS = {phone: 0.55, email: 0.25, webchat: 0.20}` | Not independently benchmarked this round | — | 2026-07-08 | ⚠ Provisional — industry customer-service convention, not discovery-agent-verified |
| Contact-centre email first-response SLA target | `simulation/contact_centre.py::EMAIL_FIRST_RESPONSE_SLA_HOURS = 24.0` | Not independently benchmarked this round | — | 2026-07-08 | ⚠ Provisional — industry customer-service convention, no specific Ofgem complaint-handling-standards figure cited |
| Acquisition-funnel stage-to-stage day spacing (quote→application, application→credit_check, credit_check→onboarding) | `simulation/acquisition_funnel.py::_QUOTE_TO_APPLICATION_DAYS/_APPLICATION_TO_CREDIT_CHECK_DAYS/_CREDIT_CHECK_TO_ONBOARDING_DAYS` | Not independently benchmarked this round | — | 2026-07-08 | ⚠ Provisional — short seed distributions, not discovery-agent-verified |
| Cooling-off statutory period | `simulation/acquisition_funnel.py::COOLING_OFF_PERIOD_DAYS = 14` | 14 calendar days — Consumer Contracts (Information, Cancellation and Additional Charges) Regulations 2013, off-premises/distance contract cancellation window | Statutory instrument (general UK consumer law knowledge, not this session's discovery-agent fetch) | 2026-07-08 | ✓ OK — well-established regulatory constant |

See `docs/market_research/meter_read_latency_estimation_2026.md` for full findings, direct
quotes, and sourcing detail on the meter-read rows. The bill-generation-lag, contact-centre,
and funnel-spacing rows above are flagged ⚠ provisional pending a dedicated discovery-agent
pass — not yet requested this session (token-economy tradeoff, Phase 3 items 3-5 unblocked by
proceeding with clearly-labelled provisional seed values per the Anchored-noise law).

## Known Gaps (not yet modelled)

| Gap | Impact | Priority |
|---|---|---|
| ~~Ofgem Domestic Price Cap (2019–present)~~ | ~~CRITICAL~~  | CLOSED Phase 47a — `get_cap_unit_rate_gbp_per_mwh()` annual lookup, clamp applied in run_phase2b for resi fixed-term customers |
| **Real forward curve (NBP/EPEX term structure)** | **HIGH — Company forward price is a 120-day lagging spot mean × risk premium, not a real term-structure curve. This understates forward price in rising markets (2021-2022 lag effect) and overstates in falling markets. Matters most for: I&C (genuinely priced against book forward, not rolling spot); dynamic resi tariffs; hedging book accuracy.** | **Future phase — substantial work** |
| **Cap-aware acquisition gate** | Medium — acquisition win rate is static (20% resi); real suppliers paused resi acquisition in 2021-2023 as all new resi customers were loss-making under the cap | Phase 47b proposed |
| ~~Annual variation in non-commodity rates~~ | ~~Medium~~ | ALREADY IMPLEMENTED — Phase 21a/27b/30a: _RO_COST_BY_OY_START, _CFD_LEVY_BY_YEAR, _CCL_ELECTRICITY_RATE_BY_YEAR, _NETWORK_COST_BY_YEAR (2016-2024) |
| De minimis VAT threshold for small SME | Low — few customers near threshold | LOW |
| ~~CCL for SME gas~~ | ~~Medium~~ | ALREADY IMPLEMENTED — Phase 30b (`get_gas_ccl_per_mwh()`, segment-aware) |
| HH smart meter customers | High — blocks ToU tariffs, VPP, DER | HIGH |
| Fixed overhead not scaled to portfolio size | Low — £50/month is underscaled for a real business | LOW |
| ~~Pricing actions not implemented~~ | ~~High~~ | CLOSED Phase 44a — £3/MWh uplift at renewal for net-negative accounts |

---

*Maintained by `background/discovery_agent.py`. Manual updates should note the source and date.*
