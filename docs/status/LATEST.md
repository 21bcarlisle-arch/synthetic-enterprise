## Phase PT + Staging Actioned (3 advisor instructions)
Last updated: 2026-07-03T21:29:06Z

**Status:** COMPLETE. 15,290 tests passing.

**Phase PT — customers.json + supplier.json:**
- `tools/generate_customers_json.py`: 16 customer groups; dual-fuel pairs with per-leg elec/gas split + combined roll-up; kwh + avg rate from bills
- `tools/generate_supplier_json.py`: portfolio_summary, 10-year series, FRA ratio series
- Both wired into `process_run_complete.py` + committed on every run
- Live: poesys.net/data/customers.json | poesys.net/data/supplier.json

**Staging actioned (3 advisor instructions):**
- `DEPLOY_PATH_DIAGNOSE.md`: root cause was pre-NQ deploy-pages.yml overwriting state file; fixed in NQ. Now confirmed regenerating on every run since 18:50 UTC.
- `STATE_ROOTCAUSE_COMMIT_STEP.md`: commit step confirmed working; PROJECT_STATE.txt in git_commit_push since NQ fix.
- `STATE_SYNC_VERIFY_BY_FETCH.md`: verified-by-fetch rule encoded in CLAUDE.md Key Learnings.

**Also in this session: Phase PS (Complaints + Arrears Population Anchoring, 22 tests)**
- `tools/population_anchor.py`: complaint rate vs Ofgem QoS benchmark + arrears rate vs DESNZ benchmark
- `saas/reporting/annual_report.py`: Population Anchoring section added
- KEY FINDING: SIM arrears RED most years (29-31% unique customers with new arrears), consistent with resi payment model. 2020: GREEN (5.3%). Signal exposed.

**CLAUDE.md addition:**
- "Observability artifacts verified by fetch" — done only when live URL fetched and confirmed current

**Latest simulation results (2016–2025):**
- Net margin: £1,445,258 | Gross: £6,452,602 | 15,290 tests
- Enterprise value: £8,826,939 | Treasury: £3,911,894
