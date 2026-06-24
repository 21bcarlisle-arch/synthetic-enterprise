# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-24T04:37:54Z

**Full Ollama run complete (2026-06-23, commit da36b38, 478s — stable):**
- **Net margin: £382,598 | Gross: £5,173,555 | Treasury: £2,849,234 | SURVIVED**
- All I&C tariff types active. Gas seasonal calibration. No admin event.

**Phase 43b COMPLETE (2026-06-23)**: VaR-constrained trading desk.
- `company/trading/hedge_decision.py`: EWMA vol estimate → 95% VaR constraint → hedge fraction
- Per-term hedge fractions now adapt to market conditions (high vol → higher hedge mandate)
- Bid-ask spread cost model (0.5-1.5%, N2EX calibrated). 15 new tests. 1,275+ total.
- Integration: 93 contracts, 46,345 MWh hedged, £463k hedge P&L, £35k bid-ask cost.

**Architecture Stages 2-4 COMPLETE (2026-06-23):**
- Stage 2: discovery-agent.md — structured assumption-finding pipeline
- Stage 3: epistemic-verifier.py — company/ barrier scan, gated in phase-close checklist
- Stage 4: agent_protocol.py — AgentMessage + IntentType, 18 tests, live in sim-runner

**Website (poesys.net):**
- robots.txt: Allow: / (permissive — all crawlers welcome)
- System page: agent_status.json last updated 2026-06-23T11:34:41Z

**Latest simulation results (2016–2025)** — auto-processed (430s / 7 min):
- Net margin: £5,122,073.96 | Gross: £5,187,169.23 | Capital: £65,095
- Treasury: £2,466,636 → £2,848,790 | 38 committee interventions | 1569 bills issued
- Enterprise value: £5,500,787.15 | Net after CTS: £5,087,309
- Retention: 20 offers, 19/20 retained | 4 no-offer churns | 5 total churned accounts