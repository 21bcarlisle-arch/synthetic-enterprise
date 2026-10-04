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

## Resolved, 2026-10-03 (delivery item `the-renewal-price-honours-the-prepayment-ruling-at-default`)

The director decided the open question above (`docs/direction/DIRECTION.yaml`): the stock term's
per-method row may stay, and the control asserts the PROPERTY that no clean account is priced higher
for how it pays, on both switch settings. Done:

- **The control asserts the property.** `test_a_clean_account_is_not_priced_for_how_it_pays` runs
  `decide_margin` over 4 rate cases x 3 consumptions x 2019/2022/2023 x both
  `renewal_default_belief` settings, outside a run AND inside a run whose book has taught the company
  that the channels shop differently. A second leg does the same with `learn_price_response` on, and
  a third shows a DEBTOR's price still moves with method, so the property cannot pass because method
  reaches nothing. The word ban is gone. `payment_method`, `unpaid_bills_by_age`,
  `billed_last_year_gbp`, `default_belief_rate` and `stayer_default_rate_gbp_per_mwh` are declared,
  each with its argument.
- **The segment-table shift is gone.** `observed_non_payment_provision_rate` returns 0 for a clean
  year before it looks up a row, so a clean prepayment account no longer falls to the 2% prior.
- **The gate selects the control** for `value_based_renewal.py`, `default_belief.py`,
  `discovered_price_sensitivity.py` and `enriched_churn_estimate.py` (`SUBJECT_TESTS`, not a rename).
- **The flip is MADE.** `DecisionPolicy.renewal_default_belief` defaults to `own_book`. Both release
  conditions hold on origin/main: the director's (B8, `4e17d1247`, landed) and the item's (the
  Grading section of `SEAT_PREREG_THE_CHOICE_IS_HELD_DOWN_BY_A_TOO_STEEP_BELIEF_..._2026-10-03.md`
  is filled in). **That prereg's next re-run (the world's debt-objection draw) must take its
  objection-off baseline at or after this commit.** Its graded figures at `c822e470e` priced on
  `segment_table` with the channel in the price, so a comparison against them has three variables.

### A second, larger channel into the price, found by the property

Prediction, written before the in-run measurement: on `own_book` the bad-debt shift vanishes, but
since `4e17d1247` passed `payment_method` into the price's churn belief, a clean prepayment household
would still price HIGHER on both settings, through PB7's learned engagement factor and B8's
per-channel slope. **It held, and was larger than the cost term.** In a run whose book had learned DD
engagement 1.54 and prepayment 0.35 (synthetic book, 2023 renewal, 215/180 uncapped, learning off), a
clean household was priced at margin GBP 48 (DD), 108.75 (standard credit) and 160 (prepayment) per
MWh. With learning on, B8's slope, learned only where a channel has closed renewals, priced clean DD
up to GBP 2.75/MWh below clean prepayment with the cap binding. Outside a run both channels read
neutral, which is why the original check missed it.

**Fixed.** The price now reads a channel-blind belief (`enriched_churn_estimate(channel_blind=True)`):
engagement at the book's own 1.0, and B8's slope pooled over every channel
(`discovered_price_sensitivity.EVERY_CHANNEL`). B8 still reaches the price. The control asserts that
learning moves some price on the grid. The churn desk's own belief keeps the channel: the ruling lets
the belief hear it and forbids only the price. All three mutations fire: per-channel slope, slope
dropped, and `4e17d1247`'s channel restored.

**What I cannot yet say:** how many real renewals the channel moved. The magnitudes above come from a
book built to differ by channel. The real book's learned engagement by method was not measured here.
The next full run on this commit prices every clean account channel-blind whatever the book learned.
