# Latest Status (mobile snapshot)

This file is served by `/ui/status` on the file API for quick mobile checks.
For full detail see `STATUS.md` at the repo root.

Last updated: 2026-06-13T11:45:00Z

Current phase: Phase 2b (gas dual fuel) COMPLETE. Full 9.5-year re-run
finished with active Context Handshake (160 wake-ups, routed through local
Ollama `qwen3:14b`, now live as the standard coder/committee model). Headline
figures: net margin **£13,970.60** (electricity £10,850.17 + gas £3,120.43)
over 2016-2025; treasury grew £21,829.17 → £35,799.77. Capital cost ratio
50.9% of gross. See `docs/observability/PHASE_2b_SUMMARY.md` for full detail.

`make check` passes — 89 tests, lint clean.

Phase 4a (customer value layer) instruction staged by Rich and now being
actioned: 4a-1 cost to serve, 4a-2 churn model, 4a-3 CLV (Shifted-BG via
PyMC-Marketing), 4a-4 home move win rate, 4a-5 enterprise value function.
REVIEW_GATE after each sub-phase, full summary on completion.

- **4a-1 (cost to serve) — done**: `saas/cost_to_serve.py` + 5 tests added
  (89 total). See `docs/observability/PHASE_4a_SUMMARY.md`.
- 4a-2 through 4a-5 — not started.

Open gates / questions for Rich (lightweight, ranked by work parked behind
each):
1. **Phase numbering conflict** — `docs/instructions/MASTER_BACKLOG.md`
   defines "Phase 4a" as the *Fully Synthetic Ecosystem Bootstrap*
   (physics-engine forward run beyond 2025, prerequisites now met since
   3b/3c are cleared). The staged `PHASE_4a_INSTRUCTION.md` describes a
   different "customer value layer" (cost-to-serve/churn/CLV/etc.) that
   reads more like the "Phase 4 core value drivers" referenced as a
   prerequisite for Phase 5. Built 4a-1 anyway since it's small and
   reversible either way — but confirm before 4a-2/3 (churn, PyMC-Marketing
   CLV) commit real effort: is the staged instruction Phase 4a as written,
   or should the customer-value work be renumbered (e.g. Phase 4) and the
   backlog's "Fully Synthetic Bootstrap" remain Phase 4a/4b?
2. **`docs/staging/TASK_AUTOSTART.md` (Windows Task Scheduler autostart)** —
   step 1 (file-api/tailscale in `start_worker.sh`) is superseded by the
   existing `background/file-api.service` + `tailscale funnel`. Steps 2-3
   (registering `SkynetAutoStart` via `powershell.exe` from WSL2) can't run
   here — `powershell.exe` is not on PATH (no WSL/Windows interop in this
   session). Needs running directly from a Windows-side shell, or interop
   re-enabled.

Open gates:
- Phase 4a — sub-phases in progress, REVIEW_GATE after each.
