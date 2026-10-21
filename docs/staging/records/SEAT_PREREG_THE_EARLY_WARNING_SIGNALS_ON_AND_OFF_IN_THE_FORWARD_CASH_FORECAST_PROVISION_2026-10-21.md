**Severity:** RECORDED · **Lane:** E_finance_treasury · **Atom:** `E6_a_forward_cash_forecast_per_customer_charges_expected_loss_as_arrears_build` · **Direction item:** `e6-the-early-warning-signals-move-the-provision`

# Pre-registration: the early-warning signals on and off, in the forward-cash-forecast provision

**Graded 2026-10-21:** P1-P5 refuted, P6 held by construction. Predictions kept as written; result and causes in `docs/staging/SEAT_FINDING_THE_EARLY_WARNING_DOUBLES_THE_PROVISIONS_ERROR_BECAUSE_IT_LEARNS_THE_FAILED_MONTH_AS_THE_SIGNALS_OUTCOME_2026-10-21.md`.

Written 2026-10-21, before any arm exists. **Not launched**, as the item asks. The build is
`company/finance/cash_forecast_provision.py` (`signals_of`, default off). Its control is
`tests/company/finance/test_the_early_warning_signals_move_the_provision.py`. The knowledge is
`docs/market_research/bad_debt_provisioning.md`, "Early warning in the forward-cash-forecast
provision".

## The pair

- **One run, read twice.** No second run is needed: the switch is an argument to a reading, and
  the run's book is the same under both. `off` is `book_provision(book, as_of=d,
  payment_method_of=m)`. `on` adds `signals_of=lambda a, on: early_warning_signals(book.ledger(a),
  failures.get(a, []), as_of=on, payment_method_of=m)`.
- **Where the inputs come from.** The book is `LivePaymentTriad._consumer.ledger_book`, and the
  failures are that consumer's `_dd_failures`, the ARUDD lines as the company recorded them. The
  run does not persist those records. So the probe wraps
  `simulation.run_phase2b._company_provision_by_year_end` to capture the triad when the run ends
  (out of tree, as the 10-15 roll-rate grading did). The method register is the one the run hands
  to that function.
- **The run** is the default book and seed at the origin of the grading day, on the full window.
- **Read dates.** Every quarter-end, AND the 15th of every month. Both matter: see P1.
- **Graded against** each account's realised shortfall over the 12 months after the read date: the
  balance owed at the read date less the cash then received against it (FIFO), out to the write-off
  point. The company never sees it.

## Predictions

- **P1. At quarter-end reads the two arms are the same to within 1% of the book's provision, and
  per account identical on at least 99% of owing accounts.** The reason is mechanical. The world
  collects on the 28th, and a failed collection leaves its month unpaid. So at that month's end the
  account is in missed state 1, and a signal is read only in state 0. The chain already moved when
  the cash did not arrive, before the ARUDD line was seen. If P1 fails, the state-0 guard is not
  doing what the build says.
- **P2. At mid-month reads, an account with a code 0 or a missed manual payment provisions above
  the off arm on 100% of those whose cell is learned.** I cannot yet say how many there are, and I
  will not guess a count.
- **P3. `SIGNAL_CODE_0_AGAIN` is read on 0 accounts at every date.** The company does not re-present
  inside a month, so a second code 0 always follows a missed month.
- **P4. The on arm's book total is None at some early read dates.** That happens wherever an
  account holds a signal the book has not yet resolved (the GAP branch). Predicted: None at the
  first one to three mid-month dates after the first code 0 the run produces, then a number.
- **P5. Accuracy, on accounts whose signal was read:** the on arm's mean absolute error against the
  realised 12-month shortfall is below the off arm's. The direction is predicted; the size is not.
  If it is not below, the learned lift is fitting noise, and the result says so.
- **P6. The run's published figures do not move, on any arm.** The module has no production caller,
  and `company_provision` is the age-band stock. The control's off-arm test holds it in code. This
  prediction holds it on the run.

## What this pair cannot show

That the provision now moves **before the 91-day band**. That claim is about the run's published
stock, `company/pricing/default_belief.provision_stock`, which this pair does not switch. The
forecast engine already moves at the first missed month-end, with or without signals. Whether that
engine replaces the age bands in the run is a separate, later decision. Per the first slice's
choice 6 it is graded beside them, never switched.
