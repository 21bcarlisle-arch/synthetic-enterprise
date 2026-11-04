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

### 1a. The book's cost lines beside this stack (N21, 2026-11-04)

The household pages publish "net after cost to serve" at 14.5% of revenue. This table lays the book's lines beside
the stack above.
- **Book:** b3ce2a4e73. 4669d77ddd reads the same to the penny on every line here except back-billing write-offs.
- **Basis:** ex-VAT settlement revenue, 2016 to June 2025, 1,291 per-fuel legs, 5,562 leg-years.
- **Numerator:** revenue less wholesale, the modelled levies, network, capital cost and the flat cost to serve.
- **Denominator:** the same records' revenue.

The page and the ledger are two P&Ls of one book. The page reads the settlement records. The ledger's management
accounts read £3,208,743 of revenue and £839,563 of non-commodity cost, against the settlement records' £3,464,489
and £1,223,851. Gap 5 below measures which is right, line by line.

| Stack line | This stack | The book, as the page counts it | What kind of gap |
|---|---|---|---|
| Wholesale | 35–40% | **42.5%** (£1,470,868). Calm years on the ledger basis: 2019 30.9%, 2020 23.6%, 2024 32.4%. The 2022 crisis year is 99.5%. | **Definition difference.** The book's wholesale is spot or hedge price times settled kWh. This stack's figure includes shaping and balancing. The calm years read low, and **I cannot yet say** whether that is world wholesale or revenue. The measurement is £/MWh against the cap's wholesale allowance per cap period. |
| Network + policy | ~23% + 10–17% | **35.3%** together on the page (£1,223,851; the run JSON does not split them at book level). 26.2% on the ledger basis. | **Within the band on the page.** ECO and WHD are not in `simulation/policy_costs.py`. Whether a supplier this size carried either obligation depends on the scheme thresholds year by year, and that is not established here: **GAP**. |
| Operating costs (service, billing, IT, metering, industry charges) | 17–18% incl. metering. The cap's "operating, debt and industry costs" allowance is £297.92 per dual-fuel DD customer per year (ASSUMPTIONS.md, MARGIN_REALISM Step 3; one period's figure, bundling bad debt and industry charges). | **6.8%** (£236,523). This is the flat £55 per leg per year in `saas/cost_to_serve.py`, about £110 per dual-fuel home, £42.5 per leg-year as realised. | **A cost the company does not bear.** The £55 is an unanchored placeholder (ASSUMPTIONS.md says so). It is the largest single gap: about 9–10 points. The MARGIN_REALISM Step 3 build has been parked since July. The cap's allowance per period is not in the tree: **GAP**. |
| Bad debt | ~1–2.5% (DD book) | **Not on the page.** The ledger carries £68,039 (2.0%) realised and £147,585 (4.3%) provisioned. | **Definition difference.** The company bears it and the page leaves it out. |
| Acquisition / marketing | inside opex (~11% of it) | **Not on the page.** The ledger carries £74,216 (2.1%). | **Definition difference.** |
| Back-billing write-offs, fixed cost, read visits | inside opex | **Not on the page.** The ledger carries £46,984–£50,458, £5,700 and £1,494 (1.5% together). | **Definition difference.** |
| Depreciation | not stated in this stack. The cap's EBIT method counts £90 per customer of fixed assets in capital employed (`price_cap_ebit_allowance.md` §C). | **None anywhere.** The book has £31,688 of capital cost (0.9%), which is a hedge-collateral proxy, not depreciation. | **A cost the company does not bear.** No published depreciation rate is in the tree: **GAP**. |
| EBIT | 1.9–2.4% (`domain_invariants.NET_MARGIN_PCT_OF_REVENUE` holds 2–5%; this file's §2 says 1–3%) | The residual: 14.5% on the page. Deducting the ledger lines the page omits gives about 8.8%. | **Not a cost.** The page's figure is not EBIT, and comparing it with the invariant's band compares two quantities. The library's own two bands also disagree with each other. |

**Read.** Of the roughly 10–12 points between 14.5% and the library's band:
- about 5.7 points are a page definition: costs the ledger bears and the page omits;
- most of the rest is operating cost the company is not charged.

Neither is value created. A margin at this level, taken from a customer billed at the cap, is the M2 shape:
transfer read as margin because the cost that would have absorbed it is missing. Every per-customer CLV inherits it.


#### Gap 5 measured: the ledger and the settlement records, per year and per fuel (a6b7a0fd47 book, 2026-11-04)

**What each figure counts.**
- **Settlement revenue:** `years[y].commodity_split[fuel].revenue_gbp`, ex-VAT, by delivery.
- **Bills ex-VAT:** Σ `total_amount_gbp − vat_gbp` over `bills`, by `period_start` year.
- **EPG:** Σ `epg_support_gbp`, the Treasury's share that the household was not billed.
- **Settlement non-commodity:** the modelled levies plus network cost (`policy_cost_gbp + network_cost_gbp`, and
  their gas pair). This is what the company owes the levy bodies and network operators.
- **Bill non-commodity:** Σ `non_commodity_amount_gbp`, the unit-rate price component the household was billed.
  It excludes the standing charge. This is the figure `saas/ledger.py` books as its non-commodity *cost*
  (`make_non_commodity_cost_event`).

| year | fuel | settlement revenue | bills ex-VAT | EPG | residual | settlement non-commodity | bill non-commodity | gap |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| 2016 | elec | 114,206 | 102,025 | 0 | 12,182 | 53,828 | 36,217 | 17,611 |
| 2016 | gas | 57,583 | 57,150 | 0 | 434 | 16,309 | 14,035 | 2,273 |
| 2017 | elec | 238,958 | 245,914 | 0 | −6,956 | 109,497 | 77,465 | 32,032 |
| 2017 | gas | 115,777 | 115,986 | 0 | −209 | 30,697 | 29,238 | 1,459 |
| 2018 | elec | 232,070 | 231,968 | 0 | 102 | 105,095 | 70,298 | 34,797 |
| 2018 | gas | 121,057 | 122,696 | 0 | −1,640 | 26,078 | 26,546 | −468 |
| 2019 | elec | 215,807 | 220,435 | 0 | −4,628 | 97,229 | 63,200 | 34,029 |
| 2019 | gas | 100,819 | 99,593 | 0 | 1,226 | 22,569 | 25,271 | −2,702 |
| 2020 | elec | 193,072 | 193,384 | 0 | −312 | 93,243 | 60,280 | 32,963 |
| 2020 | gas | 75,246 | 75,233 | 0 | 13 | 18,310 | 21,895 | −3,585 |
| 2021 | elec | 197,828 | 201,216 | 0 | −3,388 | 93,195 | 62,410 | 30,784 |
| 2021 | gas | 75,451 | 76,489 | 0 | −1,037 | 18,696 | 22,660 | −3,965 |
| 2022 | elec | 325,682 | 276,946 | 47,792 | 945 | 96,518 | 70,067 | 26,451 |
| 2022 | gas | 156,998 | 132,538 | 23,506 | 953 | 19,336 | 27,258 | −7,922 |
| 2023 | elec | 462,769 | 332,883 | 130,818 | −933 | 114,135 | 76,926 | 37,209 |
| 2023 | gas | 224,352 | 175,074 | 50,592 | −1,315 | 27,610 | 29,608 | −1,998 |
| 2024 | elec | 289,596 | 287,339 | 0 | 2,256 | 127,028 | 73,409 | 53,619 |
| 2024 | gas | 131,422 | 130,381 | 0 | 1,041 | 28,641 | 26,016 | 2,625 |
| 2025 | elec | 141,072 | 141,877 | 0 | −805 | 64,949 | 26,271 | 38,677 |
| 2025 | gas | 70,818 | 69,608 | 0 | 1,210 | 14,999 | 10,432 | 4,567 |
| **all** | elec | 2,411,061 | 2,233,988 | 178,610 | −1,537 | 954,717 | 616,543 | **338,174** |
| **all** | gas | 1,129,522 | 1,054,748 | 74,098 | 676 | 223,245 | 232,960 | **−9,715** |

**Revenue: the settlement record is right, and the gap was the journal dropping the EPG.**
- Settlement revenue equals bills ex-VAT plus the EPG to within £861 over the whole book.
- The year residuals offset each other. The 2016 electricity +£12k is the largest; it is timing between delivery
  and `period_start`, and is not attributed further.
- `saas.ledger.derive_pnl` already counts the EPG (`ledger_pnl.revenue_gbp` £3,492,488).
- The **management accounts** read £3,283,630. `company/finance/double_entry.to_journal_entry` had no branch for
  `epg_receipt_event` and returned None. Every pound the Treasury paid was dropped: £71,298 in 2022 and £181,410 in
  2023. **Fixed 2026-11-04**, with a control in
  `tests/company/finance/test_the_journal_books_the_treasurys_epg_share_as_revenue.py`.
- Three more event types the ledger emits are still dropped the same way: `revenue_restatement_event`,
  `back_billing_write_off_event` and `dd_back_billing_write_off_event`. Each needs its account pair decided, and
  they are filed rather than guessed.

**Non-commodity: the settlement record is right in kind, and the ledger books a price as a cost.**
- The whole gap is electricity: £338k over the book, £26k–£54k every year. Gas agrees to within 4%.
- The ledger's cost is the unit-rate non-commodity *price* billed to the household. It omits whatever network
  and policy cost the tariff recovers through the standing charge: £268k of electricity standing charge was billed
  over the book.
- A supplier pays the charges the network operators and levy bodies invoice, not what it chose to put in the unit
  rate. The settlement records' modelled levies and network are that cost. Whether they are the *right* levels is
  their own fidelity question (§1a: ECO and WHD absent, GAP).
- The owner is `saas/ledger.py`: book the settlement records' levies and network as the cost event. Until then the
  ledger's gross margin is overstated by about £330k, about 9.5% of revenue.

**N21's margin after this step: 15.50%, unchanged.** Neither fix touches a settlement record, and the page reads
the settlement records (£548,926 over £3,540,583).



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
