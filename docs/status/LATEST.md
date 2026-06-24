# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-24T20:14:26Z

**Phase 51 COMPLETE (2026-06-24):** ToU eligibility gate — 9 new tests (1,330 total).
- `is_tou_eligible(customer)` in `saas/smart_meter_rollout.py`: True if HH-metered OR smart_meter=True
- `simulation/run_phase2b.py`: ToU gate upgraded from `is_hh_customer` to `is_tou_eligible`
- Acquired customers with smart meters (from Phase 50 rollout model) now get peak/off-peak pricing

**Phase 50 COMPLETE (2026-06-24):** Smart meter rollout model — 30 new tests (1,321 total).
- `saas/smart_meter_rollout.py` (new): UK rollout 2016-2025 (resi 10%→75%, SME 5%→57%, I&C 100%)
- `saas/property_model.py`: `get_smart_meter_status(customer_id, year, segment)` — time-aware flag
- `saas/customers.py`: `make_acquired_customer()` stamps `smart_meter` at acquisition year

**Full Ollama run complete (2026-06-24, commit 5eb3b07, 520s):**
- **Net margin: £5,163,503 | Gross: £5,229,257 | Treasury: £2,889,212 | SURVIVED**
- 2020: -3.8% net | 2021: +3.2% net | 2022: +7.3% net (crisis profitable)
- Cap-aware acquisition gate firing 2021-22. Ofgem cap compressing resi margins.

**Latest simulation results (2016–2025)** — auto-processed (958s / 16 min):
- Net margin: £5,163,503.16 | Gross: £5,229,257.26 | Capital: £65,754
- Treasury: £2,466,636 → £2,889,212 | 50 committee interventions | 1549 bills issued
- Enterprise value: £5,666,754.67 | Net after CTS: £5,129,437
- Retention: 18 offers, 17/18 retained | 4 no-offer churns | 5 total churned accounts

**Test suite: 1,330 total (694 saas+company confirmed passing, simulation+background running)**
