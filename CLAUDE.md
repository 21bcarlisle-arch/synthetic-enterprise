# The Synthetic Enterprise — CLAUDE.md

## What This Is
A simulated UK energy supplier powered by autonomous AI agents. The core thesis: deep sector expertise combined with cheap AI execution produces highly autonomous, high-value software in compressed timeframes at radically low cost. The energy retail domain is the vehicle; the real goal is learning and proving agentic software development.

## Who Instructs Whom
Rich (the human) talks to this chat interface only — he never writes code, runs terminals, or dispatches tasks directly. This chat → Claude Code (lead orchestrator) → subagents (Cline, Aider, local models). Rich sets direction and unblocks genuine blockers. The system does the rest.

## Architecture Stack
- **Lead orchestrator:** Claude Code (Anthropic API)
- **Local execution:** Cline, Aider
- **Local model runner:** Ollama at http://localhost:11434
- **Primary local model:** Qwen2.5-Coder 14B Q4
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
- **Token ceiling** — async streams cannot run away with budget overnight; respect token limits
- **CLV-per-frontier-token** — steady-state prioritisation objective once build loop is reliable
- **The system prompts itself** — build routines, not one-off prompts

## Phase 0 Structure
- **0a** — Prove plumbing and instruct-execute-observe path
- **0b** — Test cross-model frontier-to-local delegation
- **0c** — Run SIM increments with deliberate dev approach changes to form learning verdict

## Scope Discipline
- PyPSA: premature until Phase 4
- Mellum2: Phase 2 cost-optimisation, not Day 1
- Competitors vs wholesale-only market: open Phase 2 decision
- CLV modelling requires contractual PyMC-Marketing variants (Shifted-BG, BG/BB)

## Observability Surfaces
1. **Process** — token-to-feature efficiency, DORA-style agentic dev metrics, speculative burn later discarded
2. **Business** — P&L by cohort, CLV/CAC, churn, hedge effectiveness
3. **Experience** — customer reaction function scoring, expectation gap, comprehensibility, tolerance

## Key Domain Insight
Customer reaction to bills is non-rational. Arithmetically correct bills frequently produce complaints and churn. This shapes the experience observability layer.
