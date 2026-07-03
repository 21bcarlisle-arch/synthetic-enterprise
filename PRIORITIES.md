# PRIORITIES.md — Synthetic Enterprise

## Next (highest priority)

### NT: SVT Positioning Intelligence — Company Uses Public Ofgem Cap Data

**Gap served**: Company churn model is blind to whether customers are positioned better or worse
than the Ofgem SVT cap. A real supplier DOES know this (SVT rates are public data published
quarterly by Ofgem). Currently the enriched_churn_estimate uses rate-vs-prior-term but not
rate-vs-SVT. In 2022, customers on our pre-crisis fixed rate of 20p/kWh were BETTER than
SVT (28-52p) -- zero switching incentive. In 2019, customers at 18p when SVT was 17p had
NEGATIVE positioning -- more likely to switch. This is fully epistemic (company reads Ofgem
public data, not SIM internals).

**Fidelity gain**: Company churn estimate now reflects the rate-vs-market observation that
is the PRIMARY driver of switching (per Phase NS research). Closes the epistemic gap between
what the company CAN observe and what it currently uses.

**Implementation outline**:
- `company/crm/svt_positioning.py`: `svt_rate_at_date(date_str)` reads Ofgem cap data;
  `rate_vs_svt(customer_rate, date_str)` -> pct differential;
  `svt_positioning_churn_signal(rate_vs_svt_pct)` -> float [0, 1] churn risk signal
- Wire into enriched_churn_estimate as optional `svt_differential_pct` param
- Board section: per-year table showing portfolio average rate vs SVT cap

---

## Backlog

### NU: Crisis Tariff Strategy — No Fixed Deals When Cap Below Wholesale
When SVT cap rate is below what we can profitably offer on fixed (2022 scenario), the company
should NOT offer new fixed deals. Currently run_phase2b generates fixed-rate terms even in
crisis periods. Real-world fidelity: suppliers withdrew fixed products in H2 2021 and 2022.
This would affect renewal outcomes and capital deployment.

### NV: Gas Market Churn Alignment
Gas customers currently share the electricity billing-account churn decision. But gas churn
drivers differ slightly -- gas is more inertial (fewer comparison sites; no smart meter visibility).
An independent gas churn propensity model would increase segment accuracy.

### NW: Company SVT Rate vs Cap Revenue Leakage Report
Board should track: "are we leaving money on the table vs SVT?" In years where SVT > our rate,
we under-charge customers who would accept higher prices. In years where SVT < our rate, we risk
outpricing the market. Bridges SVT data (Phase 39a) to commercial strategy.
