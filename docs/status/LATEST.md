# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-20T11:38:41Z

**Phase 10b LIVE (2026-06-20)**: 543 tests passing. Segment portfolio report committed.
- `saas/reporting/segment_report.py`: standalone segment P&L report generator
  - Per-segment unit economics: headcount trajectory, net/customer, smart-meter migration
  - `make segment-report` regenerates from saved JSON; `make run-segments` runs full simulation
- 26 new tests covering extract_segment_data(), generate_segment_report(), table helpers
- Full 2016-2025 segment simulation still in progress (background, at 2017-09, treasury £531k)

**Phase 10a (2026-06-20)**: Segment customer model live.
- `simulation/segments.py`: 5 customer segments (resi_standard 150 customers, resi_smart 20, sme_standard 40, sme_smart 5, gas_resi 80)
- `simulation/run_segments.py`: simulation loop with annual headcount evolution (churn, smart upgrades, acquisition)
- Non→Smart flow: UK smart meter rollout modelled — Standard customers upgrade to Smart at 3-10%/yr
- Speed: O(segments×periods) same as before, economically credible at realistic headcounts

**Phase 9a bill structure results (2016–2025)** — latest named-customer run (git 34d9cb2):
- Customer bills (all-in): £168,067 | VAT remitted: (£13,907) | Revenue (ex-VAT): £154,161
- Non-commodity pass-through: (£42,887) | Wholesale: (£96,087)
- Gross margin: £15,186 | Capital: £1,228 | Net margin: £13,958 (9.1% of ex-VAT revenue)
- Operating net margin (after fixed overhead £5,700 + acquisition £1,250): **£+7,008** (profitable!)
- Treasury: £29,846 → £33,407 | 2,238,162 ledger events | 160 committee interventions
- Enterprise value: £-1,635 | Cost-to-serve: £6,460 | Net after CTS: £+7,498

**Five hollow gaps status (as of 2026-06-20)**:
1. ~~No customer events firing~~ — CLOSED (Phase 6b/7e): churn events, replacement onboarding
2. ~~No ledger~~ — CLOSED (Phase 7a/7b): transaction log, cash waterfall, bad-debt events
3. SIM/company barrier structural not functional — Company layer foundation built (Phase 9a)
4. ~~HH data path~~ — CLOSED (Phase 6a): C7-C9 on real HH consumption
5. ~~Reporting~~ — CLOSED (Phase 5a/5b): ANNUAL_REPORT.md, full pipeline

**Autonomous stack status**: sim_runner, autonomous_runner, health_check, staging_watcher, ntfy_responder — all operational. NTFY spam fixed (all 3 sources). Cron self-healing installed every 30min.
Report: https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md
