# UK Energy Supplier Financial Reporting — Research Findings

Sources: OVO Energy accounts (Watt-Logic analysis), Octopus FY24/25 results, Ofgem CSS framework, 
HoC Library, KPMG IFRS 9 briefings, BEIS Select Committee evidence

## 1. P&L Cost Structure

### Direct cost of sales (Cost of Goods Sold)

| Line | % of revenue | Notes |
|------|-------------|-------|
| Wholesale energy cost | 35–40% | Forward contracts; physical + financial; net cost incl. shaping/balancing |
| Network charges | ~23% | Electricity: TNUoS + DUoS; Gas: NTS + LDZ — pass-through regulated tariffs |
| Environmental/policy levies | 10–17% | RO, CfD, FiT, WHD, ECO — essentially statutory pass-throughs |

### Operating expenses (below gross profit)

| Line | £/customer/year | Notes |
|------|----------------|-------|
| Customer service / back-office | ~£97 | Ofgem cap opex allowance (DD customer, 2023-24) |
| Bad debt (direct debit) | ~£26 / ~1% of bill | Cap allowance; actual sector average OVO ~1.4–2.6% |
| Bad debt (standard credit) | ~6% of bill | Much higher; PPM customers ~2-4% |
| Marketing / acquisition | ~11% of opex | Embedded in opex allowance |
| Smart metering / IT | Material | Separate from opex allowance; Ofgem review ongoing |

### Full tariff stack (indicative domestic dual-fuel household 2024)

| Component | % of bill |
|-----------|----------|
| Wholesale energy | 35–40% |
| Network charges | ~23% |
| Policy/environmental levies | 10–17% |
| Supplier opex + metering | 17–18% |
| EBIT allowance | 1.9–2.4% |
| VAT | 5% on ex-VAT |

## 2. Real Supplier Gross and Net Margins

### OVO Energy (most multi-year transparency)

| Year | Revenue | Gross Profit | GP% | Net Profit | Net% | Note |
|------|---------|-------------|-----|-----------|------|------|
| 2021 | £0.96bn | £99m | 10.3% | £279m | 29% | Incl. £429m derivative gain |
| 2022 | £5.04bn | £387m | 7.7% | -£1.27bn | -25% | Incl. £1.446bn derivative loss |
| 2023 | £8.17bn | £884m | 10.8% | £810m | 9.9% | Incl. £1.086bn derivative gain |
| 2024 | £5.46bn | £760m | 13.9% | -£110m | -2.0% | Bad debt £212m, admin £562m |

### Octopus Energy Group

| Year | Revenue | GP% | Net% | Note |
|------|---------|-----|------|------|
| FY23 | ~£13bn | n/a | 1.6% | No derivative distortion; underlying |
| FY24 | £12.4bn | 9.0% | 0.7% | Incl. Shell Energy UK acquisition |
| FY25 | £13.7bn | n/a | -1.9% | £144m exceptional + £103m warm weather |

### Utilita Energy (PPM specialist)
- Revenue ~£1bn, Gross profit ~£178m = **~17.8% GP margin**
- Higher margin due to digital-first model; lower cost-to-serve

### Sector-wide EBIT (Ofgem confirmed)
- 2019–2022 cumulative: **-£4bn** (sector in aggregate loss for 4 years)
- 2023: **+£2.57bn** (price cap over-recovery after crisis; not normalized profit)
- 2024: **+£0.84bn provisional** (returning to more normal)
- Ofgem cap EBIT allowance: **1.9% of revenue** (raised to reflect 12.3% CoC in 2023)

### Key takeaways for simulation calibration

**Gross margin target:** ~8–14% of revenue in normal years (pre-opex)  
**Net margin target:** 1–3% in steady state; negative during crisis years  
**Bad debt:** model at 1–2.5% of revenue (DD book), 4–6% (standard credit)  
**Derivative remeasurement:** keep separate from underlying P&L — headline statutory profits are misleading

## 3. IFRS 9 Hedge Accounting Treatment

Three approaches, commonly mixed:

### A. Own-use exemption (most common for physical supply)
- Forward contracts for physical delivery of gas/power → scoped OUT of IFRS 9
- No fair value recognized until delivery — energy cost only hits P&L when energy delivered to customers
- If contract becomes onerous (purchase price > cap/tariff revenue): recognize provision immediately
- Effect: smooth P&L closely tied to actual energy flows; no mark-to-market volatility
- **The right model for our simulation's commodity cost**

### B. Fair value through profit or loss (FVTPL)
- Financial (net-settled) derivatives → fair value changes hit income statement every reporting period
- Caused OVO's wild swings: £1.446bn MTM loss (2022) → £1.086bn MTM gain (2023)
- "Real" cash position unchanged — just the fair value of forward book remeasured
- Net profit % becomes misleading without adjusting for these items

### C. IFRS 9 cash flow hedge accounting
- Designate financial derivatives as cash flow hedges of forecast energy purchases
- Fair value change → **OCI** (not P&L)
- Recycled to P&L when hedged energy actually delivered
- Produces smooth P&L; derivative remains on-balance-sheet at fair value
- Requires hedge effectiveness testing; documentation burden

### In practice
- Boards monitor "underlying" or "adjusted EBIT" — strips out derivative remeasurement
- Statutory accounts can look wildly different from economic performance in same period
- Our simulation's own-use model (cost at delivery) = closest to approach A; this is correct

## 4. Board MI — What Suppliers Monitor

### Monitoring cadence

| Frequency | Key metrics |
|-----------|------------|
| **Daily** | Treasury position, hedge MTM, credit limits (Elexon credit cover) |
| **Weekly** | Customer net position (gains/losses), call centre KPIs, bad debt aging |
| **Monthly** | Full underlying P&L, margin bridge, working capital, hedge ratio report, arrears balance |
| **Quarterly** | Board pack: capital adequacy, Ofgem regulatory returns, forward 12-month margin forecast |
| **Annually** | CSS to Ofgem, statutory accounts, financial resilience stress test |

### Financial KPIs (monthly board pack minimum)

- **Gross margin per customer** (£/customer/month) vs. budget and prior year
- **Unit margin** (p/kWh retail minus p/kWh blended procurement cost)
- **Hedge ratio by forward period** (% of forecast volume hedged, month by month, 12–24 months out)
- **Mark-to-market value of forward book** (underlying position)
- **Adjusted Net Assets per DFE customer** (Ofgem regulatory capital metric)
- **Liquidity runway** (months of operating cash at current burn)
- **Bad debt / arrears balance** (£m at >30, >60, >90 days)
- **Bad debt provision % of debtors**
- **Customer credit balance exposure** (DD float — a liability, not an asset)

### Customer KPIs (monthly)

- Accounts gained / lost (gross adds, churn rate)
- Switching rate vs. market average
- Customer lifetime value by segment
- Cost to acquire
- Cost to serve (£/customer/year by segment)
- NPS / complaints per 100,000 accounts (Ofgem publishes league tables)

### Operational KPIs (weekly)

- Call centre handling times, first-call resolution, wait times
- Billing accuracy / billing exceptions
- Meter reading completeness
- Smart meter installation rate

### Regulatory KPIs (monthly)

- Price cap compliance check
- WHD / ECO obligation progress
- Complaints to Ombudsman / Ofgem escalation rate

### Escalation triggers

| Trigger | Action |
|---------|--------|
| Hedge ratio < 50% for any >3 month forward period | Immediate CFO/Board notification |
| Adjusted Net Assets approaching Capital Floor | Mandatory Ofgem engagement |
| Bad debt run rate > 20% above cap allowance | Reserve review |
| Single major counterparty failure | Stress test review |
| Wholesale price spike >30% vs. hedged position within cap period | Margin squeeze alert |
| Customer churn rate > 15% annualised | Tariff competitiveness investigation |

## 5. Implications for the Simulation

### What we're modeling correctly (own-use approach)
- Energy cost hits P&L on delivery — correct
- Hedge fraction reduces exposed volume — correct
- Capital cost on unhedged (naked) volume — correct proxy for BSC credit cost

### What's missing or wrong

| Gap | Priority | Fix |
|-----|----------|-----|
| Policy costs (~£40-50/MWh electricity) | High | Add explicit RO + CfD levy to settlement P&L |
| Network charges (~£23% of bill) | High | Add explicit DUoS/TNUoS to settlement P&L |
| Operating cost line (£97/customer/year) | Medium | Already partially in cost-to-serve; make explicit |
| Bad debt as P&L line | Medium | Already in ledger (bad_debt_event); quantify as % of revenue |
| Per-customer net assets (capital adequacy) | High | Add regulatory solvency metric to reports |
| BSC credit cover as working capital hold | Low | Informational; deduct from spendable treasury |
| Derivative MTM distinction | Low | Own-use approach is already correct; no change needed |
| Gross margin % target | Calibration | At full tariff stack: ~8-14% GP; current -3% is commodity-only |

### Target metrics for simulation health check

| Metric | Target (normal year) | Current sim | Gap |
|--------|---------------------|-------------|-----|
| Gross margin % (full cost stack) | 8–14% | -3.0% (commodity only) | Need policy costs in denominator |
| Net margin % | 1–3% | -4.3% (commodity only) | Same; plus opex missing |
| Bad debt % revenue | 1–2.5% (DD book) | In ledger but not reported as % | Reporting gap |
| Net assets / customer | ≥£130 (regulatory target) | ~£2,870 (treasury/9 customers) | OK but should track dynamically |
| Hedge ratio (12m forward) | 80–90% | Tracked internally | OK |

## Key Sources

- Octopus FY24/FY25: https://octopus.energy/press/octopus-energy-group-results-for-fy24-delivered-07-profit-margin-tripled-non-uk-customer-base-and-increased-net-assets-to-17bn/
- OVO multi-year analysis (Watt-Logic): https://watt-logic.com/2026/02/04/ovo-energy-looking-shaky/
- IFRS 9 own-use / hedge accounting: https://www.footnotesanalyst.com/commodity-price-risks-volatility-hedging-and-own-use/
- Ofgem CSS framework: https://www.ofgem.gov.uk/transparency-document/energy-companies-consolidated-segmental-statements-css
- Ofgem opex consultation: https://www.ofgem.gov.uk/consultation/energy-price-cap-operating-cost-and-debt-allowances-consultation
- HoC Library electricity bill breakdown: https://commonslibrary.parliament.uk/research-briefings/cbp-10505/
