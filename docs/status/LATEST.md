# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-25T11:46:30Z

**Phase 52 COMPLETE (2026-06-25):** ToU demand response — 24 new tests (1,355 total).
- `saas/demand_response.py` (new): peak→off-peak load shift (base 15% + EV +12% + heat_pump +8%)
- `make_shifted_shape_fn()` wraps consumption shape for ToU-eligible customers
- `demand_response_log` per term in run output (shift_fraction, has_ev, has_heat_pump)
- Watchdog: exponential API backoff (1m/2m/5m/10m), NTFY on failure + hourly while down
- SSH auto-attach via ~/.bashrc — SSHing into Skynet attaches to claude tmux session

**Phase 51 COMPLETE (2026-06-24):** ToU eligibility gate — 9 new tests (1,330 total).
- `is_tou_eligible(customer)` in `saas/smart_meter_rollout.py`: True if HH-metered OR smart_meter=True
- `simulation/run_phase2b.py`: ToU gate upgraded from `is_hh_customer` to `is_tou_eligible`
- Acquired customers with smart meters (from Phase 50 rollout model) now get peak/off-peak pricing

**Latest simulation run (2026-06-25, commit 06a77b6, 525s):**
- **Net P&L: £326,682 | Gross margin: £5,119,568 | Treasury: £2,793,319 | SURVIVED**
- Net/Gross: 6.4% — realistic UK energy retail after all policy/network/capital costs

**Previous Ollama run (2026-06-24, commit 5eb3b07, 520s):**
- Net margin: £5,163,503 | Gross: £5,229,257 | Treasury: £2,889,212 | SURVIVED
- Cap-aware acquisition gate firing 2021-22. Ofgem cap compressing resi margins.

**Test suite: 1,355 total (all saas/company/tools passing; 24 new Phase 52 + watchdog tests)**
