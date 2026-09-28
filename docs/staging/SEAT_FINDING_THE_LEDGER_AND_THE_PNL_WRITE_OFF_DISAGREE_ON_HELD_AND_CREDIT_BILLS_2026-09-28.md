**Severity:** LATENT · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `W2_payment_channel_dd_consistency_invariant`

# FINDING — the P&L wrote off bills the supplier never sent, and credits it owed the customer

## Measured before any change (2026-09-28, HEAD `c2191bd13`, real run output of 2026-09-27 23:31)

`simulation.arrears_engine.balance_write_offs` over the run's 10,681 bills: **£19,135.31 over 190
cases**. `tools.generate_billing_ledger.generate` over the same file: **£17,359.26**. Six accounts
disagree (C8, PROS-2016-0098, PROS-2018-0002, SYN-2016-005, -013, -052).

Two causes, both on the engine side:

1. **203 bills the pre-bill validation gate HOLDS** (195 `slc_6_7_billing_accuracy`, 8
   `vat_by_segment`). The ledger never issues them; the engine resolved a payment outcome for each
   anyway, and 6 of them are written off.
2. **Credit bills** (`amount <= 0`, 155 in this run — not the 24 the engine's docstring cites).
   The engine drew a payment outcome on a negative amount; two "failed" and were written off as
   NEGATIVE bad debt (C8 −£22.09, PROS-2018-0002 −£33.77).

## What is true

- **A held bill cannot be written off.** It was never issued, so it was never due, so no payment
  against it can fail. In this model nothing re-issues it (named as unbuilt follow-up in
  `company/billing/pre_bill_validation.py`), so it is never owed on any customer's account.
- **A credit bill cannot fail.** There is nothing to collect.

So the engine is the wrong side. Fix: `balance_write_offs` resolves outcomes only over the bills the
supplier issues (asked through the `company.interfaces.bill_assembly` seam, the same gate the ledger
runs), and a credit bill resolves to `credit` — no collection, no failure, no acknowledgement.

## Pre-registration (written before the fixed code is run over the real book)

- P1: ledger total == engine total, to the penny, per account.
- P2: that total is **£17,359.26** — i.e. dropping held bills from the engine's event stream moves no
  OTHER write-off (no statute-bar clock loses an acknowledgement that mattered; a leaver's close
  amount is the sum of their unheld failures either way).
- P3: 188 cases (190 − 2 credits − held cases that were written off, net of any shift). *I cannot
  pin this one exactly: 6 held keys were written off, 2 are credits; if those overlap the count
  is 182–184.* Recording the range rather than a number.

## Result (after the fix, same file)

- P1 **held**: no account disagrees. P2 **held**: engine £17,359.28 raw, ledger £17,359.26 (each case
  printed to the penny). P3 **held**: 182 cases.
- The committed book (`docs/reports/run_output_latest.json` at HEAD, 2026-09-09) agrees before AND
  after the fix: its 14 held bills and 170 credits include none the old engine wrote off. So the
  real-book control does not bite the two engine mutations on the committed book today; the
  fixture test `test_a_held_bill_and_a_credit_bill_are_never_written_off` does, each leg separately
  (removing the issued-bills filter reds it; removing the credit skip reds it at −£1,000.40). The
  real-book control will bite the next time the run output is committed with a held write-off in it.
- Every stayer's case that is not written off now ends `BALANCE_OPEN` ("Balance still open --
  GBP x unpaid, with no payment or arrangement against it"), and a dispute that is not written off
  no longer claims a payment plan was agreed. `tools/generate_payment_ledger_data.py` booked both
  old stages as CASH COLLECTED (`arrears_resolved`, `method: payment_plan`), so every such account's
  running balance read zero. It now carries the open balance. Restoring `RESOLVED` reds
  `test_no_open_balance_renders_as_resolved` on the real book (525 open cases).

## Open, filed not fixed

- **A credit on an account in arrears does not reduce the balance** in the balance-at-close rule
  ("nothing reduces the balance"). Any supplier nets an account credit against arrears. Not wired
  here: it changes write-off AMOUNTS per bill and the ledger's per-bill case mapping with it.
- **203 held bills are never re-issued and never collected.** 195 are resi gas bills held as
  implausibly low (3–90 kWh / 31 days) — summer cooking-only gas is plausibly in that range, so the
  floor itself may be wrong. Whether their consumption is booked as revenue while never billed has
  not been checked here.

## Re-draw disposition (2026-09-28 03:1x)

The direction item `the-billing-ledger-and-the-pnl-book-one-write-off` was drawn again after it had
landed. Re-measured, not re-built: `2bb03a094` (real-book control, held/credit bills never written
off, BALANCE_OPEN replaces "Arrears cleared via payment plan") and `ba1b6c259` (credit nets against
arrears) are both ancestors of origin/main; the real-book control and
`tests/simulation/test_balance_at_close_write_off.py` pass at `ba1b6c259` (14 passed); no code under
`tools/`, `simulation/`, `company/` or `site/` emits the resolved sentence. Premise spent; claim
released. The "live lane" the item described was `origin_reconcile`'s merge gate, not this work.
Still open, as filed above: the 203 held bills are never re-issued.
