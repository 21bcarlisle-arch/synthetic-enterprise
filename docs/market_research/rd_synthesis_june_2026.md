# R&D Synthesis — June 2026

## What We Learned and What It Means for the Simulation

Four research threads completed in parallel, 21 June 2026:
1. UK EPC open data (consumption profiles)
2. ONS/NEED/Ofgem consumption statistics
3. Ofgem regulatory framework (price cap, licence conditions, BSC)
4. UK energy supplier financial reporting (pending — see separate doc when complete)

---

## Finding 1: Our Consumption Profiles Are Roughly Calibrated, But Can Be Improved

**NEED 2026 medians (England & Wales, 2024 metered data):**
- Residential electricity: 2,500 kWh/year median (Ofgem TDCV: Low 1,600 / Med 2,500 / High 3,800)
- Residential gas: 10,000 kWh/year median (Ofgem TDCV: Low 6,000 / Med 9,500 / High 14,000)
- SME electricity: 8,500–25,000 kWh/year (sector-dependent)

**Current sim vs NEED medians:**

| Customer | Current sim elec (kWh/yr) | NEED target | Delta |
|----------|--------------------------|-------------|-------|
| C1 (resi flat) | 2,800 | 2,500 | +12% high |
| C2 (resi semi) | 3,500 | 2,500–4,100 | In range |
| C5 (SME small) | 15,000 | ~10,000 | +50% high |
| C6 (SME medium) | 45,000 | 25,000–50,000 | In range |

**Priority fix:** C1 electricity is ~12% high; C5 is likely ~50% high. These can be recalibrated.

**EPC data advantage:** The open EPC register (29.2M domestic records) provides property-type × efficiency-band × floor-area × fuel-type distributions. Using EPC data would replace single-point kWh/year estimates with statistically grounded distributions, adding realistic heterogeneity.

**EPC download:** `get-energy-performance-data.communities.gov.uk` — free with GOV.UK One Login. Key field: `ENERGY_CONSUMPTION_CURRENT` (kWh/m²/yr) × `TOTAL_FLOOR_AREA` (m²) = annual kWh. Apply 0.6–0.7 correction factor (EPC SAP methodology overpredicts metered consumption by 50–100%).

---

## Finding 2: The Simulation Is Missing ~£40-50/MWh in Electricity Policy Costs

**Real UK electricity tariff structure (2024-25):**

| Component | £/MWh | % of retail price |
|-----------|-------|------------------|
| Wholesale commodity cost | ~60–90 | ~35–45% |
| Network charges (DUoS + TNUoS) | ~40–50 | ~20–25% |
| Policy costs (RO + CfD + FiT + WHD + ECO) | ~40–50 | ~20–25% |
| Operating cost + regulated margin | ~30–40 | ~15–20% |
| VAT | 5% | 5% |

Policy costs alone:
- **Renewables Obligation: ~£31.80/MWh** (0.491 ROCs × £64.73 buy-out, 2024-25)
- **CfD operational levy: ~£9.26/MWh** (from April 2025)
- Total policy cost on electricity: **~£40-50/MWh**

**Current simulation gap:** Our tariff engine prices at `rolling_spot_mean × (1 + risk_premium)`. Elexon SSP (System Sell Price) is a **commodity-only price** — it does NOT include RO, CfD, network, or operating costs. 

This means:
1. Our absolute tariff levels (and thus revenue £/year) are ~25% of real-world tariff levels
2. Our margin % (-3% to -4.3%) is in a "commodity-only" space — comparable to a supplier's commodity P&L, but missing the network/policy cost layer
3. The cost-to-serve breakdown doesn't show regulatory levies as distinct line items

**Impact on simulation:**
- The commodity P&L is internally consistent — cost and revenue on same basis
- The absolute P&L numbers don't reflect real UK energy supply economics
- A real supplier's all-in cost is ~3× the commodity cost we're modeling

**Priority fix (Phase 21a candidate):** Add explicit policy cost line items to the settlement P&L:
- `ro_levy_gbp = consumption_kwh / 1000 × 31.80` on electricity
- `cfd_levy_gbp = consumption_kwh / 1000 × 9.26` on electricity (from 2025 onwards)
- These make the cost structure auditable and produce realistic absolute margin numbers

---

## Finding 3: Regulatory Solvency Signals Are Missing

**Ofgem capital requirements (effective 31 March 2025):**

| Level | Threshold | Consequence |
|-------|-----------|-------------|
| Capital floor | £0 net assets per customer | Licence violation; notify Ofgem within 7 days |
| Capital target | £130 net assets per dual-fuel customer | Below target = must have capitalisation plan |

**Current simulation gap:**
- Treasury ≤ £0 triggers administration (correct absolute floor)
- But there's no per-customer net assets tracker — a supplier growing customer count without capital is invisible to the current model
- Customer direct-debit credit balances (prepaid float) are not modeled as restricted capital — in reality, they can't be deployed freely

**Priority fix (Phase 21b candidate):** Add `net_assets_per_customer` metric to LATEST.md and annual report:
```
net_assets_per_customer = treasury / active_customer_count
```
Add to administration check: flag when < £130 (capital plan required) and < £0 (licence breach).

---

## Finding 4: BSC Credit Cover Is a Working Capital Drain

**BSC mechanics:**
- Credit Assessment Price (CAP): £350/MWh
- Credit cover = CAP × estimated net energy indebtedness over ~29-day settlement lag
- For a supplier with 9 customers consuming ~1,000 kWh/day total: 
  - Daily volume: ~1 MWh/day × 29 days = ~29 MWh in settlement lag
  - Credit cover required: £350 × 29 MWh = ~£10,150 cash or letter of credit

**Current simulation gap:** Credit cover is not modeled — it would reduce available treasury by ~£10,000-20,000 (the exact figure depends on customer mix and market conditions). For our current treasury of ~£26,000, this would represent ~40% of treasury tied up as Elexon collateral.

**Priority fix:** Deduct BSC credit cover from spendable treasury in the annual report (informational, not P&L impact). Optionally model as a cash hold separate from operating capital.

---

## Finding 5: Price Cap Creates Asymmetric Risk for Fixed vs Variable Tariffs

**Current simulation gap:** All customer contracts are treated identically. In reality:
- **SVT (variable) tariffs**: bounded by price cap; loss-generating in periods where wholesale cost > cap allowance
- **Fixed-rate tariffs**: outside cap; loss risk when customer is locked into a cheap deal pre-crisis and costs spike

**The 2021-22 failure dynamic:** Suppliers with a mix of (a) cheap fixed-rate customers from 2019-2020 + (b) SVT customers hit by the cap lag → losses on both books simultaneously.

Our simulation has implicitly been modeling something like the fixed-rate failure mode (tariff set at renewal based on forward estimate; if estimate is wrong, the company is stuck with that rate until next renewal). The SVT cap dynamic is not separately modeled.

**For simulation fidelity:** Not an immediate priority — our annual renewal model captures the "locked-in wrong rate" risk on fixed terms. The SVT cap lag is a more complex mechanic worth modeling in a later phase.

---

## Finding 6: 75% of Residential Customers Should Be Dual-Fuel

**From HoC Library (Oct 2025):** ~75% of UK residential customers take both gas and electricity from the same supplier.

**Current simulation:** We have dual-fuel gas legs for all customers (C1g, C2g, etc.), but each gas leg is a separate billing account. The dual-fuel account structure exists. The proportion is correct by design.

**Check:** Does our customer portfolio reflect realistic gas vs electricity consumption ratios? Gas-heated residential properties use ~4× more energy in gas than electricity (gas covers space heating + hot water = ~80% of total energy). Our C1g:C1 gas:electricity ratio should be approximately 10,000:2,500 = 4:1. Worth verifying.

---

## Priority Action List for Next Implementation Session

### Immediate (high impact, well-defined):

**Phase 21a — Explicit Policy Cost Line Items**
- Add `ro_levy_gbp` and `cfd_levy_gbp` to electricity settlement records
- Makes cost structure auditable; produces realistic absolute P&L numbers
- RO at £31.80/MWh on electricity volume; CfD levy active from 2025 (or backdate to 2019)
- Requires updating `hedged_settlement.py` and `settlement.py`
- Annual report: add policy cost section to P&L breakdown

**Phase 21b — Regulatory Solvency Dashboard**
- Add `net_assets_per_customer` to LATEST.md and annual report financial summary
- Flag levels: Green (≥£130), Amber (£0–£130), Red (<£0 = licence breach)
- No code change to sim logic — purely informational reporting layer

**Phase 21c — Consumption Recalibration**
- Update C1 electricity: 2,800 → 2,500 kWh/year (align to Ofgem TDCV medium)
- Update C5 electricity: 15,000 → 10,000 kWh/year (align to Bionic microbiz median)
- Test impact on P&L — should modestly improve C5 profitability (less volume = less loss)

### Medium term (well-defined, more effort):

**Phase 22a — EPC-Calibrated Consumption Distributions**
- Download EPC bulk data from MHCLG portal
- Build lookup table: property_type × energy_rating → (kWh/m²/yr distribution, floor_area distribution)
- At customer creation: sample from distribution → compute annual consumption
- Replaces fixed constants with statistically grounded heterogeneous consumption
- Depends on: Phase 21c (baseline recalibration first)

**Phase 22b — BSC Credit Cover Modeling**
- Track Elexon credit cover as a cash hold in treasury
- CAP (£350/MWh) × 29-day rolling settlement exposure
- Report in LATEST.md as "Elexon credit cover: £X,XXX"
- No P&L impact — working capital modeling only

### Later (requires financial reporting research to complete first):

**Phase 23a — Full Tariff Stack (post financial reporting research)**
- Add network charges (DUoS ~£20-25/MWh, TNUoS ~£5-10/MWh) as explicit cost lines
- Brings absolute tariff levels into realistic range (£90-150/MWh vs current ~£30/MWh)
- Major refactor — revisit after financial reporting findings arrive

---

## Finding 7: Real Supplier Margins and P&L Structure (Financial Reporting Research)

See `supplier_financial_reporting.md` for full detail. Key headline figures:

**Gross margin:** Real UK suppliers achieve **8–14% GP margin** in normal years (after commodity + network + levy costs, before opex). Our sim shows -3% gross on a **commodity-only** basis — this is consistent if we add network (~23%) and policy (~13%) costs to both revenue and cost side.

**Net margin:** **1–3% in steady state**; deeply negative in crisis years. Sector lost £4bn cumulatively 2019–2022.

**Bad debt:** 1–2.5% of revenue (direct debit book). Already in our ledger but not reported as a % metric.

**IFRS 9 treatment:** Our simulation's "cost at delivery" model = correct. It matches the own-use exemption that most physical suppliers apply. Mark-to-market derivative swings are an accounting artefact, not economic performance — our model correctly avoids this distortion.

**Board MI confirms a key gap:** Boards watch **Adjusted Net Assets per DFE customer** as the primary regulatory solvency signal. Capital target: £130/DFE customer. Our current treasury (~£26,000) / 9 customers = ~£2,870/customer — technically well above the floor, but this dilutes rapidly as customer count grows. Phase 21b (per-customer net assets tracker) is confirmed as high priority.

**Hedge ratio escalation trigger:** Boards flag when hedge ratio < 50% for any >3-month forward period. Our simulation tracks hedge fraction but doesn't surface this as a board-level alert. Adding a hedge adequacy warning to LATEST.md would be straightforward and high-value.

---

## Calibration Validity Check

A quick sanity check on our current simulation vs real-world benchmarks:

| Metric | Our sim (b29cca9) | Real UK supplier (typical year) |
|--------|-------------------|--------------------------------|
| Gross margin % | -3.0% | 2-5% gross margin on revenue |
| Net margin % | -4.3% | 0-3% net margin (normal) / deeply negative in crisis |
| Commodity P&L only? | Yes | No — real P&L includes all cost lines |
| Treasury floor | £0 triggers admin | £130/customer is regulatory minimum |

**Our -3% gross margin** on a commodity-only basis is worse than what real suppliers achieve, but this is the 10-year average including the 2021-22 crisis. In crisis years, many real suppliers did run deeply negative margins — and went bust. Our supplier survived (positive ledger thanks to non-commodity items), which is plausible for a hedged, cautious operator.

**The policy cost gap:** Adding £40-50/MWh in policy costs to both cost and revenue would leave the margin % roughly unchanged but make absolute numbers realistic. Worth doing for credibility.
