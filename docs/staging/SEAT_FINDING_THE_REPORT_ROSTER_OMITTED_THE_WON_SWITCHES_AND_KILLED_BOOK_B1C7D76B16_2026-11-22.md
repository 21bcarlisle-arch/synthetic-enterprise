**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

**Discharged:** `tests/saas/test_every_supplied_customer_reaches_the_report.py::test_one_record_from_every_book_survives_the_reducer`, `saas/customers.py` — one roster union, read by every reader in the report; the control fails with the production KeyError when a book is dropped

# The report's roster left out the won switches and killed book b1c7d76b16 (22 Nov 2026)

Delivery seat, item `the-book-reports-every-customer-it-supplies`.

## What happened

Book b1c7d76b16 died at 07:57:16Z on 22 Nov (sim-runner journal) with `KeyError 'SYN-2016-144_3'` at
`saas/cost_to_serve.py:246`. f80fe3951 put won switches on supply from `ACQUIRED_CUSTOMERS`.
`annual_report._build_clv_snapshots` (cost to serve) and `per_customer_lifetime` used a hand-written
roster that never named that book. This is the same class of failure that killed a run on OCC-* on
8 Oct, which was fixed for that one list only. The module held four unions and no two agreed: the CLV
snapshot and lifetime unions had no ACQUIRED, the segment map had all five books, and the I&C table
had no INCOMING_OCCUPANT.

## Fix (this landing)

`saas.customers.every_supplied_customer()` is now the only roster union. `get_customer` and all four
readers in `annual_report.py` read it. A new book is added in one place.

Control: `tests/saas/test_every_supplied_customer_reaches_the_report.py`. It finds every supply book
in `saas.customers` by name, so a sixth book is covered without editing the test, and it puts one
settled record per book through `extract_report_data`. Mutations, run here:
- dropping ACQUIRED from the function fails 2 of the 3 tests with `KeyError: 'T-ACQUIRED_CUSTOMERS'`
  at `cost_to_serve.py:246`, the production error;
- filtering the acquired account out of the CLV snapshot's roster fails 1 test with the same error.

## Not changed, on purpose

- `simulation/run_phase4c_on_phase2b._get_all_customers` reads the books through the supply-book seam
  (KNIFE). Its `CUSTOMERS` is phase2b's live population, which already includes the drawn trickle,
  so it is not missing a book. Importing a `saas` function into it would undo the seam.
- `annual_report.py` ~688 `acquisitions` counts founders by acquisition year plus won successors, and
  leaves out fresh-market wins. That is a question of what the figure means (is a won switch "an
  acquisition" in that table?), not a roster KeyError. Filed here as an open question; it does not
  block the book.
- ~858 `by_billing_account` iterates founders only. That is the same question for the CLV-by-account
  table.

## Environment note (not a code defect)

Three tests in `tests/saas/reporting` fail identically on HEAD in the executor worktree with
`LedgerFormsDisagree`. A plain `docs/state/billing_ledger.json`, written from `/var/tmp/w14/run.json`,
shadows the committed `.gz`. It is untracked and left in place.

## Pre-registration: the short probe (written before it ran)

`tools/run_annual_report --fast --end-year 2017`, outputs to /tmp, at this change:
- Q1. The run gets through `extract_report_data` without a KeyError. Refuted by any KeyError in a
  reader of the roster.
- Q2. Every id in the run's `acquired_customers` that has a settled record appears in
  `per_customer_lifetime`. Refuted by any settled won id missing.
- Q3. At least one acquired id (SYN-2016-144_3 on the 21 Nov probe) settles before the end of 2017,
  so the probe actually exercises the defect. If none does, the probe is vacuous and is reported as
  such.

## Probe result (22 Nov, 12:22Z, at this change, fast mode, 2016-2017)

- Q1 **held.** `extract_report_data` completed and wrote report_data.json. The run then died in
  `generate_annual_report` (`_section_population_anchoring`) on this worktree's stray plain ledger
  (`LedgerFormsDisagree`, see the environment note). That is downstream of the reducer and not this
  defect. sim-runner's book worktree carries only the `.gz`.
- Q2 **held.** 3 won switches were registered. 1 was supplied and settled, and it is in
  `per_customer_lifetime`. The other 2 are in `won_switches_not_supplied` (gas-only households),
  as f80fe3951 intends.
- Q3 **held, so the probe is not vacuous.** SYN-2016-144_3, the id that killed b1c7d76b16, settled
  with £522.78 of lifetime revenue and resolved in the CLV snapshot's cost-to-serve roster.
