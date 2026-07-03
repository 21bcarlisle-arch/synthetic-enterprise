## Phase PR: Population Anchoring Robustness
Last updated: 2026-07-03T20:13:09Z

**Status:** COMPLETE. 15,194 tests passing.

**What changed:**
- `tools/population_anchor.py`: `_long_run_comparison` added (SIM 10-yr avg vs Ofgem avg)
- `_crisis_churn_direction` now uses 3-year rolling windows (not single-year)
- `crisis_divergence_flag` requires rolling + absolute + N>=10
- `overall_rag` now AMBER (was false-alarm RED from Phase PQ single-year small-N noise)

**KEY FINDING:** SIM long-run average churn 6.4% vs Ofgem 13.6% (ratio=0.47) -- SIM is BELOW market average over full decade.

**Live URLs:**
- https://poesys.net/state/population_anchoring.json -- AMBER, long-run GREEN
- https://poesys.net/state/billing_ledger.json -- 1,605 invoices
- https://poesys.net/state/customer_sample.json -- behavioral data populated
- https://poesys.net/shadow/ -- all 4 sections live
