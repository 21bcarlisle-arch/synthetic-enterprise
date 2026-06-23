# Synthetic Enterprise — Assumption Library

Living log of simulation assumptions validated against real UK energy market data.
Updated by discovery agent and manually when phases change assumptions.

Last seeded: 2026-06-23 from current codebase.

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
| **EBIT% — dom electricity (CSS post-cap 2019-2022)** | **NOT MODELLED (no price cap)** | **Negative: approx -4% to -10% per year; sector -£4bn cumulative** | **Ofgem published aggregate + EDF CSS 2023-2024** | **2026-06-23** | **⚠ CRITICAL GAP — no price cap in sim** |
| **EBIT% — dom electricity (CSS recovery 2023)** | **NOT MODELLED** | **4.2% (EDF); 7.8% (British Gas) — above-normal post-crisis** | **EDF CSS 2023 PDF; British Gas CSS 2023 PDF** | **2026-06-23** | **⚠ Context: 2023 exceptional due to hedge gains** |
| **EBIT% — dom electricity (CSS 2024, normalising)** | **NOT MODELLED** | **5.4% (EDF); Ofgem EBIT allowance in cap = 1.9%** | **EDF CSS 2024 PDF** | **2026-06-23** | **⚠ Long-run normal should be ~1.9-3%** |
| **EBIT% — dom gas (CSS 2023-2024)** | **NOT MODELLED** | **-6.1% (EDF 2023); -5.4% (EDF 2024) — persistently loss-making** | **EDF CSS 2023 + 2024 PDFs** | **2026-06-23** | **⚠ CRITICAL — domestic gas structurally loss-making under cap** |
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

## Growth & Acquisition

| Assumption | SIM value | Industry benchmark | Source | Last checked | Status |
|---|---|---|---|---|---|
| Acquisition cost — residential | £150/customer | £100–250 | Cornwall Insight; industry surveys | 2026-06-18 | ✓ OK |
| Acquisition cost — SME | £400/customer | £250–600 | Industry | 2026-06-18 | ✓ OK |
| Fixed overhead | £50/month | n/a (symbolic placeholder) | Phase 8a design | 2026-06-18 | ❌ Underscaled |
| Growth mandate | flat (no active acquisition) | n/a | Config | 2026-06-18 | ✓ OK |

## Known Gaps (not yet modelled)

| Gap | Impact | Priority |
|---|---|---|
| **Ofgem Domestic Price Cap (2019–present)** | **CRITICAL — domestic supply was loss-making 2021-2023 under the cap; our resi/elec 10.2% margin is impossible post-2019. Cap sets SVT unit_rate ceiling; suppliers absorbed cost overruns. CSS data confirms: EDF dom elec -6.1% gas EBIT 2023 even in recovery year.** | **HIGH — Phase needed** |
| ~~Annual variation in non-commodity rates~~ | ~~Medium~~ | ALREADY IMPLEMENTED — Phase 21a/27b/30a: _RO_COST_BY_OY_START, _CFD_LEVY_BY_YEAR, _CCL_ELECTRICITY_RATE_BY_YEAR, _NETWORK_COST_BY_YEAR (2016-2024) |
| De minimis VAT threshold for small SME | Low — few customers near threshold | LOW |
| ~~CCL for SME gas~~ | ~~Medium~~ | ALREADY IMPLEMENTED — Phase 30b (`get_gas_ccl_per_mwh()`, segment-aware) |
| HH smart meter customers | High — blocks ToU tariffs, VPP, DER | HIGH |
| Fixed overhead not scaled to portfolio size | Low — £50/month is underscaled for a real business | LOW |
| ~~Pricing actions not implemented~~ | ~~High~~ | CLOSED Phase 44a — £3/MWh uplift at renewal for net-negative accounts |

---

*Maintained by `background/discovery_agent.py`. Manual updates should note the source and date.*
