# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

**Share with Claude.ai**: paste this URL into a claude.ai chat and Claude
will fetch the live content directly — no copy/paste needed, always
up to date with the latest push to `main`:
https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/docs/status/LATEST.md

Last updated: 2026-06-13T13:15:00Z

Current phase: Phase 2b (gas dual fuel) COMPLETE. Full 9.5-year re-run
finished with active Context Handshake (160 wake-ups, routed through local
Ollama `qwen3:14b`, now live as the standard coder/committee model). Headline
figures: net margin **£13,970.60** (electricity £10,850.17 + gas £3,120.43)
over 2016-2025; treasury grew £21,829.17 → £35,799.77. Capital cost ratio
50.9% of gross. See `docs/observability/PHASE_2b_SUMMARY.md` for full detail.

`make check` passes — 112 tests, lint clean.

Live status page: https://21bcarlisle-arch.github.io/synthetic-enterprise/status/
(renders this file, auto-refreshes every 2 minutes).

Phase 4a (Fully Synthetic Ecosystem Bootstrap, per MASTER_BACKLOG) remains a
placeholder. The customer value layer is **Phase 4b** — instruction staged by
Rich and now being actioned: 4b-1 cost to serve, 4b-2 churn model, 4b-3 CLV
(Shifted-BG via PyMC-Marketing), 4b-4 home move win rate, 4b-5 enterprise
value function. REVIEW_GATE after each sub-phase, full summary on completion.

- **4b-1 (cost to serve) — done**: `saas/cost_to_serve.py` + 5 tests added
  (89 total). See `docs/observability/PHASE_4b_SUMMARY.md`.
- **4b-2 (churn model) — done**: `saas/churn_model.py` + 7 tests added
  (96 total). Builds on Phase 3a's `score_experience_signals()`.
- **4b-3 (CLV via Shifted-BG) — done**: `saas/clv_model.py` + 9 tests added
  (109 total). Uses `pymc-marketing`'s `ShiftedBetaGeoModelIndividual` with
  method-of-moments priors (the portfolio's 6 accounts are all
  right-censored with 0 observed churns, making a direct MCMC `.fit()`
  numerically unstable — see Open Questions in `PHASE_4b_SUMMARY.md`).
- 4b-4, 4b-5 — not started.

Session watchdog: now auto-resumes on Claude Code usage-limit messages
without a "YES" confirmation (waits up to 6h, retrying every 15min) — only
crash/exit still requires confirmation. It also queues two tasks for the
independent background-worker (local Ollama, GPU) during the wait: a
forward-prep draft of 4b-4 (qwen3:14b) and an observability/housekeeping
digest (qwen2.5:7b) — both land as review-only drafts under
`docs/observability/`. See `background/session_watchdog.py`.

`docs/staging/TASK_AUTOSTART.md` — complete, registered manually by Rich.
Cleared from staging.

Open gates:
- Phase 4b — 4b-4 (home move win rate), 4b-5 (enterprise value function)
  remain, REVIEW_GATE after each.
