# Phase 1a Summary — Customer Cohort & Geography

## What was built
- `saas/customers.py` — single source of truth for the four resi customers: identity, geography (lat/lon + region), home characteristics (type, bedrooms, EPC rating, EAC), and three first-class routing fields (`commodity`, `segment`, `contract_type`) plus accessors `get_customer`, `get_customers_for_segment`, `customer_to_settlement_input`
- `docs/data-sources/customers.md` — design record explaining who the cohort is, why this geographic/archetype/EAC spread was chosen, and why each forward-looking schema field exists from day one
- `simulation/run_phase0c.py` — refactored to source identities from `saas.customers.CUSTOMERS` via `customer_to_settlement_input()` instead of a hardcoded `ACQUISITION_DATES` list

## Key findings
- **P&L is byte-for-byte unchanged**: full-year 2016 portfolio margin still **−£78.28** (consumption 9,705.99 kWh, revenue £365.71, cost £443.99), every per-customer figure identical — confirms the refactor changed *where* identities come from, not what they produce
- The cohort now has genuine geographic/archetype spread (London/Manchester/Glasgow/Cotswolds; flat/semi/tenement/detached; EAC 2,800–5,500 kWh) — deliberately, so Phase 1b weather correlation has real variation to work with rather than four near-identical profiles
- Qwen's "edit this file in place" generations are now reliably *structurally* sound but increasingly prone to small but serious substitutions buried in otherwise-correct diffs (see Key Decisions) — code review must check semantic correctness of every changed line, not just "does the diff look plausible"

## Key decisions made
- `commodity`, `segment`, and `contract_type` are first-class fields from day one (all single-valued today) specifically to avoid schema migrations when Phase 2a (SME) and Phase 2b (gas) land
- `eac_kwh` is documented nullable for a future smart-meter cohort, with **no** null-handling code written — that scenario can't happen with today's synthetic cohort, and code for it now would be speculative
- `location` stores both lat/lon (for the Phase 1b weather API) and a human-readable region (for reporting), deliberately redundant so neither consumer has to derive the other
- Hand-patched two real (not cosmetic) defects in the customers-wiring delegation round rather than re-prompting: a deleted `load_pc1_shape` import, and — more seriously — the `run_settlement()` call's consumption-shape argument silently swapped to `customer_to_settlement_input` (wrong callable for that parameter; would have broken settlement with a confusing deep TypeError rather than pointing at the cause)

## Open questions
- Should `saas/customers.py` eventually move to `interface/contracts/` now that `simulation/` reads it directly across the seam, or does "plain dicts via function arguments" remain the house pattern through Phase 1?
- Phase 1b will need a `location_id` to key weather files — should that be `customer_id` (1:1 today) or a separate identifier (in case future customers share a location)?

## Token efficiency
- **Local model** (`qwen2.5-coder:14b`, 3 delegation rounds, prompt_eval+eval): `saas/customers.py` 2,303 / `docs/data-sources/customers.md` 2,071 / wire-into-orchestration edit 2,893 → **7,267 total**
- **Produced**: 1 new module (~75 lines), 1 new doc (~37 lines), 1 surgical 11-line edit to existing orchestration — confirmed correct end-to-end against live 2016 Elexon data
- **Frontier**: session-cumulative headline tokens (in+out+cache-create) rose from 229,181 (at the Phase 0c findings checkpoint) to 475,802 — a ~246,600-token stretch covering Phase 0c wrap-up/push, authoring `MASTER_BACKLOG.md`, and all of Phase 1a. Roughly 34× the local spend for this stretch — consistent with Phase 0c's ratio and the same explanation: the frontier carries the whole codebase, runs/verifies the pipeline, and writes every commit message and doc, while the local model only ever sees short, scoped generation prompts.
