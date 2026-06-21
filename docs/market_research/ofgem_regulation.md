# Ofgem Regulatory Framework — Research Findings

Sources: Ofgem website, Elexon BSC docs, Watt-Logic, HoC BEIS Committee, Wikipedia (2021 gas crisis), GOV.UK

## 1. Default Tariff Cap (Price Cap)

### Scope

- Applies **only to Standard Variable Tariffs (SVTs)** — default fallback rates
- Fixed-rate contracts are **entirely outside the cap** — customers pay contracted rate regardless
- This was the key 2021-22 trap: suppliers with cheap pre-crisis fixed-rate books were honouring below-market prices, unable to pass through costs, while variable-tariff cap lagged spot prices

### Formula (bottom-up, quarterly rebuild)

| Component | % of capped bill |
|-----------|-----------------|
| Wholesale costs | ~40–45% |
| Network charges (TNUoS + DUoS) | ~25% |
| Policy costs (RO, CfD, FiT, WHD, ECO) | ~6–10% |
| Operating costs + regulated margin | ~15% |
| VAT | 5% |

- **Resets quarterly** (Q1: Jan–Mar, Q2: Apr–Jun, Q3: Jul–Sep, Q4: Oct–Dec)
- Wholesale allowance uses ~3.5 months of forward prices — **always stale** relative to spot
- During 2021-22 crisis: cap wholesale allowance was £80–100/MWh below actual procurement cost for unhedged suppliers

### Simulation implication

A supplier's SVT book has a ceiling. The margin on SVT = (capped retail price) - (actual procurement cost). If actual procurement cost exceeds cap allowance, every unit supplied on SVT generates a loss. Model this explicitly by comparing company hedge book cost vs. the cap wholesale allowance each quarter.

## 2. Supplier Licence Conditions (Post-Crisis Reforms, effective 31 March 2025)

### Capital Requirements

| Level | Threshold | Consequence |
|-------|-----------|-------------|
| Capital floor | **£0 net assets per dual-fuel customer equiv** | Serious licence violation; must notify Ofgem within 7 days; revocation risk |
| Capital target | **£130 net assets per dual-fuel customer** (£65 per single-fuel) | Below target: must have credible capitalisation plan |

- Annual adequacy self-assessment is a licence obligation (first due 31 March 2024)

### Credit Balance Ring-Fencing

- Ofgem has directed power to require suppliers deemed "over-reliant" on customer deposits to hold ≥20% of gross customer credit balances as monthly bank balance
- RO receipts must be ring-fenced from Q3 2023 via **RO Credit Cover Mechanism** (hold ROCs or equivalent cash in protected account)
- Customer credit balances (direct-debit float) are **not freely deployable capital**

### Wind-Down Plans

- Suppliers must maintain arrangements so SOLR or special administrator can serve customers
- Assessed annually
- Mutualised cost of SOLR transfers borne by surviving suppliers

### Simulation implication

Model `net_assets / customer_count` as a regulatory solvency signal. Administration trigger should fire well before treasury = 0 if per-customer equity falls below £130 (plan required) or £0 (breach). Customer credit balance (direct debit float from monthly DDI) is a liability, not capital.

## 3. Balancing and Settlement Code (BSC)

### Imbalance Mechanics

Every 30-minute settlement period:
- **Short** (consumed > notified): pay **System Buy Price (SBP)** for shortfall
- **Long** (notified > consumed): receive **System Sell Price (SSP)** for surplus
- Post-P316 reform: single marginal cash-out price (SBP ≈ SSP)

Prices are set by NESO's marginal balancing action cost. In benign markets: ~day-ahead power price. In stress: can exceed £5,000/MWh (e.g. winter 2022-23 acute events; average November 2022 ~£630/MWh).

### Credit Cover Requirement

- Credit Assessment Price (CAP): £350/MWh (reduced from crisis-era levels after Oct 2022)
- BSC party must lodge collateral = CAP × estimated net energy indebtedness over ~29-day settlement lag
- For 50,000 customers consuming ~1,000 MWh/day: credit cover obligation ~£10M in cash or LoCs
- This is real working capital tied up — underestimated by pre-crisis entrants

### Simulation implication

Imbalance cost is non-hedgeable residual risk. Model as ~3–5% volume variance × settlement price. At benign prices (~£50/MWh), a 5% imbalance adds ~£2.50/MWh. At crisis prices (£500/MWh), same imbalance = £25/MWh — enough to wipe out entire margin. BSC credit cover is a working capital outflow; should reduce available treasury.

## 4. The 2021-22 Supplier Failure Wave

### Scale

- 28 supply companies failed by December 2021
- ~4 million customers transferred via Supplier of Last Resort (SOLR)
- Total cost: ~£2.6bn consumer/taxpayer + £1.7bn government intervention (Bulb)
- Major failures: Bulb (1.7M customers), Avro (580,000), People's Energy (350,000)

### Cause: Hedging failure + cap lag, mutually reinforcing

1. **Wholesale gas: +250% surge** Jan–Sep 2021 (£0.50/therm → £2.50+/therm)
2. **Cap lagged by 3–4 months**: wholesale allowance was set before the surge; suppliers were pricing below actual cost on SVT for 1–2 quarters
3. **New entrants under-hedged**: typically 2–6 months forward coverage (Avro: reportedly ~20% hedged). When short hedges expired, forced to buy spot at 5–10× cap allowance
4. **Fixed-rate book losses**: suppliers who had sold cheap fixed tariffs pre-crisis honoured below-market rates while costs exploded
5. **No pre-crisis capital/hedging requirements**: companies grew on customer credit balances, ran naked exposure, then failed instantly

### Simulation validation

The sim's 2021-22 period should show:
- Suppliers with short hedge books going underwater rapidly
- 2–3 quarter lag between wholesale spike and cap catch-up
- Margin recovery only after cap resets fully reflect new wholesale cost levels
- Administration trigger should fire if treasury falls to ≤ £0 (matches current `administration_event` check)

## 5. Renewables Obligation and CfD Levies

### Renewables Obligation (RO)

- **Obligation level (2024-25):** 0.491 ROCs per MWh of electricity supplied
- **Buy-out price (2024-25):** £64.73 per ROC (RPI-linked, up from £59.01 in 2023-24)
- **Effective cost if fully buy-out:** 0.491 × £64.73 = **~£31.80/MWh on electricity**
- ROC market prices typically 5–20% above buy-out (suppliers acquire ROCs at ~£68–78/ROC)
- **Mutualisation ceiling:** £390M for England & Wales; redistributed to compliant suppliers when others fail — a contingent levy on survivors
- **RO ring-fencing** (from Q3 2023): must hold ROCs or cash in RO Credit Cover Mechanism

### Contract for Difference (CfD) Levy

- **Operational Costs Levy (from April 2025):** £9.257/MWh of electricity supplied
- **CfD Supplier Obligation Levy:** variable quarterly — funds difference payments to low-carbon generators
  - When wholesale prices > strike prices: levy goes **negative** (CfD generators pay back; suppliers receive)
  - When wholesale prices < strike prices: levy rises (2021-22: levy reduced/negative due to high prices)
- Total policy cost burden per typical domestic electricity customer (2024): ~£78/year (~9% of capped bill)

### Simulation implication

RO at ~£31.80/MWh is a significant, non-optional electricity cost that our simulation likely isn't modeling explicitly — it's currently bundled into the "cost" side of the settlement. If we're using real Elexon prices as a proxy for all-in commodity cost, the RO may be partially embedded. Should be made explicit in cost-to-serve breakdown. CfD levy is an additional ~£9.26/MWh base.

**Net policy cost on electricity (2024-25):** RO ~£31.80 + CfD ~£9.26 + other levies → total ~£40–50/MWh in policy costs on top of pure commodity cost. This is real — policy costs represent ~25–30% of the wholesale cost of electricity.

## Summary: Key Numbers for Simulation

| Parameter | Value |
|-----------|-------|
| Capital floor (regulatory insolvency) | £0 net assets / customer |
| Capital target (self-assessment) | £130 net assets / dual-fuel customer |
| Cap resets | Quarterly, wholesale allowance ~3.5 months stale |
| Fixed-rate tariffs | Outside cap (separate cost-vs-retail P&L) |
| BSC credit cover rate | ~£350/MWh × 29 days energy indebtedness |
| Imbalance cost (benign market) | ~5% volume × £50/MWh = £2.50/MWh |
| Imbalance cost (crisis) | ~5% volume × £500/MWh = £25/MWh |
| RO levy | ~£31.80/MWh on electricity (2024-25) |
| CfD operational levy | ~£9.26/MWh on electricity (from April 2025) |
| Total policy costs on electricity | ~£40–50/MWh |
| SOLR mutualisation | Contingent levy on survivors when peers fail |

## Priority Simulation Gaps Identified

1. **Per-customer net assets tracker** — regulatory solvency signal missing from dashboard
2. **Explicit RO/CfD cost line** in cost-to-serve (currently buried in commodity cost)
3. **Cap wholesale allowance** tracking vs actual procurement cost — should be visible
4. **BSC credit cover** as working capital outflow (currently not modeled)
5. **Fixed-rate vs SVT distinction** — current sim treats all customers identically; real exposure differs
