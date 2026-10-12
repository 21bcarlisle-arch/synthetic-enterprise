**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** `DD_seasonal_cashflow_physics`

# The published provision was the world's incidence, and the company's own provision stock was never read

*Delivery seat, 2026-10-11, direction item `the-bad-debt-provision-is-the-companys-own-aged-receivables`.
Duplicate-work check: the live claim `the-movers-final-bill-and-the-arrears-pool-are-read-on-the-slice-7-book`
shares `simulation/run_phase2b.py` but is the movers' exit draw on the world side. Different work; carried on.*

## What a GB supplier's provision counts

A **stock**, not a flow: at a balance-sheet date, the expected loss on the receivables the supplier
holds, read **bucket by bucket** as a share of each bucket's gross value. Centrica plc ARA 2025 Note 17
p.175 publishes the only cross-tab (`docs/market_research/dd_failure_basis_and_live_arrears_provision_rates.md`
C6): UK residential, by footing and by days beyond invoice date.

| footing | <30d | 30-90d | >90d |
|---|---:|---:|---:|
| live, direct debit | 0% | 1.4% | 7.4% |
| live, pay on receipt | 4.5% | 15.1% | 50.3% |
| **closed account (final bills)** | 31.6% | 57.6% | 87.8% |

The P&L **charge** is the change in that stock plus what was written off (Ofgem Appendix 2, Dec 2024,
s.2.4). `docs/market_research/bad_debt_provisioning.md` agrees on the shape (IFRS 9 simplified approach,
a matrix over aged receivables).

**Not established, carried as `None` with the reason:** prepayment (Centrica publishes no live
prepayment row) and business accounts (the business table on the same page is not transcribed into
the market research, and the company's method register does not answer for SME accounts). Their
receivables are reported, unprovisioned, beside the figure.

## What the run published as "provisioned"

`provisioned_total_bad_debt` (annual report `provisioned_bad_debt_gbp`, £94,999 on the single-levy run)
is `revenue_gbp x world_bad_debt_incidence(year, segment) x stress` (`simulation/run_phase2b.py`),
frozen by `settlement_clocks.refresh_settlement_scalars`. It is a **flow on settlement revenue at the
world's own default incidence**. Nothing in it is a receivable, an age, or a company record. The
annual report's comment called it "what the company PROVISIONED at flat rate". That is wrong: the
company never computed it.

The company-side machinery already existed and was never asked for a stock:
`company/pricing/default_belief._provision` reads the company's own `LedgerBook` (fed by the payment
seam in `background/live_payment_triad.py`) at the Centrica rows, with the final-bill row once an
account reads as closed, but only to learn a renewal's per-account charge.

**Which "account 1100".** `saas/ledger.build_ledger`'s account 1100 is billed minus a *modelled*
payment (`saas.payment_behaviour`: bill less a flat 2% "provision", paid on an expected date). No
observed payment reaches it, so ageing it would age the model and not the customers. The company's
**observed** receivables are the payment-seam ledger the consumer keeps. The provision is read from
that ledger. The two books disagreeing is recorded here, not fixed.

## The change

* `company/pricing/default_belief.provision_stock(book, on, payment_method_of)` is the stock at a
  date. Bucket by bucket: `final_bill` (no bill in the 62 days to the date), `live_direct_debit`,
  `live_pay_on_receipt` (incl. a DD bill unpaid past the 30-day re-presentation window, which the
  company already re-rates), and `no_published_row` (provision `None`, reason named).
* `PaymentObservationConsumer.provision_stock` and `LivePaymentTriad.provision_stock` are the doors,
  shaped like `default_belief_rate`.
* `run_phase2b` records `company_provision` at each 31 December and at the run's end, and the annual
  report publishes it as `company_provision`. The world-incidence trio keeps its keys and its
  `settled-provisioned` clock, and its comment now says what it is.
* Control: a world-truth input reds.
  `tests/company/pricing/test_the_provision_is_the_companys_own_aged_receivables.py`.

## Pre-registration (written 2026-10-11, before any run carried the new figure)

**Subject:** the single-levy run (payload stamp `7379375f6`). Its ledger was not saved, so the
company's stock can only be read on a re-run that carries this change. Any re-run is at a later HEAD
than 7379375f6, so a miss could come from the intervening commits as well as from the prediction.
The re-run's HEAD will be stated beside the grade.

**Prior used.** The own-book charge measured on 2026-10-04 (`done/SEAT_FINDING_THE_OWN_BOOK_BELIEF_SHIFT_FROM_ASKING_GAS_LEGS_ON_GAS_2026-10-04.md`)
was ~1.5% of billed, whole book. The payment-seam ledger accumulates settlement revenue (£2,228,274
on this run, unchanged by the levy fix). The company books no write-off on that ledger that I know
of, so the closing stock should carry most of the cumulative charge.

| # | prediction | refuted if |
|---|---|---|
| P1 | closing provision stock (run end) **£15k to £45k**, point £28k | outside the range |
| P2 | the `final_bill` bucket holds **at least 60%** of the stock | below 60% |
| P3 | `live_direct_debit` provision is **£0**: under 30 days the row is 0%, and older DD money re-rates to pay on receipt | any non-zero |
| P4 | `no_published_row` receivable is **> £0** (prepayment and SME money is owed and unprovisioned) | zero |
| P5 | the company's stock is **15% to 50%** of the world-incidence figure (£94,999) | outside the range |
| P6 | year-end stocks **peak at 2022 or 2023** (crisis arrears) | the peak is another year |

P5 compares a stock with a flow, on purpose. It is the comparison a reader of the old figure would
make, and it says how far that figure was from anything the company holds. It is not a ratio of like
quantities.

## Controls, each mutation-proven (2026-10-11)

The table was printed at hand-built inputs before any test was written. £400 pay-on-receipt at 30-90
days gave £60.40, and £200 of final bills past 90 days gave £175.60, both checked against the rows by
hand. Every mutation below turned the suite red:

| mutation | reds |
|---|---|
| `closed = False` (a closed account read on its live row) | 2 |
| the no-row bucket given the pay-on-receipt rate | 4 |
| `all_records` (world settlement) passed into the run's provision read | 1 (the world-input control) |
| the report falling back to the world figure when the company's is absent | 1. This stayed green until the absent-company leg was added: it was a missing test, not an equivalence |
| "closed" asked of every bill ever, not the bills held on the reading date | 1 |

## Downstream, of what this assumes

* `tools/generate_value_arms_data.py` `CLOCK_MEANING["settled-provisioned"]` and its `superseded_note`
  still tell site readers that the clock is "the company's flat-rate bad-debt assumption". It has
  been the world's incidence since 2026-08-14. That text is generated into published artefacts, so
  correcting it means regenerating them. It is not done here and is handed on.
  `simulation/settlement_clocks.py`'s meaning for the same clock is corrected in this change.
* `saas/ledger` account 1100 is still billed less a modelled payment (above). Whether that book
  should exist next to the payment-seam ledger is the question `DD_seasonal_cashflow_physics` L3
  already holds.

## Grade

*Not yet graded. The figure first exists on the next run that carries this change.*
