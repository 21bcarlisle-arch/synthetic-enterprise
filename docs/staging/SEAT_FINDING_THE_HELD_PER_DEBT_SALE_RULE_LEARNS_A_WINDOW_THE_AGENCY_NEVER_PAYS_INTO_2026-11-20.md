**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# The held per-debt sale rule learns from a window the agency never pays into, so on the varying world it sells debts worth 12.2p at 5.4p (2026-11-20)

Drawn item: `knife3-the-held-per-debt-sale-rule-lands-on-the-varying-world`. Branch
`knife3-per-debt-sale` (9fcd4a53fa) is now on origin under that name. The world change it waited for
(f696fca4eb: recovery after write-off varies with the bill's age at close) is on origin.

## Pre-registration (written 03:35Z, before any replay ran; verbatim)

```
KNIFE3 per-debt sale on the varying world -- pre-registration, written 2026-11-20 before any replay ran.
Book: docs/reports/run_output_67d454905c_20261119T184502Z.json, world at origin f696fca4eb, company
pieces from knife3-per-debt-sale 9fcd4a53fa.

Derived from constants only, not from outcomes: the world writes a close-leg debt off at final bill
+365 d (CLOSED_ACCOUNT_WRITE_OFF_AFTER_FINAL_BILL_DAYS), places it at +30 (DCA_PLACEMENT_DAYS) and the
agency remits at +180 (DCA_OUTCOME_DAYS): final bill +575 d. cash_forecast_provision.learn() counts
post-close cash in (last bill, last bill +365] (POST_CLOSE_RECOVERY_DAYS).

P1. 0 of the close-leg RECOVERED stages fall within 365 days of the debt's final_bill_on; every gap
    is 575 days.
P2. So, with the remittance posted to the company's book as cash on its own date, the learned
    cells carry NONE of the world's age gradient: an aged debt (>365 d overdue at close) and a young
    one in the same PostCloseCell get the same expected recovery, and the cells' spread, if any, is
    customer cash before write-off. Predicted: every cell's observed share is below 0.02, so every
    per-debt figure falls below the prior 0.122, towards the cell mean.
P3. Hence, at 0.054, 0.07 and 0.093, the rule SELLS nearly every close-leg debt (predicted > 90% of
    them by GBP), which contradicts the world, where working recovers 0.122 (young) or 0.063 (aged)
    per GBP and both beat 0.054. The per-debt rule as built would sell young debts at a loss.
P4 (control, window widened to 600 d in the replay only): the remittance then enters, and only cell
    (3, True) holds aged debts, so it alone falls below the others. Its figure lies in (0.063, 0.122),
    the other cells are about 0.122, and nothing is sold at 0.054 or 0.07.
Landing rule (from the direction): land the per-debt rule only if the cells spread with the world
AND both sell and work are reached at a published price. If P2/P3 hold, it does not land: only the
sensitive exclusion lands, and the window mismatch is filed as the reason.
```

## The replay (book 67d454905c, world f696fca4eb, company pieces from 9fcd4a53fa)

The company's book was rebuilt from `tools/generate_billing_ledger.generate` output:
- bills as BILL_DEBIT, with credit bills as ADJUSTMENT_CREDIT;
- successful payments as PAYMENT_CREDIT;
- the agency's RECOVERED amount as PAYMENT_CREDIT on its own date.

Then `learn(as_of=2025-07-04)` ran. Script: `/var/tmp/k3land/replay_kept.py` (machine-local).

| | window 365 (as built) | window 600 (replay only) |
|---|---|---|
| remittances inside the window | 0 of 215 (every gap is 570-599 d) | 0 of 215 in 365 d; all inside 600 d |
| cell (0, False) / (0, True) | 0.916 / 0.352 | 0.922 / 0.374 |
| cell (1, True) / (2, True) | 0.265 / 0.139 | 0.271 / 0.142 |
| cell (3, True), 149 placed debts (118 young, 31 aged) | 0.033 | 0.084 |
| SELL at 0.054 / 0.070 / 0.093 | 149 / 149 / 149 (GBP 5,991.86) | 0 / 0 / 149 |
| WORK at the same prices | 66 (GBP 2,194.95) each | 215 / 215 / 66 |

In every cell, aged and young debts get the same figure. For example, cell (0, True) holds 26 young
and 15 aged debts, and all 41 get 0.352.

## Grading

- **P1 HELD.** 0 of 215 remittances fall within 365 days of the last bill.
- **P2 WRONG in its number, right in its conclusion.** I predicted every cell would read below 0.02.
  They read 0.03 to 0.92. The cells spread, but on customer cash against the whole closing
  balance, and most of that balance is paid before write-off (582 closes, 215 written off). The
  world's age gradient reaches no cell. I had not thought about the denominator: the rule applies a
  figure learned on the whole closing balance to the written-off remainder, which is exactly the
  part the customer did not pay.
- **P3 HELD in kind, wrong in size.** I predicted over 90% of GBP sold. It was 73% (149 debts, all in
  (3, True)). The other 66 are worked only because their cell figures (0.14-0.92) are inflated by
  customer cash. They are right by accident.
- **P4 HALF HELD.** (3, True) read 0.084, inside (0.063, 0.122). Nothing sold at 0.054 or 0.070. But
  the other cells did not sit near 0.122, which is the denominator fault again.

## Disposition

The landing rule: the cells must spread *with the world*, and both sell and work must be reached.
They spread, but not with the world, so **the per-debt rule does not land.** Only the
sensitive-circumstances exclusion lands, at the rule and at the door, with mutation-checked tests.
No world caller passes `sensitive` yet: the company's PSR is not in reach of the post-run recovery
stage. Today the exclusion is reached by tests only.

**A successor needs three definitional fixes, not tuning:**
1. learn on the written-off remainder and the agency's remittance, not on the whole closing balance
   and customer cash;
2. use a window that covers write-off, placement and outcome (575 days in this world);
3. cut by the oldest unpaid bill's age at close (Energy UK's published cut, read off the company's
   own `fifo_unpaid_bills`), not by consecutive months unpaid, which caps at 3.

A further point: the company's book does not receive the agency's remittance as cash today.
`generate_payment_ledger_data` shows it as an informational `recovery_note`. So in-run, no
estimator could learn it until that remittance crosses as a ledger event.

Knowledge: `docs/market_research/debt_and_collections.md` s.7.7, "The held per-debt rule, replayed
on the varying world".

## Successor pre-registration (written before the successor's replay ran; verbatim)

```
KNIFE3 successor, pre-registered 2026-11-20 before any replay of it ran. Same book (67d454905c), world
f696fca4eb. Company change: learn() reads each written-off account's recovery as cash received AFTER
its WRITE_OFF_CREDIT over the written-off amount (not customer cash over the closing balance); an
account is resolved once write-off + the book's own observed write-off-to-remittance lag has passed
(the lag is learned off the book, not read from a world constant); and the cell is the oldest unpaid
bill's age at the last bill, over or under 12 months past due (Energy UK Fig. 5's published cut),
read off the company's own fifo_unpaid_bills. The replay posts the write-off as WRITE_OFF_CREDIT on
the world's WRITTEN_OFF date and the agency's RECOVERED amount as cash on its own date.

S1. The learned lag is one value near 210 d (write-off +30 placement +180 outcome), in [200, 240].
S2. The aged cell (over 12 months past due at close) reads in [0.04, 0.09], centre 0.063; the young
    cell reads in [0.10, 0.15], centre 0.122. Aged < young in every case.
S3. The direction's text says "so nothing sells at 5.4p or 7p". My own arithmetic disagrees at 7p: an
    aged debt expected at 0.063 is SOLD at 0.070 (0.070 > 0.063). Predicted: at 0.054 SELL 0 and WORK
    all; at 0.070 and 0.093 SELL every aged debt and WORK every young one. If the aged cell reads
    above 0.070, 7p sells nothing and the direction's line holds.
Landing rule (direction): land only if aged and young separate in the learned cells AND both SELL and
WORK are reached at a published price (0.054 / 0.070 / 0.093). If either fails, land nothing more
and record why here.
```

S4 (pre-registered after S1-S3 were read, before this run): the S1-S3 replay learns at 2025-07-04 and
decides on the same debts, so it is in-sample. Out of sample: learn at as_of 2022-06-30, then decide only
the debts written off after that date. Predicted: the aged cell, if it has resolved at least 5 debts by
then, reads below 0.070 and the young cell above 0.093; at 0.070 every later aged debt is sold and every
later young one worked. If the aged cell has fewer than 5, it sits near the book-wide figure and 0.070
sells nothing.

## The successor's replay, graded

Script: `/var/tmp/k3succ/replay_succ.py` (machine-local; it is `replay_kept.py` plus the write-off
posted as `WRITE_OFF_CREDIT` with its bill's `invoice_ref`, and the remittance earmarked to that
bill), and `/var/tmp/k3succ/oos.py`. Print: `/var/tmp/k3succ/replay.log`.

```
as_of 2025-07-04 learned lag 210 book-wide 0.1117 resolved write-offs 198 GBP 7346.01 recovered 820.2
  cell (False,) n 154 written off 6047.44 got 737.82 observed 0.122 learned 0.1219
  cell (True,) n 44 written off 1298.57 got 82.38 observed 0.0634 learned 0.0645
price 0.054: SELL 0 GBP 0.00 (aged 0) | WORK 215 GBP 8186.81
price 0.07: SELL 54 GBP 1739.50 (aged 54) | WORK 161 GBP 6447.31
price 0.093: SELL 54 GBP 1739.50 (aged 54) | WORK 161 GBP 6447.31
OOS learn at 2022-06-30 lag 210 resolved 181 {(False,): (143, 0.122, 0.1219), (True,): (38, 0.0634, 0.0647)}
price 0.07: later debts 33 SELL 16 (aged 16 of 16) WORK 17
```

- **S1 HELD.** The lag is 210 days.
- **S2 HELD.** Aged 0.0645, young 0.1219. Both sit near their centres.
- **S3 HELD, and the direction's line "nothing sells at 7p" was WRONG.** 0.070 is above 0.0645, so
  every aged debt sells at 7p. Only 5.4p sells nothing.
- **S4 HELD.**

**A correction to the pre-registration's design, made after its first run and kept here.** My first
build cut each ACCOUNT by its oldest FIFO-unpaid bill. That build read young 0.1137 and aged
0.1118, and sold nothing at any price, so it failed the landing rule. There were two reasons:
- FIFO credits payments to the oldest bill. The world's (and the company's) collections case is
  per invoice, and the unpaid invoice is often the old one.
- 7 of 73 accounts hold both aged and young write-offs.

The build that landed makes one debt per written-off bill, using the ledger's existing
`invoice_ref` and `remittance` fields. The pre-registered S1-S4 numbers were written for that
design's intent: the cells separating aged from young. They were not refitted.

**Disposition: the per-debt rule lands.** The cells separate aged from young, and both SELL and
WORK are reached at 0.070 and at 0.093, both published prices. Ten tests guard it. Each
deliberately injected defect (a "mutation") made at least one test fail: earmark, cut, per-cell
figure, lag, cash before write-off, and cap. In-run the learner still resolves nothing, because the
agency's remittance is not posted to the company's book. That is the next item.

## In-run successor: pre-registration (written 2026-11-20 08:23Z, before any in-run code changed; verbatim)

Drawn item `knife3-agency-remittance-reaches-the-company-book`. What was read at origin 37f9ff6ebf
before building:

- Neither of the company's closed-account write-offs carries `invoice_ref`. The month-end sweep
  (`arrears_engine.closed_balance_write_offs`, run by `LivePaymentTriad.write_off_closed_balances`)
  and the desk's (`PaymentObservationConsumer._post_desk_write_off`) each post ONE balance-level
  `WRITE_OFF_CREDIT` per account. `cash_forecast_provision._written_off` drops a write-off with no
  `invoice_ref`, so in-run the learner sees no debt at all, before any question of remittance.
- The live triad has no agency leg. `_post_writeoff_stages` (PLACED_WITH_DCA, RECOVERED) exists only
  in the engine's post-run cascade, read by `generate_payment_ledger_data` as a `recovery_note`.

The build, in two increments:
1. The company writes a closed account off one invoice at a time: one `WRITE_OFF_CREDIT` per unpaid
   invoice, carrying its `invoice_ref`, sized by the ledger's own remittance-else-oldest-first
   allocation. Any remainder the allocation cannot place on an invoice is written off with no ref.
   The total and the date do not change.
2. The world's agency works each written-off invoice it is given. It remits what it recovers
   (`dca_recovered_amount` on the bill's own age at close) to the company as a `RemittanceAdvice` on
   placement + outcome (write-off + 210 d), with `bank_reference` set to the invoice's ref, through
   the consumer's ordinary remittance path. The company posts it as a `PAYMENT_CREDIT` earmarked to
   that bill. A remittance dated after the run's end does not cross.

Predictions:

- I0 (after increment 1 alone): an in-run `learn()` still resolves 0 written-off debts (no cash
  after a write-off, so no lag, so `_learn_written_off` returns early), and every sale decision
  stays at the 0.122 prior. The total written off and every write-off date are unchanged to the
  penny on the same ledger.
- I1 (on the next book after both increments): at least 95% of the GBP written off in-run carries an
  `invoice_ref`.
- I2: the learned lag is one value in [200, 240] days, centre 210.
- I3: the aged cell (more than 12 months past due at close) reads in [0.04, 0.09], centre 0.063. The
  young cell reads in [0.10, 0.15], centre 0.122. Aged reads below young.
- I4: at 0.054 nothing is sold. At 0.070 and 0.093, every aged debt is sold and every young one is
  worked.
- I5 (risk named in advance): the company's cell is its own bill date against its last bill. The
  world's age is its own bill's age at close. Where the company's allocation puts the unpaid
  remainder on a different invoice from the one the world left unpaid, the remittance lands on the
  invoice the world names. If the company wrote off no invoice with that ref, the cash posts as an
  ordinary payment and the learner does not see it. Predicted: under 5% of remitted GBP is lost this
  way. If more is lost, I3's cells blur towards the book-wide figure, and that disagreement is the
  finding.

## In-run successor: both increments landed (2026-11-20); grading waits for the next book

- Increment 1, 4ea473bf18: one write-off per open invoice, under its ref (six mutations fire).
- Increment 2, this commit: `LivePaymentTriad._agency_remits` places each closed-account write-off the
  company posted with an invoice the world raised, and runs the world's one cascade
  (`_post_writeoff_stages`) on that bill's own age at close. It then crosses the terminal stage's cash
  as a `RemittanceAdvice` quoting the invoice ref, through the consumer's ordinary wire path, so it
  posts as a `PAYMENT_CREDIT` earmarked to the bill. A remittance dated after the run's end does not
  cross. A statute-barred write-off is not placed. Six mutations fire. Tests:
  `tests/background/test_the_agencys_remittance_reaches_the_company_book.py`.
- What the world reads to place a debt: the company's own write-off on its ledger. That is the
  company's placement instruction, the one thing a real agency is told. The age and the recovery are
  the world's own.

I0 cannot be read separately now: increment 2 landed on top of increment 1 before any book was made.
Said here rather than graded.

One more prediction, written before any run (I6): the published bad-debt charge moves. The run's
provision stocks are read after `write_off_closed_balances`, so `recovered_to_date_gbp`, which the
IFRS 9 charge subtracts (`test_the_ifrs9_basis_subtracts_recoveries`), now carries the agency's cash.
Predicted: on the next book, recovered-to-date at the run's end is 8% to 12% of written-off-to-date.
That is below the 0.112 book-wide share because the remittances of the last 210 days have not
arrived. On a book where it read 0 before, the IFRS 9 charge falls by that amount.

**Owed:** grade I1 to I6 on the first book made at or after this commit. That is a box run, queued
behind the census. Nothing more is owed in code for this item.

## Re-drawn 2026-11-20 ~11:00Z: premise spent

The item `knife3-agency-remittance-reaches-the-company-book` was drawn again after both increments
had landed (4ea473bf18: one write-off per invoice, each with its `invoice_ref`; 7d99949ce7: the
agency's remittance crosses as cash on its own date, earmarked to that bill). The pre-registration
above (I1 to I6) is already written. Nothing more is owed in code, so this draw takes the
premise-spent disposition. Grading I1 to I6 is handed on as
`grade-knife3-in-run-i1-to-i6-on-the-first-book-after-7d99949ce7`.

## I1 to I6, graded on book 6a588a832f (2026-11-20 16:40Z; the predictions above are unrevised)

Book: `docs/reports/run_output_6a588a832f_20261120T134224Z.json`. 6a588a832f descends from 7d99949ce7 and
4ea473bf18 (checked with `git merge-base --is-ancestor`). The prior book is 67d454905c, made before either increment.

**What this book can show.** The run output publishes the company's provision stocks
(`company_provision`, with written-off and recovered to date) and its collections journeys. It does NOT
publish the company's ledger events, so it has no `WRITE_OFF_CREDIT` refs. It does not publish
`LivePaymentTriad.agency_remittances`, and it has no in-run `learn()` result: no lag, no cells and no sale
decisions. So five of the six lines cannot be read from this book. They are not graded, and are not counted as held.

- **I1 (>= 95% of GBP written off carries an `invoice_ref`): CANNOT TELL on this book.** No write-off event is
  published. Indirect evidence only: agency cash crossed (I6), and `_agency_remits` places only a write-off
  whose ref the world billed, so at least some write-offs carry refs. That does not give a share.
- **I2 (learned lag in [200, 240], centre 210): CANNOT TELL.** No in-run `learn()` is published.
- **I3 (aged cell in [0.04, 0.09], young in [0.10, 0.15], aged < young): CANNOT TELL.** For the same reason.
- **I4 (nothing sold at 0.054; at 0.070 and 0.093 aged sold, young worked): CANNOT TELL.** No sale decision
  is taken or published in-run.
- **I5 (< 5% of remitted GBP lost to a ref the company did not write off): CANNOT TELL.**
  `agency_remittances` is not published, so remitted GBP cannot be set against posted recoveries.
- **I6 (recovered to date at the run's end is 8% to 12% of written off to date): HELD.** It reads GBP 2,331.31
  of GBP 20,184.95, which is 11.55%. On 67d454905c it read GBP 0.00 of GBP 21,327.72. The reader
  (`arrears_engine.written_off_and_recovered`) counts any cash recorded after a write-off. It read zero
  before, so the GBP 2,331.31 is the agency's remittance crossing, not cash from reopened accounts. By year
  end, the recovered share rises from 3.7% (2018) to 7.9% (2019) and 8.3% (2020), then 11.6% (2021). After
  that it sits between 10.6% and 11.6%. That fits a 210-day lag behind write-offs that are front-loaded.
  The second half of I6, "the IFRS 9 charge falls by that amount", is not graded separately. It follows
  from the charge's formula (written off less recovered). On the published figure,
  `provisioned_bad_debt_gbp` moved from 135,695.28 to 134,343.87 (-1,351.41). But the two books also
  differ in what was written off (GBP 1,142.77 less), so I cannot attribute that move to the remittance.

**Tally:** 1 held, 0 missed, 5 not readable on this book. The in-run per-debt learner is not yet shown to
learn the world's age gradient. What is shown is that the agency's cash now reaches the company's book.

**What would let I1 to I5 be graded:** the run publishes, at its end, (a) each company write-off's GBP
and whether it carries a ref, (b) `agency_remittances` as rows, and (c) the company's own
`cash_forecast_provision.learn(as_of=end)` reading: remittance lag, cell figures, and
`sells_written_off_debt` at 0.054 / 0.070 / 0.093 per written-off debt. All of these are the company's own
records. None is world truth. That is a small reporting build plus one book. The continuation
`grade-knife3-in-run-i1-to-i6-on-the-first-book-after-7d99949ce7` is recorded premise-spent against this
grade, because the first such book has come and been read as far as it can be. The unread five carry
forward under this build, not under that id.
