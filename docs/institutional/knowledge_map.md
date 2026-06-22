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
| Renewables Obligation | 0.491 ROCs/MWh electricity; buy-out £64.73/ROC (2024-25) → ~£31.80/MWh effective. Historical: £15.6/MWh (2016-17) rising steadily to £31.8/MWh (2024-25). | H | None — full 2016-2024 series now known | — |
| CfD levy | 2016: ~£0/MWh. 2017-20: £1-5/MWh growing. 2021: cut to £0 Oct 2021. **2022: NEGATIVE (−£3 to −£8/MWh) — wholesale > strike prices, LCCC rebated suppliers**. 2023-24: £5-12/MWh. From April 2025: £9.257/MWh operational costs levy. | H | Sub-quarterly precision for 2021-22 rebate | — |
| BSC credit cover | CAP = £350/MWh × 29-day settlement lag; for our sim: ~£10k–20k cash tied up | M | Exact current CAP level; how it changes | How often does Elexon revise the Credit Assessment Price? |
| Network charges (electricity) | ~23% of bill; resi/SME combined DUoS+TNUoS: £35-46/MWh (2016-2024). I&C HV: DUoS only £11-14/MWh (Triad-based TNUoS separate). Ofgem Annex 9 suggests higher combined figures (2022/23: £52.9/MWh London resi) — calibration in next phase. TCR April 2023: TNUoS residual moved from unit rate to banded standing charge (~£106/yr Band 4). | M | Precise year-by-year figures from Ofgem Annex 9 differ from our lookup table by £5-10/MWh. TCR 2023 structural shift not fully modelled (standing charge vs unit rate for post-2023) | Calibrate lookup tables from Ofgem Annex 9 data in network_charges_uk_2016_2024.md; model TCR 2023 discontinuity |
| Gas CCL | Non-domestic only (resi exempt). £1.95/MWh (2016) → £7.75/MWh (2024). Large step in 2019 (Budget 2016 rebalancing policy). Parity with electricity CCL achieved April 2024. HMRC Table 1 source. | H | None — full 2016-2024 series known | — |
| Gas network charges | GDN + NTS combined unit rate. All segments (no exemptions). £9.0–17.6/MWh (2016–2024). 2023 peak = RIIO-GD2 + SOLR cost socialisation. | M | Exact Ofgem Annex 9 figures (gas network annex is Excel-only); current figures derived from cap unit rates × network % share | Obtain gas network annex from Ofgem for authoritative year-by-year figures |
| Green Gas Levy (GGL) | Per-meter (MPRN) per day. Started 30 Nov 2021. All segments. 2022: £2.10/yr/meter; 2023: £0.45; 2024: £0.38. Normalised to £/MWh via customer AQ. DESNZ GOV.UK source. | H | Post-2025 levy rates not yet published | — |
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

## Domain: Company Operations

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| Fixed vs SVT product mix | Pre-crisis ~45% fixed; crisis trough ~15-20%; July 2025 ~33%. Suppliers withdraw fixed deals when they can't hedge. | H | Our sim doesn't model the fixed/SVT decision — all customers are on fixed annual terms | Should we model an SVT fallback product? |
| PCW acquisition channel | ~67% of switches via PCW; top-2 PCWs = 75% share. Commission: £30-60/dual-fuel customer. Direct/referral cuts blended cost by ~31% (Octopus) | H | PCW listing is a prerequisite for growth — our sim doesn't model acquisition channel | Add acquisition channel to company strategy layer |
| SME vs residential trade-offs | SME: higher volume/account, stickier (1-3yr contracts), 42% use TPI/broker (2-4% commission). Resi: simpler ops, PCW channel, price cap floor. | H | SME TPI dynamics not modeled; all our SMEs acquired identically to resi | — |
| Minimum viable scale | ~250k-500k dual-fuel customers for self-sustaining balance sheet. Below that: opex/compliance fixed costs exceed EBIT margin. 73 entrants 2010-22; 65 exited. | H | Our sim has 9 customers — a pre-viable micro-supplier. Capital from Rich (starting treasury) is the analogue of parent backing | — |
| 49-day renewal window | Statement of Renewal Terms issued 42-49 days before expiry; exit fee waiver in final 49 days. This is the primary commercial trigger for renewal campaigns. | H | Our sim renews annually but doesn't model the 49-day advance notice obligation | Add renewal notice lead time to company CRM |
| Debt lifecycle | 5-10 week minimum from missed bill to formal disconnection notice. 6-year statute of limitations. CCJs rising as PPM warrant replacement. | H | Our sim's bad debt is modeled as a flat % — not as an aged debt lifecycle | Add debt stages to customer record (current → overdue → plan → write-off) |
| Bad debt rates by payment method | DD customers: ~1% of bills. Standard credit: ~6%. Total sector debt stock: £4.43bn (June 2025, +71% since 2023). Write-off: ~1/3 of stock. | H | Are any of our sim customers on standard credit vs DD? If so, bad debt should be 6× higher | Segment sim customers by payment method; differentiate bad debt provision |
| PPM and collections | 4.3M PPM customers. 3.2M self-disconnect per year. PPM warrants now require vulnerability checks; 2023 scandal cost British Gas £20m + £70m debt write-off. | H | PPM not modeled in sim — all customers implicitly on DD | — |
| IFRS 9 debt provision matrix | 0-30d DD: 0.3-0.5%; 61-90d DD: 5-8%; 91-180d DD: 15-25%; >365d DD: 70-85%. SC rates ~6× higher. | M | This is an indicative matrix — not officially published by Ofgem | Does Ofgem or industry body publish a recommended provision matrix? |
| Treasury and hedge governance | Layered ladder hedge strategy (1/5 per quarter × 5 quarters). Target: 70-90% at 12m, 85-95% at 6m, 90-100% at 3m. Good Energy publicly >90% hedged Oct 2021. 22/26 failed suppliers underfunded. Exchange IM: 4-15% normal, 60-80% crisis peak. RCF size for 5k-50k customers: £5-50m. Capital floor £57.50/domestic (cf £130/dual-fuel from reg docs — same rule, different framing). | H | No hedge ratio waterfall in our board reporting; no collateral buffer in treasury | Add hedge ratio by tenor to LATEST.md; model BSC/exchange credit cover as reserved cash |
| Customer comms and renewal lifecycle | Domestic: 42-49 day statutory notice (SLC 22A). Exit fee banned in that window. Cannot auto-rollover to new fixed — must default to cheapest SVT. SME: 60-120 day notice. Tariff change: 30 days. Missed payment (monthly): contact after 2nd consecutive miss. ~35% actively renew to new fixed; ~65% roll to SVT. Win-back: 30d + 90d post-churn; ~5-15% conversion. PSR: ~10-15% of base; mandatory proxy/nominee, priority routing, proactive identification. Cost per contact: phone £5-12, webchat £2-5, self-serve £0.10-0.50. | H | Our sim doesn't model the 42-day notice period; no active-renewer vs SVT-roller distinction; no win-back | Add 49-day renewal flag to company CRM; model passive SVT rollover proportion |

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
| Elexon SSP as cost proxy | SSP = commodity-only. Real supply cost = SSP + network (~£35-46/MWh resi/SME, £11-14/MWh I&C DUoS) + policy (~£20-45/MWh). Both now modelled in Phase 21a+29a. | H | Network rates ~£5-10/MWh below Ofgem Annex 9 — calibration needed | Refine lookup tables in simulation/policy_costs.py against Annex 9 data in docs/market_research/network_charges_uk_2016_2024.md |
| Administration trigger | Current: treasury ≤ 0. Regulatory: £0 net assets/customer. These diverge as customer count grows. | H | — | Implement Phase 21b (per-customer net assets) |
| Phase 21a (policy costs) | Adds ~£40-50/MWh to both cost and revenue — should leave margin% roughly unchanged but makes absolute numbers realistic | M | Whether adding RO/CfD changes the 2021-22 crisis dynamics | Model the 2021-22 period with explicit RO costs — does this worsen or improve the simulated outcomes? |
| Hedge ratio adequacy | Board flags if <50% coverage for >3 months forward | H | Our current hedge ratio is tracked but not surfaced as a board KPI | Add hedge adequacy warning to LATEST.md |

---

## Domain: Novel/Unseen Scenario Generation

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| 2021-22 crisis non-linearity | Five feedback loops: storage-hedging failure, hedging-asset contamination, SOLR mutualization, regulatory capital void, cap-lag mechanism. Commodity price shock (no physical shortage), killed 28 suppliers. | H | Precise hedge ratios at each failing supplier | Could we simulate each failure trigger individually? |
| Negative price regime | 29 (2022) → 107 (2023) → 149 (2024) → projected ~1,000/yr peak 2027. CfD-backed generators are price-insensitive (key amplifier). Post-2027: merchant capacity grows, negative-price frequency declines. Regime change. | H | Post-2027 trajectory after merchant capacity reaches critical mass | What percentage of new capacity post-2027 will be merchant vs CfD-backed? |
| Bimodal price distribution | At 70%+ renewable penetration: very low/negative during surplus; very high during wind/solar droughts. Mean compressed; variance exploding. "Price cannibalization" — wind capture price diverges from baseload. | M | When does GB grid cross the 70% threshold? (UK 2030 target is 100% clean power) | How quickly does the bimodal pattern emerge post-70%? |
| Dunkelflaute + interconnector loss | January 2026 UK cold snap: demand 47.3 GW (7yr high), wind 2 GW, wholesale £1,040/MWh. Interconnectors reversed simultaneously. If UK+EU experience correlated dunkelflaute: no rescue. | H | Duration modelling — how long can a multi-country dunkelflaute last? | Wood Mackenzie study — what's their estimate of worst-case correlated dunkelflaute duration? |
| ERCOT February 2021 analogue | $9,000/MWh for 77 hours. $26.5bn damage. UK analogue: sustained cold snap + Norwegian import failure + 3+ days wind < 5 GW. UK price cap shields retail consumers but cascades into unhedged supplier insolvencies. | H | Whether UK Capacity Market provides adequate protection | At what wholesale price level do UK suppliers start failing even with hedges? |
| Electrification feedback loops | Heat pump adoption: −90% gas demand but +61% electricity demand. Winter evening peak +100%+ at full penetration. Gas network death spiral (£3–4bn stranded assets). 5.7M HPs → £40.7bn network reinforcement. | H | Rate of gas network death spiral vs policy intervention timeline | What triggers the government's 2026 decision on gas grid future? |
| EV smart charging bifurcation | 1M EVs dumb-charging 6–10pm: +7 GW peak. With smart charging: <1 GW overnight. V2G: 51 GW flex by 2050 (NESO FES 2025). Behavioral: same fleet count, radically different grid stress (7× difference). | H | Smart tariff participation rate forecasts | What percentage of EV owners in UK engage with smart tariffs currently? |
| BESS market saturation | 20–30 GW target (2030). FCR revenues 7× decline 2021→2024. At 20–30 GW: price spread compression. £32M/GW/yr arbitrage at current spreads → falls as scale increases. "Race to charge" synchronisation risk. | H | Revenue stack modelling at 23+ GW | What's the post-saturation equilibrium annual revenue per GW for BESS? |
| Interconnector as amplifier | At moments of UK stress, all interconnectors reverse simultaneously — AMPLIFYING spikes rather than dampening them. EU structural high-price scenario (high EU ETS) pulls UK generation east, tightening UK supply. | H | How to model this in our price simulation | — |
| Gas geopolitical disruption | Norwegian supply ~45–50 bcm (~50% of UK supply). UK statutory margin fell from 127 to 83 mcm/day. UK LNG imports projected to reach 46% of supply by 2035. Strait of Hormuz 2026: gas prices doubled in 48 hours. | H | Precise probability estimates for scenarios (none publicly available from Ofgem) | Are DESNZ/Ofgem confidential scenario parameters ever published in Freedom of Information responses? |

**Sources:** NESO FES 2025; SQ Energy; Modo Energy; NextEnergy Capital; UCL Bartlett; Wood Mackenzie; RAP; ICIS; Statutory Security of Supply Report 2025  
**Files:** `docs/market_research/energy_market_complexity_june2026.md`, `docs/market_research/energy_stress_scenarios_june2026.md`

---

## What we don't know (priority gap list)

Ranked by likely simulation impact:

1. **Historical RO + network charge levels by year (2016-2024)** — ~~DONE~~ (RO/CfD: Phase 21a; Network: Phase 29a; Annex 9 calibration: Phase 29b; CM levy: Phase 30a; FiT levy: Phase 31a; Gas CCL/network/GGL: Phase 30b)
2. **Small supplier opex structure** — how does our 9-customer company compare on cost-to-serve? What's realistic for our scale?
3. **Acquisition cost per channel** — PCW, direct, broker; needed to model acquisition economics properly
4. **Historical SME churn rates** — our churn model parameters are estimated, not calibrated to real data
5. **EPC property-type breakdown at NEED 2026 level** — we have 2019 data; 2026 version may have been published
6. **Novel scenario distribution parameters** — at 70%+ renewables, what parameters define the bimodal price distribution? When does UK grid cross 70%? Negative price frequency trajectory post-2027?

---

## Domain: Market Switching and Customer Flows

| Topic | What we know | Conf | Key gaps | Next question |
|-------|-------------|------|---------|---------------|
| UK household switching volumes | 3.21 million switches in 2024 (up 38% vs 2023, ElectraLink). Crashed to near zero in 2022 when all fixed deals withdrew. | H | Annual switching rates by year 2016-2024 for calibrating sim churn model | Can ElectraLink data be accessed? Or does Ofgem retail market indicators have this? |
| Active vs passive renewal | ~35% of customers actively renew to a new fixed deal; ~65% roll to SVT by default | M | Is this split consistent across residential and SME? | — |
| Win-back conversion | ~5-15% on first outreach wave (cross-sector benchmark; no UK energy-specific figure) | L | UK energy-specific win-back rate | Does any supplier publish this? |

---

## Priority Gap List (ranked by simulation impact)

1. ~~**Historical RO + CfD + network charge levels 2016-2024**~~ — **DONE** (see `historical_policy_costs_2016_2024.md`). RO: £15.6 → £31.8/MWh (2016→2024). CfD: £0 → £11/MWh, **negative in 2022** (crisis rebate). Network: ~£32–46/MWh. All-in non-wholesale: ~£72 (2016) → ~£115 (2024)/MWh.
2. ~~**RO cost as explicit P&L line**~~ — **DONE Phase 21a** (2026-06-21). `simulation/policy_costs.py` with year-indexed lookup tables; `ro_levy_gbp`, `cfd_levy_gbp`, `policy_cost_gbp` now in every electricity settlement record. `net_margin_gbp = margin_gbp - policy_cost_gbp - capital_cost_gbp`. 19 new tests.
3. **Phase 21b: Per-customer net assets tracker** — Ofgem solvency signal (£130/dual-fuel customer floor) missing from LATEST.md
4. **Phase 21c: Consumption recalibration** — C1 electricity 2,800 → 2,500 kWh/yr; C5 SME 15,000 → 10,000 kWh/yr
5. **Novel scenario distribution** — at 70%+ renewables, bimodal price distribution parameters unknown. Negative price frequency trajectory post-2027 (projected regime change). Key research area for forward scenario generation.
6. **Hedge ratio waterfall by forward tenor in LATEST.md** — critical board KPI missing from our reporting
7. **42-day renewal notice CRM flag** — regulatory obligation not currently modeled; affects renewal campaign timing
8. **Active renewer vs SVT roller distinction** — ~35/65 split changes churn dynamics significantly
9. **Debt lifecycle staging** — debt should have states (current → overdue → plan → write-off), not just a flat bad debt %

Last updated: 2026-06-22
