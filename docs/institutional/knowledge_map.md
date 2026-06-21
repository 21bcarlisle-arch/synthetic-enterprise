# Knowledge Map — Synthetic Enterprise

**Format:** Domain → What we know → Confidence (H/M/L) → Key gaps → Next question

Confidence key: **H** = primary source data, quantified | **M** = secondary source, directionally reliable | **L** = inferred, unverified

---

## Domain: Energy Consumption Profiles

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Residential electricity (NEED 2026) | Median 2,500 kWh/yr; IQR 1,600–4,100; Ofgem TDCV Low/Med/High = 1,600/2,500/3,800 | H | Distribution by property type (only 2019 data available by type) | Does NEED 2026 publish property-type disaggregation? |
| Residential gas (NEED 2026) | Median 10,000 kWh/yr; IQR 6,500–14,400; TDCV = 6,000/9,500/14,000 | H | Same gap — property type breakdown | Same as above |
| SME electricity | Microbiz: up to 15,000 kWh; Small: 15–25,000; Medium: 25–50,000. Bionic broker data: 8,500–15,000 typical | M | Sector breakdown (retail vs office vs hospitality); gas for SME | How does gas consumption scale with electricity for SME? |
| Dual-fuel proportion | ~75% of residential customers take both fuels from same supplier | H | SME dual-fuel rate | Do SME customers dual-fuel at the same rate? |
| Smart meter coverage | ~65–67% domestic (smart mode); ~64% non-domestic | H | True HH settlement rate vs. meter installed | What % are actually on HH settlement contracts vs just metered? |
| EPC data | 29.2M domestic certs; portal at get-energy-performance-data.communities.gov.uk; key field ENERGY_CONSUMPTION_CURRENT (kWh/m²/yr); apply 0.65 correction for billing use | H | Electricity/gas split (no separate column — must infer from MAIN_FUEL) | Can MHCLG publish a derived electricity/gas split field? |
| Current sim vs reality | C1 elec 12% high; C5 SME ~50% high; gas legs roughly correct | M | Full customer-by-customer calibration | Run Phase 21c consumption recalibration, then compare P&L impact |

**Sources:** DESNZ NEED 2026, Ofgem TDCV 2026 review, HoC Library CBP-9768, MHCLG EPC portal  
**Files:** `docs/market_research/ons_consumption_profiles.md`, `docs/market_research/epc_open_data.md`

---

## Domain: Regulatory Framework

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Price cap scope | SVT only; fixed-rate contracts outside cap | H | How cap interacts with mid-term rate changes for fixed customers | Can a fixed-rate customer be moved to SVT mid-term if supplier fails? |
| Cap formula | Bottom-up: wholesale (~40%) + network (~23%) + policy (~13%) + opex (~17%) + EBIT (~2%) + VAT (5%). Resets quarterly. Wholesale allowance ~3.5 months stale | H | Exact wholesale reference period mechanism | What are the precise forward price observation windows Ofgem uses? |
| Capital floor | £0 net assets per customer = licence breach | H | How Ofgem monitors this in practice | What triggers the Ofgem inspection process for capital adequacy? |
| Capital target | £130 net assets per dual-fuel customer | H | Whether this is adjusted for risk profile | Does Ofgem allow risk-based capital requirements? |
| Renewables Obligation | 0.491 ROCs/MWh electricity; buy-out £64.73/ROC (2024-25) → ~£31.80/MWh effective | H | Historical RO obligation levels for sim years 2016-2024 | What were RO obligation and buy-out price levels by year 2016–2024? |
| CfD levy | Operational costs levy: £9.257/MWh from April 2025; main levy variable quarterly (can go negative at high prices) | H | CfD levy levels for sim years 2016-2024 | What were CfD levy levels by year 2016–2024? |
| BSC credit cover | CAP = £350/MWh × 29-day settlement lag; for our sim: ~£10k–20k cash tied up | M | Exact current CAP level; how it changes | How often does Elexon revise the Credit Assessment Price? |
| Network charges (electricity) | ~23% of bill; split TNUoS (transmission) + DUoS (distribution) | M | Actual £/MWh figures by year 2016-2024 | What were network charge levels for residential/SME by year? |
| 2021-22 failure wave | 28 suppliers failed; driven by hedge ratio + cap lag; £2.6bn SOLR cost | H | Individual supplier hedge ratios at failure | Could we simulate each failure trigger? |

**Sources:** Ofgem website, Elexon BSC docs, Watt-Logic, HoC BEIS Committee  
**Files:** `docs/market_research/ofgem_regulation.md`

---

## Domain: Financial Reporting and P&L Structure

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Gross margin (real suppliers) | 8–14% of revenue in normal years (OVO: 10–14%; Octopus: ~9%; Utilita: ~18%) | H | Small supplier gross margins (our scale) | What gross margins do suppliers with <50,000 customers achieve? |
| Net margin | 1–3% steady state; negative in crisis. Octopus FY23: 1.6%; FY24: 0.7%; FY25: -1.9% | H | Decomposition of net margin by P&L line | What is the opex-to-revenue ratio at small suppliers? |
| IFRS 9 treatment | Own-use exemption (most physical suppliers) = cost at delivery, no MTM. FVTPL = MTM distorts statutory P&L. Our sim correctly models own-use. | H | Whether small suppliers use own-use or FVTPL in practice | Do small UK suppliers typically have ISDA agreements that force FVTPL treatment? |
| Bad debt (DD book) | ~1–2.5% of revenue; Ofgem cap allowance ~£26/customer/yr. OVO: 1.4–2.6%. Sector total: £3.85bn outstanding Q4 2024 | H | Bad debt write-off vs recovery rates | What % of energy bad debt is eventually recovered vs written off? |
| Opex per customer | Ofgem cap allowance: £97/customer/yr (DD, 2023-24) | H | Actual opex at small vs large suppliers | How much does cost-to-serve vary with scale? |
| Board MI cadence | Daily: treasury/hedge MTM. Weekly: customer position, debt. Monthly: underlying P&L. Quarterly: board pack + Ofgem returns | H | What triggers board escalation | Have any suppliers published their board pack templates? |
| Derivative MTM | Major P&L distortion in statutory accounts (OVO: ±£1bn swings). "Underlying EBIT" strips this out. | H | How mid-size suppliers manage this in management accounts | — |
| Our sim vs reality | Commodity-only -3% gross; -4.3% net. Full stack would show realistic 8-14% gross. Policy costs ~£40-50/MWh missing. | H | Impact of adding policy costs to both sides | Model policy cost addition → what does gross margin become? |

**Sources:** OVO accounts (Watt-Logic), Octopus investor releases, Ofgem CSS framework, KPMG IFRS 9  
**Files:** `docs/market_research/supplier_financial_reporting.md`

---

## Domain: Company Operations (Pending — Round 2 Research)

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Commercial strategy (product mix, acquisition) | Research in progress | — | — | See agents launched 2026-06-21 18:38 |
| Debt management and collections | Research in progress | — | — | See agents launched 2026-06-21 18:38 |
| Treasury and hedge governance | Research in progress | — | — | See agents launched 2026-06-21 18:38 |
| Customer comms and renewal lifecycle | Research in progress | — | — | See agents launched 2026-06-21 18:38 |

---

## Domain: Market Structure and Competition

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Supplier count | Post-crisis: ~18-20 active domestic suppliers (down from ~70 pre-crisis). Big 6 + Octopus + OVO dominate. | M | Current market share by supplier | What % market share does Octopus hold in 2026? |
| Switching rates | — | — | Historical annual switching rates 2016-2025 | How did switching behave before/during/after the crisis? |
| Acquisition channels | — | — | Cost per acquisition by channel | PCW vs. direct vs. broker — which is most cost-effective? |
| Customer lifetime / churn | — | — | Industry average churn rates by customer type | What is a typical residential annual churn rate in 2024? |

---

## Domain: Simulation-Specific Calibration

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Elexon SSP as cost proxy | SSP = commodity-only. Real supply cost = SSP + network (~£20-25/MWh) + policy (~£40-50/MWh) | H | Historical network charge data for 2016-2024 | Can we get TNUOS/DUoS historical series from NESO? |
| Administration trigger | Current: treasury ≤ 0. Regulatory: £0 net assets/customer. These diverge as customer count grows. | H | — | Implement Phase 21b (per-customer net assets) |
| Phase 21a (policy costs) | Adds ~£40-50/MWh to both cost and revenue — should leave margin% roughly unchanged but makes absolute numbers realistic | M | Whether adding RO/CfD changes the 2021-22 crisis dynamics | Model the 2021-22 period with explicit RO costs — does this worsen or improve the simulated outcomes? |
| Hedge ratio adequacy | Board flags if <50% coverage for >3 months forward | H | Our current hedge ratio is tracked but not surfaced as a board KPI | Add hedge adequacy warning to LATEST.md |

---

## What we don't know (priority gap list)

Ranked by likely simulation impact:

1. **Historical RO + network charge levels by year (2016-2024)** — needed to accurately model Phase 21a across the full sim period, not just from 2025
2. **Small supplier opex structure** — how does our 9-customer company compare on cost-to-serve? What's realistic for our scale?
3. **Acquisition cost per channel** — PCW, direct, broker; needed to model acquisition economics properly
4. **Historical SME churn rates** — our churn model parameters are estimated, not calibrated to real data
5. **EPC property-type breakdown at NEED 2026 level** — we have 2019 data; 2026 version may have been published

Last updated: 2026-06-21
