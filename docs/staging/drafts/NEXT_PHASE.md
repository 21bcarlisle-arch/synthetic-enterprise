# Proposed Phase QD — Emergent Bad Debt (Arrears Ledger Feeds Net Margin)

**Staged:** 2026-07-04 by Claude Code (autonomous). **Opt-out window:** 4h from NTFY send. Proceeds automatically after that unless Rich redirects.

## Gap this closes (PRIORITIES.md PRIORITY 1 -- Billing Depth)

Verified via read-only investigation (agent aba5ef116fefa70fc) before proposing, per the
PRIORITIES.md instruction not to assume this priority is unstarted.

**Finding: PRIORITIES.md's stated intent -- "bad debt emerges from arrears; do not build it
separately" -- is currently violated.** Three disconnected mechanisms exist:

1. **The actual reported P&L figure** (`simulation/run_phase2b.py:1464-1467`) computes
   `bad_debt_gbp` as `revenue_gbp * get_bad_debt_rate(year, segment) * stress_multiplier` -- a
   hardcoded year x segment lookup table (`saas/cost_to_serve.py:68-75`), not a sum of actual
   customer arrears outcomes. This is what feeds `net_margin_gbp`, what Phase NU's payment-health
   observatory reports (`saas/reporting/payment_health.py:48`), and what
   `company/finance/company_pl.py` uses in the board P&L.
2. **The per-customer billing ledger** (Phases PP/PW, `tools/generate_billing_ledger.py`) runs as
   a *separate post-hoc pass* over `run_output_latest.json`, with its own independent RNG-driven
   payment-outcome model and its own arrears state machine (resi
   DD_FAILED -> FIRST_NOTICE(+7d) -> SECOND_NOTICE(+21d) -> RESOLVED(+45d)|WRITTEN_OFF(+90d); I&C
   INVOICE_DISPUTED -> DISPUTE_NOTICE(+14d) -> PAYMENT_PLAN_AGREED(+30d)|WRITTEN_OFF(+60d)). Each
   WRITTEN_OFF case carries a real `arrears_gbp` amount -- but nothing sums these into the P&L.
   Only consumed today for RAG benchmark *counts* (`tools/population_anchor.py:143`,
   `annual_report.py:8137`), never for a GBP total.
3. **`company/billing/arrears_book.py`** -- a third `ArrearsBook`/`ArrearsCase` state machine,
   confirmed to have zero non-test importers. Dead code.

**Fidelity gap:** the board-reported bad debt figure (and hence net margin, and Phase NU's
payment-health RAG) is a calibrated assumption, not an emergent outcome of simulated customer
payment behaviour -- even though the emergent machinery already exists and produces directionally
realistic per-customer dunning timelines. This is exactly the kind of "formula standing in for
simulated reality" the project exists to eliminate.

## Proposed scope

1. Extract the arrears/payment-outcome state machine currently in
   `tools/generate_billing_ledger.py` into a shared, deterministic module (single RNG seeded from
   customer id + year) so the same computation can run from both call sites without diverging.
2. Wire it into `simulation/run_phase2b.py`: per customer-year, compute real payment outcomes and
   arrears progression: sum `arrears_gbp` for cases reaching `WRITTEN_OFF` that year, and use that
   as `rec["bad_debt_gbp"]` -- replacing the `get_bad_debt_rate()` flat-rate formula as the number
   baked into `net_margin_gbp`.
3. Update `tools/generate_billing_ledger.py` to consume the same underlying arrears facts (no
   second independent RNG draw) so the ledger and the P&L are provably the same source of truth --
   add a test asserting `sum(WRITTEN_OFF arrears_gbp per year) == bad_debt_gbp per year`.
4. Retire `saas/cost_to_serve.get_bad_debt_rate()` as the reported figure; keep the historical
   rate table only as a benchmark/sanity-check comparator against the new emergent figure (useful
   given DESNZ/Ofgem external benchmarks already wired in `population_anchor.py`).
5. Delete `company/billing/arrears_book.py` (confirmed dead, zero non-test importers) rather than
   leave a second unused arrears model in the tree.
6. Re-run `population_anchor.py`'s bad-debt RAG check against DESNZ benchmarks with the new
   emergent figures -- the Phase PS finding (arrears RED 29-31% most years) may have been an
   artifact of the flat-rate assumption; this phase will show whether it changes.

## Why this outranks alternatives right now

- PRIORITY 2 (shadow-live decision log persistence) and PRIORITY 3 (website design system) are
  both lower-value per PRIORITIES.md's own ordering, and neither touches a case where a reported
  financial figure is provably disconnected from the simulated mechanism meant to produce it.
- Two-way-door: additive/refactor, fully reversible (old rate table kept as comparator, not
  deleted), no company-layer epistemic barrier concern (bad debt is SIM ground truth, not a
  company estimate).

## Not in scope
- Company-side bad-debt *estimation* (how the company predicts arrears risk) -- unaffected; this
  phase only fixes how SIM ground truth is computed, which the company still can't see directly.
- Shadow-live and website-design-system priorities -- untouched, remain queued at P2/P3.
