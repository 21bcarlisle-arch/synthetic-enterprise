# The own-book belief shift from asking gas legs on gas, measured

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure` · **Claim:** `measure-the-own-book-belief-shift-from-asking-gas-legs-on-gas` (Lane 0)

Grades the prediction filed in `SEAT_FINDING_THE_OWN_BOOK_METHOD_REGISTER_ASKS_EACH_ACCOUNTS_OWN_FUEL_2026-10-04.md`
(commit `e5a85c3c2`, parent `316cacc0a`).

## Premise, re-measured at draw

Both cited commits are on origin; the measurement they ask for was never run. The duplicate claim the
draw named is this draw's own write (claimed 03:45:10, one `claude -p` live, no rival `surgical_land`).

**Correction to the parent finding, beside its claim.** It says "the default policy never reads the
register, so no default-run number moves". `DecisionPolicy.renewal_default_belief` has DEFAULTED to
`own_book` since 2026-10-03, so `CURRENT_POLICY` inherits it and every run calls
`default_belief_rate` with the register at each priced resi renewal. What stays true: only the value
arm's price reads the rate (`renewal_rate_chain` passes it to `decide_margin`), so a flat-arm run's
money figures do not move.

## Design (decided before any run)

ONE process, not two runs. The two commits differ only in which fuel `_book_method_of` asks; a two-run
pair under the value arm would also diverge downstream (the belief prices, so the book itself moves),
and the belief shift could not be told from the book shift. So: one full-decade run at `e5a85c3c2`
under `VALUE_ARM_POLICY`, with `LivePaymentTriad.default_belief_rate` wrapped so that at every call it
also reads the SAME ledger through a shadow register that asks `"electricity"` of every resi account
(the parent's behaviour), on its own memo. Both readings see the same book on the same date; the only
variable is the fuel asked. Reported: `default_belief.tabulate` per method row and per arrears state,
for both registers at run end, and the per-call belief difference across every renewal.

## Prediction (written before the run)

- P1. Some account-years move from the `direct_debit` row to the `standard_credit` row, all of them
  gas legs; the two rows' counts move by the same number in opposite directions. Size: tens at most.
- P2 (the parent finding's). The DD row's charge share falls slightly and the pay-on-receipt row's
  rises, because the movers are stopped DDs, i.e. accounts already failing to pay.
- P3. The per-state belief rises where it moves (a stopped leg's provision is read on the higher
  pay-on-receipt row), concentrated in `in_arrears_steady`/`worsening`; `no_debt` near unchanged.
  Size: under 0.5 percentage point in any state at any renewal.

## Result

Full decade, default seed, `VALUE_ARM_POLICY`, at `75c7d7b5f` (contains `e5a85c3c2`), run 2026-10-04 in
the seat worktree: 2,164 belief reads, 667 resolved account-years under each register.

**Which account-years move.** 48 account-years on 19 accounts, every one a gas leg (18 `...g` legs and
the gas-only household `SYN-2016-021`). They move in SIX directions, not one:

| electricity-pinned -> own fuel | account-years |
|---|---|
| prepayment -> direct_debit | 13 |
| standard_credit -> direct_debit | 13 |
| direct_debit -> prepayment | 11 |
| direct_debit -> standard_credit | 5 |
| prepayment -> standard_credit | 5 |
| standard_credit -> prepayment | 1 |

34 of the 48 change their charge. Only 5 are the DD -> pay-on-receipt move the prediction was about.

**The method rows** (charge per GBP billed, account-years):

| row | electricity-pinned | own fuel |
|---|---|---|
| direct_debit | 1.142% (461) | 1.056% (471) |
| standard_credit (pay on receipt) | 3.011% (133) | 3.242% (129) |
| prepayment (no live row; years unread) | 64 of 69 unread | 58 of 63 unread |
| whole book | 1.546% | 1.504% |

**The belief the price reads** (per arrears state, own fuel minus electricity-pinned, across every read):

| state | reads | mean | range | last read, pinned -> own |
|---|---|---|---|---|
| no_debt | 768 | -0.05 pp | -0.21 to 0 | 0.64% -> 0.61% |
| in_arrears_steady | 1,336 | +0.02 pp | 0 to +0.08 | 1.49% -> 1.50% |
| worsening | 52 | -0.43 pp | -1.10 to 0 | 3.85% -> 3.60% |
| unknown | 8 | +0.00 pp | -0.01 to +0.01 | 0.98% -> 0.99% |

## Graded

- **P1 refuted.** The movers are gas legs, as predicted, but the mechanism was wrong. The pinned
  register did not just miss gas DD stops. It gave every gas leg its ELECTRICITY leg's drawn channel,
  and the two legs of one household are drawn separately. So most of the correction is channel
  mismatch (DD vs prepayment vs standard credit at set-up), not stops. The DD row GAINED 10
  account-years net; I predicted it would lose them.
- **P2 holds on sign, for a different reason.** The DD row's share falls (1.142% -> 1.056%) and the
  pay-on-receipt row's rises (3.011% -> 3.242%). The DD row falls because the gas legs it gains are
  mostly clean, not because stopped debtors leave it.
- **P3 refuted on sign and on size.** The belief FALLS where it moves most: `worsening` by up to
  1.10 pp (mean -0.43), above the 0.5 pp bound I set. `no_debt` also falls slightly. Only
  `in_arrears_steady` rises, by at most 0.08 pp. Six prepayment-pinned years that were unread now
  read a charge, which also moves the cells.

**What this means for the price.** On the value arm, a worsening account was being charged about
0.25-1.1 pp too much bad debt on next year's bill. The cause was gas legs read on the wrong channel.
This is a belief correction on a fixed book. **Not measured:** how far the value arm's realised
renewals and money move once it prices on the corrected belief. That needs a two-run pair, and in
that pair the book itself diverges, so it carries two variables.

**A loose end, not chased.** Four account-years carry an empty method under both registers (the
`|*` row in `tabulate`), so the register returned nothing for an account the learner read. Who they
are was not established.

## How it was measured

`/var/tmp/ownbook_gas/measure.py` (not landed: it is a one-off wrapper). It wraps
`LivePaymentTriad.default_belief_rate`. Each call returns the real reading, and the same
`consumer.ledger_book` is also read through `observe_book` with a shadow `payment_method_of`, on its
own memo. The shadow returns `None` wherever the real register does, and otherwise asks
`LiveSimInterface().get_payment_method(cid, "electricity", as_of=on)`. At run end it applies
`default_belief.tabulate` to both memos. Smoke run to 2017-12-31 first: 250 reads, 5 movers.
