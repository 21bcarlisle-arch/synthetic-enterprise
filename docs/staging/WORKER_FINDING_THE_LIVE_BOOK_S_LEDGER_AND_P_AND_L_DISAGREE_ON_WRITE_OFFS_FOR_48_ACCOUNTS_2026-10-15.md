**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

# The live book's ledger and P&L disagree on write-offs for 48 accounts, and its control has been red since the publish

*Delivery seat, 2026-10-15, found while landing `no-run-or-publish-imports-code-that-is-not-its-stamp`.
The landing's import-derived test selection reached a control that every lane touching
`tools/run_output_store.py` will now meet.*

**Measured.** `tests/tools/test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py::test_the_ledger_and_the_pnl_write_off_agree_per_account`
reads the published `docs/reports/run_output_latest.json.gz`. That is
`run_output_2248e3baf_20261013T134447Z`, the run that every live figure comes from. The test is red at
`ed3dadd9d` (the publish itself), at `55701bb84^`, at `55701bb84` and at origin `6442d41af`, so this
is not a regression made since the publish. **48 accounts disagree.** In some the ledger has
written off money the P&L has not, e.g. `OCC-6387bf64272ag` with £13.12 against £0, and
`PROS-2017-0056g`. In others the P&L has a write-off the ledger lacks, e.g. `PROS-2016-0263` with
£0 against £215.97, `C6` with £0 against £33.71, and `PROS-2016-0117`.

**Why nobody saw it.** The control reads a generated artefact. The publish's own gate selects
tests by what the publish changed, and the run file is data, not an import, so the control never
ran at publish time. It runs only when a landing changes a module it imports.

**Open, ranked by evidence:**
- (a) The 2248e3baf run's book is the first one built by `81c129fe8`'s acquisition code (see
  `WORKER_FINDING_TWO_RUNS_AT_ONE_COMMIT_DRAW_DIFFERENT_BOOKS_FROM_FEBRUARY_2016_2026-10-15.md`). A
  bigger, different book may carry a case shape that the two write-off paths treat differently.
  The suffix `g` (a gas leg) appears on both sides.
- (b) Both sides are HEAD code over the same data, so the run's dirty bytes cannot be the cause
  directly. A shape the run wrote that HEAD's two readers disagree on can be.

**Next:** take one account from each side (`PROS-2016-0263` and `OCC-6387bf64272ag`) and print its
cases through `generate_billing_ledger` and `compute_emergent_bad_debt` side by side. The cause
split follows from what each one counts as written off.
