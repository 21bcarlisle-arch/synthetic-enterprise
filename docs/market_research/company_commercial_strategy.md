# UK Energy Supplier Commercial Strategy — Research Findings

Sources: Ofgem State of the Market 2025, NAO supplier market report, Oxera, BFY Group, Citizens Advice, SwitchInsights

## 1. Product Mix: Fixed-Rate vs Variable (SVT)

| Period | % customers on fixed-rate tariff | Drivers |
|--------|----------------------------------|---------|
| Pre-crisis (2019-2020) | ~44–46% | Active PCW switching market; competitive fixed deals 12-18 months ahead |
| Crisis (late 2021 - 2023) | ~15–20% | Suppliers withdrew all fixed deals; hedging impossible at cap-viable prices |
| Recovery (July 2025) | ~33% | Wholesale stabilised; ~2× the proportion vs July 2024 |

**Commercial logic:**
- Fixed tariffs require active forward hedging (credit lines, collateral posting)
- SVT = simpler balance sheet but exposed to quarterly cap revisions
- Small suppliers with weak balance sheets historically ran thin/no hedging → exposed on both sides
- Suppliers offer fixed deals when they hold forward positions locked below market; withdraw when uncertain

**For simulation:** Model fixed vs SVT share as a function of hedging capacity and forward price trajectory. Company should only offer fixed tariffs when it has hedged capacity to back them.

## 2. Customer Acquisition Channels

**PCW dominance:** ~2/3 of all residential switches via price comparison websites (PCWs).
- Top-2 PCWs (Uswitch, MoneySupermarket) = 75% PCW market share
- Top-3 reach 85–90%
- **Any growth-oriented supplier must be listed and competitive on Uswitch + MoneySupermarket**

**PCW commission costs:**
- ~£30–60 per completed dual-fuel customer switch
- Smaller PCWs: £15–25/fuel but face viability problems
- Industry total PCW commissions: £100m+ per year

**Direct/referral acquisition:**
- Much lower per-unit cost but lower volume
- Octopus built referral at scale, reportedly cutting blended acquisition cost by ~31%
- Below ~250k customers, direct acquisition is unlikely to generate meaningful volume

**When to go aggressive vs conservative:**
- Aggressive: forward hedges locked in below market → load customers onto those economics
- Conservative: volatile wholesale → remove tariffs from PCWs entirely to avoid below-cost commitments
- This is the most common behavioural oscillation in the UK market

## 3. Customer Segmentation: Residential vs SME

**SME characteristics:**
- Higher volume per account than residential
- Contracts typically 1–3 years (lower churn than residential)
- Historically less price-elastic than residential PCW switchers
- 42% of SMEs use a TPI/broker — TPI commissions: 2–4% of contract value embedded in unit rate

**Residential characteristics:**
- Price cap backstop protects floor revenue (SVT ceiling)
- PCW-driven annual churn cycle
- Higher operational cost per unit of revenue (small bills, same billing infrastructure)
- Simpler ops — no TPI relationships, credit-checking, or complex billing

**Typical small supplier segmentation path:**
1. Start residential-only (simpler ops, regulated floor, PCW channel works at small scale)
2. Add micro-business/SME at ~100k+ customers when credit and ops infrastructure can support it
3. Build TPI broker relationships as a channel to SME

## 4. Tariff Repricing and Renewal Mechanics

**Regulatory trigger — the 49-day window:**
- Ofgem: customers exempt from exit fees if switching within final **49 days** of fixed contract
- Supplier must issue **Statement of Renewal Terms** at least 42–49 days before expiry
- This is the primary commercial trigger for renewal campaigns

**Renewal campaign timing:** Outreach 4–6 weeks before expiry via email, letter, SMS/app.

**Offer structure:**
- Retention offer: priced between cheapest new-customer PCW rate and SVT roll-off
- New-to-supplier customers come via PCW at cheapest rate (PCW commission is the cost of acquisition)
- Loyal customers rarely get the absolute cheapest deal

**Proactive repricing:** Suppliers almost never proactively cut a customer's SVT rate mid-contract — no competitive pressure to move faster than required. Exception: occasional loyalty campaigns (e.g. Octopus loyalty tariff).

**For simulation:** The 49-day renewal window is our current annual renewal cycle's equivalent. The regulatory requirement to issue renewal terms 42–49 days before expiry means the company should be actively pricing and communicating ~45 days before each contract end-date.

## 5. Minimum Viable Scale

**Ofgem growth pause milestones:**
- Pause at **50,000 customers** (per fuel) for operational capacity and financial resilience assessment
- Pause at **200,000 customers** for second assessment

**Economics at small scale:**
- Opex cap allowance: £97/customer/year
- Embedded EBIT allowance: ~2.5% of ~£1,700 bill = ~£44/customer/year before fixed overheads
- Fixed costs (compliance, risk, treasury, IT): high relative to revenue at <250k customers
- At £44/customer/year EBIT, need ~1m customers to generate ~£44m profit — before fixed overhead

**Hedging and credit at small scale:**
- Sub-200k suppliers historically used licensed intermediaries for balancing (avoid direct credit lines to BM)
- Direct hedging requires credit lines in £hundreds of millions for 100k+ dual-fuel customers
- 100k dual-fuel customers: hedge ~400 GWh/yr electricity + ~1.2 TWh/yr gas. At crisis prices (£200/MWh gas): margin calls + collateral = tens of millions beyond any small supplier's balance sheet without parent backing

**The practical minimum:**
- Self-sustaining with own balance sheet: **~250k–500k dual-fuel customers**
- Below this: fixed cost base (compliance, treasury, risk, IT) unlikely to be covered by EBIT margin without external subsidy or unsustainable corner-cutting on hedging

**Failure data (2010–2022):**
- 73 new suppliers entered; 65 exited
- 29 failures in July 2021 – May 2022: cost ~£2.7bn via SOLR (~£94/transferred customer)
- Bulb (1.5m customers): separate £3bn+ Special Administration — too large for standard SoLR
- Common profile of failed suppliers: negative equity, <50% hedging, financing operations from customer credit balances

## Key Numbers for Simulation

| Metric | Value |
|--------|-------|
| PCW share of residential switches | ~67% |
| PCW dual-fuel commission | £30–60 per customer |
| Fixed tariff % (pre-crisis) | ~44–46% |
| Fixed tariff % (crisis trough) | ~15–20% |
| Fixed tariff % (July 2025) | ~33% |
| Statement of Renewal Terms: days before expiry | 42–49 days |
| Exit fee waiver window | Final 49 days of fixed contract |
| Ofgem growth pause milestones | 50k and 200k customers (per fuel) |
| Opex cap allowance per customer | £97/year (DD, 2025-26) |
| EBIT allowance per customer | ~£44/year (~2.5% of £1,700 bill) |
| Minimum viable scale (own balance sheet) | ~250k–500k dual-fuel customers |
| New suppliers 2010-2022 | 73 entered, 65 exited |
| SME TPI broker penetration | 42% of SMEs use TPI/broker |
| TPI commission | 2–4% of contract value in unit rate |
