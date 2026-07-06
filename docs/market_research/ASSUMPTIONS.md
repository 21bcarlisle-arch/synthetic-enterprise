# Synthetic Enterprise — Assumption Library

Living log of simulation assumptions validated against real UK energy market data.
Updated by discovery agent and manually when phases change assumptions.

Last seeded: 2026-07-06 from current codebase.

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
