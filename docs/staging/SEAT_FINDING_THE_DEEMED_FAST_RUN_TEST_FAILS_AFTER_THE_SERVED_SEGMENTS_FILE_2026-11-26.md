**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# `test_deemed_customer_in_fast_run` fails when run after `test_served_segments_curriculum.py`

Found 26 Nov while landing S1 (`CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE` taken).

## What was run

`pytest -x tests/simulation/test_served_segments_curriculum.py tests/simulation/test_phase40c_deemed_rate.py`
at a0c9d51f1b plus the S1 flip: 40 passed, then
`test_phase40c_deemed_rate.py::test_deemed_customer_in_fast_run` raised
`DwellingNotDrawn: 'SYN-2016-008' is supplied but the world drew no dwelling for it`, from
`dwelling_records.build_properties` inside `run_phase2b._main`. It failed after about 50 s, so it
died early in the run.

**Control:** the same pair with the flag forced back to `False` (a `-p` plugin that sets
`live_population.CONTRACT_THE_FIRST_TERM_AT_THE_QUOTED_STRIKE = False` before collection) gave
the same error on the same account, also in 48 s. So the S1 flip did not cause this.

Run alone, the test was still running a full fast-mode book at the 10-minute cap and was stopped
without a verdict. **I cannot yet say** whether it passes on its own. The early death only after the
curriculum file suggests state leaking between tests, not a world defect. Candidates are a module
cache in `live_population` (`live_dwellings()` memoised under a served-segment set that a curriculum
test changed) or `SE_SERVED_SEGMENTS` left set. Neither is established.

## Done means

The pair passes in this order, or the leaking state is named and reset by the test that sets it.
One control first: run `test_deemed_customer_in_fast_run` alone to the end, so we know whether it is
order-dependent at all.
