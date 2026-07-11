# E — Finance & Treasury: lane charter

**Dial reached 3 (hot) — charter earned per the map's own rule** ("a lane earns its charter when
its dial reaches 3+", `docs/design/MATURITY_MAP.md` Section 4), as part of the SPIKE_WEEKEND
2026-07-11 DISCOVER/FRAME charter flood.

## Mission

The company's books must work exactly like a real UK supplier's statutory accounts: one
double-entry ledger that actually balances, one true revenue/margin definition used consistently
everywhere it's reported, and the ability to model the accounting realities real companies live
with — Corporation Tax, accruals, and honest correction of prior-period errors — rather than a
simplified cash-in/cash-out P&L that only looks right until someone asks it to reconcile.

## Sub-capability tree

- **E1_ledger_double_entry** (this lane) — the core double-entry ledger + management accounts
  (income statement, balance sheet) a real company's finance function runs on.
- **E2_revenue_reconciliation** (this lane) — one true revenue/margin definition, reconciled
  across every reporting surface (Financial tab, margin bridge, run-completion insights).
- **E3_accrual_restatement** (this lane) — period-end accrual recognition + prior-period
  restatement handling, genuinely unbuilt.
- **B1_margin_bridge** (lane B, sibling) — consumes E2's reconciled figures as its own input;
  currently blocked on the SAME Epoch-2 sequencing as E2 (see below).
- **D2_three_clocks** (lane D, sibling, dial=4 hot, own charter `docs/design/charters/
  D_billing_metering.md`) — E2's own root-cause finding (below) traces its unresolved gap
  directly into D2's scope, not a separate E-lane problem.

## What L2/L3/L4 mean in this lane's terms

### E1_ledger_double_entry (level 3/3 — AT TARGET, loop_stage=harden)

Already real: `company/finance/double_entry.py` builds a genuine double-entry journal from
booked events, and `balance_sheet()` provably balances (Assets = Liabilities + Equity) for every
real year 2016–2025 (`docs/design/E1_CORPORATION_TAX_FINDING.md`). UK Corporation Tax is built
as a genuinely additive triplet — `profit_before_tax_gbp` / `corporation_tax_gbp` /
`profit_for_year_gbp` via `uk_corporation_tax_gbp()`, real HMRC rates (19% flat pre-April 2023,
then 19%/25%/marginal-relief thereafter) — without touching the pre-existing `net_margin_gbp`
field every other surface already consumes (deliberately, since that field is the correct
EBIT-style pre-tax basis this project's own EDF/British-Gas/Ofgem-cap benchmarking anchors
require). **What "harden" still means:** the balance sheet does not yet model Corporation Tax
*payment timing* (real UK companies pay Corporation Tax ~9 months after the accounting period
ends, via a Corporation Tax Payable liability that persists across the year-end) — a known,
registered scope limit, not an oversight, since no real anchor for the exact timing mechanic was
found when E1 was built.

### E2_revenue_reconciliation (level 2→3, loop_stage=frame)

- **L1 (behind us):** two independently-built pipelines computing "the same" gross/net margin
  disagreed silently — `years[yr].*` (SIM-side aggregate summing raw settlement records) vs
  `management_accounts[yr].income_statement.*` (the real ledger P&L) — with no reconciliation
  and, worse, `tools/generate_insights.py` comparing a commodity-only revenue % against a
  TOTAL-margin external benchmark, inflating every run's own headline narrative
  (`docs/design/MARGIN_REALISM_E2_TWO_PIPELINES_FINDING.md`).
- **L2 (partially reached):** the denominator question is fixed (Step 1: total revenue, not
  commodity-only) and `generate_insights.py`'s specific apples-to-oranges bug is fixed. The
  *root cause* of the deeper gross/net divergence is traced, not just patched: the ledger's
  single blended non-commodity £/MWh rate (`saas/non_commodity.py`) and the settlement layer's
  itemised per-levy model (`simulation/hedged_settlement.py`'s RO/CfD/CCL/CM/FiT + DUoS/TNUoS)
  are two never-reconciled models of the same real-world cost category, built at different
  points in this project's fidelity history. The gap is bidirectional and non-monotonic across
  years (+27.7% in 2016 to −25.3% in 2017, for example) — consistent with a genuine
  volume/timing mismatch (estimated reads, billing-period boundaries not aligning with
  settlement dates), not a simple missing-component bug in either pipeline.
- **L3 (target, genuinely blocked):** a real reconciliation between the billing pipeline and the
  settlement pipeline, explaining variance drivers (volume true-up, estimated-vs-actual reads,
  rate-change timing) the way a real supplier's finance team would — rather than picking one
  pipeline as "correct" and discarding the other. **This depends on `D2_three_clocks`**
  (physical/financial/regulatory settlement clocks reconciled per bill), which is Epoch-2 core
  and explicitly awaits the advisor's epoch-sequencing framing per the director's own 2026-07-10
  instruction. E2's own gauge/legibility questions (the denominator fix, the two adjacent report
  sections) are closed on their own terms; full numerical reconciliation is not this lane's to
  start independently.

### E3_accrual_restatement (level 0→2, loop_stage=idle, genuinely unbuilt)

- **L1 (current):** no accrual concept exists anywhere in this codebase — revenue and cost are
  recognised on a settlement/billing basis, not accrued at period boundaries, and there is no
  mechanism to restate a prior period's reported figures if a later-discovered error is found.
- **L2:** a real accrual mechanism exists for at least one line item that genuinely needs one
  (a candidate: revenue for consumption that occurred within a reporting period but is billed
  in a later one, given estimated-read timing lags already modelled elsewhere in this project).
- **L3:** a real prior-period restatement can be modelled end to end — a later-discovered error
  in a past period's figures is corrected retrospectively, following FRS 102/IAS 8's own
  disclosure shape (restated comparatives, the amount of correction per line item disclosed),
  not silently overwritten.
- **L4:** a restatement genuinely flows through to the double-entry ledger's own historical
  balance sheet, matching how a real company's statutory accounts show "as restated" comparative
  columns after a material prior-period error is found and corrected.

## Named best-practice references

- **FRS 102 Section 1A** (Financial Reporting Council) — small-entity statutory reporting
  requirements: a balance sheet, profit and loss account, and notes, using full FRS 102
  recognition/measurement rules with reduced disclosure. https://www.frc.org.uk/library/standards-codes-policy/accounting-and-reporting/uk-accounting-standards/frs-102/
  and https://www.icaew.com/technical/corporate-reporting/uk-gaap/frs-102-topics/small-entities
  — directly grounds E1's own real_world_twin ("a real supplier's statutory accounts").
- **HMRC Corporation Tax rates and marginal relief** — the real 19%/25% rates and the 3/200
  "Standard Fraction" this project's own `uk_corporation_tax_gbp()` already implements, confirmed
  live: https://www.gov.uk/hmrc-internal-manuals/company-taxation-manual/ctm03925 and
  https://www.gov.uk/government/publications/rates-and-allowances-corporation-tax/rates-and-allowances-corporation-tax
  — from 1 April 2023, main rate 25% (profits > £250,000), small profits rate 19%
  (profits ≤ £50,000), marginal relief in between via the 3/200 fraction; matches this codebase's
  existing implementation exactly, re-confirmed rather than assumed.
- **IAS 8 / FRS 102 prior-period error correction** — the standard E3 needs before any accrual/
  restatement code gets written: a material prior-period error is corrected retrospectively by
  restating comparative amounts, with disclosure of the correction amount per line item affected.
  https://ifrsbuddy.com/learn/en/ias-8-prior-period-error and
  https://stevecollings.co.uk/frs-102-frs-105-error-correction/ — the "as restated" comparative-
  column convention (best practice, not mandatory) is the concrete shape L3/L4 above should
  target.

## Lane roadmap

1. **DONE (E1):** double-entry ledger + Corporation Tax triplet, both provably correct against
   real data (balance sheet balances every year; CT rates match HMRC's own published thresholds).
   Registered scope limit: balance-sheet CT-payment-timing not modelled.
2. **DONE this far (E2):** revenue-denominator gauge fixed; `generate_insights.py`'s real
   apples-to-oranges bug fixed; the deeper billing-vs-settlement divergence's root cause traced
   (not just its symptom). **Genuinely blocked, not stalled:** the actual numerical reconciliation
   is `D2_three_clocks`'s scope — do not start it independently of that atom's own sequencing.
3. **Not started (E3):** needs its own DISCOVER pass identifying which real line item most needs
   an accrual mechanism first (candidate above is a hypothesis, not yet verified against real
   billing-lag data in this codebase) before any code is written.

## Simplifications register

- E1's Corporation Tax fields (`profit_before_tax_gbp`/`corporation_tax_gbp`/
  `profit_for_year_gbp`) are `None` unless a year is explicitly passed to `income_statement()` —
  only the one real call site (`annual_management_pack()`) currently populates them. Not a defect:
  additive by design, matching this project's own discipline of never silently redefining an
  existing field's meaning.
- E1 does not model Corporation Tax payment timing on the balance sheet (no real UK payment-date
  anchor was found when built) — registered, not silent.
- E2's root-cause finding is evidence feeding `D2_three_clocks`'s eventual build, not a fix in its
  own right — the non-commodity cost-category gap between the billing and settlement pipelines
  remains real and unreconciled today.
- E3 has zero code today — every L2+ claim above is a design hypothesis pending its own DISCOVER
  pass, not a partially-built mechanism.
