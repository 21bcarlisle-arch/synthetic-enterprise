# The renewal price now charges a clean prepayment household more than a clean direct-debit one

**Severity:** LATENT · **Lane:** B_commercial · **Epoch:** 3 · **Atom:** `unminted` · **Claim:** `the-company-default-belief-is-measured-against-its-own-ledger` (Lane 0 delivery)

**2026-10-03.** Found while wiring the company's book-learned default belief into the value rule.

## What is true at origin/main (`e69dbbfe5`)

`tests/company/pricing/test_the_price_rests_only_on_observables_a_supplier_may_use.py` is **red at
HEAD**. It fails on two tests, and neither is on `HEAD_RED_REGISTER.md`:

- `test_the_price_rests_only_on_declared_supplier_observables`: `decide_margin` prices against
  `billed_last_year_gbp`, `payment_method` and `unpaid_bills_by_age`, and none of them is declared.
- `test_payment_method_cannot_reach_the_price_at_all`: `value_based_renewal.py` mentions
  `payment_method`, `prepay` and `prepayment`.

Both came in with `e0370bf94` ("the renewal price reads payment history"). Its gate selected
controls by module stem and this file's name does not carry the stem, so the gate never ran it.
Reproduced in a clean worktree at `e69dbbfe5`: 2 failed, 4 passed.

**The control guards a director ruling.** Its docstring quotes it (2026-09-23): declining on payment
behaviour, credit position or arrears history is ordinary practice, but "shifting cost onto
prepayment customers, isn't". The control refuses that by construction: payment method may not reach
the price.

## The cost-shift, measured

`decide_margin`, value arm, 2,700 kWh, tenure 2 years, cost to serve GBP 60, standing charge GBP 99.
No unpaid bills, and a year's billing on the ledger. Only `payment_method` changes:

| current / base rate (GBP/MWh) | direct debit | standard credit | prepayment |
|---|---|---|---|
| 215 / 205 | 106.50 | 106.50 | **108.50** |
| 300 / 280 | 156.75 | 156.75 | **159.50** |

The cause is mechanical. A clean DD or standard-credit account reads its own non-payment share, which
is zero, and that replaces the segment prior. Prepayment has no published live provision row, so its
share cannot be read and the 2% segment prior stands. Two households with the same clean record are
priced GBP 2.00-2.75/MWh apart because of how they pay. That is the shift the ruling names.

## What this claim did about it

- `company/pricing/default_belief.py` learns the book's bad-debt charge **by arrears state only**,
  against a whole-book prior (2.0% of residential revenue, `docs/market_research/ASSUMPTIONS.md`). It
  has no payment-method argument. Method is used only to read each charge on its published provision
  row.
- Behind `DecisionPolicy.renewal_default_belief = "own_book"`, the price uses that rate in place of
  both the segment table and the persistence term. A clean prepayment household then pays what a clean
  DD one does. This is controlled by
  `test_on_the_book_rate_a_clean_prepayment_household_pays_what_a_clean_direct_debit_one_does`.
- The new parameter `default_belief_rate` also lands in the observables control's undeclared list.
  The argument for admitting it: it is a number the company computes from its own ledger about
  accounts in this arrears state, and the account's payment method cannot move it. The control file is
  NOT edited here. Editing it would make the landing gate run a file that is already red at HEAD, for
  reasons that are not this claim's.

## Not done, and why

The stock term (`receivable_provision_rates`) still picks its live row by payment method on either
switch setting. For a debtor, method still moves the price. Prepayment debt has no row, so it moves
the price down, not up. Making it method-free means a blended live row, which nobody has sourced. The
segment-table path also keeps the shift above. Both belong to `e0370bf94`'s owner and to the ruling's
owner. Recommendation, put to the director on NTFY: make `own_book` the default once the console
seat's probe has read it. That removes the shift for clean accounts. Then decide whether the stock
term may keep its per-method row. If it may, the control declares the three parameters with that
argument and turns green. If it may not, the stock term needs a method-free row.
