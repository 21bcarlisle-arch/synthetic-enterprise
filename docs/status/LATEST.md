## Phase PR + Website Fixes
Last updated: 2026-07-03T21:11:41Z

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

**Latest simulation results (2016–2025)** — auto-processed (597s / 10 min):
- Net margin: £1,445,257.67 | Gross: £6,467,308.57 | Capital: £51,433
- Treasury: £2,466,636 → £3,911,894 | 38 committee interventions | 1605 bills issued
- Enterprise value: £8,826,938.57 | Net after CTS: £6,360,822
- Retention: 12 offers, 12/12 retained | 6 no-offer churns | 6 total churned accounts