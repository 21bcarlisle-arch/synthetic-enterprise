**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `D48_billing_accuracy_the_company_measures_what_it_billed_against_what_was_used`
**Knowledge:** `home-moves` -- `docs/market_research/home_moves.md` §8.8a

# A credit bill in the middle of an account's life is never set against the next charge

Found by naming the rows behind the 7 move-outs the ledger closes in credit (60 founder supply
points to 2020-12-31, budget 0, seed 42; probe `/var/tmp/credit_refund_probe/name_rows.py`, output
`/var/tmp/credit_refund_probe/r60/named.json`).

**What.** 5 of the 7 credits are a credit bill (`outcome == "credit"`, a negative bill) from the
middle of the account's life: SYN-2016-016g (−£14.54, Dec 2016), SYN-2016-018 (−£2.23, Nov 2017),
SYN-2016-032g (−£13.65, Jun 2017), SYN-2016-035g (−£20.54, May 2017) and SYN-2016-040g (−£6.21 in
Mar 2017, −£0.21 in Aug 2019). Each sat on the account until the move, for 5 weeks to about 2½ years.
In the meantime every later bill was paid in full. The other 2 are a negative final bill, and those
are right.

**Why.** `arrears_engine.balance_settlement_from_outcomes` sets a credit against arrears only (a failed
bill). A `success` row pays its bill in full, whatever credit is waiting.

**Why it matters.** A statement of account carries the balance forward (SLC 27.17). So a credit would
ordinarily come off the next bill's amount due, and the household would pay that much less. The run
instead collects the full amount and holds the household's money. Cash is overstated by the held
credits, and the closing credit is larger than it would be.

**I cannot yet say** whether the world or the bill is the right place to fix this. It could be the
payment truth paying "amount due" rather than the bill's charges, or the bill carrying a brought-forward
line. Practitioner check before building: do suppliers on a variable DD net a credit off the next
collection, and on a fixed DD hold it until the annual review?
