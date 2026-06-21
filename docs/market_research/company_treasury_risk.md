# UK Energy Supplier Treasury and Hedge Book Governance — Research Findings

Sources: Ofgem financial resilience docs, BIS Bulletin 77, ECB FSR Nov 2022, Bank Underground,
S&P Global (Good Energy), Watt-Logic, ESP Consulting, FIA, ICAEW

## 1. Governance Structure (5,000–50,000 customers)

Three-tier model (SEC/FERC governance standard, adopted by UK consultancies):

**Front Office (Trading Desk):** 1–3 traders. Execute wholesale purchases and financial hedges within limits set by policy. Propose hedge strategy (tenors, instruments, baseload vs. shape).

**Risk / Middle Office:** 1 person at a small supplier, independent of front office, reporting to CFO or CRO (not the trading desk). Marks positions, monitors limit utilisation, raises breaches.

**Risk Committee:** CFO + head of trading + CEO or NED. Sets position limits, approves instrument types, reviews hedging strategy. At small supplier: monthly meeting; daily oversight = CFO reviewing morning risk report.

**Regulatory requirement:** Post-2022 Ofgem rules require CFO sign-off on annual financial adequacy self-assessments including hedging strategy disclosures. Board directors personally accountable.

## 2. Hedging Strategy: The Layered Ladder

**Not a single forward purchase** — position built incrementally:
- Buy ~1/5 of a quarter's baseload demand at the start of each of 5 preceding quarters
- A Q4 delivery would be partially bought from Q3 the prior year through Q3 of the delivery year
- Averages out price timing risk (avoids over-exposure to any single market date)

**Named public disclosure:** Good Energy (Oct 2021) disclosed ">90% hedged for next 12 months" — the most concrete named hedge ratio from a UK supplier, cited specifically to show insulation from the spot spike.

**Failed supplier pattern:** 22 of 26 failed suppliers directly cited inadequate hedging as a key failure reason (BEIS/Ofgem post-crisis evidence).

**Realistic hedge coverage by horizon (prudent mid-size supplier):**

| Horizon | Target hedge ratio |
|---------|-------------------|
| 18–24 months out (S-2) | 20–40% (liquidity and market depth permitting) |
| 6–12 months out (S-1) | 50–75% (bulk position built here) |
| 0–3 months out | 80–100% (topped up; residual on day-ahead/intraday) |

**Wholesale market liquidity:** Typically 1–3 years for gas/power in the UK. Very illiquid beyond 3 years for smaller counterparties.

**Shape risk:** Baseload blocks bought on forward markets; shape (hourly profile vs. flat) settled via BSUoS imbalance mechanism or shorter-dated products.

## 3. Credit, Collateral, and Credit Lines

**Exchange-cleared futures (ICE/EEX):**
- Initial margin: 4–15% of notional in normal conditions
- 2022 crisis peak: **60–80% of notional** (ICE rose 6× between Jan–Apr 2022)
- Variation margin: cash-settled daily (sometimes intraday)
- EEX peak: ~60% of notional

**OTC bilateral (EFET/ISDA Master + CSA):**
- Negotiated credit limits per counterparty (typically £5–20m net exposure for mid-size supplier)
- May have zero or low initial margin requirements for creditworthy counterparties
- Less cash-intensive than exchange clearing — many suppliers shifted OTC during 2022 to reduce IM burden
- OTC trading still fell ~50% in 2022 as counterparties tightened bilateral limits

**Bank credit lines for a 5k–50k customer supplier:** £5–50m revolving credit facility (RCF)
- Used to post initial margin on exchange positions
- Bulb (1.7m customers): needed "hundreds of millions" in collateral — unavailable from banks post-crisis
- UK Energy Markets Financing Scheme (£40bn ceiling, Oct 2022): received **zero applications** — prices fell before drawdown needed, and BB-/Ba3 credit requirement excluded most small suppliers

## 4. Mark-to-Market and Cash Buffers

**For a supplier hedging 1 TWh gas/year at £50/MWh:**
- Notional: £50m
- Cash reserve for 20% adverse price move: **£10–30m** liquid (varies with margin rate and position split)
- Liquidity waterfall: cash → RCF drawdown → parent guarantee

**BIS evidence:** Margin requirements doubled by mid-2022; credit lines to power producers grew from ~€3bn to €6bn between March–April 2022 alone (illustrates velocity of cash demand).

**Practical tools:**
- Mix exchange-cleared + OTC bilateral to manage margin
- Liquidity swaps with banks (exchange futures for swaps, avoiding initial margin)
- Shift to nearer-dated products to reduce open position size
- Maintain minimum liquidity waterfall buffer at all times

## 5. Counterparty Risk

- **OTC bilateral:** EFET General Agreement or ISDA Master + CSA. Bilateral credit limits negotiated. EFET eCredit Matrix Standard governs limit exchange with brokers.
- **Exchange-cleared:** Counterparty risk → CCP risk (ICE Clear Europe, ECC). Considered remote.
- **SoLR risk:** If counterparty supplier fails mid-hedge, positive-value hedges remain with insolvent estate. SoLR gets customers but not hedges → exposed to spot. This systemic risk drives Ofgem's capital adequacy rules.

## 6. Daily/Weekly Treasury Reporting

**Daily (risk morning report):**
- Net open position by commodity and tenor
- Hedge ratio vs. forecast demand (% hedged by month/quarter)
- Prior day's MTM P&L on hedge book
- Variation margin paid/received
- Available liquidity: cash + undrawn RCF vs. worst-case 5-day margin estimate
- Limit utilisation vs. board-approved VaR/position limits

**Weekly (CFO/Risk Committee pack):**
- Hedge ratio waterfall (% hedged by quarter for next 8 quarters)
- VaR or Cashflow-at-Risk (CFaR): 95th percentile loss over 10 trading days
- Credit exposure by counterparty vs. approved bilateral limits
- Collateral posted (IM at exchanges + CSA collateral at OTC counterparties)
- Cash headroom vs. stress scenario (e.g., if margin doubles)
- Price vs. price cap comparison — are current hedges supporting sustainable tariffs?

**Systems:** ETRM platforms (Hitachi Energy, PCI, Openlink) at larger suppliers; spreadsheet-based position books at smaller ones.

## 7. Stress Testing (Standard Scenarios)

| Scenario | Tests |
|----------|-------|
| 2021-22 price spike replay (gas 10× in 6 months) | Can supplier survive 90 days without new borrowing? |
| Warm winter: consumption 15-20% below forecast | Over-hedging exposure; forced sell-back at loss |
| Counterparty failure mid-contract | Replacement cost; credit exposure concentration |
| Price cap squeeze: wholesale rises faster than cap | Gap between cap observation and implementation (4.5m lag) |
| Combined liquidity stress: 20% adverse price + 50% credit line reduction | The scenario that killed 22 of 26 failed suppliers |

**Ofgem requirement (from 2025):** Internal stress testing methodology included in annual financial adequacy self-assessment, signed by CFO.

## Key Numbers for Simulation

| Parameter | Value |
|-----------|-------|
| Target hedge ratio (12m out) | 70–90% of forecast volume |
| Target hedge ratio (6m out) | 85–95% |
| Target hedge ratio (0–3m out) | 90–100% |
| Target hedge ratio (18–24m out) | 20–40% |
| Exchange IM rate (normal) | 4–15% of notional |
| Exchange IM rate (2022 crisis peak) | 60–80% of notional |
| RCF size (5k–50k customers) | £5–50m |
| Regulatory capital floor (2025) | £57.50/domestic customer (= ~£115/dual-fuel customer; cf. Ofgem: £65/single-fuel, £130/dual-fuel) |
| Failed suppliers due to bad hedging | 22 of 26 |
| Good Energy hedge ratio (Oct 2021) | >90% for 12m |

**Note on capital floor discrepancy:** Treasury research cites £57.50/domestic customer (Ofgem Powering Trust April 2025 report). Regulation research cites £65/single-fuel and £130/dual-fuel customer (Decision doc July 2023). May reflect different document vintages or definitions; use £130/dual-fuel as the canonical regulatory target.

## Implications for Simulation

| Gap | Priority | Fix |
|-----|----------|-----|
| Hedge ratio by tenor not tracked | High | Add portfolio hedge ratio waterfall (% hedged by quarter forward) to board reporting |
| No formal risk committee structure | Medium | Model company as having CFO-level approval gate for major hedge decisions |
| Cash buffer for margin calls | Medium | Reserve a portion of treasury as "collateral buffer" = IM_rate × notional position |
| Stress test tracking | Low | Add a simple stress test result to LATEST.md (e.g., "treasury at 20% adverse price move: £X") |
| 22/26 failure rate from under-hedging | Calibration | If sim's hedge ratio falls below 50% for >3m forward, flag as "elevated failure risk" |
