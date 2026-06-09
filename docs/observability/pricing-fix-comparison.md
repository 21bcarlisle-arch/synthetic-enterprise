# Pricing Fix Comparison — Flat Margin vs Activity-Based

**Generated:** 2026-06-09  
**Baseline:** Phase 2a (6-customer, flat 5% margin, `forward_price × 1.05`)  
**Repriced:** Phase 2a repriced (activity-based, `forward_price + capital_cost_per_mwh + £2/MWh`)  
**Window:** 2016-01-01 → 2025-06-07 (9.5 years)  
**Capital costs:** Identical in both runs — same risk physics, different tariff formula only.

---

## Formula Change

**Old (flat margin):**
```
unit_rate = forward_price × 1.05
```

**New (activity-based):**
```
sigma_stressed = 0.50 (pre-2023) or 1.50 (post-2023)
expected_capital_cost_per_mwh = Z_SCORE × sigma_stressed × forward_price × WACC
                               = 1.645 × sigma_stressed × forward_price × 0.10
unit_rate = forward_price + expected_capital_cost_per_mwh + 2.00
```

Effective multiplier: ×1.08225 + £2 (pre-2023) vs ×1.24675 + £2 (post-2023).
The old 5% flat was systematically under-priced, especially post-2023 (24.7% stressed premium vs 5%).

---

## Per-Customer Comparison

| Customer | Old tariff avg | New tariff avg | Old 9yr net | New 9yr net | Change |
|----------|---------------|---------------|-------------|-------------|--------|
| C1 (resi, 2.8k kWh, PC1) | £178.17/MWh | £190.75/MWh | £2,384.14 | £2,809.05 | +£424.91 |
| C2 (resi, 3.5k kWh, PC1) | £181.19/MWh | £199.15/MWh | £1,815.75 | £2,333.64 | +£517.89 |
| C3 (resi, 3.2k kWh, PC1) | £123.81/MWh | £134.52/MWh | £514.77 | £887.01 | +£372.24 |
| C4 (resi, 5.5k kWh, PC1) | £172.68/MWh | £184.75/MWh | £1,149.72 | £1,547.60 | +£397.88 |
| C5 (SME, 25k kWh, PC3) | £178.17/MWh | £190.75/MWh | £4,013.21 | £5,481.76 | +£1,468.55 |
| **C6 (SME, 45k kWh, PC3)** | £181.19/MWh | £199.15/MWh | **-£1,175.64** | **+£619.62** | **+£1,795.26** |

*Tariff averages are term-start-weighted means across 9–10 annual terms per customer.*  
*C1 and C5 share term start dates (and therefore forward prices and unit rates). Same for C2/C6.*

---

## Portfolio Summary

| Metric | Old (Phase 2a) | New (repriced) | Change |
|--------|---------------|----------------|--------|
| Gross margin | £25,720.70 | £30,697.42 | +£4,976.72 |
| Capital costs | £17,018.75 | £17,018.75 | 0 (unchanged) |
| Net margin | £8,701.95 | £13,678.67 | +£4,976.72 |
| Starting treasury | £18,416.67 | £18,416.67 | — |
| Final treasury | £27,118.62 | £32,095.34 | +£4,976.72 |
| Capital cost ratio | 66.2% of gross | 55.4% of gross | -10.8pp |
| Context Handshake wake-ups | 0 (all 401) | 0 (threshold not reached) | — |

---

## Year-by-Year Net Margin Comparison

| Year | Old net £ | New net £ | Diff £ | Note |
|------|----------|----------|--------|------|
| 2016 | 290 | 461 | +171 | |
| 2017 | 845 | 1,080 | +235 | |
| 2018 | 379 | 591 | +212 | |
| 2019 | 1,068 | 1,279 | +211 | |
| 2020 | 815 | 1,008 | +193 | |
| 2021 | -1,600 | -1,325 | +275 | CRISIS — pricing fix softened the blow |
| 2022 | 1,248 | 1,841 | +593 | CRISIS — tariff uplift fully captured |
| **2023** | **5,127** | **6,235** | **+1,108** | Post-2023 sigma×1.50 premium materialises |
| 2024 | 666 | 2,011 | +1,345 | Full post-2023 premium in force |
| 2025 | -135 | 496 | +631 | 2025 flips positive under new pricing |

---

## Key Findings

### 1. C6 flipped from net-negative to net-positive (+£1,795)

C6 was the headline failure of Phase 2a: 9.5 years of operation, net -£1,176. The root cause
was flat-margin pricing that didn't load capital costs into the tariff. Under activity-based
pricing, C6's gross margin rose from £5,294 to £7,089 (+£1,795), bringing it above its capital
cost of £6,470. Net margin: -£1,176 → +£620. C6 is viable — the issue was pricing, not the
customer.

### 2. The capital cost increase is fully pre-priced

The formula loads `expected_capital_cost_per_mwh` into the tariff at the time of contract
signing, so the supplier is never surprised by the capital drain. The actual capital costs
charged against the treasury remain unchanged (same risk physics), but the tariff now
recovers those costs from the customer.

### 3. Post-2023 pricing swing is largest (+£1,000+/year)

The sigma_stressed jump from 0.50 to 1.50 at 2023-01-01 triples the capital cost loading
in the tariff. In 2023, this coincided with crisis-era tariffs still being collected against
rapidly falling spot prices — net margin jumped from £5,127 (old) to £6,235 (new). In 2024,
the improvement was £1,345 as post-2023 tariffs continued loading the 1.50 sigma premium.

### 4. Context Handshake: 0 wake-ups under recalibrated thresholds

With `VAR_BREACH_MULTIPLIER = 2.50` and the treasury health gate (`new_treasury < 1.5 ×
starting = £27,625`), the committee was never triggered. The treasury climbed to £32,095 —
comfortably above the health gate threshold throughout 2023–2025. The VaR ratio peaked in
2021–2022 but activity-based pricing reduced stress enough that 2.50× was never breached
sustainably. This is the correct behaviour: the committee should sleep during healthy growth.

### 5. Activity-based pricing is size-neutral per MWh

The formula's eac_mwh terms cancel, so every MWh sold at the same forward price and in the
same regime carries the same capital cost per MWh — regardless of customer size. C6 (45k kWh)
and C2 (3.5k kWh) share the same unit rate when their contracts start on the same date. The
_absolute_ capital cost difference between them is proportional to their size, but their
tariffs recover that cost at the same per-MWh rate.

---

## Open Questions for Phase 2b

1. **Gas dual-fuel tariff**: same activity-based formula applies, but `sigma_stressed` must
   account for gas commodity volatility separately from electricity. If gas sigma is higher
   than electricity sigma in a given period, tariffs should reflect that.
2. **Context Handshake SDK**: the `anthropic` Python SDK is not installed in the system
   Python 3.14 environment. The lazy import in `sim/risk_committee_agent.py` means the
   committee fails gracefully (error caught by try/except), but no real interventions have
   ever landed. Installing the SDK or using an alternative invocation path is Phase 2b pre-work.
3. **Evolution rule under activity-based pricing**: the repriced run inherited the same hedge
   trajectory as Phase 2a (agents reset to 0.50 at start). A separate question: does
   activity-based pricing change the evolution equilibrium? The committee context now
   correctly priced, so if the committee could fire, would it see different signals?
