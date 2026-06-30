[SIM] SIM/Company Boundary: Is market/ Actually Split?

Before any further coverage sprints, diagnose this -- don't rebuild blind.

market/ has 79 modules but interfaces/ (the epistemic seam) has only 1. That's a stub, not a boundary.

- Audit every module in market/ and classify as: Observable (Elexon price, meter read, network charge -- company can legitimately see this), Sim Internal (demand forecast, forward curve generation, customer life-event modelling -- company must NOT see this), or Hybrid (currently does both, needs splitting).
- Flag specifically: does forward_curve.py (or equivalent) generate prices from an internal model the company reads directly, or does the company only see quoted/actual market prices? Same question for any demand forecasting module.
- Stamp Event Ledger entries with SOURCE: MARKET_OBSERVABLE or SOURCE: CUSTOMER_INTERFACE vs SOURCE: SIM_INTERNAL. No sim-internal events should be readable by company logic.
- Report: module classification list, count of hybrid modules needing split, any confirmed epistemic violations found.

ACCEPTANCE: This is a diagnostic + fix pass, not a rebuild from scratch. Report current state honestly even if it turns out it was already done -- or untouched entirely. Hold further coverage sprints until this report lands. Update PROJECT_STATE.txt and BUILD_STATE.md with the result.