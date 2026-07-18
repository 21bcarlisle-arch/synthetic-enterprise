# Payment Allocation, Ageing & Late-Payment Interest — anchors for M2 (D5)

**Purpose:** record the published-practice anchors that
`company/billing/account_ledger.py` (allocation) and
`company/billing/arrears_engine.py` (ageing / dunning / statutory interest /
write-offs) are built to, so the mechanism is anchored to reality rather than
invented.

**Provenance / honesty (R9):** this build ran in an autonomous context with **no
network access** — nothing below was freshly fetched this session. Statutory
figures (LPCDA 1998 rate and fixed-compensation bands; Limitation Act 1980
6-year period) are **well-established UK statute recalled from training-era
knowledge and are high-confidence as statute**, but the specific current Bank of
England base rate is an *input to* the model (passed in per period), never
hard-coded here. Ofgem SLC citations are recalled, not re-verified against the
live consolidated licence conditions — tagged `[L]` where the exact condition
number should be confirmed on next touch. Confidence tags: `[H]` high /
`[M]` medium / `[L]` low.

## 1. Payment allocation

| Rule as built | Published-practice anchor | Confidence |
|---|---|---|
| **Balance-based (resi / micro-SME):** payments post as credits against a single rolling account balance; a partial payment simply reduces the balance; NO bill-to-payment matching. | Standard UK domestic energy practice — customers on Direct Debit / budget plans run a rolling account balance (the mechanism that makes flat monthly DD vs seasonal actual bills coherent). Ofgem's DD guidance frames the account as a running credit/debit balance reconciled at annual statement, not invoice-matched. | [H] as practice / [L] exact Ofgem doc not re-fetched |
| **Open-item (SME / I&C):** a payment allocates to specific invoices per the customer's **remittance advice** where supplied, else **OLDEST-FIRST** across non-disputed open invoices. | Standard commercial accounts-receivable practice. Remittance-directed allocation is the debtor's right; in its absence, oldest-first (FIFO) is the conventional default in UK/commercial ledgers (and reduces the debtor's exposure to statutory interest, which accrues on the oldest debt first). *Note: the strict common-law rule (Clayton's Case / appropriation of payments) gives the creditor discretion where neither party appropriates; oldest-first is the near-universal SYSTEM default and what we implement — a defensible, documented simplification per R10.* | [H] as the common default / [M] on the precise legal doctrine |
| **Disputed invoices excluded from oldest-first allocation and from ageing/dunning while held.** Remittance may still name a disputed invoice (customer's explicit choice). | Matches the existing `company/billing/ic_invoice_dispute_register.py` model and general practice that a bona-fide disputed invoice is held out of collections while under review. | [H] as practice |
| **Overpayment ⇒ unallocated credit on the account**, not force-applied. | Standard AR: unapplied cash sits as a credit until matched or refunded. | [H] |

## 2. Ageing buckets

| Rule as built | Anchor | Confidence |
|---|---|---|
| 30 / 60 / 90+ day ageing over undisputed outstanding, measured from **due date** (issue + payment terms). | Universal AR ageing convention (0-30 / 31-60 / 61-90 / 90+). Consistent with the buckets already used in `company/billing/collections.py` and `company/finance/bad_debt_provision.py` in this repo. | [H] |
| Balance-based accounts age the whole positive balance from the **oldest unpaid bill** (FIFO); open-item accounts age **each** undisputed open invoice by its own due date. | FIFO for a rolling balance; per-invoice for open-item — standard for the two models respectively. | [H] |

## 3. Statutory late-payment interest — B2B ONLY

| Rule as built | Anchor | Confidence |
|---|---|---|
| **Residential debt accrues NO statutory interest.** | Domestic energy arrears are not commercial debts; no statutory late-payment interest applies. Collections are governed by Ofgem SLC 27 ability-to-pay duties, not interest. | [H] |
| **B2B interest = Bank of England base rate + 8 percentage points**, simple, pro-rata by days late. | **Late Payment of Commercial Debts (Interest) Act 1998**, s.4 / s.6 — statutory interest is "base rate + 8%". Base rate is a per-period INPUT to the model (not hard-coded). | [H] as statute |
| **Plus fixed compensation: £40 (debt < £1,000), £70 (£1,000–£9,999.99), £100 (£10,000+).** | LPCDA 1998 **s.5A** fixed sums (unchanged since the 2002 regulations). | [H] as statute |

## 4. Write-offs

| Rule as built | Anchor | Confidence |
|---|---|---|
| Write-offs are **dated, reasoned, P&L-visible ledger events** (`WRITE_OFF_CREDIT`, `affects_pnl=True`), never a silent status flip. | General accounting control (bad-debt expense recognised on write-off) and this project's R10/R14 discipline (every financial figure dated + reasoned). | [H] |
| Reasons enumerated: gone-away, insolvency, deceased-no-estate, uneconomic-to-pursue, statute-barred, goodwill. `statute_barred` reflects the **Limitation Act 1980** 6-year limitation on simple contract debt. | Standard bad-debt reason codes; Limitation Act 1980 s.5. | [H] statute / [M] reason-code set |

## Open items for next touch (do not fabricate — verify live)

- Confirm the exact Ofgem SLC number for domestic debt/ability-to-pay (recalled as
  **SLC 27**; the repo already carries an unresolved SLC-21B/21BA-vs-31A
  inconsistency for back-billing — same "verify the condition number live" caution
  applies here).
- The current BoE base rate must be sourced per settlement period from the market
  data feed / a dated table, never assumed — the model takes it as an argument by
  design.
- Clayton's Case / appropriation-of-payments doctrine: if a genuinely
  creditor-discretion allocation is ever needed, revisit the oldest-first
  simplification.

*Added 2026-07-18 for atom D5_account_hierarchy_payments (M2). Author: BUILD fork.*
