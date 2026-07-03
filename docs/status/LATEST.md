## Phase PR + Website Fixes
Last updated: 2026-07-03T20:29:11Z

**Status:** COMPLETE. 15,194 tests passing.

**What changed (PR):**
- `tools/population_anchor.py`: long-run 10-yr comparison + 3-year rolling crisis windows
- overall_rag: AMBER (was false-alarm RED from small-N single-year noise)
- SIM long-run churn 6.4% vs Ofgem 13.6% (ratio=0.47, GREEN)

**What changed (Website fixes):**
- `site/index.html`: fix rendered[] timing bug -- tabs no longer permanently blank if clicked before data loads
- `tools/generate_shadow_html.py` + shadow/supplier: added Regulatory & Compliance Framework (23 SLC obligations) + Business Capability Matrix (6 domains) to supplier shadow page
- Customer portal fix already applied (commit 6725e066): JS string concat bug fixed

**Live URLs:**
- https://poesys.net/state/population_anchoring.json -- AMBER, long-run GREEN
- https://poesys.net/state/billing_ledger.json -- 1,605 invoices
- https://poesys.net/state/customer_sample.json -- behavioral data populated
- https://poesys.net/shadow/supplier/ -- now includes Regulatory + Capabilities sections
- https://poesys.net/customers/ -- customer portal working (login with C1, C_IC1 etc)
