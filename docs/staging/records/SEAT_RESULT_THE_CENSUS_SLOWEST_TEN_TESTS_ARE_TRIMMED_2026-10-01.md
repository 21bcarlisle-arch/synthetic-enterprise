**Severity:** RECORDED · **Lane:** H_harness · **Epoch:** 3 · **Atom:** `unminted`

# RESULT — the census's ten slowest tests are trimmed: ~2,150 s → ~400 s

Lane 0 `the-census-slowest-ten-tests-are-trimmed`, direction item from
`SEAT_FINDING_THE_CENSUS_BOUND_WAS_UNDER_TWICE_ITS_WORST_RUN_FROM_09_22_BECAUSE_THE_WORST_RUN_IS_MOVED_BY_HAND_2026-09-30.md`.

**Duplicate-work note at draw:** the "other live claim" was this same id, claimed at 00:57 by
this draw's own write. No rival `surgical_land` or seat was running. There was no second piece of
work, so no disposition was needed.

| test (09-30 census) | was | now | commit |
|---|---|---|---|
| `test_couple_w2_11_d5::test_cli_runs_and_prints_all_three_gaps` | 356 s | 17 s | `1603fb367` |
| six `tests/background` brief/sweep tests (nested level-zero pass) | ~152 s each | ~4 s each | `ecb326104` |
| `test_home_move_undeliverable_win`, both call-site legs | ~296 s each | ~129 s each | `3f98974a8`, `1513ce6a5`, + window |
| `test_value_chain_credit_feed_wiring` fixture | 284 s | 91 s | same, + window |

Measured on a loaded box, so the "now" column is an upper bound.

- **Two trims are in the world code, not the tests**, and both are bit-identical:
  - the ambient solve (`3f98974a8`);
  - the 2R2C integrator's hoisted loop (`1513ce6a5`, `simulate_day` 0.577 → 0.358 ms/day).

  They speed up every `run_phase2b` in the suite and every real world run, not only these four.
- **The window trims rest on measured first lifecycle events.** Those were C5 on 2016-12-31 and
  C8 on 2017-04-01. The no-successor leg used to pin C7, whose first event is 2017-12-31, so C7
  alone set the two-year window. It now forces whichever no-successor account the world reaches
  first, and asserts that the force fired.
- **Not done here, deliberately:** `SUITE_TIMEOUT_SECONDS` stays at 17,400. The bound follows a
  measured complete run (`WORST_OBSERVED_SUITE_SECONDS`), never a predicted one. The next nightly
  census `--durations` reading is what licenses bringing it down.

**Correction, kept beside the claim:** I pre-registered that the truncated run would take ~400 s
under cProfile, with the ambient solve at ~60%. It took 575 s, and the solve was at 14%. The
weight had already moved to the integrator.
