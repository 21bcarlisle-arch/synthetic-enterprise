# Who the own-book account-years with no method are

**Severity:** RECORDED · **Lane:** W2_customer_generator · **Epoch:** 3 · **Atom:** `PB8_a_households_payment_channel_changes_over_its_tenure` · **Claim:** `who-are-the-own-book-account-years-with-no-method` (Lane 0)

Picks up the loose end in `SEAT_FINDING_THE_OWN_BOOK_BELIEF_SHIFT_FROM_ASKING_GAS_LEGS_ON_GAS_2026-10-04.md`
(commit `96517e68c`): 4 account-years in its `|*` row (empty method under both registers), with 2 charged,
GBP 75.13 on GBP 4,148.40 billed.

## Premise, re-measured at draw

The duplicate claim the draw named is this draw's own write. It was claimed 25 s before this turn began,
with an empty `paths`, by the live `seat_executor --once` that spawned this turn. No rival is working it.

## What the code says, before any run

- `LiveSimInterface.get_payment_method` cannot return a falsy method. It returns the drawn channel
  (`payment_channel_for_customer(...).value`) or `PAY_ON_RECEIPT_METHOD`, and it RAISES on a missing id or
  a missing stop board. So the seam is not the source.
- `run_phase2b._book_method_of` returns `None` in exactly one place: `_SEGMENT_OF.get(cid, "resi") != "resi"`.
  For a resi id that is off the roster it raises. The non-resi ids in `_SEGMENT_OF` are four SME
  accounts: `C5`, `C6`, `C5_2`, `C6_2`.
- `LivePaymentTriad.default_belief_rate`'s docstring defines `None` as "an account the renewal price
  does not learn from". `observe_book` does the opposite. It turns `None` into `""`
  (`payment_method_of(...) or ""`) and keeps the year. The `""` year then enters the `*|<state>` cell,
  which `default_belief` reads. The `""` row is not read.
- `_provision` with `""` returns the final-bill provision once the account is closed, 0.0 with nothing
  unpaid, and `None` (unread) with money unpaid on an open account. That fits "2 of 4 charged, 3 closed".
- `default_belief` reads one arrears-state cell, with no pooling. The `|*` row's two charged years both
  sit in `unknown` (an account's first year). So no other cell's belief can move.

## Pre-registration (written before the measurement below was run)

- **P1.** All 4 account-years belong to the SME ids `C5`/`C6`/`C5_2`/`C6_2`. None is a resi account.
- **P2.** Dropping the accounts the register answers `None` for moves the per-call belief ONLY in the
  `unknown` state. `no_debt`, `in_arrears_steady` and `worsening` are bit-identical.
- **P3.** The `unknown` move is small, under 0.5 pp at every read: 8 reads, and the cell's prior weight
  is 1 account-year.

## Design

One process, one variable. A full decade at the current base under `VALUE_ARM_POLICY`, with
`LivePaymentTriad.default_belief_rate` wrapped. At each call it re-reads the real memo and computes
`default_belief` twice on the same observations: once as the run does, and once without every
account-year whose register answer was `None`. At run end it lists the `""` account-years by account.

## Result

Full decade, default seed, `VALUE_ARM_POLICY`, at `4c061bd21`, run 2026-10-04: 2,164 belief reads. The
wrapper's `recomputed` rate equals the run's `real` rate at all 2,164 reads, so the shadow reads the
run's own observations.

| account | year start | state | billed GBP | charge GBP | closed |
|---|---|---|---|---|---|
| ACC-C5 (SME) | 2016-01-14 | unknown | 1,911.51 | 0.00 | yes |
| ACC-C6 (SME) | 2016-04-14 | unknown | 2,236.89 | 75.13 | yes |
| ACC-C5_2 (SME) | 2016-12-14 | unknown | 2,070.23 | unread | no |
| ACC-C5_2 (SME) | 2017-12-14 | no_debt | 3,395.88 | unread | yes |

| state | reads | reads moved | belief without the `None` accounts minus as run |
|---|---|---|---|
| unknown | 8 | 4 | -0.177 pp at most (2017-07-01: 0.759% -> 0.582%), mean -0.051 pp |
| no_debt | 768 | 0 | 0 |
| in_arrears_steady | 1,336 | 0 | 0 |
| worsening | 52 | 0 | 0 |

## Graded

- **P1 holds.** All four years are SME (`C5`, `C6`, and `C5_2` twice). `C6_2` has no read year.
- **P2 holds.** Only `unknown` moves. The other three cells are bit-identical at every read.
- **P3 holds.** The largest move is 0.177 pp, inside the 0.5 pp bound.

**Correction to the item's WHY, beside it.** It says "2 of the 4 years carry a charge into the belief
(GBP 75 on GBP 4,148 billed)". The two READ years are C5 (charge GBP 0.00) and C6 (GBP 75.13), and
GBP 4,148.40 is the two of them billed together. Only C6 carries a non-zero charge. Both enter the
belief, and C5's GBP 1,911.51 at zero charge pulls the cell DOWN. The net effect of the pair is to
RAISE `unknown`, because C6's 3.4% outweighs it. Also, the `|no_debt` row reading "billed GBP 0" in
`tabulate` is an unread year: `tabulate` adds `billed` only for a read charge. That year billed GBP 3,395.88.

**Why the register returned nothing.** It did not fail. `run_phase2b._book_method_of` answers `None` for
a non-resi id ON PURPOSE. The run's own door (`LivePaymentTriad.default_belief_rate`) defines `None` as
"an account the renewal price does not learn from". The defect was in `observe_book`, which turned
`None` into `""` and kept the year. So SME final-bill outcomes were part of the resi renewal price's
`unknown` cell, and only resi renewals read that belief.

## Fixed

`observe_book` no longer reads an account-year whose register answer at the year's start is `None`.
Control: `test_an_account_the_register_does_not_answer_for_is_not_learned_from`. It runs the same book
with the account answered and unanswered, so a reader that dropped every account fails it. With the
`is None` clause reverted it goes red (checked).

What moves: only the value arm's price reads this belief. On it, the first-year (`unknown`) belief falls
by up to 0.18 pp at 4 renewals in the decade. A flat-arm run's figures do not move. **Not measured:**
the realised value-arm move. As in the parent finding, that is a two-run pair whose book diverges.

`/var/tmp/nomethod_measure.py` (not landed: a one-off wrapper). Smoke to 2017-12-31 first: 250 reads,
2 empty years (C5, C6), the 2017-07-01 move already visible.
