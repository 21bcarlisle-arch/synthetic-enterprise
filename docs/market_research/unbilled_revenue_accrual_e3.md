# E3_accrual_restatement — DISCOVER findings: unbilled revenue accrual

**Atom:** `E3_accrual_restatement` (epoch 2, `docs/design/maturity_map.yaml`). **Status:** DISCOVER
only, per EPOCH_GATING_AND_ATOM_AUTHORSHIP.md Rule 1 — BUILD stays gated pending epoch sequencing.
`level_current` unchanged (0).

## The charter's own candidate hypothesis

`docs/design/charters/E_finance_treasury.md` names a candidate for E3's first accrual mechanism:
*"revenue for consumption that occurred within a reporting period but is billed in a later one,
given estimated-read timing lags already modelled elsewhere in this project"* — explicitly flagged
as "a hypothesis, not yet verified against real billing-lag data in this codebase."

This pass verifies it against both real external practice and real internal data.

## External finding (real, sourced — WebSearch, 2026-07-12)

**"Unbilled revenue" is standard, named practice in UK/US energy-utility accounting**, not a
project-specific invention:

- Accrued unbilled revenues are estimated from consumption since the last meter reading, valued at
  the applicable customer-class rate, and carried as a current asset (accounts receivable and
  unbilled revenue, net) on the balance sheet.
- Estimated amounts are adjusted when the actual meter read arrives and the true consumption is
  known — the exact "estimate now, true-up later" shape this project's own `D3_catchup_rebilling`
  atom already models on the customer-billing side.
- **FRS 102 Section 23's revenue recognition model is converging to IFRS 15's 5-step model for
  periods beginning on or after 1 January 2026** — a live, current standards change (not a stale
  citation), reinforcing rather than weakening the case for building this mechanism now: the
  disclosure/recognition bar for "revenue not yet invoiced" is getting more precise, not less.

Sources: general search results on unbilled-revenue accounting treatment in utility accounting
(FinOptimal, SOFTRAX, HiBob, HubiFi glossaries), FRS 102 Section 23 revenue-recognition update
coverage (ICAEW, KPMG UK, BDO, Crowe UK).

## Internal finding (real, quantified — `docs/reports/run_output_latest.json`, 2026-07-12)

- **468 of 1,588 real bills (29.5%) are on an ESTIMATED `billing_basis`**, totalling
  **£4,762,796.19** in billed value — a real, current, material exposure, not a theoretical concern.
- **Confirmed directly (grep, not assumed): neither `saas/ledger.py` nor
  `company/finance/double_entry.py` reference `billing_basis` or "estimated" anywhere.** An
  estimated-basis bill's revenue is recognised in the ledger identically to an actual-basis bill's —
  exactly the L1 gap the charter names: *"no accrual concept exists anywhere in this codebase —
  revenue and cost are recognised on a settlement/billing basis, not accrued at period boundaries."*

## The precise next BUILD step (evidenced, not hypothetical)

Recognise estimated-basis bill revenue as an accrual (an "unbilled revenue" current asset, not yet a
firm receivable) in the ledger, with a real restatement event firing when `D3_catchup_rebilling`'s
own catch-up-rebilling mechanism resolves the estimate against a subsequent actual read. **The two
mechanisms should share the same underlying real-vs-estimated delta, not recompute it
independently** — `D3`'s `_resolve_catchup()` already computes exactly this delta for the
customer-facing bill correction; E3's accounting-side accrual/restatement should consume that same
computed delta rather than deriving a second, independently-built version (the same "one
architecture, not two" principle already applied to `D2_three_clocks`/`W1_reveal_over_time`).

## What this does NOT yet resolve (honest, open items — R10)

- Exactly which double-entry accounts the accrual/restatement should post to (a new "unbilled
  revenue" asset account, and where the restatement's prior-period correction lands on the balance
  sheet) is a design question for the eventual BUILD/FRAME pass, not resolved here.
- Whether the accrual should be computed per-bill (matching D3's own grain) or at a coarser
  period-end aggregate is an open design choice — this DISCOVER pass found the real data supports
  either, not which is correct.
- L3/L4 (the full prior-period restatement disclosure shape, and the double-entry ledger's own
  historical balance-sheet restatement) remain untouched — this pass only sharpens the L1→L2 target.
