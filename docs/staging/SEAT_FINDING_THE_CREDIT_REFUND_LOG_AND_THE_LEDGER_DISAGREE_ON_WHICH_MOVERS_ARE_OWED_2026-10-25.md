**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8a

# The credit refund log and the ledger disagree on which movers are owed a refund

Found by the first printing of each closed account's balance at its final bill
(`docs/staging/records/SEAT_PREREG_A_CLOSED_ACCOUNTS_BALANCE_AT_ITS_FINAL_BILL_2026-10-25.md`). The run
was 60 founder supply points to 2020-12-31, budget 0, seed 42, and it graded 34 move-outs.

**What.** The ledger (`arrears_engine.balance_settlement_from_outcomes`, the walk the P&L writes off)
closes 7 of the 34 move-outs in credit, £2.23 to £37.92 each. None of the 7 has a refund in
`credit_refund_log`. One move-out, SYN-2016-052, closes owing £27.64 on the ledger, yet the refund log
paid it a credit refund, on time.

**Why.** There are two books, and neither reads the other. The refund log
(`simulation/credit_refund_events.py`) decides who is in credit from its own level-DD smoothing
balance: the trailing-mean DD less each bill, for DD payers only. The ledger reads a credit from credit
bills and overpaid repayments. §8.8a choice 4 named this as a limit. The printed table shows the two
books disagree in both directions on the same accounts.

**Why it matters.** GSoP reg 6D grades a refund against a credit that exists. A refund paid to an
account the ledger says owes money is the company handing money back to a debtor. A credit on the
ledger with no refund is a reg 6D breach that the measure cannot see, because `move_out_final_bills`
grades only the refunds the log records. In this run that is 7 of 34 move-outs, so the "credit on
time" count is graded over the wrong population.

**What it would take.** One closing balance per account that both books read: the level DD's
over- or under-collection posted to the same ledger as the bills and payments. That is DD3 (booking
held credit as a liability), registered in `simulation/dd_balance_book.py`. Until then the refund log
should fire from the ledger's closing balance. I have not built that here. It changes who is refunded
and so moves cash, and it wants its own arm.

**I cannot yet say** what makes the 7 ledger credits. The likely source is a negative final true-up
bill on an actual closing read after an over-estimate. That is not established, and the next step is
to name the credit rows that net each one.
