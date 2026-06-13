# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

Last updated: 2026-06-13T12:30:00Z

Current phase: Phase 2b (gas dual fuel) COMPLETE. Full 9.5-year re-run
finished with active Context Handshake (160 wake-ups, routed through local
Ollama `qwen3:14b`, now live as the standard coder/committee model). Headline
figures: net margin **£13,970.60** (electricity £10,850.17 + gas £3,120.43)
over 2016-2025; treasury grew £21,829.17 → £35,799.77. Capital cost ratio
50.9% of gross. See `docs/observability/PHASE_2b_SUMMARY.md` for full detail.

`make check` passes — 96 tests, lint clean.

Phase 4a (Fully Synthetic Ecosystem Bootstrap, per MASTER_BACKLOG) remains a
placeholder. The customer value layer is **Phase 4b** — instruction staged by
Rich and now being actioned: 4b-1 cost to serve, 4b-2 churn model, 4b-3 CLV
(Shifted-BG via PyMC-Marketing), 4b-4 home move win rate, 4b-5 enterprise
value function. REVIEW_GATE after each sub-phase, full summary on completion.

- **4b-1 (cost to serve) — done**: `saas/cost_to_serve.py` + 5 tests added
  (89 total). See `docs/observability/PHASE_4b_SUMMARY.md`.
- **4b-2 (churn model) — done**: `saas/churn_model.py` + 7 tests added
  (96 total). Builds on Phase 3a's `score_experience_signals()`.
- 4b-3 through 4b-5 — not started.

`docs/staging/TASK_AUTOSTART.md` — complete, registered manually by Rich.
Cleared from staging.

Open gates:
- Phase 4b — sub-phases in progress, REVIEW_GATE after each.
