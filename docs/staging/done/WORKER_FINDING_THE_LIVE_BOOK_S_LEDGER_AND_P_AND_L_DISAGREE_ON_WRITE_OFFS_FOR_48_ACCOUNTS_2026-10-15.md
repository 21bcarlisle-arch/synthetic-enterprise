**Severity:** BLOCKING · **Lane:** D_billing_metering · **Epoch:** unassigned · **Atom:** `unminted`

**Fate (2026-10-15):** DONE -- three causes found and fixed; on the published book the ledger and the P&L now agree for every account (0 of 48, from 66 once the control used the run's own leaver set). The P&L write-off on that book falls from GBP 3,980.99 (81 accounts) to GBP 2,160.67 (43) at the next publish.

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


## Resolved (worker, 2026-10-15)

Printed side by side on `run_output_2248e3baf`. What each side counted as written off:

| Account | Ledger | P&L | Cause |
|---|---|---|---|
| `OCC-6387bf64272ag` | 13.12 | 0 (control's set) | **(1) The control's leaver set was stale.** It used `churned_billing_accounts`; the run's P&L caller (`run_phase4c_on_phase2b.py:336`) and the ledger use `households_whose_account_closed`, movers included, since 10-10. The ledger was right: a mover's balance is written off at close. Fixing the control's set moved 48 → 66, because the real P&L writes off more than the control was computing. |
| `PROS-2016-0263` | 0 | 215.97 | **(2) The ledger drew each bill's outcome again** and could not see the world's payment truth (`world_payment_truth.UNIFIED = True`). The truth said the 2023-03 bill failed; the ledger's draw said it was paid. |
| (same account) | | | **(3) The engine dropped a repayment.** The truth's settlement of that bill is dated 2023-04-11, three days before the engine opens the bill (due 04-14). It met an empty outstanding list and was discarded, so the P&L wrote off GBP 215.97 the household had paid. A settlement larger than the oldest bill lost its excess the same way (`PROS-2018-0222`: 10.91, `SYN-2016-222`: 4.07). |

**Fixed as classes:**
- `arrears_engine.resolved_settlement` returns each issued bill's resolved row beside the write-offs and
  credits. `generate_billing_ledger` takes outcome, method, lateness, part-payment and the amount asked
  of the named payer from it, so it no longer has an outcome draw of its own for any bill the engine
  collects.
- `balance_settlement_from_outcomes`: an unapplied repayment waits on the account as credit (SLC 27.16,
  the same rule credit bills follow), and every repayment applied to a case is recorded in
  `credits_applied` with `kind: "repayment"`. The ledger renders it as a new `ARREARS_REPAID` stage, which
  the account ledger books as a payment received. A credit only says where the credit went. Leg 4b's
  stayer provision reads the same map, so it now nets repayments too.
- The control uses the run's own leaver set.

**Controls:** `test_the_ledger_and_the_pnl_write_off_agree_on_the_real_book.py`, all 4 green on the
published book. New: `tests/simulation/test_balance_at_close_write_off.py::test_a_repayment_the_household_made_is_never_written_off`,
which covers the partition: on time, early, excess carried, short. The mutant that drops the excess
(`if left > 0` → `if False`) reds it on EARLY and EXCESS. Neighbouring suites: 233 passed.

**Not done, and where it went:**
- 695 bills are wholly the occupier's or the owner's (B7). The engine never asks the named payer for
  them, but the ledger still draws an outcome for them. They cannot be written off, so this control
  cannot see them. Filed:
  `WORKER_FINDING_THE_LEDGER_DRAWS_A_PAYERS_OUTCOME_ON_BILLS_THE_ENGINE_NEVER_ASKS_THEM_FOR_2026-10-15.md`.
- The two red statement controls (`WORKER_FINDING_TWO_STATEMENT_CONTROLS_ARE_RED_AT_ORIGIN_ON_THE_2248E3BAF_LEDGER_AND_NO_CENSUS_HOLDS_THEM_2026-10-15.md`)
  read the committed `docs/state/billing_ledger.json`, so this fix cannot reach them until the next
  publish. Their examples `PROS-2016-0207g` and `PROS-2022-0327` are among the accounts this fix moved.
  That is a lead, not a finding: I cannot yet say whether they go green.
