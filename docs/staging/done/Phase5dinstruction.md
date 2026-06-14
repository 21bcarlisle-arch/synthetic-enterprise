# Phase 5b: Report Data Pipeline

## Objective

Make the annual report self-contained and automatically populated from real
simulation data. Fill the "Not available" placeholders. Surface hedge
effectiveness as a strategic insight. Make the report publicly fetchable by
Rich's strategy advisor (Claude) without any copy-paste.

## Context

Phase 5a built `saas/reporting/annual_report.py` and the reporting function
exists and is tested. But ANNUAL_REPORT.md currently has "Not available"
throughout because no simulation run output is persisted to disk. The 4b
outputs (CLV, churn, cost-to-serve, enterprise value) exist in a separate
run that isn't integrated. The report is a skeleton waiting for data.

Rich's strategy advisor cannot fetch raw.githubusercontent.com or Tailscale
URLs — only publicly indexed pages. This means every report review currently
requires Rich to manually copy and paste content, which is unacceptable
friction in the async operating model.

## Deliverables

### 1 — Persist simulation run output to JSON (Backlog item 1)

Add `--save-json` output to the Phase 4c run pipeline
(`simulation/run_phase4c_on_phase2b.py`). At the end of every full run,
write the complete structured output dict to:

`docs/reports/run_output_latest.json`

Also write a versioned copy stamped with git commit hash and timestamp
(backlog item 13) so stale cache can be detected.

The JSON must contain everything `annual_report.py` needs: per-customer
per-period settlement data, risk committee wake-ups with treasury and hedge
fractions, bill shock events, portfolio summary by year, bad debt provisions,
service quality scores.

Regenerate ANNUAL_REPORT.md immediately from this JSON once it exists.
The "Not available" placeholders should be gone from every section that has
real data.

### 2 — Integrate Phase 4b outputs (Backlog item 2)

Merge the Phase 4b run (`simulation/run_phase4b_on_phase2b.py`) outputs into
the same JSON cache: CLV per customer, churn risk score per customer per
year, cost-to-serve per customer, home-move win rate, enterprise value.

The annual report's Customer Book and Pricing & Margin sections should then
show real figures, not placeholders.

### 3 — Persist VaR ratio per risk committee wake-up (Backlog item 3)

`run_phase2b.py` computes `portfolio_var_current` and `portfolio_var_stressed`
at each risk committee check but doesn't return them. Add them to the
`committee_wake_ups` entries so the annual report can show VaR ratio
(current vs stressed floor) per year.

### 4 — Hedge effectiveness analysis (Backlog item 10)

The `hedge_evolution` data (`actual_net` vs `naked_net` per term per
customer) already exists in the run output. Surface it in the annual report
as a dedicated section per year:

- Total actual net margin vs what margin would have been with zero hedging
- Per customer: did hedging add or cost value that year?
- Worst hedging decision of the run: which customer, which year, how much
  did over-hedging cost?
- Best hedging decision: which customer, which year, how much did hedging
  protect?

This is the most strategically interesting question in the whole simulation:
did the risk committee's interventions actually make money or just reduce
variance?

### 5 — Public report URL via GitHub Gist (new item)

After every `make report` run, create or update a GitHub Gist with the
full content of ANNUAL_REPORT.md. The Gist should have a fixed description:
"Synthetic Enterprise Annual Report — latest" so it can be found by search.

This allows Rich's strategy advisor to search for and fetch the report
directly without any copy-paste from Rich.

Include the Gist URL in the NTFY notification when the report is regenerated.

Add `make publish-report` as a Makefile target that runs `make report` then
updates the Gist. Make this the default post-run publishing step.

## Constraints

- Delegate all implementation to local Qwen
- Do not re-architect the simulation — add persistence at the output boundary
  only, don't change the simulation internals
- The JSON cache must be regenerable from a fresh run at any time — it is a
  cache, not the source of truth
- If 4b and 4c outputs have different time bases or customer sets, handle
  the merge gracefully and document any gaps explicitly in the JSON

## Gate

**[REVIEW_GATE]** — Rich reviews the regenerated ANNUAL_REPORT.md (now with
real data) and the Gist URL before any further reporting work proceeds.

Confirm:
- "Not available" placeholders are gone from all sections with real data
- Hedge effectiveness section is present and readable
- Gist URL is publicly accessible

## NTFY

On completion:
1. "Phase 5b complete. Annual report regenerated with real data."
2. "Gist URL: [url] — strategy advisor can now fetch directly."
3. "Hedge effectiveness summary: [one line — did hedging add or cost value
   overall across the 9.5yr run?]"
