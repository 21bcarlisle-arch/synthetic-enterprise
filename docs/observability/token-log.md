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
