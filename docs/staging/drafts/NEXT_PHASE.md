# Phase 78 Proposal: Year-indexed non-commodity rates for customer bills

**The gap:** `saas/non_commodity.py` uses flat 2019 baseline rates for electricity non-commodity
(GBP55/MWh resi, GBP42/MWh SME). The simulation settlement layer (Phase 29b) already has
year-indexed network+policy charges. Customer bills therefore show wrong non-commodity
figures: in 2022 the actual network charge jumped to ~GBP73/MWh but invoices still show GBP55/MWh.
This means customers are under-billed for non-commodity by ~GBP18/MWh in the crisis year.

PROJECT_OVERVIEW.md Section 9 explicitly flags this: "Network charges still modeled as flat
pass-through in non_commodity.py rather than year-indexed actuals."

**What to build:**

1. saas/non_commodity.py:
   - Add _NON_COMMODITY_ELEC_BY_YEAR indexed 2016-2024 (resi/SME rates matching Phase 29b).
   - Add _NON_COMMODITY_GAS_BY_YEAR 2016-2024 (GDN + NTS + metering).
   - Update non_commodity_rate(commodity, segment, year=None) to use year-indexed lookup.

2. saas/bill_generator.py:
   - Extract billing year from dates[0] (already available).
   - Pass year=billing_year to non_commodity_rate.

3. Tests (~10 new in tests/saas/test_non_commodity_year_indexed.py).

**Rate calibration (GBP/MWh):**
Elec resi: 2016=52, 2017=54, 2018=53, 2019=55, 2020=57, 2021=62, 2022=73, 2023=80, 2024=74.
SME multiplier: 0.77. Gas resi: 2016=9, 2017=9.5, 2018=10, 2019=11, 2020=11,
2021=12, 2022=15, 2023=16, 2024=14. SME multiplier: 0.80.

**Expected impact:** 2022 invoice non-commodity GBP18/MWh higher than flat baseline.
Restores billing-layer consistency with settlement layer. Portal tariff-compare shows
correct year-indexed costs.

**Files changed:** saas/non_commodity.py, saas/bill_generator.py,
tests/saas/test_non_commodity_year_indexed.py (new). ~10 new tests.
