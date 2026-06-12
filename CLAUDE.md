# The Synthetic Enterprise — CLAUDE.md

## What This Is
A simulated UK energy supplier powered by autonomous AI agents. The core thesis: deep sector expertise combined with cheap AI execution produces highly autonomous, high-value software in compressed timeframes at radically low cost. The energy retail domain is the vehicle; the real goal is learning and proving agentic software development.

## Who Instructs Whom
Rich (the human) talks to this chat interface only — he never writes code, runs terminals, or dispatches tasks directly. This chat → Claude Code (lead orchestrator) → subagents (Cline, Aider, local models). Rich sets direction and unblocks genuine blockers. The system does the rest.

## How Rich Connects
- **Primary:** Claude mobile app, Remote Control — this is the day-to-day interface to this session.
- **Fallback:** SSH via Tailscale, port 2222, direct to the machine — only when Remote Control is unavailable.
- **Autostart:** Claude Code launches automatically into this project on machine boot — no manual session setup required to pick up where things left off. On Skynet startup, run `bash background/start_worker.sh` after Claude Code starts. The background worker runs independently in its own tmux session and never interferes with the main Claude Code session.
- **Session watchdog:** `bash background/start_worker.sh` also starts `session-watchdog` (own tmux session), which monitors the `claude` tmux session. If Claude Code stops, it sends an NTFY alert to `skynet-synthetic` and waits up to 4 hours for a reply containing "YES" before restarting `claude` with plain `claude` (never `--dangerously-skip-permissions` — normal permission prompts apply on restart). Max 3 restarts/hour. See `background/session_watchdog.py`.

## Architecture Stack
- **Lead orchestrator:** Claude Code (Anthropic API)
- **Local execution:** Cline, Aider
- **Local model runner:** Ollama at http://localhost:11434 (one model running at a time — swap, never run both simultaneously)
- **Local models:** Qwen2.5-Coder 14B Q4 (`qwen2.5-coder:14b` — code generation, file writing, data transformation) and Qwen2.5 7B (`qwen2.5:7b` — result analysis, summary drafting, structured output, README/STATUS updates). Routed automatically by task type — see `tools/delegate_ollama.py` and the Delegation Protocol in `docs/instructions/MASTER_BACKLOG.md`
- **Data sources:** Elexon Insights Solution (data.elexon.co.uk, key-free REST), NESO data portal (CKAN/PostgreSQL)
- **Version control:** GitHub

## Three Architectural Laws
1. **Historical Ground Truth** — real Elexon BMRS and NESO data only; no synthetic history
2. **Point-in-Time Blindfold** — business layer never sees the future; decisions on noise-smudged forecast only
3. **Synthetic Forward Curve** — historical spot + sigma-based volatility premium

## Governing Principles
- **Reversibility is law** — two-way doors run free, one-way doors escalate to Rich
- **Non-blocking concurrency** — independent work always proceeds; never speculate past an open question unless explicitly tagged as throwaway
- **Escalation format** — lightweight PR/FAQ, answerable in ~30 seconds, ranked by how much work is parked behind each question
- **NTFY links are raw, not blob** — any file referenced in an `ntfy.sh/skynet-synthetic` notification must be a raw GitHub URL (`https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/[filepath]`), never a `github.com/.../blob/...` link — Rich's strategy advisor reads these directly as text, not rendered HTML. Push to `main` before sending; see the NTFY Protocol in `docs/instructions/MASTER_BACKLOG.md` for the full spec
- **Token ceiling** — async streams cannot run away with budget overnight; respect token limits
- **CLV-per-frontier-token** — steady-state prioritisation objective once build loop is reliable
- **The system prompts itself** — build routines, not one-off prompts

## Harness Rule (standing instruction)
`make check` must pass before any REVIEW_GATE is cleared and before any phase summary is committed.
Every new feature instruction must include: write the test that proves it works.

## Phase 0 Structure
- **0a** — Prove plumbing and instruct-execute-observe path
- **0b** — Test cross-model frontier-to-local delegation
- **0c** — Run SIM increments with deliberate dev approach changes to form learning verdict

## Simulation Window
**2016-01-01 → 2025-06-07** — 1 build year (accumulate priced portfolio) + ~9.5 test years. The floor is set by the **BSC P305 boundary**: Elexon's settlement-price dataset begins 2015-11-07 because P305 replaced the imbalance pricing methodology that month — there's no earlier data under the current regime to extend into. See [`docs/simulation-period.md`](docs/simulation-period.md) for the full derivation and completeness evidence.

## Phase 0a Permissions Model
Standing approval for all reversible actions — file creation, scaffolding, git commits, and pushes proceed without pausing for confirmation. This extends "Reversibility is law" into a concrete operating mode for 0a: only stop and escalate to Rich for one-way doors — spending money, deleting data, or other irreversible changes.

## Scope Discipline
- PyPSA: premature until Phase 4
- Mellum2: Phase 2 cost-optimisation, not Day 1
- Competitors vs wholesale-only market: open Phase 2 decision
- CLV modelling requires contractual PyMC-Marketing variants (Shifted-BG, BG/BB)

## Observability Surfaces
1. **Process** — token-to-feature efficiency, DORA-style agentic dev metrics, speculative burn later discarded. Logged per-session in [`docs/observability/token-log.md`](docs/observability/token-log.md) — append an entry at the end of each session following the template there.
2. **Business** — P&L by cohort, CLV/CAC, churn, hedge effectiveness
3. **Experience** — customer reaction function scoring, expectation gap, comprehensibility, tolerance

## Key Domain Insight
Customer reaction to bills is non-rational. Arithmetically correct bills frequently produce complaints and churn. This shapes the experience observability layer.
