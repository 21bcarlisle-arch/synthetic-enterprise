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

---

## 2026-06-08 — Phase 0c — Full-year settlement, customer reaction, CLV seed: "delegate everything" test

- **Frontier tokens:** 229,181 (in: 154, out: 58,635, cache-create: 170,392 | cache-read: 4,773,678) — computed directly from this session's transcript `usage` blocks, closing the gap Phase 0b flagged (no `/cost` access, no usage-block tooling at the time; the tooling clearly exists now — just had to grep the session's own `.jsonl`).
- **Local model calls:** 5 — `qwen2.5-coder:14b` via Ollama (localhost:11434), via `tools/delegate_ollama.py`. Total local tokens (prompt_eval + eval): 9,858. Breakdown:
  - 1 — `simulation/run_phase0c.py` full-year orchestration script, from spec + sibling-file style reference (prompt_eval=1400, eval=893)
  - 1 — `saas/customer_reaction.py` new module, from spec (prompt_eval=799, eval=365)
  - 1 — wire `score_dissatisfaction` into `run_phase0c.py`, edit-in-place with full current file pasted in (prompt_eval=1445, eval=1019)
  - 1 — `saas/clv_seed.py` new module, from spec (prompt_eval=858, eval=422)
  - 1 — wire `build_clv_seed` into `run_phase0c.py`, edit-in-place with full current file pasted in (prompt_eval=1534, eval=1123)
- **Produced:**
  - Files created (3): `saas/customer_reaction.py`, `saas/clv_seed.py`, `docs/phase0c-findings.md`
  - Files modified (3): `simulation/run_phase0c.py` (new — built across rounds 1/3/5), `.gitignore` (new — `__pycache__/` housekeeping), `docs/observability/token-log.md` (this entry)
  - Lines: +194 across the three commits `a98444f`/`638488a`/`5222b8d` (per `git diff --shortstat`), plus this findings doc
  - Features shipped:
    - `simulation/run_phase0c.py` — extends the Phase 0b settlement+P&L pipeline from a Q4-2016-only window to the full 2016 calendar year. Result: portfolio margin **−£78.28** over the full year (consumption 9,705.99 kWh, revenue £365.71, wholesale cost £443.99) — confirms the Q4 loss Phase 0b found wasn't a quarter-specific blip; every customer ran at a loss for the whole year.
    - `saas/customer_reaction.py` — `score_dissatisfaction()`, the first Experience-observability seed CLAUDE.md calls for: a per-customer running counter incrementing whenever a settlement period's wholesale cost exceeds the fixed-tariff bill for that period by more than 20%. Pure, seam-safe (no `sim/` import). Result: roughly a quarter of every customer's periods triggered it (e.g. C1: 4,131 / 17,517) — a striking number that's exactly the "arithmetically correct yet provocative" signal the Key Domain Insight predicts, not a defect.
    - `saas/clv_seed.py` — `build_clv_seed()`, the first CLV building block: a per-customer chronological running total of (contract value billed − actual cost of supply), with full per-period history. Pure, seam-safe. Running totals exactly match each customer's portfolio-P&L margin (as they must — cumulative per-period margin *is* that figure); the seed's value is carrying the chronological history forward for later phases.
    - `docs/phase0c-findings.md` — the requested findings write-up: what worked, what didn't, full token breakdown, and a verdict on the "delegate all code" approach.
- **Notes:** This was the cleanest delegation session yet — see `docs/phase0c-findings.md` for the full analysis. Headlines:
  - **The "edit this file, here's the whole current source" pattern was the standout discovery.** Both wiring rounds (3 and 5) came back as minimal, surgical diffs — one new import, one new print block, one new return key, nothing else touched. Markedly more reliable than open-ended module generation, and the clear default to reach for on incremental work going forward.
  - **Three repeatable failure modes, none worth a re-delegation round:** (1) every single one of the 5 generations wrapped its output in markdown code fences despite explicit "no fences" instructions — 5/5 means this should be automated around in `tools/delegate_ollama.py` rather than re-prompted against; (2) round 2 echoed a literal `...` placeholder from the prompt's elided style-reference text straight into the generated docstring — never put placeholder ellipses in few-shot examples; (3) round 2 also produced a sort key satisfying chronological-per-customer ordering but not "customers in first-encountered order," a subtle multi-constraint sequencing slip in the same family as Phase 0b's calendar-arithmetic bugs (caught by re-reading the spec against the sort key, not by running the code — it produced the "right" answer on this dataset either way). All three hand-patched directly; same diminishing-returns call Phase 0b made.
  - **Verdict:** delegating *all* code — including wiring edits — to the local model worked at this codebase's current size, provided the frontier specs precisely, supplies sibling files as style references, and reviews by re-reading against the spec (not just by running it). The ordering-logic slip is the genuine warning sign for where this will get harder as the simulation grows more temporal.

## 2026-06-08 — Phases 1a/1b — MASTER_BACKLOG authoring + customer cohort + weather data capture

- **Frontier tokens:** 282,635 headline (in: 222, out: 90,508, cache-create: 191,905 | cache-read: 14,285,069) — computed from this session's transcript `usage` blocks, summed from the point the user issued the MASTER_BACKLOG.md instruction onward. This entry covers three pieces of work that ran back-to-back in one continuous session with no clean per-phase breakpoint: writing/committing/pushing `docs/instructions/MASTER_BACKLOG.md` verbatim, all of Phase 1a, and all of Phase 1b. Phase 1a did not get its own log entry at the time — this retroactively covers it. Future phases should get clean individual entries where the transcript has natural phase-boundary breaks.
- **Local model calls:** 6 — `qwen2.5-coder:14b` via `tools/delegate_ollama.py`, total 13,546 local tokens (prompt_eval + eval):
  - Phase 1a (3 calls, 7,267 tokens): `saas/customers.py` cohort module (prompt_eval=1183, eval=1120); `docs/data-sources/customers.md` design record (prompt_eval=1265, eval=806); wire `customer_to_settlement_input` into `run_phase0c.py`, edit-in-place (prompt_eval=1829, eval=1064)
  - Phase 1b (3 calls, 6,279 tokens): `docs/data-sources/weather.md` decision record from probed-API-facts spec (prompt_eval=1572, eval=1625); `sim/weather_ingestor.py` from probed-facts spec + sibling-style reference (prompt_eval=1191, eval=747); `simulation/run_phase1b_weather_pull.py` orchestration script from exact-signature spec (prompt_eval=752, eval=392)
- **Produced:**
  - Files created (10): `docs/instructions/MASTER_BACKLOG.md`, `saas/customers.py`, `docs/data-sources/customers.md`, `docs/observability/PHASE_1a_SUMMARY.md`, `docs/data-sources/weather.md`, `sim/weather_ingestor.py`, `simulation/run_phase1b_weather_pull.py`, `sim/weather_data/{C1,C2,C3,C4}.csv`, `docs/observability/PHASE_1b_SUMMARY.md`
  - Files modified (1): `simulation/run_phase0c.py` (refactored to source customers from `saas.customers.CUSTOMERS` — confirmed P&L byte-for-byte unchanged at −£78.28)
  - Features shipped:
    - `docs/instructions/MASTER_BACKLOG.md` — the full Phase 1+ roadmap and three operating protocols (NTFY, Phase Summary, Delegation) written verbatim per Rich's spec, now the standing reference for all future phases
    - `saas/customers.py` — the four-customer cohort (C1 London / C2 Manchester / C3 Glasgow / C4 Cotswolds — urban/suburban/tenement/rural mix, EPC D/D/E/E, EAC 2800-5500 kWh) that replaces Phase 0b/0c's hardcoded acquisition-date list with real structured profiles (location, home type, EPC rating, segment), wired through cleanly with the settlement P&L provably unchanged
    - `sim/weather_ingestor.py` + `simulation/run_phase1b_weather_pull.py` + `sim/weather_data/*.csv` — **the actual Phase 1b deliverable**: 13,784 real daily weather records (2016-01-01 → 2025-06-07) for all four customer locations, sourced live from Open-Meteo's Historical Weather Archive API (Historical Ground Truth law — real reanalysis data, no synthetic values), stored flat and uncorrelated per the brief, ready for future correlation work
- **Notes:** See `docs/observability/PHASE_1a_SUMMARY.md` and `docs/observability/PHASE_1b_SUMMARY.md` for full per-phase findings/decisions/open-questions. Headline cross-phase pattern: **the "edit this file in place, paste the whole current source" delegation pattern continues to be the standout reliable approach** for incremental wiring work (Phase 1a's customer-cohort wiring came back as a clean, mostly-correct diff). Two repeat failure modes are now well-established and worth automating around in `tools/delegate_ollama.py` rather than re-prompting against each time: (1) markdown-fence wrapping despite explicit "no fences" instructions (now seen on essentially every single generation across three phases), and (2) module docstrings written as dangling string statements *after* the code rather than as the file's first statement — syntactically valid but functionally inert, seen twice in Phase 1b alone (`sim/weather_ingestor.py` and `simulation/run_phase1b_weather_pull.py`, in the exact same form both times). Both are mechanical, detectable, and fixable post-generation — prime candidates for a harness-level post-processing step.

## 2026-06-08 — Phase 1c — Forward curve pricing: the structural fix for the 2016 losses

- **Frontier tokens:** 447,656 headline (in: 192, out: 94,377, cache-create: 353,087 | cache-read: 10,365,710) — computed from this session's transcript `usage` blocks, summed from the "Phase 1c started" NTFY send onward (a clean phase-boundary breakpoint, unlike the prior combined entry).
- **Local model calls:** 4 — `qwen2.5-coder:14b` via `tools/delegate_ollama.py`, total 10,701 local tokens (prompt_eval + eval):
  - `sim/forward_curve.py`, from an exact-algorithm spec (prompt_eval=1308, eval=774)
  - `saas/tariff_pricing.py`, edit-in-place with full current file (prompt_eval=1175, eval=362)
  - `simulation/run_phase1c.py`, copy-and-modify of `run_phase0c.py` with full sibling file supplied (prompt_eval=2202, eval=1129)
  - `simulation/run_phase1c_full_window.py`, copy-and-modify of `run_phase1c.py` with full sibling file supplied (prompt_eval=2265, eval=1486)
- **Produced:**
  - Files created (3): `sim/forward_curve.py`, `simulation/run_phase1c.py`, `simulation/run_phase1c_full_window.py`
  - Files modified (1): `saas/tariff_pricing.py` (signature change: now takes a pre-generated forward price rather than computing its own spot lookback)
  - Features shipped:
    - `sim/forward_curve.py` — `generate_forward_price()`: Law 3 (Synthetic Forward Curve) made real — a forward price built from real historical SSP spot data with a 90-day rolling base, a sigma-based volatility premium (configurable `risk_factor`, default 1.2), and a seasonal adjustment blended across the contract's delivery months (configurable `WINTER_MONTHS`/`WINTER_MULTIPLIER`/`SUMMER_MULTIPLIER` constants)
    - `saas/tariff_pricing.py` — refactored to a small pure margin step on a pre-generated forward price, moving curve-generation onto the SIM side of the seam per the brief's explicit constraint
    - `simulation/run_phase1c.py` — re-ran the Phase 0c 2016 settlement with only pricing methodology changed: **margin flips from -£78.28 to +£498.68** (revenue more than doubled, £365.71 -> £942.67, on identical consumption and identical real wholesale costs) — the forward curve closes the systematic under-pricing gap exactly as theorised
    - `simulation/run_phase1c_full_window.py` — ran the same pipeline across the full 2016-2025 simulation window with portfolio P&L broken down by year, and surfaced a real architectural finding: **the book only produces settlement records for 2016-2017** (margin +£689.62 total, entirely earned in ~21 months) — every customer's 365-day fixed contract expires by late 2017 with no renewal or new-acquisition mechanic to replace it, so 2018-2025 (most of the simulation window) is empty. 165,386 real SSP records were fetched for the full window; only 70,071 settlement records resulted.
- **Notes:** See `docs/observability/PHASE_1c_SUMMARY.md` for the full findings/decisions/open-questions writeup. Two headline patterns:
  - **"Copy this exact sibling file, make exactly these changes" remains the most reliable delegation pattern in this codebase** — both orchestration-script generations came back clean, minimal, and correct on the first try, needing only the markdown-fence strip (now seen on essentially every generation across four phases — a strong harness-automation candidate).
  - **The recurring docstring-placement defect appears to have a prompting-level fix**: explicitly stating "the docstring must be the file's first statement, before any import — not after" landed correctly on the first try in `forward_curve.py`, and (perhaps not coincidentally) did not recur in either orchestration-script generation either, even without being repeated in their prompts verbatim. Worth carrying that exact phrasing into all future module-generation prompts as a standing habit rather than a one-off fix.
  - The one genuine logic defect (an off-by-one in `forward_curve.py`'s lookback-window calculation — `start_lookback_date` derived from `end_lookback_date` instead of `acquisition_date`, silently widening a 90-day window to 91) was caught only by independently re-deriving the expected window bounds and comparing — not by running the code, which executed without error and produced a perfectly plausible-looking number. Same family, same lesson, as Phase 0b's calendar-arithmetic bugs: "does it run" is never sufficient for date/window logic; cross-check against independently-derived ground truth.
  - **The full-window run's empty-book finding is the most consequential thing Phase 1c produced** — more than the pricing fix itself, arguably, because it's the first time this simulation has been run long enough to reveal that it currently models a single cohort's single contract term, not a living book of business. That's a real design decision for Rich to make (contract renewal? customer growth? both?) before more is built on top of the current settlement model — exactly what the review-gate process exists to surface honestly rather than paper over with an invented mechanic.

## 2026-06-08 — Renewal mechanism + Phase 1d — Agent-discovered hedging strategy: the agent learned the wrong lesson

- **Frontier tokens:** 584,402 headline (in: 280, out: 84,593, cache-create: 499,529 | cache-read: 18,937,362) — computed from this session's transcript `usage` blocks, summed from the "Phase 1d started" NTFY send onward (140 usage blocks). This entry covers two pieces of work that ran back-to-back with no clean intermediate breakpoint: closing Phase 1c's open question (contract renewal — Rich's gate answer to "how should the book grow to fill the window") and all of Phase 1d, including a mid-stream full replacement of the Phase 1d design itself (from "test three fixed strategies" to "agent discovers and evolves its own position").
- **Local model calls:** 4 — `qwen2.5-coder:14b` via `tools/delegate_ollama.py`:
  - `simulation/renewals.py::build_renewal_schedule()`, from an exact-algorithm spec — correct first try, smoke-tested for contiguity and re-pricing variation
  - `sim/hedging.py::settle_hedged_period()`, from an exact-algorithm spec — math correct first try; came back wrapped in obsolete "three fixed strategies" framing because its spec had been sent *before* Rich's design-replacement message arrived (see Notes)
  - `sim/hedging_strategy.py`, from a structured spec with placeholder reasoning strings to fill in — correct first try, no fixes needed; unit-tested clamping at 0.0/1.0 and the noise-tolerance hold, all verified
  - `simulation/run_phase1c_renewals.py`, copy-and-modify of `run_phase1c_full_window.py` — substituted wrong field names (`record['date']`/`record['revenue']` vs. the real `settlement_date`/`revenue_gbp` schema) and invented broken aggregation logic despite an explicit "leave the rest exactly as is" instruction; fixed by hand-splicing the new top half onto the verified-correct original bottom half
- **Hand-written:** `simulation/hedged_settlement.py` and `simulation/run_phase1d.py` — both mirror existing, already-proven structures (`run_settlement` and the renewal-run orchestration) closely enough that writing the spec would have cost more than writing the code; both passed their smoke tests cleanly on the first run
- **Produced:**
  - Files created (9): `simulation/renewals.py`, `simulation/run_phase1c_renewals.py`, `docs/data-sources/gas-nbp.md`, `sim/hedging.py`, `sim/hedging_strategy.py`, `simulation/hedged_settlement.py`, `simulation/run_phase1d.py`, `docs/observability/PHASE_1d_SUMMARY.md`, `docs/simulation-strategy.md`
  - Files modified (1): `docs/instructions/MASTER_BACKLOG.md` (Phase 1d section replaced in place with the revised agent-discovered spec)
  - Lines: +205 (`ff3b43f`, renewal), +93/-12 (`c4bccff`, gas-ref + backlog spec replacement), +553 (`6870d94`, Phase 1d code), +118 (`2255933`, Phase 1d gate write-up) — four commits, all pushed
  - Features shipped:
    - `simulation/renewals.py` — `build_renewal_schedule()`: chains a customer's contract terms contiguously from acquisition to report-end, re-pricing each renewal at the forward curve price available on its start date (100% renewal rate, no churn — Rich's explicit gate answer). Re-running Phase 1c's full-window settlement with renewals active confirmed the book stays at **customers=4 in every single year 2016-2025** — the empty-book gap Phase 1c found is closed. Full-window naked-only baseline: revenue £23,023.39, cost £12,021.19, margin **£11,002.20** (38 contract terms, 635,225 settlement records).
    - `sim/hedging.py` + `sim/hedging_strategy.py` + `simulation/hedged_settlement.py` + `simulation/run_phase1d.py` — the agent-discovered hedging system: an agent that starts at a neutral `hedge_fraction = 0.5`, settles each contract term in isolation (structurally no foresight), and evolves its position by comparing realised actual-vs-naked margin — stepping by +/-0.1 with a +/-£5 noise deadband. **Result: all four customers' agents converged on `hedge_fraction = 0.0` (fully naked) by mid-simulation**, having watched hedging underperform on every term 2016-2020 and de-risked before the 2021-2022 crisis arrived. Naked beat actual in every single year 2016-2023; full-window agent margin = £9,966.79 vs. naked-only baseline £11,002.20 (a ~£1,035 "cost of learning"). Full per-customer evolution trajectories, the crisis-vs-stable hedge-effectiveness breakdown, and the central finding are written up in `docs/observability/PHASE_1d_SUMMARY.md` and `docs/simulation-strategy.md`.
    - `docs/data-sources/gas-nbp.md` — gas/NBP pricing reference (NBP/MIPI sources, AQ derivation, volume-to-energy conversion) for future commodity-model extensions, written verbatim per Rich's spec.
- **Notes:**
  - **The spec/implementation race condition is now a confirmed, named risk.** `sim/hedging.py`'s generation spec was written and dispatched to the local model *before* Rich's message replacing the entire Phase 1d design arrived mid-session — so its correct math came back wrapped in obsolete "three fixed strategies" framing (`STRATEGY_A_NAKED` etc.) that had to be hand-stripped. No logic was lost (the per-period calculation doesn't change based on which strategy framework wraps it), but in-flight delegation specs need a "does the brief still match what I sent?" check before their output gets integrated, not just before it gets dispatched.
  - **"Copy this file, change only X" has now failed to honour "leave the rest untouched" three times** (this session's `run_phase1c_renewals.py` is the third occurrence in this log). The named change keeps landing correctly; the *unstated* implicit constraint — don't touch anything else — keeps not surviving the model's tendency to regenerate code it half-recognises. This is no longer a one-off: treat it as a structural limitation of this delegation pattern, and either keep diffs small enough that "the rest" is nearly empty, or hand-write orchestration scripts that touch existing schemas directly (which is what happened here, and both hand-written modules passed smoke tests cleanly first try).
  - **The naked-counterfactual signal design is the standout success of this phase** — it's PiT-safe by construction (derivable entirely from a term's own already-realised history), and because `run_hedged_term()` settles one isolated term with no visibility beyond it, "no foresight" is structural in the code, not just asserted in a docstring. That combination is what makes the resulting finding (the agent converging on a position that happened to be better for this dataset, but for the wrong reasons — see the summary's "recency bias / regime-change blindness" discussion) a trustworthy, auditable result rather than a hand-wave.

---

## Session: Phase 1e — Nine-Year Portfolio Run with Enterprise Risk Physics (2026-06-08)

- **Frontier tokens:** TBD — session ongoing; entry will be updated when this session closes. Covers the full Phase 1e build: MASTER_BACKLOG.md Phase 1e section update (Rich's supersession message), tools/delegate_ollama.py dual-model routing housekeeping (qwen2.5:7b pull confirmation), NTFY protocol update (raw vs. blob URL fix), Synthetic Evolution Roadmap + Context Handshake + Phase 3b/3c/4a backlog additions, and complete Phase 1e implementation.
- **Local model calls:** 2:
  - `qwen2.5-coder:14b` (2,301 prompt / 2,112 eval) → `sim/risk_engine.py` from exact algorithm spec. Core numeric logic correct on first generation. Frontier corrections: function name (assess_risk→assess_term_risk), parameter order, two abbreviated docstrings, markdown fence stripping (the four known Qwen quirks).
  - `qwen2.5:7b` (~1,200 prompt / ~900 eval) → `docs/observability/PHASE_1e_SUMMARY.md` draft from structured findings spec. Draft provided structural skeleton (What Was Built, Key Decisions, Open Questions) and reproduced finding numbers correctly. Frontier rewrote: finding 2 agent-trajectory table, added findings 3-6 in full (the self-reinforcing trap mechanism, capital cost tables, σ_recent/σ_stressed analysis, C3 timing analysis, compound Phase 1d+1e finding). Duplicate section (Finding 3 copied verbatim as Finding 4) corrected.
- **Hand-written:** `simulation/hedged_settlement.py` (Phase 1e update — capital cost fold-in) and `simulation/run_phase1e.py` (full orchestration) — both per the Phase 1d lesson: orchestration touching settlement-record schemas produces wrong field names when delegated. Both passed import and smoke-test cleanly on first write.
- **Produced:**
  - Files created (3): `sim/risk_engine.py`, `simulation/run_phase1e.py`, `docs/observability/PHASE_1e_SUMMARY.md`
  - Files modified (5): `simulation/hedged_settlement.py` (monthly CoC fold-in), `docs/simulation-strategy.md` (Phase 1e section added), `docs/instructions/MASTER_BACKLOG.md` (Phase 1e supersession + Synthetic Evolution Roadmap + Context Handshake + Phase 3b/3c/4a), `STATUS.md` (Phase 1e in progress → complete at gate), `docs/observability/token-log.md` (this entry)
  - Run output: 279 lines, 9.5-year full window, 635k+ settlement records across 4 customers, 10 terms each
  - Key numbers: Treasury £3,250→£9,114 (survived). Gross margin £9,392. Capital costs £3,528 (37.6%). Net margin £5,864. No administration event.
- **Phase 1e key findings:**
  1. Company survived — no administration event; treasury grew 180% over 9.5 years
  2. Central hypothesis NOT confirmed — capital physics did not produce organic hedging equilibrium
  3. **The hf=0.00 trap** — evolution rule is mathematically blind at full nakedness (both sides of the comparison are identical, signal = 0 regardless of capital cost magnitude). This is architectural, not statistical — requires external threshold trigger (Phase 2 Context Handshake) to escape
  4. Capital costs substantial — 37.6% of gross margin; 2021 was the only net-loss year (capital costs £455 exceeded gross margin £300)
  5. 2023 σ_stressed regime change (0.50→1.50) tripled collateral for naked books but was invisible to already-trapped C1/C2
  6. C3 showed brief crisis-period hedging signals (July renewal dates caught crisis), peaked at 0.30, reverted to 0.10 post-crisis — timing effect, not rule difference
- **Notes:**
  - **Delegation boundary validated again**: pure numeric functions (no settlement-record schema dependency) go to qwen2.5-coder:14b; orchestration hand-written. No field-name errors this phase (zero schema-touching delegation).
  - **New architectural insight from Phase 1e**: the evolution rule's comparison becomes self-referential at hf=0.00. Any proposed escape mechanism (minimum hedge floor, direct capital term, threshold-triggered risk committee) must be evaluated against this exact structural constraint — not just "does it make the agent hedge more" but "does it produce a non-zero comparison signal when both sides of the evolution's counterfactual coincide."
  - **NTFY protocol updated this session**: all future notifications must use raw GitHub URLs (https://raw.githubusercontent.com/21bcarlisle-arch/synthetic-enterprise/main/[filepath]), not blob URLs. Documented in CLAUDE.md Governing Principles and MASTER_BACKLOG.md NTFY Protocol.

---

## Session: Phase 2a — SME Segment, Context Handshake, Background Worker (2026-06-09)

- **Frontier tokens:** ~11,500 (estimated — session spans context summary continuation)
- **Local model calls:** 1:
  - `qwen2.5-coder:14b` (~2,100 prompt / ~1,800 eval) → `sim/profile_class_3.py` from edit-in-place spec (copy `profile_class_1.py`, change CSV path and function name). Draft correct on first pass. Frontier: stripped markdown fences (sed), validated 48 periods / 48.12 kWh daily total.
- **Hand-written:** `simulation/run_phase2a.py` (360-line orchestration — true chronological term interleaving, Context Handshake integration, profile-class routing), all background worker files (background_worker.py, run_queued_tasks.py, start_worker.sh), sim/cache_store.py, all documentation.
- **Produced:**
  - Files created (11): sim/profile_class_3.py, sim/data/profile_class_3_gad.csv, simulation/run_phase2a.py, sim/cache_store.py, background/background_worker.py, background/run_queued_tasks.py, background/start_worker.sh, docs/instructions/background-tasks.md, docs/observability/background-worker-log.md, docs/observability/PHASE_2a_SUMMARY.md, docs/data-sources/profile-class-3.md
  - Files modified (5): saas/customers.py (C5+C6 added), STATUS.md, CLAUDE.md (autostart line), docs/simulation-strategy.md (Phase 2a section), docs/observability/token-log.md
  - Run output: 1,622 lines, 9.5-year full window, 760k+ settlement records across 6 customers (C1–C6), 54+ terms total
  - Key numbers: Treasury £18,417→£27,119 (+£8,702). Gross £25,721. Capital £17,019 (66.2%). Net £8,702. SURVIVED.
- **Phase 2a key findings:**
  1. **C6 (warehouse, 45k kWh) net −£1,176** — capital costs (£6,470) exceeded gross margin (£5,294) across 9.5 years. Large SME customers are not viable at flat-margin pricing under capital physics.
  2. **hf=0.00 trap is EAC-dependent** — C6 (45k) escaped it (capital cost signal strong enough throughout); C5 (25k) trapped same as all 4 resi customers. Threshold somewhere between 25k–45k kWh at prevailing price levels.
  3. **Context Handshake: all 401** — `ANTHROPIC_API_KEY` not in subprocess environment. Monitor fired ~200 times (VaR trigger too sensitive: fires every 30-day cooldown because σ_recent > 0.60 throughout), but zero successful agent invocations. Pre-Phase-2b fix required.
  4. **VaR trigger recalibration needed** — 1.20× threshold triggers too easily; treasury-health gate required so committee doesn't wake on every cycle during good years.
  5. **2021 worst year: −£1,600 net** — SME capital costs during energy crisis spike were 10× the Phase 1e 2021 loss.
  6. **2023 redemption: +£5,127 net** — same crisis-tariff-vs-falling-spot mechanism as Phase 1e, amplified by SME volume.
- **Notes:**
  - **Background worker infrastructure created this session** — autonomous off-peak Qwen-only task runner, pauses 16:00-19:00 GMT, reads docs/instructions/background-tasks.md queue. 6 tasks queued (Elexon cache, weather cache, PC3 profiles, NBP gas, code-quality audit, sensitivity experiments). Worker started in tmux session `background-worker`.
  - **API key subprocess problem confirmed** — risk_committee_agent.py uses os.environ.get("ANTHROPIC_API_KEY", "") which returns "" in background subprocesses. Fix: switch to anthropic SDK auto-discovery from ~/.anthropic/ config, or write key to a credentials file. This is the pre-condition for Phase 2b (working Context Handshake required before adding gas commodity).
  - **C6 pricing insight** — current price_fixed_tariff() applies same margin % regardless of customer size or segment. C6 at 45,000 kWh annual needs a higher margin loading to be viable under capital physics. This is Phase 2+ work; the finding is documented for Rich's review.

- [2026-06-09T10:14:18Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2a_repriced)

---

## Session: Pricing Fix + Context Handshake Recalibration (2026-06-09)

- **Frontier tokens:** ~9,000 (estimated — continuation from Phase 2a session)
- **Local model calls:** 1:
  - `qwen2.5-coder:14b` (~2,400 prompt / ~900 eval) → `saas/tariff_pricing.py` full rewrite, activity-based formula. Draft correct. Frontier: stripped fences, improved docstring (size-independence note), wrote final file.
- **Hand-written:** `simulation/run_phase1e_repriced.py`, `simulation/run_phase2a_repriced.py`, `docs/observability/pricing-fix-comparison.md`, all risk committee edits (direct frontier edits — minimal diffs not worth delegating).
- **Produced:**
  - Files created (3): `simulation/run_phase1e_repriced.py`, `simulation/run_phase2a_repriced.py`, `docs/observability/pricing-fix-comparison.md`
  - Files modified (5): `saas/tariff_pricing.py`, `simulation/renewals.py`, `sim/risk_committee.py`, `sim/risk_committee_agent.py`, `STATUS.md`
  - Run output: 2× full 9.5-year simulation runs (Phase 1e repriced + Phase 2a repriced)
  - Commit: `71d7d0e`
- **Pricing fix key numbers:**
  - C6: net -£1,176 → +£620 (+£1,795 improvement). Flat margin was under-pricing capital costs.
  - Portfolio net margin: £8,702 → £13,679 (+£4,977). Treasury: £27,119 → £32,095.
  - Capital cost ratio: 66.2% → 55.4% (gross margin grew, capital unchanged).
  - Year 2025: net -£135 → +£496 (flipped positive under new pricing).
- **Context Handshake:**
  - risk_committee_agent.py: switched from urllib+env-var to `anthropic.Anthropic()` SDK (lazy import inside `_call_frontier` — SDK not installed in system Python 3.14; fails gracefully via try/except in orchestration).
  - risk_committee.py: `VAR_BREACH_MULTIPLIER` 1.20 → 2.50; added `_starting_treasury` health gate.
  - Result: 0 wake-ups in repriced run (correct — treasury grew to £32,095, well above 1.5× start threshold of £27,625).
- **Notes:**
  - **Anthropic SDK not in system Python 3.14** — `python3` has no `pip`, no `ensurepip`. Lazy import is the workaround: module imports cleanly, committee invocations fail at call time (caught by try/except). SDK install via `pip install --break-system-packages` is the pending fix for Phase 2b.
  - **Phase 1e repriced picked up C5/C6** — `CUSTOMERS` now includes all 6; run_phase1e_repriced.py (which uses only PC1 shape) settled C5/C6 with wrong profile. Numbers for C1-C4 correct and match Phase 2a repriced exactly. C5/C6 in Phase 1e repriced output should be ignored; Phase 2a repriced is the authoritative comparison.
  - **Activity-based pricing is size-neutral per MWh** — eac_mwh cancels in the formula; confirmed by C2 and C6 having identical unit rates on shared term start dates, despite 12.9× EAC difference.
- [2026-06-09T13:40:31Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2b)
- [2026-06-09T13:42:11Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2b)
- [2026-06-09T13:51:45Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2b)
- [2026-06-09T13:52:24Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2b)
- [2026-06-09T13:55:29Z] cache_miss: elexon_ssp_full.json — fetched live (Phase 2b)
- [2026-06-11T13:44:15Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T13:46:47Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T13:51:57Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T13:55:04Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T13:55:10Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T13:55:56Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T14:23:58Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-11T14:30:08Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-12T16:55:01Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-12T17:06:11Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-13T15:47:47Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-13T15:50:51Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-13T20:55:02Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-13T23:05:25Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-14T06:13:19Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-14T11:05:58Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-14T14:28:17Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b
- [2026-06-14T20:57:35Z] cache_hit: elexon_ssp_full.json — background task  consumed by Phase 2b