# Process Observability — Token Log

A running log of frontier-token spend against what it produced, one entry per
session (or natural unit of work). This is the **Process** observability
surface from CLAUDE.md — "token-to-feature efficiency, DORA-style agentic dev
metrics, speculative burn later discarded" — and the baseline we'll use to
judge whether the dev approach is actually improving across phases (0a → 0b
→ 0c and beyond).

## How to log a session

Append an entry below using the template. Don't edit past entries except to
fix errors — this is a log, not a living document.

- **Frontier tokens** — read from `/cost` if run interactively, or computed
  from the session transcript's `usage` blocks: sum
  `input_tokens + output_tokens + cache_creation_input_tokens` for the
  headline figure. `cache_read_input_tokens` is tracked separately —
  cache reads cost roughly a tenth of a fresh input token, so folding them
  into the headline number would overstate spend.
- **Local model calls** — count of delegations to Ollama (or other local
  runners), which model, and what for. This is the signal for Phase 0b
  (cross-model frontier-to-local delegation).
- **Produced** — be concrete: file paths, line deltas (from `git log
  --shortstat` / `git diff --stat`), and a plain-language list of what
  shipped. "Features shipped" should be things a person outside this project
  could understand, not internal refactor notes.
- **Notes** — anything that would help future-you read the trend correctly:
  friction encountered, surprises, approach changes mid-session, whether a
  chunk of the spend was speculative work that got discarded.

### Template

```
## YYYY-MM-DD — Phase X — <one-line task description>

- **Frontier tokens:** <total> (in: N, out: N, cache-create: N | cache-read: N)
- **Local model calls:** <count> — <model>, <what for>
- **Produced:**
  - Files created (N): `path`, `path`, ...
  - Files modified (N): `path`, ...
  - Lines: +N / -N
  - Features shipped: <bullets>
- **Notes:** <friction, surprises, approach changes>
```

---

## 2026-06-07 — Phase 0a — Day 1: repo scaffold + first SIM increment

- **Frontier tokens:** ~131,168 (in: 192, out: 52,124, cache-create: 78,852 | cache-read: 4,345,319)
- **Local model calls:** 2 — `qwen2.5-coder:14b` via Ollama (localhost:11434), delegated through the `sim-engineer` role: write a Python function to retrieve the latest Elexon SSP/SBP data point, then revise it after the first attempt hit a 404 on a hallucinated endpoint
- **Produced:**
  - Files created (12): `sim/README.md`, `saas/README.md`, `interface/README.md`, `interface/contracts/.gitkeep`, `.claude/agents/sim-engineer.md`, `.claude/agents/saas-engineer.md`, `.claude/agents/interface-steward.md`, `sim/system_prices.py`, `docs/data-sources/elexon.md`, `docs/observability/token-log.md`
  - Files modified (2): `CLAUDE.md` (Phase 0a Permissions Model section), `.claude/settings.local.json`
  - Lines: +338 / -0 (across 3 commits: `c43b5d3`, `db1e6ee`, `2a9338b`)
  - Features shipped:
    - Private GitHub repo created and pushed (`21bcarlisle-arch/synthetic-enterprise`)
    - SIM/SaaS/interface seam scaffolded with the no-cross-import rule documented, making the Point-in-Time Blindfold a structural property rather than just a convention
    - Three subagent roles defined (`sim-engineer`, `saas-engineer`, `interface-steward`), mapped 1:1 to the seam
    - First real SIM increment: `sim/system_prices.py` — pulls live System Sell Price / System Buy Price from the Elexon Insights Solution API (Historical Ground Truth law satisfied — real data, not synthetic)
    - `docs/data-sources/elexon.md` — ground-truth reference for the Elexon API shape, written specifically to stop local models re-guessing endpoints they've already gotten wrong once
- **Notes:** First end-to-end instruct-execute-observe loop with local delegation. The local model's first attempt invented a plausible-but-fake `/systemprices/latest` endpoint (404). One round of feeding the failure + the real API shape back in was enough to get a correct, working function. That correction cost is now captured in `docs/data-sources/elexon.md` so it shouldn't recur — worth watching in Phase 0b whether reference-doc-first prompting measurably reduces the local model's wrong-guess rate.

---

## 2026-06-07 — Phase 0b — Cross-model delegation: 4-customer portfolio settlement + P&L

- **Frontier tokens:** not computed this session (no `/cost` access in this mode and no transcript usage-block tooling available to the orchestrator) — flagged as a gap; future sessions should run `/cost` before wrapping up so this line isn't blank. Qualitatively: a longer, heavier session than Day 1 — multiple research round-trips (live API probing, web fetch/search for PC1 profile data provenance, a backgrounded research subagent) plus several delegate→test→correct loops, each carrying the growing codebase in context.
- **Local model calls:** 8 — `qwen2.5-coder:14b` via Ollama (localhost:11434), via the new reusable harness `tools/delegate_ollama.py`. Total local tokens reported by Ollama: ~9,937 (prompt_eval + eval, summed across calls). Breakdown:
  - 1 — harness smoke test (prompt_eval=54, eval=16)
  - 1 — historical SSP range ingestion, correct first try (prompt_eval=608, eval=244)
  - 1 — fixed-tariff pricing function, correct first try (prompt_eval=544, eval=374)
  - 3 — PC1 shape loader: initial generation + two correction rounds (prompt_eval/eval = 1246/639, 1205/661, 1252/601) — see Notes, this is where delegation struggled
  - 1 — settlement run orchestration, correct first try (prompt_eval=941, eval=545)
  - 1 — portfolio P&L aggregation, correct first try (prompt_eval=610, eval=397)
- **Produced:**
  - Files created (10): `tools/delegate_ollama.py`, `sim/system_prices_history.py`, `sim/profile_class_1.py`, `sim/data/profile_class_1_gad.csv`, `docs/data-sources/profile-class-1.md`, `saas/tariff_pricing.py`, `simulation/README.md`, `simulation/settlement.py`, `simulation/portfolio_pnl.py`, `simulation/run_phase0b.py`
  - Files modified (1): `.claude/settings.local.json` (allowlist housekeeping, committed separately as `c27b41d`)
  - Lines: +~520 across the new modules/docs (see `git log --shortstat` once committed)
  - Features shipped:
    - `tools/delegate_ollama.py` — minimal reusable harness: POSTs a prompt to local Ollama, captures the raw response plus Ollama's own `prompt_eval_count`/`eval_count`, so local-model spend can be tracked the same way frontier spend is
    - `sim/system_prices_history.py` — historical SSP/SBP retrieval over an arbitrary date range (extends Day 1's "latest" puller)
    - `sim/profile_class_1.py` + `sim/data/profile_class_1_gad.csv` + `docs/data-sources/profile-class-1.md` — Profile Class 1 (domestic) half-hourly consumption shape, sourced from real published Group Average Demand data (UKERC/CEDA archive, Electricity Association via Elexon Ltd, Open Access) per Elexon's BSC "Load Profiles" guidance-note structure (5 seasons × 3 day-types), with full provenance documented since Elexon's modern API doesn't expose this (a real gap, not a shortcut — see the doc)
    - `saas/tariff_pricing.py` — prices a customer's 1-year fixed unit rate from the 30-day pre-acquisition average SSP plus 5% margin; pure function, receives prices only across the `interface/` seam (Blindfold-safe)
    - `simulation/` — new orchestration layer (with its own README explaining why it's allowed to see both `sim/` and `saas/`: it's the clock-bearing room, not a seam-breaker) — `settlement.py` runs per-customer-per-period settlement, `portfolio_pnl.py` aggregates to portfolio + per-customer P&L, `run_phase0b.py` wires the whole pipeline and prints the report
    - **The actual deliverable**: ran the full pipeline for 4 synthetic PC1 customers (acquired 2016-01-01/04-01/07-01/10-01) against real 2016 Elexon data. Portfolio P&L for 2016-10-01→2016-12-31: **consumption 4,301.41 kWh, revenue £164.94, wholesale cost £242.61, margin −£77.67** — a real loss, because Q4-2016 wholesale SSP averaged ~£56/MWh while each customer's fixed rate was set from an earlier-in-year 30-day lookback (£36-40/MWh). Genuine margin-compression signal from real historical data, not a bug — first glimpse of the hedge-effectiveness dynamic CLAUDE.md flags as a business-observability concern.
- **Notes:** This is the Phase 0b signal session — "test cross-model frontier-to-local delegation" — and the picture is mixed in an informative way:
  - **Simple, well-scoped tasks (API range puller, pure pricing function, settlement orchestration, aggregation) were correct on the first generation**, given a prompt that stated the exact data shapes and a couple of edge-case rules in prose. Zero correction rounds needed for 4 of the 5 delegated modules.
  - **Calendar/date-arithmetic logic was a different story.** The PC1 shape loader needed three rounds: round 1 had a dead `elif` branch (Spring unreachable), a missing import, and a CSV-reading bug that returned 48 copies of one row; round 2's "fix" for the dead branch introduced a worse bug (`date(year + 3, 3, 1)` — nonsensical year arithmetic); round 3 finally got the season classification right after the orchestrator supplied near-literal pseudocode. Even then, the frontier caught **two further defects by cross-checking against known ground-truth dates** (UK clock-change days, August Bank Holiday) that no amount of code-reading would have surfaced — `last_sunday_of_month`/`last_monday_of_month` were consistently one day off, and `high_summer_end_sunday` used a formula disconnected from the (corrected) start date. Patched those two directly rather than spending a fourth delegation round — diminishing returns were obvious by then.
  - **Takeaway for Phase 0b/0c**: the local model handles "transform this data shape per these rules" tasks well in one shot, but multi-step calendar/temporal logic needs either much more explicit (near-pseudocode) prompting up front, or — probably more efficiently — should be hand-written by the frontier and delegation reserved for the shape-transform tasks it's actually good at. Ground-truth cross-checks (not just code review) were what caught the subtlest bugs; "does it run without error" was not a sufficient test for date logic.
  - Also surfaced a real data-availability gap worth remembering: **Elexon's modern REST API has no profile-coefficient data** — that lives in a separate legacy BSC subsystem (Profile Administration / SAA-I014 / D0018) that isn't API-accessible (Elexon even ran a 2023-24 consultation on whether to expose it). The UKERC/CEDA archive was the real, citable, open-access substitute — found by a research subagent run in parallel with other delegated work, which kept the critical path moving rather than blocking on it.
