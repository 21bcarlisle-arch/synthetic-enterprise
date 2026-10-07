# H50 L2: every test after an in-process run reads the drawn book

*Worker, 2026-10-07. Continues `WORKER_RESULT_H50_A_SECOND_RUN_STARTS_FROM_THE_DRAWN_BOOK_AND_THE_LEFTOVER_MOVED_NO_SETTLED_FIGURE_2026-10-07.md` §4.*

## What was asked, and what was built instead

§4 asked for `start_from_the_drawn_book()` in the teardown of four named test files. A re-census
(grep for `run_phase2b` imported under any alias, then `.main(`) finds about twenty files that call
`main` in-process, and three run it in module-scoped fixtures. Editing each one fixes today's list
and leaves the next caller to repeat H40.

So the reset is one autouse teardown in `tests/conftest.py` (`_phase2b_book_is_put_back`). It runs
after every test, and only if `simulation.run_phase2b` is already imported. One call costs about
10 µs (measured: 1,000 calls in 10.6 ms over 261 electricity records), so roughly 0.4 s across
the suite. A module fixture that runs `main` keeps its result dict. Only module-level book state
goes back, and no test reads that state after a module fixture's `main`: the one test in that shape,
`test_the_registry_eac_rewrite_reaches_the_dd_opening.py`, asserts object identity, not values.

## Controls

`tests/simulation/test_a_test_after_an_in_process_run_reads_the_drawn_book.py`:

* **The pair.** In a subprocess, a writer test makes `main`'s own writes and leaves them (C1 →
  1604.4, the figure H40 saw; C4 off its drawn 5500; one acquired record). H40's two reds then run
  as the next test. Green with the fixture. With the fixture's call removed, both fail:
  `assert 1604.4 == 2500` for c1, and c4 fails with it.
* **The acquisitions clear.** No window short enough for a test wins an acquisition: 0 wins to
  2017-02-28 (145 s) and 0 to 2017-12-31 (232 s), measured today. A win needs a home-move churn
  that the company takes to market. So the test seeds the record a win appends, built by the run's
  own `make_acquired_customer`. With `ACQUIRED_CUSTOMERS.clear()` deleted, it fails.

## End-to-end

* **Canon:** test harness only. Nothing in `company/`, `saas/` or `simulation/` changed.
* **Logic:** a run resets at its start (L1) and every test resets at its end (L2). Phase 4c still
  reads the rewrite inside the test that ran `main`.
* **Surprise:** the L1 control could never exercise the acquired clear, because nothing it ran
  wins. Two explanations fit: the clear is dead code, or wins are just rare. The evidence says
  rare. Wins happen only on the home-move branch, and `test_home_move_undeliverable_win.py`
  reaches it only by forcing a churn.
* **Not yet seen:** c1 and c4 going green in the HEAD-red census's own order. The next census run
  will confirm that. If they stay red there, a second polluter exists and this result is wrong.

## Neighbouring suites, with the fixture in

I ran five files in one process in an `origin/main` worktree: the registry-rewrite file, the
second-run file, `test_customers.py`, phase C, and 40a. Result: 66 passed, 3 skipped, 1 failed in
42 min.

The failure is `test_phase40a_pass_through.py::test_pass_through_customer_in_fast_run`.
`LiveLedgerWriteUnderTest` refused a write to `coupled_gap_ledger.json` from inside a default-window
`main()`. That is not this change. `main` already resets the book at its own start (L1), so the
book it begins from is the same with or without the teardown, and the refusal fired inside `main`,
before any teardown. It is the live-ledger guard family filed on 2026-08-17 and 2026-09-17. The
test is not on `HEAD_RED_REGISTER.md`, so the census either skips it or runs it where that write
is not refused. I did not establish which.
