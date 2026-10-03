# The company's ledger bills one settlement record a month, not the month's bill

**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** unassigned · **Atom:** `unminted` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** Found while measuring the company's default belief against its own ledger.

## What is true

`simulation/run_phase2b.py`, the Phase NH block, calls `_payment_triad.record_period(...)` once per
customer-month. It is keyed on `_payment_month_seen` (cid, month) and passes
`amount_gbp=rec.get('revenue_gbp', 0.0)` from the **first settlement record of that month**. The
records are settlement records, not the month's bill. So the company's ledger, the one
`LivePaymentTriad` posts bills and observed cash into, holds one record's revenue as each month's
bill.

Measured on a full-decade run at `e69dbbfe5` (175 resi accounts, 8,145 posted bills): the **median
posted bill is GBP 0.023**, the largest is GBP 13.67, and the total across the decade is GBP 4,726.
One account (`C6`) is billed GBP 0.04 every month.

## What reads it

- `LivePaymentTriad.receivable` hands the renewal price `unpaid_bills_by_age` and
  `billed_last_year_gbp` (`e0370bf94`). The stock term, the loss on money already owed, is ABSOLUTE
  GBP, so in a run it is understated by orders of magnitude and is close to zero. The flow term is a
  ratio and survives.
- `arrears_state_from_collections` reads the same ledger. Whether its states depend on absolute
  amounts is NOT checked here.
- `company/pricing/default_belief.py` learns a charge per GBP billed. That is a ratio and survives,
  which is why the comparison in `docs/institutional/knowledge_map.md` stands.
- The coupled-triad gap measures (detection, ageing) count cases and are not amount-weighted. NOT
  checked here.

## The fix, not done here

Post the month's bill: the sum of that customer's records in the month, dated at the month's due
date. This changes the amounts the W2_11 payment events carry and every published figure built on
them, so it is fidelity work, done deliberately and measured. It is not a quiet repair. One leg
catches the class: assert that the ledger's billed total for a run equals the run's own billed
revenue for the same accounts, to the pound.

## Resolved 2026-10-03 (delivery seat): the ledger is billed the month's revenue

`run_phase2b` keeps one open month per leg. It sums every settlement record's `revenue_gbp` into
that month and posts the bill once, when the leg's next month starts or the run ends. Terms run
in date order across customers and a renewal splits a month between two terms of one leg, so
posting at the month's first record could not see the whole month. Posting twice is barred
because the ledger keys a bill on (customer, month).

**What moves and what does not.** `generate_payment_event` carries the amount and draws nothing on
it (`simulation/payment_behaviour_source.py`), so WHICH bills fail and which are late is unchanged.
What changes is every absolute amount the company reads from its own receivable:
- The renewal price's stock term on money already owed now prices real balances.
- `billed_last_year_gbp` and the default belief's charge-per-pound are ratios. They change only
  through the amounts actually owed.

**Prediction, written before any run of the change:** the control path's renewal outcomes are
identical before and after. The control arm prices no receivable, and the only remaining reader,
`arrears_state_from_collections`, is assumed amount-independent. A difference refutes that
assumption, which this finding listed as NOT checked.

Control: `tests/simulation/test_the_company_ledger_bills_the_months_revenue.py`. It checks that the
ledger's billed total equals the run's own revenue to the pound, and that no (customer, month) is
billed twice.
