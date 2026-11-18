**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 4 · **Atom:** `unminted`
**Knowledge:** `payments-and-direct-debit` -- `docs/market_research/payments_and_direct_debit_2026-10-25.md` "What a level direct debit must be"

# A level instalment returned in a scheme-credit month (2026-11-18)

**Question.** A bill the EBSS credit met whole is `outcome == "credit"` in the non-credit branch of
`tools/generate_billing_ledger.py` (class L'). A level collection returned in that month prints no row
(`tests/tools/test_a_scheme_credit_month_keeps_its_level_collection.py` pins it). The credit-bill sibling
(2a8a99235) showed a returned instalment is owed by the schedule, not by the month's bill, and the desk opened on
it. Does the same hold here?

**What is counted.** On `docs/reports/run_output_8a300fa561_20261116T031305Z.json`, with the ledger generator at
origin/main 2913ddd895: every bill row the engine resolved `outcome == "credit"` on a positive bill (the scheme
credit met it whole) whose `collection_result` is not `success` and which popped a level schedule slot. For each:
whether `collections_journeys` carries a stage with an `overdue_gbp` figure on the billing account on any day from
the collection day to 5 days after it; and the desk figure on the missed day (`collection_date + 1`, the key the
credit-bill fix reads).

## Pre-registration (filed before the count is run)

- **Prediction:** few returned rows (0 to 10 legs), since the scheme-credit months are Oct 2022 to Mar 2023 only
  and a bill met whole by a 66-67 credit is a low-use month. Of those, the desk opens on at least one, since the
  schedule, not the bill, is what the desk measures, so a household already in debit is short by the instalment.
- **Refuted if** there are returned rows and the desk opens on none: then the scheme-credit branch's "no row, no
  case" is right as it stands for this book, and only the row itself (money not crossing) is a page question.
- **If the desk opens on any:** fix it the credit-bill way (failed level row, case via `level_missed_on`,
  repayment by `settles_month`), and re-pin the test.

## Result (2026-11-18, run after the pre-registration above)

Instrument: `generate` at 2913ddd895 with `_resolved_settlement` wrapped to keep its rows, over the 8a300fa561 run
(probe kept out of the repo; one minute to run).

- Positive bills the scheme credit met whole: **244**. `collection_result`: 243 `success`, **1 `failed`**.
- The one: `OCC-f6813bf9f05e`, electricity, bill 2023-02-28 (61.38, all of it met by the scheme credit), level
  instalment 49.79 due 2023-02-01, returned.
- Desk: **no stage with a figure on that account from 1 to 6 Feb 2023, and no collections journey on the account at
  any point in the run.** No figure on the missed day (2 Feb) either.
- Balance before: on the page's own figures, paid 2,277.44 against 2,257.98 asked net of scheme credit before
  1 Feb 2023, so the leg was **in credit by about 19.46**. The desk's figure is the schedule shortfall capped at the
  debit balance (`arrears_engine.level_shortfall`), so a leg in credit has no figure to open on.

**The prediction is refuted.** "The desk opens on at least one" was wrong: there is one return, it is on a leg in
credit, and the desk opens nothing. On this book the scheme-credit branch's "no row, no case" drops no debt, and
`test_a_scheme_credit_month_keeps_its_level_collection.py` stays as it is. Nothing is built.

**What this does not establish.** One leg on one book. The premise of the credit-bill fix (owed by the schedule, not
by the bill) still holds here in principle: a scheme-credit-month return on a leg already in debit WOULD have a desk
figure, and this branch would drop it as the credit-bill branch did before 2a8a99235. This book has no such leg, so
the branch is untested against one. The two branches now also differ on the row itself: a credit-bill month prints
the returned instalment as a failed level row, a scheme-credit month prints nothing. Neither drops money (nothing
crossed), so it is a statement-presentation difference, not a balance defect. Re-measure on the next book that has
a scheme-credit-month return on a leg in debit; the probe above is the instrument.
