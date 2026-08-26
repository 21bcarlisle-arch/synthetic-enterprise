**Severity:** LATENT · **Lane:** H_harness

# `working_capital` subtracts VAT twice, and the only reason no published figure is wrong is that nothing has ever posted to the VAT account

**Found by:** reading `company/finance/treasury.py` while repairing the negative trade receivable
named at the end of
`docs/staging/WORKER_FINDING_THE_TREASURY_DRAWDOWN_FIGURE_IS_AN_ARTEFACT_OF_SORTING_A_BALANCE_THAT_WAS_NEVER_A_SERIES_2026-08-24.md`,
2026-08-24. Not looked for. Registered rather than fixed on sight
(SELF_INTERRUPT_DISCIPLINE — the supply of harness findings is infinite).

## Observed, with evidence (R9)

`company/finance/treasury.py::working_capital`:

```python
current_liabilities = (
    balance_sheet.get("vat_payable_gbp", 0.0)
    + balance_sheet.get("total_liabilities_gbp", 0.0)
)
```

`company/finance/double_entry.py::balance_sheet` builds `total_liabilities_gbp` by summing
**every** liability-type account in `ACCOUNTS`, which includes 2100 VAT Payable — the same figure
`vat_payable_gbp` reports on its own. So VAT is subtracted twice from working capital.

## Why no published figure is wrong today — observed, not assumed

**Nothing in the company ever credits 2100.** `grep -n '"2100"' company/finance/double_entry.py`
returns exactly two hits, both readers (the chart entry and `vat_payable = net("2100")`); no branch
of `to_journal_entry` names it. A `vat_remittance_event` posts DR 4001 / CR 1001 — "VAT was
collected inside billing revenue; remittance to HMRC reduces revenue" — so the liability is never
recognised in the first place. `vat_payable_gbp` is therefore £0.00 in every journal this company
produces, and `0 + total_liabilities == total_liabilities`.

## Why it is LATENT rather than BLOCKING, and why it is worth a document

It is a FAIL-OPEN in the R15 sense: the expression is wrong and passes because its input is
always zero. The day anything credits 2100 — the obvious candidate being a real VAT-accrual entry
at billing time, which is what a supplier's books actually do — working capital silently
understates by the whole VAT balance, on a published surface, with no test to catch it.

Note that the double count is currently the *only* thing standing between this expression and a
second defect of the opposite sign: the same line would also need to stop double-counting the
newly-added `customer_accounts_in_credit_gbp`, which `total_liabilities_gbp` now carries. It does
not, because `customer_accounts_in_credit_gbp` has no separate term here — correct today, and
correct for the same accidental reason.

## The repair, when it is drawn

Drop the `vat_payable_gbp` term: `current_liabilities = total_liabilities_gbp`. That is
already the intended meaning, and it is what the balance-sheet comment on the liability sum says
the sum exists for ("so a new liability is reflected in the equation rather than silently
omitted").

**The control that must land with it** — a null control, or the repair proves nothing. Today the
fix is a no-op on every real journal, so a test over real data would pass before and after. It
needs a journal with a genuine 2100 credit (hand-built, since no event maker produces one) proving
that the pre-repair expression subtracts the VAT twice and the post-repair one subtracts it once.
Without that, this is an untested edit to a published figure's formula.

## What is NOT claimed here

That a VAT accrual *should* be posted. Whether this company's books ought to recognise output VAT
as a liability at billing and clear it at remittance — rather than netting it inside revenue — is a
fidelity question about UK supplier accounting, not a defect report, and it is not answered here.
This document is about the arithmetic being wrong regardless of which way that question goes.
