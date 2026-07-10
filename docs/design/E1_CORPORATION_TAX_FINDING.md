# E1 (double-entry ledger) FRAME finding: Corporation Tax is completely absent

**Status:** Real, well-anchored FRAME-stage finding. No code changed. Filed from the sixteenth
dial-weighted maturity-map self-refill draw, 2026-07-10, `E1_ledger_double_entry` (level 2->3).

## What was checked

`company/finance/double_entry.py`'s `balance_sheet()` genuinely balances (Assets = Liabilities +
Equity, `equation_holds`) for every real year 2016-2025 in the current production run — confirmed
directly, not assumed. The ledger mechanism itself is sound. Checking it against its own
real_world_twin ("a real supplier's statutory accounts") found a real, complete absence: grep for
`corporation_tax`/`corp_tax`/`tax_provision` across `company/finance/` and `saas/` returns zero
hits. **No UK Corporation Tax is modelled anywhere.** `income_statement()`'s `net_margin_gbp` is
a pre-tax operating profit figure, not the post-tax "Profit for the year" a real company's
statutory accounts would report as their headline number.

## Quantified magnitude (real data, not estimated)

UK Corporation Tax since April 2023: main rate 25% (profits > £250,000), small profits rate 19%
(profits ≤ £50,000), marginal relief on a sliding scale between the two thresholds. Before April
2023: flat 19%. Applying this to the real reported pre-tax profit figures:

| Year | Pre-tax profit | Approx. rate | Approx. tax | Post-tax profit |
|---|---:|---:|---:|---:|
| 2023 | £856,787.95 | 25% | £214,196.99 | £642,590.96 |
| 2024 | £1,172,190.42 | 25% | £293,047.61 | £879,142.82 |
| 2025 | £470,392.87 | 25% | £117,598.22 | £352,794.65 |

A ~25% reduction in reported profit for any year with profits above the marginal-relief
threshold (most years in this simulation, given its growth trajectory) — a materially
significant, not cosmetic, effect.

## Why this is NOT simply "another margin bug" to fix blind

`docs/market_research/ASSUMPTIONS.md`'s EBIT% anchors (EDF/British Gas CSS, Ofgem's own cap EBIT
allowance) are, by definition, **pre-tax** figures — EBIT = Earnings Before Interest and Tax. The
sim's current pre-tax-only profit figure is the CORRECT basis for those specific comparisons;
the absence of Corporation Tax is not a bug relative to the EBIT-style benchmarking this session's
MARGIN_REALISM work has been doing. Adding Corporation Tax and silently replacing the existing
`net_margin_gbp` figures used throughout the dashboard/Financial tab/margin-bridge work would
introduce a THIRD margin-definition basis-swap into a programme already carefully unwinding two
(the commodity-vs-total-revenue question from Step 1, and the years[]-vs-ledger question from
E2/B1/D2) — repeating the exact mistake class this whole thread of work has been correcting, not
avoiding it.

**What genuinely IS missing against the real_world_twin:** a real supplier's statutory accounts
always report a proper three-line waterfall — "Profit before tax" → "Corporation tax expense" →
"Profit for the financial year" — with the LAST line, not EBIT, being the headline number in
Companies House filings and most investor-facing summaries. `E1`'s own scope (statutory-accounts
completeness) genuinely needs this; the EBIT-benchmarking work does not.

## Recommendation (not built here)

Add Corporation Tax as a genuinely NEW, clearly-labelled additional statutory-accounts line —
new ledger account (e.g. `7001 Corporation Tax Expense` / `2200 Corporation Tax Payable`), a
`make_corporation_tax_event()` following the existing `saas/ledger.py` event pattern, wired into
`income_statement()` to add a `profit_before_tax_gbp` / `corporation_tax_gbp` /
`profit_for_year_gbp` triplet — WITHOUT removing or silently renaming the existing
`net_margin_gbp` field every other surface already consumes. Real UK rate history (19% flat
pre-April 2023, 19%/25%/marginal-relief thereafter) is a clean, well-anchored, low-ambiguity
build once the labelling question above is respected. Registering as a real next BUILD step for
E1, not rushed into this same FRAME-stage turn given the basis-conflation risk.
