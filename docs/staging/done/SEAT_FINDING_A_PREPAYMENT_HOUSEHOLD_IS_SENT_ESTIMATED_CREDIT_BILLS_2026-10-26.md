**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`

# A prepayment household is sent estimated credit bills

Part of defect 1 of the director's Explore steer. Measured on the published 4ae8da9b0f book.

## What is wrong

- **100** households pay by prepayment (a `payment_received` with method `prepayment`).
- **88 of 100** are also sent bills on an estimated read (`read_type` E).
- **3 of 100** carry an outstanding balance on a bill.

A prepayment customer pays at the meter before use. They get no monthly credit bill to pay, so they
cannot get an estimated one. Any debt they carry is recovered at the meter, not shown as "£42.73 to
pay". SYN-2016-476 paid by prepayment from its first payment in Nov 2016 and was billed like a
credit customer for nine years.

## Root cause

The payment method is a ledger attribute. Billing runs the same monthly credit cycle for every
account, so prepayment is a label on the payment and nothing about the bill changes. Class: **units
pass and the joins fail**.

## What catches it now

`_common_failures` in `tools/generate_explore_cast.py` keeps any household that "pays by prepayment
yet is sent estimated credit bills" out of every Explore slot.

## What closes it

Billing must treat a prepayment account as prepayment: vend and statement, not credit bills and
estimates. Write the knowledge page first (K8): what SLC 28 and published practice say a
prepayment statement holds.

## Done

Worker, 26 Oct 2026, delivery item `a-prepayment-account-is-billed-as-prepayment`.

**Knowledge first (K8).** `docs/market_research/what_a_prepayment_customer_is_sent_2026-10-26.md`,
published on the payments-and-direct-debit Knowledge page. A prepayment meter is paid before use;
SLC 21B.5's twice-yearly bill duty excludes prepayment; SLC 31A.9's annual statement applies, and
Ofgem says prepayment customers "do not receive energy bills in the same way"; debt is recovered at
the meter. Four GAPs are named there (periodic statements, the content of a vend statement, 31A's own
text, legacy meter reads).

**The branch.** The company was already told each leg's channel (`payment_channel_feed`) and
ignored it. Now:
- `saas.bill_generator.generate_bill` names the document: `prepayment_statement` for a
  prepayment channel, `bill` for any other.
- `company.billing.monthly_bill_assembly.build_monthly_bills` charges a prepayment leg's period at
  the meter on what was used (`billing_basis` = `prepayment_meter`): no estimate, no estimated run,
  no catch-up. The settlement read status and the unread run are kept on the bill, so the read
  duty register still records a prepayment leg's unread year (outside the duty on electricity), and
  gas prepayment is still instructed under M5.9.14.
- `tools/generate_billing_ledger.py` prints read type `M` (charged at the prepayment meter) and
  `document_type` on each period. Explore labels `M` as the prepayment meter.
- `population_sanity`'s read-seam join leaves meter-charged periods out: they have no read status
  to agree with.
- Test: `tests/company/billing/test_a_prepayment_leg_is_sent_a_statement_never_an_estimated_bill.py`,
  one partition assertion (the credit leg on the same feed IS estimated). Three mutations each red it.

**Before and after, on the 67a893e749 arm-A book** (`/var/tmp/mandate-run-out-67a893e749`, its
own issued bills; probe `/tmp/prepay_probe/arm_a.py`). "Paying by prepayment" means the world's
payment record for the leg says prepayment.

| | legs | estimated bills |
|---|---|---|
| prepayment legs | 137 | of 5,615 issued |
| before: sent an estimated bill | 113 | 3,673 |
| after: still estimated | 1 | 10 |

The "after" row is by construction, not re-run. The company's bill assembly needs the run's
customer book, which a standalone process does not have. The new branch covers every leg the
channel calls prepayment (163 on arm-A, a superset of the 137, held by the test), so what remains is
any leg the world records paying by prepayment and the channel does not name. That is one leg,
**C6, an SME**: `simulated_payment_channel` returns None for every non-domestic account, so the
company is never told an SME pays at a meter. Residual, not fixed here. Whether a GB SME on a
prepayment meter belongs in this world at all is the first question.

On the published 4ae8da9b0f ledger (`docs/state/billing_ledger.json`), the same count is 136 of
164 prepayment legs, 4,155 of 6,297 period documents. It falls at the next publish.

**What moves.** Prepayment legs stop carrying estimate-priced amounts and catch-ups, so their
billed revenue now equals what was used each month. Total energy billed over a leg's life is
unchanged where a catch-up later trued it up. Timing moves, plus any amount the back-billing limit
had barred on those legs. No published figure was re-run here; the next run carries it.

**The Explore check** in `_common_failures` stays. It now matches nothing on a fresh run, so it
guards the class.
