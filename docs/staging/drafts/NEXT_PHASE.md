# Phase 142 — Green Tariff Product Catalogue

**Status:** Draft proposal  
**Proposed by:** Claude Code autonomous session, 2026-06-26  
**Opt-out window:** 4 hours from NTFY. Will proceed unless redirected.

---

## Context

The company now has:
- REGO procurement and retirement (Phase 139): buy/retire REGOs, coverage_check() against
  consumption, 2022 crisis spike to £6.50/MWh correctly modelled.
- Renewal pricing engine (Phase 136): generates 3-option renewal packs priced from observable
  market data (fixed 1yr/2yr/variable SVT).
- Fuel mix disclosure (Phase 111): full UK grid mix 2016-2025 (24.6% → 55% renewable).

What doesn't exist yet: a **tariff product catalogue**. UK energy suppliers don't sell "a tariff"
— they sell named products (e.g., "Green Flex 1yr", "Octopus Go", "EDF Clean Energy Fix").
Each product has eligibility criteria, a green certification status, and a REGO backing requirement.

This matters because:
1. Ofgem's Fuel Mix Disclosure rules tie "100% renewable" marketing claims to REGO coverage.
   The company needs to know WHICH of its products make green claims before the REGO check runs.
2. Tariff comparison websites (USwitch, MoneySuperMarket) display named products — the company's
   product catalogue defines what appears there.
3. Renewal packs (Phase 136) currently label options "Fixed 1yr" / "Fixed 2yr" / "Variable SVT".
   Real suppliers attach product names and marketing copy to each option.

---

## Proposed Change

New file: `company/billing/tariff_products.py`

```python
from dataclasses import dataclass, field
from typing import Optional

@dataclass(frozen=True)
class TariffProduct:
    code: str               # e.g. "GREEN_FIX_1YR_2024"
    name: str               # e.g. "Green Fix 1 Year"
    commodity: str          # "electricity" | "gas" | "dual"
    segment: str            # "resi" | "sme" | "ic" | "all"
    term: str               # "fixed_1yr" | "fixed_2yr" | "variable"
    is_green: bool          # makes "100% renewable" claim
    rego_required_pct: float  # fraction of consumption needing REGO backing
    unit_rate_premium_pct: float  # premium above base renewal price
    launch_date: str        # YYYY-MM-DD
    withdrawal_date: Optional[str] = None  # None = still active
```

`TariffCatalogue`:
- `_PRODUCTS`: hardcoded catalogue of 7 realistic UK products spanning 2016-2025
  (Green Fix 1yr/2yr, Standard Fix 1yr/2yr, Variable SVT, SME Fixed, I&C Baseload)
- `active_products(date_str)` — products within launch/withdrawal window
- `products_for_segment(segment, date_str)` — eligibility filter
- `green_products(date_str)` — is_green=True products
- `get_by_code(code)` — lookup
- `rego_requirement_mwh(consumption_kwh, product_code)` — consumption × rego_required_pct / 1000
- `summary(date_str)` — active count, green count, by-segment breakdown

---

## Tests (9 planned)

1. TariffProduct construction with all fields
2. active_products() returns only products in valid date window
3. Withdrawn products excluded from active_products()
4. products_for_segment() filters correctly (resi vs SME vs IC vs all)
5. green_products() returns only is_green=True products
6. get_by_code() lookup returns correct product
7. rego_requirement_mwh() correct at 100% and 50% requirement levels
8. summary() returns expected active count and green count
9. No REGO requirement for non-green products (rego_required_pct=0.0)

---

## Fidelity delta

UK suppliers maintain a formal product catalogue that determines what appears on price comparison
websites and what REGO backing they must hold. The green_products() filter is the gate that runs
before coverage_check() (Phase 139) — you only need REGOs for products that make green claims.
Phase 142 makes this connection explicit: the company knows which products are green, computes
REGO obligations from that, and can audit coverage before publishing marketing claims.

---

## Dependencies

- company/market/rego_portfolio.py (Phase 139) — coverage_check() called with output of
  rego_requirement_mwh()
- company/billing/renewal_engine.py (Phase 136) — product codes can be attached to RenewalQuote
  in a future phase (optional linkage, not required for Phase 142)
- No SIM internals accessed — pure company-layer module
